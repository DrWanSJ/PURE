#!/usr/bin/env python3
"""Verify and seal one immutable R3 condition result with its process exit."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--exit-code", type=int, required=True)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    target = run / "manifest.json"
    if target.exists():
        parser.error(f"Refusing to overwrite {target}")
    result = json.loads((run / "result.json").read_text(encoding="utf-8"))
    expected_code = 0 if result["status"] == "GRID_CONDITION_EVALUATED" else 1
    if args.exit_code != expected_code:
        parser.error(f"Exit code {args.exit_code} differs from result status {result['status']}")
    for name, digest in result["outputs_sha256"].items():
        actual = sha(run / name)
        if actual != digest:
            parser.error(f"Output hash mismatch: {name}: {actual} != {digest}")
    manifest = {
        "schema_version": "1.0",
        "status": "HASH_VERIFIED_R3_GRID_CONDITION",
        "condition_id": result["condition_id"],
        "run_kind": result["run_kind"],
        "command": result["command"],
        "cwd": result["cwd"],
        "python_executable": result["python_executable"],
        "python_version": result["python_version"],
        "numpy_version": result["numpy_version"],
        "scipy_version": result["scipy_version"],
        "exit_code": args.exit_code,
        "result_status": result["status"],
        "result_sha256": sha(run / "result.json"),
        "inputs_sha256": result["inputs_sha256"],
        "outputs_sha256": result["outputs_sha256"],
    }
    target.write_text(json.dumps(manifest, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(json.dumps({"condition_id": manifest["condition_id"],
                      "result_status": manifest["result_status"],
                      "exit_code": args.exit_code,
                      "files_verified": len(manifest["outputs_sha256"]),
                      "manifest_sha256": sha(target)}, indent=2))


if __name__ == "__main__":
    main()
