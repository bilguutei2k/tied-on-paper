#!/usr/bin/env python3
"""Independent checks of selected schedule derivatives only; no raw access."""
import json
import os
import stat
import pyarrow.parquet as pq
from common import EP, OUT, RAW, DERIVED, sha, dump, utc, progress
from snapshot import conn, sqlpath
from blind_guard import install, verify_denial

install()

def main():
    coverage=json.loads((OUT/'coverage.json').read_text())
    sources=json.loads((EP/'data/structure-manifest.json').read_text())
    sensitivity=json.loads((EP/'data/sensitivity-manifest.json').read_text())
    hashes=list(sources['derivatives'])+list(coverage['frozen_sets'].values())
    hashes+=list(coverage['structural_files'].values())+sensitivity['files']
    for r in hashes:
        p=EP/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    allowed=set(sources['projected_columns'])|{'source_year','source_month','source_row'}
    for r in sources['derivatives']:
        assert set(pq.ParquetFile(EP/r['path']).schema_arrow.names)==allowed
    assert verify_denial()
    c=conn()
    for name,file in [('f','structure.parquet'),('cells','cells.parquet'),
                      ('pairs','pair-cells.parquet'),('membership','pair-membership.parquet'),('nearest','nearest30.parquet')]:
        c.execute(f'CREATE VIEW {name} AS SELECT * FROM read_parquet({sqlpath(DERIVED/file)})')
    n,u=c.execute('SELECT count(*),count(DISTINCT source_id) FROM f').fetchone()
    assert n==u==coverage['candidate_domestic_rows']
    invalid=c.execute('''SELECT count(*) FROM f WHERE valid_key AND (
      departure_minute IS DISTINCT FROM CASE WHEN dep_hhmm=2400 THEN 0 ELSE (dep_hhmm//100)*60+dep_hhmm%100 END
      OR band IS DISTINCT FROM departure_minute//120
      OR matching_date IS DISTINCT FROM cast(flight_date+CASE WHEN dep_hhmm=2400 THEN INTERVAL 1 DAY ELSE INTERVAL 0 DAY END AS DATE)
      OR week IS DISTINCT FROM cast(date_trunc('week',matching_date) AS DATE))''').fetchone()[0]
    assert invalid==0
    national_only=c.execute("SELECT count(*) FROM f WHERE NOT valid_key AND week IS DISTINCT FROM cast(date_trunc('week',flight_date) AS DATE)").fetchone()[0]
    assert national_only==0
    assert c.execute('SELECT sum(n_cs) FROM cells').fetchone()[0]==c.execute('SELECT count(*) FROM f WHERE valid_key').fetchone()[0]
    assert c.execute('SELECT count(*) FROM pairs WHERE w_s IS DISTINCT FROM (n_a+n_b)/2.0').fetchone()[0]==0
    expected=c.execute('SELECT sum(n_a+n_b) FROM pairs').fetchone()[0]
    members,distinct=c.execute('SELECT count(*),count(DISTINCT (source_id,a,b)) FROM membership').fetchone()
    assert members==distinct==expected
    nearest=c.execute('''SELECT count(*) FROM nearest WHERE minute_gap>30 OR minute_gap<0''').fetchone()[0]
    assert nearest==0
    collision=c.execute('''SELECT count(*) FROM (SELECT a,b,source_id_a,count(*) AS n FROM nearest GROUP BY ALL HAVING count(*)>1)
      UNION ALL SELECT count(*) FROM (SELECT a,b,source_id_b,count(*) AS n FROM nearest GROUP BY ALL HAVING count(*)>1)''').fetchall()
    assert all(r[0]==0 for r in collision)
    assert coverage['support_gate']['passes']
    assert all(len(r['years'])==3 and all(y['shared_a']>=500 and y['shared_b']>=500 and y['weeks']>=40 for y in r['years']) for r in coverage['all_28_pairs'] if r['supported'])
    for item in sensitivity['counts']:
        if 'pairs-' in item['path']:
            for r in item['support']:
                for side in ('a','b'):
                    assert abs(r['retained_coverage_'+side]*r['retained_n_'+side]-r['shared_'+side])<1e-8
                    assert r['retained_n_'+side]<=r['original_n_'+side]
    result={'verified_utc':utc(),'passes':True,'hashed_artifacts':len(hashes),
            'candidate_records':n,'pair_memberships':members,
            'normalization_discrepancies':invalid,'national_only_week_discrepancies':national_only,
            'raw_access_denial':'Python audit hook tested; mode reset by workspace between calls','confirmation_outcomes_opened':False,
            'checks':['all schedule-only derivative hashes and schemas','source-ID uniqueness',
              'independent normalized date/week/minute formula','cell national denominator conservation',
              'pair weights and unique record membership','nearest-match distance and disjointness',
              'eligibility on every frozen year','original/retained sensitivity denominator consistency']}
    dump(OUT/'structure-verification.json',result)
    progress(f'Independent schedule-derivative verification passes: {len(hashes)} artifact hash/schema checks, normalization, denominators, pair membership, nearest disjointness, eligibility and sensitivity coverage. Process audit hook rejects raw opens. No synthetic or confirmation outcomes accessed.')
    print(result)

if __name__=='__main__':main()
