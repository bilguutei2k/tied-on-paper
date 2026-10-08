"""Prepare actual-timing SRTs and QA plans before Chromium assembly."""
import hashlib
import json
import sys
from pathlib import Path

EP=Path(__file__).resolve().parent
sys.path.insert(0,str(EP.parents[1]/'tools'))
import assemble

if __name__=='__main__':
    edit=json.loads((EP/'EDIT.json').read_text())
    narration=json.loads((EP/'renders/audio/narration.json').read_text())
    assert narration['story_sha256']==hashlib.sha256((EP/'STORY.md').read_bytes()).hexdigest()
    out=EP/'renders/draft';out.mkdir(parents=True,exist_ok=True)
    report={}
    for name,spec in edit['deliverables'].items():
        plans=assemble.sequence_plans(spec['shots'],narration,edit)
        timed=[(p['start']+start,line) for p in plans for start,line in zip(p['starts'],p['lines'])]
        keys=[k for k in narration['scenes'] if k.startswith('S') and not k.startswith('Short')] if name=='film' else ['Short '+name[-1].upper()]
        expected=[w['w'] for k in keys for line in narration['scenes'][k]['lines'] for w in line['words']]
        assert [w['w'] for _,line in timed for w in line['words']]==expected
        captions=assemble.captions(timed,out/(name+'.srt'),strict=True)
        duration=round(sum(p['duration'] for p in plans),3)
        report[name]=dict(duration=duration,shots=len(plans),words=len(expected),captions=captions,
                         anchors=[dict(scene=p['shot']['scene'],start=p['start'],duration=p['duration'],anchors=p['anchors'],reveals=p['reveals']) for p in plans])
        print(name,duration,'seconds;',len(plans),'shots;',captions,'SRT cues')
    qa=EP/'renders/qa';qa.mkdir(parents=True,exist_ok=True)
    (qa/'timing-preflight.json').write_text(json.dumps(report,indent=2)+'\n')
