#!/usr/bin/env python3
"""Independent exact SBML/author-CSV and token-origin verifier. Never imports builder."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
from functools import reduce
import hashlib
import io
import json
import operator
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/reduction/pathways"
SBML = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
ZIP = ROOT / "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
PARAM = ROOT / "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv"
V2 = ROOT / "docs/reduction/reaction_level_annotation_v2.csv"
NS = {"s": "http://www.sbml.org/sbml/level2/version4", "m": "http://www.w3.org/1998/Math/MathML"}
PINNED = {SBML: "dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df",
          ZIP: "beb27ebbd314133fbd83f68dcf8ad2ebe08cb16a1adda170b6b7b408ad355b52",
          PARAM: "cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465",
          V2: "ee2f80a3354199a03d3072464cbc301736afad72fba01e4bfcc499c0525f3335"}
RESOURCES = {"ATP", "ADP", "AMP", "GTP", "GDP", "PO4", "PPi", "Gly", "Met", "FD", "THF"}


class Rejection(ValueError):
    def __init__(self, code, detail):
        super().__init__(code + ": " + detail)
        self.code, self.detail = code, detail


def need(ok, code, detail):
    if not ok:
        raise Rejection(code, detail)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(n):
    """Independent recursive evaluator of constant MathML; no float oracle."""
    tag = n.tag.rsplit("}", 1)[-1]
    if tag == "math":
        need(len(n) == 1, "INVALID_MATHML", "single expression required")
        return number(n[0])
    if tag == "cn":
        x = Fraction((n.text or "").strip())
        kind = n.attrib.get("type")
        if kind in {"rational", "e-notation"}:
            need(len(n) == 1 and n[0].tag.rsplit("}", 1)[-1] == "sep", "INVALID_MATHML", "separator required")
            y = Fraction(n[0].tail.strip())
            if kind == "rational":
                return x / y
            need(y.denominator == 1, "INVALID_MATHML", "integer exponent required")
            return x * (Fraction(10) ** y.numerator)
        need(len(n) == 0, "INVALID_MATHML", "unexpected child")
        return x
    if tag == "apply":
        op = n[0].tag.rsplit("}", 1)[-1]
        terms = tuple(map(number, list(n)[1:]))
        if op == "plus":
            return sum(terms, Fraction(0))
        if op == "times":
            return reduce(operator.mul, terms, Fraction(1))
        if op == "minus" and len(terms) == 1:
            return -terms[0]
        if op == "minus" and len(terms) == 2:
            return terms[0] - terms[1]
        if op == "divide" and len(terms) == 2:
            return terms[0] / terms[1]
        if op == "power" and len(terms) == 2 and terms[1].denominator == 1:
            return terms[0] ** terms[1].numerator
    raise Rejection("INVALID_MATHML", tag)


def parse_sources():
    model = ET.parse(SBML).getroot().find("s:model", NS)
    species = {n.attrib["id"] for n in model.findall("s:listOfSpecies/s:species", NS)}
    rx, arcs = {}, 0
    for n in model.findall("s:listOfReactions/s:reaction", NS):
        rid = n.attrib["id"]
        need(rid not in rx, "DUPLICATE_SOURCE_ID", rid)
        sides = {}
        for key, tag in (("reactants", "Reactants"), ("products", "Products")):
            side = defaultdict(Fraction)
            for ref in n.findall(f"s:listOf{tag}/s:speciesReference", NS):
                math = ref.find("s:stoichiometryMath/m:math", NS)
                value = number(math) if math is not None else Fraction(ref.attrib.get("stoichiometry", "1"))
                need(value > 0 and ref.attrib["species"] in species, "INVALID_SOURCE_ARC", rid)
                side[ref.attrib["species"]] += value
                arcs += 1
            sides[key] = dict(side)
        rx[rid] = sides
    raw = PARAM.read_bytes()
    with ZIP.open("rb") as stream, zipfile.ZipFile(stream) as archive:
        members = [n for n in archive.namelist() if n.endswith("fMGG_synthesis_parameters.csv")]
        need(len(members) == 1, "AUTHOR_MEMBER_MISMATCH", str(members))
        need(archive.read(members[0]) == raw, "AUTHOR_PARAMETER_COPY_MISMATCH", members[0])
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig").replace("\r\r\n", "\n"))))
    need(len({r["Name"] for r in rows}) == len(rows), "DUPLICATE_PARAMETER", "author CSV")
    parameters = {r["Name"]: Fraction(r["Value"]) for r in rows}
    with V2.open(encoding="utf-8-sig", newline="") as stream:
        annotations = {r["reaction_id"]: r for r in csv.DictReader(stream)}
    need(set(annotations) == set(rx), "ANNOTATION_ID_MISMATCH", "v2")
    for rid in rx:
        need(parameters[rid + "_k1"] == Fraction(annotations[rid]["official_parameter_value"]), "PARAMETER_ANNOTATION_MISMATCH", rid)
        need(parameters[rid + "_k1"] >= 0, "NEGATIVE_PARAMETER", rid)
    return {"species": species, "reactions": rx, "parameters": {r: parameters[r + "_k1"] for r in rx}, "arcs": arcs}


def check_source_integrity(source):
    for path, expected in PINNED.items():
        need(digest(path) == expected, "SOURCE_HASH_MISMATCH", str(path))
    rx = source["reactions"]
    need(len(source["species"]) == 241 and len(rx) == 968 and source["arcs"] == 3854, "SOURCE_COUNT_MISMATCH", "241/968/3854")
    need(sum(v == 0 for v in source["parameters"].values()) == 485, "ZERO_PARAMETER_COUNT_MISMATCH", "485 required")
    need(rx["re0000000414"]["products"].get("PO4") == 2, "SOURCE_COEFFICIENT_MISMATCH", "re0000000414 requires 2 PO4")
    return {"species": 241, "directed_reactions": 968, "weighted_petri_arcs": 3854, "zero_author_parameters": 485,
            "re0000000414_PO4": "2", "hashes": {p.relative_to(ROOT).as_posix(): digest(p) for p in PINNED},
            "approved_hash_authority": "Published Phase A protocol/graph, independently pinned in verifier"}


def fractions(v):
    need(all(isinstance(n, str) for n in v.values()), "NONEXACT_COEFFICIENT", "coefficients must be exact strings")
    return {s: Fraction(n) for s, n in v.items()}


def strings(v):
    return {s: str(n) for s, n in sorted(v.items()) if n}


def equation(a, b):
    def render(v):
        return " + ".join(("" if n == 1 else str(n) + " ") + s for s, n in sorted(v.items())) or "0"
    return render(a) + " -> " + render(b)


def petri(w, source):
    marking = defaultdict(Fraction, fractions(w["initial_marking"]))
    rx = source["reactions"]
    trace = []
    for e in w["reaction_occurrences"]:
        r = rx[e["reaction_id"]]
        missing = {s: str(v - marking[s]) for s, v in r["reactants"].items() if marking[s] < v}
        need(not missing, "MISSING_REQUIRED_INPUT", e["event_id"] + " " + json.dumps(missing, sort_keys=True))
        for s, n in r["reactants"].items():
            marking[s] -= n
        for s, n in r["products"].items():
            marking[s] += n
        trace.append({"event_id": e["event_id"], "marking_after": strings(marking)})
    return dict(marking), trace


def check_witness(w, source):
    events = w["reaction_occurrences"]
    need(events, "EMPTY_WITNESS", w["witness_id"])
    ids = [e["event_id"] for e in events]
    need(len(ids) == len(set(ids)), "DUPLICATE_OCCURRENCE", "same actual event counted twice")
    origins = [e["occurrence_origin"] for e in events]
    need(len(origins) == len(set(origins)), "DUPLICATE_OCCURRENCE", "shared origin counted twice")
    need(w["ordered_firing_witness"] == ids, "FIRING_ORDER_MISMATCH", w["witness_id"])
    reactions = source["reactions"]
    net = defaultdict(Fraction)
    for e in events:
        rid = e["reaction_id"]
        need(rid in reactions, "UNKNOWN_REACTION", rid)
        r = reactions[rid]
        need(fractions(e["inputs"]) == r["reactants"] and fractions(e["outputs"]) == r["products"], "SOURCE_REACTION_MISMATCH", rid)
        need(e["equation"] == equation(r["reactants"], r["products"]), "SOURCE_EQUATION_MISMATCH", rid)
        for s, n in r["products"].items():
            net[s] += n
        for s, n in r["reactants"].items():
            net[s] -= n
    boundary = w["external_boundary_supplies"]
    need(len(boundary) == len({s["species_id"] for s in boundary}), "DUPLICATE_BOUNDARY", w["witness_id"])
    initial = {}
    for b in boundary:
        s, n = b["species_id"], Fraction(b["amount"])
        need(s in source["species"] and n > 0, "INVALID_BOUNDARY", s)
        need(b["independently_justified"] is False and b["source"] == "B0-1_FORMAL_BOUNDARY_ASSUMPTION", "UNSUPPORTED_BOUNDARY_JUSTIFICATION", s)
        need(b["consuming_events"] == [e["event_id"] for e in events if s in e["inputs"]], "BOUNDARY_CONSUMER_MISMATCH", s)
        initial[s] = n
    need(initial == fractions(w["initial_marking"]), "BOUNDARY_MARKING_MISMATCH", w["witness_id"])
    final, trace = petri(w, source)
    # Deliberately separate global enabling from the claimed carrier dependency.
    event_map = {e["event_id"]: e for e in events}
    for h in w["source_species_handoffs"]:
        s, t = h["source_product"], h["target_reactant"]
        need(s not in RESOURCES and t not in RESOURCES, "SHARED_RESOURCE_NOT_CARRIER", s)
        need(s == t and h["source_event"] in event_map and h["target_event"] in event_map, "CARRIER_LINEAGE_MISMATCH", str(h))
        a, b = event_map[h["source_event"]], event_map[h["target_event"]]
        need(s in a["outputs"] and t in b["inputs"] and ids.index(a["event_id"]) < ids.index(b["event_id"]), "CARRIER_LINEAGE_MISMATCH", str(h))
    # Validate consumption from each individual producer, not just total marking.
    balances = defaultdict(Fraction, {("BOUNDARY:" + s, s): n for s, n in initial.items()})
    derived_edges = []
    for e in events:
        allocated = defaultdict(Fraction)
        for binding in e["input_origins"]:
            s, origin, n = binding["species_id"], binding["origin"], Fraction(binding["amount"])
            need(n > 0 and balances[origin, s] >= n, "TOKEN_PROVENANCE_MISMATCH", f"{origin} -> {e['event_id']} {s}")
            allocated[s] += n
            balances[origin, s] -= n
            if not origin.startswith("BOUNDARY:"):
                derived_edges.append({"source_event": origin, "target_event": e["event_id"], "species_id": s, "amount": str(n), "evidence": "EXTRACTED"})
        need(dict(allocated) == reactions[e["reaction_id"]]["reactants"], "INPUT_ORIGIN_INVENTORY_MISMATCH", e["event_id"])
        for s, n in reactions[e["reaction_id"]]["products"].items():
            balances[e["event_id"], s] += n
    need(w["event_dependencies"] == derived_edges, "EVENT_DAG_MISMATCH", "edges must follow token origins")
    expected_h = [{"source_event": d["source_event"], "source_product": d["species_id"], "target_event": d["target_event"],
                   "target_reactant": d["species_id"], "amount": d["amount"], "evidence": "EXACT_SOURCE_SPECIES", "confidence": "SOURCE_REACTION_VERIFIED"}
                  for d in derived_edges if d["species_id"] not in RESOURCES]
    need(w["source_species_handoffs"] == expected_h, "CARRIER_LINEAGE_MISMATCH", "complete exact lineage must match allocated producer tokens")
    need(w["net_stoichiometry"] == strings(net), "NET_STOICHIOMETRY_MISMATCH", w["witness_id"])
    need(w["net_reaction"] == equation({s: -v for s, v in net.items() if v < 0}, {s: v for s, v in net.items() if v > 0}), "NET_EQUATION_MISMATCH", w["witness_id"])
    need(w["occurrence_counts"] == dict(Counter(e["reaction_id"] for e in events)), "OCCURRENCE_COUNT_MISMATCH", w["witness_id"])
    need(w["source_reaction_ids"] == sorted({e["reaction_id"] for e in events}), "SOURCE_ID_SET_MISMATCH", w["witness_id"])
    need(w["final_marking"] == strings(final) and w["firing_trace"] == trace, "MARKING_TRACE_MISMATCH", w["witness_id"])
    need(all(final.get(s, 0) == initial.get(s, 0) + net[s] for s in set(initial) | set(net) | set(final)), "BOUNDARY_BALANCE_MISMATCH", w["witness_id"])
    for s in w["internal_species"]:
        need(s in source["species"] and net.get(s, 0) == 0, "INTERNAL_CANCELLATION_FAILURE", s)
    for c in w["catalyst_recovery_claims"]:
        s = c["species_id"]
        need(initial.get(s, 0) > 0 and final.get(s, 0) == initial[s] and net.get(s, 0) == 0,
             "CATALYST_NOT_RECOVERED", s)
        need(Fraction(c["initial"]) == initial[s] and Fraction(c["final"]) == final[s], "CATALYST_CLAIM_MISMATCH", s)
    for s in w["expected_output_species"]:
        need(net.get(s, 0) > 0 and final.get(s, 0) > 0, "TARGET_NOT_PRODUCED", s)
    if w["classification"] == "COMPLETE_CATALYTIC_CYCLE":
        need(w["catalyst_recovery_claims"] and w["witness_id"] not in ("W1", "W3"), "FALSE_CYCLE_CLAIM", w["witness_id"])
    for rid, support in w["reference_parameter_support"].items():
        k = source["parameters"][rid]
        expected = "REFERENCE_ENABLED" if k > 0 else "REFERENCE_DISABLED"
        need(support["parameter_id"] == rid + "_k1" and Fraction(support["value"]) == k and support["status"] == expected, "REFERENCE_ACTIVITY_MISMATCH", rid)
    need(set(w["reference_parameter_support"]) == set(w["source_reaction_ids"]), "PARAMETER_SUPPORT_MISSING", w["witness_id"])
    need(w["scientific_status"] == "PENDING_HUMAN_REVIEW", "SCIENTIFIC_PROMOTION", w["witness_id"])
    for h in w["inferred_carrier_handoffs"]:
        need(h["evidence"] == "INFERRED" and h["status"] == "HUMAN_REVIEW_REQUIRED" and h["confidence"] == "PROVISIONAL", "IDENTITY_PROMOTION", w["witness_id"])
        e = event_map[h["source_event"]]
        need(h["reaction_id"] == e["reaction_id"] and h["before"] == list(e["inputs"]) and h["after"] == list(e["outputs"]), "INFERRED_PROJECTION_MISMATCH", w["witness_id"])
    return {"status": "PASS", "source_reaction_status": "SOURCE_REACTION_VERIFIED", "structural_status": "STRUCTURAL_HANDOFF_WITNESS",
            "classification": w["classification"], "events_checked": len(events), "exact_net": strings(net), "petri_status": "PASS",
            "carrier_lineage_status": "EXACT_PRODUCER_TOKEN_FLOW_VERIFIED", "composite_identity_status": "HUMAN_REVIEW_REQUIRED",
            "event_dag_edges": len(derived_edges), "catalysts_recovered": [c["species_id"] for c in w["catalyst_recovery_claims"]],
            "reference_enabled_directions": sum(source["parameters"][r] > 0 for r in w["source_reaction_ids"]),
            "reference_disabled_directions": sum(source["parameters"][r] == 0 for r in w["source_reaction_ids"]),
            "resource_net": {s: strings(net).get(s, "0") for s in sorted(RESOURCES | {"tRNAGlyGCC", "GlytRNAGlyGCC", "tRNAfMetCAU", "MettRNAfMetCAU", "fMettRNAfMetCAU"})}}


def check_contract(data, source):
    """Independent scientific scope targets and expectation nets, not builder claims."""
    ws = {w["witness_id"]: w for w in data["witnesses"]}
    need(set(ws) == {"W1", "W2", "W3", "W2-MTF", "W2-ALT"}, "WITNESS_SCOPE_MISMATCH", str(set(ws)))
    def ids(ns):
        return [f"re{n:010d}" for n in ns]
    gly = ids((126, 136, 205, 197, 189, 178, 182, 145))
    met = ids((151, 161, 247, 239, 231, 220, 224, 170))
    mtf = ids((418, 422, 426, 428, 434))
    targets = {"W1": gly + ids((275, 13)), "W2": met + mtf, "W3": met + mtf + ids((449,)),
               "W2-MTF": mtf, "W2-ALT": met + ids((420, 424, 426, 428, 434))}
    w2net = {"Met": "-1", "ATP": "-1", "tRNAfMetCAU": "-1", "FD": "-1", "fMettRNAfMetCAU": "1", "AMP": "1", "PPi": "1", "THF": "1"}
    expected = {"W1": {"Gly": "-1", "ATP": "-1", "tRNAGlyGCC": "-1", "EFTu_GTP": "-1", "elRS70SAGGU0002_fMet": "-1", "elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC": "1", "AMP": "1", "PPi": "1"},
                "W2": w2net, "W2-ALT": w2net, "W2-MTF": {"FD": "-1", "MettRNAfMetCAU": "-1", "THF": "1", "fMettRNAfMetCAU": "1"}}
    expected["W3"] = {k: v for k, v in w2net.items() if k != "fMettRNAfMetCAU"}
    expected["W3"].update(IF2_GTP="-1", IF2_GTP_fMettRNAfMetCAU="1")
    required_links = {"W1": [(182, 275, "GlytRNAGlyGCC"), (275, 13, "EFTu_GTP_GlytRNAGlyGCC")],
                      "W2": [(224, 422, "MettRNAfMetCAU"), (418, 422, "MTF_FD")],
                      "W3": [(224, 422, "MettRNAfMetCAU"), (418, 422, "MTF_FD"), (428, 449, "fMettRNAfMetCAU")],
                      "W2-ALT": [(224, 420, "MettRNAfMetCAU"), (420, 424, "MTF_MettRNAfMetCAU")],
                      "W2-MTF": [(418, 422, "MTF_FD")]}
    bmet = {"MetRS", "Met", "ATP", "tRNAfMetCAU", "MTF", "FD"}
    boundaries = {"W1": {"GlyRS", "Gly", "ATP", "tRNAGlyGCC", "EFTu_GTP", "elRS70SAGGU0002_fMet"},
                  "W2": bmet, "W3": bmet | {"IF2_GTP"}, "W2-ALT": bmet, "W2-MTF": {"MTF", "FD", "MettRNAfMetCAU"}}
    catalysts = {"W1": {"GlyRS"}, "W2": {"MetRS", "MTF"}, "W3": {"MetRS", "MTF"}, "W2-ALT": {"MetRS", "MTF"}, "W2-MTF": {"MTF"}}
    products = {"W1": ["elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC"], "W2": ["fMettRNAfMetCAU"],
                "W3": ["IF2_GTP_fMettRNAfMetCAU"], "W2-ALT": ["fMettRNAfMetCAU"], "W2-MTF": ["fMettRNAfMetCAU"]}
    for wid, target in targets.items():
        w = ws[wid]
        need([e["reaction_id"] for e in w["reaction_occurrences"]] == target, "TARGET_SEQUENCE_MISMATCH", wid)
        event_by_reaction = {e["reaction_id"]: e["event_id"] for e in w["reaction_occurrences"]}
        for a, b, s in required_links[wid]:
            source_event, target_event = event_by_reaction[f"re{a:010d}"], event_by_reaction[f"re{b:010d}"]
            need(any(h["source_event"] == source_event and h["target_event"] == target_event and h["source_product"] == h["target_reactant"] == s and Fraction(h["amount"]) == 1 for h in w["source_species_handoffs"]), "REQUIRED_CARRIER_HANDOFF_MISSING", f"{wid}: {a} -> {b} via {s}")
        need(fractions(w["initial_marking"]) == {s: Fraction(1) for s in boundaries[wid]}, "BOUNDARY_SUPPLY_SCOPE_MISMATCH", wid)
        need({c["species_id"] for c in w["catalyst_recovery_claims"]} == catalysts[wid], "CATALYST_RECOVERY_EVIDENCE_MISSING", wid)
        need(w["expected_output_species"] == products[wid], "TARGET_CLAIM_MISMATCH", wid)
        need(w["net_stoichiometry"] == expected[wid], "EXPECTED_SOURCE_NET_MISMATCH", wid)
        if wid in ("W1", "W3"):
            need(w["classification"] == "INTERFACE_ONLY", "FALSE_CYCLE_CLAIM", wid)
        else:
            need(w["classification"] == ("COMPLETE_CATALYTIC_CYCLE" if wid == "W2-MTF" else "STRUCTURAL_HANDOFF_WITNESS"), "CLASSIFICATION_MISMATCH", wid)
    for wid in ("W2", "W3"):
        w = ws[wid]
        prepare = next(e for e in w["reaction_occurrences"] if e["reaction_id"] == "re0000000418")
        join = next(e for e in w["reaction_occurrences"] if e["reaction_id"] == "re0000000422")
        need(not any(d["target_event"] == prepare["event_id"] for d in w["event_dependencies"]), "SERIALIZED_INDEPENDENT_BRANCH", wid)
        need({b["species_id"] for b in join["input_origins"] if not b["origin"].startswith("BOUNDARY:")} == {"MTF_FD", "MettRNAfMetCAU"}, "MULTI_PRECURSOR_JOIN_MISMATCH", wid)
        need(w["independent_precursor_branches"] == [[e["event_id"] for e in w["reaction_occurrences"] if e["reaction_id"] in met], [prepare["event_id"]]], "PRECURSOR_BRANCH_RECORD_MISMATCH", wid)
    need(source["reactions"]["re0000000422"]["products"] == source["reactions"]["re0000000424"]["products"] == {"MTF_FD_MettRNAfMetCAU": Fraction(1)}, "FALSE_REJOIN", "MTF entry alternatives")
    need(data["rejoin"] == {"primary_reaction": "re0000000422", "alternative_reaction": "re0000000424", "species_id": "MTF_FD_MettRNAfMetCAU", "evidence": "EXTRACTED"}, "REJOIN_RECORD_MISMATCH", "MTF")
    need(data["phase_b1_authorized"] is False and data["scientific_status"] == "PENDING_HUMAN_REVIEW", "SCOPE_PROMOTION", "B0 only")
    need(data["optional_upstream"]["included_in_core_W3"] is False and "re0000000445" not in ws["W3"]["source_reaction_ids"], "OPTIONAL_PRECURSOR_SILENTLY_ADDED", "0445")
    need(data["optional_upstream"]["equation"] == equation(source["reactions"]["re0000000445"]["reactants"], source["reactions"]["re0000000445"]["products"]), "SOURCE_EQUATION_MISMATCH", "optional 0445")
    # Independently require every original entrance/exit at the finite source anchors.
    selected = set().union(*(set(w["source_reaction_ids"]) for w in ws.values()))
    anchors = set().union(*(set(source["reactions"][r][side]) for r in selected for side in ("reactants", "products")))
    local_anchors = {s for s in anchors if s.startswith(("GlyRS", "MetRS", "MTF")) or s in
                     {"GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU", "EFTu_GTP_GlytRNAGlyGCC", "IF2_GTP_fMettRNAfMetCAU"}}
    appendix_ids = {rid for rid, q in source["reactions"].items() if (set(q["reactants"]) | set(q["products"])) & local_anchors}
    appendix_ids |= selected | {"re0000000414", "re0000000445", "re0000000446", "re0000000450"}
    need(set(data["reactions"]) == appendix_ids, "INCIDENCE_APPENDIX_INCOMPLETE", "all anchored exits/entrances required")
    for w in ws.values():
        projections = []
        for e in w["reaction_occurrences"]:
            for carrier in ("GlyRS", "tRNAGlyGCC", "MetRS", "tRNAfMetCAU", "EFTu", "MTF", "IF2", "elRS70SAGGU0002"):
                before = sorted(s for s in source["reactions"][e["reaction_id"]]["reactants"] if carrier in s)
                after = sorted(s for s in source["reactions"][e["reaction_id"]]["products"] if carrier in s)
                if before or after:
                    projections.append((e["event_id"], carrier, before, after))
        need([(h["event_id"], h["carrier_label"], h["before_species"], h["after_species"]) for h in w["provisional_carrier_streams"]] == projections, "CARRIER_PROJECTION_MISMATCH", w["witness_id"])
        need(all(h["evidence"] == "INFERRED" and h["status"] == "HUMAN_REVIEW_REQUIRED" for h in w["provisional_carrier_streams"]), "IDENTITY_PROMOTION", w["witness_id"])
    # Validate full source incidence appendix and directional metadata against fresh sources.
    for rid, r in data["reactions"].items():
        q = source["reactions"][rid]
        need(fractions(r["reactants"]) == q["reactants"] and fractions(r["products"]) == q["products"] and r["equation"] == equation(q["reactants"], q["products"]), "SOURCE_REACTION_MISMATCH", rid)
        k = source["parameters"][rid]
        need(Fraction(r["reference_parameter"]) == k and r["reference_activity"] == ("REFERENCE_ENABLED" if k > 0 else "REFERENCE_DISABLED"), "REFERENCE_ACTIVITY_MISMATCH", rid)
        inverse = sorted(t for t, v in source["reactions"].items() if v["reactants"] == q["products"] and v["products"] == q["reactants"])
        need(r["reverse_reaction_ids"] == inverse, "REVERSE_PAIR_MISMATCH", rid)
    for p in data["source_provenance"]:
        need(digest(ROOT / p["path"]) == p["sha256"], "SOURCE_HASH_MISMATCH", p["path"])
    review = json.loads((OUT / "phase_b0_b0_2_review_record.json").read_text(encoding="utf-8"))
    need(review["authority"] == "USER_SUPPLIED_RESEARCHER_REVIEW" and review["phase_b1_authorized"] is False and review["commit_push_authorized"] is False,
         "REVIEW_AUTHORITY_OR_SCOPE_MISMATCH", "B0-2 bounded user decision")
    need(data["researcher_review"]["scientific_status"] == review["scientific_status"] and data["researcher_review"]["formal_signoff_status"] == review["formal_signoff_status"],
         "REVIEW_RECORD_MISMATCH", "separate human decision record")
    annotation = data["biochemical_identity_annotations"]["FD"]
    need(annotation["identity"] == "10-formyltetrahydrofolate" and annotation["doi"] == "10.1073/pnas.1615351114" and annotation["citation"] == review["sources"]["matsuura"]["url"],
         "BIOCHEMICAL_CITATION_MISMATCH", "published FD definition; no new composition certificate")
    need(digest(ROOT / review["sources"]["matsuura"]["frozen_pdf_path"]) == review["sources"]["matsuura"]["frozen_pdf_sha256"], "SOURCE_HASH_MISMATCH", "frozen Matsuura main PDF")
    need(digest(ROOT / review["b0_1_snapshot"]["path"]) == review["b0_1_snapshot"]["sha256"], "SOURCE_HASH_MISMATCH", "pre-revision B0-1 snapshot")
    pair = data["if2_reference_directions"]
    need(set(pair) == {"re0000000449", "re0000000450"}, "IF2_DIRECTION_MISSING", "both directions required")
    for rid, record in pair.items():
        r = source["reactions"][rid]
        need(source["parameters"][rid] == Fraction(40) and Fraction(record["parameter"]) == source["parameters"][rid] and record["status"] == "REFERENCE_ENABLED" and record["equation"] == equation(r["reactants"], r["products"]), "IF2_REFERENCE_DIRECTION_MISMATCH", rid)
    pool = data["shared_substrate_competition"]
    need(pool["species_id"] == "MettRNAfMetCAU" and set(pool["competing_reaction_ids"]) == {"re0000000420", "re0000000422", "re0000000288"} and pool["pool_semantics"] == "ONE_SHARED_ORIGINAL_SOURCE_SPECIES_POOL" and pool["phase_b1_implementation_authorized"] is False,
         "SHARED_POOL_CONSTRAINT_MISMATCH", "MTF/EF-Tu exits")
    need(all(source["reactions"][r]["reactants"].get(pool["species_id"]) == Fraction(1) for r in pool["competing_reaction_ids"]), "SHARED_POOL_SOURCE_MISMATCH", "one exact common source species")
    return {"expectation_nets_checked": len(targets), "independent_precursor_joins_checked": 2, "alternative_rejoin_status": "PASS", "appendix_equations_checked": len(data["reactions"]),
            "fd_identity_context": "ORIGINAL_ARTICLE_CITATION_RECORDED_NOT_A_GLOBAL_COMPOSITION_CERTIFICATE", "if2_reference_enabled_directions": 2,
            "shared_met_trna_source_consumers": sorted(pool["competing_reaction_ids"]), "researcher_review_authority": review["authority"]}


def preservation():
    baseline = json.loads((OUT / "phase_b0_source_baseline.json").read_text(encoding="utf-8"))
    changed = [n for n, h in baseline["existing_tracked_files"].items() if not (ROOT / n).is_file() or digest(ROOT / n) != h]
    need(not changed, "PROTECTED_FILE_CHANGED", json.dumps(changed))
    return {"status": "PASS", "existing_tracked_files_unchanged": len(baseline["existing_tracked_files"]), "starting_head": baseline["starting_head"], "changed_files": changed}


def validate(data):
    source = parse_sources()
    result = {"phase": "B0-1", "scientific_status": "PENDING_HUMAN_REVIEW", "phase_b1_authorized": False,
              "source_integrity": check_source_integrity(source), "witnesses": {}}
    for w in data["witnesses"]:
        result["witnesses"][w["witness_id"]] = check_witness(w, source)
    result["contract"] = check_contract(data, source)
    result["preservation"] = preservation()
    result["structural_verification_status"] = "PASS"
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=OUT / "phase_b0_handoff_witnesses.json")
    p.add_argument("--report", type=Path, default=OUT / "phase_b0_independent_verification.json")
    args = p.parse_args()
    try:
        result = validate(json.loads(args.input.read_text(encoding="utf-8")))
    except Exception as e:
        result = {"structural_verification_status": "FAIL", "scientific_status": "PENDING_HUMAN_REVIEW", "phase_b1_authorized": False,
                  "error": str(e), "rejection_code": getattr(e, "code", type(e).__name__)}
        with (OUT / "phase_b0_failure_evidence.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps({"stage": "independent_verification", "report": result}, sort_keys=True) + "\n")
    args.report.write_bytes((json.dumps(result, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"status": result["structural_verification_status"], "witness_events": {k: v["events_checked"] for k, v in result.get("witnesses", {}).items()}, "error": result.get("error")}))
    return 0 if result["structural_verification_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
