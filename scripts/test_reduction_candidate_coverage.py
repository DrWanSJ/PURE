#!/usr/bin/env python3
"""Semantic mutants for exact conservation candidate enumeration."""
from __future__ import annotations

import copy
import unittest

from verify_reduction_audit_v0 import OUT, check_candidate_coverage, rows


class CandidateCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.laws = rows(OUT / "conservation_laws_v0.csv")
        cls.candidates = rows(OUT / "conservation_elimination_candidates_v0.csv")

    def test_source_artifact_has_complete_unique_coverage(self):
        check_candidate_coverage(self.laws, self.candidates)

    def test_real_pr_duplicate_replacement_with_unchanged_count(self):
        mutant = copy.deepcopy(self.candidates)
        donor, replaced = mutant[1], mutant[2]
        self.assertEqual(donor["conservation_id"], replaced["conservation_id"])
        self.assertEqual(donor["species_information_class"], replaced["species_information_class"])
        mutant[2] = {**donor, "candidate_id": replaced["candidate_id"]}
        self.assertEqual(len(mutant), len(self.candidates))
        self.assertEqual(len({r["candidate_id"] for r in mutant}), len(mutant))
        with self.assertRaisesRegex(AssertionError, "duplicate .* candidate"):
            check_candidate_coverage(self.laws, mutant)

    def test_duplicate_conservation_id(self):
        mutant = copy.deepcopy(self.laws)
        mutant[1]["conservation_id"] = mutant[0]["conservation_id"]
        with self.assertRaisesRegex(AssertionError, "duplicate conservation_id"):
            check_candidate_coverage(mutant, self.candidates)

    def test_duplicate_candidate_id(self):
        mutant = copy.deepcopy(self.candidates)
        mutant[1]["candidate_id"] = mutant[0]["candidate_id"]
        with self.assertRaisesRegex(AssertionError, "duplicate candidate_id"):
            check_candidate_coverage(self.laws, mutant)

    def test_missing_pair(self):
        mutant = copy.deepcopy(self.candidates[1:])
        with self.assertRaisesRegex(AssertionError, "candidate coverage mismatch: missing="):
            check_candidate_coverage(self.laws, mutant)

    def test_extra_pair(self):
        mutant = copy.deepcopy(self.candidates)
        mutant.append({**mutant[0], "candidate_id": "ELIM_EXTRA", "eliminated_species": "NOT_IN_LAW"})
        with self.assertRaisesRegex(AssertionError, "candidate coverage mismatch: missing=.*extra="):
            check_candidate_coverage(self.laws, mutant)


if __name__ == "__main__":
    unittest.main()
