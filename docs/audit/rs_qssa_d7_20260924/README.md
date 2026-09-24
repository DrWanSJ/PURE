# D7 RS QSSA validation audit

**D7 = COMPLETE for analytical derivation + synthetic main-backbone numerical validation. This does not establish experimental/microscopic validity of the one-intermediate aaRS surrogate.**

Input commit: `c2bb0ae63ba106d4f51bf2182dfd28dfe187e743`. Preregistration commit: `cec84861ab829bf451d6902283e5f078a6e89401`.
Criteria SHA-256: `61e5970fe51e18eddb72ab3f339d2bc0e81f8f578fa28c6465090d31cca9164d`. MATLAB: 25.2.0.3177638 (R2025b) Update 5.
Source/runtime SHA-256 values describe the dirty implementation actually tested after preregistration;
the final implementation commit is the Git commit containing this audit, not the execution commit.

## Run history

| Run | D7 Passed / Failed / Incomplete | Repository | Overall outcome |
|---|---|---|---|
| run_001 | 13 / 0 / 0 | not reached | INCOMPLETE: TestResult metadata serialization bug |
| run_002 | 13 / 0 / 0 | 102 / 0 / 0 + smoke PASS | PASS |
| final regression | included in repository suite | 102 / 0 / 0 + smoke PASS | PASS |

`implementation_revision_1.json` explains the reporting repair. Original logs and trajectories remain.
No equation, parameter, solver setting, or threshold changed between runs.
All 16 new/modified MATLAB files have zero checkcode messages in run_002.
Development preflight passed every check. `release_ready=false` records a dirty development checkout;
it is not a scientific gate failure, and no release-readiness flag was rewritten.
The pre-existing startup warning about the missing external `slanCM` folder is retained in process logs.

## Fixed-profile results

All errors below use the preregistered per-quantity full-trajectory peak normalization.
Each trajectory contains 1441 points, 0–14400 s at 10 s intervals. Raw errors and scales are in JSON.

| DNA (uM) | all slow states | RS transfer flux | mRNA | protein |
|---:|---:|---:|---:|---:|
| 0.00034 | 1.466684018e-07 | 1.300550188e-07 | 1.435403646e-09 | 2.263311529e-09 |
| 0.0017 | 1.438721542e-07 | 1.276005519e-07 | 2.300382894e-09 | 1.039599157e-09 |
| 0.0068 | 2.631278492e-07 | 1.234351368e-07 | 1.010360415e-08 | 2.137101976e-09 |

Reference V_RS match: 0.000000000e+00.
Reference M_qss match: 2.168404345e-16.
QSS algebraic residual: 2.133874166e-16.
Manifold derivative error: 2.168404345e-19.
Complete chain Jacobian error: 2.220446049e-16.
Full explicit Jacobian error: 3.751355959e-16.
Fast-relaxation concentration error: 2.436655912e-10;
measured tau relative error: 8.295755897e-10.
Maximum epsilon_state: 4.576659039e-06; epsilon_track: 7.279918287e-09.
Maximum normalized invariant residual: 7.389644452e-13.
No negative physical, accounting, or free-enzyme outputs were observed; no clipping or projection.
All six invariants, including original I6 without an M term, passed.

Full explicit NTP/AA inventories include M; reduced coarse invariants do not include reconstructed h.
Both start at the same ten slow concentrations, with full M0 = 0.008 uM, so full totals exceed reduced
coarse totals by M0. Each invariant is checked against its own initial value. This distinction is not hidden.

## Evidence and replay

- `validation_results.json`: current measured results, 13 native TestResult rows, code fingerprints,
  raw/per-quantity errors, invariant residues, physicality minima and full/reduced timescale statistics.
- `run_002/native_TestResults.mat`: native MATLAB objects, alongside CSV and MAT trajectories for all DNA cases.
- `run_001/` and `process_stdout_001.txt`: retained first run and reporting exception.
- `final_regression_results.json` and `final_regression_stdout.txt`: final full-suite replay.
- `independent_csv_check.json`: independent recomputation of reported errors from the exported trajectory bytes.
- `evidence_map.json`: derived EXTRACTED/INFERRED/AMBIGUOUS navigation with fingerprints; never source authority.
- `artifact_manifest.json`: SHA-256 of bound files, excluding itself; verify current or staged bytes with the builder.
- `source_byte_bindings.json`: frozen source working bytes versus input-commit blobs. Three pre-existing
  text checkouts use CRLF while their blobs use LF; the text is identical. Staged verification uses the
  recorded original blob hashes for these sources, without normalizing or editing canonical files.
- `git_status_before.txt`: snapshot before preregistration commit (prereg files were then untracked).
  `git_status_after.txt`: snapshot after validation, before final commit; post-push cleanliness is verified separately.

From repo root in MATLAB:
```matlab
addpath('scripts');
s = run_rs_qssa_validation('RunLabel','run_003','FullSuite',true);
assert(s.all_passed);
```
Choose a fresh run label: existing formal runs are never overwritten.
From the shell: `python scripts/build_rs_qssa_audit.py --verify`; use `--staged` after staging.
The builder also verifies frozen inputs, unchanged D1–D6 text, and exact preregistration bytes.

Microparameters are **synthetic_reduction_only**; Eq.8 supplies a local reference flux, not an identity.
The verified local Mavelli PDF supplies apparent kinetics, not this surrogate's k1/kminus1/k2.
The legacy extracted-text hash entry is stale; current text/PDF fingerprints are explicit in parameter JSON.
Experimental microkinetics, PPi lumping, and biological adequacy for heterogeneous aaRS remain unsupported.
D8 next step: preregister applicability and failure-domain comparisons; no D8 study was run here.
