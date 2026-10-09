# Tied on Paper — claims locked; publishing approval PENDING

The owner reviewed cfa8238 and asked to continue. **No owner claims/title or
publishing approval is recorded by this build.** TITLE.json is the sole title
configuration. All 95 claims remain proposed. Historical method/outcome-access
approvals remain historical. No public history rewrite, push or upload was run.

## Candidate outputs

`renders/final-candidate/film.mp4` (636.300 s), `short-a.mp4` (57.233 s),
`short-b.mp4` (59.100 s), `short-c.mp4` (57.467 s), with corresponding SRTs and
assembly manifests. Audio is reused unchanged. Locked-display companion:
`companion/index.locked-preview.html`; normal `index.html` retains draft status.
Candidate display is controlled by FA_LOCKED_PREVIEW=1, never ledger writes.

`analysis/final-candidate-manifest.json` freezes all 64 cue-still SHA-256s.
`renders/qa/final-candidate/` contains measured and decoded-frame evidence.
Final measurements and inspection are recorded in NARRATED_BUILD.md and
companion/QA.md. A changed title or any pixel mismatch requires refreshed
candidates and QA; do not move a mismatching candidate to final.

## Exact owner-approval sequence for Claude

Run from the workspace root. Only execute step 1 after the owner explicitly
approves the claims and final title. Publishing remains a separate owner action.
No default approver/date is inferred by the script.

```sh
python3 studio/episodes/fair-airline/analysis/lock_claims.py \
  --approver '<owner-supplied approver>' --date '<YYYY-MM-DD>'
# Optional final title: add --title '<approved title>'. Otherwise TITLE.json is used.
```

The command records the scramble-luck per-claim approved object (by/date,
gate=publication, house note), plus the same top-level lock note; sets verified;
updates TITLE.json, EPISODE/STORY headings/status and generated companion title/h1;
runs independent verify_claims, story_check, companion generation and upload
metadata generation; any failure returns nonzero and rolls back all outputs.
It does not push, publish or change analytical numbers. The scientific Python
is selected from ideation/.venv when available.

Then rebuild actual locked visuals and compare exact candidate pixels:

```sh
unset FA_LOCKED_PREVIEW
python3 studio/episodes/fair-airline/analysis/candidate_stills.py --compare
python3 studio/episodes/fair-airline/scenes/render_stills.py --audit-only
node studio/episodes/fair-airline/scenes/check_scenes.mjs
# Run the normal companion Chromium sweep with the launch command in companion/QA.md.
python3 studio/episodes/fair-airline/companion/check_browser.py
```

The comparison refuses unlocked claims, changed numerical results, changed title
or any PNG-byte difference. On PASS, keep the original candidate assembly
manifests as provenance: they describe the proposed-ledger preview that produced
the pixels. Claim/report hashes naturally change at the real lock; candidate
video bytes and audio need no re-encoding. Rebuild the companion to embed the
real verified ledger, not the preview's proposed evidence downloads.

```sh
# Require the compare PASS above and a nonexistent renders/final destination.
test ! -e studio/episodes/fair-airline/renders/final
mv studio/episodes/fair-airline/renders/final-candidate \
   studio/episodes/fair-airline/renders/final
```

The lock refreshes only the narration manifest's STORY hash after checking every
cached written line and citation. The lock edits nonspoken status/title metadata;
WAVs are untouched. Do not synthesize or change WAVs.
A different spoken script requires fresh narration/timing QA.
If the owner changes the title, rebuild EDIT (build_narrated_edit.py), prepare
actual timing, rebuild locked candidate data/stills/videos, repeat all narrated
and browser/marker QA, then run candidate_stills.py --record and --compare.
Never reset verified claims just to refresh a candidate manifest.

Commit the actual owner lock and generated episode sources, plus the public tool
script, through Claude's Git-capable workflow; then push the approved source
branch. The present helper protocol accepts episode-only paths. Therefore the
identical `studio/tools/public_repo_fair_airline.sh` is prepared locally but must
be included by Claude in that Git-capable commit. Its episode-scoped canonical
copy `analysis/public_repo_fair_airline.sh` is in this checkpoint; restore it with:

```sh
cp studio/episodes/fair-airline/analysis/public_repo_fair_airline.sh \
   studio/tools/public_repo_fair_airline.sh
chmod +x studio/tools/public_repo_fair_airline.sh
```

## Public repo and gh-pages (only after publishing approval)

Choose a disposable directory and source branch. The script deletes that target.
Do the dry run first; this build has NOT run the filter. The release filter keeps
the episode, renderer/tools and three directly cited r2/r7 ideation files; preserves
synthetic gate records and source manifests/hashes; drops other episodes,
raw/derived flight data, saved third-party pages, prompts/logs, renders and helper
receipts. Original-source commit IDs stay in source-commits.json; rewritten public
commit IDs differ. The same GitHub noreply address as scramble-luck is used.

```sh
studio/tools/public_repo_fair_airline.sh /private/tmp/fair-airline-public '<source-branch>'
git -C /private/tmp/fair-airline-public ls-files
# Inspect retained paths, README, source terms, and the rewritten history.
git -C /private/tmp/fair-airline-public remote add origin \
  https://github.com/bilguutei2k/fair-airline.git
git -C /private/tmp/fair-airline-public push -u origin main
```

Publish only the actual locked companion. For an initial gh-pages branch:

```sh
mkdir -p /private/tmp/fair-airline-pages
cp studio/episodes/fair-airline/companion/index.html /private/tmp/fair-airline-pages/index.html
touch /private/tmp/fair-airline-pages/.nojekyll
git -C /private/tmp/fair-airline-pages init -b gh-pages
git -C /private/tmp/fair-airline-pages config user.email 160076610+bilguutei2k@users.noreply.github.com
git -C /private/tmp/fair-airline-pages add index.html .nojekyll
git -C /private/tmp/fair-airline-pages commit -m 'Publish approved companion'
git -C /private/tmp/fair-airline-pages remote add origin https://github.com/bilguutei2k/fair-airline.git
git -C /private/tmp/fair-airline-pages push -u origin gh-pages
```

If gh-pages already exists, clone and update it instead of replacing its history.
Enable GitHub Pages from gh-pages/root. Expected address:
https://bilguutei2k.github.io/fair-airline/ . Verify both themes/phone/desktop online.
Replace PUBLIC_README and description link placeholders only after actual URLs
exist. Commit/push those links separately. Do not label anything Published early.

## Upload package

Run `python3 studio/episodes/fair-airline/analysis/build_upload_metadata.py` after
final title approval. `analysis/upload-metadata.json` has the exact four titles,
full descriptions (all under 5,000 characters) and MP4/SRT paths for upload.
Current titles, generated from TITLE.json for film/Short A:

| File under renders/final | Title | Duration |
| --- | --- | ---: |
| film.mp4 + film.srt | TITLE.json → title | 636.300 s |
| short-a.mp4 + short-a.srt | TITLE.json → title | 57.233 s |
| short-b.mp4 + short-b.srt | Whose deadline? | 59.100 s |
| short-c.mp4 + short-c.srt | The gap changes through the day | 57.467 s |

Descriptions carry BTS independent-processing credit and the official product
address, monthly hash-manifest pointer, DOT annual-report credits, full-film and
companion/code placeholders, operator/scope limitations and post-hoc labels.
Use those generated descriptions verbatim after substituting real URLs. The
owner uploads; this build uploads nothing.

## Tracked files larger than 5 MB

Inventory is repository-wide at preparation time; all four are dropped because
they belong to other episodes. No fair-airline/render/tool file is over 5 MB.
Exact bytes are in analysis/public-large-files.json.

| Tracked path | Bytes | Kept? |
| --- | ---: | --- |
| studio/episodes/playoff-jimmy/data/raw/heat-2023-24.pdf | 16,977,441 | No |
| studio/episodes/playoff-jimmy/data/raw/nuggets-2025-26.pdf | 16,769,865 | No |
| studio/episodes/scramble-luck/recheck/raw_rows.pkl | 6,250,151 | No |
| studio/episodes/wilt-fifty/analysis/qa.json | 8,467,901 | No |

## Published

**PENDING.** No owner editorial approval, publishing approval, lock commit,
public remote push, gh-pages publication or video upload is asserted here.
Claude should add actual dates, commit hashes and URLs only after those actions.
