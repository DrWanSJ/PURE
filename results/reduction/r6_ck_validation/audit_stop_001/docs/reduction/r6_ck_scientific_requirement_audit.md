# R6 CK scientific-requirement audit

**Decision: GROSS_FLUX_REQUIREMENT_AMBIGUOUS_HUMAN_DECISION_REQUIRED.**

The scientific-use audit is complete; CK formal validation and first-order baseline validation are both NOT_RUN. The request's Phase 3 requires this stop. The prospective candidate/startup package is frozen, but the final mandatory numerical contract requires a human scientific-use decision. Recommendation: CK_NOT_READY for promotion at this bounded closeout.

The 23-row `scientific_requirement_to_observable.csv` contains source locations, exact excerpts, SHA-256, confidence, interpretation status and the distinction between the audit and validation A–H vocabularies. `evidence_navigation.json` is derived navigation, subordinate to those source records.

## What the evidence establishes

The active use is mRNA-directed fMGG translation with explicit resource identity, inventories, fuel conversion, enzyme occupancy and cumulative resource accounting (REQ01–07, REQ09–12, REQ19). Pept0003 is the released fMGG product. The model card for GFP belongs to the frozen Mavelli benchmark (REQ08); that purpose cannot silently replace the active PNAS use contract.

The human-approved species contract protects free CK, CP, Cr, ATP and ADP trajectories while allowing reconstructable CK bound intermediates. It does not approve any kinetic candidate and does not settle microscopic turnover accuracy (REQ11–13). The exact reverse-pair contract retains forward/reverse kinetics for an exact rewrite, explicitly distinct from fast equilibrium (REQ14).

## Why the two gross-flux branches cannot yet be selected

The general protocol makes cumulative extent mandatory to prevent hidden resource consumption, and writes xi_j for individual reaction integrals (REQ05, REQ15). The CK review card specifically asks for microscopic intermediate flux comparisons and flags forward/reverse information loss (REQ18, `human_reduction_review.md:470–472`). These cannot be silently waived. They also do not explicitly say that accuracy of each of 332/333/336/337 is a mandatory promotion observable. A requested comparison is not automatically a promotion conjunction.

Conversely, resource and occupancy requirements alone do not require counting every fast binding cycle. Gross ATP/GTP production/consumption remains part of the project purpose, but the four candidate fast reactions bind/unbind CP without changing ATP/ADP stoichiometry; catalytic conversion remains dynamic (REQ06–07, REQ23). Whether binding turnover itself is a scientific endpoint is unresolved. R5-C explicitly requires a future mandatory-observable decision (REQ20). Neither past all-968 numerical coverage nor small state error resolves that decision.

There is no explicit CK-specific gross-turnover promotion mandate, and no explicit waiver of its accuracy requirement, in the audited scientific-use contract. The narrow missing decision is whether gross CP-binding rates/extents are essential endpoints or descriptive provenance outputs. This is not a claim that species-level information review is unfinished.

## Reviewable candidate and prospective obligations

`candidate_definition.json` freezes CK_PARTIAL_EQUILIBRIUM_V1, the four fast IDs, unchanged 964 non-fast dynamics, 212 slow coordinates and exact 241-state SOURCE_GENERAL reconstruction. `initial_layer_policy.json` freezes the R5 rule 10*eta*tau0 and retains full startup. The baseline switch is 9.906817032876724e-5 s; its nonzero manifold jump is disclosed, never tuned away.

Under Branch A, the R5-C minimum classes would be A, B, C, D, F and H; E and G would be descriptive/provenance-only and BUT_NOT_VALIDATED. Under Branch B, E/G accuracy would require a derived first-order constitutive reconstruction and startup extent matching, with R3_BASE testing only. These are conditional proposals, not final scientific obligations or approval. New net-current/net-extent thresholds need a semantic and normalization justification before a decisive run; inherited numerical levels alone do not supply it.

## Accounting and numerical status

Exact source-law drift, net stoichiometric accounting, algebraic-state accounting and gross directed-ledger residual remain separate. The independent R6 verifier recomputes canonical structural conservation identities; R6 numerical conservation is NOT_RUN. Historical R5 conservation evidence is retained without extending it across the nine conditions.

0 of 9 conditions executed in R6; the pass count is N/A, not 0/9 failed. R6 worst state, slow-total, protein, current and extent errors are N/A. Historical baseline all241 hybrid post-startup state error is 0.0003383575954227056; R5-C's representative hybrid post-0.05 s net-current scaled error is 0.14712397135760574. These are different historical windows/sample scopes and are not R6 formal results. The current error already cautions against assuming Branch A will pass.

No new numerical failure or domain outcome is assigned. The stopping cause is unresolved scientific-use scope. No first-order reconstruction was run, and no evidence is claimed about gross-rate recovery or startup extent repair. CK is not ready for human promotion review from R6 evidence.

## Required human decision

For CK's CP-binding pairs 332/333 and 336/337, must the reduced candidate accurately preserve each forward/reverse rate and gross directed extent for the intended scientific purpose? Or may those be explicitly descriptive provenance outputs, with states, occupancy, exact conservation and net resource conversion mandatory?

NOT_REQUIRED selects Branch A only after a complete numerical contract and source-reuse verifier are frozen. REQUIRED selects first-order derivation plus R3_BASE testing only. A decision does not promote CK. Historical R3/R4 criteria and outcomes, R5 descriptive status and R5-C corrections remain unchanged. No push, merge or next stage occurred.
