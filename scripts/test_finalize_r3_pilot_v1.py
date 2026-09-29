#!/usr/bin/env python3
"""The R3 terminal verdict must remain bound to the registered grid."""
from __future__ import annotations

import csv
import unittest

from finalize_r3_pilot_v1 import GRID, INPUTS, ROOT, check, sha


RUN = ROOT / "results/reduction/r3_aminoacylation_qssa/run_001"
COMPLETE = ("R3_BASE", "R3_GLYRS_LOW", "R3_GLYRS_HIGH", "R3_METRS_LOW")


class PilotFinalizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with GRID.open(encoding="utf-8", newline="") as stream:
            cls.grid = {row["condition_id"]: row for row in csv.DictReader(stream)}
        cls.inputs = {key: sha(ROOT / path) for key, path in INPUTS.items()}

    def test_current_evidence_cannot_be_promoted(self):
        for condition in COMPLETE:
            with self.subTest(condition=condition):
                row = check(condition, RUN / condition, self.inputs, self.grid[condition])
                self.assertEqual(row["condition_pass"], "false")
                self.assertGreater(row["all_species_E_inf"], 0.01)

    def test_mutated_preregistered_role_and_scale_are_rejected(self):
        row = self.grid["R3_GLYRS_LOW"].copy()
        row["role"] = "author_baseline"
        with self.assertRaises(AssertionError):
            check("R3_GLYRS_LOW", RUN / "R3_GLYRS_LOW", self.inputs, row)
        row = self.grid["R3_GLYRS_LOW"].copy()
        row["initial_scale_json"] = '{"GlyRS":10}'
        with self.assertRaises(AssertionError):
            check("R3_GLYRS_LOW", RUN / "R3_GLYRS_LOW", self.inputs, row)


if __name__ == "__main__":
    unittest.main()
