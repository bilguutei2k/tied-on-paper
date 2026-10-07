We still ask whether United beats Southwest by more than two points on comparable flights.
Amendment 2 changes only how the uncertainty interval is constructed.
It was designed after seeing Amendment 1's synthetic failure, after two failed outcome-blind gates.
No confirmation outcome has been read; this amendment comes before any confirmation outcome.
One 28-day studentized bootstrap method will face fresh selection and independent validation.
Confirmation stays closed until the gate passes and the owner approves; another failure ends this task.

# Amendment 2 — studentized whole-network block interval

Status at specification: unevaluated. This is a disclosed post-simulation redesign,
not a retroactive pass of either previous gate. The sealed Amendment 1 design was
`e5c9a33`; its failure report was `6bc20d7`. The owner authorized this interval-only
amendment and synthetic validation. Bank 0 has informed its design and provides
**no acceptance evidence** for Amendment 2. No Amendment 3 is authorized here.

## Retained contract

All of Amendment 1's scope, estimand, support, scoring, missingness assignments,
weights, quality cutoffs, sensitivities, periods, claims and symmetric decisions
remain unchanged. UA minus WN is the only comparison. The line is +0.02. A pools
2023–2024; B is the independent-labeled 2025 replication. Whole-network physical
calendar dates are resampled within source year. All cells, source-year memberships,
counts and denominator weights are frozen. No rematching or flight resampling.
The lower/upper envelope across primary, lower and upper missingness assignments
controls decisions: L>.02 challenges, U<.02 survives this materiality test, otherwise
inconclusive. Quality failure is inconclusive. Survival does not establish WN
superiority, and no causal or future-network claim is added.

The generator and scenario manifest are unchanged byte-for-byte at the function/
manifest level, as checked by `check_interval.py`. `structure.json`, `truths.json`
and inherited `fixtures.json` are exact copies. All 20 scenarios remain, 19 required;
scenario 19 at (.03,.03) reports local power without an acceptance requirement.

## Diagnosis, independently checked before specification

`diagnose.py` reads only saved Amendment 1 synthetic JSONL records. At scenario 9,
28-day empirical SD / mean bootstrap SD is 1.0436 (A), 1.0602 (B); estimate skew
is -0.1654/-0.0868; estimate/half-width correlation is -0.3211/-0.2754. False above
versus below counts are 15/3 and 20/6. Seven days gives SD ratios 1.0902/1.1059;
one day gives 1.4859/1.5029, a small correction to the quoted single 1.49 figure.
The nonserial boundary ratios are about 1.03–1.08. Correlations are mostly near
zero, though differential_daily A is -0.1206. Claude's diagnosis is substantially
confirmed: dependence is captured reasonably on average with 28 days, but a high
estimated UA lead tends to accompany a narrow estimated interval. That mechanism
is consistent with the saved records; those correlations alone do not prove causation.

## One primary method, no fallback

Use a nominal 99% **studentized circular moving-block interval with 28-day blocks**,
analytic linearized block SEs, finite-window variance correction, and a Student-t
critical-value floor. Keep exactly 1,999 draws. No alternative is selected after
seeing bank 2 or bank 1. Studentization lets the bootstrap distribution reflect
the association between estimate and its estimated precision. A simple widening
of the old normal interval would not model that association. The t floor prevents
an accidentally light bootstrap tail from making the short 2025 series overprecise.

Independent resampled block contributions can provide a per-draw variance without
a second bootstrap. This follows the blockwise studentization rationale described
by [Gonçalves and White](https://www.ms.uky.edu/~mai/sta662/linearRegBoot.pdf).
That literature motivates the construction, not a theorem certifying this particular
finite-schedule ratio and correction. The whole registered empirical gate remains
necessary. The correction and floor are fixed engineering conservatism; the gate
must also verify that required power survives them.

## Exact algorithm (LESSONS 6)

For each assignment k, let N_ydk be its weighted daily contrast numerator and W_yd
its daily denominator. Include zero-support dates. Years process in order 2023,
2024, 2025, and assignments remain primary, lower, upper. Let T_y be days in a year,
L=28, q_y=floor(T_y/L), r_y=T_y-q_y L. Actual T are 365,366,365, so q=13 each and
r=1,2,1. D_tk is the original ratio of summed N to summed W over period t.

For each start s=0,...,T_y-1 precompute circular sums F_N(s),F_W(s) over L days
and H_N(s),H_W(s) over r_y days. Starts wrap modulo T_y and never cross the
source-year boundary. These sums are deterministic, not additional bootstrap draws.
For each year draw a 1999 × (q_y+1) matrix of uniform integer starts in [0,T_y),
row-major draw/start order. The first q starts supply full blocks; the last supplies
the r-day prefix. This is exactly the previous 28-day concatenate-and-truncate
resampling distribution and random draw order. Every date occurrence carries the
same multiplicity across all routes, airports, carriers and assignments. Sum sampled
numerators and denominators over the relevant years and divide to obtain D*_btk.

For the original SE, separately within year form full residual block totals
F_N(s)-D_tk F_W(s) and short totals H_N(s)-D_tk H_W(s). Write V_F and V_H for their
population variances across all T circular starts (ddof=0, subtracting their own
source-year means). Then

    SE_tk² = sum_y [q_y V_F T_y/(T_y-L) + V_H T_y/(T_y-r_y)] / W_t².

The finite-window factors correct the leading loss from centering overlapping
block sums; under constant-weight independent days the factor is exact for that
variance loss. It is approximate for dependent heterogeneous data. They are not
estimated from bank-0 performance and introduce no fitted multiplier.

For each draw, form full-block residuals F_N(s_bj)-D*_btk F_W(s_bj), j=1,...,q_y.
Also form short-prefix residuals H_N(s_bj)-D*_btk H_W(s_bj) at those same q starts.
Use the sample variance of each set (ddof=1, centered separately within source year).
The q sampled starts are independent, and their prefixes estimate the variance of
the separately drawn final short block. They require no new random draws. Set

    SE*_btk² = sum_y [q_y sample_var(full residuals) + sample_var(prefix residuals)]
               / (sampled total W_bt)².

The per-draw variance is an analytic cluster/block delta-method SE; no nested
bootstrap, airport resampling or variance smoothing is used. The prefix covariance
with the full-block variance estimate does not add a covariance term to the target
variance: the actual final short block has an independently drawn start.

Compute Z*_btk=(D*_btk-D_tk)/SE*_btk. Obtain its .005 and .995 quantiles using NumPy
`quantile(method='linear')`: sorted index (1999-1)p, linearly interpolated between
adjacent order statistics. Let nu_t=sum_y(q_y-1): 24 for A, 12 for B. Let
c_t=StudentT(nu_t).ppf(.995). Define Q_plus=max(Q_.995,c_t),
Q_minus=min(Q_.005,-c_t). The assignment interval is

    [D_tk - Q_plus SE_tk, D_tk - Q_minus SE_tk].

Take the minimum lower and maximum upper over the three assignments. Do not clip.
The df counts full independent bootstrap blocks minus one centering degree per
year; they are a conservative floor convention, not exact population degrees of
freedom. All 1,999 draw denominators and all original/per-draw SEs must be finite
and positive. Otherwise the entire dataset's interval is invalid, both decisions
inconclusive, coverage and power counted false. There is no invalid-draw deletion.

## Fresh gate and fixed stop rules

Retain PCG64(SeedSequence([20261007,bank,scenario,replicate,stream])). Streams 0,1,2
and all generator operations are unchanged; stream 3 supplies bootstrap starts.
Replicates start at zero. **Bank 2** is fresh selection, exactly 1,000 datasets per
attempted scenario; bank 1 is independent validation, exactly 2,000 per scenario.
Bank 0 cannot be reused as evidence. Bank 90 is timing-only: ten datasets with ten
workers, no acceptance summaries inspected. Use ten workers, each numerical library
limited to one thread. Benchmark after the design/code commit and before bank 2.

Attempt scenarios in the original order 0–19. A failed complete mandatory scenario
stops the sole candidate immediately; all later scenarios and validation are UNRUN.
Bias failure stops globally. If all 19 required selection scenarios pass, finish
local scenario 19 and validate only this method on bank 1 in the same order. A
validation failure stops immediately. No extra replicates, fallback, changed line,
changed effects, relaxed thresholds or Amendment 3 follows failure. Partial runs
resume saved contiguous replicate IDs without overwriting completed records.

Unchanged criteria: for each of six estimates, |mean bias|+1.96 MCSE <= .002;
one-sided 95% exact-binomial lower coverage >= .92 per period and jointly; each
applicable false-direction upper <= .025, with both directions checked at the line;
valid interval fraction >= .95. At 0/.04, one-sided exact lower power >= .80 per
period and for same-direction replication when both effects agree. All datasets
remain denominators. Scenario 19 reports local three-point power, without requiring
80%. These are per-scenario simulation certification rules, not universal guarantees.

## Seals, verification and disclosure

Commit this document, design, code, frozen manifests, diagnosis, deterministic
preflight, verification code and seal before any new synthetic dataset, including
the benchmark. `run_gate.py` checks hashes against committed bytes before running.
The process audit hook denies mixed raw-file access and network; the schedule loader
checks the input hash, outcome-free schema and projected seven schedule columns.
No production weights or confirmation outcome arrays are created here.

Deterministic preflight reconstructs circular sums and integer multiplicities,
original and per-draw SEs, interpolated quantiles and floor inversion independently.
It also verifies unchanged generator, estimator, decisions and acceptance functions.
Post-gate verification independently recomputes events, bias, exact binomial bounds,
early stops and original-replicate replays. Replays provide no additional evidence.
Record results below and in GATE.md/results.json, update progress and deviations,
and make the report checkpoint. A passing gate still requires owner approval and
the later production-code/resampling-array seals before any confirmation outcome.
