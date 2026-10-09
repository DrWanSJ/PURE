"""Source-derived enzyme stationarity; no dynamical reduction comparison.

The explicit formulas are checked against the independently assembled generator.
They define a kinetic candidate, not an exact lumping or a validation decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def load_inventory(path=None):
    return json.loads(Path(path or ROOT / "results/energy_cycles_v1/source_inventory.json").read_text(encoding="utf-8"))


def reaction_id(number):
    return f"re{number:010d}"


def microscopic_parameters(inventory):
    return {r["id"]: r["k"] for r in inventory["reactions"]}


# Each entry is (A, B, C, D, EA, EB, EAB, EC, ED, ECD,
# first-order/bimolecular association IDs, catalytic forward/reverse IDs).
DIAMONDS = {
    "CK": ("ADP", "CP", "ATP", "Cr", "CK_ADP", "CK_CP", "CK_CP_ADP", "CK_ATP", "CK_Cr", "CK_Cr_ATP", 330, 332, 345, 347, 338, 339),
    "NDK": ("ATP", "GDP", "ADP", "GTP", "NDK_ATP", "NDK_GDP", "NDK_GDP_ATP", "NDK_ADP", "NDK_GTP", "NDK_GTP_ADP", 355, 357, 378, 377, 363, 364),
    "MK": ("ATP", "AMP", "ADP", "ADP", "MK_ATP", "MK_AMP", "MK_ATP_AMP", "MK_ADP_1", "MK_ADP_2", "MK_ADP_ADP", 380, 382, 395, 397, 388, 389),
}


def stationary_explicit(unit, free, enzyme_total, parameters):
    """Return ({source state: occupancy}, net catalytic current).

    Supports complex values for analytical complex-step differentiation. Source
    diamond dissociation constants must equal 1000, as checked by report().
    """
    name = unit if isinstance(unit, str) else unit["name"]
    k = lambda n: parameters[reaction_id(n)]
    if name in DIAMONDS:
        A, B, C, D, EA, EB, EAB, EC, ED, ECD, ia, ib, ic, id_, ikf, ikr = DIAMONDS[name]
        a, b, c, d = k(ia) * free[A], k(ib) * free[B], k(ic) * free[C], k(id_) * free[D]
        q = k(ia + 1)
        # ia is the association ID and the adjacent reaction its dissociation.
        left = 1 / (q + b) + 1 / (q + a)
        right = 1 / (q + d) + 1 / (q + c)
        alpha, beta = a * b * left, q * q * left
        gamma, delta = c * d * right, q * q * right
        kf, kr = k(ikf), k(ikr)
        det = beta * delta + beta * kr + delta * kf
        rAB = (alpha * (delta + kr) + kr * gamma) / det
        rCD = (gamma * (beta + kf) + kf * alpha) / det
        ratios = {name: 1, EA: (a + q * rAB) / (q + b), EB: (b + q * rAB) / (q + a), EAB: rAB,
                  EC: (c + q * rCD) / (q + d), ED: (d + q * rCD) / (q + c), ECD: rCD}
        E = enzyme_total / sum(ratios.values())
        h = {s: E * ratio for s, ratio in ratios.items()}
        v = E * (kf * alpha * delta - kr * gamma * beta) / det
        return h, v
    if name != "PPiase":
        raise KeyError(name)
    a, b, kf, kr = k(405) * free["PPi"], k(406), k(407), k(408)
    c, d, e, f = k(410) * free["PO4"], k(409), k(411), k(412) * free["PO4"]
    rP2 = (kf * a / (b + kf) + c * f / (e + c)) / (kr * b / (b + kf) + d * e / (e + c))
    rS = (a + kr * rP2) / (b + kf)
    rP = (d * rP2 + f) / (e + c)
    E = enzyme_total / (1 + rS + rP2 + rP)
    h = {"PPiase": E, "PPiase_PPi": E * rS, "PPiase_PO4_PO4": E * rP2, "PPiase_PO4": E * rP}
    v = E * (kf * a - kr * b * rP2) / (b + kf)
    return h, v


def composition_matrix(unit):
    return np.array([[unit["resource_composition"][state][resource] for state in unit["enzyme_states"]]
                     for resource in unit["boundary_species"]], dtype=float)


def total_map(unit, free_array, enzyme_total, parameters):
    free = dict(zip(unit["boundary_species"], free_array))
    h, v = stationary_explicit(unit, free, enzyme_total, parameters)
    hv = np.array([h[state] for state in unit["enzyme_states"]])
    return np.asarray(free_array) + composition_matrix(unit) @ hv, h, v


def generator(unit, free, inventory):
    """Build column-oriented Markov generator from actual kinetic species."""
    states = unit["enzyme_states"]
    si = {state: i for i, state in enumerate(states)}
    rows = {r["id"]: r for r in inventory["reactions"]}
    Q = np.zeros((len(states), len(states)), dtype=np.result_type(*free.values(), float))
    for rid in unit["active_reaction_ids"]:
        r = rows[rid]
        source = [s for s in r["reactants"] if s in si]
        target = [s for s in r["products"] if s in si]
        if len(source) != 1 or len(target) != 1 or r["reactants"][source[0]] != 1 or r["products"][target[0]] != 1:
            raise ValueError(f"Non-generator reaction {rid}")
        factors = list(r["kinetic_species"])
        if factors.count(source[0]) != 1:
            raise ValueError(f"Kinetic law not first order in source enzyme: {rid}")
        factors.remove(source[0])
        rate = r["k"]
        for s in factors:
            rate *= free[s]
        i, j = si[source[0]], si[target[0]]
        Q[j, i] += rate
        Q[i, i] -= rate
    return Q


def stationary_linear(unit, free, enzyme_total, inventory):
    Q = generator(unit, free, inventory)
    M = Q.copy()
    M[-1] = 1
    b = np.zeros(len(M), dtype=M.dtype)
    b[-1] = enzyme_total
    return np.linalg.solve(M, b), Q


def microscopic_rhs(unit, x, inventory):
    all_states = unit["boundary_species"] + unit["enzyme_states"]
    dx = {s: 0.0 for s in all_states}
    rows = {r["id"]: r for r in inventory["reactions"]}
    for rid in unit["active_reaction_ids"]:
        r = rows[rid]
        rate = r["k"]
        for s in r["kinetic_species"]:
            rate *= x[s]
        for s, n in r["reactants"].items():
            dx[s] -= n * rate
        for s, n in r["products"].items():
            dx[s] += n * rate
    return dx


def lumpability_counterexamples(unit, inventory):
    """Two same-coordinate microscopic states with unequal projected RHS."""
    resources, states = unit["boundary_species"], unit["enzyme_states"]
    first = {s: (10.0 if s in resources else 0.0) for s in resources + states}
    first[unit["free_enzyme"]] = 1
    source_state = "PPiase_PPi" if unit["name"] == "PPiase" else DIAMONDS[unit["name"]][6]
    # Free-coordinate pair preserves identical free resources and E_total.
    second_free = dict(first)
    second_free[unit["free_enzyme"]] = 0
    second_free[source_state] = 1
    d1 = microscopic_rhs(unit, first, inventory)
    d2f = microscopic_rhs(unit, second_free, inventory)
    # Total-coordinate pair moves exactly the source-inferred bound composition.
    second_total = dict(second_free)
    for resource in resources:
        second_total[resource] -= unit["resource_composition"][source_state][resource]
    d2t = microscopic_rhs(unit, second_total, inventory)
    C = composition_matrix(unit)
    total_rhs = lambda d: np.array([d[s] for s in resources]) + C @ np.array([d[s] for s in states])
    total_y = lambda x: np.array([x[s] for s in resources]) + C @ np.array([x[s] for s in states])
    return {
        "status": "NOT_EXACTLY_LUMPABLE_FOR_DECLARED_COORDINATES",
        "enzyme_total_both": 1.0, "occupied_source_state": source_state,
        "free_pair": {"state1": first, "state2": second_free, "free_y_equal": True,
                      "rhs1": {s: d1[s] for s in resources}, "rhs2": {s: d2f[s] for s in resources},
                      "max_projected_rhs_difference": float(max(abs(d1[s] - d2f[s]) for s in resources))},
        "total_pair": {"state1": first, "state2": second_total,
                       "total_y1": total_y(first).tolist(), "total_y2": total_y(second_total).tolist(),
                       "total_y_equal": bool(np.array_equal(total_y(first), total_y(second_total))),
                       "rhs1": total_rhs(d1).tolist(), "rhs2": total_rhs(d2t).tolist(),
                       "max_projected_rhs_difference": float(np.max(np.abs(total_rhs(d1) - total_rhs(d2t))))},
    }


def report(inventory):
    p = microscopic_parameters(inventory)
    units = []
    for unit in inventory["units"]:
        unit_report = {"unit": unit["name"], "lumpability": lumpability_counterexamples(unit, inventory), "fixed_free_stationarity": []}
        for label, free in [("author_initial_free", {s: inventory["initial"][s] for s in unit["boundary_species"]}),
                            ("algebraic_interior_probe_100_not_validation_scenario", {s: 100.0 for s in unit["boundary_species"]})]:
            h, v = stationary_explicit(unit, free, unit["enzyme_total_initial"], p)
            h_explicit = np.array([h[s] for s in unit["enzyme_states"]])
            h_linear, Q = stationary_linear(unit, free, unit["enzyme_total_initial"], inventory)
            eigenvalues = np.linalg.eigvals(Q)
            nonzero = eigenvalues[np.abs(eigenvalues) > 1e-7]
            unit_report["fixed_free_stationarity"].append({
                "label": label, "free": free, "occupancies": h, "net_catalytic_current": float(v),
                "max_explicit_vs_generator_error": float(np.max(np.abs(h_explicit-h_linear))),
                "generator_residual": float(np.max(np.abs(Q @ h_explicit))),
                "generator_column_sum_residual": float(np.max(np.abs(Q.sum(axis=0)))),
                "nonzero_eigenvalues_real": nonzero.real.tolist(), "nonzero_eigenvalues_imag": nonzero.imag.tolist(),
                "fixed_free_spectral_gap": float(-np.max(nonzero.real)),
                "fixed_free_relaxation_time": float(1 / -np.max(nonzero.real)),
                "interpretation": "Frozen-free generator only; not a full-network fast/slow separation certificate.",
            })
        units.append(unit_report)
    # The source equality supporting the diamond formula must be checked independently
    # of the constants in the formula, using all actual dissociation channels.
    rows = {r["id"]: r for r in inventory["reactions"]}
    bindings_verified = {}
    for unit in inventory["units"]:
        if unit["name"] not in DIAMONDS:
            continue
        diss = []
        for rid in unit["active_reaction_ids"]:
            r = rows[rid]
            if len(r["kinetic_species"]) == 1 and any(s in unit["boundary_species"] for s in r["products"]):
                diss.append((rid, r["k"]))
        bindings_verified[unit["name"]] = {"dissociation_parameters": diss, "equal_1000": all(k == 1000 for _, k in diss)}
        if not bindings_verified[unit["name"]]["equal_1000"]:
            raise ValueError("Explicit diamond formula outside source parameter assumptions")
    corner_obstructions = {
        "CK": {"positive_totals": ["CP", "ADP"], "zero_totals": ["Cr", "ATP"], "contradiction": "Zero product totals force CK_Cr_ATP=0; its stationary equation requires k338*CK_CP_ADP=0, but positive substrate totals force positive substrate free concentrations and CK_CP_ADP>0."},
        "NDK": {"positive_totals": ["ATP", "GDP"], "zero_totals": ["ADP", "GTP"], "contradiction": "Zero product totals force NDK_GTP_ADP=0; its stationary equation requires k363*NDK_GDP_ATP=0, but positive substrate totals force positive substrate free concentrations and NDK_GDP_ATP>0."},
        "MK": {"positive_totals": ["ATP", "AMP"], "zero_totals": ["ADP"], "contradiction": "Zero ADP total forces both MK_ADP site forms and MK_ADP_ADP=0; stationary product-complex balance requires k388*MK_ATP_AMP=0, contradicting positive ATP/AMP totals."},
        "PPiase": {"positive_totals": ["PPi"], "zero_totals": ["PO4"], "contradiction": "Zero PO4 total forces both phosphate-bound states zero; stationary double-phosphate balance requires k407*PPiase_PPi=0, contradicting positive PPi total."},
    }
    return {"status": "KINETIC_CANDIDATE_AND_ALGEBRAIC_CHECKS_ONLY", "source_commit": inventory["source_commit"],
            "source_hashes": inventory["source_hashes"], "environment": {"python": platform.python_version(), "numpy": np.__version__},
            "generator_tests": units, "diamond_dissociation_source_checks": bindings_verified,
            "total_closure_corner_domain_obstructions": corner_obstructions,
            "units_warning": inventory["units_warning"], "dynamical_reduction_validation_performed": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "results/energy_cycles_v1/kinetic_analysis.json")
    args = parser.parse_args()
    result = report(load_inventory(args.inventory))
    result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["command"] = "python scripts/energy_cycles/kinetics_analysis.py"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": result["status"]}))


if __name__ == "__main__":
    main()
