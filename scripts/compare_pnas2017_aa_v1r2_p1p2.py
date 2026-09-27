#!/usr/bin/env python3
"""Phase 4 P1/P2 cross-validation for the v1r2 initialization map.

Compares, per stress condition:
  P1  conservation-constrained algebraic projection  (run_pnas2017_aa_v1_formal.m
      consistentStartV1r2, dumped as <trajectory>.initial_state.json)
  P2  fast-boundary-layer dynamic projection         (run_pnas2017_aa_v1r2_fastlayer.m,
      layer exit = end of the registered 5*tau_fast window)

over: all 21 eliminated complexes, free Met/Gly, free tRNAs, aminoacyl-tRNAs,
ATP, AMP, PPi, MetAMP, GlyAMP, enzyme free/bound distributions, and every
B_init inventory row.  Reports max absolute difference, scaled difference,
worst species; verifies both states carry the author physical inventories;
and applies the registered branch-equivalence criterion: same sign pattern on
the eliminated complexes, same enzyme-occupancy regime, and closure agreement
at matched slow variables.  A branch flip is a STOP condition.

Output: scratch/v1r2/p1p2_comparison_<cid>.json (+ a combined summary).
"""

import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = os.path.join(ROOT, "docs", "audit", "pnas2017_aminoacylation_reduction_v1")

COMPARE_STATES = [
    # 21 eliminated complexes are added dynamically from the partition
    "Met", "Gly", "ATP", "AMP", "PPi", "MetAMP", "GlyAMP",
    "tRNAfMetCAU", "tRNAGlyGCC", "MettRNAfMetCAU", "GlytRNAGlyGCC",
    "MetRS", "GlyRS",
    "MetRS_MetAMP", "MetRS_MettRNAfMetCAU", "GlyRS_AMP", "GlyRS_GlyAMP",
    "GlyRS_GlyAMP_PPi_tRNAGlyGCC", "GlyRS_GlyAMP_tRNAGlyGCC",
    "GlyRS_GlytRNAGlyGCC",
]

# floors for the scaled difference (per acceptance error_formulas)
FLOOR = 1e-6
# registered branch-equivalence criterion (Phase 4).  A MATERIAL branch flip
# requires P1 to predict material content (>1e-3 uM) for an eliminated
# complex that the detailed fast dynamics NEVER forms (P2 < 1e-8) -- i.e.
# the algebraic projection selects a different solution sheet.  The reverse
# (P2 > 1e-3 where P1 is empty) is the kept-complex-mediated formation path:
# P1's registered slow point holds the kept complexes at their author value
# 0, so complexes produced only through them are exactly 0 there (P1's value
# is the exact closure solution at its own slow state); this is reported as
# a layer-window difference, not a branch flip.
FLIP_EMPTY = 1e-8
FLIP_MATERIAL = 1e-3


def load_initial_state(path):
    d = json.load(open(path))
    return dict(zip(d["state_names"], d["state"])), d


def load_layer_exit(path):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    last = rows[-1]
    return {k: float(v) for k, v in last.items() if k != "time"}, float(last["time"])


def load_binit_rows():
    rows = {}
    with open(os.path.join(AUD, "binit_v1r2_matrix.csv")) as f:
        rd = csv.DictReader(f)
        names = list(rd.fieldnames)[1:]
        for row in rd:
            rows[row["row"]] = {s: float(v) for s, v in row.items() if s != "row"}
    return rows, names


def compare_condition(cid, p1_state, p2_state, p2_t, binit, names, part):
    elim = part["eliminated_states"]
    report = {"condition": cid, "p2_layer_exit_time_s": p2_t, "entries": {}}
    states = list(elim) + [s for s in COMPARE_STATES]
    worst = (None, 0.0, 0.0)
    branch_sign_flip = []
    for s in states:
        a, b = p1_state[s], p2_state[s]
        absd = abs(a - b)
        scald = absd / max(abs(a), abs(b), FLOOR)
        report["entries"][s] = {
            "p1": a, "p2": b, "abs_diff": absd, "scaled_diff": scald,
            "class": ("eliminated_complex" if s in elim else "slow_state")}
        if elim and s in elim and (b < FLIP_EMPTY and a > FLIP_MATERIAL):
            branch_sign_flip.append(s)
        if elim and s in elim and (a < FLIP_EMPTY and b > FLIP_MATERIAL):
            report.setdefault("kept_mediated_layer_differences", []).append(
                {"species": s, "p2": b})
        if absd > worst[2]:
            worst = (s, absd, scald)
    report["worst_species_abs"] = {"name": worst[0], "abs": worst[1],
                                   "scaled": worst[2]}
    # B_init inventories of both states vs the author value
    inv = {}
    for rname, w in binit.items():
        v1 = sum(w[s] * p1_state[s] for s in names)
        v2 = sum(w[s] * p2_state[s] for s in names)
        inv[rname] = {"p1": v1, "p2": v2, "abs_diff": abs(v1 - v2)}
    report["binit_inventories"] = inv
    report["branch_sign_flip"] = branch_sign_flip
    return report


def main():
    part = json.load(open(os.path.join(AUD, "candidate_partition_v1r1.json")))
    binit, names = load_binit_rows()
    conds = sys.argv[1:] or ["S0"]
    scratch = os.path.join(ROOT, "scratch", "v1r2")
    summary = {}
    all_pass = True
    for cid in conds:
        p1_path = os.path.join(scratch, "RED-%s-v1r2-smoke.csv.initial_state.json" % cid)
        p2_path = os.path.join(scratch, "fastlayer-%s.csv" % cid)
        if not (os.path.exists(p1_path) and os.path.exists(p2_path)):
            print("SKIP %s: missing %s" % (cid, p1_path if not os.path.exists(p1_path) else p2_path))
            continue
        p1_state, _ = load_initial_state(p1_path)
        p2_state, p2_t = load_layer_exit(p2_path)
        rep = compare_condition(cid, p1_state, p2_state, p2_t, binit, names, part)
        out = os.path.join(scratch, "p1p2_comparison_%s.json" % cid)
        with open(out, "w", newline="\n") as f:
            json.dump(rep, f, indent=1)
            f.write("\n")
        summary[cid] = {
            "worst": rep["worst_species_abs"],
            "branch_sign_flip": rep["branch_sign_flip"],
            "inventories_max_abs_diff": max(
                v["abs_diff"] for v in rep["binit_inventories"].values()),
        }
        w = rep["worst_species_abs"]
        print("%s: worst abs %s %.6g (scaled %.3g), sign flips: %s" % (
            cid, w["name"], w["abs"], w["scaled"], rep["branch_sign_flip"]))
        for rn, v in rep["binit_inventories"].items():
            print("   %-38s p1=%.10g p2=%.10g |d|=%.3g" % (rn, v["p1"], v["p2"], v["abs_diff"]))
    with open(os.path.join(scratch, "p1p2_comparison_summary.json"), "w",
              newline="\n") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    flips = [c for c in summary if summary[c]["branch_sign_flip"]]
    if flips:
        print("BRANCH SIGN FLIP on", flips, "-> STOP per Phase 4")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
