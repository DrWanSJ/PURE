# A3b-r12 implementation investigation — restricted fast set and the
# material-coordinate obstruction (2026-09-26)

Record class: CANDIDATE INVESTIGATION, NEGATIVE/BLOCKED RESULT (evidence
record; no formal runs were executed — the pre-formal gates stopped them,
as designed).

## 1. Candidate definition and authorization

A3b-r12 is the Phase-6-authorized evidence-driven revision of the A3b
candidate: after the A3b-21 smoke failure (closure feasibility loss at
t = 2.498 s, reproducing the refuted v1r3 signature), the 12
tRNA-bearing complexes RETURN to the dynamic state vector and only the 9
tRNA-free binding/adenylation complexes stay algebraic
(`../pnas2017_aminoacylation_A3b_r12/`). The tRNA families then have NO
algebraic content, the free tRNAs are integrated, and the violent
GlyAMP-sequestration transient (free tRNAGlyGCC 2.19 → 3e-4 µM over
t ≈ 1–3.2 s — a FULL-model physical transient, verified against
FULL-S0) is ridden by ODE states instead of the algebraic closure.

## 2. What passed

- Pre-QSSA B1–B10: 11/11 PASS (rank(T) = 241, cond 3.90e2, exact
  round-trips, RHS identities, ledger representation);
- consistent initialization: exact inventories (max abs diff 1.5e-11 on
  nine rows), closure at t0 6.3e-13 scaled, no debit matrix needed;
- closure accuracy: at every diagnostic checkpoint in t ∈ [1e-4, 3.2] s
  the 9 algebraic occupancies track FULL to 3–5 significant digits
  (e.g. at t = 2.963: MetRS_AMP 8.72e-7 vs FULL 8.72e-7;
  MetRS_Met_ATP 5.0903e-3 vs 5.0904e-3; worst GlyRS_Gly 8.40e-4 vs
  9.76e-4 during the transient);
- **anti-sliding-leak validation (the A3a identity is ABSENT)**: on the
  integrated window [1e-4, 10] s (`A3br12_antisliding_validation.json`),
  the six exact protected ledgers hold RED-vs-FULL ledger balance to
  1.1e-10 / 6.7e-10 / 7.3e-11 / 8.3e-9 / 2.2e-8 (enzyme x2, tRNA x2,
  phosphate, guanine — the last five all ≤ 1e-8 post-layer, at
  3.6e-14 … 9.3e-14), with sliding-identity coherence ≤ 1e-9 on every
  row: the residual mismatch is NOT the drained eliminated-complex
  content. For comparison, the v1r2 (A3a) formal failure was 6.4e-2 /
  9.2e-2 (tRNA families) and 2.9e-5 (phosphate) — the total-coordinate
  structure removes the sliding leak by five orders of magnitude and
  post-layer holds it at the representation floor.

## 3. Where it stops (numerical obstruction, precisely diagnosed)

The full-window S0 smoke does not complete: ode15s at the registered
RelTol 1e-10 / AbsTol 1e-14 collapses to ~1e5 solver steps per decade
in the t ≳ 10 s plateau (the [1e-4, 10] window integrates in ~19 s;
[10, 30] alone needs > 1e5 steps). The cause is identified by direct
measurement at a t = 30.7 s FULL state: the binit-derived
`Met_material_total` / `Gly_material_total` (and, at lower amplitude,
the scope `adenine_ledger_total`) coordinate rows are NOT slow
coordinates — their 13/13/39-member scopes cut through the fast
EFTu-/MK-binding equilibria (the bound carriers are outside the row
scopes), so the rows carry genuine fast dynamics (measured row
derivatives 0.34 / 0.92 / 0.039 µM/s) against error-test tolerances of
3e-8 / 3e-8 / 3.75e-7. A coordinate with fast content cannot be
integrated as a slow state at the registered tolerances; the solver
step size collapses. The enzyme, tRNA-family and phosphate rows do NOT
have this defect (they are closed over their binding equilibria and
their reduced dynamics is identically zero).

## 4. The remedy and why it stops for human review

The remedy is to replace the material/adenine coordinate rows with
TOKEN-CLOSED rows (the methionyl / glycyl / adenosyl analogs of the
registered 44/58-member tRNA-family rows, which include every complex
and degraded carrier and are therefore exact, fast-content-free global
invariants). Mechanical derivation status:

- the left nullspace of the 241 × 968 stoichiometric matrix is
  27-dimensional (the model's conserved-moiety families);
- the audited binit evidence pins the methionyl / glycyl contents on
  the 47 aminoacylation-subsystem species only; the anchored extension
  to the full network (the downstream fMet / EFTu / MTF / ribosomal /
  peptide species) is UNDERDETERMINED by the audited evidence — the
  nullspace family restricted to the anchored subspace retains free
  dimensions, so selecting one row is a coordinate choice, not a
  mechanical consequence of the audited data;
- greedy token-propagation attempts stall for the same reason (the
  required completion is not locally determined).

Selecting the token-closed rows is therefore a new protected-ledger
derivation — a coordinate choice outside the frozen audited basis —
and per the execution instruction's stop rules ("protected ledgers
cannot be represented consistently in the coordinate transform";
arbitrary coordinate choices) this cycle STOPS for human review with
the technical analysis above. The candidate is otherwise sound: its
closure, initialization and anti-sliding behavior are demonstrated.

## 5. Evidence

- `A3br12_preqssa_verification.log` (B1–B10, this directory's
  verification transcript),
- `A3br12_antisliding_validation.json` (validator output on the
  [1e-4, 10] s window),
- `A3br12_closure_diagnosis.log` (checkpoint-by-checkpoint closure
  state vs FULL),
- `results/pnas2017_reference/2026-09-26_aa_a3bc_smoke/` (smoke run
  logs; the run artifacts are the [1e-4, 10] evidence trajectory and
  the obstructed full-window logs),
- scripts: `run_pnas2017_aa_a3b_formal.m` (candidate runner, both
  A3b variants), `a3b_*.m` (coordinate/closure core),
  `verify_pnas2017_aa_a3bc_preqssa.m`, `diagnose_pnas2017_aa_a3b_closure.m`
  (investigation helper), `validate_pnas2017_aa_a3b_ledgers.py`
  (anti-sliding validator),
  `analyze_pnas2017_aa_a3bc_coordinates.py` (candidate coordinate
  analysis; candidates a3b21 / a3br12).
