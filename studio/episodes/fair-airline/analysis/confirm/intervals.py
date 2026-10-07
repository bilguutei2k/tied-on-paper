"""Registered Amendment-2 arithmetic, using sealed starts rather than new RNG.

The circular-sum function is copied verbatim from the tested gate. The ratio
arithmetic is the gate's interval generalized to one opened period and exposed
assignment intervals. Equal-year averaging is descriptive only.
"""
import numpy as np
from scipy.stats import t as student_t

DRAWS = 1999
LENGTH = 28

def circular_sums(values, length):
    """One sum for every circular start, with no random numbers."""
    ext=np.concatenate([values,values[:length-1]],axis=0)
    cs=np.concatenate([np.zeros_like(ext[:1]),np.cumsum(ext,axis=0)],axis=0)
    return cs[length:]-cs[:-length]

def interval(groups, daily, den, starts, equal_year=False):
    pieces=[]; original=np.zeros(daily.shape[1]); od=0.; df=0
    nums=np.zeros((DRAWS,daily.shape[1])); dens=np.zeros(DRAWS)
    for year,offset,days in groups:
        sl=slice(offset,offset+days); q,tail=divmod(days,LENGTH)
        assert q>=2 and tail>0
        ss=starts[year]; assert ss.shape==(DRAWS,q+1)
        fn=circular_sums(daily[sl],LENGTH); fd=circular_sums(den[sl],LENGTH)
        tn=circular_sums(daily[sl],tail); td=circular_sums(den[sl],tail)
        sn=fn[ss[:,:q]]; sd=fd[ss[:,:q]]
        nn=sn.sum(axis=1)+tn[ss[:,q]]; dd=sd.sum(axis=1)+td[ss[:,q]]
        on=daily[sl].sum(axis=0); oo=den[sl].sum()
        nums+=nn; dens+=dd; original+=on; od+=oo; df+=q-1
        pieces.append((days,q,tail,fn,fd,tn,td,ss,sn,sd,nn,dd,on,oo))
    if od<=0 or not np.isfinite(od):
        return dict(valid=False,point=None,envelope=None,reason='nonpositive original denominator')
    point=original/od
    if equal_year:
        if any(p[-1]<=0 for p in pieces):
            return dict(valid=False,point=None,envelope=None,reason='empty source year')
        point=np.mean([p[-2]/p[-1] for p in pieces],axis=0)
    if np.any(dens<=0) or not np.isfinite(dens).all():
        return dict(valid=False,point=point.tolist(),envelope=None,reason='invalid draw denominator')
    star=nums/dens[:,None]
    if equal_year:
        if any(np.any(p[-3]<=0) for p in pieces):
            return dict(valid=False,point=point.tolist(),envelope=None,reason='empty sampled year')
        star=np.mean([p[-4]/p[-3][:,None] for p in pieces],axis=0)
    var=np.zeros(daily.shape[1]); vstar=np.zeros_like(star)
    for T,q,tail,fn,fd,tn,td,ss,sn,sd,nn,dd,on,oo in pieces:
        center=on/oo if equal_year else point
        scenter=nn/dd[:,None] if equal_year else star
        full=fn-fd[:,None]*center; short=tn-td[:,None]*center
        vv=q*full.var(axis=0,ddof=0)*T/(T-LENGTH)
        vv+=short.var(axis=0,ddof=0)*T/(T-tail)
        res=sn-sd[:,:,None]*scenter[:,None,:]
        shortstar=tn[ss[:,:q]]-td[ss[:,:q],None]*scenter[:,None,:]
        vs=q*res.var(axis=1,ddof=1)+shortstar.var(axis=1,ddof=1)
        if equal_year:
            var+=vv/(len(pieces)*oo)**2
            vstar+=vs/(len(pieces)*dd[:,None])**2
        else:
            var+=vv; vstar+=vs
    se=np.sqrt(var) if equal_year else np.sqrt(var)/od
    sestar=np.sqrt(vstar) if equal_year else np.sqrt(vstar)/dens[:,None]
    if not (np.isfinite(star).all() and np.isfinite(se).all() and
            np.isfinite(sestar).all() and np.all(se>0) and np.all(sestar>0)):
        return dict(valid=False,point=point.tolist(),envelope=None,reason='invalid original/draw SE')
    pivot=(star-point)/sestar
    quant=np.quantile(pivot,[.005,.995],axis=0,method='linear')
    floor=float(student_t.ppf(.995,df))
    lo=point-np.maximum(quant[1],floor)*se
    hi=point-np.minimum(quant[0],-floor)*se
    return dict(valid=True,point=point.tolist(),assignment_intervals=np.stack([lo,hi],axis=1).tolist(),
        envelope=[float(lo.min()),float(hi.max())],se=se.tolist(),pivot_quantiles=quant.tolist(),
        df=int(df),t_floor=floor,draws=DRAWS,valid_draws=DRAWS,
        minimum_draw_denominator=float(dens.min()),minimum_draw_se=float(sestar.min()),
        bootstrap_sha256=__import__('hashlib').sha256(star.astype('<f8').tobytes()).hexdigest(),
        _draws=star)

def verdict(result, quality=True):
    if not quality or not result['valid']: return 'inconclusive'
    lo,hi=result['envelope']
    return ('UA advantage above two points' if lo>.02 else
            'no material UA advantage under this rule' if hi<.02 else 'inconclusive')
