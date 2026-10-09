#!/usr/bin/env python3
"""Finite B0-1 witnesses, extracted from immutable SBML; standard library only."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/reduction/pathways"
SOURCE = "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
ARCHIVE = "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
CSV = "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv"
V2 = "docs/reduction/reaction_level_annotation_v2.csv"
SB = "{http://www.sbml.org/sbml/level2/version4}"
MM = "{http://www.w3.org/1998/Math/MathML}"


def exact(values):
    return {s: str(v) for s, v in sorted(values.items()) if v}


def constant(node):
    tag = node.tag.split("}")[-1]
    if tag == "math" and len(node) == 1:
        return constant(node[0])
    if tag == "cn":
        n = Fraction((node.text or "").strip())
        if node.get("type") in ("rational", "e-notation"):
            if len(node) != 1 or node[0].tag != MM + "sep":
                raise ValueError("Invalid constant separator")
            t = Fraction(node[0].tail.strip())
            return n / t if node.get("type") == "rational" else n * Fraction(10) ** int(t)
        if not len(node):
            return n
    if tag == "apply":
        op = node[0].tag.split("}")[-1]
        a = [constant(n) for n in node[1:]]
        if op == "plus":
            return sum(a, Fraction())
        if op == "times":
            n = Fraction(1)
            for v in a:
                n *= v
            return n
        if op == "minus" and len(a) in (1, 2):
            return -a[0] if len(a) == 1 else a[0] - a[1]
        if op == "divide" and len(a) == 2:
            return a[0] / a[1]
        if op == "power" and len(a) == 2 and a[1].denominator == 1:
            return a[0] ** int(a[1])
    raise ValueError("Unsupported constant MathML")


def equation(a, b):
    def side(v):
        return " + ".join(("" if Fraction(n) == 1 else str(n) + " ") + s for s, n in sorted(v.items())) or "0"
    return side(a) + " -> " + side(b)


def provenance(path, authority):
    return {"path": path, "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
            "authority": authority, "evidence": "EXTRACTED", "freshness": "HASH_CHECKED_AT_BUILD"}


def read_source():
    model = ET.parse(ROOT / SOURCE).getroot().find(SB + "model")
    with zipfile.ZipFile(ROOT / ARCHIVE) as z:
        members = [n for n in z.namelist() if n.endswith("fMGG_synthesis_parameters.csv")]
        if len(members) != 1:
            raise ValueError("Missing unique author CSV")
        raw = z.read(members[0])
    if raw != (ROOT / CSV).read_bytes():
        raise ValueError("Author archive/CSV mismatch")
    values = {r["Name"]: r["Value"] for r in csv.DictReader(io.StringIO(raw.decode("utf-8-sig").replace("\r\r\n", "\n")))}
    with (ROOT / V2).open(encoding="utf-8-sig", newline="") as f:
        annotations = {r["reaction_id"]: r for r in csv.DictReader(f)}
    reactions = {}
    for node in model.findall(SB + "listOfReactions/" + SB + "reaction"):
        r = {}
        rid = node.attrib["id"]
        for name, key in (("Reactants", "reactants"), ("Products", "products")):
            side = defaultdict(Fraction)
            for ref in node.findall(SB + "listOf" + name + "/" + SB + "speciesReference"):
                math = ref.find(SB + "stoichiometryMath/" + MM + "math")
                v = constant(math) if math is not None else Fraction(ref.get("stoichiometry", "1"))
                if v <= 0:
                    raise ValueError("Nonpositive coefficient " + rid)
                side[ref.attrib["species"]] += v
            r[key] = exact(side)
        r.update(equation=equation(r["reactants"], r["products"]),
                 reference_parameter=values[rid + "_k1"],
                 reference_activity="REFERENCE_ENABLED" if Fraction(values[rid + "_k1"]) > 0 else "REFERENCE_DISABLED",
                 level_c=annotations[rid]["level_c_functional_contexts"],
                 identity_evidence="EXACT_SOURCE_SPECIES_TRANSITION_NOT_COMPOSITION_CERTIFICATE",
                 source_provenance={"path": SOURCE, "reaction_id": rid, "evidence": "EXTRACTED"})
        reactions[rid] = r
    for rid, r in reactions.items():
        r["reverse_reaction_ids"] = sorted(t for t, q in reactions.items()
                                          if q["reactants"] == r["products"] and q["products"] == r["reactants"])
    return reactions


def rid(n):
    return f"re{n:010d}"


def supplies(species):
    return [{"species_id": s, "amount": "1", "role": "CATALYST_SEED" if s in ("GlyRS", "MetRS", "MTF") else "DECLARED_EXTERNAL_BOUNDARY",
             "source": "B0-1_FORMAL_BOUNDARY_ASSUMPTION", "independently_justified": False,
             "justification": "Explicit finite test condition; availability in the full model is unresolved"} for s in sorted(species)]


def construct(wid, ids, boundary, outputs, catalysts, classification, interpretation, rx):
    """Allocate exact tokens to occurrence origins, producing a causal event DAG."""
    pool = defaultdict(list)
    for s in boundary:
        pool[s["species_id"]].append(["BOUNDARY:" + s["species_id"], Fraction(s["amount"])])
    initial = {s["species_id"]: s["amount"] for s in boundary}
    events, deps, handoffs, trace = [], [], [], []
    net = defaultdict(Fraction)
    for i, reaction_id in enumerate(ids):
        r = rx[reaction_id]
        eid = f"{wid}:E{i+1:02d}"
        bindings = []
        for s, value in r["reactants"].items():
            need = Fraction(value)
            available = sum((v for _, v in pool[s]), Fraction())
            if available < need:
                raise ValueError(f"MISSING_REQUIRED_INPUT: {eid} {s}: {available} < {need}")
            for token in pool[s]:
                if not need:
                    break
                use = min(token[1], need)
                if not use:
                    continue
                origin = token[0]
                bindings.append({"species_id": s, "amount": str(use), "origin": origin})
                if not origin.startswith("BOUNDARY:"):
                    deps.append({"source_event": origin, "target_event": eid, "species_id": s, "amount": str(use), "evidence": "EXTRACTED"})
                    if s not in {"ATP", "ADP", "AMP", "GTP", "GDP", "PO4", "PPi", "FD", "THF", "Gly", "Met"}:
                        handoffs.append({"source_event": origin, "source_product": s, "target_event": eid,
                                         "target_reactant": s, "amount": str(use), "evidence": "EXACT_SOURCE_SPECIES", "confidence": "SOURCE_REACTION_VERIFIED"})
                token[1] -= use
                need -= use
            net[s] -= Fraction(value)
        for s, v in r["products"].items():
            pool[s].append([eid, Fraction(v)])
            net[s] += Fraction(v)
        events.append({"event_id": eid, "reaction_id": reaction_id, "occurrence_origin": eid,
                       "inputs": r["reactants"], "outputs": r["products"], "equation": r["equation"], "input_origins": bindings})
        trace.append({"event_id": eid, "marking_after": exact({s: sum((n for _, n in v), Fraction()) for s, v in pool.items()})})
    final = trace[-1]["marking_after"]
    internal = sorted((set().union(*(set(e["inputs"]) | set(e["outputs"]) for e in events)) - set(net.keys())) | {s for s, v in net.items() if not v})
    internal = sorted(s for s in internal if s not in initial and s not in outputs)
    for s in boundary:
        s["consuming_events"] = [e["event_id"] for e in events if s["species_id"] in e["inputs"]]
    streams = []
    # Source-name matching proposes identities only. Exact species flow is checked separately.
    for e in events:
        for carrier in ("GlyRS", "tRNAGlyGCC", "MetRS", "tRNAfMetCAU", "EFTu", "MTF", "IF2", "elRS70SAGGU0002"):
            before = sorted(s for s in e["inputs"] if carrier in s)
            after = sorted(s for s in e["outputs"] if carrier in s)
            if before or after:
                streams.append({"event_id": e["event_id"], "carrier_label": carrier, "before_species": before,
                                "after_species": after, "evidence": "INFERRED", "status": "HUMAN_REVIEW_REQUIRED",
                                "basis": "Source-name/context projection only; no independently verified molecular composition"})
    return {"witness_id": wid, "interpretation": interpretation, "source_reaction_ids": sorted(set(ids)),
            "reaction_occurrences": events, "occurrence_counts": dict(sorted(Counter(ids).items())),
            "ordered_firing_witness": [e["event_id"] for e in events], "event_dependencies": deps,
            "external_boundary_supplies": boundary, "initial_marking": initial, "final_marking": final,
            "firing_trace": trace, "source_species_handoffs": handoffs,
            "inferred_carrier_handoffs": [{"source_event": e["event_id"], "reaction_id": e["reaction_id"],
                "before": list(e["inputs"]), "after": list(e["outputs"]), "evidence": "INFERRED",
                "status": "HUMAN_REVIEW_REQUIRED", "confidence": "PROVISIONAL",
                "basis": "Source transition and reviewed context; molecular composition not independently certified"} for e in events],
            "provisional_carrier_streams": streams,
            "carrier_identity_status": "EXACT_SPECIES_FLOW_VERIFIED_COMPOSITE_IDENTITY_HUMAN_REVIEW_REQUIRED",
            "net_stoichiometry": exact(net), "net_reaction": equation(exact({s: -v for s, v in net.items() if v < 0}), exact({s: v for s, v in net.items() if v > 0})),
            "internal_species": internal, "expected_output_species": outputs,
            "catalyst_recovery_claims": [{"species_id": c, "initial": initial[c], "final": final.get(c, "0")} for c in catalysts],
            "reference_parameter_support": {r: {"parameter_id": r + "_k1", "value": rx[r]["reference_parameter"], "status": rx[r]["reference_activity"]} for r in sorted(set(ids))},
            "structural_status": "CANDIDATE_AWAITING_INDEPENDENT_VERIFICATION", "classification": classification,
            "scientific_status": "PENDING_HUMAN_REVIEW", "source_provenance": {"path": SOURCE, "evidence": "EXTRACTED"},
            "unresolved_assumptions": ["Boundary supplies are formal test assumptions, not full-network availability evidence",
                "Composite molecular identity projections remain HUMAN_REVIEW_REQUIRED", "No trajectory flux, kinetic dominance, timescale separation or reduction is established"]}


def build():
    rx = read_source()
    review_path = "docs/reduction/pathways/phase_b0_b0_2_review_record.json"
    review = json.loads((ROOT / review_path).read_text(encoding="utf-8"))
    graph = json.loads((OUT / "glyrs_metrs_graph.json").read_text(encoding="utf-8"))
    gly = next(p["reaction_ids"] for p in graph["modules"]["GlyRS"]["paths"] if p["id"] == "GlyRS-P01")
    met = next(p["reaction_ids"] for p in graph["modules"]["MetRS"]["paths"] if p["id"] == "MetRS-P01")
    mtf = list(map(rid, (418, 422, 426, 428, 434)))
    bmet = ["MetRS", "Met", "ATP", "tRNAfMetCAU", "MTF", "FD"]
    configs = [
        ("W1", gly + [rid(275), rid(13)], ["GlyRS", "Gly", "ATP", "tRNAGlyGCC", "EFTu_GTP", "elRS70SAGGU0002_fMet"], ["elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC"], ["GlyRS"], "INTERFACE_ONLY", "GlyRS-produced charged tRNA enters EF-Tu and the source ribosome binding interface; elongation is incomplete"),
        ("W2", met + mtf, bmet, ["fMettRNAfMetCAU"], ["MetRS", "MTF"], "STRUCTURAL_HANDOFF_WITNESS", "MetRS product and independently prepared MTF-FD converge at 0422; 0426 transforms the source complex, 0428 releases product, 0434 recovers MTF"),
        ("W3", met + mtf + [rid(449)], bmet + ["IF2_GTP"], ["IF2_GTP_fMettRNAfMetCAU"], ["MetRS", "MTF"], "INTERFACE_ONLY", "W2-produced formylated tRNA binds explicitly supplied IF2-GTP; ribosomal initiation is not reconstructed"),
        ("W2-MTF", mtf, ["MTF", "FD", "MettRNAfMetCAU"], ["fMettRNAfMetCAU"], ["MTF"], "COMPLETE_CATALYTIC_CYCLE", "Finite source-level MTF recovery and free product release under declared charged-tRNA supply"),
        ("W2-ALT", met + list(map(rid, (420, 424, 426, 428, 434))), bmet, ["fMettRNAfMetCAU"], ["MetRS", "MTF"], "STRUCTURAL_HANDOFF_WITNESS", "Alternative Met-tRNA-first binding order rejoins at MTF_FD_MettRNAfMetCAU; it competes with FD-first entry"),
    ]
    witnesses = [construct(w, ids, supplies(b), o, c, label, text, rx) for w, ids, b, o, c, label, text in configs]
    for w in witnesses:
        if w["witness_id"] in ("W2", "W3"):
            w["independent_precursor_branches"] = [[e["event_id"] for e in w["reaction_occurrences"] if e["reaction_id"] in met],
                                                  [e["event_id"] for e in w["reaction_occurrences"] if e["reaction_id"] == rid(418)]]
    selected = set().union(*(set(w["source_reaction_ids"]) for w in witnesses))
    # Bounded source incidence appendix: preserves alternatives, inverse directions and sinks,
    # without enumerating new pathways or counting appendix reactions in witness nets.
    anchors = {s for r in selected for side in ("reactants", "products") for s in rx[r][side]}
    local = {r for r, v in rx.items() if any(s in anchors and (s.startswith(("GlyRS", "MetRS", "MTF")) or s in
             {"GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU", "EFTu_GTP_GlytRNAGlyGCC", "IF2_GTP_fMettRNAfMetCAU"})
             for side in ("reactants", "products") for s in v[side])}
    local |= selected | {rid(414), rid(445), rid(446), rid(450)}
    sources = [provenance(SOURCE, "CANONICAL_SBML"), provenance(ARCHIVE, "AUTHOR_REFERENCE_PARAMETERS"),
               provenance(CSV, "AUTHOR_REFERENCE_PARAMETER_COPY"), provenance(V2, "REVIEWED_LEVEL_C_V2"),
               provenance("docs/reduction/pathways/glyrs_metrs_graph.json", "VERIFIED_PHASE_A_STARTING_PATH_ONLY"),
               provenance(review_path, "USER_REVIEW_AND_PUBLISHED_IDENTITY_CONTEXT_NOT_STOICHIOMETRIC_SOURCE")]
    return {"schema_version": 1, "phase": "B0-1", "scientific_status": "PENDING_HUMAN_REVIEW", "phase_b1_authorized": False,
            "researcher_review": {"path": review_path, "scientific_status": review["scientific_status"],
                                  "formal_signoff_status": review["formal_signoff_status"], "authority": review["authority"]},
            "biochemical_identity_annotations": {"FD": {"identity": review["sources"]["matsuura"]["definition"],
                 "evidence": "EXTRACTED_FROM_ORIGINAL_ARTICLE_INLINE_SI", "citation": review["sources"]["matsuura"]["url"],
                 "doi": review["sources"]["matsuura"]["doi"], "section": review["sources"]["matsuura"]["section"],
                 "scope": "FD biochemical identity only; complete complex composition remains INFERRED"}},
            "shared_substrate_competition": {"species_id": "MettRNAfMetCAU", "competing_reaction_ids": list(map(rid, (420, 422, 288))),
                 "pool_semantics": "ONE_SHARED_ORIGINAL_SOURCE_SPECIES_POOL", "phase_b1_implementation_authorized": False},
            "if2_reference_directions": {r: {"equation": rx[r]["equation"], "parameter": rx[r]["reference_parameter"],
                 "status": rx[r]["reference_activity"]} for r in map(rid, (449, 450))},
            "source_provenance": sources, "witnesses": witnesses, "reactions": {r: rx[r] for r in sorted(local)},
            "rejoin": {"primary_reaction": rid(422), "alternative_reaction": rid(424), "species_id": "MTF_FD_MettRNAfMetCAU", "evidence": "EXTRACTED"},
            "optional_upstream": {"reaction_id": rid(445), "included_in_core_W3": False, "equation": rx[rid(445)]["equation"], "boundary_alternative": "Supply IF2 + GTP instead of IF2_GTP; separate future test"},
            "navigation_scope": "BOUNDED_WITNESSES_AND_ONE_HOP_SOURCE_INCIDENCE_NOT_FULL_NETWORK_PATHWAY_RECONSTRUCTION"}


def markdown(data):
    lines = ["# Phase B0-1 finite multi-carrier handoff witnesses — B0-2 documentation revision", "", "Automated B0-1 contract status: `PENDING_HUMAN_REVIEW` (retained separately from researcher decisions). Current user-supplied researcher status: `" + data["researcher_review"]["scientific_status"] + "`; final formal signoff is pending. See [the B0-2 review record](phase_b0_b0_2_review_record.md). Phase B1 is not authorized.", "", "Equations below are extracted from canonical SBML. Formal tokens are not concentrations. See the JSON for every before/after marking, exact token allocation, dependency and provenance fingerprint.", "", "## FD identity from the original publication", "", "`FD` is **" + data["biochemical_identity_annotations"]["FD"]["identity"] + " (10-甲酰四氢叶酸)**, explicitly identified in Matsuura et al. 2017, DOI [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114), inline SI Results / Model Construction / Model construction for formylation of initiator tRNA. [Original article and SI text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/) and [Dataset S21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/#d35e1396). Its source species ID and coefficients stay unchanged. This identity citation does not certify full complex composition or real kinetic behavior.", ""]
    for w in data["witnesses"]:
        lines += ["## " + w["witness_id"], "", w["interpretation"], "", "Classification: `" + w["classification"] + "`; composite identity: `HUMAN_REVIEW_REQUIRED`.", "", "Boundary supplies (each exactly one formal token, independently justified availability: false):", ""]
        lines += ["- `" + s["species_id"] + "`: " + s["role"] + "; consumed at " + ", ".join(s["consuming_events"]) for s in w["external_boundary_supplies"]]
        lines += ["", "One valid firing order follows. Independent branches can be reordered; the listing does not impose their chronological order.", "", "| Event | Original directed reaction | Complete source equation | Author k | Direction | Exact inverse (not fired) |", "|---|---|---|---|---|---|"]
        for e in w["reaction_occurrences"]:
            r = data["reactions"][e["reaction_id"]]
            lines.append(f"| {e['event_id']} | {e['reaction_id']} | `{e['equation']}` | {r['reference_parameter']} | {r['reference_activity']} | {', '.join(r['reverse_reaction_ids']) or 'none'} |")
        lines += ["", "Causal DAG edges (actual carried source species, all coefficients explicit):", ""]
        lines += [f"- {d['source_event']} → {d['target_event']}: `{d['species_id']}` × {d['amount']}." for d in w["event_dependencies"]]
        lines += ["", "**Exact structural net (`S w`, not an effective kinetic reaction):**", "", "```text", w["net_reaction"], "```", "", "Recovered catalysts: " + ", ".join(c["species_id"] for c in w["catalyst_recovery_claims"]) + ".", "", "Cancelled declared internal species: " + ", ".join(w["internal_species"]) + ".", ""]
    lines += ["## Branches, alternatives and scientific boundaries", "", "W2: 0418 has no dependency on MetRS. 0224-produced MettRNAfMetCAU and 0418-produced MTF_FD converge at 0422. MetRS recovery at 0170 is a separate successor of 0224. Product release 0428 and MTF recovery 0434 are distinct events. W3 reuses the W2 occurrences once and adds 0449; no card reference creates another chemical event.", "", "W2-ALT replaces 0418/0422 with 0420/0424. Both entries produce the exact source species MTF_FD_MettRNAfMetCAU. They are mutually exclusive alternatives for one MTF seed, not consecutive steps. 0421/0423 are exact reverse outlets; 0427 is an original reference-disabled inverse of 0426. The appendix includes all source exits/entrances at the selected local enzyme/charged-tRNA states, including sinks; none is silently fired.", "", "W1 requires externally supplied EFTu_GTP and elRS70SAGGU0002_fMet. Their upstream formation remains unresolved; the endpoint is ribosome-bound and does not finish elongation. W3 requires IF2_GTP, stops before ribosomal initiation and does not recover IF2. Optional 0445 is inspected below and is excluded from all core occurrence counts.", "", "`FD` and `THF` retain their source IDs. FD's biochemical identity is documented above from the original publication. Full complex composition and nucleotide content embedded in complexes remain INFERRED; ATP/GTP and other shared resources do not certify a carrier history. No flux, preferred binding order, kinetic feasibility, QSSA, timescale separation or reduced model is approved.", "", "## IF2 directionality and shared Met-tRNA competition", "", "Both original IF2 binding directions are reference-enabled; W3 fires only 0449. Preserve 0450 as an available inverse and do not infer irreversibility or equilibrium from reference parameter values.", ""]
    for r, entry in data["if2_reference_directions"].items():
        lines.append(f"- `{r}`: `{entry['equation']}`; reference k1 = {entry['parameter']} ({entry['status']}).")
    lines += ["", "MTF entry (0420/0422) and EF-Tu entry (0288) consume the same original MettRNAfMetCAU pool. Any later B1 must preserve these competing exits and must not supply separate copies to isolated modules or simply add their nets. B1 implementation remains unauthorized. The [B0-2 review record](phase_b0_b0_2_review_record.md) cites the 2026 EF-Tu study as external supporting context, with publisher-abstract-only coverage explicitly stated.", "", "| Competing original ID | Complete source equation | Reference k1 |", "|---|---|---|"]
    for r in data["shared_substrate_competition"]["competing_reaction_ids"]:
        entry = data["reactions"][r]
        lines.append(f"| {r} | `{entry['equation']}` | {entry['reference_parameter']} |")
    lines += ["", "## Source incidence appendix (context only, excluded from witness sums)", "", "| Original ID | Complete equation | Author k | Direction | Inverse |", "|---|---|---|---|---|"]
    for rid_, r in data["reactions"].items():
        lines.append(f"| {rid_} | `{r['equation']}` | {r['reference_parameter']} | {r['reference_activity']} | {', '.join(r['reverse_reaction_ids']) or 'none'} |")
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", type=Path, default=OUT)
    args = p.parse_args()
    data = build()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "phase_b0_handoff_witnesses.json").write_bytes((json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    (args.output_dir / "phase_b0_handoff_witnesses.md").write_bytes(markdown(data).encode("utf-8"))
    print(json.dumps({"execution_status": "BUILT", "witnesses": {w["witness_id"]: len(w["reaction_occurrences"]) for w in data["witnesses"]}, "scientific_status": data["scientific_status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
