"""Compile exact spoken-word cues; after narration, split only cached PCM.

Without narration this writes a reviewable EDIT with whole-line shots and no
invented timing. Rerun after synthesis for the timed scramble-luck shot pacing.
"""
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

EP = Path(__file__).resolve().parent
sys.path.insert(0, str(EP.parents[1] / 'tools'))
from assemble import cue_time, sequence_plans, slice_line

# Use the same punctuation-sensitive, cached-PCM fragment pacing as the pilot.
spec = importlib.util.spec_from_file_location('scramble_edit', EP.parent / 'scramble-luck/build_narrated_edit.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
TARGETS = {
 's01': ['look','78.60%','2025','excluded'],
 's02': ['succeeds','fifteen','cancellation','determined'],
 's03': ['78.34%','network','opportunities'],
 's04': ['cell','Denver','different','scheduled'],
 's05': ['weight','replication','two','move'],
 's06': ['failed','redesigned','days','Fresh','history'],
 's07': ['79.75%','6.3','99%','advantage','variability'],
 's08': ['sealed','8.2','99%','replicated','reversal'],
 's09': ['one-hour','6.7','descriptive'],
 's10': ['4.5','4.8','allowance','2.6','verdict'],
 's11': ['10.1','denominator','9.9','cause'],
 's12': ['overlap','eighty','0.4','11.7','timetable','deadline'],
 'short-a': ['tied','matched','6.3','small'],
 'short-b': ['4.5','2.6','leaves','deadline'],
 'short-c': ['0.4','11.7','eighty','hidden'],
}
# Start B's envelope when it is introduced, and the short result on its gap.
OVERRIDES = {('s08','b-envelope'): 'Its nominal 99% envelope',
             ('short-a','result'): "Against each airline's own arrival timetable",
             ('short-b','duration'): 'United schedules about 4.5 minutes longer'}


def events(page, info, lines):
    prefix = page[:3] if not page.startswith('short') else page[:-5]
    found = []
    for state, target in zip(info['states'], TARGETS[prefix], strict=True):
        phrase = OVERRIDES.get((prefix,state['id']), state['cue'])
        for i,line in enumerate(lines):
            at = line['written'].find(phrase)
            if at < 0:
                continue
            first = len(line['written'][:at].split())
            j = next(j for j in range(first,len(line['words']))
                     if pilot.clean(line['words'][j]['w']) == pilot.clean(target))
            found.append(dict(state=state,index=i,word_index=j))
            break
        else:
            raise ValueError((page,state['id'],phrase,target))
    assert [(e['index'],e['word_index']) for e in found] == sorted((e['index'],e['word_index']) for e in found)
    return found


# Value gates preserve written cue keys. All copies of a primary observation
# remain hidden until its own spoken number, including later state snapshots.
A='primary_2023_2024';B='replication_2025'
VALUE_GATES={
 's01': [('78.60%', '[data-value-key*="2024"][data-value-key*="UA"][data-value-key*="rate_pct"]'),
         ('78.57%', '[data-value-key*="2024"][data-value-key*="WN"][data-value-key*="rate_pct"]')],
 's07': [('79.75%', '[data-value-key="'+A+'.weighted_matched_secondary_rates_pct.UA.on_time.estimate"]'),
         ('73.48%', '[data-value-key="'+A+'.weighted_matched_secondary_rates_pct.WN.on_time.estimate"]'),
         ('6.3', '[data-value-key="'+A+'.adjusted_gap_ua_minus_wn_pp.estimate"], [data-geometry-key="'+A+'.adjusted_gap_ua_minus_wn_pp.estimate"]'),
         ('4.60', '[data-value-key="'+A+'.adjusted_gap_ua_minus_wn_pp.interval[0]"]'),
         ('7.94', '[data-value-key="'+A+'.adjusted_gap_ua_minus_wn_pp.interval[1]"], [data-geometry-key="'+A+'.adjusted_gap_ua_minus_wn_pp.interval"]')],
 's08': [('8.2', '[data-value-key="'+B+'.adjusted_gap_ua_minus_wn_pp.estimate"], [data-geometry-key="'+B+'.adjusted_gap_ua_minus_wn_pp.estimate"]'),
         ('5.31', '[data-value-key="'+B+'.adjusted_gap_ua_minus_wn_pp.interval[0]"]'),
         ('11.00', '[data-value-key="'+B+'.adjusted_gap_ua_minus_wn_pp.interval[1]"], [data-geometry-key="'+B+'.adjusted_gap_ua_minus_wn_pp.interval"]')],
 'short-a': [('6.3','[data-value-key="'+A+'.adjusted_gap_ua_minus_wn_pp.estimate"], [data-geometry-key="'+A+'.adjusted_gap_ua_minus_wn_pp.estimate"]'),
             ('8.2','[data-value-key="'+B+'.adjusted_gap_ua_minus_wn_pp.estimate"], [data-geometry-key="'+B+'.adjusted_gap_ua_minus_wn_pp.estimate"]'),
             ('envelopes','[data-value-key*="adjusted_gap"][data-value-key*="interval"], [data-geometry-key*="adjusted_gap"][data-geometry-key*="interval"], [data-interval-label]'),
             ('replicated','.claim.chip')],
}


def key_gate(word,key):
    return (word, '[data-value-key="'+key+'"], [data-geometry-key="'+key+'"]')

VALUE_GATES['s03']=[key_gate(w,p+'.unmatched_all_flights_on_time_pct.'+op+'.estimate')
    for w,p,op in [('78.34%',A,'UA'),('77.91%',A,'WN'),('77.65%',B,'UA'),('77.76%',B,'WN')]]
VALUE_GATES['s10']=[key_gate(w,key) for w,key in [('4.5','A.schedule.UA_minus_WN'),('4.5','B.schedule.UA_minus_WN'),
    ('4.8','A.completed_cell_means.actual.UA_minus_WN'),('6.2','B.completed_cell_means.actual.UA_minus_WN'),
    ('2.6','A.common_mid.UA_minus_WN'),('4.3','B.common_mid.UA_minus_WN')]]
VALUE_GATES['short-b']=VALUE_GATES['s10']
VALUE_GATES['s11']=[key_gate(w,key) for w,key in [('10.1','A.dep_late.UA_minus_WN'),('13.1','B.dep_late.UA_minus_WN'),
    ('9.9','A.dep_timely.UA_minus_WN'),('13.3','B.dep_timely.UA_minus_WN')]]
VALUE_GATES['s12']=[key_gate(w,'derived_metrics.'+p+'.time.'+band+'.gap_pp')
    for w,p,band in [('0.4','A','before_10'),('1.4','B','before_10'),('11.7','A','from_16'),('12.9','B','from_16')]]
VALUE_GATES['short-c']=VALUE_GATES['s12']
VALUE_GATES['s09']=[key_gate(w,p+'.sensitivities.reciprocal_nearest_30min.gap_ua_minus_wn_pp.estimate')
    for w,p in [('6.7',A),('9.1',B)]]


def value_gates(shot,page,lines,i,a,b):
    prefix=page[:3] if not page.startswith('short') else page[:-5]
    reveals=[]
    for target,selector in VALUE_GATES.get(prefix,[]):
        hits=[(li,j) for li,line in enumerate(lines) for j,w in enumerate(line['words']) if pilot.clean(w['w'])==pilot.clean(target)]
        if not hits:
            raise ValueError(('missing value gate',prefix,target))
        li,j=hits[0]
        if li>i or li==i and j>=b:
            reveals.append(dict(selector=selector,hidden=True))
        elif li==i and a<=j<b:
            w=lines[i]['words'][j]['w']
            nth=sum(pilot.clean(x['w'])==pilot.clean(w) for x in lines[i]['words'][a:j+1])
            reveals.append(dict(selector=selector,line=0,word=w,nth=nth))
    if reveals:
        shot['reveals']=reveals


def main():
    cues = json.loads((EP/'scenes/CUES.json').read_text())['scenes']
    path = EP/'renders/audio/narration.json'
    actual = path.exists()
    if actual:
        narration = json.loads(path.read_text())
    else:
        forms = json.loads((EP/'SPOKEN_FORMS.json').read_text())['scenes']
        narration = {'scenes': {key: {'lines': [{**line,'words':[{'w':w} for w in line['written'].split()]} for line in lines]}
                                for key,lines in forms.items()}}
    edit = dict(status='pre-lock draft',voice='af_heart',
        about='Claims proposed; exact written-word cues. '+('Actual Kokoro timing.' if actual else 'Voice blocked in sandbox; rerun builder after synthesis for timed PCM fragments.'),
        timing='Named states start on their spoken word; original animation plays then holds. Wipes cover scene changes; cuts within scenes.',
        gap=.45,lead=.4,tail=.9,wipe=.45,bridge_word_ranges=True,strict_captions=True,
        audio_true_peak=-1.5,calibrate_loudness=True,settled_visuals=True,deliverables={})
    for name in ['film','short-a','short-b','short-c']:
        pages = [p for p in cues if not p.startswith('short')] if name=='film' else [name+'.html']
        shots=[]
        for page in pages:
            info=cues[page]
            key=page[:3].upper() if name=='film' else 'Short '+name[-1].upper()
            lines=narration['scenes'][key]['lines']
            ev=events(page,info,lines)
            active=info['states'][0]
            def hold(state):
                return next((s['at'] for s in info['states'] if s['at']>state['at']),info['duration'])-.05
            for i,line in enumerate(lines):
                ranges=pilot.split(line) if actual else [(0,len(line['words']))]
                for a,b in ranges:
                    initial=hold(active) if (i or a) else 0
                    shot=dict(scene=page[:-5],bg='night' if page.startswith('s01') else 'paper',
                        **{'in':'wipe' if name=='film' and i==a==0 and shots else 'cut'},
                        lines=[key,[i]],cues=[dict(t=initial,line=0)],about=f'{key} line {i}, words {a}–{b}')
                    if actual:
                        shot['word_ranges']=[[a,b]]
                    if not shots and name!='film':
                        shot['lead']=.15
                    for e in ev:
                        if e['index']!=i or not a<=e['word_index']<b:
                            continue
                        # State zero is the starting layout: play it from the
                        # lead-in, rather than holding an empty body until a
                        # keyword late in the introduction. Values retain
                        # independent spoken-word gates. Later jumps depart
                        # from its settled hold, not its empty first frame.
                        if e['state']['at']==0:
                            initial=hold(active)
                            continue
                        state=e['state'];w=line['words'][e['word_index']]['w']
                        nth=sum(pilot.clean(x['w'])==pilot.clean(w) for x in line['words'][a:e['word_index']+1])
                        t=max(initial,state['at'])
                        cue=dict(t=t,line=0,word=w,nth=nth)
                        if t>initial:
                            cue['jump_from']=initial
                        shot['cues'].append(cue)
                        active=state;initial=hold(active)
                    shot['end_t']=hold(active)
                    value_gates(shot,page,lines,i,a,b)
                    if actual and len(ranges)==1:
                        spoken=slice_line(line,[a,b])
                        shot['tail']=max(.9,6-(shot.get('lead',.4)+spoken['duration']))
                    shots.append(shot)
        title=json.loads((EP/'TITLE.json').read_text())['title'] if name in ['film','short-a'] else 'Whose deadline?' if name=='short-b' else 'The gap changes through the day'
        edit['deliverables'][name]=dict(format='landscape' if name=='film' else 'vertical',title=title,shots=shots)
        if actual:
            plans=sequence_plans(shots,narration,edit)
            for plan in plans:
                for cue in plan['shot']['cues']:
                    if 'word' not in cue:
                        continue
                    at=cue_time(cue,plan['lines'],plan['starts'])
                    frame=math.ceil(at*30-1e-6)
                    # Apply after PCM bridges set the effective lead. Anchor
                    # rounding must not push a word-frame jump one frame late.
                    if round(at,3)>frame/30+1e-9:
                        cue['offset']=round(math.floor(frame/30*1000)/1000-at,9)
            plans=sequence_plans(shots,narration,edit)
            if any(s['in']=='wipe' for s in shots):
                # The house compositor formats panel-source duration in ms.
                # End on a 3-frame/100-ms boundary so rounding cannot create
                # an extra terminal panel frame. Pad only the closing hold.
                frames=round(sum(p['duration'] for p in plans)*30)
                pad=(-frames)%3
                if pad:
                    shots[-1]['tail']=round(shots[-1].get('tail',edit['tail'])+pad/30,9)
                    plans=sequence_plans(shots,narration,edit)
            print(name,len(plans),'shots',round(sum(p['duration'] for p in plans),3),'seconds')
        else:
            print(name,len(shots),'whole-line shots; recorded timing pending')
    (EP/'EDIT.json').write_text(json.dumps(edit,indent=2,ensure_ascii=False)+'\n')


if __name__=='__main__':
    main()
