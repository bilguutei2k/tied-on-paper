#!/usr/bin/env python3
"""Independent post-gate checks: no new evaluation bank or threshold changes."""
import json, math, hashlib
from pathlib import Path
import run_gate as gate
import numpy as np
from scipy.optimize import brentq
from scipy.stats import binom
from rules import fixtures, status
from simulation_model import read_sealed
import duckdb

HERE=Path(__file__).resolve().parent

def bound(k,n):
    lo=0. if not k else brentq(lambda p:binom.sf(k-1,n,p)-.05,1e-15,1-1e-15,xtol=1e-14)
    hi=1. if k==n else brentq(lambda p:binom.cdf(k,n,p)-.05,1e-15,1-1e-15,xtol=1e-14)
    return lo,hi

def main():
    result=json.loads((HERE/'results.json').read_text());assert result['status']!='RUNNING'
    checked_bounds=0;max_bias_error=0.;replays=[];hashes={}
    st,manifest=gate.load_structure()
    assert manifest['cells_sha256']==json.loads((HERE/'structure.json').read_text())['cells_sha256']
    assert np.all(st['oi']!=st['di']) # the exact variance formula assumes distinct endpoints
    status_checks=fixtures()
    for n in [x[c] for x in manifest['support'] for c in ('UA','WN')]:
        assert (n//1000)*1000<=n and (n//1000+1)*1000>n
    # Known-failure and missing status templates reconstruct the count shortcut.
    templates=[(0,0,0),(0,0,None),(1,0,None),(0,1,None),(0,0,20)]
    assert [status(*x) for x in templates]==[(1,0),(0,1),(0,0),(0,0),(0,0)]
    # Independently check frozen pair-membership row counts, with no new matching.
    coverage=json.loads((gate.OUT/'coverage.json').read_text())
    table=read_sealed(coverage['structural_files']['pair_membership'])
    db=duckdb.connect();db.execute('SET threads=10');db.register('members',table)
    rows=db.execute("SELECT source_year,count(*),count(DISTINCT source_id) FROM members WHERE a='UA' AND b='WN' GROUP BY ALL ORDER BY ALL").fetchall()
    assert len(rows)==3
    for (year,count,unique),support in zip(rows,manifest['support']):
        assert year==support['year'] and count==unique==support['UA']+support['WN']
    db.close();del table
    # Independent bootstrap algorithm: reconstruct integer multiplicities and use
    # a weighted dot product instead of the runner's indexed-day summation.
    daily=np.column_stack([st['den']*.013,st['den']*.012,st['den']*.014])
    # Vary dates so SD is positive, without any generated flight outcome.
    daily += st['den'][:,None]*np.sin(np.arange(len(daily))[:,None])*.005
    bootstrap_checks=[]
    for candidate in gate.DESIGN['candidates']:
        point,low,high=gate.interval(st,daily,99,0,0,candidate)
        r=gate.rng(99,0,0,3);B=gate.DESIGN['draws'];num=[np.zeros((B,3)),np.zeros((B,3))];den=[np.zeros(B),np.zeros(B)]
        for year,offset,days in st['groups']:
            t=int(year==2025);matrix=[]
            for b in range(B):
                if candidate==1:
                    ix=r.integers(0,days,size=days,endpoint=False)
                else:
                    starts=r.integers(0,days,size=math.ceil(days/candidate),endpoint=False)
                    ix=np.array([(int(start)+j)%days for start in starts for j in range(candidate)])[:days]
                matrix.append(np.bincount(ix,minlength=days))
            matrix=np.array(matrix,dtype=float);sl=slice(offset,offset+days)
            num[t]+=matrix@daily[sl];den[t]+=matrix@st['den'][sl]
        sd=np.array([(num[t]/den[t][:,None]).std(axis=0,ddof=1) for t in (0,1)])
        assert np.max(np.abs(low-(point-gate.DESIGN['interval_critical']*sd).min(axis=1)))<1e-12
        assert np.max(np.abs(high-(point+gate.DESIGN['interval_critical']*sd).max(axis=1)))<1e-12
        bootstrap_checks.append(candidate)
    for report in result['scenarios']:
        bank=report['bank'];candidate=report['candidate'];sid=report['scenario']['id']
        path=HERE/f'bank{bank}-candidate{candidate}-scenario{sid}.jsonl'
        hashes[path.name]=gate.sha(path)
        records=[json.loads(line) for line in path.read_text().splitlines()]
        n=1000 if bank==0 else 2000
        assert len(records)==n and [r['rep'] for r in records]==list(range(n))
        if 'preserved_datasets' in report:
            prefix = b''.join(path.read_bytes().splitlines(keepends=True)[:report['preserved_datasets']])
            assert hashlib.sha256(prefix).hexdigest() == report['preserved_file_sha256']
        truth=np.array(report['truth'])
        for t in (0,1):
            for k in (0,1,2):
                values=[x['point'][t][k]-truth[t,k] for x in records]
                mean=math.fsum(values)/n
                se=math.sqrt(math.fsum((x-mean)**2 for x in values)/(n-1)/n)
                bb=abs(mean)+1.96*se
                max_bias_error=max(max_bias_error,abs(bb-report['bias_bound'][t][k]))
                assert abs(bb-report['bias_bound'][t][k])<1e-12
        for row in records:
            if row['low'] is None:
                assert row['covered']==[False,False] and row['verdict']==[0,0]
            else:
                for t in (0,1):
                    expected=0 if not row['quality'] else (1 if row['low'][t]>.02 else -1 if row['high'][t]<.02 else 0)
                    assert row['verdict'][t]==expected
                    assert row['covered'][t]==bool(row['low'][t]<=truth[t].min() and row['high'][t]>=truth[t].max())
        # Recompute event counts separately from summary implementation.
        metrics=[(report['joint_coverage'],sum(all(x['covered']) for x in records)),
                 (report['valid'],sum(x['low'] is not None for x in records))]
        for t in (0,1):
            d=report['scenario']['effects'][t];r=report['periods'][t]
            metrics.append((r['coverage'],sum(x['covered'][t] for x in records)))
            for key,direction in [('false_above',1),('false_below',-1),('power',1 if d>.02 else -1)]:
                if key in r:metrics.append((r[key],sum(x['verdict'][t]==direction for x in records)))
        for key in ('replicated_power','local_power'):
            if key in report:
                direction=1 if report['scenario']['effects'][0]>.02 else -1
                metrics.append((report[key],sum(x['verdict']==[direction,direction] for x in records)))
        for metric,count in metrics:
            assert count==metric['count'] and n==metric['n']
            lo,hi=bound(count,n)
            assert abs(lo-metric['lower'])<1e-10 and abs(hi-metric['upper'])<1e-10
            checked_bounds+=1
        # Derive acceptance independently from verified bounds, including both
        # false directions at the line and repeated-decision power off the line.
        accepted = max(map(max, report['bias_bound'])) <= .002
        accepted &= report['valid']['rate'] >= .95 and report['joint_coverage']['lower'] >= .92
        for t, period in enumerate(report['periods']):
            accepted &= period['coverage']['lower'] >= .92
            d = report['scenario']['effects'][t]
            assert ('false_above' in period) == (d <= .02)
            assert ('false_below' in period) == (d >= .02)
            assert ('power' in period) == (d in (0., .04))
            for key in ('false_above', 'false_below'):
                if key in period: accepted &= period[key]['upper'] <= .025
            if 'power' in period: accepted &= period['power']['lower'] >= .80
        if 'replicated_power' in report: accepted &= report['replicated_power']['lower'] >= .80
        assert bool(accepted) == report['passes']
        # Replay original replicate zero for each attempted candidate/bank/scenario.
        s=gate.scenarios()[sid];replay=gate.one(st,s,gate.prepare(st,s),bank,0,candidate)
        assert replay==records[0]
        replays.append([bank,candidate,sid,0])
    selected=result.get('selected')
    # Every completed attempt follows the committed early-stop order.
    for bank in (0, 1):
        for candidate in gate.DESIGN['candidates']:
            reports = [x for x in result['scenarios'] if x['bank']==bank and x['candidate']==candidate]
            assert [x['scenario']['id'] for x in reports] == list(range(len(reports)))
            failures = [x for x in reports if x['scenario']['required'] and not x['passes']]
            if failures: assert len(failures)==1 and failures[0] is reports[-1]
    if result['status']=='FAIL' and selected is None:
        for candidate in gate.DESIGN['candidates']:
            reports = [x for x in result['scenarios'] if x['bank']==0 and x['candidate']==candidate]
            assert reports and reports[-1]['scenario']['required'] and not reports[-1]['passes']
        assert not any(x['bank']==1 for x in result['scenarios'])
    if result['status']=='PASS':
        for bank in (0,1):
            reports=[x for x in result['scenarios'] if x['bank']==bank and x['candidate']==selected]
            assert {x['scenario']['id'] for x in reports}==set(range(20))
            assert all(x['passes'] for x in reports if x['scenario']['required'])
    gate.dump(HERE/'verification.json',dict(passes=True,status_fixtures=status_checks,
      membership_counts=rows,bootstrap_multiplicity_checks=bootstrap_checks,
      maximum_bias_recalculation_error=max_bias_error,exact_binomial_checks=checked_bounds,
      original_replicate_replays=replays,records_sha256=hashes,
      new_evaluation_datasets=0,confirmation_outcomes_opened=False))
    print(json.dumps(dict(passes=True,scenarios=len(result['scenarios']),binomial_checks=checked_bounds)))

if __name__=='__main__':main()
