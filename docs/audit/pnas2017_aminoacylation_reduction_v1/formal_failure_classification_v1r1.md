# Formal failure classification — v1r1 aminoacylation selective-QSSA formal cycle (2026-09-25)

Record class: FORMAL VALIDATION OUTCOME AND FAILURE CLASSIFICATION
(required by Phase 4 / Phase 8 of the execution instruction:
 "If implementation itself is clearly broken: STOP and classify as
 implementation failure before changing anything.")

## 1. Outcome summary

All 13 registered formal runs executed exactly once, in registry order, and
recorded (13/13 outcome=success; manifests under
`results/pnas2017_reference/2026-09-25_aa_v1_formal/manifests/`).  The formal
full-vs-reduced comparison under the frozen acceptance criteria FAILED on the
reference domain S0 — and identically on every stress condition S1-S5:

- T_C state trajectories: FAIL (all 6 conditions)
- T_D instantaneous fluxes: FAIL (all 6 conditions; worst errors inside the
  declared initial-layer window, plus layer-era deviations below)
- T_E cumulative resource extents: FAIL (5 of 6; worst S3 5.03e-2 vs 1e-2)
- T_G conservation: FAIL for tRNAfMetCAU family, tRNAGlyGCC family and the
  phosphate ledger in all 6 conditions; adenine ledger
  NUMERICALLY_UNRESOLVED (the FULL reference itself does not resolve that
  ledger to 1e-8 at the registered tolerances — frozen
  numeric_uncertainty_budget rule; scope
  `aminoacylation_v1_comparison_scope.json` records the rate-law-level proof
  that the source model's adenosine invariant is exact, so this is reference
  integration noise, not a model leak)

Scoped status: **FAILED_VALIDATION_ON_REFERENCE_DOMAIN**.

## 2. What passed (machinery validated)

- Algebraic closure: every RED run solved the registered 21-row closure at
  every RHS evaluation and output time; max scaled |G| <= 1.0e-12 in every
  run (registered acceptance 1e-10); zero root failures, zero line-search
  rejections, zero plateau accepts.
- Enzyme-moiety reconstruction (the v1 -> v1r1 revision): MetRS/GlyRS family
  totals agree with FULL to <= 4.4e-16 at t0 and <= 2.9e-12 relative over
  the whole window in every condition (frozen T_G met exactly for the enzyme
  moieties).  The 220-state formulation's 0.99 pool-leak is gone.
- Enzyme pool inventories at t0 agree with FULL to <= 4.4e-16 (initial-layer
  rule "enzyme total inventories must agree at t0 exactly").
- Negative software control RED-NEG1: the comparison rejected the illegal
  partition (states verdict FAIL); criterion PASS.  The validation machinery
  detects exactly this class of deviation.
- Evidence pipeline: 13/13 manifests, hash chain intact (validator
  R8/R9/R16/R17/R18 PASS pre-formal; R13/R19/R20/R21 resolved post-formal).

## 3. Root cause (quantified): the consistent initial condition duplicates
##    substrate moieties sequestered into the eliminated complexes

`consistentStart` in `scripts/run_pnas2017_aa_v1_formal.m` solves the closure
rows 0 = dC_i/dt at t0 with every NON-eliminated state frozen at its author
initial value.  It reconstructs the FREE ENZYME from the enzyme moiety
(correct), but it does NOT debit the free substrate pools
(tRNAfMetCAU, tRNAGlyGCC, Met, Gly, ATP, ...) for the substrate content now
sequestered inside the eliminated complexes.  The reduced model therefore
starts from the author inventory PLUS the complexes' contents — a physical
inventory LARGER than the author's.

Measured on the formal trajectories (RED-S0 vs FULL-S0, first output row):

| ledger (token sum)            | FULL t0      | RED t0       | excess   | rel. |
|-------------------------------|--------------|--------------|----------|------|
| tRNAfMetCAU_family_total      | 3.54767184   | 3.78252037   | +0.23485 | +6.62% |
| tRNAGlyGCC_family_total       | 3.54767184   | 3.87263394   | +0.32496 | +9.16% |
| phosphate_ledger_total (wtd)  | 68750.32000  | 68752.31017  | +1.99017 | +2.9e-5 |
| MetRS/GlyRS moiety            | 0.44 / 0.35  | 0.44 / 0.35  | 0 (exact)| 0 |

The excess is not a conserved moiety of the reduced dynamics: it washes out
through the model's degradation sinks over t ~ 1-20 s (RED-S0 tRNA token sum
3.7825 -> 3.5479 by t = 18.9 s), poisoning the transient era:

- worst post-layer state errors at t ~ 2.5-2.7 s: GlyRS-family complexes
  and charged tRNA deviate by 20-34% of scale (S0), up to 79% (S3
  enzyme_high), because the RED model charges from an inflated free-tRNA
  pool while FULL has already debited it;
- cumulative extents integrated from the physical initial condition carry a
  permanent phantom-charging signature: xi_Gly_release +1.29e-2, 
  xi_aa_ATP_consumption_total +1.67e-2 (S0) — above the frozen T_E budget
  1e-2; S3 reaches 5.03e-2.

This violates, with the implemented initialization:

- acceptance_criteria.json `initial_conditions_rule` ("both models start
  from identical physical inventories");
- frozen tier T_G as applied to "tRNA families" and the "phosphate moiety
  ledger" in every formal run (RED residuals 6.6e-2 / 9.2e-2 / 2.9e-5 vs
  threshold 1e-8);
- the user authorization's step (2) "enforce registered enzyme/moiety
  constraints" read with its natural scope (moiety constraints, not only
  the enzyme moiety).

## 4. Classification

IMPLEMENTATION / INITIALIZATION DEFECT of the reduced consistent-start
construction — not a failure of the registered QSSA partition hypothesis:

- the closure equations, the eliminated set and the attracting branch are
  the registered ones; on the RED trajectory they solve to <= 1e-12 scaled
  everywhere;
- the pre-formal partition verification (branch-vs-reference occupancy
  <= 1.12e-3 post-layer, spectrum, relaxation) was computed on reference
  states and is untouched by this defect;
- the defect is localized to the initial-state construction: the manifold
  point consistent with the AUTHOR's physical inventory must fix the
  conserved-moiety totals (enzyme AND substrate ledgers) and solve the
  closure for the eliminated complexes; the implemented start fixes the
  free-substrate coordinates instead, which does not reproduce the author
  moiety totals.

Per Phase 4 of the execution instruction the formal cycle is STOPPED here
and classified, with all 13 formal runs, manifests, comparison metrics and
this record preserved as evidence.  No repair, no re-run, no threshold
change, no initialization re-fit was applied after the results were seen.

## 5. What a repair would require (NOT executed; needs a new human-approved
##    revision)

A moiety-consistent initialization: extend `consistentStart` to solve the
closure jointly with the conserved-moiety constraints (fix total tRNA
families, amino-acid inventories, adenine/guanine/phosphate ledgers at the
scaled author values; free substrates become unknowns debited by the
complex contents).  This changes the reduced initial-state protocol — a new
IMPLEMENTATION / INITIALIZATION revision (v1r2) requiring: revision record,
re-freeze, pre-formal validator gate, a fresh smoke, and a FULLY FRESH set
of 13 formal runs (the present runs remain the recorded evidence for v1r1
and must not be reused).

## 6. Evidence pointers

- runs + manifests: `results/pnas2017_reference/2026-09-25_aa_v1_formal/`
- comparison: `results/pnas2017_reference/2026-09-25_aa_v1_formal_comparison/
  formal_comparison_summary.json` (+ metrics-S*.json, metrics-NEG1.json)
- scope + ledger verification: 
  `models/pnas2017_full_reference/audit/aminoacylation_v1_comparison_scope.json`
- active registration chain: `candidate_partition_v1r1.json`,
  `preregistration_revision_v1r1.json` (both pre-formal, hash-bound)
