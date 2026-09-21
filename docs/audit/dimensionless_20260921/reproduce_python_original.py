"""Bounded original-source replay, preserving unbuffered stdout on timeout."""
import json
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
path = "models/literature_reference/dimensionless/derive_dimensionless.py"
target = root/"results/runs/dimensionless_audit_20260921/original/derive_dimensionless.py"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(subprocess.check_output(["git", "show", "1aed082:"+path], cwd=root))
cmd = [sys.executable, "-u", str(target)]
started = time.monotonic()
try:
    run = subprocess.run(cmd, capture_output=True, timeout=60, cwd=root)
    stdout, stderr, status = run.stdout, run.stderr, {"exit_code": run.returncode, "timed_out": False}
except subprocess.TimeoutExpired as exc:
    stdout, stderr, status = exc.stdout or b"", exc.stderr or b"", {"exit_code": None, "timed_out": True}
(out/"python_original_replay.stdout.txt").write_bytes(stdout)
(out/"python_original_replay.stderr.txt").write_bytes(stderr)
status.update(command=cmd, duration_seconds=time.monotonic()-started, timeout_seconds=60)
(out/"python_original_replay.status.json").write_text(json.dumps(status, indent=2)+"\n")
print(json.dumps(status))
