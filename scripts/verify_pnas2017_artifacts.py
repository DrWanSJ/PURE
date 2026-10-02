"""Verify frozen source bytes and freshness of the derived PNAS review package.

This checks identity, coverage and provenance, not biochemical validity or a
scientific reduction decision. It uses only the Python standard library.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
NS = {"sbml": "http://www.sbml.org/sbml/level2/version4"}


def file(path: str) -> Path:
    candidate = (ROOT / path).resolve()
    if not candidate.is_relative_to(ROOT.resolve()):
        raise ValueError(f"Path escapes repository: {path}")
    return candidate


def sha(path: str) -> str:
    return hashlib.sha256(file(path).read_bytes()).hexdigest()


def registered_hashes(mapping: dict[str, str], label: str) -> None:
    for path, expected in mapping.items():
        actual = sha(path)
        if actual != expected:
            raise ValueError(f"{label}: {path}: {actual} != {expected}")


def rows(path: str) -> list[dict[str, str]]:
    with file(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def exact_ids(actual: list[str], expected: list[str], label: str) -> None:
    if len(actual) != len(set(actual)) or set(actual) != set(expected):
        raise ValueError(f"{label}: duplicate, missing or extra original SBML IDs")


REVIEW_PATH = "docs/reduction/human_reduction_review.md"
REVIEW_BASELINE_COMMIT = "0a72448ff20db8e58593a9910b8944c121750778"
REVIEW_SYNC_COMMIT = "d5874dec053e6ff210e3d1843bb7735ebe3ba84a"
REVIEW_CONTRACT_COMMIT = "678fcb709324142454fd7a80cb6185c64b900510"


def verify_review_sync() -> str:
    """Verify one exact, committed human-approved documentation transition.

    The historical renderer manifest is preserved, rather than rehashed to
    accept current bytes. No source or kinetic-reduction predicate changes.
    """
    record = json.loads(file("docs/reduction/review_sync_manifest_20260930.json").read_text(encoding="utf-8"))
    if (record["schema"] != "pnas2017_review_sync/v1"
            or record["status"] != "EXACT_HUMAN_APPROVED_DOCUMENTATION_SYNC_NOT_KINETIC_APPROVAL"
            or record["baseline_commit"] != REVIEW_BASELINE_COMMIT
            or record["approved_sync_commit"] != REVIEW_SYNC_COMMIT
            or record["information_contract_commit"] != REVIEW_CONTRACT_COMMIT):
        raise ValueError("Unknown review synchronization authority")

    def at(commit: str, path: str) -> bytes:
        file(path)  # Retain the repository path-boundary check.
        return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)

    def digest(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    for commit in (REVIEW_SYNC_COMMIT, REVIEW_CONTRACT_COMMIT):
        subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=ROOT, check=True)
    paths = subprocess.check_output(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", REVIEW_SYNC_COMMIT],
        cwd=ROOT, text=True).splitlines()
    if paths != [REVIEW_PATH]:
        raise ValueError("Approved review-sync commit changes other artifacts")
    preserved = record["preserved_render_manifest"]
    if preserved["path"] != "docs/reduction/review_render_manifest.json":
        raise ValueError("Review-sync baseline manifest path changed")
    old_manifest = at(REVIEW_BASELINE_COMMIT, preserved["path"])
    if (file(preserved["path"]).read_bytes() != old_manifest
            or digest(old_manifest) != preserved["sha256"]):
        raise ValueError("Historical renderer manifest was altered")
    transition = record["document_transition"]
    before, after = at(REVIEW_BASELINE_COMMIT, REVIEW_PATH), at(REVIEW_SYNC_COMMIT, REVIEW_PATH)
    rendered = json.loads(old_manifest)["outputs_sha256"][REVIEW_PATH]
    if (transition["path"] != REVIEW_PATH
            or transition["rendered_sha256"] != rendered
            or digest(before) != rendered
            or transition["approved_sha256"] != digest(after)
            or file(REVIEW_PATH).read_bytes() != after):
        raise ValueError("Review document differs from exact approved transition")
    expected_basis = {
        "docs/reduction/species_information_contract_summary.md",
        "docs/reduction/species_information_contract_detailed.md",
        "docs/reduction/human_audit_sync_20260930.md",
    }
    if (set(record["information_contract_basis"]) != expected_basis
            or record["information_contract_basis_line_endings"] != "CRLF_TO_LF_FOR_MARKDOWN_ONLY"):
        raise ValueError("Review-sync information-contract basis is incomplete")
    for path, expected in record["information_contract_basis"].items():
        approved = at(REVIEW_CONTRACT_COMMIT, path)
        current = file(path).read_bytes().replace(b"\r\n", b"\n")
        if digest(approved) != expected or current != approved:
            raise ValueError(f"Approved information-contract evidence changed: {path}")
    return digest(after)


def main() -> None:
    registry = json.loads(file("references/PNAS2017_Matsuura/provenance/sources.json").read_text(encoding="utf-8"))
    if len(registry["source_files"]) != 3:
        raise ValueError("Expected three captured author-site source files")
    for record in registry["source_files"] + registry["model_copies"]:
        path = record["path"]
        if file(path).stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
            raise ValueError(f"Frozen source size/hash mismatch: {path}")
    raw = "references/PNAS2017_Matsuura/raw/fMGG_synthesis.xml"
    original = "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
    if file(raw).read_bytes() != file(original).read_bytes():
        raise ValueError("Original model differs from author-site captured bytes")

    normalized = json.loads(file("models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.provenance.json").read_text(encoding="utf-8"))
    if sha(normalized["canonical_source_path"]) != normalized["canonical_source_sha256"]:
        raise ValueError("Normalized-copy source fingerprint stale")
    if sha(normalized["normalized_path"]) != normalized["normalized_sha256"]:
        raise ValueError("Normalized-copy output fingerprint stale")
    if normalized["converted_literal_count"] != 3854 or not normalized["stoichiometric_inventory_equal_after_roundtrip"]:
        raise ValueError("Normalized-copy equivalence record incomplete")

    species = [node.attrib["id"] for node in ET.parse(file(original)).findall(".//sbml:listOfSpecies/sbml:species", NS)]
    reactions = [node.attrib["id"] for node in ET.parse(file(original)).findall(".//sbml:listOfReactions/sbml:reaction", NS)]
    if (len(species), len(reactions)) != (241, 968):
        raise ValueError("Canonical SBML count drift")
    audit = "models/pnas2017_full_reference/audit/"
    exact_ids([r["species_id"] for r in rows(audit + "species.csv")], species, "species inventory")
    exact_ids([r["reaction_id"] for r in rows(audit + "reactions.csv")], reactions, "reaction inventory")
    parameters = rows(audit + "parameters.csv")
    if len(parameters) != 968 or {r["owner_reaction_id"] for r in parameters} != set(reactions):
        raise ValueError("Reaction-local parameter inventory incomplete")
    modules = rows(audit + "modules.csv")
    if len(modules) != 26 or len({r["source_file"] for r in modules}) != 26:
        raise ValueError("Original subsystem coverage incomplete")
    if any(r["mapped_combined_reaction_count"] != r["reaction_entry_count"] for r in modules):
        raise ValueError("Original subsystem counts/mapping disagree")

    resource = json.loads(file(audit + "resource_map_manifest.json").read_text(encoding="utf-8"))
    registered_hashes(resource["input_sha256"], "resource input")
    registered_hashes(resource["output_sha256"], "resource output")
    exact_ids([r["sbml_id"] for r in rows(audit + "species_properties.csv")], species, "species properties")
    exact_ids([r["sbml_reaction_id"] for r in rows(audit + "reaction_balance_audit.csv")], reactions, "reaction balance")
    decisions = rows("docs/reduction/reduction_decisions.csv")
    exact_ids([r["sbml_reaction_id"] for r in decisions], reactions, "reduction decisions")
    if any(r["decision_status"] != "PENDING" or r["HUMAN_REVIEW_REQUIRED"] != "True" for r in decisions):
        raise ValueError("A candidate reduction was silently finalized")

    review = json.loads(file("docs/reduction/review_render_manifest.json").read_text(encoding="utf-8"))
    registered_hashes(review["inputs_sha256"], "review input")
    registered_hashes({path: digest for path, digest in review["outputs_sha256"].items()
                       if path != REVIEW_PATH}, "review output")
    verify_review_sync()
    if review["counts"]["combined_reactions"] != 968 or review["counts"]["process_review_cards"] != 16:
        raise ValueError("Researcher review coverage incomplete")
    text = file("docs/reduction/human_reduction_review.md").read_text(encoding="utf-8")
    if "[x]" in text.lower() or text.count("[ ] KEEP") != 16:
        raise ValueError("Researcher review choices were checked or cards omitted")

    run = json.loads(file("results/pnas2017_reference/rr_cvode_author_csv_20260924/run_manifest.json").read_text(encoding="utf-8"))
    registered_hashes(run["source_sha256"], "run source")
    if sha(run["effective_author_conditions_sbml"]["path"]) != run["effective_author_conditions_sbml"]["sha256"]:
        raise ValueError("Effective author-condition SBML fingerprint stale")
    if sha(run["trajectory"]["path"]) != run["trajectory"]["sha256"]:
        raise ValueError("RoadRunner trajectory fingerprint stale")
    comparison = json.loads(file("results/pnas2017_reference/rr_cvode_author_csv_20260924/engine_comparison.json").read_text(encoding="utf-8"))
    registered_hashes(comparison["source_files_sha256"], "engine comparison input")
    if comparison["status"] != "ENGINE_COMPARISON_DIAGNOSTIC_NO_PREREGISTERED_PASS_THRESHOLD":
        raise ValueError("Engine comparison status unexpectedly changed")

    print(json.dumps({"status": "PROVENANCE_AND_COVERAGE_VERIFIED_NOT_SCIENTIFIC_VALIDATION", "sources": 3, "species": 241, "reactions": 968, "modules": 26, "pending_decisions": len(decisions), "review_cards": 16}, indent=2))


if __name__ == "__main__":
    main()
