#!/usr/bin/env python3
"""Reproduce the frozen PNAS-wide, author-condition pre-decision evidence.

Run with a Python providing NumPy and SymPy. If RoadRunner is installed in a
separate environment, pass --roadrunner-python PATH. No model is integrated,
fitted, clipped, or reduced. Existing reference samples are used verbatim.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIT = Path("models/pnas2017_full_reference/audit/reduction_evidence_v0")
AUTHOR = Path("models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat")
PRE_SHA = "b20d782edcef9a7a70bf3848acd2dbd8c240303e3507cc927f0041c56bc4969b"
NS = {"s": "http://www.sbml.org/sbml/level2/version4"}
NA_POOL = "N/A_POOL_MEMBERSHIP_UNRESOLVED"
NA_FLUX = "N/A_LOW_FLUX"
LIMIT = "AUTHOR_REFERENCE_CONDITION_ONLY;UNRESOLVED_ABSOLUTE_CONCENTRATION_UNITS;NO_TRANSFORMATION_EVALUATED"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
                    encoding="utf-8", newline="\n")


def join(values):
    return ";".join(sorted(set(values)))


def js(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def cell(value):
    if isinstance(value, (bool, np.bool_)):
        return "true" if value else "false"
    if isinstance(value, (float, np.floating)):
        if not np.isfinite(value):
            raise ValueError("Nonfinite numeric output; use explicit unavailable reason")
        return repr(float(value))
    if isinstance(value, (dict, list)):
        return js(value)
    return value


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Unexpected empty output: {path}")
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: cell(row.get(key, "N/A_NOT_APPLICABLE")) for key in keys} for row in rows)


def stats(values, names, reason=NA_FLUX):
    a = np.asarray(values, dtype=float)
    if not len(a):
        return dict.fromkeys(names, reason)
    functions = {"min": np.min, "median": np.median, "max": np.max,
                 "p05": lambda a: np.quantile(a, .05), "p95": lambda a: np.quantile(a, .95)}
    return {n: float(functions[n.rsplit("_", 1)[-1]](a)) for n in names}


def parse_source(root, pre):
    model = ET.parse(root / pre["canonical_sbml_path"]).getroot().find("s:model", NS)
    species = [e.attrib["id"] for e in model.find("s:listOfSpecies", NS)]
    reactions = list(model.find("s:listOfReactions", NS))
    ids = [e.attrib["id"] for e in reactions]
    assert len(species) == len(set(species)) == 241
    assert len(ids) == len(set(ids)) == 968
    si = {s: i for i, s in enumerate(species)}

    def side(reaction, name):
        result = {}
        for e in reaction.find("s:" + name, NS):
            math = e.find("s:stoichiometryMath", NS)
            if math is not None:
                cn = [q for q in math.iter() if q.tag.rsplit("}", 1)[-1] == "cn"]
                assert len(cn) == 1
                value = float(cn[0].text)
            else:
                value = float(e.get("stoichiometry", "1"))
            result[e.attrib["species"]] = value
        return result

    left = [side(r, "listOfReactants") for r in reactions]
    right = [side(r, "listOfProducts") for r in reactions]
    S = np.zeros((len(species), len(ids)))
    for j in range(len(ids)):
        for sid, value in left[j].items():
            S[si[sid], j] -= value
        for sid, value in right[j].items():
            S[si[sid], j] += value
    # Audit inventory is an independent source of mass-action participant data.
    inventory = {r["reaction_id"]: r for r in read_csv(root / "models/pnas2017_full_reference/audit/reactions.csv")}
    assert set(inventory) == set(ids)
    for rid, l, r in zip(ids, left, right):
        for key, actual in (("reactants_json", l), ("products_json", r)):
            recorded = {p["species_id"]: float(p["stoichiometry"]) for p in json.loads(inventory[rid][key])}
            assert recorded == actual, (rid, key)
    return species, ids, left, right, S


def engine_evaluate(source, snapshots, output):
    """Separate process entry point, available to a RoadRunner-only Python."""
    import roadrunner
    rr = roadrunner.RoadRunner(str(source))
    data = np.load(snapshots)
    species, ids = list(data["species"]), list(data["reactions"])
    engine_species = list(rr.model.getFloatingSpeciesIds())
    engine_reactions = list(rr.model.getReactionIds())
    assert set(engine_species) == set(species)
    assert set(engine_reactions) == set(ids)
    state_order = [species.index(s) for s in engine_species]
    rate_order = [engine_reactions.index(r) for r in ids]
    rates = []
    for state in data["x"]:
        rr.model.setFloatingSpeciesConcentrations(state[state_order])
        rates.append(np.asarray(rr.model.getReactionRates())[rate_order])
    np.save(output, np.asarray(rates))
    print(json.dumps({"RoadRunner": roadrunner.__version__, "RoadRunner_python": platform.python_version(),
                      "RoadRunner_numpy": np.__version__, "libSBML": "NOT_USED_BY_ANALYSIS"}))


def check_engine(root, pre, species, ids, x, rates, interpreter):
    with tempfile.TemporaryDirectory(prefix="pnas-evidence-engine-") as directory:
        p = Path(directory)
        np.savez(p / "snapshots.npz", species=np.asarray(species), reactions=np.asarray(ids), x=x)
        cmd = [interpreter, str(Path(__file__).resolve()), "--engine-evaluate",
               str(root / pre["effective_sbml"]["path"]), str(p / "snapshots.npz"), str(p / "rates.npy")]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8")
        engine = np.load(p / "rates.npy")
        error = np.abs(engine - rates) / np.maximum(1, np.maximum(np.abs(engine), np.abs(rates)))
        worst = np.unravel_index(np.argmax(error), error.shape)
        maximum = float(np.max(error))
        assert maximum <= pre["numeric"]["rate_crosscheck_max_scaled_abs_error"], maximum
        versions = json.loads(result.stdout.strip().splitlines()[-1])
        return {"status": "NUMERICAL_CROSSCHECK_PASS_NOT_KINETIC_APPROVAL",
                "maximum_scaled_error": maximum, "maximum_absolute_error": float(np.max(np.abs(engine-rates))),
                "samples": len(x), "directed_reactions": len(ids),
                "worst_sample_index": int(worst[0]), "worst_reaction_id": ids[worst[1]],
                "tolerance": pre["numeric"]["rate_crosscheck_max_scaled_abs_error"],
                "basis": "RoadRunner effective SBML versus canonical/audit-reactant mass action + author CSV"}, versions


def analyze(root, output, interpreter):
    from finalize_pnas2017_reduction_evidence import verify_frozen
    from pnas2017_evidence_pools import compute_pools
    from pnas2017_evidence_timescales import compute_timescales

    pre_path = root / AUDIT / "evidence_preregistration.json"
    assert hashlib.sha256(pre_path.read_bytes()).hexdigest() == PRE_SHA
    pre = json.loads(pre_path.read_text(encoding="utf-8"))
    frozen = verify_frozen(pre)
    output.mkdir(parents=True, exist_ok=True)
    species, ids, left, right, S = parse_source(root, pre)
    si, ri = {s: i for i, s in enumerate(species)}, {r: i for i, r in enumerate(ids)}
    initial = {r["Name"]: float(r["Value"]) for r in read_csv(root / AUTHOR / "fMGG_synthesis_initial_values.csv")}
    params = {r["Name"]: float(r["Value"]) for r in read_csv(root / AUTHOR / "fMGG_synthesis_parameters.csv")}
    k = np.asarray([params[r + "_k1"] for r in ids])
    stored = read_csv(root / pre["trajectory"]["path"])
    time_col = next(iter(stored[0]))
    times = np.asarray([0.0] + [float(row[time_col]) for row in stored])
    # Stored CSV identifiers may be bracketed RoadRunner selections.
    columns = {key.strip("[]"): key for key in stored[0] if key != time_col}
    assert set(columns) == set(species)
    x = np.asarray([[initial[s] for s in species]] + [[float(row[columns[s]]) for s in species] for row in stored])
    assert x.shape == (201, 241) and np.allclose(times[1:], np.logspace(-4, 3, 200), rtol=1e-13, atol=0)
    rates = np.repeat(k[None, :], len(times), axis=0)
    for j, reactants in enumerate(left):
        for sid, power in reactants.items():
            rates[:, j] *= x[:, si[sid]] ** power
    print("Evaluating independent execution-engine rates at all 201 preserved states", flush=True)
    crosscheck, versions = check_engine(root, pre, species, ids, x, rates, interpreter)
    # Signed contributions preserve any negative engine roundoff, without clipping states/rates.
    prod, cons = np.zeros_like(x), np.zeros_like(x)
    for j in range(len(ids)):
        contribution = rates[:, j, None] * S[None, :, j]
        prod += np.maximum(contribution, 0)
        cons += np.maximum(-contribution, 0)
    dzdt = prod - cons
    flux_floor = pre["numeric"]["flux_information_floor"]
    conc_floor = pre["numeric"]["concentration_denominator_floor"]
    den = prod + cons
    extents = np.sum((rates[1:] + rates[:-1]) * np.diff(times)[:, None] / 2, axis=0)
    text = (root / "docs/reduction/species_information_contract_detailed.md").read_text(encoding="utf-8")
    classes = dict(re.findall(r"^\|\s*\d+\s*\|\s*`([^`]+)`\s*\|.*?\|\s*\*\*(I|II-A|II-B|III|C)\*\*\s*\|", text, re.M))
    assert set(classes) == set(species)
    annotations = {r["reaction_id"]: r for r in read_csv(root / "docs/reduction/reaction_level_annotation_v2.csv")}
    decisions = {r["sbml_reaction_id"]: r for r in read_csv(root / "docs/reduction/reduction_decisions.csv")}
    ledger = {r["sbml_reaction_id"]: r for r in read_csv(root / "models/pnas2017_full_reference/audit/reaction_balance_audit.csv")}
    cards = pre["process_cards"]
    candidates = set(s for c in cards for s in c["candidate_state_ids"])
    memberships = {r: [c["process_id"] for c in cards if r in c["reaction_ids"]] for r in ids}
    candidate_memberships = {s: [c["process_id"] for c in cards if s in c["candidate_state_ids"]] for s in species}
    touched = {r: set(left[ri[r]]) | set(right[ri[r]]) for r in ids}
    state_memberships = {s: [c["process_id"] for c in cards if any(s in touched[r] for r in c["reaction_ids"])] for s in species}
    print("Computing registered-pool certificates and occupancy", flush=True)
    pools = compute_pools(root, pre, species, S, k, x, classes, times)
    for name in ("pool_evidence", "state_pool_metrics", "pool_timeseries"):
        write_csv(output / (name + ".csv"), pools[name])
    qss_rows, state_rows = [], []
    for j, sid in enumerate(species):
        informative = den[:, j] > flux_floor
        defects = np.abs(dzdt[:, j][informative]) / den[:, j][informative]
        values = np.full(len(times), np.nan)
        values[informative] = defects
        for ti, time in enumerate(times):
            qss_rows.append({"time": time, "species_id": sid, "dzdt": dzdt[ti, j],
                "production_flux": prod[ti, j], "consumption_flux": cons[ti, j],
                "qss_defect": values[ti] if informative[ti] else NA_FLUX,
                "informative": informative[ti], "reason": "INFORMATIVE" if informative[ti] else "LOW_FLUX_UNINFORMATIVE",
                "sampling_role": "AUTHOR_LOGSPACE" if ti else "SUPPLEMENTAL_NUMERICAL_DIAGNOSTIC"})
        valid_tau = (den[1:, j] > flux_floor) & (x[1:, j] > conc_floor)
        row = {"species_id": sid, "information_contract_class": classes[sid],
            "process_memberships": join(state_memberships[sid]), "candidate_process_memberships": join(candidate_memberships[sid]),
            "initial_value": x[0, j], **stats(x[1:, j], ["trajectory_min", "trajectory_median", "trajectory_max"]),
            "is_candidate_intermediate": sid in candidates, "protected_output": classes[sid] == "I",
            **pools["state_fields"][sid],
            **stats(prod[1:, j], ["production_flux_median", "production_flux_max"]),
            **stats(cons[1:, j], ["consumption_flux_median", "consumption_flux_max"]),
            **stats(values[1:][informative[1:]], ["qss_defect_median", "qss_defect_p95", "qss_defect_max"]),
            "qss_informative_fraction": float(np.mean(informative[1:])),
            **stats(np.abs(x[1:, j][valid_tau]) / den[1:, j][valid_tau],
                    ["turnover_tau_median", "turnover_tau_p05", "turnover_tau_p95"], "N/A_LOW_FLUX_OR_ZERO_CONCENTRATION"),
            "initial_layer_flag": "UNRESOLVED_INITIAL_LAYER_STORED_X0_AT_1E_MINUS4",
            "resource_token_status": "EXPLICIT_FREE_RESOURCE_ONLY_BOUND_MOIETY_MEMBERSHIP_UNRESOLVED" if classes[sid] == "I" else "BOUND_MOIETY_MEMBERSHIP_UNRESOLVED",
            "reconstruction_requirement": {
                "I": "PROTECTED_DYNAMIC_OUTPUT_MUST_REMAIN_RECONSTRUCTABLE",
                "II-A": "VALID_CLOSURE_AND_PROTECTED_RESOURCE_RECONSTRUCTION_REQUIRED",
                "II-B": "FUNCTIONAL_OCCUPANCY_POOL_RECONSTRUCTION_REQUIRED",
                "III": "AGGREGATE_FLUX_OCCUPANCY_MOIETY_RECONSTRUCTION_REQUIRED",
                "C": "CUMULATIVE_DEGRADATION_ACCOUNTING_REQUIRED_NOT_ZEROED"}[classes[sid]] + ";NO_TRANSFORMATION_EVALUATED",
            "evidence_limitations": LIMIT}
        state_rows.append(row)
    write_csv(output / "state_evidence.csv", state_rows)
    write_csv(output / "state_qss_timeseries.csv", qss_rows)
    # Canonical exact swap pairing, checked against the existing annotation map.
    signature = {(tuple(sorted(l.items())), tuple(sorted(r.items()))): rid for rid, l, r in zip(ids, left, right)}
    assert len(signature) == len(ids)
    pairs = sorted({tuple(sorted((rid, signature[(b, a)]))) for (a, b), rid in signature.items() if (b, a) in signature})
    assert len(pairs) == 290
    pair_rows, pair_series, partner = [], [], {}
    for n, (forward, reverse) in enumerate(pairs, 1):
        pair_id = f"EQP_{n:03d}"
        partner[forward] = (reverse, pair_id); partner[reverse] = (forward, pair_id)
        assert annotations[forward]["reverse_partner_id"] == reverse and annotations[reverse]["reverse_partner_id"] == forward
        fj, rj = ri[forward], ri[reverse]
        vf, vr = rates[:, fj], rates[:, rj]
        exchange, net = np.abs(vf) + np.abs(vr), vf - vr
        disabled = k[fj] == 0 or k[rj] == 0
        informative = (exchange > flux_floor) & (not disabled)
        defects = np.abs(net[informative]) / exchange[informative]
        values = np.full(len(times), np.nan); values[informative] = defects
        reason = "REFERENCE_DIRECTION_DISABLED" if disabled else "LOW_FLUX_UNINFORMATIVE"
        na = "N/A_REFERENCE_DIRECTION_DISABLED" if disabled else NA_FLUX
        for ti, time in enumerate(times):
            pair_series.append({"time": time, "pair_id": pair_id, "forward_reaction_id": forward,
                "reverse_reaction_id": reverse, "vf": vf[ti], "vr": vr[ti],
                "exchange_flux": exchange[ti], "net_flux": net[ti],
                "equilibrium_defect": values[ti] if informative[ti] else na,
                "informative": informative[ti], "reason": "INFORMATIVE" if informative[ti] else reason,
                "sampling_role": "AUTHOR_LOGSPACE" if ti else "SUPPLEMENTAL_NUMERICAL_DIAGNOSTIC"})
        primary = values[1:][informative[1:]]
        row = {"pair_id": pair_id, "forward_reaction_id": forward, "reverse_reaction_id": reverse,
            "forward_k": k[fj], "reverse_k": k[rj],
            "reference_activity_forward": "DISABLED_K1_ZERO" if k[fj] == 0 else "ENABLED_K1_NONZERO",
            "reference_activity_reverse": "DISABLED_K1_ZERO" if k[rj] == 0 else "ENABLED_K1_NONZERO",
            "pair_reference_status": "REFERENCE_DIRECTION_DISABLED" if disabled else "BOTH_REFERENCE_DIRECTIONS_ENABLED",
            "informative_fraction": float(np.mean(informative[1:])),
            **stats(primary, ["eq_defect_median", "eq_defect_p95", "eq_defect_max"], na),
            **{f"fraction_delta_below_{label}": float(np.mean(primary < band)) if len(primary) else na
               for label, band in [("1e-1", .1), ("1e-2", .01), ("1e-3", .001)]},
            "forward_extent": extents[fj], "reverse_extent": extents[rj], "net_extent": extents[fj] - extents[rj],
            "forward_rate_median": np.median(vf[1:]), "reverse_rate_median": np.median(vr[1:]),
            "net_rate_median": np.median(net[1:]), "exchange_rate_median": np.median(exchange[1:]),
            "protected_resources_touched": join(s for s in touched[forward] | touched[reverse] if classes[s] == "I"),
            "ledger_pair_status": "EXACT_REVERSE_PAIR_REPRESENTATION_PRESERVES_STOICHIOMETRY;NO_TRANSFORMATION_EVALUATED",
            "evidence_limitations": LIMIT + ";TRAPEZOIDAL_EXTENTS_NOT_SOLVER_INTEGRATED;DESCRIPTIVE_BANDS_ONLY"}
        pair_rows.append(row)
    write_csv(output / "reverse_pair_evidence.csv", pair_rows)
    write_csv(output / "reverse_pair_equilibrium_timeseries.csv", pair_series)
    reaction_rows, reaction_pool_rows = [], []
    resource_ids = ["ATP", "GTP", "AMP", "ADP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr", "Gly", "Met", "fMet",
                    "tRNAGlyGCC", "tRNAfMetCAU", "GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU"]
    for j, rid in enumerate(ids):
        ann, decision = annotations[rid], decisions[rid]
        assert decision["decision_status"] == "PENDING"
        pool_ids = [p for p, members in pools["members"].items() if touched[rid] & set(members)]
        metric_ids = []
        for p in sorted(pool_ids):
            mid = rid + "::" + p; metric_ids.append(mid)
            record = pools["pool_by_id"][p]
            reaction_pool_rows.append({"pool_metric_id": mid, "reaction_id": rid, "pool_id": p,
                "participating_pool_species": join(touched[rid] & set(pools["members"][p])),
                "pool_metric_status": "REGISTERED_REFERENCE_CONSERVED" if pools["valid"][p] else "POOL_MEMBERSHIP_UNRESOLVED",
                "free_fraction_min": record.get("free_fraction_min", record.get("free_total_ratio_min", NA_POOL)),
                "free_fraction_median": record.get("free_fraction_median", record.get("free_total_ratio_median", NA_POOL)),
                "free_fraction_max": record.get("free_fraction_max", record.get("free_total_ratio_max", NA_POOL)),
                "maximum_nonfree_fraction": record.get("max_bound_fraction", record.get("max_nonfree_fraction", NA_POOL)),
                "net_pool_token_delta": float(sum(S[si[s], j] for s in pools["members"][p])),
                "sequestration_status": "BOUND_MOIETY_MEMBERSHIP_UNRESOLVED",
                "source": pre["registered_pools"]["source"]})
        rev, pid = partner.get(rid, ("N/A_NO_EXACT_REVERSE_PAIR", "N/A_NO_EXACT_REVERSE_PAIR"))
        eq = "N/A_NO_EXACT_REVERSE_PAIR" if rid not in partner else ("REFERENCE_DIRECTION_DISABLED" if k[j] == 0 or k[ri[rev]] == 0 else "PAIR_LEVEL_EVIDENCE_AVAILABLE")
        row = {"reaction_id": rid, "level_a_module": ann["level_a_module_candidates"],
            "level_b_subsystems": ann["level_b_subsystem_candidates"], "reaction_family_id": ann["reaction_family_id"],
            "level_c_stage": ann["level_c_primary_stage"], "mechanistic_reaction_type": ann["mechanistic_reaction_type"],
            "reactants_json": js(left[j]), "products_json": js(right[j]), "official_parameter_id": rid + "_k1",
            "official_parameter_value": k[j], "reference_activity": ann["reference_activity"],
            "candidate_label_existing": decision["candidate_label"], "human_decision_status": "PENDING",
            "reverse_partner_id": rev, "reverse_pair_id": pid,
            "reverse_pair_status": "EXACT_REVERSE_PAIR" if rid in partner else "N/A_NO_EXACT_REVERSE_PAIR",
            "protected_species_touched": ann["protected_species_touched"], "protected_pool_touched": join(pool_ids) or NA_POOL,
            "original_annotation_pool_ids": ann["protected_pool_touched"],
            "contract_classes_touched": ann["contract_classes_touched"], "candidate_state_ids": join(touched[rid] & candidates),
            "rate_median": np.median(rates[1:, j]), "rate_max_abs": np.max(np.abs(rates[1:, j])),
            "directed_extent": extents[j], "net_tracked_particle_delta": np.sum(S[:, j]),
            "resource_delta_json": js({s: float(S[si[s], j]) for s in resource_ids}),
            "protected_state_delta_json": js({s: float(S[si[s], j]) for s in sorted(touched[rid]) if classes[s] == "I"}),
            "free_peptide_delta_json": js({s: float(S[si[s], j]) for s in ["Pept0002", "Pept0003"]}),
            "conservation_families_touched": ann["conservation_families_touched"], "pool_metric_ids": join(metric_ids) or NA_POOL,
            "state_evidence_ids": join(touched[rid]), "pair_evidence_id": pid, "process_ids": join(memberships[rid]),
            "ledger_record_id": rid, "ledger_source": "models/pnas2017_full_reference/audit/reaction_balance_audit.csv",
            "ledger_evidence_status": "EXACT_EVENT_STOICHIOMETRY_KNOWN;NO_TRANSFORMATION_EVALUATED",
            "bound_moiety_status": "BOUND_MOIETY_MEMBERSHIP_UNRESOLVED",
            "timescale_metric_status": "N/A_PROCESS_LEVEL_METRIC", "qss_metric_status": "N/A_STATE_LEVEL_METRIC",
            "equilibrium_metric_status": eq, "human_review_required": True,
            "reconstruction_requirement": "PRESERVE_BOTH_DIRECTIONAL_FLUXES_AND_HIDDEN_RESOURCES_BEFORE_TRANSFORMATION",
            "evidence_limitations": LIMIT + ";TRAPEZOIDAL_EXTENT_APPROXIMATION;PARTICLE_PROXY_NOT_OSMOTIC_PRESSURE"}
        assert row["net_tracked_particle_delta"] == float(ledger[rid]["net_tracked_particle_count_per_event"])
        reaction_rows.append(row)
    write_csv(output / "reaction_evidence.csv", reaction_rows)
    write_csv(output / "reaction_pool_metrics.csv", reaction_pool_rows)
    print("Computing process-local spectra with fixed neutral-mode handling", flush=True)
    process = compute_timescales(pre, species, S, k, left, x, times, classes, prod, cons)
    for name in ("process_timescale_evidence", "process_eigenvalue_timeseries", "process_timescale_timeseries"):
        write_csv(output / (name + ".csv"), process[name])
    import sympy
    diagnostics = {"schema": "pnas2017_reduction_evidence_diagnostics/v0",
        "analysis_timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_head": pre["source_head"], "preregistration_sha256": PRE_SHA,
        "versions": {"Python": platform.python_version(), "NumPy": np.__version__, "SymPy": sympy.__version__, **versions,
                     "MATLAB": "NOT_USED", "trajectory_RoadRunner": "2.10.0_PRESERVED"},
        "rate_crosscheck": crosscheck, "jacobian_crosscheck": process["numerical_crosscheck"],
        "first_stored_state_max_abs_difference_from_author_x0": float(np.max(np.abs(x[1]-x[0]))),
        "stored_time_convention": "First stored timestamp retained as 1e-4; no shift/resimulation; supplemental author x0 at t=0",
        "negative_concentration_samples": int(np.sum(x < 0)), "minimum_raw_concentration": float(x.min()),
        "negative_rate_samples": int(np.sum(rates < 0)), "minimum_raw_rate": float(rates.min()),
        "enabled_parameters": int(np.sum(k != 0)), "disabled_parameters": int(np.sum(k == 0)),
        "checkout_eol_equivalences": frozen["checkout_eol_equivalences"],
        "extent_method": pre["sampling"]["extent_interval"],
        "domain": pre["domain"], "status": "EVIDENCE_ONLY_NO_KINETIC_REDUCTION_APPROVED"}
    json_write(output / "analysis_diagnostics.json", diagnostics)
    verify_frozen(pre)
    print(json.dumps({"reactions": len(reaction_rows), "species": len(state_rows), "pairs": len(pair_rows),
                      "processes": len(process["process_timescale_evidence"]), "rate_crosscheck": crosscheck}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / AUDIT)
    parser.add_argument("--roadrunner-python", default=os.environ.get("PNAS_ROADRUNNER_PYTHON"))
    parser.add_argument("--engine-evaluate", nargs=3, metavar=("SBML", "SNAPSHOTS", "OUTPUT"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.engine_evaluate:
        engine_evaluate(*args.engine_evaluate)
        return
    interpreter = args.roadrunner_python
    if not interpreter and importlib.util.find_spec("roadrunner"):
        interpreter = sys.executable
    if not interpreter:
        candidate = Path(r"C:\Users\sean\Desktop\GUV\.venv-roadrunner311\Scripts\python.exe")
        if candidate.is_file():
            interpreter = str(candidate)
    if not interpreter:
        parser.error("Supply --roadrunner-python for the independent execution-engine crosscheck")
    analyze(ROOT, args.output_dir.resolve(), interpreter)


if __name__ == "__main__":
    main()
