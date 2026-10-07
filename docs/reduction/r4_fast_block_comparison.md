# R4 fast-block comparison

| Candidate | Type | Primary complete | Resolved / all gates | Scientific status |
|---|---|---:|---:|---|
|GlyRS|Chemical QSSA|9/9|0/9 ; 0/9|UNRESOLVED_ON_REGISTERED_DOMAIN|
|MetRS|Chemical QSSA|9/9|0/9 ; 0/9|UNRESOLVED_ON_REGISTERED_DOMAIN|
|MIXED_CSP_MODE_BLOCK|Geometric modes|198 samples|N/A|NUMERICALLY_UNRESOLVED|

| Candidate | Worst state | Worst post0.05 state | Worst AA rate | Worst AA extent | Coupled closure | Graph defect (uM/s) |
|---|---:|---:|---:|---:|---:|---:|
|GlyRS|1.15867506|0.0371710579|1.15912253|0.502410746|9.9997427e-11|46.0248579|
|MetRS|1.18878011|0.141076767|1.18950972|0.393154537|9.99962717e-11|163.28611|

Historical21 versus split candidates (descriptive, identical scoring definitions): worst post-layer state error is historical_R3_21=0.141076766, R4_GLYRS_ONLY=0.0371710579, R4_METRS_ONLY=0.141076767. Maximum primary RHS calls are historical_R3_21=368062, R4_GLYRS_ONLY=103635, R4_METRS_ONLY=95238. GlyRS-only improves post-layer error and reduces solver burden; this does not repair its full-window state/rate failures or resolve balance uncertainty. MetRS-only retains essentially the historical worst post-layer error.

The CSV keeps chemical QSSA gate metrics separate from geometric mode metrics. N/A is explicit; no common meaningless PASS/FAIL column is used. Detailed per-condition raw gates, uncertainties, balance, solver burden, branch geometry and lag remain in result.json and certificate tables. Side-by-side 21-state/GlyRS/MetRS comparisons are in `historical_r3_comparison/side_by_side.csv`.

Causal family outcome: **UNDETERMINED_NUMERICAL_UNCERTAINTY_OR_NONCOMPLETION**. The four logical pass/fail alternatives cannot be asserted while a family lacks resolved full-domain tests. If any raw errors improve, that alone does not establish all-gate support. No inference that aminoacylation QSSA is impossible is authorized. Historical R3 remains unchanged; its recorded nine-condition rejection is not retroactively reclassified by new uncertainty diagnostics.

Closure, defect and lag for the historical21 block were independently recomputed as diagnostic comparison, without h1 or higher-order correction. A smaller algebraic system can still carry a large moving-manifold defect. CSP span rotations and participation are not deletion authority.

Recommendation: retain all failed/unresolved work. Resolve numerical representation and tolerance-convergence qualifications before any new scientific transition; human review must distinguish initial-layer failures from post-layer errors and chemistry-facing CSP mapping. No reduced core, final winner, fitted rate, transcription/GUV coupling, push or main merge.
