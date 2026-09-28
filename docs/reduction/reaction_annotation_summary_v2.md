# PNAS2017 968-row functional annotation v2

The chemistry-first layer retains the v0/v1 provenance and source network.
This pass adds human-approved functional rules for EF-Tu, CK/NDK/MK, PPiase,
RF1/RF2, IF2 preparation and bare ribosomal subunit joining. See
`reaction_annotation_method_v2.md` for the reaction-local rules and
`reaction_annotation_manifest_v2.json` for hashes and status counts.

| v2 status | Rows |
| --- | ---: |
| `DIRECT_CHEMISTRY` | 414 |
| `GRAPH_PROPAGATED` | 74 |
| `SHARED_JUNCTION` | 6 |
| `REFERENCE_DISABLED` | 420 |
| `HUMAN_REVIEW_REQUIRED` | 54 |
| **Total** | **968** |

The 54 unresolved rows belong only to `RFAM_002` (12), `RFAM_004` (12) and
`RFAM_014` (30). They remain for a later human mechanistic audit. The live
functional review queue has 88 rows; it also records other unresolved
family-boundary and cross-family questions. There are 22 specific-intermediate
cross-family links. `SHARED_JUNCTION` remains 6.

| Reviewed family | Human-approved functional distribution | Unresolved | Queue |
| --- | --- | ---: | ---: |
| `RFAM_013` | 14 `ELONG_energy_coupling`; 4 `ELONG_aa_tRNA_delivery` | 0 | 0 |
| `RFAM_015` | 16 `EN_binding`; 2 `EN_energy_transfer` | 0 | 0 |
| `RFAM_016` | 16 `EN_binding`; 2 `EN_energy_transfer` | 0 | 0 |
| `RFAM_017` | 16 `EN_binding`; 2 `EN_energy_transfer` | 0 | 0 |
| `RFAM_018` | 6 `EN_binding`; 2 `EN_byproduct_processing` | 0 | 0 |
| `RFAM_022` | 2 `INIT_energy_commitment`; 2 `INIT_tRNA_recruitment` | 0 | 0 |
| `RFAM_024` | 2 `INIT_70S_formation` | 0 | 0 |
| `RFAM_033` | 4 `TERM_factor_binding`; 2 `TERM_peptide_release` | 0 | 0 |
| `RFAM_034` | 4 `TERM_factor_binding`; 2 `TERM_peptide_release` | 0 | 0 |

These 98 rows are now direct human-approved annotations. Previously 88 of
them had `HUMAN_REVIEW_REQUIRED` status; resolving those 88 yields the
observed `142 → 54` unresolved change. The verifier preserves the non-target
functional fingerprint, including `RFAM_035` labels and the earlier
`RFAM_005–012` and `RFAM_025/026` rules.

**Reduction scientific review remains 968 / 968 `PENDING`.** These functional
stages do not approve QSSA, fast equilibrium, reaction lumping, reaction
deletion, chemostatting, kinetic equivalence or a reduced-core model.
