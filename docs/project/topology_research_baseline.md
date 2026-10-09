# Topology-first research baseline

Pinned methodological baseline: codex/pnas-topology-first at 60abf1e371e90f70474bc98174035726cc68f064. It contains full-network topology, reaction/species graphs, module interfaces, chains, branches, cycles, shared hubs, structural aggregation candidates, effective kinetic derivations, bounded CHAIN_01 evidence, resource/occupancy accounting and a repositioned local QSSA role. This is a research baseline, not a validated reduced model.

Topology identifies possible reductions; it does not prove kinetic closure. Keep these evidence levels distinct:

1. Exact stoichiometric reduction: a chemistry/ledger relation, not a time-course equivalence claim.
2. Coordinate/conservation reduction: exact state bookkeeping under its declared domain, not enzyme QSSA.
3. Candidate kinetic lumping: a proposed closure with stated information loss.
4. Local QSSA: a scoped fast/slow hypothesis requiring physical-domain and startup checks.
5. Dynamical validation: preregistered numerical observables, conditions, uncertainty and gates.
6. Human scientific approval: an explicit decision that does not follow automatically from topology or verifier PASS.

codex/energy-cycles-v1 at 152047da1fea4e80b1b5231594c5f70122c06e98 is the next commit on this baseline. It studies CK, NDK, MK and PPiase. Feasible tested cases may meet registered isolated gates, while physical-domain, startup, microscopic storage and coupling limits remain. All four recommendations retain REVISE_WITH_EXTRA_STATE and HUMAN_REVIEW_REQUIRED. A coupled four-cycle replacement is not approved; PURE_reduced_core remains NOT_VALIDATED.

Authoritative energy evidence: docs/reduction/energy_cycles/validation_report.md, human_review.md, publication_note.md and results/energy_cycles_v1/artifact_manifest.json at the pinned energy commit. The 299-output manifest is a frozen prepublication record. This governance task changes none of those bytes or claims.

R6 remains 0/9 all-mandatory passes. Its branch label historically points to the pre-R6 parent 1181ab2; complete existing R6 evidence is at preservation commit 9282853a24d716e3021ea85123e9ba1e0bb4c6fc, reachable through the archived R8 tag. R7's CK_FIRST_ORDER_IMPROVES_EXTENT_NOT_CURRENT and R8's CK_STARTUP_LAYER_ATTRIBUTION_NOT_SUPPORTED are retained without promotion. Historical negative evidence is useful research, not a cleanup error.
