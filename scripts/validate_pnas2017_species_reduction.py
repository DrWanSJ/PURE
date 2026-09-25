#!/usr/bin/env python3
"""Independently validate the PNAS 2017 species-level reduction map.

Reads the committed artefacts (not the generator's internal state) and asserts
the scientific invariants, the preregistered tallies, and the self-containedness
of the pipeline. Exits non-zero on the first failing group.

Usage:  python scripts/validate_pnas2017_species_reduction.py
"""
import ast
import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")
MAP_CSV = os.path.join(AUDIT, "species_reduction_map.csv")
MAP_JSON = os.path.join(AUDIT, "species_reduction_map.json")
MAP_MD = os.path.join(ROOT, "docs", "reduction", "species_reduction_map.md")
SBML_REL = "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
SBML = os.path.join(ROOT, *SBML_REL.split("/"))
RAW_SBML = os.path.join(ROOT, "references", "PNAS2017_Matsuura", "raw",
                        "fMGG_synthesis.xml")
SCRIPT = os.path.join(ROOT, "scripts", "analyze_pnas2017_species_reduction.py")
PROVENANCE = os.path.join(ROOT, "data", "provenance.csv")
PROVENANCE_ITEM = "Matsuura_2017_combined_SBML"
N_SPECIES = 241
N_REACTIONS = 968
CLASS_TOTALS = {"KEEP_EXPLICIT": 23, "LUMP_FUNCTIONAL_POOL": 132,
                "ENZYME_INTERMEDIATE": 57, "DEGRADED_SINK": 29, "REVIEW": 0}
REVIEW_TOTALS = {"NONE": 204, "SCIENTIFIC_DECISION_REQUIRED": 12,
                 "MODULE_LABEL_CONFLICT_ONLY": 25}
RESOURCES = ["ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr"]
DEGRADED = "_degraded"
PEPTIDYL = re.compile(r"^(Pept\d+)(tRNA.*)$")

failures = []


def check(group, ok, detail):
    if not ok:
        failures.append(f"[{group}] {detail}")
    return ok


def main():
    with open(MAP_CSV, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with open(MAP_JSON, encoding="utf-8") as fh:
        payload = json.load(fh)
    with open(os.path.join(AUDIT, "inventory_summary.json"), encoding="utf-8") as fh:
        summary = json.load(fh)
    with open(os.path.join(AUDIT, "species.csv"), newline="", encoding="utf-8") as fh:
        audit_species = list(csv.DictReader(fh))
    by_id = {r["species_id"]: r for r in rows}
    pools = payload["pools"]

    # --- B. structural counts ------------------------------------------------
    check("B.counts", len(rows) == N_SPECIES,
          f"map has {len(rows)} species, expected {N_SPECIES}")
    check("B.counts", len(audit_species) == N_SPECIES,
          f"audit species table has {len(audit_species)} rows")
    check("B.counts", summary["reaction_count"] == N_REACTIONS,
          f"reaction count {summary['reaction_count']}")
    check("B.counts", {r["species_id"] for r in rows}
          == {r["id"] for r in audit_species},
          "map species set != SBML audit species set")
    check("B.counts", payload["meta"]["n_species"] == N_SPECIES
          and payload["meta"]["n_reactions"] == N_REACTIONS
          and payload["meta"]["model_id"] == summary["model_id"],
          "json meta counts/model_id mismatch")

    # --- C. preregistered tallies -------------------------------------------
    cc = {c: sum(1 for r in rows if r["primary_reduction_class"] == c)
          for c in CLASS_TOTALS}
    rc = {c: sum(1 for r in rows if r["scientific_review_class"] == c)
          for c in REVIEW_TOTALS}
    check("C.classes", cc == CLASS_TOTALS, f"class totals {cc}")
    check("C.review", rc == REVIEW_TOTALS, f"review totals {rc}")
    check("C.classes", cc == payload["meta"]["reduction_class_counts"]
          and rc == payload["meta"]["scientific_review_counts"],
          "json meta tallies disagree with csv")
    flagged = {r["species_id"] for r in rows
               if r["scientific_review_class"] == "SCIENTIFIC_DECISION_REQUIRED"}
    check("C.review", flagged == {s for g in payload["meta"]["decision_groups"].values()
                                  for s in g},
          "flagged species set != decision-group membership")
    check("C.groups", len(payload["meta"]["decision_groups"]) == 3,
          f"expected 3 decision groups, got "
          f"{sorted(payload['meta']['decision_groups'])}")

    # --- D. scientific invariants -------------------------------------------
    # RS30S and RS50S stay distinct moieties; RS70S feeds both.
    check("D.ribosome", "RS30S_active_pool" in pools and "RS50S_active_pool" in pools
          and "R_total" not in pools, "ribosome subunit pools must stay separate")
    for sp in [s for s in by_id if "RS70S" in s]:
        r = by_id[sp]
        check("D.ribosome", r["n_RS30S"] == r["n_RS50S"] == "1",
              f"{sp} must contribute one RS30S and one RS50S moiety")
        check("D.ribosome", f"RS30S_{'degraded' if sp.endswith(DEGRADED) else 'active'}_pool"
              in r["conservation_family"] and f"RS50S_{'degraded' if sp.endswith(DEGRADED) else 'active'}_pool"
              in r["conservation_family"], f"{sp} missing from a subunit pool")
    # Peptidyl-tRNA carries BOTH a peptide and a tRNA moiety -> double ledger.
    pept_trna = [s for s in by_id if PEPTIDYL.match(s[: -len(DEGRADED)]
                 if s.endswith(DEGRADED) else s)]
    check("D.peptidyl", len(pept_trna) >= 2,
          f"only {len(pept_trna)} peptidyl-tRNA states found")
    for sp in pept_trna:
        r = by_id[sp]
        check("D.peptidyl", int(r["n_peptide"]) >= 1 and int(r["n_tRNA"]) >= 1,
              f"{sp} not counted in both peptide and tRNA ledgers")
    for sp in ("GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU"):
        check("D.peptidyl", by_id[sp]["primary_reduction_class"] == "KEEP_EXPLICIT",
              f"aminoacyl-tRNA {sp} must not be pooled with peptidyl-tRNA")
    # Resource identities stay distinct.
    for a, b in (("ATP", "ADP"), ("ATP", "AMP"), ("ADP", "AMP"), ("GTP", "GDP"),
                 ("GTP", "GMP"), ("GDP", "GMP"), ("PO4", "PPi"), ("CP", "Cr")):
        merged = [r["species_id"] for r in rows if r[f"n_{a}"] != "0" and r[f"n_{b}"] != "0"
                  and r["species_id"] in RESOURCES]
        check("D.resources", not merged, f"{a}/{b} merged on {merged}")
        check("D.resources", by_id[a]["primary_reduction_class"] == "KEEP_EXPLICIT"
              and by_id[b]["primary_reduction_class"] == "KEEP_EXPLICIT",
              f"{a} or {b} is not KEEP_EXPLICIT")
    check("D.resources", any("NTP" in r["candidate_coarse_variable"] for r in rows) is False,
          "NTP/NXP must not become a reduction class")
    # MK numeric binding sites resolved by topology, not left unknown.
    for sp, expect in (("MK_ADP_1", 1), ("MK_ADP_2", 1), ("MK_ADP_ADP", 2)):
        check("D.MK", by_id[sp]["n_ADP"] == str(expect),
              f"{sp} n_ADP={by_id[sp]['n_ADP']} expected {expect}")
        check("D.MK", by_id[sp]["primary_reduction_class"] == "ENZYME_INTERMEDIATE",
              f"{sp} should be an enzyme intermediate, not REVIEW")
        check("D.MK", "MK_active_pool" in by_id[sp]["conservation_family"],
              f"{sp} missing from MK_active_pool")
    # Three-layer pool discipline.
    for name, members in pools.items():
        if name.startswith("coarse:"):
            continue
        if name.endswith("_family_total"):
            base = name[: -len("_family_total")]
            union = sorted(set(pools.get(f"{base}_active_pool", [])
                               + pools.get(f"{base}_degraded_pool", [])))
            check("D.pools", members == union, f"{name} != active_pool + degraded_pool")
            continue
        base = (name[: -len("_active_pool")] if name.endswith("_active_pool")
                else name[: -len("_degraded_pool")])
        for sp in members:
            comps = by_id[sp]["detected_components"].split(" + ")
            ok = (base in comps or "RS70S" in comps) if base in ("RS30S", "RS50S") \
                else base in comps
            check("D.pools", ok, f"{sp} in {name} without moiety {base}")
            if name.endswith("_active_pool"):
                check("D.pools", not sp.endswith(DEGRADED),
                      f"degraded {sp} leaked into {name}")
            else:
                check("D.pools", sp.endswith(DEGRADED),
                      f"non-degraded {sp} in {name}")
    for r in rows:
        if r["primary_reduction_class"] == "DEGRADED_SINK":
            check("D.pools", r["species_id"].endswith(DEGRADED),
                  f"{r['species_id']} class/suffix disagreement")
            check("D.pools", "_active_pool" not in r["conservation_family"],
                  f"degraded {r['species_id']} entered an active pool")

    # --- A. source immutability ---------------------------------------------
    with open(PROVENANCE, newline="", encoding="utf-8") as fh:
        registered = next((r["sha256"] for r in csv.DictReader(fh)
                           if r["item"] == PROVENANCE_ITEM), None)
    check("A.sha256", bool(registered), f"{PROVENANCE_ITEM} not registered in provenance")
    digest = hashlib.sha256(open(SBML, "rb").read()).hexdigest()
    raw_digest = hashlib.sha256(open(RAW_SBML, "rb").read()).hexdigest()
    check("A.sha256", digest == registered,
          f"reference SBML digest {digest} != registered {registered}")
    check("A.sha256", raw_digest == registered,
          f"immutable raw drop digest {raw_digest} != registered {registered}")
    check("A.sha256", payload["meta"]["sbml_sha256"] == digest,
          "json meta records a different digest than the file on disk")
    check("A.sha256", payload["meta"].get("sbml_sha256_registered_in")
          == f"data/provenance.csv::{PROVENANCE_ITEM}",
          "json meta must name the registered provenance source of the digest")

    # --- E. self-containedness ----------------------------------------------
    with open(SCRIPT, encoding="utf-8") as fh:
        src = fh.read()
    check("E.scratch", "pnas2017_sbml_visualization" not in src
          and "visualize_fMGG" not in src,
          "generator must not reference the scratch visualisation helper")
    check("E.scratch", "importlib" not in src,
          "generator must not import modules from outside the tracked package")
    check("E.provenance", registered not in src,
          "generator must not hardcode a second copy of the registered digest")
    # Prose may mention scratch/; no string constant may name it as a path.
    consts = [n.value for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    bad = [s for s in consts if s == "scratch"
           or s.startswith("scratch" + os.sep) or s.startswith(os.sep + "scratch")]
    check("E.scratch", not bad, f"generator uses a scratch/ path constant: {bad}")
    abs_path = re.compile(r"[A-Za-z]:[\\/]Users", re.I)
    for label, path in (("csv", MAP_CSV), ("json", MAP_JSON), ("md", MAP_MD),
                        ("script", SCRIPT)):
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        check("E.paths", not abs_path.search(text),
              f"{label} contains an absolute workstation path")
    check("E.paths", payload["meta"]["source_sbml"] == SBML_REL,
          "json metadata must record the repository-relative source path")
    check("E.docs", os.path.exists(MAP_MD), "docs/reduction/species_reduction_map.md missing")

    if failures:
        print("VALIDATION FAILURES: %d" % len(failures))
        for f in failures:
            print("  " + f)
        return 1
    print("PASS: species reduction map validated")
    print(f"  species={len(rows)} reactions={summary['reaction_count']}")
    print(f"  classes={cc}")
    print(f"  review={rc}")
    print(f"  pools={len(pools)} decision_groups="
          f"{sorted(payload['meta']['decision_groups'])}")
    print(f"  SBML sha256 verified: {digest[:16]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
