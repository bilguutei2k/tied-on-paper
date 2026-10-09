#!/usr/bin/env python3
"""Freeze candidate pixel hashes, or rebuild after real lock and compare them."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

EP=Path(__file__).resolve().parent.parent
MANIFEST=EP/'analysis/final-candidate-manifest.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    parser.add_argument('--compare',action='store_true')
    args=parser.parse_args()
    if args.record == args.compare:parser.error('choose --record or --compare')
    cues=json.loads((EP/'scenes/CUES.json').read_text())['scenes']
    paths=[s['path'] for v in cues.values() for s in v['states']]
    if args.record:
        states={c['status'] for c in json.loads((EP/'CLAIMS.json').read_text())['claims']}
        assert states in ({'proposed'},{'verified'}), 'Homogeneous proposed or verified ledger required'
        doc={'kind':'locked-display candidate; this command records no approval',
             'title':json.loads((EP/'TITLE.json').read_text())['title'],
             'results_sha256':sha(EP/'analysis/results.json'),
             'stills':{p:sha(EP/p) for p in paths}}
        MANIFEST.write_text(json.dumps(doc,indent=2,sort_keys=True)+'\n')
        print('Recorded',len(paths),'candidate still hashes; no approval recorded.')
    else:
        assert all(c['status']=='verified' for c in json.loads((EP/'CLAIMS.json').read_text())['claims']), 'Real claim lock required'
        env=dict(os.environ);env.pop('FA_LOCKED_PREVIEW',None)
        subprocess.run(['python3',str(EP/'scenes/build_data.py')],env=env,check=True)
        subprocess.run(['python3',str(EP/'scenes/render_stills.py')],env=env,check=True)
        doc=json.loads(MANIFEST.read_text())
        assert sha(EP/'analysis/results.json')==doc['results_sha256'],'Analytical results changed'
        assert json.loads((EP/'TITLE.json').read_text())['title']==doc['title'],'Title changed; rebuild/re-QA candidates'
        differences=[p for p in paths if sha(EP/p)!=doc['stills'][p]]
        assert not differences, 'Candidate pixel mismatch: '+str(differences)
        subprocess.run(['python3',str(EP/'companion/build.py')],env=env,check=True)
        print('PASS:',len(paths),'stills byte-identical; candidate videos may be promoted without rendering again.')
if __name__=='__main__':main()
