"""Extract actual decoded cue/cut/wipe frames and inspection contact sheets."""
import json
import os
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

EP=Path(__file__).resolve().parent
if __name__=='__main__':
    timing=json.loads((EP/'renders/qa/timing-preflight.json').read_text())
    manifest={}
    for name,spec in timing.items():
        root=Path(os.environ.get('FA_SAMPLE_DIR',str(EP/'renders/qa/decoded'))).resolve()/name;root.mkdir(parents=True,exist_ok=True)
        # A revised cue list can have fewer samples than the previous run.
        for pattern in ('[0-9][0-9][0-9][0-9].png','sheet-*.jpg'):
            for old in root.glob(pattern):
                old.unlink()
        frames={0,round(spec['duration']*30)-1}
        for p in spec['anchors']:
            times=[p['start'],p['start']+p['duration']-1/30]
            times += [p['start']+at for _,at in p['anchors'] if at<p['duration']]
            times += [p['start']+r['at'] for r in p['reveals'] if r['at']<p['duration']]
            times += [p['start']-.225,p['start']+.225]
            for t in times:
                n=math.ceil(t*30-1e-6)
                frames.update(n+d for d in [-1,0,1] if 0<=n+d<round(spec['duration']*30))
        frames=sorted(frames)
        # Coalesce adjacent frame numbers and balance the expression: the
        # film's >1000 samples exceed FFmpeg's linear expression depth limit.
        ranges=[]
        for n in frames:
            if ranges and n==ranges[-1][1]+1:
                ranges[-1][1]=n
            else:
                ranges.append([n,n])
        terms=['between(n,%d,%d)'%(a,b) for a,b in ranges]
        while len(terms)>1:
            terms=['('+ '+'.join(terms[i:i+2])+')' for i in range(0,len(terms),2)]
        select=terms[0]
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(Path(os.environ.get('FA_RENDER_DIR',str(EP/'renders/draft')))/(name+'.mp4')),
            '-vf',"select='"+select+"'",'-fps_mode','vfr',str(root/'%04d.png')],check=True)
        files=sorted(root.glob('[0-9][0-9][0-9][0-9].png'))
        assert len(files)==len(frames)
        for base in range(0,len(files),16):
            sheet=Image.new('RGB',(1280,800),'#d5cec0');draw=ImageDraw.Draw(sheet)
            for j,path in enumerate(files[base:base+16]):
                im=Image.open(path).convert('RGB');im.thumbnail((310,172))
                x=(j%4)*320;y=(j//4)*200
                sheet.paste(im,(x,y));draw.text((x+5,y+177),f'{name} frame {frames[base+j]} @ {frames[base+j]/30:.3f}s',fill='black')
            sheet.save(root/('sheet-%02d.jpg'%(base//16+1)))
        manifest[name]=[dict(frame=n,time=n/30,path=str(p.relative_to(EP))) for n,p in zip(frames,files)]
        print(name,len(files),'decoded samples; sheets:',root)
    (Path(os.environ.get('FA_SAMPLE_DIR',str(EP/'renders/qa/decoded'))).resolve()/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
