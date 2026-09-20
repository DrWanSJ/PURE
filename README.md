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

## 2. Current scientific status

> **`PURE_literature_reference` (B1) is frozen and regression-guarded;
> the scientific human audit is pending. Four B0 known-answer fixtures are
> implemented as verification problems.**

Evidence levels for B1 remain in `docs/project/evidence_levels.json`.
The new B0 fixtures do not change B1 evidence and are not PURE experimental
validation.

What this is **not**:

- **not human-verified** — the B1 scientific audit is still pending;
- **not experimentally validated** — machine-readable Stögbauer 2012 data
  are still absent;
- **not a completed project working model** — `PURE_resource_core`,
  nondimensionalization, project-model reduction/stability analysis,
  frontend, generic SSA integration and MCP remain scheduled work;
- **not evidence that generic SSA/QSSA/stability tooling is already complete** —
  the fixtures provide known-answer test problems that those tools must later
  pass.

## 3. Model identities

| identity | what it is | status |
| --- | --- | --- |
| `PURE_literature_reference` | frozen literal B1 reproduction of Mavelli, Marangoni, Stano (2015) | implemented, frozen |
| `PURE_resource_core` | the project's own working model (D6–D15 mechanisms) | not yet implemented |
| `reversible_conversion` | B0 closed reversible conversion | implemented |
| `birth_death` | B0 birth–death exact mean / Poisson / propensity reference | implemented; generic SSA hookup remains D16 |
| `enzyme_qssa` | B0 full enzyme + standard QSSA + total QSSA + failure regime | implemented |
| `appendix_a` | B0 dimensionless fixed-point/Jacobian/stability reference | implemented |

## 4. Repository layout

```
references/            source papers
models/
  literature_reference/  frozen B1 model
  pure_resource_core/    future project working model
  fixtures/              B0 known-answer models and frozen synthetic parameters
configs/               run conditions
schemas/               planned machine-readable schemas
data/                  raw/processed/audit data and provenance
matlab/
  src/
    simulate/             B1 simulation code
    fixtures/             commented B0 fixture implementations
    provenance/           provenance helpers
  codegen/               model-definition -> code generation
  generated/             generated B1 scientific code
  tests/                 B0 + B1 automated tests
scripts/                user entry points
results/                baselines, ordinary runs, release evidence
docs/                   project, validation and audit documentation
frontend/ service/ mcp/ reserved for later stages
```

## 5. Reproduce B1

```bash
matlab -batch "addpath('scripts'); reproduce_b1"
```

B1 ordinary simulation outputs go to `results/runs/<run_id>/`. Frozen
regression data remain under `results/baselines/b1_mavelli2015/`.

## 6. Run tests

```bash
matlab -batch "addpath('scripts'); run_all_tests"
```

This runs the full MATLAB test suite under `matlab/tests` (B0 fixtures +
B1 checks), the B1 benchmark smoke test, and development-mode release
preflight. Logs are written under `logs/`.

Individual B0 fixture tests can also be run directly, for example:

```matlab
runtests('matlab/tests/test_fixture_birth_death.m')
runtests('matlab/tests/test_fixture_enzyme_qssa.m')
runtests('matlab/tests/test_fixture_appendix_a.m')
```

## 7. Data / provenance rules

- `data/raw/` is immutable.
- `data/processed/` must be reproducible from registered raw inputs and tools.
- Every dataset must have provenance and licensing status.
- B0 synthetic parameters must not be copied into PURE experimental parameter
  stores.

## 8. Results policy

- `results/baselines/` — frozen regression baselines.
- `results/runs/<run_id>/` — ordinary unversioned simulation outputs.
- `results/releases/` — release evidence only.

## 9. Generated-code policy

The B1 single-source chain is:

`models/literature_reference/model_definition.json` →
`matlab/codegen/generate_pure_literature_reference.m` →
`matlab/generated/rhs_pure_literature_reference.m`.

Do not edit generated B1 files by hand.

## 10. Branch policy

The only long-lived branch is `main`. Tags mark frozen states. Release
preflight in release mode requires a clean tree.
