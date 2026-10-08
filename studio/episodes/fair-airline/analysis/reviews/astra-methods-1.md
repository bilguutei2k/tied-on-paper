# Astra adversarial methods review — 2026-10-07

**Disposition: APPROVE WITH CHANGES.** No blocking defect was found in the registered UA–WN estimates, intervals, outcome scoring, or documented access order. The large result survives independent reconstruction from raw source records. Approval is conditional on the reporting changes below before filming: give the timetable sensitivity and departure comparison real prominence, narrow the spoken scope, and correct the national-rate terminology. This is approval of the amended operator-only, comparable-flight question, not restoration of the original all-airline reversal question.

The confirmatory result is UA minus WN **6.2721 percentage points in A (2023–24), nominal 99% envelope [4.6007, 7.9435]**, and **8.2027 in B (2025), [5.3112, 10.9951]**. Both lower endpoints exceed the registered two-point line. The same-decisive-label replication verdict follows. My independent raw rescore, cell reconstruction, and independent block-interval calculation reproduce these numbers.

The most consequential new finding is that a common scheduled-block deadline reduces these gaps to **2.5874 and 4.3312 points**, but the cancellation-inclusive timely-departure advantages are **9.9130 and 13.2814 points**. United's scheduled block times are about 4.5 minutes longer, and its actual block times are also longer. Thus a large share of the own-timetable contrast is sensitive to which deadline is used; this does **not** establish artificial or deliberate schedule padding. The departure difference is strong evidence that the entire contrast is not an arrival-deadline artifact.

## Scope and evidence

Contract reviewed: `METHOD.md`, `analysis/amendment/AMENDMENT-1.md`, `analysis/amendment2/AMENDMENT-2.md`, and `analysis/amendment2/OWNER_APPROVAL.md`. Implementation reviewed: all production analysis/interval/preparation/verification code, the production and result seals, relevant schedule ingestion and normalization code, `FINDINGS.md`, `results.json`, `qa.json`, `DEVIATIONS.md` entries 21–23, and `PROGRESS.md`. I inspected the historic pilot code and saved comparison, without invoking its download/writing entry point.

All additional empirical checks in this review are **POST-HOC DESCRIPTIVE CHECKS, NOT REGISTERED**. They cannot replace either confirmatory endpoint, select an interval, or change its verdict. Executable code and aggregate outputs are in [`../review_checks/`](../review_checks/README.md). In particular:

- `review_checks.py` independently streams the 36 raw CSVs, verifies their archived byte hashes, reconstructs row IDs and schedule keys, rescores UA/WN records, rebuilds cell counts and all added comparisons, and implements the interval directly without importing production analysis functions.
- `raw_audit.json` records the monthly raw checks; `results.json` holds the descriptive checks and interval reproduction; route/airport/month/time-of-day CSVs include all observed groups, not just favorable examples.
- `integrity.json`, `evidence.json`, `git-timeline.txt`, and `production-repair.diff` preserve provenance checks. Thirty-one current input/code/report hash checks and all six raw national carrier-year count comparisons pass.

No production analysis code, registered result, raw data, or derived source file was edited. Only review documents, review code, and aggregate review evidence are proposed for commit. The review independently reconstructs production arithmetic; it does not rerun the entire 60,000-dataset synthetic gate or claim universal validity beyond that gate's modeled processes.

## 1. Order, integrity, and the three deviations

Git author and committer times agree for the relevant checkpoints. Times below are UTC on 2026-10-07; Pacific times in git are converted by adding seven hours.

| Event | Git checkpoint/time | Logged access or computation | Assessment |
|---|---|---|---|
| Owner approval | `41a6974`, 15:16:15 | Owner approval records 08:16 Pacific | Before production and A access |
| Original production seal | `af6b613`, 15:29:45 | A first open 15:29:59.000659 | Seal precedes logged outcome access by about 14 seconds |
| Technical repair seal | `4f759d3`, 15:31:25 | A resumes 15:31:40.958609 | Repair committed before resumed ingestion |
| First A calculation | — | 15:32:04.578747 | After both code checkpoints |
| A results seal | `c829f51`, 15:39:26 | B first open 15:39:44.777454 | A seal precedes logged B access by about 19 seconds |
| B results seal | `12320b0`, 15:42:57 | Contemporary DOT context opened after this seal | No context-driven alteration of A/B |

The files named by **both** historical production seals hash to the bytes in their respective git commits. The original seal says outcomes unopened; the repaired seal truthfully says outcomes opened and names the repair. Current A and B result files are byte-identical to their first result-seal commits. All three saved start arrays match their committed hashes and regenerate exactly from the stated generator/seed/order. `analyze.py` checks committed required code and seal bytes before ingestion and additionally requires committed A results before B.

These are coherent documentary and executable barriers, not a tamper-proof operating-system access log. Git timestamps and a progress entry cannot prove that nobody separately viewed an outcome. Earlier schedule projection did scan mixed-file bytes for CSV framing while materializing only its allowlist; the record also discloses incidental earlier public-ranking exposure. There is no evidence here of an unlogged confirmatory outcome analysis, and no basis to claim perfect blindness beyond the documented process.

**Deviation 21 — seed/order and production interface: acceptable, with the existing disclosure retained.** Original METHOD specified production PCG64 seed `20261005`; the amendments explicitly replace the sampling distribution, draw count, and ordering with 1,999 year-first row-major start matrices. Their `SeedSequence([20261007, bank, scenario, replicate, stream])` specification is organized around synthetic banks. Amendment 1's phrase “with the stream below” leaves some production-seed ambiguity, so retaining the separately specified original production seed is an interpretation, not textually inevitable. It was explicitly disclosed and sealed before A, not chosen by its result. No reseeding occurred. The one-open-period interface preserves the A-before-B contract. Equal-year and census-range conventions concern descriptive outputs only.

**Deviation 22 — January ingestion repair: acceptable technical repair, not an outcome-blind change.** The git diff changes `status_errors=errors` to `status_errors=0`, adds `re`, and preserves the original first-open timestamp on resumption. `errors` was local to `score_raw`, which asserts it is zero before returning. The NameError occurs after validated January scores have been formed and a partial derivative written, before any call that estimates a period contrast. Therefore January outcomes were exposed; “before estimates” must not become “before outcomes.” The metadata zero follows a mandatory assertion and does not suppress a failed validation. The partial derivative was reported discarded and rebuilt.

Crucially, the diff contains no change to filtering, scoring, identities, support, cell membership, denominators, weights, interval arithmetic, draws, materiality, or decisions. Production scientific code has no later change. The small report-field repair could not mechanically choose a favorable membership or result; the fresh raw rescore also agrees with the saved derivative on every UA/WN record. A hypothetical analyst's knowledge of January is not retroactively erased, but there is no outcome-dependent analytical adaptation in the recorded change. The honest qualification is sufficient; a new amendment is not warranted for this fix.

**Deviation 23 — incomplete SQL verification: not a blocker.** METHOD requires an independent numerical derivation, not specifically SQL. The replacement NumPy verifier independently expands per-flight weights and uses compensated summation; it agrees within 1.39e-17 in A and 9.72e-17 in B. The uncompleted SQL check is explicitly marked incomplete and excluded from required passes. However, NumPy and the original “fresh” reproduction both reuse the scored outcome derivative: they alone cannot certify raw-to-score ingestion or independently rederive the full interval. This review closes those gaps with fresh raw scoring and independent interval loops. Do not describe the original derivative-based rerun as a fresh raw ingestion. Repeated computation log entries, without code/rule changes and with stable reproduction evidence, are deterministic replays, not additional independent confirmations.

## 2. Fidelity to the amended contract

| Item | Finding and evidence |
|---|---|
| Population/identity | Reporting operators UA/DOT 19977 and WN/DOT 19393; IATA identity agrees on all audited rows. United Express/codeshare operators are not added. Directional airport IDs are retained, not city markets or reciprocal routes. |
| Cells | Source year × directional route × normalized local scheduled departure date × floor(minutes/120). Only cells containing both carriers. Independent reconstruction exactly matches frozen counts and keys: 167,457 cells in A, 83,744 in B. |
| Scoring | Both status flags zero and finite signed `ArrDelay < 15` is success; exactly 15 fails. Cancellation/diversion overrides missing outcome fields and fails. Unknowns fail primarily and receive the registered endpoint assignments. Production asserts on invalid nonmissing status/delay values; existing boundary fixtures include fractional 14.999/15, missing and invalid values. |
| Weights/denominators | `w=(n_UA+n_WN)/2`; within-carrier cell mean, followed by the same cell weight for both carriers. Failures stay in scheduled counts. A pools two source years; B uses its own basket. Independent raw counts and groupby reproduce every frozen n and point. |
| Missingness/quality | No UA/WN unknown outcomes or invalid matching keys in the independently audited source records. All registered carrier-year national/matched quality limits therefore pass. The three missingness assignments coincide; this is observed absence of unknowns, not an exemption from bounding. |
| Resampling | Exactly 1,999 draws, 28-day circular whole-network blocks within source year, thirteen full blocks plus a 1/2/1-day remainder for 2023/24/25; zero-support dates retained. One date multiplicity applies to all cells. No rematching or flight resampling. |
| Studentization | Original residual-block population variances use T/(T−28) and T/(T−r); per-draw full/prefix residual sample variances use ddof=1 at the same thirteen full-block starts. The independent final short-block start contributes to the sampled ratio. Numerator/denominator pooling and df 24/12 agree with Amendment 2. |
| Quantiles/envelope | Linear .005/.995 pivot quantiles, Student-t(.995) floor, inverse studentized endpoints, no clipping or invalid-draw deletion. All denominators and SEs positive. Independent saved-draw maximum discrepancies are 2.78e-17 / 6.94e-17; interval endpoints agree to floating precision. |
| Decision/replication | Strict L>.02 or U<.02; equality and quality failure inconclusive. Both lower envelopes exceed .02; same decisive label permits replication. B cannot revise A. Separate periods do not imply independent underlying airline/network shocks. |

For A, the t floor (2.79694) controls both tails. For B, the upper pivot (3.16296) controls the lower interval endpoint and the t floor (3.05454) controls the upper endpoint. These are the specified asymmetric calculations, not a substituted normal or percentile interval. The gate's empirical certification and low three-point replicated power are disclosed; neither invalidates an observed result substantially above three points. Nominal 99% is not an exact universal coverage guarantee or a confidence interval for the historical census itself.

## 3. Correctness: source rows, dates, failures, and joins

The streaming audit scanned **20,928,579 source rows** across all 36 archives and independently rescored **6,537,703 UA/WN rows**. Every UA/WN source ordinal, carrier/certificate identity, flight number, origin/destination ID, scheduled time, normalized date and band agrees with the schedule derivative. Every Y/U/cancellation/diversion indicator agrees with the outcome derivative. Six annual national counts/success totals reconcile exactly to production. No natural-key duplicates were found, no source rows were silently removed, and matched scheduled flight totals are **177,840 UA / 177,883 WN** in A and **88,717 / 88,087** in B.

The production cell-count mismatch query alone would not catch an absent join partner because it filters the joined carrier fields. It is complemented by the final equality between output cell count and frozen cell count, unique source-ID checks, schedule/outcome cardinality checks, and the independent NumPy membership check. My raw groupby and one-to-one frozen-cell comparison independently close that potential silent-drop path. There is no observed join inflation or loss.

Local scheduled departure dates are the correct matching basis. No UTC conversion or arrival-date join is made. A flight arriving after midnight remains on its scheduled departure-date cell. `ArrDelay` and elapsed-minute fields avoid subtracting incompatible local clocks. The 2400 next-day rule and source-year retention are implemented; there are **zero UA/WN 2400 or normalized-next-year records** in the confirmation data, so this boundary convention cannot generate the observed gap. The [BTS reporting-field dictionary](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ) supports the local-HHMM, signed delay, operating certificate, and elapsed-minute interpretations.

A useful nonzero audit finding: `DepDelay + ActualElapsedTime − ArrDelay − CRSElapsedTime` is nonzero for **76 of 6,454,899** fully observed completed UA/WN records; 75 exceed one minute (maximum absolute discrepancy 176 minutes). Four are on A's comparable support, none on B's. These source inconsistencies are not a date-normalization bug in the registered estimator, which uses `ArrDelay` directly. Repeating the common-clock scoring through `ArrDelay + CRSElapsedTime` gives identical weighted carrier rates to the elapsed-time construction in both periods. Thus they have no aggregate effect on the reported clock sensitivity. No source anomaly was silently repaired.

## 4. Post-hoc descriptive threats checks — not registered

All rates below use the frozen common cell weights and scheduled-flight denominators unless explicitly conditional. Added intervals reuse the registered block starts and independently coded arithmetic, but **were not gate-certified for these new endpoints, are not simultaneous across checks, and support no new registered verdict**.

### (a) Schedule padding and actual elapsed times

For each cell, compute each carrier's mean `CRSElapsedTime`. The shared deadline is their equal-carrier midpoint plus 15 minutes, measured from each flight's own scheduled departure. Score a completed flight successful if `DepDelay + ActualElapsedTime` is strictly below that deadline; cancellations/diversions still fail. This changes the question to a common elapsed-time allowance, not a literal common wall-clock arrival time for flights departing at different minutes. It is a normative descriptive benchmark, not a causal intervention.

| Quantity | A: 2023–24 | B: 2025 |
|---|---:|---:|
| Scheduled block minutes, UA / WN, all matched cells | 149.314 / 144.794 | 151.331 / 146.878 |
| Scheduled UA−WN difference | +4.520 min | +4.454 min |
| Actual block minutes, UA / WN, cells with completed observations for both | 143.438 / 138.647 | 147.351 / 141.121 |
| Actual UA−WN difference on that common completed-cell subset | +4.791 min | +6.230 min |
| Scheduled-minus-actual slack difference on the same subset | −0.268 min | −1.776 min |
| Original own-timetable gap | +6.272 points | +8.203 points |
| Shared midpoint deadline gap | +2.587 points | +4.331 points |
| Descriptive nominal 99% interval for shared midpoint gap | [1.082, 4.092] | [1.967, 6.821] |
| Own-minus-shared-deadline change | 3.685 points (58.75% of own gap) | 3.872 points (47.20%) |
| Both carriers scored on WN's cell-mean block allowance | +2.672 points | +4.321 points |
| Both scored on UA's cell-mean block allowance | +2.383 points | +4.441 points |

Actual-duration/slack comparisons require completed observations on both sides; they cover 97.73% / 98.55% of original cell weight, with 175,329/175,695 and 88,037/87,235 completed UA/WN rows overall. Do not subtract differently selected means and call the result padding. On the aligned subset, UA has **less**, not more, average realized schedule slack. Longer scheduled times coexist with longer actual times, which may reflect fleet, gates, taxiing or other operating circumstances.

The defensible answer to “how much could padding explain?” is a **3.69/3.87-point deadline sensitivity**, not “59%/47% caused by padding.” This check removes much of the own-timetable advantage but does not identify deliberate padding, a feasible schedule change, or the cause of the residual. The sensitivity's two descriptive lower bounds do not both clear the registered two-point line; do not transfer the registered materiality verdict to common-clock performance.

### (b) Departure punctuality

Use the same cell weights and all-scheduled denominators. Define a late departure as a **noncancelled** flight with `DepDelay >= 15`; diversions remain eligible because they can depart punctually. Report cancellation separately rather than deeming an unoperated flight an observed late departure. Cancellation-inclusive timely departure means noncancelled with known `DepDelay < 15`; unknown noncancelled departures fail. There are no such unknowns here. These categories sum to one, and cancellation/late-departure categories are mutually exclusive.

| Departure result | A | B |
|---|---:|---:|
| 15+ late, UA / WN, percent of scheduled flights | 17.898 / 28.031 | 18.421 / 31.513 |
| WN−UA late-departure gap | **10.133 points** | **13.093 points** |
| Descriptive nominal 99% interval for that gap | [8.556, 11.709] | [9.638, 16.307] |
| Cancellation-inclusive timely departure, UA / WN | 80.903% / 70.990% | 81.133% / 67.851% |
| UA−WN timely-departure gap | **9.913 points** | **13.281 points** |
| Descriptive nominal 99% interval | [8.251, 11.575] | [9.955, 16.504] |
| Late among weighted known noncancelled departures, UA / WN | 18.115% / 28.308% | 18.503% / 31.715% |

Arrival schedule padding cannot mechanically change `DepDelay`; scheduled departures and operational choices can still matter, so this is not a randomized airline-quality test. On the aligned completed-cell subset, UA's mean departure delay is also lower by 4.35 / 7.89 minutes. Stronger departure than arrival performance is consistent with UA taking longer after departure, not with the whole result being manufactured by a more generous arrival promise.

### (c) Cancellation/diversion/late-arrival decomposition

Define mutually exclusive failures: cancelled; diverted and not cancelled; completed but 15+ late; unknown. For each, WN minus UA failure rate contributes positively to the UA timely-completion advantage. Their sum exactly recovers the gap.

| Contribution, percentage points | A | B | 2015 exploration |
|---|---:|---:|---:|
| Cancellations | −0.220 | +0.189 | +1.012 |
| Diversions, excluding cancellations | +0.032 | +0.003 | +0.046 |
| Completed but 15+ minutes late | +6.459 | +8.011 | +1.896 |
| Unknown | 0 | 0 | 0 |
| Total | **6.272** | **8.203** | **2.953** |

Cancellations slightly oppose UA's advantage in A and add only 0.19 points in B. The large contemporary result is overwhelmingly late arrivals, not cancellation exclusion or a handful of diverted flights.

### (d) Concentration

There are **221 directional routes / 80 airports in A**, and **215 / 80 in B**. Routes with positive own-timetable UA gaps account for 88.86% / 93.28% of comparison weight (159/221 and 164/215 routes). This is broad but not universal.

| Concentration check | A | B |
|---|---:|---:|
| Weight touching Denver | 79.31% | 82.22% |
| Denver-incident contribution to overall gap | 4.356 points | 6.178 points |
| Gap after omitting Denver | 9.262 points | 11.388 points |
| Largest directional-route contribution | DEN→PHX: 0.227 points | SFO→DEN: 0.342 points |
| Top five contribution-ranked routes: weight / total contribution | 8.46% / 1.029 points | 11.82% / 1.401 points |
| Gap after removing those five | 5.727 points | 7.713 points |
| Top ten contribution-ranked routes: weight / total contribution | 17.68% / 1.906 points | 20.51% / 2.425 points |
| Gap after removing those ten | 5.303 points | 7.268 points |
| Gap after removing twenty largest contributors | 4.497 points | 6.345 points |
| Gap after removing ten largest routes by schedule weight | 6.533 points | 7.864 points |

A's next-largest route contributors are DEN→SFO (0.207), SFO→SAN (0.202), LAS→LAX (0.200), and SFO→DEN (0.194). B's next four are DEN→PHX (0.276), SFO→SAN (0.275), PHX→DEN (0.254), and LAS→DEN (0.254). After Denver, the largest airport contributions are SFO, LAS, LAX, PHX in A (1.460, 1.146, 1.027, 0.720 points), and SFO, LAX, LAS, PHX in B (1.866, 1.084, 1.069, 0.804). Airport contributions overlap because each route has two endpoints; **do not sum them**.

The gap is not caused arithmetically by a few extreme routes. The population is nonetheless heavily Denver-centered. Removing Denver increases the gap, so its dominance limits scope rather than explaining away the average. Contribution-ranked removals are deliberately adversarial post-hoc summaries, not newly tested populations.

### (e) Time of day and month

A's aggregate before-10:00 local gap is **−0.414 points**, on 30.64% of weight; B's is **+1.379**, on 28.75%. From 16:00 onward, gaps are **11.709 / 12.896 points**, on 32.36% / 34.25% of weight. A's 04–06 and 06–08 bands favor WN by 1.60 and 0.81 points; 08–10 is only +0.17. The 18–20 band favors UA by 12.98 / 14.90 points. There is no shared support before 04:00; the 22–24 band has only about 0.1% / 0.4% of weight. These are whole-band contrasts, not evidence of minute-level matching or causal delay propagation.

Every calendar-month aggregate favors UA, but A ranges from **3.68 points in February to 8.87 in March**; B ranges from **0.60 in January to 14.77 in October**. B is not evidence of a two-point advantage in every month. Removing timing mix in the primary estimator does not erase this effect heterogeneity. All months and observed bands, their weight shares, arrival/departure contrasts and schedule differences are saved in the CSVs. This is an important caveat to consumer advice about morning departures.

### (f) Why the result exceeds the 2015 pilot

The existing 2015 own-timetable UA–WN pilot point independently reproduces as **2.9531 points**, on 45,509 cells and 50,221 UA / 48,817 WN flights. Contemporary effects are 2.12 and 2.78 times that point, not exactly a doubling in both periods. There is no 2015 confirmatory replication claim.

| Comparable descriptive quantity | 2015 | A | B |
|---|---:|---:|---:|
| Own-timetable UA gap, points | 2.953 | 6.272 | 8.203 |
| Cancellation-inclusive timely-departure gap, points | 3.648 | 9.913 | 13.281 |
| Scheduled block UA−WN difference, minutes | 4.511 | 4.520 | 4.454 |
| Shared midpoint-clock gap, points | −0.567 | 2.587 | 4.331 |
| Own-minus-shared-clock difference, points | 3.520 | 3.685 | 3.872 |

Thus widening scheduled-duration differences are not the observed reason the point grew. The deadline sensitivity stays near 3.5–3.9 points while a large departure-performance difference emerges. In the exact failure decomposition, the late-arrival contribution increases **4.564 / 6.115 points** relative to 2015; the cancellation contribution shrinks **1.231 / 0.823 points**, partly offsetting it. The pilot's result was more dependent on cancellation differences and deadlines.

Changed route mix also fails to explain away the growth. There are 101 directional routes shared with 2015, covering 92.48% of pilot weight and 77.00% / 82.17% of contemporary weight. Within those routes, gaps rise from 3.060 points to 7.379 / 8.843. An exact symmetric decomposition of that change attributes **−1.571 / −1.319 points to route-weight composition** and **+5.890 / +7.102 to changes within routes**. Applying pilot route weights to contemporary route-specific gaps gives 9.155 / 10.030 points. This is algebra, not a causal attribution.

A finer check on common route × month × two-hour-band strata likewise yields a negative composition contribution (−0.927 / −1.068 points) and positive within-stratum change (+5.643 / +7.419). Its restricted overlap covers only 37.96% / 40.18% of contemporary weight, so it is corroborative, not an alternate headline. Exact dates cannot be held constant across years. Changed within-route operating conditions, fleets, schedules, shocks and residual passenger/flight mix remain possible explanations. These data quantify **where** the increase resides; they do not identify a unique organizational cause.

## 5. Interpretation and required reporting changes

`FINDINGS.md` correctly says own published timetable, common-basket scope, no causal airline-choice effect, no best-airline ranking, operator-only population, fixed-schedule uncertainty, and no two-period national-versus-matched reversal. Its explicit disclosure of the failed gates, amendment, incidental ranking exposure and production deviations is good. The public annual operating tables indeed put UA/WN at ranks **8/9 in 2023, 6/7 in 2024, and 5/4 in 2025**; the counts and rates match the raw annual reconstruction to published rounding. Sources: [2023 Table 1D](https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202024%20ATCR%20revised%203-06-2025.pdf), [2024 Table 1D](https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202025%20ATCR.pdf), [2025 Table 1D](https://www.transportation.gov/sites/dot.gov/files/2026-03/February%20%202026%20ATCR.pdf), each printed page 10. Annual near-equality and adjacency do not contradict a substantially different average on the small overlap basket.

**Required changes before film/publication approval:**

1. **Add the material timetable/departure finding prominently**, with the post-hoc label: about 4.5 extra scheduled minutes, common-clock gaps 2.59/4.33 instead of 6.27/8.20, and timely-departure gaps 9.91/13.28. Also say actual elapsed times are longer for UA; do not label the 59%/47% reductions causal padding shares, intentional gaming, or a newly registered materiality success. A generic one-line mention of buffers is now insufficient given the quantified sensitivity.
2. **Make operator and narrow-basket scope explicit in the film's headline/caveats**, including exclusion of United Express/codeshare operators, overlap coverage of about 11–12% of UA and 6% of WN schedules, and roughly 80% of comparison weight touching Denver. Show or state the strong time-of-day heterogeneity; the result is not a general morning-flight recommendation. Keep the national near-equality/adjacent-ranking context and do not narrate a two-period reversal.
3. **Replace “unmatched all-flights,” “A's unmatched UA lead,” and equivalent labels with “unadjusted all-flights.”** Those national denominators include matched flights. “Unmatched” properly refers to the separate outside-comparison population. Clarify that the original stable reruns reused outcome derivatives; link this review's fresh raw scoring and interval rederivation as additional verification. Preserve all original deviation and SQL-incompletion disclosures.

The statistical results need no recalculation. These changes can be made as reporting edits with explicit links to post-hoc review evidence; they must not silently expand the registered analysis.

**Exact proposed one-sentence film headline:**

> Among flights on matching directional routes, dates and two-hour departure windows, United-operated flights completed less than 15 minutes late against their own schedules 6.3 percentage points more often than Southwest-operated flights in 2023–24 and 8.2 points more often in 2025.

**Caveats the film must communicate**, in narration and/or legible adjacent graphics, with the causal/schedule limitation spoken:

- This measures each operator keeping its own timetable; it does not establish the effect of choosing an airline, faster travel, intentional padding, or passenger outcomes after rebooking. Cancellations and diversions count as failures; 15 minutes late already fails.
- The result covers overlapping mainline operating services, excludes United Express/codeshare partners, and uses the same observed cell weights for both operators. It covers a small fraction of either network and is Denver-heavy; the gap is much smaller in early departures.
- A clearly labeled exploratory common-deadline check reduces the arrival gaps to 2.6/4.3 points; UA's schedules and actual flight blocks are longer. Its cancellation-inclusive timely-departure advantage remains 9.9/13.3 points. These added checks do not inherit the confirmatory verdict.
- Whole-network rates are nearly equal and the operating-carrier tables place the airlines adjacent, with UA already ahead in 2023–24. Display the registered nominal 99% envelopes and describe 2025 as a separate-period replication, not proof of an independent causal effect or a guarantee for future flights.

**Final disposition:** approve with the three reporting changes above; **no blocking methods or integrity issue identified**. The SQL task can remain explicitly incomplete. The metadata repair does not warrant discarding the confirmatory result. A film that omits the now-quantified timetable sensitivity or markets the result as general airline quality would not satisfy this approval.
