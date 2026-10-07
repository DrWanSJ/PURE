#!/usr/bin/env python3
"""Alternative exact chart retaining the numerically delicate CK degradation sink."""
from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction

from build_reduction_audit_v0 import add_independent, echelon_rows
from build_source_coordinate_certificate_v1 import certify
from verify_reduction_audit_v0 import OUT, SOURCE, columns, rows, source_network


def main():
    species, reactions, initial = source_network()
    stoich = columns(species, reactions)
    assert len(species) == 241 and len(echelon_rows(stoich)) == 214
    laws = [law for law in rows(OUT / "conservation_laws_v0.csv") if law["scope"] == "SOURCE_GENERAL"]
    assert len(laws) == 27
    coefficients = [json.loads(law["species_coefficients_json"]) for law in laws]
    detail = (OUT / "species_information_contract_detailed.md").read_text(encoding="utf-8")
    classes = dict(re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*(I|II-A|II-B|III|C)\*\*\s*\|", detail, re.M))
    assert len(classes) == 241 and sum(value == "I" for value in classes.values()) == 42
    protected = {"CK_degraded", "GlyAMP", "MetAMP"}
    preferred = [law["biological_label_candidate"].removesuffix("_named_pool") + "_degraded"
                 for law in laws[:17]
                 if law["biological_label_candidate"] != "CK_named_pool"]
    remaining = sorted((name for name in species if name not in preferred and
                        classes[name] != "I" and name not in protected),
                       key=lambda name: (0 if classes[name] == "C" and name.endswith("_degraded")
                                         else 1 if classes[name] == "C"
                                         else 2 if classes[name] == "II-A"
                                         else 3 if classes[name] == "II-B" else 4, name))
    pivots, eliminated = {}, []
    for name in preferred + remaining:
        column = {i: Fraction(coefficient[name]) for i, coefficient in enumerate(coefficients)
                  if name in coefficient and Fraction(coefficient[name])}
        if add_independent(column, pivots):
            eliminated.append(name)
        if len(eliminated) == 27:
            break
    assert len(eliminated) == 27 and protected.isdisjoint(eliminated)
    assert all(classes[name] != "I" for name in eliminated)
    cert = certify(species, stoich, initial, laws, eliminated)
    hashes = {
        "canonical_sbml_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "conservation_laws_sha256": hashlib.sha256((OUT / "conservation_laws_v0.csv").read_bytes()).hexdigest(),
        "species_contract_sha256": hashlib.sha256((OUT / "species_information_contract_detailed.md").read_bytes()).hexdigest(),
    }
    plan = {
        "schema_version": "1.0",
        "status": "EXACT_SOURCE_GENERAL_ALTERNATIVE_CHART_NOT_NUMERIC_ACCEPTANCE",
        **hashes,
        "source_rank": 214,
        "source_left_nullity": 27,
        "protected_class_I_count": 42,
        "additional_retained_species": sorted(protected),
        "eliminated_species": eliminated,
        "intermediate_17_chart": "source_coordinate_certificate_17_v1.json",
        "selection_rule": "Exclude CK_degraded, GlyAMP, MetAMP and Class I; choose 16 named-pool sinks, then independent C and II-A/II-B/III columns",
        "reason": "Numerical alternative after exact v1 chart produced CK_degraded reconstruction drift; no exact gate changed",
    }
    (OUT / "source_coordinate_plan_v2.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "source_coordinate_certificate_v2.json").write_text(
        json.dumps({"schema_version": "1.0", **hashes, **cert}, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"retained": cert["retained_count"], "eliminated": eliminated}, indent=2))


if __name__ == "__main__":
    main()
