# Tied on Paper — narrated pre-lock draft

2026-10-08 · Sol · rendered and checked. STORY and all claims remain proposed
and unlocked. No analytical results changed. Renders are excluded from commits;
the owner helper owns Git writes.

## Narration and reproducible build

Claude completed the Metal-dependent Kokoro af_heart synthesis at speed 1.0;
see ideation/logs/fa-render.log. This resume used those real WAVs and word times.
No new synthesis or Metal access was needed. Episode spoken forms expand
numbers, years and airport/operator codes; written captions preserve STORY.
The unchanged house assembler renders animated HTML at 30 fps, landscape film
and portrait shorts, through the episode's offline_chrome wrapper.

With the existing narration cache, from the workspace root:

```sh
.venv/bin/python studio/episodes/fair-airline/build_narrated_edit.py
.venv/bin/python studio/episodes/fair-airline/prepare_narrated.py
.venv/bin/python studio/episodes/fair-airline/render_narrated.py
.venv/bin/python studio/episodes/fair-airline/check_narrated.py
python3 studio/episodes/fair-airline/sample_narrated.py
```

The sampler uses system Python's Pillow; the project venv lacks Pillow. Its
FFmpeg selection coalesces consecutive frames and balances the expression tree
rather than exceeding FFmpeg's expression-depth limit. It clears its own old
numbered samples/sheets before extraction so shorter cue lists are safe to rerun.
Individual affected outputs can be passed to render_narrated.py. Cached shots
are reused. All four were rerendered after shared episode layout changes; only
film and short-a were rerendered after the final opening-layout pacing fix.

## Assertion diagnosis and edit fixes

The reported film state was genuinely one frame late, not a different
jump_from convention. The second “fifteen” in shot 7 landed at local
5.166666667 seconds, exactly frame 155. Rounding its anchor to 5.167 left the
rendered clock at 6.95 on that frame and switched to 7 on the next. The builder
now adds a −0.000666667-second offset after PCM bridges determine the effective
lead, producing the representable 5.166 anchor. The renderer and checker retain
the same convention and the state checker arithmetic is unchanged.

State-zero cues are starting layouts, not jumps from a settled clock. Redundant
word cues on these starts also caused spurious “late state” reports on later
fragments and held several opening bodies empty for five to eight seconds.
Starting layouts now animate from the lead-in and later fragments retain their
settled hold. Independent spoken-value gates remain in place. Forty-nine
nonzero word transitions remain: 40 film and three per short.

The film closing hold gains one frame, from 0.900 to 0.933333333 seconds. Its
total ends on a three-frame/100-ms boundary, avoiding the extra terminal frame
created by the house panel source's millisecond duration formatting. No shared
assembler change was needed.

## Checker convention: intentional panel wipes

The imported scramble-luck checker was written for an all-cut edit and treats
any low-variance frame as blank. This film follows DIRECTION's 450-ms panel
wipes, including deliberate full covers. check_narrated.py is now an episode
fork with the original caption, PCM, audio, frame-count and state checks intact.
Only its blank-frame test recognizes independently verified planned covers:
inside a scheduled wipe, at least 97% predicted cubic-eased coverage, and every
interior pixel within three grayscale levels of the expected house panel.
Wrong time, wrong panel, black, insufficient coverage and corrupted interior
fixtures all reject; the valid planned panel passes. The decoded film contains
13 intentional cover frames and zero unexpected blanks. Shorts have no wipes.
The shared checker and all shared tools are unchanged. Reference checker SHA256:
`d1a5d9390dbb5450dfc75a966b0b333704f8aa85c29752d40da1c7ba8bf768a5`.
Fixture evidence: renders/qa/resume/wipe-guard-fixtures.json.

## Visual corrections and verification

Episode headers stay settled under the house __narratedAssembly flag while
chart clocks retain their motion. Verdict chips enter at their state cue; the
short replication gate still waits for “replicated”. Short A's neutral
“A separate test” heading avoids announcing replication before the spoken
result. Its endpoint/confidence labels are gated together until “envelopes”,
preventing dangling TO/PP text. Short C now uses period-labelled series and spoken-summary annotations.
Sources remain visible through state changes; full panel wipes intentionally
cover the whole layout for their brief transition.

The browser audit checks all 64 named-state onsets for settled visible headings,
visible sources and immediate ungated verdicts. Scene checks pass all 64 states,
375 numeric labels, current source/data hashes, computed bindings and seek
purity, with zero geometry or runtime issues. Claim statuses are unchanged.

## Final delivery measurements

Measured from the delivered MP4s, not speech-rate estimates. Film is
1920×1080; shorts are 1080×1920; all use H.264/AAC at 30 fps.

| Output | Duration (s) | Frames | Shots | SRT cues | LUFS | dBTP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| film | 636.300 | 19,089 | 68 | 161 | −14.0 | −1.1 |
| short-a | 57.233 | 1,717 | 6 | 16 | −13.9 | −1.1 |
| short-b | 59.100 | 1,773 | 6 | 15 | −14.0 | −1.2 |
| short-c | 57.467 | 1,724 | 6 | 16 | −13.9 | −1.1 |

Final check_narrated.py PASS for all four outputs: 24,303 decoded frames,
zero unexpected blanks, zero early/late state failures, exact cached PCM,
zero source clipping, no omitted/reordered/duplicated narration words, and
zero caption text/order/endpoint failures. Captions use at most two rows and
42 characters per row (41 for A/C). Word counts: 1,240 / 100 / 108 / 110.
Forty-nine state transitions and 44 effective value-gate records reconcile
with the current edit/preflight. Evidence: renders/qa/assembled/checks.json,
resume/check-final.log and the four ebur128 logs.

Maximum post-word holds are 2.050 / 1.008 / 1.008 / 1.017 seconds; longest
word gaps are 2.725 / 1.675 / 1.700 / 1.692 seconds. Film shot durations span
6.000–13.667 seconds; short minimums are 6.267 / 8.333 / 8.200 seconds.
The final frame and closing evidence layout are present; no extra terminal
cover frame, cramped cut or excessive silent hold remains.

## Personal decoded-frame inspection completed

After the usage-limit resume, Sol inspected every final contact sheet:
film sheet-01 through sheet-63 and sheet-01 through sheet-06 for each short.
These represent 995 film samples and 87 per short (1,256 total), with sample
frame numbers/times in renders/qa/decoded/manifest.json. Native 1920×1080
and 1080×1920 PNGs were also opened directly, including these gate pairs:

- Film A lower/upper endpoints: frames 9816→9817 and 9867→9868
  (4.60 first visible at 327.233 s; 7.94/bar at 328.933 s).
- Film B lower/upper endpoints: frames 11216→11217 and 11266→11267
  (5.31 at 373.900 s; 11.00/bar at 375.567 s).
- Film 2025 reveal/seal: frames 11076 and 11153; replication badge
  frames 11528→11529 (absent at 384.267 s, present at 384.300 s).
- Short A: frames 955→956, 1115→1116 and 1180→1181 for the B value,
  envelope labels/bars and replication badge; its A reveal is also sampled.
- Short B: frames 289→290, 414→415, 518→519 for schedule and actual
  values; 1025→1026 and completed frame 1160 for the shared allowance.
- Short C: frames 703→704, 822→823, 963→964 and 1009→1010 for
  all four early/late values, including the −0.4 sign and period spacing.
- Wipes: all before/cover/after sheet groups; native film frames 1462,
  1463 and 1470 confirm the planned contrasting panel and clean uncover.

No early numerical reveal, disappearing heading/source outside planned
panel coverage, clipped result or unresolved transition defect was found.
State changes replay chart entrances while headings/sources remain settled;
values become eligible at their word gate and still obey chart entry motion.
Native endpoint and settled-short gates above show hidden values on the
preceding frame and visible values on the first permitted frame.

Current plan starts/durations, anchors and gates were compared to the final
checked timing-preflight; all match exactly. All four MP4 SHA256s match their
delivery JSON, STORY/data hashes match, and browser_qa.json source hashes
remain current. Synthesis was not repeated. The visual-polish pass below reruns assembly,
checker and sampler against the final scene sources. No Metal work remains; RENDER_TODO removed.
No delivery blocker remains. STORY/claims still require owner publication
lock; optional listening for voice prosody was not performed or claimed.

## 2026-10-08 visual-polish delivery

Reassembled film and Shorts A/B/C with render_narrated.py through the
unchanged studio/tools/assemble.py and existing cached narration. STORY,
recorded WAVs, word times, edit clocks, SRT wording and synthesis are unchanged.
No Metal re-narration or RENDER_TODO handoff is needed. All 86 shot cache keys
match the final episode dependencies; all four output hashes and STORY/data
hashes match their delivery metadata. Renders remain uncommitted.

S03 now has proportional inside/outside coverage splits. S04 and Short A
use the explicitly schematic DEN → LAX / 15 January 2025 schedule timeline;
the reverse row is outside the highlighted cell. S12 and Short C plot both
periods over all observed two-hour bands, with fixed zero/+2 references,
faded under-1% bands and period-labelled spoken-summary annotations.
Portrait headlines/values and scope placement use y=180–1632, leaving the
bottom 15% for platform UI. Geometry-key gates include attached units and
period labels, so held layouts do not leave bare units or separators.

The final check_narrated.py rerun passes all four outputs: 24,303 decoded
frames, zero unexpected blanks, zero early/late state failures, exact cached
PCM, zero source clipping, exact narration word order and correct captions.
Durations, frame counts, shots, SRT cues and loudness remain the measurements
in the table above. All claims remain proposed; independent verification is
633/633 checks for 95 claims. Scene/browser QA passes 64 states, 375 numeric
labels and 100 independently checked plotted band points.

sample_narrated.py regenerated 995 film samples and 87 per short (1,256 total).
Reviewed changed-scene and portrait decoded layouts on inspection sheets,
including 36 additional native settled-shot frames, plus native spoken-value
and verdict gate frames. Film's complete time chart and both portrait periods
fit without clipping. Short C's −0.4 reveal and final four annotations, Short
B's completed shared-allowance chart and Short A's replication reveal were
inspected at the actual decoded frames. No visual or timing defect remains.
Evidence: renders/qa/assembled/checks.json, renders/qa/decoded/manifest.json,
renders/qa/polish-decoded/, and the updated scenes/VISUAL_QA.md.

Companion rebuilt and passes 132 page + 33 portable-fragment browser states,
including every chart coordinate/weight/fade check. QA notes and reviewed
ledger/verifier pins are current. Editorial lock, the explicitly schematic
ticks and absent exploratory band intervals remain the disclosed limits.
