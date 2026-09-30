#!/usr/bin/env python3
"""Independent checks that registered R3 baseline failure remains visible."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest

import numpy as np

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from verify_reduction_audit_v0 import ROOT


RUN = ROOT / "results/reduction/r3_aminoacylation_qssa/run_001/R3_BASE"


class BaselineValidationTests(unittest.TestCase):
    def test_hash_bound_run_is_evaluated_but_not_accepted(self):
        result = json.loads((RUN / "result.json").read_text(encoding="utf-8"))
        manifest = json.loads((RUN / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "GRID_CONDITION_EVALUATED")
        self.assertEqual(result["run_kind"], "REGISTERED_R3_GRID_CONDITION")
        self.assertFalse(result["condition_pass"])
        self.assertEqual(manifest["exit_code"], 0)
        self.assertEqual(manifest["result_sha256"],
                         hashlib.sha256((RUN / "result.json").read_bytes()).hexdigest())
        for name, expected in manifest["outputs_sha256"].items():
            self.assertEqual(hashlib.sha256((RUN / name).read_bytes()).hexdigest(), expected)
        self.assertGreater(result["maxima"]["all_species_E_inf"], 0.01)
        self.assertGreater(result["maxima"]["aminoacylation_rate_E_inf"], 0.05)
        self.assertGreater(result["maxima"]["aminoacylation_extent_E_inf"], 0.01)

    def test_post_layer_charging_failure_from_raw_states(self):
        data = np.load(RUN / "state_trajectories.npz")
        runtime = R3ResourceTotalRuntimeV2()
        post = data["times"] >= 0.05
        with (RUN / "species_errors.csv").open(encoding="utf-8", newline="") as stream:
            rows = {row["id"]: row for row in csv.DictReader(stream)}
        for name in ("MettRNAfMetCAU", "GlytRNAGlyGCC"):
            i = runtime.source.index[name]
            scale = max(float(np.max(np.abs(data["full_state"][:, i]))), 1e-6)
            error = float(np.max(np.abs(data["reduced_state"][post, i] -
                                        data["full_state"][post, i])) / scale)
            self.assertAlmostEqual(error, float(rows[name]["post_0p05_E_inf"]), places=12)
            self.assertGreater(error, 0.01)


if __name__ == "__main__":
    unittest.main()
