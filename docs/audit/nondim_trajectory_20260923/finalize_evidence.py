"""Register before any trajectory run, then bind native evidence without refitting.

python docs/audit/nondim_trajectory_20260923/finalize_evidence.py register
python docs/audit/nondim_trajectory_20260923/finalize_evidence.py finalize
The register command refuses to overwrite preregistration. Finalize never runs
MATLAB or changes criteria. Re-running finalize refreshes document fingerprints.
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[2]
EXPECTED_HEAD = "0b6fd01287fad6ee323ce4f9ed27e9605701ff6a"
DOC_CHANGES = {
    "docs/theory/conservation_report.md", "docs/theory_notes.md",
    "docs/reports/g1_pending_human_actions.md", "docs/reports/g1_report.md",
}
IMPLEMENTATION = [
    "matlab/src/theory/pure_nondim_map.m",
    "matlab/src/theory/rhs_pure_literature_dimensionless.m",
    "matlab/src/theory/simulate_pure_literature_dimensionless.m",
    "matlab/tests/test_dimensionless_trajectory_equivalence.m",
    "scripts/run_nondim_trajectory_validation.m",
    "docs/audit/nondim_trajectory_20260923/finalize_evidence.py",
    "matlab/src/theory/jacobian_pure_literature_dimensionless.m",
]


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args]).decode("utf-8").strip()


def fingerprints(paths):
    return [{"path": p, "sha256": sha(ROOT / p)} for p in sorted(paths)]


def register():
    assert not (AUDIT / "preregistration.json").exists(), "Never overwrite preregistration."
    assert git("rev-parse", "HEAD") == EXPECTED_HEAD
    remote = git("ls-remote", "origin", "refs/heads/main").split()[0]
    assert remote == EXPECTED_HEAD, "Remote main differs; report without merge/rebase."
    assert not git("diff", "--name-only"), "Registration expects original tracked files unchanged."
    assert not git("diff", "--cached", "--name-only")
    files = [p for p in git("ls-files", "-z").split("\0") if p]
    write_json(AUDIT / "integrity_before.json", {
        "recorded_at_utc": now(), "head": EXPECTED_HEAD, "remote_main": remote,
        "initial_worktree_observed_clean": True,
        "initial_status": "On branch main; up to date with origin/main; nothing to commit, working tree clean",
        "initial_log_5": git("log", "-5", "--oneline").splitlines(),
        "files": fingerprints(files),
    })
    write_json(AUDIT / "preregistration.json", {
        "schema_version": "1.0", "registered_at_utc": now(),
        "registered_before_first_trajectory_validation": True,
        "source_commit": EXPECTED_HEAD, "remote_main": remote,
        "criteria_sha256": sha(AUDIT / "acceptance_criteria.json"),
        "integrity_before_sha256": sha(AUDIT / "integrity_before.json"),
        "implementation": fingerprints(IMPLEMENTATION),
        "allowed_original_document_changes_after_success": sorted(DOC_CHANGES),
    })
    print("Registered fixed criteria, source inventory and implementation before trajectory validation.")


def finalize():
    reg = read_json(AUDIT / "preregistration.json")
    assert sha(AUDIT / "acceptance_criteria.json") == reg["criteria_sha256"]
    assert sha(AUDIT / "integrity_before.json") == reg["integrity_before_sha256"]
    revision = read_json(AUDIT / "implementation_revision_4.json")
    assert revision["previous_revision_sha256"] == sha(AUDIT / "implementation_revision_3.json")
    prior = read_json(AUDIT / "implementation_revision_3.json")
    assert prior["previous_revision_sha256"] == sha(AUDIT / "implementation_revision_2.json")
    prior = read_json(AUDIT / "implementation_revision_2.json")
    assert prior["previous_revision_sha256"] == sha(AUDIT / "implementation_revision.json")
    assert revision["criteria_sha256"] == reg["criteria_sha256"]
    assert revision["original_preregistration_sha256"] == sha(AUDIT / "preregistration.json")
    for item in revision["implementation"] + revision["initial_attempt_evidence"]:
        assert sha(ROOT / item["path"]) == item["sha256"], item["path"]
    # The mapping builder and compact ODE are identical to the first run.
    for item in reg["implementation"]:
        if item["path"].endswith(("pure_nondim_map.m", "rhs_pure_literature_dimensionless.m")):
            assert sha(ROOT / item["path"]) == item["sha256"]
    before = read_json(AUDIT / "integrity_before.json")
    missing = [f["path"] for f in before["files"] if not (ROOT / f["path"]).is_file()]
    changed = [f["path"] for f in before["files"]
               if (ROOT / f["path"]).is_file() and sha(ROOT / f["path"]) != f["sha256"]]
    unexpected = sorted(set(changed) - DOC_CHANGES)
    integrity = {
        "checked_at_utc": now(), "source_commit": before["head"],
        "original_tracked_files_checked": len(before["files"]),
        "changed_original_files": changed, "missing_original_files": missing,
        "unexpected_original_changes": unexpected,
        "unchanged_original_files_count": len(before["files"]) - len(changed) - len(missing),
        "canonical_B1_and_baselines_byte_unchanged": not unexpected and not missing,
        "audited_dimensionless_definitions_byte_unchanged": not unexpected and not missing,
        "original_preregistration_and_criteria_unchanged": True,
        "registered_revised_implementation_matches_tested_source": True,
        "initial_compact_RHS_and_mapping_builder_unchanged": True,
    }
    write_json(AUDIT / "integrity_after.json", integrity)
    assert not missing and not unexpected, "Original protected files changed; inspect integrity_after.json."
    assert git("rev-parse", "HEAD") == EXPECTED_HEAD
    assert (AUDIT / "matlab_exitcode.txt").read_text(encoding="utf-8-sig").strip() == "0"
    assert not (AUDIT / "matlab_stderr.txt").read_bytes()
    raw = (AUDIT / "matlab_stdout.txt").read_bytes()
    # Preserve native evidence; create a readable UTF-8 copy with byte roundtrip.
    try:
        decoded = raw.decode("utf-8")
        encoding = "utf-8"
    except UnicodeDecodeError:
        decoded = raw.decode("gb18030")
        encoding = "gb18030"
    assert decoded.encode(encoding) == raw
    (AUDIT / "matlab_stdout.utf8.txt").write_bytes(decoded.encode("utf-8"))
    stdout = raw.decode("ascii", errors="replace")

    def records(marker):
        return [json.loads(s) for s in re.findall(re.escape(marker) + r" (.+)", stdout)]

    summary, = records("NONDIM_TEST_SUMMARY")
    rhs, = records("NONDIM_RHS")
    initial, = records("NONDIM_INITIAL")
    roundtrip, = records("NONDIM_ROUNDTRIP")
    parameters, = records("NONDIM_PARAMETERS")
    symbolic, = records("NONDIM_SYMBOLIC")
    symbolic_output, = records("NONDIM_SYMBOLIC_OUTPUT")
    jacobian, = records("NONDIM_JACOBIAN")
    cases = records("NONDIM_CASE")
    physicality = records("NONDIM_PHYSICALITY")
    rates = records("NONDIM_RATE_BACKTRANSFORM")
    started, = re.findall(r"NONDIM_RUN_STARTED (\S+)", stdout)
    assert datetime.fromisoformat(started) > datetime.fromisoformat(reg["registered_at_utc"])
    assert datetime.fromisoformat(started) > datetime.fromisoformat(revision["registered_at_utc"])
    assert summary["allPassed"] and len(summary["suites"]) == 4
    assert all(s["passed"] > 0 and s["failed"] == s["incomplete"] == 0 for s in summary["suites"])
    c = read_json(AUDIT / "acceptance_criteria.json")
    assert rhs["max_absolute_residual"] <= c["rhs_absolute_tolerance"]
    assert initial == [1,0,0,1,1,0,0,1,0,1,0,0]
    assert symbolic["passed"] and symbolic["generated_text_byte_unchanged"]
    assert jacobian["max_scaled_complex_step_residual"] <= 1e-12
    assert jacobian["max_abs_I6_derivative_uM_per_s"] <= c["rhs_absolute_tolerance"]
    assert len(cases) == len(physicality) == len(rates) == 3
    for collection in (cases, physicality, rates):
        assert [x["DNA_uM"] for x in collection] == c["DNA_uM"]
    for case in cases:
        assert case["trajectory_pass"] and case["output_points"] == 1441
        for quantity in ("states", "rates", "compact_backtransformed_rates", "mRNA", "protein"):
            assert case[quantity]["max_normalized"] <= 1e-6
    for case in physicality:
        assert case["all_finite"]
        assert min(case["backtransform_min_per_state"]) >= -case["roundoff_allowance_uM"]
        assert case["max_scaled_invariant_residual"] <= c["invariant_scaled_tolerance"]
    assert all(x["max_scaled_residual"] <= c["rate_backtransform_scaled_tolerance"] for x in rates)
    result = {
        "schema_version": "1.0", "scope": "Frozen B1 deterministic mathematical/numerical equivalence only",
        "source_commit": EXPECTED_HEAD, "run_started_at_utc": started,
        "criteria_sha256": reg["criteria_sha256"], "stdout_sha256": sha(AUDIT / "matlab_stdout.txt"),
        "native_stdout_encoding": encoding, "summary": summary, "roundtrip": roundtrip,
        "initial_dimensionless_state": initial, "parameters": parameters, "pointwise_rhs": rhs,
        "cases": cases, "rate_backtransform": rates, "physicality": physicality,
        "symbolic_regression": symbolic, "symbolic_generated_output": symbolic_output, "jacobian": jacobian,
        "implementation_revision": revision,
        "initial_attempt": {"allPassed": False, "failure": "I6 invariant drift with finite-difference solver Jacobian",
                            "evidence": "initial_attempt_stdout.txt", "max_I6_drift_uM": 4.3267576188554813e-8},
        "solver_attempt": {"allPassed": True, "native_exitcode": 1,
                           "failure": "Post-test symbolic output differed only by CRLF to LF line endings",
                           "evidence": "solver_attempt_stdout.txt"},
        "D6_complete": True,
    }
    write_json(AUDIT / "validation_results.json", result)
    certificate_path = ROOT / "docs/theory/nondim_map.json"
    certificate = read_json(certificate_path)
    runtime_sources = [p for p in IMPLEMENTATION if p.endswith(".m")]
    certificate["source_fingerprints_sha256"] = fingerprints(certificate["source_files"] + runtime_sources)
    certificate["validation"].update({
        "status": "PASS", "D6_complete": True, "source_commit": EXPECTED_HEAD,
        "validated_at_utc": started, "criteria_sha256": reg["criteria_sha256"],
        "evidence": "docs/audit/nondim_trajectory_20260923/validation_results.json",
        "evidence_sha256": sha(AUDIT / "validation_results.json"),
        "canonical_B1_and_baselines_byte_unchanged": True,
        "audited_dimensionless_definitions_byte_unchanged": True,
        "allPassed": summary["allPassed"],
    })
    write_json(certificate_path, certificate)
    artifacts = [p.relative_to(ROOT).as_posix() for p in AUDIT.iterdir()
                 if p.is_file() and p.name != "artifact_manifest.json"]
    write_json(AUDIT / "artifact_manifest.json", {
        "recorded_at_utc": now(), "source_commit": EXPECTED_HEAD,
        "files": fingerprints(artifacts + runtime_sources + sorted(DOC_CHANGES) + ["docs/theory/nondim_map.json"]),
    })
    print(json.dumps({"D6_complete": True, "summary": summary, "integrity": integrity}, indent=2))


if __name__ == "__main__":
    {"register": register, "finalize": finalize}[sys.argv[1]]()
