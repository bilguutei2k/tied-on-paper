# Fair airline — production context

Research: 2026-10-07, after A and B were sealed. This memo supplies publication and network context; it cannot change either verdict. Pages were read online and were not saved. The source-table extract below contains numeric aggregates only, not a page/PDF snapshot or third-party article. Episode evidence: [FINDINGS](FINDINGS.md), [blind recheck](../recheck/RECHECK.md), [methods review](reviews/astra-methods-1.md), and [post-hoc raw audit](review_checks/README.md).

## What DOT publishes

The Department of Transportation's Office of Aviation Consumer Protection publishes the monthly Air Travel Consumer Report (ATCR), with flight-performance data collected by BTS. Its consumer purpose is explicit. February reports include the preceding full calendar year. Reporting covers domestic nonstop scheduled services, including US territories; these are flight operations, not passenger journeys. [DOT ATCR overview](https://www.transportation.gov/resources/individuals/aviation-consumer-protection/air-travel-consumer-reports-2025).

A flight is on time when it operates strictly less than 15 minutes after the carrier's published CRS schedule: exactly 15 minutes late fails. Cancelled and diverted scheduled operations are retained in the reported-operation denominator and are not timely arrivals. Cancellation tables separately report scheduled operations and cancellations. Do not claim the national tables discard cancellations, or confuse a completed-flight rate with the all-scheduled rate. [February 2026 ATCR, explanation and Tables 1C/1D/6](https://www.transportation.gov/sites/dot.gov/files/2026-03/February%20%202026%20ATCR.pdf); [BTS reporting-field dictionary](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ).

Operating-carrier tables identify the airline actually flying the service. Marketing-network tables combine a brand's own operations with its branded codeshare partners. For example, the United network includes regional operators flying as United Express; the registered UA/19977 comparison excludes them and other codeshare operators. Table 1C is the annual marketing-network ranking (printed page 9); Table 1D is the annual operating-carrier ranking (printed page 10). A brand-wide rank must not label our mainline-only matched result. [February 2024 ATCR](https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202024%20ATCR%20revised%203-06-2025.pdf).

## Published annual comparison

Percentages below are published rounded rates, not confidence intervals. All six operating UA/WN counts and rates reconcile with our source records. The unadjusted national rates compare each operator's whole reported network; the registered common basket covers only overlapping route/date/departure-window cells.

| Service year | Operating UA: rank / on time / scheduled flights | Operating WN: rank / on time / scheduled flights | Marketing UA: rank / on time | Marketing WN: rank / on time | Official annual tables |
|---|---|---|---|---|---|
| 2023 | 8 / 78.07% / 732,212 | 9 / 77.25% / 1,438,465 | 4 / 78.47% | 5 / 77.25% | [February 2024, revised](https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202024%20ATCR%20revised%203-06-2025.pdf) |
| 2024 | 6 / 78.60% / 760,451 | 7 / 78.57% / 1,419,419 | 3 / 79.14% | 4 / 78.57% | [February 2025](https://www.transportation.gov/sites/dot.gov/files/2025-03/February%202025%20ATCR.pdf) |
| 2025 | 5 / 77.65% / 795,271 | 4 / 77.76% / 1,391,885 | 6 / 76.87% | 3 / 77.76% | [February 2026](https://www.transportation.gov/sites/dot.gov/files/2026-03/February%20%202026%20ATCR.pdf) |

United already leads Southwest in the operating tables for 2023 and 2024. Only 2025 swaps their adjacent operating positions. The film cannot narrate a national-versus-comparable reversal in both periods.

## Rankings as consumer advice

These are examples of the belief being used, not evidence that the advice identifies a causal airline-choice effect.

- NerdWallet's *Avoid Airline Cancellations: How to Book Better*, read 2026-10-07, presents a DOT punctuality table under a subsection about knowing which airlines arrive on schedule, and explicitly recommends airlines to book or skip when timeliness matters. The article's displayed period differs from our completed annual tables; do not reuse its numbers as our annual rates. [Article](https://www.nerdwallet.com/travel/learn/avoid-airline-cancellations).
- Sean Cudahy's *The most on-time airlines (and airports) in the world in 2025*, The Points Guy, published 2026-01-02, calls the Cirium rankings information to consider when booking flights, then compares global and regional carriers. Cirium's eligibility and denominator differ from DOT's; this is a second example of consumer interpretation, not a reconciliation source. [Article](https://thepointsguy.com/news/most-on-time-airlines-airports-in-world-2025/).

## Denver and the networks

Denver is a United domestic hub; United describes its hub-and-spoke network and identifies Denver among its hub cities. [United investor relations](https://ir.united.com/).

Denver is a Southwest crew base, while Southwest describes a primarily point-to-point network that also uses core stations and intentional connections; “point-to-point” does not mean no connecting traffic or no concentration. [Southwest crew bases](https://careers.southwestair.com/us/en/flight-attendants), [Southwest annual report filed 2025-02-07, route structure](https://www.southwestairlinesinvestorrelations.com/sec-filings/all-sec-filings/content/0000092380-25-000024/0000092380-25-000024.pdf).

## Visual notes

Show a simple annual table with separate operating and marketing labels; carry “United-operated; Express/codeshares excluded” beside the matched comparison. Use an original directional-route map, with Denver and the overlap coverage visible. Route endpoints count twice in airport summaries, so airport contributions cannot be stacked into a total.

Show the own-timetable gap and nominal 99% envelope against the two-point line, separately for A and B. Introduce the shared elapsed-time allowance and departure contrasts in a distinct panel labeled “post-hoc / not registered”; the common allowance starts at each flight's scheduled departure. Do not draw a literal common arrival clock, a causal padding percentage, or a new verdict badge. Put scheduled and actual durations side by side, with the actual-duration completed-cell restriction visible.

Use early/late-day panels and all observed months to communicate heterogeneity. Show the unadjusted all-flights near-equality alongside small comparable coverage and Denver concentration. Keep source links in captions; use original typography/maps/charts, not article screenshots or copied page layouts. Claims remain proposed pending editorial approval; passing arithmetic does not approve narration.

## Numeric source table for marketing-rank verification

The following is our aggregate extraction of all ten rows of official annual Table 1C, checked online on 2026-10-07 against the reports linked above. It lets the verifier rank the complete published table independently of the proposed claim's rank. Operating ranks and rates are independently reconstructed from all reporting operators' raw records. Marketing percentages are source facts, not a reconstruction from the reporting-carrier microdata; their published precision is retained. Direct Python access to the DOT PDFs returned HTTP 403, so the online source extraction is used. This is a numeric derived table, not saved page content.

<!-- DOT_MARKETING_NUMERIC_START -->
2023 {"HAWAIIAN AIRLINES":{"n":80967,"rate_pct":75.2},"DELTA AIR LINES NETWORK":{"n":1484394,"rate_pct":83.52},"UNITED AIRLINES NETWORK":{"n":1297988,"rate_pct":78.47},"SOUTHWEST AIRLINES":{"n":1438465,"rate_pct":77.25},"ALASKA AIRLINES NETWORK":{"n":385945,"rate_pct":81.06},"ALLEGIANT AIR":{"n":115539,"rate_pct":73.37},"AMERICAN AIRLINES NETWORK":{"n":1759176,"rate_pct":78.88},"SPIRIT AIRLINES":{"n":263871,"rate_pct":69.51},"JETBLUE AIRWAYS":{"n":274852,"rate_pct":67.08},"FRONTIER AIRLINES":{"n":177542,"rate_pct":66.99}}
2024 {"HAWAIIAN AIRLINES":{"n":78530,"rate_pct":83.58},"DELTA AIR LINES NETWORK":{"n":1541707,"rate_pct":82.02},"UNITED AIRLINES NETWORK":{"n":1364270,"rate_pct":79.14},"SOUTHWEST AIRLINES":{"n":1419419,"rate_pct":78.57},"ALASKA AIRLINES NETWORK":{"n":405118,"rate_pct":77.43},"ALLEGIANT AIR":{"n":117210,"rate_pct":76.77},"AMERICAN AIRLINES NETWORK":{"n":1910725,"rate_pct":75.91},"SPIRIT AIRLINES":{"n":261103,"rate_pct":74.48},"JETBLUE AIRWAYS":{"n":240282,"rate_pct":73.06},"FRONTIER AIRLINES":{"n":208624,"rate_pct":69.5}}
2025 {"HAWAIIAN AIRLINES":{"n":80084,"rate_pct":81.95},"DELTA AIR LINES NETWORK":{"n":1626898,"rate_pct":79.26},"SOUTHWEST AIRLINES":{"n":1391885,"rate_pct":77.76},"SPIRIT AIRLINES":{"n":194515,"rate_pct":77.25},"ALASKA AIRLINES NETWORK":{"n":422375,"rate_pct":77.24},"UNITED AIRLINES NETWORK":{"n":1467730,"rate_pct":76.87},"ALLEGIANT AIR":{"n":130899,"rate_pct":74.46},"AMERICAN AIRLINES NETWORK":{"n":1992906,"rate_pct":73.52},"JETBLUE AIRWAYS":{"n":231413,"rate_pct":72.34},"FRONTIER AIRLINES":{"n":198065,"rate_pct":70.68}}
<!-- DOT_MARKETING_NUMERIC_END -->
