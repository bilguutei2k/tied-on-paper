// Provenance, arbitrary seeks and semantics; actual browser audit via --browser.
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const dir=dirname(fileURLToPath(import.meta.url));
const cues=JSON.parse(readFileSync(resolve(dir,'CUES.json')));
class Element {
 constructor(tag='div'){this.tagName=tag;this.style={setProperty(k,v){this[k]=v;}};this.children=[];this.dataset={};this.attributes={};this._html='';this.className='';this.classList={add:n=>this.className+=' '+n};}
 set innerHTML(v){this._html=String(v);this.children=[];if(this._html.startsWith('<span'))this.children.push(new Element('span'));}
 get innerHTML(){return this._html;}
 get firstChild(){return this.children[0];}
 appendChild(e){this.children.push(e);return e;}
 setAttribute(k,v){this.attributes[k]=String(v);}
 querySelector(q){return this.querySelectorAll(q)[0]??null;}
 querySelectorAll(q){const cls=q.slice(1);return this.children.flatMap(c=>(c.className.split(' ').includes(cls)?[c]:[]).concat(c.querySelectorAll(q)));}
}
function snapshot(e){return {tag:e.tagName,cls:e.className,style:e.style,html:e.innerHTML,attrs:e.attributes,dataset:e.dataset,children:e.children.map(snapshot)};}
let total=0,animated=0;
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const claimList=JSON.parse(readFileSync(resolve(dir,'../CLAIMS.json'))).claims;
const dataContext=vm.createContext({window:{}});vm.runInContext(readFileSync(resolve(dir,'data.js'),'utf8'),dataContext);
const data=dataContext.window.SCENE_DATA;
assert.equal(data.locked,false);assert(claimList.every(c=>c.status==='proposed'));
assert.equal(data.claims_sha256,hash(resolve(dir,'../CLAIMS.json')));
for(const [file,sha] of Object.entries(data.source_sha256))assert.equal(sha,hash(resolve(dir,'..',file)));
for(const [key,ids] of Object.entries(data.claim_ids)){
 assert(ids.length);assert(data.inputs[key]);
 for(const id of ids)assert(claimList.some(c=>c.id===id&&c.status===data.claims[id].status));
}
const story=readFileSync(resolve(dir,'../STORY.md'),'utf8');
for(const [page,info] of Object.entries(cues.scenes)){
 const document={title:page,body:new Element('body'),createElement:t=>new Element(t),createElementNS:(ns,t)=>new Element(t)};
 const context=vm.createContext({document,window:{},location:{search:'?format='+info.format},URLSearchParams,console});
 for(const script of ['../../../render/system.js','data.js','episode.js']){vm.runInContext(readFileSync(resolve(dir,script),'utf8'),context,{filename:script});if(script==='../../../render/system.js')context.FT=context.window.FT;if(script==='episode.js')context.FA=context.window.FA;}
 vm.runInContext(readFileSync(resolve(dir,page),'utf8').match(/<script>\s*([\s\S]*?)<\/script>/)[1],context,{filename:page});
 const clock=context.window.__ft;assert(clock?.ready);assert.equal(clock.width,info.format==='vertical'?1080:1920);assert.equal(clock.duration,info.duration);
 assert.throws(()=>context.FT.value('missing-test-key'),/Scene value missing/);
 assert.throws(()=>context.FA.num('not-a-claimed-number'),/Unclaimed numeric value/);
 for(const s of info.states){
  assert(story.includes(s.cue),'Cue not in narration '+s.cue);assert(s.still>s.at+2.6&&s.still<s.at+7);
  clock.seek(s.still);const first=JSON.stringify(snapshot(document.body));assert.equal(context.window.__faState,s.id);
  clock.seek(info.duration);clock.seek(0);clock.seek(s.still);assert.equal(first,JSON.stringify(snapshot(document.body)),page+' '+s.id+' is not seek-pure');
  const active=document.body.querySelectorAll('.fa-state').find(e=>e.dataset.state===s.id);assert(active.querySelector('.source'),'Persistent scope required');
  assert(first.includes('PROPOSED'),'Pre-lock status absent');
  if(['duration','allowance','departure','time'].includes(s.component)||s.phase==='denver')assert(JSON.stringify(snapshot(active)).includes('EXPLORATORY · POST-HOC · NOT REGISTERED'));
  clock.seek(s.at+.1);const early=JSON.stringify(snapshot(active));clock.seek(s.still);if(early!==JSON.stringify(snapshot(active)))animated++;
  total++;
 }
 console.log(page+': '+info.states.length+' states PASS');
}
assert.equal(total,64);assert.equal(animated,total,'Every cue state must animate');
const regenerated=JSON.parse(execFileSync('python3',['-B','-c',`import importlib.util,json; s=importlib.util.spec_from_file_location('bindings',${JSON.stringify(resolve(dir,'build_data.py'))});m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print(json.dumps(m.payload()))`]).toString());
assert.deepEqual(JSON.parse(JSON.stringify(data)),JSON.parse(JSON.stringify(regenerated)));
const browser=existsSync(resolve(dir,'browser_qa.json'))?JSON.parse(readFileSync(resolve(dir,'browser_qa.json'))):null;
let visible=0;
if(browser){
 assert.equal(browser.status,'PASS');assert.equal(browser.issue_count,0);assert.equal(browser.checks.length,total);
 for(const [file,sha] of Object.entries(browser.source_sha256))assert.equal(sha,hash(resolve(dir,file)),'Stale browser audit: '+file);
 assert.equal(browser.errors.length,0);
 for(const check of browser.checks)for(const label of check.labels){
  const value=data.values[label.key]*Number(label.scale),v=label.abs==='true'?Math.abs(value):value;
  const expected=Number(v.toFixed(Number(label.digits)));
  assert.equal(Number(label.text.replace(/−/g,'-').replace(/,/g,'')),expected,'Displayed number differs from source '+label.key);assert(label.claims.split(' ').every(id=>data.claim_ids[label.key].includes(id)));assert.equal(label.source,data.inputs[label.key].file);visible++;
 }
}
console.log('PASS: '+total+' animated states; hashes, reproducible computed bindings, exact narration cues and seek purity; '+visible+' browser numeric labels checked.');
if(process.argv.includes('--browser'))execFileSync('python3',['-B',resolve(dir,'render_stills.py'),'--audit-only'],{stdio:'inherit'});
