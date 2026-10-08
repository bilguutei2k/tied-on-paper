"""Reproducible Chromium QA using the locally installed agent-browser CLI.

Start the daemon with the launch command in QA.md, then run this script.
"""
import json
import os
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent.parent
OUT = EP/'renders/companion'
ENV = dict(os.environ, NPM_CONFIG_CACHE='/private/tmp/scramble-companion-npm',
           AGENT_BROWSER_SOCKET_DIR='/private/tmp/fair-airline-companion-browser')
CLI = ['npx', '--yes', 'agent-browser', '--namespace', 'fair-airline-companion']

def run(*args, code=None):
    p = subprocess.run(CLI+list(args), env=ENV, input=code, text=True, capture_output=True, check=True)
    if '--json' in args:
        result = json.loads(p.stdout)
        if not result['success']:
            raise RuntimeError(result)
        return result['data'].get('result', result['data'])
    return p.stdout.strip()

SWEEP = r'''(async()=>{
await document.fonts.ready;
const d=JSON.parse(document.getElementById('episode-data').textContent),select=document.getElementById('lens'),checks=[];
const f=n=>(n>=0?'+':'')+n.toFixed(2),scale=n=>48+(n-d.domain[0])/(d.domain[1]-d.domain[0])*604;
const dayDots=[...document.querySelectorAll('#day-chart circle')];
const dayChart=dayDots.length===20&&dayDots.every(e=>{const l=d.lenses.find(l=>l.id==='time_'+e.dataset.band),r=l.rows[e.dataset.period==='A'?0:1];return Number(e.dataset.gap)===r.estimate&&Number(e.dataset.weight)===r.weight_pct&&Math.abs(Number(e.getAttribute('cx'))-(90+(Number(e.dataset.band)-2)/9*730))<1e-9&&Math.abs(Number(e.getAttribute('cy'))-(80+(16-r.estimate)/18*300))<1e-9&&Number(e.getAttribute('opacity'))===(r.weight_pct<1?.38:1)})&&!!document.getElementById('day-chart-desc');
for(const l of d.lenses){
 select.value=l.id;select.dispatchEvent(new Event('change',{bubbles:true}));document.querySelector('details').open=true;
 const rows=[...document.querySelectorAll('#readouts .result-row')],dots=[...document.querySelectorAll('#marks .dot')],intervals=[...document.querySelectorAll('#marks .interval')];
 const numbers=l.rows.every((r,i)=>rows[i].querySelector('.point').textContent===f(r.estimate)&&rows[i].textContent.includes(r.interval?'['+r.interval.map(f).join(', ')+']':'No interval computed'));
 const geometries=l.rows.every((r,i)=>Math.abs(Number(dots[i].getAttribute('cx'))-scale(r.estimate))<1e-9);
 const bounds=l.rows.filter(r=>r.interval).every((r,i)=>Math.abs(Number(intervals[i].getAttribute('x1'))-scale(r.interval[0]))<1e-9&&Math.abs(Number(intervals[i].getAttribute('x2'))-scale(r.interval[1]))<1e-9);
 const line=Number(document.querySelector('#marks .reference').getAttribute('x1'));
 const overflow=[...document.querySelectorAll('.shell *')].filter(e=>{const s=getComputedStyle(e),b=e.getBoundingClientRect();return s.display!=='none'&&b.width>0&&(b.left < -1||b.right>innerWidth+1)}).map(e=>e.tagName+'#'+e.id);
 const style=getComputedStyle(select),ctx=document.createElement('canvas').getContext('2d');ctx.font=style.fontWeight+' '+style.fontSize+' '+style.fontFamily;
 const optionWidth=ctx.measureText(select.selectedOptions[0].textContent).width,availableWidth=select.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight),optionFits=optionWidth<=availableWidth;
 const post=l.group==='Exploratory, post-hoc',group=document.getElementById('group').textContent;
 const noFakeIntervals=intervals.length===l.rows.filter(r=>r.interval).length;
 const authority=document.getElementById('change').textContent.includes('cannot change');
 const ok=numbers&&geometries&&bounds&&noFakeIntervals&&Math.abs(line-scale(d.threshold))<1e-9&&overflow.length===0&&document.documentElement.scrollWidth===innerWidth&&optionFits&&authority&&document.querySelector('.verdict').textContent==='Replicated'&&document.getElementById('explorer').classList.contains('exploratory')===post&&(!post||group.includes('not registered'));
 checks.push({id:l.id,passed:ok,numbers,geometries,bounds,noFakeIntervals,optionFits,optionWidth,availableWidth,overflow});document.querySelector('details').open=false;
}
select.value='registered';select.dispatchEvent(new Event('change',{bubbles:true}));
return {width:innerWidth,theme:document.documentElement.dataset.theme,height:document.documentElement.scrollHeight,gutter:document.querySelector('.shell').getBoundingClientRect().left,checks,networkResources:performance.getEntriesByType('resource').filter(x=>/^https?:/.test(x.name)).length,fontChecks:{headline:document.fonts.check('900 76px "Big Shoulders Display"'),mono:document.fonts.check('600 32px "IBM Plex Mono"'),serif:document.fonts.check('500 18px "Source Serif 4"')},dayChart,passed:dayChart&&checks.every(c=>c.passed)};
})()'''

def main():
    run('open', (EP/'companion/index.html').as_uri())
    reports=[]
    for width,height in [(390,844),(1440,1000)]:
        run('set','viewport',str(width),str(height))
        for theme in ['paper','night']:
            run('eval','--stdin','--json',code=f"document.documentElement.dataset.theme!=='{theme}' && document.getElementById('theme').click()")
            reports.append(run('eval','--stdin','--json',code=SWEEP))
            run('eval','window.scrollTo(0,0)')
            run('screenshot',str(OUT/f'{width}-{theme}.png'),'--full')
            run('screenshot',str(OUT/f'{width}-{theme}-top.png'))
            run('scrollintoview','#test-title')
            run('screenshot',str(OUT/f'{width}-{theme}-control.png'))
        run('select','#lens','common_mid')
        run('scrollintoview','#metric')
        run('screenshot',str(OUT/f'{width}-night-posthoc.png'))
        run('select','#lens','time_before_10')
        run('scrollintoview','#metric')
        run('screenshot',str(OUT/f'{width}-night-time.png'))
        run('scrollintoview','#day-title')
        run('screenshot',str(OUT/f'{width}-night-day-chart.png'))
        run('scrollintoview','#method-title')
        run('screenshot',str(OUT/f'{width}-night-method.png'))
    fragment=Path('/private/tmp/fair-airline-fragment.html')
    fragment.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+(OUT/'page.html').read_text()+'</body></html>')
    run('open',fragment.as_uri());run('set','viewport','390','844')
    fragment_report=run('eval','--stdin','--json',code=SWEEP)
    logs={'errors':run('errors'),'console':run('console')}
    total=sum(len(r['checks']) for r in reports)
    passed=all(r['passed'] and not r['networkResources'] and all(r['fontChecks'].values()) for r in reports+[fragment_report]) and not logs['errors'] and not logs['console']
    (OUT/'browser-audit.json').write_text(json.dumps({'engine':'headless Chromium','reports':reports,'fragment':fragment_report,**logs,'passed':passed},indent=2)+'\n')
    print(f'Chromium: {total} page states + {len(fragment_report["checks"])} fragment states; {"PASS" if passed else "FAIL"}.')
    for r in reports+[fragment_report]:
        for c in r['checks']:
            if not c['passed']:print(r['width'],r['theme'],c)
    if not passed:raise SystemExit(1)

if __name__=='__main__':main()
