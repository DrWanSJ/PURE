#!/usr/bin/env python3
"""PNAS 2017 aminoacylation reduction v1 — A3a selective-QSSA DERIVATION stage.

Candidate A3a: eliminate enzyme-bound complexes selectively, KEEP the free
aminoacyl-adenylates (MetAMP, GlyAMP) as dynamic states, and reconstruct the
free enzyme exactly from the proved active-pool conservation:

    per-enzyme active pool: {E, C_1..C_14}, E_pool = E + sum C_i (proved invariant
    while degradation k1 = 0 — true at the author reference parameterization),
    fast coordinates q = selected C_i with E = E_pool - sum(q + q_kept).

This stage derives, for EACH enzyme separately and at states sampled along the
tight whole-network reference:
  * the reference-active connectivity graph over the 15 active enzyme states;
  * exact invariants (left null space of the enzyme-state stoichiometry);
  * the FULL eigenvalue spectrum of the closed fast Jacobian J = dG/dC,
    reported mode-by-mode (no single-lambda summaries presented as the scale);
  * algebraic closure G(C)=0 solved by feasibility-projected damped Newton from
    several starts (supporting evidence for branch uniqueness only);
  * frozen-slow relaxation tests toward the branch from perturbed starts;
  * slowest-attracting-mode tau vs empirical 1%-relaxation time.

Run:  python scripts/analyze_pnas2017_aminoacylation_reduction_v1_qssa.py
"""
import ast
import csv
import json
import math
import os
import sys
from collections import OrderedDict

import numpy as np
from scipy.integrate import solve_ivp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")
TIGHT_REL = ("results/pnas2017_reference/2026-09-25_aa_v1_reference_tight/"
             "authors_model_trajectory_tight.csv")
NAMES_REL = ("results/pnas2017_reference/2026-09-25_aa_v1_reference_tight/state_names.txt")

_ALLOWED = (ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Store,
            ast.BinOp, ast.UnaryOp, ast.operator, ast.unaryop,
            ast.BoolOp, ast.boolop, ast.Compare, ast.cmpop)


def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_side(s):
    out = {}
    for tok in (s or "").split("|"):
        tok = tok.strip()
        if not tok:
            continue
        spec, stoich = tok.rsplit(":", 1)
        out[spec] = out.get(spec, 0.0) + float(stoich)
    return out


def net_vector(rct, prd):
    v = {}
    for k, c in rct.items():
        v[k] = v.get(k, 0.0) - c
    for k, c in prd.items():
        v[k] = v.get(k, 0.0) + c
    return {k: c for k, c in v.items() if abs(c) > 0.0}


def compile_rate(expr):
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED):
            raise ValueError("disallowed node")
    return compile(tree, "<rate>", "eval")


def main():
    reactions = load_rows(os.path.join(AUDIT, "reactions.csv"))
    parameters = load_rows(os.path.join(AUDIT, "parameters.csv"))
    pmap = {}
    for p in parameters:
        try:
            pmap[(p["reaction_id"], p["parameter_id"])] = float(p["author_export_value"])
        except (ValueError, TypeError):
            pmap[(p["reaction_id"], p["parameter_id"])] = float("nan")

    rx_all = []
    for r in reactions:
        rct, prd = parse_side(r["reactants"]), parse_side(r["products"])
        nv = net_vector(rct, prd)
        k1 = pmap.get((r["id"], "k1"), float("nan"))
        rx_all.append(dict(id=r["id"], net=nv, k1=k1,
                           code=compile_rate(r["rate_law"]),
                           names={n.id for n in ast.walk(ast.parse(r["rate_law"], mode="eval"))
                                  if isinstance(n, ast.Name)} - {"k1"},
                           sub=r["subsystem_files"]))
    rx_by = {r["id"]: r for r in rx_all}

    names_t = [l.strip() for l in open(os.path.join(ROOT, NAMES_REL))]
    T = np.loadtxt(os.path.join(ROOT, TIGHT_REL), delimiter=",", usecols=range(242), skiprows=1)
    ts = T[:, 0]
    traj = [dict(zip(names_t, row)) for row in T[:, 1:]]

    struct_rows, spec_rows, closure_rows, relax_rows, defect_rows = [], [], [], [], []

    for enz in ("MetRS", "GlyRS"):
        complexes = sorted(s for s in names_t if s.startswith(enz + "_")
                           and not s.endswith("_degraded"))
        pool = [enz] + complexes
        cidx = {s: i for i, s in enumerate(complexes)}
        nq = len(complexes)
        pool_set = set(pool)
        pool_rids = [r["id"] for r in rx_all if set(r["net"]) & pool_set]
        active_rids = [rid for rid in pool_rids if rx_by[rid]["k1"] == rx_by[rid]["k1"]
                       and rx_by[rid]["k1"] != 0.0]

        # ---- enzyme-state sub-stoichiometry over ACTIVE reactions + invariants ---- #
        sidx = {s: i for i, s in enumerate(pool)}
        S = np.zeros((len(pool), len(active_rids)))
        for j, rid in enumerate(active_rids):
            for s, c in rx_by[rid]["net"].items():
                if s in sidx:
                    S[sidx[s], j] = c
        U, sv, Vt = np.linalg.svd(S, full_matrices=True)
        rank = int(np.sum(sv > 1e-12))
        null_rows = U[:, rank:].T
        inv_desc = []
        pool_one_is_invariant = False
        for row in null_rows:
            vec = {pool[i]: round(float(row[i]), 9) for i in range(len(pool))
                   if abs(row[i]) > 1e-9}
            inv_desc.append(vec)
        # the all-ones vector must be (a multiple of) one of the invariant rows
        for row in null_rows:
            if np.max(np.abs(row - row[0])) < 1e-9:
                pool_one_is_invariant = True

        # ---- connectivity of complexes under ACTIVE reactions only ---- #
        parent = {s: s for s in pool}

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for rid in active_rids:
            touched = [s for s in rx_by[rid]["net"] if s in pool_set]
            for s in touched[1:]:
                union(touched[0], s)
        comps = {}
        for s in pool:
            comps.setdefault(find(s), []).append(s)
        comps = sorted(comps.values(), key=lambda c: (enz not in c, sorted(c)))

        struct_rows.append(OrderedDict([
            ("enzyme", enz),
            ("n_complexes", nq),
            ("n_pool_states", len(pool)),
            ("n_reactions_touching_pool_all", len(pool_rids)),
            ("n_reactions_touching_pool_active", len(active_rids)),
            ("rank_active_enzyme_state_S", rank),
            ("n_invariants_active_subnetwork", len(null_rows)),
            ("invariants_active_subnetwork", json.dumps(inv_desc)),
            ("ones_vector_is_invariant", str(pool_one_is_invariant).lower()),
            ("n_connected_components_active", len(comps)),
            ("components", json.dumps([sorted(c) for c in comps])),
        ]))

        # ---- fast vector field with free enzyme reconstructed ---- #
        def fast_rhs(C, svals, e_pool):
            e0 = e_pool - C.sum()
            env = dict(svals)
            env[enz] = e0
            for i, sp in enumerate(complexes):
                env[sp] = C[i]
            dC = np.zeros(nq)
            for rid in pool_rids:
                r = rx_by[rid]
                if not r["names"] <= (set(svals) | pool_set):
                    raise SystemExit("reaction %s depends on %s outside env"
                                     % (rid, r["names"] - set(svals) - pool_set))
                env["k1"] = r["k1"]
                v = eval(r["code"], {"__builtins__": {}}, env)
                for s, c in r["net"].items():
                    if s in cidx:
                        dC[cidx[s]] += v * c
            return dC

        def GJ(C, svals, e_pool, hrel=1e-7):
            g0 = fast_rhs(C, svals, e_pool)
            J = np.zeros((nq, nq))
            for j in range(nq):
                step = hrel * (abs(C[j]) + 1e-10)
                Cp = C.copy(); Cp[j] += step
                Cm = C.copy(); Cm[j] -= step
                J[:, j] = (fast_rhs(Cp, svals, e_pool) - fast_rhs(Cm, svals, e_pool)) / (2 * step)
            return g0, J

        def flux_scale(C, svals, e_pool):
            """production-side scale for normalization (never divide by net)."""
            e0 = e_pool - C.sum()
            env = dict(svals); env[enz] = e0
            for i, sp in enumerate(complexes):
                env[sp] = C[i]
            tot = 0.0
            for rid in pool_rids:
                r = rx_by[rid]
                env["k1"] = r["k1"]
                v = eval(r["code"], {"__builtins__": {}}, env)
                for s, c in r["net"].items():
                    if s in cidx and c > 0:
                        tot += abs(v * c)
            return max(tot, 1e-30)

        samples = [0, len(traj) // 4, len(traj) // 2, 3 * len(traj) // 4, len(traj) - 1]
        for si in samples:
            print("[qssa] %s sample %d (t=%.3e)" % (enz, si, ts[si]), flush=True)
            st = traj[si]
            e_pool = st[enz] + sum(st[c] for c in complexes)
            svals = {k: v for k, v in st.items() if k not in pool_set}
            Cref = np.array([st[c] for c in complexes])

            # spectrum of the closed fast block at the reference state
            _, J = GJ(Cref, svals, e_pool)
            w = np.linalg.eigvals(J)
            for mode in np.argsort(-np.abs(w)):
                lam = w[mode]
                spec_rows.append(OrderedDict([
                    ("enzyme", enz), ("time_s", "%.4e" % ts[si]),
                    ("mode", int(mode)),
                    ("re_lambda_s^-1", "%.6e" % lam.real),
                    ("im_lambda_s^-1", "%.6e" % lam.imag),
                    ("abs_lambda_s^-1", "%.6e" % abs(lam)),
                    ("class_at_reference",
                     "attracting_stiff" if lam.real < -1e2 else
                     ("repelling_or_neutral_numerical" if lam.real > 1e-3 else
                      "near_zero_structural_candidate")),
                ]))

            # ---- algebraic closure: damped projected Newton, multiple starts ---- #
            print("[qssa]   spectrum done", flush=True)
            starts = OrderedDict([
                ("all_zero", np.zeros(nq)),
                ("uniform_half_pool", np.full(nq, 0.5 * e_pool / nq)),
                ("reference_shape/10", np.maximum(Cref, 1e-12) * 0.1),
            ])
            sols = []
            for tag, Cstart in starts.items():
                print("[qssa]     newton %s" % tag, flush=True)
                Cc = Cstart.copy()
                converged = False
                for _ in range(300):
                    g, Jc = GJ(Cc, svals, e_pool)
                    try:
                        dCn = np.linalg.solve(Jc, -g)
                    except np.linalg.LinAlgError:
                        break
                    alpha = 1.0
                    while alpha > 1e-10:
                        trial = Cc + alpha * dCn
                        if trial.min() >= -1e-15 and trial.sum() <= e_pool * (1 + 1e-12):
                            break
                        alpha *= 0.5
                    if alpha <= 1e-10:
                        break
                    Cc = np.maximum(Cc + alpha * dCn, 0.0)
                    g2, _ = GJ(Cc, svals, e_pool)
                    if np.max(np.abs(g2)) <= 1e-10 * flux_scale(Cc, svals, e_pool):
                        converged = True
                        break
                gfin, Jfin = GJ(Cc, svals, e_pool)
                res = float(np.max(np.abs(gfin)))
                sc = flux_scale(Cc, svals, e_pool)
                feasible = bool(Cc.min() >= -1e-14 and Cc.sum() <= e_pool * (1 + 1e-9))
                cond = float(np.linalg.cond(Jfin)) if Jfin.size else float("nan")
                sols.append(dict(tag=tag, C=Cc.copy(), res=res, sc=sc,
                                 scaled=res / sc, feasible=feasible,
                                 converged=converged, cond=cond))
            feas = [s for s in sols if s["feasible"] and s["converged"]]
            spread = float("nan")
            if len(feas) >= 2:
                spread = max(float(np.max(np.abs(a["C"] - b["C"]))) / max(e_pool, 1e-30)
                             for i, a in enumerate(feas) for b in feas[i + 1:])
            closure_rows.append(OrderedDict([
                ("enzyme", enz), ("time_s", "%.4e" % ts[si]),
                ("e_pool_uM", "%.10e" % e_pool),
                ("n_starts", len(sols)),
                ("n_converged_feasible", len(feas)),
                ("max_scaled_residual", "%.3e" % max((s["scaled"] for s in feas), default=float("nan"))),
                ("pairwise_start_spread_norm", "%.3e" % spread if spread == spread else "nan"),
                ("worst_cond_Jq", "%.3e" % max((s["cond"] for s in feas), default=float("nan"))),
                ("distance_to_reference_shape_norm",
                 "%.3e" % min((float(np.max(np.abs(s["C"] - Cref)) / max(e_pool, 1e-30)) for s in feas),
                              default=float("nan"))),
                ("free_enzyme_at_branch_uM",
                 "%.6e" % (e_pool - feas[0]["C"].sum()) if feas else "nan"),
            ]))

            # ---- frozen-slow relaxation toward the branch ---- #
            print("[qssa]   closure done: conv_feas=%d" % len(feas), flush=True)
            if feas:
                Cstar = feas[0]["C"]
                for pname, Cstart in (
                        ("x10_ref_shape", np.clip(Cref * 10.0, 1e-12, None)),
                        ("x0.1_ref_shape", np.clip(Cref * 0.1, 1e-12, None)),
                        ("uniform_0.5E_pool", np.full(nq, 0.5 * e_pool / nq))):
                    Cstart = Cstart * min(1.0, 0.99 * e_pool / Cstart.sum())
                    print("[qssa]     relax %s start" % pname, flush=True)
                    g0 = fast_rhs(Cstart, svals, e_pool)

                    def relax_fail(pname_, flag_):
                        return OrderedDict(
                            ("enzyme", enz), ("time_s", "%.4e" % ts[si]),
                            ("perturbation", pname_), ("success", "false"),
                            ("rel_dist_at_t_end", "nan"), ("t_to_1pct_s", "nan"),
                            ("slowest_attracting_lambda", "nan"),
                            ("fastest_attracting_lambda", "nan"),
                            ("tau_from_slowest_attracting_s", "nan"),
                            ("flags", flag_))
                    if not np.all(np.isfinite(g0)):
                        print("[qssa]     relax %s SKIPPED: non-finite rhs"
                              % pname, flush=True)
                        relax_rows.append(relax_fail(pname, "non_finite_fast_rhs"))
                        continue
                    # smooth RHS (no max() kink); transient negativity, if any,
                    # is REPORTED below, never clipped away
                    sol = solve_ivp(lambda t_, y_: fast_rhs(y_, svals, e_pool),
                                    [0.0, 10.0], Cstart, method="BDF",
                                    rtol=1e-8, atol=1e-14)
                    print("[qssa]     relax %s done nfev=%d t=%g" % (pname, sol.nfev, sol.t[-1] if sol.t.size else -1), flush=True)
                    if not sol.success:
                        relax_rows.append(relax_fail(pname, "solver_failed"))
                        continue
                    Cend = np.maximum(sol.y[:, -1], 0.0)
                    d0 = float(np.max(np.abs(Cstart - Cstar)))
                    t1 = float("nan")
                    for k in range(sol.y.shape[1]):
                        if np.max(np.abs(sol.y[:, k] - Cstar)) <= 0.01 * d0:
                            t1 = float(sol.t[k])
                            break
                    wq = np.linalg.eigvals(GJ(Cstar, svals, e_pool)[1])
                    attract = wq[wq.real < -1e-6]
                    lam_slow = float(attract.real.max()) if attract.size else float("nan")
                    lam_fast = float(wq.real.min()) if wq.size else float("nan")
                    relax_rows.append(OrderedDict([
                        ("enzyme", enz), ("time_s", "%.4e" % ts[si]),
                        ("perturbation", pname), ("success", "true"),
                        ("rel_dist_at_t_end", "%.3e" % (float(np.max(np.abs(Cend - Cstar))) / max(e_pool, 1e-30))),
                        ("t_to_1pct_s", "%.3e" % t1 if t1 == t1 else "nan"),
                        ("slowest_attracting_lambda", "%.3e" % lam_slow if lam_slow == lam_slow else "nan"),
                        ("fastest_attracting_lambda", "%.3e" % lam_fast if lam_fast == lam_fast else "nan"),
                        ("tau_from_slowest_attracting_s",
                         "%.3e" % (1.0 / abs(lam_slow)) if lam_slow == lam_slow else "nan"),
                        ("flags", "min_C_%.2e" % float(sol.y.min())),
                    ]))

        # ---- per-complex instantaneous closure defect along the FULL
        # reference trajectory (frozen-slow): dC_i/dt of the author model at
        # each reference state, normalized by that complex's own production
        # scale (never by net flux). This is the per-state QSS evidence. ---- #
        for si in range(len(traj)):
            st = traj[si]
            e_pool = st[enz] + sum(st[c] for c in complexes)
            svals = {k: v for k, v in st.items() if k not in pool_set}
            Cref = np.array([st[c] for c in complexes])
            d_ref = fast_rhs(Cref, svals, e_pool)
            env = dict(svals)
            env[enz] = e_pool - Cref.sum()
            for i, sp in enumerate(complexes):
                env[sp] = Cref[i]
            prod_i = np.zeros(nq)
            for rid in pool_rids:
                r = rx_by[rid]
                env["k1"] = r["k1"]
                v = eval(r["code"], {"__builtins__": {}}, env)
                for s, c in r["net"].items():
                    if s in cidx and c > 0:
                        prod_i[cidx[s]] += abs(v) * c
            for i, sp in enumerate(complexes):
                defect_rows.append(OrderedDict([
                    ("enzyme", enz), ("time_s", "%.4e" % ts[si]),
                    ("complex", sp),
                    ("C_ref_uM", "%.6e" % Cref[i]),
                    ("occ_frac_pool", "%.3e" % (Cref[i] / max(e_pool, 1e-30))),
                    ("prod_scale_uM_s", "%.6e" % prod_i[i]),
                    ("abs_defect_uM_s", "%.6e" % abs(d_ref[i])),
                    ("rel_defect_vs_prod_scale",
                     "%.3e" % (abs(d_ref[i]) / prod_i[i]) if prod_i[i] > 0.0
                     else "no_production_pathway"),
                ]))

    # ------------------------------------------------------------------ #
    def wcsv(fn, rows):
        path = os.path.join(AUDIT, fn)
        if not rows:
            open(path, "w").close()
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    wcsv("aminoacylation_v1_qssa_structure.csv", struct_rows)
    wcsv("aminoacylation_v1_qssa_spectrum.csv", spec_rows)
    wcsv("aminoacylation_v1_qssa_closure.csv", closure_rows)
    wcsv("aminoacylation_v1_qssa_relaxation.csv", relax_rows)
    wcsv("aminoacylation_v1_qssa_defect.csv", defect_rows)

    # per-complex defect summary over the whole reference trajectory
    per_c = {}
    for r in defect_rows:
        key = (r["enzyme"], r["complex"])
        d = (None if r["rel_defect_vs_prod_scale"] == "no_production_pathway"
             else float(r["rel_defect_vs_prod_scale"]))
        e = float(r["occ_frac_pool"])
        v = per_c.setdefault(key, {"dmax": 0.0, "dmax_t": None, "emax": 0.0})
        if d is not None and d >= v["dmax"]:
            v["dmax"], v["dmax_t"] = d, r["time_s"]
        v["emax"] = max(v["emax"], e)
    defect_summary = OrderedDict()
    for (enz_, cpx), v in per_c.items():
        defect_summary.setdefault(enz_, OrderedDict())[cpx] = OrderedDict([
            ("max_rel_defect_vs_own_production", "%.3e" % v["dmax"]),
            ("at_time_s", v["dmax_t"]),
            ("max_occupancy_frac_pool", "%.3e" % v["emax"]),
        ])

    derivation = OrderedDict([
        ("schema", "pnas2017_aminoacylation_v1_qssa_derivation/v1"),
        ("candidate", "A3a: selective enzyme-bound-complex QSSA; free MetAMP/"
                      "GlyAMP retained dynamic; free enzyme reconstructed from the "
                      "proved active-pool total (exact, not a state elimination)"),
        ("reference_trajectory", TIGHT_REL),
        ("per_enzyme", OrderedDict([
            (e["enzyme"], {k: v for k, v in e.items() if k != "enzyme"})
            for e in struct_rows])),
        ("closure", [dict(r) for r in closure_rows]),
        ("relaxation", [dict(r) for r in relax_rows]),
        ("per_complex_defect_summary", defect_summary),
        ("note_near_zero_modes",
         "near-zero eigenvalues are only classified structural after the "
         "explicit invariant/component analysis above supports it; otherwise "
         "they are reported as unresolved slow modes of the candidate fast block"),
    ])
    with open(os.path.join(AUDIT, "aminoacylation_v1_qssa_derivation.json"),
              "w", newline="\n", encoding="utf-8") as f:
        json.dump(derivation, f, indent=2)
        f.write("\n")

    for r in struct_rows:
        print(r["enzyme"], "components:", r["n_connected_components_active"],
              "invariants:", r["n_invariants_active_subnetwork"],
              "ones_inv:", r["ones_vector_is_invariant"])
    print("closure rows:")
    for r in closure_rows:
        print(" ", r["enzyme"], "t=", r["time_s"], "conv_feas=", r["n_converged_feasible"],
              "res=", r["max_scaled_residual"], "spread=", r["pairwise_start_spread_norm"],
              "dist_to_ref=", r["distance_to_reference_shape_norm"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
