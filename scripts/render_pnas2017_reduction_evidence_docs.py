#!/usr/bin/env python3
"""Render compact human views of frozen PNAS2017 evidence; make no decisions.

This renderer reads existing evidence, never evaluates rates or changes metric
definitions. --check compares deterministic Markdown without writing files.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


FILENAMES = (
    "01_amino_acid_activation.md",
    "02_trna_aminoacylation.md",
    "03_initiator_trna_formylation.md",
    "04_initiation_factor_preparation.md",
    "05_ribosome_mrna_initiation_assembly.md",
    "06_ef_tu_ternary_complex_delivery.md",
    "07_ef_g_nucleotide_cycle.md",
    "08_peptidyl_trna_ribosome_transitions.md",
    "09_rf1_rf2_peptide_release.md",
    "10_rf3_assisted_termination.md",
    "11_ribosome_recycling.md",
    "12_creatine_kinase_energy_regeneration.md",
    "13_nucleotide_diphosphate_kinase_exchange.md",
    "14_adenylate_kinase_exchange.md",
    "15_pyrophosphate_hydrolysis.md",
    "16_shared_small_molecule_transitions.md",
)
EVIDENCE = Path("models/pnas2017_full_reference/audit/reduction_evidence_v0")
DOCS = Path("docs/reduction")
STATUS = "Status: REFERENCE ONLY — NO KINETIC REDUCTION APPROVED."
QUESTIONS = (
    "Which activation states may be eliminated, and must free GlyAMP/MetAMP remain dynamic? Which total/resource coordinates preserve enzyme occupancy and ATP→AMP/PPi bookkeeping?",
    "Which charging intermediates may be eliminated while preserving each tRNA identity, bound amino acid, AMP release and synthetase occupancy? Are free-substrate or total coordinates defensible?",
    "Which MTF complexes may be reconstructed, and what complete formyl-donor/THF and initiator-tRNA token definitions are needed?",
    "Which IF2 nucleotide states must remain distinguishable, and which GTP/GDP and initiator-tRNA occupancies must be reconstructed?",
    "Which initiation microstates can share a coordinate without losing 30S/50S, mRNA, tRNA or initiation-factor occupancy and GTP hydrolysis timing?",
    "Which EF-Tu/EF-Ts and ternary-complex states need explicit dynamics to retain nucleotide exchange, charged-tRNA delivery and ribosome occupancy?",
    "Can a selected EF-G coordinate retain nucleotide exchange and ribosome-bound states across elongation and recycling interfaces?",
    "Which codon/peptide/tRNA microstates must remain resolved to reconstruct protected product, tRNA recycling and both ribosomal subunit occupancies?",
    "Can RF1/RF2 release events be aggregated while keeping factor identity, peptide release, tRNA and ribosome occupancy reconstructable?",
    "Which RF3 nucleotide and ribosome-bound states can be reconstructed without concealing RF1/RF2 release or GTP/GDP/Pi obligations?",
    "Which recycling steps preserve 30S/50S, mRNA, tRNA, RRF and EF-G return, including bound nucleotide resources?",
    "Which CK complexes can be eliminated while preserving CP/Cr, ATP/ADP and total enzyme occupancy, and over which fuel conditions?",
    "Which NDK complexes can be reconstructed while retaining adenylate/guanylate exchange and both directional gross ledgers?",
    "Which MK complexes can be reconstructed while preserving the two ADP binding sites, ATP/AMP exchange and total occupancy?",
    "Which PPiase intermediates can be eliminated while preserving PPi consumption, the two-PO4 event and phosphate-bound occupancy?",
    "Do any shared small-molecule events require retention or a separately justified transformation under a broader domain? No candidate fast-state set is currently registered for this card.",
)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(value: object) -> float | None:
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (ValueError, TypeError):
        return None


def fmt(value: object) -> str:
    v = num(value)
    return f"{v:.5g}" if v is not None else str(value or "N/A")


def numeric_range(values: list[object]) -> str:
    ns = [v for x in values if (v := num(x)) is not None]
    return f"{fmt(min(ns))}–{fmt(max(ns))}" if ns else "N/A"


def split(value: str) -> list[str]:
    return [x for x in value.split(";") if x and not x.startswith("N/A")]


def code_list(values: list[str], limit: int = 0) -> str:
    vals = sorted(set(values))
    shown = vals[:limit] if limit else vals
    result = ", ".join(f"`{v}`" for v in shown) or "none listed"
    return result + (f"; {len(vals) - limit} more in linked CSV" if limit and len(vals) > limit else "")


def link_table(prefix: str, name: str, label: str | None = None) -> str:
    return f"[{label or name}]({prefix}{EVIDENCE.as_posix()}/{name})"


def table(headers: list[str], content: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in content:
        lines.append("| " + " | ".join(str(x).replace("|", "\\|").replace("\n", " ") for x in row) + " |")
    return "\n".join(lines)


def reaction_species(reaction: dict[str, str]) -> set[str]:
    found: set[str] = set()
    for field in ("reactants_json", "products_json"):
        data = json.loads(reaction[field])
        found.update(data if isinstance(data, dict) else (x["species_id"] for x in data))
    return found


def load(root: Path) -> dict:
    e = root / EVIDENCE
    prereg = json.loads((e / "evidence_preregistration.json").read_text(encoding="utf-8-sig"))
    data = {"prereg": prereg}
    for key, name in (("reaction", "reaction_evidence.csv"), ("state", "state_evidence.csv"),
                      ("pair", "reverse_pair_evidence.csv"), ("process", "process_timescale_evidence.csv"),
                      ("reaction_pool", "reaction_pool_metrics.csv")):
        data[key] = rows(e / name)
    data["state_by_id"] = {r["species_id"]: r for r in data["state"]}
    data["reaction_by_id"] = {r["reaction_id"]: r for r in data["reaction"]}
    data["process_by_id"] = {r["process_id"]: r for r in data["process"]}
    data["historical"] = rows(root / "models/pnas2017_full_reference/audit/aminoacylation_fast_states.csv")
    data["history_by_id"] = {r["fast_state"]: r for r in data["historical"]}
    for key, name in (("pool", "pool_evidence.csv"), ("state_pool", "state_pool_metrics.csv")):
        data[key] = rows(e / name) if (e / name).exists() else []
    return data


def process_data(data: dict, card: dict) -> dict:
    rr = [data["reaction_by_id"][rid] for rid in card["reaction_ids"]]
    touched = set().union(*(reaction_species(r) for r in rr))
    states = [data["state_by_id"][sid] for sid in card["candidate_state_ids"]]
    pair_ids = {r["reverse_pair_id"] for r in rr if r["reverse_pair_id"] and not r["reverse_pair_id"].startswith("N/A")}
    pairs = [r for r in data["pair"] if r["pair_id"] in pair_ids]
    protected = sorted({s for r in rr for s in split(r["protected_species_touched"])})
    pools = sorted({p for r in rr for p in split(r["protected_pool_touched"])})
    subsystems = sorted({s for r in rr for s in split(r["level_b_subsystems"])})
    nonzero = [data["state_by_id"][s] for s in sorted(touched) if num(data["state_by_id"][s]["initial_value"]) not in (None, 0)]
    return {"reactions": rr, "touched": touched, "states": states, "pairs": pairs,
            "protected": protected, "pools": pools, "subsystems": subsystems,
            "nonzero": nonzero, "timescale": data["process_by_id"][card["process_id"]]}


def qss_summary(states: list[dict]) -> str:
    if not states:
        return "N/A: no candidate states"
    informative = sum((num(s["qss_informative_fraction"]) or 0) > 0 for s in states)
    return f"{informative}/{len(states)} states informative; median defect {numeric_range([s['qss_defect_median'] for s in states])}"


def eq_summary(pairs: list[dict]) -> str:
    if not pairs:
        return "N/A_NO_EXACT_REVERSE_PAIR"
    informative = sum((num(p["informative_fraction"]) or 0) > 0 for p in pairs)
    return f"{informative}/{len(pairs)} pairs informative; median defect {numeric_range([p['eq_defect_median'] for p in pairs])}"


def occupancy_summary(data: dict, pd: dict) -> str:
    measured = active_pools(data, pd)
    if not measured:
        return "N/A_POOL_MEMBERSHIP_UNRESOLVED"
    return "; ".join(f"{p['pool_id']}: {fmt(p['max_bound_fraction'])}" for p in measured)


def active_pools(data: dict, pd: dict) -> list[dict]:
    return sorted((p for p in data["pool"]
                   if p["pool_id"].endswith("_active_pool")
                   and not p["pool_id"].startswith("coarse:")
                   and set(split(p["member_species_ids"])) & pd["touched"]
                   and num(p["max_bound_fraction"]) is not None), key=lambda p: p["pool_id"])


def occupancy_table(data: dict, pd: dict) -> str:
    measured = active_pools(data, pd)
    if not measured:
        return "`N/A_POOL_MEMBERSHIP_UNRESOLVED`: no qualified active-pool ratio is available for this card."
    return table(["Registered active pool", "Free / total min / median", "Max nonfree fraction", "Informative sample fraction"], [
        [f"`{p['pool_id']}`", f"{fmt(p['free_total_ratio_min'])} / {fmt(p['free_total_ratio_median'])}",
         fmt(p["max_bound_fraction"]), fmt(p["informative_fraction"])] for p in measured])


def process_page(data: dict, card: dict, index: int) -> str:
    p = process_data(data, card)
    t = p["timescale"]
    rr, ss, pairs = p["reactions"], p["states"], p["pairs"]
    prefix = "../../../"
    links = " · ".join(link_table(prefix, filename, label) for filename, label in (
        ("reaction_evidence.csv", "events"), ("state_evidence.csv", "states"),
        ("reverse_pair_evidence.csv", "pairs"), ("process_timescale_evidence.csv", "timescales"),
        ("reaction_pool_metrics.csv", "pool links"), ("pool_evidence.csv", "pool certificates"),
        ("state_pool_metrics.csv", "member occupancy")))
    inputs = "; ".join(f"`{s['species_id']}={fmt(s['initial_value'])}`" for s in p["nonzero"]) or "No participating species has a nonzero author initial input."
    free_states = [data["state_by_id"][sid] for sid in p["touched"] if num(data["state_by_id"][sid].get("free_total_ratio_min")) is not None]
    free_min = min((num(s["free_total_ratio_min"]) for s in free_states), default=None)
    high = sorted(ss, key=lambda s: (-(num(s["qss_defect_median"]) or -1), s["species_id"]))[:3]
    qtable = table(["Candidate state", "QSS defect median / p95 / max", "Informative sample fraction", "Turnover median (s convention)"], [
        [f"`{s['species_id']}`", " / ".join(fmt(s[k]) for k in ("qss_defect_median", "qss_defect_p95", "qss_defect_max")), fmt(s["qss_informative_fraction"]), fmt(s["turnover_tau_median"])] for s in high
    ]) if high else "`N/A_NO_CANDIDATE_STATES`: this card defines no eliminated-state question; all participating states still have global state evidence."
    disabled = sum(num(x.get("forward_k")) == 0 or num(x.get("reverse_k")) == 0 for x in pairs)
    resource_ids = sorted({s for r in rr for s in json.loads(r["resource_delta_json"])})
    resource_text = code_list(resource_ids, 18)
    layer_counts = {}
    for s in ss:
        flag = s["initial_layer_flag"]
        layer_counts[flag] = layer_counts.get(flag, 0) + 1
    layer_text = "; ".join(f"`{flag}`: {count}" for flag, count in sorted(layer_counts.items())) or "no candidate states"
    historical = ""
    if index < 2:
        historical = "\nThe [historical aminoacylation reference](../aminoacylation_qssa_quick_reference.md) retains A3a `FAILED_VALIDATION_ON_REFERENCE_DOMAIN`, 21-state A3b `FAILED_SMOKE_CLOSURE_FEASIBILITY` and restricted 9-state `BLOCKED_NUMERICAL_COORDINATE_DEFECT`. Fast modes, high enzyme occupancy and free GlyAMP/MetAMP accumulation do not reverse those results; see the [global regression comparison](../pnas2017_reduction_quick_reference.md#aminoacylation-regression).\n"
    return f"""# {card['name']} — reduction evidence quick reference

`{card['process_id']}` · `AUTHOR_REFERENCE_CONDITION_ONLY` · [Global index](../pnas2017_reduction_quick_reference.md) · [Method](../pnas2017_reduction_evidence_method.md)

## 1. Process boundary

{len(rr)} source reactions; {len(ss)} listed candidate intermediates. Subsystems: {code_list(p['subsystems'])}. Membership can overlap other cards; the global unique count remains 968. Candidate examples: {code_list(card['candidate_state_ids'], 4)}. Exact candidate/reaction lists are in the {link_table(prefix, 'evidence_preregistration.json', 'frozen cards')}.

Protected species: {code_list(p['protected'], 10)}. Existing protected-pool links: {code_list(p['pools'], 8)}. These links do not by themselves certify pool completeness. Full evidence: {links}.

## 2. Reference-condition inputs

Relevant nonzero author values: {inputs}.

Values use the inferred reference concentration convention; author CSV absolute units are unresolved. Statistics use 200 stored `1e-4..1000 s` points. Supplemental exact `t=0` is separate; the first stored point equals the initial state, so initial-layer timing is ambiguous. No perturbation domain is claimed.

## 3. Time-scale evidence

Candidate block: full-source `J_zz` restricted to the {len(ss)} registered states. Stable relaxation range `{fmt(t['tau_fast_min'])}..{fmt(t['tau_fast_max'])}`; median `{fmt(t['tau_fast_median'])}` in the seconds convention. Stable mode count per sample: `{t['stable_mode_count_min']}..{t['stable_mode_count_max']}`; structural neutral lower bound: `{t['structural_neutral_mode_count']}`. Near-zero count: `{t['near_zero_mode_count_min']}..{t['near_zero_mode_count_max']}`; nondecaying count: `{t['nondecaying_mode_count_min']}..{t['nondecaying_mode_count_max']}`. These modes are never inverted.

Interface turnover proxy range `{fmt(t['tau_slow_min'])}..{fmt(t['tau_slow_max'])}`; `R_tau=tau_slow/tau_fast` range `{fmt(t['R_tau_min'])}..{fmt(t['R_tau_max'])}`, median `{fmt(t['R_tau_median'])}`; reciprocal `epsilon_tau` range `{fmt(t['epsilon_tau_min'])}..{fmt(t['epsilon_tau_max'])}`. These compare per-time medians, not the fastest mode alone. Status: **{t['timescale_status']}**. Slow coordinates and a valid elimination domain still require a scientific choice; no ratio certifies QSSA.

## 4. Occupancy / sequestration

Qualified active pools touching this card are listed separately; each denominator is its own registered token total, including all registered members beyond the card boundary.

{occupancy_table(data, p)}

The linked pool certificates retain active, family-total, degraded and rejected coarse memberships separately. A family-total nonfree fraction may include degradation and is not necessarily complex occupancy. Multi-token states retain a separate member/total ratio for every qualified pool in the member-occupancy table; no scalar denominator is invented.

Protected-substrate token sequestration: **N/A_BOUND_MOIETY_MEMBERSHIP_UNRESOLVED** wherever complete token membership is absent. Enzyme occupancy cannot substitute for bound ATP, amino-acid or tRNA composition. Missing/negative/zero-denominator samples remain explicit N/A; free enzyme is not assumed equal to total enzyme.

## 5. QSS evidence

{qss_summary(ss)}. Up to three candidate states with the largest informative median defect are shown; full state and long-form records retain all states and unavailable samples.

{qtable}

Initial-layer flags: {layer_text}. `delta_QSS=|dz/dt|/(production+consumption)` is unavailable at flux ≤ `1e-12`; zero flux is uninformative, not excellent QSSA. Sample fractions are unweighted author-grid fractions. No closure or full initial-layer test has been performed.
{historical}
## 6. Rapid-equilibrium evidence

{len(pairs)} distinct exact reverse pairs touch this card (a partner may cross its boundary). {eq_summary(pairs)}. `{disabled}` pair(s) have an official disabled direction and receive `REFERENCE_DIRECTION_DISABLED`; an inactive reverse reaction is not equilibrium. Defect summaries exclude disabled or low-exchange samples. Unpaired events receive `N/A_NO_EXACT_REVERSE_PAIR`; descriptive bands select no action.

## 7. Ledger obligations

Explicit free-resource delta keys: {resource_text}. ATP/GTP/AMP/ADP/GDP/Pi/PPi bookkeeping uses source IDs (`PO4` is Pi) and both directed extents. Amino-acid/tRNA, ribosome/factor occupancy and peptide effects must be reconstructed wherever source participants or protected pools touch them; absence from a free-resource delta does not establish absence of a bound moiety. The represented-particle delta is an event proxy, not osmotic pressure.

**EXACT_EVENT_STOICHIOMETRY_KNOWN; RECONSTRUCTION_REQUIRED; NO_TRANSFORMATION_EVALUATED.** Bound moieties remain unresolved where the source ledger lacks composition. Approximate trapezoidal extents and exact event stoichiometry do not establish reduced-ledger closure or kinetic validity.

## 8. Human questions

{QUESTIONS[index]} What validity domain and full-versus-reduced observable/ledger checks would justify a proposed representation? No answer is selected; **PENDING_HUMAN_REVIEW**.

{STATUS}
"""


def regression(data: dict) -> str:
    content = []
    occupancy = []
    for sid in ("GlyRS_GlyAMP", "MetRS_MetAMP", "GlyAMP", "MetAMP"):
        s = data["state_by_id"][sid]
        hist = data["history_by_id"][sid]
        relative = 100 * (float(s["trajectory_max"]) / float(hist["max_conc_uM"]) - 1)
        content.append([f"`{sid}`", fmt(hist["max_conc_uM"]), fmt(s["trajectory_max"]),
                        f"{relative:+.5g}%"])
        if "RS_" in sid:
            enzyme = sid.split("_")[0]
            pool_id = enzyme + "_active_pool"
            member = next(p for p in data["state_pool"] if p["species_id"] == sid and p["pool_id"] == pool_id)
            initial = float(data["state_by_id"][enzyme]["initial_value"])
            occupancy.append([f"`{sid}` / `{pool_id}`", fmt(float(hist["max_conc_uM"]) / initial), fmt(member["occupancy_max"])])
    t1, t2 = (data["process_by_id"][x] for x in ("P01", "P02"))
    return f"""## Aminoacylation regression

The preserved [specialized reference](aminoacylation_qssa_quick_reference.md) reports high GlyRS/MetRS complex occupancy, free adenylate accumulation, and fast modes. Its concentration summaries use the 200-point [historical author trajectory](../../results/pnas2017_reference/2026-09-24_authors_model_v0/authors_model_trajectory.csv); this layer uses the distinct 200-point [RoadRunner trajectory](../../results/pnas2017_reference/rr_cvode_author_csv_20260924/trajectory.csv). These input files are numerically different, not merely two roundings of identical samples. Historical rounded maxima and global maxima use the same inferred concentration convention:

{table(['State', 'Historical max', 'Global max', 'Relative difference vs historical'], content)}

The free adenylate maxima differ by about 0.197% for GlyAMP and 0.0268% for MetAMP; both remain substantial (about 7.89% and 9.94% of the corresponding initial free amino acid). These discrepancies are retained, without fitting or a claim of trajectory equivalence. The named complex occupancy remains high under the two explicit denominator conventions:

{table(['Member / active pool', 'Historical max concentration / initial pool', 'Global max of member(t) / pool(t)'], occupancy)}

The global column is the individual complex's member occupancy, not the pool's total nonfree fraction. Free GlyAMP/MetAMP have no complete total-token ratio asserted.

P01 stable `tau_min={fmt(t1['tau_fast_min'])}` and P02 `tau_min={fmt(t2['tau_fast_min'])}` retain short modes, but their full stable ranges are `{fmt(t1['tau_fast_min'])}..{fmt(t1['tau_fast_max'])}` and `{fmt(t2['tau_fast_min'])}..{fmt(t2['tau_fast_max'])}`. Historical `tau_fast≈1.9e-5 s` came from a different 30-state block and 30 sampled points; card-specific 12/28-state blocks, 200 samples and median-based `R_tau` do not have identical numerical conventions. This is a comparison of documented diagnostics, not an attempt to force numerical agreement.

Historical A3a remains [FAILED_VALIDATION_ON_REFERENCE_DOMAIN](aminoacylation_A3a_final_status.md); the broad 21-state A3b remains [FAILED_SMOKE_CLOSURE_FEASIBILITY](aminoacylation_A3bc_final_decision.md) near 2.498 s, and its restricted 9-state candidate remains `BLOCKED_NUMERICAL_COORDINATE_DEFECT` with an incomplete full window. Total coordinates removed a recorded bookkeeping leak but did not supply global kinetic validation. Those archived-main results keep their own domain and provenance; PR #3/#4 evidence is not imported.
"""


def global_page(data: dict) -> str:
    overview = []
    for i, card in enumerate(data["prereg"]["process_cards"]):
        p = process_data(data, card)
        t = p["timescale"]
        overview.append([
            f"[{card['process_id']} {card['name']}](process_quick_reference/{FILENAMES[i]})",
            len(p["reactions"]), len(p["states"]), code_list(p["protected"], 3), len(p["pairs"]),
            f"tau {fmt(t['tau_fast_min'])}..{fmt(t['tau_fast_max'])}; R median {fmt(t['R_tau_median'])}; NEED_MORE_INFORMATION",
            occupancy_summary(data, p), qss_summary(p["states"]), eq_summary(p["pairs"]),
            "event exact; reconstruction required", "PENDING_HUMAN_REVIEW",
        ])
    return f"""# PNAS2017 reduction evidence quick reference

**Evidence preparation only.** G1-PNAS is formally PASS / CLOSED. [Species information retention](species_information_contract_summary.md) is **HUMAN APPROVED**: I=42, II-A=57, II-B=91, III=22, C=29. All **968 kinetic decisions remain PENDING**, and all **96 process boxes remain unselected**. `PURE_reduced_core` remains `NOT_VALIDATED`. Source HEAD: `{data['prereg']['source_head']}`.

Scope is **AUTHOR_REFERENCE_CONDITION_ONLY** through 1000 s. The preserved 200-point trajectory and separate initial-state diagnostic do not validate other conditions. Author absolute chemical units are unresolved. Medians/fractions weight stored grid points equally; extents are approximate trapezoidal integrals. First stored state equals author x0 at timestamp `1e-4`: the initial layer is not fully resolved. See the [method](pnas2017_reduction_evidence_method.md), {link_table('../../', 'evidence_preregistration.json', 'frozen preregistration')} and {link_table('../../', 'evidence_manifest.json', 'provenance/verification manifest')}.

## Read the evidence by mathematical level

| Evidence | What to inspect | Interpretation boundary |
| --- | --- | --- |
| {link_table('../../', 'reaction_evidence.csv', '968 reaction rows')} | Original ID, family/process links, rate/extent, free-resource/particle delta, state/pair/pool/ledger obligations | Individual event stoichiometry is exact; no unique reaction QSSA time is invented |
| {link_table('../../', 'state_evidence.csv', '241 state rows')} and {link_table('../../', 'state_qss_timeseries.csv', 'QSS samples')} | Contract class, occupancy, production/consumption, QSS defect, turnover and initial layer | Cancellation of state fluxes is evidence; a tested algebraic closure is still needed |
| {link_table('../../', 'reverse_pair_evidence.csv', '290 exact pair rows')} and {link_table('../../', 'reverse_pair_equilibrium_timeseries.csv', 'pair samples')} | Both rates, exchange/net flux, defect, disabled directions and both extents | Pair evidence is unavailable when a direction is disabled or total exchange is too low |
| {link_table('../../', 'reaction_pool_metrics.csv', 'Many-to-many pool links')} and {link_table('../../', 'process_timescale_evidence.csv', '16 process diagnostics')} | Registered pool identities and full candidate-block mode ranges | Unresolved tokens/coordinates stay N/A or NEED_MORE_INFORMATION |

These linked CSVs are derived structured navigation. `EXTRACTED` source/contract facts, `INFERRED` numeric/annotation summaries and `AMBIGUOUS` unit/token/coordinate assumptions remain distinguishable. Their authority is the linked frozen sources; freshness depends on matching source/artifact hashes and independent verification.

## Distinctions that matter

| Concept | Required question |
| --- | --- |
| Time-scale separation | Does the selected candidate block relax faster than explicitly chosen slow coordinates? Fast modes alone do not certify QSSA. |
| QSSA | Can selected states follow a valid, stable algebraic closure while the protected trajectory is retained? |
| Total-coordinate QSSA | Can slow totals and reconstructed free/bound partitions preserve sequestered resources? |
| Rapid equilibrium | Do the particular forward/reverse fluxes balance on the proposed domain? A free/total ratio cannot decide this. |
| Lumping | Can aggregated states/events retain a justified rate, observables and reconstruction? |
| Conservation reconstruction | Can an exact invariant recover a coordinate without any fast-state approximation? |

`delta_QSS=|dz/dt|/(P+C)` differs from `delta_eq=|vf-vr|/(|vf|+|vr|)`. A denominator at/below `1e-12` is **LOW_FLUX_UNINFORMATIVE**, never `0/0=0`. Disabled reference directions are not equilibrium evidence. Pool occupancy is a separate sequestration question. Ledger closure is separate from kinetic validity, and neither follows from a short relaxation time or a small enzyme pool. No descriptive band selects KEEP/LUMP/QSSA/RAPID EQUILIBRIUM/CHEMOSTAT/DROP.

## Sixteen process views

Counts overlap across cards and are not additive. Pair counts include pairs touching the card. Tau values use the stored seconds convention; `R_tau=tau_slow/tau_fast`, so larger means greater proxy separation. All candidate slow-coordinate choices remain `NEED_MORE_INFORMATION`. Occupancy entries give each qualified active pool's maximum nonfree fraction separately; complete per-pool certificates and per-state member ratios remain in linked records.

{table(['Process', 'Reactions', 'Candidate states', 'Protected resources (examples)', 'Pairs', 'Timescale evidence', 'Occupancy / sequestration signal', 'QSS evidence', 'Equilibrium evidence', 'Ledger status', 'Human decision'], overview)}

{regression(data)}

## Open scientific choices

Define complete protected substrate-token membership and bound moieties where missing; choose candidate fast/slow coordinates and reconstruction maps; resolve absolute unit and initial-layer conventions where a future claim depends on them; specify the intended perturbation domain and full-versus-reduced acceptance checks. Exact event stoichiometry and pool certificates do not answer these choices. No kinetic transformation is evaluated or approved here.

{STATUS}
"""


def render(root: Path) -> dict[Path, str]:
    data = load(root)
    cards = data["prereg"]["process_cards"]
    if len(cards) != 16 or [c["process_id"] for c in cards] != [f"P{i:02d}" for i in range(1, 17)]:
        raise ValueError("Expected frozen P01..P16 process cards")
    out = {DOCS / "pnas2017_reduction_quick_reference.md": global_page(data)}
    out.update({DOCS / "process_quick_reference" / name: process_page(data, card, i)
                for i, (name, card) in enumerate(zip(FILENAMES, cards))})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true", help="compare existing docs without writing")
    args = parser.parse_args()
    generated = render(args.root)
    errors = []
    for rel, content in generated.items():
        target = args.root / rel
        encoded = content.encode("utf-8")
        if args.check:
            if not target.exists() or target.read_bytes() != encoded:
                errors.append(rel.as_posix())
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(encoded)
    if errors:
        print("Documentation differs: " + ", ".join(errors))
        return 1
    print(f"{'Verified' if args.check else 'Rendered'} {len(generated)} compact evidence documents; no human decision selected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
