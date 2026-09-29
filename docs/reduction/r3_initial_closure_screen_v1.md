# R3 initial algebraic-root screen

Status: **EXPLORATORY SCREEN ONLY; NO R3 FULL-COUPLED VERDICT.**
The registered ten-case grid and method are unchanged from commit `adda07b`.
This screen evaluates the candidate 21-complex fast balance at the initial
physical inventories of each condition. It does not integrate a QSSA model
or measure the required slow timescale, trajectories, process fluxes,
resource extents, or balances over 0-1000 s.

`scripts/r3_candidate_runtime_v1.py` uses the R1 v4 SOURCE_GENERAL chart
for all 241 physical species. The 21 selected bound complexes are algebraic
candidate variables `q`; six exact carrier transforms and 187 other
retained coordinates make 193 slow coordinates `z`. The runtime evaluates
the 968 canonical directed rates. Its fast residual is the 21 author-source
stoichiometric RHS rows, `G(z,q)=S_q v(x(z,q))`; its analytic `G_q` includes
the carrier reconstruction. The slow carrier derivative is exactly
`F_carrier-C F_q`. No directed reaction, gross extent, or free GlyAMP/MetAMP
is removed. Four semantic tests pass, including a directional finite
difference Jacobian check and a wrong-sign carrier-Jacobian mutant.

The first screen attempt remains in `attempt_001`: SciPy HYBR reported
success at the adverse initial condition with raw fast residual
`4.1484815582748524e-10`, above the fixed `1e-10` closure gate. A single
analytic-Jacobian Newton correction reduced it to
`2.2737367544323206e-12` without changing any source or gate. The runtime
now applies at most three fixed, residual-decreasing Newton corrections
after HYBR. Attempts 002 and 003 retain that refinement; attempt 003 pins
runtime/screen script, method, chart and grid hashes.

In attempt 003, two feasible starts per case converged to the same local
root in all ten cases. All roots were nonnegative to the declared numerical
root tolerance; all 21 fast modes had negative real parts at `t=0`.
Maximum initial fast-row residual was `2.1714186004828662e-11`, and
maximum SOURCE_GENERAL inventory shift was `5.603156827405087e-16`.
The local slowest fast-mode relaxation estimate ranged from
`0.002880367825789628` to `0.005924641162106166` seconds. These are
initial-point results, not a trajectory-wide `epsilon` screen or evidence
of QSSA accuracy. The adverse condition remains in the grid and may fail
the full coupled comparison.

Evidence: `results/reduction/r3_closure_grid_screen_v1/attempt_003/screen.csv`
and `result.json`, with prior attempts preserved beside them.
