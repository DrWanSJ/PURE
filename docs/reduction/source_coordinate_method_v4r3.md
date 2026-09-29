# R1 source-general coordinate method v4r3

This decisive method is registered after the complete-window v4 reverse-pair
extent-basis diagnostics and before the decisive run. It uses the canonical
241-species, 968-directed-reaction source, the exact v4 241-to-214
`SOURCE_GENERAL` certificate, and the frozen author initial condition. No
source rate, parameter, stoichiometric column, or scientific gate changes.

Integrate the 241-state source and the 214-coordinate model separately over
0-1000 s, reporting at `[0] + logspace(-4,3,200)` seconds. Use SciPy BDF,
`rtol=2.5e-13`, `atol=2.5e-15`, sparse analytic chain-rule Jacobians,
anchored affine reconstruction, and the `stable_direct` source RHS, which
accumulates the same 968 directed source rates with `math.fsum`.

The model-side extent system has 968 directly integrated ODE coordinates.
For each of the 290 source-certified reverse pairs `(f,r)`, integrate the
invertible coordinates `n'=v_f-v_r` and `q'=v_r`, initially zero, then recover
the original directed gross extents as `xi_f=n+q`, `xi_r=q`. Every unpaired
directed extent has `xi_j'=v_j`. Apply the same linear transform to the lower
Jacobian block. This retains the two original rates, reaction IDs, and gross
ledgers. It performs no rate quadrature and never substitutes `abs(net)` for
a directed gross extent.

Compare all 241 reconstructed species, including all 42 Class-I and all 29
Class-C outputs; all 968 sampled directed rates; and all 968 recovered
directed gross extents. The preregistered per-component `E_inf` limit is
`1e-6` for each of species, rates, and extents. For zero-initial components,
`y_scale=1`; otherwise use the maximum absolute full-trajectory value. The
absolute source material-balance residual, computed from **the recovered
968 gross extents**, must be `<=1e-8` independently for full and reduced
systems. The exact reverse-net-basis residual is reported separately as a
diagnostic. Report every negative; a value below `-1e-11` fails the declared
numerical physical-domain diagnostic. The separate pointwise RHS gate remains
`<=1e-12`.

R1 still requires tight independent RoadRunner import and parser-versus-
RoadRunner rate comparisons at identical states. This numerical result alone
is not the R1 PASS condition and does not authorize R2.
