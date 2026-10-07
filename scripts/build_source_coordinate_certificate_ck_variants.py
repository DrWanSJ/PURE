#!/usr/bin/env python3
"""Certify the remaining one-column CK_CP alternative charts."""
from __future__ import annotations

import hashlib
import json

from build_source_coordinate_certificate_v1 import certify
from verify_reduction_audit_v0 import OUT, SOURCE, columns, rows, source_network


def main():
    species, reactions, initial = source_network()
    stoich = columns(species, reactions)
    laws = [law for law in rows(OUT / "conservation_laws_v0.csv")
            if law["scope"] == "SOURCE_GENERAL"]
    v4 = json.loads((OUT / "source_coordinate_certificate_v4.json").read_text(encoding="utf-8"))
    hashes = {
        "canonical_sbml_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "conservation_laws_sha256": hashlib.sha256((OUT / "conservation_laws_v0.csv").read_bytes()).hexdigest(),
        "species_contract_sha256": hashlib.sha256((OUT / "species_information_contract_detailed.md").read_bytes()).hexdigest(),
    }
    for version, replacement in (("v6", "CK_Cr_ATP"), ("v7", "CK_Cr")):
        eliminated = [replacement if name == "CK_CP" else name
                      for name in v4["eliminated_species"]]
        assert len(eliminated) == len(set(eliminated)) == 27
        assert {"CK_CP", "CK_degraded", "NDK_degraded", "GlyAMP", "MetAMP"} <= set(species) - set(eliminated)
        cert = certify(species, stoich, initial, laws, eliminated)
        plan = {
            "schema_version": "1.0",
            "status": "EXACT_SOURCE_GENERAL_ALTERNATIVE_CHART_NOT_NUMERIC_ACCEPTANCE",
            **hashes,
            "source_rank": 214,
            "source_left_nullity": 27,
            "eliminated_species": eliminated,
            "selection_rule": f"Replace v4 CK_CP with independent {replacement}; retain CK_CP, degradation sinks, Class-I and free GlyAMP/MetAMP",
            "reason": "V4 passed domain but gross CK_CP reverse extents exceeded the fixed comparison gate; v5 CK_CP_ADP replacement failed short-domain test",
            "intermediate_17_chart": "source_coordinate_certificate_17_v1.json",
        }
        (OUT / f"source_coordinate_plan_{version}.json").write_text(
            json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n")
        (OUT / f"source_coordinate_certificate_{version}.json").write_text(
            json.dumps({"schema_version": "1.0", **hashes, **cert}, indent=2) + "\n",
            encoding="utf-8", newline="\n")
        print(f"PASS: {version} exact 241-to-214 chart with {replacement} eliminated")


if __name__ == "__main__":
    main()
