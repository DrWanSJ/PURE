"""Read immutable PNAS source bytes independently of SBML-engine imports.

Exact MathML stoichiometry, ZIP signature provenance, and author overlays remain
separate. This module writes no canonical input and makes no reduction decision.
"""
from __future__ import annotations

import csv
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict, deque

ROOT = Path(__file__).resolve().parents[2]
NS = "{http://www.sbml.org/sbml/level2/version4}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
MODEL = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
AUTHOR = ROOT / "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
SUBSYSTEMS = ROOT / "references/PNAS2017_Matsuura/raw/SBML_files.zip"
NORMALIZED = ROOT / "models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml"
UNIT_DEFINITIONS = [
    ("CK", "EnergyRegeneration_A", "RFAM_015", ["CP", "ADP", "Cr", "ATP"]),
    ("NDK", "EnergyRegeneration_B", "RFAM_016", ["ATP", "GDP", "ADP", "GTP"]),
    ("MK", "EnergyRegeneration_C", "RFAM_017", ["ATP", "AMP", "ADP"]),
    ("PPiase", "EnergyRegeneration_D", "RFAM_018", ["PPi", "PO4"]),
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def exact(node):
    if node.tag != MATH + "cn":
        raise ValueError("Only literal MathML stoichiometries are permitted")
    if node.get("type") == "rational":
        if len(node) != 1 or node[0].tag != MATH + "sep":
            raise ValueError("Malformed rational MathML")
        return Fraction(int(node.text.strip()), int(node[0].tail.strip()))
    if len(node):
        raise ValueError("Unsupported nonliteral MathML")
    return Fraction(node.text.strip())


def refs(reaction, side):
    result = defaultdict(Fraction)
    for ref in reaction.findall(NS + "listOf" + side + "/" + NS + "speciesReference"):
        math = ref.find(NS + "stoichiometryMath/" + MATH + "math")
        value = exact(math[0]) if math is not None else Fraction(ref.get("stoichiometry", "1"))
        if value <= 0:
            raise ValueError("Nonpositive stoichiometry")
        result[ref.get("species")] += value
    return dict(result)


def signature(reactants, products):
    return tuple(sorted((s, str(v)) for s, v in reactants.items())), tuple(sorted((s, str(v)) for s, v in products.items()))


def formula(node):
    name = node.tag.rsplit("}", 1)[-1]
    if name in ("ci", "cn"):
        return node.text.strip()
    if name == "math":
        return formula(node[0])
    if name == "apply" and node[0].tag == MATH + "times":
        return " * ".join(formula(n) for n in node[1:])
    raise ValueError("Unsupported source kinetic-law shape: " + name)


def parse_model(data, kinetic=True):
    model = ET.fromstring(data).find(NS + "model")
    species = list(model.find(NS + "listOfSpecies"))
    result = []
    for reaction in model.find(NS + "listOfReactions"):
        reactants, products = refs(reaction, "Reactants"), refs(reaction, "Products")
        item = {"id": reaction.get("id"), "reactants": reactants, "products": products}
        if kinetic:
            law = reaction.find(NS + "kineticLaw")
            item["kinetic_law"] = formula(law.find(MATH + "math"))
            item["kinetic_species"] = [n.text.strip() for n in law.findall(".//" + MATH + "ci") if n.text.strip() != "k1"]
            item["structural_k"] = float(law.find(NS + "listOfParameters/" + NS + "parameter").get("value"))
        result.append(item)
    return model, species, result


def csv_rows(raw):
    # Author ZIP uses CR-CR-LF in some member files.
    data = raw.decode("utf-8-sig").replace("\r\r\n", "\n").replace("\r\n", "\n")
    return list(csv.DictReader(io.StringIO(data)))


def json_stoich(side):
    return {s: int(v) if v.denominator == 1 else str(v) for s, v in side.items()}


def build_inventory():
    register = json.loads((ROOT / "references/PNAS2017_Matsuura/provenance/sources.json").read_text(encoding="utf-8"))
    expected = {r["path"]: r["sha256"] for r in register["source_files"]}
    hashes = {}
    for p in (MODEL, AUTHOR, SUBSYSTEMS, NORMALIZED, ROOT / "references/PNAS2017_Matsuura/raw/fMGG_synthesis.xml", ROOT / "docs/reduction/reaction_index.csv", ROOT / "docs/reduction/reaction_level_annotation_v2.csv"):
        rel = p.relative_to(ROOT).as_posix()
        hashes[rel] = digest(p.read_bytes())
        if rel in expected and hashes[rel] != expected[rel]:
            raise ValueError("SOURCE_PROVENANCE_FAILURE: " + rel)
    if hashes[MODEL.relative_to(ROOT).as_posix()] != hashes["references/PNAS2017_Matsuura/raw/fMGG_synthesis.xml"]:
        raise ValueError("Canonical byte copy differs")
    normalization = json.loads(NORMALIZED.with_suffix(".provenance.json").read_text(encoding="utf-8"))
    if hashes[NORMALIZED.relative_to(ROOT).as_posix()] != normalization["normalized_sha256"]:
        raise ValueError("Compatibility source hash differs")
    model, species_elements, raw_reactions = parse_model(MODEL.read_bytes())
    _, normalized_species, normalized_reactions = parse_model(NORMALIZED.read_bytes())
    species_ids = [s.get("id") for s in species_elements]
    if species_ids != [s.get("id") for s in normalized_species] or [(r["id"],signature(r["reactants"],r["products"])) for r in raw_reactions] != [(r["id"],signature(r["reactants"],r["products"])) for r in normalized_reactions]:
        raise ValueError("Constant-stoichiometry compatibility differs")
    reaction_by_signature = {signature(r["reactants"], r["products"]): r for r in raw_reactions}
    if len(reaction_by_signature) != len(raw_reactions):
        raise ValueError("Combined reaction signatures are nonunique")
    provenance = defaultdict(list)
    with zipfile.ZipFile(SUBSYSTEMS) as archive:
        for member in archive.namelist():
            if not member.endswith(".xml"):
                continue
            raw = archive.read(member)
            submodel, _, subreactions = parse_model(raw, kinetic=False)
            for reaction in subreactions:
                sig = signature(reaction["reactants"], reaction["products"])
                if sig not in reaction_by_signature:
                    raise ValueError("Unmatched original subsystem reaction")
                rid = reaction_by_signature[sig]["id"]
                provenance[rid].append({"archive": SUBSYSTEMS.relative_to(ROOT).as_posix(), "member": member, "member_sha256": digest(raw), "file": Path(member).name, "source_model_id": submodel.get("id"), "source_reaction_id": reaction["id"], "mapping_basis": "EXTRACTED_EXACT_STOICHIOMETRIC_SIGNATURE"})
    if set(provenance) != {r["id"] for r in raw_reactions}:
        raise ValueError("Subsystem provenance coverage failure")
    with zipfile.ZipFile(AUTHOR) as archive:
        input_members = {}
        author_rows = {}
        for label, suffix in (("initial", "fMGG_synthesis_initial_values.csv"), ("parameter", "fMGG_synthesis_parameters.csv")):
            members = [m for m in archive.namelist() if m.endswith(suffix)]
            if len(members) != 1:
                raise ValueError("Ambiguous author CSV member")
            member = members[0]
            raw = archive.read(member)
            input_members[label] = {"archive": AUTHOR.relative_to(ROOT).as_posix(), "member": member, "member_sha256": digest(raw)}
            author_rows[label] = csv_rows(raw)
    if [r["Name"] for r in author_rows["initial"]] != species_ids:
        raise ValueError("Author initial species identities/order differ")
    if [r["Name"] for r in author_rows["parameter"][:-1]] != [r["id"] + "_k1" for r in raw_reactions] or author_rows["parameter"][-1]["Name"] != "default":
        raise ValueError("Author parameter identities/order differ")
    initial = {r["Name"]: float(r["Value"]) for r in author_rows["initial"]}
    parameters = {r["Name"][:-3]: float(r["Value"]) for r in author_rows["parameter"][:-1]}
    index = {r["reaction_id"]: r for r in csv_rows((ROOT / "docs/reduction/reaction_index.csv").read_bytes())}
    annotation = {r["reaction_id"]: r for r in csv_rows((ROOT / "docs/reduction/reaction_level_annotation_v2.csv").read_bytes())}
    reactions = []
    for raw in raw_reactions:
        rid = raw["id"]
        source = provenance[rid]
        subsystems = sorted({Path(p["file"]).stem for p in source})
        revsig = signature(raw["products"], raw["reactants"])
        reverse = reaction_by_signature.get(revsig, {}).get("id")
        ir, ar = index[rid], annotation[rid]
        for row, subfield in ((ir,"source_subsystems"), (ar,"level_b_subsystem_candidates")):
            if set(row[subfield].split(";")) != set(subsystems):
                raise ValueError("Subsystem membership mismatch: " + rid)
        if ir["reaction_family_id"] != ar["reaction_family_id"]:
            raise ValueError("Family membership mismatch: " + rid)
        for row in (ir, ar):
            if row["reverse_partner_id"] != (reverse or ""):
                raise ValueError("Reverse partner mismatch: " + rid)
            if signature({s:Fraction(str(v)) for s,v in json.loads(row["reactants_json"]).items()}, {s:Fraction(str(v)) for s,v in json.loads(row["products_json"]).items()}) != signature(raw["reactants"],raw["products"]):
                raise ValueError("Annotation stoichiometry mismatch: " + rid)
        if float(ir["directed_reference_parameter_value"]) != parameters[rid] or float(ar["official_parameter_value"]) != parameters[rid]:
            raise ValueError("Annotation author parameter mismatch: " + rid)
        reactions.append({**raw, "reactants":json_stoich(raw["reactants"]),"products":json_stoich(raw["products"]), "k":parameters[rid], "author_parameter_id":rid+"_k1", "reference_activity":"REFERENCE_ACTIVE" if parameters[rid] != 0 else "REFERENCE_ZERO", "subsystems":subsystems, "family":ir["reaction_family_id"], "reaction_family_id":ir["reaction_family_id"], "level_c":ar["level_c_functional_contexts"].split(";"), "reverse_partner":reverse, "provenance":source})
    units = []
    for name, subsystem, family, boundary in UNIT_DEFINITIONS:
        members = [r for r in reactions if subsystem in r["subsystems"]]
        active = [r for r in members if r["k"] > 0]
        all_species = set().union(*(set(r["reactants"]) | set(r["products"]) for r in members))
        active_species = set().union(*(set(r["reactants"]) | set(r["products"]) for r in active))
        states = sorted(active_species - set(boundary))
        # Live states are established by the connected enzyme-transition graph,
        # not by lexical suffix parsing. The free catalyst is a declared anchor.
        if name not in states:
            raise ValueError("Free enzyme anchor absent")
        resource = {name:{s:0 for s in boundary}}
        edge_evidence = defaultdict(list)
        binding = defaultdict(list)
        catalytic = []
        for r in active:
            er = set(r["reactants"]) & set(states)
            ep = set(r["products"]) & set(states)
            if len(er) != 1 or len(ep) != 1:
                raise ValueError("Active transition lacks exactly one enzyme on each side")
            u, v = next(iter(er)), next(iter(ep))
            if r["reactants"][u] != 1 or r["products"][v] != 1:
                raise ValueError("Enzyme occupancy multiplicity differs")
            increment = {s:r["reactants"].get(s,0)-r["products"].get(s,0) for s in boundary}
            if any(increment.values()):
                binding[u].append((v, increment, r["id"]))
                binding[v].append((u, {s:-x for s,x in increment.items()}, r["id"]))
            else:
                catalytic.append(r["id"])
        todo = deque([name])
        while todo:
            u = todo.popleft()
            for v, change, rid in binding[u]:
                comp = {s:resource[u][s]+change[s] for s in boundary}
                if any(x < 0 for x in comp.values()):
                    raise ValueError("Negative bound-resource composition")
                if v in resource and resource[v] != comp:
                    raise ValueError("Inconsistent binding-based composition")
                if v not in resource:
                    resource[v] = comp
                    edge_evidence[v] = edge_evidence[u]+[rid]
                    todo.append(v)
        if set(resource) != set(states):
            raise ValueError("Binding paths do not establish every enzyme-state composition")
        for r in members:
            expected_family = "RFAM_DEG" if r["family"] == "RFAM_DEG" else family
            if r["family"] != expected_family:
                raise ValueError("Unexpected principal family: " + r["id"])
        units.append({"name":name,"source_subsystem":subsystem,"source_file":subsystem+".xml","reaction_family_id":family,"reaction_ids":[r["id"] for r in members],"active_reaction_ids":[r["id"] for r in active],"zero_reaction_ids":[r["id"] for r in members if r["k"]==0],"enzyme_states":states,"free_enzyme":name,"degraded_states":sorted(all_species-active_species),"boundary_species":boundary,"catalytic_pair":catalytic,"resource_composition":resource,"composition_evidence_paths":dict(edge_evidence),"composition_basis":"INFERRED_FROM_EXACT_BINDING_STOICHIOMETRY_ANCHORED_AT_FREE_CATALYST","enzyme_total_initial":sum(initial[s] for s in states),"all_species":sorted(all_species)})
    return {"schema_version":"energy_cycles_source_inventory_v1","source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"status":"SOURCE_VERIFIED","source_hashes":hashes,"author_input_members":input_members,"species_ids":species_ids,"reactions":reactions,"initial":initial,"structural_initial":{s.get("id"):float(s.get("initialConcentration")) for s in species_elements},"units":units,"SmallMolecules_reaction_ids":[r["id"] for r in reactions if "SmallMolecules" in r["subsystems"]],"compatibility_exact_inventory_equal":True,"units_warning":"No explicit unit definitions; author CSV concentration/time dimensions are unresolved. Seconds label follows the author numerical interval, not independently certified physical units.","source_dimensions":{"species":len(species_ids),"reactions":len(reactions),"subsystems":len({s for r in reactions for s in r["subsystems"]}),"positive_author_initial":sum(v>0 for v in initial.values()),"nonzero_author_parameters":sum(r["k"]>0 for r in reactions)}}


def main():
    inventory = build_inventory()
    output = ROOT / "results/energy_cycles_v1/source_inventory.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(inventory,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"path":str(output),"source_dimensions":inventory["source_dimensions"],"unit_counts":{u["name"]:{"all":len(u["reaction_ids"]),"active":len(u["active_reaction_ids"]),"states":len(u["enzyme_states"])} for u in inventory["units"]}},indent=2))


if __name__ == "__main__":
    main()
