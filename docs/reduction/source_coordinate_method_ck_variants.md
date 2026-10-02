# R1 source-general CK chart variants v6 and v7

V6 and v7 are exact alternative 241-to-214 coordinate charts derived from
the same canonical SBML and 27 `SOURCE_GENERAL` laws. Both retain `CK_CP`,
the CK and NDK degradation sinks, all 42 Class-I species, and free
`GlyAMP`/`MetAMP`. Relative to v4, v6 eliminates `CK_Cr_ATP` and v7
eliminates `CK_Cr`. Their exact certificates are independent of numerical
acceptance. V5's eliminated `CK_CP_ADP` failed the short domain test; its
negative result remains preserved. No QSSA or frozen-only law is used.

For each chart, use one canonical directed rate vector per pointwise trial
state and require elementwise scaled RHS error `<=1e-12` on the same four
deterministic states. Report physical domain and zero-row cancellation.
For numerical validation use `[0] + logspace(-4,3,200)` seconds over
0-1000 s, full 241-state and reduced 214-coordinate ODEs, and all 968
separate directly integrated directed extent ODEs on both model sides.
Use SciPy BDF with sparse analytic chain-rule Jacobians,
`rtol=1e-12`, `atol=1e-14`, and anchored affine reconstruction.

Keep the existing scales and thresholds: each of 241 species, 968 sampled
rates, and 968 direct extents must have `E_inf<=1e-6`; zero-initial
components use `y_scale=1`, and others use the full-trajectory maximum
absolute value. Full and reduced material balance each require absolute
residual `<=1e-8`. Report all negatives; any state below `-1e-11`
fails the declared numerical domain diagnostic. Never clip, fit, or relax
a gate. Independent tight RoadRunner import and identical-state rate
checks are still required for R1 acceptance.
