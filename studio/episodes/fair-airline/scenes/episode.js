/* Pure cue-state animation. Observations are resolved exclusively by claim-key. */
(function(FT){
'use strict';
const FA=window.FA={},V=FT.value,D=window.SCENE_DATA;
const A='primary_2023_2024',B='replication_2025';
const P='derived_metrics.design.';
const color=i=>'var(--player-'+(i?'b':'a')+')';
const textColor=i=>'var(--player-'+(i?'b':'a-text')+')';
const T=(g,cls,x,y,size,html,extra={})=>FT.el(g,cls,Object.assign({left:x+'px',top:y+'px',fontSize:size+'px'},extra),html);
const rule=(g,x,y,w,h=2,c='currentColor')=>FT.el(g,'',{left:x+'px',top:y+'px',width:w+'px',height:h+'px',background:c,transformOrigin:'left'});
FA.num=(key,{digits=0,scale=1,sign=false,abs=false}={})=>{
 const ids=D.claim_ids[key];if(!ids?.length)throw Error('Unclaimed numeric value: '+key);
 let val=V(key)*scale;if(abs)val=Math.abs(val);
 if(typeof val!=='number'||!Number.isFinite(val))throw Error('Non-numeric label '+key);
 const txt=FT.fmt(val,digits,sign);
 return '<span class="fa-value" data-value-key="'+key+'" data-claims="'+ids.join(' ')+'" data-source="'+D.inputs[key].file+'" data-scale="'+scale+'" data-digits="'+digits+'" data-abs="'+abs+'" data-sign="'+sign+'">'+txt+'</span>';
};
const n=(key,digits=1,scale=1,sign=false)=>FA.num(key,{digits,scale,sign});
const yearA=()=>'<span class="fa-period">'+n('scene.year_a_start',0)+'–'+n('scene.year_a_end',0)+'</span>',yearB=()=>n('scene.year_b',0);
const period=i=>i?yearB():yearA();
const gap=i=>(i?B:A)+'.adjusted_gap_ua_minus_wn_pp';
const ex='EXPLORATORY · POST-HOC · NOT REGISTERED';
const cap=(g,v,html,y=v?1215:785,size=v?36:38)=>T(g,'caption',v?72:96,y,size,html,{width:(v?848:1728)+'px'});
const header=(g,v,kicker,title,{explore=false,night=false}={})=>{
 const k=FT.kicker(g,kicker+' · PROPOSED',{x:v?72:96,y:v?180:96,size:v?30:28,color:night?'var(--paper)':'var(--player-a-text)'});
 const h=FT.claim(g,title,{x:v?72:96,y:v?240:151,size:v?108:100,color:night?'var(--paper)':'var(--ink)'});h.style.width=(v?848:1728)+'px';
 const e=explore?T(g,'label',v?72:96,v?492:294,v?28:28,ex,{width:(v?848:1728)+'px',zIndex:3}):null;
 // Narrated states switch on words; repeated entry animation must not erase
 // their heading. Keep chart motion on its original local state clock.
 return t=>{const ht=window.__narratedAssembly?Math.max(t,1.2):t;FT.rise(k,ht,0);h.at(ht,.2);};
};
const scope=(g,v,{ids='FA-C001 · FA-C002',explore=false,note='Own arrival timetable · comparable operating services',source='Results · method · numerical verification'}={})=>{
 const link=(path,label)=>'<a href="../'+path+'">'+label+'</a>';
 const rows=v?[
 ['SCOPE','United / Southwest operated'],['','Domestic nonstop overlap · Express excluded'],['',note],
 ['SOURCE',link('analysis/FINDINGS.md','Findings')+' · '+link('CLAIMS.json','Claims')],['',ids],['STATUS','PRE-LOCK DRAFT · PROPOSED']
 ]:[['SOURCE',source+' · '+ids],['SCOPE','United / Southwest operated · domestic nonstop overlap · Express excluded'],['METHOD',note+' · PRE-LOCK DRAFT · CLAIMS PROPOSED']];
 const e=FT.source(g,rows,{x:v?72:96,y:v?1390:864,width:v?848:1728,size:v?26:24});
 e.dataset.exploratory=String(explore);return e;
};
const cards=(g,v,list,{y=v?555:365,height=v?175:365}={})=>{
 const q=FT.measureCards(g,{vertical:v,y,cards:list.map((c,i)=>({index:c.id??'METHOD',name:c.name,value:c.value??'',unit:c.unit??'',leader:'',stamp:c.stamp??'',color:c.color??'currentColor',start:.7+i*.15,contentStart:.9+i*.15,stampStart:1.6+i*.15}))});
 q.element.querySelectorAll('.ft-measure-card').forEach((e,i)=>{e.style.height=height+'px';if(v)e.style.top=(y+i*(height+20))+'px';if(list[i].id)e.dataset.claims=list[i].id;if(!list[i].stamp)e.querySelector('.ft-measure-stamp').style.display='none';});
 return t=>q.render(t);
};
// Bars always start at zero. Common axes per comparison. Numeric labels bind separately.
const bars=(g,v,rows,{y=v?585:375,max=100,step=v?145:115,labelWidth=v?300:480,width=v?475:1050,digits=2,unit='%',scale=1,abs=false,track=false}={})=>{
 const x=(v?72:96)+labelWidth;
 const rs=rows.map((r,i)=>{
  const yy=y+i*step,val=V(r.key)*(r.scale??scale),length=Math.abs(val)/max*width;
  const name=T(g,'label',v?72:96,yy,v?32:30,r.name,{width:(labelWidth-24)+'px',color:r.textColor??'currentColor'});
  const rail=rule(g,x,track?yy+3:yy+52,width,track?(v?36:42):2,'var(--rule-light)');
  const b=rule(g,x,yy+3,length,v?36:42,r.color??color(i%2));b.dataset.geometryKey=r.key;b.dataset.axisMax=max;
  const label=T(g,'number',x,yy+60,v?54:38,FA.num(r.key,{digits:r.digits??digits,scale:r.scale??scale,abs:r.abs??abs,sign:r.sign??false})+' '+(v?(unit.startsWith('MIN')?'MIN':unit.startsWith('PP')?'PP':unit.startsWith('%')?'%':unit):unit),{width:width+'px'});
  label.dataset.geometryKey=r.key;
  return t=>{FT.cut(name,t,.7+i*.15);FT.cut(rail,t,.7);b.style.transform='scaleX('+FT.p(t,1+i*.15,.5)+')';FT.cut(label,t,1.6+i*.15);};
 });return t=>rs.forEach(r=>r(t));
};
// N extension: one exact domain, separate observed/endpoint lanes, no range badge.
const ranges=(g,v,indices,{y=v?630:390,showInterval=true,line=true,sealed=false}={})=>{
 const left=v?160:455,width=v?660:1240,low=-1,high=12;
 const X=z=>left+(z-low)/(high-low)*width;
 const lineKey=P+'line_pp',confidence=n(P+'nominal_interval_pct',0);
 const axis=rule(g,left,y-28,width,2,'var(--rule-light)');
 const zeroLabel=T(g,'label',X(0)-12,y-91,v?30:28,FA.num(lineKey,{scale:0}),{width:'60px'});
 const ref=null;
 const refLabel=line?T(g,'label',X(V(lineKey))+16,y-91,v?30:28,'RULE +'+n(lineKey,0)+' POINTS',{width:(v?848:1240)+'px'}):null;
 const anim=[];
 indices.forEach((i,j)=>{
  const p=gap(i),yy=y+j*(v?220:170),estimate=V(p+'.estimate'),lo=V(p+'.interval[0]'),hi=V(p+'.interval[1]');
  const zero=rule(g,X(0),yy+(v?45:-20),2,v?68:72,'var(--field)');
  const reference=line?rule(g,X(V(lineKey)),yy+(v?45:-20),3,v?68:72,'var(--ink)'):null;
  const intervalVisible=showInterval||(sealed&&i===0);
  const title=T(g,'label',v?72:96,yy-10,v?30:32,(i?'B · ':'A · ')+period(i),{width:(v?450:345)+'px'});
  const sealTag=sealed&&i===0?T(g,'label',v?72:96,yy-56,26,'SEALED',{width:(v?450:345)+'px'}):null;
  const observed=T(g,'number',v?510:96,v?yy-10:yy+40,v?64:52,n(p+'.estimate',1,1,true)+' PP',{width:(v?410:345)+'px'});
  observed.dataset.geometryKey=p+'.estimate';
  const dot=FT.el(g,'dot ft-observed-dot',{left:(X(estimate)-15)+'px',top:(yy+(v?65:9))+'px',width:'30px',height:'30px'});dot.dataset.geometryKey=p+'.estimate';
  const bar=rule(g,X(lo),yy+(v?57:1),(hi-lo)/(high-low)*width,46,color(0));bar.dataset.geometryKey=p+'.interval';
  // Position observed dot after bar in stacking order.
  dot.style.zIndex=2;
  const ends=T(g,'label',left,yy+(v?113:66),v?30:30,n(p+'.interval[0]',2,1,true)+' to '+n(p+'.interval[1]',2,1,true)+' PP',{width:width+'px'});
  const level=T(g,'label',left,yy+(v?156:105),v?27:26,confidence+'% NOMINAL MISSINGNESS ENVELOPE',{width:width+'px'});
  ends.dataset.intervalLabel=p;level.dataset.intervalLabel=p;
  anim.push(t=>{FT.cut(title,t,.7);if(sealTag)FT.cut(sealTag,t,.7);FT.cut(zero,t,.7);if(reference)FT.cut(reference,t,.7);FT.cut(observed,t,1);FT.rise(dot,t,1,15,.4);bar.style.transform='scaleX('+FT.p(t,1.2,.7)+')';bar.style.visibility=intervalVisible?'visible':'hidden';[ends,level].forEach(e=>FT.cut(e,t,intervalVisible?2:Infinity));});
 });
 return t=>{[axis,zeroLabel,ref,refLabel].filter(Boolean).forEach(e=>FT.cut(e,t,.7));anim.forEach(r=>r(t));};
};
const chip=(g,v,html,y=v?1100:770)=>{const e=T(g,'claim chip',v?72:96,y,v?52:62,html,{padding:'10px 18px',width:'auto'});return t=>FT.cut(e,t,window.__narratedAssembly?0:2.6);};
const combine=(...rs)=>t=>rs.forEach(r=>r?.(t));
FA.register=def=>FT.scene({duration:def.duration,background:def.background,formats:{[def.vertical?'vertical':'landscape']:f=>{
 const v=def.vertical;if(v)f.classList.add('fa-portrait');
 const states=def.states.map(s=>{const g=FT.el(f,'fa-state');g.dataset.state=s.id;return {...s,g,render:FA[s.component](g,v,s.phase)};});
 return t=>{let index=0;states.forEach((s,i)=>{if(t>=s.at)index=i;});states.forEach((s,i)=>{s.g.style.display=i===index?'block':'none';s.render(Math.max(0,t-s.at));});window.__faState=states[index].id;f.className='frame '+(states[index].component==='conclusion'?'night':def.background)+(v?' fa-portrait':'');const grain=f.querySelector('.grain');if(v&&grain)grain.style.setProperty('--grain-shift',(Math.floor(t*30/2)%149)+'px');};
}}});
FA.hook=(g,v,phase)=>{
 const h=header(g,v,'The apparent tie',phase==='question'?['Tied on paper?']:['Which flights?'],{night:true});
 const c=cards(g,v,phase==='question'?[{name:'National punctuality',unit:'An appealing shortcut',stamp:'EQUALLY PUNCTUAL?'}]:[{name:'United operated',unit:'Mainline operating services',color:'var(--paper)'},{name:'Southwest operated',unit:'Comparable domestic nonstop services',color:'var(--paper)'},{name:'United Express',unit:'Excluded · other codeshare operators too',color:'var(--paper)'}]);
 scope(g,v,{ids:'FA-C001',note:'Operator-only comparison · no ticket recommendation'});return combine(h,c);
};
FA.national=(g,v,phase)=>{
 const annual=phase.startsWith('annual'),isB=phase==='annual-b';
 const h=header(g,v,'National context',[v?'A national near-tie':'The national bars look tied'],{night:annual});
 let rs=[];if(annual){
  const yr=isB?'2025':'2024';
  const base='descriptive_context.published_dot_annual.'+yr+'.operating_carriers.';
  const title=T(g,'label',96,335,32,(isB?yearB():n('scene.year_a_end',0))+' · OPERATING TABLE',{width:'1728px'});
  const headings=['OPERATOR','RANK','ON TIME'];const xs=[96,800,1120];
  headings.forEach((x,i)=>T(g,'label',xs[i],425,30,x));
  ['UA','WN'].forEach((op,i)=>{const yy=500+i*130;rule(g,96,yy-16,1728,2,'var(--paper)');T(g,'claim',96,yy,68,i?'Southwest':'United',{color:'var(--paper)'});T(g,'number',800,yy,64,n(base+op+'.rank',0));T(g,'number',1120,yy,64,n(base+op+'.rate_pct',2)+'%');});
  cap(g,false,'Adjacent operating ranks. Different flight collections.',760,40);
  scope(g,false,{ids:isB?'FA-C050 · FA-C051':'FA-C046 · FA-C047',source:'Official DOT annual operating tables · CONTEXT',note:'Unadjusted all-flights · operating carrier rows'});
  return t=>h(t);
 }
 const short=phase==='short';
 const rows=(short?[0]:[0,1]).flatMap(i=>['UA','WN'].map((op,j)=>({name:(j?'Southwest':'United')+'<br>'+period(i),key:(i?B:A)+'.unmatched_all_flights_on_time_pct.'+op+'.estimate',color:color(j),textColor:textColor(j)})));
 const b=bars(g,v,rows,{y:v?560:355,step:v?220:105,max:100,width:v?450:1050});
 cap(g,v,'UNADJUSTED ALL-FLIGHTS · zero-based scale',v?1250:805,v?32:30);
 scope(g,v,{ids:'FA-C007 · FA-C026',note:v?'Own timetable · cancellations fail':'Own timetable · no national-to-matched reversal claim'});return combine(h,b);
};
FA.definition=(g,v,phase)=>{
 const minutes=n(P+'late_failure_minutes',0);
 const h=header(g,v,'Define the score',[phase==='unknown'?'Unknowns stay in':'What counts as on time?']);
 const lists={
 success:[{id:'FA-C005',name:'Timely completion',value:'LESS THAN '+minutes+' MIN',unit:'Own published arrival timetable',stamp:'SUCCESS'}],
 boundary:[{id:'FA-C005',name:'Less than '+minutes+' minutes',unit:'Completed without cancellation/diversion',stamp:'PASS'},{id:'FA-C005',name:'Exactly '+minutes+' minutes',unit:'At the boundary or later',stamp:'FAIL'}],
 failures:[{id:'FA-C005',name:'Cancelled',unit:'Remains in scheduled denominator',stamp:'FAIL'},{id:'FA-C005',name:'Diverted',unit:'Remains in scheduled denominator',stamp:'FAIL'}],
 unknown:[{id:'FA-C005',name:'Indeterminate outcome',unit:'Primary score counts failure',stamp:'FAIL'},{id:'FA-C005',name:'Missingness envelope',unit:'Allows for unknown outcomes',stamp:'RETAINED'}]};
 const c=cards(g,v,lists[phase]);cap(g,v,'Scheduled services do not disappear from the denominator.');
 scope(g,v,{ids:'FA-C005',source:'Amendment 1 · scoring definition · CONTEXT',note:'Timely completion against each operator’s own arrival timetable'});return combine(h,c);
};
FA.basket=(g,v,phase)=>{
 const titles={networks:'Different baskets',common:'Common opportunities',weights:'Same cell influence',periods:'Separate periods'};
 const h=header(g,v,'A fairer comparison',[titles[phase]]);
 let list=phase==='networks'?[{name:'United network',unit:'Own route / airport / time mix'},{name:'Southwest network',unit:'A different route / airport / time mix'}]:phase==='common'?[{name:'Both served the cell',unit:'Restrict to common opportunities'},{name:'Only one served it',unit:'Outside this comparison'}]:phase==='periods'?[{id:'FA-C006',name:'A · '+yearA(),unit:'First confirmation basket'},{id:'FA-C025',name:'B · '+yearB(),unit:'Separate replication basket'}]:[{name:'Within a cell',unit:'Calculate both success rates'},{name:'Pooled schedules',unit:'Weight by combined scheduled count'},{name:'Same influence',unit:'Common weight for both operators'}];
 if(phase==='networks'||phase==='common'){
  ['UA','WN'].forEach((op,i)=>{
   const key=A+'.matched_cell_coverage_pct.'+op+'.estimate',pct=V(key),y=415+i*185,x=470,w=1300;
   T(g,'label',96,y,42,i?'Southwest':'United',{width:'340px',color:textColor(i)});
   rule(g,x,y,w,55,'var(--rule-light)');const inside=rule(g,x,y,w*pct/100,55,color(i));inside.dataset.geometryKey=key;
   T(g,'number',x,y+75,44,n(key,1)+'% INSIDE',{width:'600px'});
   T(g,'label',x+690,y+82,30,'REMAINDER OUTSIDE',{width:'590px'});
  });
  cap(g,false,'Comparable cells are a small slice of each network · '+yearA(),800,36);
  scope(g,false,{ids:'FA-C006',note:'Share of each operator’s scheduled flights · zero to 100%'});
  return t=>h(t);
 }
 const c=cards(g,v,list);cap(g,v,phase==='weights'?'Busy shared cells matter more, equally for both sides.':'SCHEMATIC · the comparison population changes');
 scope(g,v,{ids:'FA-C005 · FA-C006 · FA-C025',note:'Common scheduled-count weights · each operator’s own timetable'});return combine(h,c);
};
FA.cell=(g,v,phase)=>{
 const h=header(g,v,'The comparable cell',[v?'Same trip. Same window.':'Same trip, same window']);
 const x=v?245:450,w=v?640:1290,X=hour=>x+hour/24*w;
 const top=v?670:440,step=v?130:100;
 T(g,'label',v?72:96,v?555:325,v?28:30,'DEN → LAX · 15 JAN 2025 · LOCAL SCHEDULED DAY',{width:(v?848:1728)+'px'});
 const highlight=FT.el(g,'fa-grid-cell',{left:X(10)+'px',top:(top-15)+'px',width:(X(12)-X(10))+'px',height:(step+35)+'px',background:'var(--rule-light)'});
 for(let hr=0;hr<=24;hr+=2){rule(g,X(hr),top-15,1,step*2+35,'var(--rule-light)');if(hr%4===0)T(g,'label',X(hr)-(hr===24?35:8),top-65,v?26:28,String(hr).padStart(2,'0'),{width:'60px'});}
 [['United',[6.2,10.25,11.6,16.3,20.1]],['Southwest',[7.1,10.8,14.4,18.2,21.7]],['LAX → DEN',[8.2,10.5,17.4]]].forEach(([name,ticks],i)=>{
  const yy=top+i*step;
  T(g,'label',v?72:96,yy-15,v?26:32,name,{width:(v?165:335)+'px'});
  rule(g,x,yy,w,2);ticks.forEach(hr=>rule(g,X(hr),yy-18,4,36,i===2?'var(--field)':color(i)));
 });
 T(g,'label',v?72:96,top+step*2+45,v?30:32,'REVERSE DIRECTION = DIFFERENT CELL',{width:(v?848:1728)+'px'});
 T(g,'label',v?72:96,v?1170:785,v?32:34,'10:00–12:00 · '+n(P+'departure_window_hours',0)+'-HOUR CELL HIGHLIGHTED',{width:(v?848:1728)+'px'});
 cap(g,v,'SCHEMATIC TICKS · scheduled departures only · no outcomes',v?1240:735,v?30:28);
 scope(g,v,{ids:'FA-C005',source:'Amendment 1 · cell definition · schematic schedule ticks',note:v?'Directional route · local scheduled window':'Directional route · same local scheduled day · scheduled departure window'});
 return t=>{h(t);highlight.style.opacity=FT.p(t,.5,.4);};
};
FA.line=(g,v,phase)=>{
 const h=header(g,v,'Registered pair rule',[phase==='frozen'?'The line stays fixed':'Clear the whole line']);
 const c=cards(g,v,[{id:'FA-C004',name:'Materiality line',value:'+'+n(P+'line_pp',0)+' POINTS',unit:'Extra timely completion per '+n(P+'per_scheduled_flights',0)+' schedules'},{id:'FA-C004',name:'Entire envelope',unit:'Must be above the line',stamp:phase==='frozen'?'FIXED BEFORE OUTCOMES':'WHOLE INTERVAL'}]);
 cap(g,v,'Post-pilot and post-failed-gate · pre-confirmation rule');scope(g,v,{ids:'FA-C004',source:'Amendment 1 · registered single-pair rule',note:'Own timetable · amended use and scope after exploratory pilot'});return combine(h,c);
};
FA.gates=(g,v,phase)=>{
 const title=phase==='failed'?'The failed checks belong here':phase==='blocks'?'Keep calendar shocks together':'Redesign before outcomes';
 const h=header(g,v,'Outcome-blind history',[title]);
 const list=phase==='failed'?[{name:'Earlier simulation gate',unit:'Known-answer synthetic outcomes',stamp:'FAIL'},{name:'Next simulation gate',unit:'Known-answer synthetic outcomes',stamp:'FAIL'}]:phase==='redesign'?[{name:'Earlier gates',unit:'Failed before confirmation outcomes',stamp:'FAIL / FAIL'},{name:'Interval redesign',unit:'Real flight outcomes stayed closed',stamp:'AMENDMENT'}]:phase==='blocks'?[{id:'FA-C005',name:n(P+'block_days',0)+'-day network blocks',unit:'Calendar disruption can persist and travel'},{name:'Fixed schedules',unit:'Repeated outcomes / calendar shocks'}]:phase==='fresh'?[{id:'FA-C073',name:'Fresh selection runs',unit:'Specified synthetic checks passed',stamp:'PASS'},{id:'FA-C074',name:'Independent validation',unit:'Separate bank passed specified checks',stamp:'PASS'},{id:'FA-C075',name:'Then open outcomes',unit:'Pre-access method and results seals',stamp:'AFTER'}]:[{name:'FAIL → FAIL',unit:'Disclosed beside the result'},{name:'REDESIGN → FRESH PASS',unit:'Not a universal disruption guarantee'},{name:'CONFIRMATION OUTCOMES',unit:'Opened after pre-access seals'}];
 const c=cards(g,v,list);cap(g,v,'Schedule fields were used; public rankings were not perfectly unseen.',785,34);
 scope(g,v,{ids:'FA-C004 · FA-C005 · FA-C073–075',source:'Both amendments · analysis PROGRESS · gate validation',note:'Synthetic checks under specified conditions · no universal guarantee'});return combine(h,c);
};
FA.primary=(g,v,phase)=>{
 const h=header(g,v,'A · first confirmation',[phase==='rates'?'Compare the same basket':phase==='gap'?'An observed gap':'The whole envelope clears']);
 let plot;if(phase==='rates'){
  plot=bars(g,v,['UA','WN'].map((op,i)=>({name:i?'Southwest':'United',key:A+'.weighted_matched_secondary_rates_pct.'+op+'.on_time.estimate',color:color(i),textColor:textColor(i)})),{y:390,step:150});
  cap(g,v,'Common-weighted timely completion · '+yearA());
 }else{
  plot=ranges(g,v,[0],{y:435,showInterval:phase!=='gap'});
  if(phase==='scope')cap(g,v,'Fixed schedules · repeated outcomes and calendar shocks<br>Not census counting error or a prediction for the next ticket.',715,38);
 }
 const verdict=phase==='verdict'?chip(g,v,'UNITED ADVANTAGE ABOVE TWO POINTS'):null;
 scope(g,v,{ids:'FA-C001 · FA-C004 · FA-C009 · FA-C011',note:'Own timetable · nominal '+n(P+'nominal_interval_pct',0)+'% missingness envelope'});return combine(h,plot,verdict);
};
FA.replicate=(g,v,phase)=>{
 const short=phase==='short',indices=phase==='seal'?[0]:[0,1];
 const h=header(g,v,'Separate replication period',[short?'A separate test':phase==='limit'?'A comparable-service result':phase==='verdict'?'A separate test repeats':'A separate period']);
 const plot=ranges(g,v,indices,{y:v?650:405,showInterval:phase!=='gap',sealed:!v});
 const badge=phase==='verdict'||short?chip(g,v,'REPLICATED',v?1250:770):null;
 if(phase==='seal')cap(g,v,'B remains unopened. It cannot rewrite A.',740,40);
 if(phase==='limit')cap(g,v,'United already led nationally in the first period.<br>This is not a repeated reversal of national rankings.',755,34);
 scope(g,v,{ids:'FA-C001 · FA-C002 · FA-C003 · FA-C004',note:v?'Own timetable · cancellations fail':'Own timetable · nominal '+n(P+'nominal_interval_pct',0)+'% envelopes · separate schedules'});return combine(h,plot,badge);
};
FA.sensitivity=(g,v,phase)=>{
 const h=header(g,v,'Registered descriptive checks',['Nearby tests, same direction']);
 const rows=phase==='nearest'?['reciprocal_nearest_30min']:['window_1h','window_4h'];
 const xs=[96,960,1390];['MATCH','A · '+yearA(),'B · '+yearB()].forEach((s,i)=>T(g,'label',xs[i],365,30,s));
 rows.forEach((name,j)=>{const yy=450+j*145;rule(g,96,yy-20,1728);const label=name==='reciprocal_nearest_30min'?'Reciprocal nearest · '+n('scene.window_30min',0)+' min':n('scene.window_'+(j?'4h':'1h'),0)+'-hour window';T(g,'label',96,yy,36,label,{width:'800px'});[A,B].forEach((p,i)=>T(g,'number',xs[i+1],yy,54,n(p+'.sensitivities.'+name+'.gap_ua_minus_wn_pp.estimate',1,1,true)+' PP'));});
 cap(g,v,'REGISTERED DESCRIPTIVE SENSITIVITIES · NO ADDITIONAL VERDICT',745,34);
 if(phase==='limit')cap(g,v,'Consistency does not expand this result to every flight.',800,34);
 scope(g,v,{ids:phase==='nearest'?'FA-C020 · FA-C038':'FA-C021 · FA-C022 · FA-C039 · FA-C040',note:'Own timetable · no replacement of registered primary result'});return t=>h(t);
};
FA.duration=(g,v,phase)=>{
 const both=phase==='actual'||phase==='short';
 const h=header(g,v,'Whose deadline?',[v?'Longer schedule. Longer trip.':'Longer schedules, longer actual trips'],{explore:true});
 const rows=[0,1].flatMap(i=>[{name:'Scheduled · '+period(i),key:(i?'B':'A')+'.schedule.UA_minus_WN',color:color(0),sign:true},...(both?[{name:'Actual · '+period(i),key:(i?'B':'A')+'.completed_cell_means.actual.UA_minus_WN',color:'var(--field)',sign:true}]:[])]);
 if(v)T(g,'label',72,550,26,'UNITED − SOUTHWEST · MINUTES',{width:'848px'});
 const plot=bars(g,v,rows,{y:v?605:365,max:8,step:v?140:102,digits:1,unit:'MIN · UNITED − SOUTHWEST',labelWidth:v?345:520,width:v?440:970});
 const note=both?'Actual-duration subset weight: '+n('A.completed_cell_means.weight_share',2,100)+'% / '+n('B.completed_cell_means.weight_share',2,100)+'%<br>Cells with completed flights from both operators.':'Common cells · common weights · gate-to-gate block duration';
 cap(g,v,note,v?1215:800,v?30:30);scope(g,v,{ids:'FA-C054 · FA-C062',explore:true,note:v?'Completed-cell subset · no padding inference':'United minus Southwest minutes · no deliberate-padding inference'});return combine(h,plot);
};
FA.allowance=(g,v,phase)=>{
 const definition=phase==='definition',limit=phase==='limit';
 const h=header(g,v,'Exploratory deadline check',[definition?'Elapsed from departure':limit?'No inherited verdict':v?'Shared deadline. Smaller gap.':'A shared allowance shrinks the gap'],{explore:true});
 let plot;if(definition){plot=cards(g,v,[{name:'Own timetable',unit:'Each operator’s published arrival time'},{name:'Shared allowance',unit:'Midpoint cell-mean scheduled duration'},{name:'Start at own departure',unit:'Same late boundary · not one wall-clock deadline'}]);}
 else{
 const rows=[0,1].flatMap(i=>[{name:'Own · '+period(i),key:gap(i)+'.estimate',sign:true,color:color(0)}, {name:'Shared · '+period(i),key:(i?'B':'A')+'.common_mid.UA_minus_WN',scale:100,sign:true,color:'var(--field)'}]);
 if(v)T(g,'label',72,550,26,'UNITED − SOUTHWEST · POINTS',{width:'848px'});
 plot=bars(g,v,rows,{y:v?605:355,step:v?140:100,max:10,digits:1,unit:'PP · UNITED − SOUTHWEST',labelWidth:v?310:520,width:v?455:970});
 cap(g,v,limit?'Deadline sensitivity ≠ identified padding or ticket advice.':'Shared allowance starts at each scheduled departure.<br>Cancellations / diversions fail; cutoff unchanged.',v?1215:790,v?32:34);
 }
 scope(g,v,{ids:'FA-C001 · FA-C002 · FA-C055 · FA-C063',explore:true,note:v?'Elapsed shared allowance · cancellations fail':'Descriptive exploratory check · no inherited registered verdict'});return combine(h,plot);
};
FA.departure=(g,v,phase)=>{
 const timely=phase==='timely';
 const h=header(g,v,'Before the arrival deadline',[timely?'Timely-departure advantage':'Southwest leaves late more often'],{explore:true});
 const key=timely?'dep_timely':'dep_late';
 const rows=[0,1].map(i=>({name:(timely?'United advantage':'Southwest excess')+'<br>'+period(i),key:(i?'B':'A')+'.'+key+'.UA_minus_WN',color:color(timely?0:1),scale:100,abs:!timely}));
 const plot=bars(g,v,rows,{y:v?610:390,step:v?195:155,max:16,digits:1,unit:'POINTS',labelWidth:v?365:570,width:v?420:950});
 let note=timely?'Timely score: cancellations count as failures.':phase==='denominator'?'ALL SCHEDULED denominator<br>Cancellations are not observed late departures.':'Noncancelled departures ≥ '+n(P+'late_failure_minutes',0)+' minutes late';
 if(phase==='limit')note='Arrival padding cannot mechanically explain departure delays.<br>Scheduled choices and operating circumstances remain bundled.';
 cap(g,v,note,v?1215:780,v?32:36);
 scope(g,v,{ids:'FA-C056 · FA-C064',explore:true,note:v?'All scheduled denominator · diversions eligible':'Common cell weights · all scheduled denominator · diversions eligible'});return combine(h,plot);
};
FA.boundary=(g,v,phase)=>{
 const denver=phase==='denver',short=phase==='short';
 const h=header(g,v,'Bound the population',[denver?'Denver carries the weight':'A small overlap'],{explore:denver||short});
 let plot;if(denver){
 plot=bars(g,v,[0,1].map(i=>({name:'Touches Denver<br>'+period(i),key:'derived_metrics.'+(i?'B':'A')+'.denver.weight_share',scale:100,color:'var(--field)'})),{y:v?620:405,step:v?180:155,max:100,digits:1,unit:'% OF COMPARISON WEIGHT',labelWidth:v?350:540,width:v?430:980});
 cap(g,v,'Weight share, not passenger share or a nationwide guarantee.',v?1215:785,v?34:38);
 }else{
 if(v)T(g,'label',72,550,26,'SHARE OF OPERATOR SCHEDULES',{width:'848px'});
 plot=bars(g,v,[0,1].flatMap(i=>['UA','WN'].map((op,j)=>({name:(j?'Southwest':'United')+' · '+period(i),key:(i?B:A)+'.matched_cell_coverage_pct.'+op+'.estimate',color:color(j),textColor:textColor(j)}))),{y:v?605:355,step:v?123:112,max:100,digits:2,unit:'% OF OPERATOR SCHEDULES',labelWidth:v?330:560,width:v?430:950,track:v&&short});
 cap(g,v,short?'Small overlap · Denver-heavy · own timetable.<br>Shared-allowance check: '+n('A.common_mid.UA_minus_WN',1,100)+' / '+n('B.common_mid.UA_minus_WN',1,100)+' PP.':'Most operating schedules lie outside the comparable basket.',v?1215:800,v?30:36);
 }
 scope(g,v,{ids:denver?'FA-C058 · FA-C066':short?'FA-C006 · FA-C025 · FA-C055 · FA-C063':'FA-C006 · FA-C025',explore:denver||short,note:v?'Own timetable · no best-airline ranking':'Operator only · small overlap · no population-wide airline ranking'});return combine(h,plot);
};
const dayKey=open=>'<svg width="72" height="24" viewBox="0 0 72 24" style="vertical-align:middle" aria-hidden="true"><line x1="0" x2="72" y1="12" y2="12" stroke="var(--ink)" stroke-width="3" '+(open?'stroke-dasharray="10 6"':'')+'/><circle cx="36" cy="12" r="6" fill="'+(open?'var(--paper)':'var(--ink)')+'" stroke="var(--ink)" stroke-width="3"/></svg>';
FA.time=(g,v,phase)=>{
 const annotation=(band,p)=>{const key='derived_metrics.'+p+'.time.'+band+'.gap_pp';return '<span data-geometry-key="'+key+'">'+p+' '+n(key,1,1,true)+' PP</span>';};
 const h=header(g,v,'Local scheduled departure',[v?'The gap grows through the day':'The gap grows through the day'],{explore:true});
 const left=v?150:195,top=v?635:390,width=v?735:1420,height=v?415:280;
 const X=b=>left+(b-2)/9*width,Y=z=>top+(16-z)/18*height;
 const svg=FT.el(g,'fa-day-chart',{left:'0px',top:'0px',width:(v?1080:1920)+'px',height:(v?1920:1080)+'px'});
 let out='<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" aria-label="Exploratory United minus Southwest own-timetable gap by two-hour local departure band">';
 [0,2,8,16].forEach(z=>{out+='<line x1="'+left+'" x2="'+(left+width)+'" y1="'+Y(z)+'" y2="'+Y(z)+'" stroke="var(--ink)" stroke-width="'+(z===0?3:1)+'" '+(z===2?'stroke-dasharray="8 6"':'')+'/>';T(g,'label',v?72:96,Y(z)-(z===2?25:7),v?26:28,z===2?'+'+n(P+'line_pp',0):String(z),{width:'80px'});});
 ['A','B'].forEach((p,i)=>{
  const c='var(--ink)';for(let b=2;b<=11;b++){
   const key='derived_metrics.'+p+'.bands.'+b+'.gap_pp',weight='derived_metrics.'+p+'.bands.'+b+'.weight_pct',fade=V(weight)<1?.38:1;
   if(b>2)out+='<line x1="'+X(b-1)+'" y1="'+Y(V('derived_metrics.'+p+'.bands.'+(b-1)+'.gap_pp'))+'" x2="'+X(b)+'" y2="'+Y(V(key))+'" stroke="'+c+'" stroke-width="5" '+(i?'stroke-dasharray="12 8" ':'')+'opacity="'+fade+'"/>';
   out+='<circle data-geometry-key="'+key+'" data-weight-key="'+weight+'" cx="'+X(b)+'" cy="'+Y(V(key))+'" r="'+(i?7:9)+'" fill="'+(i?'var(--paper)':c)+'" stroke="'+c+'" stroke-width="4" opacity="'+fade+'"/>';
  }
 });svg.innerHTML=out+'</svg>';
 T(g,'label',left,top-(v?40:62),v?26:28,v?'UNITED − SOUTHWEST · POINTS':'UNITED − SOUTHWEST · POINTS · 2-HOUR BANDS',{width:(v?735:1420)+'px'});
 [2,4,6,8,10].forEach(b=>T(g,'label',X(b)-18,top+height+18,v?26:28,String(b*2).padStart(2,'0'),{width:'65px'}));
 if(v)T(g,'label',left,top+height+65,26,'TWO-HOUR BANDS · LOCAL SCHEDULED DEPARTURE',{width:'735px'});
 T(g,'label',v?72:1030,v?550:328,v?28:28,'A '+yearA()+' '+dayKey(false)+' &nbsp; B '+yearB()+' '+dayKey(true),{width:(v?848:790)+'px'});
 T(g,'label',v?72:96,v?1160:735,v?32:30,'BEFORE '+n('scene.before_10',0)+':00 &nbsp; '+annotation('before_10','A')+' &nbsp; '+annotation('before_10','B'),{width:(v?848:790)+'px'});
 T(g,'label',v?72:1030,v?1210:735,v?32:30,'FROM '+n('scene.from_16',0)+':00 &nbsp; '+annotation('from_16','A')+' &nbsp; '+annotation('from_16','B'),{width:(v?848:790)+'px'});
 cap(g,v,'22–24 FADED: <1% WEIGHT · A '+n('derived_metrics.A.bands.11.weight_pct',2)+'% / B '+n('derived_metrics.B.bands.11.weight_pct',2)+'%<br>No overlap before 04:00 · no band intervals · no causal explanation',v?1270:790,v?26:28);
 scope(g,v,{ids:'FA-C060 · FA-C068 · FA-C076–095',explore:true,note:v?'Own timetable · cancellations fail':'Own timetable · exploratory bands · reference line confers no verdict'});
 return t=>{h(t);svg.style.opacity=FT.p(t,.5,.5);};
};
FA.conclusion=(g,v,phase)=>{
 const h=header(g,v,'What the result permits',[phase==='evidence'?'Follow the evidence':'Own timetable. Comparable flights.'],{night:true});
 const c=cards(g,v,phase==='evidence'?[{name:'Registered method',unit:'<a href="../METHOD.md">METHOD</a> · <a href="../analysis/amendment/AMENDMENT-1.md">Amendment 1</a> · <a href="../analysis/amendment2/AMENDMENT-2.md">Amendment 2</a>'},{name:'Results and checks',unit:'<a href="../analysis/FINDINGS.md">FINDINGS</a> · <a href="../CLAIMS.json">CLAIMS</a> · <a href="../analysis/claims_check.json">Numerical verification</a>'},{name:'Context and review',unit:'<a href="../analysis/CONTEXT.md">CONTEXT</a> · <a href="../analysis/review.md">Review</a>'}]:[{name:'United kept its timetable',unit:'More often on comparable operating services'},{name:'Small, Denver-heavy overlap',unit:'Express excluded · temporal heterogeneity'},{name:'No ticket recommendation',unit:'No faster-travel, rebooking or causal claim'}]);
 cap(g,v,'Ask which flights went into the average — and whose deadline.',790,40);
 scope(g,v,{ids:'FA-C001 · FA-C002 · FA-C003',note:'Replicated own-timetable difference · draft evidence and review links'});return combine(h,c);
};
})(window.FT);
