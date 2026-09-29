#!/usr/bin/env python3
"""Full-coupled fast-mode sign and timescale artifact checks."""
from __future__ import annotations

import csv
import hashlib
import json
import unittest

import numpy as np

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from verify_reduction_audit_v0 import ROOT


RUN_ROOT = ROOT / "results/reduction/r3_aminoacylation_qssa/run_001"
CONDITIONS = ("R3_BASE", "R3_GLYRS_LOW", "R3_METRS_LOW")


class TimescaleTests(unittest.TestCase):
    def test_full_coupled_trajectory_screen_and_hashes(self):
        for condition in CONDITIONS:
            with self.subTest(condition=condition):
                run = RUN_ROOT / condition
                summary = json.loads((run / "timescale.json").read_text(encoding="utf-8"))
                self.assertEqual(summary["status"],
                                 "COUPLED_FULL_TRAJECTORY_TIMESCALE_SCREEN_NOT_QSSA_VALIDATION")
                self.assertEqual(summary["sample_count"], 201)
                self.assertEqual(summary["nonattracting_samples"], 0)
                self.assertGreater(summary["epsilon_screen_fail_samples"], 0)
                self.assertEqual(hashlib.sha256((run / "timescale.csv").read_bytes()).hexdigest(),
                                 summary["timescale_csv_sha256"])
                self.assertEqual(hashlib.sha256((run / "full_state.npz").read_bytes()).hexdigest(),
                                 summary["full_state_sha256"])
                with (run / "timescale.csv").open(encoding="utf-8", newline="") as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual(len(rows), 201)
                self.assertTrue(all(float(row["tau_fast_s"]) > 0 for row in rows))

    def test_fast_mode_sign_mutant_is_nonattracting(self):
        data = np.load(RUN_ROOT / "R3_BASE/full_state.npz")
        runtime = R3ResourceTotalRuntimeV2()
        x0 = data["state"][0]
        z0 = runtime.initial_slow(x0)
        _, gq, _ = runtime.fast_rows(z0, x0[runtime.q_index], x0,
                                     with_jacobian=True)
        self.assertLess(float(np.max(np.real(np.linalg.eigvals(gq)))), 0.)
        self.assertGreater(float(np.min(np.real(np.linalg.eigvals(-gq)))), 0.)


if __name__ == "__main__":
    unittest.main()
