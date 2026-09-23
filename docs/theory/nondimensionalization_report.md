# Reduced nondimensionalization validation — D6 COMPLETE (v2)

**PATH B: historical v1 = FAIL; preregistered v2 = PASS.** The original failure, criteria and implementation revision remain byte-identical. V2 separates vector-field identity from the rounding effects of independent conservation reconstructions, and retains the unchanged trajectory, invariant, round-trip and physicality acceptance requirements. All five required suites pass (52/52), and repository-wide regression passes (89/89, zero failed or incomplete).

This is the existing 2026-09-21 audited 12-state scaling applied to the 2026-09-22 exact six-state conservation reduction, not a new nondimensionalization. The earlier 2026-09-23 full 12-state integration remains distinct historical evidence. The new simulator independently integrates six dimensionless coordinates, inverse-transforms them, and reconstructs the full dimensional state. Canonical equations, parameters, baseline, dimensional reconstruction and all production nondimensional equations are unchanged by this continuation.

## Coordinates, scales and rates

The dimensional coordinates are `z=[NTP,nt,A,AT,CP,TLcat]^T`, full indices `[1,3,4,6,8,10]`. Their dimensionless coordinates are `q=[y1,y3,y4,y6,y8,y10]^T`.

$$
z=D_zq,\quad D_z=\operatorname{diag}(c_{NTP,0},n_{NTP}c_{NTP,0},c_{A,0},c_{T,0},c_{CP,0},c_{TLcat,0}),
\quad\tau=k_{nt,deg}t,\quad t_*=1/k_{nt,deg}.
$$

The unchanged `pure_nondim_map(p)` obtains scales and groups from the canonical loader. Its current loaded reduced scale vector is `[1500, 6000, 300, 1.9, 20000, 2.2]` uM; `k_nt_deg=7.92e-05` s^-1, `t_star=12626.262626262625` s, and `V_star=0.4752` uM/s. These are output snapshots, not new parameter defaults. Full order is `[NTP,NXP,nt,A,T,AT,a,CP,C,TLcat,D_nt,D_TLcat]`.

The independent RHS directly evaluates the already audited compact laws:

$$
\widetilde V_{TX}=\mu_{TX}\theta_{DNA}\frac{y_1}{\kappa_{TX,NTP}+y_1},\qquad
\widetilde V_{RS}=\mu_{RS}\frac{y_4}{\kappa_{RS,A}+y_4}\frac{y_5}{\kappa_{RS,T}+y_5}\frac{y_1}{\kappa_{RS,NTP}+y_1},
$$
$$
\widetilde V_{TL}=\mu_{TL}y_{10}\frac{y_3}{\kappa_{TL,nt}+y_3}\frac{y_6}{\kappa_{TL,AT}+y_6}\frac{y_1}{\kappa_{TL,NTP}+y_1},\qquad
\widetilde V_{EN}=\mu_{EN}\frac{y_8}{\kappa_{EN,CP}+y_8}\frac{y_2}{\kappa_{EN,NXP}+y_2}.
$$

Here `theta_DNA=DNA/(K_TX_DNA+DNA)`, `rho_A=n_NTP*c_NTP0/(n_A*c_A0)` and `rho_T=n_NTP*c_NTP0/(n_T*c_T0)` remain independent. The `n_T/n_A` factor appears only in T/AT saturation scaling. Parameter definitions remain those of the [audited derivation](../../models/literature_reference/dimensionless/README.md).

$$
q'=\begin{bmatrix}
-\widetilde V_{TX}-\widetilde V_{RS}-2\widetilde V_{TL}+\widetilde V_{EN}\\
\widetilde V_{TX}-y_3\\-\rho_A\widetilde V_{RS}\\
\rho_T(\widetilde V_{RS}-\widetilde V_{TL})\\-\rho_C\widetilde V_{EN}\\-\mu_{TL,deg}y_{10}
\end{bmatrix}.
$$

Rate order is `[V_TX,V_nt_deg,V_RS,V_TL,V_TL_deg,V_EN]`. All six outputs use `V=V_star*Vtilde`, with `Vtilde_nt_deg=y3` and the required special common-scale expression
`Vtilde_TL_deg=mu_TLdeg*c_TLcat0/(n_NTP*c_NTP0)*y10`. Thus `V_TL_deg=k_TL_deg*c_TLcat0*y10`. Production integration never calls either dimensional RHS; physical dimensional reconstruction is postprocessing only.

## Direct dimensionless reconstruction

Fix these six constants from the loaded initial dimensionless state:

$$
I_{NTP}=y_1+y_2+y_3+y_{11},\quad
I_{AA}=(y_4+y_7)/\rho_A+y_6/\rho_T,\quad I_{tRNA}=y_5+y_6,
$$
$$
I_{CP}=y_8+y_9,\quad I_{TLcat}=y_{10}+y_{12},\quad
I_6=y_2+y_9/\rho_C-3y_7/\rho_A-y_6/\rho_T.
$$

Reconstruct directly in dimensionless variables, in dependency order:

$$
\begin{aligned}
y_5&=I_{tRNA}-y_6,\\
y_7&=\rho_A I_{AA}-y_4-(\rho_A/\rho_T)y_6,\\
y_9&=I_{CP}-y_8,\\
y_2&=I_6-y_9/\rho_C+3y_7/\rho_A+y_6/\rho_T,\\
y_{12}&=I_{TLcat}-y_{10},\\
y_{11}&=I_{NTP}-y_1-y_2-y_3.
\end{aligned}
$$

Initial and full-grid comparisons against scaled dimensional reconstruction pass; the largest scaled discrepancy is below `8.0e-16`. Synthetic in-memory initial pools and multiplicities also pass reconstruction, invariant and derivative software checks; they are not a scientific parameter set.

## Mathematical equivalence and centered reconstruction diagnostic

The old invariant equations above imply, exactly,

$$
NXP=NXP_0+(CP-CP_0)-3n_A(A-A_0)-2n_T(AT-AT_0).
$$

The corresponding centered dimensionless dependent coordinates are

$$
\begin{aligned}
y_2&=y_{2,0}+(y_8-y_{8,0})/\rho_C-3(y_4-y_{4,0})/\rho_A-2(y_6-y_{6,0})/\rho_T,\\
y_5&=y_{5,0}-(y_6-y_{6,0}),\\
y_7&=y_{7,0}-(y_4-y_{4,0})-(\rho_A/\rho_T)(y_6-y_{6,0}),\\
y_9&=y_{9,0}-(y_8-y_{8,0}),\\
y_{12}&=y_{12,0}-(y_{10}-y_{10,0}),\\
y_{11}&=y_{11,0}-(y_1-y_{1,0})-(y_2-y_{2,0})-(y_3-y_{3,0}).
\end{aligned}
$$

MATLAB Symbolic Toolbox independently simplified **all six old-minus-centered expressions to exact zero**, as well as the dimensional NXP identity. Nonzero symbolic initial dependent pools were retained; the proof does not rely on the canonical zero initial pools. [The diagnostic](../../scripts/diagnose_nondim_reconstruction.m) and [actual symbolic/numeric results](../audit/nondimensionalization_validation_v2_20260923/phase1_centered_diagnostic.json) provide the proof and all 51 fixed-sample records.

| DNA (uM) | Old composite derivative | Centered composite derivative | Old NXP discrepancy (uM) | Centered NXP discrepancy (uM) |
| --- | ---: | ---: | ---: | ---: |
| 0.00034 | 1.884367662e-12 | 1.884367662e-12 | 4.530709141e-12 | 4.530709141e-12 |
| 0.0017 | 1.175559650e-12 | 1.175559650e-12 | 2.840283564e-12 | 2.840283564e-12 |
| 0.0068 | 1.287137064e-12 | 1.295796803e-12 | 3.101241486e-12 | 3.122058168e-12 |

The low/middle results are unchanged and high-DNA residuals are slightly larger. Centered reconstruction does not pass the original `1e-12` composite gate. Consequently **centered reconstruction was not adopted in production**; the original invariant form is clearer as a direct use of the six fixed constants and has no worse measured behavior. No further rearrangement or sample selection was attempted to tune the last bits. This diagnostic changed no scientific equation.

## Numerical representation: why validation v2 exists

Before any changes, the original formal v1 runner was executed again: every per-DNA metric exactly reproduced the saved FAIL. The composite derivative residual remains **1.8843676619084704e-12**, above the original **1e-12** threshold. At the same reconstructed full state, the canonical RHS transform residual is **4.263256414560601e-14**. Independent affine reconstructions differ in sampled NXP by at most **4.530709141192801e-12 uM**, and that difference enters the nonlinear EN rate.

V1 was a mathematically legitimate but numerically conflated test: it combined independent conservation reconstruction, nonlinear rate evaluation and coordinate transformation. **V1 was stricter than the intended pure vector-field identity because it combined reconstruction conditioning with RHS equivalence.** Its failure is not reclassified, waived by trajectory agreement, or called solver noise.

V2 was separately preregistered after this diagnosis and before its first formal run. It leaves the legacy composite calculation visible as `diagnostic_only` while independently testing all three scientific/numerical questions below. The original v1 directory remains immutable, including the original FAIL result and criteria hash `443338546a05668967a95c4952ab1f32341280989ab23ed41f53f08d9edf7ced`. Its exact seven tested MATLAB files and original map are additionally preserved in a [historical source archive](../audit/nondimensionalization_validation_v2_20260923/historical_v1_implementation.zip), so modifying the current tests does not erase historical reproducibility.

V2 [criteria](../audit/nondimensionalization_validation_v2_20260923/acceptance_criteria.json) SHA-256: `b0dce1c692e66fb0998fb02d048e5008e4d52668bb175c3f5c25c3b580cc81e2`.

V2 [preregistration](../audit/nondimensionalization_validation_v2_20260923/preregistration.json) SHA-256: `b5fa47231d34d46f4b524d8a7f3bdd83ea38ea8ab23c402824c30ab560cb0f91`. Its timestamp precedes the actual run start; hashes bind all eight tested implementation/test/runner/diagnostic files. No criteria were changed after the run.

## RHS identity — v2 Gate 1

At the fixed 17 uniformly indexed trajectory points per DNA, directly reconstruct dimensionless `y_full` from `q`, then form `x_full=state_scales.*y_full`. Evaluate the canonical dimensional RHS on that **same** `x_full(1:10)`, select indices `[1,3,4,6,8,10]`, and divide by the reduced scales and `k_nt_deg`. This comparison has no second conservation reconstruction.

The maximum absolute residual over all 51 samples is **4.263256414560601e-14**, passing the preregistered **1e-12** threshold. The legacy composite residual remains recorded separately and exceeds its historical v1 threshold.

## Reconstruction equivalence — v2 Gate 2

For each dependent coordinate `j=[2,5,7,9,11,12]` and each fixed sample, compare the direct dimensionless reconstruction with the dimensional reconstruction divided by its scale:

$$
r_j=|y_j-x_j/s_j|,\qquad e_j=r_j/\max(S_j,1).
$$

With $\Delta y_i=y_i-y_{i,0}$, the preregistered absolute-term sums are

$$
\begin{aligned}
S_2&=|y_{2,0}|+|\Delta y_8/\rho_C|+|3\Delta y_4/\rho_A|+|2\Delta y_6/\rho_T|,\\
S_5&=|y_{5,0}|+|\Delta y_6|,\\
S_7&=|y_{7,0}|+|\Delta y_4|+|(\rho_A/\rho_T)\Delta y_6|,\\
S_9&=|y_{9,0}|+|\Delta y_8|,\\
S_{11}&=|y_{11,0}|+|\Delta y_1|+|\Delta y_2|+|\Delta y_3|,\\
S_{12}&=|y_{12,0}|+|\Delta y_{10}|.
\end{aligned}
$$

All 306 comparisons pass: maximum **7.551180140159472e-16**, below **64*eps(double)=1.4210854715202004e-14**. Raw dimensionless discrepancies, term sums, normalized residuals, dimensional discrepancies and sample indices are saved, including raw NXP uM disagreement.

The factor 64 was fixed before v2 execution as a conservative operation-count envelope for two short floating-point evaluation paths; normalization explicitly includes affine term magnitudes and a unit floor. It was not chosen by fitting the observed `4.53e-12 uM` discrepancy. This is a tested representation-equivalence allowance, not a theorem guaranteeing accuracy for arbitrary ill-scaled parameter sets.

## Independent integration equivalence — v2 Gate 3

Each DNA independently runs the canonical full dimensional, exact reduced dimensional and reduced dimensionless `ode15s` solvers from canonical initial conditions. The requested physical grid remains `0:10:14400` s (1441 points). `RelTol=1e-10`; dimensional `AbsTol=1e-12` uM; dimensionless `AbsTol=1e-12./diag(Dz)`. These local solver error controls are distinct from trajectory acceptance.

For each of the 12 states, six physical rates, mRNA and protein, the normalized error is `max(abs(candidate-reference))/max(max(abs(reference)),1e-12)`, with unchanged threshold `1e-6`. The canonical full trajectory is the final reference; dimensional reduced comparisons are also retained.

| DNA (uM) | Points | Same-state RHS | Reconstruction scaled | State error | Rate error | mRNA error | Protein error | Invariant residual | v2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.00034 | 1441 | 4.263256415e-14 | 7.551180140e-16 | 2.057316307e-07 | 1.886225686e-07 | 6.797419831e-12 | 1.741842384e-08 | 1.110223025e-16 | PASS |
| 0.0017 | 1441 | 4.263256415e-14 | 4.733796092e-16 | 2.066033977e-07 | 1.894224232e-07 | 4.267849417e-12 | 3.702352709e-08 | 1.110223025e-16 | PASS |
| 0.0068 | 1441 | 4.263256415e-14 | 5.828670879e-16 | 2.087415071e-07 | 1.913832523e-07 | 3.747605089e-12 | 2.902746069e-08 | 1.110223025e-16 | PASS |

The dimensionless-versus-dimensional-reduced state/rate normalized errors remain below `4.8e-12`. All state/rate/observable outputs are finite. Each DNA has minimum restored state **0**, **zero negative samples**, and six dimensionless invariant residuals at most `1.1102230246251565e-16` (threshold `1e-8`). No clipping, projection or nonnegativity solver option is used. Physicality refers to the requested output grid.

State and time round-trip fixture errors are both zero. The physical output-grid inverse-time maximum discrepancy is `1.8189894035458565e-12` s; scaled residual `1.4379362873880289e-16` passes the unchanged `1e-14` criterion. Direct/scaled dimensional reconstruction also agrees on the full output grid within `8.0e-16` scaled error.

The final [nondim_map.json](../../models/literature_reference/dimensionless/nondim_map.json) is generated from the unchanged runtime builder and canonical loader, passes runtime equality and transform-use tests, and was re-exported byte-identically after all regression tests passed. It states `validation_version=v2`, points to v2 criteria/results, and retains `historical_v1_status=FAIL`. It is derived metadata, not a new parameter authority.

## Actual regression and completion

MATLAB `25.2.0.3177638 (R2025b) Update 5`; formal v2 process exit code **0**. The [results JSON](../audit/nondimensionalization_validation_v2_20260923/validation_results.json) contains actual TestResult counts and all measured metrics.

| Suite | Passed | Failed | Incomplete |
| --- | ---: | ---: | ---: |
| `test_nondimensionalization_validation` | 18 | 0 | 0 |
| `test_exact_conservation_reduction` | 8 | 0 | 0 |
| `test_pure_literature_reference` | 9 | 0 | 0 |
| `test_codegen_and_provenance` | 5 | 0 | 0 |
| `test_dimensionless_trajectory_equivalence` | 12 | 0 | 0 |

Repository-wide `run_all_tests`: **89 passed, 0 failed, 0 incomplete**; every discovered test passed. B1 600 s smoke and development preflight checks passed. Release readiness in that recorded development run remained false while the worktree was dirty; it is not a scientific acceptance gate. All **eight** new/modified MATLAB files have zero `checkcode` messages. The unrelated pre-existing missing-`slanCM` startup-path warning remains unchanged. See [regression results](../audit/nondimensionalization_validation_v2_20260923/regression_results.json).

**D6 = COMPLETE under preregistered v2; historical v1 = FAIL remains intact.** Completion includes stoichiometric rank, complete left nullspace, six exact invariants, six independent coordinates, exact 12-to-6 reduction, dimensional full/reduced trajectory equivalence, audited nondimensional transformation, independent six-state dimensionless integration, inverse/back-transform validation and the machine-readable map. The [history/integrity record](../audit/nondimensionalization_validation_v2_20260923/historical_integrity.json) checks old audit bytes, source fingerprints and protected scientific inputs.

This establishes coordinate-transformation and implementation equivalence for the frozen deterministic B1 model on the tested conditions. It does not establish experimental predictive validity, biological completeness or dominant control groups. No D7 or D10 work was performed.

## D5 control-combination candidates

| Candidate | Formula | Physical meaning | Status |
| --- | --- | --- | --- |
| Pi_TX | `mu_TX*theta_DNA` | Effective transcription capacity relative to nucleotide degradation rate scale | `derived_candidate` |
| Pi_charge | `mu_RS/mu_TL` | Saturation-limit charging capacity relative to translation capacity | `derived_candidate` |
| Pi_life | `mu_TLdeg=k_TL_deg/k_nt_deg` | TLcat decay rate relative to mRNA decay rate | `derived_candidate` |
| Pi_E_cap | `mu_EN/(mu_TX*theta_DNA+mu_RS+2*mu_TL)` | Candidate maximal energy regeneration capacity relative to combined capacity-based demand | `derived_candidate` |

Candidate only: the processes need not reach saturation simultaneously. No D10 sweep, sensitivity ranking, curve collapse, numerical control support or experimental support was performed. D7 was not entered.
