# R7 CK first-order preregistration v1

This bounded feasibility study is authorized solely for R3_BASE, R3_ATP_LOW,
R3_TRNA_LOW. No other condition, R3_ADVERSE, full nine-condition campaign,
aminoacylation work, push, merge or scientific promotion is authorized.
The four fast reactions and all 964 slow reactions are unchanged.

Inputs and all 3079 pre-R7 files are SHA-256 bound in pre_r7_snapshot.json.
The actual R6 Git execution parent is 1181ab2f0a04d72cf76fb069be6bb842e3de75d8;
R6's final execution state was uncommitted, so its final commit SHA is N/A.
An additive local preservation commit records its exact completed files in R7.
This distinction must remain visible in the lineage report.

Freeze this document, authorization, derivation, numerical contract, executable
R7 implementation and input provenance with registration_binding.json before
any decisive R7 comparison. One registration only; never rebind after results.

Objects: ZERO_ORDER_R6, FIRST_ORDER_POSTPROCESSING_ON_Z0, and
FORMAL_FIRST_ORDER_SELF_CONSISTENT, all compared with CANONICAL_FULL_SOURCE.
Source and R6 zero-order evidence are reused after checking hashes, condition
definitions, original x0, native dense data and completed R6 result records.
Fresh primary and tighter formal slow solves are mandatory for each condition.
Analytic Dh1 is primary; complex-step is independent; centered Richardson is
a further diagnostic. Structure checks, graph residuals, eta-family identities,
h0 equality, j0 equality, j1 identity and analytic formal Jacobian are tested.

Scoring is exactly R6: FULL_WINDOW and POST_INITIAL_LAYER mandatory;
POST_0P05_DIAGNOSTIC and COMPOSITE_OR_HYBRID descriptive. State/coordinate
floor=1e-6, gate=.01; current floor=1e-9, gate=.05; extent floor=1e-6, gate=.01;
exact-law drift absolute gate=1e-8. Window scale=max(max|source|,floor).
Use primary BDF rtol=1e-10, atol=1e-14; probe 1e-11,1e-15. Net extents use
segmented DOP853, compensated accumulation, the same primary/probe tolerances
and a tighter quadrature on each primary outer trajectory. Reuse the R6/R4
source uncertainty and startup probe. Current cancellation uses 8*eps times
the two source directed rates; extents use 8*eps times source gross cumulative
extents solely for uncertainty accounting, never E/G scoring. Uncertainty sums
source/probe, reduced/probe and quadrature/cancellation. Bound each state or
extent solve to the frozen R6 1800s (state RHS <=300000). Preserve noncompletion.

Resolved status: uncertainty <=.1*gate required. error+uncertainty<=gate gives
RESOLVED_PASS; max(0,error-uncertainty)>gate gives RESOLVED_FAIL; otherwise
NUMERICALLY_UNRESOLVED. Score all frozen R6 mandatory D/F channels as well as
the two CK pairs. A includes unaffected states and all 212 slow coordinates;
B uses exactly R6 algebraically affected species; C checks both full source
and formal model exact SOURCE_GENERAL laws. No H historical reclassification.

Record each pair's signed current, source maximum, floor, absolute error,
worst time, sampled zero crossings (linear diagnostic estimates plus brackets,
no time shift) and cumulative contributions. No altered denominator or window.
Report ||h1||/max(||h0||,1e-6) and ||h1||/max(||fast totals||,1e-6), individual
physical CK free/bound margins, distance outside the physical polytope,
Gq condition number, minimum singular value and stability distance. The
descriptive FIRST_ORDER_CORRECTION_NOT_SMALL flag uses ratio>=1 against
the fast-state scale, frozen prospectively; it is not an acceptance gate.
Material new CK-domain failure means correction-induced negative CK margin
larger than the corresponding frozen .01*max(full-source state scale,1e-6)
plus probe envelope. Strict negative margins and accepted totals are always
reported separately with no clipping and no positivity threshold mutation.

Advance ONLY if on all three conditions the formal model has A/B/C all
RESOLVED_PASS, D and F both FULL_WINDOW and POST_INITIAL_LAYER RESOLVED_PASS,
no noncompletion and no new material physical-domain failure. E/G are
SOURCE_PROVENANCE_PRESERVED / DESCRIPTIVE / BUT_NOT_VALIDATED, never gates.
If any advancement requirement fails, STOP with no broader run.

Choose exactly one primary recommendation from the human-authorized list.
Priority: ill-posed derivation; noncompletion/unresolved essential scores;
all advancement requirements met; correction comparable to fast-state scale;
current-only improvement; extent-only improvement; states valid and both
improved but failing; no material improvement. Improvement is descriptive:
both full and post-layer maximum CK errors decrease in each condition;
all numerical scores remain present. Additional flags are allowed.
PURE_reduced_core remains NOT_VALIDATED; all 968 decisions remain PENDING.
Derived evidence_navigation.json records EXTRACTED/INFERRED/AMBIGUOUS status,
source hashes and freshness, subordinate to canonical evidence.
