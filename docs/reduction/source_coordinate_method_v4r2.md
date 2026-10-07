# R1 source-general coordinate method v4r2

V4r2 uses the independently certified exact v4 241-to-214 chart. The
canonical SBML, 27 `SOURCE_GENERAL` laws, protected 42 Class-I species,
free GlyAMP/MetAMP, rate laws, parameters, and 968 directed channels are
unchanged. V4's BDF full-window result failed the directed-extent and
material-balance gates. A 0-1 s Radau diagnostic passed all numerical
checks, so this method freezes Radau before a 0-1000 s decisive run.

Use `[0] + logspace(-4,3,200)` seconds over 0-1000 s. Integrate the full
241-state ODE and 214-coordinate ODE independently with all 968 directed
extent ODEs included directly on each model side. Use SciPy Radau with
sparse analytic full and chain-rule reduced Jacobians, `rtol=1e-12`,
`atol=1e-14`, and anchored affine reconstruction. No state or rate is
clipped; no kinetic parameter is fitted.

The pointwise RHS gate remains elementwise scaled error `<=1e-12` on the
frozen four-state set using one canonical rate vector per state. For the
full network, each of the 241 species, 968 sampled directed rates, and
968 directly integrated extents requires per-component `E_inf<=1e-6`.
Use `y_scale=1` for zero-initial components, otherwise the full-trajectory
maximum absolute value. Full and reduced material balance each require
absolute residual `<=1e-8`. Report all numerical negatives; a state
below `-1e-11` fails the declared physical-domain diagnostic. Independent
tight RoadRunner import and identical-state parser/RoadRunner rate checks
remain separate requirements for R1 acceptance.
