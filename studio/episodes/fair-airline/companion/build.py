"""Build a portable, evidence-bound companion; no network or Git writes.

Run from any directory: python3 studio/episodes/fair-airline/companion/build.py
The raw re-derivation report does not record a results.json hash. These reviewed
pins bind the results, proposed ledger, verifier and post-hoc results as read at
companion construction. Never refresh pins to bypass refusal: re-verify first.
All empirical page values must have a passing claim/check binding.
"""
import base64
import hashlib
import html
import json
import math
import re
import subprocess
from pathlib import Path

EP = Path(__file__).resolve().parent.parent
ROOT = EP.parents[2]
PINS = {
    'analysis/results.json': '5ad0c9319304bb645c966aca253d00035913105b900f58b6fd8be694e66597de',
    'CLAIMS.json': '64ae35817d333a3c90d6d8f60e43910ca72d3ca5dece581a5355561a6f24d74b',
    'analysis/claims_check.json': '00dc333e379f286f42ae4cea324d7037ef490e0cd1bbdedb2ea5ff8b615cca20',
    'analysis/review_checks/results.json': '0a430fc236035ca94043a76cbb9e49e076f5947ed0bfd763b8cc2ab71736a959',
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def esc(s):
    return html.escape(str(s), quote=True)

def flatten(v, p=''):
    d = {p: v}
    if isinstance(v, dict):
        for k, x in v.items():
            d.update(flatten(x, f'{p}.{k}' if p else k))
    elif isinstance(v, list):
        for k, x in enumerate(v):
            d.update(flatten(x, f'{p}[{k}]'))
    return d

def fonts():
    css = []
    source = ROOT / 'studio/render/fonts'
    for family, weights in [('IBMPlexMono', [400, 500, 600])]:
        for weight in weights:
            raw = (source / f'{family}-normal-{weight}-latin.woff2').read_bytes()
            css.append(f"@font-face{{font-family:'IBM Plex Mono';font-weight:{weight};src:url(data:font/woff2;base64,{base64.b64encode(raw).decode()}) format('woff2');font-display:swap}}")
    sibling = EP.parent / 'scramble-luck/companion/fonts'
    for file, family, weight in [('BigShouldersDisplay-800.ttf', 'Big Shoulders Display', 800), ('BigShouldersDisplay-900.ttf', 'Big Shoulders Display', 900), ('SourceSerif4-500.ttf', 'Source Serif 4', 500)]:
        css.append(f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/ttf;base64,{base64.b64encode((sibling/file).read_bytes()).decode()}) format('truetype');font-display:swap}}")
    for family in ['BigShouldersDisplay', 'IBMPlexMono', 'SourceSerif4']:
        css.append('/* ' + (source/f'OFL-{family}.txt').read_text().replace('*/', '* /') + ' */')
    return '\n'.join(css)

def main():
    files = {}
    for name, pin in PINS.items():
        raw = (EP/name).read_bytes()
        if sha(raw) != pin:
            raise SystemExit(f'REFUSED: {name} differs from the verified companion binding; re-verify and review before changing pins.')
        files[name] = json.loads(raw)
    report = files['analysis/claims_check.json']
    ledger = files['CLAIMS.json']
    if not report['all_pass'] or report['ledger_sha256'] != PINS['CLAIMS.json'] or report['discrepancies']:
        raise SystemExit('REFUSED: claims verification is not current and passing.')
    claims = {c['id']: c for c in ledger['claims']}
    flat = {f: flatten(d) for f, d in files.items()}
    checks = {(c['claim'], c['result_file'], c['key']): c for c in report['checks']}
    proof = {}
    for c in ledger['claims']:
        for v in c['values']:
            check = checks.get((c['id'], c['result_file'], v['key']))
            if check and check['passed']:
                proof.setdefault((c['result_file'], v['key']), []).append(check)
    provenance = {}
    def value(key, file='analysis/results.json'):
        actual = flat[file][key]
        candidates = proof.get((file, key), [])
        valid = []
        for c in candidates:
            other, digits = c['recomputed'], c['digits']
            same = round(actual, digits) == round(other, digits) if digits is not None else actual == other
            if same:
                valid.append(c['claim'])
        if not valid or isinstance(actual, (float, int)) and not math.isfinite(actual):
            raise SystemExit(f'REFUSED: unverified page binding {file}::{key}')
        provenance[file+'::'+key] = sorted(set(valid))
        return actual
    def design(key):
        return value('derived_metrics.design.'+key, 'analysis/claims_check.json')
    def measurement(path, period, file='analysis/results.json', factor=1, interval_key='interval', point_key='estimate'):
        row = {'label': period, 'estimate': value(path+'.'+point_key, file)*factor, 'path': file+'::'+path}
        if path+'.'+interval_key in flat[file]:
            row['interval'] = [value(path+'.'+interval_key+f'[{i}]', file)*factor for i in range(2)]
        else:
            row['interval'] = None
        return row
    periods = [('A', 'primary_2023_2024'), ('B', 'replication_2025')]
    r = files['analysis/results.json']
    period_labels = {p: p+' · '+'–'.join(str(y) for y in r[k]['years']) for p,k in periods}
    lenses = []
    def lens(id, option, change, group, rows, metric='Timely-arrival advantage', note=''):
        lenses.append({'id': id, 'option': option, 'change': change, 'group': group, 'rows': rows, 'metric': metric, 'note': note})
    primary = [measurement(k+'.adjusted_gap_ua_minus_wn_pp',period_labels[p]) for p,k in periods]
    lens('registered', 'Registered A and B', 'Uses the registered shared route/date/departure cells, scheduled-count weights and each operator’s own arrival timetable. Viewing another lens cannot change either sealed verdict.', 'Registered results', primary)
    airport = {'10397':'Atlanta', '11292':'Denver', '12889':'Las Vegas', '12892':'Los Angeles', '13930':'Chicago O’Hare'}
    changes = {
        'window_1h': ('One-hour windows', 'Rebuilds shared cells using one-hour scheduled-departure windows.'),
        'window_4h': ('Four-hour windows', 'Rebuilds shared cells using four-hour scheduled-departure windows.'),
        'equal_cell_weights': ('Equal cell weights', 'Gives each supported cell equal influence, instead of scheduled-count influence.'),
        'harmonic_weights': ('Harmonic weights', 'Uses the harmonic mean of the two scheduled cell counts, emphasizing balanced support.'),
        'equal_year_A': ('Equal-year average · A', 'Averages the separate source-year estimates equally instead of pooling schedule counts.'),
        'reciprocal_nearest_30min': ('Reciprocal nearest departures', 'Pairs reciprocal nearest scheduled departures on the same route and date within thirty minutes. Each pair has equal weight.'),
    }
    all_keys = sorted(set().union(*(r[k]['sensitivities'] for _,k in periods)))
    for key in all_keys:
        if key.startswith('omit_airport_'):
            name=airport[key.rsplit('_',1)[1]]; label, change = 'Omit '+name, 'Removes every shared cell touching '+name+'. Recomputes the retained comparison; does not extrapolate to that airport.'
        elif key.startswith('year_'):
            year=key.split('_')[1]; label, change = year+' separately', 'Restricts the comparison to source year '+year+'. Other source years are absent from this lens.'
        else:
            label, change = changes[key]
        rows = [measurement(k+'.sensitivities.'+key+'.gap_ua_minus_wn_pp', period_labels[p]) for p,k in periods if key in r[k]['sensitivities']]
        lens(key,label,change+' Descriptive registered sensitivity; cannot change the verdict.', 'Registered sensitivities',rows)
    qfile='analysis/review_checks/results.json'
    for key, label, change in [
        ('common_mid','Shared midpoint allowance','Scores both operators against the midpoint of their cell-mean scheduled blocks, plus the same late tolerance, measured from each flight’s own scheduled departure. It is a shared elapsed-time budget, not a common wall-clock arrival deadline.'),
        ('common_UA','Shared United allowance','Uses United’s cell-mean scheduled block as the elapsed-time allowance for both operators, from each scheduled departure, plus the same late tolerance.'),
        ('common_WN','Shared Southwest allowance','Uses Southwest’s cell-mean scheduled block as the elapsed-time allowance for both operators, from each scheduled departure, plus the same late tolerance.'),
        ('equalized_mid','Equalized departure + midpoint','Also removes the operators’ cell-mean scheduled-departure-minute difference before applying the shared midpoint allowance. This changes another timetable choice.'),
        ('dep_timely','Timely departures','Changes the outcome to noncancelled departures strictly less than the late tolerance behind scheduled departure. Cancellations fail, diversions remain eligible; every scheduled flight remains in the denominator.'),
        ('dep_late','Late departures · UA minus WN','Changes the outcome to noncancelled departures at least the late tolerance late. Every scheduled flight remains in the denominator; cancelled flights are not observed late departures. A negative gap means fewer United late departures, not fewer Southwest late departures.'),
    ]:
        rows=[]
        for p,_ in periods:
            row=measurement(p+'.'+key,period_labels[p],qfile,100,point_key='UA_minus_WN')
            ip=p+'.interval_checks.'+key+'.interval'
            if ip in flat[qfile]:
                row['interval']=[value(ip+f'[{i}]',qfile)*100 for i in range(2)]
                row['interval_path']=qfile+'::'+ip
            rows.append(row)
        lens(key,label,change+' Exploratory, post-hoc; cannot change the verdict.', 'Exploratory, post-hoc',rows, 'Late-departure rate gap' if key=='dep_late' else 'Timely-departure advantage' if key=='dep_timely' else 'Timely-arrival advantage')
    derived=files['analysis/claims_check.json']['derived_metrics']
    for key in ['before_10','from_16']+sorted(derived['A']['bands'], key=int):
        band=key.isdigit(); label=(f'{int(key)*2:02d}:00–{(int(key)+1)*2:02d}:00' if band else 'Before 10:00' if key=='before_10' else 'From 16:00')
        rows=[]
        for p,_ in periods:
            path=f'derived_metrics.{p}.'+('bands.' if band else 'time.')+key
            row=measurement(path,period_labels[p],'analysis/claims_check.json',point_key='gap_pp')
            row['weight_pct']=value(path+'.weight_pct','analysis/claims_check.json'); rows.append(row)
        lens('time_'+key,'Local departure · '+label, 'Restricts the frozen own-timetable comparison to '+label+' local scheduled departures. Observed bands only; no interval was computed. This average is not a morning-flight recommendation. Exploratory, post-hoc; cannot change the verdict.', 'Exploratory, post-hoc',rows)
    # Chart observations use the same verified band keys as the selector.
    def day_chart():
        X=lambda band:90+(band-2)/9*730
        Y=lambda gap:80+(16-gap)/18*300
        out=['<svg id="day-chart" viewBox="0 0 900 470" role="img" aria-labelledby="day-chart-title day-chart-desc"><title id="day-chart-title">The gap grows through the day</title><desc id="day-chart-desc">United minus Southwest own-timetable timely-completion gap, in percentage points. Two-hour local scheduled departure bands. A is 2023–2024, B is 2025. Sparse bands under one percent of comparison weight are faded. No band intervals computed.</desc>']
        for z in [0,2,8,16]:
            out.append(f'<line x1="90" x2="820" y1="{Y(z)}" y2="{Y(z)}" stroke="var(--ink)" stroke-width="{2 if z==0 else 1}"'+(' stroke-dasharray="8 6"' if z==2 else '')+'/>'+f'<text x="58" y="{Y(z)+10}" text-anchor="end">{z:+g}</text>')
        for period,color in [('A','var(--subject-text)'),('B','#3350D6')]:
            for band in range(2,12):
                path=f'derived_metrics.{period}.bands.{band}'
                gap=value(path+'.gap_pp','analysis/claims_check.json');weight=value(path+'.weight_pct','analysis/claims_check.json');opacity=.38 if weight<1 else 1
                if band>2:
                    prev=value(f'derived_metrics.{period}.bands.{band-1}.gap_pp','analysis/claims_check.json')
                    out.append(f'<line x1="{X(band-1)}" y1="{Y(prev)}" x2="{X(band)}" y2="{Y(gap)}" stroke="{color}" stroke-width="4" opacity="{opacity}"/>')
                out.append(f'<circle data-period="{period}" data-band="{band}" data-gap="{gap}" data-weight="{weight}" cx="{X(band)}" cy="{Y(gap)}" r="7" stroke="{color}" stroke-width="3" fill="{color if period=="A" else "var(--bg)"}" opacity="{opacity}"><title>{period} · {band*2:02d}:00–{band*2+2:02d}:00: {gap:+.2f} points; {weight:.2f}% weight</title></circle>')
        for band in [2,4,6,8,10]:out.append(f'<text x="{X(band)}" y="420" text-anchor="middle">{band*2:02d}</text>')
        out.append('<text x="90" y="458">Two-hour bands · local scheduled departure</text></svg>')
        out.append('<div class="day-notes"><p><span class="day-a">● A · 2023–2024</span> &nbsp; <span class="day-b">○ B · 2025</span><br>United minus Southwest · percentage points</p>')
        for key,label in [('before_10','Before 10:00'),('from_16','From 16:00')]:
            vals=[value(f'derived_metrics.{period}.time.{key}.gap_pp','analysis/claims_check.json') for period in ['A','B']]
            out.append(f'<p><strong>{label}</strong><br>{vals[0]:+.1f} / {vals[1]:+.1f} points · A / B</p>')
        weights=[value(f'derived_metrics.{period}.bands.11.weight_pct','analysis/claims_check.json') for period in ['A','B']]
        out.append(f'</div><p class="meta">22:00–24:00 faded: under 1% of weight ({weights[0]:.2f}% / {weights[1]:.2f}% in A / B). No overlap before 04:00. Zero line solid; +2-point reference dashed. No band interval computed; the reference confers no verdict.</p>')
        out.append('<details><summary>Band values and comparison weights</summary><table><thead><tr><th>Local band</th><th>A gap / weight</th><th>B gap / weight</th></tr></thead><tbody>')
        for band in range(2,12):
            cells=[]
            for period in ['A','B']:
                path=f'derived_metrics.{period}.bands.{band}';g=value(path+'.gap_pp','analysis/claims_check.json');w=value(path+'.weight_pct','analysis/claims_check.json')
                cells.append(f'<td>{g:+.2f} pp / {w:.2f}%</td>')
            out.append(f'<tr><th>{band*2:02d}–{band*2+2:02d}</th>'+''.join(cells)+'</tr>')
        out.append('</tbody></table><p class="meta">FA-C076–095 · independently recomputed raw-cell sums. Exploratory, post-hoc, not registered. No causal explanation or morning-flight recommendation.</p></details>')
        return ''.join(out)
    day=day_chart()
    threshold,level=design('line_pp'),design('nominal_interval_pct')
    domain_values=[x for l in lenses for row in l['rows'] for x in [row['estimate']]+(row['interval'] or [])]+[0,threshold]
    domain=[math.floor(min(domain_values))-1,math.ceil(max(domain_values))+1]
    def marks(rows):
        x=lambda v:48+(v-domain[0])/(domain[1]-domain[0])*604
        out=f'<line class="reference" x1="{x(threshold)}" y1="35" x2="{x(threshold)}" y2="172"/><line class="neutral" x1="{x(0)}" y1="35" x2="{x(0)}" y2="172"/>'
        for i,row in enumerate(rows):
            y=65+i*65
            if row['interval']:
                lo,hi=map(x,row['interval']);out+=f'<line class="interval" x1="{lo}" y1="{y}" x2="{hi}" y2="{y}"/><path class="cap" d="M {lo} {y-8} v 16 M {hi} {y-8} v 16"/>'
            out+=f'<circle class="dot" cx="{x(row["estimate"])}" cy="{y}" r="7"/><text class="plot-label" x="48" y="{y-18}">{esc(row["label"])}</text>'
        for t in [domain[0],0,threshold,domain[1]]:
            out+=f'<text class="axis" x="{x(t)}" y="210" text-anchor="middle">{t:g}</text>'
        return out
    def readouts(rows):
        return ''.join(f'<div class="result-row"><span class="label">{esc(row["label"])}</span><strong class="number point">{row["estimate"]:+.2f}</strong><span class="unit">percentage points</span><span class="meta">'+(f'[{row["interval"][0]:+.2f}, {row["interval"][1]:+.2f}]' if row['interval'] else 'No interval computed')+'</span></div>' for row in rows)
    options=''
    for group in dict.fromkeys(l['group'] for l in lenses):
        options+=f'<optgroup label="{esc(group)}">'+''.join(f'<option value="{l["id"]}">{esc(l["option"])}</option>' for l in lenses if l['group']==group)+'</optgroup>'
    national=''
    for p,k in periods:
        cells=[]
        for op in ['UA','WN']:
            path=k+'.unmatched_all_flights_on_time_pct.'+op
            cells.append(f'{value(path+".estimate"):.2f}%<br><span class="meta">{value(path+".n"):,} scheduled</span>')
        national+=f'<tr><th scope="row">{period_labels[p]}</th>'+''.join('<td>'+s+'</td>' for s in cells)+'</tr>'
    dot='';sources=''
    for year,record in r['descriptive_context']['published_dot_annual'].items():
        row=[]
        for op in ['UA','WN']:
            path=f'descriptive_context.published_dot_annual.{year}.operating_carriers.{op}'
            row.append(f'#{value(path+".rank")} · {value(path+".rate_pct"):.2f}%')
        dot+=f'<tr><th scope="row">{esc(year)}</th>'+''.join('<td>'+s+'</td>' for s in row)+'</tr>'
        sources+=f'<li><a href="{esc(record["official_pdf_url"])}">DOT annual operating table · {esc(year)}</a> · {esc(record["operating_table"])}.</li>'
    def metric_pair(suffix, file='analysis/review_checks/results.json',factor=1):
        return ' / '.join(f'{value(p+"."+suffix,file)*factor:.2f}' for p,_ in periods)
    coverage=[]
    for op in ['UA','WN']:
        coverage.append(' / '.join(f'{value(k+".matched_cell_coverage_pct."+op+".estimate"):.2f}%' for _,k in periods))
    denver=' / '.join(f'{value("derived_metrics."+p+".denver.weight_share","analysis/claims_check.json")*100:.2f}%' for p,_ in periods)
    recheck=json.loads((EP/'recheck/compare.json').read_text())['summary']
    if recheck['mismatched'] or recheck['matched']!=recheck['comparisons']:raise SystemExit('REFUSED: blind recheck has unresolved discrepancies')
    commits={}
    for name,rev in {'METHOD':'3672298','GATE':'153fd1b','AMENDMENT':'e5c9a33','FAIL':'6bc20d7','DESIGN':'8a33153','PASS':'02c9fb6','APPROVAL':'41a6974','PRODUCTION':'af6b613','A':'c829f51','B':'12320b0','RECHECK':'39a0e19','REVIEW':'6ce74cb','FIXES':'725423a','REPAIR':'4f759d3'}.items():
        commits[name]=subprocess.run(['git','-C',str(ROOT),'rev-parse','--verify',rev+'^{commit}'],check=True,capture_output=True,text=True).stdout.strip()
    question=(EP/'analysis/amendment/AMENDMENT-1.md').read_text().splitlines()[0]
    data={'lenses':lenses,'threshold':threshold,'level':level,'domain':domain,'provenance':provenance,'pins':PINS}
    replacements={'DAY_CHART':day,'FONTS':fonts(),'QUESTION':esc(question),'SCOPE':esc(claims['FA-C001']['scope']), 'ANSWER':''.join('<p>'+esc(claims[id]['text'])+'</p>' for id in ['FA-C001','FA-C002','FA-C003']), 'OPTIONS':options,'INITIAL_CHANGE':esc(lenses[0]['change']),'INITIAL_MARKS':marks(primary),'INITIAL_READOUTS':readouts(primary),'LEVEL':str(level),'THRESHOLD':f'{threshold:g}','LATE':str(design('late_failure_minutes')),'WINDOW':str(design('departure_window_hours')),'BLOCK':str(design('block_days')),'DRAWS':f'{design("draws"):,}','NATIONAL':national,'DOT':dot,'DOT_SOURCES':sources,'COVER_UA':coverage[0],'COVER_WN':coverage[1],'DENVER':denver,'SCHEDULE':metric_pair('schedule.UA_minus_WN'),'ACTUAL':metric_pair('completed_cell_means.actual.UA_minus_WN'),'ACTUAL_COVER':metric_pair('completed_cell_means.weight_share',factor=100),'COMMON':metric_pair('common_mid.UA_minus_WN',factor=100),'DEPARTURE':metric_pair('dep_timely.UA_minus_WN',factor=100),'MATCHED':str(recheck['matched']),'COMPARED':str(recheck['comparisons']),'DATA':json.dumps(data,ensure_ascii=False).replace('<','\\u003c'),'RESULT_HASH':PINS['analysis/results.json'],'CLAIM_HASH':PINS['CLAIMS.json']}
    replacements.update({k+'_COMMIT':v for k,v in commits.items()})
    template=(EP/'companion/template.html').read_text()
    for k,v in replacements.items():template=template.replace('__'+k+'__',v)
    def download(m):
        path=(EP/'companion'/m[1]).resolve()
        if not path.is_relative_to(EP):raise SystemExit('REFUSED: evidence path outside episode')
        mime='application/json' if path.suffix=='.json' else 'text/plain'
        return f'href="data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}" download="{path.name}"'
    template=re.sub(r'href="(\.\./[^\"]+)"',download,template)
    if re.search(r'__[A-Z_]+__',template):raise SystemExit('REFUSED: unresolved template token')
    head,body=template.split('<!--BODY-->')
    page='<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'+head+'</head>\n<body>\n'+body+'</body>\n</html>\n'
    target=EP/'renders/companion';target.mkdir(parents=True,exist_ok=True)
    (EP/'companion/index.html').write_text(page)
    (target/'page.html').write_text(head+body)
    print(f'Built {len(lenses)} lenses; {len(provenance)} verified bindings; results {PINS["analysis/results.json"][:12]}.')

if __name__=='__main__':main()
