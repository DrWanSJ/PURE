# PNAS translation-network visualization plan (architecture only)

> **2026-10-10 当前实现导航：** 下文保留原架构契约。已有
> [reduction_reasoning_atlas.html](reduction_reasoning_atlas.html) 已原位加入 Phase C
> 限定科研发布总览、四情景实际轨迹、源时间窗口、运行时间和持续可见的限制。
> [数据契约与输入哈希](phase_c_release_v1.json)由适配器生成；
> [正式接受](../reduction/rapid_reduction/phase_c_formal_acceptance_20261010.md)与
> [发布清单](../reduction/rapid_reduction/release_manifest_v1.json)单独记录。
> 原始反应图谱仍在 [reaction_atlas_prototype.html](../reduction/pathways/reaction_atlas_prototype.html)。
> 这些实现不代表下列渗透压、离子强度等所有设想已被实现或认证。

No large frontend is built at this stage. Views consume immutable original SBML IDs and derived, provenance-tagged annotations. A visual grouping is a display operation and cannot edit, merge or delete a scientific species/reaction.

## Proposed views

| View | Default level | Data and user action | Scientific boundary |
| --- | --- | --- | --- |
| Reaction-module network | Five broad modules → 26 source subsystem files → candidate reaction families | Show counts and cross-module shared reactions; open exact original reaction IDs on demand | Avoid a 968-edge hairball; never count 84 shared-module memberships as new combined reactions. |
| Material flow | Amino acids, tRNA/charged tRNA, adenylate and guanylate carriers, phosphate-containing species | Inspect substrate/product stoichiometry and later flux-weighted flow | A free-species delta is not a complete moiety balance until complex composition is vetted. |
| Energy-carrier flow | ATP/ADP/AMP, GTP/GDP, CP/Cr and Pi/PPi | Plot gross production/consumption and net flow when a valid simulation supplies reaction fluxes | Chemical energy/free-energy claims need a declared thermodynamic convention; show molecule flows first. |
| Translation machinery occupancy | Free versus bound 30S/50S/70S and IF/EF/RF/RRF pools | Trace named SBML states and proposed aggregation rules | Total pools and reconstruction rules require human-reviewed species membership. |
| Osmotic inventory | Concentration by reviewed molecule class | Show ideal represented-particle proxy `Σc_i` and reaction event particle delta | Explicitly label missing salts, buffer and activity corrections; no validated osmotic pressure. |
| Ionic-strength inventory | Only a reviewed subset with charge and concentration convention | Evaluate `0.5 × Σc_i z_i²` for that subset, with provenance displayed | Hide numeric output while net charge, protonation or Mg binding remain undefined; never imply full-buffer ionic strength. |
| Reduction drill-down | Candidate reduced reaction → original combined SBML reaction IDs → original 26-subsystem memberships | Inspect proposed mapping, assumptions, lost observables, evidence and `HUMAN_REVIEW_REQUIRED` status | Do not create a reduced-model edge until a scientific decision is approved and versioned. |

## Data contract

Every displayed entity must carry its **original** `sbml_species_id` or `sbml_reaction_id` (never only a display label), `source_sbml_sha256`, source URL/DOI, and a freshness result against the frozen source manifest. `source_module_file` plus `source_module_reaction_id` are many-to-many because an identical combined reaction may appear in several original subsystem diagrams. Exactly one combined reaction ID remains the scientific event key.

| Record | Required keys | Derived/status keys |
| --- | --- | --- |
| `species` | `sbml_species_id`, original name, compartment, source SHA | Candidate molecule class, formula/charge provenance, initial-condition source, `EXTRACTED`/`INFERRED`/`AMBIGUOUS`, human review state. |
| `reaction` | `sbml_reaction_id`, reactant/product maps keyed by original species IDs, parameter ID, source SHA | Level A module, Level B subsystem memberships, Level C family, mapping ambiguity, per-event free-resource and particle deltas. |
| `trajectory` | `run_id`, effective execution-SBML hash, time, original species ID, concentration and unit status | Engine, solver/settings, raw-versus-normalized compatibility status, QC and source hashes. |
| `flux` | `run_id`, original reaction ID, time, rate and unit status | Derived gross/net resource flows and bound-moiety completeness flag. |
| `reduction_mapping` | versioned candidate core ID, candidate reaction ID, array of original SBML reaction IDs | Transformation type, assumptions, unrecoverable observables, reviewer decision/date and provenance; absent until human approval. |

The current row sources are `models/pnas2017_full_reference/audit/{species,reactions,parameters,modules,species_properties,reaction_balance_audit}.csv`, `docs/reduction/reduction_decisions.csv`, and their source/provenance manifests. A consumer must refuse stale generated rows if the current frozen source SHA-256 differs from the recorded input SHA. `NULL` formula/charge fields mean unknown; the interface must show “unavailable,” not zero. The original SBML's all-one initial values are structural placeholders; reference-condition displays use the separately identified author CSV overlay and must show that provenance.

## Suggested interaction sequence

1. Open the five-module view with 968 unique combined reactions and 26 source subsystem cards. Display shared-membership and unit warnings.
2. Select a process, then inspect its original IDs, species, reaction family, resource delta and candidate reduction consequences.
3. Compare available reference trajectories only when the execution input hash, stoichiometry normalization record and solver status pass freshness checks.
4. For osmotic and ionic panels, show data-completeness badges before any plot. Currently the ionic panel is a provenance/coverage inventory with **no numeric total**.
5. After a human decision is recorded, permit drill-down from a proposed aggregate to every source reaction and the mapping version. Keep historic candidate versions visible.

This contract is a derived knowledge graph: source species and reactions are nodes, stoichiometric participation and candidate-module memberships are edges, and each edge carries extraction/inference/ambiguity status. It is a navigation layer, not source authority.
