#!/usr/bin/env python3
"""Seal the complete preregistered R3 grid and derive its pilot verdict."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

from verify_reduction_audit_v0 import ROOT


GRID = ROOT / "docs/reduction/r3_validation_grid_v1.csv"
EXPECTED = (
    "R3_BASE", "R3_GLYRS_LOW", "R3_GLYRS_HIGH", "R3_METRS_LOW",
    "R3_METRS_HIGH", "R3_GLY_LOW", "R3_MET_LOW", "R3_TRNA_LOW",
    "R3_ATP_LOW", "R3_ADVERSE",
)
INPUTS = {
    "canonical_sbml": "models/pnas2017_full_reference/original/fMGG_synthesis.xml",
    "grid": "docs/reduction/r3_validation_grid_v1.csv",
    "method": "docs/reduction/r3_aminoacylation_qssa_method.md",
    "protocol": "docs/reduction/r3_coupled_validation_protocol_v1.md",
    "reaction_map": "docs/reduction/r3_source_reaction_candidate_map_v1.csv",
    "aminoacylation_reactions": "models/pnas2017_full_reference/audit/aminoacylation_reactions.csv",
    "runtime_v1": "scripts/r3_resource_total_runtime_v1.py",
    "runtime_v2": "scripts/r3_resource_total_runtime_v2.py",
    "runner": "scripts/run_r3_coupled_grid_v1.py",
}
NUMERIC_KEYS = (
    "all_species_E_inf", "class_I_E_inf", "aminoacylation_rate_E_inf",
    "aminoacylation_extent_E_inf", "all_directed_rate_E_inf",
    "all_directed_extent_E_inf", "full_material_balance_abs",
    "reduced_slow_balance_abs", "source_general_inventory_drift_abs",
    "minimum_full_concentration", "minimum_reduced_concentration",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(condition: str, directory: Path, expected_inputs: dict) -> dict:
    result_path = directory / "result.json"
    manifest = read_json(directory / "manifest.json")
    result = read_json(result_path)
    assert result["condition_id"] == condition == manifest["condition_id"]
    assert result["run_kind"] == "REGISTERED_R3_GRID_CONDITION"
    assert result["status"] == manifest["result_status"]
    assert manifest["result_sha256"] == sha(result_path)
    assert result["inputs_sha256"] == manifest["inputs_sha256"] == expected_inputs
    assert result["outputs_sha256"] == manifest["outputs_sha256"]
    assert manifest["exit_code"] == (0 if result["status"] == "GRID_CONDITION_EVALUATED" else 1)
    for name, digest in result["outputs_sha256"].items():
        assert sha(directory / name) == digest, (condition, name)
    solver = result["solver"]
    assert solver["start"] == 0 and solver["end"] == 1000
    assert solver["report_points"] == 201
    assert solver["rtol"] == 1e-10 and solver["atol"] == 1e-14
    assert solver["state"] == "BDF" and solver["extent"] == "segmented DOP853 ODE states"
    screen_path = directory / "timescale.json"
    screen = read_json(screen_path) if screen_path.exists() else None
    if screen is not None:
        assert screen["status"] == "COUPLED_FULL_TRAJECTORY_TIMESCALE_SCREEN_NOT_QSSA_VALIDATION"
        assert screen["sample_count"] == 201
        assert screen["full_state_sha256"] == sha(directory / "full_state.npz")
        assert screen["timescale_csv_sha256"] == sha(directory / "timescale.csv")
    maxima = result.get("maxima", {})
    closure = result["closure_counters"].get("max_residual")
    if result["status"] == "GRID_CONDITION_EVALUATED":
        limits = result["limits"]
        assert limits == {"closure": 1e-10, "balance": 1e-8, "state": 0.01,
                          "process_rate": 0.05, "cumulative_resource_extent": 0.01}
        passed = bool(
            closure <= limits["closure"] and
            maxima["all_species_E_inf"] <= limits["state"] and
            maxima["aminoacylation_rate_E_inf"] <= limits["process_rate"] and
            maxima["aminoacylation_extent_E_inf"] <= limits["cumulative_resource_extent"] and
            maxima["full_material_balance_abs"] <= limits["balance"] and
            maxima["reduced_slow_balance_abs"] <= limits["balance"] and
            maxima["source_general_inventory_drift_abs"] <= limits["balance"]
        )
        assert result["condition_pass"] is passed
    else:
        assert result["status"] == "GRID_CONDITION_INCOMPLETE"
        assert "failure" in result
        passed = False
    row = {
        "condition_id": condition,
        "result_status": result["status"],
        "condition_pass": str(passed).lower(),
        "failure": result.get("failure", ""),
        "closure_residual": closure,
        **{key: maxima.get(key) for key in NUMERIC_KEYS},
        "epsilon_screen_fail_samples": (screen["epsilon_screen_fail_samples"]
                                        if screen else None),
        "nonattracting_samples": (screen["nonattracting_samples"]
                                  if screen else None),
        "manifest_sha256": sha(directory / "manifest.json"),
    }
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    targets = [run / name for name in ("validation_grid.csv", "summary.json", "pilot_manifest.json")]
    if any(path.exists() for path in targets):
        parser.error("Refusing to overwrite finalized pilot outputs")
    with GRID.open(encoding="utf-8", newline="") as stream:
        grid = list(csv.DictReader(stream))
    if tuple(row["condition_id"] for row in grid) != EXPECTED:
        parser.error("Registered grid IDs/order differ from the fixed ten-case protocol")
    missing = [name for name in EXPECTED if not (run / name / "manifest.json").exists()]
    if missing:
        parser.error("Unfinalized conditions: " + ", ".join(missing))
    inputs = {key: sha(ROOT / path) for key, path in INPUTS.items()}
    rows = [check(name, run / name, inputs) for name in EXPECTED]
    passed = [row["condition_id"] for row in rows if row["condition_pass"] == "true"]
    failed = [row["condition_id"] for row in rows if row["condition_pass"] == "false"]
    verdict = (
        "R3_PILOT_ACCEPTED_IN_VALIDATED_DOMAIN" if len(passed) == len(EXPECTED) else
        "R3_PILOT_PARTIAL_DOMAIN_ONLY" if passed else
        "R3_PILOT_REJECTED_BY_FULL_COUPLED_VALIDATION"
    )
    with targets[0].open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "schema_version": "1.0",
        "run_kind": "REGISTERED_R3_TEN_CONDITION_FULL_COUPLED_PILOT",
        "pilot_status": verdict,
        "validated_conditions": passed,
        "failed_or_incomplete_conditions": failed,
        "condition_count": len(rows),
        "source_and_protocol_sha256": inputs,
        "meaning": "Selective 21-complex GlyRS/MetRS approximation pilot only; not final PURE reduction or R4 approval",
    }
    targets[1].write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest = {
        "schema_version": "1.0",
        "status": "HASH_VERIFIED_COMPLETE_R3_PILOT",
        "command": [sys.executable, *sys.argv],
        "cwd": str(ROOT),
        "script_sha256": sha(Path(__file__)),
        "condition_manifests_sha256": {row["condition_id"]: row["manifest_sha256"] for row in rows},
        "outputs_sha256": {path.name: sha(path) for path in targets[:2]},
        "pilot_status": verdict,
    }
    targets[2].write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"pilot_status": verdict, "validated": passed,
                      "failed_or_incomplete": failed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
