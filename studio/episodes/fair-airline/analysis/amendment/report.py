#!/usr/bin/env python3
"""Render completed synthetic evidence, without changing any acceptance rule."""
import json
from pathlib import Path
from datetime import datetime,timezone
H=Path(__file__).resolve().parent
r=json.loads((H/'results.json').read_text());assert r['status']!='RUNNING'
verification=json.loads((H/'verification.json').read_text());assert verification['passes']
selected=r['selected']
selection_label = str(selected) if selected is not None else 'none'
lines=['# Amendment 1 — pre-confirmation gate results','',
 f"**{r['status']}**. Selected block length: {selection_label}. Confirmation outcomes remain unopened.",
 '', 'The pre-simulation design/code checkpoint was `e5c9a33`. The registered',
 'algorithm, candidates, scenarios, sample sizes and criteria were unchanged during',
 'evaluation. Nominal intervals are 99% bootstrap-SD intervals; gate acceptance',
 'uses one-sided 95% exact Monte Carlo bounds. Bias values below are percentage points.',
 '', '| Bank | Candidate | Scenario/profile | D_A / D_B (pp) | Bias bound max (pp) | Joint coverage % [lower] | Max false-direction upper % | Min required power lower % | Pass |',
 '|---|---:|---|---|---:|---|---:|---:|---|']
summary=[]
for x in r['scenarios']:
    false=[p[k]['upper'] for p in x['periods'] for k in ('false_above','false_below') if k in p]
    powers=[p['power']['lower'] for p in x['periods'] if 'power' in p]
    if 'replicated_power' in x:powers.append(x['replicated_power']['lower'])
    c=x['joint_coverage'];s=x['scenario']
    lines.append(f"| {x['bank']} | {x['candidate']} | {s['id']}: {s['profile']['name']} | {100*s['effects'][0]:g} / {100*s['effects'][1]:g} | {100*max(map(max,x['bias_bound'])):.4f} | {100*c['rate']:.2f} [{100*c['lower']:.2f}] | {100*max(false):.2f} | {100*min(powers):.2f} | {x['passes']} |" if powers else
                 f"| {x['bank']} | {x['candidate']} | {s['id']}: {s['profile']['name']} | {100*s['effects'][0]:g} / {100*s['effects'][1]:g} | {100*max(map(max,x['bias_bound'])):.4f} | {100*c['rate']:.2f} [{100*c['lower']:.2f}] | {100*max(false):.2f} | — | {x['passes']} |")
for bank in (0,1):
    xs=[x for x in r['scenarios'] if x['bank']==bank and x['candidate']==selected and x['scenario']['required']]
    if not xs:continue
    fs=[p[k] for x in xs for p in x['periods'] for k in ('false_above','false_below') if k in p]
    ps=[p['power'] for x in xs for p in x['periods'] if 'power' in p]+[x['replicated_power'] for x in xs if 'replicated_power'in x]
    summary.append(dict(bank=bank,mandatory_scenarios=len(xs),maximum_bias_bound=max(max(map(max,x['bias_bound'])) for x in xs),
      minimum_joint_coverage=min(x['joint_coverage']['rate'] for x in xs),
      minimum_joint_coverage_lower=min(x['joint_coverage']['lower'] for x in xs),
      maximum_false_rate=max(p['rate'] for p in fs),maximum_false_upper=max(p['upper'] for p in fs),
      minimum_power=min(p['rate'] for p in ps),minimum_power_lower=min(p['lower'] for p in ps)))
lines+=['','## Selection and limits','']
for candidate in (1,7,28):
    xs=[x for x in r['scenarios'] if x['bank']==0 and x['candidate']==candidate]
    if not xs:lines.append(f'- {candidate}-day candidate: NOT RUN (prior selection or required stop).');continue
    failed=[x for x in xs if x['scenario']['required'] and not x['passes']]
    lines.append(f'- {candidate}-day candidate: '+(f"stopped at scenario {failed[0]['scenario']['id']}; subsequent scenarios UNRUN. " if failed else 'completed all mandatory scenarios. ')+f'{len(xs)*1000:,} selection datasets.')
if not any(x['bank']==1 for x in r['scenarios']):
    lines.append('- Independent validation: NOT RUN; no candidate cleared selection. No validation pass or failure is inferred.')
    lines.append('- Serial-shock power, informative-missingness scenarios, mixed-period effects and local three-point power remain UNRUN after the mandatory boundary stop; the full power gate is NOT COMPLETED.')
for x in r['scenarios']:
    if 'local_power'in x:
        p=x['local_power'];lines.append(f"- Three-point local alternative, bank {x['bank']}, {x['candidate']}-day blocks: repeated-decision power {100*p['rate']:.1f}%, exact lower {100*p['lower']:.1f}%. Descriptive; no 80% claim at the pilot point.")
lines+=['','The retained materiality line is two points. Four points is an optimistic but',
 'pilot-compatible design effect (pilot point 2.953 points, SE 0.520 points); it',
 'does not guarantee useful power for a smaller effect. Survival only excludes',
 'a material UA advantage under this rule, and does not establish WN superiority.',
 'All validation applies to the specified fixed-schedule shock/missingness processes,',
 'not to arbitrary dependence or a different route network. The inherited original',
 '28-pair gate remains failed. No observed confirmation verdict has been produced.',
 '', '## Verification and timing','',
 f"Independent verifier passed {verification['exact_binomial_checks']} exact-binomial interval checks by tail inversion, compensated-sum bias calculations, all {len(verification['original_replicate_replays'])} original-replicate replays, frozen membership counts, status/cutoff fixtures and all three bootstrap multiplicity algorithms.",
 '', 'Benchmark: ten datasets per candidate, ten workers, 0.21–0.25 seconds per batch.',
 'Every worker uses one numerical-library thread. Runtime details are in timing.json',
 'and per-scenario results.json. Replayed records are not additional evaluation datasets.',
 'The usage-limit continuation preserved the first 700 records of selection',
 'candidate 28/scenario 2 byte-for-byte and completed only its remaining 300.',
 'Its saved runtime covers the resumed portion only; all other scenario times are complete.',
 '', 'A failed gate cannot authorize confirmation. A further reviewed outcome-blind',
 'amendment, new seal and passing gate are required; owner adoption and the later',
 'production-code/resampling-array seal must precede confirmation outcome access.',
 'This investigation ends at the report checkpoint.']
(H/'GATE.md').write_text('\n'.join(lines)+'\n')
(H/'summary.json').write_text(json.dumps(dict(status=r['status'],selected=selected,banks=summary,
 candidate_stops=[dict(candidate=c,completed_scenarios=len(xs),
   failure_scenario=next((x['scenario']['id'] for x in xs if x['scenario']['required'] and not x['passes']),None))
   for c in (1,7,28) for xs in [[x for x in r['scenarios'] if x['bank']==0 and x['candidate']==c]]],
 dataset_candidate_evaluations=sum(x['joint_coverage']['n'] for x in r['scenarios']),
 unique_synthetic_datasets=sum({(x['bank'],x['scenario']['id']):x['joint_coverage']['n'] for x in r['scenarios']}.values()),
 bootstrap_draws=sum(x['joint_coverage']['n'] for x in r['scenarios'])*1999,
 verification_passes=True,confirmation_outcomes_opened=False),indent=2)+'\n')
print(json.dumps(json.loads((H/'summary.json').read_text())))
