"""Complete fixed-schedule two-bank gate with per-dataset checkpoints."""
import os
for _name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS',
              'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[_name]='1'
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import numpy as np
from common import EP,OUT,DERIVED,dump,progress,sha,seal_file,utc
from blind_guard import verify_denial
from generator import committed_bytes,require_commit
from simulation_model import Model
from scenarios import process_at,processes
from gate_runtime import Runtime,components,verdict,multiplicities
from gate_statistics import summarize,power_required

FIRST=3240
FILES=('gate.py','gate_runner.py','gate_runtime.py','gate_statistics.py','gate_fixtures.py',
       'execution-plan.json','runner-verification.json','calibration-first.json')
RULES={
 'calibration':'Every mandatory calibration feasible; residual <=1e-6; global count-weighted least-squares solution and complete truth',
 'validity':'Every |mean error|+1.96 MCSE <=.002; exact coverage lower bound >=.92; >=95% valid datasets, each >=4750/5000 joint draws and every SD>0; blocking fixtures emit no verdict',
 'boundary_false_verdict':'Every applicable exact one-sided 95% upper false-verdict bound <=.025, including latent truths',
 'power':'Every mandatory designated reversal and all-zero/stable survival exact one-sided 95% lower power bound >=.80',
 'independent_validation':'First fully passing resampler only, 2000 fresh bank1 datasets/process and 5000 draws; same rules; failure stops'}

def prepare(workers):
    require_commit();model=Model();rt=Runtime(model)
    process=process_at(model.pairs,FIRST)
    p,calibration=model.calibrate(process)
    truth=model.truths(p,process['missingness'])
    checks=[]
    def check(name,value):
        assert value,name
        checks.append(name)
    check('registered full source denominator',len(rt.pid)==15243703)
    check('probability cell counts independently reconstructed',
          np.array_equal(np.bincount(rt.pid,minlength=len(model.n)),model.n))
    check('all score denominators positive and normalized',
          bool(np.all(rt.full_denominator>0)) and np.max(np.abs(rt.full_denominator-1))<1e-10)
    weekly=(rt.aggregate@(model.n*p)).reshape(rt.nweeks,-1)
    point=components(weekly.sum(axis=0)/rt.full_denominator,np.zeros(model.t.shape[0]),model.sides)
    error=float(np.max(np.abs(point-truth['components'])))
    check('independent week-score derivation equals full analytical truth',error<1e-10)
    check('complete 336-component family retained',len(point)==336)
    check('first process is required all-zero survival stress',
          process['template']['kind']=='stable' and process['template']['increment']==0 and power_required(process))
    check('all-zero calibration feasible at registered tolerance',calibration['residual']<=1e-6)
    check('full primary and latent zero truth',max(np.abs(truth['components']))<1e-6 and max(np.abs(truth['latent_G_D']))<1e-6)
    check('changes direction repeats',verdict(np.repeat(np.tile([.04,-.04],56),3),np.full(336,.001),1)[0]=='Table changes')
    check('equality gives inconclusive',verdict(np.repeat(np.tile([.02,-.02],56),3),np.zeros(336),1)[0]=='Inconclusive')
    check('sufficiently narrow zero envelope survives',verdict(np.zeros(336),np.full(336,.001),1)[0]=='Table survives')
    check('integer quality cutoff and next record',bool(np.all((rt.cy_n//1000)*1000<=rt.cy_n) and np.all((rt.cy_n//1000+1)*1000>rt.cy_n)))
    check('raw access denied',verify_denial())
    # Primitive RNG equivalence fixtures have no flight/outcome assignment.
    from bootstrap import weights
    for candidate in (1,4,8):
        a=np.random.Generator(np.random.PCG64(71))
        b=np.random.Generator(np.random.PCG64(71))
        reference=weights(a,rt.weeks_by_year,candidate)
        streamed=multiplicities(b,rt.weeks_by_year,candidate)
        check(f'5000 exact registered multiplicity arrays {candidate}',
              all(np.array_equal(reference[y],streamed[y]) for y in reference))
    for method in ('normal','uniform'):
        a=np.random.Generator(np.random.PCG64(72));b=np.random.Generator(np.random.PCG64(72))
        if method=='normal':
            whole=a.standard_normal(10003);chunk=np.concatenate([b.standard_normal(n) for n in (5000,5000,3)])
        else:
            whole=a.random((10003,3));chunk=np.concatenate([b.random((n,3)) for n in (5000,5000,3)])
        check(f'chunked PCG64 {method} primitives byte-identical',np.array_equal(whole,chunk))
    np.save(DERIVED/'calibration-first.npy',p,allow_pickle=False)
    dump(OUT/'calibration-first.json',dict(process=process,calibration=calibration,truth=truth,
         probability_file=seal_file(DERIVED/'calibration-first.npy'),synthetic_datasets_generated=0,confirmation_outcomes_opened=False))
    dump(OUT/'runner-verification.json',dict(written_utc=utc(),checks=checks,
         maximum_independent_score_residual=error,synthetic_datasets_generated=0,confirmation_outcomes_opened=False))
    dump(OUT/'execution-plan.json',dict(written_utc=utc(),scenario_commit='5aa59e2',first_process_id=FIRST,
         dispatch='Required all-zero, baseline .70, no season, combined SD .30/AR .6, no missingness first; then remaining IDs ascending. Original process IDs/streams unchanged. Failure stops; no reduced-suite pass.',
         workers=workers,parallelism='Ten dataset threads, numeric libraries one thread each, shared immutable schedule; chunked PCG64 innovations/status uniforms in exact original source order.',
         selection=dict(bank=0,datasets=1000,draws=5000,candidates=[1,4,8],same_data=True),
         validation=dict(bank=1,datasets=2000,draws=5000,selected_only=True),
         scope='All registered processes and 336 components. Complete calibration truth recorded before each process RNG. Bias failure stops all candidates. No performance-based process deletion.',
         first_calibration_sha256=sha(OUT/'calibration-first.json'),tests_sha256=sha(OUT/'runner-verification.json'),
         code_hashes={n:sha(OUT/n) for n in FILES if n.endswith('.py')}))
    progress('Runner prepared without synthetic outcomes: complete streaming generator, real weekly denominators, 336-component scorer, exact 5000-draw intervals and two-bank Monte Carlo criteria. Process 3240 calibrated/sealed. Dispatch prioritizes this mandatory high-dependence stable bias/power check, then all remaining original IDs. Helper commit required before execution.')
    print(dict(stage='prepared',checks=len(checks),first_process=FIRST,calibration_residual=calibration['residual'],outcomes_opened=False))

def check_commit():
    require_commit()
    for name in FILES:
        if not committed_bytes(OUT/name):raise PermissionError('Runner checkpoint must be committed: '+name)
    plan=json.loads((OUT/'execution-plan.json').read_text())
    assert all(sha(OUT/n)==h for n,h in plan['code_hashes'].items())
    assert sha(OUT/'calibration-first.json')==plan['first_calibration_sha256']
    assert sha(OUT/'runner-verification.json')==plan['tests_sha256']
    return plan

def dataset(rt,process,prepared,truth,bank,replicate,candidates):
    wy,wu,point,quality,unknown=rt.generate(process,bank,replicate,prepared)
    expected=np.array(truth['components']);latent=np.array(truth['latent_G_D']).reshape(-1,2,2)
    rows={}
    for c in candidates:
        fit=rt.intervals(wy,wu,point,process,bank,replicate,c)
        row=dict(valid=fit['valid'],valid_draws=fit['valid_draws'],verdict='Inconclusive',coverage=False,latent_coverage=False,designated_power=False)
        if fit['valid']:
            row['coverage']=bool(np.all(expected>=point-fit['critical']*fit['sd']) and np.all(expected<=point+fit['critical']*fit['sd']))
            row['latent_coverage']=bool(np.all(latent>=fit['lower']) and np.all(latent<=fit['upper']))
            row['critical']=fit['critical']
            if quality:
                row['verdict']=fit['verdict']
                if process['template'].get('design_power',False):
                    edge=process['template']['active'][0];k=rt.model.pairs.index(tuple(edge['pair']))
                    row['designated_power']=bool(np.all(fit['lq'][k,0 if edge['direction']==1 else 1]>.02))
        rows[str(c)]=row
    return dict(replicate_id=replicate,point=point.tolist(),quality_passes=quality,unknown_by_carrier_year=unknown.tolist(),intervals=rows)

def run_process(rt,process,p,truth,bank,candidates,workers):
    n=1000 if bank==0 else 2000;prepared=rt.prepare(process,p)
    directory=DERIVED/'gate-checkpoints';directory.mkdir(exist_ok=True)
    path=directory/f"bank{bank}-process{process['process_id']}.jsonl";meta=path.with_suffix('.meta.json')
    record=dict(bank=bank,process=process,candidates=candidates,datasets=n,draws=5000,execution_plan_sha256=sha(OUT/'execution-plan.json'))
    if meta.exists():assert json.loads(meta.read_text())==record
    else:dump(meta,record)
    rows=[]
    if path.exists():
        with path.open() as f:rows=[json.loads(line) for line in f if line.strip()]
        assert [r['replicate_id'] for r in rows]==list(range(len(rows))) and len(rows)<=n
    with ThreadPoolExecutor(max_workers=workers) as pool,path.open('a') as f:
        for start in range(len(rows),n,workers):
            futures=[pool.submit(dataset,rt,process,prepared,truth,bank,i,candidates) for i in range(start,min(start+workers,n))]
            for future in futures:
                row=future.result();rows.append(row);f.write(json.dumps(row,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n')
            f.flush()
            if len(rows)%50==0 or len(rows)==n:
                progress(f"Bank {bank}, process {process['process_id']}: {len(rows)}/{n} datasets complete; exactly 5000 draws per candidate/dataset; no interim acceptance decision.")
                print(json.dumps(dict(bank=bank,process=process['process_id'],completed=len(rows),total=n)),flush=True)
    result=summarize(process,rows,truth);result['bank']=bank;result['checkpoint']=seal_file(path)
    dump(directory/f"bank{bank}-process{process['process_id']}-summary.json",result)
    return result

def report(attempts,calibrations,overall,reason,selected=None,full=False,fixtures=None):
    coverage=json.loads((OUT/'coverage.json').read_text())
    statuses={name:('PASS' if full else 'NOT_COMPLETED') for name in RULES}
    if any(not a['bias']['passes'] and not a['quality_blocking_only'] for a in attempts):statuses['validity']='FAIL'
    if any(power_required(a['process']) and all(not r['tests']['power'] for r in a['resamplers'].values()) for a in attempts):statuses['power']='FAIL'
    if 'calibration' in reason.lower() and overall=='FAIL':statuses['calibration']='FAIL'
    if not full:statuses['independent_validation']='NOT_RUN'
    result=dict(written_utc=utc(),overall=overall,stop_reason=reason,confirmation_outcomes_opened=False,
      gates={name:dict(status=statuses[name],acceptance=rule) for name,rule in RULES.items()},
      method_sha256=sha(EP/'METHOD.md'),coverage_sha256=sha(OUT/'coverage.json'),frozen_sets=coverage['frozen_sets'],
      scenario_manifest_sha256=sha(OUT/'scenario-manifest.json'),execution_plan_sha256=sha(OUT/'execution-plan.json'),
      selected_resampler=selected,attempts=attempts,calibration_records=calibrations,
      calibration_audit_complete=full,scenario_suite_complete=full,fixtures=fixtures,
      synthetic_datasets_generated=sum(a['datasets'] for a in attempts),
      bootstrap_draws_generated=sum(a['datasets']*5000*len(a['resamplers']) for a in attempts),
      code_hashes={p.name:sha(p) for p in sorted(OUT.glob('*.py'))})
    dump(OUT/'gate.json',result)
    lines=['# Pre-confirmation gate report','',f'**{overall} — {reason}**','',
      'Confirmation outcomes remain closed. Synthetic results use the unchanged real schedule.','',
      '| Gate | Result | Registered acceptance |','|---|---|---|']
    for name,r in result['gates'].items():lines.append(f"| {name} | {r['status']} | {r['acceptance'].replace('|',chr(92)+'|')} |")
    lines+=['','## Completed attempts','']
    for a in attempts:
        b=a['bias'];lines += [f"Bank {a['bank']}, process {a['process']['process_id']}: {a['datasets']} datasets, 5000 draws/candidate/dataset. Maximum bias acceptance bound {b['maximum_bound']:.9g} versus .002; {len(b['failing_components'])}/336 components fail. All mean errors, MCSEs, exact intervals and bounds are recorded in gate.json.",'']
        for c,r in a['resamplers'].items():lines.append(f"- Resampler {c}: coverage {r['coverage']['count']}/{a['datasets']} (lower {r['coverage']['lower_95_one_sided']:.6f}); valid datasets {r['valid_datasets']}; survival {r['table_survives']['count']}/{a['datasets']} (lower {r['table_survives']['lower_95_one_sided']:.6f}); tests {r['tests']}.")
    lines+=['','## Frozen sets','','| Set | Size | SHA-256 |','|---|---:|---|']
    for name,r in coverage['frozen_sets'].items():lines.append(f"| {name} | {r['size']} | `{r['sha256']}` |")
    lines+=['','Unattempted processes/banks are unrun after failure, never inferred to pass. No pair, threshold, scenario, family or bank count was reduced. Dispatch and streaming decisions were sealed before synthetic outcomes; see DEVIATIONS.md.','',
      'Commit this gate report through the owner helper. A failed gate bars confirmation analysis; a reviewed amendment and new gate are required.']
    (OUT/'GATE.md').write_text('\n'.join(lines)+'\n')
    progress(f"Gate report {overall}: {reason}. {result['synthetic_datasets_generated']} synthetic datasets; {result['bootstrap_draws_generated']} bootstrap draws. Confirmation outcomes closed; report commit required.")
    print(dict(overall=overall,reason=reason,gates=statuses,outcomes_opened=False),flush=True)

def run(workers):
    plan=check_commit();assert workers==plan['workers']
    model=Model();rt=Runtime(model);first=json.loads((OUT/'calibration-first.json').read_text())
    pf=first['probability_file'];path=EP/pf['path'];assert sha(path)==pf['sha256'] and path.stat().st_size==pf['bytes']
    with path.open('rb') as f:first_p=np.load(f,allow_pickle=False)
    attempts=[];calibrations=[];candidates=[1,4,8]
    def ordered():
        yield process_at(model.pairs,FIRST)
        for process in processes(model.pairs):
            if process['process_id']!=FIRST:yield process
    for bank in (0,1):
        for process in ordered():
            try:
                if process['process_id']==FIRST:p=first_p;calibration=first['calibration'];truth=first['truth']
                else:p,calibration=model.calibrate(process);truth=model.truths(p,process['missingness'])
                if calibration['residual']>1e-6:raise ValueError('Required calibration residual exceeds 1e-6')
            except (ValueError,RuntimeError) as e:
                if process['template']['kind']=='two_edge_boundary' and 'infeasible' in str(e):
                    calibrations.append(dict(process_id=process['process_id'],feasible=False,mandatory_single_edge=False,reason=str(e)));continue
                report(attempts,calibrations,'FAIL',f"Required calibration failure at process {process['process_id']}: {e}");return
            directory=DERIVED/'gate-checkpoints';directory.mkdir(exist_ok=True)
            path=directory/f"calibration-{process['process_id']}.json"
            dump(path,dict(process=process,calibration=calibration,truth=truth))
            calibrations.append(dict(process_id=process['process_id'],feasible=True,residual=calibration['residual'],truth_file=seal_file(path)))
            a=run_process(rt,process,p,truth,bank,candidates,workers);attempts.append(a)
            if not a['bias']['passes'] and not a['quality_blocking_only']:
                report(attempts,calibrations,'FAIL',f"Required bias criterion fails in bank {bank}, process {process['process_id']}; METHOD bars resampler fallback after bias failure");return
            passing=[c for c in candidates if a['resamplers'][str(c)]['passes']]
            if bank==0:
                candidates=passing
                if not candidates:report(attempts,calibrations,'FAIL',f"No candidate passes all required validity and power processes; final failure at process {process['process_id']}");return
            elif not passing:
                report(attempts,calibrations,'FAIL',f"Independent validation failure at process {process['process_id']}; no new candidate permitted",selected=candidates[0]);return
        if bank==0:candidates=[candidates[0]]
    from gate_fixtures import execute
    fixtures=execute(rt)
    if not fixtures['passes']:report(attempts,calibrations,'FAIL','Registered deterministic blocking fixtures fail',selected=candidates[0],fixtures=fixtures);return
    report(attempts,calibrations,'PASS','Every registered gate and deterministic fixture passes',selected=candidates[0],full=True,fixtures=fixtures)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--run',action='store_true');ap.add_argument('--workers',type=int,default=10);args=ap.parse_args()
    assert verify_denial()
    if args.prepare==args.run:ap.error('Choose exactly one of --prepare or --run')
    if args.prepare:prepare(args.workers)
    else:run(args.workers)
