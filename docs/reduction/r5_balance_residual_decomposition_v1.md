# R4 balance residual decomposition

The exact conservation test is L[x(t)-x0] for the27 SOURCE_GENERAL laws with LS=0. It differs from x-x0-Sxi, which mixes state and ledger integrations. Every stored completed R3 full-source trajectory and R4 family trajectory was analyzed without modification. Ordinary, Kahan, math.fsum and longdouble sums act only on the diagnostic; the original binary arrays are unchanged. On this platform longdouble mantissa is 52 bits, so it may offer no extra precision beyond double; math.fsum is the reliable high-accuracy sum.

For reduced coordinates x=c+Xz z+Dq, decompose full residual exactly as Xz(z-z0-TSxi)+D(q-q0-Sqxi). The second term is algebraic manifold tracking minus microscopic fast ledger change. A zero-order graph does not supply the missing finite net redistribution automatically. This accounting identity is checked, not declared a new conservation failure. Reduced-coordinate ledger residual is assessed independently.

Stored solver-step CSVs preserve times/counters but omit accepted state arrays/dense polynomials. Thus sampled trapezoid integration of RHS is explicitly coarse-quadrature/interpolation-confounded, not a direct state-solver error measurement. Existing same-trajectory tight ledgers and state uncertainty runs quantify components, not rigorous error bounds; dense-output contribution and state integration error cannot be separated completely from these stored files. No expensive source campaign was launched to fill that gap.

Measured summary:

```json
{
  "classification": "MIXED / UNRESOLVED",
  "source_general_laws": 27,
  "max_exact_law_drift": 2.3680765681710625e-10,
  "max_primary_source_ledger_residual": 7.430298865074292e-07,
  "max_reduced_slow_ledger_residual": 5.486685040523298e-06,
  "max_postprocessing_summation_change": 1.8480932340025902e-09,
  "max_same_trajectory_tight_extent_change": 7.521652150899172e-06,
  "max_reconstructed_full_residual": 4.349483736232863,
  "max_algebraic_tracking_ledger_difference": 2.269915147661213,
  "max_affine_decomposition_identity_error": 3.3866243143165775e-12,
  "source_conservation_failure_observed": false,
  "trajectory_mutation": false,
  "historical_gate_changed": false,
  "longdouble_mantissa_bits": 52,
  "direct_state_vs_dense_vs_extent_error_separately_identified": false,
  "reason": "Stored step records contain times/counters, not all accepted states/dense polynomials. Tight-ledger variation identifies a numerical component; complete state/dense/extent error attribution is unavailable. Full reduced ledgers require algebraic redistribution policy."
}
```

MODEL CONSERVATION FAILURE: no source-general failure observed at the measured roundoff scale. SOLVER TRAJECTORY ERROR: uncertainty measured, exact component unresolved. LEDGER INTEGRATION ERROR: tighter same-trajectory ledgers show numerical sensitivity. NUMERICAL CANCELLATION: compensated/high-accuracy differences measured independently. REDUCED-COORDINATE ACCOUNTING ERROR: no new structural identity defect identified, but full-state gross-ledger policy lacks algebraic redistribution; this differs from the slow ledger numerical error. Classification remains MIXED / UNRESOLVED. R4 registered thresholds and every raw/native/derived historical classification remain frozen.
