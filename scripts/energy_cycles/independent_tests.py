"""Independent exact source checks and semantic adversarial energy-cycle controls.

This intentionally imports neither source.py nor the candidate runtime. Source
expectations come from independently parsed immutable XML and author ZIP CSVs.
Mutations take place only in memory and enter chemical/provenance predicates;
none is rejected merely because a byte hash changed.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy
import sympy as sy
from scipy.integrate import solve_ivp
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[2]
SB = "{http://www.sbml.org/sbml/level2/version4}"
MM = "{http://www.w3.org/1998/Math/MathML}"
CD = "{http://www.sbml.org/2001/ns/celldesigner}"
ORIGINAL = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
NORMALIZED = ROOT / "models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml"
AUTHOR_ZIP = ROOT / "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
SUBSYSTEM_ZIP = ROOT / "references/PNAS2017_Matsuura/raw/SBML_files.zip"
INDEX = ROOT / "docs/reduction/reaction_index.csv"
ANNOTATION = ROOT / "docs/reduction/reaction_level_annotation_v2.csv"
UNITS = {"CK": "A", "NDK": "B", "MK": "C", "PPiase": "D"}
FREE_GROUPS = {
    "adenylate": {"ATP": 1, "ADP": 1, "AMP": 1},
    "guanylate": {"GTP": 1, "GDP": 1},
    "creatine": {"CP": 1, "Cr": 1},
    "represented_phosphate_groups": {"ATP": 3, "ADP": 2, "AMP": 1, "GTP": 3, "GDP": 2, "CP": 1, "PPi": 2, "PO4": 1},
}


class SemanticFailure(ValueError):
    def __init__(self, gate, detail):
        self.gate = gate
        self.detail = detail
        super().__init__(f"{gate}: {detail}")


def require(condition, gate, detail):
    if not condition:
        raise SemanticFailure(gate, detail)


def tag(element):
    return element.tag.split("}")[-1]


def mathml(element):
    """Evaluate literal stoichiometry and translate kinetic MathML independently."""
    kind = tag(element)
    if kind == "math":
        require(len(element) == 1, "MATHML_SHAPE", kind)
        return mathml(element[0])
    if kind == "cn":
        if element.get("type") == "rational":
            parts = [element.text, element[0].tail]
            return sy.Rational(int(parts[0]), int(parts[1]))
        return sy.Rational((element.text or "").strip())
    if kind == "ci":
        return sy.Symbol((element.text or "").strip())
    require(kind == "apply" and len(element) > 1, "MATHML_UNSUPPORTED", kind)
    operator = tag(element[0])
    args = [mathml(x) for x in element[1:]]
    if operator == "times":
        return sy.Mul(*args)
    if operator == "plus":
        return sy.Add(*args)
    if operator == "minus":
        return -args[0] if len(args) == 1 else args[0] - args[1]
    if operator == "divide":
        return args[0] / args[1]
    if operator == "power":
        return args[0] ** args[1]
    raise SemanticFailure("MATHML_UNSUPPORTED", operator)


def side(reaction, name):
    result = defaultdict(Fraction)
    for ref in reaction.findall(SB + name + "/" + SB + "speciesReference"):
        literal = ref.find(SB + "stoichiometryMath/" + MM + "math")
        value = mathml(literal) if literal is not None else sy.Rational(ref.get("stoichiometry", "1"))
        require(bool(value.is_Rational) and value > 0, "EXACT_STOICHIOMETRY", str(value))
        result[ref.get("species")] += Fraction(int(sy.numer(value)), int(sy.denom(value)))
    return dict(result)


def parse_xml(data):
    model = ET.fromstring(data).find(SB + "model")
    require(model is not None, "SBML_MODEL", "no model")
    species = {x.get("id"): x.attrib for x in model.findall(SB + "listOfSpecies/" + SB + "species")}
    reactions = {}
    for element in model.findall(SB + "listOfReactions/" + SB + "reaction"):
        rid = element.get("id")
        require(rid not in reactions, "DUPLICATE_REACTION", rid)
        law = element.find(SB + "kineticLaw/" + MM + "math")
        reactions[rid] = {"id": rid, "r": side(element, "listOfReactants"), "p": side(element, "listOfProducts"), "law": mathml(law) if law is not None else None}
    # Membership is evidence of which resources occupy each complex; exact
    # repeated-copy multiplicities are independently inferred from binding laws.
    included = defaultdict(Counter)
    for element in model.findall(SB + "annotation/" + CD + "extension/" + CD + "listOfIncludedSpecies/" + CD + "species"):
        owner = element.find(CD + "annotation/" + CD + "complexSpecies")
        if owner is not None:
            included[owner.text][element.get("name")] += 1
    return {"id": model.get("id"), "species": species, "reactions": reactions, "included_members": dict(included)}


def signature(reaction):
    return tuple(sorted(reaction["r"].items())), tuple(sorted(reaction["p"].items()))


def net(reaction, species):
    return [sy.Rational(reaction["p"].get(x, 0) - reaction["r"].get(x, 0)) for x in species]


def archive_csv(archive, basename):
    matches = [x for x in archive.namelist() if x.endswith("/" + basename)]
    require(len(matches) == 1, "AUTHOR_ARCHIVE_MEMBER", basename)
    return list(csv.DictReader(io.StringIO(archive.read(matches[0]).decode("utf-8-sig"))))


def read_sources():
    source = parse_xml(ORIGINAL.read_bytes())
    normalized = parse_xml(NORMALIZED.read_bytes())
    require(source["species"] == normalized["species"], "COMPATIBILITY_SPECIES", "metadata differs")
    require(set(source["reactions"]) == set(normalized["reactions"]), "COMPATIBILITY_COVERAGE", "IDs differ")
    for rid, reaction in source["reactions"].items():
        other = normalized["reactions"][rid]
        require(signature(reaction) == signature(other), "COMPATIBILITY_STOICHIOMETRY", rid)
        require(sy.simplify(reaction["law"] - other["law"]) == 0, "COMPATIBILITY_KINETICS", rid)
    with zipfile.ZipFile(AUTHOR_ZIP) as archive:
        initial_rows = archive_csv(archive, "fMGG_synthesis_initial_values.csv")
        parameter_rows = archive_csv(archive, "fMGG_synthesis_parameters.csv")
    initial = {row["Name"]: Fraction(row["Value"]) for row in initial_rows}
    parameters = {row["Name"][:-3]: Fraction(row["Value"]) for row in parameter_rows if row["Name"] != "default"}
    require(len(initial) == len(initial_rows), "AUTHOR_INITIAL_DUPLICATE", "CSV duplicate")
    require(set(initial) == set(source["species"]), "AUTHOR_INITIAL_COVERAGE", "species IDs differ")
    require(set(parameters) == set(source["reactions"]), "AUTHOR_PARAMETER_COVERAGE", "reaction IDs differ")
    for rid, reaction in source["reactions"].items():
        reaction["k"] = parameters[rid]
    index = {row["reaction_id"]: row for row in csv.DictReader(INDEX.open(encoding="utf-8-sig", newline=""))}
    annotations = {row["reaction_id"]: row for row in csv.DictReader(ANNOTATION.open(encoding="utf-8-sig", newline=""))}
    signature_ids = defaultdict(list)
    for rid, reaction in source["reactions"].items():
        signature_ids[signature(reaction)].append(rid)
    modules = {}
    with zipfile.ZipFile(SUBSYSTEM_ZIP) as archive:
        for unit, letter in UNITS.items():
            name = f"EnergyRegeneration_{letter}.xml"
            module = parse_xml(archive.read(name))
            extracted = ROOT / "models/pnas2017_full_reference/original/subsystems" / name
            second = parse_xml(extracted.read_bytes())
            require(module == second, "SUBSYSTEM_ARCHIVE_EQUIVALENCE", name)
            mapping = {}
            for local_id, reaction in module["reactions"].items():
                matches = signature_ids[signature(reaction)]
                require(len(matches) == 1, "SUBSYSTEM_SIGNATURE_MAPPING", f"{name}/{local_id}: {matches}")
                mapping[local_id] = matches[0]
                row = index[matches[0]]
                refs = json.loads(row["source_subsystem_reaction_refs_json"])
                require(any(x["source_file"] == name and x["source_reaction_id"] == local_id for x in refs), "INDEX_SUBSYSTEM_MEMBERSHIP", matches[0])
                require({k: Fraction(v) for k, v in json.loads(row["reactants_json"]).items()} == reaction["r"], "INDEX_REACTANTS", matches[0])
                require({k: Fraction(v) for k, v in json.loads(row["products_json"]).items()} == reaction["p"], "INDEX_PRODUCTS", matches[0])
                require(Fraction(row["directed_reference_parameter_value"]) == parameters[matches[0]], "INDEX_AUTHOR_PARAMETER", matches[0])
                require(row["reaction_family_id"] == annotations[matches[0]]["reaction_family_id"], "FAMILY_CROSS_INVENTORY", matches[0])
            module["mapping"] = mapping
            module["reactions"] = {rid: copy.deepcopy(source["reactions"][rid]) for rid in mapping.values()}
            module["families"] = {rid: index[rid]["reaction_family_id"] for rid in mapping.values()}
            module["filename"] = name
            module["unit"] = unit
            modules[unit] = module
    return source, initial, parameters, index, modules


def verify_source_semantics(candidate, authority):
    require(set(candidate["reactions"]) == set(authority["reactions"]), "SOURCE_REACTION_COVERAGE", sorted(set(authority["reactions"]) - set(candidate["reactions"])))
    for rid, reaction in candidate["reactions"].items():
        expected = authority["reactions"][rid]
        require(signature(reaction) == signature(expected), "SOURCE_DIRECTED_STOICHIOMETRY", rid)
        require(sy.simplify(reaction["law"] - expected["law"]) == 0, "SOURCE_KINETIC_LAW", rid)
        require(reaction["k"] == expected["k"], "AUTHOR_DIRECTED_PARAMETER", rid)
        require(candidate["families"][rid] == authority["families"][rid], "SOURCE_FAMILY_MEMBERSHIP", rid)


def active_reactions(module):
    return [r for r in module["reactions"].values() if r["k"] > 0]


def enzyme_states(module):
    unit = module["unit"]
    states = [unit] + sorted(x for x, parts in module["included_members"].items() if parts[unit])
    require(len(set(states)) == len(states), "ENZYME_STATE_DUPLICATE", unit)
    return states


def solve_moiety(module, free_weights, enzyme_weight=0, selected_reactions=None):
    """Infer bound weights from exact active chemistry, never from ID substrings."""
    states = enzyme_states(module)
    unknown_states = states[1:]
    unknowns = sy.symbols("q0:" + str(len(unknown_states)))
    weights = {name: sy.Rational(free_weights.get(name, 0)) for name in module["species"]}
    weights[states[0]] = sy.Rational(enzyme_weight)
    weights.update(dict(zip(unknown_states, unknowns)))
    reactions = active_reactions(module) if selected_reactions is None else selected_reactions
    equations = [sum(weights[x] * n for x, n in zip(module["species"], net(r, module["species"]))) for r in reactions]
    solutions = sy.solve(equations, unknowns, dict=True)
    require(len(solutions) == 1 and all(x in solutions[0] for x in unknowns), "BOUND_MOIETY_UNIQUENESS", module["unit"])
    result = {name: sy.simplify(value.subs(solutions[0])) for name, value in weights.items()}
    require(all(x.is_Rational and x >= 0 for x in result.values()), "BOUND_MOIETY_PHYSICAL", module["unit"])
    return result


def form_composition(module):
    states = enzyme_states(module)
    boundary = [s for s in module["species"] if s not in states and not s.endswith("_degraded")]
    # Binding/release conserve the identity of each free-resource form. Chemical
    # conversion is deliberately omitted from this compositional inference.
    binding = [r for r in active_reactions(module) if any(v != 0 for v in net(r, boundary))]
    composition = {s: {} for s in states}
    for resource in boundary:
        weights = solve_moiety(module, {resource: 1}, selected_reactions=binding)
        for state in states:
            composition[state][resource] = weights[state]
    # A CellDesigner membership establishes presence, while source binding
    # stoichiometry establishes multiplicity (including repeated ADP / PO4).
    for state in states[1:]:
        present = {s for s in boundary if composition[state][s] > 0}
        declared = set(module["included_members"][state]) - {module["unit"]}
        require(present == declared, "BOUND_RESOURCE_MEMBERSHIP", state)
    return boundary, composition


def exact_rhs(module, x):
    result = {s: sy.Integer(0) for s in module["species"]}
    for reaction in active_reactions(module):
        substitutions = {sy.Symbol(s): sy.Rational(value) for s, value in x.items()}
        substitutions[sy.Symbol("k1")] = sy.Rational(reaction["k"])
        flux = reaction["law"].subs(substitutions)
        require(not flux.free_symbols, "EXACT_RHS_INPUT_COVERAGE", reaction["id"])
        for s, n in zip(module["species"], net(reaction, module["species"])):
            result[s] += n * flux
    return result


def independent_kinetic_witnesses(module):
    boundary, composition = form_composition(module)
    states = enzyme_states(module)
    unit = module["unit"]
    first = {s: (sy.Integer(10) if s in boundary else sy.Integer(0)) for s in module["species"]}
    first[unit] = sy.Integer(1)
    # Select the loaded substrate state by parsed boundary composition rather
    # than a candidate-specific reaction/state table.
    substrate = {"CK": {"CP", "ADP"}, "NDK": {"ATP", "GDP"}, "MK": {"ATP", "AMP"}, "PPiase": {"PPi"}}[unit]
    loaded = next(s for s in states if {r for r in boundary if composition[s][r] > 0} == substrate)
    second_free = dict(first)
    second_free[unit], second_free[loaded] = sy.Integer(0), sy.Integer(1)
    second_total = dict(second_free)
    for resource in boundary:
        second_total[resource] -= composition[loaded][resource]
    first_rhs = exact_rhs(module, first)
    second_free_rhs = exact_rhs(module, second_free)
    second_total_rhs = exact_rhs(module, second_total)
    def totals(x):
        return [x[r] + sum(composition[s][r] * x[s] for s in states) for r in boundary]
    require(totals(first) == totals(second_total), "TOTAL_LUMPABILITY_WITNESS_COORDINATES", unit)
    free_delta = max(abs(first_rhs[r] - second_free_rhs[r]) for r in boundary)
    total_delta = max(abs(a - b) for a, b in zip(totals(first_rhs), totals(second_total_rhs)))
    require(free_delta > 0 and total_delta > 0, "SOURCE_NONLUMPABILITY_WITNESS", unit)
    # The product-total-zero corner with substrate totals10 and Etotal1 has
    # positive free substrates >=9. Products and product-bearing complexes are
    # forced zero by nonnegative accounting. At any positive substrate values,
    # the directed graph has a unique stationary class including a forbidden
    # product state. We check reachability and the exact representative Q at
    # lower-bound substrates9; rate signs are identical over all u_sub>0.
    free = {r: sy.Integer(9 if r in substrate else 0) for r in boundary}
    state_index = {s: i for i, s in enumerate(states)}
    Q = sy.zeros(len(states))
    graph = defaultdict(set)
    for reaction in active_reactions(module):
        source = next(s for s in reaction["r"] if s in state_index)
        target = next(s for s in reaction["p"] if s in state_index)
        flux = reaction["law"].subs({sy.Symbol("k1"): sy.Rational(reaction["k"]), **{sy.Symbol(r): v for r, v in free.items()}, sy.Symbol(source): 1})
        require(not flux.free_symbols, "SOURCE_GENERATOR_MASS_ACTION", reaction["id"])
        i, j = state_index[source], state_index[target]
        Q[j, i] += flux
        Q[i, i] -= flux
        if flux > 0:
            graph[source].add(target)
    products = set(boundary) - substrate
    forbidden = [s for s in states if any(composition[s][r] > 0 for r in products)]
    require(all(max(composition[s][r] for s in states) <= 1 for r in substrate), "CORNER_SUBSTRATE_STORAGE_BOUND", unit)
    for state in states:
        reachable = {state}
        pending = [state]
        while pending:
            for following in graph[pending.pop()]:
                if following not in reachable:
                    reachable.add(following)
                    pending.append(following)
        require(reachable == set(states), "CORNER_GENERATOR_IRREDUCIBLE", state)
    # Solve linear stationarity augmented with zero product-complex occupancy.
    hvars = sy.symbols("h0:" + str(len(states)))
    h = sy.Matrix(hvars)
    equations = list(Q * h) + [sum(hvars) - 1] + [hvars[state_index[s]] for s in forbidden]
    require(not sy.linsolve(equations, hvars), "ZERO_PRODUCT_CORNER_CLOSURE_INFEASIBLE", unit)
    return {"source_form_composition": {s: {r: str(v) for r, v in parts.items()} for s, parts in composition.items()}, "same_free_and_enzyme_total_counterexample": {"loaded_state": loaded, "max_projected_rhs_difference_exact": str(free_delta)}, "same_form_totals_and_enzyme_total_counterexample": {"total_coordinates_equal": True, "max_projected_rhs_difference_exact": str(total_delta)}, "zero_product_corner": {"substrate_total_each": 10, "enzyme_total": 1, "free_substrate_lower_bound": 9, "forbidden_product_bound_states": forbidden, "positive_substrate_generator_irreducible": True, "stationarity_with_forbidden_zero_solution_set": "EmptySet", "scope": "Nonnegative stationary-total closure infeasible at this source-directed substrate-positive/product-total-zero corner; microscopic state remains physical."}}


def verify_pool(module, weights):
    residuals = {}
    for reaction in active_reactions(module):
        residual = sum(weights.get(x, 0) * n for x, n in zip(module["species"], net(reaction, module["species"])))
        if residual != 0:
            residuals[reaction["id"]] = str(residual)
    require(not residuals, "EXACT_CONSERVED_POOL_RESIDUAL", residuals)


def cycles(module):
    states = enzyme_states(module)
    adjacency = defaultdict(list)
    for reaction in active_reactions(module):
        left = [x for x in states if reaction["r"].get(x, 0)]
        right = [x for x in states if reaction["p"].get(x, 0)]
        require(len(left) == len(right) == 1, "CATALYST_STATE_TRANSITION", reaction["id"])
        require(reaction["r"][left[0]] == reaction["p"][right[0]] == 1, "CATALYST_COPY_NUMBER", reaction["id"])
        adjacency[left[0]].append((right[0], reaction["id"]))
    boundary = [x for x in module["species"] if x not in states and not x.endswith("_degraded")]
    found = []
    for start in sorted(states):
        def walk(current, visited, path):
            for following, rid in adjacency[current]:
                if following == start:
                    ids = path + [rid]
                    vector = [sum(net(module["reactions"][r], boundary)[i] for r in ids) for i in range(len(boundary))]
                    found.append({"ids": ids, "boundary": dict(zip(boundary, map(str, vector))), "vector": vector})
                elif following not in visited and following >= start:
                    walk(following, visited | {following}, path + [rid])
        walk(start, {start}, [])
    return boundary, found


def certificate(module):
    species = list(module["species"])
    states = enzyme_states(module)
    boundary, known_cycles = cycles(module)
    active = active_reactions(module)
    matrix = sy.Matrix.hstack(*(sy.Matrix(net(r, species)) for r in active))
    internal_matrix = matrix.extract([species.index(x) for x in states], range(len(active)))
    boundary_matrix = matrix.extract([species.index(x) for x in boundary], range(len(active)))
    kernel = internal_matrix.nullspace()
    projections = sy.Matrix.hstack(*(boundary_matrix * v for v in kernel))
    rank = projections.rank()
    physical_vectors = [x["vector"] for x in known_cycles if any(x["vector"])]
    physical_rank = sy.Matrix.hstack(*(sy.Matrix(v) for v in physical_vectors)).rank() if physical_vectors else 0
    require(rank == physical_rank, "CONE_VERSUS_LINEAR_SPAN", module["unit"])
    # Exact state cycles are nonnegative witnesses. LP independently tests both
    # signs of an oriented catalytic resource direction under declared channels.
    oriented = next((v for v in physical_vectors if v[boundary.index({"CK": "CP", "NDK": "ATP", "MK": "ATP", "PPiase": "PPi"}[module["unit"]])] < 0), None)
    require(oriented is not None, "FORWARD_CATALYTIC_CYCLE_REACHABLE", module["unit"])
    direction = sy.Matrix(oriented)
    divisor = abs(next(x for x in direction if x != 0))
    direction = direction / divisor
    equalities = np.asarray(internal_matrix.col_join(boundary_matrix), dtype=float)
    directions = {}
    for sign, label in [(1, "forward"), (-1, "reverse")]:
        rhs = np.concatenate([np.zeros(len(states)), sign * np.asarray(direction, dtype=float).ravel()])
        fit = linprog(np.ones(len(active)), A_eq=equalities, b_eq=rhs, bounds=(0, None), method="highs")
        directions[label] = {"nonnegative_flux_feasible": bool(fit.success), "lp_status": int(fit.status)}
        if fit.success:
            directions[label]["witness_flux"] = {r["id"]: float(v) for r, v in zip(active, fit.x) if v > 1e-9}
    pools = {"enzyme": solve_moiety(module, {}, 1)}
    for label, free in FREE_GROUPS.items():
        if any(x in module["species"] for x in free):
            pools[label] = solve_moiety(module, free)
    for weights in pools.values():
        verify_pool(module, weights)
    disabled = [r for r in module["reactions"].values() if r["k"] == 0]
    disabled_effects = {name: {r["id"]: str(sum(weights[x] * n for x, n in zip(species, net(r, species)))) for r in disabled if sum(weights[x] * n for x, n in zip(species, net(r, species))) != 0} for name, weights in pools.items()}
    return {"source_subsystem": module["id"], "source_file": module["filename"], "original_count": len(module["reactions"]), "active_count": len(active), "zero_ids": [r["id"] for r in disabled], "family_counts": dict(Counter(module["families"].values())), "active_stoichiometric_rank": matrix.rank(), "internal_rank": internal_matrix.rank(), "internal_kernel_dimension": len(kernel), "boundary_projection_rank": rank, "nonnegative_cycle_projection_rank": physical_rank, "boundary_species": boundary, "oriented_net": dict(zip(boundary, map(str, direction))), "direction_feasibility": directions, "simple_enzyme_state_cycles": [{k: v for k, v in x.items() if k != "vector"} for x in known_cycles], "conserved_weights": {label: {x: str(v) for x, v in weights.items() if v != 0} for label, weights in pools.items()}, "disabled_channel_group_changes_if_activated": disabled_effects}, pools


def capture_failure(number, name, mutation, predicate, expected_gates, scope="actual_source_module"):
    mutated = mutation()
    try:
        predicate(mutated)
    except SemanticFailure as error:
        require(error.gate in expected_gates, "NEGATIVE_CONTROL_WRONG_GATE", f"{number}: {error.gate}")
        return {"number": number, "name": name, "scope": scope, "mutation_entered_semantic_predicate": True, "hash_gate_used": False, "caught": True, "failure_gate": error.gate, "failure_detail": error.detail}
    raise SemanticFailure("NEGATIVE_CONTROL_NOT_CAUGHT", f"{number}: {name}")


def mutated_module(module, edit):
    result = copy.deepcopy(module)
    edit(result)
    return result


def fixtures():
    x1, x2, k, a, b = sy.symbols("x1 x2 k a b", positive=True)
    # Two indistinguishable first-order loss channels, y=x1+x2.
    exact = sy.simplify(-k * x1 - k * x2 + k * (x1 + x2))
    require(exact == 0, "EXACT_LUMPABILITY_FIXTURE", str(exact))
    # Same retained y, distinct derivative if rates differ.
    unequal_delta = sy.simplify((-a * x1 - b * x2).subs({x1: 1, x2: 0}) - (-a * x1 - b * x2).subs({x1: 0, x2: 1}))
    require(unequal_delta == b - a, "NONLUMPABLE_FIXTURE", str(unequal_delta))
    # E+S <-> ES -> E+P at chemostatted S. Unique attractive exact
    # stationary ES gives the derived MM law; initial layer is also analytic.
    k1, km, kc, substrate, total, complex_ = sy.symbols("k1 km kc S Et ES", positive=True)
    derivative = k1 * substrate * (total - complex_) - (km + kc) * complex_
    selected = sy.solve(derivative, complex_)[0]
    law = sy.factor(kc * selected)
    require(sy.simplify(law - total * kc * substrate / (substrate + (km + kc) / k1)) == 0, "DERIVED_RATE_FIXTURE", str(law))
    numeric = {k1: 4, km: 3, kc: 2, substrate: 5, total: 1}
    stationary = float(selected.subs(numeric))
    gap = 25.0
    times = np.array([0, 0.002, 0.02, 0.2, 1])
    answer = solve_ivp(lambda t, z: [20 * (1 - z[0]) - 5 * z[0]], [0, 1], [0], t_eval=times, method="Radau", rtol=1e-11, atol=1e-13)
    require(answer.success, "ANALYTIC_FIXTURE_INTEGRATION", answer.message)
    analytic = stationary * (1 - np.exp(-gap * times))
    error = float(np.max(np.abs(answer.y[0] - analytic)))
    require(error < 1e-10, "ANALYTIC_FIXTURE_NUMERIC", error)
    return {"exact_lumpable_parallel_losses": {"symbolic_residual": str(exact)}, "nonlumpable_unequal_parallel_losses": {"same_y_derivative_difference": str(unequal_delta)}, "analytic_chemostatted_enzyme": {"rate": str(law), "stationary_complex": str(selected), "attractivity_eigenvalue": str(sy.diff(derivative, complex_)), "numeric_max_absolute_error": error, "initial_complex": 0, "equilibrium_complex": stationary, "root_scope": "chemostatted synthetic E+S enzyme fixture, not a PNAS cycle"}}


def manifold_gate(record):
    # A pure algebraic candidate claims the eliminated state is initially on its
    # selected steady manifold. Boundary-matched off-manifold states must instead
    # be labelled NON_EQUILIBRIUM_INITIAL_LAYER or retain an occupancy state.
    require(record["status"] != "PROJECTED_FAST_MANIFOLD" or record["normalized_algebraic_residual"] <= record["allowance"], "INITIAL_FAST_MANIFOLD_ASSUMPTION", record)


def resource_gates(metrics, thresholds):
    required = ["long_retained_error", "net_flux_nrms", "cumulative_resource_error", "conservation_residual", "protein_endpoint_error"]
    for field in required:
        require(field in metrics, "REQUIRED_OBSERVABLE_COVERAGE", field)
    for field in required:
        require(metrics[field] <= thresholds[field], "PREREGISTERED_" + field.upper(), {"observed": metrics[field], "limit": thresholds[field]})


def negative_controls(modules, initial, pools):
    rows = []
    ck, ndk, mk, ppi = [modules[x] for x in ["CK", "NDK", "MK", "PPiase"]]
    ck_active = active_reactions(ck)
    catalytic_ck = next(r["id"] for r in ck_active if set(r["r"]) == {"CK_CP_ADP"} and set(r["p"]) == {"CK_Cr_ATP"})
    disabled_ndk = next(r["id"] for r in ndk["reactions"].values() if set(r["r"]) == {"NDK_GTP_ADP"} and set(r["p"]) == {"NDK_GDP_ATP"})
    release_ppi = next(r["id"] for r in active_reactions(ppi) if set(r["r"]) == {"PPiase_PO4"} and set(r["p"]) == {"PPiase", "PO4"})
    rows.append(capture_failure(1, "remove an active CK reaction", lambda: mutated_module(ck, lambda m: m["reactions"].pop(ck_active[0]["id"])), lambda m: verify_source_semantics(m, ck), {"SOURCE_REACTION_COVERAGE"}))
    def reverse_ck(m):
        r = m["reactions"][catalytic_ck]
        r["r"], r["p"] = r["p"], r["r"]
    rows.append(capture_failure(2, "reverse CK catalytic conversion with unchanged source ID mapping", lambda: mutated_module(ck, reverse_ck), lambda m: verify_source_semantics(m, ck), {"SOURCE_DIRECTED_STOICHIOMETRY"}))
    binding = next(r["id"] for r in ck_active if "ADP" in r["r"])
    def alter_nucleotide(m):
        m["reactions"][binding]["r"]["ADP"] = Fraction(2)
    rows.append(capture_failure(3, "double an ADP stoichiometric coefficient", lambda: mutated_module(ck, alter_nucleotide), lambda m: verify_pool(m, pools["CK"]["adenylate"]), {"EXACT_CONSERVED_POOL_RESIDUAL"}))
    rows.append(capture_failure(4, "activate NDK author-zero reverse chemical channel", lambda: mutated_module(ndk, lambda m: m["reactions"][disabled_ndk].update(k=Fraction(1))), lambda m: verify_source_semantics(m, ndk), {"AUTHOR_DIRECTED_PARAMETER"}))
    def omit_bound():
        q = dict(pools["CK"]["adenylate"])
        q["CK_CP_ADP"] = sy.Integer(0)
        return q
    rows.append(capture_failure(5, "omit bound CK_CP_ADP nucleotide from adenylate pool", omit_bound, lambda q: verify_pool(ck, q), {"EXACT_CONSERVED_POOL_RESIDUAL"}))
    rows.append(capture_failure(6, "omit terminal PPiase PO4 release event", lambda: mutated_module(ppi, lambda m: m["reactions"].pop(release_ppi)), certificate, {"FORWARD_CATALYTIC_CYCLE_REACHABLE"}))
    rows.append(capture_failure(7, "effective PPi to one PO4 loses a represented phosphate group", lambda: {"PPi": -1, "PO4": 1}, lambda v: require(sum(FREE_GROUPS["represented_phosphate_groups"][s] * n for s, n in v.items()) == 0, "EFFECTIVE_RESOURCE_STOICHIOMETRY", v), {"EFFECTIVE_RESOURCE_STOICHIOMETRY"}))
    rows.append(capture_failure(8, "mix all-one structural initial inputs with author parameters", lambda: {s: Fraction(1) for s in initial}, lambda x: require(x == initial, "AUTHOR_INITIAL_VALUES", {"mismatched_species": sum(x[s] != initial[s] for s in initial), "author_positive_count": sum(v > 0 for v in initial.values()), "mixed_positive_count": sum(v > 0 for v in x.values())}), {"AUTHOR_INITIAL_VALUES"}, "actual_author_input_overlay"))
    rows.append(capture_failure(9, "corrupt principal CK family membership", lambda: mutated_module(ck, lambda m: m["families"].update({catalytic_ck: "RFAM_016"})), lambda m: verify_source_semantics(m, ck), {"SOURCE_FAMILY_MEMBERSHIP"}))
    # This fixture has two independent A->B and A->C transfers with no internal
    # state. Its rank cannot be represented by a single effective direction.
    rows.append(capture_failure(10, "add a second independent synthetic net direction", lambda: sy.Matrix([[-1, -1], [1, 0], [0, 1]]), lambda s: require(s.rank() == 1, "SINGLE_NET_DIRECTION", {"exact_rank": s.rank()}), {"SINGLE_NET_DIRECTION"}, "synthetic_exact_stoichiometric_fixture"))
    registration_path = ROOT / "docs/reduction/energy_cycles/validation_preregistration.json"
    registration = json.loads(registration_path.read_text(encoding="utf-8")) if registration_path.exists() else None
    allowance = registration["solver"]["closure_absolute_residual"] if registration else 1e-8
    off_manifold = {s: (10 if s in form_composition(ck)[0] else 0) for s in ck["species"]}
    off_manifold["CK"] = 1
    residual = float(max(abs(exact_rhs(ck, off_manifold)[s]) for s in enzyme_states(ck)))
    rows.append(capture_failure(11, "declare source CK off-manifold enzyme occupancy projected", lambda: {"status": "PROJECTED_FAST_MANIFOLD", "normalized_algebraic_residual": residual, "allowance": allowance, "source_state": off_manifold, "normalization": "Etotal=1; absolute source enzyme-stationarity residual"}, manifold_gate, {"INITIAL_FAST_MANIFOLD_ASSUMPTION"}, "actual_source_CK_initialization_and_frozen_closure_policy"))
    gates = registration["gates"] if registration else {"long_concentration": .05, "long_flux_rms": .1, "cumulative_resource_flow": .02, "normalized_conservation": 1e-8, "full_Pept0003_endpoint": .05}
    thresholds = {"long_retained_error": gates["long_concentration"], "net_flux_nrms": gates["long_flux_rms"], "cumulative_resource_error": gates["cumulative_resource_flow"], "conservation_residual": gates["normalized_conservation"], "protein_endpoint_error": gates["full_Pept0003_endpoint"]}
    rows.append(capture_failure(12, "protein endpoint agrees while cumulative resource gate fails", lambda: {"long_retained_error": 0.01, "net_flux_nrms": 0.01, "cumulative_resource_error": 0.03, "conservation_residual": 0.0, "protein_endpoint_error": 0.0}, lambda x: resource_gates(x, thresholds), {"PREREGISTERED_CUMULATIVE_RESOURCE_ERROR"}, "synthetic_numeric_multiobservable_acceptance_policy"))
    return rows


def inspect_derived_inventory(modules):
    """Cross-check new inventory when present without importing its generator."""
    path = ROOT / "docs/reduction/energy_cycles/reaction_inventory.csv"
    if not path.exists():
        return {"status": "NOT_AVAILABLE_AT_TEST_TIME"}
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    expected = {rid: r for m in modules.values() for rid, r in m["reactions"].items()}
    id_key = next((x for x in ("original_directed_reaction_id", "original_reaction_id", "reaction_id") if rows and x in rows[0]), None)
    if id_key is None:
        return {"status": "SCHEMA_NOT_RECOGNIZED", "columns": list(rows[0]) if rows else []}
    observed = {r[id_key]: r for r in rows if r[id_key] in expected}
    require(set(observed) == set(expected), "DERIVED_INVENTORY_COVERAGE", sorted(set(expected) - set(observed)))
    return {"status": "COVERAGE_VERIFIED", "principal_subsystem_reactions": len(expected), "rows_total": len(rows), "limitation": "Only coverage checked here; canonical semantic parsing and adversarial checks are independent."}


def inspect_source_inventory(source, initial, modules, witnesses):
    path = ROOT / "results/energy_cycles_v1/source_inventory.json"
    if not path.exists():
        return {"status": "NOT_AVAILABLE_AT_TEST_TIME"}
    data = json.loads(path.read_text(encoding="utf-8"))
    require(set(data["species_ids"]) == set(source["species"]), "GENERATED_SOURCE_SPECIES", "coverage")
    require({s: Fraction(str(v)) for s, v in data["initial"].items()} == initial, "GENERATED_AUTHOR_INITIAL", "values")
    rows = {r["id"]: r for r in data["reactions"]}
    require(set(rows) == set(source["reactions"]), "GENERATED_SOURCE_REACTIONS", "coverage")
    symbolic_names = {s: sy.Symbol(s) for s in source["species"]}
    symbolic_names["k1"] = sy.Symbol("k1")
    for rid, reaction in source["reactions"].items():
        row = rows[rid]
        require({s: Fraction(str(v)) for s, v in row["reactants"].items()} == reaction["r"], "GENERATED_SOURCE_REACTANTS", rid)
        require({s: Fraction(str(v)) for s, v in row["products"].items()} == reaction["p"], "GENERATED_SOURCE_PRODUCTS", rid)
        require(Fraction(str(row["k"])) == reaction["k"], "GENERATED_AUTHOR_PARAMETER", rid)
        require(sy.simplify(sy.sympify(row["kinetic_law"], locals=symbolic_names) - reaction["law"]) == 0, "GENERATED_KINETIC_EXPRESSION", rid)
    for unit in data["units"]:
        name = unit["name"]
        module = modules[name]
        require(set(unit["reaction_ids"]) == set(module["reactions"]), "GENERATED_SUBSYSTEM_COVERAGE", name)
        require(set(unit["active_reaction_ids"]) == {r["id"] for r in active_reactions(module)}, "GENERATED_ACTIVE_CHANNELS", name)
        expected = witnesses[name]["source_form_composition"]
        actual = {s: {r: str(v) for r, v in parts.items()} for s, parts in unit["resource_composition"].items()}
        require(expected == actual, "GENERATED_BOUND_FORM_COMPOSITION", name)
    return {"status": "INDEPENDENT_SEMANTIC_VERIFICATION_PASS", "all_source_reaction_stoichiometries_and_laws_checked": len(rows), "author_values_checked": len(initial) + len(rows), "enzyme_bound_form_composition_checked_for_all_units": True, "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def inspect_kinetic_analysis(source, initial, modules, witnesses):
    path = ROOT / "results/energy_cycles_v1/kinetic_analysis.json"
    if not path.exists():
        return {"status": "NOT_AVAILABLE_AT_TEST_TIME"}
    data = json.loads(path.read_text(encoding="utf-8"))
    output = {}
    for entry in data["generator_tests"]:
        name = entry["unit"]
        module = modules[name]
        witness = witnesses[name]
        for mode, key in [("free_pair", "same_free_and_enzyme_total_counterexample"), ("total_pair", "same_form_totals_and_enzyme_total_counterexample")]:
            expected = float(Fraction(witness[key]["max_projected_rhs_difference_exact"]))
            observed = entry["lumpability"][mode]["max_projected_rhs_difference"]
            require(abs(expected - observed) <= 1e-10 * max(expected, 1), "KINETIC_LUMPABILITY_REPORT", name + ":" + mode)
        states = enzyme_states(module)
        boundary, composition = form_composition(module)
        index = {s: i for i, s in enumerate(states)}
        tests = []
        for probe in entry["fixed_free_stationarity"]:
            Q = np.zeros((len(states), len(states)))
            for reaction in active_reactions(module):
                source_state = next(s for s in reaction["r"] if s in index)
                target = next(s for s in reaction["p"] if s in index)
                substitutions = {sy.Symbol("k1"): sy.Rational(reaction["k"]), sy.Symbol(source_state): 1}
                substitutions.update({sy.Symbol(s): sy.Rational(str(v)) for s, v in probe["free"].items()})
                rate = float(reaction["law"].subs(substitutions))
                i, j = index[source_state], index[target]
                Q[j, i] += rate
                Q[i, i] -= rate
            h = np.array([probe["occupancies"][s] for s in states])
            enzyme_total = float(sum(initial[s] for s in states))
            residual = float(np.max(np.abs(Q @ h)))
            require(residual <= 1e-8 * max(enzyme_total, 1), "KINETIC_STATIONARY_OCCUPANCY_RESIDUAL", {"unit": name, "residual": residual})
            require(abs(h.sum() - enzyme_total) <= 1e-10 * max(enzyme_total, 1), "KINETIC_STATIONARY_ENZYME_TOTAL", name)
            require(h.min() >= -1e-12, "KINETIC_STATIONARY_POSITIVITY", name)
            independent_rhs = exact_rhs(module, {**{s: 0 for s in module["species"]}, **probe["free"], **probe["occupancies"]})
            projected = {r: float(independent_rhs[r] + sum(composition[s][r] * independent_rhs[s] for s in states)) for r in boundary}
            # Stationary free-resource derivative must agree with declared net
            # current and the independently enumerated canonical direction.
            direction = {"CK": {"CP": -1, "ADP": -1, "Cr": 1, "ATP": 1}, "NDK": {"ATP": -1, "GDP": -1, "ADP": 1, "GTP": 1}, "MK": {"ATP": -1, "AMP": -1, "ADP": 2}, "PPiase": {"PPi": -1, "PO4": 2}}[name]
            current = probe["net_catalytic_current"]
            rate_error = max(abs(projected[r] - direction[r] * current) for r in boundary)
            require(rate_error <= 1e-8 * max(abs(current), 1), "KINETIC_STATIONARY_NET_CURRENT", name)
            tests.append({"label": probe["label"], "independent_generator_residual": residual, "independent_source_net_current_error": rate_error})
        output[name] = tests
    return {"status": "INDEPENDENT_CANONICAL_RHS_VERIFICATION_PASS", "tests": output, "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "scope": "Fixed-free stationary occupancy and nonlumpability checks only; not trajectory validation."}


def serializable(value):
    if isinstance(value, dict):
        return {str(k): serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(x) for x in value]
    if isinstance(value, (Fraction, sy.Basic)):
        return str(value)
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "results/energy_cycles_v1/independent_tests.json")
    args = parser.parse_args()
    source, initial, parameters, index, modules = read_sources()
    structural_parameters = ET.fromstring(ORIGINAL.read_bytes()).findall(".//" + SB + "kineticLaw/" + SB + "listOfParameters/" + SB + "parameter")
    require(len(structural_parameters) == len(source["reactions"]), "STRUCTURAL_LOCAL_PARAMETER_COVERAGE", len(structural_parameters))
    require(all(x.get("id") == "k1" and Fraction(x.get("value")) == 1 for x in structural_parameters), "STRUCTURAL_ALL_ONE_PARAMETERS", "source placeholders differ")
    certificates = {}
    pools = {}
    for unit, module in modules.items():
        verify_source_semantics(module, module)
        certificates[unit], pools[unit] = certificate(module)
    witnesses = {name: independent_kinetic_witnesses(module) for name, module in modules.items()}
    fixture_results = fixtures()
    controls = negative_controls(modules, initial, pools)
    paths = [ORIGINAL, NORMALIZED, AUTHOR_ZIP, SUBSYSTEM_ZIP, INDEX, ANNOTATION, Path(__file__)]
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    report = {"schema_version": "energy_cycles_independent_tests_v1", "status": "INDEPENDENT_ENGINEERING_CHECKS_PASS_NOT_SCIENTIFIC_ACCEPTANCE", "executed_at_utc": datetime.now(timezone.utc).isoformat(), "source_commit": commit, "command": subprocess.list2cmdline([sys.executable, str(Path(__file__).resolve()), "--output", str(args.output.resolve())]), "environment": {"python": sys.version, "platform": platform.platform(), "sympy": sy.__version__, "scipy": scipy.__version__, "numpy": np.__version__, "xml_parser": "stdlib ElementTree independent of libSBML and source.py"}, "source_hashes": hashes, "source_summary": {"species": len(source["species"]), "reactions": len(source["reactions"]), "author_positive_initial_species": sum(v > 0 for v in initial.values()), "author_nonzero_parameters": sum(v > 0 for v in parameters.values()), "all_original_initial_concentrations_one": all(x.get("initialConcentration") == "1" for x in source["species"].values()), "all_original_local_k1_one": all(Fraction(x.get("value")) == 1 for x in ET.fromstring(ORIGINAL.read_bytes()).findall(".//" + SB + "kineticLaw/" + SB + "listOfParameters/" + SB + "parameter")), "literal_PO4_re0000000414": str(source["reactions"]["re0000000414"]["p"]["PO4"]), "combined_energy_reactions": sum(x["original_count"] for x in certificates.values()), "combined_energy_nonzero_channels": sum(x["active_count"] for x in certificates.values())}, "certificates": certificates, "source_kinetic_witnesses": witnesses, "synthetic_fixtures": fixture_results, "negative_controls": controls, "negative_controls_caught": sum(x["caught"] for x in controls), "derived_inventory_check": inspect_derived_inventory(modules), "generated_source_inventory_check": inspect_source_inventory(source, initial, modules, witnesses), "generated_kinetic_analysis_check": inspect_kinetic_analysis(source, initial, modules, witnesses), "scope_limits": ["Tests prove source/structural/ledger and specified gate behavior, never scientific reduction acceptance.", "Controls 10-12 are mathematical/policy fixtures labelled synthetic; they do not claim adverse full-PNAS trajectories were executed.", "Conserved group weights are source-representation moieties, not complete elemental/ionic conservation.", "Candidate trajectory convergence and effective-rate accuracy require separate preregistered numerical evidence."]}
    report["scope_limits"][1] = "Controls 10 and 12 are labelled synthetic mathematical/multiobservable-policy fixtures. Control 11 computes the canonical CK off-manifold enzyme RHS and applies the frozen candidate closure allowance. No adverse full-PNAS trajectory is claimed."
    report["source_summary"].update(structural_local_parameter_count=len(structural_parameters),
                                    energy_degradation_family_channels=sum(x["family_counts"].get("RFAM_DEG", 0) for x in certificates.values()),
                                    energy_principal_family_channels=sum(x["original_count"] - x["family_counts"].get("RFAM_DEG", 0) for x in certificates.values()),
                                    energy_reference_zero_channels=sum(x["original_count"] - x["active_count"] for x in certificates.values()))
    registration_path = ROOT / "docs/reduction/energy_cycles/validation_preregistration.json"
    if registration_path.exists():
        report["frozen_gate_policy_sha256"] = hashlib.sha256(registration_path.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(serializable(report), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "negative_controls_caught": report["negative_controls_caught"], "energy_count": report["source_summary"]["combined_energy_reactions"], "energy_active": report["source_summary"]["combined_energy_nonzero_channels"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
