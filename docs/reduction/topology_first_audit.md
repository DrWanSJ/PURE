# PNAS 2017 topology-first source audit

Status: **DESCRIPTIVE; HUMAN_REVIEW_REQUIRED**. No state, parameter, initial value, canonical SBML, prior evidence or decision table was changed. Audit parent: `775607bf9922c6878be0147bd7c64fa97e86a790`.

Canonical source is `models/pnas2017_full_reference/original/fMGG_synthesis.xml`, SHA256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`. Subsystem ZIP supplies exact reaction signatures, not kinetics. Author simulator CSVs are a separately named parameter/initial-condition overlay. All inputs and archive member hashes are in [summary.json](../../results/topology_audit/summary.json).

| Audit quantity | Count |
| --- | ---: |
| species | 241 |
| dynamic_species | 241 |
| reactions | 968 |
| sbml_zero_initial | 0 |
| sbml_zero_k | 0 |
| sbml_inactive_reactions | 0 |
| author_zero_initial | 214 |
| author_positive_initial | 27 |
| author_zero_k | 485 |
| author_nonzero_k | 483 |
| author_initial_zero_rate | 948 |
| author_nonzero_k_unreachable_reactions | 2 |
| source_subnetworks | 26 |
| exact_reverse_pairs | 290 |
| both_author_positive_reverse_pairs | 209 |
| full_strict_serial_chains | 0 |
| author_strict_serial_chains | 12 |
| degree_hubs_ge30 | 18 |
| full_branch_species | 209 |
| author_branch_species | 173 |
| full_largest_species_scc | 209 |
| author_largest_species_scc | 197 |
| bipartite_nodes | 1209 |
| bipartite_edges | 3854 |
| projected_species_edges | 1886 |
| projected_reaction_edges | 21124 |
| full_nontrivial_context_components | 10 |
| author_nontrivial_context_components | 10 |
| full_local_cyclic_regions_ge3 | 9 |
| author_local_cyclic_regions_ge3 | 14 |
| motifs | 364 |

**Literal SBML default:** every initial concentration and local `k1` is 1. There are no zero initials, zero constants or structurally unreachable reactions. These placeholder values do not identify the published experiment. **Author-CSV overlay:** 27 positive initial components, 214 zero initial species, 485 identically zero-rate directions, 483 positive-rate directions. A zero initial rate is not permanent inactivity: 948 rates initially vanish, while only 2 positive-k directions fail conservative reactant-AND reachability. No new numerical trajectory was run.

Activity proof uses multiplicative kinetic MathML and a monotone availability closure: all substrates and kinetic species must be potentially present. Zero-k inactivity is exact for that fixed parameter overlay. Unreachable positive-k reactions remain zero under the parsed mass-action ODE assumptions; reachable reactions are only potentially enabled. This graph closure is not a dynamical validation or an experimental finding.

The two author-positive but unreachable directions are `re0000000028` and `re0000000089`: release of EFTu_GDP from an inaccessible ribosome-bound precursor lacking the Gly-tRNA cargo. They remain in the source and audit, with an explicit condition-bound inactivity label. Tooling note: the author parameter CSV has 969 rows, including the compartment-size entry `default=1`; the audit checks that entry separately from the 968 kinetic constants. Bundled runtimes lacked the plotting/graph packages, so the existing Anaconda Python environment was used without installing or changing an environment.

All species have `boundaryCondition=false`, `constant=false`; dynamic means an ODE species, not independent dimension. Global parameters: 0; local parameters: 968; reversible SBML flags: 0. Opposite directed columns nevertheless give 290 exact reverse pairs. Constant stoichiometryMath is evaluated directly: `re0000000414` produces **2 PO4**, not the accessor default 1. Units, atomic formulas and charges remain insufficient for elemental/ionic claims.

Outputs: [species](../../results/topology_audit/species_table.csv), [reactions](../../results/topology_audit/reactions_table.csv), [parameters](../../results/topology_audit/parameters_table.csv), [net stoichiometric matrix](../../results/topology_audit/stoichiometric_matrix.csv). The signed matrix has 241 rows × 968 reaction columns; reactant/product roles remain separately available because net stoichiometry alone can cancel catalytic participants.
