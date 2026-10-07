#!/usr/bin/env python3
"""Sealed UA/WN production analysis. No fetching; A must be committed before B."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[k]='1'
import sys,json,zipfile,subprocess,argparse
from pathlib import Path
import numpy as np
import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.parquet as pq
import duckdb
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from common import EP,OUT,DERIVED,sha,dump,progress,utc
from snapshot import FIELDS
from intervals import interval,verdict

METRICS=['Y','U','C','V','F','MC','MV']
KEYS='source_year,origin_id,dest_id,matching_date,band'

def sealed_table(record,columns=None,filters=None):
    p=EP/record['path'];assert sha(p)==record['sha256'] and p.stat().st_size==record['bytes'],str(p)
    with p.open('rb') as f:return pq.read_table(f,columns=columns,filters=filters)

def committed(path):
    rel=str(path.relative_to(EP.parents[2]))
    assert subprocess.check_output(['git','show','HEAD:'+rel])==path.read_bytes(),f'Uncommitted required seal: {rel}'

def preconditions(period):
    spec=json.loads((HERE/'production-seal.json').read_text());committed(HERE/'production-seal.json')
    for rel,h in spec['files'].items():
        p=EP/rel;assert sha(p)==h,(rel,'changed');committed(p)
    committed(OUT/'amendment2/OWNER_APPROVAL.md');committed(OUT/'amendment2/summary.json')
    assert json.loads((OUT/'amendment2/summary.json').read_text())['status']=='PASS'
    if period=='B':committed(HERE/'results-A.json')
    arrays=json.loads((HERE/'resampling.json').read_text())
    starts={}
    for a in arrays['arrays']:
        p=EP/a['path'];assert sha(p)==a['sha256'];starts[a['year']]=np.load(p,allow_pickle=False)
    return arrays,starts

def records(db,sql):
    q=db.execute(sql);return [dict(zip([x[0] for x in q.description],row)) for row in q.fetchall()]

def ingest(period,years,db,coverage):
    schedule=sealed_table(coverage['structural_files']['structure'],filters=[('source_year','in',years),('carrier','in',['UA','WN'])])
    db.register('schedule',schedule)
    source=json.loads((EP/'data/flights-manifest.json').read_text())['sources']
    struct={Path(r['path']).stem:r for r in json.loads((EP/'data/structure-manifest.json').read_text())['derivatives']}
    path=DERIVED/f'confirm-outcomes-{period}.parquet'
    if path.exists():
        saved=json.loads((HERE/f'inputs-{period}.json').read_text())
        assert sha(path)==saved['outcomes']['sha256']
        db.register('outcomes',pq.read_table(path))
        return saved
    # This append is flushed before the first source ZIP is opened.
    first=utc();progress(f'Period {period} outcomes FIRST OPEN at {first}; production code/arrays committed'+(' and A sealed.' if period=='B' else '.'))
    writer=None;inputs=[];n=0
    for e in source:
        archive=EP/e['path'];year,month=map(int,archive.stem.split('-'))
        if year not in years:continue
        assert sha(archive)==e['sha256'] and archive.stat().st_size==e['bytes']
        name=next(i['name'] for i in e['members'] if i['name'].lower().endswith('.csv'))
        columns=FIELDS+['Cancelled','Diverted','ArrDelay']
        with zipfile.ZipFile(archive) as z,z.open(name) as f:
            raw=pacsv.read_csv(f,read_options=pacsv.ReadOptions(block_size=2**22,use_threads=False),
                convert_options=pacsv.ConvertOptions(include_columns=columns,column_types={k:pa.string() for k in columns},strings_can_be_null=False))
        sr=struct[f'schedule-{year}-{month:02}']
        expected=sealed_table(sr)
        assert raw.num_rows==expected.num_rows and raw.select(FIELDS).equals(expected.select(FIELDS)), 'Source schedule changed'
        raw=raw.append_column('source_year',pa.array(np.full(raw.num_rows,year,dtype=np.int16)))
        raw=raw.append_column('source_month',pa.array(np.full(raw.num_rows,month,dtype=np.int8)))
        raw=raw.append_column('source_row',pa.array(np.arange(1,raw.num_rows+1,dtype=np.int64)))
        scored=score_raw(db,raw)
        if writer is None:writer=pq.ParquetWriter(path,scored.schema,compression='zstd')
        writer.write_table(scored);n+=scored.num_rows
        inputs.append(dict(year=year,month=month,sha256=e['sha256'],rows=raw.num_rows,UA_WN_rows=scored.num_rows,status_errors=errors,schedule_identical=True))
        db.unregister('raw');del raw,expected
    writer.close()
    saved=dict(first_open_utc=first,sources=inputs,outcomes=dict(path=str(path.relative_to(EP)),sha256=sha(path),rows=n))
    dump(HERE/f'inputs-{period}.json',saved)
    db.register('outcomes',pq.read_table(path))
    return saved

def score_raw(db,raw):
    db.register('raw',raw)
    db.execute("""CREATE OR REPLACE TEMP TABLE parsed AS SELECT source_year,source_month,source_row,
        trim(Cancelled) AS rc,trim(Diverted) AS rv,trim(ArrDelay) AS rd,
        try_cast(nullif(trim(Cancelled),'') AS DOUBLE) AS c,
        try_cast(nullif(trim(Diverted),'') AS DOUBLE) AS v,
        try_cast(nullif(trim(ArrDelay),'') AS DOUBLE) AS d
        FROM raw WHERE Reporting_Airline IN ('UA','WN')""")
    errors=db.execute("""SELECT count(*) FROM parsed WHERE
        (rc!='' AND (c IS NULL OR NOT isfinite(c) OR c NOT IN (0,1))) OR
        (rv!='' AND (v IS NULL OR NOT isfinite(v) OR v NOT IN (0,1))) OR
        (rd!='' AND (d IS NULL OR NOT isfinite(d)))""").fetchone()[0]
    assert errors==0,'Invalid status/delay'
    scored=db.execute("""SELECT source_year,source_month,source_row,
        CASE WHEN c=1 OR v=1 THEN 0 WHEN c=0 AND v=0 AND d IS NOT NULL THEN (d<15)::INTEGER ELSE 0 END AS Y,
        CASE WHEN c=1 OR v=1 THEN 0 WHEN c=0 AND v=0 AND d IS NOT NULL THEN 0 ELSE 1 END AS U,
        coalesce(c=1,false)::INTEGER AS C,coalesce(v=1,false)::INTEGER AS V,
        coalesce(c=1 OR v=1,false)::INTEGER AS F,
        (c IS NULL)::INTEGER AS MC,(v IS NULL)::INTEGER AS MV
        FROM parsed ORDER BY source_row""").fetch_arrow_table()
    return scored

def rate_record(n,y,u=0):
    return dict(n=int(n),numerator=float(y),rate=float(y/n) if n else None,
        interval=[float(y/n),float((y+u)/n)] if n else None,
        interval_type='exact historical census; unknown outcomes all fail/all succeed',unknown=int(u))

def summaries(db,where='TRUE'):
    rows=records(db,f"SELECT carrier,count(*) AS n,{','.join('sum('+k+') AS '+k for k in METRICS)} FROM flights WHERE {where} GROUP BY carrier ORDER BY carrier")
    result={}
    for r in rows:
        result[r['carrier']]={k:rate_record(r['n'],r[k],r['U'] if k=='Y' else 0) for k in METRICS}
    for c in ['UA','WN']:
        if c not in result:result[c]={k:rate_record(0,0) for k in METRICS}
    return result

def weighted_shared(arr):
    return {c:{k:dict(n=int(arr['n_'+side].sum()),weight=float(arr['weight'].sum()),
        rate=float(np.average(arr[side+'_'+k],weights=arr['weight'])),
        interval=[float(np.average(arr[side+'_'+k],weights=arr['weight'])),float(np.average(arr[side+'_'+k]+(arr[side+'_U'] if k=='Y' else 0),weights=arr['weight']))],
        interval_type='weighted census unknown-assignment range') for k in METRICS} for c,side in [('UA','a'),('WN','b')]}

def cells(db,record,years,hours=2,weight='w_s',airport=None):
    pc=sealed_table(record,filters=[('source_year','in',years),('a','==','UA'),('b','==','WN')])
    db.register('pc',pc)
    exclusion='TRUE' if airport is None else f'origin_id!={airport} AND dest_id!={airport}'
    db.execute(f"""CREATE OR REPLACE TEMP TABLE agg AS SELECT source_year,origin_id,dest_id,matching_date,
        departure_minute//{hours*60} AS band,carrier,count(*) AS n,
        {','.join('sum('+k+')::DOUBLE AS '+k for k in METRICS)}
        FROM flights WHERE valid_key AND {exclusion} GROUP BY ALL""")
    # Cell counts come from the frozen schedule; equality is a mandatory check.
    mismatch=db.execute(f"SELECT count(*) FROM pc p LEFT JOIN agg a USING({KEYS}) LEFT JOIN agg b USING({KEYS}) WHERE a.carrier='UA' AND b.carrier='WN' AND (a.n!=p.n_a OR b.n!=p.n_b)").fetchone()[0]
    assert mismatch==0
    sql=f"""SELECT p.source_year,p.matching_date,p.week,p.origin_id,p.dest_id,p.band,p.n_a,p.n_b,p.{weight} AS weight,
        {','.join('a.'+k+'/p.n_a AS a_'+k+',b.'+k+'/p.n_b AS b_'+k for k in METRICS)}
        FROM pc p JOIN agg a USING({KEYS}) JOIN agg b USING({KEYS})
        WHERE a.carrier='UA' AND b.carrier='WN'
        ORDER BY p.source_year,p.matching_date,p.origin_id,p.dest_id,p.band"""
    arr=db.execute(sql).fetchnumpy();assert len(arr['weight'])==pc.num_rows
    return arr

def gap(arr,spec,starts,years,equal_year=False):
    groups=[];ix=np.empty(len(arr['weight']),dtype=int);off=0
    for g in spec['groups']:
        if g['year'] not in years:continue
        groups.append((g['year'],off,g['days']));sel=arr['source_year']==g['year']
        di=(arr['matching_date'][sel].astype('datetime64[D]')-np.datetime64(g['start'])).astype(int)
        assert np.all((di>=0)&(di<g['days'])),'Sensitivity outside frozen daily span'
        ix[sel]=off+di;off+=g['days']
    w=arr['weight'];d=arr['a_Y']-arr['b_Y']
    values=np.stack([d,d-arr['b_U'],d+arr['a_U']],axis=1)*w[:,None]
    den=np.bincount(ix,weights=w,minlength=off)
    daily=np.stack([np.bincount(ix,weights=values[:,k],minlength=off) for k in range(3)],axis=1)
    result=interval(groups,daily,den,starts,equal_year)
    if '_draws' in result:
        draws=result.pop('_draws')
    else:draws=None
    result.update(n={c:int(arr['n_a' if c=='UA' else 'n_b'].sum()) for c in ['UA','WN']},
        cells=len(w),weeks=len(set(zip(arr['source_year'].tolist(),arr['week'].tolist()))),weight=float(w.sum()),
        descriptive_only=True)
    return result,draws

def support(arr,national,retained=None):
    retained=retained or national
    return {c:dict(n=int(arr['n_a' if c=='UA' else 'n_b'].sum()),
        original_denominator=national[c]['Y']['n'],retained_denominator=retained[c]['Y']['n'],
        original_coverage=rate_record(national[c]['Y']['n'],arr['n_a' if c=='UA' else 'n_b'].sum()),
        retained_coverage=rate_record(retained[c]['Y']['n'],arr['n_a' if c=='UA' else 'n_b'].sum())) for c in ['UA','WN']}

def nearest(db,record,years):
    table=sealed_table(record,filters=[('source_year','in',years),('a','==','UA'),('b','==','WN')]);db.register('nearest',table)
    arr=db.execute(f"SELECT p.source_year,p.matching_date,p.week,1 AS n_a,1 AS n_b,1.0 AS weight,{','.join('a.'+k+'::DOUBLE AS a_'+k+',b.'+k+'::DOUBLE AS b_'+k for k in METRICS)} FROM nearest p JOIN flights a ON p.source_id_a=a.source_id JOIN flights b ON p.source_id_b=b.source_id ORDER BY p.source_year,p.source_month_a,p.source_row_a").fetchnumpy()
    assert len(arr['weight'])==table.num_rows
    return arr

def main(period):
    years=[2023,2024] if period=='A' else [2025]
    spec,starts=preconditions(period)
    coverage=json.loads((OUT/'coverage.json').read_text())
    assert not json.loads((OUT/'natural-key-collisions.json').read_text())['groups']
    db=duckdb.connect();db.execute('SET threads=4');db.execute("SET memory_limit='6GB'")
    inputs=ingest(period,years,db,coverage)
    db.execute('CREATE TEMP TABLE flights AS SELECT s.*,o.* EXCLUDE(source_year,source_month,source_row) FROM schedule s JOIN outcomes o USING(source_year,source_month,source_row)')
    count,unique=db.execute('SELECT count(*),count(DISTINCT source_id) FROM flights').fetchone()
    assert count==unique==inputs['outcomes']['rows']
    assert db.execute('SELECT count(*) FROM schedule').fetchone()[0]==count
    national=summaries(db);annual={str(y):summaries(db,f'source_year={y}') for y in years}
    primary_record=coverage['frozen_sets']['pair_cells']
    arr=cells(db,primary_record,years)
    primary,draws=gap(arr,spec,starts,years)
    primary['descriptive_only']=False
    if draws is not None:
        drawpath=DERIVED/f'confirm-draws-{period}.npy';np.save(drawpath,draws,allow_pickle=False)
        primary['draw_file']=dict(path=str(drawpath.relative_to(EP)),sha256=sha(drawpath))
    quality=[]
    for y in years:
        for c in ['UA','WN']:
            n=annual[str(y)][c]['Y']['n'];u=annual[str(y)][c]['U']['numerator']
            invalid=db.execute('SELECT count(*) FROM flights WHERE source_year=? AND carrier=? AND NOT valid_key',[y,c]).fetchone()[0]
            quality.extend([dict(name=f'{c}-{y}-national-unknown',n=n,count=int(u),cutoff=.001,passes=u*1000<=n),
                dict(name=f'{c}-{y}-invalid-key',n=n,count=invalid,cutoff=.001,passes=invalid*1000<=n)])
            sel=arr['source_year']==y;side='a' if c=='UA' else 'b'
            sn=int(arr['n_'+side][sel].sum());su=int(round((arr[side+'_U'][sel]*arr['n_'+side][sel]).sum()))
            quality.append(dict(name=f'{c}-{y}-matched-unknown',n=sn,count=su,cutoff=.001,passes=su*1000<=sn))
    quality.append(dict(name='interval-all-1999-draws-valid',passes=primary['valid'],evidence={k:primary.get(k) for k in ['valid_draws','minimum_draw_denominator','minimum_draw_se']}))
    passed=all(q['passes'] for q in quality)
    primary['verdict']=verdict(primary,passed)
    matched=support(arr,national)
    shared=weighted_shared(arr)
    # Mark shared membership without changing any schedule or outcomes.
    db.execute(f'CREATE TEMP TABLE primary_keys AS SELECT {KEYS} FROM pc')
    db.execute(f'ALTER TABLE flights ADD COLUMN pair_shared BOOLEAN')
    db.execute(f'UPDATE flights SET pair_shared=valid_key AND EXISTS(SELECT 1 FROM primary_keys p WHERE '+ ' AND '.join('p.'+k+'=flights.'+k for k in KEYS.split(','))+')')
    union=sealed_table(coverage['frozen_sets']['cells'],filters=[('source_year','in',years)])
    db.register('all_cells',union)
    db.execute(f'CREATE TEMP TABLE union_keys AS SELECT {KEYS} FROM all_cells GROUP BY ALL HAVING count(DISTINCT carrier)>1')
    union_condition='valid_key AND EXISTS(SELECT 1 FROM union_keys p WHERE '+' AND '.join('p.'+k+'=flights.'+k for k in KEYS.split(','))+')'
    excluded=dict(pair_unsupported=summaries(db,'NOT pair_shared'),invalid_key=summaries(db,'NOT valid_key'),
        outside_all_supported_cells=summaries(db,'NOT ('+union_condition+')'))
    annual_excluded={str(y):{name:summaries(db,f'source_year={y} AND ({condition})') for name,condition in [
        ('pair_unsupported','NOT pair_shared'),('invalid_key','NOT valid_key'),('outside_all_supported_cells','NOT ('+union_condition+')')]} for y in years}
    excluded_exposure={name:{c:rate_record(national[c]['Y']['n'],values[c]['Y']['n']) for c in ['UA','WN']} for name,values in excluded.items()}
    sensitivities={};files={Path(r['path']).name:r for r in json.loads((EP/'data/sensitivity-manifest.json').read_text())['files']}
    variants=[('window_1h',files['pairs-1h.parquet'],1,'w_s',None),('window_4h',files['pairs-4h.parquet'],4,'w_s',None),
        ('equal_cell_weights',files['pairs-alternate-weights.parquet'],2,'equal_weight',None),
        ('harmonic_weights',files['pairs-alternate-weights.parquet'],2,'harmonic_weight',None)]
    variants += [(f'omit_airport_{a}',files[f'pairs-omit-{a}.parquet'],2,'w_s',a) for a in coverage['omission_airport_ranking']]
    for name,rec,h,w,a in variants:
        alt=cells(db,rec,years,h,w,a);res,_=gap(alt,spec,starts,years)
        retained=national if a is None else summaries(db,f'origin_id!={a} AND dest_id!={a}')
        res['coverage']=support(alt,national,retained);res['national_rates']=retained
        res['national_gap']=national_gap(retained);sensitivities[name]=res
    for y in years:
        sub={k:v[arr['source_year']==y] for k,v in arr.items()}
        res,_=gap(sub,spec,starts,[y]);res['national_gap']=national_gap(annual[str(y)])
        res['weighted_shared']=weighted_shared(sub);res['coverage']=support(sub,annual[str(y)])
        sensitivities[f'year_{y}']=res
    if period=='A':
        res,_=gap(arr,spec,starts,years,equal_year=True)
        yy=[national_gap(annual[str(y)]) for y in years]
        res['national_gap']=dict(point=float(np.mean([x['point'] for x in yy])),interval=np.mean([x['interval'] for x in yy],axis=0).tolist(),n={c:national[c]['Y']['n'] for c in ['UA','WN']})
        sensitivities['equal_year_A']=res
    near=nearest(db,files['nearest30.parquet'],years);res,_=gap(near,spec,starts,years)
    res['coverage']=support(near,national);res['national_gap']=national_gap(national);sensitivities['reciprocal_nearest_30min']=res
    raw_shared={c:rate_record(int(arr['n_'+side].sum()),float((arr[side+'_Y']*arr['n_'+side]).sum()),int(round((arr[side+'_U']*arr['n_'+side]).sum()))) for c,side in [('UA','a'),('WN','b')]}
    G=national_gap(national);R=raw_shared['UA']['rate']-raw_shared['WN']['rate'];D=primary['point'][0]
    result=dict(period=period,years=years,written_utc=utc(),inputs=inputs,primary=primary,quality=dict(passes=passed,checks=quality),
        national=national,national_gap=G,annual=annual,matched_coverage=matched,weighted_shared=shared,
        raw_shared=raw_shared,excluded=excluded,annual_excluded=annual_excluded,excluded_exposure=excluded_exposure,sensitivities=sensitivities,
        decomposition=dict(descriptive_only=True,G=G['point'],R=R,D=D,restriction=G['point']-R,reweighting=R-D,total=G['point']-D,n=primary['n']),
        descriptive_interval_note='Census ranges are missingness identification ranges, not sampling confidence intervals. Sensitivity block intervals are descriptive nominal 99%, not independently gate-certified.',
        no_sensitivity_can_change_verdict=True)
    if period=='B':
        av=json.loads((HERE/'results-A.json').read_text())['primary']['verdict']
        bv=primary['verdict'];same=av==bv and av!='inconclusive'
        result['replication']=dict(replicated=same,A=av,B=bv,decision='replicated' if same else 'replication unsettled',
            rule='Only the same decisive label in A and B permits replicated; B cannot rewrite A.')
    dump(HERE/f'results-{period}.json',result)
    progress(f'Period {period} computed: {primary["verdict"]}; all registered sensitivities saved; quality={passed}. Result and draw hashes require checkpoint before '+('opening B.' if period=='A' else 'final descriptive reconciliation.'))
    print(json.dumps(dict(period=period,point=primary['point'],envelope=primary['envelope'],quality=passed,verdict=primary['verdict'],sensitivities=len(sensitivities))))

def national_gap(rates):
    a,b=rates['UA']['Y'],rates['WN']['Y']
    if not a['n'] or not b['n']:return dict(point=None,interval=None,n={'UA':a['n'],'WN':b['n']})
    d=a['rate']-b['rate']
    return dict(point=d,interval=[d-b['unknown']/b['n'],d+a['unknown']/a['n']],n={'UA':a['n'],'WN':b['n']},descriptive_only=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('period',choices=['A','B']);main(p.parse_args().period)
