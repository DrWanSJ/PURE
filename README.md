# PURE — Cell-Free Expression Modeling Workbench

This repository studies PURE cell-free expression with explicit model,
source, simulation, audit and decision boundaries. The active detailed
benchmark is the **mRNA-directed translation** network of Matsuura et al.
(PNAS 2017, DOI: [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114)).
Transcription and GUV transport are future project extensions; they are not
part of the imported PNAS reference model.

## Scientific status and model identities

| Identity | Role | Status |
| --- | --- | --- |
| `PNAS2017_full_reference` | Literal, provenance-bound SBML import of the Matsuura et al. translation network; benchmark and inventory only | **Active acquisition and audit**; no scientific modification permitted |
| `PURE_reduced_core` | Future interpretable project model derived from explicit, human-reviewed reduction decisions | **Proposal only**; no validated model yet |
| `Mavelli2015_coarse_reference` | Mavelli, Marangoni and Stano (2015) coarse-grained comparator, DOI: [10.1007/s11538-015-0082-8](https://doi.org/10.1007/s11538-015-0082-8) | **Frozen legacy benchmark**, completed through the previous D7 RS-QSSA work |

As of 2026-09-27, the [G1-PNAS evidence report](docs/pnas2017/g1_pnas_report.md)
is **BLOCKED**: the official author-site SBML and simulator files are frozen,
but the publisher article/SI and Datasets S01–S29 are still unavailable here.
The structural and two-engine numerical checks do not close the missing-source,
chemical-unit or human-review gaps.

The Mavelli benchmark remains valid for its coarse-grained question. It is no
longer the primary benchmark because the revised question requires the
detailed translation reaction network and explicit small-molecule/resource
accounting. The existing Mavelli code and evidence remain in their current
paths. Historical results retain their original scope and acceptance status;
they are not evidence that the new PNAS model or a future reduced core has been
validated. The legacy B1 human source-to-repository audit was completed for
literature reproduction, not independent experimental validation.

The active sequence is: freeze and inventory the original PNAS sources;
validate and execute the unchanged SBML where possible; classify reaction
families and chemical flows; prepare candidate transformations with their
information loss; obtain **human scientific decisions**; then construct and
validate a reduced model. Similar protein output alone is not a deletion
criterion. The proposed reduced core must retain the information needed for
ATP/GTP, AMP/ADP/GDP, Pi/PPi, creatine phosphate/creatine, amino acids,
tRNA charging, translation-machine occupancy and an explicitly qualified
osmotic-particle proxy. Quantitative ionic-strength accounting requires
defined charges, protonation and Mg-binding conventions.

## Repository layout

```text
references/                         source files and provenance
  R01_Mavelli2015/                  legacy literature source
  PNAS2017_Matsuura/                active source acquisition (as available)
models/
  literature_reference/             frozen Mavelli B1 implementation
  pnas2017_full_reference/          immutable import, normalization and audit (as available)
  pure_reduced_core/                future human-reviewed model
  pure_resource_core/               earlier project-model planning material
  fixtures/                         B0 known-answer models
configs/                            run conditions
data/                               raw, processed and audit data
matlab/                             legacy simulation, generated code and tests
results/                            baselines, ordinary runs and release evidence
docs/                               scientific, validation and audit records
```

The PNAS SBML is the scientific source of truth for the detailed benchmark.
Normalized inventories and solver outputs are derived artifacts. A handwritten
MATLAB or Python ODE must not replace the imported reference definition.
Source files are preserved byte-for-byte with URLs, access dates, sizes and
SHA-256 hashes. Missing sources and unsupported solver imports are recorded
as missing or blocked rather than reconstructed from descriptions.

## Legacy Mavelli reproduction

The existing B1 workflow remains available for historical comparison:

```bash
matlab -batch "addpath('scripts'); reproduce_b1"
```

Ordinary B1 outputs go to `results/runs/<run_id>/`; frozen regression data
remain under `results/baselines/b1_mavelli2015/`. Its generated-code chain is

`models/literature_reference/model_definition.json` →
`matlab/codegen/generate_pure_literature_reference.m` →
`matlab/generated/rhs_pure_literature_reference.m`.

Do not edit generated B1 code by hand or reinterpret it as the PNAS model.

## Existing tests and evidence

```bash
matlab -batch "addpath('scripts'); run_all_tests"
```

This is the existing MATLAB suite for B0 fixtures and the Mavelli B1
workflow. Passing it does not validate the new PNAS reference or future
project reduction. Reports must distinguish executed tests, failed or pending
checks, source review, solver integrity and experimental validation.

`data/raw/` and new reference-source directories are immutable inputs.
Processed data must be reproducible from registered sources and tools, with
licensing status recorded. B0 synthetic parameters do not become PURE
experimental inputs. Release preflight requires a clean tree; the only
long-lived branch is `main`, and tags mark frozen states.

The current execution order and **G1-PNAS** gate are in [tasklist.md](tasklist.md).
Future phases include a human-approved `PURE_reduced_core`, transcription
extension, GUV transport, flow visualization and MCP access to audited
computations.
