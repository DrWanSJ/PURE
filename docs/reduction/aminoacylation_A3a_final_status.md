# Aminoacylation A3a — final status (completed negative candidate)

Record class: STATUS FREEZE. This file closes the A3a candidate as a
completed negative result and records its scoped interpretation. It
supersedes nothing and modifies nothing; the historical evidence listed
below remains byte-for-byte on disk and is the permanent record.

## Scoped interpretation

A3a = the aminoacylation selective-QSSA candidate consisting of

- free-substrate slow coordinates (every non-eliminated species,
  including the free tRNA / amino-acid / nucleotide pools, integrated
  under the author RHS rows);
- 21 algebraically slaved enzyme-complex states (12 MetRS + 9 GlyRS,
  the registered partition), enforced as 0 = dC_i/dt of the author RHS
  at every evaluation;
- exact free-enzyme reconstruction from the conserved enzyme moieties
  (v1r1), with the v1r2 moiety-consistent initialization map (B_init
  debit rows) and the v1r3 ledger-reconstruction investigation.

## Final status

`FAILED_VALIDATION_ON_REFERENCE_DOMAIN`

with two independent, separately evidenced reasons:

1. **Protected-ledger sliding leak (structural).** Along the reduced
   flow the eliminated complexes are algebraic, so for any conserved
   ledger l, d/dt(l·x_red) = d/dt(token content of the eliminated
   complexes): the ledger total drifts by exactly the drained complex
   content. Measured on the v1r2 formal runs: tRNAfMetCAU family
   6.4e-2, tRNAGlyGCC family 9.1e-2, phosphate ledger 2.9e-5 (scaled;
   budget 1e-8). The leak is a property of the state-coordinate
   realization (integrated free substrates + algebraic complexes), not
   of any initialization map.

2. **Unavoidable full-window fast-state initial-layer jump under the
   historical scoring semantics.** The eliminated complexes are
   algebraic from t0, so their full-window T_C error is ~1.0 by
   construction (the QSSA layer jump at the first output point); under
   the frozen scoring no QSSA realization of this partition can exceed
   `APPROXIMATELY_VALIDATED_OUTSIDE_LAYER`.

## Evidence (permanent, do not modify)

- v1r1: `aminoacylation_reduction_certificate_v1.md` (phantom-inventory
  initialization defect; formal failure classification
  `../audit/pnas2017_aminoacylation_reduction_v1/formal_failure_classification_v1r1.md`);
- v1r2: `aminoacylation_reduction_certificate_v1r2.md` (moiety-consistent
  initialization: exact t0 inventories, formal failure classification
  `../audit/pnas2017_aminoacylation_reduction_v1/formal_failure_classification_v1r2.md`
  — the sliding-leak mechanism);
- v1r3: `../audit/pnas2017_aminoacylation_reduction_v1/v1r3_investigation/implementation_investigation_v1r3.md`
  (ledger reconstruction refuted at the smoke gate: fail-closed closure
  loss at t = 2.501 s; the sliding-rate correction is dynamically large).

Formal run artifacts: `results/pnas2017_reference/2026-09-25_aa_v1_formal/`,
`results/pnas2017_reference/2026-09-26_aa_v1r2_formal/` (+ comparison
directories). Validator reports: 24 PASS / 0 FAIL (v1r1), 13 PASS / 0 FAIL
(v1r2) — the evidence pipeline is intact; the scientific outcome is the
recorded failure.

## Disposition

- A3a is CLOSED. Do not rerun it; do not modify its certificates.
- Successor candidates: A3b (total-coordinate / tQSSA) and A3c
  (conservative restricted-QSSA) — see
  `aminoacylation_A3b_A3c_candidate_review.md` (this cycle).
- The new candidates change the SLOW COORDINATES (or the eliminated
  set); they do not patch the A3a implementation.
