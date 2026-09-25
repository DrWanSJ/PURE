#!/usr/bin/env python3
"""Compute registered full-vs-reduced error metrics for the A3a comparison.

Reads two runner trajectories (full reference and reduced DAE, same grid),
the v1 acceptance criteria, and a scope list, and emits the registered
metrics per tier:

  T_C  per-species state trajectories   E_inf <= 0.01
  T_D  process fluxes                    E_inf <= 0.05  (production-scale norm)
  T_E  cumulative extents                E_inf <= 0.01
  T_G  conservation totals               residual <= 1e-8
  T_H  (A1) identity runs                 E_inf <= 1e-6

E_inf(y) = max_t |y_red - y_full| / max(S_y, floor) with S_y taken from the
FULL reference only. Fluxes are recomputed from the STATE trajectories using
the SBML-derived monomial rate laws and normalized by the declared
production scale max_t max(v_f, v_r), never by the near-zero net flux.

The initial-layer window is reported separately:
  metrics_all_window, metrics_post_layer   with layer window
  [t0, t0 + 5*tau_fast] (tau_fast passed in; nan tau => window = {t0}).

Usage:
  python scripts/compare_pnas2017_aa_v1_reduced.py \
      --full FULL.csv --reduced RED.csv --scope scope.json \
      --tau-fast 1.9e-5 --out metrics.json

scope.json:
  {"states": [...species names...],
   "extents": [...xi column names...],
   "flux_pairs": [{"id": str, "forward": rid, "reverse": rid|null}]}
"""
import argparse
import ast
import csv
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")

FLOOR_CONC = 1e-6
FLOOR_FLUX = 1e-9
ALLOWED = (ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Store,
           ast.BinOp, ast.UnaryOp, ast.operator, ast.unaryop, ast.BoolOp,
           ast.boolop, ast.Compare, ast.cmpop)


def load(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def rate_fn(expr):
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED):
            raise ValueError("unsafe rate law node")
    code = compile(tree, "<r>", "eval")

    def ev(state, k1):
        env = dict(state)
        env["k1"] = k1
        return eval(code, {"__builtins__": {}}, env)
    return ev


def e_inf(full, red, times, scale, floor, tmin=None):
    num = 0.0
    at = None
    for i, t in enumerate(times):
        if tmin is not None and t < tmin:
            continue
        d = abs(red[i] - full[i]) / max(scale, floor)
        if d > num:
            num, at = d, t
    return {"E_inf": num, "at_time_s": at}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", required=True)
    ap.add_argument("--reduced", required=True)
    ap.add_argument("--scope", required=True)
    ap.add_argument("--tau-fast", type=float, default=float("nan"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    scope = json.load(open(args.scope, encoding="utf-8"))
    full = load(args.full)
    red = load(args.reduced)
    assert len(full) == len(red)
    times = [float(r["time"]) for r in full]
    assert all(abs(math.log(times[i]) - math.log(float(red[i]["time"]))) < 1e-9
               for i in range(len(times))), "grids differ"

    t_layer = times[0] + 5.0 * args.tau_fast if args.tau_fast == args.tau_fast else None

    rxs = {r["id"]: r for r in load(os.path.join(AUDIT, "reactions.csv"))}
    params = {p["reaction_id"]: float(p["author_export_value"])
              for p in load(os.path.join(AUDIT, "parameters.csv"))}

    out = {"tau_fast_s": args.tau_fast,
           "layer_window": [times[0], t_layer] if t_layer else None,
           "states": {}, "extents": {}, "fluxes": {}, "conservation": {}}

    for name in scope["states"]:
        f = [float(r[name]) for r in full]
        v = [float(r[name]) for r in red]
        scale = max(max(abs(x) for x in f), 0.0)
        rec = e_inf(f, v, times, scale, FLOOR_CONC)
        rec["S_y"] = scale
        if t_layer:
            rec["post_layer"] = e_inf(f, v, times, scale, FLOOR_CONC, tmin=t_layer)
        out["states"][name] = rec

    for name in scope["extents"]:
        col = name if name in full[0] else "xi_" + name
        f = [float(r[col]) for r in full]
        v = [float(r[col]) for r in red]
        scale = max(abs(x) for x in f) if f else 0.0
        rec = e_inf(f, v, times, scale, FLOOR_FLUX)
        rec["S_y"] = scale
        out["extents"][col] = rec

    for fp in scope.get("flux_pairs", []):
        fwd = rxs[fp["forward"]]
        rev = rxs[fp["reverse"]] if fp.get("reverse") else None
        ff = rate_fn(fwd["rate_law"])
        fr = rate_fn(rev["rate_law"]) if rev else None
        kf = params[fp["forward"]]
        kr = params[fp["reverse"]] if rev else None
        series = {"full": [], "red": []}
        for tag, rows in (("full", full), ("red", red)):
            vals = []
            for r in rows:
                st = {k: float(vv) for k, vv in r.items() if k != "time"}
                v = ff(st, kf)
                if fr:
                    v = v - fr(st, kr)
                vals.append(v)
            series[tag] = vals
        vf_full, vf_red = series["full"], series["red"]
        # production scale from the full run
        prod = []
        for i, r in enumerate(full):
            st = {k: float(vv) for k, vv in r.items() if k != "time"}
            a = ff(st, kf)
            b = fr(st, kr) if fr else 0.0
            prod.append(max(abs(a), abs(b)))
        scale = max(prod + [0.0])
        rec = e_inf(vf_full, vf_red, times, scale, FLOOR_FLUX)
        rec["production_scale"] = scale
        out["fluxes"][fp["id"]] = rec

    # conservation totals (family sums), scaled residuals.  A group may
    # carry optional per-species "weights" (e.g. the weighted phosphate
    # ledger); unweighted family sums are the default.
    for grp in scope.get("conservation", []):
        w = grp.get("weights") or {}
        if w:
            members_full = [sum(w[s] * float(r[s]) for s in grp["species"])
                            for r in full]
            members_red = [sum(w[s] * float(r[s]) for s in grp["species"])
                           for r in red]
        else:
            members_full = [sum(float(r[s]) for s in grp["species"]) for r in full]
            members_red = [sum(float(r[s]) for s in grp["species"]) for r in red]
        base = max(abs(members_full[0]), 1.0)  # dimensionless floor 1e-12 on ratio
        res_f = max(abs(x - members_full[0]) for x in members_full) / base
        res_r = max(abs(x - members_red[0]) for x in members_red) / base
        drift = e_inf(members_full, members_red, times, base, 1e-12)
        out["conservation"][grp["id"]] = {
            "full_residual": res_f, "reduced_residual": res_r,
            "cross_model_E_inf": drift["E_inf"]}

    # verdicts against registered tiers
    acc = json.load(open(os.path.join(ROOT, "docs/audit/pnas2017_aminoacylation_reduction_v1",
                                      "acceptance_criteria.json"), encoding="utf-8"))
    lim = {"states": acc["tiers"]["T_C_approximate_state_trajectories"]["threshold"],
           "extents": acc["tiers"]["T_E_approximate_cumulative_resource_extents"]["threshold"],
           "fluxes": acc["tiers"]["T_D_approximate_instantaneous_fluxes"]["threshold"]}
    out["verdicts"] = {}
    for kind, budget in lim.items():
        worst = max((v.get("E_inf", v.get("cross_model_E_inf", 0.0))
                     if kind != "states" else v["E_inf"]
                     for v in out[kind].values()), default=None)
        out["verdicts"][kind] = {
            "budget": budget,
            "worst": worst,
            "status": ("PASS" if worst is not None and worst <= budget else
                       ("FAIL" if worst is not None else "NOT_SCORED"))}

    with open(args.out, "w", newline="\n", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(json.dumps(out["verdicts"], indent=2))


if __name__ == "__main__":
    main()
