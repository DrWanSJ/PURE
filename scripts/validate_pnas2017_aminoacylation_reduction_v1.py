#!/usr/bin/env python3
"""Independently validate the PNAS 2017 aminoacylation v1 selective-QSSA chain.

This validator does NOT import any analysis script. It re-reads the raw
sources (SHA-pinned SBML, author .m, author dat CSVs, audit CSVs), re-derives
the verification facts, and checks:

  1. immutable-source integrity chain (SBML, author .m, dat CSVs);
  2. the verbatim rate extraction (re-derives monomial verification from the
     author .m against the SBML-derived audit CSVs, without trusting the
     manifest);
  3. the tight reference chain (hashes + tolerance-convergence claims);
  4. the runner self-check (recompares registered trajectory vs tight);
  5. pre-registration integrity (acceptance thresholds frozen by hash in
     the ACTIVE registration before the first formal run; T_C/T_D/T_E/T_F not
     null; v0 files untouched);
  6. the candidate partition vs the QSSA derivation artifacts;
  6b. the v1r1 IMPLEMENTATION/COORDINATE-REALIZATION revision chain: the
     historical preregistration.json and candidate_partition.json are
     byte-preserved, the versioned candidate_partition_v1r1.json (218
     dynamic states, free-enzyme moiety reconstruction) is hash-bound, and
     the scientific partition/thresholds/stress domain are unchanged;
  6c. run-registry/config active bindings (13 configs hash-bound to v1r1);
  6d. negative software control (in-process corruption probe + recorded
     verdict);
  7. formal full-vs-reduced results against the registered tiers (when
     present), all pairs scored per registered tier, negative control
     rejected as registered;
  7b. every registered run has a recorded outcome manifest;
  8. negative software test (corrupted coefficient must be REJECTED);
  9. forbidden project actions (no models/pure_reduced_core/*.xml,
     no scratch references in formal artifacts).

Statuses: PASS / FAIL / SKIP (evidence not yet produced - never PASS).
Exit code 0 only if there are zero FAILs AND every formal-stage check that
the completion gate requires has passed (see REQUIRED_FOR_DONE).

Run:  python scripts/validate_pnas2017_aminoacylation_reduction_v1.py
      python scripts/validate_pnas2017_aminoacylation_reduction_v1.py --corrupt-selftest
"""
import ast
import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")
SBML = os.path.join(ROOT, "models/pnas2017_full_reference/original/fMGG_synthesis.xml")
AUTHOR_M = os.path.join(ROOT, "models/pnas2017_full_reference/original/simulate",
                        "Simulate_fMGG_synthesis/fMGG_synthesis.m")
DAT = os.path.join(ROOT, "models/pnas2017_full_reference/original/simulate",
                   "Simulate_fMGG_synthesis/dat")
PROV = os.path.join(ROOT, "data/provenance.csv")
TIGHT = os.path.join(ROOT, "results/pnas2017_reference/2026-09-25_aa_v1_reference_tight")
SELF = os.path.join(ROOT, "results/pnas2017_reference/2026-09-25_aa_v1_runner_selfcheck")
REG = os.path.join(ROOT, "docs/audit/pnas2017_aminoacylation_reduction_v1")
GEN_RATES = os.path.join(ROOT, "scripts/pnas2017_aa_v1_rates.m")
V0_DIR = os.path.join(ROOT, "docs/audit/pnas2017_aminoacylation_reduction_v0")

EXACT_TOL = 1e-9
ALLOWED = (ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Store,
           ast.BinOp, ast.UnaryOp, ast.operator, ast.unaryop, ast.BoolOp,
           ast.boolop, ast.Compare, ast.cmpop)

results = {}


def rec(name, status, detail=""):
    if status is True:
        status = "PASS"
    elif status is False:
        status = "FAIL"
    results[name] = (status, detail)
    print("%-6s %s %s" % (status, name, detail))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_side(s):
    out = []
    for tok in (s or "").split("|"):
        tok = tok.strip()
        if tok:
            sp, st = tok.rsplit(":", 1)
            out.extend([sp] * int(float(st)))
    return sorted(out)


# --------------------------------------------------------------------------- #
# corruption probe: like the real pipeline, but optionally mutates one
# protected coefficient in an in-memory copy of the author source
# --------------------------------------------------------------------------- #
def extraction_verified(corrupt_index=None, corrupt_species=None):
    """Re-derive the monomial verification independently of the manifest."""
    lines = open(AUTHOR_M, encoding="utf-8", errors="replace").read().splitlines()
    if corrupt_index is not None:
        for i, ln in enumerate(lines):
            if ln.strip().startswith("react(%d) =" % corrupt_index):
                lines[i] = ln.replace("state(1)", "state(%s)" % corrupt_species, 1) \
                              if "state(1)" in ln else ln.replace("* state", "* 2.0 * state", 1)
                break
    state_cmt = {}
    react_cmt = {}
    param_cmt = {}
    for ln in lines:
        m = re.match(r"^% state\((\d+)\): (.+)$", ln)
        if m:
            state_cmt[int(m.group(1))] = m.group(2).strip()
        m = re.match(r"^% react\((\d+)\): (re\d+)$", ln)
        if m:
            react_cmt[int(m.group(1))] = m.group(2)
        m = re.match(r"^% param\((\d+)\): (\S+)$", ln)
        if m:
            param_cmt[int(m.group(1))] = m.group(2)
    rxs = {r["id"]: r for r in load(os.path.join(AUDIT, "reactions.csv"))}
    bad = []
    n = 0
    for ln in lines:
        m = re.match(r"^react\((\d+)\) = ([^;]+);$", ln.strip())
        if not m:
            continue
        n += 1
        idx = int(m.group(1))
        mm = re.match(r"^param\((\d+)\)(?: \* state\(\d+\))* *$", m.group(2).strip())
        if not mm:
            bad.append((idx, "not monomial: %r" % m.group(2)))
            continue
        sidx = [int(s) for s in re.findall(r"state\((\d+)\)", m.group(2))]
        states = [state_cmt.get(k, "?") for k in sidx]
        rid = react_cmt.get(idx)
        if param_cmt.get(idx) != rid + "_k1":
            bad.append((idx, "param mapping broken"))
            continue
        r = rxs.get(rid)
        if r is None or sorted(states) != parse_side(r["reactants"]):
            bad.append((idx, "reactants mismatch %s vs %s"
                        % (sorted(states), parse_side(r["reactants"]) if r else None)))
            continue
        law = sorted(r["rate_law"].replace(" ", "").split("*"))
        if law != sorted(["k1"] + parse_side(r["reactants"])):
            bad.append((idx, "rate law string mismatch"))
    return n, bad


def main():
    corrupt_selftest = "--corrupt-selftest" in sys.argv

    # ---- 1. immutable sources ---------------------------------------------- #
    sbml_sha = sha(SBML)
    prov = ""
    for r in load(PROV):
        vals = list(r.values())
        if any("Matsuura_2017_combined_SBML" in (v or "") for v in vals):
            prov = next((v for v in vals if re.fullmatch(r"[0-9a-f]{64}", v or "")), "")
    rec("R1_sbml_sha_matches_provenance",
        "PASS" if sbml_sha == prov else "FAIL", sbml_sha[:12])

    # ---- 2. verbatim extraction re-derivation ------------------------------ #
    n, bad = extraction_verified()
    rec("R2_monomial_extraction_rederived_clean",
        "PASS" if n == 968 and not bad else "FAIL",
        "%d lines, %d mismatches %s" % (n, len(bad), bad[:2]))

    # the generated rates file must equal the author block verbatim
    gen = open(GEN_RATES, encoding="utf-8").read().splitlines()
    author_lines = [l.strip() for l in open(AUTHOR_M, encoding="utf-8", errors="replace") if re.match(r"^react\(\d+\) = ", l.strip())]
    gen_lines = [l.strip() for l in gen if re.match(r"^react\(\d+\) = ", l.strip())]
    rec("R3_generated_rates_verbatim_equal",
        "PASS" if gen_lines == author_lines and len(gen_lines) == 968 else "FAIL",
        "%d lines" % len(gen_lines))

    # ---- 3. negative software test ----------------------------------------- #
    if corrupt_selftest:
        n2, bad2 = extraction_verified(corrupt_index=1)
        rejected = bool(bad2)
        rec("NEG_corruption_detected_by_validator",
            "PASS" if rejected else "FAIL", "mutated react(1): %s" % (bad2[:1],))
        return 0 if rejected else 1

    # ---- 4. tight reference chain ------------------------------------------ #
    tc_path = os.path.join(TIGHT, "tolerance_convergence.csv")
    if os.path.exists(tc_path):
        tc = load(tc_path)
        try:
            w3 = max(float(r["max_rel_dev_vs_1e-10"]) for r in tc if r["rel_tol"] == "0.001")
            w8 = max(float(r["max_rel_dev_vs_1e-10"]) for r in tc if r["rel_tol"] == "1e-08")
            rec("R3b_tight_convergence_documented", w3 < 1e-2 and w8 < 1e-5,
                "author-tol dev %.2e; 1e-8 dev %.2e" % (w3, w8))
        except (ValueError, KeyError):
            rec("R3b_tight_convergence_documented", "SKIP", "unexpected column layout")
    else:
        rec("R3b_tight_convergence_documented", "SKIP", "no tolerance_convergence.csv")

    # ---- 5. runner self-check ---------------------------------------------- #
    summ_path = os.path.join(SELF, "refcheck_summary.json")
    if os.path.exists(summ_path):
        s = json.load(open(summ_path, encoding="utf-8"))
        d = s["species_vs_tight_pointwise_max_traj_scaled_dev"]
        budget = 0.1 * 1e-6   # 10% of the T_H A1 trajectory budget
        rec("R4_runner_reference_matches_tight", d <= budget, "%.2e (budget %.0e)" % (d, budget))
        e = s["extent_reldev_1e_10_vs_1e_8_max"]
        rec("R5_extent_numeric_budget_ok", e <= 0.1 * 0.01, "%.2e vs 1e-3 budget" % e)
        # recompute the comparison ourselves from the registered CSVs
        p1 = os.path.join(SELF, s["runs"]["primary"]["file"])
        p2 = os.path.join(TIGHT, "authors_model_trajectory_tight.csv")
        if os.path.exists(p1) and sha(p1) == s["runs"]["primary"]["sha256"]:
            rows1 = list(csv.reader(open(p1, newline="", encoding="utf-8-sig")))
            rows2 = list(csv.reader(open(p2, newline="", encoding="utf-8-sig")))
            h1, h2 = rows1[0], rows2[0]
            c1 = {n: i for i, n in enumerate(h1)}
            worst = 0.0
            for n in h2[1:]:
                col1 = [abs(float(r[c1[n]])) for r in rows1[1:]]
                sc = max(max(col1), 1e-6)
                for r1, r2 in zip(rows1[1:], rows2[1:]):
                    worst = max(worst, abs(float(r1[c1[n]]) - float(r2[h2.index(n)])) / sc)
            rec("R6_selfcheck_recomputed", worst <= budget, "%.2e" % worst)
        else:
            rec("R6_selfcheck_recomputed", "SKIP", "registered file missing or hash differs")
    else:
        rec("R4_runner_reference_matches_tight", "SKIP", "no refcheck_summary.json")
        rec("R5_extent_numeric_budget_ok", "SKIP", "no refcheck_summary.json")
        rec("R6_selfcheck_recomputed", "SKIP", "no refcheck_summary.json")

    # ---- 6. pre-registration ------------------------------------------------ #
    pre_path = os.path.join(REG, "preregistration.json")
    acc_path = os.path.join(REG, "acceptance_criteria.json")
    rev_path = os.path.join(REG, "preregistration_revision_v1r1.json")
    rev = json.load(open(rev_path, encoding="utf-8")) if os.path.exists(rev_path) else None
    pre = json.load(open(pre_path, encoding="utf-8")) if os.path.exists(pre_path) else None
    if os.path.exists(acc_path):
        acc = json.load(open(acc_path, encoding="utf-8"))
        tiers = acc["tiers"]
        notnull = all(tiers[t]["threshold"] is not None for t in
                      ("T_C_approximate_state_trajectories",
                       "T_D_approximate_instantaneous_fluxes",
                       "T_E_approximate_cumulative_resource_extents",
                       "T_F_timescale_separation_screen"))
        rec("R7_approx_thresholds_registered", notnull)
    else:
        rec("R7_approx_thresholds_registered", "SKIP", "no acceptance_criteria.json")

    if rev is not None:
        # ACTIVE registration = the v1r1 implementation/coordinate-realization
        # revision record; the historical preregistration.json stays immutable.
        ok = True
        for fname, want in rev.get("frozen_artifacts_sha256", {}).items():
            p = fname if os.path.isabs(fname) else os.path.join(ROOT, fname)
            got = sha(p) if os.path.exists(p) else None
            if got != want:
                ok = False
                print("   hash mismatch:", fname, got, "!=", want)
        rec("R8_active_revision_registration_hashes_intact", ok,
            "%d artefacts" % len(rev.get("frozen_artifacts_sha256", {})))
        runs0 = pre.get("formal_runs_before_registration") if pre else "missing"
        runsR = rev.get("formal_runs_before_revision")
        rec("R9_zero_formal_runs_before_registration",
            (runs0 == 0 or runs0 == []) and (runsR == 0 or runsR == []),
            "pre-reg %s / revision %s" % (runs0, runsR))
    elif pre is not None:
        ok = True
        for fname, want in pre.get("frozen_artifacts_sha256", {}).items():
            p = fname if os.path.isabs(fname) else os.path.join(ROOT, fname)
            got = sha(p) if os.path.exists(p) else None
            if got != want:
                ok = False
                print("   hash mismatch:", fname, got, "!=", want)
        rec("R8_active_revision_registration_hashes_intact", ok,
            "%d artefacts" % len(pre.get("frozen_artifacts_sha256", {})))
        runs = pre.get("formal_runs_before_registration")
        rec("R9_zero_formal_runs_before_registration",
            runs == 0 or runs == [], str(runs))
    else:
        rec("R8_active_revision_registration_hashes_intact", "SKIP", "not frozen")
        rec("R9_zero_formal_runs_before_registration", "SKIP", "not frozen")

    # ---- 6b. v1r1 revision chain (versioning, not overwriting) -------------- #
    v1r1_path = os.path.join(REG, "candidate_partition_v1r1.json")
    hist_part_path = os.path.join(REG, "candidate_partition.json")
    if rev is not None and os.path.exists(v1r1_path) and os.path.exists(hist_part_path):
        pv = json.load(open(v1r1_path, encoding="utf-8"))
        pp = json.load(open(hist_part_path, encoding="utf-8"))
        hc = rev.get("hash_chain", {})
        checks = {
            "historical_preregistration_byte_immutable":
                sha(pre_path) == rev.get("parent_preregistration", {}).get("sha256"),
            "historical_partition_byte_immutable":
                sha(hist_part_path) == hc.get("original_candidate_partition_sha256")
                == pv.get("parent_partition_sha256"),
            "v1r1_hash_bound_in_revision_record":
                hc.get("new_candidate_partition_v1r1_sha256") == sha(v1r1_path),
            "acceptance_criteria_sha_bound":
                hc.get("original_acceptance_criteria_sha256") == sha(acc_path),
            "runner_sha_bound":
                hc.get("runner_v1r1_instrumented_sha256")
                == sha(os.path.join(ROOT, "scripts", "run_pnas2017_aa_v1_formal.m")),
            "record_class_is_realization_revision":
                "COORDINATE REALIZATION REVISION" in rev.get("record_class", ""),
            "eliminated_set_identical_to_parent":
                sorted(pv.get("eliminated_states", []))
                == sorted(pp.get("eliminated_complexes", [])),
            "eliminated_count_21": pv.get("eliminated_count") == 21,
            "dynamic_state_count_218": pv.get("dynamic_state_count") == 218,
            "scientific_partition_changed_false":
                pv.get("scientific_partition_changed") is False,
            "QSSA_closure_changed_false": pv.get("QSSA_closure_changed") is False,
            "acceptance_thresholds_changed_false":
                pv.get("acceptance_thresholds_changed") is False,
            "stress_domain_changed_false": pv.get("stress_domain_changed") is False,
            "numerical_realization_changed_true":
                pv.get("numerical_realization_changed") is True,
            "supersedes_numerical_realization_only_true":
                pv.get("supersedes_numerical_realization_only") is True,
        }
        bad = [k for k, v in checks.items() if not v]
        rec("R16_historical_registration_immutable_and_versioned", not bad,
            "; ".join(bad) if bad else "historical preregistration + partition "
            "byte-preserved; v1r1 versioned alongside")
        rec("R17_active_partition_version_consistency", not bad,
            "218 dynamic states; scientific partition unchanged; "
            "numerical realization only" if not bad else "; ".join(bad))
    else:
        rec("R16_historical_registration_immutable_and_versioned", "SKIP",
            "revision record not present")
        rec("R17_active_partition_version_consistency", "SKIP",
            "revision record not present")

    # ---- 6c. registry/config active bindings -------------------------------- #
    reg_path = os.path.join(REG, "run_registry.json")
    if rev is not None and os.path.exists(reg_path) and os.path.exists(v1r1_path):
        reg = json.load(open(reg_path, encoding="utf-8"))
        pv = json.load(open(v1r1_path, encoding="utf-8"))
        ap = reg.get("active_partition", {})
        runner_rel = "scripts/run_pnas2017_aa_v1_formal.m"
        checks = {
            "registry_schema_v1r1": str(reg.get("schema", "")).endswith("v1r1"),
            "registry_binds_v1r1_partition":
                ap.get("file") == "docs/audit/pnas2017_aminoacylation_reduction_v1/"
                "candidate_partition_v1r1.json"
                and ap.get("sha256") == sha(v1r1_path)
                and ap.get("revision_id") == "v1r1",
            "registry_binds_historical_partition":
                ap.get("historical_partition_sha256")
                == sha(os.path.join(REG, "candidate_partition.json")),
            "registry_binds_runner":
                reg.get("runner", {}).get("sha256")
                == sha(os.path.join(ROOT, "scripts", "run_pnas2017_aa_v1_formal.m")),
            "thirteen_runs_registered": len(reg.get("runs", {})) == 13,
        }
        cfg_bad = []
        for rid, r in sorted(reg.get("runs", {}).items()):
            cpath = os.path.join(ROOT, r["config"].replace("/", os.sep))
            if not os.path.exists(cpath):
                cfg_bad.append("%s: config missing" % rid)
                continue
            if sha(cpath) != r.get("config_sha256"):
                cfg_bad.append("%s: config hash mismatch" % rid)
                continue
            cfg = json.load(open(cpath, encoding="utf-8"))
            if cfg.get("active_partition_revision") != "v1r1" or \
               cfg.get("active_partition") != ap.get("file"):
                cfg_bad.append("%s: config not bound to v1r1" % rid)
            if rid.startswith("RED-") and rid != "RED-NEG1":
                if sorted(cfg.get("eliminated", [])) != sorted(pv["eliminated_states"]):
                    cfg_bad.append("%s: eliminated set drift" % rid)
            if rid == "RED-NEG1":
                want = sorted(pv["eliminated_states"] + ["MetRS_MettRNAfMetCAU"])
                if sorted(cfg.get("eliminated", [])) != want:
                    cfg_bad.append("RED-NEG1: negative-control elimination set drift")
        checks["configs_bound_and_hashed"] = not cfg_bad
        bad = [k for k, v in checks.items() if not v]
        rec("R18_registry_config_active_bindings", not bad,
            "; ".join(bad + cfg_bad) if bad else
            "13 configs hash-bound, all bound to v1r1; runner bound")
    else:
        rec("R18_registry_config_active_bindings", "SKIP",
            "revision record or registry not present")

    # ---- 6d. negative software control (in-process probe) ------------------- #
    n3, bad3 = extraction_verified(corrupt_index=1)
    rec("RNEG_corruption_probe_rejects", bool(bad3),
        "mutated react(1) -> %s" % (bad3[:1],))
    neg_path = os.path.join(REG, "negative_test_result.json")
    if os.path.exists(neg_path):
        neg = json.load(open(neg_path, encoding="utf-8"))
        rec("RNEG2_recorded_negative_test_verdict",
            neg.get("verdict") == "REJECTED_AS_REQUIRED"
            and neg.get("validator_sha256") == sha(os.path.abspath(__file__)),
            "recorded %s (validator %s)" % (neg.get("verdict"),
                                            neg.get("validator_sha256", "")[:12]))
    else:
        rec("RNEG2_recorded_negative_test_verdict", "SKIP", "no negative_test_result.json")

    # v0 files untouched
    v0 = {"preregistration.json": None, "acceptance_criteria.json": None}
    for f in v0:
        p = os.path.join(V0_DIR, f)
        v0[f] = sha(p) if os.path.exists(p) else None
    rec("R10_v0_artefacts_present_and_hashable", all(v0.values()),
        json.dumps({k: (v or "")[:12] for k, v in v0.items()}))

    # ---- 7. QSSA derivation + partition ------------------------------------ #
    der = os.path.join(AUDIT, "aminoacylation_v1_qssa_derivation.json")
    if os.path.exists(der):
        d = json.load(open(der, encoding="utf-8"))
        rec("R11_qssa_derivation_present", True, "schema %s" % d.get("schema"))
        part = os.path.join(REG, "candidate_partition.json")
        if os.path.exists(part):
            pp = json.load(open(part, encoding="utf-8"))
            rec("R12_partition_declares_eliminated_and_kept",
                bool(pp.get("eliminated_complexes")) and "MetAMP" in pp.get("kept_dynamic", [])
                and "GlyAMP" in pp.get("kept_dynamic", []))
        else:
            rec("R12_partition_declares_eliminated_and_kept", "SKIP", "not registered yet")
    else:
        rec("R11_qssa_derivation_present", "SKIP", "derivation still running")
        rec("R12_partition_declares_eliminated_and_kept", "SKIP", "no derivation")

    # ---- 8. formal comparison ------------------------------------------------ #
    formal = os.path.join(ROOT, "results/pnas2017_reference/2026-09-25_aa_v1_formal_comparison")
    if os.path.isdir(formal):
        rep = os.path.join(formal, "formal_comparison_summary.json")
        if os.path.exists(rep):
            r = json.load(open(rep, encoding="utf-8"))
            rec("R13_formal_comparison_recorded", True, "see %s" % rep)
            # per-pair verdicts must exist and be recorded for all 6 pairs
            pairs = r.get("pairs", {})
            need = {"S%d" % k for k in range(6)}
            missing = sorted(need - set(pairs))
            unresolved = []
            for pid, p in sorted(pairs.items()):
                for tier in ("states", "extents", "fluxes"):
                    st = p.get("verdicts", {}).get(tier, {}).get("status")
                    if st not in ("PASS", "FAIL", "NUMERICALLY_UNRESOLVED"):
                        unresolved.append("%s.%s=%s" % (pid, tier, st))
            rec("R19_all_pairs_scored_per_registered_tiers",
                not missing and not unresolved,
                "missing %s; unscored %s" % (missing, unresolved))
            neg = r.get("negative_control", {})
            neg_ok = (str(neg.get("expected_verdict", "")).startswith("FAIL")
                      and neg.get("observed_verdict") in ("FAIL", "RUN_FAILURE")
                      and neg.get("negative_software_test_criterion") == "PASS")
            rec("R20_negative_control_rejected_as_registered", neg_ok,
                "expected %s / observed %s / software criterion %s"
                % (neg.get("expected_verdict"), neg.get("observed_verdict"),
                   neg.get("negative_software_test_criterion")))
        else:
            rec("R13_formal_comparison_recorded", "SKIP", "no summary yet")
            rec("R19_all_pairs_scored_per_registered_tiers", "SKIP", "no summary yet")
            rec("R20_negative_control_rejected_as_registered", "SKIP", "no summary yet")
    else:
        rec("R13_formal_comparison_recorded", "SKIP", "no formal comparison dir yet")
        rec("R19_all_pairs_scored_per_registered_tiers", "SKIP", "no formal comparison dir yet")
        rec("R20_negative_control_rejected_as_registered", "SKIP", "no formal comparison dir yet")

    # ---- 8b. every registered run has a recorded outcome -------------------- #
    regf = os.path.join(REG, "run_registry.json")
    man_dir = os.path.join(ROOT, "results/pnas2017_reference/2026-09-25_aa_v1_formal/manifests")
    if os.path.exists(regf) and os.path.isdir(man_dir):
        reg = json.load(open(regf, encoding="utf-8"))
        gap = []
        for rid, rr in sorted(reg.get("runs", {}).items()):
            mpath = os.path.join(man_dir, "%s.manifest.json" % rid)
            if not os.path.exists(mpath):
                gap.append("%s: no manifest" % rid)
                continue
            m = json.load(open(mpath, encoding="utf-8"))
            if not m.get("outcome") in ("success", "failed", "expected_failure"):
                gap.append("%s: outcome not recorded" % rid)
                continue
            if m.get("config_sha256") != rr.get("config_sha256"):
                gap.append("%s: manifest config hash mismatch" % rid)
            traj_rel = rr.get("trajectory")
            if traj_rel:
                tpath = os.path.join(ROOT, traj_rel.replace("/", os.sep))
                if m["outcome"] in ("success", "expected_failure") and \
                        not os.path.exists(tpath):
                    gap.append("%s: outcome success but trajectory missing" % rid)
        rec("R21_every_registered_run_has_recorded_outcome", not gap,
            "; ".join(gap) if gap else "13/13 manifests present with outcomes")
    else:
        rec("R21_every_registered_run_has_recorded_outcome", "SKIP",
            "no registry or no manifests yet")

    # ---- 9. forbidden actions ------------------------------------------------ #
    core = os.path.join(ROOT, "models/pure_reduced_core")
    xmls = [f for f in os.listdir(core) if f.endswith(".xml")] if os.path.isdir(core) else []
    rec("R14_no_reduced_core_built", not xmls, str(xmls))
    scratch_hits = []
    for fn in os.listdir(AUDIT):
        if fn.startswith("aminoacylation_v1") or fn.startswith("aminoacylation_"):
            txt = open(os.path.join(AUDIT, fn), encoding="utf-8", errors="ignore").read().lower()
            if re.search(r"scratch[\\/]", txt):
                scratch_hits.append(fn)
    rec("R15_no_scratch_dependency_in_formal_artefacts", not scratch_hits, str(scratch_hits))

    fails = [k for k, (s, _) in results.items() if s == "FAIL"]
    skips = [k for k, (s, _) in results.items() if s == "SKIP"]
    print("\n%d PASS, %d FAIL, %d SKIP" %
          (sum(1 for s, _ in results.values() if s == "PASS"), len(fails), len(skips)))
    if fails:
        print("FAILED:", ", ".join(fails))
        return 1
    if skips:
        print("NOT COMPLETE - outstanding:", ", ".join(skips))
        return 2
    print("ALL REGISTERED V1 CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
