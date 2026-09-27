# G1-PNAS evidence report — 2026-09-27

**Gate status: BLOCKED.** The author-site combined SBML, subsystem archive and
simulation archive are frozen and audited, but the publisher article PDF,
Supporting Information and Datasets S01–S29 (especially S27 and S28) have not
been acquired. A completed author-input simulator check does not substitute
for a frozen publisher dataset comparison. No proposed scientific reduction
has been approved or implemented.

## Source and model boundary

The pre-pivot Mavelli state is frozen by annotated tag
`archive-mavelli2015-d7-20260924` at commit
`876d5adce13fbf7b833a889d7e22507b96f15aa1` (tag object
`b5693ae7c3730b8e8b1b6f01e6733a4fc72579c3`). The unchanged author-site
SBML is `models/pnas2017_full_reference/original/fMGG_synthesis.xml`, SHA-256
`dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df5`.
The source manifest also freezes `SBML_files.zip` and
`Simulate_fMGG_synthesis.zip`; see
[`sources.json`](../../references/PNAS2017_Matsuura/provenance/sources.json)
and the [missing-source record](../../references/PNAS2017_Matsuura/MISSING_SOURCES.md).

This benchmark is **mRNA-directed translation**, not a DNA-to-RNA transcription
model. The original SBML is canonical. Its separately documented numeric
stoichiometry copy is an execution compatibility artifact, and the
author-condition SBML is a further derived run input. Neither replaces the
raw source. The prospective `PURE_reduced_core` is a structural proposal only.

## Gate checklist

| G1-PNAS requirement | Evidence | Status |
| --- | --- | --- |
| 1. Authoritative source files frozen with checksums | Three official author-site files and original SBML copy have URL/date/byte/SHA-256 records. Publisher article/SI/S01–S29 are missing. | **BLOCKED** |
| 2. Reference network readable through SBML tooling | libSBML 5.21.2 parses source; RoadRunner 2.10.0 and SimBiology R2025b import it. Both raw imports misread one `2 PO4` coefficient as `1`, so raw execution is diagnostic only. Equal-coefficient derived copy is independently checked. | **PASS for structural reading; compatibility caveat** |
| 3. Species/reaction/parameter inventory | Generated `species.csv`, `reactions.csv`, `parameters.csv`, `modules.csv`, retaining original identifiers. | **PASS** |
| 4. Published counts explained or discrepancies documented | 241 species, 968 combined reactions, 26 subsystem XML files, 27 positive author-CSV initial components. 1,098 subsystem entries collapse to 968 unique reaction signatures. Original all-one SBML values differ from author run CSV. | **PASS with documented source distinction** |
| 5. Resource/small-molecule ledger available | 241-row `species_properties.csv` and 968-row `reaction_balance_audit.csv` include free carrier, amino-acid/tRNA and particle-event fields. Complex moieties/formulas/charges are unresolved. | **PARTIAL** |
| 6. All reactions mapped to modules/families | 968/968 original combined IDs mapped to 26 original files and five broad modules; 884 unique-subsystem and 84 shared-subsystem reactions; 16 process review cards. | **PASS as candidate classification** |
| 7. No AI reduction decision silently finalized | Every decision row is `PENDING`, `HUMAN_REVIEW_REQUIRED=true`; all review checkboxes remain unchecked. Source network unchanged. | **PASS** |
| 8. Candidate core documented | [`candidate_core_v0.md`](../reduction/candidate_core_v0.md) states proposed states, roughly 42–70 channels, original-family links, information loss and open assumptions. No reduced model or fit exists. | **PASS as proposal only** |
| 9. Osmotic/ionic requirements mapped to species | Reaction-level ideal-particle proxy and explicit resource classes are present. Formula, charge/protonation and Mg binding remain unavailable, so no full ionic-strength value or validated osmotic pressure is reported. | **PASS for requirements map; quantitative work BLOCKED** |
| 10. Visualization data contract drafted | [`visualization_plan.md`](../visualization/visualization_plan.md) specifies source IDs, family mapping, provenance/freshness, resources, occupancy and qualified particle/charge views. | **PASS** |

## Reference integrity check

The author CSVs supply 241 initial values (27 positive) and 968 named local
parameters. The separate execution SBML was run unchanged in scientific
stoichiometry using RoadRunner CVODE and SimBiology `ode15s` through 1000 s.
Free `Pept0003` endpoints were 5.164478733656283 and 5.164582654018584,
respectively. This is numerical agreement between two engines, without a
preregistered pass threshold. The original S28 trajectory is absent, SBML
unit metadata is insufficient, and neither result is experimental validation.
See the [reference reproduction report](reference_reproduction.md), full run
manifests and retained warnings.

## Work requiring researcher review

- Acquire and inspect publisher article/SI/S27/S28, and reconcile S27's
  published combined-SBML description with the `.xlsx` attachment listing.
- Define molecule formulas and complex composition, charge/protonation/Mg
  conventions and concentration units before asserting elemental balances,
  total carrier conservation or quantitative ionic strength.
- Review each process card and the 968 pending candidate labels; determine
  which microscopic occupancies and resource flows must remain observable.
- Establish evidence for any future lumping, QSSA, equilibrium, chemostat or
  deletion across the intended conditions; record unrecoverable quantities.
- Compare against S28 and published trajectories once frozen publisher data
  exist. The two-engine check is an integrity check only.

The gate must be rerun after these source and chemistry gaps are resolved.
