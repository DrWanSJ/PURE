# PNAS 2017 combined SBML audit

This is a structural and tool-compatibility audit of the **unaltered source file**. It is not reference-trajectory reproduction or a validated reduction. The four CSV inventories below are derived and can be regenerated with `scripts/audit_pnas2017_sbml.py`.

## Inputs and reproducibility

- Combined source: `models/pnas2017_full_reference/original/fMGG_synthesis.xml`; SHA-256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`.
- Subsystem archive: `references/PNAS2017_Matsuura/raw/SBML_files.zip`; SHA-256 `24f0748c883eb6dcb748c20de7fdb2c8e495397f4b8ffb6c82246a03f0a93b03`.
- Parser: python-libsbml 5.21.2.
- Regenerate with CPython 3.12 and python-libsbml 5.21.2: `python scripts/audit_pnas2017_sbml.py` (use `--simbiology skip` where MATLAB is unavailable).
- Output: `models/pnas2017_full_reference/audit/{species,reactions,parameters,modules}.csv` and this report. Original SBML IDs remain in every inventory row.

## SBML inventory

| Field | Observed |
| --- | ---: |
| Model ID | `fMGG_synthesis` |
| SBML level/version | 2/4 |
| Compartments | 1 |
| Species | 241 |
| Reactions | 968 |
| Global parameters | 0 |
| Reaction-local parameters | 968 |
| Explicit unit definitions | 0 |
| Reversible / irreversible reactions | 0 / 968 |
| Reactions with / without kinetic law | 968 / 0 |
| Assignment / rate / algebraic rules | 0 / 0 / 0 |
| Events | 0 |
| Boundary / constant species | 0 / 0 |

Kinetic-law MathML top-level types: `multiplication` 968. These are expression shapes, not mechanistic classifications. No conserved-moiety relationships are declared by the SBML; none is inferred here.

## Published-count comparison and source limitation

The reported 241 components, 968 reactions and 26 subsystems match this combined file and the 26 XML entries in the official subsystem ZIP. The subsystem diagrams contain 1098 reaction entries but 968 distinct stoichiometric reactions; 130 entries repeat a reaction across subsystems. All 968 combined reaction signatures map to at least one ZIP entry when constant `stoichiometryMath` is evaluated; 84 combined reactions appear in multiple ZIP entries. Unmatched ZIP signatures: 0. The ZIP subsystem SBMLs have no kinetic laws, so their 1,098 entries are structural diagrams rather than 1,098 separately executable reactions.

The combined file sets `initialConcentration=1` for **all 241 species**, and `k1=1` for **all 968 reaction-local parameters**. It therefore encodes 241 initially positive species, not the paper's 27 initially present components. The publication's original numerical initial-condition/parameter set is not identified by this SBML. Do not claim an original-parameter fMGG reproduction from this file alone.

## Stoichiometry encoding and engine compatibility

All 3854 combined reactant/product references encode a constant `stoichiometryMath`; 3,853 equal 1 and one equals 2. For `re0000000414`, the product `PO4` has MathML coefficient **2** although `SpeciesReference.getStoichiometry()` returns the default **1**. The matching `EnergyRegeneration_D.xml` source reaction is `re13`. The CSV inventory uses the MathML value and retains its encoding.

- Nonunit MathML coefficient in combined model: `re0000000414`.

### libRoadRunner

- Import status: **success** with libRoadRunner 2.10.0; 241 floating species and 968 reactions. Default integrator: `cvode`. No reference simulation was run here.
- Raw import stoichiometric-matrix differences from the source MathML: **1**.
  - `re0000000414` / `PO4`: source net coefficient 2; imported matrix 1.
- **Status: diagnostic-only raw import.** Direct numerical execution does not preserve the source stoichiometry and cannot serve as a faithful benchmark. A separately verified, mathematically equivalent compatibility copy is required before RoadRunner simulation.

### MATLAB SimBiology

- Import status: **success**; 241 species, 968 reactions, 1 compartments.
- Import emitted 3854 `Stoichiometry Math is not supported ... will be read ... 1` warnings for 3854 source references. The one nonunit coefficient (`re0000000414` → `PO4`: 2) is therefore not preserved. **Status: diagnostic-only raw import; no independent equivalent simulation claim.**
- MATLAB process exit code: 0. A separate stale startup search-path warning (`slanCM`) appeared.
- Reproduce import probe: `matlab -batch "m=sbmlimport('C:/Users/sean/Desktop/PURE/models/pnas2017_full_reference/original/fMGG_synthesis.xml'); fprintf('SIMBIOLOGY_IMPORT_OK species=%d reactions=%d compartments=%d\n',numel(m.Species),numel(m.Reactions),numel(m.Compartments));"`

## Units and libSBML consistency

- The file defines **zero** explicit unit definitions. Its compartment declares the built-in `volume` unit; all 241 species leave `substanceUnits` and `spatialSizeUnits` unset. All 968 local `k1` parameters declare `substance` and all 968 kinetic laws leave substance/time units unset. The implied numerical concentration, time and rate-constant units are therefore not sufficiently documented for a biochemical units claim.
- No charge, protonation or Mg-binding metadata appear in this audit. A solver import cannot validate ionic-strength or osmotic calculations.
- libSBML `checkConsistency()` reported **2904** messages: 0 errors, 0 fatal, 2904 warnings. All message classes are below.

| Severity | Category | Rule ID | Count | Representative message |
| --- | --- | ---: | ---: | --- |
| Warning | SBML unit consistency | 10541 | 968 | The units of the 'math' formula in a <kineticLaw> definition are expected to be the equivalent of _substance per time_. Reference: L2V4 Section 4.13.5 Expected units are mole (exponent = 1, multiplier = 1, scale = 0), second (exponent = -1, multiplier = 1, scale = 0) but the units returned by the... |
| Warning | SBML unit consistency | 99505 | 1936 | In situations where a mathematical expression contains literal numbers or parameters whose units have not been declared, it is not possible to verify accurately the consistency of the units in the expression. The units of the <reaction> <speciesReference> <stoichiometryMath> expression '1' cannot... |

Warnings are not waived. In particular, kinetic-law unit consistency cannot be established from the source declarations. The CSV files and source hash above provide the row-level audit trail; this table aggregates every libSBML message by rule ID and severity.

## Subsystem archive inventory

Each row below is an original XML model ID. Exact combined-reaction memberships (including shared reactions) are in `reactions.csv`; source reaction IDs are preserved there. This is structural mapping only.

| Source file | Original model ID | Species | Reaction entries | Kinetic laws |
| --- | --- | ---: | ---: | ---: |
| `Aminoacylation_A_Gly.xml` | `Aminoacylation_A` | 13 | 25 | 0 |
| `Aminoacylation_A_Met.xml` | `Aminoacylation_A` | 13 | 25 | 0 |
| `Aminoacylation_B_fMetCAU.xml` | `Aminoacylation_B` | 25 | 44 | 0 |
| `Aminoacylation_B_GlyGCC.xml` | `Aminoacylation_B` | 25 | 44 | 0 |
| `Elongation_A_Gly.xml` | `Elongation_A` | 14 | 29 | 0 |
| `Elongation_A_Met.xml` | `Elongation_A` | 14 | 29 | 0 |
| `Elongation_B.xml` | `Elongation_B` | 18 | 40 | 0 |
| `Elongation_Ca1_fMetCAU.xml` | `Elongation_Ca1` | 14 | 12 | 0 |
| `Elongation_Ca1_GlyGCC.xml` | `Elongation_Ca1` | 14 | 12 | 0 |
| `Elongation_Ca2_pept0002.xml` | `Elongation_Ca` | 34 | 61 | 0 |
| `Elongation_Ca2_pept0003.xml` | `Elongation_Ca` | 34 | 61 | 0 |
| `EnergyRegeneration_A.xml` | `EnergyRegeneration_A` | 12 | 25 | 0 |
| `EnergyRegeneration_B.xml` | `EnergyRegeneration_B` | 12 | 25 | 0 |
| `EnergyRegeneration_C.xml` | `EnergyRegeneration_C` | 11 | 25 | 0 |
| `EnergyRegeneration_D.xml` | `EnergyRegeneration_D` | 7 | 12 | 0 |
| `FMet_tRNASynthesis.xml` | `fMet_tRNASynthesis` | 15 | 29 | 0 |
| `Initiation_A.xml` | `Initiation_A` | 8 | 10 | 0 |
| `Initiation_B1.xml` | `Initiation_B1` | 36 | 156 | 0 |
| `Initiation_B2.xml` | `Initiation_B2` | 38 | 110 | 0 |
| `Initiation_C.xml` | `Initiation_C` | 30 | 80 | 0 |
| `SmallMolecules.xml` | `SmallMolecules` | 8 | 12 | 0 |
| `Termination_A_RF1.xml` | `Termination_A` | 17 | 22 | 0 |
| `Termination_A_RF2.xml` | `Termination_A` | 17 | 22 | 0 |
| `Termination_B_RF1.xml` | `Termination_B` | 25 | 51 | 0 |
| `Termination_B_RF2.xml` | `Termination_B` | 25 | 51 | 0 |
| `Termination_C.xml` | `Termination_C` | 31 | 86 | 0 |

## Interpretation boundary

This inventory preserves original SBML species/reaction IDs and subsystem source IDs. It does not select reaction families, delete states, estimate timescales, refit parameters or declare a reduction scientifically acceptable. Such decisions require a separate `HUMAN_REVIEW_REQUIRED` record with explicit material, nucleotide, phosphate, tRNA, osmotic and ionic consequences.
