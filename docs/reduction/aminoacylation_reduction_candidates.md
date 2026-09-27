# Aminoacylation — reduction candidate levels (A0–A4)

First worked case for
[`reduction_validation_protocol_v0.md`](reduction_validation_protocol_v0.md).
Each candidate is classified by protocol class, and its status is deliberately
capped at what the current evidence supports. **No approximate candidate is
accepted here**; several terminate at `HUMAN_REVIEW_REQUIRED` by design.

Evidence artefacts: [`aminoacylation_fast_states.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_fast_states.csv),
[`aminoacylation_enzyme_pool_conservation.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_enzyme_pool_conservation.csv),
[`aminoacylation_timescale.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_timescale.csv),
[`aminoacylation_pathway_balance.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_pathway_balance.csv),
[`aminoacylation_reversible_pair_validation.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_reversible_pair_validation.csv).

---

## Candidate A0 — reference subsystem

All 138 aminoacylation reactions / 47 species, exactly as in the source. No
transformation. Status: reference baseline. Used as the comparison target for
A1–A4 and as the source of the reference trajectory diagnostics.

---

## Candidate A1 — exact reversible rewrite  *(protocol class A)*

Combine only the 52 structural forward/reverse pairs into single reversible
reactions with `v_net = v_f − v_r`; **no state is eliminated and no rate law is
approximated** — the forward and reverse laws are both retained.

- **Mathematical operation:** representation change; reverse net vector == −forward net vector (verified for all 52).
- **Exact vs approximate:** **exact**.
- **Evidence:** exactness validated at 400 feasible states per pair (200 reference + 200 arbitrary positive);
  max relative residual = 0.0; **52/52 pass** at the T-A tolerance (≲1e-9).
- **Resource/moiety accounting:** unchanged by construction.
- **Observables lost:** none.
- **Guardrails honoured:** this is *not* QSSA and does *not* assert that any pair
  is at equilibrium (both `v_f` and `v_r` are kept). Inactive (`k1 = 0`) reverse
  members are noted as inactive, not equilibrated.
- **Status:** `EXACT_VALIDATED` (representation). Reaction-count effect: merges
  52 pairs from 104 one-way reactions into 52 reversible laws.

A1 is the **only** aminoacylation reduction this task certifies. It buys
representational clarity, not state-count reduction of the ODEs (the number of
distinct species is unchanged).

---

## Candidate A2 — functional enzyme-pool reporting  *(protocol class C)*

Define `MetRS_total` = free MetRS + all MetRS\_\* complexes, and `GlyRS_total`
analogously. Bound forms are **not** deleted — the pools are defined and tested
first.

- **Conservation test result:** over every reaction active at the author
  reference (`k1 > 0`), `L·S = 0` for the active pool (max residual `0.0e+00`) —
  the active enzyme pools are **exact conserved coordinates at the reference**.
- They are broken *only* by the `_degraded` enzyme sinks, whose `k1 = 0` at the
  reference. The **active + degraded family total** is conserved over *all*
  aminoacylation reactions (max residual `0.0e+00`).
- **Classification:** the family total is a legitimate **conservation candidate**
  (protocol class B reconstruction applies); the *active* pool alone is a
  **reporting variable** — a conserved total *conditional on degradation being
  off*, not an unconditional elimination.
- **Reconstruction / accounting role:** the pools give a moiety ledger for
  synthetase, but the microstate occupancy (which complex holds the enzyme) is
  **not recoverable** from the pool total.
- **Status:** `HUMAN_REVIEW_REQUIRED` — using these totals as *reporting*
  variables is well-founded; *eliminating* bound states via the pool requires the
  A3 closure argument and is not accepted here.

---

## Candidate A3 — aminoacyl-adenylate / enzyme-complex QSSA  *(protocol class D)*

Fast block derived **from the network**, not from names:

- **Fast states (30 subsystem-wide; 15 per synthetase):** the 28 `E_*` enzyme-bound
  complexes plus the free aminoacyl-adenylates `MetAMP`, `GlyAMP`. Per-state
  producers/consumers, typical concentration, enzyme and moiety membership are in
  `aminoacylation_fast_states.csv`.
- **Slow states (11):** `Met, Gly, ATP, AMP, PPi`, free `MetRS, GlyRS`,
  free `tRNAfMetCAU, tRNAGlyGCC`, `MettRNAfMetCAU, GlytRNAGlyGCC`.

**Timescale evidence (report-only).** Along the author trajectory, the fast block
Jacobian has a stable stiff relaxation scale `λ_stiff ≈ 5.15e4 s⁻¹`
(`τ_fast ≈ 1.9e-5 s`), essentially constant over `t ∈ [1e-4, 1e3] s`, against a
slow-pool scale `τ_slow ≈ 1e-1 … 5e4 s`. The stiff/slow gap ratio
`ε_stiff` ranges **3.2e-10 … 1.5e-4**, i.e. a large separation exists.

**Why A3 is nevertheless NOT certified:**

1. **No algebraic manifold `q = h(s)` was derived.** A stiff eigenvalue gap is
   *necessary, not sufficient* for QSSA. Without a unique attracting branch and a
   moving-manifold residual `G − (∂h/∂s)F`, protocol class D is unsatisfied →
   status `BLOCKED` / `HUMAN_REVIEW_REQUIRED`.
2. **Structural neutral modes are present.** The fast block also carries
   near-zero eigenvalues (up to 2 per sample) that come from enzyme conservation
   and zero-concentration complexes — these must **not** be inverted into a fast
   timescale (D6 methodology).
3. **Guardrail #1 & #4 are live risks.** Complex *concentrations* are small
   (median 1e-6…1e-2 µM vs enzyme total 0.35–0.44 µM) but **not** all negligible:
   the free adenylate `GlyAMP` reaches ~24 µM on the reference. "Bound complexes
   are fast" and "enzyme occupancy is negligible" are **not** demonstrated.
4. The subsystem-local diagnostic assumes aminoacylation closure; the real
   network couples `ATP/AMP/PPi` to energy regeneration, so a whole-network
   `τ_slow` could differ.

**Status:** `BLOCKED` (no manifold) → `HUMAN_REVIEW_REQUIRED` for whether to
attempt a manifold derivation at all.

---

## Candidate A4 — one-step effective charging flux  *(protocol classes C + G, strongest lump)*

Collapse each synthetase cycle to one effective reaction
`AA + ATP + tRNA → aa-tRNA + AMP + PPi`.

- **Net stoichiometry:** derived from the SBML and **matches** the expected net
  chemistry for both Met and Gly (see `aminoacylation_pathway_balance.csv`):
  ΔATP −1, ΔAMP +1, ΔPPi +1, ΔAA −1, ΔtRNA −1, Δaa-tRNA +1, particle-number Δ 0,
  8 enzyme intermediates cancelled each.
- **What the stoichiometric audit proves:** the *chemistry* (one amino-acid
  incorporation, one charging event, ATP→AMP, PPi generated, particle number
  conserved) is exactly the net of the detailed cycle.
- **What it does NOT prove:** the *kinetics*. A single effective rate law must
  reproduce charging flux and cumulative resource use across the validity domain.
  That requires the A3 manifold (to eliminate intermediates), non-saturated
  conditions, or an experimentally fixed rate law — none established here.
- **Observables lost:** all 28 complex occupancies, the free adenylates, the
  adenylate/pyrophosphate *partitioning timing*, and any mischarging/proofreading
  signal. Cumulative `AMP`/`PPi` may match while the *instantaneous* flux and
  intermediate occupancy differ.
- **Explicit non-claim:** A4 is **not** declared accepted merely because aa-tRNA
  production matches (forbidden claim #6, #7).
- **Status:** `PROPOSED` → `HUMAN_REVIEW_REQUIRED` (a threshold for cumulative
  resource tolerance T-E cannot be justified without the researcher's purpose).

---

## Cross-candidate accounting summary

| candidate | class | exact? | states removed | accounting preserved | status |
|---|---|---|---|---|---|
| A1 | A representation | exact | 0 | full | `EXACT_VALIDATED` |
| A2 | C pooling | exact totals, active pool conditional | 0 (reporting) | enzyme moiety total | `HUMAN_REVIEW_REQUIRED` |
| A3 | D QSSA | approximate | up to 30 fast (per pathway 15) | needs manifold | `BLOCKED` → review |
| A4 | C+G lump | stoichiometry exact, kinetics unproven | all intermediates | net ledger matches, kinetics unproven | `PROPOSED` → review |

None of A2–A4 may be promoted past a human scientific decision in this task.
