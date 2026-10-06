#!/usr/bin/env python3
"""Seal executable mathematical scenario specifications without random outcomes."""
import hashlib
import json
from collections import Counter
from itertools import combinations
import numpy as np
import scipy
from common import EP, OUT, sha, dump, progress, utc
from simulation_model import Model
from scenarios import templates, stresses, mechanisms

def main():
    model=Model();pairs=model.pairs
    counts=Counter();digest=hashlib.sha256();examples=[]
    for i,t in enumerate(templates(pairs)):
        counts[t['kind']]+=1
        digest.update((json.dumps(dict(template_id=i,**t),sort_keys=True,separators=(',',':'))+'\n').encode())
        if len(examples)<5:examples.append(dict(template_id=i,**t))
    assert len(pairs)==28 and len(model.sides)*3==336
    assert np.max(np.abs(np.asarray(model.t.sum(axis=1)).ravel()-1))<1e-12
    constant=model.truths(np.full(len(model.n),.8),dict(kind='none',r=0.))
    assert np.max(np.abs(constant['components']))<1e-9
    base_truth=[]
    for baseline in (.7,.8,.9):
        for season in (0.,.05):
            for increment in (0.,.005):
                stress=dict(baseline=baseline,season=season)
                p=model.base(stress,increment)
                assert np.min(p)>=.05 and np.max(p)<=.99
                base_truth.append(dict(baseline=baseline,season=season,increment=increment,
                  **model.truths(p,dict(kind='none',r=0.))))
    dump(OUT/'scenario-base-truth.json',dict(outcomes_generated=0,truths=base_truth))
    disjoint=sum(not(set(p)&set(q)) for p,q in combinations(pairs,2))
    code_files=['generator.py','scenarios.py','simulation_model.py','seal_scenarios.py',
                'blind_guard.py','common.py','rules.py','verify_scenarios.py','bootstrap.py']
    manifest={
      'schema_version':1,'freeze_utc':utc(),'status':'EXECUTABLE_SPECIFICATION_PENDING_COMMIT',
      'confirmation_outcomes_opened':False,'synthetic_outcomes_generated':0,
      'method_sha256':sha(EP/'METHOD.md'),'support_commit':'af8e89f',
      'coverage_sha256':sha(OUT/'coverage.json'),
      'simulation_structure_sha256':sha(OUT/'simulation-structure.json'),
      'base_truth_sha256':sha(OUT/'scenario-base-truth.json'),
      'code_hashes':{name:sha(OUT/name) for name in code_files},
      'dependencies':{'numpy':np.__version__,'scipy':scipy.__version__,
                      'environment_sha256':sha(OUT/'environment.json')},
      'enumeration':{'iterator':'scenarios.processes(pairs)',
        'template_counts':dict(counts),'templates':sum(counts.values()),
        'templates_canonical_sha256':digest.hexdigest(),
        'canonical_encoding':'JSON sorted keys, compact separators; template_id prepended; UTF-8, LF per template',
        'stress_settings':list(stresses()),'missingness_settings':list(mechanisms()),
        'processes':sum(counts.values())*1500,
        'process_id':'1500*template_id + 10*stress_id + mechanism_id',
        'two_vertex_disjoint_sets':disjoint,'examples':examples},
      'base_probability':{
        'formula':'clip(baseline + season*sin(2*pi*(day_of_year-1)/365.25) + heterogeneity + increment*(carrier_index-3.5),.05,.99)',
        'day':'normalized matching date for valid keys; FlightDate otherwise',
        'heterogeneity':'+.03 when low bit of final SHA256 byte of UTF8 OriginAirportID|DestAirportID|band is 1; -.03 otherwise',
        'invalid_key_encoding':'Missing integer endpoint or band = -1; retain numeric invalid endpoint IDs',
        'carrier_order':model.codes,
        'national_only':'Calibrated cases use one p per source-year/carrier/date. Average clipped per-record bases within that variable; this preserves the exact minimizer of per-record squared loss. Uncalibrated nominal cases retain per-record heterogeneity; cell averages are used only in linear expectations.'},
      'calibration':{
        'probability_definition':'For every enumerated process, p is the deterministic global minimizer returned by simulation_model.Model.calibrate(process) on the sealed simulation cells, counts and operator. The full probability vector is specified by this executable mathematical definition, not an outcome-fitted coefficient.',
        'objective':'sum_records (p_cell - p_base_record)^2; one probability per carrier/shared-cell or national-only carrier/date',
        'bounds':[.05,.99],'constraints':'All active ordered-edge A/B G,-D equal the template values. Stable templates impose every G=D=increment*(index_a-index_b) in both periods. Boundary templates impose all specified nonactive-pair R/H caps by exhaustive min-branch enumeration.',
        'scoring':'Targets are failure-imputed primary expectations. Informative masking leaves contrasts unchanged; MCAR/status multiply Q by (1-r) before calibration.',
        'calibration_bases':'Registered stable-order .005 case includes the sorted-carrier base increment before clipping/calibration. All-zero and optional .001 near-tie targets use the no-carrier base. Reversal/boundary cases use the no-carrier base.',
        'solver':'Equality-only unclipped cases: exact SVD least-squares dual. Otherwise strictly convex bounded quadratic dual: scipy.optimize.minimize L-BFGS-B plus up to 100 deterministic projected Newton/SVD refinements. Min-disjunctions: exhaustive deterministic best-bound branching, first violated disjunction, branch order G_A,-D_A,G_B,-D_B. No branch/time limit.',
        'options':{'ftol':1e-15,'gtol':1e-10,'maxiter':10000,'maxls':100},
        'infeasibility':'Dual residual failure invokes scipy.optimize.linprog(method=highs), feasibility tolerance 1e-8. Only LP status 2 proves branch infeasibility; other numerical failure blocks execution.',
        'residual_max':1e-6,
        'tie':'Least objective; equal computed objectives choose lexicographic probability vector in sealed model-cell order. Branch pruning uses the dual Lagrangian lower bound, with conservative 1e-7 floating-point slack.',
        'two_edge':'All 210 structural sets and all four directions; both active edges receive each enumerated boundary configuration. Infeasible two-edge scenarios are recorded, never selected by performance. An infeasible mandatory single edge blocks the full gate.',
        'numeric_calibration_gate':'NOT RUN. Numerical optimizer evaluation and all-case feasibility certification remain mandatory before any gate can pass.'},
      'expected_truth':{
        'representation':'Exact executable expressions, evaluated by Model.truths, with numeric sealed T and count/base coefficients in simulation-structure.json; all 336 components returned in frozen components.txt order.',
        'latent':'T @ p; each G,D subtracts its registered a and b score rows.',
        'none':{'primary':'p','unknown':'0'},
        'informative':{'primary':'p-r','unknown':'r'},
        'mcar_or_status':{'primary':'p*(1-r)','unknown':'r*(.7+.3*p)'},
        'endpoints':'primary contrast; low=primary contrast - b unknown score; high=primary contrast + a unknown score, in national and matched populations.',
        'R':'max_ordered_pair min_period min(G,-D)',
        'H':'max_ordered_pair,period min(G,-D)',
        'pre_draw_check':'Evaluate and record the entire probability/endpoint/latent truth vector before each process emits its first outcome.',
        'boundary_numerics':'Residual tolerance does not excuse errors: include false-changes applicability when numerical R<=.02+1e-6 and false-survives applicability when H>=.02-1e-6.'},
      'probit':{
        'formula':'Z=sqrt(1+v)*Phi_inverse(p)+national_week+origin_week+destination_week+carrier_week+epsilon; timely iff Z>0',
        'epsilon':'independent N(0,1) per flight; independent Bernoulli marginal cases use the same probit with all shared variances zero',
        'stationary':'First physical week shock N(0,sd^2); later ar*prior + sd*sqrt(1-ar^2)*N(0,1)',
        'continuity':'Full physical Monday-week range; no year restart; same physical week shares shocks across source years.',
        'airport_identity':'One common numeric airport-ID series for origins and destinations; missing numeric ID uses -1. Two equal endpoints contribute twice the same shock, hence 4*sd^2 variance.',
        'variance':'national_sd^2 + (2 or 4 for equal endpoints)*airport_sd^2 + carrier_sd^2; inactive types contribute zero.',
        'shock_order':'national, airport, carrier; then numeric entity ID; then physical week'},
      'status':{
        'failure_assignment':{'cancelled':.25,'diverted':.05,'known_late':.70},
        'complete_delay':{'timely':0,'late':20},
        'known_failure_delay':'missing; other flag zero',
        'uniforms':'Exactly 3 independent uniforms per source flight, row-major: failure category, masking, flag choice.',
        'informative':'Mask delay of latent timely flights iff uniform < r/p.',
        'mcar':'Mask delay of each completed flight iff uniform < r.',
        'status':'Blank exactly one completed-flight flag iff uniform < r; second uniform for .5 flag choice.',
        'precedence':'rules.status; invalid nonmissing flags or nonfinite/non-numeric delays stop.'},
      'streams':{'seed_sequence':[20261006,'bank','process_id','replicate_id','stream_id'],
        'generator':'Generator(PCG64)','banks':{'0':'selection','1':'independent validation'},
        'stream_ids':{'0':'Gaussian shocks','1':'flight innovations','2':'status/masking uniforms','3':'bootstrap indices'},
        'replicate_start':0,'flight_order':'source_year,source_month,numeric source_row',
        'resampler_change':'Same generated dataset; reset only bootstrap stream.'},
      'quality_fixtures':[
        {'name':'unknown_at_cutoff','count':'floor(.001*n_carrier_year)','mapping':'First known-completed source IDs: both flags 0, delay missing','quality_pass':True},
        {'name':'unknown_above_cutoff','count':'floor(.001*n_carrier_year)+1','mapping':'Same as at-cutoff','substantive_verdicts_allowed':0},
        {'name':'keys_at_cutoff','count':'floor(.001*n_carrier_year)','mapping':'First valid-key source IDs become invalid matching keys; retain national rows and fixed pair roster','quality_pass':True},
        {'name':'keys_above_cutoff','count':'floor(.001*n_carrier_year)+1','mapping':'Same as at-cutoff','substantive_verdicts_allowed':0},
        {'name':'invalid_flag','mapping':'First record Cancelled=2','must_stop':True},
        {'name':'invalid_delay','mapping':'First completed record ArrDelay=nonfinite','must_stop':True}],
      'banks':{'selection':{'datasets_per_scenario':1000,'draws_per_dataset':5000},
               'validation':{'datasets_per_scenario':2000,'draws_per_dataset':5000}},
      'resampler_order':['independent weeks','circular 4 weeks','circular 8 weeks'],
      'execution':'Commit this manifest and all code/structure seals before generator --emit or any synthetic gate. No random draw was made to prepare this seal.'}
    dump(OUT/'scenario-manifest.json',manifest)
    progress(f'Executable scenario specification sealed: {sum(counts.values()):,} templates ×150 stresses ×10 missingness settings = {manifest["enumeration"]["processes"]:,} fixed process IDs. All exact probability/calibration/336-component truth expressions and generator coefficients frozen. Base expectation/operator checks pass without random draws; full numerical calibration remains unrun. STOP at mandatory scenario/generator commit before synthetic outcomes.')
    print(dict(templates=sum(counts.values()),processes=manifest['enumeration']['processes'],
      disjoint_sets=disjoint,synthetic_outcomes_generated=0))

if __name__=='__main__':main()
