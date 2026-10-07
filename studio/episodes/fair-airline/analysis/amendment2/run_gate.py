#!/usr/bin/env python3
"""Outcome-blind Amendment 2: studentized whole-network circular block interval."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[k] = '1'
import sys, json, time, math, hashlib, argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pyarrow.parquet as pq
import duckdb
from scipy.special import ndtr, ndtri
from scipy.signal import lfilter
from scipy.stats import beta, t as student_t
from common import EP, OUT, DERIVED, dump, sha, utc, progress
from blind_guard import install, verify_denial
install()
HERE = Path(__file__).resolve().parent
DESIGN = json.loads((HERE/'design.json').read_text())


def rng(bank, scenario, rep, stream):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(
        [DESIGN['seed'], bank, scenario, rep, stream])))


def scenarios():
    result = []
    for profile in DESIGN['profiles']:
        for effects in DESIGN['effects']:
            result.append(dict(id=len(result), profile=profile, effects=effects, required=True))
    profile = next(p for p in DESIGN['profiles'] if p['name']=='serial_daily')
    for effects in DESIGN['additional_serial_effects']:
        result.append(dict(id=len(result), profile=profile, effects=effects,
                           required=effects != [.03,.03]))
    return result


def load_structure():
    record = json.loads((OUT/'coverage.json').read_text())['structural_files']['structure']
    path = EP/record['path']
    assert sha(path)==record['sha256'] and path.stat().st_size==record['bytes']
    columns = ['source_year','carrier','origin_id','dest_id','matching_date','band','valid_key']
    with path.open('rb') as f:
        schema = pq.read_schema(f)
        assert not any(x in schema.names for x in ['ArrDelay','Cancelled','Diverted','Y','U'])
        f.seek(0)
        table = pq.read_table(f, columns=columns)
    db=duckdb.connect(); db.execute('SET threads=10'); db.register('schedule',table)
    counts=db.execute("SELECT carrier, source_year, count(*) FROM schedule GROUP BY ALL ORDER BY ALL").fetchall()
    rows=db.execute("""WITH c AS (
      SELECT source_year, origin_id, dest_id, matching_date, band,
        count(*) FILTER (WHERE carrier='UA') AS na,
        count(*) FILTER (WHERE carrier='WN') AS nb
      FROM schedule WHERE valid_key AND carrier IN ('UA','WN') GROUP BY ALL)
      SELECT * FROM c WHERE na>0 AND nb>0 ORDER BY source_year, matching_date, origin_id, dest_id, band
      """).fetchnumpy()
    db.close()
    year=rows['source_year'].astype(int); date=rows['matching_date'].astype('datetime64[D]')
    start=date.min(); day=(date-start).astype(int)
    origin=rows['origin_id'].astype(int); dest=rows['dest_id'].astype(int)
    airports=np.unique(np.r_[origin,dest]); oi=np.searchsorted(airports,origin); di=np.searchsorted(airports,dest)
    n=np.stack([rows['na'],rows['nb']],axis=1).astype(int); w=n.sum(axis=1)/2
    season=np.sin(2*np.pi*(date-date.astype('datetime64[Y]')).astype(int)/365.25)
    keys=list(zip(origin,dest,rows['band'].astype(int)))
    cache={k:(.03 if hashlib.sha256(f'{k[0]}|{k[1]}|{k[2]}'.encode()).digest()[-1]&1 else -.03) for k in set(keys)}
    hetero=np.array([cache[k] for k in keys])
    group=[]; den=[]; ix=np.empty(len(n),dtype=int); offset=0
    for y in (2023,2024,2025):
        sel=year==y
        # Include every physical date in the source year's normalized matching span,
        # even a zero-support day; never bridge a source-year resampling boundary.
        days=np.arange(day[sel].min(),day[sel].max()+1)
        ix[sel]=offset+day[sel]-days[0]
        group.append((y,offset,len(days)));offset+=len(days)
    den=np.bincount(ix,weights=w,minlength=offset)
    st=dict(year=year,date=date,day=day,ndays=int(day.max()+1),oi=oi,di=di,airports=airports,
            n=n,w=w,ix=ix,den=den,groups=group,season=season,hetero=hetero)
    support=[]
    for y,off,length in group:
        sel=year==y
        support.append(dict(year=y,cells=int(sel.sum()),UA=int(n[sel,0].sum()),WN=int(n[sel,1].sum()),
            calendar_days=length,routes=len(set(zip(origin[sel],dest[sel]))),weight=float(w[sel].sum()),
            largest_day_share=float(den[off:off+length].max()/den[off:off+length].sum())))
    manifest=dict(input=record,support=support,full_carrier_year_counts=counts,
        cells_sha256=hashlib.sha256(np.column_stack([year,day,origin,dest,rows['band'],n]).astype('<i8').tobytes()).hexdigest(),
        raw_denial=verify_denial(),confirmation_outcomes_opened=False,
        numpy=np.__version__,scipy=__import__('scipy').__version__,duckdb=duckdb.__version__,python=sys.version,
        pilot=dict(point=.029530752505772195,se=.005202749651889861,sim_ci=[.012946504550839281,.04611500046070511]))
    return st,manifest


def prepare(st, scenario):
    effect=np.where(st['year']<=2024,scenario['effects'][0],scenario['effects'][1])
    # Route-varying effects, centered separately on each period's frozen weights.
    h=st['hetero']/3
    for sel in (st['year']<=2024,st['year']==2025):
        h[sel]-=np.average(h[sel],weights=st['w'][sel])
    base=.8+.05*st['season']+st['hetero']
    p=np.stack([base+(effect+h)/2,base-(effect+h)/2],axis=1)
    s=scenario['profile']; load=np.array([[1.,1.],[.5,.75]]) if s['differential'] else np.ones((2,2))
    var=s['sd']**2*(load[:,0]**2+2*load[:,1]**2)
    mu=ndtri(p)*np.sqrt(1+var)
    assert p.min()>.05 and p.max()<.99
    truth=[]
    for sel in (st['year']<=2024,st['year']==2025):
        d=np.average(p[sel,0]-p[sel,1],weights=st['w'][sel])
        truth.append([d,d-s['missing'],d+s['missing']])
    assert np.max(np.abs(np.array(truth)[:,0]-scenario['effects']))<1e-12
    return p,mu,load,np.array(truth)


def shock_series(random, entities, days, sd, ar):
    eps=random.standard_normal((entities,days))
    eps[:,0]*=sd
    eps[:,1:]*=sd*np.sqrt(1-ar*ar)
    return lfilter([1.],[1.,-ar],eps,axis=1)


def generate(st, scenario, prepared, bank, rep):
    p,mu,load,truth=prepared;s=scenario['profile']
    r=rng(bank,scenario['id'],rep,0)
    network=shock_series(r,1,st['ndays'],s['sd'],s['ar'])[0]
    airport=shock_series(r,len(st['airports']),st['ndays'],s['sd'],s['ar'])
    q=np.empty_like(p)
    a=airport[st['oi'],st['day']]+airport[st['di'],st['day']]
    for c in (0,1):
        q[:,c]=ndtr(mu[:,c]+load[c,0]*network[st['day']]+load[c,1]*a)
    # Conditional iid probit errors integrate exactly to binomial cell counts.
    # Cell order is sealed; within each cell UA then WN. No normal count approximation.
    timely=rng(bank,scenario['id'],rep,1).binomial(st['n'],q)
    r=rng(bank,scenario['id'],rep,2)
    unknown=r.binomial(timely,s['missing']/p)
    failures=st['n']-timely
    cancelled=r.binomial(failures,.25)
    diverted=r.binomial(failures-cancelled,1/15)
    late=failures-cancelled-diverted
    success=st['n']-unknown-cancelled-diverted-late
    assert np.array_equal(success,timely-unknown)
    # Unknown outcomes elsewhere are zero in this synthetic process. Also impose
    # the stricter matched-support quality cutoff, preserved in production.
    quality=True
    for year in (2023,2024,2025):
        sel=st['year']==year
        quality &= bool(np.all(unknown[sel].sum(axis=0)*1000<=st['n'][sel].sum(axis=0)))
    rate=success/st['n'];u=unknown/st['n']; gap=rate[:,0]-rate[:,1]
    values=np.stack([gap,gap-u[:,1],gap+u[:,0]],axis=1)*st['w'][:,None]
    daily=np.stack([np.bincount(st['ix'],weights=values[:,k],minlength=len(st['den'])) for k in range(3)],axis=1)
    return daily,quality


def indices(random, days, length, draws):
    if length==1:
        return random.integers(0,days,size=(draws,days),endpoint=False)
    start=random.integers(0,days,size=(draws,math.ceil(days/length)),endpoint=False)
    return ((start[:,:,None]+np.arange(length))%days).reshape(draws,-1)[:,:days]


def circular_sums(values, length):
    """One sum for every circular start, with no random numbers."""
    ext=np.concatenate([values,values[:length-1]],axis=0)
    cs=np.concatenate([np.zeros_like(ext[:1]),np.cumsum(ext,axis=0)],axis=0)
    return cs[length:]-cs[:-length]


def interval(st,daily,bank,sid,rep,length):
    assert length==28
    r=rng(bank,sid,rep,3); B=DESIGN['draws']
    nums=[np.zeros((B,3)),np.zeros((B,3))]; dens=[np.zeros(B),np.zeros(B)]
    original=[np.zeros(3),np.zeros(3)]; od=np.zeros(2); pieces=[[],[]]
    df=np.zeros(2,dtype=int)
    # Same year/draw/start order and exact indices as Amendment 1 length 28.
    for year,offset,days in st['groups']:
        t=int(year==2025); sl=slice(offset,offset+days)
        q,tail=divmod(days,length)
        assert q>=2 and tail>0
        starts=r.integers(0,days,size=(B,q+1),endpoint=False)
        full_n=circular_sums(daily[sl],length); full_d=circular_sums(st['den'][sl],length)
        tail_n=circular_sums(daily[sl],tail); tail_d=circular_sums(st['den'][sl],tail)
        sn=full_n[starts[:,:q]];sd=full_d[starts[:,:q]]
        nums[t]+=sn.sum(axis=1)+tail_n[starts[:,q]]
        dens[t]+=sd.sum(axis=1)+tail_d[starts[:,q]]
        original[t]+=daily[sl].sum(axis=0);od[t]+=st['den'][sl].sum()
        pieces[t].append((days,q,tail,full_n,full_d,tail_n,tail_d,starts,sn,sd))
        df[t]+=q-1
    point=np.array(original)/od[:,None];lower=[];upper=[]
    for t in (0,1):
        if np.any(dens[t]<=0):return point,None,None
        star=nums[t]/dens[t][:,None]
        var=np.zeros(3);vstar=np.zeros((B,3))
        for days,q,tail,fn,fd,tn,td,starts,sn,sd in pieces[t]:
            # Delta-method residual block totals, centered within source year.
            full=fn-fd[:,None]*point[t]
            short=tn-td[:,None]*point[t]
            var+=q*full.var(axis=0,ddof=0)*days/(days-length)
            var+=short.var(axis=0,ddof=0)*days/(days-tail)
            res=sn-sd[:,:,None]*star[:,None,:]
            # Prefixes of the q independent full-block starts estimate tail variance.
            shortstar=tn[starts[:,:q]]-td[starts[:,:q],None]*star[:,None,:]
            vstar+=q*res.var(axis=1,ddof=1)+shortstar.var(axis=1,ddof=1)
        se=np.sqrt(var)/od[t];sestar=np.sqrt(vstar)/dens[t][:,None]
        if not (np.isfinite(star).all() and np.isfinite(se).all() and
                np.isfinite(sestar).all() and np.all(se>0) and np.all(sestar>0)):
            return point,None,None
        pivot=(star-point[t])/sestar
        quant=np.quantile(pivot,[DESIGN['alpha']/2,1-DESIGN['alpha']/2],axis=0,method='linear')
        floor=float(student_t.ppf(1-DESIGN['alpha']/2,df[t]))
        lo=point[t]-np.maximum(quant[1],floor)*se
        hi=point[t]-np.minimum(quant[0],-floor)*se
        lower.append(lo.min());upper.append(hi.max())
    return point,np.array(lower),np.array(upper)


def verdict(low,high,quality=True):
    if not quality or low is None:return [0,0]
    return np.where(low>.02,1,np.where(high<.02,-1,0)).tolist()


def one(st,s,prepared,bank,rep,candidate):
    daily,quality=generate(st,s,prepared,bank,rep)
    point,low,high=interval(st,daily,bank,s['id'],rep,candidate)
    truth=prepared[3]
    return dict(rep=rep,point=point.tolist(),low=None if low is None else low.tolist(),
      high=None if high is None else high.tolist(),quality=quality,verdict=verdict(low,high,quality),
      covered=[False,False] if low is None else ((low<=truth.min(axis=1))&(high>=truth.max(axis=1))).tolist())


def exact(k,n):
    return dict(count=int(k),n=n,rate=k/n,mcse=float(np.sqrt(k/n*(1-k/n)/n)),
      lower=0. if k==0 else float(beta.ppf(.05,k,n-k+1)),
      upper=1. if k==n else float(beta.ppf(.95,k+1,n-k)))


def summarize(rows,s,truth):
    n=len(rows);err=np.array([x['point'] for x in rows])-truth
    bias=np.abs(err.mean(axis=0))+1.96*err.std(axis=0,ddof=1)/np.sqrt(n)
    v=np.array([x['verdict'] for x in rows]);cov=np.array([x['covered'] for x in rows])
    result=dict(scenario=s,truth=truth.tolist(),bias_mean=err.mean(axis=0).tolist(),
      bias_mcse=(err.std(axis=0,ddof=1)/np.sqrt(n)).tolist(),bias_bound=bias.tolist(),
      joint_coverage=exact(cov.all(axis=1).sum(),n),periods=[],valid=exact(sum(x['low'] is not None for x in rows),n))
    tests=[bool(np.all(bias<=.002)),result['joint_coverage']['lower']>=.92,result['valid']['rate']>=.95]
    for t in (0,1):
        d=s['effects'][t];r=dict(coverage=exact(cov[:,t].sum(),n))
        tests.append(r['coverage']['lower']>=.92)
        if d<=.02:
            r['false_above']=exact((v[:,t]==1).sum(),n);tests.append(r['false_above']['upper']<=.025)
        if d>=.02:
            r['false_below']=exact((v[:,t]==-1).sum(),n);tests.append(r['false_below']['upper']<=.025)
        if d in (0.,.04):
            r['power']=exact((v[:,t]==(1 if d>.02 else -1)).sum(),n);tests.append(r['power']['lower']>=.80)
        result['periods'].append(r)
    if s['effects'] in ([0.,0.],[.04,.04]):
        direction=1 if s['effects'][0]>.02 else -1
        result['replicated_power']=exact((v==direction).all(axis=1).sum(),n)
        tests.append(result['replicated_power']['lower']>=.80)
    if s['effects']==[.03,.03]:
        result['local_power']=exact((v==1).all(axis=1).sum(),n)
    result['passes']=all(tests)
    return result


def check_seal():
    seal=json.loads((HERE/'seal.json').read_text())
    import subprocess
    for name,expected in seal['files'].items():
        assert sha(HERE/name)==expected,(name,'changed since seal')
        data=subprocess.check_output(['git','show',f"HEAD:studio/episodes/fair-airline/analysis/amendment2/{name}"])
        assert hashlib.sha256(data).hexdigest()==expected,(name,'not committed')


def run(args):
    start=time.perf_counter();st,manifest=load_structure()
    if args.action=='prepare':
        truths=[]
        for s in scenarios():
            pr=prepare(st,s);truths.append(dict(scenario=s,truth=pr[3].tolist(),min_p=float(pr[0].min()),max_p=float(pr[0].max())))
        dump(HERE/'structure.json',manifest);dump(HERE/'truths.json',truths)
        dump(HERE/'fixtures.json',fixtures(st))
        print(json.dumps(dict(support=manifest['support'],prepare_seconds=time.perf_counter()-start)))
        return
    check_seal()
    if args.action=='benchmark':
        s=scenarios()[9];pr=prepare(st,s)
        measured=[]
        with ThreadPoolExecutor(max_workers=10) as pool:
            for c in DESIGN['candidates']:
                begin=time.perf_counter()
                # Do not summarize/inspect acceptance on benchmark stream.
                list(pool.map(lambda rep:one(st,s,pr,90,rep,c),range(10)))
                measured.append(dict(candidate=c,datasets=10,workers=10,seconds=time.perf_counter()-begin))
        dump(HERE/'timing.json',dict(written_utc=utc(),measurements=measured,acceptance_inspected=False))
        print(json.dumps(measured));return
    summaries=[];selected=None
    if (HERE/'results.json').exists():
        old=json.loads((HERE/'results.json').read_text());summaries=old['scenarios']
    for bank in (2,1):
        candidates=DESIGN['candidates'] if bank==2 else [selected]
        if candidates==[None]:break
        for c in candidates:
            candidate_pass=True
            for s in scenarios():
                existing=next((x for x in summaries if x['bank']==bank and x['candidate']==c and x['scenario']['id']==s['id']),None)
                if existing is None:
                    pr=prepare(st,s);n=DESIGN['selection_datasets'] if bank==2 else DESIGN['validation_datasets']
                    path=HERE/f'bank{bank}-candidate{c}-scenario{s["id"]}.jsonl'
                    rows=[json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
                    assert [row['rep'] for row in rows]==list(range(len(rows))) and len(rows)<=n
                    begin=time.perf_counter()
                    with path.open('a') as f,ThreadPoolExecutor(max_workers=10) as pool:
                        for row in pool.map(lambda rep:one(st,s,pr,bank,rep,c),range(len(rows),n)):
                            rows.append(row);f.write(json.dumps(row,separators=(',',':'))+'\n')
                    existing=summarize(rows,s,pr[3]);existing.update(bank=bank,candidate=c,seconds=time.perf_counter()-begin)
                    summaries.append(existing)
                    dump(HERE/'results.json',dict(status='RUNNING',selected=selected,scenarios=summaries,confirmation_outcomes_opened=False))
                    print(json.dumps(dict(bank=bank,candidate=c,scenario=s['id'],passes=existing['passes'],seconds=existing['seconds'])),flush=True)
                if s['required'] and not existing['passes']:
                    candidate_pass=False
                    # Bias failure invalidates every resampler; otherwise fixed fallback.
                    if np.max(existing['bias_bound'])>.002:
                        dump(HERE/'results.json',dict(status='FAIL_BIAS',selected=None,scenarios=summaries,confirmation_outcomes_opened=False));return
                    break
            if candidate_pass:
                selected=c;break
        if not candidate_pass:
            dump(HERE/'results.json',dict(status='FAIL',selected=selected,scenarios=summaries,confirmation_outcomes_opened=False));return
    dump(HERE/'results.json',dict(status='PASS',selected=selected,scenarios=summaries,confirmation_outcomes_opened=False))


def fixtures(st):
    # Exact endpoint semantics and independent expansion of all count weights.
    from fractions import Fraction
    count_a=[1,2,3];count_b=[3,1,2];success_a=[1,1,2];success_b=[1,1,0]
    direct=sum(Fraction(a+b,2)*(Fraction(ya,a)-Fraction(yb,b)) for a,b,ya,yb in zip(count_a,count_b,success_a,success_b))/sum(Fraction(a+b,2) for a,b in zip(count_a,count_b))
    expanded=sum((a+b)/2*(ya/a-yb/b) for a,b,ya,yb in zip(count_a,count_b,success_a,success_b))/sum((a+b)/2 for a,b in zip(count_a,count_b))
    assert abs(float(direct)-expanded)<1e-15
    assert verdict(np.array([.02,.02]),np.array([.02,.02]))==[0,0]
    assert verdict(np.array([.021,.01]),np.array([.03,.019]))==[1,-1]
    assert verdict(np.array([.03,.03]),np.array([.04,.04]),False)==[0,0]
    for c in DESIGN['candidates']:
        ix=indices(rng(99,0,0,3),366,c,20)
        assert ix.shape==(20,366) and ix.min()>=0 and ix.max()<366
    assert verify_denial()
    return dict(passes=True,checks=['fractional-weight expansion','strict equality inconclusive','symmetric directions','quality stops verdict','day/block lengths','raw access denied'],synthetic_datasets=0)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','benchmark','run'])
    run(parser.parse_args())
