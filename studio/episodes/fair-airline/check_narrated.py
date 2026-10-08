"""House delivery checks, with verified intentional full-cover panel wipes.

Fork of scramble-luck/check_narrated.py; state, caption, PCM and audio checks
are unchanged. This episode follows DIRECTION's 450 ms panel-wipe convention.
"""
import argparse
import json
import math
import re
import struct
import subprocess
import sys
import wave
from pathlib import Path

EP = Path(__file__).resolve().parent
sys.path.insert(0, str(EP.parents[1]/'tools'))
import assemble


def seconds(text):
    h,m,s = text.replace(',','.').split(':')
    return int(h)*3600+int(m)*60+float(s)


def scene_time(plan, t):
    """The shared renderer's timemap, including exact clock jumps/holds."""
    anchors = sorted(plan['anchors'],key=lambda a:a[1])
    if t<=anchors[0][1]:return anchors[0][0]
    i=0
    while i+1<len(anchors) and t>=anchors[i+1][1]:i+=1
    a,w=anchors[i]
    if i+1==len(anchors):return a+t-w
    a2,w2=anchors[i+1]
    speed=max(1,(a2-a)/max(w2-w,1e-6))
    return max(a,min(a+(t-w)*speed,a2-.001))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edit',type=Path,default=EP/'EDIT.json')
    parser.add_argument('--narration',type=Path,default=EP/'renders/audio/narration.json')
    parser.add_argument('--deliverables',nargs='+')
    parser.add_argument('--render-dir',type=Path,default=EP/'renders/draft')
    parser.add_argument('--qa-dir',type=Path,default=EP/'renders/qa/assembled')
    args = parser.parse_args()
    edit = json.loads(args.edit.read_text())
    narration = json.loads(args.narration.read_text())
    cues = json.loads((EP/'scenes/CUES.json').read_text())['scenes']
    out = args.qa_dir
    out.mkdir(parents=True,exist_ok=True)
    report = {}
    for name,spec in edit['deliverables'].items():
        if args.deliverables and name not in args.deliverables:
            continue
        plans = assemble.sequence_plans(spec['shots'],narration,edit)
        timed,placements,bridges = [],[],[]
        state_alignment = []
        for plan in plans:
            for cue in plan['shot']['cues']:
                if 'word' not in cue or cue['t']==0:continue
                states=cues[plan['shot']['scene']+'.html']['states']
                assert cue['t'] in [s['at'] for s in states],(name,'cue crossed a named-state boundary',cue)
                at=max(0,assemble.cue_time(cue,plan['lines'],plan['starts']))
                frame=math.ceil(at*30-1e-6)
                before=scene_time(plan,max(0,(frame-1)/30))
                after=scene_time(plan,frame/30)
                assert after>=cue['t']-.0011,(name,'late state',cue,after)
                assert frame==0 or before<cue['t'],(name,'early state',cue,before)
                state_alignment.append(dict(shot=plan['shot']['scene'],word=cue['word'],at=plan['start']+at,scene_clock=cue['t'],before=before,after=after))
            for start,line in zip(plan['starts'],plan['lines']):
                at = plan['start']+start
                timed += [(at+w['start'],at+w['end'],w['w']) for w in line['words']]
                placements.append((at,assemble.read_wav(EP/line['wav'],line.get('audio_range'))))
        scene_keys = [key for key in narration['scenes'] if key.startswith('S') and not key.startswith('Short')] if name=='film' else ['Short '+name[-1].upper()]
        expected = [w['w'] for key in scene_keys for line in narration['scenes'][key]['lines'] for w in line['words']]
        assert [w[2] for w in timed]==expected, (name,'written words omitted/duplicated/reordered')
        for a,b in zip(plans,plans[1:]):
            la,lb = a['lines'][-1],b['lines'][0]
            if la['wav']==lb['wav'] and la.get('audio_range') and lb.get('audio_range'):
                gap = round((b['start']+b['starts'][0]-a['start']-a['starts'][-1]-la['duration'])*24000)
                assert gap==0,(name,'PCM bridge',gap)
                bridges.append(dict(at=b['start'],gap_samples=gap))
        with wave.open(str(args.render_dir/f'{name}/narration.wav')) as f:
            pcm = f.readframes(f.getnframes())
        assert all(pcm[2*round(at*24000):2*round(at*24000)+len(seg)]==seg for at,seg in placements)
        vals = struct.unpack('<'+'h'*(len(pcm)//2),pcm)
        clip_count = sum(abs(x)>=32767 for x in vals)
        assert clip_count==0,(name,'source PCM clips')
        steps = []
        for at,seg in placements:
            for sample in [round(at*24000),round(at*24000)+len(seg)//2]:
                if 0<sample<len(vals):steps.append(abs(vals[sample]-vals[sample-1]))
        blocks = (args.render_dir/f'{name}.srt').read_text().strip().split('\n\n')
        cursor,maxrows,maxwidth = 0,0,0
        for block in blocks:
            rows = block.splitlines();start,end = map(seconds,rows[1].split(' --> '))
            words = ' '.join(rows[2:]).split();chunk = timed[cursor:cursor+len(words)]
            assert words==[w[2] for w in chunk],(name,'caption text/order')
            assert abs(start-chunk[0][0])<=.0011 and abs(end-chunk[-1][1])<=.0011,(name,'caption endpoints')
            maxrows = max(maxrows,len(rows)-2);maxwidth = max(maxwidth,*map(len,rows[2:]));cursor+=len(words)
        assert cursor==len(timed) and maxrows<=2 and maxwidth<=42
        video = args.render_dir/f'{name}.mp4'
        command = ['ffmpeg','-hide_banner','-i',str(video),'-vn','-af','ebur128=peak=true','-f','null','-']
        result = subprocess.run(command,capture_output=True,text=True,check=True)
        (out/(name+'-ebur128.log')).write_text(result.stderr)
        summary = result.stderr.rsplit('Summary:',1)[-1]
        level = float(re.search(r'I:\s*([-\d.]+) LUFS',summary)[1])
        peak = float(re.search(r'Peak:\s*([-\d.]+) dBFS',summary)[1])
        assert abs(level+14)<=.2 and peak<=-1,(name,level,peak)
        probe = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height,r_frame_rate,duration','-of','json',str(video)],capture_output=True,text=True,check=True)
        metadata = json.loads(probe.stdout)
        duration = sum(p['duration'] for p in plans)
        assert abs(float(metadata['format']['duration'])-duration)<.05
        # Decode every delivery frame; no black, blank or corrupt frame can hide
        # between the personally inspected cue/transition samples.
        process = subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-i',str(video),'-vf','scale=160:90,format=gray','-an','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # The reference episode uses cuts only. Our compositor deliberately
        # covers each scene cut with a solid contrasting panel (DIRECTION).
        # Accept low variance only where that panel covers >=97% of the frame
        # and its interior pixels match the independently generated color.
        panel_levels = {}
        wipes = [(p['start'],assemble.PANEL[p['shot']['bg']])
                 for p in plans if p['shot']['in']=='wipe']
        for color in {color for _,color in wipes}:
            swatch = subprocess.check_output(['ffmpeg','-v','error','-f','lavfi','-i',
                'color=c='+color+':s=160x90:r=30','-frames:v','1',
                '-vf','format=gray','-f','rawvideo','pipe:1'])
            assert len(set(swatch))==1
            panel_levels[color]=swatch[0]
        def verified_panel(frame,t):
            half=edit['wipe']/2
            for cut,color in wipes:
                if not cut-half<=t<=cut+half:
                    continue
                # Same cubic easing as assemble.wipe_graph; discard two
                # edge columns where scaling/encoding blends the boundary.
                progress=(t-cut+half)/half if t<cut else (t-cut)/half
                eased=1-(1-progress)**3
                x=-160+160*eased if t<cut else 160*eased
                left=max(0,x);right=min(160,x+160)
                if (right-left)/160<.97:
                    continue
                lo=math.ceil(left)+2;hi=math.floor(right)-2
                pixels=[v for row in range(90) for v in frame[row*160+lo:row*160+hi]]
                expected=panel_levels[color]
                if pixels and max(abs(v-expected) for v in pixels)<=3:
                    return dict(frame=round(t*30),cut=cut,panel=color,
                                coverage=round((right-left)/160,6))
            return None
        n,blank,minimum,intentional_panels = 0,[],(999,0),[]
        while True:
            frame = process.stdout.read(14400)
            if not frame:break
            assert len(frame)==14400
            mean = sum(frame)/len(frame)
            sd = math.sqrt(sum(x*x for x in frame)/len(frame)-mean*mean)
            if sd<minimum[0]:minimum=(sd,n/30)
            if sd<3:
                panel=verified_panel(frame,n/30)
                if panel:intentional_panels.append(panel)
                else:blank.append(n)
            n+=1
        assert process.wait()==0 and not blank
        assert n==round(duration*30),(name,'frame count',n,duration)
        gates = [dict(shot=i+1,selector=r['selector'],at=round(p['start']+r['at'],6)) for i,p in enumerate(plans) for r in p['reveals'] if r['at']<p['duration']]
        tails = [p['duration']-max(st+line['words'][-1]['end'] for st,line in zip(p['starts'],p['lines'])) for p in plans]
        gaps = [b[0]-a[1] for a,b in zip(timed,timed[1:])]
        report[name] = dict(duration=round(duration,3),shots=len(plans),srt_cues=len(blocks),max_caption_rows=maxrows,max_caption_width=maxwidth,
                            word_count=len(expected),caption_text_order_endpoint_failures=0,pcm_matches_cache=True,pcm_clip_count=clip_count,
                            pcm_bridges=bridges,max_placement_sample_step=max(steps,default=0),integrated_lufs=level,true_peak_dbtp=peak,
                            decoded_frames=n,blank_frames=blank,intentional_wipe_frames=intentional_panels,
                            minimum_frame_luma_sd=minimum[0],longest_word_gap=max(gaps,default=0),
                            max_post_word_hold=max(tails),shot_range=[min(p['duration'] for p in plans),max(p['duration'] for p in plans)],
                            gates=gates,metadata=metadata)
        report[name]['state_alignment']=state_alignment
        report[name]['early_or_late_state_failures']=0
        print(name,round(duration,3),'seconds;',level,'LUFS;',peak,'dBTP;',n,'frames; captions/PCM/words PASS',flush=True)
    target = 'checks-'+ '-'.join(args.deliverables)+'.json' if args.deliverables else 'checks.json'
    (out/target).write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
