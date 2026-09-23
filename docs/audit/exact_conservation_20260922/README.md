# Exact conservation reduction: evidence inventory

This audit records the D6 exact-reduction subtask on source commit `91bb36488ad159a8becffc2addfadea99a8adbc4`. The initial worktree was clean. The recorded run verified that all 265 original tracked files were byte-identical at that time. The recorded validation run was performed before the resulting artifacts were subsequently committed.

The first and only trajectory-validation run passed all three required suites: 8/8 exact-reduction tests, 9/9 literature-reference tests, 5/5 codegen/provenance tests. No acceptance threshold or tested MATLAB implementation was changed after that run. A subsequent static-analysis run reported zero `checkcode` messages. Both processes emitted the existing missing-`slanCM` startup-path warning, retained verbatim in stdout.

## Committed implementation and report files

| File | Why it exists |
| --- | --- |
| `matlab/src/theory/pure_exact_conservation_constants.m` | Compute six invariant constants from the existing loaded initial state and multiplicities. |
| `matlab/src/theory/reconstruct_pure_exact_reduced_state.m` | Reconstruct the fixed 12-state order using physically readable affine equations. |
| `matlab/src/theory/rhs_pure_exact_reduced.m` | Reuse the frozen RHS and select the six independent derivatives. |
| `matlab/src/theory/simulate_pure_exact_reduced.m` | Integrate six coordinates with `ode15s`, then reconstruct states, rates and observables. |
| `matlab/tests/test_exact_conservation_reduction.m` | Initial reconstruction, general constants, structural regression, derivative identity, three full trajectories, physicality and invariants. |
| `scripts/run_exact_conservation_validation.m` | Run exactly the three requested suites and print actual TestResult summaries. |
| `docs/theory/conservation_report.md` | Formal D6 deliverable with equations, measured errors, validity limits and remaining work. |

## Added audit files in this directory

| Files | Why they exist |
| --- | --- |
| `README.md` | This complete inventory and reproduction guide. |
| `git_status_before.txt`, `git_log_before.txt` | The requested initial Git status and last five commits. |
| `source_inventory_before.json` | SHA-256 of all 265 original tracked files before implementation. |
| `acceptance_criteria.json` | Thresholds, grid, tolerances and physicality policy fixed before observing errors. |
| `preregistration.json` | Timestamp, criteria hash and hashes of all six MATLAB implementation/test/runner files before first execution. |
| `matlab_stdout.txt`, `matlab_stderr.txt`, `matlab_exitcode.txt` | Actual native process evidence, including all per-quantity comparisons and TestResults. |
| `matlab_stdout.utf8.txt` | Readable UTF-8 conversion of the native Windows stdout; byte-roundtrip checked. |
| `matlab_checkcode_stdout.txt`, `matlab_checkcode_stderr.txt`, `matlab_checkcode_exitcode.txt` | Native static-analysis evidence for the six new MATLAB files. |
| `matlab_checkcode_stdout.utf8.txt` | Readable, byte-roundtrip checked static-analysis stdout. |
| `validation_results.json` | Structured extraction of real stdout: errors/scales for each quantity, minima, derivative and structural checks, suite counts. |
| `integrity_after.json` | Final original-file integrity check and confirmation that criteria/tested MATLAB files did not change. |
| `finalize_evidence.py` | Re-extract results and refuse failed, incomplete or changed-source evidence. |
| `git_status_after.txt` | Final complete Git status listing all new files; no original tracked changes. |
| `artifact_manifest.json` | Current committed audit artifact paths, SHA-256 and sizes, excluding this manifest itself. |

No existing file was modified during the recorded run. Project-graph artifacts were generated in the local working session but were not included in the committed exact-conservation deliverable and are not part of this audit's authoritative artifact set.

## Reproduction

From the repository root in MATLAB, run `addpath('scripts'); run_exact_conservation_validation`. This prints the three real test suites; it does not silently overwrite the recorded evidence. If capturing a new audit, preserve its native stdout/stderr and process exit code separately from this historical run.

The existing native capture used:

```text
matlab.exe -wait -batch "addpath('scripts'); run_exact_conservation_validation;"
```

For this recorded audit, `python docs/audit/exact_conservation_20260922/finalize_evidence.py` verifies and extracts the saved evidence. Its preregistration binds the tested implementation paths on this machine. This historical extractor checks the original source snapshot; it is not a current-worktree regeneration command.

At the time of this recorded exact-reduction run, D6 remained incomplete: dimensional/dimensionless integration, inverse/back-transform comparison and final `nondim_map.json` are still pending. None of these tests establishes independent experimental prediction validity.

The current manifest hashes committed Git file bytes. The audit directory preserves those bytes on checkout; historical captured text is unchanged. Earlier local CRLF hashes in frozen provenance records describe the original local run and are retained as historical evidence.
