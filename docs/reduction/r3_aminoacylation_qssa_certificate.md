# R3 selective aminoacylation QSSA pilot: bounded closeout certificate

**R3 FULL-GRID PROTOCOL: INCOMPLETE BY HUMAN-AUTHORIZED COMPUTATIONAL STOP.**
The original protocol required ten complete coupled comparisons for a terminal
R3 classification. The human decision to stop the adverse numerical campaign
ends computation; it does not supply the missing comparison.

**CURRENT CANDIDATE RESULT: REJECTED ON ALL NINE COMPLETED FULL-COUPLED TEST
CONDITIONS.** Each of those measured conditions fails unchanged coupled gates.
**R3_ADVERSE: NUMERICALLY NONCOMPLETED UNDER THE REGISTERED SOLVER/TOLERANCE
PROTOCOL.** Its full-source trajectory exists, but its reduced trajectory and
directed ledgers do not. The historical `run_001/summary.json` field
`pilot_status=R3_PILOT_REJECTED_BY_FULL_COUPLED_VALIDATION` is a nine-case
aggregate rejection, not certification that the preregistered ten-case
terminal protocol finished. No adverse acceptance or failure score is inferred.

This is an approximate GlyRS/MetRS pilot. The exact R1 SOURCE_GENERAL chart
and R2 frozen-author execution view retain their separate accepted scope;
neither implies that this QSSA is accurate. The canonical PNAS2017 SBML has
SHA-256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`.
Author kinetics and all fixed acceptance limits are unchanged.

## Source authority and branch lineage

The original author parameter CSV has SHA-256
`cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465`;
the original initial-value CSV has SHA-256
`a1b6f832303303c888999968d4652b00205e6adba478b11ceab9cbff4d1c41ec`.
The registered grid, method, coupled protocol, source-reaction map, and v2
runtime hashes are fixed in every selected condition `result.json` and in
`run_001/summary.json`; the grid hash is
`6ce3c7197dff37666ff54191db08b7cfd989e8815ea055fa558cc33657900e4a`.
These raw hashes, not this prose, bind the measurements to the model and
protocol.

R3 is on `research/aminoacylation-qssa-pilot-v0`, stacked on verified exact
R1/R2 commit `b678a7c951967ecdab1c89e549011bf050307ff9` in open PR #3.
At closeout recovery, `origin/main` was
`3b0e0f9c482129fa40c2c442388866e2dc3a1e00`. R3 history starts with
preregistration `adda07b`, develops the physical carrier chart and dynamic
resource totals in `1533635` and `dccde0c`, records completed coupled
conditions through `e8df10e`, and seals the nine-fail/one-incomplete aggregate
in `d068140`. Commits `3bb7213` through `116a513` preserve bounded adverse
solver diagnostics. The complete, unrevised R3 history is the Git range
`b678a7c951967ecdab1c89e549011bf050307ff9..research/aminoacylation-qssa-pilot-v0`;
the closeout commits extend that range without rewriting it.

## Derivation and representation

The 241-species, 968-directed-reaction source has a rank-214 SOURCE_GENERAL
chart with 27 exact conservation laws. The R3 candidate retains 193 slow
coordinates and solves 21 selected GlyRS/MetRS enzyme-bound fast equations
`G(z,q)=S_q v(x(z,q))=0` on a physical branch. Free `GlyAMP` and `MetAMP`
remain dynamic. Six exact carrier coordinates reconstruct enzyme and tRNA
moieties. Additional dynamic adenine/phosphate coordinates account for
bound-state ATP/AMP/PPi content without using the R2 frozen-only phosphate
law. The slow RHS is derived from all 968 canonical directed rates, and its
Jacobian differentiates the physical closure via
`dq/dz = -G_q^{-1} G_z`. Source-general inventories are recomputed for each
registered initial condition. No concentration is clipped and no parameter
is fitted.

The standard concentration-coordinate candidate was evaluated separately.
Its diagnostic closures can have small fast residuals while shifting exact
carrier inventories; the full coupled validation uses the same-inventory
total-coordinate candidate. Initial-point multistart screening found a
common local physical root from two feasible starts in all ten conditions,
with maximum corrected fast residual `2.17142e-11`; this is a local screen,
not proof of global uniqueness or coupled accuracy. The standard-candidate
diagnostics, total-coordinate derivation, and failed short smokes remain in
`docs/reduction/r3_initial_closure_screen_v1.md`,
`docs/reduction/r3_resource_total_candidate_v1.md`, and their recorded runs.

`docs/reduction/r3_source_reaction_candidate_map_v1.csv` maps every one of the
968 source reactions to evaluation at the reconstructed state. Of these,
103 touch the 21 fast states and contribute to both fast and slow balances;
865 keep the slow source-reaction role. Every original directed gross rate
and extent remains a separate channel, including reverse partners. The
map's preregistered `CANDIDATE_PENDING_FULL_COUPLED_VALIDATION` label is a
pre-run classification; the terminal pilot outcome below governs scientific
use of this candidate.

## Registered coupled validation

The ten-case grid in `docs/reduction/r3_validation_grid_v1.csv` was fixed
before decisive comparison. Nine full 241-state and reconstructed QSSA models
were solved in the complete translation/resource network over 0–1000 s at
the same 201 report points and BDF tolerances `rtol=1e-10`, `atol=1e-14`.
For those nine, all 968 directed gross extents were separately integrated as
ODE states against dense trajectories with segmented DOP853 at the same
tolerances. The adverse full-source trajectory completed; its reduced solve
did not.
The full-window score includes the initial layer; per-observable CSV tables
also retain post-0.05 s diagnostics. The five fixed limits are closure
`1e-10`, balance `1e-8`, state `0.01`, process rate `0.05`, and cumulative
extent `0.01`. `epsilon<=0.01` is a timescale screen only.

| Condition | All-state E_inf | Class-I E_inf | Aminoacylation rate E_inf | Aminoacylation extent E_inf | Full / reduced balance, max abs | Closure max abs | Epsilon screen failures / 201 | Coupled gate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| R3_BASE | 1.02130 | 0.999055 | 1.02130 | 0.0769243 | 7.43030e-7 / 2.44358e-6 | 9.99995e-11 | 94 | FAIL |
| R3_GLYRS_LOW | 1.02051 | 0.999127 | 1.02051 | 0.0769549 | 6.65748e-7 / 6.80707e-6 | 9.99911e-11 | 92 | FAIL |
| R3_GLYRS_HIGH | 1.03280 | 0.997131 | 1.03280 | 0.502411 | 6.47542e-7 / 2.80258e-6 | 9.99778e-11 | 113 | FAIL |
| R3_METRS_LOW | 1.02130 | 0.999055 | 1.02130 | 0.0518071 | 5.68689e-7 / 3.49760e-6 | 9.99592e-11 | 92 | FAIL |
| R3_METRS_HIGH | 1.02130 | 0.999054 | 1.02130 | 0.393154 | 6.62885e-7 / 2.27085e-6 | 9.99303e-11 | 94 | FAIL |
| R3_GLY_LOW | 1.04549 | 0.994841 | 1.04769 | 0.0769294 | 6.68764e-7 / 1.87655e-6 | 9.99312e-11 | 98 | FAIL |
| R3_MET_LOW | 1.02130 | 0.999055 | 1.02130 | 0.0517968 | 6.03155e-7 / 3.04873e-6 | 9.99734e-11 | 99 | FAIL |
| R3_TRNA_LOW | 1.18878 | 0.993176 | 1.18951 | 0.302253 | 6.55513e-7 / 5.14553e-6 | 9.99418e-11 | 109 | FAIL |
| R3_ATP_LOW | 1.01967 | 0.996671 | 1.01979 | 0.0653771 | 6.29139e-7 / 1.19325e-5 | 9.99876e-11 | 95 | FAIL |
| R3_ADVERSE | N/A | N/A | N/A | N/A | N/A | N/A | 108 | INCOMPLETE |

The aminoacylation extent column is also the maximum error across all 968
directed cumulative extents for each of the nine evaluated conditions; the
raw `validation_grid.csv` retains both fields. Likewise, its all-directed
rate maxima equal the listed aminoacylation rate maxima. These are measured
maxima, not a replacement of directed gross channels by a net reaction.

| Completed condition | SOURCE_GENERAL inventory drift, max abs | Full minimum concentration (uM) | Reduced reconstructed minimum (uM) |
| --- | ---: | ---: | ---: |
| R3_BASE | 1.81899e-12 | 0 | -1.73225e-12 |
| R3_GLYRS_LOW | 1.36424e-12 | 0 | -4.53422e-12 |
| R3_GLYRS_HIGH | 1.36424e-12 | 0 | -2.90203e-12 |
| R3_METRS_LOW | 1.36424e-12 | 0 | -6.90238e-12 |
| R3_METRS_HIGH | 1.36424e-12 | 0 | -2.01210e-12 |
| R3_GLY_LOW | 1.81899e-12 | 0 | -6.78238e-12 |
| R3_MET_LOW | 1.36424e-12 | 0 | -1.84297e-12 |
| R3_TRNA_LOW | 1.36424e-12 | 0 | -2.07851e-12 |
| R3_ATP_LOW | 1.36424e-12 | 0 | -3.24642e-12 |

All nine evaluated cases have algebraic residuals below `1e-10` but fail state,
aminoacylation rate, cumulative extent, and both measured balance limits.
**Balance attribution:** the full detailed reference's material-balance
residual `x_full-x0-S ξ_full` is `5.68689e-7` to `7.43030e-7`, already above
the fixed `1e-8` diagnostic limit. The reduced slow-system residual
`z_reduced-z0-T S ξ_reduced` is separately
`1.87655e-6` to `1.19325e-5`, also above it. The balance gate therefore
fails for both numerical/accounting trajectories; it cannot be attributed
solely to QSSA. The full-versus-reduced state, process-rate, and directed
extent discrepancies independently reject the candidate in all completed
conditions. Exact SOURCE_GENERAL inventory drift remains below `1e-8`.
The tiny negative reconstructed minima were retained without clipping;
they are numerical feasibility diagnostics, not proof of a validated physical
domain.

**Initial-layer distinction:** in all nine completed cases the largest
whole-window state error occurs at `t=0`, so the initial layer contributes to
the preregistered `E_inf` failure. After `0.05 s`, the maximum state errors
still range from `0.0371711` to `0.141077`, aminoacylation rate errors from
`0.310604` to `0.646047`, and directed extent errors from `0.0470915` to
`0.454657`; every range remains above its respective gate. The baseline
post-layer charged-tRNA errors include MettRNAfMetCAU `0.04125` and
GlytRNAGlyGCC `0.01205`. These post-layer diagnostics explain the failure;
they do not replace the frozen whole-window metric.

The independent full-source trajectory screens found 21 locally attracting
fast modes at every sampled point in all ten conditions, but `epsilon` failed
its `0.01` screen at 92–113 of 201 samples per condition. The largest finite
epsilon across the screens was `597.989`; GlyRS and MetRS occupied fractions
approached `0.999963` and `0.999974`. These observations describe the
tested dynamics and do not rescue the failed coupled gates.

## Domain and evidence boundary

The tested grid spans baseline; 0.1x and 10x GlyRS/MetRS totals; 0.1x Gly,
Met, ATP, and both charging tRNAs; and a preregistered adverse condition
with 20x both synthetases, 0.02x ATP, and 0.02x both tRNAs. The nine evaluated
cases show no accepted full-window QSSA domain. A successful local closure
is therefore insufficient to replace this source mechanism in those cases.
The adverse full-source trajectory and timescale screen completed, but its
reduced BDF solve did not reach 1000 s at the registered tolerances. A
read-only progress probe recorded five samples from 362.236238 to
362.237423 s over 8.54 wall seconds, with 16,506.875 process CPU seconds
at the last sample. The process was externally stopped after 16,521.78125
CPU seconds. Its OS exit code was not captured, and it is **not** represented
as a runner exit-1 solver exception. No adverse reduced trajectory, directed
extent, balance, or error score is claimed. This is a numerical noncompletion
region, not a validated approximation domain; see
`docs/reduction/r3_adverse_numerical_noncompletion_v1.md` for the preserved
progress record and fixed-tolerance diagnostics. The rejection of this
candidate on the completed domain follows from those nine failures
regardless of the adverse numerical outcome.

An independently hash-bound BDF restart from a saved reduced state near
`t=359.059 s` made only `0.000676487 s` of model-time progress in 200 accepted
steps: 1,337 RHS calls and 564 internal trial solves. Of those trials, 364
failed the implicit Newton convergence test, while zero converged trials were
rejected by the local error estimate. Accepted steps were roughly
`1.26e-7` to `1.14e-5 s`. A fixed physical closure seed gave comparable
progress, and 50-digit reconstruction/rate products did not resolve the
slowdown. These are local numerical diagnostics, not a completed adverse
comparison or evidence that the algebraic root itself is invalid. Looser
tolerances used in an exploratory probe are diagnostic only and cannot satisfy
the registered fixed-tolerance protocol.

At bounded closeout recovery, no process running the old R3 adverse grid or
its task-specific diagnostics remained, and the scheduled auto-resume worker
was absent. No process was terminated during this closeout. This terminal
disposition is **`USER_AUTHORIZED_BOUNDED_CLOSEOUT`**. The older sealed
external-stop attempt retains its `null` OS exit code and its original
termination record; the present human stop decision does not rewrite that
historical event. The adverse condition remains scientifically unscored.

For the nine evaluated cases, raw 201x241 full/reduced trajectories,
201x968 directed rates/extents,
241-species and 968-rate/extent error tables, timescale screens, per-condition
exit-code manifests for evaluated conditions, an explicit null external-stop
code for the adverse condition, and source/protocol/output hashes are retained under
`results/reduction/r3_aminoacylation_qssa/`. The first four selected runs
are in `run_001`; six interrupted first attempts are retained there, and
their fresh selected attempts are in `restart_001`. The hash-bound
`run_001/attempt_map.json` names each selected attempt; the execution
environment document records the exact restart and screen reuse. The
`run_001/validation_grid.csv`, `summary.json`, and
`pilot_manifest.json` are the machine-readable rejection evidence. They
distinguish nine `GRID_CONDITION_EVALUATED` failures from one
`GRID_CONDITION_INCOMPLETE` adverse attempt and list zero validated conditions.
They explicitly mark the full validation grid and durable R3 stage incomplete.
The separate read-only `scripts/verify_r3_bounded_closeout_v1.py` checks the
nine selected measured attempts, missing adverse outputs, aggregate/source
hashes, and bounded adverse trace. It reports
`HASH_VERIFIED_BOUNDED_R3_CLOSEOUT` with `original_full_grid_protocol=INCOMPLETE`;
it is not the preregistered ten-condition acceptance finalizer.

## Theory-facing conclusion and bounded questions

R1 removed **exact state redundancy**: its SOURCE_GENERAL 241-to-214 chart
reconstructs the source model and retains directed gross ledgers. R2 uses
**frozen-author-condition simplifications**: the 485 author-zero directions
can be excluded from that execution view, but the 37 additional
`FROZEN_REFERENCE_ONLY` laws are not generic conservation and no canonical
reaction is deleted. R3 tests **approximate dynamical elimination** of 21
selected enzyme-bound coordinates. Its small local closure residuals coexist
with large coupled state, process-rate, and extent errors on nine completed
conditions. Thus `G(z,q)≈0` alone does not guarantee reproduced coupled
trajectories.

For `z_dot = F(z,q)`, `q_dot = G(z,q)` and a candidate root
`G(z,h0(z)) = 0`, the moving root requires the eliminated coordinates to
change at `Dh0(z) F(z,h0(z))`. The local root residual does not measure this
motion. Future theory should examine the manifold's invariance defect under
the coupled slow flow, and whether a slow-manifold correction explains the
observed failure. Concrete questions are which eliminated coordinates drive
the trajectory error, which resource/tRNA/enzyme totals must remain dynamic,
and what smallest retained state set can answer GFP/resource-control
questions. This closeout launches no new candidate or R4 work.

## Review boundary

The nine completed comparisons reject this **tested formulation** over their
measured domain. The adverse condition is a numerical noncompletion, and
the original ten-condition terminal protocol remains incomplete by human
decision. These findings do not prove all aminoacylation QSSA impossible,
mandate that all 21 candidate states remain dynamic, or establish a general
no-QSSA theorem. The 968 reaction-reduction decisions remain `PENDING` and
`HUMAN_REVIEW_REQUIRED`; any later candidate mechanism, target domain, or
reduced-model promotion requires its own scientific review. R1/R2 PR #3 and
the separate R3 closeout remain unmerged pending review. No main merge or
R4 work is part of this closeout.
