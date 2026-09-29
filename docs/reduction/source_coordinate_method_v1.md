# R1 source-general simultaneous coordinate method v1

The canonical PNAS2017 SBML supplies species order, directed stoichiometry, and
kinetic laws. The 27 `SOURCE_GENERAL` laws in the v0 audit supply an exact left
nullspace basis. No `FROZEN_REFERENCE_ONLY` law enters the generic chart. The
first 17 named-pool degraded sinks form a 241-to-224 intermediate chart. A
deterministic exact column-rank selection extends that set to 27 non-Class-I
eliminated species, giving the 241-to-214 chart. All 42 Class-I species remain
independent and outputtable; all eliminated species remain reconstructable.

For each initial condition, recompute `b = L*x0`. With eliminated columns `E`
and retained columns `R`, use exact rational `A = inverse(L_E)` and
`B = -A*L_R`, then `x_E = A*b + B*x_R`. The physical domain is precisely
`x_R >= 0` and `x_E >= 0`; no negative value is clipped. Exact certificates
prove `L_E*A=I`, `L_E*B+L_R=0`, `S_E=B*S_R` for every directed reaction, and
invariance of the reconstruction map under an invertible rebasing of `L`.
Exact rational trial inputs are reconstructed in rational arithmetic before
conversion to floating rates. Solver supplied floating states use stable
summation, and any negative reconstruction is reported as a domain diagnostic.

The pointwise implementation gate is fixed before numerical trials:

`max_i |f_full_i - f_lift_i| / max(1, |f_full_i|, |f_lift_i|) <= 1e-12`.

At each trial state, evaluate all 968 source rates once in canonical reaction
order. Form retained derivatives by stable summation of `S_R*v`. The lifted
eliminated derivative uses coefficients compiled exactly from `B*S_R`, then
stable summation of those coefficients against that same rate vector. This
avoids a second floating multiplication of `B` by already-rounded retained
derivatives. The latter calculation remains a diagnostic, including rows
whose full derivative is zero. The exact identity and the floating gate are
reported separately. Trial states are the author initial state and the three
deterministic positive states from the v0 reverse-representation audit.

The author RoadRunner trajectory remains a source-reproduction artifact. A
separate tight independent import, common output grid, directed integrated
extents, and all-species/class/resource comparisons are required for full R1
acceptance. This method does not approve R1 based on the pointwise gate alone.

## Full coupled numerical gate, frozen before the decisive run

Integrate the complete 241-state source ODE and the 214-coordinate ODE, both
augmented by the same 968 **directed** extent states with `dξ_j/dt=v_j`. The
two models use the same author parameters, author initial condition, SciPy BDF
solver, sparse analytic Jacobian, `rtol=1e-10`, `atol=1e-12`, and output grid
`[0] + logspace(-4,3,200)` seconds. The reduced initial condition is the
source initial state restricted to `R`; recompute `b=L*x0`. For floating
integration evaluate the algebraically identical anchored reconstruction
`x_E=x_E0+B*(x_R-x_R0)` to avoid subtracting large conserved totals near
zero. This is not a projection and never clips negative values.

The trajectory metric is the project protocol's per-component
`E_inf=max_t|reduced-full|/max(y_scale,1e-12)`, with `y_scale=1` for a
zero-initial component and otherwise `y_scale=max_t|full|`. Apply it to all
241 species, all 968 directed rates sampled at the grid, and all 968 directly
integrated extents. The exact trajectory, rate, and directed-extent thresholds
are each `E_inf <= 1e-6`. Report individual maxima and the Class-I, Class-C,
resource, and other subgroup maxima. The absolute material-balance gate is
`max_t,i |x_i(t)-x_i(0)-Σ_j S_ij ξ_j(t)| <= 1e-8` for each solver. Report
conservation residuals, minimum retained/reconstructed/full concentrations,
and every negative value. Values in `[-1e-11,0)` are classified as numerical
negatives relative to the declared absolute solver tolerance; values below
`-1e-11` fail physical feasibility. Neither category is clipped.

The old RoadRunner author baseline with `rtol=1e-3, atol=1e-9` is never used
as the acceptance oracle. A separate RoadRunner import at the tight settings
above is required as an independent engine diagnostic, including source-rate
comparison at identical states. Solver-state and direct integrated-extent
comparisons are labeled separately from any rate-quadrature diagnostic.
