# R1 source-general coordinate method v5

V5 uses the canonical SBML and the same 27 `SOURCE_GENERAL` conservation
laws. It replaces v4's eliminated `CK_CP` with independent `CK_CP_ADP`,
retaining the high-turnover `CK_CP` state and the frozen-zero CK and NDK
degradation sinks. All 42 Class-I species and free `GlyAMP`/`MetAMP` remain
dynamic coordinates. The exact 241-to-214 certificate is checked separately.
This is an exact chart choice, not QSSA or a condition-specific deletion.
V1-v4 and their failed numerical results remain preserved.

Use one canonical directed rate vector for each pointwise trial state. The
unchanged four-state elementwise scaled RHS gate is `<=1e-12`; report
physical-domain and zero-row cancellation results. For full validation,
compare the 241-state source and 214-coordinate ODEs on `[0] +
logspace(-4,3,200)` seconds over 0-1000 s. Integrate all 968 directed
extent ODEs directly on both model sides. Use SciPy BDF, sparse analytic
chain-rule Jacobians, `rtol=1e-12`, `atol=1e-14`, and anchored affine
reconstruction. Keep all canonical rate laws and parameters unchanged.

All 241 species, 968 sampled rates, and 968 directly integrated extents
require per-component `E_inf<=1e-6`. Use `y_scale=1` for a zero-initial
component and otherwise the full-trajectory maximum absolute value. Full
and reduced material balance each require absolute residual `<=1e-8`.
Report every negative concentration; a state below `-1e-11` fails the
declared numerical physical-domain diagnostic. Never clip or fit.
Independent tight RoadRunner import and identical-state rate checks remain
required for R1 acceptance.
