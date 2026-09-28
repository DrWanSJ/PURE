# Reaction annotation v1 — anchor → graph propagation

**Status:** graph-aware provisional annotation. v1 supersedes the v0 row table as the current reaction-level navigation method. v0 is retained only as an auditable direct-anchor seed layer.

## Method

1. Build the full reaction–species bipartite graph: **968 reaction nodes**, **241 species nodes**, **3,854 reaction-species incidences**.
2. Separate 388 terminal degradation/inactivation rows. The active graph has **580 directed reactions**.
3. Propagate only through the **170 Class II-A / II-B / III bridge species**. Class-I protected free pools and Class-C sinks stay in the accounting tables but are not graph bridges, preventing ATP/GTP/free-ribosome hub leakage.
4. Select high-confidence functional anchors. v0 high-confidence direct rows seed the graph; chemically explicit medium groups are promoted for `ELONG_energy_coupling`, `ELONG_translocation`, `ELONG_aa_tRNA_delivery`, `INIT_energy_commitment`, and `RECYCLE_component_release`. Four isolated aaRS–AMP endpoint channels are explicit `RS_activation` anchors.
5. One graph hop means `reaction → bridge intermediate → reaction`. Propagate each anchor at most **3 reaction hops**.
6. Cluster active reactions into reaction families when they share a bridge intermediate and overlap in original Level-B subsystem provenance. Exact reverse pairs are always linked. Result: **35 active reaction families** plus `RFAM_DEG`.
7. Filter propagated stages by each reaction's source Level-A module(s).
8. If multiple nearest functional basins meet, keep all contexts and mark `SHARED_JUNCTION`; do not force a primary stage.
9. Exact reverse pairs must have identical family, topology status and contexts.
10. Only rows that cannot be located by 1–3 hop propagation or a unique family context become `UNRESOLVED` and are sent to human review.

## Result

| topology status | rows |
| --- | ---: |
| `ANCHOR` | 846 |
| `PROPAGATED` | 42 |
| `FAMILY_PROPAGATED` | 4 |
| `SHARED_JUNCTION` | 76 |
| `UNRESOLVED` | **0** |

The 76 shared-junction rows are:
- 54 × `INIT_assembly;INIT_tRNA_recruitment`
- 16 × `INIT_70S_formation;INIT_assembly;INIT_tRNA_recruitment`
- 4 × `RS_binding;RS_charging`
- 2 × `ELONG_energy_coupling;RECYCLE_component_release`

## EFG/50S case

```text
re0000000327:
EFG_GDP + RS50S → RS50S_EFG_GDP

re0000000308:
RS50S_EFG_GDP → EFG_GDP + RS50S
```

The source provenance is `Elongation_B;Termination_C`. The graph places both relevant basins one reaction hop away:

```text
ELONG_energy_coupling
          ↓
EFG_GDP + RS50S ⇄ RS50S_EFG_GDP
          ↑
RECYCLE_component_release
```

Therefore both rows are `SHARED_JUNCTION`, with no forced primary Level-C stage, and share `RFAM_014`.

Current v1 has **0 graph-unresolved rows**, so no row is sent to manual disambiguation under this rule. This is a topology result only; it does not validate QSSA, fast equilibrium, lumping or kinetic accuracy.
