# Tied on Paper — narrated pre-lock draft

2026-10-08 · Sol · build in progress. STORY and claims remain proposed and
unlocked. No analytical results or claim statuses changed. Renders are excluded
from commits; the owner helper owns Git writes.

Read the existing analysis progress first, then scramble-luck's narrated build,
EDIT head, DIRECTION's narrated-assembly rules, narrate.py, assemble.py, render
README and this episode's STORY, scenes README, CUES and VISUAL_QA.

## Pipeline

Use the unchanged house narrator and assembler. Episode-only spoken forms read
percentages, decimals, full-year intervals and airport/operator codes naturally;
claim tags are removed, while written cue tokens and captions stay unchanged.
Short 1/2/3 headings are aliased to the house Short A/B/C keys at parsing time.
Voice: local Kokoro af_heart, speed 1.0. Outputs target renders/draft, with
separate strict SRT captions, 30 fps landscape film and portrait shorts.
Audio target: −14 LUFS integrated, ≤−1 dBTP; retain −1.5 dBTP normalization
headroom and calibrate the encoded AAC as scramble-luck did.

## Progress

- Prepared SPOKEN_FORMS.json and episode-scoped narration adapter; no shared
  tool or STORY edit. Next: synthesize, construct word-cued edit and validate
  motion, timing, captions, transitions and measured audio; inspect frames.

## Sandbox result and completed checks

- Local af_heart synthesis attempted through unchanged narrate.py: blocked on
  MLX import, `[metal::load_device] No Metal device available`. No narration
  manifest/WAV was fabricated; no alternate voice or static-card film substituted.
- SPOKEN_FORMS.json: 15 sections / 58 lines. Natural full-year ranges, decimals,
  percentages, UA/United, WN/Southwest, DEN/Denver and LAX/Los Angeles checked;
  tags removed. Written text/caption/cue tokens preserve STORY exactly.
- EDIT: 46 film whole-line shots and four per short, 64 named-state word cues.
  Every source line occurs exactly once; gate words and ordered anchors resolve.
  Structural timing checks used synthetic word spans only in memory, never as
  narration or recorded-duration evidence. Builder recompiles with actual Kokoro
  timestamps and scramble-luck's word-range/PCM pacing after external synthesis.
- Value gates cover national rates, primary gaps and endpoints, replication,
  durations, shared allowances, departures and early/late contrasts; the short
  replication chip waits for “replicated”. Animation retains the designed speed
  and settled hold; scene changes use 450 ms wipes, within-scene fragments cuts.
- Unchanged scene suite passes all 64 animated states, data/source hashes,
  reproducible computed bindings, exact STORY substrings, seek purity and 344
  browser numeric labels. Chromium starts through offline_chrome. A fresh
  short-c late-state smoke capture matches the audited still byte for byte.
- Personally inspected native A envelope, B replication, short A result, short B
  allowance and fresh short C early/late layout. Labels, ranges, replication chip,
  sources, exploratory status and safe edges are legible. These are scene samples,
  not claimed decoded-film QA. Smoke/captures/check logs remain in renders/.

## Pending external commands and measurements

RENDER_TODO.md gives exact sequential commands for synthesis, actual-timing
EDIT/strict SRT preparation, unchanged assembler, identical scramble-luck
loudness/caption/PCM/state/whole-frame checks and decoded sample extraction.
Episode wrappers leave shared tools, scene sources, STORY and claims unchanged.
The checker and split helper reuse the scramble-luck implementations explicitly.

No MP4 or recorded SRT exists yet; measured durations/LUFS/dBTP, actual cue and
value-gate alignment, wipe/cut frames and final pacing remain pending. Expanded
speech-only estimates at 150 wpm: 1,354 words / 541.6 s film; 110 / 44.0 s short A;
123 / 49.2 s each short B/C. Layout holds are additional. Actual-timing samples
must be inspected on resume and any early/late/long-hold issues corrected.

Submitting episode-only handoff checkpoint; renders/raw/derived excluded.
