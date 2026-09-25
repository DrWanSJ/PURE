#!/usr/bin/env python3
"""Freeze the v1r2 preregistration revision (Phase 7) BEFORE any formal run.

v1r2 = moiety-consistent initialization map revision.  Per the user
execution instruction of 2026-09-26:

  * the 21-state eliminated set, the closure equations, the acceptance
    thresholds, the stress domain and the source model are UNCHANGED;
  * only the initialization realization changes (consistentStartV1r2 with
    the frozen B_init debit matrix + the P2 fast-layer cumulative offsets);
  * the FULL-S0..S5 reference runs are REUSED byte-for-byte from the v1r1
    formal cycle: their configs are copied unchanged (same config sha256,
    same model/source/solver settings) and the validator explicitly
    verifies the equivalence (R30/R33 class checks);
  * every RED run is new;
  * formal_runs_before_v1r2_registration = [] (no formal v1r2 run may
    exist before this freeze).
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(ROOT, "docs", "audit", "pnas2017_aminoacylation_reduction_v1")
V1_FORMAL = os.path.join(ROOT, "results", "pnas2017_reference", "2026-09-25_aa_v1_formal")
V1R2_FORMAL = os.path.join(ROOT, "results", "pnas2017_reference", "2026-09-26_aa_v1r2_formal")
CFGS = os.path.join(V1R2_FORMAL, "configs")
SCR = os.path.join(ROOT, "scratch", "v1r2")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def sha_rel(rel):
    return sha(os.path.join(ROOT, rel.replace("/", os.sep)))


def main():
    part = json.load(open(os.path.join(AUD, "candidate_partition_v1r1.json")))
    binit = json.load(open(os.path.join(AUD, "binit_v1r2.json")))
    cumdefs = json.load(open(os.path.join(AUD, "cumdefs.json")))["cumdefs"]
    accept = json.load(open(os.path.join(AUD, "acceptance_criteria.json")))
    implrev = json.load(open(os.path.join(AUD, "implementation_revision_v1r2.json")))

    # ---- consistency gate -------------------------------------------------
    assert part["eliminated_count"] == 21
    eliminated = sorted(part["eliminated_states"])
    assert implrev["scientific_partition_changed"] is False
    assert implrev["eliminated_state_set_changed"] is False
    assert implrev["closure_equations_changed"] is False
    assert implrev["acceptance_thresholds_changed"] is False
    assert implrev["stress_domain_changed"] is False
    assert implrev["initialization_map_changed"] is True
    runner_sha = sha_rel("scripts/run_pnas2017_aa_v1_formal.m")
    binit_sha = sha(os.path.join(AUD, "binit_v1r2.json"))

    # P2 layer diagnostics (initialization-only, already executed)
    layer_summaries = {}
    for cid in ["S0", "S1", "S2", "S3", "S4", "S5"]:
        p = os.path.join(SCR, "fastlayer-%s_summary.json" % cid)
        s = json.load(open(p))
        layer_summaries[cid] = {
            "t_layer": s["t_layer"],
            "exit_criterion": s["exit_criterion"],
            "scaled_G_at_exit": s["scaled_G_at_exit"],
            "branch_check_rel_diff": s["branch_check_rel_diff"],
            "extents_at_exit": s["extents_at_exit"],
            "csv_sha256": sha(os.path.join(SCR, "fastlayer-%s.csv" % cid)),
            "summary_sha256": sha(p),
        }

    # debit matrix per free pool
    debits = {}
    for row, info in binit["debit_matrix"].items():
        debits.setdefault(info["free_pool"], {})
        for cx, c in info["coefficients"].items():
            debits[info["free_pool"]][cx] = float(c)

    conds = {
        "S0": ({}, "reference condition, unmodified author initial values"),
        "S1": ({"ATP": 0.1}, "ATP x0.1"),
        "S2": ({"tRNAfMetCAU": 0.1, "tRNAGlyGCC": 0.1}, "both tRNAs x0.1"),
        "S3": ({"MetRS": 10.0, "GlyRS": 10.0}, "both enzymes x10"),
        "S4": ({"MetRS": 0.1, "GlyRS": 0.1}, "both enzymes x0.1"),
        "S5": ({"CP": 0.1}, "CP x0.1, energy system dynamic"),
    }
    reg = json.dumps(accept.get("stress_conditions_one_at_a_time", accept),
                     sort_keys=True)
    for cid in conds:
        assert cid in reg, "condition %s not registered" % cid

    os.makedirs(CFGS, exist_ok=True)
    os.makedirs(os.path.join(V1R2_FORMAL, 'trajectories'), exist_ok=True)
    os.makedirs(os.path.join(V1R2_FORMAL, 'logs'), exist_ok=True)
    traj_rel = "results/pnas2017_reference/2026-09-26_aa_v1r2_formal/trajectories"

    cfg_paths = {}
    # FULL configs: byte-for-byte copies of the v1r1 formal configs (reuse)
    for cid in conds:
        src = os.path.join(V1_FORMAL, "configs", "FULL-%s.json" % cid)
        dst = os.path.join(CFGS, "FULL-%s.json" % cid)
        shutil.copyfile(src, dst)
        assert sha(src) == sha(dst)
        cfg_paths["FULL-%s" % cid] = (
            "results/pnas2017_reference/2026-09-25_aa_v1_formal/configs/FULL-%s.json" % cid)

    # RED configs: new, v1r2 initializer with frozen debits + P2 offsets
    for cid, (scale, desc) in conds.items():
        ext = layer_summaries[cid]["extents_at_exit"]
        assert len(ext) == len(cumdefs)
        cfg = {
            "mode": "reduced",
            "initializer": "v1r2",
            "init_debits": debits,
            "init_extents_offset": ext,
            "reltol": 1e-10,
            "abstol": 1e-14,
            "grid": [1e-4, 1000.0, 200],
            "x0_scale": scale,
            "outfile": (os.path.join(V1R2_FORMAL, "trajectories",
                                     "RED-v1r2-%s.csv" % cid)).replace("\\", "/"),
            "stats": True,
            "cumdefs": cumdefs,
            "condition_description": desc,
            "active_partition": "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition_v1r1.json",
            "active_partition_revision": "v1r1",
            "initialization_revision": "v1r2",
            "binit_artifact": "docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2.json",
            "binit_sha256": binit_sha,
            "p2_layer_summary_sha256": layer_summaries[cid]["summary_sha256"],
        }
        cfg["eliminated"] = eliminated
        p = os.path.join(CFGS, "RED-v1r2-%s.json" % cid)
        with open(p, "w", newline="\n", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
            f.write("\n")
        cfg_paths["RED-v1r2-%s" % cid] = (
            "results/pnas2017_reference/2026-09-26_aa_v1r2_formal/configs/RED-v1r2-%s.json" % cid)

    # negative control: v1r2 initializer with the illegal partition
    neg_cfg = {
        "mode": "reduced",
        "initializer": "v1r2",
        "init_debits": debits,
        "init_extents_offset": layer_summaries["S0"]["extents_at_exit"],
        "reltol": 1e-10,
        "abstol": 1e-14,
        "grid": [1e-4, 1000.0, 200],
        "x0_scale": {},
        "outfile": (os.path.join(V1R2_FORMAL, "trajectories",
                                 "RED-v1r2-NEG1.csv")).replace("\\", "/"),
        "stats": True,
        "cumdefs": cumdefs,
        "condition_description": ("negative control: one evidence-kept complex "
                                  "illegally eliminated under the v1r2 "
                                  "initializer; FAIL verdict expected"),
        "active_partition": "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition_v1r1.json",
        "active_partition_revision": "v1r1",
        "initialization_revision": "v1r2",
        "eliminated": sorted(eliminated + ["MetRS_MettRNAfMetCAU"]),
    }
    p = os.path.join(CFGS, "RED-v1r2-NEG1.json")
    with open(p, "w", newline="\n", encoding="utf-8") as f:
        json.dump(neg_cfg, f, indent=2)
        f.write("\n")
    cfg_paths["RED-v1r2-NEG1"] = (
        "results/pnas2017_reference/2026-09-26_aa_v1r2_formal/configs/RED-v1r2-NEG1.json")

    # ---- run registry ------------------------------------------------------
    v1_reg = json.load(open(os.path.join(AUD, "run_registry.json")))
    registry = {
        "schema": "pnas2017_aa_v1_run_registry/v1r2",
        "binding": "local SHA-256 config binding; executor is "
                   "run_pnas2017_aa_v1_formal.m with the unmodified author "
                   "model directory; RED runs use the v1r2 initializer",
        "active_partition": {
            "file": "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition_v1r1.json",
            "sha256": sha_rel("docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition_v1r1.json"),
            "revision_id": "v1r1",
            "initialization_revision": "v1r2",
        },
        "runner": {"file": "scripts/run_pnas2017_aa_v1_formal.m",
                   "sha256": runner_sha},
        "binit": {"file": "docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2.json",
                  "sha256": binit_sha},
        "full_run_reuse": {
            "policy": ("FULL-S0..S5 reference trajectories are reused "
                       "byte-for-byte from the v1r1 formal cycle because the "
                       "v1r2 revision changes no FULL-side input: the configs "
                       "are byte-identical copies (sha256 equality asserted "
                       "at freeze), the model/source/solver settings are "
                       "identical, and validator check R30 verifies the "
                       "equivalence against the v1r1 registry"),
            "v1_formal_registry_sha256": v1_reg and sha(os.path.join(AUD, "run_registry.json")),
            "reused_runs": {cid: {
                "config_sha256": sha(os.path.join(V1_FORMAL, "configs", "FULL-%s.json" % cid)),
                "trajectory": "results/pnas2017_reference/2026-09-25_aa_v1_formal/trajectories/FULL-%s.csv" % cid,
                "trajectory_sha256": sha(os.path.join(
                    V1_FORMAL, "trajectories", "FULL-%s.csv" % cid)),
            } for cid in conds},
        },
        "p2_fast_layer_diagnostics": layer_summaries,
        "runs": {},
    }
    for runid, rel in sorted(cfg_paths.items()):
        entry = {
            "config": rel,
            "config_sha256": sha(os.path.join(ROOT, rel.replace("/", os.sep))),
            "status": "planned",
        }
        if runid.startswith("FULL"):
            entry["trajectory"] = ("results/pnas2017_reference/2026-09-25_aa_v1_formal/"
                                   "trajectories/%s.csv" % runid)
            entry["status"] = "reused_from_v1r1_byte_identical_config"
        else:
            entry["trajectory"] = "%s/%s.csv" % (traj_rel, runid)
        if runid.endswith("NEG1"):
            entry["expected_verdict"] = "FAIL (pipeline negative control)"
        registry["runs"][runid] = entry

    reg_path = os.path.join(AUD, "run_registry_v1r2.json")
    with open(reg_path, "w", newline="\n", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
        f.write("\n")

    # ---- preregistration revision record -----------------------------------
    branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    head = subprocess.run(["git", "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    rec = {
        "schema": "pnas2017_aa_v1_preregistration_revision/v1",
        "revision_id": "v1r2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "record_class": "IMPLEMENTATION / INITIALIZATION-MAP REVISION -- NOT a new scientific preregistration",
        "binding_statement": ("Local SHA-256 hash-binding revision record created BEFORE "
                              "any formal v1r2 full-vs-reduced comparison. The v1r1 "
                              "failure evidence chain (candidate_partition_v1r1.json, "
                              "preregistration_revision_v1r1.json, formal runs, comparison, "
                              "formal_failure_classification_v1r1.md) remains historical, "
                              "frozen and byte-for-byte unchanged."),
        "authorization_source": ("user execution instruction of 2026-09-26 (Phase 1: "
                                 "'The next task is to construct, verify, and formally "
                                 "validate a MOIETY-CONSISTENT INITIALIZATION MAP')"),
        "parent_preregistration": {
            "file": "docs/audit/pnas2017_aminoacylation_reduction_v1/preregistration_revision_v1r1.json",
            "sha256": sha_rel("docs/audit/pnas2017_aminoacylation_reduction_v1/preregistration_revision_v1r1.json"),
            "status": "HISTORICAL AND IMMUTABLE",
            "formal_runs_completed_before_this_revision": 13,
        },
        "hash_chain": {
            "implementation_revision_v1r2_sha256": sha_rel("docs/audit/pnas2017_aminoacylation_reduction_v1/implementation_revision_v1r2.json"),
            "binit_v1r2_sha256": binit_sha,
            "binit_matrix_csv_sha256": sha_rel("docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv"),
            "candidate_partition_v1r1_sha256": sha_rel("docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition_v1r1.json"),
            "acceptance_criteria_sha256": sha_rel("docs/audit/pnas2017_aminoacylation_reduction_v1/acceptance_criteria.json"),
            "cumdefs_sha256": sha_rel("docs/audit/pnas2017_aminoacylation_reduction_v1/cumdefs.json"),
            "runner_v1r2_sha256": runner_sha,
            "runner_v1r1_instrumented_sha256": "eb4ba2c49d41d8014cc6063473de796709f76ef3e175391ac9ea25c639016085",
            "runner_v1r2_change_note": ("adds the config-selected v1r2 initializer "
                                        "(consistentStartV1r2: joint 21-dim closure+inventory "
                                        "Newton with the frozen debit matrix), the "
                                        "init_extents_offset seeding, the x0_override test "
                                        "hook, and the projected-initial-state artifact dump; "
                                        "the v1r1 code path (initializer absent -> v1r1) is "
                                        "byte-identical in its decision logic"),
            "fastlayer_driver_v1r2_sha256": sha_rel("scripts/run_pnas2017_aa_v1r2_fastlayer.m"),
            "initializer_test_suite_v1r2_sha256": sha_rel("scripts/test_pnas2017_aa_v1r2_initializer.m"),
            "initializer_validator_v1r2_sha256": sha_rel("scripts/validate_pnas2017_aa_v1r2_initializer.py"),
            "p1p2_comparison_sha256": sha_rel("scripts/compare_pnas2017_aa_v1r2_p1p2.py"),
            "source_sbml_fMGG_synthesis_xml_sha256": sha_rel("models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
            "author_parameters_sha256": sha_rel("models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv"),
            "author_initial_values_sha256": sha_rel("models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv"),
            "author_reactions_sha256": sha_rel("models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_reactions.csv"),
            "author_model_m_sha256": sha_rel("models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/fMGG_synthesis.m"),
            "initializer_tests_v1r2_sha256": sha(os.path.join(AUD, "initializer_tests_v1r2.json")),
        },
        "what_changed_in_this_revision": {
            "changed": [
                "RED initial-state protocol: consistentStartV1r2 (moiety-consistent joint "
                "projection with the frozen B_init debit matrix; free AMP held at its "
                "author value 0, the registered additional condition)",
                "RED cumulative counters seeded with the registered P2 fast-layer extents "
                "at the 5*tau_fast layer-window exit, per stress condition",
                "FULL runs reused byte-for-byte from v1r1 (identical configs, verified)",
            ],
            "unchanged": [
                "21-state eliminated set", "closure equations (author RHS rows)",
                "7 kept-dynamic complexes + free MetAMP/GlyAMP mandate",
                "enzyme-moiety reconstruction (v1r1)",
                "acceptance thresholds T_A..T_H and the QSSA scaled residual 1e-10",
                "stress conditions S0..S5", "cumulative-extent definitions",
                "solver tolerances RelTol 1e-10 / AbsTol 1e-14, output grid",
                "source SBML, author .m, author CSVs",
            ],
        },
        "formal_runs_before_v1r2_registration": [],
        "registered_formal_case_count": len(registry["runs"]),
        "registered_formal_cases": sorted(registry["runs"]),
        "run_registry_binding": {
            "run_registry_file": "docs/audit/pnas2017_aminoacylation_reduction_v1/run_registry_v1r2.json",
            "run_registry_sha256": sha(reg_path),
        },
        "git_context_informational": {"branch": branch, "head_before_freeze": head},
        "prohibitions_ack": [
            "no edit of the v1r1 evidence chain",
            "no relaxation of any acceptance threshold",
            "no change to the 21-state eliminated set",
            "no change to stress conditions S0-S5",
            "no clipping / projection / refit",
            "raw PNAS sources untouched",
        ],
        "frozen_artifacts_sha256": {},
    }
    frozen = {}
    for rel in [
        "docs/audit/pnas2017_aminoacylation_reduction_v1/acceptance_criteria.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition_v1r1.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/cumdefs.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/implementation_revision_v1r2.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/formal_failure_classification_v1r1.md",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/preregistration_revision_v1r1.json",
        "docs/audit/pnas2017_aminoacylation_reduction_v1/run_registry.json",
        "scripts/run_pnas2017_aa_v1_formal.m",
        "scripts/run_pnas2017_aa_v1r2_fastlayer.m",
        "scripts/test_pnas2017_aa_v1r2_initializer.m",
        "scripts/validate_pnas2017_aa_v1r2_initializer.py",
        "scripts/compare_pnas2017_aa_v1r2_p1p2.py",
        "scripts/build_pnas2017_aa_v1r2_binit.py",
    ]:
        frozen[rel] = sha_rel(rel)
    for cid in conds:
        frozen["results/pnas2017_reference/2026-09-26_aa_v1r2_formal/configs/RED-v1r2-%s.json" % cid] = \
            sha(os.path.join(CFGS, "RED-v1r2-%s.json" % cid))
        frozen["results/pnas2017_reference/2026-09-26_aa_v1r2_formal/configs/FULL-%s.json" % cid] = \
            sha(os.path.join(CFGS, "FULL-%s.json" % cid))
        frozen["scratch/v1r2/fastlayer-%s.csv" % cid] = \
            sha(os.path.join(SCR, "fastlayer-%s.csv" % cid))
        frozen["scratch/v1r2/fastlayer-%s_summary.json" % cid] = \
            sha(os.path.join(SCR, "fastlayer-%s_summary.json" % cid))
    frozen["results/pnas2017_reference/2026-09-26_aa_v1r2_formal/configs/RED-v1r2-NEG1.json"] = \
        sha(os.path.join(CFGS, "RED-v1r2-NEG1.json"))
    rec["frozen_artifacts_sha256"] = dict(sorted(frozen.items()))

    rec_path = os.path.join(AUD, "preregistration_revision_v1r2.json")
    with open(rec_path, "w", newline="\n", encoding="utf-8") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    print("v1r2 preregistration frozen:", rec["generated_at_utc"])
    print("registry:", reg_path, "cases:", rec["registered_formal_case_count"])
    print("formal_runs_before_v1r2_registration = []")
    return 0


if __name__ == "__main__":
    sys.exit(main())
