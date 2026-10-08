#!/usr/bin/env python3
"""Independent source/content gates for the PNAS2017 mechanism atlas.

Uses only Python's standard library; never imports the renderer. Source species,
effective rational stoichiometry, local subsystem mapping, reverse pairs and
author-reference parameters are reconstructed independently. Generated Markdown
table equations are checked in addition to the companion CSV. Reproducibility
renders twice into temporary directories and checks protected inputs bytewise.
No kinetic simulation, reduction decision or source modification is performed.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import csv
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
RED = ROOT / "docs/reduction"
AUDIT = ROOT / "models/pnas2017_full_reference/audit"
SB = "{http://www.sbml.org/sbml/level2/version4}"
MM = "{http://www.w3.org/1998/Math/MathML}"
RID = re.compile(r"re\d{10}\Z")
JUNCTIONS = {
    "re0000000207": "RS_activation;RS_charging",
    "re0000000208": "RS_activation;RS_charging",
    "re0000000249": "RS_activation;RS_charging",
    "re0000000250": "RS_activation;RS_charging",
    "re0000000308": "ELONG_energy_coupling;RECYCLE_component_release",
    "re0000000327": "ELONG_energy_coupling;RECYCLE_component_release",
}
STAGES = {
    "RS_binding", "RS_activation", "RS_charging", "RS_to_INIT_formylation",
    "INIT_assembly", "INIT_tRNA_recruitment", "INIT_energy_commitment",
    "INIT_70S_formation", "INIT_factor_release", "ELONG_aa_tRNA_delivery",
    "ELONG_energy_coupling", "ELONG_peptide_formation", "ELONG_translocation",
    "ELONG_tRNA_release", "TERM_factor_binding", "TERM_peptide_release",
    "TERM_energy_coupling", "RECYCLE_disassembly", "RECYCLE_component_release",
    "EN_binding", "EN_energy_transfer", "EN_byproduct_processing", "DEG_sink",
}
SHARED_CARRIERS = {
    "EFTu_GTP", "EFTu_GDP", "EFTu_EFTs", "EFTu_GDP_EFTs", "EFTu_GTP_EFTs",
    "EFG_GDP", "EFG_GTP", "IF2_GDP", "IF2_GTP", "RF3_GDP", "RF3_GTP",
}
REQUIRED = {
    "reaction_id", "primary_stage", "all_stages", "multi_classification",
    "level_a_modules", "source_subsystems", "reaction_family_id", "pathway_order",
    "original_equation", "reverse_partner_id", "reference_activity",
    "functional_annotation_status", "classification_evidence", "markdown_anchor",
    "source_sbml_sha256", "reactants_json", "products_json", "stoichiometry_json",
    "modifiers_json", "source_subsystem_reaction_refs_json", "display_stage",
    "mechanistic_reaction_type", "classification_reason", "cross_module_context",
    "source_kinetic_reversible", "directed_reference_parameter_value",
    "directed_reference_activity", "topology_basis", "connected_reactions",
    "specific_intermediates", "ordering_evidence_status",
    "topology_layer", "step_id",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader), set(reader.fieldnames or [])


def labels(value):
    return set(filter(None, value.split(";")))


def math_constant(node):
    """Evaluate constant MathML exactly, rejecting variables and unsupported forms."""
    tag = node.tag.removeprefix(MM)
    if tag == "math":
        require(len(node) == 1, "MathML math must have one expression")
        return math_constant(node[0])
    if tag == "cn":
        kind = node.get("type", "real")
        left = (node.text or "").strip()
        if kind in {"rational", "e-notation"}:
            require(len(node) == 1 and node[0].tag == MM + "sep", "Invalid cn separator")
            right = (node[0].tail or "").strip()
            if kind == "rational":
                return Fraction(left) / Fraction(right)
            return Fraction(left) * Fraction(10) ** int(right)
        require(not list(node), "Unsupported nested cn")
        return Fraction(left)
    if tag == "apply":
        require(len(node) >= 2, "Empty MathML apply")
        op = node[0].tag.removeprefix(MM)
        args = [math_constant(child) for child in list(node)[1:]]
        if op == "plus":
            return sum(args, Fraction(0))
        if op == "times":
            product = Fraction(1)
            for arg in args:
                product *= arg
            return product
        if op == "minus" and len(args) in {1, 2}:
            return -args[0] if len(args) == 1 else args[0] - args[1]
        if op == "divide" and len(args) == 2:
            return args[0] / args[1]
        if op == "power" and len(args) == 2 and args[1].denominator == 1:
            return args[0] ** int(args[1])
    raise AssertionError(f"Nonconstant or unsupported stoichiometryMath: {tag}")


def source_side(reaction, side):
    result = defaultdict(Fraction)
    for ref in reaction.findall(f"{SB}listOf{side}/{SB}speciesReference"):
        math = ref.find(f"{SB}stoichiometryMath/{MM}math")
        coefficient = math_constant(math) if math is not None else Fraction(ref.get("stoichiometry", "1"))
        require(coefficient > 0, "Nonpositive source stoichiometry")
        result[ref.attrib["species"]] += coefficient
    return dict(result)


@dataclass
class Reaction:
    reactants: dict
    products: dict
    modifiers: tuple
    reversible: str

    def signature(self):
        return tuple(sorted(self.reactants.items())), tuple(sorted(self.products.items())), self.modifiers


def parse_sbml(path):
    model = ET.parse(path).getroot().find(SB + "model")
    require(model is not None, f"Missing model: {path}")
    species = {item.attrib["id"] for item in model.findall(f"{SB}listOfSpecies/{SB}species")}
    reactions = {}
    for item in model.findall(f"{SB}listOfReactions/{SB}reaction"):
        rid = item.attrib["id"]
        require(rid not in reactions, f"Duplicate source ID: {rid}")
        reactants, products = source_side(item, "Reactants"), source_side(item, "Products")
        modifiers = tuple(sorted(ref.attrib["species"] for ref in item.findall(f"{SB}listOfModifiers/{SB}modifierSpeciesReference")))
        require(set(reactants) | set(products) | set(modifiers) <= species, f"Unknown source participant: {rid}")
        reactions[rid] = Reaction(reactants, products, modifiers, item.get("reversible", "true"))
    return model.attrib["id"], species, reactions


def exact_json_side(value):
    decoded = json.loads(value)
    require(isinstance(decoded, dict), "Index stoichiometry must be a species-coefficient object")
    require(all(isinstance(number, str) for number in decoded.values()), "Exact index coefficients must be strings")
    return {species: Fraction(number) for species, number in decoded.items()}


def equation_side(value):
    value = value.strip().strip("`")
    if value in {"", "∅", "0"}:
        return {}
    result = defaultdict(Fraction)
    for term in value.split(" + "):
        parts = term.strip().split()
        require(len(parts) in {1, 2}, f"Malformed equation term: {term}")
        coefficient, species = (Fraction(1), parts[0]) if len(parts) == 1 else (Fraction(parts[0]), parts[1])
        require(coefficient > 0, f"Nonpositive equation coefficient: {term}")
        result[species] += coefficient
    return dict(result)


def parse_equation(value):
    require(value.count(" -> ") == 1, f"Source equation must be a directed channel: {value}")
    left, right = value.strip().strip("`").split(" -> ")
    return equation_side(left), equation_side(right)


def markdown_details(markdown):
    rows = defaultdict(list)
    for line_number, line in enumerate(markdown.splitlines(), 1):
        columns = [column.strip() for column in line.strip().strip("|").split("|")]
        if len(columns) >= 3 and RID.fullmatch(columns[0].strip("`")) and " -> " in columns[1]:
            rows[columns[0].strip("`")].append((columns[1].strip("`"), columns[2], line_number))
    return dict(rows)


def reaction_sections(markdown):
    """Read the actual per-reaction detail beneath each full-ID anchor."""
    matches = list(re.finditer(r'<a\s+id=[\"\']([^\"\']+)[\"\']\s*></a>', markdown))
    return {match.group(1): markdown[match.end():matches[number + 1].start() if number + 1 < len(matches) else len(markdown)]
            for number, match in enumerate(matches) if RID.fullmatch(match.group(1))}


def independent_layers(graph):
    """Kosaraju SCC plus recursive predecessor depth, independent of the renderer."""
    reverse = {node: set() for node in graph}
    for node, children in graph.items():
        for child in children:
            reverse[child].add(node)
    seen, postorder = set(), []

    def postvisit(node):
        if node in seen:
            return
        seen.add(node)
        for child in graph[node]:
            postvisit(child)
        postorder.append(node)

    for node in graph:
        postvisit(node)
    component = {}

    def assign(node, number):
        if node in component:
            return
        component[node] = number
        for parent in reverse[node]:
            assign(parent, number)

    number = 0
    for node in reversed(postorder):
        if node not in component:
            assign(node, number)
            number += 1
    predecessors = {number: set() for number in set(component.values())}
    for node, children in graph.items():
        for child in children:
            if component[node] != component[child]:
                predecessors[component[child]].add(component[node])
    depths = {}

    def depth(number):
        if number not in depths:
            depths[number] = max((depth(parent) + 1 for parent in predecessors[number]), default=0)
        return depths[number]

    return {node: depth(component[node]) for node in graph}


class Validator:
    def __init__(self):
        self.source_hash = digest(SOURCE)
        _, self.species, self.source = parse_sbml(SOURCE)
        self.v2_rows, _ = read_csv(RED / "reaction_level_annotation_v2.csv")
        self.v2 = {row["reaction_id"]: row for row in self.v2_rows}
        self.audit_rows, _ = read_csv(AUDIT / "reactions.csv")
        self.audit = {row["reaction_id"]: row for row in self.audit_rows}
        module_rows, _ = read_csv(AUDIT / "modules.csv")
        self.modules = {Path(row["source_file"]).stem: row for row in module_rows}
        self.family_rows, _ = read_csv(RED / "reaction_family_summary_v2.csv")
        self.manifest = json.loads((RED / "reaction_annotation_manifest_v2.json").read_text(encoding="utf-8"))
        self.decisions, _ = read_csv(RED / "reduction_decisions.csv")
        self.local_mapping = defaultdict(list)
        self.local_entry_count = 0
        for path in sorted((SOURCE.parent / "subsystems").glob("*.xml")):
            model_id, species, reactions = parse_sbml(path)
            require(path.stem in self.modules, f"Unknown subsystem: {path.name}")
            record = self.modules[path.stem]
            require(record["source_entry_sha256"] == digest(path), f"Subsystem source hash: {path.name}")
            require(int(record["species_count"]) == len(species), f"Subsystem species count: {path.name}")
            require(int(record["reaction_entry_count"]) == len(reactions), f"Subsystem reaction count: {path.name}")
            self.local_entry_count += len(reactions)
            for rid, reaction in reactions.items():
                self.local_mapping[reaction.signature()].append({
                    "source_model_id": model_id, "source_file": path.name, "source_reaction_id": rid,
                })
        self.mapping = {rid: self.local_mapping[reaction.signature()] for rid, reaction in self.source.items()}
        signatures = defaultdict(list)
        for rid, reaction in self.source.items():
            signatures[reaction.signature()].append(rid)
        self.reverse = {}
        for rid, reaction in self.source.items():
            candidates = signatures[(tuple(sorted(reaction.products.items())), tuple(sorted(reaction.reactants.items())), reaction.modifiers)]
            require(len(candidates) <= 1, f"Ambiguous exact reverse: {rid}")
            self.reverse[rid] = candidates[0] if candidates else ""
        archive_path = ROOT / "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
        with zipfile.ZipFile(archive_path) as archive:
            names = [name for name in archive.namelist() if name.endswith("fMGG_synthesis_parameters.csv")]
            require(len(names) == 1, "Author parameter CSV must be unique")
            raw = archive.read(names[0]).decode("utf-8-sig").replace("\r\r\n", "\n").replace("\r\n", "\n")
            self.author_parameters = {row["Name"]: Fraction(row["Value"]) for row in csv.DictReader(io.StringIO(raw))}
        self.stage_counts = Counter(stage for row in self.v2_rows for stage in labels(row["level_c_functional_contexts"]))
        self.module_counts = Counter(module for row in self.v2_rows for module in labels(row["level_a_module_candidates"]))
        self.family_counts = Counter(row["reaction_family_id"] for row in self.v2_rows)
        self.subsystem_counts = Counter(subsystem for rid in self.source for subsystem in {Path(record["source_file"]).stem for record in self.mapping[rid]})
        eligible = set().union(*(labels(row["bridge_species_participants"]) for row in self.v2_rows)) - SHARED_CARRIERS
        consumers = defaultdict(set)
        for rid, reaction in self.source.items():
            if "DEG_sink" not in labels(self.v2[rid]["level_c_functional_contexts"]):
                for species in reaction.reactants:
                    consumers[species].add(rid)
        self.connected = {}
        for rid, reaction in self.source.items():
            connections = {}
            if "DEG_sink" not in labels(self.v2[rid]["level_c_functional_contexts"]):
                for species in set(reaction.products) & eligible:
                    downstream = consumers[species] - {rid, self.reverse[rid]}
                    if downstream:
                        connections[species] = downstream
            self.connected[rid] = connections
        self.representative = {}
        family_representatives = defaultdict(set)
        for rid in sorted(self.source):
            if rid in self.representative:
                continue
            pair = {rid, self.reverse[rid]} - {""}
            stage = self.v2[rid]["level_c_functional_contexts"]
            preferred_type = None
            if stage in {"RS_binding", "INIT_assembly", "INIT_tRNA_recruitment", "INIT_70S_formation"}:
                preferred_type = "HETERODIMER_ASSOCIATION"
            elif stage in {"INIT_factor_release", "ELONG_tRNA_release", "RECYCLE_component_release"}:
                preferred_type = "DISSOCIATION"
            preferred = {item for item in pair if self.v2[item]["mechanistic_reaction_type"] == preferred_type}
            representative = min(preferred or pair)
            for item in pair:
                self.representative[item] = representative
            family_representatives[self.v2[rid]["reaction_family_id"]].add(representative)
        representative_layers = {}
        for family, representatives in family_representatives.items():
            if family == "RFAM_DEG":
                representative_layers.update({representative: 0 for representative in representatives})
                continue
            graph = {representative: set() for representative in representatives}
            for left in representatives:
                for right in representatives - {left}:
                    if set(self.source[left].products) & set(self.source[right].reactants) & eligible:
                        graph[left].add(right)
            representative_layers.update(independent_layers(graph))
        self.layers = {rid: representative_layers[representative] for rid, representative in self.representative.items()}

    def gate_a(self, rows, markdown):
        ids = [row["reaction_id"] for row in rows]
        details = markdown_details(markdown)
        require(len(self.species) == 241 and len(self.source) == 968, "Canonical inventory must be 241 species / 968 reactions")
        require(len(ids) == len(set(ids)) == 968, "Index must have 968 unique rows without duplicates")
        require(set(ids) == set(self.source) == set(details), "Index/detail source coverage mismatch")
        require(all(len(entries) == 1 for entries in details.values()), "Every reaction must have exactly one complete detailed equation")
        require(all(RID.fullmatch(rid) for rid in ids), "Shortened or fabricated reaction ID")
        sections = reaction_sections(markdown)
        require(set(sections) == set(self.source), "All detail equations need matching full-ID anchors")
        require(all(set(markdown_details(section)) == {rid} for rid, section in sections.items()), "Detailed row must occur under its matching full-ID anchor")

    def gate_b(self, rows, markdown):
        details = markdown_details(markdown)
        for row in rows:
            rid, reaction = row["reaction_id"], self.source[row["reaction_id"]]
            expected = (reaction.reactants, reaction.products)
            require(parse_equation(row["original_equation"]) == expected, f"Index equation disagrees with source: {rid}")
            require(parse_equation(details[rid][0][0]) == expected, f"Actual Markdown equation disagrees with source: {rid}")
            require((exact_json_side(row["reactants_json"]), exact_json_side(row["products_json"])) == expected, f"Index exact sides: {rid}")
            coefficients = json.loads(row["stoichiometry_json"])
            require(set(coefficients) == {"reactants", "products"}, f"Index stoichiometry sides: {rid}")
            require((exact_json_side(json.dumps(coefficients["reactants"])), exact_json_side(json.dumps(coefficients["products"]))) == expected, f"Index effective stoichiometry: {rid}")
            require(tuple(sorted(json.loads(row["modifiers_json"]))) == reaction.modifiers, f"Modifier preservation: {rid}")
            require(row["source_kinetic_reversible"] == reaction.reversible, f"Source reversible flag changed: {rid}")
        reaction = self.source["re0000000414"]
        require(reaction.products.get("PO4") == 2, "Critical source re0000000414 must produce 2 PO4")
        require("2 PO4" in details["re0000000414"][0][0], "Critical Markdown coefficient 2 PO4 missing")

    def gate_c(self, rows, markdown):
        sections = reaction_sections(markdown)
        require(self.manifest["source_sbml_sha256"] == self.source_hash, "Reviewed manifest source identity changed")
        for name, expected_hash in self.manifest["artifact_sha256"].items():
            require(digest(RED / name) == expected_hash, f"Reviewed v2 artifact bytes changed: {name}")
        require(digest(RED / "reduction_decisions.csv") == self.manifest["reduction_decisions_sha256"], "Existing scientific decisions changed")
        require(len(self.decisions) == 968 and all(row["decision_status"] == "PENDING" for row in self.decisions), "All existing scientific decisions must remain PENDING")
        require(len(self.v2_rows) == len(self.v2) == len(self.audit) == 968, "Authoritative annotation/audit inventory")
        require(len(self.modules) == len(self.subsystem_counts) == 26 and self.local_entry_count == 1098, "26 subsystem / 1098 local-entry coverage")
        require(set(self.v2) == set(self.source) == set(self.audit), "Authoritative input ID mismatch")
        require(set(self.stage_counts) == STAGES, "All 23 source-coverage stages required")
        require({row["reaction_family_id"]: int(row["reaction_count"]) for row in self.family_rows} == self.family_counts, "Reviewed family count source mismatch")
        require(all(int(record["mapped_combined_reaction_count"]) == self.subsystem_counts[name] for name, record in self.modules.items()), "Independent source subsystem mapped counts")
        for row in rows:
            rid = row["reaction_id"]
            reviewed, source_audit = self.v2[rid], self.audit[rid]
            for atlas_field, v2_field in (
                ("primary_stage", "level_c_primary_stage"), ("all_stages", "level_c_functional_contexts"),
                ("level_a_modules", "level_a_module_candidates"), ("source_subsystems", "level_b_subsystem_candidates"),
                ("reaction_family_id", "reaction_family_id"), ("mechanistic_reaction_type", "mechanistic_reaction_type"),
                ("reverse_partner_id", "reverse_partner_id"), ("reference_activity", "reference_activity"),
                ("functional_annotation_status", "functional_annotation_status"), ("specific_intermediates", "specific_intermediates"),
            ):
                require(row[atlas_field] == reviewed[v2_field], f"Reviewed v2 field changed: {rid} {atlas_field}")
            require(bool(labels(row["all_stages"])) and labels(row["all_stages"]) <= STAGES, f"Invalid functional stage: {rid}")
            require(row["display_stage"] == row["all_stages"].split(";")[0], f"Display navigation stage: {rid}")
            require(row["multi_classification"] == str(len(labels(row["all_stages"])) > 1).lower(), f"Multi flag: {rid}")
            require(row["source_sbml_sha256"] == reviewed["source_sbml_sha256"] == source_audit["source_sbml_sha256"] == self.source_hash, f"Source hash: {rid}")
            independently_mapped = sorted(self.mapping[rid], key=lambda value: (value["source_file"], value["source_reaction_id"], value["source_model_id"]))
            for value in (row["source_subsystem_reaction_refs_json"], source_audit["source_module_reaction_refs_json"]):
                require(sorted(json.loads(value), key=lambda record: (record["source_file"], record["source_reaction_id"], record["source_model_id"])) == independently_mapped, f"Independent local provenance: {rid}")
            require(labels(row["source_subsystems"]) == {Path(record["source_file"]).stem for record in independently_mapped}, f"Subsystem stems: {rid}")
            require(row["reverse_partner_id"] == self.reverse[rid], f"Independent exact reverse: {rid}")
            author_value = self.author_parameters[reviewed["official_parameter_id"]]
            require(Fraction(row["directed_reference_parameter_value"]) == Fraction(reviewed["official_parameter_value"]) == author_value, f"Author reference parameter: {rid}")
            require(row["directed_reference_activity"] == ("ZERO_PARAMETER" if author_value == 0 else "NONZERO_PARAMETER"), f"Directed author-reference activity: {rid}")
            section = sections[rid]
            require(all(stage in section for stage in labels(row["all_stages"])), f"Actual Markdown functional context lost: {rid}")
            require(all(subsystem in section for subsystem in labels(row["source_subsystems"])), f"Actual Markdown subsystem provenance lost: {rid}")
            require(row["reaction_family_id"] in section, f"Actual Markdown family lost: {rid}")
            require(row["reference_activity"] in section and row["functional_annotation_status"] in section, f"Actual Markdown reference/annotation status lost: {rid}")
            if self.reverse[rid]:
                require(self.reverse[rid] in section, f"Actual Markdown reverse channel cross-reference lost: {rid}")
            require(bool(row["classification_evidence"].strip()) and bool(row["classification_reason"].strip()), f"Missing classification evidence: {rid}")
            evidence_status = labels(row["ordering_evidence_status"])
            require(bool(row["topology_basis"].strip()) and bool(evidence_status) and evidence_status <= {"EXTRACTED", "INFERRED", "AMBIGUOUS", "PARTIAL_ORDER_ONLY", "NO_CAUSAL_ORDER"}, f"Missing ordering evidence status: {rid}")
            require(int(row["topology_layer"]) == self.layers[rid], f"Independent family SCC predecessor layer: {rid}")
            require(row["step_id"] == self.representative[rid], f"Paired source step representative: {rid}")
            connected = json.loads(row["connected_reactions"])
            require(isinstance(connected, dict), f"Connected reaction graph format: {rid}")
            for species, downstream_ids in connected.items():
                require(species in self.source[rid].products, f"Connected species is not a product: {rid} {species}")
                require(isinstance(downstream_ids, list) and len(set(downstream_ids)) == len(downstream_ids), f"Connected reaction IDs: {rid}")
                for downstream in downstream_ids:
                    require(downstream in self.source and species in self.source[downstream].reactants, f"Fabricated downstream graph edge: {rid} {species} {downstream}")
            require({species: set(downstream) for species, downstream in connected.items()} == self.connected[rid], f"Missing or extra eligible source graph connection: {rid}")
        require([int(row["pathway_order"]) for row in rows] == list(range(1, 969)), "Pathway navigation ordinals must cover 1..968 in index row order")
        require([row["reaction_id"] for row in rows] == list(sections), "Index pathway order must match actual Markdown detail order")
        disabled = sum(row["functional_annotation_status"] == "REFERENCE_DISABLED" for row in rows)
        zero = sum(Fraction(row["directed_reference_parameter_value"]) == 0 for row in rows)
        require(disabled == 420 and zero == 485, "Pair-aware 420 disabled annotations must be distinct from 485 directed zero parameters")
        require(sum(bool(partner) for partner in self.reverse.values()) // 2 == 290, "290 exact reverse pairs required")
        require(self.stage_counts["RS_to_INIT_formylation"] == 22 and self.stage_counts["DEG_sink"] == 388, "Formylation and degradation completeness")

    def gate_d(self, rows, markdown):
        by = {row["reaction_id"]: row for row in rows}
        sections = reaction_sections(markdown)
        for rid, expected in JUNCTIONS.items():
            row = by[rid]
            require(row["all_stages"] == expected and row["primary_stage"] == "", f"Shared junction labels or blank primary lost: {rid}")
            require(row["multi_classification"] == "true" and row["functional_annotation_status"] == "SHARED_JUNCTION", f"Shared junction MULTI status: {rid}")
            require("MULTI" in sections[rid] and all(stage in sections[rid] for stage in expected.split(";")), f"Actual Markdown MULTI secondary labels missing: {rid}")
        require(sum(row["multi_classification"] == "true" for row in rows) == 6, "Only six reviewed multistage classifications")

    def gate_e(self, rows, markdown):
        anchors = re.findall(r'<a\s+id=[\"\']([^\"\']+)[\"\']\s*></a>', markdown)
        require(len(anchors) == len(set(anchors)), "Duplicate explicit Markdown anchors")
        require(set(self.source) <= set(anchors), "Missing full reaction anchors")
        for row in rows:
            require(row["markdown_anchor"] in {row["reaction_id"], "#" + row["reaction_id"]}, f"Unstable reaction anchor: {row['reaction_id']}")
        # GitHub-compatible automatic heading fragments supplement explicit anchors.
        targets = set(anchors)
        heading_seen = Counter()
        for line in markdown.splitlines():
            if re.match(r"^#{1,6} ", line):
                heading = re.sub(r"^#{1,6} ", "", line).strip().lower()
                heading = re.sub(r"[^\w\- ]", "", heading)
                heading = heading.replace(" ", "-")
                occurrence = heading_seen[heading]
                heading_seen[heading] += 1
                targets.add(heading + (f"-{occurrence}" if occurrence else ""))
        links = re.findall(r'\]\(\s*#([^\s)]+)\s*(?:"[^"]*")?\)', markdown) + re.findall(r'href=[\"\']#([^\"\']+)[\"\']', markdown)
        links += re.findall(r'(?m)^\s{0,3}\[[^\]]+\]:\s*<?#([^>\s]+)>?', markdown)
        require(all(link in targets for link in links), f"Broken internal links: {sorted(set(links) - targets)[:10]}")
        metrics = {
            "Source species": len(self.species), "Source reactions": len(self.source),
            "Unique atlas reactions": len(rows), "Classified reactions": len(self.v2),
            "Multi-stage reactions": len(JUNCTIONS), "Annotation reference-disabled": 420,
            "Directed zero-parameter channels": 485, "Exact reverse pairs": 290,
            "Source subsystems": len(self.modules), "Local subsystem entries": self.local_entry_count,
            "Level-C memberships": sum(self.stage_counts.values()),
            "Level-A provenance memberships": sum(self.module_counts.values()),
        }
        metric_values = defaultdict(list)
        for line in markdown.splitlines():
            columns = [column.strip().strip("`*") for column in line.strip().strip("|").split("|")]
            if len(columns) >= 2 and columns[0] in metrics:
                require(columns[1].isdigit(), f"Nonnumeric overview metric: {columns[0]}")
                metric_values[columns[0]].append(int(columns[1]))
            if len(columns) >= 2 and columns[0] == "Unique source reactions":
                require(columns[1].isdigit() and int(columns[1]) == len(self.source), "Contradictory source-reaction total")
        require(set(metric_values) == set(metrics), f"Missing independently checked overview metrics: {sorted(set(metrics) - set(metric_values))}")
        require(all(values == [metrics[key]] for key, values in metric_values.items()), "Incorrect or repeated overview metric")
        functional_groups = {
            "RS / AMINOACYLATION": {stage for stage in STAGES if stage.startswith("RS_")},
            "INITIATION": {stage for stage in STAGES if stage.startswith("INIT_")},
            "ELONGATION": {stage for stage in STAGES if stage.startswith("ELONG_")},
            "TERMINATION / RECYCLING": {stage for stage in STAGES if stage.startswith(("TERM_", "RECYCLE_"))},
            "ENERGY REGENERATION": {stage for stage in STAGES if stage.startswith("EN_")},
            "DEG_sink / inactive reference pathways": {"DEG_sink"},
        }
        group_counts = {}
        for line in markdown.splitlines():
            columns = [column.strip() for column in line.strip().strip("|").split("|")]
            if len(columns) < 3:
                continue
            match = re.fullmatch(r"\[([^\]]+)\]\(#group-\d+\)", columns[0])
            if match and match[1] in functional_groups:
                require(match[1] not in group_counts and columns[1].isdigit() and columns[2].isdigit(), "Functional group count table format")
                group_counts[match[1]] = (int(columns[1]), int(columns[2]))
        require(set(group_counts) == set(functional_groups), "Every broad functional group needs independently checked counts")
        for title, stages in functional_groups.items():
            unique = sum(bool(labels(row["level_c_functional_contexts"]) & stages) for row in self.v2_rows)
            placed = sum(row["level_c_functional_contexts"].split(";")[0] in stages for row in self.v2_rows)
            require(group_counts[title] == (unique, placed), f"Functional group unique/placement counts: {title}")
        require(sum(placed for _, placed in group_counts.values()) == 968, "Functional-group detail placements must total exactly 968")
        for group_name, expected in (("stage", self.stage_counts), ("module", self.module_counts), ("family", self.family_counts), ("subsystem", self.subsystem_counts)):
            found = defaultdict(list)
            for line in markdown.splitlines():
                columns = [column.strip().strip("`") for column in line.strip().strip("|").split("|")]
                if len(columns) >= 2 and columns[0] in expected and columns[1].isdigit():
                    found[columns[0]].append(int(columns[1]))
            require(set(found) == set(expected), f"Missing {group_name} unique-count summary rows: {sorted(set(expected) - set(found))}")
            require(all(all(value == expected[key] for value in values) for key, values in found.items()), f"Incorrect {group_name} unique-count summary")
        require("974" in markdown and "992" in markdown and "968" in markdown, "Stage, module membership and unique totals must be distinguished")
        require("420" in markdown and "485" in markdown, "Pair-aware vs directed-zero activity counts must be distinguished")
        require(all(token in markdown for token in ("CYCLE", "BRANCH A", "BRANCH B", "SHARED_JUNCTION", "PARTIAL_ORDER_ONLY")), "Required topology reading distinctions missing")
        require("CONCEPTUAL_NET" in markdown or "conceptual net" in markdown.lower() or "概念净反应" in markdown, "Conceptual-net/source distinction missing")
        require("not a source" in markdown.lower() or "不是" in markdown and "source" in markdown.lower(), "Conceptual net reactions need explicit non-source labeling")
        for line in markdown.splitlines():
            if " -> " not in line:
                continue
            if markdown_details(line):
                continue
            if "CONCEPTUAL_NET" in line:
                require("(not a source reaction)" in line, "Every conceptual equation needs an individual non-source marker")
                continue
            ids = set(re.findall(r"\bre\d{10}\b", line))
            equations = re.findall(r"`([^`]* -> [^`]*)`", line)
            require(bool(equations) and bool(ids) and ids <= set(self.source), f"Unmarked or fabricated source equation: {line[:150]}")
            for equation in equations:
                require(any(parse_equation(equation) == (self.source[rid].reactants, self.source[rid].products) for rid in ids), f"Non-detail equation is not an attributed original source channel: {equation}")
        require("PENDING" in markdown and "968" in markdown, "Existing scientific reduction boundary absent")
        require(not re.search(r"`?re\d{10}`?\s*(?:\.\.\.|…|[-–—~])\s*`?re\d{10}", markdown), "Unexpanded reaction ID range")
        require(not re.search(r"(?:其余类似反应省略|其余反应省略|reactions? omitted)", markdown, re.I), "Omitted detail placeholder")
        require(not any(token in markdown for token in ("peptide0 + AT1", "peptide1 + AT2", "peptide2 + AT3")), "Illustrative peptide-only equations fabricated")
        details = markdown_details(markdown)
        require(all(entries[0][1] and re.search(r"[\u4e00-\u9fff]", entries[0][1]) for entries in details.values()), "Each reaction needs a Chinese physical-role explanation")
        role_fixtures = {
            143: ("aminoacyl-AMP", "化学"), 168: ("aminoacyl-AMP", "化学"),
            149: ("化学",), 174: ("化学",),
            176: ("去酰化", "共价"), 218: ("去酰化", "共价"), 417: ("去酰化", "共价"),
            216: ("再酰化", "共价"), 259: ("再酰化", "共价"), 443: ("再酰化", "共价"),
        }
        for number, required_words in role_fixtures.items():
            rid = f"re{number:010d}"
            require(all(word in details[rid][0][1] for word in required_words), f"Critical covalent-cleavage/reformation role: {rid}")
        for rid, annotation in self.v2.items():
            if "SmallMolecules" in labels(annotation["level_b_subsystem_candidates"]):
                require("游离" in details[rid][0][1] and "不含催化酶" in details[rid][0][1], f"Source nucleotide channel must not invent an enzyme: {rid}")
        require(all(Path(record["source_file"]).stem in markdown for records in self.mapping.values() for record in records), "Every subsystem needs visible provenance")


def protected_snapshot():
    """Includes every existing scientific record, original source and reference."""
    excluded = {RED / "reaction.md", RED / "reaction_index.csv"}
    return {path.relative_to(ROOT).as_posix(): digest(path)
            for directory in (ROOT / "models", ROOT / "references", ROOT / "results", ROOT / "docs/reduction")
            for path in directory.rglob("*") if path.is_file() and path not in excluded}


def gate_f(output_dir):
    before = protected_snapshot()
    renderer = ROOT / "scripts/render_pnas2017_reaction_atlas.py"
    require(renderer.exists(), "Renderer does not exist")
    with tempfile.TemporaryDirectory(prefix="pnas2017-atlas-validation-") as temp:
        generated = []
        for number in (1, 2):
            directory = Path(temp) / str(number)
            command = [sys.executable, str(renderer), "--output-dir", str(directory)]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
            require(result.returncode == 0, f"Renderer failed ({number}): {result.stdout}\n{result.stderr}")
            generated.append({name: (directory / name).read_bytes() for name in ("reaction.md", "reaction_index.csv")})
        require(generated[0] == generated[1], "Second renderer run is not byte-identical")
        require(all((output_dir / name).read_bytes() == content for name, content in generated[0].items()), "Checked-in atlas differs from reproducible renderer output")
    require(protected_snapshot() == before, "Renderer modified protected source/scientific input")
    result = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30)
    require(result.returncode == 0, f"git diff --check failed: {result.stdout}\n{result.stderr}")


def negative_controls(validator, rows, markdown):
    """Meaningful mutation probes verify guards reject adverse artifacts."""
    cases = []
    cases.append(("missing row", "a", rows[:-1], markdown))
    cases.append(("duplicate row", "a", rows + [rows[0]], markdown))
    first, second = rows[0]["reaction_id"], rows[1]["reaction_id"]
    swapped = markdown.replace(f'id="{first}"', 'id="temporary-swapped-anchor"', 1)
    swapped = swapped.replace(f'id="{second}"', f'id="{first}"', 1)
    swapped = swapped.replace('id="temporary-swapped-anchor"', f'id="{second}"', 1)
    cases.append(("equations under wrong anchors", "a", rows, swapped))
    modified = copy.deepcopy(rows)
    modified[0]["original_equation"] = "ATP -> ADP"
    cases.append(("CSV equation", "b", modified, markdown))
    detail = markdown_details(markdown)["re0000000414"][0][0]
    cases.append(("Markdown 2 PO4", "b", rows, markdown.replace(detail, detail.replace("2 PO4", "PO4"), 1)))
    modified = copy.deepcopy(rows)
    modified[0]["source_subsystem_reaction_refs_json"] = "[]"
    cases.append(("local provenance", "c", modified, markdown))
    modified = copy.deepcopy(rows)
    next(row for row in modified if row["reference_activity"] != "DISABLED_EXACT")["reference_activity"] = "DISABLED_EXACT"
    cases.append(("pair activity", "c", modified, markdown))
    modified = copy.deepcopy(rows)
    modified[0]["directed_reference_activity"] = "BAD"
    cases.append(("directed activity", "c", modified, markdown))
    modified = copy.deepcopy(rows)
    next(row for row in modified if validator.connected[row["reaction_id"]])["connected_reactions"] = "{}"
    cases.append(("eligible topology edge omitted", "c", modified, markdown))
    modified = copy.deepcopy(rows)
    modified[-1]["pathway_order"] = "1"
    cases.append(("navigation order repeated", "c", modified, markdown))
    modified = copy.deepcopy(rows)
    modified[0]["topology_layer"] = str(int(modified[0]["topology_layer"]) + 1)
    cases.append(("family SCC layer altered", "c", modified, markdown))
    modified = copy.deepcopy(rows)
    oriented = next(row for row in modified if validator.reverse[row["reaction_id"]] and validator.representative[row["reaction_id"]] != min(row["reaction_id"], validator.reverse[row["reaction_id"]]))
    oriented["step_id"] = min(oriented["reaction_id"], validator.reverse[oriented["reaction_id"]])
    cases.append(("paired mechanistic orientation altered", "c", modified, markdown))
    disabled_id = next(row["reaction_id"] for row in rows if row["functional_annotation_status"] == "REFERENCE_DISABLED")
    section = reaction_sections(markdown)[disabled_id]
    cases.append(("Markdown disabled status lost", "c", rows, markdown.replace(section, section.replace("REFERENCE_DISABLED", "omitted"), 1)))
    modified = copy.deepcopy(rows)
    next(row for row in modified if row["reaction_id"] == "re0000000207")["all_stages"] = "RS_activation"
    cases.append(("secondary stage lost", "d", modified, markdown))
    section = reaction_sections(markdown)["re0000000207"]
    cases.append(("Markdown secondary stage lost", "d", rows, markdown.replace(section, section.replace("RS_charging", "omitted"), 1)))
    cases.append(("duplicate anchor", "e", rows, markdown + '\n<a id="re0000000001"></a>\n'))
    cases.append(("broken link", "e", rows, markdown + "\n[broken](#nonexistent-pnas2017-anchor)\n"))
    cases.append(("broken reference link", "e", rows, markdown + "\n[missing][internal]\n\n[internal]: #nonexistent-pnas2017-anchor\n"))
    cases.append(("fabricated source equation", "e", rows, markdown + "\n**Original source reaction:** GFP + ATP -> Pi\n"))
    covalent_role = markdown_details(markdown)["re0000000176"][0][1]
    cases.append(("covalent channel mislabeled binding", "e", rows, markdown.replace(covalent_role, "普通因子解离。", 1)))
    cases.append(("count corruption", "e", rows, re.sub(r"(\|\s*`?RS_binding`?\s*\|\s*)48(\s*\|)", r"\g<1>49\2", markdown, count=1)))
    pattern = r"(\|\s*\[RS / AMINOACYLATION\]\(#group-4\)\s*\|\s*)(\d+)(\s*\|)"
    corrupted = re.sub(pattern, lambda match: match[1] + str(int(match[2]) + 1) + match[3], markdown, count=1)
    cases.append(("functional-group count corruption", "e", rows, corrupted))
    for name in ("Source species", "Source reactions", "Unique atlas reactions", "Classified reactions",
                 "Multi-stage reactions", "Annotation reference-disabled", "Directed zero-parameter channels",
                 "Exact reverse pairs", "Source subsystems", "Local subsystem entries",
                 "Level-C memberships", "Level-A provenance memberships"):
        pattern = r"(\|\s*`?" + re.escape(name) + r"`?\s*\|\s*)(\d+)(\s*\|)"
        corrupted = re.sub(pattern, lambda match: match[1] + str(int(match[2]) + 1) + match[3], markdown, count=1)
        cases.append(("overview metric " + name, "e", rows, corrupted))
    for name, gate, mutated_rows, mutated_markdown in cases:
        require(mutated_rows != rows or mutated_markdown != markdown, f"Negative control was a no-op: {name}")
        try:
            getattr(validator, "gate_" + gate)(mutated_rows, mutated_markdown)
        except (AssertionError, KeyError, ValueError):
            continue
        raise AssertionError(f"Negative control not rejected: {name}")
    return len(cases)


def parser_regressions():
    fixtures = (
        ("<cn>2</cn>", Fraction(2)),
        ('<cn type="rational">2<sep/>3</cn>', Fraction(2, 3)),
        ('<cn type="e-notation">2<sep/>-3</cn>', Fraction(1, 500)),
        ("<apply><plus/><cn>1</cn><cn>2</cn></apply>", Fraction(3)),
    )
    for expression, expected in fixtures:
        node = ET.fromstring('<math xmlns="http://www.w3.org/1998/Math/MathML">' + expression + "</math>")
        require(math_constant(node) == expected, "Exact constant MathML parser regression")
    node = ET.fromstring('<math xmlns="http://www.w3.org/1998/Math/MathML"><ci>variable</ci></math>')
    try:
        math_constant(node)
    except AssertionError:
        return
    raise AssertionError("Symbolic stoichiometryMath must never default to coefficient one")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=RED, help="Atlas directory to validate")
    args = parser.parse_args()
    try:
        parser_regressions()
        validator = Validator()
        rows, fields = read_csv(args.output_dir / "reaction_index.csv")
        require(REQUIRED <= fields, f"Missing index fields: {sorted(REQUIRED - fields)}")
        markdown = (args.output_dir / "reaction.md").read_text(encoding="utf-8")
        for gate in "abcde":
            getattr(validator, "gate_" + gate)(rows, markdown)
            print(f"Gate {gate.upper()}: PASS")
        controls = negative_controls(validator, rows, markdown)
        print(f"Adversarial content controls: PASS ({controls} mutations rejected)")
        gate_f(args.output_dir)
        print("Gate F: PASS (two byte-identical temporary renders; protected inputs unchanged; git diff --check)")
        print(json.dumps({"species": len(validator.species), "source_reactions": len(validator.source),
                          "unique_atlas_reactions": len(rows), "multi_stage": 6,
                          "annotation_reference_disabled": 420, "directed_zero_parameter": 485,
                          "exact_reverse_pairs": 290, "subsystems": len(validator.modules),
                          "subsystem_local_entries": validator.local_entry_count,
                          "stage_memberships": sum(validator.stage_counts.values()),
                          "module_memberships": sum(validator.module_counts.values()),
                          "stage_counts": dict(sorted(validator.stage_counts.items()))}, sort_keys=True))
        return 0
    except (AssertionError, OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"Atlas validation: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
