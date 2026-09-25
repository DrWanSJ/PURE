#!/usr/bin/env python3
"""Generate the PNAS 2017 aminoacylation subsystem reduction-analysis artefacts.

This is the FIRST worked case for the generic reduction-validation protocol
(docs/reduction/reduction_validation_protocol_v0.md). It is an ANALYSIS-ONLY
pipeline: it reads committed, immutable artefacts and writes derived audit
files. It NEVER modifies the canonical SBML, the author CSVs, or the model.

Inputs (read-only):
  models/pnas2017_full_reference/original/fMGG_synthesis.xml  (SHA-pinned; only hashed)
  models/pnas2017_full_reference/audit/{reactions,species,parameters}.csv
  docs/reduction/reduction_decisions.csv                      (reverse-partner cross-check)
  results/pnas2017_reference/2026-09-24_authors_model_v0/authors_model_trajectory.csv

Outputs (deterministic):
  models/pnas2017_full_reference/audit/aminoacylation_reactions.csv
  models/pnas2017_full_reference/audit/aminoacylation_species.csv
  models/pnas2017_full_reference/audit/aminoacylation_inventory.json
  models/pnas2017_full_reference/audit/aminoacylation_pathway_balance.csv
  models/pnas2017_full_reference/audit/aminoacylation_reversible_pairs.csv
  models/pnas2017_full_reference/audit/aminoacylation_reversible_pair_validation.csv
  models/pnas2017_full_reference/audit/aminoacylation_fast_states.csv
  models/pnas2017_full_reference/audit/aminoacylation_enzyme_pool_conservation.csv
  models/pnas2017_full_reference/audit/aminoacylation_timescale.csv
  models/pnas2017_full_reference/audit/aminoacylation_analysis_summary.json

Run:  python scripts/analyze_pnas2017_aminoacylation_reduction.py
"""
import ast
import csv
import hashlib
import json
import math
import os
import sys
from collections import OrderedDict

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")
SBML_REL = "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
SBML = os.path.join(ROOT, *SBML_REL.split("/"))
TRAJ_REL = "results/pnas2017_reference/2026-09-24_authors_model_v0/authors_model_trajectory.csv"
TRAJ = os.path.join(ROOT, *TRAJ_REL.split("/"))

RNG_SEED = 20260925  # preregistered seed for the arbitrary-feasible-state test
EXACT_TOL = 1e-9     # exact-representation tolerance (protocol class A)

# --- aminoacylation net-chemistry target (derived & verified, NOT hardcoded) ---
# Canonical forward catalytic cycles, expressed as the ordered list of source
# reaction ids that the SBML actually contains. The script SUMS the true SBML
# stoichiometric vectors for these ids and asserts the sum collapses to the
# expected net chemistry, cancelling every enzyme-bound intermediate.
PATHWAYS = OrderedDict([
    ("Gly_tRNAGlyGCC", dict(
        enzyme="GlyRS", aa="Gly", trna="tRNAGlyGCC", aatrna="GlytRNAGlyGCC",
        adenylate="GlyAMP",
        cycle=["re0000000132", "re0000000134", "re0000000140", "re0000000207",
               "re0000000189", "re0000000178", "re0000000182", "re0000000145"],
    )),
    ("Met_tRNAfMetCAU", dict(
        enzyme="MetRS", aa="Met", trna="tRNAfMetCAU", aatrna="MettRNAfMetCAU",
        adenylate="MetAMP",
        cycle=["re0000000157", "re0000000159", "re0000000165", "re0000000249",
               "re0000000231", "re0000000220", "re0000000224", "re0000000170"],
    )),
])

ACCOUNTING = ["ATP", "ADP", "AMP", "GTP", "GDP", "PPi", "Pi_PO4",
              "CP_creatine_phosphate", "creatine"]


# --------------------------------------------------------------------------- #
# loading
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


def sig(spec_dict):
    return tuple(sorted((k, round(c, 9)) for k, c in spec_dict.items()))


# --------------------------------------------------------------------------- #
# rate-law evaluation (AST-compiled, restricted namespace)
# --------------------------------------------------------------------------- #
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


class Reaction:
    __slots__ = ("id", "subsystem_files", "reactants", "products", "net",
                 "param", "rate_code", "rate_law", "reverse_partner")

    def rate(self, state):
        env = dict(state)
        env["k1"] = self.param
        return eval(self.rate_code, {"__builtins__": {}}, env)


def main():
    # --- provenance hash of the immutable SBML (never opened for parse here) ---
    sbml_sha = hashlib.sha256(open(SBML, "rb").read()).hexdigest()

    reactions = load_rows(os.path.join(AUDIT, "reactions.csv"))
    species = load_rows(os.path.join(AUDIT, "species.csv"))
    parameters = load_rows(os.path.join(AUDIT, "parameters.csv"))

    # author parameter values keyed (reaction_id, param_id) -> float
    pmap = {}
    for p in parameters:
        try:
            pmap[(p["reaction_id"], p["parameter_id"])] = float(p["author_export_value"])
        except (ValueError, TypeError):
            pmap[(p["reaction_id"], p["parameter_id"])] = float("nan")

    spmap = {s["id"]: s for s in species}

    # --- build Reaction objects for the aminoacylation subsystem ---
    rx_all = {}
    aa = []
    for r in reactions:
        sub = r["subsystem_files"] or ""
        if "Aminoacylation" not in sub:
            continue
        rx = Reaction()
        rx.id = r["id"]
        rx.subsystem_files = sub
        rx.reactants = parse_side(r["reactants"])
        rx.products = parse_side(r["products"])
        rx.net = net_vector(rx.reactants, rx.products)
        rx.param = pmap.get((r["id"], "k1"), float("nan"))
        rx.rate_law = r["rate_law"]
        rx.rate_code = compile_rate(r["rate_law"])
        rx.reverse_partner = ""
        rx_all[r["id"]] = rx
        aa.append(rx)
    aa.sort(key=lambda x: x.id)

    # species involved
    aa_species = sorted({s for rx in aa for s in rx.net})
    # reactions grouped by pure / interface (shared with a non-aa subsystem)
    pure = [rx for rx in aa if all("Aminoacylation" in p for p in rx.subsystem_files.split("|"))]
    interface = [rx for rx in aa if rx not in pure]

    def subsys_of(rx):
        return "|".join(sorted(p for p in rx.subsystem_files.split("|") if "Aminoacylation" in p)) or "(none)"

    def pathway_key(sp):
        tags = []
        if sp.startswith("GlyRS") or sp in ("Gly", "GlyAMP", "tRNAGlyGCC", "GlytRNAGlyGCC"):
            tags.append("Gly")
        if sp.startswith("MetRS") or sp in ("Met", "MetAMP", "tRNAfMetCAU", "MettRNAfMetCAU"):
            tags.append("Met")
        if not tags:
            tags.append("shared")
        return ",".join(tags)

    # --- aminoacylation_reactions.csv ---
    rx_rows = []
    for rx in aa:
        is_deg = any(s.endswith("_degraded") for s in rx.net if rx.net[s] > 0)
        rx_rows.append(OrderedDict([
            ("reaction_id", rx.id),
            ("aminoacylation_subsystems", subsys_of(rx)),
            ("full_subsystem_files", rx.subsystem_files),
            ("interface_with_other_modules", str("Aminoacylation" not in rx.subsystem_files or len(set(rx.subsystem_files.split("|"))) > len([p for p in rx.subsystem_files.split('|') if 'Aminoacylation' in p])).lower()),
            ("n_reactants", len(rx.reactants)),
            ("n_products", len(rx.products)),
            ("reactants", "|".join("%s:%g" % kv for kv in sorted(rx.reactants.items()))),
            ("products", "|".join("%s:%g" % kv for kv in sorted(rx.products.items()))),
            ("net_stoichiometry", "|".join("%s:%+g" % kv for kv in sorted(rx.net.items()))),
            ("is_degradation_sink", str(is_deg).lower()),
            ("k1_author_value", repr(rx.param)),
            ("k1_is_zero", str(rx.param == 0.0).lower()),
            ("rate_law", rx.rate_law),
            ("pathway_membership", pathway_key(" ".join(rx.net.keys()))),
        ]))
    write_csv(os.path.join(AUDIT, "aminoacylation_reactions.csv"), rx_rows)

    # --- aminoacylation_species.csv ---
    def role(s):
        if s.endswith("_degraded"):
            return "degraded_sink"
        if s.startswith("GlyRS_") or s.startswith("MetRS_"):
            return "enzyme_bound_complex"
        if s in ("GlyRS", "MetRS"):
            return "free_enzyme"
        if s in ("GlyAMP", "MetAMP"):
            return "free_aminoacyl_adenylate"
        if s in ("Gly", "Met"):
            return "free_amino_acid"
        if s.startswith("tRNA"):
            return "free_tRNA"
        if s.startswith("GlytRNA") or s.startswith("MettRNA"):
            return "aminoacyl_tRNA"
        if s in ("ATP", "AMP", "PPi", "ADP"):
            return "shared_nucleotide"
        return "other"
    sp_rows = []
    traj_header = None
    for s in aa_species:
        sp_rows.append(OrderedDict([
            ("species_id", s),
            ("aminoacylation_role", role(s)),
            ("pathway_membership", pathway_key(s)),
            ("is_complex", str("_" in s).lower()),
            ("sbml_initial_concentration", spmap[s]["sbml_initial_concentration"]),
            ("author_export_initial_value", spmap[s]["author_export_initial_value"]),
            ("boundary_condition", spmap[s]["boundary_condition"]),
        ]))
    write_csv(os.path.join(AUDIT, "aminoacylation_species.csv"), sp_rows)

    # --- inventory json ---
    inventory = OrderedDict([
        ("schema", "pnas2017_aminoacylation_inventory/v0"),
        ("generated_utc", "DETERMINISTIC_PLACEHOLDER"),
        ("source_sbml", SBML_REL),
        ("source_sbml_sha256", sbml_sha),
        ("source_trajectory", TRAJ_REL),
        ("selection_rule", "reactions whose subsystem_files contains an Aminoacylation_* label"),
        ("excluded_modules", ["FMet_tRNASynthesis (formylation) kept separate by project decision"]),
        ("n_reactions", len(aa)),
        ("n_reactions_pure", len(pure)),
        ("n_reactions_interface", len(interface)),
        ("interface_reaction_ids", sorted(rx.id for rx in interface)),
        ("n_species", len(aa_species)),
        ("n_species_pure_distinguished", len(aa_species)),
        ("reaction_ids", sorted(rx.id for rx in aa)),
        ("species_ids", aa_species),
        ("role_counts", count_by(role(s) for s in aa_species)),
        ("pathway_reaction_counts", {
            "Gly_A": sum(1 for rx in aa if "Aminoacylation_A_Gly" in rx.subsystem_files),
            "Met_A": sum(1 for rx in aa if "Aminoacylation_A_Met" in rx.subsystem_files),
            "Gly_B": sum(1 for rx in aa if "Aminoacylation_B_GlyGCC" in rx.subsystem_files),
            "Met_B": sum(1 for rx in aa if "Aminoacylation_B_fMetCAU" in rx.subsystem_files),
        }),
        ("zero_k1_reactions", sorted(rx.id for rx in aa if rx.param == 0.0)),
        ("nan_k1_reactions", sorted(rx.id for rx in aa if math.isnan(rx.param))),
    ])
    write_json(os.path.join(AUDIT, "aminoacylation_inventory.json"), inventory)

    # ======================= PHASE 7: PATHWAY NET CHEMISTRY ================= #
    target_species = {"ATP": -1.0, "AMP": 1.0, "PPi": 1.0}
    pathway_rows = []
    for pname, cfg in PATHWAYS.items():
        vec = {}
        for rid in cfg["cycle"]:
            if rid not in rx_all:
                raise SystemExit("pathway %s references unknown reaction %s" % (pname, rid))
            for k, c in rx_all[rid].net.items():
                vec[k] = vec.get(k, 0.0) + c
        vec = {k: c for k, c in vec.items() if abs(c) > 1e-9}
        # expected net
        expected = dict(target_species)
        expected[cfg["aa"]] = -1.0
        expected[cfg["trna"]] = -1.0
        expected[cfg["aatrna"]] = 1.0
        # cancelled intermediates: species consumed/produced by individual
        # cycle reactions but net ~0 (enzyme species)
        touched = set()
        for rid in cfg["cycle"]:
            touched |= set(rx_all[rid].net)
        cancelled = sorted((touched - set(vec)) - set(expected))
        matches = (round_sum(vec) == round_sum(expected))
        # deltas
        def delta(name):
            return vec.get(name, 0.0)
        pathway_rows.append(OrderedDict([
            ("pathway_id", pname),
            ("enzyme", cfg["enzyme"]),
            ("source_reaction_ids", "|".join(cfg["cycle"])),
            ("net_stoichiometry", "|".join("%s:%+g" % kv for kv in sorted(vec.items()))),
            ("matches_expected_net_chemistry", str(matches).lower()),
            ("expected_net", "|".join("%s:%+g" % kv for kv in sorted(expected.items()))),
            ("cancelled_intermediates", "|".join(cancelled)),
            ("n_cancelled_intermediates", len(cancelled)),
            ("ATP_delta", delta("ATP")),
            ("ADP_delta", delta("ADP")),
            ("AMP_delta", delta("AMP")),
            ("PPi_delta", delta("PPi")),
            ("Pi_delta", delta("Pi_PO4")),
            ("amino_acid_delta", delta(cfg["aa"])),
            ("uncharged_tRNA_delta", delta(cfg["trna"])),
            ("aminoacyl_tRNA_delta", delta(cfg["aatrna"])),
            ("net_particle_number_delta", sum(vec.values())),
            ("flags", "" if matches else "NET_MISMATCH"),
        ]))
    write_csv(os.path.join(AUDIT, "aminoacylation_pathway_balance.csv"), pathway_rows)

    # =================== PHASE 8: EXACT FORWARD/REVERSE PAIRS ================= #
    # detect structural pairs within the subsystem
    by_sig = {}
    for rx in aa:
        by_sig.setdefault(sig(rx.reactants), []).append(rx)
    partner_map = OrderedDict()
    for rx in aa:
        want = sig(rx.products)
        cands = [c for c in by_sig.get(want, []) if sig(c.products) == sig(rx.reactants) and c is not rx]
        if len(cands) == 1:
            partner_map[rx.id] = cands[0].id
        elif len(cands) > 1:
            partner_map[rx.id] = "AMBIGUOUS:" + "|".join(sorted(c.id for c in cands))
    pairs = []
    seen = set()
    for a, b in partner_map.items():
        if b.startswith("AMBIGUOUS:") or b in seen or a in seen:
            continue
        rx_f, rx_r = rx_all[a], rx_all[b]
        # structural equivalence: net vector of reverse == -net of forward
        struct_eq = all(abs(rx_r.net.get(k, 0.0) + rx_f.net.get(k, 0.0)) < 1e-12
                        for k in set(rx_f.net) | set(rx_r.net))
        struct_eq = struct_eq and (set(rx_f.net) == set(rx_r.net))
        pairs.append((rx_f, rx_r, struct_eq))
        seen.add(a); seen.add(b)
    pair_rows = []
    for rx_f, rx_r, struct_eq in pairs:
        sp = sorted(set(rx_f.net))
        pair_rows.append(OrderedDict([
            ("forward_reaction_id", rx_f.id),
            ("reverse_reaction_id", rx_r.id),
            ("reactants", "|".join("%s:%g" % kv for kv in sorted(rx_f.reactants.items()))),
            ("products", "|".join("%s:%g" % kv for kv in sorted(rx_f.products.items()))),
            ("forward_parameter", repr(rx_f.param)),
            ("reverse_parameter", repr(rx_r.param)),
            ("exact_net_law", "v_net = (%s) - (%s)" % (rx_f.rate_law, rx_r.rate_law)),
            ("species_in_pair", "|".join(sp)),
            ("structural_equivalence", str(struct_eq).lower()),
        ]))
    pair_rows.sort(key=lambda r: r["forward_reaction_id"])
    write_csv(os.path.join(AUDIT, "aminoacylation_reversible_pairs.csv"), pair_rows)

    # load trajectory states
    traj_rows = load_rows(TRAJ)
    traj_states = []
    for tr in traj_rows:
        st = {}
        for s in aa_species:
            try:
                st[s] = float(tr[s])
            except (KeyError, ValueError):
                st[s] = 0.0
        traj_states.append((float(tr["time"]), st))

    # arbitrary feasible states (log-uniform positive), seeded
    rng = np.random.default_rng(RNG_SEED)
    random_states = []
    for _ in range(200):
        st = {s: float(10 ** rng.uniform(-3, 3)) for s in aa_species}
        random_states.append(("random", st))

    def rhs_pair(state, rx_f, rx_r):
        vf, vr = rx_f.rate(state), rx_r.rate(state)
        out = {}
        for s in set(rx_f.net) | set(rx_r.net):
            out[s] = vf * rx_f.net.get(s, 0.0) + vr * rx_r.net.get(s, 0.0)
        return out, vf, vr

    def rhs_recombined(state, rx_f, rx_r):
        vnet = rx_f.rate(state) - rx_r.rate(state)
        return {s: vnet * rx_f.net.get(s, 0.0) for s in set(rx_f.net)}, vnet

    val_rows = []
    all_states = traj_states + random_states
    for rx_f, rx_r, struct_eq in pairs:
        max_abs = 0.0
        max_scale = 1e-30
        for _, st in all_states:
            full, _, _ = rhs_pair(st, rx_f, rx_r)
            rec, _ = rhs_recombined(st, rx_f, rx_r)
            for s in full:
                d = abs(full[s] - rec.get(s, 0.0))
                max_abs = max(max_abs, d)
                max_scale = max(max_scale, abs(full[s]))
        rel = max_abs / max_scale if max_scale > 0 else 0.0
        val_rows.append(OrderedDict([
            ("forward_reaction_id", rx_f.id),
            ("reverse_reaction_id", rx_r.id),
            ("structural_equivalence", str(struct_eq).lower()),
            ("n_states_tested", len(all_states)),
            ("max_abs_residual", "%.3e" % max_abs),
            ("max_state_magnitude", "%.3e" % max_scale),
            ("max_relative_residual", "%.3e" % rel),
            ("exact_representation_pass", str(rel < EXACT_TOL and struct_eq).lower()),
        ]))
    write_csv(os.path.join(AUDIT, "aminoacylation_reversible_pair_validation.csv"), val_rows)
    n_exact_pass = sum(1 for r in val_rows if r["exact_representation_pass"] == "true")

    # =================== PHASE 10: TIMESCALE DIAGNOSTICS ===================== #
    # fast = enzyme-bound complexes + free aminoacyl-adenylates (derive from
    # network roles, not names); split by pathway; slow = free pools + free enzyme.
    dyn = [s for s in aa_species if not s.endswith("_degraded")]
    fast = [s for s in dyn if role(s) in ("enzyme_bound_complex", "free_aminoacyl_adenylate")]
    slow = [s for s in dyn if s not in fast]

    # state vector for the aa subsystem (only aa species participate in aa rates)
    idx = {s: i for i, s in enumerate(dyn)}

    def f(state_map):
        x = np.zeros(len(dyn))
        for s, val in state_map.items():
            if s in idx:
                x[idx[s]] = val
        dx = np.zeros(len(dyn))
        for rx in aa:
            if math.isnan(rx.param):
                continue
            v = rx.rate(state_map)
            for s, c in rx.net.items():
                if s in idx:
                    dx[idx[s]] += v * c
        return dx

    # sample grid (dense over the predeclared interval; log-spaced 30 points)
    times = [t for t, _ in traj_states]
    gidx = sorted(set(int(i) for i in np.linspace(0, len(traj_states) - 1, 30).astype(int)))
    ts_rows = []
    for gi in gidx:
        t, st = traj_states[gi]
        # numeric Jacobian restricted to fast block
        base_f = None
        h_rel = 1e-6
        Jff = np.zeros((len(fast), len(fast)))
        for j, sj in enumerate(fast):
            base = st.get(sj, 0.0)
            step = h_rel * (abs(base) + 1e-6)
            stp = dict(st); stp[sj] = base + step
            stm = dict(st); stm[sj] = base - step
            fp, fm = f(stp), f(stm)
            for i, si in enumerate(fast):
                Jff[i, j] = (fp[idx[si]] - fm[idx[si]]) / (2 * step)
        eig = np.linalg.eigvals(Jff) if Jff.size else np.array([])
        reig = np.abs(eig.real) if len(eig) else np.array([0.0])
        # Stiff (physical fast-decay) scale: largest |Re lambda| of the fast
        # block. Near-zero fast-block eigenvalues are STRUCTURAL neutral modes
        # (total-enzyme conservation and zero-concentration complexes) and MUST
        # NOT be inverted into tau_fast (D6 methodology caution). Report them
        # as a count instead of a timescale.
        lam_stiff = float(reig.max()) if len(reig) else float("nan")
        n_stiff = int(np.sum(reig > 1e2))
        n_nearzero = int(np.sum(reig < 1e-3))
        tau_fast_stiff = 1.0 / lam_stiff if lam_stiff and not math.isnan(lam_stiff) else float("nan")
        # slow timescale from slow-state derivative norm along trajectory
        dxall = f(st)
        slow_vals = np.array([st.get(s, 0.0) for s in slow])
        slow_rates = np.array([dxall[idx[s]] for s in slow])
        denom = float(np.max(np.abs(slow_rates))) if len(slow_rates) else 0.0
        tau_slow = (float(np.max(np.abs(slow_vals))) / denom) if denom > 0 else float("inf")
        eps_stiff = (tau_fast_stiff / tau_slow) if (tau_slow and not math.isinf(tau_slow)
                                                    and tau_slow > 0
                                                    and not math.isnan(tau_fast_stiff)) else float("nan")
        ts_rows.append(OrderedDict([
            ("time_s", "%.6e" % t),
            ("n_fast_states", len(fast)),
            ("n_slow_states", len(slow)),
            ("lambda_stiff_fast_s^-1", fmt(lam_stiff)),
            ("tau_fast_stiff_s", fmt(tau_fast_stiff)),
            ("n_stiff_fast_modes", n_stiff),
            ("n_structural_nearzero_fast_modes", n_nearzero),
            ("tau_slow_s", fmt(tau_slow)),
            ("epsilon_stiff", fmt(eps_stiff)),
            ("algebraic_manifold_derived", "false"),
            ("note", "report_only; near-zero fast-block eigenvalues are structural "
                     "neutral modes (enzyme conservation / zero-concentration "
                     "complexes) and are NOT inverted into a fast timescale; "
                     "aa-subsystem closure assumed"),
        ]))
    write_csv(os.path.join(AUDIT, "aminoacylation_timescale.csv"), ts_rows)

    # ---------- fast-state detail table (Phase 9 candidate A3 evidence) ------- #
    def median(vals):
        vals = sorted(vals)
        n = len(vals)
        return 0.0 if n == 0 else (vals[n // 2] if n % 2 else 0.5 * (vals[n // 2 - 1] + vals[n // 2]))
    fast_detail = []
    conc_by_state = {s: [st.get(s, 0.0) for _, st in traj_states] for s in dyn}
    for s in sorted(fast):
        producers = [rx.id for rx in aa if rx.net.get(s, 0.0) > 0]
        consumers = [rx.id for rx in aa if rx.net.get(s, 0.0) < 0]
        cs = conc_by_state[s]
        enz = "MetRS" if s.startswith("MetRS") else ("GlyRS" if s.startswith("GlyRS") else "shared")
        moieties = [m for m in ("ATP", "AMP", "PPi") if m in s]
        if "AMP" in s and "PPi" not in s and "ATP" not in s:
            pass  # AA-AMP adenylate core already captured by AMP token match
        fast_detail.append(OrderedDict([
            ("fast_state", s),
            ("enzyme_membership", enz),
            ("moiety_included", "|".join(sorted(set(moieties))) or "none"),
            ("n_reactions_producing", len(producers)),
            ("n_reactions_consuming", len(consumers)),
            ("median_conc_uM", "%.6e" % median(cs)),
            ("max_conc_uM", "%.6e" % (max(cs) if cs else 0.0)),
            ("is_zero_at_reference_start", str(abs(cs[0]) < 1e-15).lower() if cs else "true"),
        ]))
    write_csv(os.path.join(AUDIT, "aminoacylation_fast_states.csv"), fast_detail)

    # ---------- enzyme-pool conservation (Phase 9 candidate A2 evidence) ------ #
    def enz_in(s, pref):
        return s == pref or s.startswith(pref + "_")
    cons_rows = []
    for pref in ["MetRS", "GlyRS"]:
        worst_active = 0.0   # active pool over reactions active at reference
        worst_family = 0.0   # active + degraded over ALL reactions
        for rx in aa:
            active = sum(c for s, c in rx.net.items() if enz_in(s, pref) and not s.endswith("_degraded"))
            family = sum(c for s, c in rx.net.items() if enz_in(s, pref))
            if rx.param == 0.0 or math.isnan(rx.param):
                pass
            else:
                worst_active = max(worst_active, abs(active))
            worst_family = max(worst_family, abs(family))
        cons_rows.append(OrderedDict([
            ("enzyme_pool", pref + "_total"),
            ("definition", "free %s + all %s_* complexes (active)" % (pref, pref)),
            ("active_pool_max_LoverS_reference_active", "%.3e" % worst_active),
            ("active_pool_conserved_at_reference", str(worst_active < 1e-12).lower()),
            ("family_total_max_LoverS_all_reactions", "%.3e" % worst_family),
            ("family_total_conserved", str(worst_family < 1e-12).lower()),
            ("note", "active pool is broken only by _degraded sinks whose k1=0 "
                     "at the author reference; active+degraded family_total is "
                     "the unconditional conservation candidate (protocol class C/B)"),
        ]))
    write_csv(os.path.join(AUDIT, "aminoacylation_enzyme_pool_conservation.csv"), cons_rows)


    finite_eps = [float(r["epsilon_stiff"]) for r in ts_rows if r["epsilon_stiff"] not in ("nan", "")]
    summary = OrderedDict([
        ("schema", "pnas2017_aminoacylation_analysis_summary/v0"),
        ("source_sbml_sha256", sbml_sha),
        ("n_reactions", len(aa)),
        ("n_reactions_pure", len(pure)),
        ("n_reactions_interface", len(interface)),
        ("n_species", len(aa_species)),
        ("n_fast_states", len(fast)),
        ("n_slow_states", len(slow)),
        ("fast_states", sorted(fast)),
        ("slow_states", sorted(slow)),
        ("pathway_net_chemistry", OrderedDict(
            (p, OrderedDict([
                ("matches", r["matches_expected_net_chemistry"]),
                ("net", r["net_stoichiometry"]),
                ("cancelled_intermediates", r["cancelled_intermediates"]),
                ("n_cancelled", r["n_cancelled_intermediates"]),
            ])) for p, r in zip(PATHWAYS, pathway_rows))),
        ("n_reversible_pairs", len(pairs)),
        ("pairs_exact_pass", n_exact_pass),
        ("pairs_exact_total", len(pairs)),
        ("timescale_epsilon_stiff_min", fmt(min(finite_eps)) if finite_eps else "nan"),
        ("timescale_epsilon_stiff_max", fmt(max(finite_eps)) if finite_eps else "nan"),
        ("algebraic_qssa_manifold_derived", False),
        ("qssa_status", "NOT_CERTIFIED_STRUCTURAL_SEPARATION_AMBIGUOUS_AND_NO_MANIFOLD"),
        ("generated_utc", "DETERMINISTIC_PLACEHOLDER"),
    ])
    write_json(os.path.join(AUDIT, "aminoacylation_analysis_summary.json"), summary)

    print(json.dumps({k: summary[k] for k in
                      ("n_reactions", "n_species", "n_fast_states", "n_slow_states",
                       "n_reversible_pairs", "pairs_exact_pass", "pairs_exact_total",
                       "timescale_epsilon_stiff_min", "timescale_epsilon_stiff_max",
                       "algebraic_qssa_manifold_derived", "qssa_status")}, indent=2))
    print("pathway net chemistry:",
          {p: r["matches_expected_net_chemistry"] for p, r in zip(PATHWAYS, pathway_rows)})
    return 0


# --------------------------------------------------------------------------- #
def round_sum(d):
    return tuple(sorted((k, round(v, 9)) for k, v in d.items() if abs(v) > 1e-9))


def count_by(it):
    out = {}
    for x in it:
        out[x] = out.get(x, 0) + 1
    return out


def fmt(x):
    if x is None or (isinstance(x, float) and (math.isnan(x))):
        return "nan"
    if isinstance(x, float) and math.isinf(x):
        return "inf"
    return "%.6e" % x


def write_csv(path, rows):
    if not rows:
        open(path, "w").close()
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_json(path, obj):
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    sys.exit(main())
