# Whole-network proposed reduction order

**HUMAN_REVIEW_REQUIRED; every route is PENDING.** This additive map does not supersede prior acceptance records or authorize elimination.

| Source region | Proposed route | Nonhub interface species |
| --- | --- | ---: |
| Aminoacylation_A_Gly | QSSA_AFTER_TOPOLOGY | 8 |
| Aminoacylation_A_Met | QSSA_AFTER_TOPOLOGY | 8 |
| Aminoacylation_B_GlyGCC | QSSA_AFTER_TOPOLOGY | 8 |
| Aminoacylation_B_fMetCAU | QSSA_AFTER_TOPOLOGY | 8 |
| Elongation_A_Gly | QSSA_ONLY | 1 |
| Elongation_A_Met | QSSA_ONLY | 0 |
| Elongation_B | KEEP_EXPLICIT | 2 |
| Elongation_Ca1_GlyGCC | TOPOLOGY_REDUCE_FIRST | 4 |
| Elongation_Ca1_fMetCAU | TOPOLOGY_REDUCE_FIRST | 2 |
| Elongation_Ca2_pept0002 | TOPOLOGY_REDUCE_FIRST | 3 |
| Elongation_Ca2_pept0003 | TOPOLOGY_REDUCE_FIRST | 4 |
| EnergyRegeneration_A | QSSA_AFTER_TOPOLOGY | 0 |
| EnergyRegeneration_B | QSSA_AFTER_TOPOLOGY | 0 |
| EnergyRegeneration_C | QSSA_AFTER_TOPOLOGY | 0 |
| EnergyRegeneration_D | QSSA_AFTER_TOPOLOGY | 0 |
| FMet_tRNASynthesis | QSSA_AFTER_TOPOLOGY | 0 |
| Initiation_A | DO_NOT_TOUCH_YET | 3 |
| Initiation_B1 | DO_NOT_TOUCH_YET | 18 |
| Initiation_B2 | DO_NOT_TOUCH_YET | 15 |
| Initiation_C | DO_NOT_TOUCH_YET | 4 |
| SmallMolecules | KEEP_EXPLICIT | 0 |
| Termination_A_RF1 | KEEP_EXPLICIT | 5 |
| Termination_A_RF2 | KEEP_EXPLICIT | 5 |
| Termination_B_RF1 | KEEP_EXPLICIT | 5 |
| Termination_B_RF2 | KEEP_EXPLICIT | 5 |
| Termination_C | KEEP_EXPLICIT | 2 |

`TOPOLOGY_REDUCE_FIRST`: prototype the two elongation serial subchains and test occupancy/ledger closure. `QSSA_AFTER_TOPOLOGY`: reconsider aaRS/formylation and energy enzyme blocks on the chosen retained coordinates, reusing exact conservation and observable contracts. `QSSA_ONLY`: local aminoacyl-tRNA/factor carrier assembly where no serial-growth simplification was detected. `KEEP_EXPLICIT`: shared resources, factor states with cross-module competition, terminal product and recycling outputs. `DO_NOT_TOUCH_YET`: initiation assembly with unresolved interface/closure choice. These are sequencing proposals, not conclusions that a category will succeed.

The source module counts overlap; do not sum them as disjoint partition sizes. [CSV map](../../results/topology_audit/reduction_map.csv) records exact reactions/species; [interface table](../../results/topology_audit/module_interfaces.csv) records actual coupling. A module label alone never justifies one lumped state. Retain free ATP/GTP/ADP/GDP, amino-acid/aa-tRNA pools, PO4/PPi, ribosome availability and factor coupling in the accounting contract.
