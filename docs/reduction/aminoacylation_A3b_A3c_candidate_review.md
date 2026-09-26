# A3b vs A3c — aminoacylation reduction candidate review (2026-09-26)

Record class: CANDIDATE COMPARISON REVIEW (Phase 8 of the 2026-09-26
execution instruction). Factual comparison before any formal run; no
winner is selected by state count. Both candidates were designed under
the Phase-2 coordinate framework (T = [A; Q], rank(T) = 241 required).

## Candidate definitions

### A3b — total-coordinate / tQSSA

Slow coordinates y (220 rows) = 212 identity rows + 8 protected-ledger
total rows, each total replacing the identity coordinate of one free
carrier:

| ledger total row | replaces |
|---|---|
| MetRS_total (15 members) | free MetRS |
| GlyRS_total (15 members) | free GlyRS |
| tRNAfMetCAU_total (44 members) | free tRNAfMetCAU |
| tRNAGlyGCC_total (58 members) | free tRNAGlyGCC |
| adenine_ledger_total (39 members) | free ATP |
| phosphate_ledger_total (123 members, P-weighted) | free PPi |
| Met_material_total (13 members, binit) | free Met |
| Gly_material_total (13 members, binit) | free Gly |

Fast coordinates q (21) = the registered A3a eliminated set (initial A3b
attempt per Phase 6, so the effect of changing coordinates is isolated).

Verified properties (`../audit/pnas2017_aminoacylation_A3b/`):

- rank(T) = 241 exactly (two independent modular proofs + numeric),
  cond(T) = 4.05e2 (B1/B2);
- every protected ledger lies in rowspace(A) BY CONSTRUCTION — each is an
  A row — which removes the A3a sliding-leak mechanism structurally:
  a changing q cannot move any ledger total except through the retained
  interface-flux rows (Phase 4B criterion);
- the five exact rows (enzyme x2, tRNA x2, phosphate) have identically
  zero reduced dynamics on the active network (their only (w^T S)-violating
  reactions carry k1 = 0); the adenine row moves exactly by its 8 MK
  binding-scope fluxes and the Met/Gly material rows by their 6/2
  interface fluxes — external exchange is retained, not frozen (Phase 4C);
- closure G(y, q) = Q f(R(y, q)) is the registered author-RHS row set;
  it is degree 2 in q (NOT affine — 29 enzyme-binding reactions couple the
  reconstructed enzyme and substrate carriers), so the registered damped
  projected Newton closure discipline is retained (Phase 6A);
- exact pre-QSSA validation B1-B10: 11/11 PASS (Phase 5;
  `verify_pnas2017_aa_a3bc_preqssa`).

### A3c — conservative restricted-QSSA

Selection rule (structural, Phase 7): a complex is eligible for algebraic
elimination only if, after accounting for the exactly reconstructed enzyme
totals, its algebraic motion creates no unresolved contribution to any
protected ledger row. Protected rows examined: both tRNA families (exact
global), the phosphate ledger (exact on the active network), the adenine
ledger (interface balance), and the Met/Gly material rows (resource
accounting with active interface fluxes).

Mechanical result (`../audit/pnas2017_aminoacylation_A3c/
a3c_eligibility.json`): **0 of the 21 complexes are eligible.** Every
eliminated-complex candidate carries tRNA-family tokens (12 states), or
adenylate/phosphate tokens (16 states), or amino-acid material tokens
(MetRS_Met, GlyRS_Gly), and in each case the algebraic motion of that
content is exactly the A3a sliding-leak identity
d/dt(ledger) = d/dt(eliminated token content) that Phase 12 forbids.
The v1r3 investigation already demonstrated dynamically that
substrate-ledger reconstruction is not a benign repair (fail-closed
closure loss at t = 2.501 s), so the conservative rule keeps the free
substrates integrated and therefore cannot eliminate any of the 21
complexes.

Disposition: **A3c is REFUSED BY ITS OWN SELECTION RULE** — the
conservative candidate degenerates to the unreduced model; there is no
restricted-QSSA candidate to smoke-test. This is a scientifically
defensible negative/limit result, recorded with the full classification
table. (Counterfactual for human review: if the Met/Gly material rows
were reclassified as unprotected, {MetRS_Met, GlyRS_Gly} would become
eligible; the classification table records the blocking rows per state.)

## Comparison table

| | A3b | A3c |
|---|---|---|
| eliminated states | 21 | 0 (rule-refused) |
| retained coordinates | 220 (212 identity + 8 ledger totals) | 241 (unreduced) |
| dynamic dimension | 220 (215 non-constant) | 241 |
| algebraic dimension | 21 | 0 |
| protected ledgers | all 9 exact by construction (coordinate rows) | trivially exact (no elimination) |
| exact reconstruction | 8 free carriers from ledger totals | none needed |
| interface handling | retained as coordinate dynamics (adenine/Met/Gly rows) | retained in full model |
| expected lost observables | eliminated-complex occupancy becomes algebraic (still reconstructable); no material observable lost | none |
| QSSA epsilon | closure manifold accuracy (pre-formal partition verification: occupancy <= 1.12e-3 on the reference) | n/a |
| closure conditioning | 21x21 nonlinear root solve, FD Jacobian, feasibility-projected (registered discipline) | n/a |
| branch continuity | multi-start + start-agreement at t0; warm start along trajectory | n/a |
| implementation complexity | new coordinate runner; no debit matrix needed (totals transfer the inventory exactly) | none |

## Decision (before formal runs)

A3b proceeds to the Phase-12 S0 smoke gate (candidate A3b-S0) and, if it
passes, to formal validation. A3c is recorded as rule-refused with no
runnable candidate. The comparison is NOT decided by state count: A3c
eliminates nothing (so it is not a reduction at all), and A3b's
suitability will be decided by the smoke gate's anti-sliding-leak,
closure-feasibility and branch-continuity evidence.
