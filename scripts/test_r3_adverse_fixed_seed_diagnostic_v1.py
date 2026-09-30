#!/usr/bin/env python3
"""Verify the fixed-seed adverse probe is bound to source and unscored."""
from __future__ import annotations

import hashlib
import json
import unittest

from verify_reduction_audit_v0 import ROOT


BASE = ROOT / "results/reduction/r3_aminoacylation_qssa"
DIRECTORY = BASE / "adverse_fixed_seed_diagnostic_001"
INPUTS = {
    "snapshot": BASE / "adverse_bdf_stepper_001/state_0006.npz",
    "grid": ROOT / "docs/reduction/r3_validation_grid_v1.csv",
    "canonical_sbml": ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml",
    "runtime_v2": ROOT / "scripts/r3_resource_total_runtime_v2.py",
    "script": ROOT / "scripts/diagnose_r3_adverse_fixed_seed_v1.py",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FixedSeedDiagnosticEvidence(unittest.TestCase):
    def test_hashes_and_nonacceptance(self):
        manifest = json.loads((DIRECTORY / "manifest.json").read_text())
        result = json.loads((DIRECTORY / "result.json").read_text())
        self.assertEqual(manifest["status"],
                         "HASH_BOUND_FIXED_SEED_DIAGNOSTIC_NOT_GRID_ACCEPTANCE")
        self.assertEqual(result["status"],
                         "FIXED_SEED_DIAGNOSTIC_NOT_REGISTERED_GRID_RESULT")
        self.assertEqual(manifest["result_sha256"], sha(DIRECTORY / "result.json"))
        for name, path in INPUTS.items():
            with self.subTest(input=name):
                self.assertEqual(manifest["inputs_sha256"][name], sha(path))
        self.assertEqual(result["stop_reason"], "ACCEPTED_STEP_BUDGET")
        self.assertEqual(result["accepted_steps"], 200)
        self.assertEqual(result["rtol"], 1e-10)
        self.assertEqual(result["atol"], 1e-14)
        self.assertLess(result["last_t"], result["start_t"] + 0.1)


if __name__ == "__main__":
    unittest.main()
