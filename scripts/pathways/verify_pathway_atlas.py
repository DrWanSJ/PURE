#!/usr/bin/env python3
"""Independent, source-based acceptance checks for the Phase A pathway atlas.

This verifier does not import the builder. It reparses canonical SBML, evaluates
stoichiometryMath exactly, and reads the archived author parameter CSV itself.
Passing these checks establishes bounded structural consistency, never kinetics
or human approval of Phase B.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

import networkx as nx


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
RED = ROOT / "docs/reduction"
AUTHOR = ROOT / "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
DEFAULT_OUTPUT = RED / "pathways"
SB = "{http://www.sbml.org/sbml/level2/version4}"
MM = "{http://www.w3.org/1998/Math/MathML}"
RID = re.compile(r"re\d{10}\Z")
ALLOWED_TYPES = {"PRODUCTIVE_PATH", "ALTERNATIVE_ENTRY", "COMPETITIVE_BRANCH",
                 "REVERSE_EDGE", "RETURN_LOOP", "REJOIN", "CROSS_FAMILY_LINK",
                 "REFERENCE_DISABLED", "UNRESOLVED"}
GLY_SAMPLE = [f"re{x:010d}" for x in (126, 136, 205, 197, 189, 178, 182, 145)]
GLY_ALTERNATE = [f"re{x:010d}" for x in (126, 136, 140, 127, 209, 178, 182, 145)]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def labels(value):
    return set(filter(None, value.split(";")))


def constant(node):
    """Evaluate only constant MathML; reject unknown/variable expressions."""
    tag = node.tag.removeprefix(MM)
    if tag == "math":
        require(len(node) == 1, "MathML requires exactly one expression")
        return constant(node[0])
    if tag == "cn":
        left = (node.text or "").strip()
        kind = node.get("type", "real")
        if kind in {"rational", "e-notation"}:
            require(len(node) == 1 and node[0].tag == MM + "sep", "Invalid cn separator")
            right = (node[0].tail or "").strip()
            return Fraction(left) / Fraction(right) if kind == "rational" else Fraction(left) * Fraction(10) ** int(right)
        require(not list(node), "Unexpected nested cn")
        return Fraction(left)
    if tag == "apply":
        require(len(node) > 1, "Empty MathML operation")
        op = node[0].tag.removeprefix(MM)
        values = [constant(child) for child in list(node)[1:]]
        if op == "plus":
            return sum(values, Fraction())
        if op == "times":
            result = Fraction(1)
            for value in values:
                result *= value
            return result
        if op == "minus" and len(values) in {1, 2}:
            return -values[0] if len(values) == 1 else values[0] - values[1]
        if op == "divide" and len(values) == 2:
            return values[0] / values[1]
        if op == "power" and len(values) == 2 and values[1].denominator == 1:
            return values[0] ** int(values[1])
    raise AssertionError(f"Unsupported or nonconstant stoichiometryMath: {tag}")


def source_side(reaction, name):
    result = defaultdict(Fraction)
    for ref in reaction.findall(f"{SB}listOf{name}/{SB}speciesReference"):
        math = ref.find(f"{SB}stoichiometryMath/{MM}math")
        number = constant(math) if math is not None else Fraction(ref.get("stoichiometry", "1"))
        require(number > 0, "Nonpositive SBML coefficient")
        result[ref.attrib["species"]] += number
    return dict(result)


def parse_source(path=SOURCE):
    model = ET.parse(path).getroot().find(SB + "model")
    require(model is not None, "SBML model missing")
    items = model.findall(f"{SB}listOfSpecies/{SB}species")
    species = {item.attrib["id"] for item in items}
    require(len(species) == len(items), "Duplicate source species IDs")
    reactions = {}
    for item in model.findall(f"{SB}listOfReactions/{SB}reaction"):
        rid = item.attrib["id"]
        require(rid not in reactions, f"Duplicate source reaction {rid}")
        left, right = source_side(item, "Reactants"), source_side(item, "Products")
        modifiers = sorted(ref.attrib["species"] for ref in item.findall(f"{SB}listOfModifiers/{SB}modifierSpeciesReference"))
        require(set(left) | set(right) | set(modifiers) <= species, f"Unknown source species at {rid}")
        reactions[rid] = {"reactants": left, "products": right, "modifiers": modifiers,
                          "source_reversible": item.get("reversible", "true")}
    return species, reactions


def exact_side(value):
    require(isinstance(value, dict), "Stoichiometry must be an object")
    require(all(isinstance(number, str) for number in value.values()), "Exact coefficients must be strings")
    result = {species: Fraction(number) for species, number in value.items()}
    require(all(number > 0 for number in result.values()), "Nonpositive rendered stoichiometry")
    return result


def equation_side(value):
    if value.strip() in {"", "0", "∅"}:
        return {}
    result = defaultdict(Fraction)
    for term in value.split(" + "):
        parts = term.strip().split()
        require(len(parts) in {1, 2}, f"Invalid equation term {term}")
        number, species = (Fraction(1), parts[0]) if len(parts) == 1 else (Fraction(parts[0]), parts[1])
        require(number > 0, "Nonpositive displayed coefficient")
        result[species] += number
    return dict(result)


def parse_equation(value):
    value = value.strip().strip("`")
    require(value.count(" -> ") == 1, f"Equation must show one directed channel: {value}")
    left, right = value.split(" -> ")
    return equation_side(left), equation_side(right)


def signature(reaction, reverse=False):
    left, right = reaction["reactants"], reaction["products"]
    if reverse:
        left, right = right, left
    return tuple(sorted(left.items())), tuple(sorted(right.items())), tuple(reaction["modifiers"])


def markdown_equations(markdown):
    """Inspect equations that are actually printed, retaining duplicate displays."""
    result = defaultdict(list)
    for line_number, line in enumerate(markdown.splitlines(), 1):
        columns = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if len(columns) >= 2 and RID.fullmatch(columns[0]):
            require(len(columns) == 5, f"Malformed reaction table at Markdown line {line_number}")
            require(" -> " in columns[1], f"Missing actual equation at line {line_number}")
            result[columns[0]].append((columns, line_number))
    return result


def load_artifacts(output_dir):
    output_dir = Path(output_dir)
    return (json.loads((output_dir / "glyrs_metrs_graph.json").read_text(encoding="utf-8")),
            read_csv(output_dir / "glyrs_metrs_pathway_index.csv"),
            (output_dir / "glyrs_metrs_sample.md").read_text(encoding="utf-8"))


class Validator:
    def __init__(self):
        self.species, self.source = parse_source()
        self.species_names = {item.attrib["id"]: item.get("name", item.attrib["id"])
                              for item in ET.parse(SOURCE).getroot().findall(f"{SB}model/{SB}listOfSpecies/{SB}species")}
        self.v2 = {row["reaction_id"]: row for row in read_csv(RED / "reaction_level_annotation_v2.csv")}
        require(set(self.v2) == set(self.source), "Reviewed annotations must cover source exactly")
        require({row["source_sbml_sha256"] for row in self.v2.values()} == {digest(SOURCE)}, "Canonical SBML fingerprint must agree with reviewed source evidence")
        with zipfile.ZipFile(AUTHOR) as archive:
            names = [name for name in archive.namelist() if name.endswith("fMGG_synthesis_parameters.csv")]
            require(len(names) == 1, "Author parameter CSV must be unique")
            raw = archive.read(names[0]).decode("utf-8-sig").replace("\r\r\n", "\n").replace("\r\n", "\n")
            rows = list(csv.DictReader(io.StringIO(raw)))
        self.author_parameters = {row["Name"]: Fraction(row["Value"]) for row in rows}
        require(len(self.author_parameters) == len(rows), "Duplicate author parameters")
        self.values = {}
        for rid, row in self.v2.items():
            value = self.author_parameters[row["official_parameter_id"]]
            require(value == Fraction(row["official_parameter_value"]), f"Author/annotation parameter mismatch at {rid}")
            self.values[rid] = value
        by_signature = defaultdict(list)
        for rid, reaction in self.source.items():
            by_signature[signature(reaction)].append(rid)
        self.reverse = {}
        for rid, reaction in self.source.items():
            candidates = by_signature[signature(reaction, reverse=True)]
            require(len(candidates) <= 1, f"Ambiguous exact reverse at {rid}")
            self.reverse[rid] = candidates[0] if candidates else None
        self.carriers = {enzyme: {species for species in self.species if species == enzyme or species.startswith(enzyme + "_")}
                         for enzyme in ("GlyRS", "MetRS")}
        self.incident = {enzyme: {rid for rid, reaction in self.source.items()
                                 if (set(reaction["reactants"]) | set(reaction["products"])) & states}
                         for enzyme, states in self.carriers.items()}
        self.scoped = set().union(*self.incident.values()) | {
            rid for rid, row in self.v2.items()
            if labels(row["level_c_functional_contexts"]) & {"RS_binding", "RS_activation", "RS_charging"}}
        self.noncarrier = self.scoped - set().union(*self.incident.values())

    def activity(self, rid):
        return "REFERENCE_DISABLED" if self.values[rid] == 0 else "NONZERO_PARAMETER"

    def gate_1(self, graph, rows, markdown):
        require(len(self.species) == 241 and len(self.source) == 968, "Canonical 241 species / 968 reactions")
        require(graph["schema_version"] == 1, "Unsupported pathway graph schema")
        require(set(graph["species"]) == self.species, "Full source species identity")
        require({sid: item["name"] for sid, item in graph["species"].items()} == self.species_names, "Original SBML species names")
        require(set(graph["reactions"]) == set(self.source), "Full source reaction identity; directed channels must not merge")
        required_sources = {SOURCE.relative_to(ROOT).as_posix(), (RED / "reaction_level_annotation_v2.csv").relative_to(ROOT).as_posix(), AUTHOR.relative_to(ROOT).as_posix()}
        provenance = graph["source_provenance"]
        require(required_sources <= {record["path"] for record in provenance}, "Source provenance must include SBML, reviewed annotations and author archive")
        for record in provenance:
            require(record["sha256"] == digest(ROOT / record["path"]), f"Stale source provenance {record['path']}")
            require(bool(record["authority"]), "Source authority missing")
        expected_arcs = Counter()
        for rid, source in self.source.items():
            item = graph["reactions"][rid]
            for side in ("reactants", "products"):
                require(exact_side(item[side]) == source[side], f"Source stoichiometry {rid} {side}")
            require(parse_equation(item["equation"]) == (source["reactants"], source["products"]), f"JSON equation {rid}")
            require(item["modifiers"] == source["modifiers"], f"Source modifiers {rid}")
            require(item["source_reversible"] is (source["source_reversible"] == "true"), f"Source reversibility flag {rid}")
            require(item["reverse_reaction_id"] == self.reverse[rid], f"Exact directed reverse {rid}")
            require(Fraction(item["reference_parameter"]) == self.values[rid], f"Archived author parameter {rid}")
            require(item["reference_activity"] == self.activity(rid), f"Directed reference activity {rid}")
            require(item["reference_pair_activity"] == self.v2[rid]["reference_activity"], f"Original pair-aware activity {rid}")
            require(set(item["level_c"]) == labels(self.v2[rid]["level_c_functional_contexts"]), f"Reviewed multi-label classification {rid}")
            require(item["reaction_family"] == self.v2[rid]["reaction_family_id"], f"Reviewed RFAM {rid}")
            require(item["mechanistic_reaction_type"] == self.v2[rid]["mechanistic_reaction_type"], f"Reviewed reaction mechanism {rid}")
            require(bool(item["source_provenance"]), f"Reaction provenance {rid}")
            for species, number in source["reactants"].items():
                expected_arcs[species, rid, str(number), "reactant"] += 1
            for species, number in source["products"].items():
                expected_arcs[rid, species, str(number), "product"] += 1
            expected_net = {species: source["products"].get(species, Fraction()) - source["reactants"].get(species, Fraction())
                            for species in set(source["reactants"]) | set(source["products"])}
            expected_net = {species: value for species, value in expected_net.items() if value}
            require({species: Fraction(number) for species, number in graph["petri_net"]["stoichiometry"][rid].items()} == expected_net,
                    f"Petri net signed stoichiometry {rid}")
        actual_arcs = Counter((arc["source"], arc["target"], str(Fraction(arc["stoichiometry"])), arc["role"])
                              for arc in graph["petri_net"]["arcs"])
        require(actual_arcs == expected_arcs, "All directed, weighted source Petri arcs must match")
        require(set(graph["petri_net"]["stoichiometry"]) == set(self.source), "Petri matrix reaction IDs")
        require(self.source["re0000000414"]["products"]["PO4"] == 2, "Source stoichiometryMath must produce 2 PO4")
        details = markdown_equations(markdown)
        require(set(details) == self.scoped, "Actual Markdown equation coverage must equal Phase A scope")
        for rid, displays in details.items():
            for columns, line in displays:
                require(parse_equation(columns[1]) == (self.source[rid]["reactants"], self.source[rid]["products"]), f"Actual Markdown equation {rid}, line {line}")
                require(labels(columns[2]) == labels(self.v2[rid]["level_c_functional_contexts"]), f"Actual Markdown labels {rid}")
                require(columns[3] == self.v2[rid]["reaction_family_id"], f"Actual Markdown RFAM {rid}")
                require(columns[4] == self.activity(rid), f"Actual Markdown directed activity {rid}")
        return {"species": 241, "original_reactions": 968, "petri_arcs": sum(expected_arcs.values()),
                "actual_markdown_equations": sum(map(len, details.values())), "directed_zero_parameters": sum(value == 0 for value in self.values.values())}

    def check_transition(self, enzyme, transition):
        rid = transition["reaction_id"]
        require(rid in self.incident[enzyme], f"Noncarrier reaction cannot be a {enzyme} transition: {rid}")
        source, states = self.source[rid], self.carriers[enzyme]
        before, after = set(source["reactants"]) & states, set(source["products"]) & states
        require(len(transition["carrier_before"]) == len(before) and set(transition["carrier_before"]) == before, f"Carrier before {rid}")
        require(len(transition["carrier_after"]) == len(after) and set(transition["carrier_after"]) == after, f"Carrier after {rid}")
        require(exact_side(transition["other_reactants"]) == {s: n for s, n in source["reactants"].items() if s not in states}, f"Required other reactants omitted or changed at {rid}")
        require(exact_side(transition["other_products"]) == {s: n for s, n in source["products"].items() if s not in states}, f"Other products omitted or changed at {rid}")
        require(set(transition["level_c"]) == labels(self.v2[rid]["level_c_functional_contexts"]), f"Transition multi-labels {rid}")
        require(transition["reaction_family"] == self.v2[rid]["reaction_family_id"], f"Transition RFAM {rid}")
        require(transition["reverse_reaction_id"] == self.reverse[rid], f"Transition reverse {rid}")
        require(transition["reference_activity"] == self.activity(rid), f"Transition reference activity {rid}")
        require(transition["mechanistic_reaction_type"] == self.v2[rid]["mechanistic_reaction_type"], f"Transition exit mechanism {rid}")
        require(bool(transition["source_provenance"]), f"Transition provenance {rid}")
        require(exact_side(transition["simultaneous_requirements"]) == source["reactants"], f"Simultaneous multi-reactant requirements {rid}")
        projections = transition["tracked_carriers"]
        require(len({p["carrier"] for p in projections}) == len(projections), f"Duplicate tracked carriers {rid}")
        expected_projections = {enzyme: (before, after)}
        token = {"GlyRS": "tRNAGlyGCC", "MetRS": "tRNAfMetCAU"}[enzyme]
        trna_before = {s for s in source["reactants"] if token in s}
        trna_after = {s for s in source["products"] if token in s}
        if trna_before or trna_after:
            expected_projections[token] = trna_before, trna_after
        require({p["carrier"] for p in projections} == set(expected_projections), f"All simultaneous tracked carriers must remain explicit {rid}")
        for projection in projections:
            expected_before, expected_after = expected_projections[projection["carrier"]]
            require(set(projection["before"]) == expected_before and set(projection["after"]) == expected_after,
                    f"Tracked carrier source-state projection {rid}/{projection['carrier']}")
            require(projection["evidence"] == "INFERRED_IDENTITY_PROJECTION", f"Bounded carrier interpretation {rid}")
        types = set(transition["types"])
        require(types <= ALLOWED_TYPES, f"Unknown transition type {rid}")
        require(("REFERENCE_DISABLED" in types) == (self.values[rid] == 0), f"Zero-parameter transition type {rid}")
        require(("REVERSE_EDGE" in types) == bool(self.reverse[rid]), f"Explicit reverse-edge label {rid}")

    def check_walk(self, enzyme, rids, states):
        require(bool(rids) and len(states) == len(rids) + 1, "Walk length must match carrier states")
        require(set(states) <= self.carriers[enzyme], f"Walk contains nonexistent or wrong carrier for {enzyme}")
        for number, rid in enumerate(rids):
            require(rid in self.incident[enzyme], f"Walk reaction outside {enzyme}: {rid}")
            require(states[number] in self.source[rid]["reactants"], f"Carrier not consumed at {rid}")
            require(states[number + 1] in self.source[rid]["products"], f"Carrier not produced at {rid}; mutually exclusive exits cannot form a chain")

    def gate_2(self, graph, rows, markdown):
        require(graph["phase"] == "A" and graph["scientific_status"] == "HUMAN_REVIEW_REQUIRED", "Phase A human-review boundary must remain explicit")
        total_paths = 0
        for enzyme, module in graph["modules"].items():
            require(enzyme in self.carriers, f"Unauthorized Phase B carrier {enzyme}")
            paths = {path["id"]: path for path in module["paths"]}
            require(len(paths) == len(module["paths"]), "Duplicate pathway ID")
            require(bool(paths), f"Missing sample paths for {enzyme}")
            for path in paths.values():
                total_paths += 1
                rids, states = path["reaction_ids"], path["states"]
                self.check_walk(enzyme, rids, states)
                simple_states = states[:-1] if states[0] == states[-1] else states
                require(len(simple_states) == len(set(simple_states)), f"Representative path repeats internal carrier states {path['id']}")
                require(path["start"] == states[0] and path["end"] == states[-1], f"Path endpoints {path['id']}")
                require(path["evidence_status"] == "STRUCTURALLY_SUPPORTED", f"Path lacks bounded structural evidence: {path['id']}")
                require(len(path["steps"]) == len(rids), f"Path step inventory {path['id']}")
                require([step["reaction_id"] for step in path["steps"]] == rids, f"Path step order {path['id']}")
                for step in path["steps"]:
                    self.check_transition(enzyme, step)
                require(path["reference_feasible"] is all(self.values[rid] > 0 for rid in rids), f"A disabled reaction cannot represent a parameter-enabled reference path: {path['id']}")
                types = set(path["types"])
                require(types <= ALLOWED_TYPES and types & {"PRODUCTIVE_PATH", "ALTERNATIVE_ENTRY"}, f"Pathway type {path['id']}")
                if "PRODUCTIVE_PATH" in types:
                    require(states[0] == enzyme and states[-1] == enzyme, f"Productive path must restore enzyme {path['id']}")
                    target = path["target_product"]
                    require(target in self.species and target not in self.carriers[enzyme], f"Real released product required {path['id']}")
                    require(target == {"GlyRS": "GlytRNAGlyGCC", "MetRS": "MettRNAfMetCAU"}[enzyme], f"Charging target must be the cognate aminoacylated tRNA: {path['id']}")
                    net = sum(self.source[rid]["products"].get(target, Fraction()) - self.source[rid]["reactants"].get(target, Fraction()) for rid in rids)
                    require(net > 0, f"Productive path does not release net target product {path['id']}")
                for link in path["rejoins"]:
                    require(link["path_id"] in paths, f"Rejoin target path missing {path['id']}")
                    require(link["state"] == path["end"] and link["state"] in paths[link["path_id"]]["states"], f"Rejoin must reach same actual carrier state {path['id']}")
                for link in path["shared_continuations"]:
                    require(link["path_id"] in paths and link["reaction_ids"], f"Shared continuation target {path['id']}")
                    target_path = paths[link["path_id"]]
                    count = len(link["reaction_ids"])
                    require(rids[-count:] == target_path["reaction_ids"][-count:] == link["reaction_ids"], f"Actual consecutive shared suffix {path['id']}")
                    require(states[-count - 1] == target_path["states"][-count - 1] == link["state"], f"Shared continuation actual rejoin state {path['id']}")
        require(set(graph["modules"]) == set(self.carriers), "Both GlyRS and MetRS prototypes required")
        gly_paths = graph["modules"]["GlyRS"]["paths"]
        require(any(path["reaction_ids"] == GLY_SAMPLE for path in gly_paths), "Required eight-step GlyRS sample missing")
        require(any(path["reaction_ids"] == GLY_ALTERNATE for path in gly_paths), "Required pre-tRNA activation route missing")
        require(any(path["reaction_ids"][:2] == ["re0000000132", "re0000000134"] and "GlyRS_Gly_ATP" in path["states"] for path in gly_paths), "GlyRS ATP-first alternative missing")
        require(set().union(*(labels(self.v2[rid]["level_c_functional_contexts"]) for rid in GLY_SAMPLE)) == {"RS_binding", "RS_activation", "RS_charging"}, "GlyRS fixture must cross all three Level-C contexts")
        require(len({self.v2[rid]["reaction_family_id"] for rid in GLY_SAMPLE}) > 1, "GlyRS fixture must span RFAMs")
        for enzyme, tRNA, amino in (("GlyRS", "tRNAGlyGCC", "Gly"), ("MetRS", "tRNAfMetCAU", "Met")):
            module = graph["modules"][enzyme]
            for ligand in (amino, "ATP", tRNA):
                require(any(path["states"][0] == enzyme and ligand in self.source[path["reaction_ids"][0]]["reactants"] for path in module["paths"]), f"Missing {ligand}-first entry for {enzyme}")
            activation_timing = set()
            for path in module["paths"]:
                if "PRODUCTIVE_PATH" not in path["types"]:
                    continue
                for rid in path["reaction_ids"]:
                    reaction = self.source[rid]
                    # Exact source transformation ATP-bound -> aminoacyl-AMP
                    # distinguishes activation from reversible ligand binding.
                    before = set(reaction["reactants"]) & self.carriers[enzyme]
                    after = set(reaction["products"]) & self.carriers[enzyme]
                    if any("_ATP" in state for state in before) and any(amino + "AMP" in state for state in after):
                        activation_timing.add(any(tRNA in state for state in before | after))
            require(activation_timing == {False, True}, f"Both pre-tRNA and tRNA-bound activation representatives required for {enzyme}")
        return {"representative_paths": total_paths, "required_glyrs_fixture_steps": 8, "enzyme_recovery": "CHECKED", "scope": "PHASE_A_STRUCTURAL_ONLY"}

    def gate_3(self, graph, rows, markdown):
        totals = Counter()
        for enzyme, states in self.carriers.items():
            module = graph["modules"][enzyme]
            require(len(module["carrier_states"]) == len(states) and set(module["carrier_states"]) == states, f"Complete {enzyme} carrier inventory")
            require(len(module["reaction_ids"]) == len(self.incident[enzyme]) and set(module["reaction_ids"]) == self.incident[enzyme], f"All source exits, including sinks and reverse channels, required for {enzyme}")
            transitions = {item["reaction_id"]: item for item in module["transitions"]}
            require(len(transitions) == len(module["transitions"]) and set(transitions) == self.incident[enzyme], f"Transition completeness {enzyme}; cross-family edges cannot be cut")
            source_graph = nx.DiGraph()
            source_graph.add_nodes_from(states)
            outgoing, incoming = defaultdict(set), defaultdict(set)
            for rid in self.incident[enzyme]:
                self.check_transition(enzyme, transitions[rid])
                reaction = self.source[rid]
                before, after = set(reaction["reactants"]) & states, set(reaction["products"]) & states
                for state in before:
                    outgoing[state].add(rid)
                for state in after:
                    incoming[state].add(rid)
                for start in before:
                    for end in after:
                        source_graph.add_edge(start, end)
            expected_branches = {state: rids for state, rids in outgoing.items() if len(rids) > 1}
            expected_rejoins = {state: rids for state, rids in incoming.items() if len(rids) > 1}
            branches = {item["state"]: set(item["outgoing_reaction_ids"]) for item in module["branches"]}
            rejoins = {item["state"]: set(item["incoming_reaction_ids"]) for item in module["rejoins"]}
            require(len(branches) == len(module["branches"]) and branches == expected_branches, f"All mutually competing original exits required for {enzyme}")
            require(len(rejoins) == len(module["rejoins"]) and rejoins == expected_rejoins, f"All real source-state rejoins required for {enzyme}")
            require(all(len(item["outgoing_reaction_ids"]) == len(set(item["outgoing_reaction_ids"])) for item in module["branches"]), "Duplicate branch reaction")
            require(all(len(item["incoming_reaction_ids"]) == len(set(item["incoming_reaction_ids"])) for item in module["rejoins"]), "Duplicate rejoin reaction")
            expected_sccs = {frozenset(component) for component in nx.strongly_connected_components(source_graph)}
            actual_sccs = {frozenset(item["members"]) for item in module["sccs"]}
            require(len(actual_sccs) == len(module["sccs"]) and actual_sccs == expected_sccs, f"Directed cycles cannot be treated as DAG states: {enzyme} SCC partition")
            state_component = {}
            for item in module["sccs"]:
                component = set(item["members"])
                require(len(component) == len(item["members"]), "Duplicate SCC state")
                cyclic = len(component) > 1 or any(source_graph.has_edge(state, state) for state in component)
                require(item["cyclic"] is cyclic, f"Directed SCC cycle flag {enzyme}/{item['id']}")
                for state in component:
                    state_component[state] = item["id"]
            require(len({item["id"] for item in module["sccs"]}) == len(module["sccs"]), "Duplicate SCC ID")
            expected_condensation = {(state_component[start], state_component[end]) for start, end in source_graph.edges if state_component[start] != state_component[end]}
            actual_condensation = {tuple(edge) for edge in module["condensation_edges"]}
            require(actual_condensation == expected_condensation and len(actual_condensation) == len(module["condensation_edges"]), f"Actual SCC condensation edges {enzyme}")
            condensed = nx.DiGraph()
            condensed.add_nodes_from(state_component.values())
            condensed.add_edges_from(actual_condensation)
            require(nx.is_directed_acyclic_graph(condensed), "Only SCC condensation may be called a DAG")
            require(bool(module["return_loops"]), f"Directed returns require explicit certificates {enzyme}")
            for loop in module["return_loops"]:
                self.check_walk(enzyme, loop["reaction_ids"], loop["states"])
                require(loop["states"][0] == loop["states"][-1], f"Return loop not closed {loop['id']}")
                require(len(set(loop["states"][:-1])) == len(loop["states"]) - 1, f"Return certificate repeats internal states {loop['id']}")
                require(loop["reference_feasible"] is all(self.values[rid] > 0 for rid in loop["reaction_ids"]), f"Return certificate directional activity {loop['id']}")
            enabled_ids = {rid for rid in self.incident[enzyme] if self.values[rid] > 0}
            enabled_graph = nx.DiGraph()
            enabled_graph.add_nodes_from(states)
            for rid in enabled_ids:
                reaction = self.source[rid]
                enabled_graph.add_edges_from((a, b) for a in set(reaction["reactants"]) & states for b in set(reaction["products"]) & states)
            view = module["parameter_enabled_view"]
            require(set(view["reaction_ids"]) == enabled_ids and len(view["reaction_ids"]) == len(enabled_ids), f"Directional parameter-enabled view {enzyme}")
            require({frozenset(c) for c in view["scc_members"]} == {frozenset(c) for c in nx.strongly_connected_components(enabled_graph)}, f"Parameter-enabled SCCs {enzyme}")
            require(set(view["branch_states"]) == {s for s in states if enabled_graph.out_degree(s) > 1}, f"Parameter-enabled branch states {enzyme}")
            require(set(view["rejoin_states"]) == {s for s in states if enabled_graph.in_degree(s) > 1}, f"Parameter-enabled rejoin states {enzyme}")
            expected_cross = set()
            for state in states:
                for left in incoming[state]:
                    for right in outgoing[state]:
                        if left == right or "DEG_sink" in labels(self.v2[left]["level_c_functional_contexts"]) or "DEG_sink" in labels(self.v2[right]["level_c_functional_contexts"]):
                            continue
                        if self.v2[left]["reaction_family_id"] != self.v2[right]["reaction_family_id"]:
                            expected_cross.add((left, right, state))
            actual_cross = {(item["from_reaction_id"], item["to_reaction_id"], item["state"]) for item in module["cross_family_links"]}
            require(actual_cross == expected_cross and len(actual_cross) == len(module["cross_family_links"]), f"Complete carrier-mediated cross-RFAM connections {enzyme}")
            cross_ids = {rid for left, right, _ in expected_cross for rid in (left, right)}
            for rid, transition in transitions.items():
                require(("CROSS_FAMILY_LINK" in transition["types"]) == (rid in cross_ids), f"Cross-family transition label {rid}")
                before = transition["carrier_before"]
                after = transition["carrier_after"]
                require(("COMPETITIVE_BRANCH" in transition["types"]) == any(state in expected_branches for state in before), f"Competing-exit label {rid}")
                require(("REJOIN" in transition["types"]) == any(state in expected_rejoins for state in after), f"Rejoin label {rid}")
            totals.update({"carrier_transitions": len(transitions), "branch_states": len(branches), "rejoin_states": len(rejoins),
                           "nondegraded_rejoin_states": sum(not s.endswith("_degraded") for s in rejoins),
                           "degraded_sink_convergences": sum(s.endswith("_degraded") for s in rejoins),
                           "strongly_connected_components": len(actual_sccs), "cyclic_sccs": sum(item["cyclic"] for item in module["sccs"]),
                           "return_certificates": len(module["return_loops"]), "cross_family_links": len(actual_cross)})
        required_exits = {f"re{x:010d}" for x in (197, 206, 196, 194)}
        gly = next(item for item in graph["modules"]["GlyRS"]["branches"] if item["state"] == "GlyRS_Gly_ATP_tRNAGlyGCC")
        require(required_exits <= set(gly["outgoing_reaction_ids"]), "GlyRS four competing exits fixture")
        return dict(totals)

    def gate_4(self, graph, rows, markdown):
        coverage = graph["coverage"]
        require(set(coverage["phase_a_reaction_ids"]) == self.scoped and len(coverage["phase_a_reaction_ids"]) == len(self.scoped), "Phase A scope inventory")
        require(set(coverage["out_of_phase_reaction_ids"]) == set(self.source) - self.scoped and len(coverage["out_of_phase_reaction_ids"]) == len(self.source) - len(self.scoped), "Out-of-phase source inventory")
        require(coverage["unassigned_phase_a"] == [], "Every scoped original reaction requires attribution")
        require(coverage["source_unique_reaction_count"] == len(self.source), "Original reaction count cannot count duplicate references")
        require(coverage["unique_reaction_count"] == len(self.scoped), "Phase A unique count cannot count shared reaction occurrences")
        require(coverage["markdown_reaction_reference_count"] == len(re.findall(r"re\d{10}", markdown)), "Actual Markdown reference count")
        occurrences = Counter(rid for module in graph["modules"].values() for path in module["paths"] for rid in set(path["reaction_ids"]))
        shared = sum(number > 1 for number in occurrences.values())
        require(coverage["shared_path_reaction_count"] == shared, "Shared pathway IDs counted uniquely")
        require(set(graph["noncarrier_reactions"]) == self.noncarrier and len(graph["noncarrier_reactions"]) == len(self.noncarrier), "Unprojected free-ligand reactions must remain explicit")
        outside = set(self.source) - self.scoped
        expected_boundaries = set()
        for enzyme, token, charged, adenylate in (("GlyRS", "tRNAGlyGCC", "GlytRNAGlyGCC", "GlyAMP"),
                                                ("MetRS", "tRNAfMetCAU", "MettRNAfMetCAU", "MetAMP")):
            for rid in outside:
                for role, side in (("reactant", "reactants"), ("product", "products")):
                    for participant in (token, charged, adenylate):
                        if participant in self.source[rid][side]:
                            expected_boundaries.add((enzyme, participant, rid, role, self.source[rid][side][participant]))
        actual_boundaries = {(b["module"], b["species"], b["reaction_id"], b["role"], Fraction(b["stoichiometry"])) for b in graph["boundary_links"]}
        require(actual_boundaries == expected_boundaries and len(actual_boundaries) == len(graph["boundary_links"]), "All external tRNA and adenylate boundary incidence must match source")
        require(all(b["evidence"] == "EXTRACTED_SPECIES_INCIDENCE" and b["interpretation_status"] == "HUMAN_REVIEW_REQUIRED" for b in graph["boundary_links"]), "Unresolved global carrier handoffs must retain human-review status")
        require(set().union(*(set(item["level_c"]) for item in graph["reactions"].values())) == set().union(*(labels(row["level_c_functional_contexts"]) for row in self.v2.values())), "All 23 reviewed Level-C labels preserved")
        require(len(set().union(*(labels(row["level_c_functional_contexts"]) for row in self.v2.values()))) == 23, "Reviewed taxonomy must have 23 contexts")
        index = {row["reaction_id"]: row for row in rows}
        require(len(index) == len(rows) and set(index) == self.scoped, "CSV unique Phase A inventory")
        for rid, row in index.items():
            source = self.source[rid]
            require(parse_equation(row["equation"]) == (source["reactants"], source["products"]), f"CSV equation {rid}")
            require(labels(row["level_c"]) == labels(self.v2[rid]["level_c_functional_contexts"]), f"CSV multi-label {rid}")
            require(row["reaction_family"] == self.v2[rid]["reaction_family_id"], f"CSV RFAM {rid}")
            require((row["reverse_reaction_id"] or None) == self.reverse[rid], f"CSV reverse {rid}")
            require(row["reference_activity"] == self.activity(rid), f"CSV reference parameter classification {rid}")
            require(bool(json.loads(row["source_provenance"])), f"CSV provenance {rid}")
            before, after = json.loads(row["carrier_before"]), json.loads(row["carrier_after"])
            if rid in self.noncarrier:
                require(before == [] and after == [], f"Unresolved free-ligand reaction cannot invent enzyme carrier {rid}")
                carrier_states = set()
            else:
                enzyme = next(enzyme for enzyme, rids in self.incident.items() if rid in rids)
                carrier_states = self.carriers[enzyme]
                require(set(before) == set(source["reactants"]) & carrier_states, f"CSV carrier before {rid}")
                require(set(after) == set(source["products"]) & carrier_states, f"CSV carrier after {rid}")
            require(exact_side(json.loads(row["other_reactants"])) == {s: n for s, n in source["reactants"].items() if s not in carrier_states}, f"CSV all required co-reactants {rid}")
            require(exact_side(json.loads(row["other_products"])) == {s: n for s, n in source["products"].items() if s not in carrier_states}, f"CSV all released coproducts {rid}")
            expected_paths = {path["id"] for module in graph["modules"].values() for path in module["paths"] if rid in path["reaction_ids"]}
            path_ids = json.loads(row["path_ids"])
            require(set(path_ids) == expected_paths and len(path_ids) == len(expected_paths), f"CSV shared path membership {rid}")
        gly_scope = {rid for rid in self.scoped if any("Gly" in s for s in set(self.source[rid]["reactants"]) | set(self.source[rid]["products"]))}
        met_scope = self.scoped - gly_scope
        def rename(s):
            return s.replace("GlyRS", "MetRS").replace("tRNAGlyGCC", "tRNAfMetCAU").replace("Gly", "Met")
        met_signatures = {signature(self.source[rid]): rid for rid in met_scope}
        mapping = {}
        for rid in sorted(gly_scope):
            reaction = self.source[rid]
            renamed = {"reactants": {rename(s): n for s, n in reaction["reactants"].items()},
                       "products": {rename(s): n for s, n in reaction["products"].items()},
                       "modifiers": sorted(rename(s) for s in reaction["modifiers"])}
            require(signature(renamed) in met_signatures, f"Independently compared local topology differs at {rid}")
            mapping[rid] = met_signatures[signature(renamed)]
        require(len(set(mapping.values())) == len(met_scope), "Independent local topology comparison must be bijective")
        comparison = {"glyrs_scoped_reactions": len(gly_scope), "metrs_scoped_reactions": len(met_scope),
                      "renamed_local_stoichiometry": "BIJECTIVE", "mapping": mapping,
                      "equal_reference_parameters": sum(self.values[a] == self.values[b] for a, b in mapping.items()),
                      "different_reference_parameters": sum(self.values[a] != self.values[b] for a, b in mapping.items()),
                      "same_zero_pattern": all((self.values[a] == 0) == (self.values[b] == 0) for a, b in mapping.items()),
                      "same_reviewed_level_c": all(labels(self.v2[a]["level_c_functional_contexts"]) == labels(self.v2[b]["level_c_functional_contexts"]) for a, b in mapping.items()),
                      "scope": "LOCAL_RENAMED_CHEMISTRY_ONLY", "kinetic_equivalence_claimed": False}
        return {"source_unique_reactions": len(self.source), "phase_a_unique_reactions": len(self.scoped),
                "out_of_phase_a": len(self.source) - len(self.scoped), "unassigned_phase_a": 0,
                "unprojected_free_ligand_reactions": len(self.noncarrier), "markdown_references": coverage["markdown_reaction_reference_count"],
                "shared_path_reactions": shared, "level_c_contexts_preserved": 23, "phase_b_status": "NOT_ATTEMPTED",
                "external_boundary_incidences": len(expected_boundaries), "independent_glyrs_metrs_comparison": comparison}

    def run(self, graph, rows, markdown):
        gates = []
        names = ("Source Integrity", "Path Continuity", "Branch Completeness", "Reaction Coverage")
        for number, name in enumerate(names, 1):
            try:
                evidence = getattr(self, f"gate_{number}")(graph, rows, markdown)
                gates.append({"gate": number, "name": name, "status": "PASS", "evidence": evidence})
            except (AssertionError, KeyError, ValueError, TypeError, StopIteration) as error:
                gates.append({"gate": number, "name": name, "status": "FAIL", "error": f"{type(error).__name__}: {error}"})
        return {"schema_version": 1, "phase": "A", "scientific_status": "HUMAN_REVIEW_REQUIRED",
                "structural_status": "PASS" if all(gate["status"] == "PASS" for gate in gates) else "FAIL",
                "gates": gates, "independence": "Canonical XML and author ZIP parsed independently; builder not imported"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = Validator().run(*load_artifacts(args.output_dir))
    if args.report:
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["structural_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
