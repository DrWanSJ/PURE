#!/usr/bin/env python3
"""Adversarial scope tests for the author-condition zero-rate view."""
from __future__ import annotations

import copy
import json
import tempfile
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path

from build_frozen_reference_domain_v1 import CSV_NAME, JSON_NAME, derive, digest, dot, law_vectors
from verify_reduction_audit_v0 import M, OUT, S, SOURCE, columns, fraction, parse, rows, source_network


def reject_mutated_xml(tree, mutate):
    mutant = copy.deepcopy(tree)
    model = mutant.getroot().find(S + "model")
    mutate(model)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "mutated.xml"
        mutant.write(path, encoding="utf-8", xml_declaration=True)
        try:
            parse(path)
        except AssertionError:
            return
    raise AssertionError("zero-rate semantic bypass was accepted")


def main():
    species, reactions, initial = source_network()
    stoich = columns(species, reactions)
    laws = rows(OUT / "conservation_laws_v0.csv")
    vectors = law_vectors(species, laws)
    source_ids = [row["conservation_id"] for row in laws if row["scope"] == "SOURCE_GENERAL"]
    frozen_ids = [row["conservation_id"] for row in laws if row["scope"] == "FROZEN_REFERENCE_ONLY"]
    by_id = {reaction["id"]: (reaction, column) for reaction, column in zip(reactions, stoich)}

    derived, expected_certificate = derive()
    recorded = rows(OUT / CSV_NAME)
    assert recorded == derived
    certificate = json.loads((OUT / JSON_NAME).read_text(encoding="utf-8"))
    assert certificate.pop("reactivation_csv_sha256") == digest(OUT / CSV_NAME)
    assert certificate == expected_certificate
    by_row = {row["reaction_id"]: row for row in recorded}

    # These are kinetic changes only: each reactivated k1=1 gives a nonzero
    # rate at the positive unit state, while the original k1=0 gives zero.
    for rid, pattern, breaks_frozen in (
        ("re0000000003", "UNPAIRED_ZERO", True),
        ("re0000000417", "BIDIRECTIONAL_ZERO", True),
        ("re0000000002", "ONLY_REVERSE_ZERO", False),
    ):
        row = by_row[rid]
        reaction, column = by_id[rid]
        assert row["pair_zero_pattern"] == pattern
        assert row["author_active_rhs_treatment"] == "EXCLUDED_FROM_FROZEN_REFERENCE_ACTIVE_RHS"
        assert row["reactivated_active_rhs_treatment"] == "INCLUDED_IN_REACTIVATED_ACTIVE_RHS"
        assert row["source_reaction_retained"] == "true"
        assert row["domain_decision"] == "DOMAIN_DECISION_REQUIRED"
        assert reaction["k"] == 0
        assert fraction(row["reactivated_k1"]) == 1
        assert all(factor == "k1" or factor in species for factor in reaction["factors"])
        impacted = json.loads(row["frozen_laws_invalidated_json"])
        assert bool(impacted) == breaks_frozen
        assert impacted == {law_id: str(dot(vectors[law_id], column)) for law_id in frozen_ids
                            if dot(vectors[law_id], column) != 0}
        assert all(dot(vectors[law_id], column) == 0 for law_id in source_ids)
        if pattern == "ONLY_REVERSE_ZERO":
            assert by_id[row["reverse_partner_id"]][0]["k"] != 0
    print("PASS: three parameter-reactivation mutants; frozen-law and source-chart scopes distinguished")

    # An initial value is part of b=L*x0, not a structural zero. Reusing the
    # author constant would reconstruct zero and fail on the new condition.
    singletons = certificate["singleton_initial_perturbations"]
    assert len(singletons) == 34
    for witness in singletons:
        coefficient = fraction(witness["coefficient"])
        changed_value = fraction(witness["perturbed_initial"])
        changed_constant = fraction(witness["perturbed_constant"])
        assert changed_value == Fraction(7, 13)
        assert changed_constant == coefficient * changed_value
        assert fraction(witness["reconstructed_species"]) == changed_value
        assert fraction(witness["author_constant"]) / coefficient != changed_value
        assert initial[witness["species"]] == 0
    print("PASS: 34 singleton mutants reconstruct nonzero initial constants; stale author b rejected")

    # Alternative MathML paths or model-level controllers would invalidate
    # the proof that k1=0 annihilates every zero-marked reaction.
    tree = ET.parse(SOURCE)
    for forbidden in ("listOfRules", "listOfEvents", "listOfInitialAssignments",
                      "listOfFunctionDefinitions", "listOfConstraints"):
        def add_controller(model, name=forbidden):
            ET.SubElement(ET.SubElement(model, S + name), S + "mutant")
        reject_mutated_xml(tree, add_controller)
    for operator in ("plus", "piecewise"):
        def bypass_zero(model, name=operator):
            reaction = model.find(S + "listOfReactions")[1]
            expression = reaction.find(S + "kineticLaw").find(M + "math")[0]
            expression[0].tag = M + name
        reject_mutated_xml(tree, bypass_zero)
    print("PASS: rule/event/initial-assignment/function/constraint and additive/piecewise bypass mutants rejected")


if __name__ == "__main__":
    main()
