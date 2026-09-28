# PNAS2017 968-row functional annotation v2

The chemistry-first v2 layer retains the graph-aware v1 topology, corrects
32 RS reaction contexts and 90 initiation reaction contexts from explicit
biochemical events, and records specific
intermediates connecting families across source subsystems. See
`reaction_annotation_method_v2.md` for priorities, limitations and status
definitions; `reaction_annotation_manifest_v2.json` is the machine-readable
count and freshness record.

| v2 primary status | Rows |
| --- | ---: |
| `DIRECT_CHEMISTRY` | 324 |
| `GRAPH_PROPAGATED` | 76 |
| `SHARED_JUNCTION` | 6 |
| `REFERENCE_DISABLED` | 420 |
| `HUMAN_REVIEW_REQUIRED` | 142 |
| **Total** | **968** |

There are **22 cross-family specific-intermediate links** and **177 flagged
functional-review rows**. The reviewed initiation families have no remaining
functional queue rows; the remaining queue concerns other families, including
`RFAM_014` (32). `functional_annotation_unresolved = 142` counts
rows whose inherited candidate context lacks matching hard-anchor support.
Candidate contexts are preserved for review, not silently promoted.

| Reviewed family | Earlier queue | Current queue | Earlier unresolved | Current unresolved | Earlier shared | Current shared |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `RFAM_025` | 108 | 0 | 80 | 0 | 28 | 0 |
| `RFAM_026` | 80 | 0 | 38 | 0 | 42 | 0 |

`RFAM_025` now has 52 assembly, 20 initiator-tRNA recruitment, 10 explicit
70S formation, 8 IF2 energy commitment and 28 factor release rows.
`RFAM_026` has 60 assembly and 20 initiator-tRNA recruitment rows. All 198
are direct, human-approved initiation classifications. The initiation shared
junction count falls **70 → 0** and initiation unresolved falls **118 → 0**.
The verifier also confirms that no other family's functional label, status or
queue flag changed from the prior v2 commit.

The approved RFAM_005–010 chemistry cases pass regression checks. The
RFAM_011/012 Met charging network was matched against Gly source chemistry,
intermediate identity and parameter topology: **52/52 structural counterparts
match** in functional context and activity class. Numeric rate magnitudes
differ in some counterparts and were not treated as equal or as kinetic
equivalence.

**Reduction scientific review: 968 / 968 `PENDING`.** This is a functional
annotation/navigation layer. It does **not** approve QSSA, fast equilibrium,
reaction lumping, reaction deletion or reduced-core kinetics.
