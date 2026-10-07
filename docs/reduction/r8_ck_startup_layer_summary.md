# R8 CK startup-layer attribution summary

**CK_STARTUP_LAYER_ATTRIBUTION_NOT_SUPPORTED**

Attribution only; original R7 failures remain. promotion=false; PURE_reduced_core=NOT_VALIDATED.
Exactly BASE, ATP_LOW, TRNA_LOW. No state or extent ODE solve, matching layer, h2 or aminoacylation work.

Signed scaled contributions use the unchanged R7 FULL_WINDOW F scale:

| Condition / pair / model | by switch | by 1 ms | by 0.05 s | after 1 ms | after 0.05 s | terminal | R7 F supremum |
|---|---:|---:|---:|---:|---:|---:|---:|
| R3_BASE / re0000000332_MINUS_re0000000333 / ZERO_ORDER_R6 | 0 | 9.53237518369e-08 | 1.00340952335e-07 | -0.00157844362739 | -0.00157844864459 | -0.00157834830363 | 0.00157834830363 |
| R3_BASE / re0000000332_MINUS_re0000000333 / FORMAL_FIRST_ORDER_SELF_CONSISTENT | 0 | 9.72436914296e-08 | 9.89963710232e-08 | -0.000646911308889 | -0.000646913061568 | -0.000646814065197 | 0.000646814065197 |
| R3_BASE / re0000000336_MINUS_re0000000337 / ZERO_ORDER_R6 | 0 | -1.21721984578e-21 | -3.3957013846e-10 | 0.126294962593 | 0.126294962932 | 0.126294962593 | 0.126294962593 |
| R3_BASE / re0000000336_MINUS_re0000000337 / FORMAL_FIRST_ORDER_SELF_CONSISTENT | 0 | -2.98966336728e-22 | 2.73042215789e-12 | -0.0111896083799 | -0.0111896083827 | -0.0111896083799 | 0.0111896083799 |
| R3_ATP_LOW / re0000000332_MINUS_re0000000333 / ZERO_ORDER_R6 | 0 | 1.59070609544e-07 | 1.60829539279e-07 | -0.00129672704523 | -0.00129672880415 | -0.00129656797462 | 0.00129656797462 |
| R3_ATP_LOW / re0000000332_MINUS_re0000000333 / FORMAL_FIRST_ORDER_SELF_CONSISTENT | 0 | 1.5944774709e-07 | 1.59773820271e-07 | -0.00012050430601 | -0.000120504632083 | -0.000120344858263 | 0.000120344858263 |
| R3_ATP_LOW / re0000000336_MINUS_re0000000337 / ZERO_ORDER_R6 | 0 | 5.60342023339e-22 | -2.50880776195e-10 | 0.106413113513 | 0.106413113764 | 0.106413113513 | 0.106413113513 |
| R3_ATP_LOW / re0000000336_MINUS_re0000000337 / FORMAL_FIRST_ORDER_SELF_CONSISTENT | 0 | -1.01578958616e-22 | 2.64941803618e-12 | -0.00306951850964 | -0.00306951851229 | -0.00306951850964 | 0.00306951850964 |
| R3_TRNA_LOW / re0000000332_MINUS_re0000000333 / ZERO_ORDER_R6 | 0 | 9.47293866126e-08 | 9.99205630233e-08 | -0.00159475323192 | -0.0015947584231 | -0.00159465850254 | 0.00159465850254 |
| R3_TRNA_LOW / re0000000332_MINUS_re0000000333 / FORMAL_FIRST_ORDER_SELF_CONSISTENT | 0 | 9.66373780839e-08 | 9.84025410793e-08 | -0.000647203221674 | -0.000647204986837 | -0.000647106584296 | 0.000647106584296 |
| R3_TRNA_LOW / re0000000336_MINUS_re0000000337 / ZERO_ORDER_R6 | 0 | -5.31666272869e-22 | -1.12181312085e-10 | 0.127362020483 | 0.127362020595 | 0.127362020483 | 0.127362020483 |
| R3_TRNA_LOW / re0000000336_MINUS_re0000000337 / FORMAL_FIRST_ORDER_SELF_CONSISTENT | 0 | -4.20771196773e-22 | 1.09490248808e-12 | -0.0112956365026 | -0.0112956365037 | -0.0112956365026 | 0.0112956365026 |

The cumulative startup difference through switch is exactly zero: the inherited candidates share source startup integrals. This does not assert that the physical initial layer is absent.
A short real switch current tail and sustained cumulative extent error must be distinguished. Signed later increments, opposite-sign cancellation and each pair remain explicit in the CSVs.
Fixed-time interpolation uses frozen cumulative ledgers and currents. No dense post-switch source is available. Primary/probe, original tighter quadrature, cancellation, and Hermite/linear disagreement are reported; the latter is descriptive, not a rigorous interpolation bound.
F scores are original supremum scores, not terminal residuals. Current maxima use the original scoring grid plus the exact lower boundary. No registered metric is replaced.
Permitted next recommendation: **INVESTIGATE_SUSTAINED_OUTER_TRUNCATION_OR_MECHANISM_ERROR_BEFORE_MATCHING**. No implementation follows.
Fast graph distance is descriptive and includes interpolation disagreement; see fast_state_distance.csv. Optional linear-fast-mode check skipped because native dense post-switch source is absent.
Independent verification is recorded separately. Every pre-R8 tracked file and Desktop donor is hash-bound. Derived navigation is subordinate to canonical artifacts.
E/G remain DESCRIPTIVE / BUT_NOT_VALIDATED; all 968 mechanistic decisions remain PENDING.
