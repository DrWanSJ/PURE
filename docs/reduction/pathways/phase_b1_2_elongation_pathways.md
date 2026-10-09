# Phase B1-2: two Gly elongation rounds

**Scientific status: PENDING_HUMAN_REVIEW; formally accepted: false.** This is structural source reconstruction.

Source E2 `elRS70SAGGU0002_fMet` -> first peptide-bearing states -> second-round entry `elRS70SAGGU0003_Pept0002` -> proposed T_pre `elRS70SAUAA0004_Pept0003tRNAGlyGCC`.

Boundary supplies are conditional formal tokens: E2 x1, EFTu_GTP_GlytRNAGlyGCC x2, EFG_GTP x2. They are not author initial concentrations. Each delivery/factor token has its own origin lot.

EXTRACTED means exact canonical source species/equation. Functional labels come unchanged from reviewed Level-C. Physiological role and complete composite composition remain INFERRED. Shared nucleotide pools do not identify a carrier.

## Independent-review net expectation

CONCEPTUAL_NET (derived event sum; not a new source reaction or effective kinetic law):

```text
2 EFG_GTP + 2 EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> 2 EFG_GDP + 2 EFTu_GDP + 4 PO4 + elRS70SAUAA0004_Pept0003tRNAGlyGCC + tRNAGlyGCC
```

The independent verifier reparses source and recomputes this net. Free GTP/GDP/ATP/ADP/AMP/PPi have zero change: none occurs in the principal event equations. Four PO4 are released; two EFTu_GDP and two EFG_GDP remain free. One tRNAGlyGCC is released between rounds; the second tRNA is represented in T_pre. These are source-state statements, not elemental or global nucleotide-moiety conservation.

EF-Tu and EF-G GTP are already represented inside supplied composite species. No extra free GTP is charged. GDP-form release is not GTP-form regeneration. fMet-tRNA release belongs to the single upstream 0001 event and does not occur in W3.

## Round 1: fMet -> Pept0002

### W3:E01 / re0000000013

Level-C: `ELONG_aa_tRNA_delivery`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0002.xml / re1

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `140`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000021. No reverse is fired automatically.

### W3:E02 / re0000000014

Level-C: `ELONG_energy_coupling`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0002.xml / re3

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `260`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000015. No reverse is fired automatically.

### W3:E03 / re0000000016

Level-C: `ELONG_energy_coupling`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> PO4 + elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0002.xml / re7

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `1000`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000060. No reverse is fired automatically.

### W3:E04 / re0000000017

Level-C: `ELONG_aa_tRNA_delivery`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu_GDP + elRS70SAGGU0002_fMet_GlytRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0002.xml / re9

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `7`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000061. No reverse is fired automatically.

### W3:E05 / re0000000018

Level-C: `ELONG_peptide_formation`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> elRS70SBGGU0002_Pept0002tRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0002.xml / re10

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `1000`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000062. No reverse is fired automatically.

### W3:E06 / re0000000019

Level-C: `ELONG_energy_coupling`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
EFG_GTP + elRS70SBGGU0002_Pept0002tRNAGlyGCC -> elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0002.xml / re12

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `30`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000020. No reverse is fired automatically.

### W3:E07 / re0000000022

Level-C: `ELONG_energy_coupling`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP -> elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0002.xml / re16

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `31`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000023. No reverse is fired automatically.

### W3:E08 / re0000000024

Level-C: `ELONG_translocation`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4 -> PO4 + elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0002.xml / re18

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `5`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000066. No reverse is fired automatically.

### W3:E09 / re0000000025

Level-C: `ELONG_translocation`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP -> EFG_GDP + elRS70SAGGU0003_Pept0002tRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0002.xml / re19

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `1000`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000067. No reverse is fired automatically.

### W3:E10 / re0000000068

Level-C: `ELONG_tRNA_release`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SAGGU0003_Pept0002tRNAGlyGCC -> elRS70SAGGU0003_Pept0002 + tRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca1_GlyGCC.xml / re1

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `1000`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000069. No reverse is fired automatically.

## Round 2: Pept0002 -> Pept0003

### W3:E11 / re0000000074

Level-C: `ELONG_aa_tRNA_delivery`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002 -> elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0003.xml / re1

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `140`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000082. No reverse is fired automatically.

### W3:E12 / re0000000075

Level-C: `ELONG_energy_coupling`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0003.xml / re3

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `260`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000076. No reverse is fired automatically.

### W3:E13 / re0000000077

Level-C: `ELONG_energy_coupling`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> PO4 + elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0003.xml / re7

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `1000`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000118. No reverse is fired automatically.

### W3:E14 / re0000000078

Level-C: `ELONG_aa_tRNA_delivery`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu_GDP + elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0003.xml / re9

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `7`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000119. No reverse is fired automatically.

### W3:E15 / re0000000079

Level-C: `ELONG_peptide_formation`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> elRS70SBGGU0003_Pept0003tRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0003.xml / re10

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `1000`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000120. No reverse is fired automatically.

### W3:E16 / re0000000080

Level-C: `ELONG_energy_coupling`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
EFG_GTP + elRS70SBGGU0003_Pept0003tRNAGlyGCC -> elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0003.xml / re12

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `30`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000081. No reverse is fired automatically.

### W3:E17 / re0000000083

Level-C: `ELONG_energy_coupling`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP -> elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0003.xml / re16

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `31`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000084. No reverse is fired automatically.

### W3:E18 / re0000000085

Level-C: `ELONG_translocation`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4 -> PO4 + elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0003.xml / re18

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `5`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000124. No reverse is fired automatically.

### W3:E19 / re0000000086

Level-C: `ELONG_translocation`; source event: EXTRACTED; biochemical interpretation: INFERRED.

```text
elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> EFG_GDP + elRS70SAUAA0004_Pept0003tRNAGlyGCC
```

Original subsystem: models/pnas2017_full_reference/original/subsystems/Elongation_Ca2_pept0003.xml / re19

This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.

Parameter: `1000`; REFERENCE_ENABLED. Exact reverse direction(s): re0000000125. No reverse is fired automatically.

## Staged witnesses and accepted upstream composition

| Witness | Target | Events | Original sequence |
|---|---|---:|---|
| W1 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | 1 | re0000000013 |
| W2 | `elRS70SAGGU0003_Pept0002` | 10 | re0000000013 -> re0000000014 -> re0000000016 -> re0000000017 -> re0000000018 -> re0000000019 -> re0000000022 -> re0000000024 -> re0000000025 -> re0000000068 |
| W3 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC` | 19 | re0000000013 -> re0000000014 -> re0000000016 -> re0000000017 -> re0000000018 -> re0000000019 -> re0000000022 -> re0000000024 -> re0000000025 -> re0000000068 -> re0000000074 -> re0000000075 -> re0000000077 -> re0000000078 -> re0000000079 -> re0000000080 -> re0000000083 -> re0000000085 -> re0000000086 |
| W4 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC` | 30 | re0000000459 -> re0000000507 -> re0000000513 -> re0000000519 -> re0000000529 -> re0000000717 -> re0000000722 -> re0000000747 -> re0000000757 -> re0000000726 -> re0000000001 -> re0000000013 -> re0000000014 -> re0000000016 -> re0000000017 -> re0000000018 -> re0000000019 -> re0000000022 -> re0000000024 -> re0000000025 -> re0000000068 -> re0000000074 -> re0000000075 -> re0000000077 -> re0000000078 -> re0000000079 -> re0000000080 -> re0000000083 -> re0000000085 -> re0000000086 |

W1 revalidates the P7 binding interface. W4 imports only the signed IF3-first E1 scenario, adds 0001 once, and composes W3; it does not mix alternative initiation histories. IF1 and IF3 recovery is source-free-state recovery; IF2_GDP adds one PO4 to W4. External two EF-Tu and two EF-G supplies remain conditional.

## Source resource ledger for W3

| Source species | Initial | Final | Net |
|---|---:|---:|---:|
| `ADP` | 0 | 0 | 0 |
| `AMP` | 0 | 0 | 0 |
| `ATP` | 0 | 0 | 0 |
| `EFG` | 0 | 0 | 0 |
| `EFG_GDP` | 0 | 2 | 2 |
| `EFG_GTP` | 2 | 0 | -2 |
| `EFTu` | 0 | 0 | 0 |
| `EFTu_GDP` | 0 | 2 | 2 |
| `EFTu_GTP` | 0 | 0 | 0 |
| `EFTu_GTP_GlytRNAGlyGCC` | 2 | 0 | -2 |
| `FD` | 0 | 0 | 0 |
| `GDP` | 0 | 0 | 0 |
| `GTP` | 0 | 0 | 0 |
| `Gly` | 0 | 0 | 0 |
| `GlytRNAGlyGCC` | 0 | 0 | 0 |
| `Met` | 0 | 0 | 0 |
| `PO4` | 0 | 4 | 4 |
| `PPi` | 0 | 0 | 0 |
| `THF` | 0 | 0 | 0 |
| `elRS70SAGGU0002_fMet` | 1 | 0 | -1 |
| `elRS70SAGGU0002_fMettRNAfMetCAU` | 0 | 0 | 0 |
| `elRS70SAGGU0003_Pept0002` | 0 | 0 | 0 |
| `elRS70SAUAA0004_Pept0003tRNAGlyGCC` | 0 | 1 | 1 |
| `fMettRNAfMetCAU` | 0 | 0 | 0 |
| `tRNAGlyGCC` | 0 | 1 | 1 |
| `tRNAfMetCAU` | 0 | 0 | 0 |

## Competing exits, reverse channels, disabled paths and exact rejoins

All original outlets of every selected non-resource source state appear below, including off-path channels and disabled directions. Shared composite source-state identities define possible rejoins; free resource pools alone do not. Alternatives are separate potential scenarios and are never extra mandatory events.

### `EFG_GDP`

- `re0000000067`; ELONG_translocation; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000025; equation: `EFG_GDP + elRS70SAGGU0003_Pept0002tRNAGlyGCC -> elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP`.
- `re0000000125`; ELONG_translocation; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000086; equation: `EFG_GDP + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP`.
- `re0000000292`; ELONG_energy_coupling; k1=300; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000293; equation: `EFG_GDP -> EFG + GDP`.
- `re0000000297`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `EFG_GDP -> EFG_degraded + GDP`.
- `re0000000327`; ELONG_energy_coupling;RECYCLE_component_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000308; equation: `EFG_GDP + RS50S -> RS50S_EFG_GDP`.
- `re0000000328`; ELONG_energy_coupling; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000309; equation: `EFG_GDP + RS70S -> RS70S_EFG_GDP`.
- `re0000000959`; RECYCLE_component_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000913; equation: `EFG_GDP + RS50S_tRNAGlyGCC_RRF -> RS50S_tRNAGlyGCC_RRF_EFG_GDP`.
- `re0000000961`; RECYCLE_component_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000920; equation: `EFG_GDP + RS50S_tRNAGlyGCC -> RS50S_tRNAGlyGCC_EFG_GDP`.
- `re0000000966`; RECYCLE_component_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000922; equation: `EFG_GDP + RS50S_RRF -> RS50S_RRF_EFG_GDP`.

### `EFG_GTP`

- `re0000000019`; ELONG_energy_coupling; k1=30; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000020; equation: `EFG_GTP + elRS70SBGGU0002_Pept0002tRNAGlyGCC -> elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP`.
- `re0000000080`; ELONG_energy_coupling; k1=30; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000081; equation: `EFG_GTP + elRS70SBGGU0003_Pept0003tRNAGlyGCC -> elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP`.
- `re0000000295`; ELONG_energy_coupling; k1=13; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000294; equation: `EFG_GTP -> EFG + GTP`.
- `re0000000296`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `EFG_GTP -> EFG_degraded + GTP`.
- `re0000000298`; ELONG_energy_coupling; k1=30; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000299; equation: `EFG_GTP + RS50S -> RS50S_EFG_GTP`.
- `re0000000300`; ELONG_energy_coupling; k1=30; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000301; equation: `EFG_GTP + RS70S -> RS70S_EFG_GTP`.
- `re0000000895`; RECYCLE_disassembly; k1=31; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000896; equation: `EFG_GTP + termRS70SUAA0004_tRNAGlyGCC_RRF -> termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP`.
- `re0000000906`; RECYCLE_disassembly; k1=31; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000907; equation: `EFG_GTP + termRS70SUAA0004_tRNAGlyGCC -> termRS70SUAA0004_tRNAGlyGCC_EFG_GTP`.

### `EFTu_GDP`

- `re0000000061`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000017; equation: `EFTu_GDP + elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC`.
- `re0000000065`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000028; equation: `EFTu_GDP + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GDP`.
- `re0000000119`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000078; equation: `EFTu_GDP + elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC`.
- `re0000000123`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000089; equation: `EFTu_GDP + elRS70SAGGU0003_Pept0002 -> elRS70SAGGU0003_Pept0002_EFTu_GDP`.
- `re0000000266`; ELONG_energy_coupling; k1=60; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000265; equation: `EFTs + EFTu_GDP -> EFTu_GDP_EFTs`.
- `re0000000267`; ELONG_energy_coupling; k1=0.002; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000268; equation: `EFTu_GDP -> EFTu + GDP`.
- `re0000000279`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `EFTu_GDP -> EFTu_degraded + GDP`.

### `EFTu_GTP_GlytRNAGlyGCC`

- `re0000000013`; ELONG_aa_tRNA_delivery; k1=140; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000021; equation: `EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC`.
- `re0000000074`; ELONG_aa_tRNA_delivery; k1=140; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000082; equation: `EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002 -> elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC`.
- `re0000000276`; ELONG_aa_tRNA_delivery; k1=0.0013; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000275; equation: `EFTu_GTP_GlytRNAGlyGCC -> EFTu_GTP + GlytRNAGlyGCC`.
- `re0000000286`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `EFTu_GTP_GlytRNAGlyGCC -> EFTu_degraded + GTP + GlytRNAGlyGCC`.
- `re0000000287`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC_degraded`.

### `elRS70SAGGU0002_fMet`

- `re0000000002`; ELONG_tRNA_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000001; equation: `elRS70SAGGU0002_fMet + tRNAfMetCAU -> elRS70SAGGU0002_fMettRNAfMetCAU`.
- `re0000000011`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet -> RS30S + RS50S_degraded + fMet + mRNA`.
- `re0000000012`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet -> RS30S_degraded + RS50S + fMet + mRNA`.
- `re0000000013`; ELONG_aa_tRNA_delivery; k1=140; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000021; equation: `EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC`.
- `re0000000064`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000027; equation: `GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_GlytRNAGlyGCC`.
- `re0000000065`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000028; equation: `EFTu_GDP + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GDP`.

### `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC`

- `re0000000017`; ELONG_aa_tRNA_delivery; k1=7; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000061; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu_GDP + elRS70SAGGU0002_fMet_GlytRNAGlyGCC`.
- `re0000000026`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000063; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> GlytRNAGlyGCC + elRS70SAGGU0002_fMet_EFTu_GDP`.
- `re0000000039`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + RS30S + RS50S_degraded + fMet + mRNA`.
- `re0000000040`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + RS30S_degraded + RS50S + fMet + mRNA`.
- `re0000000041`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + RS30S + RS50S + fMet + mRNA`.
- `re0000000060`; ELONG_energy_coupling; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000016; equation: `PO4 + elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC`.

### `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC`

- `re0000000015`; ELONG_energy_coupling; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000014; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC`.
- `re0000000016`; ELONG_energy_coupling; k1=1000; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000060; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> PO4 + elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC`.
- `re0000000036`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + RS30S + RS50S_degraded + fMet + mRNA`.
- `re0000000037`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + RS30S_degraded + RS50S + fMet + mRNA`.
- `re0000000038`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + PO4 + RS30S + RS50S + fMet + mRNA`.

### `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC`

- `re0000000014`; ELONG_energy_coupling; k1=260; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000015; equation: `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC`.
- `re0000000021`; ELONG_aa_tRNA_delivery; k1=0.23; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000013; equation: `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet`.
- `re0000000033`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + RS30S + RS50S_degraded + fMet + mRNA`.
- `re0000000034`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + RS30S_degraded + RS50S + fMet + mRNA`.
- `re0000000035`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu_degraded + GTP + GlytRNAGlyGCC + RS30S + RS50S + fMet + mRNA`.

### `elRS70SAGGU0002_fMet_GlytRNAGlyGCC`

- `re0000000018`; ELONG_peptide_formation; k1=1000; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000062; equation: `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> elRS70SBGGU0002_Pept0002tRNAGlyGCC`.
- `re0000000027`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000064; equation: `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> GlytRNAGlyGCC + elRS70SAGGU0002_fMet`.
- `re0000000045`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> GlytRNAGlyGCC + RS30S + RS50S_degraded + fMet + mRNA`.
- `re0000000046`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> GlytRNAGlyGCC + RS30S_degraded + RS50S + fMet + mRNA`.
- `re0000000061`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000017; equation: `EFTu_GDP + elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC`.

### `elRS70SAGGU0003_Pept0002`

- `re0000000069`; ELONG_tRNA_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000068; equation: `elRS70SAGGU0003_Pept0002 + tRNAGlyGCC -> elRS70SAGGU0003_Pept0002tRNAGlyGCC`.
- `re0000000072`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002 -> Pept0002 + RS30S + RS50S_degraded + mRNA`.
- `re0000000073`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002 -> Pept0002 + RS30S_degraded + RS50S + mRNA`.
- `re0000000074`; ELONG_aa_tRNA_delivery; k1=140; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000082; equation: `EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002 -> elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC`.
- `re0000000122`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000088; equation: `GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002 -> elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC`.
- `re0000000123`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000089; equation: `EFTu_GDP + elRS70SAGGU0003_Pept0002 -> elRS70SAGGU0003_Pept0002_EFTu_GDP`.

### `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC`

- `re0000000078`; ELONG_aa_tRNA_delivery; k1=7; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000119; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu_GDP + elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC`.
- `re0000000087`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000121; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002_EFTu_GDP`.
- `re0000000097`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S_degraded + mRNA`.
- `re0000000098`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + Pept0002 + RS30S_degraded + RS50S + mRNA`.
- `re0000000099`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S + mRNA`.
- `re0000000118`; ELONG_energy_coupling; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000077; equation: `PO4 + elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC`.

### `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC`

- `re0000000076`; ELONG_energy_coupling; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000075; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC`.
- `re0000000077`; ELONG_energy_coupling; k1=1000; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000118; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> PO4 + elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC`.
- `re0000000094`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + Pept0002 + RS30S + RS50S_degraded + mRNA`.
- `re0000000095`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + Pept0002 + RS30S_degraded + RS50S + mRNA`.
- `re0000000096`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + PO4 + Pept0002 + RS30S + RS50S + mRNA`.

### `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC`

- `re0000000075`; ELONG_energy_coupling; k1=260; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000076; equation: `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC`.
- `re0000000082`; ELONG_aa_tRNA_delivery; k1=0.23; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000074; equation: `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002`.
- `re0000000091`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S_degraded + mRNA`.
- `re0000000092`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + Pept0002 + RS30S_degraded + RS50S + mRNA`.
- `re0000000093`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu_degraded + GTP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S + mRNA`.

### `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC`

- `re0000000079`; ELONG_peptide_formation; k1=1000; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000120; equation: `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> elRS70SBGGU0003_Pept0003tRNAGlyGCC`.
- `re0000000088`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000122; equation: `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> GlytRNAGlyGCC + elRS70SAGGU0003_Pept0002`.
- `re0000000103`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> GlytRNAGlyGCC + Pept0002 + RS30S + RS50S_degraded + mRNA`.
- `re0000000104`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> GlytRNAGlyGCC + Pept0002 + RS30S_degraded + RS50S + mRNA`.
- `re0000000119`; ELONG_aa_tRNA_delivery; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000078; equation: `EFTu_GDP + elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC`.

### `elRS70SAGGU0003_Pept0002tRNAGlyGCC`

- `re0000000058`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002tRNAGlyGCC -> Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000059`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAGGU0003_Pept0002tRNAGlyGCC -> Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000067`; ELONG_translocation; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000025; equation: `EFG_GDP + elRS70SAGGU0003_Pept0002tRNAGlyGCC -> elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP`.
- `re0000000068`; ELONG_tRNA_release; k1=1000; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000069; equation: `elRS70SAGGU0003_Pept0002tRNAGlyGCC -> elRS70SAGGU0003_Pept0002 + tRNAGlyGCC`.

### `elRS70SAUAA0004_Pept0003tRNAGlyGCC`

- `re0000000116`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAUAA0004_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000117`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SAUAA0004_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000125`; ELONG_translocation; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000086; equation: `EFG_GDP + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP`.
- `re0000000796`; TERM_factor_binding; k1=60; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000797; equation: `RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`.
- `re0000000811`; TERM_factor_binding; k1=23; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000812; equation: `RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`.

### `elRS70SBGGU0002_Pept0002tRNAGlyGCC`

- `re0000000019`; ELONG_energy_coupling; k1=30; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000020; equation: `EFG_GTP + elRS70SBGGU0002_Pept0002tRNAGlyGCC -> elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP`.
- `re0000000047`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC -> Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000048`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC -> Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000062`; ELONG_peptide_formation; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000018; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC -> elRS70SAGGU0002_fMet_GlytRNAGlyGCC`.

### `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4`

- `re0000000023`; ELONG_energy_coupling; k1=5; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000022; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4 -> elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP`.
- `re0000000024`; ELONG_translocation; k1=5; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000066; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4 -> PO4 + elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP`.
- `re0000000055`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4 -> EFG + GDP + PO4 + Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000056`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4 -> EFG + GDP + PO4 + Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000057`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4 -> EFG_degraded + GDP + PO4 + Pept0002tRNAGlyGCC + RS30S + RS50S + mRNA`.

### `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP`

- `re0000000020`; ELONG_energy_coupling; k1=25; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000019; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP -> EFG_GTP + elRS70SBGGU0002_Pept0002tRNAGlyGCC`.
- `re0000000022`; ELONG_energy_coupling; k1=31; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000023; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP -> elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4`.
- `re0000000049`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP -> EFG + GTP + Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000050`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP -> EFG + GTP + Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000051`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP -> EFG_degraded + GTP + Pept0002tRNAGlyGCC + RS30S + RS50S + mRNA`.

### `elRS70SBGGU0003_Pept0003tRNAGlyGCC`

- `re0000000080`; ELONG_energy_coupling; k1=30; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000081; equation: `EFG_GTP + elRS70SBGGU0003_Pept0003tRNAGlyGCC -> elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP`.
- `re0000000105`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000106`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000120`; ELONG_peptide_formation; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000079; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC -> elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC`.

### `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4`

- `re0000000084`; ELONG_energy_coupling; k1=5; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000083; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4 -> elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP`.
- `re0000000085`; ELONG_translocation; k1=5; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000124; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4 -> PO4 + elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP`.
- `re0000000113`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4 -> EFG + GDP + PO4 + Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000114`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4 -> EFG + GDP + PO4 + Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000115`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4 -> EFG_degraded + GDP + PO4 + Pept0003tRNAGlyGCC + RS30S + RS50S + mRNA`.

### `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP`

- `re0000000081`; ELONG_energy_coupling; k1=25; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000080; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP -> EFG_GTP + elRS70SBGGU0003_Pept0003tRNAGlyGCC`.
- `re0000000083`; ELONG_energy_coupling; k1=31; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000084; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP -> elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4`.
- `re0000000107`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP -> EFG + GTP + Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000108`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP -> EFG + GTP + Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000109`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP -> EFG_degraded + GTP + Pept0003tRNAGlyGCC + RS30S + RS50S + mRNA`.

### `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP`

- `re0000000025`; ELONG_translocation; k1=1000; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000067; equation: `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP -> EFG_GDP + elRS70SAGGU0003_Pept0002tRNAGlyGCC`.
- `re0000000052`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP -> EFG + GDP + Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000053`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP -> EFG + GDP + Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000054`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP -> EFG_degraded + GDP + Pept0002tRNAGlyGCC + RS30S + RS50S + mRNA`.
- `re0000000066`; ELONG_translocation; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000024; equation: `PO4 + elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP -> elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4`.

### `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP`

- `re0000000086`; ELONG_translocation; k1=1000; REFERENCE_ENABLED; ELONGATION_SEARCH_SCOPE; reverse=re0000000125; equation: `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> EFG_GDP + elRS70SAUAA0004_Pept0003tRNAGlyGCC`.
- `re0000000110`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> EFG + GDP + Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000111`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> EFG + GDP + Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000112`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> EFG_degraded + GDP + Pept0003tRNAGlyGCC + RS30S + RS50S + mRNA`.
- `re0000000124`; ELONG_translocation; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000085; equation: `PO4 + elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4`.

### `tRNAGlyGCC`

- `re0000000069`; ELONG_tRNA_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000068; equation: `elRS70SAGGU0003_Pept0002 + tRNAGlyGCC -> elRS70SAGGU0003_Pept0002tRNAGlyGCC`.
- `re0000000070`; DEG_sink; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=; equation: `tRNAGlyGCC -> tRNAGlyGCC_degraded`.
- `re0000000199`; RS_binding; k1=376; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000201; equation: `GlyRS + tRNAGlyGCC -> GlyRS_tRNAGlyGCC`.
- `re0000000200`; RS_binding; k1=376; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000202; equation: `GlyRS_Gly + tRNAGlyGCC -> GlyRS_Gly_tRNAGlyGCC`.
- `re0000000203`; RS_binding; k1=376; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000204; equation: `GlyRS_ATP + tRNAGlyGCC -> GlyRS_ATP_tRNAGlyGCC`.
- `re0000000205`; RS_binding; k1=376; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000206; equation: `GlyRS_Gly_ATP + tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC`.
- `re0000000207`; RS_activation;RS_charging; k1=353; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000208; equation: `GlyRS_GlyAMP_PPi + tRNAGlyGCC -> GlyRS_GlyAMP_PPi_tRNAGlyGCC`.
- `re0000000209`; RS_charging; k1=353; REFERENCE_ENABLED; BOUNDARY_CONTEXT_ONLY; reverse=re0000000210; equation: `GlyRS_GlyAMP + tRNAGlyGCC -> GlyRS_GlyAMP_tRNAGlyGCC`.
- `re0000000216`; RS_charging; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000176; equation: `Gly + tRNAGlyGCC -> GlytRNAGlyGCC`.
- `re0000000960`; RECYCLE_component_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000915; equation: `RS50S_RRF_EFG_GDP + tRNAGlyGCC -> RS50S_tRNAGlyGCC_RRF_EFG_GDP`.
- `re0000000963`; RECYCLE_component_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000921; equation: `RS50S_EFG_GDP + tRNAGlyGCC -> RS50S_tRNAGlyGCC_EFG_GDP`.
- `re0000000965`; RECYCLE_component_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000916; equation: `RS50S_RRF + tRNAGlyGCC -> RS50S_tRNAGlyGCC_RRF`.
- `re0000000967`; RECYCLE_component_release; k1=0; REFERENCE_DISABLED; DISABLED_SOURCE_CONTEXT; reverse=re0000000919; equation: `RS50S + tRNAGlyGCC -> RS50S_tRNAGlyGCC`.

## Read-only T_pre / termination interface

0086 produces the proposed endpoint and EFG_GDP. T_pre also participates in RF1/RF2 binding, their reverses, disabled EF-G association and degradation. No termination event is executed in W1-W4; no free Pept0003 product is claimed.

- `re0000000086` / ELONG_translocation / REFERENCE_ENABLED: `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> EFG_GDP + elRS70SAUAA0004_Pept0003tRNAGlyGCC`.
- `re0000000116` / DEG_sink / REFERENCE_DISABLED: `elRS70SAUAA0004_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA`.
- `re0000000117` / DEG_sink / REFERENCE_DISABLED: `elRS70SAUAA0004_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA`.
- `re0000000125` / ELONG_translocation / REFERENCE_DISABLED: `EFG_GDP + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP`.
- `re0000000796` / TERM_factor_binding / REFERENCE_ENABLED: `RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`.
- `re0000000797` / TERM_factor_binding / REFERENCE_ENABLED: `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC`.
- `re0000000811` / TERM_factor_binding / REFERENCE_ENABLED: `RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`.
- `re0000000812` / TERM_factor_binding / REFERENCE_ENABLED: `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC`.

## Coverage, interpretation and source authority

```json
{
  "classification_counts": {
    "BOUNDARY_CONTEXT_ONLY": 47,
    "DISABLED_SOURCE_CONTEXT": 232,
    "ELONGATION_SEARCH_SCOPE": 62,
    "OUT_OF_B1_2_SCOPE": 627
  },
  "context_only_directions": 147,
  "core_directions": 194,
  "core_positive": 62,
  "core_zero": 132,
  "entire_model_inventory": 968,
  "inventory_positive": 109,
  "inventory_zero": 232,
  "search_directions": 61,
  "selected_family_ids": [
    "RFAM_001",
    "RFAM_002",
    "RFAM_003",
    "RFAM_004",
    "RFAM_009",
    "RFAM_010",
    "RFAM_011",
    "RFAM_012",
    "RFAM_013",
    "RFAM_014",
    "RFAM_019",
    "RFAM_025",
    "RFAM_033",
    "RFAM_034",
    "RFAM_DEG"
  ],
  "selected_inventory": 341
}
```

Inventory selection is the union of exact original subsystem membership and ELONG contexts, augmented by one-hop carrier incidence and exact reverse metadata. It is not an ID interval. Positive author parameters mean REFERENCE_ENABLED, not measured flux, dominance, equilibrium or guaranteed occupancy. Sorted IDs are search tie-breakers only.

The local article (Matsuura et al. 2017, DOI 10.1073/pnas.1615351114), p.2 and p.8, describes 241 components / 968 reactions and construction by functional subsystems. Page 7 discusses deactivating reaction 22 as EF-G GTP hydrolysis on translating ribosomes. This supports that limited context; it does not experimentally certify all composite names or the source-model early tRNA-release order. Complete standalone SI text/PDF remains unavailable locally.

Original S27 calls E2 and the second-round entry virtual elongation complexes. Its author definitions describe the peptide-bearing states and hydrolysis/phosphate-release/translocation steps. These definitions are EXTRACTED author-model documentation; full molecular composition and physiological identity remain INFERRED/UNRESOLVED. The proposed T_pre is factor-free and has UAA at the A site; S27 calls the RF1/RF2-bound successors pre-termination complexes. The proposed boundary label remains pending H6.

S05-S11 and S27 local XLSX source evidence are inspected separately in [the original-source interpretation appendix](phase_b1_2_original_source_evidence.md). Seven elongation workbook models map 244 local reaction rows with no equation discrepancy; 44 relevant S27 parameter rows agree with the author CSV. Secondary literature references in the paper do not replace independently inspected evidence. H1-H7 remain PENDING.

Finite search counts are retained per waypoint. Reaching T_pre is one structural witness, not complete elongation-network coverage, full-model feasibility or elapsed-time dynamics.

