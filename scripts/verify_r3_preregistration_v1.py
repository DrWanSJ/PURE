#!/usr/bin/env python3
"""Bind the R3 pilot grid and historical fast-state candidate to source SBML."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from verify_reduction_audit_v0 import OUT, ROOT, SOURCE, columns, fraction, rows, source_network

GRID = OUT / "r3_validation_grid_v1.csv"
METHOD = OUT / "r3_aminoacylation_qssa_method.md"
PARTITION = ROOT / "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition.json"
FAILURE = ROOT / "docs/audit/pnas2017_aminoacylation_reduction_v1/formal_failure_classification_v1r2.md"
MAP = OUT / "r3_source_reaction_candidate_map_v1.csv"
REPORT = OUT / "r3_preregistration_certificate_v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    species, reactions, initial = source_network()
    stoich = columns(species, reactions)
    species_set = set(species)
    grid = rows(GRID)
    expected = ["R3_BASE", "R3_GLYRS_LOW", "R3_GLYRS_HIGH", "R3_METRS_LOW", "R3_METRS_HIGH",
                "R3_GLY_LOW", "R3_MET_LOW", "R3_TRNA_LOW", "R3_ATP_LOW", "R3_ADVERSE"]
    assert [row["condition_id"] for row in grid] == expected
    conditions = []
    for row in grid:
        scales = json.loads(row["initial_scale_json"])
        assert set(scales) <= species_set
        assert all(isinstance(value, (int, float)) and value > 0 for value in scales.values())
        x0 = {name: initial[name] * fraction(scales.get(name, 1)) for name in species}
        assert all(value >= 0 for value in x0.values())
        conditions.append({"condition_id": row["condition_id"], "scaled_species": scales,
                           "GlyRS_initial": str(x0["GlyRS"]), "MetRS_initial": str(x0["MetRS"]),
                           "ATP_initial": str(x0["ATP"]), "Gly_initial": str(x0["Gly"]),
                           "Met_initial": str(x0["Met"])})
    assert grid[0]["initial_scale_json"] == "{}"
    assert grid[-1]["role"] == "anticipated_failure_domain"

    historical = json.loads(PARTITION.read_text(encoding="utf-8"))
    selected = historical["eliminated_complexes"]
    kept = historical["kept_dynamic"]
    assert len(selected) == len(set(selected)) == 21
    assert len(kept) == len(set(kept)) == 9
    assert not set(selected) & set(kept)
    assert {"GlyAMP", "MetAMP"} <= set(kept)
    assert all(name.startswith(("GlyRS_", "MetRS_")) and name in species_set for name in selected)
    assert all(name in species_set for name in kept)
    source_laws = {row["conservation_id"]: row for row in rows(OUT / "conservation_laws_v0.csv")
                   if row["scope"] == "SOURCE_GENERAL"}
    index = {name: i for i, name in enumerate(species)}
    for law_id, prefix in (("CONS_001", "GlyRS"), ("CONS_002", "MetRS")):
        vector = json.loads(source_laws[law_id]["species_coefficients_json"])
        assert all(vector[name] == 1 for name in selected if name.startswith(prefix + "_"))
        assert vector[prefix] == 1 and vector[prefix + "_degraded"] == 1
        assert all(sum(fraction(value) * column.get(index[name], 0) for name, value in vector.items()) == 0
                   for column in stoich)

    mapped = []
    covered = set()
    for reaction in reactions:
        fast_reactants = sorted(set(reaction["reactants"]) & set(selected))
        fast_products = sorted(set(reaction["products"]) & set(selected))
        covered.update(fast_reactants + fast_products)
        mapped.append({
            "reaction_id": reaction["id"],
            "canonical_k1": str(reaction["k"]),
            "fast_reactants": ";".join(fast_reactants),
            "fast_products": ";".join(fast_products),
            "candidate_representation": "SOURCE_DIRECTED_RATE_AT_RECONSTRUCTED_STATE",
            "fast_balance_role": "FAST_AND_SLOW_STOICHIOMETRIC_CONTRIBUTOR" if fast_reactants or fast_products
                                 else "SLOW_SOURCE_REACTION_UNCHANGED",
            "gross_directed_extent_retained": "true",
            "candidate_status": "CANDIDATE_PENDING_FULL_COUPLED_VALIDATION",
        })
    assert covered == set(selected)
    assert len(mapped) == 968
    with MAP.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(mapped[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(mapped)
    report = {
        "schema_version": "1.0", "status": "R3_PREREGISTERED_UNVALIDATED",
        "canonical_sbml_sha256": sha(SOURCE),
        "method_sha256": sha(METHOD), "grid_sha256": sha(GRID),
        "historical_partition_sha256": sha(PARTITION),
        "historical_failure_classification_sha256": sha(FAILURE),
        "source_reaction_map_sha256": sha(MAP),
        "grid_conditions": conditions,
        "historical_candidate_selected_complexes": selected,
        "historical_candidate_kept_dynamic": kept,
        "canonical_source_reaction_count": len(mapped),
        "source_reactions_touching_candidate_fast_states": sum(bool(row["fast_reactants"] or row["fast_products"]) for row in mapped),
        "source_general_enzyme_pool_laws": ["CONS_001", "CONS_002"],
        "scope": "Candidate selection and preregistered grid only; no QSSA closure or coupled validation claim.",
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PASS: {len(grid)} fixed grid cases; all perturbed initial states nonnegative")
    print(f"PASS: 21 candidate bound states and 9 kept dynamic states verified against source species")
    print(f"PASS: 968 source-directed reaction mappings; {report['source_reactions_touching_candidate_fast_states']} touch candidate fast states")
    print("NOTE: historical candidate remains unvalidated; prior formal failure retained")


if __name__ == "__main__":
    main()
