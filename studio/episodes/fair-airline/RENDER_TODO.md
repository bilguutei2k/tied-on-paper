# Outside-sandbox narrated draft handoff

Blocker confirmed 2026-10-08: `.venv/bin/python .../narrate_episode.py` reaches
house narrate.py, then MLX import fails with `[metal::load_device] No Metal
device available`. No synthesized WAVs or narration.json were produced.
Chromium works through the episode's offline_chrome wrapper; a fresh portrait
smoke frame matches the previously audited PNG byte for byte.
Do not replace animated scene HTML with static cards. Keep claims proposed.

Run these exact commands from `/Users/bilguutei/Documents/ChatGPT/operator`
in a macOS session with Metal access, sequentially; stop on any failure:

```sh
.venv/bin/python studio/episodes/fair-airline/narrate_episode.py --voice af_heart --speed 1.0
.venv/bin/python studio/episodes/fair-airline/build_narrated_edit.py
.venv/bin/python studio/episodes/fair-airline/prepare_narrated.py
.venv/bin/python studio/episodes/fair-airline/render_narrated.py
.venv/bin/python studio/episodes/fair-airline/check_narrated.py
.venv/bin/python studio/episodes/fair-airline/sample_narrated.py
```

The first command delegates synthesis to studio/tools/narrate.py with this
episode's spoken forms and Short A/B/C aliases. The second recompiles EDIT
from actual word durations, using scramble-luck's cached-PCM splitting. The
third writes actual-timing strict captions and the timing QA plan. The fourth
runs unchanged studio/tools/assemble.py, --jobs 4, --out-dir .../renders/draft,
inside the same disposable offline Chromium environment as scramble-luck.
The fifth runs scramble-luck's identical delivery checker against this episode.
The sixth extracts before/at/after frames at cue, gate, shot and wipe boundaries.

Expected outputs: renders/draft/{film,short-a,short-b,short-c}.{mp4,srt,json};
Kokoro WAVs/word timing in renders/audio; timing-preflight.json, assembled
checks.json/audio logs, decoded frames and contact sheets in renders/qa.
All renders remain uncommitted.

Resume Sol with NARRATED_BUILD.md and analysis/PROGRESS.md. Personally inspect
all renders/qa/decoded/*/sheet-*.jpg and open key native frames (both primary
endpoints, B reveal, replication badge, all three short value reveals, wipes).
Resolve any early values, headings/source disappearance, long holds or cramped
cuts; rerender affected outputs and rerun checks. Report measured durations,
LUFS/dBTP, caption counts, exact state/gate alignment and transition quality.
Optional listening for prosody is separate from these automated checks.

Current EDIT is reviewable whole-line cue planning, not measured delivery.
Speech-only estimates at 150 expanded words/minute: film 9:01.6; shorts A
0:44.0, B 0:49.2, C 0:49.2. These omit lead/gaps/tails and are not Kokoro timings.
Actual audio, measured total durations, timed SRTs, loudness and decoded-video
QA remain pending. No synthetic timing or substituted voice is a deliverable.
After successful QA update build/progress and commit the episode sources with
the owner helper; remove or mark this TODO completed. Publication lock is pending.
