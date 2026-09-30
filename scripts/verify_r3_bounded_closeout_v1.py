#!/usr/bin/env python3
"""Verify the bounded R3 closeout without certifying the original full grid."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from finalize_r3_pilot_v1 import EXPECTED, GRID, INPUTS, check, resolve_attempts, sha
from verify_reduction_audit_v0 import ROOT


RUN = ROOT / "results/reduction/r3_aminoacylation_qssa/run_001"
COMPLETED = EXPECTED[:-1]
ADVERSE = EXPECTED[-1]
TRACE = ROOT / "results/reduction/r3_aminoacylation_qssa/adverse_newton_trace_001"
COMPLETE_OUTPUTS = {
    "full_state.npz", "state_trajectories.npz", "directed_ledgers.npz",
    "species_errors.csv", "directed_rate_errors.csv",
    "directed_extent_errors.csv", "timescale.csv", "timescale.json",
}
ADVERSE_MISSING_OUTPUTS = {
    "state_trajectories.npz", "directed_ledgers.npz",
    "species_errors.csv", "directed_rate_errors.csv",
    "directed_extent_errors.csv",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(run: Path = RUN) -> dict:
    """Check immutable source, attempt, raw-output, and aggregate evidence."""
    run = run.resolve()
    with GRID.open(encoding="utf-8", newline="") as stream:
        grid = list(csv.DictReader(stream))
    assert tuple(row["condition_id"] for row in grid) == EXPECTED
    assert len(COMPLETED) == 9 and ADVERSE == "R3_ADVERSE"

    attempt_map_path = run / "attempt_map.json"
    mapping = read_json(attempt_map_path)
    attempts = resolve_attempts(run, mapping)
    inputs = {name: sha(ROOT / path) for name, path in INPUTS.items()}
    checked = [check(name, attempts[name], inputs, registered)
               for name, registered in zip(EXPECTED, grid)]
    for row in checked:
        row["evidence_directory"] = mapping[row["condition_id"]]

    for condition, row in zip(COMPLETED, checked[:9]):
        assert row["condition_id"] == condition
        assert row["result_status"] == "GRID_CONDITION_EVALUATED"
        assert row["condition_pass"] == "false"
        assert row["closure_residual"] is not None
        assert row["closure_residual"] <= 1e-10
        # The candidate fails measured approximation gates independently of
        # the full model's own material-balance diagnostic residual.
        assert row["all_species_E_inf"] > 0.01
        assert row["aminoacylation_rate_E_inf"] > 0.05
        assert row["aminoacylation_extent_E_inf"] > 0.01
        result = read_json(attempts[condition] / "result.json")
        assert COMPLETE_OUTPUTS.issubset(result["outputs_sha256"])
        assert all((attempts[condition] / name).is_file()
                   for name in COMPLETE_OUTPUTS)

    adverse = checked[-1]
    assert adverse["condition_id"] == ADVERSE
    assert adverse["result_status"] == "GRID_CONDITION_INCOMPLETE"
    assert adverse["condition_pass"] == "false"
    assert adverse["all_species_E_inf"] is None
    assert adverse["aminoacylation_rate_E_inf"] is None
    assert adverse["aminoacylation_extent_E_inf"] is None
    adverse_result = read_json(attempts[ADVERSE] / "result.json")
    assert adverse_result["termination"]["kind"] == (
        "EXTERNAL_STOP_AFTER_DOCUMENTED_NUMERICAL_STALL")
    assert "full_state.npz" in adverse_result["outputs_sha256"]
    assert ADVERSE_MISSING_OUTPUTS.isdisjoint(adverse_result["outputs_sha256"])
    assert all(not (attempts[ADVERSE] / name).exists()
               for name in ADVERSE_MISSING_OUTPUTS)

    summary = read_json(run / "summary.json")
    assert summary["run_kind"] == "REGISTERED_R3_TEN_CONDITION_FULL_COUPLED_PILOT"
    assert summary["condition_count"] == 10
    assert summary["evaluated_failed_conditions"] == list(COMPLETED)
    assert summary["incomplete_conditions"] == [ADVERSE]
    assert summary["validated_conditions"] == []
    assert summary["failed_or_incomplete_conditions"] == list(EXPECTED)
    assert summary["validation_grid_complete"] is False
    assert summary["durable_r3_stage_complete"] is False
    assert summary["source_and_protocol_sha256"] == inputs
    assert summary["condition_attempts"] == mapping

    manifest = read_json(run / "pilot_manifest.json")
    assert manifest["status"] == "HASH_VERIFIED_R3_REJECTION_WITH_INCOMPLETE_CONDITION"
    assert manifest["evaluated_condition_count"] == 9
    assert manifest["incomplete_condition_count"] == 1
    assert manifest["attempt_map_sha256"] == sha(attempt_map_path)
    assert manifest["script_sha256"] == sha(ROOT / "scripts/finalize_r3_pilot_v1.py")
    assert manifest["execution_environment_sha256"] == sha(
        ROOT / "docs/reduction/r3_grid_execution_environment_v1.md")
    assert manifest["condition_manifests_sha256"] == {
        row["condition_id"]: row["manifest_sha256"] for row in checked
    }
    assert manifest["outputs_sha256"] == {
        "validation_grid.csv": sha(run / "validation_grid.csv"),
        "summary.json": sha(run / "summary.json"),
    }
    with (run / "validation_grid.csv").open(encoding="utf-8", newline="") as stream:
        aggregate = list(csv.DictReader(stream))
    assert len(aggregate) == len(checked)
    for actual, expected in zip(aggregate, checked):
        assert actual == {key: "" if value is None else str(value)
                          for key, value in expected.items()}

    trace_manifest = read_json(TRACE / "manifest.json")
    trace_result = read_json(TRACE / "result.json")
    assert trace_manifest["status"] == "HASH_BOUND_NEWTON_TRACE_NOT_GRID_ACCEPTANCE"
    assert trace_manifest["exit_code"] == 0
    assert trace_manifest["inputs_sha256"] == {
        "snapshot": sha(ROOT / "results/reduction/r3_aminoacylation_qssa/"
                        "adverse_bdf_stepper_001/state_0006.npz"),
        "grid": sha(GRID),
        "canonical_sbml": sha(ROOT / INPUTS["canonical_sbml"]),
        "runtime_v2": sha(ROOT / INPUTS["runtime_v2"]),
        "script": sha(ROOT / "scripts/diagnose_r3_adverse_newton_trace_v1.py"),
    }
    assert trace_manifest["result_sha256"] == sha(TRACE / "result.json")
    assert trace_result["status"] == "NEWTON_TRACE_DIAGNOSTIC_NOT_REGISTERED_GRID_RESULT"
    assert trace_result["accepted_steps"] == 200
    assert trace_result["trial_count"] == 564
    assert trace_result["break_reason_counts"] == {
        "CONVERGED": 200,
        "PREDICTED_NONCONVERGENCE": 235,
        "NONCONTRACTING_CORRECTION": 129,
    }

    return {
        "closeout_status": "HASH_VERIFIED_BOUNDED_R3_CLOSEOUT",
        "original_full_grid_protocol": "INCOMPLETE",
        "candidate_on_completed_conditions": "REJECTED",
        "completed_full_coupled_comparisons": len(COMPLETED),
        "incomplete_conditions": [ADVERSE],
        "original_terminal_acceptance_claim": False,
        "bounded_adverse_trace_hash_verified": True,
    }


def main() -> None:
    print(json.dumps(verify(), indent=2))


if __name__ == "__main__":
    main()
