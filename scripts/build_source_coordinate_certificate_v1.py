#!/usr/bin/env python3
"""Derive exact source-general affine coordinates from canonical SBML stoichiometry."""
from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

import sympy as sp

from build_reduction_audit_v0 import add_independent, echelon_rows
from verify_reduction_audit_v0 import OUT, ROOT, SOURCE, columns, rows, source_network


def as_fraction(value):
    return Fraction(str(value))


def matrix(data):
    return sp.Matrix([[sp.Rational(str(value)) for value in row] for row in data])


def sparse_rows(values, names):
    return [{name: str(value) for name, value in zip(names, values.row(i)) if value}
            for i in range(values.rows)]


def certify(species, stoich, initial, laws, eliminated):
    """Build x_E=A*b+B*x_R and prove its exact structural identities."""
    names = {name: i for i, name in enumerate(species)}
    selected = [names[name] for name in eliminated]
    retained = [i for i in range(len(species)) if i not in set(selected)]
    coefficient_rows = [json.loads(law["species_coefficients_json"]) for law in laws]
    L = matrix([[coefficient.get(name, 0) for name in species] for coefficient in coefficient_rows])
    L_E = L[:, selected]
    assert L_E.rows == L_E.cols == len(laws) and L_E.det() != 0
    L_R = L[:, retained]
    A = L_E.inv()
    B = -A * L_R
    assert L_E * A == sp.eye(len(laws))
    assert L_E * B + L_R == sp.zeros(len(laws), len(retained))
    x0 = matrix([[initial[name]] for name in species])
    b = L * x0
    assert A * b + B * x0[retained, :] == x0[selected, :]
    for column in stoich:
        source = {i: sp.Rational(str(value)) for i, value in column.items()}
        assert L * matrix([[source.get(i, 0)] for i in range(len(species))]) == sp.zeros(len(laws), 1)
        sr = matrix([[source.get(i, 0)] for i in retained])
        assert B * sr == matrix([[source.get(i, 0)] for i in selected])
    # An exact law-basis shear must leave the physical coordinate map unchanged.
    T = sp.eye(len(laws))
    T[0, 1] = 1
    rebased = T * L
    A_rebased = rebased[:, selected].inv()
    assert A_rebased * T == A
    assert -A_rebased * rebased[:, retained] == B
    trial = x0.copy()
    trial[selected[0], 0] += sp.Rational(1, 7)
    trial[retained[0], 0] += sp.Rational(1, 10)
    trial_b = L * trial
    assert A * trial_b + B * trial[retained, :] == trial[selected, :]
    assert A * b + B * trial[retained, :] != trial[selected, :]
    assert all(value >= 0 for value in x0)
    assert all(value >= 0 for value in A * b + B * x0[retained, :])
    return {
        "status": "EXACT_DERIVATION_NOT_NUMERIC_ACCEPTANCE",
        "source_species_count": len(species),
        "retained_count": len(retained),
        "eliminated_count": len(selected),
        "law_ids": [law["conservation_id"] for law in laws],
        "eliminated_species": eliminated,
        "retained_species": [species[i] for i in retained],
        "A_rows": [[str(value) for value in A.row(i)] for i in range(A.rows)],
        "B_sparse_rows": sparse_rows(B, [species[i] for i in retained]),
        "author_initial_b": [str(value) for value in b],
        "proofs": {
            "rank_L_E": len(laws),
            "L_E_A_identity": True,
            "L_E_B_plus_L_R_zero": True,
            "initial_reconstruction_exact": True,
            "S_E_equals_B_S_R_exact_all_directed_columns": True,
            "lifted_vector_field_identity_exact": True,
            "law_rebasing_preserves_physical_map": True,
            "changed_initial_recomputes_b": True,
            "reused_b_mutant_rejected": True,
            "author_initial_in_physical_domain": True,
        },
        "physical_domain": "x_R >= 0 AND A*(L*x0) + B*x_R >= 0; no clipping",
    }


def main():
    species, reactions, initial = source_network()
    stoich = columns(species, reactions)
    assert len(species) == 241 and len(stoich) == 968 and len(echelon_rows(stoich)) == 214
    laws = [law for law in rows(OUT / "conservation_laws_v0.csv") if law["scope"] == "SOURCE_GENERAL"]
    assert len(laws) == 27
    detail = (OUT / "species_information_contract_detailed.md").read_text(encoding="utf-8")
    classes = dict(re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*(I|II-A|II-B|III|C)\*\*\s*\|", detail, re.M))
    assert set(classes) == set(species)
    protected = [name for name in species if classes[name] == "I"]
    assert len(protected) == 42
    first_laws = laws[:17]
    assert all(law["biological_label_candidate"].endswith("_named_pool") for law in first_laws)
    first_sinks = [law["biological_label_candidate"].removesuffix("_named_pool") + "_degraded"
                   for law in first_laws]
    assert all(classes[name] == "C" for name in first_sinks)
    first = certify(species, stoich, initial, first_laws, first_sinks)
    assert first["retained_count"] == 224
    coefficients = [json.loads(law["species_coefficients_json"]) for law in laws]
    other = sorted((name for name in species if name not in first_sinks and classes[name] != "I"),
                   key=lambda name: (0 if classes[name] == "C" and name.endswith("_degraded")
                                     else 1 if classes[name] == "C"
                                     else 2 if classes[name] == "II-A"
                                     else 3 if classes[name] == "II-B" else 4, name))
    pivots = {}
    eliminated = []
    for name in first_sinks + other:
        column = {i: as_fraction(coefficient[name]) for i, coefficient in enumerate(coefficients)
                  if name in coefficient and as_fraction(coefficient[name])}
        if add_independent(column, pivots):
            eliminated.append(name)
        if len(eliminated) == 27:
            break
    assert len(eliminated) == 27 and all(name not in protected for name in eliminated)
    full = certify(species, stoich, initial, laws, eliminated)
    assert full["retained_count"] == 214 and set(protected) <= set(full["retained_species"])
    hashes = {
        "canonical_sbml_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "conservation_laws_sha256": hashlib.sha256((OUT / "conservation_laws_v0.csv").read_bytes()).hexdigest(),
        "species_contract_sha256": hashlib.sha256((OUT / "species_information_contract_detailed.md").read_bytes()).hexdigest(),
    }
    plan = {
        "schema_version": "1.0",
        "status": "EXACT_SOURCE_GENERAL_COORDINATE_PLAN_NOT_NUMERIC_ACCEPTANCE",
        **hashes,
        "source_rank": 214,
        "source_left_nullity": 27,
        "protected_class_I_species": protected,
        "intermediate_chart": {"laws": first["law_ids"], "eliminated_species": first_sinks},
        "simultaneous_chart": {"laws": full["law_ids"], "eliminated_species": eliminated},
        "selection_rule": "17 named-pool degraded sinks first; then independent non-Class-I columns in C, II-A, II-B, III order",
        "basis_interpretation": "Exact algebra only; law basis is not biological ontology",
    }
    for path, data in (
        ("source_coordinate_plan_v1.json", plan),
        ("source_coordinate_certificate_17_v1.json", {"schema_version": "1.0", **hashes, **first}),
        ("source_coordinate_certificate_v1.json", {"schema_version": "1.0", **hashes, **full}),
    ):
        (OUT / path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"source_rank": 214, "left_nullity": 27, "intermediate": 224,
                      "full": 214, "protected_class_I": len(protected), "eliminated": eliminated}, indent=2))


if __name__ == "__main__":
    main()
