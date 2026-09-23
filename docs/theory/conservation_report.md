# D6 conservation reduction and dimensional/dimensionless validation

The exact 12-to-6 conservation reduction was validated on 2026-09-22 with MATLAB R2025b Update 5, starting at Git commit `91bb364`. The dimensional/dimensionless trajectory back-transform was validated on 2026-09-23 from `0b6fd01287fad6ee323ce4f9ed27e9605701ff6a`. **D6 complete.** No parameters were fitted, no states were clipped, and no canonical B1 scientific source, baseline or audited dimensionless definition was changed.

## Representation and structural result

B1 has 10 physical states plus two no-feedback accounting integrators, $D_{nt}$ and $D_{TLcat}$, for 12 augmented states. The fixed orders are

$$
x=[NTP,NXP,nt,A,T,AT,a,CP,C,TLcat,D_{nt},D_{TLcat}]^T,
$$

$$
V=[V_{TX},V_{nt,deg},V_{RS},V_{TL},V_{TL,deg},V_{EN}]^T.
$$

The effective stoichiometric matrix is the matrix in [theory notes, sections 3.1 and 4.4](../theory_notes.md), with the loaded multiplicities used for its species divisors. The regression also compares its physical rows against `model_definition.json` and its action against the canonical RHS. Actual results are

$$
S_{eff}\in\mathbb R^{12\times6},\qquad
\operatorname{rank}(S_{eff})=6,\qquad
\operatorname{rank}(L)=6,\qquad
\max|LS_{eff}|=2.7755575615628914\times10^{-17}.
$$

Here $L$ denotes the invariant coefficient matrix; $L_{protein}=p.L$ below is the distinct protein-length parameter. The six invariant rows are the five published balances with explicit degradation accounting, followed by the RS/TL energy-cost coupling invariant:

$$
\begin{aligned}
B_{NTP}&=n_{NTP}NTP+NXP+nt+D_{nt},\\
B_{AA}&=n_A A+a+n_T AT,\\
B_{tRNA}&=n_T T+n_T AT,\\
B_{CP}&=CP+C,\\
B_{TLcat}&=TLcat+D_{TLcat},\\
I_6&=NXP+C-3a-n_T AT.
\end{aligned}
$$

Since the left nullspace has dimension $12-6=6$, these six independent rows form its complete basis. These are invariants of this coarse-grained model, not claims of complete elemental, charge or thermodynamic energy conservation. Their constants are evaluated from `p.y0`, `p.n_NTP`, `p.n_A`, `p.n_T` and the canonical zero initial accounting pools.

### Structural zero modes of the full Jacobian

For the 12-state augmented representation, the vector field has the form

$
f(x)=S_{eff}v(x),\qquad J_{full}=S_{eff}\frac{\partial v}{\partial x}.
$

Because $LS_{eff}=0$,

$
LJ_{full}=LS_{eff}\frac{\partial v}{\partial x}=0.
$

Thus $\operatorname{rank}(J_{full})\le \operatorname{rank}(S_{eff})=6$. In the unreduced 12-state coordinates, at least six zero modes are therefore structural consequences of the conserved/accounting directions and of representing six-dimensional stoichiometric motion with twelve state coordinates. They do **not**, by themselves, imply a bifurcation, critical slowing, or a physical neutral mode.

Stability and slow-mode conclusions for a fixed compatibility class must instead be based on the Jacobian restricted to the stoichiometric tangent space, equivalently the exact six-state reduced Jacobian used here. A zero eigenvalue that persists in that reduced Jacobian would require a separate dynamical interpretation; it must not be attributed automatically to conservation.

## Chosen coordinates and reconstruction

The coordinates are fixed as requested, with MATLAB indices `[1 3 4 6 8 10]`:

$$
z=[NTP,nt,A,AT,CP,TLcat]^T.
$$

The omitted states are reconstructed in this dependency order:

$$
\begin{aligned}
T&=B_{tRNA}/n_T-AT,\\
a&=B_{AA}-n_A A-n_T AT,\\
C&=B_{CP}-CP,\\
NXP&=I_6-C+3a+n_T AT,\\
D_{TLcat}&=B_{TLcat}-TLcat,\\
D_{nt}&=B_{NTP}-n_{NTP}NTP-NXP-nt.
\end{aligned}
$$

The assembled output retains the full 12-state order above. Initial reconstruction actually returned `[1500,0,0,300,1.9,0,0,20000,0,2.2,0,0]`, derived from the existing loader. A separate synthetic algebra fixture changes in-memory initial pools and multiplicities to detect hardcoded standard-initial constants; it is not a fitted model or an alternative scientific parameter set.

## Exact reduced ODE

The implementation reconstructs the 10 physical states, calls `rhs_pure_literature_reference`, and selects derivatives `[1 3 4 6 8 10]`. It contains no second implementation of the rate laws:

$$
\begin{aligned}
\dot{NTP}&=(-V_{TX}-V_{RS}-2V_{TL}+V_{EN})/n_{NTP},\\
\dot{nt}&=V_{TX}-V_{nt,deg},\\
\dot A&=-V_{RS}/n_A,\\
\dot{AT}&=(V_{RS}-V_{TL})/n_T,\\
\dot{CP}&=-V_{EN},\\
\dot{TLcat}&=-V_{TL,deg}.
\end{aligned}
$$

Differentiating the reconstruction gives

$$
\begin{aligned}
\dot T&=-\dot{AT}=(-V_{RS}+V_{TL})/n_T,\\
\dot a&=-n_A\dot A-n_T\dot{AT}=V_{TL},\\
\dot C&=-\dot{CP}=V_{EN},\\
\dot{NXP}&=-\dot C+3\dot a+n_T\dot{AT}=V_{RS}+2V_{TL}-V_{EN},\\
\dot D_{TLcat}&=-\dot{TLcat}=V_{TL,deg},\\
\dot D_{nt}&=-n_{NTP}\dot{NTP}-\dot{NXP}-\dot{nt}=V_{nt,deg}.
\end{aligned}
$$

Thus the affine reconstruction restores every augmented derivative on the invariant leaf and recovers the initial state. Wherever the canonical RHS is defined and the initial-value problem is unique, the reconstructed reduced solution is the full solution. No timescale assumption, QSSA, fast-slow approximation or parameter fitting is involved; only invariant-constrained redundant coordinates are removed. Numerical sampling checks the implementation of this identity: 51 trajectory points across the three DNA conditions gave a maximum derivative residual of $4.163336342344337\times10^{-17}$ uM/s, below the preregistered $10^{-12}$ tolerance.

## Preregistered trajectory validation

Both simulators used `ode15s`, `Tfinal=14400` s, `OutputDt=10` s, `RelTol=1e-10`, `AbsTol=1e-12`, with identical output grids of 1,441 points. The full reference is the existing `simulate_pure_literature_reference`, including both accounting integrators. Every output point is compared for all 12 states, all 6 rates and both observables:

$$
mRNA=nt/(3L_{protein}),\qquad protein=a/L_{protein},\qquad L_{protein}=p.L.
$$

The [acceptance criteria](../audit/exact_conservation_20260922/acceptance_criteria.json) and their [timestamped hash](../audit/exact_conservation_20260922/preregistration.json) were recorded before the first numerical validation. For each quantity $j$,

$$
scale_j=\max\left(\max_t|reference_j(t)|,10^{-12}\right),\qquad
error_j=\frac{\max_t|reduced_j(t)-reference_j(t)|}{scale_j}.
$$

All four categories must have maximum normalized error at most $10^{-6}$. Thresholds and solver tolerances were not changed after inspecting results.

| DNA (uM) | Max state normalized error | Max rate normalized error | mRNA normalized error | Protein normalized error | States / rates / mRNA / protein |
| --- | ---: | ---: | ---: | ---: | --- |
| 0.00034 | 2.057321e-7 | 1.886226e-7 | 6.797277e-12 | 1.741782e-8 | PASS / PASS / PASS / PASS |
| 0.0017 | 2.066044e-7 | 1.894230e-7 | 4.268080e-12 | 3.702314e-8 | PASS / PASS / PASS / PASS |
| 0.0068 | 2.087435e-7 | 1.913852e-7 | 3.749641e-12 | 2.902742e-8 | PASS / PASS / PASS / PASS |

Raw maximum absolute differences, each taken across the complete trajectory:

| DNA (uM) | States (uM) | Rates (uM/s) | mRNA (uM) | Protein (uM) |
| --- | ---: | ---: | ---: | ---: |
| 0.00034 | 1.813618e-6 | 1.271750e-7 | 8.248992e-13 | 2.534432e-9 |
| 0.0017 | 1.034523e-5 | 1.277309e-7 | 2.059242e-12 | 1.448363e-8 |
| 0.0068 | 1.220524e-5 | 1.290816e-7 | 4.089729e-12 | 1.708882e-8 |

The largest normalized state and rate errors occur in NXP and V_EN respectively for all three conditions. The largest raw state errors occur in C (low DNA) and CP (middle/high DNA). Solver tolerances control local error estimates; they are not a guarantee that separately integrated representations agree to that relative tolerance in every reconstructed pool. The measured comparisons pass the specified trajectory criterion without repair.

All full/reconstructed states, rates and observables were finite. All 12 state minima were nonnegative on the output grid; the minimum was exactly zero, with **zero negative samples** in the reconstructed trajectories. No roundoff exception was needed. The preregistered floating-point allowance was $64\,\mathrm{eps}(\max(1,|x_0|,|Lx_0|))=2.3283064365386963\times10^{-10}$ uM. The maximum reconstructed invariant residual was $9.094947017729282\times10^{-13}$ uM for each condition. These physicality checks concern the saved output grid, not every internal solver stage.

## Actual regression evidence and reproduction

The native MATLAB process exited 0; stderr was empty. Actual `TestResult` summaries:

| Suite | Passed | Failed | Incomplete |
| --- | ---: | ---: | ---: |
| `test_exact_conservation_reduction` | 8 | 0 | 0 |
| `test_pure_literature_reference` | 9 | 0 | 0 |
| `test_codegen_and_provenance` | 5 | 0 | 0 |

`allPassed = 1`. Read the [actual stdout and TestResult tables (UTF-8 copy)](../audit/exact_conservation_20260922/matlab_stdout.utf8.txt), [original native stdout](../audit/exact_conservation_20260922/matlab_stdout.txt), [structured results](../audit/exact_conservation_20260922/validation_results.json), and [source integrity audit](../audit/exact_conservation_20260922/integrity_after.json). The JSON retains per-quantity raw errors, reference scales, normalized errors, minima and negative counts. The encoding conversion is byte-roundtrip checked; the native evidence is unchanged.

MATLAB emitted a startup warning for a pre-existing missing `slanCM` search-path directory. It is retained in stdout; no environment paths were changed. A separate `checkcode` run reported zero messages for all six new MATLAB files. The startup warning is not a scientific inconsistency or a failed test.

Reproduce from the repository root in MATLAB:

```matlab
addpath('scripts');
summary = run_exact_conservation_validation();
```

The runner executes the three required `runtests` calls and displays their real results. This section preserves the exact-reduction evidence from 2026-09-22; the subsequent dimensional/dimensionless validation and its four-suite regression are recorded below.

## Validity of the exact reduction

No scientific inconsistency was found in the checked canonical structure, reconstruction identities or deterministic trajectory comparisons. This establishes an exact reduced representation of the current frozen B1 deterministic model with numerical implementation agreement on the tested conditions. It does **not** establish independent predictive validity for real experimental systems, extend model mechanisms, or demonstrate a speedup.

## Dimensional/dimensionless trajectory validation (2026-09-23)

**PASS; D6 complete.** The new simulator integrates the existing audited compact 12-state equations directly in $\tau$, independently of the dimensional reference. The canonical RHS is called only after integration to cross-check dimensional rates. The state order remains `[NTP,NXP,nt,A,T,AT,a,CP,C,TLcat,D_nt,D_TLcat]`.

The runtime scales and all groups are computed from `pure_literature_reference_params` and its initial state:

$$
s_x=[c_{NTP,0},n_{NTP}c_{NTP,0},n_{NTP}c_{NTP,0},c_{A,0},c_{T,0},c_{T,0},n_Ac_{A,0},c_{CP,0},c_{CP,0},c_{TLcat,0},n_{NTP}c_{NTP,0},c_{TLcat,0}]^T.
$$

$$
y=x\oslash s_x,\qquad x=s_x\odot y,\qquad
\tau=k_{nt,deg}t,\qquad t=\tau/k_{nt,deg},\qquad
\widetilde V=V/V_*,\qquad V=V_*\widetilde V,
$$

$$
V_*=k_{nt,deg}n_{NTP}c_{NTP,0}.
$$

The automatically mapped initial state is `[1,0,0,1,1,0,0,1,0,1,0,0]`. State/time/rate roundtrips passed on the canonical state and deterministic synthetic positive fixtures; measured maximum raw roundtrip errors were zero. The parameter checks cover all 20 runtime quantities (the audited groups plus `fTA` and the TLcat/nucleotide scale ratio), including independent pool ratios and synthetic in-memory multiplicities. Scientific parameters were not changed.

Both systems use `ode15s`, `RelTol=1e-10`, `AbsTol=1e-12`, 0–14400 s and 10 s physical output spacing: 1,441 points per DNA condition. The dimensionless endpoint is $\tau=1.14048$. Maximum time roundtrip error is $1.8189894035458565\times10^{-12}$ s. The [fixed acceptance criteria](../audit/nondim_trajectory_20260923/acceptance_criteria.json) and [timestamp/hash preregistration](../audit/nondim_trajectory_20260923/preregistration.json) precede the first trajectory run. The normalization is the same reference-trajectory maximum with a $10^{-12}$ floor used above, and all four trajectory thresholds remain $10^{-6}$.

Maximum normalized errors over every output point and quantity in each category:

| DNA (uM) | States | Rates | mRNA | Protein |
| --- | ---: | ---: | ---: | ---: |
| 0.00034 | 7.637046621e-09 | 7.169911960e-09 | 3.898811970e-12 | 3.617618922e-09 |
| 0.0017 | 7.635974295e-09 | 7.168981293e-09 | 2.826440631e-12 | 1.903857669e-09 |
| 0.0068 | 7.634174568e-09 | 7.167419490e-09 | 2.564091919e-12 | 1.245381820e-09 |

Maximum raw absolute errors over the same full trajectories:

| DNA (uM) | States (uM) | Rates (uM/s) | mRNA (uM) | Protein (uM) |
| --- | ---: | ---: | ---: | ---: |
| 0.00034 | 3.799295030e-07 | 4.834169398e-09 | 4.731492975e-13 | 5.263924296e-10 |
| 0.0017 | 5.357505870e-07 | 4.834156409e-09 | 1.363686941e-12 | 7.447982786e-10 |
| 0.0068 | 5.274305295e-07 | 4.834134981e-09 | 2.796651799e-12 | 7.331726337e-10 |

The pointwise chain-rule comparison uses 51 feasible states sampled from the canonical reference across all three DNA conditions. Its maximum absolute RHS residual is $2.8421709430404007\times10^{-14}$, below the preregistered $10^{-12}$ threshold.

All six common-scale rates are independently back-transformed and compared against canonical rates evaluated on the restored states, as well as against the dimensional reference trajectory. In particular,

$$
\widetilde V_{TL,deg}=\mu_{TL,deg}\frac{c_{TLcat,0}}{n_{NTP}c_{NTP,0}}y_{10},\qquad
V_{TL,deg}=k_{TL,deg}TLcat.
$$

The maximum same-state rate back-transform discrepancy is below $4\times10^{-16}$ uM/s. Observable definitions remain $mRNA=nt/(3p.L)$ and $protein=a/p.L$.

### Solver diagnosis and unchanged acceptance criteria

The first run passed all trajectory comparisons but failed the extra $I_6$ regression: drift reached $4.3267576188554813\times10^{-8}$ uM, exceeding the registered $10^{-8}$ criterion for this zero-initial invariant. Supplying the analytic derivative of the unchanged compact RHS to `ode15s` reduced that drift below $1.1\times10^{-12}$ uM. The default finite-difference Jacobian and analytic-Jacobian runs used identical equations, scales, parameters, grids and numeric tolerances; there was no projection, clipping, refit or threshold relaxation. The [solver revision](../audit/nondim_trajectory_20260923/implementation_revision.json) was recorded before its rerun, and the failed native logs are retained.

Every analytic Jacobian entry was checked against complex-step differentiation at 51 points: maximum scaled residual $2.217878763897636\times10^{-15}$. The sampled $I_6$ derivative was at most $9.00399754755199\times10^{-18}$ uM/s. The initial compact RHS and mapping builder remained byte-identical throughout the solver fix.

### Back-transformed invariants and physicality

| Invariant | Maximum absolute residual across all three trajectories (uM) |
| --- | ---: |
| B_NTP | 1.728039933e-11 |
| B_AA | 1.091393642e-11 |
| B_tRNA | 1.563194019e-13 |
| B_CP | 7.275957614e-11 |
| B_TLcat | 3.996802889e-15 |
| I6 | 1.051603249e-12 |

All 12 back-transformed states, all rates and both observables were finite. The minimum state value was zero, with zero negative samples in every state and every DNA condition; the reference trajectories also had zero negative samples. The registered physicality allowance was $2.3283064365386963\times10^{-10}$ uM and was not needed. The maximum scaled six-invariant residual was $1.0516032489249483\times10^{-12}$, below $10^{-8}$. These checks apply to the output grid.

### Final evidence and completion boundary

| MATLAB suite | Passed | Failed | Incomplete |
| --- | ---: | ---: | ---: |
| `test_dimensionless_trajectory_equivalence` | 12 | 0 | 0 |
| `test_exact_conservation_reduction` | 8 | 0 | 0 |
| `test_pure_literature_reference` | 9 | 0 | 0 |
| `test_codegen_and_provenance` | 5 | 0 | 0 |

`allPassed = 1`; native MATLAB exit code 0, empty stderr. All six new MATLAB files have zero analyzer messages. The unchanged MATLAB symbolic audit passed 12/12 equations and both sets of five published balances. Its generated text differed only in CRLF/LF serialization; complete normalized text equality was verified and the original bytes restored. The startup warning about the pre-existing missing `slanCM` directory remains in the native log.

The historical full-12-state [mapping certificate](nondim_map.json) includes state/time/rate mappings, scale/group definitions, observables, clearly labeled loaded reference values, source SHA-256 fingerprints and validation status for that earlier full-state audit. It remains historical evidence, not a parameter source. The current reduced D6 v2 mapping certificate is `models/literature_reference/dimensionless/nondim_map.json`, linked again in the final v2 section below. [Structured results](../audit/nondim_trajectory_20260923/validation_results.json), [native TestResult output (UTF-8 copy)](../audit/nondim_trajectory_20260923/matlab_stdout.utf8.txt), [source integrity](../audit/nondim_trajectory_20260923/integrity_after.json) and [audit/reproduction notes](../audit/nondim_trajectory_20260923/README.md) provide the evidence chain.

D6 now has completed rank, complete left nullspace, independent coordinates, exact conservation reduction, full/reduced validation, dimensional/dimensionless back-transform validation and `nondim_map.json`. This establishes mathematical/numerical equivalence of representations of the current frozen B1 deterministic model only. It does not establish independent experimental validation, biological completeness, new biological predictions or a frozen `PURE_resource_core`.

## Independent six-state dimensionless validation (v2, 2026-09-23)

**D6 = COMPLETE under preregistered v2; historical v1 = FAIL remains unchanged.** The additional reduced simulator independently integrates `[y1,y3,y4,y6,y8,y10]` in tau, inverse-transforms `[NTP,nt,A,AT,CP,TLcat]`, and exactly reconstructs all 12 dimensional states. The existing 2026-09-21 scaling, canonical parameters/rate laws and dimensional reconstruction are unchanged.

The original composite derivative gate reproduced `1.8843676619084704e-12 > 1e-12`. Symbolically equivalent centered reconstruction did not improve it, so the existing production invariant form was retained. Separately preregistered v2 gates pass: same-full-state RHS residual `4.263256414560601e-14 <= 1e-12`; conditioning-scaled reconstruction residual `7.551180140159472e-16 <= 64*eps(double)`; all three DNA full-grid comparisons of 12 states, six rates, mRNA and protein pass the unchanged `1e-6` criterion. All six dimensionless invariants pass `1e-8`; output-grid negative count is zero. Five required suites pass 52/52 and repository-wide tests pass 89/89, zero failed or incomplete.

See the [reduced nondimensionalization report](nondimensionalization_report.md), [current generated map](../../models/literature_reference/dimensionless/nondim_map.json), and [v2 audit](../audit/nondimensionalization_validation_v2_20260923/README.md). The earlier numerical tables and historical 12-state mapping certificate above remain evidence for their original runs. This completion concerns mathematical/numerical equivalence only; it does not add experimental validation or enter D7/D10.
