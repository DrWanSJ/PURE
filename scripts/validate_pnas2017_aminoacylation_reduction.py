#!/usr/bin/env python3
"""Independently validate the PNAS 2017 aminoacylation reduction artefacts.

This script does NOT import or trust
scripts/analyze_pnas2017_aminoacylation_reduction.py. It re-reads the committed
artefacts AND re-derives the science from the raw audit CSVs, the SHA-pinned
SBML, and the author reference trajectory, then asserts the protocol invariants,
the pre-registration integrity, and the self-containedness of the pipeline.

Exits non-zero if ANY check fails.

Run:  python scripts/validate_pnas2017_aminoacylation_reduction.py
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
SBML_REL = "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
SBML = os.path.join(ROOT, *SBML_REL.split("/"))
PROVENANCE = os.path.join(ROOT, "data", "provenance.csv")
PROVENANCE_ITEM = "Matsuura_2017_combined_SBML"
TRAJ_REL = "results/pnas2017_reference/2026-09-24_authors_model_v0/authors_model_trajectory.csv"
TRAJ = os.path.join(ROOT, *TRAJ_REL.split("/"))
PREREG = os.path.join(ROOT, "docs", "audit", "pnas2017_aminoacylation_reduction_v0", "preregistration.json")
ACCEPT = os.path.join(ROOT, "docs", "audit", "pnas2017_aminoacylation_reduction_v0", "acceptance_criteria.json")

EXACT_TOL = 1e-9
CONS_TOL = 1e-12
N_REACTIONS = 138
N_SPECIES = 47
N_PAIRS = 52

PATHWAYS = {
    "Gly": dict(cycle=["re0000000132", "re0000000134", "re0000000140", "re0000000207",
                        "re0000000189", "re0000000178", "re0000000182", "re0000000145"],
                net={"Gly": -1, "ATP": -1, "tRNAGlyGCC": -1, "GlytRNAGlyGCC": 1, "AMP": 1, "PPi": 1}),
    "Met": dict(cycle=["re0000000157", "re0000000159", "re0000000165", "re0000000249",
                        "re0000000231", "re0000000220", "re0000000224", "re0000000170"],
                net={"Met": -1, "ATP": -1, "tRNAfMetCAU": -1, "MettRNAfMetCAU": 1, "AMP": 1, "PPi": 1}),
}

fails = []
passes = 0


def check(name, cond, detail=""):
    global passes
    if cond:
        passes += 1
        print("PASS  %s %s" % (name, detail))
    else:
        fails.append(name)
        print("FAIL  %s %s" % (name, detail))


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_side(s):
    d = {}
    for tok in (s or "").split("|"):
        tok = tok.strip()
        if tok:
            sp, st = tok.rsplit(":", 1)
            d[sp] = d.get(sp, 0.0) + float(st)
    return d


def net_of(r):
    d = {}
    for k, c in parse_side(r["reactants"]).items():
        d[k] = d.get(k, 0.0) - c
    for k, c in parse_side(r["products"]).items():
        d[k] = d.get(k, 0.0) + c
    return {k: c for k, c in d.items() if abs(c) > 1e-12}


_ALLOWED = (ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Store,
            ast.BinOp, ast.UnaryOp, ast.operator, ast.unaryop,
            ast.BoolOp, ast.boolop, ast.Compare, ast.cmpop)


def rate_fn(expr):
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED):
            raise ValueError("unsafe rate law node")
    code = compile(tree, "<r>", "eval")

    def ev(state, k1):
        env = dict(state); env["k1"] = k1
        return eval(code, {"__builtins__": {}}, env)
    return ev


def canonical_hash(path):
    d = json.load(open(path, encoding="utf-8"))
    return hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    # ---- 1. SBML SHA vs provenance (no canonical source modification) -------- #
    sha = hashlib.sha256(open(SBML, "rb").read()).hexdigest()
    prov_sha = ""
    for r in load(PROVENANCE):
        vals = list(r.values())
        if PROVENANCE_ITEM in vals:
            prov_sha = next((v for v in vals if re.fullmatch(r"[0-9a-f]{64}", v or "")), "")
    check("sbml_sha_matches_provenance", sha == prov_sha and len(sha) == 64, sha[:12])

    # ---- 2. independent subsystem selection --------------------------------- #
    reactions = load(os.path.join(AUDIT, "reactions.csv"))
    species = {s["id"]: s for s in load(os.path.join(AUDIT, "species.csv"))}
    aa = [r for r in reactions if "Aminoacylation" in (r["subsystem_files"] or "")]
    aa_ids = sorted(r["id"] for r in aa)
    aa_species = sorted({s for r in aa for s in net_of(r)})
    check("reaction_count_reproducible", len(aa) == N_REACTIONS, "%d" % len(aa))
    check("species_count_reproducible", len(aa_species) == N_SPECIES, "%d" % len(aa_species))

    inv = json.load(open(os.path.join(AUDIT, "aminoacylation_inventory.json"), encoding="utf-8"))
    check("inventory_matches_recount",
          inv["n_reactions"] == len(aa) and inv["n_species"] == len(aa_species)
          and inv["reaction_ids"] == aa_ids and inv["species_ids"] == aa_species)
    check("inventory_sbml_sha_matches", inv["source_sbml_sha256"] == sha)

    # ---- 3. committed reaction/species artefacts reference real ids ---------- #
    cmm_rx = load(os.path.join(AUDIT, "aminoacylation_reactions.csv"))
    cmm_sp = load(os.path.join(AUDIT, "aminoacylation_species.csv"))
    check("committed_rx_ids_exist", {r["reaction_id"] for r in cmm_rx} == set(aa_ids))
    check("committed_sp_ids_exist", {r["species_id"] for r in cmm_sp} == set(aa_species))
    check("all_species_in_model", all(s in species for s in aa_species))

    # ---- 4. pathway net chemistry re-derivation ----------------------------- #
    rxmap = {r["id"]: r for r in reactions}
    for name, cfg in PATHWAYS.items():
        vec = {}
        for rid in cfg["cycle"]:
            if rid not in rxmap:
                check("pathway_%s_reactions_exist" % name, False, rid); vec = None; break
            for k, c in net_of(rxmap[rid]).items():
                vec[k] = vec.get(k, 0.0) + c
        if vec is None:
            continue
        vec = {k: c for k, c in vec.items() if abs(c) > 1e-9}
        check("pathway_%s_net_matches_expected" % name, vec == cfg["net"], str(sorted(vec.items())))
        # ATP->AMP+PPi and tRNA charging balance
        check("pathway_%s_energy_balance" % name,
              vec.get("ATP") == -1 and vec.get("AMP") == 1 and vec.get("PPi") == 1)
        check("pathway_%s_trna_balance" % name,
              vec.get("tRNAGlyGCC" if name == "Gly" else "tRNAfMetCAU") == -1
              and vec.get("GlytRNAGlyGCC" if name == "Gly" else "MettRNAfMetCAU") == 1)

    # ---- 5. reversible pairs: recompute + exact RHS identity ---------------- #
    pmap = {}
    for p in load(os.path.join(AUDIT, "parameters.csv")):
        try:
            pmap[(p["reaction_id"], p["parameter_id"])] = float(p["author_export_value"])
        except (ValueError, TypeError):
            pmap[(p["reaction_id"], p["parameter_id"])] = float("nan")

    def sig(r):
        return tuple(sorted((k, round(c, 9)) for k, c in parse_side(r["reactants"]).items()))

    def sigp(r):
        return tuple(sorted((k, round(c, 9)) for k, c in parse_side(r["products"]).items()))

    by_sigp = {}
    for r in aa:
        by_sigp.setdefault(sigp(r), []).append(r)
    pairs = []
    seen = set()
    for r in aa:
        for cand in by_sigp.get(sig(r), []):
            if cand["id"] != r["id"] and sig(cand) == sigp(r):
                key = tuple(sorted((r["id"], cand["id"])))
                if key not in seen:
                    seen.add(key)
                    pairs.append((r, cand))
    check("pair_count_reproducible", len(pairs) == N_PAIRS, "%d" % len(pairs))
    cmm_pairs = load(os.path.join(AUDIT, "aminoacylation_reversible_pairs.csv"))
    committed_pairset = {tuple(sorted((p["forward_reaction_id"], p["reverse_reaction_id"]))) for p in cmm_pairs}
    check("committed_pairs_match_recount",
          {tuple(sorted((a["id"], b["id"]))) for a, b in pairs} == committed_pairset)

    # exact RHS identity at reference trajectory states
    traj = load(TRAJ)
    worst = 0.0
    for a, b in pairs:
        na, nb = net_of(a), net_of(b)
        struct = set(na) == set(nb) and all(abs(na[k] + nb[k]) < 1e-12 for k in na)
        if not struct:
            check("pair_structural_%s_%s" % (a["id"], b["id"]), False); continue
        ka, kb = pmap.get((a["id"], "k1")), pmap.get((b["id"], "k1"))
        fa, fb = rate_fn(a["rate_law"]), rate_fn(b["rate_law"])
        for row in traj:
            state = {s: float(row.get(s, 0.0) or 0.0) for s in aa_species}
            vf, vr = fa(state, ka), fb(state, kb)
            for s in na:
                full = vf * na[s] + vr * nb[s]
                red = (vf - vr) * na[s]
                scale = max(abs(full), 1e-12)
                worst = max(worst, abs(full - red) / scale)
    check("reversible_pairs_exact_rhs_identity", worst < EXACT_TOL, "max_rel_residual=%.3e" % worst)

    # ---- 6. enzyme-pool conservation --------------------------------------- #
    for pref in ("MetRS", "GlyRS"):
        worst_c = 0.0
        for r in aa:
            if pmap.get((r["id"], "k1"), 0.0) in (0.0,) or pmap.get((r["id"], "k1")) is None:
                continue
            n = net_of(r)
            active = sum(c for s, c in n.items() if (s == pref or s.startswith(pref + "_")) and not s.endswith("_degraded"))
            worst_c = max(worst_c, abs(active))
        check("%s_active_pool_conserved" % pref, worst_c < CONS_TOL, "max|L.S|=%.2e" % worst_c)

    # ---- 7. pre-registration integrity ------------------------------------- #
    pre = json.load(open(PREREG, encoding="utf-8"))
    frozen = pre["frozen_artifacts_sha256"]
    ok_hashes = True
    for fname, want in frozen.items():
        got = hashlib.sha256(open(os.path.join(AUDIT, fname), "rb").read()).hexdigest()
        if got != want:
            ok_hashes = False
            print("   hash mismatch:", fname, got[:12], "!=" , want[:12])
    check("preregistration_artifact_hashes_intact", ok_hashes, "%d artefacts" % len(frozen))
    check("preregistration_source_head_matches_freeze",
          pre["frozen_source"]["source_head"] == "8710b85cac27dbe7a1a2805a8e7f79d87e3d51e6")
    check("preregistration_sbml_sha_matches",
          pre["frozen_source"]["source_model_sha256"] == sha)

    # ---- 8. thresholds unchanged after pre-registration -------------------- #
    acc_canon = canonical_hash(ACCEPT)
    m = re.search(r"[0-9a-f]{64}", pre["preregistration_commit_or_hash"])
    check("acceptance_thresholds_unchanged", bool(m) and m.group(0) == acc_canon, acc_canon[:12])
    acc = json.load(open(ACCEPT, encoding="utf-8"))
    # approximate tiers must remain null (not silently invented)
    approx_null = all(acc["tiers"][t]["threshold"] is None for t in
                      ("T_C_approximate_state_trajectory", "T_D_approximate_instantaneous_flux",
                       "T_E_approximate_cumulative_resource_extent"))
    check("approximate_thresholds_not_invented", approx_null)

    # ---- 9. no scratch dependency ------------------------------------------ #
    scratch_hit = []
    for fn in os.listdir(AUDIT):
        if fn.startswith("aminoacylation_"):
            txt = open(os.path.join(AUDIT, fn), encoding="utf-8", errors="ignore").read().lower()
            if re.search(r"\bscratch[\\/]", txt) or "scratch dir" in txt:
                scratch_hit.append(fn)
    check("no_scratch_dependency", not scratch_hit, str(scratch_hit))

    # ---- 10. structural integrity of JSON artefacts ------------------------ #
    for fn in ("aminoacylation_inventory.json", "aminoacylation_analysis_summary.json"):
        try:
            json.load(open(os.path.join(AUDIT, fn), encoding="utf-8"))
            check("json_valid_" + fn, True)
        except Exception as e:  # noqa
            check("json_valid_" + fn, False, str(e))
    summ = json.load(open(os.path.join(AUDIT, "aminoacylation_analysis_summary.json"), encoding="utf-8"))
    check("summary_no_manifold_claimed", summ["algebraic_qssa_manifold_derived"] is False)
    check("summary_qssa_not_certified", "CERTIFIED" not in summ["qssa_status"] or "NOT_CERTIFIED" in summ["qssa_status"])

    # ---- 11. forbidden project action -------------------------------------- #
    core = os.path.join(ROOT, "models", "pure_reduced_core")
    bad_xml = []
    if os.path.isdir(core):
        bad_xml = [f for f in os.listdir(core) if f.endswith(".xml")]
    check("no_reduced_core_built", not bad_xml, str(bad_xml))

    print("\n%d checks passed, %d failed." % (passes, len(fails)))
    if fails:
        print("FAILED:", ", ".join(fails))
        return 1
    print("ALL AMINOACYLATION REDUCTION CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
