# R5 human authorization — 2026-10-07

The following is the verbatim supplied authorization. Only CK pair partial-equilibrium theory/testing, frozen-R4 GlyRS transverse diagnostics and balance decomposition are authorized. No promotion, deletion, fitting, threshold mutation, push or merge.

```text
You are starting R5 of the PURE reduction project.

Repository:
https://github.com/DrWanSJ/PURE

RUN FROM THE REPOSITORY ROOT.

============================================================
R5 TITLE
============================================================

R5 — MECHANISM-FIRST SINGULAR-PERTURBATION REDUCTION

The central methodological change is:

OLD APPROACH:
    choose a set of apparently fast species
    -> impose dq/dt = 0
    -> test the resulting QSSA numerically

R5 APPROACH:
    choose a mechanistically defined fast reaction subsystem
    -> derive invariants of the fast stoichiometric subnetwork
    -> define a parameterized singular limit
    -> derive the critical manifold
    -> prove / verify physical root uniqueness and fast-layer attractivity
    -> derive the reduced slow flow
    -> only then test the original-parameter model

This is a theory-first reduction stage.

Do NOT perform another combinatorial search over fast-state subsets.

============================================================
SCIENTIFIC AUTHORIZATION
============================================================

The human researcher authorizes exactly the following R5 work:

A. CK rapid-equilibrium / partial-equilibrium reduction study
   focused initially on the two CP-binding reversible reaction pairs;

B. GlyRS post-R4 transverse-dynamics / moving-manifold diagnostic,
   including feedback-aware transverse linearization;

C. numerical balance-residual decomposition to separate:
   - true conservation-law drift,
   - state integration error,
   - cumulative directed-extent integration error,
   - interpolation / cancellation error,
   - reduced-coordinate accounting error.

This authorization DOES NOT approve:

- any new reaction deletion;
- any new PURE_reduced_core;
- any automatic merging of CK, MK or NDK into an effective rate law;
- any higher-order GlyRS reduced model;
- any new full nine-condition candidate campaign;
- any parameter fitting;
- any modification of the canonical source model;
- any weakening of R3/R4 thresholds;
- any reinterpretation of R4 failures.

R4 remains frozen historical evidence.

============================================================
PHASE 0 — REPOSITORY SAFETY AND LINEAGE
============================================================

Before modifying anything:

1. git fetch origin
2. inspect:
       git status
       git branch -vv
       git log -10 --oneline --decorate
       git rev-parse HEAD
       git rev-parse origin/main
3. require a clean temporary worktree or isolated local branch;
4. record the actual parent main SHA;
5. verify R1/R2/R3/R4 frozen files remain unchanged.

Expected historical parent before R5 work:

    0b6f9ad649a7e283e440e0294a021123551f6858

R4 local commits reported by the previous stage were:

    88c0bfa
    9def91d

Those may or may not already exist on the current branch.

Do NOT assume they are on origin/main.

Inspect actual repository state and report it.

Do NOT:

- force reset;
- rewrite history;
- push;
- merge;
- delete historical attempts.

============================================================
PHASE 1 — FREEZE R5 THEORY REGISTRATION
============================================================

Create before decisive new numerical comparisons:

    docs/reduction/r5_mechanism_first_authorization_20261007.md
    docs/reduction/r5_mechanism_first_preregistration_v1.md
    docs/reduction/r5_theory_scope_v1.json

Bind them by SHA-256.

The preregistration must explicitly distinguish:

1. analytical / structural claims;
2. asymptotic-limit claims;
3. original-parameter numerical claims;
4. scientific promotion claims.

Never promote a statement from one category to another.

Example:

    "the eta -> 0 limit is mathematically consistent"

does NOT imply:

    "eta = 1 is quantitatively accurate".

============================================================
PHASE 2 — THEORY PRINCIPLE
============================================================

R5 must use the following logical sequence.

For a chosen fast reaction set R_f with stoichiometric matrix S_f:

1. derive a full-row-rank left-null basis L_f such that

       L_f S_f = 0

2. use

       z = L_f x

   as the natural slow / total coordinates associated with the fast subsystem;

3. identify independent fast coordinates q;

4. define a singularly parameterized family in which ONLY the declared fast
   reaction kinetics are rescaled;

5. derive the fast-layer problem at frozen z;

6. solve / characterize its equilibrium:

       g(z,q;0) = 0

7. establish:
       physical existence,
       local or global uniqueness where possible,
       attractivity,
       normal hyperbolicity on the declared domain;

8. derive the slow flow from the SLOW reactions evaluated on the critical
   manifold, not by simply deleting ODE rows;

9. reconstruct eliminated species from the slow coordinates;

10. separately define how eliminated microscopic reaction fluxes are
    reconstructed, if such reconstruction is claimed.

Do NOT use:

    "small closure residual"

alone as a validity criterion.

Do NOT require a candidate module to coincide with the globally fastest
same-dimensional Schur subspace.

That is a diagnostic, not a theorem requirement.

============================================================
TRACK A — CK PARTIAL-EQUILIBRIUM REDUCTION
============================================================

============================================================
PHASE A1 — VERIFY THE CANONICAL REACTIONS
============================================================

Start from the canonical source reaction table.

Expected candidate reversible pairs are:

    re0000000332
    re0000000333

and

    re0000000336
    re0000000337

Expected chemistry, to be VERIFIED from the repository:

    CK + CP <-> CK_CP

    CK_ADP + CP <-> CK_CP_ADP

Do not trust the prompt if the canonical source disagrees.

Write:

    docs/reduction/r5_ck_fast_reaction_definition_v1.md
    results/reduction/r5_mechanism_first/ck/reaction_definition.csv

For every reaction record:

- canonical reaction ID;
- reactants;
- products;
- stoichiometry;
- source subsystem;
- original source reaction ID;
- author kinetic parameter;
- units;
- canonical rate law;
- source hash.

Also explicitly list ALL other canonical reactions touching:

    CK
    CK_ADP
    CK_CP
    CK_CP_ADP
    CP

These are NOT removed.
They are the slow forcing of the fast subsystem.

============================================================
PHASE A2 — VERIFY AUTHOR PARAMETERS
============================================================

Read the actual author parameter CSV.

Expected values to verify:

    re0000000332_k1 = 2
    re0000000333_k1 = 1000
    re0000000336_k1 = 2
    re0000000337_k1 = 1000

Do not infer these from a default XML parameter.

Record exact parameter provenance.

If the values differ on the actual branch, STOP this derivation and report.

If they match, define descriptively:

    k_on = 2
    k_off = 1000
    K_d = k_off / k_on = 500 uM

Do NOT silently assume concentration units.
Verify repository unit conventions.

============================================================
PHASE A3 — FAST-SUBNETWORK STOICHIOMETRIC ANALYSIS
============================================================

Construct S_f for exactly the four directed reactions above.

Compute:

- rank(S_f);
- nullity;
- left-nullspace;
- independent reaction coordinates.

Independently verify the following candidate fast invariants:

    T0 = CK + CK_CP

    T1 = CK_ADP + CK_CP_ADP

    B  = CP + CK_CP + CK_CP_ADP

These are invariants of the FAST SUBSYSTEM ONLY.

They are NOT asserted to be conserved by the complete 968-reaction model.

Verify algebraically:

    dT0/dtau_fast = 0
    dT1/dtau_fast = 0
    dB/dtau_fast  = 0

under R_f alone.

Then quantify which non-fast canonical reactions change T0, T1 and B.

Write:

    docs/reduction/r5_ck_fast_invariants_v1.md
    results/reduction/r5_mechanism_first/ck/fast_left_nullspace.csv
    results/reduction/r5_mechanism_first/ck/slow_forcing_of_fast_totals.csv

============================================================
PHASE A4 — DERIVE THE CRITICAL MANIFOLD ANALYTICALLY
============================================================

Let:

    p  = [CP]
    q0 = [CK_CP]
    q1 = [CK_CP_ADP]

and use:

    CK     = T0 - q0
    CK_ADP = T1 - q1
    p      = B - q0 - q1

For the rapid-equilibrium candidate derive:

    q0 = T0 * p / (K0 + p)

    q1 = T1 * p / (K1 + p)

with K0 and K1 derived from the author parameters.

Then derive the scalar material equation:

    H(p; T0,T1,B)
      = p
        + T0*p/(K0+p)
        + T1*p/(K1+p)
        - B
      = 0

Independently prove / verify that for:

    T0 >= 0
    T1 >= 0
    B  >= 0
    K0 > 0
    K1 > 0

the physically relevant p root is unique.

Explicitly calculate:

    dH/dp
      = 1
        + T0*K0/(K0+p)^2
        + T1*K1/(K1+p)^2

and verify it is strictly positive for p >= 0.

Also prove:

    0 <= p <= B

for the physical root.

This analytical monotonicity / uniqueness result is preferred over a
multistart numerical root argument.

Still perform numerical cross-checks against direct nonlinear solving.

Create:

    docs/reduction/r5_ck_critical_manifold_derivation_v1.md
    scripts/verify_r5_ck_critical_manifold_v1.py

============================================================
PHASE A5 — FAST-LAYER ATTRACTIVITY
============================================================

Derive the frozen-total fast layer.

Using:

    q0_dot = k0_on * p * (T0 - q0) - k0_off * q0

    q1_dot = k1_on * p * (T1 - q1) - k1_off * q1

    p = B - q0 - q1

derive the exact fast Jacobian with respect to q0,q1.

For the special case where the two pairs have identical k_on/k_off,
derive the analytical eigenvalues if possible.

Expected structure:

    lambda_1 = -(k_on*p + k_off)

    lambda_2 = -(k_on*p + k_off
                 + k_on*((T0-q0)+(T1-q1)))

Verify the derivation symbolically and numerically.

For the actual repository parameters, evaluate the eigenvalues over the
full-source trajectories already available from R4.

Report:

- min |Re(lambda_fast)|
- max fast relaxation time
- condition dependence
- whether either eigenvalue approaches zero
- whether any physical-domain loss of normal hyperbolicity is observed

Do NOT infer global Fenichel validity outside the sampled / proven region.

Write:

    docs/reduction/r5_ck_fast_layer_stability_v1.md
    results/reduction/r5_mechanism_first/ck/fast_layer_stability.csv

============================================================
PHASE A6 — DEFINE A CLEAN SINGULAR LIMIT
============================================================

Construct a THEORY-ONLY parameterized family using a dimensionless
singular parameter eta.

For the selected fast reaction pairs define:

    k_on(eta)  = k_on*  / eta
    k_off(eta) = k_off* / eta

so that:

    K_d = k_off / k_on

remains constant.

DO NOT modify stoichiometry.

DO NOT scale the effects of those reactions on only selected species.

Every selected fast reaction must retain its full canonical stoichiometric
vector.

All non-fast canonical reactions remain unchanged.

Interpretation:

    eta -> 0

makes the selected reversible binding reactions infinitely fast relative to
the unscaled network while preserving the binding equilibrium constants.

This parameterized model is for asymptotic consistency testing only.

It is NOT the original physical model except at eta = 1.

Create:

    docs/reduction/r5_ck_singular_family_v1.md

The canonical source model must remain byte-identical.

Do not write eta-scaled parameters into the canonical parameter CSV.

============================================================
PHASE A7 — DERIVE THE REDUCED SLOW FLOW
============================================================

Do not derive the reduced model by deleting:

    CK_CP_dot
    CK_CP_ADP_dot

or any other ODE row.

Instead derive the slow flow from the fast invariants.

Let z contain at least the independent fast totals:

    T0
    T1
    B

plus the remaining exact R1 SOURCE_GENERAL slow coordinates required for the
full model.

Let Phi(z) reconstruct the fast-equilibrium physical state.

Then derive:

    z_dot = L_f * S_s * v_s(Phi(z))

where:

    S_s = all canonical stoichiometric columns not in R_f

and L_f is the appropriate coordinate map.

All 968 source reactions remain accounted for structurally.

The four fast directed reactions have zero leading-order NET fast-layer
contribution to z_dot because:

    L_f S_f = 0

Do NOT delete their microscopic gross ledgers from provenance.

Document separately:

- slow-coordinate dynamics;
- full-state reconstruction;
- microscopic fast-flux reconstruction policy.

Create:

    docs/reduction/r5_ck_reduced_slow_flow_derivation_v1.md
    scripts/r5_ck_partial_equilibrium_runtime_v1.py

============================================================
PHASE A8 — ASYMPTOTIC CONSISTENCY TEST
============================================================

Before testing the original model at eta=1, verify that the reduction behaves
as an actual singular perturbation approximation.

Use a small, preregistered sequence such as:

    eta = 1
          0.3
          0.1
          0.03
          0.01

unless numerical stiffness makes a value intractable.

If a different sequence is required, record it BEFORE decisive comparison.

For each eta:

- solve the eta-scaled full model;
- solve the eta=0 reduced model;
- compare slow coordinates;
- compare reconstructed fast states after the initial layer;
- estimate convergence order descriptively;
- retain the initial layer separately.

Do NOT claim a formal convergence order unless the data support it.

Expected qualitative question:

    Does error decrease systematically as eta -> 0?

If not, stop and inspect the derivation.

Do NOT run all nine R4 conditions at this stage.

Use baseline first.

============================================================
PHASE A9 — INITIAL LAYER
============================================================

Explicitly study the initial layer.

Do not require the zero-order outer solution to match all fast concentrations
at t=0 if the full initial state does not lie on the critical manifold.

Compute:

    q_full(0) - h0(z0)

and the corresponding fast-layer relaxation.

Construct and compare TWO clearly separated objects:

A. OUTER QSSA:
       algebraic critical-manifold solution only;

B. COMPOSITE / HYBRID APPROXIMATION:
       full fast-layer startup
       followed by reduced slow evolution.

Do not hide the startup period.

A hybrid switch, if studied, must use a preregistered switch rule based on
fast-layer relaxation / manifold distance.

No fitted switch time.

No time shift.

No initial-condition fitting.

============================================================
PHASE A10 — ORIGINAL PARAMETER eta=1 TEST
============================================================

Only after the singular-family test succeeds, evaluate the real source
parameter point eta=1.

Initially use BASELINE only.

Compare:

1. exact slow totals T0,T1,B;
2. relevant reconstructed fast species;
3. ATP / ADP / CP / Cr;
4. protein output;
5. energy-regeneration net conversion;
6. relevant CK-family rates;
7. source-general conservation quantities.

Do not yet require every microscopic fast gross directed extent to satisfy the
same state-error criterion.

Instead report three separate observability classes:

    REDUCED_SLOW_OBSERVABLES
    RECONSTRUCTED_FAST_STATES
    MICROSCOPIC_GROSS_FLUXES

Do not invent new acceptance thresholds.

For now this is:

    THEORY_VALIDATION / DESCRIPTIVE_ORIGINAL_PARAMETER_TEST

not a promotion gate.

============================================================
TRACK B — GLYRS TRANSVERSE-DYNAMICS DIAGNOSTIC
============================================================

============================================================
PHASE B1 — DO NOT BUILD A NEW GLYRS REDUCED MODEL YET
============================================================

Use the frozen R4 GlyRS-only results.

Do not rerun the nine-condition coupled screen unless necessary for missing
derivative data.

R4 reported strong post-layer lag correlation but nonzero residual error.

The next question is:

    Did the old lag predictor omit important feedback terms?

Do not assume the answer.

============================================================
PHASE B2 — DERIVE THE FULL TRANSVERSE ERROR LINEARIZATION
============================================================

For the R4 GlyRS-only graph:

    q = h0(z)

with:

    G(z,h0(z)) = 0

define:

    e = q - h0(z)

For:

    z_dot = F(z,q)
    q_dot = G(z,q)

derive:

    e_dot =
        -Dh0 F0
        + (G_q - Dh0 F_q) e
        + higher-order terms

where:

    F0 = F(z,h0(z))

and all Jacobians are evaluated on the zero-order graph.

Define:

    A_perp = G_q - Dh0 F_q

This is the feedback-aware local transverse operator.

Compare it to the old approximation that effectively used G_q alone.

============================================================
PHASE B3 — COMPUTE THE MISSING FEEDBACK TERM
============================================================

Using the existing R4 full-source trajectories and QSSA roots, compute:

    G_q
    F_q
    Dh0
    A_perp
    Dh0*F_q

at every valid source sample.

Report:

    ||Dh0 F_q|| / max(||G_q||, floor)

and suitable scale-normalized variants.

Also compare spectra / decay measures of:

    G_q

versus:

    A_perp

Do not compare only raw eigenvalues if matrices are strongly nonnormal.

Also compute:

- spectral abscissa;
- smallest singular value where informative;
- conditioning;
- logarithmic norm / numerical abscissa if useful;
- transient amplification diagnostics if nonnormality is significant.

Do not invent PASS thresholds.

============================================================
PHASE B4 — FEEDBACK-AWARE QUASI-STATIC LAG PREDICTOR
============================================================

Compare:

OLD predictor:

    e_old = G_q^{-1} Dh0 F0

NEW local quasi-static predictor:

    e_new = A_perp^{-1} Dh0 F0

where A_perp is nonsingular and locally stable.

Compare both to:

    e_true = q_full - h0(z_full)

For each GlyRS coordinate and condition report:

- correlation;
- relative L2 error;
- amplitude ratio;
- sign agreement;
- full window;
- post 0.05 s;
- t >= 1 s.

Do not use median alone.

Also report:

- worst coordinate;
- 95th percentile;
- worst condition;
- occupancy-weighted error;
- absolute concentration error.

============================================================
PHASE B5 — INVARIANCE-EQUATION RESIDUAL
============================================================

The true graph satisfies:

    G(z,h) = Dh F(z,h)

The zero-order graph h0 has defect:

    Delta0 = G(z,h0) - Dh0 F(z,h0)

Since G(z,h0)=0,

    Delta0 = -Dh0 F0

Compute a scale-aware diagnostic such as:

    tau_perp * ||Delta0||

where tau_perp is derived from the stable transverse dynamics.

The purpose is to turn an invariance defect with units uM/s into an estimated
state-tracking scale.

Do NOT declare this a rigorous error bound unless all assumptions required
for a bound have actually been established.

Call it:

    DEFECT_PROPAGATION_DIAGNOSTIC

unless rigorously proven otherwise.

============================================================
PHASE B6 — DECISION RULE FOR FUTURE GLYRS WORK
============================================================

Do NOT automatically build an h1 model.

At the end classify GlyRS into one of:

A.

    FEEDBACK_AWARE_CORRECTION_PROMISING
    HUMAN_REVIEW_REQUIRED

B.

    ZERO_ORDER_GRAPH_ERROR_NOT_EXPLAINED_BY_LOCAL_TRANSVERSE_FORCING

C.

    TRANSVERSE_DYNAMICS_NOT_UNIFORMLY_STABLE

D.

    NUMERICALLY_UNRESOLVED

For A, provide a proposed derivation for a true first-order invariance
correction, but do not execute a nine-condition validation.

============================================================
TRACK C — BALANCE RESIDUAL DECOMPOSITION
============================================================

============================================================
PHASE C1 — EXPLAIN THE R4 BALANCE PROBLEM
============================================================

R4 had balance uncertainty larger than its registered numerical budget.

Do not treat the single quantity:

    x(t) - x0 - S*xi(t)

as equivalent to a conservation-law test.

Separate at least:

1. EXACT CONSERVATION DRIFT

       L*x(t) - L*x(0)

   for the 27 SOURCE_GENERAL exact laws;

2. DIRECT STATE-INTEGRATION RESIDUAL

   based on solver trajectory and RHS;

3. DIRECTED-EXTENT RECONSTRUCTION RESIDUAL

       x(t) - x0 - S*xi(t)

4. GROSS-FLUX CANCELLATION SENSITIVITY;

5. EXTENT ODE integration error;

6. dense-output / interpolation contribution;

7. reduced-coordinate balance residual;

8. reconstructed full-state residual from algebraic states.

============================================================
PHASE C2 — USE EXISTING DATA FIRST
============================================================

Before rerunning anything, use the stored R3/R4 arrays.

The R4 package already contains:

- state trajectories;
- directed ledgers;
- solver-step records;
- uncertainty runs;
- exact conservation cross-checks.

Use them before starting expensive new solves.

Recompute balance residuals using:

- ordinary floating-point summation;
- compensated summation;
- math.fsum / high-accuracy summation;
- where practical, higher precision post-processing.

If higher-precision arithmetic changes only the diagnostic residual but not
the trajectory, record that fact.

Do not alter canonical trajectory values.

============================================================
PHASE C3 — IDENTIFY WHICH BALANCE TEST IS SCIENTIFICALLY MEANINGFUL
============================================================

Produce a report distinguishing:

    MODEL CONSERVATION FAILURE
    SOLVER TRAJECTORY ERROR
    LEDGER INTEGRATION ERROR
    NUMERICAL CANCELLATION
    REDUCED-COORDINATE ACCOUNTING ERROR

Do not weaken the historical R4 registered balance gate.

Do not retroactively change R4 classifications.

This analysis is explanatory only.

Create:

    docs/reduction/r5_balance_residual_decomposition_v1.md
    results/reduction/r5_mechanism_first/balance/
        balance_decomposition.csv
        balance_decomposition_summary.json

============================================================
PHASE 3 — LITERATURE / THEORY NOTE
============================================================

Create:

    docs/theory/qssa_singular_perturbation_guidance.md

The note should organize, not merely list, the theory relevant to this project.

Include separate sections for:

1. classical QSSA / Tikhonov singular perturbation;
2. rapid-equilibrium / partial-equilibrium approximations;
3. total QSSA;
4. noninteracting-species / linear elimination;
5. reaction-network graphical elimination;
6. coordinate-independent GSPT;
7. initial-layer and matched-asymptotic issues;
8. output / flux reconstruction after state elimination.

Do not claim a theorem applies to PURE unless its assumptions have been
checked.

The literature note should explicitly distinguish:

    theorem assumptions
    from
    PURE-specific verified facts.

If web access is unavailable, do not fabricate bibliographic details.
Use repository literature where available and leave external references as
TO_VERIFY rather than inventing citations.

============================================================
PHASE 4 — DO NOT USE GLOBAL SPECTRAL GAP AS THE PRIMARY GATE
============================================================

R5 must not repeat the following logical error:

    "candidate fast module does not equal the globally fastest m-dimensional
     Schur subspace"
    therefore
    "candidate QSSA is invalid".

Global Schur / CSP information may remain as supporting diagnostics.

The primary fast-layer questions are instead:

- what singular limit is being taken?
- what quantities are invariant under the fast reactions?
- does the frozen fast subsystem have the required physical equilibrium?
- is it attracting?
- is normal hyperbolicity retained on the domain?
- are the actual slow forcing rates small enough relative to relaxation?
- what error does the approximation produce at eta=1?

============================================================
PHASE 5 — DO NOT OVERCLAIM FAST-SUBSYSTEM CONSERVATION
============================================================

Every new quantity such as:

    T0
    T1
    B

must be labeled as one of:

    SOURCE_GENERAL_EXACT_CONSERVATION
    FAST_SUBSYSTEM_INVARIANT
    FROZEN_CONDITION_INVARIANT
    DYNAMIC_TOTAL_COORDINATE
    REPORTING_ONLY

For CK:

    T0
    T1
    B

are expected to be:

    FAST_SUBSYSTEM_INVARIANT
    DYNAMIC_TOTAL_COORDINATE

not global conserved constants.

============================================================
PHASE 6 — DO NOT CONFLATE PARTIAL EQUILIBRIUM WITH QSSA
============================================================

For the CK pair study use explicit terminology:

    RAPID_EQUILIBRIUM
    or
    PARTIAL_EQUILIBRIUM

Do NOT call it enzyme-cycle QSSA unless that is what is actually derived.

The approximation:

    forward gross flux ~= reverse gross flux

for selected reversible binding pairs is different from:

    intermediate derivative ~= 0

for a full catalytic cycle carrying nonzero steady throughput.

Document this distinction.

============================================================
PHASE 7 — MICROSCOPIC FLUX RECONSTRUCTION
============================================================

Do not assume that a state reduction automatically gives accurate individual
gross forward/reverse fast fluxes.

For every eliminated fast reaction distinguish:

A. leading-order equilibrium gross rates;

B. net slow redistribution flux needed to follow changing totals;

C. exact source gross directed extent.

If a first-order correction is required to reconstruct the net redistribution
flux, derive it rather than assigning zero net flux by definition.

Do not claim the reduced model preserves all 968 microscopic ledgers unless
this is independently demonstrated.

============================================================
PHASE 8 — COMPUTATIONAL COST
============================================================

R5 is deliberately smaller than R4.

Do not launch a large nine-condition full-coupled campaign yet.

Priority:

1. symbolic / structural derivation;
2. existing trajectory diagnostics;
3. baseline singular-family test;
4. baseline eta=1 test;
5. only then propose broader validation.

Reuse verified full-source R4 trajectories wherever source/model/hash
conditions match.

Avoid recomputing source trajectories without need.

============================================================
PHASE 9 — REQUIRED OUTPUT TREE
============================================================

Suggested structure:

    docs/reduction/
        r5_mechanism_first_authorization_20261007.md
        r5_mechanism_first_preregistration_v1.md
        r5_ck_fast_reaction_definition_v1.md
        r5_ck_fast_invariants_v1.md
        r5_ck_critical_manifold_derivation_v1.md
        r5_ck_fast_layer_stability_v1.md
        r5_ck_singular_family_v1.md
        r5_ck_reduced_slow_flow_derivation_v1.md
        r5_glyrs_transverse_dynamics_v1.md
        r5_balance_residual_decomposition_v1.md
        r5_mechanism_first_summary.md

    docs/theory/
        qssa_singular_perturbation_guidance.md

    results/reduction/r5_mechanism_first/
        ck/
            reaction_definition.csv
            fast_left_nullspace.csv
            slow_forcing_of_fast_totals.csv
            fast_layer_stability.csv
            singular_eta_scan.csv
            baseline_original_parameter_comparison.csv
        glyrs/
            transverse_operator.csv
            feedback_term.csv
            lag_predictor_comparison.csv
            lag_predictor_summary.csv
        balance/
            balance_decomposition.csv
            balance_decomposition_summary.json
        manifest.json

Suggested scripts:

    scripts/r5_ck_structure_v1.py
    scripts/r5_ck_partial_equilibrium_runtime_v1.py
    scripts/r5_ck_eta_scan_v1.py
    scripts/r5_glyrs_transverse_dynamics_v1.py
    scripts/r5_balance_decomposition_v1.py
    scripts/verify_r5_mechanism_first_v1.py

============================================================
PHASE 10 — INDEPENDENT VERIFICATION
============================================================

Write an independent verifier.

At minimum verify:

- canonical SBML unchanged;
- canonical parameter CSV unchanged;
- source initial values unchanged;
- all historical R1/R2/R3/R4 frozen evidence unchanged;
- selected CK reaction IDs match the canonical source;
- selected CK author parameters match the canonical parameter file;
- S_f is constructed correctly;
- L_f S_f = 0;
- declared fast invariants are algebraically correct;
- analytical CK root satisfies the fast equations;
- scalar-root monotonicity derivation matches numerical differentiation;
- fast-layer Jacobian formula matches finite differences;
- analytical eigenvalues match numerical eigenvalues where the special formula applies;
- eta scaling preserves K_d exactly;
- eta scaling preserves full stoichiometric action;
- non-fast reactions are unchanged;
- reduced slow flow is derived from projected non-fast source reactions;
- no parameter fitting;
- no clipping;
- no hidden projection of canonical source trajectories;
- no threshold mutation;
- no historical evidence mutation.

For GlyRS verify independently:

- G_q;
- F_q;
- Dh0;
- A_perp = G_q - Dh0 F_q;
- old and new lag predictor formulas.

============================================================
PHASE 11 — R5 SCIENTIFIC OUTPUT CLASSIFICATION
============================================================

The final report must distinguish at least these levels.

CK:

    CK_FAST_SUBSYSTEM_STRUCTURE_VERIFIED
    CK_CRITICAL_MANIFOLD_ANALYTICALLY_DEFINED
    CK_FAST_LAYER_ATTRACTING_ON_TESTED_DOMAIN
    CK_SINGULAR_LIMIT_CONSISTENT / NOT_CONSISTENT
    CK_ETA1_ACCURACY_DESCRIPTIVE
    CK_REDUCTION_NOT_YET_PROMOTED

GlyRS:

    FEEDBACK_AWARE_CORRECTION_PROMISING
or
    LOCAL_CORRECTION_INSUFFICIENT
or
    TRANSVERSE_DYNAMICS_NOT_UNIFORMLY_STABLE
or
    NUMERICALLY_UNRESOLVED

Balance:

    CONSERVATION_OK_LEDGER_NUMERIC_LIMITATION
or
    REDUCED_ACCOUNTING_DEFECT
or
    SOURCE_NUMERICAL_DEFECT
or
    MIXED / UNRESOLVED

No candidate is automatically approved.

============================================================
PHASE 12 — FINAL HUMAN DECISION POINT
============================================================

At the end DO NOT continue automatically.

Present a decision table:

Question 1:
    Is the CK partial-equilibrium singular limit mathematically coherent?

Question 2:
    Does error decrease as eta -> 0?

Question 3:
    Is eta=1 accurate enough to justify a formal broader validation?

Question 4:
    Does the feedback-aware GlyRS predictor substantially improve the R4
    lag explanation?

Question 5:
    Is the R4 balance uncertainty mostly ledger numerics or a real reduced
    accounting problem?

Then recommend exactly one of:

A.
    PROCEED_TO_CK_FORMAL_BASELINE_REDUCTION_VALIDATION

B.
    REFINE_CK_FAST_REACTION_SET

C.
    PROCEED_TO_GLYRS_FIRST_ORDER_MANIFOLD_DERIVATION

D.
    FIX_BALANCE_ACCOUNTING_BEFORE_ANY_NEW_REDUCTION

E.
    NO_R5_CANDIDATE_READY_FOR_PROMOTION

The recommendation is evidence for human review only.

Do not execute the next stage.

============================================================
FINAL REPORT TO USER
============================================================

Report concisely:

1. actual repository parent SHA;
2. whether historical evidence remained byte-identical;
3. CK selected reactions and verified equations;
4. CK parameter values;
5. rank(S_f);
6. derived fast invariants;
7. analytical critical manifold;
8. uniqueness proof status;
9. fast-layer attractivity status;
10. worst fast relaxation time on the tested source domain;
11. eta-scan behavior;
12. eta=1 baseline error;
13. initial-layer behavior;
14. GlyRS old vs feedback-aware predictor result;
15. role of Dh0*F_q;
16. balance-residual decomposition result;
17. unresolved assumptions;
18. generated files;
19. independent verifier result;
20. git status / local commits;
21. recommended next human decision.

Stop before push or merge.

============================================================
CORE R5 RULE
============================================================

Do not ask:

    "which species look fastest?"

Ask:

    "which reaction process admits a defensible singular limit,
     what does that process conserve on its fast timescale,
     what is its attracting critical manifold,
     and how accurate is that asymptotic approximation at the actual
     PURE parameter point?"

That is the governing methodology for R5.
```
