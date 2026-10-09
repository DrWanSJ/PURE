"""Recompute numerical evidence from trajectories using independent XML parsing.

No runtime.py/source.py/kinetics_analysis.py imports. The independently parsed
canonical chemistry, not saved mappings or reported metrics, defines ledgers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import sympy as sy
from scipy.linalg import null_space

from independent_tests import (ROOT, SemanticFailure, active_reactions, certificate,
                               enzyme_states, form_composition, net, read_sources,
                               require, serializable)


def rms(time, values):
    # Trapezoidal quadrature is frozen by the numerical protocol.
    return float(np.sqrt(np.trapz(np.square(values), time) / (time[-1] - time[0])))


def source_rates(module, species, trajectory, reaction_order):
    index = {name: i for i, name in enumerate(species)}
    by_id = module["reactions"]
    rates = []
    for rid in reaction_order:
        reaction = by_id[rid]
        expression = sy.expand(reaction["law"] / sy.Symbol("k1"))
        powers = expression.as_powers_dict()
        rate = np.full(len(trajectory), float(reaction["k"]))
        for symbol, exponent in powers.items():
            require(symbol.is_Symbol and exponent.is_Integer and exponent >= 0, "NUMERIC_SOURCE_MONOMIAL", rid)
            rate *= trajectory[:, index[str(symbol)]] ** int(exponent)
        rates.append(rate)
    return np.column_stack(rates)


def verify_one(path, modules, registration):
    metrics = json.loads(path.read_text(encoding="utf-8"))
    trajectory_path = ROOT / metrics["trajectory"]["path"]
    require(hashlib.sha256(trajectory_path.read_bytes()).hexdigest() == metrics["trajectory"]["sha256"], "NUMERICAL_TRAJECTORY_HASH", str(path))
    case = metrics["initial_conditions"]
    frozen_case = next(x for x in registration["scenarios"] if x["id"] == case["id"])
    require(case == frozen_case, "NUMERICAL_FROZEN_INITIAL_SCENARIO", case["id"])
    require(metrics["initial_mode"] in frozen_case["initial_modes"], "NUMERICAL_FROZEN_INITIAL_MODE", case["id"])
    require([x["window"] for x in metrics["windows"]] == registration["windows"], "NUMERICAL_ALL_TRANSIENT_WINDOWS", case["id"])
    module = modules[case["unit"]]
    with np.load(trajectory_path, allow_pickle=False) as data:
        time = data["time"]
        species = list(data["species"])
        reaction_order = list(data["reaction_ids"])
        active = active_reactions(module)
        require(set(reaction_order) == {r["id"] for r in active}, "NUMERICAL_ACTIVE_SOURCE_CHANNELS", case["id"])
        require(set(species) == set(module["species"]), "NUMERICAL_SPECIES_COVERAGE", case["id"])
        require(np.array_equal(time, registration["comparison_grid"]) and time[0] == 0 and time[-1] == 1000, "NUMERICAL_FROZEN_GRID", case["id"])
        expected_boundary, composition = form_composition(module)
        states = enzyme_states(module)
        boundary = species[:len(expected_boundary)]
        require(set(boundary) == set(expected_boundary), "NUMERICAL_RETAINED_ORDER", case["id"])
        index = {name: i for i, name in enumerate(species)}
        state_columns = [index[s] for s in states]
        C = np.array([[float(composition[s][r]) for s in states] for r in boundary])
        A = np.zeros((len(boundary), len(species)))
        for i, resource in enumerate(boundary):
            A[i, index[resource]] = 1
            for j, state in enumerate(states):
                A[i, index[state]] = C[i, j]
        require(np.array_equal(A, data["total_mapping"]), "NUMERICAL_TOTAL_MAPPING_SOURCE", case["id"])
        # Saved bound mapping columns follow the saved enzyme order.
        saved_state_order = species[len(boundary):len(boundary) + len(states)]
        saved_C = np.array([[float(composition[s][r]) for s in saved_state_order] for r in boundary])
        require(np.array_equal(saved_C, data["bound_mapping"]), "NUMERICAL_BOUND_MAPPING_SOURCE", case["id"])
        proof, pools = certificate(module)
        N = np.array([float(proof["oriented_net"][r]) for r in boundary])
        require(np.array_equal(N, data["net_stoichiometry"]), "NUMERICAL_NET_DIRECTION_SOURCE", case["id"])
        S = np.column_stack([np.array(net(module["reactions"][r], species), dtype=float) for r in reaction_order])
        projected_S = A @ S
        forward = [j for j in range(len(reaction_order)) if np.array_equal(projected_S[:, j], N)]
        reverse = [j for j in range(len(reaction_order)) if np.array_equal(projected_S[:, j], -N)]
        require(len(forward) == 1 and len(reverse) <= 1, "NUMERICAL_CATALYTIC_CURRENT_SOURCE", case["id"])
        require(all(np.array_equal(projected_S[:, j], N) or np.array_equal(projected_S[:, j], -N) or np.all(projected_S[:, j] == 0) for j in range(len(reaction_order))), "NUMERICAL_HIDDEN_BOUNDARY_TRANSFER", case["id"])
        arrays = {key: data[key] for key in ["microscopic", "microscopic_tight", "microscopic_independent_bdf", "reduced", "reduced_tight"]}
        source_initial = np.array([case["initial_original"][s] for s in species])
        initial_micro = arrays["microscopic"][0, :len(species)]
        if metrics["initial_mode"] == "ORIGINAL_NONEQUILIBRIUM":
            require(np.array_equal(initial_micro, source_initial), "NUMERICAL_ORIGINAL_INITIAL_CONDITION", case["id"])
        else:
            require(np.max(np.abs(A @ (initial_micro - source_initial))) <= 1e-8, "NUMERICAL_PROJECTED_RESOURCE_TOTALS", case["id"])
            require(abs(initial_micro[state_columns].sum() - case["enzyme_total"]) <= 1e-8, "NUMERICAL_PROJECTED_CATALYST_TOTAL", case["id"])
        observations = {}
        max_ledger = 0.0
        for label, trajectory in arrays.items():
            x = trajectory[:, :len(species)]
            flux = source_rates(module, species, x, reaction_order)
            current_f = flux[:, forward[0]]
            current_r = flux[:, reverse[0]] if reverse else np.zeros(len(time))
            extent = trajectory[:, -2] - trajectory[:, -1]
            require(trajectory[0, -2] == trajectory[0, -1] == 0, "NUMERICAL_CUMULATIVE_FROM_ZERO", label)
            totals = x @ A.T
            residual = np.max(np.abs(totals - totals[0] - extent[:, None] * N))
            max_ledger = max(max_ledger, float(residual))
            require(residual <= 1e-6, "NUMERICAL_EXACT_RESOURCE_EXTENT_LEDGER", {"case": case["id"], "array": label, "residual": float(residual)})
            observations[label] = {"free": x[:, [index[s] for s in boundary]], "retained": totals,
                                   "bound": x[:, state_columns] @ C.T, "occupancy": x[:, state_columns],
                                   "net_flux": current_f - current_r, "extent": extent, "source_flux": flux}
        for label, stored in [("microscopic", "microscopic_active_flux"), ("reduced", "reconstructed_active_flux")]:
            error = float(np.max(np.abs(observations[label]["source_flux"] - data[stored])))
            require(error <= 1e-9 * max(1, np.max(np.abs(data[stored]))), "NUMERICAL_STORED_FLUX_CANONICAL", {"array": label, "error": error})
        scales = np.array([case["concentration_scales"][r] for r in boundary])
        bound_scales = np.array([case["bound_scales"][r] for r in boundary])
        E = case["enzyme_total"]
        original, reduced = observations["microscopic"], observations["reduced"]
        long_window = time >= 1
        # Capacity uses both microscopic author constants, including the exact
        # zero reverse parameter. Catalytic channels found by composition.
        all_module_reactions = module["reactions"].values()
        capacity_k = sum(float(r["k"]) for r in all_module_reactions if np.any(A @ np.asarray(net(r, species), dtype=float)))
        flux_scale = max(rms(time[long_window], original["net_flux"][long_window]), .01 * E * capacity_k, 1e-12)
        require(abs(flux_scale - metrics["flux_scale"]) <= 1e-10 * max(1, flux_scale), "NUMERICAL_FLUX_SCALE", case["id"])
        results = []
        numeric_residual = 0.0
        for reported in metrics["windows"]:
            lo, hi = reported["window"]
            window = (time >= lo) & (time <= hi)
            t = time[window]
            result = {
                "max_scaled_free": float(np.max(np.abs(original["free"][window] - reduced["free"][window]) / scales)),
                "max_scaled_retained": float(np.max(np.abs(original["retained"][window] - reduced["retained"][window]) / scales)),
                "max_scaled_bound": float(np.max(np.abs(original["bound"][window] - reduced["bound"][window]) / bound_scales)),
                "max_scaled_occupancy": float(np.max(np.abs(original["occupancy"][window] - reduced["occupancy"][window])) / E),
                "normalized_net_flux_rms": rms(t, (original["net_flux"] - reduced["net_flux"])[window]) / flux_scale,
                "max_normalized_cumulative_resource_flow": float(np.max(np.abs(original["extent"][window] - reduced["extent"][window]))) / case["cumulative_extent_scale"],
            }
            uncertainty = {"concentration": 0.0, "flux": 0.0, "flow": 0.0}
            for changed, base in [("microscopic_tight", "microscopic"), ("microscopic_independent_bdf", "microscopic"), ("reduced_tight", "reduced")]:
                one, zero = observations[changed], observations[base]
                uncertainty["concentration"] = max(uncertainty["concentration"], float(np.max(np.abs(one["free"][window] - zero["free"][window]) / scales)), float(np.max(np.abs(one["retained"][window] - zero["retained"][window]) / scales)))
                uncertainty["flux"] = max(uncertainty["flux"], rms(t, (one["net_flux"] - zero["net_flux"])[window]) / flux_scale)
                uncertainty["flow"] = max(uncertainty["flow"], float(np.max(np.abs(one["extent"][window] - zero["extent"][window]))) / case["cumulative_extent_scale"])
            for key, value in result.items():
                residual = abs(value - reported[key])
                numeric_residual = max(numeric_residual, residual)
                require(residual <= 1e-9 * max(1, abs(value)), "NUMERICAL_RECOMPUTED_METRIC", {"case": case["id"], "metric": key, "reported": reported[key], "independent": value})
            for key, value in uncertainty.items():
                require(abs(value - reported["uncertainty"][key]) <= 1e-9 * max(1, abs(value)), "NUMERICAL_RECOMPUTED_UNCERTAINTY", {"case": case["id"], "metric": key})
            result.update(window=reported["window"], uncertainty=uncertainty)
            results.append(result)
        # These conserved pools were independently proved exact from source
        # chemistry, and differ from the runtime's orthonormal nullspace basis.
        moiety_residuals = {}
        for name, weights in pools.items():
            q = np.array([float(weights[s]) for s in species])
            worst = 0.0
            for trajectory in arrays.values():
                inventory = trajectory[:, :len(species)] @ q
                worst = max(worst, float(np.max(np.abs(inventory - inventory[0])) / max(abs(inventory[0]), 1)))
            require(worst <= 1e-8, "NUMERICAL_SOURCE_MOIETY_CONSERVATION", {"case": case["id"], "pool": name, "residual": worst})
            moiety_residuals[name] = worst
        invariant = np.vstack([null_space(N.reshape(1, -1)).T @ A,
                               np.array([1.0 if s in states else 0.0 for s in species])])
        invariant_initial = invariant @ arrays["microscopic"][0, :len(species)]
        invariant_scale = np.maximum(np.abs(invariant_initial), 1)
        conservation = max(float(np.max(np.abs(arrays[label][:, :len(species)] @ invariant.T - invariant_initial) / invariant_scale)) for label in ["microscopic", "reduced"])
        require(abs(conservation - metrics["normalized_conservation_residual"]) <= 1e-10, "NUMERICAL_RECOMPUTED_REPORTED_CONSERVATION", case["id"])
        minimum = float(min(np.min(a[:, :len(species)]) for a in arrays.values()))
        require(minimum == metrics["minimum_unclipped_inventory"], "NUMERICAL_RECOMPUTED_MINIMUM_INVENTORY", case["id"])
        latest = results[-1]
        errors = {"concentration": max(latest["max_scaled_free"], latest["max_scaled_retained"]), "flux": latest["normalized_net_flux_rms"], "flow": latest["max_normalized_cumulative_resource_flow"]}
        gates = registration["gates"]
        thresholds = {"concentration": gates["long_concentration"], "flux": gates["long_flux_rms"], "flow": gates["cumulative_resource_flow"]}
        uncertainties = latest["uncertainty"]
        failures = [k for k, v in errors.items() if v - uncertainties[k] > thresholds[k]]
        inconclusive = [k for k, v in errors.items() if uncertainties[k] > .1 * thresholds[k] or (v + uncertainties[k] > thresholds[k] and k not in failures)]
        if conservation > gates["normalized_conservation"]:
            failures.append("conservation")
        if minimum < -gates["negative_inventory_allowance"]:
            failures.append("negative_inventory")
        status = "FAILED" if failures else "NUMERICALLY_INCONCLUSIVE" if inconclusive else "SCENARIO_GATES_PASS"
        require(status == metrics["scientific_status"] and failures == metrics["failed_gates"] and inconclusive == metrics["uncertain_gates"], "NUMERICAL_FROZEN_SCIENTIFIC_GATE_CLASSIFICATION", {"case": case["id"], "recomputed": status, "reported": metrics["scientific_status"]})
        # Source enzyme equations must be stationary at every reconstructed point.
        stationary_residual = 0.0
        for label in ["reduced", "reduced_tight"]:
            dx = observations[label]["source_flux"] @ S.T
            stationary_residual = max(stationary_residual, float(np.max(np.abs(dx[:, state_columns]))))
        require(stationary_residual <= 1e-6 * max(E, 1), "NUMERICAL_RECONSTRUCTED_STATIONARITY", case["id"])
        return {"case": case["id"], "initial_mode": metrics["initial_mode"], "reported_scientific_status": metrics["scientific_status"],
                "status": "INDEPENDENT_NUMERICAL_RECOMPUTATION_PASS", "trajectory_sha256": metrics["trajectory"]["sha256"],
                "maximum_source_resource_extent_identity_residual": max_ledger,
                "maximum_reported_metric_difference": numeric_residual,
                "source_moiety_normalized_conservation_residuals": moiety_residuals,
                "independently_recomputed_scientific_status": status,
                "independently_recomputed_failed_gates": failures,
                "endpoint_net_conversion_extents_from_t0": {label: float(observations[label]["extent"][-1]) for label in ["microscopic", "reduced"]},
                "initial_net_catalytic_currents_from_canonical_laws": {label: float(observations[label]["net_flux"][0]) for label in ["microscopic", "reduced"]},
                "maximum_reconstructed_source_stationarity_residual": stationary_residual, "recomputed_windows": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "results/energy_cycles_v1/numerical_verification.json")
    parser.add_argument("--registration", type=Path, default=ROOT / "docs/reduction/energy_cycles/validation_preregistration.json")
    parser.add_argument("--numerical-dir", type=Path, default=ROOT / "results/energy_cycles_v1/numerical")
    args = parser.parse_args()
    registration_path = args.registration.resolve()
    registration = json.loads(registration_path.read_text(encoding="utf-8"))
    source, initial, parameters, index, modules = read_sources()
    paths = sorted(args.numerical_dir.resolve().glob("*/*/metrics.json"))
    require(bool(paths), "NUMERICAL_EVIDENCE_AVAILABLE", "No completed trajectory metrics exist")
    checks = []
    failures = []
    for path in paths:
        try:
            checks.append(verify_one(path, modules, registration))
        except Exception as error:
            failures.append({"path": path.relative_to(ROOT).as_posix(), "error_type": type(error).__name__, "error": str(error)})
    report = {"status": "INDEPENDENT_NUMERICAL_RECOMPUTATION_PASS" if not failures else "INDEPENDENT_NUMERICAL_RECOMPUTATION_FAILED", "completed_trajectory_pairs_checked": len(paths), "checks": checks, "failures": failures,
              "preregistration_sha256": hashlib.sha256(registration_path.read_bytes()).hexdigest(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "authority": "Canonical XML MathML independently parsed by independent_tests.py; author parameters parsed from immutable ZIP; form-specific composition re-derived from exact binding stoichiometry.",
              "scope": "Independent metric/uncertainty/source-ledger/stationary-RHS verification of emitted trajectories; no scientific promotion and no full-PNAS candidate embedding claim."}
    report.update(source_commit=registration["source_commit"], source_hashes=registration["source_hashes"],
                  environment={"python": sys.version, "numpy": np.__version__, "sympy": sy.__version__, "platform": platform.platform()},
                  command=[sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                  independent_parser_sha256=hashlib.sha256((ROOT / "scripts/energy_cycles/independent_tests.py").read_bytes()).hexdigest())
    args.output.write_text(json.dumps(serializable(report), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "trajectory_pairs": len(paths), "failures": len(failures)}))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
