#!/usr/bin/env python3
"""Adversarial structural tests for the simultaneous exact-coordinate chart."""
from __future__ import annotations

import copy
import json
import unittest

from verify_reduction_audit_v0 import OUT, columns, rows, source_network
from verify_source_coordinate_certificate_v1 import check_certificate


class ExactChartMutants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.species, reactions, cls.initial = source_network()
        cls.stoich = columns(cls.species, reactions)
        cls.laws = {law["conservation_id"]: law for law in rows(OUT / "conservation_laws_v0.csv")}
        cls.cert = json.loads((OUT / "source_coordinate_certificate_v1.json").read_text(encoding="utf-8"))

    def test_source_certificate(self):
        self.assertTrue(check_certificate(self.cert, self.species, self.stoich, self.initial, self.laws))

    def test_wrong_reconstruction_sign(self):
        mutant = copy.deepcopy(self.cert)
        row = next(row for row in mutant["B_sparse_rows"] if row)
        key = next(iter(row))
        row[key] = str(-int(row[key]))
        with self.assertRaises(AssertionError):
            check_certificate(mutant, self.species, self.stoich, self.initial, self.laws)

    def test_duplicate_eliminated_coordinate(self):
        mutant = copy.deepcopy(self.cert)
        mutant["eliminated_species"][1] = mutant["eliminated_species"][0]
        with self.assertRaises(AssertionError):
            check_certificate(mutant, self.species, self.stoich, self.initial, self.laws)

    def test_frozen_only_law_cannot_enter_generic_chart(self):
        mutant = copy.deepcopy(self.cert)
        mutant["law_ids"][0] = next(key for key, law in self.laws.items()
                                       if law["scope"] == "FROZEN_REFERENCE_ONLY")
        with self.assertRaises(AssertionError):
            check_certificate(mutant, self.species, self.stoich, self.initial, self.laws)

    def test_altered_source_stoichiometry(self):
        mutant = copy.deepcopy(self.stoich)
        index = self.species.index(self.cert["eliminated_species"][0])
        mutant[0][index] = mutant[0].get(index, 0) + 1
        with self.assertRaises(AssertionError):
            check_certificate(self.cert, self.species, mutant, self.initial, self.laws)


if __name__ == "__main__":
    unittest.main()
