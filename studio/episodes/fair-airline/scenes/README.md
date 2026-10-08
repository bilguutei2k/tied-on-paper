# Tied on Paper — pre-lock animated draft

Twelve STORY landscape scenes (1920×1080) and three independently composed
portrait shorts (1080×1920). Claims remain proposed and numerically verified;
no editorial lock or recorded-voice timing is implied. CUES.json uses exact
narration substrings and designed clocks with settled holds. Each HTML is a
pure time function through the unchanged shared FT clock.

`build_data.py` binds numeric labels to claim IDs, keys and source hashes.
Primary observations: analysis/results.json. Exploratory duration/departure:
analysis/review_checks/results.json. Design, Denver and grouped time values:
computed derived_metrics in the independent analysis/claims_check.json result
artifact, whose ledger hash and all-pass result are checked. The ledger's
stated values are never read as data. Only claim-bound keys enter data.js.

Episode adaptations recorded here before renderer use (DIRECTION's token and
grammar rule; no changes to shared house files):

- **National pair bars + operating-row table.** Zero-based paired orange/blue
  bars use equal axes; adjacent ranks stay annual operating rows, never
  marketing networks. Names accompany both contrast roles; no brand styling.
- **Comparable-cell and common-weight diagrams.** Q cards + Ink route/date/
  window rules; clearly SCHEMATIC, no invented flight records. Direction,
  scheduled day/window, pooled schedule-count weights and excluded trips get
  distinct cues. Window numerals bind to the definition claim.
- **Nominal envelope against materiality line.** N-style exact observed dot
  and unrounded endpoints on one linear domain including zero and the
  two-point rule. Endpoint labels use a separate lane. A seals before B;
  one mint chip only for the registered decisive conclusion. Caption names
  nominal missingness envelope, own timetable and fixed-schedule variability.
- **Failed-gate chronology.** Q cards: FAIL / FAIL / REDESIGN / FRESH PASS /
  OUTCOMES CLOSED, with selection and independent validation separate.
  No implication that schedules or public rankings were unseen.
- **Schedule-versus-actual minutes strip + own/shared allowance bars.** Matched
  duration contrasts and completed-cell subset coverage remain adjacent.
  Shared allowance is elapsed from each scheduled departure, not a shared
  wall-clock deadline. No deliberate-padding inference or verdict badge.
- **Departure-gap bars.** Observed late departures have all scheduled flights
  as denominator; cancellations excluded from numerator. Timely-departure
  score separately includes cancellations as failures; diversions eligible.
- **Coverage splits and schedule timeline.** S03 shows the claimed fraction
  inside comparable cells against the remainder on equal 100% bars. S04
  names DEN → LAX, 15 January 2025; all ticks are SCHEMATIC and outcome-free.
  The highlighted forward cell excludes the separate reverse-direction row.
- **Denver weight bar and time-of-day bands.** Comparison-weight share,
  not route count or passenger share. All observed two-hour bands use local
  scheduled
  departure time and retain period names. Solid zero/dashed +2 references,
  faded under-1% bands and early/late spoken annotations stay visible. New
  per-band claims FA-C076–095 are independently rescored. Exploratory panels
  carry
  EXPLORATORY · POST-HOC · NOT REGISTERED and never mint.

Paper/Night, Big Shoulders, Plex Mono labels, Source Serif captions, Ink
rules, local grain, no radius/shadows/logos. Portraits stack within x=72–920,
y=180–1632 (bottom 15% reserved for platform UI); landscapes within 96px edges.
Source/scope stays visible.

Narrated assembly uses the house `__narratedAssembly` flag only to keep
headings settled across word-cued state switches and place verdict chips on
their state cue. Chart animation retains the original clock. Short A uses
the neutral “A separate test” heading; its envelope labels and replication
chip have independent spoken-word gates. Short C separates period series and spoken-summary annotations.
Value gates include their attached period labels and units.
The browser audit also checks heading/source/badge visibility at all 64
narrated state onsets; the existing still-clock audit remains intact.

Run from repository root:

```sh
python3 -B studio/episodes/fair-airline/scenes/build_data.py
python3 -B studio/episodes/fair-airline/scenes/build_scenes.py
node studio/episodes/fair-airline/scenes/check_scenes.mjs
python3 -B studio/episodes/fair-airline/scenes/render_stills.py
python3 -B studio/episodes/fair-airline/scenes/render_stills.py --audit-only
```

PNG inspection and browser status are recorded in VISUAL_QA.md. Renders are
excluded from commits. No voice synthesis is needed for this pre-lock stage.
