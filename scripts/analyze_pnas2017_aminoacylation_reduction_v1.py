#!/usr/bin/env python3
"""PNAS 2017 aminoacylation reduction v1 — STRUCTURE stage.

Addresses the v1 execution-prompt requirements:

  §IV.A  three-layer ledger semantics (free_species_delta / carrier_state_delta
         / conserved_moiety_delta) with known-answer tests;
  §IV.B  full-path audit of both synthetase routes against the SELECTED cycle
         (all routes with author k1, including k1 = 0 channels);
  §IV.C  reaction-ownership / replacement table over the full 968-reaction
         network (which reactions change candidate q, which external rates
         depend on candidate states, shared pools, multi-subsystem labels);
  §V     GlyAMP/MetAMP audit of the author trajectory (peak, producers,
         consumers, inventory contribution, enzyme-bound fractions).

Analysis-only: reads immutable committed artefacts, writes derived files.
NEVER modifies the canonical SBML, the author CSVs, or v0 artefacts.

Run:  python scripts/analyze_pnas2017_aminoacylation_reduction_v1.py structure
"""
import ast
import csv
import hashlib
import json
import math
import os
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")
SBML_REL = "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
SBML = os.path.join(ROOT, *SBML_REL.split("/"))
TRAJ_REL = "results/pnas2017_reference/2026-09-24_authors_model_v0/authors_model_trajectory.csv"
TRAJ = os.path.join(ROOT, *TRAJ_REL.split("/"))
AUTHOR_PARAM_REL = ("models/pnas2017_full_reference/original/simulate/"
                    "Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv")
AUTHOR_IC_REL = ("models/pnas2017_full_reference/original/simulate/"
                 "Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv")
P_ARM = "\n"


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
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


def net_vector(reactants, products):
    v = {}
    for k, c in reactants.items():
        v[k] = v.get(k, 0.0) - c
    for k, c in products.items():
        v[k] = v.get(k, 0.0) + c
    return {k: c for k, c in v.items() if abs(c) > 0.0}


_ALLOWED_NODES = (
    ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Store,
    ast.BinOp, ast.UnaryOp, ast.operator, ast.unaryop, ast.BoolOp, ast.boolop,
    ast.Compare, ast.cmpop,
)


def compile_rate(expr):
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ValueError("disallowed node %s in %r" % (type(node).__name__, expr))
    return compile(tree, "<rate>", "eval")


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_json(path, obj):
    with open(path, "w", newline=P_ARM, encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


# --------------------------------------------------------------------------- #
# composition model (DECLARED, with known-answer tests below)
# --------------------------------------------------------------------------- #
# A species name is compositional: either a bare component token, or an enzyme
# complex "MetRS_<tok>[_<tok>…]" / "GlyRS_<tok>[_<tok>…]".
NUC_TOKENS = {"ATP": 1, "AMP": 1, "MetAMP": 1, "GlyAMP": 1}       # adenosine carriers, 1 each
PPi_TOKENS = {"PPi"}
AA_TOKENS_GLY = {"Gly": 1, "GlyAMP": 1, "GlytRNAGlyGCC": 1}       # glycyl residue carriers
AA_TOKENS_MET = {"Met": 1, "MetAMP": 1, "MettRNAfMetCAU": 1}      # methionyl residue carriers
TRNA_TOKENS = {"tRNAGlyGCC": 1, "GlytRNAGlyGCC": 1,
               "tRNAfMetCAU": 1, "MettRNAfMetCAU": 1}             # tRNA backbone carriers
PHOSPHORUS = {"ATP": 3, "AMP": 1, "MetAMP": 1, "GlyAMP": 1, "PPi": 2}


def tokens_of(species):
    """Return the multiset of component tokens for a species name."""
    if species.endswith("_degraded"):
        return []                              # degraded sink: composition of the *sunk* species is
                                               # tracked at the parent pool, not via tokens here
    for enz in ("MetRS", "GlyRS"):
        if species == enz:
            return []
        if species.startswith(enz + "_"):
            return species[len(enz) + 1:].split("_")
    return [species]


def carrier_states_free():
    return None  # (reserved; membership resolved via carrier_members below)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    sbml_sha = hashlib.sha256(open(SBML, "rb").read()).hexdigest()

    reactions = load_rows(os.path.join(AUDIT, "reactions.csv"))
    parameters = load_rows(os.path.join(AUDIT, "parameters.csv"))
    pmap = {}
    for p in parameters:
        try:
            pmap[(p["reaction_id"], p["parameter_id"])] = float(p["author_export_value"])
        except (ValueError, TypeError):
            pmap[(p["reaction_id"], p["parameter_id"])] = float("nan")

    aa = [r for r in reactions if "Aminoacylation" in (r["subsystem_files"] or "")]
    aa_species = sorted({s for r in aa for s in net_vector(parse_side(r["reactants"]),
                                                            parse_side(r["products"]))})
    dyn_species = [s for s in aa_species if not s.endswith("_degraded")]

    # ---- carrier-state sets (free form + all bound states carrying it) ---- #
    def carries(species, token):
        return token in tokens_of(species)

    CARRIER = OrderedDict([
        # carrier chemical form -> its free species
        ("ATP", "ATP"), ("AMP", "AMP"), ("PPi", "PPi"),
        ("MetAMP", "MetAMP"), ("GlyAMP", "GlyAMP"),
        ("Met", "Met"), ("Gly", "Gly"),
        ("tRNAfMetCAU", "tRNAfMetCAU"), ("tRNAGlyGCC", "tRNAGlyGCC"),
        ("MettRNAfMetCAU", "MettRNAfMetCAU"), ("GlytRNAGlyGCC", "GlytRNAGlyGCC"),
    ])
    # bound-complex membership is by NAME TOKEN; residue carriers (Gly/Met) also
    # live inside the AA-AMP and aa-tRNA tokens, so their token set is wider.
    CARRIER_TOKENS = {
        "Gly": set(AA_TOKENS_GLY), "Met": set(AA_TOKENS_MET),
    }

    def carrier_members(carrier):
        tokens = CARRIER_TOKENS.get(carrier, {carrier})
        return [sp for sp in aa_species
                if sp == carrier or any(t in tokens for t in tokens_of(sp))]

    # ---- moiety count functions (declared inventories) ---- #
    def moiety_counts(species):
        toks = tokens_of(species)
        enz = "MetRS" if species.startswith("MetRS") else ("GlyRS" if species.startswith("GlyRS") else None)
        base = species[:-len("_degraded")] if species.endswith("_degraded") else species
        c = OrderedDict()
        c["adenosine"] = sum(NUC_TOKENS.get(t, 0) for t in toks) if not species.endswith("_degraded") else 0
        c["pyrophosphate_P"] = sum(2 for t in toks if t in PPi_TOKENS)
        c["phosphorus_total"] = sum(PHOSPHORUS.get(t, 0) for t in toks)
        c["glycyl"] = sum(AA_TOKENS_GLY.get(t, 0) for t in toks)
        c["methionyl"] = sum(AA_TOKENS_MET.get(t, 0) for t in toks)
        c["trna_gly"] = 1 if "tRNAGlyGCC" in toks or "GlytRNAGlyGCC" in toks else 0
        c["trna_fmet"] = 1 if "tRNAfMetCAU" in toks or "MettRNAfMetCAU" in toks else 0
        c["enzyme_metrs"] = 1 if (base == "MetRS" or base.startswith("MetRS_")) else 0
        c["enzyme_glyrs"] = 1 if (base == "GlyRS" or base.startswith("GlyRS_")) else 0
        return c

    MOIETY_KEYS = ["adenosine", "pyrophosphate_P", "phosphorus_total",
                   "glycyl", "methionyl", "trna_gly", "trna_fmet",
                   "enzyme_metrs", "enzyme_glyrs"]

    # ===================================================================== #
    # §IV.A  per-reaction three-layer ledger
    # ===================================================================== #
    ledger_rows = []
    rx_by_id = {}
    for r in aa:
        rct, prd = parse_side(r["reactants"]), parse_side(r["products"])
        nv = net_vector(rct, prd)
        rx_by_id[r["id"]] = (rct, prd, nv)
        row = OrderedDict([("reaction_id", r["id"]),
                           ("reactants", r["reactants"]), ("products", r["products"]),
                           ("k1_author", repr(pmap.get((r["id"], "k1"), float("nan")))),
                           ("active_at_reference", str(pmap.get((r["id"], "k1"), 0.0) != 0.0).lower())])
        for carrier, free_sp in CARRIER.items():
            members = carrier_members(carrier)
            free_delta = nv.get(free_sp, 0.0)
            carrier_delta = sum(nv.get(m, 0.0) for m in members)
            row["%s_free_delta" % carrier] = free_delta
            row["%s_carrier_delta" % carrier] = carrier_delta
        for moi in MOIETY_KEYS:
            row["moiety_%s_delta" % moi] = sum(nv.get(sp, 0.0) * moiety_counts(sp)[moi] for sp in nv)
        # signed net vs forward/reverse chemical roles (kept distinct per §IV.A)
        ledger_rows.append(row)
    write_csv(os.path.join(AUDIT, "aminoacylation_v1_ledger.csv"), ledger_rows)

    # ---- known-answer tests (§IV.A) ---- #
    def get(rid, col):
        for row in ledger_rows:
            if row["reaction_id"] == rid:
                return row[col]
        raise KeyError(rid)

    tests = OrderedDict()
    # T1 simple binding E + ATP -> E.ATP must NOT count as chemical consumption
    tests["T1_binding_E_ATP"] = dict(
        reaction="re0000000132",  # GlyRS + ATP -> GlyRS_ATP
        expect=dict(ATP_free_delta=-1.0, ATP_carrier_delta=0.0,
                    moiety_adenosine_delta=0.0, moiety_enzyme_glyrs_delta=0.0))
    # T2 true chemical adenylation inside the complex
    tests["T2_chemical_adenylation"] = dict(
        reaction="re0000000140",  # GlyRS_Gly_ATP -> GlyRS_GlyAMP_PPi
        expect=dict(ATP_free_delta=0.0, ATP_carrier_delta=-1.0,
                    PPi_carrier_delta=1.0, PPi_free_delta=0.0,
                    moiety_adenosine_delta=0.0, moiety_phosphorus_total_delta=0.0,
                    moiety_glycyl_delta=0.0, moiety_enzyme_glyrs_delta=0.0))
    # T3 PPi release from a complex: free rise, carrier total unchanged
    tests["T3_PPi_release"] = dict(
        reaction="re0000000127",  # GlyRS_GlyAMP_PPi -> GlyRS_GlyAMP + PPi
        expect=dict(PPi_free_delta=1.0, PPi_carrier_delta=0.0,
                    moiety_adenosine_delta=0.0, moiety_pyrophosphate_P_delta=0.0))
    # T4 transfer isomerization inside the enzyme
    tests["T4_transfer"] = dict(
        reaction="re0000000178",  # GlyRS_GlyAMP_tRNA -> GlyRS_AMP_GlytRNA
        expect=dict(moiety_glycyl_delta=0.0, moiety_adenosine_delta=0.0,
                    moiety_trna_gly_delta=0.0, moiety_pyrophosphate_P_delta=0.0,
                    GlyAMP_carrier_delta=-1.0, AMP_carrier_delta=1.0,
                    GlytRNAGlyGCC_carrier_delta=1.0))
    # T5 AMP release: free AMP rise, adenosine carrier total unchanged
    tests["T5_AMP_release"] = dict(
        reaction="re0000000145",  # GlyRS_AMP -> GlyRS + AMP (identity asserted below)
        expect=dict(AMP_free_delta=1.0, AMP_carrier_delta=0.0,
                    moiety_adenosine_delta=0.0, moiety_enzyme_glyrs_delta=0.0))
    test_rows = []
    all_ok = True
    for tname, spec in tests.items():
        rid = spec["reaction"]
        ok = True
        detail = {}
        for col, want in spec["expect"].items():
            got = get(rid, col)
            good = abs(got - want) < 1e-12
            detail[col] = dict(expected=want, got=got, ok=good)
            ok = ok and good
        # sanity: reaction side text matches the test description
        test_rows.append(OrderedDict([
            ("test", tname), ("reaction_id", rid),
            ("sides", "%s -> %s" % (rx_by_id[rid][0], rx_by_id[rid][1])),
            ("all_fields_ok", str(ok).lower()),
            ("detail", json.dumps(detail))]))
        all_ok = all_ok and ok
    # T5 identity check: re0000000145 must be GlyRS_AMP -> GlyRS + AMP
    t5 = rx_by_id["re0000000145"]
    assert "GlyRS_AMP" in t5[0] and "AMP" in t5[1], "T5 reaction identity changed: %s" % (t5,)

    # ---- mechanically-derived invariant table: every declared moiety, over ALL
    # 138 aa reactions (and separately over reference-active ones) ---- #
    invariants = OrderedDict()
    for moi in MOIETY_KEYS:
        viol_all = [row["reaction_id"] for row in ledger_rows
                    if abs(row["moiety_%s_delta" % moi]) > 1e-12]
        viol_act = [rid for rid in viol_all
                    if any(row["reaction_id"] == rid and row["active_at_reference"] == "true"
                           for row in ledger_rows)]
        invariants[moi] = OrderedDict([
            ("reactions_breaking_over_all_aa", viol_all),
            ("reactions_breaking_over_reference_active", viol_act),
            ("exact_conservation_over_all_aa", str(not viol_all).lower()),
        ])
    write_json(os.path.join(AUDIT, "aminoacylation_v1_ledger_tests.json"), OrderedDict([
        ("schema", "pnas2017_aminoacylation_v1_ledger_tests/v1"),
        ("source_sbml_sha256", sbml_sha),
        ("known_answer_tests", test_rows),
        ("all_known_answer_tests_pass", all_ok),
        ("moiety_invariants_derived", invariants),
        ("semantics_note",
         "free_species_delta = net stoich coefficient of the FREE species; "
         "carrier_state_delta = net change of that chemical form summed over free "
         "+ all bound complexes carrying it (binding never counts as consumption); "
         "moiety_delta = net change of the declared conserved group inventory. "
         "Cumulative/gross accounting downstream MUST use original directed fluxes, "
         "never |v_net| of merged pairs."),
    ]))

    # ===================================================================== #
    # §IV.B  full-path audit against the selected cycle
    # ===================================================================== #
    CYCLE = {
        "Gly": ["re0000000132", "re0000000134", "re0000000140", "re0000000207",
                "re0000000189", "re0000000178", "re0000000182", "re0000000145"],
        "Met": ["re0000000157", "re0000000159", "re0000000165", "re0000000249",
                "re0000000231", "re0000000220", "re0000000224", "re0000000170"],
    }
    all_touching = []          # every aa reaction with its routes
    for r in aa:
        rct, prd, nv = parse_side(r["reactants"]), parse_side(r["products"]), None
        nv = net_vector(rct, prd)
        sps = set(nv)
        pathway = "Gly" if any(s.startswith("GlyRS") or s in ("Gly", "GlyAMP", "tRNAGlyGCC", "GlytRNAGlyGCC") for s in sps) else \
                  ("Met" if any(s.startswith("MetRS") or s in ("Met", "MetAMP", "tRNAfMetCAU", "MettRNAfMetCAU") for s in sps) else "shared")
        in_cycle = r["id"] in CYCLE["Gly"] + CYCLE["Met"]
        k1 = pmap.get((r["id"], "k1"), float("nan"))
        # route classification
        if any(s.endswith("_degraded") and nv[s] > 0 for s in nv):
            route = "degradation_sink"
        elif (len(rct) == 1 and list(rct)[0] in ("MettRNAfMetCAU", "GlytRNAGlyGCC")
              and "tRNAfMetCAU" in prd and ("Met" in prd or "Gly" in prd)):
            route = "free_aa_tRNA_decharging"
        elif list(rct) in (["GlyAMP"], ["MetAMP"]) and "AMP" in prd:
            route = "free_adenylate_hydrolysis"
        elif set(rct) in ({"Gly", "AMP"}, {"Met", "AMP"}):
            route = "free_adenylate_synthesis"
        elif pathway == "shared":
            route = "shared_nucleotide_side"
        else:
            route = "enzyme_cycle_or_branch"
        all_touching.append(OrderedDict([
            ("reaction_id", r["id"]), ("pathway", pathway),
            ("in_selected_cycle", str(in_cycle).lower()),
            ("route_class", route),
            ("reactants", r["reactants"]), ("products", r["products"]),
            ("k1_author", repr(k1)),
            ("active_at_reference", str(k1 == k1 and k1 != 0.0).lower()),
            ("subsystem_files", r["subsystem_files"]),
        ]))
    write_csv(os.path.join(AUDIT, "aminoacylation_v1_path_audit.csv"), all_touching)

    # coverage summary: per pathway, reactions NOT in the selected cycle but active
    cov = OrderedDict()
    for pw in ("Gly", "Met"):
        pw_rxs = [r for r in all_touching if r["pathway"] == pw]
        cov[pw] = OrderedDict([
            ("n_reactions_total", len(pw_rxs)),
            ("n_in_selected_cycle", sum(1 for r in pw_rxs if r["in_selected_cycle"] == "true")),
            ("n_active_outside_selected_cycle", sum(1 for r in pw_rxs
                                                    if r["active_at_reference"] == "true"
                                                    and r["in_selected_cycle"] == "false")),
            ("outside_cycle_ids", [r["reaction_id"] for r in pw_rxs
                                   if r["active_at_reference"] == "true"
                                   and r["in_selected_cycle"] == "false"]),
            ("inactive_channels_present_k1_zero", [r["reaction_id"] for r in pw_rxs
                                                   if r["active_at_reference"] == "false"
                                                   and r["route_class"] in
                                                   ("free_aa_tRNA_decharging", "degradation_sink",
                                                    "free_adenylate_hydrolysis",
                                                    "free_adenylate_synthesis")]),
        ])
    # ===================================================================== #
    # §IV.C  ownership / replacement table over the FULL 968-reaction network
    # ===================================================================== #
    aa_id_set = set(r["id"] for r in aa)
    aa_dyn_set = set(dyn_species)
    own_rows = []
    for r in reactions:
        rct, prd = parse_side(r["reactants"]), parse_side(r["products"])
        touched = (set(rct) | set(prd)) & aa_dyn_set
        multi = "|" in (r["subsystem_files"] or "")
        own = "aminoacylation_replacement_set" if r["id"] in aa_id_set else \
              ("external_touches_aa" if touched else "external_independent")
        if r["id"] not in aa_id_set and touched:
            own_rows.append(OrderedDict([
                ("reaction_id", r["id"]),
                ("ownership", own),
                ("subsystem_files", r["subsystem_files"]),
                ("multi_subsystem_label", str(multi).lower()),
                ("aa_species_touched", "|".join(sorted(touched))),
                ("reactants", r["reactants"]), ("products", r["products"]),
            ]))
    # also flag multi-label aa reactions (interface)
    for r in aa:
        if "|" in (r["subsystem_files"] or ""):
            own_rows.append(OrderedDict([
                ("reaction_id", r["id"]),
                ("ownership", "aminoacylation_shared_label"),
                ("subsystem_files", r["subsystem_files"]),
                ("multi_subsystem_label", "true"),
                ("aa_species_touched", "|".join(sorted((set(parse_side(r["reactants"])) |
                                                        set(parse_side(r["products"]))) & aa_dyn_set))),
                ("reactants", r["reactants"]), ("products", r["products"]),
            ]))
    own_rows.sort(key=lambda x: (x["ownership"], x["reaction_id"]))
    write_csv(os.path.join(AUDIT, "aminoacylation_v1_ownership.csv"), own_rows)
    n_ext_touch = sum(1 for x in own_rows if x["ownership"] == "external_touches_aa")
    n_shared = sum(1 for x in own_rows if x["ownership"] == "aminoacylation_shared_label")

    # ===================================================================== #
    # §V  GlyAMP / MetAMP audit + enzyme-bound fractions (author trajectory)
    # ===================================================================== #
    traj = load_rows(TRAJ)
    ts = [float(r["time"]) for r in traj]
    col = lambda s: [float(r[s]) for r in traj]
    gly_amp, met_amp = col("GlyAMP"), col("MetAMP")

    def peak(v):
        i = max(range(len(v)), key=lambda j: v[j])
        return v[i], ts[i]

    # rate laws compiled; production/consumption of GlyAMP and MetAMP along traj
    rate_code = {r["id"]: compile_rate(r["rate_law"]) for r in aa}
    nv_by_id = {r["id"]: net_vector(parse_side(r["reactants"]), parse_side(r["products"])) for r in aa}

    def gross_rates(state):
        out = {}
        for rid, code in rate_code.items():
            k1 = pmap.get((rid, "k1"), float("nan"))
            if k1 != k1:      # nan
                continue
            env = dict(state)
            env["k1"] = k1
            try:
                out[rid] = eval(code, {"__builtins__": {}}, env)
            except Exception:
                out[rid] = 0.0
        return out

    def prod_cons(species, idx):
        state = {s: float(traj[idx][s]) for s in traj[idx].keys() if s in aa_dyn_set}
        v = gross_rates(state)
        prod, cons = [], []
        for rid, rate in v.items():
            c = nv_by_id[rid].get(species, 0.0)
            if c > 0 and abs(rate * c) > 0:
                prod.append((rid, c, rate, c * rate))
            elif c < 0 and abs(rate * c) > 0:
                cons.append((rid, c, rate, -c * rate))
        prod.sort(key=lambda x: -abs(x[3]))
        cons.sort(key=lambda x: -abs(x[3]))
        return prod[:6], cons[:6], state

    def fmt_routes(routes):
        return [OrderedDict([("reaction_id", rid), ("coeff", c), ("k1", repr(pmap.get((rid, "k1")))),
                             ("rate_uM_s", "%.6e" % v), ("flux_uM_s", "%.6e" % f)])
                for rid, c, v, f in routes]

    audit_times = {"t_initial": 0, "t_mid": len(traj) // 2, "t_final": len(traj) - 1}
    glyamp_audit = OrderedDict()
    for sp, series in (("GlyAMP", gly_amp), ("MetAMP", met_amp)):
        pk, pt = peak(series)
        routes = OrderedDict()
        for label, idx in audit_times.items():
            p, c, state = prod_cons(sp, idx)
            routes[label] = OrderedDict([("time_s", "%.4e" % ts[idx]),
                                         ("producers", fmt_routes(p)),
                                         ("consumers", fmt_routes(c))])
        # moiety inventory contribution at first/mid/last
        contrib = OrderedDict()
        for label, idx in audit_times.items():
            state = {s: float(traj[idx][s]) for s in traj[idx].keys() if s in aa_dyn_set}
            inv = {m: sum(state.get(sp2, 0.0) * moiety_counts(sp2)[m] for sp2 in aa_dyn_set)
                   for m in MOIETY_KEYS}
            tot_aden = inv["adenosine"] if inv["adenosine"] > 0 else 1.0
            tot_gly = inv["glycyl"] + 0.0
            contrib[label] = OrderedDict([
                ("inventory", OrderedDict((m, "%.6e" % inv[m]) for m in MOIETY_KEYS)),
                ("free_adenylate_share_of_adenosine",
                 "%.6f" % ((state.get("GlyAMP", 0.0) + state.get("MetAMP", 0.0)) / max(tot_aden, 1e-30))),
            ])
        glyamp_audit[sp] = OrderedDict([
            ("initial_uM", series[0]), ("max_uM", pk), ("max_at_s", pt),
            ("final_uM", series[-1]), ("still_rising_at_window_end", series[-1] >= series[-2]),
            ("peak_and_terminal_routes", routes),
            ("moiety_inventory", contrib),
        ])

    # enzyme-bound fractions from the FULL author trajectory (free + 14 complexes per enzyme)
    def enz_series(pref):
        complexes = [s for s in aa_dyn_set if s.startswith(pref + "_") and not s.endswith("_degraded")]
        free = col(pref)
        series = {s: col(s) for s in complexes}
        bound = [sum(series[s][i] for s in complexes) for i in range(len(ts))]
        tot = [free[i] + bound[i] for i in range(len(ts))]
        frac = [(bound[i] / tot[i]) if tot[i] > 0 else float("nan") for i in range(len(ts))]
        return OrderedDict([
            ("complexes", len(complexes)),
            ("total_max_uM", max(tot)), ("total_min_uM", min(tot)),
            ("bound_fraction_min", min(frac)), ("bound_fraction_at_t0", frac[0]),
            ("bound_fraction_final", frac[-1]),
            ("bound_fraction_series", ["%.8f" % f for f in frac]),
        ])
    enz_bound = OrderedDict((p, enz_series(p)) for p in ("MetRS", "GlyRS"))

    # moiety-total drift of the SUBSYSTEM view of the full-network trajectory
    # (open-system: boundary fluxes come from non-aa modules; report drift, do not assume closure)
    def moiety_drift(m):
        vals = []
        for row in traj:
            state = {s: float(row[s]) for s in aa_dyn_set}
            vals.append(sum(state.get(sp, 0.0) * moiety_counts(sp)[m] for sp in aa_dyn_set))
        return OrderedDict([("initial", vals[0]), ("final", vals[-1]),
                            ("max_abs_dev_from_initial", max(abs(v - vals[0]) for v in vals))])
    drift = OrderedDict((m, moiety_drift(m)) for m in MOIETY_KEYS)

    write_json(os.path.join(AUDIT, "aminoacylation_v1_glyamp_audit.json"), OrderedDict([
        ("schema", "pnas2017_aminoacylation_v1_glyamp_audit/v1"),
        ("trajectory_source", TRAJ_REL),
        ("trajectory_note", "author-saved 200-point run, RelTol 1e-3 / AbsTol 1e-9 "
         "(exploration-grade; formal v1 acceptance uses the stricter converged reference)"),
        ("adenylate_audit", glyamp_audit),
        ("enzyme_bound_fraction_excludes_free_adenylates", True),
        ("enzyme_bound_fraction", enz_bound),
        ("subsystem_inventory_drift_OPEN_SYSTEM", drift),
    ]))

    print(json.dumps(OrderedDict([
        ("ledger_known_answer_tests_pass", all_ok),
        ("pathway_cycle_coverage", cov),
        ("external_reactions_touching_aa_states", n_ext_touch),
        ("aa_reactions_with_shared_subsystem_label", n_shared),
        ("GlyAMP_max_uM", glyamp_audit["GlyAMP"]["max_uM"]),
        ("MetAMP_max_uM", glyamp_audit["MetAMP"]["max_uM"]),
        ("MetRS_bound_fraction_final", enz_bound["MetRS"]["bound_fraction_final"]),
        ("GlyRS_bound_fraction_final", enz_bound["GlyRS"]["bound_fraction_final"]),
    ]), indent=2))
    return 0


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "structure"
    if stage != "structure":
        raise SystemExit("unknown stage %r" % stage)
    sys.exit(main())
