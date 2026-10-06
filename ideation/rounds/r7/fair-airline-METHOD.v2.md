Does the published-style airline order survive comparison on the same routes, dates and two-hour departure windows?
Use eight named operators in 2023–2024 and 2025; freeze supported pairs from schedule-only counts before any confirmation outcomes; 2015 is exploration.
“Changes”: the same pair reverses in both periods, with simultaneous 95% bounds establishing advantages greater than 2 percentage points on each side.
“Survives”: simultaneous upper bounds rule out every 2-point reversal among supported pairs in both periods; this allows smaller swaps.
Otherwise the answer is inconclusive; open outcomes only after full-family validity and ≥80% power gates pass at the registered alternatives.
Count arrival under 15 minutes late as success and failed/indeterminate services as failures, with missingness bounds; claims cover overlapping reported services, not causal airline quality.

# Which airline is really most on time? — methods

Status: revised draft pre-registration, 2026-10-06, after reading the 2015 pilot
and external methods review. Owner approval, commit, outcome-blind support audit,
and validity AND power gates are pending. No gate has run. This is an approvable
staged plan, not evidence of adequate power or permission to open outcomes.
No 2019 or 2023–2025 flight files were opened in this review; exposure disclosed
by the earlier draft, including its incidental 2024 ranking snippet, persists.
Later changes go under Amendments with date, reason, exposure and effect on claims.

## Question

Among eight fixed reporting/operating carriers, does a material national
on-time advantage reverse when comparing services sharing a directional
airport route, departure date and scheduled two-hour departure window?
The motivating title is broader: say early that we answer a supported-pair
question, not which airline is best on every route or for every passenger.

## Belief → obvious answer → flaw → fairer test

Belief: the airline higher in the national punctuality table is the better
on-time choice when both airlines serve the trip. The obvious answer is the
published on-time ranking. [DOT's February 2016 Air Travel Consumer Report](https://www.transportation.gov/airconsumer/february-2016-air-travel-consumer-report)
publishes carrier tables; [its annual table, printed p. 5](https://www.transportation.gov/sites/dot.gov/files/docs/resources/individuals/aviation-consumer-protection/155801/2016februaryatcr_0.pdf)
ranks 2015 performance. [Forbes, 27 April 2015](https://www.forbes.com/sites/michelinemaynard/2015/04/27/the-best-and-worst-airlines-for-summer-2015-vacation-travel/)
turns BTS punctuality rankings into advice about selecting airlines for summer
travel. These document publication and consumer interpretation, not the truth
of a causal claim. No contemporary ranking is needed to motivate this test.

Flaw: national averages compare different routes, dates and departure times.
An airline serving easier circumstances can rank higher without doing better
where the carriers overlap. Both airlines also choose their scheduled arrival
times. Matching scheduled departures does not give them a common arrival deadline.
DOT already includes failed services in its reported-flight denominator: do not
claim otherwise. The pilot's completed-flight `naive` rate is a separate sensitivity.

Fairer test: keep the same all-scheduled success definition on both sides;
give each pair the same observed route/date/departure-window distribution.
This adjusts the comparison for those measured circumstances. Minute-level
timing, schedule buffers, aircraft, staffing, rotations, hubs, passenger mix
and operational choices remain bundled with carrier differences. Neither an
airline-choice effect nor deliberate timetable gaming is identified.

## Scope, sources and exposure

- Confirmation: all 36 monthly BTS Reporting Carrier On-Time Performance ZIPs,
  January 2023–December 2025. Primary period A is 2023–2024; replication B is
  2025. No alternative years, 2019 benchmark or extra exploratory flight data.
- Endpoint template: `https://www.transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{YYYY}_{M}.zip`.
  Use unpadded month; record member names, retrieval dates, bytes and SHA-256s.
  Official definitions: [BTS table dictionary](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ)
  and ATCR explanatory notes. Resolve and seal the documentation before ingestion;
  the source/rights register below records the current verification status.
- Fixed codes/DOT IDs: AA/19805, AS/19930, B6/20409, DL/19790, F9/20436,
  NK/20416, UA/19977, WN/19393. Verify identity/coverage against official metadata
  before outcome access. Codes must agree with IDs; unresolved changes stop analysis.
  These are reporting operators, not whole marketed brands or regional affiliates.
  Do not combine regionals, subsidiaries or merger partners into these operators.
- Eight candidates are inherited from the pilot. Exclude HA, VX, other operators,
  international services and connections; keep all reported domestic nonstop
  services, including US territories, in the chosen operators' source population.
  Exclusion of Hawaiian means this is not a test of the entire national table.
- Save immutable ZIPs and a selected-column derivative; hash both. Use IDs
  `YYYY-MM:source-row-ordinal`, source order, LF-terminated sorted manifest.
  Check year/month/date and source-row uniqueness; do not assume flight numbers
  are unique. Analysis reads frozen files and never fetches.
- Phase 1 reads only schedule/identity fields: source IDs, flight date, carrier,
  airport IDs, flight number and scheduled departure. No cancellations,
  diversions, actual times, delays, completion counts or outcome-based exclusions.
  Freeze support lists/code hashes and validate synthetic outcomes on that structure.
  Generate bootstrap weight arrays in Phase 1. After the gate, freeze A's point
  estimates and bootstrap draws before B; the final joint critical value uses both.
  Do not consult 2023–2025 published outcome tables before the gate; annual
  published-table reconciliation happens after the appropriate outcomes are opened.
- 2015 outcomes, ranks and sensitivities informed this redesign. An incidental
  2024-ranking search snippet appeared during historical source research; its
  article was not opened and it did not inform these rules. No assertion of
  complete ignorance of public rankings. See `airline-redteam.md` for exposure.
- Source/rights register: distinguish raw reporting-carrier records, our derived
  numeric tables/code, official documentation, and third-party articles. The r2
  design (`../r2/verify-S6.json`) records a factual-record/federal-work reuse basis
  but explicitly notes its public-domain metadata link concerns a DIFFERENT
  marketing-carrier product; it is not the raw ZIP's licence. Before any raw-file
  redistribution, record the exact reporting-carrier source terms and their URL,
  retrieval date and privately verified byte hash. If terms are unresolved,
  publish retrieval code, source URLs/hashes and our aggregates, not raw ZIPs or
  row-level derivatives. Attribute BTS; label processing independent; no logos
  or suggestion of agency endorsement. This is a release condition, not grounds
  to select observations or change statistical results.
- Third-party pages and official page/PDF snapshots stay privately stored and
  outside public history. Publish addresses and SHA-256 only for bytes actually
  saved; an access failure has a date/status and no invented hash. Audit the
  proposed public file list/history before release; no blanket licence claim
  covers linked articles or images. Resolve any previously tracked snapshots
  before publication through a separate documented release action.
- The official BTS dictionary was accessible during this methods review on
  2026-10-06: [Reporting Carrier fields](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ).
  It identifies CRSDepTime as local HHMM, signed ArrDelay, unique reporting
  carrier/DOT certificate IDs, and separate cancellation/diversion flags.
  Web-tool access is not a sealed byte snapshot. Before ingestion, freeze a
  field mapping, status rules, domestic/territory metadata and identity lookup
  with hashes; fixture-test 14.999/15, negative delay, blank/nonbinary flags,
  valid/invalid HHMM, midnight normalization and source-boundary clustering.
  Do not open contemporary outcome tables to verify this schema.

## Outcome, support and frozen weighting

For every reported scheduled flight, parse status flags as 0, 1 or missing.
Any nonmissing value outside {0,1}, or an invalid nonmissing numeric delay,
is a data error that stops analysis. Apply this precedence:
1. Either flag is 1: known failure, Y=0, even if the other flag or delay is missing.
2. Both flags are 0 and signed ArrDelay is finite: Y=1 iff ArrDelay<15;
   exactly 15 is a known failure. There is no arrival-delay trimming.
3. Otherwise: indeterminate outcome, primary Y=0, uncertainty indicator U=1.
All other rows have U=0. Cancellation and diversion indicator rates count their
own known flags separately, including both if both equal 1; do not double-count
rows in the union of failed services. Missing flags are reported separately.

Primary scores measure recorded timely completions with indeterminate outcomes
scored as failures. They are not necessarily latent true timely-completion rates.
For each contrast a−b, the low completion endpoint sets U rows of a to 0 and
of b to 1; the high endpoint does the reverse, in BOTH national and shared scores.
Known failures can never become successes. Uncertainty intervals for this
partially identified completion contrast use the envelope over primary and both
endpoints; the conservative envelope also governs the primary verdict.
This concerns reported scheduled flights, not unreported service, rebooking,
missed connections, fares, safety or passengers' eventual arrival.

Stratum s = source year × directional `(OriginAirportID, DestAirportID)` ×
scheduled local departure date × `floor(departure_minutes/120)`.
Windows are [00:00,02:00), …, [22:00,24:00); no actual-departure matching.
Parse CRSDepTime as integer HHMM: hours 0–23 and minutes 0–59 are valid;
2400 alone maps to next-day 00:00. The matching date is this normalized date.
Retain source year for cohort membership, so matching never crosses source years.
Other invalid/missing schedule keys cannot match. Airport IDs must be valid
in the frozen official airport metadata; never merge airports or reverse routes.
Cluster ID is (source year, Monday-start week of the NORMALIZED matching date).
Use this same ID for support, every valid-key row and all pair-cell contributions.
This prevents a Sunday-2400/Monday-0000 shared cell from spanning two clusters.
For an unmatchable record with valid FlightDate, use its FlightDate week for its
national-only contribution. Invalid FlightDate or source-year/month inconsistency
stops ingestion. Source-year boundary clusters stay separate in resampling;
this is an approximation that must pass simulations with shocks continuous
across those boundaries. Keep source membership even if normalization enters
the following year. Record boundary counts and test fixtures before outcomes.

For pair a,b, retain only strata with both carriers scheduled. Let n_cs be
scheduled flights, p_cs their arithmetic mean Y, and w_s=(n_as+n_bs)/2.
Direct adjusted gap D_ab = Σ_s w_s(p_as−p_bs)/Σ_s w_s.
Both carriers receive exactly the same stratum weights; each flight within a
carrier/stratum has weight w_s/n_cs. No passenger weights, equal-opponent
average, shrinkage or fixed-effect network projection enters the verdict.
This targets that pair's pooled scheduled-flight distribution on its shared
opportunities. Each pair and period has its own basket; there is no common
eight-carrier population and no extrapolation to unserved cells.

National score N_c=ΣY/number of reported scheduled flights for that carrier;
G_ab=N_a−N_b. Pool flights/stratum masses across 2023–2024 for A, rather than
averaging years equally; compute B separately. Reconstruct the published-style
table with this source/denominator and reconcile each annual ATCR reporting
carrier table to displayed rounding. List brand/merger/source-revision differences;
unresolved mismatches prohibit calling our reconstruction the exact published table.

“Supported pair” means precisely the following outcome-blind rule. Start with
all 28 unordered pairs of the eight fixed codes, in lexicographic code order.
Both carriers must have source records in every one of the 36 source months.
For each pair and each source year 2023, 2024 and 2025, count each scheduled
record once if its valid stratum contains both carriers, irrespective of status.
Require ≥500 such records for EACH carrier and ≥40 distinct cluster-week IDs
containing a shared stratum in EACH year. The intersection across the three
years is the single roster used in A, B, all simulations and every bootstrap.
Require ≥4 distinct carriers incident to at least one retained edge. A carrier
or pair failing this rule is unsupported, never tied, and cannot be replaced.
The thresholds are screening minima, not evidence of adequate precision.

Before outcomes are decoded, commit a support manifest containing all 28 pass/fail
rows and reasons, per-carrier/year/month counts, source-row IDs, valid/invalid key
flags, pair-stratum membership, n_cs and w_s, cluster IDs, and the exact vector
component order. Include ZIP/derivative/code hashes, dependency versions, UTC
freeze time and exposure log. Report counts, routes, monthly mass, largest
weekly weight share and effective week count (sum v_w)^2/sum v_w^2, where v_w
is the pair's summed w_s in that year. These diagnostics do not select pairs.
Report missing-key and shared-flight coverage using each carrier's full source
schedule denominator. Keep the roster even if an outcome-quality, precision,
variance or power check later fails: failure blocks the verdict for the entire
registered family; it does not delete the offending edge or shrink multiplicity.

Phase 1 may download and hash full ZIP bytes, but its parser projects only the
listed identity/schedule fields; it must not decode, summarize, log or expose
outcome columns. Store raw files outside public history and deny the analysis
process access until the gate is sealed. Commit the support manifest BEFORE
synthetic outcomes or power results are inspected. Read-only schedule corrections
require a dated new seal and rerun of the entire gate, with outcomes still closed.
Freeze the selected resampler, power/validity report, analysis code, dependencies
and production weight arrays before opening A; seal all A point estimates and
draws before opening B. No pruning based on A; no B-driven reanalysis of A.
No annual ranking tables or flight outcomes from 2023–2025 may be consulted in
Phase 1. Report accidental exposure and stop for a reviewed amendment.

No overall minimum shared-flight percentage licenses national generalization.
The old 40% gate stays retired for this narrower target. If fewer than four
carriers qualify, there is no table verdict; report support only.

Missing schedule-key records remain in national rates but cannot enter D.
Require their share and the unknown-outcome share each ≤0.1% of scheduled
flights per carrier-year; otherwise inconclusive, with bounds shown. Unknown
outcomes are exactly U=1 under the precedence above; invalid nonbinary flags
or unresolved duplicate source records stop outcome analysis.
Resolve confirmed duplicate exports by source provenance, never by their outcome;
natural-key collisions are investigated, not silently collapsed.

## Resampling and simultaneous intervals

These are variability intervals over comparable calendar weeks in the observed
service networks, not uncertainty in counting the historical census, and not
predictions for a new network. Condition on the fixed carrier/pair roster.
Use exactly 5,000 draws in BOTH simulation and production. Pin NumPy and its
quantile implementation in the environment manifest. Use Generator(PCG64(seed))
and integers(0,W_y,size=W_y,endpoint=False) for independent week sampling,
then bincount(minlength=W_y) for multiplicities. Production seed is 20261005;
loop draw index first, then source years 2023, 2024, 2025; week IDs sort by
Monday date, carriers/pairs lexicographically. For block resamplers use the same
integer API for start indices and the fixed block algorithm below. Generate
production arrays once after resampler selection, seal their hashes and reuse
them for all endpoints, secondary summaries and sensitivity specifications.
Changing a sensitivity's cells never regenerates or reorders the cluster draws.
For s_j use sample SD (ddof=1) over complete valid joint draws; center using their
arithmetic mean and use np.quantile(...,0.95,method='linear') for c. Duplicate
components stay in the family. Opposite directions are exact negations, not
additional selected hypotheses. With 28 pairs there are at most
28 × 2 periods × 2 contrasts × 3 scoring assignments = 336 components. Week IDs are the source-year/matching-date clusters defined above;
preserve all partial boundary weeks, including normalized next-year dates. For each draw, in year
order 2023, 2024, 2025, sample W_y week IDs with replacement from its W_y IDs.
Assign each flight its week's multiplicity, jointly across all routes,
airports, carriers and outcomes. Do not resample flights, routes or carriers
independently: the same week's weather/operations span all those dimensions.

Recompute national numerator/denominator ratios and D with weights m_week*w_s;
within each realized dataset, carrier-cell means/counts, support and eligibility
remain fixed across draws; cell means are recomputed for each simulated dataset.
No new pair selection or matching inside draws. Period A pools its sampled
2023/2024 contributions; B uses its independently sampled 2025 contributions.
Calendar-week independence is an assumption; serial shocks are tested in the gate.

Joint vector θ comprises G and D for every eligible unordered pair in A and B,
for failure-imputed scores and both missing-outcome endpoint assignments below
(at most 336 components); this same full family is used for replication.
For component j let s_j be SD across valid bootstrap draws and e_bj=θ*_bj−mean_b θ*_bj.
Let c be the 95th percentile of max_j |e_bj/s_j| (linear quantile interpolation).
Report simultaneous intervals [θ_j−c*s_j, θ_j+c*s_j], without clipping.
Center bootstrap errors to remove bootstrap-location drift, not point-estimate
bias. Nonfinite fits or empty denominators invalidate a joint draw; require
≥4,750/5,000 valid draws and every s_j>0, otherwise inconclusive. No component deletion.
The gate must count dataset-level failures, including zero variance, rather than
report coverage only among datasets that produced intervals.
Pointwise supplementary intervals are labeled and cannot support the table verdict.

## Pass/fail rule and threshold timing

Use the missingness-envelope intervals below throughout this rule.
For each **ordered** pair a,b and period t, define reversal strength
q_ab,t=min(G_ab,t, −D_ab,t). Positive q means a leads nationally and b leads
on matched services. From simultaneous intervals for G and D obtain
Lq=min(LG,−UD), Uq=min(UG,−LD). Reverse-direction intervals follow by negation;
both directions are in the rule, not chosen after seeing who leads.

| Outcome | Numerical condition after all gates | Permitted claim |
|---|---|---|
| Table changes | Some same ordered pair has Lq_A >0.02 AND Lq_B >0.02 | A material national-versus-shared-service reversal repeats in 2025. Name the pair/populations. |
| Table survives | Every ordered eligible pair has Uq_A <0.02 AND Uq_B <0.02 | No reversal as large as 2 points on both sides is compatible with these intervals, among supported pairs in either period. |
| Inconclusive | Neither preceding numerical condition holds, or any gate fails | The test cannot settle material stability. Show estimates, bounds and missing support. |

For clarity, define R=max_ab min(q_ab,A,q_ab,B) and H=max_ab,t q_ab,t,
over all ordered supported pairs. “Changes” requires the simultaneous lower
bound for R >0.02; “survives” requires the simultaneous upper bound for H <0.02.
Construct these bounds by applying the same max/min operations to Lq and Uq.
Thus survival is deliberately stronger than merely ruling out a repeated
reversal: a reversal confined to one period can leave the verdict inconclusive.
These are two separated decision regions, not complementary tests of one scalar.
Equality of the relevant aggregate bound to .02 does not satisfy that verdict.
Apply the table literally; an unrelated pair's equality cannot veto a qualifying
repeated reversal elsewhere in the frozen family.

“Survives” concerns this practical ordering criterion, not identical ranks or
unchanged gap sizes. A near-tie swapping places is allowed; “changes” requires
at least a four-point swing from a >2-point advantage to a >2-point disadvantage.
Absence of a passing reversal alone is not survival. Eligibility limits apply
even if all point ranks agree. No named winner claim from an incomplete pair graph.
Replication means the same pair/direction on each period's own supported basket,
not the same routes, schedules or effect magnitude. Outcomes are descriptive
of reported services. For uncertainty, G and D target their expected scores
under repeated outcomes on the frozen schedule, integrating the stipulated
calendar shocks; the historical census point scores themselves have no sampling
error. Calibration must validate this fixed-schedule target despite the bootstrap
reweighting weeks. No new-network or future-passenger prediction is identified.

Two points means one extra timely completion per 50 scheduled flights; requiring
it on both sides excludes trivial flips. The numerical scale existed in r2
before the 2015 pilot, for a different own-promise/common-clock test. Its use
here, the strict whole-interval rule, two-period symmetry and scope revision
are fixed **after** seeing 2015 and before held-out BTS outcomes. They must not
be described as pre-pilot. Do not lower 2 points to accommodate Southwest's
approximately 1.56-point national pilot lead over United.
The 500-flight and four-carrier gates come from r2; 40 weeks comes from the
post-pilot redesign to avoid temporally concentrated comparisons. The 0.1%
missingness limits cap small denominator ambiguities; bounds still govern claims.

## Pre-confirmation simulation gate — required before real outcomes

On the frozen real 36-month schedule structure only, generate synthetic Y and
status/missingness fields. Run the entire ingestion/scoring, fixed eligibility,
aggregation, resampling, simultaneous-interval and two-period decision pipeline.
Before the first simulated outcome is generated, commit a machine-readable
scenario manifest and executable generator, giving every coefficient, marginal
probability, covariance, status/missingness mapping, calibration constraint,
process order, solver/tolerance, stream and expected G,D/R/H. No coefficients
may be fitted to confirmation outcomes. The manifest must implement the grid
and boundary/power cases below; changing it requires a dated outcome-blind
amendment and a new independent evaluation bank, never selective deletion.

Use a probit latent variable per flight: Z_i=mu_i+u_week+u_origin,week+
u_destination,week+u_carrier,week+epsilon_i, with independent standard-normal
epsilon_i and mutually independent shock processes except shared airport IDs.
For each shock series specify its stationary SD and AR coefficient. Its marginal
variance v_i is known, so set mu_i=sqrt(1+v_i)*Phi_inverse(p_i), ensuring exact
marginal timely-completion probability p_i. Independent Bernoulli cases set all
shared SDs to zero. Airport shocks use one common airport series whether that
airport is origin or destination. AR shocks start stationary and continue across
all physical weeks and source-year boundaries; do not restart them in January.

Base p_i levels are 0.70/0.80/0.90. Stress each with fixed seasonal probability
amplitude 0 or 0.05 times sin(2*pi*(day_of_year-1)/365.25), and fixed route/time
heterogeneity of ±0.03 determined by the low bit of SHA-256 of the UTF-8 key
`OriginAirportID|DestAirportID|band`. No-carrier-effect cases use identical
probabilities for carriers in the same cell. Stable-order cases add carrier
increments 0.005*(j-3.5), j=0,...,7 in sorted code order. Clip these BASE
probabilities to [0.05,0.99] before the deterministic contrast calibration.
Run no-shock cases and national-only, airport-only, carrier-only and combined
shock cases; active series have stationary SD 0.15 and 0.30, with AR coefficients
0, 0.3 and 0.6. Use all listed levels, not a selection based on results.

For reversal/boundary cases calibrate expected per-carrier/cell probabilities
on the real schedule counts, minimizing sum_i(p_i-p_base_i)^2 over records,
subject to the stated linear G,D constraints and 0.05≤p_i≤0.99. Use one p for
all records of a carrier/cell; national-only records form separate carrier/date
cells. For constraints on minima, enumerate the possible binding components
or use a deterministic mixed-integer solver; choose the least objective value,
with lexicographic probability-vector ties. Record residuals ≤1e-6 and truth for
EVERY pair, not just the named one. Infeasible required cases block the gate;
no substituting an easier pair, smaller family or larger target effect.

Generate latent completion from Z_i>0. Among latent failures, use an independent
uniform to assign cancellation/diversion/known-late with probabilities .25/.05/.70;
completed timely/late records receive ArrDelay=0/20 and both flags zero.
Add informative missingness by masking timing only among latent timely records,
with probability r/p_i for r=0.0005, 0.001 or 0.01, giving marginal unknown mass r and
observed timely probability p_i-r. In separate MCAR cases, mask timing on each
known completed record with independent probability r. In separate status cases,
with probability r on each known completed record, blank exactly one flag,
chosen with equal probability; keep its other flag zero and its recorded delay.
These two mechanisms give primary success p_i*(1-r) and marginal U probability
r*(p_i+0.70*(1-p_i)); integrate them in endpoint truths. Add deterministic
fixtures at the quality cutoff and
just above it; random realizations exceeding the cutoff must block the verdict,
even when expected missingness is at or below it. Gate failures count as
nondecisions in power calculations. Test missing keys and invalid flags separately.

Truth is expected G,D on the frozen counts, after the specified scoring and
missingness transformations, not one realized dataset or a 2015 fitted effect.
Use independent RNG streams via SeedSequence([20261006,bank,process_id,
replicate_id,stream_id]) with PCG64: bank 0=selection, bank 1=validation;
stream 0=Gaussian shocks, 1=flight innovations, 2=status/masking uniforms,
3=bootstrap indices. Sort shock types national/airport/carrier, then numeric
entity ID, then physical week; sort flights by source month and numeric ordinal.
Use replicate IDs starting at zero. Never change outcomes when trying another
resampler; reset only the bootstrap stream to the same seed.

Implement Bernoulli/probit generators with marginal mean probabilities known
analytically after integrating Gaussian shocks. Include (1) no carrier effect
but route/time difficulty and unequal networks; (2) additive carrier effects
with stable ordering; (3) heterogeneous carrier×route effects and repeated
reversals of the explicitly calibrated component magnitudes below; (4) national, airport and carrier shocks shared within weeks;
(5) week shocks with AR(1) correlation 0.3 and 0.6, tested separately;
(6) shocks that raise cancellations and informative timing missingness at 0.1%
and 1%, the latter judged only on correctly blocking a verdict; (7) a reversal only in A;
(8) nearly tied carriers and weak supported pairs on the actual overlap graph.
Use baseline success levels 0.70, 0.80, 0.90 and latent shock SDs 0.15/0.30
across stress cases; publish all fixed generator coefficients and seeds.
If outcomes are missing, primary truth includes failure imputation; validate
envelope coverage for latent timely completion as well as component truth.

Add explicit decision-line processes on the frozen structure, separately for
every supported pair and both directions: (G,-D)=(.02,.04),(.04,.02),(.02,.02),
with tolerance 1e-6, in both periods; A above/B on the line AND A on the line/B
above. Above means both components .04. Repeat with different binding components
in A and B. For simultaneous boundary stress also activate every feasible set
of two vertex-disjoint supported pairs; no feasible set may be selected by its
simulated performance. If none exists, record that structural fact; single-edge
cases remain mandatory. Calibrate other pairs so R≤.02 in cases judging false
“changes”; verify this from the full truth vector before simulation. Include
H=.02 cases judging false “survives”, including a line in A with B below and
vice versa. Include small perturbations ±.001 around each boundary and changing
seasonal difficulty. Every required infeasible single-edge calibration blocks
the gate and needs a reviewed amendment, not silent omission.

A false “changes” is a changes verdict when true R≤.02. A false “survives” is
a survives verdict when true H≥.02. Count BOTH at joint-line cases. A true
one-period-only reversal makes “survives” false but need not make an inconclusive
result a failure. Compute R,H both for the failure-imputed truth and for the
latent-completion truth in missingness cases. Envelope coverage and verdict
error checks must cover the latter too. Nominal 95% two-sided simultaneous
coverage alone does not guarantee each directional false-verdict rate ≤2.5%;
these full-rule checks are additional requirements.

Run exactly 1,000 datasets per scenario in selection bank 0, with 5,000
bootstrap draws per dataset. Screen each candidate resampler on the same data
against the validity and power criteria. For bias require abs(mean error) plus
1.96 times its Monte Carlo SE ≤0.002 for EACH G,D component. For coverage,
require the one-sided 95% exact binomial lower bound for full-family coverage
≥0.92. For each applicable false-verdict rate require the one-sided 95% exact
binomial upper bound ≤0.025. Report counts, Monte Carlo SEs and exact intervals;
point estimates alone do not pass. A dataset with invalid intervals counts as
uncovered and as no verdict, not as a discarded replicate. Each dataset must
have ≥4,750 valid joint draws; also require ≥95% of datasets to have valid
intervals. Quality-blocking 1% missingness/invalid-data fixtures are scored on
correct blocking, not coverage or power; none may emit a substantive verdict.

Choose the first passing resampler in the fixed order below. Then test ONLY
that choice on 2,000 fresh datasets per scenario in bank 1 with identical
acceptance criteria and 5,000 draws. This independent validation bank protects
against selecting the luckiest calibration run. If it fails, stop; do not test
the next resampler on that same bank or increase replicates until passing.
These are per-scenario engineering acceptance bounds, not a simultaneous
confidence claim about all possible data-generating processes. Publish every
attempt. No outcomes open until selection and independent validation both pass.
The 0.002 bias tolerance, ≥92% coverage and ≤2.5% error limits remain unchanged;
all gate choices are post-pilot/pre-confirmation. Check q and the whole verdict,
not only marginal rate coverage. Do not bootstrap selected extreme ranks.

Power is a REQUIRED gate, not a report-only diagnostic. Keep all supported pairs
and the complete ≤336-component family, both periods, endpoint envelopes, quality
stops and selected resampling algorithm in every power calculation. Never use
pointwise intervals, a pilot-selected pair alone, or a different critical value.

For every supported ordered pair calibrate repeated alternatives with both
G and -D equal to delta in A and B, delta=.025,.03,.04,.06. Also run (.04,.06)
and (.06,.04) bottlenecks, swapping the bottleneck between periods. Report power
curves for the designated pair's JOINT event Lq_A>.02 AND Lq_B>.02; a discovery
on some easier other pair cannot count toward that pair's power. Report table
power separately. The mandatory design alternative is delta=.04: a true
4-point advantage on each side (an 8-point national-to-matched swing), with a
2-point distance from each decision boundary. Require the one-sided 95% exact
binomial LOWER bound on designated-pair joint power ≥0.80 for every supported
pair/direction in both selection and validation banks, at all the registered
baseline/shock/seasonality settings without missingness and with 0.05% expected
informative missingness. Use all attempted datasets as the denominator. Expected
missingness exactly at the 0.1% quality cutoff is a validity/blocking stress,
not an 80%-power requirement: random shares above that cutoff correctly prevent
a verdict. Report its power, including every blocked dataset, without requiring
it to pass the alternative-power threshold.

For survival, calibrate all G=D=0 in both periods, and separately calibrate
G_ab=D_ab=0.005*(j_a-j_b) for all supported pairs in both periods (sorted carrier
indices j). These are true stable-order cases despite unequal networks; do not
assume additive carrier coefficients alone make national and adjusted orders
agree. Require the same ≥0.80 lower bound on the probability that EVERY ordered
pair has Uq_A<.02 AND Uq_B<.02. Also report, without a pass requirement, survival
power near H=.01 and false survival under A-only/B-only reversals. No claim of
80% power at or arbitrarily close to .02 is possible or intended. The .04 design
alternative and .80 requirement are new post-pilot design standards, not changes
to the substantive .02 decision line. They target a clearly material signal
and a useful chance of settling a true stable table. Simulations report where
power actually reaches 80%; never relabel a larger detectable effect as .04.

The 500-flight/40-week screen cannot establish power. If any required pair,
direction or survival scenario fails, or a required calibration is infeasible,
the full table test is not cleared. Do not drop weak pairs, lower the line,
relax confidence, borrow a pilot effect, or pool B into A. Keep outcomes closed;
a redesigned scope/period/rule needs a new dated reviewed registration and gate.
No power or eligibility result for 2023–2025 is asserted by this document.

Fixed fallback order for validity or power failure with acceptable bias:
independent whole weeks → circular moving blocks of 4 weeks → blocks of 8 weeks.
For block length l, within each year draw ceil(W_y/l) uniform start indices,
take l consecutive week IDs modulo W_y per start, concatenate and truncate to
W_y; multiplicities enter exactly as above. Draw years in ascending order.
In selection bank 0, evaluate candidates on identical synthetic datasets and
use the first passing every validity AND power process. Any bias failure in a
required process or no passing candidate blocks confirmation. Bank 1 validates
only the selected candidate; its failure also blocks confirmation. Keep confirmation outcomes closed until a new amendment is
reviewed, committed and passes. Commit gate code, hashes and report first.

## Robustness, failed outcomes, verification and amendments

Mandatory non-verdict checks alter ONE choice at a time: 1-hour and 4-hour
bands; equal stratum weights; harmonic weights 2*n_a*n_b/(n_a+n_b); arithmetic
mean of separately computed 2023 and 2024 gaps instead of pooling A; each source
year separately; omission of each of five airports. Freeze those airports from
the schedule-only union of records entering any supported pair over 2023–2025,
counting each record once per endpoint, not once per pair; sort by endpoint
count descending, then numeric airport ID. For each omission recompute shared
counts, weights, national G after the SAME airport exclusion, D and coverage.
Show coverage against both the original and retained schedule denominators.

For the ±30-minute sensitivity, within each pair/normalized route/date give each
flight its nearest opposing flight within 30 minutes, across band boundaries;
rank candidates by absolute minute gap, candidate departure minute, then numeric
source-month/row ordinal. Retain only reciprocal choices, in one pass, with
no rematching after removal. Each flight occurs at most once in a pair and each
match has equal weight; D is the arithmetic mean of paired Y differences.
G remains the full national score. Use the original source-year/normalized-week
clusters; never match across source years. Freeze code and schedule support for
all sensitivities before outcome access. Keep the primary pair roster, require
positive denominators, and disclose sensitivity counts/weeks without applying
new count-based pruning. No sensitivity can replace the registered verdict;
contrary results limit wording.

Preregister descriptive secondary rates by carrier/source year and pooled A/B:
known cancellation, known diversion, their union, each missing-status flag,
U=1 indeterminate outcomes, invalid/missing schedule keys, and flights outside
the union of all frozen supported-pair strata. Denominator is all reported
scheduled flights in that carrier/period, with explicit numerator counts.
For each supported pair report both carrier-specific national rates and the
same w_s-weighted shared-cell rates for cancellation, diversion and U; all
scheduled flights within the respective national/shared population remain in
the denominator. Define pair-unsupported as no valid shared stratum with that
specific counterpart, independently of whether another supported counterpart
exists. Report success/failure counts and rates on each excluded population;
unknown rows remain failures in its primary success rate, with bounds shown.

Secondary endpoints, decompositions and sensitivities carry point estimates
and descriptive ranges only; no significance labels, winner declarations or
additional hypothesis-test claims. The common week draws may describe their
variability but only the registered G,D family can determine the verdict.
An unavailable denominator is reported as unavailable, never as zero.
For each G,D include missingness endpoints (a's unknowns fail/b's succeed,
and the reverse) in θ; a known cancellation/diversion can never become success.
Use the smallest lower and largest upper bound over primary/endpoints for each
gap in the verdict. Show all-fail/all-success rates too; no favorable imputation selection.
Schedule-unmatchable flights cannot be assigned a fair score; report their
national outcomes and excluded exposure separately. Never silently drop failures.

Decomposition, descriptive only: for each eligible pair form R from each
carrier's flight-weighted Y on that pair's shared support before common weighting.
Report G−D=(G−R)+(R−D): restriction plus reweighting, not percent caused by network.
Freeze AS–NK as a pilot-motivated best–worst example; if ineligible, report unavailable.
Do not select new extremes for a confirmatory “gap explained” claim. No common-clock
score or schedule-padding verdict is part of this simplified registration.

Show all pairs before choosing examples; choose the illustrative route by maximum
shared scheduled count, ties by airport IDs. Highlight WN–UA as pilot-motivated,
whether it repeats or fails. Publish a pair matrix with unsupported cells and
uncertain comparisons; any optional additive network index is descriptive only.
Companion-page window/weight toggles are sensitivity displays, not new verdicts.

Before filming: independent source/ID checks, boundary/status fixtures, verification
of weights and all denominators, annual published-table reconciliation, independent
numerical re-derivation, methods review and byte-identical fresh reproduction.
Every script number cites a result key; record planned versus passing checks.
Registration amendments: simplified own-schedule endpoint; national all-scheduled
baseline; direct pairs instead of a league index; retired 2019/40% requirements;
symmetric two-period interval rule and simulation gate. All are disclosed after
2015 exploration. The dated review changes below are also post-pilot. No registration commit or
confirmation gate is asserted; owner approval and all pre-access seals are pending.


## Changes after the methods review — 2026-10-06

All twelve changes below were made AFTER the reviewer saw the 2015 pilot
results and earlier design/red-team notes, and BEFORE this review accessed any
2019 or 2023–2025 flight records. The earlier incidental 2024-ranking snippet
is disclosed above; do not claim perfect ignorance of public rankings. No
confirmation support audit, calibration, simulation or power gate was executed
in this review. The original 2026-10-05 draft remains unchanged.

- **C01 — Define the two verdict targets and the limits of replication.** Post-pilot change; exact specification is in the body and the paired review.
- **C02 — Seal support and exposure before any confirmation outcome is decoded.** Post-pilot change; exact specification is in the body and the paired review.
- **C03 — Make missing status and missing timing deterministic.** Post-pilot change; exact specification is in the body and the paired review.
- **C04 — Align matching dates, eligibility weeks and bootstrap clusters.** Post-pilot change; exact specification is in the body and the paired review.
- **C05 — Pin the production and simulation bootstrap implementation.** Post-pilot change; exact specification is in the body and the paired review.
- **C06 — Freeze a complete synthetic generator suite before running it.** Post-pilot change; exact specification is in the body and the paired review.
- **C07 — Strengthen boundary cases and make gate error labels correct.** Post-pilot change; exact specification is in the body and the paired review.
- **C08 — Account for Monte Carlo uncertainty and fallback selection.** Post-pilot change; exact specification is in the body and the paired review.
- **C09 — Require power for the complete simultaneous two-period verdict.** Post-pilot change; exact specification is in the body and the paired review.
- **C10 — Specify secondary endpoints and multiplicity boundaries.** Post-pilot change; exact specification is in the body and the paired review.
- **C11 — Remove remaining sensitivity-selection ambiguities.** Post-pilot change; exact specification is in the body and the paired review.
- **C12 — Document source verification, rights and review timing.** Post-pilot change; exact specification is in the body and the paired review.

The 2-point decision line, eight candidates, periods, direct pair weighting
and conservative two-period decision regions are retained. New 4-point design
alternatives, 80% power requirements, Monte Carlo acceptance rules and staged
seals are post-pilot standards, not retroactive passes. Count/coverage minima
remain post-pilot inherited screens and must not be advertised as power proof.
Approval of this text approves the plan only; confirmation access depends on
committed outcome-blind support and independently validated gate artifacts.
