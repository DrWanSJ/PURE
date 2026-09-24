# PNAS 2017 — `PURE_reduced_core` candidate structure **v0** (Phase 8)

> **STATUS: STRUCTURAL PROPOSAL ONLY. NOT validated. NOT fitted. No QSSA has
> been performed to hit a reaction count.** This is the shape the reduced model
> *could* take **after** the Phase-7 human decisions. It is derived from the
> reduction map, not from ad-hoc deletion. Every item below is contingent on the
> researcher's checkboxes in `human_reduction_review.md`.

## Engineering target vs. ledger reality

Target: **roughly a few tens of reactions**. Reality check from the ledger:
preserving the required **resource accounting** (ATP/GTP/AMP/ADP/GDP/Pi/PPi,
CP/Cr, amino acids, charged/uncharged tRNA, machine occupancy, particle-number
proxy) is the binding constraint, **not** protein output. A core that keeps the
free-carrier, phosphate and tRNA moiety sums explicit realistically lands at
**~50–70 effective reactions**, not ~30, because each energy step and the PPiase
split must stay individually countable. **Stated explicitly, per the brief.**
Reaching ~30 requires dropping at least one accounting target — a human decision.

## Candidate retained states (small set, illustrative — not final)

- **Pools / resources:** `ATP, ADP, AMP, GTP, GDP, PPi, Pi(PO4), CP, Cr`
- **Substrates:** amino acids (`Met, Gly`), uncharged `tRNA`, `aa-tRNA`,
  `fMet-tRNA`
- **Machinery (aggregate):** `RS70S` free + `RS50S`/`RS30S`, key factors
  collapsed to total (`EFTu_tot, EFG_tot, IF_tot, RF_tot, RRF_tot`),
  enzymes (`MetRS, GlyRS, CK, NDK, MK, PPiase`)
- **Template & product:** `mRNA`, elongating-peptide surrogate, `fMGG` product
- **Sinks:** one aggregate `degraded` reservoir per moiety class (P, aa, base)

## Candidate reaction families → effective steps

| # | effective reaction (proposal) | PNAS reactions it represents (family) | resource emitted |
| --- | --- | --- | --- |
| 1 | aa + ATP + tRNA → aa-tRNA + AMP + PPi | Aminoacylation (138) | −1 ATP, +AMP, +PPi |
| 2 | PPi → 2 Pi | PPiase (`re0000000414` family) | +2 Pi |
| 3 | Met-tRNA → fMet-tRNA (MTF) | formylation (29) | cofactor |
| 4 | fMet-tRNA + mRNA + 30S/50S → 70S·init + GDP + Pi | initiation (339) | −1 GTP |
| 5 | aa-tRNA + 70S·pep → pep+1 + GDP + Pi + deacyl-tRNA | elongation (190) | −2 GTP, −1 aa |
| 6 | stop → product release + RF + GTP hydrolysis | termination (173) | −1–2 GTP |
| 7 | recycled subunits re-associate | recycling (in #6 set) | — |
| 8 | CP + ADP → Cr + ATP | energy regen CK | +ATP, −CP |
| 9 | 2 ADP ⇄ ATP + AMP | MK | ATP/AMP balance |
| 10 | NDP + ATP ⇄ NTP + ADP | NDK (GDP→GTP) | GTP regen |
| … | *per-moiety degradation sinks (aa/P/base)* | 388 `_degraded` reactions | returns monomers |

The 580 forward/reverse pairs collapse into reversible forms of steps 3–7
(representation change, no loss). The 388 degradation reactions collapse to
~3–6 conserving sinks **only if** total moiety conservation is preserved —
otherwise they remain ~individual.

## Omitted species (candidate — needs Phase-7 approval)

Per-residue and per-IF/EF/RF intermediate complexes (the 73 `bound_state`
species), individual aminoacyl-adenylates, separate 30S·IF subcomplexes.

## Reconstructable vs non-reconstructable

- **Reconstructable (via conservation):** factor totals, ribosome totals,
  tRNA pool, adenine/guanine nucleotide pools.
- **Reconstructable only with the fast assumption:** instantaneous complex
  occupancies (needs QSSA the human has *not* yet approved).
- **NON-reconstructable from the proposed core:** per-codon ribosome positions,
  aminoacyl-adenylate intermediate concentrations, individual factor
  distributions, free-vs-bound enzyme fractions, **any charge/ionic-strength
  quantity (never available in the SBML)**.

## Proposed fast variables / chemostats / conservation laws — ALL UNDECIDED

- **Proposed fast vars:** enzyme-substrate complexes (steps 1, 4–7). *Requires
  QSSA approval + timescale data — not yet done.*
- **Proposed chemostats:** water, and possibly a well-buffered Pi reservoir.
  *The CP/Cr donor should NOT be chemostatted* (see §6 of the review doc) if
  osmotic accounting is wanted.
- **Conservation laws to enforce:** total adenine (A+ADP+ATP+aa-AMP), total
  guanine, total phosphate (P+Pi+PPi+ATP+GTP+CP+…), total tRNA per isoacceptor,
  total ribosome, total each factor/enzyme.

## Expected material / energy accounting (must survive reduction)

Per fMGG made (3 residues): **≈ −1 ATP (fMet charge) −2 ATP/… (Gly charges)
→ AMP+PPi; ≈ −(initiation+elongation+recycling) GTP → GDP+Pi; CP consumed to
re-buffer ATP; net Pi and particle increase.** The reference run caps this at
~5.2 µM product with ATP flat and CP down ~17% — the reduced core must reproduce
that *resource* signature, not only the product curve.

## Unresolved scientific decisions (blockers to a "v1")

1. Timescale evidence for every `LUMP`/`QSSA` — needs SI Datasets parsed.
2. Whether degradation is lumped conserving or kept explicit.
3. Whether machine occupancy is a required observable (drives how far initiation/
   termination can be collapsed).
4. Unit convention + charge/protonation sourcing for ionic strength.
5. The **reaction-count floor** set by the ledger (30 vs ~50–70) — human call.

> Do **not** build, fit, or run this candidate as if validated. It becomes a real
> `PURE_reduced_core` model (SBML, canonical) only after Phase-7 sign-off.
