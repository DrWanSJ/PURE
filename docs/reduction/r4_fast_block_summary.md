# R4 fast-block screen summary — 2026-10-07

Actual parent main: `0b6f9ad649a7e283e440e0294a021123551f6858`. Execution approval is for testing only. Execution status: COMPLETED_BOUNDED_SCREEN. Numerical and scientific statuses are per candidate/condition below; human promotion: HUMAN_REVIEW_REQUIRED.

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

Frozen source, parameters, initial values, acceptance criteria and all pre-existing R1/R2/R3/H4/H5 evidence are individually checked against the 1,644-file parent snapshot. See the independent verifier for the final measured result. External audit: all161 registered outputs verified; used files have exact hashes; directory read only. Fresh baseline source agreement: 4.49409e-14 trajectory-scaled.

Primary domain is exactly the nine completed historical source conditions. All R4 reduced primary/uncertainty solves are fresh. Numerical noncompletion is UNSCORED; relevant uncertainty >10% of tier budget takes precedence over raw gate pass/failure. Full initial layers, all241 state errors and all968 gross directed rate/extent channels are retained wherever a primary comparison completes.

Both families have nine resolved FAIL_STATE and nine resolved FAIL_RATE tier outcomes. Each has eight FAIL_EXTENT and one PASS_REGISTERED_TIER extent outcome (its own low-enzyme condition); all nine balance tiers remain NUMERICALLY_UNRESOLVED. Native reporting-only failures in six records were recovered from hash-bound completed numerical arrays; raw records/tracebacks and all failed arithmetic attempts remain unchanged. Review classification is in derived_review_result.json.

Causal family outcome: UNDETERMINED_NUMERICAL_UNCERTAINTY_OR_NONCOMPLETION. No supported causal conclusion about combined-block/shared-resource geometry is available unless both family screens are numerically decidable. Mixed diagnostic: NUMERICALLY_UNRESOLVED; span variation reaches 90 degrees temporally and 90 across conditions. Strong CK/MK participation requires human chemistry-facing review; no global fixed block is approved.

Seven figures, each with underlying CSV, are under `figures/`. Inspect individual certificates, comparison, per-condition result/uncertainty/geometry tables and the hash-bound manifest. The derived evidence graph is navigation only and never replaces source evidence.

Unresolved questions: whether numerical uncertainty can be controlled at the fixed balance budget; whether family-only post-layer accuracy survives every coupled gate; whether moving mode-space support can be mapped to a conservation-preserving chemical module. Recommendations are for human review only. R3_ADVERSE is unchanged, unscored and not rerun. All968 mechanistic decisions remain PENDING. PURE_reduced_core remains NOT_VALIDATED. No old21 higher-order correction or automatic next stage was executed. No push or main merge.
