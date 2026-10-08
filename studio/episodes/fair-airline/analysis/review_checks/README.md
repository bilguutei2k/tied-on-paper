# Astra review checks — POST-HOC, NOT REGISTERED

These checks were designed after the confirmatory findings were known, on 2026-10-07. They assess implementation and threats to interpretation. They do not change the registered estimand, support, weights, intervals, acceptance rule or replication decision. No production code or source data is changed.

From the repository root:

```sh
ideation/.venv/bin/python studio/episodes/fair-airline/analysis/review_checks/review_checks.py
ideation/.venv/bin/python studio/episodes/fair-airline/analysis/review_checks/audit_evidence.py
```

The first command streams selected CSV columns from 36 hash-verified monthly ZIPs using ten workers with single-thread numerical libraries. It retains UA/WN records for raw scoring and schedule checks, then only matched rows for descriptive calculations. It reads existing exposed 2015 pilot Parquets for the historical comparison. It never fetches flight data, imports production analysis functions, runs the pilot entry point, or writes under data/. Reruns overwrite these aggregate review outputs and update their timestamps. The second command verifies current seals/input/report hashes and annual raw counts, and saves git provenance. Dependencies are those in the supplied `ideation/.venv` (NumPy, pandas, PyArrow, SciPy); production pins are in `analysis/confirm/resampling.json`.

## Files

| File | Contents |
|---|---|
| `results.json` | A/B and 2015 matched summaries; scheduled/actual duration means; common-clock and departure metrics; exact failure decomposition; route-removal and historical-composition checks; independent registered interval reproduction and descriptive added intervals |
| `raw_audit.json` | Per-month archive hashes, source and UA/WN counts, scoring/schedule equality, duplicates, midnight boundaries, elapsed-time identity discrepancies, national counts |
| `integrity.json` | Historical pre-outcome/repaired seal verification, exact start-array regeneration, A/B first-open and seal times, current results identical to original seal commits |
| `evidence.json` | Current input/code/report hashes and independently rescored carrier-year national counts |
| `git-timeline.txt`, `production-repair.diff` | Read-only git evidence of relevant ordering and precise production repair |
| `routes-{A,B}.csv` | Every observed directional route, cell/weight shares, own-arrival contribution, departure/common-clock contrast, schedule difference; sorted by contribution |
| `airports-{A,B}.csv` | Incident-route weight, contribution and omission gap for every airport; contributions overlap at route endpoints and must not be summed |
| `month-{A,B}.csv`, `time_of_day-{A,B}.csv`, `year-{A,B}.csv` | Complete observed temporal groups and weight shares; band b means local [2b,2b+2) hours |

`results.json` rates and intervals are fractions (multiply by 100 for percentage points). Fields ending `_points`, and CSV gaps/contributions, are already percentage points. Duration fields are minutes. UA-minus-WN is the default sign; a negative `dep_late` contrast favors UA. The full review reverses that sign when describing the WN-minus-UA late-departure excess. JSON keys `decomposition_advantage_points` have the latter sign for mutually exclusive failures and sum to the positive UA arrival gap.

## Definitions and limitations

- The independent raw audit recomputes source-row ordinals, carrier IDs, date normalization and exact `<15` outcome scoring. Source flags are valid/nonmissing in these records; no invalid value is silently discarded. It compares every audited UA/WN record to the saved derivatives and independently rebuilds frozen pair-cell keys/counts.
- All primary descriptive contrasts use the frozen scheduled counts and `w=(n_UA+n_WN)/2`. Departures 15+ late are noncancelled flights with known `DepDelay>=15`, divided by all scheduled flights; diversions remain eligible. Cancellation-inclusive timely departure requires noncancelled `DepDelay<15`. Noncancelled missing departure delay is separately counted (zero here). The conditional-known rates divide weighted late-departure rates by weighted known-noncancelled rates; they are not the registered estimand.
- For each cell, the common midpoint budget is the equal-carrier mean of UA and WN mean scheduled block minutes. A completion passes when `DepDelay+ActualElapsedTime < budget+15`. Failures stay failures. Two additional clocks use WN's or UA's mean schedule for both carriers. The `equalized_mid` key evaluates the midpoint comparison using `ArrDelay+CRSElapsedTime`; it checks robustness to small inconsistencies in the reported elapsed-time identity, not a distinct intervention.
- Scheduled means use all matched records. Actual/slack means condition on completed flights, then retain cells with observations for both carriers; `completed_cell_means.weight_share` records their restricted coverage. Completed-row counts are overall matched counts, not counts after that cell restriction. Longer scheduled block time alone does not identify unnecessary or intentional padding. Common-clock changes are deadline sensitivities, never causal attributable fractions.
- Independent intervals explicitly calculate circular blocks, original finite-window variance correction, analytic per-draw studentization, linear pivot quantiles and the t floor. Saved Y draws/endpoints reproduce production. Added departure/common-clock intervals are only descriptive nominal 99% intervals: not separately gate-certified and not simultaneous across checks.
- Route contributions sum to the total gap. Airport contributions overlap. Removing contribution-ranked routes is intentionally post-hoc. No inferential claims are made for selected routes, months, bands or omitted populations.
- The 2015 result is an already-exposed exploratory pilot, independently reproduced using the same own-timetable scoring/weighting. The review's midpoint clock differs from the pilot's original all-carrier route benchmark. Historical decompositions use common routes (and separately common route×month×band strata), normalized within the overlap. Symmetric twofold decomposition is `sum((q-p)*(a+b)/2)` for composition and `sum((q+p)*(b-a)/2)` for within-group changes; overlap shares are saved. These are arithmetic descriptions, not causes.
- Git/PROGRESS evidence supports the recorded access order but is not a tamper-proof access log. The first raw rescore was rerun after making cancellation and observed-late departure categories explicitly disjoint; the final saved code/output use that definition. This is review-only diagnostic development after outcomes, not a change to confirmation.

All saved files are code, hashes, logs or aggregates. There are no raw/derived flight rows or third-party page snapshots here. Official definition and DOT annual-report URLs and the full interpretive disposition are in [`../reviews/astra-methods-1.md`](../reviews/astra-methods-1.md).
