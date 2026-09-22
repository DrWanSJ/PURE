# D6 dimensional/dimensionless trajectory audit

**Final status: PASS; D6 complete (2026-09-23, Asia/Shanghai).** Source commit: `0b6fd01287fad6ee323ce4f9ed27e9605701ff6a`. MATLAB: 25.2.0.3177638 (R2025b) Update 5. This audit reuses the frozen B1 model and the previously audited compact dimensionless definitions; it adds their independent numerical runtime and inverse-transform certificate.

## Preregistration and evidence

- [Acceptance criteria](acceptance_criteria.json): SHA-256 `f8c67a0a16e5f1917620a70aabfcb049e2cc2fb2465d463afae66776a06ac8bb`.
- [Original preregistration](preregistration.json): `2026-09-22T16:25:45.904732+00:00`, before the first trajectory run.
- [Initial source inventory](integrity_before.json): all 291 original tracked files, initial clean Git status and five-entry Git log, locally and remotely verified starting commit.
- [Final results](validation_results.json): raw and normalized errors for every state/rate/observable, six-invariant residuals, raw minima and negative counts, real suite counts and prior-attempt provenance.
- [Native stdout](matlab_stdout.txt), [byte-roundtrip-checked UTF-8 copy](matlab_stdout.utf8.txt), [stderr](matlab_stderr.txt), [exit code](matlab_exitcode.txt). Final native exit code is 0; stderr is empty.
- [Final integrity](integrity_after.json): only the four requested status/report documents differ among original tracked files. Canonical scientific source, baseline snapshots, reference simulator, audited definitions and symbolic generated text match original bytes.
- [Artifact manifest](artifact_manifest.json) binds the audit, runtime, tests, reports and [mapping certificate](../../theory/nondim_map.json) to their SHA-256 fingerprints.

## Independent runtime and comparison

`pure_nondim_map` loads scales/groups from the existing parameter struct. `rhs_pure_literature_dimensionless` implements the audited compact equations directly. `simulate_pure_literature_dimensionless` integrates that RHS in tau and inverse-transforms its states. Canonical dimensional RHS calls occur only in postprocessing/reference checks. The analytic compact Jacobian is supplied to `ode15s` and independently tested with complex-step differentiation.

Both integrations use RelTol 1e-10 and scalar AbsTol 1e-12, 0–14400 s and 10 s physical output spacing. All 1,441 points per DNA condition are compared; tau is computed as k_nt_deg times the physical grid. Normalization is the maximum absolute reference value per quantity, with floor 1e-12. Every trajectory-category threshold is 1e-6. All 12 states, 6 rates, mRNA and protein pass. The compact rates restored with Vstar also pass against both same-state canonical rates and dimensional reference trajectories.

Maximum normalized trajectory errors:

| DNA (uM) | States | Rates | mRNA | Protein |
| --- | ---: | ---: | ---: | ---: |
| 0.00034 | 7.637046621e-09 | 7.169911960e-09 | 3.898811970e-12 | 3.617618922e-09 |
| 0.0017 | 7.635974295e-09 | 7.168981293e-09 | 2.826440631e-12 | 1.903857669e-09 |
| 0.0068 | 7.634174568e-09 | 7.167419490e-09 | 2.564091919e-12 | 1.245381820e-09 |

Raw maximum errors:

| DNA (uM) | States (uM) | Rates (uM/s) | mRNA (uM) | Protein (uM) |
| --- | ---: | ---: | ---: | ---: |
| 0.00034 | 3.799295030e-07 | 4.834169398e-09 | 4.731492975e-13 | 5.263924296e-10 |
| 0.0017 | 5.357505870e-07 | 4.834156409e-09 | 1.363686941e-12 | 7.447982786e-10 |
| 0.0068 | 5.274305295e-07 | 4.834134981e-09 | 2.796651799e-12 | 7.331726337e-10 |

| Invariant | Maximum absolute residual across all three trajectories (uM) |
| --- | ---: |
| B_NTP | 1.728039933e-11 |
| B_AA | 1.091393642e-11 |
| B_tRNA | 1.563194019e-13 |
| B_CP | 7.275957614e-11 |
| B_TLcat | 3.996802889e-15 |
| I6 | 1.051603249e-12 |

Mapping roundtrips and canonical initial state pass. Pointwise RHS maximum absolute residual is 2.8421709430404007e-14 at 51 feasible states; threshold remains 1e-12. All output values are finite; every state has zero negative samples. Minimum state value is exactly zero. Detailed minima and per-condition invariant residuals are in the JSON.

## Recorded attempts and solver correction

1. [Initial attempt](initial_attempt_stdout.txt): all trajectory comparisons passed, but the I6 invariant check failed at 4.3267576188554813e-8 uM versus the registered 1e-8 threshold. Native exit code 1; all failure output is preserved.
2. [Solver revision](implementation_revision.json), recorded before rerunning: provide the analytic Jacobian of the unchanged compact RHS to ode15s. The map, compact RHS, parameters, RelTol, AbsTol, grid and acceptance criteria were unchanged. [Solver attempt](solver_attempt_stdout.txt) passed 34/34 tests and the frozen symbolic equations, then exited 1 because generated symbolic text changed only CRLF to LF. Original bytes were restored after content identity was verified.
3. [Runner revision](implementation_revision_2.json): verify complete normalized generated text and restore original bytes automatically. [Analyzer-only attempt](runner_preflight_stdout.txt) stopped before tests on a newline-style diagnostic; no trajectory was run in this attempt.
4. [Runner revision 3](implementation_revision_3.json): use MATLAB `newline` directly. Native execution passes all suites, all symbolic checks and byte restoration.
5. [Final evidence revision](implementation_revision_4.json): write the UTF-8 viewing copy as encoded bytes to avoid a second Windows newline conversion. Native evidence and numerical runtime were unaffected. The runner binds the corrected utility hash, and the final native execution again passes. The criterion hash is identical in every revision. The original preregistration and prior revisions were never overwritten.

The final I6 drift is at most 1.0516032489249483e-12 uM. Analytic Jacobian vs complex-step maximum scaled discrepancy is 2.2178787638976362e-15; sampled I6 derivative is at most 9.0039975475519896e-18 uM/s. No clipping, state projection, scaling change, parameter fitting or relaxed threshold was used.

## Actual regression results

| MATLAB suite | Passed | Failed | Incomplete |
| --- | ---: | ---: | ---: |
| `test_dimensionless_trajectory_equivalence` | 12 | 0 | 0 |
| `test_exact_conservation_reduction` | 8 | 0 | 0 |
| `test_pure_literature_reference` | 9 | 0 | 0 |
| `test_codegen_and_provenance` | 5 | 0 | 0 |

`allPassed = 1`. The frozen symbolic script proves 12/12 equations and both sets of 5 published balances in this run. Generated symbolic output is byte-identical after restoring CRLF serialization; its semantic text was identical before restoration. All six new MATLAB files have zero analyzer messages. The existing missing `slanCM` search-path warning is retained in stdout and did not affect the tests.

## Reproduce

From the repository root in MATLAB:

```matlab
addpath('scripts');
summary = run_nondim_trajectory_validation();
```

The runner checks registered source/criteria hashes, displays real TestResult tables, runs the unchanged symbolic audit, and writes a provisional certificate. For a new auditable run, retain its native stdout, stderr and exit code, then bind them with:

```text
python docs/audit/nondim_trajectory_20260923/finalize_evidence.py finalize
```

Finalization refuses failed/incomplete tests, altered criteria, altered registered code or unexpected original-file changes. Numeric certificate values are loaded reference snapshots; the canonical files remain scientific authority. This result concerns mathematical/numerical equivalence of the frozen B1 deterministic representations only; it does not provide independent experimental validation or freeze PURE_resource_core.
