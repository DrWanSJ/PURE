#!/usr/bin/env python3
"""Locate worst R1 balance residuals and audit their stored-float arithmetic."""
from __future__ import annotations

import argparse
import json
from decimal import Decimal, localcontext
from pathlib import Path

import numpy as np

from runtime_reconstruction_rhs import SourceCoordinateRuntime
from validate_source_coordinates_full_v1 import stable_material_balance


def audit_one(runtime, arrays, prefix, initial):
    states = arrays[f"{prefix}_state"]
    extents = arrays[f"{prefix}_extent"]
    residuals = stable_material_balance(runtime, states, extents, initial)
    time_index, species_index = np.unravel_index(np.argmax(np.abs(residuals)), residuals.shape)
    with localcontext() as context:
        context.prec = 80
        state = Decimal.from_float(float(states[time_index, species_index]))
        start = Decimal.from_float(float(initial[species_index]))
        extent_change = sum(
            (Decimal.from_float(float(coefficient)) *
             Decimal.from_float(float(extents[time_index, reaction_index]))
             for reaction_index, coefficient in runtime.source_rows[species_index]),
            Decimal(0),
        )
        exact_stored_float_residual = state - start - extent_change
    return {
        "time_index": int(time_index),
        "time_seconds": float(arrays["times"][time_index]),
        "species_index": int(species_index),
        "species_id": runtime.species[species_index],
        "max_abs_fsum_residual": float(abs(residuals[time_index, species_index])),
        "exact_stored_float_residual_decimal": str(exact_stored_float_residual),
        "stoichiometric_terms": len(runtime.source_rows[species_index]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trajectory", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--chart", choices=("v1", "v2", "v3", "v4", "v5"), default="v3")
    args = parser.parse_args()
    runtime = SourceCoordinateRuntime(f"source_coordinate_certificate_{args.chart}.json")
    initial = np.array([float(runtime.author_initial[name]) for name in runtime.species])
    with np.load(args.trajectory) as arrays:
        report = {
            "status": "R1_BALANCE_STORED_FLOAT_DIAGNOSTIC",
            "trajectory": str(args.trajectory),
            "chart": args.chart,
            "full": audit_one(runtime, arrays, "full", initial),
            "reduced": audit_one(runtime, arrays, "reduced", initial),
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
