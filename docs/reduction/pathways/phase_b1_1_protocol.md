# Phase B1-1 — bounded initiation reconstruction protocol

Authority: the researcher's supplied B1-1 task, dated 2026-10-09 (Asia/Shanghai).
Implementation and local tests are authorized. B0 is `B0_FORMALLY_ACCEPTED_LIMITED_SCOPE`;
B1-1 remains `PENDING_HUMAN_REVIEW`. B1-2, full Phase B and commit/push are not authorized.
Historical Phase A/B0 authorization fields describe their original checkpoints and
remain byte unchanged. The only checkout is sean's `C:\Users\sean\Desktop\GUV`,
branch `codex/energy-cycles-v1`. The complete beginning tracked-byte manifest is
[phase_b1_1_source_baseline.json](phase_b1_1_source_baseline.json).

## Authority and scope

Canonical SBML species, directed reaction IDs and constant MathML coefficients are
the chemical authority. The original author parameter CSV must match its archived
copy. Reviewed Level-C v2 labels and source family/subsystem records supply context,
without changing stoichiometry. The published B0 W3 supplies actual event identities
for composition. Carrier/moiety interpretations from composite names remain
`INFERRED`; boundary availability remains an explicit conditional assumption.

The source index is read for all 241 species and 968 directed reactions, with 3,854
weighted Petri arcs. This is indexing, not reconstruction of all pathways. The
search scope is the union of reviewed contexts beginning `INIT_` and RFAM_022–026.
The bounded context inventory adds one-hop incidence at initiation complexes,
free ribosomal/factor source states, the E1/E2 interfaces, and the single shared
Met-tRNA/formylated-tRNA pools; it adds used B0 directions, exact inverses and
the 0414 coefficient safeguard. Free subunit and tRNA incidence brings in many
disabled source sinks from other modules. Those remain context only, excluded
from searches and witness sums. No other elongation, termination or recycling
pathway is reconstructed. No completeness claim follows from this inventory.

## Endpoints, search and alternative scenarios

E1 is `elRS70SAGGU0002_fMettRNAfMetCAU`, the source-model initiation exit. E2 is
`elRS70SAGGU0002_fMet`; one actual `re0000000001` converts E1 to E2 and releases
`tRNAfMetCAU`. Its context must remain `ELONG_tRNA_release`. Reaction 0013 is
only a conditional first elongation binding encounter, with explicit EF-Tu/Gly-tRNA
complex supply; it is not a completed elongation round.

Discovery is breadth-first over complete exact rational markings. Every candidate
transition requires all original reactants. Positive source parameters select the
search view; zero directions and exact reverses remain in the context inventory.
Ordered source-state waypoints choose representative IF3-first, IF1-first,
IF1-absent and IF2-early-release scenarios. No complete reaction-ID sequence is
embedded in discovery. Each leg chooses the shortest enabled route to its next
state, sorted by original reaction ID, with 50,000 visited-state and 16-event depth
limits. Visited markings, selected legs and bounds are saved. This is a bounded
representative search; it does not enumerate all initiation paths or rank kinetics.

The main route requires formation of the dual-factor 30S/mRNA precursor from free
RS30S, IF1, IF3 and mRNA, followed by IF2 recruitment, independent RS50S input,
70S formation, GDP/PO4 and GDP source states, factor release and E1. A source
state waypoint that omits one intermediate factor need not pick the prompt's
example release order; actual discovered directions are retained and audited.
Different assembly and release orders are separate witnesses. Rejoins require
the exact same original species and a checked common suffix. They are never
summed as consecutive outputs of the same carrier.

P2 references P1 occurrences once and adds 0001. P5 composes all 14 published
W3 occurrences once with P1 and supplies no second IF2/formylated-tRNA token.
P5-E2 adds the boundary once. P6 replaces external IF2_GTP with IF2 plus free
GTP and one actual 0445 event; its ledger is recomputed. P7 uses P2 and a
declared `EFTu_GTP_GlytRNAGlyGCC` supply for one 0013 occurrence.

## Exact arithmetic and stronger provenance acceptance

For each source r, S[:,r] = beta_r - alpha_r. Each witness is an occurrence vector
w and has exact net nu = S w, independently recomputed with `Fraction`.
Formal markings obey m[k-1] >= alpha_r and m[k] = m[k-1] + S[:,r]. They are
reaction inventories, not concentrations, experimental initial conditions or
trajectories. The source parameter sign establishes directional reference
activity, not positive flux.

Each event has a unique identity and occurrence origin. Input allocations consume
finite tokens from an exact earlier producer or explicit boundary. DAG edges
record producer, consumer, exact species, rational amount, role and evidence.
The saved order is one topological order; independent precursor branches carry
no artificial chronological edges. The verifier recalculates all markings,
checks token amounts, reconstructs DAG edges and requires actual productive
target tokens. Petri-enabled mutations with independent extra tokens can still
fail the requested lineage. Shared ATP/GTP/GDP/PO4 is not carrier identity.

Free source-state recovery requires a supplied seed, equal final amount, exact
zero net and an actual source event restoring that free state. IF1/IF3 recovery,
MetRS/MTF recovery, IF2_GDP release, nucleotide-state recovery and ribosome
incorporation remain separate claims. IF2_GTP is not regenerated. RS30S and RS50S
are incorporated into an endpoint, not recovered. The free-species ledger
tracks ATP/AMP/PPi/FD/THF and all task-specified factors, nucleotides and tRNA
states. Bound GTP-to-GDP/PO4 transitions are source-state changes; free GTP has
zero net in initiation-only P1 and -1 only when 0445 is actually included.
No global nucleotide-moiety certificate or invented mRNA release is asserted.

The MTF entrances 0420/0422 and EF-Tu entrance 0288 consume one original
`MettRNAfMetCAU` pool. Their co-reactants and inverse 0289 remain visible.
Both 0449/0450 have positive author parameters; an inverse is never an automatic
occurrence, and reversible binding is not equilibrium.

## Acceptance and safe execution

The new verifier imports no new builder. It uses the previously audited B0
read-only parser/hash helpers, whose independent MathML implementation differs
from the builder's source parser; it implements B1-1 membership, occurrence,
net, marking, ledger, origin, DAG, endpoint, rejoin and composition acceptance
independently. The researcher reading document's full source equations are
checked too. Candidate JSON carries no self-awarded scientific PASS.

Gates A–H require source integrity, true 30S assembly, IF2/fMet-tRNA recruitment,
50S/GDP/PO4 transitions, E1, E2, alternatives/competition and exact nets/ledgers.
Gate I executes N01–N20 through the same acceptance functions, preserving the
mutated fixtures and expected/actual codes. N10/N11/N18/N20 must be Petri-enabled
while their claimed lineage is rejected; rejection for unrelated enabling
failure is insufficient. Supplements check another coefficient and genuine
repetition/reordering of independent precursors.

Gate J executes Phase A tests in temporary copies, B0 verification/negative
controls with its report and failure destinations redirected to temporary
copies, existing read-only HTML acceptance and browser functions using installed
dependencies, two deterministic B1-1 builds, and all beginning tracked hashes.
B0 defaults must never be run where they can overwrite accepted reports.
All actual commands, outputs, failures and exit codes belong to B1-1 evidence.

Only all executed gates A–J passing can produce `execution_status=COMPLETED` and
`engineering_status=PASS`. Scientific status always remains `PENDING_HUMAN_REVIEW`.
No acceptance, commit, push, reduced model, QSSA, effective rate, kinetic
equivalence or Phase B1-2 follows from these structural checks.

Reproduce from the existing repository with:

```powershell
python scripts/pathways/phase_b1_1/run_phase_b1_1_validation.py
```

The runner preserves old artifacts, routes all new reports to B1-1, and retains
real failures. It does not synchronize branches, commit or push.
