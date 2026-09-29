#!/usr/bin/env python3
"""Derive condition-specific zero-rate and law reactivation evidence from SBML."""
from __future__ import annotations

import csv
import hashlib
import json
from fractions import Fraction

from verify_reduction_audit_v0 import OUT, ROOT, SOURCE, columns, fraction, rows, source_network

DOMAIN = "DOMAIN_DECISION_REQUIRED"
CSV_NAME = "frozen_reference_reactivation_v1.csv"
JSON_NAME = "frozen_reference_domain_certificate_v1.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def law_vectors(species, laws):
    index = {name: i for i, name in enumerate(species)}
    return {law["conservation_id"]: {index[name]: fraction(value)
            for name, value in json.loads(law["species_coefficients_json"]).items()}
            for law in laws}


def dot(vector, column):
    return sum((value * column.get(i, 0) for i, value in vector.items()), Fraction())


def derive():
    species, reactions, initial = source_network()
    stoich = columns(species, reactions)
    laws = rows(OUT / "conservation_laws_v0.csv")
    vectors = law_vectors(species, laws)
    source_ids = [law["conservation_id"] for law in laws if law["scope"] == "SOURCE_GENERAL"]
    frozen_ids = [law["conservation_id"] for law in laws if law["scope"] == "FROZEN_REFERENCE_ONLY"]
    assert len(source_ids) == 27 and len(frozen_ids) == 37
    zero = {row["reaction_id"]: row for row in rows(OUT / "reference_zero_reactions_v0.csv")}
    assert len(zero) == 485
    by_id = {reaction["id"]: reaction for reaction in reactions}
    output = []
    for reaction, column in zip(reactions, stoich):
        rid = reaction["id"]
        assert all(dot(vectors[law_id], column) == 0 for law_id in source_ids)
        if rid not in zero:
            assert reaction["k"] != 0
            continue
        assert reaction["k"] == 0 and reaction["factors"].count("k1") == 1
        row = zero[rid]
        affected = {law_id: dot(vectors[law_id], column) for law_id in frozen_ids
                    if dot(vectors[law_id], column) != 0}
        partner = row["reverse_partner_id"]
        if row["pair_zero_pattern"] == "ONLY_REVERSE_ZERO":
            assert partner and by_id[partner]["k"] != 0 and not affected
        output.append({
            "reaction_id": rid,
            "author_k1": "0",
            "reactivated_k1": "1",
            "pair_zero_pattern": row["pair_zero_pattern"],
            "reverse_partner_id": partner,
            "partner_author_k1": str(by_id[partner]["k"]) if partner else "",
            "author_active_rhs_treatment": "EXCLUDED_FROM_FROZEN_REFERENCE_ACTIVE_RHS",
            "reactivated_active_rhs_treatment": "INCLUDED_IN_REACTIVATED_ACTIVE_RHS",
            "source_reaction_retained": "true",
            "invariant_scope": "FROZEN_REFERENCE_ONLY",
            "generic_chart_scope": "SOURCE_GENERAL",
            "generic_chart_exact_residual": "0",
            "frozen_laws_invalidated_json": json.dumps({key: str(value) for key, value in affected.items()},
                                                    sort_keys=True, separators=(",", ":")),
            "domain_decision": DOMAIN,
        })
    assert len(output) == 485
    singleton = []
    index = {name: i for i, name in enumerate(species)}
    for law in laws:
        if law["scope"] != "FROZEN_REFERENCE_ONLY" or int(law["support_size"]) != 1:
            continue
        law_id = law["conservation_id"]
        vector = vectors[law_id]
        (i, coefficient), = vector.items()
        name = species[i]
        author_constant = coefficient * initial[name]
        assert fraction(law["constant_initial"]) == author_constant
        changed = dict(initial)
        changed[name] = Fraction(7, 13)
        changed_constant = sum(value * changed[species[j]] for j, value in vector.items())
        reconstructed = changed_constant / coefficient
        assert reconstructed == Fraction(7, 13)
        singleton.append({"law_id": law_id, "species": name,
                          "coefficient": str(coefficient), "author_constant": str(author_constant),
                          "perturbed_initial": "7/13", "perturbed_constant": str(changed_constant),
                          "reconstructed_species": str(reconstructed)})
    assert len(singleton) == 34
    by_pattern = {}
    invalidating = {}
    for row in output:
        pattern = row["pair_zero_pattern"]
        by_pattern[pattern] = by_pattern.get(pattern, 0) + 1
        invalidating[pattern] = invalidating.get(pattern, 0) + bool(json.loads(row["frozen_laws_invalidated_json"]))
    assert by_pattern == {"ONLY_REVERSE_ZERO": 65, "UNPAIRED_ZERO": 388, "BIDIRECTIONAL_ZERO": 32}
    assert invalidating == {"ONLY_REVERSE_ZERO": 0, "UNPAIRED_ZERO": 388, "BIDIRECTIONAL_ZERO": 8}
    certificate = {
        "schema_version": "1.0",
        "status": "CONDITION_SPECIFIC_EXACT_VIEW",
        "canonical_sbml_sha256": digest(SOURCE),
        "author_parameter_csv_sha256": digest(ROOT / "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv"),
        "author_initial_csv_sha256": digest(ROOT / "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv"),
        "conservation_laws_sha256": digest(OUT / "conservation_laws_v0.csv"),
        "source_general_laws": len(source_ids),
        "frozen_reference_only_laws": len(frozen_ids),
        "frozen_zero_directions": len(output),
        "author_active_directions": len(reactions) - len(output),
        "reactivation_by_pair_pattern": by_pattern,
        "reactivations_invalidating_frozen_law_by_pair_pattern": invalidating,
        "singleton_initial_perturbations": singleton,
        "domain_decision": DOMAIN,
        "scope_rule": "Frozen-only laws may optimize the author-condition execution view; they cannot delete states in the generic variable-condition model.",
        "ledger_rule": "Retain every canonical directed reaction and recover each gross directed extent; never replace gross ledgers with absolute net extent.",
    }
    return output, certificate


def main():
    reactivations, certificate = derive()
    with (OUT / CSV_NAME).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(reactivations[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(reactivations)
    certificate["reactivation_csv_sha256"] = digest(OUT / CSV_NAME)
    (OUT / JSON_NAME).write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("PASS: 485 frozen-zero directions; 483 author-active directions")
    print("PASS: 37 frozen-only laws, 27 source-general laws; 34 singleton constants recomputed")
    print("PASS: reactivation invalidates 388 unpaired and 8 bidirectional-zero frozen-law cases")
    print("PASS: 65 only-reverse-zero reactivations change profile while preserving the existing invariant span")


if __name__ == "__main__":
    main()
