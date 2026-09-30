#!/usr/bin/env python3
"""Checkpoint an adverse reduced BDF diagnostic without changing grid evidence.

The original registered solve remains sealed. This separate stepper exposes
accepted reduced states and solver progress at the same fixed tolerances. Its
extra snapshots make it a diagnostic, not a replacement validation run.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import BDF

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from verify_reduction_audit_v0 import ROOT


GRID = ROOT / "docs/reduction/r3_validation_grid_v1.csv"
STOP = ROOT / ".codex-auto-resume/STOP"
RTOL = 1e-10
ATOL = 1e-14


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8",
                    newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--max-wall-seconds", type=float, default=300.)
    parser.add_argument("--checkpoint-seconds", type=float, default=30.)
    parser.add_argument("--max-rhs-calls", type=int, default=100000)
    args = parser.parse_args()
    if not (args.max_wall_seconds > 0 and args.checkpoint_seconds > 0
            and args.max_rhs_calls > 0):
        parser.error("All bounds must be positive")
    if STOP.exists():
        parser.error("STOP present")
    out = args.out.resolve()
    if out.exists():
        parser.error(f"Refusing to overwrite {out}")
    with GRID.open(encoding="utf-8", newline="") as stream:
        row = next(row for row in csv.DictReader(stream)
                   if row["condition_id"] == "R3_ADVERSE")
    runtime = R3ResourceTotalRuntimeV2()
    source = runtime.source
    scales = json.loads(row["initial_scale_json"])
    x0 = np.array([float(source.author_initial[name]) * scales.get(name, 1.)
                   for name in source.species])
    assert np.min(x0) >= 0
    z0 = runtime.initial_slow(x0)
    out.mkdir(parents=True)
    progress_path = out / "progress.json"
    inputs = {
        "canonical_sbml": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
        "grid": sha(GRID),
        "method": sha(ROOT / "docs/reduction/r3_aminoacylation_qssa_method.md"),
        "protocol": sha(ROOT / "docs/reduction/r3_coupled_validation_protocol_v1.md"),
        "runtime_v1": sha(ROOT / "scripts/r3_resource_total_runtime_v1.py"),
        "runtime_v2": sha(ROOT / "scripts/r3_resource_total_runtime_v2.py"),
        "script": sha(Path(__file__)),
    }
    started = time.perf_counter()
    process_started = time.process_time()
    last_write = started
    step_count = 0
    snapshots = []

    def physical_root(z):
        found = runtime.solve_fast(z, x0)
        if not found["valid_local_root"]:
            raise RuntimeError(f"Physical closure failed: residual={found['residual_max']}")
        return found["q"]

    def rhs(t, z):
        return runtime.slow_rhs(z, physical_root(z), x0)[0]

    def jac(t, z):
        return runtime.slow_jacobian(z, physical_root(z), x0)[0]

    stepper = BDF(rhs, 0., z0, 1000., jac=jac, rtol=RTOL, atol=ATOL)
    stop_reason = None
    failure = None

    def snapshot() -> None:
        nonlocal last_write
        # The separate runtime keeps this read-only probe from changing the
        # warm-start seed used by the running BDF callbacks.
        probe = R3ResourceTotalRuntimeV2()
        found = probe.solve_fast(stepper.y, x0)
        index = len(snapshots)
        name = f"state_{index:04d}.npz"
        np.savez_compressed(out / name, t=float(stepper.t), z=stepper.y,
                            q=found["q"], state=found["state"])
        entry = {
            "name": name, "sha256": sha(out / name),
            "t": float(stepper.t), "steps": step_count,
            "nfev": int(stepper.nfev), "njev": int(stepper.njev),
            "nlu": int(stepper.nlu), "order": int(stepper.order),
            "h_abs": float(stepper.h_abs),
            "root_valid": bool(found["valid_local_root"]),
            "root_residual_max": float(found["residual_max"]),
            "minimum_q": float(found["min_q"]),
            "minimum_resource": float(found["min_resource"]),
            "wall_elapsed_s": time.perf_counter() - started,
            "process_cpu_s": time.process_time() - process_started,
            "utc": datetime.now(timezone.utc).isoformat(),
        }
        snapshots.append(entry)
        write_json(progress_path, {
            "schema_version": "1.0",
            "status": "DIAGNOSTIC_PARTIAL_NOT_REGISTERED_GRID_RESULT",
            "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
            "python_version": platform.python_version(),
            "numpy_version": np.__version__, "scipy_version": scipy.__version__,
            "condition_id": "R3_ADVERSE", "rtol": RTOL, "atol": ATOL,
            "inputs_sha256": inputs, "snapshots": snapshots,
        })
        last_write = time.perf_counter()
        print(f"t={entry['t']:.9f} steps={step_count} nfev={entry['nfev']} "
              f"h={entry['h_abs']:.3g}", flush=True)

    try:
        snapshot()
        while stepper.status == "running":
            if STOP.exists():
                stop_reason = "STOP_MARKER"
                break
            if time.perf_counter() - started >= args.max_wall_seconds:
                stop_reason = "WALL_TIME_BUDGET"
                break
            if stepper.nfev >= args.max_rhs_calls:
                stop_reason = "RHS_CALL_BUDGET"
                break
            stepper.step()
            step_count += 1
            if time.perf_counter() - last_write >= args.checkpoint_seconds:
                snapshot()
        if stepper.status == "finished":
            stop_reason = "INTEGRATOR_FINISHED"
        elif stepper.status == "failed":
            stop_reason = "INTEGRATOR_FAILED"
    except Exception as error:
        stop_reason = "EXCEPTION"
        failure = repr(error)
    finally:
        if not snapshots or snapshots[-1]["t"] != float(stepper.t):
            try:
                snapshot()
            except Exception as error:
                failure = repr(error) if failure is None else failure + "; snapshot: " + repr(error)
        result = {
            "schema_version": "1.0",
            "status": "DIAGNOSTIC_ONLY_NOT_REGISTERED_GRID_RESULT",
            "stop_reason": stop_reason, "failure": failure,
            "last_t": float(stepper.t), "steps": step_count,
            "nfev": int(stepper.nfev), "njev": int(stepper.njev),
            "nlu": int(stepper.nlu),
            "wall_elapsed_s": time.perf_counter() - started,
            "process_cpu_s": time.process_time() - process_started,
            "snapshot_sha256": {item["name"]: item["sha256"] for item in snapshots},
            "inputs_sha256": inputs,
        }
        write_json(out / "result.json", result)
        write_json(out / "manifest.json", {
            "schema_version": "1.0",
            "status": "HASH_BOUND_DIAGNOSTIC_NOT_GRID_ACCEPTANCE",
            "script_sha256": inputs["script"],
            "result_sha256": sha(out / "result.json"),
            "progress_sha256": sha(progress_path) if progress_path.exists() else None,
            "stop_reason": stop_reason,
            "output_paths": ["result.json", "progress.json", *result["snapshot_sha256"]],
        })
    return 0 if failure is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
