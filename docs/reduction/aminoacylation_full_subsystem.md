# Aminoacylation — full reference subsystem

Part of the first formal reduction-validation cycle for
`PNAS2017_full_reference`. Machine-readable artefacts produced by
[`scripts/analyze_pnas2017_aminoacylation_reduction.py`](../../scripts/analyze_pnas2017_aminoacylation_reduction.py):

- [`aminoacylation_reactions.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_reactions.csv)
- [`aminoacylation_species.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_species.csv)
- [`aminoacylation_inventory.json`](../../models/pnas2017_full_reference/audit/aminoacylation_inventory.json)
- [`aminoacylation_pathway_balance.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_pathway_balance.csv)
- [`aminoacylation_reversible_pairs.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_reversible_pairs.csv)
- [`aminoacylation_reversible_pair_validation.csv`](../../models/pnas2017_full_reference/audit/aminoacylation_reversible_pair_validation.csv)

Source: `models/pnas2017_full_reference/original/fMGG_synthesis.xml`,
SHA-256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`
(matched against `data/provenance.csv`). The canonical SBML was hashed, never
parsed-and-rewritten, in this analysis.

## Selection rule

Every reaction whose `subsystem_files` carries an `Aminoacylation_*` label
(the original subsystem labels), using original reaction and species ids.

| | count |
|---|---|
| aminoacylation reactions | **138** (134 pure + 4 interface) |
| aminoacylation species | **47** |
| MetRS sub-system (A_Met 25 + B_fMetCAU 44) | 69 reaction appearances |
| GlyRS sub-system (A_Gly 25 + B_GlyGCC 44) | 69 reaction appearances |
| reactions inactive at the author reference (`k1 = 0`) | 54 |

**Excluded by project decision:** `FMet_tRNASynthesis` (29 reactions,
formylation) is kept **separate**. `FMet_tRNASynthesis` is *not* silently merged
into aminoacylation — whether it belongs to aminoacylation or initiation is a
declared, still-unresolved scientific review decision (see
`human_reduction_review.md`). The two modules share only the `MettRNAfMetCAU`
interface species, which is retained here as a boundary species and not
interpreted.

Species roles (47 total):

| role | n | species |
|---|---|---|
| free_enzyme | 2 | MetRS, GlyRS |
| enzyme_bound_complex | 28 | all `MetRS_*` / `GlyRS_*` |
| free_aminoacyl_adenylate | 2 | MetAMP, GlyAMP |
| free_amino_acid | 2 | Met, Gly |
| free_tRNA | 2 | tRNAfMetCAU, tRNAGlyGCC |
| aminoacyl_tRNA | 2 | MettRNAfMetCAU, GlytRNAGlyGCC |
| shared_nucleotide | 3 | ATP, AMP, PPi |
| degraded_sink | 6 | {MetRS,GlyRS,tRNA…,aa-tRNA…}\_degraded |

## A. MetRS charging,  B. GlyRS charging

Both synthetases instantiate the *same* detailed mechanism (an aminoacyl-tRNA
synthetase two-step pathway):

1. substrate binding — `E + ATP ⇌ E·ATP`, `E + AA ⇌ E·AA`, ternary
   `E·AA·ATP` reached by either order;
2. adenylation (isomerization) — `E·AA·ATP → E·AA-AMP·PPi`;
3. PPi release/bind — `E·AA-AMP·PPi ⇌ E·AA-AMP + PPi`;
4. tRNA binding — `E·AA-AMP (+ tRNA) ⇌ E·AA-AMP·tRNA` (and the PPi-bound variant);
5. transfer isomerization — `E·AA-AMP·tRNA ⇌ E·AMP·(AA-tRNA)`;
6. product/AMP release — `E·AMP·(AA-tRNA) → AA-tRNA + E·AMP`, `E·AMP ⇌ E + AMP`.

Free aminoacyl-adenylate `AA-AMP` also participates directly
(`AA + AMP ⇌ AA-AMP`, `E + AA-AMP ⇌ E·AA-AMP`).

## C. Shared ATP/AMP/PPi accounting

`ATP`, `AMP`, `PPi` are the only shared nucleotides inside the subsystem
(no free `ADP`/`GTP`/`Pi` appear here). Both synthetases draw on **one** free
ATP/AMP/PPi pool. Per the project chemical ledger and `human_reduction_review.md`
key constraint, any reduced form must still emit exactly **1 AMP + 1 PPi per
charged tRNA**, or the phosphate ledger breaks. `PPi` in the whole model is
produced only by aminoacylation (then cleared by PPiase elsewhere), so this
subsystem is the sole `PPi` source and cannot be lumped without keeping that.

## D. tRNA / aminoacyl-tRNA pools

Per isoacceptor: `free tRNA` ⇄ `aminoacyl-tRNA` (charging), each with a
`_degraded` sink. `tRNA` pools are **not** interchangeable with the
`peptidyl-tRNA` or ribosome pools handled in elongation.

## E. aminoacyl-adenylate intermediates

`MetAMP`, `GlyAMP` (free) plus every `E·…-AMP…` bound state. These are the
chemistry that makes the mechanism *not* a single elementary step; they are
intermediates, not endpoints.

## F. enzyme-bound states

28 complexes. These are the candidate fast/microstate variables
(se [`aminoacylation_reduction_candidates.md`](aminoacylation_reduction_candidates.md)).

## G. degradation / turnover associated with the subsystem

Six `_degraded` sinks (enzyme, tRNA, aa-tRNA per synthetase). Their formation
`k1 = 0` in the author parameter export, so they are **inactive at the reference
trajectory** — but they are the mechanism by which enzyme and tRNA moieties
leave the active pools, and any sink lump must conserve them (protocol class G).

Interface (non-pure) reactions — shared with elongation modules:
`re0000000006` (`tRNAfMetCAU → _degraded`), `re0000000031`
(`GlytRNAGlyGCC → _degraded`), `re0000000070` (`tRNAGlyGCC → _degraded`),
`re0000000258` (`MettRNAfMetCAU → _degraded`). These are aa-tRNA/tRNA turnover
that also appear in elongation subsystem files; they are reported here but are a
whole-network accounting concern, not a pure aminoacylation reaction.

## Derived net chemistry (Phase 7 — derived, not assumed)

The net reaction was obtained by **summing the true SBML stoichiometric vectors**
of the declared catalytic cycles and verifying cancellation of every
enzyme-bound intermediate. See `aminoacylation_pathway_balance.csv`.

| pathway | net (derived) | matches expected | cancelled intermediates |
|---|---|---|---|
| Gly | `Gly + ATP + tRNAGlyGCC → GlytRNAGlyGCC + AMP + PPi` | ✔ | 8 enzyme states |
| Met | `Met + ATP + tRNAfMetCAU → MettRNAfMetCAU + AMP + PPi` | ✔ | 8 enzyme states |

Per pathway: ΔATP = −1, ΔAMP = +1, ΔPPi = +1, ΔADP = ΔPi = 0, ΔAA = −1,
Δ(free tRNA) = −1, Δ(aa-tRNA) = +1, **net particle-number change = 0** (so a
one-step lumping at least does not perturb the particle-number proxy). The
cancelled intermediates are exactly the enzyme states the catalytic cycle routes
through, confirming the enzyme is regenerated.

This establishes that the *chemistry* of the aminoacylation network **is**
`AA + tRNA + ATP → aa-tRNA + AMP + PPi`. It does **not** by itself validate the
one-step *kinetics* (candidate A4) — matching net stoichiometry is a necessary,
not sufficient, condition.

## Exact forward/reverse recombination (Phase 8)

**52 structural forward/reverse pairs** were detected inside the subsystem (by
reactant/product multiset inversion, self-contained; the reaction-map
`reverse_partner_id` is consistent). For each, the reverse net vector equals the
negative of the forward net vector (**structural equivalence: all 52 true**), so
`A ⇌ B` with `v_net = v_f − v_r` is a **class-A exact representation change**.

Exactness was validated by evaluating both the original two-reaction RHS and the
recombined single-reversible RHS at **400 feasible states** per pair
(200 author-reference trajectory points + 200 arbitrary positive log-uniform
states, seed 20260925). **All 52 pairs: max relative residual = 0.0 (exact),
pass = 52/52.**

Caveat required by protocol: *a reversible pair is not at equilibrium.* The
recombination retains both `v_f` and `v_r`; it makes **no** claim that
`v_net = 0`. Separately, some reverse members have `k1 = 0` at the author
reference (e.g. `re0000000127`/`re0000000150`), so the reverse contributes
nothing *at the reference* — an inactive reverse rate, **not** an equilibrated
one. This is an exact representation check only and must not be counted as QSSA
or fast-equilibrium evidence.
