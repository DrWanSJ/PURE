#!/usr/bin/env python3
"""Verify the generated PNAS2017 reaction-level annotation v0."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNOTATION = ROOT / "docs/reduction/reaction_level_annotation_v0.csv"
CONTRACT = ROOT / "docs/reduction/reaction_level_contract_v0.json"
BALANCE = ROOT / "models/pnas2017_full_reference/audit/reaction_balance_audit.csv"

EXPECTED_STAGE_COUNTS = {
    "DEG_sink": 388,
    "ELONG_aa_tRNA_delivery": 24,
    "ELONG_energy_coupling": 50,
    "ELONG_peptide_formation": 4,
    "ELONG_tRNA_release": 4,
    "ELONG_translocation": 8,
    "EN_binding": 54,
    "EN_byproduct_processing": 2,
    "EN_energy_transfer": 18,
    "INIT_70S_formation": 12,
    "INIT_assembly": 112,
    "INIT_energy_commitment": 14,
    "INIT_factor_release": 26,
    "INIT_tRNA_recruitment": 42,
    "RECYCLE_component_release": 24,
    "RECYCLE_disassembly": 14,
    "RS_activation": 36,
    "RS_binding": 48,
    "RS_charging": 20,
    "RS_to_INIT_formylation": 22,
    "TERM_energy_coupling": 34,
    "TERM_factor_binding": 8,
    "TERM_peptide_release": 4
}
EXPECTED_CONFIDENCE = {"high": 776, "medium": 190, "low": 2}
EXPECTED_TYPES = {
    "HETERODIMER_ASSOCIATION": 266,
    "DISSOCIATION": 266,
    "STATE_TRANSITION": 436,
}

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def main() -> None:
    rows = read_csv(ANNOTATION)
    balance = read_csv(BALANCE)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert len(rows) == 968
    assert len({r["reaction_id"] for r in rows}) == 968
    assert {r["reaction_id"] for r in rows} == {r["sbml_reaction_id"] for r in balance}
    allowed = {x["id"] for x in contract["level_c_functional_stages"]}
    assert {r["level_c_functional_stage"] for r in rows} <= allowed
    assert dict(sorted(Counter(r["level_c_functional_stage"] for r in rows).items())) == dict(sorted(EXPECTED_STAGE_COUNTS.items()))
    assert dict(Counter(r["annotation_confidence"] for r in rows)) == EXPECTED_CONFIDENCE
    assert dict(Counter(r["mechanistic_reaction_type"] for r in rows)) == EXPECTED_TYPES
    by_id = {r["reaction_id"]: r for r in rows}
    paired = [r for r in rows if r["reversibility_class"] == "EXACT_REVERSE_PAIR"]
    irreversible = [r for r in rows if r["reversibility_class"] == "IRREVERSIBLE"]
    assert len(paired) == 580
    assert len(irreversible) == 388
    assert all(r["level_c_functional_stage"] == "DEG_sink" for r in irreversible)
    pair_keys = set()
    for row in paired:
        partner = row["reverse_partner_id"]
        assert partner in by_id
        other = by_id[partner]
        assert other["reverse_partner_id"] == row["reaction_id"]
        assert other["level_c_functional_stage"] == row["level_c_functional_stage"]
        assert row["exact_reversible_merge"] == "true"
        pair_keys.add(tuple(sorted((row["reaction_id"], partner))))
    assert len(pair_keys) == 290
    low = [r for r in rows if r["annotation_confidence"] == "low"]
    assert {r["reaction_id"] for r in low} == {"re0000000308", "re0000000327"}
    for row in rows:
        json.loads(row["reactants_json"])
        json.loads(row["products_json"])
        json.loads(row["resource_ledger_effect_json"])
        json.loads(row["functional_pool_effect_json"])
        json.loads(row["conservation_family_effect_json"])
        assert row["human_review_status"].startswith("PENDING_HUMAN_REVIEW") or row["human_review_status"].startswith("PRIORITY_HUMAN_REVIEW")
    print("PASS: 968 unique reaction annotations")
    print("PASS: all primary Level-C labels are in the controlled vocabulary")
    print("PASS: stage/confidence/mechanistic-type fingerprints match v0")
    print("PASS: 580 directed rows form 290 symmetric exact reverse channels")
    print("PASS: 388 irreversible rows are DEG_sink coverage rows")
    print("PASS: only EFG-GDP/50S shared pair is low-confidence priority review")
    print("NOTE: structural/annotation verification only; no QSSA, lumping, or kinetic accuracy is validated")

if __name__ == "__main__":
    main()
