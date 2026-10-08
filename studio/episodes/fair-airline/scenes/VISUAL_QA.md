# Visual QA — proposed, pre-lock draft

PASS · Sol · 2026-10-08. Open visual issues: none.

All 64 settled cue states were rendered with the unchanged studio renderer
and personally opened as native-resolution PNGs: 52 at 1920×1080 and 12 at
1080×1920. All initial captures were inspected; the 17 changed captures were
reinspected after corrections, followed by the final replication badge.
The other final captures have unchanged image hashes. `visual_qa.json`
records the inspected final PNG hashes, dimensions and state IDs. Renders
and their provenance sidecars remain in the episode's uncommitted renders/.

| Pages | Cues | Delivery review |
| --- | ---: | --- |
| S01 / S02 / S03 | 4 / 4 / 3 | National tie, scoring and mixed basket clear |
| S04 / S05 / S06 | 4 / 4 / 5 | Comparable-cell, materiality and failed gates clear |
| S07 / S08 / S09 | 5 / 5 / 3 | A/B envelopes, sealed A and sensitivity clear |
| S10 / S11 / S12 | 5 / 4 / 6 | Minutes, departure, scope/time and ending clear |
| Short A / B / C | 4 / 4 / 4 | Independent stacked portrait compositions clear |

Checked clipping, safe edges, actual font shapes, text/shape overlap,
contrast, numeral/unit attribution, source and scope legibility. Landscapes
retain 96px edges. Portrait information stays inside x=72–920, y=220–1500.
No logos, airline brand colours, radius or shadows. Paper/Night, Plex Mono,
Ink rules and local grain follow the system; mint marks only registered
decisive conclusions. Exploratory panels carry the visible
EXPLORATORY · POST-HOC · NOT REGISTERED label.

Corrections verified in final captures:

- Separated bar labels and value lanes; tightened landscape row spacing.
- Separated SEALED from A's period name; retained A's envelope during B's reveal.
- Limited chart rules to diagram lanes, clear of endpoint/envelope captions.
- Added a claim-bound zero reference; kept A/B on the same unrounded domain.
- Restored Night stamp contrast and Night conclusion/evidence cards.
- Kept portrait period ranges together and added contrast/unit attribution.
- Moved the replication badge above the source rule with visible clearance.

`browser_qa.json`: 64 states, zero safe-edge/overlap/card/font/clearance
flags and zero runtime errors. It records episode/shared source hashes to
reject stale audits. `check_scenes.mjs`: all 64 states animate, exact STORY
cue substrings, arbitrary seek purity, regenerated data equality, source
hashes and 344 visible numeric labels pass. PNG/sidecar/page/data hashes and
delivery dimensions also pass.

Numbers come only from claim-bound computed result keys; the ledger supplies
IDs and proposed status. README documents the primary/review results and
the independent verifier's computed design, Denver and grouped-time values.
No claims were locked or analysis rerun. Scope labels distinguish operating
services, own timetable, small overlap, excluded Express and exploratory
denominator/subset limits.

Timing remains a designed pre-lock clock. Recorded-narration cue alignment
and final editorial timing follow script lock; they are not visual defects.
Chromium launched successfully in the sandbox; no external render handoff
or RENDER_TODO is required for these stills or the browser audit.
