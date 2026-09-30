#!/usr/bin/env python3
"""Retained 0-0.1 s diagnostic for the dynamic-resource R3 candidate."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import traceback

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from r3_resource_total_runtime_v1 import MATRIX
from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2 as R3ResourceTotalRuntime
from validate_source_coordinates_full_v1 import rate_jacobian, rate_vector
from verify_reduction_audit_v0 import OUT, ROOT

RUN = ROOT / "results/reduction/r3_resource_total_smoke_v1/attempt_002"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if RUN.exists():
        raise SystemExit(f"Refusing to overwrite diagnostic: {RUN}")
    RUN.mkdir(parents=True)
    r = R3ResourceTotalRuntime()
    s = r.source
    x0 = np.array([float(s.author_initial[name]) for name in s.species])
    z0 = r.initial_slow(x0)
    times = np.r_[0., np.geomspace(1e-4, 0.1, 20)]
    info = {
        "status": "EXPLORATORY_RESOURCE_TOTAL_SMOKE_NOT_R3_VALIDATION",
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
        "python_version": platform.python_version(), "numpy_version": np.__version__,
        "scipy_version": scipy.__version__, "condition_id": "R3_BASE",
        "time_start": 0., "time_end": 0.1, "report_points": len(times),
        "rtol": 1e-10, "atol": 1e-14,
        "canonical_sbml_sha256": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
        "method_sha256": sha(OUT / "r3_aminoacylation_qssa_method.md"),
        "grid_sha256": sha(OUT / "r3_validation_grid_v1.csv"),
        "runtime_sha256": sha(ROOT / "scripts/r3_resource_total_runtime_v2.py"),
        "accounting_matrix_sha256": sha(MATRIX),
    }
    calls = {"closure": 0, "closure_nfev": 0, "warm_start_newton": 0,
             "hybr_fallback": 0, "max_residual": 0., "min_resource": float("inf")}

    def full_rhs(_t, x):
        return np.asarray(s.full_rhs_from_rates(rate_vector(s, x)))

    def full_jac(_t, x):
        return r.S @ rate_jacobian(s, x)

    def closure(z):
        root = r.solve_fast(z, x0)
        calls["closure"] += 1
        calls["closure_nfev"] += root["nfev"]
        calls[root["method"]] += 1
        calls["max_residual"] = max(calls["max_residual"], root["residual_max"])
        calls["min_resource"] = min(calls["min_resource"], root["min_resource"])
        if not root["valid_local_root"]:
            raise RuntimeError(f"Invalid physical root: {root}")
        return root["q"]

    def slow_rhs(_t, z):
        return r.slow_rhs(z, closure(z), x0)[0]

    def slow_jac(_t, z):
        return r.slow_jacobian(z, closure(z), x0)[0]

    try:
        full = solve_ivp(full_rhs, (0., 0.1), x0, method="BDF", jac=full_jac,
                         t_eval=times, rtol=1e-10, atol=1e-14)
        info["full_solver"] = {"success": bool(full.success), "message": full.message,
                               "nfev": full.nfev, "njev": full.njev, "nlu": full.nlu}
        if not full.success:
            raise RuntimeError(full.message)
        reduced = solve_ivp(slow_rhs, (0., 0.1), z0, method="BDF", jac=slow_jac,
                            t_eval=times, rtol=1e-10, atol=1e-14)
        info["reduced_solver"] = {"success": bool(reduced.success),
                                  "message": reduced.message, "nfev": reduced.nfev,
                                  "njev": reduced.njev, "nlu": reduced.nlu}
        if not reduced.success:
            raise RuntimeError(reduced.message)
        states = []
        for z in reduced.y.T:
            root = r.solve_fast(z, x0)
            if not root["valid_local_root"]:
                raise RuntimeError("Output-time closure invalid")
            states.append(root["state"])
        xred = np.asarray(states)
        xfull = full.y.T
        np.savez_compressed(RUN / "trajectories.npz", times=times,
                            full_state=xfull, reduced_state=xred)
        scale = np.maximum(np.max(np.abs(xfull), axis=0), 1e-6)
        error = np.max(np.abs(xred - xfull), axis=0) / scale
        post = times >= 0.05
        post_error = np.max(np.abs(xred[post] - xfull[post]), axis=0) / scale
        names = ("ATP", "AMP", "PPi", "PO4", "GlytRNAGlyGCC", "MettRNAfMetCAU",
                 "GlyAMP", "MetAMP")
        info["diagnostics"] = {
            "max_all_species_E_inf": float(np.max(error)),
            "t0_max_abs_initial_layer_jump": float(np.max(np.abs(xred[0] - xfull[0]))),
            "min_reduced_state": float(np.min(xred)),
            "selected_post_0p05_E_inf": {name: float(post_error[s.index[name]])
                                       for name in names if name in s.index},
        }
        info["status"] = "EXPLORATORY_RESOURCE_TOTAL_SMOKE_SOLVED_NOT_R3_VALIDATION"
    except Exception as exc:
        info["failure"] = str(exc)
        (RUN / "traceback.log").write_text(traceback.format_exc(), encoding="utf-8", newline="\n")
    info["closure_counters"] = calls
    (RUN / "result.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(info, indent=2))
    return 0 if info["status"] == "EXPLORATORY_RESOURCE_TOTAL_SMOKE_SOLVED_NOT_R3_VALIDATION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
