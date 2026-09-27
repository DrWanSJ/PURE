# Aminoacylation reduction — final candidate matrix and cycle decision
(2026-09-26)

Record class: FINAL SCIENTIFIC DECISION of the 2026-09-26 execution cycle
(Phase 23). Factual status per candidate; no candidate is selected by
size. Per the stop rules, the aminoacylation reduction STOPS FOR HUMAN
REVIEW at the end of this cycle.

## Candidate matrix

| | A3a (selective QSSA, free-substrate coordinates) | A3b-21 (total-coordinate, 21-state fast set) | A3b-r12 (total-coordinate, 9-state restricted fast set) | A3c (conservative restricted-QSSA) |
|---|---|---|---|---|
| structural validity | registered partition; coordinate transform never formulated in T=[A;Q] form | transform exact: rank(T)=241, cond 4.05e2, B1-B10 11/11 | transform exact: rank(T)=241, cond 3.90e2, B1-B10 11/11 | no admissible fast set exists under its own rule |
| conservation validity | T_G FAIL: tRNA families 6.4e-2/9.2e-2, phosphate 2.9e-5 (sliding leak) | sliding leak ABSENT by construction (ledgers are coordinate rows) | sliding leak ABSENT (validated: post-layer 1e-14, full-window 1e-10..2e-8, coherence <= 1e-9) | trivially exact (no elimination) |
| S0 validity | FAILED_VALIDATION_ON_REFERENCE_DOMAIN (formal) | FAILED_SMOKE_CLOSURE_FEASIBILITY: closure loses feasibility at t = 2.498 s (min q = 5.3e-13, scaled residual 5.6e-1) | BLOCKED_NUMERICAL_COORDINATE_DEFECT: integrates and validates on [1e-4, 10] s (~19 s wall); the full window does not complete (solver step collapse for t >~ 10 s) | REFUSED_BY_SELECTION_RULE (0/21 states eligible) |
| stress-domain result | all 6 conditions fail identically | not reached (smoke stop) | not reached (smoke stop) | not applicable |
| complexity | 218 dynamic + 21 algebraic | 220 dynamic (215 non-constant) + 21 algebraic | 232 dynamic (229 non-constant) + 9 algebraic | none (unreduced) |
| dynamic dimension | 218 | 220 | 232 | 241 |
| major lost observables | eliminated-complex occupancy becomes algebraic | same (still reconstructable at checkpoints) | same (reconstructable, accurate to 3-5 digits) | none |
| failure mechanism | phantom inventory (v1r1); structural sliding leak (v1r2); ledger reconstruction dynamically large (v1r3) | closed-loop 21-state QSSA dynamically invalid in the GlyAMP-sequestration transient (free tRNAGlyGCC 2.19 -> 3e-4 uM over t = 1-3.2 s): a complex's quasi-steady branch is driven through the feasibility floor | the audited binit Met/Gly material and scope adenine total rows cut fast EFTu-/MK-binding equilibria (bound carriers outside the row scopes): fast row dynamics (0.34/0.92/0.039 uM/s) vs 3e-8 error-test tolerances -> ode15s step collapse | every eliminated-complex candidate carries tRNA-family, phosphate/adenylate, or amino-acid material tokens whose algebraic motion is the forbidden sliding identity |

## What this cycle established (positive knowledge)

1. **The Phase-2 coordinate framework is exact and the A3a sliding-leak
   mechanism is removable by construction.** For both A3b variants the
   transformation T = [A; Q] is exactly invertible (rank 241 by two
   independent modular proofs), every protected ledger lies in
   rowspace(A) (each is a coordinate row), and the anti-sliding
   validation shows the v1r2 failure signature (tRNA 6.4e-2/9.2e-2,
   phosphate 2.9e-5) reduced to 1e-10..2e-8 full-window and 1e-14
   post-layer, with sliding-identity coherence <= 1e-9 — the A3a
   identity is provably absent.
2. **The 21-state fast set is refuted under exact ledgers** (A3b-21
   smoke reproduces the refuted v1r3 closure loss at t = 2.498 vs
   2.501 s): the QSSA partition itself, not the bookkeeping, fails in
   the GlyAMP-sequestration transient.
3. **The conservative A3c rule admits no elimination at all** — a
   mechanical, reproducible result (a3c_eligibility.json): every
   complex's algebraic motion would create unresolved protected-ledger
   content.
4. **The restricted 9-state closure is quantitatively excellent** where
   it integrates: the eliminated occupancies track FULL to 3-5
   significant digits through the violent transient, and the
   initialization is exact with no debit matrix.
5. **The remaining obstruction is a defect of the AUDITED ledger rows,
   not of the candidate**: the binit Met/Gly material rows and the
   scope adenine row are t0-accounting scopes that cut fast binding
   equilibria; as dynamic coordinates they carry fast content
   incompatible with the registered tolerances.

## The human review question

To complete the A3b-r12 candidate the coordinate basis needs three
TOKEN-CLOSED ledger rows (methionyl, glycyl, adenosyl — the analogs of
the registered 44/58-member tRNA-family rows: every complex and
degraded carrier included, exact global invariants, no fast content).
Their mechanical derivation is UNDERDETERMINED by the audited moiety
evidence: the left nullspace of the full 241x968 stoichiometric matrix
is 27-dimensional, and the audited binit anchors pin the contents of
the 47 aminoacylation-subsystem species only, leaving the downstream
extension (fMet / EFTu / MTF / ribosomal / peptide carriers) a
coordinate choice. Approving a specific construction (e.g. name-token
propagation with enzyme-token exclusion, or a maximal-support
non-negative integer solution) is a scientific sign-off on the ledger
definition — precisely the class of decision the stop rules reserve
for human review.

## Decision

- A3a: CLOSED (negative, permanent).
- A3c: REFUSED by its own selection rule (negative, permanent).
- A3b-21: CLOSED at the smoke gate (negative, permanent).
- A3b-r12: SCIENTIFICALLY ALIVE but BLOCKED at the smoke gate on the
  token-closed ledger-row derivation. It is the only candidate with
  demonstrated exact ledgers, exact initialization, accurate closure
  and absent sliding leak; with the approved rows its smoke gate is
  expected to pass, after which the formal S0-S5 chain proceeds under
  the frozen candidate-level acceptance semantics.
- **STOP aminoacylation reduction for human review** before inventing
  the token-closed ledger construction (mission stop rule: both A3b and
  A3c failed their pre-formal gates; the remedy is a new ledger
  mechanism). A4a/A4b are NOT pursued: Phase 19/20 are conditional on a
  candidate passing reference-domain validation, which did not occur.
