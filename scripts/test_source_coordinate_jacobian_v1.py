#!/usr/bin/env python3
"""Directional checks of full and reduced chain-rule rate Jacobians."""
from __future__ import annotations

import unittest

import numpy as np

from runtime_reconstruction_rhs import SourceCoordinateRuntime
from validate_source_coordinates_full_v1 import lift_matrix, rate_jacobian, rate_vector


class CoordinateJacobianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = SourceCoordinateRuntime()
        cls.state = np.array([0.5 + (i % 17) / 20 for i in range(len(cls.runtime.species))])

    def test_full_rate_jacobian(self):
        direction = np.array([((i * 7) % 19 - 9) / 19 for i in range(len(self.state))])
        step = 1e-6
        finite = (rate_vector(self.runtime, self.state + step * direction) -
                  rate_vector(self.runtime, self.state - step * direction)) / (2 * step)
        analytic = rate_jacobian(self.runtime, self.state) @ direction
        error = np.max(np.abs(finite - analytic) / np.maximum(1, np.abs(analytic)))
        self.assertLessEqual(error, 1e-6)

    def test_reduced_rate_jacobian_uses_reconstruction_chain_rule(self):
        r0 = self.state[self.runtime.r_index]
        direction = np.array([((i * 11) % 23 - 11) / 23 for i in range(len(r0))])
        step = 1e-6
        plus = self.runtime.reconstruct_anchored(r0 + step * direction, self.state)
        minus = self.runtime.reconstruct_anchored(r0 - step * direction, self.state)
        finite = (rate_vector(self.runtime, plus) - rate_vector(self.runtime, minus)) / (2 * step)
        analytic = (rate_jacobian(self.runtime, self.state) @ lift_matrix(self.runtime)) @ direction
        error = np.max(np.abs(finite - analytic) / np.maximum(1, np.abs(analytic)))
        self.assertLessEqual(error, 1e-6)


if __name__ == "__main__":
    unittest.main()
