#!/usr/bin/env python3
"""Exploratory source-derived 21-complex closure at saved full-network states.

This is a diagnostic, not the preregistered full-coupled R3 validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import root

from runtime_reconstruction_rhs import SourceCoordinateRuntime
from verify_reduction_audit_v0 import OUT, rows

ROOT = Path(__file__).resolve().parents[1]
SAVED = ROOT / "results/reduction/r1_full_coupled_v4r3/decisive_001/trajectories.npz"
PARTITION = ROOT / "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition.json"
DEFAULT_OUTPUT = ROOT / "results/reduction/r3_closure_diagnostic_v1/attempt_004"
CARRIER_CHART = OUT / "r3_carrier_chart_v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output_path = args.out.resolve()
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite diagnostic: {output_path}")
    output_path.mkdir(parents=True)
    runtime = SourceCoordinateRuntime("source_coordinate_certificate_v4.json")
    partition = json.loads(PARTITION.read_text(encoding="utf-8"))
    q_names = partition["eliminated_complexes"]
    q_indices = np.array([runtime.index[name] for name in q_names])
    names = runtime.species
    source_rows = [runtime.source_rows[i] for i in q_indices]
    relevant = sorted({j for row in source_rows for j, _ in row})
    assert len(q_names) == 21 and len(relevant) == 103
    groups = {prefix: [i for i, name in enumerate(q_names) if name.startswith(prefix + "_")]
              for prefix in ("GlyRS", "MetRS")}
    enzyme_index = {prefix: runtime.index[prefix] for prefix in groups}
    chart = json.loads(CARRIER_CHART.read_text(encoding="utf-8"))
    assert chart["candidate_fast_species"] == q_names
    carrier_indices = [runtime.index[name] for name in chart["carrier_species"]]
    carrier_matrix = np.array([[float(row.get(name, 0)) for name in q_names]
                               for row in chart["carrier_delta_per_fast_delta_rows"]])
    assert carrier_matrix.shape == (6, 21)
    saved = np.load(SAVED)
    times, full = saved["times"], saved["full_state"]
    assert full.shape == (201, 241)
    report = []
    for point in (0, 1, 50, 100, 140, 160, 180, 200):
        reference = full[point].copy()
        q0 = reference[q_indices].copy()
        for coordinate in ("fixed_free_standard", "enzyme_total", "six_carrier_total"):
            def reconstruct(q):
                state = reference.copy()
                state[q_indices] = q
                if coordinate == "enzyme_total":
                    for prefix, members in groups.items():
                        state[enzyme_index[prefix]] = (reference[enzyme_index[prefix]]
                                                      + np.sum(q0[members]) - np.sum(q[members]))
                elif coordinate == "six_carrier_total":
                    state[carrier_indices] = reference[carrier_indices] + carrier_matrix @ (q - q0)
                return state

            def residual(q):
                state = reconstruct(q)
                rates = np.zeros(len(runtime.reactions))
                for j in relevant:
                    parameter, factors = runtime.rate_specs[j]
                    rate = parameter
                    for factor in factors:
                        rate *= state[factor]
                    rates[j] = rate
                return np.array([sum(value * rates[j] for j, value in row) for row in source_rows])

            result = root(residual, q0, method="hybr", options={"xtol": 1e-11})
            solved = reconstruct(result.x)
            absolute_residual = float(np.max(np.abs(residual(result.x))))
            min_q = float(np.min(result.x))
            min_enzyme = float(min(solved[enzyme_index[prefix]] for prefix in groups))
            min_carrier = float(np.min(solved[carrier_indices]))
            pool_shifts = {prefix: float(solved[enzyme_index[prefix]] - reference[enzyme_index[prefix]]
                                           + np.sum(result.x[members] - q0[members]))
                           for prefix, members in groups.items()}
            pool_compatible = all(abs(value) <= 1e-10 for value in pool_shifts.values())
            source_law_shifts = [float(sum(float(weight) * (solved[i] - reference[i])
                                           for i, weight in law.items())) for law in runtime.laws]
            max_source_law_shift = max(abs(value) for value in source_law_shifts)
            report.append({"time": float(times[point]), "sample_index": point,
                           "coordinate": coordinate, "solver_success": bool(result.success),
                           "solver_message": str(result.message), "nfev": int(result.nfev),
                           "max_abs_fast_rhs": absolute_residual,
                           "min_complex": min_q, "min_free_enzyme": min_enzyme,
                           "min_six_carriers": min_carrier,
                           "physical_branch": bool(min_q >= -1e-12 and min_carrier >= -1e-12),
                           "enzyme_pool_shifts": pool_shifts,
                           "same_initial_enzyme_pools": pool_compatible,
                           "source_general_law_shifts": source_law_shifts,
                           "max_source_general_law_shift": max_source_law_shift,
                           "same_initial_source_general_inventories": max_source_law_shift <= 1e-10,
                           "reference_complex_max_abs_difference": float(np.max(np.abs(result.x - q0)))})
            print(f"{coordinate} t={times[point]:.6g}: residual={absolute_residual:.3g}, "
                  f"min_q={min_q:.3g}, min_E={min_enzyme:.3g}, min_carrier={min_carrier:.3g}, "
                  f"pool_shift={max(abs(v) for v in pool_shifts.values()):.3g}, "
                  f"source_law_shift={max_source_law_shift:.3g}, "
                  f"success={result.success}", flush=True)
    output = {"schema_version": "1.0", "status": "EXPLORATORY_CLOSURE_DIAGNOSTIC_ONLY",
              "source_sha256": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
              "saved_full_trajectory_sha256": sha(SAVED),
              "candidate_partition_sha256": sha(PARTITION),
              "source_coordinate_certificate_sha256": sha(OUT / "source_coordinate_certificate_v4.json"),
              "carrier_chart_sha256": sha(CARRIER_CHART),
              "method_sha256": sha(OUT / "r3_aminoacylation_qssa_method.md"),
              "python_executable": sys.executable, "python_version": platform.python_version(),
              "numpy_version": np.__version__, "scipy_version": scipy.__version__,
              "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
              "q_count": len(q_names), "source_reaction_count_in_fast_rows": len(relevant),
              "samples": report}
    (output_path / "result.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
