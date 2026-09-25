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

> **The primary benchmark has pivoted to Matsuura et al. 2017 (PNAS).**
> `PNAS2017_full_reference` is now the detailed, SBML-canonical reference
> (acquired, hashed, inventoried, ledger-built, reduction-mapped). The previous
> coarse benchmark `PURE_literature_reference` (B1, Mavelli 2015) is **frozen
> legacy** through the prior D7 RS-QSSA work — it is not wrong, it is simply no
> longer detailed enough for the revised scientific question.

### Project status

- **OLD / FROZEN — `Mavelli2015_coarse_reference`.** Coarse-grained comparator,
  completed through the previous D7 RS-QSSA work. Frozen regression-guarded
  (tag `b1-reference-v1` and the pre-PNAS archival tag
  `archive-mavelli2015-d7-20260924`). No longer the active main benchmark; a
  historical coarse endpoint against which an independently derived reduction
  may later be compared.
- **ACTIVE — `PNAS2017_full_reference`.** Acquisition ✅ · checksum freeze ✅ ·
  SBML inventory/audit ✅ · chemical/resource ledger ✅ · 968-reaction reduction
  **map** + 241-species / moiety-level pooling **map** (no reduction performed)
  ✅. Pending: libSBML/RoadRunner validation (tooling unavailable — see
  `MISSING_SOURCES.md`), SI-dataset parsing, and the human reduction decisions.
- **FUTURE — `PURE_reduced_core`.** Derived only from approved reduction
  decisions (structural proposal in `docs/reduction/candidate_core_v0.md`);
  transcription extension; GUV transport; flow visualization; MCP service.

Evidence levels and gates live in `docs/project/evidence_levels.json` and
`tasklist.md`. **No reduction has been finalised by the AI; every candidate
transformation is marked `HUMAN_REVIEW_REQUIRED`.**

What this is **not**:

- **not a validated reduced model** — `PURE_reduced_core` does not exist yet;
- **not experimentally validated** — this is a literature reference network;
- **not a completed SBML-standard reproduction** — libRoadRunner/Tellurium could
  not be installed, so the reference was corroborated with the authors' own
  MATLAB integrator (see `docs/pnas2017/reference_reproduction.md`);
- **not charge/ionic-strength complete** — the SBML carries no formula/charge,
  so ionic strength is deliberately **not** computed (see the ledger).

## 3. Model identities

| identity | what it is | status |
| --- | --- | --- |
| `PNAS2017_full_reference` | **NEW primary benchmark** — literal imported Matsuura 2017 detailed translation network (SBML-canonical, no scientific modification, benchmark + provenance only) | acquired, hashed, audited, ledgered, reduction-mapped |
| `PURE_reduced_core` | **the project's future model** — derived from explicit reduction decisions, NOT ad-hoc deletion; ~few-tens of reactions, SBML | proposal only, not created |
| `Mavelli2015_coarse_reference` | **frozen historical coarse comparator** (was B1 / `PURE_literature_reference`) — no longer primary | frozen through prior D7 RS-QSSA work |
| `reversible_conversion` | B0 closed reversible conversion | implemented |
| `birth_death` | B0 birth–death exact mean / Poisson / propensity reference | implemented; generic SSA hookup remains D16 |
| `enzyme_qssa` | B0 full enzyme + standard QSSA + total QSSA + failure regime | implemented |
| `appendix_a` | B0 dimensionless fixed-point/Jacobian/stability reference | implemented |

> The PNAS benchmark is **mRNA-directed translation**. It does **not** contain a
> DNA → RNA transcription module; transcription and membrane (GUV) transport are
> future project modules and must **not** be injected into
> `PNAS2017_full_reference`.

## 4. Repository layout

```
references/
  R01_Mavelli2015/          frozen coarse legacy source (paper)
  PNAS2017_Matsuura/        NEW primary benchmark: raw/ + provenance/ (immutable)
models/
  pnas2017_full_reference/  canonical detailed reference SBML: original/ normalized/ audit/
  pure_reduced_core/        future project model (proposal only today)
  literature_reference/     frozen B1 (Mavelli) coarse model — legacy
  fixtures/                 B0 known-answer models and frozen synthetic parameters
configs/               run conditions
schemas/               planned machine-readable schemas
data/                  raw/processed/audit data and provenance (data/provenance.csv)
matlab/
  src/  codegen/  generated/  tests/  tools/    (B0/B1 stack, legacy)
scripts/                user entry points + PNAS audit/ledger/reduction generators
results/
  baselines/  releases/   pnas2017_reference/  runs/
docs/
  pnas2017/                SBML audit, chemical ledger, reference reproduction
  reduction/               reduction map, decisions CSV, human review, candidate core
  visualization/           visualization plan + data contract
  project/  validation/  audit/  theory/   (existing)
frontend/ service/ mcp/ reserved for later stages
```

## 5. Reproduce B1

```bash
matlab -batch "addpath('scripts'); reproduce_b1"
```

B1 ordinary simulation outputs go to `results/runs/<run_id>/`. Frozen
regression data remain under `results/baselines/b1_mavelli2015/`.

## 5b. Regenerate the PNAS 2017 reference audit / ledger / reduction map

These read only the immutable SBML + authors' CSVs and never edit the model:

```bash
python scripts/parse_pnas2017_sbml.py        # species/reactions/parameters/modules + summary
python scripts/build_pnas2017_ledger.py      # species_properties + reaction_balance_audit
python scripts/build_pnas2017_reduction_map.py  # reduction_decisions.csv (candidates only)
```

The Phase-4 integrity run is driven from MATLAB SimBiology/the authors' model;
see `docs/pnas2017/reference_reproduction.md`. Outputs land in
`models/pnas2017_full_reference/audit/`, `docs/reduction/` and
`results/pnas2017_reference/`.

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
