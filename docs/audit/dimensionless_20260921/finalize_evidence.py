"""Record source identities and check the saved native-run terminal states."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
source_paths = [
    "models/literature_reference/model_definition.json",
    "models/literature_reference/parameters.json",
    "models/literature_reference/model_manifest.json",
    "models/literature_reference/species.csv",
    "models/literature_reference/reactions.csv",
    "matlab/generated/rhs_pure_literature_reference.m",
    "matlab/generated/pure_literature_reference_params.m",
    "matlab/src/simulate/simulate_pure_literature_reference.m",
    "matlab/tests/test_pure_literature_reference.m",
    "models/literature_reference/dimensionless/verify_wolfram_v2.wl",
    "models/literature_reference/dimensionless/derive_dimensionless.py",
    "models/literature_reference/dimensionless/derive_dimensionless.m",
    "models/literature_reference/dimensionless/README.md",
    "models/literature_reference/dimensionless/dimensionless_result.txt",
    "models/literature_reference/dimensionless/dimensionless_result_matlab.txt",
    "docs/theory_notes.md",
]
sources = []
for name in source_paths:
    raw = (root/name).read_bytes()
    base = subprocess.run(["git", "show", "HEAD:"+name], cwd=root, capture_output=True)
    unchanged = base.returncode == 0 and raw.replace(b"\r\n", b"\n") == base.stdout.replace(b"\r\n", b"\n")
    sources.append({"path": name, "sha256": hashlib.sha256(raw).hexdigest(),
                    "unchanged_from_HEAD_ignoring_CRLF": unchanged})
assert all(row["unchanged_from_HEAD_ignoring_CRLF"] for row in sources[:9])
assert sources[13]["unchanged_from_HEAD_ignoring_CRLF"]

runs = {}
for name, marker in {
    "wolfram_fixed": "AUDIT ALL PASS: True",
    "python_fixed_direct": "ALL PASS (5 trials x 12 eqs)",
    "python_fixed_source_bridge": "SOURCE BRIDGE ALL PASS",
    "matlab_fixed": "MATLAB AUDIT ALL PASS (9 existing model tests)",
    "mutations": "MUTATION / CONTEXT CHECKS: ALL PASS",
}.items():
    code = int((out/(name+".exitcode.txt")).read_text().strip())
    stdout = (out/(name+".stdout.txt")).read_bytes()
    assert code == 0 and marker.encode() in stdout, name
    assert not (out/(name+".stderr.txt")).read_bytes(), name
    runs[name] = {"exit_code": code, "success_marker": marker, "stderr_empty": True}

for path in sorted(out.glob("matlab_*.std*.txt")):
    if ".utf8." in path.name:
        continue
    raw = path.read_bytes()
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError:
        decoded = raw.decode("gb18030")
    (out/(path.stem+".utf8.txt")).write_text(decoded, encoding="utf-8")

subprocess.run(["git", "diff", "--check"], cwd=root, check=True, capture_output=True)
artifacts = [{"path": str(p.relative_to(root)).replace("\\", "/"),
              "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.iterdir())
             if p.is_file() and p.name != "provenance.json"]
result = {"recorded_at_utc": datetime.now(timezone.utc).isoformat(),
          "baseline_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip(),
          "sources": sources, "verified_fixed_runs": runs, "evidence_artifacts": artifacts,
          "canonical_assets_unchanged": True, "git_diff_check": "PASS",
          "original_python_initial_run": "manually terminated during display factorization; exit -1; later original-source replay completed with exit 0"}
(out/"provenance.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print("FINAL EVIDENCE CHECK: PASS; canonical assets and compact reference unchanged")
