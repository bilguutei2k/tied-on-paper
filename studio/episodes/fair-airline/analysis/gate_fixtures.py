"""Deterministic real-count status/key cutoff fixtures; no confirmation I/O."""
import numpy as np
from common import OUT,dump,utc
from rules import status,fixtures
from gate_runtime import components,verdict


def execute(rt):
    checks=dict(fixtures())
    # Give all records a known timely completion, then construct exact integer
    # cutoff counts separately within every frozen carrier/source-year cohort.
    # These fixtures test ingestion/quality blocking, not variance or coverage.
    for above in (False,True):
        ycounts=rt.model.n.astype(np.int64).copy()
        ucounts=np.zeros_like(ycounts)
        key_invalid=rt.invalid_n.copy()
        unknown=np.zeros(24,dtype=np.int64)
        for cy in range(24):
            selected=np.flatnonzero(rt.cy==cy)
            target=len(selected)//1000+int(above)
            unknown[cy]=target
            # Registered precedence: completed missing delay is indeterminate;
            # known failures cannot become successes under any endpoint.
            assert status(0,0,None)==(0,1)
            ix=selected[:target]
            np.add.at(ycounts,rt.pid[ix],-1);np.add.at(ucounts,rt.pid[ix],1)
            existing=int(key_invalid[cy])
            assert existing<=target
            key_invalid[cy]=target
        wy=(rt.aggregate@ycounts).reshape(rt.nweeks,-1)
        wu=(rt.aggregate@ucounts).reshape(rt.nweeks,-1)
        point=components(wy.sum(axis=0)/rt.full_denominator,wu.sum(axis=0)/rt.full_denominator,rt.sides)
        unknown_quality=bool(np.all(unknown*1000<=rt.cy_n))
        key_quality=bool(np.all(key_invalid*1000<=rt.cy_n))
        checks[f'unknown_{"above" if above else "at"}_cutoff']=unknown_quality==not_above(above)
        checks[f'keys_{"above" if above else "at"}_cutoff']=key_quality==not_above(above)
        checks[f'unknown_envelopes_{above}']=bool(np.all(point.reshape(-1,3)[:,1]<=point.reshape(-1,3)[:,0]) and np.all(point.reshape(-1,3)[:,0]<=point.reshape(-1,3)[:,2]))
        # A candidate otherwise yielding a substantive verdict must be blocked
        # by the same per-cohort quality guard before any verdict is exposed.
        provisional=verdict(np.repeat(np.tile([.04,-.04],56),3),np.full(336,.001),1)[0]
        actual=provisional if unknown_quality and key_quality else 'Inconclusive'
        checks[f'quality_guard_{above}']=actual==('Inconclusive' if above else provisional)
    for name,values in (('nonbinary',(2,0,0)),('invalid_numeric',(0,0,'bad')),('nonfinite',(0,0,float('inf')))):
        try:status(*values)
        except ValueError:checks[f'{name}_stops']=True
        else:checks[f'{name}_stops']=False
    result=dict(written_utc=utc(),checks=checks,passes=all(checks.values()),confirmation_outcomes_opened=False)
    dump(OUT/'gate-fixtures.json',result)
    return result


def not_above(above):
    return not above
