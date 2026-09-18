# b1_hardening_report.md — B1 benchmark audit hardening

Date: 2026-09-18 · Branch: `audit/b1-hardening` · Baseline: `ai-b1-baseline`
(tag on `ee3dedcfac3ceb51015836756a22a347c9fecd7c`, tag **not pushed**)

> Note (2026-09-18): after this report was written the repository layout was
> reorganized (branch audit/b1-hardening fast-forwarded into main). Paths below
> point to the current layout; the commands were originally executed when
> results/literature_reference/ was the baseline directory and
> results/b1_fig4_hardening_20260918/ the run output directory.

## 1. What was changed


- **A — baseline freeze:** annotated tag `ai-b1-baseline` ("AI-generated B1
  baseline before human audit hardening") on the baseline commit;
  `docs/audit/audit_status.md` records baseline facts (single root commit, not
  human-audited, no retroactive provenance) and `docs/project/evidence_levels.json`
  splits the single `reproduced=true` into explicit evidence layers with
  locked pending/false values.
- **B — real provenance for new runs:** `matlab/src/provenance/`
  (`pure_sha256_file/string` — fixed SHA-256, FIPS 180-4 vector tested;
  `pure_git_state` — live `git rev-parse HEAD` + `git status --porcelain`;
  `pure_run_provenance` — model-definition/parameter/input hashes).
  `run_fig4_benchmark` now writes `results/runs/<run_id>/manifest.json` for every
  new run; the legacy directory `results/baselines/b1_mavelli2015/` is frozen and
  labeled `legacy_unbound_to_execution_commit` (labels only, numbers
  untouched); README distinguishes legacy vs provenance-bound results.
- **C — truthful "generated":** canonical machine-readable definition
  `models/literature_reference/model_definition.json` (state order, exact
  rate-law/ODE expressions, stoichiometry matrix + average-species divisors,
  parameter refs, units, observables) + real generator
  `matlab/codegen/generate_pure_literature_reference.m` that deterministically
  emits `matlab/generated/rhs_pure_literature_reference.m` (header embeds the
  definition SHA-256) and self-checks the emitted expressions against the
  stoichiometry matrix (max violation 4.4e-16 uM/s). The pre-hardening RHS is
  preserved as `rhs_pure_literature_reference_baseline_snapshot.m`. Deleting
  the generated file and rerunning the generator reproduces it (sync test).
- **D — Fig. 4 circularity fixed:** `digitize_fig4.m` keeps its algorithm but
  is now explicitly `non_independent_assignment` (calculated-vs-dotted cluster
  assignment uses nearest-to-simulation tracking);
  `data/processed/literature/R01/fig4/fig4_digitized_validation_status.json` records this;
  blind human protocol (`docs/audit/manual_fig4_audit_protocol.md`) + template
  (`data/manual_audit/fig4_human_digitization_template.csv`) added;
  `fig4_independent_human_audit = pending_human_audit`. All wording that
  cited "≤ 1.8 % everywhere" as evidence was demoted to an exploratory
  envelope tier in registry/benchmark_v0/README/legacy summary JSON.
- **E — evidence levels:** `docs/project/evidence_levels.json` with
  `bibliography_verified / equations_transcribed / equation_level_tests_passed /
  numerical_solver_qc_passed / paper_text_anchor_match = true`,
  `fig4_simulation_assisted_digitization_match = true (non_independent_assignment)`,
  `fig4_independent_human_audit = pending_human_audit`,
  `experimental_data_validation = false`, `b2_predictive_validation = false`;
  guarded by preflight tests (silent flipping fails the suite).
- **F — guards:** `scripts/release_preflight.m` (git/HEAD/dirty,
  hash computability, generated-artifact sync, legacy labels, manifest field
  completeness, evidence-level locks, persisted-log requirement) +
  `matlab/tests/test_release_preflight.m` incl. a behavioral dirty-tree test.
- **G — test log + CI draft:** `scripts/run_all_tests.m` (unit + smoke +
  preflight, diary to `logs/<timestamp>_tests.log`); two logs committed
  (pre-preflight and post-preflight). `.github/workflows/matlab-ci.yml` is a
  **draft that has never run**; `CI = not_verified`.
- **H — mutation protocol:** `docs/audit/mutation_test_protocol.md` (M1–M5 with
  expected failing tests and documented non-failures; human-executed on a
  scratch branch; AI execution must not be reported as human review).
- **I — licensing register:** `docs/project/licensing_review.md` — tracked publisher
  PDF/transcription/figure render listed; keep/remove/purge decision left to
  the human owner; no deletion, no history rewrite.
- **J — honest status:** README now states "engineering/audit hardening in
  progress; scientific human audit pending" and lists the not-started
  tasklist items (PURE_resource_core, nondimensionalization, reduction,
  stability analysis, flow frontend, SSA, MCP).

## 2. What was NOT changed

- The scientific model: `parameters.json` values (Table 1/2 central values),
  all equations Eqs. (5), (6), (8), (10), (12), (14), (20)–(27), the
  multiplicity factors, the state set — byte-for-byte unchanged in meaning
  (`parameters.json` hash unchanged from baseline; see §13/§12).
- The legacy numerical results (`results/baselines/b1_mavelli2015/*.csv` values).
- Git history (no rebase/filter/force; `main` untouched, nothing merged).
- No fake human-audit data, no back-filled provenance, no CI success claims.

## 3. Commits (in order, on `audit/b1-hardening`)

| SHA | subject |
| --- | --- |
| `ee3dedc` | (baseline, tagged `ai-b1-baseline`) |
| `32d72b9` | docs(audit): freeze AI baseline status and split evidence levels |
| `123bc50` | feat(codegen): real single-source generation chain for the B1 RHS |
| `f4ff67b` | feat(provenance): run manifests with live git binding; label legacy results |
| `2faf32b` | fix(audit): reclassify Fig.4 digitization as non_independent_assignment |
| `2bece5e` | test(hardening): run_all_tests with persisted logs + CI workflow draft |
| `fccf621` | test(hardening): release/development preflight guards |
| `10235db` | run(hardening): first provenance-bound benchmark run |
| `1752255` | docs(hardening): mutation protocol, licensing register, honest project status |
| (HEAD) | docs(audit): this report |

## 4. Tests actually executed (exact commands)

```bash
# full unit suite (multiple times during hardening; final state):
matlab -batch "r = runtests('matlab/tests'); fprintf('TOTAL: %d passed, %d failed\n', sum([r.Passed]), sum([r.Failed]));"
# -> TOTAL: 18 passed, 0 failed

# full check runner with persisted log:
matlab -batch "addpath('scripts'); run_all_tests"
# -> docs/audit/logs/20260918_130736_tests.log: 18/18 unit tests, smoke passed, preflight run

# provenance-bound benchmark run:
matlab -batch "addpath('matlab/src/simulate','matlab/generated','matlab/src/provenance'); run_fig4_benchmark('RunId', 'b1_fig4_hardening_20260918')"
# -> results/baselines/b1_mavelli2015/audit/hardening_20260918/manifest.json (git fccf621…, dirty=false)

# numeric identity check vs legacy:
for d in DNA_0p34nM DNA_1p7nM DNA_6p8nM; do
  diff -q "results/baselines/b1_mavelli2015/$d/trajectory.csv" "results/baselines/b1_mavelli2015/audit/hardening_20260918/$d/trajectory.csv"
  diff -q "results/baselines/b1_mavelli2015/$d/rates.csv" "results/baselines/b1_mavelli2015/audit/hardening_20260918/$d/rates.csv"
done   # -> all IDENTICAL
```

## 5. Pass / fail / not_run

| item | status |
| --- | --- |
| unit suite (9 baseline + 5 codegen/provenance + 4 preflight tests) | **18/18 pass** |
| benchmark smoke test (600 s @ 6.8 nM, QC asserts) | **pass** (log) |
| provenance-bound benchmark run (3 DNA × 0–4 h, 3 repeats, tight-tolerance study) | **pass**, `passed_all_qc` (manifest + qc.json) |
| numeric identity new run vs legacy trajectories/rates | **pass** (byte-identical) |
| generator idempotence / sync | **pass** |
| generated RHS vs frozen baseline snapshot at fixed states | **pass** (exact, 0 diff) |
| stoichiometry vs state expressions | **pass** (≤ 4.4e-16 uM/s) |
| mutation tests M1–M5 | **not_run** (human task per protocol) |
| blind human Fig. 4 audit | **not_run** (`pending_human_audit`) |
| experimental data validation | **false / not possible** (no data) |
| CI | **not_verified** (draft workflow only) |
| licensing decision | **pending human decision** |

## 6. Legacy provenance limitations

`results/baselines/b1_mavelli2015/` values were produced before the provenance
system existed and are labeled `legacy_unbound_to_execution_commit`. The
session record associates them with `ee3dedc`, but this is not
cryptographically bound and is not presented as such. No legacy file was
back-filled with execution provenance; only status labels were added. The
provenance-bound replacement run (`b1_fig4_hardening_20260918`) reproduces
the legacy numbers byte-identically, which is the strongest legitimate bridge
between the two.

## 7. Items requiring human review

1. Scientific audit of the transcription against the paper (AI tests ≠ human review).
2. Blind Fig. 4 digitization per protocol; then set `fig4_independent_human_audit`.
3. Mutation tests M1–M5 on a scratch branch; record results in the protocol.
4. Licensing decisions for the tracked publisher files (`docs/project/licensing_review.md`).
5. CI enablement (MATLAB license/runner) and removal of the draft banner.
6. Decide whether to push the `ai-b1-baseline` tag:
   `git push origin ai-b1-baseline`.

## 8. Deliberately deferred (out of scope by instruction)

PURE_resource_core · nondimensionalization · QSSA/reduction · stability
analysis · flow frontend · SSA · MCP · any new biological mechanism · any
refitting.

## 9–10. Numerical results statement

**No numerical result changed.** Evidence: (a) `trajectory.csv` and
`rates.csv` of the provenance-bound run are byte-identical to the legacy
baseline results for all three DNA conditions; (b) the generated RHS is
exactly equal (0 diff) to the frozen baseline snapshot at fixed states;
(c) all QC numbers (balance residuals ~4e-15 scaled, energy split
72.0/15.4/12.5 %, protein(4h) 0.589 µM) match the baseline records. The only
content differences in model files are comments/headers (generator provenance
header) — the RHS arithmetic expressions are line-for-line identical.
Because of this, no stop condition under K.13 was triggered.

## 11. Repository state at the end of this pass

- Branch `audit/b1-hardening`, working tree clean, `main` untouched.
- Tag `ai-b1-baseline` created locally, **not pushed** (owner command above).
- Branch push (performed so the human reviewer can see it):
  `git push -u origin audit/b1-hardening`. No merge, no push of `main`.
