#!/usr/bin/env python3
"""Semantic tests for the source-derived R3 candidate runtime and grid screen."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest

import numpy as np

from r3_candidate_runtime_v1 import R3CandidateRuntime
from verify_reduction_audit_v0 import OUT, ROOT

SCREEN = ROOT / "results/reduction/r3_closure_grid_screen_v1/attempt_003"


class CandidateRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = R3CandidateRuntime()
        cls.author = np.array([float(cls.runtime.source.author_initial[name])
                               for name in cls.runtime.source.species])
        cls.z = cls.runtime.initial_slow(cls.author)
        cls.root = cls.runtime.solve_fast(cls.z, cls.author)

    def test_exact_base_and_dynamic_free_adenylates(self):
        runtime = self.runtime
        self.assertEqual(runtime.source.certificate_name, "source_coordinate_certificate_v4.json")
        self.assertEqual(len(runtime.q_index), 21)
        self.assertEqual(len(runtime.slow_index), 193)
        self.assertFalse({"GlyAMP", "MetAMP"} & set(runtime.q_names))
        self.assertTrue({runtime.source.index[name] for name in ("GlyAMP", "MetAMP")} <=
                        set(runtime.slow_index))
        self.assertEqual(float(np.max(np.abs(runtime.reconstruct(
            self.z, self.author[runtime.q_index], self.author) - self.author))), 0.0)

    def test_analytic_fast_jacobian_and_sign_mutant(self):
        runtime = self.runtime
        q = self.root["q"]
        _, jac, _ = runtime.fast_rows(self.z, q, self.author, True)
        direction = np.cos(np.arange(len(q), dtype=float))
        direction /= np.linalg.norm(direction)
        step = 1e-7
        finite = (runtime.fast_rows(self.z, q + step * direction, self.author)[0] -
                  runtime.fast_rows(self.z, q - step * direction, self.author)[0]) / (2 * step)
        scale = max(1.0, float(np.max(np.abs(jac @ direction))))
        self.assertLess(float(np.max(np.abs(finite - jac @ direction))) / scale, 1e-7)
        saved = runtime.D.copy()
        try:
            runtime.D[runtime.carrier_index[0]] *= -1
            _, wrong_jac, _ = runtime.fast_rows(self.z, q, self.author, True)
        finally:
            runtime.D[:] = saved
        self.assertGreater(float(np.max(np.abs(finite - wrong_jac @ direction))) / scale, 1e-4)

    def test_physical_root_and_source_general_inventory(self):
        self.assertTrue(self.root["valid_local_root"])
        self.assertLessEqual(self.root["residual_max"], 1e-10)
        self.assertGreaterEqual(self.root["min_q"], -1e-12)
        self.assertGreaterEqual(self.root["min_carrier"], -1e-12)
        difference = self.root["state"] - self.author
        law_shift = max(abs(sum(float(value) * difference[i] for i, value in law.items()))
                        for law in self.runtime.source.laws)
        self.assertLess(law_shift, 1e-10)
        z_rhs, rates, _ = self.runtime.slow_rhs(self.z, self.root["q"], self.author)
        full_rhs = np.array(self.runtime.source.full_rhs_from_rates(rates))
        q_rhs = full_rhs[self.runtime.q_index]
        for row, i in enumerate(self.runtime.carrier_index):
            self.assertAlmostEqual(z_rhs[self.runtime.slow_position[i]],
                                   full_rhs[i] - self.runtime.C[row] @ q_rhs, delta=1e-8)

    def test_registered_grid_screen_and_hashes(self):
        result = json.loads((SCREEN / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "EXPLORATORY_INITIAL_ROOT_SCREEN_NOT_R3_VALIDATION")
        self.assertEqual(result["physical_multistart_conditions"], 10)
        for path, expected in ((SCREEN / "screen.csv", result["screen_csv_sha256"]),
                               (ROOT / "scripts/r3_candidate_runtime_v1.py", result["runtime_script_sha256"]),
                               (ROOT / "scripts/screen_r3_closure_grid_v1.py", result["screen_script_sha256"]),
                               (OUT / "r3_validation_grid_v1.csv", result["grid_sha256"])):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
        with (SCREEN / "screen.csv").open(encoding="utf-8", newline="") as stream:
            data = list(csv.DictReader(stream))
        self.assertEqual(len(data), 10)
        self.assertTrue(all(row["first_root_physical"] == row["second_root_physical"] == "true"
                            and row["same_local_branch"] == "true"
                            and float(row["first_residual_max"]) <= 1e-10
                            and float(row["max_source_general_law_shift"]) <= 1e-10
                            for row in data))
        adverse = next(row for row in data if row["condition_id"] == "R3_ADVERSE")
        self.assertGreater(float(adverse["first_hybr_initial_residual_max"]), 1e-10)
        self.assertGreater(int(adverse["first_newton_refinement_steps"]), 0)


if __name__ == "__main__":
    unittest.main()
