# Phase B1-1 — 启动路径与首次延伸交接

Scientific status: `PENDING_HUMAN_REVIEW`. Formal tokens are not concentrations; enabled parameters are not observed flux.

E1: `elRS70SAGGU0002_fMettRNAfMetCAU`. E2: `elRS70SAGGU0002_fMet`. E1 is initiation exit; E2 follows the separately classified `ELONG_tRNA_release` event.

P1/P4 share the dual-factor 30S state; P3 omits IF1; the separate release alternative reaches E1 with IF2 released earlier. These are exclusive scenarios for one ribosomal carrier, never consecutive output units.

| Scenario | Occurrences | Endpoint | Recovered free source states |
|---|---:|---|---|
| P1 | 10 | elRS70SAGGU0002_fMettRNAfMetCAU | IF1, IF3 |
| P1-RELEASE-ALT | 10 | elRS70SAGGU0002_fMettRNAfMetCAU | IF1, IF3 |
| P2 | 11 | elRS70SAGGU0002_fMet | IF1, IF3 |
| P3 | 8 | elRS70SAGGU0002_fMettRNAfMetCAU | IF3 |
| P4 | 10 | elRS70SAGGU0002_fMettRNAfMetCAU | IF1, IF3 |
| P5 | 24 | elRS70SAGGU0002_fMettRNAfMetCAU | MetRS, MTF, IF1, IF3 |
| P5-E2 | 25 | elRS70SAGGU0002_fMet | MetRS, MTF, IF1, IF3 |
| P6 | 25 | elRS70SAGGU0002_fMettRNAfMetCAU | MetRS, MTF, IF1, IF3 |
| P7 | 12 | elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC | IF1, IF3 |

## P1

Purpose: INITIATION_E1. Boundary supplies: `IF1 × 1, IF2_GTP_fMettRNAfMetCAU × 1, IF3 × 1, RS30S × 1, RS50S × 1, mRNA × 1`.

Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.

### 30S preparation

- **re0000000459** (P1:E01): `IF3 + RS30S -> RS30S_IF3`. Context: `INIT_assembly`; author k1=1160 (REFERENCE_ENABLED); exact inverse: re0000000460 k=0.8.
  Carrier/source states: `IF3, RS30S` → `RS30S_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000507** (P1:E02): `IF1 + RS30S_IF3 -> RS30S_IF1_IF3`. Context: `INIT_assembly`; author k1=20 (REFERENCE_ENABLED); exact inverse: re0000000508 k=0.7.
  Carrier/source states: `IF1, RS30S_IF3` → `RS30S_IF1_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000513** (P1:E03): `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA`. Context: `INIT_assembly`; author k1=36 (REFERENCE_ENABLED); exact inverse: re0000000514 k=0.7.
  Carrier/source states: `RS30S_IF1_IF3, mRNA` → `RS30S_IF1_IF3_mRNA`. All co-reactants and outputs are in the full equation.
### mRNA / IF2-fMet-tRNA recruitment

- **re0000000519** (P1:E04): `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_tRNA_recruitment`; author k1=220 (REFERENCE_ENABLED); exact inverse: re0000000520 k=1.
  Carrier/source states: `IF2_GTP_fMettRNAfMetCAU, RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### 50S joining

- **re0000000529** (P1:E05): `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_70S_formation`; author k1=34 (REFERENCE_ENABLED); exact inverse: re0000000530 k=35.
  Carrier/source states: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA, RS50S` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### GTP / GDP / PO4 source-state transition

- **re0000000717** (P1:E06): `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=2.3 (REFERENCE_ENABLED); exact inverse: re0000000718 k=2.1.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000722** (P1:E07): `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=12 (REFERENCE_ENABLED); exact inverse: re0000000746 k=0.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### Factor release / E1

- **re0000000724** (P1:E08): `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=0.0025 (REFERENCE_ENABLED); exact inverse: re0000000723 k=16.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF1, RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000755** (P1:E09): `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000756 k=0.
  Carrier/source states: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3, RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000726** (P1:E10): `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU`. Context: `INIT_factor_release`; author k1=4 (REFERENCE_ENABLED); exact inverse: re0000000752 k=200.
  Carrier/source states: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP, elRS70SAGGU0002_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.

**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**

```text
IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> IF2_GDP + PO4 + elRS70SAGGU0002_fMettRNAfMetCAU
```

DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):

- `P1:E01` → `P1:E02`: `RS30S_IF3` × 1.
- `P1:E02` → `P1:E03`: `RS30S_IF1_IF3` × 1.
- `P1:E03` → `P1:E04`: `RS30S_IF1_IF3_mRNA` × 1.
- `P1:E04` → `P1:E05`: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E05` → `P1:E06`: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E06` → `P1:E07`: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E07` → `P1:E08`: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E08` → `P1:E09`: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E09` → `P1:E10`: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.

True rejoins: `RS30S_IF1_IF3, RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA, elRS70SAGGU0002_fMettRNAfMetCAU`. IF2_GDP release is not IF2_GTP recovery. The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.

Competing source exits from this witness's actual precursor states (context only; inverse/sink directions are not extra occurrences):

| Original precursor state | Original outgoing directions (reference k1) |
|---|---|
| `IF1` | re0000000501 (k=20), re0000000503 (k=20), re0000000505 (k=20), re0000000507 (k=20), re0000000509 (k=12), re0000000511 (k=12), re0000000531 (k=20), re0000000533 (k=20), re0000000535 (k=12), re0000000537 (k=16), re0000000539 (k=16), re0000000541 (k=0), re0000000649 (k=20), re0000000651 (k=20), re0000000677 (k=20), re0000000679 (k=20), re0000000683 (k=20), re0000000685 (k=20), re0000000719 (k=16), re0000000723 (k=16), re0000000754 (k=0), re0000000758 (k=0), re0000000766 (k=0) |
| `IF2_GTP_fMettRNAfMetCAU` | re0000000450 (k=40), re0000000454 (k=0), re0000000465 (k=280), re0000000475 (k=280), re0000000497 (k=220), re0000000519 (k=220), re0000000611 (k=280), re0000000623 (k=280), re0000000645 (k=220), re0000000665 (k=220) |
| `IF3` | re0000000457 (k=0.082), re0000000459 (k=1160), re0000000489 (k=0.082), re0000000491 (k=1100), re0000000542 (k=0), re0000000615 (k=1160), re0000000617 (k=1160), re0000000635 (k=1160), re0000000637 (k=1160), re0000000639 (k=1160), re0000000641 (k=1160), re0000000653 (k=1100), re0000000655 (k=1100), re0000000667 (k=1100), re0000000669 (k=1100), re0000000671 (k=1100), re0000000673 (k=1100), re0000000748 (k=0), re0000000756 (k=0), re0000000762 (k=0), re0000000764 (k=0) |
| `RS30S` | re0000000004 (k=0), re0000000456 (k=12), re0000000459 (k=1160), re0000000503 (k=20), re0000000609 (k=280), re0000000611 (k=280), re0000000619 (k=36), re0000000912 (k=0) |
| `RS30S_IF1_IF3` | re0000000492 (k=0.08), re0000000494 (k=0.18), re0000000495 (k=220), re0000000497 (k=220), re0000000508 (k=0.7), re0000000513 (k=36), re0000000559 (k=0), re0000000560 (k=0), re0000000561 (k=0) |
| `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000520 (k=1), re0000000522 (k=0.015), re0000000524 (k=1.5), re0000000528 (k=0.006), re0000000529 (k=34), re0000000538 (k=0.0025), re0000000596 (k=0), re0000000597 (k=0), re0000000598 (k=0), re0000000599 (k=0), re0000000674 (k=0.08) |
| `RS30S_IF1_IF3_mRNA` | re0000000514 (k=0.7), re0000000515 (k=220), re0000000517 (k=5), re0000000519 (k=220), re0000000532 (k=0.7), re0000000568 (k=0), re0000000569 (k=0), re0000000570 (k=0), re0000000668 (k=0.08) |
| `RS30S_IF3` | re0000000460 (k=0.8), re0000000462 (k=0.18), re0000000463 (k=280), re0000000465 (k=280), re0000000469 (k=36), re0000000507 (k=20), re0000000547 (k=0), re0000000548 (k=0) |
| `RS50S` | re0000000003 (k=0), re0000000298 (k=30), re0000000327 (k=0), re0000000456 (k=12), re0000000462 (k=0.18), re0000000485 (k=34), re0000000488 (k=12), re0000000494 (k=0.18), re0000000529 (k=34), re0000000967 (k=0), re0000000968 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | re0000000718 (k=2.1), re0000000720 (k=0.0025), re0000000722 (k=12), re0000000740 (k=0), re0000000741 (k=0), re0000000742 (k=0), re0000000743 (k=0), re0000000744 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000724 (k=0.0025), re0000000731 (k=0), re0000000732 (k=0), re0000000733 (k=0), re0000000734 (k=0), re0000000735 (k=0), re0000000746 (k=0), re0000000747 (k=1000), re0000000749 (k=4) |
| `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000530 (k=35), re0000000540 (k=0.0025), re0000000604 (k=0), re0000000605 (k=0), re0000000606 (k=0), re0000000607 (k=0), re0000000608 (k=0), re0000000717 (k=2.3) |
| `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000726 (k=4), re0000000756 (k=0), re0000000758 (k=0), re0000000767 (k=0), re0000000768 (k=0), re0000000769 (k=0) |
| `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000723 (k=16), re0000000725 (k=4), re0000000727 (k=0), re0000000728 (k=0), re0000000729 (k=0), re0000000730 (k=0), re0000000745 (k=0), re0000000755 (k=1000) |

## P1-RELEASE-ALT

Purpose: INITIATION_E1. Boundary supplies: `IF1 × 1, IF2_GTP_fMettRNAfMetCAU × 1, IF3 × 1, RS30S × 1, RS50S × 1, mRNA × 1`.

Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.

### 30S preparation

- **re0000000459** (P1-RELEASE-ALT:E01): `IF3 + RS30S -> RS30S_IF3`. Context: `INIT_assembly`; author k1=1160 (REFERENCE_ENABLED); exact inverse: re0000000460 k=0.8.
  Carrier/source states: `IF3, RS30S` → `RS30S_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000507** (P1-RELEASE-ALT:E02): `IF1 + RS30S_IF3 -> RS30S_IF1_IF3`. Context: `INIT_assembly`; author k1=20 (REFERENCE_ENABLED); exact inverse: re0000000508 k=0.7.
  Carrier/source states: `IF1, RS30S_IF3` → `RS30S_IF1_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000513** (P1-RELEASE-ALT:E03): `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA`. Context: `INIT_assembly`; author k1=36 (REFERENCE_ENABLED); exact inverse: re0000000514 k=0.7.
  Carrier/source states: `RS30S_IF1_IF3, mRNA` → `RS30S_IF1_IF3_mRNA`. All co-reactants and outputs are in the full equation.
### mRNA / IF2-fMet-tRNA recruitment

- **re0000000519** (P1-RELEASE-ALT:E04): `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_tRNA_recruitment`; author k1=220 (REFERENCE_ENABLED); exact inverse: re0000000520 k=1.
  Carrier/source states: `IF2_GTP_fMettRNAfMetCAU, RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### 50S joining

- **re0000000529** (P1-RELEASE-ALT:E05): `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_70S_formation`; author k1=34 (REFERENCE_ENABLED); exact inverse: re0000000530 k=35.
  Carrier/source states: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA, RS50S` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### GTP / GDP / PO4 source-state transition

- **re0000000717** (P1-RELEASE-ALT:E06): `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=2.3 (REFERENCE_ENABLED); exact inverse: re0000000718 k=2.1.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000722** (P1-RELEASE-ALT:E07): `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=12 (REFERENCE_ENABLED); exact inverse: re0000000746 k=0.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### Factor release / E1

- **re0000000749** (P1-RELEASE-ALT:E08): `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=4 (REFERENCE_ENABLED); exact inverse: re0000000750 k=200.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP, RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000753** (P1-RELEASE-ALT:E09): `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000754 k=0.
  Carrier/source states: `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1, RS70S_IF3_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000763** (P1-RELEASE-ALT:E10): `RS70S_IF3_fMettRNAfMetCAU_mRNA -> IF3 + elRS70SAGGU0002_fMettRNAfMetCAU`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000764 k=0.
  Carrier/source states: `RS70S_IF3_fMettRNAfMetCAU_mRNA` → `IF3, elRS70SAGGU0002_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.

**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**

```text
IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> IF2_GDP + PO4 + elRS70SAGGU0002_fMettRNAfMetCAU
```

DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):

- `P1-RELEASE-ALT:E01` → `P1-RELEASE-ALT:E02`: `RS30S_IF3` × 1.
- `P1-RELEASE-ALT:E02` → `P1-RELEASE-ALT:E03`: `RS30S_IF1_IF3` × 1.
- `P1-RELEASE-ALT:E03` → `P1-RELEASE-ALT:E04`: `RS30S_IF1_IF3_mRNA` × 1.
- `P1-RELEASE-ALT:E04` → `P1-RELEASE-ALT:E05`: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1-RELEASE-ALT:E05` → `P1-RELEASE-ALT:E06`: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1-RELEASE-ALT:E06` → `P1-RELEASE-ALT:E07`: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` × 1.
- `P1-RELEASE-ALT:E07` → `P1-RELEASE-ALT:E08`: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1-RELEASE-ALT:E08` → `P1-RELEASE-ALT:E09`: `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` × 1.
- `P1-RELEASE-ALT:E09` → `P1-RELEASE-ALT:E10`: `RS70S_IF3_fMettRNAfMetCAU_mRNA` × 1.

True rejoins: `elRS70SAGGU0002_fMettRNAfMetCAU`. IF2_GDP release is not IF2_GTP recovery. The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.

Competing source exits from this witness's actual precursor states (context only; inverse/sink directions are not extra occurrences):

| Original precursor state | Original outgoing directions (reference k1) |
|---|---|
| `IF1` | re0000000501 (k=20), re0000000503 (k=20), re0000000505 (k=20), re0000000507 (k=20), re0000000509 (k=12), re0000000511 (k=12), re0000000531 (k=20), re0000000533 (k=20), re0000000535 (k=12), re0000000537 (k=16), re0000000539 (k=16), re0000000541 (k=0), re0000000649 (k=20), re0000000651 (k=20), re0000000677 (k=20), re0000000679 (k=20), re0000000683 (k=20), re0000000685 (k=20), re0000000719 (k=16), re0000000723 (k=16), re0000000754 (k=0), re0000000758 (k=0), re0000000766 (k=0) |
| `IF2_GTP_fMettRNAfMetCAU` | re0000000450 (k=40), re0000000454 (k=0), re0000000465 (k=280), re0000000475 (k=280), re0000000497 (k=220), re0000000519 (k=220), re0000000611 (k=280), re0000000623 (k=280), re0000000645 (k=220), re0000000665 (k=220) |
| `IF3` | re0000000457 (k=0.082), re0000000459 (k=1160), re0000000489 (k=0.082), re0000000491 (k=1100), re0000000542 (k=0), re0000000615 (k=1160), re0000000617 (k=1160), re0000000635 (k=1160), re0000000637 (k=1160), re0000000639 (k=1160), re0000000641 (k=1160), re0000000653 (k=1100), re0000000655 (k=1100), re0000000667 (k=1100), re0000000669 (k=1100), re0000000671 (k=1100), re0000000673 (k=1100), re0000000748 (k=0), re0000000756 (k=0), re0000000762 (k=0), re0000000764 (k=0) |
| `RS30S` | re0000000004 (k=0), re0000000456 (k=12), re0000000459 (k=1160), re0000000503 (k=20), re0000000609 (k=280), re0000000611 (k=280), re0000000619 (k=36), re0000000912 (k=0) |
| `RS30S_IF1_IF3` | re0000000492 (k=0.08), re0000000494 (k=0.18), re0000000495 (k=220), re0000000497 (k=220), re0000000508 (k=0.7), re0000000513 (k=36), re0000000559 (k=0), re0000000560 (k=0), re0000000561 (k=0) |
| `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000520 (k=1), re0000000522 (k=0.015), re0000000524 (k=1.5), re0000000528 (k=0.006), re0000000529 (k=34), re0000000538 (k=0.0025), re0000000596 (k=0), re0000000597 (k=0), re0000000598 (k=0), re0000000599 (k=0), re0000000674 (k=0.08) |
| `RS30S_IF1_IF3_mRNA` | re0000000514 (k=0.7), re0000000515 (k=220), re0000000517 (k=5), re0000000519 (k=220), re0000000532 (k=0.7), re0000000568 (k=0), re0000000569 (k=0), re0000000570 (k=0), re0000000668 (k=0.08) |
| `RS30S_IF3` | re0000000460 (k=0.8), re0000000462 (k=0.18), re0000000463 (k=280), re0000000465 (k=280), re0000000469 (k=36), re0000000507 (k=20), re0000000547 (k=0), re0000000548 (k=0) |
| `RS50S` | re0000000003 (k=0), re0000000298 (k=30), re0000000327 (k=0), re0000000456 (k=12), re0000000462 (k=0.18), re0000000485 (k=34), re0000000488 (k=12), re0000000494 (k=0.18), re0000000529 (k=34), re0000000967 (k=0), re0000000968 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | re0000000718 (k=2.1), re0000000720 (k=0.0025), re0000000722 (k=12), re0000000740 (k=0), re0000000741 (k=0), re0000000742 (k=0), re0000000743 (k=0), re0000000744 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000724 (k=0.0025), re0000000731 (k=0), re0000000732 (k=0), re0000000733 (k=0), re0000000734 (k=0), re0000000735 (k=0), re0000000746 (k=0), re0000000747 (k=1000), re0000000749 (k=4) |
| `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000530 (k=35), re0000000540 (k=0.0025), re0000000604 (k=0), re0000000605 (k=0), re0000000606 (k=0), re0000000607 (k=0), re0000000608 (k=0), re0000000717 (k=2.3) |
| `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` | re0000000750 (k=200), re0000000753 (k=1000), re0000000761 (k=1000), re0000000773 (k=0), re0000000774 (k=0), re0000000775 (k=0), re0000000776 (k=0) |
| `RS70S_IF3_fMettRNAfMetCAU_mRNA` | re0000000751 (k=200), re0000000754 (k=0), re0000000763 (k=1000), re0000000770 (k=0), re0000000771 (k=0), re0000000772 (k=0) |

## P2

Purpose: INITIATION_WITH_E2_BOUNDARY. Boundary supplies: `IF1 × 1, IF2_GTP_fMettRNAfMetCAU × 1, IF3 × 1, RS30S × 1, RS50S × 1, mRNA × 1`.

Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.

### 30S preparation

- **re0000000459** (P1:E01): `IF3 + RS30S -> RS30S_IF3`. Context: `INIT_assembly`; author k1=1160 (REFERENCE_ENABLED); exact inverse: re0000000460 k=0.8.
  Carrier/source states: `IF3, RS30S` → `RS30S_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000507** (P1:E02): `IF1 + RS30S_IF3 -> RS30S_IF1_IF3`. Context: `INIT_assembly`; author k1=20 (REFERENCE_ENABLED); exact inverse: re0000000508 k=0.7.
  Carrier/source states: `IF1, RS30S_IF3` → `RS30S_IF1_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000513** (P1:E03): `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA`. Context: `INIT_assembly`; author k1=36 (REFERENCE_ENABLED); exact inverse: re0000000514 k=0.7.
  Carrier/source states: `RS30S_IF1_IF3, mRNA` → `RS30S_IF1_IF3_mRNA`. All co-reactants and outputs are in the full equation.
### mRNA / IF2-fMet-tRNA recruitment

- **re0000000519** (P1:E04): `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_tRNA_recruitment`; author k1=220 (REFERENCE_ENABLED); exact inverse: re0000000520 k=1.
  Carrier/source states: `IF2_GTP_fMettRNAfMetCAU, RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### 50S joining

- **re0000000529** (P1:E05): `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_70S_formation`; author k1=34 (REFERENCE_ENABLED); exact inverse: re0000000530 k=35.
  Carrier/source states: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA, RS50S` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### GTP / GDP / PO4 source-state transition

- **re0000000717** (P1:E06): `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=2.3 (REFERENCE_ENABLED); exact inverse: re0000000718 k=2.1.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000722** (P1:E07): `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=12 (REFERENCE_ENABLED); exact inverse: re0000000746 k=0.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### Factor release / E1

- **re0000000724** (P1:E08): `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=0.0025 (REFERENCE_ENABLED); exact inverse: re0000000723 k=16.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF1, RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000755** (P1:E09): `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000756 k=0.
  Carrier/source states: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3, RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000726** (P1:E10): `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU`. Context: `INIT_factor_release`; author k1=4 (REFERENCE_ENABLED); exact inverse: re0000000752 k=200.
  Carrier/source states: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP, elRS70SAGGU0002_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
### E2 cross-module boundary

- **re0000000001** (P2:E2-BRIDGE): `elRS70SAGGU0002_fMettRNAfMetCAU -> elRS70SAGGU0002_fMet + tRNAfMetCAU`. Context: `ELONG_tRNA_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000002 k=0.
  Carrier/source states: `elRS70SAGGU0002_fMettRNAfMetCAU` → `elRS70SAGGU0002_fMet, tRNAfMetCAU`. All co-reactants and outputs are in the full equation.

**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**

```text
IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> IF2_GDP + PO4 + elRS70SAGGU0002_fMet + tRNAfMetCAU
```

DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):

- `P1:E01` → `P1:E02`: `RS30S_IF3` × 1.
- `P1:E02` → `P1:E03`: `RS30S_IF1_IF3` × 1.
- `P1:E03` → `P1:E04`: `RS30S_IF1_IF3_mRNA` × 1.
- `P1:E04` → `P1:E05`: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E05` → `P1:E06`: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E06` → `P1:E07`: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E07` → `P1:E08`: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E08` → `P1:E09`: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E09` → `P1:E10`: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E10` → `P2:E2-BRIDGE`: `elRS70SAGGU0002_fMettRNAfMetCAU` × 1.

True rejoins: ``. IF2_GDP release is not IF2_GTP recovery. The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.

Competing source exits from this witness's actual precursor states (context only; inverse/sink directions are not extra occurrences):

| Original precursor state | Original outgoing directions (reference k1) |
|---|---|
| `IF1` | re0000000501 (k=20), re0000000503 (k=20), re0000000505 (k=20), re0000000507 (k=20), re0000000509 (k=12), re0000000511 (k=12), re0000000531 (k=20), re0000000533 (k=20), re0000000535 (k=12), re0000000537 (k=16), re0000000539 (k=16), re0000000541 (k=0), re0000000649 (k=20), re0000000651 (k=20), re0000000677 (k=20), re0000000679 (k=20), re0000000683 (k=20), re0000000685 (k=20), re0000000719 (k=16), re0000000723 (k=16), re0000000754 (k=0), re0000000758 (k=0), re0000000766 (k=0) |
| `IF2_GTP_fMettRNAfMetCAU` | re0000000450 (k=40), re0000000454 (k=0), re0000000465 (k=280), re0000000475 (k=280), re0000000497 (k=220), re0000000519 (k=220), re0000000611 (k=280), re0000000623 (k=280), re0000000645 (k=220), re0000000665 (k=220) |
| `IF3` | re0000000457 (k=0.082), re0000000459 (k=1160), re0000000489 (k=0.082), re0000000491 (k=1100), re0000000542 (k=0), re0000000615 (k=1160), re0000000617 (k=1160), re0000000635 (k=1160), re0000000637 (k=1160), re0000000639 (k=1160), re0000000641 (k=1160), re0000000653 (k=1100), re0000000655 (k=1100), re0000000667 (k=1100), re0000000669 (k=1100), re0000000671 (k=1100), re0000000673 (k=1100), re0000000748 (k=0), re0000000756 (k=0), re0000000762 (k=0), re0000000764 (k=0) |
| `RS30S` | re0000000004 (k=0), re0000000456 (k=12), re0000000459 (k=1160), re0000000503 (k=20), re0000000609 (k=280), re0000000611 (k=280), re0000000619 (k=36), re0000000912 (k=0) |
| `RS30S_IF1_IF3` | re0000000492 (k=0.08), re0000000494 (k=0.18), re0000000495 (k=220), re0000000497 (k=220), re0000000508 (k=0.7), re0000000513 (k=36), re0000000559 (k=0), re0000000560 (k=0), re0000000561 (k=0) |
| `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000520 (k=1), re0000000522 (k=0.015), re0000000524 (k=1.5), re0000000528 (k=0.006), re0000000529 (k=34), re0000000538 (k=0.0025), re0000000596 (k=0), re0000000597 (k=0), re0000000598 (k=0), re0000000599 (k=0), re0000000674 (k=0.08) |
| `RS30S_IF1_IF3_mRNA` | re0000000514 (k=0.7), re0000000515 (k=220), re0000000517 (k=5), re0000000519 (k=220), re0000000532 (k=0.7), re0000000568 (k=0), re0000000569 (k=0), re0000000570 (k=0), re0000000668 (k=0.08) |
| `RS30S_IF3` | re0000000460 (k=0.8), re0000000462 (k=0.18), re0000000463 (k=280), re0000000465 (k=280), re0000000469 (k=36), re0000000507 (k=20), re0000000547 (k=0), re0000000548 (k=0) |
| `RS50S` | re0000000003 (k=0), re0000000298 (k=30), re0000000327 (k=0), re0000000456 (k=12), re0000000462 (k=0.18), re0000000485 (k=34), re0000000488 (k=12), re0000000494 (k=0.18), re0000000529 (k=34), re0000000967 (k=0), re0000000968 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | re0000000718 (k=2.1), re0000000720 (k=0.0025), re0000000722 (k=12), re0000000740 (k=0), re0000000741 (k=0), re0000000742 (k=0), re0000000743 (k=0), re0000000744 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000724 (k=0.0025), re0000000731 (k=0), re0000000732 (k=0), re0000000733 (k=0), re0000000734 (k=0), re0000000735 (k=0), re0000000746 (k=0), re0000000747 (k=1000), re0000000749 (k=4) |
| `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000530 (k=35), re0000000540 (k=0.0025), re0000000604 (k=0), re0000000605 (k=0), re0000000606 (k=0), re0000000607 (k=0), re0000000608 (k=0), re0000000717 (k=2.3) |
| `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000726 (k=4), re0000000756 (k=0), re0000000758 (k=0), re0000000767 (k=0), re0000000768 (k=0), re0000000769 (k=0) |
| `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000723 (k=16), re0000000725 (k=4), re0000000727 (k=0), re0000000728 (k=0), re0000000729 (k=0), re0000000730 (k=0), re0000000745 (k=0), re0000000755 (k=1000) |
| `elRS70SAGGU0002_fMettRNAfMetCAU` | re0000000001 (k=1000), re0000000009 (k=0), re0000000010 (k=0), re0000000752 (k=200), re0000000764 (k=0), re0000000766 (k=0) |

## P3

Purpose: INITIATION_E1. Boundary supplies: `IF2_GTP_fMettRNAfMetCAU × 1, IF3 × 1, RS30S × 1, RS50S × 1, mRNA × 1`.

Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.

### 30S preparation

- **re0000000459** (P3:E01): `IF3 + RS30S -> RS30S_IF3`. Context: `INIT_assembly`; author k1=1160 (REFERENCE_ENABLED); exact inverse: re0000000460 k=0.8.
  Carrier/source states: `IF3, RS30S` → `RS30S_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000469** (P3:E02): `RS30S_IF3 + mRNA -> RS30S_IF3_mRNA`. Context: `INIT_assembly`; author k1=36 (REFERENCE_ENABLED); exact inverse: re0000000470 k=0.7.
  Carrier/source states: `RS30S_IF3, mRNA` → `RS30S_IF3_mRNA`. All co-reactants and outputs are in the full equation.
### mRNA / IF2-fMet-tRNA recruitment

- **re0000000475** (P3:E03): `IF2_GTP_fMettRNAfMetCAU + RS30S_IF3_mRNA -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_tRNA_recruitment`; author k1=280 (REFERENCE_ENABLED); exact inverse: re0000000476 k=1.5.
  Carrier/source states: `IF2_GTP_fMettRNAfMetCAU, RS30S_IF3_mRNA` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### 50S joining

- **re0000000485** (P3:E04): `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_70S_formation`; author k1=34 (REFERENCE_ENABLED); exact inverse: re0000000486 k=35.
  Carrier/source states: `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA, RS50S` → `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### GTP / GDP / PO4 source-state transition

- **re0000000715** (P3:E05): `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=2.3 (REFERENCE_ENABLED); exact inverse: re0000000716 k=2.1.
  Carrier/source states: `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000721** (P3:E06): `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=12 (REFERENCE_ENABLED); exact inverse: re0000000745 k=0.
  Carrier/source states: `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### Factor release / E1

- **re0000000755** (P3:E07): `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000756 k=0.
  Carrier/source states: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3, RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000726** (P3:E08): `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU`. Context: `INIT_factor_release`; author k1=4 (REFERENCE_ENABLED); exact inverse: re0000000752 k=200.
  Carrier/source states: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP, elRS70SAGGU0002_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.

**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**

```text
IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> IF2_GDP + PO4 + elRS70SAGGU0002_fMettRNAfMetCAU
```

DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):

- `P3:E01` → `P3:E02`: `RS30S_IF3` × 1.
- `P3:E02` → `P3:E03`: `RS30S_IF3_mRNA` × 1.
- `P3:E03` → `P3:E04`: `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P3:E04` → `P3:E05`: `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P3:E05` → `P3:E06`: `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` × 1.
- `P3:E06` → `P3:E07`: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P3:E07` → `P3:E08`: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.

True rejoins: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. IF2_GDP release is not IF2_GTP recovery. The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.

Competing source exits from this witness's actual precursor states (context only; inverse/sink directions are not extra occurrences):

| Original precursor state | Original outgoing directions (reference k1) |
|---|---|
| `IF2_GTP_fMettRNAfMetCAU` | re0000000450 (k=40), re0000000454 (k=0), re0000000465 (k=280), re0000000475 (k=280), re0000000497 (k=220), re0000000519 (k=220), re0000000611 (k=280), re0000000623 (k=280), re0000000645 (k=220), re0000000665 (k=220) |
| `IF3` | re0000000457 (k=0.082), re0000000459 (k=1160), re0000000489 (k=0.082), re0000000491 (k=1100), re0000000542 (k=0), re0000000615 (k=1160), re0000000617 (k=1160), re0000000635 (k=1160), re0000000637 (k=1160), re0000000639 (k=1160), re0000000641 (k=1160), re0000000653 (k=1100), re0000000655 (k=1100), re0000000667 (k=1100), re0000000669 (k=1100), re0000000671 (k=1100), re0000000673 (k=1100), re0000000748 (k=0), re0000000756 (k=0), re0000000762 (k=0), re0000000764 (k=0) |
| `RS30S` | re0000000004 (k=0), re0000000456 (k=12), re0000000459 (k=1160), re0000000503 (k=20), re0000000609 (k=280), re0000000611 (k=280), re0000000619 (k=36), re0000000912 (k=0) |
| `RS30S_IF3` | re0000000460 (k=0.8), re0000000462 (k=0.18), re0000000463 (k=280), re0000000465 (k=280), re0000000469 (k=36), re0000000507 (k=20), re0000000547 (k=0), re0000000548 (k=0) |
| `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000476 (k=1.5), re0000000478 (k=12), re0000000480 (k=1.5), re0000000484 (k=0.7), re0000000485 (k=34), re0000000537 (k=16), re0000000577 (k=0), re0000000578 (k=0), re0000000579 (k=0), re0000000642 (k=0.8) |
| `RS30S_IF3_mRNA` | re0000000470 (k=0.7), re0000000471 (k=280), re0000000473 (k=5), re0000000475 (k=280), re0000000531 (k=20), re0000000549 (k=0), re0000000550 (k=0), re0000000636 (k=0.8) |
| `RS50S` | re0000000003 (k=0), re0000000298 (k=30), re0000000327 (k=0), re0000000456 (k=12), re0000000462 (k=0.18), re0000000485 (k=34), re0000000488 (k=12), re0000000494 (k=0.18), re0000000529 (k=34), re0000000967 (k=0), re0000000968 (k=0) |
| `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000726 (k=4), re0000000756 (k=0), re0000000758 (k=0), re0000000767 (k=0), re0000000768 (k=0), re0000000769 (k=0) |
| `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | re0000000716 (k=2.1), re0000000719 (k=16), re0000000721 (k=12), re0000000736 (k=0), re0000000737 (k=0), re0000000738 (k=0), re0000000739 (k=0) |
| `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000723 (k=16), re0000000725 (k=4), re0000000727 (k=0), re0000000728 (k=0), re0000000729 (k=0), re0000000730 (k=0), re0000000745 (k=0), re0000000755 (k=1000) |
| `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000486 (k=35), re0000000539 (k=16), re0000000600 (k=0), re0000000601 (k=0), re0000000602 (k=0), re0000000603 (k=0), re0000000715 (k=2.3) |

## P4

Purpose: INITIATION_E1. Boundary supplies: `IF1 × 1, IF2_GTP_fMettRNAfMetCAU × 1, IF3 × 1, RS30S × 1, RS50S × 1, mRNA × 1`.

Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.

### 30S preparation

- **re0000000503** (P4:E01): `IF1 + RS30S -> RS30S_IF1`. Context: `INIT_assembly`; author k1=20 (REFERENCE_ENABLED); exact inverse: re0000000504 k=0.7.
  Carrier/source states: `IF1, RS30S` → `RS30S_IF1`. All co-reactants and outputs are in the full equation.
- **re0000000491** (P4:E02): `IF3 + RS30S_IF1 -> RS30S_IF1_IF3`. Context: `INIT_assembly`; author k1=1100 (REFERENCE_ENABLED); exact inverse: re0000000492 k=0.08.
  Carrier/source states: `IF3, RS30S_IF1` → `RS30S_IF1_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000513** (P4:E03): `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA`. Context: `INIT_assembly`; author k1=36 (REFERENCE_ENABLED); exact inverse: re0000000514 k=0.7.
  Carrier/source states: `RS30S_IF1_IF3, mRNA` → `RS30S_IF1_IF3_mRNA`. All co-reactants and outputs are in the full equation.
### mRNA / IF2-fMet-tRNA recruitment

- **re0000000519** (P4:E04): `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_tRNA_recruitment`; author k1=220 (REFERENCE_ENABLED); exact inverse: re0000000520 k=1.
  Carrier/source states: `IF2_GTP_fMettRNAfMetCAU, RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### 50S joining

- **re0000000529** (P4:E05): `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_70S_formation`; author k1=34 (REFERENCE_ENABLED); exact inverse: re0000000530 k=35.
  Carrier/source states: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA, RS50S` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### GTP / GDP / PO4 source-state transition

- **re0000000717** (P4:E06): `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=2.3 (REFERENCE_ENABLED); exact inverse: re0000000718 k=2.1.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000722** (P4:E07): `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=12 (REFERENCE_ENABLED); exact inverse: re0000000746 k=0.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### Factor release / E1

- **re0000000724** (P4:E08): `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=0.0025 (REFERENCE_ENABLED); exact inverse: re0000000723 k=16.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF1, RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000755** (P4:E09): `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000756 k=0.
  Carrier/source states: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3, RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000726** (P4:E10): `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU`. Context: `INIT_factor_release`; author k1=4 (REFERENCE_ENABLED); exact inverse: re0000000752 k=200.
  Carrier/source states: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP, elRS70SAGGU0002_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.

**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**

```text
IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> IF2_GDP + PO4 + elRS70SAGGU0002_fMettRNAfMetCAU
```

DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):

- `P4:E01` → `P4:E02`: `RS30S_IF1` × 1.
- `P4:E02` → `P4:E03`: `RS30S_IF1_IF3` × 1.
- `P4:E03` → `P4:E04`: `RS30S_IF1_IF3_mRNA` × 1.
- `P4:E04` → `P4:E05`: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P4:E05` → `P4:E06`: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P4:E06` → `P4:E07`: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` × 1.
- `P4:E07` → `P4:E08`: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P4:E08` → `P4:E09`: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P4:E09` → `P4:E10`: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.

True rejoins: `RS30S_IF1_IF3`. IF2_GDP release is not IF2_GTP recovery. The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.

Competing source exits from this witness's actual precursor states (context only; inverse/sink directions are not extra occurrences):

| Original precursor state | Original outgoing directions (reference k1) |
|---|---|
| `IF1` | re0000000501 (k=20), re0000000503 (k=20), re0000000505 (k=20), re0000000507 (k=20), re0000000509 (k=12), re0000000511 (k=12), re0000000531 (k=20), re0000000533 (k=20), re0000000535 (k=12), re0000000537 (k=16), re0000000539 (k=16), re0000000541 (k=0), re0000000649 (k=20), re0000000651 (k=20), re0000000677 (k=20), re0000000679 (k=20), re0000000683 (k=20), re0000000685 (k=20), re0000000719 (k=16), re0000000723 (k=16), re0000000754 (k=0), re0000000758 (k=0), re0000000766 (k=0) |
| `IF2_GTP_fMettRNAfMetCAU` | re0000000450 (k=40), re0000000454 (k=0), re0000000465 (k=280), re0000000475 (k=280), re0000000497 (k=220), re0000000519 (k=220), re0000000611 (k=280), re0000000623 (k=280), re0000000645 (k=220), re0000000665 (k=220) |
| `IF3` | re0000000457 (k=0.082), re0000000459 (k=1160), re0000000489 (k=0.082), re0000000491 (k=1100), re0000000542 (k=0), re0000000615 (k=1160), re0000000617 (k=1160), re0000000635 (k=1160), re0000000637 (k=1160), re0000000639 (k=1160), re0000000641 (k=1160), re0000000653 (k=1100), re0000000655 (k=1100), re0000000667 (k=1100), re0000000669 (k=1100), re0000000671 (k=1100), re0000000673 (k=1100), re0000000748 (k=0), re0000000756 (k=0), re0000000762 (k=0), re0000000764 (k=0) |
| `RS30S` | re0000000004 (k=0), re0000000456 (k=12), re0000000459 (k=1160), re0000000503 (k=20), re0000000609 (k=280), re0000000611 (k=280), re0000000619 (k=36), re0000000912 (k=0) |
| `RS30S_IF1` | re0000000488 (k=12), re0000000491 (k=1100), re0000000504 (k=0.7), re0000000545 (k=0), re0000000546 (k=0), re0000000643 (k=220), re0000000645 (k=220), re0000000675 (k=36) |
| `RS30S_IF1_IF3` | re0000000492 (k=0.08), re0000000494 (k=0.18), re0000000495 (k=220), re0000000497 (k=220), re0000000508 (k=0.7), re0000000513 (k=36), re0000000559 (k=0), re0000000560 (k=0), re0000000561 (k=0) |
| `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000520 (k=1), re0000000522 (k=0.015), re0000000524 (k=1.5), re0000000528 (k=0.006), re0000000529 (k=34), re0000000538 (k=0.0025), re0000000596 (k=0), re0000000597 (k=0), re0000000598 (k=0), re0000000599 (k=0), re0000000674 (k=0.08) |
| `RS30S_IF1_IF3_mRNA` | re0000000514 (k=0.7), re0000000515 (k=220), re0000000517 (k=5), re0000000519 (k=220), re0000000532 (k=0.7), re0000000568 (k=0), re0000000569 (k=0), re0000000570 (k=0), re0000000668 (k=0.08) |
| `RS50S` | re0000000003 (k=0), re0000000298 (k=30), re0000000327 (k=0), re0000000456 (k=12), re0000000462 (k=0.18), re0000000485 (k=34), re0000000488 (k=12), re0000000494 (k=0.18), re0000000529 (k=34), re0000000967 (k=0), re0000000968 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | re0000000718 (k=2.1), re0000000720 (k=0.0025), re0000000722 (k=12), re0000000740 (k=0), re0000000741 (k=0), re0000000742 (k=0), re0000000743 (k=0), re0000000744 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000724 (k=0.0025), re0000000731 (k=0), re0000000732 (k=0), re0000000733 (k=0), re0000000734 (k=0), re0000000735 (k=0), re0000000746 (k=0), re0000000747 (k=1000), re0000000749 (k=4) |
| `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000530 (k=35), re0000000540 (k=0.0025), re0000000604 (k=0), re0000000605 (k=0), re0000000606 (k=0), re0000000607 (k=0), re0000000608 (k=0), re0000000717 (k=2.3) |
| `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000726 (k=4), re0000000756 (k=0), re0000000758 (k=0), re0000000767 (k=0), re0000000768 (k=0), re0000000769 (k=0) |
| `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000723 (k=16), re0000000725 (k=4), re0000000727 (k=0), re0000000728 (k=0), re0000000729 (k=0), re0000000730 (k=0), re0000000745 (k=0), re0000000755 (k=1000) |

## P5

Purpose: INITIATION_E1. Boundary supplies: `ATP × 1, FD × 1, IF1 × 1, IF2_GTP × 1, IF3 × 1, MTF × 1, Met × 1, MetRS × 1, RS30S × 1, RS50S × 1, mRNA × 1, tRNAfMetCAU × 1`.

Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.

### B0 upstream precursor (independent of 30S)

- **re0000000151** (W3:E01): `Met + MetRS -> MetRS_Met`. Context: `RS_binding`; author k1=5 (REFERENCE_ENABLED); exact inverse: re0000000156 k=350.
  Carrier/source states: `MetRS` → `MetRS_Met`. All co-reactants and outputs are in the full equation.
- **re0000000161** (W3:E02): `ATP + MetRS_Met -> MetRS_Met_ATP`. Context: `RS_binding`; author k1=10 (REFERENCE_ENABLED); exact inverse: re0000000162 k=2500.
  Carrier/source states: `MetRS_Met` → `MetRS_Met_ATP`. All co-reactants and outputs are in the full equation.
- **re0000000247** (W3:E03): `MetRS_Met_ATP + tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU`. Context: `RS_binding`; author k1=50 (REFERENCE_ENABLED); exact inverse: re0000000248 k=150.
  Carrier/source states: `MetRS_Met_ATP, tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000239** (W3:E04): `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU`. Context: `RS_activation`; author k1=200 (REFERENCE_ENABLED); exact inverse: re0000000240 k=0.
  Carrier/source states: `MetRS_Met_ATP_tRNAfMetCAU` → `MetRS_MetAMP_PPi_tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000231** (W3:E05): `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU + PPi`. Context: `RS_activation`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000260 k=0.
  Carrier/source states: `MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetRS_MetAMP_tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000220** (W3:E06): `MetRS_MetAMP_tRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU`. Context: `RS_charging`; author k1=13.7 (REFERENCE_ENABLED); exact inverse: re0000000221 k=0.
  Carrier/source states: `MetRS_MetAMP_tRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000224** (W3:E07): `MetRS_AMP_MettRNAfMetCAU -> MetRS_AMP + MettRNAfMetCAU`. Context: `RS_charging`; author k1=1.685 (REFERENCE_ENABLED); exact inverse: re0000000225 k=5.6.
  Carrier/source states: `MetRS_AMP_MettRNAfMetCAU` → `MetRS_AMP, MettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000170** (W3:E08): `MetRS_AMP -> AMP + MetRS`. Context: `RS_charging`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000171 k=0.
  Carrier/source states: `MetRS_AMP` → `MetRS`. All co-reactants and outputs are in the full equation.
- **re0000000418** (W3:E09): `FD + MTF -> MTF_FD`. Context: `RS_to_INIT_formylation`; author k1=74.07407407 (REFERENCE_ENABLED); exact inverse: re0000000419 k=1000.
  Carrier/source states: `MTF` → `MTF_FD`. All co-reactants and outputs are in the full equation.
- **re0000000422** (W3:E10): `MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU`. Context: `RS_to_INIT_formylation`; author k1=2000 (REFERENCE_ENABLED); exact inverse: re0000000423 k=1000.
  Carrier/source states: `MTF_FD, MettRNAfMetCAU` → `MTF_FD_MettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000426** (W3:E11): `MTF_FD_MettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU`. Context: `RS_to_INIT_formylation`; author k1=37.3 (REFERENCE_ENABLED); exact inverse: re0000000427 k=0.
  Carrier/source states: `MTF_FD_MettRNAfMetCAU` → `MTF_THF_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000428** (W3:E12): `MTF_THF_fMettRNAfMetCAU -> MTF_THF + fMettRNAfMetCAU`. Context: `RS_to_INIT_formylation`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000429 k=0.
  Carrier/source states: `MTF_THF_fMettRNAfMetCAU` → `MTF_THF, fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000434** (W3:E13): `MTF_THF -> MTF + THF`. Context: `RS_to_INIT_formylation`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000435 k=0.
  Carrier/source states: `MTF_THF` → `MTF`. All co-reactants and outputs are in the full equation.
- **re0000000449** (W3:E14): `IF2_GTP + fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU`. Context: `INIT_tRNA_recruitment`; author k1=40 (REFERENCE_ENABLED); exact inverse: re0000000450 k=40.
  Carrier/source states: `IF2_GTP, fMettRNAfMetCAU` → `IF2_GTP_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
### 30S preparation

- **re0000000459** (P1:E01): `IF3 + RS30S -> RS30S_IF3`. Context: `INIT_assembly`; author k1=1160 (REFERENCE_ENABLED); exact inverse: re0000000460 k=0.8.
  Carrier/source states: `IF3, RS30S` → `RS30S_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000507** (P1:E02): `IF1 + RS30S_IF3 -> RS30S_IF1_IF3`. Context: `INIT_assembly`; author k1=20 (REFERENCE_ENABLED); exact inverse: re0000000508 k=0.7.
  Carrier/source states: `IF1, RS30S_IF3` → `RS30S_IF1_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000513** (P1:E03): `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA`. Context: `INIT_assembly`; author k1=36 (REFERENCE_ENABLED); exact inverse: re0000000514 k=0.7.
  Carrier/source states: `RS30S_IF1_IF3, mRNA` → `RS30S_IF1_IF3_mRNA`. All co-reactants and outputs are in the full equation.
### mRNA / IF2-fMet-tRNA recruitment

- **re0000000519** (P1:E04): `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_tRNA_recruitment`; author k1=220 (REFERENCE_ENABLED); exact inverse: re0000000520 k=1.
  Carrier/source states: `IF2_GTP_fMettRNAfMetCAU, RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### 50S joining

- **re0000000529** (P1:E05): `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_70S_formation`; author k1=34 (REFERENCE_ENABLED); exact inverse: re0000000530 k=35.
  Carrier/source states: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA, RS50S` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### GTP / GDP / PO4 source-state transition

- **re0000000717** (P1:E06): `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=2.3 (REFERENCE_ENABLED); exact inverse: re0000000718 k=2.1.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000722** (P1:E07): `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=12 (REFERENCE_ENABLED); exact inverse: re0000000746 k=0.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### Factor release / E1

- **re0000000724** (P1:E08): `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=0.0025 (REFERENCE_ENABLED); exact inverse: re0000000723 k=16.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF1, RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000755** (P1:E09): `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000756 k=0.
  Carrier/source states: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3, RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000726** (P1:E10): `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU`. Context: `INIT_factor_release`; author k1=4 (REFERENCE_ENABLED); exact inverse: re0000000752 k=200.
  Carrier/source states: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP, elRS70SAGGU0002_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.

**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**

```text
ATP + FD + IF2_GTP + Met + RS30S + RS50S + mRNA + tRNAfMetCAU -> AMP + IF2_GDP + PO4 + PPi + THF + elRS70SAGGU0002_fMettRNAfMetCAU
```

DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):

- `W3:E01` → `W3:E02`: `MetRS_Met` × 1.
- `W3:E02` → `W3:E03`: `MetRS_Met_ATP` × 1.
- `W3:E03` → `W3:E04`: `MetRS_Met_ATP_tRNAfMetCAU` × 1.
- `W3:E04` → `W3:E05`: `MetRS_MetAMP_PPi_tRNAfMetCAU` × 1.
- `W3:E05` → `W3:E06`: `MetRS_MetAMP_tRNAfMetCAU` × 1.
- `W3:E06` → `W3:E07`: `MetRS_AMP_MettRNAfMetCAU` × 1.
- `W3:E07` → `W3:E08`: `MetRS_AMP` × 1.
- `W3:E09` → `W3:E10`: `MTF_FD` × 1.
- `W3:E07` → `W3:E10`: `MettRNAfMetCAU` × 1.
- `W3:E10` → `W3:E11`: `MTF_FD_MettRNAfMetCAU` × 1.
- `W3:E11` → `W3:E12`: `MTF_THF_fMettRNAfMetCAU` × 1.
- `W3:E12` → `W3:E13`: `MTF_THF` × 1.
- `W3:E12` → `W3:E14`: `fMettRNAfMetCAU` × 1.
- `P1:E01` → `P1:E02`: `RS30S_IF3` × 1.
- `P1:E02` → `P1:E03`: `RS30S_IF1_IF3` × 1.
- `W3:E14` → `P1:E04`: `IF2_GTP_fMettRNAfMetCAU` × 1.
- `P1:E03` → `P1:E04`: `RS30S_IF1_IF3_mRNA` × 1.
- `P1:E04` → `P1:E05`: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E05` → `P1:E06`: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E06` → `P1:E07`: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E07` → `P1:E08`: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E08` → `P1:E09`: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E09` → `P1:E10`: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.

True rejoins: ``. IF2_GDP release is not IF2_GTP recovery. The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.

Competing source exits from this witness's actual precursor states (context only; inverse/sink directions are not extra occurrences):

| Original precursor state | Original outgoing directions (reference k1) |
|---|---|
| `IF1` | re0000000501 (k=20), re0000000503 (k=20), re0000000505 (k=20), re0000000507 (k=20), re0000000509 (k=12), re0000000511 (k=12), re0000000531 (k=20), re0000000533 (k=20), re0000000535 (k=12), re0000000537 (k=16), re0000000539 (k=16), re0000000541 (k=0), re0000000649 (k=20), re0000000651 (k=20), re0000000677 (k=20), re0000000679 (k=20), re0000000683 (k=20), re0000000685 (k=20), re0000000719 (k=16), re0000000723 (k=16), re0000000754 (k=0), re0000000758 (k=0), re0000000766 (k=0) |
| `IF2_GTP` | re0000000446 (k=67), re0000000449 (k=40), re0000000453 (k=0), re0000000463 (k=280), re0000000471 (k=280), re0000000477 (k=280), re0000000495 (k=220), re0000000515 (k=220), re0000000521 (k=320), re0000000609 (k=280), re0000000625 (k=280), re0000000627 (k=280), re0000000643 (k=220), re0000000657 (k=220), re0000000663 (k=220) |
| `IF2_GTP_fMettRNAfMetCAU` | re0000000450 (k=40), re0000000454 (k=0), re0000000465 (k=280), re0000000475 (k=280), re0000000497 (k=220), re0000000519 (k=220), re0000000611 (k=280), re0000000623 (k=280), re0000000645 (k=220), re0000000665 (k=220) |
| `IF3` | re0000000457 (k=0.082), re0000000459 (k=1160), re0000000489 (k=0.082), re0000000491 (k=1100), re0000000542 (k=0), re0000000615 (k=1160), re0000000617 (k=1160), re0000000635 (k=1160), re0000000637 (k=1160), re0000000639 (k=1160), re0000000641 (k=1160), re0000000653 (k=1100), re0000000655 (k=1100), re0000000667 (k=1100), re0000000669 (k=1100), re0000000671 (k=1100), re0000000673 (k=1100), re0000000748 (k=0), re0000000756 (k=0), re0000000762 (k=0), re0000000764 (k=0) |
| `MettRNAfMetCAU` | re0000000218 (k=0), re0000000225 (k=5.6), re0000000227 (k=5.6), re0000000258 (k=0), re0000000288 (k=1.5), re0000000420 (k=2000), re0000000422 (k=2000) |
| `RS30S` | re0000000004 (k=0), re0000000456 (k=12), re0000000459 (k=1160), re0000000503 (k=20), re0000000609 (k=280), re0000000611 (k=280), re0000000619 (k=36), re0000000912 (k=0) |
| `RS30S_IF1_IF3` | re0000000492 (k=0.08), re0000000494 (k=0.18), re0000000495 (k=220), re0000000497 (k=220), re0000000508 (k=0.7), re0000000513 (k=36), re0000000559 (k=0), re0000000560 (k=0), re0000000561 (k=0) |
| `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000520 (k=1), re0000000522 (k=0.015), re0000000524 (k=1.5), re0000000528 (k=0.006), re0000000529 (k=34), re0000000538 (k=0.0025), re0000000596 (k=0), re0000000597 (k=0), re0000000598 (k=0), re0000000599 (k=0), re0000000674 (k=0.08) |
| `RS30S_IF1_IF3_mRNA` | re0000000514 (k=0.7), re0000000515 (k=220), re0000000517 (k=5), re0000000519 (k=220), re0000000532 (k=0.7), re0000000568 (k=0), re0000000569 (k=0), re0000000570 (k=0), re0000000668 (k=0.08) |
| `RS30S_IF3` | re0000000460 (k=0.8), re0000000462 (k=0.18), re0000000463 (k=280), re0000000465 (k=280), re0000000469 (k=36), re0000000507 (k=20), re0000000547 (k=0), re0000000548 (k=0) |
| `RS50S` | re0000000003 (k=0), re0000000298 (k=30), re0000000327 (k=0), re0000000456 (k=12), re0000000462 (k=0.18), re0000000485 (k=34), re0000000488 (k=12), re0000000494 (k=0.18), re0000000529 (k=34), re0000000967 (k=0), re0000000968 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | re0000000718 (k=2.1), re0000000720 (k=0.0025), re0000000722 (k=12), re0000000740 (k=0), re0000000741 (k=0), re0000000742 (k=0), re0000000743 (k=0), re0000000744 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000724 (k=0.0025), re0000000731 (k=0), re0000000732 (k=0), re0000000733 (k=0), re0000000734 (k=0), re0000000735 (k=0), re0000000746 (k=0), re0000000747 (k=1000), re0000000749 (k=4) |
| `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000530 (k=35), re0000000540 (k=0.0025), re0000000604 (k=0), re0000000605 (k=0), re0000000606 (k=0), re0000000607 (k=0), re0000000608 (k=0), re0000000717 (k=2.3) |
| `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000726 (k=4), re0000000756 (k=0), re0000000758 (k=0), re0000000767 (k=0), re0000000768 (k=0), re0000000769 (k=0) |
| `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000723 (k=16), re0000000725 (k=4), re0000000727 (k=0), re0000000728 (k=0), re0000000729 (k=0), re0000000730 (k=0), re0000000745 (k=0), re0000000755 (k=1000) |
| `fMettRNAfMetCAU` | re0000000005 (k=0), re0000000417 (k=0), re0000000429 (k=0), re0000000433 (k=0), re0000000449 (k=40), re0000000467 (k=5), re0000000473 (k=5), re0000000479 (k=5), re0000000499 (k=5), re0000000517 (k=5), re0000000523 (k=5), re0000000613 (k=5), re0000000621 (k=5), re0000000629 (k=5), re0000000647 (k=5), re0000000659 (k=5), re0000000661 (k=5) |

## P5-E2

Purpose: INITIATION_WITH_E2_BOUNDARY. Boundary supplies: `ATP × 1, FD × 1, IF1 × 1, IF2_GTP × 1, IF3 × 1, MTF × 1, Met × 1, MetRS × 1, RS30S × 1, RS50S × 1, mRNA × 1, tRNAfMetCAU × 1`.

Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.

### B0 upstream precursor (independent of 30S)

- **re0000000151** (W3:E01): `Met + MetRS -> MetRS_Met`. Context: `RS_binding`; author k1=5 (REFERENCE_ENABLED); exact inverse: re0000000156 k=350.
  Carrier/source states: `MetRS` → `MetRS_Met`. All co-reactants and outputs are in the full equation.
- **re0000000161** (W3:E02): `ATP + MetRS_Met -> MetRS_Met_ATP`. Context: `RS_binding`; author k1=10 (REFERENCE_ENABLED); exact inverse: re0000000162 k=2500.
  Carrier/source states: `MetRS_Met` → `MetRS_Met_ATP`. All co-reactants and outputs are in the full equation.
- **re0000000247** (W3:E03): `MetRS_Met_ATP + tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU`. Context: `RS_binding`; author k1=50 (REFERENCE_ENABLED); exact inverse: re0000000248 k=150.
  Carrier/source states: `MetRS_Met_ATP, tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000239** (W3:E04): `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU`. Context: `RS_activation`; author k1=200 (REFERENCE_ENABLED); exact inverse: re0000000240 k=0.
  Carrier/source states: `MetRS_Met_ATP_tRNAfMetCAU` → `MetRS_MetAMP_PPi_tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000231** (W3:E05): `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU + PPi`. Context: `RS_activation`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000260 k=0.
  Carrier/source states: `MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetRS_MetAMP_tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000220** (W3:E06): `MetRS_MetAMP_tRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU`. Context: `RS_charging`; author k1=13.7 (REFERENCE_ENABLED); exact inverse: re0000000221 k=0.
  Carrier/source states: `MetRS_MetAMP_tRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000224** (W3:E07): `MetRS_AMP_MettRNAfMetCAU -> MetRS_AMP + MettRNAfMetCAU`. Context: `RS_charging`; author k1=1.685 (REFERENCE_ENABLED); exact inverse: re0000000225 k=5.6.
  Carrier/source states: `MetRS_AMP_MettRNAfMetCAU` → `MetRS_AMP, MettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000170** (W3:E08): `MetRS_AMP -> AMP + MetRS`. Context: `RS_charging`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000171 k=0.
  Carrier/source states: `MetRS_AMP` → `MetRS`. All co-reactants and outputs are in the full equation.
- **re0000000418** (W3:E09): `FD + MTF -> MTF_FD`. Context: `RS_to_INIT_formylation`; author k1=74.07407407 (REFERENCE_ENABLED); exact inverse: re0000000419 k=1000.
  Carrier/source states: `MTF` → `MTF_FD`. All co-reactants and outputs are in the full equation.
- **re0000000422** (W3:E10): `MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU`. Context: `RS_to_INIT_formylation`; author k1=2000 (REFERENCE_ENABLED); exact inverse: re0000000423 k=1000.
  Carrier/source states: `MTF_FD, MettRNAfMetCAU` → `MTF_FD_MettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000426** (W3:E11): `MTF_FD_MettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU`. Context: `RS_to_INIT_formylation`; author k1=37.3 (REFERENCE_ENABLED); exact inverse: re0000000427 k=0.
  Carrier/source states: `MTF_FD_MettRNAfMetCAU` → `MTF_THF_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000428** (W3:E12): `MTF_THF_fMettRNAfMetCAU -> MTF_THF + fMettRNAfMetCAU`. Context: `RS_to_INIT_formylation`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000429 k=0.
  Carrier/source states: `MTF_THF_fMettRNAfMetCAU` → `MTF_THF, fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000434** (W3:E13): `MTF_THF -> MTF + THF`. Context: `RS_to_INIT_formylation`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000435 k=0.
  Carrier/source states: `MTF_THF` → `MTF`. All co-reactants and outputs are in the full equation.
- **re0000000449** (W3:E14): `IF2_GTP + fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU`. Context: `INIT_tRNA_recruitment`; author k1=40 (REFERENCE_ENABLED); exact inverse: re0000000450 k=40.
  Carrier/source states: `IF2_GTP, fMettRNAfMetCAU` → `IF2_GTP_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
### 30S preparation

- **re0000000459** (P1:E01): `IF3 + RS30S -> RS30S_IF3`. Context: `INIT_assembly`; author k1=1160 (REFERENCE_ENABLED); exact inverse: re0000000460 k=0.8.
  Carrier/source states: `IF3, RS30S` → `RS30S_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000507** (P1:E02): `IF1 + RS30S_IF3 -> RS30S_IF1_IF3`. Context: `INIT_assembly`; author k1=20 (REFERENCE_ENABLED); exact inverse: re0000000508 k=0.7.
  Carrier/source states: `IF1, RS30S_IF3` → `RS30S_IF1_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000513** (P1:E03): `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA`. Context: `INIT_assembly`; author k1=36 (REFERENCE_ENABLED); exact inverse: re0000000514 k=0.7.
  Carrier/source states: `RS30S_IF1_IF3, mRNA` → `RS30S_IF1_IF3_mRNA`. All co-reactants and outputs are in the full equation.
### mRNA / IF2-fMet-tRNA recruitment

- **re0000000519** (P1:E04): `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_tRNA_recruitment`; author k1=220 (REFERENCE_ENABLED); exact inverse: re0000000520 k=1.
  Carrier/source states: `IF2_GTP_fMettRNAfMetCAU, RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### 50S joining

- **re0000000529** (P1:E05): `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_70S_formation`; author k1=34 (REFERENCE_ENABLED); exact inverse: re0000000530 k=35.
  Carrier/source states: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA, RS50S` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### GTP / GDP / PO4 source-state transition

- **re0000000717** (P1:E06): `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=2.3 (REFERENCE_ENABLED); exact inverse: re0000000718 k=2.1.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000722** (P1:E07): `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=12 (REFERENCE_ENABLED); exact inverse: re0000000746 k=0.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### Factor release / E1

- **re0000000724** (P1:E08): `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=0.0025 (REFERENCE_ENABLED); exact inverse: re0000000723 k=16.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF1, RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000755** (P1:E09): `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000756 k=0.
  Carrier/source states: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3, RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000726** (P1:E10): `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU`. Context: `INIT_factor_release`; author k1=4 (REFERENCE_ENABLED); exact inverse: re0000000752 k=200.
  Carrier/source states: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP, elRS70SAGGU0002_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
### E2 cross-module boundary

- **re0000000001** (P2:E2-BRIDGE): `elRS70SAGGU0002_fMettRNAfMetCAU -> elRS70SAGGU0002_fMet + tRNAfMetCAU`. Context: `ELONG_tRNA_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000002 k=0.
  Carrier/source states: `elRS70SAGGU0002_fMettRNAfMetCAU` → `elRS70SAGGU0002_fMet, tRNAfMetCAU`. All co-reactants and outputs are in the full equation.

**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**

```text
ATP + FD + IF2_GTP + Met + RS30S + RS50S + mRNA -> AMP + IF2_GDP + PO4 + PPi + THF + elRS70SAGGU0002_fMet
```

DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):

- `W3:E01` → `W3:E02`: `MetRS_Met` × 1.
- `W3:E02` → `W3:E03`: `MetRS_Met_ATP` × 1.
- `W3:E03` → `W3:E04`: `MetRS_Met_ATP_tRNAfMetCAU` × 1.
- `W3:E04` → `W3:E05`: `MetRS_MetAMP_PPi_tRNAfMetCAU` × 1.
- `W3:E05` → `W3:E06`: `MetRS_MetAMP_tRNAfMetCAU` × 1.
- `W3:E06` → `W3:E07`: `MetRS_AMP_MettRNAfMetCAU` × 1.
- `W3:E07` → `W3:E08`: `MetRS_AMP` × 1.
- `W3:E09` → `W3:E10`: `MTF_FD` × 1.
- `W3:E07` → `W3:E10`: `MettRNAfMetCAU` × 1.
- `W3:E10` → `W3:E11`: `MTF_FD_MettRNAfMetCAU` × 1.
- `W3:E11` → `W3:E12`: `MTF_THF_fMettRNAfMetCAU` × 1.
- `W3:E12` → `W3:E13`: `MTF_THF` × 1.
- `W3:E12` → `W3:E14`: `fMettRNAfMetCAU` × 1.
- `P1:E01` → `P1:E02`: `RS30S_IF3` × 1.
- `P1:E02` → `P1:E03`: `RS30S_IF1_IF3` × 1.
- `W3:E14` → `P1:E04`: `IF2_GTP_fMettRNAfMetCAU` × 1.
- `P1:E03` → `P1:E04`: `RS30S_IF1_IF3_mRNA` × 1.
- `P1:E04` → `P1:E05`: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E05` → `P1:E06`: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E06` → `P1:E07`: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E07` → `P1:E08`: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E08` → `P1:E09`: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E09` → `P1:E10`: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E10` → `P2:E2-BRIDGE`: `elRS70SAGGU0002_fMettRNAfMetCAU` × 1.

True rejoins: ``. IF2_GDP release is not IF2_GTP recovery. The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.

Competing source exits from this witness's actual precursor states (context only; inverse/sink directions are not extra occurrences):

| Original precursor state | Original outgoing directions (reference k1) |
|---|---|
| `IF1` | re0000000501 (k=20), re0000000503 (k=20), re0000000505 (k=20), re0000000507 (k=20), re0000000509 (k=12), re0000000511 (k=12), re0000000531 (k=20), re0000000533 (k=20), re0000000535 (k=12), re0000000537 (k=16), re0000000539 (k=16), re0000000541 (k=0), re0000000649 (k=20), re0000000651 (k=20), re0000000677 (k=20), re0000000679 (k=20), re0000000683 (k=20), re0000000685 (k=20), re0000000719 (k=16), re0000000723 (k=16), re0000000754 (k=0), re0000000758 (k=0), re0000000766 (k=0) |
| `IF2_GTP` | re0000000446 (k=67), re0000000449 (k=40), re0000000453 (k=0), re0000000463 (k=280), re0000000471 (k=280), re0000000477 (k=280), re0000000495 (k=220), re0000000515 (k=220), re0000000521 (k=320), re0000000609 (k=280), re0000000625 (k=280), re0000000627 (k=280), re0000000643 (k=220), re0000000657 (k=220), re0000000663 (k=220) |
| `IF2_GTP_fMettRNAfMetCAU` | re0000000450 (k=40), re0000000454 (k=0), re0000000465 (k=280), re0000000475 (k=280), re0000000497 (k=220), re0000000519 (k=220), re0000000611 (k=280), re0000000623 (k=280), re0000000645 (k=220), re0000000665 (k=220) |
| `IF3` | re0000000457 (k=0.082), re0000000459 (k=1160), re0000000489 (k=0.082), re0000000491 (k=1100), re0000000542 (k=0), re0000000615 (k=1160), re0000000617 (k=1160), re0000000635 (k=1160), re0000000637 (k=1160), re0000000639 (k=1160), re0000000641 (k=1160), re0000000653 (k=1100), re0000000655 (k=1100), re0000000667 (k=1100), re0000000669 (k=1100), re0000000671 (k=1100), re0000000673 (k=1100), re0000000748 (k=0), re0000000756 (k=0), re0000000762 (k=0), re0000000764 (k=0) |
| `MettRNAfMetCAU` | re0000000218 (k=0), re0000000225 (k=5.6), re0000000227 (k=5.6), re0000000258 (k=0), re0000000288 (k=1.5), re0000000420 (k=2000), re0000000422 (k=2000) |
| `RS30S` | re0000000004 (k=0), re0000000456 (k=12), re0000000459 (k=1160), re0000000503 (k=20), re0000000609 (k=280), re0000000611 (k=280), re0000000619 (k=36), re0000000912 (k=0) |
| `RS30S_IF1_IF3` | re0000000492 (k=0.08), re0000000494 (k=0.18), re0000000495 (k=220), re0000000497 (k=220), re0000000508 (k=0.7), re0000000513 (k=36), re0000000559 (k=0), re0000000560 (k=0), re0000000561 (k=0) |
| `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000520 (k=1), re0000000522 (k=0.015), re0000000524 (k=1.5), re0000000528 (k=0.006), re0000000529 (k=34), re0000000538 (k=0.0025), re0000000596 (k=0), re0000000597 (k=0), re0000000598 (k=0), re0000000599 (k=0), re0000000674 (k=0.08) |
| `RS30S_IF1_IF3_mRNA` | re0000000514 (k=0.7), re0000000515 (k=220), re0000000517 (k=5), re0000000519 (k=220), re0000000532 (k=0.7), re0000000568 (k=0), re0000000569 (k=0), re0000000570 (k=0), re0000000668 (k=0.08) |
| `RS30S_IF3` | re0000000460 (k=0.8), re0000000462 (k=0.18), re0000000463 (k=280), re0000000465 (k=280), re0000000469 (k=36), re0000000507 (k=20), re0000000547 (k=0), re0000000548 (k=0) |
| `RS50S` | re0000000003 (k=0), re0000000298 (k=30), re0000000327 (k=0), re0000000456 (k=12), re0000000462 (k=0.18), re0000000485 (k=34), re0000000488 (k=12), re0000000494 (k=0.18), re0000000529 (k=34), re0000000967 (k=0), re0000000968 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | re0000000718 (k=2.1), re0000000720 (k=0.0025), re0000000722 (k=12), re0000000740 (k=0), re0000000741 (k=0), re0000000742 (k=0), re0000000743 (k=0), re0000000744 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000724 (k=0.0025), re0000000731 (k=0), re0000000732 (k=0), re0000000733 (k=0), re0000000734 (k=0), re0000000735 (k=0), re0000000746 (k=0), re0000000747 (k=1000), re0000000749 (k=4) |
| `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000530 (k=35), re0000000540 (k=0.0025), re0000000604 (k=0), re0000000605 (k=0), re0000000606 (k=0), re0000000607 (k=0), re0000000608 (k=0), re0000000717 (k=2.3) |
| `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000726 (k=4), re0000000756 (k=0), re0000000758 (k=0), re0000000767 (k=0), re0000000768 (k=0), re0000000769 (k=0) |
| `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000723 (k=16), re0000000725 (k=4), re0000000727 (k=0), re0000000728 (k=0), re0000000729 (k=0), re0000000730 (k=0), re0000000745 (k=0), re0000000755 (k=1000) |
| `elRS70SAGGU0002_fMettRNAfMetCAU` | re0000000001 (k=1000), re0000000009 (k=0), re0000000010 (k=0), re0000000752 (k=200), re0000000764 (k=0), re0000000766 (k=0) |
| `fMettRNAfMetCAU` | re0000000005 (k=0), re0000000417 (k=0), re0000000429 (k=0), re0000000433 (k=0), re0000000449 (k=40), re0000000467 (k=5), re0000000473 (k=5), re0000000479 (k=5), re0000000499 (k=5), re0000000517 (k=5), re0000000523 (k=5), re0000000613 (k=5), re0000000621 (k=5), re0000000629 (k=5), re0000000647 (k=5), re0000000659 (k=5), re0000000661 (k=5) |

## P6

Purpose: INITIATION_E1. Boundary supplies: `ATP × 1, FD × 1, GTP × 1, IF1 × 1, IF2 × 1, IF3 × 1, MTF × 1, Met × 1, MetRS × 1, RS30S × 1, RS50S × 1, mRNA × 1, tRNAfMetCAU × 1`.

Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.

### GTP / GDP / PO4 source-state transition

- **re0000000445** (P6:IF2-PREP): `GTP + IF2 -> IF2_GTP`. Context: `INIT_energy_commitment`; author k1=10 (REFERENCE_ENABLED); exact inverse: re0000000446 k=67.
  Carrier/source states: `IF2` → `IF2_GTP`. All co-reactants and outputs are in the full equation.
### B0 upstream precursor (independent of 30S)

- **re0000000151** (W3:E01): `Met + MetRS -> MetRS_Met`. Context: `RS_binding`; author k1=5 (REFERENCE_ENABLED); exact inverse: re0000000156 k=350.
  Carrier/source states: `MetRS` → `MetRS_Met`. All co-reactants and outputs are in the full equation.
- **re0000000161** (W3:E02): `ATP + MetRS_Met -> MetRS_Met_ATP`. Context: `RS_binding`; author k1=10 (REFERENCE_ENABLED); exact inverse: re0000000162 k=2500.
  Carrier/source states: `MetRS_Met` → `MetRS_Met_ATP`. All co-reactants and outputs are in the full equation.
- **re0000000247** (W3:E03): `MetRS_Met_ATP + tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU`. Context: `RS_binding`; author k1=50 (REFERENCE_ENABLED); exact inverse: re0000000248 k=150.
  Carrier/source states: `MetRS_Met_ATP, tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000239** (W3:E04): `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU`. Context: `RS_activation`; author k1=200 (REFERENCE_ENABLED); exact inverse: re0000000240 k=0.
  Carrier/source states: `MetRS_Met_ATP_tRNAfMetCAU` → `MetRS_MetAMP_PPi_tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000231** (W3:E05): `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU + PPi`. Context: `RS_activation`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000260 k=0.
  Carrier/source states: `MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetRS_MetAMP_tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000220** (W3:E06): `MetRS_MetAMP_tRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU`. Context: `RS_charging`; author k1=13.7 (REFERENCE_ENABLED); exact inverse: re0000000221 k=0.
  Carrier/source states: `MetRS_MetAMP_tRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000224** (W3:E07): `MetRS_AMP_MettRNAfMetCAU -> MetRS_AMP + MettRNAfMetCAU`. Context: `RS_charging`; author k1=1.685 (REFERENCE_ENABLED); exact inverse: re0000000225 k=5.6.
  Carrier/source states: `MetRS_AMP_MettRNAfMetCAU` → `MetRS_AMP, MettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000170** (W3:E08): `MetRS_AMP -> AMP + MetRS`. Context: `RS_charging`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000171 k=0.
  Carrier/source states: `MetRS_AMP` → `MetRS`. All co-reactants and outputs are in the full equation.
- **re0000000418** (W3:E09): `FD + MTF -> MTF_FD`. Context: `RS_to_INIT_formylation`; author k1=74.07407407 (REFERENCE_ENABLED); exact inverse: re0000000419 k=1000.
  Carrier/source states: `MTF` → `MTF_FD`. All co-reactants and outputs are in the full equation.
- **re0000000422** (W3:E10): `MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU`. Context: `RS_to_INIT_formylation`; author k1=2000 (REFERENCE_ENABLED); exact inverse: re0000000423 k=1000.
  Carrier/source states: `MTF_FD, MettRNAfMetCAU` → `MTF_FD_MettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000426** (W3:E11): `MTF_FD_MettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU`. Context: `RS_to_INIT_formylation`; author k1=37.3 (REFERENCE_ENABLED); exact inverse: re0000000427 k=0.
  Carrier/source states: `MTF_FD_MettRNAfMetCAU` → `MTF_THF_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000428** (W3:E12): `MTF_THF_fMettRNAfMetCAU -> MTF_THF + fMettRNAfMetCAU`. Context: `RS_to_INIT_formylation`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000429 k=0.
  Carrier/source states: `MTF_THF_fMettRNAfMetCAU` → `MTF_THF, fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
- **re0000000434** (W3:E13): `MTF_THF -> MTF + THF`. Context: `RS_to_INIT_formylation`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000435 k=0.
  Carrier/source states: `MTF_THF` → `MTF`. All co-reactants and outputs are in the full equation.
- **re0000000449** (W3:E14): `IF2_GTP + fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU`. Context: `INIT_tRNA_recruitment`; author k1=40 (REFERENCE_ENABLED); exact inverse: re0000000450 k=40.
  Carrier/source states: `IF2_GTP, fMettRNAfMetCAU` → `IF2_GTP_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
### 30S preparation

- **re0000000459** (P1:E01): `IF3 + RS30S -> RS30S_IF3`. Context: `INIT_assembly`; author k1=1160 (REFERENCE_ENABLED); exact inverse: re0000000460 k=0.8.
  Carrier/source states: `IF3, RS30S` → `RS30S_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000507** (P1:E02): `IF1 + RS30S_IF3 -> RS30S_IF1_IF3`. Context: `INIT_assembly`; author k1=20 (REFERENCE_ENABLED); exact inverse: re0000000508 k=0.7.
  Carrier/source states: `IF1, RS30S_IF3` → `RS30S_IF1_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000513** (P1:E03): `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA`. Context: `INIT_assembly`; author k1=36 (REFERENCE_ENABLED); exact inverse: re0000000514 k=0.7.
  Carrier/source states: `RS30S_IF1_IF3, mRNA` → `RS30S_IF1_IF3_mRNA`. All co-reactants and outputs are in the full equation.
### mRNA / IF2-fMet-tRNA recruitment

- **re0000000519** (P1:E04): `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_tRNA_recruitment`; author k1=220 (REFERENCE_ENABLED); exact inverse: re0000000520 k=1.
  Carrier/source states: `IF2_GTP_fMettRNAfMetCAU, RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### 50S joining

- **re0000000529** (P1:E05): `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_70S_formation`; author k1=34 (REFERENCE_ENABLED); exact inverse: re0000000530 k=35.
  Carrier/source states: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA, RS50S` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### GTP / GDP / PO4 source-state transition

- **re0000000717** (P1:E06): `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=2.3 (REFERENCE_ENABLED); exact inverse: re0000000718 k=2.1.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000722** (P1:E07): `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=12 (REFERENCE_ENABLED); exact inverse: re0000000746 k=0.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### Factor release / E1

- **re0000000724** (P1:E08): `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=0.0025 (REFERENCE_ENABLED); exact inverse: re0000000723 k=16.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF1, RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000755** (P1:E09): `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000756 k=0.
  Carrier/source states: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3, RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000726** (P1:E10): `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU`. Context: `INIT_factor_release`; author k1=4 (REFERENCE_ENABLED); exact inverse: re0000000752 k=200.
  Carrier/source states: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP, elRS70SAGGU0002_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.

**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**

```text
ATP + FD + GTP + IF2 + Met + RS30S + RS50S + mRNA + tRNAfMetCAU -> AMP + IF2_GDP + PO4 + PPi + THF + elRS70SAGGU0002_fMettRNAfMetCAU
```

DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):

- `W3:E01` → `W3:E02`: `MetRS_Met` × 1.
- `W3:E02` → `W3:E03`: `MetRS_Met_ATP` × 1.
- `W3:E03` → `W3:E04`: `MetRS_Met_ATP_tRNAfMetCAU` × 1.
- `W3:E04` → `W3:E05`: `MetRS_MetAMP_PPi_tRNAfMetCAU` × 1.
- `W3:E05` → `W3:E06`: `MetRS_MetAMP_tRNAfMetCAU` × 1.
- `W3:E06` → `W3:E07`: `MetRS_AMP_MettRNAfMetCAU` × 1.
- `W3:E07` → `W3:E08`: `MetRS_AMP` × 1.
- `W3:E09` → `W3:E10`: `MTF_FD` × 1.
- `W3:E07` → `W3:E10`: `MettRNAfMetCAU` × 1.
- `W3:E10` → `W3:E11`: `MTF_FD_MettRNAfMetCAU` × 1.
- `W3:E11` → `W3:E12`: `MTF_THF_fMettRNAfMetCAU` × 1.
- `W3:E12` → `W3:E13`: `MTF_THF` × 1.
- `P6:IF2-PREP` → `W3:E14`: `IF2_GTP` × 1.
- `W3:E12` → `W3:E14`: `fMettRNAfMetCAU` × 1.
- `P1:E01` → `P1:E02`: `RS30S_IF3` × 1.
- `P1:E02` → `P1:E03`: `RS30S_IF1_IF3` × 1.
- `W3:E14` → `P1:E04`: `IF2_GTP_fMettRNAfMetCAU` × 1.
- `P1:E03` → `P1:E04`: `RS30S_IF1_IF3_mRNA` × 1.
- `P1:E04` → `P1:E05`: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E05` → `P1:E06`: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E06` → `P1:E07`: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E07` → `P1:E08`: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E08` → `P1:E09`: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E09` → `P1:E10`: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.

True rejoins: ``. IF2_GDP release is not IF2_GTP recovery. The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.

Competing source exits from this witness's actual precursor states (context only; inverse/sink directions are not extra occurrences):

| Original precursor state | Original outgoing directions (reference k1) |
|---|---|
| `IF1` | re0000000501 (k=20), re0000000503 (k=20), re0000000505 (k=20), re0000000507 (k=20), re0000000509 (k=12), re0000000511 (k=12), re0000000531 (k=20), re0000000533 (k=20), re0000000535 (k=12), re0000000537 (k=16), re0000000539 (k=16), re0000000541 (k=0), re0000000649 (k=20), re0000000651 (k=20), re0000000677 (k=20), re0000000679 (k=20), re0000000683 (k=20), re0000000685 (k=20), re0000000719 (k=16), re0000000723 (k=16), re0000000754 (k=0), re0000000758 (k=0), re0000000766 (k=0) |
| `IF2` | re0000000445 (k=10), re0000000447 (k=10), re0000000451 (k=0) |
| `IF2_GTP` | re0000000446 (k=67), re0000000449 (k=40), re0000000453 (k=0), re0000000463 (k=280), re0000000471 (k=280), re0000000477 (k=280), re0000000495 (k=220), re0000000515 (k=220), re0000000521 (k=320), re0000000609 (k=280), re0000000625 (k=280), re0000000627 (k=280), re0000000643 (k=220), re0000000657 (k=220), re0000000663 (k=220) |
| `IF2_GTP_fMettRNAfMetCAU` | re0000000450 (k=40), re0000000454 (k=0), re0000000465 (k=280), re0000000475 (k=280), re0000000497 (k=220), re0000000519 (k=220), re0000000611 (k=280), re0000000623 (k=280), re0000000645 (k=220), re0000000665 (k=220) |
| `IF3` | re0000000457 (k=0.082), re0000000459 (k=1160), re0000000489 (k=0.082), re0000000491 (k=1100), re0000000542 (k=0), re0000000615 (k=1160), re0000000617 (k=1160), re0000000635 (k=1160), re0000000637 (k=1160), re0000000639 (k=1160), re0000000641 (k=1160), re0000000653 (k=1100), re0000000655 (k=1100), re0000000667 (k=1100), re0000000669 (k=1100), re0000000671 (k=1100), re0000000673 (k=1100), re0000000748 (k=0), re0000000756 (k=0), re0000000762 (k=0), re0000000764 (k=0) |
| `MettRNAfMetCAU` | re0000000218 (k=0), re0000000225 (k=5.6), re0000000227 (k=5.6), re0000000258 (k=0), re0000000288 (k=1.5), re0000000420 (k=2000), re0000000422 (k=2000) |
| `RS30S` | re0000000004 (k=0), re0000000456 (k=12), re0000000459 (k=1160), re0000000503 (k=20), re0000000609 (k=280), re0000000611 (k=280), re0000000619 (k=36), re0000000912 (k=0) |
| `RS30S_IF1_IF3` | re0000000492 (k=0.08), re0000000494 (k=0.18), re0000000495 (k=220), re0000000497 (k=220), re0000000508 (k=0.7), re0000000513 (k=36), re0000000559 (k=0), re0000000560 (k=0), re0000000561 (k=0) |
| `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000520 (k=1), re0000000522 (k=0.015), re0000000524 (k=1.5), re0000000528 (k=0.006), re0000000529 (k=34), re0000000538 (k=0.0025), re0000000596 (k=0), re0000000597 (k=0), re0000000598 (k=0), re0000000599 (k=0), re0000000674 (k=0.08) |
| `RS30S_IF1_IF3_mRNA` | re0000000514 (k=0.7), re0000000515 (k=220), re0000000517 (k=5), re0000000519 (k=220), re0000000532 (k=0.7), re0000000568 (k=0), re0000000569 (k=0), re0000000570 (k=0), re0000000668 (k=0.08) |
| `RS30S_IF3` | re0000000460 (k=0.8), re0000000462 (k=0.18), re0000000463 (k=280), re0000000465 (k=280), re0000000469 (k=36), re0000000507 (k=20), re0000000547 (k=0), re0000000548 (k=0) |
| `RS50S` | re0000000003 (k=0), re0000000298 (k=30), re0000000327 (k=0), re0000000456 (k=12), re0000000462 (k=0.18), re0000000485 (k=34), re0000000488 (k=12), re0000000494 (k=0.18), re0000000529 (k=34), re0000000967 (k=0), re0000000968 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | re0000000718 (k=2.1), re0000000720 (k=0.0025), re0000000722 (k=12), re0000000740 (k=0), re0000000741 (k=0), re0000000742 (k=0), re0000000743 (k=0), re0000000744 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000724 (k=0.0025), re0000000731 (k=0), re0000000732 (k=0), re0000000733 (k=0), re0000000734 (k=0), re0000000735 (k=0), re0000000746 (k=0), re0000000747 (k=1000), re0000000749 (k=4) |
| `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000530 (k=35), re0000000540 (k=0.0025), re0000000604 (k=0), re0000000605 (k=0), re0000000606 (k=0), re0000000607 (k=0), re0000000608 (k=0), re0000000717 (k=2.3) |
| `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000726 (k=4), re0000000756 (k=0), re0000000758 (k=0), re0000000767 (k=0), re0000000768 (k=0), re0000000769 (k=0) |
| `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000723 (k=16), re0000000725 (k=4), re0000000727 (k=0), re0000000728 (k=0), re0000000729 (k=0), re0000000730 (k=0), re0000000745 (k=0), re0000000755 (k=1000) |
| `fMettRNAfMetCAU` | re0000000005 (k=0), re0000000417 (k=0), re0000000429 (k=0), re0000000433 (k=0), re0000000449 (k=40), re0000000467 (k=5), re0000000473 (k=5), re0000000479 (k=5), re0000000499 (k=5), re0000000517 (k=5), re0000000523 (k=5), re0000000613 (k=5), re0000000621 (k=5), re0000000629 (k=5), re0000000647 (k=5), re0000000659 (k=5), re0000000661 (k=5) |

## P7

Purpose: FIRST_ELONGATION_BINDING_INTERFACE. Boundary supplies: `EFTu_GTP_GlytRNAGlyGCC × 1, IF1 × 1, IF2_GTP_fMettRNAfMetCAU × 1, IF3 × 1, RS30S × 1, RS50S × 1, mRNA × 1`.

Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.

### 30S preparation

- **re0000000459** (P1:E01): `IF3 + RS30S -> RS30S_IF3`. Context: `INIT_assembly`; author k1=1160 (REFERENCE_ENABLED); exact inverse: re0000000460 k=0.8.
  Carrier/source states: `IF3, RS30S` → `RS30S_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000507** (P1:E02): `IF1 + RS30S_IF3 -> RS30S_IF1_IF3`. Context: `INIT_assembly`; author k1=20 (REFERENCE_ENABLED); exact inverse: re0000000508 k=0.7.
  Carrier/source states: `IF1, RS30S_IF3` → `RS30S_IF1_IF3`. All co-reactants and outputs are in the full equation.
- **re0000000513** (P1:E03): `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA`. Context: `INIT_assembly`; author k1=36 (REFERENCE_ENABLED); exact inverse: re0000000514 k=0.7.
  Carrier/source states: `RS30S_IF1_IF3, mRNA` → `RS30S_IF1_IF3_mRNA`. All co-reactants and outputs are in the full equation.
### mRNA / IF2-fMet-tRNA recruitment

- **re0000000519** (P1:E04): `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_tRNA_recruitment`; author k1=220 (REFERENCE_ENABLED); exact inverse: re0000000520 k=1.
  Carrier/source states: `IF2_GTP_fMettRNAfMetCAU, RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### 50S joining

- **re0000000529** (P1:E05): `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. Context: `INIT_70S_formation`; author k1=34 (REFERENCE_ENABLED); exact inverse: re0000000530 k=35.
  Carrier/source states: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA, RS50S` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### GTP / GDP / PO4 source-state transition

- **re0000000717** (P1:E06): `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=2.3 (REFERENCE_ENABLED); exact inverse: re0000000718 k=2.1.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000722** (P1:E07): `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_energy_commitment`; author k1=12 (REFERENCE_ENABLED); exact inverse: re0000000746 k=0.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
### Factor release / E1

- **re0000000724** (P1:E08): `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=0.0025 (REFERENCE_ENABLED); exact inverse: re0000000723 k=16.
  Carrier/source states: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF1, RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000755** (P1:E09): `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. Context: `INIT_factor_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000756 k=0.
  Carrier/source states: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3, RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA`. All co-reactants and outputs are in the full equation.
- **re0000000726** (P1:E10): `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU`. Context: `INIT_factor_release`; author k1=4 (REFERENCE_ENABLED); exact inverse: re0000000752 k=200.
  Carrier/source states: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP, elRS70SAGGU0002_fMettRNAfMetCAU`. All co-reactants and outputs are in the full equation.
### E2 cross-module boundary

- **re0000000001** (P2:E2-BRIDGE): `elRS70SAGGU0002_fMettRNAfMetCAU -> elRS70SAGGU0002_fMet + tRNAfMetCAU`. Context: `ELONG_tRNA_release`; author k1=1000 (REFERENCE_ENABLED); exact inverse: re0000000002 k=0.
  Carrier/source states: `elRS70SAGGU0002_fMettRNAfMetCAU` → `elRS70SAGGU0002_fMet, tRNAfMetCAU`. All co-reactants and outputs are in the full equation.
### Conditional first elongation binding

- **re0000000013** (P7:ENCOUNTER): `EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC`. Context: `ELONG_aa_tRNA_delivery`; author k1=140 (REFERENCE_ENABLED); exact inverse: re0000000021 k=0.23.
  Carrier/source states: `EFTu_GTP_GlytRNAGlyGCC, elRS70SAGGU0002_fMet` → `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC`. All co-reactants and outputs are in the full equation.

**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**

```text
EFTu_GTP_GlytRNAGlyGCC + IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> IF2_GDP + PO4 + elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC + tRNAfMetCAU
```

DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):

- `P1:E01` → `P1:E02`: `RS30S_IF3` × 1.
- `P1:E02` → `P1:E03`: `RS30S_IF1_IF3` × 1.
- `P1:E03` → `P1:E04`: `RS30S_IF1_IF3_mRNA` × 1.
- `P1:E04` → `P1:E05`: `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E05` → `P1:E06`: `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E06` → `P1:E07`: `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E07` → `P1:E08`: `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E08` → `P1:E09`: `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E09` → `P1:E10`: `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` × 1.
- `P1:E10` → `P2:E2-BRIDGE`: `elRS70SAGGU0002_fMettRNAfMetCAU` × 1.
- `P2:E2-BRIDGE` → `P7:ENCOUNTER`: `elRS70SAGGU0002_fMet` × 1.

True rejoins: ``. IF2_GDP release is not IF2_GTP recovery. The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.

Competing source exits from this witness's actual precursor states (context only; inverse/sink directions are not extra occurrences):

| Original precursor state | Original outgoing directions (reference k1) |
|---|---|
| `IF1` | re0000000501 (k=20), re0000000503 (k=20), re0000000505 (k=20), re0000000507 (k=20), re0000000509 (k=12), re0000000511 (k=12), re0000000531 (k=20), re0000000533 (k=20), re0000000535 (k=12), re0000000537 (k=16), re0000000539 (k=16), re0000000541 (k=0), re0000000649 (k=20), re0000000651 (k=20), re0000000677 (k=20), re0000000679 (k=20), re0000000683 (k=20), re0000000685 (k=20), re0000000719 (k=16), re0000000723 (k=16), re0000000754 (k=0), re0000000758 (k=0), re0000000766 (k=0) |
| `IF2_GTP_fMettRNAfMetCAU` | re0000000450 (k=40), re0000000454 (k=0), re0000000465 (k=280), re0000000475 (k=280), re0000000497 (k=220), re0000000519 (k=220), re0000000611 (k=280), re0000000623 (k=280), re0000000645 (k=220), re0000000665 (k=220) |
| `IF3` | re0000000457 (k=0.082), re0000000459 (k=1160), re0000000489 (k=0.082), re0000000491 (k=1100), re0000000542 (k=0), re0000000615 (k=1160), re0000000617 (k=1160), re0000000635 (k=1160), re0000000637 (k=1160), re0000000639 (k=1160), re0000000641 (k=1160), re0000000653 (k=1100), re0000000655 (k=1100), re0000000667 (k=1100), re0000000669 (k=1100), re0000000671 (k=1100), re0000000673 (k=1100), re0000000748 (k=0), re0000000756 (k=0), re0000000762 (k=0), re0000000764 (k=0) |
| `RS30S` | re0000000004 (k=0), re0000000456 (k=12), re0000000459 (k=1160), re0000000503 (k=20), re0000000609 (k=280), re0000000611 (k=280), re0000000619 (k=36), re0000000912 (k=0) |
| `RS30S_IF1_IF3` | re0000000492 (k=0.08), re0000000494 (k=0.18), re0000000495 (k=220), re0000000497 (k=220), re0000000508 (k=0.7), re0000000513 (k=36), re0000000559 (k=0), re0000000560 (k=0), re0000000561 (k=0) |
| `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000520 (k=1), re0000000522 (k=0.015), re0000000524 (k=1.5), re0000000528 (k=0.006), re0000000529 (k=34), re0000000538 (k=0.0025), re0000000596 (k=0), re0000000597 (k=0), re0000000598 (k=0), re0000000599 (k=0), re0000000674 (k=0.08) |
| `RS30S_IF1_IF3_mRNA` | re0000000514 (k=0.7), re0000000515 (k=220), re0000000517 (k=5), re0000000519 (k=220), re0000000532 (k=0.7), re0000000568 (k=0), re0000000569 (k=0), re0000000570 (k=0), re0000000668 (k=0.08) |
| `RS30S_IF3` | re0000000460 (k=0.8), re0000000462 (k=0.18), re0000000463 (k=280), re0000000465 (k=280), re0000000469 (k=36), re0000000507 (k=20), re0000000547 (k=0), re0000000548 (k=0) |
| `RS50S` | re0000000003 (k=0), re0000000298 (k=30), re0000000327 (k=0), re0000000456 (k=12), re0000000462 (k=0.18), re0000000485 (k=34), re0000000488 (k=12), re0000000494 (k=0.18), re0000000529 (k=34), re0000000967 (k=0), re0000000968 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | re0000000718 (k=2.1), re0000000720 (k=0.0025), re0000000722 (k=12), re0000000740 (k=0), re0000000741 (k=0), re0000000742 (k=0), re0000000743 (k=0), re0000000744 (k=0) |
| `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000724 (k=0.0025), re0000000731 (k=0), re0000000732 (k=0), re0000000733 (k=0), re0000000734 (k=0), re0000000735 (k=0), re0000000746 (k=0), re0000000747 (k=1000), re0000000749 (k=4) |
| `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | re0000000530 (k=35), re0000000540 (k=0.0025), re0000000604 (k=0), re0000000605 (k=0), re0000000606 (k=0), re0000000607 (k=0), re0000000608 (k=0), re0000000717 (k=2.3) |
| `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000726 (k=4), re0000000756 (k=0), re0000000758 (k=0), re0000000767 (k=0), re0000000768 (k=0), re0000000769 (k=0) |
| `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | re0000000723 (k=16), re0000000725 (k=4), re0000000727 (k=0), re0000000728 (k=0), re0000000729 (k=0), re0000000730 (k=0), re0000000745 (k=0), re0000000755 (k=1000) |
| `elRS70SAGGU0002_fMet` | re0000000002 (k=0), re0000000011 (k=0), re0000000012 (k=0), re0000000013 (k=140), re0000000064 (k=0), re0000000065 (k=0) |
| `elRS70SAGGU0002_fMettRNAfMetCAU` | re0000000001 (k=1000), re0000000009 (k=0), re0000000010 (k=0), re0000000752 (k=200), re0000000764 (k=0), re0000000766 (k=0) |
## Alternatives, competition and source incidence

All outgoing source directions at every retained anchor are listed in JSON `competition_outlets`, including inverse and disabled sink channels. At the GDP dual-factor 70S state, 0747 and 0749 are genuine alternative exits; the release-alt witness fires 0749. No dominance is inferred. 0449/0450 each have k1=40; no inverse occurs automatically. 0420/0422/0288 compete for the single original MettRNAfMetCAU pool; 0289 and all source incidence remain available as context.

The following bounded appendix is excluded from witness sums. It preserves complete source equations, full direction IDs, reverse partners, reviewed contexts and disabled channels. Composite carrier projections remain INFERRED.

| Original ID | Complete source equation | Context / family | Author k1 | Exact inverses | Concrete source subsystem |
|---|---|---|---:|---|---|
| re0000000001 | `elRS70SAGGU0002_fMettRNAfMetCAU -> elRS70SAGGU0002_fMet + tRNAfMetCAU` | ELONG_tRNA_release / RFAM_001 | 1000 (REFERENCE_ENABLED) | re0000000002 |  |
| re0000000002 | `elRS70SAGGU0002_fMet + tRNAfMetCAU -> elRS70SAGGU0002_fMettRNAfMetCAU` | ELONG_tRNA_release / RFAM_001 | 0 (REFERENCE_DISABLED) | re0000000001 |  |
| re0000000003 | `RS50S -> RS50S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000004 | `RS30S -> RS30S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000005 | `fMettRNAfMetCAU -> fMettRNAfMetCAU_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000009 | `elRS70SAGGU0002_fMettRNAfMetCAU -> RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000010 | `elRS70SAGGU0002_fMettRNAfMetCAU -> RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000011 | `elRS70SAGGU0002_fMet -> RS30S + RS50S_degraded + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000012 | `elRS70SAGGU0002_fMet -> RS30S_degraded + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000013 | `EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | ELONG_aa_tRNA_delivery / RFAM_002 | 140 (REFERENCE_ENABLED) | re0000000021 |  |
| re0000000021 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet` | ELONG_aa_tRNA_delivery / RFAM_002 | 0.23 (REFERENCE_ENABLED) | re0000000013 |  |
| re0000000027 | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> GlytRNAGlyGCC + elRS70SAGGU0002_fMet` | ELONG_aa_tRNA_delivery / RFAM_002 | 0 (REFERENCE_DISABLED) | re0000000064 |  |
| re0000000028 | `elRS70SAGGU0002_fMet_EFTu_GDP -> EFTu_GDP + elRS70SAGGU0002_fMet` | ELONG_aa_tRNA_delivery / RFAM_002 | 1000 (REFERENCE_ENABLED) | re0000000065 |  |
| re0000000033 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + RS30S + RS50S_degraded + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000034 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + RS30S_degraded + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000035 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC -> EFTu_degraded + GTP + GlytRNAGlyGCC + RS30S + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000036 | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + RS30S + RS50S_degraded + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000037 | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + RS30S_degraded + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000038 | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + PO4 + RS30S + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000039 | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + RS30S + RS50S_degraded + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000040 | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + RS30S_degraded + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000041 | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + RS30S + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000042 | `elRS70SAGGU0002_fMet_EFTu_GDP -> EFTu + GDP + RS30S + RS50S_degraded + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000043 | `elRS70SAGGU0002_fMet_EFTu_GDP -> EFTu + GDP + RS30S_degraded + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000044 | `elRS70SAGGU0002_fMet_EFTu_GDP -> EFTu_degraded + GDP + RS30S + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000045 | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> GlytRNAGlyGCC + RS30S + RS50S_degraded + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000046 | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC -> GlytRNAGlyGCC + RS30S_degraded + RS50S + fMet + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000047 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC -> Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000048 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC -> Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000049 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP -> EFG + GTP + Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000050 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP -> EFG + GTP + Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000051 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP -> EFG_degraded + GTP + Pept0002tRNAGlyGCC + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000052 | `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP -> EFG + GDP + Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000053 | `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP -> EFG + GDP + Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000054 | `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP -> EFG_degraded + GDP + Pept0002tRNAGlyGCC + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000055 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4 -> EFG + GDP + PO4 + Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000056 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4 -> EFG + GDP + PO4 + Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000057 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4 -> EFG_degraded + GDP + PO4 + Pept0002tRNAGlyGCC + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000058 | `elRS70SAGGU0003_Pept0002tRNAGlyGCC -> Pept0002tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000059 | `elRS70SAGGU0003_Pept0002tRNAGlyGCC -> Pept0002tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000064 | `GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | ELONG_aa_tRNA_delivery / RFAM_002 | 0 (REFERENCE_DISABLED) | re0000000027 |  |
| re0000000065 | `EFTu_GDP + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GDP` | ELONG_aa_tRNA_delivery / RFAM_002 | 0 (REFERENCE_DISABLED) | re0000000028 |  |
| re0000000072 | `elRS70SAGGU0003_Pept0002 -> Pept0002 + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000073 | `elRS70SAGGU0003_Pept0002 -> Pept0002 + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000091 | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000092 | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu + GTP + GlytRNAGlyGCC + Pept0002 + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000093 | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC -> EFTu_degraded + GTP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000094 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + Pept0002 + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000095 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + PO4 + Pept0002 + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000096 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + PO4 + Pept0002 + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000097 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000098 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu + GDP + GlytRNAGlyGCC + Pept0002 + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000099 | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC -> EFTu_degraded + GDP + GlytRNAGlyGCC + Pept0002 + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000100 | `elRS70SAGGU0003_Pept0002_EFTu_GDP -> EFTu + GDP + Pept0002 + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000101 | `elRS70SAGGU0003_Pept0002_EFTu_GDP -> EFTu + GDP + Pept0002 + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000102 | `elRS70SAGGU0003_Pept0002_EFTu_GDP -> EFTu_degraded + GDP + Pept0002 + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000103 | `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> GlytRNAGlyGCC + Pept0002 + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000104 | `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC -> GlytRNAGlyGCC + Pept0002 + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000105 | `elRS70SBGGU0003_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000106 | `elRS70SBGGU0003_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000107 | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP -> EFG + GTP + Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000108 | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP -> EFG + GTP + Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000109 | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP -> EFG_degraded + GTP + Pept0003tRNAGlyGCC + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000110 | `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> EFG + GDP + Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000111 | `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> EFG + GDP + Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000112 | `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP -> EFG_degraded + GDP + Pept0003tRNAGlyGCC + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000113 | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4 -> EFG + GDP + PO4 + Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000114 | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4 -> EFG + GDP + PO4 + Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000115 | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4 -> EFG_degraded + GDP + PO4 + Pept0003tRNAGlyGCC + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000116 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000117 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC -> Pept0003tRNAGlyGCC + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000151 | `Met + MetRS -> MetRS_Met` | RS_binding / RFAM_007 | 5 (REFERENCE_ENABLED) | re0000000156 |  |
| re0000000156 | `MetRS_Met -> Met + MetRS` | RS_binding / RFAM_007 | 350 (REFERENCE_ENABLED) | re0000000151 |  |
| re0000000161 | `ATP + MetRS_Met -> MetRS_Met_ATP` | RS_binding / RFAM_007 | 10 (REFERENCE_ENABLED) | re0000000162 |  |
| re0000000162 | `MetRS_Met_ATP -> ATP + MetRS_Met` | RS_binding / RFAM_007 | 2500 (REFERENCE_ENABLED) | re0000000161 |  |
| re0000000170 | `MetRS_AMP -> AMP + MetRS` | RS_charging / RFAM_008 | 1000 (REFERENCE_ENABLED) | re0000000171 |  |
| re0000000171 | `AMP + MetRS -> MetRS_AMP` | RS_charging / RFAM_008 | 0 (REFERENCE_DISABLED) | re0000000170 |  |
| re0000000218 | `MettRNAfMetCAU -> Met + tRNAfMetCAU` | RS_charging / RFAM_011 | 0 (REFERENCE_DISABLED) | re0000000259 |  |
| re0000000220 | `MetRS_MetAMP_tRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | RS_charging / RFAM_012 | 13.7 (REFERENCE_ENABLED) | re0000000221 |  |
| re0000000221 | `MetRS_AMP_MettRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU` | RS_charging / RFAM_012 | 0 (REFERENCE_DISABLED) | re0000000220 |  |
| re0000000224 | `MetRS_AMP_MettRNAfMetCAU -> MetRS_AMP + MettRNAfMetCAU` | RS_charging / RFAM_012 | 1.685 (REFERENCE_ENABLED) | re0000000225 |  |
| re0000000225 | `MetRS_AMP + MettRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | RS_charging / RFAM_012 | 5.6 (REFERENCE_ENABLED) | re0000000224 |  |
| re0000000226 | `MetRS_MettRNAfMetCAU -> MetRS + MettRNAfMetCAU` | RS_charging / RFAM_012 | 1.685 (REFERENCE_ENABLED) | re0000000227 |  |
| re0000000227 | `MetRS + MettRNAfMetCAU -> MetRS_MettRNAfMetCAU` | RS_charging / RFAM_012 | 5.6 (REFERENCE_ENABLED) | re0000000226 |  |
| re0000000228 | `MetRS_AMP_MettRNAfMetCAU -> AMP + MetRS_degraded + MettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000229 | `MetRS_MettRNAfMetCAU -> MetRS_degraded + MettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000231 | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU + PPi` | RS_activation / RFAM_012 | 1000 (REFERENCE_ENABLED) | re0000000260 |  |
| re0000000239 | `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU` | RS_activation / RFAM_012 | 200 (REFERENCE_ENABLED) | re0000000240 |  |
| re0000000240 | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | RS_activation / RFAM_012 | 0 (REFERENCE_DISABLED) | re0000000239 |  |
| re0000000247 | `MetRS_Met_ATP + tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | RS_binding / RFAM_012 | 50 (REFERENCE_ENABLED) | re0000000248 |  |
| re0000000248 | `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_Met_ATP + tRNAfMetCAU` | RS_binding / RFAM_012 | 150 (REFERENCE_ENABLED) | re0000000247 |  |
| re0000000258 | `MettRNAfMetCAU -> MettRNAfMetCAU_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000259 | `Met + tRNAfMetCAU -> MettRNAfMetCAU` | RS_charging / RFAM_011 | 0 (REFERENCE_DISABLED) | re0000000218 |  |
| re0000000260 | `MetRS_MetAMP_tRNAfMetCAU + PPi -> MetRS_MetAMP_PPi_tRNAfMetCAU` | RS_activation / RFAM_012 | 0 (REFERENCE_DISABLED) | re0000000231 |  |
| re0000000288 | `EFTu_GTP + MettRNAfMetCAU -> EFTu_GTP_MettRNAfMetCAU` | ELONG_aa_tRNA_delivery / RFAM_013 | 1.5 (REFERENCE_ENABLED) | re0000000289 |  |
| re0000000289 | `EFTu_GTP_MettRNAfMetCAU -> EFTu_GTP + MettRNAfMetCAU` | ELONG_aa_tRNA_delivery / RFAM_013 | 0.0453 (REFERENCE_ENABLED) | re0000000288 |  |
| re0000000290 | `EFTu_GTP_MettRNAfMetCAU -> EFTu_degraded + GTP + MettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000298 | `EFG_GTP + RS50S -> RS50S_EFG_GTP` | ELONG_energy_coupling / RFAM_014 | 30 (REFERENCE_ENABLED) | re0000000299 |  |
| re0000000299 | `RS50S_EFG_GTP -> EFG_GTP + RS50S` | ELONG_energy_coupling / RFAM_014 | 25 (REFERENCE_ENABLED) | re0000000298 |  |
| re0000000300 | `EFG_GTP + RS70S -> RS70S_EFG_GTP` | ELONG_energy_coupling / RFAM_014 | 30 (REFERENCE_ENABLED) | re0000000301 |  |
| re0000000301 | `RS70S_EFG_GTP -> EFG_GTP + RS70S` | ELONG_energy_coupling / RFAM_014 | 25 (REFERENCE_ENABLED) | re0000000300 |  |
| re0000000308 | `RS50S_EFG_GDP -> EFG_GDP + RS50S` | ELONG_energy_coupling;RECYCLE_component_release / RFAM_014 | 1000 (REFERENCE_ENABLED) | re0000000327 |  |
| re0000000309 | `RS70S_EFG_GDP -> EFG_GDP + RS70S` | ELONG_energy_coupling / RFAM_014 | 1000 (REFERENCE_ENABLED) | re0000000328 |  |
| re0000000310 | `RS50S_EFG_GTP -> EFG_degraded + GTP + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000312 | `RS50S_EFG_GDP_PO4 -> EFG_degraded + GDP + PO4 + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000314 | `RS50S_EFG_GDP -> EFG_degraded + GDP + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000316 | `RS70S_EFG_GTP -> EFG_degraded + GTP + RS30S + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000317 | `RS70S_EFG_GTP -> EFG + GTP + RS30S + RS50S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000318 | `RS70S_EFG_GDP_PO4 -> EFG_degraded + GDP + PO4 + RS30S + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000319 | `RS70S_EFG_GDP_PO4 -> EFG + GDP + PO4 + RS30S + RS50S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000320 | `RS70S_EFG_GTP -> EFG + GTP + RS30S_degraded + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000321 | `RS70S_EFG_GDP_PO4 -> EFG + GDP + PO4 + RS30S_degraded + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000322 | `RS70S_EFG_GDP -> EFG + GDP + RS30S + RS50S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000323 | `RS70S_EFG_GDP -> EFG_degraded + GDP + RS30S + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000324 | `RS70S_EFG_GDP -> EFG + GDP + RS30S_degraded + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000327 | `EFG_GDP + RS50S -> RS50S_EFG_GDP` | ELONG_energy_coupling;RECYCLE_component_release / RFAM_014 | 0 (REFERENCE_DISABLED) | re0000000308 |  |
| re0000000328 | `EFG_GDP + RS70S -> RS70S_EFG_GDP` | ELONG_energy_coupling / RFAM_014 | 0 (REFERENCE_DISABLED) | re0000000309 |  |
| re0000000414 | `PPiase_PO4_PO4 -> 2 PO4 + PPiase_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000417 | `fMettRNAfMetCAU -> fMet + tRNAfMetCAU` | RS_to_INIT_formylation / RFAM_019 | 0 (REFERENCE_DISABLED) | re0000000443 |  |
| re0000000418 | `FD + MTF -> MTF_FD` | RS_to_INIT_formylation / RFAM_020 | 74.07407407 (REFERENCE_ENABLED) | re0000000419 |  |
| re0000000419 | `MTF_FD -> FD + MTF` | RS_to_INIT_formylation / RFAM_020 | 1000 (REFERENCE_ENABLED) | re0000000418 |  |
| re0000000420 | `MTF + MettRNAfMetCAU -> MTF_MettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 2000 (REFERENCE_ENABLED) | re0000000421 |  |
| re0000000421 | `MTF_MettRNAfMetCAU -> MTF + MettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 1000 (REFERENCE_ENABLED) | re0000000420 |  |
| re0000000422 | `MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 2000 (REFERENCE_ENABLED) | re0000000423 |  |
| re0000000423 | `MTF_FD_MettRNAfMetCAU -> MTF_FD + MettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 1000 (REFERENCE_ENABLED) | re0000000422 |  |
| re0000000426 | `MTF_FD_MettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 37.3 (REFERENCE_ENABLED) | re0000000427 |  |
| re0000000427 | `MTF_THF_fMettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 0 (REFERENCE_DISABLED) | re0000000426 |  |
| re0000000428 | `MTF_THF_fMettRNAfMetCAU -> MTF_THF + fMettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 1000 (REFERENCE_ENABLED) | re0000000429 |  |
| re0000000429 | `MTF_THF + fMettRNAfMetCAU -> MTF_THF_fMettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 0 (REFERENCE_DISABLED) | re0000000428 |  |
| re0000000432 | `MTF_fMettRNAfMetCAU -> MTF + fMettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 1000 (REFERENCE_ENABLED) | re0000000433 |  |
| re0000000433 | `MTF + fMettRNAfMetCAU -> MTF_fMettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_020 | 0 (REFERENCE_DISABLED) | re0000000432 |  |
| re0000000434 | `MTF_THF -> MTF + THF` | RS_to_INIT_formylation / RFAM_020 | 1000 (REFERENCE_ENABLED) | re0000000435 |  |
| re0000000435 | `MTF + THF -> MTF_THF` | RS_to_INIT_formylation / RFAM_020 | 0 (REFERENCE_DISABLED) | re0000000434 |  |
| re0000000437 | `MTF_MettRNAfMetCAU -> MTF_degraded + MettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000438 | `MTF_FD_MettRNAfMetCAU -> FD + MTF_degraded + MettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000439 | `MTF_THF_fMettRNAfMetCAU -> MTF_degraded + THF + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000440 | `MTF_fMettRNAfMetCAU -> MTF_degraded + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000443 | `fMet + tRNAfMetCAU -> fMettRNAfMetCAU` | RS_to_INIT_formylation / RFAM_019 | 0 (REFERENCE_DISABLED) | re0000000417 |  |
| re0000000445 | `GTP + IF2 -> IF2_GTP` | INIT_energy_commitment / RFAM_022 | 10 (REFERENCE_ENABLED) | re0000000446 |  |
| re0000000446 | `IF2_GTP -> GTP + IF2` | INIT_energy_commitment / RFAM_022 | 67 (REFERENCE_ENABLED) | re0000000445 |  |
| re0000000447 | `GDP + IF2 -> IF2_GDP` | INIT_energy_commitment / RFAM_023 | 10 (REFERENCE_ENABLED) | re0000000448 |  |
| re0000000448 | `IF2_GDP -> GDP + IF2` | INIT_energy_commitment / RFAM_023 | 16 (REFERENCE_ENABLED) | re0000000447 |  |
| re0000000449 | `IF2_GTP + fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_022 | 40 (REFERENCE_ENABLED) | re0000000450 |  |
| re0000000450 | `IF2_GTP_fMettRNAfMetCAU -> IF2_GTP + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_022 | 40 (REFERENCE_ENABLED) | re0000000449 |  |
| re0000000451 | `IF2 -> IF2_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000452 | `IF2_GDP -> GDP + IF2_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000453 | `IF2_GTP -> GTP + IF2_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000454 | `IF2_GTP_fMettRNAfMetCAU -> GTP + IF2_degraded + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000455 | `RS70S -> RS30S + RS50S` | INIT_70S_formation / RFAM_024 | 0.012 (REFERENCE_ENABLED) | re0000000456 |  |
| re0000000456 | `RS30S + RS50S -> RS70S` | INIT_70S_formation / RFAM_024 | 12 (REFERENCE_ENABLED) | re0000000455 |  |
| re0000000457 | `IF3 + RS70S -> RS70S_IF3` | INIT_assembly / RFAM_025 | 0.082 (REFERENCE_ENABLED) | re0000000458 |  |
| re0000000458 | `RS70S_IF3 -> IF3 + RS70S` | INIT_assembly / RFAM_025 | 0.26 (REFERENCE_ENABLED) | re0000000457 |  |
| re0000000459 | `IF3 + RS30S -> RS30S_IF3` | INIT_assembly / RFAM_025 | 1160 (REFERENCE_ENABLED) | re0000000460 |  |
| re0000000460 | `RS30S_IF3 -> IF3 + RS30S` | INIT_assembly / RFAM_025 | 0.8 (REFERENCE_ENABLED) | re0000000459 |  |
| re0000000461 | `RS70S_IF3 -> RS30S_IF3 + RS50S` | INIT_70S_formation / RFAM_025 | 0.0068 (REFERENCE_ENABLED) | re0000000462 |  |
| re0000000462 | `RS30S_IF3 + RS50S -> RS70S_IF3` | INIT_70S_formation / RFAM_025 | 0.18 (REFERENCE_ENABLED) | re0000000461 |  |
| re0000000463 | `IF2_GTP + RS30S_IF3 -> RS30S_IF3_IF2_GTP` | INIT_assembly / RFAM_025 | 280 (REFERENCE_ENABLED) | re0000000464 |  |
| re0000000464 | `RS30S_IF3_IF2_GTP -> IF2_GTP + RS30S_IF3` | INIT_assembly / RFAM_025 | 12 (REFERENCE_ENABLED) | re0000000463 |  |
| re0000000465 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF3 -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 280 (REFERENCE_ENABLED) | re0000000466 |  |
| re0000000466 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF3` | INIT_tRNA_recruitment / RFAM_025 | 1.5 (REFERENCE_ENABLED) | re0000000465 |  |
| re0000000467 | `RS30S_IF3_IF2_GTP + fMettRNAfMetCAU -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 5 (REFERENCE_ENABLED) | re0000000468 |  |
| re0000000468 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF3_IF2_GTP + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 1.5 (REFERENCE_ENABLED) | re0000000467 |  |
| re0000000469 | `RS30S_IF3 + mRNA -> RS30S_IF3_mRNA` | INIT_assembly / RFAM_025 | 36 (REFERENCE_ENABLED) | re0000000470 |  |
| re0000000470 | `RS30S_IF3_mRNA -> RS30S_IF3 + mRNA` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000469 |  |
| re0000000471 | `IF2_GTP + RS30S_IF3_mRNA -> RS30S_IF3_IF2_GTP_mRNA` | INIT_assembly / RFAM_025 | 280 (REFERENCE_ENABLED) | re0000000472 |  |
| re0000000472 | `RS30S_IF3_IF2_GTP_mRNA -> IF2_GTP + RS30S_IF3_mRNA` | INIT_assembly / RFAM_025 | 12 (REFERENCE_ENABLED) | re0000000471 |  |
| re0000000473 | `RS30S_IF3_mRNA + fMettRNAfMetCAU -> RS30S_IF3_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_025 | 5 (REFERENCE_ENABLED) | re0000000474 |  |
| re0000000474 | `RS30S_IF3_fMettRNAfMetCAU_mRNA -> RS30S_IF3_mRNA + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 1.5 (REFERENCE_ENABLED) | re0000000473 |  |
| re0000000475 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF3_mRNA -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_025 | 280 (REFERENCE_ENABLED) | re0000000476 |  |
| re0000000476 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF3_mRNA` | INIT_tRNA_recruitment / RFAM_025 | 1.5 (REFERENCE_ENABLED) | re0000000475 |  |
| re0000000477 | `IF2_GTP + RS30S_IF3_fMettRNAfMetCAU_mRNA -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 280 (REFERENCE_ENABLED) | re0000000478 |  |
| re0000000478 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP + RS30S_IF3_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 12 (REFERENCE_ENABLED) | re0000000477 |  |
| re0000000479 | `RS30S_IF3_IF2_GTP_mRNA + fMettRNAfMetCAU -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_025 | 5 (REFERENCE_ENABLED) | re0000000480 |  |
| re0000000480 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF3_IF2_GTP_mRNA + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 1.5 (REFERENCE_ENABLED) | re0000000479 |  |
| re0000000481 | `RS30S_IF3_IF2_GTP + mRNA -> RS30S_IF3_IF2_GTP_mRNA` | INIT_assembly / RFAM_025 | 36 (REFERENCE_ENABLED) | re0000000482 |  |
| re0000000482 | `RS30S_IF3_IF2_GTP_mRNA -> RS30S_IF3_IF2_GTP + mRNA` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000481 |  |
| re0000000483 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU + mRNA -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 36 (REFERENCE_ENABLED) | re0000000484 |  |
| re0000000484 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU + mRNA` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000483 |  |
| re0000000485 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_70S_formation / RFAM_025 | 34 (REFERENCE_ENABLED) | re0000000486 |  |
| re0000000486 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S` | INIT_70S_formation / RFAM_025 | 35 (REFERENCE_ENABLED) | re0000000485 |  |
| re0000000487 | `RS70S_IF1 -> RS30S_IF1 + RS50S` | INIT_70S_formation / RFAM_025 | 0.012 (REFERENCE_ENABLED) | re0000000488 |  |
| re0000000488 | `RS30S_IF1 + RS50S -> RS70S_IF1` | INIT_70S_formation / RFAM_025 | 12 (REFERENCE_ENABLED) | re0000000487 |  |
| re0000000489 | `IF3 + RS70S_IF1 -> RS70S_IF1_IF3` | INIT_assembly / RFAM_025 | 0.082 (REFERENCE_ENABLED) | re0000000490 |  |
| re0000000490 | `RS70S_IF1_IF3 -> IF3 + RS70S_IF1` | INIT_assembly / RFAM_025 | 0.26 (REFERENCE_ENABLED) | re0000000489 |  |
| re0000000491 | `IF3 + RS30S_IF1 -> RS30S_IF1_IF3` | INIT_assembly / RFAM_025 | 1100 (REFERENCE_ENABLED) | re0000000492 |  |
| re0000000492 | `RS30S_IF1_IF3 -> IF3 + RS30S_IF1` | INIT_assembly / RFAM_025 | 0.08 (REFERENCE_ENABLED) | re0000000491 |  |
| re0000000493 | `RS70S_IF1_IF3 -> RS30S_IF1_IF3 + RS50S` | INIT_70S_formation / RFAM_025 | 0.0068 (REFERENCE_ENABLED) | re0000000494 |  |
| re0000000494 | `RS30S_IF1_IF3 + RS50S -> RS70S_IF1_IF3` | INIT_70S_formation / RFAM_025 | 0.18 (REFERENCE_ENABLED) | re0000000493 |  |
| re0000000495 | `IF2_GTP + RS30S_IF1_IF3 -> RS30S_IF1_IF3_IF2_GTP` | INIT_assembly / RFAM_025 | 220 (REFERENCE_ENABLED) | re0000000496 |  |
| re0000000496 | `RS30S_IF1_IF3_IF2_GTP -> IF2_GTP + RS30S_IF1_IF3` | INIT_assembly / RFAM_025 | 1 (REFERENCE_ENABLED) | re0000000495 |  |
| re0000000497 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3 -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 220 (REFERENCE_ENABLED) | re0000000498 |  |
| re0000000498 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3` | INIT_tRNA_recruitment / RFAM_025 | 1 (REFERENCE_ENABLED) | re0000000497 |  |
| re0000000499 | `RS30S_IF1_IF3_IF2_GTP + fMettRNAfMetCAU -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 5 (REFERENCE_ENABLED) | re0000000500 |  |
| re0000000500 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF1_IF3_IF2_GTP + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 1.5 (REFERENCE_ENABLED) | re0000000499 |  |
| re0000000501 | `IF1 + RS70S -> RS70S_IF1` | INIT_assembly / RFAM_025 | 20 (REFERENCE_ENABLED) | re0000000502 |  |
| re0000000502 | `RS70S_IF1 -> IF1 + RS70S` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000501 |  |
| re0000000503 | `IF1 + RS30S -> RS30S_IF1` | INIT_assembly / RFAM_025 | 20 (REFERENCE_ENABLED) | re0000000504 |  |
| re0000000504 | `RS30S_IF1 -> IF1 + RS30S` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000503 |  |
| re0000000505 | `IF1 + RS70S_IF3 -> RS70S_IF1_IF3` | INIT_assembly / RFAM_025 | 20 (REFERENCE_ENABLED) | re0000000506 |  |
| re0000000506 | `RS70S_IF1_IF3 -> IF1 + RS70S_IF3` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000505 |  |
| re0000000507 | `IF1 + RS30S_IF3 -> RS30S_IF1_IF3` | INIT_assembly / RFAM_025 | 20 (REFERENCE_ENABLED) | re0000000508 |  |
| re0000000508 | `RS30S_IF1_IF3 -> IF1 + RS30S_IF3` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000507 |  |
| re0000000509 | `IF1 + RS30S_IF3_IF2_GTP -> RS30S_IF1_IF3_IF2_GTP` | INIT_assembly / RFAM_025 | 12 (REFERENCE_ENABLED) | re0000000510 |  |
| re0000000510 | `RS30S_IF1_IF3_IF2_GTP -> IF1 + RS30S_IF3_IF2_GTP` | INIT_assembly / RFAM_025 | 0.02 (REFERENCE_ENABLED) | re0000000509 |  |
| re0000000511 | `IF1 + RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | INIT_assembly / RFAM_025 | 12 (REFERENCE_ENABLED) | re0000000512 |  |
| re0000000512 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> IF1 + RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | INIT_assembly / RFAM_025 | 0.02 (REFERENCE_ENABLED) | re0000000511 |  |
| re0000000513 | `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA` | INIT_assembly / RFAM_025 | 36 (REFERENCE_ENABLED) | re0000000514 |  |
| re0000000514 | `RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3 + mRNA` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000513 |  |
| re0000000515 | `IF2_GTP + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_mRNA` | INIT_assembly / RFAM_025 | 220 (REFERENCE_ENABLED) | re0000000516 |  |
| re0000000516 | `RS30S_IF1_IF3_IF2_GTP_mRNA -> IF2_GTP + RS30S_IF1_IF3_mRNA` | INIT_assembly / RFAM_025 | 1 (REFERENCE_ENABLED) | re0000000515 |  |
| re0000000517 | `RS30S_IF1_IF3_mRNA + fMettRNAfMetCAU -> RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_025 | 5 (REFERENCE_ENABLED) | re0000000518 |  |
| re0000000518 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_mRNA + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 1.5 (REFERENCE_ENABLED) | re0000000517 |  |
| re0000000519 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_025 | 220 (REFERENCE_ENABLED) | re0000000520 |  |
| re0000000520 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA` | INIT_tRNA_recruitment / RFAM_025 | 1 (REFERENCE_ENABLED) | re0000000519 |  |
| re0000000521 | `IF2_GTP + RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 320 (REFERENCE_ENABLED) | re0000000522 |  |
| re0000000522 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP + RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 0.015 (REFERENCE_ENABLED) | re0000000521 |  |
| re0000000523 | `RS30S_IF1_IF3_IF2_GTP_mRNA + fMettRNAfMetCAU -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_025 | 5 (REFERENCE_ENABLED) | re0000000524 |  |
| re0000000524 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_IF2_GTP_mRNA + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_025 | 1.5 (REFERENCE_ENABLED) | re0000000523 |  |
| re0000000525 | `RS30S_IF1_IF3_IF2_GTP + mRNA -> RS30S_IF1_IF3_IF2_GTP_mRNA` | INIT_assembly / RFAM_025 | 36 (REFERENCE_ENABLED) | re0000000526 |  |
| re0000000526 | `RS30S_IF1_IF3_IF2_GTP_mRNA -> RS30S_IF1_IF3_IF2_GTP + mRNA` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000525 |  |
| re0000000527 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU + mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 36 (REFERENCE_ENABLED) | re0000000528 |  |
| re0000000528 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU + mRNA` | INIT_assembly / RFAM_025 | 0.006 (REFERENCE_ENABLED) | re0000000527 |  |
| re0000000529 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_70S_formation / RFAM_025 | 34 (REFERENCE_ENABLED) | re0000000530 |  |
| re0000000530 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S` | INIT_70S_formation / RFAM_025 | 35 (REFERENCE_ENABLED) | re0000000529 |  |
| re0000000531 | `IF1 + RS30S_IF3_mRNA -> RS30S_IF1_IF3_mRNA` | INIT_assembly / RFAM_025 | 20 (REFERENCE_ENABLED) | re0000000532 |  |
| re0000000532 | `RS30S_IF1_IF3_mRNA -> IF1 + RS30S_IF3_mRNA` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000531 |  |
| re0000000533 | `IF1 + RS30S_IF3_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 20 (REFERENCE_ENABLED) | re0000000534 |  |
| re0000000534 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + RS30S_IF3_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 0.7 (REFERENCE_ENABLED) | re0000000533 |  |
| re0000000535 | `IF1 + RS30S_IF3_IF2_GTP_mRNA -> RS30S_IF1_IF3_IF2_GTP_mRNA` | INIT_assembly / RFAM_025 | 12 (REFERENCE_ENABLED) | re0000000536 |  |
| re0000000536 | `RS30S_IF1_IF3_IF2_GTP_mRNA -> IF1 + RS30S_IF3_IF2_GTP_mRNA` | INIT_assembly / RFAM_025 | 0.02 (REFERENCE_ENABLED) | re0000000535 |  |
| re0000000537 | `IF1 + RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 16 (REFERENCE_ENABLED) | re0000000538 |  |
| re0000000538 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF1 + RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_025 | 0.0025 (REFERENCE_ENABLED) | re0000000537 |  |
| re0000000539 | `IF1 + RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 16 (REFERENCE_ENABLED) | re0000000540 |  |
| re0000000540 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0.0025 (REFERENCE_ENABLED) | re0000000539 |  |
| re0000000541 | `IF1 -> IF1_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000542 | `IF3 -> IF3_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000543 | `RS70S -> RS30S_degraded + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000544 | `RS70S -> RS30S + RS50S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000545 | `RS30S_IF1 -> IF1_degraded + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000546 | `RS30S_IF1 -> IF1 + RS30S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000547 | `RS30S_IF3 -> IF3_degraded + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000548 | `RS30S_IF3 -> IF3 + RS30S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000549 | `RS30S_IF3_mRNA -> IF3_degraded + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000550 | `RS30S_IF3_mRNA -> IF3 + RS30S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000551 | `RS30S_IF3_fMettRNAfMetCAU_mRNA -> IF3_degraded + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000552 | `RS30S_IF3_fMettRNAfMetCAU_mRNA -> IF3 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000553 | `RS70S_IF3 -> IF3 + RS30S_degraded + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000554 | `RS70S_IF3 -> IF3 + RS30S + RS50S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000555 | `RS70S_IF3 -> IF3_degraded + RS30S + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000556 | `RS70S_IF1 -> IF1 + RS30S_degraded + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000557 | `RS70S_IF1 -> IF1 + RS30S + RS50S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000558 | `RS70S_IF1 -> IF1_degraded + RS30S + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000559 | `RS30S_IF1_IF3 -> IF1 + IF3_degraded + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000560 | `RS30S_IF1_IF3 -> IF1 + IF3 + RS30S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000561 | `RS30S_IF1_IF3 -> IF1_degraded + IF3 + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000562 | `RS30S_IF3_IF2_GTP -> GTP + IF2 + IF3 + RS30S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000563 | `RS30S_IF3_IF2_GTP -> GTP + IF2_degraded + IF3 + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000564 | `RS30S_IF3_IF2_GTP -> GTP + IF2 + IF3_degraded + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000565 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2 + IF3 + RS30S_degraded + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000566 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2_degraded + IF3 + RS30S + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000567 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2 + IF3_degraded + RS30S + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000568 | `RS30S_IF1_IF3_mRNA -> IF1 + IF3_degraded + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000569 | `RS30S_IF1_IF3_mRNA -> IF1 + IF3 + RS30S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000570 | `RS30S_IF1_IF3_mRNA -> IF1_degraded + IF3 + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000571 | `RS30S_IF3_IF2_GTP_mRNA -> GTP + IF2 + IF3 + RS30S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000572 | `RS30S_IF3_IF2_GTP_mRNA -> GTP + IF2 + IF3_degraded + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000573 | `RS30S_IF3_IF2_GTP_mRNA -> GTP + IF2_degraded + IF3 + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000574 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3_degraded + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000575 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000576 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1_degraded + IF3 + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000577 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000578 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2_degraded + IF3 + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000579 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3_degraded + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000580 | `RS70S_IF1_IF3 -> IF1 + IF3_degraded + RS30S + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000581 | `RS70S_IF1_IF3 -> IF1 + IF3 + RS30S + RS50S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000582 | `RS70S_IF1_IF3 -> IF1_degraded + IF3 + RS30S + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000583 | `RS70S_IF1_IF3 -> IF1 + IF3 + RS30S_degraded + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000584 | `RS30S_IF1_IF3_IF2_GTP -> GTP + IF1 + IF2 + IF3_degraded + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000585 | `RS30S_IF1_IF3_IF2_GTP -> GTP + IF1 + IF2_degraded + IF3 + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000586 | `RS30S_IF1_IF3_IF2_GTP -> GTP + IF1_degraded + IF2 + IF3 + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000587 | `RS30S_IF1_IF3_IF2_GTP -> GTP + IF1 + IF2 + IF3 + RS30S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000588 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2 + IF3_degraded + RS30S + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000589 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2_degraded + IF3 + RS30S + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000590 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1_degraded + IF2 + IF3 + RS30S + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000591 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2 + IF3 + RS30S_degraded + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000592 | `RS30S_IF1_IF3_IF2_GTP_mRNA -> GTP + IF1 + IF2 + IF3_degraded + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000593 | `RS30S_IF1_IF3_IF2_GTP_mRNA -> GTP + IF1 + IF2 + IF3 + RS30S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000594 | `RS30S_IF1_IF3_IF2_GTP_mRNA -> GTP + IF1 + IF2_degraded + IF3 + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000595 | `RS30S_IF1_IF3_IF2_GTP_mRNA -> GTP + IF1_degraded + IF2 + IF3 + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000596 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3_degraded + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000597 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000598 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2_degraded + IF3 + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000599 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1_degraded + IF2 + IF3 + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000600 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000601 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000602 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000603 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000604 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000605 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000606 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000607 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1_degraded + IF2 + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000608 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000609 | `IF2_GTP + RS30S -> RS30S_IF2_GTP` | INIT_assembly / RFAM_026 | 280 (REFERENCE_ENABLED) | re0000000610 |  |
| re0000000610 | `RS30S_IF2_GTP -> IF2_GTP + RS30S` | INIT_assembly / RFAM_026 | 12 (REFERENCE_ENABLED) | re0000000609 |  |
| re0000000611 | `IF2_GTP_fMettRNAfMetCAU + RS30S -> RS30S_IF2_GTP_fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 280 (REFERENCE_ENABLED) | re0000000612 |  |
| re0000000612 | `RS30S_IF2_GTP_fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU + RS30S` | INIT_tRNA_recruitment / RFAM_026 | 1.5 (REFERENCE_ENABLED) | re0000000611 |  |
| re0000000613 | `RS30S_IF2_GTP + fMettRNAfMetCAU -> RS30S_IF2_GTP_fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 5 (REFERENCE_ENABLED) | re0000000614 |  |
| re0000000614 | `RS30S_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF2_GTP + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 1.5 (REFERENCE_ENABLED) | re0000000613 |  |
| re0000000615 | `IF3 + RS30S_IF2_GTP -> RS30S_IF3_IF2_GTP` | INIT_assembly / RFAM_026 | 1160 (REFERENCE_ENABLED) | re0000000616 |  |
| re0000000616 | `RS30S_IF3_IF2_GTP -> IF3 + RS30S_IF2_GTP` | INIT_assembly / RFAM_026 | 0.8 (REFERENCE_ENABLED) | re0000000615 |  |
| re0000000617 | `IF3 + RS30S_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | INIT_assembly / RFAM_026 | 1160 (REFERENCE_ENABLED) | re0000000618 |  |
| re0000000618 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU -> IF3 + RS30S_IF2_GTP_fMettRNAfMetCAU` | INIT_assembly / RFAM_026 | 0.8 (REFERENCE_ENABLED) | re0000000617 |  |
| re0000000619 | `RS30S + mRNA -> RS30S_mRNA` | INIT_assembly / RFAM_026 | 36 (REFERENCE_ENABLED) | re0000000620 |  |
| re0000000620 | `RS30S_mRNA -> RS30S + mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000619 |  |
| re0000000621 | `RS30S_mRNA + fMettRNAfMetCAU -> RS30S_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_026 | 5 (REFERENCE_ENABLED) | re0000000622 |  |
| re0000000622 | `RS30S_fMettRNAfMetCAU_mRNA -> RS30S_mRNA + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 1.5 (REFERENCE_ENABLED) | re0000000621 |  |
| re0000000623 | `IF2_GTP_fMettRNAfMetCAU + RS30S_mRNA -> RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_026 | 280 (REFERENCE_ENABLED) | re0000000624 |  |
| re0000000624 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP_fMettRNAfMetCAU + RS30S_mRNA` | INIT_tRNA_recruitment / RFAM_026 | 1.5 (REFERENCE_ENABLED) | re0000000623 |  |
| re0000000625 | `IF2_GTP + RS30S_mRNA -> RS30S_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 280 (REFERENCE_ENABLED) | re0000000626 |  |
| re0000000626 | `RS30S_IF2_GTP_mRNA -> IF2_GTP + RS30S_mRNA` | INIT_assembly / RFAM_026 | 12 (REFERENCE_ENABLED) | re0000000625 |  |
| re0000000627 | `IF2_GTP + RS30S_fMettRNAfMetCAU_mRNA -> RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 280 (REFERENCE_ENABLED) | re0000000628 |  |
| re0000000628 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP + RS30S_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 12 (REFERENCE_ENABLED) | re0000000627 |  |
| re0000000629 | `RS30S_IF2_GTP_mRNA + fMettRNAfMetCAU -> RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_026 | 5 (REFERENCE_ENABLED) | re0000000630 |  |
| re0000000630 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF2_GTP_mRNA + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 1.5 (REFERENCE_ENABLED) | re0000000629 |  |
| re0000000631 | `RS30S_IF2_GTP + mRNA -> RS30S_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 36 (REFERENCE_ENABLED) | re0000000632 |  |
| re0000000632 | `RS30S_IF2_GTP_mRNA -> RS30S_IF2_GTP + mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000631 |  |
| re0000000633 | `RS30S_IF2_GTP_fMettRNAfMetCAU + mRNA -> RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 36 (REFERENCE_ENABLED) | re0000000634 |  |
| re0000000634 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF2_GTP_fMettRNAfMetCAU + mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000633 |  |
| re0000000635 | `IF3 + RS30S_mRNA -> RS30S_IF3_mRNA` | INIT_assembly / RFAM_026 | 1160 (REFERENCE_ENABLED) | re0000000636 |  |
| re0000000636 | `RS30S_IF3_mRNA -> IF3 + RS30S_mRNA` | INIT_assembly / RFAM_026 | 0.8 (REFERENCE_ENABLED) | re0000000635 |  |
| re0000000637 | `IF3 + RS30S_fMettRNAfMetCAU_mRNA -> RS30S_IF3_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 1160 (REFERENCE_ENABLED) | re0000000638 |  |
| re0000000638 | `RS30S_IF3_fMettRNAfMetCAU_mRNA -> IF3 + RS30S_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 0.8 (REFERENCE_ENABLED) | re0000000637 |  |
| re0000000639 | `IF3 + RS30S_IF2_GTP_mRNA -> RS30S_IF3_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 1160 (REFERENCE_ENABLED) | re0000000640 |  |
| re0000000640 | `RS30S_IF3_IF2_GTP_mRNA -> IF3 + RS30S_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 0.8 (REFERENCE_ENABLED) | re0000000639 |  |
| re0000000641 | `IF3 + RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 1160 (REFERENCE_ENABLED) | re0000000642 |  |
| re0000000642 | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF3 + RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 0.8 (REFERENCE_ENABLED) | re0000000641 |  |
| re0000000643 | `IF2_GTP + RS30S_IF1 -> RS30S_IF1_IF2_GTP` | INIT_assembly / RFAM_026 | 220 (REFERENCE_ENABLED) | re0000000644 |  |
| re0000000644 | `RS30S_IF1_IF2_GTP -> IF2_GTP + RS30S_IF1` | INIT_assembly / RFAM_026 | 1 (REFERENCE_ENABLED) | re0000000643 |  |
| re0000000645 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1 -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 220 (REFERENCE_ENABLED) | re0000000646 |  |
| re0000000646 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF1` | INIT_tRNA_recruitment / RFAM_026 | 1 (REFERENCE_ENABLED) | re0000000645 |  |
| re0000000647 | `RS30S_IF1_IF2_GTP + fMettRNAfMetCAU -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 5 (REFERENCE_ENABLED) | re0000000648 |  |
| re0000000648 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF1_IF2_GTP + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 1.5 (REFERENCE_ENABLED) | re0000000647 |  |
| re0000000649 | `IF1 + RS30S_IF2_GTP -> RS30S_IF1_IF2_GTP` | INIT_assembly / RFAM_026 | 20 (REFERENCE_ENABLED) | re0000000650 |  |
| re0000000650 | `RS30S_IF1_IF2_GTP -> IF1 + RS30S_IF2_GTP` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000649 |  |
| re0000000651 | `IF1 + RS30S_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | INIT_assembly / RFAM_026 | 20 (REFERENCE_ENABLED) | re0000000652 |  |
| re0000000652 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> IF1 + RS30S_IF2_GTP_fMettRNAfMetCAU` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000651 |  |
| re0000000653 | `IF3 + RS30S_IF1_IF2_GTP -> RS30S_IF1_IF3_IF2_GTP` | INIT_assembly / RFAM_026 | 1100 (REFERENCE_ENABLED) | re0000000654 |  |
| re0000000654 | `RS30S_IF1_IF3_IF2_GTP -> IF3 + RS30S_IF1_IF2_GTP` | INIT_assembly / RFAM_026 | 0.08 (REFERENCE_ENABLED) | re0000000653 |  |
| re0000000655 | `IF3 + RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | INIT_assembly / RFAM_026 | 1100 (REFERENCE_ENABLED) | re0000000656 |  |
| re0000000656 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU -> IF3 + RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | INIT_assembly / RFAM_026 | 0.08 (REFERENCE_ENABLED) | re0000000655 |  |
| re0000000657 | `IF2_GTP + RS30S_IF1_mRNA -> RS30S_IF1_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 220 (REFERENCE_ENABLED) | re0000000658 |  |
| re0000000658 | `RS30S_IF1_IF2_GTP_mRNA -> IF2_GTP + RS30S_IF1_mRNA` | INIT_assembly / RFAM_026 | 1 (REFERENCE_ENABLED) | re0000000657 |  |
| re0000000659 | `RS30S_IF1_mRNA + fMettRNAfMetCAU -> RS30S_IF1_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_026 | 5 (REFERENCE_ENABLED) | re0000000660 |  |
| re0000000660 | `RS30S_IF1_fMettRNAfMetCAU_mRNA -> RS30S_IF1_mRNA + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 1.5 (REFERENCE_ENABLED) | re0000000659 |  |
| re0000000661 | `RS30S_IF1_IF2_GTP_mRNA + fMettRNAfMetCAU -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_026 | 5 (REFERENCE_ENABLED) | re0000000662 |  |
| re0000000662 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF2_GTP_mRNA + fMettRNAfMetCAU` | INIT_tRNA_recruitment / RFAM_026 | 1.5 (REFERENCE_ENABLED) | re0000000661 |  |
| re0000000663 | `IF2_GTP + RS30S_IF1_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 220 (REFERENCE_ENABLED) | re0000000664 |  |
| re0000000664 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP + RS30S_IF1_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 1 (REFERENCE_ENABLED) | re0000000663 |  |
| re0000000665 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_mRNA -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment / RFAM_026 | 220 (REFERENCE_ENABLED) | re0000000666 |  |
| re0000000666 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_mRNA` | INIT_tRNA_recruitment / RFAM_026 | 1 (REFERENCE_ENABLED) | re0000000665 |  |
| re0000000667 | `IF3 + RS30S_IF1_mRNA -> RS30S_IF1_IF3_mRNA` | INIT_assembly / RFAM_026 | 1100 (REFERENCE_ENABLED) | re0000000668 |  |
| re0000000668 | `RS30S_IF1_IF3_mRNA -> IF3 + RS30S_IF1_mRNA` | INIT_assembly / RFAM_026 | 0.08 (REFERENCE_ENABLED) | re0000000667 |  |
| re0000000669 | `IF3 + RS30S_IF1_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 1100 (REFERENCE_ENABLED) | re0000000670 |  |
| re0000000670 | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF3 + RS30S_IF1_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 0.08 (REFERENCE_ENABLED) | re0000000669 |  |
| re0000000671 | `IF3 + RS30S_IF1_IF2_GTP_mRNA -> RS30S_IF1_IF3_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 1100 (REFERENCE_ENABLED) | re0000000672 |  |
| re0000000672 | `RS30S_IF1_IF3_IF2_GTP_mRNA -> IF3 + RS30S_IF1_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 0.08 (REFERENCE_ENABLED) | re0000000671 |  |
| re0000000673 | `IF3 + RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 1100 (REFERENCE_ENABLED) | re0000000674 |  |
| re0000000674 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF3 + RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 0.08 (REFERENCE_ENABLED) | re0000000673 |  |
| re0000000675 | `RS30S_IF1 + mRNA -> RS30S_IF1_mRNA` | INIT_assembly / RFAM_026 | 36 (REFERENCE_ENABLED) | re0000000676 |  |
| re0000000676 | `RS30S_IF1_mRNA -> RS30S_IF1 + mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000675 |  |
| re0000000677 | `IF1 + RS30S_mRNA -> RS30S_IF1_mRNA` | INIT_assembly / RFAM_026 | 20 (REFERENCE_ENABLED) | re0000000678 |  |
| re0000000678 | `RS30S_IF1_mRNA -> IF1 + RS30S_mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000677 |  |
| re0000000679 | `IF1 + RS30S_IF2_GTP_mRNA -> RS30S_IF1_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 20 (REFERENCE_ENABLED) | re0000000680 |  |
| re0000000680 | `RS30S_IF1_IF2_GTP_mRNA -> IF1 + RS30S_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000679 |  |
| re0000000681 | `RS30S_IF1_IF2_GTP + mRNA -> RS30S_IF1_IF2_GTP_mRNA` | INIT_assembly / RFAM_026 | 36 (REFERENCE_ENABLED) | re0000000682 |  |
| re0000000682 | `RS30S_IF1_IF2_GTP_mRNA -> RS30S_IF1_IF2_GTP + mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000681 |  |
| re0000000683 | `IF1 + RS30S_fMettRNAfMetCAU_mRNA -> RS30S_IF1_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 20 (REFERENCE_ENABLED) | re0000000684 |  |
| re0000000684 | `RS30S_IF1_fMettRNAfMetCAU_mRNA -> IF1 + RS30S_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000683 |  |
| re0000000685 | `IF1 + RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 20 (REFERENCE_ENABLED) | re0000000686 |  |
| re0000000686 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> IF1 + RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000685 |  |
| re0000000687 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU + mRNA -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_assembly / RFAM_026 | 36 (REFERENCE_ENABLED) | re0000000688 |  |
| re0000000688 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS30S_IF1_IF2_GTP_fMettRNAfMetCAU + mRNA` | INIT_assembly / RFAM_026 | 0.7 (REFERENCE_ENABLED) | re0000000687 |  |
| re0000000689 | `RS30S_IF2_GTP -> GTP + IF2 + RS30S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000690 | `RS30S_IF2_GTP -> GTP + IF2_degraded + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000691 | `RS30S_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2 + RS30S_degraded + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000692 | `RS30S_IF2_GTP_fMettRNAfMetCAU -> GTP + IF2_degraded + RS30S + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000693 | `RS30S_mRNA -> RS30S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000694 | `RS30S_fMettRNAfMetCAU_mRNA -> RS30S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000695 | `RS30S_IF2_GTP_mRNA -> GTP + IF2 + RS30S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000696 | `RS30S_IF2_GTP_mRNA -> GTP + IF2_degraded + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000697 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000698 | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF2_degraded + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000699 | `RS30S_IF1_IF2_GTP -> GTP + IF1 + IF2 + RS30S_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000700 | `RS30S_IF1_IF2_GTP -> GTP + IF1 + IF2_degraded + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000701 | `RS30S_IF1_IF2_GTP -> GTP + IF1_degraded + IF2 + RS30S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000702 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2 + RS30S_degraded + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000703 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1 + IF2_degraded + RS30S + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000704 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU -> GTP + IF1_degraded + IF2 + RS30S + fMettRNAfMetCAU` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000705 | `RS30S_IF1_mRNA -> IF1 + RS30S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000706 | `RS30S_IF1_mRNA -> IF1_degraded + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000707 | `RS30S_IF1_fMettRNAfMetCAU_mRNA -> IF1 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000708 | `RS30S_IF1_fMettRNAfMetCAU_mRNA -> IF1_degraded + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000709 | `RS30S_IF1_IF2_GTP_mRNA -> GTP + IF1 + IF2 + RS30S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000710 | `RS30S_IF1_IF2_GTP_mRNA -> GTP + IF1 + IF2_degraded + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000711 | `RS30S_IF1_IF2_GTP_mRNA -> GTP + IF1_degraded + IF2 + RS30S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000712 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2 + RS30S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000713 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1 + IF2_degraded + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000714 | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA -> GTP + IF1_degraded + IF2 + RS30S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000715 | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment / RFAM_025 | 2.3 (REFERENCE_ENABLED) | re0000000716 |  |
| re0000000716 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment / RFAM_025 | 2.1 (REFERENCE_ENABLED) | re0000000715 |  |
| re0000000717 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment / RFAM_025 | 2.3 (REFERENCE_ENABLED) | re0000000718 |  |
| re0000000718 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment / RFAM_025 | 2.1 (REFERENCE_ENABLED) | re0000000717 |  |
| re0000000719 | `IF1 + RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 16 (REFERENCE_ENABLED) | re0000000720 |  |
| re0000000720 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0.0025 (REFERENCE_ENABLED) | re0000000719 |  |
| re0000000721 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment / RFAM_025 | 12 (REFERENCE_ENABLED) | re0000000745 |  |
| re0000000722 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment / RFAM_025 | 12 (REFERENCE_ENABLED) | re0000000746 |  |
| re0000000723 | `IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 16 (REFERENCE_ENABLED) | re0000000724 |  |
| re0000000724 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0.0025 (REFERENCE_ENABLED) | re0000000723 |  |
| re0000000725 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + RS70S_IF3_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 4 (REFERENCE_ENABLED) | re0000000751 |  |
| re0000000726 | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU` | INIT_factor_release / RFAM_025 | 4 (REFERENCE_ENABLED) | re0000000752 |  |
| re0000000727 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000728 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000729 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000730 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000731 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000732 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000733 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000734 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1_degraded + IF2 + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000735 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000736 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF2_degraded + IF3 + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000737 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3 + PO4 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000738 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3_degraded + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000739 | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF2 + IF3 + PO4 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000740 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3 + PO4 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000741 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2_degraded + IF3 + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000742 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3 + PO4 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000743 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1_degraded + IF2 + IF3 + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000744 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + IF3_degraded + PO4 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000745 | `PO4 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment / RFAM_025 | 0 (REFERENCE_DISABLED) | re0000000721 |  |
| re0000000746 | `PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment / RFAM_025 | 0 (REFERENCE_DISABLED) | re0000000722 |  |
| re0000000747 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 1000 (REFERENCE_ENABLED) | re0000000748 |  |
| re0000000748 | `IF3 + RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0 (REFERENCE_DISABLED) | re0000000747 |  |
| re0000000749 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 4 (REFERENCE_ENABLED) | re0000000750 |  |
| re0000000750 | `IF2_GDP + RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 200 (REFERENCE_ENABLED) | re0000000749 |  |
| re0000000751 | `IF2_GDP + RS70S_IF3_fMettRNAfMetCAU_mRNA -> RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 200 (REFERENCE_ENABLED) | re0000000725 |  |
| re0000000752 | `IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU -> RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 200 (REFERENCE_ENABLED) | re0000000726 |  |
| re0000000753 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 1000 (REFERENCE_ENABLED) | re0000000754 |  |
| re0000000754 | `IF1 + RS70S_IF3_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0 (REFERENCE_DISABLED) | re0000000753 |  |
| re0000000755 | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 1000 (REFERENCE_ENABLED) | re0000000756 |  |
| re0000000756 | `IF3 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0 (REFERENCE_DISABLED) | re0000000755 |  |
| re0000000757 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 1000 (REFERENCE_ENABLED) | re0000000758 |  |
| re0000000758 | `IF1 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0 (REFERENCE_DISABLED) | re0000000757 |  |
| re0000000759 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + RS70S_IF1_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 4 (REFERENCE_ENABLED) | re0000000760 |  |
| re0000000760 | `IF2_GDP + RS70S_IF1_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 200 (REFERENCE_ENABLED) | re0000000759 |  |
| re0000000761 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF1_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 1000 (REFERENCE_ENABLED) | re0000000762 |  |
| re0000000762 | `IF3 + RS70S_IF1_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0 (REFERENCE_DISABLED) | re0000000761 |  |
| re0000000763 | `RS70S_IF3_fMettRNAfMetCAU_mRNA -> IF3 + elRS70SAGGU0002_fMettRNAfMetCAU` | INIT_factor_release / RFAM_025 | 1000 (REFERENCE_ENABLED) | re0000000764 |  |
| re0000000764 | `IF3 + elRS70SAGGU0002_fMettRNAfMetCAU -> RS70S_IF3_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0 (REFERENCE_DISABLED) | re0000000763 |  |
| re0000000765 | `RS70S_IF1_fMettRNAfMetCAU_mRNA -> IF1 + elRS70SAGGU0002_fMettRNAfMetCAU` | INIT_factor_release / RFAM_025 | 1000 (REFERENCE_ENABLED) | re0000000766 |  |
| re0000000766 | `IF1 + elRS70SAGGU0002_fMettRNAfMetCAU -> RS70S_IF1_fMettRNAfMetCAU_mRNA` | INIT_factor_release / RFAM_025 | 0 (REFERENCE_DISABLED) | re0000000765 |  |
| re0000000767 | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000768 | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000769 | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF2 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000770 | `RS70S_IF3_fMettRNAfMetCAU_mRNA -> IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000771 | `RS70S_IF3_fMettRNAfMetCAU_mRNA -> IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000772 | `RS70S_IF3_fMettRNAfMetCAU_mRNA -> IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000773 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000774 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000775 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1_degraded + IF3 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000776 | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA -> IF1 + IF3_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000777 | `RS70S_IF1_fMettRNAfMetCAU_mRNA -> IF1 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000778 | `RS70S_IF1_fMettRNAfMetCAU_mRNA -> IF1 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000779 | `RS70S_IF1_fMettRNAfMetCAU_mRNA -> IF1_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000780 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + RS30S_degraded + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000781 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2_degraded + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000782 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1 + IF2 + RS30S + RS50S_degraded + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000783 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> GDP + IF1_degraded + IF2 + RS30S + RS50S + fMettRNAfMetCAU + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000801 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> Pept0003tRNAGlyGCC + RF1 + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000802 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> Pept0003tRNAGlyGCC + RF1 + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000804 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> Pept0003tRNAGlyGCC + RF1_degraded + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000805 | `termRS70SUAA0004_tRNAGlyGCC_RF1 -> RF1 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000806 | `termRS70SUAA0004_tRNAGlyGCC_RF1 -> RF1 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000807 | `termRS70SUAA0004_tRNAGlyGCC_RF1 -> RF1_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000808 | `termRS70SUAA0004_tRNAGlyGCC -> RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000809 | `termRS70SUAA0004_tRNAGlyGCC -> RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000816 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> Pept0003tRNAGlyGCC + RF2 + RS30S_degraded + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000817 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> Pept0003tRNAGlyGCC + RF2 + RS30S + RS50S_degraded + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000819 | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> Pept0003tRNAGlyGCC + RF2_degraded + RS30S + RS50S + mRNA` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000820 | `termRS70SUAA0004_tRNAGlyGCC_RF2 -> RF2 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000821 | `termRS70SUAA0004_tRNAGlyGCC_RF2 -> RF2 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000822 | `termRS70SUAA0004_tRNAGlyGCC_RF2 -> RF2_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000835 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP -> GTP + RF1 + RF3 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000836 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP -> GTP + RF1 + RF3 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000837 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP -> GTP + RF1_degraded + RF3 + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000850 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP -> GTP + RF1 + RF3_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000851 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP -> GDP + RF1 + RF3 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000852 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP -> GDP + RF1 + RF3 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000853 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP -> GDP + RF1_degraded + RF3 + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000854 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP -> GDP + RF1 + RF3_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000855 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3 -> RF1 + RF3 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000856 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3 -> RF1 + RF3 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000857 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3 -> RF1_degraded + RF3 + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000858 | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3 -> RF1 + RF3_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000859 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP -> GTP + RF3 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000860 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP -> GTP + RF3 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000861 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP -> GTP + RF3_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000862 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4 -> GDP + PO4 + RF3 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000863 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4 -> GDP + PO4 + RF3 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000864 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4 -> GDP + PO4 + RF3_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000865 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP -> GDP + RF3 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000866 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP -> GDP + RF3 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000867 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP -> GDP + RF3_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000876 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP -> GTP + RF2 + RF3 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000877 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP -> GTP + RF2 + RF3 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000878 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP -> GTP + RF2_degraded + RF3 + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000885 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP -> GTP + RF2 + RF3_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000886 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP -> GDP + RF2 + RF3 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000887 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP -> GDP + RF2 + RF3 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000888 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP -> GDP + RF2_degraded + RF3 + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000889 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP -> GDP + RF2 + RF3_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000890 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3 -> RF2 + RF3 + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000891 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3 -> RF2 + RF3 + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000892 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3 -> RF2_degraded + RF3 + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000893 | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3 -> RF2 + RF3_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000897 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP -> EFG + GTP + RRF + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000898 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP -> EFG + GTP + RRF + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000899 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP -> EFG + GTP + RRF_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000903 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP -> EFG_degraded + GTP + RRF + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000911 | `termRS30S_mRNA -> RS30S + mRNA` | RECYCLE_component_release / RFAM_014 | 1000 (REFERENCE_ENABLED) | re0000000912 |  |
| re0000000912 | `RS30S + mRNA -> termRS30S_mRNA` | RECYCLE_component_release / RFAM_014 | 0 (REFERENCE_DISABLED) | re0000000911 |  |
| re0000000918 | `RS50S_RRF -> RRF + RS50S` | RECYCLE_component_release / RFAM_014 | 1000 (REFERENCE_ENABLED) | re0000000968 |  |
| re0000000919 | `RS50S_tRNAGlyGCC -> RS50S + tRNAGlyGCC` | RECYCLE_component_release / RFAM_014 | 1000 (REFERENCE_ENABLED) | re0000000967 |  |
| re0000000927 | `RS50S_tRNAGlyGCC -> RS50S + tRNAGlyGCC_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000928 | `RS50S_RRF -> RRF_degraded + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000929 | `RS50S_tRNAGlyGCC_RRF -> RRF + RS50S + tRNAGlyGCC_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000931 | `RS50S_tRNAGlyGCC_RRF -> RRF_degraded + RS50S + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000932 | `RS50S_tRNAGlyGCC_EFG_GDP -> EFG + GDP + RS50S + tRNAGlyGCC_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000934 | `RS50S_tRNAGlyGCC_EFG_GDP -> EFG_degraded + GDP + RS50S + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000935 | `RS50S_RRF_EFG_GDP -> EFG + GDP + RRF_degraded + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000937 | `RS50S_RRF_EFG_GDP -> EFG_degraded + GDP + RRF + RS50S` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000938 | `termRS70SUAA0004_tRNAGlyGCC_RRF -> RRF + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000939 | `termRS70SUAA0004_tRNAGlyGCC_RRF -> RRF + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000940 | `termRS70SUAA0004_tRNAGlyGCC_RRF -> RRF_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000941 | `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP -> EFG + GTP + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000942 | `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP -> EFG + GTP + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000943 | `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP -> EFG_degraded + GTP + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000944 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP -> EFG + GDP + RRF + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000945 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP -> EFG + GDP + RRF + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000946 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP -> EFG + GDP + RRF_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000947 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP -> EFG_degraded + GDP + RRF + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000948 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4 -> EFG + GDP + PO4 + RRF + RS30S_degraded + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000949 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4 -> EFG + GDP + PO4 + RRF + RS30S + RS50S_degraded + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000950 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4 -> EFG + GDP + PO4 + RRF_degraded + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000951 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4 -> EFG_degraded + GDP + PO4 + RRF + RS30S + RS50S + mRNA + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000952 | `RS50S_tRNAGlyGCC_RRF_EFG_GDP -> EFG + GDP + RRF + RS50S + tRNAGlyGCC_degraded` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000954 | `RS50S_tRNAGlyGCC_RRF_EFG_GDP -> EFG_degraded + GDP + RRF + RS50S + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000955 | `RS50S_tRNAGlyGCC_RRF_EFG_GDP -> EFG + GDP + RRF_degraded + RS50S + tRNAGlyGCC` | DEG_sink / RFAM_DEG | 0 (REFERENCE_DISABLED) | none |  |
| re0000000967 | `RS50S + tRNAGlyGCC -> RS50S_tRNAGlyGCC` | RECYCLE_component_release / RFAM_014 | 0 (REFERENCE_DISABLED) | re0000000919 |  |
| re0000000968 | `RRF + RS50S -> RS50S_RRF` | RECYCLE_component_release / RFAM_014 | 0 (REFERENCE_DISABLED) | re0000000918 |  |
