# A3b/A3c acceptance semantics — new candidate-level preregistration basis
(2026-09-26)

Record class: PREREGISTRATION BASIS for the new scientific candidates
(Phase 9 of the 2026-09-26 execution instruction). The historical
v1r1/v1r2 acceptance files are NOT modified; this document declares the
acceptance semantics under which the NEW candidates are judged. The
quantitative targets are the project's established ones, unchanged.

## 1. Quantitative accuracy targets (frozen, unchanged)

| tier | quantity | budget |
|---|---|---|
| T_G | conservation / accounting residual (scaled) | <= 1e-8 |
| T_C | retained physical-state trajectories (scaled E_inf) | <= 1e-2 |
| T_D | instantaneous process fluxes (scaled) | <= 5e-2 |
| T_E | cumulative resources (scaled) | <= 1e-2 |
| T_Q | algebraic QSSA residual (scaled) | <= 1e-10 |

Numerical uncertainty must remain <= 10% of the scientific error budget;
the frozen numeric_uncertainty_budget rule (a ledger the FULL reference
itself does not hold to T_G is reported NUMERICALLY_UNRESOLVED, not
FAIL) is retained verbatim.

## 2. Initial-layer semantics (candidate-level; new)

The A3a evidence (certificates v1, v1r2) proved that a QSSA microstate
cannot reproduce the full fast transient at t0 when RED starts on the
slow manifold. The NEW preregistration therefore separates three
scoring windows:

**A. FULL-WINDOW PHYSICAL ACCEPTANCE** — for quantities expected to be
meaningful from t0, scored over the complete registered window
[1e-4, 1000] s:

- protected material/resource ledgers (T_G);
- total-coordinate variables (the 8 A3b ledger rows);
- retained slow states;
- experimentally relevant product/resource outputs;
- cumulative accounting (T_E), never reset after the layer.

**B. POST-LAYER MICROSTATE ACCEPTANCE** — for the algebraically
eliminated fast complexes and their internal fast fluxes, scored over
[t_layer, 1000] s.

**C. FULL-WINDOW FAST-MICROSTATE ERROR** — still computed and reported
for the eliminated complexes as a diagnostic (never hidden), but an
unavoidable initial-layer jump is not the primary acceptance criterion
for an eliminated microstate.

This is a NEW candidate's declared semantics. It does NOT retroactively
change the A3a failure, which remains `FAILED_VALIDATION_ON_REFERENCE_DOMAIN`
under the historical scoring.

## 3. Layer window (derived before formal comparison, Phase 9B)

The registered layer end remains the pre-formal relaxation rule
t_layer = t0 + 5 * tau_fast with tau_fast = max(MetRS 0.006105 s,
GlyRS 0.009825 s) = 0.009825 s (registered in
`aminoacylation_v1_comparison_scope.json`, tau_fast_note), i.e.
t_layer = 0.049225 s for the registered grid. This rule is inherited
UNCHANGED from the frozen registration (it was derived from local fast
relaxation evidence before any formal trajectory comparison; no
post-hoc boundary choice is permitted or needed). For a candidate that
passes S0, the per-condition layer end under stress is the same rule
applied to the same tau_fast (the stress conditions scale initial
values, not the fast-rate constants; a tau re-derivation per condition
is not registered).

## 4. Anti-sliding-leak acceptance (Phase 12, structural)

For every protected ledger l (the 9 audited rows), along the smoke and
formal reduced runs:

    d/dt (l . x_reconstructed)   must equal   the exact full-network
                                              ledger balance (l^T S) v
                                              retained by the reduced
                                              coordinate rows,

evaluated numerically on the reconstructed output states. For the five
exact rows (MetRS_total, GlyRS_total, tRNAfMetCAU_total,
tRNAGlyGCC_total, phosphate_ledger_total) this balance is identically
zero on the active network, so the A3a identity

    ledger drift = d/dt (eliminated token content)

must NOT appear. If it appears, A3b has failed its defining purpose and
is STOPPED before formal runs. For the adenine/Met/Gly material rows
the reduced balance must match the FULL model's own interface balance
(the MK binding-scope fluxes / formylation-era fluxes), within the T_G
budget of the FULL reference itself.

## 5. Initial conditions (Phase 10, frozen)

y0 = A x0_full exactly (the totals transfer the FULL physical
inventory); q0 solves the closure at y0 with the registered multi-start,
start-agreement and per-pool capacity discipline; x0_red = R(y0, q0).
Acceptance at t0: every protected ledger exact to <= 1e-8 scaled,
closure residual <= 1e-10 scaled, nonnegative reconstruction
(min >= -1e-10). No debit matrix is used (the totals make it
unnecessary); the v1r1 phantom-inventory initialization is structurally
impossible in these coordinates.

## 6. What would constitute failure

The same frozen classification classes apply (Phase 17 of the
execution instruction): COORDINATE_TRANSFORM_FAILURE,
CONSERVATION_FAILURE, INTERFACE_BALANCE_FAILURE,
ALGEBRAIC_CLOSURE_FAILURE, LOSS_OF_ATTRACTIVITY,
BRANCH_FEASIBILITY_FAILURE, INITIAL_LAYER_ONLY_FAILURE,
POST_LAYER_STATE_FAILURE, FLUX_FAILURE, CUMULATIVE_RESOURCE_FAILURE,
NUMERICAL_RESOLUTION_FAILURE. No threshold may be changed after
results are visible; a formal failure is final evidence.
