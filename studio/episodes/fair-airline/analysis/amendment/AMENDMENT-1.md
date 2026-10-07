The amended question is whether United beats Southwest by more than two points on comparable flights.
Southwest led the published 2015 table; this tests whether that ordering misses a material United advantage.
The same carriers, frozen routes, cells and 2015 exploration year are retained, with no secondary pairs.
The primary comparison is 2023–2024, with 2025 as a separate replication; cancellations and diversions fail.
The amended gate FAILED: all three day/block methods exceeded the allowed boundary-error upper bound.
Confirmation outcomes remain unopened; a further reviewed amendment and passing gate are required.

# Amendment 1 — focused United–Southwest comparison

Status: evaluated draft, amendment gate **FAIL**, after failed gate `153fd1b`, before any
confirmation flight outcome is decoded. The owner authorized drafting and
validation, not outcome access. Written 2026-10-07 UTC (2026-10-06 Pacific).
The registered METHOD remains unchanged. This amendment is post-pilot and
post-failed-simulation; it is not a retroactive pass of that registration.
Prior incidental public-ranking exposure disclosed in METHOD remains disclosed.

## Scope and belief

The published 2015 DOT annual table put Southwest at 79.7% and United at 78.2%
(the supplied red-team, printed table 1A). The all-scheduled pilot difference
was 1.56 points for WN. Thus the motivating belief is that this ordering is
useful when both carriers serve a trip. We test its narrower, material implication:
**using the WN-over-UA ordering does not overlook a UA advantage exceeding two
percentage points on comparable scheduled flights.** We do not assume the
2023–2025 published ordering, which remains unread. Its later reconciliation
will be descriptive and cannot choose, reverse or replace this contrast.

Primary pair, fixed now: UA minus WN. No secondary pairs are added: the pilot's
UA–WN comparison directly addresses the question, and a second pair would add
no necessary evidence for its verdict. The eight frozen operators and all
original schedule, route and support artifacts stay intact. Only the inferential
family is narrowed; no route, cell or service is selected by an outcome.
We supersede the 28-pair G/D family, extreme-rank rules, four-carrier verdict
condition and their simulation Cartesian product. The two-period primary direct
contrast replaces them. Old all-pair matrices, AS–NK examples and all-pair
sensitivity obligations are retired; they cannot return as confirmatory tests.

For each shared directional route × normalized scheduled date × two-hour window,
retain the original n_UA,s, n_WN,s and w_s=(n_UA,s+n_WN,s)/2. Source-year membership,
2400 normalization, airport identities, eligibility, flight records and matching
are exactly those sealed in `coverage.json`. Do not merge reciprocal routes or
other airports, add regionals or create a common population across carriers.
D_t = sum_s w_s(mean Y_UA,s − mean Y_WN,s) / sum_s w_s.
A pools 2023 and 2024 counts and weights; B is 2025, on its own frozen basket.
2015 remains exploration. Frozen structure hashes and counts are in `structure.json`.

Y=1 only for a known noncancelled, nondiverted flight arriving strictly less than
15 minutes late against its own published arrival time. A known cancellation or
diversion overrides other missing fields and is a failure. Exactly 15 is failure.
Indeterminate outcomes fail in the primary estimate and have U=1. Nonbinary status,
invalid nonmissing delay, unresolved source duplicates or identity errors stop.
For each contrast calculate D_low=D−weighted U_WN and D_high=D+weighted U_UA;
known failures cannot become successes. The interval envelope over these three
assignments governs decisions. Original national source-year key/unknown limits
remain for UA and WN (each ≤0.1%); also require each carrier's unknown share on
matched support in each year ≤0.1%. Other six carriers remain the frozen source
roster, with descriptive support; they cannot block or change this pair's verdict.

This is adjusted timetable-promise performance on overlapping services, not a
causal airline-choice effect, common-clock speed, passenger-weighted reliability,
or a best-airline ranking. Arrival buffers, within-window timing, fleet, staffing,
rotations and network choices remain bundled. Preserve descriptive UA/WN national
and unmatched rates, cancellation/diversion/unknown rates, annual estimates and
UA/WN-only original window/weight/airport-omission sensitivities. None changes the
primary verdict. No third-party snapshots or row-level data enter public history.

## One line, symmetric decisions, timing

The substantive line is D=+0.02: one additional timely completion per 50 scheduled
flights for UA over WN on the shared basket. This preserves the original scale;
it is neither lowered to fit WN's 1.56-point pilot lead nor required on an additional
national contrast. The line's new single-pair use, family reduction and rule are
chosen after the pilot and failed gate, before confirmation. For each period:

* L>0.02: material counterexample to using the published ordering ("challenged").
* U<0.02: no UA advantage as large as two points ("survives this materiality test").
* Otherwise, including equality or a quality failure: inconclusive.

The whole interval is compared with the **same** line in both directions. Survival
is not evidence that WN is better, equivalent or causally preferable. A precisely
estimated one-point UA lead can survive this narrower practical test; show it.
A's result is the primary result. B is a separately labeled replication. Only the
same decisive label in both periods permits "replicated"; mixed labels or one
inconclusive period leave the replication unsettled. B cannot rewrite A or choose
a new pair. Gate power below concerns both the per-period and repeated decisions.

## Exact uncertainty algorithm and fixed fallback

Use the first passing candidate in this order: **1 calendar day → 7 consecutive
calendar days → 28 consecutive calendar days**. The latter are one-/four-week
moving blocks of days, not independently sampled airport days. Sampling airports
independently would break the network-wide daily shock and is intentionally excluded.

For each source year sort all calendar dates spanning its normalized shared dates,
including any date with zero shared weight. Keep source-year boundary memberships;
shocks in simulations remain continuous across physical year boundaries. In year
order 2023, 2024, 2025 and then bootstrap draw order, use PCG64 with the stream
below. For length 1 draw T uniform integer indices in [0,T). For length l draw
ceil(T/l) starts, append l consecutive indices modulo T from each start, concatenate
and truncate to T. NumPy generates the complete matrix in row-major draw/start
order. Every occurrence assigns the **same multiplicity to the entire network**
on that date, across both carriers, all routes, airports and missingness assignments.
Do not rematch, select cells or resample flights. Within-cell means stay fixed.
Recompute D* using multiplicity×w_s in numerator and denominator; pool sampled
2023/2024 contributions for A. B uses its own year's draws.

Use 1,999 draws in simulation and eventual production. For each of the three
endpoint assignments compute sample SD of D* (ddof=1); report original D ±
2.5758293035489004×SD. This is a **nominal 99% normal bootstrap-SD interval**, not
a percentile or guaranteed exact interval. The fixed conservative critical value
allows headroom for the empirical directional-error gate; it is fixed before
synthetic evaluation. Take the minimum lower and maximum upper across assignments.
All 1,999 draws must have finite positive denominators, and each SD must be positive;
otherwise no verdict, counted as uncovered and powerless. Do not clip intervals.
The fixed-schedule target integrates repeated outcomes and calendar shocks on
these services. Bootstrap schedule variation is an approximation requiring this gate,
not sampling error in the observed historical census or a future-network guarantee.

## Sealed simulation gate

`design.json`, `run_gate.py`, `structure.json`, `truths.json`, `fixtures.json` and
this draft are checkpointed before the first synthetic dataset. Code reads only
the hash-verified schedule derivative through a Python file object, verifies its
outcome-free schema and projects seven schedule columns. The inherited process
audit hook denies raw-file opens and network connections; this is not a kernel
sandbox claim. No full mixed raw ZIP or contemporary ranking is opened.

The real UA–WN cells and counts are retained exactly. Let base_s=.80 + .05 sine
seasonality + route/time SHA256 heterogeneity ±.03. Add centered route heterogeneity
h_s=heterogeneity/3, centered by w separately in A and B. Set marginal probabilities
p_UA=base+(delta_t+h_s)/2 and p_WN=base−(delta_t+h_s)/2. This calibrates D=delta_t
analytically; require residual <1e-12, and probabilities strictly between .05 and .99.
There is no outcome fitting, clipping or numerical optimization to a realized dataset.

Flight probit latent value is mu_cs + a_c network_day + b_c(origin_day+destination_day)
+ independent N(0,1). Independent stationary Gaussian network and airport series
have SD .30 when active; one airport series is shared between origin and destination.
Set mu_cs=sqrt(1+.30²(a_c²+2b_c²)) Phi^-1(p_cs), or Phi^-1(p_cs) when SD=0.
Thus marginal p is exact even under differing carrier shock vulnerability. Airport
IDs sort numerically; dates are physically continuous, including across years.
Start AR(1) stationary; subsequent innovations have SD .30 sqrt(1−rho²).
Profiles: independent flights; shared daily shocks with all loadings 1; differential
daily shocks with (a_UA,b_UA)=(1,1), (a_WN,b_WN)=(.5,.75); those differential
shocks with rho=.6; and the serial profile with informative unknown outcomes.
Daily network and airport shocks are active together in all four shock profiles.

Conditional on shocks, generate exact binomial timely counts at each carrier/cell;
this is distributionally identical to individual independent probit innovations,
without discarding any flight count. Cells sort source year/date/origin/destination/
band, carrier UA then WN. Among timely counts, independently mark unknown with
probability .0005/p_cs for the missingness profile (zero elsewhere). Assign latent
failures cancellation/diversion/late with probabilities .25/.05/.70 using sequential
binomials. Known timely/late delays are 0/20; unknown completed timing is blank.
The code reconstructs scored success from those status counts. Primary truth is
delta, lower/upper assignment truths delta−.0005 and delta+.0005. Latent truth is
delta. Nonmatched records have no unknowns in these synthetic processes and do not
enter D. This validates the specified missingness stress, not arbitrary masking.

All five profiles run delta_A=delta_B in {0,.02,.04}. Additional serial profiles
run (.02,.04),(.04,.02),(0,.04),(.04,0), and descriptive (.03,.03). The exact
20-scenario manifest/truths includes all coefficients; 19 scenarios are mandatory.
No selective pruning. Both false directions are checked at the calibrated .02
boundary, separately for A and B, including mixed-boundary cases. At other truths
check the applicable false direction. Check coverage of all endpoint truths and
the latent truth in each period and jointly. Since decisions use conservative
envelopes, unknown outcomes cannot create an easier verdict.

Stream=PCG64(SeedSequence([20261007,bank,scenario,replicate,stream])). Bank 0 is
selection, bank 1 independent validation, bank 90 timing only; replicate starts 0.
Streams: 0 network then airport Gaussian shocks (entity/date order); 1 timely counts;
2 unknown then cancellation then diversion counts; 3 bootstrap indices, resetting
identically for each candidate. No changing outcomes between candidates.

Exactly 1,000 datasets per attempted selection scenario, 2,000 for validation,
1,999 draws each. Require |mean error|+1.96 MCSE≤.002 for all six endpoint/period
estimates; one-sided 95% exact binomial lower coverage ≥.92 (each period and joint);
each applicable directional false-verdict one-sided 95% exact upper ≤.025; valid
interval fraction ≥.95. At delta=0 and .04 require exact lower power ≥.80 per
period and for the repeated same-direction decision. All datasets are denominators.
The .03 case reports local power without a pass claim. These are per-scenario
engineering bounds, not simultaneous confidence statements over all conceivable DGPs.

The pilot's saved `se_own` is .00520275, point .02953075, simultaneous interval
[.01294650,.04611500]. A .04 UA advantage is 2.01 pilot SE above its point estimate,
inside its simultaneous interval: a plausible but optimistic effect, not its observed
value. Zero is the symmetric power alternative two points below the decision line.
We cannot promise 80% power at the line or at the pilot's exact effect. Report .03
power to expose that limitation; never substitute a larger effect after evaluation.

Use ten worker threads with numerical libraries at one thread each. First benchmark
10 disjoint bank-90 datasets/candidate, reporting runtime only, not acceptance or
power; then run the committed suite. Candidate failure at the first complete mandatory
scenario stops that candidate; later scenarios are explicitly unrun. Bias failure
stops all candidates. Choose the first candidate passing every mandatory selection
scenario, then test only it on fresh bank 1. Validation failure stops, without another
fallback, threshold change or sample-size increase. Save dataset records and exact
bounds. A gate pass never grants outcome access.

## Results and remaining approval barrier

**FAIL — no candidate clears selection.** The pre-simulation design/code checkpoint
was `e5c9a33`. All three candidates completed selection scenarios 0–9 with exactly
1,000 datasets per scenario and 1,999 bootstrap draws. Each failed required scenario
9: the calibrated two-point boundary in both periods with network-wide and airport
shocks, unequal carrier loadings, and AR(1)=.6. The fixed fallback order was exhausted.

| Whole-network resampling | Joint coverage (exact lower) | Worst directional error (exact upper) | Boundary result |
|---|---:|---:|---|
| 1 day | 82.7% (80.612%) | 5.6% (6.947%) | Coverage and error fail |
| 7 days | 95.2% (93.935%) | 2.3% (3.243%) | Error bound fails |
| 28 days | 95.7% (94.490%) | 2.0% (2.893%) | Error bound fails |

Bounds are one-sided 95% exact binomial bounds. The worst directional error is a
false challenge in 2025 at the true decision line. For 28 days its count is 20/1,000:
the observed 2.0% is below 2.5%, but its upper bound is not. This fails the sealed
certification rule; it is not proof that the population error rate exceeds 2.5%.
No extra replicates, threshold relaxation, new candidate or scenario deletion follows.

Across all completed attempts, the largest absolute mean-bias-plus-1.96-MCSE bound
is 0.0281 percentage points, below the allowed 0.2; every dataset has valid intervals.
The completed no-serial-shock power alternatives at zero/four points achieved
100% per-period and repeated-decision power (exact lower 99.701%). **The full power
gate is NOT COMPLETED:** serial-shock power, informative missingness, mixed-period
and local three-point scenarios 10–19 are unrun. Independent bank 1 is NOT RUN.
Those omissions are the registered early stop, never evidence of a pass.

There are 10,000 distinct simulated datasets reused across three candidates,
30,000 dataset-candidate evaluations and 59,970,000 joint bootstrap draws.
Ten-worker timing batches, run before evaluation, took 0.2433/0.2460/0.2133 seconds
for 1/7/28 days respectively; individual complete selection scenarios took about
18.5–26.4 seconds. The usage-limit continuation preserved all complete scenarios and
the first 700 records of candidate 28/scenario 2 byte-for-byte, completing only its
remaining 300 with the sealed functions. That scenario's runtime covers only the
resumed portion. No generator, interval, seed, sample size or acceptance rule changed.

`verify.py` independently confirms all 258 exact-binomial interval checks by tail inversion,
bias arithmetic with compensated sums, event counts, acceptance decisions, strict
boundary/status fixtures, frozen membership counts, bootstrap multiplicity algorithms,
and early-stop order. All 30 original-replicate-zero replays agree exactly. Replays
are verification, not new evaluation datasets. See `GATE.md`, `results.json`,
`verification.json`, `summary.json`, `timing.json` and `artifact-hashes.json`.

The original registered gate remains failed; this narrowed amendment also does
not clear confirmation. Commit this investigation through the helper, record its
hash in PROGRESS.md, and stop. A further outcome-blind redesign needs owner review,
a new seal and a passing gate. Before any later outcome access, owner approval and
the accepted amendment, production analysis code and production resampling arrays
must be committed; seal A before opening B. No observed confirmation verdict exists.
