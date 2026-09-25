# Aminoacylation reduction certificate — v0

> **Scoped result.** This certificate records what the first formal
> reduction-validation cycle on the PNAS 2017 aminoacylation subsystem actually
> proved. **Only the class-A exact rewrite (A1) is certified as exact.** Every
> approximate candidate is recorded as *not accepted*, at an explicit status.
> No project-wide reduced model was built (`models/pure_reduced_core/*.xml` was
> **not** created; that remains unauthorized for this task).

1. **Source / version / provenance.**
   Branch `research/pnas2017-full-network-reduction`, source HEAD
   `8710b85cac27dbe7a1a2805a8e7f79d87e3d51e6`. Model
   `models/pnas2017_full_reference/original/fMGG_synthesis.xml`, SHA-256
   `dc43bcec…40183df` (matches `data/provenance.csv`). Canonical SBML and author
   CSVs **unmodified**.

2. **Reference subsystem definition.** 138 reactions (134 pure + 4 interface),
   47 species, selected by `Aminoacylation_*` subsystem label. Formylation
   (`FMet_tRNASynthesis`) excluded by project decision. See
   [`aminoacylation_full_subsystem.md`](aminoacylation_full_subsystem.md).

3. **Proposed reduced coordinates.** A1: none removed (representation only).
   A2: `MetRS_total`, `GlyRS_total` (reporting). A3: 30 fast states
   (15/synthetase) on a hypothetical manifold. A4: net `aa-tRNA` only.

4. **Reaction mapping.** A1: 52 forward/reverse pairs → 52 reversible laws
   (`aminoacylation_reversible_pairs.csv`). A4: per-enzyme catalytic cycles →
   one net charging reaction (`aminoacylation_pathway_balance.csv`).

5. **Exact transformations.**
   - **Class A (A1):** `v_net = v_f − v_r` on each structural pair; reverse net
     vector = −forward net vector for all 52.
   - **Stoichiometric identity (A4 net):** summing true SBML cycle vectors
     cancels all 8 enzyme intermediates per pathway and yields exactly
     `AA + ATP + tRNA → aa-tRNA + AMP + PPi` (ΔATP −1, ΔAMP +1, ΔPPi +1,
     particle Δ 0). **This is a statement about stoichiometry, not kinetics.**

6. **Approximate assumptions.**
   - A3 assumes an attracting `q = h(s)` — **not derived**.
   - A4 assumes an effective single rate law — **not derived**.
   - A2 active-pool conservation assumes degradation `k1 = 0` (true at reference
     only).

7. **Algebraic derivation.** Net-chemistry derivation shown in §5 / pathway
   balance CSV. **No closed-form reduced rate law was derived or justified**;
   per protocol none was manufactured.

8. **Conservation / moiety accounting.** `MetRS_total` and `GlyRS_total`
   (`L·S = 0`) verified; family total (active + degraded) conserved over all
   reactions. Enzyme and tRNA moieties tracked; degraded sinks kept separate.

9. **Resource accounting.** ATP/AMP/PPi ledger: exactly 1 ATP→1 AMP+1 PPi per
   charging event, in both derived pathways. Ionic strength
   **NOT ASSESSABLE FROM CURRENT SOURCE DATA** (left uncomputed by policy).

10. **Timescale evidence (report-only).** Stiff fast scale `λ≈5.15e4 s⁻¹`
    (`τ_fast≈1.9e-5 s`) vs slow pools; `ε_stiff ≈ 3e-10…1.5e-4`. **A large gap
    was observed. This is not, and is not recorded as, a QSSA certificate:** the
    fast block carries structural near-zero modes (conservation / zero-concentration
    complexes), and no attracting algebraic manifold or moving-manifold residual
    was established.

11. **Full-vs-reduced numerical evidence.** Performed only for the **exact**
    class (A1): RHS-equivalence at 400 feasible states (200 reference + 200
    arbitrary positive), max relative residual **0.0**, **52/52 pass** at
    tolerance 1e-9. **Approximate full-vs-reduced runs were not executed**
    (Phase 13 stop).

12. **Validity domain.** A1: all feasible states (exact). A2 reporting: any
    state; A2 elimination: none claimed. A3/A4: undetermined.

13. **Failure domain.** A2 active pool: fails if degradation is activated.
    A3: expected in initial layer / saturation / low-synthetase / energy-coupled
    regimes. A4: expected under saturation and where intermediate partitioning
    timing matters. These are **declared failure tests**, not yet run.

14. **Unrecoverable observables.** A2: enzyme microstate occupancy. A3/A4: all
    enzyme-bound complex and free-adenylate occupancies, adenylate/PPi
    partitioning timing, mischarging/proofreading signal.

15. **Evidence classification.** Structural/mathematical correctness established
    for A1 (exact) and for the A4 **stoichiometry**. Numerical approximation
    quality: **not assessed** (no approximate run). Literature/experimental
    validity: **not assessed**.

16. **Unresolved scientific questions.** Formylation boundary; in-coupling vs
    isolated validation; the T_C/T_D/T_E/T_F thresholds; whether to attempt an
    A3 manifold at all; the GlyAMP ~24 µM non-negligibility. See
    [`aminoacylation_human_review_v0.md`](aminoacylation_human_review_v0.md).

17. **Explicit status (per candidate, with scope).**

    | candidate | status |
    |---|---|
    | **A1** | `EXACT_REWRITE_VALIDATED` — *scope: class-A representation change only; no state or accounting change* |
    | A2 | `HUMAN_REVIEW_REQUIRED` — *exact enzyme-pool totals confirmed as conservation candidates; state elimination not accepted* |
    | A3 | `BLOCKED` (no algebraic manifold) → `HUMAN_REVIEW_REQUIRED` — *QSSA not certified* |
    | A4 | `PROPOSED` → `HUMAN_REVIEW_REQUIRED` — *net stoichiometry exact; effective kinetics not derived or tested* |

**Forbidden-claim attestation.** None of protocol §5 claims (bound complexes are
fast; aminoacylation is at steady state; ATP is constant; enzyme occupancy is
negligible; all complexes collapse; one-step charging validated; a good aa-tRNA
curve proves the ledger; similar output ⇒ valid; a reversible pair is at
equilibrium; `DROP_CANDIDATE` ⇒ removable) was assumed. Each was explicitly
checked and *not* relied upon.
