# fMGG reference integrity check (2026-09-24)

**Status:** author-input simulation completed in two SBML engines on an explicitly derived compatibility input. This is an integrity and numerical cross-check, not a reduction test or experimental validation. The publisher PDF and Dataset S28 are now preserved as source files, but this run has not been compared pointwise against S28. S28's future gate role remains `OPEN_SCIENTIFIC_DECISION`.

## Inputs and compatibility boundary

The unchanged author [combined SBML](../../models/pnas2017_full_reference/original/fMGG_synthesis.xml) (SHA-256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`) contains 241 species and 968 reactions, but sets **all** initial concentrations and all local `k1` parameters to 1. The author [`Simulate_fMGG_synthesis.zip`](../../references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip) (SHA-256 `beb27ebbd314133fbd83f68dcf8ad2ebe08cb16a1adda170b6b7b408ad355b52`) supplies a 241-row initial-value CSV and 968 named local parameter values (plus one `default` sentinel). The names and order match the original SBML identifiers; the CSV has 27 positive initial components and 483 nonzero `k1` values. Its sample MATLAB script uses `ode15s` and `logspace(-4,3,200)` over 0.0001–1000 s; a nearby script comment says `1e-5`, but the executable expression is `1e-4`.

Both tested engines import the **raw** XML while reading the one nonunit `stoichiometryMath` coefficient incorrectly: `re0000000414` releases `2 PO4` in the source and is imported as `1 PO4`. Direct raw import is diagnostic only. [`run_pnas2017_reference.py`](../../scripts/run_pnas2017_reference.py) uses libSBML to replace each of the 3,854 **literal constant** `stoichiometryMath` entries with its identical numeric `stoichiometry` attribute in a separate [normalized compatibility copy](../../models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml). A full before/after species-reference inventory, roundtrip read, and independent engine matrix checks verify equality, including the `PO4` coefficient 2. No original reaction, species, parameter or stoichiometric value is scientifically changed. The [normalization manifest](../../models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.provenance.json) binds both files and the transformation.

The same script overlays the author's CSV values **only in a derived execution SBML** under [`results/pnas2017_reference/rr_cvode_author_csv_20260924/`](../../results/pnas2017_reference/rr_cvode_author_csv_20260924/run_manifest.json). The raw source and its byte-identical `original/` copy are never edited. This overlay, not the all-one structural SBML, is the numerical input to both engines.

## Solver runs

| Check | libRoadRunner 2.10.0 | MATLAB R2025b SimBiology |
| --- | ---: | ---: |
| Import of derived execution SBML | 241 species / 968 reactions | 241 species / 968 reactions |
| Stoichiometry `re0000000414 → PO4` | 2 | 2 |
| Solver | CVODE, stiff=true | `ode15s` |
| Relative / absolute tolerances | `1e-3` / `1e-9` | `1e-3` / `1e-9`; absolute scaling off |
| Output times | author's 200 logarithmic sample times | 435 adaptive sample times, final time 1000 s |
| Free `Pept0003` at 1000 s | 5.164478733656283 | 5.164582654018584 |
| Minimum recorded species value | −2.52×10⁻¹⁹ | −3.71×10⁻¹² |
| Dimensional-analysis warning status | SBML declarations unresolved | 968 rate-dimension warnings, retained in run log |

`Pept0003` is the released fMGG product ID in the original model; bound peptide intermediates have separate IDs. The tiny negative values were recorded as solver diagnostics, with no clipping. SimBiology's run emitted 968 warnings because rates lacked enough units for a verified concentration/time or substance/time dimension; it assumed substance/time. Neither successful solver run resolves the [unit audit](sbml_audit.md).

The [engine comparison](../../results/pnas2017_reference/rr_cvode_author_csv_20260924/engine_comparison.json) aligns species by original ID and linearly interpolates SimBiology output to the RoadRunner times. Absolute difference at the 1000 s product endpoint is **0.0001039204** in the model's reported concentration scale (about 0.0020% of the RoadRunner endpoint); its maximum interpolated product-trajectory difference is 0.00015243. The largest absolute final difference among 241 states is 0.21354 for `PO4` at about 8,375. This diagnostic has **no preregistered acceptance threshold**. Interpolation, solver error controls, nonnegativity behavior and unresolved unit semantics limit numerical equivalence claims.

The [paper](https://doi.org/10.1073/pnas.1615351114) reports 0.15 amino acids/s/mRNA for the fMGG simulation. A descriptive linear fit to the RoadRunner product between 100 and 1000 s gives approximately 0.160 amino acids/s/mRNA when the author's initial `mRNA=0.1` and three amino acids per released product are used. This is a broad sanity anchor, not a fit, acceptance threshold or replacement for Dataset S28.

## What remains unresolved

- The publisher S27 and S28 attachments are now frozen; S27's attachment format and S28's observable mapping/numeric trajectory still require interpretation and comparison. See the [source record](../../references/PNAS2017_Matsuura/README.md) and [open decisions](../reduction/open_scientific_decisions.md).
- Absolute chemical units are not established by the SBML declarations. The author's CSV has no explicit units; the paper context supports a concentration interpretation but does not repair the SBML unit metadata.
- The paper's MATLAB `NonNegative` option and CVODE/SimBiology numerical constraint behavior have not been proven equivalent. No parameter was refit and no reaction was removed.
- This check does not validate chemical formulas, charge, Mg binding, ionic strength, an osmotic pressure calculation or any proposed `PURE_reduced_core` structure.

**Reproduce:** run `scripts/run_pnas2017_reference.py` in a Python environment with libSBML and libRoadRunner, then `scripts/run_pnas2017_simbiology.m` in MATLAB with SimBiology, then `scripts/compare_pnas2017_engines.py`. The run manifest, exact input/output hashes, full trajectories and warnings are stored with the run.
