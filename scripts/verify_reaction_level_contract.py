#!/usr/bin/env python3
"""Structural verifier for the PNAS2017 reaction-level functional contract v0.

This verifier checks the controlled Level-C vocabulary and source-network facts.
It does NOT assign all 968 reactions to Level-C stages and does NOT validate
lumping, QSSA, fast equilibrium, or kinetic accuracy.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REACTIONS = ROOT / "models/pnas2017_full_reference/audit/reactions.csv"
DECISIONS = ROOT / "docs/reduction/reduction_decisions.csv"
MODULES = ROOT / "models/pnas2017_full_reference/audit/modules.csv"
CONTRACT = ROOT / "docs/reduction/reaction_level_contract_v0.json"
SUMMARY = ROOT / "docs/reduction/reaction_level_contract_summary.md"
DETAILED = ROOT / "docs/reduction/reaction_level_contract_detailed.md"

EXPECTED_TYPES = {
    "DISSOCIATION": 266,
    "HETERODIMER_ASSOCIATION": 266,
    "STATE_TRANSITION": 436,
}
EXPECTED_REVERSIBILITY_CLASSES = {
    "IRREVERSIBLE",
    "EXACT_REVERSE_PAIR",
    "POSSIBLE_REVERSE_PAIR",
    "UNKNOWN",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def canonical_side(payload: str) -> tuple[tuple[str, str], ...]:
    items = json.loads(payload)
    return tuple(sorted((item["species_id"], str(item["stoichiometry"])) for item in items))


def reverse_pair_stats(rows: list[dict[str, str]]) -> tuple[int, int, int]:
    by_signature = defaultdict(list)
    for row in rows:
        signature = (canonical_side(row["reactants_json"]), canonical_side(row["products_json"]))
        by_signature[signature].append(row["reaction_id"])

    seen = set()
    pair_groups = 0
    paired_reactions = 0
    ambiguous_groups = 0
    for signature, ids in by_signature.items():
        if signature in seen:
            continue
        reverse = (signature[1], signature[0])
        reverse_ids = by_signature.get(reverse, [])
        seen.add(signature)
        seen.add(reverse)
        if reverse_ids and reverse != signature:
            pair_groups += 1
            paired_reactions += len(ids) + len(reverse_ids)
            if len(ids) != 1 or len(reverse_ids) != 1:
                ambiguous_groups += 1
    return pair_groups, paired_reactions, ambiguous_groups


def main() -> None:
    reactions = read_csv(REACTIONS)
    decisions = read_csv(DECISIONS)
    modules = read_csv(MODULES)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    summary = SUMMARY.read_text(encoding="utf-8")
    detailed = DETAILED.read_text(encoding="utf-8")

    assert len(reactions) == 968, len(reactions)
    assert len({row["reaction_id"] for row in reactions}) == 968
    assert len(decisions) == 968, len(decisions)
    assert len({row["sbml_reaction_id"] for row in decisions}) == 968
    assert len(modules) == 26, len(modules)

    sbml_reversible_true = sum(row["reversible"].strip().lower() == "true" for row in reactions)
    assert sbml_reversible_true == 0, sbml_reversible_true

    pair_groups, paired_reactions, ambiguous_groups = reverse_pair_stats(reactions)
    assert (pair_groups, paired_reactions, ambiguous_groups) == (290, 580, 0), (
        pair_groups,
        paired_reactions,
        ambiguous_groups,
    )

    type_counts = Counter(row["cell_designer_reaction_type"] for row in decisions)
    assert dict(type_counts) == EXPECTED_TYPES, (type_counts, EXPECTED_TYPES)

    degradation_reactions = sum(
        "_degraded" in row["reactants_json"] or "_degraded" in row["products_json"]
        for row in decisions
    )
    assert degradation_reactions == 388, degradation_reactions

    formylation_reactions = sum(
        "FMet_tRNASynthesis" in row["level_b_subsystem_candidates"].split(";")
        for row in decisions
    )
    assert formylation_reactions == 29, formylation_reactions

    assert contract["mapping_status"] == "VOCABULARY_ONLY_NO_968_ROW_ASSIGNMENT"
    stages = contract["level_c_functional_stages"]
    stage_ids = [stage["id"] for stage in stages]
    assert len(stage_ids) == 23, len(stage_ids)
    assert len(set(stage_ids)) == 23

    active = [stage for stage in stages if stage.get("coverage_role") == "active_process"]
    special = [stage for stage in stages if stage.get("coverage_role") == "coverage_only"]
    assert len(active) == 22, len(active)
    assert len(special) == 1 and special[0]["id"] == "DEG_sink", special
    assert sum(stage["level_a_module"] == "elongation" for stage in active) == 5
    assert "RS_to_INIT_formylation" in stage_ids

    assert set(contract["mechanistic_reaction_types"]) == set(EXPECTED_TYPES)
    assert set(contract["reversibility_classes"]) == EXPECTED_REVERSIBILITY_CLASSES

    checks = contract["source_checks"]
    assert checks["combined_reactions"] == 968
    assert checks["original_subsystems"] == 26
    assert checks["sbml_reversible_true"] == 0
    assert checks["exact_reverse_stoichiometry_pairs"] == 290
    assert checks["reaction_ids_in_exact_reverse_pairs"] == 580
    assert checks["ambiguous_reverse_signature_groups"] == 0
    assert checks["degradation_related_reactions"] == 388
    assert checks["fMet_tRNASynthesis_reactions"] == 29
    assert checks["mechanistic_reaction_type_counts"] == EXPECTED_TYPES

    for stage_id in stage_ids:
        assert f"`{stage_id}`" in summary, f"summary missing {stage_id}"
        assert f"`{stage_id}`" in detailed, f"detailed missing {stage_id}"

    print("PASS: 968 unique source reactions; 26 source subsystems")
    print("PASS: CellDesigner reaction types = association 266, dissociation 266, state transition 436")
    print("PASS: source SBML reversible=true count = 0")
    print("PASS: 290 exact reverse-stoichiometry pairs cover 580 directed reactions; no ambiguous signature groups")
    print("PASS: 388 degradation-related reactions require explicit DEG_sink coverage")
    print("PASS: 29 FMet_tRNASynthesis reactions require the RS-to-INIT formylation bridge")
    print("PASS: Level-C vocabulary = 22 active stages + 1 coverage-only stage; elongation keeps 5 active stages")
    print("PASS: summary/detailed Markdown contain every controlled Level-C label")
    print("NOTE: vocabulary/source-structure verification only; no 968-row functional assignment or kinetic reduction is validated")


if __name__ == "__main__":
    main()
