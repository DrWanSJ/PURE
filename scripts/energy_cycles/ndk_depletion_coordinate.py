"""Exact numerical coordinate change for the frozen irreversible NDK candidate.

This library changes no source rates, total-QSSA closure, scientific gates,
scenario, initial condition, output grid, or observation mapping. The frozen
runtime.py is imported, never edited. This file has no executable CLI and does
not run comparisons on import. Its use must be frozen in a separate engineering
addendum before comparison outcomes are inspected.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

from runtime import DomainFailure


def ndk_depletion_hazard(module, x, limiting_index):
    """Continuous source-derived coefficient v/T_lim, including T_lim=0.

    At kr=0, rAB=alpha/(beta+kf). Factoring either association out of rAB
    and its exact resource total cancels division by the depleted inventory.
    The formula remains finite when its limiting resource is zero. It is
    algebraically equal to v/T_lim on an exact physical closure when T_lim>0.
    """
    p = module.parameters
    a = p["re0000000355"] * x[module.index["ATP"]]
    b = p["re0000000357"] * x[module.index["GDP"]]
    d0 = p["re0000000356"]
    kf = p["re0000000363"]
    Efree = x[module.index["NDK"]]
    L = 1 / (d0 + b) + 1 / (d0 + a)
    beta = d0 * d0 * L
    if limiting_index == 1:  # GDP
        theta = a * L / (beta + kf)  # rAB = b*theta
        k = p["re0000000357"]
        binary_denominator = d0 + a
    elif limiting_index == 0:  # ATP
        theta = b * L / (beta + kf)  # rAB = a*theta
        k = p["re0000000355"]
        binary_denominator = d0 + b
    else:
        raise ValueError("The limiting NDK substrate must be ATP or GDP")
    storage = (1 + d0 * theta) / binary_denominator + theta
    value = kf * Efree * k * theta / (1 + Efree * k * storage)
    if not np.isfinite(value) or value < 0:
        raise DomainFailure("NDK depletion hazard is outside the positive physical closure branch")
    return float(value)


class NDKDepletionCoordinate:
    """R=L0*exp(-q), extent=L0*(1-exp(-q)), retaining exact source totals."""

    def __init__(self, module, initial_totals, enzyme_total):
        if module.name != "NDK" or module.B != ["ATP", "GDP", "ADP", "GTP"]:
            raise ValueError("Coordinate is restricted to the verified NDK source ordering")
        if module.parameters["re0000000364"] != 0:
            raise ValueError("Monotone depletion coordinate requires source-disabled NDK reverse chemistry")
        if not np.array_equal(module.N, [-1, -1, 1, 1]):
            raise ValueError("Coordinate requires the verified NDK net stoichiometry")
        self.module = module
        self.T0 = np.asarray(initial_totals, dtype=float).copy()
        if np.any(self.T0 < 0):
            raise DomainFailure("Negative initial retained inventories")
        self.enzyme_total = enzyme_total
        self.limiting_index = int(np.argmin(self.T0[:2]))
        self.other_index = 1 - self.limiting_index
        self.L0 = float(self.T0[self.limiting_index])
        self.difference = float(self.T0[self.other_index] - self.L0)

    def totals(self, q):
        # No subtraction of two almost equal original substrate inventories.
        # np.exp underflow yields the analytic depletion boundary, not clipping.
        R = self.L0 * np.exp(-q)
        extent = -self.L0 * np.expm1(-q)
        if not np.isfinite(R) or not np.isfinite(extent):
            raise DomainFailure("Nonfinite depletion-coordinate trial")
        T = np.empty(4)
        T[self.limiting_index] = R
        T[self.other_index] = self.difference + R
        T[2:] = self.T0[2:] + extent
        return T, float(R), float(extent)

    def point(self, q):
        T, R, extent = self.totals(q)
        x, currents, residual, singular = self.module.closure(T, self.enzyme_total)
        hazard = ndk_depletion_hazard(self.module, x, self.limiting_index)
        # This is a source-equivalent factorization, not a threshold or clipping
        # of a small reconstructed catalytic rate. At an exact closure it equals
        # k363*h_NDK_GDP_ATP. Near R=0 it avoids magnifying absolute root residual.
        factored_current = R * hazard
        return x, currents, residual, singular, hazard, factored_current, R, extent

    def rhs(self, t, y):
        _, _, _, _, hazard, current, _, _ = self.point(float(y[0]))
        # q and the original directed extent quadratures start at zero.
        # Reverse extent is identically zero for the frozen source overlay.
        return np.array([hazard, current, 0.0])


def integrate_reduced_ndk(module, initial_totals, enzyme_total, grid, rtol, atol):
    """Drop-in return layout for runtime.integrate_reduced, using exact q.

    Returns original species plus direct forward/reverse extent quadratures,
    reconstructed microscopic currents, and engineering diagnostics. The same
    Module physical closure and sampled fast-tangent guards remain authoritative.
    """
    coordinate = NDKDepletionCoordinate(module, initial_totals, enzyme_total)
    grid = np.asarray(grid, dtype=float)
    if len(grid) < 2 or grid[0] != 0 or grid[-1] != 1000:
        raise ValueError("Use the unchanged frozen comparison grid from 0 through 1000")
    if coordinate.L0 == 0:
        x, currents, residual, singular = module.closure(coordinate.T0, enzyme_total)
        if np.any(currents != 0):
            raise DomainFailure("Zero limiting inventory has nonzero source NDK current")
        eig = module.fast_eigen(x)
        if float(np.max(eig.real)) >= -1e-8:
            raise DomainFailure("Selected root lacks local fixed-total fast attractivity")
        trajectory = np.column_stack([np.tile(x, (len(grid), 1)), np.zeros((len(grid), 2))])
        return trajectory, np.zeros((len(grid), 2)), {
            "method": "Static exact zero-current boundary", "coordinate": "NDK exponential limiting inventory",
            "nfev": 0, "njev": 0, "nlu": 0, "message": "R0=0 gives the same static irreversible source candidate",
            "maximum_closure_residual": float(residual), "minimum_total_jacobian_singular_value": float(singular),
            "maximum_fast_tangent_real_eigenvalue": float(np.max(eig.real)),
            "minimum_fast_relaxation_rate": float(np.min(-eig.real)),
            "maximum_extent_coordinate_vs_direct_quadrature_error": 0.0,
            "maximum_factored_vs_reconstructed_source_current_error": 0.0,
            "limiting_resource": module.B[coordinate.limiting_index], "initial_limiting_inventory": 0.0,
            "no_clipping_or_product_seeding": True,
        }
    solution = solve_ivp(coordinate.rhs, (0, 1000), [0.0, 0.0, 0.0], method="Radau", rtol=rtol, atol=atol, t_eval=grid)
    if not solution.success or solution.y.shape[1] != len(grid):
        raise RuntimeError("Transformed reduced solver did not complete: " + solution.message)
    xs, cs, residuals, singulars, eigenvalues, factor_errors, extent_errors, remaining = [], [], [], [], [], [], [], []
    for q, forward_extent, reverse_extent in solution.y.T:
        x, currents, residual, singular, _, factored_current, R, extent = coordinate.point(float(q))
        eig = module.fast_eigen(x)
        if float(np.max(eig.real)) >= -1e-8:
            raise DomainFailure("Selected root lacks local fixed-total fast attractivity")
        xs.append(x)
        cs.append(currents)
        residuals.append(residual)
        singulars.append(singular)
        eigenvalues.append(eig)
        factor_errors.append(abs(factored_current - currents[0]))
        extent_errors.append(abs(extent - (forward_extent - reverse_extent)))
        remaining.append(R)
    trajectory = np.column_stack([xs, solution.y[1:].T])
    diagnostics = {
        "method": "Radau", "coordinate": "NDK exponential limiting inventory",
        "nfev": solution.nfev, "njev": solution.njev, "nlu": solution.nlu, "message": solution.message,
        "maximum_closure_residual": float(max(residuals)), "minimum_total_jacobian_singular_value": float(min(singulars)),
        "maximum_fast_tangent_real_eigenvalue": float(np.max(np.asarray(eigenvalues).real)),
        "minimum_fast_relaxation_rate": float(np.min(-np.asarray(eigenvalues).real)),
        "maximum_extent_coordinate_vs_direct_quadrature_error": float(max(extent_errors)),
        "maximum_factored_vs_reconstructed_source_current_error": float(max(factor_errors)),
        "limiting_resource": module.B[coordinate.limiting_index], "initial_limiting_inventory": coordinate.L0,
        "minimum_remaining_inventory": float(min(remaining)), "maximum_q": float(np.max(solution.y[0])),
        "remaining_inventory_underflow_samples": int(np.count_nonzero(np.asarray(remaining) == 0)),
        "fast_attractivity_scope": "Initial/output-grid roots, matching frozen runtime; not a uniform global certificate",
        "no_clipping_or_product_seeding": True,
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    return trajectory, np.asarray(cs), diagnostics
