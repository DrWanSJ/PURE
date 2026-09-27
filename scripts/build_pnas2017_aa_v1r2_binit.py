#!/usr/bin/env python3
"""Build the v1r2 moiety-consistent initialization inventory basis B_init.

Mechanical derivation from the source data only (no expected answers encoded):

  1. per-species moiety contents (methionyl, glycyl, adenosine, phosphorus,
     tRNAfMetCAU token, tRNAGlyGCC token, MetRS enzyme, GlyRS enzyme) are
     solved from the 138-reaction aminoacylation ledger deltas in exact
     rational arithmetic, anchored on the free species;
  2. every solved content vector is verified against all 138 subsystem
     reaction deltas AND (for the rows that claim global scope) against the
     full 968-reaction author stoichiometry;
  3. B_init rows are assembled with semantic names; the movable columns (21
     eliminated complexes + the free pools the initializer may debit) are
     identified and the debit matrix M (delta = M @ C) is emitted;
  4. the fast-subsystem stoichiometric left nullspace is computed in exact
     arithmetic and every B_init row is classified;
  5. REGRESSION (Phase 2C): B_init applied to the recorded v1r1 RED-S0
     consistent-start state must independently reproduce the known phantom
     inventory; the script stops with a nonzero exit code if it cannot.

Outputs (machine-readable):
  docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2.json
  docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv
"""

import csv
import json
import sys
from fractions import Fraction
from itertools import product

import sympy

ROOT = __file__.rsplit("/", 1)[0].rsplit("\\", 1)[0] if "/" in __file__ or "\\" in __file__ else "."
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AUD = os.path.join(ROOT, "docs", "audit", "pnas2017_aminoacylation_reduction_v1")
MODEL_DIR = os.path.join(ROOT, "models", "pnas2017_full_reference", "original",
                         "simulate", "Simulate_fMGG_synthesis")
AUDIT_DIR = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")

MOIETIES = {
    "methionyl": "moiety_methionyl_delta",
    "glycyl": "moiety_glycyl_delta",
    "adenosine": "moiety_adenosine_delta",
    "phosphorus": "moiety_phosphorus_total_delta",
    "trna_fmet": "moiety_trna_fmet_delta",
    "trna_gly": "moiety_trna_gly_delta",
    "enzyme_metrs": "moiety_enzyme_metrs_delta",
    "enzyme_glyrs": "moiety_enzyme_glyrs_delta",
}

# anchors: content 1 on the free carrier of each moiety, 0 on the free
# carriers of the others (they are chemically distinct molecules)
ANCHORS = {
    "methionyl": {"Met": 1, "Gly": 0, "ATP": 0, "AMP": 0, "PPi": 0,
                  "tRNAfMetCAU": 0, "tRNAGlyGCC": 0, "MetRS": 0, "GlyRS": 0},
    "glycyl": {"Gly": 1, "Met": 0, "ATP": 0, "AMP": 0, "PPi": 0,
               "tRNAfMetCAU": 0, "tRNAGlyGCC": 0, "MetRS": 0, "GlyRS": 0},
    "adenosine": {"ATP": 1, "AMP": 1, "Met": 0, "Gly": 0, "PPi": 0,
                  "tRNAfMetCAU": 0, "tRNAGlyGCC": 0, "MetRS": 0, "GlyRS": 0},
    "phosphorus": {"ATP": 3, "AMP": 1, "PPi": 2, "Met": 0, "Gly": 0,
                   "tRNAfMetCAU": 0, "tRNAGlyGCC": 0, "MetRS": 0, "GlyRS": 0},
    "trna_fmet": {"tRNAfMetCAU": 1, "Met": 0, "Gly": 0, "ATP": 0, "AMP": 0,
                  "PPi": 0, "tRNAGlyGCC": 0, "MetRS": 0, "GlyRS": 0},
    "trna_gly": {"tRNAGlyGCC": 1, "Met": 0, "Gly": 0, "ATP": 0, "AMP": 0,
                 "PPi": 0, "tRNAfMetCAU": 0, "MetRS": 0, "GlyRS": 0},
    "enzyme_metrs": {"MetRS": 1, "GlyRS": 0, "Met": 0, "Gly": 0, "ATP": 0,
                     "AMP": 0, "PPi": 0, "tRNAfMetCAU": 0, "tRNAGlyGCC": 0},
    "enzyme_glyrs": {"GlyRS": 1, "MetRS": 0, "Met": 0, "Gly": 0, "ATP": 0,
                     "AMP": 0, "PPi": 0, "tRNAfMetCAU": 0, "tRNAGlyGCC": 0},
}


def load_species():
    with open(os.path.join(MODEL_DIR, "dat", "fMGG_synthesis_initial_values.csv")) as f:
        rows = list(csv.DictReader(f))
    names = [r["Name"] for r in rows]
    x0 = {r["Name"]: float(r["Value"]) for r in rows}
    return names, x0


def load_ledger():
    with open(os.path.join(AUDIT_DIR, "aminoacylation_v1_ledger.csv")) as f:
        return list(csv.DictReader(f))


def parse_side(s):
    """'GlyRS:1|Gly:1' or 'A:1,B:2' -> {species: coeff}"""
    out = {}
    for part in s.split("|"):
        for term in part.split(","):
            term = term.strip()
            if not term:
                continue
            sp, _, n = term.partition(":")
            out[sp.strip()] = out.get(sp.strip(), 0) + float(n or 1)
    return out


def solve_contents(ledger, species47, moiety_col, anchor):
    """Solve A m = delta in exact rationals with the anchor constraints."""
    rxns = []
    for r in ledger:
        rea = parse_side(r["reactants"])
        pro = parse_side(r["products"])
        rxns.append((rea, pro, Fraction(r[moiety_col])))
    cols = species47
    A = sympy.zeros(len(rxns), len(cols))
    b = sympy.zeros(len(rxns), 1)
    for i, (rea, pro, d) in enumerate(rxns):
        for sp, n in rea.items():
            A[i, cols.index(sp)] -= sympy.Integer(int(n))
        for sp, n in pro.items():
            A[i, cols.index(sp)] += sympy.Integer(int(n))
        b[i] = sympy.Integer(int(d))
    # anchor rows: content of anchored free species is fixed
    rows_anchor = []
    for sp, val in anchor.items():
        if sp in cols:
            e = sympy.zeros(1, len(cols))
            e[cols.index(sp)] = 1
            rows_anchor.append((e, sympy.Integer(val)))
    A2 = sympy.Matrix.vstack(A, sympy.Matrix([e for e, _ in rows_anchor]))
    b2 = sympy.Matrix.vstack(b, sympy.Matrix([[v] for _, v in rows_anchor]))
    sol = sympy.linsolve((A2, b2), sympy.symbols("m0:" + str(len(cols))))
    sols = list(sol)
    if not sols:
        raise RuntimeError(f"no solution for {moiety_col}")
    sol = sols[0]
    m = {sp: Fraction(str(sol[cols.index(sp)].evalf(20))) for sp in cols}
    # verify exactness against all 138 deltas
    worst = Fraction(0)
    for (rea, pro, d), _ in zip(rxns, range(len(rxns))):
        val = Fraction(0)
        for sp, n in rea.items():
            val -= m[sp] * Fraction(int(n))
        for sp, n in pro.items():
            val += m[sp] * Fraction(int(n))
        worst = max(worst, abs(val - d))
    if worst != 0:
        raise RuntimeError(f"{moiety_col}: content solve inconsistent, worst {worst}")
    # free-symbol DOF check: are the anchored contents uniquely determined?
    dof = len(sol.free_symbols)
    return m, dof


def global_token_check(names, content, ledger_reactions_full, active=None):
    """Check the row vector (content on 47 species, 0 elsewhere) against the
    FULL 968-reaction author stoichiometry; return the list of violating
    reactions with nonzero net content change.  Reactions with author k1 = 0
    never fire and are excluded when `active` (a set of indices) is given."""
    bad = []
    idx = {s: i for i, s in enumerate(names)}
    for j, (rid, rea, pro) in enumerate(ledger_reactions_full):
        if active is not None and j not in active:
            continue
        net = Fraction(0)
        for sp, n in rea.items():
            if sp in idx:
                net -= content.get(sp, Fraction(0)) * Fraction(int(n))
        for sp, n in pro.items():
            if sp in idx:
                net += content.get(sp, Fraction(0)) * Fraction(int(n))
        if net != 0:
            bad.append((rid, net))
    return bad


def main():
    names, x0 = load_species()
    ledger = load_ledger()
    species47 = sorted({sp for r in ledger
                        for side in ("reactants", "products")
                        for sp in parse_side(r[side])})
    missing = [s for s in species47 if s not in names]
    assert not missing, f"ledger species not in model: {missing}"

    # ---- 1. solve every moiety content vector -------------------------------
    contents, dofs = {}, {}
    for moi, col in MOIETIES.items():
        m, dof = solve_contents(ledger, species47, col, ANCHORS[moi])
        contents[moi] = m
        dofs[moi] = dof
        print(f"[contents] {moi:14s} dof_after_anchors={dof}")

    # ---- 2. load the registered eliminated set ------------------------------
    part = json.load(open(os.path.join(AUD, "candidate_partition_v1r1.json")))
    elim = part["eliminated_states"]
    assert len(elim) == 21
    scope = json.load(open(os.path.join(ROOT, "models", "pnas2017_full_reference",
                                        "audit", "aminoacylation_v1_comparison_scope.json")))
    scope_by_id = {g["id"]: g for g in scope["conservation"]}

    # cross-check the solved tRNA/enzyme contents against the scope lists.
    # The scope family lists (the declared T_G inventories) keep degraded
    # species inside the family (degradation moves the token to _degraded);
    # the ledger-delta solve treats degradation as destroying the intact-tRNA
    # moiety.  The two accountings may therefore differ ONLY on _degraded
    # species; on every non-degraded species they must agree.
    for moi, gid in (("trna_fmet", "tRNAfMetCAU_family_total"),
                     ("trna_gly", "tRNAGlyGCC_family_total"),
                     ("enzyme_metrs", "MetRS_moiety_total"),
                     ("enzyme_glyrs", "GlyRS_moiety_total")):
        scope_set = set(scope_by_id[gid]["species"])
        solved_set = {s for s in species47 if contents[moi][s] != 0}
        extra = solved_set - scope_set
        lack = {s for s in scope_set if s in species47} - solved_set
        # the ledger-delta enzyme moiety counts total enzyme protein (keeps
        # _degraded inside); the scope's active-enzyme pool does not.  The
        # tRNA delta-moiety destroys the token on degradation; the scope
        # family keeps _degraded inside.  In both directions the difference
        # is confined to _degraded species.
        assert all(s.endswith("_degraded") for s in extra | lack), \
            f"{moi}: scope/solved membership differ off _degraded: extra={extra} lack={lack}"

    # ---- 3. assemble B_init rows -------------------------------------------
    # movable columns: the 21 eliminated complexes + the free pools the
    # initializer may debit (AMP excluded: kept dynamic state, author value 0,
    # additional condition delta_AMP = 0 -- see binit JSON notes)
    movable_free = ["tRNAfMetCAU", "tRNAGlyGCC", "Met", "Gly", "ATP", "PPi"]
    movable = elim + movable_free

    rows_def = [
        # (row name, source of coefficients, forced class when not globally exact)
        # the four structural rows use the SCOPE's declared T_G inventory
        # lists verbatim (they are the registered conserved moieties); the
        # tRNA scope lists additionally keep _degraded species inside the
        # family, which the ledger-delta solve does not
        ("MetRS_total", ("scope", "MetRS_moiety_total"), "GLOBAL_MOIETY_ACCOUNTING"),
        ("GlyRS_total", ("scope", "GlyRS_moiety_total"), "GLOBAL_MOIETY_ACCOUNTING"),
        ("tRNAfMetCAU_total", ("scope", "tRNAfMetCAU_family_total"), None),
        ("tRNAGlyGCC_total", ("scope", "tRNAGlyGCC_family_total"), None),
        ("Met_total", ("solved", "methionyl"), None),
        ("Gly_total", ("solved", "glycyl"), None),
        ("adenine_moiety_total", ("solved", "adenosine"), None),
        ("declared_phosphate_equivalent_total", ("solved", "phosphorus"), None),
    ]

    # full 968-reaction stoichiometry for global classification, restricted to
    # reactions whose author k1 is nonzero (k = 0 rows never fire)
    with open(os.path.join(MODEL_DIR, "dat", "fMGG_synthesis_reactions.csv")) as f:
        rxn_rows = list(csv.DictReader(f))
    with open(os.path.join(MODEL_DIR, "dat", "fMGG_synthesis_parameters.csv")) as f:
        kvals = [float(r["Value"]) for r in csv.DictReader(f)]
    rxn_full = [(r["id"], parse_side(r["reactants"]), parse_side(r["products"]))
                for r in rxn_rows]
    active = {j for j, r in enumerate(rxn_rows)
              if kvals[int(r["id"][2:]) - 1] != 0.0}
    print(f"[stoich] active author reactions (k1 != 0): {len(active)}/{len(rxn_full)}")

    binit_rows = {}
    classification = {}
    for name, (src, key), forced in rows_def:
        if src == "scope":
            grp = scope_by_id[key]
            w = grp.get("weights") or {}
            row = {s: Fraction(w.get(s, 1)) for s in grp["species"]}
            for s in names:
                row.setdefault(s, Fraction(0))
        else:
            c = contents[key]
            row = {s: c.get(s, Fraction(0)) for s in names}
        binit_rows[name] = row
        classification[name] = {}
        # subsystem exactness: for scope rows verify against the 138 deltas
        # via the solved content on the 47 species (they agree off _degraded);
        # for solved rows it was verified inside solve_contents
        if src == "scope":
            sub_bad = []
            for r in ledger:
                rea, pro = parse_side(r["reactants"]), parse_side(r["products"])
                net = sum(Fraction(int(n)) * row.get(sp, Fraction(0)) for sp, n in pro.items()) \
                    - sum(Fraction(int(n)) * row.get(sp, Fraction(0)) for sp, n in rea.items())
                if net != 0:
                    sub_bad.append(r["reaction_id"])
            # the active-enzyme scope rows are violated by the enzyme
            # degradation reactions (enzyme leaves the active pool) -- that is
            # precisely why they classify as GLOBAL_MOIETY_ACCOUNTING with the
            # exact-by-reconstruction realization; the tRNA scope rows must be
            # subsystem-exact (degradation keeps the token in the family)
            if forced is None:
                assert not sub_bad, f"{name}: scope row violates subsystem deltas: {sub_bad}"
            classification[name]["subsystem_violations"] = len(sub_bad)
            classification[name]["subsystem_violating_reactions"] = sub_bad[:12]
        glob_bad = global_token_check(names, row, rxn_full, active)
        if not glob_bad:
            cls = "EXACT_FAST_SUBSYSTEM_INVARIANT_AND_GLOBAL"
        elif forced:
            cls = forced
        else:
            cls = "RESOURCE_ACCOUNTING_ONLY"
        classification[name] = {
            "class": cls,
            "global_violations": len(glob_bad),
            "global_violating_reactions": [rid for rid, _ in glob_bad][:12],
        }
        print(f"[B_init] {name:38s} {cls:42s} global_violations={len(glob_bad)}")

    # scope-guanine check row: coefficients 0 on every movable column
    guan = {s: Fraction(0) for s in names}
    for s in scope_by_id["guanine_ledger_total"]["species"]:
        guan[s] = Fraction(1)
    binit_rows["guanine_check_total"] = guan
    classification["guanine_check_total"] = {
        "class": "RESOURCE_ACCOUNTING_ONLY",
        "note": "verification-only row: no movable species carries guanine",
        "global_violations": 0}

    # ---- 4. fast-subsystem left nullspace (exact) ---------------------------
    S = sympy.zeros(len(species47), len(ledger))
    for j, r in enumerate(ledger):
        rea, pro = parse_side(r["reactants"]), parse_side(r["products"])
        for sp, n in rea.items():
            S[species47.index(sp), j] -= sympy.Integer(int(n))
        for sp, n in pro.items():
            S[species47.index(sp), j] += sympy.Integer(int(n))
    ns = S.T.nullspace()          # left nullspace of S
    L = sympy.Matrix.hstack(*ns).T
    print(f"[nullspace] left-nullspace(S_fast) dimension = {L.rows}")
    # express each B_init row in terms of the nullspace basis where possible
    for name, _src, _forced in rows_def:
        v = sympy.Matrix([[int(binit_rows[name][s]) for s in species47]])
        coeff = None
        if L.rows:
            sol = sympy.linsolve((L.T, v.T))
            its = list(sol)
            coeff = its[0] if its else None
        classification[name]["in_fast_subsystem_left_nullspace"] = bool(
            coeff is not None and all(c == 0 for c in v) or (coeff is not None))
        # direct verification: L * S^T row = 0 already by construction; verify
        # the row itself is conserved: v * S = 0 ?
        vs = v * S
        classification[name]["row_times_S_fast_is_zero"] = all(c == 0 for c in vs)

    # ---- 5. emit matrix + debit matrix M -----------------------------------
    out_csv = os.path.join(AUD, "binit_v1r2_matrix.csv")
    with open(out_csv, "w", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["row"] + names)
        for name, row in binit_rows.items():
            w.writerow([name] + [str(row[s]) for s in names])
    print(f"[emit] {out_csv}")

    M = {}   # debit row -> {eliminated complex: coefficient}  (delta = M C)
    # rows whose free-pool coefficient is 1 resolve directly:
    #   delta_pool = -sum_i B[row, elim_i] * C_i
    # the phosphate row is coupled to the adenine row through delta_ATP:
    #   adenine:   delta_ATP + sum_i a_i C_i = 0            (delta_AMP = 0)
    #   phosphate: 3 delta_ATP + 2 delta_PPi + sum_i w_i C_i = 0
    #   => delta_PPi = (3 aAde(C) - aPh(C)) / 2  = the PPi already RELEASED
    #      from the bare-adenylate eliminated complexes     [a CREDIT, >= 0]
    for name in ["tRNAfMetCAU_total", "tRNAGlyGCC_total", "Met_total",
                 "Gly_total", "adenine_moiety_total"]:
        row = binit_rows[name]
        M[name] = {e: -row[e] for e in elim if row[e] != 0}
    ade_row, pho_row = binit_rows["adenine_moiety_total"], \
        binit_rows["declared_phosphate_equivalent_total"]
    M["declared_phosphate_equivalent_total"] = {
        e: (3 * ade_row[e] - pho_row[e]) / 2
        for e in elim if (3 * ade_row[e] - pho_row[e]) != 0}
    # delta_AMP = 0 (additional condition), delta rows for the free pools:
    debit_map = {
        "tRNAfMetCAU_total": "tRNAfMetCAU",
        "tRNAGlyGCC_total": "tRNAGlyGCC",
        "Met_total": "Met",
        "Gly_total": "Gly",
        "adenine_moiety_total": "ATP",
        "declared_phosphate_equivalent_total": "PPi",
    }

    # ---- 6. Phase 2C regression against the v1r1 phantom -------------------
    smoke = os.path.join(ROOT, "results", "pnas2017_reference",
                         "2026-09-26_aa_v1r1_smoke", "RED-S0_smoke.csv")
    with open(smoke) as f:
        first = next(csv.DictReader(f))
    x_v1r1 = {s: float(first[s]) for s in names}
    regression = {}
    for name, row in binit_rows.items():
        full_v = sum(row[s] * x_v1r1[s] for s in names)
        auth_v = sum(row[s] * x0[s] for s in names)
        excess = full_v - auth_v
        rel = excess / auth_v if auth_v != 0 else None
        regression[name] = {"b_x_v1r1_t0": full_v, "b_x_author_t0": auth_v,
                            "excess": excess, "relative_excess": rel}
        print(f"[regress] {name:38s} excess={float(excess):+.6f} "
              f"rel={'' if rel is None else format(float(rel), '+.3e')}")

    # ---- 7. write JSON ------------------------------------------------------
    out = {
        "schema": "pnas2017_aa_v1r2_binit/v1",
        "created": "2026-09-26",
        "derivation": ("mechanical: per-species moiety contents solved in exact "
                       "rational arithmetic from the 138-reaction aminoacylation "
                       "ledger deltas with free-species anchors; verified against "
                       "all 138 subsystem deltas and, where classified global, "
                       "against the full 968-reaction author stoichiometry"),
        "moiety_solve_dof_after_anchors": dofs,
        "rows": {name: {"semantic_name": name,
                        "moiety": moi if moi else "guanine-scope-check",
                        "nonzero_species_count": sum(1 for s in names if binit_rows[name][s] != 0),
                        **classification[name]}
                 for name, moi, _ in rows_def + [("guanine_check_total", None, None)]},
        "movable_columns": movable,
        "movable_free_pools": movable_free,
        "additional_condition": ("delta_AMP = 0: free AMP is a kept dynamic state of the "
                                 "registered reduced formulation with author initial value 0; "
                                 "the adenine/phosphate token rows then determine delta_ATP = "
                                 "-(adenosine content of the eliminated complexes) and delta_PPi "
                                 "= (PPi content released from the eliminated complexes, i.e. the "
                                 "bare-adenylate complexes). The residual token-null direction "
                                 "(ATP +t, AMP -t, PPi -t) is excluded: t < 0 would debit free "
                                 "AMP below its author value 0 (infeasible), t > 0 would move a "
                                 "kept dynamic state off its registered initial condition."),
        "debit_matrix": {r: {"free_pool": debit_map[r], "coefficients": M[r]}
                         for r in M},
        "phase_2c_regression_v1r1_phantom": regression,
        "regression_verdict": None,
        "matrix_csv": "docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv",
    }
    # regression verdict: the known phantom signature must be reproduced
    r = regression
    ok = (abs(float(r["tRNAfMetCAU_total"]["excess"])) > 0.1
          and abs(float(r["tRNAGlyGCC_total"]["excess"])) > 0.1
          and abs(float(r["declared_phosphate_equivalent_total"]["excess"])) > 1.0
          and abs(float(r["MetRS_total"]["excess"])) < 1e-9
          and abs(float(r["GlyRS_total"]["excess"])) < 1e-9)
    out["regression_verdict"] = ("V1R1_PHANTOM_REPRODUCED" if ok
                                 else "V1R1_PHANTOM_NOT_REPRODUCED")
    out_path = os.path.join(AUD, "binit_v1r2.json")
    with open(out_path, "w", newline="\n") as f:
        json.dump(out, f, indent=2, default=str)
        f.write("\n")
    print(f"[emit] {out_path}")
    print(f"[verdict] {out['regression_verdict']}")
    if not ok:
        sys.exit(2)


if __name__ == "__main__":
    main()
