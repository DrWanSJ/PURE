# R1 alternative source-general coordinate method v3

V3 is an exact alternative chart from the same canonical SBML and 27
`SOURCE_GENERAL` laws. It replaces v1's eliminated `CK_degraded` with
`CK_ATP`; all other 26 eliminated species are unchanged. It retains all
42 Class-I species, free `GlyAMP`, free `MetAMP`, and the CK degradation sink.
The 241-to-214 affine map, exact invertibility, all 968 lifted columns,
rebasing, and initial reconstruction are certified independently in
`source_coordinate_certificate_v3.json`. V1 and v2 remain preserved,
including their negative numerical runs. This coordinate selection is exact
algebra, not QSSA or a biological pooling decision.

Pointwise implementation uses one canonical rate vector for the author
initial condition and the same three deterministic positive states as v1.
Its unchanged elementwise scaled RHS gate is `<=1e-12`; report physical
domain and zero-row cancellation without clipping.

For full coupled comparison, use the same author condition, `[0] +
logspace(-4,3,200)` second grid, full 241-state and v3 214-coordinate
systems, and all 968 direct directed extent ODEs (`dξ_j/dt=v_j`). Use
SciPy BDF with sparse analytic chain-rule Jacobians, `rtol=1e-12`,
`atol=1e-14`, and anchored affine reconstruction. Evaluate the source RHS
from the canonical directed rate vector; preserve every directed rate and
parameter. Stable `math.fsum` material-balance diagnostics retain both gross
directions of every reverse channel.

The fixed thresholds and scales are unchanged: all 241 species, 968 sampled
rates, and 968 directly integrated extents require per-component
`E_inf<=1e-6`, using `y_scale=1` for zero-initial components and otherwise
the full-trajectory maximum absolute value. Full and reduced material
balance each require `<=1e-8` absolute residual. Any state below `-1e-11`
fails the declared physical-domain diagnostic; smaller numerical negatives
are reported, never clipped. Independent tight RoadRunner import and
identical-state parser/rate comparison remain required for R1 acceptance.
