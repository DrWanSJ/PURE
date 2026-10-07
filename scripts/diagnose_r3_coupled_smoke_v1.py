#!/usr/bin/env python3
"""Diagnostic 0-1 s full-versus-QSSA coupled solve before decisive R3 grid."""
from __future__ import annotations

import hashlib
import json
import math
import platform
import re
import sys
import traceback
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from r3_candidate_runtime_v1 import R3CandidateRuntime
from validate_source_coordinates_full_v1 import rate_jacobian, rate_vector
from verify_reduction_audit_v0 import OUT, ROOT

RUN = ROOT / "results/reduction/r3_coupled_smoke_v1/attempt_002"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if RUN.exists():
        raise SystemExit(f"Refusing to overwrite diagnostic: {RUN}")
    RUN.mkdir(parents=True)
    runtime = R3CandidateRuntime()
    source = runtime.source
    x0 = np.array([float(source.author_initial[name]) for name in source.species])
    z0 = runtime.initial_slow(x0)
    grid = np.r_[0.0, np.geomspace(1e-4, 1.0, 40)]
    result = {"schema_version": "1.0", "status": "EXPLORATORY_COUPLED_SMOKE_NOT_R3_VALIDATION",
              "canonical_sbml_sha256": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
              "method_sha256": sha(OUT / "r3_aminoacylation_qssa_method.md"),
              "grid_sha256": sha(OUT / "r3_validation_grid_v1.csv"),
              "runtime_sha256": sha(ROOT / "scripts/r3_candidate_runtime_v1.py"),
              "carrier_chart_sha256": sha(OUT / "r3_carrier_chart_v1.json"),
              "python_executable": sys.executable, "python_version": platform.python_version(),
              "numpy_version": np.__version__, "scipy_version": scipy.__version__,
              "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
              "condition_id": "R3_BASE", "time_start": 0.0, "time_end": 1.0,
              "report_points": len(grid), "rtol": 1e-10, "atol": 1e-14}
    counters = {"closure_calls": 0, "closure_nfev": 0, "jacobian_calls": 0,
                "max_fast_residual": 0.0, "minimum_q": float("inf"),
                "minimum_carrier": float("inf"), "max_Gq_condition_number": 0.0}

    def full_rhs(_t, x):
        rates = rate_vector(source, x)
        return np.asarray(source.full_rhs_from_rates(rates))

    def full_jac(_t, x):
        return runtime.S @ rate_jacobian(source, x)

    def closure(z):
        solved = runtime.solve_fast(z, x0)
        counters["closure_calls"] += 1
        counters["closure_nfev"] += solved["nfev"]
        counters["max_fast_residual"] = max(counters["max_fast_residual"], solved["residual_max"])
        counters["minimum_q"] = min(counters["minimum_q"], solved["min_q"])
        counters["minimum_carrier"] = min(counters["minimum_carrier"], solved["min_carrier"])
        if not solved["valid_local_root"]:
            raise RuntimeError(f"Invalid closure: residual={solved['residual_max']}; "
                               f"min_q={solved['min_q']}; min_carrier={solved['min_carrier']}; "
                               f"message={solved['message']}")
        return solved["q"]

    def reduced_rhs(_t, z):
        q = closure(z)
        return runtime.slow_rhs(z, q, x0)[0]

    def reduced_jac(_t, z):
        q = closure(z)
        jac, diagnostics = runtime.slow_jacobian(z, q, x0)
        counters["jacobian_calls"] += 1
        counters["max_Gq_condition_number"] = max(counters["max_Gq_condition_number"],
                                                   diagnostics["Gq_condition_number"])
        return jac

    try:
        full = solve_ivp(full_rhs, (0.0, 1.0), x0, method="BDF", jac=full_jac,
                         t_eval=grid, rtol=1e-10, atol=1e-14)
        result["full_solver"] = {"success": bool(full.success), "message": full.message,
                                 "nfev": full.nfev, "njev": full.njev, "nlu": full.nlu}
        if not full.success:
            raise RuntimeError(full.message)
        reduced = solve_ivp(reduced_rhs, (0.0, 1.0), z0, method="BDF", jac=reduced_jac,
                            t_eval=grid, rtol=1e-10, atol=1e-14)
        result["reduced_solver"] = {"success": bool(reduced.success), "message": reduced.message,
                                    "nfev": reduced.nfev, "njev": reduced.njev, "nlu": reduced.nlu}
        if not reduced.success:
            raise RuntimeError(reduced.message)
        q_seed = x0[runtime.q_index]
        reconstructed = []
        for z in reduced.y.T:
            solved = runtime.solve_fast(z, x0, seed=q_seed)
            if not solved["valid_local_root"]:
                raise RuntimeError("Output-time closure invalid")
            q_seed = solved["q"]
            reconstructed.append(solved["state"])
        reduced_x = np.asarray(reconstructed)
        full_x = full.y.T
        np.savez_compressed(RUN / "trajectories.npz", times=grid, full_state=full_x,
                            reduced_state=reduced_x)
        detail = (OUT / "species_information_contract_detailed.md").read_text(encoding="utf-8")
        class_i_names = re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*I\*\*", detail, re.M)
        assert len(class_i_names) == 42
        class_i_indices = [source.index[name] for name in class_i_names]
        scale = np.maximum(np.max(np.abs(full_x), axis=0), 1e-6)
        errors = np.max(np.abs(reduced_x - full_x), axis=0) / scale
        result["exploratory_metrics"] = {
            "all_species_max_E_inf": float(np.max(errors)),
            "class_I_count": len(class_i_indices),
            "class_I_max_E_inf": float(np.max(errors[class_i_indices])),
            "fast_complex_max_E_inf": float(np.max(errors[runtime.q_index])),
            "minimum_reduced_state": float(np.min(reduced_x)),
            "t0_max_abs_initial_layer_jump": float(np.max(np.abs(reduced_x[0] - full_x[0]))),
        }
        result["status"] = "EXPLORATORY_COUPLED_SMOKE_SOLVED_NOT_R3_VALIDATION"
    except Exception as exc:
        result["failure"] = str(exc)
        (RUN / "traceback.log").write_text(traceback.format_exc(), encoding="utf-8", newline="\n")
    counters = {key: (value if not isinstance(value, float) or math.isfinite(value) else None)
                for key, value in counters.items()}
    result["closure_counters"] = counters
    (RUN / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": result["status"], "failure": result.get("failure"),
                      "full_solver": result.get("full_solver"),
                      "reduced_solver": result.get("reduced_solver"),
                      "exploratory_metrics": result.get("exploratory_metrics"),
                      "closure_counters": counters}, indent=2))
    return 0 if result["status"] == "EXPLORATORY_COUPLED_SMOKE_SOLVED_NOT_R3_VALIDATION" else 1


if __name__ == "__main__":
    raise SystemExit(main())
