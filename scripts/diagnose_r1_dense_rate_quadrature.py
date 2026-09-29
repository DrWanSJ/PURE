#!/usr/bin/env python3
"""Diagnose R1 extents by quadrature on each BDF dense-output step.

This is rate quadrature, not a model-side direct integrated-extent gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import solve_ivp

from runtime_reconstruction_rhs import SourceCoordinateRuntime
from validate_source_coordinates_full_v1 import (
    BALANCE_LIMIT, EXTENT_LIMIT, NEGATIVE_DIAGNOSTIC_FLOOR,
    RATE_LIMIT, TRAJECTORY_LIMIT, lift_matrix, metric_rows, negativity,
    rate_jacobian, rate_vector, source_matrix, stable_material_balance,
)
from verify_reduction_audit_v0 import OUT, SOURCE


def integrate_dense_rates(runtime, solution, lift, times, label):
    """Eight-node Gauss rule integrates each piecewise polynomial rate exactly."""
    nodes, weights = np.polynomial.legendre.leggauss(8)
    boundaries = np.union1d(solution.sol.ts, times)
    report_index = {float(value): i for i, value in enumerate(times)}
    extents = np.zeros((len(times), len(runtime.reactions)))
    total = np.zeros(len(runtime.reactions))
    compensation = np.zeros(len(runtime.reactions))
    for step, (start, stop) in enumerate(zip(boundaries[:-1], boundaries[1:]), 1):
        mid = (start + stop) / 2
        half = (stop - start) / 2
        coordinates = solution.sol(mid + half * nodes).T
        rates = np.stack([rate_vector(runtime, lift(row)) for row in coordinates])
        increment = half * (weights @ rates)
        corrected = increment - compensation
        updated = total + corrected
        compensation = (updated - total) - corrected
        total = updated
        if stop in report_index:
            extents[report_index[float(stop)]] = total
        if step % 2000 == 0:
            print(f"{label} dense steps {step}/{len(boundaries) - 1}", flush=True)
    assert np.all(np.isfinite(extents))
    return extents, len(boundaries) - 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--chart", choices=("v3", "v4"), default="v4")
    args = parser.parse_args()
    runtime = SourceCoordinateRuntime(f"source_coordinate_certificate_{args.chart}.json")
    source = source_matrix(runtime)
    source_r = source[runtime.r_index, :].tocsc()
    lift = lift_matrix(runtime)
    x0 = np.array([float(runtime.author_initial[name]) for name in runtime.species])
    r0 = x0[runtime.r_index]
    times = np.r_[0.0, np.geomspace(1e-4, 1000.0, 200)]
    options = dict(method="BDF", rtol=1e-12, atol=1e-14,
                   t_eval=times, dense_output=True)

    print("Integrating state-only full source with dense output", flush=True)
    full = solve_ivp(lambda t, x: source @ rate_vector(runtime, x),
                     (0.0, 1000.0), x0,
                     jac=lambda t, x: source @ rate_jacobian(runtime, x),
                     **options)
    print(f"full success={full.success} nfev={full.nfev}: {full.message}", flush=True)
    print("Integrating state-only reduced coordinates with dense output", flush=True)
    reduced = solve_ivp(
        lambda t, r: source_r @ rate_vector(runtime, runtime.reconstruct_anchored(r, x0)),
        (0.0, 1000.0), r0,
        jac=lambda t, r: source_r @ rate_jacobian(
            runtime, runtime.reconstruct_anchored(r, x0)) @ lift,
        **options)
    print(f"reduced success={reduced.success} nfev={reduced.nfev}: {reduced.message}", flush=True)
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "1.0",
        "status": "R1_DENSE_RATE_QUADRATURE_DIAGNOSTIC_NOT_ACCEPTANCE",
        "acceptance_eligible": False,
        "canonical_sbml_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "coordinate_certificate": runtime.certificate_name,
        "coordinate_certificate_sha256": hashlib.sha256(
            (OUT / runtime.certificate_name).read_bytes()).hexdigest(),
        "scipy_version": scipy.__version__,
        "state_solver": {"name": "BDF", "rtol": 1e-12, "atol": 1e-14},
        "quadrature": {"nodes_per_dense_step": 8, "rule": "Gauss-Legendre",
                       "extent_status": "rate_quadrature_not_model_side_direct_ODE"},
        "full_solver": {"success": bool(full.success), "message": full.message,
                        "nfev": full.nfev, "njev": full.njev, "nlu": full.nlu},
        "reduced_solver": {"success": bool(reduced.success), "message": reduced.message,
                           "nfev": reduced.nfev, "njev": reduced.njev, "nlu": reduced.nlu},
    }
    if not full.success or not reduced.success:
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 1

    full_extent, full_steps = integrate_dense_rates(runtime, full, lambda x: x, times, "full")
    reduced_extent, reduced_steps = integrate_dense_rates(
        runtime, reduced, lambda r: runtime.reconstruct_anchored(r, x0), times, "reduced")
    full_state = full.y.T
    reduced_state = np.array([runtime.reconstruct_anchored(row, x0)
                              for row in reduced.y.T])
    full_rates = np.array([rate_vector(runtime, row) for row in full_state])
    reduced_rates = np.array([rate_vector(runtime, row) for row in reduced_state])
    identifiers = [reaction["id"] for reaction in runtime.reactions]
    maxima = {
        "species": max(row["E_inf"] for row in metric_rows(
            runtime.species, full_state, reduced_state, x0, TRAJECTORY_LIMIT)),
        "rates": max(row["E_inf"] for row in metric_rows(
            identifiers, full_rates, reduced_rates, full_rates[0], RATE_LIMIT)),
        "rate_quadrature_extents": max(row["E_inf"] for row in metric_rows(
            identifiers, full_extent, reduced_extent, np.zeros(len(identifiers)), EXTENT_LIMIT)),
        "full_balance_absolute": float(np.max(np.abs(stable_material_balance(
            runtime, full_state, full_extent, x0)))),
        "reduced_balance_absolute": float(np.max(np.abs(stable_material_balance(
            runtime, reduced_state, reduced_extent, x0)))),
    }
    report.update({
        "dense_intervals": {"full": full_steps, "reduced": reduced_steps},
        "maxima": maxima,
        "physical_domain": {"full": negativity(full_state), "reduced": negativity(reduced_state)},
        "thresholds_for_context_only": {"species_E_inf": TRAJECTORY_LIMIT,
                                        "rates_E_inf": RATE_LIMIT,
                                        "direct_extent_E_inf": EXTENT_LIMIT,
                                        "balance_absolute": BALANCE_LIMIT,
                                        "negative_floor": NEGATIVE_DIAGNOSTIC_FLOOR},
        "trajectory_arrays": "trajectories.npz",
    })
    np.savez_compressed(out.parent / "trajectories.npz", times=times,
                        full_state=full_state, reduced_state=reduced_state,
                        full_extent_quadrature=full_extent,
                        reduced_extent_quadrature=reduced_extent)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(maxima, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
