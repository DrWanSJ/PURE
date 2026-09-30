#!/usr/bin/env python3
"""Bounded BDF trial-error audit from an actual adverse reduced snapshot.

This instruments SciPy 1.13.1's BDF trial solver only in this process. It is
not a registered t=0 grid integration or an acceptance result.
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
    names = [runtime.source.species[i] for i in runtime.slow_index]

    def observed_solver(fun, t_new, y_predict, c, psi, lu, solve_lu, scale, tol):
        converged, n_iter, y_new, d = original_solver(
            fun, t_new, y_predict, c, psi, lu, solve_lu, scale, tol)
        record = {"t_trial": float(t_new), "order": int(stepper.order),
                  "converged": bool(converged), "newton_iterations": int(n_iter)}
        if converged:
            weighted = np.abs(stepper.error_const[stepper.order] * d) / (
                ATOL + RTOL * np.abs(y_new))
            index = int(np.argmax(weighted))
            record.update(error_rms=float(np.linalg.norm(weighted) / np.sqrt(len(weighted))),
                          max_weighted_error=float(weighted[index]),
                          dominant_coordinate=names[index],
                          dominant_coordinate_value=float(y_new[index]),
                          dominant_error_abs=float(abs(stepper.error_const[stepper.order] * d[index])))
        trials.append(record)
        return converged, n_iter, y_new, d

    stop_reason = None
    bdf_module.solve_bdf_system = observed_solver
    try:
        for _ in range(args.accepted_steps):
            if STOP.exists():
                stop_reason = "STOP_MARKER"
                break
            if stepper.status != "running":
                stop_reason = stepper.status.upper()
                break
            before = len(trials)
            before_t = float(stepper.t)
            before_order = int(stepper.order)
            stepper.step()
            local_trials = trials[before:]
            steps.append({"t_from": before_t, "t_to": float(stepper.t),
                          "order_from": before_order, "order_to": int(stepper.order),
                          "trial_count": len(local_trials),
                          "newton_nonconverged": sum(not item["converged"] for item in local_trials),
                          "error_rejected": sum(item.get("error_rms", 0.) > 1. for item in local_trials)})
        if stop_reason is None:
            stop_reason = "ACCEPTED_STEP_BUDGET"
    except RuntimeError as error:
        stop_reason = str(error)
    finally:
        bdf_module.solve_bdf_system = original_solver

    high_error = [item for item in trials if item.get("error_rms", 0.) > 1.]
    accepted = [item for item in trials if item["converged"] and item.get("error_rms", float("inf")) <= 1.]
    result = {
        "schema_version": "1.0",
        "status": "BDF_ERROR_DIAGNOSTIC_NOT_REGISTERED_GRID_RESULT",
        "start_t": t0, "last_t": float(stepper.t), "stop_reason": stop_reason,
        "rtol": RTOL, "atol": ATOL,
        "accepted_steps": len(steps), "rhs_calls": rhs_calls,
        "trial_count": len(trials),
        "newton_nonconverged_trials": sum(not item["converged"] for item in trials),
        "error_rejected_trials": len(high_error),
        "accepted_trial_count": len(accepted),
        "top_error_rejection_coordinates": Counter(
            item["dominant_coordinate"] for item in high_error).most_common(10),
        "max_rejected_error_rms": max((item["error_rms"] for item in high_error), default=None),
        "min_accepted_step_s": min((item["t_to"] - item["t_from"] for item in steps), default=None),
        "max_accepted_step_s": max((item["t_to"] - item["t_from"] for item in steps), default=None),
        "steps": steps, "trials": trials,
    }
    out.mkdir(parents=True)
    result_path = out / "result.json"
    write_json(result_path, result)
    manifest = {
        "schema_version": "1.0",
        "status": "HASH_BOUND_BDF_ERROR_DIAGNOSTIC_NOT_GRID_ACCEPTANCE",
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "inputs_sha256": {
            "snapshot": sha(SNAPSHOT), "grid": sha(GRID),
            "canonical_sbml": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
            "runtime_v2": sha(ROOT / "scripts/r3_resource_total_runtime_v2.py"),
            "script": sha(Path(__file__)),
        },
        "result_sha256": sha(result_path), "exit_code": 0,
    }
    write_json(out / "manifest.json", manifest)
    print(f"{stop_reason}: t={stepper.t:.9f} steps={len(steps)} rhs={rhs_calls} "
          f"newton_reject={result['newton_nonconverged_trials']} "
          f"error_reject={len(high_error)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
