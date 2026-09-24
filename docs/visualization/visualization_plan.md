# PNAS 2017 → PURE reduced core — visualization plan (Phase 9)

**Design only.** No frontend is built here. The plan defines a **data contract**
so every view is generated from the canonical SBML ids — **never** by editing
the scientific model for presentational grouping.

## Guiding rules

- Every node/edge/series is keyed by an **original SBML id**
  (`species.csv`/`reactions.csv`) or by an id in the audit ledgers.
- Visualization groupings (module colours, families) live in the **audit
  tables**, not in the model. A view may aggregate; the model may not.
- Views must degrade honestly where data are missing (charge, osmotic pressure)
  rather than render an assumed value.

## Views

**A. Reaction-module network.** Level-A (5) + Level-B (26) module graph, edges =
shared species between modules; **not** a 968-edge hairball. Drill: module →
subsystem → reaction (`subsystem_files` column).

**B. Material flow.** Sankey per atom/moiety class: amino-acid path
(Met/Gly → aa-tRNA → peptide), nucleotide path (free ↔ complex), phosphate path
(ATP/GTP/PPi/Pi/CP). Sourced from `reaction_balance_audit.csv` moiety columns.

**C. Energy-carrier flow.** ATP/ADP/AMP, GTP/GDP, CP/Cr pools over time with
production/consumption flux arrows per reaction family. Sourced from
`*_free_net`, `*_consumed_free`, `*_produced_free`. Overlay the reference run
(`results/pnas2017_reference/.../authors_model_trajectory.csv`) as the golden
curve (ATP flat / CP drawdown).

**D. Translation-machinery occupancy.** stacked area of free vs bound
`RS70S/50S/30S`, IF/EF/RF, and charged vs uncharged tRNA — from the
`complex:bound_state` / `aminoacyl_tRNA` classes and per-species trajectories.
Only shown where the model actually resolves the state (i.e. in the full
reference, before reduction).

**E. Osmotic inventory.** current particle concentration by molecule class using
`net_particle_number_change` and species counts — labelled **ideal proxy**, with
a hard toggle refusing to present it as validated osmotic pressure.

**F. Ionic-strength inventory.** rendered **only** for species with a defined
`z`; today that set is empty, so the view shows "no charge data — not computed"
until charge/protonation/Mg info is sourced. Uses
`I = 0.5 Σ cᵢzᵢ²` strictly on defined species.

**G. Reduction drill-down.** clicking any reduced-core reaction expands to the
set of PNAS `reaction_id`s it represents. Requires the reduction map's reverse
fields.

## Data contract (schema the generators must emit)

| view | key(s) | columns consumed | source file |
| --- | --- | --- | --- |
| A | reaction_id, subsystem | `subsystem_files`,`level_A_module`,`level_B_subsystems` | audit + reduction CSVs |
| B | species_id, moiety | molecule_class, `*_free_net` | species_properties / reaction_balance_audit |
| C | carrier, time | initial/peak/final, free-net per family | reaction_balance_audit + trajectory CSV |
| D | species_id | class, bound/free flag, trajectory | species_properties + trajectory |
| E | class | `net_particle_number_change`, counts | reaction_balance_audit |
| F | species_id | `formal_net_charge`,`c` (null until defined) | species_properties |
| G | reduced_reaction_id | `reverse_partner_id`, original ids | reduction_decisions.csv |

Stable identities: SBML id is the join key everywhere. Human-readable names are
decorators only. **Grouping must be recomputable from the ledgers so that a
change of visual category never changes the science.**
