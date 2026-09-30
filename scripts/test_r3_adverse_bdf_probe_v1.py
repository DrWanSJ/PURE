#!/usr/bin/env python3
"""Keep the adverse BDF snapshots hash-bound and outside grid acceptance."""
from __future__ import annotations

import hashlib
import json
import unittest

import numpy as np

from verify_reduction_audit_v0 import ROOT


BASE = ROOT / "results/reduction/r3_aminoacylation_qssa"
INPUTS = {
    "canonical_sbml": ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml",
    "grid": ROOT / "docs/reduction/r3_validation_grid_v1.csv",
    "method": ROOT / "docs/reduction/r3_aminoacylation_qssa_method.md",
    "protocol": ROOT / "docs/reduction/r3_coupled_validation_protocol_v1.md",
    "runtime_v1": ROOT / "scripts/r3_resource_total_runtime_v1.py",
    "runtime_v2": ROOT / "scripts/r3_resource_total_runtime_v2.py",
    "script": ROOT / "scripts/probe_r3_adverse_bdf_state_v1.py",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AdverseBdfProbeEvidence(unittest.TestCase):
    def test_bounded_snapshots_are_not_full_grid_comparisons(self):
        for directory_name in ("adverse_bdf_stepper_smoke_001",
                               "adverse_bdf_stepper_001"):
            with self.subTest(directory=directory_name):
                directory = BASE / directory_name
                manifest = json.loads((directory / "manifest.json").read_text())
                result = json.loads((directory / "result.json").read_text())
                progress = json.loads((directory / "progress.json").read_text())
                self.assertEqual(manifest["status"],
                                 "HASH_BOUND_DIAGNOSTIC_NOT_GRID_ACCEPTANCE")
                self.assertEqual(result["status"],
                                 "DIAGNOSTIC_ONLY_NOT_REGISTERED_GRID_RESULT")
                self.assertEqual(result["stop_reason"], "WALL_TIME_BUDGET")
                self.assertIsNone(result["failure"])
                self.assertLess(result["last_t"], 1000.)
                self.assertEqual(progress["rtol"], 1e-10)
                self.assertEqual(progress["atol"], 1e-14)
                self.assertEqual(manifest["result_sha256"], sha(directory / "result.json"))
                self.assertEqual(manifest["progress_sha256"], sha(directory / "progress.json"))
                self.assertEqual(manifest["script_sha256"], sha(INPUTS["script"]))
                for key, path in INPUTS.items():
                    self.assertEqual(result["inputs_sha256"][key], sha(path))
                times = []
                for item in progress["snapshots"]:
                    path = directory / item["name"]
                    self.assertEqual(item["sha256"], sha(path))
                    self.assertEqual(result["snapshot_sha256"][item["name"]], sha(path))
                    with np.load(path) as state:
                        self.assertEqual(state["z"].shape, (193,))
                        self.assertEqual(state["q"].shape, (21,))
                        self.assertEqual(state["state"].shape, (241,))
                        self.assertEqual(float(state["t"]), item["t"])
                    self.assertTrue(item["root_valid"])
                    self.assertLessEqual(item["root_residual_max"], 1e-10)
                    times.append(item["t"])
                self.assertEqual(times, sorted(times))
                self.assertEqual(times[-1], result["last_t"])
        self.assertGreater(
            json.loads((BASE / "adverse_bdf_stepper_001/progress.json").read_text())
            ["snapshots"][-1]["t"], 359.)


if __name__ == "__main__":
    unittest.main()
