#!/usr/bin/env python3
"""Source-bound Phase A pathway atlas. Does not construct a reduced model.

Run from any directory: python scripts/pathways/build_pathway_atlas.py
Only --output-dir (default docs/reduction/pathways) is written.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import csv
from fractions import Fraction
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

import networkx as nx

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
AUTHOR = "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
SB = "{http://www.sbml.org/sbml/level2/version4}"
MM = "{http://www.w3.org/1998/Math/MathML}"
RS_LABELS = {"RS_binding", "RS_activation", "RS_charging"}
CONFIG = {
    "GlyRS": {"aa": "Gly", "trna": "tRNAGlyGCC", "charged": "GlytRNAGlyGCC"},
    "MetRS": {"aa": "Met", "trna": "tRNAfMetCAU", "charged": "MettRNAfMetCAU"},
}


def csv_rows(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_text(path, content):
    path.write_bytes(content.encode("utf-8"))


def math_value(node):
    tag = node.tag.removeprefix(MM)
    if tag == "math":
        assert len(node) == 1
        return math_value(node[0])
    if tag == "cn":
        value = Fraction((node.text or "").strip())
        if node.get("type") in {"rational", "e-notation"}:
            assert len(node) == 1 and node[0].tag == MM + "sep"
            second = Fraction(node[0].tail.strip())
            return value / second if node.get("type") == "rational" else value * Fraction(10) ** int(second)
        assert not list(node)
        return value
    if tag == "apply":
        op = node[0].tag.removeprefix(MM)
        args = [math_value(n) for n in node[1:]]
        if op == "plus":
            return sum(args, Fraction())
        if op == "times":
            value = Fraction(1)
            for arg in args:
                value *= arg
            return value
        if op == "minus" and len(args) in (1, 2):
            return -args[0] if len(args) == 1 else args[0] - args[1]
        if op == "divide" and len(args) == 2:
            return args[0] / args[1]
        if op == "power" and len(args) == 2 and args[1].denominator == 1:
            return args[0] ** int(args[1])
    raise ValueError(f"Unsupported constant stoichiometry: {ET.tostring(node)!r}")


def side(node, name):
    values = defaultdict(Fraction)
    for ref in node.findall(f"{SB}listOf{name}/{SB}speciesReference"):
        math = ref.find(f"{SB}stoichiometryMath/{MM}math")
        value = math_value(math) if math is not None else Fraction(ref.get("stoichiometry", "1"))
        assert value > 0
        values[ref.attrib["species"]] += value
    return {s: str(v) for s, v in sorted(values.items())}


def equation(reactants, products):
    def render(values):
        return " + ".join(("" if Fraction(v) == 1 else v + " ") + s for s, v in sorted(values.items())) or "0"
    return render(reactants) + " -> " + render(products)


def fingerprint(path, authority):
    return {"path": path, "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), "authority": authority}


def read_source():
    provenance = [fingerprint(SOURCE, "CANONICAL_SBML"), fingerprint(AUTHOR, "AUTHOR_REFERENCE_PARAMETERS")]
    paths = ["reaction_level_annotation_v2.csv", "reaction_family_summary_v2.csv", "reaction_cross_family_links_v2.csv",
             "reaction_annotation_method_v2.md", "reaction_index.csv", "reaction.md", "reduction_map.md", "human_reduction_review.md"]
    provenance += [fingerprint("docs/reduction/" + path, "REVIEWED_LEVEL_C_V2" if path.startswith("reaction_level_annotation") else "CONTEXT_ONLY") for path in paths]
    annotations = {r["reaction_id"]: r for r in csv_rows("docs/reduction/reaction_level_annotation_v2.csv")}
    with zipfile.ZipFile(ROOT / AUTHOR) as archive:
        members = [p for p in archive.namelist() if p.endswith("fMGG_synthesis_parameters.csv")]
        assert len(members) == 1
        raw = archive.read(members[0])
        parameter_provenance = {**provenance[1], "member": members[0], "member_sha256": hashlib.sha256(raw).hexdigest()}
        decoded = raw.decode("utf-8-sig").replace("\r\r\n", "\n").replace("\r\n", "\n")
        parameters = {r["Name"]: r["Value"] for r in csv.DictReader(io.StringIO(decoded))}
    model = ET.parse(ROOT / SOURCE).getroot().find(SB + "model")
    species = {s.attrib["id"]: {"name": s.get("name", s.attrib["id"])} for s in model.findall(f"{SB}listOfSpecies/{SB}species")}
    reactions = {}
    for node in model.findall(f"{SB}listOfReactions/{SB}reaction"):
        rid = node.attrib["id"]
        assert rid not in reactions
        a = annotations[rid]
        reactants, products = side(node, "Reactants"), side(node, "Products")
        assert set(reactants) | set(products) <= species.keys()
        parameter = parameters[rid + "_k1"]
        assert Fraction(parameter) == Fraction(a["official_parameter_value"])
        assert Fraction(parameter) >= 0
        reactions[rid] = {
            "reactants": reactants, "products": products, "equation": equation(reactants, products),
            "modifiers": sorted(n.attrib["species"] for n in node.findall(f"{SB}listOfModifiers/{SB}modifierSpeciesReference")),
            "source_reversible": node.get("reversible", "true") == "true",
            "level_c": sorted(filter(None, a["level_c_functional_contexts"].split(";"))),
            "reaction_family": a["reaction_family_id"], "reverse_reaction_id": None,
            "reference_activity": "REFERENCE_DISABLED" if Fraction(parameter) == 0 else "NONZERO_PARAMETER",
            "reference_pair_activity": a["reference_activity"],
            "reference_parameter": parameter, "mechanistic_reaction_type": a["mechanistic_reaction_type"],
            "source_provenance": [{**provenance[0], "reaction_id": rid, "evidence": "EXTRACTED"},
                                  {**provenance[2], "reaction_id": rid, "evidence": "EXTRACTED"},
                                  {**parameter_provenance, "parameter_id": rid + "_k1", "evidence": "EXTRACTED"}],
        }
    signatures = defaultdict(list)
    for rid, r in reactions.items():
        signatures[(compact(r["reactants"]), compact(r["products"]), tuple(r["modifiers"]))].append(rid)
    for rid, r in reactions.items():
        reverse = signatures[(compact(r["products"]), compact(r["reactants"]), tuple(r["modifiers"]))]
        assert len(reverse) <= 1
        r["reverse_reaction_id"] = reverse[0] if reverse else None
    assert len(species) == 241 and len(reactions) == 968 and len(annotations) == 968
    return species, dict(sorted(reactions.items())), provenance


def petri(reactions):
    arcs, stoichiometry = [], {}
    for rid, r in reactions.items():
        for s, v in r["reactants"].items():
            arcs.append({"source": s, "target": rid, "stoichiometry": v, "role": "reactant"})
        for s, v in r["products"].items():
            arcs.append({"source": rid, "target": s, "stoichiometry": v, "role": "product"})
        net = {s: Fraction(r["products"].get(s, "0")) - Fraction(r["reactants"].get(s, "0")) for s in set(r["reactants"]) | set(r["products"])}
        stoichiometry[rid] = {s: str(v) for s, v in sorted(net.items()) if v}
    return {"arcs": arcs, "stoichiometry": stoichiometry}


def transition(rid, r, carriers, enzyme, config):
    before = sorted(set(r["reactants"]) & carriers)
    after = sorted(set(r["products"]) & carriers)
    types = []
    if r["reverse_reaction_id"]:
        types.append("REVERSE_EDGE")  # symmetric relation; never claims a preferred chemical direction
    if r["reference_activity"] == "REFERENCE_DISABLED":
        types.append("REFERENCE_DISABLED")
    if len(before) != 1 or len(after) != 1:
        types.append("UNRESOLVED")
    tracked = [{"carrier": enzyme, "before": before, "after": after, "evidence": "INFERRED_IDENTITY_PROJECTION"}]
    token = config["trna"]
    trna_before = sorted(s for s in r["reactants"] if token in s)
    trna_after = sorted(s for s in r["products"] if token in s)
    if trna_before or trna_after:
        tracked.append({"carrier": token, "before": trna_before, "after": trna_after, "evidence": "INFERRED_IDENTITY_PROJECTION"})
    return {
        "reaction_id": rid, "carrier_before": before, "carrier_after": after,
        "other_reactants": {s: v for s, v in r["reactants"].items() if s not in before},
        "other_products": {s: v for s, v in r["products"].items() if s not in after},
        "level_c": r["level_c"], "reaction_family": r["reaction_family"],
        "reverse_reaction_id": r["reverse_reaction_id"], "reference_activity": r["reference_activity"],
        "mechanistic_reaction_type": r["mechanistic_reaction_type"], "source_provenance": r["source_provenance"],
        "types": types, "tracked_carriers": tracked, "simultaneous_requirements": r["reactants"],
    }


def shortest(transitions, start, end, allowed=lambda t: True):
    """Deterministic directed BFS; no all-simple-paths or cycle enumeration."""
    if start == end:
        return []
    outgoing = defaultdict(list)
    for t in transitions:
        if len(t["carrier_before"]) == len(t["carrier_after"]) == 1 and allowed(t):
            outgoing[t["carrier_before"][0]].append(t)
    queue = deque([(start, [])])
    seen = {start}
    while queue:
        state, path = queue.popleft()
        for t in sorted(outgoing[state], key=lambda t: t["reaction_id"]):
            following = t["carrier_after"][0]
            next_path = path + [t["reaction_id"]]
            if following == end:
                return next_path
            if following not in seen:
                seen.add(following)
                queue.append((following, next_path))
    raise ValueError(f"No witnessed carrier route {start} -> {end}")


def through(transitions, milestones):
    result = []
    for start, end in zip(milestones, milestones[1:]):
        # Milestones select a biological question; BFS retrieves actual source IDs.
        result.extend(shortest(transitions, start, end, lambda t: "DEG_sink" not in t["level_c"]))
    return result


def build_paths(enzyme, config, transitions):
    aa, trna, charged = config["aa"], config["trna"], config["charged"]
    E = enzyme
    ternary = f"{E}_{aa}_ATP_{trna}"
    binary = f"{E}_{aa}_ATP"
    activated = f"{E}_{aa}AMP_PPi"
    adenylate = f"{E}_{aa}AMP"
    bound_activated = f"{activated}_{trna}"
    bound_adenylate = f"{adenylate}_{trna}"
    charged_complex = f"{E}_AMP_{charged}"
    by_id = {t["reaction_id"]: t for t in transitions}
    paths = []

    def add(title, ids, productive=False):
        assert ids
        steps = [by_id[rid] for rid in ids]
        states = [steps[0]["carrier_before"][0]] + [t["carrier_after"][0] for t in steps]
        for state, step in zip(states, steps):
            assert step["carrier_before"] == [state]
        paths.append({
            "id": f"{E}-P{len(paths) + 1:02d}", "title": title,
            "types": ["PRODUCTIVE_PATH", "RETURN_LOOP"] if productive else ["ALTERNATIVE_ENTRY"],
            "states": states, "reaction_ids": ids, "steps": steps, "start": states[0], "end": states[-1],
            "target_product": charged if productive else None,
            "reference_feasible": all(t["reference_activity"] != "REFERENCE_DISABLED" for t in steps),
            "evidence_status": "STRUCTURALLY_SUPPORTED", "scientific_status": "HUMAN_REVIEW_REQUIRED", "rejoins": [],
        })

    main = [E, f"{E}_{aa}", binary, ternary, bound_activated, bound_adenylate, charged_complex, f"{E}_AMP", E]
    add(f"{aa}-first：tRNA 在活化前结合，charged tRNA 先释放", through(transitions, main), True)
    add("ATP-first entry", through(transitions, [E, f"{E}_ATP", binary]))
    # Four remaining association orders; stop at the common ternary complex.
    for order in [(trna, aa, "ATP"), (trna, "ATP", aa), (aa, trna, "ATP"), ("ATP", trna, aa)]:
        state, ids = E, []
        for substrate in order:
            candidates = [t for t in transitions if t["carrier_before"] == [state]
                          and t["other_reactants"] == {substrate: "1"} and not t["other_products"]
                          and t["level_c"] == ["RS_binding"]]
            assert len(candidates) == 1, (E, order, state, candidates)
            chosen = candidates[0]
            ids.append(chosen["reaction_id"])
            state = chosen["carrier_after"][0]
        assert state == ternary
        add(" → ".join(order) + " entry", ids)
    add("先活化、释放 PPi，再结合 tRNA", through(transitions, [E, f"{E}_{aa}", binary, activated, adenylate,
        bound_adenylate, charged_complex, f"{E}_AMP", E]), True)
    add("先活化、结合 tRNA，再释放 PPi", through(transitions, [E, f"{E}_{aa}", binary, activated, bound_activated,
        bound_adenylate, charged_complex, f"{E}_AMP", E]), True)
    add("产物出口替代：AMP 先释放，再释放 charged tRNA", through(transitions, [E, f"{E}_{aa}", binary, ternary,
        bound_activated, bound_adenylate, charged_complex, f"{E}_{charged}", E]), True)
    add("游离 aminoacyl-AMP 再结合入口", through(transitions, [E, adenylate]))
    # Entry paths rejoin at their endpoint. Complete cycles separately identify
    # a witnessed shared reaction suffix after their alternative section.
    for p in paths:
        for q in paths:
            if q["id"] >= p["id"]:
                continue
            if p["end"] != E and p["end"] in q["states"][1:]:
                state = p["end"]
                p["rejoins"].append({"path_id": q["id"], "state": state})
                if "REJOIN" not in p["types"]:
                    p["types"].append("REJOIN")
        p["shared_continuations"] = []
        if "PRODUCTIVE_PATH" in p["types"]:
            for q in paths:
                if q["id"] >= p["id"] or "PRODUCTIVE_PATH" not in q["types"]:
                    continue
                count = 0
                for a, b in zip(reversed(p["reaction_ids"]), reversed(q["reaction_ids"])):
                    if a != b:
                        break
                    count += 1
                if count and count < min(len(p["reaction_ids"]), len(q["reaction_ids"])):
                    p["shared_continuations"].append({"path_id": q["id"], "state": p["states"][-count - 1],
                                                      "reaction_ids": p["reaction_ids"][-count:]})
    return paths


def build_module(enzyme, config, species, reactions):
    carriers = {s for s in species if s == enzyme or s.startswith(enzyme + "_")}
    ids = [rid for rid, r in reactions.items() if (set(r["reactants"]) | set(r["products"])) & carriers]
    transitions = [transition(rid, reactions[rid], carriers, enzyme, config) for rid in ids]
    outgoing, incoming = defaultdict(list), defaultdict(list)
    graph = nx.DiGraph()
    graph.add_nodes_from(sorted(carriers))
    for t in transitions:
        for state in t["carrier_before"]:
            outgoing[state].append(t["reaction_id"])
        for state in t["carrier_after"]:
            incoming[state].append(t["reaction_id"])
        if len(t["carrier_before"]) == len(t["carrier_after"]) == 1:
            graph.add_edge(t["carrier_before"][0], t["carrier_after"][0])
    components = sorted((sorted(s) for s in nx.strongly_connected_components(graph)), key=lambda s: s[0])
    sccs = [{"id": f"{enzyme}-SCC{i + 1:02d}", "members": members,
             "cyclic": len(members) > 1 or graph.has_edge(members[0], members[0])} for i, members in enumerate(components)]
    membership = {s: c["id"] for c in sccs for s in c["members"]}
    condensation = sorted({(membership[a], membership[b]) for a, b in graph.edges if membership[a] != membership[b]})
    condensed = nx.DiGraph()
    condensed.add_nodes_from(c["id"] for c in sccs)
    condensed.add_edges_from(condensation)
    assert nx.is_directed_acyclic_graph(condensed)
    cross = []
    for state in sorted(carriers):
        for source_id in incoming[state]:
            for target_id in outgoing[state]:
                a, b = reactions[source_id], reactions[target_id]
                if source_id != target_id and "DEG_sink" not in a["level_c"] + b["level_c"] and a["reaction_family"] != b["reaction_family"]:
                    cross.append({"from_reaction_id": source_id, "to_reaction_id": target_id, "state": state})
    cross_ids = {x[k] for x in cross for k in ["from_reaction_id", "to_reaction_id"]}
    for t in transitions:
        if len(outgoing[t["carrier_before"][0]]) > 1:
            t["types"].append("COMPETITIVE_BRANCH")
        if len(incoming[t["carrier_after"][0]]) > 1:
            t["types"].append("REJOIN")
        if t["reaction_id"] in cross_ids:
            t["types"].append("CROSS_FAMILY_LINK")
    loops, seen_loops = [], set()
    nondeg = lambda t: "DEG_sink" not in t["level_c"]
    by_id = {t["reaction_id"]: t for t in transitions}
    for t in transitions:
        if not nondeg(t):
            continue
        a, b = t["carrier_before"][0], t["carrier_after"][0]
        try:
            ids_loop = [t["reaction_id"]] + shortest(transitions, b, a, nondeg)
        except ValueError:
            continue
        canonical = min(tuple(ids_loop[i:] + ids_loop[:i]) for i in range(len(ids_loop)))
        if canonical in seen_loops:
            continue
        seen_loops.add(canonical)
        states = [a] + [by_id[rid]["carrier_after"][0] for rid in ids_loop]
        assert states[0] == states[-1]
        loops.append({"id": f"{enzyme}-L{len(loops) + 1:02d}", "reaction_ids": ids_loop, "states": states,
                      "type": "RETURN_LOOP", "reference_feasible": all(reactions[rid]["reference_activity"] != "REFERENCE_DISABLED" for rid in ids_loop)})
    paths = build_paths(enzyme, config, transitions)
    enabled = nx.DiGraph()
    enabled.add_nodes_from(sorted(carriers))
    enabled_ids = [t["reaction_id"] for t in transitions if t["reference_activity"] != "REFERENCE_DISABLED"]
    enabled.add_edges_from((t["carrier_before"][0], t["carrier_after"][0]) for t in transitions if t["reaction_id"] in enabled_ids)
    enabled_components = sorted((sorted(c) for c in nx.strongly_connected_components(enabled)), key=lambda c: c[0])
    return {"carrier_states": sorted(carriers), "reaction_ids": ids, "transitions": transitions,
            "branches": [{"state": s, "outgoing_reaction_ids": sorted(v)} for s, v in sorted(outgoing.items()) if len(v) > 1],
            "rejoins": [{"state": s, "incoming_reaction_ids": sorted(v)} for s, v in sorted(incoming.items()) if len(v) > 1],
            "sccs": sccs, "condensation_edges": [list(e) for e in condensation], "return_loops": loops,
            "cross_family_links": cross, "paths": paths,
            "parameter_enabled_view": {"reaction_ids": enabled_ids, "scc_members": enabled_components,
                                       "branch_states": sorted(s for s in carriers if enabled.out_degree(s) > 1),
                                       "rejoin_states": sorted(s for s in carriers if enabled.in_degree(s) > 1)},
            "unresolved_reaction_ids": [t["reaction_id"] for t in transitions if "UNRESOLVED" in t["types"]]}


def sample_markdown(data):
    R = data["reactions"]
    lines = ["# PNAS2017 Reaction Pathway Atlas — GlyRS / MetRS 样板", "",
             "源网：241 species / 968 reactions。Phase A：134 条原始反应；其余 834 条保留在底层 Petri 网，尚未进行路径重构。", "",
             "本样板沿真实载体状态阅读。`PRODUCTIVE_PATH` 仅表示结构上到达 charged tRNA 并恢复酶，不表示通量大小；所有多底物必须同时具备。`NONZERO_PARAMETER` 只说明作者参考参数非零。", "",
             "科学状态：`HUMAN_REVIEW_REQUIRED`。算法、来源及验收见 [protocol](pathway_first_protocol_v1.md)；检查结果和待决问题见 [review](glyrs_metrs_review.md)。", "",
             "## 1. RS / AMINOACYLATION", ""]
    displayed = set()

    def detail(rid):
        r = R[rid]
        if rid in displayed:
            return [f"原始方程：[{rid}](#{rid})。", ""]
        displayed.add(rid)
        return [f'<a id="{rid}"></a>', "", "| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |",
                "|---|---|---|---|---|",
                f"| `{rid}` | `{r['equation']}` | `{';'.join(r['level_c'])}` | `{r['reaction_family']}` | `{r['reference_activity']}` |", ""]

    def refs(ids):
        return ", ".join(f"[{rid}](#{rid})" for rid in ids)

    for number, (enzyme, module) in enumerate(data["modules"].items(), 1):
        lines += [f"### 1.{number} {enzyme} charging", "",
                  "路径共享的步骤采用链接引用；分支列表为同一前体的并行出口，不能逐行串联。", ""]
        for path in module["paths"]:
            lines += [f'<a id="{path["id"]}"></a>', "", f"#### {path['id']} — {path['title']}", "",
                      f"类型：`{';'.join(path['types'])}`。起点 `{path['start']}`；终点 `{path['end']}`。", ""]
            if path["target_product"]:
                lines += [f"目标释放产物：`{path['target_product']}`；最后恢复 `{enzyme}`。", ""]
            for i, step in enumerate(path["steps"], 1):
                rid = step["reaction_id"]
                lines += [f"{i:02d}. **{rid}** `[{';'.join(step['level_c'])}]`：`{step['carrier_before'][0]}` → `{step['carrier_after'][0]}`", "",
                          f"    同时消耗：`{equation(step['other_reactants'], {}).split(' -> ')[0]}`；另外释放：`{equation({}, step['other_products']).split(' -> ')[1]}`（`0` 表示无）。", ""]
                lines += detail(rid)
            for rejoin in path["rejoins"]:
                lines += [f"`REJOIN`：在 `{rejoin['state']}` 接入 [{rejoin['path_id']}](#{rejoin['path_id']})。", ""]
            for continuation in path["shared_continuations"]:
                lines += [f"替代路段在 `{continuation['state']}` 汇合；随后与 [{continuation['path_id']}](#{continuation['path_id']}) 共享连续步骤：{refs(continuation['reaction_ids'])}。", ""]
        lines += ["#### 竞争出口：按实际前体状态展开", "",
                  "每个状态列出全部原始出口。`REVERSE_EDGE` 表示存在精确逆反应伙伴，两方向都保留；它不指定哪一方向为生化正向。降解出口的完整方程在附录。", ""]
        # Breadth-first order from free enzyme; IDs only break ties among simultaneous alternatives.
        states = list(nx.bfs_tree(nx.DiGraph([(t["carrier_before"][0], t["carrier_after"][0]) for t in module["transitions"]]), enzyme))
        branch_map = {b["state"]: b for b in module["branches"]}
        transition_map = {t["reaction_id"]: t for t in module["transitions"]}
        for state in states:
            if state not in branch_map:
                continue
            lines += [f'<a id="state-{state}"></a>', "", f"##### Branches from `{state}`", ""]
            for rid in branch_map[state]["outgoing_reaction_ids"]:
                t = transition_map[rid]
                lines += [f"- [{rid}](#{rid}) → `{t['carrier_after'][0]}`；`{t['mechanistic_reaction_type']}`；`{';'.join(t['types'])}`。"]
            lines += [""]
            for rid in branch_map[state]["outgoing_reaction_ids"]:
                if "DEG_sink" not in R[rid]["level_c"]:
                    lines += detail(rid)
        lines += ["#### 汇合与跨 RFAM 连接", "",
                  "以下为到达同一载体状态的真实入边；有向可达性依赖每步完整底物。分支的目标状态可在本节或上面的状态出口定位。", "",
                  "| 汇合状态 | 所有原始入边 |", "|---|---|"]
        for rejoin in module["rejoins"]:
            lines += [f"| `{rejoin['state']}` | {refs(rejoin['incoming_reaction_ids'])} |"]
        lines += ["", "跨 RFAM 的载体接续（不以功能标签切断）：", "",
                  "| 载体状态 | 上游反应 | 下游反应 |", "|---|---|---|"]
        for link in module["cross_family_links"]:
            lines += [f"| `{link['state']}` | {refs([link['from_reaction_id']])} | {refs([link['to_reaction_id']])} |"]
        lines += ["", "#### 逆反应与返回环", "",
                  "下列是有限的最短返回见证，不是所有可能循环的枚举。每行从所列载体出发并回到相同载体；包含禁用边的环只能作源结构阅读。SCC 内部保留全部边，仅 SCC 之间的压缩图为 DAG。", "",
                  "| 返回环 | 起止载体 | 连续原始反应 | 参考参数支持 |", "|---|---|---|---|"]
        for loop in module["return_loops"]:
            sequence = " → ".join(f"[{rid}](#{rid})" for rid in loop["reaction_ids"])
            lines += [f"| {loop['id']} | `{loop['states'][0]}` | {sequence} | {'全部非零' if loop['reference_feasible'] else '含 REFERENCE_DISABLED'} |"]
        lines += ["", "逆向伙伴与零参数方向：", "", "| 原始方向 | 精确逆方向 | 参考方向活性 |", "|---|---|---|"]
        for rid in module["reaction_ids"]:
            if "DEG_sink" in R[rid]["level_c"]:
                continue
            lines += [f"| {refs([rid])} | {refs([R[rid]['reverse_reaction_id']]) if R[rid]['reverse_reaction_id'] else '无'} | `{R[rid]['reference_activity']}` |"]
        lines += [""]
    lines += ["## 2. 游离中间体通道与载体交接边界", "",
              "以下 8 条 RS 反应不含 GlyRS / MetRS，不能伪造酶载体边。按真实底物/产物成对保留；参考条件下全部禁用。酶释放或再结合游离 adenylate 的步骤仍见相应酶路径。", ""]
    for rid in data["noncarrier_reactions"]:
        lines += detail(rid)
    lines += ["### 通往其他载体的边界", "",
              "源方程支持下列 charged tRNA 的直接交接。GlyRS / MetRS 与 tRNA 的同步状态均保留在图文件；本样板不把 tRNA 与其他复合物的相遇展开为已经验证的后续路径。`HUMAN_REVIEW_REQUIRED`。", "",
              "| 交接物种 | 消耗它的外部反应 | 该方向参考活性 |", "|---|---|---|"]
    for link in data["boundary_links"]:
        if link["role"] == "reactant" and link["species"] in {c["charged"] for c in CONFIG.values()}:
            rid = link["reaction_id"]
            lines += [f"| `{link['species']}` | [{rid}](../reaction.md#{rid}) | `{R[rid]['reference_activity']}` |"]
    lines += ["", "## Appendix — DEG_sink and reference-disabled outlets", "",
              "30 条酶载体降解出口逐条保留，均为 `REFERENCE_DISABLED`。它们属于相应前体的竞争出口，但不接入参考参数支持的产物路径。", ""]
    for rid in data["coverage"]["phase_a_reaction_ids"]:
        if "DEG_sink" in R[rid]["level_c"]:
            lines += detail(rid)
    assert displayed == set(data["coverage"]["phase_a_reaction_ids"])
    return "\n".join(lines).rstrip() + "\n"


def build(output_dir):
    species, reactions, provenance = read_source()
    modules = {enzyme: build_module(enzyme, config, species, reactions) for enzyme, config in CONFIG.items()}
    carrier_ids = set().union(*(set(m["reaction_ids"]) for m in modules.values()))
    scoped = sorted(carrier_ids | {rid for rid, r in reactions.items() if RS_LABELS & set(r["level_c"])})
    noncarrier = sorted(set(scoped) - carrier_ids)
    outside = sorted(set(reactions) - set(scoped))
    path_counts = Counter(rid for m in modules.values() for p in m["paths"] for rid in set(p["reaction_ids"]))
    boundary = []
    for enzyme, config in CONFIG.items():
        for state in [config["trna"], config["charged"], config["aa"] + "AMP"]:
            for rid in outside:
                for role, side_name in [("reactant", "reactants"), ("product", "products")]:
                    if state in reactions[rid][side_name]:
                        boundary.append({"module": enzyme, "species": state, "reaction_id": rid, "role": role,
                                         "stoichiometry": reactions[rid][side_name][state], "evidence": "EXTRACTED_SPECIES_INCIDENCE",
                                         "interpretation_status": "HUMAN_REVIEW_REQUIRED"})
    data = {"schema_version": 1, "phase": "A", "scientific_status": "HUMAN_REVIEW_REQUIRED",
            "source_provenance": provenance, "species": species, "reactions": reactions, "petri_net": petri(reactions),
            "modules": modules, "noncarrier_reactions": noncarrier, "boundary_links": boundary,
            "coverage": {"source_unique_reaction_count": len(reactions), "phase_a_reaction_ids": scoped,
                         "out_of_phase_reaction_ids": outside, "unassigned_phase_a": [], "unique_reaction_count": len(scoped),
                         "markdown_reaction_reference_count": 0, "shared_path_reaction_count": sum(v > 1 for v in path_counts.values())},
            "claim_boundaries": {"pathways_reconstructed_for_full_network": False, "actual_reference_flux_claimed": False,
                                 "carrier_identity_status": "INFERRED_FROM_EXPLICIT_SOURCE_SPECIES_NAMES",
                                 "all_other_substrates_required_simultaneously": True,
                                 "multi_carrier_global_handoffs": "HUMAN_REVIEW_REQUIRED"}}
    text = sample_markdown(data)
    data["coverage"]["markdown_reaction_reference_count"] = len(re.findall(r"re\d{10}", text))
    output_dir.mkdir(parents=True, exist_ok=True)
    write_text(output_dir / "glyrs_metrs_sample.md", text)
    write_text(output_dir / "glyrs_metrs_graph.json", json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    transitions = {t["reaction_id"]: (enzyme, t) for enzyme, m in modules.items() for t in m["transitions"]}
    fields = ["reaction_id", "module", "carrier_before", "carrier_after", "other_reactants", "other_products", "level_c",
              "reaction_family", "reverse_reaction_id", "reference_activity", "source_provenance", "path_ids", "equation"]
    with (output_dir / "glyrs_metrs_pathway_index.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for rid in scoped:
            r = reactions[rid]
            enzyme, t = transitions.get(rid, ("FREE_INTERMEDIATE", {"carrier_before": [], "carrier_after": [],
                              "other_reactants": r["reactants"], "other_products": r["products"]}))
            writer.writerow({"reaction_id": rid, "module": enzyme,
                             **{key: compact(t[key]) for key in ["carrier_before", "carrier_after", "other_reactants", "other_products"]},
                             "level_c": ";".join(r["level_c"]), "reaction_family": r["reaction_family"],
                             "reverse_reaction_id": r["reverse_reaction_id"] or "", "reference_activity": r["reference_activity"],
                             "source_provenance": compact(r["source_provenance"]),
                             "path_ids": compact([p["id"] for m in modules.values() for p in m["paths"] if rid in p["reaction_ids"]]), "equation": r["equation"]})
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/reduction/pathways")
    args = parser.parse_args()
    data = build(args.output_dir)
    print(json.dumps({"scope": "PHASE_A_ONLY", "scientific_status": data["scientific_status"],
                      "coverage": {k: v for k, v in data["coverage"].items() if not isinstance(v, list)},
                      "modules": {e: {"paths": len(m["paths"]), "branches": len(m["branches"]), "rejoins": len(m["rejoins"]),
                                      "sccs": len(m["sccs"]), "cyclic_sccs": sum(c["cyclic"] for c in m["sccs"]), "return_loops": len(m["return_loops"])} for e, m in data["modules"].items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
