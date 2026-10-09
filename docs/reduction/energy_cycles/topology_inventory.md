# PNAS2017 energy-cycle topology inventory

Status: `SOURCE_VERIFIED`; active-network topology is `STRUCTURE_VERIFIED`. All reduction choices remain `HUMAN_REVIEW_REQUIRED`. Source commit `60abf1e371e90f70474bc98174035726cc68f064`. No original inputs or historical decisions were changed.

The independent XML parser evaluates exact constant MathML stoichiometry and matches each combined reaction to the original subsystem ZIP by its complete reactant/product signature. It verifies annotation subsystem memberships, stoichiometry, reverse partners, author parameters and family consistency. The normalized compatibility copy has an identical full stoichiometric inventory, including `re0000000414 -> 2 PO4`.

| Unit | Original subsystem channels | Principal family channels | Reference active | Live enzyme states |
|---|---:|---:|---:|---:|
| CK | 25 | 18 (RFAM_015) | 18 | 7 |
| NDK | 25 | 18 (RFAM_016) | 17 | 7 |
| MK | 25 | 18 (RFAM_017) | 18 | 7 |
| PPiase | 12 | 8 (RFAM_018) | 8 | 4 |

The 87 subsystem channels include 25 degradation channels classified `RFAM_DEG`; 26 channels are reference-zero because the NDK catalytic reverse is additionally disabled. The stated RFAM_015–018 are principal catalytic-family labels rather than labels on every subsystem row. Total reference-active channels: 61. All 12 SmallMolecules channels are reference-zero. Source-wide reproduced counts: 241 species, 968 reactions, 26 source subsystems, 27 positive author initial components and 483 nonzero author parameters.

Level-C category count independently reproduced from reviewed annotation memberships: 23. The categories are: `DEG_sink`, `ELONG_aa_tRNA_delivery`, `ELONG_energy_coupling`, `ELONG_peptide_formation`, `ELONG_tRNA_release`, `ELONG_translocation`, `EN_binding`, `EN_byproduct_processing`, `EN_energy_transfer`, `INIT_70S_formation`, `INIT_assembly`, `INIT_energy_commitment`, `INIT_factor_release`, `INIT_tRNA_recruitment`, `RECYCLE_component_release`, `RECYCLE_disassembly`, `RS_activation`, `RS_binding`, `RS_charging`, `RS_to_INIT_formylation`, `TERM_energy_coupling`, `TERM_factor_binding`, `TERM_peptide_release`. Energy units span `EN_binding`, `EN_energy_transfer`/`EN_byproduct_processing`, and reference-disabled `DEG_sink`; categories are navigation labels rather than effective reactions.

The bipartite edge list uses species→reaction reactant edges and reaction→species product edges with exact coefficients, activity, direction, and boundary/internal roles. Structural reachability is distinct from kinetic flux. All complete reaction and source-local IDs are in `reaction_inventory.csv`; all 968 source laws and author overlays are in `results/energy_cycles_v1/source_inventory.json`.

## CK

Source: `EnergyRegeneration_A.xml`; principal family `RFAM_015`. Free boundaries: `CP`, `ADP`, `Cr`, `ATP`.

Complete live enzyme pool: `CK + CK_ADP + CK_ATP + CK_CP + CK_CP_ADP + CK_Cr + CK_Cr_ATP`; author initial total 30.0. No external author-active reaction touches this pool, so it is conserved in the full author-reference active network as well as this isolated unit.

| Enzyme state | Bound resources inferred from exact binding edges |
|---|---|
| `CK` | none (free anchor) |
| `CK_ADP` | ADP=1 |
| `CK_ATP` | ATP=1 |
| `CK_CP` | CP=1 |
| `CK_CP_ADP` | ADP=1; CP=1 |
| `CK_Cr` | Cr=1 |
| `CK_Cr_ATP` | ATP=1; Cr=1 |

Catalytic source channels: `re0000000338`, `re0000000339`. Reference-zero channels: `re0000000329`, `re0000000348`, `re0000000349`, `re0000000350`, `re0000000351`, `re0000000352`, `re0000000353`.

Directed simple-cycle counts: {"FORWARD": 4, "REVERSE": 4, "ZERO_BOUNDARY": 13}. Every enzyme-state composition follows connected association/dissociation paths from the declared free-enzyme anchor; the complete binding graph has consistent compositions, including alternative binding orders.

ADP and CP can bind in either order to CK_CP_ADP; ATP and Cr can release in either order from CK_Cr_ATP. Both catalytic conversions are active. No active independent bypass or resource-consuming futile direction exists.

## NDK

Source: `EnergyRegeneration_B.xml`; principal family `RFAM_016`. Free boundaries: `ATP`, `GDP`, `ADP`, `GTP`.

Complete live enzyme pool: `NDK + NDK_ADP + NDK_ATP + NDK_GDP + NDK_GDP_ATP + NDK_GTP + NDK_GTP_ADP`; author initial total 1.8. No external author-active reaction touches this pool, so it is conserved in the full author-reference active network as well as this isolated unit.

| Enzyme state | Bound resources inferred from exact binding edges |
|---|---|
| `NDK` | none (free anchor) |
| `NDK_ADP` | ADP=1 |
| `NDK_ATP` | ATP=1 |
| `NDK_GDP` | GDP=1 |
| `NDK_GDP_ATP` | ATP=1; GDP=1 |
| `NDK_GTP` | GTP=1 |
| `NDK_GTP_ADP` | ADP=1; GTP=1 |

Catalytic source channels: `re0000000363`, `re0000000364`. Reference-zero channels: `re0000000354`, `re0000000364`, `re0000000369`, `re0000000370`, `re0000000371`, `re0000000372`, `re0000000373`, `re0000000374`.

Directed simple-cycle counts: {"FORWARD": 4, "ZERO_BOUNDARY": 12}. Every enzyme-state composition follows connected association/dissociation paths from the declared free-enzyme anchor; the complete binding graph has consistent compositions, including alternative binding orders.

ATP/GDP binding and ADP/GTP release each branch through both orders. `re0000000364` is the exact catalytic reverse partner but has author k=0. All binding reverse directions remain present; they do not restore reverse net chemistry when the chemical reverse channel is disabled.

## MK

Source: `EnergyRegeneration_C.xml`; principal family `RFAM_017`. Free boundaries: `ATP`, `AMP`, `ADP`.

Complete live enzyme pool: `MK + MK_ADP_1 + MK_ADP_2 + MK_ADP_ADP + MK_AMP + MK_ATP + MK_ATP_AMP`; author initial total 5.6. No external author-active reaction touches this pool, so it is conserved in the full author-reference active network as well as this isolated unit.

| Enzyme state | Bound resources inferred from exact binding edges |
|---|---|
| `MK` | none (free anchor) |
| `MK_ADP_1` | ADP=1 |
| `MK_ADP_2` | ADP=1 |
| `MK_ADP_ADP` | ADP=2 |
| `MK_AMP` | AMP=1 |
| `MK_ATP` | ATP=1 |
| `MK_ATP_AMP` | AMP=1; ATP=1 |

Catalytic source channels: `re0000000388`, `re0000000389`. Reference-zero channels: `re0000000379`, `re0000000398`, `re0000000399`, `re0000000400`, `re0000000401`, `re0000000402`, `re0000000403`.

Directed simple-cycle counts: {"FORWARD": 4, "REVERSE": 4, "ZERO_BOUNDARY": 13}. Every enzyme-state composition follows connected association/dissociation paths from the declared free-enzyme anchor; the complete binding graph has consistent compositions, including alternative binding orders.

ATP/AMP binding branches; two distinct one-ADP occupancy states provide alternative product-release orders. MK_ADP_ADP carries two bound ADP molecules. Disabled degradation `re0000000401` releases only one ADP, and `re0000000400` releases ATP without its bound AMP. These exact source effects are retained and would violate the represented nucleotide ledger if activated.

## PPiase

Source: `EnergyRegeneration_D.xml`; principal family `RFAM_018`. Free boundaries: `PPi`, `PO4`.

Complete live enzyme pool: `PPiase + PPiase_PO4 + PPiase_PO4_PO4 + PPiase_PPi`; author initial total 0.16. No external author-active reaction touches this pool, so it is conserved in the full author-reference active network as well as this isolated unit.

| Enzyme state | Bound resources inferred from exact binding edges |
|---|---|
| `PPiase` | none (free anchor) |
| `PPiase_PO4` | PO4=1 |
| `PPiase_PO4_PO4` | PO4=2 |
| `PPiase_PPi` | PPi=1 |

Catalytic source channels: `re0000000407`, `re0000000408`. Reference-zero channels: `re0000000404`, `re0000000413`, `re0000000414`, `re0000000415`.

Directed simple-cycle counts: {"FORWARD": 1, "REVERSE": 1, "ZERO_BOUNDARY": 4}. Every enzyme-state composition follows connected association/dissociation paths from the declared free-enzyme anchor; the complete binding graph has consistent compositions, including alternative binding orders.

Complete pathway: PPi binding 405/406; bound conversion 407/408; first PO4 release 409/410; second PO4 release 411/412. Two distinct product-release events yield two free PO4. Contrary to a strictly irreversible conceptual shorthand, source k408=140, k410=0.059 and k412=0.26 support the complete reverse path. Degradation 414 releases two PO4 through its MathML coefficient.

## Reference-disabled SmallMolecules interfaces

| ID | Source equation | Author k |
|---|---|---:|
| `re0000000784` | ATP → ADP + PO4 | 0.0 |
| `re0000000785` | ADP → AMP + PO4 | 0.0 |
| `re0000000786` | ATP → AMP + PPi | 0.0 |
| `re0000000787` | GTP → GDP + PO4 | 0.0 |
| `re0000000788` | GDP → GMP + PO4 | 0.0 |
| `re0000000789` | GTP → GMP + PPi | 0.0 |
| `re0000000790` | ADP + PO4 → ATP | 0.0 |
| `re0000000791` | AMP + PO4 → ADP | 0.0 |
| `re0000000792` | AMP + PPi → ATP | 0.0 |
| `re0000000793` | GDP + PO4 → GTP | 0.0 |
| `re0000000794` | GMP + PO4 → GDP | 0.0 |
| `re0000000795` | GMP + PPi → GTP | 0.0 |

The extra free species GMP connects only through these disabled small-molecule channels in this scope. Activating SmallMolecules increases the combined independent boundary net rank from 4 to 6; four principal net reactions cannot then cover the chemical directions.

## Provenance and limits

Source hashes and original ZIP-member hashes are retained in the JSON and row-level inventory. Canonical combined SBML all-one initial concentrations and k values are structural inputs; execution must use the separately identified author CSV overlay. Parameter and concentration/time units remain unresolved in source metadata. No H2O, H+, Mg2+ or unrepresented chemical species is added.
