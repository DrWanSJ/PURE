# R3 selective aminoacylation QSSA pilot interim certificate

Pilot verdict: **`R3_PILOT_REJECTED_BY_FULL_COUPLED_VALIDATION`** from nine
evaluated conditions that fail fixed gates. The tenth adverse reduced solve is
incomplete, so the durable R3 full-grid stage is **not yet complete**.
This is an approximate GlyRS/MetRS pilot. The exact R1 SOURCE_GENERAL chart
and R2 frozen-author execution view retain their separate accepted scope;
neither implies that this QSSA is accurate. The canonical PNAS2017 SBML has
SHA-256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`.
Author kinetics and all fixed acceptance limits are unchanged.

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

All nine evaluated cases have algebraic residuals below `1e-10` but fail state,
aminoacylation rate, cumulative extent, and both measured balance limits.
The exact SOURCE_GENERAL inventory drift is separately recorded in each raw
result and remains below `1e-8` in these cases. Reported reconstructed
concentration minima range in the `-1e-12` uM numerical-noise scale; they
were not clipped and are not treated as a physically validated domain.
The baseline post-0.05 s charged-tRNA errors include MettRNAfMetCAU
`0.04125` and GlytRNAGlyGCC `0.01205`, so its failure persists after the
initial layer.

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
progress record and fixed-tolerance diagnostics. The pilot rejection follows
from the nine completed failures regardless of the adverse numerical outcome.

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

R3 is a selective approximation pilot. No R4 work, blanket Class-II-A QSSA
approval, final reduced PURE model claim, or change to any of the 968
pending human reaction-reduction decisions follows from these results.
