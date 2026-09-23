# Reduced nondimensionalization validation v2 — preregistered PATH B

The original v1 audit is immutable and remains FAIL. An unchanged formal rerun reproduced every per-DNA metric exactly before any implementation changes. MATLAB Symbolic Toolbox then proved all six centered reconstruction formulas and the dimensional NXP formula equivalent, but the fixed 51-point numerical diagnostic did not pass the original composite gate. The unchanged invariant-form production reconstruction is retained.

V2 separates three questions: same-full-state RHS identity (`1e-12`), reconstruction equivalence normalized by centered affine absolute-term sums (`64*eps(double)`), and independent full/reduced/dimensionless trajectory equivalence (`1e-6`). Six invariants retain `1e-8`; DNA, grids, solver tolerances, round trips, physicality and no-clipping rules are unchanged. The legacy composite derivative is still computed and recorded, with role `diagnostic_only`. This version does not turn the v1 result into PASS.

The 64-epsilon envelope was specified before the first v2 numerical run. It reflects a small number of basic operations in two evaluation paths and uses term magnitudes to account for cancellation; it was not fitted to the measured raw NXP discrepancy. It is an acceptance bound for these tested transforms, not a universal conditioning theorem for arbitrary scales.

`acceptance_criteria.json` and `preregistration.json` were written and hashed before the formal v2 run. Source fingerprints bind the tested code. The original criteria, failed results and implementation revision remain in `../nondimensionalization_validation_20260923/` without edits.

Reproduce from the repository root:

```matlab
addpath('scripts');
run_nondimensionalization_validation;
run_all_tests;
```

The v2 runner checks registered hashes, prints actual TestResults, writes measured JSON, and errors on failed/incomplete tests. Existing results are never overwritten: default reruns write to a fresh temporary directory. `diagnose_nondim_reconstruction` independently reproduces the symbolic proof and fixed-sample comparison; it does not modify production code.

Artifacts:

- `continuation_record.json`: incoming worktree/source fingerprints, exact v1 reproduction check, and the PATH B decision.
- `historical_v1_implementation.zip`: exact seven original v1 MATLAB source files and original mapping certificate. The archive preserves the otherwise uncommitted v1 implementation for historical reproduction; its SHA-256 is in the continuation record. To reproduce v1, overlay this archive and the unchanged v1 audit onto an isolated copy of the recorded source commit; do not overwrite the current v2 workspace.
- `phase1_centered_diagnostic.json`: actual symbolic zeros and all 51 old/centered/dimensional-scaled full-state records, dependent-state differences and residuals.
- `acceptance_criteria.json`, `preregistration.json`: immutable v2 design and pre-run source binding.
- `validation_results.json`: actual formal TestResults and per-sample/per-DNA metrics, generated after execution.
- `regression_results.json`: repository-wide runner outcome, generated after execution.
- `historical_integrity.json`: final byte-integrity checks, generated at closeout.

Scientific authority remains the canonical B1 sources. This validation does not establish experimental predictive validity or enter D7/D10.

## Final executed outcome

**V2 PASS; D6 COMPLETE under v2. V1 remains historical FAIL.** The formal v2 runner exited 0: 52/52 tests across the five required suites passed, zero failed or incomplete. Repository-wide `run_all_tests` passed all 89 discovered tests; smoke and development checks passed. All eight registered MATLAB files have zero analyzer messages. Same-state RHS maximum is `4.263256414560601e-14`; reconstruction condition-scaled maximum is `7.551180140159472e-16`. All trajectory, invariant, round-trip and physicality criteria pass, with zero negative output samples. The legacy composite residual remains `1.8843676619084704e-12`, explicitly diagnostic-only in v2.

The current map was re-exported after all tests passed and was byte-identical to the tested map. Statements in the immutable v1 README about withholding completion/commit describe that failed historical run; this v2 audit records the subsequent authorized completion. Full equations, measured tables and scope are in the [report](../../theory/nondimensionalization_report.md).
