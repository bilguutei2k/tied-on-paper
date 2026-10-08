"""Generate HTML cue configurations; numerical observations live only in data.js."""
import json
from pathlib import Path
S = Path(__file__).resolve().parent
# Exact narration substrings. Designed clocks are retimed to recorded voice after lock.
SCENES = [
('s01-tied-on-paper','night',False,[
 ('question','hook','question','I look at an airline punctuality table'),
 ('annual-a','national','annual-a','In 2024, their on-time rates'),
 ('annual-b','national','annual-b','In 2025, both are still about'),
 ('population','hook','population','United Express and other codeshare operators are excluded')]),
('s02-fifteen-minutes','paper',False,[
 ('success','definition','success','a flight succeeds if it completes'),
 ('boundary','definition','boundary','Exactly fifteen minutes late fails'),
 ('failures','definition','failures','A cancellation is a failure'),
 ('unknown','definition','unknown','If the outcome cannot be determined')]),
('s03-the-mixed-basket','paper',False,[
 ('national','national','pooled','Across all reported flights in 2023–2024'),
 ('networks','basket','networks','different network'),
 ('common','basket','common','opportunities both operators actually served')]),
('s04-same-trip-same-window','paper',False,[
 ('cell','cell','definition','My unit is a comparable cell'),
 ('example','cell','example','imagine Denver to Los Angeles'),
 ('reverse','cell','reverse','Los Angeles to Denver is a different cell'),
 ('scheduled','cell','scheduled','I match scheduled departures')]),
('s05-same-basket-same-line','paper',False,[
 ('weight','basket','weights','give both operators the same cell weight'),
 ('periods','basket','periods','I keep 2025 separate as replication'),
 ('line','line','rule','The decision line is two percentage points'),
 ('frozen','line','frozen',"I don't get to move the line after seeing the answer")]),
('s06-two-failed-checks','paper',False,[
 ('failed','gates','failed','Two earlier simulation checks failed'),
 ('redesign','gates','redesign','The interval was redesigned after those failures'),
 ('blocks','gates','blocks','whole stretches of calendar days together'),
 ('fresh','gates','fresh','Fresh simulation runs and a separate validation bank'),
 ('history','gates','history','that history belongs beside its result')]),
('s07-the-first-result','paper',False,[
 ('rates','primary','rates',"United's common-weighted timely-completion rate"),
 ('gap','primary','gap','The gap is 6.3 percentage points'),
 ('envelope','primary','envelope','The nominal 99% uncertainty envelope'),
 ('verdict','primary','verdict','The permitted verdict is'),
 ('scope','primary','scope','variability under repeated outcomes and calendar disruptions')]),
('s08-the-replication','paper',False,[
 ('seal','replicate','seal','I sealed that first result'),
 ('b-gap','replicate','gap','In 2025, the United advantage'),
 ('b-envelope','replicate','envelope','Again, the whole interval is above two points'),
 ('replicated','replicate','verdict','The same decisive label repeats'),
 ('limit','replicate','limit',"it isn't a repeated reversal of the national ranking")]),
('s09-the-nearby-tests','paper',False,[
 ('windows','sensitivity','windows','With one-hour or four-hour windows'),
 ('nearest','sensitivity','nearest','Matching reciprocal nearest departures'),
 ('limit','sensitivity','limit','Those are descriptive sensitivity checks')]),
('s10-whose-deadline','paper',False,[
 ('schedule','duration','schedule','United schedules about 4.5 minutes longer'),
 ('actual','duration','actual','its actual gate-to-gate duration is longer too'),
 ('shared','allowance','definition','shared elapsed-time allowance from their own scheduled departure'),
 ('shrink','allowance','shrink','The United gaps shrink to 2.6 and 4.3 points'),
 ('limit','allowance','limit','These exploratory results do not inherit the registered verdict')]),
('s11-leaving-late','paper',False,[
 ('late','departure','late','Southwest has noncancelled departures fifteen minutes or more late'),
 ('denominator','departure','denominator','The denominator is all scheduled flights'),
 ('timely','departure','timely','Including cancellations as failures'),
 ('limit','departure','limit','I haven\'t isolated a cause')]),
('s12-the-boundary-of-the-answer','paper',False,[
 ('overlap','boundary','coverage','Finally, this is a small overlap'),
 ('denver','boundary','denver','about eighty percent of the comparison weight touches Denver'),
 ('early','time','early','Before ten in the morning'),
 ('late','time','late','From four in the afternoon onward'),
 ('conclusion','conclusion','full','United kept its own timetable more often'),
 ('evidence','conclusion','evidence','whose deadline they had to meet')]),
('short-a','paper',True,[
 ('tie','national','short','look almost tied in national punctuality tables'),
 ('match','cell','short','I matched the same directional route'),
 ('result','replicate','short','Both whole nominal 99% uncertainty envelopes'),
 ('caveat','boundary','short','This is a small, Denver-heavy overlap')]),
('short-b','paper',True,[
 ('duration','duration','short','It also actually takes longer'),
 ('allowance','allowance','short','United\'s arrival advantages shrink'),
 ('departure','departure','short','Southwest also leaves fifteen-plus minutes late'),
 ('limit','allowance','limit','They show why the deadline matters')]),
('short-c','paper',True,[
 ('early','time','early','Before ten in the morning, United\'s gaps are near zero'),
 ('late','time','late',"From four in the afternoon onward, they're"),
 ('denver','boundary','denver','About eighty percent of the weight touches Denver'),
 ('limit','time','limit','It tells me to ask what an average has hidden')])]

def main():
    cues = {'status':'PRE-LOCK DRAFT · CLAIMS PROPOSED',
      'clock':'Designed animation clocks. Exact narration substrings; retime after script/voice lock. Each state has a settled hold; no synthesized voice.',
      'scenes':{}}
    story=(S.parent/'STORY.md').read_text()
    for name, bg, vertical, beats in SCENES:
        states=[]
        for i,(ident,component,phase,cue) in enumerate(beats):
            assert cue in story, cue
            states.append(dict(id=ident,component=component,phase=phase,at=i*7,still=i*7+3.5,cue=cue,path=f'renders/stills/{name}-{ident}.png'))
        definition=dict(background=bg,vertical=vertical,duration=len(states)*7,states=states)
        page=name+'.html'
        html='''<!doctype html><html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="../../../render/fonts/fonts.css"><link rel="stylesheet" href="../../../render/system.css"><link rel="stylesheet" href="episode.css">
<script src="../../../render/system.js"></script><script src="data.js"></script><script src="episode.js"></script>
<title>'''+name+''' · proposed pre-lock draft</title></head><body><script>
FA.register('''+json.dumps(definition,ensure_ascii=False)+''');
</script></body></html>
'''
        (S/page).write_text(html)
        cues['scenes'][page]=dict(format='vertical' if vertical else 'landscape',duration=definition['duration'],states=states)
        with (S/'PROGRESS.md').open('a') as f:
            f.write(f'\n- Built `{page}`: {len(states)} animated cue states; distinct '+('portrait composition' if vertical else 'landscape composition')+'; computed claim bindings, draft and scope labels. Rendering/visual QA pending.\n')
    (S/'CUES.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2)+'\n')
    print(len(SCENES),'pages;',sum(len(s['states']) for s in cues['scenes'].values()),'cue states')
if __name__=='__main__':main()
