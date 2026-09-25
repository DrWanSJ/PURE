# Aminoacylation — human scientific review (v0)

Checkpoint per protocol §4. This document lays out each candidate for a
**researcher decision**. The decision boxes are intentionally left **unchecked**;
no scientific selection has been made by the analysis. The AI-generated
evidence levels here are *structural / numerical*, **not** human verification or
experimental validity.

Companion: [`aminoacylation_reduction_candidates.md`](aminoacylation_reduction_candidates.md),
[`preregistration.json`](../audit/pnas2017_aminoacylation_reduction_v0/preregistration.json).

---

## A0 — reference subsystem
1. **Biochemical meaning:** the full MetRS/GlyRS charging mechanism as published.
2. **Source reactions:** 138 (134 pure + 4 interface). **Source species:** 47.
3. **Mathematical operation:** none. 4. **Exact vs approximate:** n/a (baseline).
5. **Assumptions:** none. 6. **Evidence:** this is the reference.
7. **Accounting preserved:** all. 8. **Observables lost:** none.
9. **Validity domain:** all. 10. **Failure modes:** stiffness (24 fast stiff
   modes, `λ≈5.15e4 s⁻¹`) makes it costly to integrate.

## A1 — exact reversible rewrite
1. **Meaning:** represent the 52 recognised forward/reverse pairs as reversible
   reactions.
2. **Source reactions:** the 104 reactions forming the 52 pairs.
3. **Species:** all 47 retained. 4. **Operation:** `A ⇌ B`, `v_net = v_f − v_r`.
5. **Exact:** **yes**, an identity. 6. **Assumptions:** none (equilibrium is
   *not* imposed; both laws kept).
7. **Evidence available:** 52/52 exact, max relative residual 0.0 over 400
   feasible states. 8. **Accounting preserved:** fully. 9. **Observables lost:**
   none. 10. **Validity domain:** all feasible states. 11. **Failure modes:**
   none mathematical; only cosmetic (fewer written reactions).

## A2 — functional enzyme-pool reporting
1. **Meaning:** track `MetRS_total` / `GlyRS_total`.
2. **Source reactions:** all MetRS\_\*/GlyRS\_\* producing/consuming steps.
3. **Species:** free enzyme + complexes (and `_degraded` for the family total).
4. **Operation:** linear pool `y = A·x`. 5. **Exact:** family total exact;
   active-pool exact **only while degradation `k1=0`** (true at reference).
6. **Assumptions:** none for reporting; **elimination** of bound states would
   need A3. 7. **Evidence:** `L·S = 0` for both pools (conservation CSV).
8. **Accounting preserved:** enzyme moiety total. 9. **Observables lost:**
   microstate occupancy (unrecoverable). 10. **Validity:** active-pool conservation
   breaks the moment degradation is switched on. 11. **Failure modes:** treating a
   *reporting* pool as if it *eliminated* states.

## A3 — aminoacyl-adenylate / complex QSSA
1. **Meaning:** set the 30 fast enzyme/adenylate states on a slow manifold.
2. **Source reactions:** the binding/adenylation/transfer steps.
3. **Species:** 30 fast removed; 11 slow retained.
4. **Operation:** `G(s,q)≈0`, `q=h(s)`. 5. **Approximate.**
6. **Assumptions required:** unique attracting manifold, slow manifold motion,
   clean fast/slow split. 7. **Evidence available:** only a stiff/slow eigenvalue
   *gap* (`ε_stiff` 3e-10…1.5e-4) — **no manifold derived**, near-zero structural
   modes present, and GlyAMP occupancy is **not** negligible (~24 µM).
8. **Accounting:** depends on the derived `h(s)`; unproven. 9. **Observables
   lost:** all complex/adenylate occupancies. 10. **Validity:** unknown.
11. **Likely failure modes:** initial layer; saturated-enzyme regimes; low
   synthetase; ATP/PPi coupling to energy regeneration.

## A4 — one-step effective charging
1. **Meaning:** replace each synthetase cycle by `AA + ATP + tRNA → aa-tRNA + AMP + PPi`.
2. **Source reactions:** the whole per-enzyme cycle. 3. **Species:** all
   intermediates removed. 4. **Operation:** stoichiometric lump (+ conserving
   degradation sinks).
5. **Exact:** **stoichiometry** exact (net verified, 8 intermediates cancel,
   ΔATP −1/ΔAMP +1/ΔPPi +1, particle Δ 0); **kinetics unproven**.
6. **Assumptions required:** an effective rate law (needs A3 or a non-saturation
   assumption). 7. **Evidence available:** net chemistry only. 8. **Accounting:**
   net ledger matches; instantaneous/cumulative flux unverified. 9. **Observables
   lost:** every intermediate, the adenylate/PPi partitioning timing, mischarging
   signal. 10. **Validity:** unknown. 11. **Failure modes:** saturation, low
   enzyme, co-limiting ATP, proofreading.

---

## Researcher decisions (leave unchecked — for human sign-off)

```
[ ] KEEP REFERENCE DETAIL
[ ] ACCEPT EXACT REWRITE (A1)  — analysis certifies A1 as exact; formal acceptance is the researcher's
[ ] ACCEPT FUNCTIONAL POOL ONLY (A2 reporting, no state elimination)
[ ] TEST QSSA (A3)  — requires deriving an algebraic manifold; set T_C/T_D/T_E/T_F
[ ] TEST ONE-STEP EFFECTIVE CHARGING (A4)  — requires an effective rate law + T-E threshold
[ ] NEED MORE INFORMATION
[ ] REJECT THIS REDUCTION
```

## Open scientific questions for the researcher

1. **Formylation boundary.** Is `FMet_tRNASynthesis` part of aminoacylation or
   initiation for the reduction target? (Module assignment is itself a declared
   review decision; it was kept separate here.)
2. **Shared ATP/AMP/PPi ledger.** Should aminoacylation reductions be validated
   *in-coupling* with energy regeneration (so chemostat guards on ATP/CP apply),
   or as an isolated subsystem with the nucleotides as slow boundary pools?
3. **Cumulative-resource tolerance (T-E).** What relative error in cumulative
   ATP→AMP→PPi conversion and total charging events is acceptable, given the
   project's resource-accounting contract?
4. **QSSA intent.** Do we attempt a genuine algebraic manifold derivation (A3),
   or explicitly mark aminoacylation microstates as always-explicit?
5. **Occupancy non-negligibility.** GlyAMP reaching ~24 µM contradicts the
   "complexes/intermediates are negligible" premise — confirm whether this is a
   real feature of the author parameters or a data artifact before any lumping.
