# Phase B0-1 finite multi-carrier handoff witnesses — B0-2 documentation revision

Automated B0-1 contract status: `PENDING_HUMAN_REVIEW` (retained separately from researcher decisions). Current user-supplied researcher status: `B0_2_CONDITIONALLY_ACCEPTED`; final formal signoff is pending. See [the B0-2 review record](phase_b0_b0_2_review_record.md). Phase B1 is not authorized.

Equations below are extracted from canonical SBML. Formal tokens are not concentrations. See the JSON for every before/after marking, exact token allocation, dependency and provenance fingerprint.

## FD identity from the original publication

`FD` is **10-formyltetrahydrofolate (10-甲酰四氢叶酸)**, explicitly identified in Matsuura et al. 2017, DOI [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114), inline SI Results / Model Construction / Model construction for formylation of initiator tRNA. [Original article and SI text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/) and [Dataset S21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/#d35e1396). Its source species ID and coefficients stay unchanged. This identity citation does not certify full complex composition or real kinetic behavior.

## W1

GlyRS-produced charged tRNA enters EF-Tu and the source ribosome binding interface; elongation is incomplete

Classification: `INTERFACE_ONLY`; composite identity: `HUMAN_REVIEW_REQUIRED`.

Boundary supplies (each exactly one formal token, independently justified availability: false):

- `ATP`: DECLARED_EXTERNAL_BOUNDARY; consumed at W1:E02
- `EFTu_GTP`: DECLARED_EXTERNAL_BOUNDARY; consumed at W1:E09
- `Gly`: DECLARED_EXTERNAL_BOUNDARY; consumed at W1:E01
- `GlyRS`: CATALYST_SEED; consumed at W1:E01
- `elRS70SAGGU0002_fMet`: DECLARED_EXTERNAL_BOUNDARY; consumed at W1:E10
- `tRNAGlyGCC`: DECLARED_EXTERNAL_BOUNDARY; consumed at W1:E03

One valid firing order follows. Independent branches can be reordered; the listing does not impose their chronological order.

| Event | Original directed reaction | Complete source equation | Author k | Direction | Exact inverse (not fired) |
|---|---|---|---|---|---|
| W1:E01 | re0000000126 | `Gly + GlyRS -> GlyRS_Gly` | 20 | REFERENCE_ENABLED | re0000000131 |
| W1:E02 | re0000000136 | `ATP + GlyRS_Gly -> GlyRS_Gly_ATP` | 10 | REFERENCE_ENABLED | re0000000137 |
| W1:E03 | re0000000205 | `GlyRS_Gly_ATP + tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC` | 376 | REFERENCE_ENABLED | re0000000206 |
| W1:E04 | re0000000197 | `GlyRS_Gly_ATP_tRNAGlyGCC -> GlyRS_GlyAMP_PPi_tRNAGlyGCC` | 2 | REFERENCE_ENABLED | re0000000198 |
| W1:E05 | re0000000189 | `GlyRS_GlyAMP_PPi_tRNAGlyGCC -> GlyRS_GlyAMP_tRNAGlyGCC + PPi` | 1000 | REFERENCE_ENABLED | re0000000217 |
| W1:E06 | re0000000178 | `GlyRS_GlyAMP_tRNAGlyGCC -> GlyRS_AMP_GlytRNAGlyGCC` | 22 | REFERENCE_ENABLED | re0000000179 |
| W1:E07 | re0000000182 | `GlyRS_AMP_GlytRNAGlyGCC -> GlyRS_AMP + GlytRNAGlyGCC` | 353 | REFERENCE_ENABLED | re0000000183 |
| W1:E08 | re0000000145 | `GlyRS_AMP -> AMP + GlyRS` | 1000 | REFERENCE_ENABLED | re0000000146 |
| W1:E09 | re0000000275 | `EFTu_GTP + GlytRNAGlyGCC -> EFTu_GTP_GlytRNAGlyGCC` | 1.5 | REFERENCE_ENABLED | re0000000276 |
| W1:E10 | re0000000013 | `EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | 140 | REFERENCE_ENABLED | re0000000021 |

Causal DAG edges (actual carried source species, all coefficients explicit):

- W1:E01 → W1:E02: `GlyRS_Gly` × 1.
- W1:E02 → W1:E03: `GlyRS_Gly_ATP` × 1.
- W1:E03 → W1:E04: `GlyRS_Gly_ATP_tRNAGlyGCC` × 1.
- W1:E04 → W1:E05: `GlyRS_GlyAMP_PPi_tRNAGlyGCC` × 1.
- W1:E05 → W1:E06: `GlyRS_GlyAMP_tRNAGlyGCC` × 1.
- W1:E06 → W1:E07: `GlyRS_AMP_GlytRNAGlyGCC` × 1.
- W1:E07 → W1:E08: `GlyRS_AMP` × 1.
- W1:E07 → W1:E09: `GlytRNAGlyGCC` × 1.
- W1:E09 → W1:E10: `EFTu_GTP_GlytRNAGlyGCC` × 1.

**Exact structural net (`S w`, not an effective kinetic reaction):**

```text
ATP + EFTu_GTP + Gly + elRS70SAGGU0002_fMet + tRNAGlyGCC -> AMP + PPi + elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC
```

Recovered catalysts: GlyRS.

Cancelled declared internal species: EFTu_GTP_GlytRNAGlyGCC, GlyRS_AMP, GlyRS_AMP_GlytRNAGlyGCC, GlyRS_Gly, GlyRS_GlyAMP_PPi_tRNAGlyGCC, GlyRS_GlyAMP_tRNAGlyGCC, GlyRS_Gly_ATP, GlyRS_Gly_ATP_tRNAGlyGCC, GlytRNAGlyGCC.

## W2

MetRS product and independently prepared MTF-FD converge at 0422; 0426 transforms the source complex, 0428 releases product, 0434 recovers MTF

Classification: `STRUCTURAL_HANDOFF_WITNESS`; composite identity: `HUMAN_REVIEW_REQUIRED`.

Boundary supplies (each exactly one formal token, independently justified availability: false):

- `ATP`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2:E02
- `FD`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2:E09
- `MTF`: CATALYST_SEED; consumed at W2:E09
- `Met`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2:E01
- `MetRS`: CATALYST_SEED; consumed at W2:E01
- `tRNAfMetCAU`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2:E03

One valid firing order follows. Independent branches can be reordered; the listing does not impose their chronological order.

| Event | Original directed reaction | Complete source equation | Author k | Direction | Exact inverse (not fired) |
|---|---|---|---|---|---|
| W2:E01 | re0000000151 | `Met + MetRS -> MetRS_Met` | 5 | REFERENCE_ENABLED | re0000000156 |
| W2:E02 | re0000000161 | `ATP + MetRS_Met -> MetRS_Met_ATP` | 10 | REFERENCE_ENABLED | re0000000162 |
| W2:E03 | re0000000247 | `MetRS_Met_ATP + tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | 50 | REFERENCE_ENABLED | re0000000248 |
| W2:E04 | re0000000239 | `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU` | 200 | REFERENCE_ENABLED | re0000000240 |
| W2:E05 | re0000000231 | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU + PPi` | 1000 | REFERENCE_ENABLED | re0000000260 |
| W2:E06 | re0000000220 | `MetRS_MetAMP_tRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | 13.7 | REFERENCE_ENABLED | re0000000221 |
| W2:E07 | re0000000224 | `MetRS_AMP_MettRNAfMetCAU -> MetRS_AMP + MettRNAfMetCAU` | 1.685 | REFERENCE_ENABLED | re0000000225 |
| W2:E08 | re0000000170 | `MetRS_AMP -> AMP + MetRS` | 1000 | REFERENCE_ENABLED | re0000000171 |
| W2:E09 | re0000000418 | `FD + MTF -> MTF_FD` | 74.07407407 | REFERENCE_ENABLED | re0000000419 |
| W2:E10 | re0000000422 | `MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | 2000 | REFERENCE_ENABLED | re0000000423 |
| W2:E11 | re0000000426 | `MTF_FD_MettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU` | 37.3 | REFERENCE_ENABLED | re0000000427 |
| W2:E12 | re0000000428 | `MTF_THF_fMettRNAfMetCAU -> MTF_THF + fMettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000429 |
| W2:E13 | re0000000434 | `MTF_THF -> MTF + THF` | 1000 | REFERENCE_ENABLED | re0000000435 |

Causal DAG edges (actual carried source species, all coefficients explicit):

- W2:E01 → W2:E02: `MetRS_Met` × 1.
- W2:E02 → W2:E03: `MetRS_Met_ATP` × 1.
- W2:E03 → W2:E04: `MetRS_Met_ATP_tRNAfMetCAU` × 1.
- W2:E04 → W2:E05: `MetRS_MetAMP_PPi_tRNAfMetCAU` × 1.
- W2:E05 → W2:E06: `MetRS_MetAMP_tRNAfMetCAU` × 1.
- W2:E06 → W2:E07: `MetRS_AMP_MettRNAfMetCAU` × 1.
- W2:E07 → W2:E08: `MetRS_AMP` × 1.
- W2:E09 → W2:E10: `MTF_FD` × 1.
- W2:E07 → W2:E10: `MettRNAfMetCAU` × 1.
- W2:E10 → W2:E11: `MTF_FD_MettRNAfMetCAU` × 1.
- W2:E11 → W2:E12: `MTF_THF_fMettRNAfMetCAU` × 1.
- W2:E12 → W2:E13: `MTF_THF` × 1.

**Exact structural net (`S w`, not an effective kinetic reaction):**

```text
ATP + FD + Met + tRNAfMetCAU -> AMP + PPi + THF + fMettRNAfMetCAU
```

Recovered catalysts: MetRS, MTF.

Cancelled declared internal species: MTF_FD, MTF_FD_MettRNAfMetCAU, MTF_THF, MTF_THF_fMettRNAfMetCAU, MetRS_AMP, MetRS_AMP_MettRNAfMetCAU, MetRS_Met, MetRS_MetAMP_PPi_tRNAfMetCAU, MetRS_MetAMP_tRNAfMetCAU, MetRS_Met_ATP, MetRS_Met_ATP_tRNAfMetCAU, MettRNAfMetCAU.

## W3

W2-produced formylated tRNA binds explicitly supplied IF2-GTP; ribosomal initiation is not reconstructed

Classification: `INTERFACE_ONLY`; composite identity: `HUMAN_REVIEW_REQUIRED`.

Boundary supplies (each exactly one formal token, independently justified availability: false):

- `ATP`: DECLARED_EXTERNAL_BOUNDARY; consumed at W3:E02
- `FD`: DECLARED_EXTERNAL_BOUNDARY; consumed at W3:E09
- `IF2_GTP`: DECLARED_EXTERNAL_BOUNDARY; consumed at W3:E14
- `MTF`: CATALYST_SEED; consumed at W3:E09
- `Met`: DECLARED_EXTERNAL_BOUNDARY; consumed at W3:E01
- `MetRS`: CATALYST_SEED; consumed at W3:E01
- `tRNAfMetCAU`: DECLARED_EXTERNAL_BOUNDARY; consumed at W3:E03

One valid firing order follows. Independent branches can be reordered; the listing does not impose their chronological order.

| Event | Original directed reaction | Complete source equation | Author k | Direction | Exact inverse (not fired) |
|---|---|---|---|---|---|
| W3:E01 | re0000000151 | `Met + MetRS -> MetRS_Met` | 5 | REFERENCE_ENABLED | re0000000156 |
| W3:E02 | re0000000161 | `ATP + MetRS_Met -> MetRS_Met_ATP` | 10 | REFERENCE_ENABLED | re0000000162 |
| W3:E03 | re0000000247 | `MetRS_Met_ATP + tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | 50 | REFERENCE_ENABLED | re0000000248 |
| W3:E04 | re0000000239 | `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU` | 200 | REFERENCE_ENABLED | re0000000240 |
| W3:E05 | re0000000231 | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU + PPi` | 1000 | REFERENCE_ENABLED | re0000000260 |
| W3:E06 | re0000000220 | `MetRS_MetAMP_tRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | 13.7 | REFERENCE_ENABLED | re0000000221 |
| W3:E07 | re0000000224 | `MetRS_AMP_MettRNAfMetCAU -> MetRS_AMP + MettRNAfMetCAU` | 1.685 | REFERENCE_ENABLED | re0000000225 |
| W3:E08 | re0000000170 | `MetRS_AMP -> AMP + MetRS` | 1000 | REFERENCE_ENABLED | re0000000171 |
| W3:E09 | re0000000418 | `FD + MTF -> MTF_FD` | 74.07407407 | REFERENCE_ENABLED | re0000000419 |
| W3:E10 | re0000000422 | `MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | 2000 | REFERENCE_ENABLED | re0000000423 |
| W3:E11 | re0000000426 | `MTF_FD_MettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU` | 37.3 | REFERENCE_ENABLED | re0000000427 |
| W3:E12 | re0000000428 | `MTF_THF_fMettRNAfMetCAU -> MTF_THF + fMettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000429 |
| W3:E13 | re0000000434 | `MTF_THF -> MTF + THF` | 1000 | REFERENCE_ENABLED | re0000000435 |
| W3:E14 | re0000000449 | `IF2_GTP + fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU` | 40 | REFERENCE_ENABLED | re0000000450 |

Causal DAG edges (actual carried source species, all coefficients explicit):

- W3:E01 → W3:E02: `MetRS_Met` × 1.
- W3:E02 → W3:E03: `MetRS_Met_ATP` × 1.
- W3:E03 → W3:E04: `MetRS_Met_ATP_tRNAfMetCAU` × 1.
- W3:E04 → W3:E05: `MetRS_MetAMP_PPi_tRNAfMetCAU` × 1.
- W3:E05 → W3:E06: `MetRS_MetAMP_tRNAfMetCAU` × 1.
- W3:E06 → W3:E07: `MetRS_AMP_MettRNAfMetCAU` × 1.
- W3:E07 → W3:E08: `MetRS_AMP` × 1.
- W3:E09 → W3:E10: `MTF_FD` × 1.
- W3:E07 → W3:E10: `MettRNAfMetCAU` × 1.
- W3:E10 → W3:E11: `MTF_FD_MettRNAfMetCAU` × 1.
- W3:E11 → W3:E12: `MTF_THF_fMettRNAfMetCAU` × 1.
- W3:E12 → W3:E13: `MTF_THF` × 1.
- W3:E12 → W3:E14: `fMettRNAfMetCAU` × 1.

**Exact structural net (`S w`, not an effective kinetic reaction):**

```text
ATP + FD + IF2_GTP + Met + tRNAfMetCAU -> AMP + IF2_GTP_fMettRNAfMetCAU + PPi + THF
```

Recovered catalysts: MetRS, MTF.

Cancelled declared internal species: MTF_FD, MTF_FD_MettRNAfMetCAU, MTF_THF, MTF_THF_fMettRNAfMetCAU, MetRS_AMP, MetRS_AMP_MettRNAfMetCAU, MetRS_Met, MetRS_MetAMP_PPi_tRNAfMetCAU, MetRS_MetAMP_tRNAfMetCAU, MetRS_Met_ATP, MetRS_Met_ATP_tRNAfMetCAU, MettRNAfMetCAU, fMettRNAfMetCAU.

## W2-MTF

Finite source-level MTF recovery and free product release under declared charged-tRNA supply

Classification: `COMPLETE_CATALYTIC_CYCLE`; composite identity: `HUMAN_REVIEW_REQUIRED`.

Boundary supplies (each exactly one formal token, independently justified availability: false):

- `FD`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2-MTF:E01
- `MTF`: CATALYST_SEED; consumed at W2-MTF:E01
- `MettRNAfMetCAU`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2-MTF:E02

One valid firing order follows. Independent branches can be reordered; the listing does not impose their chronological order.

| Event | Original directed reaction | Complete source equation | Author k | Direction | Exact inverse (not fired) |
|---|---|---|---|---|---|
| W2-MTF:E01 | re0000000418 | `FD + MTF -> MTF_FD` | 74.07407407 | REFERENCE_ENABLED | re0000000419 |
| W2-MTF:E02 | re0000000422 | `MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | 2000 | REFERENCE_ENABLED | re0000000423 |
| W2-MTF:E03 | re0000000426 | `MTF_FD_MettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU` | 37.3 | REFERENCE_ENABLED | re0000000427 |
| W2-MTF:E04 | re0000000428 | `MTF_THF_fMettRNAfMetCAU -> MTF_THF + fMettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000429 |
| W2-MTF:E05 | re0000000434 | `MTF_THF -> MTF + THF` | 1000 | REFERENCE_ENABLED | re0000000435 |

Causal DAG edges (actual carried source species, all coefficients explicit):

- W2-MTF:E01 → W2-MTF:E02: `MTF_FD` × 1.
- W2-MTF:E02 → W2-MTF:E03: `MTF_FD_MettRNAfMetCAU` × 1.
- W2-MTF:E03 → W2-MTF:E04: `MTF_THF_fMettRNAfMetCAU` × 1.
- W2-MTF:E04 → W2-MTF:E05: `MTF_THF` × 1.

**Exact structural net (`S w`, not an effective kinetic reaction):**

```text
FD + MettRNAfMetCAU -> THF + fMettRNAfMetCAU
```

Recovered catalysts: MTF.

Cancelled declared internal species: MTF_FD, MTF_FD_MettRNAfMetCAU, MTF_THF, MTF_THF_fMettRNAfMetCAU.

## W2-ALT

Alternative Met-tRNA-first binding order rejoins at MTF_FD_MettRNAfMetCAU; it competes with FD-first entry

Classification: `STRUCTURAL_HANDOFF_WITNESS`; composite identity: `HUMAN_REVIEW_REQUIRED`.

Boundary supplies (each exactly one formal token, independently justified availability: false):

- `ATP`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2-ALT:E02
- `FD`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2-ALT:E10
- `MTF`: CATALYST_SEED; consumed at W2-ALT:E09
- `Met`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2-ALT:E01
- `MetRS`: CATALYST_SEED; consumed at W2-ALT:E01
- `tRNAfMetCAU`: DECLARED_EXTERNAL_BOUNDARY; consumed at W2-ALT:E03

One valid firing order follows. Independent branches can be reordered; the listing does not impose their chronological order.

| Event | Original directed reaction | Complete source equation | Author k | Direction | Exact inverse (not fired) |
|---|---|---|---|---|---|
| W2-ALT:E01 | re0000000151 | `Met + MetRS -> MetRS_Met` | 5 | REFERENCE_ENABLED | re0000000156 |
| W2-ALT:E02 | re0000000161 | `ATP + MetRS_Met -> MetRS_Met_ATP` | 10 | REFERENCE_ENABLED | re0000000162 |
| W2-ALT:E03 | re0000000247 | `MetRS_Met_ATP + tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | 50 | REFERENCE_ENABLED | re0000000248 |
| W2-ALT:E04 | re0000000239 | `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU` | 200 | REFERENCE_ENABLED | re0000000240 |
| W2-ALT:E05 | re0000000231 | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU + PPi` | 1000 | REFERENCE_ENABLED | re0000000260 |
| W2-ALT:E06 | re0000000220 | `MetRS_MetAMP_tRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | 13.7 | REFERENCE_ENABLED | re0000000221 |
| W2-ALT:E07 | re0000000224 | `MetRS_AMP_MettRNAfMetCAU -> MetRS_AMP + MettRNAfMetCAU` | 1.685 | REFERENCE_ENABLED | re0000000225 |
| W2-ALT:E08 | re0000000170 | `MetRS_AMP -> AMP + MetRS` | 1000 | REFERENCE_ENABLED | re0000000171 |
| W2-ALT:E09 | re0000000420 | `MTF + MettRNAfMetCAU -> MTF_MettRNAfMetCAU` | 2000 | REFERENCE_ENABLED | re0000000421 |
| W2-ALT:E10 | re0000000424 | `FD + MTF_MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | 74.07407407 | REFERENCE_ENABLED | re0000000425 |
| W2-ALT:E11 | re0000000426 | `MTF_FD_MettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU` | 37.3 | REFERENCE_ENABLED | re0000000427 |
| W2-ALT:E12 | re0000000428 | `MTF_THF_fMettRNAfMetCAU -> MTF_THF + fMettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000429 |
| W2-ALT:E13 | re0000000434 | `MTF_THF -> MTF + THF` | 1000 | REFERENCE_ENABLED | re0000000435 |

Causal DAG edges (actual carried source species, all coefficients explicit):

- W2-ALT:E01 → W2-ALT:E02: `MetRS_Met` × 1.
- W2-ALT:E02 → W2-ALT:E03: `MetRS_Met_ATP` × 1.
- W2-ALT:E03 → W2-ALT:E04: `MetRS_Met_ATP_tRNAfMetCAU` × 1.
- W2-ALT:E04 → W2-ALT:E05: `MetRS_MetAMP_PPi_tRNAfMetCAU` × 1.
- W2-ALT:E05 → W2-ALT:E06: `MetRS_MetAMP_tRNAfMetCAU` × 1.
- W2-ALT:E06 → W2-ALT:E07: `MetRS_AMP_MettRNAfMetCAU` × 1.
- W2-ALT:E07 → W2-ALT:E08: `MetRS_AMP` × 1.
- W2-ALT:E07 → W2-ALT:E09: `MettRNAfMetCAU` × 1.
- W2-ALT:E09 → W2-ALT:E10: `MTF_MettRNAfMetCAU` × 1.
- W2-ALT:E10 → W2-ALT:E11: `MTF_FD_MettRNAfMetCAU` × 1.
- W2-ALT:E11 → W2-ALT:E12: `MTF_THF_fMettRNAfMetCAU` × 1.
- W2-ALT:E12 → W2-ALT:E13: `MTF_THF` × 1.

**Exact structural net (`S w`, not an effective kinetic reaction):**

```text
ATP + FD + Met + tRNAfMetCAU -> AMP + PPi + THF + fMettRNAfMetCAU
```

Recovered catalysts: MetRS, MTF.

Cancelled declared internal species: MTF_FD_MettRNAfMetCAU, MTF_MettRNAfMetCAU, MTF_THF, MTF_THF_fMettRNAfMetCAU, MetRS_AMP, MetRS_AMP_MettRNAfMetCAU, MetRS_Met, MetRS_MetAMP_PPi_tRNAfMetCAU, MetRS_MetAMP_tRNAfMetCAU, MetRS_Met_ATP, MetRS_Met_ATP_tRNAfMetCAU, MettRNAfMetCAU.

## Branches, alternatives and scientific boundaries

W2: 0418 has no dependency on MetRS. 0224-produced MettRNAfMetCAU and 0418-produced MTF_FD converge at 0422. MetRS recovery at 0170 is a separate successor of 0224. Product release 0428 and MTF recovery 0434 are distinct events. W3 reuses the W2 occurrences once and adds 0449; no card reference creates another chemical event.

W2-ALT replaces 0418/0422 with 0420/0424. Both entries produce the exact source species MTF_FD_MettRNAfMetCAU. They are mutually exclusive alternatives for one MTF seed, not consecutive steps. 0421/0423 are exact reverse outlets; 0427 is an original reference-disabled inverse of 0426. The appendix includes all source exits/entrances at the selected local enzyme/charged-tRNA states, including sinks; none is silently fired.

W1 requires externally supplied EFTu_GTP and elRS70SAGGU0002_fMet. Their upstream formation remains unresolved; the endpoint is ribosome-bound and does not finish elongation. W3 requires IF2_GTP, stops before ribosomal initiation and does not recover IF2. Optional 0445 is inspected below and is excluded from all core occurrence counts.

`FD` and `THF` retain their source IDs. FD's biochemical identity is documented above from the original publication. Full complex composition and nucleotide content embedded in complexes remain INFERRED; ATP/GTP and other shared resources do not certify a carrier history. No flux, preferred binding order, kinetic feasibility, QSSA, timescale separation or reduced model is approved.

## IF2 directionality and shared Met-tRNA competition

Both original IF2 binding directions are reference-enabled; W3 fires only 0449. Preserve 0450 as an available inverse and do not infer irreversibility or equilibrium from reference parameter values.

- `re0000000449`: `IF2_GTP + fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU`; reference k1 = 40 (REFERENCE_ENABLED).
- `re0000000450`: `IF2_GTP_fMettRNAfMetCAU -> IF2_GTP + fMettRNAfMetCAU`; reference k1 = 40 (REFERENCE_ENABLED).

MTF entry (0420/0422) and EF-Tu entry (0288) consume the same original MettRNAfMetCAU pool. Any later B1 must preserve these competing exits and must not supply separate copies to isolated modules or simply add their nets. B1 implementation remains unauthorized. The [B0-2 review record](phase_b0_b0_2_review_record.md) cites the 2026 EF-Tu study as external supporting context, with publisher-abstract-only coverage explicitly stated.

| Competing original ID | Complete source equation | Reference k1 |
|---|---|---|
| re0000000420 | `MTF + MettRNAfMetCAU -> MTF_MettRNAfMetCAU` | 2000 |
| re0000000422 | `MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | 2000 |
| re0000000288 | `EFTu_GTP + MettRNAfMetCAU -> EFTu_GTP_MettRNAfMetCAU` | 1.5 |

## Source incidence appendix (context only, excluded from witness sums)

| Original ID | Complete equation | Author k | Direction | Inverse |
|---|---|---|---|---|
| re0000000005 | `fMettRNAfMetCAU -> fMettRNAfMetCAU_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000009 | `elRS70SAGGU0002_fMettRNAfMetCAU -> RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000010 | `elRS70SAGGU0002_fMettRNAfMetCAU -> RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000013 | `EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | 140 | REFERENCE_ENABLED | re0000000021 |
| re0000000021 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet` | 0.23 | REFERENCE_ENABLED | re0000000013 |
| re0000000026 | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> GlytRNAGlyGCC + elRS70SAGGU0002_fMet_EFTu_GDP` | 0 | REFERENCE_DISABLED | re0000000063 |
| re0000000027 | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> GlytRNAGlyGCC + elRS70SAGGU0002_fMet` | 0 | REFERENCE_DISABLED | re0000000064 |
| re0000000031 | `GlytRNAGlyGCC -> GlytRNAGlyGCC_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000033 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + RS30S + RS50S_degraded + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000034 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + RS30S_degraded + RS50S + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000035 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu_degraded + GTP + GlytRNAGlyGCC + RS30S + RS50S + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000036 | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + RS30S + RS50S_degraded + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000037 | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + RS30S_degraded + RS50S + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000038 | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + PO4 + RS30S + RS50S + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000039 | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + RS30S + RS50S_degraded + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000040 | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + RS30S_degraded + RS50S + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000041 | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + RS30S + RS50S + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000045 | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> GlytRNAGlyGCC + RS30S + RS50S_degraded + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000046 | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> GlytRNAGlyGCC + RS30S_degraded + RS50S + fMet + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000063 | `GlytRNAGlyGCC + elRS70SAGGU0002_fMet_EFTu_GDP -> elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000026 |
| re0000000064 | `GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000027 |
| re0000000074 | `EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002 -> elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` | 140 | REFERENCE_ENABLED | re0000000082 |
| re0000000082 | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002` | 0.23 | REFERENCE_ENABLED | re0000000074 |
| re0000000087 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002_EFTu_GDP` | 0 | REFERENCE_DISABLED | re0000000121 |
| re0000000088 | `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002` | 0 | REFERENCE_DISABLED | re0000000122 |
| re0000000091 | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S_degraded + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000092 | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + Pept0002 + RS30S_degraded + RS50S + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000093 | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu_degraded + GTP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000094 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + Pept0002 + RS30S + RS50S_degraded + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000095 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + Pept0002 + RS30S_degraded + RS50S + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000096 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + PO4 + Pept0002 + RS30S + RS50S + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000097 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S_degraded + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000098 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + Pept0002 + RS30S_degraded + RS50S + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000099 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000103 | `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> GlytRNAGlyGCC + Pept0002 + RS30S + RS50S_degraded + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000104 | `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> GlytRNAGlyGCC + Pept0002 + RS30S_degraded + RS50S + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000121 | `GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002_EFTu_GDP -> elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000087 |
| re0000000122 | `GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002 -> elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000088 |
| re0000000126 | `Gly + GlyRS -> GlyRS_Gly` | 20 | REFERENCE_ENABLED | re0000000131 |
| re0000000128 | `GlyRS -> GlyRS_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000129 | `GlyRS_Gly_ATP -> ATP + Gly + GlyRS_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000131 | `GlyRS_Gly -> Gly + GlyRS` | 470 | REFERENCE_ENABLED | re0000000126 |
| re0000000132 | `ATP + GlyRS -> GlyRS_ATP` | 10 | REFERENCE_ENABLED | re0000000133 |
| re0000000133 | `GlyRS_ATP -> ATP + GlyRS` | 8900 | REFERENCE_ENABLED | re0000000132 |
| re0000000134 | `Gly + GlyRS_ATP -> GlyRS_Gly_ATP` | 0.024 | REFERENCE_ENABLED | re0000000135 |
| re0000000135 | `GlyRS_Gly_ATP -> Gly + GlyRS_ATP` | 3.2 | REFERENCE_ENABLED | re0000000134 |
| re0000000136 | `ATP + GlyRS_Gly -> GlyRS_Gly_ATP` | 10 | REFERENCE_ENABLED | re0000000137 |
| re0000000137 | `GlyRS_Gly_ATP -> ATP + GlyRS_Gly` | 4500 | REFERENCE_ENABLED | re0000000136 |
| re0000000139 | `GlyRS_Gly -> Gly + GlyRS_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000140 | `GlyRS_Gly_ATP -> GlyRS_GlyAMP_PPi` | 29 | REFERENCE_ENABLED | re0000000141 |
| re0000000141 | `GlyRS_GlyAMP_PPi -> GlyRS_Gly_ATP` | 47 | REFERENCE_ENABLED | re0000000140 |
| re0000000144 | `GlyRS_AMP -> AMP + GlyRS_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000145 | `GlyRS_AMP -> AMP + GlyRS` | 1000 | REFERENCE_ENABLED | re0000000146 |
| re0000000146 | `AMP + GlyRS -> GlyRS_AMP` | 0 | REFERENCE_DISABLED | re0000000145 |
| re0000000147 | `GlyRS_GlyAMP -> GlyAMP + GlyRS` | 0.07 | REFERENCE_ENABLED | re0000000148 |
| re0000000148 | `GlyAMP + GlyRS -> GlyRS_GlyAMP` | 2.4 | REFERENCE_ENABLED | re0000000147 |
| re0000000151 | `Met + MetRS -> MetRS_Met` | 5 | REFERENCE_ENABLED | re0000000156 |
| re0000000153 | `MetRS -> MetRS_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000154 | `MetRS_Met_ATP -> ATP + Met + MetRS_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000156 | `MetRS_Met -> Met + MetRS` | 350 | REFERENCE_ENABLED | re0000000151 |
| re0000000157 | `ATP + MetRS -> MetRS_ATP` | 10 | REFERENCE_ENABLED | re0000000158 |
| re0000000158 | `MetRS_ATP -> ATP + MetRS` | 2500 | REFERENCE_ENABLED | re0000000157 |
| re0000000159 | `Met + MetRS_ATP -> MetRS_Met_ATP` | 5 | REFERENCE_ENABLED | re0000000160 |
| re0000000160 | `MetRS_Met_ATP -> Met + MetRS_ATP` | 350 | REFERENCE_ENABLED | re0000000159 |
| re0000000161 | `ATP + MetRS_Met -> MetRS_Met_ATP` | 10 | REFERENCE_ENABLED | re0000000162 |
| re0000000162 | `MetRS_Met_ATP -> ATP + MetRS_Met` | 2500 | REFERENCE_ENABLED | re0000000161 |
| re0000000164 | `MetRS_Met -> Met + MetRS_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000165 | `MetRS_Met_ATP -> MetRS_MetAMP_PPi` | 60 | REFERENCE_ENABLED | re0000000166 |
| re0000000166 | `MetRS_MetAMP_PPi -> MetRS_Met_ATP` | 150 | REFERENCE_ENABLED | re0000000165 |
| re0000000169 | `MetRS_AMP -> AMP + MetRS_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000170 | `MetRS_AMP -> AMP + MetRS` | 1000 | REFERENCE_ENABLED | re0000000171 |
| re0000000171 | `AMP + MetRS -> MetRS_AMP` | 0 | REFERENCE_DISABLED | re0000000170 |
| re0000000172 | `MetRS_MetAMP -> MetAMP + MetRS` | 0.07 | REFERENCE_ENABLED | re0000000173 |
| re0000000173 | `MetAMP + MetRS -> MetRS_MetAMP` | 2.4 | REFERENCE_ENABLED | re0000000172 |
| re0000000176 | `GlytRNAGlyGCC -> Gly + tRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000216 |
| re0000000177 | `GlyRS_GlyAMP_tRNAGlyGCC -> GlyAMP + GlyRS_degraded + tRNAGlyGCC` | 0 | REFERENCE_DISABLED | none |
| re0000000178 | `GlyRS_GlyAMP_tRNAGlyGCC -> GlyRS_AMP_GlytRNAGlyGCC` | 22 | REFERENCE_ENABLED | re0000000179 |
| re0000000179 | `GlyRS_AMP_GlytRNAGlyGCC -> GlyRS_GlyAMP_tRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000178 |
| re0000000180 | `GlyRS_AMP_GlytRNAGlyGCC -> AMP + GlyRS_GlytRNAGlyGCC` | 1000 | REFERENCE_ENABLED | re0000000181 |
| re0000000181 | `AMP + GlyRS_GlytRNAGlyGCC -> GlyRS_AMP_GlytRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000180 |
| re0000000182 | `GlyRS_AMP_GlytRNAGlyGCC -> GlyRS_AMP + GlytRNAGlyGCC` | 353 | REFERENCE_ENABLED | re0000000183 |
| re0000000183 | `GlyRS_AMP + GlytRNAGlyGCC -> GlyRS_AMP_GlytRNAGlyGCC` | 100 | REFERENCE_ENABLED | re0000000182 |
| re0000000184 | `GlyRS_GlytRNAGlyGCC -> GlyRS + GlytRNAGlyGCC` | 353 | REFERENCE_ENABLED | re0000000185 |
| re0000000185 | `GlyRS + GlytRNAGlyGCC -> GlyRS_GlytRNAGlyGCC` | 100 | REFERENCE_ENABLED | re0000000184 |
| re0000000186 | `GlyRS_AMP_GlytRNAGlyGCC -> AMP + GlyRS_degraded + GlytRNAGlyGCC` | 0 | REFERENCE_DISABLED | none |
| re0000000187 | `GlyRS_GlytRNAGlyGCC -> GlyRS_degraded + GlytRNAGlyGCC` | 0 | REFERENCE_DISABLED | none |
| re0000000189 | `GlyRS_GlyAMP_PPi_tRNAGlyGCC -> GlyRS_GlyAMP_tRNAGlyGCC + PPi` | 1000 | REFERENCE_ENABLED | re0000000217 |
| re0000000193 | `Gly + GlyRS_ATP_tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC` | 0.024 | REFERENCE_ENABLED | re0000000194 |
| re0000000194 | `GlyRS_Gly_ATP_tRNAGlyGCC -> Gly + GlyRS_ATP_tRNAGlyGCC` | 3.2 | REFERENCE_ENABLED | re0000000193 |
| re0000000195 | `ATP + GlyRS_Gly_tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC` | 10 | REFERENCE_ENABLED | re0000000196 |
| re0000000196 | `GlyRS_Gly_ATP_tRNAGlyGCC -> ATP + GlyRS_Gly_tRNAGlyGCC` | 4500 | REFERENCE_ENABLED | re0000000195 |
| re0000000197 | `GlyRS_Gly_ATP_tRNAGlyGCC -> GlyRS_GlyAMP_PPi_tRNAGlyGCC` | 2 | REFERENCE_ENABLED | re0000000198 |
| re0000000198 | `GlyRS_GlyAMP_PPi_tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000197 |
| re0000000199 | `GlyRS + tRNAGlyGCC -> GlyRS_tRNAGlyGCC` | 376 | REFERENCE_ENABLED | re0000000201 |
| re0000000200 | `GlyRS_Gly + tRNAGlyGCC -> GlyRS_Gly_tRNAGlyGCC` | 376 | REFERENCE_ENABLED | re0000000202 |
| re0000000201 | `GlyRS_tRNAGlyGCC -> GlyRS + tRNAGlyGCC` | 100 | REFERENCE_ENABLED | re0000000199 |
| re0000000202 | `GlyRS_Gly_tRNAGlyGCC -> GlyRS_Gly + tRNAGlyGCC` | 100 | REFERENCE_ENABLED | re0000000200 |
| re0000000205 | `GlyRS_Gly_ATP + tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC` | 376 | REFERENCE_ENABLED | re0000000206 |
| re0000000206 | `GlyRS_Gly_ATP_tRNAGlyGCC -> GlyRS_Gly_ATP + tRNAGlyGCC` | 100 | REFERENCE_ENABLED | re0000000205 |
| re0000000207 | `GlyRS_GlyAMP_PPi + tRNAGlyGCC -> GlyRS_GlyAMP_PPi_tRNAGlyGCC` | 353 | REFERENCE_ENABLED | re0000000208 |
| re0000000208 | `GlyRS_GlyAMP_PPi_tRNAGlyGCC -> GlyRS_GlyAMP_PPi + tRNAGlyGCC` | 100 | REFERENCE_ENABLED | re0000000207 |
| re0000000209 | `GlyRS_GlyAMP + tRNAGlyGCC -> GlyRS_GlyAMP_tRNAGlyGCC` | 353 | REFERENCE_ENABLED | re0000000210 |
| re0000000210 | `GlyRS_GlyAMP_tRNAGlyGCC -> GlyRS_GlyAMP + tRNAGlyGCC` | 100 | REFERENCE_ENABLED | re0000000209 |
| re0000000214 | `GlyRS_Gly_ATP_tRNAGlyGCC -> ATP + Gly + GlyRS_degraded + tRNAGlyGCC` | 0 | REFERENCE_DISABLED | none |
| re0000000215 | `GlyRS_GlyAMP_PPi_tRNAGlyGCC -> GlyAMP + GlyRS_degraded + PPi + tRNAGlyGCC` | 0 | REFERENCE_DISABLED | none |
| re0000000216 | `Gly + tRNAGlyGCC -> GlytRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000176 |
| re0000000217 | `GlyRS_GlyAMP_tRNAGlyGCC + PPi -> GlyRS_GlyAMP_PPi_tRNAGlyGCC` | 0 | REFERENCE_DISABLED | re0000000189 |
| re0000000218 | `MettRNAfMetCAU -> Met + tRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000259 |
| re0000000219 | `MetRS_MetAMP_tRNAfMetCAU -> MetAMP + MetRS_degraded + tRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000220 | `MetRS_MetAMP_tRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | 13.7 | REFERENCE_ENABLED | re0000000221 |
| re0000000221 | `MetRS_AMP_MettRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000220 |
| re0000000222 | `MetRS_AMP_MettRNAfMetCAU -> AMP + MetRS_MettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000223 |
| re0000000223 | `AMP + MetRS_MettRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000222 |
| re0000000224 | `MetRS_AMP_MettRNAfMetCAU -> MetRS_AMP + MettRNAfMetCAU` | 1.685 | REFERENCE_ENABLED | re0000000225 |
| re0000000225 | `MetRS_AMP + MettRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | 5.6 | REFERENCE_ENABLED | re0000000224 |
| re0000000226 | `MetRS_MettRNAfMetCAU -> MetRS + MettRNAfMetCAU` | 1.685 | REFERENCE_ENABLED | re0000000227 |
| re0000000227 | `MetRS + MettRNAfMetCAU -> MetRS_MettRNAfMetCAU` | 5.6 | REFERENCE_ENABLED | re0000000226 |
| re0000000228 | `MetRS_AMP_MettRNAfMetCAU -> AMP + MetRS_degraded + MettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000229 | `MetRS_MettRNAfMetCAU -> MetRS_degraded + MettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000231 | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU + PPi` | 1000 | REFERENCE_ENABLED | re0000000260 |
| re0000000235 | `Met + MetRS_ATP_tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | 5 | REFERENCE_ENABLED | re0000000236 |
| re0000000236 | `MetRS_Met_ATP_tRNAfMetCAU -> Met + MetRS_ATP_tRNAfMetCAU` | 350 | REFERENCE_ENABLED | re0000000235 |
| re0000000237 | `ATP + MetRS_Met_tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | 10 | REFERENCE_ENABLED | re0000000238 |
| re0000000238 | `MetRS_Met_ATP_tRNAfMetCAU -> ATP + MetRS_Met_tRNAfMetCAU` | 2500 | REFERENCE_ENABLED | re0000000237 |
| re0000000239 | `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU` | 200 | REFERENCE_ENABLED | re0000000240 |
| re0000000240 | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000239 |
| re0000000241 | `MetRS + tRNAfMetCAU -> MetRS_tRNAfMetCAU` | 50 | REFERENCE_ENABLED | re0000000243 |
| re0000000242 | `MetRS_Met + tRNAfMetCAU -> MetRS_Met_tRNAfMetCAU` | 50 | REFERENCE_ENABLED | re0000000244 |
| re0000000243 | `MetRS_tRNAfMetCAU -> MetRS + tRNAfMetCAU` | 150 | REFERENCE_ENABLED | re0000000241 |
| re0000000244 | `MetRS_Met_tRNAfMetCAU -> MetRS_Met + tRNAfMetCAU` | 150 | REFERENCE_ENABLED | re0000000242 |
| re0000000247 | `MetRS_Met_ATP + tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | 50 | REFERENCE_ENABLED | re0000000248 |
| re0000000248 | `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_Met_ATP + tRNAfMetCAU` | 150 | REFERENCE_ENABLED | re0000000247 |
| re0000000249 | `MetRS_MetAMP_PPi + tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU` | 50 | REFERENCE_ENABLED | re0000000250 |
| re0000000250 | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_PPi + tRNAfMetCAU` | 150 | REFERENCE_ENABLED | re0000000249 |
| re0000000251 | `MetRS_MetAMP + tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU` | 50 | REFERENCE_ENABLED | re0000000252 |
| re0000000252 | `MetRS_MetAMP_tRNAfMetCAU -> MetRS_MetAMP + tRNAfMetCAU` | 150 | REFERENCE_ENABLED | re0000000251 |
| re0000000256 | `MetRS_Met_ATP_tRNAfMetCAU -> ATP + Met + MetRS_degraded + tRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000257 | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetAMP + MetRS_degraded + PPi + tRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000258 | `MettRNAfMetCAU -> MettRNAfMetCAU_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000259 | `Met + tRNAfMetCAU -> MettRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000218 |
| re0000000260 | `MetRS_MetAMP_tRNAfMetCAU + PPi -> MetRS_MetAMP_PPi_tRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000231 |
| re0000000275 | `EFTu_GTP + GlytRNAGlyGCC -> EFTu_GTP_GlytRNAGlyGCC` | 1.5 | REFERENCE_ENABLED | re0000000276 |
| re0000000276 | `EFTu_GTP_GlytRNAGlyGCC -> EFTu_GTP + GlytRNAGlyGCC` | 0.0013 | REFERENCE_ENABLED | re0000000275 |
| re0000000286 | `EFTu_GTP_GlytRNAGlyGCC -> EFTu_degraded + GTP + GlytRNAGlyGCC` | 0 | REFERENCE_DISABLED | none |
| re0000000287 | `EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000288 | `EFTu_GTP + MettRNAfMetCAU -> EFTu_GTP_MettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000289 |
| re0000000289 | `EFTu_GTP_MettRNAfMetCAU -> EFTu_GTP + MettRNAfMetCAU` | 0.0453 | REFERENCE_ENABLED | re0000000288 |
| re0000000290 | `EFTu_GTP_MettRNAfMetCAU -> EFTu_degraded + GTP + MettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000414 | `PPiase_PO4_PO4 -> 2 PO4 + PPiase_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000416 | `MTF -> MTF_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000417 | `fMettRNAfMetCAU -> fMet + tRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000443 |
| re0000000418 | `FD + MTF -> MTF_FD` | 74.07407407 | REFERENCE_ENABLED | re0000000419 |
| re0000000419 | `MTF_FD -> FD + MTF` | 1000 | REFERENCE_ENABLED | re0000000418 |
| re0000000420 | `MTF + MettRNAfMetCAU -> MTF_MettRNAfMetCAU` | 2000 | REFERENCE_ENABLED | re0000000421 |
| re0000000421 | `MTF_MettRNAfMetCAU -> MTF + MettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000420 |
| re0000000422 | `MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | 2000 | REFERENCE_ENABLED | re0000000423 |
| re0000000423 | `MTF_FD_MettRNAfMetCAU -> MTF_FD + MettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000422 |
| re0000000424 | `FD + MTF_MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | 74.07407407 | REFERENCE_ENABLED | re0000000425 |
| re0000000425 | `MTF_FD_MettRNAfMetCAU -> FD + MTF_MettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000424 |
| re0000000426 | `MTF_FD_MettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU` | 37.3 | REFERENCE_ENABLED | re0000000427 |
| re0000000427 | `MTF_THF_fMettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000426 |
| re0000000428 | `MTF_THF_fMettRNAfMetCAU -> MTF_THF + fMettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000429 |
| re0000000429 | `MTF_THF + fMettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000428 |
| re0000000430 | `MTF_THF_fMettRNAfMetCAU -> MTF_fMettRNAfMetCAU + THF` | 1000 | REFERENCE_ENABLED | re0000000431 |
| re0000000431 | `MTF_fMettRNAfMetCAU + THF -> MTF_THF_fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000430 |
| re0000000432 | `MTF_fMettRNAfMetCAU -> MTF + fMettRNAfMetCAU` | 1000 | REFERENCE_ENABLED | re0000000433 |
| re0000000433 | `MTF + fMettRNAfMetCAU -> MTF_fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000432 |
| re0000000434 | `MTF_THF -> MTF + THF` | 1000 | REFERENCE_ENABLED | re0000000435 |
| re0000000435 | `MTF + THF -> MTF_THF` | 0 | REFERENCE_DISABLED | re0000000434 |
| re0000000436 | `MTF_FD -> FD + MTF_degraded` | 0 | REFERENCE_DISABLED | none |
| re0000000437 | `MTF_MettRNAfMetCAU -> MTF_degraded + MettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000438 | `MTF_FD_MettRNAfMetCAU -> FD + MTF_degraded + MettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000439 | `MTF_THF_fMettRNAfMetCAU -> MTF_degraded + THF + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000440 | `MTF_fMettRNAfMetCAU -> MTF_degraded + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000441 | `MTF_THF -> MTF_degraded + THF` | 0 | REFERENCE_DISABLED | none |
| re0000000443 | `fMet + tRNAfMetCAU -> fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | re0000000417 |
| re0000000445 | `GTP + IF2 -> IF2_GTP` | 10 | REFERENCE_ENABLED | re0000000446 |
| re0000000446 | `IF2_GTP -> GTP + IF2` | 67 | REFERENCE_ENABLED | re0000000445 |
| re0000000449 | `IF2_GTP + fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU` | 40 | REFERENCE_ENABLED | re0000000450 |
| re0000000450 | `IF2_GTP_fMettRNAfMetCAU -> IF2_GTP + fMettRNAfMetCAU` | 40 | REFERENCE_ENABLED | re0000000449 |
| re0000000454 | `IF2_GTP_fMettRNAfMetCAU -> GTP + IF2_degraded + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000465 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF3 -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | 280 | REFERENCE_ENABLED | re0000000466 |
| re0000000466 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF3` | 1.5 | REFERENCE_ENABLED | re0000000465 |
| re0000000467 | `RS30S_IF3_IF2_GTP + fMettRNAfMetCAU -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | 5 | REFERENCE_ENABLED | re0000000468 |
| re0000000468 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF3_IF2_GTP + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000467 |
| re0000000473 | `RS30S_IF3_mRNA + fMettRNAfMetCAU -> RS30S_IF3_fMettRNAfMetCAU_mRNA` | 5 | REFERENCE_ENABLED | re0000000474 |
| re0000000474 | `RS30S_IF3_fMettRNAfMetCAU_mRNA -> RS30S_IF3_mRNA + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000473 |
| re0000000475 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF3_mRNA -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | 280 | REFERENCE_ENABLED | re0000000476 |
| re0000000476 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF3_mRNA` | 1.5 | REFERENCE_ENABLED | re0000000475 |
| re0000000479 | `RS30S_IF3_IF2_GTP_mRNA + fMettRNAfMetCAU -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | 5 | REFERENCE_ENABLED | re0000000480 |
| re0000000480 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF3_IF2_GTP_mRNA + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000479 |
| re0000000497 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3 -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | 220 | REFERENCE_ENABLED | re0000000498 |
| re0000000498 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3` | 1 | REFERENCE_ENABLED | re0000000497 |
| re0000000499 | `RS30S_IF1_IF3_IF2_GTP + fMettRNAfMetCAU -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | 5 | REFERENCE_ENABLED | re0000000500 |
| re0000000500 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF1_IF3_IF2_GTP + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000499 |
| re0000000517 | `RS30S_IF1_IF3_mRNA + fMettRNAfMetCAU -> RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` | 5 | REFERENCE_ENABLED | re0000000518 |
| re0000000518 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_mRNA + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000517 |
| re0000000519 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | 220 | REFERENCE_ENABLED | re0000000520 |
| re0000000520 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA` | 1 | REFERENCE_ENABLED | re0000000519 |
| re0000000523 | `RS30S_IF1_IF3_IF2_GTP_mRNA + fMettRNAfMetCAU -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | 5 | REFERENCE_ENABLED | re0000000524 |
| re0000000524 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_IF2_GTP_mRNA + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000523 |
| re0000000551 | `RS30S_IF3_fMettRNAfMetCAU_mRNA -> IF3_degraded + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000552 | `RS30S_IF3_fMettRNAfMetCAU_mRNA -> IF3 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000565 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2 + IF3 + RS30S_degraded + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000566 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2_degraded + IF3 + RS30S + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000567 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2 + IF3_degraded + RS30S + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000574 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3_degraded + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000575 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000576 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1_degraded + IF3 + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000577 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000578 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2_degraded + IF3 + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000579 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3_degraded + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000588 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2 + IF3_degraded + RS30S + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000589 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2_degraded + IF3 + RS30S + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000590 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1_degraded + IF2 + IF3 + RS30S + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000591 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2 + IF3 + RS30S_degraded + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000596 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3_degraded + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000597 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000598 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2_degraded + IF3 + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000599 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1_degraded + IF2 + IF3 + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000600 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000601 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000602 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000603 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000604 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000605 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000606 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000607 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1_degraded + IF2 + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000608 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000611 | `IF2_GTP_fMettRNAfMetCAU + RS30S -> RS30S_IF2_GTP_fMettRNAfMetCAU` | 280 | REFERENCE_ENABLED | re0000000612 |
| re0000000612 | `RS30S_IF2_GTP_fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU + RS30S` | 1.5 | REFERENCE_ENABLED | re0000000611 |
| re0000000613 | `RS30S_IF2_GTP + fMettRNAfMetCAU -> RS30S_IF2_GTP_fMettRNAfMetCAU` | 5 | REFERENCE_ENABLED | re0000000614 |
| re0000000614 | `RS30S_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF2_GTP + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000613 |
| re0000000621 | `RS30S_mRNA + fMettRNAfMetCAU -> RS30S_fMettRNAfMetCAU_mRNA` | 5 | REFERENCE_ENABLED | re0000000622 |
| re0000000622 | `RS30S_fMettRNAfMetCAU_mRNA -> RS30S_mRNA + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000621 |
| re0000000623 | `IF2_GTP_fMettRNAfMetCAU + RS30S_mRNA -> RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | 280 | REFERENCE_ENABLED | re0000000624 |
| re0000000624 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP_fMettRNAfMetCAU + RS30S_mRNA` | 1.5 | REFERENCE_ENABLED | re0000000623 |
| re0000000629 | `RS30S_IF2_GTP_mRNA + fMettRNAfMetCAU -> RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | 5 | REFERENCE_ENABLED | re0000000630 |
| re0000000630 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF2_GTP_mRNA + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000629 |
| re0000000645 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1 -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | 220 | REFERENCE_ENABLED | re0000000646 |
| re0000000646 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF1` | 1 | REFERENCE_ENABLED | re0000000645 |
| re0000000647 | `RS30S_IF1_IF2_GTP + fMettRNAfMetCAU -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | 5 | REFERENCE_ENABLED | re0000000648 |
| re0000000648 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF1_IF2_GTP + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000647 |
| re0000000659 | `RS30S_IF1_mRNA + fMettRNAfMetCAU -> RS30S_IF1_fMettRNAfMetCAU_mRNA` | 5 | REFERENCE_ENABLED | re0000000660 |
| re0000000660 | `RS30S_IF1_fMettRNAfMetCAU_mRNA -> RS30S_IF1_mRNA + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000659 |
| re0000000661 | `RS30S_IF1_IF2_GTP_mRNA + fMettRNAfMetCAU -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | 5 | REFERENCE_ENABLED | re0000000662 |
| re0000000662 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF2_GTP_mRNA + fMettRNAfMetCAU` | 1.5 | REFERENCE_ENABLED | re0000000661 |
| re0000000665 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_mRNA -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | 220 | REFERENCE_ENABLED | re0000000666 |
| re0000000666 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_mRNA` | 1 | REFERENCE_ENABLED | re0000000665 |
| re0000000691 | `RS30S_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2 + RS30S_degraded + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000692 | `RS30S_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2_degraded + RS30S + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000694 | `RS30S_fMettRNAfMetCAU_mRNA -> RS30S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000697 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000698 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2_degraded + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000702 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2 + RS30S_degraded + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000703 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2_degraded + RS30S + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000704 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1_degraded + IF2 + RS30S + fMettRNAfMetCAU` | 0 | REFERENCE_DISABLED | none |
| re0000000707 | `RS30S_IF1_fMettRNAfMetCAU_mRNA -> IF1 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000708 | `RS30S_IF1_fMettRNAfMetCAU_mRNA -> IF1_degraded + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000712 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000713 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2_degraded + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000714 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1_degraded + IF2 + RS30S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000727 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000728 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000729 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000730 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000731 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000732 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000733 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000734 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1_degraded + IF2 + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000735 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000736 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF2_degraded + IF3 + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000737 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3 + PO4 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000738 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3_degraded + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000739 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3 + PO4 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000740 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3 + PO4 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000741 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2_degraded + IF3 + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000742 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3 + PO4 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000743 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1_degraded + IF2 + IF3 + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000744 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3_degraded + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000767 | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000768 | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000769 | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000770 | `RS70S_IF3_fMettRNAfMetCAU_mRNA -> IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000771 | `RS70S_IF3_fMettRNAfMetCAU_mRNA -> IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000772 | `RS70S_IF3_fMettRNAfMetCAU_mRNA -> IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000773 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000774 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000775 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000776 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000777 | `RS70S_IF1_fMettRNAfMetCAU_mRNA -> IF1 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000778 | `RS70S_IF1_fMettRNAfMetCAU_mRNA -> IF1 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000779 | `RS70S_IF1_fMettRNAfMetCAU_mRNA -> IF1_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000780 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000781 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000782 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
| re0000000783 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1_degraded + IF2 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | 0 | REFERENCE_DISABLED | none |
