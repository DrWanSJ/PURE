#!/usr/bin/env python3
"""Measure full-coupled fast modes and coordinate timescales for an R3 case."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from verify_reduction_audit_v0 import OUT, ROOT

MATRIX = ROOT / "docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv"
METHOD = OUT / "r3_timescale_method_v1.md"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-state", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error(f"Refusing to overwrite {args.out}")
    data = np.load(args.full_state)
    times = data["times"]
    states = data["state"]
    assert states.shape == (201, 241) and times.shape == (201,)
    r = R3ResourceTotalRuntimeV2()
    x0 = states[0]
    z = np.array([r.initial_slow(x) for x in states])
    scale = np.maximum(np.max(np.abs(z), axis=0), 1e-6)
    with MATRIX.open(encoding="utf-8", newline="") as stream:
        moieties = {row["row"]: row for row in csv.DictReader(stream)}
    enzyme_weights = {
        enzyme: np.array([float(moieties[f"{enzyme}_total"][name])
                          for name in r.source.species])
        for enzyme in ("GlyRS", "MetRS")
    }
    rows = []
    for time, state, slow in zip(times, states, z):
        q = state[r.q_index]
        residual, gq, _ = r.fast_rows(slow, q, x0, with_jacobian=True)
        real_modes = np.real(np.linalg.eigvals(gq))
        nonattracting = int(np.count_nonzero(real_modes >= 0.))
        tau_fast = float("inf") if nonattracting else 1. / float(np.min(-real_modes))
        rates = r.source.rates(state)
        full_rhs = np.asarray(r.source.full_rhs_from_rates(rates))
        slow_rhs = r.T @ full_rhs
        active = np.abs(slow_rhs) > 0
        tau_slow = (float(np.min(scale[active] / np.abs(slow_rhs[active])))
                    if np.any(active) else float("inf"))
        values = {"time_s": float(time),
                  "fast_eigen_real_min": float(np.min(real_modes)),
                  "fast_eigen_real_max": float(np.max(real_modes)),
                  "nonattracting_fast_modes": nonattracting,
                  "tau_fast_s": tau_fast, "tau_slow_s": tau_slow,
                  "epsilon": tau_fast / tau_slow if math.isfinite(tau_fast) else float("inf"),
                  "epsilon_screen_pass": bool(tau_fast / tau_slow <= 0.01),
                  "fast_rhs_max_abs": float(np.max(np.abs(residual)))}
        for enzyme, substrate in (("GlyRS", "Gly"), ("MetRS", "Met")):
            total = float(enzyme_weights[enzyme] @ state)
            free = float(state[r.source.index[enzyme]])
            values[f"{enzyme}_total"] = total
            values[f"{enzyme}_free"] = free
            values[f"{enzyme}_occupied_fraction"] = (total - free) / total if total else float("nan")
            values[f"{substrate}_to_{enzyme}_total_ratio"] = (
                float(state[r.source.index[substrate]]) / total if total else float("nan"))
        rows.append(values)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "status": "COUPLED_FULL_TRAJECTORY_TIMESCALE_SCREEN_NOT_QSSA_VALIDATION",
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
        "python_version": platform.python_version(), "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "full_state_sha256": sha(args.full_state), "method_sha256": sha(METHOD),
        "matrix_sha256": sha(MATRIX), "runtime_v2_sha256": sha(ROOT / "scripts/r3_resource_total_runtime_v2.py"),
        "script_sha256": sha(Path(__file__)), "timescale_csv_sha256": sha(args.out),
        "sample_count": len(rows),
        "nonattracting_samples": sum(row["nonattracting_fast_modes"] > 0 for row in rows),
        "epsilon_screen_fail_samples": sum(not row["epsilon_screen_pass"] for row in rows),
        "max_finite_epsilon": max((row["epsilon"] for row in rows if math.isfinite(row["epsilon"])),
                                  default=None),
        "max_full_fast_rhs_abs": max(row["fast_rhs_max_abs"] for row in rows),
        "GlyRS_occupied_fraction_range": [min(row["GlyRS_occupied_fraction"] for row in rows),
                                            max(row["GlyRS_occupied_fraction"] for row in rows)],
        "MetRS_occupied_fraction_range": [min(row["MetRS_occupied_fraction"] for row in rows),
                                            max(row["MetRS_occupied_fraction"] for row in rows)],
    }
    summary_path = args.out.with_suffix(".json")
    if summary_path.exists():
        raise RuntimeError(f"Refusing to overwrite {summary_path}")
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
