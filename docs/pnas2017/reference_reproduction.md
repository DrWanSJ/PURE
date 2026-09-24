# PNAS 2017 — reference reproduction (integrity benchmark)

**Scope.** This is only an integrity check that the acquired reference files are
complete and runnable, and that they produce the physically expected behaviour.
It is **not** new scientific analysis and does **not** reproduce every figure.
No parameters are refit.

## 1. Engine availability (decisive constraint)

| engine | required role | available? | outcome |
| --- | --- | --- | --- |
| libRoadRunner / Tellurium | **primary SBML execution** | ❌ cannot install (no network) | SBML-standard simulation **not run** |
| MATLAB SimBiology (R2025b) | independent SBML cross-check | ⚠ imports, but lossy (see §3) | SBML-driven reproduction **not trustworthy** |
| authors' MATLAB model (`fMGG_synthesis.m`) + CSVs | shipped reference integrator | ✅ | **RAN** — used as the integrity trajectory (§2) |

Because the SBML is the canonical model but **no faithful SBML engine is
present**, the honest status is: *the reference network runs and behaves as
published (via the authors' own integrator), but the SBML-standard reproduction
gate item is OPEN* pending libRoadRunner/Tellurium. See `MISSING_SOURCES.md`.

## 2. Integrity run — authors' reference model

Run id: `2026-09-24_authors_model_v0`
Command basis: the authors' own driver (`fMGG_synthesis_Sample.m`):
`t = logspace(-4, 3, 200)` s (1e-4 … 1e3 s), `ode15s`, `NonNegative` on all
states, `RelTol = 1e-3`, `AbsTol = 1e-9`; **published** parameter and initial
values loaded from `dat/fMGG_synthesis_parameters.csv` and
`dat/fMGG_synthesis_initial_values.csv`.
Output: `results/pnas2017_reference/2026-09-24_authors_model_v0/authors_model_trajectory.csv`
(200 × 241 states, original species names/ordering).

Terminal / peak values (µM) confirm expected PURE behaviour:

| species | initial | peak | final (t=1e3 s) | reading |
| --- | --- | --- | --- | --- |
| `ATP` | 3750 | 3750 | 3672 | nearly flat → **buffered by CP/CK regeneration** |
| `GTP` | 2500 | 2500 | 2402 | mild consumption (translation uses GTP) |
| `GDP` | 0 | — | 7.93 | GTP-hydrolysis product appears |
| `CP` | 50000 | 50000 | 41720 | creatine-phosphate donor is drawn down |
| `Cr` | 0 | — | 8251 | creatine produced 1:1 with CP → ATP |
| `PO4` | 0 | — | 8375 | large phosphate release (PPi + hydrolysis) |
| `PPi` | 0 | — | 4.81 | pyrophosphate from charging, then PPiase |
| `Gly` | 300 | 300 | 262 | amino-acid incorporation into product |
| `Pept0003` | 0 | 5.16 | 5.16 | **fMGG product formed** |
| `mRNA` | 0.1 | 0.1 | ~7e-5 | template consumed/degraded |
| `RS70S` | 3 | 3 | ~2e-5 | ribosomes sequestered/degraded over the window |

Consistency checks: 241 states and 968 reactions match the audit; 27 nonzero
initial species match the paper; the product (`Pept0003`) rises monotonically
while ATP holds ~constant and CP falls — the signature of the creatine-phosphate
energy-regeneration module. **Result: PASS as an integrity benchmark.**

## 3. What is NOT yet done, and why the SimBiology SBML path was rejected

- **SimBiology SBML import is lossy here**: `sbmlimport` cannot represent
  `stoichiometryMath` (forces stoichiometry = 1, silently wrong for `2 PO4`
  products such as `re0000000414`) and exposes reaction-local `k1` parameters
  in a way that could not be reliably overwritten from the CSV (model-level
  `Parameters` was empty). Injecting published values through the imported SBML
  therefore cannot be trusted → **not used for numbers**.
- **Dataset S28 / S27 numeric comparison**: **not yet performed**. The xlsx
  files are present but `openpyxl` is unavailable; parsing OOXML with the
  standard library is scheduled (see `MISSING_SOURCES.md`). Until then the
  comparison is to the authors' integrator + reported counts, **not** to
  published per-dataset trajectories.
- **Second independent SBML engine** (RoadRunner): **blocked**, cannot install.

## 4. Gate implications

- G1-PNAS item "authoritative source files frozen with checksums" → **met**.
- item "reference network readable through SBML tooling" → **partially met**
  (fully inventoried + a reference integrator runs it; libSBML/RoadRunner not run).
- item "published counts explained" → **met** (241 / 27 / 968 / 26 all confirmed;
  one combined-only orphan reaction `re0000000414` documented in `sbml_audit.md`).
- Quantitative figure-level reproduction → **deferred by design** (explicitly not
  this cycle's goal).
