#!/usr/bin/env python3
"""Analyze an accepted adverse reduced snapshot without scoring the grid.

All integrations here start at a diagnostic BDF checkpoint near 359 s, not
the preregistered t=0 initial condition. The fixed tolerances are retained.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from r3_resource_total_precise_diagnostic_v1 import R3ResourceTotalPreciseDiagnostic
from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from verify_reduction_audit_v0 import ROOT


SNAPSHOT = ROOT / "results/reduction/r3_aminoacylation_qssa/adverse_bdf_stepper_001/state_0006.npz"
GRID = ROOT / "docs/reduction/r3_validation_grid_v1.csv"
RTOL = 1e-10
ATOL = 1e-14
WINDOW = 0.1
BUDGET = 5000


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_trial(name: str, t0: float, z: np.ndarray, q: np.ndarray,
                initial: np.ndarray) -> dict:
    runtime = (R3ResourceTotalPreciseDiagnostic() if name == "decimal_bdf" else
               R3ResourceTotalRuntimeV2())
    runtime._last_root = q.copy()
    progress = {"calls": 0, "t": t0}
    started = time.perf_counter()

    def root(zz):
        found = runtime.solve_fast(zz, initial)
        if not found["valid_local_root"]:
            raise RuntimeError("Physical closure failed")
        return found["q"]

    def rhs(t, zz):
        progress["calls"] += 1
        progress["t"] = float(t)
        if progress["calls"] > BUDGET:
            raise RuntimeError("RHS call budget")
        return runtime.slow_rhs(zz, root(zz), initial)[0]

    def jac(t, zz):
        return runtime.slow_jacobian(zz, root(zz), initial)[0]

    method = "LSODA" if name == "lsoda" else "BDF"
    trial = {"name": name, "method": method, "rtol": RTOL, "atol": ATOL,
             "start_t": t0, "target_t": t0 + WINDOW, "rhs_call_budget": BUDGET}
    try:
        solved = solve_ivp(rhs, (t0, t0 + WINDOW), z, method=method,
                           jac=jac, rtol=RTOL, atol=ATOL)
        trial.update(success=bool(solved.success), message=solved.message,
                     last_t=float(solved.t[-1]), nfev=int(solved.nfev),
                     njev=int(solved.njev))
    except Exception as error:
        trial.update(success=False, error=str(error),
                     last_t=progress["t"], nfev=progress["calls"])
    trial["wall_s"] = time.perf_counter() - started
    return trial


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        parser.error(f"Refusing to overwrite {out}")
    with GRID.open(encoding="utf-8", newline="") as stream:
        row = next(row for row in csv.DictReader(stream)
                   if row["condition_id"] == "R3_ADVERSE")
    with np.load(SNAPSHOT) as data:
        t0, z, q = float(data["t"]), data["z"], data["q"]
    assert z.shape == (193,) and q.shape == (21,) and 359 < t0 < 360
    runtime = R3ResourceTotalRuntimeV2()
    scales = json.loads(row["initial_scale_json"])
    x0 = np.array([float(runtime.source.author_initial[name]) * scales.get(name, 1.)
                   for name in runtime.source.species])
    root = runtime.solve_fast(z, x0, seed=q)
    assert root["valid_local_root"] and root["residual_max"] <= 1e-10
    standard = runtime.slow_rhs(z, root["q"], x0)
    precise = R3ResourceTotalPreciseDiagnostic().slow_rhs(z, root["q"], x0)
    direction = standard[0] / np.max(np.abs(standard[0]))
    jacobian, _ = runtime.slow_jacobian(z, root["q"], x0)
    prediction = jacobian @ direction
    differences = []
    for h in (1e-2, 1e-3, 1e-4, 1e-5):
        sampled = []
        valid = []
        for sign in (1, -1):
            zz = z + sign * h * direction
            found = runtime.solve_fast(zz, x0, seed=root["q"])
            valid.append(bool(found["valid_local_root"]))
            sampled.append(runtime.slow_rhs(zz, found["q"], x0)[0])
        finite = (sampled[0] - sampled[1]) / (2 * h)
        differences.append({"h": h, "physical_roots": valid,
                            "max_abs_directional_error": float(np.max(np.abs(finite - prediction))),
                            "max_abs_finite_derivative": float(np.max(np.abs(finite)))})
    rates = standard[1]
    cancellation = {}
    for name in ("CP", "GDP", "ATP", "GlyRS"):
        i = runtime.source.species.index(name)
        terms = [float(coef) * rates[j] for j, coef in runtime.source.source_rows[i]]
        gross = float(sum(abs(value) for value in terms))
        net = math.fsum(terms)
        cancellation[name] = {"gross_abs_rate_sum": gross,
                              "net_rate": net,
                              "gross_to_net_abs_ratio": gross / max(abs(net), 1e-30)}
    eigen = np.linalg.eigvals(jacobian)
    result = {
        "schema_version": "1.0",
        "status": "REDUCED_SNAPSHOT_DIAGNOSTIC_NOT_REGISTERED_GRID_RESULT",
        "snapshot_t": t0,
        "root_residual_max": float(root["residual_max"]),
        "max_float_vs_decimal_rhs_difference": float(np.max(np.abs(standard[0] - precise[0]))),
        "max_float_vs_decimal_rate_difference": float(np.max(np.abs(standard[1] - precise[1]))),
        "jacobian_eigen_real_min": float(np.min(eigen.real)),
        "jacobian_eigen_real_max": float(np.max(eigen.real)),
        "directional_checks": differences,
        "rate_cancellation": cancellation,
        "local_trials": [],
    }
    out.mkdir(parents=True)
    result_path = out / "result.json"
    for name in ("bdf", "lsoda", "decimal_bdf"):
        result["local_trials"].append(local_trial(name, t0, z, q, x0))
        result_path.write_text(json.dumps(result, indent=2) + "\n",
                               encoding="utf-8", newline="\n")
        print(f"{name}: {result['local_trials'][-1]['last_t']:.9f}, "
              f"{result['local_trials'][-1]['nfev']} RHS", flush=True)
    inputs = {
        "snapshot": sha(SNAPSHOT),
        "grid": sha(GRID),
        "canonical_sbml": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
        "runtime_v2": sha(ROOT / "scripts/r3_resource_total_runtime_v2.py"),
        "precise_diagnostic": sha(ROOT / "scripts/r3_resource_total_precise_diagnostic_v1.py"),
        "script": sha(Path(__file__)),
    }
    (out / "manifest.json").write_text(json.dumps({
        "schema_version": "1.0",
        "status": "HASH_BOUND_SNAPSHOT_DIAGNOSTIC_NOT_GRID_ACCEPTANCE",
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "inputs_sha256": inputs, "result_sha256": sha(result_path),
        "exit_code": 0,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
