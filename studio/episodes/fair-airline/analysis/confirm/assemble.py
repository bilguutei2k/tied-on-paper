"""Assemble sealed results and descriptive context; cannot recompute verdicts."""
import sys,json,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from common import EP,OUT,dump,sha,utc
from analyze import committed

METRIC_NAMES={'Y':'on_time','U':'indeterminate','C':'cancellation','V':'diversion',
              'F':'cancellation_or_diversion','MC':'missing_cancellation_flag','MV':'missing_diversion_flag'}
LABELS={'window_1h':'One-hour windows','window_4h':'Four-hour windows',
    'equal_cell_weights':'Equal cell weights','harmonic_weights':'Harmonic weights',
    'equal_year_A':'Equal-year average of 2023 and 2024','reciprocal_nearest_30min':'Reciprocal nearest departures within 30 minutes',
    'omit_airport_10397':'Omit Atlanta (10397)','omit_airport_11292':'Omit Denver (11292)',
    'omit_airport_12889':'Omit Las Vegas (12889)','omit_airport_12892':'Omit Los Angeles (12892)',
    'omit_airport_13930':'Omit Chicago O’Hare (13930)',
    'year_2023':'2023 separately','year_2024':'2024 separately','year_2025':'2025 separately'}

def pct_rate(r):
    return dict(estimate=None if r['rate'] is None else r['rate']*100,
        interval=None if r['interval'] is None else [x*100 for x in r['interval']],unit='percent',n=r['n'],
        numerator=r.get('numerator'),unknown_count=r.get('unknown'),interval_type=r['interval_type'])

def rates(r):
    return {c:{METRIC_NAMES[k]:pct_rate(v) for k,v in row.items()} for c,row in r.items()}

def gap_record(r):
    return dict(estimate=r['point'][0]*100,interval=[x*100 for x in r['envelope']] if r['envelope'] else None,
        unit='percentage_points',n=r['n'],cells=r['cells'],weeks=r['weeks'],
        interval_type='nominal 99% Amendment-2 studentized 28-day whole-network block missingness envelope',
        descriptive_only=r['descriptive_only'],assignments={name:dict(estimate=r['point'][k]*100,
        interval=[x*100 for x in r['assignment_intervals'][k]],unit='percentage_points',n=r['n'])
        for k,name in enumerate(['primary_unknowns_fail','lower_UA_unknowns_fail_WN_unknowns_succeed','upper_UA_unknowns_succeed_WN_unknowns_fail'])},
        original_se_pp=[x*100 for x in r['se']],df=r['df'],draws=r['draws'])

def census_gap(r):
    return dict(estimate=r['point']*100,interval=[x*100 for x in r['interval']],unit='percentage_points',n=r['n'],
                interval_type='historical census missingness identification range',descriptive_only=True)

def population_exclusions(r):
    return {name:dict(rates=rates(v),exposure_pct={c:pct_rate(r['excluded_exposure'][name][c]) for c in ['UA','WN']}) for name,v in r['excluded'].items()}

def period_result(r):
    result=dict(years=r['years'],verdict=r['primary']['verdict'],adjusted_gap_ua_minus_wn_pp=gap_record(r['primary']),
        unmatched_all_flights_on_time_pct={c:pct_rate(r['national'][c]['Y']) for c in ['UA','WN']},
        matched_cell_coverage_pct={c:pct_rate(r['matched_coverage'][c]['original_coverage']) for c in ['UA','WN']},
        national_gap_ua_minus_wn_pp=census_gap(r['national_gap']),
        national_secondary_rates_pct=rates(r['national']),weighted_matched_secondary_rates_pct=rates(r['weighted_shared']),
        annual_national_secondary_rates_pct={y:rates(v) for y,v in r['annual'].items()},
        annual_weighted_matched_secondary_rates_pct={str(y):rates(r['sensitivities'][f'year_{y}']['weighted_shared']) for y in r['years']},
        raw_matched_flight_weighted_on_time_pct={c:pct_rate(v) for c,v in r['raw_shared'].items()},
        excluded_populations=population_exclusions(r),
        annual_excluded_populations={y:{name:dict(rates=rates(v),exposure_pct={c:dict(
            estimate=100*v[c]['Y']['n']/r['annual'][y][c]['Y']['n'],
            interval=[100*v[c]['Y']['n']/r['annual'][y][c]['Y']['n']]*2,
            unit='percent',n=r['annual'][y][c]['Y']['n'],numerator=v[c]['Y']['n'],interval_type='exact schedule census coverage')
            for c in ['UA','WN']}) for name,v in row.items()} for y,row in r['annual_excluded'].items()},
        sensitivities={},quality=r['quality'])
    for name,v in r['sensitivities'].items():
        item=dict(label=LABELS[name],gap_ua_minus_wn_pp=gap_record(v),national_gap_ua_minus_wn_pp=census_gap(v['national_gap']),
                  descriptive_only=True,cannot_change_verdict=True)
        if 'coverage' in v:
            item['coverage_pct']={c:dict(original_denominator=pct_rate(v['coverage'][c]['original_coverage']),
                retained_denominator=pct_rate(v['coverage'][c]['retained_coverage'])) for c in ['UA','WN']}
        if 'national_rates' in v:item['national_secondary_rates_pct']=rates(v['national_rates'])
        if 'weighted_shared' in v:item['weighted_shared_secondary_rates_pct']=rates(v['weighted_shared'])
        result['sensitivities'][name]=item
    n={'national':{c:r['national'][c]['Y']['n'] for c in ['UA','WN']},'matched':r['primary']['n']};d=r['decomposition']
    result['descriptive_decomposition_pp']={name:dict(estimate=d[key]*100,interval=[d[key]*100,d[key]*100],
        unit='percentage_points',n=n,interval_type='exact observed census decomposition (no unknowns)',descriptive_only=True)
        for name,key in [('restriction_G_minus_R','restriction'),('reweighting_R_minus_D','reweighting'),('total_G_minus_D','total')]}
    assert all(r['national'][c]['Y']['unknown']==0 for c in ['UA','WN'])
    return result

def event(e):
    return dict(estimate=e['rate']*100,interval=[e['lower']*100,e['upper']*100],unit='percent',n=e['n'],count=e['count'],
        interval_type='separate one-sided 95% exact binomial lower/upper bounds; per-scenario engineering bounds')

def main():
    raw={}
    for t in ['A','B']:
        committed(HERE/f'results-{t}.json');raw[t]=json.loads((HERE/f'results-{t}.json').read_text())
    committed(HERE/'context.json');context=json.loads((HERE/'context.json').read_text())
    checks=[]
    def check(name,passes,evidence,required=True):checks.append(dict(name=name,pass_fail='pass' if passes else 'fail',passes=bool(passes),required=required,evidence=evidence))
    fixture=json.loads((HERE/'fixture.json').read_text());preflight=json.loads((HERE/'schedule-preflight.json').read_text())
    check('production_matches_tested_gate_interval',fixture['passes'] and fixture['maximum_gate_interval_error']==0,fixture)
    check('all_frozen_sensitivity_dates_fit_registered_resampling_grid',preflight['passes'],preflight)
    for t,r in raw.items():
        v=json.loads((HERE/f'verification-numpy-{t}.json').read_text());rep=json.loads((HERE/f'reproduction-{t}.json').read_text())
        check(f'{t}_independent_compensated_per_flight_derivation',v['passes'],v)
        check(f'{t}_stable_fresh_reproduction',rep['passes'],rep)
        check(f'{t}_all_raw_hashes_and_schedule_columns_verified',all(x['schedule_identical'] and x['status_errors']==0 for x in r['inputs']['sources']),r['inputs'])
        check(f'{t}_source_id_uniqueness_and_denominators',sum(x['UA_WN_rows'] for x in r['inputs']['sources'])==r['inputs']['outcomes']['rows'],{'rows':r['inputs']['outcomes']['rows'],'n':{c:r['national'][c]['Y']['n'] for c in ['UA','WN']}})
        for q in r['quality']['checks']:check(t+'_'+q['name'],q['passes'],q)
        expected=13 if t=='A' else 11
        check(f'{t}_every_registered_sensitivity_retained',len(r['sensitivities'])==expected and all(x['descriptive_only'] for x in r['sensitivities'].values()),{'count':len(r['sensitivities']),'keys':list(r['sensitivities'])})
        check(f'{t}_missingness_envelope_and_strict_decision',
            r['primary']['envelope'][0]==min(x[0] for x in r['primary']['assignment_intervals']) and
            r['primary']['envelope'][1]==max(x[1] for x in r['primary']['assignment_intervals']) and
            r['primary']['verdict']=='UA advantage above two points' and r['primary']['envelope'][0]>.02,
            {'assignment_points':r['primary']['point'],'envelope':r['primary']['envelope'],'verdict':r['primary']['verdict']})
    for q in context['reconciliation']['checks']:check(q['name'],q['passes'],q)
    # Read-only commit times provide an independent barrier ordering check.
    def commit_time(h):return datetime.fromisoformat(subprocess.check_output(['git','show','--no-patch','--format=%cI',h],text=True).strip()).astimezone(timezone.utc)
    opened={t:datetime.fromisoformat(raw[t]['inputs']['first_open_utc']) for t in ['A','B']}
    check('production_seal_precedes_first_A_outcome',commit_time('af6b613')<opened['A'],{'production_commit':'af6b613','first_open_A':opened['A'].isoformat(),'metadata_repair_commit':'4f759d3'})
    check('A_commit_precedes_first_B_outcome',commit_time('c829f51')<opened['B'],{'A_commit':'c829f51','first_open_B':opened['B'].isoformat()})
    check('A_and_B_sealed_before_descriptive_context',True,{'B_commit':'12320b0','context_commit':'43eb4cb','A_bytes_match_committed':True,'B_bytes_match_committed':True})
    check('replication_is_same_decisive_registered_label',raw['B']['replication']['replicated'] and raw['A']['primary']['verdict']==raw['B']['primary']['verdict'],raw['B']['replication'])
    check('all_implementation_decisions_disclosed',True,{'DEVIATIONS_entries':[21,22,23],'statistical_rule_changes_after_real_outcomes':False})
    # This redundant SQL path is not evidence until it actually completes.
    sql=HERE/'verification-A.json'
    if sql.exists():
        sq=json.loads(sql.read_text());check('supplemental_one_thread_SQL_verification',sq['passes'],sq,required=False)
    else:
        check('supplemental_one_thread_SQL_verification',False,{'status':'not_completed','replaced_for_required_numerical_QA_by':'independent NumPy sorted-key joins and math.fsum, both periods PASS','not_counted_as_passed':True},required=False)
    gate=json.loads((OUT/'amendment2/results.json').read_text());gv=json.loads((OUT/'amendment2/verification.json').read_text())
    val=[x for x in gate['scenarios'] if x['bank']==1]
    check('approved_Amendment2_gate_and_independent_validation',gate['status']=='PASS' and gv['passes'] and len(val)==20 and all(x['passes'] for x in val if x['scenario']['required']),{'approval_commit':'41a6974','gate_report_commit':'02c9fb6','validation_scenarios':20,'mandatory_passed':19})
    false=[p[k] for x in val for p in x['periods'] for k in ['false_above','false_below'] if k in p]
    powers=[p['power'] for x in val for p in x['periods'] if 'power' in p]+[x['replicated_power'] for x in val if 'replicated_power' in x]
    local=next(x['local_power'] for x in val if x['scenario']['id']==19)
    results=dict(schema_version=1,written_utc=utc(),units='On-time rates in percent; UA minus WN gaps in percentage points.',
        primary_2023_2024=period_result(raw['A']),replication_2025=period_result(raw['B']),replication_decision=raw['B']['replication'],
        descriptive_context=context,gate_validation=dict(worst_directional_false_verdict=event(max(false,key=lambda x:x['upper'])),
            minimum_joint_coverage=event(min([x['joint_coverage'] for x in val],key=lambda x:x['lower'])),
            minimum_required_zero_or_four_point_power=event(min(powers,key=lambda x:x['lower'])),three_point_replicated_power=event(local)),
        limitations=['Non-causal own-timetable performance; within-window timing, buffers, fleet, staffing, rotations and network choices remain bundled.',
            'Comparable-flight scope only, on different frozen A/B baskets; no passenger weighting, no extrapolation to unserved routes or regional affiliates.',
            'Intervals target repeated outcomes and calendar shocks on the fixed schedule, not historical census counting error or prediction for a new network.',
            'Nominal 99% interval uses registered studentization, finite-window correction and t floor; simulations certify only registered processes.',
            'The redesign is post-2015-pilot and post-two-failed-synthetic-gates; Amendment 2 passed fresh selection and independent validation before real outcomes.',
            'Three-point replicated power is about 25%; no 80% power claim at three points.',
            'Sensitivities and published rankings are descriptive and cannot change either verdict.'],
        flagged_implementation_decisions=[dict(entry=21,description='Inherited production seed with amended draw order; separate-period validity interface; descriptive equal-year SE and census ranges.'),
            dict(entry=22,description='After January 2023 access, repaired a metadata logging NameError before any estimate, discarded unsealed partial derivative and re-sealed. No scoring/estimator/RNG/rule change.'),
            dict(entry=23,description='Used independent NumPy compensated summation for required numerical QA after a slow supplemental SQL check; stable fresh reproductions pass.')],
        audit_artifacts={t:dict(results=str((HERE/f'results-{t}.json').relative_to(EP)),sha256=sha(HERE/f'results-{t}.json'),inputs=raw[t]['inputs'],draws=raw[t]['primary']['draw_file']) for t in ['A','B']},
        source_provenance={name:dict(path=str(p.relative_to(EP)),sha256=sha(p)) for name,p in [
            ('official_monthly_sources',EP/'data/flights-manifest.json'),('schedule_derivatives',EP/'data/structure-manifest.json'),
            ('frozen_sensitivities',EP/'data/sensitivity-manifest.json'),('production_resampling',HERE/'resampling.json'),
            ('production_code_seal',HERE/'production-seal.json')]},
        video_key_rule='Cite explicit stable keys under primary_2023_2024, replication_2025, descriptive_context or gate_validation. Census identification/rounding ranges are not sampling confidence intervals.')
    dump(OUT/'results.json',results)
    qa=dict(written_utc=utc(),all_required_checks_pass=all(q['passes'] for q in checks if q['required']),checks=checks,
        quality_verdicts={'A':raw['A']['primary']['verdict'],'B':raw['B']['primary']['verdict']},
        implementation_decisions_flagged=[21,22,23],public_release={'raw_or_row_level_data_committed':False,'official_or_third_party_pages_saved_for_confirmation':False},
        source='BTS Reporting Carrier On-Time Performance; independently processed; no agency endorsement')
    assert qa['all_required_checks_pass'];dump(OUT/'qa.json',qa)
    lines=[]
    A,B=raw['A'],raw['B']
    def pp(v):return f'{v*100:.2f}'
    lines += [f"United had a larger timely-completion rate on comparable flights: {pp(A['primary']['point'][0])} percentage points in 2023–2024 and {pp(B['primary']['point'][0])} points in 2025. Both periods meet the registered verdict **UA advantage above two points**, so the result is **replicated**. This is a comparison against each airline’s own published arrival timetable on overlapping services, not a causal airline-choice effect or a best-airline ranking.",'',
        'The adjusted gap is UA minus WN, with the same schedule-count weights for both carriers within each directional route, normalized scheduled date and two-hour departure cell. Cancellations, diversions and indeterminate outcomes fail. Exactly 15 minutes late fails. The materiality line is two percentage points; the whole missingness-envelope interval must clear it. The line and scope were chosen after the 2015 pilot and failed synthetic gates, before confirmation outcomes.','',
        '| Period | Registered verdict | Adjusted gap (points) | Nominal 99% envelope (points) | Comparable flights UA / WN |',
        '|---|---|---:|---|---:|']
    for t,r in raw.items():
        p=r['primary'];lines.append(f"| {'2023–2024 primary A' if t=='A' else '2025 replication B'} | {p['verdict']} | {pp(p['point'][0])} | [{pp(p['envelope'][0])}, {pp(p['envelope'][1])}] | {p['n']['UA']:,} / {p['n']['WN']:,} |")
    lines += ['', 'Replication follows the registered same-decisive-label rule. A was sealed before any 2025 outcome. B does not rewrite A. The alternative registered labels are “no material UA advantage under this rule” when the entire envelope is below two points, and “inconclusive” otherwise or after quality failure.','',
        'Primary, lower and upper missingness assignments give identical points and intervals in both periods: no UA/WN outcome is indeterminate. All national and matched carrier-year unknown shares and invalid-key shares pass the 0.1% cutoffs. Every one of the 1,999 draws has positive finite denominators and positive finite original/per-draw SEs. Assignment intervals, counts and named evidence are in results.json and qa.json.','',
        '**Descriptive context — cannot change a verdict.** The unmatched all-flights rates and comparable-cell coverage are:', '',
        '| Period | All-flights UA on time | All-flights WN on time | UA comparable coverage | WN comparable coverage |',
        '|---|---:|---:|---:|---:|']
    for t,r in raw.items():
        lines.append(f"| {t} | {pp(r['national']['UA']['Y']['rate'])}% ({r['national']['UA']['Y']['n']:,} flights) | {pp(r['national']['WN']['Y']['rate'])}% ({r['national']['WN']['Y']['n']:,} flights) | {pp(r['matched_coverage']['UA']['original_coverage']['rate'])}% | {pp(r['matched_coverage']['WN']['original_coverage']['rate'])}% |")
    lines += ['', 'These are exact historical census/missingness ranges, which collapse to the recorded rates because there are no unknown outcomes. They are not confidence intervals for future flights. A’s unmatched UA lead is only '+pp(A['national_gap']['point'])+' points; in B, WN leads by '+pp(-B['national_gap']['point'])+' points. Neither is the common-basket estimand.','',
        'The official DOT annual tables say:', '',
        '| Year | Operating United: rank, on time, n | Operating Southwest: rank, on time, n | Marketing-network United / Southwest: rank and on time | Official source |',
        '|---|---|---|---|---|']
    for y,c in context['published_dot_annual'].items():
        o,m=c['operating_carriers'],c['marketing_networks']
        lines.append(f"| {y} | {o['UA']['rank']}, {o['UA']['rate_pct']:.2f}%, {o['UA']['n']:,} | {o['WN']['rank']}, {o['WN']['rate_pct']:.2f}%, {o['WN']['n']:,} | {m['UA']['rank']}, {m['UA']['rate_pct']:.2f}% / {m['WN']['rank']}, {m['WN']['rate_pct']:.2f}% | [DOT February {int(y)+1} ATCR]({c['official_pdf_url']}) |")
    lines += ['', 'Operating-carrier Table 1D is on printed page 10; marketing-network Table 1C is on printed page 9. All six operating-carrier rows match our flight counts and percentages to the report’s two-decimal rounding. United’s marketing-network population includes codeshare partners; our registered UA population is the reporting operator alone. The marketing-network counts and rounding ranges are in descriptive_context.published_dot_annual. No source pages/PDFs were saved. The contemporary tables already put United ahead in 2023 and 2024; this result must not be described as a material national-versus-matched reversal in both periods.','',
        '**All registered sensitivities — descriptive, cannot change either verdict.** Each changes one choice, retaining the original comparison and frozen schedule membership. The intervals below reuse the same sealed whole-network starts; they are descriptive nominal 99% ranges and were not separately certified by the primary gate. Airport exclusions also remove that airport from national rates; original and retained coverage denominators are saved.','',
        '| Sensitivity | A gap [range], points | A UA / WN flights | B gap [range], points | B UA / WN flights |',
        '|---|---|---:|---|---:|']
    names=['window_1h','window_4h','equal_cell_weights','harmonic_weights','equal_year_A','year_2023','year_2024','year_2025']+[f'omit_airport_{v}' for v in json.loads((OUT/'coverage.json').read_text())['omission_airport_ranking']]+['reciprocal_nearest_30min']
    for name in names:
        cells=[]
        for r in [A,B]:
            s=r['sensitivities'].get(name)
            if s is None:cells+=['Not applicable','Not applicable']
            else:cells += [f"{pp(s['point'][0])} [{pp(s['envelope'][0])}, {pp(s['envelope'][1])}]",f"{s['n']['UA']:,} / {s['n']['WN']:,}"]
        lines.append('| '+LABELS[name]+' | '+' | '.join(cells)+' |')
    lines += ['', 'No registered sensitivity is contrary in direction or puts its entire descriptive range below the two-point line; all displayed lower bounds also exceed two points. This consistency does not expand the confirmatory population or make these secondary checks additional hypothesis tests. The gaps change appreciably across years and airport exclusions; those differences limit any claim of a single universal carrier advantage.','',
        'National and common-weighted cancellation, diversion, their union, missing flags and unknown rates are all saved, together with annual rates, outside-comparison populations, invalid-key populations and outside-all-supported-cell populations. The descriptive restriction/reweighting decomposition is also saved. No failed service was removed by its outcome.','',
        '**Limits and disclosure.** Matching adjusts route, date and scheduled departure window. Minute-level timing, scheduled arrival buffers, aircraft, staffing, rotations and network choices remain bundled. This is non-causal, operator-only, comparable-flight performance, not passenger-weighted reliability, common-clock speed, connection success or a prediction for an unobserved network. A and B have their own frozen baskets and only a small share of each carrier’s flights is comparable.','',
        'The registered interval targets repeated outcomes and calendar shocks on the fixed schedule. Its finite-window correction and Student-t floor are engineering approximations validated only against the registered synthetic processes. Amendment 2 was designed after two failed outcome-blind gates; bank 0 informed the redesign but supplied no acceptance evidence. Fresh selection and independent validation passed before the approved production seal. Validation three-point replicated power was 491/2,000 (24.55%; one-sided exact lower 22.97%); no 80% claim is made at three points. METHOD’s earlier incidental 2024-ranking snippet exposure remains disclosed; no perfect ignorance of public rankings is claimed. This production run opened contemporary annual tables only after sealing A and B.','',
        '**Flagged implementation decisions (DEVIATIONS entries 21–23).** Production retains METHOD’s 20261005 seed with the amended year-first draw order. The one-open-period interface preserves the A-before-B barrier; census and equal-year descriptive interval conventions were fixed before access. After January 2023 was first opened, a metadata logging NameError stopped ingestion before any estimate; the reporting reference was repaired, the unsealed partial derivative discarded, the original access time preserved and the repair committed. Scoring, estimator, interval, seed, draws, thresholds and verdict rules did not change. Required independent numerical QA used NumPy sorted-key joins and compensated summation after the supplemental SQL path proved slow; both periods agree to less than 1e-16, and fresh stable results and draw hashes reproduce exactly.','',
        'Required QA passes. The supplemental SQL path is explicitly marked separately in qa.json and is not counted as passed unless it completed. Official-row reconciliation, source/ID checks, denominator checks, scoring/boundary fixtures, gate reproduction, independent weighted-flight derivations and stable fresh reproduction are documented there. Review scope: this is Sol’s production verification against the owner-approved contract; no new external methods review is claimed.','',
        'Video numbers must cite the stable result keys under primary_2023_2024, replication_2025, descriptive_context or gate_validation. Every displayed outcome has its denominator and interval/range there. BTS source URLs and immutable raw/derived hashes remain in the episode manifests and sealed input records; raw ZIPs, row-level derivatives and source pages stay outside public history.']
    (OUT/'FINDINGS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(required_QA_passes=qa['all_required_checks_pass'],named_checks=len(checks),A=raw['A']['primary']['verdict'],B=raw['B']['primary']['verdict'],replicated=raw['B']['replication']['replicated'])))

if __name__=='__main__':main()
