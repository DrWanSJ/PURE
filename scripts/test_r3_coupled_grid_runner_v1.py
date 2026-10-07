#!/usr/bin/env python3
"""Directed gross-extent and retained diagnostic evidence tests."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest

import numpy as np

from run_r3_coupled_grid_v1 import integrate_extents
from verify_reduction_audit_v0 import ROOT


RUN = ROOT / "results/reduction/r3_grid_runner_diagnostic_v1/attempt_001"


class GridRunnerTests(unittest.TestCase):
    def test_directed_gross_channels_are_not_abs_net(self):
        def rates(_t, _state):
            value = np.zeros(968)
            value[0] = 10
            value[1] = 9
            return value

        extents, stats = integrate_extents(lambda t: np.array([t]), rates,
                                           np.array([0., 0.1, 1.]))
        self.assertEqual(stats["segments"], 2)
        self.assertAlmostEqual(extents[-1, 0], 10, places=10)
        self.assertAlmostEqual(extents[-1, 1], 9, places=10)
        self.assertNotAlmostEqual(extents[-1, 0], abs(10 - 9), places=5)

    def test_short_diagnostic_is_labeled_and_hash_bound(self):
        result = json.loads((RUN / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(result["run_kind"], "EXPLORATORY_DIAGNOSTIC")
        self.assertEqual(result["status"], "GRID_CONDITION_EVALUATED")
        self.assertFalse(result["condition_pass"])
        self.assertEqual(result["solver"]["report_points"], 201)
        self.assertEqual(result["solver"]["rtol"], 1e-10)
        self.assertEqual(result["solver"]["atol"], 1e-14)
        for name, expected in result["outputs_sha256"].items():
            self.assertEqual(hashlib.sha256((RUN / name).read_bytes()).hexdigest(), expected)
        for name, count in (("species_errors.csv", 241),
                            ("directed_rate_errors.csv", 968),
                            ("directed_extent_errors.csv", 968)):
            with (RUN / name).open(encoding="utf-8", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), count)


if __name__ == "__main__":
    unittest.main()
