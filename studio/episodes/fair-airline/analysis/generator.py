#!/usr/bin/env python3
"""Registered probit/status generator. Emission requires committed exact bytes.

No import, describe, or calibration operation draws outcomes. The only random
outcome entry point is generate(), guarded before any RNG is constructed.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import numpy as np
import scipy
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.special import ndtri
from common import EP, OUT, DERIVED, sha, dump, progress, seal_file, utc
from blind_guard import install, verify_denial
from simulation_model import Model, read_sealed
from scenarios import process_at

install()

def committed_bytes(path,revision='HEAD'):
    root=EP.parents[2]
    r=subprocess.run(['git','show',f'{revision}:{path.relative_to(root)}'],
      cwd=root,capture_output=True,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
    return r.returncode==0 and r.stdout==path.read_bytes()

def require_commit():
    manifest=json.loads((OUT/'scenario-manifest.json').read_text())
    assert verify_denial()
    required=['scenario-manifest.json','simulation-structure.json','scenario-base-truth.json',
              'environment.json']+list(manifest['code_hashes'])
    missing=[]
    for name in required:
        p=OUT/name
        if not committed_bytes(p):missing.append(name)
    if not committed_bytes(OUT/'coverage.json','af8e89f'):
        missing.append('support bytes differ from af8e89f')
    for name,value in manifest['code_hashes'].items():
        if sha(OUT/name)!=value:missing.append(f'{name}: seal hash mismatch')
    for name,key in [('simulation-structure.json','simulation_structure_sha256'),
                     ('scenario-base-truth.json','base_truth_sha256'),
                     ('coverage.json','coverage_sha256')]:
        if sha(OUT/name)!=manifest[key]:missing.append(f'{name}: seal hash mismatch')
    if sha(OUT/'environment.json')!=manifest['dependencies']['environment_sha256']:
        missing.append('environment.json: seal hash mismatch')
    if (np.__version__!=manifest['dependencies']['numpy'] or
        scipy.__version__!=manifest['dependencies']['scipy']):
        missing.append('NumPy/SciPy runtime differs from sealed versions')
    if missing:
        raise PermissionError('METHOD requires a scenario/generator commit before synthetic outcomes: '+', '.join(missing))
    return manifest

def rng(bank,process_id,replicate_id,stream):
    if bank not in (0,1) or min(process_id,replicate_id)<0:
        raise ValueError('Invalid bank/process/replicate')
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(
      [20261006,bank,process_id,replicate_id,stream])))

def ar_series(random,entities,weeks,sd,ar):
    # Entity-major, then physical-week order, stationary initial distribution.
    z=random.standard_normal((len(entities),len(weeks)))
    z[:,0]*=sd
    innovation_sd=sd*np.sqrt(1-ar*ar)
    for w in range(1,len(weeks)):
        z[:,w]=ar*z[:,w-1]+innovation_sd*z[:,w]
    return z

def generate(process,bank,replicate_id,model=None,calibrated=None):
    require_commit()  # Before shocks, innovations, statuses or masks exist.
    model=model or Model()
    p,calibration=calibrated if calibrated is not None else model.calibrate(process)
    # Recompute complete truths before any random outcome, including latent R/H.
    truth=model.truths(p,process['missingness'])
    record=next(r for r in model.record['files'] if r['path'].endswith('simulation-flights.parquet'))
    flights=read_sealed(record)
    def array(name,dtype=None):
        return flights[name].to_numpy(zero_copy_only=False).astype(dtype) if dtype else flights[name].to_numpy(zero_copy_only=False)
    probability=p[array('probability_id',np.int64)]
    if process['template']['kind']=='base':
        # Uncalibrated nominal processes retain each record's route/time base.
        # The probability-cell means are sufficient only for linear truths.
        ci=np.array([model.codes.index(c) for c in flights['carrier'].to_pylist()])
        probability=np.clip(process['stress']['baseline']+
          process['stress']['season']*array('season')+array('hetero')+
          process['template']['increment']*(ci-3.5),.05,.99)
    week=array('week').astype('datetime64[D]')
    physical=np.arange(week.min(),week.max()+np.timedelta64(7,'D'),np.timedelta64(7,'D'))
    wi=np.searchsorted(physical,week)
    origin=np.array([-1 if x is None else x for x in flights['origin_id'].to_pylist()],dtype=np.int32)
    destination=np.array([-1 if x is None else x for x in flights['dest_id'].to_pylist()],dtype=np.int32)
    carrier=array('dot_id',np.int32)
    s=process['stress'];sd=s['sd'];ar=s['ar'];mode=s['mode']
    shock=rng(bank,process['process_id'],replicate_id,0)
    total=np.zeros(len(probability));variance=np.zeros(len(probability))
    if mode in ('national','combined'):
        national=ar_series(shock,[0],physical,sd,ar)[0]
        total+=national[wi];variance+=sd*sd
    if mode in ('airport','combined'):
        entities=np.unique(np.concatenate((origin,destination)))
        airport=ar_series(shock,entities,physical,sd,ar)
        total+=airport[np.searchsorted(entities,origin),wi]
        total+=airport[np.searchsorted(entities,destination),wi]
        variance+=np.where(origin==destination,4.,2.)*sd*sd
    if mode in ('carrier','combined'):
        entities=np.unique(carrier) # Numeric DOT ID order, not code order.
        c=ar_series(shock,entities,physical,sd,ar)
        total+=c[np.searchsorted(entities,carrier),wi];variance+=sd*sd
    innovation=rng(bank,process['process_id'],replicate_id,1)
    timely=np.sqrt(1+variance)*ndtri(probability)+total+innovation.standard_normal(len(total))>0
    uniforms=rng(bank,process['process_id'],replicate_id,2).random((len(total),3))
    cancelled=((~timely)&(uniforms[:,0]<.25)).astype(np.int8)
    diverted=((~timely)&(uniforms[:,0]>=.25)&(uniforms[:,0]<.30)).astype(np.int8)
    completed=(cancelled==0)&(diverted==0)
    delay=np.where(timely,0.,20.)
    delay[~completed]=np.nan
    mechanism=process['missingness'];r=mechanism['r'];kind=mechanism['kind']
    if kind=='informative':
        mask=timely&(uniforms[:,1]<r/probability);delay[mask]=np.nan
    elif kind=='mcar':
        mask=completed&(uniforms[:,1]<r);delay[mask]=np.nan
    elif kind=='status':
        mask=completed&(uniforms[:,1]<r)
        cancelled[mask&(uniforms[:,2]<.5)]=-1
        diverted[mask&(uniforms[:,2]>=.5)]=-1
    result=pa.table({'source_year':flights['source_year'],
      'source_month':flights['source_month'],'source_row':flights['source_row'],
      'Cancelled':pa.array(cancelled,mask=cancelled==-1),
      'Diverted':pa.array(diverted,mask=diverted==-1),
      'ArrDelay':pa.array(delay,mask=np.isnan(delay)),
      'latent_timely':pa.array(timely)})
    return result,dict(truth=truth,calibration=calibration,process=process,
                       bank=bank,replicate_id=replicate_id)

def fixture(outcomes,model,name):
    """Deterministic registered quality fixtures on nominal synthetic records."""
    require_commit()
    record=next(r for r in model.record['files'] if r['path'].endswith('simulation-flights.parquet'))
    flights=read_sealed(record)
    cancelled=outcomes['Cancelled'].to_pylist();diverted=outcomes['Diverted'].to_pylist()
    delay=outcomes['ArrDelay'].to_pylist()
    valid=flights['valid_key'].to_numpy().copy()
    carrier=np.asarray(flights['carrier'].to_pylist())
    year=flights['source_year'].to_numpy()
    completed=np.array([c==0 and d==0 for c,d in zip(cancelled,diverted)])
    if name=='invalid_flag':cancelled[0]=2
    elif name=='invalid_delay':delay[np.flatnonzero(completed)[0]]=float('inf')
    else:
        for code in model.codes:
            for y in (2023,2024,2025):
                mask=(carrier==code)&(year==y);n=int(mask.sum())
                count=n//1000+int(name.endswith('above_cutoff'))
                if name.startswith('unknown_'):
                    selected=np.flatnonzero(mask&completed)[:count]
                    if len(selected)!=count:raise ValueError('Insufficient completed fixture records')
                    for i in selected:cancelled[i]=0;diverted[i]=0;delay[i]=None
                elif name.startswith('keys_'):
                    existing=int((mask&~valid).sum())
                    if existing>count:raise ValueError('Frozen missing-key share already exceeds fixture target')
                    selected=np.flatnonzero(mask&valid)[:count-existing]
                    valid[selected]=False
                else:raise ValueError('Unknown fixture')
    return pa.table({'source_year':outcomes['source_year'],'source_month':outcomes['source_month'],
      'source_row':outcomes['source_row'],'Cancelled':pa.array(cancelled,type=pa.int8()),
      'Diverted':pa.array(diverted,type=pa.int8()),'ArrDelay':pa.array(delay,type=pa.float64()),
      'latent_timely':outcomes['latent_timely'],'fixture_valid_key':pa.array(valid)})

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--process',type=int,default=0)
    parser.add_argument('--calibrate',action='store_true')
    parser.add_argument('--emit',action='store_true')
    parser.add_argument('--bank',type=int,choices=(0,1),default=0)
    parser.add_argument('--replicate',type=int,default=0)
    parser.add_argument('--fixture',choices=('unknown_at_cutoff','unknown_above_cutoff',
      'keys_at_cutoff','keys_above_cutoff','invalid_flag','invalid_delay'))
    args=parser.parse_args()
    if args.emit:require_commit() # Reject before loading model as well.
    model=Model();process=process_at(model.pairs,args.process)
    if args.fixture and (not args.emit or process['missingness']['kind']!='none'):
        raise ValueError('Deterministic quality fixtures require emission with no missingness')
    if not args.emit and not args.calibrate:
        print(json.dumps(process,sort_keys=True));return
    p,calibration=model.calibrate(process)
    truth=model.truths(p,process['missingness'])
    directory=DERIVED/'calibration';directory.mkdir(exist_ok=True)
    stem=f"template-{process['template_id']:06}-stress-{process['stress_id']:03}-mechanism-{process['mechanism_id']}"
    with (directory/f'{stem}.npy').open('wb') as f:np.save(f,p,allow_pickle=False)
    dump(directory/f'{stem}.json',dict(process=process,calibration=calibration,
                                     truth=truth,probabilities=seal_file(directory/f'{stem}.npy')))
    progress(f'Deterministic calibration evaluated for process {args.process}; residual {calibration.get("residual",0):.3g}. Full 336-component and latent truth recorded in ignored derivative. No random outcome generated by calibration.')
    if args.emit:
        outcomes,record=generate(process,args.bank,args.replicate,model,(p,calibration))
        if args.fixture:
            outcomes=fixture(outcomes,model,args.fixture);record['fixture']=args.fixture
        destination=DERIVED/'synthetic'/f'bank-{args.bank}'/f'process-{args.process}'
        destination.mkdir(parents=True,exist_ok=True)
        path=destination/f'replicate-{args.replicate:04}.parquet'
        with path.open('wb') as f:pq.write_table(outcomes,f,compression='zstd')
        dump(path.with_suffix('.json'),dict(**record,file=seal_file(path),written_utc=utc()))
        progress(f'Synthetic dataset generated after committed seal: bank {args.bank}, process {args.process}, replicate {args.replicate}. Confirmation outcomes remain closed.')
    print(dict(process=args.process,calibration_residual=calibration.get('residual',0),
               synthetic_datasets_generated=int(args.emit)))

if __name__=='__main__':main()
