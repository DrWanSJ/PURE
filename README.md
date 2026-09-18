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

**Status: `bibliography_verified = true`, `equations_verified = true`,
`reproduced = true`** (executed with MATLAB R2025b, `ode15s`; 9/9 tests pass;
all QC passed; curves quantitatively matched to an automated digitization of
the paper's Fig. 4 — [a] panel ≤ 1.8 % everywhere, [nt] panel ≤ 1.3 % of full
scale). Details: [`docs/benchmark_v0.md`](docs/benchmark_v0.md),
[`docs/benchmark_registry.md`](docs/benchmark_registry.md).

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
