# R6 CK formal Branch A validation summary

**CK_STATE_VALID_NET_CURRENT_FAIL**. Recommendation: **CK_STATE_REDUCTION_SUPPORTED_BUT_FLUX_NOT_READY**.

Completed 9/9 full numerical workflows; 9/9 have completed state/current assessments; 0/9 passed every mandatory gate. The researcher's Branch A decision makes A, B, C, D, F and H mandatory. E/G remain SOURCE_PROVENANCE_PRESERVED / descriptive / BUT_NOT_VALIDATED. No CK or reduced-core promotion occurred.

| Condition | A/B states | C conservation | D net current | F net extent | H initial layer | Overall |
|---|---|---|---|---|---|---|
| R3_BASE | STATE_VALID | RESOLVED_PASS | RESOLVED_FAIL | RESOLVED_FAIL | NUMERICALLY_UNRESOLVED | CK_STATE_VALID_NET_CURRENT_FAIL |
| R3_GLYRS_LOW | STATE_VALID | RESOLVED_PASS | RESOLVED_FAIL | RESOLVED_FAIL | RESOLVED_FAIL | CK_STATE_VALID_NET_CURRENT_FAIL |
| R3_GLYRS_HIGH | STATE_VALID | RESOLVED_PASS | RESOLVED_FAIL | RESOLVED_FAIL | NUMERICALLY_UNRESOLVED | CK_STATE_VALID_NET_CURRENT_FAIL |
| R3_METRS_LOW | STATE_VALID | RESOLVED_PASS | RESOLVED_FAIL | RESOLVED_FAIL | RESOLVED_FAIL | CK_STATE_VALID_NET_CURRENT_FAIL |
| R3_METRS_HIGH | STATE_VALID | RESOLVED_PASS | RESOLVED_FAIL | RESOLVED_FAIL | NUMERICALLY_UNRESOLVED | CK_STATE_VALID_NET_CURRENT_FAIL |
| R3_GLY_LOW | STATE_VALID | RESOLVED_PASS | RESOLVED_FAIL | RESOLVED_FAIL | RESOLVED_FAIL | CK_STATE_VALID_NET_CURRENT_FAIL |
| R3_MET_LOW | STATE_VALID | RESOLVED_PASS | RESOLVED_FAIL | RESOLVED_FAIL | RESOLVED_FAIL | CK_STATE_VALID_NET_CURRENT_FAIL |
| R3_TRNA_LOW | STATE_VALID | RESOLVED_PASS | RESOLVED_FAIL | RESOLVED_FAIL | NUMERICALLY_UNRESOLVED | CK_STATE_VALID_NET_CURRENT_FAIL |
| R3_ATP_LOW | STATE_VALID | RESOLVED_PASS | RESOLVED_FAIL | RESOLVED_FAIL | RESOLVED_PASS | CK_STATE_VALID_NET_CURRENT_FAIL |

## Measured worst errors

| Observable | Maximum | Condition |
|---|---:|---|
| state | 0.0042833517289 | R3_ATP_LOW |
| slow_total | 5.32756643081e-05 | R3_TRNA_LOW |
| retained_coordinate | 0.000340748579536 | R3_TRNA_LOW |
| protein | 3.01831917926e-07 | R3_METRS_LOW |
| ck_net_current | 0.993319489377 | R3_ATP_LOW |
| net_current | 0.993319489377 | R3_ATP_LOW |
| ck_net_extent | 0.127362020483 | R3_TRNA_LOW |
| net_extent | 0.127362020483 | R3_TRNA_LOW |
| conservation | 2.36807656817e-10 | R3_TRNA_LOW |
| switch_jump_scaled | 4.36129486543e-05 | R3_ATP_LOW |
| ck_net_current_post_0p05 | 0.148178849535 | R3_TRNA_LOW |

## Distinct balance reports

| Accounting | Model | Maximum absolute residual | Measured conditions |
|---|---|---:|---:|
| EXACT_SOURCE_GENERAL_LAW_DRIFT | source | 2.36807656817e-10 | 9 |
| EXACT_SOURCE_GENERAL_LAW_DRIFT | reduced | 7.45963291138e-11 | 9 |
| NET_STOICHIOMETRIC_FULL_STATE_LEDGER | source | 7.43029886507e-07 | 9 |
| NET_STOICHIOMETRIC_FULL_STATE_LEDGER | reduced | 0.00128935614157 | 9 |
| NET_STOICHIOMETRIC_SLOW_COORDINATE_LEDGER | source | 6.91010427545e-07 | 9 |
| NET_STOICHIOMETRIC_SLOW_COORDINATE_LEDGER | reduced | 7.55384462536e-07 | 9 |
| ALGEBRAIC_ACCOUNTING_AFTER_DISCLOSED_SWITCH_JUMP | source | 7.43029886507e-07 | 9 |
| ALGEBRAIC_ACCOUNTING_AFTER_DISCLOSED_SWITCH_JUMP | reduced | 7.79029505793e-07 | 9 |
| GROSS_MICROSCOPIC_DIRECTED_LEDGER | source | 7.43029886507e-07 | 9 |
| GROSS_MICROSCOPIC_DIRECTED_LEDGER | reduced | 8302.9492305 | 9 |

## CK current and extent windows

| Metric | Window | Maximum E_inf | Condition |
|---|---|---:|---|
| CK_NET_CURRENT | FULL_WINDOW | 0.148178849535 | R3_TRNA_LOW |
| CK_NET_CURRENT | POST_INITIAL_LAYER | 0.993319489377 | R3_ATP_LOW |
| CK_NET_CURRENT | POST_0P05_DIAGNOSTIC | 0.148178849535 | R3_TRNA_LOW |
| CK_NET_CURRENT | COMPOSITE_OR_HYBRID | 0.148178849535 | R3_TRNA_LOW |
| CK_NET_EXTENT | FULL_WINDOW | 0.127362020483 | R3_TRNA_LOW |
| CK_NET_EXTENT | POST_INITIAL_LAYER | 0.127362020483 | R3_TRNA_LOW |
| CK_NET_EXTENT | POST_0P05_DIAGNOSTIC | 0.127362020483 | R3_TRNA_LOW |
| CK_NET_EXTENT | COMPOSITE_OR_HYBRID | 0.127362020483 | R3_TRNA_LOW |

Every mandatory non-pass row, including numerical uncertainty, is collected in `failed_or_unresolved_observables.csv` with its source table, condition, window, error, uncertainty and unchanged gate.

## H uncertainty and strict-domain results

H condition counts are {"RESOLVED_PASS": 1, "RESOLVED_FAIL": 4, "NUMERICALLY_UNRESOLVED": 4}. Resolved failure takes precedence at class level while each unresolved row remains visible. The strict CK predicate fails wherever an accepted fast total or reported CK state is negative, including finite-precision-scale values. `physical_domain_diagnostics.csv` records the minimum, coordinate/species and time for each condition; no tolerance was added and no value was clipped.

| Condition | Minimum accepted fast total | Coordinate | Strict CK-domain pass |
|---|---:|---|---|
| R3_BASE | 3.32985909905e-22 | T1 | True |
| R3_GLYRS_LOW | -7.65268241665e-17 | T1 | False |
| R3_GLYRS_HIGH | 2.03341207949e-21 | T1 | True |
| R3_METRS_LOW | -1.22907415322e-17 | T1 | False |
| R3_METRS_HIGH | 1.54762724414e-21 | T1 | True |
| R3_GLY_LOW | -6.65514769319e-17 | T1 | False |
| R3_MET_LOW | -1.6449594288e-17 | T1 | False |
| R3_TRNA_LOW | 3.45203914982e-23 | T1 | True |
| R3_ATP_LOW | 2.01532204247e-23 | T1 | True |

Eight slow-coordinate continuity checks have tiny measured jumps but uncertainty above the frozen 1e-9 allowance (10% of the 1e-8 gate). They remain NUMERICALLY_UNRESOLVED; this is separate from C exact-law drift. ATP-low passes H.

Worst mandatory curve errors include separate FULL_WINDOW and POST_INITIAL_LAYER gates. CK net-current post-0.05 s is a separate descriptive window; it never replaces the boundary-inclusive post-layer gate. Every numerical status uses the registered uncertainty envelope and its 10% budget. Detailed per-observable rows retain scale, floor, uncertainty, lower/upper error and resolved status.

Exact conservation laws numerically resolved on all conditions: True. H startup/continuity/domain gates resolved on all conditions: False. Failure classes: D, F, H. Numerically unresolved conditions: R3_BASE, R3_GLYRS_LOW, R3_GLYRS_HIGH, R3_METRS_LOW, R3_METRS_HIGH, R3_GLY_LOW, R3_MET_LOW, R3_TRNA_LOW.

## Interpretation and accounting boundaries

Full-source trajectories and source uncertainty probes were reused only after the explicit source verifier passed. Every reduced primary/tighter trajectory and each full-source startup solve is fresh. The frozen R5 rule 10*eta*tau0 was used without tuning. The startup and switch jump remain visible; actual startup net/gross integrals were retained. No source projection, fitted effective parameter, initial-condition fit, clipping or time shift was used.

The state and current conclusions are separate. A resolved D failure prevents the registered formal conjunction even when state trajectories are valid. An unresolved class does not erase a resolved failure, and a resolved failure is not evidence that every observable is numerically characterized. If an extent integration reaches its registered computational bound, the original noncompletion result and native dense state evidence are retained; completed A/B/C/D tiers are extracted separately without another state solve. F/H remain unresolved and missing extent errors are N/A, never zero or inferred PASS. Worst metrics identify how many conditions were actually measured.

Exact SOURCE_GENERAL law drift, net stoichiometric accounting, algebraic-state accounting and the gross directed ledger are reported separately in balance_accounting.csv. A disclosed switch reconstruction jump can appear in the full-state net ledger; it is not invented reaction turnover. Gross directed rates/extents and gross-ledger residuals are descriptive and BUT_NOT_VALIDATED, so they do not enter this Branch A promotion conjunction.

Tiny negative values in unused reconstructed species remain visible in each condition record. Physical CK totals/root checks are separate from global mathematical positivity; unresolved absolute chemical units, Mg/protonation and broad physical-domain proof are not resolved by this numerical campaign. Released source product is fMGG Pept0003, not mature GFP.

The original R6 ambiguity stop is preserved under audit_stop_001. This new prospective contract changes no historical R3/R4 gates, R5 descriptive status or R5-C corrections. The independent verifier checks final hashes and recomputes observable scores from the primary/probe arrays; verification is not scientific promotion.

Stop at this bounded closeout. No first-order follow-on, adverse solve, aminoacylation reduction, push, merge or automatic promotion.
