# R1 source-general full-coupled numerical method v1r3

This is an RHS evaluation-order revision of v1r2 (SHA-256
`c3b662a56ef9efe9414fd7684004fc4d0d2e222b47e81f3352b5a506c349dfe3`).
All source kinetics, exact coordinates, author parameters, initial conditions,
solver tolerances (`rtol=1e-12`, `atol=1e-14`), output grid
(`[0] + logspace(-4,3,200)` seconds), per-component E_inf scaling, and
acceptance limits remain fixed. V1 and v1r2 failed decisive runs remain in
`results/reduction/r1_full_coupled_v1/decisive_001` and `_002`.

Both full and 214-coordinate RHS implementations now group the 290 source-
verified exact reverse channels before accumulating species derivatives.
For each source pair, evaluate the original `v_f` and `v_r` separately, then
use `S_f*(v_f-v_r)` for the RHS. Unpaired source reactions retain their own
directed terms. Exact matrix verification requires `S_net*T=S_source` for all
968 columns; no kinetic law, local parameter, or reaction ID is dropped.
Stable summation combines net-channel contributions to each species. Sparse
analytic Jacobians use the same channel transform and the full reconstruction
chain rule. The 968 directed extent ODEs still obey `dξ_j/dt=v_j` individually;
gross resource ledgers are never computed from `abs(v_f-v_r)`.

The change targets floating cancellation in the CK/CP reverse cycle, whose
two gross extents reached about 23.7 million at 1000 seconds. V1r2 still
failed the unchanged direct-extent, material-balance, and physical-domain
gates, with more than 100 reconstructed negative samples below `-1e-11`.

Acceptance remains: all 241 species, 968 sampled directed rates, and 968
directly integrated directed extents each have `E_inf <= 1e-6`; full and
reduced absolute material balance each `<=1e-8`; no state below `-1e-11`.
The separate tight RoadRunner import and parser-rate checks remain required.
