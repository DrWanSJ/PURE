# R3 dynamic adenine/phosphate carrier candidate

Status: **exploratory candidate; full coupled acceptance is untested and the
0–0.1 s diagnostic fails the 0.01 state-error target.** This supplements the
preregistered R3 method; it does not change the ten-case grid or any gate.

The historical `binit_v1r2_matrix.csv` assigns each of the 21 selected bound
states an adenosine count `a_j` in `{0,1}` and a phosphate equivalent count
`p_j` in `{0,1,3}`. We independently multiply those rows by the canonical
stoichiometric columns for all 103 reactions touching the selected states;
both products are identically zero. These rows are **resource accounting for
the aminoacylation subsystem**, not SOURCE_GENERAL conservation laws. They
have global reaction violations. The full 968-reaction source RHS remains the
derivative of every slow coordinate.

In addition to the exact six-carrier chart, define two dynamic coordinates

```text
z_A = ATP + AMP + a·q
k   = (p - 3a)/2
z_P = PPi - AMP + k·q
ATP = z_A - AMP - a·q
PPi = z_P + AMP - k·q
```

`AMP` remains a physical slow coordinate; free `GlyAMP` and `MetAMP` remain
dynamic. `z_A` and `z_P` are integrated with derivatives from all source
reactions, including translation and energy regeneration. This retains the
ATP→AMP+PPi transient during the initial layer without asserting the
FROZEN_REFERENCE_ONLY PPi/PO4 invariant. At the author initial state, the
physical closure gives ATP `3749.269367732283`, AMP `0`, PPi
`0.0980469571353564` uM and a fast residual `4.069988790433854e-11`.
Initial reconstruction is exact, the 27 source-general inventories shift by
at most `1.67e-16`, and the analytic implicit Jacobian passes a finite
direction check. A wrong PPi-sign mutant breaks `T·D=0`.

The retained matched-tolerance 0–0.1 s author-baseline diagnostic is
`results/reduction/r3_resource_total_smoke_v1/attempt_001/`. Both BDF solves
completed (`rtol=1e-10`, `atol=1e-14`): full 3184 RHS calls and reduced 6980
RHS calls. The closure had 7207 calls and maximum residual `4.07e-11`.
Reduced minimum concentration was `-2.17e-12` uM without clipping; maximum
source-general inventory drift was `2.83e-14` uM-equivalent (full `1.05e-10`).
The full-window all-species E_inf was `1.02124`, including the initial layer.
Over reported times `0.05–0.1 s`, PPi E_inf was `0.04622`, PO4 `0.04679`,
AMP `0.02915`, and MettRNAfMetCAU `0.08561`. The prior six-carrier smoke
showed PPi `0.31747` and MettRNAfMetCAU `0.09996` over its nearby saved
`0.05–0.1 s` samples; the grids differ, so this is diagnostic only.

The dynamic coordinates remove much of the PPi mismatch but do not establish
R3 validity. Timescale, all ten full 0–1000 s grid cases, directed extents,
process scores, and a terminal status remain outstanding.

## Closure implementation diagnostic

`r3_resource_total_runtime_v2.py` applies a physical, residual-checked
warm-start Newton solve and falls back to the unchanged HYBR implementation
when it cannot satisfy the same root predicate. It changes no coordinate,
kinetic law, solver tolerance, or acceptance gate. On 21 saved v1 trajectory
states, its roots matched HYBR to within `5.29e-14` uM; a negative ATP
coordinate triggered fallback and was rejected. The repeated 0–0.1 s run in
`attempt_002` solved with 6954 closure calls, all using the Newton path;
the largest residual was `9.857e-11`. Reduced RHS calls fell from 6980 to
6758. Saved reduced trajectories differ from attempt 001 by at most
`2.11e-9` uM, and post-0.05 s Met charged-tRNA E_inf remains `0.08561`.
The diagnostic still fails the state gate.
