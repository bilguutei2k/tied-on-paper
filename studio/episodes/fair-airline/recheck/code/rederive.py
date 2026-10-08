#!/usr/bin/env python3
"""Independent raw-BTS re-derivation for fair-airline.

Reads only the raw ZIPs named in data/flights-manifest.json.  The intermediate
monthly aggregates contain no row-level data and are deleted after combination.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import math
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[5]
EP = ROOT / "studio/episodes/fair-airline"
MANIFEST = EP / "data/flights-manifest.json"
OUT = EP / "recheck"
WORK = OUT / "work"
UA, WN = "UA", "WN"
IDS = {UA: 19977, WN: 19393}
USECOLS = ["Year", "Month", "FlightDate", "Reporting_Airline",
           "DOT_ID_Reporting_Airline", "OriginAirportID", "DestAirportID",
           "CRSDepTime", "Cancelled", "Diverted", "ArrDelay"]


def parse_schedule(frame: pd.DataFrame) -> pd.DataFrame:
    """Return valid matching key fields; 2400 advances FlightDate one day."""
    d = pd.to_datetime(frame.FlightDate, errors="coerce")
    raw = pd.to_numeric(frame.CRSDepTime, errors="coerce")
    finite_integer = raw.notna() & np.isfinite(raw) & (raw == np.floor(raw))
    h = raw // 100
    m = raw % 100
    is_2400 = finite_integer & (raw == 2400)
    normal = finite_integer & (h.between(0, 23)) & (m.between(0, 59))
    valid = d.notna() & (normal | is_2400)
    mins = (h * 60 + m).where(normal, 0)
    d = d + pd.to_timedelta(is_2400.astype(int), unit="D")
    # Raw airport IDs are treated as valid identifiers iff positive finite integers.
    for col in ("OriginAirportID", "DestAirportID"):
        x = pd.to_numeric(frame[col], errors="coerce")
        valid &= x.notna() & np.isfinite(x) & (x > 0) & (x == np.floor(x))
        frame[col] = x.astype("Int64")
    frame["match_date"] = d.dt.strftime("%Y-%m-%d")
    frame["band1"] = (mins // 60).astype("Int64")
    frame["valid_key"] = valid
    return frame


def score(frame: pd.DataFrame) -> pd.DataFrame:
    """Contract scoring: known cancelled/diverted first, unknown outcomes fail."""
    ca = pd.to_numeric(frame.Cancelled, errors="coerce")
    di = pd.to_numeric(frame.Diverted, errors="coerce")
    ad = pd.to_numeric(frame.ArrDelay, errors="coerce")
    # The contract would stop on nonbinary flags; enforce that rather than coerce.
    for x, name in ((ca, "Cancelled"), (di, "Diverted")):
        bad = x.notna() & ~x.isin([0, 1])
        if bad.any():
            raise ValueError(f"nonbinary {name}: {int(bad.sum())}")
    bad_delay = ad.notna() & ~np.isfinite(ad)
    if bad_delay.any():
        raise ValueError(f"nonfinite ArrDelay: {int(bad_delay.sum())}")
    known_fail = (ca == 1) | (di == 1)
    completed = (ca == 0) & (di == 0) & ad.notna()
    frame["y"] = (completed & (ad < 15)).astype(np.int64)
    frame["u"] = (~known_fail & ~completed).astype(np.int64)
    return frame


def one_month(source: dict) -> str:
    """Stream a source ZIP and save carrier/cell aggregates only."""
    path = EP / source["path"]
    all_parts, cell_parts = [], []
    with zipfile.ZipFile(path) as archive:
        member = next(n for n in archive.namelist() if n.endswith(".csv"))
        with archive.open(member) as raw:
            for f in pd.read_csv(raw, usecols=USECOLS, chunksize=200_000, low_memory=False):
                f = f[f.Reporting_Airline.isin([UA, WN])].copy()
                if f.empty:
                    continue
                # Confirm the fixed operator identity rather than using code alone.
                good_id = f.apply(lambda r: r.DOT_ID_Reporting_Airline == IDS[r.Reporting_Airline], axis=1)
                f = f[good_id].copy()
                f = score(f)
                all_parts.append(f.groupby(["Year", "Reporting_Airline"], observed=True)
                                 .agg(n=("y", "size"), y=("y", "sum"), u=("u", "sum")).reset_index())
                f = parse_schedule(f)
                f = f[f.valid_key].copy()
                if f.empty:
                    continue
                # Maintain all three requested partitions in one compact table.
                for width in (1, 2, 4):
                    g = f.assign(window=(f.band1 // width).astype(int), width=width)
                    cell_parts.append(g.groupby(["Year", "Reporting_Airline", "match_date",
                                                 "OriginAirportID", "DestAirportID", "width", "window"],
                                                observed=True)
                                      .agg(n=("y", "size"), y=("y", "sum"), u=("u", "sum")).reset_index())
    all_df = pd.concat(all_parts).groupby(["Year", "Reporting_Airline"], as_index=False).sum(numeric_only=True)
    cells = pd.concat(cell_parts).groupby(["Year", "Reporting_Airline", "match_date",
                                            "OriginAirportID", "DestAirportID", "width", "window"],
                                           as_index=False).sum(numeric_only=True)
    stem = path.stem
    target = WORK / f"{stem}.pkl"
    pd.to_pickle({"all": all_df, "cells": cells}, target)
    return str(target)


def panel(paths: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    objs = [pd.read_pickle(p) for p in paths]
    all_df = pd.concat([x["all"] for x in objs]).groupby(["Year", "Reporting_Airline"], as_index=False).sum(numeric_only=True)
    c = pd.concat([x["cells"] for x in objs])
    key = ["Year", "match_date", "OriginAirportID", "DestAirportID", "width", "window"]
    c = c.groupby(key + ["Reporting_Airline"], as_index=False).sum(numeric_only=True)
    wide = c.pivot(index=key, columns="Reporting_Airline", values=["n", "y", "u"]).fillna(0)
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    return all_df, wide.reset_index()


def estimate(cells: pd.DataFrame, years: list[int], width: int) -> dict:
    x = cells[(cells.Year.isin(years)) & (cells.width == width)].copy()
    x = x[(x.n_UA > 0) & (x.n_WN > 0)].copy()
    x["w"] = (x.n_UA + x.n_WN) / 2.0
    x["d"] = x.y_UA / x.n_UA - x.y_WN / x.n_WN
    x["num"] = x.w * x.d
    # Assignment numerators implement the specified one-sided unknown endpoints.
    x["num_low"] = x.w * (x.y_UA / x.n_UA - (x.y_WN + x.u_WN) / x.n_WN)
    x["num_high"] = x.w * ((x.y_UA + x.u_UA) / x.n_UA - x.y_WN / x.n_WN)
    den = float(x.w.sum())
    out = {"cells": int(len(x)), "ua_n": int(x.n_UA.sum()), "wn_n": int(x.n_WN.sum()),
           "weight": den, "D": float(x.num.sum() / den),
           "D_low": float(x.num_low.sum() / den), "D_high": float(x.num_high.sum() / den),
           "data": x}
    return out


def interval_a(est: dict) -> dict:
    """Amendment 2 exact 28-day studentized circular moving-block algorithm."""
    x = est["data"].copy()
    assignments = ["num", "num_low", "num_high"]
    # Contract seed retained from METHOD; draw year then the complete row-major matrix.
    rng = np.random.Generator(np.random.PCG64(20261005))
    starts, arrays = {}, {}
    for year in (2023, 2024):
        dates = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
        d = x[x.Year == year].groupby("match_date")[["w"] + assignments].sum()
        d.index = pd.to_datetime(d.index)
        d = d.reindex(dates, fill_value=0.0)
        arrays[year] = {col: d[col].to_numpy(float) for col in ["w"] + assignments}
        T, q, r = len(dates), len(dates) // 28, len(dates) % 28
        starts[year] = rng.integers(0, T, size=(1999, q + 1), endpoint=False)
    result = {}
    for assignment in assignments:
        D = est[{"num": "D", "num_low": "D_low", "num_high": "D_high"}[assignment]]
        orig_se_sq, db, seb = 0.0, np.empty(1999), np.empty(1999)
        totals = []
        cache = {}
        for year in (2023, 2024):
            N, W = arrays[year][assignment], arrays[year]["w"]
            T, q, r = len(W), len(W) // 28, len(W) % 28
            ix = (np.arange(28)[None, :] + np.arange(T)[:, None]) % T
            FN, FW = N[ix].sum(1), W[ix].sum(1)
            ih = (np.arange(r)[None, :] + np.arange(T)[:, None]) % T
            HN, HW = N[ih].sum(1), W[ih].sum(1)
            RF, RH = FN - D * FW, HN - D * HW
            orig_se_sq += q * RF.var(ddof=0) * T / (T - 28) + RH.var(ddof=0) * T / (T - r)
            s = starts[year]
            cache[year] = (FN, FW, HN, HW, s, q)
            totals.append((FN[s[:, :q]].sum(1) + HN[s[:, q]], FW[s[:, :q]].sum(1) + HW[s[:, q]]))
        tn = sum(z[0] for z in totals); tw = sum(z[1] for z in totals)
        db[:] = tn / tw
        for b in range(1999):
            vs = 0.0
            for year in (2023, 2024):
                FN, FW, HN, HW, s, q = cache[year]
                ind = s[b, :q]
                full = FN[ind] - db[b] * FW[ind]
                short = HN[ind] - db[b] * HW[ind]
                vs += q * full.var(ddof=1) + short.var(ddof=1)
            seb[b] = math.sqrt(vs) / tw[b]
        se = math.sqrt(orig_se_sq) / est["weight"]
        z = (db - D) / seb
        loq, hiq = np.quantile(z, [.005, .995], method="linear")
        floor = student_t.ppf(.995, 24)
        qp, qm = max(hiq, floor), min(loq, -floor)
        result[assignment] = {"D": D, "se": se, "q_minus": float(qm), "q_plus": float(qp),
                              "lower": float(D - qp * se), "upper": float(D - qm * se),
                              "draw_min_se": float(seb.min()), "draw_max_se": float(seb.max())}
    result["envelope"] = {"lower": min(v["lower"] for v in result.values()),
                          "upper": max(v["upper"] for v in result.values())}
    return result


def entry(value, n, definition):
    return {"value": value, "n": n, "definition": definition}


def main():
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True, exist_ok=True)
    sources = json.loads(MANIFEST.read_text())["sources"]
    with cf.ProcessPoolExecutor(max_workers=10) as pool:
        paths = list(pool.map(one_month, sources))
    all_df, cells = panel(paths)
    shutil.rmtree(WORK)
    e = {(label, width): estimate(cells, years, width)
         for label, years in (("A", [2023, 2024]), ("B", [2025]), ("2023", [2023]), ("2024", [2024]))
         for width in (1, 2, 4)}
    values = {}
    for label in ("A", "B", "2023", "2024"):
        z = e[(label, 2)]
        values[f"{label}_comparable_cells"] = entry(z["cells"], z["cells"], "Shared UA/WN directional route-date-two-hour cells.")
        values[f"{label}_ua_matched_flights"] = entry(z["ua_n"], z["ua_n"], "UA scheduled flights in shared two-hour cells.")
        values[f"{label}_wn_matched_flights"] = entry(z["wn_n"], z["wn_n"], "WN scheduled flights in shared two-hour cells.")
        values[f"{label}_cell_weight_sum"] = entry(z["weight"], z["cells"], "Sum of cell weights (n_UA+n_WN)/2.")
        values[f"{label}_adjusted_gap"] = entry(z["D"], z["cells"], "Weighted timely-arrival gap UA minus WN, primary scoring.")
        values[f"{label}_adjusted_gap_low"] = entry(z["D_low"], z["cells"], "Unknowns assigned against UA in shared cells.")
        values[f"{label}_adjusted_gap_high"] = entry(z["D_high"], z["cells"], "Unknowns assigned for UA in shared cells.")
    for label in ("A", "B"):
        for width, name in ((1, "one_hour"), (4, "four_hour")):
            z = e[(label, width)]
            values[f"{label}_{name}_gap"] = entry(z["D"], z["cells"], f"Primary adjusted UA-minus-WN gap using {width}-hour cells.")
    for label, years in (("A", [2023, 2024]), ("B", [2025])):
        for carrier in (UA, WN):
            r = all_df[(all_df.Year.isin(years)) & (all_df.Reporting_Airline == carrier)].sum(numeric_only=True)
            values[f"{label}_{carrier.lower()}_all_flights_rate"] = entry(float(r.y / r.n), int(r.n), "Unadjusted all-scheduled primary timely-arrival rate.")
    ia = interval_a(e[("A", 2)])
    for assignment in ("num", "num_low", "num_high"):
        for stat in ("se", "q_minus", "q_plus", "lower", "upper"):
            values[f"A_interval_{assignment}_{stat}"] = entry(ia[assignment][stat], 1999, f"Amendment 2 A {assignment} {stat}.")
    for stat in ("lower", "upper"):
        values[f"A_interval_envelope_{stat}"] = entry(ia["envelope"][stat], 1999, "Amendment 2 A envelope across primary/lower/upper assignments.")
    OUT.mkdir(exist_ok=True)
    (OUT / "values.json").write_text(json.dumps(values, indent=2, sort_keys=True) + "\n")
    print(f"wrote {len(values)} values")


if __name__ == "__main__":
    main()
