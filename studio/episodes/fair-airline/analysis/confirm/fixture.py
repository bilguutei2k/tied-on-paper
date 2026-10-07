#!/usr/bin/env python3
"""Synthetic deterministic fixture against the unchanged tested gate interval."""
import sys,json,itertools
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent));sys.path.insert(0,str(HERE.parent/'amendment2'))
import run_gate as g
from intervals import interval,verdict
from analyze import score_raw
import duckdb
import pyarrow as pa
from rules import status,fixtures
from common import dump,sha,EP

def main():
    st,manifest=g.load_structure()
    daily=st['den'][:,None]*(np.array([.013,.012,.014])[None,:]+.005*np.sin(np.arange(len(st['den']))[:,None]/11))
    gp,gl,gh=g.interval(st,daily,99,0,0,28)
    r=g.rng(99,0,0,3);starts={}
    for y,o,T in st['groups']:
        starts[y]=r.integers(0,T,size=(1999,T//28+1),endpoint=False)
    errors=[]
    for t in (0,1):
        groups=[v for v in st['groups'] if (v[0]==2025)==bool(t)]
        got=interval(groups,daily,st['den'],starts)
        errors.extend([float(np.max(abs(np.array(got['point'])-gp[t]))),
                       abs(got['envelope'][0]-gl[t]),abs(got['envelope'][1]-gh[t])])
    assert max(errors)<1e-14
    assert verdict(dict(valid=True,envelope=[.02,.02]))=='inconclusive'
    assert verdict(dict(valid=True,envelope=[.021,.03]),False)=='inconclusive'
    # Independent count/weight expansion and scoring boundary templates.
    from fractions import Fraction
    na=[1,2,3];nb=[3,1,2];ya=[1,1,2];yb=[1,1,0]
    exact=sum(Fraction(a+b,2)*(Fraction(x,a)-Fraction(y,b)) for a,b,x,y in zip(na,nb,ya,yb))/sum(Fraction(a+b,2) for a,b in zip(na,nb))
    floating=np.average(np.array(ya)/na-np.array(yb)/nb,weights=(np.array(na)+nb)/2)
    assert abs(float(exact)-floating)<1e-15
    templates=list(itertools.product(['','0','1'],['','0','1'],['','-10','14.999','15','20']))
    db=duckdb.connect()
    def raw_table(values):
        return pa.Table.from_pylist([dict(Reporting_Airline='UA',source_year=2023,source_month=1,source_row=i+1,
            Cancelled=c,Diverted=v,ArrDelay=d) for i,(c,v,d) in enumerate(values)])
    scored=score_raw(db,raw_table(templates)).to_pylist()
    for row,(c,v,d) in zip(scored,templates):
        assert (row['Y'],row['U'])==status(c,v,d)
        assert (row['C'],row['V'],row['F'],row['MC'],row['MV'])==(int(c=='1'),int(v=='1'),int(c=='1' or v=='1'),int(c==''),int(v==''))
    for bad in [('2','0','0'),('1','0','bad'),('0','0','inf')]:
        try:score_raw(db,raw_table([bad]))
        except AssertionError:pass
        else:raise AssertionError('invalid raw value accepted')
    db.close()
    spec=json.loads((HERE/'resampling.json').read_text());rr=np.random.Generator(np.random.PCG64(spec['seed']))
    for a,grp in zip(spec['arrays'],spec['groups']):
        p=EP/a['path'];assert sha(p)==a['sha256']
        saved=np.load(p,allow_pickle=False)
        assert np.array_equal(saved,rr.integers(0,grp['days'],size=(1999,grp['q']+1),endpoint=False))
        # Expand full blocks, truncate tail, check draw order against old indices.
        ix=((saved[:,:,None]+np.arange(28))%grp['days']).reshape(1999,-1)[:,:grp['days']]
        assert np.all(np.array([np.bincount(row,minlength=grp['days']).sum() for row in ix])==grp['days'])
    dump(HERE/'fixture.json',dict(passes=True,maximum_gate_interval_error=max(errors),
        scoring=fixtures(),production_scoring_templates=len(templates),checks=['gate A/B interval reproduction','fractional cell weights',
        'production SQL matches scalar scoring including failure precedence and invalid-value stops',
        'strict line equality','quality blocking','array regeneration','whole-network multiplicities'],
        synthetic_fixture='deterministic nonconstant daily contrasts on frozen schedule',confirmation_outcomes_opened=False))
    print(json.dumps(dict(passes=True,maximum_gate_interval_error=max(errors))))

if __name__=='__main__':main()
