# PNAS 2017 — Human reduction review package (Phase 7)

Organised **by biochemical process**, not by the 968 reaction numbers. For each
process: the chemistry, the implementing reactions, the intermediates, the small
molecules moved, whether particle number changes, whether it matters to the
energy ledger, candidate lumpings, **exactly what each lumping loses**, and a
decision box. **No box is pre-checked — these decisions are the researcher's.**

Legend for boxes: `[ ] KEEP` · `[ ] LUMP` · `[ ] QSSA` · `[ ] CHEMOSTAT` ·
`[ ] DROP` · `[ ] NEED MORE INFORMATION`.

Per-reaction evidence (ids, free-carrier nets, particle deltas) is in
`reduction_decisions.csv`; grep `subsystem_files` or `reverse_partner_id`.

Per-species evidence (which moiety a state carries, which pool it is a candidate
member of, and the three remaining species-level resolution decisions) is in
`species_reduction_map.md` and
`models/pnas2017_full_reference/audit/species_reduction_map.csv`. Decision groups **D1 formylation**, **D2
peptidyl-tRNA** and **D3 free RS70S** there feed sections 2, 4 and 3 below.
Deleting a species is only ever justified against that map's `n_*` moiety
columns — a reaction-level `LUMP_CANDIDATE` is not a species-deletion licence.

---

## 1. Aminoacylation (tRNA charging) — `Aminoacylation_A_*`, `Aminoacylation_B_*`

1. **Chemistry.** MetRS/GlyRS bind an amino acid + ATP → aminoacyl-adenylate
   (`MetAMP`/`GlyAMP`) + PPi; then transfer the amino acid to its tRNA →
   aminoacyl-tRNA + AMP. Two half-reactions, both irreversible overall via PPi.
2. **Implementing reactions.** ~138 reactions across the aminoacylation
   subsystems; the charging pairs are the only ones changing **free ATP→AMP+PPi**.
3. **Intermediates.** enzyme•aa, `MetAMP`/`GlyAMP` (aminoacyl-adenylate),
   enzyme•aa-AMP, free aminoacyl-tRNA.
4. **Small molecules.** consumes 1 ATP; produces 1 AMP + 1 PPi per charge.
5. **Particle number.** yes — ATP→AMP+PPi splits particles; PPiase then splits
   PPi→2 Pi.
6. **Energy-ledger relevance.** **critical** — the dominant ATP sink and PPi
   source. PPi→2 Pi is the main phosphate-release channel (PO4 reaches ~8.4 mM).
7. **Candidate lumpings.** (a) collapse 2-step charging to one
   `aa + ATP + tRNA → aa-tRNA + AMP + PPi`; (b) QSSA the enzyme complexes.
8. **What each lumping loses.** (a) loses the aminoacyl-adenylate intermediate
   and the enzyme-occupancy observable, and hides that PPi is produced *before*
   transfer; (b) loses free-vs-bound enzyme split (a translation-machinery
   occupancy the model can otherwise report).
9. Decision:
```
[ ] KEEP   [ ] LUMP   [ ] QSSA   [ ] CHEMOSTAT   [ ] DROP   [ ] NEED MORE INFORMATION
```
   Key constraint: **the reduced core must still emit exactly 1 AMP + 1 PPi per
   charged tRNA** or the phosphate/charge ledger breaks.

---

## 2. fMet-tRNA formylation — `FMet_tRNASynthesis`

1. **Chemistry.** Transformylase (MTF) formylates Met-tRNA^fMet →
   fMet-tRNA^fMet (THF → THF-derived cofactor appears; `THF` species).
2. **Implementing reactions.** ~29 reactions (formylation family).
3. **Intermediates.** MTF•Met-tRNA, MTF•fMet-tRNA, cofactor states.
4. **Small molecules.** cofactor (THF) cycling; no direct ATP/GTP.
5. **Particle number.** mostly complex-forming (−1) then releasing.
6. **Energy-ledger relevance.** low for ATP/GTP, **but** it is the sole producer
   of `fMettRNAfMetCAU`, the initiation substrate.
7. **Candidate lumpings.** fold into a single `Met-tRNA → fMet-tRNA` step;
   chemostat the cofactor.
8. **Losses.** removes the transformylase-occupancy observable and the cofactor
   pool bookkeeping (relevant if osmolarity/ionic accounting later needs THF).
9.
```
[ ] KEEP   [ ] LUMP   [ ] QSSA   [ ] CHEMOSTAT   [ ] DROP   [ ] NEED MORE INFORMATION
```

---

## 3. Initiation — `Initiation_A`, `Initiation_B1/B2`, `Initiation_C`

1. **Chemistry.** IF1/IF2(GTP)/IF3 load fMet-tRNA + mRNA onto 30S, subunit join
   with 50S, GTP hydrolysis and IF release → 70S initiation complex.
2. **Implementing reactions.** ~339 reactions — the single largest block.
3. **Intermediates.** many 30S/50S/70S•IF•tRNA•mRNA complexes (the bulk of the
   73 `bound_state` species).
4. **Small molecules.** IF2 GTP→GDP+Pi; IF binding/release.
5. **Particle number.** heavily association-driven (many −1 steps reverse-paired).
6. **Energy-ledger relevance.** **yes** — one GTP per initiation (IF2).
7. **Candidate lumpings.** merge the reversible IF-on/off pairs; reduce the
   complex ladder to 1–2 effective initiation states.
8. **Losses.** collapses the **translation-machinery occupancy** observable
   (which ribosome/IF state is populated) that this model uniquely provides.
9.
```
[ ] KEEP   [ ] LUMP   [ ] QSSA   [ ] CHEMOSTAT   [ ] DROP   [ ] NEED MORE INFORMATION
```

---

## 4. Elongation cycle — `Elongation_A_*`, `Elongation_B`, `Elongation_Ca1_*`, `Elongation_Ca2_*`

1. **Chemistry.** EF-Tu•GTP delivers aminoacyl-tRNA; GTP hydrolysis + Pi;
   peptidyl transfer (peptide bond); EF-G•GTP translocation + hydrolysis;
   deacyl-tRNA release.
2. **Implementing reactions.** ~190 reactions.
3. **Intermediates.** A/P/E-site complexes, `Pept*` elongating peptides.
4. **Small molecules.** **2 GTP → 2 GDP + 2 Pi per added residue** (EF-Tu +
   EF-G); amino acid consumed into peptide.
5. **Particle number.** association + hydrolysis split → mixed.
6. **Energy-ledger relevance.** **the main GTP sink**; directly couples product
   formation to GTP consumption — central to the model's purpose.
7. **Candidate lumpings.** one effective `add-residue` reaction with fixed
   GTP:residue stoichiometry; QSSA the transient ternary complex.
8. **Losses.** loses the accuracy/proofreading and factor-competition dynamics;
   if the residue count is fixed the model can no longer answer per-codon
   occupancy or EF-Tu vs EF-G competition.
9.
```
[ ] KEEP   [ ] LUMP   [ ] QSSA   [ ] CHEMOSTAT   [ ] DROP   [ ] NEED MORE INFORMATION
```

---

## 5. Termination & ribosome recycling — `Termination_A/B/C_*`

1. **Chemistry.** RF1/RF2 recognise stop codon → peptide release; RF3•GDP→GTP
   removes RF; RRF + EF-G•GTP split 70S into 50S+30S; subunits re-enter.
2. **Implementing reactions.** ~173 reactions.
3. **Intermediates.** `termRS70S*` complexes, recycled subunits.
4. **Small molecules.** RF3 + RRF/EF-G recycling consume additional **GTP**.
5. **Particle number.** splitting (recycling raises particle count).
6. **Energy-ledger relevance.** **yes** — recycling GTP cost per round.
7. **Candidate lumpings.** fold termination+recycling into one
   "release-product + free-ribosome" step with a GTP cost.
8. **Losses.** loses free-vs-sequestered ribosome accounting; in the reference
   run ribosomes end near-exhausted, so recycling rate controls the
   **machine-occupancy** observable.
9.
```
[ ] KEEP   [ ] LUMP   [ ] QSSA   [ ] CHEMOSTAT   [ ] DROP   [ ] NEED MORE INFORMATION
```

---

## 6. Energy regeneration — `EnergyRegeneration_A/B/C/D`, `SmallMolecules`

1. **Chemistry.** CP + ADP ⇄ Cr + ATP (CK); NDP + ATP ⇄ NDP-family (NDK);
   2 ADP ⇄ ATP + AMP (MK); PPi + H₂O → 2 Pi (PPiase); FD cofactor reactions.
2. **Implementing reactions.** ~86 + 12 resource-pool reactions.
3. **Intermediates.** enzyme•substrate complexes; `GMP` etc.
4. **Small molecules.** this *is* the small-molecule engine: buffers ATP, clears
   PPi, recycles GDP→GTP.
5. **Particle number.** PPiase PPi→2 Pi **raises** particle count (osmotic impact).
6. **Energy-ledger relevance.** **definitional** — this module is *why* explicit
   resource accounting matters.
7. **Candidate lumpings.** chemostat ATP at its quasi-plateau; treat PPi→2 Pi as
   an instantaneous source.
8. **Losses.** chemostating ATP/GTP destroys the CP→Cr drawdown signal
   (CP 50 mM→42 mM, Cr→8.3 mM) that is the whole point for later osmotic/ionic
   work — **the reference run shows ATP is nearly flat *because* CP is being
   consumed**, so a flat chemostat hides a finite donor.
9.
```
[ ] KEEP   [ ] LUMP   [ ] QSSA   [ ] CHEMOSTAT   [ ] DROP   [ ] NEED MORE INFORMATION
```
   Recommendation-to-consider (not a decision): **do not chemostat the CP/Cr
   reservoir** if osmotic accounting is a downstream goal.

---

## 7. Degradation / turnover — the `_degraded` species

1. **Chemistry.** irreversible first-order removal of every macromolecule back to
   monomer/phosphate species (ribosome, tRNA, factors, mRNA, peptide).
2. **Implementing reactions.** all **388** irreversible reactions in the model.
3. **Intermediates.** `*_degraded` terminal species.
4. **Small molecules.** return PO4, bases, amino acids to pools.
5. **Particle number.** generally raises it.
6. **Energy-ledger relevance.** indirect but real (recycles P and monomers).
7. **Candidate lumpings.** single first-order `X → ∑ monomers`; or drop.
8. **Losses.** Dropping removes the *only* sink that conserves total phosphate /
   nucleotide moieties over long times, and erases the observable that
   components are being lost from the active pool (relevant for a GUV, where
   material is finite and not replenished).
9.
```
[ ] KEEP   [ ] LUMP   [ ] QSSA   [ ] CHEMOSTAT   [ ] DROP   [ ] NEED MORE INFORMATION
```
   Constraint: this class is why the default for `DROP_CANDIDATE` in
   `reduction_map.md` is **overridden to "KEEP unless a conserving sink is
   re-added."**

---

## 8. Cross-cutting decisions

```
[ ] Confirm Level-A grouping (formylation → aminoacylation vs initiation)
[ ] Decide whether reversible-pair re-combination (580→290) is adopted as a
    pure representation change before any QSSA
[ ] Fix the unit convention (µM · s) for all reduced-core rate constants
[ ] Source charge/protonation/Mg data before any ionic-strength claim
[ ] Load SI Datasets (S1–S29) to supply the timescale evidence every
    *_CANDIDATE label currently lacks
```
