# PNAS2017 968-row functional annotation v2

**Functional annotation review: COMPLETE.**

`functional_annotation_unresolved = 0`; live human functional review queue =
**0**. This completes functional-stage annotation of the unchanged source
network. The v0/v1 tables, source provenance and evidence distinctions remain
available; 50 rows retain `GRAPH_PROPAGATED` provenance.

**Reduction scientific review: 968 / 968 `PENDING`.** No QSSA,
fast-equilibrium, lumping, deletion, or reduced-core kinetic decision is
approved. Functional annotation completion does not complete reduction.

| v2 status | Rows |
| --- | ---: |
| `DIRECT_CHEMISTRY` | 492 |
| `GRAPH_PROPAGATED` | 50 |
| `HUMAN_REVIEW_REQUIRED` | 0 |
| `REFERENCE_DISABLED` | 420 |
| `SHARED_JUNCTION` | 6 |
| **Total** | **968** |

The final human mechanistic audit approved all 24 rows in each elongation
cycle and all 58 EF-G/recycling rows:

| Family | Functional distribution |
| --- | --- |
| `RFAM_002` | 10 `ELONG_aa_tRNA_delivery`; 8 `ELONG_energy_coupling`; 2 `ELONG_peptide_formation`; 4 `ELONG_translocation` |
| `RFAM_004` | 10 `ELONG_aa_tRNA_delivery`; 8 `ELONG_energy_coupling`; 2 `ELONG_peptide_formation`; 4 `ELONG_translocation` |
| `RFAM_014` | 18 `ELONG_energy_coupling`; 2 `ELONG_energy_coupling;RECYCLE_component_release`; 14 `RECYCLE_disassembly`; 24 `RECYCLE_component_release` |

Each elongation family retains four double-zero side-path rows as
`REFERENCE_DISABLED`, with approved delivery context but no propagation
anchor. `RFAM_014` retains the real EF-G/50S junction `0308/0327`.
The other approved junctions are `0207/0208` and `0249/0250`; all six remain
`SHARED_JUNCTION` with no live review flag. All 22 cross-family mechanistic
links remain available as provenance.

The newly approved rules moved 54 rows out of `HUMAN_REVIEW_REQUIRED`; another
24 graph-supported rows became direct approved annotations. The verifier
checks the two elongation cycles' structural/functional pattern without
asserting rate equality or kinetic equivalence. It also checks the previously
approved RFAM_005–013, RFAM_015–018, RFAM_022, RFAM_024–026 and RFAM_033–035
scientific labels against the prior baseline. The method and SHA-256 manifest
record the complete rule set and source identity.
