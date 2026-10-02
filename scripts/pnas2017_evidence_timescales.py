#!/usr/bin/env python3
"""Frozen PNAS2017 process-block diagnostics, never a reduction decision.

Only original mass-action reactions and the preregistered candidate lists enter
the Jacobian.  Its derivative is evaluated as a polynomial, without division
by a concentration; exact zeros and signed reference roundoff are preserved.
"""
from __future__ import annotations

import numpy as np
import sympy as sp


NA = "N/A_NO_INFORMATIVE_SAMPLES"
PRIMARY = "PRIMARY_AUTHOR_REFERENCE_GRID"


def _summary(values, prefix, reason=NA):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not values.size:
        return {prefix + suffix: reason for suffix in ("_min", "_median", "_max")}
    return {prefix + "_min": float(values.min()),
            prefix + "_median": float(np.quantile(values, .5, method="linear")),
            prefix + "_max": float(values.max())}


def _terms(species, reactants):
    index = {sid: j for j, sid in enumerate(species)}
    result = []
    for side in reactants:
        row = []
        for sid, coefficient in side.items():
            coefficient = float(coefficient)
            if not coefficient.is_integer() or coefficient <= 0:
                raise ValueError("Reference mass-action stoichiometry must be a positive integer")
            row.append((index[sid], int(coefficient)))
        result.append(row)
    return result


def mass_action_rates(x, k, terms):
    """Polynomial RHS ingredient used independently by central differences."""
    rates = np.asarray(k, dtype=float).copy()
    for r, row in enumerate(terms):
        for j, power in row:
            rates[r] *= x[j] ** power
    return rates


def analytic_jacobian(x, S, k, terms):
    """Full source RHS Jacobian, including reactions crossing card boundaries."""
    dv = np.zeros((len(k), len(x)), dtype=float)
    for r, row in enumerate(terms):
        for differentiated, power in row:
            derivative = float(k[r]) * power
            for j, exponent in row:
                derivative *= x[j] ** (exponent - (j == differentiated))
            dv[r, differentiated] = derivative
    return S @ dv


def _jacobian_crosscheck(x, times, S, k, terms, pre):
    # A nonzero-time interior reference state is more informative than the
    # repeated initial state.  Central perturbations may cross zero: they are
    # polynomial derivative probes, not new physical trajectories.
    ti = max(1, len(times) // 2)
    state = x[ti].copy()
    jac = analytic_jacobian(state, S, k, terms)
    finite_difference = np.empty_like(jac)
    step_definition = pre["numeric"]["jacobian_central_difference_step"]
    if step_definition != "1e-4*max(1,abs(x_j))":
        raise ValueError("Unexpected preregistered central difference step")
    for j in range(len(state)):
        h = 1e-4 * max(1.0, abs(float(state[j])))
        plus, minus = state.copy(), state.copy()
        plus[j] += h
        minus[j] -= h
        finite_difference[:, j] = (
            S @ mass_action_rates(plus, k, terms)
            - S @ mass_action_rates(minus, k, terms)
        ) / (2.0 * h)
    scaled = np.abs(jac - finite_difference) / np.maximum(
        1.0, np.maximum(np.abs(jac), np.abs(finite_difference)))
    worst = np.unravel_index(int(np.argmax(scaled)), scaled.shape)
    error = float(scaled[worst])
    tolerance = float(pre["numeric"]["jacobian_crosscheck_max_scaled_abs_error"])
    return {"status": "PASS" if error <= tolerance else "FAIL",
            "method": "independent central difference of full polynomial mass-action RHS",
            "scope": "all source reactions, all species rows and derivative columns",
            "reference_time": float(times[ti]), "reference_sample_index": ti,
            "sampling_role": PRIMARY, "point_count": 1,
            "step": step_definition, "maximum_scaled_absolute_error": error,
            "tolerance": tolerance, "worst_row_index": int(worst[0]),
            "worst_column_index": int(worst[1]),
            "analytic_value_at_worst": float(jac[worst]),
            "finite_difference_value_at_worst": float(finite_difference[worst]),
            "negative_perturbation_policy": "retained as polynomial derivative probes; no state clipping"}


def compute_timescales(pre, species, S, k, reactants, x, times, classes, prod, cons):
    """Return summary, full primary spectra, per-time ratios and Jacobian check.

    Inputs have the canonical species/reaction ordering.  Input row zero is
    supplemental exact t=0; rows 1..200 retain the primary stored time grid.
    The source reaction IDs are the canonical contiguous re0000000001..968.
    No solver is run, source parameter changed, or mode removed/reassigned.
    """
    S, k, x, times, prod, cons = (np.asarray(v, dtype=float)
                                for v in (S, k, x, times, prod, cons))
    ns, nr = len(species), len(k)
    expected_points = int(pre["sampling"]["primary_points"])
    if S.shape != (ns, nr) or len(reactants) != nr:
        raise ValueError("Canonical matrix/rate/reactant dimensions disagree")
    if x.shape != (expected_points + 1, ns) or prod.shape != x.shape or cons.shape != x.shape:
        raise ValueError("Expected supplemental t0 plus complete primary state/flux grid")
    if times.shape != (len(x),) or times[0] != 0 or not np.all(np.diff(times) > 0):
        raise ValueError("Reference sample times must increase from supplemental zero")
    if not all(np.isfinite(v).all() for v in (S, k, x, times, prod, cons)):
        raise ValueError("Nonfinite reference input")
    if len(set(species)) != ns:
        raise ValueError("Duplicate canonical species ID")
    terms = _terms(species, reactants)
    si = {sid: j for j, sid in enumerate(species)}
    ri = {f"re{j + 1:010d}": j for j in range(nr)}
    numeric = pre["numeric"]
    flux_floor = float(numeric["flux_information_floor"])
    concentration_floor = float(numeric["concentration_denominator_floor"])
    abs_floor = float(numeric["near_zero_eigenvalue_abs_floor"])
    rel_floor = float(numeric["near_zero_eigenvalue_relative_floor"])
    denominator = prod + cons
    jacobians = [analytic_jacobian(state, S, k, terms) for state in x[1:]]
    summaries, eigen_rows, time_rows = [], [], []
    for card in pre["process_cards"]:
        pid = card["process_id"]
        zids = card["candidate_state_ids"]
        if len(zids) != len(set(zids)):
            raise ValueError(f"Duplicate candidate state in {pid}")
        z = [si[sid] for sid in zids]
        zset = set(z)
        reaction_indices = [ri[rid] for rid in card["reaction_ids"]]
        # The union includes net-zero catalysts explicitly present as reactants.
        touched = {j for r in reaction_indices for j, _ in terms[r]}
        touched.update(int(j) for j in np.flatnonzero(np.any(S[:, reaction_indices] != 0, axis=1)))
        slow = [j for j in range(ns) if j in touched and j not in zset and classes[species[j]] == "I"]
        rdep = [r for r, row in enumerate(terms)
                if k[r] != 0 and any(j in zset for j, _ in row)]
        if z and rdep:
            exact = sp.Matrix([[sp.Rational(str(float(S[j, r]))) for r in rdep] for j in z])
            rank = int(exact.rank())
        else:
            rank = 0
        structural = len(z) - rank
        all_fast, all_slow, ratios, epsilons = [], [], [], []
        stable_counts, neutral_counts, nondecaying_counts = [], [], []
        valid_ratio_count = 0
        for ti, jac in enumerate(jacobians, start=1):
            if z:
                eig = np.linalg.eigvals(jac[np.ix_(z, z)])
                # Sorting is only deterministic presentation; indices do not
                # track a physical mode between different reference points.
                eig = sorted(eig, key=lambda v: (float(v.real), float(v.imag)))
                threshold = max(abs_floor, rel_floor * max(abs(v) for v in eig))
            else:
                eig, threshold = [], abs_floor
            fast, stable, neutral, nondecaying = [], 0, 0, 0
            for mode, value in enumerate(eig, start=1):
                if value.real < -threshold:
                    status = "STABLE_DECAY"
                    tau = 1.0 / -float(value.real)
                    stable += 1
                    fast.append(tau)
                elif abs(value) <= threshold:
                    status, tau = "NEAR_ZERO_NEUTRAL", "N/A_NEAR_ZERO_MODE"
                    neutral += 1
                else:
                    status, tau = "NONDECAYING_OR_UNRESOLVED_DECAY", "N/A_NONDECAYING_OR_UNRESOLVED_DECAY"
                    nondecaying += 1
                eigen_rows.append({"process_id": pid, "time": float(times[ti]),
                                   "sampling_role": PRIMARY, "mode_index": mode,
                                   "lambda_real": float(value.real), "lambda_imag": float(value.imag),
                                   "lambda_abs": float(abs(value)), "neutral_threshold": float(threshold),
                                   "mode_status": status, "relaxation_tau": tau})
            valid_slow = [j for j in slow if x[ti, j] > concentration_floor and denominator[ti, j] > flux_floor]
            slow_taus = [float(abs(x[ti, j]) / denominator[ti, j]) for j in valid_slow]
            if not z:
                reason = "N/A_NO_CANDIDATE_STATES"
            elif not fast:
                reason = "N/A_NO_STABLE_DECAY_MODES"
            elif not slow_taus:
                reason = "N/A_NO_INFORMATIVE_SLOW_INTERFACE"
            else:
                reason = "AVAILABLE_DIAGNOSTIC_PROXY_ONLY"
            if fast and slow_taus:
                ratio = float(np.median(slow_taus) / np.median(fast))
                epsilon = 1.0 / ratio
                ratios.append(ratio)
                epsilons.append(epsilon)
                valid_ratio_count += 1
            else:
                ratio = epsilon = reason
            time_rows.append({"process_id": pid, "time": float(times[ti]), "sampling_role": PRIMARY,
                              "stable_mode_count": stable, "near_zero_mode_count": neutral,
                              "nondecaying_mode_count": nondecaying,
                              "structural_neutral_mode_count": structural,
                              "neutral_threshold": float(threshold),
                              **_summary(fast, "tau_fast", "N/A_NO_CANDIDATE_STATES" if not z else "N/A_NO_STABLE_DECAY_MODES"),
                              "slow_informative_state_count": len(valid_slow),
                              "slow_informative_state_ids": ";".join(species[j] for j in valid_slow),
                              **_summary(slow_taus, "tau_slow", "N/A_NO_INFORMATIVE_SLOW_INTERFACE"),
                              "R_tau": ratio, "epsilon_tau": epsilon,
                              "metric_status": reason, "timescale_status": "NEED_MORE_INFORMATION"})
            all_fast.extend(fast)
            all_slow.extend(slow_taus)
            stable_counts.append(stable)
            neutral_counts.append(neutral)
            nondecaying_counts.append(nondecaying)
        fast_range = f"{min(stable_counts)}..{max(stable_counts)}"
        reason = "N/A_NO_CANDIDATE_STATES" if not z else NA
        summaries.append({"process_id": pid, "process_name": card["name"],
                          "reaction_ids": ";".join(card["reaction_ids"]),
                          "candidate_state_ids": ";".join(zids), "candidate_state_count": len(z),
                          "primary_sample_count": expected_points,
                          "trajectory_points": expected_points,
                          "nonzero_fast_mode_count": stable_counts[0] if min(stable_counts) == max(stable_counts) else fast_range,
                          "stable_mode_count_min": min(stable_counts), "stable_mode_count_max": max(stable_counts),
                          "near_zero_mode_count_min": min(neutral_counts), "near_zero_mode_count_max": max(neutral_counts),
                          "nondecaying_mode_count_min": min(nondecaying_counts), "nondecaying_mode_count_max": max(nondecaying_counts),
                          "structural_neutral_mode_count": structural,
                          "structural_rank": rank, "structural_dependency_reaction_count": len(rdep),
                          **_summary(all_fast, "tau_fast", reason),
                          "tau_fast_summary_basis": "all stable eigenmodes at 200 unweighted primary reference points",
                          "tau_slow_basis": "Class-I reaction-interface states outside candidate list; turnover abs(x)/(production+consumption); per-time median for R_tau",
                          "slow_interface_state_ids": ";".join(species[j] for j in slow),
                          **_summary(all_slow, "tau_slow", "N/A_NO_INFORMATIVE_SLOW_INTERFACE"),
                          "tau_slow_summary_basis": "all informative positive interface-state turnover samples at primary points",
                          **_summary(ratios, "R_tau", reason), **_summary(epsilons, "epsilon_tau", reason),
                          "ratio_informative_fraction": valid_ratio_count / expected_points,
                          "metric_status": "AVAILABLE_DIAGNOSTIC_PROXY_ONLY" if ratios else reason,
                          "timescale_status": "NEED_MORE_INFORMATION",
                          "assumptions": "Full-source local Jzz; frozen exact card coordinates; enabled mass-action dependencies for exact rational structural rank; neutral threshold max(abs_floor,rel_floor*max(abs(lambda)))",
                          "limitations": "Local coordinate-dependent block; candidate slow turnover proxies not certified coordinates; near-zero and nondecaying or unresolved-decay modes never inverted; structural count is a lower bound; eigen index does not track modes; no closure or initial-layer test; author reference condition only"})
    return {"process_timescale_evidence": summaries,
            "process_eigenvalue_timeseries": eigen_rows,
            "process_timescale_timeseries": time_rows,
            "numerical_crosscheck": {"jacobian_crosscheck": _jacobian_crosscheck(x, times, S, k, terms, pre)}}
