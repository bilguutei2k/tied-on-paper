"""Registered per-scenario Monte Carlo acceptance; no file or RNG access."""
import numpy as np
from scipy.stats import beta


def exact(k, n):
    return dict(count=int(k), total=int(n), estimate=float(k/n),
                mcse=float(np.sqrt((k/n)*(1-k/n)/n)),
                lower_95_one_sided=0. if k == 0 else float(beta.ppf(.05, k, n-k+1)),
                upper_95_one_sided=1. if k == n else float(beta.ppf(.95, k+1, n-k)))


def power_required(process):
    t = process['template']; m = process['missingness']
    condition = m['kind'] == 'none' or (m['kind'] == 'informative' and m['r'] == .0005)
    return condition and (t.get('design_power', False) or
                          (t['kind'] == 'stable' and t['increment'] in (0., .005)))


def summarize(process, records, truth):
    n = len(records)
    assert n in (1000, 2000)
    errors = np.array([r['point'] for r in records])-np.array(truth['components'])
    mean = errors.mean(axis=0)
    mcse = errors.std(axis=0, ddof=1)/np.sqrt(n)
    bias_bound = np.abs(mean)+1.96*mcse
    bias = dict(mean_error=mean.tolist(), mcse=mcse.tolist(),
                acceptance_bound=bias_bound.tolist(), threshold=.002,
                passes=bool(np.all(bias_bound <= .002)),
                failing_components=np.flatnonzero(bias_bound > .002).tolist(),
                worst_component=int(bias_bound.argmax()),
                maximum_bound=float(bias_bound.max()))
    blocking_only = process['missingness']['r'] == .01
    result = dict(process=process, datasets=n, draws_per_dataset=5000,
                  truth=truth, bias=bias, quality_blocking_only=blocking_only,
                  resamplers={})
    # Numerically calibrated decision lines also conservatively count truths
    # within the registered residual tolerance as applicable error cases.
    false_changes_applies = any(truth[x]['R'] <= .02+1e-6 for x in ('primary', 'latent'))
    false_survives_applies = any(truth[x]['H'] >= .02-1e-6 for x in ('primary', 'latent'))
    for resampler in records[0]['intervals']:
        rows = [r['intervals'][resampler] for r in records]
        valid = sum(r['valid'] for r in rows)
        coverage = exact(sum(r.get('coverage', False) for r in rows), n)
        latent_coverage = exact(sum(r.get('latent_coverage', False) for r in rows), n)
        changes = exact(sum(r['verdict'] == 'Table changes' for r in rows), n)
        survives = exact(sum(r['verdict'] == 'Table survives' for r in rows), n)
        designated = exact(sum(r.get('designated_power', False) for r in rows), n)
        power = designated if process['template'].get('design_power', False) else survives
        tests = dict(valid_dataset_fraction=valid/n >= .95,
                     coverage=coverage['lower_95_one_sided'] >= .92,
                     latent_envelope_coverage=latent_coverage['lower_95_one_sided'] >= .92,
                     false_changes=(not false_changes_applies or changes['upper_95_one_sided'] <= .025),
                     false_survives=(not false_survives_applies or survives['upper_95_one_sided'] <= .025),
                     power=(not power_required(process) or power['lower_95_one_sided'] >= .80))
        if blocking_only:
            tests = dict(correct_blocking=all(r['verdict'] == 'Inconclusive' for r in rows))
        result['resamplers'][str(resampler)] = dict(valid_datasets=valid,
            valid_dataset_fraction=valid/n, minimum_valid_draws=min(r['valid_draws'] for r in rows),
            coverage=coverage, latent_envelope_coverage=latent_coverage,
            table_changes=changes, table_survives=survives, designated_pair_power=designated,
            false_changes_applicable=false_changes_applies,
            false_survives_applicable=false_survives_applies,
            power_required=power_required(process), tests=tests,
            passes=all(tests.values()) and (blocking_only or bias['passes']))
    return result
