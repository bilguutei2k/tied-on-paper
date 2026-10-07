# Production seal

`analyze.py A` verifies committed production bytes before opening only 2023–2024.
`analyze.py B` additionally requires the committed A results before opening 2025.
All monthly raw hashes and schedule columns are verified against the frozen source.
Only UA/WN outcomes enter this narrowed comparison; the other six carriers retain
their frozen descriptive schedule support. Source IDs and all schedule counts are
retained, including failed and indeterminate services. No natural-key collisions
were present in the sealed source audit.

Production uses METHOD's **20261005** PCG64 seed. Amendment 1/2 replace the old
draw-first week order with year-first, row-major 1,999 × 14 block starts. The
20261007 SeedSequence streams are synthetic-bank streams, not a replacement
production seed. The `.npy` arrays in `data/derived/` have committed byte hashes
and regenerate with `prepare.py`; no outcome is needed for regeneration.

`intervals.py` retains the tested Amendment-2 arithmetic, exposing each assignment
and allowing one opened period at a time. The fixture reproduces the gate's A/B
intervals exactly. A's validity/quality is determined on A; B is determined on B.
This implements the separate-period decision and prohibition on B rewriting A.
The synthetic gate's whole-dataset invalidity convention is tested jointly there.

The descriptive equal-year A sensitivity averages the two annual ratios and
their resampled ratios, using corresponding linearized annual SE contributions.
All sensitivities reuse the primary sealed starts, use their frozen membership,
and report nominal 99% block ranges without a separate certification or verdict.
Annual and national census rates have exact missingness assignment ranges; these
are not confidence intervals for future flights. Exact scheduled counts and
coverage shares are census quantities, not estimated sampling populations.
Each airport omission uses the same exclusion in national and shared rates and
shows both original and retained denominators. The retired AS/NK and all-pair
inference obligations do not return.

The fixture tests production SQL against the scalar scoring rule on all 45
status/timing templates and checks invalid-value stops, strict decision equality,
cell weight expansion, array regeneration and whole-network multiplicities.
The schedule preflight verifies every sensitivity's dates fit the frozen day grid.
Results include all three points, assignment intervals, envelope, quality evidence,
saved primary draw hashes, secondary rates, excluded populations and sensitivities.
Third-party pages and row-level files are excluded from commits.
