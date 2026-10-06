#!/usr/bin/env python3
"""Deterministic implementation checks. Never generates simulated outcomes."""
import json
import numpy as np
from common import OUT, dump, progress, sha, utc
from simulation_model import Model
from scenarios import process_at,templates,stresses,mechanisms
from blind_guard import verify_denial

def main():
    assert verify_denial()
    model=Model()
    checks=[]
    def check(name,condition):
        assert condition,name
        checks.append(name)
    check('all operator score rows normalized',np.max(np.abs(
      np.asarray(model.t.sum(axis=1)).ravel()-1))<1e-12)
    check('all cell counts positive',bool(np.all(model.n>0)))
    check('full source denominator retained',int(model.n.sum())==15243703)
    check('complete fixed contrast family',len(model.sides)*3==336)
    check('stresses count 150',len(list(stresses()))==150)
    check('mechanisms count 10',len(list(mechanisms()))==10)
    ts=list(templates(model.pairs))
    check('templates count 62333',len(ts)==62333)
    for i in (0,1,2,3,4,7,85,len(ts)-1):
        check(f'process ID round trip {i}',process_at(model.pairs,i*1500)['template']==ts[i])
    p=np.full(len(model.n),.8)
    for kind in ('none','informative','mcar','status'):
        m=dict(kind=kind,r=0. if kind=='none' else .0005)
        truth=model.truths(p,m)
        components=np.array(truth['components']).reshape(-1,3)
        check(f'constant primary and latent zero under {kind}',
          np.max(np.abs(components[:,0]))<1e-9 and
          np.max(np.abs(truth['latent_G_D']))<1e-9)
        expected_u=0 if kind=='none' else (.0005 if kind=='informative' else .0005*(.7+.3*.8))
        check(f'endpoint widths under {kind}',np.max(np.abs(
          components[:,2]-components[:,1]-2*expected_u))<1e-9)
    probes=[]
    # These are code checks, not a sample-based substitute for the full audit.
    for process_id in (3000,4500,10500,127500,22500,11751):
        process=process_at(model.pairs,process_id)
        probability,calibration=model.calibrate(process)
        check(f'probability bounds {process_id}',np.min(probability)>=.05 and np.max(probability)<=.99)
        check(f'constraint residual {process_id}',calibration['residual']<=1e-6)
        probes.append(dict(process=process,calibration=calibration,
                           expected_truth=model.truths(probability,process['missingness'])))
        if process_id==22500:
            check('boundary full-vector R cap',probes[-1]['expected_truth']['primary']['R']<=.02+1e-6)
    # All rows preserve the promised source ordering and map to one probability cell.
    from simulation_model import read_sealed
    record=next(r for r in model.record['files'] if r['path'].endswith('simulation-flights.parquet'))
    f=read_sealed(record)
    ids=f['probability_id'].to_numpy()
    check('every source record maps to a probability cell',len(ids)==15243703 and
      ids.min()>=0 and ids.max()<len(model.n))
    check('flight map recovers every probability-cell denominator',
          np.array_equal(np.bincount(ids,minlength=len(model.n)),model.n))
    dump(OUT/'scenario-verification.json',dict(written_utc=utc(),checks=checks,
      deterministic_probability_probes=probes,synthetic_outcomes_generated=0,
      full_calibration_gate_passed=False,full_calibration_audit_run=False,
      code_hashes={name:sha(OUT/name) for name in
                  ('verify_scenarios.py','scenarios.py','simulation_model.py','generator.py')}))
    progress(f'Scenario implementation verification passes {len(checks)} deterministic checks, including two opposite .04 designated-edge calibrations, all-zero calibration, a decision-line full-vector cap and the high-baseline seasonal informative-missingness case; maximum probe residual {max(p["calibration"]["residual"] for p in probes):.3g}. These are code probes, not the required all-case calibration gate. No synthetic outcomes or bootstrap draws generated.')
    print(dict(checks_passed=len(checks),calibration_probes=len(probes),outcomes_generated=0))

if __name__=='__main__':main()
