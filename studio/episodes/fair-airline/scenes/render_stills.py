"""Render every cue state offline; keep shared renderer unchanged.

Uses render.mjs unchanged. The disposable Chromium launcher keeps everything
local and supports macOS environments requiring single-process Chromium.
Writes episode renders/ and progress; shared renderer sources are read-only.
"""
import argparse
import contextlib
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

SCENES = Path(__file__).resolve().parent
ROOT = SCENES.parents[3]
RENDER = ROOT / 'studio/render/render.mjs'
OUT = SCENES.parent / 'renders/stills'


@contextlib.contextmanager
def offline_chrome():
    chrome = os.environ.get('CHROME')
    if not chrome:
        candidates = sorted(Path.home().glob('Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell'))
        if not candidates:
            raise RuntimeError('No local headless Chromium; set CHROME')
        chrome = str(candidates[-1])
    with tempfile.TemporaryDirectory(prefix='fa-local-chrome-') as temp:
        wrapper = Path(temp) / 'chrome'
        flags = ['--single-process', '--no-sandbox', '--in-process-gpu', '--disable-background-networking',
                 '--disable-component-update', '--disable-sync', '--no-first-run', '--disable-default-apps',
                 '--disable-domain-reliability', '--metrics-recording-only',
                 '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost']
        wrapper.write_text('#!/bin/sh\nexec ' + shlex.quote(chrome) + ' ' + ' '.join(map(shlex.quote, flags)) + ' "$@"\n')
        wrapper.chmod(0o755)
        yield dict(os.environ, CHROME=str(wrapper))


def render(page, t, target, fmt, env):
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['node', str(RENDER), str(page), '--still', str(t), '--format', fmt, '--out', str(target)],
                   check=True, env=env, timeout=120)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', nargs='*')
    parser.add_argument('--audit-only', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cues = json.loads((SCENES / 'CUES.json').read_text())
    manifest = []
    with offline_chrome() as env:
        if args.audit_only:
            subprocess.run(['node', str(SCENES / 'browser_audit.mjs')], check=True, env=env, timeout=240)
            return
        for page, info in cues['scenes'].items():
            for state in info['states']:
                target = SCENES.parent / state['path']
                if args.pages is None or page in args.pages:
                    render(SCENES / page, state['still'], target, info['format'], env)
                if target.exists():
                    manifest.append(dict(page=page, state=state['id'], t=state['still'], path=state['path'], sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
            with (SCENES / 'PROGRESS.md').open('a') as f:
                f.write('\n- Render pass completed for `' + page + '`: ' + str(len(info['states'])) + ' cue PNGs.\n')
    (OUT / 'manifest.json').write_text(json.dumps(dict(status='locked-display preview; owner approval PENDING' if os.environ.get('FA_LOCKED_PREVIEW') == '1' else 'locked' if all(c['status']=='verified' for c in json.loads((SCENES.parent/'CLAIMS.json').read_text())['claims']) else 'PRE-LOCK DRAFT', results_sha256=hashlib.sha256((SCENES.parent / 'analysis/results.json').read_bytes()).hexdigest(), shared_renderer_sha256={name:hashlib.sha256((ROOT / 'studio/render' / name).read_bytes()).hexdigest() for name in ['system.css','system.js','render.mjs']}, episode_source_sha256={name:hashlib.sha256((SCENES / name).read_bytes()).hexdigest() for name in ['episode.js','episode.css','build_data.py','CUES.json']}, stills=manifest), indent=2) + '\n')

if __name__ == '__main__':
    main()
