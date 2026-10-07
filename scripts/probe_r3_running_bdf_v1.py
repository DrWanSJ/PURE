#!/usr/bin/env python3
"""Read-only sample of the live registered adverse BDF solver."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sample(pid: int, process: psutil.Process) -> dict:
    spy = subprocess.run(
        ["py-spy", "dump", "-l", "-j", "--pid", str(pid)],
        capture_output=True, text=True, check=True, timeout=30,
    )
    thread = json.loads(spy.stdout)[0]
    frames = thread["frames"]
    step = next(frame for frame in frames if frame["name"] == "_step_impl")
    values = {item["name"]: item.get("repr") for item in step["locals"]}
    root = next((frame for frame in frames if frame["name"] == "solve_fast"), None)
    cpu = process.cpu_times()
    return {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "process_cpu_seconds": cpu.user + cpu.system,
        "bdf_time_s": float(values["t"]),
        "bdf_step_s": float(values["h_abs"]),
        "bdf_order": int(values["order"]),
        "closure_stack_line": root["line"] if root else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    assert 2 <= args.samples <= 20 and 0 < args.interval <= 30
    run = args.run_dir.resolve()
    output = run / "stall_diagnostic.json"
    assert not output.exists()
    process = psutil.Process(args.pid)
    command = process.cmdline()
    assert "run_r3_coupled_grid_v1.py" in " ".join(command)
    assert "R3_ADVERSE" in command
    assert Path(command[-1]).resolve() == run
    full = run / "full_state.npz"
    assert full.exists() and not (run / "result.json").exists()
    samples = []
    for index in range(args.samples):
        samples.append(sample(args.pid, process))
        if index + 1 < args.samples:
            time.sleep(args.interval)
    record = {
        "status": "LIVE_REDUCED_BDF_PROGRESS_DIAGNOSTIC_NOT_ACCEPTANCE",
        "condition_id": "R3_ADVERSE",
        "process_id": args.pid,
        "command": command,
        "python_executable": process.exe(),
        "script_sha256": sha(Path(__file__)),
        "full_state_sha256": sha(full),
        "samples": samples,
    }
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(output), "sha256": sha(output),
                      "first_time_s": samples[0]["bdf_time_s"],
                      "last_time_s": samples[-1]["bdf_time_s"],
                      "last_cpu_s": samples[-1]["process_cpu_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
