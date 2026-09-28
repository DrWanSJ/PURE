# PNAS2017 968-row reaction annotation v0

**Status:** provisional machine-assisted annotation; every scientific Level-C assignment remains pending human review.

## Structural result

- 968 directed source reactions are present exactly once.
- 580 non-degradation directed reactions form **290 exact reverse-stoichiometry pairs**. Every pair has one shared primary Level-C label.
- 388 unpaired degradation/inactivation rows are annotated `DEG_sink`.
- Confidence fingerprint: **776 high**, **190 medium**, **2 low** directed rows.
- The only low-confidence pair is `re0000000308` / `re0000000327`: `EFG_GDP + RS50S <=> RS50S_EFG_GDP`, shared by elongation and termination/recycling.

Exact reverse pairing is an **exact representation rewrite candidate** only. It is not evidence for fast equilibrium, QSSA, lumpability, or deletion.

## Level-C distribution

| Level C | directed rows | reversible channels |\n| --- | ---: | ---: |\n| `RS_binding` | 48 | 24 |\n| `RS_activation` | 36 | 18 |\n| `RS_charging` | 20 | 10 |\n| `RS_to_INIT_formylation` | 22 | 11 |\n| `INIT_assembly` | 112 | 56 |\n| `INIT_tRNA_recruitment` | 42 | 21 |\n| `INIT_energy_commitment` | 14 | 7 |\n| `INIT_70S_formation` | 12 | 6 |\n| `INIT_factor_release` | 26 | 13 |\n| `ELONG_aa_tRNA_delivery` | 24 | 12 |\n| `ELONG_energy_coupling` | 50 | 25 |\n| `ELONG_peptide_formation` | 4 | 2 |\n| `ELONG_translocation` | 8 | 4 |\n| `ELONG_tRNA_release` | 4 | 2 |\n| `TERM_factor_binding` | 8 | 4 |\n| `TERM_peptide_release` | 4 | 2 |\n| `TERM_energy_coupling` | 34 | 17 |\n| `RECYCLE_disassembly` | 14 | 7 |\n| `RECYCLE_component_release` | 24 | 12 |\n| `EN_binding` | 54 | 27 |\n| `EN_energy_transfer` | 18 | 9 |\n| `EN_byproduct_processing` | 2 | 1 |\n| `DEG_sink` | 388 | - |\n
## What each row now records

Each of the 968 rows records Level A/Level B provenance, primary Level C plus alternate candidates, rule ID and confidence, CellDesigner reaction type, reactants/products, exact reverse partner, Class-I species touched, protected/reconstructable pools touched, explicit free-resource ledger delta, functional-pool and conservation-family effects, the pre-existing scientific reduction candidate label, and human-review status.

## Human-review status

- `PENDING_HUMAN_REVIEW`: high-confidence first-pass assignment, not human-approved.
- `PENDING_HUMAN_REVIEW_MEDIUM_CONFIDENCE`: neighboring Level-C stage is chemically plausible and should be reviewed before freezing.
- `PRIORITY_HUMAN_REVIEW_SHARED_CHEMISTRY`: shared chemistry crosses macro-process boundaries.

## Recommended review order

1. Review the single low-confidence reversible channel.
2. Review elongation `energy_coupling` vs `translocation` medium-confidence channels.
3. Review initiation `assembly` / `tRNA_recruitment` / `70S_formation` boundaries.
4. Review aminoacylation `activation` vs `binding` product-release channels.
5. Only after review, freeze accepted annotations and use them to define module-specific reduction certificates.

## Boundary

This file does **not** prove QSSA, fast-equilibrium, or kinetic accuracy. It is the reaction information contract layer needed before reduction.
