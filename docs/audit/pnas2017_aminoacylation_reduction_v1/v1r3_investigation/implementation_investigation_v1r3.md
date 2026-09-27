# v1r3 implementation investigation — ledger reconstruction attempt (2026-09-26)

Record class: IMPLEMENTATION-REVISION INVESTIGATION, NEGATIVE RESULT.
The execution instruction of 2026-09-26 authorizes at most ONE automatic
implementation revision (v1r3) after the v1r2 formal failure, for an
independently demonstrated defect of the same class as the v1r1 enzyme
leak.  This record documents that the candidate repair was implemented,
tested at the smoke level, and REFUTED; no formal v1r3 runs were
executed (the pre-formal smoke gate stopped them, as registered).

## 1. The defect targeted

The v1r2 formal cycle failed T_G on the tRNA families (6.4e-2 / 9.1e-2)
and the phosphate ledger (2.9e-5) through the QSSA sliding-leak: along
the reduced flow, d/dt(ledger) = d/dt(token content of the eliminated
complexes), so the ledger drifts by exactly the drained complex content
and the drained material never re-enters the product flow (the
formylated-tRNA chain ends 0.105 uM below FULL at S0).

## 2. The candidate repair (implemented in scripts/run_pnas2017_aa_v1_formal.m)

Reconstruct the free carriers of the exact conserved ledgers at every
RHS evaluation and output time — the same realization pattern as the
registered v1r1 enzyme-moiety reconstruction:

    free tRNAfMetCAU: corrected so the tRNAfMetCAU family token sum
                      equals its author t0 total (44 members, weight 1);
    free tRNAGlyGCC:  the tRNAGlyGCC family (58 members);
    free PPi:         the weighted phosphate ledger (123 members,
                      carrier weight 2).

The v1r2 joint initializer is retained unchanged (its B_init debit rows
ARE the t0 value of the reconstruction — the seed's ledger-consistency
correction is measured at 7.3e-12 uM, asserted <= 1e-9 at every run).
The reconstruction acts only along the trajectory, where the
warm-started block solves track the physical branch continuously.

## 3. What was measured (S0 smoke; evidence in this directory)

1. Seed consistency: the projected initial state satisfies all three
   ledger constraints to 7.3e-12 uM (assertion in the runner log).
2. The reconstructed free tRNAGlyGCC does NOT track the author-row
   trajectory: it first rises ABOVE FULL (e.g. +0.21 uM at t = 1.44 s),
   then crashes below FULL (0.46 uM at t = 2.4 s vs FULL ~1.2 uM), and
   the closure loses feasibility at t = 2.501 s: a eliminated complex's
   quasi-steady value is driven through zero (min C at the feasibility
   floor) and the damped Newton finds no feasible improving step — the
   run terminates fail-closed at 5.0e3 uM/s residual (scaled 3.8e-1).
3. Mechanism: the reconstruction's implied carrier derivative differs
   from the author row by -l_q * qdot (the negative of the sliding
   rate).  During the t ~ 1-3 s sequestration era the complexes' token
   content changes on the SAME timescale as the pool dynamics (the
   refund rate is 1-10% of the author row and accumulates to ~0.5 uM on
   a pool of ~1.4 uM), so the reconstruction is not a benign
   bookkeeping correction for this model: it materially changes the
   reduced dynamics.  (For the enzyme moieties, the v1r1 reconstruction
   is benign because the enzyme pools' token content is carried by
   states whose dynamics are otherwise slow; the substrate pools are
   not.)

## 4. Conclusion

The sliding-leak defect of the A3a selective-QSSA realization is NOT
repairable by the ledger-reconstruction implementation change: the
repair refutes itself at the smoke gate (fail-closed closure loss at
t = 2.5 s) and, before that, trades the v1r2 state deviations for
different ones of the same order.  The v1r2 failure classification
(CONSERVATION_FAILURE with the sliding-leak mechanism) therefore stands
as the final characterization of the registered realization: the T_G
drift on the tRNA families and the phosphate ledger is an intrinsic
property of integrating the free substrate pools while slaving the
eliminated complexes algebraically.

## 5. Status and what a genuine repair would require

- v1r3 formal runs: NOT executed (smoke-gate stop; no preregistration
  freeze was consumed — the revision was never registered for formal
  execution).
- The one authorized automatic implementation revision is spent on this
  investigation.
- Any further repair changes the reduction scientifically (e.g.
  re-selecting the eliminated set so no eliminated complex carries
  tRNA/nucleotide tokens, or a tQSSA-style formulation that conserves
  the ledgers by construction) and requires HUMAN REVIEW per the
  execution instruction's stop rules.
- Runner code: the reconstruction path remains in
  scripts/run_pnas2017_aa_v1_formal.m behind the config-gated
  `reconstructed_ledgers` field; it is INERT for every registered
  configuration (v1r1/v1r2 configs do not set it) and its activation is
  asserted to be seed-consistent before integration.
