# B1-2 original-source interpretation appendix

Read-only inspection of local article pages 2, 7, 8 and original S05-S11/S27 workbooks. Canonical SBML/author CSV retains priority. Sources were never saved or altered.

## Author definitions and scientific boundaries

S27 explicitly calls E2 and the second-round entry virtual elongation complexes. Exact equations are author-model structure, not complete physiological steps.

S27 calls factor-free T_pre an elongation complex at stop codon; RF1/RF2-bound states are named pre-termination complexes. T_pre is a proposed structural interface label, pending H6.

The author-defined phrase and molecular interpretation are distinct: author definitions are EXTRACTED, full composition and physiological identity remain INFERRED/UNRESOLVED. The proposed T_pre label is not substituted by a release-factor-bound endpoint.

## Relevant S27 source definitions

| Source species | S27 row | Author model definition | Initial uM |
|---|---:|---|---:|
| `elRS70SAGGU0002_fMettRNAfMetCAU` | 5 | a post-initiation complex with fMet-tRNAfMetCAU at the P site and GGU codon (a second codon in the ORF) at the A site | 0 |
| `elRS70SAGGU0002_fMet` | 6 | a virtual elongation complex with formylmethionine at the P site and GGU codon (a second codon in the ORF) at the A site | 0 |
| `PO4` | 16 | phosphate | 0 |
| `EFTu_GTP_GlytRNAGlyGCC` | 17 | a complex composed of EF-Tu, GTP, and Gly-tRNAGlyGCC | 0 |
| `EFG_GTP` | 19 | a complex composed of EF-G and GTP | 0 |
| `EFG_GDP` | 20 | a complex composed of EF-G and GDP | 0 |
| `elRS70SAGGU0003_Pept0002tRNAGlyGCC` | 21 | an elongation complex with fMet-Gly-tRNAGlyGCC at the P site and GGU codon (a third codon in the ORF) at the A site | 0 |
| `EFTu_GDP` | 26 | a complex composed of EF-Tu and GDP | 0 |
| `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | 32 | an elongation complex, in which EF-Tu complex with Gly-tRNAGlyGCC and GTP is bound to the A site of No. 5 complex  | 0 |
| `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` | 33 | an elongation complex, just after GTP is hydrolyzed in No. 31 complex | 0 |
| `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` | 34 | an elongation complex, after phosphate is dissociated from No. 32 complex | 0 |
| `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | 36 | an elongation complex, after EF-Tu complex with GDP is dissociated from No. 33 complex | 0 |
| `elRS70SBGGU0002_Pept0002tRNAGlyGCC` | 37 | an elongation complex after the peptidyltransfer reaction in No. 35 complex | 0 |
| `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP` | 38 | an elongation complex, in which EF-G complex with GTP is bound to No. 36 complex | 0 |
| `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4` | 39 | an elongation complex, just after GTP is hydrolyzed in No. 37 complex | 0 |
| `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP` | 40 | an elongation complex, after phosphate is dissociated from No. 38 complex and the following tranlocation | 0 |
| `tRNAGlyGCC` | 41 | tRNAGlyGCC | 3.5476718403547673 |
| `elRS70SAGGU0003_Pept0002` | 43 | a virtual elongation complex with fMet-Gly at the P site and GGU codon (a third codon in the ORF) at the A site | 0 |
| `elRS70SAUAA0004_Pept0003tRNAGlyGCC` | 46 | an elongation complex with fMet-Gly-Gly-tRNAGlyGCC at the P site and UAA codon (stop codon in the ORF) at the A site | 0 |
| `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` | 49 | an elongation complex, in which EF-Tu complex with Gly-tRNAGlyGCC and GTP is bound to the A site of No. 42 complex  | 0 |
| `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC` | 50 | an elongation complex, just after GTP is hydrolyzed in No. 48 complex | 0 |
| `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` | 51 | an elongation complex, after phosphate is dissociated from No. 49 complex | 0 |
| `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` | 53 | an elongation complex, after EF-Tu complex with GDP is dissociated from No. 50 complex | 0 |
| `elRS70SBGGU0003_Pept0003tRNAGlyGCC` | 54 | an elongation complex after the peptidyltransfer reaction in No. 52 complex | 0 |
| `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP` | 55 | an elongation complex, in which EF-G complex with GTP is bound to No. 53 complex | 0 |
| `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4` | 56 | an elongation complex, just after GTP is hydrolyzed in No. 54 complex | 0 |
| `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP` | 57 | an elongation complex, after phosphate is dissociated from No. 55 complex and the following tranlocation | 0 |

## Reaction notes and assumptions

| Original ID | S27 row | Author note | Reference no. | Parameter agreement |
|---|---:|---|---|---|
| re0000000001 | 2 | assumed to be a fast reaction | n/a | True |
| re0000000002 | 3 | assumed to be an irreversible reaction | n/a | True |
| re0000000013 | 14 |  | 1 | True |
| re0000000014 | 15 |  | 1 | True |
| re0000000015 | 16 | assumed to be an irreversible reaction | 1 | True |
| re0000000016 | 17 | assumed to be a fast reaction | 1 | True |
| re0000000017 | 18 |  | 1 | True |
| re0000000018 | 19 | assumed to be a fast reaction | 1 | True |
| re0000000019 | 20 |  | 2 | True |
| re0000000020 | 21 |  | 2 | True |
| re0000000021 | 22 |  | 1 | True |
| re0000000022 | 23 |  | 2 | True |
| re0000000023 | 24 |  | 2 | True |
| re0000000024 | 25 |  | 2 | True |
| re0000000025 | 26 | assumed to be a fast reaction | 2 | True |
| re0000000060 | 61 | assumed to be an irreversible reaction | 1 | True |
| re0000000061 | 62 | assumed to be an irreversible reaction | 1 | True |
| re0000000062 | 63 | assumed to be an irreversible reaction | 1 | True |
| re0000000066 | 67 | assumed to be an irreversible reaction | 2 | True |
| re0000000067 | 68 | assumed to be an irreversible reaction | 2 | True |
| re0000000068 | 69 | assumed to be a fast reaction | n/a | True |
| re0000000069 | 70 | assumed to be an irreversible reaction | n/a | True |
| re0000000074 | 75 |  | 1 | True |
| re0000000075 | 76 |  | 1 | True |
| re0000000076 | 77 | assumed to be an irreversible reaction | 1 | True |
| re0000000077 | 78 | assumed to be a fast reaction | 1 | True |
| re0000000078 | 79 |  | 1 | True |
| re0000000079 | 80 | assumed to be a fast reaction | 1 | True |
| re0000000080 | 81 |  | 2 | True |
| re0000000081 | 82 |  | 2 | True |
| re0000000082 | 83 |  | 1 | True |
| re0000000083 | 84 |  | 2 | True |
| re0000000084 | 85 |  | 2 | True |
| re0000000085 | 86 |  | 2 | True |
| re0000000086 | 87 | assumed to be a fast reaction | 2 | True |
| re0000000116 | 117 | degradation | n/a | True |
| re0000000117 | 118 | degradation | n/a | True |
| re0000000118 | 119 | assumed to be an irreversible reaction | 1 | True |
| re0000000119 | 120 | assumed to be an irreversible reaction | 1 | True |
| re0000000120 | 121 | assumed to be an irreversible reaction | 1 | True |
| re0000000124 | 125 | assumed to be an irreversible reaction | 2 | True |
| re0000000125 | 126 | assumed to be an irreversible reaction | 2 | True |
| re0000000796 | 797 |  | 25 | True |
| re0000000811 | 812 |  | 25 | True |

Several source events are explicitly assumed fast (including 0001, 0016, 0018, 0025, 0068 and their round-two counterparts). This is author model provenance, not measured path dominance or elapsed-time evidence. The physiological ordering of early initiator/inter-round tRNA release and peptidyl transfer remains a Human Review issue.

## Original article and supplement coverage

Article p.7 provides limited direct context for reaction 22 as EF-G GTP hydrolysis on translating ribosomes. S27 defines bound GDP/GTP complexes and translocation states. This supports interpretation as author-model steps; no detailed SI text/PDF or experimental certification is invented.

Seven original elongation workbook models: 244 reaction rows mapped by local model/ID to canonical exact equations; 0 equation discrepancies. S27 checked parameter rows: 44; discrepancies: 0.

The workbook reader warns about unsupported extensions. It is used read-only and every inspected source raw hash remains unchanged. The machine appendix records every warning, row locator, mapping and any discrepancy.

