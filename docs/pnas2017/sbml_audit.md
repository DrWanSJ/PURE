# PNAS 2017 — SBML audit of `PNAS2017_full_reference`

Source of truth: **SBML**. The canonical detailed reference model is the
combined SBML `models/pnas2017_full_reference/original/fMGG_synthesis.xml`
(model id `fMGG_synthesis`). A hand-written `rhs.m` / Python ODE is **not** the
canonical model; the authors' MATLAB file is retained only as an execution
cross-check (see `reference_reproduction.md`).

Inventory was produced by `scripts/parse_pnas2017_sbml.py` from the raw SBML
and the authors' `dat/` CSVs, and exported unchanged (original SBML ids
preserved in every row) to:

- `models/pnas2017_full_reference/audit/species.csv`
- `models/pnas2017_full_reference/audit/reactions.csv`
- `models/pnas2017_full_reference/audit/parameters.csv`
- `models/pnas2017_full_reference/audit/modules.csv`
- `models/pnas2017_full_reference/audit/inventory_summary.json`

## 1. Headline inventory (matches published counts)

| property | value | published / expected | status |
| --- | --- | --- | --- |
| SBML level/version | 2 / 4 | — | — |
| model id | `fMGG_synthesis` | — | — |
| compartments | **1** (`default`, size 1, units volume) | — | — |
| species (components) | **241** | 241 | ✅ match |
| species initially present (nonzero author value) | **27** | 27 | ✅ match |
| reactions | **968** | 968 | ✅ match |
| reaction-local kinetic parameters | **968** (one `k1` per reaction) | — | see §4 |
| model-level (global) parameters | **0** | — | — |
| rules (assignment/rate/algebraic) | **0** | — | none present |
| events | **0** | — | none present |
| unit definitions | **0** | — | ⚠ none declared |
| subsystem SBML files | **26** | 26 | ✅ match |

## 2. Kinetic laws & reversibility

- **All 968 reactions are `reversible="false"` and `fast="false"`** (SBML
  attribute counts: `false|false → 968`).
- **Every** `kineticLaw` has the same structural form: a single `apply/times`
  mass-action product `k1 * <reactant> * <reactant> ...` (no custom laws, no
  Michaelis–Menten helpers). Family split: 702 unimolecular-mass-action, 266
  bimolecular-mass-action.
- Reversibility is expressed **structurally**: 290 reversible steps are encoded
  as **580** forward+reverse irreversible reactions (see the reduction map).
  An SBML "reversible=0" reading would wrongly suggest no reversible chemistry.
- Every `speciesReference` uses `<stoichiometryMath>` (not a literal
  `stoichiometry` attribute). This is legal SBML L2 but see §6 for a tooling
  consequence.

## 3. Conservation / boundary species

- `boundaryCondition` = false and `constant` = false for all 241 species →
  **no SBML-declared boundary or constant species**; the closed model treats
  everything as dynamic. Chemostat/boundary behaviour is therefore a modelling
  *choice we may add*, not something the reference encodes.
- No SBO terms, no model annotations, no `<group>` elements — so **module
  membership is not machine-labelled in the combined SBML**; it is recovered
  from the 26 subsystem files (§5).

## 4. ⚠ Numeric parameter values in the SBML are PLACEHOLDERS

The SBML ships with **every kinetic parameter as `value="1" units="substance"`**
(959 of 968 are exactly `1` while the published value differs). **The SBML
therefore does not carry the numeric parameter set.** The real numbers are in
the authors' export:

| artefact | where | what |
| --- | --- | --- |
| SBML | `fMGG_synthesis.xml` kineticLaw params | `k1 = 1` (placeholder) |
| authors' parameters | `.../dat/fMGG_synthesis_parameters.csv` (969 rows) | real `<rxnid>_k1` values |
| authors' initial values | `.../dat/fMGG_synthesis_initial_values.csv` (241 rows) | real concentrations (µM) |
| SBML species initial | `fMGG_synthesis.xml` | `initialConcentration="1"` (placeholder) |

`audit/parameters.csv` records **both** `sbml_value` and `author_export_value`
plus a `value_is_placeholder` flag per parameter. **Any solver run on the raw
SBML (ignoring the CSVs) would simulate an all-ones toy model, not the paper.**
This must be remembered for Phase 4 and for the future reduced core.

## 5. Module / subsystem mapping (Level B)

Subsystem files use local reaction ids (`re1`, `re12`, …) that do **not** match
the combined ids (`re0000000001`…). Species ids **are** shared, so reactions were
mapped back to the combined model by `(reactants, products)` **content
signature**; the 968 combined signatures are unique. Result:

- subsystem reactions sum to **1098** (> 968) because the 26 subsystems
  **overlap** (shared steps appear in several files).
- **967 / 968** combined reactions map to ≥1 subsystem file.
- **1 combined reaction is orphaned**: `re0000000414`
  (`PPiase_PO4_PO4 → PPiase_degraded + 2 PO4`) exists in the combined model but
  in **none** of the 26 published subsystem files. This is a genuine,
  documented discrepancy (not an artefact of the matcher). Per-module counts are
  in `audit/modules.csv`.

## 6. ⚠ Unit / metadata audit (do not trust the solver to "just work")

- **0 `unitDefinition`s.** Kinetic parameters declare `units="substance"`,
  species use concentration, compartment `size="1"` with `units="volume"` but
  **no explicit scale** (e.g. µM vs M) is declared anywhere.
- The authors' simulation runs on the raw CSV numbers (µM-scale magnitudes:
  GTP 2500, ATP 3750, CP 50000) with **no unit conversion**, so effective units
  are "as-written" and the time base is **seconds** (`logspace(-4,3)` in the
  driver). Rate-constant dimensions are **implicit** per reaction order
  (unimolecular s⁻¹, bimolecular µM⁻¹·s⁻¹) and are **not** encoded in SBML.
- Consequence: no unit system is machine-checkable here. Any osmotic /
  ionic / moiety arithmetic downstream must fix and document its own unit
  convention explicitly (see `chemical_ledger.md`).

## 7. Validation status (per tool)

| tool | role | status |
| --- | --- | --- |
| libSBML | syntax + consistency validation, official warning list | **NOT RUN** — libSBML not installable (no network). See `MISSING_SOURCES.md`. |
| Python `xml.etree` (this repo) | structural inventory | **RAN** — full inventory above; this is *not* a substitute for libSBML's semantic checks. |
| libRoadRunner / Tellurium | primary SBML numerical execution | **NOT RUN** — not installable (no network). No import status available. |
| MATLAB SimBiology (R2025b) | independent import/execution cross-check | **IMPORT RAN** (241/968/1, 0 rules, 0 events) with **stoichiometryMath dropped to 1** and **kinetic parameters not exposed as settable model parameters** — see `reference_reproduction.md`. |

### Import warnings captured (SimBiology)
`sbmlimport` emitted "Stoichiometry Math is not supported for species … will be
read in with a stoichiometry of 1" for the affected `speciesReference`s (e.g. the
`2 PO4` products such as `re0000000414`, and reactions from re…953 onward).
Any SimBiology-based result silently under-counts those stoichiometries.

## 8. What this audit does **not** claim

- It does **not** assert the SBML is libSBML-consistent (not run).
- It does **not** assert the SBML reproduces the published figures (needs a
  real SBML engine + parsed Datasets — see `reference_reproduction.md`,
  `MISSING_SOURCES.md`).
- It does **not** reduce, relabel or reinterpret any reaction; classification is
  candidate-only downstream.
