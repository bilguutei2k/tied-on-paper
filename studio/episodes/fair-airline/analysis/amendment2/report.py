"""Summarize completed synthetic evidence; no fitting or new datasets."""
from pathlib import Path
import json,hashlib,datetime
HERE=Path(__file__).resolve().parent
result=json.loads((HERE/'results.json').read_text());assert result['status']!='RUNNING'
verification=json.loads((HERE/'verification.json').read_text());assert verification['passes']
reports=result['scenarios'];status=result['status'];timing=json.loads((HERE/'timing.json').read_text())
summary={'status':status,'design_commit':'8a33153','selected':result['selected'],'confirmation_outcomes_opened':False,
         'diagnostic_bank0_acceptance_evidence':False,'banks':[]}
lines=['# Amendment 2 — outcome-blind gate results','',f'**{status}**. Design/code checkpoint: `8a33153`. Confirmation outcomes remain unopened.','',
'Amendment 2 was designed after seeing Amendment 1’s synthetic failure, after two failed outcome-blind gates and before any confirmation outcome. Bank 0 informed design and supplies no acceptance evidence here. The sole candidate is the sealed 28-day studentized block interval; no fallback or Amendment 3 was attempted.','',
'The comparison, two-point line, frozen support, periods, scoring, missingness envelope, generator, all 20 scenarios and acceptance/early-stop rules are unchanged. Exactly 1,999 draws per dataset. All reported probability bounds are one-sided 95% exact binomial bounds; bias is in percentage points.','',
'| Bank | Scenario/profile | A/B truth (pp) | Max bias bound (pp) | Joint coverage % [lower] | Max false upper % | Min required power lower % | Pass |',
'|---|---|---|---|---|---|---|---|']
for x in reports:
    false=[p[k]['upper'] for p in x['periods'] for k in ('false_above','false_below') if k in p]
    power=[p['power']['lower'] for p in x['periods'] if 'power' in p]
    if 'replicated_power' in x:power.append(x['replicated_power']['lower'])
    s=x['scenario'];jc=x['joint_coverage'];pw=f'{min(power)*100:.3f}' if power else '—'
    lines.append(f"| {x['bank']} | {s['id']}: {s['profile']['name']} | {s['effects'][0]*100:g}/{s['effects'][1]*100:g} | {max(map(max,x['bias_bound']))*100:.4f} | {jc['rate']*100:.2f} [{jc['lower']*100:.3f}] | {max(false)*100:.3f} | {pw} | {x['passes']} |")
lines+=['','## Completion and limits','']
for bank in (2,1):
    rr=[x for x in reports if x['bank']==bank]
    false=[p[k] for x in rr for p in x['periods'] for k in ('false_above','false_below') if k in p]
    power=[p['power'] for x in rr for p in x['periods'] if 'power' in p]+[x['replicated_power'] for x in rr if 'replicated_power' in x]
    local=next((x['local_power'] for x in rr if 'local_power' in x),None)
    b=dict(bank=bank,completed=len(rr),mandatory_completed=sum(x['scenario']['required'] for x in rr),
        mandatory_passed=sum(x['scenario']['required'] and x['passes'] for x in rr),
        unrun=[i for i in range(20) if i not in [x['scenario']['id'] for x in rr]],
        datasets=sum(x['valid']['n'] for x in rr),worst_false=max(false,key=lambda x:x['upper']) if false else None,
        minimum_joint_coverage_lower=min((x['joint_coverage']['lower'] for x in rr),default=None),
        minimum_required_power_lower=min((x['lower'] for x in power),default=None),local_replicated_power=local)
    summary['banks'].append(b)
    lines.append(f"- Bank {bank}: {b['completed']}/20 scenarios completed; {b['mandatory_passed']}/19 required scenarios passed; {b['datasets']:,} datasets. Unrun: {b['unrun']}.")
    if false:lines.append(f"- Bank {bank} worst false-direction exact upper: {b['worst_false']['upper']*100:.3f}%; minimum joint-coverage lower: {b['minimum_joint_coverage_lower']*100:.3f}%.")
    if power:lines.append(f"- Bank {bank} minimum required-power lower: {b['minimum_required_power_lower']*100:.3f}%.")
    if local:lines.append(f"- Bank {bank} descriptive three-point replicated power: {local['count']}/{local['n']} ({local['rate']*100:.2f}%; exact lower {local['lower']*100:.3f}%). This scenario has no required-power pass claim.")
    for x in rr:
        if x['scenario']['id']==9:
            lines.append(f"- Bank {bank} serial boundary scenario 9: A above/below {x['periods'][0]['false_above']['count']}/{x['periods'][0]['false_below']['count']}; B above/below {x['periods'][1]['false_above']['count']}/{x['periods'][1]['false_below']['count']}, out of {x['valid']['n']} each.")
summary['total_datasets']=sum(x['datasets'] for x in summary['banks']);summary['bootstrap_draws']=summary['total_datasets']*1999
summary['benchmark']=timing;summary['verification_passes']=True
lines+=['',f"Total: {summary['total_datasets']:,} distinct evaluation datasets, {summary['bootstrap_draws']:,} joint bootstrap draws. Timing-only and replay datasets are excluded.",
'','## Verification and timing','',
f"Independent verification passes: {verification['exact_binomial_checks']} binomial-tail inversions, {len(verification['original_replicate_replays'])} original-replicate replays, compensated-sum bias checks, event counts, acceptance and early-stop logic, unchanged manifests/functions, direct interval arithmetic and frozen membership/status checks.",
f"Ten-worker bank-90 timing: {timing['measurements'][0]['seconds']:.4f} seconds for ten datasets. Numerical libraries use one thread. Benchmark acceptance was not inspected. Per-scenario runtimes are saved in results.json.",'',
'Wording clarification: the sealed draft calls B “independent-labeled”; B is a separately labeled 2025 replication, with no added assumption of independence between A and B. The unchanged generator keeps shocks continuous across physical year boundaries. Bank 1 is the independent validation bank.',
'The finite-window variance correction and Student-t floor are specified approximations; this gate certifies only the registered fixed-schedule processes. Three-point power is descriptive. A passing gate does not establish an observed airline advantage or authorize confirmation access. Owner approval and later production-code/resampling-array seals are still required.']
if status!='PASS':lines+=['','The required failure stop has been reached. Later scenarios/validation are unrun as listed; no Amendment 3 was designed.']
(HERE/'GATE.md').write_text('\n'.join(lines)+'\n')
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
files=[p for p in HERE.iterdir() if p.is_file() and p.name!='artifact-hashes.json']
(HERE/'artifact-hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['benchmark','banks']}))
for b in summary['banks']:print(json.dumps(b))
