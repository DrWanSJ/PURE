# Controlled PNAS 2017 research migration: local review packet

**Base:** `origin/main` at `0a72448ff20db8e58593a9910b8944c121750778`.
**Source:** `origin/research/pnas2017-full-network-reduction` at
`025fd340300a56f069c2136ea8bb0ff542b046d4`.
**Branch:** `codex/pnas2017-integration`. No push or merge was performed.
The machine-readable [verification](verification.json) and
[evidence graph](evidence_graph.json) are derived navigation, not source or
scientific authority.

| Package | Preserved or adapted | Intentionally excluded or deferred |
| --- | --- | --- |
| P1 | Publisher PDF, S01–S29, manifest and byte provenance | Identical author-site captures were not recopied |
| P2 | Species map, CSV/JSON, generator and validator; main-audit schema adapter | No state-elimination approval |
| P3 | 138-reaction, 47-species aminoacylation inventory, 52 pairing checks, analyses and validator | No new subsystem boundary or QSSA claim |
| P4 | A3a preregistration, partition, initialization, input hashes, negative controls, formal comparisons and failure records | No repair of failed A3a candidate |
| P5 | A3b-21 coordinate, ledger, smoke and closure-failure evidence | No restarted formal run |
| P6 | A3b-r12 nine-fast-state candidate, partial trajectory, solver failure, notes and logs | Token-ledger decision and new cycle remain open |
| P7 | A3c rule, protected rows and 0/21 table | No alternative selection rule invented |
| P8 | 37 selected research scripts, 31 author ZIP members, 38-file historical input snapshot and older runner; branch parser duplicates excluded | Advanced historical runners require the isolated historical input layout; current main audit was not replaced |
| P9 | 179 hash-bound historical run files in coherent families | No original run regenerated or overwritten |
| P10 | Current-status wording and OPEN-01–OPEN-08 register | No candidate promoted; G1 not rerun |

## Automated verification

| Check and command | Result | Scope |
| --- | --- | --- |
| `python scripts/verify_pnas2017_artifacts.py` | PASS | Main source/provenance, 241/968/26 inventory, 968 pending decisions and 16 review cards |
| `python scripts/verify_pnas2017_integration.py` | PASS, 10/0 | 30 publisher sources, 38 historical inputs, 179 run files, original/main identity, statuses and graph freshness |
| `python scripts/audit_pnas2017_sbml.py --output-dir <temp> --report <temp> --simbiology skip` | PASS for libSBML inventory | Four regenerated CSVs were byte-identical to main; RoadRunner unavailable in temporary Python environment, SimBiology deliberately skipped |
| `python scripts/pnas2017_research_schema_adapter.py --output-dir <temp>` and P2/P3 analyzers/validators with `PNAS2017_RESEARCH_AUDIT_DIR=<temp>` | PASS | 241/968/968 adapter; 241 species-map rows and ten aminoacylation tables equal historical data; P2 PASS and P3 30/0 |
| `python scripts/validate_pnas2017_aa_v1r2.py` in an isolated historical workspace | PASS, 13/0/0 | All 75 A3a input hashes restored with documented line endings and earlier runner; evidence integrity only |
| `python scripts/validate_pnas2017_aa_a3bc_cycle.py 025fd34 <temp-json>` in a clean detached research worktree, with `PYTHONUTF8=1` | PASS, 18/0/3 | Three formal-run checks correctly SKIP because the candidates stopped before formal validation |
| New MATLAB formal candidate runs or S28 pointwise comparison | NOT RUN | Historical failures are preserved; new scientific runs and acceptance rules require separate decisions |

The historical A3b/A3c validator's clean-worktree check fails in a temporary
workspace after historical tables are overlaid by design; the same validator
passed 18/0/3 in a clean detached research checkout. The migrated snapshot and
archive were separately matched to the source commit by byte and Git blob.
The first A3a validator attempt caught a worktree CRLF mismatch in a frozen
script; restoring that script's Git-blob LF bytes in the isolated workspace
gave 13/0/0. No archived bytes or criteria were changed.

## Human semantic review

Only review the current wording and the two decision indexes:

```powershell
git diff origin/main codex/pnas2017-integration -- README.md tasklist.md docs/pnas2017/g1_pnas_report.md docs/pnas2017/reference_reproduction.md models/pnas2017_full_reference/README.md references/PNAS2017_Matsuura/README.md references/PNAS2017_Matsuura/MISSING_SOURCES.md
git diff origin/main codex/pnas2017-integration -- docs/reduction/open_scientific_decisions.md docs/reduction/pnas2017_historical_evidence.md
```

Confirm: (A) no newer main result was overwritten, (B) failed/blocked/proposal
work was not relabeled as validated, (C) OPEN decisions were not silently
resolved, (D) the direction remains detailed PNAS reference -> classification
-> human review -> future reduced CRN, and (E) sources and negative evidence
remain preserved. `PURE_reduced_core` is **NOT YET APPROVED**.
