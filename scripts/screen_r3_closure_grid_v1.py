#!/usr/bin/env python3
"""Exploratory multistart QSSA root screen on the registered R3 initial grid."""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

from r3_candidate_runtime_v1 import R3CandidateRuntime
from verify_reduction_audit_v0 import OUT, ROOT, fraction, rows

RUN = ROOT / "results/reduction/r3_closure_grid_screen_v1/attempt_005"
GRID = OUT / "r3_validation_grid_v1.csv"
METHOD = OUT / "r3_aminoacylation_qssa_method.md"
CHART = OUT / "r3_carrier_chart_v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if RUN.exists():
        raise SystemExit(f"Refusing to overwrite exploratory screen: {RUN}")
    RUN.mkdir(parents=True)
    runtime = R3CandidateRuntime()
    source = runtime.source
    records = []
    for condition in rows(GRID):
        scales = json.loads(condition["initial_scale_json"])
        initial = np.array([float(source.author_initial[name] * fraction(scales.get(name, 1)))
                            for name in source.species])
        z = runtime.initial_slow(initial)
        zero_seed = initial[runtime.q_index]
        alternate_seed = np.zeros(21)
        for prefix in ("GlyRS", "MetRS"):
            members = [j for j, name in enumerate(runtime.q_names) if name.startswith(prefix + "_")]
            alternate_seed[members] = 0.001 * initial[source.index[prefix]] / len(members)
        first = runtime.solve_fast(z, initial, seed=zero_seed)
        second = runtime.solve_fast(z, initial, seed=alternate_seed)
        branch_gap = float(np.max(np.abs(first["q"] - second["q"])))
        source_law_shift = max(abs(sum(float(value) * (first["state"][i] - initial[i])
                                       for i, value in law.items())) for law in source.laws)
        eigenvalues = np.linalg.eigvals(runtime.fast_rows(z, first["q"], initial, True)[1])
        real = np.real(eigenvalues)
        attracting = bool(np.all(real < 0))
        tau_fast = float(1.0 / min(-real)) if attracting else None
        records.append({
            "condition_id": condition["condition_id"],
            "first_solver_success": str(first["solver_success"]).lower(),
            "first_root_physical": str(first["physical"]).lower(),
            "first_residual_max": first["residual_max"],
            "first_hybr_initial_residual_max": first["hybr_initial_residual_max"],
            "first_newton_refinement_steps": first["newton_refinement_steps"],
            "first_min_q": first["min_q"],
            "first_min_carrier": first["min_carrier"],
            "first_min_full_state": float(np.min(first["state"])),
            "first_nfev": first["nfev"],
            "second_solver_success": str(second["solver_success"]).lower(),
            "second_root_physical": str(second["physical"]).lower(),
            "second_residual_max": second["residual_max"],
            "second_nfev": second["nfev"],
            "multistart_max_abs_q_gap": branch_gap,
            "same_local_branch": str(branch_gap <= 1e-8).lower(),
            "max_source_general_law_shift": source_law_shift,
            "fast_modes_attracting_at_t0": str(attracting).lower(),
            "slowest_fast_mode_real_part": float(max(real)),
            "initial_local_tau_fast_s": tau_fast if tau_fast is not None else "",
            "status": "EXPLORATORY_INITIAL_ROOT_ONLY",
        })
        print(f"{condition['condition_id']}: residual={first['residual_max']:.3g}, "
              f"physical={first['physical']}, branch_gap={branch_gap:.3g}, "
              f"law_shift={source_law_shift:.3g}, attracting={attracting}", flush=True)
    csv_path = RUN / "screen.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    result = {
        "schema_version": "1.0", "status": "EXPLORATORY_INITIAL_ROOT_SCREEN_NOT_R3_VALIDATION",
        "source_sha256": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
        "grid_sha256": sha(GRID), "method_sha256": sha(METHOD), "carrier_chart_sha256": sha(CHART),
        "runtime_script_sha256": sha(ROOT / "scripts/r3_candidate_runtime_v1.py"),
        "screen_script_sha256": sha(Path(__file__)),
        "screen_csv_sha256": sha(csv_path),
        "python_executable": sys.executable, "python_version": platform.python_version(),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
        "condition_count": len(records),
        "exit_code": 0,
        "physical_multistart_conditions": sum(row["first_root_physical"] == "true" and
                                              row["second_root_physical"] == "true" and
                                              row["same_local_branch"] == "true" for row in records),
        "warning": "Only initial roots and local fast Jacobian were screened. No coupled reduced trajectories or slow timescales were measured.",
    }
    (RUN / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
