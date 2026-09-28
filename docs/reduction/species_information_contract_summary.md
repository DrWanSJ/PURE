# PNAS2017 241-species information-retention contract — summary

**Status:** human-approved species-level classification v1  
**Source snapshot:** `models/pnas2017_full_reference/audit/species_reduction_map.csv` at `a8104aaff64709298052404c2e7dacb7a19827cb`  
**Source blob:** `f18b67db52cfd0d740b05ab372bbae20258c08b0`  
**Scope:** 241 SBML species only. Derived observables such as `AT`, `P_complete`, `a_polymerized`, `R_init`, `R_elong`, `R_term`, and `R_recycle` are not additional source species.

> Important: “Class I” means the trajectory is a protected output. It does **not** mean every Class-I quantity must remain an independent ODE coordinate after exact conservation reduction.  
> “Class II-A” is an information-retention decision; it does **not** by itself prove QSSA/time-scale validity.

## Final tally

| Class | Count | Meaning |
| --- | ---: | --- |
| I | 42 | protected dynamic observable |
| II-A | 57 | enzyme/catalytic intermediate; algebraic/QSSA/effective reconstruction candidate |
| II-B | 91 | microstate identity not protected; functional occupancy/pool must be reconstructable |
| III | 22 | elongation microstate identity may be discarded; aggregate flux/occupancy/moiety information remains protected |
| C | 29 | terminal degradation sink; main ODE may omit, cumulative accounting required |
| **Total** | **241** | **all source species classified exactly once** |

## 241-species classification v1

| 类别 | 数量 | Species 落实结果 |
| --- | ---: | --- |
| **I — 必须输出动力学** | **42** | `ADP`, `AMP`, `ATP`, `CK`, `CP`, `Cr`, `EFG`, `EFTs`, `EFTu`, `FD`, `GDP`, `GMP`, `GTP`, `Gly`, `GlyRS`, `GlytRNAGlyGCC`, `IF1`, `IF2`, `IF3`, `MK`, `MTF`, `Met`, `MetRS`, `MettRNAfMetCAU`, `NDK`, `PO4`, `PPi`, `PPiase`, `Pept0003`, `RF1`, `RF2`, `RF3`, `RRF`, `RS30S`, `RS50S`, `RS70S`, `THF`, `fMet`, `fMettRNAfMetCAU`, `mRNA`, `tRNAGlyGCC`, `tRNAfMetCAU` |
| **II-A — 酶催化中间体，可代数/QSSA/有效速率重构** | **57** | `CK_ADP`, `CK_ATP`, `CK_CP`, `CK_CP_ADP`, `CK_Cr`, `CK_Cr_ATP`, `GlyAMP`, `GlyRS_AMP`, `GlyRS_AMP_GlytRNAGlyGCC`, `GlyRS_ATP`, `GlyRS_ATP_tRNAGlyGCC`, `GlyRS_Gly`, `GlyRS_GlyAMP`, `GlyRS_GlyAMP_PPi`, `GlyRS_GlyAMP_PPi_tRNAGlyGCC`, `GlyRS_GlyAMP_tRNAGlyGCC`, `GlyRS_Gly_ATP`, `GlyRS_Gly_ATP_tRNAGlyGCC`, `GlyRS_Gly_tRNAGlyGCC`, `GlyRS_GlytRNAGlyGCC`, `GlyRS_tRNAGlyGCC`, `MK_ADP_1`, `MK_ADP_2`, `MK_ADP_ADP`, `MK_AMP`, `MK_ATP`, `MK_ATP_AMP`, `MTF_FD`, `MTF_FD_MettRNAfMetCAU`, `MTF_MettRNAfMetCAU`, `MTF_THF`, `MTF_THF_fMettRNAfMetCAU`, `MTF_fMettRNAfMetCAU`, `MetAMP`, `MetRS_AMP`, `MetRS_AMP_MettRNAfMetCAU`, `MetRS_ATP`, `MetRS_ATP_tRNAfMetCAU`, `MetRS_Met`, `MetRS_MetAMP`, `MetRS_MetAMP_PPi`, `MetRS_MetAMP_PPi_tRNAfMetCAU`, `MetRS_MetAMP_tRNAfMetCAU`, `MetRS_Met_ATP`, `MetRS_Met_ATP_tRNAfMetCAU`, `MetRS_Met_tRNAfMetCAU`, `MetRS_MettRNAfMetCAU`, `MetRS_tRNAfMetCAU`, `NDK_ADP`, `NDK_ATP`, `NDK_GDP`, `NDK_GDP_ATP`, `NDK_GTP`, `NDK_GTP_ADP`, `PPiase_PO4`, `PPiase_PO4_PO4`, `PPiase_PPi` |
| **II-B — microstate 不保留，但 functional occupancy 必须可重构** | **91** | **Factor states:** `EFG_GDP`, `EFG_GTP`, `EFTu_EFTs`, `EFTu_GDP`, `EFTu_GDP_EFTs`, `EFTu_GTP`, `EFTu_GTP_EFTs`, `EFTu_GTP_GlytRNAGlyGCC`, `EFTu_GTP_MettRNAfMetCAU`, `IF2_GDP`, `IF2_GTP`, `IF2_GTP_fMettRNAfMetCAU`, `RF3_GDP`, `RF3_GTP`. **Peptide length:** `Pept0002`. **Peptidyl-tRNA:** `Pept0002tRNAGlyGCC`, `Pept0003tRNAGlyGCC`. **Initiation `R_init`:** `RS30S_IF1`, `RS30S_IF1_IF2_GTP`, `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU`, `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS30S_IF1_IF2_GTP_mRNA`, `RS30S_IF1_IF3`, `RS30S_IF1_IF3_IF2_GTP`, `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU`, `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS30S_IF1_IF3_IF2_GTP_mRNA`, `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA`, `RS30S_IF1_IF3_mRNA`, `RS30S_IF1_fMettRNAfMetCAU_mRNA`, `RS30S_IF1_mRNA`, `RS30S_IF2_GTP`, `RS30S_IF2_GTP_fMettRNAfMetCAU`, `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS30S_IF2_GTP_mRNA`, `RS30S_IF3`, `RS30S_IF3_IF2_GTP`, `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU`, `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS30S_IF3_IF2_GTP_mRNA`, `RS30S_IF3_fMettRNAfMetCAU_mRNA`, `RS30S_IF3_mRNA`, `RS30S_fMettRNAfMetCAU_mRNA`, `RS30S_mRNA`, `RS70S_IF1`, `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_IF3`, `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA`, `RS70S_IF1_fMettRNAfMetCAU_mRNA`, `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`, `RS70S_IF3`, `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`, `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`, `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`, `RS70S_IF3_fMettRNAfMetCAU_mRNA`. **Recycling `R_recycle`:** `RS50S_EFG_GDP`, `RS50S_EFG_GDP_PO4`, `RS50S_EFG_GTP`, `RS50S_RRF`, `RS50S_RRF_EFG_GDP`, `RS50S_tRNAGlyGCC`, `RS50S_tRNAGlyGCC_EFG_GDP`, `RS50S_tRNAGlyGCC_RRF`, `RS50S_tRNAGlyGCC_RRF_EFG_GDP`, `RS70S_EFG_GDP`, `RS70S_EFG_GDP_PO4`, `RS70S_EFG_GTP`. **Pretermination `R_term/R_preterm`:** `elRS70SAUAA0004_Pept0003tRNAGlyGCC`, `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`, `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`. **Termination `R_term`:** `termRS30S_mRNA`, `termRS70SUAA0004_tRNAGlyGCC`, `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP`, `termRS70SUAA0004_tRNAGlyGCC_RF1`, `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3`, `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP`, `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP`, `termRS70SUAA0004_tRNAGlyGCC_RF2`, `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3`, `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP`, `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP`, `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP`, `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4`, `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP`, `termRS70SUAA0004_tRNAGlyGCC_RRF`, `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP`, `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4`, `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP`. |
| **III — elongation microscopic identity 可以丢失** | **22** | 全部折叠进 `R_elong` / elongation flux / peptide+tRNA+ribosome+GTP/GDP/Pi ledgers：`elRS70SAGGU0002_fMet`, `elRS70SAGGU0002_fMet_EFTu_GDP`, `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC`, `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC`, `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC`, `elRS70SAGGU0002_fMet_GlytRNAGlyGCC`, `elRS70SAGGU0002_fMettRNAfMetCAU`, `elRS70SAGGU0003_Pept0002`, `elRS70SAGGU0003_Pept0002_EFTu_GDP`, `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC`, `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC`, `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC`, `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC`, `elRS70SAGGU0003_Pept0002tRNAGlyGCC`, `elRS70SBGGU0002_Pept0002tRNAGlyGCC`, `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4`, `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP`, `elRS70SBGGU0003_Pept0003tRNAGlyGCC`, `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4`, `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP`, `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP`, `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP` |
| **C — degradation 只做累计 accounting** | **29** | `CK_degraded`, `EFG_degraded`, `EFTs_degraded`, `EFTu_degraded`, `GlyRS_degraded`, `GlytRNAGlyGCC_degraded`, `IF1_degraded`, `IF2_degraded`, `IF3_degraded`, `MK_degraded`, `MTF_degraded`, `MetRS_degraded`, `MettRNAfMetCAU_degraded`, `NDK_degraded`, `PPiase_degraded`, `Pept0002_degraded`, `Pept0002tRNAGlyGCC_degraded`, `Pept0003tRNAGlyGCC_degraded`, `RF1_degraded`, `RF2_degraded`, `RF3_degraded`, `RRF_degraded`, `RS30S_degraded`, `RS50S_degraded`, `fMet_degraded`, `fMettRNAfMetCAU_degraded`, `mRNA_degraded`, `tRNAGlyGCC_degraded`, `tRNAfMetCAU_degraded` |

## Human decisions incorporated

1. `Pept0002` → **II-B**, retained as a reconstructable peptide-length-2 pool rather than a Class-I trajectory.
2. `RS50S_tRNAGlyGCC` → **II-B / `R_recycle`**.
3. `elRS70SAUAA0004_Pept0003tRNAGlyGCC`, `..._RF1`, and `..._RF2` → **II-B / `R_term/R_preterm`**, not Class III elongation.
4. `RS30S`, `RS50S`, and `RS70S` remain Class I free-ribosome observables; bound ribosome occupancy is reconstructed through functional pools.
5. No synthetic `TLcat` source species is introduced into the 241-species contract.

## Validation boundary

This table is a **scientific information contract**, not a kinetic reduction proof. Later reduction still has to demonstrate positivity/feasibility, conservation and moiety accounting, protected-output reconstruction, and full-vs-reduced trajectory/flux errors.
