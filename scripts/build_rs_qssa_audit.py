"""Derive D7 navigation/audit metadata; never replace MATLAB evidence.

Run after MATLAB validation and again after final_regression_results.json exists.
--verify checks current bytes; --staged checks the corresponding Git index bytes.
No third-party Python packages are required.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import subprocess

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/audit/rs_qssa_d7_20260924"
INPUT = "c2bb0ae63ba106d4f51bf2182dfd28dfe187e743"
PREREG = "cec84861ab829bf451d6902283e5f078a6e89401"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def reference_checks(result, params):
    for item in result["implementation"] + params["source_fingerprints"]:
        assert digest((ROOT / item["path"]).read_bytes()) == item["sha256"], item["path"]
    for name in ("preregistration.json", "acceptance_criteria.json"):
        rel = f"docs/audit/rs_qssa_d7_20260924/{name}"
        assert git("show", f"{PREREG}:{rel}") == (ROOT / rel).read_bytes(), rel
    protected = ["models/literature_reference", "matlab/generated", "references", "data/provenance.csv",
                 "docs/audit/exact_conservation_20260922", "docs/audit/nondim_trajectory_20260923",
                 "docs/audit/nondimensionalization_validation_20260923",
                 "docs/audit/nondimensionalization_validation_v2_20260923"]
    assert not git("diff", "--name-only", INPUT, "--", *protected).strip(), "Frozen content changed"
    old = git("show", f"{INPUT}:docs/theory_notes.md").decode("utf-8").replace("\r\n", "\n")
    new = (ROOT / "docs/theory_notes.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert old.split("## 8. D7", 1)[0] == new.split("## 8. D7", 1)[0], "D1-D6 text changed"


def csv_checks(result):
    """Independently recalculate MATLAB-reported errors from exported CSV bytes."""
    rows = []
    names = ["NTP", "NXP", "nt", "A", "T", "AT", "a", "CP", "C", "TLcat"]
    for index, case in enumerate(result["measurements"]["CASE"], 1):
        tables = []
        for model in ("full_explicit", "qssa"):
            with (AUDIT / result["run_label"] / f"dna_{index}_{model}.csv").open(newline="", encoding="utf-8-sig") as stream:
                table = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]
            assert len(table) == 1441
            assert [row["time_s"] for row in table] == list(range(0, 14401, 10))
            tables.append(table)
        full, reduced = tables
        errors = {}
        for group, columns in (("states", names), ("RS_flux", ["V_RS"]), ("mRNA", ["mRNA"]), ("protein", ["protein"])):
            e = max(max(abs(a[key] - b[key]) for a, b in zip(full, reduced)) /
                    max(max(abs(a[key]) for a in full), 1e-12) for key in columns)
            assert e <= 1e-3
            assert math.isclose(e, case[group]["max_normalized"], rel_tol=1e-5, abs_tol=1e-12), (index, group, e)
            errors[group] = e
        max_eps = max(row["diag_epsilon_state"] for table in tables for row in table)
        assert max_eps < 1e-2
        for table in tables:
            assert all(math.isfinite(row[key]) for row in table for key in names + ["V_RS", "mRNA", "protein"])
            assert min(row[key] for row in table for key in names) >= 0
        rows.append({"DNA_uM": case["DNA_uM"], "output_points": 1441,
                     "independently_recomputed_normalized_errors": errors, "max_epsilon_state": max_eps})
    return {"method": "Python standard-library CSV parsing, independent per-quantity peak normalization", "cases": rows, "passed": True}


def build():
    result = read(AUDIT / "validation_results.json")
    params = read(ROOT / "models/reductions/rs_qssa/parameters.json")
    reference_checks(result, params)
    source_bindings = []
    for item in params["source_fingerprints"]:
        raw = (ROOT / item["path"]).read_bytes()
        blob = git("show", f"{INPUT}:{item['path']}")
        if raw != blob:
            assert raw.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), item["path"]
        source_bindings.append({"path": item["path"], "tested_raw_sha256": digest(raw),
                                "git_blob_sha256": digest(blob), "git_blob_bytes": len(blob),
                                "normalized_text_identical": raw.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"),
                                "difference": "none" if raw == blob else "checkout line endings only; original bytes preserved"})
    write(AUDIT / "source_byte_bindings.json", source_bindings)
    assert result["all_passed"] and result["d7_tests"]["Passed"] == 13
    assert result["d7_tests"]["Failed"] == result["d7_tests"]["Incomplete"] == 0
    assert all(not entry["messages"] for entry in result["checkcode"])
    repo = result["repository"]
    assert repo["unit_tests_failed"] == repo["unit_tests_incomplete"] == 0
    assert repo["smoke_test"] == "passed" and repo["preflight"]["development_checks_passed"]
    csv_result = csv_checks(result)
    write(AUDIT / "independent_csv_check.json", csv_result)
    final_path = AUDIT / "final_regression_results.json"
    final = read(final_path) if final_path.exists() else None
    if final:
        assert final["unit_tests_passed"] == 102
        assert final["unit_tests_failed"] == final["unit_tests_incomplete"] == 0
        assert final["smoke_test"] == "passed" and final["preflight"]["development_checks_passed"]
    m = result["measurements"]
    trajectory_table = "| DNA (uM) | all slow states | RS transfer flux | mRNA | protein |\n|---:|---:|---:|---:|---:|\n"
    for row in m["CASE"]:
        trajectory_table += "| " + " | ".join([f'{row["DNA_uM"]:g}'] +
            [f'{row[key]["max_normalized"]:.9e}' for key in ("states", "RS_flux", "mRNA", "protein")]) + " |\n"
    max_state_eps = max(row[model]["max_epsilon_state"] for row in m["TIMESCALES"] for model in ("full", "reduced"))
    max_track_eps = max(row[model]["max_epsilon_track"] for row in m["TIMESCALES"] for model in ("full", "reduced"))
    invariant = max(row[key] for row in m["PHYSICALITY"] for key in
                    ("full_max_normalized_invariant_residual", "reduced_max_normalized_invariant_residual"))
    status = ("D7 = COMPLETE for analytical derivation + synthetic main-backbone numerical validation. "
              "This does not establish experimental/microscopic validity of the one-intermediate aaRS surrogate.") if final else "D7 scientific gates passed; final repository regression pending."
    audit_text = f"""# D7 RS QSSA validation audit

**{status}**

Input commit: `{INPUT}`. Preregistration commit: `{PREREG}`.
Criteria SHA-256: `{result['criteria_sha256']}`. MATLAB: {result['matlab_version']}.
Source/runtime SHA-256 values describe the dirty implementation actually tested after preregistration;
the final implementation commit is the Git commit containing this audit, not the execution commit.

## Run history

| Run | D7 Passed / Failed / Incomplete | Repository | Overall outcome |
|---|---|---|---|
| run_001 | 13 / 0 / 0 | not reached | INCOMPLETE: TestResult metadata serialization bug |
| run_002 | 13 / 0 / 0 | 102 / 0 / 0 + smoke PASS | PASS |
| final regression | included in repository suite | {'102 / 0 / 0 + smoke PASS' if final else 'pending'} | {'PASS' if final else 'pending'} |

`implementation_revision_1.json` explains the reporting repair. Original logs and trajectories remain.
No equation, parameter, solver setting, or threshold changed between runs.
All {len(result['checkcode'])} new/modified MATLAB files have zero checkcode messages in run_002.
Development preflight passed every check. `release_ready=false` records a dirty development checkout;
it is not a scientific gate failure, and no release-readiness flag was rewritten.
The pre-existing startup warning about the missing external `slanCM` folder is retained in process logs.

## Fixed-profile results

All errors below use the preregistered per-quantity full-trajectory peak normalization.
Each trajectory contains 1441 points, 0–14400 s at 10 s intervals. Raw errors and scales are in JSON.

{trajectory_table}
Reference V_RS match: {m['PARAMETERS']['reference_flux_normalized_error']:.9e}.
Reference M_qss match: {m['PARAMETERS']['reference_M_normalized_error']:.9e}.
QSS algebraic residual: {m['ALGEBRA']['max_QSS_normalized_residual']:.9e}.
Manifold derivative error: {m['DERIVATIVES']['max_dh_normalized_error']:.9e}.
Complete chain Jacobian error: {m['DERIVATIVES']['max_chain_J_normalized_error']:.9e}.
Full explicit Jacobian error: {m['DERIVATIVES']['max_explicit_J_normalized_error']:.9e}.
Fast-relaxation concentration error: {m['FAST_RELAXATION']['max_normalized_error']:.9e};
measured tau relative error: {m['FAST_RELAXATION']['normalized_tau_error']:.9e}.
Maximum epsilon_state: {max_state_eps:.9e}; epsilon_track: {max_track_eps:.9e}.
Maximum normalized invariant residual: {invariant:.9e}.
No negative physical, accounting, or free-enzyme outputs were observed; no clipping or projection.
All six invariants, including original I6 without an M term, passed.

Full explicit NTP/AA inventories include M; reduced coarse invariants do not include reconstructed h.
Both start at the same ten slow concentrations, with full M0 = 0.008 uM, so full totals exceed reduced
coarse totals by M0. Each invariant is checked against its own initial value. This distinction is not hidden.

## Evidence and replay

- `validation_results.json`: current measured results, 13 native TestResult rows, code fingerprints,
  raw/per-quantity errors, invariant residues, physicality minima and full/reduced timescale statistics.
- `run_002/native_TestResults.mat`: native MATLAB objects, alongside CSV and MAT trajectories for all DNA cases.
- `run_001/` and `process_stdout_001.txt`: retained first run and reporting exception.
- `final_regression_results.json` and `final_regression_stdout.txt`: final full-suite replay.
- `independent_csv_check.json`: independent recomputation of reported errors from the exported trajectory bytes.
- `evidence_map.json`: derived EXTRACTED/INFERRED/AMBIGUOUS navigation with fingerprints; never source authority.
- `artifact_manifest.json`: SHA-256 of bound files, excluding itself; verify current or staged bytes with the builder.
- `source_byte_bindings.json`: frozen source working bytes versus input-commit blobs. Three pre-existing
  text checkouts use CRLF while their blobs use LF; the text is identical. Staged verification uses the
  recorded original blob hashes for these sources, without normalizing or editing canonical files.
- `git_status_before.txt`: snapshot before preregistration commit (prereg files were then untracked).
  `git_status_after.txt`: snapshot after validation, before final commit; post-push cleanliness is verified separately.

From repo root in MATLAB:
```matlab
addpath('scripts');
s = run_rs_qssa_validation('RunLabel','run_003','FullSuite',true);
assert(s.all_passed);
```
Choose a fresh run label: existing formal runs are never overwritten.
From the shell: `python scripts/build_rs_qssa_audit.py --verify`; use `--staged` after staging.
The builder also verifies frozen inputs, unchanged D1–D6 text, and exact preregistration bytes.

Microparameters are **synthetic_reduction_only**; Eq.8 supplies a local reference flux, not an identity.
The verified local Mavelli PDF supplies apparent kinetics, not this surrogate's k1/kminus1/k2.
The legacy extracted-text hash entry is stale; current text/PDF fingerprints are explicit in parameter JSON.
Experimental microkinetics, PPi lumping, and biological adequacy for heterogeneous aaRS remain unsupported.
D8 next step: preregister applicability and failure-domain comparisons; no D8 study was run here.
"""
    (AUDIT / "README.md").write_text(audit_text, encoding="utf-8", newline="\n")
    nodes = [
        ("canonical", "EXTRACTED", "Frozen canonical backbone and primary source", "models/literature_reference/model_definition.json"),
        ("criteria", "EXTRACTED", "Acceptance criteria frozen before execution", "docs/audit/rs_qssa_d7_20260924/acceptance_criteria.json"),
        ("parameters", "INFERRED", "Synthetic local construction, not sourced microscopic constants", "models/reductions/rs_qssa/parameters.json"),
        ("full", "INFERRED", "Declared explicit surrogate coupling", "matlab/src/theory/rhs_pure_rs_explicit.m"),
        ("manifold", "INFERRED", "Algebraic solution G(s,h)=0", "matlab/src/theory/rs_qssa_manifold.m"),
        ("qssa", "INFERRED", "Restriction F(s,h(s))", "matlab/src/theory/rhs_pure_rs_qssa.m"),
        ("jacobian", "INFERRED", "Analytic Fs+FM*dh", "matlab/src/theory/jacobian_pure_rs_qssa_chain.m"),
        ("tests", "EXTRACTED", "MATLAB executable acceptance checks", "matlab/tests/test_rs_qssa_reduction.m"),
        ("results", "EXTRACTED", "Native MATLAB run_002 results", "docs/audit/rs_qssa_d7_20260924/run_002/validation_results.json"),
        ("biology", "AMBIGUOUS", "Experimental adequacy unresolved; no supporting experiment", "docs/theory/reduction_certificate.md"),
    ]
    edges = [("canonical", "parameters", "supplies_reference_flux"), ("parameters", "full", "parameterizes"),
             ("full", "manifold", "reduced_by_G_zero"), ("manifold", "qssa", "substitutes_into_F"),
             ("manifold", "jacobian", "supplies_chain_derivative"), ("criteria", "tests", "gates"),
             ("qssa", "tests", "tested_against_full"), ("jacobian", "tests", "checked_with_complex_step"),
             ("tests", "results", "produces"), ("results", "biology", "does_not_establish")]
    graph = {"schema_version": "1.0", "role": "derived navigation; not source authority", "input_commit": INPUT,
             "claim_freshness": "verify each source fingerprint; no claim upgrades from graph links",
             "nodes": [{"id": key, "classification": tag, "claim": claim, "source": path,
                        "sha256": digest((ROOT / path).read_bytes()),
                        "confidence": "unresolved" if tag == "AMBIGUOUS" else "verified within declared source/synthetic scope"}
                       for key, tag, claim, path in nodes],
             "edges": [{"from": a, "to": b, "relation": relation} for a, b, relation in edges]}
    write(AUDIT / "evidence_map.json", graph)
    files = set(AUDIT.rglob("*"))
    files.update(ROOT / entry["path"] for entry in result["implementation"] + params["source_fingerprints"])
    files.update([ROOT / "scripts/build_rs_qssa_audit.py", ROOT / "models/reductions/rs_qssa/parameters.json",
                  ROOT / "docs/theory/reduction_certificate.md", ROOT / "docs/theory_notes.md", ROOT / ".gitattributes"])
    files.discard(AUDIT / "artifact_manifest.json")
    entries = [{"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size,
                "sha256": digest(path.read_bytes())} for path in sorted(files) if path.is_file()]
    original_blobs = {item["path"]: item for item in source_bindings}
    for item in entries:
        if item["path"] in original_blobs:
            original = original_blobs[item["path"]]
            item["git_blob_sha256"] = original["git_blob_sha256"]
            item["git_blob_bytes"] = original["git_blob_bytes"]
    write(AUDIT / "artifact_manifest.json", {"schema_version": "1.0", "input_commit": INPUT,
          "preregistration_commit": PREREG, "status": status, "self_excluded": True, "files": entries})
    print(json.dumps({"bound_files": len(entries), "independent_csv_check": "PASS", "status": status}))


def verify(staged=False):
    manifest = read(AUDIT / "artifact_manifest.json")
    for entry in manifest["files"]:
        data = git("show", ":" + entry["path"]) if staged else (ROOT / entry["path"]).read_bytes()
        expected_hash = entry.get("git_blob_sha256", entry["sha256"]) if staged else entry["sha256"]
        expected_bytes = entry.get("git_blob_bytes", entry["bytes"]) if staged else entry["bytes"]
        assert len(data) == expected_bytes and digest(data) == expected_hash, entry["path"]
    print(f"PASS: {len(manifest['files'])} {'staged' if staged else 'working-tree'} SHA-256 bindings")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()
    if args.verify or args.staged:
        verify(args.staged)
    else:
        build()
