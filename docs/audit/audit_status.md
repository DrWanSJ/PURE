# audit_status.md — B1 benchmark audit hardening

Recorded: 2026-09-18. Last updated: 2026-09-20 (human D4 review).

## Baseline freeze

| item | value |
| --- | --- |
| AI B1 baseline commit | `ee3dedcfac3ceb51015836756a22a347c9fecd7c` |
| Annotated tag | `ai-b1-baseline` — "AI-generated B1 baseline before human audit hardening" |
| Tag pushed? | **No** (deferred to the user). Command: `git push origin ai-b1-baseline` |
| Audit branch | `audit/b1-hardening` (work happens here; `main` untouched, no merge) |
| Repository history | The baseline has **exactly one root commit** (`ee3dedc`); the whole B1 baseline was produced in a single AI working session. There is no per-step history behind the baseline artifacts. |
| Human audit of the baseline | **Partial human review completed 2026-09-20.** The user manually inspected the Fig. 4 calculated continuous curves at 48 points and reran the benchmark locally. The Fig. 4 reading was **not blind** because simulation output had already been viewed, so it does not satisfy the independent blind-audit protocol. The original model/tests/automated digitization remain AI-generated unless separately checked. |

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
- The manual readings support the same curve ordering, shape, and magnitude as the reproduced trajectories,
  but `fig4_independent_human_audit` remains `pending_human_audit` until a genuinely simulation-blind
  reading with declared uncertainty is performed.

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
| `fig4_independent_human_audit` | **`pending_human_audit`** (blind protocol: `docs/audit/manual_fig4_audit_protocol.md`; template: `data/manual_audit/fig4_human_digitization_template.csv`) |
| `experimental_data_validation` | **false** — no machine-readable Stögbauer 2012 data exist in the repo; the experimental dotted curves were not digitized |
| B2 predictive validation | not started (out of B1 scope) |

`independent_fig4_validation_status = "pending_human_audit"` until the blind human CSV is
filled and reviewed.

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

1. Scientific review of the model transcription against the paper (AI audit is not human audit).
2. Strict blind Fig. 4 human digitization remains pending if independent raster evidence is required; the 2026-09-20 D4 review is recorded but was non-blind.
3. Licensing decision for the tracked publisher PDFs (`docs/project/licensing_review.md`).
4. Mutation tests M1–M5 by a human on a scratch branch (`docs/audit/mutation_test_protocol.md`).
5. CI enablement decision (license/runner).
