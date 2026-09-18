# PURE — Cell-Free Expression Modeling Workbench

CRN modeling workbench for the PURE transcription–translation system
(synthetic-cell platform project). This repository currently contains the
**B1 literature benchmark**: a literal, equation-by-equation reproduction of

> Mavelli, F., Marangoni, R., Stano, P. (2015).
> *A Simple Protein Synthesis Model for the PURE System Operation.*
> Bulletin of Mathematical Biology **77**, 1185–1212.
> DOI: [10.1007/s11538-015-0082-8](https://doi.org/10.1007/s11538-015-0082-8)

as the model `PURE_literature_reference` (deterministic, 10 ODE states,
6 Michaelis–Menten rate laws, 16 kinetic parameters; time in s,
concentrations in µM).

**Status (evidence levels, see `docs/evidence_levels.json`):**
`bibliography_verified = true`, `equations_transcribed = true`,
`equation_level_tests_passed = true` (AI-written tests — **not** human scientific review),
`numerical_solver_qc_passed = true`, `paper_text_anchor_match = true`,
`fig4_simulation_assisted_digitization_match = true` (**`non_independent_assignment`** —
not usable as independent evidence),
`fig4_independent_human_audit = pending_human_audit`,
`experimental_data_validation = false` (no machine-readable Stögbauer 2012 data).
**The repo is in engineering/audit hardening; the scientific human audit is pending.**

## Repository layout

```
models/literature_reference/   model manifest + parameters.json (single source of truth)
matlab/generated/              ODE right-hand side + parameter loader (literal translation)
matlab/simulate/               simulator, Fig.4 benchmark, Fig.4 raster digitizer
matlab/tests/                  equation-level test suite (9 tests)
data/                          provenance ledger; raw Fig.4 page render; digitized curves
results/literature_reference/  trajectories, rates, qc.json per DNA condition, figures
docs/                          benchmark registry + execution/QC report
environment_lock.md            locked environment and source hashes
```

## Reproduce

```bash
# tests (equation-level verification)
matlab -batch "r = runtests('matlab/tests/test_pure_literature_reference.m'); assert(all([r.Passed]))"
# full benchmark: three DNA conditions (0.34 / 1.7 / 6.8 nM), 0-4 h
matlab -batch "addpath('matlab/simulate','matlab/generated','matlab/provenance'); run_fig4_benchmark"
```

New runs write `results/<run_id>/` with `manifest.json` (live git commit,
dirty-tree status, SHA-256 of model definition / parameters / inputs).

## Results: legacy vs provenance-bound (read before citing numbers)

| location | status | meaning |
| --- | --- | --- |
| `results/literature_reference/` | `provenance_status = "legacy_unbound_to_execution_commit"` | AI-baseline results produced **before** the provenance system existed (session records point to commit `ee3dedc`; NOT cryptographically bound). Numerical values are frozen and untouched. |
| `results/<run_id>/` (new runs) | `provenance_status = "provenance_bound"`, `manifest.json` present | git commit read live via `git rev-parse HEAD` at run time, live dirty-tree check, SHA-256 hashes of model definition, parameter file and run inputs. |

Legacy results are never overwritten and never back-filled with execution
provenance that cannot be proven.

## Scope statement

This benchmark model is a **literal literature reference**. Its effective
Michaelis–Menten rate laws must not be read as validated stochastic propensity
functions, and nothing here is the project's working model
(`PURE_resource_core`): no parameters were refitted, no mechanisms added.

## Project status (honest, 2026-09-18)

> **PURE_literature_reference B1 benchmark: engineering/audit hardening in
> progress; scientific human audit pending.**

What exists: locked sources, literal equation transcription, a real
single-source code-generation chain, an equation-level test suite (AI-written,
18/18 passing, logs in `logs/`), provenance-bound run manifests, preflight
guards, and executed benchmark runs with QC.

What this is **not** (none of these claims may be made yet):

- **not human-verified** — no human scientific audit of the transcription,
  the tests, or the Fig. 4 digitization has been performed
  (`docs/audit_status.md`, `docs/mutation_test_protocol.md`,
  `docs/manual_fig4_audit_protocol.md` define the pending human work);
- **not experimentally validated** — no machine-readable Stögbauer 2012 data
  exist here; `experimental_data_validation = false`;
- **not "fully reproduced"** in a strong sense — the Fig. 4 raster
  digitization match is simulation-assisted (`non_independent_assignment`)
  and counts only as an envelope check; the independent evidence so far is
  the paper-text anchor match;
- the following tasklist items have **not been started**: PURE_resource_core,
  nondimensionalization, QSSA/reduction, stability analysis, flow frontend,
  SSA, MCP. CI is a draft and `not_verified`.
