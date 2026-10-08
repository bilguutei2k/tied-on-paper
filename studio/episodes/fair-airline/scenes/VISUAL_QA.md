# Visual QA — proposed, pre-lock draft

PASS · Sol · 2026-10-08 visual polish after Claude review. No open visual defect.

Re-rendered the 25 cue stills for S03, S04, S12 and Shorts A/B/C with the
unchanged house renderer. Reviewed all 25 in film/portrait sheets and inspected
changed compositions as native PNGs. Twenty-one image hashes changed; the
other 43 episode captures retain the previous inspected hashes. The current
64-state inventory and source hashes are in visual_qa.json. Renders stay local.

- S03 uses equal-length 100% bars split into inside comparable cells and
  outside: United 11.9%, Southwest 6.2% in 2023–2024, bound to FA-C006.
- S04 and Short A show a local day axis, two-hour guides, operator departure
  ticks, and a highlighted 10:00–12:00 cell. The reverse-direction row stays
  outside the highlight and is labelled DIFFERENT CELL. DEN → LAX and
  15 January 2025 identify the teaching example; ticks are explicitly
  SCHEMATIC, with no observed flight pair or outcome asserted (FA-C005).
- S12 and Short C plot every observed two-hour band for both periods on one
  −2 to +16-point domain. Solid zero and dashed +2 references stay fixed.
  The 22:00–24:00 points/segments fade: A 0.14%, B 0.36% of comparison weight.
  The no-support-before-04:00 note and exploratory/post-hoc/not-registered
  label remain visible. Period symbols and labels identify both series.
- Spoken summaries stay visible as annotations: −0.4 / +1.4 before 10:00,
  +11.7 / +12.9 from 16:00. Existing narrated word gates remain intact; each period label/unit is
  gated with its value, preventing bare separators or units during holds.
- Portrait headlines grew from 88 to 108px; bar/range values grew to 54/64px.
  Charts occupy the middle third and scope strips begin at y=1390. Important
  content remains within x=72–920, y=180–1632, above the bottom 15% UI area.
  The shared house files and landscape 96px edges remain unchanged.

Corrected S12's axis-caption/annotation collision found by PNG inspection.
The browser audit now distinguishes actual element owners, so equal-top
labels cannot hide overlaps. It independently checks all 100 plotted band
points across five states against claim-bound values, coordinates and fading.
Exploratory labels are static above chart layers throughout state changes.

Validation: 95 proposed claims, 633/633 independent numeric checks; fresh raw
archive scoring and normalized band sums pass. Scene checks: 64 animated
states, reproducible bindings, exact narration cues, arbitrary seek purity,
375 visible numeric labels. Chromium: 64 settled states and 64 narrated
onsets, zero geometry flags, zero runtime errors, all band points passing.

Narration audio, STORY wording, edit clocks and claim statuses are unchanged.
No re-narration or Metal handoff is required. Editorial lock remains open;
schematic ticks and missing exploratory intervals are disclosed evidence limits.

## 2026-10-08 visual polish 2

PASS. Time-chart A is solid ink/filled dots; B is dashed ink/open dots in
S12, all three Short C chart states and the companion, including legends.
The faded 22–24 band and zero/+2 references retain their treatment. Short A’s
four coverage bars now sit on equal beige 100% tracks, retaining carrier colors.

Inspected all 14 regenerated cue stills, native changed compositions, 104
decoded samples on seven sheets, film chart frame 18300 and native final
frames film 19088, A 1716, C 1723. Companion phone/desktop chart and page-end
captures inspected. No clipping, legend clash or missing track remains.
Scene/browser: 64 states/375 labels PASS; companion: 132 + 33 states PASS.
Narrated checker passes all 24,303 frames; sampler regenerated 1,256 samples.
All three rebuilt encoded audio streams are byte-identical to pre-edit audio.
Evidence: ../renders/qa/polish2-inspection/ and polish2-audio-comparison.json.
