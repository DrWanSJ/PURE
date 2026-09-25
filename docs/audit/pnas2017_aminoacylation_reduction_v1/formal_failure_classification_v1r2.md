# Formal failure classification — v1r2 moiety-consistent-initialization formal cycle (2026-09-26)

Record class: FORMAL VALIDATION OUTCOME AND FAILURE CLASSIFICATION
(required by Phase 12 of the execution instruction: "If v1r2 fails,
classify the failure BEFORE changing anything.")

## 1. Outcome summary

The v1r2 formal cycle (13 registered cases; FULL-S0..S5 reused
byte-for-byte from the v1r1 formal cycle under byte-identical configs;
RED-v1r2-S0..S5 and RED-v1r2-NEG1 executed fresh, one pass each,
manifests under `results/pnas2017_reference/2026-09-26_aa_v1r2_formal/`)
completed with the frozen acceptance criteria UNCHANGED:

- T_C state trajectories: FAIL (all 6 conditions; 39/56 observables
  full-window, 35/56 post-layer at S0)
- T_D instantaneous fluxes: FAIL (all 6)
- T_E cumulative extents: FAIL (all 6; at S0 eight extent curves exceed
  the 1e-2 budget; S4 extents PASS)
- T_G conservation: FAIL for the tRNAfMetCAU family (6.4e-2), the
  tRNAGlyGCC family (9.1e-2) and the phosphate ledger (2.9e-5) in all 6
  conditions; adenine NUMERICALLY_UNRESOLVED (unchanged: the FULL
  reference does not resolve that ledger to 1e-8); enzyme and guanine
  ledgers PASS at 1e-16/4e-14
- Negative software control RED-v1r2-NEG1: the comparison REJECTED the
  illegal partition (criterion PASS) — the validation machinery still
  detects exactly this class of deviation.

Scoped status: **FAILED_VALIDATION_ON_REFERENCE_DOMAIN**.

## 2. What v1r2 DID fix (the registered hypothesis of the revision)

The v1r2 hypothesis — "the v1r1 formal failure is caused by a
non-physical initialization map" — is CONFIRMED and the defect is FIXED:

- the projected initial states satisfy every B_init inventory row to
  <= 3.6e-16 relative (initializer suite I2, all 6 conditions), where
  v1r1 carried the phantom excesses tRNAfMetCAU +0.234849 uM,
  tRNAGlyGCC +0.324962 uM, weighted phosphate +1.990165 uM, adenine
  +0.7309 uM, Met +0.3673 uM, Gly +0.3336 uM (all recomputed
  mechanically from the recorded artifacts, `smoke_gate_v1r2.json`
  phase_9_regression);
- the closure solves jointly with the inventory rows: max scaled |G| at
  the projected states 2.7e-16..1.4e-11, along every trajectory
  <= 1.0e-12 (registered acceptance 1e-10), zero root failures, zero
  plateau accepts, no clipping (min reconstructed C = 0);
- P1/P2 cross-validation: same attracting branch on all 6 conditions
  (inventories agree to <= 3e-10; no material branch flip);
- initializer suite I1-I9: ALL PASS (idempotency 4.4e-16, byte-level
  determinism, multi-start agreement, Lipschitz ratio 1.45 under +/-1%
  pool perturbations with zero branch jumps);
- the enzyme/guanine T_G ledgers pass at 1e-16/4e-14 exactly as in v1r1.

## 3. Why the formal acceptance still fails — two distinct mechanisms

### 3a. The intrinsic QSSA sliding-leak (structural; NOT an initialization defect)

Along the reduced flow the eliminated complexes are algebraic
(0 = dC_i/dt enforced to 1e-12), so for any linear ledger l with
l*f = 0 on the full vector field,

    d/dt (l x_red) = l_s f_s + l_q qdot = -l_q f_q(x_red) + l_q qdot
                   = l_q (qdot - 0) = d/dt (token content of the
                                        eliminated complexes),

i.e. the RED ledger total equals the author total plus the complexes'
CURRENT token content, and the ledger drifts by exactly the drained
complex content.  Verified numerically on the recorded trajectories:
the tRNA family total of the v1r2 smoke equals author - q0 + q_content(t)
to 7 significant digits at every output time.  This is the SAME defect
class already documented for the enzyme pools in v1r1 ("integrating the
free enzyme instead was measured to leak ~99% of each pool ... because
QSSA pins the eliminated rows to zero so enzyme held in those complexes
never returns to the free pool as substrates drain") and fixed there by
exact moiety reconstruction.  It is NOT fixable by any initialization
map: it is a property of the state-coordinate realization (integrated
free substrates + algebraic complexes).

Consequences measured (all 6 conditions): T_G tRNA families
6.4e-2 / 9.1e-2 and phosphate 2.9e-5 — essentially unchanged from v1r1
(6.6e-2 / 9.2e-2 / 2.9e-5), because v1r1's t0 phantom and v1r2's
t0-consistent complex content are nearly the same magnitude; the drift
direction differs (v1r1: phantom decays; v1r2: complex content drains),
the amplitude is the same.

The same channel drains the sequestered substrate material out of the
product flow: the drained tokens never re-enter the free pools, so the
formylated-tRNA chain ends at 0.771 uM vs FULL's 0.876 uM (S0, t=1000),
and the free tRNAGlyGCC sits 0.124 uM below FULL at t = 1.66 s while
v1r1's phantom sat 0.315 uM above.

### 3b. The QSSA layer jump (declared failure domain; intrinsic to QSSA)

The eliminated complexes are algebraic in RED: at the first output point
(t = 1e-4 s, inside the registered layer window [t0, t0+5*tau_fast]) RED
holds them at the quasi-steady values while FULL is still at ~0, so
their full-window E_inf is ~1.0 in BOTH v1r1 and v1r2 (e.g.
GlyRS_Gly_ATP_tRNAGlyGCC 1.029 -> 1.021).  This is the registered
initial-layer signature ("the dfinit consistent-initialization
adjustment ... is NEVER suppressed"), scored in the declared layer
window; per the frozen initial_layer_rules a reduction that fails only
there is at most APPROXIMATELY_VALIDATED_OUTSIDE_LAYER.

### 3c. Post-layer state errors

Post-layer (window [5*tau_fast, 1000 s]) the worst relative state errors
at S0 are dominated by the GlyRS/MetRS complex families during the
GlyAMP-accumulation era (v1r2: 0.39-0.58 relative; v1r1: 0.26-0.34).
The mechanism is the free-tRNA deficit of 3a (the tRNA-bearing complex
occupancies track the free-tRNA pool), compounded by the P2-offset
credits on the small PPi/AMP pools early in the window.  v1r1's phantom
free pools accidentally compensated part of this by keeping the substrate
pools inflated; v1r2 removes that non-physical compensation.

## 4. Classification

    CONSERVATION_FAILURE          (T_G tRNA families + phosphate ledger;
                                   mechanism 3a, structural)
    STATE_TRAJECTORY_FAILURE      (T_C; mechanisms 3a + 3b + 3c)
    FLUX_FAILURE                  (T_D; driven by 3a/3c)
    CUMULATIVE_RESOURCE_FAILURE   (T_E; 8 curves at S0)

Explicitly NOT:

    INITIALIZER_FAILURE           - the initializer passed I1-I9 and
                                    achieves exact t0 inventories;
    ALGEBRAIC_CLOSURE_FAILURE     - closure <= 1e-12 scaled everywhere,
                                    zero root failures;
    LOSS_OF_ATTRACTIVITY          - P1/P2 branch agreement on all 6
                                    conditions;
    NUMERICAL_RESOLUTION_FAILURE  - solver statistics unchanged from the
                                    healthy v1r1 machinery.

## 5. Repair path (NOT executed in this cycle; requires a new revision)

The 3a channel has the same repair the project already registered for
the enzyme moieties (v1r1): reconstruct the free carrier of each EXACT
conserved ledger from the ledger itself instead of integrating it —

    tRNAfMetCAU_free = T_tRNAfMet - sum(family \ {free carrier})
    tRNAGlyGCC_free  = T_tRNAGly  - sum(family \ {free carrier})
    PPi_free         = (T_phosphate - sum_{j != PPi} w_j x_j) / 2

(the tRNA families and the phosphate ledger are exact invariants of the
active network: 0 violating reactions among the 483 with k1 != 0, and
FULL holds them to 5.6e-14 / 8.5e-14).  The reconstruction makes the
T_G ledgers exact by construction AND returns the drained tokens to the
free pools (removing the product-chain deficit of 3a).  This changes the
state-coordinate realization (which rows are integrated vs slaved), NOT
the 21-state eliminated set, NOT the closure equations (the eliminated
rows remain author-RHS rows), NOT the thresholds and NOT the stress
domain — the same revision class as the v1r1 enzyme reconstruction.

Per Phase 12 of the execution instruction at most ONE further automatic
implementation revision (v1r3) is authorized for this defect class;
the decision to spend it, the reconstruction scope, and the T_C
all-window layer-jump semantics (mechanism 3b caps any QSSA realization
at APPROXIMATELY_VALIDATED_OUTSIDE_LAYER under the frozen scoring) are
flagged for the final report's HUMAN REVIEW section.

## 6. Evidence pointers

- runs + manifests: `results/pnas2017_reference/2026-09-26_aa_v1r2_formal/`
- comparison: `results/pnas2017_reference/2026-09-26_aa_v1r2_formal_comparison/
  formal_comparison_summary.json` (+ metrics-S*.json, metrics-NEG1.json)
- smoke gate + v1r1 regression: `smoke_gate_v1r2.json`
- initializer suite: `initializer_tests_v1r2.json`
- B_init + debit matrix: `binit_v1r2.json`, `binit_v1r2_matrix.csv`
- P1/P2 cross-validation: `scratch/v1r2/p1p2_comparison_S*.json`
- active registration chain: `preregistration_revision_v1r2.json`,
  `run_registry_v1r2.json` (both pre-formal, hash-bound)
