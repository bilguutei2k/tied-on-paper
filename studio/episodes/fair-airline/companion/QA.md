# Fair-airline companion QA — 2026-10-08

Status: **pre-lock draft: claims proposed**. Working title follows STORY:
“Tied on Paper.” Passing arithmetic is not editorial approval.

## Deliverables and interaction

- `build.py` and `template.html` generate the self-contained `index.html` and
  `../renders/companion/page.html`, with identical content but no document
  wrapper in the latter. Both are approximately 2.17 MB, including fonts and
  evidence downloads. No server, neighboring assets or network is required.
- One analytical selector offers **33 lenses**: registered A/B together;
  all **14** distinct registered sensitivities (including equal-year A and
  each separate source year); **4** shared-timetable checks, **2** departure
  checks, and **12** time-of-day views (ten observed two-hour bands plus the
  before-10/from-16 summaries). A/B appear together where applicable.
- Shared midpoint and departure checks show their saved descriptive intervals.
  Other shared allowances and time bands have no saved intervals; they show
  “No interval computed” and no interval mark. Nothing is imputed.
- The fixed axis covers every saved point/endpoint and includes zero and the
  registered +2-point line. All gaps remain **United minus Southwest**;
  late-departure gaps are negative when United has fewer late departures.
- Native optgroups, a dashed exploratory label and a separate panel treatment
  distinguish “Exploratory, post-hoc · not registered.” Every lens explains
  its change and says it cannot change either sealed verdict. The Paper/Night
  button is a separate display preference, with system-theme support.
- The amended question and the registered answer use the episode's words.
  Operator-only/comparable-cell/own-timetable scope precedes the headline.
  National all-flights rates and DOT operating ranks sit beside the method
  diagram on desktop, and stack on phones. Required review disclosures,
  failures, approvals and full commit hashes remain visible.
- Diagram and chart reuse the established dot/range, Ink-rule and schematic
  grammar: orange United subject, blue Southwest comparison, Field intervals,
  one mint verdict; no radius except dots, no shadow. Fonts are embedded
  Big Shoulders 800/900, Source Serif 500 and Plex Mono 400/500/600, with licences.

## Evidence binding

The verifier independently derives values from raw evidence; it does **not**
record the results.json file hash. The companion therefore explicitly binds
these current verified bytes together and checks **188** displayed bindings
against passing claim/verifier entries. It never silently refreshes pins.

- Registered results: `5ad0c9319304bb645c966aca253d00035913105b900f58b6fd8be694e66597de`
- Proposed claims: `64ae35817d333a3c90d6d8f60e43910ca72d3ca5dece581a5355561a6f24d74b`
- Claim verifier: `00dc333e379f286f42ae4cea324d7037ef490e0cd1bbdedb2ea5ff8b615cca20`
- Post-hoc results: `0a430fc236035ca94043a76cbb9e49e076f5947ed0bfd763b8cc2ab71736a959`

Temporary-copy mutation checks altered each pinned file separately. All four
builds refused before writing either output; sentinel outputs stayed unchanged.
A repeated clean build produced byte-identical outputs. All **20** embedded
evidence downloads decode byte-for-byte to their source documents. Wrapper-free
content matches the standalone head/body content after removing the wrapper.
The selected-result disclosure includes claim IDs and paths for both points
and saved intervals. Derived time-band values are explicitly sourced from the
independent verifier's claimed `derived_metrics`, not invented in the template.

## Chromium checks

Actual local headless Chromium launched successfully. No QA_TODO is needed.
`check_browser.py` records the sweep in `../renders/companion/browser-audit.json`.

- **132/132 page states pass**: all 33 lenses at 390×844 and 1440×1000, in
  Paper and Night, including expanded provenance. **33/33 fragment states**
  also pass when page.html is placed in a minimal host wrapper at phone width.
- Readouts match embedded results; every point and available endpoint has the
  correct SVG coordinate. Point-only lenses draw no interval. The reference
  and domain stay fixed, the verdict stays registered, and the exploratory
  state/labels change with the selected lens.
- Document width equals viewport width throughout. Phone gutters are exactly
  **16px**; desktop gutters **160px**. No element spills beyond either viewport.
  All selected native-option labels fit without clipping.
- Embedded faces load; zero HTTP resource requests, console messages or
  runtime errors. Static registered readouts and SVG are present without JS.
- Visual inspection passed for phone/desktop headlines and controls, Night
  post-hoc readouts, point-only time bands, and the method diagram. Keyboard
  focus styling, native select semantics, live readouts, skip link, SVG title/
  description and descriptive table headers are present.
- `git diff --check` passes. No Git writes, staging or commits were performed.

Screenshots: `390-paper.png`, `390-night.png`, `1440-paper.png`, `1440-night.png`
(full pages), plus `*-top.png`, `*-control.png`, `*-night-posthoc.png`,
`*-night-time.png` and `*-night-method.png`, all in `../renders/companion/`.
The repository's existing render ignore rules apply; generated files exist
locally at the requested paths.

## Reproduction

From the repository root:

```sh
python3 studio/episodes/fair-airline/companion/build.py

env NPM_CONFIG_CACHE=/private/tmp/scramble-companion-npm \
  AGENT_BROWSER_SOCKET_DIR=/private/tmp/fair-airline-companion-browser \
  npx --yes agent-browser --namespace fair-airline-companion \
  --executable-path /Users/bilguutei/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell \
  --args '--single-process,--no-sandbox,--in-process-gpu,--disable-gpu' \
  --allow-file-access open "file://$PWD/studio/episodes/fair-airline/companion/index.html"

python3 studio/episodes/fair-airline/companion/check_browser.py
```

## Open issues

No known layout, runtime or numerical-binding issue remains. Editorial claim
lock and the working title remain with the owner. Missing post-hoc intervals
are an evidence limit and are explicitly disclosed. This page makes no causal
padding claim, airline-choice recommendation, universal advantage, future-flight
prediction or claim that the incomplete supplemental SQL check passed.

## 2026-10-08 visual polish

Added the complete time-of-day chart in a separate exploratory section.
Both periods use connected points across all ten observed two-hour local
scheduled-departure bands. Solid zero and dashed +2 lines are references;
no exploratory verdict is assigned. The 22:00–24:00 band fades and is labelled
under 1% of comparison weight (A 0.14%, B 0.36%); no support exists before
04:00. The −0.4/+1.4 before-10:00 and +11.7/+12.9 from-16:00 annotations
remain visible. Period legends, own-timetable scope, no band intervals and
no causal/morning-flight recommendation are explicit. An expandable table
exposes all band values and weights; SVG title/description travel offline.

Added FA-C076–095 per plotted observation. The independent raw-cell verifier
passes 633/633 checks for 95 proposed claims; reviewed ledger/report pins
above reflect that passing rerun. The chart and selector use the same verified
keys, with 188 distinct page bindings. Repeated builds are byte-identical;
all 20 embedded evidence links decode to current episode source bytes.

Rebuilt index.html and portable page.html. Chromium passes 132/132 page
states (phone/desktop, Paper/Night) and 33/33 portable-fragment states. Every
state also checks all 20 chart coordinates, values, weights and fade opacity.
No overflow, runtime error, console message or HTTP resource request occurs.
Personally inspected phone/desktop chart captures and full-frame context;
chart geometry, period attribution and exploratory label are legible.
Screenshots: ../renders/companion/*-night-day-chart.png. No new open issue;
editorial lock and the disclosed absence of band intervals remain unchanged.

## 2026-10-08 visual polish 2

Time-chart periods and legend markers now use solid ink/filled dots (A) and
dashed ink/open dots (B) in both themes. Values, coordinates, sparse-band
fading and zero/+2 references unchanged. Rebuilt index.html/page.html;
Chromium passes 132 page + 33 fragment states. Phone/desktop chart and
page-end screenshots inspected; no visual defect. Narration/data unchanged.
