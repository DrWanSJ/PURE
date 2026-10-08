# CHAIN_01 V2 prospective resource-preserving comparison

Date: 2026-10-08 (Asia/Shanghai). Branch: `codex/pnas-topology-first`.
R0 source HEAD: `3a216aab92e1976f433d9b83641c6ef96b22a6cf`.

This new protocol is independent of CHAIN_01 V1. V1 remains
`LOCAL_CANDIDATE_FAILED_REGISTERED_SCREEN`. No V2 trajectory was computed before
this protocol freeze. R1 may begin only after this R0 commit has been pushed and
the actual remote branch SHA has been verified.

The exact source audit rereads canonical SBML, the author parameter, initial-value
and reaction CSVs, all 968 topology reaction-table entries, the original three-step
case study, and the V1 implementation. All 241 source-species net column
differences are exactly zero for each candidate. The author constants are
260, 1000, 7, 1000, with re21=0.23; placeholder SBML k1=1 is not the condition.
Source time units are retained without conversion to seconds.

The old three-step aliases A/X1/X2/B map to new S1/S2/S3/S4. The exact five-state
mapping, source kinetic MathML, side incidences, author overlay and raw file
fingerprints are recorded in `results/reduction/chain01_v2/source_manifest.json`.
S4 is the bound Pept0002 extension state, not free final Pept0003 or a full PURE
protein yield. The proposed comparisons measure this local production proxy.

| Model | Local path | Rates | Reactions | Chemical states including S4 |
|---|---|---|---:|---:|
| Full | S0→S1→S2+Pi→S3+EFTu_GDP→S4 | 260,1000,7,1000 | 4 | 5 |
| Direct | S0→S4+Pi+EFTu_GDP | ke=1/tau | 1 | 2 |
| Two-stage | S0→S2+Pi→S4+EFTu_GDP | ka=1/(1/260+1/1000), kb=1/(1/7+1/1000) | 2 | 3 |
| Three-stage | S0→S1→S2+Pi→S4+EFTu_GDP | 260,1000,kb | 3 | 4 |

All candidates use mean-dwell-matched Markov rates; matching the mean is not an
exact waiting-kernel equivalence. If z_i denotes a retained stage, J_i=k_i z_i,
then z_0'=u-J_0, z_i'=J_{i-1}-J_i, S4'=J_last. Each directed extent has derivative
J_i. Pi is emitted at the designated Pi stage and free EF-Tu.GDP at its designated
release stage. Chemical inventory coefficients are tied to the literal retained
source state. No uncounted hidden reconstruction variables are used.

For constant input u and no competition, z_i*=u/k_i and every eventual stage
current equals u. The mean total wait is sum(1/k_i); the variance is sum(1/k_i^2).
If d_R is the sum of waits up to resource release, xi_R=u(t-d_R)+o(1).
Thus xi_candidate-xi_Full→u(d_Full-d_candidate), a persistent absolute offset
that does not disappear when the percentage relative to cumulative input shrinks.
The complete exact rational steady ledgers and model-specific asymptotes are in
`mathematical_certificate.json`. These are algebraic predictions, not simulated
acceptance results.

The base experiment replaces the upstream network by nonnegative prescribed u,
omits active re21, and isolates S4 downstream. R2 restores source re21 as
S0→EFTu_GTP_GlytRNAGlyGCC+elRS70SAGGU0002_fMet. Both products accumulate explicitly;
re13 rebinding remains outside this open local test. Success probability is
k_in/(k_in+c), escape is c/(k_in+c). The conditional successful dwell includes
1/(k_in+c) followed by all downstream waits. Exact chemical product columns and
fate identities are recorded for checking this boundary implementation.

The frozen JSON fixes unit pulse [0,100]tau; sustained input [0,10000]tau;
exp(-t/T) with T/tau=20,100,1000 over ten supply decay times; V1 rectangular inputs;
and the V1 nonzero-inventory control. It fixes [5,10]tau and [10,end]tau as required
macro windows, alongside the early and V1 transient/post windows as diagnostics.
The initial-composition control is excluded prospectively because its projection
preserves ribosome amount while changing nucleotide/factor stage composition.

The independent exploratory macro budget is 1% for both product current and
integrated formation extent, and 1% for resource currents, extents, bound Pi/GDP,
bound GTP precursor, EF-Tu occupancy, unreleased phosphate equivalents and
unfinished ribosome inventory. Amount scales are fixed at cohort 1 or u0*tau;
current scales are cohort/tau or u0. Relative cumulative errors remain descriptive.
R2 additionally requires 1% relative accuracy of **both** success and escape
probabilities, to preserve allocation of a small resource-carrying return route.
Numerical tolerances, grids, windows and threshold rationales are in the JSON.
No thresholds can be retuned after trajectories are observed.

R0 validation: five structural tests, exact source/column checks and all preexisting
1737 tracked-file raw byte fingerprints. R1 will use the reliable V1 Radau and
matrix-exponential logic, augmented for exponential input, tighter tolerances,
and a standalone source-reconstructed analytic verifier. Numerical noncompletion
must remain NUMERICALLY_UNRESOLVED. The final smallest-model recommendation will
be conditional on independent product, ledger and boundary support; full coupled
validation and reduced-core approval remain separate decisions.
