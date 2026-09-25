# Aminoacylation reduction certificate — v1r2 (2026-09-26)

## Scoped status

**FAILED_VALIDATION_ON_REFERENCE_DOMAIN**
(the moiety-consistent initialization revision v1r2 of the registered
A3a selective-QSSA candidate; the 21-state partition, the closure
equations, the acceptance thresholds and the stress domain are the
frozen v1r1 ones, unchanged)

## Relation to the failed v1r1 and the exact cause of the v1r1 failure

v1r1 failed because `consistentStart` solved the closure for the 21
eliminated complexes while leaving every free substrate pool at its
author value, so the RED initial state carried the complexes' substrate
content twice (the "phantom inventory"): tRNAfMetCAU +0.234849 uM
(+6.62%), tRNAGlyGCC +0.324962 uM (+9.16%), weighted phosphate
+1.990165 uM, adenine +0.7309 uM, Met +0.3673 uM, Gly +0.3336 uM at t0,
all propagating into trajectories, fluxes and cumulative extents
(`formal_failure_classification_v1r1.md`).  v1r2 changed ONLY the
initialization map: the 21 closure rows are solved jointly with the
B_init inventory rows (a single 21-dimensional damped projected Newton
whose free-pool debits are the frozen, mechanically derived debit
matrix), free AMP stays at its author value 0 (the registered
additional condition), and the RED cumulative counters are seeded with
the P2 fast-layer extents at the registered 5*tau_fast layer-window
exit.  The v1r1 failure signature is gone: the projected initial states
match the author physical inventories to <= 3.6e-16 relative on all
nine B_init rows in all six stress conditions.

## Initialization mathematics

- Inventory basis B_init (9 rows, `binit_v1r2.json` /
  `binit_v1r2_matrix.csv`): MetRS_total, GlyRS_total,
  tRNAfMetCAU_total, tRNAGlyGCC_total, Met_total, Gly_total,
  adenine_moiety_total, declared_phosphate_equivalent_total,
  guanine_check_total.  Per-species moiety contents are solved in exact
  rational arithmetic from the 138-reaction aminoacylation ledger
  deltas with free-species anchors (0 residual DOF after anchoring;
  verified against all 138 subsystem reaction deltas).  Classification:
  the two enzyme and two tRNA rows are exact invariants of the full
  active network (0 violating reactions among the 483 with k1 != 0);
  the Met/Gly/adenine/phosphorus rows are exact on the fast subsystem
  and used as t0 resource accounting only (RESOURCE_ACCOUNTING_ONLY).
- The token inventory rows leave exactly one null direction in the
  (ATP, AMP, PPi) debit split — the adenylation conversion direction
  ATP <-> AMP + PPi.  The registered additional condition delta_AMP = 0
  (free AMP is a kept dynamic state with author value 0; the RED
  trajectory regenerates it through its own flux) resolves the split:
  delta_ATP = -(adenosine content of the eliminated complexes),
  delta_PPi = +(PPi content already released from the bare-adenylate
  complexes MetRS_AMP, MetRS_AMP_MettRNAfMetCAU,
  MetRS_MetAMP_tRNAfMetCAU, GlyRS_AMP_GlytRNAGlyGCC).
- The debit is taken relative to the input state's own bound content,
  which makes the projection idempotent (I5: 4.4e-16).

## P1/P2 agreement

P1 (conservation-constrained algebraic projection) and P2
(fast-boundary-layer dynamic projection: the 47-species closed
aminoacylation subsystem under the 138 registered reactions, integrated
from the author initial state to the registered 5*tau_fast layer-window
exit) land on the SAME attracting branch in all six conditions: every
B_init inventory agrees to <= 3e-10 between the two constructions, no
material branch flip, identical enzyme occupancy.  The remaining
differences are the layer's cycle-progress coordinates (the layer
processes the sequestered enzyme further into post-adenylation forms
and releases PPi/AMP/charged-tRNA that the registered RED formulation
starts at author values); they are confined to the declared layer
window.  The natural layer approaches the manifold to the QSSA defect
level (scaled |G| 5.3e-5 at the window exit); the registered 1e-10
algebraic criterion is an algebraic-solve criterion, not a trajectory
criterion — recorded explicitly.

## Initializer validation (I1-I9: ALL PASS)

I1 manifold residual <= 1.4e-11 scaled at every projected state;
I2 inventories <= 6.1e-16 relative; I3 min projected concentration 0
(never clipped); I4 enzyme reconstruction exact; I5 idempotency 4.4e-16;
I6 byte-level determinism (trajectories and initial-state artifacts);
I7 production multi-start (three deterministic feasible starts, agreement
asserted at 1e-6*ePool, refusal otherwise); I8 +/-1% pool perturbations
flow through with worst Lipschitz ratio 1.45 and zero branch jumps;
I9 structural audit (the initializer reads only the scaled author state,
the parameters, the frozen debit matrix and the author RHS).

## Formal result (S0 and S1-S5)

13 registered cases (FULL-S0..S5 reused byte-for-byte from v1r1 under
byte-identical configs, verified; RED-v1r2-S0..S5 and RED-v1r2-NEG1
fresh, one pass each):

- T_C states: FAIL all 6 conditions (39/56 observables full-window,
  35/56 post-layer at S0)
- T_D fluxes: FAIL all 6
- T_E extents: FAIL 5 of 6 (S4 extents PASS)
- T_G conservation: enzyme 1.7e-16 and guanine 3.9e-14 PASS; tRNA
  families 6.4e-2 / 9.1e-2 FAIL; phosphate 2.9e-5 FAIL; adenine
  NUMERICALLY_UNRESOLVED (unchanged: the FULL reference does not resolve
  it to 1e-8)
- QSSA closure: max scaled |G| <= 1.0e-12 along every trajectory,
  zero root failures, zero plateau accepts
- Negative control RED-v1r2-NEG1: correctly REJECTED (criterion PASS)

## Why it still fails — the structural finding of this cycle

The eliminated complexes are algebraic, so for any conserved ledger l,
d/dt (l x_red) = d/dt (token content of the eliminated complexes): the
RED ledger total equals the author total plus the complexes' CURRENT
content, and drifts by exactly the drained complex content (verified to
7 significant digits on the recorded trajectories).  This "sliding
leak" is the substrate-ledger analog of the enzyme-pool leak already
documented and repaired in v1r1 by moiety reconstruction; it is NOT
fixable by any initialization map.  It simultaneously drains the
sequestered substrate material out of the product flow (formylated
tRNA ends at 0.771 vs FULL 0.876 uM at S0), which shapes the post-layer
state and extent errors.  The full classification:
`formal_failure_classification_v1r2.md` (CONSERVATION_FAILURE +
STATE_TRAJECTORY_FAILURE + FLUX_FAILURE + CUMULATIVE_RESOURCE_FAILURE;
explicitly NOT an initializer, closure, attractivity or numerical
failure).

## Validity domain

Not characterized: the candidate failed the reference condition S0, so
per the execution instruction no S1-S5 validity-domain map was pursued
beyond the registered stress results (all 6 conditions fail
identically in kind).

## Numerical uncertainty

Solver statistics unchanged from the healthy v1r1 machinery (ode15s
RelTol 1e-10 / AbsTol 1e-14; S0: 4343 successful / 73 failed steps,
10627 RHS evaluations).  The closure residual along every trajectory
(<= 1e-12 scaled) is three orders below the registered 1e-10
acceptance; no tolerance-driven NUMERICALLY_UNRESOLVED verdict beyond
the pre-registered adenine ledger.

## Unrecoverable observables

None dropped.  All 56 registered observables were compared; none was
excluded to obtain a pass.

## Experimental-validation status

Not applicable (no experimental data in this cycle).

## Repair path: attempted and refuted (post-cycle v1r3 investigation)

The one authorized automatic implementation revision (v1r3) was spent on
the natural repair: reconstructing the free carriers of the exact
ledgers (free tRNAfMetCAU/tRNAGlyGCC from the tRNA family totals, free
PPi from the phosphate ledger) at every evaluation — the same
realization pattern as the registered v1r1 enzyme reconstruction.  The
repair REFUTES ITSELF at the smoke level: the reconstruction's implied
carrier derivative differs from the author row by the sliding-rate
term, which is NOT small in the t ~ 1-3 s sequestration era; the
reconstructed free tRNAGlyGCC first rises +0.21 uM above FULL, then
crashes below it, and the closure loses feasibility at t = 2.501 s (a
complex's quasi-steady value is driven through the feasibility floor;
the run terminates fail-closed).  Full record:
`v1r3_investigation/implementation_investigation_v1r3.md`.  No formal
v1r3 runs were executed; the v1r2 formal evidence is unaffected (the
extended runner reproduces the committed v1r2 trajectories
byte-for-byte).

Independently of any repair, the eliminated complexes' full-window T_C
error is ~1.0 by construction (the QSSA layer jump at the first output
point), so under the frozen scoring no QSSA realization of this
partition can exceed APPROXIMATELY_VALIDATED_OUTSIDE_LAYER.  Any repair
that would change the T_G outcome must change the reduction
scientifically (re-selecting the eliminated set so no eliminated
complex carries tRNA/nucleotide tokens, or a tQSSA-style
ledger-conserving formulation) and requires HUMAN REVIEW.

## Evidence

`preregistration_revision_v1r2.json`, `run_registry_v1r2.json`,
`implementation_revision_v1r2.json`, `binit_v1r2.json`,
`smoke_gate_v1r2.json`, `initializer_tests_v1r2.json`,
`validator_v1r2_report.json` (13 PASS / 0 FAIL),
`formal_failure_classification_v1r2.md`,
`results/pnas2017_reference/2026-09-26_aa_v1r2_formal/`,
`results/pnas2017_reference/2026-09-26_aa_v1r2_formal_comparison/`.
