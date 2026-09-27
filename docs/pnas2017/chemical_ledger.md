# PNAS 2017 chemical and resource ledger (candidate annotation)

**Source and scope.** `models/pnas2017_full_reference/original/fMGG_synthesis.xml` is the unchanged SBML reaction network; the authors' `Simulate_fMGG_synthesis.zip` contains the reference initial-value and parameter CSVs. The derived tables are [`species_properties.csv`](../../models/pnas2017_full_reference/audit/species_properties.csv) (241 rows) and [`reaction_balance_audit.csv`](../../models/pnas2017_full_reference/audit/reaction_balance_audit.csv) (968 rows). `scripts/build_pnas2017_resource_map.py` regenerates them, and `resource_map_manifest.json` binds input/output bytes with SHA-256. These tables are navigation and bookkeeping aids, **not** chemical source authority or an accepted reduced model.

The combined SBML gives all 241 species `initialConcentration=1` and each reaction a local `k1=1`; those literal values are not the fMGG reference conditions. The author simulator's initial CSV has 241 matching SBML IDs, of which exactly 27 have positive initial values. Its parameter CSV supplies 968 `reaction_id_k1` values. The CSVs omit explicit unit metadata; the concentration interpretation as µM is inferred from the paper's concentration examples (including the 50 mM creatine-phosphate condition corresponding to 50,000 in the CSV), **not** from the SBML unit definitions. Unit conversion and solver semantics require a separate audit.

## What each species row records

Each row retains the original SBML ID/name, compartment, SBML placeholder initial value, author-CSV reference initial value, boundary/constant flags, and candidate Level A/B module membership derived from reaction participation. A molecule-class label and 17 resource/category flags are supplied for browsing. A `true` ATP/ADP/AMP/GTP/GDP/Pi/PPi/CP/Cr flag means the **free species ID equals** the named resource; it does not imply that the resource is absent from complexes. Categories inferred from ID patterns are tagged `INFERRED_FROM_ID` or `AMBIGUOUS` and need biochemical review. The original author IDs remain available for correcting the annotation without changing the SBML.

| Resource question | Explicit free SBML IDs or states | Remaining accounting work |
| --- | --- | --- |
| Adenylates | `ATP`, `ADP`, `AMP`; enzyme-bound forms such as `CK_ATP`, `MK_ATP_AMP`, `GlyRS_GlyAMP` | Define adenylate/activation moieties in every complex and intermediate before claiming total-carrier conservation. |
| Guanylates and phosphate | `GTP`, `GDP`, `GMP`, `PO4` (the model's Pi ID), `PPi` | Include factor-bound GTP/GDP/Pi; determine phosphate and protonation bookkeeping. |
| Regeneration fuel | `CP`, `Cr`, `CK`, `NDK`, `MK`, `PPiase` and their complexes | Record creatine-phosphate transfer, nucleotide exchange and pyrophosphate hydrolysis with all bound states. |
| Amino acids and tRNA | `Gly`, `Met`, `fMet`, `tRNAGlyGCC`, `tRNAfMetCAU`, `GlytRNAGlyGCC`, `MettRNAfMetCAU`, `fMettRNAfMetCAU` | Resolve aminoacyl-adenylates, formyl donor, peptide incorporation and all enzyme/ribosome-bound tRNA states. |
| Translation machinery | 30S/50S/70S species and many initiation, elongation and termination complexes | Derive occupancy pools and conservation laws; do not interpret free-ribosome concentration as total capacity. |
| Product | `Pept0002`, `Pept0003` and bound/complex forms | Verify which states belong in the published fMGG observable and whether release/degradation changes the readout. |

## What each reaction row records

For every combined-SBML reaction, the row stores the original reaction ID, reactant/product stoichiometry as JSON keyed by original species IDs, original-module candidate IDs, the author-CSV parameter ID/value, and event-level changes in each **free** carrier or resource listed above. This is enough to construct a stoichiometric matrix, inspect free ATP/GTP, AMP/ADP/GDP, Pi/PPi, CP/Cr, amino-acid and tRNA exchange, and later attach vetted moiety/formula vectors. It is **not yet** a balanced elemental or total-carrier ledger: complexes and aminoacyl-adenylates have no authoritative composition vectors in the acquired SBML.

`net_tracked_particle_count_per_event = Σν_products − Σν_reactants` is a stoichiometric **ideal-particle proxy** over represented species. `net_explicit_free_small_solute_count_per_event` counts only the named free small solutes; it omits bound resources and unmodeled salts. Neither is a measured osmolarity or validated osmotic pressure. If a future simulation supplies concentration trajectories `c_i(t)` with consistent units and an agreed particle scope, an ideal osmolarity proxy can be evaluated as `Σ c_i(t)` over that scope. A pressure calculation would additionally need temperature, activity/osmotic coefficients and an explicit solvent/compartment convention.

No molecular formula, formal charge, protonation state, Mg-binding state, or corresponding authoritative provenance was encoded in the acquired combined SBML. The formula/charge cells are intentionally blank. Consequently **no quantitative ionic-strength number is published**. Only after charge conventions and concentrations are supplied for a declared subset may the conditional expression `I_subset = 0.5 × Σ c_i z_i²` be evaluated for that subset; it must be named a partial inventory and cannot stand in for full-buffer ionic strength.

## Audit status and human review

- `EXTRACTED`: species/reaction IDs, stoichiometry (including `stoichiometryMath`), SBML flags, and the author-CSV values.
- `INFERRED`: broad molecule classes, functional participation, and candidate reaction families from source names/structure.
- `AMBIGUOUS`: 84 combined reactions appear by identical stoichiometry in more than one of the 26 original module files; the reaction stays one combined-SBML event. These are shared module attributions, not 84 extra reactions.
- `UNRESOLVED`: formulas, charge/Mg/protonation, complete bound-carrier moieties, osmotic calibration, and whether approximate occupancy pools remain reconstructable under any proposed lumping.

`HUMAN_REVIEW_REQUIRED` applies to the inferred classes and all scientific reduction choices. A zero reference parameter or an unchanged peptide curve alone does not establish that a reaction may be removed for other conditions or for material/particle accounting.
