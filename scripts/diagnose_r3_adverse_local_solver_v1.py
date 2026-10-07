#!/usr/bin/env python3
"""Bounded local solver diagnostics at a saved adverse full-source state.

This does not start at the registered reduced initial state and cannot score
the 0-1000 s coupled grid. It only diagnoses numerical progress at the fixed
state-solver tolerances near a saved source point.
"""
from __future__ import annotations

import argparse
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

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from r3_resource_total_runtime_v3 import R3ResourceTotalRuntimeV3
from verify_reduction_audit_v0 import ROOT


FULL = ROOT / "results/reduction/r3_aminoacylation_qssa/restart_001/R3_ADVERSE/full_state.npz"
RTOL = 1e-10
ATOL = 1e-14
TARGET_SOURCE_TIME = 348.91
LOCAL_WINDOW = 0.1
CALL_BUDGET = 5000


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OnManifoldRuntime(R3ResourceTotalRuntimeV2):
    """Omit terms proportional to G=0 from the evaluated slow RHS."""

    def slow_rhs(self, z, q, full_initial):
        state = self.reconstruct(z, q, full_initial)
        rates = self.source.rates(state)
        derivative = np.array([
            math.fsum(value * rates[j] for j, value in self.source.source_rows[i])
            for i in self.slow_index
        ])
        amp = derivative[self.amp_pos]
        derivative[self.atp_pos] += amp
        derivative[self.ppi_pos] -= amp
        return derivative, np.asarray(rates), state


class StableFastRuntime(R3ResourceTotalRuntimeV2):
    """Accumulate the fast residual with math.fsum as a diagnostic."""

    def fast_rows(self, z, q, full_initial, with_jacobian=False):
        result = super().fast_rows(z, q, full_initial,
                                   with_jacobian=with_jacobian)
        state = result[-1]
        rates = []
        for j in self.fast_reactions:
            parameter, factors = self.source.rate_specs[j]
            value = parameter
            for i in factors:
                value *= state[i]
            rates.append(value)
        residual = np.array([
            math.fsum(float(coef) * float(rate)
                      for coef, rate in zip(row, rates) if coef)
            for row in self.Sq
        ])
        if with_jacobian:
            return residual, result[1], state
        return residual, state


def trial(name: str, t0: float, x: np.ndarray) -> dict:
    runtime = (OnManifoldRuntime() if name == "on_manifold_rhs" else
               StableFastRuntime() if name == "stable_fast_residual" else
               R3ResourceTotalRuntimeV2())
    z0 = runtime.initial_slow(x)
    fixed_seed = (runtime.solve_fast(z0, x)["q"].copy()
                  if name == "fixed_seed" else None)
    progress = {"calls": 0, "last_t": t0}
    started = time.perf_counter()

    def root(z):
        found = runtime.solve_fast(z, x, seed=fixed_seed)
        if not found["valid_local_root"]:
            raise RuntimeError("Physical closure failed")
        return found["q"]

    def rhs(t, z):
        progress["calls"] += 1
        progress["last_t"] = float(t)
        if progress["calls"] > CALL_BUDGET:
            raise RuntimeError("RHS call budget")
        return runtime.slow_rhs(z, root(z), x)[0]

    def jac(t, z):
        return runtime.slow_jacobian(z, root(z), x)[0]

    method = "LSODA" if name == "lsoda_analytic" else "BDF"
    analytic = name != "finite_difference_jacobian"
    output = {"strategy": name, "method": method,
              "jacobian": "analytic_implicit" if analytic else "scipy_finite_difference",
              "start_t": t0, "target_t": t0 + LOCAL_WINDOW,
              "rtol": RTOL, "atol": ATOL, "rhs_call_budget": CALL_BUDGET}
    try:
        solved = solve_ivp(rhs, (t0, t0 + LOCAL_WINDOW), z0,
                           method=method, jac=jac if analytic else None,
                           rtol=RTOL, atol=ATOL)
        output.update(success=bool(solved.success), message=solved.message,
                      last_t=float(solved.t[-1]), nfev=int(solved.nfev),
                      njev=int(solved.njev))
    except Exception as error:
        output.update(success=False, error=str(error),
                      last_t=progress["last_t"], nfev=progress["calls"])
    output["wall_s"] = time.perf_counter() - started
    return output


def root_spread(x: np.ndarray) -> dict:
    results = {}
    for name, cls in (("v2", R3ResourceTotalRuntimeV2),
                      ("v3", R3ResourceTotalRuntimeV3)):
        runtime = cls()
        z = runtime.initial_slow(x)
        q = x[runtime.q_index]
        seeds = (q, q * 0.9, q * 1.1, np.zeros_like(q))
        roots = [runtime.solve_fast(z, x, seed=seed) for seed in seeds]
        rhs = [runtime.slow_rhs(z, root["q"], x)[0] for root in roots]
        results[name] = {
            "physical_valid": [bool(root["valid_local_root"]) for root in roots],
            "fast_residual_max": [float(root["residual_max"]) for root in roots],
            "q_spread_max_abs": float(max(np.max(np.abs(a["q"] - b["q"]))
                                       for a in roots for b in roots)),
            "slow_rhs_spread_max_abs": float(max(np.max(np.abs(a - b))
                                                 for a in rhs for b in rhs)),
        }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        parser.error(f"Refusing to overwrite {out}")
    with np.load(FULL) as data:
        times, states = data["times"], data["state"]
    assert times.shape == (201,) and states.shape == (201, 241)
    index = int(np.argmin(np.abs(times - TARGET_SOURCE_TIME)))
    t0, x = float(times[index]), states[index]
    assert abs(t0 - TARGET_SOURCE_TIME) < 0.01
    out.mkdir(parents=True)
    result = {
        "schema_version": "1.0",
        "status": "LOCAL_DIAGNOSTIC_NOT_REGISTERED_FULL_COUPLED_VALIDATION",
        "meaning": "Saved full-source state is a local probe, not the reduced trajectory state",
        "source_state_index": index,
        "source_state_time_s": t0,
        "root_seed_spread": root_spread(x),
        "trials": [],
    }
    result_path = out / "result.json"
    for name in ("v2_analytic", "fixed_seed", "on_manifold_rhs",
                 "finite_difference_jacobian", "stable_fast_residual",
                 "lsoda_analytic"):
        result["trials"].append(trial(name, t0, x))
        result_path.write_text(json.dumps(result, indent=2) + "\n",
                               encoding="utf-8", newline="\n")
        print(f"{name}: {result['trials'][-1]['last_t']:.9f}, "
              f"{result['trials'][-1]['nfev']} RHS", flush=True)
    manifest = {
        "schema_version": "1.0",
        "status": "HASH_BOUND_LOCAL_DIAGNOSTIC_NOT_GRID_ACCEPTANCE",
        "command": [sys.executable, *sys.argv],
        "cwd": str(ROOT),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "script_sha256": sha(Path(__file__)),
        "full_source_state_sha256": sha(FULL),
        "runtime_v2_sha256": sha(ROOT / "scripts/r3_resource_total_runtime_v2.py"),
        "runtime_v3_sha256": sha(ROOT / "scripts/r3_resource_total_runtime_v3.py"),
        "result_sha256": sha(result_path),
        "exit_code": 0,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                       encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
