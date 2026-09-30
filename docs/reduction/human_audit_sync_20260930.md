# Human audit synchronization — 2026-09-30

**Status:** human-confirmed documentation sync.  
**Scope:** PNAS2017 species-level information retention and the boundary between already-reviewed information requirements and still-pending reaction-level reduction decisions.

## 1. What is already human reviewed

The authoritative species-level decision is
[`species_information_contract_summary.md`](species_information_contract_summary.md)
with the detailed rationale in
[`species_information_contract_detailed.md`](species_information_contract_detailed.md).

The 241 source species are already classified exactly once:

| Class | Count | Approved information-retention meaning |
| --- | ---: | --- |
| I | 42 | protected dynamic observable; trajectory must remain outputtable, although exact conservation may later reconstruct it algebraically |
| II-A | 57 | enzyme/catalytic microstate is not a protected independent trajectory; algebraic/QSSA/effective reconstruction is allowed only if enzyme occupancy and bound resource moieties remain reconstructable |
| II-B | 91 | microscopic identity may be lumped, but the declared functional occupancy/pool and relevant moieties must remain reconstructable |
| III | 22 | elongation microstate identity may be discarded; aggregate elongation flux/occupancy, peptide progress, tRNA/ribosome occupancy and resource ledgers remain protected |
| C | 29 | terminal non-feedback degradation sink may leave the main ODE, but cumulative loss accounting remains required |

This is a **human-approved information contract**, not a candidate kinetic reduction.

## 2. Figure 2D interpretation and normative rule

The researcher reaffirmed on 2026-09-30 that the Figure 2D solid/dashed distinction was the motivation for separating quantities that require protected kinetic output from microscopic states that need only aggregate/reconstructed information.

For repository decisions, the normative artifact is the explicit I / II-A / II-B / III / C classification above, not line style by itself. Future work should cite the information contract rather than infer a new retention rule from the figure.

## 3. Amino-acid activation decision already fixed at the information level

For the amino-acid activation process, the GlyRS/MetRS binding and catalytic microstates are **not required as protected independent dynamic observables**.

The process-card activation complexes

- `GlyRS_Gly_ATP`, `GlyRS_Gly`, `GlyRS_ATP`, `GlyRS_GlyAMP_PPi`, `GlyRS_GlyAMP`, `GlyRS_AMP`;
- `MetRS_Met_ATP`, `MetRS_Met`, `MetRS_ATP`, `MetRS_MetAMP_PPi`, `MetRS_MetAMP`, `MetRS_AMP`

are Class II-A in the approved information contract. `GlyAMP` and `MetAMP` are also Class II-A.

The protected/free information relevant to this process includes the Class-I trajectories and ledgers for `Gly`, `Met`, `ATP`, `AMP`, `PPi`, `GlyRS`, and `MetRS`, together with reconstructable enzyme occupancy and bound moieties.

Therefore:

- eliminating individual GlyRS/MetRS microstate trajectories is scientifically allowed in principle;
- their material/resource content may not disappear from the accounting;
- the GlyRS/MetRS active pools and relevant bound moieties must remain reconstructable;
- this decision **does not approve any particular QSSA, fast-equilibrium, lumped rate law or reaction deletion**.

The failed R3 aminoacylation QSSA pilot is consistent with this distinction: it rejects that specific kinetic elimination formulation over its tested domain; it does not reverse the prior information-retention decision and does not make the eliminated complexes new protected observables.

## 4. What is still pending human review

The empty `KEEP / LUMP / QSSA / CHEMOSTAT / DROP / NEED MORE INFORMATION` boxes in
[`human_reduction_review.md`](human_reduction_review.md) refer to **reaction/process transformation choices**, not to the already-approved 241-species information classification.

Still pending:

1. which specific reaction families are kept, lumped, eliminated or represented by effective kinetics;
2. which mathematical operation is used for each elimination;
3. the validity domain and acceptance thresholds for each reduction;
4. conservation/moiety closure, protected-output reconstruction and full-vs-reduced trajectory/flux validation;
5. final approval of any candidate as `PURE_reduced_core`.

Accordingly, it is incorrect to state that "the species/observable audit has not been done." The correct status is:

> **Species-level information retention: HUMAN-APPROVED v1. Reaction-level kinetic reduction decisions: still pending unless separately certified.**
