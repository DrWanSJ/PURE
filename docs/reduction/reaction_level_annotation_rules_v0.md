# Reaction-level annotation rules v0

This document records the deterministic first-pass rules used to populate `reaction_level_annotation_v0.csv`. They are navigation rules, not scientific acceptance decisions.

| Rule | Primary Level C | First-pass criterion | Confidence |
| --- | --- | --- | --- |
| `D00_degraded_participant` | `DEG_sink` | any participant ends in `_degraded` | high |
| `RSF_fMet_module` | `RS_to_INIT_formylation` | source subsystem `FMet_tRNASynthesis` | high |
| `RS1_pre_activation_binding` | `RS_binding` | aminoacylation association/dissociation before adenylate/PPi/AMP/charged-tRNA signatures | high |
| `RS2_activation_chemistry_or_products` | `RS_activation` | aminoacyl-adenylate / PPi / AMP / activation state transition | medium |
| `RS3_charged_tRNA_identity` | `RS_charging` | charged-tRNA identity appears in the channel | high |
| `IN1_mRNA_assembly` | `INIT_assembly` | mRNA joins/leaves pre-initiation assembly | high |
| `IN1_factor_ribosome_assembly` | `INIT_assembly` | general B1/B2 factor-ribosome assembly without a more specific signature | medium |
| `IN2_IF2_tRNA_complex`, `IN2_standalone_initiator_tRNA` | `INIT_tRNA_recruitment` | initiator fMet-tRNA recruitment | high |
| `IN3_IF2_nucleotide_preparation`, `IN3_GTP_GDP_Pi_state` | `INIT_energy_commitment` | IF2 nucleotide-state / GTP-GDP-Pi chemistry | medium |
| `IN4_30S_50S_70S` | `INIT_70S_formation` | explicit 30S + 50S <=> 70S assembly channel | high |
| `IN5_posthydrolysis_factor_release` | `INIT_factor_release` | post-hydrolysis IF release or elongation-ready 70S | high |
| `EL1_ternary_complex`, `EL1_EFTu_delivery` | `ELONG_aa_tRNA_delivery` | charged-tRNA / EF-Tu delivery channel | high |
| `EL1_charged_tRNA_delivery` | `ELONG_aa_tRNA_delivery` | Ca2 charged-tRNA delivery without a stronger energy signature | medium |
| `EL2_EFTu_nucleotide_exchange` | `ELONG_energy_coupling` | EF-Tu/EF-Ts nucleotide exchange | high |
| `EL2_EFTu_energy_step`, `EL2_EFG_energy_step` | `ELONG_energy_coupling` | GTP/GDP/Pi-linked elongation chemistry | medium |
| `EL2_EFG_nucleotide_cycle` | `ELONG_energy_coupling` | EFG nucleotide cycle in Elongation_B | high |
| `EL2_shared_EFG_R50` | `ELONG_energy_coupling` | EFG-GDP/50S chemistry shared with Termination_C | low |
| `EL3_peptide_length_transition` | `ELONG_peptide_formation` | peptide-length transition | high |
| `EL4_EFG_positional_progress`, `EL4_EFG_cycle` | `ELONG_translocation` | EFG-associated positional/codon progression | medium |
| `EL5_Ca1_tRNA_release` | `ELONG_tRNA_release` | deacylated tRNA release/return channel | high |
| `TM1_RF1_RF2_binding` | `TERM_factor_binding` | RF1/RF2 binding/release without peptide-release signature | high |
| `TM2_peptide_release` | `TERM_peptide_release` | free completed peptide appears/disappears | high |
| `TM3_RF3_cycle` | `TERM_energy_coupling` | RF3-assisted termination cycle | high |
| `RC1_term70S_RRF_EFG` | `RECYCLE_disassembly` | post-termination 70S + RRF/EFG recycling chemistry | high |
| `RC2_postsplit_component_release` | `RECYCLE_component_release` | post-split 50S/30S/mRNA/tRNA/factor component channels | medium |
| `EN1_enzyme_binding_release`, `EN1_ppiase_binding_release` | `EN_binding` | CK/NDK/MK/PPiase association/dissociation | high |
| `EN2_carrier_state_transition` | `EN_energy_transfer` | CK/NDK/MK catalytic state transition | high |
| `EN2_ppiase_chemistry` | `EN_byproduct_processing` | PPiase PPi <=> 2Pi bound-state chemistry | high |
| `EN3_small_molecule_carrier_conversion` | `EN_energy_transfer` | shared free nucleotide/phosphate conversion | high |

For medium/low rows, `level_c_candidate_stages` explicitly records the alternate stage(s). All rows remain subject to human review.
