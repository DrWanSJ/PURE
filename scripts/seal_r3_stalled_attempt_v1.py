#!/usr/bin/env python3
"""Seal an externally stopped R3 condition as incomplete, never evaluated."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from finalize_r3_pilot_v1 import INPUTS
from verify_reduction_audit_v0 import ROOT


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def seal(run: Path) -> None:
    run = run.resolve()
    assert run.name == "R3_ADVERSE"
    assert not (run / "result.json").exists() and not (run / "manifest.json").exists()
    diagnostic = json.loads((run / "stall_diagnostic.json").read_text(encoding="utf-8"))
    screen = json.loads((run / "timescale.json").read_text(encoding="utf-8"))
    samples = diagnostic["samples"]
    assert diagnostic["status"] == "LIVE_REDUCED_BDF_PROGRESS_DIAGNOSTIC_NOT_ACCEPTANCE"
    assert diagnostic["condition_id"] == run.name and len(samples) >= 2
    assert diagnostic["script_sha256"] == sha(ROOT / "scripts/probe_r3_running_bdf_v1.py")
    assert diagnostic["full_state_sha256"] == sha(run / "full_state.npz")
    assert screen["full_state_sha256"] == diagnostic["full_state_sha256"]
    assert screen["timescale_csv_sha256"] == sha(run / "timescale.csv")
    assert 0 < samples[0]["bdf_time_s"] <= samples[-1]["bdf_time_s"] < 1000
    assert samples[-1]["process_cpu_seconds"] >= samples[0]["process_cpu_seconds"]
    assert samples[-1]["process_cpu_seconds"] > 0
    command = diagnostic["command"]
    assert "run_r3_coupled_grid_v1.py" in " ".join(command)
    assert "R3_ADVERSE" in command and Path(command[-1]).resolve() == run
    outputs = {name: sha(run / name) for name in (
        "full_state.npz", "timescale.csv", "timescale.json", "stall_diagnostic.json")}
    inputs = {key: sha(ROOT / path) for key, path in INPUTS.items()}
    termination = {
        "kind": "EXTERNAL_STOP_AFTER_DOCUMENTED_NUMERICAL_STALL",
        "os_exit_code": None,
        "os_exit_code_note": "The external process exit code was not captured; it is not represented as runner exit 1.",
        "last_observed_bdf_time_s": samples[-1]["bdf_time_s"],
        "last_observed_bdf_step_s": samples[-1]["bdf_step_s"],
        "last_observed_process_cpu_seconds": samples[-1]["process_cpu_seconds"],
        "progress_diagnostic_sha256": outputs["stall_diagnostic.json"],
    }
    result = {
        "schema_version": "1.0",
        "status": "GRID_CONDITION_INCOMPLETE",
        "run_kind": "REGISTERED_R3_GRID_CONDITION",
        "condition_id": run.name,
        "condition_role": "anticipated_failure_domain",
        "initial_scale_json": '{"GlyRS":20,"MetRS":20,"ATP":0.02,"tRNAGlyGCC":0.02,"tRNAfMetCAU":0.02}',
        "command": command,
        "cwd": str(ROOT),
        "python_executable": command[0],
        "python_version": screen["python_version"],
        "numpy_version": screen["numpy_version"],
        "scipy_version": screen["scipy_version"],
        "solver": {"state": "BDF", "extent": "segmented DOP853 ODE states",
                   "rtol": 1e-10, "atol": 1e-14, "start": 0., "end": 1000.,
                   "report_points": 201},
        "inputs_sha256": inputs,
        "outputs_sha256": outputs,
        "closure_counters": {},
        "condition_pass": False,
        "failure": "Reduced BDF solve did not complete the registered 0-1000 s window; externally stopped after documented near-zero progress at about 362 s. No reduced trajectory, directed extents, or coupled error scores are claimed for this condition.",
        "termination": termination,
    }
    write_json(run / "result.json", result)
    manifest = {
        "schema_version": "1.0",
        "status": "HASH_VERIFIED_R3_GRID_CONDITION",
        "condition_id": run.name,
        "run_kind": result["run_kind"],
        "command": command,
        "cwd": result["cwd"],
        "python_executable": result["python_executable"],
        "python_version": result["python_version"],
        "numpy_version": result["numpy_version"],
        "scipy_version": result["scipy_version"],
        "exit_code": None,
        "termination": termination,
        "sealer_sha256": sha(Path(__file__)),
        "result_status": result["status"],
        "result_sha256": sha(run / "result.json"),
        "inputs_sha256": inputs,
        "outputs_sha256": outputs,
    }
    write_json(run / "manifest.json", manifest)
    print(json.dumps({"condition_id": run.name, "status": result["status"],
                      "manifest_sha256": sha(run / "manifest.json"),
                      "os_exit_code": None}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    seal(args.run_dir)


if __name__ == "__main__":
    main()
