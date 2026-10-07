#!/usr/bin/env python3
"""Dynamic adenine/phosphate carrier coordinates for the R3 total QSSA.

The two accounting rows are exact on the canonical aminoacylation subsystem,
but are not asserted to be conserved across the complete source network.
Their derivatives always come from all 968 source-directed reaction rates.
"""
from __future__ import annotations

import csv

import numpy as np

from r3_candidate_runtime_v1 import R3CandidateRuntime
from verify_reduction_audit_v0 import ROOT


MATRIX = ROOT / "docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv"


class R3ResourceTotalRuntime(R3CandidateRuntime):
    def __init__(self):
        super().__init__()
        with MATRIX.open(encoding="utf-8", newline="") as stream:
            rows = {row["row"]: row for row in csv.DictReader(stream)}
        adenine = rows["adenine_moiety_total"]
        phosphorus = rows["declared_phosphate_equivalent_total"]
        self.a = np.array([float(adenine[name]) for name in self.q_names])
        self.p = np.array([float(phosphorus[name]) for name in self.q_names])
        self.k = (self.p - 3 * self.a) / 2
        self.atp = self.source.index["ATP"]
        self.amp = self.source.index["AMP"]
        self.ppi = self.source.index["PPi"]
        self.atp_pos = self.slow_position[self.atp]
        self.amp_pos = self.slow_position[self.amp]
        self.ppi_pos = self.slow_position[self.ppi]
        assert np.array_equal(self.a, self.a.astype(int))
        assert np.array_equal(self.p, self.p.astype(int))
        assert set(np.unique(self.k)) <= {0., -1.}
        # Source-general inventories have no ATP/AMP/PPi coefficient. This
        # ensures the added carrier shifts do not alter the R1 inventory b.
        assert all(not any(law.get(i, 0) for i in (self.atp, self.amp, self.ppi))
                   for law in self.source.laws)
        # Independently check the historical coefficients against each
        # canonical reaction touching the 21 selected fast concentrations.
        for accounting_row in (adenine, phosphorus):
            weights = np.array([float(accounting_row[name]) for name in self.source.species])
            assert np.max(np.abs(weights @ self.S[:, self.fast_reactions])) == 0

        # z_A = ATP + AMP + a*q; z_P = PPi - AMP + k*q.
        # Physical ATP and PPi follow by solving these two identities.
        self.D[self.atp, :] = -self.a
        self.D[self.ppi, :] = -self.k
        self.Xz[self.atp, self.amp_pos] = -1
        self.Xz[self.ppi, self.amp_pos] = 1
        self.T[self.atp_pos, self.amp] = 1
        self.T[self.atp_pos, self.q_index] = self.a
        self.T[self.ppi_pos, self.amp] = -1
        self.T[self.ppi_pos, self.q_index] = self.k
        assert np.max(np.abs(self.T @ self.D)) == 0
        assert np.max(np.abs(self.T @ self.Xz - np.eye(len(self.slow_index)))) == 0

    def initial_slow(self, full_initial):
        x0 = np.asarray(full_initial, dtype=float)
        z = super().initial_slow(x0)
        q0 = x0[self.q_index]
        z[self.atp_pos] += x0[self.amp] + self.a @ q0
        z[self.ppi_pos] += -x0[self.amp] + self.k @ q0
        return z

    def reconstruct(self, z, q, full_initial):
        z = np.asarray(z, dtype=float)
        q = np.asarray(q, dtype=float)
        y = np.empty(len(self.source.r_index), dtype=float)
        for i, value in zip(self.slow_index, z):
            y[self.retained_position[i]] = value
        for i, value in zip(self.q_index, q):
            y[self.retained_position[i]] = value
        for row, i in enumerate(self.carrier_index):
            y[self.retained_position[i]] += self.C[row] @ q
        amp = z[self.amp_pos]
        y[self.retained_position[self.atp]] -= amp + self.a @ q
        y[self.retained_position[self.ppi]] += amp - self.k @ q
        return np.asarray(self.source.reconstruct_anchored(y, full_initial), dtype=float)

    def solve_fast(self, z, full_initial, seed=None):
        result = super().solve_fast(z, full_initial, seed=seed)
        result["min_resource"] = float(min(result["state"][self.atp],
                                           result["state"][self.amp],
                                           result["state"][self.ppi]))
        result["valid_local_root"] &= result["min_resource"] >= -1e-12
        if not result["valid_local_root"]:
            self._last_root = None
        return result

    def slow_rhs(self, z, q, full_initial):
        derivative, rates, state = super().slow_rhs(z, q, full_initial)
        fast = self.S[self.q_index, :] @ rates
        amp = derivative[self.amp_pos]
        derivative[self.atp_pos] += amp + self.a @ fast
        derivative[self.ppi_pos] += -amp + self.k @ fast
        return derivative, rates, state
