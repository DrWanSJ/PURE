#!/usr/bin/env python3
"""Run one reduction acceptance command with raw logs and a run manifest."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not argv:
        parser.error("a command is required after --")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "safe.directory",
                "GIT_CONFIG_VALUE_0": ROOT.as_posix()})
    head = subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, env=env, text=True).strip()
    branch = subprocess.check_output(("git", "branch", "--show-current"), cwd=ROOT, env=env, text=True).strip()
    versions = {}
    for package in ("numpy", "scipy", "sympy", "libroadrunner"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    started = datetime.now(timezone.utc).isoformat()
    # Write child output as it arrives so long numerical runs are inspectable
    # without retaining large logs in the parent process's memory.
    with (out / "stdout.log").open("wb") as stdout, (out / "stderr.log").open("wb") as stderr:
        process = subprocess.run(argv, cwd=ROOT, env=env, stdout=stdout, stderr=stderr)
    manifest = {
        "schema_version": "1.0",
        "label": args.label,
        "command": argv,
        "cwd": str(ROOT),
        "environment": {key: env.get(key) for key in (
            "PYTHONHASHSEED", "PYTHONPATH", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
            "MKL_NUM_THREADS", "GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0")},
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "package_versions": versions,
        "source_commit": head,
        "source_branch": branch,
        "canonical_sbml_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "started_utc": started,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code": process.returncode,
        "stdout_path": "stdout.log",
        "stderr_path": "stderr.log",
    }
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"{args.label}: exit {process.returncode}; logs in {out}")
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
