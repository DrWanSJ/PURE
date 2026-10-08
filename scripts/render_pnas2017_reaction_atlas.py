#!/usr/bin/env python3
"""Render a source-faithful mechanism atlas, never a reduced model.

Read-only inputs: canonical/subsystem SBML, reviewed v2 annotations and their
source/graph contracts. Only reaction.md and reaction_index.csv are written.
Run: python scripts/render_pnas2017_reaction_atlas.py [--output-dir DIRECTORY]
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from decimal import Decimal
from fractions import Fraction
import hashlib
import heapq
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/reduction"
SOURCE = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
SUBSYSTEMS = SOURCE.parent / "subsystems"
NS = "{http://www.sbml.org/sbml/level2/version4}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
SHARED_CARRIERS = {
    "EFTu_GTP", "EFTu_GDP", "EFTu_EFTs", "EFTu_GDP_EFTs", "EFTu_GTP_EFTs",
    "EFG_GDP", "EFG_GTP", "IF2_GDP", "IF2_GTP", "RF3_GDP", "RF3_GTP",
}
GROUPS = [
    ("4", "RS / AMINOACYLATION", ["RS_binding", "RS_activation", "RS_charging", "RS_to_INIT_formylation"],
     "GlyRS / MetRS 的底物装配、腺苷酸活化、tRNA 酰化和酶再生构成有分支的循环；MTF 甲酰化连接 aminoacylation 与 initiation。"),
    ("5", "INITIATION", ["INIT_assembly", "INIT_tRNA_recruitment", "INIT_energy_commitment", "INIT_70S_formation", "INIT_factor_release"],
     "IF1、IF3、IF2-GTP、mRNA 与起始 fMet-tRNA 可依不同顺序装配；30S 加入 50S 后，IF2 核苷酸状态改变并释放因子，进入延伸。"),
    ("6", "ELONGATION", ["ELONG_aa_tRNA_delivery", "ELONG_energy_coupling", "ELONG_peptide_formation", "ELONG_translocation", "ELONG_tRNA_release"],
     "本源模型逐步合成 fMet-Gly-Gly：两轮 Gly-tRNA 递送分别生成 Pept0002 和 Pept0003；肽键形成、EF-G 能量步骤、核糖体位置变化和去酰化 tRNA 释放分别记录。"),
    ("7", "TERMINATION / RECYCLING", ["TERM_factor_binding", "TERM_peptide_release", "TERM_energy_coupling", "RECYCLE_disassembly", "RECYCLE_component_release"],
     "RF1 / RF2 是共享终止位点的并行分支；RF3 处理因子核苷酸循环，RRF / EF-G 参与亚基分裂，随后 mRNA、tRNA 与因子沿多条路径释放。"),
    ("8", "ENERGY REGENERATION", ["EN_binding", "EN_energy_transfer", "EN_byproduct_processing"],
     "CK、NDK、MK 的底物结合、酶内转换和产物释放分开展示；PPiase 在结合态处理 PPi，然后逐个释放 PO4。SmallMolecules 独立保留游离核苷酸通道。"),
    ("9", "DEG_sink / inactive reference pathways", ["DEG_sink"],
     "388 条源降解 / 失活通道均有详细条目，按被消耗的源物种归组；作者参考参数为零也不删除。其余功能类中的禁用通道仍在对应机制路径内展示。"),
]
STAGES = [stage for _, _, stages, _ in GROUPS for stage in stages]
STAGE_GUIDES = {
    "RS_binding": "分别识别 amino acid、ATP、tRNA 和混合底物装配。ATP 结合只改变复合物占据状态，不自动意味着 ATP 水解。",
    "RS_activation": "ATP / amino acid 结合态转换为 aminoacyl-AMP / PPi 中间体，继而处理 PPi 和腺苷酸释放；与 charging 的真实边界保留 MULTI。",
    "RS_charging": "活化中间体招募 tRNA、aminoacyl transfer、AMP 与 charged tRNA 释放及 aaRS 再生；禁用的游离 aa-tRNA 逆向通道也保留。",
    "RS_to_INIT_formylation": "MTF / FD 将 Met-tRNA 转为起始 fMet-tRNA；独立的 FD / THF 转换和 fMet-tRNA 解离通道不被伪装为完整甲酰转移。",
    "INIT_assembly": "30S / 70S 与 IF1、IF3、IF2-GTP、mRNA 的占据态形成和解离，存在并行装配顺序。",
    "INIT_tRNA_recruitment": "IF2-GTP-fMet-tRNA cargo 形成及起始 tRNA 的核糖体招募；区别于延伸 Gly-tRNA 载体。",
    "INIT_energy_commitment": "IF2 的 GTP / GDP 装载、结合态 GTP→GDP_PO4 转换及 PO4 释放属于不同事件。",
    "INIT_70S_formation": "真正的 30S + 50S 与 70S 之间的结合 / 分裂；保留裸核糖体及带因子复合物的所有原始方向。",
    "INIT_factor_release": "已形成 70S 起始复合物释放 / 再结合 IF1、IF2、IF3，存在不同释放顺序。",
    "ELONG_aa_tRNA_delivery": "EF-Tu-GTP-aa-tRNA 载体形成、核糖体递送、EF-Tu 释放及未成功递送的支路；禁用侧路仍有原始方程。",
    "ELONG_energy_coupling": "EF-Tu / EF-G 的核苷酸装载、结合态 GTP 化学和 PO4 / 因子释放；出现 GTP 或 GDP 并不逐条证明水解。",
    "ELONG_peptide_formation": "两次真实复合物转换分别形成 fMet-Gly 与 fMet-Gly-Gly，并保留各自逆通道。",
    "ELONG_translocation": "核糖体 B / C / A 状态与 codon-position 的转换；同一步可能伴随 PO4 或 EF-G-GDP 释放，但与肽键形成区分。",
    "ELONG_tRNA_release": "去酰化起始 tRNA 或 Gly-tRNA 从延伸核糖体释放，及其逆向结合。",
    "TERM_factor_binding": "RF1 / RF2 在肽释放前后核糖体上的识别、结合和释放；保留两条并行通路。",
    "TERM_peptide_release": "源反应把带 Pept0003-tRNA 的复合物转为游离 Pept0003 和 posttermination 复合物；生化解释为肽酰-tRNA 水解，源方程不额外添加水。",
    "TERM_energy_coupling": "RF3 GDP / GTP 装载、因子招募 / 释放、结合态核苷酸转换和 PO4 释放构成终止循环。",
    "RECYCLE_disassembly": "RRF / EF-G 装配、相关核苷酸状态变化及 posttermination 70S 的实际分裂。",
    "RECYCLE_component_release": "分裂后的 mRNA、tRNA、RRF、EF-G-GDP 释放 / 再结合；50S-EF-G-GDP 共享连接完整保留。",
    "EN_binding": "按 CK / NDK / MK / PPiase 分别显示底物和产物的结合 / 解离，产物释放不算新的磷酰转移。",
    "EN_energy_transfer": "CK / NDK / MK 的实际酶内转换，加上已审核归于此类的 SmallMolecules 游离核苷酸转换；二者的具体化学意义分别解释。",
    "EN_byproduct_processing": "PPiase_PPi 与 PPiase_PO4_PO4 的转换，逐个 PO4 的后续释放留在 EN_binding。",
    "DEG_sink": "完整显示失活产物和从被失活复合物释放的其余组分；保留 2 PO4 等原始系数，不能以 sink 简称替代完整方程。",
}


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def split(value):
    return set(filter(None, value.split(";")))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def coefficient(value):
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    # All current coefficients are integers; finite decimals remain exact.
    denominator = value.denominator
    for factor in (2, 5):
        while denominator % factor == 0:
            denominator //= factor
    if denominator != 1:
        return f"{value.numerator}/{value.denominator}"
    return format(Decimal(value.numerator) / Decimal(value.denominator), "f").rstrip("0").rstrip(".")


def math_number(node):
    tag = node.tag.removeprefix(MATH)
    if tag in {"math", "stoichiometryMath"}:
        if len(node) != 1:
            raise ValueError("Expected one constant MathML expression")
        return math_number(node[0])
    if tag == "cn":
        kind = node.get("type", "real")
        if kind in {"rational", "e-notation"}:
            first = Fraction((node.text or "").strip())
            if len(node) != 1 or node[0].tag != MATH + "sep":
                raise ValueError("Invalid numeric MathML separator")
            second = Fraction((node[0].tail or "").strip())
            if kind == "rational":
                return first / second
            if second.denominator != 1:
                raise ValueError("Noninteger MathML exponent")
            return first * Fraction(10) ** int(second)
        return Fraction((node.text or "").strip())
    if tag == "apply":
        op = node[0].tag.removeprefix(MATH)
        args = [math_number(child) for child in node[1:]]
        if op == "plus":
            return sum(args, Fraction(0))
        if op == "times":
            result = Fraction(1)
            for arg in args:
                result *= arg
            return result
        if op == "minus" and len(args) in (1, 2):
            return -args[0] if len(args) == 1 else args[0] - args[1]
        if op == "divide" and len(args) == 2:
            return args[0] / args[1]
        if op == "power" and len(args) == 2 and args[1].denominator == 1:
            return args[0] ** int(args[1])
    raise ValueError(f"Unsupported/nonconstant stoichiometryMath: {tag}")


def references(reaction, side):
    values = defaultdict(Fraction)
    for ref in reaction.findall(f"{NS}listOf{side}/{NS}speciesReference"):
        math = ref.find(NS + "stoichiometryMath")
        amount = Fraction(ref.get("stoichiometry", "1")) if math is None else math_number(math[0])
        if amount <= 0:
            raise ValueError("Nonpositive species-reference coefficient")
        values[ref.get("species")] += amount
    return {species: coefficient(amount) for species, amount in sorted(values.items())}


def parse_sbml(path):
    model = ET.parse(path).getroot().find(NS + "model")
    if model is None:
        raise ValueError(f"Missing SBML model: {path}")
    reactions = {}
    for element in model.findall(f"{NS}listOfReactions/{NS}reaction"):
        rid = element.get("id")
        if rid in reactions:
            raise ValueError(f"Duplicate source reaction: {rid}")
        reactions[rid] = {
            "reaction_id": rid, "reactants": references(element, "Reactants"),
            "products": references(element, "Products"),
            "modifiers": sorted(ref.get("species") for ref in element.findall(f"{NS}listOfModifiers/{NS}modifierSpeciesReference")),
            "source_kinetic_reversible": element.get("reversible", "true"),
        }
    return model, reactions


def signature(reaction):
    return tuple(reaction["reactants"].items()), tuple(reaction["products"].items()), tuple(reaction["modifiers"])


def equation(reaction):
    def side(values):
        return " + ".join(("" if amount == "1" else amount + " ") + species for species, amount in values.items()) or "∅"
    return side(reaction["reactants"]) + " -> " + side(reaction["products"])


def rid(number):
    return f"re{number:010d}"


def rxlink(reaction_id):
    return f"[`{reaction_id}`](#{reaction_id})"


def chain(numbers):
    return " → ".join(rxlink(rid(number)) for number in numbers)


def pair_orientation(pair, annotations):
    """Navigation direction only; no source channel is replaced or removed."""
    stage = annotations[pair[0]]["level_c_functional_contexts"]
    prefer = None
    if stage in {"RS_binding", "INIT_assembly", "INIT_tRNA_recruitment", "INIT_70S_formation"}:
        prefer = "HETERODIMER_ASSOCIATION"
    if stage in {"INIT_factor_release", "ELONG_tRNA_release", "RECYCLE_component_release"}:
        prefer = "DISSOCIATION"
    if prefer:
        candidates = [r for r in pair if annotations[r]["mechanistic_reaction_type"] == prefer]
        if candidates:
            return min(candidates)
    return min(pair)


def strongly_connected(graph):
    """Deterministic Tarjan SCC, for a small family-level navigation graph."""
    counter = 0
    indices, low, stack, on_stack, components = {}, {}, [], set(), []

    def visit(node):
        nonlocal counter
        indices[node] = low[node] = counter
        counter += 1
        stack.append(node)
        on_stack.add(node)
        for other in sorted(graph[node]):
            if other not in indices:
                visit(other)
                low[node] = min(low[node], low[other])
            elif other in on_stack:
                low[node] = min(low[node], indices[other])
        if low[node] == indices[node]:
            component = []
            while True:
                other = stack.pop()
                on_stack.remove(other)
                component.append(other)
                if other == node:
                    break
            components.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return components


def topology(reactions, annotations):
    bridges = set().union(*(split(row["bridge_species_participants"]) for row in annotations.values())) - SHARED_CARRIERS
    consumers = defaultdict(set)
    for key, reaction in reactions.items():
        if annotations[key]["level_c_functional_contexts"] != "DEG_sink":
            for species in reaction["reactants"]:
                consumers[species].add(key)
    connected = {}
    for key, reaction in reactions.items():
        links = {}
        if annotations[key]["level_c_functional_contexts"] != "DEG_sink":
            for species in sorted(set(reaction["products"]) & bridges):
                targets = consumers[species] - {key, annotations[key]["reverse_partner_id"]}
                if targets:
                    links[species] = sorted(targets)
        connected[key] = links
    families = defaultdict(list)
    seen = set()
    for key in sorted(reactions):
        if key in seen:
            continue
        partner = annotations[key]["reverse_partner_id"]
        pair = sorted({key, partner} - {""})
        seen.update(pair)
        representative = pair_orientation(pair, annotations)
        families[annotations[key]["reaction_family_id"]].append((representative, pair))
    ordered, layers, cyclic = {}, {}, {}
    for family, steps in families.items():
        reps = {rep: pair for rep, pair in steps}
        if family == "RFAM_DEG":
            # Sink reactions have no invented causal order; source consumed-state
            # identity groups multiple mechanisms of inactivation together.
            order = sorted(reps, key=lambda r: (tuple(reactions[r]["reactants"]), tuple(reactions[r]["products"]), r))
            ordered[family] = [(r, reps[r]) for r in order]
            layers.update({r: 0 for r in order})
            cyclic[family] = []
            continue
        graph = {rep: set() for rep in reps}
        for left in reps:
            for right in reps:
                if left != right and set(reactions[left]["products"]) & set(reactions[right]["reactants"]) & bridges:
                    graph[left].add(right)
        comps = strongly_connected(graph)
        membership = {node: i for i, comp in enumerate(comps) for node in comp}
        children = {i: set() for i in range(len(comps))}
        indegree = {i: 0 for i in children}
        for node, targets in graph.items():
            for target in targets:
                a, b = membership[node], membership[target]
                if a != b and b not in children[a]:
                    children[a].add(b)
                    indegree[b] += 1
        levels = {i: 0 for i in children}
        queue = [(comps[i][0], i) for i in children if not indegree[i]]
        heapq.heapify(queue)
        comp_order = []
        while queue:
            _, component = heapq.heappop(queue)
            comp_order.append(component)
            for child in sorted(children[component]):
                levels[child] = max(levels[child], levels[component] + 1)
                indegree[child] -= 1
                if not indegree[child]:
                    heapq.heappush(queue, (comps[child][0], child))
        assert len(comp_order) == len(comps)
        # Within a layer, actual source species identities break display ties;
        # SCC internals remain partial order, never a fictitious time sequence.
        order = sorted(reps, key=lambda r: (levels[membership[r]], tuple(reactions[r]["reactants"]), tuple(reactions[r]["products"]), r))
        ordered[family] = [(r, reps[r]) for r in order]
        for r in order:
            layers[r] = levels[membership[r]]
        cyclic[family] = [comp for comp in comps if len(comp) > 1]
    return connected, ordered, layers, cyclic


def family_guide(family):
    number = int(family[-3:]) if family != "RFAM_DEG" else 0
    if number in (1, 3):
        return "上一轮起始 / 延伸完成后，去酰化 tRNA 从 A 状态核糖体释放；逆向通道独立保留。"
    if number in (2, 4):
        numbers = [13, 14, 16, 17, 18, 19, 22, 24, 25] if number == 2 else [74, 75, 77, 78, 79, 80, 83, 85, 86]
        return "实际延伸主路径：" + chain(numbers) + "。递送未成功的侧路返回前置核糖体状态；本段按具体中间体分层，跨阶段完整序列见第 3 节。"
    if number in (5, 7, 10, 12):
        enzyme = "GlyRS" if number in (5, 10) else "MetRS"
        return f"{enzyme} 的 amino acid / ATP 装配有 BRANCH A（amino acid 先结合）与 BRANCH B（ATP 先结合），汇入共同活化前复合物。tRNA 进入和 AMP / charged-tRNA 退出各有并行路线；CYCLE 返回 {enzyme}，跨 family 的 AMP-reset 连接保留。PARTIAL_ORDER_ONLY。"
    if number in (6, 8):
        return "aaRS-bound AMP 释放 / 再结合端点，连接 charging family；CYCLE 返回游离 synthetase，不能将其孤立误判为新的 activation。"
    if number in (9, 11, 19):
        return "参考禁用的游离 aminoacyl-tRNA / formyl-tRNA 解离及其逆向通道；原始物种、完整方程与双向 ID 均保留。"
    if number == 13:
        return "EF-Tu / EF-Ts 的 GDP 释放与 GTP 装载可走 EF-Ts 辅助或直接装载路线，之后形成 Gly / Met aa-tRNA carrier。CYCLE 返回 EF-Tu；核苷酸结合 / 解离不等于水解。"
    if number == 14:
        return "EF-G GDP→游离 EF-G→EF-G-GTP 准备状态分别连接延伸-side ribosome 与 posttermination RRF 路线。回收主路径 " + chain([904, 895, 908, 902, 910]) + "；SHARED_JUNCTION `RS50S_EFG_GDP` 连接 elongation 与 recycling。分裂后各组分释放为并行分支。"
    if number in (15, 16, 17, 20):
        enzyme = {15: "CK", 16: "NDK", 17: "MK", 20: "MTF"}[number]
        return f"{enzyme} 的两条底物结合路线汇入催化复合物；一次结合态化学转换后，两种产物释放顺序返回游离 {enzyme}。BRANCH A/B 与 CYCLE 的具体路径见第 3 节；无唯一全局先后顺序。"
    if number == 18:
        return "PPi 结合 → bound PPi 转换为两个 bound phosphate → 分两步释放 PO4，CYCLE 返回 PPiase。源路线 " + chain([405, 407, 409, 411]) + "。"
    if number == 21:
        return "独立 FD / THF 状态转换；本条源方程不含 tRNA，不能称为完整 Met-tRNA 甲酰转移。保留已审核桥接阶段。"
    if number in (22, 23):
        return "IF2 GTP / GDP 装载与 pre-ribosome fMet-tRNA cargo 准备；核苷酸 binding 本身没有新增水解产物。"
    if number == 24:
        return "裸 30S / 50S / 70S 结合与分裂；单独保留两条 source directions。"
    if number in (25, 26):
        return "IF1 / IF3 / IF2 / mRNA / initiator cargo 的平行装配网络。BRANCH A/B 在特异 30S 中间体汇合；50S joining 后 IF2 化学与 factor-release 路线进入延伸。不同可逆装配顺序只支持 PARTIAL_ORDER_ONLY，不宣称某一路线通量占优。"
    if 27 <= number <= 32:
        return "SmallMolecules 游离核苷酸裂解 / 逆向重组通道；保留已审核 EN_energy_transfer 标签。没有源 enzyme，不能解释为 CK / NDK / MK 催化。全部 REFERENCE_DISABLED。"
    if number in (33, 34):
        factor = "RF1" if number == 33 else "RF2"
        return f"{factor} 结合共同 stop-site Pept0003-ribosome，释放 Pept0003，再释放因子。RF1 与 RF2 为 BRANCH A/B，汇入同一 posttermination 核糖体。"
    if number == 35:
        return "RF3 可在 RF1 或 RF2 复合物上进入不同 GDP / GTP 状态，因子释放、GTP chemistry 与 PO4 释放形成循环；CYCLE 返回游离 RF3，PARTIAL_ORDER_ONLY。"
    return "按被消耗的源物种列出失活通道和剩余组分释放；这些通道无虚构时间顺序。"


def role(reaction, annotation):
    stages = split(annotation["level_c_functional_contexts"])
    src, dst = set(reaction["reactants"]), set(reaction["products"])
    form = annotation["mechanistic_reaction_type"]
    if "DEG_sink" in stages:
        return "源物种进入降解 / 失活产物，同时按原方程释放剩余组分；这仍是一条原始通道。"
    if annotation["reaction_family_id"] in {"RFAM_009", "RFAM_011", "RFAM_019"}:
        charged = {"GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU"}
        if src & charged:
            return "游离 aminoacyl / formyl-aminoacyl tRNA 的去酰化通道，生成源方程中的氨基酸和 tRNA；涉及共价连接变化，不是因子复合物解离。"
        return "源中的逆向氨基酸 / tRNA 再酰化通道；涉及共价连接变化，本方程没有 synthetase 或 ATP，不能虚构催化步骤。"
    if src & {"GlyAMP", "MetAMP"} or dst & {"GlyAMP", "MetAMP"}:
        if src & {"GlyAMP", "MetAMP"} and not any(s.startswith(("GlyRS", "MetRS")) for s in dst):
            return "游离 aminoacyl-AMP 裂解为 amino acid 与 AMP，涉及腺苷酸化学连接变化；本通道不含 aaRS。"
        if dst & {"GlyAMP", "MetAMP"} and not any(s.startswith(("GlyRS", "MetRS")) for s in src):
            return "源中的逆向游离 amino acid / AMP 重组为 aminoacyl-AMP；涉及化学连接变化，本通道不含 ATP 或 aaRS。"
    if "ELONG_peptide_formation" in stages:
        forward = any(s.startswith("elRS70SB") for s in dst)
        length = "fMet → fMet-Gly（Pept0002）" if annotation["reaction_family_id"] == "RFAM_002" else "fMet-Gly → fMet-Gly-Gly（Pept0003）"
        return ("完成 " + length + " 的肽链延伸，产物仍结合 tRNA / 核糖体。") if forward else ("源中的逆向肽链状态转换，对应 " + length + " 的逆通道；参考参数为零仍保留。")
    if "ELONG_translocation" in stages:
        return "核糖体 codon / 位置状态改变，伴随方程中的 PO4 或 EF-G-GDP 释放 / 再结合；不是新的肽键形成。"
    if "TERM_peptide_release" in stages:
        return "从肽酰-tRNA 核糖体释放完整 Pept0003，形成 posttermination 复合物。" if "Pept0003" in dst else "源中的逆向 Pept0003 再结合 / 肽酰复合物恢复通道。"
    if "RECYCLE_disassembly" in stages and any(s.startswith("RS50S") for s in dst) and any(s.startswith("termRS30S") for s in dst):
        return "将 posttermination 70S 分裂为带 tRNA / RRF / EF-G 的 50S 与带 mRNA 的 30S。"
    if "RECYCLE_disassembly" in stages and any(s.startswith("termRS30S") for s in src):
        return "源中的逆向亚基再结合，恢复 posttermination 70S 复合物。"
    if annotation["reaction_family_id"] in {f"RFAM_{n:03d}" for n in range(27, 33)}:
        return "游离核苷酸与其 phosphate / PPi 产物之间的源状态转换；本方程不含催化酶。"
    if form == "STATE_TRANSITION":
        if "RS_activation" in stages:
            return "酶内 amino acid / ATP 状态与 aminoacyl-AMP / PPi 状态相互转换，涉及氨基酸活化化学。"
        if "RS_charging" in stages:
            return "酶内 aminoacyl-AMP / tRNA 状态与 aa-tRNA / AMP 状态转换，涉及 aminoacyl transfer。"
        if "RS_to_INIT_formylation" in stages:
            return "MTF 结合态的 FD / Met-tRNA 与 THF / fMet-tRNA 发生甲酰化状态转换。" if any(s.startswith("MTF_") for s in src | dst) else "独立 formyl donor FD / THF 转换；不把此单步等同于完整 tRNA 甲酰化。"
        if "EN_energy_transfer" in stages:
            return "酶结合态底物 / 产物复合物转换，执行源中的磷酰基转移；结合和产物释放另列。"
        if "EN_byproduct_processing" in stages:
            return "PPiase 结合态 PPi 与两个结合态 phosphate 相互转换，游离 PO4 后续分步释放。"
        if any("_GTP" in s for s in src) and any("_GDP_PO4" in s for s in dst):
            return "因子 / 核糖体结合态 GTP 转为 GDP_PO4，生化解释为 GTP 水解；PO4 暂留结合态，后续释放另列。"
        if any("_GDP_PO4" in s for s in src) and any("_GTP" in s for s in dst):
            return "源中结合态 GDP_PO4 转回 GTP 的逆化学通道；保留此原始方向，不把它解释为核苷酸结合。"
        raise ValueError(f"Uninterpreted source state transition: {reaction['reaction_id']}")
    # Species identity and source form determine an explicit physical event,
    # while the preserved reviewed stage describes its functional context.
    if form == "HETERODIMER_ASSOCIATION":
        free = sorted(s for s in src if "_" not in s or s in SHARED_CARRIERS)
        cargo = "、".join(free) if free else "源方程所列的载体 / 复合物"
        return f"结合 {cargo}，装配方程中的产物复合物；核苷酸结合本身不证明水解。"
    if form == "DISSOCIATION":
        free = sorted(s for s in dst if "_" not in s or s in SHARED_CARRIERS)
        cargo = "、".join(free) if free else "方程中的组分 / 中间体"
        return f"从源复合物释放 {cargo}，恢复相应池或残余复合物；若是化学产物释放，其生成步骤另列。"
    raise ValueError(f"Unsupported mechanistic form: {form}")


def overview():
    return [
        "<a id=\"pathway-overview\"></a>", "## 3. Reaction pathway overview", "",
        "以下箭头按实际中间体的生成 / 消耗连接原始通道；伴随底物必须同时存在。路线是结构示例，不是必然事件顺序、通量优势或新的净反应。所有链接指向完整单向方程。", "",
        "### RS 与 MTF：分支和返回节点", "",
        f"GlyRS：BRANCH A {chain([126, 136])} 与 BRANCH B {chain([132, 134])} 汇入 SHARED_JUNCTION `GlyRS_Gly_ATP`，继而 {chain([140, 127])} 到 `GlyRS_GlyAMP`。tRNA 可在活化前结合，也可在活化后经 {rxlink(rid(207))} / {rxlink(rid(209))} 招募；{rxlink(rid(207))} 与其 reverse 是已审核 MULTI。", "",
        f"MetRS：BRANCH A {chain([151, 161])} 与 BRANCH B {chain([157, 159])} 汇入 `MetRS_Met_ATP`，继而 {chain([165, 152])}。tRNA-bound activation {rxlink(rid(239))} 和共享 recruitment {rxlink(rid(249))} 保留真实旁路。", "",
        f"Charging：Gly {chain([209, 178])} 到 `GlyRS_AMP_GlytRNAGlyGCC`；BRANCH A {chain([180, 184])}（先 AMP）与 BRANCH B {chain([182, 145])}（先 aa-tRNA）构成 CYCLE 返回 `GlyRS`。Met 对应 {chain([251, 220])}，返回路径 {chain([222, 226])} / {chain([224, 170])}。不同招募 / 释放顺序为 PARTIAL_ORDER_ONLY。", "",
        f"MTF：BRANCH A {chain([418, 422])} 与 BRANCH B {chain([420, 424])} 汇入 `MTF_FD_MettRNAfMetCAU`；{rxlink(rid(426))} 形成 `MTF_THF_fMettRNAfMetCAU`；产品释放 {chain([428, 434])} / {chain([430, 432])} 构成 CYCLE 返回 `MTF`。", "",
        "### Initiation：并行装配和 factor-release", "",
        f"IF1 / IF3：BRANCH A {chain([503, 491])} 与 BRANCH B {chain([459, 507])} 汇入 `RS30S_IF1_IF3`。IF2 cargo：{chain([463, 467])} 与 {chain([449, 465])} 汇入 `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU`；mRNA 可以先经 {chain([469, 475])} 或后经 {chain([465, 483])} 加入完整 30S initiation complex。PARTIAL_ORDER_ONLY。", "",
        f"随后 {chain([485, 715, 721])} 表示 50S joining、IF2-bound GTP 化学和 PO4 释放。释放 BRANCH A {chain([755, 726])} 与 BRANCH B {chain([725, 763])} 汇入 `elRS70SAGGU0002_fMettRNAfMetCAU`；含 IF1 的真实支路也逐条列出。", "",
        "### Elongation：两次真实肽链延伸", "",
        f"起始 tRNA 释放 {rxlink(rid(1))} 后，第一轮：{chain([13, 14, 16, 17, 18, 19, 22, 24, 25])}；第二轮先 {rxlink(rid(68))}，再 {chain([74, 75, 77, 78, 79, 80, 83, 85, 86])}。两个 peptide formation steps 分别为 {rxlink(rid(18))} 和 {rxlink(rid(79))}，不是任意长度蛋白或 peptide-only 代理方程。", "",
        "### Termination 与 recycling：分支及共享连接", "",
        f"共同 stop-site `elRS70SAUAA0004_Pept0003tRNAGlyGCC`：BRANCH A {chain([796, 798, 799])}（RF1）与 BRANCH B {chain([811, 813, 814])}（RF2）生成相同 `Pept0003` / posttermination 状态。RF3 的核苷酸 / 因子处理为 family RFAM_035 的分支循环。", "",
        f"Recycling recruitment：BRANCH A {chain([904, 895])} 与 BRANCH B {chain([906, 901])} 汇入 `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP`；继而 {chain([908, 902, 910])} 完成 GTP chemistry、PO4 释放和 70S 分裂。30S 经 {rxlink(rid(911))} 释放 mRNA；50S 经 {rxlink(rid(913))} / {rxlink(rid(914))} / {rxlink(rid(915))} 进入不同释放顺序。{rxlink(rid(308))} / {rxlink(rid(327))} 的 `RS50S_EFG_GDP` 为真实 SHARED_JUNCTION，CYCLE 返回游离亚基 / 因子。", "",
        "### Energy enzyme cycles：净解释与真实 source steps", "",
        "CONCEPTUAL_NET (not a source reaction)：`CP + ADP ⇌ Cr + ATP`，CK 多步循环的净解释。", "",
        f"CK：BRANCH A {chain([330, 336])} 与 BRANCH B {chain([332, 334])} 汇入 `CK_CP_ADP`；{rxlink(rid(338))} 执行转换；产品释放 {chain([340, 346])} / {chain([342, 344])} 构成 CYCLE 返回 `CK`。", "",
        "CONCEPTUAL_NET (not a source reaction)：`ATP + GDP ⇌ ADP + GTP`，NDK 多步循环的净解释。", "",
        f"NDK：底物分支 {chain([355, 361])} / {chain([357, 359])}；{rxlink(rid(363))} 转换；产品分支 {chain([365, 367])} / {chain([366, 368])}，CYCLE 返回 `NDK`。", "",
        "CONCEPTUAL_NET (not a source reaction)：`ATP + AMP ⇌ 2 ADP`，MK 多步循环的净解释。", "",
        f"MK：底物分支 {chain([380, 386])} / {chain([382, 384])}；{rxlink(rid(388))} 转换；产品分支 {chain([390, 394])} / {chain([392, 396])}，CYCLE 返回 `MK`。", "",
        "CONCEPTUAL_NET (not a source reaction)：`PPi -> 2 PO4`，PPiase 多步循环的净解释，PO4 是 source Pi ID。", "",
        f"PPiase source sequence：{chain([405, 407, 409, 411])}；{rxlink(rid(407))} 为 bound conversion，随后两次 PO4 release 均为 EN_binding。", "",
    ]


FIELDS = [
    "reaction_id", "primary_stage", "all_stages", "multi_classification", "level_a_modules",
    "source_subsystems", "reaction_family_id", "pathway_order", "topology_layer", "step_id", "display_stage",
    "original_equation", "reactants_json", "products_json", "stoichiometry_json", "modifiers_json",
    "reverse_partner_id", "reference_activity", "directed_reference_parameter_value", "directed_reference_activity",
    "functional_annotation_status", "mechanistic_reaction_type", "classification_evidence", "classification_reason",
    "cross_module_context", "source_subsystem_reaction_refs_json", "source_kinetic_reversible",
    "connected_reactions", "specific_intermediates", "topology_basis", "ordering_evidence_status",
    "markdown_anchor", "source_sbml_sha256",
]


def render(output_dir):
    inputs = [SOURCE, DOC / "reaction_level_annotation_v2.csv", DOC / "reaction_annotation_method_v2.md",
              DOC / "reaction_annotation_summary_v2.md", DOC / "reaction_family_summary_v2.csv",
              DOC / "reaction_cross_family_links_v2.csv", DOC / "reaction_level_contract_detailed.md",
              DOC / "reduction_map.md", DOC / "reduction_decisions.csv", DOC / "human_reduction_review.md",
              DOC / "species_information_contract_detailed.md", DOC / "species_information_contract_summary.md",
              ROOT / "docs/pnas2017/chemical_ledger.md", DOC / "reaction_annotation_manifest_v2.json",
              ROOT / "models/pnas2017_full_reference/audit/reactions.csv",
              ROOT / "models/pnas2017_full_reference/audit/modules.csv"] + sorted(SUBSYSTEMS.glob("*.xml"))
    fingerprints = {path: digest(path) for path in inputs}
    # Read all contracts as evidence, never rewrite a reviewed document.
    for path in inputs:
        if path.suffix == ".md":
            path.read_text(encoding="utf-8")
    model, reactions = parse_sbml(SOURCE)
    species = {e.get("id") for e in model.findall(f"{NS}listOfSpecies/{NS}species")}
    annotations = {row["reaction_id"]: row for row in read_csv(DOC / "reaction_level_annotation_v2.csv")}
    audit = {row["reaction_id"]: row for row in read_csv(ROOT / "models/pnas2017_full_reference/audit/reactions.csv")}
    families = read_csv(DOC / "reaction_family_summary_v2.csv")
    links = read_csv(DOC / "reaction_cross_family_links_v2.csv")
    assert set(reactions) == set(annotations) == set(audit) and len(reactions) == 968
    assert len(species) == 241
    source_hash = fingerprints[SOURCE]
    local_signatures = defaultdict(list)
    for path in sorted(SUBSYSTEMS.glob("*.xml")):
        subsystem, local = parse_sbml(path)
        for key, reaction in local.items():
            local_signatures[signature(reaction)].append({"source_model_id": subsystem.get("id"), "source_file": path.name, "source_reaction_id": key})
    for key, reaction in reactions.items():
        a = annotations[key]
        assert a["source_sbml_sha256"] == source_hash
        for side in ("reactants", "products"):
            values = {s: Fraction(str(c)) for s, c in json.loads(a[side + "_json"]).items()}
            assert values == {s: Fraction(c) for s, c in reaction[side].items()}, key
            assert set(reaction[side]) <= species
        expected = sorted(local_signatures[signature(reaction)], key=lambda r: (r["source_model_id"], r["source_reaction_id"]))
        recorded = sorted(json.loads(audit[key]["source_module_reaction_refs_json"]), key=lambda r: (r["source_model_id"], r["source_reaction_id"]))
        assert expected == recorded and expected, key
        assert set(a["level_c_functional_contexts"].split(";")) <= set(STAGES)
        partner = a["reverse_partner_id"]
        if partner:
            reverse = reactions[partner]
            assert reaction["reactants"] == reverse["products"] and reaction["products"] == reverse["reactants"]
            assert annotations[partner]["level_c_functional_contexts"] == a["level_c_functional_contexts"]
    connected, ordered, layers, cyclic = topology(reactions, annotations)
    rows = []
    # Functional stage -> family -> subsystem provenance -> source-connected
    # mechanistic layer -> adjacent directed exact partners.
    for stage in STAGES:
        for family in sorted(ordered):
            for rep, pair in ordered[family]:
                if annotations[rep]["level_c_functional_contexts"].split(";")[0] != stage:
                    continue
                for key in [rep] + [other for other in pair if other != rep]:
                    a, reaction = annotations[key], reactions[key]
                    evidence = {field: a[field] for field in ("anchor_basis", "direct_chemistry_rule", "supporting_anchor_ids", "graph_distance_to_anchor", "graph_support_status", "cross_family_link_ids", "change_reason")}
                    row = {
                        "reaction_id": key, "primary_stage": a["level_c_primary_stage"],
                        "all_stages": a["level_c_functional_contexts"], "multi_classification": str(len(split(a["level_c_functional_contexts"])) > 1).lower(),
                        "level_a_modules": a["level_a_module_candidates"], "source_subsystems": a["level_b_subsystem_candidates"],
                        "reaction_family_id": family, "pathway_order": len(rows) + 1, "topology_layer": layers[rep], "step_id": rep, "display_stage": stage,
                        "original_equation": equation(reaction), "reactants_json": compact(reaction["reactants"]), "products_json": compact(reaction["products"]),
                        "stoichiometry_json": compact({"reactants": reaction["reactants"], "products": reaction["products"]}), "modifiers_json": compact(reaction["modifiers"]),
                        "reverse_partner_id": a["reverse_partner_id"], "reference_activity": a["reference_activity"],
                        "directed_reference_parameter_value": a["official_parameter_value"], "directed_reference_activity": "ZERO_PARAMETER" if Decimal(a["official_parameter_value"]) == 0 else "NONZERO_PARAMETER",
                        "functional_annotation_status": a["functional_annotation_status"], "mechanistic_reaction_type": a["mechanistic_reaction_type"],
                        "classification_evidence": compact(evidence), "classification_reason": a["direct_chemistry_rule"] or a["anchor_basis"] or a["graph_support_status"],
                        "cross_module_context": "FUNCTIONAL_MULTI:" + a["level_c_functional_contexts"] if len(split(a["level_c_functional_contexts"])) > 1 else "",
                        "source_subsystem_reaction_refs_json": compact(json.loads(audit[key]["source_module_reaction_refs_json"])),
                        "source_kinetic_reversible": reaction["source_kinetic_reversible"], "connected_reactions": compact(connected[key]),
                        "specific_intermediates": a["specific_intermediates"],
                        "topology_basis": "EXTRACTED_SPECIES_INCIDENCE;INFERRED_PAIR_ORIENTATION;SCC_CONDENSATION_PARTIAL_ORDER" if stage != "DEG_sink" else "EXTRACTED_CONSUMED_SPECIES_GROUPING",
                        "ordering_evidence_status": "INFERRED;PARTIAL_ORDER_ONLY" if stage != "DEG_sink" else "EXTRACTED;NO_CAUSAL_ORDER",
                        "markdown_anchor": key, "source_sbml_sha256": source_hash,
                    }
                    if len(split(a["level_b_subsystem_candidates"])) > 1:
                        row["cross_module_context"] += (";" if row["cross_module_context"] else "") + "SOURCE_MULTIPLICITY:" + a["level_b_subsystem_candidates"]
                    rows.append(row)
    assert len(rows) == 968 and len({row["reaction_id"] for row in rows}) == 968
    stage_counts = Counter(stage for row in rows for stage in split(row["all_stages"]))
    module_counts = Counter(module for row in rows for module in split(row["level_a_modules"]))
    subsystem_counts = Counter(subsystem for row in rows for subsystem in split(row["source_subsystems"]))
    family_counts = Counter(row["reaction_family_id"] for row in rows)
    metrics = {
        "Source species": len(species), "Source reactions": len(reactions), "Unique atlas reactions": len(rows), "Classified reactions": len(rows),
        "Multi-stage reactions": sum(row["multi_classification"] == "true" for row in rows),
        "Annotation reference-disabled": sum(row["functional_annotation_status"] == "REFERENCE_DISABLED" for row in rows),
        "Directed zero-parameter channels": sum(row["directed_reference_activity"] == "ZERO_PARAMETER" for row in rows),
        "Exact reverse pairs": sum(bool(row["reverse_partner_id"]) for row in rows) // 2,
        "Source subsystems": len(subsystem_counts), "Local subsystem entries": sum(len(json.loads(row["source_subsystem_reaction_refs_json"])) for row in rows),
        "Level-C memberships": sum(stage_counts.values()), "Level-A provenance memberships": sum(module_counts.values()),
    }
    text = ["# PNAS2017 FULL TRANSLATION NETWORK", "", "## 0. Model identity and source", "",
            "本目录逐条解释 canonical combined SBML 的完整 fMet-Gly-Gly 翻译网络。reaction ID、species ID 和 effective stoichiometry 来自原始 XML；功能标签原样保留已完成人工审核的 v2。本文只提供机制导航，不进行删除、合并、QSSA、拟合或 reduced SBML 构建。", "",
            f"Canonical SHA-256：`{source_hash}`。源文件含 241 species / 968 directed reactions；26 个 subsystem 的 1,098 local entries 映射到相同 968 combined channels，84 条具有多重来源。", "",
            "权威顺序：combined SBML → subsystem SBML → reviewed v2 → family / graph evidence → 标明 INFERRED 的导航解释。源 XML 中 k1 和初值为 1 是占位值；reference activity 来自已有 v2 的 author-CSV 参数，独立测试对作者 parameter archive 复核。", "",
            "### Source fingerprints / freshness", "", "下表绑定实际读取的源和合同字节；新版本输入需重新生成并通过测试，旧图谱不会自动成为新源的权威。", "", "| Input | SHA-256 |", "| --- | --- |"]
    for path, fingerprint in fingerprints.items():
        relative = path.relative_to(ROOT).as_posix()
        destination = "../../" + relative
        text.append(f"| [{relative}]({destination}) | `{fingerprint}` |")
    text += ["", "## 1. Reading guide and classification rules", "",
             "每条原始反应有唯一 full-ID anchor、完整 source equation、中文物理意义、source subsystem / local ID、family、全部 stages、reverse、reference activity 和分类证据。每个 exact reverse pair 相邻展示；两个 directed channels 从不改写成一条 source reversible reaction。索引 [reaction_index.csv](reaction_index.csv) 每条原始反应恰好一行。", "",
             "`primary_stage` 逐字保留 v2；6 条 SHARED_JUNCTION 的审核 primary 为空，显示为 NO_FORCED_PRIMARY。`display_stage` 只是首个已有标签的目录位置，不是新的科学分类；其余标签在阶段 cross-reference 和 MULTI index 中可见。未提出新增 secondary stages；若今后提出只能标 PROPOSED_SECONDARY_STAGE。", "",
             "`REFERENCE_DISABLED` / `DISABLED_EXACT` 表示 420 条 pair-aware / unpaired-zero rows；`ZERO_PARAMETER` 另标 485 条单方向参数零通道。65 条零速率 reverse rows 属于 FORWARD_ONLY pairs。非零参数不保证沿任意轨迹有非零通量；禁用不等于不存在或批准 DROP。", "",
             "EXTRACTED = 原始 equation / incidence / source IDs；REVIEWED_V2 = 已审核功能标签（50 条仍保留 GRAPH_PROPAGATED 证据）；INFERRED = 导航方向与机制文字；PARTIAL_ORDER_ONLY = 分支、循环或并行状态没有唯一时间序。CYCLE 指返回已命名 enzyme / machinery 节点；SHARED_JUNCTION 可表示具体共同中间体，功能 MULTI 仅用于 6 条已审核边界。", "",
             "排序先按功能阶段与 family 导航，family 内折叠 exact pairs 仅用于排序，选择 source form 支持的装配 / 释放方向，按特异中间体的生成→消耗建图。SCC 凝聚图的最长前驱层 `topology_layer` 决定层次；同层 / SCC 内按物种身份稳定排列，ID 只作最后 tie-break。逆通道仍完整展示。`pathway_order` 是 1–968 的目录行序号，不是时间顺序；跨阶段真实串联见第 3 节。", "",
             "`connected_reactions` 保存产物→下游反应物的特异中间体连接，排除 self、exact reverse 与 DEG consumers；DEG rows 为终端且连接为空。eligible species 来自原样读取 v2 bridge_species_participants 的全集，排除下列共享载体，以免自由 currency / factor hubs 伪造机理路径：`" + ";".join(sorted(SHARED_CARRIERS)) + "`。这不是动力学承诺，不忽略方程中的其他底物。", "",
             "原始 CellDesigner association / dissociation / transition 是 source form，不单独决定是否改变共价连接；游离 aminoacyl-AMP 裂解、aa-tRNA 去酰化与肽释放在逐条中文解释中明确标为化学事件。CONCEPTUAL_NET 表示概念净反应（conceptual net），每个净式均另标 not a source reaction。", "",
             "## 2. Global reaction inventory and coverage", "", "| Metric | Value |", "| --- | ---: |"]
    text += [f"| {label} | {value} |" for label, value in metrics.items()]
    text += ["", "Level-C membership sum 为 974；其相对 unique 968 多出的 6 仅为已有 secondary memberships。Level-A provenance sum 992 与 source-subsystem membership 是来源计数，不能相加称为更多 source reactions。", "", "| Level-A module | Unique reactions |", "| --- | ---: |"]
    text += [f"| `{name}` | {count} |" for name, count in sorted(module_counts.items())]
    text += ["", "| Level-C stage | Unique reactions |", "| --- | ---: |"]
    text += [f"| `{stage}` | {stage_counts[stage]} |" for stage in STAGES]
    text += ["", "### 功能大类：非互斥 unique counts", "", "| Functional group | Unique reactions | Detail entries placed here |", "| --- | ---: | ---: |"]
    for section, title, stages, _ in GROUPS:
        unique = sum(bool(split(row["all_stages"]) & set(stages)) for row in rows)
        placed = sum(row["display_stage"] in stages for row in rows)
        text.append(f"| [{title}](#group-{section}) | {unique} | {placed} |")
    text += ["", "以上各大类 unique counts 可重叠；Detail entries placed here 之和严格为 968。", ""]
    text += overview()
    for section, title, stages, guide in GROUPS:
        text += [f'<a id="group-{section}"></a>', f"## {section}. {title}", "", guide, ""]
        for stage_number, stage in enumerate(stages, 1):
            text += [f'<a id="stage-{stage}"></a>', f"### {section}.{stage_number} {stage} — {stage_counts[stage]} unique reactions", "", STAGE_GUIDES[stage], ""]
            secondary = [row for row in rows if stage in split(row["all_stages"]) and row["display_stage"] != stage]
            if secondary:
                text += ["MULTI secondary-stage cross-reference：" + "；".join(rxlink(row["reaction_id"]) + " `" + row["all_stages"] + "`" for row in secondary) + "。", ""]
            stage_rows = [row for row in rows if row["display_stage"] == stage]
            last_family, last_step, last_sink = None, None, None
            for row in stage_rows:
                key, family = row["reaction_id"], row["reaction_family_id"]
                if family != last_family:
                    text += [f"#### {family} / {row['source_subsystems']}", "", family_guide(family), ""]
                    if cyclic[family]:
                        text += ["CYCLE / PARTIAL_ORDER_ONLY：导航代表方向的 SCC 包含 " + "；".join("、".join(rxlink(key) for key in comp) for comp in cyclic[family]) + "；SCC 内没有强制唯一顺序。", ""]
                    last_family, last_step = family, None
                if stage == "DEG_sink":
                    sink = ";".join(reactions[key]["reactants"])
                    if sink != last_sink:
                        text += ["##### Consumed source state：`" + sink + "`", ""]
                        last_sink = sink
                elif row["step_id"] != last_step:
                    text += [f"##### Mechanistic layer {row['topology_layer']} — {row['step_id']}", ""]
                    last_step = row["step_id"]
                text += [f'<a id="{key}"></a>', "", "| Reaction ID | Original SBML reaction | 中文物理意义 |", "| --- | --- | --- |",
                         f"| `{key}` | `{row['original_equation']}` | {role(reactions[key], annotations[key])} |", ""]
                marker = "MULTI; " if row["multi_classification"] == "true" else ""
                text += [f"`{key}`：{marker}all_stages=`{row['all_stages']}`；primary_stage=`{row['primary_stage'] or 'NO_FORCED_PRIMARY'}`；display_stage=`{row['display_stage']}`。", "",
                         f"来源 subsystem=`{row['source_subsystems']}`；family=`{family}`；Level-A=`{row['level_a_modules']}`；source form=`{row['mechanistic_reaction_type']}`。", ""]
                local = json.loads(row["source_subsystem_reaction_refs_json"])
                text += ["原始 local entries：" + "；".join(
                    f"[{entry['source_file']}](../../models/pnas2017_full_reference/original/subsystems/{entry['source_file']}) / `{entry['source_model_id']}:{entry['source_reaction_id']}`"
                    for entry in local) + "。", ""]
                text += [f"reference_activity=`{row['reference_activity']}`；annotation_status=`{row['functional_annotation_status']}`；author reference k1=`{row['directed_reference_parameter_value']}`；directed_reference_activity=`{row['directed_reference_activity']}`。", ""]
                if row["directed_reference_activity"] == "ZERO_PARAMETER":
                    text += ["此 directed channel 的作者参考参数为零，仍属于源网络；REFERENCE_DISABLED 仅当上列 v2 annotation_status 如此标记。", ""]
                partner = row["reverse_partner_id"]
                text += ["Exact reverse partner：" + (rxlink(partner) if partner else "无；不得虚构逆反应") + f"；source reversible attribute=`{row['source_kinetic_reversible']}`（保留原始单向方程，属性不新增 reaction ID）。", "",
                         "分类证据 REVIEWED_V2：`" + row["classification_evidence"] + "`。", ""]
                edges = json.loads(row["connected_reactions"])
                if edges:
                    text += ["EXTRACTED adjacency / INFERRED downstream context：" + "；".join(f"`{species}` → " + "、".join(rxlink(target) for target in targets) for species, targets in edges.items()) + "。PARTIAL_ORDER_ONLY。", ""]
                else:
                    text += ["本条无 eligible specific-intermediate 下游连接；其他自由池仍按完整 source equation 保留。", ""]
    text += ["<a id=\"cross-module-index\"></a>", "## 10. Cross-module and multi-label index", "", "### 已审核功能 MULTI", "",
             "| Reaction ID | All reviewed stages | Primary stage | Family |", "| --- | --- | --- | --- |"]
    text += [f"| {rxlink(row['reaction_id'])} | `{row['all_stages']}` | NO_FORCED_PRIMARY | `{row['reaction_family_id']}` |" for row in rows if row["multi_classification"] == "true"]
    text += ["", "### CROSS_MODULE_INDEX：来源多重归属", "", "以下 84 条反应具有多个 source subsystem；这是交叉引用，不新增 ID，也不自动新增功能标签。", "", "| Reaction ID | Source subsystems | Reviewed stages |", "| --- | --- | --- |"]
    text += [f"| {rxlink(row['reaction_id'])} | `{row['source_subsystems']}` | `{row['all_stages']}` |" for row in rows if len(split(row["source_subsystems"])) > 1]
    text += ["", "### 已有 22 条特异中间体跨 family evidence", "", "这些 links 保留 source / target reactions 与 evidence scope；不会合并 family、改变标签或判断平衡。", "", "| Link | Intermediate | From family / channels | To family / channels | Evidence |", "| --- | --- | --- | --- | --- |"]
    for link in links:
        text.append(f"| `{link['link_id']}` | `{link['specific_intermediate']}` | `{link['source_family']}`：" + "、".join(rxlink(key) for key in sorted(split(link["source_reaction_ids"]))) + f" | `{link['target_family']}`：" + "、".join(rxlink(key) for key in sorted(split(link["target_reaction_ids"]))) + f" | {link['link_basis']}；{link['inference_scope']} |")
    text += ["", "## 11. Reaction-family / subsystem index", "", "| Family | Unique reactions | Reviewed stages | Source subsystems |", "| --- | ---: | --- | --- |"]
    text += [f"| `{family['reaction_family_id']}` | {family_counts[family['reaction_family_id']]} | `{family['functional_contexts']}` | `{family['source_subsystems']}` |" for family in families]
    text += ["", "| Source subsystem | Unique reactions |", "| --- | ---: |"]
    text += [f"| `{subsystem}` | {count} |" for subsystem, count in sorted(subsystem_counts.items())]
    text += ["", "### Full-ID lookup：每条链接指向唯一详细条目", ""]
    for family in sorted(family_counts):
        text.append(f"- `{family}`：" + "、".join(rxlink(row["reaction_id"]) for row in rows if row["reaction_family_id"] == family))
    text += ["", "## 12. Coverage and integrity verification", "",
             "验证命令（Python 3.12，标准库；不执行模拟或改写任何输入）：", "", "```text", "python scripts/render_pnas2017_reaction_atlas.py", "python scripts/test_pnas2017_reaction_atlas.py", "git diff --check", "```", "",
             "Gate A：XML、索引和 Markdown detail IDs 必须恰为同一 968；index 与 detail anchor 各唯一。Gate B：独立重解析 effective MathML，逐物种 / side 比较 index 和实际 Markdown equations；专检 re0000000414 的 2 PO4。Gate C：全部 v2 labels / status / source provenance、26 subsystems、disabled channels 和 exact reverse 同时保留。Gate D：六条已审核 MULTI 的所有 secondary stages 与 blank primary 保留。Gate E：内部 anchors / links / actual detail rows、counts 与 conceptual-net distinction 核验。Gate F：两次临时生成与 checked-in atlas 字节相同，protected source / evidence hashes 不变。", "",
             "本文记录验证协议；实际运行 PASS / FAIL 由独立 test 的输出给出，不以本文的措辞替代测试。图谱生成时同时拒绝 source / audit / v2 的 stoichiometry 或 subsystem mismatch。", "",
             "## 13. Unresolved interpretation questions", "",
             "- SOURCE_RENDERING_DISCREPANCY：历史 `reference_zero_reactions_v0.csv` 的 re0000000414 reaction_equation 文本漏掉 2 PO4；其冻结历史文件保留，本文以 canonical stoichiometryMath 和精确 audit / v2 JSON 为准。", "- PARTIAL_ORDER_ONLY：并行装配、载体交换和循环没有由静态 SBML 唯一指定的时间顺序；本文分层与路径解释是 INFERRED navigation。", "- 原始 chemical ledger 不提供完整 complex 元素组成、charge / protonation / Mg 约定；本文的 source-equation fidelity 不声称已经完成元素、质子或镁配平。", "",
             "未发现需要新 CLASSIFICATION_CONFLICT 决策的 source / reviewed-v2 冲突；没有修改任何审核标签。已有信息保留合同和 reduction_decisions 的 968 PENDING 记录保持原状，功能文档化不构成科学约化批准。", ""]
    for path, fingerprint in fingerprints.items():
        assert digest(path) == fingerprint, f"Input changed while rendering: {path}"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "reaction.md").write_text("\n".join(text), encoding="utf-8", newline="\n")
    with (output_dir / "reaction_index.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DOC)
    arguments = parser.parse_args()
    print(json.dumps(render(arguments.output_dir.resolve()), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
