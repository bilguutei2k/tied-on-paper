#!/usr/bin/env python3
"""Outcome-free production arrays: METHOD seed, amended year/draw/start order."""
import sys,json,hashlib,subprocess
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
sys.path.insert(0,str(HERE.parent/'amendment2'))
import run_gate as gate  # Installs and tests the raw/network audit denial.
from common import EP,OUT,DERIVED,sha,dump,progress,utc

def main():
    assert json.loads((HERE.parent/'amendment2/results.json').read_text())['status']=='PASS'
    assert subprocess.check_output(['git','show','41a6974:studio/episodes/fair-airline/analysis/amendment2/OWNER_APPROVAL.md'])==(HERE.parent/'amendment2/OWNER_APPROVAL.md').read_bytes()
    st,manifest=gate.load_structure()
    frozen=json.loads((gate.HERE/'structure.json').read_text())
    assert manifest['cells_sha256']==frozen['cells_sha256']
    r=np.random.Generator(np.random.PCG64(20261005)); arrays=[]; groups=[]
    for y,off,T in st['groups']:
        q,tail=divmod(T,28)
        a=r.integers(0,T,size=(1999,q+1),endpoint=False)
        p=DERIVED/f'confirm-starts-{y}.npy';np.save(p,a,allow_pickle=False)
        arrays.append(dict(year=y,path=str(p.relative_to(EP)),sha256=sha(p),bytes=p.stat().st_size,
            shape=list(a.shape),dtype=str(a.dtype),array_sha256=hashlib.sha256(a.astype('<i8').tobytes()).hexdigest()))
        groups.append(dict(year=y,days=T,start=str(st['date'][st['year']==y].min()),q=q,tail=tail))
    dump(HERE/'resampling.json',dict(seed=20261005,rng='Generator(PCG64)',draws=1999,length=28,
        order='source year 2023,2024,2025; row-major draw/start',arrays=arrays,groups=groups,
        regenerate='ideation/.venv/bin/python studio/episodes/fair-airline/analysis/confirm/prepare.py',
        schedule_cells_sha256=manifest['cells_sha256'],schedule_input=manifest['input'],
        support=manifest['support'],environment={k:manifest[k] for k in ['numpy','scipy','duckdb','python']},
        raw_denial=manifest['raw_denial'],confirmation_outcomes_opened=False))
    from analyze import sealed_table
    support=[]
    for rec in json.loads((EP/'data/sensitivity-manifest.json').read_text())['files']:
        name=Path(rec['path']).name
        if not (name.startswith('pairs-') or name=='nearest30.parquet'):continue
        t=sealed_table(rec,filters=[('a','==','UA'),('b','==','WN')])
        yr=t['source_year'].to_numpy();date=t['matching_date'].to_numpy().astype('datetime64[D]')
        for grp in groups:
            dates=date[yr==grp['year']]
            delta=(dates-np.datetime64(grp['start'])).astype(int)
            assert len(dates)>0 and np.all((delta>=0)&(delta<grp['days']))
            support.append(dict(specification=name,year=grp['year'],cells=len(dates),within_frozen_daily_span=True))
    dump(HERE/'schedule-preflight.json',dict(passes=True,sensitivities=support,confirmation_outcomes_opened=False))
    print(json.dumps(dict(prepared=True,groups=groups,confirmation_outcomes_opened=False)))

if __name__=='__main__':main()
