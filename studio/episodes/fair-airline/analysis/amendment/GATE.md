# Amendment 1 — pre-confirmation gate results

**FAIL**. Selected block length: none. Confirmation outcomes remain unopened.

The pre-simulation design/code checkpoint was `e5c9a33`. The registered
algorithm, candidates, scenarios, sample sizes and criteria were unchanged during
evaluation. Nominal intervals are 99% bootstrap-SD intervals; gate acceptance
uses one-sided 95% exact Monte Carlo bounds. Bias values below are percentage points.

| Bank | Candidate | Scenario/profile | D_A / D_B (pp) | Bias bound max (pp) | Joint coverage % [lower] | Max false-direction upper % | Min required power lower % | Pass |
|---|---:|---|---|---:|---|---:|---:|---|
| 0 | 1 | 0: independent | 2 / 2 | 0.0134 | 97.40 [96.41] | 1.57 | — | True |
| 0 | 1 | 1: independent | 0 / 0 | 0.0137 | 97.80 [96.87] | 0.30 | 99.70 | True |
| 0 | 1 | 2: independent | 4 / 4 | 0.0169 | 99.00 [98.31] | 0.30 | 99.70 | True |
| 0 | 1 | 3: shared_daily | 2 / 2 | 0.0202 | 98.00 [97.11] | 1.31 | — | True |
| 0 | 1 | 4: shared_daily | 0 / 0 | 0.0245 | 98.00 [97.11] | 0.30 | 99.70 | True |
| 0 | 1 | 5: shared_daily | 4 / 4 | 0.0233 | 98.50 [97.70] | 0.30 | 99.70 | True |
| 0 | 1 | 6: differential_daily | 2 / 2 | 0.0240 | 98.60 [97.82] | 1.05 | — | True |
| 0 | 1 | 7: differential_daily | 0 / 0 | 0.0179 | 98.60 [97.82] | 0.30 | 99.70 | True |
| 0 | 1 | 8: differential_daily | 4 / 4 | 0.0200 | 97.80 [96.87] | 0.30 | 99.70 | True |
| 0 | 1 | 9: serial_daily | 2 / 2 | 0.0281 | 82.70 [80.61] | 6.95 | — | False |
| 0 | 7 | 0: independent | 2 / 2 | 0.0134 | 96.90 [95.84] | 1.69 | — | True |
| 0 | 7 | 1: independent | 0 / 0 | 0.0137 | 97.90 [96.99] | 0.30 | 99.70 | True |
| 0 | 7 | 2: independent | 4 / 4 | 0.0169 | 97.80 [96.87] | 0.30 | 99.70 | True |
| 0 | 7 | 3: shared_daily | 2 / 2 | 0.0202 | 97.30 [96.30] | 1.44 | — | True |
| 0 | 7 | 4: shared_daily | 0 / 0 | 0.0245 | 97.10 [96.07] | 0.30 | 99.70 | True |
| 0 | 7 | 5: shared_daily | 4 / 4 | 0.0233 | 97.90 [96.99] | 0.30 | 99.70 | True |
| 0 | 7 | 6: differential_daily | 2 / 2 | 0.0240 | 98.10 [97.22] | 1.18 | — | True |
| 0 | 7 | 7: differential_daily | 0 / 0 | 0.0179 | 98.50 [97.70] | 0.30 | 99.70 | True |
| 0 | 7 | 8: differential_daily | 4 / 4 | 0.0200 | 97.10 [96.07] | 0.30 | 99.70 | True |
| 0 | 7 | 9: serial_daily | 2 / 2 | 0.0281 | 95.20 [93.93] | 3.24 | — | False |
| 0 | 28 | 0: independent | 2 / 2 | 0.0134 | 95.90 [94.71] | 2.06 | — | True |
| 0 | 28 | 1: independent | 0 / 0 | 0.0137 | 95.50 [94.27] | 0.30 | 99.70 | True |
| 0 | 28 | 2: independent | 4 / 4 | 0.0169 | 96.80 [95.73] | 0.30 | 99.70 | True |
| 0 | 28 | 3: shared_daily | 2 / 2 | 0.0202 | 96.20 [95.05] | 2.18 | — | True |
| 0 | 28 | 4: shared_daily | 0 / 0 | 0.0245 | 96.00 [94.82] | 0.30 | 99.70 | True |
| 0 | 28 | 5: shared_daily | 4 / 4 | 0.0233 | 96.30 [95.16] | 0.30 | 99.70 | True |
| 0 | 28 | 6: differential_daily | 2 / 2 | 0.0240 | 96.80 [95.73] | 1.69 | — | True |
| 0 | 28 | 7: differential_daily | 0 / 0 | 0.0179 | 97.10 [96.07] | 0.30 | 99.70 | True |
| 0 | 28 | 8: differential_daily | 4 / 4 | 0.0200 | 95.20 [93.93] | 0.30 | 99.70 | True |
| 0 | 28 | 9: serial_daily | 2 / 2 | 0.0281 | 95.70 [94.49] | 2.89 | — | False |

## Selection and limits

- 1-day candidate: stopped at scenario 9; subsequent scenarios UNRUN. 10,000 selection datasets.
- 7-day candidate: stopped at scenario 9; subsequent scenarios UNRUN. 10,000 selection datasets.
- 28-day candidate: stopped at scenario 9; subsequent scenarios UNRUN. 10,000 selection datasets.
- Independent validation: NOT RUN; no candidate cleared selection. No validation pass or failure is inferred.
- Serial-shock power, informative-missingness scenarios, mixed-period effects and local three-point power remain UNRUN after the mandatory boundary stop; the full power gate is NOT COMPLETED.

The retained materiality line is two points. Four points is an optimistic but
pilot-compatible design effect (pilot point 2.953 points, SE 0.520 points); it
does not guarantee useful power for a smaller effect. Survival only excludes
a material UA advantage under this rule, and does not establish WN superiority.
All validation applies to the specified fixed-schedule shock/missingness processes,
not to arbitrary dependence or a different route network. The inherited original
28-pair gate remains failed. No observed confirmation verdict has been produced.

## Verification and timing

Independent verifier passed 258 exact-binomial interval checks by tail inversion, compensated-sum bias calculations, all 30 original-replicate replays, frozen membership counts, status/cutoff fixtures and all three bootstrap multiplicity algorithms.

Benchmark: ten datasets per candidate, ten workers, 0.21–0.25 seconds per batch.
Every worker uses one numerical-library thread. Runtime details are in timing.json
and per-scenario results.json. Replayed records are not additional evaluation datasets.
The usage-limit continuation preserved the first 700 records of selection
candidate 28/scenario 2 byte-for-byte and completed only its remaining 300.
Its saved runtime covers the resumed portion only; all other scenario times are complete.

A failed gate cannot authorize confirmation. A further reviewed outcome-blind
amendment, new seal and passing gate are required; owner adoption and the later
production-code/resampling-array seal must precede confirmation outcome access.
This investigation ends at the report checkpoint.
