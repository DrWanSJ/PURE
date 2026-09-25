# Aminoacylation — review response and decisions (v1)

This document responds to the v0 human-review checkpoint
([`aminoacylation_human_review_v0.md`](aminoacylation_human_review_v0.md)) and
records the scientific decisions, boundaries, thresholds and errata that govern
the v1 cycle. It supersedes the v0 decision boxes **without rewriting them**:
every v0 artefact listed below remains byte-frozen at the hashes recorded in
`docs/audit/pnas2017_aminoacylation_reduction_v0/preregistration.json`; where a
v0 statement was wrong or overstated, the correction appears here (and only
here) as an erratum, and the v0 text stands as the historical record.

**Authorization source.** The decisions in §1–§3 were issued by the user in the
execution prompt of this working session (2026-09-25). They are *research,
implementation and testing authorizations*, not pre-approvals of results: no
approximation in this document is certified until the v1 validation evidence
exists. This document is an AI-transcribed record of the user's written
decisions; it is not a human signature and does not constitute independent
human verification of any numerical result.

Workspace baseline at the start of this round:

| item | value |
|---|---|
| branch | `research/pnas2017-full-network-reduction` |
| HEAD | `8710b85cac27dbe7a1a2805a8e7f79d87e3d51e6` (unchanged; no commit, no push this round) |
| prior-round artefacts | 20 untracked v0 files, SHA-256 baselined before this round began; none modified or deleted |
| unexplained files | `docs/reduction.zip` (SHA-256 `7629efa4…b5a67311`) — a 2026-09-25 snapshot of `docs/reduction/`; ownership indeterminate, retained untouched |

---

## 1. Accepted decisions (A0–A4)

### A0 — full reference model retained (accepted)

The complete 138-reaction / 47-species aminoacylation subsystem (A0) stays the
declared reference against which every reduction is compared. It remains in
force as the *unreduced control*; nothing in v1 deletes or replaces it.
See erratum E1 for what "reference" does and does not mean.

### A1 — exact reversible merge of 52 forward/reverse pairs (accepted)

Merging the 52 recognised pairs into reversible representations is accepted as
an **exact representation transform**. Requirements for v1 bookkeeping:

- `v_forward`, `v_reverse` and `v_net = v_f − v_r` are all retained and
  reported, together with both original reaction IDs;
- the merge is **not** a QSSA, **not** a fast-equilibrium claim, and licenses
  neither interpretation;
- cumulative/gross accounting in v1 ledgers is computed from the **original
  directed fluxes**, never from |v_net| (see erratum E7 and ledger semantics
  fix §2 of this round's ledger audit);
- trajectory-level equivalence: the v0 evidence is pointwise RHS identity at
  400 states. Integrated-trajectory comparison was **not executed in v0** and
  is executed in v1 under the frozen tolerance (erratum E2).

### A2 — enzyme active/degraded/family pools as reporting variables (accepted)

`MetRS_active_pool`, `MetRS_family_total` (and GlyRS counterparts) are accepted
as **reporting** variables. Adding a report does not delete any microstate and
does not lose any information still carried by the retained states (erratum
E3). Separately permitted and proven where applicable:

```
free_enzyme = enzyme_total − Σ bound_enzyme_states          (exact reconstruction)
```

including the degraded pool where the declared total covers it. This is exact
coordinate elimination of a *redundant* variable backed by a proved conservation
law; it is **not** a claim that the total determines the bound-state
distribution.

### A3 — QSSA: authorized research, selectively, evidence-first (accepted with restriction)

QSSA research is authorized. The v0 candidate's blanket 30-fast-state
pre-designation is **not** adopted. The v1 working candidate is:

> **A3a — selective enzyme-bound-state QSSA with the free aminoacyl-adenylates
> `MetAMP` and `GlyAMP` explicitly retained as dynamic states.**

Which enzyme-bound states may be eliminated is decided by this round's
mathematical and numerical evidence (§6 of the execution plan: algebraic
closure `G(s,q)=0`, attraction spectrum explained mode-by-mode, relaxation
tests, invariance defect). A final outcome that eliminates only a subset of the
bound states is an accepted result, not a failed one. High intermediate
concentration neither rejects QSSA by itself (cf. E4) nor does a large negative
eigenvalue accept it.

### A4 — one-step charging replacement (deferred, not authorized this round)

Replacing the subsystem by a single effective charging law is kept as a later
candidate only. The v0 net-stoichiometry proof for the two selected catalytic
cycles is retained but does **not** license closure of the whole network by one
flux (erratum E7). Evidence for or against A4 accrues in v1 only as a
by-product of A3a work and is reported, not acted upon.

### Formylation boundary (decided)

`FMet_tRNASynthesis` (29 reactions) stays **independent, unmodified, and
dynamically coupled** in the whole-network reference. No reduction of
`FMet_tRNASynthesis` is performed this round. `MettRNAfMetCAU` is **not**
treated as a constant boundary species; its production (aminoacylation
reactions) and consumption (formylation) remain dynamic on both sides of every
comparison.

### Validation environment (decided)

- Local freeze-and-diagnose and input-replay runs are permitted as *diagnostic*
  tiers, and must be labelled as such (they do not test feedback of the reduced
  module into the network).
- **Formal approximate acceptance must run in the coupled PNAS whole-network
  context**: full 968-reaction reference vs. the same network with *only* the
  approved aminoacylation replacement, everything else (formylation, energy
  regeneration, elongation, termination/recycling, degradation) untouched, and
  ATP/AMP/PPi, tRNA/aa-tRNA shared dynamically. No infinite reservoirs.

---

## 2. Thresholds adopted for v1 (engineering acceptance conventions)

These are project engineering-acceptance conventions fixed by the user prompt
of this round — not literature experimental error bars and not universality
theorems. They are frozen in
`docs/audit/pnas2017_aminoacylation_reduction_v1/acceptance_criteria.json`
before the first formal full-vs-reduced error comparison (local hash-binding;
explicitly *not* an immutable Git-time proof since this round does not commit).

| tier | scope | criterion |
|---|---|---|
| A-structure | integer/rational net-stoichiometry identities | exact |
| A-conservation | declared exact conservation laws | structural, exact |
| A-RHS | independent implementation vs. reference RHS | scaled ≤ 1e-12 |
| A-A1 | integrated-trajectory equivalence of the exact merge | scaled ≤ 1e-6 |
| A-algebra | QSSA algebraic closure residual `G(s,h(s))` | scaled ≤ 1e-10 |
| B | normalized conservation / boundary-inclusive balance residual, both models | ≤ 1e-8 |
| C (`T_C`) | approximate state/output trajectories `E_inf` | ≤ 0.01 |
| D (`T_D`) | approximate instantaneous process fluxes `E_inf` | ≤ 0.05 |
| E (`T_E`) | cumulative chemical conversions / charging / resource extents (whole curve) | ≤ 0.01 |
| F (`T_F`) | timescale separation screen `ε = τ_fast/τ_slow` | ≤ 0.01 (screen only, never a substitute for attraction/ledger/layer/trajectory evidence) |

Error normalization: `E_inf(y) = max_t |y_red − y_full| / max(S_y, floor_y)`,
`S_y = max_t |y_full|` computed **only from the corresponding full reference**
on the frozen output grid; floors: concentration and concentration-form
cumulants 1e-6 µM, concentration fluxes 1e-9 µM/s, dimensionless ratios 1e-12.
Zero-initial variables are *not* uniformly assigned scale 1; absolute errors
and floor-usage flags are reported alongside every scaled error. Reported
integral errors include time normalization
`E_int = ∫|y_red−y_full|dt / (T_window · max(S_y, floor_y))`. Near-zero net
fluxes are never used as denominators; reaction-contribution or
production/consumption scales declared before the run are used instead.
Initial-layer windows, the numerical-error budget rule (solver uncertainty ≤
10 % of the allowed approximation error, else `NUMERICALLY_UNRESOLVED`), and
the full acceptance procedure are in the v1 acceptance-criteria JSON.

---

## 3. What is authorized vs. what remains unverified

Authorized this round: the A1 representation change (exact), A2 reporting and
exact free-enzyme reconstruction (exact), the *derivation and testing* of A3a
(approximate — status to be decided by evidence), the frozen-threshold
validation protocol, the six pre-declared stress conditions, and the software
negative test.

**Not** verified or claimed anywhere in this round until the corresponding run
exists and is recorded: A1 integrated-trajectory equivalence (now scheduled),
any A3a manifold validity, any full-vs-reduced agreement, any failure-domain
characterization, and every statement about behaviour outside the tested
conditions. No claim in these documents constitutes experimental or
literature validation.

---

## 4. Errata against the v0 record

The v0 files remain as written (hash-frozen). The following statements in the
v0 record are corrected here; each references the exact v0 location.

**E1 — A0 is a declared reference model, not an assumption-free oracle.**
v0 (`aminoacylation_human_review_v0.md` §A0: "Assumptions: none … Validity
domain: all"). A0 is the *published author model as embedded in our pipeline*:
it carries the authors' modelling assumptions, the author parameter export
(including 54 aminoacylation reactions with `k1 = 0`), the unit convention, and
our import/normalization choices. Its "validity domain" is the declared
reference domain of that construction, not "all real systems".

**E2 — A1 evidence is representation identity + pointwise checks, not
trajectory verification.** v0 (`aminoacylation_reduction_candidates.md` §A1,
`aminoacylation_full_subsystem.md` §Phase 8) records 52/52 exact RHS identity
at 400 states — that is a *pointwise* check. No integrated full-vs-reduced
trajectory comparison was executed in v0; the v0 wording did not say so
explicitly. v1 executes the trajectory comparison at ≤ 1e-6 and reports it as
performed-then, not before.

**E3 — A2 reporting loses nothing; distribution unrecoverability is a separate
statement.** v0 (`human_review_v0` §A2: "Observables lost: microstate occupancy
(unrecoverable)"). Correction: adding the pool reports does **not** lose any
microstate — all 47 states remain in the model. The correct, separate statement
is: from the *pool total alone* one cannot recover the bound-state
distribution (i.e. the map `x → A·x` is non-invertible); that is a statement
about what a single scalar determines, not about what the model has discarded.
Exact elimination of the *free enzyme* coordinate via the proved total is
additionally permitted (A2 decision above) and is a redundancy removal, which
retains recoverability of the free state by construction.

**E4 — free GlyAMP/MetAMP are not enzyme occupancy.** v0 (§A3 evidence
"GlyAMP occupancy is not negligible (~24 µM)"). `GlyAMP`/`MetAMP` are *free*
aminoacyl-adenylate species in solution. Their concentration is not an enzyme
occupancy in any sense. The actual occupancy metric is defined in this round's
audit as

```
enzyme_bound_fraction(E) = Σ bound_states(E) / active_enzyme_total(E)
```

and is reported separately from free-adenylate levels. This round's audit
confirms the ~24 µM figure is real in the author trajectory (GlyAMP terminal
23.73 µM, MetAMP 29.82 µM at t = 1e3 s — see the v1 GlyAMP audit artefact) and
that it must be interpreted as a *free intermediate inventory*, whose size is
exactly why A3a retains both adenylates as dynamic states.

**E5 — the stiffest eigenvalue does not characterize the fast subspace.** v0
(§A3: "stable stiff relaxation scale λ_stiff ≈ 5.15e4 s⁻¹"). That number was
the largest |Re λ| of the fast block. The relaxation of the whole eliminated
subspace is bounded from below by the **slowest attracting mode**,
`α = min_j(−Re λ_j)` over modes proven attracting; every candidate fast-block
mode (attracting, near-zero, positive, complex) must receive an individual
explanation in v1. v1 reports the full spectrum, not a single λ.

**E6 — near-zero eigenvalues require proof, not size or zero-concentration
heuristics.** v0 (fast-block near-zero modes attributed to "enzyme
conservation and zero-concentration complexes"). Attribution by smallness or by
zero current concentration is not evidence. Only modes with an explicit
conservation-law or redundant-coordinate proof may be removed from the fast
analysis; modes arising from boundary effects, rank loss, or genuine slow
chemistry must be kept and reported, and any loss of attractivity is a
candidate failure, not a rounding detail.

**E7 — the selected-cycle net stoichiometry is not a whole-network flux
identity.** v0 (§Phase 7 "net chemistry", §A4, certificate §5). The 8-step
cycle sums establish the *net计量 of two chosen cycles only*. They do not
identity ATP chemical consumption ≡ PPi production ≡ AMP free release ≡ charging
at any time, because the network contains additional active routes (e.g. free
adenylate binding/dissociation `re0000000147/148`, and branch steps outside the
selected cycles), intermediate inventories that change in time (free GlyAMP and
MetAMP *accumulate to tens of µM*), and reverse channels. v1 replaces the
"two-stage" picture with ledgers derived from the full stoichiometric matrix
plus measured inventory terms; the simplified diagram is marked local
explanation only.

**E8 — zero net particle change of a cycle does not freeze a particle proxy in
time.** v0 (§Phase 7 "net particle-number change = 0 (so a one-step lumping at
least does not perturb the particle-number proxy)"). Correction: the cycle sum
proves only that one net event conserves particle count. In finite time,
interconversion between bound complexes and free species changes the count of
*dissolved particles* (e.g. `E·AA-AMP → E + AA-AMP` raises it), so any
particle-number proxy must be computed from species counts of the full (or
fully reconstructed) state, per declared definition, and tracked, not assumed
constant.

**E9 — eliminated states may be approximately recoverable through `h(s)`.**
v0 (certificate §14 "Unrecoverable observables" listed all complex
occupancies). Correction: under A3a, once `q = h(s)` is established, the
eliminated occupancies are *approximately reconstructed* by `h(s)` within the
validated error budget, and (for exactly eliminated redundant coordinates such
as free enzyme under A2) *exactly* reconstructed. Only if closure fails are
they genuinely lost. The blanket "unrecoverable" label is withdrawn; per-state
classification (exact / approximate-via-h / lost) is delivered in the v1
certificate.

**E10 — "proofreading/mischarging signal" was imported from general biochemistry
without a source-model locator.** v0 (§A4 observables lost, certificate §14).
The PNAS 2017 aminoacylation network contains no non-cognate substrate and no
dedicated editing/proofreading reaction. The nearest modelled channels are:
tRNA-deacylation `re0000000176` (Gly-tRNA → Gly + tRNA) and `re0000000218`
(Met-tRNA → Met + tRNA), and free-adenylate hydrolysis/synthesis
`re0000000143/149` (GlyAMP ⇌ Gly + AMP) and `re0000000168/174`
(MetAMP ⇌ Met + AMP) — all with `k1 = 0` at the author reference (verified this
round against the author parameter export). v0's "mischarging signal loss" is
therefore corrected to: A4 would additionally destroy these *inactive-at-
reference decharging/hydrolysis channels*, which are the only editing-like
mechanisms present in the source. No claim beyond these named reactions may be
made about proofreading.

**E11 — registration order of v0.** The v0 `preregistration.json` freezes the
hashes of artefacts that had already been generated, and records
`formal_runs_before_registration: 0`. That field was true for *formal
approximate runs* but the ordering claim it supports is weaker than it reads:
post-hoc content hashing cannot prove that registration preceded exploratory
analysis, and exploratory analysis did occur before the freeze. v1 records
honestly:

```
prior_exploratory_runs_exist = true
registration_binding = local_content_hashing (not a git-history proof; this round does not commit)
```

Any post-registration change to equations, thresholds, or domains creates a new
revision; old runs are kept.
