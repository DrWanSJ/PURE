# Dataset S28 figure inventory

All figure execution is PAUSED_BY_USER. Main source mappings are recorded separately.

| Sheet | Source classification | Limitation |
| --- | --- | --- |
| Fig. 2B | UNRESOLVED | Species identity mapped; RRF condition contradiction; no run |
| Fig. 3A | UNRESOLVED | Exact QSS transform unavailable |
| Fig. 5A | UNRESOLVED | Exact source subset; no run; RRF condition contradiction |
| Fig. S1B | REQUIRES_DIFFERENT_CONDITION | 241 direct species; A4:A203 200 times; first row CK DP4=1, NDK DT4=0.06, RRF HU4=16; relative to Fig2B CK=30 NDK=1.8 RRF=1600. Author CSV differs only CK and NDK. Paper p2/E1337 describes 30-fold CK/NDK increase for main run. Separate SI caption not frozen. |
| Fig. S4 | UNRESOLVED | B1 Rate of concentration changes; 241 exact species headers B2:IH2; log-slope definition paper p4 incomplete estimator conventions; 7039 NaN text cells and 185 Inf/-Inf cells; states B202:IH202 blank at t1000; do not replace nonfinite values. |
| Fig.S7A | REQUIRES_DIFFERENT_CONDITION | 483 unique A3:A485 k1 names equal precisely the positive author k1 ID set; B2:E2 factors 1,.5,.25,.1; B1 tau seconds threshold MGG>0.02 碌M; G1 product micorM at1000s, G2=.1; F3:F485 formulas Erow/Brow. Sweeps require altered parameters and exact threshold-time convention is absent. |
| Fig. S8 | REQUIRES_UNAVAILABLE_INFORMATION | B1 number of QSS components; B2:DM2 labels data1..data116 have no initial-condition identities; paper p7/E1342 selects116 of216 trials by final peptide<10%difference but source does not bind these116 columns to explicit conditions. QSS transform also unresolved. A3:A202 time200 points; B202:DM202 blank. |

Species-column identity and workbook-internal equality do not establish model reproduction or permission to override the author's inputs.
