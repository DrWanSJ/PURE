#!/usr/bin/env python3
"""Trace bounded BDF Newton break conditions at an adverse reduced state.

The SciPy 1.13.1 inner iteration is copied verbatim apart from recording its
norms and break reason. This is a diagnostic local restart, not grid evidence.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import scipy
import scipy.integrate._ivp.bdf as bdf_module
from scipy.integrate import BDF

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from verify_reduction_audit_v0 import ROOT


SNAPSHOT = ROOT / "results/reduction/r3_aminoacylation_qssa/adverse_bdf_stepper_001/state_0006.npz"
GRID = ROOT / "docs/reduction/r3_validation_grid_v1.csv"
STOP = ROOT / ".codex-auto-resume/STOP"
RTOL = 1e-10
ATOL = 1e-14


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--accepted-steps", type=int, default=200)
    parser.add_argument("--max-rhs-calls", type=int, default=5000)
    args = parser.parse_args()
    if args.accepted_steps <= 0 or args.max_rhs_calls <= 0:
        parser.error("Budgets must be positive")
    if STOP.exists():
        parser.error("STOP present")
    out = args.out.resolve()
    if out.exists():
        parser.error(f"Refusing to overwrite {out}")
    with GRID.open(encoding="utf-8", newline="") as stream:
        row = next(item for item in csv.DictReader(stream)
                   if item["condition_id"] == "R3_ADVERSE")
    with np.load(SNAPSHOT) as data:
        t0, z0, q0 = float(data["t"]), data["z"], data["q"]
    runtime = R3ResourceTotalRuntimeV2()
    scales = json.loads(row["initial_scale_json"])
    x0 = np.array([float(runtime.source.author_initial[name]) * scales.get(name, 1.)
                   for name in runtime.source.species])
    assert z0.shape == (193,) and q0.shape == (21,) and 359 < t0 < 360
    runtime._last_root = q0.copy()
    rhs_calls = 0

    def physical_root(z):
        found = runtime.solve_fast(z, x0)
        if not found["valid_local_root"]:
            raise RuntimeError("Physical root lost")
        return found["q"]

    def rhs(t, z):
        nonlocal rhs_calls
        rhs_calls += 1
        if rhs_calls > args.max_rhs_calls:
            raise RuntimeError("RHS call budget")
        return runtime.slow_rhs(z, physical_root(z), x0)[0]

    def jac(t, z):
        return runtime.slow_jacobian(z, physical_root(z), x0)[0]

    stepper = BDF(rhs, t0, z0, t0 + 0.1, jac=jac, rtol=RTOL, atol=ATOL)
    original_solver = bdf_module.solve_bdf_system
    trials = []
    steps = []

    def traced_solver(fun, t_new, y_predict, c, psi, lu, solve_lu, scale, tol):
        # Match scipy.integrate._ivp.bdf.solve_bdf_system in SciPy 1.13.1.
        d = 0
        y = y_predict.copy()
        dy_norm_old = None
        converged = False
        norms = []
        rates = []
        reason = "NEWTON_MAXITER"
        for k in range(bdf_module.NEWTON_MAXITER):
            f = fun(t_new, y)
            if not np.all(np.isfinite(f)):
                reason = "NONFINITE_RHS"
                break
            dy = solve_lu(lu, c * f - psi - d)
            dy_norm = bdf_module.norm(dy / scale)
            norms.append(float(dy_norm))
            if dy_norm_old is None:
                rate = None
            else:
                rate = dy_norm / dy_norm_old
            rates.append(None if rate is None else float(rate))
            if rate is not None and rate >= 1:
                reason = "NONCONTRACTING_CORRECTION"
                break
            if (rate is not None and
                    rate ** (bdf_module.NEWTON_MAXITER - k) / (1 - rate) * dy_norm > tol):
                reason = "PREDICTED_NONCONVERGENCE"
                break
            y += dy
            d += dy
            if dy_norm == 0 or (rate is not None and
                                rate / (1 - rate) * dy_norm < tol):
                converged = True
                reason = "CONVERGED"
                break
            dy_norm_old = dy_norm
        trials.append({"t_trial": float(t_new), "order": int(stepper.order),
                       "converged": converged, "break_reason": reason,
                       "iterations": k + 1, "scaled_correction_norms": norms,
                       "correction_rates": rates, "newton_tolerance": float(tol)})
        return converged, k + 1, y, d

    reason = None
    bdf_module.solve_bdf_system = traced_solver
    try:
        for _ in range(args.accepted_steps):
            if STOP.exists():
                reason = "STOP_MARKER"
                break
            if stepper.status != "running":
                reason = stepper.status.upper()
                break
            before = len(trials)
            before_t = float(stepper.t)
            stepper.step()
            steps.append({"t_from": before_t, "t_to": float(stepper.t),
                          "trial_count": len(trials) - before})
        if reason is None:
            reason = "ACCEPTED_STEP_BUDGET"
    except RuntimeError as error:
        reason = str(error)
    finally:
        bdf_module.solve_bdf_system = original_solver

    result = {
        "schema_version": "1.0",
        "status": "NEWTON_TRACE_DIAGNOSTIC_NOT_REGISTERED_GRID_RESULT",
        "start_t": t0, "last_t": float(stepper.t), "stop_reason": reason,
        "rtol": RTOL, "atol": ATOL, "accepted_steps": len(steps),
        "rhs_calls": rhs_calls, "trial_count": len(trials),
        "break_reason_counts": dict(Counter(item["break_reason"] for item in trials)),
        "steps": steps, "trials": trials,
    }
    out.mkdir(parents=True)
    write_json(out / "result.json", result)
    write_json(out / "manifest.json", {
        "schema_version": "1.0",
        "status": "HASH_BOUND_NEWTON_TRACE_NOT_GRID_ACCEPTANCE",
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "inputs_sha256": {
            "snapshot": sha(SNAPSHOT), "grid": sha(GRID),
            "canonical_sbml": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
            "runtime_v2": sha(ROOT / "scripts/r3_resource_total_runtime_v2.py"),
            "script": sha(Path(__file__)),
        },
        "result_sha256": sha(out / "result.json"), "exit_code": 0,
    })
    print(f"{reason}: t={stepper.t:.9f}, {len(steps)} steps, {rhs_calls} RHS, "
          f"breaks={result['break_reason_counts']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
