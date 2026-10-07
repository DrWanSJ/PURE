#!/usr/bin/env python3
"""Adversarial exact reverse-channel and gross-ledger tests."""
from __future__ import annotations

import copy
import unittest

from verify_reduction_audit_v0 import (check_reverse_pair_semantics, columns,
                                       directed_channel_ledger, reverse_pairs,
                                       source_network)


class ReverseChannelMutants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.species, cls.reactions, _ = source_network()
        cls.stoich = columns(cls.species, cls.reactions)
        cls.pairs = reverse_pairs(cls.reactions, cls.stoich)

    def test_canonical_pairs(self):
        self.assertEqual(len(self.pairs), 290)
        check_reverse_pair_semantics(self.reactions, self.stoich, self.pairs)

    def test_wrong_pairing_preserves_count_and_unique_endpoints(self):
        mutant = self.pairs.copy()
        first, second = mutant[0], mutant[1]
        mutant[0] = (first[0], second[1])
        mutant[1] = (second[0], first[1])
        self.assertEqual(len(mutant), len(self.pairs))
        self.assertEqual(len({rid for pair in mutant for rid in pair}), 580)
        with self.assertRaisesRegex(AssertionError, "reactant/product swap mismatch"):
            check_reverse_pair_semantics(self.reactions, self.stoich, mutant)

    def test_stoichiometric_sign_mutation(self):
        mutant = copy.deepcopy(self.stoich)
        by_id = {reaction["id"]: j for j, reaction in enumerate(self.reactions)}
        first, second = self.pairs[0]
        index = by_id[second]
        species_index = next(iter(mutant[index]))
        mutant[index][species_index] *= -1
        with self.assertRaisesRegex(AssertionError, "stoichiometric sign mismatch"):
            check_reverse_pair_semantics(self.reactions, mutant, self.pairs)

    def test_lost_kinetic_law_factor(self):
        mutant = copy.deepcopy(self.reactions)
        by_id = {reaction["id"]: reaction for reaction in mutant}
        by_id[self.pairs[0][0]]["factors"].remove("k1")
        with self.assertRaisesRegex(AssertionError, "kinetic law/parameter unavailable"):
            check_reverse_pair_semantics(mutant, self.stoich, self.pairs)

    def test_gross_ledger_cannot_be_abs_net(self):
        ledger = directed_channel_ledger(5.0, 4.0)
        self.assertEqual((ledger["forward"], ledger["reverse"]), (5.0, 4.0))
        self.assertEqual(ledger["net"], 1.0)
        self.assertEqual(ledger["gross"], 9.0)
        self.assertNotEqual(ledger["gross"], abs(ledger["net"]))


if __name__ == "__main__":
    unittest.main()
