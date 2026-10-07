# R5 mechanism-first summary — 2026-10-07

Parent main: `0b6f9ad649a7e283e440e0294a021123551f6858`. Execution parent: local R4 `9def91d` (registration `88c0bfa`), which was not on origin/main. Isolated branch `codex/r5-mechanism-first-20261007`. No merge, push, fitting, reaction deletion, threshold change or next-stage execution.

Canonical four CK binding reactions agree with author parameters 2/1000/2/1000, K0=K1=500 in the inferred reference concentration convention. Sf rank2; full left-null basis rank239, restriction to R1 class rank212. T0,T1,B are fast invariants and dynamic totals, not global constants. Hprime>0 yields unique p∈[0,B]; qi=Ti p/(500+p). Equal-rate Jacobian eigenvalues are −(2p+1000) and −(2p+1000+2(CK+CK_ADP)). Fast layer attracts on physical frozen domain. Across1809 frozen source samples, max equilibrium relaxation is 1.18571108987e-05 seconds; no sampled loss of normal hyperbolicity.

CK scan/initial layer:

```json
{
  "status": "CK_SINGULAR_LIMIT_CONSISTENT",
  "completed": true,
  "systematically_decreasing_hybrid": true,
  "claim": "descriptive baseline convergence, no formal order or promotion",
  "worst_initial_layer_jump": 29.7027954890137,
  "tau0_s": 9.906817032876725e-06,
  "eta1_descriptive_test_executed": true,
  "full_eta1_uncertainty_scaled": 1.4960482847101157e-09,
  "outer_uncertainty_scaled": 2.920177635790322e-09,
  "eta1_outer_post_startup_worst_scaled": 0.9002658494638833,
  "eta1_hybrid_post_startup_worst_scaled": 0.0004492951313555845,
  "original_eta1_all241_post_startup_max_scaled": {
    "outer": 0.9002658494638835,
    "hybrid": 0.0003383575954227056
  },
  "original_eta1_all241_post_0p05_max_scaled": {
    "outer": 0.0003383575954769899,
    "hybrid": 0.0003383575954227056
  },
  "source_general_conservation_drift_max": 1.1749764919702366e-10,
  "reduced_source_general_conservation_drift_max": 1.0266435812397807e-11,
  "net_conversion_extent_max_absolute_difference": 0.0014388781200977974,
  "strict_physical_domain_not_proven": "Some reconstructed unused/zero-inventory species have retained tiny negative roundoff; hybrid eta0.3 minimum -2.18e-11. No clipping or physical-domain promotion."
}
```

Initial layer and startup rule are explicit in ck/initial_layer_definition.json and initial_layer_comparison.csv. Earlier arithmetic/coordinate attempts, their failures, checkpoints and computational stops remain retained. They are UNSCORED. The final chart prioritizes R1 retained coordinates and uses centered totals plus accurate row sums; parameters, tolerances, eta sequence and switch rule remain fixed. See r5_ck_runtime_qualification_v1.md. No source trajectory is clipped or projected.

GlyRS:

```json
{
  "classification": "ZERO_ORDER_GRAPH_ERROR_NOT_EXPLAINED_BY_LOCAL_TRANSVERSE_FORCING",
  "valid_samples": 1809,
  "unstable_valid_samples": 0,
  "improved_conditions": 7,
  "total_conditions": 9,
  "feedback_raw_norm_ratio_max": 0.06340510854453421,
  "feedback_scaled_norm_ratio_max": 0.055245859843672245,
  "new_over_old_error_range": [
    0.01689005874032407,
    1.4113157572736124
  ],
  "worst_old_scaled_l2": 0.793750336934905,
  "worst_new_scaled_l2": 0.13021456370423862,
  "human_review": "HUMAN_REVIEW_REQUIRED",
  "higher_order_model_built": false
}
```

Aperp=Gq−Dh Fq is feedback-aware; measured ratios and nonnormality diagnostics are retained. Predictors are diagnostics, not an h1 model or rigorous error bound.

Balance:

```json
{
  "classification": "MIXED / UNRESOLVED",
  "source_general_laws": 27,
  "max_exact_law_drift": 2.3680765681710625e-10,
  "max_primary_source_ledger_residual": 7.430298865074292e-07,
  "max_reduced_slow_ledger_residual": 5.486685040523298e-06,
  "max_postprocessing_summation_change": 1.8480932340025902e-09,
  "max_same_trajectory_tight_extent_change": 7.521652150899172e-06,
  "max_reconstructed_full_residual": 4.349483736232863,
  "max_algebraic_tracking_ledger_difference": 2.269915147661213,
  "max_affine_decomposition_identity_error": 3.3866243143165775e-12,
  "source_conservation_failure_observed": false,
  "trajectory_mutation": false,
  "historical_gate_changed": false,
  "longdouble_mantissa_bits": 52,
  "direct_state_vs_dense_vs_extent_error_separately_identified": false,
  "reason": "Stored step records contain times/counters, not all accepted states/dense polynomials. Tight-ledger variation identifies a numerical component; complete state/dense/extent error attribution is unavailable. Full reduced ledgers require algebraic redistribution policy."
}
```

27 exact law drifts are separate from directed ledger and reconstructed algebraic-state residuals. High-accuracy summation changes diagnostics only. Full state/dense/extent attribution is unresolved; no historical R4 gate or classification is altered.

| Human question | Evidence-based answer |
|---|---|
|Is CK partial-equilibrium singular limit mathematically coherent?|Yes for the declared binding subsystem and physical frozen-total domain; full-PURE uniform theorem hypotheses remain open.|
|Does error decrease as eta tends to zero?|CK_SINGULAR_LIMIT_CONSISTENT|
|Is eta=1 accurate enough to justify formal broader validation?|No promotion decision. Baseline state and slow-total accuracy is descriptive; numerical budgets, flux reconstruction and broader conditions require human review.|
|Does feedback-aware GlyRS predictor substantially improve R4 lag explanation?|7/9 improve; baseline approximately halves error, high GlyRS strongly improves, low GlyRS and low tRNA worsen. Local feedback does not explain every condition.|
|Is R4 balance uncertainty mostly ledger numerics or a real reduced accounting problem?|Tight-ledger sensitivity exceeds summation-only changes, with no exact-law failure observed. Full reconstructed ledgers require algebraic redistribution. State/dense/extent attribution remains mixed/unresolved.|

Exactly one next human recommendation: **FIX_BALANCE_ACCOUNTING_BEFORE_ANY_NEW_REDUCTION**. This is evidence for review only; stop before next stage. CK remains NOT_YET_PROMOTED and PURE_reduced_core remains NOT_VALIDATED.

Independent verification: see results/reduction/r5_mechanism_first/verification.json for the measured result. Its PASS, if obtained, establishes engineering/provenance checks only. All2420 pre-R5 files are individually byte-hash checked; new outputs are SHA-256 bound by manifest.json and verifier outputs by verification_binding.json. The evidence_navigation.json graph is derived navigation only. Complete requested documentation, CSVs, retained solver arrays and scripts are in the registered tree; original absolute unit metadata and full-PURE uniform bounds remain unresolved.
