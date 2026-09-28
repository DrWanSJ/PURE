#!/usr/bin/env python3
"""Rebuild the chemistry-first, provisional PNAS2017 functional map.

The v1 table is an immutable seed and source/audit carrier. This program never
changes scientific reduction decisions or infers kinetic simplifications.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs/reduction"
V1 = DIR / "reaction_level_annotation_v1.csv"
DECISIONS = DIR / "reduction_decisions.csv"


def read(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def num(row):
    return float(row["official_parameter_value"])


def species(row):
    return set(json.loads(row["reactants_json"])) | set(json.loads(row["products_json"]))


def equation(row):
    def side(key):
        return " + ".join(json.loads(row[key])) or "∅"
    return f"{side('reactants_json')} -> {side('products_json')}"


def ids(numbers):
    return {f"re{n:010d}" for n in numbers}


GLY_BIND = ids([126,131,132,133,134,135,136,137,188,190,191,192,193,194,195,196,199,201,200,202,203,204,205,206])
GLY_ACT = ids([140,141,127,150,147,148,143,149,197,198,189,217])
GLY_CHARGE = ids([145,146,176,216,209,210,178,179,180,181,182,183,184,185])
GLY_SHARED = ids([207,208])
MET_BIND = ids([151,156,157,158,159,160,161,162,230,232,233,234,235,236,237,238,241,243,242,244,245,246,247,248])
MET_ACT = ids([165,166,152,175,172,173,168,174,239,240,231,260])
MET_CHARGE = ids([170,171,218,259,251,252,220,221,222,223,224,225,226,227])
MET_SHARED = ids([249,250])
APPROVED = {}
for group, stage in ((GLY_BIND | MET_BIND, "RS_binding"),
                     (GLY_ACT | MET_ACT, "RS_activation"),
                     (GLY_CHARGE | MET_CHARGE, "RS_charging"),
                     (GLY_SHARED | MET_SHARED, "RS_activation;RS_charging")):
    APPROVED.update({rid: stage for rid in group})


INITIATION_FAMILIES = {"RFAM_025", "RFAM_026"}
NEWLY_REVIEWED_FAMILIES = {"RFAM_013", "RFAM_015", "RFAM_016", "RFAM_017",
                           "RFAM_018", "RFAM_022", "RFAM_024", "RFAM_033", "RFAM_034"}
FINAL_REVIEWED_FAMILIES = {"RFAM_002", "RFAM_004", "RFAM_014"}

# Human-reviewed reaction-local events. ID and family are both checked; the
# verifier checks source identity and representative mechanistic equations.
REVIEWED_EVENTS = {}
def reviewed(family, numbers, stage, rule):
    for rid in ids(numbers):
        assert rid not in REVIEWED_EVENTS
        REVIEWED_EVENTS[rid] = (family, stage, rule)

reviewed("RFAM_013", range(261, 275), "ELONG_energy_coupling", "APPROVED_EFTU_NUCLEOTIDE_CYCLE")
reviewed("RFAM_013", [275, 276, 288, 289], "ELONG_aa_tRNA_delivery", "APPROVED_EFTU_AATRNA_TERNARY_FORMATION")
for family, binding, conversion, rule in (
        ("RFAM_015", list(range(330, 338)) + list(range(340, 348)), [338, 339], "APPROVED_CK_TRANSFER"),
        ("RFAM_016", list(range(355, 363)) + list(range(365, 369)) + list(range(375, 379)), [363, 364], "APPROVED_NDK_TRANSFER"),
        ("RFAM_017", list(range(380, 388)) + list(range(390, 398)), [388, 389], "APPROVED_MK_TRANSFER")):
    reviewed(family, binding, "EN_binding", "APPROVED_ENZYME_LIGAND_BINDING")
    reviewed(family, conversion, "EN_energy_transfer", rule)
reviewed("RFAM_018", [405, 406, 409, 410, 411, 412], "EN_binding", "APPROVED_ENZYME_LIGAND_BINDING")
reviewed("RFAM_018", [407, 408], "EN_byproduct_processing", "APPROVED_PPIASE_CONVERSION")
reviewed("RFAM_022", [445, 446], "INIT_energy_commitment", "APPROVED_IF2_GTP_LOADING")
reviewed("RFAM_022", [449, 450], "INIT_tRNA_recruitment", "APPROVED_IF2_FMET_TRNA_CARGO")
reviewed("RFAM_024", [455, 456], "INIT_70S_formation", "APPROVED_BARE_70S_FORMATION")
reviewed("RFAM_033", [796, 797, 799, 800], "TERM_factor_binding", "APPROVED_RF1_FACTOR_BINDING")
reviewed("RFAM_033", [798, 810], "TERM_peptide_release", "APPROVED_RF1_PEPTIDE_RELEASE")
reviewed("RFAM_034", [811, 812, 814, 815], "TERM_factor_binding", "APPROVED_RF2_FACTOR_BINDING")
reviewed("RFAM_034", [813, 823], "TERM_peptide_release", "APPROVED_RF2_PEPTIDE_RELEASE")

# Final human mechanistic audit: two elongation cycles and the shared EF-G
# elongation/recycling machinery. The disabled side paths retain these labels.
for family, delivery, energy, peptide, translocation in (
        ("RFAM_002", [13, 17, 21, 26, 27, 28, 61, 63, 64, 65],
         [14, 15, 16, 19, 20, 22, 23, 60], [18, 62], [24, 25, 66, 67]),
        ("RFAM_004", [74, 78, 82, 87, 88, 89, 119, 121, 122, 123],
         [75, 76, 77, 80, 81, 83, 84, 118], [79, 120], [85, 86, 124, 125])):
    reviewed(family, delivery, "ELONG_aa_tRNA_delivery", "APPROVED_EFTU_AATRNA_DELIVERY")
    reviewed(family, energy, "ELONG_energy_coupling", "APPROVED_ELONG_NUCLEOTIDE_ENERGY_CYCLE")
    reviewed(family, peptide, "ELONG_peptide_formation", "APPROVED_PEPTIDE_EXTENSION")
    reviewed(family, translocation, "ELONG_translocation", "APPROVED_RIBOSOME_POSITIONAL_TRANSLOCATION")
reviewed("RFAM_014", [292, 293, 294, 295], "ELONG_energy_coupling", "APPROVED_EFG_FREE_NUCLEOTIDE_CYCLE")
reviewed("RFAM_014", [298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 309, 325, 326, 328],
         "ELONG_energy_coupling", "APPROVED_ELONG_EFG_RIBOSOME_ENERGY_CYCLE")
reviewed("RFAM_014", [895, 896, 900, 901, 902, 904, 905, 906, 907, 908, 909, 956],
         "RECYCLE_disassembly", "APPROVED_RECYCLE_RRF_EFG_DISASSEMBLY")
reviewed("RFAM_014", [910, 957], "RECYCLE_disassembly", "APPROVED_RECYCLE_70S_SPLITTING")
reviewed("RFAM_014", list(range(911, 924)) + list(range(958, 969)),
         "RECYCLE_component_release", "APPROVED_RECYCLE_COMPONENT_RELEASE")
reviewed("RFAM_014", [308, 327], "ELONG_energy_coupling;RECYCLE_component_release",
         "APPROVED_EFG_50S_SHARED_JUNCTION")
assert len(REVIEWED_EVENTS) == 204


def initiation_chemistry(row):
    """Human-approved reaction-local initiation rules, in strict priority order."""
    src, dst = (set(json.loads(row[k])) for k in ("reactants_json", "products_json"))

    def ribosome(side, subunit):
        return any(name.startswith(subunit) for name in side)

    # Joining and its exact reverse are the only 70S-formation events here.
    if (("RS50S" in src and ribosome(src, "RS30S") and ribosome(dst, "RS70S")) or
            ("RS50S" in dst and ribosome(dst, "RS30S") and ribosome(src, "RS70S"))):
        return "INIT_70S_formation", "APPROVED_EXPLICIT_30S_50S_70S_CONVERSION"

    def has(side, token):
        return any(token in name for name in side)

    # A bound IF2 nucleotide-state change or PO4 release/rebinding is chemical
    # energy commitment; mere IF2_GTP binding to a ribosome is not.
    gtp_gdp_po4 = ((has(src, "IF2_GTP") and has(dst, "IF2_GDP_PO4")) or
                    (has(dst, "IF2_GTP") and has(src, "IF2_GDP_PO4")))
    po4_release = ((has(src, "IF2_GDP_PO4") and "PO4" in dst and has(dst, "IF2_GDP")) or
                   (has(dst, "IF2_GDP_PO4") and "PO4" in src and has(src, "IF2_GDP")))
    if gtp_gdp_po4 or po4_release:
        return "INIT_energy_commitment", "APPROVED_IF2_NUCLEOTIDE_OR_PO4_CHEMISTRY"

    # Cargo-bound IF2 counts only when fMet-tRNA occupancy of a ribosome
    # changes across the reaction, including the exact reverse channel.
    def bound_initiator(side):
        return any("fMettRNAfMetCAU" in name and (name.startswith("RS30S") or name.startswith("RS70S") or name.startswith("elRS70S")) for name in side)

    if bound_initiator(src) != bound_initiator(dst):
        return "INIT_tRNA_recruitment", "APPROVED_RIBOSOME_BOUND_INITIATOR_TRNA_CHANGE"

    # Pre/post-joining state matters: IF1/IF3/IF2_GDP occupancy on an already
    # formed 70S initiation complex is factor release/rebinding. Bare 70S+IF3
    # and 70S+IF1 assembly remain INIT_assembly.
    post_joining_70s = any((name.startswith("RS70S") or name.startswith("elRS70S")) and
                           any(token in name for token in ("fMettRNAfMetCAU", "_mRNA", "IF2_GDP"))
                           for name in src | dst)
    free_factor = any(name in {"IF1", "IF3", "IF2_GDP"} for name in src | dst)
    if post_joining_70s and free_factor:
        return "INIT_factor_release", "APPROVED_POST_JOINING_70S_FACTOR_OCCUPANCY"

    free_assembly_component = any(name in {"IF1", "IF3", "IF2_GTP", "mRNA"} for name in src | dst)
    if free_assembly_component and any(ribosome(side, "RS30S") or ribosome(side, "RS70S") for side in (src, dst)):
        return "INIT_assembly", "APPROVED_INITIATION_FACTOR_OR_MRNA_ASSEMBLY"
    return "", ""


def chemistry(row):
    """Only structurally explicit events receive hard anchors."""
    rid = row["reaction_id"]
    if rid in REVIEWED_EVENTS:
        family, stage, rule = REVIEWED_EVENTS[rid]
        assert row["reaction_family_id"] == family, rid
        return stage, rule
    if row["reaction_family_id"] in INITIATION_FAMILIES:
        return initiation_chemistry(row)
    if rid in APPROVED:
        stage = APPROVED[rid]
        return stage, "APPROVED_RS_CHEMISTRY" if ";" not in stage else "APPROVED_RS_STAGE_BOUNDARY"
    src, dst = (set(json.loads(row[k])) for k in ("reactants_json", "products_json"))
    all_names = src | dst
    if row["reaction_family_id"] == "RFAM_DEG" and any("degraded" in s for s in dst):
        return "DEG_sink", "EXPLICIT_DEGRADATION_PRODUCT"
    if row["reaction_family_id"] in {"RFAM_027", "RFAM_028", "RFAM_029", "RFAM_030", "RFAM_031", "RFAM_032"}:
        return "EN_energy_transfer", "EXPLICIT_NUCLEOTIDE_CONVERSION"
    if row["reaction_family_id"] in {"RFAM_015", "RFAM_016", "RFAM_017", "RFAM_018"} and row["mechanistic_reaction_type"] == "STATE_TRANSITION":
        stage = "EN_byproduct_processing" if "PPiase" in "".join(all_names) else "EN_energy_transfer"
        return stage, "EXPLICIT_ENZYME_BOUND_CHEMISTRY"
    if row["mechanistic_reaction_type"] == "STATE_TRANSITION":
        stage = row["level_c_primary_stage"]
        if stage in {"ELONG_peptide_formation", "ELONG_translocation", "TERM_peptide_release", "RECYCLE_disassembly", "RS_to_INIT_formylation", "INIT_energy_commitment", "TERM_energy_coupling", "ELONG_energy_coupling"}:
            return stage, "EXPLICIT_STATE_TRANSFORMATION_REVIEWED_V1_STAGE"
    if row["reaction_family_id"] in {"RFAM_001", "RFAM_003"} and "tRNA" in equation(row):
        return "ELONG_tRNA_release", "EXPLICIT_TRNA_RELEASE_STATE"
    return "", ""


def normalize(name):
    return (name.replace("GlytRNAGlyGCC", "AAtRNAX")
                .replace("MettRNAfMetCAU", "AAtRNAX")
                .replace("tRNAGlyGCC", "tRNAX")
                .replace("tRNAfMetCAU", "tRNAX")
                .replace("GlyRS", "AARS").replace("MetRS", "AARS")
                .replace("GlyAMP", "AAAMP").replace("MetAMP", "AAAMP")
                .replace("Gly", "AA").replace("Met", "AA"))


def signature(row):
    return tuple(tuple(sorted((normalize(k), v) for k, v in json.loads(row[field]).items()))
                 for field in ("reactants_json", "products_json"))


def specific(name):
    """Identity is required; degree alone never turns a currency hub into a bridge."""
    if name in {"ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "Gly", "Met", "RS30S", "RS50S", "RS70S", "CK", "NDK", "MK", "PPiase"}:
        return False
    return (name in {"GlyRS_AMP", "MetRS_AMP"} or
            ("RS" in name and "_" in name and any(token in name for token in ("EFG", "EFTu", "IF", "RF", "Pept"))))


def main():
    old = read(V1)
    decisions = read(DECISIONS)
    assert len(old) == len({r["reaction_id"] for r in old}) == 968
    assert len(decisions) == 968 and all(r["decision_status"] == "PENDING" for r in decisions)
    by = {r["reaction_id"]: r for r in old}
    output = []
    for oldrow in old:
        row = dict(oldrow)
        rid = row["reaction_id"]
        partner = by.get(row["reverse_partner_id"])
        own_zero = num(row) == 0
        partner_zero = num(partner) == 0 if partner else own_zero
        if own_zero and partner_zero:
            activity = "DISABLED_EXACT"
        elif partner and own_zero != partner_zero:
            first = min(rid, partner["reaction_id"])
            activity = "FORWARD_ONLY" if num(by[first]) != 0 else "REVERSE_ONLY"
        else:
            activity = "ACTIVE_OR_PARAMETERIZED"
        hard, rule = chemistry(row)
        seed = row["level_c_functional_contexts"]
        contexts = hard or seed
        if hard and ";" in hard:
            status = "SHARED_JUNCTION"
        elif activity == "DISABLED_EXACT":
            status = "REFERENCE_DISABLED"
        elif hard:
            status = "DIRECT_CHEMISTRY"
        elif row["topology_status"] == "SHARED_JUNCTION":
            status = "SHARED_JUNCTION"
        else:
            status = "GRAPH_PROPAGATED"
        anchor = bool(hard and ";" not in hard and activity != "DISABLED_EXACT")
        row.update(functional_annotation_status=status,
                   level_c_primary_stage="" if ";" in contexts else contexts,
                   level_c_functional_contexts=contexts,
                   is_functional_anchor=str(anchor).lower(),
                   anchor_basis=rule if anchor else "",
                   direct_chemistry_rule=rule,
                   reference_activity=activity,
                   reverse_parameter_value=partner["official_parameter_value"] if partner else "",
                   specific_intermediates="", cross_family_link_ids="",
                   graph_distance_to_anchor="0" if anchor else "",
                   graph_support_status="HARD_ANCHOR" if anchor else "NOT_APPLICABLE",
                   seed_v1_stage=seed, seed_v1_status=row["topology_status"],
                   annotation_changed_from_v1=str(contexts != seed).lower(),
                   change_reason=(rule if contexts != seed else ""),
                   human_functional_review_required="false",
                   human_functional_review_reason="")
        output.append(row)

    current = {r["reaction_id"]: r for r in output}
    # Recompute support from *v2 hard anchors only*. The old v1 anchor list
    # includes disabled channels and must not be reused as v2 evidence.
    incidence = defaultdict(list)
    for row in output:
        if row["reference_activity"] == "DISABLED_EXACT":
            row["supporting_anchor_ids"] = ""
            continue
        bridge = set(filter(None, row["bridge_species_participants"].split(";")))
        for name in species(row):
            if name in bridge or specific(name):
                incidence[name].append(row["reaction_id"])
    adjacent = defaultdict(set)
    for name, members in incidence.items():
        for rid in members:
            for other in members:
                if rid == other:
                    continue
                left, right = current[rid], current[other]
                same_module = bool(set(left["level_a_module_candidates"].split(";")) & set(right["level_a_module_candidates"].split(";")))
                if same_module or specific(name):
                    adjacent[rid].add(other)
    support = defaultdict(list)
    for anchor_row in output:
        if anchor_row["is_functional_anchor"] != "true":
            continue
        anchor = anchor_row["reaction_id"]
        frontier, seen = {anchor}, {anchor}
        for distance in range(1, 4):
            frontier = {neighbor for rid in frontier for neighbor in adjacent[rid]} - seen
            for rid in frontier:
                # Earlier initiation anchors and newly reviewed family
                # anchors must not silently reclassify outside families.
                # Keep the four pre-existing IF2 chemistry anchors as the
                # outside-family initiation support.
                if (anchor_row["reaction_family_id"] in INITIATION_FAMILIES and
                        anchor not in ids([715, 716, 717, 718]) and
                        current[rid]["reaction_family_id"] not in INITIATION_FAMILIES):
                    continue
                if (anchor_row["reaction_family_id"] in NEWLY_REVIEWED_FAMILIES and
                        current[rid]["reaction_family_id"] not in NEWLY_REVIEWED_FAMILIES):
                    continue
                if (anchor_row["reaction_family_id"] in FINAL_REVIEWED_FAMILIES and
                        current[rid]["reaction_family_id"] not in FINAL_REVIEWED_FAMILIES):
                    continue
                support[rid].append((distance, anchor, anchor_row["level_c_functional_contexts"]))
            seen |= frontier
    for row in output:
        rid = row["reaction_id"]
        if row["is_functional_anchor"] == "true":
            row["supporting_anchor_ids"] = rid
            continue
        if row["reference_activity"] == "DISABLED_EXACT":
            row["graph_support_status"] = "DISABLED_NOT_PROPAGATED"
            continue
        candidates = support[rid]
        if not candidates:
            row["supporting_anchor_ids"] = ""
            row["graph_support_status"] = "NO_HARD_ANCHOR_WITHIN_3"
            if row["functional_annotation_status"] == "GRAPH_PROPAGATED":
                row["functional_annotation_status"] = "HUMAN_REVIEW_REQUIRED"
            continue
        nearest = min(item[0] for item in candidates)
        close = [item for item in candidates if item[0] == nearest]
        row["graph_distance_to_anchor"] = str(nearest)
        row["supporting_anchor_ids"] = ";".join(sorted({item[1] for item in close}))
        contexts = {item[2] for item in close}
        seed_contexts = set(row["level_c_functional_contexts"].split(";"))
        if row["direct_chemistry_rule"]:
            row["graph_support_status"] = "DIRECT_CHEMISTRY_HAS_PRIORITY"
        elif len(contexts) > 1:
            row["graph_support_status"] = "MULTIPLE_EQUIDISTANT_HARD_ANCHORS"
            if row["functional_annotation_status"] == "GRAPH_PROPAGATED":
                row["functional_annotation_status"] = "HUMAN_REVIEW_REQUIRED"
        elif contexts & seed_contexts:
            row["graph_support_status"] = "MATCHING_HARD_ANCHOR_CONTEXT"
        else:
            row["graph_support_status"] = "CONFLICTING_HARD_ANCHOR_CONTEXT"
            if row["functional_annotation_status"] == "GRAPH_PROPAGATED":
                row["functional_annotation_status"] = "HUMAN_REVIEW_REQUIRED"

    # Provenance-bound cross-family links. A source/product incidence is kept even
    # when its families have different Level-B subsystem names.
    occurrences = defaultdict(lambda: defaultdict(set))
    for row in output:
        if row["reaction_family_id"] == "RFAM_DEG":
            continue
        for name in species(row):
            if specific(name):
                occurrences[name][row["reaction_family_id"]].add(row["reaction_id"])
    links = []
    for name, families in sorted(occurrences.items()):
        keys = sorted(families)
        for i, left in enumerate(keys):
            for right in keys[i + 1:]:
                left_rows, right_rows = sorted(families[left]), sorted(families[right])
                ls = {current[x]["level_b_subsystem_candidates"] for x in left_rows}
                rs = {current[x]["level_b_subsystem_candidates"] for x in right_rows}
                if ls == rs:
                    continue
                # Orient an unambiguous producer -> consumer bridge. If both
                # families produce and consume it, retain alphabetical order.
                left_produces = any(num(current[x]) > 0 and name in json.loads(current[x]["products_json"]) for x in left_rows)
                right_produces = any(num(current[x]) > 0 and name in json.loads(current[x]["products_json"]) for x in right_rows)
                left_consumes = any(num(current[x]) > 0 and name in json.loads(current[x]["reactants_json"]) for x in left_rows)
                right_consumes = any(num(current[x]) > 0 and name in json.loads(current[x]["reactants_json"]) for x in right_rows)
                if right_produces and left_consumes and not (left_produces and right_consumes):
                    left, right = right, left
                    left_rows, right_rows = right_rows, left_rows
                    ls, rs = rs, ls
                lid = f"CFL_{len(links)+1:03d}"
                links.append(dict(link_id=lid, specific_intermediate=name,
                                  source_family=left, target_family=right,
                                  source_reaction_ids=";".join(left_rows), target_reaction_ids=";".join(right_rows),
                                  source_subsystems=";".join(sorted(ls)), target_subsystems=";".join(sorted(rs)),
                                  link_basis="SPECIFIC_INTERMEDIATE_SHARED_ACROSS_SOURCE_SUBSYSTEMS",
                                  inference_scope="MECHANISTIC_CONNECTIVITY_ONLY"))
                for rid in left_rows + right_rows:
                    row = current[rid]
                    row["specific_intermediates"] = ";".join(sorted(set(filter(None, row["specific_intermediates"].split(";"))) | {name}))
                    row["cross_family_link_ids"] = ";".join(sorted(set(filter(None, row["cross_family_link_ids"].split(";"))) | {lid}))

    # Compare actual stoichiometry, rather than assuming a fixed Gly/Met ID offset.
    gly = [r for r in output if r["reaction_family_id"] in {"RFAM_005", "RFAM_006", "RFAM_009", "RFAM_010"}]
    met = [r for r in output if r["reaction_family_id"] in {"RFAM_007", "RFAM_008", "RFAM_011", "RFAM_012"}]
    met_by_sig = defaultdict(list)
    for row in met:
        met_by_sig[signature(row)].append(row)
    symmetry = []
    for row in gly:
        matches = met_by_sig[signature(row)]
        mirror = matches[0] if len(matches) == 1 else None
        result = "MATCH" if mirror and row["level_c_functional_contexts"] == mirror["level_c_functional_contexts"] and row["reference_activity"] == mirror["reference_activity"] else "EXCEPTION"
        symmetry.append((row, mirror, result))

    family_contexts = defaultdict(set)
    for row in output:
        family_contexts[row["reaction_family_id"]].update(row["level_c_functional_contexts"].split(";"))
    queue = []
    for row in output:
        # Live review means a new human functional decision is still needed.
        # Approved junctions, cross-family links, multi-stage families, and
        # disabled reference channels remain auditable in their own columns.
        if row["functional_annotation_status"] != "HUMAN_REVIEW_REQUIRED":
            continue
        reasons = []
        if row["graph_support_status"] == "NO_HARD_ANCHOR_WITHIN_3":
            reasons.append("NO_HARD_CHEMISTRY_ANCHOR_REVIEW")
        if row["graph_support_status"] == "CONFLICTING_HARD_ANCHOR_CONTEXT":
            reasons.append("HARD_ANCHOR_GRAPH_CONTEXT_CONFLICT_REVIEW")
        if row["graph_support_status"] == "MULTIPLE_EQUIDISTANT_HARD_ANCHORS":
            reasons.append("MULTIPLE_EQUIDISTANT_CONTEXTS_REVIEW")
        if not row["level_c_functional_contexts"]:
            reasons.append("UNEXPLAINED_REACTION_REVIEW")
        if not reasons:
            reasons.append("UNEXPLAINED_FUNCTIONAL_STATUS_REVIEW")
        row["human_functional_review_required"] = "true"
        row["human_functional_review_reason"] = ";".join(sorted(set(reasons)))
        queue.append(dict(reaction_id=row["reaction_id"], reaction_family_id=row["reaction_family_id"],
                          reaction_equation=equation(row), candidate_contexts=row["level_c_functional_contexts"],
                          reason_for_review=row["human_functional_review_reason"],
                          graph_evidence="supporting_anchor_ids=" + row["supporting_anchor_ids"] + ";cross_family_link_ids=" + row["cross_family_link_ids"],
                          chemistry_evidence=row["direct_chemistry_rule"] or "NO_HARD_CHEMISTRY_RULE",
                          source_subsystems=row["level_b_subsystem_candidates"], parameter_status=row["reference_activity"],
                          recommended_question_for_human="Confirm functional context from source chemistry; do not decide reduction."))
    family_rows = []
    for family in sorted(family_contexts):
        group = [r for r in output if r["reaction_family_id"] == family]
        family_rows.append(dict(reaction_family_id=family, reaction_count=len(group),
                                functional_contexts=";".join(sorted(family_contexts[family])),
                                hard_anchor_count=sum(r["is_functional_anchor"] == "true" for r in group),
                                disabled_exact_count=sum(r["reference_activity"] == "DISABLED_EXACT" for r in group),
                                human_functional_review_count=sum(r["human_functional_review_required"] == "true" for r in group),
                                source_subsystems=";".join(sorted({r["level_b_subsystem_candidates"] for r in group})),
                                cross_family_link_ids=";".join(sorted({x for r in group for x in r["cross_family_link_ids"].split(";") if x}))))
    extra = ["functional_annotation_status", "anchor_basis", "direct_chemistry_rule", "reference_activity",
             "reverse_parameter_value", "specific_intermediates", "cross_family_link_ids", "graph_distance_to_anchor",
             "seed_v1_stage", "seed_v1_status", "graph_support_status", "annotation_changed_from_v1", "change_reason",
             "human_functional_review_required", "human_functional_review_reason"]
    write(DIR / "reaction_level_annotation_v2.csv", output, list(old[0]) + [x for x in extra if x not in old[0]])
    write(DIR / "reaction_family_summary_v2.csv", family_rows, list(family_rows[0]))
    write(DIR / "reaction_cross_family_links_v2.csv", links, list(links[0]) if links else ["link_id", "specific_intermediate", "source_family", "target_family", "source_reaction_ids", "target_reaction_ids", "source_subsystems", "target_subsystems", "link_basis", "inference_scope"])
    write(DIR / "human_functional_review_queue_v2.csv", queue, ["reaction_id", "reaction_family_id", "reaction_equation", "candidate_contexts", "reason_for_review", "graph_evidence", "chemistry_evidence", "source_subsystems", "parameter_status", "recommended_question_for_human"])
    artifacts = ["reaction_level_annotation_v2.csv", "reaction_family_summary_v2.csv",
                 "reaction_cross_family_links_v2.csv", "human_functional_review_queue_v2.csv"]
    unresolved = sum(r["functional_annotation_status"] == "HUMAN_REVIEW_REQUIRED" for r in output)
    review_complete = unresolved == 0 and len(queue) == 0
    manifest = dict(schema_version="2.0", status="FUNCTIONAL_ANNOTATION_REVIEW_COMPLETE" if review_complete else "CHEMISTRY_FIRST_PROVISIONAL_FUNCTIONAL_NAVIGATION",
                    source_v1_sha256=hashlib.sha256(V1.read_bytes()).hexdigest(),
                    reduction_decisions_sha256=hashlib.sha256(DECISIONS.read_bytes()).hexdigest(),
                    source_sbml_sha256=old[0]["source_sbml_sha256"], reaction_count=len(output),
                    artifact_sha256={name: hashlib.sha256((DIR / name).read_bytes()).hexdigest() for name in artifacts},
                    functional_annotation_status_counts={status: sum(r["functional_annotation_status"] == status for r in output)
                                                         for status in ("DIRECT_CHEMISTRY", "GRAPH_PROPAGATED",
                                                                        "HUMAN_REVIEW_REQUIRED", "REFERENCE_DISABLED",
                                                                        "SHARED_JUNCTION")},
                    reference_activity_counts=dict(sorted(Counter(r["reference_activity"] for r in output).items())),
                    functional_annotation_unresolved=unresolved,
                    human_functional_review_queue=len(queue), functional_annotation_review_complete=review_complete,
                    cross_family_mechanistic_links=len(links),
                    gly_met_symmetry=dict(sorted(Counter(x[2] for x in symmetry).items())),
                    reduction_scientific_review=dict(pending=968, total=968),
                    scientific_boundary="No QSSA, fast equilibrium, lumping, deletion, reduced-core kinetics or kinetic equivalence approval.")
    manifest["human_approved_initiation_rules"] = [
        "INIT_assembly", "INIT_tRNA_recruitment", "INIT_70S_formation",
        "INIT_energy_commitment", "INIT_factor_release"]
    manifest["reviewed_initiation_families"] = {
        family: {
            "rows": sum(r["reaction_family_id"] == family for r in output),
            "stage_counts": dict(sorted(Counter(r["level_c_functional_contexts"] for r in output
                                                if r["reaction_family_id"] == family).items())),
            "status_counts": dict(sorted(Counter(r["functional_annotation_status"] for r in output
                                                 if r["reaction_family_id"] == family).items())),
            "human_functional_review_queue": sum(r["reaction_family_id"] == family for r in queue),
        }
        for family in sorted(INITIATION_FAMILIES)
    }
    manifest["newly_reviewed_functional_families"] = {
        family: {
            "rows": sum(r["reaction_family_id"] == family for r in output),
            "stage_counts": dict(sorted(Counter(r["level_c_functional_contexts"] for r in output
                                                if r["reaction_family_id"] == family).items())),
            "human_functional_review_queue": sum(r["reaction_family_id"] == family for r in queue),
        }
        for family in sorted(NEWLY_REVIEWED_FAMILIES)
    }
    manifest["final_reviewed_functional_families"] = {
        family: {
            "rows": sum(r["reaction_family_id"] == family for r in output),
            "stage_counts": dict(sorted(Counter(r["level_c_functional_contexts"] for r in output
                                                if r["reaction_family_id"] == family).items())),
            "status_counts": dict(sorted(Counter(r["functional_annotation_status"] for r in output
                                                 if r["reaction_family_id"] == family).items())),
        }
        for family in sorted(FINAL_REVIEWED_FAMILIES)
    }
    with (DIR / "reaction_annotation_manifest_v2.json").open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
