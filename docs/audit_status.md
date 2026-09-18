# audit_status.md — B1 benchmark audit hardening

Recorded: 2026-09-18, branch `audit/b1-hardening`.

## Baseline freeze

| item | value |
| --- | --- |
| AI B1 baseline commit | `ee3dedcfac3ceb51015836756a22a347c9fecd7c` |
| Annotated tag | `ai-b1-baseline` — "AI-generated B1 baseline before human audit hardening" |
| Tag pushed? | **No** (deferred to the user). Command: `git push origin ai-b1-baseline` |
| Audit branch | `audit/b1-hardening` (work happens here; `main` untouched, no merge) |
| Repository history | The baseline has **exactly one root commit** (`ee3dedc`); the whole B1 baseline was produced in a single AI working session. There is no per-step history behind the baseline artifacts. |
| Human audit of the baseline | **Not done.** Everything below `ai-b1-baseline` is AI-generated: equations transcription, parameter lock, tests, digitization, and documentation. Passing tests written by the same session that wrote the model are NOT a substitute for human scientific review. |

## Provenance honesty statement

- The legacy results under `results/literature_reference/` were produced **before** the
  provenance system (run manifests, execution-commit binding) existed. They are labeled
  `provenance_status = "legacy_unbound_to_execution_commit"`. Their numerical values are
  untouched. The claim that they were produced at commit `ee3dedc` rests on session
  records only; it is **not** cryptographically bound and must not be presented as if it
  were. No retroactive provenance has been (or may be) fabricated for them.
- All runs executed after this hardening pass write `results/<run_id>/manifest.json` with
  a git commit read live from `git rev-parse HEAD`, an actual dirty-tree check, and
  SHA-256 hashes of the model definition, parameter file, and run inputs.
- The hardening pass itself does not rebuild provenance that never existed.

## Validation status layers (see `docs/evidence_levels.json`)

| layer | value |
| --- | --- |
| `bibliography_verified` | true |
| `equations_transcribed` | true |
| `equation_level_tests_passed` | true (AI-written tests; logs under `logs/`) |
| `numerical_solver_qc_passed` | true |
| `paper_text_anchor_match` | true |
| `fig4_simulation_assisted_digitization_match` | true, but **`non_independent_assignment`** — the digitized "calculated" cluster was selected by nearest-to-simulation tracking, so the comparison is NOT an independent check and must not be used as reproduction acceptance evidence by itself |
| `fig4_independent_human_audit` | **`pending_human_audit`** (blind protocol: `docs/manual_fig4_audit_protocol.md`; template: `data/manual_audit/fig4_human_digitization_template.csv`) |
| `experimental_data_validation` | **false** — no machine-readable Stögbauer 2012 data exist in the repo; the experimental dotted curves were not digitized |
| B2 predictive validation | not started (out of B1 scope) |

`independent_fig4_validation_status = "pending_human_audit"` until the blind human CSV is
filled and reviewed.

## CI status

**`CI = not_verified`.** No CI existed in the baseline. A GitHub Actions workflow draft
was added (`.github/workflows/matlab-ci.yml`) but has never run: MATLAB-on-runner
licensing/availability is unconfirmed in this environment. Manual verification command:

```bash
matlab -batch "addpath('matlab/tests','matlab/simulate','matlab/generated','matlab/codegen','matlab/provenance'); run_all_tests"
```

(or push the branch with Actions enabled and inspect the run log).

## Explicitly not done (per project tasklist; deliberately out of scope here)

PURE_resource_core · nondimensionalization · QSSA/reduction · stability analysis ·
flow frontend · SSA · MCP. The hardening pass adds no scientific mechanisms and does not
start these tasks.

## Items requiring human review (summary)

1. Scientific review of the model transcription against the paper (AI audit is not human audit).
2. Blind Fig. 4 human digitization (protocol + template provided).
3. Licensing decision for the tracked publisher PDFs (`docs/licensing_review.md`).
4. Mutation tests M1–M5 by a human on a scratch branch (`docs/mutation_test_protocol.md`).
5. CI enablement decision (license/runner).
