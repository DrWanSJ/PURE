#!/usr/bin/env python3
"""Canonical-rate RHS and exact-coordinate reconstruction for PNAS2017 PURE."""
from __future__ import annotations

import json
import math
from fractions import Fraction

from verify_reduction_audit_v0 import OUT, columns, source_network


class SourceCoordinateRuntime:
    def __init__(self, certificate_name="source_coordinate_certificate_v1.json"):
        self.species, self.reactions, self.author_initial = source_network()
        self.index = {name: i for i, name in enumerate(self.species)}
        self.stoich = columns(self.species, self.reactions)
        self.certificate_name = certificate_name
        self.cert = json.loads((OUT / certificate_name).read_text(encoding="utf-8"))
        self.eliminated = self.cert["eliminated_species"]
        self.retained = self.cert["retained_species"]
        self.e_index = [self.index[name] for name in self.eliminated]
        self.r_index = [self.index[name] for name in self.retained]
        assert len(self.e_index) == 27 and len(self.r_index) == 214
        assert set(self.e_index).isdisjoint(self.r_index)
        self.laws = self._load_laws()
        self.A = [[Fraction(value) for value in row] for row in self.cert["A_rows"]]
        self.B = [{self.index[name]: Fraction(value) for name, value in row.items()}
                  for row in self.cert["B_sparse_rows"]]
        self.rate_specs = [(float(reaction["k"]),
                            [self.index[name] for name in reaction["factors"] if name != "k1"])
                           for reaction in self.reactions]
        self.source_rows = [tuple((j, float(col[i])) for j, col in enumerate(self.stoich) if i in col)
                            for i in range(len(self.species))]
        self.lifted_rows = []
        for e_i, weights in zip(self.e_index, self.B):
            row = []
            for j, col in enumerate(self.stoich):
                coefficient = sum((value * col.get(i, 0) for i, value in weights.items()), Fraction())
                assert coefficient == col.get(e_i, 0), (self.species[e_i], self.reactions[j]["id"])
                if coefficient:
                    row.append((j, float(coefficient)))
            self.lifted_rows.append(tuple(row))

    def _load_laws(self):
        from verify_reduction_audit_v0 import rows
        by_id = {law["conservation_id"]: law for law in rows(OUT / "conservation_laws_v0.csv")}
        assert all(by_id[law_id]["scope"] == "SOURCE_GENERAL" for law_id in self.cert["law_ids"])
        return [{self.index[name]: Fraction(coefficient)
                 for name, coefficient in json.loads(by_id[law_id]["species_coefficients_json"]).items()}
                for law_id in self.cert["law_ids"]]

    def b_for_initial(self, full_initial):
        """Recompute conservation constants for this initial condition."""
        assert len(full_initial) == len(self.species)
        return [sum((coefficient * Fraction(str(full_initial[i])) for i, coefficient in law.items()),
                    Fraction()) for law in self.laws]

    def reconstruct(self, retained_state, b):
        assert len(retained_state) == len(self.retained) and len(b) == len(self.laws)
        full = [0.0] * len(self.species)
        for i, value in zip(self.r_index, retained_state):
            full[i] = float(value)
        exact_input = all(isinstance(value, (Fraction, int)) for value in retained_state) and all(
            isinstance(value, (Fraction, int)) for value in b)
        exact_retained = dict(zip(self.r_index, retained_state)) if exact_input else None
        for e, i in enumerate(self.e_index):
            if exact_input:
                value = sum((coefficient * b[k] for k, coefficient in enumerate(self.A[e])), Fraction())
                value += sum((coefficient * exact_retained[j] for j, coefficient in self.B[e].items()), Fraction())
                full[i] = float(value)
            else:
                full[i] = math.fsum([float(value) * float(b[k]) for k, value in enumerate(self.A[e]) if value] +
                                    [float(value) * full[j] for j, value in self.B[e].items()])
        return full

    def domain(self, full_state):
        retained_min = min(full_state[i] for i in self.r_index)
        reconstructed_min = min(full_state[i] for i in self.e_index)
        return {"feasible": retained_min >= 0 and reconstructed_min >= 0,
                "retained_min": retained_min, "reconstructed_min": reconstructed_min}

    def reconstruct_anchored(self, retained_state, full_initial):
        """Floating form of the same affine map, anchored at this run's x0."""
        assert len(retained_state) == len(self.retained) and len(full_initial) == len(self.species)
        full = [float(value) for value in full_initial]
        for i, value in zip(self.r_index, retained_state):
            full[i] = float(value)
        for e, i in enumerate(self.e_index):
            full[i] = math.fsum([float(full_initial[i])] +
                                [float(coefficient) * (full[j] - float(full_initial[j]))
                                 for j, coefficient in self.B[e].items()])
        return full

    def rates(self, full_state):
        assert len(full_state) == len(self.species)
        result = []
        for parameter, factors in self.rate_specs:
            value = parameter
            for i in factors:
                value *= full_state[i]
            result.append(value)
        return result

    @staticmethod
    def _sum_rows(rows, rates):
        return [math.fsum(coefficient * rates[j] for j, coefficient in row) for row in rows]

    def full_rhs_from_rates(self, rates):
        assert len(rates) == len(self.reactions)
        return self._sum_rows(self.source_rows, rates)

    def coordinate_rhs_from_rates(self, rates):
        """Evaluate S_R*v and exactly compiled (B*S_R)*v from one rate vector."""
        assert len(rates) == len(self.reactions)
        result = [0.0] * len(self.species)
        for i, value in zip(self.r_index, self._sum_rows([self.source_rows[i] for i in self.r_index], rates)):
            result[i] = value
        for i, value in zip(self.e_index, self._sum_rows(self.lifted_rows, rates)):
            result[i] = value
        return result

    def rounded_b_times_retained_rhs_diagnostic(self, rates):
        retained_rhs = self._sum_rows([self.source_rows[i] for i in self.r_index], rates)
        by_index = dict(zip(self.r_index, retained_rhs))
        return [math.fsum(float(value) * by_index[j] for j, value in row.items()) for row in self.B]
