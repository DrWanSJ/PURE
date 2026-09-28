# Reaction functional annotation v2: chemistry first

**Scope:** provisional functional annotation and navigation for the unchanged
PNAS2017 968-reaction source network. This table answers which functional
stage a source reaction depicts. It does not decide whether a reaction or
state may be removed or approximated.

## Evidence order

1. Explicit reactant/product chemical event and the approved RS pathway rules.
2. Identity of a specific mechanistic intermediate.
3. Local reaction–species graph context, limited to the v1 one-to-three-hop
   interpretation where no hard chemistry rule applies.
4. Source Level-A/Level-B subsystem provenance as supporting context.
5. A review exception when the above leave a real boundary or conflict.

CellDesigner `HETERODIMER_ASSOCIATION`, `DISSOCIATION` and `STATE_TRANSITION`
describe source reaction *form*, not the functional stage. The v2 generator
uses a state transition as hard evidence only for selected explicitly named
chemical stages; it does not assign RS binding or charging from CellDesigner
type. In the RS network, preactivation substrate assembly is `RS_binding`;
ATP-to-aminoacyl-AMP conversion, PPi handling and aminoacyl-AMP release are
`RS_activation`; postactivation tRNA recruitment, aminoacyl transfer, charged
tRNA release and aaRS-bound AMP reset are `RS_charging`. The approved Gly rules
are applied to the corresponding Met equations only after actual reactants,
products, parameter topology and intermediate identities are checked.

`GlyRS_Gly_ATP ⇄ GlyRS_GlyAMP_PPi` and its Met counterpart are hard
`RS_activation` anchors. `GlyRS_AMP ⇄ GlyRS + AMP` and the Met counterpart are
`RS_charging`. The tRNA encounter with enzyme-bound aminoacyl-AMP/PPi is a
true `RS_activation;RS_charging` boundary. These explicit rules take priority
over the inherited v1 graph label. The earlier v2 RS audit corrected 32
reaction contexts; this initiation update corrects another 90.

## Human-approved Initiation classification rules

For `RFAM_025` and `RFAM_026`, the reaction-local pathway state takes priority
over graph proximity, family context, CellDesigner reaction type and source
subsystem label. Apply the following rules in order, in both directions of an
exact reverse pair:

1. Explicit `RS30S_xxx + RS50S ⇄ RS70S_xxx` joining/splitting is
   `INIT_70S_formation`. `re0000000461/0462` and `0485/0486` are examples.
2. IF2-bound `GTP ⇄ GDP_PO4` conversion or `IF2_GDP_PO4 ⇄ IF2_GDP + PO4`
   is `INIT_energy_commitment`. The latter includes source
   association/dissociation representations `0721/0722` and `0745/0746`.
3. A change in **ribosome-bound** `fMettRNAfMetCAU` occupancy is
   `INIT_tRNA_recruitment`. Cargo-bound `IF2_GTP_fMettRNAfMetCAU` counts only
   when the initiator tRNA enters or leaves a ribosome complex. The initiator
   tRNA remaining bound on both sides is not recruitment.
4. IF1, IF3 or IF2_GDP release/rebinding on a formed 70S initiation complex
   carrying initiator tRNA, mRNA or an IF2 GDP state is
   `INIT_factor_release`. This includes `0539/0540`, `0719/0720` and
   `0723–0726`. The `elRS70S...` elongation-entry representation of the
   complex remains ribosome bound when evaluating tRNA occupancy.
5. Otherwise, initiation-factor or mRNA assembly/disassembly on the complex
   is `INIT_assembly`. Bare/preinitiation 70S + IF3 in `0457/0458`, 30S +
   IF3 in `0459/0460`, and IF2_GTP + 30S complex in `0463/0464` are assembly,
   even if adjacent graph basins have other labels.

The source equations in both families were checked one by one against this
precedence. All 198 rows have one direct stage, with 99 exact reverse pairs
retaining identical contexts. Their former 70 graph-derived shared junctions
are not reaction-local two-stage events and are removed from the v2 status.
The 22 cross-family intermediate links remain as provenance, but a link does
not reopen an already human-approved local functional stage. No other family
context, status or queue flag changed in this update; a verifier fingerprint
guards that boundary.

## Graph and cross-family context

The v1 968-reaction/241-species graph and 35 active families plus `RFAM_DEG`
remain the seed topology. A currency/resource hub is a species used across
unrelated biochemical events, such as free ATP, ADP, AMP, GTP, GDP, PO4, PPi,
free amino acids, free ribosomal subunits and ubiquitous free factors. These
cannot establish a mechanistic link merely by adjacency or low graph degree.
A specific intermediate has molecular identity tied to a pathway state, for
example `GlyRS_AMP`, `MetRS_AMP`, ribosome–factor complexes or a specific
peptidyl-ribosome state. The builder applies explicit identity patterns and
records qualifying connections across source subsystem boundaries in
`reaction_cross_family_links_v2.csv`. It does not merge families simply
because they share an intermediate. In particular, active chemistry gives
`RFAM_010 → RFAM_006` via `GlyRS_AMP` and `RFAM_012 → RFAM_008` via
`MetRS_AMP`.

Each exact reverse-stoichiometry pair keeps one family, one functional context,
one junction status and one reference-activity class. A reverse pair is a
structural source relation. It says nothing about fast equilibrium. The
`FORWARD_ONLY`/`REVERSE_ONLY` labels describe which direction in the canonical
lower-ID pair has a nonzero official parameter; both rows of a pair receive
the same class. Two zero parameters give `DISABLED_EXACT`. Such reactions
remain in the source and may retain functional context, but are never hard
anchors or propagation sources. `RFAM_009` is an example. This is a reference
parameter fact, not a permanent deletion decision.

## Status and audit semantics

`DIRECT_CHEMISTRY` means an explicit approved chemical rule or narrowly
identified event controls the label. `GRAPH_PROPAGATED` means the provisional
v1 context has a matching v2 hard anchor within one to three reaction hops.
The generator recomputes these paths using non-disabled reactions and hard
anchors only; it never reuses v1 supporting-anchor IDs. A v1 context without
such support, in conflict with its nearest hard anchor, or tied between
different hard-anchor contexts is marked
`HUMAN_REVIEW_REQUIRED` while preserving the old candidate label for review.
`SHARED_JUNCTION` retains all plausible functional basins and leaves the
primary stage blank. `REFERENCE_DISABLED` takes precedence in the status
column for double-zero rows; its context remains separately visible. The
`reference_activity` and `direct_chemistry_rule` columns retain both facts.
The v1 source/audit, resource-ledger and conservation columns are carried
forward unchanged. Its `topology_status`, `anchor_source` and `human_review_status`
columns are historical v1 fields; v2 authority is in the new columns.

`functional_annotation_unresolved` counts rows whose inherited v1 candidate
context has no matching v2 hard-anchor support and therefore needs a new
functional decision. `human_functional_review_queue` counts flagged v2 exception rows:
shared stage boundaries, specific-intermediate source-subsystem crossings,
and a representative row for each family with several stages. A resolved
chemistry correction or exact double-zero parameter state remains traceable
in the v2 table without automatically sending it for another human decision.
The queue is deliberately independent of reduction review. A queue row asks
about its functional context or family boundary; it cannot approve a
transformation. Where a family has several stages, the representative row
flags family-level review, not every member as uncertain.

The full 968 rows were checked against source IDs, equations and official
parameter values. The hard rules cover the approved RS and initiation cases,
explicit degradation and nucleotide/enzyme state conversions, and selected
named pathway state transitions. Other v1 labels remain provisional graph-supported
assignments or are sent to functional review when hard-anchor support fails.
The presence of a candidate context does **not** mean every functional
assignment has been independently confirmed; the review
queue and stage provenance must be considered together.

## Reproduction

```text
python scripts/build_reaction_level_annotation_v2.py
python scripts/verify_reaction_level_annotation.py
```

The manifest binds the source v1 table, untouched reduction decision table,
source SBML identity and four generated CSVs by SHA-256. The builder is
deterministic and uses only checked-in Python standard-library inputs. v0 and
v1 files remain as an audit trail.

**Scientific boundary:** no QSSA, fast equilibrium, timescale separation,
lumping, reaction deletion, chemostat, kinetic equivalence or reduced-core
kinetics is approved here. All 968 reduction decisions remain `PENDING`.
