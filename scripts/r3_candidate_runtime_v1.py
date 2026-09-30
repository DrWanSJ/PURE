#!/usr/bin/env python3
"""Source-derived selective aminoacylation QSSA candidate runtime.

The exact carrier and R1 coordinate maps are certified separately. This
module implements their state mapping and algebraic fast rows; coupled
trajectory validity has not yet been established.
"""
from __future__ import annotations

import json
import math

import numpy as np
from scipy.optimize import root

from runtime_reconstruction_rhs import SourceCoordinateRuntime
from validate_source_coordinates_full_v1 import rate_jacobian, source_matrix
from verify_reduction_audit_v0 import OUT


class R3CandidateRuntime:
    def __init__(self):
        self.source = SourceCoordinateRuntime("source_coordinate_certificate_v4.json")
        self.chart = json.loads((OUT / "r3_carrier_chart_v1.json").read_text(encoding="utf-8"))
        self.q_names = self.chart["candidate_fast_species"]
        self.carrier_names = self.chart["carrier_species"]
        self.q_index = np.array([self.source.index[name] for name in self.q_names], dtype=int)
        self.carrier_index = np.array([self.source.index[name] for name in self.carrier_names], dtype=int)
        retained_set = set(self.source.r_index)
        assert set(self.q_index) | set(self.carrier_index) <= retained_set
        self.slow_index = np.array([i for i in self.source.r_index if i not in set(self.q_index)], dtype=int)
        assert len(self.slow_index) == 193
        self.slow_position = {index: position for position, index in enumerate(self.slow_index)}
        self.retained_position = {index: position for position, index in enumerate(self.source.r_index)}
        self.C = np.array([[float(row.get(name, 0)) for name in self.q_names]
                           for row in self.chart["carrier_delta_per_fast_delta_rows"]], dtype=float)
        assert self.C.shape == (6, 21)
        self.D = np.zeros((len(self.source.species), len(self.q_names)))
        self.D[self.q_index, np.arange(len(self.q_names))] = 1.0
        self.D[self.carrier_index, :] = self.C
        self.fast_reactions = np.array(sorted({j for i in self.q_index
                                                for j, _ in self.source.source_rows[i]}), dtype=int)
        assert len(self.fast_reactions) == 103
        self.Sq = np.array([[float(self.source.stoich[j].get(i, 0)) for j in self.fast_reactions]
                            for i in self.q_index])
        assert self.Sq.shape == (21, 103)
        self.S = source_matrix(self.source)
        self.Xz = np.zeros((len(self.source.species), len(self.slow_index)))
        for position, i in enumerate(self.slow_index):
            self.Xz[i, position] = 1.0
        for e, i in enumerate(self.source.e_index):
            for retained_i, coefficient in self.source.B[e].items():
                position = self.slow_position.get(retained_i)
                if position is not None:
                    self.Xz[i, position] = float(coefficient)
        self.T = np.zeros((len(self.slow_index), len(self.source.species)))
        for position, i in enumerate(self.slow_index):
            self.T[position, i] = 1.0
        for row, i in enumerate(self.carrier_index):
            self.T[self.slow_position[i], self.q_index] -= self.C[row]
        assert np.max(np.abs(self.T @ self.D)) == 0.0
        self._last_root = None

    def initial_slow(self, full_initial):
        x0 = np.asarray(full_initial, dtype=float)
        assert x0.shape == (len(self.source.species),)
        z = x0[self.slow_index].copy()
        q0 = x0[self.q_index]
        for row, i in enumerate(self.carrier_index):
            z[self.slow_position[i]] -= float(self.C[row] @ q0)
        return z

    def reconstruct(self, z, q, full_initial):
        z = np.asarray(z, dtype=float)
        q = np.asarray(q, dtype=float)
        assert z.shape == (193,) and q.shape == (21,)
        y = np.empty(214, dtype=float)
        for i, value in zip(self.slow_index, z):
            y[self.retained_position[i]] = value
        for i, value in zip(self.q_index, q):
            y[self.retained_position[i]] = value
        carrier_physical = self.C @ q
        for row, i in enumerate(self.carrier_index):
            y[self.retained_position[i]] += carrier_physical[row]
        return np.asarray(self.source.reconstruct_anchored(y, full_initial), dtype=float)

    def fast_rows(self, z, q, full_initial, with_jacobian=False):
        state = self.reconstruct(z, q, full_initial)
        rates = np.empty(len(self.fast_reactions), dtype=float)
        derivatives = np.zeros((len(self.fast_reactions), len(self.q_names))) if with_jacobian else None
        for local_j, j in enumerate(self.fast_reactions):
            parameter, factors = self.source.rate_specs[j]
            value = parameter
            for i in factors:
                value *= state[i]
            rates[local_j] = value
            if with_jacobian and parameter != 0:
                for position, factor in enumerate(factors):
                    if not np.any(self.D[factor]):
                        continue
                    partial = parameter
                    for other_position, other in enumerate(factors):
                        if other_position != position:
                            partial *= state[other]
                    derivatives[local_j] += partial * self.D[factor]
        residual = self.Sq @ rates
        if with_jacobian:
            return residual, self.Sq @ derivatives, state
        return residual, state

    def solve_fast(self, z, full_initial, seed=None):
        if seed is None:
            seed = self._last_root
        if seed is None:
            seed = np.asarray(full_initial, dtype=float)[self.q_index]
        cached = {"q": None, "residual": None, "jacobian": None}

        def evaluate(q):
            if cached["q"] is None or not np.array_equal(q, cached["q"]):
                residual, jacobian, _ = self.fast_rows(z, q, full_initial, with_jacobian=True)
                cached.update(q=q.copy(), residual=residual, jacobian=jacobian)
            return cached["residual"], cached["jacobian"]

        result = root(lambda q: evaluate(q)[0], np.asarray(seed, dtype=float),
                      jac=lambda q: evaluate(q)[1], method="hybr", options={"xtol": 1e-11})
        q = result.x.copy()
        residual, jacobian, state = self.fast_rows(z, q, full_initial, with_jacobian=True)
        root_initial_residual_max = float(np.max(np.abs(residual)))
        refinement_steps = 0
        # A fixed, small Newton polish resolves HYBR's small-step stop on
        # high-flux adverse cases without changing the closure threshold.
        for _ in range(3):
            if float(np.max(np.abs(residual))) <= 1e-10:
                break
            try:
                step = np.linalg.solve(jacobian, -residual)
            except np.linalg.LinAlgError:
                break
            candidate = q + step
            new_residual, new_jacobian, new_state = self.fast_rows(
                z, candidate, full_initial, with_jacobian=True)
            if float(np.max(np.abs(new_residual))) >= float(np.max(np.abs(residual))):
                break
            q, residual, jacobian, state = candidate, new_residual, new_jacobian, new_state
            refinement_steps += 1
        residual_max = float(np.max(np.abs(residual)))
        min_q = float(np.min(q))
        min_carrier = float(np.min(state[self.carrier_index]))
        physical = min_q >= -1e-12 and min_carrier >= -1e-12
        try:
            correction = np.linalg.solve(jacobian, -residual)
            correction_max = float(np.max(np.abs(correction)))
            condition_number = float(np.linalg.cond(jacobian))
        except np.linalg.LinAlgError:
            correction_max = float("inf")
            condition_number = float("inf")
        local_convergence = (residual_max <= 1e-10 and correction_max <= 1e-10
                             and condition_number < 1e12)
        valid = local_convergence and physical
        if valid:
            self._last_root = q.copy()
        return {"q": q, "state": state, "residual": residual,
                "residual_max": residual_max, "min_q": min_q,
                "min_carrier": min_carrier, "physical": physical,
                "solver_success": bool(result.success), "nfev": int(result.nfev),
                "njev": int(result.njev), "valid_local_root": bool(valid),
                "local_convergence_by_residual_and_jacobian": bool(local_convergence),
                "Gq_condition_number": condition_number,
                "newton_correction_max_abs": correction_max,
                "hybr_initial_residual_max": root_initial_residual_max,
                "newton_refinement_steps": refinement_steps,
                "message": str(result.message)}

    def slow_rhs(self, z, q, full_initial):
        state = self.reconstruct(z, q, full_initial)
        rates = self.source.rates(state)
        fast_derivative = np.array([math.fsum(value * rates[j] for j, value in self.source.source_rows[i])
                                    for i in self.q_index])
        slow_derivative = np.array([math.fsum(value * rates[j] for j, value in self.source.source_rows[i])
                                    for i in self.slow_index])
        adjustment = self.C @ fast_derivative
        for row, i in enumerate(self.carrier_index):
            slow_derivative[self.slow_position[i]] -= adjustment[row]
        return slow_derivative, np.asarray(rates), state

    def slow_jacobian(self, z, q, full_initial):
        """Apply dh/dz=-G_q^-1 G_z, including R1 and carrier reconstruction."""
        state = self.reconstruct(z, q, full_initial)
        full_jacobian = self.S @ rate_jacobian(self.source, state)
        fast_jacobian = full_jacobian[self.q_index, :]
        Gq = np.asarray(fast_jacobian @ self.D)
        Gz = np.asarray(fast_jacobian @ self.Xz)
        implicit = -np.linalg.solve(Gq, Gz)
        lifted = self.Xz + self.D @ implicit
        reduced = np.asarray(self.T @ (full_jacobian @ lifted))
        assert reduced.shape == (193, 193)
        return reduced, {"Gq_condition_number": float(np.linalg.cond(Gq)),
                         "implicit_derivative_max_abs": float(np.max(np.abs(implicit)))}
