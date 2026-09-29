# R3 coupled 0-1 s smoke diagnostic

Status: **EXPLORATORY COUPLED SMOKE SOLVED; R3 PILOT UNVALIDATED.**
This is the author baseline only, over 0-1 s and 41 report points. The
preregistered comparison remains 0-1000 s for all ten conditions with
protected observables, process fluxes, gross extents, and balances. No
terminal R3 status follows from this smoke run.

The canonical 241-state full system and the selective 193-slow-coordinate
plus 21-algebraic-complex system both solved with SciPy BDF at matched
`rtol=1e-10`, `atol=1e-14`. The reduced RHS uses the exact R1 v4 chart,
six-carrier transform, all 968 original directed rates, source-derived
`G=F_q=0`, and the implicit chain-rule Jacobian. It does not clip states.
The full solve used 3,829 RHS evaluations; the reduced solve used 32,892
RHS evaluations, 1,792 Jacobian evaluations, 6,530 linear solves and
34,684 closure calls. This cost is an implementation concern for the full
ten-case grid.

Attempt 001 stopped the reduced solver when HYBR reported no progress even
though the physical root had fast-row residual `6.30e-13`. The fixed root
predicate now also accepts a physical root only when residual `<=1e-10`,
its analytic Newton correction is `<=1e-10`, and `cond(G_q)<1e12`.
Attempt 002 completed without altering any scientific gate. Its maximum
fast-row residual during the solve was `5.12e-12`, and its largest observed
`cond(G_q)` was about `1170`.

The smoke result fails the registered full-window trajectory target if it
were scored as an acceptance run: all-species `E_inf=1.02125`, Class-I
`E_inf=0.99906`, with a `0.43637` uM maximum initial algebraic-layer jump.
The minimum reduced concentration was `-5.16e-12` uM, reported without
clipping. After `t>=0.05 s`, PPi and PPiase-bound phosphate species still
show errors near `0.30-0.32`; free AMP differs by `0.0330`, and
MettRNAfMetCAU by `0.0401`. These post-layer differences exceed relevant
state budgets and suggest a missing dynamic phosphate-carrier correction,
which must be derived and tested from source chemistry before use.

The exact SOURCE_GENERAL inventory drift in saved reduced states is at
most `6.58e-14` (the full solver's own drift is `1.43e-10`). This supports
the exact carrier accounting, but source-general conservation alone does
not establish QSSA trajectory or resource validity. The PPi/PO4 law in
the old audit is FROZEN_REFERENCE_ONLY and cannot be used for generic
state deletion.

Raw diagnostic results and trajectories are retained under
`results/reduction/r3_coupled_smoke_v1/attempt_001` and `attempt_002`.
The next implementation task is to derive dynamic phosphate/adenylate
carrier coordinates from canonical reactions, then reassess the coupled
trajectory and runtime cost before the full preregistered grid.
