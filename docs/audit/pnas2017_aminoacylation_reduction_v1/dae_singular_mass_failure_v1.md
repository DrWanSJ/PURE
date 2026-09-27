# Singular-mass-matrix DAE realization: failure diagnostics (v1, 2026-09-25)

Status: PRESERVED FAILURE EVIDENCE. The reduced run was first realized as a
singular-mass-matrix index-1 DAE for `ode15s` (R2025b):
`M = I` except `M(elim,elim) = 0` for the 21 registered eliminated complexes,
algebraic rows `0 = dx_i/dt` taken verbatim from the author RHS
(`fMGG_synthesis.m`, unmodified), consistent ICs from the registered damped
projected Newton, handed to the solver via `'InitialSlope'`.

This realization FAILED at the registered tolerances (RelTol 1e-10 /
AbsTol 1e-14). The failure is a numerical implementation limitation of the
DAE route, not evidence against the scientific QSSA closure. Recorded here
before the formulation switch (see `implementation_revision_v1.json`).

## What worked

- Registered Newton consistent start at t0 = 1e-4 s converged from the
  all-zero start for both pools:
  - MetRS: n = 12, max|g| = 8.553e-13 uM/s (1.045e-16 of production scale
    8.183e+03 uM/s), 2 iterations
  - GlyRS: n = 9, max|g| = 6.041e-09 uM/s (4.853e-13 of production scale
    1.245e+04 uM/s), 2 iterations
- Layer jump (recorded, never suppressed): largest adjustment
  MetRS 0.44 -> 0.00354689 uM (0.436 uM); free enzyme reconstructed from
  pool conservation; consistent with the verified t = 1e-4 branch
  (free_enzyme_at_branch 8.6e-5 uM order).
- `'InitialSlope'` acceptance test passed (`yp0_OK`): `daeic12` was never
  invoked, so the known zero-valued-IC finite-difference collapse of
  `daeic12` (spurious "index greater than 1") was bypassed.

## How it failed

`ode15s` rejected the FIRST step repeatedly and aborted with
"step size must be reduced below the minimum allowed" at t = 1e-4 s.

Instrumented measurement (local instrumented solver copy in `scratch/`,
non-formal, git-ignored; printed rejection diagnostics):

- Rejection reason was the ERROR TEST ONLY (`err > rtol`). The corrector
  Newton CONVERGED on every attempt (`tooslow` never triggered).
- The error plateau is STEP-SIZE INDEPENDENT: `err/rtol = 1.672 ... 1.675`
  constant while h shrank through 12 failed attempts from 2.667e-16 s down
  to hmin = 2.168e-19 s (= 16*eps(1e-4)). Shrinking h does not help.
- Worst components at the plateau: state indices 63/64 = `GlyRS_Gly`
  (C = 2.50e-3 uM) and `GlyRS_ATP` (C = 1.23e-3 uM) - both ELIMINATED
  (algebraic) states.
- Explicit `'InitialStep'` overrides 1e-4, 1e-5, 1e-6, 1e-7, 1e-8 all fail
  identically -> not an initial-step-selection artifact.
- Looser tolerances integrate fine with the identical formulation:
  RelTol/AbsTol 1e-8/1e-12 and 1e-6/1e-10 both completed the smoke grid
  (30 points to t = 1 s) from the same consistent start.

## Root cause (quantified)

- The author RHS rows reach |dx_i/dt| up to 3.154e+06 uM/s at the
  consistent point (max over all 241 rows). Each row sum therefore carries
  double-precision cancellation noise of order 1e-9 uM/s
  (measured residual floor of the GlyRS block: 6.04e-9 uM/s at 4.85e-13 of
  its production scale - i.e. already at the noise floor).
- The algebraic error test demands the eliminated states to be resolved to
  rtol*|C_i| ~ 1e-13 uM for the small ones. The implied root jitter
  noise/|J_ii| (small Jacobian diagonals for weakly bound complexes)
  exceeds that bound, producing the observed flat 1.67*rtol plateau that no
  step size can remove.
- R2025b `ode15s` provides no algebraic-state handling (`'MStates'` does
  not exist; verified via `odeset` help lookup), so the algebraic rows
  cannot be excluded from the componentwise error vector.

## Conclusion

The singular-mass DAE realization of the registered closure is numerically
unattainable at RelTol 1e-10 / AbsTol 1e-14 in R2025b. The registered
science (closure rows, partition, thresholds, conditions) is untouched by
this finding. The formulation was replaced by exact per-evaluation
algebraic elimination (`implementation_revision_v1.json`).

## Preserved diagnostic artifacts (scratch/, git-ignored, not committed)

- `scratch/ode15s_dbg.m` - locally instrumented copy of the installed
  solver used ONLY to print rejection reasons (not part of any formal run).
- `scratch/private/` - solver helper shadow for the instrumented copy.
- `scratch/diag_red_tol.m`, `scratch/diag_red_tol{1,2,3}.{json,csv}` -
  tolerance ladder (1e-6/1e-10 OK, 1e-8/1e-12 OK, 1e-10/1e-14 FAIL).
- `scratch/diag_red_h0.m`, `scratch/diag_red_h0_*.{json,csv}` -
  InitialStep sweep (all FAIL identically).
- `scratch/diag_red_dbg.m`, `scratch/diag_red_dbg1.{json,csv}` -
  instrumented run producing the plateau listing quoted above.
- `scratch/smoke_red_config.json`, `scratch/smoke_red_s0.csv*` - original
  singular-mass smoke attempt (1 point at t0, then the hmin abort).
