# PNAS 2017 reaction-family reduction map — candidate labels only

**Canonical source:** Matsuura et al., DOI `10.1073/pnas.1615351114`, unchanged combined SBML `fMGG_synthesis.xml`. This map is derived navigation, not a reduced model or a scientific acceptance decision. Every proposed non-KEEP row is `HUMAN_REVIEW_REQUIRED=true` and `decision_status=PENDING` in [`reduction_decisions.csv`](reduction_decisions.csv).

## Coverage and interpretation

- Level A: initiation; elongation; aminoacylation (including initiator formylation); termination/ribosome recycling; energy regeneration (including the shared SmallMolecules source card). Cross-process appearances are retained as multiple candidate memberships, not extra reactions.
- Level B: all 26 original SBML subsystem files. They contain 1,098 reaction *entries*; after collapsing exact stoichiometric duplicates across diagrams, 968 unique signatures match all 968 combined-SBML reactions. Exactly 884 combined reactions map to one subsystem and 84 map to more than one. Original subsystem-local IDs are recorded beside the combined IDs in the CSV.
- Level C: biochemical process plus original CellDesigner reaction type. Across the combined model: DISSOCIATION 266, HETERODIMER_ASSOCIATION 266, STATE_TRANSITION 436. Reaction types describe graph structure; they are not evidence of fast equilibrium or QSSA.
- Candidate labels: DROP_CANDIDATE 388, KEEP 202, LUMP_CANDIDATE 378. `DROP_CANDIDATE` is reserved here for degradation-related reactions whose official fMGG parameter is exactly zero; it is conditional on that reference condition and does not authorize deletion. `LUMP_CANDIDATE` marks nondegradation association/dissociation/state transitions without a direct free-resource delta. Resource/peptide steps are provisionally `KEEP`. No QSSA, fast-equilibrium or chemostat claim is made without time-scale, reconstruction and chemical-ledger evidence.
- The original combined SBML stores one `PO4` product coefficient as MathML 2 in `re0000000414`; inventories use the effective value 2. The exact source mapping is `EnergyRegeneration_D.xml/re13`. Raw RoadRunner/SimBiology imports read it as 1, so use the separately verified compatibility copy for numerical work.

## Original 26 subsystems

| Level A | Original subsystem file / model ID | Source entries | Combined IDs in subsystem | Level C reaction types |
| --- | --- | ---: | ---: | --- |
| aminoacylation | `Aminoacylation_A_Gly.xml` / `Aminoacylation_A` | 25 | 25 | DISSOCIATION 8, HETERODIMER_ASSOCIATION 8, STATE_TRANSITION 9 |
| aminoacylation | `Aminoacylation_A_Met.xml` / `Aminoacylation_A` | 25 | 25 | DISSOCIATION 8, HETERODIMER_ASSOCIATION 8, STATE_TRANSITION 9 |
| aminoacylation | `Aminoacylation_B_fMetCAU.xml` / `Aminoacylation_B` | 44 | 44 | DISSOCIATION 15, HETERODIMER_ASSOCIATION 15, STATE_TRANSITION 14 |
| aminoacylation | `Aminoacylation_B_GlyGCC.xml` / `Aminoacylation_B` | 44 | 44 | DISSOCIATION 15, HETERODIMER_ASSOCIATION 15, STATE_TRANSITION 14 |
| elongation | `Elongation_A_Gly.xml` / `Elongation_A` | 29 | 29 | DISSOCIATION 8, HETERODIMER_ASSOCIATION 8, STATE_TRANSITION 13 |
| elongation | `Elongation_A_Met.xml` / `Elongation_A` | 29 | 29 | DISSOCIATION 8, HETERODIMER_ASSOCIATION 8, STATE_TRANSITION 13 |
| elongation | `Elongation_B.xml` / `Elongation_B` | 40 | 40 | DISSOCIATION 8, HETERODIMER_ASSOCIATION 8, STATE_TRANSITION 24 |
| elongation | `Elongation_Ca1_fMetCAU.xml` / `Elongation_Ca1` | 12 | 12 | DISSOCIATION 1, HETERODIMER_ASSOCIATION 1, STATE_TRANSITION 10 |
| elongation | `Elongation_Ca1_GlyGCC.xml` / `Elongation_Ca1` | 12 | 12 | DISSOCIATION 1, HETERODIMER_ASSOCIATION 1, STATE_TRANSITION 10 |
| elongation | `Elongation_Ca2_pept0002.xml` / `Elongation_Ca` | 61 | 61 | DISSOCIATION 9, HETERODIMER_ASSOCIATION 9, STATE_TRANSITION 43 |
| elongation | `Elongation_Ca2_pept0003.xml` / `Elongation_Ca` | 61 | 61 | DISSOCIATION 9, HETERODIMER_ASSOCIATION 9, STATE_TRANSITION 43 |
| energy regeneration | `EnergyRegeneration_A.xml` / `EnergyRegeneration_A` | 25 | 25 | DISSOCIATION 8, HETERODIMER_ASSOCIATION 8, STATE_TRANSITION 9 |
| energy regeneration | `EnergyRegeneration_B.xml` / `EnergyRegeneration_B` | 25 | 25 | DISSOCIATION 8, HETERODIMER_ASSOCIATION 8, STATE_TRANSITION 9 |
| energy regeneration | `EnergyRegeneration_C.xml` / `EnergyRegeneration_C` | 25 | 25 | DISSOCIATION 8, HETERODIMER_ASSOCIATION 8, STATE_TRANSITION 9 |
| energy regeneration | `EnergyRegeneration_D.xml` / `EnergyRegeneration_D` | 12 | 12 | DISSOCIATION 3, HETERODIMER_ASSOCIATION 3, STATE_TRANSITION 6 |
| aminoacylation | `FMet_tRNASynthesis.xml` / `fMet_tRNASynthesis` | 29 | 29 | DISSOCIATION 9, HETERODIMER_ASSOCIATION 9, STATE_TRANSITION 11 |
| initiation | `Initiation_A.xml` / `Initiation_A` | 10 | 10 | DISSOCIATION 3, HETERODIMER_ASSOCIATION 3, STATE_TRANSITION 4 |
| initiation | `Initiation_B1.xml` / `Initiation_B1` | 156 | 156 | DISSOCIATION 43, HETERODIMER_ASSOCIATION 43, STATE_TRANSITION 70 |
| initiation | `Initiation_B2.xml` / `Initiation_B2` | 110 | 110 | DISSOCIATION 40, HETERODIMER_ASSOCIATION 40, STATE_TRANSITION 30 |
| initiation | `Initiation_C.xml` / `Initiation_C` | 80 | 80 | DISSOCIATION 16, HETERODIMER_ASSOCIATION 16, STATE_TRANSITION 48 |
| energy regeneration | `SmallMolecules.xml` / `SmallMolecules` | 12 | 12 | DISSOCIATION 6, HETERODIMER_ASSOCIATION 6 |
| termination / ribosome recycling | `Termination_A_RF1.xml` / `Termination_A` | 22 | 22 | DISSOCIATION 3, HETERODIMER_ASSOCIATION 3, STATE_TRANSITION 16 |
| termination / ribosome recycling | `Termination_A_RF2.xml` / `Termination_A` | 22 | 22 | DISSOCIATION 3, HETERODIMER_ASSOCIATION 3, STATE_TRANSITION 16 |
| termination / ribosome recycling | `Termination_B_RF1.xml` / `Termination_B` | 51 | 51 | DISSOCIATION 10, HETERODIMER_ASSOCIATION 10, STATE_TRANSITION 31 |
| termination / ribosome recycling | `Termination_B_RF2.xml` / `Termination_B` | 51 | 51 | DISSOCIATION 10, HETERODIMER_ASSOCIATION 10, STATE_TRANSITION 31 |
| termination / ribosome recycling | `Termination_C.xml` / `Termination_C` | 86 | 86 | DISSOCIATION 19, HETERODIMER_ASSOCIATION 19, STATE_TRANSITION 48 |

## How to evaluate a transformation

For each original combined reaction, the decision CSV exposes reactant/product IDs and stoichiometry, official author-CSV `k1`, suggested label and assumption, evidence gap, effects on free ATP/GTP/AMP/ADP/GDP, Pi/PPi, tRNA, ideal-particle proxy, unknown ionic contribution and observables that may be lost. The [`reaction_balance_audit.csv`](../../models/pnas2017_full_reference/audit/reaction_balance_audit.csv) retains the full event-level resource deltas. Formula, net charge, protonation and Mg-binding information remain unresolved, so neither elemental balance nor quantitative ionic strength can be certified.

The candidate label is not a command to change the model. The human researcher must examine the [process review](human_reduction_review.md), supply validation data and approve or reject each scientific transformation. Similar peptide output cannot replace resource, occupancy, particle and moiety checks.
