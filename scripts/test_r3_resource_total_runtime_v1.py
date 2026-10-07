#!/usr/bin/env python3
"""Source-accounting and semantic tests for the dynamic R3 resource chart."""
from __future__ import annotations

import unittest

import numpy as np

from r3_resource_total_runtime_v1 import R3ResourceTotalRuntime


class ResourceTotalRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = R3ResourceTotalRuntime()
        cls.x0 = np.array([float(cls.runtime.source.author_initial[name])
                           for name in cls.runtime.source.species])
        cls.z0 = cls.runtime.initial_slow(cls.x0)
        cls.root = cls.runtime.solve_fast(cls.z0, cls.x0)

    def test_exact_coordinate_inverse_and_inventory(self):
        r = self.runtime
        self.assertEqual(float(np.max(np.abs(r.reconstruct(
            self.z0, self.x0[r.q_index], self.x0) - self.x0))), 0)
        self.assertEqual(float(np.max(np.abs(r.T @ r.D))), 0)
        self.assertEqual(float(np.max(np.abs(r.T @ r.Xz - np.eye(193)))), 0)
        shift = self.root["state"] - self.x0
        self.assertLess(max(abs(sum(float(value) * shift[i] for i, value in law.items()))
                            for law in r.source.laws), 1e-12)
        self.assertFalse({"GlyAMP", "MetAMP"} & set(r.q_names))

    def test_canonical_fast_reaction_accounting_and_physical_root(self):
        r = self.runtime
        self.assertEqual(len(r.fast_reactions), 103)
        self.assertTrue(self.root["valid_local_root"])
        self.assertLessEqual(self.root["residual_max"], 1e-10)
        self.assertGreaterEqual(self.root["min_resource"], -1e-12)
        self.assertGreater(self.root["state"][r.ppi], 0)
        self.assertLess(self.root["state"][r.atp], self.x0[r.atp])
        self.assertEqual(self.root["state"][r.amp], self.x0[r.amp])

    def test_full_source_dynamic_derivative_and_wrong_ppi_sign(self):
        r = self.runtime
        derivative, rates, _ = r.slow_rhs(self.z0, self.root["q"], self.x0)
        full = np.array(r.source.full_rhs_from_rates(rates))
        self.assertLess(float(np.max(np.abs(derivative - r.T @ full))), 1e-10)
        wrong = r.T.copy()
        wrong[r.ppi_pos, r.q_index] *= -1
        self.assertGreater(float(np.max(np.abs(wrong @ r.D))), 0.5)

    def test_implicit_chain_rule_finite_direction(self):
        r = self.runtime
        jac, _ = r.slow_jacobian(self.z0, self.root["q"], self.x0)
        direction = np.zeros(len(self.z0))
        direction[r.atp_pos] = 1
        direction[r.ppi_pos] = 0.2
        direction[r.slow_position[r.source.index["Gly"]]] = 0.1
        step = 1e-4
        plus = r.solve_fast(self.z0 + step * direction, self.x0, seed=self.root["q"])
        minus = r.solve_fast(self.z0 - step * direction, self.x0, seed=self.root["q"])
        self.assertTrue(plus["valid_local_root"] and minus["valid_local_root"])
        finite = (r.slow_rhs(self.z0 + step * direction, plus["q"], self.x0)[0] -
                  r.slow_rhs(self.z0 - step * direction, minus["q"], self.x0)[0]) / (2 * step)
        scale = max(1., float(np.max(np.abs(finite))))
        self.assertLess(float(np.max(np.abs(finite - jac @ direction))) / scale, 1e-6)


if __name__ == "__main__":
    unittest.main()
