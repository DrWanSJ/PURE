#!/usr/bin/env python3
"""Independent PNAS-wide evidence verifier; never makes kinetic decisions.

The generator is deliberately not imported. Source IDs, stoichiometry, reaction
rates and production/consumption are independently reconstructed from frozen
SBML and author inputs. Negative controls invoke the same semantic predicates
as production checks, independently of artifact hashes, on temporary copies.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIT = "models/pnas2017_full_reference/audit/reduction_evidence_v0"
PRE_SHA = "b20d782edcef9a7a70bf3848acd2dbd8c240303e3507cc927f0041c56bc4969b"
SOURCE_HEAD = "3e22aeeb6124e2ad7d3373e0cf056383bf9c8c1e"
AUTHOR = "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/"
CLASS_COUNTS = {"I": 42, "II-A": 57, "II-B": 91, "III": 22, "C": 29}
DOC_NAMES = [
    "01_amino_acid_activation", "02_trna_aminoacylation", "03_initiator_trna_formylation",
    "04_initiation_factor_preparation", "05_ribosome_mrna_initiation_assembly",
    "06_ef_tu_ternary_complex_delivery", "07_ef_g_nucleotide_cycle",
    "08_peptidyl_trna_ribosome_transitions", "09_rf1_rf2_peptide_release",
    "10_rf3_assisted_termination", "11_ribosome_recycling",
    "12_creatine_kinase_energy_regeneration", "13_nucleotide_diphosphate_kinase_exchange",
    "14_adenylate_kinase_exchange", "15_pyrophosphate_hydrolysis",
    "16_shared_small_molecule_transitions",
]


class EvidenceError(AssertionError):
    def __init__(self, code: str, detail: str):
        self.code = code
        super().__init__(f"{code}: {detail}")


def require(condition, code, detail):
    if not condition:
        raise EvidenceError(code, str(detail))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=list(rows[0]))
        out.writeheader()
        out.writerows(rows)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def split(value):
    if not value or value.startswith("N/A"):
        return set()
    if value.startswith("["):
        return set(json.loads(value))
    return set(value.split(";"))


def is_na(value):
    return str(value).startswith("N/A")


def truth(value):
    return str(value).lower() in {"true", "1", "yes"}


def close(value, expected, label, tolerance=1e-9):
    try:
        actual = float(value)
    except (ValueError, TypeError):
        raise EvidenceError("NUMERICAL_VALUE", f"{label}: expected {expected}, got {value}")
    require(math.isfinite(actual), "NONFINITE", label)
    error = abs(actual - float(expected)) / max(1.0, abs(actual), abs(float(expected)))
    require(error <= tolerance, "NUMERICAL_VALUE", f"{label}: {actual} vs {expected}; scaled error {error}")


def coverage(rows, key, ids, label):
    values = [row[key] for row in rows]
    require(len(values) == len(ids), "ROW_COUNT", f"{label}: {len(values)} != {len(ids)}")
    require(len(set(values)) == len(values), "DUPLICATE_ID", label)
    require(set(values) == set(ids), "ID_SET", f"{label}: missing {set(ids)-set(values)}, extra {set(values)-set(ids)}")


def source_digest(data, expected, label):
    require(sha(data) == expected, "SOURCE_HASH", label)


def prereg_semantics(pre):
    require(pre["source_head"] == SOURCE_HEAD, "SOURCE_HEAD", pre["source_head"])
    require(pre["canonical_sbml_sha256"] == pre["input_sha256"][pre["canonical_sbml_path"]], "DECLARED_SBML_HASH", "canonical declaration differs from registered input")
    require(pre["domain"] == "AUTHOR_REFERENCE_CONDITION_ONLY", "DOMAIN", pre["domain"])
    require(pre["descriptive_bands"]["mapping_to_decision"] is None, "NO_DECISION", "descriptive thresholds must not select reductions")


def verify_inputs(root, pre):
    prereg_semantics(pre)
    eol_only = []
    for rel, expected in pre["input_sha256"].items():
        data = (root / rel).read_bytes()
        if sha(data) == expected:
            continue
        # Only the historically observed Markdown CRLF checkout variation is
        # accepted, and only against its frozen Git blob, never arbitrary text.
        require(rel == "docs/reduction/aminoacylation_qssa_quick_reference.md", "SOURCE_HASH", rel)
        blob = subprocess.check_output(["git", "show", f"{SOURCE_HEAD}:{rel}"], cwd=root)
        source_digest(blob, pre["protected_git_blob_sha256"][rel], rel + " frozen Git blob")
        require(data.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), "SOURCE_HASH", rel)
        require(expected in {sha(blob), sha(blob.replace(b"\r\n", b"\n")), sha(blob.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))}, "SOURCE_HASH", rel + " registered checkout representation")
        eol_only.append(rel)
    for rel, expected in pre["protected_git_blob_sha256"].items():
        blob = subprocess.check_output(["git", "show", f"{SOURCE_HEAD}:{rel}"], cwd=root)
        source_digest(blob, expected, rel + " frozen Git blob")
    return eol_only


def canonical(root, pre):
    tree = ET.parse(root / pre["canonical_sbml_path"])
    ns = {"s": "http://www.sbml.org/sbml/level2/version4", "m": "http://www.w3.org/1998/Math/MathML"}
    model = tree.getroot().find("s:model", ns)
    species = [e.attrib["id"] for e in model.find("s:listOfSpecies", ns)]
    reactions = {}
    for element in model.find("s:listOfReactions", ns):
        sides = []
        for side in ("listOfReactants", "listOfProducts"):
            values = {}
            container = element.find("s:" + side, ns)
            if container is not None:
                for reference in container:
                    literal = reference.find("s:stoichiometryMath/m:math/m:cn", ns)
                    stoich = float(literal.text) if literal is not None else float(reference.attrib.get("stoichiometry", "1"))
                    sid = reference.attrib["species"]
                    values[sid] = values.get(sid, 0) + stoich
            sides.append(values)
        reactions[element.attrib["id"]] = tuple(sides)
    require(len(species) == len(set(species)) == 241, "SOURCE_SPECIES_COUNT", len(species))
    require(len(reactions) == 968, "SOURCE_REACTION_COUNT", len(reactions))
    require(reactions["re0000000414"][1].get("PO4") == 2, "LITERAL_STOICHIOMETRY", "PPi hydrolysis coefficient")
    return species, reactions


def exact_reverse(reactions):
    signatures = defaultdict(list)
    for rid, (left, right) in reactions.items():
        signatures[(tuple(sorted(left.items())), tuple(sorted(right.items())))].append(rid)
    pairs = set()
    for signature, ids in signatures.items():
        reverse = signature[::-1]
        if reverse in signatures and reverse != signature:
            require(len(ids) == len(signatures[reverse]) == 1, "AMBIGUOUS_REVERSE", ids)
            pairs.add(tuple(sorted((ids[0], signatures[reverse][0]))))
    require(len(pairs) == 290, "REVERSE_COUNT", len(pairs))
    return pairs


def classifications(text):
    pattern = r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*(I|II-A|II-B|III|C)\*\*\s*\|"
    entries = re.findall(pattern, text, re.M)
    require(len(entries) == len(dict(entries)) == 241, "CLASS_COVERAGE", len(entries))
    require(dict(Counter(c for _, c in entries)) == CLASS_COUNTS, "CLASS_COUNTS", Counter(c for _, c in entries))
    return dict(entries)


def check_classes(rows, classes):
    for row in rows:
        require(row["information_contract_class"] == classes[row["species_id"]], "SPECIES_CLASS", row["species_id"])
        require(truth(row["protected_output"]) == (classes[row["species_id"]] == "I"), "PROTECTED_OUTPUT", row["species_id"])


def check_decisions(rows):
    require(len(rows) == 968 and all(row["decision_status"] == "PENDING" for row in rows), "HUMAN_DECISION", "all 968 scientific decisions must remain PENDING")


def check_boxes(text):
    require(not re.search(r"^\s*-\s*\[[xX]\]", text, re.M), "PRESELECTED_BOX", "process choice selected")
    require(len(re.findall(r"^\s*-\s*\[ \]", text, re.M)) == 96, "BOX_COUNT", "expected 96 unselected process choices")


def process_cards(text, pre):
    # The frozen review also contains a decision-record section without a card.
    sections = [section for section in re.split(r"^## ", text, flags=re.M)[1:]
                if re.search(r"^Original combined reaction IDs:", section, re.M)]
    require(len(sections) == 16, "PROCESS_COUNT", len(sections))
    parsed = []
    for index, section in enumerate(sections, 1):
        name = section.splitlines()[0]
        ids = re.search(r"^Original combined reaction IDs:(.*)$", section, re.M)
        states = re.search(r"^Candidate complex/intermediate IDs:(.*)$", section, re.M)
        parsed.append({"process_id": f"P{index:02d}", "name": name, "reaction_ids": re.findall(r"`([^`]+)`", ids.group(1)) if ids else [], "candidate_state_ids": re.findall(r"`([^`]+)`", states.group(1)) if states else []})
    require(parsed == pre["process_cards"], "PROCESS_SOURCE", "preregistered process cards must exactly match source Markdown")
    return parsed


def check_reverse_rows(rows, pairs, reactions):
    actual = []
    for row in rows:
        f, r = row["forward_reaction_id"], row["reverse_reaction_id"]
        require((f, r) in pairs or (r, f) in pairs, "REVERSE_PARTNER", f"{f}/{r}")
        require(reactions[f] == reactions[r][::-1], "REVERSE_PARTNER", f"{f}/{r}")
        actual.append(tuple(sorted((f, r))))
    require(len(actual) == 290 and len(set(actual)) == 290 and set(actual) == pairs, "REVERSE_SET", "pair set differs from independently reconstructed source")


def check_pool_ids(rows, pools):
    for row in rows:
        sid = row["species_id"]
        for pool in split(row["known_pool_ids"]):
            require(pool in pools and sid in pools[pool], "FABRICATED_POOL", f"{sid}: {pool}")
        if row["pool_membership_status"] == "UNRESOLVED":
            require(all(is_na(row[k]) for k in ("free_total_ratio_min", "free_total_ratio_median", "free_total_ratio_max", "max_bound_fraction")), "MISSING_POOL_VALUE", sid)


def qss_sample(row, floor):
    production, consumption, dzdt = map(float, (row["production_flux"], row["consumption_flux"], row["dzdt"]))
    close(dzdt, production - consumption, "QSS production minus consumption")
    require(production >= 0 and consumption >= 0, "FLUX_SIGN", row["species_id"])
    denominator = production + consumption
    if denominator <= floor:
        require(not truth(row["informative"]) and is_na(row["qss_defect"]) and "LOW_FLUX" in row["reason"], "ZERO_QSS", row["species_id"])
    else:
        require(truth(row["informative"]), "QSS_INFORMATIVE", row["species_id"])
        close(row["qss_defect"], abs(dzdt) / denominator, "QSS defect")


def pair_sample(row, floor, disabled):
    vf, vr = float(row["vf"]), float(row["vr"])
    exchange = abs(vf) + abs(vr)
    close(row["exchange_flux"], exchange, "pair exchange")
    close(row["net_flux"], vf - vr, "pair net")
    if disabled:
        require(not truth(row["informative"]) and is_na(row["equilibrium_defect"]) and "REFERENCE_DIRECTION_DISABLED" in row["reason"], "DISABLED_EQUILIBRIUM", row["pair_id"])
    elif exchange <= floor:
        require(not truth(row["informative"]) and is_na(row["equilibrium_defect"]) and "LOW_FLUX" in row["reason"], "ZERO_EQUILIBRIUM", row["pair_id"])
    else:
        require(truth(row["informative"]), "PAIR_INFORMATIVE", row["pair_id"])
        close(row["equilibrium_defect"], abs(vf-vr) / exchange, "equilibrium defect")


def source_numerics(root, pre, species, reactions):
    initial = {r["Name"]: float(r["Value"]) for r in read_csv(root / (AUTHOR + "fMGG_synthesis_initial_values.csv"))}
    params = {r["Name"]: float(r["Value"]) for r in read_csv(root / (AUTHOR + "fMGG_synthesis_parameters.csv"))}
    trajectory = read_csv(root / pre["trajectory"]["path"])
    require(len(trajectory) == 200, "TRAJECTORY_COUNT", len(trajectory))
    time_col = next(key for key in ("time", "Time", "time_seconds") if key in trajectory[0])
    times = np.array([0.0] + [float(r[time_col]) for r in trajectory])
    require(np.allclose(times[1:], np.logspace(-4, 3, 200), rtol=1e-12, atol=1e-14), "AUTHOR_GRID", times[[1, -1]])
    x = np.array([[initial[s] for s in species]] + [[float(row.get(s, row.get(f"[{s}]", "nan"))) for s in species] for row in trajectory])
    require(np.isfinite(x).all(), "TRAJECTORY_STATE", "missing or nonfinite source state")
    rids = list(reactions)
    si = {s: i for i, s in enumerate(species)}
    rates = np.zeros((len(times), len(rids)))
    matrix = np.zeros((len(species), len(rids)))
    for j, rid in enumerate(rids):
        rates[:, j] = params[rid + "_k1"]
        for sid, coefficient in reactions[rid][0].items():
            rates[:, j] *= x[:, si[sid]] ** coefficient
            matrix[si[sid], j] -= coefficient
        for sid, coefficient in reactions[rid][1].items():
            matrix[si[sid], j] += coefficient
    # Split by contribution sign, including unmodified tiny signed roundoff rates.
    production = np.zeros_like(x)
    consumption = np.zeros_like(x)
    for j in range(len(rids)):
        contribution = rates[:, j, None] * matrix[None, :, j]
        production += np.maximum(contribution, 0)
        consumption += np.maximum(-contribution, 0)
    return times, x, rates, matrix, production, consumption, params


def independent_numerical_checks(root, pre, species, reactions, numeric):
    """A separate MathML interpreter plus central differences, without generator imports."""
    times, x, rates, matrix, _, _, params = numeric
    si = {s: i for i, s in enumerate(species)}
    ns = {"s": "http://www.sbml.org/sbml/level2/version4", "m": "http://www.w3.org/1998/Math/MathML"}
    effective = ET.parse(root / pre["effective_sbml"]["path"])
    effective_reactions = effective.getroot().find("s:model/s:listOfReactions", ns)
    reconstructed = np.zeros_like(rates)

    def evaluate(node, environment):
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "math":
            return evaluate(node[0], environment)
        if tag == "ci":
            return environment[node.text.strip()]
        if tag == "cn":
            return float(node.text)
        require(tag == "apply", "MATHML_SUPPORTED", tag)
        operator = node[0].tag.rsplit("}", 1)[-1]
        values = [evaluate(child, environment) for child in node[1:]]
        if operator == "times":
            result = 1.0
            for value in values:
                result = result * value
            return result
        if operator == "power":
            return values[0] ** values[1]
        if operator == "plus":
            return sum(values)
        if operator == "minus":
            return -values[0] if len(values) == 1 else values[0] - values[1]
        if operator == "divide":
            return values[0] / values[1]
        raise EvidenceError("MATHML_SUPPORTED", operator)

    rids = list(reactions)
    require([element.attrib["id"] for element in effective_reactions] == rids, "EFFECTIVE_IDS", "effective reaction order/source IDs")
    for j, element in enumerate(effective_reactions):
        law = element.find("s:kineticLaw", ns)
        environment = {s: x[:, index] for s, index in si.items()}
        environment.update({p.attrib["id"]: float(p.attrib["value"]) for p in law.findall("s:listOfParameters/s:parameter", ns)})
        close(environment["k1"], params[rids[j]+"_k1"], "effective author parameter")
        reconstructed[:, j] = evaluate(law.find("m:math", ns), environment)
    scaled = np.abs(reconstructed-rates) / np.maximum(1, np.maximum(np.abs(reconstructed), np.abs(rates)))
    rate_error = float(np.max(scaled))
    require(rate_error <= pre["numeric"]["rate_crosscheck_max_scaled_abs_error"], "RATE_CROSSCHECK", rate_error)

    def rhs(state):
        values = np.array([params[r+"_k1"] for r in rids])
        for j, rid in enumerate(rids):
            for sid, coefficient in reactions[rid][0].items():
                values[j] *= state[si[sid]] ** coefficient
        return matrix @ values

    jacobians = {}
    jac_error = 0.0
    for ti in (0, 1, 50, 100, 150, 200):
        state = x[ti]
        derivative = np.zeros((968, 241))
        for j, rid in enumerate(rids):
            left = reactions[rid][0]
            for sid, coefficient in left.items():
                value = params[rid+"_k1"] * coefficient
                for other, power in left.items():
                    value *= state[si[other]] ** (power - (1 if other == sid else 0))
                derivative[j, si[sid]] = value
        analytic = matrix @ derivative
        finite = np.zeros_like(analytic)
        for j in range(241):
            step = 1e-4 * max(1.0, abs(state[j]))
            plus, minus = state.copy(), state.copy()
            plus[j] += step
            minus[j] -= step
            finite[:, j] = (rhs(plus) - rhs(minus)) / (2 * step)
        err = np.abs(finite-analytic) / np.maximum(1, np.maximum(np.abs(finite), np.abs(analytic)))
        jac_error = max(jac_error, float(np.max(err)))
        jacobians[ti] = analytic
    require(jac_error <= pre["numeric"]["jacobian_crosscheck_max_scaled_abs_error"], "JACOBIAN_CROSSCHECK", jac_error)
    return {"effective_mathml_vs_author_mass_action_max_scaled_error": rate_error,
            "analytic_vs_central_difference_jacobian_max_scaled_error": jac_error,
            "jacobian_sample_indices": [0, 1, 50, 100, 150, 200],
            "finite_difference_state_columns": 241}, jacobians


def summary(row, fields, values, label):
    values = np.asarray(values, dtype=float)
    if not len(values):
        require(all(is_na(row[field]) for field in fields), "UNAVAILABLE_SUMMARY", label)
        return
    stats = {"min": np.min, "median": np.median, "max": np.max,
             "p05": lambda a: np.quantile(a, .05), "p95": lambda a: np.quantile(a, .95)}
    for field in fields:
        key = field.rsplit("_", 1)[-1]
        close(row[field], stats[key](values), label + ":" + field)


def verify_tables(root, audit, pre):
    species, reactions = canonical(root, pre)
    pairs = exact_reverse(reactions)
    rows = {name: read_csv(audit / (name + ".csv")) for name in (
        "reaction_evidence", "state_evidence", "reverse_pair_evidence", "process_timescale_evidence",
        "reaction_pool_metrics", "state_qss_timeseries", "reverse_pair_equilibrium_timeseries")}
    coverage(rows["reaction_evidence"], "reaction_id", reactions, "reactions")
    coverage(rows["state_evidence"], "species_id", species, "states")
    check_reverse_rows(rows["reverse_pair_evidence"], pairs, reactions)
    classes = classifications((root / "docs/reduction/species_information_contract_detailed.md").read_text(encoding="utf-8"))
    check_classes(rows["state_evidence"], classes)
    review = (root / "docs/reduction/human_reduction_review.md").read_text(encoding="utf-8")
    check_boxes(review)
    cards = process_cards(review, pre)
    decisions = read_csv(root / "docs/reduction/reduction_decisions.csv")
    check_decisions(decisions)
    decision_by_id = {r["sbml_reaction_id"]: r for r in decisions}
    annotations = {r["reaction_id"]: r for r in read_csv(root / "docs/reduction/reaction_level_annotation_v2.csv")}
    pools = pre["registered_pools"]["membership"]
    source_pools = read_json(root / pre["registered_pools"]["source"])["pools"]
    for pool, members in pools.items():
        require(source_pools.get(pool) == members, "FABRICATED_POOL", pool)
    check_pool_ids(rows["state_evidence"], pools)
    coverage(rows["process_timescale_evidence"], "process_id", [p["process_id"] for p in cards], "processes")
    times, x, rates, matrix, prod, cons, params = source_numerics(root, pre, species, reactions)
    ri, si = {r: i for i, r in enumerate(reactions)}, {s: i for i, s in enumerate(species)}
    time_index = {float(t): i for i, t in enumerate(times)}
    floor = pre["numeric"]["flux_information_floor"]
    denominator_floor = pre["numeric"]["concentration_denominator_floor"]
    extents = np.sum((rates[1:] + rates[:-1]) * np.diff(times)[:, None] / 2, axis=0)
    pair_by_id = {r["pair_id"]: r for r in rows["reverse_pair_evidence"]}
    require(len(pair_by_id) == 290, "DUPLICATE_PAIR_ID", "pair IDs")
    partner = {}
    for p in rows["reverse_pair_evidence"]:
        f, r = p["forward_reaction_id"], p["reverse_reaction_id"]
        partner[f] = (r, p["pair_id"])
        partner[r] = (f, p["pair_id"])
    annotation_fields = {"level_a_module": "level_a_module_candidates", "level_b_subsystems": "level_b_subsystem_candidates", "reaction_family_id": "reaction_family_id", "level_c_stage": "level_c_primary_stage", "mechanistic_reaction_type": "mechanistic_reaction_type", "reference_activity": "reference_activity", "contract_classes_touched": "contract_classes_touched", "conservation_families_touched": "conservation_families_touched", "protected_species_touched": "protected_species_touched", "original_annotation_pool_ids": "protected_pool_touched"}
    candidates = set().union(*(set(card["candidate_state_ids"]) for card in cards))
    for row in rows["reaction_evidence"]:
        rid = row["reaction_id"]
        annotation, decision = annotations[rid], decision_by_id[rid]
        for target, source in annotation_fields.items():
            require(row[target] == annotation[source], "ANNOTATION_DRIFT", f"{rid}: {target}")
        for target, source in (("candidate_label_existing", "candidate_label"), ("human_decision_status", "decision_status")):
            require(row[target] == decision[source], "HUMAN_DECISION", f"{rid}: {target}")
        require(truth(row["human_review_required"]), "NO_DECISION", rid)
        require(row["official_parameter_id"] == rid + "_k1", "PARAMETER_ID", rid)
        close(row["official_parameter_value"], params[rid + "_k1"], rid)
        for key, expected in zip(("reactants_json", "products_json"), reactions[rid]):
            payload = json.loads(row[key])
            if isinstance(payload, list):
                payload = {p["species_id"]: float(p["stoichiometry"]) for p in payload}
            require(payload == expected, "EVENT_STOICHIOMETRY", rid)
        if rid in partner:
            require((row["reverse_partner_id"], row["reverse_pair_id"]) == partner[rid], "REVERSE_PARTNER", rid)
            require(row["pair_evidence_id"] == partner[rid][1], "PAIR_LINK", rid)
        else:
            require("NO_EXACT_REVERSE_PAIR" in row["equilibrium_metric_status"], "UNPAIRED_NA", rid)
        require("STATE_LEVEL" in row["qss_metric_status"], "REACTION_QSS", rid)
        require("EXACT_EVENT_STOICHIOMETRY_KNOWN" in row["ledger_evidence_status"] and "PASS" not in row["ledger_evidence_status"], "LEDGER_STATUS", rid)
        require("UNRESOLVED" in row["bound_moiety_status"], "BOUND_MOIETY", rid)
        expected_processes = {p["process_id"] for p in cards if rid in p["reaction_ids"]}
        require(split(row["process_ids"]) == expected_processes and bool(expected_processes), "PROCESS_LINK", rid)
        touched = set(reactions[rid][0]) | set(reactions[rid][1])
        require(split(row["state_evidence_ids"]) == touched, "STATE_LINK", rid)
        require(split(row["candidate_state_ids"]) == touched & candidates, "CANDIDATE_LINK", rid)
        require(row["reaction_family_id"] and row["qss_metric_status"] and row["equilibrium_metric_status"], "EVIDENCE_LINK", rid)
        j = ri[rid]
        close(row["rate_median"], np.median(rates[1:, j]), rid + " rate median")
        close(row["rate_max_abs"], np.max(np.abs(rates[1:, j])), rid + " rate maximum")
        close(row["directed_extent"], extents[j], rid + " extent")
        close(row["net_tracked_particle_delta"], np.sum(matrix[:, j]), rid + " particle delta")
    qss_by_state = defaultdict(list)
    observed_qss = set()
    for row in rows["state_qss_timeseries"]:
        sid, time = row["species_id"], float(row["time"])
        require(sid in si and time in time_index, "SAMPLE_SOURCE", f"{sid}/{time}")
        require((sid, time) not in observed_qss, "DUPLICATE_SAMPLE", f"{sid}/{time}")
        observed_qss.add((sid, time))
        qss_sample(row, floor)
        ti, sj = time_index[time], si[sid]
        close(row["production_flux"], prod[ti, sj], sid + " P")
        close(row["consumption_flux"], cons[ti, sj], sid + " C")
        close(row["dzdt"], prod[ti, sj] - cons[ti, sj], sid + " dzdt")
        require(("SUPPLEMENTAL" in row["sampling_role"]) == (ti == 0), "SAMPLING_ROLE", f"{sid}/{time}")
        if ti:
            qss_by_state[sid].append(row)
    require(len(observed_qss) == 241 * 201, "QSS_GRID_COVERAGE", len(observed_qss))
    for row in rows["state_evidence"]:
        sid, j = row["species_id"], si[row["species_id"]]
        expected_candidate_processes = {card["process_id"] for card in cards if sid in card["candidate_state_ids"]}
        expected_processes = {card["process_id"] for card in cards if any(sid in reactions[rid][0] or sid in reactions[rid][1] for rid in card["reaction_ids"])}
        require(split(row["candidate_process_memberships"]) == expected_candidate_processes, "CANDIDATE_LINK", sid)
        require(split(row["process_memberships"]) == expected_processes, "STATE_PROCESS_LINK", sid)
        require(truth(row["is_candidate_intermediate"]) == bool(expected_candidate_processes), "CANDIDATE_LINK", sid)
        close(row["initial_value"], x[0, j], sid + " initial")
        summary(row, ["trajectory_min", "trajectory_median", "trajectory_max"], x[1:, j], sid)
        samples = qss_by_state[sid]
        defects = [float(s["qss_defect"]) for s in samples if truth(s["informative"])]
        summary(row, ["qss_defect_median", "qss_defect_p95", "qss_defect_max"], defects, sid)
        close(row["qss_informative_fraction"], len(defects) / 200, sid)
        summary(row, ["production_flux_median", "production_flux_max"], prod[1:, j], sid)
        summary(row, ["consumption_flux_median", "consumption_flux_max"], cons[1:, j], sid)
        den = prod[1:, j] + cons[1:, j]
        valid = (den > floor) & (x[1:, j] > denominator_floor)
        summary(row, ["turnover_tau_median", "turnover_tau_p05", "turnover_tau_p95"], np.abs(x[1:, j][valid]) / den[valid], sid)
    pair_samples = defaultdict(list)
    observed_pair = set()
    for row in rows["reverse_pair_equilibrium_timeseries"]:
        pid, time = row["pair_id"], float(row["time"])
        require(pid in pair_by_id and time in time_index, "PAIR_SAMPLE_SOURCE", pid)
        require((pid, time) not in observed_pair, "DUPLICATE_SAMPLE", f"{pid}/{time}")
        observed_pair.add((pid, time))
        p = pair_by_id[pid]
        f, r = p["forward_reaction_id"], p["reverse_reaction_id"]
        require((row["forward_reaction_id"], row["reverse_reaction_id"]) == (f, r), "REVERSE_PARTNER", pid)
        disabled = params[f+"_k1"] == 0 or params[r+"_k1"] == 0
        pair_sample(row, floor, disabled)
        ti = time_index[time]
        close(row["vf"], rates[ti, ri[f]], pid + " vf")
        close(row["vr"], rates[ti, ri[r]], pid + " vr")
        require(("SUPPLEMENTAL" in row["sampling_role"]) == (ti == 0), "SAMPLING_ROLE", pid)
        if ti:
            pair_samples[pid].append(row)
    require(len(observed_pair) == 290 * 201, "PAIR_GRID_COVERAGE", len(observed_pair))
    for row in rows["reverse_pair_evidence"]:
        pid, f, r = row["pair_id"], row["forward_reaction_id"], row["reverse_reaction_id"]
        for key, rid in (("forward_k", f), ("reverse_k", r)):
            close(row[key], params[rid+"_k1"], pid)
        defects = [float(s["equilibrium_defect"]) for s in pair_samples[pid] if truth(s["informative"])]
        summary(row, ["eq_defect_median", "eq_defect_p95", "eq_defect_max"], defects, pid)
        close(row["informative_fraction"], len(defects) / 200, pid)
        for band, key in ((.1, "fraction_delta_below_1e-1"), (.01, "fraction_delta_below_1e-2"), (.001, "fraction_delta_below_1e-3")):
            if defects:
                close(row[key], np.mean(np.asarray(defects) < band), pid + key)
            else:
                require(is_na(row[key]), "UNAVAILABLE_SUMMARY", pid + key)
        close(row["forward_extent"], extents[ri[f]], pid)
        close(row["reverse_extent"], extents[ri[r]], pid)
        close(row["net_extent"], extents[ri[f]] - extents[ri[r]], pid)
        vf, vr = rates[1:, ri[f]], rates[1:, ri[r]]
        for field, values in (("forward_rate_median", vf), ("reverse_rate_median", vr), ("net_rate_median", vf-vr), ("exchange_rate_median", np.abs(vf)+np.abs(vr))):
            close(row[field], np.median(values), pid + field)
        disabled = params[f+"_k1"] == 0 or params[r+"_k1"] == 0
        require(row["pair_reference_status"] == ("REFERENCE_DIRECTION_DISABLED" if disabled else "BOTH_REFERENCE_DIRECTIONS_ENABLED"), "PAIR_ACTIVITY", pid)
        for field, rid in (("reference_activity_forward", f), ("reference_activity_reverse", r)):
            require(row[field] == ("DISABLED_K1_ZERO" if params[rid+"_k1"] == 0 else "ENABLED_K1_NONZERO"), "PAIR_ACTIVITY", pid)
    return rows, species, reactions, pairs, classes, cards, pools, (times, x, rates, matrix, prod, cons, params)


def verify_reaction_ledger(root, rows, species, reactions, classes, numeric):
    """Compare every event delta directly with canonical stoichiometry and frozen ledger."""
    ledger_rel = "models/pnas2017_full_reference/audit/reaction_balance_audit.csv"
    ledger_rows = read_csv(root / ledger_rel)
    coverage(ledger_rows, "sbml_reaction_id", reactions, "frozen event ledger")
    ledger = {row["sbml_reaction_id"]: row for row in ledger_rows}
    resources = {field.removeprefix("net_free_") for field in ledger_rows[0] if field.startswith("net_free_")}
    require(resources <= set(species), "RESOURCE_SOURCE", resources-set(species))
    si, ri = {sid: j for j, sid in enumerate(species)}, {rid: j for j, rid in enumerate(reactions)}
    matrix = numeric[3]
    for row in rows["reaction_evidence"]:
        rid = row["reaction_id"]
        j = ri[rid]
        touched = set(reactions[rid][0]) | set(reactions[rid][1])
        for field, ids in (("resource_delta_json", resources), ("protected_state_delta_json", {s for s in touched if classes[s] == "I"}), ("free_peptide_delta_json", {"Pept0002", "Pept0003"})):
            expected = {sid: float(matrix[si[sid], j]) for sid in ids}
            require(json.loads(row[field]) == expected, "EVENT_RESOURCE_DELTA", rid + "/" + field)
        for sid in resources:
            close(ledger[rid]["net_free_"+sid], matrix[si[sid], j], rid + "/frozen-ledger/" + sid, tolerance=0)
        close(ledger[rid]["net_tracked_particle_count_per_event"], np.sum(matrix[:, j]), rid + "/frozen-ledger/particles", tolerance=0)
        require(row["ledger_record_id"] == rid and row["ledger_source"] == ledger_rel, "LEDGER_LINK", rid)
    return {"reaction_event_rows_checked": len(rows["reaction_evidence"]), "explicit_resource_species_checked": len(resources), "protected_output_count": sum(classes[s] == "I" for s in species), "transformation_validation_status": "NOT_EVALUATED"}


def verify_docs(root):
    folder = root / "docs/reduction/process_quick_reference"
    require({p.stem for p in folder.glob("*.md")} == set(DOC_NAMES), "PROCESS_DOC_COVERAGE", "exact 16 process filenames")
    for name in DOC_NAMES:
        text = (folder / (name + ".md")).read_text(encoding="utf-8")
        require(text.rstrip().endswith("Status: REFERENCE ONLY — NO KINETIC REDUCTION APPROVED."), "DOC_STATUS", name)
        require(not re.search(r"^\s*-\s*\[[xX]\]", text, re.M), "PRESELECTED_BOX", name)
        require(len(re.findall(r"^## [1-8]\.", text, re.M)) == 8, "DOC_SECTIONS", name)
    for name in ("pnas2017_reduction_evidence_method.md", "pnas2017_reduction_quick_reference.md"):
        require((root / "docs/reduction" / name).is_file(), "MISSING_DOC", name)


def verify_pool_metrics(audit, pre, rows, species, reactions, classes, numeric):
    """Rebuild all pool certificates, masks and ratios from source data only."""
    times, x, _, matrix, _, _, params = numeric
    pools = pre["registered_pools"]["membership"]
    si = {sid: j for j, sid in enumerate(species)}
    ti = {float(t): n for n, t in enumerate(times)}
    pool_rows = read_csv(audit / "pool_evidence.csv")
    member_rows = read_csv(audit / "state_pool_metrics.csv")
    sample_rows = read_csv(audit / "pool_timeseries.csv")
    coverage(pool_rows, "pool_id", pools, "pools")
    by_id = {row["pool_id"]: row for row in pool_rows}
    members = {}
    for row in member_rows:
        key = row["species_id"], row["pool_id"]
        require(key not in members, "DUPLICATE_POOL_MEMBER", key)
        members[key] = row
    require(set(members) == {(sid, pid) for pid, ss in pools.items() for sid in ss}, "POOL_MEMBER_COVERAGE", len(members))
    samples = {}
    for row in sample_rows:
        key = row["pool_id"], float(row["time"])
        require(key not in samples, "DUPLICATE_POOL_SAMPLE", key)
        samples[key] = row
    require(set(samples) == {(pid, float(t)) for pid in pools for t in times}, "POOL_SAMPLE_COVERAGE", len(samples))
    enabled = np.array([params[rid+"_k1"] != 0 for rid in reactions])
    floor = pre["numeric"]["concentration_denominator_floor"]
    qualified = {}
    certificates = {}

    def same_metric(actual, expected, label):
        if is_na(expected):
            require(is_na(actual), "POOL_UNAVAILABLE", label)
        else:
            close(actual, expected, label)

    for pid, listed in pools.items():
        row = by_id[pid]
        require(split(row["member_species_ids"]) == set(listed), "FABRICATED_POOL", pid)
        close(row["member_count"], len(listed), pid)
        require(row["member_coefficients"] == "1", "POOL_COEFFICIENT", pid)
        indices = [si[s] for s in listed]
        residual = np.sum(matrix[indices], axis=0)
        reference, unconditional = np.all(residual[enabled] == 0), np.all(residual == 0)
        certificates[pid] = bool(reference)
        require(truth(row["reference_conserved"]) == reference and truth(row["unconditional_conserved"]) == unconditional, "POOL_CERTIFICATE", pid)
        close(row["reference_stoichiometric_residual_max_abs"], max(np.abs(residual[enabled]), default=0), pid)
        close(row["unconditional_stoichiometric_residual_max_abs"], max(np.abs(residual), default=0), pid)
        candidates = [s for s in listed if classes[s] == "I"]
        free = pre["registered_pools"]["explicit_free_counterparts"].get(pid, candidates[0] if len(candidates) == 1 else None)
        require(row["free_species_id"] == (free or "N/A_FREE_COUNTERPART_UNRESOLVED"), "FREE_COUNTERPART", pid)
        qualified[pid] = bool(reference and free is not None)
        total = np.sum(x[:, indices], axis=1)
        negative = np.any(x[:, indices] < 0, axis=1)
        occupancy_mask = reference & ~negative & (total > floor)
        free_mask = occupancy_mask & (free is not None)
        ratio = np.full(len(times), np.nan)
        if free is not None:
            ratio[free_mask] = x[free_mask, si[free]] / total[free_mask]
        close(row["total_initial"], total[0], pid)
        summary(row, ["total_min", "total_median", "total_max"], total[1:], pid)
        ratios = ratio[1:][free_mask[1:]]
        summary(row, ["free_total_ratio_min", "free_total_ratio_median", "free_total_ratio_max"], ratios, pid)
        same_metric(row["max_bound_fraction"], np.max(1-ratios) if len(ratios) else "N/A", pid)
        close(row["primary_sample_count"], 200, pid)
        close(row["informative_fraction"], np.mean(free_mask[1:]), pid)
        close(row["occupancy_informative_fraction"], np.mean(occupancy_mask[1:]), pid)
        close(row["negative_member_sample_count"], np.sum(negative[1:]), pid)
        close(row["zero_denominator_sample_count"], np.sum(total[1:] <= floor), pid)
        for time in times:
            n = ti[float(time)]
            sample = samples[pid, float(time)]
            close(sample["total_concentration"], total[n], pid)
            require(truth(sample["negative_member"]) == negative[n], "POOL_NEGATIVE_MASK", pid)
            require(truth(sample["occupancy_informative"]) == occupancy_mask[n], "POOL_OCCUPANCY_MASK", pid)
            require(truth(sample["informative"]) == free_mask[n], "POOL_FREE_MASK", pid)
            require(("SUPPLEMENTAL" in sample["sample_kind"]) == (n == 0), "SAMPLING_ROLE", pid)
            occupancy_reason = ("N/A_POOL_NOT_REFERENCE_CONSERVED" if not reference else
                                "N/A_NEGATIVE_POOL_MEMBER" if negative[n] else
                                "N/A_ZERO_POOL_TOTAL" if total[n] <= floor else "INFORMATIVE")
            free_reason = "N/A_FREE_COUNTERPART_UNRESOLVED" if reference and free is None else occupancy_reason
            require(sample["occupancy_reason"] == occupancy_reason and sample["reason"] == free_reason, "POOL_UNAVAILABLE_REASON", pid)
            require(sample["free_species_id"] == row["free_species_id"], "FREE_COUNTERPART", pid)
            same_metric(sample["free_concentration"], x[n, si[free]] if free else "N/A", pid)
            same_metric(sample["free_fraction"], ratio[n] if free_mask[n] else "N/A", pid)
            same_metric(sample["bound_fraction"], 1-ratio[n] if free_mask[n] else "N/A", pid)
        for sid in listed:
            member = members[sid, pid]
            require(member["state_pool_metric_id"] == f"{sid}::{pid}", "POOL_MEMBER_LINK", pid)
            close(member["member_coefficient"], 1, pid)
            require(truth(member["is_free_counterpart"]) == (sid == free), "FREE_COUNTERPART", pid)
            values = x[1:, si[sid]][occupancy_mask[1:]] / total[1:][occupancy_mask[1:]]
            summary(member, ["occupancy_min", "occupancy_median", "occupancy_max"], values, pid)
            for field in ("free_total_ratio_min", "free_total_ratio_median", "free_total_ratio_max", "max_bound_fraction"):
                same_metric(member[field], row[field], f"{sid}/{pid}/{field}")
            close(member["occupancy_informative_fraction"], np.mean(occupancy_mask[1:]), pid)
            close(member["free_fraction_informative_fraction"], np.mean(free_mask[1:]), pid)
    for row in rows["state_evidence"]:
        sid = row["species_id"]
        expected = {p for p, ss in pools.items() if sid in ss}
        require(split(row["known_pool_ids"]) == expected, "POOL_LINK_COVERAGE", sid)
        require(split(row["state_pool_metric_ids"]) == {f"{sid}::{p}" for p in expected}, "POOL_MEMBER_LINK", sid)
        active = [p for p in expected if not p.startswith("coarse:") and p.endswith("_active_pool") and qualified[p]]
        require((row["pool_membership_status"] == "REGISTERED_REFERENCE_CONSERVED") == any(certificates[p] for p in expected), "POOL_STATE_STATUS", sid)
        for field in ("free_total_ratio_min", "free_total_ratio_median", "free_total_ratio_max", "max_bound_fraction", "occupancy_min", "occupancy_median", "occupancy_max"):
            reference = members[sid, active[0]][field] if len(active) == 1 else "N/A"
            same_metric(row[field], reference, f"{sid}/{field}")
        require(row["scalar_pool_id"] == (active[0] if len(active) == 1 else "N/A_MULTIPLE_POOLS" if len(active) > 1 else "N/A_POOL_MEMBERSHIP_UNRESOLVED"), "SCALAR_POOL_POLICY", sid)
    return {"pools_checked": len(pool_rows), "state_pool_memberships_checked": len(member_rows), "pool_samples_checked": len(sample_rows), "reference_conserved_pools": sum(certificates.values()), "quantified_pools": sum(qualified.values())}


def verify_process_metrics(audit, pre, rows, species, reactions, classes, cards, numeric, jacobians):
    """Independently check every spectrum's algebra and summaries; re-solve sampled blocks."""
    from scipy.optimize import linear_sum_assignment
    from sympy import Matrix, QQ
    from sympy.polys.matrices import DomainMatrix

    times, x, _, matrix, prod, cons, params = numeric
    si = {sid: j for j, sid in enumerate(species)}
    time_index = {float(t): i for i, t in enumerate(times)}
    process_rows = {r["process_id"]: r for r in rows["process_timescale_evidence"]}
    sample_rows = read_csv(audit / "process_timescale_timeseries.csv")
    eigen_rows = read_csv(audit / "process_eigenvalue_timeseries.csv")
    samples, modes = {}, defaultdict(list)
    for row in sample_rows:
        key = (row["process_id"], float(row["time"]))
        require(key not in samples, "DUPLICATE_PROCESS_SAMPLE", key)
        samples[key] = row
    for row in eigen_rows:
        modes[(row["process_id"], float(row["time"]))].append(row)
    expected = {(c["process_id"], float(t)) for c in cards for t in times[1:]}
    require(set(samples) == expected, "PROCESS_GRID_COVERAGE", len(samples))
    require(set(modes) <= expected, "EIGEN_GRID_COVERAGE", set(modes)-expected)
    compared_blocks = 0
    max_eigen_error = 0.0
    for card in cards:
        pid, candidate = card["process_id"], card["candidate_state_ids"]
        row = process_rows[pid]
        indices = [si[s] for s in candidate]
        touched = set().union(*(set(reactions[r][0]) | set(reactions[r][1]) for r in card["reaction_ids"]))
        slow = sorted(s for s in touched - set(candidate) if classes[s] == "I")
        require(split(row["candidate_state_ids"]) == set(candidate), "FAST_COORDINATES", pid)
        require(split(row["slow_interface_state_ids"]) == set(slow), "SLOW_COORDINATES", pid)
        require(split(row["reaction_ids"]) == set(card["reaction_ids"]), "PROCESS_LINK", pid)
        require(row["timescale_status"] == "NEED_MORE_INFORMATION", "NO_TIMESCALE_APPROVAL", pid)
        close(row["candidate_state_count"], len(candidate), pid)
        close(row["primary_sample_count"], 200, pid)
        dependent = [j for j, (rid, sides) in enumerate(reactions.items()) if params[rid+"_k1"] != 0 and set(sides[0]) & set(candidate)]
        if candidate and dependent:
            exact = Matrix(matrix[np.ix_(indices, dependent)].astype(int).tolist())
            rank = DomainMatrix.from_Matrix(exact).convert_to(QQ).rank()
        else:
            rank = 0
        neutral_lower_bound = len(candidate) - rank
        close(row["structural_neutral_mode_count"], neutral_lower_bound, pid)
        all_fast, all_slow, ratios, reciprocals = [], [], [], []
        stable_counts, zero_counts, other_counts = [], [], []
        for ti, time in enumerate(times[1:], 1):
            key = (pid, float(time))
            sample, spectrum = samples[key], modes.get(key, [])
            require(len(spectrum) == len(candidate), "EIGEN_MODE_COVERAGE", key)
            require(len({m["mode_index"] for m in spectrum}) == len(candidate), "DUPLICATE_EIGEN_MODE", key)
            values = np.array([complex(float(m["lambda_real"]), float(m["lambda_imag"])) for m in spectrum])
            threshold = max(pre["numeric"]["near_zero_eigenvalue_abs_floor"], pre["numeric"]["near_zero_eigenvalue_relative_floor"] * max(np.abs(values), default=0.0))
            if spectrum:
                close(sample["neutral_threshold"], threshold, str(key))
            fast = []
            zero = other = 0
            for m, value in zip(spectrum, values):
                close(m["lambda_abs"], abs(value), str(key))
                close(m["neutral_threshold"], threshold, str(key))
                require("SUPPLEMENTAL" not in m["sampling_role"], "SAMPLING_ROLE", str(key))
                if value.real < -threshold:
                    require(m["mode_status"] == "STABLE_DECAY", "EIGEN_CLASS", str(key))
                    close(m["relaxation_tau"], -1/value.real, str(key))
                    fast.append(-1/value.real)
                elif abs(value) <= threshold:
                    zero += 1
                    require(m["mode_status"] == "NEAR_ZERO_NEUTRAL" and is_na(m["relaxation_tau"]), "NEUTRAL_INVERSION", str(key))
                else:
                    other += 1
                    require(m["mode_status"] == "NONDECAYING_OR_UNRESOLVED_DECAY" and is_na(m["relaxation_tau"]), "NONDECAYING_INVERSION", str(key))
            require(zero >= neutral_lower_bound, "STRUCTURAL_NEUTRAL_LOWER_BOUND", key)
            close(sample["structural_neutral_mode_count"], neutral_lower_bound, str(key))
            for field, expected_count in (("stable_mode_count", len(fast)), ("near_zero_mode_count", zero), ("nondecaying_mode_count", other)):
                close(sample[field], expected_count, str(key))
            slow_values = []
            for sid in slow:
                j = si[sid]
                denominator = prod[ti, j] + cons[ti, j]
                if denominator > pre["numeric"]["flux_information_floor"] and x[ti, j] > pre["numeric"]["concentration_denominator_floor"]:
                    slow_values.append(abs(x[ti, j]) / denominator)
            summary(sample, ["tau_fast_min", "tau_fast_median", "tau_fast_max"], fast, str(key))
            summary(sample, ["tau_slow_min", "tau_slow_median", "tau_slow_max"], slow_values, str(key))
            close(sample["slow_informative_state_count"], len(slow_values), str(key))
            if fast and slow_values:
                ratio = np.median(slow_values)/np.median(fast)
                close(sample["R_tau"], ratio, str(key))
                close(sample["epsilon_tau"], 1/ratio, str(key))
                ratios.append(ratio)
                reciprocals.append(1/ratio)
            else:
                require(is_na(sample["R_tau"]) and is_na(sample["epsilon_tau"]), "MISSING_TIMESCALE", key)
            require(sample["timescale_status"] == "NEED_MORE_INFORMATION", "NO_TIMESCALE_APPROVAL", key)
            all_fast.extend(fast)
            all_slow.extend(slow_values)
            stable_counts.append(len(fast))
            zero_counts.append(zero)
            other_counts.append(other)
            if ti in jacobians and candidate:
                independent = np.linalg.eigvals(jacobians[ti][np.ix_(indices, indices)])
                cost = np.abs(independent[:, None]-values[None, :]) / np.maximum(1, np.maximum(np.abs(independent[:, None]), np.abs(values[None, :])))
                aa, bb = linear_sum_assignment(cost)
                error = float(np.max(cost[aa, bb]))
                require(error <= 1e-7, "INDEPENDENT_BLOCK_EIGENVALUES", f"{key}: {error}")
                max_eigen_error = max(max_eigen_error, error)
                compared_blocks += 1
        for prefix, distribution in (("tau_fast", all_fast), ("tau_slow", all_slow), ("R_tau", ratios), ("epsilon_tau", reciprocals)):
            summary(row, [prefix+"_"+suffix for suffix in ("min", "median", "max")], distribution, pid)
        for prefix, counts in (("stable_mode_count", stable_counts), ("near_zero_mode_count", zero_counts), ("nondecaying_mode_count", other_counts)):
            close(row[prefix+"_min"], min(counts), pid)
            close(row[prefix+"_max"], max(counts), pid)
    return {"process_sample_rows_checked": len(sample_rows), "eigenvalue_rows_checked": len(eigen_rows), "independently_resolved_blocks": compared_blocks, "independent_eigenvalue_max_scaled_error": max_eigen_error, "independent_eigenvalue_scaled_tolerance": 1e-7}


def verify_manifest(root, audit, pre):
    manifest = read_json(audit / "evidence_manifest.json")
    require(manifest["source_head"] == SOURCE_HEAD, "MANIFEST_SOURCE", manifest["source_head"])
    require(manifest["preregistration_sha256"] == PRE_SHA, "MANIFEST_PREREG", manifest["preregistration_sha256"])
    require(manifest["source_hashes"] == pre["input_sha256"], "MANIFEST_INPUTS", "source hash map differs")
    for key in ("versions", "row_counts", "metric_availability", "verification_results"):
        require(bool(manifest.get(key)), "MANIFEST_FIELD", key)
    expected_files = {p.relative_to(root).as_posix() for p in audit.glob("*.csv")}
    require(expected_files <= set(manifest["generated_artifact_sha256"]), "MANIFEST_COVERAGE", expected_files-set(manifest["generated_artifact_sha256"]))
    for group in ("scripts_sha256", "generated_artifact_sha256"):
        for rel, expected in manifest[group].items():
            require(sha((root / rel).read_bytes()) == expected, "ARTIFACT_HASH", rel)
    for script in ("scripts/analyze_pnas2017_reduction_evidence.py", "scripts/verify_pnas2017_reduction_evidence.py"):
        require(script in manifest["scripts_sha256"], "MANIFEST_SCRIPT", script)
    for filename, count in (("reaction_evidence.csv", 968), ("state_evidence.csv", 241), ("reverse_pair_evidence.csv", 290), ("process_timescale_evidence.csv", 16)):
        found = manifest["row_counts"].get(filename, manifest["row_counts"].get(filename.removesuffix(".csv")))
        require(found == count, "MANIFEST_ROW_COUNT", filename)


def negative_controls(root, pre, rows, reactions, species, pairs, classes, pools):
    results = []
    with tempfile.TemporaryDirectory(prefix="pnas-evidence-adversarial-") as directory:
        temp = Path(directory)

        def reject(name, code, callback):
            try:
                callback()
            except EvidenceError as exc:
                require(exc.code == code, "WRONG_NEGATIVE_FAILURE", f"{name}: expected {code}, got {exc.code}")
                results.append({"name": name, "expected_rejection": code, "result": "REJECTED_AS_EXPECTED", "hash_checks_used": code in {"SOURCE_HASH", "DECLARED_SBML_HASH"}})
            else:
                raise EvidenceError("NEGATIVE_CONTROL_ACCEPTED", name)

        def csv_case(name, data, callback):
            path = temp / (name + ".csv")
            write_csv(path, data)
            return lambda: callback(read_csv(path))

        missing = copy.deepcopy(rows["reaction_evidence"][:-1])
        reject("missing_reaction", "ROW_COUNT", csv_case("missing", missing, lambda a: coverage(a, "reaction_id", reactions, "negative")))
        duplicate = copy.deepcopy(rows["reaction_evidence"])
        duplicate[-1] = duplicate[0].copy()
        reject("duplicate_reaction", "DUPLICATE_ID", csv_case("duplicate", duplicate, lambda a: coverage(a, "reaction_id", reactions, "negative")))
        altered = copy.deepcopy(pre)
        altered["canonical_sbml_sha256"] = "0" * 64
        altered_path = temp / "altered_preregistration.json"
        altered_path.write_text(json.dumps(altered), encoding="utf-8")
        reject("altered_declared_source_sha", "DECLARED_SBML_HASH", lambda: prereg_semantics(read_json(altered_path)))
        bad_pairs = copy.deepcopy(rows["reverse_pair_evidence"])
        bad_pairs[0]["reverse_reaction_id"] = bad_pairs[0]["forward_reaction_id"]
        reject("wrong_reverse_partner", "REVERSE_PARTNER", csv_case("wrong_pair", bad_pairs, lambda a: check_reverse_rows(a, pairs, reactions)))
        false_eq = {"time": "0", "pair_id": "adversarial", "vf": "0", "vr": "0", "exchange_flux": "0", "net_flux": "0", "equilibrium_defect": "0", "informative": "false", "reason": "LOW_FLUX_UNINFORMATIVE"}
        reject("zero_zero_pair_false_equilibrium", "ZERO_EQUILIBRIUM", csv_case("zero_pair", [false_eq], lambda a: pair_sample(a[0], pre["numeric"]["flux_information_floor"], False)))
        false_qss = {"time": "0", "species_id": "adversarial", "production_flux": "0", "consumption_flux": "0", "dzdt": "0", "qss_defect": "0", "informative": "false", "reason": "LOW_FLUX_UNINFORMATIVE"}
        reject("zero_flux_false_qss", "ZERO_QSS", csv_case("zero_qss", [false_qss], lambda a: qss_sample(a[0], pre["numeric"]["flux_information_floor"])))
        bad_pools = copy.deepcopy(rows["state_evidence"])
        bad_pools[0]["known_pool_ids"] = "invented_total_pool"
        reject("fabricated_pool", "FABRICATED_POOL", csv_case("pool", bad_pools, lambda a: check_pool_ids(a, pools)))
        wrong_member = copy.deepcopy(rows["state_evidence"])
        nonmember_pool = next(pool for pool, members in pools.items() if wrong_member[0]["species_id"] not in members)
        wrong_member[0]["known_pool_ids"] = nonmember_pool
        reject("real_pool_fabricated_nonmember", "FABRICATED_POOL", csv_case("pool_nonmember", wrong_member, lambda a: check_pool_ids(a, pools)))
        bad_class = copy.deepcopy(rows["state_evidence"])
        bad_class[0]["information_contract_class"] = "C" if bad_class[0]["information_contract_class"] != "C" else "I"
        reject("altered_species_classification", "SPECIES_CLASS", csv_case("class", bad_class, lambda a: check_classes(a, classes)))
        bad_decisions = read_csv(root / "docs/reduction/reduction_decisions.csv")
        bad_decisions[0]["decision_status"] = "QSSA"
        reject("altered_scientific_decision", "HUMAN_DECISION", csv_case("decision", bad_decisions, check_decisions))
        review = (root / "docs/reduction/human_reduction_review.md").read_text(encoding="utf-8")
        selected_path = temp / "selected_review.md"
        selected_path.write_text(review.replace("- [ ] KEEP", "- [x] KEEP", 1), encoding="utf-8")
        reject("preselected_process_checkbox", "PRESELECTED_BOX", lambda: check_boxes(selected_path.read_text(encoding="utf-8")))
        canonical_path = temp / "modified_canonical.xml"
        canonical_path.write_bytes((root / pre["canonical_sbml_path"]).read_bytes().replace(b'value="1"', b'value="2"', 1))
        reject("canonical_source_mutation", "SOURCE_HASH", lambda: source_digest(canonical_path.read_bytes(), pre["canonical_sbml_sha256"], "canonical"))
        author_path = temp / "modified_author_parameters.csv"
        author_rel = AUTHOR + "fMGG_synthesis_parameters.csv"
        author_path.write_bytes((root / author_rel).read_bytes().replace(b"re0000000001_k1,1000", b"re0000000001_k1,1001", 1))
        reject("author_parameter_mutation", "SOURCE_HASH", lambda: source_digest(author_path.read_bytes(), pre["input_sha256"][author_rel], "author"))
        initial_rel = AUTHOR + "fMGG_synthesis_initial_values.csv"
        initial_path = temp / "modified_author_initial_values.csv"
        initial_rows = read_csv(root / initial_rel)
        initial_rows[0]["Value"] = str(float(initial_rows[0]["Value"]) + 1)
        write_csv(initial_path, initial_rows)
        reject("author_initial_value_mutation", "SOURCE_HASH", lambda: source_digest(initial_path.read_bytes(), pre["input_sha256"][initial_rel], "author initial"))
        false_enabled = dict(false_eq, vf="1", exchange_flux="1", net_flux="1", informative="true", equilibrium_defect="1", reason="INFORMATIVE")
        reject("disabled_direction_false_evidence", "DISABLED_EQUILIBRIUM", csv_case("disabled", [false_enabled], lambda a: pair_sample(a[0], pre["numeric"]["flux_information_floor"], True)))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--audit-dir", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--skip-manifest", action="store_true", help="development only; report records skipped check")
    parser.add_argument("--skip-docs", action="store_true", help="development only; report records skipped check")
    parser.add_argument("--skip-negative-controls", action="store_true", help="development only; report records skipped check")
    args = parser.parse_args()
    root = args.root.resolve()
    audit = (args.audit_dir or root / AUDIT).resolve()
    pre_path = audit / "evidence_preregistration.json"
    require(sha(pre_path.read_bytes()) == PRE_SHA, "PREREGISTRATION_FROZEN", "frozen file bytes changed")
    pre = read_json(pre_path)
    eol = verify_inputs(root, pre)
    rows, species, reactions, pairs, classes, cards, pools, numeric = verify_tables(root, audit, pre)
    numerical_crosschecks, jacobians = independent_numerical_checks(root, pre, species, reactions, numeric)
    pool_checks = verify_pool_metrics(audit, pre, rows, species, reactions, classes, numeric)
    process_checks = verify_process_metrics(audit, pre, rows, species, reactions, classes, cards, numeric, jacobians)
    if not args.skip_docs:
        verify_docs(root)
    controls = [] if args.skip_negative_controls else negative_controls(root, pre, rows, reactions, species, pairs, classes, pools)
    if not args.skip_manifest:
        verify_manifest(root, audit, pre)
    report = {"schema": "pnas2017_reduction_evidence_verification/v0", "status": "PASS" if not (args.skip_manifest or args.skip_docs or args.skip_negative_controls) else "PARTIAL_DEVELOPMENT_CHECKS_PASS", "source_head": SOURCE_HEAD, "preregistration_sha256": PRE_SHA, "reaction_coverage": 968, "species_coverage": 241, "reverse_pairs": 290, "processes": 16, "kinetic_decisions_pending": 968, "unselected_process_boxes": 96, "reduced_model_status": "NOT_VALIDATED", "eol_only_checkout_differences": eol, "negative_controls": controls, "hash_checks_separate_from_semantic_controls": True, "numerical_check": "all 201 samples: independent canonical-stoichiometry and author-CSV mass action; all QSS, pair and concentration/turnover/extent summaries", "skipped_checks": [key for key, value in (("manifest", args.skip_manifest), ("docs", args.skip_docs), ("negative_controls", args.skip_negative_controls)) if value]}
    report["independent_numerical_crosschecks"] = numerical_crosschecks
    report["pool_verification"] = pool_checks
    report["process_timescale_verification"] = process_checks
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
