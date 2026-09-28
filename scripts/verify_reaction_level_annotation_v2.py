#!/usr/bin/env python3
"""Independent contracts for the chemistry-first annotation navigation layer."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs/reduction"
REVIEWED_FAMILIES = {"RFAM_013", "RFAM_015", "RFAM_016", "RFAM_017", "RFAM_018",
                     "RFAM_022", "RFAM_024", "RFAM_033", "RFAM_034"}
FINAL_FAMILIES = {"RFAM_002", "RFAM_004", "RFAM_014"}
NON_TARGET_SCIENTIFIC_SHA256 = "ebb6f2be26345d2206d2fcb02bc719f8749b8c85b5c071180a743355a102e72d"
SOURCE_V1_SHA256 = "805aaa2b9afa356486d83f6e12fb11b0def004ec4429e42ed0a4631085ec4562"
SOURCE_SBML_SHA256 = "dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df"
REDUCTION_DECISIONS_SHA256 = "70fd3f98de5056a1a63c29db58d310ec5986d4c52b6bfcbae9634b38e2e8d7f8"


def read(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def full(numbers):
    return {f"re{n:010d}" for n in numbers}


def main():
    v1path = DIR / "reaction_level_annotation_v1.csv"
    v1 = read(v1path)
    v2 = read(DIR / "reaction_level_annotation_v2.csv")
    audit = read(ROOT / "models/pnas2017_full_reference/audit/reaction_balance_audit.csv")
    decisions = read(DIR / "reduction_decisions.csv")
    queue = read(DIR / "human_functional_review_queue_v2.csv")
    links = read(DIR / "reaction_cross_family_links_v2.csv")
    families = read(DIR / "reaction_family_summary_v2.csv")
    manifest = json.loads((DIR / "reaction_annotation_manifest_v2.json").read_text(encoding="utf-8"))
    assert (DIR / "reaction_level_annotation_v0.csv").exists()
    assert (DIR / "reaction_graph_manifest_v1.json").exists()
    assert manifest["source_v1_sha256"] == hashlib.sha256(v1path.read_bytes()).hexdigest()
    assert manifest["reduction_decisions_sha256"] == hashlib.sha256((DIR / "reduction_decisions.csv").read_bytes()).hexdigest()
    assert manifest["source_v1_sha256"] == SOURCE_V1_SHA256
    assert manifest["source_sbml_sha256"] == SOURCE_SBML_SHA256
    assert manifest["reduction_decisions_sha256"] == REDUCTION_DECISIONS_SHA256
    for name, digest in manifest["artifact_sha256"].items():
        assert hashlib.sha256((DIR / name).read_bytes()).hexdigest() == digest, name
    by = {r["reaction_id"]: r for r in v2}
    a_by = {r["sbml_reaction_id"]: r for r in audit}
    assert len(v1) == len(v2) == len(by) == len(audit) == len(a_by) == 968
    assert set(by) == set(a_by)
    assert len(decisions) == 968 and {r["sbml_reaction_id"] for r in decisions} == set(by)
    assert all(r["decision_status"] == "PENDING" for r in decisions)
    assert not any(any(token in field.lower() for token in ("qssa_approved", "fast_eq_approved", "drop_approved", "lump_approved", "reduced_kinetics_approved"))
                   for field in decisions[0]), "reduction approval field introduced"
    assert all(r["source_sbml_sha256"] == manifest["source_sbml_sha256"] for r in v2)
    controlled = set()
    for row in v1:
        controlled.update(row["level_c_functional_contexts"].split(";"))
    pairs = set()
    queue_ids = {q["reaction_id"] for q in queue}
    for rid, row in by.items():
        source = a_by[rid]
        for field in ("reactants_json", "products_json", "official_parameter_id", "official_parameter_value", "level_a_module_candidates", "level_b_subsystem_candidates"):
            assert row[field] == source[field], (rid, field)
        assert row["functional_annotation_status"] in {"DIRECT_CHEMISTRY", "GRAPH_PROPAGATED", "SHARED_JUNCTION", "REFERENCE_DISABLED", "HUMAN_REVIEW_REQUIRED"}
        assert set(row["level_c_functional_contexts"].split(";")) <= controlled
        if row["direct_chemistry_rule"] and row["functional_annotation_status"] != "REFERENCE_DISABLED":
            assert row["level_c_functional_contexts"] != "", rid
            assert row["functional_annotation_status"] != "GRAPH_PROPAGATED", rid
        if row["reference_activity"] == "DISABLED_EXACT":
            assert row["is_functional_anchor"] == "false" and float(row["official_parameter_value"]) == 0
            assert not row["anchor_basis"]
        if row["is_functional_anchor"] == "true":
            assert row["direct_chemistry_rule"] and row["reference_activity"] != "DISABLED_EXACT"
        for anchor_id in filter(None, row["supporting_anchor_ids"].split(";")):
            assert by[anchor_id]["is_functional_anchor"] == "true"
            assert by[anchor_id]["reference_activity"] != "DISABLED_EXACT"
        if row["functional_annotation_status"] == "GRAPH_PROPAGATED":
            assert row["graph_support_status"] == "MATCHING_HARD_ANCHOR_CONTEXT"
            assert row["supporting_anchor_ids"] and 1 <= int(row["graph_distance_to_anchor"]) <= 3
        if row["functional_annotation_status"] == "HUMAN_REVIEW_REQUIRED":
            assert rid in queue_ids
        if row["reversibility_class"] == "EXACT_REVERSE_PAIR":
            partner = by[row["reverse_partner_id"]]
            assert partner["reverse_partner_id"] == rid
            assert all(row[k] == partner[k] for k in ("reaction_family_id", "level_c_functional_contexts", "functional_annotation_status", "reference_activity"))
            assert row["functional_annotation_status"] == "SHARED_JUNCTION" == partner["functional_annotation_status"] or (row["functional_annotation_status"] != "SHARED_JUNCTION" and partner["functional_annotation_status"] != "SHARED_JUNCTION")
            pairs.add(tuple(sorted((rid, partner["reaction_id"]))))
        assert row["human_functional_review_required"] == str(rid in queue_ids).lower()
    assert len(pairs) == 290

    # Approved independent regression fixtures for all explicitly named Gly
    # chemistry and its Met mirror. Reverse pairs must have identical contexts.
    fixtures = {
        "RS_binding": [126,131,132,133,134,135,136,137,188,190,191,192,193,194,195,196,199,201,200,202,203,204,205,206,
                       151,156,157,158,159,160,161,162,230,232,233,234,235,236,237,238,241,243,242,244,245,246,247,248],
        "RS_activation": [140,141,127,150,147,148,143,149,197,198,189,217,
                          165,166,152,175,172,173,168,174,239,240,231,260],
        "RS_charging": [145,146,176,216,209,210,178,179,180,181,182,183,184,185,
                        170,171,218,259,251,252,220,221,222,223,224,225,226,227],
        "RS_activation;RS_charging": [207,208,249,250],
    }
    for stage, numbers in fixtures.items():
        for rid in full(numbers):
            assert by[rid]["level_c_functional_contexts"] == stage, (rid, stage)
            assert by[rid]["direct_chemistry_rule"], rid
    for rid in full([143,149,168,174,176,216,218,259]):
        assert by[rid]["reference_activity"] == "DISABLED_EXACT"
        assert by[rid]["is_functional_anchor"] == "false"
    for rid in full([145,146,170,171]):
        assert by[rid]["reference_activity"] == "FORWARD_ONLY"

    approved = {
        "RFAM_013": {"ELONG_energy_coupling": list(range(261, 275)),
                     "ELONG_aa_tRNA_delivery": [275, 276, 288, 289]},
        "RFAM_015": {"EN_binding": list(range(330, 338)) + list(range(340, 348)),
                     "EN_energy_transfer": [338, 339]},
        "RFAM_016": {"EN_binding": list(range(355, 363)) + list(range(365, 369)) + list(range(375, 379)),
                     "EN_energy_transfer": [363, 364]},
        "RFAM_017": {"EN_binding": list(range(380, 388)) + list(range(390, 398)),
                     "EN_energy_transfer": [388, 389]},
        "RFAM_018": {"EN_binding": [405, 406, 409, 410, 411, 412],
                     "EN_byproduct_processing": [407, 408]},
        "RFAM_022": {"INIT_energy_commitment": [445, 446], "INIT_tRNA_recruitment": [449, 450]},
        "RFAM_024": {"INIT_70S_formation": [455, 456]},
        "RFAM_033": {"TERM_factor_binding": [796, 797, 799, 800], "TERM_peptide_release": [798, 810]},
        "RFAM_034": {"TERM_factor_binding": [811, 812, 814, 815], "TERM_peptide_release": [813, 823]},
    }
    assert set(approved) == REVIEWED_FAMILIES
    for family, stages in approved.items():
        expected_ids = set()
        for stage, numbers in stages.items():
            for rid in full(numbers):
                expected_ids.add(rid)
                row = by[rid]
                assert row["reaction_family_id"] == family and row["level_c_functional_contexts"] == stage, rid
                assert row["functional_annotation_status"] == "DIRECT_CHEMISTRY", rid
                assert row["direct_chemistry_rule"].startswith("APPROVED_"), rid
                assert rid not in queue_ids and row["human_functional_review_required"] == "false", rid
        assert {r["reaction_id"] for r in v2 if r["reaction_family_id"] == family} == expected_ids, family
        summary = manifest["newly_reviewed_functional_families"][family]
        assert summary["rows"] == len(expected_ids) and summary["human_functional_review_queue"] == 0
        assert summary["stage_counts"] == {stage: len(numbers) for stage, numbers in stages.items()}
    assert sum(len(numbers) for stages in approved.values() for numbers in stages.values()) == 98
    final = {
        "RFAM_002": {
            "ELONG_aa_tRNA_delivery": [13, 17, 21, 26, 27, 28, 61, 63, 64, 65],
            "ELONG_energy_coupling": [14, 15, 16, 19, 20, 22, 23, 60],
            "ELONG_peptide_formation": [18, 62],
            "ELONG_translocation": [24, 25, 66, 67]},
        "RFAM_004": {
            "ELONG_aa_tRNA_delivery": [74, 78, 82, 87, 88, 89, 119, 121, 122, 123],
            "ELONG_energy_coupling": [75, 76, 77, 80, 81, 83, 84, 118],
            "ELONG_peptide_formation": [79, 120],
            "ELONG_translocation": [85, 86, 124, 125]},
        "RFAM_014": {
            "ELONG_energy_coupling": [292, 293, 294, 295, 298, 299, 300, 301, 302, 303, 304, 305,
                                      306, 307, 309, 325, 326, 328],
            "ELONG_energy_coupling;RECYCLE_component_release": [308, 327],
            "RECYCLE_disassembly": [895, 896, 900, 901, 902, 904, 905, 906, 907, 908, 909, 910, 956, 957],
            "RECYCLE_component_release": list(range(911, 924)) + list(range(958, 969))},
    }
    for family, stages in final.items():
        expected_ids = set()
        for stage, numbers in stages.items():
            for rid in full(numbers):
                expected_ids.add(rid)
                row = by[rid]
                assert (row["reaction_family_id"], row["level_c_functional_contexts"]) == (family, stage), rid
                assert row["direct_chemistry_rule"].startswith("APPROVED_"), rid
                assert row["human_functional_review_required"] == "false" and rid not in queue_ids, rid
        group = [r for r in v2 if r["reaction_family_id"] == family]
        assert {r["reaction_id"] for r in group} == expected_ids, family
        assert not any(r["functional_annotation_status"] == "HUMAN_REVIEW_REQUIRED" for r in group), family
        summary = manifest["final_reviewed_functional_families"][family]
        assert summary["rows"] == len(expected_ids) and summary["stage_counts"] == {stage: len(numbers) for stage, numbers in stages.items()}, family
    for family, disabled in (("RFAM_002", [26, 27, 63, 64]), ("RFAM_004", [87, 88, 121, 122])):
        group = [r for r in v2 if r["reaction_family_id"] == family]
        assert len(group) == 24
        assert {r["reaction_id"] for r in group if r["functional_annotation_status"] == "REFERENCE_DISABLED"} == full(disabled)
        assert all(r["is_functional_anchor"] == "false" and r["direct_chemistry_rule"].startswith("APPROVED_")
                   for r in group if r["reaction_id"] in full(disabled))
        assert sum(r["functional_annotation_status"] == "DIRECT_CHEMISTRY" for r in group) == 20
    # The two source cycles have the same ordered functional pattern and
    # reference activity classes; numerical rate constants are not compared.
    for first, second in list(zip(range(13, 29), range(74, 90))) + list(zip(range(60, 68), range(118, 126))):
        left, right = by[next(iter(full([first])))], by[next(iter(full([second])))]
        for field in ("level_c_functional_contexts", "functional_annotation_status", "reference_activity", "mechanistic_reaction_type"):
            assert left[field] == right[field], (first, second, field)
    assert {r["reaction_id"] for r in v2 if r["reaction_family_id"] == "RFAM_014" and r["functional_annotation_status"] == "SHARED_JUNCTION"} == full([308, 327])
    assert all(by[rid]["functional_annotation_status"] == "DIRECT_CHEMISTRY" for rid in full([910, 957]))
    junctions = {207: "RS_activation;RS_charging", 208: "RS_activation;RS_charging",
                 249: "RS_activation;RS_charging", 250: "RS_activation;RS_charging",
                 308: "ELONG_energy_coupling;RECYCLE_component_release",
                 327: "ELONG_energy_coupling;RECYCLE_component_release"}
    assert {r["reaction_id"] for r in v2 if r["functional_annotation_status"] == "SHARED_JUNCTION"} == full(junctions)
    for number, stage in junctions.items():
        row = by[next(iter(full([number])))]
        assert row["level_c_functional_contexts"] == stage and row["level_c_primary_stage"] == ""
        assert row["human_functional_review_required"] == "false"
    assert len(queue) == 0 and not queue_ids

    # Check the local chemical events behind the labels, including RF2's
    # source equations independently of the RF1 family name.
    equations = {
        292: ({"EFG_GDP"}, {"EFG", "GDP"}),
        294: ({"EFG", "GTP"}, {"EFG_GTP"}),
        308: ({"RS50S_EFG_GDP"}, {"EFG_GDP", "RS50S"}),
        910: ({"termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP"},
              {"RS50S_tRNAGlyGCC_RRF_EFG_GDP", "termRS30S_mRNA"}),
        338: ({"CK_CP_ADP"}, {"CK_Cr_ATP"}),
        363: ({"NDK_GDP_ATP"}, {"NDK_GTP_ADP"}),
        388: ({"MK_ATP_AMP"}, {"MK_ADP_ADP"}),
        407: ({"PPiase_PPi"}, {"PPiase_PO4_PO4"}),
        445: ({"GTP", "IF2"}, {"IF2_GTP"}),
        449: ({"IF2_GTP", "fMettRNAfMetCAU"}, {"IF2_GTP_fMettRNAfMetCAU"}),
        455: ({"RS70S"}, {"RS30S", "RS50S"}),
        796: ({"RF1", "elRS70SAUAA0004_Pept0003tRNAGlyGCC"},
              {"elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1"}),
        798: ({"elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1"},
              {"Pept0003", "termRS70SUAA0004_tRNAGlyGCC_RF1"}),
        799: ({"termRS70SUAA0004_tRNAGlyGCC_RF1"},
              {"RF1", "termRS70SUAA0004_tRNAGlyGCC"}),
        811: ({"RF2", "elRS70SAUAA0004_Pept0003tRNAGlyGCC"},
              {"elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2"}),
        813: ({"elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2"},
              {"Pept0003", "termRS70SUAA0004_tRNAGlyGCC_RF2"}),
        814: ({"termRS70SUAA0004_tRNAGlyGCC_RF2"},
              {"RF2", "termRS70SUAA0004_tRNAGlyGCC"}),
    }
    for number, (reactants, products) in equations.items():
        row = by[next(iter(full([number])))]
        assert set(json.loads(row["reactants_json"])) == reactants, number
        assert set(json.loads(row["products_json"])) == products, number

    # Human-approved initiation rules are checked independently of the
    # builder's graph routine and CellDesigner association/dissociation type.
    initiation_fixtures = {
        "INIT_assembly": [457,458,459,460,463,464,469,470,489,490,501,502,505,506],
        "INIT_tRNA_recruitment": [465,466,467,468],
        "INIT_70S_formation": [461,462,485,486],
        "INIT_energy_commitment": [715,716,717,718,721,722,745,746],
        "INIT_factor_release": [539,540,719,720,723,724,725,726,747,748,749,750,751,752,763,764,765,766],
    }
    for stage, numbers in initiation_fixtures.items():
        for rid in full(numbers):
            assert by[rid]["level_c_functional_contexts"] == stage, (rid, stage)
            assert by[rid]["functional_annotation_status"] == "DIRECT_CHEMISTRY", rid
            assert by[rid]["direct_chemistry_rule"].startswith("APPROVED_"), rid
    initiation = [r for r in v2 if r["reaction_family_id"] in {"RFAM_025", "RFAM_026"}]
    assert len(initiation) == 198
    assert all(r["functional_annotation_status"] == "DIRECT_CHEMISTRY" and r["is_functional_anchor"] == "true" for r in initiation)
    assert not any(r["reaction_id"] in queue_ids for r in initiation)
    expected_init = {
        "RFAM_025": {"INIT_assembly": 52, "INIT_tRNA_recruitment": 20, "INIT_70S_formation": 10,
                     "INIT_energy_commitment": 8, "INIT_factor_release": 28},
        "RFAM_026": {"INIT_assembly": 60, "INIT_tRNA_recruitment": 20},
    }
    for family, counts in expected_init.items():
        actual = Counter(r["level_c_functional_contexts"] for r in initiation if r["reaction_family_id"] == family)
        assert dict(actual) == counts, (family, actual)
    for row in initiation:
        left = set(json.loads(row["reactants_json"]))
        right = set(json.loads(row["products_json"]))
        stage = row["level_c_functional_contexts"]
        join = (("RS50S" in left and any(s.startswith("RS30S") for s in left) and any(s.startswith("RS70S") for s in right)) or
                ("RS50S" in right and any(s.startswith("RS30S") for s in right) and any(s.startswith("RS70S") for s in left)))
        def bound_tRNA(side):
            return any("fMettRNAfMetCAU" in s and s.startswith(("RS30S", "RS70S", "elRS70S")) for s in side)
        tRNA_change = bound_tRNA(left) != bound_tRNA(right)
        def any_name(side, text):
            return any(text in s for s in side)
        energy = ((any_name(left, "IF2_GTP") and any_name(right, "IF2_GDP_PO4")) or
                  (any_name(right, "IF2_GTP") and any_name(left, "IF2_GDP_PO4")) or
                  (any_name(left, "IF2_GDP_PO4") and "PO4" in right and any_name(right, "IF2_GDP")) or
                  (any_name(right, "IF2_GDP_PO4") and "PO4" in left and any_name(left, "IF2_GDP")))
        if stage == "INIT_70S_formation":
            assert join, row["reaction_id"]
        elif stage == "INIT_energy_commitment":
            assert not join and energy, row["reaction_id"]
        elif stage == "INIT_tRNA_recruitment":
            assert not join and not energy and tRNA_change, row["reaction_id"]
        elif stage == "INIT_factor_release":
            assert not join and not energy and not tRNA_change
            assert any(s in {"IF1", "IF3", "IF2_GDP"} for s in left | right), row["reaction_id"]
            assert any(s.startswith(("RS70S", "elRS70S")) and
                       any(token in s for token in ("fMettRNAfMetCAU", "_mRNA", "IF2_GDP"))
                       for s in left | right), row["reaction_id"]
        else:
            assert stage == "INIT_assembly" and not join and not energy and not tRNA_change, row["reaction_id"]

    non_target_fields = ("reaction_id", "reaction_family_id", "level_c_functional_contexts",
                         "functional_annotation_status", "reference_activity", "reactants_json",
                         "products_json", "official_parameter_value", "official_parameter_id")
    non_target_records = [{key: r[key] for key in non_target_fields} for r in v2
                          if r["reaction_family_id"] not in FINAL_FAMILIES]
    non_target_digest = hashlib.sha256(json.dumps(non_target_records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    assert non_target_digest == NON_TARGET_SCIENTIFIC_SHA256, "non-target scientific fingerprint changed"

    link_keys = {(r["specific_intermediate"], r["source_family"], r["target_family"]) for r in links}
    assert ("GlyRS_AMP", "RFAM_010", "RFAM_006") in link_keys
    assert ("MetRS_AMP", "RFAM_012", "RFAM_008") in link_keys
    assert len(links) == 22
    assert manifest["artifact_sha256"]["reaction_cross_family_links_v2.csv"] == "7d3551b04a1c7f2a229fec6f2e3656db45da7836c34925f6cb690f85d4b28a50"
    assert all(r["inference_scope"] == "MECHANISTIC_CONNECTIVITY_ONLY" for r in links)
    assert len({r["reaction_id"] for r in queue}) == len(queue)
    assert all(r["reason_for_review"] and r["reaction_id"] in by for r in queue)
    assert all("AUTO_RESOLVED" not in reason for r in queue for reason in r["reason_for_review"].split(";"))
    assert len(families) == 36

    # Compare actual source stoichiometry, functional stage and parameter
    # topology across the Gly/Met structures, including RFAM_011/012.
    def normalized_side(row, key):
        result = []
        for name, value in json.loads(row[key]).items():
            name = (name.replace("GlytRNAGlyGCC", "AAtRNAX").replace("MettRNAfMetCAU", "AAtRNAX")
                        .replace("tRNAGlyGCC", "tRNAX").replace("tRNAfMetCAU", "tRNAX")
                        .replace("GlyRS", "AARS").replace("MetRS", "AARS")
                        .replace("GlyAMP", "AAAMP").replace("MetAMP", "AAAMP")
                        .replace("Gly", "AA").replace("Met", "AA"))
            result.append((name, value))
        return tuple(sorted(result))
    gly_fams = {"RFAM_005", "RFAM_006", "RFAM_009", "RFAM_010"}
    met_fams = {"RFAM_007", "RFAM_008", "RFAM_011", "RFAM_012"}
    met_signatures = defaultdict(list)
    for row in v2:
        if row["reaction_family_id"] in met_fams:
            met_signatures[(normalized_side(row, "reactants_json"), normalized_side(row, "products_json"))].append(row)
    symmetry_count = 0
    for row in v2:
        if row["reaction_family_id"] in gly_fams:
            matches = met_signatures[(normalized_side(row, "reactants_json"), normalized_side(row, "products_json"))]
            assert len(matches) == 1, row["reaction_id"]
            mirror = matches[0]
            assert row["level_c_functional_contexts"] == mirror["level_c_functional_contexts"]
            assert row["reference_activity"] == mirror["reference_activity"]
            symmetry_count += 1
    assert symmetry_count == 52
    assert manifest["functional_annotation_status_counts"] == {status: sum(r["functional_annotation_status"] == status for r in v2)
                                                             for status in ("DIRECT_CHEMISTRY", "GRAPH_PROPAGATED",
                                                                            "HUMAN_REVIEW_REQUIRED", "REFERENCE_DISABLED",
                                                                            "SHARED_JUNCTION")}
    assert manifest["human_functional_review_queue"] == len(queue)
    assert manifest["functional_annotation_unresolved"] == sum(r["functional_annotation_status"] == "HUMAN_REVIEW_REQUIRED" for r in v2)
    assert manifest["functional_annotation_status_counts"] == {"DIRECT_CHEMISTRY": 492, "GRAPH_PROPAGATED": 50, "HUMAN_REVIEW_REQUIRED": 0, "REFERENCE_DISABLED": 420, "SHARED_JUNCTION": 6}
    assert manifest["functional_annotation_review_complete"] is True
    assert manifest["functional_annotation_unresolved"] == manifest["human_functional_review_queue"] == 0
    assert manifest["reduction_scientific_review"] == {"pending": 968, "total": 968}
    assert not any(key in row for row in v2 for key in ("qssa_approved", "fast_equilibrium_approved", "lumping_approved", "deletion_approved"))
    print("PASS: 968 unique source-identical reactions; 290 symmetric exact reverse channels")
    print("PASS: hard chemistry priority; double-zero edges never functional anchors")
    print("PASS: RFAM_005-010 approved regressions; RFAM_011/012 Gly/Met source and parameter-topology symmetry (52/52)")
    print("PASS: RFAM_025/026 reviewed initiation rules and reverse symmetry")
    print("PASS: nine prior reviewed families = 98 direct rules; RFAM_002/004/014 final reviewed patterns and source equations")
    print("PASS: six approved shared junctions; non-target scientific fingerprint unchanged")
    print(f"PASS: {len(links)} specific-intermediate cross-family links; {len(queue)} live functional-review rows")
    print("PASS: reduction scientific review remains 968/968 PENDING; v0/v1 retained")
    print("STATUS COUNTS:", json.dumps(manifest["functional_annotation_status_counts"], sort_keys=True))


if __name__ == "__main__":
    main()
