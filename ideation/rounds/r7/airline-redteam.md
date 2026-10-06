# Airline pilot — red-team review

**Verdict: useful exploration; revise before confirmation.** The saved core
arithmetic reproduces, and the slice is genuinely 2015. It supports a narrower
story about overlapping services, not a corrected national league table or a
causal estimate of airline quality. The original r2 design does not pass: its
40% coverage gate fails, and its 2019 benchmark and later-year replication were
never tested. The absence of a qualifying reversal is not evidence of stability.

## What I checked, and what actually exists

Read `LESSONS.md`, `BRIEF.md`, `verify-S6.json`, the requested pilot artifacts,
the ingestion code and the three house methods. Did not run the pilot's entry
point: it writes into r3 and downloads on `all`. No non-2015 BTS data were
opened, downloaded or analysed for this review.

Independent check: `scratch/airline_r7_check.py`; evidence:
`scratch/airline-r7-check.json`. Reproduce from the repository root with
`.venv/bin/python scratch/airline_r7_check.py`. It writes only under scratch.

- All twelve raw ZIP hashes and the slice-ID hash agree with the saved manifests.
- All 5,819,079 Parquet records have dates in 2015 and month matching their source
  month; all source-month/row IDs are unique. Monthly counts match the seal.
- Independently streamed the January raw CSV: 469,968 rows, zero slice violations;
  its candidate counts, successes and completed-known counts match Parquet.
  This is a raw-to-Parquet check for January, not a fresh parse of all twelve ZIPs.
- Independently recomputed all eight national rates (exact agreement), all
  26 eligible own-promise pair contrasts (maximum error <6e-17), and the centered
  network effects through a separate edge/Laplacian formulation (<7e-13).
  Recreated the 4,000 bootstrap coefficient draws (<4e-12 maximum difference).
- Independently recovered 1,111,509 shared flights out of 4,027,227 candidate
  flights (27.60%); at most five candidates occur in one stratum.

`PILOT.md` is a progress log, not the interpretation its last line promises.
There is **no `pilot.json`**. Nor are `league-contrasts.json`, `nearest30.json`,
`pair-bootstrap.npz` or `power.json` present. The current `analysis.py` contains
code to create these; that does not establish that those later checks ran.
The existing `03-shared-route-arrivals.png` also conflicts with the current
code's replacement/deletion logic. Treat the saved numerical artifacts as the
available evidence; do not quote the unwritten report, nearest-match results
or a power calculation as completed validation. This is an artifact/provenance
failure, not evidence that the reproduced ranking arithmetic is wrong.

## Did it test what it says?

The simplified test does what its core definition says: directional airport
route × date × local scheduled two-hour departure window; success is signed
`ArrDelay <15`, and cancellation, diversion and unknown arrival timing fail.
The candidate slice has no unknown completed-flight arrival times, so missing
timing does not drive the observed result. Exactly 15 minutes is late.

It does **not** test r2's joint common-clock design. The main outcome keeps each
airline's own scheduled arrival. Its common-clock sensitivity uses a median of
2015 scheduled durations, rather than a frozen 2019 benchmark. Pair weights
come from 2015 flights, rather than a 2019 target distribution; there is no
2023–2024 estimation or untouched 2025 replication. These were exploratory
design changes and must remain disclosed as such.

There is also an important baseline-label error. The pilot's `naive` denominator
is completed, nondiverted flights with known timing. It is **not** the published
DOT annual on-time rate. The February 2016 ATCR reports Alaska 86.4%, Delta
85.9%, Southwest 79.7% and United 78.2%: these match the pilot's all-scheduled
rates to rounding, not its completed-flight rates. DOT's flight-causation table
also includes cancellations and diversions in the reported-flight denominator.
The published 2015 leader is Hawaiian, excluded from these eight candidates;
Alaska is first **among the selected eight**, not nationally. American's merger
aggregation also needs reconciliation before claiming an exact official-table
reproduction. [DOT ATCR, tables 1A and 9, printed pp. 5 and 22](https://www.transportation.gov/sites/dot.gov/files/docs/resources/individuals/aviation-consumer-protection/155801/2016februaryatcr_0.pdf).

Use the all-scheduled national score for confirmation so the primary comparison
changes the basket, not both basket and denominator. Do not allege that DOT
ignores cancellations. Other publishers may use different definitions; name
and check the particular table before criticizing it.

## Population and the apparent fairer ranking

The direct pair estimate is the cleanest estimand. On strata shared by a and b,
average each carrier's success fraction; weight each stratum by `(n_a+n_b)/2`.
Thus both carriers receive the same stratum distribution, with equal weighting
of flights within each carrier/stratum. It describes the two carriers' observed
services on their overlapping route/date/time opportunities in 2015. It is not
passenger-weighted, not a complete itinerary outcome, and not an estimate for
routes or departure windows where one carrier is absent.

The league table is something else: a weighted additive carrier-plus-stratum
projection. Each carrier cell has weight `total_stratum_flights / k`; fitted
carrier effects sum to zero, and a shared-stratum baseline anchors the scores.
Different pairs meet on different baskets. The index summarizes a connected
comparison network; connectedness does not supply an observed common basket
for eight airlines. Reading the index as eight common-population probabilities
requires transportable additive effects across routes and opponents. Carrier ×
route differences can violate that interpretation and produce cycles or
disagreement with direct pairs. The displayed baseline is not a passenger's
national chance of success.

Coverage is a **fatal problem for a national “really best” claim**, and it fails
the original ≥40% design gate. It is not fatal to carefully labeled supported
pair comparisons. Only 19.10% of all reporting-flight records enter any shared
candidate stratum; 27.60% uses the eight-carrier denominator. Coverage varies
from Southwest's 16.75% to Spirit's 57.31%. Alaska has 29.67%. There is no
all-eight stratum. Selecting shared strata emphasizes competitive services;
the omitted flights are not missing at random. Bigger samples cannot fix this.
Publish coverage by carrier, pair, route and time, plus outcomes for unsupported
flights. Replacing the 40% gate is a new, narrower design after the pilot, not
a retroactive pass for the old one.

## Resampling and bugs

The actual resampling unit is sounder than a flight bootstrap: 53 Monday-start
calendar-week clusters, 4,000 multinomial draws, NumPy default generator seed
20151001. Each draw applies the same week multiplicities to every carrier,
route and outcome, and refits the network effects. It retains within-week
weather, airport and airline-wide dependence. This is variability over
comparable weeks, not sampling error in counting this near-census of flights.
Independent week resampling misses serial dependence across weeks, seasonality
and cross-year structural change. It has not passed a known-truth calibration
gate. No airport/route bootstrap is needed for a target conditional on these
observed routes; generalizing to new networks would require a different design.

Pointwise score/rank intervals are not simultaneous ranking confidence sets.
Pair intervals use max-|T| over **26 eligible pairs × two outcomes**, not every
one of the 28 possible pairs. AS–NK and B6–F9 lack the count support. Eligibility
is count-based, which is appropriate, but missing pairs remain unknown. The
old reversal rule requires point gaps ≥2 points with intervals excluding zero;
that does not establish a reversal of at least 2 points. The replacement rule
must compare the entire interval with 2 points on both sides.

**Confirmed reporting bug:** `analysis.py`'s robustness `add()` obtains coverage
from all `supported` cells even after `network_index(exclude=airport)` removes
that airport. All five leave-airport rows incorrectly retain 27.60% coverage.
For example, removing Atlanta (10397) leaves 858,246 shared flights, or 21.31%
of the original candidate schedule, not 1,111,509/27.60%. If instead using the
remaining schedule as denominator, recompute that denominator too and label it.
The exclusion is applied to the fit, so this bug does not negate its ranking.

**Other limitations:** 2400 is mapped to midnight of the same date in code,
potentially moving a next-midnight departure into the wrong date; there are
zero candidate 2400 records here, so it cannot affect this pilot. Raw-to-Parquet
hashes are not separately sealed and a current-code/saved-output identity is
missing. The nearest-match implementation is mutual-nearest within the original
two-hour band, not unrestricted ±30-minute matching across a band boundary.
No evidence here certifies that sensitivity's output. No arithmetic bug was
found in the saved primary rates, direct contrasts or network coefficients.

## What survives, and where the episode turns

| Selected carrier | Completed-flight rank | Matched index rank |
|---|---:|---:|
| Alaska | 1 | 1 |
| Delta | 2 | 2 |
| American | 3 | 3 |
| Southwest | 4 | 6 |
| United | 5 | 4 |
| JetBlue | 6 | 5 |
| Frontier | 7 | 7 |
| Spirit | 8 | 8 |

The all-scheduled national ordering is the same as the completed-flight ordering
within these eight. The top three and bottom two survive the index adjustment.
Southwest's 4→6 is a point-rank description: its bootstrap rank range is 5–6,
and it trades places with JetBlue under four-hour windows, two hub omissions,
and equal-opponent weighting. More revealingly, the **direct** JetBlue–Southwest
estimate favors Southwest by 2.46 points, while the network index puts JetBlue
ahead. Its simultaneous interval includes zero. This is an excellent explanation
of why there is no single unqualified “fair table.”

The strongest concrete turn is **United versus Southwest**:

- National completed-flight difference, United minus Southwest: −1.58 points.
  With failures included for both: −1.56 points.
- Direct shared-stratum difference: **+2.95 points**, simultaneous 95% interval
  **+1.29 to +4.61**, based on 50,221 United and 48,817 Southwest flights in
  45,509 shared strata. These are the saved pilot intervals, not newly validated
  confirmatory evidence of a >2-point effect.
- On the same pair population, the exploratory common-clock difference is
  −0.68 points, interval −2.13 to +0.77. United schedules about 4.51 more minutes
  in those weighted cells. This distinguishes keeping a timetable promise from
  beating a common allowance; it does not establish intentional padding or a
  significant opposite winner. It is optional context, outside the new primary.

The “network mix explains the best–worst gap” alternative is **not supported**.
Alaska–Spirit's completed-flight gap is 16.67 points, its all-scheduled gap 17.43,
and the network-index gap 18.48: adjustment widens it. More importantly, their
direct overlap is only 129 flights per carrier and fails eligibility. Subtracting
these gaps does not identify a percent caused by network choice. A future
fixed-pair decomposition can separate population restriction from reweighting
arithmetically, but not causally. Do not select whichever confirmatory extremes
produce the biggest “percent explained.”

**Honest exploratory headline:** “In 2015, most of the eight-airline table
survived—but United overtook Southwest on comparable flights.” Put the narrow
population on screen immediately. Alaska's surviving index lead and the
coverage limit supply the second turn: a fairer comparison can retain a winner
while answering a much smaller question.

There is an episode, conditional on the new test's validation: familiar table →
same-trip comparison → Southwest/United or another preregistered pair → the
limits of a universal winner. A stable result is publishable too. Route-level
rankings and network adjustment already have precedents catalogued in r2;
dropping the common-clock requirement weakens that design's novelty claim.
Sell the transparent test and an honest answer, not the invention of adjustment.

## Exposure and handoff

The accompanying `fair-airline-METHOD.md` is a draft after 2015 exploration,
not an already committed registration or a completed simulation gate. Its
2-point scale is inherited from r2; applying it to national-versus-matched
reversals, the symmetric survival rule and revised coverage scope are new now.

For belief/source checking, I opened historical DOT and Forbes publications,
not held-out BTS files. A broad historical web search incidentally returned
a later AP ranking snippet concerning 2024; I did not open that article or use
it to select carriers, thresholds or hypotheses. Do not claim perfect blindness
to all public rankings. Historical articles also contain earlier-year context;
the only flight-level outcome data used were 2015. Direct source-byte retrieval
for new hashes returned HTTP 403; no page snapshot or invented hash is supplied
(`scratch/airline-r7-source-hashes.json`). Archive addresses and verified hashes
before production; third-party pages must stay out of public history.
