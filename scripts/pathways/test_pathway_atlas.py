#!/usr/bin/env python3
"""Run independent Phase A gates, ten actual mutation controls and rebuilds.

Each counterexample mutates the generated artifact in memory and invokes the
same source-based validator used on the real outputs. No control has a special
test-only detector. Failures append to failure_evidence.jsonl and are retained.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from verify_pathway_atlas import (AUTHOR, DEFAULT_OUTPUT, MM, RED, ROOT, SOURCE,
                                 Validator, constant, digest, load_artifacts,
                                 markdown_equations, require)


OUTPUTS = ("glyrs_metrs_graph.json", "glyrs_metrs_pathway_index.csv", "glyrs_metrs_sample.md")


def replace_walk(graph, enzyme, rids):
    module = graph["modules"][enzyme]
    transitions = {item["reaction_id"]: item for item in module["transitions"]}
    steps = [copy.deepcopy(transitions[rid]) for rid in rids]
    path = module["paths"][0]
    # Deliberately use each local edge's endpoint; source validation must detect
    # the fact that the next reaction does not consume the preceding endpoint.
    states = [steps[0]["carrier_before"][0]] + [step["carrier_after"][0] for step in steps]
    path.update({"reaction_ids": list(rids), "states": states, "steps": steps,
                 "start": states[0], "end": states[-1], "types": ["ALTERNATIVE_ENTRY"],
                 "target_product": None, "reference_feasible": False, "rejoins": []})
    return path


def controls(validator, graph, rows, markdown):
    cases = []

    mutated = copy.deepcopy(graph)
    replace_walk(mutated, "GlyRS", ["re0000000206", "re0000000196"])
    cases.append((1, "Forced 0206 -> 0196", 2, mutated, rows, markdown, "carrier continuity"))

    mutated = copy.deepcopy(graph)
    replace_walk(mutated, "GlyRS", ["re0000000197", "re0000000206", "re0000000196", "re0000000194"])
    cases.append((2, "Mutually exclusive exits presented as four serial steps", 2, mutated, rows, markdown, "carrier continuity"))

    mutated = copy.deepcopy(graph)
    path = next(path for path in mutated["modules"]["GlyRS"]["paths"] if "re0000000136" in path["reaction_ids"])
    step = next(step for step in path["steps"] if step["reaction_id"] == "re0000000136")
    require("ATP" in step["other_reactants"], "Negative-control setup requires actual ATP cosubstrate")
    del step["other_reactants"]["ATP"]
    cases.append((3, "Required ATP omitted from a real pathway step", 2, mutated, rows, markdown, "required other reactants"))

    mutated = copy.deepcopy(graph)
    zero = next(item for item in mutated["modules"]["GlyRS"]["transitions"] if validator.values[item["reaction_id"]] == 0)
    path = replace_walk(mutated, "GlyRS", [zero["reaction_id"]])
    path["reference_feasible"] = True
    cases.append((4, "Zero author-reference parameter claimed enabled", 2, mutated, rows, markdown, "reference feasibility"))

    mutated = copy.deepcopy(graph)
    gly = next(item for item in mutated["modules"]["GlyRS"]["transitions"] if "ATP" in item["other_reactants"] and item["carrier_before"] == ["GlyRS"])
    met = next(item for item in mutated["modules"]["MetRS"]["transitions"] if "ATP" in item["other_reactants"] and item["carrier_before"] == ["MetRS"])
    path = mutated["modules"]["GlyRS"]["paths"][0]
    path.update({"reaction_ids": [gly["reaction_id"], met["reaction_id"]], "states": ["GlyRS", gly["carrier_after"][0], met["carrier_after"][0]],
                 "steps": [copy.deepcopy(gly), copy.deepcopy(met)], "start": "GlyRS", "end": met["carrier_after"][0],
                 "types": ["ALTERNATIVE_ENTRY"], "target_product": None, "reference_feasible": True, "rejoins": []})
    cases.append((5, "Different enzyme carriers linked by shared ordinary ATP", 2, mutated, rows, markdown, "wrong carrier"))

    mutated = copy.deepcopy(graph)
    links = mutated["modules"]["GlyRS"]["cross_family_links"]
    require(bool(links), "Negative control requires real cross-family connection")
    removed = links.pop(0)
    cases.append((6, f"Real cross-RFAM connection deleted: {removed}", 3, mutated, rows, markdown, "cross-RFAM completeness"))

    mutated = copy.deepcopy(graph)
    component = next(item for item in mutated["modules"]["GlyRS"]["sccs"] if item["cyclic"])
    component["cyclic"] = False
    cases.append((7, "Directed cyclic SCC misrepresented as DAG component", 3, mutated, rows, markdown, "SCC cycle evidence"))

    mutated = copy.deepcopy(graph)
    mutated["reactions"]["re0000000414"]["products"]["PO4"] = "1"
    cases.append((8, "Original PPiase outlet 0414 changed from 2 PO4 to PO4", 1, mutated, rows, markdown, "source coefficient"))

    mutated = copy.deepcopy(graph)
    shared = mutated["coverage"]["shared_path_reaction_count"]
    require(shared > 0, "Negative-control setup requires shared pathway reactions")
    mutated["coverage"]["unique_reaction_count"] += shared
    cases.append((9, "Shared reaction IDs double-counted as unique coverage", 4, mutated, rows, markdown, "unique coverage"))

    mutated = copy.deepcopy(graph)
    mutated["modules"]["GlyRS"]["paths"][0]["evidence_status"] = "VALIDATED"
    cases.append((10, "Path promoted beyond bounded structural evidence", 2, mutated, rows, markdown, "scientific evidence boundary"))

    results = []
    for number, name, gate, changed_graph, changed_rows, changed_markdown, detection in cases:
        try:
            getattr(validator, f"gate_{gate}")(changed_graph, changed_rows, changed_markdown)
        except AssertionError as error:
            results.append({"control": number, "name": name, "gate": gate, "expected": "REJECT",
                            "actual": "REJECT", "status": "PASS", "expected_detection": detection,
                            "observed_error": str(error)})
        except Exception as error:
            results.append({"control": number, "name": name, "gate": gate, "expected": "REJECT",
                            "actual": "UNEXPECTED_ERROR", "status": "FAIL", "expected_detection": detection,
                            "observed_error": f"{type(error).__name__}: {error}"})
        else:
            results.append({"control": number, "name": name, "gate": gate, "expected": "REJECT",
                            "actual": "ACCEPT", "status": "FAIL", "expected_detection": detection})
    return results


def supplemental_checks(validator, graph, rows, markdown):
    """Verify rendered text and the second required-cosubstrate failure too."""
    expressions = {
        '<cn type="rational">3<sep/>2</cn>': Fraction(3, 2),
        '<cn type="e-notation">2<sep/>-2</cn>': Fraction(1, 50),
        '<apply><times/><cn>2</cn><cn>3</cn></apply>': Fraction(6),
        '<apply><divide/><cn>1</cn><cn>4</cn></apply>': Fraction(1, 4),
    }
    for expression, expected in expressions.items():
        node = ET.fromstring(f'<math xmlns="{MM[1:-1]}">{expression}</math>')
        require(constant(node) == expected, f"Exact MathML constant regression {expression}")
    try:
        constant(ET.fromstring(f'<math xmlns="{MM[1:-1]}"><ci>variable</ci></math>'))
    except AssertionError:
        pass
    else:
        raise AssertionError("Variable stoichiometryMath must not silently become one")

    detail = markdown_equations(markdown)["re0000000136"][0][0][1]
    require("ATP + " in detail, "Markdown mutation setup requires visible ATP")
    corrupted_markdown = markdown.replace(detail, detail.replace("ATP + ", "", 1), 1)
    try:
        validator.gate_1(graph, rows, corrupted_markdown)
    except AssertionError as error:
        require("Actual Markdown equation" in str(error), f"Markdown rejection must arise from actual displayed equation: {error}")
        markdown_error = str(error)
    else:
        raise AssertionError("Corrupt actual Markdown equation was accepted")

    corrupted = copy.deepcopy(graph)
    path = next(path for path in corrupted["modules"]["GlyRS"]["paths"] if "re0000000205" in path["reaction_ids"])
    step = next(step for step in path["steps"] if step["reaction_id"] == "re0000000205")
    del step["other_reactants"]["tRNAGlyGCC"]
    try:
        validator.gate_2(corrupted, rows, markdown)
    except AssertionError as error:
        require("Required other reactants" in str(error), f"tRNA omission rejected for wrong reason: {error}")
        trna_error = str(error)
    else:
        raise AssertionError("Missing tRNA cosubstrate was accepted")
    return {"status": "PASS", "constant_mathml_regressions": 5,
            "actual_markdown_equation_mutation": markdown_error, "required_trna_mutation": trna_error}


def protected_snapshot():
    """Snapshot tracked source/research bytes; new pathway outputs are excluded."""
    result = subprocess.run(["git", "ls-files", "-z", "models", "references", "results", "docs/reduction"],
                            cwd=ROOT, capture_output=True, check=True)
    paths = [ROOT / name for name in result.stdout.decode("utf-8").split("\0") if name]
    return {path.relative_to(ROOT).as_posix(): digest(path) for path in paths if path.is_file() and DEFAULT_OUTPUT not in path.parents}


def reproducibility(output_dir):
    before = protected_snapshot()
    with tempfile.TemporaryDirectory(prefix="pnas-pathway-reproduction-") as temp:
        directories = [Path(temp) / "run1", Path(temp) / "run2"]
        runs = []
        for directory in directories:
            command = [sys.executable, str(ROOT / "scripts/pathways/build_pathway_atlas.py"), "--output-dir", str(directory)]
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
            runs.append({"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
            require(completed.returncode == 0, f"Reproducibility builder failed: {runs[-1]}")
        hashes = {}
        for name in OUTPUTS:
            values = [digest(directory / name) for directory in directories]
            require(values[0] == values[1] == digest(output_dir / name), f"Reproducibility mismatch: {name}")
            hashes[name] = values[0]
    after = protected_snapshot()
    require(before == after, "Builder modified protected existing scientific/source files")
    return {"status": "PASS", "independent_builder_runs": 2, "matches_published_artifact_bytes": True,
            "protected_existing_files_unchanged": len(before), "artifact_sha256": hashes, "runs": runs}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_failure(output_dir, report):
    if report["structural_status"] == "PASS":
        return
    evidence = {"recorded_at_utc": datetime.now(timezone.utc).isoformat(), "report": report}
    with (output_dir / "failure_evidence.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(evidence, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output_dir = args.output_dir
    validator = Validator()
    graph, rows, markdown = load_artifacts(output_dir)
    report = validator.run(graph, rows, markdown)
    if report["structural_status"] != "PASS":
        report["gates"].append({"gate": 5, "name": "Negative Controls", "status": "NOT_RUN", "reason": "Baseline gates must pass before mutations have interpretable outcomes"})
        append_failure(output_dir, report)
        write_json(output_dir / "validation_report.json", report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    negatives = controls(validator, graph, rows, markdown)
    negative_status = "PASS" if len(negatives) == 10 and all(item["status"] == "PASS" for item in negatives) else "FAIL"
    negative_report = {"schema_version": 1, "phase": "A", "status": negative_status,
                       "controls_executed": len(negatives), "controls": negatives}
    write_json(output_dir / "negative_controls.json", negative_report)
    report["gates"].append({"gate": 5, "name": "Negative Controls", "status": negative_status,
                            "evidence": {"actual_mutations": len(negatives), "rejected_as_expected": sum(item["status"] == "PASS" for item in negatives)}})
    for name, operation in (("supplemental_checks", lambda: supplemental_checks(validator, graph, rows, markdown)),
                            ("reproducibility", lambda: reproducibility(output_dir))):
        try:
            report[name] = operation()
        except Exception as error:
            report[name] = {"status": "FAIL", "error": f"{type(error).__name__}: {error}"}
    report["structural_status"] = "PASS" if all(item["status"] == "PASS" for item in report["gates"]) and all(report[name]["status"] == "PASS" for name in ("supplemental_checks", "reproducibility")) else "FAIL"
    append_failure(output_dir, report)
    write_json(output_dir / "validation_report.json", report)
    print(json.dumps({"structural_status": report["structural_status"], "phase": "A", "scientific_status": "HUMAN_REVIEW_REQUIRED",
                      "gates": [{"gate": gate["gate"], "status": gate["status"]} for gate in report["gates"]],
                      "negative_controls": negative_status, "reproducibility": report["reproducibility"],
                      "supplemental_checks": report["supplemental_checks"]}, indent=2, sort_keys=True))
    return 0 if report["structural_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
