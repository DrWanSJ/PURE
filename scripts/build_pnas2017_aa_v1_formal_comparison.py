#!/usr/bin/env python3
"""Build the v1r1 formal full-vs-reduced comparison (Phases 5-8).

For each registered stress condition Sk (S0..S5) the FULL-Sk and RED-Sk
trajectories are compared under the frozen acceptance_criteria.json tiers
using scripts/compare_pnas2017_aa_v1_reduced.py and the registered scope:

  T_C  state trajectories          (56 declared observables, E_inf <= 0.01)
  T_D  instantaneous process fluxes (12 registered gross fluxes, <= 0.05)
  T_E  cumulative resource extents  (12 registered complete curves, <= 0.01)
  T_G  conservation ledgers         (residual <= 1e-8, with the frozen
       numeric_uncertainty_budget rule: a ledger the FULL reference itself
       does not resolve to 1e-8 at the registered tolerances is scored
       NUMERICALLY_UNRESOLVED, not FAIL)

RED-NEG1 (one evidence-kept complex illegally eliminated) is compared
against FULL-S0 and must be REJECTED (comparison verdict FAIL, or the run
itself failed under the closure guards) - a software negative control.

Every tiered metric is reported separately per observable: max absolute
error, registered scaled error, acceptance threshold, worst-error time,
PASS/FAIL/NUMERICALLY_UNRESOLVED, and a floor-materiality flag when the
registered scale floor (not the signal) dominates the normalization.

Outputs (results/pnas2017_reference/2026-09-25_aa_v1_formal_comparison/):
  metrics-<CASE>.json       raw compare output per case (incl. NEG1)
  formal_comparison_summary.json   the aggregate record read by the
                            independent validator (R13/R19/R20)
"""
import csv
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMAL = os.path.join(ROOT, "results", "pnas2017_reference", "2026-09-25_aa_v1_formal")
TRAJ = os.path.join(FORMAL, "trajectories")
MANS = os.path.join(FORMAL, "manifests")
OUTDIR = os.path.join(ROOT, "results", "pnas2017_reference",
                      "2026-09-25_aa_v1_formal_comparison")
REG = os.path.join(ROOT, "docs", "audit", "pnas2017_aminoacylation_reduction_v1")
SCOPE = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit",
                     "aminoacylation_v1_comparison_scope.json")
TAU_FAST = 0.009825
FLOOR_CONC = 1e-6


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_cols(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    idx = {n: i for i, n in enumerate(header)}
    out = []
    for r in rows[1:]:
        out.append({n: float(r[idx[n]]) for n in header})
    return out


def max_abs_error(full, red, name):
    worst = 0.0
    at = None
    for rf, rr in zip(full, red):
        d = abs(rr[name] - rf[name])
        if d > worst:
            worst, at = d, rf["time"]
    return worst, at


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    scope = json.load(open(SCOPE, encoding="utf-8"))
    reg = json.load(open(os.path.join(REG, "run_registry.json"), encoding="utf-8"))
    hashes = json.load(open(os.path.join(REG, "input_hashes.json"), encoding="utf-8"))
    acc = json.load(open(os.path.join(REG, "acceptance_criteria.json"), encoding="utf-8"))
    tiers = acc["tiers"]

    pairs = []
    neg = {}
    cases = ["S0", "S1", "S2", "S3", "S4", "S5"]
    for cid in cases:
        pairs.append(compare_pair(cid, scope, reg, hashes, tiers))
    neg = compare_negative(scope, reg, hashes, tiers)

    summary = {
        "schema": "pnas2017_aa_v1_formal_comparison/v1r1",
        "generated_by": "scripts/build_pnas2017_aa_v1_formal_comparison.py",
        "compare_instrument": "scripts/compare_pnas2017_aa_v1_reduced.py",
        "scope": "models/pnas2017_full_reference/audit/aminoacylation_v1_comparison_scope.json",
        "scope_sha256": sha(SCOPE),
        "active_partition_revision": "v1r1",
        "active_partition_sha256": sha(os.path.join(
            REG, "candidate_partition_v1r1.json")),
        "historical_partition_sha256": sha(os.path.join(
            REG, "candidate_partition.json")),
        "runner_sha256": sha(os.path.join(ROOT, "scripts",
                                          "run_pnas2017_aa_v1_formal.m")),
        "source_sbml_sha256": hashes.get(
            "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
        "author_parameters_sha256": hashes.get(
            "models/pnas2017_full_reference/original/simulate/"
            "Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv"),
        "author_initial_values_sha256": hashes.get(
            "models/pnas2017_full_reference/original/simulate/"
            "Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv"),
        "acceptance_criteria_sha256": sha(os.path.join(REG,
                                                       "acceptance_criteria.json")),
        "solver": {"engine": "MATLAB R2025b ode15s", "reltol": 1e-10,
                   "abstol": 1e-14, "grid": [1e-4, 1000.0, 200]},
        "tau_fast_for_layer_window_s": TAU_FAST,
        "numerical_budget": numerical_budget(acc),
        "pairs": {p["condition"]: p for p in pairs},
        "negative_control": neg,
        "scoped_classification": classify(pairs, neg),
    }
    out = os.path.join(OUTDIR, "formal_comparison_summary.json")
    with open(out, "w", newline="\n", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print("summary written:", out)
    for p in pairs:
        v = p["verdicts"]
        print("%-4s states=%-8s extents=%-8s fluxes=%-8s conservation=%s" % (
            p["condition"], v["states"]["status"], v["extents"]["status"],
            v["fluxes"]["status"], v["conservation_summary"]))
    print("negative control:", neg["observed_verdict"],
          "| software criterion:", neg["negative_software_test_criterion"])
    print("classification:", summary["scoped_classification"])
    return 0


def run_compare(full_csv, red_csv, tag):
    mpath = os.path.join(OUTDIR, "metrics-%s.json" % tag)
    cmd = [sys.executable, os.path.join(ROOT, "scripts",
                                        "compare_pnas2017_aa_v1_reduced.py"),
           "--full", full_csv, "--reduced", red_csv,
           "--scope", SCOPE, "--tau-fast", repr(TAU_FAST), "--out", mpath]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("compare failed for %s: %s" % (tag, r.stderr[-800:]))
    return json.load(open(mpath, encoding="utf-8")), mpath


def enrich(full_csv, red_csv, metrics, tiers):
    """per-observable max-abs error + floor materiality (raw alongside scaled)"""
    full = load_cols(full_csv)
    red = load_cols(red_csv)
    detail = {"states": {}, "extents": {}, "fluxes": {}}
    for name, rec in metrics["states"].items():
        worst, at = max_abs_error(full, red, name)
        sy = rec["S_y"]
        detail["states"][name] = {
            "E_inf": rec["E_inf"], "at_time_s": rec["at_time_s"],
            "max_abs_error": worst, "S_y": sy,
            "floor_dominates_scale": sy < FLOOR_CONC,
            "post_layer": rec.get("post_layer")}
    for name, rec in metrics["extents"].items():
        worst, at = max_abs_error(full, red, name)
        detail["extents"][name] = {
            "E_inf": rec["E_inf"], "at_time_s": rec["at_time_s"],
            "max_abs_error": worst, "S_y": rec["S_y"]}
    for fid, rec in metrics["fluxes"].items():
        detail["fluxes"][fid] = {
            "E_inf": rec["E_inf"], "at_time_s": rec["at_time_s"],
            "production_scale": rec.get("production_scale")}
    out = dict(metrics)
    out["detail_max_abs_error"] = detail
    out["thresholds"] = {
        "T_C": tiers["T_C_approximate_state_trajectories"]["threshold"],
        "T_D": tiers["T_D_approximate_instantaneous_fluxes"]["threshold"],
        "T_E": tiers["T_E_approximate_cumulative_resource_extents"]["threshold"],
        "T_G": tiers["T_G_conservation_balance_residual"]["threshold"]}
    return out


def conservation_status(metrics, scope):
    """T_G scoring with the frozen numeric_uncertainty_budget rule.
    Groups the scope marks as non-tiered proxies (e.g. the particle-count
    comparison) are reported but not T_G-scored."""
    tiered = {g["id"]: g.get("tiered", True) for g in scope["conservation"]}
    rows = {}
    for gid, g in metrics["conservation"].items():
        fr, rr = g["full_residual"], g["reduced_residual"]
        if not tiered.get(gid, True):
            st = "PROXY_NOT_TIERED"
        elif rr <= 1e-8:
            st = "PASS"
        elif fr > 1e-8:
            # the FULL reference itself does not hold this ledger to T_G at
            # the registered tolerances -> not decidable there (frozen rule)
            st = "NUMERICALLY_UNRESOLVED"
        else:
            st = "FAIL"
        rows[gid] = {"full_residual": fr, "reduced_residual": rr,
                     "cross_model_E_inf": g["cross_model_E_inf"],
                     "status": st}
    return rows


def pool_t0_agreement(full_csv, red_csv):
    """enzyme family totals at t0 must agree exactly (initial-layer rule)."""
    full = load_cols(full_csv)
    red = load_cols(red_csv)
    scope = json.load(open(SCOPE, encoding="utf-8"))
    out = {}
    for grp in scope["conservation"]:
        if grp["id"] not in ("MetRS_moiety_total", "GlyRS_moiety_total"):
            continue
        w = grp.get("weights") or {}
        f = sum(w.get(s, 1.0) * full[0][s] for s in grp["species"])
        r = sum(w.get(s, 1.0) * red[0][s] for s in grp["species"])
        out[grp["id"]] = {"full_t0": f, "reduced_t0": r,
                          "abs_diff": abs(f - r)}
    return out


def compare_pair(cid, scope, reg, hashes, tiers):
    full_csv = os.path.join(ROOT, reg["runs"]["FULL-%s" % cid]["trajectory"]
                            .replace("/", os.sep))
    red_csv = os.path.join(ROOT, reg["runs"]["RED-%s" % cid]["trajectory"]
                           .replace("/", os.sep))
    assert os.path.exists(full_csv), full_csv
    assert os.path.exists(red_csv), red_csv
    metrics, mpath = run_compare(full_csv, red_csv, cid)
    metrics = enrich(full_csv, red_csv, metrics, tiers)
    fm = json.load(open(os.path.join(MANS, "FULL-%s.manifest.json" % cid),
                        encoding="utf-8"))
    rm = json.load(open(os.path.join(MANS, "RED-%s.manifest.json" % cid),
                        encoding="utf-8"))
    cons = conservation_status(metrics, scope)
    cons_summary = []
    for gid, row in sorted(cons.items()):
        if row["status"] not in ("PASS", "PROXY_NOT_TIERED"):
            cons_summary.append("%s=%s" % (gid, row["status"]))
    verdicts = dict(metrics["verdicts"])
    verdicts["conservation_summary"] = ("ALL_PASS"
                                        if not cons_summary else
                                        "; ".join(cons_summary))
    any_fail = any(v["status"] == "FAIL" for k, v in verdicts.items()
                   if isinstance(v, dict)) or \
        any(row["status"] == "FAIL" for row in cons.values())
    any_unres = any(v["status"] == "NUMERICALLY_UNRESOLVED"
                    for k, v in verdicts.items() if isinstance(v, dict)) or \
        any(row["status"] == "NUMERICALLY_UNRESOLVED" for row in cons.values())
    verdicts["pair_status"] = ("FAIL" if any_fail else
                               "NUMERICALLY_UNRESOLVED" if any_unres else "PASS")
    worst_layer = None
    for name, rec in metrics["states"].items():
        pl = rec.get("post_layer")
        if pl and pl.get("E_inf") is not None:
            if worst_layer is None or pl["E_inf"] > worst_layer[1]:
                worst_layer = (name, pl["E_inf"])
    return {
        "condition": cid,
        "description": json.load(open(os.path.join(
            ROOT, reg["runs"]["FULL-%s" % cid]["config"].replace("/", os.sep)),
            encoding="utf-8"))["condition_description"],
        "full_config_sha256": reg["runs"]["FULL-%s" % cid]["config_sha256"],
        "red_config_sha256": reg["runs"]["RED-%s" % cid]["config_sha256"],
        "metrics_file": os.path.relpath(mpath, ROOT).replace("\\", "/"),
        "verdicts": verdicts,
        "conservation": cons,
        "initial_layer": {
            "red_consistent_start": rm.get("consistent_start"),
            "red_max_adjustment": rm.get("initial_layer_adjustment"),
            "layer_window_s": [1e-4, 1e-4 + 5 * TAU_FAST],
            "enzyme_pool_t0_agreement": pool_t0_agreement(full_csv, red_csv),
            "worst_post_layer_state": ({"state": worst_layer[0],
                                        "E_inf": worst_layer[1]}
                                       if worst_layer else None),
        },
        "red_algebraic_stats": rm.get("algebraic_root_statistics"),
        "numerics": {"full": {k: fm.get("solver_stats", {}).get(k)
                              for k in ("steps_successful", "steps_failed",
                                        "rhs_evaluations")},
                     "red": {k: rm.get("solver_stats", {}).get(k)
                             for k in ("steps_successful", "steps_failed",
                                       "rhs_evaluations")}},
    }


def compare_negative(scope, reg, hashes, tiers):
    exp = reg["runs"]["RED-NEG1"].get("expected_verdict", "FAIL")
    red_csv = os.path.join(ROOT, reg["runs"]["RED-NEG1"]["trajectory"]
                           .replace("/", os.sep))
    full_csv = os.path.join(ROOT, reg["runs"]["FULL-S0"]["trajectory"]
                            .replace("/", os.sep))
    try:
        if os.path.exists(red_csv):
            metrics, mpath = run_compare(full_csv, red_csv, "NEG1")
            metrics = enrich(full_csv, red_csv, metrics, tiers)
            worst = max((v["E_inf"] for v in metrics["states"].values()),
                        default=0.0)
            verdict = metrics["verdicts"]["states"]["status"]
            rejected = verdict == "FAIL"
            detail = {"comparison_states_worst_E_inf": worst,
                      "verdicts": metrics["verdicts"],
                      "metrics_file": os.path.relpath(mpath, ROOT).replace("\\", "/")}
        else:
            verdict = "RUN_FAILURE"
            rejected = True   # machinery refused the illegal partition
            detail = {"note": "RED-NEG1 produced no trajectory; the closure "
                              "guards rejected the illegal partition"}
        rm_path = os.path.join(MANS, "RED-NEG1.manifest.json")
        if os.path.exists(rm_path):
            rm = json.load(open(rm_path, encoding="utf-8"))
            detail["run_outcome"] = rm.get("outcome")
            detail["run_error"] = rm.get("error")
            detail["run_failure_class"] = classify_run_failure(rm.get("error"))
    except Exception as e:   # comparison machinery failure is NOT a rejection
        verdict = "COMPARISON_ERROR"
        rejected = False
        detail = {"error": str(e)}
    return {
        "run_id": "RED-NEG1",
        "compared_against": "FULL-S0",
        "expected_verdict": exp,
        "observed_verdict": verdict,
        "rejected_as_registered": rejected,
        "negative_software_test_criterion":
            "PASS" if rejected else "FAIL",
        "kind": "SOFTWARE/VALIDATOR negative control (not a biochemical "
                "failure regime)",
        "detail": detail,
    }


def classify_run_failure(err):
    if not err:
        return None
    e = err.lower()
    if "closure-lost" in e or "root failure" in e:
        return "ALGEBRAIC_CLOSURE_GUARD_REJECTED_PARTITION"
    return "OTHER_RUN_FAILURE"


def numerical_budget(acc):
    """frozen rule: reference uncertainty <= 10% of tier budget to decide."""
    # registered tolerance-convergence evidence (reference_chain.json):
    # worst deviation of RelTol 1e-8 vs 1e-10 over the 43 aa quantities
    dev_1e8 = 1.496205e-07
    budgets = {"T_C": 0.01, "T_D": 0.05, "T_E": 0.01, "T_H": 1e-6}
    rows = {}
    for k, b in budgets.items():
        rows[k] = {"budget": b, "ten_pct": 0.1 * b,
                   "reference_dev_1e8_vs_1e10": dev_1e8,
                   "decidable_at_registered_tolerances": dev_1e8 <= 0.1 * b}
    rows["note"] = ("registered reference-chain evidence: worst RelTol 1e-8 "
                    "vs 1e-10 deviation 1.496205e-07 over the 43 aminoacylation "
                    "quantities; runner reference-mode reproduction of the "
                    "tight reference 4.975e-10 trajectory-scaled (refcheck)")
    return rows


def classify(pairs, neg):
    s0 = next(p for p in pairs if p["condition"] == "S0")
    stress = [p for p in pairs if p["condition"] != "S0"]
    failed_stress = [p["condition"] for p in stress
                     if p["verdicts"]["pair_status"] != "PASS"]
    if s0["verdicts"]["pair_status"] == "PASS" and not failed_stress:
        return "APPROXIMATE_REDUCTION_VALIDATED_ON_DECLARED_DOMAIN"
    if s0["verdicts"]["pair_status"] == "PASS":
        cats = sorted({c for p in stress for c in failure_categories(p)})
        return ("APPROXIMATE_REDUCTION_VALIDATED_ON_REFERENCE_DOMAIN_"
                "WITH_STRESS_LIMITS [failing conditions: %s; categories: %s]"
                % (",".join(failed_stress), ",".join(cats)))
    if s0["verdicts"]["pair_status"] == "NUMERICALLY_UNRESOLVED":
        return "NUMERICALLY_UNRESOLVED"
    return "FAILED_VALIDATION_ON_REFERENCE_DOMAIN [categories: %s]" % \
        ",".join(sorted(failure_categories(s0)))


def failure_categories(p):
    cats = []
    for tier, cat in (("states", "state_trajectory"), ("extents", "cumulative_resource"),
                      ("fluxes", "instantaneous_flux")):
        st = p["verdicts"].get(tier, {}).get("status")
        if st == "FAIL":
            cats.append(cat)
        elif st == "NUMERICALLY_UNRESOLVED":
            cats.append(cat + "_numerically_unresolved")
    for gid, row in p.get("conservation", {}).items():
        if row["status"] == "FAIL":
            cats.append("conservation:" + gid)
        elif row["status"] == "NUMERICALLY_UNRESOLVED":
            cats.append("conservation_numerically_unresolved:" + gid)
    return cats


if __name__ == "__main__":
    sys.exit(main())
