# `PURE_reduced_core` candidate structure v0 — unapproved

**Status:** `STRUCTURAL_PROPOSAL_ONLY`, `HUMAN_REVIEW_REQUIRED`. This is not an SBML model, fitted parameter set, QSSA derivation or validation claim. The scientific reference remains the literal 241-species/968-reaction Matsuura PNAS 2017 translation SBML. Candidate channels below refer to original reaction families through [reduction_decisions.csv](reduction_decisions.csv) and the [16 process review cards](human_reduction_review.md); no original reaction has been deleted or rewritten.

The engineering scale estimate is **about 42–70 reaction channels**, depending on how many factor/ribosome occupancy states and carrier-release steps the chemical ledger requires. If review shows that 70 are necessary to preserve ATP/GTP, Pi/PPi, charged tRNA and particle accounting, **70 is preferable to forcing 30**. No count is an acceptance gate.

## Candidate retained states

| Category | Proposed explicit states | Reason / unresolved point |
| --- | --- | --- |
| Free carrier and phosphate inventory | `ATP`, `ADP`, `AMP`, `GTP`, `GDP`, `GMP`, `PO4` (Pi), `PPi`, `CP`, `Cr` | Direct material, carrier and ideal-particle accounting. Bound carrier moieties also need a vetted composition map. |
| Amino-acid and donor inventory | `Gly`, `Met`, `fMet`, `FD`, `THF`; possibly GlyAMP/MetAMP | Sequence-specific fMGG resource use and formyl-donor accounting. Formula/charge unknown. |
| tRNA inventory | `tRNAGlyGCC`, `tRNAfMetCAU`, `GlytRNAGlyGCC`, `MettRNAfMetCAU`, `fMettRNAfMetCAU` plus a small set of bound pools | Must distinguish charging, delivery, deacylation and return. Total-pool conservation has not been proven. |
| Translation template/product | `mRNA`, `Pept0002`, `Pept0003`, peptidyl-tRNA length/stage pools | PNAS is mRNA-directed translation; no DNA or transcription species belong in the reference import. |
| Machinery occupancy | free `RS30S`, `RS50S`, `RS70S`; proposed 30S initiation, 70S pre/post-translocation, pretermination, posttermination and recycling pools | Free/occupied ribosome is an intended observable, so a single abstract `TLcat` is inadequate without review. |
| Enzyme/factor pools | GlyRS, MetRS, MTF, IF1/IF2/IF3, EF-Tu/EF-Ts/EF-G, RF1/RF2/RF3/RRF, CK/NDK/MK/PPiase, with occupancy states where needed | Pool aggregation is conditional on microscopic binding, conservation and fast-state evidence. |

The table names original SBML IDs where available. “Pool” names are **proposed new state definitions**, not IDs in the original SBML. Any future implementation must version a complete original-ID-to-new-state map and ensure each source species is accounted for exactly once or explicitly marked omitted.

## Candidate reaction families and channel scale

The equations below are **topology sketches**. An arrow does not specify an accepted rate law, thermodynamic reversibility, QSSA or actual stoichiometric implementation. Each family retains the indicated original subsystem files as its traceable source set; exact combined reaction IDs and source-local IDs are in the decision CSV. A candidate aggregate may be created only after the researcher records a reaction-level mapping and its information loss.

| Candidate family | Original Level B source files | Channel sketch with explicit chemical resources | Estimated channels |
| --- | --- | --- | ---: |
| Gly and Met activation | `Aminoacylation_A_Gly/Met.xml` | amino acid + ATP ↔ synthetase-bound activation states → aminoacyl-adenylate + PPi; retain AMP destination | 4–8 |
| tRNA charging | `Aminoacylation_B_GlyGCC/fMetCAU.xml` | aminoacyl-adenylate + specific uncharged tRNA → charged tRNA + AMP, with synthetase recycling | 4–8 |
| Initiator formylation | `FMet_tRNASynthesis.xml` | Met-tRNA + formyl donor → fMet-tRNA + donor product, MTF regenerated | 2–4 |
| Initiation machinery | `Initiation_A/B1/B2/C.xml` | 30S/mRNA/fMet-tRNA/IF assembly → 70S initiation; IF2 GTP → GDP + Pi and factor release explicitly retained | 7–11 |
| EF-Tu delivery and exchange | `Elongation_A_Gly/Met.xml` | EF-Tu GDP↔GTP exchange, charged-tRNA ternary complex, ribosome delivery, GTP→GDP+Pi | 5–9 |
| Peptide extension and EF-G translocation | `Elongation_B/Ca1/Ca2*.xml` | two sequence-specific Gly incorporation steps with peptide-length/tRNA return and EF-G GTP→GDP+Pi | 8–14 |
| Termination and ribosome recycling | `Termination_A_RF1/RF2`, `Termination_B_RF1/RF2`, `Termination_C.xml` | RF1/RF2 peptide release, RF3 recycling, RRF/EF-G 70S splitting and tRNA/mRNA return | 8–12 |
| Energy carrier regeneration | `EnergyRegeneration_A/B/C/D.xml`, `SmallMolecules.xml` | CP + ADP ↔ Cr + ATP; ATP + GDP ↔ ADP + GTP; ATP + AMP ↔ 2 ADP; PPi → 2 Pi | 4–8 |

The ranges total approximately **42–74** if all maxima are independently retained; shared events must be deduplicated, so the working target is **roughly 42–70**. A row is a family proposal, not a reaction-level license to lump every member. The 84 combined reactions with multiple source-subsystem memberships remain single events.

## Candidate omissions, reconstruction and loss

| Candidate treatment | Original examples | Reconstruction condition | Information lost if adopted |
| --- | --- | --- | --- |
| Group selected reversible synthetase-binding intermediates | `GlyRS_Gly_ATP`, `MetRS_Met_ATP`, `GlyRS_GlyAMP_PPi` | Demonstrated binding/activation time-scale separation plus explicit carrier and enzyme moiety closure | Microscopic occupancy, adenylate and PPi release timing, reverse flux. |
| Group factor nucleotide states only where a factor pool remains observable | `EFTu_GDP_EFTs`, `EFG_GDP`, `IF2_GDP` | Validated factor total and GDP/GTP/Pi reconstruction over the intended domain | Exchange delay and specific factor occupancy. |
| Group selected ribosome-bound intermediate paths | original `RS30S_*`, `elRS70S*`, `termRS70S*` families | Verified free/occupied totals, codon/peptide-state mapping and retained tRNA/guanylate cost | Path-specific residence times, binding order and microscopic ribosome states. |
| Zero-rate degradation reactions in the author fMGG condition | exact IDs labeled `DROP_CANDIDATE` in the decision CSV | Only a human-approved, fixed-reference-domain exclusion with explicit consequences and reintroduction rule | Degradation-state trajectories, nonreference-condition failure modes and possible particle changes. |

None of these omissions is approved. “Reconstructable” means a proposed algebraic or conserved-pool relation **to be derived and tested**, not a property already established. Individual microscopic fluxes, binding order, phase-specific occupancy and some small-particle changes may remain intrinsically **non-reconstructable** after lumping. Such quantities must be listed by ID in the eventual signed decision.

## Proposed fast variables and chemostats

- Possible fast-variable candidates: synthetase-substrate complexes, EF-Tu ternary-complex binding, IF/RF bound intermediates and PPiase-bound states. No QSSA or fast-equilibrium operation is applied here. A single large `k1` is not a time-scale certificate; compare Jacobian/eigenmode, flux and initial-layer evidence over the intended domain first.
- Possible chemostat candidates for **separate future boundary-condition studies**: supplied mRNA or an external resource reservoir. In this closed fMGG reference simulation, no species is chemostatted. Chemostatting CP, ATP/GTP, amino acids or tRNA would hide consumption and/or ideal-particle changes central to this project; it requires an explicit external feed/transport ledger and researcher decision.

## Material, energy and particle obligations

Every future aggregate must provide source-reaction IDs, exact net stoichiometry, explicit ATP/ADP/AMP and GTP/GDP production/consumption, Pi/PPi, CP/Cr, amino-acid incorporation, charged/uncharged tRNA and machinery-pool exchange. Candidate conserved pools to **test**, not assume, include adenylate/guanylate moieties across bound forms, total tRNA by identity, total ribosomal subunits, creatine moiety and phosphate. The existing source lacks authoritative molecular formulas and complex composition vectors, so these laws are not yet certified. Gross and net carrier flows should remain distinct; chemical free energy cannot be inferred from ATP counts alone.

An ideal osmolarity proxy may sum concentrations of a declared subset of represented particles. Every candidate aggregate must state whether its hidden binding/dissociation changes this proxy and how it would be reconstructed. A validated osmotic pressure requires additional solution data. Ionic-strength reporting remains disabled until charge, protonation, Mg-binding and concentration units are defined for an explicit subset; only then may `I_subset = 0.5 Σ c_i z_i²` be evaluated and labeled partial.

## Decisions still required from the researcher

1. Which enzyme/factor and ribosome occupancies must remain experimentally or visually observable?
2. Which intermediate pools admit a quantified fast-state or equilibrium reconstruction, and over which initial conditions and time window?
3. What exact bound-moiety vectors and protonation/Mg conventions should be used for ATP/GTP, phosphate and aminoacyl intermediates?
4. Should the two release-factor branches, specific tRNA identities or peptide-length stages ever be grouped? What information loss is acceptable?
5. Are any reference-zero degradation pathways safely absent in the intended project domain, and how would reactivation be represented?
6. Which carrier and particle accounting tolerances and independent data will be required before a future reduced model can be called validated?

Until these are answered and the [review checkboxes](human_reduction_review.md) are completed by the researcher, this document is a structural proposal only. No parameter fitting, QSSA, chemostat or deletion has been performed.
