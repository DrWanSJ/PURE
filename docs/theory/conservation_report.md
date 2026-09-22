# D6 exact conservation reduction: 12 states to 6 coordinates

Validated on 2026-09-22 with MATLAB R2025b Update 5, starting at Git commit `91bb364`. **This subtask passes; D6 is not yet complete.** No parameters were fitted, no states were clipped, and no canonical B1 scientific source or baseline was changed.

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

The runner executes the three required `runtests` calls and displays their real results. [Implementation and evidence map](../project/GRAPH_REPORT.md) provides derived navigation based on the existing flow contract, with source fingerprints and confidence labels; it is not a new scientific authority. The older theory notes retain the structural milestone's historical next-step wording; this report records completion of the exact-reduction subtask.

## Validity and remaining D6 work

No scientific inconsistency was found in the checked canonical structure, reconstruction identities or deterministic trajectory comparisons. This establishes an exact reduced representation of the current frozen B1 deterministic model with numerical implementation agreement on the tested conditions. It does **not** establish independent predictive validity for real experimental systems, extend model mechanisms, or demonstrate a speedup.

**D6 尚未全部完成。** The remaining items are:

- dimensional ↔ dimensionless trajectory integration;
- inverse/back-transform trajectory comparison;
- the final `nondim_map.json`.

No commit or push was performed.
