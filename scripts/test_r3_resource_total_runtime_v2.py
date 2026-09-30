#!/usr/bin/env python3
"""Warm-start solver equivalence and physical-domain rejection tests."""
from __future__ import annotations

import unittest

import numpy as np

from r3_resource_total_runtime_v1 import R3ResourceTotalRuntime
from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from verify_reduction_audit_v0 import ROOT


class WarmStartTests(unittest.TestCase):
    def test_saved_coupled_states_match_hybr(self):
        data = np.load(ROOT / "results/reduction/r3_resource_total_smoke_v1/attempt_001/trajectories.npz")
        initial = data["full_state"][0]
        baseline = R3ResourceTotalRuntime()
        accelerated = R3ResourceTotalRuntimeV2()
        comparison = []
        for state in data["reduced_state"]:
            z = baseline.initial_slow(state)
            a = baseline.solve_fast(z, initial)
            b = accelerated.solve_fast(z, initial)
            self.assertTrue(a["valid_local_root"] and b["valid_local_root"])
            self.assertEqual(b["method"], "warm_start_newton")
            comparison.append(float(np.max(np.abs(a["state"] - b["state"]))))
        self.assertLess(max(comparison), 1e-10)

    def test_negative_atp_domain_falls_back_and_rejects(self):
        r = R3ResourceTotalRuntimeV2()
        initial = np.array([float(r.source.author_initial[name]) for name in r.source.species])
        z = r.initial_slow(initial)
        good = r.solve_fast(z, initial)
        self.assertTrue(good["valid_local_root"])
        z[r.atp_pos] = -1
        bad = r.solve_fast(z, initial, seed=good["q"])
        self.assertEqual(bad["method"], "hybr_fallback")
        self.assertFalse(bad["valid_local_root"])
        self.assertLess(bad["min_resource"], -0.1)


if __name__ == "__main__":
    unittest.main()
