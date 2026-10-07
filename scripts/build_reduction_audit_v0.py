#!/usr/bin/env python3
"""Build a source-bound R1/R2 audit without making reduction decisions.

All stoichiometric algebra uses Fraction. Floating calculations below are
independent numerical sanity checks of an already exact representation.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/reduction"
SBML = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
COMPAT = ROOT / "models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml"
EFFECTIVE = ROOT / "results/pnas2017_reference/rr_cvode_author_csv_20260924/effective_author_conditions.xml"
AUTHOR = ROOT / "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat"
S = "{http://www.sbml.org/sbml/level2/version4}"
M = "{http://www.w3.org/1998/Math/MathML}"
RESOURCE_NAMES = {"ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr",
                  "Gly", "Met", "fMet", "tRNAGlyGCC", "tRNAfMetCAU", "GlytRNAGlyGCC",
                  "MettRNAfMetCAU", "fMettRNAfMetCAU", "RS30S", "RS50S", "RS70S"}
POOL_TOKENS = ("GlyRS", "MetRS", "EFTu", "EFTs", "EFG", "IF1", "IF2", "IF3",
               "RF1", "RF2", "RF3", "RRF", "CK", "NDK", "MK", "PPiase", "MTF")
APPROVED_SIDE_PATHS = {f"re{number:010d}" for number in (26, 27, 63, 64, 87, 88, 121, 122)}


def read(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value):
    return Fraction(str(value).strip())


def fmt(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def side(reaction, side_name):
    parent = reaction.find(S + side_name)
    result = {}
    if parent is None:
        return result
    for ref in parent.findall(S + "speciesReference"):
        sid = ref.attrib["species"]
        math = ref.find(S + "stoichiometryMath")
        if math is None:
            coefficient = number(ref.attrib.get("stoichiometry", "1"))
        else:
            node = math.find(M + "math")
            assert node is not None and len(node) == 1 and node[0].tag == M + "cn", sid
            coefficient = number(node[0].text)
        assert coefficient > 0 and sid not in result
        result[sid] = coefficient
    return result


def rate_factors(reaction, species_set):
    law = reaction.find(S + "kineticLaw")
    assert law is not None, reaction.attrib["id"]
    params = law.find(S + "listOfParameters")
    assert params is not None and len(params) == 1, reaction.attrib["id"]
    parameter = params[0]
    assert parameter.attrib["id"] == "k1" and parameter.attrib.get("constant") == "true"
    math = law.find(M + "math")
    assert math is not None and len(math) == 1
    apply = math[0]
    assert apply.tag == M + "apply" and len(apply) >= 3 and apply[0].tag == M + "times"
    assert all(node.tag == M + "ci" for node in apply[1:]), reaction.attrib["id"]
    factors = [node.text.strip() for node in apply[1:]]
    assert factors.count("k1") == 1 and all(x == "k1" or x in species_set for x in factors)
    # No alternative term or piecewise branch can bypass the direct k1 factor.
    return factors, parameter.attrib


def parse_sbml(path):
    root = ET.parse(path).getroot()
    model = root.find(S + "model")
    assert model is not None
    for forbidden in ("listOfRules", "listOfEvents", "listOfInitialAssignments", "listOfFunctionDefinitions"):
        node = model.find(S + forbidden)
        assert node is None or len(node) == 0, f"unsupported source override: {forbidden}"
    species_nodes = model.find(S + "listOfSpecies")
    species = [node.attrib["id"] for node in species_nodes.findall(S + "species")]
    species_set = set(species)
    assert len(species) == len(species_set) == 241
    reactions = []
    for node in model.find(S + "listOfReactions").findall(S + "reaction"):
        reactants = side(node, "listOfReactants")
        products = side(node, "listOfProducts")
        factors, param = rate_factors(node, species_set)
        assert set(reactants) | set(products) <= species_set
        reactions.append(dict(id=node.attrib["id"], reactants=reactants, products=products,
                              factors=factors, parameter=param,
                              formula=" * ".join(factors)))
    assert len(reactions) == len({r["id"] for r in reactions}) == 968
    return species, reactions


def load_source_network():
    species, reactions = parse_sbml(SBML)
    compatible_species, compatible = parse_sbml(COMPAT)
    assert species == compatible_species
    for left, right in zip(reactions, compatible):
        assert all(left[key] == right[key] for key in ("id", "reactants", "products", "factors", "parameter")), left["id"]
    author_parameters = {row["Name"]: number(row["Value"]) for row in read(AUTHOR / "fMGG_synthesis_parameters.csv")}
    assert set(author_parameters) == {r["id"] + "_k1" for r in reactions} | {"default"}
    effective_species, effective = parse_sbml(EFFECTIVE)
    assert species == effective_species
    annotation = {row["reaction_id"]: row for row in read(OUT / "reaction_level_annotation_v2.csv")}
    balance = {row["sbml_reaction_id"]: row for row in read(ROOT / "models/pnas2017_full_reference/audit/reaction_balance_audit.csv")}
    assert set(annotation) == set(balance) == {r["id"] for r in reactions}
    for reaction, imported in zip(reactions, effective):
        rid = reaction["id"]
        key = rid + "_k1"
        assert key in author_parameters
        reaction["k"] = author_parameters[key]
        assert number(balance[rid]["official_parameter_value"]) == reaction["k"]
        assert balance[rid]["official_parameter_id"] == key
        assert reaction["parameter"].get("units") == "substance"
        assert reaction["parameter"].get("value") == "1"
        assert all(reaction[field] == imported[field] for field in ("id", "reactants", "products", "factors")), rid
        assert imported["parameter"].get("id") == "k1" and imported["parameter"].get("constant") == "true"
        assert imported["parameter"].get("units") == reaction["parameter"].get("units")
        assert number(imported["parameter"]["value"]) == reaction["k"], rid
        assert reaction["formula"] == source_reaction_inventory[rid]["kinetic_law_formula"]
    initial = {row["Name"]: number(row["Value"]) for row in read(AUTHOR / "fMGG_synthesis_initial_values.csv")}
    assert set(initial) == set(species)
    return species, reactions, annotation, initial


# Inventory is a cross-check; MathML above is the source of rate semantics.
source_reaction_inventory = {row["reaction_id"]: row for row in read(ROOT / "models/pnas2017_full_reference/audit/reactions.csv")}


def build_exact_stoichiometry(species, reactions):
    index = {name: i for i, name in enumerate(species)}
    columns = []
    for reaction in reactions:
        col = {}
        for side_map, sign in ((reaction["reactants"], -1), (reaction["products"], 1)):
            for name, value in side_map.items():
                i = index[name]
                col[i] = col.get(i, Fraction()) + sign * value
        columns.append({i: value for i, value in col.items() if value})
    return columns


def find_reverse_channels(reactions, columns, annotation):
    def signature(side_map):
        return tuple(sorted(side_map.items()))
    by_sides = {}
    for reaction in reactions:
        key = (signature(reaction["reactants"]), signature(reaction["products"]))
        by_sides.setdefault(key, []).append(reaction["id"])
    by_id = {reaction["id"]: (i, reaction) for i, reaction in enumerate(reactions)}
    paired = set()
    channels = []
    for reaction in reactions:
        rid = reaction["id"]
        if rid in paired:
            continue
        swapped = (signature(reaction["products"]), signature(reaction["reactants"]))
        partners = [x for x in by_sides.get(swapped, []) if x != rid]
        assert len(partners) <= 1, (rid, partners)
        if not partners:
            continue
        partner_id = partners[0]
        assert partner_id not in paired
        left, right = sorted((rid, partner_id))
        li, forward = by_id[left]
        ri, reverse = by_id[right]
        assert columns[li] == {i: -v for i, v in columns[ri].items()}
        assert forward["reactants"] == reverse["products"] and forward["products"] == reverse["reactants"]
        assert annotation[left]["reaction_family_id"] == annotation[right]["reaction_family_id"]
        assert annotation[left]["level_c_functional_contexts"] == annotation[right]["level_c_functional_contexts"]
        paired.update((left, right))
        channels.append((forward, reverse))
    assert len(channels) == 290 and len(paired) == 580
    return channels, paired


def flux(reaction, state):
    value = float(reaction["k"])
    for factor in reaction["factors"]:
        if factor != "k1":
            value *= state[factor]
    return value


def rhs_original(species, reactions, columns, state):
    result = [0.0] * len(species)
    for reaction, column in zip(reactions, columns):
        rate = flux(reaction, state)
        for i, value in column.items():
            result[i] += float(value) * rate
    return result


def rhs_reverse_view(species, reactions, columns, channels, paired, state):
    result = [0.0] * len(species)
    by_id = {reaction["id"]: (reaction, column) for reaction, column in zip(reactions, columns)}
    for forward, reverse in channels:
        net = flux(forward, state) - flux(reverse, state)
        for i, value in by_id[forward["id"]][1].items():
            result[i] += float(value) * net
    for reaction, column in zip(reactions, columns):
        if reaction["id"] in paired:
            continue
        rate = flux(reaction, state)
        for i, value in column.items():
            result[i] += float(value) * rate
    return result


def trajectory_sanity(reactions, columns, initial):
    # A nontrivial author-initialized reversible channel is sufficient for a
    # numerical integration smoke. The exact proof is the stoichiometric one.
    by_id = {r["id"]: (r, c) for r, c in zip(reactions, columns)}
    pair = (by_id["re0000000457"][0], by_id["re0000000458"][0])
    names = sorted(set(pair[0]["reactants"]) | set(pair[0]["products"]))
    x0 = {name: float(initial[name]) for name in names}

    def derivative(state, alternative):
        vf, vr = (flux(r, state) for r in pair)
        out = {name: 0.0 for name in names}
        for name in names:
            coeff = float(pair[0]["products"].get(name, 0) - pair[0]["reactants"].get(name, 0))
            if alternative:
                out[name] = coeff * (vf - vr)
            else:
                out[name] = coeff * vf + (-coeff) * vr
        return out

    def rk4(state, alternative, dt):
        k1 = derivative(state, alternative)
        k2 = derivative({n: state[n] + dt * k1[n] / 2 for n in names}, alternative)
        k3 = derivative({n: state[n] + dt * k2[n] / 2 for n in names}, alternative)
        k4 = derivative({n: state[n] + dt * k3[n] for n in names}, alternative)
        return {n: state[n] + dt * (k1[n] + 2*k2[n] + 2*k3[n] + k4[n]) / 6 for n in names}

    direct, merged = dict(x0), dict(x0)
    error = 0.0
    for _ in range(100):
        direct = rk4(direct, False, 0.01)
        merged = rk4(merged, True, 0.01)
        error = max(error, *(abs(direct[n] - merged[n]) for n in names))
    assert error <= 1e-6
    return error


def prove_reverse_representation(species, reactions, columns, channels, paired, initial):
    by_id = {r["id"]: c for r, c in zip(reactions, columns)}
    for forward, reverse in channels:
        fcol, rcol = by_id[forward["id"]], by_id[reverse["id"]]
        assert fcol == {i: -v for i, v in rcol.items()}
        # Every resource ledger still has two directed extents, vf and vr.
        assert all(fcol.get(i, 0) == -rcol.get(i, 0) for i, name in enumerate(species) if name in RESOURCE_NAMES)
    states = [initial]
    for seed in (1, 7, 29):
        states.append({name: 0.1 + (((i + 1) * (seed + 3)) % 31) / 10 for i, name in enumerate(species)})
    error = 0.0
    for state in states:
        direct = rhs_original(species, reactions, columns, {n: float(v) for n, v in state.items()})
        merged = rhs_reverse_view(species, reactions, columns, channels, paired, {n: float(v) for n, v in state.items()})
        scale = max(1.0, *(abs(x) for x in direct), *(abs(x) for x in merged))
        error = max(error, max(abs(a - b) for a, b in zip(direct, merged)) / scale)
    assert error <= 1e-12, error
    return error, trajectory_sanity(reactions, columns, initial)


def find_zero_flux_reactions(reactions, channels, annotation):
    partner = {}
    for forward, reverse in channels:
        partner[forward["id"]] = reverse
        partner[reverse["id"]] = forward
    records = []
    for reaction in reactions:
        if reaction["k"] != 0:
            continue
        rid = reaction["id"]
        assert reaction["factors"].count("k1") == 1
        other = partner.get(rid)
        if annotation[rid]["reaction_family_id"] == "RFAM_DEG":
            zero_class = "REFERENCE_ZERO_DEGRADATION"
        elif rid in APPROVED_SIDE_PATHS:
            assert other and other["k"] == 0
            zero_class = "REFERENCE_ZERO_SIDE_PATH"
        elif other:
            zero_class = "REFERENCE_ZERO_REVERSE_CHANNEL" if other["k"] != 0 else "REFERENCE_ZERO_OTHER"
        else:
            zero_class = "REFERENCE_ZERO_OTHER"
        if other is None:
            pattern = "UNPAIRED_ZERO"
        elif other["k"] == 0:
            pattern = "BIDIRECTIONAL_ZERO"
        else:
            pattern = "ONLY_FORWARD_ZERO" if rid < other["id"] else "ONLY_REVERSE_ZERO"
        row = annotation[rid]
        records.append(dict(reaction_id=rid, reaction_family_id=row["reaction_family_id"],
                            functional_contexts=row["level_c_functional_contexts"],
                            cross_family_link_ids=row["cross_family_link_ids"],
                            reaction_equation=" + ".join(reaction["reactants"]) + " -> " + " + ".join(reaction["products"]),
                            official_parameter_name=rid + "_k1", official_parameter_value=fmt(reaction["k"]),
                            kinetic_law=reaction["formula"],
                            zero_flux_proof="MathML is a single product with constant local k1 as a direct factor; frozen author CSV sets reaction-local k1=0; no rules/events/alternative branch; normalized import matches",
                            zero_class=zero_class, reverse_partner_id=other["id"] if other else "",
                            partner_parameter_value=fmt(other["k"]) if other else "",
                            pair_zero_pattern=pattern, scope="FROZEN_REFERENCE_ONLY",
                            source_provenance="canonical_SBML_MathML+author_parameter_CSV+normalized_compatibility_copy",
                            active_rhs_treatment="EXCLUDED_FROM_FROZEN_REFERENCE_ACTIVE_RHS",
                            confidence="HIGH_EXACT", human_review_required="false", reason=""))
    return records


def echelon_rows(columns):
    """Exact row echelon of S^T; pivot count is exact rank over Q."""
    pivots = {}
    for column in columns:
        row = dict(column)
        while row:
            pivot = min(row)
            value = row[pivot]
            if pivot not in pivots:
                pivots[pivot] = {j: entry / value for j, entry in row.items()}
                break
            for j, entry in pivots[pivot].items():
                row[j] = row.get(j, Fraction()) - value * entry
                if not row[j]:
                    del row[j]
    return pivots


def nullspace_basis(pivots, count):
    free = sorted(set(range(count)) - set(pivots))
    basis = []
    for free_index in free:
        vector = {free_index: Fraction(1)}
        for pivot in sorted(pivots, reverse=True):
            value = -sum(entry * vector.get(j, 0) for j, entry in pivots[pivot].items() if j != pivot)
            if value:
                vector[pivot] = value
        basis.append(vector)
    return basis


def primitive_integer(vector):
    denominator = math.lcm(*(value.denominator for value in vector.values()))
    result = {i: int(value * denominator) for i, value in vector.items()}
    gcd = math.gcd(*result.values())
    result = {i: value // gcd for i, value in result.items()}
    if result[min(result)] < 0:
        result = {i: -value for i, value in result.items()}
    return result


def add_independent(vector, pivots):
    row = {i: Fraction(value) for i, value in vector.items()}
    while row:
        pivot = min(row)
        value = row[pivot]
        if pivot not in pivots:
            pivots[pivot] = {j: entry / value for j, entry in row.items()}
            return True
        for j, entry in pivots[pivot].items():
            row[j] = row.get(j, Fraction()) - value * entry
            if not row[j]:
                del row[j]
    return False


def annihilates(vector, columns):
    return all(sum(value * column.get(i, 0) for i, value in vector.items()) == 0 for column in columns)


def build_source_general_conservation(species, columns):
    pivots = echelon_rows(columns)
    raw = nullspace_basis(pivots, len(species))
    selected, labels, independent = [], [], {}
    # Name-derived pools are candidates only. Stoichiometric annihilation is
    # checked before a label can enter the mathematical basis.
    for token in POOL_TOKENS:
        candidate = {i: 1 for i, name in enumerate(species) if token in name}
        if candidate and annihilates(candidate, columns) and add_independent(candidate, independent):
            selected.append(candidate)
            labels.append((token + "_named_pool", "LOW_CONFIDENCE"))
    for vector in sorted(raw, key=lambda item: (len(item), tuple(sorted(item)))):
        candidate = primitive_integer(vector)
        if add_independent(candidate, independent):
            selected.append(candidate)
            labels.append(("", "UNASSIGNED"))
    assert len(selected) == len(raw) == len(species) - len(pivots)
    assert all(annihilates(vector, columns) for vector in selected)
    return len(pivots), selected, labels


def build_reference_active_conservation(species, active_columns, source_basis):
    pivots = echelon_rows(active_columns)
    raw = nullspace_basis(pivots, len(species))
    independent = {}
    for vector in source_basis:
        assert annihilates(vector, active_columns)
        assert add_independent(vector, independent)
    extra = []
    for vector in sorted(raw, key=lambda item: (len(item), tuple(sorted(item)))):
        candidate = primitive_integer(vector)
        if add_independent(candidate, independent):
            extra.append(candidate)
    assert len(source_basis) + len(extra) == len(raw) == len(species) - len(pivots)
    assert all(annihilates(vector, active_columns) for vector in extra)
    return len(pivots), extra


def species_classes():
    detail = (OUT / "species_information_contract_detailed.md").read_text(encoding="utf-8")
    pattern = re.compile(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*(I|II-A|II-B|III|C)\*\*\s*\|", re.M)
    classes = dict(pattern.findall(detail))
    source_ids = {row["species_id"] for row in read(ROOT / "models/pnas2017_full_reference/audit/species_reduction_map.csv")}
    assert len(classes) == 241 and set(classes) == source_ids
    return classes


def law_records(species, initial, classes, source_rank, active_rank, source_basis, labels, extra):
    records = []
    all_laws = [("SOURCE_GENERAL", vector, label) for vector, label in zip(source_basis, labels)]
    all_laws += [("FROZEN_REFERENCE_ONLY", vector, ("", "UNASSIGNED")) for vector in extra]
    for index, (scope, vector, (label, label_confidence)) in enumerate(all_laws, 1):
        name = f"CONS_{index:03d}"
        coefficients = {species[i]: value for i, value in sorted(vector.items())}
        constant = sum(value * initial[species[i]] for i, value in vector.items())
        classes_touched = {classes[species[i]] for i in vector}
        records.append(dict(conservation_id=name, scope=scope,
                            species_coefficients_json=json.dumps(coefficients, sort_keys=True, separators=(",", ":")),
                            species_ids=";".join(sorted(coefficients)),
                            support_size=len(vector), constant_initial=fmt(constant),
                            exact_rank_certificate=f"rank(S_source)={source_rank};rank(S_active)={active_rank};exact_fraction_echelon",
                            exact_nullspace_certificate=f"primitive_integer_vector;independent_basis_member;scope={scope}",
                            proof_residual_exact="0", biological_label_candidate=label,
                            label_confidence=label_confidence,
                            touches_class_I=str("I" in classes_touched).lower(),
                            touches_class_II_A=str("II-A" in classes_touched).lower(),
                            touches_class_II_B=str("II-B" in classes_touched).lower(),
                            touches_class_III=str("III" in classes_touched).lower(),
                            touches_class_C=str("C" in classes_touched).lower(),
                            notes="Exact algebraic law; no coordinate elimination or kinetic approximation approved."))
    return records


def assign_deterministic_confidence(law, coefficient_count):
    if law["scope"] == "SOURCE_GENERAL" and law["biological_label_candidate"] and coefficient_count <= 16:
        return "MEDIUM_EXACT", "Multiple exact coordinate choices; name-derived pool label."
    if law["scope"] == "FROZEN_REFERENCE_ONLY" and coefficient_count == 1:
        return "MEDIUM_EXACT", "Single coordinate is constant only under frozen reference."
    return "LOW_CONFIDENCE", "Mixed or broad pool interpretation, coordinate choice, or frozen-only scope requires researcher selection."


def enumerate_elimination_candidates(laws, classes):
    candidates, queue = [], []
    count = 0
    for law in laws:
        coefficients = {name: int(value) for name, value in json.loads(law["species_coefficients_json"]).items()}
        confidence, reason = assign_deterministic_confidence(law, len(coefficients))
        for eliminated in sorted(coefficients):
            count += 1
            coefficient = coefficients[eliminated]
            remainder = " - ".join(f"({value})*{name}" for name, value in sorted(coefficients.items()) if name != eliminated)
            formula = f"{eliminated} = ({law['constant_initial']}" + (f" - {remainder}" if remainder else "") + f")/({coefficient})"
            cls = classes[eliminated]
            candidates.append(dict(candidate_id=f"ELIM_{count:04d}", conservation_id=law["conservation_id"],
                                   eliminated_species=eliminated, species_information_class=cls,
                                   reconstruction_type="CONSERVATION_LINEAR_EXACT", reconstruction_formula=formula,
                                   scope=law["scope"],
                                   protected_output_effect="EXACT_CLASS_I_TRAJECTORY_RECONSTRUCTION" if cls == "I" else "ALL_CLASS_I_OUTPUTS_RETAINED",
                                   information_loss="NONE", exact_reconstructable="true",
                                   choice_ambiguity=str(len(coefficients) > 1).lower(),
                                   confidence=confidence, candidate_status="CODE_VERIFIED_EXACT_CANDIDATE",
                                   human_review_required=str(confidence == "LOW_CONFIDENCE").lower(), reason=reason))
        if confidence == "LOW_CONFIDENCE":
            affected = ";".join(sorted(coefficients))
            queue.append(dict(review_id=f"RREV_{len(queue)+1:03d}", audit_type="CONSERVATION_COORDINATE_CHOICE",
                              affected_ids=law["conservation_id"] + ":" + affected,
                              mechanistic_context=law["biological_label_candidate"] or "unassigned exact mathematical pool",
                              automatic_result="Exact conservation basis member; all listed single-coordinate alternatives reconstructable",
                              confidence=confidence, why_low_confidence=reason,
                              exact_facts=f"scope={law['scope']};support={len(coefficients)};residual=0",
                              unresolved_scientific_choice="Select biologically useful retained observables and interpret pool membership; do not infer QSSA.",
                              recommended_human_question="Which exactly reconstructable coordinate, if any, is appropriate to eliminate while retaining protected outputs?"))
    return candidates, queue


def write_audit_artifacts(species, reactions, annotation, channels, paired, columns,
                          zero_rows, source_rank, active_rank, source_basis, labels,
                          additional_basis, initial, rhs_error, trajectory_error):
    classes = species_classes()
    laws = law_records(species, initial, classes, source_rank, active_rank,
                       source_basis, labels, additional_basis)
    candidates, queue = enumerate_elimination_candidates(laws, classes)
    by_id = {r["id"]: r for r in reactions}
    reverse_rows = []
    for index, (forward, reverse) in enumerate(channels, 1):
        fid, rid = forward["id"], reverse["id"]
        ann = annotation[fid]
        def equation(reaction):
            return " + ".join(reaction["reactants"]) + " -> " + " + ".join(reaction["products"])
        reverse_rows.append(dict(reversible_channel_id=f"RCH_{index:03d}",
                                 forward_reaction_id=fid, reverse_reaction_id=rid,
                                 forward_equation=equation(forward), reverse_equation=equation(reverse),
                                 forward_kinetic_law=forward["formula"], reverse_kinetic_law=reverse["formula"],
                                 forward_k=fmt(forward["k"]), reverse_k=fmt(reverse["k"]),
                                 vf_definition=f"({fmt(forward['k'])}) * " + " * ".join(x for x in forward["factors"] if x != "k1"),
                                 vr_definition=f"({fmt(reverse['k'])}) * " + " * ".join(x for x in reverse["factors"] if x != "k1"),
                                 functional_contexts=ann["level_c_functional_contexts"],
                                 reaction_family_id=ann["reaction_family_id"],
                                 cross_family_link_ids=ann["cross_family_link_ids"],
                                 stoich_exact_negative="true", reactant_product_exact_swap="true",
                                 vf_retained="true", vr_retained="true", vnet_definition="v_forward - v_reverse",
                                 gross_ledger_recoverable="true", rhs_identity_status="EXACT_STOICHIOMETRIC_IDENTITY",
                                 confidence="HIGH_EXACT",
                                 evidence="canonical source stoichiometry and MathML; both directed fluxes/parameters retained"))
    active_rows = [dict(reaction_id=r["id"], frozen_reference_flux_status="IDENTICALLY_ZERO_PROVED" if r["k"] == 0 else "ACTIVE_OR_STATE_DEPENDENT",
                        active_rhs_included=str(r["k"] != 0).lower(),
                        source_reaction_retained="true", official_parameter_value=fmt(r["k"]),
                        functional_contexts=annotation[r["id"]]["level_c_functional_contexts"])
                   for r in reactions]
    files = {
        "exact_reverse_channels_v0.csv": reverse_rows,
        "conservation_laws_v0.csv": laws,
        "conservation_elimination_candidates_v0.csv": candidates,
        "reference_zero_reactions_v0.csv": zero_rows,
        "reference_active_view_v0.csv": active_rows,
        "low_confidence_reduction_review_queue_v0.csv": queue,
    }
    fields = {
        "exact_reverse_channels_v0.csv": ["reversible_channel_id", "forward_reaction_id", "reverse_reaction_id", "forward_equation", "reverse_equation", "forward_kinetic_law", "reverse_kinetic_law", "forward_k", "reverse_k", "vf_definition", "vr_definition", "functional_contexts", "reaction_family_id", "cross_family_link_ids", "stoich_exact_negative", "reactant_product_exact_swap", "vf_retained", "vr_retained", "vnet_definition", "gross_ledger_recoverable", "rhs_identity_status", "confidence", "evidence"],
        "conservation_laws_v0.csv": ["conservation_id", "scope", "species_coefficients_json", "species_ids", "support_size", "constant_initial", "exact_rank_certificate", "exact_nullspace_certificate", "proof_residual_exact", "biological_label_candidate", "label_confidence", "touches_class_I", "touches_class_II_A", "touches_class_II_B", "touches_class_III", "touches_class_C", "notes"],
        "conservation_elimination_candidates_v0.csv": ["candidate_id", "conservation_id", "eliminated_species", "species_information_class", "reconstruction_type", "reconstruction_formula", "scope", "protected_output_effect", "information_loss", "exact_reconstructable", "choice_ambiguity", "confidence", "candidate_status", "human_review_required", "reason"],
        "reference_zero_reactions_v0.csv": ["reaction_id", "reaction_family_id", "functional_contexts", "cross_family_link_ids", "reaction_equation", "official_parameter_name", "official_parameter_value", "kinetic_law", "zero_flux_proof", "zero_class", "reverse_partner_id", "partner_parameter_value", "pair_zero_pattern", "scope", "source_provenance", "active_rhs_treatment", "confidence", "human_review_required", "reason"],
        "reference_active_view_v0.csv": ["reaction_id", "frozen_reference_flux_status", "active_rhs_included", "source_reaction_retained", "official_parameter_value", "functional_contexts"],
        "low_confidence_reduction_review_queue_v0.csv": ["review_id", "audit_type", "affected_ids", "mechanistic_context", "automatic_result", "confidence", "why_low_confidence", "exact_facts", "unresolved_scientific_choice", "recommended_human_question"],
    }
    for name, rows in files.items():
        write(OUT / name, rows, fields[name])
    zero_counts = dict(sorted(Counter(r["zero_class"] for r in zero_rows).items()))
    pattern_counts = {name: sum(r["pair_zero_pattern"] == name for r in zero_rows)
                      for name in ("BIDIRECTIONAL_ZERO", "ONLY_FORWARD_ZERO", "ONLY_REVERSE_ZERO", "UNPAIRED_ZERO")}
    candidate_counts = {name: sum(r["confidence"] == name for r in candidates)
                        for name in ("HIGH_EXACT", "MEDIUM_EXACT", "LOW_CONFIDENCE")}
    inputs = [SBML, COMPAT, EFFECTIVE, AUTHOR / "fMGG_synthesis_parameters.csv",
              AUTHOR / "fMGG_synthesis_initial_values.csv",
              OUT / "reaction_level_annotation_v2.csv", OUT / "reaction_family_summary_v2.csv",
              OUT / "reaction_cross_family_links_v2.csv", OUT / "reduction_decisions.csv",
              OUT / "species_information_contract_detailed.md",
              ROOT / "models/pnas2017_full_reference/audit/species_reduction_map.csv",
              ROOT / "models/pnas2017_full_reference/audit/reactions.csv",
              ROOT / "models/pnas2017_full_reference/audit/reaction_balance_audit.csv"]
    manifest = dict(schema_version="0.1", status="R1_R2_AUTOMATED_AUDIT_EXACT_CANDIDATES_NOT_REDUCTION_APPROVAL",
                    source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
                    artifact_sha256={name: sha(OUT / name) for name in files},
                    source_species=241, source_reactions=968, exact_reverse_channels=len(channels),
                    directed_reactions_in_reverse_channels=len(paired),
                    reverse_representation=dict(symbolic_exact=True, scaled_rhs_max_error=rhs_error,
                                                tolerance=1e-12, representative_channel="re0000000457/re0000000458",
                                                trajectory_max_error=trajectory_error, trajectory_tolerance=1e-6,
                                                gross_directed_fluxes_retained=True),
                    source_general_rank=source_rank, source_general_conservation_dimension=len(source_basis),
                    sparse_named_pool_laws=sum(bool(label[0]) for label in labels),
                    frozen_reference_active_rank=active_rank,
                    frozen_reference_additional_invariants=len(additional_basis),
                    exact_elimination_candidate_counts=candidate_counts,
                    frozen_reference_zero_reactions=len(zero_rows), zero_classes=zero_counts,
                    zero_pair_patterns=pattern_counts, reference_active_reactions=968-len(zero_rows),
                    zero_pair_channel_counts=dict(bidirectional_zero_pairs=pattern_counts["BIDIRECTIONAL_ZERO"] // 2,
                                                  only_forward_zero_pairs=pattern_counts["ONLY_FORWARD_ZERO"],
                                                  only_reverse_zero_pairs=pattern_counts["ONLY_REVERSE_ZERO"],
                                                  unpaired_zero_reactions=pattern_counts["UNPAIRED_ZERO"]),
                    low_confidence_review_queue=len(queue),
                    reduction_decisions_pending=968,
                    scientific_boundary="R1/R2 exact audit only; no QSSA, fast equilibrium, lumping, effective kinetics, deletion, or final reduced model approved.")
    with (OUT / "reduction_audit_manifest_v0.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    priority = sorted(queue, key=lambda item: -int(item["exact_facts"].split("support=")[1].split(";")[0]))[:3]
    priority_lines = "\n".join(f"- `{item['affected_ids'].split(':', 1)[0]}`: {item['exact_facts']}; "
                               "researcher must choose a useful observable/pool interpretation."
                               for item in priority)
    summary = f"""# PNAS2017 R1/R2 exact reduction audit v0

This is an automated audit of exact representations and the frozen fMGG
reference. It is **not** a reduced model or scientific reduction approval.

| Finding | Result |
| --- | ---: |
| Source reactions / species | 968 / 241 |
| Exact reverse channels | {len(channels)} (580 directed reactions) |
| Source-general exact rank / conservation dimension | {source_rank} / {len(source_basis)} |
| Verified name-derived sparse pool laws in source basis | {manifest['sparse_named_pool_laws']} |
| Frozen-reference active rank | {active_rank} |
| Additional frozen-reference-only invariants | {len(additional_basis)} |
| Exact elimination alternatives: HIGH / MEDIUM / LOW | {candidate_counts['HIGH_EXACT']} / {candidate_counts['MEDIUM_EXACT']} / {candidate_counts['LOW_CONFIDENCE']} |
| Frozen-reference identically-zero directed reactions | {len(zero_rows)} |
| Reference-active directed reactions | {968-len(zero_rows)} |
| Low-confidence human review items (grouped by law) | {len(queue)} |

Zero classes: {json.dumps(zero_counts, sort_keys=True)}. Directed zero-flux
patterns: {json.dumps(pattern_counts, sort_keys=True)}. A single-zero reverse
channel retains its active direction. The 32 bidirectionally zero directed
reactions form 16 channels; 65 channels have only the reverse direction zero,
none has only the forward direction zero, and 388 zero reactions are unpaired.
The 388 zero-rate degradation reactions
remain in the source and in the accounting schema; they are excluded only
from the frozen-reference active RHS and become available if parameters change.

The reverse-channel alternative retains both directed source kinetic laws,
official parameters, reaction IDs, `v_forward` and `v_reverse`. It uses
`v_net = v_forward - v_reverse` only for the net RHS. Gross ATP/GTP/phosphate,
tRNA, amino-acid and ribosomal-subunit ledgers continue to use the directed
fluxes. Exact stoichiometric identity is established for all 290 channels;
the scaled numerical RHS check was {rhs_error:.3g} (limit 1e-12), and the
representative source-initialized trajectory difference was
{trajectory_error:.3g} (numerical limit 1e-6). These numerical limits check
implementation, not scientific approximation.

The conservation basis uses exact rational row reduction. Each source-general
law annihilates all 968 source columns; each additional frozen-reference law
annihilates only the proven-active columns. Biological labels are name-derived
candidates and may remain unassigned. Elimination entries are **one-at-a-time
alternatives**: each formula reconstructs its coordinate exactly if every
other coordinate in that law is retained. No simultaneous eliminated set is
selected. Class-I observables require exact reconstruction in any later
implementation. The human queue asks for pool interpretation and coordinate
choice, not for a code-level nullspace calculation.

The largest low-confidence pool supports are listed as a deterministic review
triage heuristic, not a scientific priority or approval:

{priority_lines}

`reduction_decisions.csv` remains **968 / 968 PENDING**. Functional annotation
v2 is unchanged and supplies mechanistic context only. R3 QSSA, R4 functional
pool lumping, R5 effective kinetics, and all later approximate or final model
decisions remain deferred.
"""
    (OUT / "reduction_audit_v0_summary.md").write_text(summary, encoding="utf-8", newline="\n")
    method = """# R1/R2 exact audit v0 method

## Evidence levels and source

`SOURCE_GENERAL` is an identity for every allowed state and parameter value
in the unchanged canonical SBML stoichiometry. `FROZEN_REFERENCE_ONLY` is
strictly conditional on the author fMGG simulation parameter CSV. Anything
requiring timescale separation, QSSA, fast equilibrium, fitting or a change
of effective kinetic law is deferred to R3–R5 and is not approved here.

The canonical combined SBML MathML is parsed directly. Each of its 968 rate
expressions is one multiplication of constant local `k1` and species factors.
The normalized execution-compatibility copy has identical rate factors,
local parameter semantics and exact stoichiometry. The recorded effective
author-condition SBML also has identical kinetic logic and reaction sides,
with each local `k1` equal to the author CSV. There are no assignment
rules, events, initial assignments or piecewise bypasses. Author parameter
names map one-to-one to `<reaction_id>_k1`; the author initial-value CSV sets
the constants for conservation laws. The model's default local `k1=1` is
not confused with the frozen author parameter override.

## R1 exact reverse representation

Exact reactant/product swap and exact negative stoichiometric columns are
checked independently of functional annotation. Every directed reaction can
enter at most one of 290 channels. `S_f*v_f + S_r*v_r = S_f*(v_f-v_r)` is
algebraically exact because `S_r=-S_f`. The alternative keeps `v_f`, `v_r`,
both source reaction IDs, both kinetic laws and both parameters; gross
resource accounting must use the directed fluxes, never `abs(v_net)`.
Random-state and source-initial RHS comparisons and one source-initialized
channel trajectory are numerical implementation checks only. A reverse pair
does not imply fast equilibrium or a `k_f/k_r` equilibrium constant.

## R1 exact conservation and candidate reconstruction

Stoichiometric coefficients are parsed as rational values, including literal
`stoichiometryMath`. Exact Fraction echelon reduction computes the rank of
all 968 columns and, separately, only columns whose frozen flux is not
identically zero. Candidate name-derived factor pools enter a basis only
when their integer vector exactly annihilates S and increases basis rank;
the remainder comes from the exact nullspace. The additional reference-only
vectors extend the source-general basis to the active-network nullspace.

Every reported law has an exact zero residual. Each elimination formula
solves one nonzero coefficient of a law with all other coordinates retained.
Alternatives must not be combined without a separate independence proof.
`HIGH_EXACT` requires an unambiguous source-general choice; none is selected
automatically. `MEDIUM_EXACT` is assigned deterministically to a source-
general named pool of support at most 16 or a frozen-reference singleton.
Other broad, mixed or interpretation-dependent laws are `LOW_CONFIDENCE` and
enter a law-level human queue. All candidates remain code-verified proposals.

## R2 frozen-reference zero flux

Only a zero author parameter that is a direct factor of the complete source
MathML product, constant locally and unmodified by rules/events, proves
`v_j(x)=0` for all x under the frozen reference. The compatibility copy is
checked for the same kinetic logic. Proven-zero directed reactions are marked
`EXCLUDED_FROM_FROZEN_REFERENCE_ACTIVE_RHS`, never deleted from source.
Single-zero channels retain their nonzero direction. Degradation cumulative
accounting and source provenance remain available for parameter changes.
`REFERENCE_ZERO_SIDE_PATH` is reserved for the eight explicitly reviewed
elongation side-path directions; other bidirectionally zero pairs are
`REFERENCE_ZERO_OTHER` unless their source role is separately established.

The species information contract and functional annotation supply output
requirements and mechanistic context; neither is used as kinetic reduction
evidence. Class I may be an algebraically reconstructed output. Class II-A
does not authorize QSSA. No final coordinate system or reduced RHS is built.
"""
    (OUT / "reduction_audit_v0_method.md").write_text(method, encoding="utf-8", newline="\n")
    manifest["artifact_sha256"].update({name: sha(OUT / name) for name in ("reduction_audit_v0_summary.md", "reduction_audit_v0_method.md")})
    with (OUT / "reduction_audit_manifest_v0.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def main():
    species, reactions, annotation, initial = load_source_network()
    columns = build_exact_stoichiometry(species, reactions)
    channels, paired = find_reverse_channels(reactions, columns, annotation)
    rhs_error, trajectory_error = prove_reverse_representation(species, reactions, columns,
                                                               channels, paired, initial)
    zero_rows = find_zero_flux_reactions(reactions, channels, annotation)
    zero_ids = {row["reaction_id"] for row in zero_rows}
    assert zero_ids == {r["id"] for r in reactions if r["k"] == 0}
    active_columns = [col for reaction, col in zip(reactions, columns) if reaction["id"] not in zero_ids]
    source_rank, source_basis, labels = build_source_general_conservation(species, columns)
    active_rank, additional_basis = build_reference_active_conservation(species, active_columns, source_basis)
    assert source_rank == 214 and active_rank == 177, (source_rank, active_rank)
    assert len(source_basis) == 27 and len(additional_basis) == 37
    assert len(zero_rows) == 485
    decisions = read(OUT / "reduction_decisions.csv")
    assert len(decisions) == 968 and all(row["decision_status"] == "PENDING" for row in decisions)
    manifest = write_audit_artifacts(species, reactions, annotation, channels, paired, columns,
                                     zero_rows, source_rank, active_rank, source_basis, labels,
                                     additional_basis, initial, rhs_error, trajectory_error)
    print(json.dumps({key: manifest[key] for key in (
        "source_species", "source_reactions", "exact_reverse_channels",
        "source_general_rank", "source_general_conservation_dimension",
        "sparse_named_pool_laws", "frozen_reference_active_rank",
        "frozen_reference_additional_invariants", "exact_elimination_candidate_counts",
        "frozen_reference_zero_reactions", "zero_classes", "zero_pair_patterns",
        "low_confidence_review_queue", "reduction_decisions_pending")}, indent=2))


if __name__ == "__main__":
    main()
