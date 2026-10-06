"""Schedule-only probability cells and exact linear expectation operators.

Native readers receive Python-opened file objects; DuckDB receives only Arrow
tables. No native SQL filename or raw source is used by this module.
"""
import hashlib
import heapq
import json
from io import BytesIO
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
from scipy import sparse
from scipy.optimize import minimize, linprog
from common import EP, OUT, DERIVED, CARRIERS, sha, progress, dump, seal_file
from blind_guard import install, verify_denial

install()

def read_sealed(record):
    p=EP/record['path']
    if DERIVED.resolve() not in p.resolve().parents:
        raise PermissionError('Only sealed schedule derivatives are inputs')
    assert p.stat().st_size==record['bytes'] and sha(p)==record['sha256']
    with p.open('rb') as f:
        return pq.read_table(f)

def heterogeneity(origin,destination,band):
    key=f'{origin}|{destination}|{band}'.encode('utf-8')
    return .03 if hashlib.sha256(key).digest()[-1]&1 else -.03

def build():
    assert verify_denial()
    coverage=json.loads((OUT/'coverage.json').read_text())
    table=read_sealed(coverage['structural_files']['structure'])
    # This exact schema check precedes all materialization and SQL registration.
    allowed={'source_year','source_month','source_row','flight_date','carrier',
      'dot_id','flight_number','origin_id','dest_id','dep_hhmm','raw_dep_hhmm',
      'airports_valid','time_valid','valid_key','departure_minute',
      'matching_date','band','week','source_id'}
    assert set(table.column_names)==allowed
    db=duckdb.connect();db.execute('SET threads=10');db.register('schedule',table)
    db.execute('''CREATE TABLE route_keys AS SELECT DISTINCT
      coalesce(origin_id,-1) AS origin,coalesce(dest_id,-1) AS destination,
      coalesce(band,-1) AS band FROM schedule''')
    keys=db.execute('SELECT * FROM route_keys ORDER BY ALL').fetchall()
    h=pa.table({'origin':[k[0] for k in keys],'destination':[k[1] for k in keys],
      'band':[k[2] for k in keys],'hetero':[heterogeneity(*k) for k in keys]})
    db.register('hetero_keys',h)
    db.execute('''CREATE TABLE cell_counts AS SELECT source_year,origin_id,
      dest_id,matching_date,band,count(DISTINCT carrier) AS carriers
      FROM schedule WHERE valid_key GROUP BY ALL''')
    db.execute('''CREATE TABLE prepared AS SELECT s.*,
      coalesce(valid_key AND c.carriers>1,false) AS shared,
      CASE WHEN valid_key THEN matching_date ELSE flight_date END AS model_date,
      CASE WHEN valid_key AND c.carriers>1 THEN origin_id ELSE -1 END AS model_origin,
      CASE WHEN valid_key AND c.carriers>1 THEN dest_id ELSE -1 END AS model_destination,
      CASE WHEN valid_key AND c.carriers>1 THEN s.band ELSE -1 END AS model_band,
      h.hetero,
      sin(2*pi()*(dayofyear(CASE WHEN valid_key THEN matching_date ELSE flight_date END)-1)/365.25) AS season
      FROM schedule s LEFT JOIN cell_counts c USING
      (source_year,origin_id,dest_id,matching_date,band)
      JOIN hetero_keys h ON h.origin=coalesce(s.origin_id,-1)
      AND h.destination=coalesce(s.dest_id,-1) AND h.band=coalesce(s.band,-1)''')
    groups='source_year,carrier,model_date,model_origin,model_destination,model_band'
    codes=sorted(CARRIERS)
    db.execute(f'''CREATE TABLE model_cells AS SELECT
      (row_number() OVER(ORDER BY {groups})-1)::INTEGER AS probability_id,
      *, CASE WHEN source_year=2025 THEN 1 ELSE 0 END AS period
      FROM (SELECT {groups},bool_or(shared) AS shared,count(*) AS n,
      count(*) FILTER(WHERE hetero>0) AS positive_n,min(season) AS cell_season
      FROM prepared GROUP BY {groups})''')
    mt=db.execute('SELECT * FROM model_cells ORDER BY probability_id').to_arrow_table()
    cells=mt.to_pandas();n=cells.n.to_numpy(dtype=float)
    positive=cells.positive_n.to_numpy(dtype=float);negative=n-positive
    carrier_index=cells.carrier.map({c:i for i,c in enumerate(codes)}).to_numpy()
    constants=[]
    for base,season,increment in __import__('itertools').product((.7,.8,.9),(0.,.05),(0.,.005)):
        center=base+season*cells.cell_season.to_numpy()+increment*(carrier_index-3.5)
        plus=np.clip(center+.03,.05,.99);minus=np.clip(center-.03,.05,.99)
        column=(positive*plus+negative*minus)/n
        mt=mt.append_column(f'p{len(constants)}',pa.array(column))
        # Exact two-mass variance identity; no subtraction of huge moments.
        constants.append(float(np.sum(positive*negative/n*(plus-minus)**2)))
    with (DERIVED/'simulation-cells.parquet').open('wb') as f:
        pq.write_table(mt,f,compression='zstd')
    ft=db.execute(f'''SELECT s.source_year,s.source_month,s.source_row,s.carrier,
      s.dot_id,s.origin_id,s.dest_id,s.week,s.valid_key,s.hetero,s.season,m.probability_id
      FROM prepared s JOIN model_cells m USING({groups})
      ORDER BY s.source_year,s.source_month,s.source_row''').to_arrow_table()
    with (DERIVED/'simulation-flights.parquet').open('wb') as f:
        pq.write_table(ft,f,compression='zstd')
    pairs=[tuple(line.split('|')) for line in
      (EP/coverage['frozen_sets']['supported_pairs']['path']).read_text().splitlines()]
    rows=[];cols=[];values=[]
    for period in (0,1):
        for j,code in enumerate(codes):
            mask=(cells.period.to_numpy()==period)&(cells.carrier.to_numpy()==code)
            indices=np.flatnonzero(mask)
            rows.extend([period*8+j]*len(indices));cols.extend(indices.tolist())
            values.extend((n[indices]/n[indices].sum()).tolist())
    pc=db.execute('''SELECT a.period,a.carrier AS a,b.carrier AS b,
      a.probability_id AS ia,b.probability_id AS ib,(a.n+b.n)/2. AS w
      FROM model_cells a JOIN model_cells b USING
      (source_year,model_date,model_origin,model_destination,model_band)
      WHERE a.shared AND b.shared AND a.carrier<b.carrier
      ORDER BY a.carrier,b.carrier,a.period,a.probability_id''').to_arrow_table().to_pandas()
    for k,(a,b) in enumerate(pairs):
        for period in (0,1):
            part=pc[(pc.a==a)&(pc.b==b)&(pc.period==period)]
            weight=part.w.to_numpy();weight=weight/weight.sum()
            for side,col in enumerate(('ia','ib')):
                rows.extend([16+(k*2+period)*2+side]*len(part))
                cols.extend(part[col].to_numpy().tolist());values.extend(weight.tolist())
    t=sparse.csr_matrix((values,(rows,cols)),shape=(16+len(pairs)*4,len(n)))
    with (DERIVED/'simulation-operator.npz').open('wb') as f:sparse.save_npz(f,t)
    record={'source_commit':'af8e89f','coverage_sha256':sha(OUT/'coverage.json'),
      'probability_cells':len(n),'source_flights':len(ft),'pairs':[list(p) for p in pairs],
      'carriers':codes,'rows':'national period/carrier, then pair/period/side',
      'base_columns':[dict(baseline=b,season=s,increment=i,column=f'p{k}')
        for k,(b,s,i) in enumerate(__import__('itertools').product((.7,.8,.9),(0.,.05),(0.,.005)))],
      'per_record_base_variance_constants':constants,
      'probability_cell_order':groups,
      'files':[seal_file(DERIVED/name) for name in
        ('simulation-cells.parquet','simulation-flights.parquet','simulation-operator.npz')]}
    dump(OUT/'simulation-structure.json',record)
    progress(f'Deterministic simulation model built from sealed schedule only: {len(n):,} probability cells and {len(ft):,} flight mappings. Exact national/shared linear expectation operator sealed; no Y, statuses, shocks or bootstrap draws generated.')
    return Model(record)

class Model:
    def __init__(self,record=None):
        self.record=record or json.loads((OUT/'simulation-structure.json').read_text())
        files={r['path'].split('/')[-1]:r for r in self.record['files']}
        self.cells=read_sealed(files['simulation-cells.parquet']).to_pandas()
        op=files['simulation-operator.npz'];p=EP/op['path'];assert sha(p)==op['sha256']
        with p.open('rb') as f:self.t=sparse.load_npz(BytesIO(f.read())).tocsr()
        self.n=self.cells.n.to_numpy(dtype=float)
        self.pairs=[tuple(p) for p in self.record['pairs']]
        self.codes=self.record['carriers']
        selectors=[]
        for k,(a,b) in enumerate(self.pairs):
            for period in (0,1):
                selectors.append((period*8+self.codes.index(a),period*8+self.codes.index(b)))
                selectors.append((16+(k*2+period)*2,17+(k*2+period)*2))
        self.sides=selectors
        self.q=sparse.vstack([self.t[a]-self.t[b] for a,b in selectors],format='csr')

    def base(self,stress,increment=0.):
        k=next(i for i,r in enumerate(self.record['base_columns']) if
          (r['baseline'],r['season'],r['increment'])==
          (stress['baseline'],stress['season'],increment))
        return np.clip(self.cells[f'p{k}'].to_numpy(),.05,.99)

    def truths(self,p,mechanism):
        r=mechanism['r'];kind=mechanism['kind']
        if kind=='informative':primary=p-r;unknown=np.full_like(p,r)
        elif kind in ('mcar','status'):
            primary=p*(1-r);unknown=r*(.7+.3*p)
        else:primary=p;unknown=np.zeros_like(p)
        rates=self.t@primary;u=self.t@unknown
        components=np.array([[rates[a]-rates[b],rates[a]-rates[b]-u[b],
          rates[a]-rates[b]+u[a]] for a,b in self.sides]).reshape(-1)
        latent=self.q@p
        def rh(x):
            x=x.reshape(len(self.pairs),2,2)
            q=np.stack((np.minimum(x[:,:,0],-x[:,:,1]),
                        np.minimum(-x[:,:,0],x[:,:,1])),axis=1)
            return dict(R=float(q.min(axis=2).max()),H=float(q.max()))
        return dict(components=components.tolist(),latent_G_D=latent.tolist(),
                    primary=rh(components.reshape(-1,3)[:,0]),latent=rh(latent))

    def solve_convex(self,base,equalities,inequalities):
        constraints=equalities+inequalities
        if not constraints:return base.copy(),0.,dict(dual=[],residual=0.)
        a=sparse.vstack([r[0] for r in constraints],format='csr')
        b=np.array([r[1] for r in constraints]);total=self.n.sum()
        def evaluate(lam):
            p=np.clip(base-total*(a.T@lam)/self.n,.05,.99)
            ap=a@p
            loss=-np.dot(self.n,(p-base)**2)/(2*total)-np.dot(lam,ap-b)
            return float(loss),b-ap
        # The unclipped equality-only solution is an exact small linear solve.
        # It also avoids optimizer stopping on an objective change before the
        # probability constraints reach their required residual tolerance.
        if not inequalities:
            h=total*(a.multiply(1/self.n)@a.T).toarray()
            lam=np.linalg.lstsq(h,a@base-b,rcond=1e-12)[0]
            candidate=base-total*(a.T@lam)/self.n
            if (np.min(candidate)>=.05 and np.max(candidate)<=.99 and
                np.max(np.abs(a@candidate-b),initial=0.)<=1e-10):
                objective=float(np.dot(self.n,(candidate-base)**2))
                dual=objective+2*total*float(np.dot(lam,a@candidate-b))
                return candidate,objective,dict(
                  dual=lam.tolist(),residual=float(np.max(np.abs(a@candidate-b),initial=0.)),
                  dual_objective_lower_bound=dual,
                  iterations=1,solver='unclipped equality quadratic, SVD least-squares dual')
        fit=minimize(evaluate,np.zeros(len(b)),jac=True,method='L-BFGS-B',
          bounds=[(None,None)]*len(equalities)+[(0,None)]*len(inequalities),
          options={'ftol':1e-15,'gtol':1e-10,'maxiter':10000,'maxls':100})
        lam=fit.x.copy()
        # Deterministic projected Newton refinement on the active probability
        # bounds and dual inequality bounds; rank-deficient equalities use SVD.
        for _ in range(100):
            unbounded=base-total*(a.T@lam)/self.n
            p=np.clip(unbounded,.05,.99);gradient=b-a@p
            free=np.array([i for i in range(len(b)) if i<len(equalities)
              or lam[i]>1e-12 or gradient[i]<-1e-10],dtype=int)
            active=(unbounded>.05)&(unbounded<.99)
            if not len(free):break
            af=a[free]
            h=total*(af.multiply(active/self.n)@af.T).toarray()
            step=np.zeros_like(lam)
            step[free]=-np.linalg.lstsq(h,gradient[free],rcond=1e-12)[0]
            if np.max(np.abs(gradient[free]),initial=0.)<=1e-10:break
            old,_=evaluate(lam);alpha=1.
            for _ in range(50):
                candidate=lam+alpha*step
                candidate[len(equalities):]=np.maximum(0,candidate[len(equalities):])
                loss,_=evaluate(candidate)
                if loss<=old+1e-16:
                    lam=candidate;break
                alpha*=.5
            else:break
        p=np.clip(base-total*(a.T@lam)/self.n,.05,.99)
        residual=a@p-b
        error=max(np.max(np.abs(residual[:len(equalities)]),initial=0.),
                  np.max(residual[len(equalities):],initial=0.))
        if error>1e-6:
            # A failed numerical fit is never labeled proven infeasible.
            feasible=linprog(np.zeros(len(p)),
              A_eq=a[:len(equalities)] if equalities else None,
              b_eq=b[:len(equalities)] if equalities else None,
              A_ub=a[len(equalities):] if inequalities else None,
              b_ub=b[len(equalities):] if inequalities else None,
              bounds=(.05,.99),method='highs',options={'primal_feasibility_tolerance':1e-8})
            if feasible.status==2:return None,float('inf'),dict(infeasible=True)
            raise RuntimeError(f'Calibration numerical failure; residual={error}; LP status={feasible.status}')
        objective=float(np.dot(self.n,(p-base)**2))
        dual_objective=objective+2*total*float(np.dot(lam,residual))
        return p,objective,dict(dual=lam.tolist(),residual=float(error),
          dual_objective_lower_bound=dual_objective,
          normalized_duality_gap=max(0.,(objective-dual_objective)/total),
          iterations=int(fit.nit),solver='scipy L-BFGS-B bounded dual')

    def calibrate(self,process):
        template=process['template'];kind=template['kind']
        increment=(template.get('increment',0.) if kind=='base' or
          (kind=='stable' and template['increment'] in (0.,.005)) else 0.)
        base=self.base(process['stress'],increment)
        if kind=='base':return base,dict(objective=0.,residual=0.,constraints=[])
        equalities=[];active=set()
        mechanism=process['missingness']
        # Informative masking subtracts the same r from every carrier score;
        # completed-record MCAR/status masking scales every primary contrast.
        scale=1-mechanism['r'] if mechanism['kind'] in ('mcar','status') else 1.
        q=scale*self.q
        if kind=='stable':
            for k,(a,b) in enumerate(self.pairs):
                target=template['increment']*(self.codes.index(a)-self.codes.index(b))
                for period,contrast in __import__('itertools').product((0,1),(0,1)):
                    equalities.append((q[k*4+period*2+contrast],target))
        else:
            for edge in template['active']:
                k=self.pairs.index(tuple(edge['pair']));active.add(k);direction=edge['direction']
                for period,name in enumerate(('A','B')):
                    g,minus_d=template[name]
                    equalities.extend(((direction*q[k*4+period*2],g),
                                       (-direction*q[k*4+period*2+1],minus_d)))
        disjunctions=[]
        if template.get('cap_other_R') is not None:
            for k in range(len(self.pairs)):
                if k in active:continue
                for direction in (1,-1):
                    branches=[(direction*q[k*4+period*2+contrast]*(1 if contrast==0 else -1),template['cap_other_R'])
                      for period,contrast in __import__('itertools').product((0,1),(0,1))]
                    disjunctions.append(branches)
        if template.get('cap_other_H') is not None:
            for k in range(len(self.pairs)):
                if k in active:continue
                for direction,period in __import__('itertools').product((1,-1),(0,1)):
                    disjunctions.append([(direction*q[k*4+period*2],template['cap_other_H']),
                                         (-direction*q[k*4+period*2+1],template['cap_other_H'])])
        # Exhaustive deterministic branch-and-bound of the minimum constraints.
        # Each convex relaxation gives a global lower bound. No branch/time cap.
        counter=0;heap=[(0.,counter,[])];best=None;best_objective=float('inf');best_info=None
        while heap:
            lower,_,inequalities=heapq.heappop(heap)
            if lower>best_objective+1e-7:continue
            p,obj,info=self.solve_convex(base,equalities,inequalities)
            if p is None:continue
            # A feasible primal objective is an upper bound, not a lower bound.
            # The dual Lagrangian value safely bounds unexplored branches.
            bound=info['dual_objective_lower_bound']
            if bound>best_objective+1e-7:continue
            failed=next((branches for branches in disjunctions if
              min(float((row@p)[0])-bound for row,bound in branches)>1e-6),None)
            if failed:
                for branch in failed:
                    counter+=1;heapq.heappush(heap,(bound,counter,inequalities+[branch]))
            elif (best is None or obj<best_objective or
                  (obj==best_objective and tuple(p)<tuple(best))):
                best=p;best_objective=obj;best_info=info
        if best is None:raise ValueError('Required deterministic calibration is infeasible')
        base_index=next(i for i,r in enumerate(self.record['base_columns']) if
          (r['baseline'],r['season'],r['increment'])==
          (process['stress']['baseline'],process['stress']['season'],increment))
        constant=self.record['per_record_base_variance_constants'][base_index]
        return best,dict(objective=best_objective+constant,variable_objective=best_objective,
                        within_national_only_base_constant=constant,**best_info,
                        branches_solved=counter+1,truth=self.truths(best,process['missingness']))

if __name__=='__main__':
    m=build()
    print(dict(probability_cells=len(m.n),flights=m.record['source_flights'],outcomes_generated=0))
