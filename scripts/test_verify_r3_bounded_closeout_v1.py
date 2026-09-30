#!/usr/bin/env python3
"""The closeout check must preserve the incomplete-grid boundary."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from verify_r3_bounded_closeout_v1 import RUN, read_json, verify


class BoundedCloseoutTests(unittest.TestCase):
    def test_hash_verified_partial_evidence_is_not_terminal_acceptance(self):
        result = verify()
        self.assertEqual(result["closeout_status"],
                         "HASH_VERIFIED_BOUNDED_R3_CLOSEOUT")
        self.assertEqual(result["completed_full_coupled_comparisons"], 9)
        self.assertEqual(result["incomplete_conditions"], ["R3_ADVERSE"])
        self.assertEqual(result["original_full_grid_protocol"], "INCOMPLETE")
        self.assertFalse(result["original_terminal_acceptance_claim"])

    def test_false_full_grid_completion_is_rejected(self):
        original = read_json

        def false_completion(path):
            value = original(path)
            if path == RUN / "summary.json":
                value["validation_grid_complete"] = True
            return value

        with patch("verify_r3_bounded_closeout_v1.read_json",
                   side_effect=false_completion):
            with self.assertRaises(AssertionError):
                verify()


if __name__ == "__main__":
    unittest.main()
