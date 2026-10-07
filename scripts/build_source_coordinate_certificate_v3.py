#!/usr/bin/env python3
"""Exact chart replacing the v1 CK degradation sink with CK_ATP."""
from __future__ import annotations

import hashlib
import json

from build_source_coordinate_certificate_v1 import certify
from verify_reduction_audit_v0 import OUT, SOURCE, columns, rows, source_network


def main():
    species, reactions, initial = source_network()
    stoich = columns(species, reactions)
    laws = [law for law in rows(OUT / "conservation_laws_v0.csv") if law["scope"] == "SOURCE_GENERAL"]
    v1 = json.loads((OUT / "source_coordinate_certificate_v1.json").read_text(encoding="utf-8"))
    eliminated = ["CK_ATP" if name == "CK_degraded" else name for name in v1["eliminated_species"]]
    assert len(eliminated) == len(set(eliminated)) == 27
    assert {"CK_degraded", "GlyAMP", "MetAMP"} <= set(species) - set(eliminated)
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
        "eliminated_species": eliminated,
        "selection_rule": "Replace v1 CK_degraded coordinate with independent CK_ATP; retain all 42 Class-I and free GlyAMP/MetAMP",
        "reason": "V1 reconstructs a frozen-zero CK sink with drift; v2 eliminated small fast CK_ADP and was numerically poor",
        "intermediate_17_chart": "source_coordinate_certificate_17_v1.json",
    }
    (OUT / "source_coordinate_plan_v3.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "source_coordinate_certificate_v3.json").write_text(
        json.dumps({"schema_version": "1.0", **hashes, **cert}, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("PASS: v3 exact 241-to-214 chart; CK_degraded retained and CK_ATP eliminated")


if __name__ == "__main__":
    main()
