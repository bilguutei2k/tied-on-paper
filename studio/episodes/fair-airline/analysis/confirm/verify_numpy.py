"""Independent sorted-key joins and compensated per-flight summation; no SQL."""
import sys,json,argparse,math
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from common import EP,OUT,sha,dump
from analyze import sealed_table,preconditions

def keys(table,names):
    arrays=[]
    for name in names:
        a=table[name].to_numpy()
        if name=='matching_date':a=a.astype('datetime64[D]').astype('int64')
        arrays.append(a.astype('int64'))
    result=np.empty(len(arrays[0]),dtype=[(f'k{i}','<i8') for i in range(len(arrays))])
    for i,a in enumerate(arrays):result[f'k{i}']=a
    return result

def main(period):
    preconditions(period)
    r=json.loads((HERE/f'results-{period}.json').read_text());years=r['years']
    coverage=json.loads((OUT/'coverage.json').read_text())
    names=['source_year','origin_id','dest_id','matching_date','band']
    s=sealed_table(coverage['structural_files']['structure'],columns=names+['source_month','source_row','carrier','valid_key'],filters=[('source_year','in',years),('carrier','in',['UA','WN'])])
    p=sealed_table(coverage['frozen_sets']['pair_cells'],columns=names+['n_a','n_b','w_s'],filters=[('source_year','in',years),('a','==','UA'),('b','==','WN')])
    op=EP/r['inputs']['outcomes']['path'];assert sha(op)==r['inputs']['outcomes']['sha256']
    with op.open('rb') as f:o=pq.read_table(f)
    sk=keys(s,['source_year','source_month','source_row']);ok=keys(o,['source_year','source_month','source_row'])
    assert np.array_equal(sk,ok),'Source-row alignment changed'
    pk=keys(p,names);order=np.argsort(pk);sorted_pk=pk[order]
    assert np.all(sorted_pk[1:]!=sorted_pk[:-1])
    lookup=keys(s,names);pos=np.searchsorted(sorted_pk,lookup);safe=np.minimum(pos,len(pk)-1)
    matched=(pos<len(pk))&(sorted_pk[safe]==lookup)&s['valid_key'].to_numpy()
    carrier=s['carrier'].to_numpy();Y=o['Y'].to_numpy();U=o['U'].to_numpy()
    w=p['w_s'].to_numpy();W=math.fsum(w.tolist());contribution={};counts={}
    for c,ncol in [('UA','n_a'),('WN','n_b')]:
        sel=matched&(carrier==c);cell=order[safe[sel]]
        fw=w[cell]/p[ncol].to_numpy()[cell]
        contribution[c]=[math.fsum((fw*x[sel]).tolist())/W for x in [Y,U]]
        counts[c]=int(sel.sum());assert counts[c]==r['primary']['n'][c]
        allsel=carrier==c;ny=int(allsel.sum());yy=int(Y[allsel].sum());uu=int(U[allsel].sum())
        assert (ny,yy,uu)==(r['national'][c]['Y']['n'],r['national'][c]['Y']['numerator'],r['national'][c]['Y']['unknown'])
    d=contribution['UA'][0]-contribution['WN'][0]
    point=[d,d-contribution['WN'][1],d+contribution['UA'][1]]
    err=float(np.max(np.abs(np.array(point)-r['primary']['point'])))
    assert err<1e-12
    dp=EP/r['primary']['draw_file']['path'];assert sha(dp)==r['primary']['draw_file']['sha256']
    draws=np.load(dp,allow_pickle=False);assert draws.shape==(1999,3) and np.isfinite(draws).all()
    assert __import__('hashlib').sha256(draws.astype('<f8').tobytes()).hexdigest()==r['primary']['bootstrap_sha256']
    dump(HERE/f'verification-numpy-{period}.json',dict(passes=True,period=period,independent_per_flight_points=point,
        maximum_point_error=err,matched_flight_counts=counts,n=r['inputs']['outcomes']['rows'],draws=1999,
        checks=['independent NumPy sorted-key membership joins','compensated per-flight weight summation',
        'source-row alignment','national success/unknown denominators','finite saved draws and exact hashes']))
    print(json.dumps(dict(period=period,passes=True,maximum_point_error=err)))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('period',choices=['A','B']);main(ap.parse_args().period)
