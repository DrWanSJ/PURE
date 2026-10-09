# Exact energy-cycle stoichiometric reduction certificate

Status: `STRUCTURE_VERIFIED` under fixed author-reference active-channel assumptions. This certificate establishes admissible net chemistry and exact resource identities. It does not establish kinetic lumpability, QSSA, time-scale separation or scientific acceptance.

For each unit B consists of the declared free-resource boundary; I contains the entire live enzyme pool including the free enzyme. Exact rational matrices satisfy `S_I j=0`; the rank of `S_B ker(S_I)` is computed without floating-point tolerances. Nonnegative flux feasibility is independently established by directed simple-cycle enumeration: every stationary nonnegative enzyme-transition flow decomposes into those cycles.

| Unit | rank S_I | dim ker S_I | Boundary rank | Active signed net directions | Decision |
|---|---:|---:|---:|---|---|
| CK | 6 | 12 | 1 | forward and reverse | ONE_NET_DIRECTION_SUPPORTED |
| NDK | 6 | 11 | 1 | forward only | ONE_NET_DIRECTION_SUPPORTED |
| MK | 6 | 12 | 1 | forward and reverse | ONE_NET_DIRECTION_SUPPORTED |
| PPiase | 3 | 5 | 1 | forward and reverse | ONE_NET_DIRECTION_SUPPORTED |

All active simple cycles project to zero or an integer multiple of the stated net direction; there are no independent bypass directions. Zero-boundary loops include association/dissociation excursions and alternate binding-order cycles. They can occupy enzyme and exchange microscopic flux without net chemical conversion; this is not source-certified fuel-consuming hydrolysis. Rational nullspace bases, projected bases, all nonnegative directed cycle witnesses and exact conserved-pool coefficients are supplied in `stoichiometric_checks.json`.

## CK

Exact net vector: `ADP + CP -> ATP + Cr`. Active cone direction: both signs.

| Conserved represented pool | Exact nonzero species coefficients |
|---|---|
| adenylate_group | `ADP + ATP + CK_ADP + CK_ATP + CK_CP_ADP + CK_Cr_ATP` |
| creatine_group | `CK_CP + CK_CP_ADP + CK_Cr + CK_Cr_ATP + CP + Cr` |
| live_enzyme_total | `CK + CK_ADP + CK_ATP + CK_CP + CK_CP_ADP + CK_Cr + CK_Cr_ATP` |
| represented_phosphate_groups | `2*ADP + 3*ATP + 2*CK_ADP + 3*CK_ATP + CK_CP + 3*CK_CP_ADP + 3*CK_Cr_ATP + CP` |

Every listed pool has zero symbolic active residual. Their independent rank 4 equals full active left nullity 4, so they span the conserved linear pool space of this declared isolated unit. Phosphate-group coefficients use represented nucleotide identities (ATP3, ADP2, AMP1, GTP3, GDP2, CP1, PPi2, PO4 1) and do not assert complete molecular formula or ionic conservation.

One explicit forward stationary nonnegative cycle: `re0000000330` + `re0000000336` + `re0000000338` + `re0000000340` + `re0000000346` (each channel flux=1).
Reverse witness: `re0000000331` + `re0000000345` + `re0000000343` + `re0000000339` + `re0000000337`.

When disabled degradation is admitted, signed-nullspace boundary rank becomes 1. However, stationary nonnegative live-enzyme balance forces every degradation flux to zero: sum of the live-enzyme rows is minus the sum of degradation currents. Allowing degradation in a transient model depletes the catalytic pool; live+degraded enzyme count remains conserved, but a constant live enzyme total cannot be used.

## NDK

Exact net vector: `ATP + GDP -> ADP + GTP`. Active cone direction: nonnegative forward sign only.

| Conserved represented pool | Exact nonzero species coefficients |
|---|---|
| adenylate_group | `ADP + ATP + NDK_ADP + NDK_ATP + NDK_GDP_ATP + NDK_GTP_ADP` |
| guanylate_group | `GDP + GTP + NDK_GDP + NDK_GDP_ATP + NDK_GTP + NDK_GTP_ADP` |
| live_enzyme_total | `NDK + NDK_ADP + NDK_ATP + NDK_GDP + NDK_GDP_ATP + NDK_GTP + NDK_GTP_ADP` |
| represented_phosphate_groups | `2*ADP + 3*ATP + 2*GDP + 3*GTP + 2*NDK_ADP + 3*NDK_ATP + 2*NDK_GDP + 5*NDK_GDP_ATP + 3*NDK_GTP + 5*NDK_GTP_ADP` |

Every listed pool has zero symbolic active residual. Their independent rank 4 equals full active left nullity 4, so they span the conserved linear pool space of this declared isolated unit. Phosphate-group coefficients use represented nucleotide identities (ATP3, ADP2, AMP1, GTP3, GDP2, CP1, PPi2, PO4 1) and do not assert complete molecular formula or ionic conservation.

One explicit forward stationary nonnegative cycle: `re0000000355` + `re0000000361` + `re0000000363` + `re0000000365` + `re0000000367` (each channel flux=1).

When disabled degradation is admitted, signed-nullspace boundary rank becomes 1. However, stationary nonnegative live-enzyme balance forces every degradation flux to zero: sum of the live-enzyme rows is minus the sum of degradation currents. Allowing degradation in a transient model depletes the catalytic pool; live+degraded enzyme count remains conserved, but a constant live enzyme total cannot be used.

## MK

Exact net vector: `AMP + ATP -> 2 ADP`. Active cone direction: both signs.

| Conserved represented pool | Exact nonzero species coefficients |
|---|---|
| adenylate_group | `ADP + AMP + ATP + MK_ADP_1 + MK_ADP_2 + 2*MK_ADP_ADP + MK_AMP + MK_ATP + 2*MK_ATP_AMP` |
| live_enzyme_total | `MK + MK_ADP_1 + MK_ADP_2 + MK_ADP_ADP + MK_AMP + MK_ATP + MK_ATP_AMP` |
| represented_phosphate_groups | `2*ADP + AMP + 3*ATP + 2*MK_ADP_1 + 2*MK_ADP_2 + 4*MK_ADP_ADP + MK_AMP + 3*MK_ATP + 4*MK_ATP_AMP` |

Every listed pool has zero symbolic active residual. Their independent rank 3 equals full active left nullity 3, so they span the conserved linear pool space of this declared isolated unit. Phosphate-group coefficients use represented nucleotide identities (ATP3, ADP2, AMP1, GTP3, GDP2, CP1, PPi2, PO4 1) and do not assert complete molecular formula or ionic conservation.

One explicit forward stationary nonnegative cycle: `re0000000380` + `re0000000386` + `re0000000388` + `re0000000390` + `re0000000394` (each channel flux=1).
Reverse witness: `re0000000381` + `re0000000395` + `re0000000391` + `re0000000389` + `re0000000387`.

When disabled degradation is admitted, signed-nullspace boundary rank becomes 3. However, stationary nonnegative live-enzyme balance forces every degradation flux to zero: sum of the live-enzyme rows is minus the sum of degradation currents. Allowing degradation in a transient model depletes the catalytic pool; live+degraded enzyme count remains conserved, but a constant live enzyme total cannot be used.

The all-channel signed rank is three because disabled source degradation releases incomplete bound resources. `re0000000400` loses one adenylate/phosphate group (bound AMP); `re0000000401` loses one adenylate and two phosphate groups (bound ADP). Exact active conservation is valid; activating these source channels would invalidate those resource pools. No canonical correction is made.

## PPiase

Exact net vector: `PPi -> 2 PO4`. Active cone direction: both signs.

| Conserved represented pool | Exact nonzero species coefficients |
|---|---|
| live_enzyme_total | `PPiase + PPiase_PO4 + PPiase_PO4_PO4 + PPiase_PPi` |
| represented_phosphate_groups | `PO4 + 2*PPi + PPiase_PO4 + 2*PPiase_PO4_PO4 + 2*PPiase_PPi` |

Every listed pool has zero symbolic active residual. Their independent rank 2 equals full active left nullity 2, so they span the conserved linear pool space of this declared isolated unit. Phosphate-group coefficients use represented nucleotide identities (ATP3, ADP2, AMP1, GTP3, GDP2, CP1, PPi2, PO4 1) and do not assert complete molecular formula or ionic conservation.

One explicit forward stationary nonnegative cycle: `re0000000405` + `re0000000407` + `re0000000409` + `re0000000411` (each channel flux=1).
Reverse witness: `re0000000406` + `re0000000412` + `re0000000410` + `re0000000408`.

When disabled degradation is admitted, signed-nullspace boundary rank becomes 1. However, stationary nonnegative live-enzyme balance forces every degradation flux to zero: sum of the live-enzyme rows is minus the sum of degradation currents. Allowing degradation in a transient model depletes the catalytic pool; live+degraded enzyme count remains conserved, but a constant live enzyme total cannot be used.

## Dynamic versus steady identities

Let C map live enzyme states to their bound free-resource inventory, inferred from binding paths. The physical total-resource coordinates are `T=x_B+C*x_I`. Exact source algebra gives `(S_B+C*S_I)j = nu*(j_cat_forward-j_cat_reverse)` for every active channel, without internal stationarity. Binding contributes zero to this total ledger. Therefore `dx_B/dt = nu*j_cat - C*dx_I/dt`: free boundary resource dynamics differ from catalytic net conversion during accumulation or release of bound intermediates. The exact channel ledger is included in JSON. A reduced model must reconstruct C*x_I or retain a storage state if free-resource timing is a required observable.

The steady relation `S_I j=0` removes that storage derivative; it does not justify eliminating dynamic enzyme occupancy. Four net reactions give four independent chemical directions among nine retained free-resource coordinates, and 25 live enzyme occupancy coordinates constrained by four catalyst totals; they do not imply four dynamic states.

## Coupled directions and disabled interfaces

The four-cycle active internal rank is 21; coupled boundary projection rank is 4. Their shared ATP/ADP pools are represented once. Adding all 12 SmallMolecules channels raises admissible net rank to 6, so that extension requires additional net reactions. The author-reference overlay keeps those channels zero.
