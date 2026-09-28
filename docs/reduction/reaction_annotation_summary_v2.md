# PNAS2017 968-row functional annotation v2

The chemistry-first v2 layer retains the graph-aware v1 topology, corrects
32 reaction contexts from explicit biochemical events, and records specific
intermediates connecting families across source subsystems. See
`reaction_annotation_method_v2.md` for priorities, limitations and status
definitions; `reaction_annotation_manifest_v2.json` is the machine-readable
count and freshness record.

| v2 primary status | Rows |
| --- | ---: |
| `DIRECT_CHEMISTRY` | 130 |
| `GRAPH_PROPAGATED` | 82 |
| `SHARED_JUNCTION` | 76 |
| `REFERENCE_DISABLED` | 420 |
| `HUMAN_REVIEW_REQUIRED` | 260 |
| **Total** | **968** |

There are **22 cross-family specific-intermediate links** and **365 flagged
functional-review rows**. The queue is concentrated in initiation families
`RFAM_025` (108) and `RFAM_026` (80), followed by `RFAM_014` (32). These are
functional annotation questions, including true/maybe shared boundaries and
cross-subsystem connectivity. `functional_annotation_unresolved = 260` counts
rows whose inherited candidate context lacks matching hard-anchor support.
Candidate contexts are preserved for review, not silently promoted.

The approved RFAM_005–010 chemistry cases pass regression checks. The
RFAM_011/012 Met charging network was matched against Gly source chemistry,
intermediate identity and parameter topology: **52/52 structural counterparts
match** in functional context and activity class. Numeric rate magnitudes
differ in some counterparts and were not treated as equal or as kinetic
equivalence.

**Reduction scientific review: 968 / 968 `PENDING`.** This is a functional
annotation/navigation layer. It does **not** approve QSSA, fast equilibrium,
reaction lumping, reaction deletion or reduced-core kinetics.
