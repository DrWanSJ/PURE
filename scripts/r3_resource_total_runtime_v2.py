#!/usr/bin/env python3
"""Warm-started physical closure for the R3 dynamic-resource candidate.

Only the nonlinear solver implementation changes from v1. The source RHS,
coordinate map, Jacobian, thresholds, and fallback HYBR solver are unchanged.
"""
from __future__ import annotations

import numpy as np

from r3_resource_total_runtime_v1 import R3ResourceTotalRuntime


class R3ResourceTotalRuntimeV2(R3ResourceTotalRuntime):
    def solve_fast(self, z, full_initial, seed=None):
        if seed is None:
            seed = self._last_root
        if seed is None:
            seed = np.asarray(full_initial, dtype=float)[self.q_index]
        initial_seed = np.asarray(seed, dtype=float)
        q = initial_seed.copy()
        first_residual = None
        evaluations = 0
        for step_number in range(5):
            residual, jacobian, state = self.fast_rows(z, q, full_initial, with_jacobian=True)
            evaluations += 1
            residual_max = float(np.max(np.abs(residual)))
            if first_residual is None:
                first_residual = residual_max
            try:
                correction = np.linalg.solve(jacobian, -residual)
                condition = float(np.linalg.cond(jacobian))
            except np.linalg.LinAlgError:
                break
            correction_max = float(np.max(np.abs(correction)))
            min_q = float(np.min(q))
            min_carrier = float(np.min(state[self.carrier_index]))
            min_resource = float(min(state[self.atp], state[self.amp], state[self.ppi]))
            physical = min_q >= -1e-12 and min_carrier >= -1e-12 and min_resource >= -1e-12
            if residual_max <= 1e-10 and correction_max <= 1e-10 and condition < 1e12 and physical:
                self._last_root = q.copy()
                return {"q": q, "state": state, "residual": residual,
                        "residual_max": residual_max, "min_q": min_q,
                        "min_carrier": min_carrier, "min_resource": min_resource,
                        "physical": True, "solver_success": True,
                        "nfev": evaluations, "njev": evaluations,
                        "valid_local_root": True,
                        "local_convergence_by_residual_and_jacobian": True,
                        "Gq_condition_number": condition,
                        "newton_correction_max_abs": correction_max,
                        "hybr_initial_residual_max": None,
                        "newton_refinement_steps": step_number,
                        "method": "warm_start_newton", "initial_residual_max": first_residual,
                        "message": "Physical warm-start Newton root"}
            candidate = q + correction
            if not np.all(np.isfinite(candidate)):
                break
            q = candidate
        fallback = super().solve_fast(z, full_initial, seed=initial_seed)
        fallback["method"] = "hybr_fallback"
        fallback["warm_start_newton_evaluations"] = evaluations
        fallback["initial_residual_max"] = first_residual
        return fallback
