#!/usr/bin/env python3
"""Bind the pre-decision evidence package to inputs and actual verification runs.

This does not change source data, scientific decisions, or acceptance criteria.
The two verification reports are excluded from artifact hashes to avoid a
self-referential manifest/report cycle. Their commands and results are recorded
in the manifest, which is checked again after the results have been recorded.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = Path("models/pnas2017_full_reference/audit/reduction_evidence_v0")
EXCLUDED = {"evidence_manifest.json", "verification_report.json",
            "verification_final_report.json"}
VALIDATORS = ["verify_pnas2017_artifacts.py", "verify_pnas2017_integration.py",
              "verify_reaction_level_annotation.py",
              "verify_reaction_level_annotation_v2.py",
              "verify_reaction_level_contract.py",
              "verify_species_information_contract.py"]
NEW_VERIFIER = "verify_pnas2017_reduction_evidence.py"
PREREG_SHA = "b20d782edcef9a7a70bf3848acd2dbd8c240303e3507cc927f0041c56bc4969b"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True, sort_keys=True,
                  allow_nan=False)
        stream.write("\n")


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def verify_frozen(prereg: dict) -> dict:
    """Accept raw registered bytes or source-verified text checkout EOL only."""
    actual, eol = {}, []
    for name, expected in prereg["input_sha256"].items():
        data = (ROOT / name).read_bytes()
        actual[name] = sha(data)
        if actual[name] == expected:
            continue
        blob = git("show", f"{prereg['source_head']}:{name}")
        expected_blob = prereg["protected_git_blob_sha256"].get(name)
        # Only protected Markdown has a documented source/checkout distinction.
        if not (name.endswith(".md") and expected_blob == sha(blob)
                and data.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n")
                and expected in {sha(blob), sha(blob.replace(b"\r\n", b"\n")),
                                 sha(blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))}):
            raise ValueError(f"Frozen input changed: {name}")
        eol.append({"path": name, "registered_checkout_sha256": expected,
                    "current_checkout_sha256": actual[name],
                    "source_git_blob_sha256": expected_blob,
                    "status": "EXACT_LF_CRLF_EQUIVALENCE_ONLY"})
    for name, expected in prereg["protected_git_blob_sha256"].items():
        if sha(git("show", f"HEAD:{name}")) != expected:
            raise ValueError(f"Protected HEAD blob changed: {name}")
    for branch, expected in prereg["research_branches_unchanged"].items():
        if git("rev-parse", branch).decode().strip() != expected:
            raise ValueError(f"Protected research branch changed: {branch}")
    return {"current_input_sha256": actual, "checkout_eol_equivalences": eol}


def csv_inventory() -> tuple[dict, dict]:
    counts, availability = {}, {}
    for path in sorted((ROOT / AUDIT).glob("*.csv")):
        rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
        counts[path.name] = len(rows)
        by_column = {}
        for field in rows[0] if rows else []:
            vals = [row[field] for row in rows]
            na = collections.Counter(v for v in vals if v.startswith("N/A"))
            numeric = 0
            for value in vals:
                try:
                    float(value)
                    numeric += 1
                except (ValueError, TypeError):
                    pass
            if na or numeric:
                by_column[field] = {"numeric_cells": numeric,
                                    "unavailable_cells": sum(na.values()),
                                    "na_reasons": dict(sorted(na.items()))}
        record = {"columns": by_column}
        for field in ["reason", "qss_metric_status", "equilibrium_metric_status",
                      "pool_membership_status", "sequestration_metric_status",
                      "timescale_status", "informative"]:
            if rows and field in rows[0]:
                record[field] = dict(sorted(collections.Counter(row[field] for row in rows).items()))
        availability[path.name] = record
    return counts, availability


def generated_paths() -> list[Path]:
    paths = [p for p in (ROOT / AUDIT).rglob("*")
             if p.is_file() and p.name not in EXCLUDED
             and p.name != "evidence_navigation.json"]
    paths.extend((ROOT / "docs/reduction/process_quick_reference").glob("*.md"))
    paths.extend(ROOT / "docs/reduction" / n for n in
                 ["pnas2017_reduction_evidence_method.md", "pnas2017_reduction_quick_reference.md"])
    return sorted(set(p for p in paths if p.is_file()))


def make_navigation(prereg: dict, paths: list[Path]) -> Path:
    pipeline = "scripts/analyze_pnas2017_reduction_evidence.py"
    nodes = [{"id": "analysis", "path": pipeline,
              "sha256": sha((ROOT / pipeline).read_bytes()), "provenance": "INFERRED",
              "meaning": "Derived analysis, subordinate to frozen source evidence"}]
    edges = []
    for name, digest in sorted(prereg["input_sha256"].items()):
        nodes.append({"id": name, "path": name, "registered_sha256": digest,
                      "provenance": "EXTRACTED", "source_head": prereg["source_head"]})
        edges.append({"source": name, "target": "analysis", "relation": "frozen_input",
                      "provenance": "EXTRACTED"})
    for path in paths:
        name = path.relative_to(ROOT).as_posix()
        nodes.append({"id": name, "path": name, "sha256": sha(path.read_bytes()),
                      "provenance": "INFERRED"})
        edges.append({"source": "analysis", "target": name,
                      "relation": "derived_evidence_or_review_documentation",
                      "provenance": "INFERRED"})
    nodes.append({"id": "scientific_questions", "provenance": "AMBIGUOUS",
                  "questions": ["Fast and slow coordinate choices and validity domain",
                                "Authoritative absolute concentration units",
                                "Unresolved protected substrate-token composition",
                                "Initial-layer resolution and extent quadrature error"],
                  "status": "PENDING_HUMAN_REVIEW"})
    edges.append({"source": "analysis", "target": "scientific_questions",
                  "relation": "exposes_unresolved_choices", "provenance": "AMBIGUOUS"})
    path = ROOT / AUDIT / "evidence_navigation.json"
    write_json(path, {"schema": "pnas2017_evidence_navigation/v0", "nodes": nodes,
                      "edges": edges, "authority": "NAVIGATION_ONLY_NOT_SOURCE_AUTHORITY",
                      "freshness": "Verify preregistered inputs and artifact hashes before use"})
    return path


def build_manifest(results: list, verification_timestamp: str | None = None) -> dict:
    prereg_path = ROOT / AUDIT / "evidence_preregistration.json"
    if sha(prereg_path.read_bytes()) != PREREG_SHA:
        raise ValueError("Original preregistration was altered")
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    frozen = verify_frozen(prereg)
    paths = generated_paths()
    paths.append(make_navigation(prereg, paths))
    counts, availability = csv_inventory()
    diagnostic_path = ROOT / AUDIT / "analysis_diagnostics.json"
    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8")) if diagnostic_path.exists() else {}
    scripts = sorted(p for p in (ROOT / "scripts").glob("*pnas2017_reduction_evidence*.py"))
    scripts += sorted((ROOT / "scripts").glob("pnas2017_evidence_*.py"))
    # Hash all validators actually invoked, including the v1 validator's v2 dependency.
    scripts += [ROOT / "scripts" / n for n in VALIDATORS]
    versions = diagnostic.get("versions", {})
    versions["manifest_python"] = platform.python_version()
    versions["MATLAB_analysis"] = "NOT_USED"
    versions["trajectory_RoadRunner"] = "2.10.0 (preserved prior trajectory)"
    manifest = {
        "schema": "pnas2017_reduction_evidence_manifest/v0",
        "status": "EVIDENCE_PREPARATION_ONLY_NO_REDUCTION_APPROVAL",
        "source_head": prereg["source_head"], "git_head": git("rev-parse", "HEAD").decode().strip(),
        "domain": prereg["domain"], "preregistration_sha256": PREREG_SHA,
        "source_hashes": prereg["input_sha256"], **frozen,
        "protected_git_blob_sha256": prereg["protected_git_blob_sha256"],
        "input_trajectory_hashes": {prereg["trajectory"]["path"]: prereg["trajectory"]["sha256"]},
        "scripts_sha256": {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in scripts},
        "generated_artifact_sha256": {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in paths},
        "versions": versions,
        "analysis_timestamp": diagnostic.get("analysis_timestamp", dt.datetime.now(dt.timezone.utc).isoformat()),
        "row_counts": counts, "metric_availability": availability,
        "reverse_pair_count": counts.get("reverse_pair_evidence.csv"),
        "process_count": counts.get("process_timescale_evidence.csv"),
        "verification_commands": [f"python scripts/{n}" for n in VALIDATORS + [NEW_VERIFIER]] + ["git diff --check"],
        "verification_results": results,
        "verification_timestamp": verification_timestamp,
        "verification_report_cycle_policy": "Reports and manifest excluded from generated-artifact hash map; final manifest reverified after result recording",
        "decisions": {"kinetic_pending": 968, "selected_process_boxes": 0,
                      "PURE_reduced_core": "NOT_VALIDATED", "PR_3_PR_4": "UNTOUCHED"},
        "reproducibility": "All generated CSV bytes must match a second build from the frozen preregistration and inputs; see reproducibility.json when present",
    }
    write_json(ROOT / AUDIT / "evidence_manifest.json", manifest)
    return manifest


def run_command(args: list[str], command: str) -> dict:
    proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    record = {"command": command, "exit_code": proc.returncode,
              "status": "PASS" if proc.returncode == 0 else "FAIL",
              "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    print(json.dumps({"command": command, "exit_code": proc.returncode}), flush=True)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Run and record all required validators")
    args = parser.parse_args()
    results = [{"status": "NOT_YET_RUN_IN_THIS_FINALIZATION"}]
    build_manifest(results)
    if args.verify:
        results = []
        for name in VALIDATORS:
            # The existing integration validator rewrites a historical report.
            # Retain that report's bytes and capture this invocation separately.
            report = ROOT / "docs/audit/pnas2017_integration/verification.json"
            saved = report.read_bytes() if name == "verify_pnas2017_integration.py" else None
            try:
                results.append(run_command([sys.executable, str(ROOT / "scripts" / name)],
                                           f"python scripts/{name}"))
            finally:
                if saved is not None:
                    report.write_bytes(saved)
        results.append(run_command(["git", "diff", "--check"], "git diff --check"))
        build_manifest(results)
        results.append(run_command([sys.executable, str(ROOT / "scripts" / NEW_VERIFIER),
                                    "--report", str(ROOT / AUDIT / "verification_report.json")],
                                   f"python scripts/{NEW_VERIFIER}"))
        stamp = dt.datetime.now(dt.timezone.utc).isoformat()
        build_manifest(results, stamp)
        if all(r["exit_code"] == 0 for r in results):
            final = run_command([sys.executable, str(ROOT / "scripts" / NEW_VERIFIER),
                                 "--report",
                                 str(ROOT / AUDIT / "verification_final_report.json")],
                                "Independent recheck of finalized manifest")
            if final["exit_code"]:
                print(final["stdout"], final["stderr"])
                return 1
        else:
            for item in results:
                if item["exit_code"]:
                    print(item["stdout"], item["stderr"])
            return 1
    print("Evidence manifest written; no kinetic reduction approved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
