# Topology-first motif catalog

All categories are **candidate proposals; HUMAN_REVIEW_REQUIRED=true**. The machine-readable [catalog](../../results/topology_audit/motif_catalog.csv) contains 364 motifs with complete member IDs, view, evidence and required assumptions. Membership is intentionally overlapping.

| Motif type | Structural evidence | Candidate interpretation |
| --- | --- | --- |
| Strict serial chains | One producer + one consumer for each internal state; no external kinetic dependence; acyclic reaction path | AGGREGATE_STATE_CANDIDATE; direct closure requires additional delay/occupancy/ledger evidence |
| Two Gly-addition backbones | Ordered source-supported elongation reactions; repeated factor and bound-nucleotide pattern | AGGREGATE_STATE_CANDIDATE, including return loops; not an unbranched line |
| 290 exact reverse pairs | Exact stoichiometric swap | Signed net-flux rewrite is exact with no state removal; 209 pairs with both author directions positive are only local kinetic/QSSA review candidates |
| Hub-attached motifs | Explicit degree and module membership | KEEP_EXPLICIT resources/machinery unless a validated coordinate reconstruction exists |
| 26 source subnetworks | Exact source signatures + measured external interfaces | Open local submodules; no independent-module claim |

## Detected strict serial paths

- `SERIAL_AUTHOR_NONZERO_001`: re0000000014, re0000000016, re0000000017, re0000000018; internal: elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC, elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC, elRS70SAGGU0002_fMet_GlytRNAGlyGCC.
- `SERIAL_AUTHOR_NONZERO_002`: re0000000075, re0000000077, re0000000078, re0000000079; internal: elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC, elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC, elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC.
- `SERIAL_AUTHOR_NONZERO_003`: re0000000024, re0000000025, re0000000068; internal: elRS70SAGGU0003_Pept0002tRNAGlyGCC, elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP.
- `SERIAL_AUTHOR_NONZERO_004`: re0000000902, re0000000910, re0000000911; internal: termRS30S_mRNA, termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP.
- `SERIAL_AUTHOR_NONZERO_005`: re0000000085, re0000000086; internal: elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP.
- `SERIAL_AUTHOR_NONZERO_006`: re0000000147, re0000000148; internal: GlyAMP.
- `SERIAL_AUTHOR_NONZERO_007`: re0000000172, re0000000173; internal: MetAMP.
- `SERIAL_AUTHOR_NONZERO_008`: re0000000288, re0000000289; internal: EFTu_GTP_MettRNAfMetCAU.
- `SERIAL_AUTHOR_NONZERO_009`: re0000000307, re0000000309; internal: RS70S_EFG_GDP.
- `SERIAL_AUTHOR_NONZERO_010`: re0000000428, re0000000434; internal: MTF_THF.
- `SERIAL_AUTHOR_NONZERO_011`: re0000000430, re0000000432; internal: MTF_fMettRNAfMetCAU.
- `SERIAL_AUTHOR_NONZERO_012`: re0000000842, re0000000847; internal: termRS70SUAA0004_tRNAGlyGCC_RF3_GDP.

First prototype is `re0000000016→re0000000017→re0000000018`. Its two internal states have no author-positive side exits, but the full canonical graph retains multiple side reactions. This supports a **condition-bound candidate**, not source-general deletion. The counterpart `re0000000077→re0000000078→re0000000079` occurs in the second Gly addition.

The actual fMGG network has **two** growth cycles. A long `A→X1→...→B` polymer lattice is an explanatory schematic, not a claim about this file. Each whole elongation backbone also has docking/dissociation/nucleotide return loops; these are reasons to retain occupancy and resource/progress information.

`DIRECT_LUMP_CANDIDATE` appears only as an explicitly derived, unvalidated case-study option, never as a topology-only automatic deletion rule. Topology alone establishes no exact memoryless A→B kinetics. The case study documents its delay and ledger losses. The exact reverse-channel net rewrite is a different operation that preserves all states. No category is copied into `reduction_decisions.csv`.
