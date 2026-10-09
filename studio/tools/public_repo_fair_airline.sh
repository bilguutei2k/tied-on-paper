#!/bin/sh
# Deterministic public history. Claude must dry-run before pushing.
# Usage: studio/tools/public_repo_fair_airline.sh <empty/disposable directory> [branch]
# Only cited r7 method/red-team and r2 source-verification ideation files.
# LESSONS 10: saved third-party pages are never redistributed; manifests survive.
set -eu
[ "$#" -ge 1 ] || { echo 'Supply an empty/disposable output directory' >&2; exit 2; }
SRC=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
WORK=$1
BRANCH=${2:-next-investigations}
case "$WORK" in ''|/|.|..|"$SRC"|"$SRC"/*) echo 'Unsafe output directory' >&2; exit 2;; esac
rm -rf "$WORK"
git clone --quiet --no-local --single-branch --branch "$BRANCH" "$SRC" "$WORK"
cd "$WORK"
git remote remove origin
git branch -m "$BRANCH" main
KEEP='^(LICENSE|\.gitignore|studio/episodes/fair-airline/|studio/render/|studio/tools/|ideation/rounds/r2/verify-S6\.json$|ideation/rounds/r7/(airline-redteam|fair-airline-METHOD\.v2)\.md$)'
DROP='(^|/)(raw|derived|renders|prompts|logs|__pycache__|node_modules)/|\.(html|htm|pdf|warc|mhtml)$|\.(parquet|zip|mp4|wav)$|(^|/)(COMMIT_REQUEST|COMMIT_DONE)\.json$|(^|/)([^/]*\.log|commit_helper[^/]*)$|^studio/tools/public_repo\.sh$'
export KEEP DROP
NOREPLY=160076610+bilguutei2k@users.noreply.github.com
export NOREPLY
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --prune-empty --tag-name-filter cat \
 --env-filter 'GIT_AUTHOR_EMAIL=$NOREPLY; GIT_COMMITTER_EMAIL=$NOREPLY; export GIT_AUTHOR_EMAIL GIT_COMMITTER_EMAIL' \
 --index-filter '
 list=$(mktemp)
 git ls-files | { grep -vE "$KEEP" || true; } > "$list"
 # Keep original authored scene/companion HTML; drop all other saved pages.
 git ls-files | { grep -E "$DROP" || true; } | { grep -vE "^studio/episodes/fair-airline/(scenes/[^/]+\.html|companion/(template|index)\.html)$|^studio/tools/storyboard\.html$" || true; } >> "$list"
 if [ -s "$list" ]; then git rm -q --cached --ignore-unmatch --pathspec-from-file="$list"; fi
 rm -f "$list"
' -- --all > /dev/null
rm -rf .git/refs/original
git reflog expire --expire=now --all
git gc --quiet --prune=now
cp studio/episodes/fair-airline/PUBLIC_README.md README.md
git add README.md
GIT_AUTHOR_EMAIL=$NOREPLY GIT_COMMITTER_EMAIL=$NOREPLY git commit --quiet -m 'README for the public repository'
echo "Public history in $WORK: $(git rev-list --count main) commits"
