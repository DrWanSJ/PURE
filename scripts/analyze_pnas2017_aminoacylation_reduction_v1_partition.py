"""A3a partition verification (v1).

Given the evidence-derived candidate partition (docs/audit/.../
candidate_partition.json), verify that the RESTRICTED algebraic block
(21 eliminated complexes; 7 enzyme-bound complexes kept dynamic) still
closes well-posedly:
  * per-sample multi-start damped projected Newton on the eliminated
    block only, with the kept complexes frozen at their reference values
    (frozen-slow semantics identical to the full-block derivation),
  * spectrum of the eliminated-block Jacobian (attractivity),
  * frozen-slow relaxation of the eliminated block from 3 perturbations.

Row definition matches run_pnas2017_aa_v1_formal.m reduced mode exactly:
algebraic row i is 0 = dC_i/dt of the AUTHOR RHS, restricted to
eliminated species. Helper loaders/parsers are imported from the
derivation script so no scientific definition is restated here.
"""
import ast
import csv
import json
import os
import sys
from collections import OrderedDict

import numpy as np
from scipy.integrate import solve_ivp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import analyze_pnas2017_aminoacylation_reduction_v1_qssa as q  # noqa: E402

AUDIT = q.AUDIT
PARTITION = os.path.join(ROOT, "docs", "audit",
                         "pnas2017_aminoacylation_reduction_v1",
                         "candidate_partition.json")


def main():
    part = json.load(open(PARTITION, encoding="utf-8"))
    reactions = q.load_rows(os.path.join(AUDIT, "reactions.csv"))
    parameters = q.load_rows(os.path.join(AUDIT, "parameters.csv"))
    pmap = {}
    for p in parameters:
        try:
            pmap[(p["reaction_id"], p["parameter_id"])] = float(p["author_export_value"])
        except (ValueError, TypeError):
            pmap[(p["reaction_id"], p["parameter_id"])] = float("nan")
    rx_all = []
    for r in reactions:
        nv = q.net_vector(q.parse_side(r["reactants"]), q.parse_side(r["products"]))
        rx_all.append(dict(id=r["id"], net=nv,
                           k1=pmap.get((r["id"], "k1"), float("nan")),
                           code=q.compile_rate(r["rate_law"]),
                           names={n.id for n in ast.walk(
                               ast.parse(r["rate_law"], mode="eval"))
                                 if isinstance(n, ast.Name)} - {"k1"}))
    rx_by = {r["id"]: r for r in rx_all}

    names_t = [l.strip() for l in open(os.path.join(ROOT, q.NAMES_REL))]
    T = np.loadtxt(os.path.join(ROOT, q.TIGHT_REL), delimiter=",",
                   usecols=range(242), skiprows=1)
    ts = T[:, 0]
    traj = [dict(zip(names_t, row)) for row in T[:, 1:]]

    closure_rows, spec_rows, relax_rows = [], [], []
    verdict_ok = True

    for enz in ("MetRS", "GlyRS"):
        all_complexes = sorted(s for s in names_t if s.startswith(enz + "_")
                               and not s.endswith("_degraded"))
        E = [c for c in all_complexes if c in set(part[enz]["eliminated"])]
        K = [c for c in all_complexes if c not in set(part[enz]["eliminated"])]
        assert len(E) + len(K) == len(all_complexes) and E and K
        pool_set = {enz} | set(all_complexes)
        cidx = {s: i for i, s in enumerate(E)}
        nq = len(E)
        pool_rids = [r["id"] for r in rx_all if set(r["net"]) & pool_set]
        print("[part] %s: eliminate %d, keep %d dynamic" % (enz, nq, len(K)))

        def fast_rhs_E(Ce, Kvals, svals, e_pool):
            env = dict(svals)
            env[enz] = e_pool - Ce.sum() - sum(Kvals.values())
            for i, sp in enumerate(E):
                env[sp] = Ce[i]
            for sp, v in Kvals.items():
                env[sp] = v
            dC = np.zeros(nq)
            for rid in pool_rids:
                r = rx_by[rid]
                env["k1"] = r["k1"]
                v = eval(r["code"], {"__builtins__": {}}, env)
                for s, c in r["net"].items():
                    if s in cidx:
                        dC[cidx[s]] += v * c
            return dC

        def GJ_E(Ce, Kvals, svals, e_pool, hrel=1e-7):
            g0 = fast_rhs_E(Ce, Kvals, svals, e_pool)
            J = np.zeros((nq, nq))
            for j in range(nq):
                step = hrel * (abs(Ce[j]) + 1e-10)
                Cp = Ce.copy(); Cp[j] += step
                Cm = Ce.copy(); Cm[j] -= step
                J[:, j] = (fast_rhs_E(Cp, Kvals, svals, e_pool)
                           - fast_rhs_E(Cm, Kvals, svals, e_pool)) / (2 * step)
            return g0, J

        def prod_scale_E(Ce, Kvals, svals, e_pool):
            env = dict(svals)
            env[enz] = e_pool - Ce.sum() - sum(Kvals.values())
            for i, sp in enumerate(E):
                env[sp] = Ce[i]
            for sp, v in Kvals.items():
                env[sp] = v
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
            st = traj[si]
            e_pool = st[enz] + sum(st[c] for c in all_complexes)
            svals = {k: v for k, v in st.items() if k not in pool_set}
            Kvals = {c: st[c] for c in K}
            Eref = np.array([st[c] for c in E])
            eK = e_pool - sum(Kvals.values())  # free + eliminated capacity

            starts = OrderedDict([
                ("all_zero", np.zeros(nq)),
                ("uniform_half", np.full(nq, 0.5 * max(eK, 0.0) / nq)),
                ("reference_shape/10", np.maximum(Eref, 0.0) * 0.1),
            ])
            sols = []
            for tag, C0 in starts.items():
                Cc = C0.copy()
                converged = False
                for _ in range(300):
                    g, Jc = GJ_E(Cc, Kvals, svals, e_pool)
                    try:
                        dCn = np.linalg.solve(Jc, -g)
                    except np.linalg.LinAlgError:
                        break
                    alpha = 1.0
                    while alpha > 1e-10:
                        trial = Cc + alpha * dCn
                        if trial.min() >= -1e-15 and trial.sum() <= eK * (1 + 1e-12):
                            break
                        alpha *= 0.5
                    if alpha <= 1e-10:
                        break
                    Cc = np.maximum(Cc + alpha * dCn, 0.0)
                    g2, _ = GJ_E(Cc, Kvals, svals, e_pool)
                    if np.max(np.abs(g2)) <= 1e-10 * prod_scale_E(Cc, Kvals, svals, e_pool):
                        converged = True
                        break
                gfin, Jfin = GJ_E(Cc, Kvals, svals, e_pool)
                res = float(np.max(np.abs(gfin)))
                sc = prod_scale_E(Cc, Kvals, svals, e_pool)
                feasible = bool(Cc.min() >= -1e-14 and Cc.sum() <= eK * (1 + 1e-9))
                cond = float(np.linalg.cond(Jfin)) if Jfin.size else float("nan")
                sols.append(dict(tag=tag, C=Cc.copy(), res=res / sc,
                                 feasible=feasible, converged=converged, cond=cond))
            feas = [s for s in sols if s["feasible"] and s["converged"]]
            spread = float("nan")
            if len(feas) >= 2:
                spread = max(float(np.max(np.abs(a["C"] - b["C"]))) / max(e_pool, 1e-30)
                             for i, a in enumerate(feas) for b in feas[i + 1:])
            # per-complex branch vs reference distance at this sample
            if feas:
                dist_vec = np.abs(feas[0]["C"] - Eref) / max(e_pool, 1e-30)
                worst_i = int(np.argmax(dist_vec))
            else:
                dist_vec = np.full(nq, np.nan)
                worst_i = -1
            # well-posedness of the restricted algebraic block: existence,
            # start-agreement, residual, invertibility. Branch-vs-reference
            # distance is judged SEPARATELY and only outside the initial
            # layer window [t0, t0 + 5*tau_fast] (acceptance_criteria rule).
            ok = (len(feas) >= 1 and (len(feas) < 2 or spread <= 1e-10)
                  and max((s["res"] for s in feas), default=1.0) <= 1e-10
                  and np.isfinite(np.linalg.cond(GJ_E(feas[0]["C"], Kvals, svals,
                                                      e_pool)[1])))
            verdict_ok = verdict_ok and ok
            sample_row = OrderedDict([
                ("enzyme", enz), ("time_s", "%.4e" % ts[si]),
                ("e_pool_uM", "%.10e" % e_pool),
                ("n_eliminated", nq), ("n_starts", len(sols)),
                ("n_converged_feasible", len(feas)),
                ("max_scaled_residual", "%.3e" % max((s["res"] for s in feas),
                                                     default=float("nan"))),
                ("pairwise_start_spread_norm", "%.3e" % spread if spread == spread else "nan"),
                ("worst_cond_Jelim", "%.3e" % max((s["cond"] for s in feas),
                                                  default=float("nan"))),
                ("max_branch_vs_reference_dist", "%.3e" % np.nanmax(dist_vec)),
                ("worst_complex", E[worst_i] if worst_i >= 0 else "nan"),
                ("block_well_posed", str(bool(ok)).lower()),
                ("initial_layer_window", "pending"),
                ("ref_match_outside_layer", "pending"),
            ])
            closure_rows.append(sample_row)

            # spectrum at branch
            if feas:
                _, Jb = GJ_E(feas[0]["C"], Kvals, svals, e_pool)
                w = np.linalg.eigvals(Jb)
                re_min_att = np.nan
                for lam in w:
                    spec_rows.append(OrderedDict([
                        ("enzyme", enz), ("time_s", "%.4e" % ts[si]),
                        ("re_lambda", "%.6e" % lam.real),
                        ("im_lambda", "%.6e" % lam.imag),
                        ("class", "attracting" if lam.real < -1e-6 else
                         ("neutral_or_repelling" if lam.real > 1e-6 else "near_zero")),
                    ]))
                att = w[w.real < -1e-6]
                nz = w[np.abs(w.real) <= 1e-6]
                rp = w[w.real > 1e-6]
                print("[part]   t=%.3e feas=%d spread=%.2e eig: att=%d nz=%d rep=%d"
                      " maxdist=%.2e %s" % (
                          ts[si], len(feas), spread, att.size, nz.size, rp.size,
                          np.nanmax(dist_vec), "OK" if ok else "NOT_OK"), flush=True)

                # ---- relaxation of the eliminated block (K frozen) ---- #
                Cstar = feas[0]["C"]
                cap = max(e_pool - sum(Kvals.values()), 1e-30)
                for pname, C0 in (
                        ("x10_ref_shape", np.clip(Eref * 10.0, 1e-12, None)),
                        ("x0.1_ref_shape", np.clip(Eref * 0.1, 1e-12, None)),
                        ("uniform_0.5cap", np.full(nq, 0.5 * cap / nq))):
                    C0 = C0 * min(1.0, 0.99 * cap / C0.sum())
                    g0 = fast_rhs_E(C0, Kvals, svals, e_pool)
                    if not np.all(np.isfinite(g0)):
                        relax_rows.append(OrderedDict([
                            ("enzyme", enz), ("time_s", "%.4e" % ts[si]),
                            ("perturbation", pname), ("success", "false"),
                            ("rel_dist_at_t_end", "nan"), ("t_to_1pct_s", "nan"),
                            ("min_C_along_run", "nan"),
                            ("flags", "non_finite_fast_rhs")]))
                        verdict_ok = False
                        continue
                    sol = solve_ivp(lambda t_, y_: fast_rhs_E(y_, Kvals, svals, e_pool),
                                    [0.0, 10.0], C0, method="BDF",
                                    rtol=1e-8, atol=1e-14)
                    d0 = float(np.max(np.abs(C0 - Cstar)))
                    t1 = float("nan")
                    if sol.success and d0 <= 1e-12 * e_pool:
                        t1 = 0.0   # started on the branch within layer noise
                    elif sol.success and d0 > 0:
                        for k in range(sol.y.shape[1]):
                            if np.max(np.abs(sol.y[:, k] - Cstar)) <= 0.01 * d0:
                                t1 = float(sol.t[k])
                                break
                    rdist = (float(np.max(np.abs(np.maximum(sol.y[:, -1], 0.0) - Cstar)))
                             / max(e_pool, 1e-30)) if sol.y.size else float("nan")
                    ok_r = bool(sol.success) and (t1 == t1) and rdist <= 1e-6
                    verdict_ok = verdict_ok and ok_r
                    relax_rows.append(OrderedDict([
                        ("enzyme", enz), ("time_s", "%.4e" % ts[si]),
                        ("perturbation", pname),
                        ("success", str(bool(sol.success)).lower()),
                        ("rel_dist_at_t_end", "%.3e" % rdist),
                        ("t_to_1pct_s", "%.3e" % t1 if t1 == t1 else "nan"),
                        ("min_C_along_run", "%.3e" % float(sol.y.min())),
                        ("flags", "" if ok_r else "no_1pct_convergence")]))

    # ---- backfill verdicts: initial-layer window from the RESTRICTED
    # spectrum (tau = 1/|slowest attracting lambda|, max over samples), and
    # post-layer branch-vs-reference match at <= 0.01 (T_F screen scale) ---- #
    taus = {}
    for enz in ("MetRS", "GlyRS"):
        re_att = [float(r["re_lambda"]) for r in spec_rows
                  if r["enzyme"] == enz and r["class"] == "attracting"]
        bad = [r for r in spec_rows if r["enzyme"] == enz
               and r["class"] != "attracting"]
        if not re_att or bad:
            verdict_ok = False
            print("[part] %s: spectrum not fully attracting (%d bad)"
                  % (enz, len(bad)))
        taus[enz] = (-1.0 / max(re_att)) if re_att else float("inf")
    verdict_match = True
    for r in closure_rows:
        t_ = float(r["time_s"])
        in_layer = t_ < 5.0 * taus[r["enzyme"]]
        r["initial_layer_window"] = str(bool(in_layer)).lower()
        match = float(r["max_branch_vs_reference_dist"]) <= 0.01
        r["ref_match_outside_layer"] = ("not_scored_in_layer" if in_layer
                                        else str(match).lower())
        if not in_layer and not match:
            verdict_match = False
    print("[part] restricted-block tau_fast_s:",
          {k: "%.2e" % v for k, v in taus.items()},
          "| post-layer branch-ref match:", verdict_match)

    def wcsv(fn, rows):
        path = os.path.join(AUDIT, fn)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    wcsv("aminoacylation_v1_partition_closure.csv", closure_rows)
    wcsv("aminoacylation_v1_partition_spectrum.csv", spec_rows)
    wcsv("aminoacylation_v1_partition_relaxation.csv", relax_rows)

    out = OrderedDict([
        ("schema", "pnas2017_aminoacylation_v1_partition_verification/v1"),
        ("partition_file", "docs/audit/pnas2017_aminoacylation_reduction_v1/"
                           "candidate_partition.json"),
        ("eliminated_counts", {"MetRS": len(part["MetRS"]["eliminated"]),
                               "GlyRS": len(part["GlyRS"]["eliminated"])}),
        ("closure", [dict(r) for r in closure_rows]),
        ("relaxation", [dict(r) for r in relax_rows]),
        ("restricted_block_tau_fast_s", {k: float(v) for k, v in taus.items()}),
        ("restricted_block_attracting_all_samples", "see spectrum csv; flag below"),
        ("restricted_block_well_posed_and_relaxing", bool(verdict_ok)),
        ("post_layer_branch_matches_reference_le_0.01", bool(verdict_match)),
        ("restricted_block_mathematically_well_posed_on_reference_samples",
         bool(verdict_ok and verdict_match)),
    ])
    with open(os.path.join(AUDIT, "aminoacylation_v1_partition_verification.json"),
              "w", newline="\n", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("[part] restricted-block well-posed on all reference samples:",
          verdict_ok)
    return 0


if __name__ == "__main__":
    sys.exit(main())
