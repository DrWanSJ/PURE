#!/usr/bin/env python3
"""The R3 pilot verdict must remain bound to the registered grid."""
from __future__ import annotations

import csv
import json
import unittest
from unittest.mock import patch

from finalize_r3_pilot_v1 import (EXPECTED, GRID, INPUTS, ROOT, check,
                                  read_json, resolve_attempts, sha)


RUN = ROOT / "results/reduction/r3_aminoacylation_qssa/run_001"
class PilotFinalizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with GRID.open(encoding="utf-8", newline="") as stream:
            cls.grid = {row["condition_id"]: row for row in csv.DictReader(stream)}
        cls.inputs = {key: sha(ROOT / path) for key, path in INPUTS.items()}

    def test_current_evidence_cannot_be_promoted(self):
        mapping = json.loads((RUN / "attempt_map.json").read_text(encoding="utf-8"))
        attempts = resolve_attempts(RUN, mapping)
        for condition in EXPECTED:
            with self.subTest(condition=condition):
                row = check(condition, attempts[condition], self.inputs, self.grid[condition])
                self.assertEqual(row["condition_pass"], "false")
                if condition == "R3_ADVERSE":
                    self.assertEqual(row["result_status"], "GRID_CONDITION_INCOMPLETE")
                    self.assertIsNone(row["all_species_E_inf"])
                else:
                    self.assertGreater(row["all_species_E_inf"], 0.01)

    def test_stalled_attempt_requires_explicit_termination_and_unfinished_time(self):
        directory = RUN.parent / "restart_001/R3_ADVERSE"
        original = read_json

        def missing_termination(path):
            value = original(path)
            if path == directory / "manifest.json":
                value["termination"]["kind"] = "UNVERIFIED_STOP"
            return value

        with patch("finalize_r3_pilot_v1.read_json", side_effect=missing_termination):
            with self.assertRaises(AssertionError):
                check("R3_ADVERSE", directory, self.inputs, self.grid["R3_ADVERSE"])

        def false_completion(path):
            value = original(path)
            if path == directory / "stall_diagnostic.json":
                value["samples"][-1]["bdf_time_s"] = 1000
            return value

        with patch("finalize_r3_pilot_v1.read_json", side_effect=false_completion):
            with self.assertRaises(AssertionError):
                check("R3_ADVERSE", directory, self.inputs, self.grid["R3_ADVERSE"])

    def test_mutated_preregistered_role_and_scale_are_rejected(self):
        row = self.grid["R3_GLYRS_LOW"].copy()
        row["role"] = "author_baseline"
        with self.assertRaises(AssertionError):
            check("R3_GLYRS_LOW", RUN / "R3_GLYRS_LOW", self.inputs, row)
        row = self.grid["R3_GLYRS_LOW"].copy()
        row["initial_scale_json"] = '{"GlyRS":10}'
        with self.assertRaises(AssertionError):
            check("R3_GLYRS_LOW", RUN / "R3_GLYRS_LOW", self.inputs, row)

    def test_attempt_map_requires_exact_condition_and_local_path(self):
        mapping = {name: f"run_001/{name}" for name in EXPECTED}
        attempts = resolve_attempts(RUN, mapping)
        self.assertEqual(attempts["R3_BASE"], (RUN / "R3_BASE").resolve())
        missing = mapping.copy()
        del missing["R3_ADVERSE"]
        with self.assertRaises(AssertionError):
            resolve_attempts(RUN, missing)
        traversal = mapping.copy()
        traversal["R3_ADVERSE"] = "../outside/R3_ADVERSE"
        with self.assertRaises(AssertionError):
            resolve_attempts(RUN, traversal)
        substituted = mapping.copy()
        substituted["R3_ADVERSE"] = "run_001/R3_BASE"
        with self.assertRaises(AssertionError):
            resolve_attempts(RUN, substituted)


if __name__ == "__main__":
    unittest.main()
