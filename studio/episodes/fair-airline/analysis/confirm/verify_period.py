#!/usr/bin/env python3
"""Independent per-flight numerical derivation, restricted to an opened period."""
import sys,json,argparse,math
from pathlib import Path
import duckdb
import numpy as np
import pyarrow.parquet as pq
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from common import EP,OUT,sha,dump
from analyze import sealed_table,preconditions

def main(period):
    preconditions(period)
    r=json.loads((HERE/f'results-{period}.json').read_text());years=r['years']
    coverage=json.loads((OUT/'coverage.json').read_text())
    db=duckdb.connect();db.execute('SET threads=1')
    db.register('s',sealed_table(coverage['structural_files']['structure'],filters=[('source_year','in',years),('carrier','in',['UA','WN'])]))
    db.register('p',sealed_table(coverage['frozen_sets']['pair_cells'],filters=[('source_year','in',years),('a','==','UA'),('b','==','WN')]))
    op=EP/r['inputs']['outcomes']['path'];assert sha(op)==r['inputs']['outcomes']['sha256']
    with op.open('rb') as f:db.register('o',pq.read_table(f))
    # Independent per-flight expansion: no production cell-mean aggregation.
    vals=db.execute('''SELECT s.carrier,sum(o.Y*p.w_s/CASE WHEN s.carrier='UA' THEN p.n_a ELSE p.n_b END),
        sum(o.U*p.w_s/CASE WHEN s.carrier='UA' THEN p.n_a ELSE p.n_b END),count(*)
        FROM s JOIN o USING(source_year,source_month,source_row)
        JOIN p USING(source_year,origin_id,dest_id,matching_date,band)
        WHERE s.valid_key GROUP BY s.carrier ORDER BY s.carrier''').fetchall()
    weight=db.execute('SELECT sum(w_s) FROM p').fetchone()[0]
    a,b=vals;d=(a[1]-b[1])/weight;point=[d,d-b[2]/weight,d+a[2]/weight]
    error=float(np.max(abs(np.array(point)-r['primary']['point'])))
    assert error<1e-12 and [a[3],b[3]]==[r['primary']['n']['UA'],r['primary']['n']['WN']]
    for c,n,y,u in db.execute('SELECT s.carrier,count(*),sum(o.Y),sum(o.U) FROM s JOIN o USING(source_year,source_month,source_row) GROUP BY s.carrier').fetchall():
        assert r['national'][c]['Y']['n']==n and r['national'][c]['Y']['numerator']==y and r['national'][c]['Y']['unknown']==u
    draw=EP/r['primary']['draw_file']['path'];assert sha(draw)==r['primary']['draw_file']['sha256']
    array=np.load(draw,allow_pickle=False);assert array.shape==(1999,3) and np.isfinite(array).all()
    assert __import__('hashlib').sha256(array.astype('<f8').tobytes()).hexdigest()==r['primary']['bootstrap_sha256']
    expected=['window_1h','window_4h','equal_cell_weights','harmonic_weights','reciprocal_nearest_30min']+[f'omit_airport_{a}' for a in coverage['omission_airport_ranking']]+[f'year_{y}' for y in years]+(['equal_year_A'] if period=='A' else [])
    assert set(expected)==set(r['sensitivities'])
    assert all(v['descriptive_only'] for v in r['sensitivities'].values())
    dump(HERE/f'verification-{period}.json',dict(passes=True,independent_per_flight_points=point,maximum_point_error=error,
        checks=['independent expanded flight weights and counts','national success/unknown denominators',
        'all sealed primary draws finite and hash-identical','all registered sensitivity keys','sensitivities descriptive'],
        period=period,source_rows=r['inputs']['outcomes']['rows'],draws=1999))
    print(json.dumps(dict(period=period,passes=True,maximum_point_error=error)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('period',choices=['A','B']);main(p.parse_args().period)
