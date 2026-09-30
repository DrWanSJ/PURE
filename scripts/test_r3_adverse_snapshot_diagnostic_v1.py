#!/usr/bin/env python3
"""Verify the reduced-state numerical diagnostic remains hash-bound and unscored."""
from __future__ import annotations

import hashlib
import json
import unittest

from verify_reduction_audit_v0 import ROOT


DIRECTORY = ROOT / "results/reduction/r3_aminoacylation_qssa/adverse_snapshot_diagnostic_001"
INPUTS = {
    "snapshot": ROOT / "results/reduction/r3_aminoacylation_qssa/adverse_bdf_stepper_001/state_0006.npz",
    "grid": ROOT / "docs/reduction/r3_validation_grid_v1.csv",
    "canonical_sbml": ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml",
    "runtime_v2": ROOT / "scripts/r3_resource_total_runtime_v2.py",
    "precise_diagnostic": ROOT / "scripts/r3_resource_total_precise_diagnostic_v1.py",
    "script": ROOT / "scripts/diagnose_r3_adverse_snapshot_v1.py",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AdverseSnapshotDiagnosticEvidence(unittest.TestCase):
    def test_provenance_and_nonacceptance(self):
        manifest = json.loads((DIRECTORY / "manifest.json").read_text())
        result = json.loads((DIRECTORY / "result.json").read_text())
        self.assertEqual(manifest["status"],
                         "HASH_BOUND_SNAPSHOT_DIAGNOSTIC_NOT_GRID_ACCEPTANCE")
        self.assertEqual(result["status"],
                         "REDUCED_SNAPSHOT_DIAGNOSTIC_NOT_REGISTERED_GRID_RESULT")
        self.assertEqual(manifest["exit_code"], 0)
        self.assertEqual(manifest["result_sha256"], sha(DIRECTORY / "result.json"))
        for name, path in INPUTS.items():
            with self.subTest(input=name):
                self.assertEqual(manifest["inputs_sha256"][name], sha(path))
        self.assertGreater(result["snapshot_t"], 359.)
        self.assertLess(result["snapshot_t"], 360.)
        self.assertLessEqual(result["root_residual_max"], 1e-10)
        self.assertEqual(len(result["local_trials"]), 3)
        for trial in result["local_trials"]:
            with self.subTest(trial=trial["name"]):
                self.assertEqual(trial["rtol"], 1e-10)
                self.assertEqual(trial["atol"], 1e-14)
                self.assertFalse(trial["success"])
                self.assertEqual(trial["error"], "RHS call budget")
                self.assertEqual(trial["nfev"], 5001)
                self.assertLess(trial["last_t"], trial["target_t"])


if __name__ == "__main__":
    unittest.main()
