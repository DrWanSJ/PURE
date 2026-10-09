# Phase B0-1 multi-carrier structural protocol

Scope: W1 GlyRS–EF-Tu–ribosome binding, W2 MetRS–MTF formylation and its
alternative entry, W3 MTF product–IF2 binding. This is a finite local structural
test, not full-network pathway enumeration or kinetic reduction. Scientific
The automated B0-1 contract retains `PENDING_HUMAN_REVIEW` separately from the
researcher's subsequent decisions. Current user-supplied B0-2 status is
`B0_2_CONDITIONALLY_ACCEPTED`, with final formal signoff pending;
`phase_b1_authorized = false`. See [the B0-2 review record](phase_b0_b0_2_review_record.md).

## Source authority and immutable evidence

1. Canonical SBML: `models/pnas2017_full_reference/original/fMGG_synthesis.xml`.
2. Author parameter ZIP and its original CSV copy; their CSV bytes must agree.
3. Reviewed `docs/reduction/reaction_level_annotation_v2.csv`.
4. Existing family/context and cross-family records, for interpretation only.
5. Verified Phase A graph, for GlyRS-P01 and MetRS-P01 starting IDs only.
6. New provisional multi-carrier projections, explicitly `INFERRED`.

The independent verifier pins the published Phase A source hashes, reparses
SBML and author CSV, and checks all 241 species, 968 directed reactions,
3,854 weighted arcs, 485 zero parameters, and the `2 PO4` coefficient in
`re0000000414`. It uses a separate constant MathML implementation. No source,
parameter, existing report, annotation, HTML or existing script is edited.
`phase_b0_source_baseline.json` captures every existing tracked file's raw
SHA-256 before implementation, bound to the clean synchronized starting HEAD.
That preservation manifest supplements the pinned reference hashes; it does
not replace source authority. Independent regression reparses the full Phase A
Petri matrix and original equations.

FD's biochemical identity is **10-formyltetrahydrofolate (10-甲酰四氢叶酸)**.
Matsuura et al. 2017, DOI [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114),
explicitly identifies FD in the inline SI Results / Model Construction section
“Model construction for formylation of initiator tRNA”, referring to
FMet_tRNASynthesis and Dataset S21. [Original article and SI text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/).
This resolves the earlier FD documentation gap while retaining source IDs and
parameters. It does not establish a full composition certificate for complexes,
observed flux or kinetic dominance; no new formula or ionic parameters are added.

## Exact stoichiometry and occurrences

For each directed source reaction r, alpha_r and beta_r are exact nonnegative
input/output multisets, read from actual `stoichiometryMath` constant MathML.
Every rational is represented by `Fraction`, serialized as an exact string.
S[:, r] = beta_r − alpha_r. For a finite witness, w_r counts actual directed
event occurrences, and nu_net = S w. Both signs are retained. Reverse partners
are source context; they are never automatically fired or added to w.

Event IDs and occurrence origins identify actual events. A shared occurrence
referenced from W2 while composing W3 occurs once; a duplicated event/origin
is rejected. Legitimate repetition has distinct event/origin IDs and a count
greater than one. A repeated two-cycle MTF positive control verifies this.
Separate W2-MTF and W2-ALT records are alternative test scenarios, not events
to be summed into one combined witness.

## Explicit boundary and Petri enabling

The marking m contains formal stoichiometric tokens, not physical counts or
concentrations. A firing r at k requires m[k−1] >= alpha_r componentwise;
then m[k] = m[k−1] + beta_r − alpha_r. Missing exact input species produce
`MISSING_REQUIRED_INPUT`. Required tokens are never inserted to repair a test.

Each boundary record includes the source species ID, positive exact amount,
role, declared source assumption, consuming events, and whether full-model
availability is independently justified. Every positive B0 scenario explicitly
uses amount 1 for each listed seed/substrate; its availability justification
is false. This is an auditable finite conditional test. All initial, final and
per-event markings are preserved. Required nucleotide, tRNA, amino acid,
cofactor, enzyme and factor species remain source-exact. Free ADP/GDP/PO4 may
have net zero; a named nucleotide-containing complex does not provide an
independently proven component conservation ledger.

## Event DAG and carrier evidence

Each consumed input is allocated to an exact boundary token or an earlier
event's output token. The verifier checks that the producer really generated
that species and that its unconsumed amount suffices. The resulting producer
edges form an event DAG; the saved firing sequence is one valid topological
order. Independent branches have no artificial chronological edges.

W2's 0418 prepares MTF_FD independently of MetRS. 0224 releases MettRNAfMetCAU.
Their tokens converge at 0422. 0170 enzyme recovery can occur independently of
the downstream MTF branch. 0428 product release precedes the IF2 handoff;
0434 MTF recovery need not precede that handoff. The chosen order is a finite
witness, not a claim about biochemical chronology.

Exact source-species handoffs check source event/product, target event/reactant,
amount and producer provenance separately from global Petri enabling. N05
supplies enough independent extra molecules to enable 0420 and 0422 while
claiming an invalid same-MTF history: it must pass enabling and fail lineage.
ATP/GTP and other ordinary resource species cannot certify carrier identity.
N09 exercises that rejection with independently enabled enzyme reactions.

Composite carrier streams are source-name/context projections with actual
source species before/after each event. They remain `INFERRED` and
`HUMAN_REVIEW_REQUIRED`; names alone do not verify molecular composition.
Exact species flow is extracted and independently checked without silently
promoting those projections. Molecular identity, biochemical chronology and
full-network availability remain distinct questions.

## Alternative entries, branches and cancellation

FD-first 0418/0422 and Met-tRNA-first 0420/0424 meet at the true shared source
species MTF_FD_MettRNAfMetCAU. The alternative is tested separately, retaining
0421/0423 inverse outlets and 0427's zero parameter. A bounded source incidence
appendix preserves all original entrances/exits at selected enzyme and charged
tRNA anchors, including alternative exits and sinks. Appendix references are
not counted in the witness net; this does not certify new pathways.

For declared internal species I, S_I w must be exactly zero. Recovery claims
also require a supplied catalyst to be restored in the final marking, zero net
change and a produced target output. `COMPLETE_CATALYTIC_CYCLE` is used for the
five-step W2-MTF subwitness, which releases free fMettRNAfMetCAU and recovers MTF.
W2 is a combined structural handoff with MetRS/MTF recovery. W1 and W3 end
at bound interfaces and are `INTERFACE_ONLY`; they cannot be promoted to
complete elongation/initiation cycles.

## Directional activity and status boundaries

Author k > 0 means `REFERENCE_ENABLED`; k = 0 means `REFERENCE_DISABLED`.
Neither means positive trajectory flux, pathway dominance, equilibrium or
timescale separation. An exact reverse pair is two separate source directions.
Disabled reactions remain in source context and are not deleted.

Specifically, `re0000000449` and its exact inverse `re0000000450` both have
author-reference k1 = 40. W3 counts only the selected 0449 event, but IF2
binding must not be interpreted as irreversible. Equal numeric values for
different reaction orders do not establish equilibrium.

`MettRNAfMetCAU` is a shared substrate pool for the MTF entrances
`re0000000420/0422` and EF-Tu entrance `re0000000288`. The existing source
incidence appendix retains those equations and reverse partners. Any separately
authorized B1 must preserve competition for the one source pool; separate B0
boundary scenarios cannot be summed as if each module owned another copy of
the same finite Met-tRNA supply. The 2026 EF-Tu study cited in the B0-2 review
record provides supporting context, with abstract-only coverage and its
model-based/experimental evidence distinguished. No B1 implementation is added.

`SOURCE_REACTION_VERIFIED` records exact source agreement;
`STRUCTURAL_HANDOFF_WITNESS` records enabled finite events and exact producer
flow; `COMPLETE_CATALYTIC_CYCLE` additionally records release/recovery;
`INTERFACE_ONLY` marks a bound endpoint; `UNRESOLVED` and
`HUMAN_REVIEW_REQUIRED` preserve insufficient biochemical identity evidence.
Automated gate PASS never grants researcher approval or Phase B1 authorization.

## Executed acceptance contract

Independent source and witness tests cover Gates A–E, including source hashes,
all co-reactants, token lineage, true rejoin, exact nets, catalyst recovery and
scope endpoints. Gate F runs N01–N12 and supplemental mutations through the
same acceptance routines as positives. Gate G runs the existing Phase A
verifier, its mutation/reproduction suite in a temporary artifact directory,
and safe read-only calls to the existing HTML regression functions. Any
unavailable browser is `NOT_RUN`; no package or browser is installed.

Build twice into temporary directories and compare both deterministic outputs
with delivered bytes. Save commands, exit codes, counts, raw outputs, regression
reports, actual failures and the final aggregate report. Preserve failed
attempts rather than rewriting history. All deliverables are additive and
local; stop at the B0-2 researcher checkpoint without commit, push or B1 work.
