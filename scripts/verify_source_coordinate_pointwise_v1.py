#!/usr/bin/env python3
"""Apply the preregistered 1e-12 pointwise gate to one-rate-vector coordinates."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

from runtime_reconstruction_rhs import SourceCoordinateRuntime
from verify_reduction_audit_v0 import OUT, SOURCE


def scaled_error(first, second):
    return max(abs(a - b) / max(1.0, abs(a), abs(b)) for a, b in zip(first, second))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--chart", choices=("v1", "v2", "v3", "v4", "v5", "v6", "v7"), default="v1")
    args = parser.parse_args()
    certificate_name = f"source_coordinate_certificate_{args.chart}.json"
    runtime = SourceCoordinateRuntime(certificate_name)
    initial = [runtime.author_initial[name] for name in runtime.species]
    cases = [("author_initial", initial)] + [
        (f"positive_seed_{seed}", [Fraction(1, 10) + Fraction(((i + 1) * (seed + 3)) % 31, 10)
                                     for i in range(len(runtime.species))])
        for seed in (1, 7, 29)
    ]
    reports = []
    for label, source_state in cases:
        b = runtime.b_for_initial(source_state)
        reconstructed = runtime.reconstruct([source_state[i] for i in runtime.r_index], b)
        domain = runtime.domain(reconstructed)
        source_float = [float(value) for value in source_state]
        reconstruction_error = scaled_error(source_float, reconstructed)
        rates = runtime.rates(reconstructed)
        assert all(math.isfinite(rate) for rate in rates)
        full = runtime.full_rhs_from_rates(rates)
        lifted = runtime.coordinate_rhs_from_rates(rates)
        error = scaled_error(full, lifted)
        zero_rows = [i for i, value in enumerate(full) if value == 0]
        zero_row_error = max((abs(lifted[i]) for i in zero_rows), default=0.0)
        rounded = runtime.rounded_b_times_retained_rhs_diagnostic(rates)
        rounded_error = scaled_error([full[i] for i in runtime.e_index], rounded)
        reports.append({
            "case": label,
            "physical_domain": domain,
            "reconstruction_scaled_error": reconstruction_error,
            "pointwise_rhs_scaled_error": error,
            "zero_full_rhs_rows": len(zero_rows),
            "zero_row_absolute_error": zero_row_error,
            "rounded_B_times_rhs_R_diagnostic_scaled_error": rounded_error,
            "rate_vector_evaluations": 1,
        })
    result = {
        "schema_version": "1.0",
        "status": "R1_POINTWISE_IMPLEMENTATION_GATE_ONLY",
        "canonical_sbml_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "coordinate_certificate_file": certificate_name,
        "coordinate_certificate_sha256": hashlib.sha256((OUT / certificate_name).read_bytes()).hexdigest(),
        "metric": "max_i |f_full_i-f_lift_i|/max(1,|f_full_i|,|f_lift_i|)",
        "threshold": 1e-12,
        "cases": reports,
        "max_pointwise_rhs_scaled_error": max(case["pointwise_rhs_scaled_error"] for case in reports),
        "pass": all(case["physical_domain"]["feasible"] and
                    case["reconstruction_scaled_error"] <= 1e-12 and
                    case["pointwise_rhs_scaled_error"] <= 1e-12 and
                    case["zero_row_absolute_error"] <= 1e-12 for case in reports),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"pass": result["pass"], "max_pointwise_rhs_scaled_error":
                      result["max_pointwise_rhs_scaled_error"], "cases": reports}, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
