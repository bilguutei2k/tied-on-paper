#!/usr/bin/env python3
"""Independently audit completed synthetic checkpoints; never read raw inputs."""
import os
for name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
import json
import math
import numpy as np
from scipy.optimize import brentq
from scipy.stats import binom
from common import OUT, EP, dump, progress, sha, utc
from blind_guard import install, verify_denial

install()


def bounds(k, n):
    low = 0. if k == 0 else brentq(lambda p: binom.sf(k-1, n, p)-.05,
                                  0., 1., xtol=1e-14)
    high = 1. if k == n else brentq(lambda p: binom.cdf(k, n, p)-.05,
                                   0., 1., xtol=1e-14)
    return low, high


def main():
    assert verify_denial()
    report = json.loads((OUT/'gate.json').read_text())
    assert report['overall'] == 'FAIL' and not report['confirmation_outcomes_opened']
    assert len(report['attempts']) == 1
    attempt = report['attempts'][0]
    record = attempt['checkpoint']
    path = EP/record['path']
    assert sha(path) == record['sha256'] and path.stat().st_size == record['bytes']
    with path.open() as f:
        rows = [json.loads(line) for line in f]
    n = len(rows)
    assert n == 1000 and [r['replicate_id'] for r in rows] == list(range(n))
    assert attempt['process']['process_id'] == 3240 and attempt['bank'] == 0
    truth = attempt['truth']['components']
    assert len(truth) == 336 and max(map(abs, truth)) <= 1e-6
    errors = [[r['point'][j]-truth[j] for r in rows] for j in range(336)]
    means = [math.fsum(e)/n for e in errors]
    mcse = [math.sqrt(math.fsum((x-m)**2 for x in e)/(n-1)/n)
            for e, m in zip(errors, means)]
    acceptance = [abs(m)+1.96*s for m, s in zip(means, mcse)]
    bias = attempt['bias']
    assert np.allclose(means, bias['mean_error'], rtol=0, atol=1e-12)
    assert np.allclose(mcse, bias['mcse'], rtol=0, atol=1e-12)
    assert np.allclose(acceptance, bias['acceptance_bound'], rtol=0, atol=1e-12)
    failing = [j for j, b in enumerate(acceptance) if b > .002]
    assert failing == bias['failing_components'] and failing
    exact_checks = 0
    for candidate, summary in attempt['resamplers'].items():
        fits = [r['intervals'][candidate] for r in rows]
        counts = dict(coverage=sum(r['coverage'] for r in fits),
                      latent_envelope_coverage=sum(r['latent_coverage'] for r in fits),
                      table_changes=sum(r['verdict'] == 'Table changes' for r in fits),
                      table_survives=sum(r['verdict'] == 'Table survives' for r in fits),
                      designated_pair_power=sum(r['designated_power'] for r in fits))
        for key, count in counts.items():
            saved = summary['latent_envelope_coverage'] if key == 'latent_envelope_coverage' else summary[key]
            low, high = bounds(count, n)
            assert saved['count'] == count and saved['total'] == n
            assert abs(saved['lower_95_one_sided']-low) < 1e-11
            assert abs(saved['upper_95_one_sided']-high) < 1e-11
            assert abs(saved['mcse']-math.sqrt((count/n)*(1-count/n)/n)) < 1e-12
            exact_checks += 1
        assert summary['valid_datasets'] == sum(r['valid'] for r in fits)
        assert summary['minimum_valid_draws'] == min(r['valid_draws'] for r in fits)
        assert all(r['valid_draws'] == 5000 for r in fits)
        assert not summary['tests']['power'] and not summary['tests']['coverage']
        assert counts['table_survives'] == 0 and counts['table_changes'] == 0
    assert report['synthetic_datasets_generated'] == 1000
    assert report['bootstrap_draws_generated'] == 15000000
    for name in ('validity', 'power'):
        assert report['gates'][name]['status'] == 'FAIL'
    for name in ('calibration', 'boundary_false_verdict'):
        assert report['gates'][name]['status'] == 'NOT_COMPLETED'
    assert report['gates']['independent_validation']['status'] == 'NOT_RUN'
    assert not report['scenario_suite_complete'] and not report['calibration_audit_complete']
    # Byte-identical replay of the original replicate, not a fresh dataset/bank.
    from gate_runner import check_commit, dataset
    from simulation_model import Model
    from gate_runtime import Runtime
    check_commit()
    first = json.loads((OUT/'calibration-first.json').read_text())
    probability_record = first['probability_file']
    probability_path = EP/probability_record['path']
    assert sha(probability_path) == probability_record['sha256']
    with probability_path.open('rb') as f:
        probability = np.load(f, allow_pickle=False)
    runtime = Runtime(Model())
    replay = dataset(runtime, first['process'], runtime.prepare(first['process'], probability),
                     first['truth'], 0, 0, [1, 4, 8])
    assert replay == rows[0], 'Original replicate replay differs'
    result = dict(written_utc=utc(),passes=True,confirmation_outcomes_opened=False,
                  gate_sha256=sha(OUT/'gate.json'),checkpoint_sha256=sha(path),
                  verifier_sha256=sha(OUT/'verify_gate.py'),datasets=n,components=336,
                  independent_exact_binomial_checks=exact_checks,
                  maximum_bias_bound=max(acceptance),failing_components=len(failing),
                  original_replicate_replayed=0,byte_identical_replay=True,
                  new_unique_bank_datasets_generated=0,
                  audit='math.fsum bias/variance; binomial-tail inversion bounds; exact original stream replay')
    dump(OUT/'gate-verification.json', result)
    progress('Failed gate independently verified: all 1000 replicate IDs and 336 components; math.fsum bias/MCSE and 15 exact binomial-tail checks agree. Original bank0/process3240/replicate0 replay is byte-identical across all three resamplers, with no fresh dataset or bank. Confirmation outcomes remain closed.')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
