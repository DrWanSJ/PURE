#!/usr/bin/env python3
"""Verify migration bytes, main authority, and preserved candidate statuses.

This verifies evidence integrity. It does not accept a scientific reduction.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

from verify_pnas2017_artifacts import REVIEW_PATH, REVIEW_SYNC_COMMIT, verify_review_sync


ROOT = Path(__file__).resolve().parents[1]
MAIN = "0a72448ff20db8e58593a9910b8944c121750778"
RESEARCH = "025fd340300a56f069c2136ea8bb0ff542b046d4"
OUT = ROOT / "docs/audit/pnas2017_integration/verification.json"


def data(rel: str) -> bytes:
    path = (ROOT / rel).resolve()
    if not path.is_relative_to(ROOT.resolve()):
        raise ValueError(f"Path escapes repository: {rel}")
    return path.read_bytes()


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_object(rev_path: str) -> bytes:
    return subprocess.check_output(["git", "show", rev_path], cwd=ROOT)


def git_blob(rev_path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", rev_path], cwd=ROOT, text=True
    ).strip()


def main() -> int:
    checks: list[dict] = []

    def record(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    publisher = json.loads(data("references/PNAS2017_Matsuura/provenance/publisher_capture.json"))
    files = publisher["files"]
    sd = sorted(int(m.group(1)) for x in files if
                (m := re.search(r"pnas\.1615351114\.sd(\d\d)\.xlsx$", x["path"])))
    record("P1_expected_source_set", len(files) == 30 and sd == list(range(1, 30))
           and sum(x["path"].endswith(".pdf") for x in files) == 1,
           f"{len(files)} captured files; {len(sd)} supplements")
    wrong = []
    for item in files:
        content = data(item["path"])
        if (len(content) != item["bytes"] or sha(content) != item["sha256"]
                or git_blob(f"{RESEARCH}:{item['path']}") != item["research_git_blob_sha1"]
                or content != git_object(f"{RESEARCH}:{item['path']}")):
            wrong.append(item["path"])
    record("P1_source_bytes", not wrong, f"{len(files)} SHA-256, sizes and research blobs checked; mismatches={wrong}")

    frozen = [
        "models/pnas2017_full_reference/original/fMGG_synthesis.xml",
        "models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml",
        "models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.provenance.json",
        "models/pnas2017_full_reference/audit/species.csv",
        "models/pnas2017_full_reference/audit/reactions.csv",
        "models/pnas2017_full_reference/audit/parameters.csv",
        "models/pnas2017_full_reference/audit/modules.csv",
        "models/pnas2017_full_reference/audit/species_properties.csv",
        "models/pnas2017_full_reference/audit/reaction_balance_audit.csv",
        "docs/reduction/reduction_decisions.csv",
        "docs/reduction/human_reduction_review.md",
    ]
    verify_review_sync()
    changed = [p for p in frozen if data(p) != git_object(
        f"{REVIEW_SYNC_COMMIT if p == REVIEW_PATH else MAIN}:{p}")]
    record("main_authority_unchanged", not changed,
           f"{len(frozen) - 1} canonical/normalized/generated files unchanged vs main {MAIN}; "
           f"review matches exact approved documentation sync {REVIEW_SYNC_COMMIT}; changed={changed}")
    canonical = data(frozen[0])
    author = data("references/PNAS2017_Matsuura/raw/fMGG_synthesis.xml")
    record("canonical_author_identity", canonical == author,
           f"canonical SHA-256={sha(canonical)}")

    inputs = json.loads(data("docs/audit/pnas2017_research_inputs_025fd34/snapshot_manifest.json"))
    wrong = []
    for item in inputs["files"]:
        content = data(item["archive_path"])
        if (len(content) != item["bytes"] or sha(content) != item["sha256"]
                or content != git_object(f"{RESEARCH}:{item['source_path']}")
                or git_blob(f"{RESEARCH}:{item['source_path']}") != item["git_blob"]):
            wrong.append(item["source_path"])
    record("historical_input_snapshot", not wrong and len(inputs["files"]) == 38,
           f"{len(inputs['files'])} research inputs; mismatches={wrong}")
    runner = inputs["historical_runner"]
    old = data(runner["archive_path"])
    record("historical_runner_revision", len(old) == runner["bytes"]
           and sha(old) == runner["sha256"]
           and old == git_object(runner["source_revision"]),
           f"source={runner['source_revision']}")

    archive = json.loads(data("results/pnas2017_reference/historical_archive_manifest.json"))
    wrong = []
    for item in archive["files"]:
        content = data(item["path"])
        if (len(content) != item["bytes"] or sha(content) != item["sha256"]
                or content != git_object(f"{RESEARCH}:{item['path']}")
                or git_blob(f"{RESEARCH}:{item['path']}") != item["git_blob"]):
            wrong.append(item["path"])
    record("historical_run_archive", not wrong and len(archive["files"]) == 179,
           f"{len(archive['files'])} run files; mismatches={wrong}")

    prefixes = (
        "docs/audit/pnas2017_aminoacylation_reduction_v1/",
        "docs/audit/pnas2017_aminoacylation_A3b/",
        "docs/audit/pnas2017_aminoacylation_A3b_r12/",
        "docs/audit/pnas2017_aminoacylation_A3c/",
    )
    historical_paths = [path for prefix in prefixes for path in subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", RESEARCH, prefix],
        cwd=ROOT, text=True).splitlines()]
    changed = [path for path in historical_paths if
               git_blob(f"HEAD:{path}") != git_blob(f"{RESEARCH}:{path}")]
    record("historical_candidate_records", not changed and len(historical_paths) == 65,
           f"{len(historical_paths)} original Git blobs; changed={changed}")

    a3a = data("docs/reduction/aminoacylation_A3a_final_status.md")
    a3b = json.loads(data("docs/audit/pnas2017_aminoacylation_A3b/A3b21_S0_smoke_gate.json"))
    r12 = json.loads(data("docs/audit/pnas2017_aminoacylation_A3b_r12/A3br12_S0_smoke_gate.json"))
    a3c = json.loads(data("docs/audit/pnas2017_aminoacylation_A3c/a3c_eligibility.json"))
    open_text = data("docs/reduction/open_scientific_decisions.md").decode("utf-8")
    statuses_ok = (b"FAILED_VALIDATION_ON_REFERENCE_DOMAIN" in a3a
                   and a3b["outcome"] == "FAILED_SMOKE_CLOSURE_FEASIBILITY"
                   and r12["outcome"] == "BLOCKED_NUMERICAL_COORDINATE_DEFECT"
                   and a3c["n_eligible"] == 0 and len(a3c["states"]) == 21
                   and all(f"OPEN-{n:02d}" in open_text for n in range(1, 9)))
    record("historical_status_and_open_decisions", statuses_ok,
           "A3a failed; A3b-21 failed; A3b-r12 blocked; A3c 0/21; OPEN-01..08")
    core = ROOT / "models/pure_reduced_core"
    approved = list(core.glob("*.xml")) if core.exists() else []
    record("no_reduced_core_promoted", not approved and
           b"NOT YET APPROVED" in data("docs/reduction/open_scientific_decisions.md"),
           f"reduced XML files={len(approved)}")

    graph = json.loads(data("docs/audit/pnas2017_integration/evidence_graph.json"))
    nodes = {item["id"]: item for item in graph["nodes"]}
    edges_ok = all(a in nodes and b in nodes for a, b, _ in graph["edges"])
    paths_ok = all((ROOT / item["path"]).is_file() for item in nodes.values())
    source_ok = nodes["canonical_sbml"]["sha256"] == sha(canonical)
    record("evidence_graph_freshness", edges_ok and paths_ok and source_ok
           and len(nodes) == len(graph["nodes"]),
           f"{len(nodes)} nodes, {len(graph['edges'])} edges; source fingerprint verified")

    result = {"schema": "pnas2017_integration_verification/v1",
              "authority": "Evidence-integrity check only; no reduction acceptance",
              "main_base": MAIN, "research_source": RESEARCH,
              "pass": sum(x["status"] == "PASS" for x in checks),
              "fail": sum(x["status"] == "FAIL" for x in checks),
              "checks": checks}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"pass": result["pass"], "fail": result["fail"]}))
    return 0 if result["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
