# Reaction functional annotation v2: chemistry first

**Scope:** completed functional-stage annotation review and navigation for the unchanged
PNAS2017 968-reaction source network. This table answers which functional
stage a source reaction depicts. It does not decide whether a reaction or
state may be removed or approximated.

## Evidence order

1. Explicit reactant/product chemical event and the human-approved local rules.
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
reaction contexts; the earlier initiation update corrected another 90.

## Additional human-approved functional rules

The following rules classify the reaction-local event in both directions of
each exact reverse pair. They are functional annotation decisions only.

* `RFAM_013`: EF-Tu/EF-Ts GDP/GTP binding, release and exchange-state
  assembly (`0261–0274`) is `ELONG_energy_coupling` (14 rows). Formation or
  dissociation of the EF-Tu-GTP-aa-tRNA carrier (`0275/0276`, `0288/0289`)
  is `ELONG_aa_tRNA_delivery` (4 rows). The former block does not imply GTP
  hydrolysis at every step.
* `RFAM_015–017`: CK, NDK and MK substrate/product binding or release is
  `EN_binding` (16 rows per family), including product-side release.
  Only enzyme-bound chemical conversions `0338/0339`, `0363/0364` and
  `0388/0389` are `EN_energy_transfer` (2 per family). A zero reverse
  parameter for `0364` changes reference activity, not its stage.
* `RFAM_018`: PPiase binding and product release (`0405/0406`, `0409–0412`)
  is `EN_binding` (6); bound PPi to two bound phosphate groups (`0407/0408`)
  is `EN_byproduct_processing` (2).
* `RFAM_033/034`: RF1 and RF2 binding/release on pre/posttermination
  ribosomes is `TERM_factor_binding` (4 each). Peptidyl-tRNA to free peptide
  and posttermination ribosome (`0798/0810`, `0813/0823`) is
  `TERM_peptide_release` (2 each). Both source equations were inspected;
  CellDesigner association/dissociation types do not set these stages.
* `RFAM_022`: IF2 GTP loading (`0445/0446`) is
  `INIT_energy_commitment` (2), meaning preparation of a GTP-loaded IF2
  state without claiming hydrolysis. IF2-GTP-fMet-tRNA cargo formation
  (`0449/0450`) is `INIT_tRNA_recruitment` (2). This extends recruitment
  to the pre-ribosome cargo; IF2-GTP binding to a ribosome without a tRNA
  cargo change remains `INIT_assembly`.
* `RFAM_024`: bare `RS30S + RS50S ⇄ RS70S` (`0455/0456`) is
  `INIT_70S_formation` (2), under the same explicit joining rule used for
  occupied subunits.

Approved local rules take priority over graph conflicts, equal-distance
anchors, family span flags and cross-family mechanistic links. Such links
remain recorded, while the resolved rows leave the live human functional
queue. `RFAM_035` retains its previous scientific labels. The non-target
scientific fingerprint is checked by the verifier.

## Final human-approved elongation and recycling rules

The final mechanistic audit fixes every source reaction in `RFAM_002`,
`RFAM_004` and `RFAM_014` by explicit reaction ID, family and stage. These
rules have priority over graph proximity and source CellDesigner form.

* `RFAM_002` and `RFAM_004` each have 10 `ELONG_aa_tRNA_delivery`, 8
  `ELONG_energy_coupling`, 2 `ELONG_peptide_formation`, and 4
  `ELONG_translocation` reactions. EF-Tu-GTP-aa-tRNA docking,
  accommodation-associated EF-Tu release and the corresponding source side
  paths are delivery. EF-Tu/EF-G nucleotide conversion and phosphate handling
  without ribosome positional change are energy coupling. The fMet-to-Pept0002
  and Pept0002-to-Pept0003 reactions are peptide extension. A codon or
  positional shift is translocation even when phosphate or EFG_GDP is also
  released. The two cycles have matching functional and reference-activity
  patterns; this makes no kinetic-equivalence claim.
* The four double-zero delivery paths in each elongation family retain their
  approved `ELONG_aa_tRNA_delivery` context and `REFERENCE_DISABLED` status.
  They are never propagation anchors.
* `RFAM_014` has 18 `ELONG_energy_coupling` rows covering free EF-G GDP/GTP
  loading/reset, elongation-side ribosome recruitment, bound GTP conversion,
  phosphate handling and EF-G release. Its 14 `RECYCLE_disassembly` rows cover
  posttermination RRF/EF-G assembly, energy chemistry and explicit 70S
  splitting (`0910/0957`). Its 24 `RECYCLE_component_release` rows are
  post-split mRNA, tRNA, RRF and EFG_GDP release/rebinding and cleanup.
* `0308/0327`, `RS50S_EFG_GDP ⇄ EFG_GDP + RS50S`, remain the true
  `ELONG_energy_coupling;RECYCLE_component_release` `SHARED_JUNCTION`.
  This state can occur in both elongation-side and posttermination histories;
  neither stage is discarded. Together with `0207/0208` and `0249/0250`,
  these are six human-approved junction rows.

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
   `INIT_tRNA_recruitment` within `RFAM_025/026`. The initiator tRNA
   remaining bound on both sides is not recruitment. The separately approved
   `RFAM_022` pre-ribosome IF2-GTP-fMet-tRNA cargo rule above extends the
   stage definition without changing these family-specific cases.
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
not reopen an already human-approved local functional stage. The final audit
guards all non-target scientific labels, statuses and source fields with a
baseline fingerprint; live queue bookkeeping changes separately.

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

`DIRECT_CHEMISTRY` includes an explicit human-approved reaction-local
mechanistic rule; a covalent transformation is not required. `GRAPH_PROPAGATED` means the provisional
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

`functional_annotation_unresolved` counts rows still requiring a new human
functional decision. `human_functional_review_queue_v2.csv` is the **live**
queue for exactly those rows. Approved direct rules, shared junctions,
cross-family links, families spanning several stages, resolved graph conflicts
and disabled reference channels do not enter the live queue merely because
they have audit interest. Their evidence remains in the reaction table, link
table and manifest. The live queue is independent of reduction review and is
empty after this completed functional audit.

The full 968 rows were checked against source IDs, equations and official
parameter values. The hard rules cover approved RS, elongation, initiation,
enzyme and termination cases, plus explicit degradation and other identified
events. Fifty rows retain `GRAPH_PROPAGATED` status and their graph provenance;
the completed review means no row currently requires another human functional
decision. It does not convert graph evidence into direct chemistry evidence.

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
