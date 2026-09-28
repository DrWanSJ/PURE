#!/usr/bin/env python3
"""Independently verify exact R1/R2 audit artifacts against canonical SBML."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/reduction"
SOURCE = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
COMPAT = ROOT / "models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml"
EFFECTIVE = ROOT / "results/pnas2017_reference/rr_cvode_author_csv_20260924/effective_author_conditions.xml"
AUTHOR = ROOT / "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat"
S = "{http://www.sbml.org/sbml/level2/version4}"
M = "{http://www.w3.org/1998/Math/MathML}"
SOURCE_SHA = "dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df"
FUNCTIONAL_SHA = {
    "docs/reduction/reaction_level_annotation_v2.csv": "ee2f80a3354199a03d3072464cbc301736afad72fba01e4bfcc499c0525f3335",
    "docs/reduction/reaction_family_summary_v2.csv": "228ce72fe99b54fc8be69ccca8f94e9892d1f8f53b370c0891c144447477e695",
    "docs/reduction/reaction_cross_family_links_v2.csv": "7d3551b04a1c7f2a229fec6f2e3656db45da7836c34925f6cb690f85d4b28a50",
    "docs/reduction/human_functional_review_queue_v2.csv": "7833cee3bd229ed9f5979224dd3368acf09a5db63435ecd70a603daa47a42bc2",
    "docs/reduction/reaction_annotation_manifest_v2.json": "e8246502a2e5a012c223e345182556f63a98e04b9281dd537de742eb4602439f",
    "docs/reduction/reaction_annotation_method_v2.md": "22e9fb93bdf8833af6d229426bc216f5ae3e981cfdcc2993ed158607e9247bfc",
    "docs/reduction/reaction_annotation_summary_v2.md": "007b72db9f45dd7c4b1feb1d288e0455202f9ee3376a3462de586640776644fd",
    "scripts/build_reaction_level_annotation_v2.py": "10f57e5424b628ecf5395ca9f9adf6990b676a5921826ac99fe8239ecfe5d00d",
    "scripts/verify_reaction_level_annotation_v2.py": "528803bf3b83759794445275f3462658f7957d8c44cd1532095e76fbc3a8c0e4",
}
RESOURCE = {"ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr",
            "Gly", "Met", "fMet", "tRNAGlyGCC", "tRNAfMetCAU", "GlytRNAGlyGCC",
            "MettRNAfMetCAU", "fMettRNAfMetCAU", "RS30S", "RS50S", "RS70S"}
APPROVED_SIDE_PATHS = {f"re{number:010d}" for number in (26, 27, 63, 64, 87, 88, 121, 122)}


def rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_text_digest(path):
    """Hash tracked text independent of Git's checkout newline setting."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def fraction(value):
    return Fraction(str(value).strip())


def parse(path):
    model = ET.parse(path).getroot().find(S + "model")
    assert model is not None
    for forbidden in ("listOfRules", "listOfEvents", "listOfInitialAssignments", "listOfFunctionDefinitions"):
        node = model.find(S + forbidden)
        assert node is None or len(node) == 0
    species = [node.attrib["id"] for node in model.find(S + "listOfSpecies").findall(S + "species")]
    assert len(species) == len(set(species)) == 241
    names = set(species)
    reactions = []
    for node in model.find(S + "listOfReactions").findall(S + "reaction"):
        sides = []
        for key in ("listOfReactants", "listOfProducts"):
            parent = node.find(S + key)
            side = {}
            for ref in parent.findall(S + "speciesReference") if parent is not None else []:
                sid = ref.attrib["species"]
                math = ref.find(S + "stoichiometryMath")
                if math is None:
                    value = fraction(ref.attrib.get("stoichiometry", "1"))
                else:
                    children = list(math.find(M + "math"))
                    assert len(children) == 1 and children[0].tag == M + "cn"
                    value = fraction(children[0].text)
                assert sid not in side and value > 0
                side[sid] = value
            sides.append(side)
        law = node.find(S + "kineticLaw")
        assert law is not None
        params = law.find(S + "listOfParameters")
        assert params is not None and len(params) == 1
        param = params[0].attrib
        assert param["id"] == "k1" and param.get("constant") == "true" and param.get("units") == "substance"
        math = law.find(M + "math")
        assert math is not None and len(math) == 1
        apply = math[0]
        assert apply.tag == M + "apply" and apply[0].tag == M + "times"
        assert all(term.tag == M + "ci" for term in apply[1:])
        factors = [term.text.strip() for term in apply[1:]]
        assert factors.count("k1") == 1 and all(x == "k1" or x in names for x in factors)
        reactions.append(dict(id=node.attrib["id"], reactants=sides[0], products=sides[1],
                              factors=factors, parameter=param))
    assert len(reactions) == len({r["id"] for r in reactions}) == 968
    return species, reactions


def source_network():
    assert digest(SOURCE) == SOURCE_SHA
    species, reactions = parse(SOURCE)
    compat_species, compatible = parse(COMPAT)
    assert species == compat_species
    for left, right in zip(reactions, compatible):
        assert all(left[k] == right[k] for k in ("id", "reactants", "products", "factors", "parameter")), left["id"]
    parameters = {row["Name"]: fraction(row["Value"]) for row in rows(AUTHOR / "fMGG_synthesis_parameters.csv")}
    assert set(parameters) == {r["id"] + "_k1" for r in reactions} | {"default"}
    effective_species, effective = parse(EFFECTIVE)
    assert species == effective_species
    initial = {row["Name"]: fraction(row["Value"]) for row in rows(AUTHOR / "fMGG_synthesis_initial_values.csv")}
    assert set(initial) == set(species)
    balance = {row["sbml_reaction_id"]: row for row in rows(ROOT / "models/pnas2017_full_reference/audit/reaction_balance_audit.csv")}
    inventory = {row["reaction_id"]: row for row in rows(ROOT / "models/pnas2017_full_reference/audit/reactions.csv")}
    assert set(balance) == set(inventory) == {r["id"] for r in reactions}
    for reaction, imported in zip(reactions, effective):
        rid = reaction["id"]
        reaction["k"] = parameters[rid + "_k1"]
        assert all(reaction[key] == imported[key] for key in ("id", "reactants", "products", "factors"))
        assert fraction(imported["parameter"]["value"]) == reaction["k"]
        assert reaction["k"] == fraction(balance[rid]["official_parameter_value"])
        assert balance[rid]["official_parameter_id"] == rid + "_k1"
        assert " * ".join(reaction["factors"]) == inventory[rid]["kinetic_law_formula"]
        for key, side in (("reactants_json", reaction["reactants"]), ("products_json", reaction["products"])):
            from_inventory = {x["species_id"]: fraction(x["stoichiometry"]) for x in json.loads(inventory[rid][key])}
            assert side == from_inventory, (rid, key)
    return species, reactions, initial


def columns(species, reactions):
    index = {name: i for i, name in enumerate(species)}
    result = []
    for reaction in reactions:
        col = Counter()
        for name, value in reaction["products"].items():
            col[index[name]] += value
        for name, value in reaction["reactants"].items():
            col[index[name]] -= value
        result.append({i: value for i, value in col.items() if value})
    return result


def reverse_pairs(reactions, stoich):
    def sig(side):
        return tuple(sorted(side.items()))
    by_sides = {}
    for reaction in reactions:
        by_sides.setdefault((sig(reaction["reactants"]), sig(reaction["products"])), []).append(reaction["id"])
    id_index = {r["id"]: i for i, r in enumerate(reactions)}
    pairs, used = [], set()
    for reaction in reactions:
        rid = reaction["id"]
        if rid in used:
            continue
        others = [x for x in by_sides.get((sig(reaction["products"]), sig(reaction["reactants"])), []) if x != rid]
        assert len(others) <= 1, (rid, others)
        if others:
            other = others[0]
            assert other not in used
            first, second = sorted((rid, other))
            c1, c2 = stoich[id_index[first]], stoich[id_index[second]]
            assert c1 == {i: -v for i, v in c2.items()}
            pairs.append((first, second))
            used.update((first, second))
    assert len(pairs) == 290 and len(used) == 580
    return pairs


def exact_rank(vectors):
    # Independent fraction elimination with highest-index pivots.
    pivots = {}
    for vector in vectors:
        row = dict(vector)
        while row:
            pivot = max(row)
            value = row[pivot]
            if pivot not in pivots:
                pivots[pivot] = {i: entry / value for i, entry in row.items()}
                break
            for i, entry in pivots[pivot].items():
                row[i] = row.get(i, Fraction()) - value * entry
                if not row[i]:
                    del row[i]
    return len(pivots)


def annihilates(vector, stoich):
    return all(sum(value * column.get(i, 0) for i, value in vector.items()) == 0 for column in stoich)


def numeric_rhs(species, reactions, stoich, pairs, state, alternative):
    by_id = {r["id"]: (r, col) for r, col in zip(reactions, stoich)}
    rates = {}
    for reaction in reactions:
        value = float(reaction["k"])
        for factor in reaction["factors"]:
            if factor != "k1":
                value *= state[factor]
        rates[reaction["id"]] = value
    result = [0.0] * len(species)
    if alternative:
        used = set()
        for first, second in pairs:
            used.update((first, second))
            for i, value in by_id[first][1].items():
                result[i] += float(value) * (rates[first] - rates[second])
        items = [(r, col) for r, col in zip(reactions, stoich) if r["id"] not in used]
    else:
        items = list(zip(reactions, stoich))
    for reaction, col in items:
        for i, value in col.items():
            result[i] += float(value) * rates[reaction["id"]]
    return result


def channel_trajectory_error(reactions, initial):
    pair = [next(r for r in reactions if r["id"] == rid) for rid in ("re0000000457", "re0000000458")]
    names = sorted(set(pair[0]["reactants"]) | set(pair[0]["products"]))
    direct = {name: float(initial[name]) for name in names}
    merged = dict(direct)

    def rate(reaction, state):
        value = float(reaction["k"])
        for factor in reaction["factors"]:
            if factor != "k1":
                value *= state[factor]
        return value

    def step(state, alternative):
        def derivative(current):
            vf, vr = [rate(reaction, current) for reaction in pair]
            return {name: float(pair[0]["products"].get(name, 0) - pair[0]["reactants"].get(name, 0)) *
                    ((vf - vr) if alternative else vf) +
                    (0 if alternative else float(pair[1]["products"].get(name, 0) - pair[1]["reactants"].get(name, 0)) * vr)
                    for name in names}
        dt = 0.01
        k1 = derivative(state)
        k2 = derivative({n: state[n] + dt*k1[n]/2 for n in names})
        k3 = derivative({n: state[n] + dt*k2[n]/2 for n in names})
        k4 = derivative({n: state[n] + dt*k3[n] for n in names})
        return {n: state[n] + dt*(k1[n] + 2*k2[n] + 2*k3[n] + k4[n])/6 for n in names}

    error = 0.0
    for _ in range(100):
        direct, merged = step(direct, False), step(merged, True)
        error = max(error, *(abs(direct[name] - merged[name]) for name in names))
    return error


def verify_invariants():
    manifest = json.loads((OUT / "reduction_audit_manifest_v0.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "R1_R2_AUTOMATED_AUDIT_EXACT_CANDIDATES_NOT_REDUCTION_APPROVAL"
    for name, expected in manifest["source_sha256"].items():
        assert digest(ROOT / name) == expected, name
    for name, expected in manifest["artifact_sha256"].items():
        assert digest(OUT / name) == expected, name
    for name, expected in FUNCTIONAL_SHA.items():
        assert canonical_text_digest(ROOT / name) == expected, f"functional annotation changed: {name}"
    decisions_path = OUT / "reduction_decisions.csv"
    assert digest(decisions_path) == "70fd3f98de5056a1a63c29db58d310ec5986d4c52b6bfcbae9634b38e2e8d7f8"
    decisions = rows(decisions_path)
    assert len(decisions) == 968 and all(r["decision_status"] == "PENDING" for r in decisions)
    assert not any(token in field.lower() for field in decisions[0] for token in
                   ("qssa_approved", "fast_eq_approved", "drop_approved", "lump_approved", "reduced_kinetics_approved"))
    species, reactions, initial = source_network()
    stoich = columns(species, reactions)
    by_id = {r["id"]: r for r in reactions}
    id_index = {r["id"]: i for i, r in enumerate(reactions)}
    assert {r["sbml_reaction_id"] for r in decisions} == set(by_id)
    pairs = reverse_pairs(reactions, stoich)
    reverse = rows(OUT / "exact_reverse_channels_v0.csv")
    assert {(r["forward_reaction_id"], r["reverse_reaction_id"]) for r in reverse} == set(pairs)
    assert len(reverse) == manifest["exact_reverse_channels"] == 290
    resource_indices = {i for i, name in enumerate(species) if name in RESOURCE}
    for row in reverse:
        first, second = row["forward_reaction_id"], row["reverse_reaction_id"]
        f, r = by_id[first], by_id[second]
        assert row["forward_k"] == str(f["k"]) or fraction(row["forward_k"]) == f["k"]
        assert fraction(row["reverse_k"]) == r["k"]
        assert row["forward_kinetic_law"] == " * ".join(f["factors"])
        assert row["reverse_kinetic_law"] == " * ".join(r["factors"])
        assert row["vf_definition"] == f"({row['forward_k']}) * " + " * ".join(x for x in f["factors"] if x != "k1")
        assert row["vr_definition"] == f"({row['reverse_k']}) * " + " * ".join(x for x in r["factors"] if x != "k1")
        assert all(row[k] == "true" for k in ("stoich_exact_negative", "reactant_product_exact_swap", "vf_retained", "vr_retained", "gross_ledger_recoverable"))
        assert row["vnet_definition"] == "v_forward - v_reverse"
        c1, c2 = stoich[id_index[first]], stoich[id_index[second]]
        assert all(c1.get(i, 0) == -c2.get(i, 0) for i in resource_indices)
        assert row["rhs_identity_status"] == "EXACT_STOICHIOMETRIC_IDENTITY"
    rhs_error = 0.0
    for state in [initial] + [{name: Fraction(1, 10) + Fraction(((i+1)*(seed+3))%31, 10)
                               for i, name in enumerate(species)} for seed in (1, 7, 29)]:
        numeric = {name: float(value) for name, value in state.items()}
        direct = numeric_rhs(species, reactions, stoich, pairs, numeric, False)
        merged = numeric_rhs(species, reactions, stoich, pairs, numeric, True)
        scale = max(1.0, *(abs(x) for x in direct), *(abs(x) for x in merged))
        rhs_error = max(rhs_error, max(abs(a-b) for a, b in zip(direct, merged))/scale)
    assert rhs_error <= 1e-12 and manifest["reverse_representation"]["scaled_rhs_max_error"] <= 1e-12
    trajectory_error = channel_trajectory_error(reactions, initial)
    assert trajectory_error <= 1e-6 and manifest["reverse_representation"]["trajectory_max_error"] <= 1e-6
    assert manifest["reverse_representation"]["gross_directed_fluxes_retained"] is True
    zero = rows(OUT / "reference_zero_reactions_v0.csv")
    zero_ids = {r["reaction_id"] for r in zero}
    assert zero_ids == {r["id"] for r in reactions if r["k"] == 0}
    assert len(zero) == manifest["frozen_reference_zero_reactions"] == 485
    partners = {first: second for first, second in pairs} | {second: first for first, second in pairs}
    annotation = {r["reaction_id"]: r for r in rows(OUT / "reaction_level_annotation_v2.csv")}
    for row in zero:
        rid = row["reaction_id"]
        reaction = by_id[rid]
        assert reaction["k"] == 0 and reaction["factors"].count("k1") == 1
        assert row["official_parameter_name"] == rid + "_k1" and fraction(row["official_parameter_value"]) == 0
        assert row["kinetic_law"] == " * ".join(reaction["factors"])
        assert row["functional_contexts"] == annotation[rid]["level_c_functional_contexts"]
        assert row["cross_family_link_ids"] == annotation[rid]["cross_family_link_ids"]
        other = partners.get(rid)
        expected_pattern = "UNPAIRED_ZERO" if other is None else "BIDIRECTIONAL_ZERO" if by_id[other]["k"] == 0 else "ONLY_FORWARD_ZERO" if rid < other else "ONLY_REVERSE_ZERO"
        expected_class = "REFERENCE_ZERO_DEGRADATION" if annotation[rid]["reaction_family_id"] == "RFAM_DEG" else "REFERENCE_ZERO_SIDE_PATH" if rid in APPROVED_SIDE_PATHS else "REFERENCE_ZERO_REVERSE_CHANNEL" if other and by_id[other]["k"] != 0 else "REFERENCE_ZERO_OTHER"
        assert row["pair_zero_pattern"] == expected_pattern and row["zero_class"] == expected_class
        assert row["reverse_partner_id"] == (other or "")
        assert row["scope"] == "FROZEN_REFERENCE_ONLY"
        assert row["active_rhs_treatment"] == "EXCLUDED_FROM_FROZEN_REFERENCE_ACTIVE_RHS"
        assert row["human_review_required"] == "false"
    assert dict(Counter(r["zero_class"] for r in zero)) == manifest["zero_classes"]
    assert {name: sum(r["pair_zero_pattern"] == name for r in zero)
            for name in ("BIDIRECTIONAL_ZERO", "ONLY_FORWARD_ZERO", "ONLY_REVERSE_ZERO", "UNPAIRED_ZERO")} == manifest["zero_pair_patterns"]
    assert manifest["zero_pair_channel_counts"] == {"bidirectional_zero_pairs": 16,
                                                    "only_forward_zero_pairs": 0,
                                                    "only_reverse_zero_pairs": 65,
                                                    "unpaired_zero_reactions": 388}
    active_view = rows(OUT / "reference_active_view_v0.csv")
    assert len(active_view) == len({r["reaction_id"] for r in active_view}) == 968
    for row in active_view:
        rid = row["reaction_id"]
        assert row["active_rhs_included"] == str(rid not in zero_ids).lower()
        assert row["source_reaction_retained"] == "true"
    assert sum(row["active_rhs_included"] == "true" for row in active_view) == manifest["reference_active_reactions"] == 483
    active_columns = [col for reaction, col in zip(reactions, stoich) if reaction["id"] not in zero_ids]
    assert exact_rank(stoich) == manifest["source_general_rank"] == 214
    assert exact_rank(active_columns) == manifest["frozen_reference_active_rank"] == 177
    laws = rows(OUT / "conservation_laws_v0.csv")
    assert len(laws) == 64
    vectors = {}
    source_vectors, all_vectors = [], []
    index = {name: i for i, name in enumerate(species)}
    for law in laws:
        vector = {index[name]: fraction(value) for name, value in json.loads(law["species_coefficients_json"]).items()}
        assert vector and all(value.denominator == 1 for value in vector.values())
        assert law["species_ids"] == ";".join(sorted(species[i] for i in vector))
        assert len(vector) == int(law["support_size"]) and law["proof_residual_exact"] == "0"
        assert law["exact_rank_certificate"] == "rank(S_source)=214;rank(S_active)=177;exact_fraction_echelon"
        assert law["exact_nullspace_certificate"] == f"primitive_integer_vector;independent_basis_member;scope={law['scope']}"
        assert annihilates(vector, active_columns)
        if law["scope"] == "SOURCE_GENERAL":
            assert annihilates(vector, stoich)
            source_vectors.append(vector)
        else:
            assert law["scope"] == "FROZEN_REFERENCE_ONLY" and not annihilates(vector, stoich)
        constant = sum(value * initial[species[i]] for i, value in vector.items())
        assert fraction(law["constant_initial"]) == constant
        if law["biological_label_candidate"]:
            assert law["label_confidence"] == "LOW_CONFIDENCE"
        vectors[law["conservation_id"]] = (law, vector)
        all_vectors.append(vector)
    assert len(source_vectors) == manifest["source_general_conservation_dimension"] == 27
    assert len(all_vectors)-len(source_vectors) == manifest["frozen_reference_additional_invariants"] == 37
    assert exact_rank(source_vectors) == 27 and exact_rank(all_vectors) == 64
    assert sum(bool(r["biological_label_candidate"]) for r in laws if r["scope"] == "SOURCE_GENERAL") == manifest["sparse_named_pool_laws"]
    detail = (OUT / "species_information_contract_detailed.md").read_text(encoding="utf-8")
    classes = dict(re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*(I|II-A|II-B|III|C)\*\*\s*\|", detail, re.M))
    assert len(classes) == 241
    candidates = rows(OUT / "conservation_elimination_candidates_v0.csv")
    assert len(candidates) == sum(int(r["support_size"]) for r in laws)
    for row in candidates:
        law, vector = vectors[row["conservation_id"]]
        name = row["eliminated_species"]
        i = index[name]
        assert i in vector and row["species_information_class"] == classes[name]
        assert row["scope"] == law["scope"] and row["information_loss"] == "NONE"
        assert row["exact_reconstructable"] == "true" and row["candidate_status"] == "CODE_VERIFIED_EXACT_CANDIDATE"
        reconstructed = (fraction(law["constant_initial"]) - sum(value * initial[species[j]] for j, value in vector.items() if j != i)) / vector[i]
        assert reconstructed == initial[name], row["candidate_id"]
        coeffs = {species[j]: int(value) for j, value in vector.items()}
        remainder = " - ".join(f"({value})*{other}" for other, value in sorted(coeffs.items()) if other != name)
        expected_formula = f"{name} = ({law['constant_initial']}" + (f" - {remainder}" if remainder else "") + f")/({int(vector[i])})"
        assert row["reconstruction_formula"] == expected_formula, row["candidate_id"]
        assert row["choice_ambiguity"] == str(len(vector) > 1).lower()
        expected_confidence = "MEDIUM_EXACT" if law["scope"] == "SOURCE_GENERAL" and law["biological_label_candidate"] and len(vector) <= 16 else "MEDIUM_EXACT" if law["scope"] == "FROZEN_REFERENCE_ONLY" and len(vector) == 1 else "LOW_CONFIDENCE"
        assert row["confidence"] == expected_confidence
        assert row["human_review_required"] == str(expected_confidence == "LOW_CONFIDENCE").lower()
        if classes[name] == "I":
            assert row["protected_output_effect"] == "EXACT_CLASS_I_TRAJECTORY_RECONSTRUCTION"
            test_column = stoich[0] if law["scope"] == "SOURCE_GENERAL" else active_columns[0]
            trial = {species[j]: initial[species[j]] + Fraction(1, 1000) * test_column.get(j, 0)
                     for j in range(len(species))}
            trial_reconstructed = (fraction(law["constant_initial"]) - sum(value * trial[species[j]]
                                  for j, value in vector.items() if j != i)) / vector[i]
            assert trial_reconstructed == trial[name], row["candidate_id"]
    assert {c: sum(r["confidence"] == c for r in candidates) for c in ("HIGH_EXACT", "MEDIUM_EXACT", "LOW_CONFIDENCE")} == manifest["exact_elimination_candidate_counts"]
    queue = rows(OUT / "low_confidence_reduction_review_queue_v0.csv")
    low_laws = {r["conservation_id"] for r in candidates if r["confidence"] == "LOW_CONFIDENCE"}
    assert {r["affected_ids"].split(":", 1)[0] for r in queue} == low_laws
    assert len(queue) == manifest["low_confidence_review_queue"]
    assert all(r["confidence"] == "LOW_CONFIDENCE" and r["recommended_human_question"] for r in queue)
    assert manifest["reduction_decisions_pending"] == 968
    print("PASS: 968 canonical reactions / 241 species; SBML, author parameters, normalized kinetic logic and functional bytes pinned")
    print("PASS: 290 independent exact reverse channels; directed gross fluxes retained; scaled RHS <= 1e-12")
    print("PASS: exact rational source rank 214 / nullity 27; frozen active rank 177 / 37 additional invariants")
    print(f"PASS: {len(candidates)} one-at-a-time exact reconstruction alternatives; Class-I initial reconstruction exact")
    print("PASS: 485 MathML-proved frozen-zero directed fluxes; 483 active directions retained")
    print(f"PASS: {len(queue)} grouped low-confidence scientific review items; reduction decisions 968/968 PENDING")
    print("NOTE: R3+ approximation and final reduced model are not approved")


if __name__ == "__main__":
    verify_invariants()
