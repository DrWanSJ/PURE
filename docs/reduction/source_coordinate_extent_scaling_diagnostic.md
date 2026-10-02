# R1 v4 directed extent state scaling diagnostic

This is a numerical diagnostic for the exact v4 SOURCE_GENERAL chart, not a
decisive R1 acceptance run. The canonical rates, parameters, stoichiometry,
initial state, gross directionality, and scientific thresholds are unchanged.

For each of the 968 directed reactions, integrate a separate state
`zeta_j = xi_j / 1000` with `zeta_j' = v_j(x) / 1000` and `zeta_j(0) = 0`.
Recover each physical gross extent as `xi_j = 1000*zeta_j` before computing
the trajectory errors and material balance. The lower Jacobian block is
scaled by the same factor. The common scale of 1000 is declared before the
run to reduce the numerical range of the large opposing CK/CP gross extent
states without selecting reactions or fitting any observed error. No
interpolated rate quadrature or net-to-gross conversion is used.

Run the complete 0-1000 s, 201-point author condition on the full 241-state
and reduced 214-coordinate systems separately with SciPy BDF and the
`stable_direct` source RHS. Use `rtol=5e-13`, `atol=5e-15`, the same setting
as the prior v4 stable-RHS diagnostic whose extent error passed but balance
failed. Test all 241 species, all 968 sampled directed rates, all 968 recovered
direct integrated extents, source balance, and physical domain. Keep
per-component species/rate/extent `E_inf <= 1e-6`, full and reduced balance
absolute residual `<= 1e-8`, and negative domain floor `-1e-11`.

If this diagnostic passes every fixed gate, register a distinct method file
before an independent decisive run. If any gate fails, preserve the result
and continue diagnosis. The tight RoadRunner import and identical-state
rate check remain separately required.
