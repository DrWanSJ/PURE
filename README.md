# PURE — Cell-Free Expression Modeling Workbench

CRN modeling workbench for the PURE transcription–translation system
(synthetic-cell platform project).

## 1. Project purpose

Build a reproducible modeling stack for cell-free expression: a frozen
literature benchmark, then a project working model, verification fixtures,
deterministic and stochastic solvers, analysis (conservation,
nondimensionalization, reduction, stability) and, later, a flow frontend,
service and MCP interface. This repository is organized around clear
boundaries between **model, data, run conditions, code, results, theory,
audit and interfaces** — files are not to be piled into the repository root.

## 2. Current scientific status (honest, 2026-09-18)

> **`PURE_literature_reference` (B1) is frozen and regression-guarded;
> the scientific human audit is pending. Nothing else has been started.**

Evidence levels (see `docs/project/evidence_levels.json`):
`bibliography_verified = true`, `equations_transcribed = true`,
`equation_level_tests_passed = true` (AI-written tests — **not** human
scientific review), `numerical_solver_qc_passed = true`,
`paper_text_anchor_match = true`,
`fig4_simulation_assisted_digitization_match = true`
(**`non_independent_assignment`** — not usable as independent evidence),
`fig4_independent_human_audit = pending_human_audit`,
`experimental_data_validation = false` (no machine-readable Stögbauer 2012 data).

What this is **not** (none of these claims may be made yet):

- **not human-verified** — no human scientific audit of the transcription, the
  tests, or the Fig. 4 digitization has been performed
  (`docs/audit/audit_status.md`, `docs/audit/mutation_test_protocol.md`,
  `docs/audit/manual_fig4_audit_protocol.md`, `docs/audit/human_b1_audit.md`
  define the pending human work);
- **not experimentally validated** — no machine-readable Stögbauer 2012 data
  exist here;
- **not "fully reproduced"** in a strong sense — the Fig. 4 raster
  digitization match is simulation-assisted and counts only as an envelope
  check; the independent evidence so far is the paper-text anchor match;
- the following tasklist items have **not been started**: PURE_resource_core,
  B0 fixtures, nondimensionalization, QSSA/reduction, stability analysis, flow
  frontend, SSA, MCP. CI is a draft and `not_verified`.

## 3. Model identities

| identity | what it is | status |
| --- | --- | --- |
| `PURE_literature_reference` | frozen literal B1 reproduction of Mavelli, Marangoni, Stano (2015), *Bull. Math. Biol.* 77:1185–1212, DOI [10.1007/s11538-015-0082-8](https://doi.org/10.1007/s11538-015-0082-8) — deterministic, 10 ODE states, 6 Michaelis–Menten rate laws, 16 kinetic parameters; time in s, concentrations in µM | implemented, frozen; never extended or "upgraded" |
| `PURE_resource_core` | the project's own working model (D6–D15 mechanisms) | **not yet implemented** — separate identity, lives in `models/pure_resource_core/` |
| fixtures (`reversible_conversion`, `birth_death`, `enzyme_qssa`, `appendix_a`) | B0 mathematical/software verification models | **not yet implemented** |

## 4. Repository layout

```
references/            source papers (R01 = Mavelli 2015) + per-paper README
models/
  literature_reference/  B1 model: model_definition.json (numeric source of truth),
                         model_manifest.json (identity/evidence), parameters.json
  pure_resource_core/    project working model (skeleton, not implemented)
  fixtures/              B0 verification models (skeleton, not implemented)
configs/               run conditions (model ≠ run condition); benchmarks/b1_fig4/
schemas/               planned machine-readable schemas (skeleton)
data/
  raw/                   immutable source material (raw/literature/R01/)
  processed/             derived data, reproducible from raw (processed/literature/R01/fig4/)
  manual_audit/          blind human audit templates
  provenance.csv         single provenance ledger (SHA-256, licensing)
matlab/
  src/                   hand-maintained scientific code (simulate/, provenance/)
  codegen/               model-definition -> code generator
  generated/             AUTO-GENERATED code - do not edit by hand
  tools/                 auxiliary tools (digitization/)
  tests/                 test suite (+ fixtures/ frozen test fixtures)
scripts/                user entry points: reproduce_b1.m, run_all_tests.m, release_preflight.m
results/
  baselines/             frozen regression baselines (committed, never overwritten)
  runs/<run_id>/         ordinary run outputs (NOT versioned; each has manifest.json)
  releases/              release evidence (D20 v0.1; empty)
docs/
  project/               benchmark registry, evidence levels, licensing review
  validation/            execution/validation reports
  audit/                 audit status, protocols, human audit checklists, logs/
environment_lock.md     locked environment and source hashes
tasklist.md             scientific task definitions (do not edit casually)
CHANGELOG.md            repository-level changes
frontend/  service/  mcp/   reserved for later stages (not started)
```

## 5. Reproduce B1

```bash
# full benchmark: three DNA conditions (0.34 / 1.7 / 6.8 nM), 0-4 h, ode15s
matlab -batch "addpath('scripts'); reproduce_b1"
# or directly (RunId defaults to a timestamp):
matlab -batch "addpath('matlab/src/simulate','matlab/generated','matlab/src/provenance'); run_fig4_benchmark"
```

Outputs go to `results/runs/<run_id>/` (unversioned) with `manifest.json`
(live git commit, dirty-tree status, SHA-256 of model definition /
parameters / inputs). Compare against the frozen baseline
`results/baselines/b1_mavelli2015/` — `DNA_*/trajectory.csv` and
`rates.csv` must reproduce numerically (byte-identical on the same MATLAB
release).

## 6. Run tests

```bash
matlab -batch "addpath('scripts'); run_all_tests"
```

Runs the full unit suite (`matlab/tests`, 18 tests), a benchmark smoke test,
and `release_preflight('Mode','development')`. Logs are persisted under
`logs/`; evidence worth keeping is committed to `docs/audit/logs/`.

## 7. Data / provenance rules

- `data/raw/` is immutable: never overwrite, regenerate or "improve" raw files.
- `data/processed/` must be reproducible from `data/raw/` + the registered
  tool (e.g. `matlab/tools/digitization/digitize_fig4.m`).
- Every dataset has a row in `data/provenance.csv` (origin, role, SHA-256,
  licensing). File identity for locked sources is also recorded in
  `environment_lock.md`.
- `.gitattributes` pins `*.json` to LF so provenance hashes reproduce on any
  fresh checkout.

## 8. Results policy

- `results/baselines/` — frozen regression baselines, committed, **never
  overwritten and never extended** by ordinary runs.
- `results/runs/<run_id>/` — ordinary simulation outputs, **not versioned**
  (gitignored); each carries its own provenance manifest.
- `results/releases/` — release evidence only (produced via
  `scripts/release_preflight.m` in release mode on a clean tree).

Ordinary simulation outputs belong in `results/runs/` and are not versioned.
Only regression baselines and release evidence are committed.

## 9. Generated-code policy

The single-source chain is:
`models/literature_reference/model_definition.json` →
`matlab/codegen/generate_pure_literature_reference.m` →
`matlab/generated/rhs_pure_literature_reference.m`.

**Do not edit files under `matlab/generated` manually. They must be
regenerated from the registered model definition.** Hand edits are detected
by the regeneration-sync test (`matlab/tests/test_codegen_and_provenance.m`).

Run conditions belong in `configs/`, not in new copies of a model.

## 10. Branch policy

- The only long-lived branch is `main`. All work lands on `main` (no
  `feature/*`, `audit/*`, `week/*` long-lived branches; use short-lived
  branches only when necessary and delete them after integration).
- Tags mark frozen states: `ai-b1-baseline` (pre-hardening AI baseline) and
  `b1-reference-v1` (frozen verified B1 benchmark after the repository
  reorganization; no scientific/numerical model changes).
- A dirty tree blocks `release_preflight('Mode','release')`; releases require
  a clean `main`.
