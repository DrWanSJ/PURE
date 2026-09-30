#!/usr/bin/env python3
"""Run one registered full-coupled R3 condition with directed extent ODEs."""
from __future__ import annotations

import argparse
import csv
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

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from validate_source_coordinates_full_v1 import rate_jacobian, rate_vector, stable_material_balance
from verify_reduction_audit_v0 import OUT, ROOT

GRID = OUT / "r3_validation_grid_v1.csv"
METHOD = OUT / "r3_aminoacylation_qssa_method.md"
PROTOCOL = OUT / "r3_coupled_validation_protocol_v1.md"
MAP = OUT / "r3_source_reaction_candidate_map_v1.csv"
AA_REACTIONS = ROOT / "models/pnas2017_full_reference/audit/aminoacylation_reactions.csv"
RTOL = 1e-10
ATOL = 1e-14


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def score_rows(names, full, reduced, floor, subset=None):
    scale = np.maximum(np.max(np.abs(full), axis=0), floor)
    difference = np.abs(full - reduced)
    errors = np.max(difference, axis=0) / scale
    if subset is None:
        subset = np.ones(len(full), dtype=bool)
    post_errors = np.max(difference[subset], axis=0) / scale
    return [{"id": name, "reference_scale": float(scale[j]),
             "max_abs_error": float(np.max(difference[:, j])),
             "E_inf": float(errors[j]), "post_0p05_E_inf": float(post_errors[j])}
            for j, name in enumerate(names)]


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def integrate_extents(dense_state, rates_at_state, times):
    """Integrate 968 triangular gross-extent ODEs on each reporting interval."""
    total = np.zeros(968)
    compensation = np.zeros(968)
    values = np.zeros((len(times), 968))
    counters = {"segments": 0, "nfev": 0, "max_segment_abs": 0.}
    for k, (left, right) in enumerate(zip(times[:-1], times[1:]), start=1):
        solved = solve_ivp(lambda t, _e: rates_at_state(t, dense_state(t)),
                           (float(left), float(right)), np.zeros(968),
                           method="DOP853", rtol=RTOL, atol=ATOL, t_eval=[right])
        counters["segments"] += 1
        counters["nfev"] += solved.nfev
        if not solved.success:
            raise RuntimeError(f"Extent segment {k}: {solved.message}")
        increment = solved.y[:, -1]
        counters["max_segment_abs"] = max(counters["max_segment_abs"],
                                           float(np.max(np.abs(increment))))
        corrected = increment - compensation
        newer = total + corrected
        compensation = (newer - total) - corrected
        total = newer
        values[k] = total
    return values, counters


def stable_slow_balance(runtime, slow, extents, initial):
    ts = np.asarray(runtime.T @ runtime.S)
    rows = [[(j, float(value)) for j, value in enumerate(row) if value]
            for row in ts]
    result = np.empty_like(slow)
    for k in range(len(slow)):
        for i, row in enumerate(rows):
            change = math.fsum(value * extents[k, j] for j, value in row)
            result[k, i] = math.fsum((slow[k, i], -initial[i], -change))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--diagnostic-end", type=float)
    args = parser.parse_args()
    conditions = {row["condition_id"]: row for row in csv.DictReader(
        GRID.open(encoding="utf-8", newline=""))}
    if args.condition not in conditions:
        parser.error(f"Unknown condition {args.condition}")
    end = 1000. if args.diagnostic_end is None else args.diagnostic_end
    if not 1e-4 < end <= 1000:
        parser.error("End must be in (1e-4,1000]")
    output = args.out.resolve()
    if output.exists():
        parser.error(f"Refusing to overwrite {output}")
    output.mkdir(parents=True)
    condition = conditions[args.condition]
    r = R3ResourceTotalRuntimeV2()
    source = r.source
    scales = json.loads(condition["initial_scale_json"])
    x0 = np.array([float(source.author_initial[name]) * scales.get(name, 1.)
                   for name in source.species])
    assert np.min(x0) >= 0
    z0 = r.initial_slow(x0)
    times = np.r_[0., np.geomspace(1e-4, end, 200)]
    result = {
        "schema_version": "1.0", "status": "RUNNING",
        "run_kind": "EXPLORATORY_DIAGNOSTIC" if args.diagnostic_end is not None else "REGISTERED_R3_GRID_CONDITION",
        "condition_id": args.condition, "condition_role": condition["role"],
        "initial_scale_json": condition["initial_scale_json"],
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
        "python_executable": sys.executable, "python_version": platform.python_version(),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "solver": {"state": "BDF", "extent": "segmented DOP853 ODE states",
                   "rtol": RTOL, "atol": ATOL, "start": 0., "end": end,
                   "report_points": len(times)},
        "inputs_sha256": {
            "canonical_sbml": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
            "grid": sha(GRID), "method": sha(METHOD), "protocol": sha(PROTOCOL),
            "reaction_map": sha(MAP), "aminoacylation_reactions": sha(AA_REACTIONS),
            "runtime_v1": sha(ROOT / "scripts/r3_resource_total_runtime_v1.py"),
            "runtime_v2": sha(ROOT / "scripts/r3_resource_total_runtime_v2.py"),
            "runner": sha(Path(__file__)),
        },
    }
    closure = {"calls": 0, "max_residual": 0., "min_q": float("inf"),
               "min_carrier": float("inf"), "min_resource": float("inf"),
               "max_Gq_condition_number": 0., "fallbacks": 0}

    def checked_root(t, z):
        root = r.solve_fast(z, x0)
        closure["calls"] += 1
        closure["max_residual"] = max(closure["max_residual"], root["residual_max"])
        closure["min_q"] = min(closure["min_q"], root["min_q"])
        closure["min_carrier"] = min(closure["min_carrier"], root["min_carrier"])
        closure["min_resource"] = min(closure["min_resource"], root["min_resource"])
        closure["max_Gq_condition_number"] = max(
            closure["max_Gq_condition_number"], root["Gq_condition_number"])
        closure["fallbacks"] += root.get("method") == "hybr_fallback"
        if not root["valid_local_root"]:
            result["root_failure"] = {"time": float(t), "residual_max": root["residual_max"],
                                      "min_q": root["min_q"],
                                      "min_carrier": root["min_carrier"],
                                      "min_resource": root["min_resource"],
                                      "method": root.get("method"), "message": root["message"]}
            raise RuntimeError(f"Physical closure failed at t={t}: {result['root_failure']}")
        return root

    def full_rhs(_t, x):
        return np.asarray(source.full_rhs_from_rates(rate_vector(source, x)))

    def full_jac(_t, x):
        return r.S @ rate_jacobian(source, x)

    def reduced_rhs(t, z):
        q = checked_root(t, z)["q"]
        return r.slow_rhs(z, q, x0)[0]

    def reduced_jac(t, z):
        q = checked_root(t, z)["q"]
        return r.slow_jacobian(z, q, x0)[0]

    try:
        print(f"{args.condition}: full source 0-{end} s", flush=True)
        full = solve_ivp(full_rhs, (0., end), x0, method="BDF", jac=full_jac,
                         t_eval=times, dense_output=True, rtol=RTOL, atol=ATOL)
        result["full_solver"] = {key: getattr(full, key) for key in
                                 ("success", "message", "nfev", "njev", "nlu")}
        if not full.success:
            raise RuntimeError(full.message)
        np.savez_compressed(output / "full_state.npz", times=times, state=full.y.T)
        print(f"{args.condition}: reduced QSSA 0-{end} s", flush=True)
        reduced = solve_ivp(reduced_rhs, (0., end), z0, method="BDF", jac=reduced_jac,
                            t_eval=times, dense_output=True, rtol=RTOL, atol=ATOL)
        result["reduced_solver"] = {key: getattr(reduced, key) for key in
                                    ("success", "message", "nfev", "njev", "nlu")}
        if not reduced.success:
            raise RuntimeError(reduced.message)
        xfull = full.y.T
        zred = reduced.y.T
        xred = np.array([checked_root(t, z)["state"] for t, z in zip(times, zred)])
        np.savez_compressed(output / "state_trajectories.npz", times=times,
                            full_state=xfull, reduced_state=xred, reduced_slow=zred)
        print(f"{args.condition}: 968 directed extent ODEs for each trajectory", flush=True)
        full_extent, full_extent_stats = integrate_extents(
            full.sol, lambda _t, x: rate_vector(source, x), times)
        reduced_extent, reduced_extent_stats = integrate_extents(
            reduced.sol, lambda t, z: rate_vector(source, checked_root(t, z)["state"]), times)
        result["full_extent_solver"] = full_extent_stats
        result["reduced_extent_solver"] = reduced_extent_stats
        full_rates = np.array([rate_vector(source, x) for x in xfull])
        reduced_rates = np.array([rate_vector(source, x) for x in xred])
        np.savez_compressed(output / "directed_ledgers.npz", times=times,
                            full_extent=full_extent, reduced_extent=reduced_extent,
                            full_rates=full_rates, reduced_rates=reduced_rates)
        post = times >= 0.05
        species_rows = score_rows(source.species, xfull, xred, 1e-6, post)
        reaction_ids = [reaction["id"] for reaction in source.reactions]
        rate_rows = score_rows(reaction_ids, full_rates, reduced_rates, 1e-9, post)
        extent_rows = score_rows(reaction_ids, full_extent, reduced_extent, 1e-6, post)
        with MAP.open(encoding="utf-8", newline="") as stream:
            mapping = {row["reaction_id"]: row for row in csv.DictReader(stream)}
        with AA_REACTIONS.open(encoding="utf-8", newline="") as stream:
            aminoacylation_ids = {row["reaction_id"] for row in csv.DictReader(stream)}
        assert set(mapping) == set(reaction_ids)
        for rows in (rate_rows, extent_rows):
            for row in rows:
                row["fast_touch"] = mapping[row["id"]]["fast_balance_role"] == "FAST_AND_SLOW_STOICHIOMETRIC_CONTRIBUTOR"
                row["aminoacylation_subsystem"] = row["id"] in aminoacylation_ids
        for name, rows in (("species_errors.csv", species_rows),
                           ("directed_rate_errors.csv", rate_rows),
                           ("directed_extent_errors.csv", extent_rows)):
            write_csv(output / name, rows)
        full_balance = stable_material_balance(source, xfull, full_extent, x0)
        slow_balance = stable_slow_balance(r, zred, reduced_extent, z0)
        initial_laws = [sum(float(v) * x0[i] for i, v in law.items()) for law in source.laws]
        law_drift = max(abs(sum(float(v) * x[i] for i, v in law.items()) - target)
                        for x in xred for law, target in zip(source.laws, initial_laws))
        details = (OUT / "species_information_contract_detailed.md").read_text(encoding="utf-8")
        class_i = re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*I\*\*", details, re.M)
        assert len(class_i) == 42
        class_i_set = set(class_i)
        maxima = {
            "all_species_E_inf": max(row["E_inf"] for row in species_rows),
            "class_I_E_inf": max(row["E_inf"] for row in species_rows if row["id"] in class_i_set),
            "aminoacylation_rate_E_inf": max(row["E_inf"] for row in rate_rows if row["aminoacylation_subsystem"]),
            "aminoacylation_extent_E_inf": max(row["E_inf"] for row in extent_rows if row["aminoacylation_subsystem"]),
            "all_directed_rate_E_inf": max(row["E_inf"] for row in rate_rows),
            "all_directed_extent_E_inf": max(row["E_inf"] for row in extent_rows),
            "full_material_balance_abs": float(np.max(np.abs(full_balance))),
            "reduced_slow_balance_abs": float(np.max(np.abs(slow_balance))),
            "source_general_inventory_drift_abs": float(law_drift),
            "minimum_full_concentration": float(np.min(xfull)),
            "minimum_reduced_concentration": float(np.min(xred)),
        }
        result["maxima"] = maxima
        result["limits"] = {"closure": 1e-10, "balance": 1e-8,
                            "state": 0.01, "process_rate": 0.05,
                            "cumulative_resource_extent": 0.01}
        result["condition_pass"] = bool(
            closure["max_residual"] <= 1e-10 and
            maxima["all_species_E_inf"] <= 0.01 and
            maxima["aminoacylation_rate_E_inf"] <= 0.05 and
            maxima["aminoacylation_extent_E_inf"] <= 0.01 and
            maxima["full_material_balance_abs"] <= 1e-8 and
            maxima["reduced_slow_balance_abs"] <= 1e-8 and
            maxima["source_general_inventory_drift_abs"] <= 1e-8)
        result["status"] = "GRID_CONDITION_EVALUATED"
    except Exception as exc:
        result["status"] = "GRID_CONDITION_INCOMPLETE"
        result["failure"] = str(exc)
        (output / "traceback.log").write_text(traceback.format_exc(), encoding="utf-8", newline="\n")
    result["closure_counters"] = closure
    result["outputs_sha256"] = {path.name: sha(path) for path in sorted(output.iterdir())
                                if path.name != "result.json" and path.is_file()}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n",
                                         encoding="utf-8", newline="\n")
    print(json.dumps({"status": result["status"], "condition_id": args.condition,
                      "failure": result.get("failure"), "maxima": result.get("maxima"),
                      "full_solver": result.get("full_solver"),
                      "reduced_solver": result.get("reduced_solver"),
                      "closure": closure}, indent=2), flush=True)
    return 0 if result["status"] == "GRID_CONDITION_EVALUATED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
