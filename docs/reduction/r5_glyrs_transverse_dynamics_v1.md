# GlyRS feedback-aware transverse diagnostics

For e=q-h0(z), edot=G(z,h0+e)-Dh0 F(z,h0+e)=-Dh0 F0+(Gq-Dh0 Fq)e+O(||e||²). Dh0=-Gq^-1 Gz and Aperp=Gq-Dh0 Fq, all on the R4 graph. Old predictor is Gq^-1 Dh0 F0; new predictor is Aperp^-1 Dh0 F0. Signs follow setting the linear edot to zero. This predicts transverse lag on frozen full-source paths, not a new reduced model.

All stored R4 valid roots and source trajectories are used; no coupled screens rerun. Full matrices are in condition NPZs; sample spectra/conditioning/numerical abscissa, term ratios and per-coordinate three-window metrics are in the CSVs. Positive numerical abscissa diagnoses potential transient growth, even with stable eigenvalues. tau_perp from spectral abscissa times defect is DEFECT_PROPAGATION_DIAGNOSTIC, not a rigorous bound; nonnormality prevents a semigroup bound from eigenvalues alone. Inverse-operator response is also reported.

Measured summary:

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

Future derivation, only if human review selects it: introduce a defensible singular family and solve the invariance equation G(z,h;eta)=Dh F(z,h;eta) order by order. In standard slow-fast scaling eta qdot=g+eta g1, the first correction satisfies gq h1=Dh0 F0-g1. At eta=1 there is no automatically justified small parameter; replacing Gq by Aperp is a local lag diagnostic, not by itself an asymptotic h1 theorem. No h1 implementation or nine-condition validation was executed.
