# PNAS2017 reaction-level functional contract — 详解版 v0

**Status:** human-approved functional vocabulary v0 with source-completeness additions.  
**Scope:** 定义 Level A / B / C、reversibility schema、mechanistic reaction type 以及 reaction-row 最小字段。它不是 968-row functional assignment，也不是 reduction certificate。

## 1. 为什么需要这层 contract

241-species information-retention contract 已经回答“哪些信息不能丢”。reaction-level contract 继续回答：

1. 这条 reaction 属于哪个 PURE 功能模块？
2. 它在宏观因果链中做什么？
3. 原 SBML 把它表示成哪种 graph reaction type？
4. 它是否存在 exact reverse partner？
5. 如果以后要 merge / lump / QSSA，会碰到哪些 protected species、pools、resource ledgers 和 occupancy 信息？

Level-C label 本身不授权任何 reduction。

## 2. 三层 reaction hierarchy

| 层级 | 含义 | 示例 |
| --- | --- | --- |
| Level A | broad PURE functional module | aminoacylation / initiation / elongation / termination-recycling / energy regeneration |
| Level B | original PNAS source subsystem provenance | `Aminoacylation_A_Gly`, `Initiation_B1`, `Elongation_Ca2_pept0002` |
| Level C | project functional stage | `RS_activation`, `ELONG_translocation`, `RECYCLE_disassembly` |

原仓库 `reduction_map.md` 曾把 “biochemical process + CellDesigner reaction type” 称为 Level C。为了避免语义混淆，本 contract 从 v0 起把 **functional stage** 固定为 Level C；`cell_designer_reaction_type` 作为独立字段保留。现有生成物不在本轮重写，后续 968-row remap 时再统一迁移。

## 3. Source-level code verification

结构检查基于当前：

- `models/pnas2017_full_reference/audit/reactions.csv`
- `docs/reduction/reduction_decisions.csv`
- `models/pnas2017_full_reference/audit/modules.csv`

得到：

| 检查项 | 结果 |
| --- | ---: |
| unique combined reactions | 968 |
| original source subsystems | 26 |
| SBML `reversible=true` | 0 |
| exact reverse-stoichiometry pairs | 290 |
| directed reaction IDs covered by exact pairs | 580 |
| ambiguous reverse-signature groups | 0 |
| HETERODIMER_ASSOCIATION | 266 |
| DISSOCIATION | 266 |
| STATE_TRANSITION | 436 |
| degradation-related reactions | 388 |
| `FMet_tRNASynthesis` reactions | 29 |

这两个最后的检查直接暴露出原 21-label 草案的两个 coverage gap：

1. `FMet_tRNASynthesis` 不是普通 aaRS charging，因此增加 `RS_to_INIT_formylation`；
2. degradation 不属于 Mavelli 主链，但 source network 中大量存在，因此增加 coverage-only `DEG_sink`。

最终 controlled vocabulary = **22 个 active-process Level-C stages + 1 个 coverage-only special stage = 23 个 labels**。

## 4. Reaction-row 最小字段

后续 968-row mapping 至少包含：

```text
reaction_id

level_a_module
level_b_subsystem
level_c_functional_stage

mechanistic_reaction_type

reactants
products
stoichiometry

reversibility_class
reverse_partner_id
reverse_pair_basis
exact_reversible_merge

protected_species_touched
protected_pool_touched
resource_ledger_effect
occupancy_effect

candidate_reduction_type
human_review_status
```

其中 `candidate_reduction_type` 与 Level C 分开：同一个 `RS_binding` 可以最后是 KEEP、exact reversible merge、fast-equilibrium candidate 或 QSSA candidate；这些需要后续证据。

## 5. Reversibility：先做 exact representation，再谈 approximation

当前 combined SBML 968 条 reactions 全部以 directed `reversible=false` rows 保存，但化学计量自动匹配发现 290 个 exact reverse pairs。

定义：

- `IRREVERSIBLE`：未发现或不接受 reverse partner。
- `EXACT_REVERSE_PAIR`：reactants/products stoichiometric signatures 完全互换。
- `POSSIBLE_REVERSE_PAIR`：疑似 reverse，但需要人工核对 species identity / stoichiometry / provenance。
- `UNKNOWN`：尚未判断。

对 `EXACT_REVERSE_PAIR`，允许：

```text
A + B --vf--> C
C     --vr--> A + B

      ↓ exact representation rewrite

A + B <=> C
v_net = vf - vr
```

必须保留 `vf`、`vr`、`v_net`、两个 original IDs 与两条 kinetic laws。该 merge 不减少状态、不宣称快平衡，也不改变 ODE。

## 6. Mechanistic reaction type：与功能标签正交

原 CellDesigner graph type 只有三类：

- `HETERODIMER_ASSOCIATION` — 266
- `DISSOCIATION` — 266
- `STATE_TRANSITION` — 436

例如同一个 functional stage `ELONG_aa_tRNA_delivery` 中可以同时出现 association、dissociation 和 state transition；反过来，一个 `STATE_TRANSITION` 也可能属于 energy coupling、peptide formation 或 degradation。

## 7. Level-C controlled vocabulary

### 7.1 RS / aminoacylation

#### `RS_binding`

aaRS 与 amino acid、ATP、tRNA 的 binding/unbinding 与 synthetase occupancy。

典型语义：

```text
RS + AA <=> RS·AA
RS + ATP <=> RS·ATP
RS·AA + ATP <=> RS·AA·ATP
RS·AA-AMP + tRNA <=> RS·AA-AMP·tRNA
```

后续可能出现 exact reverse merge / fast-equilibrium / QSSA candidate，但本标签不预先决定。

#### `RS_activation`

ATP 驱动 amino-acid activation。宏观资源事件：

```text
AA + ATP -> aminoacyl-AMP + PPi
```

必须保留 ATP、AMP-moiety destination、PPi 与 activation event count。

#### `RS_charging`

activated amino acid 转移到 specific tRNA：

```text
aminoacyl-AMP + tRNA -> aa-tRNA + AMP
```

activation + charging 的净账本为：

```text
AA + ATP + tRNA -> aa-tRNA + AMP + PPi
```

#### `RS_to_INIT_formylation`

source audit 中 `FMet_tRNASynthesis` 有 29 reactions。它不是 aaRS charging，因此不能硬塞进 `RS_charging`。本标签表示 MTF-catalyzed bridge：

```text
Met-tRNA + formyl-donor chemistry -> fMet-tRNA + donor product
```

它连接 aminoacylation 与 initiation；Level-A provenance 仍保留原 source subsystem。

### 7.2 INIT

#### `INIT_assembly`

30S、mRNA、IF1/IF2/IF3 等形成 pre-initiation occupancy graph。

#### `INIT_tRNA_recruitment`

initiator fMet-tRNA 进入 initiation complex；必须与普通 elongation aa-tRNA delivery 区分。

#### `INIT_energy_commitment`

IF2 等相关 GTP/GDP/Pi chemistry，使 initiation 向 productive 方向推进。

#### `INIT_70S_formation`

50S 加入，建立 70S initiation complex；必须保留 30S/50S/70S moiety accounting。

#### `INIT_factor_release`

IF pools 返回 free state，ribosome 进入 elongation-ready occupancy。

### 7.3 ELONG — 固定保留 5 类

#### `ELONG_aa_tRNA_delivery`

EF-Tu/EF-Ts、GTP/GDP 与 charged tRNA 的 ternary-complex assembly/exchange/ribosome delivery。

#### `ELONG_energy_coupling`

EF-Tu / EF-G 相关 GTP -> GDP + Pi。Level C 暂不继续拆成 EF-Tu-energy 与 EF-G-energy；具体来源由 Level B、participants 和 ledger 区分。

#### `ELONG_peptide_formation`

真正导致 peptide length `n -> n+1` 的 productive chemistry；保护 peptide progression 与 amino-acid incorporation。

#### `ELONG_translocation`

peptide formation 后 ribosome/tRNA positional state 推进。它与 peptide formation 分开，因为两者改变的 protected information 不同。

#### `ELONG_tRNA_release`

deacylated tRNA 返回 free tRNA pool，连接下一轮 aminoacylation。

### 7.4 TERM / RECYCLE

#### `TERM_factor_binding`

RF1/RF2 等与 stop-codon complex 的识别和结合。

#### `TERM_peptide_release`

peptidyl-tRNA hydrolysis / completed peptide release；定义 product-formation event。

#### `TERM_energy_coupling`

RF3 等 termination turnover 的 GTP/GDP/Pi coupling。

#### `RECYCLE_disassembly`

RRF/EF-G 等驱动 post-termination ribosome splitting：

```text
70S -> 30S + 50S
```

#### `RECYCLE_component_release`

mRNA、tRNA、RF/RRF/EF-G 等从 post-termination occupancy 返回 free pools。

### 7.5 EN / energy regeneration

#### `EN_binding`

CK、NDK、MK、PPiase 等的 enzyme/substrate/product binding 与 occupancy。

#### `EN_energy_transfer`

主要宏观 carrier conversions：

```text
CP + ADP <=> Cr + ATP
ATP + GDP <=> ADP + GTP
ATP + AMP <=> 2 ADP
```

#### `EN_byproduct_processing`

例如：

```text
PPi -> 2 Pi
```

必须保留 PPi/Pi 与 represented-particle-count consequence，不能因“不直接产 ATP”而删。

### 7.6 coverage-only special stage

#### `DEG_sink`

所有涉及 `*_degraded` terminal sink 的 degradation/inactivation reaction。它不是 Mavelli 主功能链，而是 source-completeness class。

与 241-species contract 对齐：

- degraded sink species 可不作为 main ODE coordinate；
- cumulative loss 必须继续可输出；
- 参考条件下 `k1=0` 不能自动升级成“永久删除”。

## 8. 引用文字式 reaction atlas

```text
PNAS2017 FULL TRANSLATION NETWORK
241 species / 968 directed reactions / 26 source subsystems

├── RS / AMINOACYLATION
│   ├── RS_binding
│   │   ├── aaRS + amino acid association/dissociation
│   │   ├── aaRS + ATP association/dissociation
│   │   └── aaRS + tRNA / intermediate association/dissociation
│   ├── RS_activation
│   │   └── amino acid + ATP -> aminoacyl-AMP + PPi
│   ├── RS_charging
│   │   └── aminoacyl-AMP + tRNA -> aa-tRNA + AMP
│   └── RS_to_INIT_formylation
│       └── Met-tRNA -> fMet-tRNA bridge chemistry
│
├── INITIATION
│   ├── INIT_assembly
│   ├── INIT_tRNA_recruitment
│   ├── INIT_energy_commitment
│   ├── INIT_70S_formation
│   └── INIT_factor_release
│
├── ELONGATION
│   ├── ELONG_aa_tRNA_delivery
│   │   ├── EF-Tu / EF-Ts exchange
│   │   └── charged-tRNA ternary-complex delivery
│   ├── ELONG_energy_coupling
│   │   ├── EF-Tu GTP/GDP/Pi
│   │   └── EF-G GTP/GDP/Pi
│   ├── ELONG_peptide_formation
│   │   └── peptide_n -> peptide_(n+1)
│   ├── ELONG_translocation
│   │   └── ribosome/tRNA positional progression
│   └── ELONG_tRNA_release
│       └── deacylated tRNA -> free tRNA pool
│
├── TERMINATION / RECYCLING
│   ├── TERM_factor_binding
│   ├── TERM_peptide_release
│   ├── TERM_energy_coupling
│   ├── RECYCLE_disassembly
│   │   └── 70S -> 30S + 50S
│   └── RECYCLE_component_release
│       ├── tRNA release
│       ├── mRNA release
│       └── factor release
│
├── ENERGY REGENERATION
│   ├── EN_binding
│   ├── EN_energy_transfer
│   │   ├── CP + ADP <=> Cr + ATP
│   │   ├── ATP + GDP <=> ADP + GTP
│   │   └── ATP + AMP <=> 2 ADP
│   └── EN_byproduct_processing
│       └── PPi -> 2 Pi
│
└── CROSS-CUTTING SOURCE COVERAGE
    └── DEG_sink
        └── active species / complex -> *_degraded terminal sink
```

## 9. 26 source subsystems 对 Level-C 的候选覆盖

这只是 **candidate coverage map**，不是 968-row finalized assignment。

| Source subsystem(s) | Level-C candidate coverage |
| --- | --- |
| `Aminoacylation_A_Gly`, `Aminoacylation_A_Met` | `RS_binding`, `RS_activation`, `DEG_sink` |
| `Aminoacylation_B_GlyGCC`, `Aminoacylation_B_fMetCAU` | `RS_binding`, `RS_charging`, `DEG_sink` |
| `FMet_tRNASynthesis` | `RS_to_INIT_formylation`, `DEG_sink` |
| `Initiation_A` | `INIT_energy_commitment`, factor preparation / release, `DEG_sink` |
| `Initiation_B1`, `Initiation_B2`, `Initiation_C` | all five INIT stages + `DEG_sink` |
| `Elongation_A_Gly`, `Elongation_A_Met` | `ELONG_aa_tRNA_delivery`, `ELONG_energy_coupling`, `DEG_sink` |
| `Elongation_B` | `ELONG_energy_coupling`, `ELONG_translocation`, `DEG_sink` |
| `Elongation_Ca1_*`, `Elongation_Ca2_*` | five ELONG stages as applicable + `DEG_sink` |
| `Termination_A_RF1`, `Termination_A_RF2` | `TERM_factor_binding`, `TERM_peptide_release`, `DEG_sink` |
| `Termination_B_RF1`, `Termination_B_RF2` | `TERM_factor_binding`, `TERM_energy_coupling`, component release, `DEG_sink` |
| `Termination_C` | `TERM_energy_coupling`, `RECYCLE_disassembly`, `RECYCLE_component_release`, `DEG_sink` |
| `EnergyRegeneration_A/B/C` | `EN_binding`, `EN_energy_transfer`, `DEG_sink` |
| `EnergyRegeneration_D` | `EN_binding`, `EN_byproduct_processing`, `DEG_sink` |
| `SmallMolecules` | shared EN bookkeeping; exact Level-C assignment must be reaction-specific |

## 10. 当前不能宣称什么

本 v0 **没有**：

- 给 968 条 reactions 全部自动贴 Level-C 标签；
- 用 Level C 推断 QSSA；
- 用 exact reverse pair 推断 fast equilibrium；
- 删除 degradation；
- 合并 peptide formation 与 translocation；
- 生成新的 reduced SBML。

下一步应从这个 vocabulary 出发，建立 968-row annotation，并对 ambiguous rows 保留 `HUMAN_REVIEW_REQUIRED`。
