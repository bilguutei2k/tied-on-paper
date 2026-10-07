"""Deterministic direct-summation fixture; no generated flight outcomes."""
import ast
import json
import numpy as np
from scipy.stats import t as student_t
import run_gate as g

def check(st):
    old=g.HERE.with_name('amendment')
    def funcs(path):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
    a,b=funcs(old/'run_gate.py'),funcs(g.HERE/'run_gate.py')
    unchanged=['rng','scenarios','load_structure','prepare','shock_series','generate','indices','verdict','one','exact','summarize','fixtures']
    assert all(a[k]==b[k] for k in unchanged)
    for name in ['structure.json','truths.json','fixtures.json']:
        assert (old/name).read_bytes()==(g.HERE/name).read_bytes()
    daily=st['den'][:,None]*(np.array([.013,.012,.014])[None,:]+.005*np.sin(np.arange(len(st['den']))[:,None]/11))
    point,lo,hi=g.interval(st,daily,99,0,0,28)
    B=g.DESIGN['draws'];r=g.rng(99,0,0,3);pieces=[[],[]]
    num=np.zeros((2,B,3));den=np.zeros((2,B));orig=np.zeros((2,3));od=np.zeros(2);dfs=[0,0]
    for y,o,T in st['groups']:
        k=int(y==2025);q,tail=divmod(T,28);nn=daily[o:o+T];dd=st['den'][o:o+T]
        # Explicit circular sums, independent of cumulative-sum implementation.
        fn=np.array([nn[(j+np.arange(28))%T].sum(axis=0) for j in range(T)])
        fd=np.array([dd[(j+np.arange(28))%T].sum() for j in range(T)])
        tn=np.array([nn[(j+np.arange(tail))%T].sum(axis=0) for j in range(T)])
        td=np.array([dd[(j+np.arange(tail))%T].sum() for j in range(T)])
        starts=np.array([r.integers(0,T,size=q+1) for _ in range(B)])
        for i,ss in enumerate(starts):
            ix=np.array([(int(s)+j)%T for s in ss for j in range(28)])[:T]
            counts=np.bincount(ix,minlength=T)
            num[k,i]=num[k,i]+counts@nn;den[k,i]+=counts@dd
        orig[k]+=nn.sum(axis=0);od[k]+=dd.sum();dfs[k]+=q-1
        pieces[k].append((T,q,tail,fn,fd,tn,td,starts))
    assert np.max(abs(point-orig/od[:,None]))<1e-14
    def variance(x,axis,ddof):
        c=x-x.mean(axis=axis,keepdims=True)
        return (c*c).sum(axis=axis)/(x.shape[axis]-ddof)
    for k in (0,1):
        star=num[k]/den[k,:,None];v=np.zeros(3);vs=np.zeros((B,3))
        for T,q,tail,fn,fd,tn,td,starts in pieces[k]:
            v+=q*variance(fn-fd[:,None]*point[k],0,0)*T/(T-28)
            v+=variance(tn-td[:,None]*point[k],0,0)*T/(T-tail)
            for i,ss in enumerate(starts):
                vs[i]+=q*variance(fn[ss[:q]]-fd[ss[:q],None]*star[i],0,1)
                vs[i]+=variance(tn[ss[:q]]-td[ss[:q],None]*star[i],0,1)
        se=np.sqrt(v)/od[k];sestar=np.sqrt(vs)/den[k,:,None]
        piv=np.sort((star-point[k])/sestar,axis=0)
        # Independent linear quantiles at fixed p, including interpolation convention.
        def quant(p):
            rank=(B-1)*p;i=int(rank);return piv[i]+(rank-i)*(piv[i+1]-piv[i])
        floor=student_t.ppf(.995,dfs[k])
        assert abs(lo[k]-(point[k]-np.maximum(quant(.995),floor)*se).min())<1e-12
        assert abs(hi[k]-(point[k]-np.minimum(quant(.005),-floor)*se).max())<1e-12
    return dict(passes=True,unchanged_functions=unchanged,draws=B,df=dfs,new_synthetic_datasets=0,
                checks=['direct circular sums','integer multiplicities','analytical original and draw SEs','quantile inversion','finite-window correction','t floors','inherited manifests identical'])

if __name__=='__main__':
    st,manifest=g.load_structure();result=check(st)
    assert manifest['cells_sha256']==json.loads((g.HERE/'structure.json').read_text())['cells_sha256']
    assert g.fixtures(st)['passes']
    g.dump(g.HERE/'preflight.json',result);print(json.dumps(result))
