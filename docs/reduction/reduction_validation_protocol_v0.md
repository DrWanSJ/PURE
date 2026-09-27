# Reduction Validation Protocol — v0

Status: **FORMAL METHODOLOGY (v0)** for every PNAS 2017 subsystem reduction.
Scope: governs how a proposed reduction of the `PNAS2017_full_reference` model
is *classified, derived, pre-registered, tested, and certified*. It does **not**
authorize any specific reduction and does **not** build a project-wide reduced
model.

Companion machine-readable schema:
[`schemas/reduction_validation_protocol_v0.json`](../../schemas/reduction_validation_protocol_v0.json).

The first worked case is the aminoacylation subsystem
([`aminoacylation_full_subsystem.md`](aminoacylation_full_subsystem.md),
[`aminoacylation_reduction_candidates.md`](aminoacylation_reduction_candidates.md)).

---

## 0. Governing principles

1. **A reduction is never "validated" in the abstract.** Every claim is made
   relative to a *declared observable set*, a *declared accounting ledger*, a
   *declared mathematical operation*, and a *declared validity domain*. A model
   that reproduces the product curve but corrupts the ATP/GTP/PPi ledger is
   **invalid for this project** (see §H).
2. **Exactness is a mathematical property, not a numerical coincidence.** A
   transformation is called *exact* only when an identity holds to
   representation tolerance at *arbitrary feasible states*, not merely along the
   reference trajectory.
3. **Approximation requires pre-registration.** Thresholds, observables, and
   failure tests are frozen *before* any reduced-model error is inspected. No
   post-hoc threshold relaxation (D6/D7 discipline).
4. **Timescale separation is not a theorem inferred from one time point, and a
   stiff eigenvalue is not a QSSA certificate.** Structural/neutral modes must
   be excluded, an attracting algebraic manifold must exist, and it must move
   slowly. Absent these, a QSSA candidate is *blocked*, not *passed*.
5. **No silent acceptance.** If the evidence does not support a claim, the
   status is `FAILED`/`BLOCKED`/`HUMAN_REVIEW_REQUIRED`. The pipeline must
   *stop* rather than manufacture a closed form or a threshold to continue.
6. **Immutable sources.** Raw SBML, author CSVs, the Mavelli definition, frozen
   B1/D6/D7 evidence, and `scratch/` are read-only; `scratch/` is never a formal
   source. The canonical model is never edited to test a reduction.

The scientific question is **not** "can the reaction count be made small?" It is:
*"Which states and reactions can be removed or lumped while preserving the
observables, moiety accounting, resource accounting, and validity domain this
project requires?"*

---

## 1. Reduction classes

A candidate reduction is assigned to exactly one primary class (or is rejected).
Classes **A** and **B** are exact; **C–G** are representational or approximate;
**H** is an orthogonal qualifier that every reduction must also carry.

### A. Exact representation change

Replacing a description with a mathematically identical one at arbitrary states.
Canonical example: two one-way reactions `A→B` (rate `v_f`) and `B→A`
(rate `v_r`) re-expressed as one reversible reaction `A ⇌ B` with net flux
`v_net = v_f − v_r`.

- This is **not** QSSA, **not** fast equilibrium, **not** an assumption of any
  sort. The reverse rate `v_r` is retained; equilibrium is **not** imposed.
- **Required evidence**
  - exact stoichiometric equivalence: net vector of reverse == −net of forward;
  - exact RHS equivalence at arbitrary feasible states (not just the reference);
  - full trajectory equivalence to numerical (representation) precision;
  - identical resource / moiety accounting (the ledger is untouched).
- **Status ceiling:** `EXACT_VALIDATED`. Never reported as evidence for an
  approximate class.

### B. Exact conservation reduction

Use `L·S = 0` (left null space of the stoichiometry matrix `S`) to eliminate
redundant state coordinates **only when an explicit reconstruction map exists**.

- **Required evidence**
  - `rank(S)` and a complete declared invariant basis `L`;
  - a set of independent reduced coordinates;
  - an explicit reconstruction map `x = R(y, c)` from reduced state `y` and
    invariant constants `c` back to full state `x`;
  - the RHS reconstruction identity `S·v(R(y,c))` reproduces `dy/dt`;
  - full ⇄ reconstructed trajectory equivalence.
- **Do not** call this QSSA. Rank deficiency of the full Jacobian that merely
  reflects conserved totals is a conservation law, not a slow manifold.

### C. Functional pooling / lumping

For a proposed coarse state `y = A·x`, exact closure asks whether some
`f̄` exists with `A·f(x) = f̄(A·x)` over the declared domain.

- If exact closure does **not** hold, the pool is at most a **reporting
  variable** or an **approximate** reduction candidate — never an exact
  elimination.
- **Required evidence:** pool definition `A`; moieties represented; a closure
  test; the list of *unrecoverable microstate observables* destroyed by the
  projection; the assumptions needed for approximate closure.
- Only a declared **family total** (active + degraded, see project species map)
  may be labelled a *conservation candidate*; an "active pool" is a reporting
  variable unless closure is proven.

### D. QSSA (quasi-steady-state / slow manifold)

Partition into fast `q` and slow `s`:
`ds/dt = F(s,q)`, `dq/dt = G(s,q)`. QSSA requires `G(s,q) ≈ 0` **with an
attracting slow manifold** `q = h(s)`. It does **not** mean `q ≈ 0`.

- **Required evidence:** explicit fast and slow variables; the algebraic
  manifold `h(s)`; branch uniqueness; local attraction (eigenvalues of
  `∂G/∂q` with negative real part and a genuine gap); fast and slow relaxation
  times; `ε = τ_fast/τ_slow`; a **moving-manifold** diagnostic (`ḣ ≠ 0` handled
  via `dq/dt = (∂h/∂s)·(ds/dt)`, i.e. the residual is `G − (∂h/∂s)F`, not `G`);
  initial-layer behaviour; full-vs-reduced trajectories; an explicit failure
  domain.
- **Guardrail:** near-zero fast-block eigenvalues arising from conservation or
  zero-concentration states are **structural neutral modes** and must never be
  inverted into `τ_fast`. A stiff eigenvalue alone is not sufficient; the
  attracting-manifold and slow-motion conditions must both hold.

### E. Fast (rapid) equilibrium

Stronger and different from generic QSSA: a reversible step is treated as
algebraically equilibrated (`v_net = 0`).

- **Required evidence:** a forward/reverse pair *plus* demonstration that it is
  equilibrated (affinity ≈ 0 relative to the slow scales), not merely that a
  pair exists.
- **Guardrail:** *never* infer fast equilibrium because an `A ⇌ B` pair exists.
  The pair's existence is a class-A structural fact only.

### F. Chemostat (boundary-condition fixing)

Fixing a species to a constant is an external-reservoir boundary condition, not
state deletion.

- **Required evidence:** the reservoir species; its full dynamic depletion in
  the reference; reservoir capacity relative to consumption; the error induced
  by freezing it; the physical interpretation.
- **Project guardrail:** `CP`/`Cr` **must not** be silently chemostatted — the
  current reference shows CP drawdown buffers ATP. Any chemostat of an energy
  carrier is a human scientific decision, never a reduction convenience.

### G. Conserving degradation / sink lump

Degradation may **not** be replaced by `X → ∅` where material accounting matters.
A lumped sink must preserve the declared amino-acid, phosphate, and
nucleotide/base moieties and relevant particle-number accounting.

- **Guardrail:** the generic label `DROP_CANDIDATE` is **never** permission to
  delete a degradation without a conserving replacement.

### H. Observable-dependency qualifier (mandatory on every reduction)

Every reduction record declares its observable set and accounting variables. A
reduction is only valid *relative to those observables*. Product concentration
alone is an insufficient observable; the energy/moiety ledger is part of the
contract.

---

## 2. Common validation outputs (Phase 3)

Where relevant, a reduction comparison reports **all** of:

1. product / process output; 2. state trajectories; 3. free energy-carrier
pools; 4. tRNA pools; 5. machinery occupancy; 6. instantaneous fluxes `v(t)`;
7. **cumulative reaction extents** `ξ_j(t) = ∫₀ᵗ v_j(τ)dτ`; 8. conservation /
moiety totals; 9. degradation inventories; 10. a particle-number proxy.

**Cumulative extent is mandatory**, because similar endpoint trajectories can
conceal very different cumulative resource consumption.

For PNAS translation reductions the accounting set includes, where applicable:
`ATP, ADP, AMP, GTP, GDP, PPi, Pi/PO4, CP, Cr`; `free tRNA`,
`aminoacyl-tRNA`, `peptidyl-tRNA`; and the relevant `free ribosome`,
initiation / elongation / termination-recycling occupancy.

**Ionic strength is `NOT ASSESSABLE FROM CURRENT SOURCE DATA`.** The source SBML
carries no reliable charge / protonation / Mg convention (0 `unitDefinition`s;
`formal_net_charge` null; `protonation_convention="unknown"`). It must be left
explicitly marked as such and never inferred.

---

## 3. Error metrics (Phase 4)

For a trajectory quantity `y(t)`:

```
E_inf(y) = max_t |y_red(t) − y_full(t)| / max(y_scale, 1e-12)
```

with `y_scale` **declared before** reduced-model results are inspected (default
`y_scale = max_t |y_full(t)|`; zero-initial quantities use `y_scale = 1`).

Also report, as appropriate: maximum absolute error; endpoint relative error;
integrated absolute error `∫|y_red−y_full|dt / y_scale`; peak-time error. For
vectors/pools report per-component errors **and** the overall maximum. For
fluxes report both `v(t)` and `ξ(t)`. For conservation totals report the
absolute residual **and** the scaled residual.

**Tolerance tiers are quantity-class specific; one blind number is forbidden:**

| Tier | Applies to | Representative criterion |
|---|---|---|
| T-A | exact algebra / exact rewrite (class A) | machine precision (≲ 1e-9 relative), at arbitrary feasible states |
| T-B | conservation / reconstruction identity (class B) | invariant residual ≲ declared conservation tolerance |
| T-C | approximate state trajectories (D–G) | pre-registered, purpose-scaled |
| T-D | approximate instantaneous fluxes | pre-registered; looser than T-C (fluxes are noisier) |
| T-E | approximate **cumulative** resource extents | pre-registered; the resource ledger is usually the binding constraint |
| T-F | timescale separation | `ε = τ_fast/τ_slow` with structural modes excluded; report-only unless a manifold exists |

Exact classes use a **much stricter** criterion than approximate classes. A tier
may never be relaxed after results are seen; relaxation is a new, separately
recorded, human-approved revision.

---

## 4. Lifecycle and statuses

`PROPOSED → PREREGISTERED → {EXACT_VALIDATED | APPROXIMATELY_VALIDATED |
FAILED | BLOCKED | HUMAN_REVIEW_REQUIRED}`.

- A reduction may not enter numerical acceptance testing until it is
  `PREREGISTERED` (source SHA, mapping, reduced equations, parameters, initial
  conditions, solver, window, observables, accounting, error formulas,
  thresholds, validity/failure domain frozen).
- If a scientifically justified threshold cannot be chosen without human
  judgment, set `HUMAN_REVIEW_REQUIRED = true` and **stop** the approximate
  acceptance run. Do not invent a threshold to continue.
- Every certificate must end with an explicit, **scoped** status. The bare word
  "validated" is prohibited; write the class and the domain.
- A certificate is incomplete without ≥ 1 negative/stress test
  (§ failure tests): the reduction is documented as reference-only if it holds
  only at the reference condition.

See the schema for the exact field set and the allowed `status` enumeration.
