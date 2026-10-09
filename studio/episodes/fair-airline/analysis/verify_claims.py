#!/usr/bin/env python3
"""Independent claim arithmetic; never reads reported results or review outputs.

Registered estimates: rebuild carrier/cell means from schedule and scored outcome
Parquets, independently evaluate Amendment 2 using sealed starts. Post-hoc checks:
rescore hash-verified raw monthly ZIPs; never import production/review functions.
DOT operating ranks/rates: raw records across every reporting operator. Marketing
source facts: the numeric Table 1C extract in CONTEXT.md, checked online against
the official reports; rank all ten rows. Direct Python PDF access returned 403.
No page is saved and marketing rates are not rederived from operating microdata. Pilot: exposed 2015 flight Parquets.
No new flight data, bootstrap selection, verdict rule, or claim status changes.
Run from any directory with ideation/.venv/bin/python. --compute-only is useful
before the proposed ledger exists; normal execution checks every ledger value.
"""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import argparse, calendar, concurrent.futures, datetime, hashlib, json, math, sys, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.compute as pc
import pyarrow.parquet as pq
from scipy.stats import t
from scipy.special import betaincinv
EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[2]
DER=EP/'data/derived'
KEY=['source_year','origin_id','dest_id','matching_date','band']
M={}; INPUTS=[]
REG='analysis/results.json'; POST='analysis/review_checks/results.json'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(2**20),b''):h.update(block)
    return h.hexdigest()

def record(path):
    INPUTS.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})

def put(file,key,value):
    if file=='analysis/claims_check.json' and not key.startswith('derived_metrics.'):key='derived_metrics.'+key
    if isinstance(value,np.generic):value=value.item()
    M[file+'::'+key]=value

def interval(c, column='gap', equal_year=False):
    """Direct circular indexing and per-draw variance; no cumulative-sum helper."""
    parts=[]
    for year,x in c.groupby('source_year',sort=True):
        year=int(year);T=366 if calendar.isleap(year) else 365;q,r=divmod(T,28)
        di=(x.matching_date-pd.Timestamp(year,1,1)).dt.days.to_numpy()
        assert ((di>=0)&(di<T)).all()
        n=np.bincount(di,weights=x.weight*x[column],minlength=T)
        w=np.bincount(di,weights=x.weight,minlength=T)
        def blocks(a,length):return a[(np.arange(T)[:,None]+np.arange(length))%T].sum(axis=1)
        fn,fw=blocks(n,28),blocks(w,28);hn,hw=blocks(n,r),blocks(w,r)
        ss=np.load(DER/f'confirm-starts-{year}.npy');assert ss.shape==(1999,q+1)
        bn=fn[ss[:,:q]].sum(axis=1)+hn[ss[:,q]]
        bw=fw[ss[:,:q]].sum(axis=1)+hw[ss[:,q]]
        assert (bw>0).all()
        parts.append((T,q,r,n.sum(),w.sum(),fn,fw,hn,hw,ss,bn,bw))
    total=sum(p[4] for p in parts)
    point=np.mean([p[3]/p[4] for p in parts]) if equal_year else sum(p[3] for p in parts)/total
    draw=np.mean([p[10]/p[11] for p in parts],axis=0) if equal_year else sum(p[10] for p in parts)/sum(p[11] for p in parts)
    vv=0.;vb=np.zeros(1999)
    for T,q,r,on,ow,fn,fw,hn,hw,ss,bn,bw in parts:
        center=on/ow if equal_year else point
        dcenter=bn/bw if equal_year else draw
        v=q*np.var(fn-center*fw,ddof=0)*T/(T-28)+np.var(hn-center*hw,ddof=0)*T/(T-r)
        b=q*np.var(fn[ss[:,:q]]-dcenter[:,None]*fw[ss[:,:q]],axis=1,ddof=1)
        b+=np.var(hn[ss[:,:q]]-dcenter[:,None]*hw[ss[:,:q]],axis=1,ddof=1)
        if equal_year:vv+=v/(len(parts)*ow)**2;vb+=b/(len(parts)*bw)**2
        else:vv+=v;vb+=b
    se=math.sqrt(vv) if equal_year else math.sqrt(vv)/total
    sb=np.sqrt(vb) if equal_year else np.sqrt(vb)/sum(p[11] for p in parts)
    assert np.isfinite(sb).all() and (sb>0).all() and se>0
    z=(draw-point)/sb;low,high=np.quantile(z,[.005,.995],method='linear')
    df=sum(p[1]-1 for p in parts);floor=t.ppf(.995,df)
    return {'point':float(point),'low':float(point-max(high,floor)*se),'high':float(point-min(low,-floor)*se),'se':se,'df':df}

def cell_table(f,hours=2,weighting='schedule'):
    q=f[f.valid_key].copy();q['band']=q.departure_minute//(60*hours)
    g=q.groupby(KEY+['carrier'],observed=True).agg(n=('Y','size'),Y=('Y','mean'),U=('U','mean')).unstack('carrier')
    g=g.dropna();c=g.index.to_frame(index=False)
    for carrier,side in [('UA','a'),('WN','b')]:
        for field in ['n','Y','U']:c[side+'_'+field]=g[field,carrier].to_numpy()
    c['weight']=(c.a_n+c.b_n)/2
    if weighting=='equal':c['weight']=1.
    if weighting=='harmonic':c['weight']=2*c.a_n*c.b_n/(c.a_n+c.b_n)
    c['gap']=c.a_Y-c.b_Y
    return c

def write_metric(prefix,c,equal_year=False):
    assign={'primary_unknowns_fail':'gap','lower_UA_unknowns_fail_WN_unknowns_succeed':'lower','upper_UA_unknowns_succeed_WN_unknowns_fail':'upper'}
    c=c.assign(lower=c.gap-c.b_U,upper=c.gap+c.a_U)
    ivs={k:interval(c,v,equal_year) for k,v in assign.items()}
    iv=ivs['primary_unknowns_fail'];lo=min(v['low'] for v in ivs.values());hi=max(v['high'] for v in ivs.values())
    put(REG,prefix+'.estimate',100*iv['point']);put(REG,prefix+'.interval[0]',100*lo);put(REG,prefix+'.interval[1]',100*hi)
    for k,v in ivs.items():
        for suffix,value in [('estimate',100*v['point']),('interval[0]',100*v['low']),('interval[1]',100*v['high'])]:put(REG,prefix+'.assignments.'+k+'.'+suffix,value)
    for carrier,side in [('UA','a'),('WN','b')]:put(REG,prefix+'.n.'+carrier,int(c[side+'_n'].sum()))
    put(REG,prefix+'.cells',len(c));put(REG,prefix+'.draws',1999);put(REG,prefix+'.df',iv['df'])
    weeks=c.matching_date-pd.to_timedelta(c.matching_date.dt.weekday,unit='D')
    put(REG,prefix+'.weeks',len(set(zip(c.source_year,weeks))))
    for j in range(3):put(REG,prefix+f'.original_se_pp[{j}]',100*ivs[list(assign)[j]]['se'])
    return 'UA advantage above two points' if lo>.02 else 'no material UA advantage under this rule' if hi<.02 else 'inconclusive'

def registered():
    cols=['source_year','source_month','source_row','carrier','origin_id','dest_id','matching_date','departure_minute','valid_key','source_id']
    f=pq.read_table(DER/'structure.parquet',columns=cols,filters=[('carrier','in',['UA','WN'])]).to_pandas()
    ys=pd.concat([pq.read_table(DER/f'confirm-outcomes-{p}.parquet').to_pandas() for p in ['A','B']],ignore_index=True)
    f=f.merge(ys,on=['source_year','source_month','source_row'],validate='one_to_one');del ys
    f['matching_date']=pd.to_datetime(f.matching_date)
    c=cell_table(f);near=pq.read_table(DER/'nearest30.parquet',filters=[('a','==','UA'),('b','==','WN')]).to_pandas()
    lookup=f.set_index('source_id')[['Y','U']]
    labels=[]
    for period,years,base in [('A',[2023,2024],'primary_2023_2024'),('B',[2025],'replication_2025')]:
        x=f[f.source_year.isin(years)];cc=c[c.source_year.isin(years)]
        verdict=write_metric(base+'.adjusted_gap_ua_minus_wn_pp',cc);put(REG,base+'.verdict',verdict);labels.append(verdict)
        national={}
        for carrier,side in [('UA','a'),('WN','b')]:
            xx=x[x.carrier==carrier];n=len(xx);national[carrier]=100*xx.Y.mean()
            p=base+'.unmatched_all_flights_on_time_pct.'+carrier
            for suffix,val in [('estimate',national[carrier]),('n',n),('numerator',int(xx.Y.sum())),('unknown_count',int(xx.U.sum()))]:put(REG,p+'.'+suffix,val)
            put(REG,base+'.matched_cell_coverage_pct.'+carrier+'.estimate',100*cc[side+'_n'].sum()/n)
            for field,label in [('C','cancellation'),('V','diversion'),('F','cancellation_or_diversion'),('MC','missing_cancellation_flag'),('MV','missing_diversion_flag'),('U','indeterminate'),('Y','on_time')]:
                p=base+'.national_secondary_rates_pct.'+carrier+'.'+label
                put(REG,p+'.estimate',100*xx[field].mean());put(REG,p+'.numerator',int(xx[field].sum()));put(REG,p+'.n',n)
                put(REG,base+'.weighted_matched_secondary_rates_pct.'+carrier+'.'+label+'.estimate',100*np.average(cc[side+'_'+field] if field in ['Y','U'] else weighted_secondary(x,cc,carrier,field),weights=cc.weight))
        put(REG,base+'.national_gap_ua_minus_wn_pp.estimate',national['UA']-national['WN'])
        variations={'window_1h':cell_table(x,1),'window_4h':cell_table(x,4),'equal_cell_weights':cell_table(x,2,'equal'),'harmonic_weights':cell_table(x,2,'harmonic')}
        for airport in [10397,11292,12889,12892,13930]:variations[f'omit_airport_{airport}']=cc[(cc.origin_id!=airport)&(cc.dest_id!=airport)]
        for y in years:variations[f'year_{y}']=cc[cc.source_year==y]
        if period=='A':variations['equal_year_A']=cc
        nn=near[near.source_year.isin(years)].copy();nn['matching_date']=pd.to_datetime(nn.matching_date);nn['weight']=1.;nn['a_n']=1;nn['b_n']=1
        for side in ['a','b']:
            vals=lookup.loc[nn['source_id_'+side]]
            nn[side+'_Y']=vals.Y.to_numpy();nn[side+'_U']=vals.U.to_numpy()
        nn['gap']=nn.a_Y-nn.b_Y;variations['reciprocal_nearest_30min']=nn
        for name,tab in variations.items():write_metric(base+'.sensitivities.'+name+'.gap_ua_minus_wn_pp',tab,name=='equal_year_A')
    put(REG,'replication_decision.replicated',labels[0]==labels[1] and labels[0]!='inconclusive')
    put(REG,'replication_decision.decision','replicated' if labels[0]==labels[1] and labels[0]!='inconclusive' else 'unsettled')
    return c

def weighted_secondary(f,c,carrier,field):
    g=f[f.carrier==carrier].assign(band=lambda x:x.departure_minute//120).groupby(KEY)[field].mean()
    return g.reindex(pd.MultiIndex.from_frame(c[KEY])).to_numpy()

RENAME={'Reporting_Airline':'carrier','DOT_ID_Reporting_Airline':'dot_id','IATA_CODE_Reporting_Airline':'iata','OriginAirportID':'origin_id','DestAirportID':'dest_id','CRSDepTime':'dep_hhmm','CRSElapsedTime':'scheduled_minutes','ActualElapsedTime':'actual_minutes','DepDelay':'dep_delay','ArrDelay':'arr_delay','Cancelled':'cancelled','Diverted':'diverted','FlightDate':'flight_date'}

def indicators(f):
    can=f.cancelled;div=f.diverted;arr=f.arr_delay;dep=f.dep_delay
    assert can.dropna().isin([0,1]).all() and div.dropna().isin([0,1]).all()
    failed=can.eq(1)|div.eq(1);complete=can.eq(0)&div.eq(0)&np.isfinite(arr)
    f['Y']=(complete & arr.lt(15)).astype(float);f['U']=(~failed & ~complete).astype(float)
    f['C']=can.eq(1).astype(float);f['V_only']=(~can.eq(1)&div.eq(1)).astype(float)
    f['late_arrival']=(complete & arr.ge(15)).astype(float)
    f['complete']=complete.astype(float)
    f['dep_timely']=(can.eq(0)&np.isfinite(dep)&dep.lt(15)).astype(float)
    f['dep_late']=(can.eq(0)&np.isfinite(dep)&dep.ge(15)).astype(float)
    f['dep_known']=(can.eq(0)&np.isfinite(dep)).astype(float)
    f['dep_unknown_non_cancel']=(can.eq(0)&~np.isfinite(dep)).astype(float)
    date=pd.to_datetime(f.flight_date);hh=f.dep_hhmm
    assert ((hh==2400)|((hh>=0)&(hh<2400)&(hh%100<60)&(hh%1==0))).all()
    f['matching_date']=date+pd.to_timedelta(hh.eq(2400).astype(int),unit='D')
    f['departure_minute']=np.where(hh==2400,0,(hh//100)*60+hh%100).astype(int);f['band']=f.departure_minute//120
    return f

def raw_month(entry):
    path=EP/entry['path'];year,month=map(int,path.stem.split('-'))
    assert path.stat().st_size==entry['bytes'] and sha(path)==entry['sha256']
    tables=[];nation={};rows=0
    keys=FROZEN[FROZEN.source_year==year][KEY]
    member=next(x['name'] for x in entry['members'] if x['name'].lower().endswith('.csv'))
    with zipfile.ZipFile(path) as z,z.open(member) as stream:
        strings=['Reporting_Airline','IATA_CODE_Reporting_Airline','FlightDate']
        reader=csv.open_csv(stream,read_options=csv.ReadOptions(block_size=2**22,use_threads=False),convert_options=csv.ConvertOptions(include_columns=list(RENAME),column_types={k:pa.string() if k in strings else pa.float64() for k in RENAME}))
        for batch in reader:
            q=batch.to_pandas().rename(columns=RENAME);rows+=len(q)
            success=q.cancelled.eq(0)&q.diverted.eq(0)&np.isfinite(q.arr_delay)&q.arr_delay.lt(15)
            totals=q.assign(success=success).groupby('carrier').agg(n=('success','size'),y=('success','sum'))
            for carrier,v in totals.iterrows():
                old=nation.setdefault(carrier,[0,0]);old[0]+=int(v.n);old[1]+=int(v.y)
            q=q[q.carrier.isin(['UA','WN'])].copy();q['source_year']=year
            assert q.dot_id.eq(q.carrier.map({'UA':19977,'WN':19393})).all() and q.iata.eq(q.carrier).all()
            q=indicators(q);q=q.merge(keys,on=KEY,validate='many_to_one');tables.append(q)
    return pd.concat(tables,ignore_index=True),{'year':year,'month':month,'source_rows':rows,'national':nation,'path':entry['path'],'sha256':entry['sha256']}

METRICS=['Y','U','C','V_only','late_arrival','dep_timely','dep_late','dep_known','dep_unknown_non_cancel']

def post_cells(f):
    grouped=f.groupby(KEY+['carrier'],observed=True)
    n=grouped.size().unstack().dropna();c=n.index.to_frame(index=False)
    c['weight']=(n.UA.to_numpy()+n.WN.to_numpy())/2
    for carrier,side in [('UA','a'),('WN','b')]:c[side+'_n']=n[carrier].to_numpy()
    for field in METRICS+['scheduled_minutes']:
        g=grouped[field].mean().unstack().reindex(n.index)
        for carrier in ['UA','WN']:c[carrier+'_'+field]=g[carrier].to_numpy()
    means=grouped.scheduled_minutes.mean().unstack()
    z=f.merge(means.rename(columns={'UA':'schedule_UA','WN':'schedule_WN'}).reset_index(),on=KEY,validate='many_to_one')
    for metric,deadline in [('common_mid',(z.schedule_UA+z.schedule_WN)/2),('common_UA',z.schedule_UA),('common_WN',z.schedule_WN)]:
        z[metric]=(z.complete.eq(1)&(z.dep_delay+z.actual_minutes).lt(deadline+15)).astype(float)
    z['equalized_mid']=(z.complete.eq(1)&(z.arr_delay+z.scheduled_minutes-(z.schedule_UA+z.schedule_WN)/2).lt(15)).astype(float)
    for metric in ['common_mid','common_UA','common_WN','equalized_mid']:
        g=z.groupby(KEY+['carrier'])[metric].mean().unstack().reindex(n.index)
        for carrier in ['UA','WN']:c[carrier+'_'+metric]=g[carrier].to_numpy()
    z=z[z.complete.eq(1)].assign(slack=lambda x:x.scheduled_minutes-x.actual_minutes)
    for label,field in [('actual','actual_minutes'),('dep_delay','dep_delay'),('slack','slack'),('sched_completed','scheduled_minutes')]:
        g=z.groupby(KEY+['carrier'])[field].mean().unstack().reindex(n.index)
        for carrier in ['UA','WN']:c[carrier+'_'+label]=g[carrier].to_numpy()
    for metric in METRICS+['common_mid','common_UA','common_WN','equalized_mid']:c['gap_'+metric]=c['UA_'+metric]-c['WN_'+metric]
    return c

def avg(c,col):return float(np.average(c[col],weights=c.weight))

def post_summary(period,c,f):
    for field,val in [('cells',len(c)),('weight',c.weight.sum())]:put(POST,period+'.'+field,val)
    for carrier,side in [('UA','a'),('WN','b')]:put(POST,period+'.flights.'+carrier,int(c[side+'_n'].sum()))
    for metric in METRICS+['common_mid','common_UA','common_WN','equalized_mid','schedule']:
        field='scheduled_minutes' if metric=='schedule' else metric
        a,b=avg(c,'UA_'+field),avg(c,'WN_'+field)
        for k,v in [('UA',a),('WN',b),('UA_minus_WN',a-b)]:put(POST,period+'.'+metric+'.'+k,v)
    selected=c[['UA_actual','WN_actual','UA_dep_delay','WN_dep_delay']].notna().all(axis=1);sub=c[selected]
    put(POST,period+'.completed_cell_means.cells',len(sub));put(POST,period+'.completed_cell_means.weight_share',sub.weight.sum()/c.weight.sum())
    for carrier in ['UA','WN']:put(POST,period+'.completed_cell_means.completed_rows_'+carrier,int((f.carrier.eq(carrier)&f.complete.eq(1)).sum()))
    for metric in ['actual','dep_delay','slack','sched_completed','schedule']:
        field='scheduled_minutes' if metric=='schedule' else metric
        a,b=avg(sub,'UA_'+field),avg(sub,'WN_'+field)
        for k,v in [('UA',a),('WN',b),('UA_minus_WN',a-b)]:put(POST,period+'.completed_cell_means.'+metric+'.'+k,v)
    for metric in ['C','V_only','late_arrival','U']:put(POST,period+'.decomposition_advantage_points.'+metric,-100*avg(c,'gap_'+metric))
    put(POST,period+'.own_minus_common_mid_points',100*(avg(c,'gap_Y')-avg(c,'gap_common_mid')))
    for carrier in ['UA','WN']:put(POST,period+'.departures_conditional_known.'+carrier,avg(c,carrier+'_dep_late')/avg(c,carrier+'_dep_known'))
    if period=='pilot_2015':return
    for metric in ['Y','dep_timely','dep_late','common_mid']:
        iv=interval(c,'gap_'+metric)
        for name,val in [('point',iv['point']),('interval[0]',iv['low']),('interval[1]',iv['high'])]:put(POST,period+'.interval_checks.'+metric+'.'+name,val)
    den=(c.origin_id==11292)|(c.dest_id==11292)
    for key,val in [('weight_share',c.loc[den,'weight'].sum()/c.weight.sum()),('contribution_points',100*(c.loc[den,'weight']*c.loc[den,'gap_Y']).sum()/c.weight.sum()),('gap_without_airport_points',100*avg(c[~den],'gap_Y'))]:put('analysis/claims_check.json',period+'.denver.'+key,val)
    route=c.assign(num=c.weight*c.gap_Y).groupby(['origin_id','dest_id']).agg(weight=('weight','sum'),num=('num','sum'))
    route['contribution']=100*route.num/c.weight.sum()
    put(POST,period+'.concentration.routes',len(route));put(POST,period+'.concentration.airports',len(set(c.origin_id)|set(c.dest_id)))
    for by,field in [('contribution_points','contribution'),('weight_share','weight')]:
        ranked=route.sort_values(field,ascending=False,kind='stable')
        for number in [1,5,10,20]:
            removed=pd.MultiIndex.from_frame(c[['origin_id','dest_id']]).isin(ranked.head(number).index)
            idx=([1,5,10,20].index(number))+(0 if by=='contribution_points' else 4)
            p=period+f'.concentration.removals[{idx}]'
            for key,val in [('n',number),('weight_share',c.loc[removed,'weight'].sum()/c.weight.sum()),('contribution_points',100*(c.loc[removed,'weight']*c.loc[removed,'gap_Y']).sum()/c.weight.sum()),('remaining_gap_points',100*avg(c[~removed],'gap_Y'))]:put(POST,p+'.'+key,val)
    for label,selection in [('before_10',c.band<5),('from_16',c.band>=8)]:
        sub=c[selection];put('analysis/claims_check.json',period+'.time.'+label+'.gap_pp',100*avg(sub,'gap_Y'));put('analysis/claims_check.json',period+'.time.'+label+'.weight_pct',100*sub.weight.sum()/c.weight.sum())
    # All plotted two-hour bands: independent raw-cell weighted sums, with
    # explicit local-clock bounds and normalized weight checks. No review CSV
    # or reported band values enter this recomputation.
    band_weight=0.0
    total_weight=math.fsum(c.weight.tolist())
    for band,sub in c.groupby('band'):
        assert 0 <= int(band) < 12
        weight=math.fsum(sub.weight.tolist());band_weight+=weight
        numerator=math.fsum((sub.weight*(sub.UA_Y-sub.WN_Y)).tolist())
        for k,v in [('gap_pp',100*numerator/weight),('weight_pct',100*weight/total_weight)]:
            put('analysis/claims_check.json',period+f'.bands.{band}.'+k,v)
    assert math.isclose(band_weight,total_weight,rel_tol=1e-12)
    month_values=[]
    for month,sub in c.groupby(c.matching_date.dt.month):
        value=100*avg(sub,'gap_Y');month_values.append((int(month),value))
        put('analysis/claims_check.json',period+f'.months.{month}.gap_pp',value)
        put('analysis/claims_check.json',period+f'.months.{month}.weight_pct',100*sub.weight.sum()/c.weight.sum())
    low=min(month_values,key=lambda x:x[1]);high=max(month_values,key=lambda x:x[1])
    for k,v in [('min_pp',low[1]),('min_month',low[0]),('max_pp',high[1]),('max_month',high[0])]:put('analysis/claims_check.json',period+'.months.'+k,v)
    return route

PDFS={2023:'https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202024%20ATCR%20revised%203-06-2025.pdf',2024:'https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202025%20ATCR.pdf',2025:'https://www.transportation.gov/sites/dot.gov/files/2026-03/February%20%202026%20ATCR.pdf'}

def dot_sources():
    # Numeric source-table extraction, not a report/results output or a page snapshot.
    context=(EP/'analysis/CONTEXT.md').read_text()
    block=context.split('<!-- DOT_MARKETING_NUMERIC_START -->')[1].split('<!-- DOT_MARKETING_NUMERIC_END -->')[0]
    tables={int(line.split(' ',1)[0]):json.loads(line.split(' ',1)[1]) for line in block.strip().splitlines()}
    record(EP/'analysis/CONTEXT.md')
    for year,url in PDFS.items():
        rows=tables[year];assert len(rows)==10
        INPUTS.append({'url':url,'source':'all annual Table 1C numeric rows independently extracted online into CONTEXT.md; no page saved','direct_python_access':'HTTP 403','verification':'published rates/counts are source facts; rank computed from all ten rows'})
        for carrier,name in [('UA','UNITED AIRLINES NETWORK'),('WN','SOUTHWEST AIRLINES')]:
            n,y=NATIONAL[year][carrier];rate=y/n
            rank=1+sum(v[1]/v[0]>rate for v in NATIONAL[year].values())
            prefix=f'descriptive_context.published_dot_annual.{year}.operating_carriers.{carrier}'
            for k,v in [('rank',rank),('rate_pct',100*rate),('n',n)]:put(REG,prefix+'.'+k,v)
            row=rows[name];rank=1+sum(r['rate_pct']>row['rate_pct'] for r in rows.values())
            prefix=f'descriptive_context.published_dot_annual.{year}.marketing_networks.{carrier}'
            for k,v in [('rank',rank),('rate_pct',row['rate_pct']),('n',row['n'])]:put(REG,prefix+'.'+k,v)


def gate_records():
    truths=json.loads((EP/'analysis/amendment2/truths.json').read_text())
    coverage=[];power=[];error=[];local=None
    def exact(k,n):
        return dict(count=int(k),n=n,estimate=100*k/n,**{'interval[0]':100*(betaincinv(k,n-k+1,.05) if k else 0),'interval[1]':100*(betaincinv(k+1,n-k,.95) if k<n else 1)})
    for item in truths:
        scenario=item['scenario'];sid=scenario['id'];path=EP/f'analysis/amendment2/bank1-candidate28-scenario{sid}.jsonl';record(path)
        rows=[json.loads(line) for line in path.read_text().splitlines() if line.strip()];assert len(rows)==2000
        low=np.array([r['low'] for r in rows]);high=np.array([r['high'] for r in rows]);quality=np.array([r['quality'] for r in rows])
        truth=np.array(item['truth']);verdict=np.where(low>.02,1,np.where(high<.02,-1,0));verdict[~quality]=0
        covered=(low<=truth.min(axis=1))&(high>=truth.max(axis=1));coverage.append(exact(covered.all(axis=1).sum(),len(rows)))
        for j,effect in enumerate(scenario['effects']):
            if effect<=.02:error.append(exact((verdict[:,j]==1).sum(),len(rows)))
            if effect>=.02:error.append(exact((verdict[:,j]==-1).sum(),len(rows)))
            if effect in [0.,.04]:power.append(exact((verdict[:,j]==(1 if effect>.02 else -1)).sum(),len(rows)))
        effects=scenario['effects']
        if effects in [[0.,0.],[.04,.04]]:power.append(exact((verdict==(1 if effects[0]>.02 else -1)).all(axis=1).sum(),len(rows)))
        if effects==[.03,.03]:local=exact((verdict==1).all(axis=1).sum(),len(rows))
    for name,event in [('minimum_joint_coverage',min(coverage,key=lambda x:x['interval[0]'])),('minimum_required_zero_or_four_point_power',min(power,key=lambda x:x['interval[0]'])),('worst_directional_false_verdict',max(error,key=lambda x:x['interval[1]'])),('three_point_replicated_power',local)]:
        for key,value in event.items():put(REG,'gate_validation.'+name+'.'+key,value)


def main():
    global FROZEN,NATIONAL
    args=argparse.ArgumentParser();args.add_argument('--compute-only',action='store_true');options=args.parse_args()
    for name in ['structure.parquet','confirm-outcomes-A.parquet','confirm-outcomes-B.parquet','pair-cells.parquet','nearest30.parquet']+[f'confirm-starts-{y}.npy' for y in [2023,2024,2025]]:record(DER/name)
    print('Rebuilding registered estimates and all sensitivity intervals...',flush=True)
    c=registered();FROZEN=c[KEY].drop_duplicates();del c
    print('Registered arithmetic complete; rescoring 36 raw archives...',flush=True)
    manifest=json.loads((EP/'data/flights-manifest.json').read_text());frames=[];audit=[];NATIONAL={y:{} for y in [2023,2024,2025]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for frame,qa in pool.map(raw_month,manifest['sources']):
            frames.append(frame);audit.append(qa)
            for carrier,vals in qa['national'].items():
                old=NATIONAL[qa['year']].setdefault(carrier,[0,0]);old[0]+=vals[0];old[1]+=vals[1]
    f=pd.concat(frames,ignore_index=True);del frames;c=post_cells(f)
    assert len(c)==len(FROZEN)
    for period,years in [('A',[2023,2024]),('B',[2025])]:post_summary(period,c[c.source_year.isin(years)],f[f.source_year.isin(years)])
    pilot=[]
    for month in range(1,13):
        path=ROOT/f'ideation/data/S6/2015-{month:02}.parquet';record(path)
        q=pq.read_table(path,filters=[('carrier','in',['UA','WN'])]).to_pandas().rename(columns={'date':'flight_date'});q['source_year']=2015;pilot.append(indicators(q))
    pf=pd.concat(pilot,ignore_index=True)
    # Restrict to cells where both operators scheduled, independent of outcomes.
    ns=pf.groupby(KEY+['carrier']).size().unstack().dropna();pf=pf.merge(ns.index.to_frame(index=False),on=KEY,validate='many_to_one')
    cp=post_cells(pf);post_summary('pilot_2015',cp,pf)
    print('Raw/pilot checks complete; re-ranking official source-table numeric extracts...',flush=True)
    dot_sources()
    # Design facts are checked against the retained method/amendment documents.
    method=(EP/'METHOD.md').read_text();am1=(EP/'analysis/amendment/AMENDMENT-1.md').read_text();am2=(EP/'analysis/amendment2/AMENDMENT-2.md').read_text()
    assert 'one additional timely completion per 50' in am1 and 'The line is +0.02' in am2
    assert 'chosen after the pilot and failed gate, before confirmation' in am1
    assert 'after two failed outcome-blind gates' in am2 and 'strictly less than\n15 minutes' in am1
    for key,value in [('design.line_pp',2),('design.per_scheduled_flights',50),('design.late_failure_minutes',15),('design.departure_window_hours',2),('design.nominal_interval_pct',99),('design.draws',1999),('design.block_days',28),('design.threshold_timing','post-pilot and post-failed-gate, before confirmation outcomes')]:put('analysis/claims_check.json',key,value)
    gate_records()
    derived={}
    for name,value in M.items():
        if name.startswith('analysis/claims_check.json::derived_metrics.'):
            path=name.split('::derived_metrics.',1)[1].split('.');node=derived
            for part in path[:-1]:node=node.setdefault(part,{})
            node[path[-1]]=value
    checks=[];errors=[]
    if not options.compute_only:
        ledger=json.loads((EP/'CLAIMS.json').read_text());assert ledger['schema_version']==1
        seen=set()
        for claim in ledger['claims']:
            assert claim['id'] not in seen;seen.add(claim['id']);assert claim['status'] in {'proposed', 'verified'}
            assert not claim['exploratory'] or any('not registered' in s.lower() or 'pilot' in s.lower() for s in claim['limitations'])
            for val in claim['values']:
                name=claim['result_file']+'::'+val['key'];actual=M.get(name);digits=val['digits'];stated=val['stated']
                ok=(actual==stated) if digits is None else actual is not None and round(float(actual),digits)==round(float(stated),digits)
                item={'claim':claim['id'],'result_file':claim['result_file'],'key':val['key'],'stated':stated,'digits':digits,'recomputed':actual,'passed':bool(ok)}
                checks.append(item)
                if not ok:errors.append(item)
    report={'schema_version':1,'written_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'claim_count':len(seen) if not options.compute_only else 0,'ledger_sha256':sha(EP/'CLAIMS.json') if not options.compute_only else None,'verifier_sha256':sha(Path(__file__)),'checks':checks,'checks_passed':sum(x['passed'] for x in checks),'checks_total':len(checks),'all_pass':bool(checks) and not errors,'discrepancies':errors,'method':'Independent derived-cell estimates and studentized intervals; fresh raw post-hoc scoring; operating DOT ranks/rates rebuilt from raw records and marketing ranks re-ranked from complete official numeric source-table extracts in CONTEXT.md (published rates are source facts; Python access returned 403). No results.json or review output is read. Saved starts are inputs, not a fresh bootstrap. Proposed statuses remain unchanged.','inputs':INPUTS,'raw_archives':audit,'derived_metrics':derived,'recomputed':M}
    (EP/'analysis/claims_check.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({k:report[k] for k in ['claim_count','checks_passed','checks_total','all_pass','discrepancies']},indent=2),flush=True)
    if errors:sys.exit(1)

if __name__=='__main__':main()
