#!/usr/bin/env python3
"""Semantic tests for the source-derived R3 candidate runtime and grid screen."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest

import numpy as np

from r3_candidate_runtime_v1 import R3CandidateRuntime
from validate_source_coordinates_full_v1 import rate_jacobian
from verify_reduction_audit_v0 import OUT, ROOT

SCREEN = ROOT / "results/reduction/r3_closure_grid_screen_v1/attempt_005"


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

    def test_implicit_chain_jacobian_rejects_deleted_fast_rows(self):
        runtime = self.runtime
        q = self.root["q"]
        jac, diagnostics = runtime.slow_jacobian(self.z, q, self.author)
        self.assertLess(diagnostics["Gq_condition_number"], 1e6)
        direction = np.zeros(len(self.z))
        for j, name in enumerate(("GlyRS", "MetRS", "tRNAGlyGCC", "tRNAfMetCAU",
                                   "Gly", "Met", "ATP")):
            direction[runtime.slow_position[runtime.source.index[name]]] = np.cos(j + 1)
        direction /= np.linalg.norm(direction)
        step = 1e-4
        plus_z, minus_z = self.z + step * direction, self.z - step * direction
        plus = runtime.solve_fast(plus_z, self.author, seed=q)
        minus = runtime.solve_fast(minus_z, self.author, seed=q)
        self.assertTrue(plus["valid_local_root"] and minus["valid_local_root"])
        finite = (runtime.slow_rhs(plus_z, plus["q"], self.author)[0] -
                  runtime.slow_rhs(minus_z, minus["q"], self.author)[0]) / (2 * step)
        scale = max(1.0, float(np.max(np.abs(finite))))
        self.assertLess(float(np.max(np.abs(finite - jac @ direction))) / scale, 1e-6)
        full_jac = runtime.S @ rate_jacobian(runtime.source, self.root["state"])
        deleted_fast_rows = runtime.T @ (full_jac @ runtime.Xz)
        self.assertGreater(float(np.max(np.abs(finite - deleted_fast_rows @ direction))) / scale, 1e-2)

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

    def test_coupled_smoke_failure_evidence_is_not_acceptance(self):
        run = ROOT / "results/reduction/r3_coupled_smoke_v1"
        failed = json.loads((run / "attempt_001/result.json").read_text(encoding="utf-8"))
        solved = json.loads((run / "attempt_002/result.json").read_text(encoding="utf-8"))
        self.assertIn("Invalid closure", failed["failure"])
        self.assertEqual(solved["status"], "EXPLORATORY_COUPLED_SMOKE_SOLVED_NOT_R3_VALIDATION")
        self.assertTrue(solved["full_solver"]["success"] and solved["reduced_solver"]["success"])
        self.assertLessEqual(solved["closure_counters"]["max_fast_residual"], 1e-10)
        self.assertGreater(solved["exploratory_metrics"]["all_species_max_E_inf"], 0.01)
        self.assertGreater(solved["exploratory_metrics"]["class_I_max_E_inf"], 0.01)


if __name__ == "__main__":
    unittest.main()
