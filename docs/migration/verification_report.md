# PNAS2017 authority migration verification — 2026-10-08

Qualification is limited to engineering integrity, source identity, mapping boundaries and historical preservation.
Figure reproduction is PAUSED_BY_USER; no new author ODE integration, panel comparison or figure generation was run.
Published-figure reproduction and independent experimental validation are NOT_ESTABLISHED.

## Qualified revision and evidence

The complete local preflight passed at committed revision `80b5cfa0a157978688d4a78bd9b61bfe08fcfbee`, with a clean worktree.
Its timestamp is `2026-10-08T02:05:44.275715+00:00`.
The external `pnas2017-authority-migration-validation-03/preflight.json` records 21 successful commands, their exact arguments,
native log hashes and verifier input hashes. Logs and pointwise reports remain outside Git; hosted CI saves the equivalent artifact.
The later closeout adds this report, expands the legacy navigation and declares native CRLF whitespace semantics for exact copies;
it makes no implementation or scientific changes.

## Results

| Check | Result and scope |
| --- | --- |
| Current authority/source guard | PASS; frozen input hashes, 241 species, 968 reactions, 26 subsystems, author mappings, 3854 normalization signatures, S28 identity and historical Git blobs |
| verify_pnas2017_artifacts.py | PASS |
| verify_pnas2017_integration.py | PASS; same checks, successor output redirected externally |
| verify_reaction_level_annotation.py / v2 / contract | PASS, all three |
| verify_species_information_contract.py | PASS |
| verify_reduction_audit_v0.py | PASS |
| verify_source_coordinate_certificate_v1.py | PASS; existing coordinate certificates retained |
| verify_pnas2017_reduction_evidence.py | PASS, including its existing negative controls |
| verify_r3_preregistration_v1.py | PASS |
| verify_r3_bounded_closeout_v1.py | PASS; negative and incomplete scientific outcomes retained |
| Source-coordinate pointwise verifier, charts v1–v7 | PASS, all seven |
| New active-authority mutation suite | PASS, 8 tests |
| Existing S28 status/protection suite | PASS, 5 tests |
| MATLAB author entrypoint syntax and source CSV import | PASS under MATLAB R2025b; integration NOT_RUN |
| git diff --check | PASS |
| Fig. 2B / Fig. 3A / Fig. 5A / supplementary panels | PAUSED_NOT_RUN; numerical errors NOT_COMPUTED |

The eight new negative controls reject modified S28 bytes, permuted exact species columns, an altered author initial value,
an altered k1 value, a changed PO4 coefficient in re0000000414, a 1e-5 time start, unsupported QSS resolution and unsupported figure PASS.
They use read overlays or copied semantic structures and leave source bytes unchanged.

## Preserved failed qualification

Validation-01 ran all 21 commands with exit code zero but **failed qualification** because the existing integration verifier
rewrote a historical detail record. The frozen report described 11 immutable review files; the current verifier described
10 immutable files plus the already approved review synchronization. Both byte hashes and the native successor output remain
in validation-01. Historical report bytes were restored. No expected hash or scientific status was relaxed.
The current preflight redirects only the integration verifier's output destination, preserving every original check.
Validation-02 and validation-03 passed without any historical report rewrites.

A subsequent full-branch whitespace check initially flagged native CRLF in the new exact legacy copies.
Those source bytes remain unchanged. The scoped whitespace attribute now recognizes carriage returns at end of line while
continuing to check actual trailing spaces, trailing blank lines and spaces before tabs. The full-branch check then passed.

## Scientific boundaries

241→214 SOURCE_GENERAL coordinate reduction, the rank-177 frozen-author execution boundary, H1–H5,
the R3 negative/adverse incomplete records, all 968 PENDING kinetic decisions and PURE_reduced_core NOT_VALIDATED remain unchanged.
The S28 RRF1600 versus author CSV/S27 RRF16 contradiction and the exact Fig. 3A QSS transform remain unresolved.
Neither curation PASS nor the present engineering PASS approves a figure reproduction, reduced model or experiment.

## Repeat the current checks

```sh
python -B scripts/reproduce_pnas2017_reference.py --verify
python -B scripts/run_pnas2017_preflight.py --report-dir <new-external-directory>
```

These commands generate no figures. A hosted-runner result must be read separately; this local record does not assert hosted CI PASS.

## Hosted environment qualification

The first Ubuntu/pip hosted run at 5bbb300 failed the frozen P08 eigenvalue check at time0.005291978735958442:
2.5477468286180927e-7 exceeded the unchanged1e-7 requirement. All other20 commands passed; the native failed artifact is preserved.
See [failed hosted run](https://github.com/DrWanSJ/PURE/actions/runs/37717040384).
The CI now registers the exact Windows/MKL package builds from the successful local qualification environment,
using an explicit package dependency closure and the existing SymPy overlay. Thresholds, protected verifier bytes and scientific inputs remain unchanged.
The failed Linux check remains a limitation of cross-platform numerical verification; a Windows CI PASS does not establish Linux equivalence.
