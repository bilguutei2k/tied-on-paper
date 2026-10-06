"""Deterministic enumeration of the complete registered suite; no random draws.

The manifest stores this Cartesian product as a lossless recipe rather than
millions of repeated records. Process IDs are positions in this iterator.
"""
from itertools import combinations, product

LINE = ((.02, .04), (.04, .02), (.02, .02))
ABOVE = (.04, .04)
ZERO = (0., 0.)

def shapes():
    # Every combination of binding component between periods, including equal.
    for a, b in product(LINE, repeat=2):
        yield 'line_both', a, b
    for line in LINE:
        yield 'line_A', line, ABOVE
        yield 'line_B', ABOVE, line
        yield 'H_A', line, ZERO
        yield 'H_B', ZERO, line
    yield 'only_A', ABOVE, ZERO
    yield 'only_B', ZERO, ABOVE

def templates(pairs):
    yield dict(kind='base', name='no_carrier_effect', increment=0.)
    yield dict(kind='base', name='additive_carrier', increment=.005)
    for increment in (0., .005, .001):
        yield dict(kind='stable', name=f'stable_{increment}', increment=increment)
    for pair in pairs:
        for direction in (1, -1):
            active = [dict(pair=list(pair), direction=direction)]
            for delta in (.025, .03, .04, .06):
                yield dict(kind='reversal', active=active, A=[delta,delta],
                           B=[delta,delta], design_power=delta==.04)
            for a,b in product(((.04,.06),(.06,.04)), repeat=2):
                yield dict(kind='reversal', active=active, A=list(a), B=list(b),
                           design_power=False)
            yield dict(kind='near_H',active=active,A=[.01,.01],B=[.01,.01],cap_other_H=.01)
            for name,a,b in shapes():
                for perturbation in (-.001,0.,.001):
                    change=lambda v: [x+perturbation if x==.02 else x for x in v]
                    aa,bb=change(a),change(b)
                    yield dict(kind='boundary',name=name,active=active,
                               A=aa,B=bb,perturbation=perturbation,
                               cap_other_R=.02 if min(min(aa),min(bb))<=.02 else None,
                               cap_other_H=.02 if name.startswith('H_') else None)
    for p,q in combinations(pairs,2):
        if set(p)&set(q):
            continue
        for directions in product((1,-1),repeat=2):
            active=[dict(pair=list(e),direction=d) for e,d in zip((p,q),directions)]
            for name,a,b in shapes():
                for perturbation in (-.001,0.,.001):
                    change=lambda v: [x+perturbation if x==.02 else x for x in v]
                    aa,bb=change(a),change(b)
                    yield dict(kind='two_edge_boundary',name=name,active=active,
                               A=aa,B=bb,perturbation=perturbation,
                               cap_other_R=.02 if min(min(aa),min(bb))<=.02 else None,
                               cap_other_H=.02 if name.startswith('H_') else None)

def stresses():
    for baseline,season in product((.7,.8,.9),(0.,.05)):
        yield dict(baseline=baseline,season=season,mode='none',sd=0.,ar=0.)
        for mode,sd,ar in product(('national','airport','carrier','combined'),
                                  (.15,.30),(0.,.3,.6)):
            yield dict(baseline=baseline,season=season,mode=mode,sd=sd,ar=ar)

def mechanisms():
    yield dict(kind='none',r=0.)
    for kind,r in product(('informative','mcar','status'),(.0005,.001,.01)):
        yield dict(kind=kind,r=r)

def processes(pairs):
    process_id=0
    for template_id,t in enumerate(templates(pairs)):
        for stress_id,s in enumerate(stresses()):
            for mechanism_id,m in enumerate(mechanisms()):
                yield dict(process_id=process_id,template_id=template_id,
                           stress_id=stress_id,mechanism_id=mechanism_id,
                           template=t,stress=s,missingness=m)
                process_id+=1

def process_at(pairs,process_id):
    if process_id<0:
        raise ValueError('Negative process ID')
    template_id,rem=divmod(process_id,1500)
    stress_id,mechanism_id=divmod(rem,10)
    for i,t in enumerate(templates(pairs)):
        if i==template_id:
            return dict(process_id=process_id,template_id=i,stress_id=stress_id,
                        mechanism_id=mechanism_id,template=t,
                        stress=list(stresses())[stress_id],
                        missingness=list(mechanisms())[mechanism_id])
    raise IndexError('Process ID outside sealed suite')
