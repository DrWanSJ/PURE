#!/usr/bin/env python3
"""Structural verifier for the PNAS2017 241-species information-retention contract.

This verifies classification completeness/consistency only. It does NOT validate
QSSA time-scale separation or reduced-model kinetic accuracy.
"""
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "models/pnas2017_full_reference/audit/species_reduction_map.csv"
DETAIL = ROOT / "docs/reduction/species_information_contract_detailed.md"

I_SET = {
    "ADP","AMP","ATP","CK","CP","Cr","EFG","EFTs","EFTu","FD","GDP","GMP","GTP","Gly",
    "GlyRS","GlytRNAGlyGCC","IF1","IF2","IF3","MK","MTF","Met","MetRS","MettRNAfMetCAU",
    "NDK","PO4","PPi","PPiase","Pept0003","RF1","RF2","RF3","RRF","RS30S","RS50S","RS70S",
    "THF","fMet","fMettRNAfMetCAU","mRNA","tRNAGlyGCC","tRNAfMetCAU",
}
EXPECTED = {"I": 42, "II-A": 57, "II-B": 91, "III": 22, "C": 29}
ENERGY = {"ATP","ADP","AMP","GTP","GDP","GMP","PO4","PPi","CP","Cr"}
PRETERM = {
    "elRS70SAUAA0004_Pept0003tRNAGlyGCC",
    "elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1",
    "elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2",
}

def classify(row: dict[str, str]) -> tuple[str, str]:
    s = row["species_id"]
    cand = row.get("candidate_coarse_variable", "")
    if s in I_SET:
        return "I", "protected_dynamic"
    if row["primary_reduction_class"] == "DEGRADED_SINK":
        return "C", "degradation"
    if row["primary_reduction_class"] == "ENZYME_INTERMEDIATE":
        return "II-A", "enzyme_intermediate"
    if s == "Pept0002":
        return "II-B", "peptide_length"
    if s in {"Pept0002tRNAGlyGCC", "Pept0003tRNAGlyGCC"}:
        return "II-B", "peptidyl_tRNA"
    if s == "RS50S_tRNAGlyGCC":
        return "II-B", "R_recycle"
    if s in PRETERM:
        return "II-B", "R_term_preterm"
    if cand in {"R_init", "R_recycle", "R_term"}:
        return "II-B", cand
    if cand == "R_elong":
        return "III", "R_elong"
    if row["primary_reduction_class"] == "LUMP_FUNCTIONAL_POOL":
        return "II-B", cand or row.get("conservation_family", "") or "functional_pool"
    raise AssertionError(f"unmapped species: {s}")

def parse_detail(path: Path) -> list[tuple[str, str]]:
    out = []
    row_re = re.compile(r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*(I|II-A|II-B|III|C)\*\*\s*\|")
    for line in path.read_text(encoding="utf-8").splitlines():
        m = row_re.match(line)
        if m:
            out.append((m.group(2), m.group(3)))
    return out

def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 241, len(rows)
    ids = [r["species_id"] for r in rows]
    assert len(set(ids)) == 241

    classes = {r["species_id"]: classify(r) for r in rows}
    counts = Counter(v[0] for v in classes.values())
    assert dict(counts) == EXPECTED, (counts, EXPECTED)

    assert all(classes[r["species_id"]][0] == "C" for r in rows if r["primary_reduction_class"] == "DEGRADED_SINK")
    assert all(classes[r["species_id"]][0] == "II-A" for r in rows if r["primary_reduction_class"] == "ENZYME_INTERMEDIATE")
    assert all(classes[s][0] == "I" for s in ENERGY)
    assert classes["Pept0002"] == ("II-B", "peptide_length")
    assert classes["RS50S_tRNAGlyGCC"] == ("II-B", "R_recycle")
    assert all(classes[s] == ("II-B", "R_term_preterm") for s in PRETERM)

    detail = parse_detail(DETAIL)
    assert len(detail) == 241, len(detail)
    assert len({s for s, _ in detail}) == 241
    assert {s for s, _ in detail} == set(ids)
    for s, cls in detail:
        assert classes[s][0] == cls, (s, cls, classes[s])

    print("PASS: 241 unique source species")
    print("PASS: class counts I=42, II-A=57, II-B=91, III=22, C=29")
    print("PASS: source species set equals detailed Markdown table")
    print("PASS: degraded/enzyme-intermediate source rules")
    print("PASS: resource Class-I contract")
    print("PASS: Pept0002, RS50S_tRNAGlyGCC and UAA pretermination decisions")
    print("NOTE: structural verification only; QSSA/kinetic validity is not tested")

if __name__ == "__main__":
    main()
