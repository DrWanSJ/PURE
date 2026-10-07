#!/usr/bin/env python3
"""Build docs/visualization/reduction_reasoning_atlas.html.

Read-only generator. Every scientific input is read from a pinned git ref so the
artifact can be rebuilt from any branch and its provenance is unambiguous. No
source CSV or Markdown file is modified.

    python scripts/build_reduction_reasoning_atlas.py
    python scripts/build_reduction_reasoning_atlas.py --source-ref origin/main
    python scripts/build_reduction_reasoning_atlas.py --check   # assert only

Any failed assertion aborts the build; stale or inconsistent data is never
rendered silently.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

# Immutable scientific closeout. An explicit --source-ref can select a later
# reviewed evidence commit; default builds remain reproducible after tracking.
DEFAULT_SOURCE_REF = "829ce48b044329fd9bc789acef58872b8cd9037e"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO_ROOT, "scripts", "reduction_reasoning_atlas.template.html")
OUTPUT = os.path.join(REPO_ROOT, "docs", "visualization", "reduction_reasoning_atlas.html")

AUDIT = "models/pnas2017_full_reference/audit"
EVID = f"{AUDIT}/reduction_evidence_v0"
RED = "docs/reduction"

CANONICAL_SBML_SHA256 = "dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df"

EXPECTED_CLASSES = {"I": 42, "II-A": 57, "II-B": 91, "III": 22, "C": 29}
EXPECTED_SPECIES = 241
EXPECTED_REACTIONS = 968
EXPECTED_ANNOTATION = {
    "DIRECT_CHEMISTRY": 492,
    "GRAPH_PROPAGATED": 50,
    "HUMAN_REVIEW_REQUIRED": 0,
    "REFERENCE_DISABLED": 420,
    "SHARED_JUNCTION": 6,
}
CANDIDATE_LABELS = {"KEEP", "LUMP_CANDIDATE", "DROP_CANDIDATE"}

SOURCES = [
    f"{RED}/species_information_contract_summary.md",
    f"{RED}/species_information_contract_detailed.md",
    f"{RED}/human_audit_sync_20260930.md",
    f"{RED}/reaction_annotation_summary_v2.md",
    f"{RED}/reaction_annotation_method_v2.md",
    f"{RED}/reaction_level_annotation_v2.csv",
    f"{RED}/reaction_family_summary_v2.csv",
    f"{RED}/reduction_map.md",
    f"{RED}/reduction_decisions.csv",
    f"{RED}/human_reduction_review.md",
    f"{RED}/candidate_core_v0.md",
    f"{RED}/aminoacylation_qssa_quick_reference.md",
    f"{RED}/aminoacylation_A3a_final_status.md",
    f"{RED}/aminoacylation_A3bc_final_decision.md",
    f"{RED}/pnas2017_reduction_quick_reference.md",
    f"{RED}/pnas2017_reduction_evidence_method.md",
    f"{AUDIT}/species.csv",
    f"{AUDIT}/species_properties.csv",
    f"{AUDIT}/species_reduction_map.csv",
    f"{AUDIT}/reactions.csv",
    f"{AUDIT}/reaction_balance_audit.csv",
    f"{AUDIT}/modules.csv",
    f"{AUDIT}/aminoacylation_timescale.csv",
    f"{AUDIT}/aminoacylation_fast_states.csv",
    f"{AUDIT}/aminoacylation_enzyme_pool_conservation.csv",
    f"{EVID}/state_evidence.csv",
    f"{EVID}/reaction_evidence.csv",
    f"{EVID}/reverse_pair_evidence.csv",
    f"{EVID}/pool_evidence.csv",
    f"{EVID}/process_timescale_evidence.csv",
    f"{EVID}/verification_final_report.json",
    "docs/visualization/visualization_plan.md",
    "docs/pnas2017/g1_pnas_report.md",
]

CK7 = "results/reduction/r7_ck_first_order"
CK8 = "results/reduction/r8_ck_startup_layer"
CK_SOURCES = [
    f"{CK7}/advancement_decision.json", f"{CK7}/verification.json",
    f"{CK7}/condition_summary.csv", f"{CK7}/first_order_self_consistent_current.csv",
    f"{CK7}/first_order_postprocessing_current.csv", f"{CK7}/first_order_net_extent.csv",
    f"{CK8}/registration.json", f"{CK8}/manifest.json", f"{CK8}/verification.json",
    f"{CK8}/r7_read_only_reverification.json", f"{CK8}/decision.json",
    f"{CK8}/condition_summary.csv", f"{CK8}/extent_interval_decomposition.csv",
    f"{CK8}/current_time_localization.csv", f"{CK8}/fast_state_distance.csv",
    f"{CK8}/boundary_values.csv", f"{CK8}/evidence_navigation.json",
    "docs/reduction/r7_ck_first_order_summary.md",
    "docs/reduction/r8_ck_startup_layer_summary.md",
    "docs/reduction/r8_ck_startup_layer_preregistration.md",
]


class IntegrityError(Exception):
    """Raised when a repository assertion fails. The build must stop."""


class AssertionLog:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def check(self, aid: str, text: str, ok: bool, detail: str) -> bool:
        self.rows.append(
            {"id": aid, "text": text, "status": "PASS" if ok else "FAIL", "detail": detail}
        )
        if not ok:
            raise IntegrityError(f"[{aid}] {text} -- {detail}")
        return ok


class Source:
    """Reads text inputs from a pinned git ref (falls back to the working tree)."""

    def __init__(self, ref: str | None) -> None:
        self.ref = ref
        self.blobs: dict[str, str] = {}
        self.hashes: dict[str, str] = {}
        if ref:
            self.commit = subprocess.run(
                ["git", "rev-parse", ref], capture_output=True, text=True, cwd=REPO_ROOT
            ).stdout.strip()
            if not re.fullmatch(r"[0-9a-f]{40}", self.commit):
                raise IntegrityError(f"cannot resolve git ref {ref!r}")
        else:
            self.commit = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=REPO_ROOT
            ).stdout.strip()

    def text(self, path: str) -> str:
        if path not in self.blobs:
            if self.ref:
                proc = subprocess.run(
                    ["git", "show", f"{self.commit}:{path}"],
                    capture_output=True,
                    cwd=REPO_ROOT,
                )
                if proc.returncode != 0:
                    raise IntegrityError(
                        f"missing {path} at {self.ref} ({proc.stderr.decode('utf-8', 'replace').strip()})"
                    )
                data = proc.stdout.decode("utf-8")
            else:
                full = os.path.join(REPO_ROOT, path.replace("/", os.sep))
                if not os.path.exists(full):
                    raise IntegrityError(f"missing {path} in working tree")
                with open(full, encoding="utf-8", newline="") as fh:
                    data = fh.read()
            self.blobs[path] = data
            self.hashes[path] = hashlib.sha256(data.encode("utf-8")).hexdigest()
        return self.blobs[path]

    def rows(self, path: str) -> list[dict]:
        return list(csv.DictReader(io.StringIO(self.text(path))))

    def json(self, path: str):
        return json.loads(self.text(path))


def num(value: str):
    """Parse a numeric cell; non-numeric sentinels stay strings (never become 0)."""
    if value is None:
        return None
    s = value.strip()
    if s == "" or s.upper().startswith("N/A") or s.upper().startswith("UNKNOWN"):
        return s if s else None
    try:
        f = float(s)
    except ValueError:
        return s
    return int(f) if f.is_integer() and abs(f) < 1e15 and "." not in s and "e" not in s.lower() else f


def split_ids(value: str) -> list[str]:
    return [p.strip() for p in (value or "").split(";") if p.strip()]


def strip_md(value: str) -> str:
    return (value or "").strip().strip("*").strip("`")


# --------------------------------------------------------------------------- #
# species
# --------------------------------------------------------------------------- #

def parse_contract_classes(src: Source) -> dict[str, dict]:
    """Parse the approved 241-row rationale table from the detailed contract."""
    text = src.text(f"{RED}/species_information_contract_detailed.md")
    lines = text.split("\n")
    start = next(
        (i for i, ln in enumerate(lines) if ln.startswith("| # | Species")), None
    )
    if start is None:
        raise IntegrityError("rationale table header not found in species_information_contract_detailed.md")
    out: dict[str, dict] = {}
    for ln in lines[start + 2 :]:
        if not ln.startswith("|"):
            break
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 7:
            continue
        sid = strip_md(cells[1])
        out[sid] = {
            "cls": strip_md(cells[3]),
            "src_module": strip_md(cells[2]),
            "reduced_repr": strip_md(cells[4]),
            "why": cells[5].strip(),
            "must_keep": cells[6].strip(),
        }
    return out


def build_species(src: Source, a: AssertionLog):
    contract = parse_contract_classes(src)
    rmap = {r["species_id"]: r for r in src.rows(f"{AUDIT}/species_reduction_map.csv")}
    props = {r["sbml_id"]: r for r in src.rows(f"{AUDIT}/species_properties.csv")}
    base = {r["species_id"]: r for r in src.rows(f"{AUDIT}/species.csv")}
    state_ev = {r["species_id"]: r for r in src.rows(f"{EVID}/state_evidence.csv")}

    a.check(
        "A2",
        "每个 source species 在信息契约中恰好出现一次",
        len(contract) == len(rmap) == len(props) == len(base) == len(state_ev) == EXPECTED_SPECIES
        and set(contract) == set(rmap) == set(props) == set(base) == set(state_ev),
        f"contract={len(contract)} reduction_map={len(rmap)} properties={len(props)} "
        f"species={len(base)} state_evidence={len(state_ev)}",
    )

    counts: dict[str, int] = {}
    for rec in contract.values():
        counts[rec["cls"]] = counts.get(rec["cls"], 0) + 1

    a.check(
        "A1",
        "五个信息类别的 species 数量之和恰为 241，且与已批准契约逐项一致",
        counts == EXPECTED_CLASSES and sum(counts.values()) == EXPECTED_SPECIES,
        f"observed={counts} sum={sum(counts.values())} expected={EXPECTED_CLASSES}",
    )

    # Contract cross-rules recorded in the detailed document's verification table.
    bad_sink = [s for s, r in rmap.items() if r["primary_reduction_class"] == "DEGRADED_SINK" and contract[s]["cls"] != "C"]
    bad_enz = [s for s, r in rmap.items() if r["primary_reduction_class"] == "ENZYME_INTERMEDIATE" and contract[s]["cls"] != "II-A"]
    a.check(
        "A1b",
        "source DEGRADED_SINK 全部归入 Class C，source ENZYME_INTERMEDIATE 全部归入 Class II-A",
        not bad_sink and not bad_enz,
        f"degraded_not_C={bad_sink[:5]} enzyme_not_IIA={bad_enz[:5]}",
    )

    resources = ["ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr"]
    bad_res = [s for s in resources if contract[s]["cls"] != "I"]
    a.check(
        "A1c",
        "全部自由资源载体 (ATP/ADP/AMP/GTP/GDP/GMP/PO4/PPi/CP/Cr) 均为 Class I",
        not bad_res,
        f"not_class_I={bad_res}",
    )

    moiety_cols = [
        "n_peptide", "n_tRNA", "n_RS30S", "n_RS50S", "n_ATP", "n_ADP", "n_AMP",
        "n_GTP", "n_GDP", "n_GMP", "n_PO4", "n_PPi", "n_CP", "n_Cr",
    ]
    flag_cols = [
        "small_molecule", "macromolecule", "complex", "amino_acid", "tRNA",
        "aminoacyl_tRNA", "ribosomal_species", "translation_factor",
        "aminoacyl_tRNA_synthetase", "energy_regeneration_enzyme", "peptide_product",
    ]

    species = []
    for sid in sorted(contract, key=lambda s: (contract[s]["cls"], s)):
        c, r, p, b, e = contract[sid], rmap[sid], props[sid], base[sid], state_ev[sid]
        moieties = {k[2:]: num(r[k]) for k in moiety_cols if num(r[k]) not in (0, None)}
        flags = [k for k in flag_cols if (p.get(k) or "").strip().lower() == "true"]
        species.append({
            "id": sid,
            "name": p.get("sbml_name") or sid,
            "cls": c["cls"],
            "molecule_class": p.get("molecule_class") or "UNRESOLVED",
            "classification_basis": p.get("classification_basis") or "",
            "flags": flags,
            "functional_module": r.get("functional_module") or "",
            "contract_module": c["src_module"],
            "pool": "" if (r.get("candidate_coarse_variable") or "") == "" else r["candidate_coarse_variable"],
            "conservation_family": r.get("conservation_family") or "",
            "x0_reference": num(p.get("reference_initial_concentration")),
            "x0_sbml": num(p.get("sbml_initial_concentration")),
            "unit_status": p.get("reference_initial_unit_status") or "",
            "initial_source": p.get("initial_source") or "",
            "dynamic_status": p.get("dynamic_status") or "",
            "boundary": p.get("boundary_condition") or "",
            "why": c["why"],
            "must_keep": c["must_keep"],
            "reduced_repr": c["reduced_repr"],
            "rule_used": r.get("rule_used") or "",
            "confidence": r.get("confidence") or "",
            "needs_human_review": (r.get("needs_human_review") or "").lower() == "true",
            "map_reason": r.get("reason") or "",
            "level_a": split_ids(p.get("level_a_module_candidates")),
            "level_b": split_ids(p.get("level_b_subsystem_candidates")),
            "moieties": moieties,
            "formula": p.get("formula") or "",
            "net_charge": p.get("net_charge") or "",
            "formula_status": p.get("formula_charge_provenance") or "UNRESOLVED",
            "particle_relevance": num(r.get("detected_components")),
            "protected_output": (e.get("protected_output") or "").lower() == "true",
            "candidate_intermediate": (e.get("is_candidate_intermediate") or "").lower() == "true",
            "processes": split_ids(e.get("process_memberships")),
            "pool_status": e.get("pool_membership_status") or "",
            "max_bound_fraction": num(e.get("max_bound_fraction")),
            "qss_defect_median": num(e.get("qss_defect_median")),
            "qss_defect_p95": num(e.get("qss_defect_p95")),
            "qss_informative_fraction": num(e.get("qss_informative_fraction")),
            "turnover_tau_median": num(e.get("turnover_tau_median")),
            "traj_max": num(e.get("trajectory_max")),
            "traj_median": num(e.get("trajectory_median")),
            "initial_layer_flag": e.get("initial_layer_flag") or "",
            "resource_token_status": e.get("resource_token_status") or "",
            "reconstruction_requirement": e.get("reconstruction_requirement") or "",
            "source_sbml_sha256": b.get("source_sbml_sha256") or "",
        })

    a.check(
        "A7a",
        "每个 payload species 记录都保留原始 SBML ID 与 source SHA-256",
        all(s["id"] and s["source_sbml_sha256"] == CANONICAL_SBML_SHA256 for s in species),
        f"n={len(species)}",
    )
    return species, counts


# --------------------------------------------------------------------------- #
# reactions
# --------------------------------------------------------------------------- #

def compact_stoich(js: str) -> str:
    """'{"A":1.0}' -> 'A:1'; keeps original SBML species IDs verbatim."""
    try:
        d = json.loads(js) if js else {}
    except json.JSONDecodeError:
        return js or ""
    if isinstance(d, list):  # audit reactions.csv encoding
        return " + ".join(
            f"{e['species_id']}:{num(str(e.get('stoichiometry', 1)))}" for e in d
        )
    return " + ".join(f"{k}:{num(str(v))}" for k, v in d.items())


def compact_resource(js: str) -> str:
    try:
        d = json.loads(js) if js else {}
    except json.JSONDecodeError:
        return js or ""
    nz = {k: v for k, v in d.items() if float(v) != 0.0}
    return "; ".join(f"{k}{v:+g}" for k, v in nz.items()) or "no free-resource delta"


def build_reactions(src: Source, a: AssertionLog):
    ann = {r["reaction_id"]: r for r in src.rows(f"{RED}/reaction_level_annotation_v2.csv")}
    dec = {r["sbml_reaction_id"]: r for r in src.rows(f"{RED}/reduction_decisions.csv")}
    rx = {r["reaction_id"]: r for r in src.rows(f"{AUDIT}/reactions.csv")}
    bal = {r["sbml_reaction_id"]: r for r in src.rows(f"{AUDIT}/reaction_balance_audit.csv")}
    rev = {r["reaction_id"]: r for r in src.rows(f"{EVID}/reaction_evidence.csv")}

    a.check(
        "A3",
        "reaction 功能注释恰好覆盖 968 个唯一 combined reaction ID",
        len(ann) == len(dec) == len(rx) == len(bal) == len(rev) == EXPECTED_REACTIONS
        and set(ann) == set(dec) == set(rx) == set(bal) == set(rev),
        f"annotation={len(ann)} decisions={len(dec)} reactions={len(rx)} "
        f"balance={len(bal)} evidence={len(rev)}",
    )

    ev_counts: dict[str, int] = {}
    for r in ann.values():
        k = r["functional_annotation_status"]
        ev_counts[k] = ev_counts.get(k, 0) + 1

    a.check(
        "A4",
        "reaction functional-status 计数之和为 968，且与 v2 摘要逐项一致",
        ev_counts == {k: v for k, v in EXPECTED_ANNOTATION.items() if v}
        and sum(ev_counts.values()) == EXPECTED_REACTIONS,
        f"observed={ev_counts} sum={sum(ev_counts.values())}",
    )

    live_queue = sum(1 for r in ann.values() if (r["human_functional_review_required"] or "").lower() == "true")
    a.check(
        "A4b",
        "HUMAN_REVIEW_REQUIRED 功能注释行为 0（功能归属审查已完成）",
        ev_counts.get("HUMAN_REVIEW_REQUIRED", 0) == 0 and live_queue == 0,
        f"status_rows={ev_counts.get('HUMAN_REVIEW_REQUIRED', 0)} live_queue={live_queue}",
    )

    dec_counts: dict[str, int] = {}
    hr_counts: dict[str, int] = {}
    cand_counts: dict[str, int] = {}
    for r in dec.values():
        dec_counts[r["decision_status"]] = dec_counts.get(r["decision_status"], 0) + 1
        hr_counts[r["HUMAN_REVIEW_REQUIRED"]] = hr_counts.get(r["HUMAN_REVIEW_REQUIRED"], 0) + 1
        cand_counts[r["candidate_label"]] = cand_counts.get(r["candidate_label"], 0) + 1

    a.check(
        "A5",
        "reaction 科学降维决定状态全部保持 PENDING (968/968)",
        dec_counts == {"PENDING": EXPECTED_REACTIONS},
        f"decision_status={dec_counts}",
    )
    a.check(
        "A6",
        "候选标签未被转换成已批准标签",
        set(cand_counts) <= CANDIDATE_LABELS
        and hr_counts == {"True": EXPECTED_REACTIONS}
        and all(rev[i]["human_decision_status"] == "PENDING" for i in rev),
        f"candidate_label={cand_counts} HUMAN_REVIEW_REQUIRED={hr_counts}",
    )

    # Long prose fields repeat heavily across rows; intern them to keep the
    # embedded payload small without changing any value.
    prose_keys = [
        "biochemical_role", "reason_candidate", "required_assumption", "timescale_evidence",
        "conservation_moiety_consequence", "ATP_GTP_accounting_consequence",
        "PPi_Pi_consequence", "tRNA_accounting_consequence", "osmolarity_consequence",
        "ionic_strength_consequence", "observables_unrecoverable_if_applied",
        "data_needed_to_validate",
    ]
    intern: dict[str, int] = {}
    table: list[str] = []

    def ref(s: str) -> int:
        s = s or ""
        if s not in intern:
            intern[s] = len(table)
            table.append(s)
        return intern[s]

    reactions = []
    for rid in sorted(ann):
        n, d, s, b, e = ann[rid], dec[rid], rx[rid], bal[rid], rev[rid]
        reactions.append({
            "id": rid,
            "level_a": split_ids(n["level_a_module_candidates"]),
            "level_b": split_ids(n["level_b_subsystem_candidates"]),
            "family": n["reaction_family_id"],
            "stage": n["level_c_primary_stage"] or "",
            "contexts": split_ids(n["level_c_functional_contexts"]),
            "ev": n["functional_annotation_status"],
            "cd_type": n["mechanistic_reaction_type"],
            "anchor_basis": n.get("anchor_basis") or "",
            "direct_rule": n.get("direct_chemistry_rule") or "",
            "activity": n.get("reference_activity") or "",
            "k1": num(n.get("official_parameter_value")),
            "param_id": n.get("official_parameter_id") or "",
            "reactants": compact_stoich(n["reactants_json"]),
            "products": compact_stoich(n["products_json"]),
            "reverse": n.get("reverse_partner_id") or "",
            "rev_class": n.get("reversibility_class") or "",
            "cand": d["candidate_label"],
            "dec": d["decision_status"],
            "hr": d["HUMAN_REVIEW_REQUIRED"] == "True",
            "processes": split_ids(e.get("process_ids")),
            "particle_delta": num(b.get("net_tracked_particle_count_per_event")),
            "solute_delta": num(b.get("net_explicit_free_small_solute_count_per_event")),
            "resource_delta": compact_resource(e.get("resource_delta_json")),
            "protected_touched": split_ids(e.get("protected_species_touched")),
            "pools_touched": split_ids(e.get("protected_pool_touched")),
            "classes_touched": split_ids(e.get("contract_classes_touched")),
            "conservation_touched": split_ids(e.get("conservation_families_touched")),
            "rate_median": num(e.get("rate_median")),
            "rate_max": num(e.get("rate_max_abs")),
            "extent": num(e.get("directed_extent")),
            "pair_id": e.get("reverse_pair_id") or "",
            "pair_status": e.get("reverse_pair_status") or "",
            "eq_status": e.get("equilibrium_metric_status") or "",
            "ledger_status": e.get("ledger_evidence_status") or "",
            "bound_status": e.get("bound_moiety_status") or "",
            "elem_status": b.get("elemental_balance_status") or "",
            "moiety_status": b.get("moiety_balance_status") or "",
            "osmotic_status": b.get("osmotic_proxy_status") or "",
            "ionic_status": b.get("ionic_strength_status") or "",
            "prose": [ref(d.get(k, "")) for k in prose_keys],
            "source_sbml_sha256": s.get("source_sbml_sha256") or "",
        })

    a.check(
        "A7b",
        "每个 payload reaction 记录都保留原始 combined SBML ID 与 source SHA-256",
        all(r["id"] and r["source_sbml_sha256"] == CANONICAL_SBML_SHA256 for r in reactions),
        f"n={len(reactions)}",
    )
    return reactions, ev_counts, cand_counts, dec_counts, table, prose_keys


# --------------------------------------------------------------------------- #
# structure: modules / subsystems / families / processes / pools
# --------------------------------------------------------------------------- #

def build_structure(src: Source, reactions, a: AssertionLog):
    modules = src.rows(f"{AUDIT}/modules.csv")
    fams = src.rows(f"{RED}/reaction_family_summary_v2.csv")
    procs = src.rows(f"{EVID}/process_timescale_evidence.csv")
    pools = src.rows(f"{EVID}/pool_evidence.csv")
    pairs = src.rows(f"{EVID}/reverse_pair_evidence.csv")

    fam_total = sum(int(f["reaction_count"]) for f in fams)
    a.check(
        "A9",
        "reaction family 计数之和为 968",
        fam_total == EXPECTED_REACTIONS,
        f"families={len(fams)} sum={fam_total}",
    )

    entry_total = sum(int(m["reaction_entry_count"]) for m in modules)
    mapped_total = sum(int(m["mapped_combined_reaction_count"]) for m in modules)
    a.check(
        "A10",
        "26 个原始 subsystem 文件的 1098 条 reaction entry 折叠为 968 个唯一 combined reaction",
        len(modules) == 26 and entry_total == 1098 and mapped_total == 1098
        and len(set(r["id"] for r in reactions)) == 968,
        f"files={len(modules)} entries={entry_total} mapped={mapped_total}",
    )

    multi = sum(1 for r in reactions if len(r["level_b"]) > 1)
    single = sum(1 for r in reactions if len(r["level_b"]) == 1)
    a.check(
        "A10b",
        "884 个 combined reaction 只属于一个 subsystem，84 个属于多个（不是新反应）",
        single == 884 and multi == 84,
        f"single={single} multi={multi}",
    )

    a.check(
        "A11",
        "evidence 层覆盖 16 个 process、290 个 exact reverse pair、82 个 registered pool",
        len(procs) == 16 and len(pairs) == 290 and len(pools) == 82,
        f"processes={len(procs)} pairs={len(pairs)} pools={len(pools)}",
    )

    a.check(
        "A12",
        "全部 16 个 process 的 timescale_status 仍为 NEED_MORE_INFORMATION",
        all(p["timescale_status"] == "NEED_MORE_INFORMATION" for p in procs),
        f"{sorted(set(p['timescale_status'] for p in procs))}",
    )

    subsystems = [{
        "file": m["source_file"],
        "model_id": m["source_model_id"],
        "entries": int(m["reaction_entry_count"]),
        "mapped": int(m["mapped_combined_reaction_count"]),
        "sha256": m["source_entry_sha256"],
    } for m in modules]

    families = [{
        "id": f["reaction_family_id"],
        "count": int(f["reaction_count"]),
        "contexts": split_ids(f["functional_contexts"]),
        "hard_anchors": int(f["hard_anchor_count"]),
        "disabled_exact": int(f["disabled_exact_count"]),
        "human_review": int(f["human_functional_review_count"]),
        "subsystems": sorted(set(split_ids(f["source_subsystems"]))),
        "links": split_ids(f["cross_family_link_ids"]),
    } for f in fams]

    processes = [{
        "id": p["process_id"],
        "name": p["process_name"],
        "reaction_count": len(split_ids(p["reaction_ids"])),
        "candidate_state_count": int(p["candidate_state_count"]),
        "slow_interface_states": split_ids(p["slow_interface_state_ids"]),
        "tau_fast_min": num(p["tau_fast_min"]),
        "tau_fast_median": num(p["tau_fast_median"]),
        "tau_fast_max": num(p["tau_fast_max"]),
        "tau_slow_median": num(p["tau_slow_median"]),
        "R_tau_min": num(p["R_tau_min"]),
        "R_tau_median": num(p["R_tau_median"]),
        "R_tau_max": num(p["R_tau_max"]),
        "epsilon_tau_median": num(p["epsilon_tau_median"]),
        "stable_mode_min": num(p["stable_mode_count_min"]),
        "stable_mode_max": num(p["stable_mode_count_max"]),
        "structural_neutral": num(p["structural_neutral_mode_count"]),
        "ratio_informative_fraction": num(p["ratio_informative_fraction"]),
        "metric_status": p["metric_status"],
        "status": p["timescale_status"],
        "samples": int(p["primary_sample_count"]),
        "assumptions": p["assumptions"],
        "limitations": p["limitations"],
    } for p in procs]

    pool_records = [{
        "id": p["pool_id"],
        "members": split_ids(p["member_species_ids"]),
        "count": int(p["member_count"]),
        "free": p["free_species_id"],
        "free_basis": p["free_counterpart_basis"],
        "membership_status": p["membership_status"],
        "reference_conserved": (p["reference_conserved"] or "").lower() == "true",
        "unconditional_conserved": (p["unconditional_conserved"] or "").lower() == "true",
        "max_bound_fraction": num(p["max_bound_fraction"]),
        "free_total_ratio_median": num(p["free_total_ratio_median"]),
        "total_initial": num(p["total_initial"]),
        "sequestration_status": p["sequestration_metric_status"],
    } for p in pools]

    pair_counts = {
        "total": len(pairs),
        "disabled": sum(1 for p in pairs if p["pair_reference_status"] == "REFERENCE_DIRECTION_DISABLED"),
        "informative": sum(1 for p in pairs if num(p["informative_fraction"]) not in (None, 0, 0.0)),
    }

    return subsystems, families, processes, pool_records, pair_counts


# --------------------------------------------------------------------------- #
# aminoacylation case study
# --------------------------------------------------------------------------- #

CASE_STATES = ["Gly", "Met", "ATP", "AMP", "PPi", "GlyRS", "MetRS", "GlyAMP", "MetAMP",
               "GlyRS_GlyAMP", "MetRS_MetAMP", "tRNAGlyGCC", "tRNAfMetCAU",
               "GlytRNAGlyGCC", "MettRNAfMetCAU"]


def build_case_study(src: Source, species_by_id: dict, a: AssertionLog):
    ts = src.rows(f"{AUDIT}/aminoacylation_timescale.csv")
    fast = {r["fast_state"]: r for r in src.rows(f"{AUDIT}/aminoacylation_fast_states.csv")}
    pools = {p["pool_id"]: p for p in src.rows(f"{EVID}/pool_evidence.csv")}
    procs = {p["process_id"]: p for p in src.rows(f"{EVID}/process_timescale_evidence.csv")}

    lam = [float(r["lambda_stiff_fast_s^-1"]) for r in ts]
    tau = [float(r["tau_fast_stiff_s"]) for r in ts]
    eps = [float(r["epsilon_stiff"]) for r in ts]

    a.check(
        "A16",
        "aminoacylation 历史 timescale 记录中每一行都是 algebraic_manifold_derived=false",
        ts and all((r["algebraic_manifold_derived"] or "").lower() == "false" for r in ts),
        f"rows={len(ts)} distinct={sorted(set((r['algebraic_manifold_derived'] or '') for r in ts))}",
    )

    # Quoted historical statuses must literally exist in the archived documents;
    # nothing here is paraphrased into a new scientific claim.
    quotes = [
        (f"{RED}/aminoacylation_A3a_final_status.md", "FAILED_VALIDATION_ON_REFERENCE_DOMAIN"),
        (f"{RED}/aminoacylation_A3bc_final_decision.md", "FAILED_SMOKE_CLOSURE_FEASIBILITY"),
        (f"{RED}/aminoacylation_A3bc_final_decision.md", "BLOCKED_NUMERICAL_COORDINATE_DEFECT"),
        (f"{RED}/human_audit_sync_20260930.md", "does not approve any particular QSSA"),
    ]
    missing = [f"{tok} not in {path}" for path, tok in quotes if tok not in src.text(path)]
    a.check(
        "A17",
        "case study 引用的历史结论字符串逐字存在于其源文档中",
        not missing,
        "; ".join(missing) or f"{len(quotes)} quotes verified",
    )

    sync_text = src.text(f"{RED}/human_audit_sync_20260930.md")
    m = re.search(r"The failed R3 aminoacylation QSSA pilot[^\n]*(?:\n(?![\n#])[^\n]*)*", sync_text)
    r3_statement = " ".join(m.group(0).split()) if m else ""
    a.check(
        "A18",
        "human_audit_sync_20260930.md 中关于失败 R3 pilot 的原始陈述已被逐字提取",
        bool(r3_statement) and "does not reverse" in r3_statement,
        r3_statement[:120] or "not found",
    )

    def st(sid):
        s = species_by_id.get(sid)
        return None if s is None else {
            "id": sid, "cls": s["cls"], "x0": s["x0_reference"],
            "traj_max": s["traj_max"], "traj_median": s["traj_median"],
            "qss_defect_median": s["qss_defect_median"],
            "qss_defect_p95": s["qss_defect_p95"],
            "qss_informative_fraction": s["qss_informative_fraction"],
            "turnover_tau_median": s["turnover_tau_median"],
            "max_bound_fraction": s["max_bound_fraction"],
            "protected_output": s["protected_output"],
        }

    def pool(pid):
        p = pools.get(pid)
        return None if p is None else {
            "id": pid, "count": int(p["member_count"]), "free": p["free_species_id"],
            "max_bound_fraction": num(p["max_bound_fraction"]),
            "free_total_ratio_median": num(p["free_total_ratio_median"]),
            "total_initial": num(p["total_initial"]),
            "reference_conserved": (p["reference_conserved"] or "").lower() == "true",
            "unconditional_conserved": (p["unconditional_conserved"] or "").lower() == "true",
            "status": p["sequestration_metric_status"],
        }

    def proc(pid):
        p = procs.get(pid)
        return None if p is None else {
            "id": pid, "name": p["process_name"],
            "candidate_state_count": int(p["candidate_state_count"]),
            "tau_fast_min": num(p["tau_fast_min"]), "tau_fast_median": num(p["tau_fast_median"]),
            "tau_fast_max": num(p["tau_fast_max"]),
            "R_tau_median": num(p["R_tau_median"]), "R_tau_min": num(p["R_tau_min"]),
            "R_tau_max": num(p["R_tau_max"]),
            "epsilon_tau_median": num(p["epsilon_tau_median"]),
            "status": p["timescale_status"],
        }

    gly0 = species_by_id["Gly"]["x0_reference"]
    met0 = species_by_id["Met"]["x0_reference"]
    glyamp_max = float(fast["GlyAMP"]["max_conc_uM"])
    metamp_max = float(fast["MetAMP"]["max_conc_uM"])

    return {
        "timescale": {
            "samples": len(ts),
            "n_fast_states": int(ts[0]["n_fast_states"]),
            "n_slow_states": int(ts[0]["n_slow_states"]),
            "lambda_fast_min": min(lam), "lambda_fast_max": max(lam),
            "tau_fast_min": min(tau), "tau_fast_max": max(tau),
            "epsilon_min": min(eps), "epsilon_max": max(eps),
            "algebraic_manifold_derived": False,
            "time_range": [float(ts[0]["time_s"]), float(ts[-1]["time_s"])],
            "source": f"{AUDIT}/aminoacylation_timescale.csv",
        },
        "fast_states": [
            {"id": k, "enzyme": fast[k]["enzyme_membership"], "moiety": fast[k]["moiety_included"],
             "median": num(fast[k]["median_conc_uM"]), "max": num(fast[k]["max_conc_uM"]),
             "zero_at_start": (fast[k]["is_zero_at_reference_start"] or "").lower() == "true",
             "producing": int(fast[k]["n_reactions_producing"]),
             "consuming": int(fast[k]["n_reactions_consuming"])}
            for k in ["GlyAMP", "MetAMP", "GlyRS_GlyAMP", "MetRS_MetAMP"] if k in fast
        ],
        "sequestration": {
            "GlyRS_active_pool": pool("GlyRS_active_pool"),
            "MetRS_active_pool": pool("MetRS_active_pool"),
            "glyamp_fraction_of_gly0": glyamp_max / gly0 if gly0 else None,
            "metamp_fraction_of_met0": metamp_max / met0 if met0 else None,
            "gly0": gly0, "met0": met0,
            "glyamp_max": glyamp_max, "metamp_max": metamp_max,
        },
        "states": {sid: st(sid) for sid in CASE_STATES if sid in species_by_id},
        "processes": {"P01": proc("P01"), "P02": proc("P02")},
        "historical": [
            {"id": "A3a", "label": "selective / free-substrate QSSA",
             "status": "FAILED_VALIDATION_ON_REFERENCE_DOMAIN",
             "issue": "integrated free substrates plus algebraic complexes produced a structural sliding leak in the protected ledger",
             "source": f"{RED}/aminoacylation_A3a_final_status.md"},
            {"id": "A3b (21-state)", "label": "broad total-coordinate closure",
             "status": "FAILED_SMOKE_CLOSURE_FEASIBILITY",
             "issue": "lost feasibility during a GlyAMP-associated transient at about 2.498 s",
             "source": f"{RED}/aminoacylation_A3bc_final_decision.md"},
            {"id": "A3b-r12 (9-state)", "label": "restricted total-coordinate candidate",
             "status": "BLOCKED_NUMERICAL_COORDINATE_DEFECT",
             "issue": "better local behaviour on [1e-4, 10] s, but the full window did not complete; ledger-row scopes cut fast binding equilibria, leaving coordinate/ledger-definition issues",
             "source": f"{RED}/aminoacylation_A3bc_final_decision.md"},
        ],
        "r3_statement": r3_statement,
        "r3_source": f"{RED}/human_audit_sync_20260930.md",
        "verdict": {
            "species_information_decision": "APPROVED",
            "kinetic_elimination": "NOT_APPROVED",
            "reaction_decision_status": "PENDING",
        },
    }


# --------------------------------------------------------------------------- #
# provenance / verification
# --------------------------------------------------------------------------- #

def build_provenance(src: Source, a: AssertionLog):
    verif = src.json(f"{EVID}/verification_final_report.json")

    a.check(
        "A13",
        "evidence 层独立验证报告为 PASS，且 source_head 与记录的 main HEAD 一致",
        verif.get("status") == "PASS"
        and verif.get("source_head") == "3e22aeeb6124e2ad7d3373e0cf056383bf9c8c1e",
        f"status={verif.get('status')} source_head={verif.get('source_head')}",
    )
    a.check(
        "A14",
        "验证报告覆盖 968 reaction / 241 species / 290 pair / 16 process，968 个 kinetic 决定 PENDING，96 个 process box 未选，reduced model 为 NOT_VALIDATED",
        verif.get("reaction_coverage") == 968 and verif.get("species_coverage") == 241
        and verif.get("reverse_pairs") == 290 and verif.get("processes") == 16
        and verif.get("kinetic_decisions_pending") == 968
        and verif.get("unselected_process_boxes") == 96
        and verif.get("reduced_model_status") == "NOT_VALIDATED",
        json.dumps({k: verif.get(k) for k in (
            "reaction_coverage", "species_coverage", "reverse_pairs", "processes",
            "kinetic_decisions_pending", "unselected_process_boxes", "reduced_model_status")}),
    )

    # Touch every declared source so its blob hash is recorded and a missing
    # file aborts the build rather than silently dropping provenance.
    missing = []
    for p in SOURCES:
        try:
            src.text(p)
        except IntegrityError as exc:
            missing.append(str(exc))
    a.check(
        "A15",
        "全部声明的 source 文件在指定 ref 下都存在并已记录 SHA-256",
        not missing,
        "; ".join(missing[:3]) or f"{len(SOURCES)} files",
    )
    files = [{"path": p, "sha256": src.hashes[p]} for p in SOURCES]
    return {
        "source_ref": src.ref or "(working tree)",
        "source_commit": src.commit,
        "evidence_source_head": verif.get("source_head"),
        "verification_status": verif.get("status"),
        "verification_sha256": hashlib.sha256(
            json.dumps(verif, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "preregistration_sha256": verif.get("preregistration_sha256"),
        "canonical_sbml_sha256": CANONICAL_SBML_SHA256,
        "reduced_model_status": verif.get("reduced_model_status"),
        "kinetic_decisions_pending": verif.get("kinetic_decisions_pending"),
        "unselected_process_boxes": verif.get("unselected_process_boxes"),
        "numerical_crosschecks": verif.get("independent_numerical_crosschecks"),
        "pool_verification": verif.get("pool_verification"),
        "built_at": subprocess.check_output(
            ["git", "show", "-s", "--format=%cI", src.commit], cwd=REPO_ROOT, text=True
        ).strip(),
        "generator": "scripts/build_reduction_reasoning_atlas.py",
        "files": files,
    }


# --------------------------------------------------------------------------- #
# payload
# --------------------------------------------------------------------------- #

def build_ck(src: Source, a: AssertionLog) -> dict:
    """Add the bounded CK evidence without replacing the atlas's global schema."""
    for p in CK_SOURCES:
        src.text(p)
    manifest = src.json(f"{CK8}/manifest.json")
    verification = src.json(f"{CK8}/verification.json")
    registration = src.json(f"{CK8}/registration.json")
    decision = src.json(f"{CK8}/decision.json")
    r7decision = src.json(f"{CK7}/advancement_decision.json")
    expected = ["R3_BASE", "R3_ATP_LOW", "R3_TRNA_LOW"]
    a.check("CK1", "R8 三条件、原始 R7 谱系、诊断范围与不晋升状态",
            registration["conditions"] == expected and decision["conditions"] == expected
            and registration["parent_SHA"] == "20ca5215d949c9451b3e6fd4435c18991783ac29"
            and decision["promotion"] is False and decision["PURE_reduced_core"] == "NOT_VALIDATED"
            and decision["new_state_solves"] == decision["new_extent_ODE_solves"] == 0
            and not decision["matched_layer_implemented"] and not decision["h2_implemented"],
            json.dumps(decision, ensure_ascii=False))
    a.check("CK2", "R8 独立核验与逐文件 manifest SHA-256 一致",
            verification["status"] == "PASS_ENGINEERING_AND_EVIDENCE_ONLY"
            and verification["manifest_sha256"] == src.hashes[f"{CK8}/manifest.json"]
            and all(hashlib.sha256(src.text(p).encode("utf-8")).hexdigest() == h
                    for p, h in manifest["files"].items()), "Engineering verification is not scientific validation")
    a.check("CK3", "R7 formal / postprocessing 身份和两个 mandatory CK pair 保留",
            r7decision["recommendation"] == "CK_FIRST_ORDER_IMPROVES_EXTENT_NOT_CURRENT"
            and all(o["boundaries_s"] == [0, o["switch_s"], .001, .05, 1000]
                    and o["CK_pairs"] == ["re0000000332_MINUS_re0000000333", "re0000000336_MINUS_re0000000337"]
                    for o in registration["objects"]), "Postprocessing on z0 is diagnostic only")
    def numeric_rows(path):
        return [{k: (num(v) if k not in {"condition", "pair", "model", "window", "interval",
                    "diagnostic_interval", "R7_F_status", "R7_D_status", "CK_status",
                    "status", "label", "category", "maximum_definition"} else v)
                 for k, v in row.items()} for row in src.rows(path)]
    current = numeric_rows(f"{CK7}/first_order_self_consistent_current.csv")
    post = {(row["condition"], row["pair"], row["time_s"]): row
            for row in numeric_rows(f"{CK7}/first_order_postprocessing_current.csv")}
    extent = {(row["condition"], row["pair"], row["time_s"]): row
              for row in numeric_rows(f"{CK7}/first_order_net_extent.csv")}
    series = []
    for row in current:
        key = (row["condition"], row["pair"], row["time_s"])
        ex = extent[key]
        series.append(dict(condition=row["condition"], pair=row["pair"], time_s=row["time_s"],
              source=row["source_current"], zero=row["zero_order_current"], formal=row["first_order_current"],
              post=post[key]["first_order_current"], source_extent=ex["source_extent"],
              zero_extent=ex["zero_order_extent"], formal_extent=ex["formal_extent"], post_extent=ex["postprocessed_extent"]))
    a.check("CK4", "CK current / extent 系列严格来自已存储 R7 表",
            len(series) == len(post) == len(extent)
            and {r["condition"] for r in series} == set(expected), f"{len(series)} frozen rows; no solve")
    g1 = src.text("docs/pnas2017/g1_pnas_report.md")
    return dict(conditions=expected, objects=registration["objects"], decision=decision,
                r7_recommendation=r7decision["recommendation"],
                r7_scores=numeric_rows(f"{CK7}/condition_summary.csv"),
                summaries=numeric_rows(f"{CK8}/condition_summary.csv"),
                intervals=numeric_rows(f"{CK8}/extent_interval_decomposition.csv"),
                current_localization=numeric_rows(f"{CK8}/current_time_localization.csv"),
                fast_distance=numeric_rows(f"{CK8}/fast_state_distance.csv"), series=series,
                g1_status="PASS / CLOSED" if "**G1-PNAS = PASS / CLOSED.**" in g1 else "SEE_CANONICAL_REPORT",
                sources=[dict(path=p, sha256=src.hashes[p]) for p in CK_SOURCES],
                verification=verification["status"],
                uncertainty="原 R7 primary/probe、tight quadrature、cancellation；固定时刻另报告 Hermite/linear interpolation disagreement（不是严格误差界）。",
                authority="DERIVED_NAVIGATION_SUBORDINATE_TO_CANONICAL_STORED_EVIDENCE")

def build_payload(src: Source, a: AssertionLog) -> dict:
    species, class_counts = build_species(src, a)
    reactions, ev_counts, cand_counts, dec_counts, prose_table, prose_keys = build_reactions(src, a)
    subsystems, families, processes, pools, pair_counts = build_structure(src, reactions, a)
    provenance = build_provenance(src, a)
    case_study = build_case_study(src, {s["id"]: s for s in species}, a)
    ck = build_ck(src, a)

    # Level-A module roll-up. Memberships overlap by design; the unique event
    # count stays 968 and the overlap is reported rather than hidden.
    level_a: dict[str, int] = {}
    for r in reactions:
        for m in r["level_a"]:
            level_a[m] = level_a.get(m, 0) + 1

    payload = {
        "schema": "pnas2017_reduction_reasoning_atlas/v1",
        "provenance": provenance,
        "assertions": a.rows,
        "class_counts": class_counts,
        "species_total": len(species),
        "species": species,
        "reaction_total": len(reactions),
        "reactions": reactions,
        "prose_table": prose_table,
        "prose_keys": prose_keys,
        "annotation_counts": ev_counts,
        "candidate_counts": cand_counts,
        "decision_counts": dec_counts,
        "level_a_counts": level_a,
        "subsystems": subsystems,
        "families": families,
        "processes": processes,
        "pools": pools,
        "reverse_pairs": pair_counts,
        "case_study": case_study,
        "ck": ck,
    }

    a.check(
        "A8",
        "payload 保留 source SHA-256、preregistration 与 verification 的 provenance 引用",
        bool(provenance["canonical_sbml_sha256"] and provenance["preregistration_sha256"]
             and provenance["verification_sha256"] and provenance["source_commit"]),
        f"sbml={provenance['canonical_sbml_sha256'][:12]} "
        f"prereg={str(provenance['preregistration_sha256'])[:12]} "
        f"verif={provenance['verification_sha256'][:12]}",
    )
    return payload


def render(payload: dict) -> str:
    with open(TEMPLATE, encoding="utf-8") as fh:
        template = fh.read()
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # A literal "</script" inside JSON would terminate the inline script early.
    blob = blob.replace("</", "<\\/")
    marker = "/*__ATLAS_PAYLOAD__*/null"
    if marker not in template:
        raise IntegrityError(f"template placeholder {marker!r} not found in {TEMPLATE}")
    return template.replace(marker, blob)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-ref", default=DEFAULT_SOURCE_REF,
                    help=f"git ref holding the authoritative inputs (default: {DEFAULT_SOURCE_REF})")
    ap.add_argument("--working-tree", action="store_true",
                    help="read inputs from the working tree instead of a git ref")
    ap.add_argument("--check", action="store_true", help="run assertions only; write nothing")
    ap.add_argument("--output", default=OUTPUT)
    args = ap.parse_args()

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    ref = None if args.working_tree else args.source_ref
    src = Source(ref)
    a = AssertionLog()
    try:
        payload = build_payload(src, a)
    except IntegrityError as exc:
        print(f"\nASSERTION FAILED -- build stopped, nothing written.\n  {exc}\n", file=sys.stderr)
        for row in a.rows:
            print(f"  [{row['status']}] {row['id']}: {row['text']}", file=sys.stderr)
        return 1

    print(f"source ref      : {payload['provenance']['source_ref']}")
    print(f"source commit   : {payload['provenance']['source_commit']}")
    print(f"evidence HEAD   : {payload['provenance']['evidence_source_head']}")
    print(f"species classes : {payload['class_counts']} = {payload['species_total']}")
    print(f"annotation      : {payload['annotation_counts']} = {payload['reaction_total']}")
    print(f"candidates      : {payload['candidate_counts']}")
    print(f"decisions       : {payload['decision_counts']}")
    print("\nassertions:")
    for row in a.rows:
        print(f"  [{row['status']}] {row['id']}  {row['text']}")
        print(f"          {row['detail']}")

    if args.check:
        print("\n--check: no files written.")
        return 0

    html = render(payload)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    print(f"\nwrote {os.path.relpath(args.output, REPO_ROOT)} "
          f"({len(html.encode('utf-8')) / 1024:.0f} KiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
