"""Saved bank-0 diagnostic evidence only; never generates data."""
import json
from pathlib import Path
import numpy as np
from scipy.stats import skew
HERE=Path(__file__).resolve().parent
rows=[]
for length,sid in [(28,0),(28,3),(28,6),(28,9),(7,9),(1,9)]:
    records=[json.loads(x) for x in (HERE.with_name('amendment')/f'bank0-candidate{length}-scenario{sid}.jsonl').read_text().splitlines()]
    point=np.array([x['point'] for x in records])[:,:,0]
    half=(np.array([x['high'] for x in records])-np.array([x['low'] for x in records]))/2
    rows.append(dict(block_days=length,scenario=sid,n=len(records),
       empirical_sd_over_mean_bootstrap_sd=(point.std(axis=0,ddof=1)/(half/2.5758293035489004).mean(axis=0)).tolist(),
       skew=skew(point,axis=0,bias=False).tolist(),
       point_halfwidth_correlation=[float(np.corrcoef(point[:,i],half[:,i])[0,1]) for i in (0,1)],
       above_below_counts=[[sum(x['verdict'][i]==v for x in records) for v in (1,-1)] for i in (0,1)]))
(HERE/'diagnosis.json').write_text(json.dumps(dict(acceptance_evidence=False,source_bank=0,results=rows),indent=2)+'\n')
print('Saved diagnostic summary; no synthetic generation.')
