# audit_status.md — B1 benchmark audit hardening

Recorded: 2026-09-18. Last updated: 2026-09-22 (human B1 source audit completed).

## Baseline freeze

| item | value |
| --- | --- |
| AI B1 baseline commit | `ee3dedcfac3ceb51015836756a22a347c9fecd7c` |
| Annotated tag | `ai-b1-baseline` — "AI-generated B1 baseline before human audit hardening" |
| Tag pushed? | **No** (deferred to the user). Command: `git push origin ai-b1-baseline` |
| Audit branch | `audit/b1-hardening` (work happens here; `main` untouched, no merge) |
| Repository history | The baseline has **exactly one root commit** (`ee3dedc`); the whole B1 baseline was produced in a single AI working session. There is no per-step history behind the baseline artifacts. |
| Human audit of the baseline | **Completed for B1 literature-reproduction scope on 2026-09-22.** H01-H06 in `docs/audit/human_b1_audit.md` were confirmed `Y`, and both B1 MATLAB test suites passed. H07 records the explicit decision that a strict blind Fig. 4 audit is **not required** for B1 literature reproduction. The earlier 48-point Fig. 4 review remains non-blind and is not promoted to independent experimental validation. |

## Provenance honesty statement

- The legacy results under `results/baselines/b1_mavelli2015/` were produced **before** the
  provenance system (run manifests, execution-commit binding) existed. They are labeled
  `provenance_status = "legacy_unbound_to_execution_commit"`. Their numerical values are
  untouched. The claim that they were produced at commit `ee3dedc` rests on session
  records only; it is **not** cryptographically bound and must not be presented as if it
  were. No retroactive provenance has been (or may be) fabricated for them.
- All runs executed after this hardening pass write `results/runs/<run_id>/manifest.json` with
  a git commit read live from `git rev-parse HEAD`, an actual dirty-tree check, and
  SHA-256 hashes of the model definition, parameter file, and run inputs.
- The hardening pass itself does not rebuild provenance that never existed.

## Human B1 source audit (2026-09-22)

- `docs/audit/human_b1_audit.md`: H01-H06 = **Y**.
- Both B1 MATLAB test suites passed in the user's local run (`allPassed = 1`).
- Final B1 audit decision: **`human_audited = Y`** for literature-reproduction scope.
- H07 decision: strict simulation-blind Fig. 4 auditing is **not required** for B1 reproduction.
- This decision does not create an independent experimental-validation claim; `experimental_data_validation` remains false.

## Human D4 review (2026-09-20)

- Manual Fig. 4 readings were recorded for all **48 points** (3 DNA conditions × 2 panels × 8 times) in
  `data/manual_audit/fig4_human_digitization_sean.csv`.
- The reading targeted the paper's **calculated continuous curves**: top panel `[nt]`, bottom panel `[a]`;
  DNA 0.34 / 1.7 / 6.8 nM = blue / green / red.
- `simulation_hidden_during_reading = false`: the auditor had already seen simulation outputs. Therefore this
  is a **human visual review, not an independent blind audit**. No per-point numerical reading-error estimate
  was declared in the original reading, so the CSV leaves `estimated_reading_error_uM` blank.
- The user reran `run_fig4_benchmark('RunId','d4_human_check')` in MATLAB R2025b Update 5. All three DNA
  conditions completed with `scientific_status = passed_all_qc`; scaled mass-balance residuals were
  (5.821e-15, 4.396e-15, 3.941e-15) and tighter-tolerance trajectory differences were
  (3.766e-9, 3.757e-9, 3.742e-9).
- The local rerun was **not commit-bound** because Git metadata was unavailable
  (`git_commit = unavailable_git_not_found`, `git_dirty = unknown`). Per repository policy, ordinary
  `results/runs/` outputs are not committed.
- The manual readings support the same curve ordering, shape, and magnitude as the reproduced trajectories. A strict simulation-blind reading was not performed. On 2026-09-22 the human reviewer explicitly decided that this stronger evidence stream is not required for B1 literature reproduction; it would only be needed for a stronger independent Fig. 4 raster-validation claim.

## Validation status layers (see `docs/project/evidence_levels.json`)

| layer | value |
| --- | --- |
| `bibliography_verified` | true |
| `equations_transcribed` | true |
| `equation_level_tests_passed` | true (AI-written tests; logs under `logs/`) |
| `numerical_solver_qc_passed` | true |
| `paper_text_anchor_match` | true |
| `fig4_simulation_assisted_digitization_match` | true, but **`non_independent_assignment`** — the digitized "calculated" cluster was selected by nearest-to-simulation tracking, so the comparison is NOT an independent check and must not be used as reproduction acceptance evidence by itself |
| `fig4_human_visual_review` | **`completed_nonblind`** — 48 manual readings recorded in `data/manual_audit/fig4_human_digitization_sean.csv`; useful as D4 human review, but not independent because the auditor had previously seen the simulation |
| `d4_manual_benchmark_rerun` | **`passed_all_qc`** — local run `d4_human_check`; Git provenance unavailable in the local downloaded directory, so the run is not commit-bound |
| `b1_human_source_audit` | **completed** — H01-H06 = Y; B1 marked `human_audited` for literature-reproduction scope |
| `fig4_independent_human_audit` | **not performed; not required for B1 reproduction** — the machine-readable evidence field remains `pending_human_audit` only to guard against falsely claiming independent raster validation; blind protocol remains available if that stronger claim is later desired |
| `experimental_data_validation` | **false** — no machine-readable Stögbauer 2012 data exist in the repo; the experimental dotted curves were not digitized |
| B2 predictive validation | not started (out of B1 scope) |

The independent Fig. 4 raster-validation stream is intentionally **not completed** for B1. The 2026-09-22 H07 decision records that it is not required for the current literature-reproduction claim; no pass is claimed for that stronger evidence layer.

## CI status

**`CI = not_verified`.** No CI existed in the baseline. A GitHub Actions workflow draft
was added (`.github/workflows/matlab-ci.yml`) but has never run: MATLAB-on-runner
licensing/availability is unconfirmed in this environment. Manual verification command:

```bash
matlab -batch "addpath('matlab/tests','matlab/src/simulate','matlab/generated','matlab/codegen','matlab/src/provenance'); run_all_tests"
```

(or push the branch with Actions enabled and inspect the run log).

## Explicitly not done (per project tasklist; deliberately out of scope here)

PURE_resource_core · nondimensionalization · QSSA/reduction · stability analysis ·
flow frontend · SSA · MCP. The hardening pass adds no scientific mechanisms and does not
start these tasks.

## Items requiring human review (summary)

The B1 source-to-repository scientific audit is complete for the current literature-reproduction scope, and the blind Fig. 4 decision has been made. Remaining human/governance items are:

1. Licensing decision for the tracked publisher PDFs (`docs/project/licensing_review.md`).
2. Mutation tests M1–M5 by a human on a scratch branch if independent software-hardening evidence is desired (`docs/audit/mutation_test_protocol.md`).
3. CI enablement decision (license/runner).

A strict blind Fig. 4 audit is optional future evidence, not an unfinished B1 reproduction requirement.
