#!/usr/bin/env python3
"""Read-only evidence packaging after review_checks.py; writes only review artifacts."""
from pathlib import Path
import hashlib,json,subprocess,datetime
HERE=Path(__file__).resolve().parent;EP=HERE.parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(2**20):h.update(b)
 return h.hexdigest()
checks=[]
coverage=json.loads((EP/'analysis/coverage.json').read_text())
records=[coverage['structural_files']['structure'],coverage['frozen_sets']['pair_cells']]
for period in ['A','B']:
 r=json.loads((EP/f'analysis/confirm/results-{period}.json').read_text());records.append(r['inputs']['outcomes']);records.append(r['primary']['draw_file'])
for r in records:
 p=EP/r['path'];assert sha(p)==r['sha256'];checks.append({'path':r['path'],'sha256':r['sha256'],'passes':True})
for manifest in ['production-seal.json','final-artifacts.json']:
 d=json.loads((EP/f'analysis/confirm/{manifest}').read_text())
 for rel,h in d['files'].items():
  assert sha(EP/rel)==h;checks.append({'path':rel,'sha256':h,'passes':True})
raw=json.loads((HERE/'raw_audit.json').read_text());annual=[]
for y in [2023,2024,2025]:
 r=json.loads((EP/f'analysis/confirm/results-{"A" if y<2025 else "B"}.json').read_text())
 for c in ['UA','WN']:
  allm=[json.loads(x['national']) for x in raw['months'] if x['year']==y]
  n=sum(x["('Y', 'size')"][c] for x in allm)
  assert n==r['annual'][str(y)][c]['Y']['n']
  row={'year':y,'carrier':c,'n':n}
  for k in ['Y','U','C','V']:
   value=sum(x[str((k,'sum'))][c] for x in allm);assert value==r['annual'][str(y)][c][k]['numerator'];row[k]=int(value)
  annual.append(row)
( HERE/'evidence.json').write_text(json.dumps({'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'post_hoc_not_registered':True,'hash_checks':checks,'independent_raw_annual_counts':annual,'all_pass':True},indent=2)+'\n')
paths=['studio/episodes/fair-airline/analysis/confirm','studio/episodes/fair-airline/analysis/amendment2/OWNER_APPROVAL.md']
(HERE/'git-timeline.txt').write_text(subprocess.check_output(['git','log','--format=%H %aI %cI %s','--']+paths,text=True))
(HERE/'production-repair.diff').write_text(subprocess.check_output(['git','diff','af6b613','4f759d3','--','studio/episodes/fair-airline/analysis/confirm'],text=True))
print(json.dumps({'hash_checks':len(checks),'annual_count_checks':len(annual),'all_pass':True}))
