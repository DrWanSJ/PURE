#!/usr/bin/env python3
"""Check the registered coupled-grid evidence against raw arrays and source files."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest

import numpy as np

from verify_reduction_audit_v0 import ROOT


RUN = ROOT / "results/reduction/r3_aminoacylation_qssa/run_001"
CONDITIONS = ("R3_BASE", "R3_GLYRS_LOW", "R3_GLYRS_HIGH", "R3_METRS_LOW")
INPUTS = {
    "canonical_sbml": "models/pnas2017_full_reference/original/fMGG_synthesis.xml",
    "grid": "docs/reduction/r3_validation_grid_v1.csv",
    "method": "docs/reduction/r3_aminoacylation_qssa_method.md",
    "protocol": "docs/reduction/r3_coupled_validation_protocol_v1.md",
    "reaction_map": "docs/reduction/r3_source_reaction_candidate_map_v1.csv",
    "aminoacylation_reactions": "models/pnas2017_full_reference/audit/aminoacylation_reactions.csv",
    "runtime_v1": "scripts/r3_resource_total_runtime_v1.py",
    "runtime_v2": "scripts/r3_resource_total_runtime_v2.py",
    "runner": "scripts/run_r3_coupled_grid_v1.py",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def max_error(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return max(float(row["E_inf"]) for row in csv.DictReader(stream))


class CoupledGridEvidenceTests(unittest.TestCase):
    def test_source_and_raw_evidence_are_hash_bound(self):
        for condition in CONDITIONS:
            with self.subTest(condition=condition):
                run = RUN / condition
                result = json.loads((run / "result.json").read_text(encoding="utf-8"))
                manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(result["condition_id"], condition)
                self.assertEqual(result["status"], "GRID_CONDITION_EVALUATED")
                self.assertEqual(result["run_kind"], "REGISTERED_R3_GRID_CONDITION")
                self.assertEqual(manifest["exit_code"], 0)
                self.assertEqual(manifest["result_sha256"], sha(run / "result.json"))
                self.assertEqual(manifest["inputs_sha256"], result["inputs_sha256"])
                self.assertEqual(manifest["outputs_sha256"], result["outputs_sha256"])
                for name, path in INPUTS.items():
                    self.assertEqual(result["inputs_sha256"][name], sha(ROOT / path))
                for name, digest in result["outputs_sha256"].items():
                    self.assertEqual(digest, sha(run / name))

    def test_errors_and_dimensions_are_backed_by_raw_arrays(self):
        for condition in CONDITIONS:
            with self.subTest(condition=condition):
                run = RUN / condition
                result = json.loads((run / "result.json").read_text(encoding="utf-8"))
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
                self.assertLessEqual(result["closure_counters"]["max_residual"], 1e-10)
                self.assertFalse(result["condition_pass"])
                self.assertGreater(result["maxima"]["all_species_E_inf"], 0.01)
                self.assertGreater(result["maxima"]["aminoacylation_extent_E_inf"], 0.01)


if __name__ == "__main__":
    unittest.main()
