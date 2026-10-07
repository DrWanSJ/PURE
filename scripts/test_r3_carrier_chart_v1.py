#!/usr/bin/env python3
"""Adversarial exact-coordinate and exploratory closure checks for R3."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import sympy as sp

from build_r3_carrier_chart_v1 import OUTPUT, build
from verify_reduction_audit_v0 import OUT, rows

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC = ROOT / "results/reduction/r3_closure_diagnostic_v1/attempt_004/result.json"


class CarrierChartMutants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
        laws = {law["conservation_id"]: law for law in rows(OUT / "conservation_laws_v0.csv")}
        cls.laws = laws
        fast = cls.certificate["candidate_fast_species"]
        carriers = cls.certificate["carrier_species"]
        vectors = [json.loads(laws[law_id]["species_coefficients_json"])
                   for law_id in cls.certificate["source_general_law_ids"]]
        cls.Lc = sp.Matrix([[sp.Rational(vector.get(name, 0)) for name in carriers] for vector in vectors])
        cls.Lq = sp.Matrix([[sp.Rational(vector.get(name, 0)) for name in fast] for vector in vectors])
        cls.C = sp.Matrix([[sp.Rational(row.get(name, 0)) for name in fast]
                           for row in cls.certificate["carrier_delta_per_fast_delta_rows"]])

    def test_rederived_certificate(self):
        self.assertEqual(self.certificate, build())
        self.assertEqual(self.Lc * self.C + self.Lq, sp.zeros(27, 21))
        self.assertTrue(all(self.laws[law_id]["scope"] == "SOURCE_GENERAL"
                            for law_id in self.certificate["source_general_law_ids"]))

    def test_wrong_carrier_sign_rejected(self):
        mutant = self.C.copy()
        i, j = next((i, j) for i in range(6) for j in range(21) if mutant[i, j] != 0)
        mutant[i, j] *= -1
        self.assertNotEqual(self.Lc * mutant + self.Lq, sp.zeros(27, 21))

    def test_missing_carrier_rejected(self):
        for i in range(6):
            self.assertLess(self.Lc[:, [j for j in range(6) if j != i]].rank(), 6)

    def test_historical_frozen_law_cannot_be_generic(self):
        self.assertEqual(self.laws["CONS_064"]["scope"], "FROZEN_REFERENCE_ONLY")
        self.assertNotIn("CONS_064", self.certificate["source_general_law_ids"])
        self.assertFalse({"GlyAMP", "MetAMP"} & set(self.certificate["candidate_fast_species"]))

    def test_exploratory_same_inventory_branch(self):
        result = json.loads(DIAGNOSTIC.read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "EXPLORATORY_CLOSURE_DIAGNOSTIC_ONLY")
        total = [sample for sample in result["samples"] if sample["coordinate"] == "six_carrier_total"]
        standard = [sample for sample in result["samples"] if sample["coordinate"] == "fixed_free_standard"]
        enzyme = [sample for sample in result["samples"] if sample["coordinate"] == "enzyme_total"]
        self.assertEqual(len(total), len(standard), len(enzyme))
        self.assertEqual(len(total), 8)
        self.assertTrue(all(sample["solver_success"] and sample["physical_branch"]
                            and sample["max_abs_fast_rhs"] <= 1e-10
                            and sample["same_initial_source_general_inventories"] for sample in total))
        self.assertGreater(standard[0]["max_source_general_law_shift"], 1)
        self.assertGreater(enzyme[0]["max_source_general_law_shift"], 0.1)
        self.assertLess(max(sample["max_source_general_law_shift"] for sample in total), 1e-10)


if __name__ == "__main__":
    unittest.main()
