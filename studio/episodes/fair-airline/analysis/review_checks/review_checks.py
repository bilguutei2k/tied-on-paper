#!/usr/bin/env python3
"""POST-HOC, NOT REGISTERED. Independent raw audit and descriptive threats checks.
No production imports/mutations. Streams monthly ZIP CSVs with at most 10 workers.
Writes aggregate evidence only here; no raw/flight rows are released.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[k]='1'
from pathlib import Path
import json, hashlib, zipfile, subprocess, concurrent.futures, datetime, math
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pcsv
import pyarrow.compute as pc
import pyarrow.parquet as pq
from scipy.stats import t
HERE=Path(__file__).resolve().parent
EP=HERE.parents[1]; ROOT=EP.parents[2]; D=EP/'data/derived'
KEY=['source_year','origin_id','dest_id','matching_date','band']
RENAME={'Reporting_Airline':'carrier','DOT_ID_Reporting_Airline':'dot_id','IATA_CODE_Reporting_Airline':'iata','Flight_Number_Reporting_Airline':'flight_number','OriginAirportID':'origin_id','DestAirportID':'dest_id','Origin':'origin','Dest':'dest','CRSDepTime':'dep_hhmm','CRSElapsedTime':'scheduled_minutes','ActualElapsedTime':'actual_minutes','DepDelay':'dep_delay','ArrDelay':'arr_delay','Cancelled':'cancelled','Diverted':'diverted','FlightDate':'flight_date'}
STR={'Reporting_Airline','IATA_CODE_Reporting_Airline','Flight_Number_Reporting_Airline','Origin','Dest','FlightDate'}
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        while b:=f.read(2**20):h.update(b)
    return h.hexdigest()
def dump(name,obj):
    (HERE/name).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False,default=lambda v:v.item() if isinstance(v,np.generic) else str(v))+'\n')
def normalize(f):
    f['matching_date']=pd.to_datetime(f.flight_date).dt.normalize()+pd.to_timedelta((f.dep_hhmm==2400).astype(int),unit='D')
    minute=(f.dep_hhmm//100)*60+f.dep_hhmm%100
    f['departure_minute']=np.where(f.dep_hhmm==2400,0,minute)
    f['band']=(f.departure_minute//120).astype('int64')
    return f

def indicators(f):
    c=f.cancelled;v=f.diverted;a=f.arr_delay;dep=f.dep_delay
    assert c.isin([0.,1.]).all() and v.isin([0.,1.]).all()
    assert np.isfinite(a.dropna()).all()
    complete=(c==0)&(v==0)
    f['Y']=(complete&(a<15)).astype(float)
    f['U']=(complete&a.isna()).astype(float)
    f['C']=(c==1).astype(float)
    f['V']=(v==1).astype(float)
    f['V_only']=((c!=1)&(v==1)).astype(float)
    f['late_arrival']=(complete&(a>=15)).astype(float)
    f['dep_late']=((c==0)&(dep>=15)).astype(float) # all-scheduled denominator; cancellations separate
    f['dep_known']=((c==0)&dep.notna()).astype(float)
    f['dep_timely']=((c==0)&(dep<15)).astype(float) # diversions can depart on time
    f['dep_unknown_non_cancel']=((c==0)&dep.isna()).astype(float)
    f['complete']=complete.astype(float)
    assert np.array_equal(f.Y+f.C+f.V_only+f.late_arrival+f.U,np.ones(len(f)))
    return f

FROZEN=pq.read_table(D/'pair-cells.parquet',filters=[('a','==','UA'),('b','==','WN')]).to_pandas()
FROZEN['matching_date']=pd.to_datetime(FROZEN.matching_date)

def month(entry):
    path=EP/entry['path'];y,m=map(int,path.stem.split('-'))
    assert sha(path)==entry['sha256'] and path.stat().st_size==entry['bytes']
    member=next(v['name'] for v in entry['members'] if v['name'].endswith('.csv'))
    chunks=[];offset=0
    with zipfile.ZipFile(path) as z,z.open(member) as raw:
        reader=pcsv.open_csv(raw,read_options=pcsv.ReadOptions(block_size=2**22,use_threads=False),convert_options=pcsv.ConvertOptions(include_columns=list(RENAME),column_types={k:pa.string() if k in STR else pa.float64() for k in RENAME}))
        for b in reader:
            mask=pc.is_in(b['Reporting_Airline'],value_set=pa.array(['UA','WN']))
            idx=np.flatnonzero(mask.to_numpy(zero_copy_only=False))
            q=b.filter(mask).to_pandas().rename(columns=RENAME)
            q['source_row']=offset+idx+1;offset+=b.num_rows
            chunks.append(q)
    f=pd.concat(chunks,ignore_index=True);f['source_year']=y;f['source_month']=m
    assert (f.dot_id==f.carrier.map({'UA':19977,'WN':19393})).all() and (f.iata==f.carrier).all()
    f=indicators(normalize(f))
    assert ((f.dep_hhmm==2400)|((f.dep_hhmm>=0)&(f.dep_hhmm<2400)&(f.dep_hhmm%100<60)&(f.dep_hhmm%1==0))).all()
    dates=pd.to_datetime(f.flight_date);assert (dates.dt.year==y).all() and (dates.dt.month==m).all()
    s=pq.read_table(D/'structure.parquet',filters=[('source_year','==',y),('source_month','==',m),('carrier','in',['UA','WN'])]).to_pandas()
    o=pq.read_table(D/('confirm-outcomes-A.parquet' if y<2025 else 'confirm-outcomes-B.parquet'),filters=[('source_year','==',y),('source_month','==',m)]).to_pandas()
    for z in (s,o):z.sort_values('source_row',inplace=True)
    f.sort_values('source_row',inplace=True);assert len(f)==len(s)==len(o)
    for k in ['source_row','carrier','dot_id','flight_number','origin_id','dest_id','dep_hhmm','band','departure_minute']:
        assert np.array_equal(f[k].to_numpy(),s[k].to_numpy()),(y,m,k)
    assert np.array_equal(f.matching_date.to_numpy().astype('datetime64[D]'),s.matching_date.to_numpy().astype('datetime64[D]'))
    assert s.valid_key.all()
    assert np.array_equal(f.source_row,o.source_row)
    for k in ['Y','U','C','V']:assert np.array_equal(f[k].to_numpy(),o[k].to_numpy()),(y,m,k)
    natural=['carrier','flight_date','flight_number','origin_id','dest_id','dep_hhmm']
    dup=int(f.duplicated(natural).sum());assert dup==0
    good=f.complete.astype(bool)&f[['dep_delay','actual_minutes','arr_delay','scheduled_minutes']].notna().all(axis=1)
    identity=f.loc[good,'dep_delay']+f.loc[good,'actual_minutes']-f.loc[good,'arr_delay']-f.loc[good,'scheduled_minutes']
    qa=dict(year=y,month=m,raw_rows=offset,UA_WN_rows=len(f),sha256=entry['sha256'],raw_scoring_equals_derivative=True,schedule_equals_frozen=True,natural_duplicates=dup,midnight_2400=int((f.dep_hhmm==2400).sum()),normalized_next_year=int((f.matching_date.dt.year!=y).sum()),elapsed_identity_rows=int(good.sum()),elapsed_identity_nonzero=int((identity!=0).sum()),elapsed_identity_gt1=int((identity.abs()>1).sum()),elapsed_identity_max_abs=float(identity.abs().max()),national=f.groupby('carrier')[['Y','C','V','U']].agg(['size','sum']).to_json())
    p=FROZEN[FROZEN.source_year==y][KEY+['n_a','n_b','w_s']]
    f=f.merge(p,on=KEY,how='inner',validate='many_to_one')
    residual=f.dep_delay+f.actual_minutes-f.arr_delay-f.scheduled_minutes
    qa['matched_elapsed_identity_nonzero']=int((residual.notna()&(residual!=0)).sum())
    qa['matched_elapsed_identity_gt1']=int((residual.notna()&(residual.abs()>1)).sum())
    return f,qa

METRICS=['Y','C','V_only','late_arrival','U','dep_late','dep_timely','dep_unknown_non_cancel','dep_known','complete']
def cellify(f,verify=True):
    # Independent groupby over source rows, never production scoring/cell helpers.
    n=f.groupby(KEY+['carrier']).size().unstack('carrier')
    n=n.dropna(subset=['UA','WN']);c=n.rename(columns={'UA':'n_a','WN':'n_b'}).reset_index();c['w_s']=(c.n_a+c.n_b)/2
    f=f.drop(columns=['n_a','n_b','w_s'],errors='ignore').merge(c,on=KEY,validate='many_to_one')
    if verify:
        sealed=FROZEN[FROZEN.source_year.isin(f.source_year.unique())]
        check=c.merge(sealed,on=KEY,validate='one_to_one',suffixes=('','_sealed'))
        assert len(check)==len(c)==len(sealed)
        for k in ['n_a','n_b','w_s']:assert np.array_equal(check[k],check[k+'_sealed'])
    for col in METRICS:
        g=f.groupby(KEY+['carrier'])[col].mean().unstack('carrier')
        c=c.merge(g.rename(columns={a:a+'_'+col for a in ['UA','WN']}).reset_index(),on=KEY,validate='one_to_one')
    sc=f.groupby(KEY+['carrier']).scheduled_minutes.mean().unstack('carrier')
    assert sc.notna().all().all()
    c=c.merge(sc.rename(columns={'UA':'UA_schedule','WN':'WN_schedule'}).reset_index(),on=KEY)
    # Common departure-relative deadlines; cancels/diversions still fail.
    f=f.merge(sc.rename(columns={'UA':'s_UA','WN':'s_WN'}).reset_index(),on=KEY,validate='many_to_one')
    common=(f.s_UA+f.s_WN)/2
    f['common_mid']=(f.complete.astype(bool)&((f.dep_delay+f.actual_minutes)<common+15)).astype(float)
    f['common_WN']=(f.complete.astype(bool)&((f.dep_delay+f.actual_minutes)<f.s_WN+15)).astype(float)
    f['common_UA']=(f.complete.astype(bool)&((f.dep_delay+f.actual_minutes)<f.s_UA+15)).astype(float)
    # Symmetric counterfactual clock shifts preserve within-carrier timetable variation.
    f['equalized_mid']=(f.complete.astype(bool)&((f.arr_delay+f.scheduled_minutes-common)<15)).astype(float)
    for col in ['common_mid','common_WN','common_UA','equalized_mid']:
        g=f.groupby(KEY+['carrier'])[col].mean().unstack('carrier')
        c=c.merge(g.rename(columns={a:a+'_'+col for a in ['UA','WN']}).reset_index(),on=KEY)
    comp=f[f.complete==1]
    for name,col in [('actual','actual_minutes'),('dep_delay','dep_delay'),('slack','slack'),('sched_completed','scheduled_minutes')]:
        if col=='slack':comp=comp.assign(slack=comp.scheduled_minutes-comp.actual_minutes)
        g=comp.groupby(KEY+['carrier'])[col].mean().unstack('carrier')
        c=c.merge(g.rename(columns={a:a+'_'+name for a in ['UA','WN']}).reset_index(),on=KEY,how='left')
    c['month']=c.matching_date.dt.month
    for col in METRICS+['common_mid','common_WN','common_UA','equalized_mid']:
        c['gap_'+col]=c['UA_'+col]-c['WN_'+col]
    return f,c

def avg(c,col):return float(np.average(c[col],weights=c.w_s))
def summary(c,f):
    out=dict(cells=len(c),flights={'UA':int(c.n_a.sum()),'WN':int(c.n_b.sum())},weight=float(c.w_s.sum()))
    for metric in METRICS+['common_mid','common_WN','common_UA','equalized_mid','schedule']:
        out[metric]={'UA':avg(c,'UA_'+metric),'WN':avg(c,'WN_'+metric),'UA_minus_WN':avg(c,'UA_'+metric)-avg(c,'WN_'+metric)}
    # Conditional elapsed means restricted to cells with completed observations for both carriers.
    sel=c[['UA_actual','WN_actual','UA_dep_delay','WN_dep_delay']].notna().all(axis=1);q=c[sel]
    out['completed_cell_means']={'cells':len(q),'weight_share':float(q.w_s.sum()/c.w_s.sum()),'completed_rows_UA':int(((f.carrier=='UA')&(f.complete==1)).sum()),'completed_rows_WN':int(((f.carrier=='WN')&(f.complete==1)).sum())}
    for metric in ['actual','dep_delay','slack','sched_completed','schedule']:
        out['completed_cell_means'][metric]={'UA':avg(q,'UA_'+metric),'WN':avg(q,'WN_'+metric),'UA_minus_WN':avg(q,'UA_'+metric)-avg(q,'WN_'+metric)}
    out['missing']={k:int(f[k].isna().sum()) for k in ['scheduled_minutes','actual_minutes','dep_delay','arr_delay']}
    out['complete_elapsed_missing']=int(((f.complete==1)&f[['scheduled_minutes','actual_minutes','dep_delay','arr_delay']].isna().any(axis=1)).sum())
    assert np.max(np.abs(c.UA_dep_timely+c.UA_dep_late+c.UA_C+c.UA_dep_unknown_non_cancel-1))<1e-12
    assert np.max(np.abs(c.WN_dep_timely+c.WN_dep_late+c.WN_C+c.WN_dep_unknown_non_cancel-1))<1e-12
    out['departures_conditional_known']={a:out['dep_late'][a]/out['dep_known'][a] for a in ['UA','WN']}
    out['decomposition_advantage_points']={k:-100*out[k]['UA_minus_WN'] for k in ['C','V_only','late_arrival','U']}
    out['own_minus_common_mid_points']=100*(out['Y']['UA_minus_WN']-out['common_mid']['UA_minus_WN'])
    return out

def independent_interval(c,metric):
    """Literal independent loops over draws/blocks; no production interval code."""
    D0=avg(c,'gap_'+metric);W=c.w_s.sum();var=0.;parts=[];df=0
    for y in sorted(c.source_year.unique()):
        x=c[c.source_year==y];T=366 if y==2024 else 365;q,r=divmod(T,28);df+=q-1
        days=(x.matching_date-pd.Timestamp(int(y),1,1)).dt.days.to_numpy();assert days.min()>=0 and days.max()<T
        dn=np.bincount(days,weights=x.w_s*x['gap_'+metric],minlength=T);dw=np.bincount(days,weights=x.w_s,minlength=T)
        fn=np.array([sum(dn[(s+np.arange(28))%T]) for s in range(T)]);fw=np.array([sum(dw[(s+np.arange(28))%T]) for s in range(T)])
        hn=np.array([sum(dn[(s+np.arange(r))%T]) for s in range(T)]);hw=np.array([sum(dw[(s+np.arange(r))%T]) for s in range(T)])
        var+=q*np.var(fn-D0*fw)*T/(T-28)+np.var(hn-D0*hw)*T/(T-r)
        starts=np.load(D/f'confirm-starts-{y}.npy');parts.append((q,fn,fw,hn,hw,starts))
    se=math.sqrt(var)/W;draws=[];pivots=[];minimum_den=math.inf;minimum_se=math.inf
    for b in range(1999):
        N=0.;den=0.
        for q,fn,fw,hn,hw,ss in parts:
            s=ss[b];N+=sum(fn[s[:q]])+hn[s[q]];den+=sum(fw[s[:q]])+hw[s[q]]
        point=N/den;vv=0.
        for q,fn,fw,hn,hw,ss in parts:
            s=ss[b,:q];vv+=q*np.var(fn[s]-point*fw[s],ddof=1)+np.var(hn[s]-point*hw[s],ddof=1)
        sb=math.sqrt(vv)/den;assert np.isfinite(sb) and sb>0 and den>0
        draws.append(point);pivots.append((point-D0)/sb);minimum_den=min(minimum_den,den);minimum_se=min(minimum_se,sb)
    low,high=np.quantile(pivots,[.005,.995],method='linear');floor=t.ppf(.995,df)
    return dict(point=D0,se=se,interval=[D0-max(high,floor)*se,D0-min(low,-floor)*se],df=df,t_floor=float(floor),pivot_quantiles=[float(low),float(high)],minimum_den=minimum_den,minimum_draw_se=minimum_se),np.array(draws)

def grouping(c,cols):
    total=c.w_s.sum();rows=[]
    for key,g in c.groupby(cols,sort=True):
        if not isinstance(key,tuple):key=(key,)
        row=dict(zip(cols,key));row.update(cells=len(g),weight=float(g.w_s.sum()),weight_share=float(g.w_s.sum()/total),gap_points=100*avg(g,'gap_Y'),contribution_points=100*float((g.w_s*g.gap_Y).sum()/total),departure_timely_gap_points=100*avg(g,'gap_dep_timely'),common_clock_gap_points=100*avg(g,'gap_common_mid'),schedule_difference_minutes=avg(g,'UA_schedule')-avg(g,'WN_schedule'))
        rows.append(row)
    return pd.DataFrame(rows)

def seal_audit():
    out={};prefix='studio/episodes/fair-airline/'
    for rev in ['af6b613','4f759d3']:
        spec=json.loads(subprocess.check_output(['git','show',rev+':'+prefix+'analysis/confirm/production-seal.json']))
        checked=[]
        for rel,h in spec['files'].items():
            raw=subprocess.check_output(['git','show',rev+':'+prefix+rel]);assert hashlib.sha256(raw).hexdigest()==h;checked.append(rel)
        out[rev]={'commit':subprocess.check_output(['git','show','-s','--format=%H %aI %cI',rev],text=True).strip(),'files_verified':checked,'outcomes_opened':spec['confirmation_outcomes_opened']}
    rng=np.random.Generator(np.random.PCG64(20261005));r=json.loads((EP/'analysis/confirm/resampling.json').read_text());out['arrays']=[]
    for a in r['arrays']:
        p=EP/a['path'];assert sha(p)==a['sha256'];T=366 if a['year']==2024 else 365
        expected=rng.integers(0,T,size=(1999,14),endpoint=False);assert np.array_equal(expected,np.load(p))
        out['arrays'].append({'year':a['year'],'byte_hash_pass':True,'regeneration_exact':True})
    for per,rev in [('A','c829f51'),('B','12320b0')]:
        p=EP/f'analysis/confirm/results-{per}.json';raw=subprocess.check_output(['git','show',rev+':'+prefix+str(p.relative_to(EP))]);assert raw==p.read_bytes()
        x=json.loads(raw);out[per]={'seal_commit':subprocess.check_output(['git','show','-s','--format=%H %aI %cI',rev],text=True).strip(),'first_open_utc':x['inputs']['first_open_utc'],'current_results_identical_to_first_seal':True}
    dump('integrity.json',out)

def main():
    seal_audit();manifest=json.loads((EP/'data/flights-manifest.json').read_text())
    results=[];qa=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for f,q in pool.map(month,manifest['sources']):results.append(f);qa.append(q)
    f=pd.concat(results,ignore_index=True);del results
    f,c=cellify(f);dump('raw_audit.json',{'post_hoc_not_registered':True,'months':qa,'total_UA_WN_rows':sum(x['UA_WN_rows'] for x in qa),'all_36_months_pass':True})
    out={'post_hoc_not_registered':True,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Same frozen pair cells and w=(n_UA+n_WN)/2. No rematching. All extra contrasts descriptive; no multiplicity-certified decisions. Elapsed means condition on cells with completed flights in both carriers. Common clocks use equal-carrier mean scheduled block time per cell plus 15, relative to each scheduled departure; cancellations/diversions fail.'}
    airport_names=pd.concat([f[['origin_id','origin']].rename(columns={'origin_id':'id','origin':'name'}),f[['dest_id','dest']].rename(columns={'dest_id':'id','dest':'name'})]).drop_duplicates().set_index('id')['name'].to_dict()
    for period,years in [('A',[2023,2024]),('B',[2025])]:
        cp=c[c.source_year.isin(years)];fp=f[f.source_year.isin(years)];out[period]=summary(cp,fp)
        reg=json.loads((EP/f'analysis/confirm/results-{period}.json').read_text())
        out[period]['interval_checks']={}
        for metric in ['Y','dep_timely','dep_late','common_mid']:
            iv,draws=independent_interval(cp,metric)
            if metric=='Y':
                saved=np.load(EP/reg['primary']['draw_file']['path']);err=float(np.max(np.abs(draws-saved[:,0])))
                assert err<1e-12 and np.max(np.abs(np.array(iv['interval'])-reg['primary']['envelope']))<1e-12
                assert abs(iv['point']-reg['primary']['point'][0])<1e-12
                iv['maximum_saved_draw_error']=err;iv['registered_interval_reproduced']=True
            out[period]['interval_checks'][metric]=iv
        route=grouping(cp,['origin_id','dest_id']);route['origin']=route.origin_id.map(airport_names);route['dest']=route.dest_id.map(airport_names)
        route.sort_values('contribution_points',ascending=False).to_csv(HERE/f'routes-{period}.csv',index=False)
        airport=[]
        for a in sorted(set(cp.origin_id)|set(cp.dest_id)):
            sel=(cp.origin_id==a)|(cp.dest_id==a);g=cp[sel];r=grouping(g,['source_year'])
            airport.append(dict(airport_id=int(a),airport=airport_names[a],weight_share=float(g.w_s.sum()/cp.w_s.sum()),gap_points=100*avg(g,'gap_Y'),contribution_points=100*float((g.w_s*g.gap_Y).sum()/cp.w_s.sum()),gap_without_airport_points=100*avg(cp[~sel],'gap_Y')))
        pd.DataFrame(airport).sort_values('contribution_points',ascending=False).to_csv(HERE/f'airports-{period}.csv',index=False)
        for cols,name in [(['month'],'month'),(['band'],'time_of_day'),(['source_year'],'year')]:grouping(cp,cols).to_csv(HERE/f'{name}-{period}.csv',index=False)
        out[period]['concentration']={'routes':len(route),'airports':len(airport),'removals':[]}
        for by in ['contribution_points','weight_share']:
            ranked=route.sort_values(by,ascending=False)
            for n in [1,5,10,20]:
                selected=pd.MultiIndex.from_frame(ranked.head(n)[['origin_id','dest_id']]);sel=pd.MultiIndex.from_frame(cp[['origin_id','dest_id']]).isin(selected)
                out[period]['concentration']['removals'].append(dict(rank_by=by,n=n,weight_share=float(cp[sel].w_s.sum()/cp.w_s.sum()),contribution_points=100*float((cp[sel].w_s*cp[sel].gap_Y).sum()/cp.w_s.sum()),remaining_gap_points=100*avg(cp[~sel],'gap_Y')))
    # 2015 is already-exposed exploration. Rebuild its original all-scheduled own-promise pair.
    pilot=ROOT/'ideation/data/S6';pp=[];pilot_hashes=[]
    for m in range(1,13):
        path=pilot/f'2015-{m:02}.parquet';q=pq.read_table(path,filters=[('carrier','in',['UA','WN'])]).to_pandas();q=q.rename(columns={'date':'flight_date'});q['source_year']=2015
        pp.append(indicators(normalize(q)));pilot_hashes.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
    pf,cp=cellify(pd.concat(pp,ignore_index=True),False);out['pilot_2015']=summary(cp,pf);out['pilot_2015']['input_hashes']=pilot_hashes
    saved=json.loads((ROOT/'ideation/rounds/r3/pilot-S6/pairwise.json').read_text());pair=next(r for r in saved['pairs'] if r['a']=='UA' and r['b']=='WN');assert abs(avg(cp,'gap_Y')-pair['own'])<1e-12
    out['pilot_2015']['saved_pilot_own_gap_reproduced']=True;old=grouping(cp,['origin_id','dest_id']);old['oldgap']=old.gap_points/100;old=old.rename(columns={'weight':'oldweight'})
    for period,years in [('A',[2023,2024]),('B',[2025])]:
        cur=c[c.source_year.isin(years)];new=grouping(cur,['origin_id','dest_id']);both=new.merge(old[['origin_id','dest_id','oldgap','oldweight']],on=['origin_id','dest_id'],validate='one_to_one')
        p=both.oldweight/both.oldweight.sum();q=both.weight/both.weight.sum();a=both.oldgap;b=both.gap_points/100
        # Exact symmetric twofold decomposition on common directional routes.
        composition=float(((q-p)*(a+b)/2).sum());within=float(((q+p)*(b-a)/2).sum())
        out[period]['versus_2015']={'common_routes':len(both),'current_weight_share':float(both.weight.sum()/cur.w_s.sum()),'pilot_weight_share':float(both.oldweight.sum()/cp.w_s.sum()),'pilot_gap_common_routes':float((p*a).sum()),'current_gap_common_routes':float((q*b).sum()),'current_rates_pilot_route_weights':float((p*b).sum()),'route_composition_change_points':100*composition,'within_route_change_points':100*within}
        assert abs(composition+within-((q*b).sum()-(p*a).sum()))<1e-12
        finekeys=['origin_id','dest_id','band','month']
        fineold=grouping(cp,finekeys).rename(columns={'weight':'oldweight','gap_points':'oldgap_points'})
        fine=grouping(cur,finekeys).merge(fineold[finekeys+['oldweight','oldgap_points']],on=finekeys,validate='one_to_one')
        pp=fine.oldweight/fine.oldweight.sum();qq=fine.weight/fine.weight.sum();aa=fine.oldgap_points;bb=fine.gap_points
        out[period]['versus_2015_route_band_month']={'common_strata':len(fine),'current_weight_share':float(fine.weight.sum()/cur.w_s.sum()),'pilot_weight_share':float(fine.oldweight.sum()/cp.w_s.sum()),'pilot_gap_points':float((pp*aa).sum()),'current_gap_points':float((qq*bb).sum()),'composition_change_points':float(((qq-pp)*(aa+bb)/2).sum()),'within_stratum_change_points':float(((qq+pp)*(bb-aa)/2).sum())}
    dump('results.json',out)
    print(json.dumps({p:{'arrival_gap_points':100*out[p]['Y']['UA_minus_WN'],'schedule_difference_minutes':out[p]['schedule']['UA_minus_WN'],'actual_difference_minutes':out[p]['completed_cell_means']['actual']['UA_minus_WN'],'departure_timely_gap_points':100*out[p]['dep_timely']['UA_minus_WN'],'common_clock_gap_points':100*out[p]['common_mid']['UA_minus_WN']} for p in ['A','B','pilot_2015']},indent=2))
if __name__=='__main__':main()
