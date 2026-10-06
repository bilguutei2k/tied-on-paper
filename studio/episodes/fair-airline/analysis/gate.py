#!/usr/bin/env python3
"""Audit mandatory pre-simulation seals and report blocked gates honestly.

This is the staged precondition checker, not an implemented Monte Carlo runner.
It cannot generate synthetic outcomes. METHOD requires the support manifest,
scenario manifest and executable generator to be committed first. Claude must
commit the complete scenario/generator seal before any simulated outcomes.
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
    support_committed=committed(OUT/'coverage.json',root)
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
    report['support_commit_satisfied']=support_committed
    if (OUT/'scenario-manifest.json').exists():
        scenario=json.loads((OUT/'scenario-manifest.json').read_text())
        report['scenario_seal']={'manifest_sha256':sha(OUT/'scenario-manifest.json'),
          'status':scenario['status'],'templates':scenario['enumeration']['templates'],
          'processes':scenario['enumeration']['processes'],
          'expected_truth_representation':scenario['expected_truth']['representation'],
          'numeric_calibration_audit_complete':False}
        verification=json.loads((OUT/'scenario-verification.json').read_text())
        report['deterministic_scenario_checks']={'checks_passed':len(verification['checks']),
          'probability_probes':len(verification['deterministic_probability_probes']),
          'max_probe_residual':max(p['calibration']['residual'] for p in verification['deterministic_probability_probes']),
          'sha256':sha(OUT/'scenario-verification.json'),
          'is_full_calibration_gate':False}
    dump(OUT/'gate.json',report)
    lines=['# Pre-confirmation gate status','', '**BLOCKED — no simulation gate has run.**','',
      'No confirmation outcome columns were materialized, decoded into analysis tables, summarized or plotted. No synthetic datasets or bootstrap draws were generated.', '',
      'Support commit `af8e89f` satisfies the first barrier. METHOD also requires: “Before the first simulated outcome is generated, commit a machine-readable scenario manifest and executable generator”. The owner prohibits this agent from writing `.git`; Claude commits. The second barrier is unsatisfied.', '',
      'The executable generator, fixed Cartesian scenario enumeration, exact probability/truth recipes and schedule-only probability-cell operator are prepared. Deterministic implementation probes are separate from the full numerical calibration audit, which has not run. `gate.py` remains a prerequisite checker/report writer; the complete Monte Carlo runner is still required after the generator commit.', '',
      '| Gate | Result | Registered acceptance rule |','|---|---|---|']
    for name,rule in RULES.items():
        rule_text='; '.join(rule.values()).replace('|','\\|')
        lines.append(f"| {name} | BLOCKED / NOT RUN | {rule_text} |")
    lines += ['', 'Selection: exactly 1,000 datasets/scenario, 5,000 draws/dataset; independent validation: exactly 2,000 datasets/scenario, 5,000 draws/dataset. No attempts, resampler selection, bias estimates, coverage counts, false-verdict counts or power estimates exist.', '',
      'The schedule eligibility and deterministic fixtures are separate structural checks; passing those cannot clear validity or power.', '', '## Frozen sets','',
      '| Set | Size | SHA-256 |','|---|---:|---|']
    for name,s in coverage['frozen_sets'].items():lines.append(f"| {name} | {s['size']} | `{s['sha256']}` |")
    if 'scenario_seal' in report:
        ss=report['scenario_seal'];v=report['deterministic_scenario_checks']
        lines += ['', '## Scenario specification and deterministic checks', '',
          f"{ss['templates']:,} templates × 150 stress settings × 10 missingness settings = {ss['processes']:,} fixed process IDs, including all 210 two-disjoint-edge sets and both directions of every supported pair.", '',
          f"{v['checks_passed']} implementation checks pass. {v['probability_probes']} deterministic probability calibrations have maximum residual {v['max_probe_residual']:.3g}, against the 1e-6 constraint tolerance. These probes do not certify the required all-case calibration gate.", '',
          'The manifest freezes calibrated probabilities and all expected G/D/R/H as exact executable mathematical recipes on the sealed numeric structure. Twelve base expectation vectors are also recorded numerically. Full numeric feasibility certification remains unrun; see DEVIATIONS.md for this literal interpretation and SCENARIOS.md for the handoff.', '',
          f"Scenario manifest SHA-256: `{ss['manifest_sha256']}`."]
    lines += ['', '## Required handoff','',
      'Claude must now commit the scenario/generator seal and its reviewable artifacts. Do not generate synthetic outcomes before that commit. Afterward, complete all-case numerical calibration/feasibility certification and the full registered selection/validation banks. No reduced scenario count, roster or acceptance criterion is authorized. Confirmation outcomes remain closed regardless of any later gate result until the gate report is committed.', '',
      'Source-specific raw redistribution terms remain unresolved. Publish retrieval code, URLs/hashes and aggregates; raw ZIPs, documentation snapshots and row-level derivatives remain ignored. See DEVIATIONS.md and data/docs-manifest.json.']
    (OUT/'GATE.md').write_text('\n'.join(lines)+'\n')
    progress('gate.py precondition audit: support commit af8e89f satisfied; scenario/generator bytes not yet committed. Validity, full calibration, boundary false-verdict, power and independent validation BLOCKED / NOT RUN. Zero synthetic datasets/draws. Deterministic implementation probes are not full gate passes. Confirmation outcomes remain closed.')
    print({'overall':report['overall'],'gate_results':{name:'NOT_RUN' for name in RULES},'outcomes_opened':False})

if __name__=='__main__':main()
