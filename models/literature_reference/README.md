# PURE_literature_reference — B1 literature benchmark model

Literal deterministic translation of:

> Mavelli, F., Marangoni, R., Stano, P. (2015).
> *A Simple Protein Synthesis Model for the PURE System Operation.*
> Bulletin of Mathematical Biology **77**, 1185–1212. DOI: 10.1007/s11538-015-0082-8

This model exists **only** as the B1 benchmark (`PURE_literature_reference`).
It is **not** the project working model (`PURE_resource_core`). Nothing was
added, removed, re-fitted, or "improved" relative to the paper.

## Contents

| file | role |
| --- | --- |
| `parameters.json` | single source of truth: Table 1 initial conditions, Table 2 kinetic parameters (central/best estimates), multiplicity factors, derived `K_TL_RNA` |
| `model_manifest.json` | full model card: states, rates, observables, conservation relations, assumptions, disclaimer on stochastic use |
| `README.md` | this file |

## Model summary (paper Sect. 2)

Nine species of the paper map onto **10 dynamic ODE states**
(`NTP, NXP, nt, A, T, AT, a, CP, C, TLcat`, paper Eqs. (20)–(27)) plus fixed
inputs `DNA, TXcat, RScat, ENcat`. Two auxiliary pure integrators
(`D_nt, D_TLcat`) reconstruct the "degradation species" of the paper's
conservation relations Eqs. (15) and (19); they have **no feedback** into any
rate law, so the dynamics of the 10 physical states is exactly the paper's.

Six rate laws, each a literal transcription (paper equation number in the
code comments):

- `V_TX`  Eq. (5)  transcription (TXcat, DNA template, NTP)
- `V_nt_deg` Eq. (6) mRNA decay, pseudo-first-order
- `V_RS`  Eq. (8)  aminoacylation (with the multiplicity factor 2.3·[T])
- `V_TL`  Eq. (10) translation elongation (with 2.3·[AT]; **single**
  rectangular-hyperbolic NTP factor even though each event consumes 2 NTP)
- `V_TL_deg` Eq. (12) TL machinery decay
- `V_EN`  Eq. (14) energy regeneration (CP + NXP → C + NTP)

Units: **time in seconds, all concentrations in µM, rates in µM/s**.
Figures may display hours; CSVs store seconds.

## Observables (paper Sect. 2.5)

- `nt` and `a` are **overall polymerized monomer concentrations** — these are
  the quantities plotted in the paper's Fig. 4 (top: [nt], bottom: [a]).
- molecule concentrations: `[mRNA] = nt/(3L)`, `[protein] = a/L`, `L = 238` (GFP).
- `K_TL_RNA = K_TL_nt/(3L) = 226/714 ≈ 0.3165 µM` (paper Eq. (29)) is a
  **derived QC quantity**, not an 11th independent Michaelis–Menten parameter,
  and is not used in the RHS.

## Simulation (paper Sects. 3–5 conditions)

- `t ∈ [0, 14400] s` (4 h), `ode15s`, `RelTol = 1e-9`, `AbsTol = 1e-12`.
- Fig. 4 DNA conditions: 0.34 / 1.7 / 6.8 nM (0.00034 / 0.0017 / 0.0068 µM).
- No clipping of negative values anywhere; positivity is structurally
  guaranteed by the rate laws (checked in the test suite).

## How to run

```matlab
cd <project root>
runtests('matlab/tests/test_pure_literature_reference.m')   % equation-level suite
matlab -batch "run_fig4_benchmark"                          % full benchmark + figures
```

Single runs:

```matlab
addpath('matlab/generated','matlab/simulate');
out = simulate_pure_literature_reference(0.0068);   % 6.8 nM, 0-4 h
```

## Explicit non-goals / disclaimers

- The effective Michaelis–Menten rate laws must **not** automatically be
  interpreted as validated stochastic propensity functions (paper designs
  the model for negligible intrinsic stochasticity; SSA use is forbidden
  without separate validation per the project tasklist).
- PPi hydrolysis (paper Eq. (3)) is not integrated; GFP maturation is omitted
  (paper Sect. 2.3); TLcat is a fictitious effective catalyst (paper Sect. 2.3).
- No refitting, no Hill coefficients, no ATP/GTP splitting, no extra
  ribosome states, no maturation reaction — any such change creates a new
  model version, not this benchmark.
