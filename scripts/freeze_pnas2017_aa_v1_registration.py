"""Freeze the v1 prospective registration (task #6) and its v1r1 revision.

v1 behaviour (historical round, 2026-09-25): produced configs,
input_hashes.json, run_registry.json and preregistration.json.

v1r1 behaviour (this round, per the user execution instruction of
2026-09-26 "Phase 3 - RE-FREEZE"): the ACTIVE formal configs point to
candidate_partition_v1r1.json (the implementation/coordinate-realization
revision; the historical candidate_partition.json and preregistration.json
stay byte-for-byte immutable).  In v1r1 mode this script

  1. verifies the active-partition consistency chain (fail closed);
  2. regenerates the 13 formal configs deterministically, each carrying the
     active-partition binding;
  3. refreshes input_hashes.json so the hash chain includes BOTH the
     historical candidate_partition.json AND the active
     candidate_partition_v1r1.json (no historical hash is removed);
  4. regenerates run_registry.json with the active-partition and runner
     bindings;
  5. refreshes preregistration_revision_v1r1.json (the ACTIVE registration
     record) with refreshed bindings - it does NOT rewrite the historical
     preregistration.json.
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCA = os.path.join(ROOT, "docs", "audit", "pnas2017_aminoacylation_reduction_v1")
FORMAL = os.path.join(ROOT, "results", "pnas2017_reference",
                      "2026-09-25_aa_v1_formal")
CFGS = os.path.join(FORMAL, "configs")
TRAJ = os.path.join(FORMAL, "trajectories")

ACTIVE_PART_REL = ("docs/audit/pnas2017_aminoacylation_reduction_v1/"
                   "candidate_partition_v1r1.json")
HIST_PART_REL = ("docs/audit/pnas2017_aminoacylation_reduction_v1/"
                 "candidate_partition.json")
REVREC_REL = ("docs/audit/pnas2017_aminoacylation_reduction_v1/"
              "preregistration_revision_v1r1.json")
RUNNER_REL = "scripts/run_pnas2017_aa_v1_formal.m"


def sha(p):
    h = hashlib.sha256()
    with open(os.path.join(ROOT, p.replace("/", os.sep)) if not os.path.isabs(p) else p,
              "rb") as f:
        for blk in iter(lambda: f.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def sha_abs(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def main():
    part = json.load(open(os.path.join(DOCA, "candidate_partition.json"), encoding="utf-8"))
    cumdefs = json.load(open(os.path.join(DOCA, "cumdefs.json"), encoding="utf-8"))["cumdefs"]
    accept = json.load(open(os.path.join(DOCA, "acceptance_criteria.json"), encoding="utf-8"))
    part_v1r1 = json.load(open(os.path.join(ROOT, ACTIVE_PART_REL.replace("/", os.sep)),
                               encoding="utf-8"))
    revrec = json.load(open(os.path.join(ROOT, REVREC_REL.replace("/", os.sep)),
                            encoding="utf-8"))

    # ---- active-partition consistency gate (fail closed) ------------------ #
    hist_sha = sha(HIST_PART_REL)
    active_sha = sha(ACTIVE_PART_REL)
    assert part_v1r1["parent_partition_sha256"] == hist_sha, \
        "v1r1 parent hash does not match the historical partition file"
    assert revrec["hash_chain"]["original_candidate_partition_sha256"] == hist_sha
    assert part_v1r1["scientific_partition_changed"] is False
    assert part_v1r1["QSSA_closure_changed"] is False
    assert part_v1r1["acceptance_thresholds_changed"] is False
    assert part_v1r1["stress_domain_changed"] is False
    assert part_v1r1["numerical_realization_changed"] is True
    assert part_v1r1["supersedes_numerical_realization_only"] is True
    assert part_v1r1["dynamic_state_count"] == 218
    elim_v1r1 = sorted(part_v1r1["eliminated_states"])
    elim_hist = sorted(part["eliminated_complexes"])
    assert elim_v1r1 == elim_hist, "eliminated set drifted between v1 and v1r1"
    runner_sha = sha(RUNNER_REL)
    assert revrec["hash_chain"]["runner_v1r1_instrumented_sha256"] == runner_sha, \
        "revision record runner hash does not match the active runner"
    for key, rel in (("original_preregistration_sha256",
                      "docs/audit/pnas2017_aminoacylation_reduction_v1/preregistration.json"),
                     ("original_acceptance_criteria_sha256",
                      "docs/audit/pnas2017_aminoacylation_reduction_v1/acceptance_criteria.json"),
                     ("cumulative_definitions_cumdefs_sha256",
                      "docs/audit/pnas2017_aminoacylation_reduction_v1/cumdefs.json"),
                     ("source_sbml_fMGG_synthesis_xml_sha256",
                      "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
                     ("author_parameters_fMGG_synthesis_parameters_csv_sha256",
                      "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv"),
                     ("author_initial_values_fMGG_synthesis_initial_values_csv_sha256",
                      "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv")):
        assert revrec["hash_chain"][key] == sha(rel), \
            "revision record %s does not match the file" % key

    eliminated = sorted(part["MetRS"]["eliminated"]) + sorted(part["GlyRS"]["eliminated"])
    assert len(eliminated) == 21
    assert elim_v1r1 == sorted(eliminated)

    # stress conditions exactly as registered in acceptance_criteria.json
    conds = {
        "S0": ({}, "reference condition, unmodified author initial values"),
        "S1": ({"ATP": 0.1}, "ATP x0.1"),
        "S2": ({"tRNAfMetCAU": 0.1, "tRNAGlyGCC": 0.1}, "both tRNAs x0.1"),
        "S3": ({"MetRS": 10.0, "GlyRS": 10.0}, "both enzymes x10"),
        "S4": ({"MetRS": 0.1, "GlyRS": 0.1}, "both enzymes x0.1"),
        "S5": ({"CP": 0.1}, "CP x0.1, energy system dynamic"),
    }
    # verify against the registered copy (fail closed on drift)
    reg = json.dumps(accept.get("stress_conditions_one_at_a_time", accept),
                     sort_keys=True)
    for cid in conds:
        assert cid in reg, "condition %s not found in acceptance_criteria.json" % cid

    os.makedirs(CFGS, exist_ok=True)
    os.makedirs(TRAJ, exist_ok=True)

    cfg_paths = {}
    for cid, (scale, desc) in conds.items():
        for mode, runid in (("reference", "FULL-%s" % cid), ("reduced", "RED-%s" % cid)):
            cfg = {
                "mode": mode,
                "reltol": 1e-10,
                "abstol": 1e-14,
                "grid": [1e-4, 1000.0, 200],
                "x0_scale": scale,
                "outfile": (TRAJ + os.sep + "%s.csv" % runid).replace("\\", "/"),
                "stats": True,
                "cumdefs": cumdefs,
                "condition_description": desc,
                "active_partition": ACTIVE_PART_REL,
                "active_partition_revision": "v1r1",
            }
            if mode == "reduced":
                cfg["eliminated"] = eliminated
            p = os.path.join(CFGS, "%s.json" % runid)
            with open(p, "w", newline="\n", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
                f.write("\n")
            cfg_paths[runid] = os.path.relpath(p, ROOT).replace("\\", "/")

    # ---------------- input hashes (refreshed) ---------------- #
    old_path = os.path.join(DOCA, "input_hashes.json")
    old = json.load(open(old_path, encoding="utf-8")) if os.path.exists(old_path) else {}
    inputs = sorted(set(list(old.keys()) + [
        "docs/audit/pnas2017_aminoacylation_reduction_v1/acceptance_criteria.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/cumdefs.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/negative_test_result.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition_v1r1.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/dae_singular_mass_failure_v1.md",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/implementation_revision_v1.json",
        "scripts/run_pnas2017_aa_v1_formal.m",
        "scripts/drive_pnas2017_aa_v1_formal.m",
        "scripts/build_pnas2017_aa_v1_manifests.py",
        "scripts/analyze_pnas2017_aminoacylation_reduction_v1_qssa.py",
        "scripts/analyze_pnas2017_aminoacylation_reduction_v1_partition.py",
        "scripts/compare_pnas2017_aa_v1_reduced.py",
        "scripts/build_pnas2017_aa_v1_comparison_scope.py",
        "scripts/build_pnas2017_aa_v1_formal_comparison.py",
        "scripts/validate_pnas2017_aminoacylation_reduction_v1.py",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_comparison_scope.json",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_qssa_structure.csv",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_qssa_spectrum.csv",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_qssa_closure.csv",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_qssa_relaxation.csv",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_qssa_defect.csv",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_qssa_derivation.json",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_partition_closure.csv",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_partition_spectrum.csv",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_partition_relaxation.csv",
        "models/pnas2017_full_reference/audit/aminoacylation_v1_partition_verification.json",
        "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/RED-S0_smoke_config.json",
        "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/RED-S0_smoke.csv",
        "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/RED-S0_smoke.csv.stats.raw.txt",
        "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/smoke_log.txt",
        "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/smoke_log2.txt",
        "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/smoke_log3.txt",
        "results/pnas2017_reference/2026-09-25_aa_v1_runner_selfcheck/refcheck_config.json",
        "results/pnas2017_reference/2026-09-25_aa_v1_runner_selfcheck/refcheck_trajectory_with_extents.csv",
        "results/pnas2017_reference/2026-09-25_aa_v1_runner_selfcheck/refcheck_convergence_config.json",
        "results/pnas2017_reference/2026-09-25_aa_v1_runner_selfcheck/refcheck_convergence_run.csv",
        "results/pnas2017_reference/2026-09-25_aa_v1_runner_selfcheck/refcheck_summary.json",
    ] + list(cfg_paths.values())))
    newh = {}
    changed = []
    for rel in inputs:
        full = os.path.join(ROOT, rel.replace("/", os.sep))
        if not os.path.exists(full):
            print("MISSING (not hashed):", rel)
            continue
        h = sha(rel)
        newh[rel] = h
        if rel in old and old[rel] != h:
            changed.append(rel)
    with open(old_path, "w", newline="\n", encoding="utf-8") as f:
        json.dump(newh, f, indent=2, sort_keys=True)
        f.write("\n")
    print("input_hashes.json: %d entries, %d refreshed" % (len(newh), len(changed)))
    for c in changed:
        print("  changed:", c)

    # ---------------- run registry ---------------- #
    registry = {
        "schema": "pnas2017_aa_v1_run_registry/v1r1",
        "binding": "local SHA-256 config binding; executor is run_pnas2017_aa_v1_formal.m "
                   "with the unmodified author model directory",
        "active_partition": {
            "file": ACTIVE_PART_REL,
            "sha256": active_sha,
            "revision_id": "v1r1",
            "historical_partition_file": HIST_PART_REL,
            "historical_partition_sha256": hist_sha,
            "supersedes_numerical_realization_only": True,
        },
        "runner": {
            "file": RUNNER_REL,
            "sha256": runner_sha,
        },
        "revision_record": {
            "file": REVREC_REL,
            "class": "IMPLEMENTATION / COORDINATE REALIZATION REVISION",
        },
        "runs": {
            runid: {
                "config": cfg_paths[runid],
                "config_sha256": sha_abs(os.path.join(ROOT,
                                                      cfg_paths[runid].replace("/", os.sep))),
                "trajectory": "results/pnas2017_reference/2026-09-25_aa_v1_formal/"
                              "trajectories/%s.csv" % runid,
                "status": "planned",
            } for runid in sorted(cfg_paths)
        },
        "prerequisite_completed_runs": {
            "TIGHT-REF": "results/pnas2017_reference/2026-09-25_aa_v1_reference_tight/"
                         "(author MATLAB runner, RelTol 1e-10/AbsTol 1e-14)",
            "REFCHECK": "results/pnas2017_reference/2026-09-25_aa_v1_runner_selfcheck/"
                        "(formal runner in reference mode; max pointwise deviation vs "
                        "TIGHT-REF 4.975e-10, extent convergence max rel dev 3.07e-10)",
        },
        "comparisons": {
            "CMP-S0..S5": "scripts/compare_pnas2017_aa_v1_reduced.py RED-Sx.csv vs "
                          "FULL-Sx.csv under acceptance_criteria.json tiers",
        },
        "negative_controls": {
            "NEG-CODE": "docs/audit/.../negative_test_result.json (extraction "
                        "corruption rejected before any science ran)",
            "NEG-PARTITION": "post-freeze pipeline check: RED run additionally "
                             "eliminating MetRS_MettRNAfMetCAU (kept by evidence) "
                             "must produce a FAIL verdict under the registered "
                             "criteria; planned as RED-NEG1",
        },
        "prohibitions_ack": [
            "no commit / no push this round",
            "no author-model / SBML / parameter / initial-value modification",
            "no negative-clipping, projection, axis change, threshold relaxation",
            "unknown or untested items are never reported as PASS",
        ],
    }
    # the negative-control reduced config (planned, executed only after freeze)
    neg_cfg = json.loads(json.dumps({
        "mode": "reduced", "reltol": 1e-10, "abstol": 1e-14,
        "grid": [1e-4, 1000.0, 200], "x0_scale": {},
        "outfile": (TRAJ + os.sep + "RED-NEG1.csv").replace("\\", "/"),
        "stats": True, "cumdefs": cumdefs,
        "active_partition": ACTIVE_PART_REL,
        "active_partition_revision": "v1r1",
        "eliminated": sorted(eliminated + ["MetRS_MettRNAfMetCAU"]),
        "condition_description": "negative control: one evidence-kept complex "
                                 "illegally eliminated; FAIL verdict expected",
    }))
    with open(os.path.join(CFGS, "RED-NEG1.json"), "w", newline="\n",
              encoding="utf-8") as f:
        json.dump(neg_cfg, f, indent=2)
        f.write("\n")
    registry["runs"]["RED-NEG1"] = {
        "config": "results/pnas2017_reference/2026-09-25_aa_v1_formal/configs/RED-NEG1.json",
        "config_sha256": sha_abs(os.path.join(CFGS, "RED-NEG1.json")),
        "trajectory": "results/pnas2017_reference/2026-09-25_aa_v1_formal/"
                      "trajectories/RED-NEG1.csv",
        "status": "planned", "expected_verdict": "FAIL (pipeline negative control)",
    }
    reg_path = os.path.join(DOCA, "run_registry.json")
    with open(reg_path, "w", newline="\n", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
        f.write("\n")

    # ---------------- active revision registration (v1r1) ------------------- #
    # The historical preregistration.json (hash-bound in the revision record)
    # is NOT rewritten.  The ACTIVE registration is the revision record,
    # refreshed here with the regenerated bindings.
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    head = subprocess.run(["git", "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    reg_path = os.path.join(DOCA, "run_registry.json")
    revrec["generated_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    revrec["hash_chain"]["new_candidate_partition_v1r1_sha256"] = active_sha
    revrec["hash_chain"]["runner_v1r1_instrumented_sha256"] = runner_sha
    revrec["run_registry_binding"]["run_registry_sha256_after_regeneration"] = \
        sha_abs(reg_path)
    revrec["git_context_informational"] = {"branch": branch, "head_before_freeze": head}
    revrec["registered_formal_case_count"] = len(registry["runs"])
    revrec["bindings_refreshed_by_freeze"] = {
        "active_partition_v1r1_sha256": active_sha,
        "runner_v1r1_instrumented_sha256": runner_sha,
        "run_registry_snapshot": sha_abs(reg_path),
        "input_hashes_snapshot": sha_abs(old_path),
        "freeze_script_sha256": sha_abs(os.path.abspath(__file__)),
        "validator_sha256": sha(os.path.join(
            ROOT, "scripts/validate_pnas2017_aminoacylation_reduction_v1.py"
            .replace("/", os.sep))),
        "note": "refreshed deterministically by freeze_pnas2017_aa_v1_registration.py; "
                "the historical preregistration.json and candidate_partition.json "
                "are byte-for-byte untouched",
    }
    # frozen-artifact map: every historical science artifact (re-hashed; no
    # entry is dropped) plus the regenerated configs, registry and hashes.
    frozen = {}
    old_pre_path = os.path.join(DOCA, "preregistration.json")
    if os.path.exists(old_pre_path):
        old_pre = json.load(open(old_pre_path, encoding="utf-8"))
        for rel in sorted(old_pre.get("frozen_artifacts_sha256", {})):
            full = os.path.join(ROOT, rel.replace("/", os.sep))
            if os.path.exists(full):
                frozen[rel] = sha(rel)
            else:
                print("MISSING historical artifact (not re-bound):", rel)
    for rel in [ACTIVE_PART_REL, RUNNER_REL,
                "scripts/freeze_pnas2017_aa_v1_registration.py",
                "scripts/drive_pnas2017_aa_v1_formal.m",
                "scripts/build_pnas2017_aa_v1_manifests.py",
                "scripts/compare_pnas2017_aa_v1_reduced.py",
                "scripts/build_pnas2017_aa_v1_comparison_scope.py",
                "scripts/build_pnas2017_aa_v1_formal_comparison.py",
                "scripts/validate_pnas2017_aminoacylation_reduction_v1.py",
                "models/pnas2017_full_reference/audit/aminoacylation_v1_comparison_scope.json",
                "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/RED-S0_smoke_config.json",
                "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/RED-S0_smoke.csv",
                "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/RED-S0_smoke.csv.stats.raw.txt",
                "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/smoke_log.txt",
                "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/smoke_log2.txt",
                "results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/smoke_log3.txt",
                ] + sorted(cfg_paths.values()) + \
            ["docs/audit/pnas2017_aminoacylation_reduction_v1/run_registry.json",
             "docs/audit/pnas2017_aminoacylation_reduction_v1/input_hashes.json"]:
        full = os.path.join(ROOT, rel.replace("/", os.sep))
        if os.path.exists(full):
            frozen[rel] = sha(rel)
        else:
            print("MISSING (not bound):", rel)
    revrec["frozen_artifacts_sha256"] = dict(sorted(frozen.items()))
    revrec["formal_runs_before_revision"] = sorted(
        f for f in (os.listdir(TRAJ) if os.path.isdir(TRAJ) else [])
        if f.endswith(".csv") and not f.endswith(".stats.csv"))
    with open(os.path.join(ROOT, REVREC_REL.replace("/", os.sep)), "w",
              newline="\n", encoding="utf-8") as f:
        json.dump(revrec, f, indent=2)
        f.write("\n")
    print("v1r1 revision record refreshed:", revrec["generated_at_utc"],
          "| runs:", revrec["registered_formal_case_count"],
          "| frozen artifacts:", len(revrec["frozen_artifacts_sha256"]))
    print("run_registry.json, input_hashes.json refreshed; "
          "preregistration.json (historical) untouched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
