#!/usr/bin/env python3
"""Capture reproducible R1/R2 baseline commands and their raw output."""
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
SOURCE_PATHS = (
    "models/pnas2017_full_reference/original/fMGG_synthesis.xml",
    "models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml",
    "results/pnas2017_reference/rr_cvode_author_csv_20260924/effective_author_conditions.xml",
    "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv",
    "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv",
    "docs/reduction/reaction_level_annotation_v2.csv",
    "docs/reduction/species_information_contract_detailed.md",
)
COMMANDS = (
    ("audit_before_build", (sys.executable, "scripts/verify_reduction_audit_v0.py")),
    ("audit_builder", (sys.executable, "scripts/build_reduction_audit_v0.py")),
    ("audit_after_build", (sys.executable, "scripts/verify_reduction_audit_v0.py")),
    ("pnas_integration", (sys.executable, "scripts/verify_pnas2017_integration.py")),
    ("species_contract", (sys.executable, "scripts/verify_species_information_contract.py")),
    ("functional_annotation", (sys.executable, "scripts/verify_reaction_level_annotation_v2.py")),
    ("pnas_artifacts", (sys.executable, "scripts/verify_pnas2017_artifacts.py")),
    ("diff_check", ("git", "-c", f"safe.directory={ROOT.as_posix()}", "diff", "--check")),
)


def git(*args: str) -> str:
    result = subprocess.run(
        ("git", "-c", f"safe.directory={ROOT.as_posix()}", *args),
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    audit = json.loads((ROOT / "docs/reduction/reduction_audit_manifest_v0.json").read_text(encoding="utf-8"))
    actual_hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_PATHS}
    versions = {}
    for name in ("numpy", "scipy", "sympy", "libroadrunner", "roadrunner", "lxml"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    manifest = {
        "schema_version": "1.0",
        "stage": "PREFLIGHT",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "cwd": str(ROOT),
        "branch": git("branch", "--show-current"),
        "source_commit": git("rev-parse", "HEAD"),
        "origin_main_local": git("rev-parse", "refs/remotes/origin/main"),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "environment": {key: os.environ.get(key) for key in (
            "PYTHONHASHSEED", "PYTHONPATH", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
        "package_versions": versions,
        "source_sha256": actual_hashes,
        "source_hashes_match_audit_v0": all(
            actual_hashes[name] == audit["source_sha256"][name] for name in SOURCE_PATHS
        ),
        "commands": [],
    }
    child_env = os.environ.copy()
    child_env.update({
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "safe.directory",
        "GIT_CONFIG_VALUE_0": ROOT.as_posix(),
    })
    for label, argv in COMMANDS:
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, env=child_env)
        stdout_name, stderr_name = f"{label}.stdout.log", f"{label}.stderr.log"
        (out / stdout_name).write_bytes(result.stdout)
        (out / stderr_name).write_bytes(result.stderr)
        command = {
            "label": label,
            "argv": list(argv),
            "cwd": str(ROOT),
            "git_safe_directory_environment": {
                key: child_env[key] for key in ("GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0")
            },
            "started_utc": started,
            "ended_utc": datetime.now(timezone.utc).isoformat(),
            "exit_code": result.returncode,
            "stdout_path": stdout_name,
            "stderr_path": stderr_name,
        }
        manifest["commands"].append(command)
        print(f"{label}: exit {result.returncode}", flush=True)
    manifest["all_commands_passed"] = all(item["exit_code"] == 0 for item in manifest["commands"])
    (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 0 if manifest["source_hashes_match_audit_v0"] and manifest["all_commands_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
