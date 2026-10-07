# R1 source-general full-coupled numerical method v1r2

This is a numerical precision revision of
`source_coordinate_method_v1.md` (SHA-256
`ae6edf1df37d97bd9710481c1db1dc05350aa23ecf743192fb87bbb6f06c7f05`).
The canonical source, exact chart, protected outputs, physical-domain rule,
time grid, error definitions, and all acceptance thresholds remain exactly as
registered there. No source parameter, kinetic law, model state, or gate is
changed. The v1 decisive failure is retained in
`results/reduction/r1_full_coupled_v1/decisive_001`.

The v1 run exposed 22-million-unit opposing gross extents in reactions
`re0000000332/0333`. Their separately integrated values differed by
`5.55e-5`, while species and rate trajectory errors passed. Direct material
balance was slightly above `1e-8`, and three reconstructed `CK_degraded`
samples were below the declared `-1e-11` numerical-negative floor. These
failures motivate more accurate integration and accumulation, not a looser
comparison criterion.

For v1r2, integrate the same full 241-state and 214-coordinate systems,
each with all 968 directed extent states, using SciPy BDF and the same sparse
analytic chain-rule Jacobians at `rtol=1e-12`, `atol=1e-14`. Use the same
`[0] + logspace(-4,3,200)` second output grid and the same author condition.
Evaluate `x-x0-S*ξ` with `math.fsum` over each species's directed source
contributions to avoid avoidable cancellation of large opposing gross
extents. This changes only floating accumulation of the diagnostic. Keep
all observed negative states; never clip or project them.

The unchanged acceptance gates are per-component `E_inf <= 1e-6` for all
241 species, 968 sampled directed rates, and 968 directly integrated directed
extents; absolute material balance `<=1e-8` for both systems; and no
reconstructed state below `-1e-11`. Zero-initial quantities retain
`y_scale=1`. Independently imported tight RoadRunner and parser-rate checks
remain required before R1 acceptance.
