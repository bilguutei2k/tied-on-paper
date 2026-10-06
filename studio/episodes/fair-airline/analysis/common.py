"""Outcome-blind paths, hashes and append-only progress helpers."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

EP = Path(__file__).resolve().parents[1]
OUT = EP / 'analysis'
RAW = EP / 'data/raw'
DERIVED = EP / 'data/derived'
CARRIERS = {'AA': 19805, 'AS': 19930, 'B6': 20409, 'DL': 19790,
            'F9': 20436, 'NK': 20416, 'UA': 19977, 'WN': 19393}

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(2**20), b''):
            h.update(b)
    return h.hexdigest()

def dump(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + '\n')
    tmp.replace(path)

def progress(message):
    with (OUT / 'PROGRESS.md').open('a') as f:
        f.write(f'\n- {utc()}: {message}\n')

def seal_file(path):
    path = Path(path)
    return {'path': str(path.relative_to(EP)), 'bytes': path.stat().st_size,
            'sha256': sha(path)}
