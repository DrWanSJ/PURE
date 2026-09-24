# PNAS 2017 — Chemical / resource ledger

Machine-readable ledgers (Phase 5) are produced by
`scripts/build_pnas2017_ledger.py` from the SBML inventory:

- `models/pnas2017_full_reference/audit/species_properties.csv` — 241 rows, one
  per reference species, **original SBML ids preserved**.
- `models/pnas2017_full_reference/audit/reaction_balance_audit.csv` — 968 rows,
  per-reaction free-carrier / moiety / particle accounting.

This is a **ledger, not a reduction**: every species is kept. Class labels are
heuristic **candidates** derived from SBML identifiers only and carry
`HUMAN_REVIEW_REQUIRED`; they must not be treated as curated annotations.

## 1. How resource detection works

CellDesigner-style complex ids are underscore-joined, e.g.
`EFTu_GTP_GlytRNAGlyGCC`. A resource token is tracked at two levels:

- **free pool** — the species id *equals* the token (`GTP`, `ATP`, `PO4`, …);
- **in-complex moiety** — the token is one underscore component of the id.

This lets us separate "free GTP consumed" from "GTP carried inside a complex".

## 2. Species population by (candidate) molecule class

| class | count | notes |
| --- | --- | --- |
| macromolecule:tRNA | 76 | uncharged tRNA species (incl. `_degraded`) |
| complex:bound_state | 73 | ribosome/factor complexes |
| complex:aminoacyl_tRNA | 22 | charged tRNA (e.g. `GlytRNAGlyGCC`) |
| macromolecule:translation_factor | 22 | EF-Tu/EF-G/EF-Ts/IF1-3/RF1-3/RRF/MTF (incl. states) |
| macromolecule:energy_regeneration_enzyme | 9 | CK, NDK, MK, PPiase, FD (+ states) |
| small_molecule:energy_carrier | 7 | ATP/ADP/AMP/GTP/GDP/PPi/PO4 free pool |
| macromolecule:peptide_product | 7 | `Pept0002/0003` (+degraded/complex forms) |
| complex:aminoacyl_adenylate | 6 | `MetAMP`,`GlyAMP` charging intermediates |
| macromolecule:ribosomal | 5 | RS70S/RS50S/RS30S free |
| small_molecule:amino_acid | 4 | Met, Gly, fMet (+degraded) |
| macromolecule:aminoacyl_tRNA_synthetase | 4 | MetRS, GlyRS (+degraded) |
| macromolecule:mRNA | 2 | `mRNA`, `mRNA_degraded` |
| small_molecule:cofactor_nucleotide | 2 | THF, GMP |
| small_molecule:energy_regeneration | 1 | CP (creatine phosphate) |
| small_molecule:creatine | 1 | Cr |
| **total** | **241** | |

**27 species have nonzero initial concentration** (matches the paper). These
are the true "input components"; all complexes and intermediates start at 0.
`species_properties.csv` lists each one's author-export initial value.

## 3. Small-molecule / carrier inventory (the accounting backbone)

Free-pool species and their reference initial concentrations (µM, from the
authors' export): `ATP = 3750`, `GTP = 2500`, `CP = 50000` (creatine phosphate),
amino acids `Met = 300`, `Gly = 300`, plus `ADP/AMP/GDP/PPi/PO4/Cr` starting at
0. The regeneration enzymes `CK` (creatinase/creatine kinase), `NDK`,
`MK` (myokinase), `PPiase`, `FD` are present so the ATP/GTP pools are
**actively regenerated**, not a fixed reservoir — a key reason we must keep
explicit small-molecule accounting (see reduction map).

## 4. Per-reaction balance columns (`reaction_balance_audit.csv`)

For each of the 968 reactions the ledger records, per carrier
(ATP, ADP, AMP, GTP, GDP, PPi, Pi/PO4, CP, creatine):
`<carrier>_free_net`, `<carrier>_consumed_free`, `<carrier>_produced_free`,
plus `net_particle_number_change` and `subsystem_files`.

Reactions that change a **free** pool:

| carrier | # reactions changing free pool |
| --- | --- |
| GTP | 26 |
| GDP | 26 |
| Pi / PO4 | 33 |
| ATP | 18 |
| AMP | 15 |
| PPi | 14 |
| ADP | 14 |
| CP (creatine-P) | 2 |

**Net particle-number change** (Σ product stoichiometry − Σ reactant
stoichiometry, a crude osmotic-particle **proxy**): 625 reactions increase
particle count, 266 decrease, 77 neutral; range −1 … +8. This is an *ideal
dilute-solution proxy*, **not** a validated osmotic-pressure calculation — it
ignores activity coefficients, Mg²⁺ binding and the differing osmotic weight of
a macromolecular complex vs a monovalent ion.

## 5. ⚠ Charge / ionic strength — explicitly NOT computed

The SBML carries **no** `formula`, **no** charge, **no** protonation and **no**
annotation for any species. Therefore:

- `molecular_formula`, `formal_net_charge`, `charge_provenance` are written as
  **empty (null)** — not guessed;
- `protonation_convention = "unknown"`;
- `unresolved_fields` lists exactly what is missing per row.

The ionic-strength estimator
```
I = 0.5 · Σ cᵢ zᵢ²
```
is **not evaluated**, because every `zᵢ` is undefined. A quantitative ionic
strength is deferred until charge/protonation/Mg-binding information is sourced
and a convention is fixed. When it is, it will use **only** species whose
`cᵢ` and `zᵢ` are both explicitly defined.

## 6. Reconstructable vs non-reconstructable quantities (for later reduction)

Mechanically reconstructable from the ledger: total free-carrier pools,
per-reaction carrier deltas, particle-number proxy, complex occupancy
(`complex:bound_state` counts). NOT reconstructable from this SBML at all:
charge, ionic strength, validated osmotic pressure, per-nucleotide Mg state,
and the amino-acid identity beyond the two residues used in fMGG. Any reduction
that drops a species must state which of these it loses.
