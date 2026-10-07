#!/usr/bin/env python3
"""Check the registered coupled-grid evidence against raw arrays and source files."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest

import numpy as np

from finalize_r3_pilot_v1 import EXPECTED, INPUTS, resolve_attempts
from verify_reduction_audit_v0 import ROOT


RUN = ROOT / "results/reduction/r3_aminoacylation_qssa/run_001"
ATTEMPTS = resolve_attempts(RUN, json.loads((RUN / "attempt_map.json").read_text(encoding="utf-8")))
PROTECTED = {
    "Gly", "Met", "ATP", "ADP", "AMP", "PPi", "PO4",
    "tRNAGlyGCC", "tRNAfMetCAU", "GlytRNAGlyGCC",
    "MettRNAfMetCAU", "fMettRNAfMetCAU",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def max_error(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return max(float(row["E_inf"]) for row in csv.DictReader(stream))


class CoupledGridEvidenceTests(unittest.TestCase):
    def test_terminal_summary_separates_evaluated_failures_from_noncompletion(self):
        summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))
        manifest = json.loads((RUN / "pilot_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["pilot_status"],
                         "R3_PILOT_REJECTED_BY_FULL_COUPLED_VALIDATION")
        self.assertEqual(summary["validated_conditions"], [])
        self.assertEqual(len(summary["evaluated_failed_conditions"]), 9)
        self.assertEqual(summary["incomplete_conditions"], ["R3_ADVERSE"])
        self.assertFalse(summary["validation_grid_complete"])
        self.assertFalse(summary["durable_r3_stage_complete"])
        self.assertEqual(manifest["status"],
                         "HASH_VERIFIED_R3_REJECTION_WITH_INCOMPLETE_CONDITION")
        self.assertEqual(manifest["evaluated_condition_count"], 9)
        self.assertEqual(manifest["incomplete_condition_count"], 1)
        for name, digest in manifest["outputs_sha256"].items():
            self.assertEqual(sha(RUN / name), digest)

    def test_source_and_raw_evidence_are_hash_bound(self):
        for condition in EXPECTED:
            with self.subTest(condition=condition):
                run = ATTEMPTS[condition]
                result = json.loads((run / "result.json").read_text(encoding="utf-8"))
                manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(result["condition_id"], condition)
                self.assertEqual(result["run_kind"], "REGISTERED_R3_GRID_CONDITION")
                if condition == "R3_ADVERSE":
                    self.assertEqual(result["status"], "GRID_CONDITION_INCOMPLETE")
                    self.assertIsNone(manifest["exit_code"])
                    self.assertEqual(result["termination"]["kind"],
                                     "EXTERNAL_STOP_AFTER_DOCUMENTED_NUMERICAL_STALL")
                    self.assertFalse(result["condition_pass"])
                else:
                    self.assertEqual(result["status"], "GRID_CONDITION_EVALUATED")
                    self.assertEqual(manifest["exit_code"], 0)
                self.assertEqual(manifest["result_sha256"], sha(run / "result.json"))
                self.assertEqual(manifest["inputs_sha256"], result["inputs_sha256"])
                self.assertEqual(manifest["outputs_sha256"], result["outputs_sha256"])
                for name, path in INPUTS.items():
                    self.assertEqual(result["inputs_sha256"][name], sha(ROOT / path))
                for name, digest in result["outputs_sha256"].items():
                    self.assertEqual(digest, sha(run / name))

    def test_errors_and_dimensions_are_backed_by_raw_arrays(self):
        for condition in EXPECTED:
            with self.subTest(condition=condition):
                run = ATTEMPTS[condition]
                result = json.loads((run / "result.json").read_text(encoding="utf-8"))
                if condition == "R3_ADVERSE":
                    with np.load(run / "full_state.npz") as full:
                        self.assertEqual(full["state"].shape, (201, 241))
                        self.assertAlmostEqual(float(full["times"][-1]), 1000.)
                    self.assertFalse((run / "state_trajectories.npz").exists())
                    self.assertFalse((run / "directed_ledgers.npz").exists())
                    continue
                with np.load(run / "state_trajectories.npz") as states, np.load(
                    run / "directed_ledgers.npz"
                ) as ledgers:
                    self.assertEqual(states["full_state"].shape, (201, 241))
                    self.assertEqual(states["reduced_state"].shape, (201, 241))
                    self.assertEqual(ledgers["full_rates"].shape, (201, 968))
                    self.assertEqual(ledgers["reduced_rates"].shape, (201, 968))
                    self.assertEqual(ledgers["full_extent"].shape, (201, 968))
                    self.assertEqual(ledgers["reduced_extent"].shape, (201, 968))
                    np.testing.assert_array_equal(states["times"], ledgers["times"])
                    self.assertAlmostEqual(float(states["times"][-1]), 1000.)
                for label, name in (
                    ("all_species_E_inf", "species_errors.csv"),
                    ("all_directed_rate_E_inf", "directed_rate_errors.csv"),
                    ("all_directed_extent_E_inf", "directed_extent_errors.csv"),
                ):
                    self.assertAlmostEqual(result["maxima"][label], max_error(run / name))
                with (run / "species_errors.csv").open(encoding="utf-8", newline="") as stream:
                    species = list(csv.DictReader(stream))
                self.assertEqual(len(species), 241)
                self.assertEqual(len({row["id"] for row in species}), 241)
                self.assertTrue(PROTECTED.issubset({row["id"] for row in species}))
                for name in ("directed_rate_errors.csv", "directed_extent_errors.csv"):
                    with (run / name).open(encoding="utf-8", newline="") as stream:
                        reactions = list(csv.DictReader(stream))
                    self.assertEqual(len(reactions), 968)
                    self.assertEqual(len({row["id"] for row in reactions}), 968)
                    self.assertEqual(sum(row["fast_touch"] == "True" for row in reactions), 103)
                self.assertLessEqual(result["closure_counters"]["max_residual"], 1e-10)
                self.assertEqual(result["limits"], {
                    "closure": 1e-10, "balance": 1e-8, "state": 0.01,
                    "process_rate": 0.05, "cumulative_resource_extent": 0.01,
                })


if __name__ == "__main__":
    unittest.main()
