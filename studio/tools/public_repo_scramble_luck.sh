#!/bin/sh
# Build the public history of the scramble-luck episode from the private working repository.
#
#   studio/tools/public_repo_scramble_luck.sh <empty or disposable directory> [branch]
#
# Clones the branch (default next-investigations) and rewrites every commit to keep only the
# episode, the renderer, the tools, and the idea-search files the episode's METHOD.md cites
# (the brief, the slate, the scramble pilot and validation study, the red-team, the method
# drafts). Other pilots, prompts, logs and scratch files are dropped. The WCA export itself is
# never committed (its manifest and hash are), and neither are the saved third-party web pages the
# claim checker reads for quotes and dates (analysis/claim_sources/; their manifest is kept). Commits left empty are dropped; the result is
# deterministic, so rerunning reproduces the same hashes and a later push is a fast-forward.
# The episode's PUBLIC_README.md becomes the repository README in a final commit.
set -eu
SRC=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
WORK=$1
BRANCH=${2:-next-investigations}
rm -rf "$WORK"
git clone --quiet --no-local --single-branch --branch "$BRANCH" "$SRC" "$WORK"
cd "$WORK"
git remote remove origin
git branch -m "$BRANCH" main

KEEP='^(LICENSE|\.gitignore|studio/episodes/scramble-luck/|studio/render/|studio/tools/|ideation/(BRIEF|SLATE)\.md$|ideation/rounds/r1/SHORTLIST\.md$|ideation/rounds/r2/verify-S1\.json$|ideation/rounds/r3/pilot-S1/|ideation/rounds/r4/(REDTEAM\.md|redteam\.json)$|ideation/rounds/r5/pilot-S1/|ideation/rounds/r6/)'
DROP='^(studio/tools/public_repo\.sh|studio/episodes/scramble-luck/analysis/claim_sources/.*\.(html|txt))$'
export KEEP DROP
NOREPLY=160076610+bilguutei2k@users.noreply.github.com
export NOREPLY
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --prune-empty --tag-name-filter cat \
  --env-filter 'GIT_AUTHOR_EMAIL=$NOREPLY; GIT_COMMITTER_EMAIL=$NOREPLY; export GIT_AUTHOR_EMAIL GIT_COMMITTER_EMAIL' \
  --index-filter '
  list=$(mktemp)
  git ls-files | { grep -vE "$KEEP" || true; } > "$list"
  git ls-files | { grep -E "$DROP" || true; } >> "$list"
  if [ -s "$list" ]; then git rm -q --cached --ignore-unmatch --pathspec-from-file="$list"; fi
  rm -f "$list"
' -- --all > /dev/null
rm -rf .git/refs/original
git reflog expire --expire=now --all
git gc --quiet --prune=now
cp studio/episodes/scramble-luck/PUBLIC_README.md README.md
git add README.md
GIT_AUTHOR_EMAIL=$NOREPLY GIT_COMMITTER_EMAIL=$NOREPLY git commit --quiet -m "README for the public repository"
echo "Public history in $WORK: $(git rev-list --count main) commits"
