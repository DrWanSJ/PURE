#!/usr/bin/env python3
"""Exploratory high-precision R3 slow RHS; never a registered grid runtime.

The float64 fast closure and analytic Jacobian are unchanged. Decimal only
tests whether reconstruction/rate-product roundoff limits BDF progress.
"""
from __future__ import annotations

from decimal import Decimal, localcontext

import numpy as np

from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2


def dec(value):
    return Decimal.from_float(float(value))


class R3ResourceTotalPreciseDiagnostic(R3ResourceTotalRuntimeV2):
    def slow_rhs(self, z, q, full_initial):
        with localcontext() as context:
            context.prec = 50
            zz = [dec(value) for value in z]
            qq = [dec(value) for value in q]
            initial = [dec(value) for value in full_initial]
            y = {}
            for i, value in zip(self.slow_index, zz):
                y[i] = value
            for i, value in zip(self.q_index, qq):
                y[i] = value
            for row, i in enumerate(self.carrier_index):
                y[i] += sum((Decimal(int(coef)) * value
                             for coef, value in zip(self.C[row], qq) if coef),
                            Decimal(0))
            amp = zz[self.amp_pos]
            y[self.atp] -= amp + sum(
                (Decimal(int(coef)) * value
                 for coef, value in zip(self.a, qq) if coef), Decimal(0))
            y[self.ppi] += amp - sum(
                (Decimal(int(coef)) * value
                 for coef, value in zip(self.k, qq) if coef), Decimal(0))
            full = initial.copy()
            for i in self.source.r_index:
                full[i] = y[i]
            for e, i in enumerate(self.source.e_index):
                full[i] = initial[i] + sum(
                    (dec(coefficient) * (full[j] - initial[j])
                     for j, coefficient in self.source.B[e].items()),
                    Decimal(0))
            rates = []
            for parameter, factors in self.source.rate_specs:
                value = dec(parameter)
                for i in factors:
                    value *= full[i]
                rates.append(value)

            def source_rhs(i):
                return sum((dec(value) * rates[j]
                            for j, value in self.source.source_rows[i]),
                           Decimal(0))

            fast = [source_rhs(i) for i in self.q_index]
            slow = [source_rhs(i) for i in self.slow_index]
            for row, i in enumerate(self.carrier_index):
                slow[self.slow_position[i]] -= sum(
                    (Decimal(int(coef)) * value
                     for coef, value in zip(self.C[row], fast) if coef),
                    Decimal(0))
            amp_derivative = slow[self.amp_pos]
            slow[self.atp_pos] += amp_derivative + sum(
                (Decimal(int(coef)) * value
                 for coef, value in zip(self.a, fast) if coef), Decimal(0))
            slow[self.ppi_pos] += -amp_derivative + sum(
                (Decimal(int(coef)) * value
                 for coef, value in zip(self.k, fast) if coef), Decimal(0))
            return (np.array([float(value) for value in slow]),
                    np.array([float(value) for value in rates]),
                    np.array([float(value) for value in full]))
