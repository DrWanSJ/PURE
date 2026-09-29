# R1 source-general coordinate method v4

V4 is an exact alternative chart using the canonical SBML and the same 27
`SOURCE_GENERAL` laws. Relative to v3, it retains the frozen-zero
`NDK_degraded` sink and eliminates the independent `NDK_ATP` enzyme-bound
coordinate. V3 reconstructed `NDK_degraded` below the declared numerical
domain floor in full-window diagnostics. V4 also retains `CK_degraded`, all
42 Class-I species, free `GlyAMP`, and free `MetAMP`. No QSSA or
condition-specific invariant is used. The exact 241-to-214 certificate
precedes this numerical run; v1-v3 and their failed runs remain preserved.

The pointwise RHS gate uses one canonical directed rate vector per trial
state. It requires elementwise scaled error at most `1e-12` on the frozen
four-state set, with physical-domain and zero-row reports. The full-network
window is 0-1000 s on `[0] + logspace(-4,3,200)` seconds. Compare the full
241-state ODE with the 214-coordinate ODE and integrate all 968 separate
directed extent ODEs on each model side. Use SciPy BDF with sparse analytic
chain-rule Jacobians, `rtol=1e-12`, `atol=1e-14`, and anchored affine
reconstruction. The canonical directed rate laws and parameters are unchanged.

All 241 species, 968 sampled rates, and 968 directly integrated extents
require per-component `E_inf<=1e-6`. Use `y_scale=1` for a zero-initial
component and otherwise the full-trajectory maximum absolute value. Full
and reduced material balance each require an absolute residual `<=1e-8`.
Report every negative; a state below `-1e-11` fails the declared numerical
physical-domain diagnostic. No clipping, fitting, or gate relaxation is
permitted. Tight independent RoadRunner import and identical-state
parser/RoadRunner rate checks remain required for R1 acceptance.
