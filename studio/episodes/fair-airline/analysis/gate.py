#!/usr/bin/env python3
"""Audit mandatory pre-simulation seals and report blocked gates honestly.

This is the staged precondition checker, not an implemented Monte Carlo runner.
It cannot generate synthetic outcomes. METHOD requires the support manifest,
scenario manifest and executable generator to be committed first. Claude must
commit support before implementation/commit of the complete scenario seal.
"""
import argparse
import json
import os
import subprocess
from pathlib import Path
from common import EP, OUT, dump, progress, sha, utc
from blind_guard import install, verify_denial

install()

RULES = {
    'validity': {'bias': 'Each |mean G,D error| + 1.96*MCSE <=0.002',
        'coverage': 'One-sided 95% exact binomial lower bound on whole-family coverage >=0.92',
        'intervals': 'At least 4750/5000 joint draws per valid dataset; >=95% datasets valid; every component SD >0',
        'quality_blocking': 'No substantive verdict from 1% missingness, invalid-data or above-cutoff fixtures'},
    'calibration': {'constraints': 'Every required single-edge probability calibration feasible; full-vector residual <=1e-6',
        'family': 'Complete frozen unordered-pair x period x contrast x scoring-assignment family',
        'probabilities': 'Least squared distance to fixed base, one carrier/cell probability, bounds [0.05,0.99]'},
    'boundary_false_verdict': {'errors': 'Each applicable one-sided 95% exact binomial upper bound <=0.025',
        'targets': 'False changes if true R<=0.02; false survives if true H>=0.02; latent truth also judged under missingness'},
    'power': {'reversal': 'Each supported pair/direction at delta=.04: designated-pair joint power lower exact 95% bound >=0.80',
        'survival': 'Whole-table survival lower exact 95% bound >=0.80 for all-zero and calibrated stable-order cases',
        'grid': 'All registered baseline/shock/seasonality levels, with no missingness and .05% informative missingness'},
    'independent_validation': {'bank': 'Only first fully passing resampler, fresh bank1, same acceptance rules; failure stops'},
}

def committed(path, root):
    relative = str(path.relative_to(root))
    r = subprocess.run(['git','show',f'HEAD:{relative}'], cwd=root,
                       capture_output=True, env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
    return r.returncode == 0 and r.stdout == path.read_bytes()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workers',type=int,default=10);args=ap.parse_args()
    root=EP.parents[2]
    coverage=json.loads((OUT/'coverage.json').read_text())
    assert verify_denial()
    missing=[]
    for name in ['coverage.json','scenario-manifest.json','generator.py']:
        p=OUT/name
        if not p.exists():missing.append(f'{name}: not implemented/sealed')
        elif not committed(p,root):missing.append(f'{name}: bytes not present in HEAD commit')
    # This staged tool cannot become a simulation runner through an unchecked flag.
    if not missing:
        missing.append('Complete Monte Carlo runner implementation required before execution; this tool only checks prerequisites.')
    report={'written_utc':utc(),'overall':'BLOCKED_NOT_RUN','confirmation_outcomes_opened':False,
      'synthetic_datasets_generated':0,'bootstrap_draws_generated':0,'workers_requested':args.workers,
      'raw_access_denial': 'Python audit hook verified; persistent chmod and nested kernel sandbox unavailable',
      'blockers':missing,'method_sha256':sha(EP/'METHOD.md'),'coverage_sha256':sha(OUT/'coverage.json'),
      'frozen_sets':coverage['frozen_sets'],
      'gates':{name:{'status':'BLOCKED_NOT_RUN','acceptance':rule,'results':None} for name,rule in RULES.items()},
      'structural_checks':{'support':coverage['support_gate'],
                          'missing_key_quality_passes':all(r['passes'] for r in coverage['per_carrier_year']),
                          'fixtures':json.loads((OUT/'field-map.json').read_text())['fixtures']},
      'selection_bank':{'datasets_per_scenario':1000,'draws_per_dataset':5000,'attempts':[]},
      'validation_bank':{'datasets_per_scenario':2000,'draws_per_dataset':5000,'attempts':[]},
      'resampler_order':['independent whole weeks','circular 4 weeks','circular 8 weeks'],
      'selected_resampler':None,'production_weights':None,
      'code_hashes':{p.name:sha(p) for p in sorted(OUT.glob('*.py'))}}
    dump(OUT/'gate.json',report)
    lines=['# Pre-confirmation gate status','', '**BLOCKED — no simulation gate has run.**','',
      'No confirmation outcome columns were materialized, decoded into analysis tables, summarized or plotted. No synthetic datasets or bootstrap draws were generated.', '',
      'METHOD requires: “Commit the support manifest BEFORE synthetic outcomes or power results are inspected.” It also requires a committed scenario manifest and executable generator before the first simulated outcome. The owner prohibits this agent from writing `.git`; Claude commits. No commit barrier is waived.', '',
      'The complete Monte Carlo runner and executable scenario manifest are not implemented in this staged handoff. `gate.py` is an honest prerequisite checker and blocked-report writer; it is not evidence of executed simulations.', '',
      '| Gate | Result | Registered acceptance rule |','|---|---|---|']
    for name,rule in RULES.items():lines.append(f"| {name} | BLOCKED / NOT RUN | {'; '.join(rule.values())} |")
    lines += ['', 'Selection: exactly 1,000 datasets/scenario, 5,000 draws/dataset; independent validation: exactly 2,000 datasets/scenario, 5,000 draws/dataset. No attempts, resampler selection, bias estimates, coverage counts, false-verdict counts or power estimates exist.', '',
      'The schedule eligibility and deterministic fixtures are separate structural checks; passing those cannot clear validity or power.', '', '## Frozen sets','',
      '| Set | Size | SHA-256 |','|---|---:|---|']
    for name,s in coverage['frozen_sets'].items():lines.append(f"| {name} | {s['size']} | `{s['sha256']}` |")
    lines += ['', '## Required handoff','',
      'Claude must commit the support artifacts. Then implement and commit the full deterministic calibration/scenario manifest and executable generator, without generating simulated outcomes before that commit. Only then run the complete registered selection and validation banks. Confirmation outcomes remain closed regardless of any later gate result until the gate report is committed.', '',
      'Source-specific raw redistribution terms remain unresolved. Publish retrieval code, URLs/hashes and aggregates; raw ZIPs, documentation snapshots and row-level derivatives remain ignored. See DEVIATIONS.md and data/docs-manifest.json.']
    (OUT/'GATE.md').write_text('\n'.join(lines)+'\n')
    progress('gate.py precondition audit: validity, calibration, boundary false-verdict, power and independent validation BLOCKED / NOT RUN. Zero synthetic datasets/draws. Support and scenario/generator commits absent; raw outcomes remain closed. Reports explicitly distinguish structural fixtures from unexecuted statistical gates.')
    print({'overall':report['overall'],'gate_results':{name:'NOT_RUN' for name in RULES},'outcomes_opened':False})

if __name__=='__main__':main()
