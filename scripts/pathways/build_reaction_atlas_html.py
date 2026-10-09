#!/usr/bin/env python3
"""Build the offline HTML reading layer from the immutable Phase A atlas.

No scientific source or Phase A artifact is written. The output is one HTML
file with local CSS, JavaScript and compact JSON embedded at build time.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from verify_pathway_atlas import Validator, load_artifacts

ROOT = Path(__file__).resolve().parents[2]
PHASE = ROOT / "docs/reduction/pathways"
UI = Path(__file__).resolve().parent / "reaction_atlas_ui"

# Browsing titles, not new scientific classifications. Outside Phase A the
# titles never claim an approved mapping of individual reactions to substeps.
HIERARCHY = [
    ("RS", "RS / AMINOACYLATION", "氨基酸活化、tRNA 酰化与起始 tRNA 甲酰化", [
        ("RS_binding", "aaRS 底物装配", "氨基酸、ATP 和 tRNA 可按不同顺序进入酶复合物；解离方向独立保留。", ["enzyme + amino acid association", "enzyme + ATP association", "enzyme + tRNA association", "corresponding dissociation reactions"]),
        ("RS_activation", "aminoacyl-AMP 活化", "ATP 结合态转为 aminoacyl-AMP / PPi 中间体，并经明确步骤处理 PPi。", ["aminoacyl-AMP formation / PPi handling"]),
        ("RS_charging", "tRNA 氨酰化与酶恢复", "活化态招募 tRNA、转移氨基酸、释放 charged tRNA 与 AMP，并恢复酶。", ["aminoacyl transfer / product release / enzyme recovery"]),
        ("RS_to_INIT_formylation", "起始 tRNA 甲酰化", "Met-tRNA 到 fMet-tRNA 的源反应连接 aminoacylation 与 initiation。", ["Met-tRNA → fMet-tRNA"]),
    ]),
    ("INIT", "INITIATION", "起始复合物的多顺序装配与因子释放", [
        ("INIT_assembly", "起始复合物装配", "30S、mRNA 和 IF1 / IF2 / IF3 的结合与解离存在替代入口。", ["30S binding", "mRNA binding", "IF1 / IF2 / IF3 binding", "reverse dissociation paths"]),
        ("INIT_tRNA_recruitment", "起始 tRNA 招募", "招募 fMet-tRNA，保留真实 cargo 与核糖体复合物状态。", ["fMet-tRNA recruitment"]),
        ("INIT_energy_commitment", "IF2 核苷酸步骤", "GTP 装载、结合态转换和 PO4 处理是不同的原始事件。", ["GTP loading / conversion"]),
        ("INIT_70S_formation", "70S 形成", "真实 30S 与 50S 加入或拆分；完整原始复合物名称保留。", ["30S complex + 50S → 70S complex"]),
        ("INIT_factor_release", "起始因子释放", "形成 70S 后 IF 释放或再结合；源方向分别保留。", ["IF release"]),
    ]),
    ("ELONG", "ELONGATION", "两轮真实 Gly 加入及相关因子、tRNA 状态", [
        ("ELONG_aa_tRNA_delivery", "aa-tRNA 递送", "EF-Tu cargo 装配、递送和对应旁路保留各自原始反应。", ["EF-Tu/GTP carrier preparation", "ternary complex formation", "ribosome delivery"]),
        ("ELONG_energy_coupling", "延伸核苷酸耦合", "EF-Tu 与 EF-G 的核苷酸转换和因子复合物步骤。", ["EF-Tu nucleotide conversion", "EF-G nucleotide conversion"]),
        ("ELONG_peptide_formation", "两轮肽链增长", "源模型分别记录 fMet → fMet-Gly 与 fMet-Gly → fMet-Gly-Gly。", ["fMet → fMet-Gly", "fMet-Gly → fMet-Gly-Gly"]),
        ("ELONG_translocation", "核糖体移位", "核糖体 / tRNA 位置改变，按完整原始状态读取。", ["ribosome / tRNA positional transition"]),
        ("ELONG_tRNA_release", "去酰化 tRNA 释放", "去酰化 tRNA 离开延伸核糖体，以及对应逆向结合。", ["deacylated tRNA release"]),
    ]),
    ("TERM", "TERMINATION / RECYCLING", "RF1 / RF2 终止和 RRF / EF-G 核糖体回收", [
        ("TERM_factor_binding", "终止因子结合", "RF1 和 RF2 识别、结合或解离；不合并两种方向。", ["RF1 / RF2 recognition and binding"]),
        ("TERM_peptide_release", "肽产物释放", "带肽酰-tRNA 的原始复合物转为游离肽与终止后状态。", ["peptidyl-tRNA release chemistry"]),
        ("TERM_energy_coupling", "RF3 核苷酸步骤", "RF3 相关核苷酸装载、转换、因子及 PO4 释放。", ["RF3-associated nucleotide cycle"]),
        ("RECYCLE_disassembly", "核糖体拆分", "RRF / EF-G 装配及真实 70S 拆分源反应。", ["RRF / EF-G / ribosome splitting"]),
        ("RECYCLE_component_release", "回收组分释放", "拆分后的 tRNA、mRNA 和因子释放 / 再结合。", ["tRNA release", "mRNA release", "factor release"]),
    ]),
    ("ENERGY", "ENERGY REGENERATION", "CK、NDK、MK、PPiase 的原始微观反应", [
        ("EN_binding", "能源酶底物与产物结合", "分别查看四种酶的底物装配、产物释放和逆方向。", ["CK substrate / product binding", "NDK nucleotide binding", "MK nucleotide binding", "PPiase substrate / product binding"]),
        ("EN_energy_transfer", "磷酰基转移", "实际酶内化学转换与已审核的游离核苷酸转换保留各自源方程。", ["CK phosphotransfer", "NDK nucleotide phosphotransfer", "MK nucleotide phosphotransfer"]),
        ("EN_byproduct_processing", "PPi 处理", "结合态 PPi 到两个结合态 phosphate 的源反应；后续 PO4 释放独立保留。", ["PPi processing / two phosphate groups"]),
    ]),
    ("OTHER", "OTHER / DEG / INACTIVE", "失活和降解通道，保留全部方向与计量", [
        ("DEG_sink", "原始降解与失活出口", "被降解载体及其他释放组分的完整方程；参考参数为零仍可检索。", ["original degradation / inactive outlets"]),
    ]),
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def net_for_ids(ids, reactions):
    net = {}
    for rid in ids:  # Count occurrences, never deduplicate a reaction sequence.
        r = reactions[rid]
        for sign, key in ((-1, "reactants"), (1, "products")):
            for sid, value in r[key].items():
                net[sid] = net.get(sid, Fraction()) + sign * Fraction(value)
    return {s: str(n) for s, n in sorted(net.items()) if n}


def adapt():
    graph, phase_rows, markdown = load_artifacts(PHASE)
    validation = Validator().run(graph, phase_rows, markdown)
    if validation["structural_status"] != "PASS":
        raise ValueError("Phase A / canonical source inconsistency: " + json.dumps(validation))
    with (ROOT / "docs/reduction/reaction_index.csv").open(encoding="utf-8-sig", newline="") as stream:
        source_index = {r["reaction_id"]: r for r in csv.DictReader(stream)}
    if set(source_index) != set(graph["reactions"]):
        raise ValueError("Existing source index differs from Phase A source inventory")
    reactions = {}
    for rid, r in graph["reactions"].items():
        index = source_index[rid]
        if set(index["all_stages"].split(";")) != set(r["level_c"]):
            raise ValueError("Reviewed classifications disagree at " + rid)
        reactions[rid] = {
            "reactants": r["reactants"], "products": r["products"], "equation": r["equation"],
            "level_c": r["level_c"], "family": r["reaction_family"], "reverse": r["reverse_reaction_id"],
            "reference_activity": r["reference_activity"], "reference_parameter": r["reference_parameter"],
            "reference_pair_activity": r["reference_pair_activity"], "mechanism": r["mechanistic_reaction_type"],
            "source_refs": json.loads(index["source_subsystem_reaction_refs_json"]),
        }
    paths, transitions, modules = {}, {}, {}
    for enzyme, m in graph["modules"].items():
        modules[enzyme] = {
            "carrier_states": m["carrier_states"], "reaction_ids": m["reaction_ids"],
            "branches": {b["state"]: b["outgoing_reaction_ids"] for b in m["branches"]},
            "rejoins": {b["state"]: b["incoming_reaction_ids"] for b in m["rejoins"]},
            "return_loops": m["return_loops"], "sccs": m["sccs"], "path_ids": [p["id"] for p in m["paths"]],
        }
        for t in m["transitions"]:
            transitions[t["reaction_id"]] = {
                "enzyme": enzyme, "carrier_before": t["carrier_before"], "carrier_after": t["carrier_after"],
                "other_reactants": t["other_reactants"], "other_products": t["other_products"],
                "tracked_carriers": t["tracked_carriers"], "types": t["types"],
            }
        for p in m["paths"]:
            net = net_for_ids(p["reaction_ids"], reactions)
            enzyme_balanced = all(not Fraction(net.get(s, "0")) for s in m["carrier_states"])
            cycle = ("PRODUCTIVE_PATH" in p["types"] and p["start"] == p["end"] == enzyme
                     and enzyme_balanced and Fraction(net.get(p["target_product"], "0")) > 0)
            paths[p["id"]] = {k: p[k] for k in ("id", "title", "reaction_ids", "states", "start", "end", "types", "target_product", "reference_feasible", "rejoins", "shared_continuations", "evidence_status", "scientific_status")}
            paths[p["id"]].update({"enzyme": enzyme, "net_reference": net, "complete_catalytic_cycle": cycle})
    stages = sorted({c for r in reactions.values() for c in r["level_c"]})
    groups = []
    for key, title, description, definitions in HIERARCHY:
        contexts = []
        for stage, caption, function, topics in definitions:
            ids = sorted(rid for rid, r in reactions.items() if stage in r["level_c"])
            substeps = []
            for number, topic in enumerate(topics):
                members = ids
                status = "SUBSTEP_MAPPING_NOT_VALIDATED"
                if stage == "RS_binding":
                    status = "SOURCE_DERIVED_UI_GROUPING"
                    members = []
                    for rid in ids:
                        t = transitions[rid]
                        r = reactions[rid]
                        enzyme = t["enzyme"]
                        aa, trna = ("Gly", "tRNAGlyGCC") if enzyme == "GlyRS" else ("Met", "tRNAfMetCAU")
                        ligands = (aa, "ATP", trna)
                        if number < 3 and t["other_reactants"] == {ligands[number]: "1"} and not t["other_products"]:
                            members.append(rid)
                        elif number == 3 and r["mechanism"] == "DISSOCIATION":
                            members.append(rid)
                substeps.append({"id": stage + ":" + str(number), "title": topic, "reaction_ids": sorted(members), "mapping_status": status})
            contexts.append({"id": stage, "caption": caption, "function": function, "reaction_ids": ids, "substeps": substeps})
        groups.append({"id": key, "title": title, "description": description, "contexts": contexts})
    if {c["id"] for g in groups for c in g["contexts"]} != set(stages):
        raise ValueError("Browsing hierarchy must preserve all reviewed Level-C contexts")
    return {
        "metadata": {"schema_version": 1, "source_species": 241, "source_reactions": 968,
                     "phase_a_reactions": 134, "representative_paths": 20, "remaining_pathways": 834,
                     "scientific_status": "HTML_PROTOTYPE_READY_FOR_HUMAN_REVIEW",
                     "scope": "PHASE_A_PATHWAYS_ONLY", "phase_b": "PHASE_B_NOT_AUTHORIZED",
                     "provenance": graph["source_provenance"],
                     "phase_a_inputs": {p.name: digest(p) for p in [PHASE / n for n in (
                         "glyrs_metrs_graph.json", "glyrs_metrs_pathway_index.csv", "glyrs_metrs_sample.md", "glyrs_metrs_review.md", "pathway_first_protocol_v1.md", "validation_report.json")]},
                     "hierarchy_titles_authority": "UI_READING_TITLES_NOT_NEW_SCIENTIFIC_LABELS"},
        "species": graph["species"], "reactions": reactions, "level_c_contexts": stages, "groups": groups,
        "phase_a_ids": graph["coverage"]["phase_a_reaction_ids"], "noncarrier_ids": graph["noncarrier_reactions"],
        "paths": paths, "transitions": transitions, "modules": modules, "boundary_links": graph["boundary_links"],
    }


def build(output):
    data = adapt()
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    html = (UI / "template.html").read_text(encoding="utf-8")
    for marker, value in (("<!--ATLAS_CSS-->", (UI / "atlas.css").read_text(encoding="utf-8")),
                          ("<!--ATLAS_DATA-->", payload),
                          ("<!--ATLAS_JS-->", (UI / "atlas.js").read_text(encoding="utf-8"))):
        if html.count(marker) != 1:
            raise ValueError("Template insertion must be unique: " + marker)
        html = html.replace(marker, value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes((html.rstrip() + "\n").encode("utf-8"))
    print(json.dumps({"output": str(output), "bytes": output.stat().st_size, "sha256": digest(output),
                      "source_species": 241, "source_reactions": 968, "phase_a_reactions": 134,
                      "representative_paths": 20, "scientific_status": data["metadata"]["scientific_status"]}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PHASE / "reaction_atlas_prototype.html")
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
