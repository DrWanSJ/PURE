#!/usr/bin/env python3
"""Test deterministic fast-root seeding at an adverse reduced snapshot.

This is a bounded local restart, not a registered grid condition. The physical
root predicate, analytic Jacobian, source rates, and tolerances are unchanged.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import BDF

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from verify_reduction_audit_v0 import ROOT


SNAPSHOT = ROOT / "results/reduction/r3_aminoacylation_qssa/adverse_bdf_stepper_001/state_0006.npz"
GRID = ROOT / "docs/reduction/r3_validation_grid_v1.csv"
STOP = ROOT / ".codex-auto-resume/STOP"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--accepted-steps", type=int, default=200)
    parser.add_argument("--max-rhs-calls", type=int, default=5000)
    args = parser.parse_args()
    if args.accepted_steps <= 0 or args.max_rhs_calls <= 0:
        parser.error("Budgets must be positive")
    if STOP.exists():
        parser.error("STOP present")
    out = args.out.resolve()
    if out.exists():
        parser.error(f"Refusing to overwrite {out}")
    with GRID.open(encoding="utf-8", newline="") as stream:
        row = next(item for item in csv.DictReader(stream)
                   if item["condition_id"] == "R3_ADVERSE")
    with np.load(SNAPSHOT) as data:
        t0, z0, seed = float(data["t"]), data["z"], data["q"]
    runtime = R3ResourceTotalRuntimeV2()
    scales = json.loads(row["initial_scale_json"])
    x0 = np.array([float(runtime.source.author_initial[name]) * scales.get(name, 1.)
                   for name in runtime.source.species])
    assert z0.shape == (193,) and seed.shape == (21,) and 359 < t0 < 360
    calls = 0

    def physical_root(z):
        # Every RHS/Jacobian evaluation begins from the same physical seed.
        # This removes dependence on the order of BDF callback evaluations.
        found = runtime.solve_fast(z, x0, seed=seed)
        if not found["valid_local_root"]:
            raise RuntimeError("Physical root lost")
        return found["q"]

    def rhs(t, z):
        nonlocal calls
        calls += 1
        if calls > args.max_rhs_calls:
            raise RuntimeError("RHS call budget")
        return runtime.slow_rhs(z, physical_root(z), x0)[0]

    def jac(t, z):
        return runtime.slow_jacobian(z, physical_root(z), x0)[0]

    started = time.perf_counter()
    stepper = BDF(rhs, t0, z0, t0 + 0.1, jac=jac, rtol=1e-10, atol=1e-14)
    accepted = 0
    reason = None
    try:
        while accepted < args.accepted_steps and stepper.status == "running":
            if STOP.exists():
                reason = "STOP_MARKER"
                break
            stepper.step()
            if stepper.status != "failed":
                accepted += 1
        if reason is None:
            reason = ("ACCEPTED_STEP_BUDGET" if accepted == args.accepted_steps
                      else stepper.status.upper())
    except RuntimeError as error:
        reason = str(error)
    result = {
        "schema_version": "1.0",
        "status": "FIXED_SEED_DIAGNOSTIC_NOT_REGISTERED_GRID_RESULT",
        "start_t": t0, "last_t": float(stepper.t), "stop_reason": reason,
        "rtol": 1e-10, "atol": 1e-14,
        "accepted_steps": accepted, "rhs_calls": calls,
        "jacobian_calls": int(stepper.njev), "lu_factorizations": int(stepper.nlu),
        "wall_s": time.perf_counter() - started,
        "seed_sha256": hashlib.sha256(seed.tobytes()).hexdigest(),
    }
    out.mkdir(parents=True)
    write_json(out / "result.json", result)
    write_json(out / "manifest.json", {
        "schema_version": "1.0",
        "status": "HASH_BOUND_FIXED_SEED_DIAGNOSTIC_NOT_GRID_ACCEPTANCE",
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        "inputs_sha256": {
            "snapshot": sha(SNAPSHOT), "grid": sha(GRID),
            "canonical_sbml": sha(ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
            "runtime_v2": sha(ROOT / "scripts/r3_resource_total_runtime_v2.py"),
            "script": sha(Path(__file__)),
        },
        "result_sha256": sha(out / "result.json"), "exit_code": 0,
    })
    print(f"{reason}: t={stepper.t:.9f}, {accepted} accepted, {calls} RHS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
