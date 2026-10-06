"""Streaming exact registered generator and fixed-schedule week scorer.

Only hash-verified schedule columns enter this process. Chunking consumes each
PCG64 stream in exactly the sealed generator's source-record order. All flights,
cells, endpoints and joint bootstrap draws are retained.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
              'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_name] = '1'
import numpy as np
import math
from scipy import sparse
from scipy.special import ndtri
from generator import rng, ar_series, require_commit
from simulation_model import read_sealed
from common import CARRIERS


def components(rates, unknown, sides):
    a, b = np.asarray(sides).T
    gap = rates[..., a] - rates[..., b]
    return np.stack((gap, gap - unknown[..., b], gap + unknown[..., a]),
                    axis=-1).reshape(*gap.shape[:-1], -1)


def multiplicities(random, weeks_by_year, resampler):
    """Same integer API and draw/year loops as committed bootstrap.weights."""
    result = {y: np.empty((5000, len(weeks_by_year[y])), dtype=np.uint16)
              for y in sorted(weeks_by_year)}
    for draw in range(5000):
        for year in sorted(weeks_by_year):
            w = len(weeks_by_year[year])
            if resampler == 1:
                sampled = random.integers(0, w, size=w, endpoint=False)
            else:
                starts = random.integers(0, w, size=math.ceil(w/resampler), endpoint=False)
                sampled = ((starts[:, None]+np.arange(resampler)) % w).ravel()[:w]
            result[year][draw] = np.bincount(sampled, minlength=w)
    return result


def verdict(point, sd, critical):
    lower = (point-critical*sd).reshape(-1, 3).min(axis=1).reshape(-1, 2, 2)
    upper = (point+critical*sd).reshape(-1, 3).max(axis=1).reshape(-1, 2, 2)
    lq = np.stack((np.minimum(lower[:, :, 0], -upper[:, :, 1]),
                   np.minimum(-upper[:, :, 0], lower[:, :, 1])), axis=1)
    uq = np.stack((np.minimum(upper[:, :, 0], -lower[:, :, 1]),
                   np.minimum(-lower[:, :, 0], upper[:, :, 1])), axis=1)
    lower_R = float(lq.min(axis=2).max())
    upper_H = float(uq.max())
    label = ('Table changes' if lower_R > .02 else
             'Table survives' if upper_H < .02 else 'Inconclusive')
    return label, lq, uq, lower, upper, lower_R, upper_H


class Runtime:
    def __init__(self, model):
        require_commit()
        self.model = model
        record = next(r for r in model.record['files']
                      if r['path'].endswith('simulation-flights.parquet'))
        flights = read_sealed(record)
        self.pid = flights['probability_id'].to_numpy().astype(np.int32)
        self.year = flights['source_year'].to_numpy().astype(np.int16)
        self.dot = flights['dot_id'].to_numpy().astype(np.int32)
        self.valid_key = flights['valid_key'].to_numpy()
        self.week = flights['week'].to_numpy().astype('datetime64[D]')
        self.hetero = flights['hetero'].to_numpy()
        self.season = flights['season'].to_numpy()
        self.origin = np.array([-1 if x is None else x for x in
                                flights['origin_id'].to_pylist()], dtype=np.int32)
        self.destination = np.array([-1 if x is None else x for x in
                                     flights['dest_id'].to_pylist()], dtype=np.int32)
        code_from_dot = {v: k for k, v in CARRIERS.items()}
        dots = np.array(sorted(code_from_dot), dtype=np.int32)
        ci = np.array([model.codes.index(code_from_dot[int(d)]) for d in dots])
        self.carrier = ci[np.searchsorted(dots, self.dot)].astype(np.int8)
        self.cy = ((self.year-2023)*8+self.carrier).astype(np.int8)
        self.cy_n = np.bincount(self.cy, minlength=24)
        self.invalid_n = np.bincount(self.cy[~self.valid_key], minlength=24)
        self.weeks_by_year = {int(y): np.unique(self.week[self.year == y])
                              for y in np.unique(self.year)}
        self.weeks = [(y, w) for y, ws in self.weeks_by_year.items() for w in ws]
        self.physical = np.arange(self.week.min(), self.week.max()+np.timedelta64(7, 'D'),
                                  np.timedelta64(7, 'D'))
        self.physical_index = np.searchsorted(self.physical, self.week).astype(np.int16)
        self.airports = np.unique(np.concatenate((self.origin, self.destination)))
        self.oi = np.searchsorted(self.airports, self.origin).astype(np.int16)
        self.di = np.searchsorted(self.airports, self.destination).astype(np.int16)
        self.dots = dots
        self.ci = np.searchsorted(dots, self.dot).astype(np.int8)
        # Every probability cell has one source-year/week, including national-only
        # carrier/date cells. Validate this independently from its model_date.
        cell_week = np.full(len(model.n), -1, dtype=np.int16)
        offset = 0
        for y, ws in self.weeks_by_year.items():
            selected = self.year == y
            ix = offset + np.searchsorted(ws, self.week[selected])
            cell_week[self.pid[selected]] = ix
            assert np.all(cell_week[self.pid[selected]] == ix)
            offset += len(ws)
        assert np.all(cell_week >= 0)
        self.cell_week = cell_week
        self.nweeks = offset
        # Sparse expansion assigns each frozen score coefficient to its week.
        coo = model.t.tocoo()
        self.aggregate = sparse.csr_matrix((coo.data/model.n[coo.col],
                           (cell_week[coo.col]*model.t.shape[0]+coo.row, coo.col)),
                           shape=(offset*model.t.shape[0], len(model.n)))
        self.denominator = np.asarray(self.aggregate @ model.n).reshape(offset, -1)
        self.full_denominator = self.denominator.sum(axis=0)
        assert np.max(np.abs(self.full_denominator-1)) < 1e-10
        self.sides = model.sides

    def prepare(self, process, probability):
        p = probability[self.pid]
        if process['template']['kind'] == 'base':
            p = np.clip(process['stress']['baseline'] +
                        process['stress']['season']*self.season+self.hetero+
                        process['template']['increment']*(self.carrier-3.5), .05, .99)
        stress = process['stress']
        variance = np.zeros(len(p))
        if stress['mode'] in ('national', 'combined'):
            variance += stress['sd']**2
        if stress['mode'] in ('airport', 'combined'):
            variance += np.where(self.origin == self.destination, 4., 2.)*stress['sd']**2
        if stress['mode'] in ('carrier', 'combined'):
            variance += stress['sd']**2
        return p, np.sqrt(1+variance)*ndtri(p)

    def generate(self, process, bank, replicate, prepared):
        # The runner checks all committed executable bytes once, before creating
        # workers. No raw native file reader or network API is reachable here.
        p, mu = prepared
        s = process['stress']; mode = s['mode']
        shock = rng(bank, process['process_id'], replicate, 0)
        national = airport = carrier = None
        if mode in ('national', 'combined'):
            national = ar_series(shock, [0], self.physical, s['sd'], s['ar'])[0]
        if mode in ('airport', 'combined'):
            airport = ar_series(shock, self.airports, self.physical, s['sd'], s['ar'])
        if mode in ('carrier', 'combined'):
            carrier = ar_series(shock, self.dots, self.physical, s['sd'], s['ar'])
        innovation = rng(bank, process['process_id'], replicate, 1)
        status = rng(bank, process['process_id'], replicate, 2)
        ycounts = np.zeros(len(self.model.n), dtype=np.int32)
        ucounts = np.zeros_like(ycounts)
        unknown = np.zeros(24, dtype=np.int64)
        # Chunks only change allocation size. Gaussian innovations and triples of
        # status uniforms are consumed in the sealed source-row order.
        for start in range(0, len(p), 524288):
            end = min(start+524288, len(p)); sl = slice(start, end)
            total = np.zeros(end-start)
            wi = self.physical_index[sl]
            if national is not None: total += national[wi]
            if airport is not None:
                total += airport[self.oi[sl], wi]
                total += airport[self.di[sl], wi]
            if carrier is not None: total += carrier[self.ci[sl], wi]
            timely = mu[sl]+total+innovation.standard_normal(end-start) > 0
            uniforms = status.random((end-start, 3))
            cancelled = (~timely) & (uniforms[:, 0] < .25)
            diverted = (~timely) & (uniforms[:, 0] >= .25) & (uniforms[:, 0] < .30)
            completed = ~(cancelled | diverted)
            # Synthetic delays are 0 for timely and 20 for known late. Timing
            # masks and one-flag masks give exactly the registered status result.
            kind = process['missingness']['kind']; r = process['missingness']['r']
            if kind == 'informative':
                u = timely & (uniforms[:, 1] < r/p[sl])
            elif kind in ('mcar', 'status'):
                u = completed & (uniforms[:, 1] < r)
            else: u = np.zeros(end-start, dtype=bool)
            y = timely & ~u
            np.add.at(ycounts, self.pid[sl], y)
            np.add.at(ucounts, self.pid[sl], u)
            unknown += np.bincount(self.cy[sl][u], minlength=24)
        weekly_y = np.asarray(self.aggregate @ ycounts).reshape(self.nweeks, -1)
        weekly_u = np.asarray(self.aggregate @ ucounts).reshape(self.nweeks, -1)
        point = components(weekly_y.sum(axis=0)/self.full_denominator,
                           weekly_u.sum(axis=0)/self.full_denominator, self.sides)
        quality = bool(np.all(unknown*1000 <= self.cy_n) and
                       np.all(self.invalid_n*1000 <= self.cy_n))
        return weekly_y, weekly_u, point, quality, unknown

    def intervals(self, weekly_y, weekly_u, point, process, bank, replicate, resampler):
        random = rng(bank, process['process_id'], replicate, 3)
        by_year = multiplicities(random, self.weeks_by_year, resampler)
        multiplicity = np.concatenate([by_year[y] for y in sorted(by_year)], axis=1).astype(float)
        denom = multiplicity @ self.denominator
        with np.errstate(divide='ignore', invalid='ignore'):
            draws = components((multiplicity @ weekly_y)/denom,
                               (multiplicity @ weekly_u)/denom, self.sides)
        valid = np.isfinite(draws).all(axis=1) & (denom > 0).all(axis=1)
        nvalid = int(valid.sum())
        if nvalid < 4750:
            return dict(valid=False, valid_draws=nvalid, reason='joint draw fraction')
        complete = draws[valid]
        sd = complete.std(axis=0, ddof=1)
        if not np.all(np.isfinite(sd) & (sd > 0)):
            return dict(valid=False, valid_draws=nvalid, reason='nonpositive component SD')
        standardized = np.abs((complete-complete.mean(axis=0))/sd)
        critical = float(np.quantile(standardized.max(axis=1), .95, method='linear'))
        label, lq, uq, lower, upper, lr, uh = verdict(point, sd, critical)
        return dict(valid=True, valid_draws=nvalid, sd=sd, critical=critical,
                    verdict=label, lq=lq, uq=uq, lower=lower, upper=upper,
                    lower_R=lr, upper_H=uh)
