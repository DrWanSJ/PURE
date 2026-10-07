#!/usr/bin/env python3
"""Extra numerical polish for the unchanged R3 physical QSSA closure.

The acceptance predicate remains the v2 physical root predicate. A second
Newton correction reduces warm-start-dependent fast-root jitter before the
very tight BDF state solve evaluates its slow RHS.
"""
from __future__ import annotations

import numpy as np

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2


class R3ResourceTotalRuntimeV3(R3ResourceTotalRuntimeV2):
    def solve_fast(self, z, full_initial, seed=None):
        result = super().solve_fast(z, full_initial, seed=seed)
        if not result["valid_local_root"]:
            return result
        q = result["q"].copy()
        steps = 0
        for _ in range(3):
            residual, jacobian, state = self.fast_rows(
                z, q, full_initial, with_jacobian=True)
            try:
                correction = np.linalg.solve(jacobian, -residual)
            except np.linalg.LinAlgError:
                break
            if float(np.max(np.abs(correction))) <= 1e-14:
                break
            candidate = q + correction
            new_residual, new_jacobian, new_state = self.fast_rows(
                z, candidate, full_initial, with_jacobian=True)
            if (float(np.max(np.abs(new_residual))) > 1e-10 or
                    float(np.min(candidate)) < -1e-12 or
                    float(np.min(new_state[self.carrier_index])) < -1e-12 or
                    float(min(new_state[self.atp], new_state[self.amp],
                              new_state[self.ppi])) < -1e-12):
                break
            q = candidate
            residual, jacobian, state = new_residual, new_jacobian, new_state
            steps += 1
        result.update(q=q, state=state, residual=residual,
                      residual_max=float(np.max(np.abs(residual))),
                      min_q=float(np.min(q)),
                      min_carrier=float(np.min(state[self.carrier_index])),
                      min_resource=float(min(state[self.atp], state[self.amp],
                                             state[self.ppi])),
                      polish_steps=steps)
        self._last_root = q.copy()
        return result
