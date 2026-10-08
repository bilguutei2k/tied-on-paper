# Independent recheck

## Phase 1 (blind)

I derived these values from the registered METHOD, Amendments 1 and 2, EPISODE,
the supplied manifest, and only the 36 raw BTS ZIPs named by that manifest.  I
did not open `analysis/` results, confirmation files, derived data, or analysis
code before writing `values.json`.

`code/rederive.py` uses `ideation/.venv/bin/python`, streams CSV members in
200,000-row chunks, and uses ten worker processes (one source ZIP per task). It
keeps only rows whose reporting code and fixed DOT ID jointly identify UA/19977
or WN/19393.  Its temporary `work/` files are per-month aggregates, not
row-level extracts, and the script deletes them after combining the months.

Scoring follows the precedence in the contract: a known cancellation or
diversion fails; otherwise a flight with both flags zero and finite ArrDelay is
successful exactly when ArrDelay < 15; all other outcomes are indeterminate and
score zero.  The raw inputs produced no UA/WN indeterminate outcomes, so primary,
lower, and upper adjusted estimates coincide.

Cells use source year, directional positive airport IDs, normalized FlightDate,
and floor(scheduled-departure-minute/window).  `2400` is normalized to the next
date at minute zero; no other invalid HHMM is matched.  A is the pooled 2023 and
2024 cell basket and B is the 2025 basket.  The direct estimate is the contract's
sum of `(n_UA+n_WN)/2` times the within-cell UA-minus-WN mean difference divided
by the sum of those weights.  The one- and four-hour sensitivities rebuild cells
and their weights at their respective widths.

The reported all-flights rates are the unadjusted, all-scheduled rates (the
natural reading of “unmatched all-flights”); they include every identified UA or
WN raw row, including rows without a matchable schedule key.  `values.json`
states an `n` and one-line definition for each statistic.

For Amendment 2's A interval, I implemented the 28-day circular block,
studentized procedure with 1,999 draws, all calendar days in each source year,
and source years drawn 2023 then 2024.  Amendment 2 changes only the interval;
it does not give a production seed.  I therefore retained METHOD's production
PCG64 seed `20261005`, generating each year's complete row-major `(1999, q+1)`
start matrix before the next year.  The t floor binds in both tails, yielding
the primary/envelope interval saved in `values.json`.

Interpretation: because frozen official airport metadata was not among the
permitted blind inputs, I treated a raw airport ID as valid when it is a finite,
positive integer; I did not merge IDs.  That is the only material operational
interpretation beyond the supplied files.  The one existing airport identity
requirement otherwise cannot be independently checked from the allowed inputs.

## Phase 2 comparison

`compare.py` maps the saved recheck keys to `analysis/results.json`; it compares
counts exactly and proportions, interval endpoints, and SEs at an absolute
tolerance of `1e-9` (all Sol percentage-point fields are converted to
proportions first).  The resulting `compare.json` records 47 comparisons: all
47 match and there are no mismatches to investigate.

Five weight sums and six bootstrap pivotal quantiles remain unmapped because
Sol's public `results.json` does not expose those internal diagnostics.  They
are recorded in `values.json`, but their absence is not a numerical discrepancy.
