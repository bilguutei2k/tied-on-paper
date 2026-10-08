// Native Chromium geometry audit for all cue states; text uses actual font metrics.
import {spawn} from 'node:child_process';
import {readFileSync,writeFileSync,mkdtempSync,rmSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
const dir=dirname(fileURLToPath(import.meta.url));
class CDP {
  constructor(url) { this.ws = new WebSocket(url); this.id = 0; this.pending = new Map(); this.listeners = []; }
  open() {
    return new Promise((res, rej) => {
      this.ws.onopen = res;
      this.ws.onerror = rej;
      this.ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.id && this.pending.has(msg.id)) {
          const { resolve: ok, reject } = this.pending.get(msg.id);
          this.pending.delete(msg.id);
          msg.error ? reject(new Error(msg.error.message)) : ok(msg.result);
        } else this.listeners.forEach((l) => l(msg));
      };
    });
  }
  send(method, params = {}, sessionId) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params, sessionId }));
    return new Promise((ok, reject) => this.pending.set(id, { resolve: ok, reject }));
  }
  once(method, sessionId) {
    return new Promise((ok) => {
      const l = (m) => { if (m.method === method && m.sessionId === sessionId) { this.listeners.splice(this.listeners.indexOf(l), 1); ok(m.params); } };
      this.listeners.push(l);
    });
  }
}


const profile=mkdtempSync(resolve(tmpdir(),'fa-audit-'));
const chrome=spawn(process.env.CHROME,['--headless','--remote-debugging-port=0','--hide-scrollbars','--force-device-scale-factor=1','--font-render-hinting=none','--user-data-dir='+profile,'about:blank'],{stdio:['ignore','ignore','pipe']});
let cdp;const errors=[],checks=[],narrated_checks=[];
try{
 const endpoint=await new Promise((ok,fail)=>{let out='';chrome.stderr.on('data',d=>{out+=d;const m=out.match(/DevTools listening on (ws:\/\/\S+)/);if(m)ok(m[1]);});chrome.on('exit',()=>fail(Error(out.slice(-400))));});
 cdp=new CDP(endpoint);await cdp.open();const {targetId}=await cdp.send('Target.createTarget',{url:'about:blank'});const {sessionId}=await cdp.send('Target.attachToTarget',{targetId,flatten:true});
 await cdp.send('Page.enable',{},sessionId);await cdp.send('Runtime.enable',{},sessionId);
 cdp.listeners.push(m=>{if(m.sessionId===sessionId&&m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description??m.params.exceptionDetails.text);});
 const cues=JSON.parse(readFileSync(resolve(dir,'CUES.json')));
 for(const [page,info] of Object.entries(cues.scenes)){
  const v=info.format==='vertical';await cdp.send('Emulation.setDeviceMetricsOverride',{width:v?1080:1920,height:v?1920:1080,deviceScaleFactor:1,mobile:false},sessionId);
  const loaded=cdp.once('Page.loadEventFired',sessionId);await cdp.send('Page.navigate',{url:pathToFileURL(resolve(dir,page)).href+'?format='+info.format},sessionId);await loaded;
  await cdp.send('Runtime.evaluate',{expression:'document.fonts.ready',awaitPromise:true},sessionId);
  for(const state of info.states){
   const evaluate=await cdp.send('Runtime.evaluate',{expression:`(()=>{
    __ft.seek(${state.still});
    const safe=${JSON.stringify({left:72,right:920,top:220,bottom:1500})};if(!${v})Object.assign(safe,{left:96,right:1824,top:96,bottom:984});
    const active=document.querySelector('.fa-state[data-state="${state.id}"]');
    const visible=e=>{for(let p=e;p&&p!==document.body;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return false;}return true;};
    const boxes=[],issues=[];const walker=document.createTreeWalker(active,NodeFilter.SHOW_TEXT);let node;
    while(node=walker.nextNode()){
     if(!node.textContent.trim()||!visible(node.parentElement))continue;
     const owner=node.parentElement.closest('.ft-measure-name,.ft-measure-unit,.ft-measure-stamp,.ft-measure-index,.ft-measure-value,.label,.number,.caption,.source,.claim')??node.parentElement;
     const range=document.createRange();range.selectNodeContents(node);const font=parseFloat(getComputedStyle(node.parentElement).fontSize);
     for(const r of range.getClientRects()){
      if(r.width<1||r.height<1)continue;const b={text:node.textContent.trim(),cls:owner.className,x:r.x,y:r.y,right:r.right,bottom:r.bottom,font,owner:owner.className+'@'+Math.round(owner.getBoundingClientRect().top)};boxes.push(b);
      if(r.x<safe.left-1||r.right>safe.right+1||r.y<safe.top-1||r.bottom>safe.bottom+1)issues.push({kind:'safe edge',...b});
      if(font<24)issues.push({kind:'small font',...b});
      const card=node.parentElement.closest('.ft-measure-card');if(card){const p=card.getBoundingClientRect();if(r.x<p.x||r.right>p.right||r.y<p.y||r.bottom>p.bottom)issues.push({kind:'card overflow',...b});}
     }
    }
    for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){const a=boxes[i],b=boxes[j];if(a.owner===b.owner)continue;const ox=Math.min(a.right,b.right)-Math.max(a.x,b.x),oy=Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y);if(ox>2&&oy>3)issues.push({kind:'overlap',a:a.text,b:b.text,ox,oy});}
    for(const e of active.querySelectorAll('.chip'))if(visible(e)&&e.getBoundingClientRect().bottom>(${v}?1205:864)-12)issues.push({kind:'badge/source clearance',text:e.textContent});
    const labels=[...active.querySelectorAll('[data-value-key]')].filter(visible).map(e=>({key:e.dataset.valueKey,claims:e.dataset.claims,text:e.textContent,source:e.dataset.source,scale:e.dataset.scale,digits:e.dataset.digits,abs:e.dataset.abs,sign:e.dataset.sign}));
    return JSON.stringify({page:${JSON.stringify(page)},state:${JSON.stringify(state.id)},issues,labels,box_count:boxes.length});
   })()`,returnByValue:true},sessionId);
   if(evaluate.exceptionDetails)throw Error(evaluate.exceptionDetails.text);checks.push(JSON.parse(evaluate.result.value));
   const narrated=await cdp.send('Runtime.evaluate',{expression:`(()=>{
    window.__narratedAssembly=true;__ft.seek(${state.at});
    const active=document.querySelector('.fa-state[data-state="${state.id}"]');
    const spans=[...active.querySelectorAll('.claim .line span')];
    const visible=e=>{for(let p=e;p&&p!==document.body;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return false;}return true;};
    const issues=[];
    if(!spans.length||spans.some(e=>!visible(e)||Math.abs(new DOMMatrixReadOnly(getComputedStyle(e).transform).m42)>.01))issues.push('heading hidden at state onset');
    const source=active.querySelector('.source');if(!source||!visible(source))issues.push('source hidden at state onset');
    const chip=active.querySelector('.chip');if(chip&&!visible(chip))issues.push('badge delayed after state cue');
    window.__narratedAssembly=false;__ft.seek(${state.still});
    return JSON.stringify({page:${JSON.stringify(page)},state:${JSON.stringify(state.id)},issues});
   })()`,returnByValue:true},sessionId);
   if(narrated.exceptionDetails)throw Error(narrated.exceptionDetails.text);narrated_checks.push(JSON.parse(narrated.result.value));
  }
 }
 const source_sha256=Object.fromEntries(['episode.js','episode.css','data.js','CUES.json','browser_audit.mjs','../STORY.md','../../../render/system.js','../../../render/system.css'].map(file=>[file,createHash('sha256').update(readFileSync(resolve(dir,file))).digest('hex')]));
 const issue_count=checks.reduce((n,c)=>n+c.issues.length,0)+narrated_checks.reduce((n,c)=>n+c.issues.length,0);
 const report={status:errors.length||issue_count?'FAIL':'PASS',source_sha256,errors,checks,narrated_checks,issue_count};
 writeFileSync(resolve(dir,'browser_qa.json'),JSON.stringify(report,null,2)+'\n');
 console.log('Chromium audit:',checks.length,'states,',report.issue_count,'geometry flags,',errors.length,'runtime errors.');
 for(const c of checks.filter(c=>c.issues.length))console.log(c.page,c.state,JSON.stringify(c.issues.map(x=>({kind:x.kind,text:x.text,a:x.a,b:x.b}))).slice(0,650));
 if(errors.length||report.issue_count)throw Error('Audit failed: '+report.issue_count+' geometry issues; '+errors.join('; '));
}finally{cdp?.ws.close();chrome.kill('SIGKILL');rmSync(profile,{recursive:true,force:true,maxRetries:4,retryDelay:50});}
