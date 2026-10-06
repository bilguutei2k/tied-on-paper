#!/usr/bin/env python3
"""Project registered identity/schedule columns; freeze support before simulations.

Arrow ConvertOptions(include_columns=FIELDS) prohibits materialization, inference,
conversion and logging of nonselected fields. No SELECT * on mixed source files.
CSV framing necessarily scans opaque bytes; only allowlisted values are decoded
into Arrow strings. The analysis process subsequently uses schedule-only Parquet.
"""
import argparse
import csv
import hashlib
import itertools
import json
import platform
import re
import zipfile
from pathlib import Path
import duckdb
import numpy as np
import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.parquet as pq
from common import EP, OUT, RAW, DERIVED, CARRIERS, dump, progress, seal_file, sha, utc
from rules import fixtures

FIELDS = ['Year', 'Month', 'FlightDate', 'Reporting_Airline',
          'DOT_ID_Reporting_Airline', 'IATA_CODE_Reporting_Airline',
          'Flight_Number_Reporting_Airline', 'OriginAirportID', 'DestAirportID', 'CRSDepTime']
KEYS = 'source_year,origin_id,dest_id,matching_date,band,week'

def sqlpath(path):
    return "'" + str(path).replace("'", "''") + "'"

def conn():
    c = duckdb.connect()
    c.execute('SET threads=10')
    c.execute("SET memory_limit='8GB'")
    c.execute(f'SET temp_directory={sqlpath(DERIVED / "duckdb-temp")}')
    return c

def records(c, sql):
    r = c.execute(sql)
    return [dict(zip([d[0] for d in r.description], row)) for row in r.fetchall()]

def copy(c, sql, name):
    p = DERIVED / name
    c.execute(f'COPY ({sql}) TO {sqlpath(p)} (FORMAT PARQUET, COMPRESSION ZSTD)')
    return seal_file(p)

def listseal(name, lines):
    p = DERIVED / name
    # Inputs are already explicitly sorted by registered numeric/lexicographic order.
    p.write_text(''.join(str(x) + '\n' for x in lines))
    return {**seal_file(p), 'size': len(lines), 'format': 'UTF-8, LF-terminated canonical sorted list'}

def metadata():
    m = json.loads((EP / 'data/docs-manifest.json').read_text())
    required = ['dictionary.html', 'airport-id.csv', 'airline-id.csv',
                'unique-carrier.csv', 'state-codes.csv', 'table-profile.html']
    entries = {Path(e['path']).name: e for e in m['sources']}
    for name in required:
        e = entries[name]
        assert e['status'] == 'saved' and sha(EP / e['path']) == e['sha256'], name
    dictionaries = {}
    for name in ['airline-id.csv', 'unique-carrier.csv', 'state-codes.csv']:
        dictionaries[name] = {r['Code']: r['Description'] for r in csv.DictReader((RAW/name).open())}
    identities = {}
    for code, dot in CARRIERS.items():
        desc = dictionaries['airline-id.csv'][str(dot)]
        assert desc.rsplit(':', 1)[-1].strip() == code
        assert dictionaries['unique-carrier.csv'][code] == desc.rsplit(':', 1)[0].strip()
        identities[code] = {'dot_id': dot, 'name': dictionaries['unique-carrier.csv'][code]}
    states = {k for k,v in dictionaries['state-codes.csv'].items() if ', Canada' not in v}
    airports = []
    for r in csv.DictReader((RAW/'airport-id.csv').open(encoding='cp1252')):
        mt = re.search(r', ([A-Z]{2}):', r['Description'])
        region = mt.group(1) if mt else None
        airports.append({'airport_id': int(r['Code']), 'description': r['Description'],
                         'region': region, 'domestic': region in states})
    airports.sort(key=lambda r: r['airport_id'])
    assert len({r['airport_id'] for r in airports}) == len(airports)
    pq.write_table(pa.Table.from_pylist(airports), DERIVED/'airport-metadata.parquet', compression='zstd')
    mapping = {'freeze_utc': utc(), 'input_columns': FIELDS, 'source_dictionary': entries['dictionary.html'],
               'carrier_identity': identities, 'airport_metadata': seal_file(DERIVED/'airport-metadata.parquet'),
               'domestic_region_codes': sorted(states), 'territory_policy': 'Includes PR, VI and BTS TT possessions; no territory excluded.',
               'status_rules': 'rules.status: failure precedence; finite signed delay <15; indeterminate Y=0,U=1; invalid values stop.',
               'schedule_rules': 'Integer local HHMM; 2400 alone next-day zero; source year retained; Monday of normalized matching date.',
               'historical_atcr_notes': {'url': entries['historical-atcr.pdf']['url'],
                    'local_byte_access': 'HTTP 403; no saved PDF and no invented hash',
                    'web_read': '2026-10-06, February 2016 report, printed page 3: domestic nonstop including territories; under-15 definition.',
                    'definition_snapshot': 'Authoritative field definitions sealed from saved BTS dictionary; METHOD supplies exact precedence and normalization.'},
               'fixtures': fixtures()}
    dump(OUT/'field-map.json', mapping)
    import scipy
    dump(OUT/'environment.json', {'python': platform.python_version(), 'numpy': np.__version__,
         'duckdb': duckdb.__version__, 'pyarrow': pa.__version__, 'scipy': scipy.__version__,
         'threads': 10, 'quantile': "numpy.quantile(method='linear')", 'rng': 'Generator(PCG64)',
         'bootstrap_draws': 5000, 'production_seed': 20261005})
    progress('Official dictionary, airport IDs, region/territory classification and eight code/DOT identities sealed in field-map.json before ingestion. Deterministic status/HHMM/boundary fixtures pass; no Monte Carlo outcomes generated. Historical ATCR notes read through web; local PDF and policy byte fetches failed 403, explicitly recorded without hashes.')

def project():
    manifest = json.loads((EP / 'data/flights-manifest.json').read_text())
    assert len(manifest['sources']) == 36
    assert all(e['status'] == 'saved' for e in manifest['sources'])
    cols = {n: pa.string() for n in FIELDS}
    rows = []
    h = hashlib.sha256()
    ids = DERIVED/'source-ids.txt'
    with ids.open('wb') as idout:
        for e in manifest['sources']:
            archive = EP/e['path']
            assert sha(archive) == e['sha256'] and archive.stat().st_size == e['bytes']
            year, month = map(int, archive.stem.split('-'))
            dest = DERIVED/f'schedule-{year}-{month:02}.parquet'
            n = 0
            writer = None
            with zipfile.ZipFile(archive) as z:
                name = next(i['name'] for i in e['members'] if i['name'].lower().endswith('.csv'))
                with z.open(name) as f:
                    reader = pacsv.open_csv(f, read_options=pacsv.ReadOptions(block_size=2**22, use_threads=False),
                        convert_options=pacsv.ConvertOptions(include_columns=FIELDS, column_types=cols,
                                                             strings_can_be_null=False))
                    for batch in reader:
                        t = pa.Table.from_batches([batch])
                        t = t.append_column('source_year', pa.array(np.full(batch.num_rows, year, dtype=np.int16)))
                        t = t.append_column('source_month', pa.array(np.full(batch.num_rows, month, dtype=np.int8)))
                        t = t.append_column('source_row', pa.array(np.arange(n+1, n+batch.num_rows+1, dtype=np.int64)))
                        if writer is None:
                            writer = pq.ParquetWriter(dest, t.schema, compression='zstd')
                        writer.write_table(t)
                        b = ''.join(f'{year}-{month:02}:{i:09}\n' for i in range(n+1,n+batch.num_rows+1)).encode()
                        h.update(b); idout.write(b); n += batch.num_rows
            assert writer is not None
            writer.close()
            rows.append({'year':year, 'month':month, 'rows':n, **seal_file(dest)})
            dump(EP/'data/structure-manifest.json', {'outcome_columns_read': [], 'projected_columns': FIELDS,
                 'derivatives': rows, 'source_order': 'numeric month, one-based CSV ordinal'})
            progress(f'Projected {year}-{month:02}: {n:,} source records. Arrow include_columns selected only the ten identity/schedule fields; no outcome inference, conversion, summary or logging.')
    return rows, {**seal_file(ids), 'size': sum(r['rows'] for r in rows), 'list_sha256':h.hexdigest()}

def build(rows, idseal):
    c = conn()
    paths = [str(EP/r['path']) for r in rows]
    c.execute('CREATE TABLE source AS SELECT * FROM read_parquet(?)', [paths])
    violations = c.execute('''SELECT count(*) FROM source WHERE try_cast(Year AS INTEGER) IS DISTINCT FROM source_year
        OR try_cast(Month AS INTEGER) IS DISTINCT FROM source_month OR try_cast(FlightDate AS DATE) IS NULL
        OR year(try_cast(FlightDate AS DATE)) IS DISTINCT FROM source_year
        OR month(try_cast(FlightDate AS DATE)) IS DISTINCT FROM source_month''').fetchone()[0]
    assert violations == 0, 'invalid date/source year-month'
    c.execute('CREATE TABLE fixed AS SELECT * FROM (VALUES '+','.join(f"('{a}',{b})" for a,b in CARRIERS.items())+') t(carrier,dot_id)')
    identity_bad = c.execute('''SELECT count(*) FROM source s JOIN fixed f ON s.Reporting_Airline=f.carrier
      WHERE try_cast(DOT_ID_Reporting_Airline AS INTEGER) IS DISTINCT FROM f.dot_id
         OR IATA_CODE_Reporting_Airline IS DISTINCT FROM f.carrier''').fetchone()[0]
    assert identity_bad == 0, 'carrier identity inconsistency'
    c.execute(f'CREATE TABLE airports AS SELECT * FROM read_parquet({sqlpath(DERIVED/"airport-metadata.parquet")})')
    other = c.execute('SELECT count(*) FROM source WHERE Reporting_Airline NOT IN (SELECT carrier FROM fixed)').fetchone()[0]
    c.execute('''CREATE TABLE candidate AS SELECT source_year,source_month,source_row,
      cast(FlightDate AS DATE) AS flight_date, Reporting_Airline AS carrier,
      cast(DOT_ID_Reporting_Airline AS INTEGER) AS dot_id,
      Flight_Number_Reporting_Airline AS flight_number,
      try_cast(OriginAirportID AS INTEGER) AS origin_id,try_cast(DestAirportID AS INTEGER) AS dest_id,
      CASE WHEN regexp_full_match(trim(CRSDepTime),'[0-9]+') THEN try_cast(CRSDepTime AS INTEGER) END AS dep_hhmm,
      CRSDepTime AS raw_dep_hhmm
      FROM source WHERE Reporting_Airline IN (SELECT carrier FROM fixed)''')
    international = c.execute('''SELECT count(*) FROM candidate c LEFT JOIN airports a ON c.origin_id=a.airport_id
      LEFT JOIN airports b ON c.dest_id=b.airport_id WHERE a.domestic=false OR b.domestic=false''').fetchone()[0]
    c.execute('''CREATE TABLE normalized AS WITH x AS (
      SELECT c.*,a.airport_id IS NOT NULL AND b.airport_id IS NOT NULL AS airports_valid,
        (dep_hhmm=2400 OR (dep_hhmm>=0 AND dep_hhmm<2400 AND dep_hhmm%100<60)) IS TRUE AS time_valid
      FROM candidate c LEFT JOIN airports a ON c.origin_id=a.airport_id
      LEFT JOIN airports b ON c.dest_id=b.airport_id
      WHERE coalesce(a.domestic,true) AND coalesce(b.domestic,true)), y AS (
      SELECT *, airports_valid AND time_valid AS valid_key,
        CASE WHEN dep_hhmm=2400 THEN 0 WHEN time_valid THEN dep_hhmm//100*60+dep_hhmm%100 END AS departure_minute,
        cast(flight_date + CASE WHEN dep_hhmm=2400 THEN INTERVAL 1 DAY ELSE INTERVAL 0 DAY END AS DATE) AS matching_date
      FROM x) SELECT *, departure_minute//120 AS band,
        cast(date_trunc('week',CASE WHEN valid_key THEN matching_date ELSE flight_date END) AS DATE) AS week,
        printf('%04d-%02d:%09d',source_year,source_month,source_row) AS source_id
      FROM y''')
    n, unique = c.execute('SELECT count(*),count(DISTINCT source_id) FROM normalized').fetchone()
    assert n == unique
    structure_seal=copy(c,'SELECT * FROM normalized ORDER BY source_year,source_month,source_row','structure.parquet')
    natural = records(c,'''SELECT source_year,source_month,carrier,flight_date,flight_number,origin_id,dest_id,
      dep_hhmm,count(*) AS rows FROM normalized GROUP BY ALL HAVING count(*)>1 ORDER BY ALL''')
    dump(OUT/'natural-key-collisions.json', {'groups':natural, 'policy':'Investigate; retain distinct source records. No deduplication by natural key.'})
    monthly = records(c,'''SELECT carrier,source_year,source_month,count(*) AS scheduled,
      count(*) FILTER(WHERE NOT valid_key) AS invalid_keys FROM normalized GROUP BY ALL ORDER BY ALL''')
    yearcounts = records(c,'''SELECT carrier,source_year,count(*) AS scheduled,
      count(*) FILTER(WHERE NOT valid_key) AS invalid_keys,
      count(*) FILTER(WHERE dep_hhmm=2400) AS midnight_2400,
      count(*) FILTER(WHERE year(matching_date)>source_year AND valid_key) AS normalized_next_year
      FROM normalized GROUP BY ALL ORDER BY ALL''')
    c.execute(f'''CREATE TABLE cells AS SELECT {KEYS},carrier,count(*) AS n_cs FROM normalized
       WHERE valid_key GROUP BY ALL''')
    cells = copy(c,'SELECT * FROM cells ORDER BY source_year,origin_id,dest_id,matching_date,band,carrier','cells.parquet')
    c.execute('''CREATE TABLE pair_cells AS SELECT a.source_year,a.origin_id,a.dest_id,a.matching_date,a.band,a.week,
      a.carrier AS a,b.carrier AS b,a.n_cs AS n_a,b.n_cs AS n_b,(a.n_cs+b.n_cs)/2.0 AS w_s
      FROM cells a JOIN cells b USING(source_year,origin_id,dest_id,matching_date,band,week)
      WHERE a.carrier<b.carrier''')
    support=[]
    for a,b in itertools.combinations(sorted(CARRIERS),2):
        stats = records(c,f'''SELECT source_year,sum(n_a)::BIGINT AS shared_a,sum(n_b)::BIGINT AS shared_b,
          count(DISTINCT week) AS weeks,count(*) AS strata,count(DISTINCT (origin_id,dest_id)) AS routes
          FROM pair_cells WHERE a='{a}' AND b='{b}' GROUP BY source_year ORDER BY source_year''')
        lookup = {r['source_year']:r for r in stats}
        reasons=[]
        for code in (a,b):
            if sum(r['carrier']==code and r['scheduled']>0 for r in monthly)!=36:reasons.append(f'{code}: missing source month')
        years=[]
        for year in (2023,2024,2025):
            r=lookup.get(year,{'source_year':year,'shared_a':0,'shared_b':0,'weeks':0,'strata':0,'routes':0})
            for k,limit in [('shared_a',500),('shared_b',500),('weeks',40)]:
                if r[k]<limit:reasons.append(f'{year}: {k}<{limit}')
            years.append(r)
        support.append({'a':a,'b':b,'supported':not reasons,'reasons':reasons,'years':years})
    roster=[(r['a'],r['b']) for r in support if r['supported']]
    incident=sorted({code for pair in roster for code in pair})
    c.execute('CREATE TABLE roster(a VARCHAR,b VARCHAR)')
    c.executemany('INSERT INTO roster VALUES (?,?)',roster) if roster else None
    c.execute('CREATE TABLE retained_pairs AS SELECT p.* FROM pair_cells p JOIN roster USING(a,b)')
    pc=copy(c,'SELECT * FROM retained_pairs ORDER BY a,b,source_year,origin_id,dest_id,matching_date,band','pair-cells.parquet')
    c.execute('''CREATE TABLE shared_member AS SELECT DISTINCT source_year,origin_id,dest_id,matching_date,band,week,carrier
      FROM (SELECT source_year,origin_id,dest_id,matching_date,band,week,a AS carrier FROM retained_pairs UNION ALL
       SELECT source_year,origin_id,dest_id,matching_date,band,week,b AS carrier FROM retained_pairs)''')
    unioncounts=records(c,f'''SELECT f.carrier,f.source_year,count(*) AS shared FROM normalized f JOIN shared_member s
      USING({KEYS},carrier) WHERE f.valid_key GROUP BY ALL ORDER BY ALL''')
    endpoints=records(c,f'''SELECT airport_id,count(*) AS endpoint_records FROM (
       SELECT f.origin_id AS airport_id FROM normalized f JOIN shared_member s USING({KEYS},carrier) WHERE f.valid_key
       UNION ALL SELECT f.dest_id FROM normalized f JOIN shared_member s USING({KEYS},carrier) WHERE f.valid_key)
       GROUP BY airport_id ORDER BY endpoint_records DESC,airport_id''')
    top=[r['airport_id'] for r in endpoints[:5]]
    dump(OUT/'airport-endpoint-counts.json',endpoints)
    weeks=records(c,'SELECT DISTINCT source_year,week FROM normalized ORDER BY source_year,week')
    routes=records(c,'SELECT DISTINCT origin_id,dest_id FROM retained_pairs ORDER BY origin_id,dest_id')
    components=[f'{a}|{b}|{period}|{contrast}|{assignment}' for a,b in roster
      for period in ('A','B') for contrast in ('G','D') for assignment in ('primary','low','high')]
    freezes={'source_rows':idseal,'supported_pairs':listseal('supported-pairs.txt',[f'{a}|{b}' for a,b in roster]),
      'incident_carriers':listseal('incident-carriers.txt',incident),
      'weeks':listseal('weeks.txt',[f"{r['source_year']}|{r['week'].isoformat()}" for r in weeks]),
      'routes':listseal('routes.txt',[f"{r['origin_id']}|{r['dest_id']}" for r in routes]),
      'omission_airports':listseal('omission-airports.txt',sorted(top)),
      'components':listseal('components.txt',components),
      'cells':{**cells,'size':c.execute('SELECT count(*) FROM cells').fetchone()[0]},
      'pair_cells':{**pc,'size':c.execute('SELECT count(*) FROM retained_pairs').fetchone()[0]}}
    diagnostics=records(c,'''WITH w AS (SELECT a,b,source_year,week,sum(w_s) AS mass FROM retained_pairs GROUP BY ALL)
      SELECT a,b,source_year,max(mass)/sum(mass) AS largest_week_share,
      sum(mass)*sum(mass)/sum(mass*mass) AS effective_weeks FROM w GROUP BY ALL ORDER BY ALL''')
    monthlymass=records(c,'''SELECT a,b,source_year,month(matching_date) AS normalized_month,
      sum(w_s) AS mass,sum(n_a) AS shared_a,sum(n_b) AS shared_b FROM retained_pairs GROUP BY ALL ORDER BY ALL''')
    # Source-month mass remains separately available through membership; midnight normalization cannot change source month.
    membership_seal=copy(c,f'''SELECT f.source_id,f.source_year,f.source_month,f.source_row,p.a,p.b,p.n_a,p.n_b,p.w_s,p.week
      FROM normalized f JOIN retained_pairs p USING({KEYS}) WHERE f.valid_key AND f.carrier IN (p.a,p.b)
      ORDER BY f.source_year,f.source_month,f.source_row,p.a,p.b''','pair-membership.parquet')
    source_month_mass=records(c,f'''SELECT f.carrier,f.source_year,f.source_month,count(*) AS shared
      FROM normalized f JOIN shared_member s USING({KEYS},carrier) WHERE f.valid_key GROUP BY ALL ORDER BY ALL''')
    quality=[{**r,'invalid_key_share':r['invalid_keys']/r['scheduled'],'passes':r['invalid_keys']/r['scheduled']<=.001} for r in yearcounts]
    illustrative=records(c,'''SELECT origin_id,dest_id,sum(n_cs) AS shared_scheduled FROM cells c JOIN shared_member s
      USING(source_year,origin_id,dest_id,matching_date,band,week,carrier)
      GROUP BY ALL ORDER BY shared_scheduled DESC,origin_id,dest_id LIMIT 1''')
    coverage={'freeze_utc':utc(),'status':'support_sealed_pending_commit','confirmation_outcomes_opened':False,
      'method_sha256':sha(EP/'METHOD.md'),'all_source_rows':idseal['size'],'candidate_domestic_rows':n,
      'exclusions':{'other_reporting_operators':other,'international_candidate_records':international,
                   'connections':'Not represented in the registered domestic nonstop source.',
                   'invalid_keys_retained_national':sum(r['invalid_keys'] for r in yearcounts)},
      'source_date_violations':violations,'source_identity_violations':identity_bad,'source_id_duplicates':n-unique,
      'natural_key_collision_groups':len(natural),'per_carrier_year':quality,'per_carrier_month':monthly,
      'all_28_pairs':support,'support_gate':{'supported_pairs':len(roster),'incident_carriers':len(incident),'passes':len(incident)>=4},
      'shared_union_counts':unioncounts,'source_month_shared_union':source_month_mass,
      'pair_normalized_month_mass':monthlymass,'weekly_weight_diagnostics':diagnostics,
      'omission_airport_ranking':top,'illustrative_route':illustrative,'frozen_sets':freezes,
      'exposure_log':['2015 pilot and historical 2014 schema/design notes read; no historical raw records opened.',
        'Inherited incidental 2024 ranking snippet disclosed by registration; no new contemporary outcome tables accessed.',
        'Only allowlisted identity/schedule columns materialized from 2023–2025.'],
      'structural_files':{'structure':structure_seal,'pair_membership':membership_seal},
      'code_hashes':{p.name:sha(p) for p in sorted(OUT.glob('*.py'))},
      'environment_sha256':sha(OUT/'environment.json'),'field_map_sha256':sha(OUT/'field-map.json'),
      'bootstrap_weights':'Not generated: resampler selection requires committed support and scenario generator.'}
    dump(OUT/'coverage.json',coverage)
    progress(f'Primary support audit complete: {n:,} candidate records; {len(roster)} supported pairs, {len(incident)} incident carriers. coverage.json seals all sets and all 28 eligibility decisions; no synthetic outcomes inspected. Sensitivity support still to freeze.')
    sensitivities(c, top)
    coverage['sensitivity_manifest_sha256']=sha(EP/'data/sensitivity-manifest.json')
    m=json.loads((EP/'data/structure-manifest.json').read_text())
    m['bulk_structural_derivatives']=coverage['structural_files']
    m['frozen_sets']=coverage['frozen_sets'];m['freeze_utc']=coverage['freeze_utc']
    dump(EP/'data/structure-manifest.json',m)
    coverage['structure_manifest_sha256']=sha(EP/'data/structure-manifest.json')
    dump(OUT/'coverage.json',coverage)
    # Gate process must not be able to traverse the mixed raw directory.
    RAW.chmod(0o000)
    progress('Schedule support and sensitivity derivatives sealed. Raw directory traversal disabled (mode 000); gate consumes only structure. STOP before synthetic generation: support-manifest commit is required by METHOD and only Claude may commit.')
    print({'source_rows':idseal['size'],'candidate_rows':n,'supported_pairs':len(roster),'carriers':len(incident),'outcomes_opened':False})

def sensitivities(c, top):
    results=[]
    for hours in (1,4):
        c.execute(f'''CREATE OR REPLACE TABLE sens_cells AS SELECT source_year,origin_id,dest_id,matching_date,
          departure_minute//{hours*60} AS band,week,carrier,count(*) AS n_cs
          FROM normalized WHERE valid_key GROUP BY ALL''')
        results.append(copy(c,'''SELECT a.source_year,a.origin_id,a.dest_id,a.matching_date,a.band,a.week,
          a.carrier AS a,b.carrier AS b,a.n_cs AS n_a,b.n_cs AS n_b,(a.n_cs+b.n_cs)/2.0 AS w_s
          FROM sens_cells a JOIN sens_cells b USING(source_year,origin_id,dest_id,matching_date,band,week)
          JOIN roster r ON a.carrier=r.a AND b.carrier=r.b
          ORDER BY a.carrier,b.carrier,a.source_year,a.origin_id,a.dest_id,a.matching_date,a.band''',f'pairs-{hours}h.parquet'))
    for airport in top:
        results.append(copy(c,f'''SELECT * FROM retained_pairs WHERE origin_id!={airport} AND dest_id!={airport}
          ORDER BY a,b,source_year,origin_id,dest_id,matching_date,band''',f'pairs-omit-{airport}.parquet'))
        results.append(copy(c,f'''SELECT source_id FROM normalized WHERE origin_id!={airport} AND dest_id!={airport}
          ORDER BY source_year,source_month,source_row''',f'national-omit-{airport}.parquet'))
    results.append(copy(c,'''SELECT *,1.0 AS equal_weight,2.0*n_a*n_b/(n_a+n_b) AS harmonic_weight
      FROM retained_pairs ORDER BY a,b,source_year,origin_id,dest_id,matching_date,band''','pairs-alternate-weights.parquet'))
    progress('Sensitivity support frozen: 1h/4h, equal/harmonic weights, five same-airport national/shared exclusions; no extra count pruning.')
    results.append(copy(c,'''SELECT a.source_year,a.origin_id,a.dest_id,a.matching_date,a.week,
      a.carrier AS a,b.carrier AS b,a.source_id AS source_id_a,b.source_id AS source_id_b,
      a.source_month AS source_month_a,b.source_month AS source_month_b,
      a.source_row AS source_row_a,b.source_row AS source_row_b,
      abs(a.departure_minute-b.departure_minute) AS minute_gap
      FROM normalized a JOIN normalized b USING(source_year,origin_id,dest_id,matching_date,week)
      JOIN roster r ON a.carrier=r.a AND b.carrier=r.b
      WHERE a.valid_key AND b.valid_key AND abs(a.departure_minute-b.departure_minute)<=30
      QUALIFY row_number() OVER(PARTITION BY a.source_id,b.carrier ORDER BY abs(a.departure_minute-b.departure_minute),b.departure_minute,b.source_month,b.source_row)=1
        AND row_number() OVER(PARTITION BY b.source_id,a.carrier ORDER BY abs(a.departure_minute-b.departure_minute),a.departure_minute,a.source_month,a.source_row)=1
      ORDER BY a.carrier,b.carrier,a.source_year,a.source_month,a.source_row''','nearest30.parquet'))
    stats=[]
    original={(r['carrier'],r['source_year']):r['scheduled'] for r in records(c,
        'SELECT carrier,source_year,count(*) AS scheduled FROM normalized GROUP BY ALL')}
    for item in results:
        path=EP/item['path']
        item['rows']=pq.ParquetFile(path).metadata.num_rows
        if path.name.startswith('pairs-'):
            support=records(c,f'''SELECT a,b,source_year,count(*) AS strata,
              sum(n_a) AS shared_a,sum(n_b) AS shared_b,count(DISTINCT week) AS weeks
              FROM read_parquet({sqlpath(path)}) GROUP BY ALL ORDER BY ALL''')
            retained=original
            if path.name.startswith('pairs-omit-'):
                airport=int(path.stem.rsplit('-',1)[1])
                retained={(r['carrier'],r['source_year']):r['scheduled'] for r in records(c,
                    f'SELECT carrier,source_year,count(*) AS scheduled FROM normalized WHERE origin_id!={airport} AND dest_id!={airport} GROUP BY ALL')}
            for r in support:
                for side in ('a','b'):
                    key=(r[side],r['source_year'])
                    r['original_n_'+side]=original[key];r['retained_n_'+side]=retained[key]
                    r['original_coverage_'+side]=r['shared_'+side]/original[key]
                    r['retained_coverage_'+side]=r['shared_'+side]/retained[key]
            stats.append({'path':item['path'],'support':support})
        elif path.name=='nearest30.parquet':
            stats.append({'path':item['path'],'support':records(c,f'''SELECT a,b,source_year,count(*) AS matches,
              count(DISTINCT week) AS weeks FROM read_parquet({sqlpath(path)}) GROUP BY ALL ORDER BY ALL''')})
    dump(EP/'data/sensitivity-manifest.json',{'frozen_utc':utc(),'files':results,'counts':stats,
       'roster':'Original supported pairs; positive denominators only; no new eligibility thresholds.',
       'equal_year_A':'Arithmetic average of separately computed 2023 and 2024 G,D; existing cell membership.',
       'year_separate':'Existing source-year cell membership.',
       'nearest30':'Reciprocal choices in one pass; across bands, same route/date/source year; equal match weights.'})
    progress('Reciprocal nearest ±30-minute schedule matches and all sensitivity counts/hashes frozen; no outcome fields read.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--metadata-only',action='store_true');args=ap.parse_args()
    DERIVED.mkdir(parents=True,exist_ok=True)
    metadata()
    if not args.metadata_only:
        rows,idseal=project();build(rows,idseal)

if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        # CSV framing exceptions can include an entire mixed-field input row.
        # Never expose the exception value or its chained source payload.
        progress(f'Snapshot stopped with {type(exc).__name__}; exception payload suppressed to preserve outcome blindness.')
        print({'snapshot':'stopped','error_type':type(exc).__name__,'outcomes_opened':False})
        raise SystemExit(1) from None
