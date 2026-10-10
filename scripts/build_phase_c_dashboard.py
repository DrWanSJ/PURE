#!/usr/bin/env python3
"""Read frozen Phase C evidence into the existing atlas; never run an experiment.

The JSON is a deterministic, portable presentation contract. --check compares its
bytes with a fresh derivation and verifies every recorded input hash.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from fractions import Fraction
import xml.etree.ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "docs/visualization/phase_c_release_v1.json"
RESULT = "results/reduction/rapid_v1/"
DOC = "docs/reduction/rapid_reduction/"
CONFIG = "configs/reduction/rapid_v1.json"
SBML = "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
PARAMETERS = "models/pnas2017_full_reference/original/parameters.csv"
FINAL = "R3_CHAIN12_RECYCLE"
MODELS = ["R0", "R1", "R2", "R3_CHAIN1", "R3_CHAIN12", "R3_RECYCLE", FINAL]
SCENARIOS = ["AUTHOR_BASELINE", "FLOW_CHALLENGE", "ENERGY_FACTOR_LIMITED", "COMPETITION_OCCUPANCY"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def serialize(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def build_data():
    sources = {}

    def source(path):
        p = ROOT / path
        sources[path] = {"path": path, "bytes": p.stat().st_size, "sha256": digest(p),
                         "authority": "SOURCE_EVIDENCE" if not path.startswith("scripts/") else "DERIVATION_CODE"}
        return p

    def read(path):
        return json.loads(source(path).read_text(encoding="utf-8"))

    cfg = read(CONFIG)
    cert = read(DOC + "mathematical_certificate.json")
    validation = read(RESULT + "validation_results.json")
    summary = read(RESULT + "model_summary.json")
    ribosome = read(RESULT + "ribosome_errors.json")
    local = read(RESULT + "local_validation.json")
    freeze = read(RESULT + "freeze.json")
    decision = read(DOC + "current_decision_v1.json")
    source(DOC + "protocol.md")
    source(DOC + "candidate_source_map.json")
    source(DOC + "reduction_report.md")
    source(DOC + "b1_3_independent_scientific_audit.md")
    source("scripts/build_phase_c_dashboard.py")
    for asset in ["build_reduction_reasoning_atlas.py", "reduction_reasoning_atlas.template.html", "phase_c_dashboard.css", "phase_c_dashboard.js", "phase_c_dashboard.inc"]:
        source("scripts/" + asset)
    for name in ["runtime.py", "mathematics.py", "common.py", "score_saved.py"]:
        source("scripts/reduction/rapid_v1/" + name)
    assert digest(ROOT / CONFIG) == freeze["config_sha256"] == validation["config_sha256"]
    assert digest(ROOT / (DOC + "protocol.md")) == freeze["protocol_sha256"]
    assert digest(ROOT / (DOC + "mathematical_certificate.json")) == "c698ca685bf1052f529c9b8b2bb3626c2a3176818e868469cf9b29e6f3e26df0"
    xml = source(SBML)
    assert digest(xml) == "dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df"
    # Use the source reader's authoritative author overlay path, never guess it.
    sys.path.insert(0, str(ROOT / "scripts"))
    import verify_reduction_audit_v0 as original
    parameter_path = original.AUTHOR / "fMGG_synthesis_parameters.csv" if hasattr(original, "AUTHOR") else None
    if parameter_path is None:
        candidates = [p for p in (ROOT / "models/pnas2017_full_reference").rglob("*.csv")
                      if digest(p) == "cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465"]
        assert len(candidates) == 1, "Cannot uniquely locate frozen author parameters"
        parameter_path = candidates[0]
    source(parameter_path.relative_to(ROOT).as_posix())
    assert digest(parameter_path) == "cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465"
    sys.path.insert(0, str(ROOT / "scripts/reduction/rapid_v1"))
    from runtime import observable_matrix

    source("scripts/verify_reduction_audit_v0.py")
    species, rxns = original.parse(xml)
    selected_ids = ["re000000" + x for x in ["0001", "0016", "0017", "0018", "0077", "0078", "0079", "0796", "0797", "0798", "0799", "0810", "0811", "0812", "0813", "0814", "0823", "0847", "0902", "0910", "0911", "0913", "0916", "0918", "0306", "0952", "0414"]]
    reactions = {}
    for r in rxns:
        rid = r["id"]
        if rid not in selected_ids:
            continue
        sides = {side: {name: str(value) for name, value in r[side].items()}
                 for side in ["reactants", "products"]}
        reactions[rid] = {"id": rid, **sides, "author_k_exact": cfg["author_parameters_exact"][rid]}
    assert len(species) == cert["exact_source_matrix_shape"][0] == 241
    assert len(rxns) == cert["exact_source_matrix_shape"][1] == 968
    assert float(reactions["re0000000414"]["products"]["PO4"]) == 2
    summaries = {r["model"]: r for r in summary}
    assert set(summaries) == set(MODELS)
    trajectories = {}
    comparisons = {}
    labels = None
    counter_names = None
    for scenario in SCENARIOS:
        comparisons[scenario] = {m: validation["scenarios"][scenario]["models"][m] for m in MODELS if m != "R0"}
        trajectories[scenario] = {}
        for model in ["R0", FINAL]:
            # Frozen score_saved.py uses tight BDF as the common reference.
            tag = scenario + "__" + ("R0_TIGHT" if model == "R0" else model)
            diag = read(RESULT + "trajectories/" + tag + ".json")
            assert diag["config_sha256"] == freeze["config_sha256"]
            assert diag["success"] and diag["scenario"] == scenario and diag["model"] == model
            assert diag["extra_counter_dimension"] == 20
            names, matrix, _ = observable_matrix(diag["source_species_order"])
            if labels is None:
                labels, counter_names = names, diag["counter_names"]
            assert labels == names and counter_names == diag["counter_names"]
            with np.load(source(RESULT + "trajectories/" + tag + ".npz")) as z:
                np.testing.assert_array_equal(z["t"], cfg["observation_grid"])
                values = np.concatenate([matrix @ z["X"], z["counters"]], axis=0)
                assert np.all(np.isfinite(values))
                trajectories[scenario][model] = values.tolist()
        comp = comparisons[scenario][FINAL]["comparison"]
        assert comp["long_gates_pass"]
        scales = np.array([comp["fixed_scales"][s] for s in labels] +
                          [comp["counter_fixed_scales"][s] for s in counter_names])
        difference = np.abs(np.array(trajectories[scenario][FINAL]) - np.array(trajectories[scenario]["R0"])) / scales[:, None]
        for window in comp["windows"]:
            low, high = window["range"]
            mask = (np.array(cfg["observation_grid"]) >= low) & (np.array(cfg["observation_grid"]) <= high)
            calculated = [difference[0, mask].max(), difference[1:len(labels), mask].max(), difference[len(labels):, mask].max()]
            reported = [window[k] for k in ["peptide_max", "resource_max", "cumulative_max"]]
            np.testing.assert_allclose(calculated, reported, rtol=2e-9, atol=2e-14)
    assert all(summaries[m]["counter_dimension"] == len(counter_names) for m in MODELS)
    local_early = max(r["windows"][0]["resource_error"] for r in local if r.get("fixture") == "INTERNAL_NONZERO")
    proof = cert["projection_proofs"]["R3_RECYCLE"]
    final = summaries[FINAL]
    for key, val in final["maxima_long"].items():
        assert val == max(comparisons[s][FINAL]["comparison"]["windows"][-1][key] for s in SCENARIOS)
    return {
        "schema": "pnas2017_phase_c_dashboard/v1", "authority": "DERIVED_PRESENTATION_ONLY",
        "milestone_id": decision["milestone_id"], "current_decision": decision,
        "freshness": {"status": "INPUT_HASHES_AND_SAVED_ERRORS_VERIFIED", "method": "python -B scripts/build_phase_c_dashboard.py --check",
                      "scope": "Build-time byte hashes and saved trajectory error verification; no fresh ODE solve in dashboard build."},
        "source": {"species": len(species), "canonical_directions": len(rxns),
                   "positive_author_directions": sum(Fraction(v) > 0 for v in cfg["author_parameters_exact"].values()),
                   "support_directions": final["mapped_source_directions"], "source_time_unit": cfg["time_unit"]},
        "models": summary,
        "mathematics": {k: cert[k] for k in ["source_rank", "source_left_nullity", "author_support_species", "zero_count", "support_live_rank", "charts", "projection_proofs", "closure_counterexamples"]},
        "quotient": {"microstates": proof["P_rank"] + proof["kernel_dimension"], "observables": proof["P_rank"], **proof},
        "config": {k: cfg[k] for k in ["gates", "scale_rule", "windows", "solver", "tight_solver", "performance_repeats"]},
        "scenarios": [s for s in cfg["scenarios"] if s["id"] in SCENARIOS],
        "comparisons": comparisons, "ribosome_long_errors": ribosome,
        "local_early_resource_error": local_early, "local_failure_evidence": local,
        "out_of_domain": validation["scenarios"]["ZERO_BRANCH_REACTIVATION"],
        "grid": cfg["observation_grid"], "observable_labels": labels,
        "plotted_reference": "R0_TIGHT", "plotted_candidate": FINAL,
        "counter_names": counter_names, "trajectory_labels": labels + counter_names,
        "trajectories": trajectories, "reactions": reactions,
        "inputs": [sources[k] for k in sorted(sources)],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    data = build_data()
    expected = serialize(data).encode("utf-8")
    if args.check:
        assert DATA_PATH.read_bytes() == expected, "Presentation data is stale; rebuild the existing atlas"
        print("PASS: Phase C schema, hashes, all scenario/window stored errors, deterministic data freshness")
    else:
        DATA_PATH.write_bytes(expected)
        print(DATA_PATH.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
