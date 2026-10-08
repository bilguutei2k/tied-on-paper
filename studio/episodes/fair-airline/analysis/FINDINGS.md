United-operated flights had a larger timely-completion rate than Southwest-operated flights on comparable flights: 6.27 percentage points in 2023–2024 and 8.20 points in 2025. Both periods meet the registered verdict **UA advantage above two points**, so the result is **replicated**. This is a comparison against each airline’s own published arrival timetable on overlapping services, not a causal airline-choice effect or a best-airline ranking.

The population is operator-only: UA/19977 and WN/19393. United Express and flights flown by other codeshare operators are excluded. The overlap covers about 11–12% of United-operated schedules and 6% of Southwest-operated schedules; about 80% of comparison weight touches Denver. This is a small, Denver-heavy slice of the two networks.

The adjusted gap is UA minus WN, with the same schedule-count weights for both carriers within each directional route, normalized scheduled date and two-hour departure cell. Cancellations, diversions and indeterminate outcomes fail. Exactly 15 minutes late fails. The materiality line is two percentage points; the whole missingness-envelope interval must clear it. The two-point scale existed before the pilot for a different test; its amended single-pair use, scope and whole-envelope rule were fixed after the 2015 pilot and the initial failed gate, before confirmation outcomes. Amendment 2’s interval was specified after two failed outcome-blind gates.

| Period | Registered verdict | Adjusted gap (points) | Nominal 99% envelope (points) | Comparable flights UA / WN |
|---|---|---:|---|---:|
| 2023–2024 primary A | UA advantage above two points | 6.27 | [4.60, 7.94] | 177,840 / 177,883 |
| 2025 replication B | UA advantage above two points | 8.20 | [5.31, 11.00] | 88,717 / 88,087 |

**Prominent timetable and departure disclosure — post-hoc descriptive checks, not registered.** With the same frozen comparison cells and weights, United schedules about 4.5 more block minutes: +4.52 in A and +4.45 in B. Its actual flight blocks are also longer on cells with completed observations for both operators: +4.79 minutes in A and +6.23 in B, covering 97.73% / 98.55% of comparison weight. “About 4.8 minutes longer” describes A only. Longer schedules alone do not identify unnecessary or deliberate padding.

Scoring both operators against a shared departure-relative elapsed-time allowance (the midpoint of their cell-mean scheduled blocks, plus the same 15-minute tolerance) reduces the UA arrival gaps to **2.59 / 4.33 points**, from 6.27 / 8.20. The changes are 3.69 / 3.87 points of deadline sensitivity; no causal fraction of the gap is identified. The added descriptive nominal 99% intervals are [1.08, 4.09] / [1.97, 6.82] points and do not inherit the registered materiality verdict. This is a shared elapsed-time budget from each scheduled departure, not one wall-clock arrival deadline.

The departure contrast also remains large: WN has **10.13 / 13.09 points more noncancelled departures 15+ minutes late**, using all scheduled flights as denominators. UA’s cancellation-inclusive timely-departure advantage is **9.91 / 13.28 points**. Diversions remain eligible for the departure check; an unoperated cancelled flight is not an observed late departure. Arrival timetables cannot mechanically change departure delay, but scheduled departure choices and operating circumstances remain bundled. These checks establish no causal airline-choice effect.

**Post-hoc scope and heterogeneity, not registered.** Denver touches 79.31% / 82.22% of comparison weight. Before 10:00 local scheduled departure, arrival gaps are −0.41 / +1.38 points; from 16:00 onward they are +11.71 / +12.90. This average is not a general morning-flight recommendation or a two-point advantage in every month: monthly gaps range from 3.68 to 8.87 in A and 0.60 to 14.77 in B. Full definitions, all groups and the independent raw audit are in [the review checks](review_checks/README.md), [raw_audit.json](review_checks/raw_audit.json) and [the methods review](reviews/astra-methods-1.md).

Replication follows the registered same-decisive-label rule. A was sealed before any 2025 outcome. B does not rewrite A. The alternative registered labels are “no material UA advantage under this rule” when the entire envelope is below two points, and “inconclusive” otherwise or after quality failure.

Primary, lower and upper missingness assignments give identical points and intervals in both periods: no UA/WN outcome is indeterminate. All national and matched carrier-year unknown shares and invalid-key shares pass the 0.1% cutoffs. Every one of the 1,999 draws has positive finite denominators and positive finite original/per-draw SEs. Assignment intervals, counts and named evidence are in results.json and qa.json.

**Descriptive context — cannot change a verdict.** The unadjusted all-flights rates and comparable-cell coverage are:

| Period | All-flights UA on time | All-flights WN on time | UA comparable coverage | WN comparable coverage |
|---|---:|---:|---:|---:|
| A | 78.34% (1,492,663 flights) | 77.91% (2,857,884 flights) | 11.91% | 6.22% |
| B | 77.65% (795,271 flights) | 77.76% (1,391,885 flights) | 11.16% | 6.33% |

These are exact historical census/missingness ranges, which collapse to the recorded rates because there are no unknown outcomes. They are not confidence intervals for future flights. A’s unadjusted all-flights UA lead is only 0.43 points; in B, WN leads by 0.10 points. Neither is the common-basket estimand.

The official DOT annual tables say:

| Year | Operating United: rank, on time, n | Operating Southwest: rank, on time, n | Marketing-network United / Southwest: rank and on time | Official source |
|---|---|---|---|---|
| 2023 | 8, 78.07%, 732,212 | 9, 77.25%, 1,438,465 | 4, 78.47% / 5, 77.25% | [DOT February 2024 ATCR](https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202024%20ATCR%20revised%203-06-2025.pdf) |
| 2024 | 6, 78.60%, 760,451 | 7, 78.57%, 1,419,419 | 3, 79.14% / 4, 78.57% | [DOT February 2025 ATCR](https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202025%20ATCR.pdf) |
| 2025 | 5, 77.65%, 795,271 | 4, 77.76%, 1,391,885 | 6, 76.87% / 3, 77.76% | [DOT February 2026 ATCR](https://www.transportation.gov/sites/dot.gov/files/2026-03/February%20%202026%20ATCR.pdf) |

Operating-carrier Table 1D is on printed page 10; marketing-network Table 1C is on printed page 9. All six operating-carrier rows match our flight counts and percentages to the report’s two-decimal rounding. United’s marketing-network population includes codeshare partners; our registered UA population is the reporting operator alone. The marketing-network counts and rounding ranges are in descriptive_context.published_dot_annual. No source pages/PDFs were saved. The contemporary tables already put United ahead in 2023 and 2024; this result must not be described as a material national-versus-matched reversal in both periods.

**All registered sensitivities — descriptive, cannot change either verdict.** Each changes one choice, retaining the original comparison and frozen schedule membership. The intervals below reuse the same sealed whole-network starts; they are descriptive nominal 99% ranges and were not separately certified by the primary gate. Airport exclusions also remove that airport from national rates; original and retained coverage denominators are saved.

| Sensitivity | A gap [range], points | A UA / WN flights | B gap [range], points | B UA / WN flights |
|---|---|---:|---|---:|
| One-hour windows | 6.61 [4.89, 8.34] | 97,768 / 97,671 | 8.83 [6.01, 11.45] | 51,116 / 51,014 |
| Four-hour windows | 6.06 [4.41, 7.71] | 286,978 / 278,052 | 7.88 [5.03, 10.72] | 140,408 / 132,894 |
| Equal cell weights | 6.26 [4.57, 7.95] | 177,840 / 177,883 | 8.19 [5.38, 10.89] | 88,717 / 88,087 |
| Harmonic weights | 6.26 [4.59, 7.94] | 177,840 / 177,883 | 8.20 [5.33, 10.96] | 88,717 / 88,087 |
| Equal-year average of 2023 and 2024 | 6.30 [4.63, 7.96] | 177,840 / 177,883 | Not applicable | Not applicable |
| 2023 separately | 7.51 [4.56, 10.41] | 86,958 / 87,124 | Not applicable | Not applicable |
| 2024 separately | 5.09 [2.76, 7.64] | 90,882 / 90,759 | Not applicable | Not applicable |
| 2025 separately | Not applicable | Not applicable | 8.20 [5.31, 11.00] | 88,717 / 88,087 |
| Omit Denver (11292) | 9.26 [6.81, 11.64] | 37,415 / 36,181 | 11.39 [8.38, 14.94] | 16,285 / 15,151 |
| Omit Atlanta (10397) | 6.33 [4.66, 8.00] | 175,533 / 175,576 | 8.20 [5.29, 11.01] | 87,862 / 87,225 |
| Omit Chicago O’Hare (13930) | 6.32 [4.62, 8.03] | 160,028 / 162,096 | 8.31 [5.47, 11.15] | 83,466 / 83,236 |
| Omit Los Angeles (12892) | 5.97 [4.33, 7.60] | 155,962 / 156,763 | 8.02 [5.14, 10.76] | 78,268 / 78,625 |
| Omit Las Vegas (12889) | 5.82 [4.10, 7.55] | 157,646 / 155,411 | 7.95 [4.99, 10.67] | 79,835 / 78,879 |
| Reciprocal nearest departures within 30 minutes | 6.68 [4.86, 8.50] | 101,198 / 101,198 | 9.09 [6.25, 11.90] | 52,968 / 52,968 |

No registered sensitivity is contrary in direction or puts its entire descriptive range below the two-point line; all displayed lower bounds also exceed two points. This consistency does not expand the confirmatory population or make these secondary checks additional hypothesis tests. The gaps change appreciably across years and airport exclusions; those differences limit any claim of a single universal carrier advantage.

National and common-weighted cancellation, diversion, their union, missing flags and unknown rates are all saved, together with annual rates, outside-comparison populations, invalid-key populations and outside-all-supported-cell populations. The descriptive restriction/reweighting decomposition is also saved. No failed service was removed by its outcome.

**Limits and disclosure.** Matching adjusts route, date and scheduled departure window. Minute-level timing, scheduled arrival buffers, aircraft, staffing, rotations and network choices remain bundled. This is non-causal, operator-only, comparable-flight performance, not passenger-weighted reliability, common-clock speed, connection success or a prediction for an unobserved network. A and B have their own frozen baskets and only a small share of each carrier’s flights is comparable.

The registered interval targets repeated outcomes and calendar shocks on the fixed schedule. Its finite-window correction and Student-t floor are engineering approximations validated only against the registered synthetic processes. Amendment 2 was designed after two failed outcome-blind gates; bank 0 informed the redesign but supplied no acceptance evidence. Fresh selection and independent validation passed before the approved production seal. Validation three-point replicated power was 491/2,000 (24.55%; one-sided exact lower 22.97%); no 80% claim is made at three points. METHOD’s earlier incidental 2024-ranking snippet exposure remains disclosed; no perfect ignorance of public rankings is claimed. This production run opened contemporary annual tables only after sealing A and B.

**Flagged implementation decisions (DEVIATIONS entries 21–23).** Production retains METHOD’s 20261005 seed with the amended year-first draw order. The one-open-period interface preserves the A-before-B barrier; census and equal-year descriptive interval conventions were fixed before access. After January 2023 was first opened, a metadata logging NameError stopped ingestion before any estimate; the reporting reference was repaired, the unsealed partial derivative discarded, the original access time preserved and the repair committed. Scoring, estimator, interval, seed, draws, thresholds and verdict rules did not change. Required independent numerical QA used NumPy sorted-key joins and compensated summation after the supplemental SQL path proved slow; both periods agree to less than 1e-16, and stable reruns using the existing scored outcome derivatives and draw hashes reproduce exactly. Those reruns were not fresh raw ingestions. The [blind re-derivation](../recheck/RECHECK.md) matched all 47 compared values; the review independently performed [fresh raw scoring and full interval reconstruction](review_checks/README.md), with [monthly raw-audit evidence](review_checks/raw_audit.json).

Required QA passes. The supplemental SQL path is explicitly marked separately in qa.json and is not counted as passed unless it completed. Official-row reconciliation, source/ID checks, denominator checks, scoring/boundary fixtures, gate reproduction, independent weighted-flight derivations and stable fresh reproduction are documented there. Review scope: this is Sol’s production verification against the owner-approved contract; no new external methods review is claimed.

Video numbers must cite the proposed [claims ledger](../CLAIMS.json), whose keys point to the sealed registered results, explicitly labeled review checks, or independent derived summaries in [claims_check.json](claims_check.json). Keep the registered and post-hoc interval labels, scheduled denominators and completed-cell restrictions with the numbers. BTS source URLs and immutable raw/derived hashes remain in the episode manifests and sealed input records; raw ZIPs, row-level derivatives and source pages stay outside public history.
