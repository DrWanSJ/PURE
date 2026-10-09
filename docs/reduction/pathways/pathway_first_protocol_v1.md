# Pathway-first protocol v1 — GlyRS / MetRS prototype

Status: `HUMAN_REVIEW_REQUIRED`. Scope: Phase A only. Structural verification
does not approve a biochemical interpretation, establish an observed flux, or
authorize expansion to Phase B. This work creates no reduced reaction, rate
law, QSSA model, parameter fit, or numerical kinetic simulation.

## 1. Execution boundary and source authority

The authorized existing checkout is `C:\Users\sean\Desktop\GUV` on sean,
branch `codex/energy-cycles-v1`. The orchestrating preflight recorded starting
HEAD `152047da1fea4e80b1b5231594c5f70122c06e98`, a clean tree and upstream
ahead/behind `0/0`. Existing energy-cycle work was confirmed complete and
published before Phase A edits. Follow `PURE_two_computer_git_rules.txt`;
create no checkout or branch, modify no frozen source or previous research,
and commit/push only the verified additive Phase A artifacts. A final Git
record belongs in the delivery report rather than this frozen protocol.

Authority, from highest to lowest:

1. `models/pnas2017_full_reference/original/fMGG_synthesis.xml`: original
   species IDs, reaction IDs, directions, reactant/product multiplicities.
2. `docs/reduction/reaction_level_annotation_v2.csv` and its approved method:
   reaction-local Level-C labels, including multiple contexts.
3. `reaction_family_summary_v2.csv`, `reaction_cross_family_links_v2.csv`
   and original reaction-family/subsystem provenance: local context.
4. Exact graph computations: derived connectivity evidence.
5. Carrier interpretation and representative-path choices: explicitly
   scoped derived interpretations, never replacements for source equations.

The SBML SHA-256 is
`dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`.
It has 241 species, 968 directed reactions and 3,854 directed Petri arcs.
All 3,854 stoichiometric references use literal MathML coefficients; reading
only a `stoichiometry` attribute is insufficient. In particular,
`re0000000414` is `PPiase_PO4_PO4 -> PPiase_degraded + 2 PO4`.

Directional reference activity comes from
`models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv`,
SHA-256 `cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465`.
Its bytes match `Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv`
inside `references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip`.
The 968 reaction parameters match the existing reviewed-v2 values; the
additional `default=1` is a compartment entry. There are 485 zero and 483
positive reaction parameters. Existing provenance is recorded in
`docs/pnas2017/reference_reproduction.md` and
`docs/reduction/reduction_audit_manifest_v0.json`.

`k=0` means `REFERENCE_DISABLED` for that direction under the fixed author
parameters. `k>0` means parameter-enabled, without asserting positive flux
on an actual trajectory. Preserve the original v2 pair-aware activity label
separately: `FORWARD_ONLY` can label both the positive and the zero direction
of a pair. SBML all-one initial conditions and local `k1=1` are placeholders.

## 2. Exact scope and representation

Parse the full network before selecting any module. Store species and
reaction nodes separately, with reactant-to-reaction and
reaction-to-product arcs and exact coefficients. Compute each sparse
stoichiometric column as products minus reactants. Never merge explicit
reverse reactions or replace a multi-reactant event with independent
unconditional edges.

Phase A includes the union of:

- Every reaction consuming or producing a species equal to `GlyRS` or
  `MetRS`, or beginning with `GlyRS_` or `MetRS_`, including degraded sinks.
- Every reviewed-v2 row carrying `RS_binding`, `RS_activation`, or
  `RS_charging` among its contexts.

This independently yields 134 unique reactions: 126 enzyme-touching rows
plus eight enzyme-free rows, with 84 positive and 50 zero author parameters.
The IDs are `re0000000126` through `re0000000260`, except
`re0000000258`. The remaining 834 original reactions stay represented in
the full Petri network and coverage ledger as `OUT_OF_PHASE_A`; no claim
of full-network pathway coverage follows.

The eight enzyme-free boundary rows are `re0000000143`, `re0000000149`,
`re0000000168`, `re0000000174`, `re0000000176`, `re0000000216`,
`re0000000218`, and `re0000000259`. They comprise four exact reverse pairs
for free aminoacyl-AMP and free aminoacyl-tRNA interconversion; all have
zero author parameters. Preserve their full equations without inventing an
enzyme state. Free charged-tRNA degradation `re0000000031` and
`re0000000258` is recorded as external boundary incidence, symmetrically,
rather than silently expanding one enzyme's scope.

For each enzyme, source-name selection yields 15 nondegraded states and one
degraded sink. Every one of its 63 enzyme-touching reactions has exactly one
selected state on each side. The local enzyme projection is therefore
unambiguous: 48 nondegradation edges and 15 degradation exits. This is a
local rule, not a general single-carrier model of translation.

Each transition retains its reaction ID, carrier-before and carrier-after
state(s), every other reactant/product and coefficient, all Level-C labels,
family, exact reverse partner, directional author activity, and provenance.
The full reactant and product multisets remain available to reconstruct the
source event. aaRS/tRNA assembly and release involve composite carriers;
the enzyme projection does not certify a complete tRNA or ribosome history.
External handoffs retain source incidence and `HUMAN_REVIEW_REQUIRED`.
Generic ATP, AMP, PPi or other shared substrates cannot establish carrier
continuity. A future multi-carrier event must preserve separate tracked
carriers or remain unresolved; never arbitrarily choose one to force a chain.

## 3. Deterministic pathway decomposition

Use sorted original IDs for every tie-break. Keep all directed edges in the
source graph, with a separately derived positive-parameter view. Exact
reverse pairs are found by swapping complete stoichiometric multisets,
not by reaction names or source reversible flags.

Identify all outgoing edges from each carrier state as competing exits and
all incoming edges as potential structural rejoins. Include degradation and
zero-parameter exits in completeness checks. In particular,
`GlyRS_Gly_ATP_tRNAGlyGCC` has four nondegradation exits
(`re0000000197`, `re0000000206`, `re0000000196`, `re0000000194`) and the
zero-parameter degradation exit `re0000000214`.

Generate finite representative paths by deterministic breadth-first search
under declared substrate-entry orders and chemical waypoint constraints.
Waypoints require the source state changes for aminoacyl-AMP formation,
charging, product release and enzyme recovery; the builder must derive
reaction sequences rather than embed the requested example sequence.
Independent verification may use the user's eight-step GlyRS witness as
an external acceptance example. Permit the recovered initial enzyme only
as the closing state of a catalytic return. Record omitted alternatives as
branches and rejoins, preserving every original scoped edge elsewhere.

Compute strongly connected components on the complete carrier graph. The
condensation graph alone is a DAG; no within-component edge may be lost.
For every nondegradation edge with a return route, obtain a deterministic
shortest return path and retain the resulting finite cycle certificate.
Deduplicate equivalent certificates by canonical rotation. Certificate
count is not the number of all possible cycles. Avoid all-simple-path or
all-cycle enumeration. Preserve returns, alternative entrances and exact
reverse edges as distinct source directions.

Classify records with the applicable labels `PRODUCTIVE_PATH`,
`ALTERNATIVE_ENTRY`, `COMPETITIVE_BRANCH`, `REVERSE_EDGE`, `RETURN_LOOP`,
`REJOIN`, `CROSS_FAMILY_LINK`, `REFERENCE_DISABLED`, and `UNRESOLVED`.
`PRODUCTIVE_PATH` means structural reachability of the specified output
with the required co-reactants supplied; it does not rank flux or imply
that the complete Petri network enables that route at any particular time.
Cross-family continuity must survive an RFAM boundary, including
GlyRS charging-to-AMP reset and its MetRS counterpart. Preserve approved
dual labels on `re0000000207/0208` and `re0000000249/0250`.

Extract MetRS independently before comparison. Compare complete renamed
stoichiometric signatures and author activity patterns. A successful
topological mapping is not kinetic equivalence. External substrate/product
incidence may differ even when the two local enzyme graphs match.

## 4. Artifact and validation contract

`glyrs_metrs_sample.md` is the biological reading view: connected routes,
complete equations, original IDs, Level-C tags, branch exits, rejoin anchors,
reverse/disabled channels, and a separate sink/boundary appendix. It must
display every scoped source equation accurately at least once. Repeated
path references are permitted and must not inflate unique coverage.

`glyrs_metrs_pathway_index.csv` and `glyrs_metrs_graph.json` retain machine
navigation, source fingerprints, edge provenance, path/cycle certificates,
scope and review status. `glyrs_metrs_review.md` records actual verification
results and remaining decisions. This protocol and the review contain
algorithm/audit detail; the reading view should not contain a parameter
audit, SHA inventory, or reduction discussion.

Structural gates check original counts and IDs, exact stoichiometry and
directions, all required co-reactants, consecutive carrier continuity,
branch completeness including disabled sinks, true rejoin states,
cross-family links, SCC/return preservation, directional activity, scope
coverage and evidence status. Report separately unique scoped reactions,
Markdown reaction references and reactions shared by multiple paths.

The test program must actually run these ten negative controls and record
expected versus actual rejection:

1. Force `re0000000206 -> re0000000196` into a path.
2. Serialize mutually exclusive exits from a common predecessor.
3. Omit a required ATP or tRNA reactant from a displayed step.
4. Treat a zero-parameter direction as enabled reference flux.
5. Connect unrelated carriers through an ordinary shared substrate.
6. Delete a real cross-RFAM connection.
7. Treat the cyclic carrier graph as a DAG.
8. Change the `re0000000414` phosphate coefficient from 2 to 1.
9. Count repeated references as distinct covered reaction IDs.
10. Mark a path verified without complete supporting evidence.

Verification failure remains a failure; do not remove evidence, weaken a
check, or infer human approval to finish the task. Successful structural
checks may support implementation readiness for later expansion, but all
scientific interpretation and external carrier-handoff approval remain
`HUMAN_REVIEW_REQUIRED`. Stop after delivering and publishing the Phase A
prototype. Phase B pathway reconstruction requires explicit researcher
confirmation; the full Petri inventory by itself is not that confirmation.
