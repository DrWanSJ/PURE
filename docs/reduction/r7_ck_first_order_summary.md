# R7 CK first-order feasibility summary

**CK_FIRST_ORDER_IMPROVES_EXTENT_NOT_CURRENT**. Exactly three diagnostic conditions; no promotion or broader run.

## Actual lineage

R6 execution parent: `1181ab2f0a04d72cf76fb069be6bb842e3de75d8`. R6 final execution state: uncommitted, final commit SHA N/A. Local byte-preservation commit: `9282853a24d716e3021ea85123e9ba1e0bb4c6fc`. origin/main at inspection: `0b6f9ad649a7e283e440e0294a021123551f6858`.

All 3079 pre-R7 files are snapshot-bound and read-only. This work is additive on branch codex/r7-ck-first-order-20261008. The R6 preservation commit records its existing evidence; it is not a new R6 execution.

## Derived correction

h1 was derived from the exact R5 eta-scaled canonical family. F and G0 are eta-independent in the frozen chart. j0 reproduces the existing finite R6 redistribution current. j1 follows the next invariance coefficient without constructing h2. The formal slow RHS is the Taylor truncation F0+Fq*h1, not nonlinear substitution.

Maximum ||h1||/fast-state scale: 0.000504163704767; maximum ||h1||/fast-total scale: 2.99501374403e-07. These eta=1 size diagnostics are descriptive.
Gq condition range: 1.00000731389 to 1.00001013798; minimum singular value: 84337.5120616 s^-1.
Independent analytic-versus-complex-step Dh1 maximum relative error: 5.55811956363e-11. Richardson finite-difference maximum relative discrepancy: 5.51749086728e-05; complex-step is the independent verifier because finite differences can lose significance on near-zero slopes.

## CK net-current and cumulative net-extent scaled errors

| Condition | Class/window | R6 zero order | Postprocessing on z0 | Formal first order | Formal CK status |
|---|---|---:|---:|---:|---|
| R3_BASE | D FULL_WINDOW | 0.1471239714 | 0.002060901281 | 0.01565716764 | RESOLVED_PASS |
| R3_BASE | D POST_INITIAL_LAYER | 0.9845466279 | 0.9852392198 | 0.9852392198 | RESOLVED_FAIL |
| R3_BASE | F FULL_WINDOW | 0.1262949626 | 0.06338771068 | 0.01118960838 | RESOLVED_FAIL |
| R3_BASE | F POST_INITIAL_LAYER | 0.1262949626 | 0.06338771068 | 0.01118960838 | RESOLVED_FAIL |
| R3_ATP_LOW | D FULL_WINDOW | 0.1134923714 | 0.001530017091 | 0.004640211547 | RESOLVED_PASS |
| R3_ATP_LOW | D POST_INITIAL_LAYER | 0.9933194894 | 0.9938468907 | 0.9938468907 | RESOLVED_FAIL |
| R3_ATP_LOW | F FULL_WINDOW | 0.1064131135 | 0.01388456121 | 0.00306951851 | RESOLVED_PASS |
| R3_ATP_LOW | F POST_INITIAL_LAYER | 0.1064131135 | 0.01388456121 | 0.00306951851 | RESOLVED_PASS |
| R3_TRNA_LOW | D FULL_WINDOW | 0.1481788495 | 0.002080766614 | 0.01580882979 | RESOLVED_PASS |
| R3_TRNA_LOW | D POST_INITIAL_LAYER | 0.9845466268 | 0.9852392191 | 0.9852392191 | RESOLVED_FAIL |
| R3_TRNA_LOW | F FULL_WINDOW | 0.1273620205 | 0.06348141308 | 0.0112956365 | RESOLVED_FAIL |
| R3_TRNA_LOW | F POST_INITIAL_LAYER | 0.1273620205 | 0.06348141308 | 0.0112956365 | RESOLVED_FAIL |

The formal advancement rule also checks every frozen R6 mandatory slow channel; all-channel scores and uncertainty are retained in condition_summary.csv and per-condition observable_scores.csv. Floors, windows and budgets are unchanged.

## State guards and boundary/domain diagnostics

- R3_BASE: {'A': 'RESOLVED_PASS', 'B': 'RESOLVED_PASS', 'C': 'RESOLVED_PASS'}; maximum state/coordinate error 0.00285733855418802; conservation drift 1.1485876700671197e-10; switch scaled jump 2.867149632620581e-05; physical-domain minimum 3.2988183520833777e-24; material new domain failure False.
- R3_ATP_LOW: {'A': 'RESOLVED_PASS', 'B': 'RESOLVED_PASS', 'C': 'RESOLVED_PASS'}; maximum state/coordinate error 0.004254736751445679; conservation drift 1.0336059785842622e-10; switch scaled jump 4.332159188009457e-05; physical-domain minimum 1.3396954984715732e-25; material new domain failure False.
- R3_TRNA_LOW: {'A': 'RESOLVED_PASS', 'B': 'RESOLVED_PASS', 'C': 'RESOLVED_PASS'}; maximum state/coordinate error 0.002857338501593088; conservation drift 2.3680765681710625e-10; switch scaled jump 2.867149182503018e-05; physical-domain minimum 3.419859447747971e-25; material new domain failure False.

Historical R6 H is preserved exactly. Fresh formal primary/probe trajectories use identical original retained switch coordinates and source startup; cumulative net extents retain the source startup integral.

## ATP-low post-layer current interpretation

R6 worst post-layer CK pair: `re0000000332_MINUS_re0000000333`. Scaled error 0.9933194893774895, maximum absolute error 129.24053750228694 concentration/s, source scale 130.10973698228918, floor 1e-09, worst time 9.906817032876724e-05 s. At that time signed source current 130.10973698228918 and R6 current 0.8691994800022276. Source zero crossings: []. Model zero crossings: []. Post-layer integrated source contribution 7983.3123138130695, zero-order contribution 7993.701536260628.

The boundary-inclusive post-layer normalization is reported together with its physical absolute scale and cumulative contribution. A large relative score near a small signed source signal does not by itself measure a large sustained absolute turnover error. The full-window and post-0.05 diagnostics remain separate; the formal post-layer score is never replaced.

## Bounded decision

A/B/C all resolved pass: True. D/F all mandatory rows in both windows pass: False. No material new domain failure: True. All advancement requirements met: False.
Formal current decreases in each condition/both windows: False; formal extent decreases in each condition/both windows: True.
Exactly one primary recommendation: **CK_FIRST_ORDER_IMPROVES_EXTENT_NOT_CURRENT**.

STOP after this report. No nine-condition first-order campaign has run. No push, merge, CK promotion or aminoacylation work. E/G remain descriptive BUT_NOT_VALIDATED. PURE_reduced_core remains NOT_VALIDATED and all 968 mechanistic decisions remain PENDING. Engineering verifier success does not confer scientific promotion.

## Signed startup-tail interpretation

The ATP_LOW 99.3% R6 post-layer peak is **a real short-lived boundary-current discrepancy, not a floor or zero-crossing artifact**. The worst point is the fixed switch at 9.90681703288e-05 s. Source current is 130.109736982, R6 current 0.869199480002, and the first-order current at identical switch slow coordinates is 0.800579427889 concentration/s. Its post-layer scale is 130.109736982, far above the 1e-9 floor; the source is nonzero at the worst point. The full-window source scale is 3000000, 23057.459569 times larger. Thus removing the initial burst changes the relative normalization substantially, but does not create the absolute discrepancy. By the first stored point at/after 1 ms, the source-minus-R6 startup-tail cumulative contribution is 0.00127507911378 concentration units. After 0.05 s the R6 CP-pair maximum absolute discrepancy is 0.0135613877359 concentration/s. The signed source fast-state distance from the first-order graph and its amplification by Gq are retained in boundary_current_diagnostics.csv. These observations support residual startup fast motion at the frozen switch. exp(-10) is a descriptive linear-mode reference, never a fitted law. No startup retuning, extra matching layer, time shift or source projection was performed.

The recommendation uses the preregistered requirement that current improve in **both** formal windows for each condition. A full-window current improvement alone cannot overturn the boundary-inclusive D failure. Cumulative extent improvement and current improvement are reported separately; the first-order postprocessing trajectory is not a self-consistent model.

## Component-wise correction sizes

- CK_CP: maximum |h1_i|/max(|h0_i|,1e-6) = 0.000504163704767, at R3_BASE t=0.0 s. The 1e-6 state floor is frozen R6; this is descriptive and creates no new gate.
- CK_CP_ADP: maximum |h1_i|/max(|h0_i|,1e-6) = 3.46924346939e-07, at R3_ATP_LOW t=1000.0 s. The 1e-6 state floor is frozen R6; this is descriptive and creates no new gate.

All retained outer postprocessing/formal samples were also checked: maximum vector correction/state ratio 5.29644288459e-06; maximum Gq condition 1.00001013809. Full signed physical margins are in first_order_trajectory_scale_diagnostics.csv.

The vector q norm can hide a larger relative change in a small free CK state. Across all source/outer samples, maximum physical-fast-state relative change is 0.0503864203338 in CK (SOURCE_SLOW_COORDINATES, t=0 s); this sample is applied by the candidate: False. Across the actual formal outer trajectory the corresponding maximum is 0.000449274689486. These individual physical-state ratios use the frozen 1e-6 state floor and remain descriptive.

## Local commits before evidence closeout

9282853a24d716e3021ea85123e9ba1e0bb4c6fc research: preserve uncommitted R6 Branch A evidence for additive R7 lineage
063ba6ea6518d22dda66123b96a468b2a6e06233 research: freeze additive R7 CK first-order derivation and three-condition contract

## Independent verification entry repair

The first final-verifier launch raised a missing `Path` import before score verification. Its failure is retained in verification_attempt_001.json. Run `python scripts/verify_r7_ck_first_order_entry_v1.py` to supply that import and execute the unchanged hash-bound verifier body. No model implementation, equation, data, preregistration or gate was changed. Canonical off-graph family/Gq verification is separately hash-bound. Nonlinear flow evaluations inside the consistency verifier are labelled RESUMMED_SUBSTITUTION_DIAGNOSTIC; no resummed trajectory was solved or scored.
