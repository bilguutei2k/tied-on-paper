"""Exact registered week multiplicities; called only after the scenario commit.

No arrays are generated on import. Production arrays additionally require the
selected resampler to have passed selection and independent validation.
"""
import math
import numpy as np
from common import OUT

def weights(random,weeks_by_year,resampler,draws=5000):
    from generator import require_commit
    require_commit()
    if draws!=5000 or resampler not in (1,4,8):
        raise ValueError('The registered draw count/resampler cannot be changed')
    years=sorted(weeks_by_year)
    result={y:np.empty((draws,len(weeks_by_year[y])),dtype=np.uint16) for y in years}
    for draw in range(draws):
        for year in years:
            w=len(weeks_by_year[year])
            if resampler==1:
                sampled=random.integers(0,w,size=w,endpoint=False)
            else:
                starts=random.integers(0,w,size=math.ceil(w/resampler),endpoint=False)
                sampled=((starts[:,None]+np.arange(resampler))%w).ravel()[:w]
            result[year][draw]=np.bincount(sampled,minlength=w)
    return result

def production(weeks_by_year,resampler):
    import json
    gate=json.loads((OUT/'gate.json').read_text())
    if gate['overall']!='PASS' or gate['selected_resampler']!=resampler:
        raise PermissionError('Production arrays require passing both registered banks')
    random=np.random.Generator(np.random.PCG64(20261005))
    return weights(random,weeks_by_year,resampler)
