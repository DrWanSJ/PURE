#!/usr/bin/env python3
"""Execute mutations through the independent positive acceptance routines."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path

import verify_phase_b0_witnesses as verify


def fixture(name, numbers, boundary, source):
    """Source-derived test fixtures; mutations never touch canonical files."""
    ids = [f"re{n:010d}" for n in numbers]
    events, edges, handoffs, trace = [], [], [], []
    pool = defaultdict(list)
    marking = defaultdict(Fraction, {s: Fraction(n) for s, n in boundary.items()})
    for s, n in marking.items():
        pool[s].append(["BOUNDARY:" + s, n])
    net = defaultdict(Fraction)
    for i, rid in enumerate(ids):
        eid = f"{name}:E{i+1:02d}"
        r = source["reactions"][rid]
        bindings = []
        for s, n in r["reactants"].items():
            remaining = n
            for token in pool[s]:
                amount = min(token[1], remaining)
                if amount <= 0:
                    continue
                bindings.append({"species_id": s, "amount": str(amount), "origin": token[0]})
                if not token[0].startswith("BOUNDARY:"):
                    edges.append({"source_event": token[0], "target_event": eid, "species_id": s, "amount": str(amount), "evidence": "EXTRACTED"})
                    if s not in verify.RESOURCES:
                        handoffs.append({"source_event": token[0], "source_product": s, "target_event": eid, "target_reactant": s,
                                         "amount": str(amount), "evidence": "EXACT_SOURCE_SPECIES", "confidence": "SOURCE_REACTION_VERIFIED"})
                token[1] -= amount
                remaining -= amount
            marking[s] -= n
            net[s] -= n
        for s, n in r["products"].items():
            marking[s] += n
            net[s] += n
            pool[s].append([eid, n])
        events.append({"event_id": eid, "reaction_id": rid, "occurrence_origin": eid,
                       "inputs": verify.strings(r["reactants"]), "outputs": verify.strings(r["products"]),
                       "equation": verify.equation(r["reactants"], r["products"]), "input_origins": bindings})
        trace.append({"event_id": eid, "marking_after": verify.strings(marking)})
    bs = [{"species_id": s, "amount": str(n), "role": "DECLARED_EXTERNAL_BOUNDARY",
           "source": "B0-1_FORMAL_BOUNDARY_ASSUMPTION", "independently_justified": False,
           "consuming_events": [e["event_id"] for e in events if s in e["inputs"]]} for s, n in sorted(boundary.items())]
    return {"witness_id": name, "reaction_occurrences": events, "source_reaction_ids": sorted(set(ids)),
            "occurrence_counts": dict(Counter(ids)), "ordered_firing_witness": [e["event_id"] for e in events],
            "event_dependencies": edges, "source_species_handoffs": handoffs,
            "inferred_carrier_handoffs": [], "external_boundary_supplies": bs,
            "initial_marking": {s: str(n) for s, n in boundary.items()}, "final_marking": verify.strings(marking), "firing_trace": trace,
            "net_stoichiometry": verify.strings(net), "net_reaction": verify.equation({s: -v for s, v in net.items() if v < 0}, {s: v for s, v in net.items() if v > 0}),
            "internal_species": [], "expected_output_species": [], "catalyst_recovery_claims": [],
            "classification": "STRUCTURAL_HANDOFF_WITNESS", "scientific_status": "PENDING_HUMAN_REVIEW",
            "reference_parameter_support": {r: {"parameter_id": r + "_k1", "value": str(source["parameters"][r]), "status": "REFERENCE_ENABLED" if source["parameters"][r] > 0 else "REFERENCE_DISABLED"} for r in set(ids)}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=verify.OUT / "phase_b0_handoff_witnesses.json")
    p.add_argument("--report", type=Path, default=verify.OUT / "phase_b0_negative_controls.json")
    args = p.parse_args()
    source = verify.parse_sources()
    verify.check_source_integrity(source)
    data = json.loads(args.input.read_text(encoding="utf-8"))
    ws = {w["witness_id"]: w for w in data["witnesses"]}
    controls = []

    def control(cid, description, expected, w=None, mutated_source=None, full_contract=False):
        actual, detail = "ACCEPTED", ""
        petri_status = "NOT_APPLICABLE"
        if w is not None:
            try:
                verify.petri(w, source)
                petri_status = "PASS"
            except verify.Rejection as e:
                petri_status = e.code
        try:
            if mutated_source is not None:
                verify.check_source_integrity(mutated_source)
            else:
                verify.check_witness(w, source)
                if full_contract:
                    mutated_data = deepcopy(data)
                    mutated_data["witnesses"] = [w if x["witness_id"] == w["witness_id"] else x for x in mutated_data["witnesses"]]
                    verify.check_contract(mutated_data, source)
        except verify.Rejection as e:
            actual, detail = e.code, e.detail
        except Exception as e:
            actual, detail = type(e).__name__, str(e)
        controls.append({"id": cid, "mutation_description": description,
                         "source_reaction_ids": w["source_reaction_ids"] if w else ["re0000000414"],
                         "expected_rejection_code": expected, "actual_rejection_code": actual,
                         "rejection_observed": actual == expected, "status": "PASS" if actual == expected else "FAIL",
                         "independent_verifier_evidence": {"routine": "check_source_integrity" if mutated_source else "check_witness + check_contract" if full_contract else "check_witness", "detail": detail, "petri_enabling_status": petri_status},
                         "mutated_fixture": w if w else {"re0000000414_products": verify.strings(mutated_source["reactions"]["re0000000414"]["products"])}})

    f = lambda name, ids, boundary: fixture(name, ids, boundary, source)
    control("N01", "0275 lacks charged Gly-tRNA precursor/source", "MISSING_REQUIRED_INPUT", f("N01", [275], {"EFTu_GTP": 1}))
    control("N02", "0013 lacks ribosomal complex", "MISSING_REQUIRED_INPUT", f("N02", [13], {"EFTu_GTP_GlytRNAGlyGCC": 1}))
    control("N03", "0275 lacks EFTu_GTP", "MISSING_REQUIRED_INPUT", f("N03", [275], {"GlytRNAGlyGCC": 1}))
    control("N04", "0422 lacks MTF_FD", "MISSING_REQUIRED_INPUT", f("N04", [422], {"MettRNAfMetCAU": 1}))
    bad = f("N05", [420, 422], {"MTF": 1, "MettRNAfMetCAU": 2, "MTF_FD": 1})
    bad["source_species_handoffs"].append({"source_event": "N05:E01", "source_product": "MTF_MettRNAfMetCAU", "target_event": "N05:E02", "target_reactant": "MTF_FD", "amount": "1", "evidence": "EXACT_SOURCE_SPECIES", "confidence": "SOURCE_REACTION_VERIFIED"})
    control("N05", "Fireable 0420/0422 with independently supplied MTF_FD falsely claimed as one continuous MTF history", "CARRIER_LINEAGE_MISMATCH", bad)
    control("N06", "0426 supplied wrong precursor complex", "MISSING_REQUIRED_INPUT", f("N06", [426], {"MTF_MettRNAfMetCAU": 1}))
    control("N07", "0449 substitutes unformylated MettRNAfMetCAU", "MISSING_REQUIRED_INPUT", f("N07", [449], {"IF2_GTP": 1, "MettRNAfMetCAU": 1}))
    control("N08", "0449 lacks IF2_GTP", "MISSING_REQUIRED_INPUT", f("N08", [449], {"fMettRNAfMetCAU": 1}))
    bad = f("N09", [136, 161], {"ATP": 2, "GlyRS_Gly": 1, "MetRS_Met": 1})
    bad["source_species_handoffs"].append({"source_event": "N09:E01", "source_product": "ATP", "target_event": "N09:E02", "target_reactant": "ATP", "amount": "1", "evidence": "EXACT_SOURCE_SPECIES", "confidence": "SOURCE_REACTION_VERIFIED"})
    control("N09", "Unrelated GlyRS/MetRS streams joined through shared ATP", "SHARED_RESOURCE_NOT_CARRIER", bad)
    bad = f("N10", [427], {"MTF_THF_fMettRNAfMetCAU": 1})
    bad["reference_parameter_support"]["re0000000427"]["status"] = "REFERENCE_ENABLED"
    control("N10", "Zero author parameter 0427 falsely labeled enabled", "REFERENCE_ACTIVITY_MISMATCH", bad)
    bad = deepcopy(ws["W3"])
    bad["reaction_occurrences"].append(deepcopy(bad["reaction_occurrences"][11]))
    control("N11", "Shared W2 release occurrence counted a second time when composing W3", "DUPLICATE_OCCURRENCE", bad)
    mutated = deepcopy(source)
    mutated["reactions"]["re0000000414"]["products"]["PO4"] = Fraction(1)
    control("N12", "In-memory 0414 coefficient changed from 2 PO4 to 1 PO4", "SOURCE_COEFFICIENT_MISMATCH", mutated_source=mutated)

    for cid, field, description, expected, mutation in [
        ("S01", "net_stoichiometry", "Wrong claimed net ATP coefficient", "NET_STOICHIOMETRY_MISMATCH", lambda w: w["net_stoichiometry"].update(ATP="-2")),
        ("S02", "event_dependencies", "Remove a true producer DAG edge", "EVENT_DAG_MISMATCH", lambda w: w["event_dependencies"].pop()),
        ("S03", "classification", "W1 falsely labeled complete catalytic cycle", "FALSE_CYCLE_CLAIM", lambda w: w.update(classification="COMPLETE_CATALYTIC_CYCLE")),
        ("S04", "input_origins", "Replace actual producer by unavailable boundary token", "TOKEN_PROVENANCE_MISMATCH", lambda w: w["reaction_occurrences"][8]["input_origins"][1].update(origin="BOUNDARY:GlytRNAGlyGCC")),
        ("S05", "catalyst_recovery_claims", "Claim EF-Tu-GTP recovered at W1 endpoint", "CATALYST_NOT_RECOVERED", lambda w: w["catalyst_recovery_claims"].append({"species_id": "EFTu_GTP", "initial": "1", "final": "1"})),
    ]:
        bad = deepcopy(ws["W1"])
        mutation(bad)
        control(cid, description, expected, bad)

    # A globally enabled same-sequence fixture can still route an independent
    # boundary molecule into 0275. The requested source-produced handoff must fail.
    bad = f("W1", [126, 136, 205, 197, 189, 178, 182, 145, 275, 13],
            {"GlyRS": 1, "Gly": 1, "ATP": 1, "tRNAGlyGCC": 1, "EFTu_GTP": 1,
             "elRS70SAGGU0002_fMet": 1, "GlytRNAGlyGCC": 1})
    bad["classification"] = "INTERFACE_ONLY"
    bad["expected_output_species"] = ["elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC"]
    bad["catalyst_recovery_claims"] = [{"species_id": "GlyRS", "initial": "1", "final": "1"}]
    control("S06", "W1 uses independently supplied charged tRNA at 0275 while leaving its GlyRS-generated charged tRNA unused", "REQUIRED_CARRIER_HANDOFF_MISSING", bad, full_contract=True)

    positives = []
    for name, nums, b in [
        ("REORDERED_PRECURSOR", [418, 151, 161, 247, 239, 231, 220, 224, 170, 422, 426, 428, 434], {"MetRS": 1, "Met": 1, "ATP": 1, "tRNAfMetCAU": 1, "MTF": 1, "FD": 1}),
        ("REPEATED_MTF_CYCLE", [418, 422, 426, 428, 434] * 2, {"MTF": 1, "FD": 2, "MettRNAfMetCAU": 2}),
    ]:
        try:
            test = f(name, nums, b)
            result = verify.check_witness(test, source)
            positives.append({"id": name, "status": "PASS", "evidence": result, "fixture": test})
        except Exception as e:
            positives.append({"id": name, "status": "FAIL", "error": str(e)})
    passed = sum(c["status"] == "PASS" for c in controls)
    result = {"required_controls_run": 12, "required_controls_passed": sum(c["status"] == "PASS" for c in controls[:12]),
              "required_controls_failed": sum(c["status"] != "PASS" for c in controls[:12]), "controls_run": len(controls),
              "controls_passed": passed, "controls_failed": len(controls) - passed, "controls": controls, "supplemental_positive_tests": positives,
              "status": "PASS" if passed == len(controls) and all(x["status"] == "PASS" for x in positives) else "FAIL",
              "scientific_status": "PENDING_HUMAN_REVIEW", "canonical_mutation": False}
    args.report.write_bytes((json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    if result["status"] == "FAIL":
        with (verify.OUT / "phase_b0_failure_evidence.jsonl").open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps({"stage": "negative_controls", "report": result}, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "required_controls_run", "required_controls_passed", "required_controls_failed", "controls_run", "controls_passed", "controls_failed")}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
