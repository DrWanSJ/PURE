# PNAS2017 graph-aware 968-row reaction annotation v1

The final annotation layer in PR #2 now uses **anchor → graph propagation**, not row-by-row heuristic assignment.

- 968 reaction nodes / 241 species nodes / 3,854 incidence edges.
- 580 active reactions, 388 `DEG_sink` coverage rows.
- 170 bridge species used for propagation.
- 35 active reaction families + `RFAM_DEG`.
- 290 exact reverse channels.
- 846 anchors, 42 1–3-hop propagated rows, 4 family-propagated rows, 76 shared junctions.
- **0 unresolved rows; 0 human-review-required rows.**

`re0000000308/re0000000327` is explicitly resolved as a shared junction:
`ELONG_energy_coupling;RECYCLE_component_release`.

See `reaction_graph_method_v1.md`, `reaction_level_annotation_v1.csv`, and `reaction_family_summary_v1.csv`.
