#!/usr/bin/env python3
"""Compare the blind recheck values with Sol's released result JSON.

Point estimates are compared as proportions at abs tolerance 1e-9.  Interval
endpoints and SEs use the same 1e-9 tolerance; counts must be exactly equal.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
POINT_TOL = 1e-9
INTERVAL_TOL = 1e-9


def get(obj, path):
    for bit in path.split("."):
        obj = obj[int(bit)] if isinstance(obj, list) else obj[bit]
    return obj


def main():
    ours = json.loads((HERE / "values.json").read_text())
    sol = json.loads((ROOT / "studio/episodes/fair-airline/analysis/results.json").read_text())
    mappings = []

    def add(key, path, scale=1.0, kind="point"):
        mappings.append((key, path, scale, kind))

    main_paths = {"A": "primary_2023_2024", "B": "replication_2025"}
    assignments = {
        "": "primary_unknowns_fail",
        "_low": "lower_UA_unknowns_fail_WN_unknowns_succeed",
        "_high": "upper_UA_unknowns_succeed_WN_unknowns_fail",
    }
    for label, base in main_paths.items():
        g = base + ".adjusted_gap_ua_minus_wn_pp"
        add(f"{label}_comparable_cells", g + ".cells", kind="count")
        add(f"{label}_ua_matched_flights", g + ".n.UA", kind="count")
        add(f"{label}_wn_matched_flights", g + ".n.WN", kind="count")
        for suffix, assignment in assignments.items():
            add(f"{label}_adjusted_gap{suffix}", g + f".assignments.{assignment}.estimate", scale=.01)
        for carrier in ("ua", "wn"):
            add(f"{label}_{carrier}_all_flights_rate",
                base + f".unmatched_all_flights_on_time_pct.{carrier.upper()}.estimate", scale=.01)

    sens_paths = {"2023": "year_2023", "2024": "year_2024"}
    for label, sens in sens_paths.items():
        g = "primary_2023_2024.sensitivities." + sens + ".gap_ua_minus_wn_pp"
        add(f"{label}_comparable_cells", g + ".cells", kind="count")
        add(f"{label}_ua_matched_flights", g + ".n.UA", kind="count")
        add(f"{label}_wn_matched_flights", g + ".n.WN", kind="count")
        for suffix, assignment in assignments.items():
            add(f"{label}_adjusted_gap{suffix}", g + f".assignments.{assignment}.estimate", scale=.01)

    for label, base in main_paths.items():
        for ours_name, sol_name in (("one_hour", "window_1h"), ("four_hour", "window_4h")):
            g = base + ".sensitivities." + sol_name + ".gap_ua_minus_wn_pp"
            add(f"{label}_{ours_name}_gap", g + ".estimate", scale=.01)
            # The recheck's n for these gap entries is deliberately the cell count.
            # Compare it to Sol's cells separately from the point estimate.
            add(f"{label}_{ours_name}_gap#n", g + ".cells", kind="count")

    ag = "primary_2023_2024.adjusted_gap_ua_minus_wn_pp"
    for ours_assign, sol_assign in (("num", "primary_unknowns_fail"),
                                    ("num_low", "lower_UA_unknowns_fail_WN_unknowns_succeed"),
                                    ("num_high", "upper_UA_unknowns_succeed_WN_unknowns_fail")):
        add(f"A_interval_{ours_assign}_se", ag + ".original_se_pp.0", scale=.01, kind="interval")
        add(f"A_interval_{ours_assign}_lower", ag + f".assignments.{sol_assign}.interval.0", scale=.01, kind="interval")
        add(f"A_interval_{ours_assign}_upper", ag + f".assignments.{sol_assign}.interval.1", scale=.01, kind="interval")
    add("A_interval_envelope_lower", ag + ".interval.0", scale=.01, kind="interval")
    add("A_interval_envelope_upper", ag + ".interval.1", scale=.01, kind="interval")

    report, mapped = [], set()
    for key, path, scale, kind in mappings:
        n_key = key[:-2] if key.endswith("#n") else key
        ours_record = ours[n_key]
        actual = ours_record["n"] if key.endswith("#n") else ours_record["value"]
        expected = get(sol, path) * scale
        if kind == "count":
            ok = actual == expected
            tol = 0
        else:
            tol = INTERVAL_TOL if kind == "interval" else POINT_TOL
            ok = abs(actual - expected) <= tol
        report.append({"key": n_key, "sol_path": path, "comparison": "n" if key.endswith("#n") else "value",
                       "ours": actual, "sol": expected, "tolerance": tol, "matched": ok,
                       "difference": actual - expected})
        mapped.add(n_key)
    payload = {
        "tolerances": {"point_estimate": POINT_TOL, "interval_endpoint_or_se": INTERVAL_TOL,
                       "counts": "exact"},
        "summary": {"comparisons": len(report), "matched": sum(x["matched"] for x in report),
                    "mismatched": sum(not x["matched"] for x in report),
                    "unmapped_recheck_keys": sorted(set(ours) - mapped)},
        "comparisons": report,
    }
    (HERE / "compare.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
