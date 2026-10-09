#!/usr/bin/env python3
"""Rebind nonspoken STORY metadata only when every cached line/citation matches."""
import hashlib
import json
import re
import sys
from pathlib import Path
EP=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(EP.parents[1]/'tools'))
from story_check import TAG, scenes

def main():
    cache=EP/'renders/audio/narration.json'
    if not cache.exists():
        print('No cached narration metadata to refresh; no audio synthesized.')
        return
    doc=json.loads(cache.read_text());seen=set()
    for (_,heading),lines in scenes((EP/'STORY.md').read_text()).items():
        heading=re.sub(r'^Short ([123]):',lambda m:'Short '+'ABC'[int(m[1])-1]+':',heading)
        match=re.match(r'(S\d\d|Short [A-Z])',heading)
        if not match:continue
        key=match[1];seen.add(key);saved=doc['scenes'][key]['lines']
        assert len(lines)==len(saved),f'Changed narration count: {key}'
        for line,entry in zip(lines,saved):
            assert TAG.sub('',line).strip()==entry['written'],f'Spoken text changed: {key}; fresh narration/QA required'
            assert [c.strip() for group in TAG.findall(line) for c in group.split(',')]==entry['claims'],f'Citation changed: {key}'
    assert seen==set(doc['scenes']),'Narration scenes changed'
    doc['story_sha256']=hashlib.sha256((EP/'STORY.md').read_bytes()).hexdigest()
    cache.write_text(json.dumps(doc,indent=2,ensure_ascii=False)+'\n')
    print('Cached written lines/citations match; STORY metadata hash refreshed. WAVs untouched.')
if __name__=='__main__':main()
