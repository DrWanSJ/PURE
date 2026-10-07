#!/usr/bin/env python3
"""Register the R2 semantic/domain gates and retain their raw output."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/reduction/r2_frozen_reference_domain_v1/decisive_001"
SOURCE = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if RUN.exists():
        raise SystemExit(f"Refusing to overwrite registered run: {RUN}")
    RUN.mkdir(parents=True)
    commands = [
        ("audit", ["scripts/verify_reduction_audit_v0.py"]),
        ("domain_build", ["scripts/build_frozen_reference_domain_v1.py"]),
        ("domain_mutants", ["scripts/test_frozen_reference_domain_v1.py"]),
        ("reverse_mutants", ["scripts/test_reduction_reverse_channels.py"]),
        ("candidate_mutants", ["scripts/test_reduction_candidate_coverage.py"]),
        ("chart_mutants", ["scripts/test_source_coordinate_certificate_v1.py"]),
        ("chart_certificate", ["scripts/verify_source_coordinate_certificate_v1.py"]),
        ("pointwise", ["scripts/verify_source_coordinate_pointwise_v1.py", "--chart", "v4", "--out",
                       str(RUN / "pointwise_result.json")]),
    ]
    records = []
    for label, args in commands:
        command = [sys.executable, *args]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, check=False)
        stdout = RUN / f"{label}.stdout.log"
        stderr = RUN / f"{label}.stderr.log"
        stdout.write_bytes(result.stdout)
        stderr.write_bytes(result.stderr)
        record = {"label": label, "command": command, "cwd": str(ROOT),
                  "exit_code": result.returncode,
                  "stdout": stdout.relative_to(ROOT).as_posix(), "stdout_sha256": sha(stdout),
                  "stderr": stderr.relative_to(ROOT).as_posix(), "stderr_sha256": sha(stderr)}
        records.append(record)
        print(f"{label}: exit {result.returncode}", flush=True)
    packages = {}
    for name in ("numpy", "scipy", "sympy", "python-libsbml", "roadrunner"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    git = subprocess.run(["git", "-c", "safe.directory=C:/Users/sean/Desktop/GUV", "rev-parse", "HEAD"],
                         cwd=ROOT, capture_output=True, text=True, check=True)
    inputs = [SOURCE, ROOT / "docs/reduction/conservation_laws_v0.csv",
              ROOT / "docs/reduction/r2_frozen_reference_domain_v1.md",
              ROOT / "scripts/verify_reduction_audit_v0.py",
              ROOT / "scripts/build_frozen_reference_domain_v1.py",
              ROOT / "scripts/test_frozen_reference_domain_v1.py"]
    outputs = [ROOT / "docs/reduction/frozen_reference_reactivation_v1.csv",
               ROOT / "docs/reduction/frozen_reference_domain_certificate_v1.json"]
    manifest = {
        "schema_version": "1.0", "stage": "R2", "run_id": "decisive_001",
        "cwd": str(ROOT), "git_head_before_r2_commit": git.stdout.strip(),
        "python_executable": sys.executable, "python_version": platform.python_version(),
        "platform": platform.platform(),
        "environment": {"PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
                        "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV")},
        "package_versions": packages,
        "input_sha256": {path.relative_to(ROOT).as_posix(): sha(path) for path in inputs},
        "output_sha256": {path.relative_to(ROOT).as_posix(): sha(path) for path in outputs},
        "commands": records,
        "pass": all(record["exit_code"] == 0 for record in records),
    }
    (RUN / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0 if manifest["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
