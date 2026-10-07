# R1 alternative source-general coordinate method v2

The v2 241-to-214 chart is a separate exact coordinate candidate derived
from the same canonical PNAS2017 SBML, original author CSV, and 27
`SOURCE_GENERAL` laws. It retains all 42 Class-I species, `CK_degraded`, free
`GlyAMP`, and free `MetAMP` as independent dynamic coordinates. Its exact
`A/B`, `L_E` rank, initial reconstruction, law rebasing, and all 968
`S_E=B*S_R` columns are independently certified in
`source_coordinate_certificate_v2.json`. The 241-to-224 sink certificate v1
remains available as an independently valid intermediate. V1 remains an
exact chart but its full-network numerical gates failed; the failed runs are
retained under `results/reduction/r1_full_coupled_v1`.

For pointwise comparison use the same four preregistered states and metric
`max_i |f_full_i-f_lift_i|/max(1,|f_full_i|,|f_lift_i|) <= 1e-12` as v1.
Evaluate one canonical rate vector per state, form retained RHS, and lift
with exact compiled `B*S_R` coefficients. This is a floating implementation
check separate from the exact certificate. The physical domain remains
`x_R>=0` and reconstructed `x_E>=0`, with no clipping.

For the decisive full-coupled test, integrate full source and v2-coordinate
systems separately with 968 directed extent ODEs (`dξ_j/dt=v_j`), SciPy BDF,
sparse analytic chain-rule Jacobians, `rtol=1e-12`, `atol=1e-14`, and output
times `[0]+logspace(-4,3,200)` seconds. Both use the same author condition,
unaltered source rates, and anchored affine reconstruction. Use the direct
source stoichiometric RHS with stable summation for balance diagnostics.
Keep both directed rates and extents in reverse channels; gross ledgers never
use `abs(net)`.

The fixed acceptance metrics remain per-component `E_inf <=1e-6` for all
241 species, 968 sampled directed rates, and 968 directly integrated
directed extents. `E_inf=max_t|reduced-full|/max(y_scale,1e-12)`, where
zero-initial components use `y_scale=1` and other components use their full
trajectory maximum absolute value. Full and reduced material-balance maxima
must each be `<=1e-8`. Values in `[-1e-11,0)` are numerical-negative
diagnostics; any state below `-1e-11` fails physical feasibility. All
negatives are retained and reported. A separate tight RoadRunner import and
parser-rate comparison remain required for R1 acceptance.
