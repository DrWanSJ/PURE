# GlyRS / MetRS pathway prototype — Phase A review

Structural status: **PASS**. Scientific interpretation and Phase B authorization:
**HUMAN_REVIEW_REQUIRED**. Results below come from actual source parsing,
artifact generation, independent verification and mutation tests on 2026-10-09
(Asia/Shanghai). No kinetic simulation or flux ranking is part of this atlas.

## Reading and evidence

Start with [the pathway sample](glyrs_metrs_sample.md). It presents actual
substrate-entry orders, aminoacyl-AMP formation, PPi release, charging,
alternative product-release orders and enzyme recovery. Every one of the 134
scoped reactions has its complete original equation displayed once; repeated
steps link to that equation. The [index](glyrs_metrs_pathway_index.csv) records
all scoped reaction IDs, carrier states, co-reactants/products, labels,
families, reverses, activity, provenance and representative-path membership.

The [graph](glyrs_metrs_graph.json) retains all 241 species and all 968 original
directed reactions, 3,854 weighted Petri arcs, and the exact sparse
stoichiometric matrix. Its Phase A carrier projections preserve simultaneous
aaRS and cognate tRNA participants rather than collapsing a tRNA encounter
into an unconditional enzyme edge. The original 23 Level-C contexts and all
reviewed multiple memberships remain in the full graph.

The [protocol](pathway_first_protocol_v1.md) describes the scope, source
authority and deterministic decomposition. Actual checks are in
[validation_report.json](validation_report.json) and
[negative_controls.json](negative_controls.json). The
[execution log](execution_log.txt) and
[first failure record](failure_evidence.jsonl) retain the unsuccessful first
run as well as later successful execution. The generator and verifier are
separate implementations; the verifier independently reparses canonical XML
and the author parameter archive and checks the actual Markdown equations.

## Scope and topology counts

| Quantity | GlyRS | MetRS | Total |
|---|---:|---:|---:|
| Nondegraded enzyme carrier states | 15 | 15 | 30 |
| Degraded terminal carrier states | 1 | 1 | 2 |
| Original enzyme-touching directions | 63 | 63 | 126 |
| Nondegradation directions | 48 | 48 | 96 |
| Degradation outlets | 15 | 15 | 30 |
| Additional enzyme-free RS directions | 4 | 4 | 8 |
| Unique Phase A reactions | 67 | 67 | 134 |
| Positive / zero author parameters within scope | 42 / 25 | 42 / 25 | 84 / 50 |
| Representative paths / entries | 10 | 10 | 20 |
| Complete productive catalytic paths among representatives | 4 | 4 | 8 |
| Branch states, including disabled degradation exits | 15 | 15 | 30 |
| Nondegraded structural rejoin states | 15 | 15 | 30 |
| Degraded sink convergence states | 1 | 1 | 2 |
| SCCs / cyclic SCCs | 2 / 1 | 2 / 1 | 4 / 2 |
| Finite shortest-return certificates | 24 | 24 | 48 |
| Nondegradation cross-RFAM consecutive-edge links | 46 | 46 | 92 |
| Positive-parameter branch / rejoin states | 14 / 14 | 14 / 14 | 28 / 28 |

Each nondegraded 15-state carrier graph forms one SCC; the degraded state is
a terminal singleton SCC. The 24 shortest-return certificates per enzyme are
two-step forward/reverse structural returns. The four complete productive
paths per enzyme separately witness eight-step catalytic recovery. Neither
number enumerates all possible cycles or all possible substrate-order and
release-order combinations.

Coverage counts are deliberately separate:

- Original unique reactions retained in the Petri graph: **968 / 968**.
- Unique reactions with Phase A equations and attribution: **134 / 134**.
- Actual full-ID occurrences in the Markdown, including anchors and links:
  **2,058**. This is a reference count, not chemical coverage.
- Unique reaction IDs used by more than one representative path: **26**.
- Scoped reactions without attribution: **0**.
- Source reactions deferred as `OUT_OF_PHASE_A`: **834**.

The eight enzyme-free rows are four exact reverse pairs for free GlyAMP,
MetAMP, Gly-tRNA and Met-tRNA chemistry. All have zero author parameters.
They have complete equations and provenance, with empty enzyme-carrier
fields. This is an explicit noncarrier assignment, not a fabricated enzyme
connection or a missing reaction.

## Required GlyRS witnesses

`GlyRS-P01` is independently checked against the requested eight source IDs:
`re0000000126 → re0000000136 → re0000000205 → re0000000197 →
re0000000189 → re0000000178 → re0000000182 → re0000000145`.
It releases GlytRNAGlyGCC, restores GlyRS, crosses all three RS Level-C
contexts, and spans RFAM_005, RFAM_010 and RFAM_006.

`GlyRS-P02` uses ATP-first binding (`0132/0134`, with complete IDs in the
sample) and ends at the same GlyRS_Gly_ATP state as P01. P03–P06 retain the
other four representative three-substrate association orders. P07 activates
before tRNA binding, releases PPi, then binds tRNA and rejoins charging; P08
binds tRNA to the activated PPi-containing state before PPi release. P09
releases AMP before charged tRNA, and P10 records free GlyAMP rebinding.

From GlyRS_Gly_ATP_tRNAGlyGCC, all **five** original exits are retained:
activation `0197`, tRNA dissociation `0206`, ATP dissociation `0196`, Gly
dissociation `0194`, and disabled degradation `0214`. They share a precursor;
the algorithm never serializes these exits as a four-step pathway. Entries
rejoin at their actual endpoint; complete alternative catalytic routes also
record an independently checked common reaction suffix after a real merge.

## Independent GlyRS / MetRS comparison

MetRS was extracted from its own source reactions before comparison. Both
enzymes have amino-acid-first, ATP-first and tRNA-first entries, activation
with and without prebound tRNA, aminoacyl transfer, both represented
product-release orders and enzyme recovery.

The verifier compares each of the **67** GlyRS-scoped directions to the
independently extracted MetRS scope by an explicit Gly→Met and cognate-tRNA
renaming of complete reactant/product multisets. The resulting mapping is
bijective and is retained in Gate 4 of the validation report. In this local
scope the stoichiometric topology, reviewed Level-C memberships and
zero/nonzero patterns match. **35 paired parameter values match; 32 differ.**
For example, the tRNA-bound activation directions `re0000000197` and
`re0000000239` have different reference parameters. No kinetic equivalence
follows from the local graph mapping.

Downstream interfaces differ. Charged Gly-tRNA has the explicit EF-Tu
interface `re0000000275/0276`; charged Met-tRNA has EF-Tu `0288/0289` and
MTF `0420/0421`, `0422/0423` interfaces. Full IDs and source equations are
preserved in the graph and linked existing atlas. In total **127** directed
external tRNA/charged-tRNA/adenylate incidence records are source-checked;
they are boundary evidence, not 127 certified temporal handoffs.

## Actual acceptance results

| Gate | Result | Evidence scope |
|---|---|---|
| 1 — Source Integrity | PASS | 241/968 identities, all Petri arcs and matrix columns, author parameters, 134 actual displayed equations, all explicit reverse channels; original 0414 retains 2 PO4 |
| 2 — Path Continuity | PASS | 20 representatives; exact consumed/produced carriers, all co-reactants and products, simultaneous enzyme/tRNA projections, true endpoint rejoins and shared continuations, target release and enzyme recovery |
| 3 — Branch Completeness | PASS | All 126 source carrier transitions, 30 branch states, 30 nondegraded rejoins plus 2 terminal sink convergences, 92 cross-family links, exact SCCs and returns, positive-parameter view |
| 4 — Reaction Coverage | PASS | 134 unique scoped equations/index rows; 834 explicit deferred IDs; 8 enzyme-free assignments; 23 source contexts; source-checked boundaries and independent local comparison |
| 5 — Negative Controls | PASS | All 10 actual counterexamples rejected by the same independent acceptance routines |

| Negative control | Expected | Actual source-based rejection |
|---|---|---|
| Force 0206 → 0196 | REJECT | Next step does not consume preceding carrier |
| Serialize mutually exclusive exits | REJECT | Carrier is not consumed at the second purported step |
| Omit required ATP | REJECT | Exact other-reactant inventory mismatch |
| Claim zero-parameter direction enabled | REJECT | Directional parameter-enabled path mismatch |
| Join different enzyme carriers through ATP | REJECT | State belongs to wrong carrier |
| Remove true cross-RFAM link | REJECT | Complete source-derived cross-family set mismatch |
| Treat cyclic SCC as DAG | REJECT | Source-derived cyclic SCC flag mismatch |
| Change 0414 from 2 PO4 to 1 PO4 | REJECT | Exact original product coefficient mismatch |
| Count shared IDs twice as coverage | REJECT | Unique scoped count mismatch |
| Promote incomplete path evidence to VALIDATED | REJECT | Bounded structural evidence status mismatch |

Control 8 uses the **actual** source equation
`PPiase_PO4_PO4 -> PPiase_degraded + 2 PO4`; it does not replace that equation
with a hypothetical free-PPi hydrolysis step. Supplemental checks also
reject omission of required tRNA and corruption of a displayed Markdown
equation, and evaluate constant MathML exactly.

Two fresh builder subprocess runs reproduce the graph, CSV and Markdown
byte-for-byte and match the delivered files. The test snapshot confirms
**1,678** existing tracked model/reference/result/reduction-document files
unchanged during those runs. Final Git scope review checks all existing
tracked files, including previous scripts and research. Tests ran using the
existing Python runtime and NetworkX; no dependency installation was needed.

The first run failed on erroneous interior-state rejoin records and mixing
the Level-C DEG_sink label into the pathway-type field. The generator was
corrected; the original checks remained in place and were subsequently
strengthened for simultaneous carrier projections, shared suffixes and
external boundaries. Failed evidence remains in failure_evidence.jsonl.

## Unresolved interpretations and researcher checkpoint

No local enzyme-carrier path is discontinuous, and no scoped reaction lacks
an equation or assignment. Source names support the local enzyme and tRNA
projections; the model lacks a complete molecular-composition certificate
for all complexes. These projections therefore retain inferred identity
status rather than asserting a newly verified global biochemical carrier
ontology.

Researcher decisions required before Phase B:

- Confirm that the explicit 134-reaction scope, finite representatives and
  branch-first reading layout meet the intended pathway interpretation.
- Confirm enzyme/tRNA carrier identity rules and decide how a history across
  EF-Tu, MTF, ribosomal and peptidyl-tRNA composite states should be tracked.
- Review the free adenylate and free aminoacyl-tRNA boundary pairs and the
  disabled degradation outlets as separately retained source channels.
- Approve expansion and module-specific carrier/milestone rules for
  initiation, each elongation round, RF1/RF2 termination, recycling and the
  four energy enzymes.

The full parser, Petri representation, deterministic graph operations and
independent source checks provide an engineering foundation for Phase B.
The present aminoacylation carrier rules and chemical milestones do not
automatically certify other modules. Per the task's section 11, this phase
stops at the GlyRS/MetRS review checkpoint; full-network pathway
reconstruction and scientific acceptance remain **NOT_ATTEMPTED**.

## Repository delivery context

Computer: sean. Existing repository: `C:\Users\sean\Desktop\GUV`.
Branch: `codex/energy-cycles-v1`. Starting HEAD:
`152047da1fea4e80b1b5231594c5f70122c06e98`.
Startup checks confirmed origin `https://github.com/DrWanSJ/PURE.git`, clean
tracked tree and `0/0` upstream relation; previous energy-cycle research was
closed out and published. This task adds only the two pathway directories.
The final delivery message records the new commit, ordinary push result,
remote HEAD comparison and final Git status. No branch or worktree was
created and no existing scientific source or decision was overwritten.

The new directory attributes preserve native report/log bytes. Publication
checks explicitly recognize CRLF as a line ending while retaining ordinary
blank-at-eol, blank-at-eof and space-before-tab checks; the initial default
Git check had interpreted native CR characters as trailing whitespace.
Staged Git blobs are compared byte-for-byte with the actual files before
commit. This handling changes no scientific acceptance check or threshold.
