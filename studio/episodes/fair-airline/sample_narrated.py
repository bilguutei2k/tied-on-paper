"""Extract actual decoded cue/cut/wipe frames and inspection contact sheets."""
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

EP=Path(__file__).resolve().parent
if __name__=='__main__':
    timing=json.loads((EP/'renders/qa/timing-preflight.json').read_text())
    manifest={}
    for name,spec in timing.items():
        root=EP/'renders/qa/decoded'/name;root.mkdir(parents=True,exist_ok=True)
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
        select='+'.join('eq(n\\,%d)'%n for n in frames)
        subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(EP/'renders/draft'/(name+'.mp4')),
            '-vf','select='+select,'-fps_mode','vfr',str(root/'%04d.png')],check=True)
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
    (EP/'renders/qa/decoded/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
