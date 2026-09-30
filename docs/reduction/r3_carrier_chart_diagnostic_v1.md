# R3 exact carrier coordinates and exploratory closure diagnostic

Status: **EXACT COORDINATE CERTIFICATE PASS; QSSA PILOT UNVALIDATED.**
The source-derived coordinate result below is exact. The sampled closure
roots are exploratory numerical diagnostics and are not a full coupled
reduced-model comparison or an R3 terminal result.

The historical selective candidate contains 21 GlyRS/MetRS bound complexes;
free GlyAMP and MetAMP remain dynamic. The source's 27 SOURCE_GENERAL laws
give rank six to the law columns of those 21 complexes. Six R1-retained
carrier coordinates span that same law-column space: free GlyRS, free
MetRS, tRNAGlyGCC, tRNAfMetCAU, Gly, and Met. The exact rational matrix
`C` in `r3_carrier_chart_v1.json` satisfies

`L_carrier C + L_fast = 0`.

For fast complexes `q`, define transformed slow carriers
`z_carrier = x_carrier - C q`, so `x_carrier = z_carrier + C q`.
Every nonzero entry of `C` is `-1`: when an enzyme-bound complex gains one
unit, the relevant free enzyme, tRNA, and/or amino-acid carrier loses one
unit according to its source-derived law content. The other slow R1
coordinates are retained; all 27 R1 eliminated coordinates remain
unchanged under this fast-carrier adjustment. The rational perturbation
test `delta_q=1/100000` for all 21 fast states keeps all six carriers
nonnegative at the author initial condition, preserves all 27 laws exactly,
and gives zero exact delta for every R1 eliminated coordinate. Five
adversarial tests include a wrong-sign carrier coefficient, a missing
carrier, and a frozen-only law inserted as a generic law.

For a full source field partitioned into fast and slow physical rows
`F_q` and `F_s`, the exact transformed carrier derivative is
`z'_carrier = F_carrier - C F_q`. A future QSSA realization may set
`G(z,q)=F_q(x(z,q))=0` on a physical attracting branch. Its derivative
must include the implicit term `dq/dz=-G_q^{-1}G_z`; deleting fast
Jacobian rows is invalid. Other source reactions, rates, and both directed
gross extents stay present.

The exploratory diagnostic evaluates the canonical fast-row RHS at eight
saved full-network states from `t=0` to `1000 s`. A solver found
nonnegative roots for the six-carrier coordinate at all eight samples;
maximum absolute fast-row residual was `3.73e-12`, and maximum drift in
the 27 SOURCE_GENERAL inventories was `5.77e-14`. This is a sample result,
not proof of uniqueness, attraction, trajectory accuracy, process-flux
accuracy, or validity across the registered ten-condition grid.

The same sampled calculation exposes why two simpler coordinate choices
cannot be treated as physical reduced states at the same initial
inventories. Holding free enzyme fixed while changing bound complexes
shifts an enzyme family total by about `404` at `t=0`. Reconstructing only
free enzyme fixes those two pools but still shifts another SOURCE_GENERAL
inventory by `0.803` at `t=0`. These are structural accounting failures,
even though the fast algebraic residuals are small. All four exploratory
attempts are retained under `results/reduction/r3_closure_diagnostic_v1/`;
`attempt_004/result.json` is the expanded eight-sample comparison.

Next, implement both candidate closures in the complete R1-coordinate
coupled system, screen the physical root and timescales on each fixed grid
condition, and measure the required protected species, rates, directed
resource extents, and balances. No R3 acceptance status is assigned here.
