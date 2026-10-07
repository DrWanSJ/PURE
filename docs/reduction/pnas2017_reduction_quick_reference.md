# PNAS2017 reduction evidence quick reference

**Evidence preparation only.** G1-PNAS is formally PASS / CLOSED. [Species information retention](species_information_contract_summary.md) is **HUMAN APPROVED**: I=42, II-A=57, II-B=91, III=22, C=29. All **968 kinetic decisions remain PENDING**, and all **96 process boxes remain unselected**. `PURE_reduced_core` remains `NOT_VALIDATED`. Source HEAD: `3e22aeeb6124e2ad7d3373e0cf056383bf9c8c1e`.

Scope is **AUTHOR_REFERENCE_CONDITION_ONLY** through 1000 s. The preserved 200-point trajectory and separate initial-state diagnostic do not validate other conditions. Author absolute chemical units are unresolved. Medians/fractions weight stored grid points equally; extents are approximate trapezoidal integrals. First stored state equals author x0 at timestamp `1e-4`: the initial layer is not fully resolved. See the [method](pnas2017_reduction_evidence_method.md), [frozen preregistration](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/evidence_preregistration.json) and [provenance/verification manifest](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/evidence_manifest.json).

## Read the evidence by mathematical level

| Evidence | What to inspect | Interpretation boundary |
| --- | --- | --- |
| [968 reaction rows](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_evidence.csv) | Original ID, family/process links, rate/extent, free-resource/particle delta, state/pair/pool/ledger obligations | Individual event stoichiometry is exact; no unique reaction QSSA time is invented |
| [241 state rows](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_evidence.csv) and [QSS samples](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_qss_timeseries.csv) | Contract class, occupancy, production/consumption, QSS defect, turnover and initial layer | Cancellation of state fluxes is evidence; a tested algebraic closure is still needed |
| [290 exact pair rows](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reverse_pair_evidence.csv) and [pair samples](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reverse_pair_equilibrium_timeseries.csv) | Both rates, exchange/net flux, defect, disabled directions and both extents | Pair evidence is unavailable when a direction is disabled or total exchange is too low |
| [Many-to-many pool links](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_pool_metrics.csv) and [16 process diagnostics](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/process_timescale_evidence.csv) | Registered pool identities and full candidate-block mode ranges | Unresolved tokens/coordinates stay N/A or NEED_MORE_INFORMATION |

These linked CSVs are derived structured navigation. `EXTRACTED` source/contract facts, `INFERRED` numeric/annotation summaries and `AMBIGUOUS` unit/token/coordinate assumptions remain distinguishable. Their authority is the linked frozen sources; freshness depends on matching source/artifact hashes and independent verification.

## Distinctions that matter

| Concept | Required question |
| --- | --- |
| Time-scale separation | Does the selected candidate block relax faster than explicitly chosen slow coordinates? Fast modes alone do not certify QSSA. |
| QSSA | Can selected states follow a valid, stable algebraic closure while the protected trajectory is retained? |
| Total-coordinate QSSA | Can slow totals and reconstructed free/bound partitions preserve sequestered resources? |
| Rapid equilibrium | Do the particular forward/reverse fluxes balance on the proposed domain? A free/total ratio cannot decide this. |
| Lumping | Can aggregated states/events retain a justified rate, observables and reconstruction? |
| Conservation reconstruction | Can an exact invariant recover a coordinate without any fast-state approximation? |

`delta_QSS=|dz/dt|/(P+C)` differs from `delta_eq=|vf-vr|/(|vf|+|vr|)`. A denominator at/below `1e-12` is **LOW_FLUX_UNINFORMATIVE**, never `0/0=0`. Disabled reference directions are not equilibrium evidence. Pool occupancy is a separate sequestration question. Ledger closure is separate from kinetic validity, and neither follows from a short relaxation time or a small enzyme pool. No descriptive band selects KEEP/LUMP/QSSA/RAPID EQUILIBRIUM/CHEMOSTAT/DROP.

## Sixteen process views

Counts overlap across cards and are not additive. Pair counts include pairs touching the card. Tau values use the stored seconds convention; `R_tau=tau_slow/tau_fast`, so larger means greater proxy separation. All candidate slow-coordinate choices remain `NEED_MORE_INFORMATION`. Occupancy entries give each qualified active pool's maximum nonfree fraction separately; complete per-pool certificates and per-state member ratios remain in linked records.

| Process | Reactions | Candidate states | Protected resources (examples) | Pairs | Timescale evidence | Occupancy / sequestration signal | QSS evidence | Equilibrium evidence | Ledger status | Human decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [P01 Amino-acid activation](process_quick_reference/01_amino_acid_activation.md) | 50 | 12 | `AMP`, `ATP`, `Gly`; 4 more in linked CSV | 18 | tau 2.2853e-05..13.481; R median 74.031; NEED_MORE_INFORMATION | GlyRS_active_pool: 0.99996; MetRS_active_pool: 0.99997 | 12/12 states informative; median defect 4.567e-06–0.0099974 | 12/18 pairs informative; median defect 0.00099405–0.9998 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P02 tRNA aminoacylation](process_quick_reference/02_trna_aminoacylation.md) | 88 | 28 | `AMP`, `ATP`, `Gly`; 8 more in linked CSV | 34 | tau 1.9342e-05..14.134; R median 11.553; NEED_MORE_INFORMATION | GlyRS_active_pool: 0.99996; MetRS_active_pool: 0.99997 | 28/28 states informative; median defect 4.567e-06–0.30421 | 24/34 pairs informative; median defect 0.00033391–1 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P03 Initiator-tRNA formylation](process_quick_reference/03_initiator_trna_formylation.md) | 29 | 6 | `FD`, `MTF`, `MettRNAfMetCAU`; 4 more in linked CSV | 11 | tau 8.772e-05..0.0010491; R median 15.784; NEED_MORE_INFORMATION | MTF_active_pool: 0.90266 | 6/6 states informative; median defect 4.0782e-07–0.00013801 | 4/11 pairs informative; median defect 1.2251e-05–0.016832 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P04 Initiation factor preparation](process_quick_reference/04_initiation_factor_preparation.md) | 10 | 3 | `GDP`, `GTP`, `IF2`; 1 more in linked CSV | 3 | tau 0.0080099..0.0625; R median 0.85614; NEED_MORE_INFORMATION | IF2_active_pool: 0.99955 | 3/3 states informative; median defect 0.00012821–0.033822 | 3/3 pairs informative; median defect 8.3697e-06–0.033805 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P05 Ribosome and mRNA initiation assembly](process_quick_reference/05_ribosome_mrna_initiation_assembly.md) | 336 | 45 | `GDP`, `GTP`, `IF1`; 8 more in linked CSV | 100 | tau 0.00011366..2.0125e+07; R median 18.518; NEED_MORE_INFORMATION | IF1_active_pool: 0.030217; IF2_active_pool: 0.99955; IF3_active_pool: 0.58472; RS30S_active_pool: 1; RS50S_active_pool: 1 | 45/45 states informative; median defect 7.0907e-06–0.57599 | 91/100 pairs informative; median defect 1.1925e-05–1 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P06 EF-Tu ternary-complex delivery](process_quick_reference/06_ef_tu_ternary_complex_delivery.md) | 34 | 7 | `EFTs`, `EFTu`, `GDP`; 3 more in linked CSV | 9 | tau 6.6289e-05..1389.2; R median 0.017125; NEED_MORE_INFORMATION | EFTs_active_pool: 0.97133; EFTu_active_pool: 0.99998 | 7/7 states informative; median defect 1.8398e-08–0.99903 | 9/9 pairs informative; median defect 6.3248e-06–0.99903 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P07 EF-G nucleotide cycle](process_quick_reference/07_ef_g_nucleotide_cycle.md) | 40 | 8 | `EFG`, `GDP`, `GTP`; 4 more in linked CSV | 10 | tau 0.001..0.21863; R median 0.23103; NEED_MORE_INFORMATION | EFG_active_pool: 0.99451; RS30S_active_pool: 1; RS50S_active_pool: 1 | 8/8 states informative; median defect 0.00023705–0.14261 | 6/10 pairs informative; median defect 0.016891–0.70133 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P08 Peptidyl-tRNA and ribosome transitions](process_quick_reference/08_peptidyl_trna_ribosome_transitions.md) | 125 | 27 | `EFG`, `EFTu`, `GDP`; 10 more in linked CSV | 26 | tau 0.00099795..5.9235e+08; R median 1.521; NEED_MORE_INFORMATION | EFG_active_pool: 0.99451; EFTu_active_pool: 0.99998; RS30S_active_pool: 1; RS50S_active_pool: 1 | 25/27 states informative; median defect 1.4012e-05–0.99903 | 6/26 pairs informative; median defect 0.23763–0.99823 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P09 RF1/RF2 peptide release](process_quick_reference/09_rf1_rf2_peptide_release.md) | 35 | 6 | `Pept0003`, `RF1`, `RF2`; 4 more in linked CSV | 6 | tau 0.0050658..1.9972; R median 0.47115; NEED_MORE_INFORMATION | RF1_active_pool: 0.32102; RF2_active_pool: 0.064281; RS30S_active_pool: 1; RS50S_active_pool: 1 | 6/6 states informative; median defect 0.00011841–0.026986 | 4/6 pairs informative; median defect 0.30978–0.9895 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P10 RF3-assisted termination](process_quick_reference/10_rf3_assisted_termination.md) | 76 | 14 | `GDP`, `GTP`, `PO4`; 7 more in linked CSV | 17 | tau 1.5991e-05..31.25; R median 1.6648; NEED_MORE_INFORMATION | RF1_active_pool: 0.32102; RF2_active_pool: 0.064281; RF3_active_pool: 0.99914; RS30S_active_pool: 1; RS50S_active_pool: 1 | 14/14 states informative; median defect 3.405e-07–0.97113 | 15/17 pairs informative; median defect 5.5238e-05–0.9861 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P11 Ribosome recycling](process_quick_reference/11_ribosome_recycling.md) | 86 | 16 | `EFG`, `GDP`, `GTP`; 6 more in linked CSV | 20 | tau 0.00033333..6.6918; R median 9.8338; NEED_MORE_INFORMATION | EFG_active_pool: 0.99451; RRF_active_pool: 9.2698e-05; RS30S_active_pool: 1; RS50S_active_pool: 1 | 16/16 states informative; median defect 5.4325e-06–0.0017791 | 5/20 pairs informative; median defect 0.33491–0.98419 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P12 Creatine-kinase energy regeneration](process_quick_reference/12_creatine_kinase_energy_regeneration.md) | 25 | 6 | `ADP`, `ATP`, `CK`; 2 more in linked CSV | 9 | tau 9.8039e-06..0.0026345; R median 182.85; NEED_MORE_INFORMATION | CK_active_pool: 0.99159 | 6/6 states informative; median defect 3.69e-06–0.00028838 | 9/9 pairs informative; median defect 1.2574e-05–0.99889 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P13 Nucleotide-diphosphate kinase exchange](process_quick_reference/13_nucleotide_diphosphate_kinase_exchange.md) | 25 | 6 | `ADP`, `ATP`, `GDP`; 2 more in linked CSV | 9 | tau 5.3571e-05..0.001439; R median 68.879; NEED_MORE_INFORMATION | NDK_active_pool: 0.95466 | 6/6 states informative; median defect 5.2175e-06–0.00030713 | 8/9 pairs informative; median defect 0.00026729–0.15108 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P14 Adenylate kinase exchange](process_quick_reference/14_adenylate_kinase_exchange.md) | 25 | 6 | `ADP`, `AMP`, `ATP`; 1 more in linked CSV | 9 | tau 1.5503e-05..0.0010443; R median 6.3342; NEED_MORE_INFORMATION | MK_active_pool: 0.98426 | 6/6 states informative; median defect 2.4992e-07–0.00055046 | 9/9 pairs informative; median defect 3.3005e-06–0.99097 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P15 Pyrophosphate hydrolysis](process_quick_reference/15_pyrophosphate_hydrolysis.md) | 12 | 3 | `PO4`, `PPi`, `PPiase` | 4 | tau 0.00073571..0.0064974; R median 29.439; NEED_MORE_INFORMATION | PPiase_active_pool: 0.92687 | 3/3 states informative; median defect 0.00041415–0.0009737 | 4/4 pairs informative; median defect 0.60268–0.99961 | event exact; reconstruction required | PENDING_HUMAN_REVIEW |
| [P16 Shared small-molecule transitions](process_quick_reference/16_shared_small_molecule_transitions.md) | 12 | 0 | `ADP`, `AMP`, `ATP`; 5 more in linked CSV | 6 | tau N/A_NO_CANDIDATE_STATES..N/A_NO_CANDIDATE_STATES; R median N/A_NO_CANDIDATE_STATES; NEED_MORE_INFORMATION | N/A_POOL_MEMBERSHIP_UNRESOLVED | N/A: no candidate states | 0/6 pairs informative; median defect N/A | event exact; reconstruction required | PENDING_HUMAN_REVIEW |

## Aminoacylation regression

The preserved [specialized reference](aminoacylation_qssa_quick_reference.md) reports high GlyRS/MetRS complex occupancy, free adenylate accumulation, and fast modes. Its concentration summaries use the 200-point [historical author trajectory](../../results/pnas2017_reference/2026-09-24_authors_model_v0/authors_model_trajectory.csv); this layer uses the distinct 200-point [RoadRunner trajectory](../../results/pnas2017_reference/rr_cvode_author_csv_20260924/trajectory.csv). These input files are numerically different, not merely two roundings of identical samples. Historical rounded maxima and global maxima use the same inferred concentration convention:

| State | Historical max | Global max | Relative difference vs historical |
| --- | --- | --- | --- |
| `GlyRS_GlyAMP` | 0.3489 | 0.3482 | -0.19961% |
| `MetRS_MetAMP` | 0.43741 | 0.4373 | -0.025078% |
| `GlyAMP` | 23.727 | 23.68 | -0.19694% |
| `MetAMP` | 29.815 | 29.807 | -0.026773% |

The free adenylate maxima differ by about 0.197% for GlyAMP and 0.0268% for MetAMP; both remain substantial (about 7.89% and 9.94% of the corresponding initial free amino acid). These discrepancies are retained, without fitting or a claim of trajectory equivalence. The named complex occupancy remains high under the two explicit denominator conventions:

| Member / active pool | Historical max concentration / initial pool | Global max of member(t) / pool(t) |
| --- | --- | --- |
| `GlyRS_GlyAMP` / `GlyRS_active_pool` | 0.99685 | 0.99684 |
| `MetRS_MetAMP` / `MetRS_active_pool` | 0.99412 | 0.99413 |

The global column is the individual complex's member occupancy, not the pool's total nonfree fraction. Free GlyAMP/MetAMP have no complete total-token ratio asserted.

P01 stable `tau_min=2.2853e-05` and P02 `tau_min=1.9342e-05` retain short modes, but their full stable ranges are `2.2853e-05..13.481` and `1.9342e-05..14.134`. Historical `tau_fast≈1.9e-5 s` came from a different 30-state block and 30 sampled points; card-specific 12/28-state blocks, 200 samples and median-based `R_tau` do not have identical numerical conventions. This is a comparison of documented diagnostics, not an attempt to force numerical agreement.

Historical A3a remains [FAILED_VALIDATION_ON_REFERENCE_DOMAIN](aminoacylation_A3a_final_status.md); the broad 21-state A3b remains [FAILED_SMOKE_CLOSURE_FEASIBILITY](aminoacylation_A3bc_final_decision.md) near 2.498 s, and its restricted 9-state candidate remains `BLOCKED_NUMERICAL_COORDINATE_DEFECT` with an incomplete full window. Total coordinates removed a recorded bookkeeping leak but did not supply global kinetic validation. Those archived-main results keep their own domain and provenance; PR #3/#4 evidence is not imported.


## Open scientific choices

Define complete protected substrate-token membership and bound moieties where missing; choose candidate fast/slow coordinates and reconstruction maps; resolve absolute unit and initial-layer conventions where a future claim depends on them; specify the intended perturbation domain and full-versus-reduced acceptance checks. Exact event stoichiometry and pool certificates do not answer these choices. No kinetic transformation is evaluated or approved here.

Status: REFERENCE ONLY — NO KINETIC REDUCTION APPROVED.
