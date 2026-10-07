#!/usr/bin/env python3
"""Full coupled 241-vs-214 exact-coordinate test with directed extent ODEs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.sparse import block_diag, csc_matrix, eye, hstack, vstack

from runtime_reconstruction_rhs import SourceCoordinateRuntime
from verify_reduction_audit_v0 import OUT, RESOURCE, SOURCE, reverse_pairs


ROOT = Path(__file__).resolve().parents[1]
SOLVER_PROFILES = {
    "v1": ("source_coordinate_method_v1.md", 1e-10, 1e-12, "direct"),
    "v1r2": ("source_coordinate_method_v1r2.md", 1e-12, 1e-14, "direct"),
    "v1r3": ("source_coordinate_method_v1r3.md", 1e-12, 1e-14, "reverse_net"),
    "v2": ("source_coordinate_method_v2.md", 1e-12, 1e-14, "direct"),
    "v3": ("source_coordinate_method_v3.md", 1e-12, 1e-14, "direct"),
    "v4": ("source_coordinate_method_v4.md", 1e-12, 1e-14, "direct"),
    "v4r2": ("source_coordinate_method_v4r2.md", 1e-12, 1e-14, "direct"),
    "v4r3": ("source_coordinate_method_v4r3.md", 2.5e-13, 2.5e-15, "stable_direct"),
    "v5": ("source_coordinate_method_v5.md", 1e-12, 1e-14, "direct"),
    "v6": ("source_coordinate_method_ck_variants.md", 1e-12, 1e-14, "direct"),
    "v7": ("source_coordinate_method_ck_variants.md", 1e-12, 1e-14, "direct"),
}
TRAJECTORY_LIMIT = RATE_LIMIT = EXTENT_LIMIT = 1e-6
BALANCE_LIMIT = 1e-8
NEGATIVE_DIAGNOSTIC_FLOOR = -1e-11


def source_matrix(runtime):
    row, col, data = [], [], []
    for j, reaction_col in enumerate(runtime.stoich):
        for i, coefficient in reaction_col.items():
            row.append(i)
            col.append(j)
            data.append(float(coefficient))
    return csc_matrix((data, (row, col)), shape=(len(runtime.species), len(runtime.reactions)))


def lift_matrix(runtime):
    row, col, data = [], [], []
    for j, i in enumerate(runtime.r_index):
        row.append(i)
        col.append(j)
        data.append(1.0)
    retained_position = {i: j for j, i in enumerate(runtime.r_index)}
    for i, weights in zip(runtime.e_index, runtime.B):
        for retained_i, coefficient in weights.items():
            row.append(i)
            col.append(retained_position[retained_i])
            data.append(float(coefficient))
    return csc_matrix((data, (row, col)), shape=(len(runtime.species), len(runtime.retained)))


def reverse_channel_view(runtime):
    """Exact net RHS columns; all original directed rates remain separate."""
    pair_ids = reverse_pairs(runtime.reactions, runtime.stoich)
    index = {reaction["id"]: j for j, reaction in enumerate(runtime.reactions)}
    first_to_second = {index[first]: index[second] for first, second in pair_ids}
    reverse_indices = set(first_to_second.values())
    assert all(first < second for first, second in first_to_second.items())
    channel_rows, channel_cols, channel_data = [], [], []
    transform_rows, transform_cols, transform_data = [], [], []
    channels = []
    for j, col in enumerate(runtime.stoich):
        if j in reverse_indices:
            continue
        second = first_to_second.get(j)
        if second is not None:
            assert col == {i: -value for i, value in runtime.stoich[second].items()}
        channel = len(channels)
        channels.append((j, second))
        transform_rows.append(channel)
        transform_cols.append(j)
        transform_data.append(1.0)
        if second is not None:
            transform_rows.append(channel)
            transform_cols.append(second)
            transform_data.append(-1.0)
        for i, value in col.items():
            channel_rows.append(i)
            channel_cols.append(channel)
            channel_data.append(float(value))
    assert len(channels) == len(runtime.reactions) - len(pair_ids) == 678
    net_stoich = csc_matrix((channel_data, (channel_rows, channel_cols)),
                            shape=(len(runtime.species), len(channels)))
    transform = csc_matrix((transform_data, (transform_rows, transform_cols)),
                           shape=(len(channels), len(runtime.reactions)))
    assert (net_stoich @ transform - source_matrix(runtime)).nnz == 0
    row_terms = [[] for _ in runtime.species]
    for channel, (j, _) in enumerate(channels):
        for i, value in runtime.stoich[j].items():
            row_terms[i].append((channel, float(value)))

    def net_rhs(rates):
        net_rates = [rates[j] if second is None else rates[j] - rates[second]
                     for j, second in channels]
        return np.array([math.fsum(value * net_rates[channel] for channel, value in row)
                         for row in row_terms])

    return net_stoich, transform, net_rhs


def rate_vector(runtime, state):
    rates = np.empty(len(runtime.reactions))
    for j, (parameter, factors) in enumerate(runtime.rate_specs):
        value = parameter
        for i in factors:
            value *= state[i]
        rates[j] = value
    return rates


def rate_jacobian(runtime, state):
    row, col, data = [], [], []
    for j, (parameter, factors) in enumerate(runtime.rate_specs):
        if parameter == 0:
            continue
        derivatives = {}
        for position, i in enumerate(factors):
            value = parameter
            for other_position, other_i in enumerate(factors):
                if other_position != position:
                    value *= state[other_i]
            derivatives[i] = derivatives.get(i, 0.0) + value
        for i, value in derivatives.items():
            if value:
                row.append(j)
                col.append(i)
                data.append(value)
    return csc_matrix((data, (row, col)), shape=(len(runtime.reactions), len(runtime.species)))


def augmented_jacobian(top, bottom, extent_count):
    zero_top = csc_matrix((top.shape[0], extent_count))
    zero_bottom = csc_matrix((extent_count, extent_count))
    return vstack((hstack((top, zero_top)), hstack((bottom, zero_bottom)))).tocsc()


def metric_rows(names, full, reduced, initial, threshold):
    rows = []
    for j, name in enumerate(names):
        scale = 1.0 if initial[j] == 0 else max(float(np.max(np.abs(full[:, j]))), 1e-12)
        maximum = float(np.max(np.abs(full[:, j] - reduced[:, j])))
        rows.append({"id": name, "max_absolute_error": maximum, "y_scale": scale,
                     "E_inf": maximum / max(scale, 1e-12), "threshold": threshold})
    return rows


def write_table(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def negativity(values):
    minimum = float(np.min(values))
    return {"minimum": minimum,
            "negative_count": int(np.count_nonzero(values < 0)),
            "numerical_negative_count": int(np.count_nonzero((values < 0) & (values >= NEGATIVE_DIAGNOSTIC_FLOOR))),
            "domain_failure_count": int(np.count_nonzero(values < NEGATIVE_DIAGNOSTIC_FLOOR))}


def stable_material_balance(runtime, states, extents, initial):
    """Use stable directed-extent summation, including large opposing gross flows."""
    result = np.empty_like(states)
    for k in range(len(states)):
        for i, row in enumerate(runtime.source_rows):
            source_change = math.fsum(coefficient * extents[k, j] for j, coefficient in row)
            result[k, i] = math.fsum((states[k, i], -initial[i], -source_change))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--diagnostic-end", type=float)
    parser.add_argument("--diagnostic-solver", choices=("BDF", "Radau"))
    parser.add_argument("--diagnostic-rhs", choices=("direct", "stable_direct", "reverse_net"))
    parser.add_argument("--diagnostic-joint", action="store_true")
    parser.add_argument("--diagnostic-split-extents", action="store_true")
    parser.add_argument("--diagnostic-extent-scale", type=float)
    parser.add_argument("--diagnostic-net-extent-basis", action="store_true")
    parser.add_argument("--diagnostic-rtol", type=float)
    parser.add_argument("--diagnostic-atol", type=float)
    parser.add_argument("--method", choices=SOLVER_PROFILES, default="v1")
    parser.add_argument("--chart", choices=("v1", "v2", "v3", "v4", "v5", "v6", "v7"), default="v1")
    args = parser.parse_args()
    method_file, rtol, atol, rhs_evaluation = SOLVER_PROFILES[args.method]
    if args.chart in ("v2", "v3", "v4", "v5", "v6", "v7"):
        assert args.method == args.chart or (args.chart == "v4" and args.method in ("v4r2", "v4r3")), "alternative chart requires its matching method"
    else:
        assert args.method not in ("v2", "v3", "v4", "v4r2", "v4r3", "v5", "v6", "v7"), "v1 method required for v1 chart"
    diagnostic = args.diagnostic_end is not None
    if args.diagnostic_rtol is not None or args.diagnostic_atol is not None:
        assert diagnostic, "tolerance changes require a diagnostic run before a new method is registered"
        assert args.diagnostic_rtol is not None and args.diagnostic_atol is not None
        assert math.isfinite(args.diagnostic_rtol) and 0 < args.diagnostic_rtol < 1
        assert math.isfinite(args.diagnostic_atol) and args.diagnostic_atol > 0
        rtol, atol = args.diagnostic_rtol, args.diagnostic_atol
    if args.diagnostic_solver is not None:
        assert diagnostic, "solver changes require a diagnostic run before a new method is registered"
    if args.diagnostic_rhs is not None:
        assert diagnostic, "RHS changes require a diagnostic run before a new method is registered"
        rhs_evaluation = args.diagnostic_rhs
    if args.diagnostic_joint:
        assert diagnostic, "joint stepping must be registered as a new method before a decisive run"
    if args.diagnostic_split_extents:
        assert diagnostic, "split extent integration must be registered before a decisive run"
        assert not args.diagnostic_joint, "split and joint diagnostic modes are distinct"
    if args.diagnostic_extent_scale is not None:
        assert diagnostic, "extent scaling must be registered before a decisive run"
        assert math.isfinite(args.diagnostic_extent_scale) and args.diagnostic_extent_scale > 0
        assert not args.diagnostic_split_extents, "split extents use a separate integration method"
    if args.diagnostic_net_extent_basis:
        assert diagnostic, "net extent basis must be registered before a decisive run"
        assert not args.diagnostic_split_extents, "split extents use a separate integration method"
        assert args.diagnostic_extent_scale is None, "test extent basis separately from scaling"
    net_extent_basis = args.diagnostic_net_extent_basis or args.method == "v4r3"
    extent_scale = args.diagnostic_extent_scale or 1.0
    solver_name = args.diagnostic_solver or ("Radau" if args.method == "v4r2" else "BDF")
    end = args.diagnostic_end if diagnostic else 1000.0
    assert 1e-4 < end <= 1000
    times = np.r_[0.0, np.geomspace(1e-4, end, 200)]
    certificate_name = f"source_coordinate_certificate_{args.chart}.json"
    runtime = SourceCoordinateRuntime(certificate_name)
    reaction_index = {reaction["id"]: j for j, reaction in enumerate(runtime.reactions)}
    reverse_extent_pairs = [(reaction_index[first], reaction_index[second])
                            for first, second in reverse_pairs(runtime.reactions, runtime.stoich)]
    assert len(reverse_extent_pairs) == 290
    if net_extent_basis:
        # For each reverse pair, replace its first gross extent by its exact
        # net extent. The second gross extent and every unpaired gross extent
        # remain separate ODE states. This is an invertible 968-state basis.
        assert all(runtime.stoich[first] == {i: -value for i, value in runtime.stoich[second].items()}
                   for first, second in reverse_extent_pairs)
        extent_basis = (eye(len(runtime.reactions), format="csc") +
                        csc_matrix(([-1.0] * len(reverse_extent_pairs),
                                    ([first for first, _ in reverse_extent_pairs],
                                     [second for _, second in reverse_extent_pairs])),
                                   shape=(len(runtime.reactions), len(runtime.reactions))))
    else:
        extent_basis = None
    source = source_matrix(runtime)
    source_R = source[runtime.r_index, :].tocsc()
    if rhs_evaluation == "reverse_net":
        net_source, net_transform, net_rhs = reverse_channel_view(runtime)
        net_source_R = net_source[runtime.r_index, :].tocsc()
    lift = lift_matrix(runtime)
    x0_exact = [runtime.author_initial[name] for name in runtime.species]
    _b = runtime.b_for_initial(x0_exact)
    x0 = np.array([float(value) for value in x0_exact])
    r0 = x0[runtime.r_index]
    assert np.array_equal(np.asarray(runtime.reconstruct_anchored(r0, x0)), x0)
    assert len(_b) == 27
    zeros = np.zeros(len(runtime.reactions))

    def extent_rhs(rates):
        return (extent_basis @ rates if extent_basis is not None else rates) / extent_scale

    def extent_jacobian(dv):
        return (extent_basis @ dv if extent_basis is not None else dv) / extent_scale

    def full_rhs(_t, y):
        rates = rate_vector(runtime, y[:len(runtime.species)])
        state_rhs = (net_rhs(rates) if rhs_evaluation == "reverse_net" else
                     np.array(runtime.full_rhs_from_rates(rates)) if rhs_evaluation == "stable_direct" else
                     source @ rates)
        return np.r_[state_rhs, extent_rhs(rates)]

    def full_jac(_t, y):
        dv = rate_jacobian(runtime, y[:len(runtime.species)])
        top = net_source @ (net_transform @ dv) if rhs_evaluation == "reverse_net" else source @ dv
        return augmented_jacobian(top, extent_jacobian(dv), len(runtime.reactions))

    def reduced_rhs(_t, y):
        state = runtime.reconstruct_anchored(y[:len(runtime.retained)], x0)
        rates = rate_vector(runtime, state)
        state_rhs = (net_rhs(rates)[runtime.r_index] if rhs_evaluation == "reverse_net" else
                     np.array(runtime.full_rhs_from_rates(rates))[runtime.r_index]
                     if rhs_evaluation == "stable_direct" else source_R @ rates)
        return np.r_[state_rhs, extent_rhs(rates)]

    def reduced_jac(_t, y):
        state = runtime.reconstruct_anchored(y[:len(runtime.retained)], x0)
        dv = rate_jacobian(runtime, state) @ lift
        top = net_source_R @ (net_transform @ dv) if rhs_evaluation == "reverse_net" else source_R @ dv
        return augmented_jacobian(top, extent_jacobian(dv), len(runtime.reactions))

    options = {"method": solver_name, "t_eval": times, "rtol": rtol, "atol": atol}
    full_initial = np.r_[x0, zeros]
    reduced_initial = np.r_[r0, zeros]
    if args.diagnostic_split_extents:
        # The extent equations are triangular: x' = S v(x), xi' = v(x).
        # Integrate xi directly on each predeclared reporting interval against
        # the state solver's dense trajectory, retaining all directed channels.
        # Segment-local zero starts and compensated accumulation limit roundoff
        # from the ~2e7 opposing CK gross extents. This is diagnostic only.
        state_options = {**options, "dense_output": True}
        print("Integrating full and reduced states with dense BDF output", flush=True)
        full_state_solution = solve_ivp(lambda t, y: full_rhs(t, y)[:len(x0)],
                                        (0.0, end), x0,
                                        jac=lambda t, y: full_jac(t, y)[:len(x0), :len(x0)],
                                        **state_options)
        reduced_state_solution = solve_ivp(lambda t, y: reduced_rhs(t, y)[:len(r0)],
                                           (0.0, end), r0,
                                           jac=lambda t, y: reduced_jac(t, y)[:len(r0), :len(r0)],
                                           **state_options)
        if full_state_solution.success and reduced_state_solution.success:
            def integrate_direct_extents(state_solution, reconstruct, label):
                extents = np.zeros((len(times), len(zeros)))
                cumulative = np.zeros(len(zeros))
                compensation = np.zeros(len(zeros))
                for k, (start, stop) in enumerate(zip(times[:-1], times[1:]), 1):
                    segment = solve_ivp(
                        lambda t, xi: rate_vector(runtime, reconstruct(state_solution.sol(t))),
                        (float(start), float(stop)), zeros, method="DOP853",
                        rtol=3e-14, atol=1e-13)
                    if not segment.success:
                        raise RuntimeError(f"{label} extent segment {k}: {segment.message}")
                    increment = segment.y[:, -1] - compensation
                    updated = cumulative + increment
                    compensation = (updated - cumulative) - increment
                    cumulative = updated
                    extents[k] = cumulative
                    if k % 50 == 0:
                        print(f"{label} direct extent segments {k}/{len(times) - 1}", flush=True)
                return extents

            full_direct = integrate_direct_extents(full_state_solution, lambda x: x, "full")
            reduced_direct = integrate_direct_extents(
                reduced_state_solution, lambda r: runtime.reconstruct_anchored(r, x0), "reduced")
            full = SimpleNamespace(y=np.vstack((full_state_solution.y, full_direct.T)),
                                   **{key: getattr(full_state_solution, key)
                                      for key in ("success", "message", "nfev", "njev", "nlu")})
            reduced = SimpleNamespace(y=np.vstack((reduced_state_solution.y, reduced_direct.T)),
                                      **{key: getattr(reduced_state_solution, key)
                                         for key in ("success", "message", "nfev", "njev", "nlu")})
        else:
            full, reduced = full_state_solution, reduced_state_solution
    elif args.diagnostic_joint:
        split = len(full_initial)

        def joint_rhs(t, y):
            return np.r_[full_rhs(t, y[:split]), reduced_rhs(t, y[split:])]

        def joint_jac(t, y):
            return block_diag((full_jac(t, y[:split]), reduced_jac(t, y[split:])), format="csc")

        print("Integrating full and reduced blocks on shared adaptive steps", flush=True)
        joint = solve_ivp(joint_rhs, (0.0, end), np.r_[full_initial, reduced_initial],
                          jac=joint_jac, **options)
        common = {key: getattr(joint, key) for key in ("success", "message", "nfev", "njev", "nlu")}
        full = SimpleNamespace(y=joint.y[:split], **common)
        reduced = SimpleNamespace(y=joint.y[split:], **common)
    else:
        print("Integrating full 241-state source with 968 direct extents", flush=True)
        full = solve_ivp(full_rhs, (0.0, end), full_initial, jac=full_jac, **options)
        print(f"Full success={full.success}, nfev={full.nfev}, njev={full.njev}: {full.message}", flush=True)
        print("Integrating 214 source-general coordinates with 968 direct extents", flush=True)
        reduced = solve_ivp(reduced_rhs, (0.0, end), reduced_initial, jac=reduced_jac, **options)
        print(f"Reduced success={reduced.success}, nfev={reduced.nfev}, njev={reduced.njev}: {reduced.message}", flush=True)
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema_version": "1.0",
        "status": "R1_FULL_COUPLED_DIAGNOSTIC" if diagnostic else "R1_FULL_COUPLED_DECISIVE",
        "canonical_sbml_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "method_file": method_file,
        "method_sha256": hashlib.sha256((OUT / method_file).read_bytes()).hexdigest(),
        "coordinate_certificate_file": certificate_name,
        "coordinate_certificate_sha256": hashlib.sha256((OUT / certificate_name).read_bytes()).hexdigest(),
        "scipy_version": scipy.__version__,
        "solver": {"name": f"SciPy {solver_name}", "rtol": rtol, "atol": atol, "start": 0.0, "end": end,
                   "rhs_evaluation": rhs_evaluation,
                   "direct_extent_rtol": 3e-14 if args.diagnostic_split_extents else rtol,
                   "extent_state_scale": extent_scale,
                   "extent_state_definition": ("first_pair_state=forward_gross-reverse_gross; "
                                               "second_pair_state=reverse_gross; unpaired_state=gross"
                                               if net_extent_basis else
                                               "zeta=directed_gross_extent/extent_state_scale"),
                   "reverse_pair_net_extent_basis": net_extent_basis,
                   "reverse_pair_basis_count": len(reverse_extent_pairs) if net_extent_basis else 0,
                   "split_direct_extent_ode": args.diagnostic_split_extents,
                   "split_extent_solver": "DOP853" if args.diagnostic_split_extents else None,
                   "split_extent_rtol": 3e-14 if args.diagnostic_split_extents else None,
                   "split_extent_atol": 1e-13 if args.diagnostic_split_extents else None,
                   "joint_adaptive_steps": args.diagnostic_joint,
                   "grid_points": len(times), "direct_integrated_extent_states": len(zeros)},
        "full_solver": {"success": bool(full.success), "message": full.message, "nfev": full.nfev,
                        "njev": full.njev, "nlu": full.nlu},
        "reduced_solver": {"success": bool(reduced.success), "message": reduced.message, "nfev": reduced.nfev,
                           "njev": reduced.njev, "nlu": reduced.nlu},
    }
    if not full.success or not reduced.success or full.y.shape[1] != len(times) or reduced.y.shape[1] != len(times):
        result["pass"] = False
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return 1
    full_state = full.y[:len(runtime.species)].T
    full_extent_basis = full.y[len(runtime.species):].T * extent_scale
    reduced_state = np.array([runtime.reconstruct_anchored(row, x0)
                              for row in reduced.y[:len(runtime.retained)].T])
    reduced_extent_basis = reduced.y[len(runtime.retained):].T * extent_scale
    full_extent = full_extent_basis.copy()
    reduced_extent = reduced_extent_basis.copy()
    if net_extent_basis:
        for first, second in reverse_extent_pairs:
            full_extent[:, first] += full_extent_basis[:, second]
            reduced_extent[:, first] += reduced_extent_basis[:, second]
    full_rates = np.array([rate_vector(runtime, row) for row in full_state])
    reduced_rates = np.array([rate_vector(runtime, row) for row in reduced_state])
    class_table = (OUT / "species_information_contract_detailed.md").read_text(encoding="utf-8")
    classes = dict(re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*(I|II-A|II-B|III|C)\*\*\s*\|", class_table, re.M))
    assert len(classes) == 241 and sum(value == "I" for value in classes.values()) == 42
    assert sum(value == "C" for value in classes.values()) == 29
    species_rows = metric_rows(runtime.species, full_state, reduced_state, x0, TRAJECTORY_LIMIT)
    reaction_ids = [reaction["id"] for reaction in runtime.reactions]
    rate_rows = metric_rows(reaction_ids, full_rates, reduced_rates, full_rates[0], RATE_LIMIT)
    extent_rows = metric_rows(reaction_ids, full_extent, reduced_extent, np.zeros(len(reaction_ids)), EXTENT_LIMIT)
    for label, rows in (("species_errors.csv", species_rows), ("rate_errors.csv", rate_rows),
                        ("direct_extent_errors.csv", extent_rows)):
        write_table(out.parent / label, rows)
    full_balance = stable_material_balance(runtime, full_state, full_extent, x0)
    reduced_balance = stable_material_balance(runtime, reduced_state, reduced_extent, x0)
    if net_extent_basis:
        # Exact S_f=-S_r makes S*xi equal to S_f*net for each pair. Report
        # this separately; the unchanged gross-ledger balance gate remains.
        reverse_indices = {second for _, second in reverse_extent_pairs}

        def net_basis_balance(states, extents):
            residual = np.empty_like(states)
            for k in range(len(states)):
                for i, row in enumerate(runtime.source_rows):
                    change = math.fsum(coefficient * extents[k, j]
                                       for j, coefficient in row if j not in reverse_indices)
                    residual[k, i] = math.fsum((states[k, i], -x0[i], -change))
            return residual

        result["net_basis_balance_diagnostic"] = {
            "full_absolute": float(np.max(np.abs(net_basis_balance(full_state, full_extent_basis)))),
            "reduced_absolute": float(np.max(np.abs(net_basis_balance(reduced_state, reduced_extent_basis)))),
        }
    b_float = np.array([float(value) for value in _b])
    law_rows = [{i: float(value) for i, value in law.items()} for law in runtime.laws]
    law_matrix = csc_matrix((
        [value for row in law_rows for value in row.values()],
        ([j for j, row in enumerate(law_rows) for _ in row], [i for row in law_rows for i in row])),
        shape=(len(law_rows), len(runtime.species)))
    full_law_error = float(np.max(np.abs((law_matrix @ full_state.T).T - b_float)))
    reduced_law_error = float(np.max(np.abs((law_matrix @ reduced_state.T).T - b_float)))
    maxima = {"species": max(row["E_inf"] for row in species_rows),
              "rates": max(row["E_inf"] for row in rate_rows),
              "direct_extents": max(row["E_inf"] for row in extent_rows),
              "class_I": max(row["E_inf"] for row in species_rows if classes[row["id"]] == "I"),
              "class_C": max(row["E_inf"] for row in species_rows if classes[row["id"]] == "C"),
              "resources": max(row["E_inf"] for row in species_rows if row["id"] in RESOURCE),
              "full_balance_absolute": float(np.max(np.abs(full_balance))),
              "reduced_balance_absolute": float(np.max(np.abs(reduced_balance))),
              "full_law_absolute": full_law_error, "reduced_law_absolute": reduced_law_error}
    domain = {"full": negativity(full_state), "reduced": negativity(reduced_state),
              "retained": negativity(reduced_state[:, runtime.r_index]),
              "reconstructed": negativity(reduced_state[:, runtime.e_index])}
    result.update({"maxima": maxima, "physical_domain": domain,
                   "error_tables": ["species_errors.csv", "rate_errors.csv", "direct_extent_errors.csv"],
                   "trajectory_arrays": "trajectories.npz",
                   "thresholds": {"species_E_inf": TRAJECTORY_LIMIT, "rates_E_inf": RATE_LIMIT,
                                  "direct_extents_E_inf": EXTENT_LIMIT, "material_balance_absolute": BALANCE_LIMIT,
                                  "negative_domain_failure_floor": NEGATIVE_DIAGNOSTIC_FLOOR}})
    result["pass"] = all((maxima["species"] <= TRAJECTORY_LIMIT,
                          maxima["rates"] <= RATE_LIMIT,
                          maxima["direct_extents"] <= EXTENT_LIMIT,
                          maxima["full_balance_absolute"] <= BALANCE_LIMIT,
                          maxima["reduced_balance_absolute"] <= BALANCE_LIMIT,
                          all(item["domain_failure_count"] == 0 for item in domain.values())))
    np.savez_compressed(out.parent / "trajectories.npz", times=times, full_state=full_state,
                        reduced_state=reduced_state, full_extent=full_extent,
                        reduced_extent=reduced_extent, full_rates=full_rates, reduced_rates=reduced_rates)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": result["pass"], "maxima": maxima, "physical_domain": domain}, indent=2), flush=True)
    return 0 if diagnostic or result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
