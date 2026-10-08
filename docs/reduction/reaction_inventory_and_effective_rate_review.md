# PNAS 2017 全反应清单、功能分类与串联等效约化审查

> **审查草案 / scientific status: HUMAN_REVIEW_REQUIRED — NOT A REDUCED MODEL.** 这里的简化反应数均为结构上的条件化计数或未验证的假设算术，绝不是已执行模型或成功数值验证。

- 生成日期：2026-10-08；审查分支：`codex/pnas-topology-first`，读取时分支 SHA：`86afa8099901406d0333d08fff002938b7e3ec49`。
- Canonical PNAS2017 full SBML：`models/pnas2017_full_reference/original/fMGG_synthesis.xml`，SHA-256：`dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`。
- 本表逐行依据 [`reaction_level_annotation_v2.csv`](reaction_level_annotation_v2.csv) 的 968 条 `reaction_id`/source stoichiometry/stage 和 [`source_subnetworks.csv`](../../results/topology_audit/source_subnetworks.csv) 的 26 个源子系统；12 条链取自 [`summary.json`](../../results/topology_audit/summary.json)。具体反应动力学、酶中间体与参数可追到 [`reactions_table.csv`](../../results/topology_audit/reactions_table.csv)。
- 作用范围：Matsuura et al., PNAS 2017 **mRNA-directed fMet–Gly–Gly translation**，不是 DNA→RNA→protein 全转录翻译；有两次 Gly 加入，不是任意长度蛋白的直接证明。

## 1. 先把三种“减少数量”分开

| 层次 | 有向反应数 / 通量表示数 | 动态状态数 | 数值及物理意义 |
| --- | ---: | ---: | --- |
| L0：完整 canonical source | **968 有向方向** | 241 原始物种（独立维数另算） | 原样保留所有 source reactions；原始 SBML 的 `k1` 与初值为占位值 1。 |
| L1：290 对精确反向通道配对 | **678 个净通量表达式**，仍代表 968 个方向 | 不变 | 纯表示变换，等于 968−290；**不是物理反应删减**，也不是 QSSA。 |
| C1：作者固定参数（author CSV） | **483 个非零 k 方向**，485 个 k=0 方向保留在 source | 不变 | 指定条件下禁用的方向，不代表 source-general 反应删除；初值为零也不等于永久失活。 |
| C2：作者条件下的反向方向配对 | **274 个净通量表达式**，代表 483 个非零 k 方向 | 不变 | 209 对两向均非零：483−209=274；只是条件化通量写法。 |
| P1：仅三个连续反应的 A→D 候选 | **481 个非零 k 方向（483−3+1）** | 尚未实施 | 仅将 `re0000000016/17/18` 变为一条净计量反应的**候选算术**。 |
| P2：仅 9 组非零净计量串联候选如均验证并各合为一条 | **468 个非零 k 方向（483−24+9）** | 尚未实施 | 12 组算法候选中 3 组为正反往返对（净计量为零），必须排除；468 只是 9 组串联候选的假设计数，**不是已验证的减少**。 |
| Goal：模块级中等复杂度 CRN | **未定** | **未定** | 若希望几十条，仍须处理大量结合、解离、循环及跨模块耦合；项目尚未做到。 |

**禁止混算：** L1/C2 是表示数，C1 是固定参数下的活跃方向数，P1 与更正后的 P2 才是待验证的串联反应合并提议；这些行不是可无条件顺次相减的一条已完成工作流。

## 2. 生化模块分组：每条源反应唯一计入一次

这是从已审查的 `level_c_primary_stage` 建立的**互斥展示分区**，专用于可加总的计数；它不同于 26 个可重叠的源 SBML 子系统。`DEG_sink` 单列，因为失活/降解横跨多个生化模块。6 条 `SHARED_MULTI_CONTEXT` 没有被强制塞入单一生化模块。

| 功能组（互斥展示） | 完整有向反应 | 作者条件 k>0 | 作者条件 k=0 | 仅9组非零净链假设合并的剩余方向 |
| --- | ---: | ---: | ---: | ---: |
| Initiation | 206 | 197 | 9 | 197 |
| Elongation | 88 | 61 | 27 | 51 |
| Aminoacylation / formylation | 122 | 93 | 29 | 91 |
| Termination | 46 | 42 | 4 | 41 |
| Ribosome recycling | 38 | 24 | 14 | 22 |
| Energy regeneration | 74 | 61 | 13 | 61 |
| Shared multi-context | 6 | 5 | 1 | 5 |
| Degradation sinks | 388 | 0 | 388 | 0 |
| **总计** | **968** | **483** | **485** | **468（未验证）** |

### 2.1 如何看 phosphorylation 等化学过程

**Initiation、elongation、termination、ribosome recycling、aminoacylation、energy regeneration 是生化功能阶段；phosphorylation/磷酰基转移、核苷酸水解、结合/解离则是可能跨阶段的化学事件。** 不应把两套标签当成可相加的互斥模块。

| 已有逐反应功能注释标签 | 有向反应条数 | 化学意义及注意事项 |
| --- | ---: | --- |
| `RS_activation` | 24 | amino acid adenylation：aaRS 使氨基酸活化，涉及 AMP/PPi；不是简单 ATP→ADP 磷酸化 |
| `RS_charging` | 28 | aa-tRNA charging：活化氨基酸转移到 tRNA |
| `RS_to_INIT_formylation` | 22 | formylation：起始 fMet 相关化学 |
| `EN_binding` | 54 | ATP/GTP 再生酶的底物结合/解离 |
| `EN_energy_transfer` | 18 | phosphoryl-transfer / nucleotide regeneration 候选：须按酶复合物化学计量逐条核查 |
| `EN_byproduct_processing` | 2 | PPi processing：焦磷酸副产物相关转换 |
| `INIT_energy_commitment` | 12 | 起始相关核苷酸装配和承诺 |
| `ELONG_energy_coupling` | 48 | 延伸相关 GTP/因子能量循环及释放 |
| `ELONG_peptide_formation` | 4 | peptide-bond/chain growth：肽链延长 |
| `TERM_energy_coupling` | 34 | 终止相关核苷酸/因子循环 |
| `RECYCLE_disassembly` | 14 | ribosome disassembly/recycling |
| `DEG_sink` | 388 | 失活/降解反应，在作者特定参数条件下 k=0 |

逐条化学事件必须以完整底物/产物（包括**结合态中的 ATP/GTP/AMP/GDP/PO4/PPi**）判定，不能只根据自由小分子浓度差或名称推断。原有 968 行注释的 `mechanistic_reaction_type` 只有 association / dissociation / transition 三类机械形式，不能代替更细的生化判读。

## 3. 源文献的 26 个子系统（非互斥）

**不能把此表的 reaction_count 相加当 968。** 同一反应（例如共同的核糖体失活）会出现在多个源子系统内；下表忠实保留这种复用。第 2 节的主阶段统计才是互斥的。

| 大类 | 作者源子系统 | 子系统反应成员数 | 该子系统中作者 k>0 的成员数 |
| --- | --- | ---: | ---: |
| Aminoacylation / formylation | `Aminoacylation_A_Gly` | 25 | 14 |
| Aminoacylation / formylation | `Aminoacylation_A_Met` | 25 | 14 |
| Aminoacylation / formylation | `Aminoacylation_B_GlyGCC` | 44 | 28 |
| Aminoacylation / formylation | `Aminoacylation_B_fMetCAU` | 44 | 28 |
| Elongation | `Elongation_A_Gly` | 29 | 16 |
| Elongation | `Elongation_A_Met` | 29 | 16 |
| Elongation | `Elongation_B` | 40 | 16 |
| Elongation | `Elongation_Ca1_GlyGCC` | 12 | 1 |
| Elongation | `Elongation_Ca1_fMetCAU` | 12 | 1 |
| Elongation | `Elongation_Ca2_pept0002` | 61 | 13 |
| Elongation | `Elongation_Ca2_pept0003` | 61 | 13 |
| Energy regeneration | `EnergyRegeneration_A` | 25 | 18 |
| Energy regeneration | `EnergyRegeneration_B` | 25 | 17 |
| Energy regeneration | `EnergyRegeneration_C` | 25 | 18 |
| Energy regeneration | `EnergyRegeneration_D` | 12 | 8 |
| Aminoacylation / formylation | `FMet_tRNASynthesis` | 29 | 13 |
| Initiation | `Initiation_A` | 10 | 6 |
| Initiation | `Initiation_B1` | 156 | 86 |
| Initiation | `Initiation_B2` | 110 | 80 |
| Initiation | `Initiation_C` | 80 | 27 |
| Shared small molecules | `SmallMolecules` | 12 | 0 |
| Termination / recycling | `Termination_A_RF1` | 22 | 5 |
| Termination / recycling | `Termination_A_RF2` | 22 | 5 |
| Termination / recycling | `Termination_B_RF1` | 51 | 20 |
| Termination / recycling | `Termination_B_RF2` | 51 | 20 |
| Termination / recycling | `Termination_C` | 86 | 25 |

## 4. 拓扑算法检出的 12 组：9 条非零净计量串联候选 + 3 对正反往返反应

这 12 组来自**作者固定参数中关闭 k=0 方向**后的拓扑图；完整 968 通道图的严格串联链为 0。经核对源反应，原 CHAIN_06/07/08 是相反方向的**同一结合/解离反应对**，并非 A→…→D 的净化学转化，不能从 ∅ → ∅ 推断可删除动态。其余 9 组有非零的路径净计量，但不自动存在精确的常数 `k_eff`。该算法未排除二步回到起点的回路。

| 分类 | 原有反应 ID（先后） | 类型/表示变化 | 净计量 / 化学意义 |
| --- | --- | --- | --- |
| CHAIN_01 | `re0000000014` → `re0000000016` → `re0000000017` → `re0000000018` | 4→1 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` → `PO4` + `EFTu_GDP` + `elRS70SBGGU0002_Pept0002tRNAGlyGCC` |
| CHAIN_02 | `re0000000075` → `re0000000077` → `re0000000078` → `re0000000079` | 4→1 | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` → `PO4` + `EFTu_GDP` + `elRS70SBGGU0003_Pept0003tRNAGlyGCC` |
| CHAIN_03 | `re0000000024` → `re0000000025` → `re0000000068` | 3→1 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4` → `PO4` + `EFG_GDP` + `elRS70SAGGU0003_Pept0002` + `tRNAGlyGCC` |
| CHAIN_04 | `re0000000902` → `re0000000910` → `re0000000911` | 3→1 | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` → `PO4` + `RS50S_tRNAGlyGCC_RRF_EFG_GDP` + `RS30S` + `mRNA` |
| CHAIN_05 | `re0000000085` → `re0000000086` | 2→1 | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4` → `PO4` + `EFG_GDP` + `elRS70SAUAA0004_Pept0003tRNAGlyGCC` |
| PAIR_06 (原 CHAIN_06) | `re0000000147` ↔ `re0000000148` | 2→1 净通量写法（L1/C2），不减少物种 | `GlyRS_GlyAMP` ⇄ `GlyRS` + `GlyAMP`；正反结合/解离，**不属于串联约化** |
| PAIR_07 (原 CHAIN_07) | `re0000000172` ↔ `re0000000173` | 2→1 净通量写法（L1/C2），不减少物种 | `MetRS_MetAMP` ⇄ `MetRS` + `MetAMP`；正反结合/解离，**不属于串联约化** |
| PAIR_08 (原 CHAIN_08) | `re0000000288` ↔ `re0000000289` | 2→1 净通量写法（L1/C2），不减少物种 | `EFTu_GTP` + `MettRNAfMetCAU` ⇄ `EFTu_GTP_MettRNAfMetCAU`；正反结合/解离，**不属于串联约化** |
| CHAIN_09 | `re0000000307` → `re0000000309` | 2→1 | `RS70S_EFG_GDP_PO4` → `PO4` + `EFG_GDP` + `RS70S` |
| CHAIN_10 | `re0000000428` → `re0000000434` | 2→1 | `MTF_THF_fMettRNAfMetCAU` → `fMettRNAfMetCAU` + `MTF` + `THF` |
| CHAIN_11 | `re0000000430` → `re0000000432` | 2→1 | `MTF_THF_fMettRNAfMetCAU` → `THF` + `MTF` + `fMettRNAfMetCAU` |
| CHAIN_12 | `re0000000842` → `re0000000847` | 2→1 | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4` → `PO4` + `RF3_GDP` + `termRS70SUAA0004_tRNAGlyGCC` |

串联候选只包括 `CHAIN_01–05` 和 `CHAIN_09–12`，共 **9 组**。`PAIR_06–08` 应由 L1/C2 精确反向净通量表示，不是有效速率 A→D 模型；即便两列化学计量之和为零，正反**瞬时净通量**通常仍不为零，不能删除自由/结合状态。9 组串联候选仍全部 **HUMAN_REVIEW_REQUIRED / PENDING**，未改变 SBML 或批准约化。

### 4.1 优先亲自核查的三步链（原 SBML 真正的化学过程）

| 原通道 | 实际事件 | 作者 k（源模型时间单位的倒数） |
| --- | --- | ---: |
| `re0000000016` | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` → `PO4` + `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` | 1000.0 |
| `re0000000017` | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` → `EFTu_GDP` + `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | 7.0 |
| `re0000000018` | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` → `elRS70SBGGU0002_Pept0002tRNAGlyGCC` | 1000.0 |

将 `A=elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC`、`X1=elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC`、`X2=elRS70SAGGU0002_fMet_GlytRNAGlyGCC`、`D=elRS70SBGGU0002_Pept0002tRNAGlyGCC` 定义为该局部边界，则这三列净和为：

`A → D + PO4 + EFTu_GDP`

在不可逆一阶、常数速率、无激活旁支的 **单个分子通过链** 的平均完成时间近似下，候选

\[k_{\mathrm{eff}}=\left(\frac{1}{1000}+\frac{1}{7}+\frac{1}{1000}\right)^{-1}\approx 6.903353\quad (\text{source time unit})^{-1}.\]

该 `k_eff` **只是匹配平均等待时间**。原模型在第一步释放 PO4、第二步释放 EF-Tu·GDP、第三步进行肽链延长；直接净反应会提前或推迟某些瞬时账本事件，且改变内部核糖体占据。对于初始层、短时间响应、旁支重新激活、耗竭状态，不能推断该单步模型准确。若平均速率公式涉及多分子结合、状态依赖和回流，更不能把几个 `k` 直接求倒数和。

建议优先把 **direct A→D** 作为老师要求的主候选，与 **A→E_mid→D**（保留延伸占据）作为备选并行比较，不要一开始便默认选择 E_mid。

### 4.2 逐链人工审查卡

| Path | 主功能阶段 | 主要必须核对的闭合条件 | 决定 |
| --- | --- | --- | --- |
| CHAIN_01 | Elongation | author-k=0 的旁支是否在目标适用域仍为零；中间态是否积累；自由和结合态核苷酸/因子/核糖体收支；参数变化能否定义有效速率 | ☐ KEEP ☐ DIRECT_LUMP ☐ AGGREGATE ☐ QSSA_LATER ☐ REJECT |
| CHAIN_02 | Elongation | author-k=0 的旁支是否在目标适用域仍为零；中间态是否积累；自由和结合态核苷酸/因子/核糖体收支；参数变化能否定义有效速率 | ☐ KEEP ☐ DIRECT_LUMP ☐ AGGREGATE ☐ QSSA_LATER ☐ REJECT |
| CHAIN_03 | Elongation | author-k=0 的旁支是否在目标适用域仍为零；中间态是否积累；自由和结合态核苷酸/因子/核糖体收支；参数变化能否定义有效速率 | ☐ KEEP ☐ DIRECT_LUMP ☐ AGGREGATE ☐ QSSA_LATER ☐ REJECT |
| CHAIN_04 | Ribosome recycling | author-k=0 的旁支是否在目标适用域仍为零；中间态是否积累；自由和结合态核苷酸/因子/核糖体收支；参数变化能否定义有效速率 | ☐ KEEP ☐ DIRECT_LUMP ☐ AGGREGATE ☐ QSSA_LATER ☐ REJECT |
| CHAIN_05 | Elongation | author-k=0 的旁支是否在目标适用域仍为零；中间态是否积累；自由和结合态核苷酸/因子/核糖体收支；参数变化能否定义有效速率 | ☐ KEEP ☐ DIRECT_LUMP ☐ AGGREGATE ☐ QSSA_LATER ☐ REJECT |
| PAIR_06 (原 CHAIN_06) | Aminoacylation / formylation | 正反结合/解离的闭环，不是串联净转化。保留自由态、结合态和正反通量 | **EXCLUDE_FROM_SERIAL_LUMP**；L1/C2 可精确配对 |
| PAIR_07 (原 CHAIN_07) | Aminoacylation / formylation | 正反结合/解离的闭环，不是串联净转化。保留自由态、结合态和正反通量 | **EXCLUDE_FROM_SERIAL_LUMP**；L1/C2 可精确配对 |
| PAIR_08 (原 CHAIN_08) | Elongation | 正反结合/解离的闭环，不是串联净转化。保留自由态、结合态和正反通量 | **EXCLUDE_FROM_SERIAL_LUMP**；L1/C2 可精确配对 |
| CHAIN_09 | Elongation | author-k=0 的旁支是否在目标适用域仍为零；中间态是否积累；自由和结合态核苷酸/因子/核糖体收支；参数变化能否定义有效速率 | ☐ KEEP ☐ DIRECT_LUMP ☐ AGGREGATE ☐ QSSA_LATER ☐ REJECT |
| CHAIN_10 | Aminoacylation / formylation | author-k=0 的旁支是否在目标适用域仍为零；中间态是否积累；自由和结合态核苷酸/因子/核糖体收支；参数变化能否定义有效速率 | ☐ KEEP ☐ DIRECT_LUMP ☐ AGGREGATE ☐ QSSA_LATER ☐ REJECT |
| CHAIN_11 | Aminoacylation / formylation | author-k=0 的旁支是否在目标适用域仍为零；中间态是否积累；自由和结合态核苷酸/因子/核糖体收支；参数变化能否定义有效速率 | ☐ KEEP ☐ DIRECT_LUMP ☐ AGGREGATE ☐ QSSA_LATER ☐ REJECT |
| CHAIN_12 | Termination | author-k=0 的旁支是否在目标适用域仍为零；中间态是否积累；自由和结合态核苷酸/因子/核糖体收支；参数变化能否定义有效速率 | ☐ KEEP ☐ DIRECT_LUMP ☐ AGGREGATE ☐ QSSA_LATER ☐ REJECT |

## 5. 全部 968 个原始反应（完整索引）

**阅读方式：**按互斥生化模块→细分功能阶段折叠阅读；每条 `re...` **出现且仅出现一次**，列出从原始计量解析得到的完整反应物与产物（合并后的化学式不要反写进这张源清单）。`author k` 是作者参数 CSV 的值；0 只表示固定作者条件下方向关闭。`Src` 是源子系统的简写：`(+n shared)` 表示此行还出现在另外 n 个源子系统，全部成员名单可从上方链接的原始注释 CSV 查看。`Rev` 对应 source 中精确化学计量反向通道，不是作者两向都非零的保证。`Motif` 是未批准的结构候选。

分类与功能状态不构成 kinetics approval；不存在由这张表自动生成的有效速率或减阶仿真。

### Initiation — 206 source directions

<details>
<summary><strong>INIT_70S_formation</strong> — 12 reactions; author k&gt;0: 12</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000455` | `RS70S` → `RS30S` + `RS50S` | `Initiation_B1` | 0.012 | release | `re0000000456` | — |
| `re0000000456` | `RS30S` + `RS50S` → `RS70S` | `Initiation_B1` | 12.0 | binding | `re0000000455` | — |
| `re0000000461` | `RS70S_IF3` → `RS30S_IF3` + `RS50S` | `Initiation_B1` | 0.0068 | release | `re0000000462` | — |
| `re0000000462` | `RS30S_IF3` + `RS50S` → `RS70S_IF3` | `Initiation_B1` | 0.18 | binding | `re0000000461` | — |
| `re0000000485` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` + `RS50S` → `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 34.0 | binding | `re0000000486` | — |
| `re0000000486` | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` + `RS50S` | `Initiation_B1` | 35.0 | release | `re0000000485` | — |
| `re0000000487` | `RS70S_IF1` → `RS30S_IF1` + `RS50S` | `Initiation_B1` | 0.012 | release | `re0000000488` | — |
| `re0000000488` | `RS30S_IF1` + `RS50S` → `RS70S_IF1` | `Initiation_B1` | 12.0 | binding | `re0000000487` | — |
| `re0000000493` | `RS70S_IF1_IF3` → `RS30S_IF1_IF3` + `RS50S` | `Initiation_B1` | 0.0068 | release | `re0000000494` | — |
| `re0000000494` | `RS30S_IF1_IF3` + `RS50S` → `RS70S_IF1_IF3` | `Initiation_B1` | 0.18 | binding | `re0000000493` | — |
| `re0000000529` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` + `RS50S` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 34.0 | binding | `re0000000530` | — |
| `re0000000530` | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` + `RS50S` | `Initiation_B1` | 35.0 | release | `re0000000529` | — |

</details>

<details>
<summary><strong>INIT_assembly</strong> — 112 reactions; author k&gt;0: 112</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000457` | `IF3` + `RS70S` → `RS70S_IF3` | `Initiation_B1` | 0.082 | binding | `re0000000458` | — |
| `re0000000458` | `RS70S_IF3` → `IF3` + `RS70S` | `Initiation_B1` | 0.26 | release | `re0000000457` | — |
| `re0000000459` | `IF3` + `RS30S` → `RS30S_IF3` | `Initiation_B1` | 1160.0 | binding | `re0000000460` | — |
| `re0000000460` | `RS30S_IF3` → `IF3` + `RS30S` | `Initiation_B1` | 0.8 | release | `re0000000459` | — |
| `re0000000463` | `IF2_GTP` + `RS30S_IF3` → `RS30S_IF3_IF2_GTP` | `Initiation_B1` | 280.0 | binding | `re0000000464` | — |
| `re0000000464` | `RS30S_IF3_IF2_GTP` → `IF2_GTP` + `RS30S_IF3` | `Initiation_B1` | 12.0 | release | `re0000000463` | — |
| `re0000000469` | `RS30S_IF3` + `mRNA` → `RS30S_IF3_mRNA` | `Initiation_B1` | 36.0 | binding | `re0000000470` | — |
| `re0000000470` | `RS30S_IF3_mRNA` → `RS30S_IF3` + `mRNA` | `Initiation_B1` | 0.7 | release | `re0000000469` | — |
| `re0000000471` | `IF2_GTP` + `RS30S_IF3_mRNA` → `RS30S_IF3_IF2_GTP_mRNA` | `Initiation_B1` | 280.0 | binding | `re0000000472` | — |
| `re0000000472` | `RS30S_IF3_IF2_GTP_mRNA` → `IF2_GTP` + `RS30S_IF3_mRNA` | `Initiation_B1` | 12.0 | release | `re0000000471` | — |
| `re0000000477` | `IF2_GTP` + `RS30S_IF3_fMettRNAfMetCAU_mRNA` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 280.0 | binding | `re0000000478` | — |
| `re0000000478` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF2_GTP` + `RS30S_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 12.0 | release | `re0000000477` | — |
| `re0000000481` | `RS30S_IF3_IF2_GTP` + `mRNA` → `RS30S_IF3_IF2_GTP_mRNA` | `Initiation_B1` | 36.0 | binding | `re0000000482` | — |
| `re0000000482` | `RS30S_IF3_IF2_GTP_mRNA` → `RS30S_IF3_IF2_GTP` + `mRNA` | `Initiation_B1` | 0.7 | release | `re0000000481` | — |
| `re0000000483` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` + `mRNA` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 36.0 | binding | `re0000000484` | — |
| `re0000000484` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0.7 | release | `re0000000483` | — |
| `re0000000489` | `IF3` + `RS70S_IF1` → `RS70S_IF1_IF3` | `Initiation_B1` | 0.082 | binding | `re0000000490` | — |
| `re0000000490` | `RS70S_IF1_IF3` → `IF3` + `RS70S_IF1` | `Initiation_B1` | 0.26 | release | `re0000000489` | — |
| `re0000000491` | `IF3` + `RS30S_IF1` → `RS30S_IF1_IF3` | `Initiation_B1` | 1100.0 | binding | `re0000000492` | — |
| `re0000000492` | `RS30S_IF1_IF3` → `IF3` + `RS30S_IF1` | `Initiation_B1` | 0.08 | release | `re0000000491` | — |
| `re0000000495` | `IF2_GTP` + `RS30S_IF1_IF3` → `RS30S_IF1_IF3_IF2_GTP` | `Initiation_B1` | 220.0 | binding | `re0000000496` | — |
| `re0000000496` | `RS30S_IF1_IF3_IF2_GTP` → `IF2_GTP` + `RS30S_IF1_IF3` | `Initiation_B1` | 1.0 | release | `re0000000495` | — |
| `re0000000501` | `IF1` + `RS70S` → `RS70S_IF1` | `Initiation_B1` | 20.0 | binding | `re0000000502` | — |
| `re0000000502` | `RS70S_IF1` → `IF1` + `RS70S` | `Initiation_B1` | 0.7 | release | `re0000000501` | — |
| `re0000000503` | `IF1` + `RS30S` → `RS30S_IF1` | `Initiation_B1` | 20.0 | binding | `re0000000504` | — |
| `re0000000504` | `RS30S_IF1` → `IF1` + `RS30S` | `Initiation_B1` | 0.7 | release | `re0000000503` | — |
| `re0000000505` | `IF1` + `RS70S_IF3` → `RS70S_IF1_IF3` | `Initiation_B1` | 20.0 | binding | `re0000000506` | — |
| `re0000000506` | `RS70S_IF1_IF3` → `IF1` + `RS70S_IF3` | `Initiation_B1` | 0.7 | release | `re0000000505` | — |
| `re0000000507` | `IF1` + `RS30S_IF3` → `RS30S_IF1_IF3` | `Initiation_B1` | 20.0 | binding | `re0000000508` | — |
| `re0000000508` | `RS30S_IF1_IF3` → `IF1` + `RS30S_IF3` | `Initiation_B1` | 0.7 | release | `re0000000507` | — |
| `re0000000509` | `IF1` + `RS30S_IF3_IF2_GTP` → `RS30S_IF1_IF3_IF2_GTP` | `Initiation_B1` | 12.0 | binding | `re0000000510` | — |
| `re0000000510` | `RS30S_IF1_IF3_IF2_GTP` → `IF1` + `RS30S_IF3_IF2_GTP` | `Initiation_B1` | 0.02 | release | `re0000000509` | — |
| `re0000000511` | `IF1` + `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B1` | 12.0 | binding | `re0000000512` | — |
| `re0000000512` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` → `IF1` + `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B1` | 0.02 | release | `re0000000511` | — |
| `re0000000513` | `RS30S_IF1_IF3` + `mRNA` → `RS30S_IF1_IF3_mRNA` | `Initiation_B1` | 36.0 | binding | `re0000000514` | — |
| `re0000000514` | `RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3` + `mRNA` | `Initiation_B1` | 0.7 | release | `re0000000513` | — |
| `re0000000515` | `IF2_GTP` + `RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_mRNA` | `Initiation_B1` | 220.0 | binding | `re0000000516` | — |
| `re0000000516` | `RS30S_IF1_IF3_IF2_GTP_mRNA` → `IF2_GTP` + `RS30S_IF1_IF3_mRNA` | `Initiation_B1` | 1.0 | release | `re0000000515` | — |
| `re0000000521` | `IF2_GTP` + `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 320.0 | binding | `re0000000522` | — |
| `re0000000522` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF2_GTP` + `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 0.015 | release | `re0000000521` | — |
| `re0000000525` | `RS30S_IF1_IF3_IF2_GTP` + `mRNA` → `RS30S_IF1_IF3_IF2_GTP_mRNA` | `Initiation_B1` | 36.0 | binding | `re0000000526` | — |
| `re0000000526` | `RS30S_IF1_IF3_IF2_GTP_mRNA` → `RS30S_IF1_IF3_IF2_GTP` + `mRNA` | `Initiation_B1` | 0.7 | release | `re0000000525` | — |
| `re0000000527` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` + `mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 36.0 | binding | `re0000000528` | — |
| `re0000000528` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0.006 | release | `re0000000527` | — |
| `re0000000531` | `IF1` + `RS30S_IF3_mRNA` → `RS30S_IF1_IF3_mRNA` | `Initiation_B1` | 20.0 | binding | `re0000000532` | — |
| `re0000000532` | `RS30S_IF1_IF3_mRNA` → `IF1` + `RS30S_IF3_mRNA` | `Initiation_B1` | 0.7 | release | `re0000000531` | — |
| `re0000000533` | `IF1` + `RS30S_IF3_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 20.0 | binding | `re0000000534` | — |
| `re0000000534` | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1` + `RS30S_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 0.7 | release | `re0000000533` | — |
| `re0000000535` | `IF1` + `RS30S_IF3_IF2_GTP_mRNA` → `RS30S_IF1_IF3_IF2_GTP_mRNA` | `Initiation_B1` | 12.0 | binding | `re0000000536` | — |
| `re0000000536` | `RS30S_IF1_IF3_IF2_GTP_mRNA` → `IF1` + `RS30S_IF3_IF2_GTP_mRNA` | `Initiation_B1` | 0.02 | release | `re0000000535` | — |
| `re0000000537` | `IF1` + `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 16.0 | binding | `re0000000538` | — |
| `re0000000538` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF1` + `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 0.0025 | release | `re0000000537` | — |
| `re0000000609` | `IF2_GTP` + `RS30S` → `RS30S_IF2_GTP` | `Initiation_B2` | 280.0 | binding | `re0000000610` | — |
| `re0000000610` | `RS30S_IF2_GTP` → `IF2_GTP` + `RS30S` | `Initiation_B2` | 12.0 | release | `re0000000609` | — |
| `re0000000615` | `IF3` + `RS30S_IF2_GTP` → `RS30S_IF3_IF2_GTP` | `Initiation_B2` | 1160.0 | binding | `re0000000616` | — |
| `re0000000616` | `RS30S_IF3_IF2_GTP` → `IF3` + `RS30S_IF2_GTP` | `Initiation_B2` | 0.8 | release | `re0000000615` | — |
| `re0000000617` | `IF3` + `RS30S_IF2_GTP_fMettRNAfMetCAU` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 1160.0 | binding | `re0000000618` | — |
| `re0000000618` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` → `IF3` + `RS30S_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 0.8 | release | `re0000000617` | — |
| `re0000000619` | `RS30S` + `mRNA` → `RS30S_mRNA` | `Initiation_B2` | 36.0 | binding | `re0000000620` | — |
| `re0000000620` | `RS30S_mRNA` → `RS30S` + `mRNA` | `Initiation_B2` | 0.7 | release | `re0000000619` | — |
| `re0000000625` | `IF2_GTP` + `RS30S_mRNA` → `RS30S_IF2_GTP_mRNA` | `Initiation_B2` | 280.0 | binding | `re0000000626` | — |
| `re0000000626` | `RS30S_IF2_GTP_mRNA` → `IF2_GTP` + `RS30S_mRNA` | `Initiation_B2` | 12.0 | release | `re0000000625` | — |
| `re0000000627` | `IF2_GTP` + `RS30S_fMettRNAfMetCAU_mRNA` → `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 280.0 | binding | `re0000000628` | — |
| `re0000000628` | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF2_GTP` + `RS30S_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 12.0 | release | `re0000000627` | — |
| `re0000000631` | `RS30S_IF2_GTP` + `mRNA` → `RS30S_IF2_GTP_mRNA` | `Initiation_B2` | 36.0 | binding | `re0000000632` | — |
| `re0000000632` | `RS30S_IF2_GTP_mRNA` → `RS30S_IF2_GTP` + `mRNA` | `Initiation_B2` | 0.7 | release | `re0000000631` | — |
| `re0000000633` | `RS30S_IF2_GTP_fMettRNAfMetCAU` + `mRNA` → `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 36.0 | binding | `re0000000634` | — |
| `re0000000634` | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF2_GTP_fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0.7 | release | `re0000000633` | — |
| `re0000000635` | `IF3` + `RS30S_mRNA` → `RS30S_IF3_mRNA` | `Initiation_B2` | 1160.0 | binding | `re0000000636` | — |
| `re0000000636` | `RS30S_IF3_mRNA` → `IF3` + `RS30S_mRNA` | `Initiation_B2` | 0.8 | release | `re0000000635` | — |
| `re0000000637` | `IF3` + `RS30S_fMettRNAfMetCAU_mRNA` → `RS30S_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 1160.0 | binding | `re0000000638` | — |
| `re0000000638` | `RS30S_IF3_fMettRNAfMetCAU_mRNA` → `IF3` + `RS30S_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 0.8 | release | `re0000000637` | — |
| `re0000000639` | `IF3` + `RS30S_IF2_GTP_mRNA` → `RS30S_IF3_IF2_GTP_mRNA` | `Initiation_B2` | 1160.0 | binding | `re0000000640` | — |
| `re0000000640` | `RS30S_IF3_IF2_GTP_mRNA` → `IF3` + `RS30S_IF2_GTP_mRNA` | `Initiation_B2` | 0.8 | release | `re0000000639` | — |
| `re0000000641` | `IF3` + `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 1160.0 | binding | `re0000000642` | — |
| `re0000000642` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF3` + `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 0.8 | release | `re0000000641` | — |
| `re0000000643` | `IF2_GTP` + `RS30S_IF1` → `RS30S_IF1_IF2_GTP` | `Initiation_B2` | 220.0 | binding | `re0000000644` | — |
| `re0000000644` | `RS30S_IF1_IF2_GTP` → `IF2_GTP` + `RS30S_IF1` | `Initiation_B2` | 1.0 | release | `re0000000643` | — |
| `re0000000649` | `IF1` + `RS30S_IF2_GTP` → `RS30S_IF1_IF2_GTP` | `Initiation_B2` | 20.0 | binding | `re0000000650` | — |
| `re0000000650` | `RS30S_IF1_IF2_GTP` → `IF1` + `RS30S_IF2_GTP` | `Initiation_B2` | 0.7 | release | `re0000000649` | — |
| `re0000000651` | `IF1` + `RS30S_IF2_GTP_fMettRNAfMetCAU` → `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 20.0 | binding | `re0000000652` | — |
| `re0000000652` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` → `IF1` + `RS30S_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 0.7 | release | `re0000000651` | — |
| `re0000000653` | `IF3` + `RS30S_IF1_IF2_GTP` → `RS30S_IF1_IF3_IF2_GTP` | `Initiation_B2` | 1100.0 | binding | `re0000000654` | — |
| `re0000000654` | `RS30S_IF1_IF3_IF2_GTP` → `IF3` + `RS30S_IF1_IF2_GTP` | `Initiation_B2` | 0.08 | release | `re0000000653` | — |
| `re0000000655` | `IF3` + `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 1100.0 | binding | `re0000000656` | — |
| `re0000000656` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` → `IF3` + `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 0.08 | release | `re0000000655` | — |
| `re0000000657` | `IF2_GTP` + `RS30S_IF1_mRNA` → `RS30S_IF1_IF2_GTP_mRNA` | `Initiation_B2` | 220.0 | binding | `re0000000658` | — |
| `re0000000658` | `RS30S_IF1_IF2_GTP_mRNA` → `IF2_GTP` + `RS30S_IF1_mRNA` | `Initiation_B2` | 1.0 | release | `re0000000657` | — |
| `re0000000663` | `IF2_GTP` + `RS30S_IF1_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 220.0 | binding | `re0000000664` | — |
| `re0000000664` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF2_GTP` + `RS30S_IF1_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 1.0 | release | `re0000000663` | — |
| `re0000000667` | `IF3` + `RS30S_IF1_mRNA` → `RS30S_IF1_IF3_mRNA` | `Initiation_B2` | 1100.0 | binding | `re0000000668` | — |
| `re0000000668` | `RS30S_IF1_IF3_mRNA` → `IF3` + `RS30S_IF1_mRNA` | `Initiation_B2` | 0.08 | release | `re0000000667` | — |
| `re0000000669` | `IF3` + `RS30S_IF1_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 1100.0 | binding | `re0000000670` | — |
| `re0000000670` | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF3` + `RS30S_IF1_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 0.08 | release | `re0000000669` | — |
| `re0000000671` | `IF3` + `RS30S_IF1_IF2_GTP_mRNA` → `RS30S_IF1_IF3_IF2_GTP_mRNA` | `Initiation_B2` | 1100.0 | binding | `re0000000672` | — |
| `re0000000672` | `RS30S_IF1_IF3_IF2_GTP_mRNA` → `IF3` + `RS30S_IF1_IF2_GTP_mRNA` | `Initiation_B2` | 0.08 | release | `re0000000671` | — |
| `re0000000673` | `IF3` + `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 1100.0 | binding | `re0000000674` | — |
| `re0000000674` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF3` + `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 0.08 | release | `re0000000673` | — |
| `re0000000675` | `RS30S_IF1` + `mRNA` → `RS30S_IF1_mRNA` | `Initiation_B2` | 36.0 | binding | `re0000000676` | — |
| `re0000000676` | `RS30S_IF1_mRNA` → `RS30S_IF1` + `mRNA` | `Initiation_B2` | 0.7 | release | `re0000000675` | — |
| `re0000000677` | `IF1` + `RS30S_mRNA` → `RS30S_IF1_mRNA` | `Initiation_B2` | 20.0 | binding | `re0000000678` | — |
| `re0000000678` | `RS30S_IF1_mRNA` → `IF1` + `RS30S_mRNA` | `Initiation_B2` | 0.7 | release | `re0000000677` | — |
| `re0000000679` | `IF1` + `RS30S_IF2_GTP_mRNA` → `RS30S_IF1_IF2_GTP_mRNA` | `Initiation_B2` | 20.0 | binding | `re0000000680` | — |
| `re0000000680` | `RS30S_IF1_IF2_GTP_mRNA` → `IF1` + `RS30S_IF2_GTP_mRNA` | `Initiation_B2` | 0.7 | release | `re0000000679` | — |
| `re0000000681` | `RS30S_IF1_IF2_GTP` + `mRNA` → `RS30S_IF1_IF2_GTP_mRNA` | `Initiation_B2` | 36.0 | binding | `re0000000682` | — |
| `re0000000682` | `RS30S_IF1_IF2_GTP_mRNA` → `RS30S_IF1_IF2_GTP` + `mRNA` | `Initiation_B2` | 0.7 | release | `re0000000681` | — |
| `re0000000683` | `IF1` + `RS30S_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 20.0 | binding | `re0000000684` | — |
| `re0000000684` | `RS30S_IF1_fMettRNAfMetCAU_mRNA` → `IF1` + `RS30S_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 0.7 | release | `re0000000683` | — |
| `re0000000685` | `IF1` + `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 20.0 | binding | `re0000000686` | — |
| `re0000000686` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF1` + `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 0.7 | release | `re0000000685` | — |
| `re0000000687` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` + `mRNA` → `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 36.0 | binding | `re0000000688` | — |
| `re0000000688` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0.7 | release | `re0000000687` | — |

</details>

<details>
<summary><strong>INIT_energy_commitment</strong> — 12 reactions; author k&gt;0: 10</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000445` | `GTP` + `IF2` → `IF2_GTP` | `Initiation_A` | 10.0 | binding | `re0000000446` | — |
| `re0000000446` | `IF2_GTP` → `GTP` + `IF2` | `Initiation_A` | 67.0 | release | `re0000000445` | — |
| `re0000000447` | `GDP` + `IF2` → `IF2_GDP` | `Initiation_A` | 10.0 | binding | `re0000000448` | — |
| `re0000000448` | `IF2_GDP` → `GDP` + `IF2` | `Initiation_A` | 16.0 | release | `re0000000447` | — |
| `re0000000715` | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 2.3 | transition | `re0000000716` | — |
| `re0000000716` | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 2.1 | transition | `re0000000715` | — |
| `re0000000717` | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 2.3 | transition | `re0000000718` | — |
| `re0000000718` | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 2.1 | transition | `re0000000717` | — |
| `re0000000721` | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `PO4` + `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 12.0 | release | `re0000000745` | — |
| `re0000000722` | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `PO4` + `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 12.0 | release | `re0000000746` | — |
| `re0000000745` | `PO4` + `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0 | binding | `re0000000721` | — |
| `re0000000746` | `PO4` + `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0 | binding | `re0000000722` | — |

</details>

<details>
<summary><strong>INIT_factor_release</strong> — 28 reactions; author k&gt;0: 21</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000539` | `IF1` + `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` (+1 shared) | 16.0 | binding | `re0000000540` | — |
| `re0000000540` | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF1` + `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` (+1 shared) | 0.0025 | release | `re0000000539` | — |
| `re0000000719` | `IF1` + `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 16.0 | binding | `re0000000720` | — |
| `re0000000720` | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `IF1` + `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0.0025 | release | `re0000000719` | — |
| `re0000000723` | `IF1` + `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 16.0 | binding | `re0000000724` | — |
| `re0000000724` | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF1` + `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0.0025 | release | `re0000000723` | — |
| `re0000000725` | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP` + `RS70S_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 4.0 | release | `re0000000751` | — |
| `re0000000726` | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP` + `elRS70SAGGU0002_fMettRNAfMetCAU` | `Initiation_C` | 4.0 | release | `re0000000752` | — |
| `re0000000747` | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3` + `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 1000.0 | release | `re0000000748` | — |
| `re0000000748` | `IF3` + `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0 | binding | `re0000000747` | — |
| `re0000000749` | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP` + `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 4.0 | release | `re0000000750` | — |
| `re0000000750` | `IF2_GDP` + `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 200.0 | binding | `re0000000749` | — |
| `re0000000751` | `IF2_GDP` + `RS70S_IF3_fMettRNAfMetCAU_mRNA` → `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 200.0 | binding | `re0000000725` | — |
| `re0000000752` | `IF2_GDP` + `elRS70SAGGU0002_fMettRNAfMetCAU` → `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 200.0 | binding | `re0000000726` | — |
| `re0000000753` | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1` + `RS70S_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 1000.0 | release | `re0000000754` | — |
| `re0000000754` | `IF1` + `RS70S_IF3_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0 | binding | `re0000000753` | — |
| `re0000000755` | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF3` + `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 1000.0 | release | `re0000000756` | — |
| `re0000000756` | `IF3` + `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0 | binding | `re0000000755` | — |
| `re0000000757` | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF1` + `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 1000.0 | release | `re0000000758` | — |
| `re0000000758` | `IF1` + `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0 | binding | `re0000000757` | — |
| `re0000000759` | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` → `IF2_GDP` + `RS70S_IF1_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 4.0 | release | `re0000000760` | — |
| `re0000000760` | `IF2_GDP` + `RS70S_IF1_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 200.0 | binding | `re0000000759` | — |
| `re0000000761` | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF3` + `RS70S_IF1_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 1000.0 | release | `re0000000762` | — |
| `re0000000762` | `IF3` + `RS70S_IF1_fMettRNAfMetCAU_mRNA` → `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0 | binding | `re0000000761` | — |
| `re0000000763` | `RS70S_IF3_fMettRNAfMetCAU_mRNA` → `IF3` + `elRS70SAGGU0002_fMettRNAfMetCAU` | `Initiation_C` | 1000.0 | release | `re0000000764` | — |
| `re0000000764` | `IF3` + `elRS70SAGGU0002_fMettRNAfMetCAU` → `RS70S_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0 | binding | `re0000000763` | — |
| `re0000000765` | `RS70S_IF1_fMettRNAfMetCAU_mRNA` → `IF1` + `elRS70SAGGU0002_fMettRNAfMetCAU` | `Initiation_C` | 1000.0 | release | `re0000000766` | — |
| `re0000000766` | `IF1` + `elRS70SAGGU0002_fMettRNAfMetCAU` → `RS70S_IF1_fMettRNAfMetCAU_mRNA` | `Initiation_C` | 0 | binding | `re0000000765` | — |

</details>

<details>
<summary><strong>INIT_tRNA_recruitment</strong> — 42 reactions; author k&gt;0: 42</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000449` | `IF2_GTP` + `fMettRNAfMetCAU` → `IF2_GTP_fMettRNAfMetCAU` | `Initiation_A` | 40.0 | binding | `re0000000450` | — |
| `re0000000450` | `IF2_GTP_fMettRNAfMetCAU` → `IF2_GTP` + `fMettRNAfMetCAU` | `Initiation_A` | 40.0 | release | `re0000000449` | — |
| `re0000000465` | `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF3` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B1` | 280.0 | binding | `re0000000466` | — |
| `re0000000466` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` → `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF3` | `Initiation_B1` | 1.5 | release | `re0000000465` | — |
| `re0000000467` | `RS30S_IF3_IF2_GTP` + `fMettRNAfMetCAU` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B1` | 5.0 | binding | `re0000000468` | — |
| `re0000000468` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` → `RS30S_IF3_IF2_GTP` + `fMettRNAfMetCAU` | `Initiation_B1` | 1.5 | release | `re0000000467` | — |
| `re0000000473` | `RS30S_IF3_mRNA` + `fMettRNAfMetCAU` → `RS30S_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 5.0 | binding | `re0000000474` | — |
| `re0000000474` | `RS30S_IF3_fMettRNAfMetCAU_mRNA` → `RS30S_IF3_mRNA` + `fMettRNAfMetCAU` | `Initiation_B1` | 1.5 | release | `re0000000473` | — |
| `re0000000475` | `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF3_mRNA` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 280.0 | binding | `re0000000476` | — |
| `re0000000476` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF3_mRNA` | `Initiation_B1` | 1.5 | release | `re0000000475` | — |
| `re0000000479` | `RS30S_IF3_IF2_GTP_mRNA` + `fMettRNAfMetCAU` → `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 5.0 | binding | `re0000000480` | — |
| `re0000000480` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF3_IF2_GTP_mRNA` + `fMettRNAfMetCAU` | `Initiation_B1` | 1.5 | release | `re0000000479` | — |
| `re0000000497` | `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF1_IF3` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B1` | 220.0 | binding | `re0000000498` | — |
| `re0000000498` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` → `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF1_IF3` | `Initiation_B1` | 1.0 | release | `re0000000497` | — |
| `re0000000499` | `RS30S_IF1_IF3_IF2_GTP` + `fMettRNAfMetCAU` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B1` | 5.0 | binding | `re0000000500` | — |
| `re0000000500` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` → `RS30S_IF1_IF3_IF2_GTP` + `fMettRNAfMetCAU` | `Initiation_B1` | 1.5 | release | `re0000000499` | — |
| `re0000000517` | `RS30S_IF1_IF3_mRNA` + `fMettRNAfMetCAU` → `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 5.0 | binding | `re0000000518` | — |
| `re0000000518` | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF3_mRNA` + `fMettRNAfMetCAU` | `Initiation_B1` | 1.5 | release | `re0000000517` | — |
| `re0000000519` | `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF1_IF3_mRNA` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 220.0 | binding | `re0000000520` | — |
| `re0000000520` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF1_IF3_mRNA` | `Initiation_B1` | 1.0 | release | `re0000000519` | — |
| `re0000000523` | `RS30S_IF1_IF3_IF2_GTP_mRNA` + `fMettRNAfMetCAU` → `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B1` | 5.0 | binding | `re0000000524` | — |
| `re0000000524` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF3_IF2_GTP_mRNA` + `fMettRNAfMetCAU` | `Initiation_B1` | 1.5 | release | `re0000000523` | — |
| `re0000000611` | `IF2_GTP_fMettRNAfMetCAU` + `RS30S` → `RS30S_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 280.0 | binding | `re0000000612` | — |
| `re0000000612` | `RS30S_IF2_GTP_fMettRNAfMetCAU` → `IF2_GTP_fMettRNAfMetCAU` + `RS30S` | `Initiation_B2` | 1.5 | release | `re0000000611` | — |
| `re0000000613` | `RS30S_IF2_GTP` + `fMettRNAfMetCAU` → `RS30S_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 5.0 | binding | `re0000000614` | — |
| `re0000000614` | `RS30S_IF2_GTP_fMettRNAfMetCAU` → `RS30S_IF2_GTP` + `fMettRNAfMetCAU` | `Initiation_B2` | 1.5 | release | `re0000000613` | — |
| `re0000000621` | `RS30S_mRNA` + `fMettRNAfMetCAU` → `RS30S_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 5.0 | binding | `re0000000622` | — |
| `re0000000622` | `RS30S_fMettRNAfMetCAU_mRNA` → `RS30S_mRNA` + `fMettRNAfMetCAU` | `Initiation_B2` | 1.5 | release | `re0000000621` | — |
| `re0000000623` | `IF2_GTP_fMettRNAfMetCAU` + `RS30S_mRNA` → `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 280.0 | binding | `re0000000624` | — |
| `re0000000624` | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF2_GTP_fMettRNAfMetCAU` + `RS30S_mRNA` | `Initiation_B2` | 1.5 | release | `re0000000623` | — |
| `re0000000629` | `RS30S_IF2_GTP_mRNA` + `fMettRNAfMetCAU` → `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 5.0 | binding | `re0000000630` | — |
| `re0000000630` | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF2_GTP_mRNA` + `fMettRNAfMetCAU` | `Initiation_B2` | 1.5 | release | `re0000000629` | — |
| `re0000000645` | `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF1` → `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 220.0 | binding | `re0000000646` | — |
| `re0000000646` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` → `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF1` | `Initiation_B2` | 1.0 | release | `re0000000645` | — |
| `re0000000647` | `RS30S_IF1_IF2_GTP` + `fMettRNAfMetCAU` → `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` | `Initiation_B2` | 5.0 | binding | `re0000000648` | — |
| `re0000000648` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` → `RS30S_IF1_IF2_GTP` + `fMettRNAfMetCAU` | `Initiation_B2` | 1.5 | release | `re0000000647` | — |
| `re0000000659` | `RS30S_IF1_mRNA` + `fMettRNAfMetCAU` → `RS30S_IF1_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 5.0 | binding | `re0000000660` | — |
| `re0000000660` | `RS30S_IF1_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_mRNA` + `fMettRNAfMetCAU` | `Initiation_B2` | 1.5 | release | `re0000000659` | — |
| `re0000000661` | `RS30S_IF1_IF2_GTP_mRNA` + `fMettRNAfMetCAU` → `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 5.0 | binding | `re0000000662` | — |
| `re0000000662` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` → `RS30S_IF1_IF2_GTP_mRNA` + `fMettRNAfMetCAU` | `Initiation_B2` | 1.5 | release | `re0000000661` | — |
| `re0000000665` | `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF1_mRNA` → `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` | `Initiation_B2` | 220.0 | binding | `re0000000666` | — |
| `re0000000666` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` → `IF2_GTP_fMettRNAfMetCAU` + `RS30S_IF1_mRNA` | `Initiation_B2` | 1.0 | release | `re0000000665` | — |

</details>

### Elongation — 88 source directions

<details>
<summary><strong>ELONG_aa_tRNA_delivery</strong> — 24 reactions; author k&gt;0: 12</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000013` | `EFTu_GTP_GlytRNAGlyGCC` + `elRS70SAGGU0002_fMet` → `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 140.0 | binding | `re0000000021` | — |
| `re0000000017` | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` → `EFTu_GDP` + `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 7.0 | release | `re0000000061` | CHAIN_01 |
| `re0000000021` | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` → `EFTu_GTP_GlytRNAGlyGCC` + `elRS70SAGGU0002_fMet` | `Elongation_Ca2_pept0002` | 0.23 | release | `re0000000013` | — |
| `re0000000026` | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` → `GlytRNAGlyGCC` + `elRS70SAGGU0002_fMet_EFTu_GDP` | `Elongation_Ca2_pept0002` | 0 | release | `re0000000063` | — |
| `re0000000027` | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` → `GlytRNAGlyGCC` + `elRS70SAGGU0002_fMet` | `Elongation_Ca2_pept0002` | 0 | release | `re0000000064` | — |
| `re0000000028` | `elRS70SAGGU0002_fMet_EFTu_GDP` → `EFTu_GDP` + `elRS70SAGGU0002_fMet` | `Elongation_Ca2_pept0002` | 1000.0 | release | `re0000000065` | — |
| `re0000000061` | `EFTu_GDP` + `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` → `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 0 | binding | `re0000000017` | — |
| `re0000000063` | `GlytRNAGlyGCC` + `elRS70SAGGU0002_fMet_EFTu_GDP` → `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 0 | binding | `re0000000026` | — |
| `re0000000064` | `GlytRNAGlyGCC` + `elRS70SAGGU0002_fMet` → `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 0 | binding | `re0000000027` | — |
| `re0000000065` | `EFTu_GDP` + `elRS70SAGGU0002_fMet` → `elRS70SAGGU0002_fMet_EFTu_GDP` | `Elongation_Ca2_pept0002` | 0 | binding | `re0000000028` | — |
| `re0000000074` | `EFTu_GTP_GlytRNAGlyGCC` + `elRS70SAGGU0003_Pept0002` → `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 140.0 | binding | `re0000000082` | — |
| `re0000000078` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` → `EFTu_GDP` + `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 7.0 | release | `re0000000119` | CHAIN_02 |
| `re0000000082` | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` → `EFTu_GTP_GlytRNAGlyGCC` + `elRS70SAGGU0003_Pept0002` | `Elongation_Ca2_pept0003` | 0.23 | release | `re0000000074` | — |
| `re0000000087` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` → `GlytRNAGlyGCC` + `elRS70SAGGU0003_Pept0002_EFTu_GDP` | `Elongation_Ca2_pept0003` | 0 | release | `re0000000121` | — |
| `re0000000088` | `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` → `GlytRNAGlyGCC` + `elRS70SAGGU0003_Pept0002` | `Elongation_Ca2_pept0003` | 0 | release | `re0000000122` | — |
| `re0000000089` | `elRS70SAGGU0003_Pept0002_EFTu_GDP` → `EFTu_GDP` + `elRS70SAGGU0003_Pept0002` | `Elongation_Ca2_pept0003` | 1000.0 | release | `re0000000123` | — |
| `re0000000119` | `EFTu_GDP` + `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` → `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 0 | binding | `re0000000078` | — |
| `re0000000121` | `GlytRNAGlyGCC` + `elRS70SAGGU0003_Pept0002_EFTu_GDP` → `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 0 | binding | `re0000000087` | — |
| `re0000000122` | `GlytRNAGlyGCC` + `elRS70SAGGU0003_Pept0002` → `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 0 | binding | `re0000000088` | — |
| `re0000000123` | `EFTu_GDP` + `elRS70SAGGU0003_Pept0002` → `elRS70SAGGU0003_Pept0002_EFTu_GDP` | `Elongation_Ca2_pept0003` | 0 | binding | `re0000000089` | — |
| `re0000000275` | `EFTu_GTP` + `GlytRNAGlyGCC` → `EFTu_GTP_GlytRNAGlyGCC` | `Elongation_A_Gly` | 1.5 | binding | `re0000000276` | — |
| `re0000000276` | `EFTu_GTP_GlytRNAGlyGCC` → `EFTu_GTP` + `GlytRNAGlyGCC` | `Elongation_A_Gly` | 0.0013 | release | `re0000000275` | — |
| `re0000000288` | `EFTu_GTP` + `MettRNAfMetCAU` → `EFTu_GTP_MettRNAfMetCAU` | `Elongation_A_Met` | 1.5 | binding | `re0000000289` | PAIR_08 |
| `re0000000289` | `EFTu_GTP_MettRNAfMetCAU` → `EFTu_GTP` + `MettRNAfMetCAU` | `Elongation_A_Met` | 0.0453 | release | `re0000000288` | PAIR_08 |

</details>

<details>
<summary><strong>ELONG_energy_coupling</strong> — 48 reactions; author k&gt;0: 41</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000014` | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` → `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 260.0 | transition | `re0000000015` | CHAIN_01 |
| `re0000000015` | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` → `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 0 | transition | `re0000000014` | — |
| `re0000000016` | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` → `PO4` + `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 1000.0 | release | `re0000000060` | CHAIN_01 |
| `re0000000019` | `EFG_GTP` + `elRS70SBGGU0002_Pept0002tRNAGlyGCC` → `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP` | `Elongation_Ca2_pept0002` | 30.0 | binding | `re0000000020` | — |
| `re0000000020` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP` → `EFG_GTP` + `elRS70SBGGU0002_Pept0002tRNAGlyGCC` | `Elongation_Ca2_pept0002` | 25.0 | release | `re0000000019` | — |
| `re0000000022` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP` → `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4` | `Elongation_Ca2_pept0002` | 31.0 | transition | `re0000000023` | — |
| `re0000000023` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4` → `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP` | `Elongation_Ca2_pept0002` | 5.0 | transition | `re0000000022` | — |
| `re0000000060` | `PO4` + `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` → `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 0 | binding | `re0000000016` | — |
| `re0000000075` | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` → `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 260.0 | transition | `re0000000076` | CHAIN_02 |
| `re0000000076` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC` → `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 0 | transition | `re0000000075` | — |
| `re0000000077` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC` → `PO4` + `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 1000.0 | release | `re0000000118` | CHAIN_02 |
| `re0000000080` | `EFG_GTP` + `elRS70SBGGU0003_Pept0003tRNAGlyGCC` → `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP` | `Elongation_Ca2_pept0003` | 30.0 | binding | `re0000000081` | — |
| `re0000000081` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP` → `EFG_GTP` + `elRS70SBGGU0003_Pept0003tRNAGlyGCC` | `Elongation_Ca2_pept0003` | 25.0 | release | `re0000000080` | — |
| `re0000000083` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP` → `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4` | `Elongation_Ca2_pept0003` | 31.0 | transition | `re0000000084` | — |
| `re0000000084` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4` → `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP` | `Elongation_Ca2_pept0003` | 5.0 | transition | `re0000000083` | — |
| `re0000000118` | `PO4` + `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` → `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 0 | binding | `re0000000077` | — |
| `re0000000261` | `EFTs` + `EFTu` → `EFTu_EFTs` | `Elongation_A_Gly` (+1 shared) | 10.0 | binding | `re0000000262` | — |
| `re0000000262` | `EFTu_EFTs` → `EFTs` + `EFTu` | `Elongation_A_Gly` (+1 shared) | 0.03 | release | `re0000000261` | — |
| `re0000000263` | `EFTu_EFTs` + `GDP` → `EFTu_GDP_EFTs` | `Elongation_A_Gly` (+1 shared) | 14.0 | binding | `re0000000264` | — |
| `re0000000264` | `EFTu_GDP_EFTs` → `EFTu_EFTs` + `GDP` | `Elongation_A_Gly` (+1 shared) | 125.0 | release | `re0000000263` | — |
| `re0000000265` | `EFTu_GDP_EFTs` → `EFTs` + `EFTu_GDP` | `Elongation_A_Gly` (+1 shared) | 350.0 | release | `re0000000266` | — |
| `re0000000266` | `EFTs` + `EFTu_GDP` → `EFTu_GDP_EFTs` | `Elongation_A_Gly` (+1 shared) | 60.0 | binding | `re0000000265` | — |
| `re0000000267` | `EFTu_GDP` → `EFTu` + `GDP` | `Elongation_A_Gly` (+1 shared) | 0.002 | release | `re0000000268` | — |
| `re0000000268` | `EFTu` + `GDP` → `EFTu_GDP` | `Elongation_A_Gly` (+1 shared) | 2.0 | binding | `re0000000267` | — |
| `re0000000269` | `EFTu_EFTs` + `GTP` → `EFTu_GTP_EFTs` | `Elongation_A_Gly` (+1 shared) | 6.0 | binding | `re0000000270` | — |
| `re0000000270` | `EFTu_GTP_EFTs` → `EFTu_EFTs` + `GTP` | `Elongation_A_Gly` (+1 shared) | 85.0 | release | `re0000000269` | — |
| `re0000000271` | `EFTu_GTP_EFTs` → `EFTs` + `EFTu_GTP` | `Elongation_A_Gly` (+1 shared) | 60.0 | release | `re0000000272` | — |
| `re0000000272` | `EFTs` + `EFTu_GTP` → `EFTu_GTP_EFTs` | `Elongation_A_Gly` (+1 shared) | 30.0 | binding | `re0000000271` | — |
| `re0000000273` | `EFTu` + `GTP` → `EFTu_GTP` | `Elongation_A_Gly` (+1 shared) | 0.5 | binding | `re0000000274` | — |
| `re0000000274` | `EFTu_GTP` → `EFTu` + `GTP` | `Elongation_A_Gly` (+1 shared) | 0.03 | release | `re0000000273` | — |
| `re0000000292` | `EFG_GDP` → `EFG` + `GDP` | `Elongation_B` | 300.0 | release | `re0000000293` | — |
| `re0000000293` | `EFG` + `GDP` → `EFG_GDP` | `Elongation_B` | 17.6 | binding | `re0000000292` | — |
| `re0000000294` | `EFG` + `GTP` → `EFG_GTP` | `Elongation_B` | 0.58 | binding | `re0000000295` | — |
| `re0000000295` | `EFG_GTP` → `EFG` + `GTP` | `Elongation_B` | 13.0 | release | `re0000000294` | — |
| `re0000000298` | `EFG_GTP` + `RS50S` → `RS50S_EFG_GTP` | `Elongation_B` | 30.0 | binding | `re0000000299` | — |
| `re0000000299` | `RS50S_EFG_GTP` → `EFG_GTP` + `RS50S` | `Elongation_B` | 25.0 | release | `re0000000298` | — |
| `re0000000300` | `EFG_GTP` + `RS70S` → `RS70S_EFG_GTP` | `Elongation_B` | 30.0 | binding | `re0000000301` | — |
| `re0000000301` | `RS70S_EFG_GTP` → `EFG_GTP` + `RS70S` | `Elongation_B` | 25.0 | release | `re0000000300` | — |
| `re0000000302` | `RS50S_EFG_GTP` → `RS50S_EFG_GDP_PO4` | `Elongation_B` | 31.0 | transition | `re0000000303` | — |
| `re0000000303` | `RS50S_EFG_GDP_PO4` → `RS50S_EFG_GTP` | `Elongation_B` | 5.0 | transition | `re0000000302` | — |
| `re0000000304` | `RS70S_EFG_GTP` → `RS70S_EFG_GDP_PO4` | `Elongation_B` | 31.0 | transition | `re0000000305` | — |
| `re0000000305` | `RS70S_EFG_GDP_PO4` → `RS70S_EFG_GTP` | `Elongation_B` | 5.0 | transition | `re0000000304` | — |
| `re0000000306` | `RS50S_EFG_GDP_PO4` → `PO4` + `RS50S_EFG_GDP` | `Elongation_B` | 5.0 | release | `re0000000325` | — |
| `re0000000307` | `RS70S_EFG_GDP_PO4` → `PO4` + `RS70S_EFG_GDP` | `Elongation_B` | 5.0 | release | `re0000000326` | CHAIN_09 |
| `re0000000309` | `RS70S_EFG_GDP` → `EFG_GDP` + `RS70S` | `Elongation_B` | 1000.0 | release | `re0000000328` | CHAIN_09 |
| `re0000000325` | `PO4` + `RS50S_EFG_GDP` → `RS50S_EFG_GDP_PO4` | `Elongation_B` | 0 | binding | `re0000000306` | — |
| `re0000000326` | `PO4` + `RS70S_EFG_GDP` → `RS70S_EFG_GDP_PO4` | `Elongation_B` | 0 | binding | `re0000000307` | — |
| `re0000000328` | `EFG_GDP` + `RS70S` → `RS70S_EFG_GDP` | `Elongation_B` | 0 | binding | `re0000000309` | — |

</details>

<details>
<summary><strong>ELONG_peptide_formation</strong> — 4 reactions; author k&gt;0: 2</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000018` | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` → `elRS70SBGGU0002_Pept0002tRNAGlyGCC` | `Elongation_Ca2_pept0002` | 1000.0 | transition | `re0000000062` | CHAIN_01 |
| `re0000000062` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC` → `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | `Elongation_Ca2_pept0002` | 0 | transition | `re0000000018` | — |
| `re0000000079` | `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` → `elRS70SBGGU0003_Pept0003tRNAGlyGCC` | `Elongation_Ca2_pept0003` | 1000.0 | transition | `re0000000120` | CHAIN_02 |
| `re0000000120` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC` → `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` | `Elongation_Ca2_pept0003` | 0 | transition | `re0000000079` | — |

</details>

<details>
<summary><strong>ELONG_tRNA_release</strong> — 4 reactions; author k&gt;0: 2</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000001` | `elRS70SAGGU0002_fMettRNAfMetCAU` → `elRS70SAGGU0002_fMet` + `tRNAfMetCAU` | `Elongation_Ca1_fMetCAU` | 1000.0 | release | `re0000000002` | — |
| `re0000000002` | `elRS70SAGGU0002_fMet` + `tRNAfMetCAU` → `elRS70SAGGU0002_fMettRNAfMetCAU` | `Elongation_Ca1_fMetCAU` | 0 | binding | `re0000000001` | — |
| `re0000000068` | `elRS70SAGGU0003_Pept0002tRNAGlyGCC` → `elRS70SAGGU0003_Pept0002` + `tRNAGlyGCC` | `Elongation_Ca1_GlyGCC` | 1000.0 | release | `re0000000069` | CHAIN_03 |
| `re0000000069` | `elRS70SAGGU0003_Pept0002` + `tRNAGlyGCC` → `elRS70SAGGU0003_Pept0002tRNAGlyGCC` | `Elongation_Ca1_GlyGCC` | 0 | binding | `re0000000068` | — |

</details>

<details>
<summary><strong>ELONG_translocation</strong> — 8 reactions; author k&gt;0: 4</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000024` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4` → `PO4` + `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP` | `Elongation_Ca2_pept0002` | 5.0 | release | `re0000000066` | CHAIN_03 |
| `re0000000025` | `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP` → `EFG_GDP` + `elRS70SAGGU0003_Pept0002tRNAGlyGCC` | `Elongation_Ca2_pept0002` | 1000.0 | release | `re0000000067` | CHAIN_03 |
| `re0000000066` | `PO4` + `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP` → `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4` | `Elongation_Ca2_pept0002` | 0 | binding | `re0000000024` | — |
| `re0000000067` | `EFG_GDP` + `elRS70SAGGU0003_Pept0002tRNAGlyGCC` → `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP` | `Elongation_Ca2_pept0002` | 0 | binding | `re0000000025` | — |
| `re0000000085` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4` → `PO4` + `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP` | `Elongation_Ca2_pept0003` | 5.0 | release | `re0000000124` | CHAIN_05 |
| `re0000000086` | `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP` → `EFG_GDP` + `elRS70SAUAA0004_Pept0003tRNAGlyGCC` | `Elongation_Ca2_pept0003` | 1000.0 | release | `re0000000125` | CHAIN_05 |
| `re0000000124` | `PO4` + `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP` → `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4` | `Elongation_Ca2_pept0003` | 0 | binding | `re0000000085` | — |
| `re0000000125` | `EFG_GDP` + `elRS70SAUAA0004_Pept0003tRNAGlyGCC` → `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP` | `Elongation_Ca2_pept0003` | 0 | binding | `re0000000086` | — |

</details>

### Aminoacylation / formylation — 122 source directions

<details>
<summary><strong>RS_activation</strong> — 24 reactions; author k&gt;0: 14</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000127` | `GlyRS_GlyAMP_PPi` → `GlyRS_GlyAMP` + `PPi` | `Aminoacylation_A_Gly` | 1000.0 | release | `re0000000150` | — |
| `re0000000140` | `GlyRS_Gly_ATP` → `GlyRS_GlyAMP_PPi` | `Aminoacylation_A_Gly` | 29.0 | transition | `re0000000141` | — |
| `re0000000141` | `GlyRS_GlyAMP_PPi` → `GlyRS_Gly_ATP` | `Aminoacylation_A_Gly` | 47.0 | transition | `re0000000140` | — |
| `re0000000143` | `GlyAMP` → `AMP` + `Gly` | `Aminoacylation_A_Gly` | 0 | release | `re0000000149` | — |
| `re0000000147` | `GlyRS_GlyAMP` → `GlyAMP` + `GlyRS` | `Aminoacylation_A_Gly` | 0.07 | release | `re0000000148` | PAIR_06 |
| `re0000000148` | `GlyAMP` + `GlyRS` → `GlyRS_GlyAMP` | `Aminoacylation_A_Gly` | 2.4 | binding | `re0000000147` | PAIR_06 |
| `re0000000149` | `AMP` + `Gly` → `GlyAMP` | `Aminoacylation_A_Gly` | 0 | binding | `re0000000143` | — |
| `re0000000150` | `GlyRS_GlyAMP` + `PPi` → `GlyRS_GlyAMP_PPi` | `Aminoacylation_A_Gly` | 0 | binding | `re0000000127` | — |
| `re0000000152` | `MetRS_MetAMP_PPi` → `MetRS_MetAMP` + `PPi` | `Aminoacylation_A_Met` | 1000.0 | release | `re0000000175` | — |
| `re0000000165` | `MetRS_Met_ATP` → `MetRS_MetAMP_PPi` | `Aminoacylation_A_Met` | 60.0 | transition | `re0000000166` | — |
| `re0000000166` | `MetRS_MetAMP_PPi` → `MetRS_Met_ATP` | `Aminoacylation_A_Met` | 150.0 | transition | `re0000000165` | — |
| `re0000000168` | `MetAMP` → `AMP` + `Met` | `Aminoacylation_A_Met` | 0 | release | `re0000000174` | — |
| `re0000000172` | `MetRS_MetAMP` → `MetAMP` + `MetRS` | `Aminoacylation_A_Met` | 0.07 | release | `re0000000173` | PAIR_07 |
| `re0000000173` | `MetAMP` + `MetRS` → `MetRS_MetAMP` | `Aminoacylation_A_Met` | 2.4 | binding | `re0000000172` | PAIR_07 |
| `re0000000174` | `AMP` + `Met` → `MetAMP` | `Aminoacylation_A_Met` | 0 | binding | `re0000000168` | — |
| `re0000000175` | `MetRS_MetAMP` + `PPi` → `MetRS_MetAMP_PPi` | `Aminoacylation_A_Met` | 0 | binding | `re0000000152` | — |
| `re0000000189` | `GlyRS_GlyAMP_PPi_tRNAGlyGCC` → `GlyRS_GlyAMP_tRNAGlyGCC` + `PPi` | `Aminoacylation_B_GlyGCC` | 1000.0 | release | `re0000000217` | — |
| `re0000000197` | `GlyRS_Gly_ATP_tRNAGlyGCC` → `GlyRS_GlyAMP_PPi_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 2.0 | transition | `re0000000198` | — |
| `re0000000198` | `GlyRS_GlyAMP_PPi_tRNAGlyGCC` → `GlyRS_Gly_ATP_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | `re0000000197` | — |
| `re0000000217` | `GlyRS_GlyAMP_tRNAGlyGCC` + `PPi` → `GlyRS_GlyAMP_PPi_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | binding | `re0000000189` | — |
| `re0000000231` | `MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetRS_MetAMP_tRNAfMetCAU` + `PPi` | `Aminoacylation_B_fMetCAU` | 1000.0 | release | `re0000000260` | — |
| `re0000000239` | `MetRS_Met_ATP_tRNAfMetCAU` → `MetRS_MetAMP_PPi_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 200.0 | transition | `re0000000240` | — |
| `re0000000240` | `MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | `re0000000239` | — |
| `re0000000260` | `MetRS_MetAMP_tRNAfMetCAU` + `PPi` → `MetRS_MetAMP_PPi_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | binding | `re0000000231` | — |

</details>

<details>
<summary><strong>RS_binding</strong> — 48 reactions; author k&gt;0: 48</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000126` | `Gly` + `GlyRS` → `GlyRS_Gly` | `Aminoacylation_A_Gly` | 20.0 | binding | `re0000000131` | — |
| `re0000000131` | `GlyRS_Gly` → `Gly` + `GlyRS` | `Aminoacylation_A_Gly` | 470.0 | release | `re0000000126` | — |
| `re0000000132` | `ATP` + `GlyRS` → `GlyRS_ATP` | `Aminoacylation_A_Gly` | 10.0 | binding | `re0000000133` | — |
| `re0000000133` | `GlyRS_ATP` → `ATP` + `GlyRS` | `Aminoacylation_A_Gly` | 8900.0 | release | `re0000000132` | — |
| `re0000000134` | `Gly` + `GlyRS_ATP` → `GlyRS_Gly_ATP` | `Aminoacylation_A_Gly` | 0.024 | binding | `re0000000135` | — |
| `re0000000135` | `GlyRS_Gly_ATP` → `Gly` + `GlyRS_ATP` | `Aminoacylation_A_Gly` | 3.2 | release | `re0000000134` | — |
| `re0000000136` | `ATP` + `GlyRS_Gly` → `GlyRS_Gly_ATP` | `Aminoacylation_A_Gly` | 10.0 | binding | `re0000000137` | — |
| `re0000000137` | `GlyRS_Gly_ATP` → `ATP` + `GlyRS_Gly` | `Aminoacylation_A_Gly` | 4500.0 | release | `re0000000136` | — |
| `re0000000151` | `Met` + `MetRS` → `MetRS_Met` | `Aminoacylation_A_Met` | 5.0 | binding | `re0000000156` | — |
| `re0000000156` | `MetRS_Met` → `Met` + `MetRS` | `Aminoacylation_A_Met` | 350.0 | release | `re0000000151` | — |
| `re0000000157` | `ATP` + `MetRS` → `MetRS_ATP` | `Aminoacylation_A_Met` | 10.0 | binding | `re0000000158` | — |
| `re0000000158` | `MetRS_ATP` → `ATP` + `MetRS` | `Aminoacylation_A_Met` | 2500.0 | release | `re0000000157` | — |
| `re0000000159` | `Met` + `MetRS_ATP` → `MetRS_Met_ATP` | `Aminoacylation_A_Met` | 5.0 | binding | `re0000000160` | — |
| `re0000000160` | `MetRS_Met_ATP` → `Met` + `MetRS_ATP` | `Aminoacylation_A_Met` | 350.0 | release | `re0000000159` | — |
| `re0000000161` | `ATP` + `MetRS_Met` → `MetRS_Met_ATP` | `Aminoacylation_A_Met` | 10.0 | binding | `re0000000162` | — |
| `re0000000162` | `MetRS_Met_ATP` → `ATP` + `MetRS_Met` | `Aminoacylation_A_Met` | 2500.0 | release | `re0000000161` | — |
| `re0000000188` | `Gly` + `GlyRS_tRNAGlyGCC` → `GlyRS_Gly_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 20.0 | binding | `re0000000190` | — |
| `re0000000190` | `GlyRS_Gly_tRNAGlyGCC` → `Gly` + `GlyRS_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 470.0 | release | `re0000000188` | — |
| `re0000000191` | `ATP` + `GlyRS_tRNAGlyGCC` → `GlyRS_ATP_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 10.0 | binding | `re0000000192` | — |
| `re0000000192` | `GlyRS_ATP_tRNAGlyGCC` → `ATP` + `GlyRS_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 8900.0 | release | `re0000000191` | — |
| `re0000000193` | `Gly` + `GlyRS_ATP_tRNAGlyGCC` → `GlyRS_Gly_ATP_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0.024 | binding | `re0000000194` | — |
| `re0000000194` | `GlyRS_Gly_ATP_tRNAGlyGCC` → `Gly` + `GlyRS_ATP_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 3.2 | release | `re0000000193` | — |
| `re0000000195` | `ATP` + `GlyRS_Gly_tRNAGlyGCC` → `GlyRS_Gly_ATP_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 10.0 | binding | `re0000000196` | — |
| `re0000000196` | `GlyRS_Gly_ATP_tRNAGlyGCC` → `ATP` + `GlyRS_Gly_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 4500.0 | release | `re0000000195` | — |
| `re0000000199` | `GlyRS` + `tRNAGlyGCC` → `GlyRS_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 376.0 | binding | `re0000000201` | — |
| `re0000000200` | `GlyRS_Gly` + `tRNAGlyGCC` → `GlyRS_Gly_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 376.0 | binding | `re0000000202` | — |
| `re0000000201` | `GlyRS_tRNAGlyGCC` → `GlyRS` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 100.0 | release | `re0000000199` | — |
| `re0000000202` | `GlyRS_Gly_tRNAGlyGCC` → `GlyRS_Gly` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 100.0 | release | `re0000000200` | — |
| `re0000000203` | `GlyRS_ATP` + `tRNAGlyGCC` → `GlyRS_ATP_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 376.0 | binding | `re0000000204` | — |
| `re0000000204` | `GlyRS_ATP_tRNAGlyGCC` → `GlyRS_ATP` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 100.0 | release | `re0000000203` | — |
| `re0000000205` | `GlyRS_Gly_ATP` + `tRNAGlyGCC` → `GlyRS_Gly_ATP_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 376.0 | binding | `re0000000206` | — |
| `re0000000206` | `GlyRS_Gly_ATP_tRNAGlyGCC` → `GlyRS_Gly_ATP` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 100.0 | release | `re0000000205` | — |
| `re0000000230` | `Met` + `MetRS_tRNAfMetCAU` → `MetRS_Met_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 5.0 | binding | `re0000000232` | — |
| `re0000000232` | `MetRS_Met_tRNAfMetCAU` → `Met` + `MetRS_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 350.0 | release | `re0000000230` | — |
| `re0000000233` | `ATP` + `MetRS_tRNAfMetCAU` → `MetRS_ATP_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 10.0 | binding | `re0000000234` | — |
| `re0000000234` | `MetRS_ATP_tRNAfMetCAU` → `ATP` + `MetRS_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 2500.0 | release | `re0000000233` | — |
| `re0000000235` | `Met` + `MetRS_ATP_tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 5.0 | binding | `re0000000236` | — |
| `re0000000236` | `MetRS_Met_ATP_tRNAfMetCAU` → `Met` + `MetRS_ATP_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 350.0 | release | `re0000000235` | — |
| `re0000000237` | `ATP` + `MetRS_Met_tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 10.0 | binding | `re0000000238` | — |
| `re0000000238` | `MetRS_Met_ATP_tRNAfMetCAU` → `ATP` + `MetRS_Met_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 2500.0 | release | `re0000000237` | — |
| `re0000000241` | `MetRS` + `tRNAfMetCAU` → `MetRS_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 50.0 | binding | `re0000000243` | — |
| `re0000000242` | `MetRS_Met` + `tRNAfMetCAU` → `MetRS_Met_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 50.0 | binding | `re0000000244` | — |
| `re0000000243` | `MetRS_tRNAfMetCAU` → `MetRS` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 150.0 | release | `re0000000241` | — |
| `re0000000244` | `MetRS_Met_tRNAfMetCAU` → `MetRS_Met` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 150.0 | release | `re0000000242` | — |
| `re0000000245` | `MetRS_ATP` + `tRNAfMetCAU` → `MetRS_ATP_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 50.0 | binding | `re0000000246` | — |
| `re0000000246` | `MetRS_ATP_tRNAfMetCAU` → `MetRS_ATP` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 150.0 | release | `re0000000245` | — |
| `re0000000247` | `MetRS_Met_ATP` + `tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 50.0 | binding | `re0000000248` | — |
| `re0000000248` | `MetRS_Met_ATP_tRNAfMetCAU` → `MetRS_Met_ATP` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 150.0 | release | `re0000000247` | — |

</details>

<details>
<summary><strong>RS_charging</strong> — 28 reactions; author k&gt;0: 18</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000145` | `GlyRS_AMP` → `AMP` + `GlyRS` | `Aminoacylation_A_Gly` | 1000.0 | release | `re0000000146` | — |
| `re0000000146` | `AMP` + `GlyRS` → `GlyRS_AMP` | `Aminoacylation_A_Gly` | 0 | binding | `re0000000145` | — |
| `re0000000170` | `MetRS_AMP` → `AMP` + `MetRS` | `Aminoacylation_A_Met` | 1000.0 | release | `re0000000171` | — |
| `re0000000171` | `AMP` + `MetRS` → `MetRS_AMP` | `Aminoacylation_A_Met` | 0 | binding | `re0000000170` | — |
| `re0000000176` | `GlytRNAGlyGCC` → `Gly` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | release | `re0000000216` | — |
| `re0000000178` | `GlyRS_GlyAMP_tRNAGlyGCC` → `GlyRS_AMP_GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 22.0 | transition | `re0000000179` | — |
| `re0000000179` | `GlyRS_AMP_GlytRNAGlyGCC` → `GlyRS_GlyAMP_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | `re0000000178` | — |
| `re0000000180` | `GlyRS_AMP_GlytRNAGlyGCC` → `AMP` + `GlyRS_GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 1000.0 | release | `re0000000181` | — |
| `re0000000181` | `AMP` + `GlyRS_GlytRNAGlyGCC` → `GlyRS_AMP_GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | binding | `re0000000180` | — |
| `re0000000182` | `GlyRS_AMP_GlytRNAGlyGCC` → `GlyRS_AMP` + `GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 353.0 | release | `re0000000183` | — |
| `re0000000183` | `GlyRS_AMP` + `GlytRNAGlyGCC` → `GlyRS_AMP_GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 100.0 | binding | `re0000000182` | — |
| `re0000000184` | `GlyRS_GlytRNAGlyGCC` → `GlyRS` + `GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 353.0 | release | `re0000000185` | — |
| `re0000000185` | `GlyRS` + `GlytRNAGlyGCC` → `GlyRS_GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 100.0 | binding | `re0000000184` | — |
| `re0000000209` | `GlyRS_GlyAMP` + `tRNAGlyGCC` → `GlyRS_GlyAMP_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 353.0 | binding | `re0000000210` | — |
| `re0000000210` | `GlyRS_GlyAMP_tRNAGlyGCC` → `GlyRS_GlyAMP` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 100.0 | release | `re0000000209` | — |
| `re0000000216` | `Gly` + `tRNAGlyGCC` → `GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | binding | `re0000000176` | — |
| `re0000000218` | `MettRNAfMetCAU` → `Met` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | release | `re0000000259` | — |
| `re0000000220` | `MetRS_MetAMP_tRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 13.7 | transition | `re0000000221` | — |
| `re0000000221` | `MetRS_AMP_MettRNAfMetCAU` → `MetRS_MetAMP_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | `re0000000220` | — |
| `re0000000222` | `MetRS_AMP_MettRNAfMetCAU` → `AMP` + `MetRS_MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 1000.0 | release | `re0000000223` | — |
| `re0000000223` | `AMP` + `MetRS_MettRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | binding | `re0000000222` | — |
| `re0000000224` | `MetRS_AMP_MettRNAfMetCAU` → `MetRS_AMP` + `MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 1.685 | release | `re0000000225` | — |
| `re0000000225` | `MetRS_AMP` + `MettRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 5.6 | binding | `re0000000224` | — |
| `re0000000226` | `MetRS_MettRNAfMetCAU` → `MetRS` + `MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 1.685 | release | `re0000000227` | — |
| `re0000000227` | `MetRS` + `MettRNAfMetCAU` → `MetRS_MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 5.6 | binding | `re0000000226` | — |
| `re0000000251` | `MetRS_MetAMP` + `tRNAfMetCAU` → `MetRS_MetAMP_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 50.0 | binding | `re0000000252` | — |
| `re0000000252` | `MetRS_MetAMP_tRNAfMetCAU` → `MetRS_MetAMP` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 150.0 | release | `re0000000251` | — |
| `re0000000259` | `Met` + `tRNAfMetCAU` → `MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | binding | `re0000000218` | — |

</details>

<details>
<summary><strong>RS_to_INIT_formylation</strong> — 22 reactions; author k&gt;0: 13</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000417` | `fMettRNAfMetCAU` → `fMet` + `tRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | release | `re0000000443` | — |
| `re0000000418` | `FD` + `MTF` → `MTF_FD` | `FMet_tRNASynthesis` | 74.07407407 | binding | `re0000000419` | — |
| `re0000000419` | `MTF_FD` → `FD` + `MTF` | `FMet_tRNASynthesis` | 1000.0 | release | `re0000000418` | — |
| `re0000000420` | `MTF` + `MettRNAfMetCAU` → `MTF_MettRNAfMetCAU` | `FMet_tRNASynthesis` | 2000.0 | binding | `re0000000421` | — |
| `re0000000421` | `MTF_MettRNAfMetCAU` → `MTF` + `MettRNAfMetCAU` | `FMet_tRNASynthesis` | 1000.0 | release | `re0000000420` | — |
| `re0000000422` | `MTF_FD` + `MettRNAfMetCAU` → `MTF_FD_MettRNAfMetCAU` | `FMet_tRNASynthesis` | 2000.0 | binding | `re0000000423` | — |
| `re0000000423` | `MTF_FD_MettRNAfMetCAU` → `MTF_FD` + `MettRNAfMetCAU` | `FMet_tRNASynthesis` | 1000.0 | release | `re0000000422` | — |
| `re0000000424` | `FD` + `MTF_MettRNAfMetCAU` → `MTF_FD_MettRNAfMetCAU` | `FMet_tRNASynthesis` | 74.07407407 | binding | `re0000000425` | — |
| `re0000000425` | `MTF_FD_MettRNAfMetCAU` → `FD` + `MTF_MettRNAfMetCAU` | `FMet_tRNASynthesis` | 1000.0 | release | `re0000000424` | — |
| `re0000000426` | `MTF_FD_MettRNAfMetCAU` → `MTF_THF_fMettRNAfMetCAU` | `FMet_tRNASynthesis` | 37.3 | transition | `re0000000427` | — |
| `re0000000427` | `MTF_THF_fMettRNAfMetCAU` → `MTF_FD_MettRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | transition | `re0000000426` | — |
| `re0000000428` | `MTF_THF_fMettRNAfMetCAU` → `MTF_THF` + `fMettRNAfMetCAU` | `FMet_tRNASynthesis` | 1000.0 | release | `re0000000429` | CHAIN_10 |
| `re0000000429` | `MTF_THF` + `fMettRNAfMetCAU` → `MTF_THF_fMettRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | binding | `re0000000428` | — |
| `re0000000430` | `MTF_THF_fMettRNAfMetCAU` → `MTF_fMettRNAfMetCAU` + `THF` | `FMet_tRNASynthesis` | 1000.0 | release | `re0000000431` | CHAIN_11 |
| `re0000000431` | `MTF_fMettRNAfMetCAU` + `THF` → `MTF_THF_fMettRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | binding | `re0000000430` | — |
| `re0000000432` | `MTF_fMettRNAfMetCAU` → `MTF` + `fMettRNAfMetCAU` | `FMet_tRNASynthesis` | 1000.0 | release | `re0000000433` | CHAIN_11 |
| `re0000000433` | `MTF` + `fMettRNAfMetCAU` → `MTF_fMettRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | binding | `re0000000432` | — |
| `re0000000434` | `MTF_THF` → `MTF` + `THF` | `FMet_tRNASynthesis` | 1000.0 | release | `re0000000435` | CHAIN_10 |
| `re0000000435` | `MTF` + `THF` → `MTF_THF` | `FMet_tRNASynthesis` | 0 | binding | `re0000000434` | — |
| `re0000000442` | `FD` → `THF` | `FMet_tRNASynthesis` | 0 | transition | `re0000000444` | — |
| `re0000000443` | `fMet` + `tRNAfMetCAU` → `fMettRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | binding | `re0000000417` | — |
| `re0000000444` | `THF` → `FD` | `FMet_tRNASynthesis` | 0 | transition | `re0000000442` | — |

</details>

### Termination — 46 source directions

<details>
<summary><strong>TERM_energy_coupling</strong> — 34 reactions; author k&gt;0: 32</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000825` | `RF3_GDP` → `GDP` + `RF3` | `Termination_B_RF1` (+1 shared) | 0.032 | release | `re0000000826` | — |
| `re0000000826` | `GDP` + `RF3` → `RF3_GDP` | `Termination_B_RF1` (+1 shared) | 5.82 | binding | `re0000000825` | — |
| `re0000000827` | `GTP` + `RF3` → `RF3_GTP` | `Termination_B_RF1` (+1 shared) | 10.0 | binding | `re0000000828` | — |
| `re0000000828` | `RF3_GTP` → `GTP` + `RF3` | `Termination_B_RF1` (+1 shared) | 25.0 | release | `re0000000827` | — |
| `re0000000829` | `RF3_GDP` + `termRS70SUAA0004_tRNAGlyGCC_RF1` → `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP` | `Termination_B_RF1` | 30.0 | binding | `re0000000830` | — |
| `re0000000830` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP` → `RF3_GDP` + `termRS70SUAA0004_tRNAGlyGCC_RF1` | `Termination_B_RF1` | 25.0 | release | `re0000000829` | — |
| `re0000000831` | `RF3_GTP` + `termRS70SUAA0004_tRNAGlyGCC_RF1` → `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` | `Termination_B_RF1` | 30.0 | binding | `re0000000832` | — |
| `re0000000832` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` → `RF3_GTP` + `termRS70SUAA0004_tRNAGlyGCC_RF1` | `Termination_B_RF1` | 25.0 | release | `re0000000831` | — |
| `re0000000833` | `RF3` + `termRS70SUAA0004_tRNAGlyGCC_RF1` → `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` | `Termination_B_RF1` | 30.0 | binding | `re0000000834` | — |
| `re0000000834` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` → `RF3` + `termRS70SUAA0004_tRNAGlyGCC_RF1` | `Termination_B_RF1` | 25.0 | release | `re0000000833` | — |
| `re0000000838` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` → `RF1` + `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` | `Termination_B_RF1` | 0.3 | release | `re0000000839` | — |
| `re0000000839` | `RF1` + `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` → `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` | `Termination_B_RF1` | 60.0 | binding | `re0000000838` | — |
| `re0000000840` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` → `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4` | `Termination_B_RF1` (+1 shared) | 31.0 | transition | `re0000000841` | — |
| `re0000000841` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4` → `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` | `Termination_B_RF1` (+1 shared) | 5.0 | transition | `re0000000840` | — |
| `re0000000842` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4` → `PO4` + `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP` | `Termination_B_RF1` (+1 shared) | 5.0 | release | `re0000000868` | CHAIN_12 |
| `re0000000843` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP` → `GDP` + `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` | `Termination_B_RF1` | 10.5 | release | `re0000000844` | — |
| `re0000000844` | `GDP` + `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` → `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP` | `Termination_B_RF1` | 5.82 | binding | `re0000000843` | — |
| `re0000000845` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` → `GTP` + `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` | `Termination_B_RF1` | 10.0 | release | `re0000000846` | — |
| `re0000000846` | `GTP` + `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` → `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` | `Termination_B_RF1` | 25.0 | binding | `re0000000845` | — |
| `re0000000847` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP` → `RF3_GDP` + `termRS70SUAA0004_tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 1000.0 | release | `re0000000869` | CHAIN_12 |
| `re0000000868` | `PO4` + `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP` → `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4` | `Termination_B_RF1` (+1 shared) | 0 | binding | `re0000000842` | — |
| `re0000000869` | `RF3_GDP` + `termRS70SUAA0004_tRNAGlyGCC` → `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP` | `Termination_B_RF1` (+1 shared) | 0 | binding | `re0000000847` | — |
| `re0000000870` | `RF3_GDP` + `termRS70SUAA0004_tRNAGlyGCC_RF2` → `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP` | `Termination_B_RF2` | 30.0 | binding | `re0000000871` | — |
| `re0000000871` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP` → `RF3_GDP` + `termRS70SUAA0004_tRNAGlyGCC_RF2` | `Termination_B_RF2` | 25.0 | release | `re0000000870` | — |
| `re0000000872` | `RF3_GTP` + `termRS70SUAA0004_tRNAGlyGCC_RF2` → `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` | `Termination_B_RF2` | 30.0 | binding | `re0000000873` | — |
| `re0000000873` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` → `RF3_GTP` + `termRS70SUAA0004_tRNAGlyGCC_RF2` | `Termination_B_RF2` | 25.0 | release | `re0000000872` | — |
| `re0000000874` | `RF3` + `termRS70SUAA0004_tRNAGlyGCC_RF2` → `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` | `Termination_B_RF2` | 30.0 | binding | `re0000000875` | — |
| `re0000000875` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` → `RF3` + `termRS70SUAA0004_tRNAGlyGCC_RF2` | `Termination_B_RF2` | 25.0 | release | `re0000000874` | — |
| `re0000000879` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` → `RF2` + `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` | `Termination_B_RF2` | 0.77 | release | `re0000000880` | — |
| `re0000000880` | `RF2` + `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` → `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` | `Termination_B_RF2` | 23.0 | binding | `re0000000879` | — |
| `re0000000881` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP` → `GDP` + `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` | `Termination_B_RF2` | 10.5 | release | `re0000000882` | — |
| `re0000000882` | `GDP` + `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` → `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP` | `Termination_B_RF2` | 5.82 | binding | `re0000000881` | — |
| `re0000000883` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` → `GTP` + `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` | `Termination_B_RF2` | 10.0 | release | `re0000000884` | — |
| `re0000000884` | `GTP` + `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` → `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` | `Termination_B_RF2` | 25.0 | binding | `re0000000883` | — |

</details>

<details>
<summary><strong>TERM_factor_binding</strong> — 8 reactions; author k&gt;0: 8</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000796` | `RF1` + `elRS70SAUAA0004_Pept0003tRNAGlyGCC` → `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1` | `Termination_A_RF1` | 60.0 | binding | `re0000000797` | — |
| `re0000000797` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1` → `RF1` + `elRS70SAUAA0004_Pept0003tRNAGlyGCC` | `Termination_A_RF1` | 0.0028 | release | `re0000000796` | — |
| `re0000000799` | `termRS70SUAA0004_tRNAGlyGCC_RF1` → `RF1` + `termRS70SUAA0004_tRNAGlyGCC` | `Termination_A_RF1` | 0.0028 | release | `re0000000800` | — |
| `re0000000800` | `RF1` + `termRS70SUAA0004_tRNAGlyGCC` → `termRS70SUAA0004_tRNAGlyGCC_RF1` | `Termination_A_RF1` | 60.0 | binding | `re0000000799` | — |
| `re0000000811` | `RF2` + `elRS70SAUAA0004_Pept0003tRNAGlyGCC` → `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2` | `Termination_A_RF2` | 23.0 | binding | `re0000000812` | — |
| `re0000000812` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2` → `RF2` + `elRS70SAUAA0004_Pept0003tRNAGlyGCC` | `Termination_A_RF2` | 0.016 | release | `re0000000811` | — |
| `re0000000814` | `termRS70SUAA0004_tRNAGlyGCC_RF2` → `RF2` + `termRS70SUAA0004_tRNAGlyGCC` | `Termination_A_RF2` | 0.016 | release | `re0000000815` | — |
| `re0000000815` | `RF2` + `termRS70SUAA0004_tRNAGlyGCC` → `termRS70SUAA0004_tRNAGlyGCC_RF2` | `Termination_A_RF2` | 23.0 | binding | `re0000000814` | — |

</details>

<details>
<summary><strong>TERM_peptide_release</strong> — 4 reactions; author k&gt;0: 2</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000798` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1` → `Pept0003` + `termRS70SUAA0004_tRNAGlyGCC_RF1` | `Termination_A_RF1` | 0.5 | release | `re0000000810` | — |
| `re0000000810` | `Pept0003` + `termRS70SUAA0004_tRNAGlyGCC_RF1` → `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1` | `Termination_A_RF1` | 0 | binding | `re0000000798` | — |
| `re0000000813` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2` → `Pept0003` + `termRS70SUAA0004_tRNAGlyGCC_RF2` | `Termination_A_RF2` | 1.5 | release | `re0000000823` | — |
| `re0000000823` | `Pept0003` + `termRS70SUAA0004_tRNAGlyGCC_RF2` → `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2` | `Termination_A_RF2` | 0 | binding | `re0000000813` | — |

</details>

### Ribosome recycling — 38 source directions

<details>
<summary><strong>RECYCLE_component_release</strong> — 24 reactions; author k&gt;0: 12</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000911` | `termRS30S_mRNA` → `RS30S` + `mRNA` | `Termination_C` | 1000.0 | release | `re0000000912` | CHAIN_04 |
| `re0000000912` | `RS30S` + `mRNA` → `termRS30S_mRNA` | `Termination_C` | 0 | binding | `re0000000911` | — |
| `re0000000913` | `RS50S_tRNAGlyGCC_RRF_EFG_GDP` → `EFG_GDP` + `RS50S_tRNAGlyGCC_RRF` | `Termination_C` | 1000.0 | release | `re0000000959` | — |
| `re0000000914` | `RS50S_tRNAGlyGCC_RRF_EFG_GDP` → `RRF` + `RS50S_tRNAGlyGCC_EFG_GDP` | `Termination_C` | 1000.0 | release | `re0000000958` | — |
| `re0000000915` | `RS50S_tRNAGlyGCC_RRF_EFG_GDP` → `RS50S_RRF_EFG_GDP` + `tRNAGlyGCC` | `Termination_C` | 1000.0 | release | `re0000000960` | — |
| `re0000000916` | `RS50S_tRNAGlyGCC_RRF` → `RS50S_RRF` + `tRNAGlyGCC` | `Termination_C` | 1000.0 | release | `re0000000965` | — |
| `re0000000917` | `RS50S_tRNAGlyGCC_RRF` → `RRF` + `RS50S_tRNAGlyGCC` | `Termination_C` | 1000.0 | release | `re0000000962` | — |
| `re0000000918` | `RS50S_RRF` → `RRF` + `RS50S` | `Termination_C` | 1000.0 | release | `re0000000968` | — |
| `re0000000919` | `RS50S_tRNAGlyGCC` → `RS50S` + `tRNAGlyGCC` | `Termination_C` | 1000.0 | release | `re0000000967` | — |
| `re0000000920` | `RS50S_tRNAGlyGCC_EFG_GDP` → `EFG_GDP` + `RS50S_tRNAGlyGCC` | `Termination_C` | 1000.0 | release | `re0000000961` | — |
| `re0000000921` | `RS50S_tRNAGlyGCC_EFG_GDP` → `RS50S_EFG_GDP` + `tRNAGlyGCC` | `Termination_C` | 1000.0 | release | `re0000000963` | — |
| `re0000000922` | `RS50S_RRF_EFG_GDP` → `EFG_GDP` + `RS50S_RRF` | `Termination_C` | 1000.0 | release | `re0000000966` | — |
| `re0000000923` | `RS50S_RRF_EFG_GDP` → `RRF` + `RS50S_EFG_GDP` | `Termination_C` | 1000.0 | release | `re0000000964` | — |
| `re0000000958` | `RRF` + `RS50S_tRNAGlyGCC_EFG_GDP` → `RS50S_tRNAGlyGCC_RRF_EFG_GDP` | `Termination_C` | 0 | binding | `re0000000914` | — |
| `re0000000959` | `EFG_GDP` + `RS50S_tRNAGlyGCC_RRF` → `RS50S_tRNAGlyGCC_RRF_EFG_GDP` | `Termination_C` | 0 | binding | `re0000000913` | — |
| `re0000000960` | `RS50S_RRF_EFG_GDP` + `tRNAGlyGCC` → `RS50S_tRNAGlyGCC_RRF_EFG_GDP` | `Termination_C` | 0 | binding | `re0000000915` | — |
| `re0000000961` | `EFG_GDP` + `RS50S_tRNAGlyGCC` → `RS50S_tRNAGlyGCC_EFG_GDP` | `Termination_C` | 0 | binding | `re0000000920` | — |
| `re0000000962` | `RRF` + `RS50S_tRNAGlyGCC` → `RS50S_tRNAGlyGCC_RRF` | `Termination_C` | 0 | binding | `re0000000917` | — |
| `re0000000963` | `RS50S_EFG_GDP` + `tRNAGlyGCC` → `RS50S_tRNAGlyGCC_EFG_GDP` | `Termination_C` | 0 | binding | `re0000000921` | — |
| `re0000000964` | `RRF` + `RS50S_EFG_GDP` → `RS50S_RRF_EFG_GDP` | `Termination_C` | 0 | binding | `re0000000923` | — |
| `re0000000965` | `RS50S_RRF` + `tRNAGlyGCC` → `RS50S_tRNAGlyGCC_RRF` | `Termination_C` | 0 | binding | `re0000000916` | — |
| `re0000000966` | `EFG_GDP` + `RS50S_RRF` → `RS50S_RRF_EFG_GDP` | `Termination_C` | 0 | binding | `re0000000922` | — |
| `re0000000967` | `RS50S` + `tRNAGlyGCC` → `RS50S_tRNAGlyGCC` | `Termination_C` | 0 | binding | `re0000000919` | — |
| `re0000000968` | `RRF` + `RS50S` → `RS50S_RRF` | `Termination_C` | 0 | binding | `re0000000918` | — |

</details>

<details>
<summary><strong>RECYCLE_disassembly</strong> — 14 reactions; author k&gt;0: 12</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000895` | `EFG_GTP` + `termRS70SUAA0004_tRNAGlyGCC_RRF` → `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` | `Termination_C` | 31.0 | binding | `re0000000896` | — |
| `re0000000896` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` → `EFG_GTP` + `termRS70SUAA0004_tRNAGlyGCC_RRF` | `Termination_C` | 2.4 | release | `re0000000895` | — |
| `re0000000900` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` → `RRF` + `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP` | `Termination_C` | 0.6 | release | `re0000000901` | — |
| `re0000000901` | `RRF` + `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP` → `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` | `Termination_C` | 3.1 | binding | `re0000000900` | — |
| `re0000000902` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` → `PO4` + `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP` | `Termination_C` | 5.0 | release | `re0000000956` | CHAIN_04 |
| `re0000000904` | `RRF` + `termRS70SUAA0004_tRNAGlyGCC` → `termRS70SUAA0004_tRNAGlyGCC_RRF` | `Termination_C` | 3.1 | binding | `re0000000905` | — |
| `re0000000905` | `termRS70SUAA0004_tRNAGlyGCC_RRF` → `RRF` + `termRS70SUAA0004_tRNAGlyGCC` | `Termination_C` | 0.6 | release | `re0000000904` | — |
| `re0000000906` | `EFG_GTP` + `termRS70SUAA0004_tRNAGlyGCC` → `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP` | `Termination_C` | 31.0 | binding | `re0000000907` | — |
| `re0000000907` | `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP` → `EFG_GTP` + `termRS70SUAA0004_tRNAGlyGCC` | `Termination_C` | 2.4 | release | `re0000000906` | — |
| `re0000000908` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` → `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` | `Termination_C` | 31.0 | transition | `re0000000909` | — |
| `re0000000909` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` → `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` | `Termination_C` | 5.0 | transition | `re0000000908` | — |
| `re0000000910` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP` → `RS50S_tRNAGlyGCC_RRF_EFG_GDP` + `termRS30S_mRNA` | `Termination_C` | 1000.0 | release | `re0000000957` | CHAIN_04 |
| `re0000000956` | `PO4` + `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP` → `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` | `Termination_C` | 0 | binding | `re0000000902` | — |
| `re0000000957` | `RS50S_tRNAGlyGCC_RRF_EFG_GDP` + `termRS30S_mRNA` → `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP` | `Termination_C` | 0 | binding | `re0000000910` | — |

</details>

### Energy regeneration — 74 source directions

<details>
<summary><strong>EN_binding</strong> — 54 reactions; author k&gt;0: 54</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000330` | `ADP` + `CK` → `CK_ADP` | `EnergyRegeneration_A` | 19.60784314 | binding | `re0000000331` | — |
| `re0000000331` | `CK_ADP` → `ADP` + `CK` | `EnergyRegeneration_A` | 1000.0 | release | `re0000000330` | — |
| `re0000000332` | `CK` + `CP` → `CK_CP` | `EnergyRegeneration_A` | 2.0 | binding | `re0000000333` | — |
| `re0000000333` | `CK_CP` → `CK` + `CP` | `EnergyRegeneration_A` | 1000.0 | release | `re0000000332` | — |
| `re0000000334` | `ADP` + `CK_CP` → `CK_CP_ADP` | `EnergyRegeneration_A` | 19.60784314 | binding | `re0000000335` | — |
| `re0000000335` | `CK_CP_ADP` → `ADP` + `CK_CP` | `EnergyRegeneration_A` | 1000.0 | release | `re0000000334` | — |
| `re0000000336` | `CK_ADP` + `CP` → `CK_CP_ADP` | `EnergyRegeneration_A` | 2.0 | binding | `re0000000337` | — |
| `re0000000337` | `CK_CP_ADP` → `CK_ADP` + `CP` | `EnergyRegeneration_A` | 1000.0 | release | `re0000000336` | — |
| `re0000000340` | `CK_Cr_ATP` → `ATP` + `CK_Cr` | `EnergyRegeneration_A` | 1000.0 | release | `re0000000341` | — |
| `re0000000341` | `ATP` + `CK_Cr` → `CK_Cr_ATP` | `EnergyRegeneration_A` | 1.369863014 | binding | `re0000000340` | — |
| `re0000000342` | `CK_Cr_ATP` → `CK_ATP` + `Cr` | `EnergyRegeneration_A` | 1000.0 | release | `re0000000343` | — |
| `re0000000343` | `CK_ATP` + `Cr` → `CK_Cr_ATP` | `EnergyRegeneration_A` | 0.204081633 | binding | `re0000000342` | — |
| `re0000000344` | `CK_ATP` → `ATP` + `CK` | `EnergyRegeneration_A` | 1000.0 | release | `re0000000345` | — |
| `re0000000345` | `ATP` + `CK` → `CK_ATP` | `EnergyRegeneration_A` | 1.369863014 | binding | `re0000000344` | — |
| `re0000000346` | `CK_Cr` → `CK` + `Cr` | `EnergyRegeneration_A` | 1000.0 | release | `re0000000347` | — |
| `re0000000347` | `CK` + `Cr` → `CK_Cr` | `EnergyRegeneration_A` | 0.204081633 | binding | `re0000000346` | — |
| `re0000000355` | `ATP` + `NDK` → `NDK_ATP` | `EnergyRegeneration_B` | 0.555555556 | binding | `re0000000356` | — |
| `re0000000356` | `NDK_ATP` → `ATP` + `NDK` | `EnergyRegeneration_B` | 1000.0 | release | `re0000000355` | — |
| `re0000000357` | `GDP` + `NDK` → `NDK_GDP` | `EnergyRegeneration_B` | 20.40816327 | binding | `re0000000358` | — |
| `re0000000358` | `NDK_GDP` → `GDP` + `NDK` | `EnergyRegeneration_B` | 1000.0 | release | `re0000000357` | — |
| `re0000000359` | `ATP` + `NDK_GDP` → `NDK_GDP_ATP` | `EnergyRegeneration_B` | 0.555555556 | binding | `re0000000360` | — |
| `re0000000360` | `NDK_GDP_ATP` → `ATP` + `NDK_GDP` | `EnergyRegeneration_B` | 1000.0 | release | `re0000000359` | — |
| `re0000000361` | `GDP` + `NDK_ATP` → `NDK_GDP_ATP` | `EnergyRegeneration_B` | 20.40816327 | binding | `re0000000362` | — |
| `re0000000362` | `NDK_GDP_ATP` → `GDP` + `NDK_ATP` | `EnergyRegeneration_B` | 1000.0 | release | `re0000000361` | — |
| `re0000000365` | `NDK_GTP_ADP` → `GTP` + `NDK_ADP` | `EnergyRegeneration_B` | 1000.0 | release | `re0000000376` | — |
| `re0000000366` | `NDK_GTP_ADP` → `ADP` + `NDK_GTP` | `EnergyRegeneration_B` | 1000.0 | release | `re0000000375` | — |
| `re0000000367` | `NDK_ADP` → `ADP` + `NDK` | `EnergyRegeneration_B` | 1000.0 | release | `re0000000378` | — |
| `re0000000368` | `NDK_GTP` → `GTP` + `NDK` | `EnergyRegeneration_B` | 1000.0 | release | `re0000000377` | — |
| `re0000000375` | `ADP` + `NDK_GTP` → `NDK_GTP_ADP` | `EnergyRegeneration_B` | 15.15151515 | binding | `re0000000366` | — |
| `re0000000376` | `GTP` + `NDK_ADP` → `NDK_GTP_ADP` | `EnergyRegeneration_B` | 6.666666667 | binding | `re0000000365` | — |
| `re0000000377` | `GTP` + `NDK` → `NDK_GTP` | `EnergyRegeneration_B` | 6.666666667 | binding | `re0000000368` | — |
| `re0000000378` | `ADP` + `NDK` → `NDK_ADP` | `EnergyRegeneration_B` | 15.15151515 | binding | `re0000000367` | — |
| `re0000000380` | `ATP` + `MK` → `MK_ATP` | `EnergyRegeneration_C` | 16.66666667 | binding | `re0000000381` | — |
| `re0000000381` | `MK_ATP` → `ATP` + `MK` | `EnergyRegeneration_C` | 1000.0 | release | `re0000000380` | — |
| `re0000000382` | `AMP` + `MK` → `MK_AMP` | `EnergyRegeneration_C` | 8.333333333 | binding | `re0000000383` | — |
| `re0000000383` | `MK_AMP` → `AMP` + `MK` | `EnergyRegeneration_C` | 1000.0 | release | `re0000000382` | — |
| `re0000000384` | `ATP` + `MK_AMP` → `MK_ATP_AMP` | `EnergyRegeneration_C` | 16.66666667 | binding | `re0000000385` | — |
| `re0000000385` | `MK_ATP_AMP` → `ATP` + `MK_AMP` | `EnergyRegeneration_C` | 1000.0 | release | `re0000000384` | — |
| `re0000000386` | `AMP` + `MK_ATP` → `MK_ATP_AMP` | `EnergyRegeneration_C` | 8.333333333 | binding | `re0000000387` | — |
| `re0000000387` | `MK_ATP_AMP` → `AMP` + `MK_ATP` | `EnergyRegeneration_C` | 1000.0 | release | `re0000000386` | — |
| `re0000000390` | `MK_ADP_ADP` → `ADP` + `MK_ADP_1` | `EnergyRegeneration_C` | 1000.0 | release | `re0000000391` | — |
| `re0000000391` | `ADP` + `MK_ADP_1` → `MK_ADP_ADP` | `EnergyRegeneration_C` | 35.71428571 | binding | `re0000000390` | — |
| `re0000000392` | `MK_ADP_ADP` → `ADP` + `MK_ADP_2` | `EnergyRegeneration_C` | 1000.0 | release | `re0000000393` | — |
| `re0000000393` | `ADP` + `MK_ADP_2` → `MK_ADP_ADP` | `EnergyRegeneration_C` | 1.098901099 | binding | `re0000000392` | — |
| `re0000000394` | `MK_ADP_1` → `ADP` + `MK` | `EnergyRegeneration_C` | 1000.0 | release | `re0000000395` | — |
| `re0000000395` | `ADP` + `MK` → `MK_ADP_1` | `EnergyRegeneration_C` | 1.098901099 | binding | `re0000000394` | — |
| `re0000000396` | `MK_ADP_2` → `ADP` + `MK` | `EnergyRegeneration_C` | 1000.0 | release | `re0000000397` | — |
| `re0000000397` | `ADP` + `MK` → `MK_ADP_2` | `EnergyRegeneration_C` | 35.71428571 | binding | `re0000000396` | — |
| `re0000000405` | `PPi` + `PPiase` → `PPiase_PPi` | `EnergyRegeneration_D` | 46.0 | binding | `re0000000406` | — |
| `re0000000406` | `PPiase_PPi` → `PPi` + `PPiase` | `EnergyRegeneration_D` | 200.0 | release | `re0000000405` | — |
| `re0000000409` | `PPiase_PO4_PO4` → `PO4` + `PPiase_PO4` | `EnergyRegeneration_D` | 440.0 | release | `re0000000410` | — |
| `re0000000410` | `PO4` + `PPiase_PO4` → `PPiase_PO4_PO4` | `EnergyRegeneration_D` | 0.059 | binding | `re0000000409` | — |
| `re0000000411` | `PPiase_PO4` → `PO4` + `PPiase` | `EnergyRegeneration_D` | 400.0 | release | `re0000000412` | — |
| `re0000000412` | `PO4` + `PPiase` → `PPiase_PO4` | `EnergyRegeneration_D` | 0.26 | binding | `re0000000411` | — |

</details>

<details>
<summary><strong>EN_byproduct_processing</strong> — 2 reactions; author k&gt;0: 2</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000407` | `PPiase_PPi` → `PPiase_PO4_PO4` | `EnergyRegeneration_D` | 800.0 | transition | `re0000000408` | — |
| `re0000000408` | `PPiase_PO4_PO4` → `PPiase_PPi` | `EnergyRegeneration_D` | 140.0 | transition | `re0000000407` | — |

</details>

<details>
<summary><strong>EN_energy_transfer</strong> — 18 reactions; author k&gt;0: 5</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000338` | `CK_CP_ADP` → `CK_Cr_ATP` | `EnergyRegeneration_A` | 2.527408333 | transition | `re0000000339` | — |
| `re0000000339` | `CK_Cr_ATP` → `CK_CP_ADP` | `EnergyRegeneration_A` | 0.548808667 | transition | `re0000000338` | — |
| `re0000000363` | `NDK_GDP_ATP` → `NDK_GTP_ADP` | `EnergyRegeneration_B` | 470.0 | transition | `re0000000364` | — |
| `re0000000364` | `NDK_GTP_ADP` → `NDK_GDP_ATP` | `EnergyRegeneration_B` | 0 | transition | `re0000000363` | — |
| `re0000000388` | `MK_ATP_AMP` → `MK_ADP_ADP` | `EnergyRegeneration_C` | 255.6 | transition | `re0000000389` | — |
| `re0000000389` | `MK_ADP_ADP` → `MK_ATP_AMP` | `EnergyRegeneration_C` | 345.6 | transition | `re0000000388` | — |
| `re0000000784` | `ATP` → `ADP` + `PO4` | `SmallMolecules` | 0 | release | `re0000000790` | — |
| `re0000000785` | `ADP` → `AMP` + `PO4` | `SmallMolecules` | 0 | release | `re0000000791` | — |
| `re0000000786` | `ATP` → `AMP` + `PPi` | `SmallMolecules` | 0 | release | `re0000000792` | — |
| `re0000000787` | `GTP` → `GDP` + `PO4` | `SmallMolecules` | 0 | release | `re0000000793` | — |
| `re0000000788` | `GDP` → `GMP` + `PO4` | `SmallMolecules` | 0 | release | `re0000000794` | — |
| `re0000000789` | `GTP` → `GMP` + `PPi` | `SmallMolecules` | 0 | release | `re0000000795` | — |
| `re0000000790` | `ADP` + `PO4` → `ATP` | `SmallMolecules` | 0 | binding | `re0000000784` | — |
| `re0000000791` | `AMP` + `PO4` → `ADP` | `SmallMolecules` | 0 | binding | `re0000000785` | — |
| `re0000000792` | `AMP` + `PPi` → `ATP` | `SmallMolecules` | 0 | binding | `re0000000786` | — |
| `re0000000793` | `GDP` + `PO4` → `GTP` | `SmallMolecules` | 0 | binding | `re0000000787` | — |
| `re0000000794` | `GMP` + `PO4` → `GDP` | `SmallMolecules` | 0 | binding | `re0000000788` | — |
| `re0000000795` | `GMP` + `PPi` → `GTP` | `SmallMolecules` | 0 | binding | `re0000000789` | — |

</details>

### Shared multi-context — 6 source directions

<details>
<summary><strong>SHARED_MULTI_CONTEXT</strong> — 6 reactions; author k&gt;0: 5</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000207` | `GlyRS_GlyAMP_PPi` + `tRNAGlyGCC` → `GlyRS_GlyAMP_PPi_tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 353.0 | binding | `re0000000208` | — |
| `re0000000208` | `GlyRS_GlyAMP_PPi_tRNAGlyGCC` → `GlyRS_GlyAMP_PPi` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 100.0 | release | `re0000000207` | — |
| `re0000000249` | `MetRS_MetAMP_PPi` + `tRNAfMetCAU` → `MetRS_MetAMP_PPi_tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 50.0 | binding | `re0000000250` | — |
| `re0000000250` | `MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetRS_MetAMP_PPi` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 150.0 | release | `re0000000249` | — |
| `re0000000308` | `RS50S_EFG_GDP` → `EFG_GDP` + `RS50S` | `Elongation_B` (+1 shared) | 1000.0 | release | `re0000000327` | — |
| `re0000000327` | `EFG_GDP` + `RS50S` → `RS50S_EFG_GDP` | `Elongation_B` (+1 shared) | 0 | binding | `re0000000308` | — |

</details>

### Degradation sinks — 388 source directions

<details>
<summary><strong>DEG_sink</strong> — 388 reactions; author k&gt;0: 0</summary>

| Source reaction ID | Exact reactants → products | Src (abridged) | Author k | Mechanism | Rev | Motif candidate |
| --- | --- | --- | ---: | --- | --- | --- |
| `re0000000003` | `RS50S` → `RS50S_degraded` | `Elongation_B` (+11 shared) | 0 | transition | — | — |
| `re0000000004` | `RS30S` → `RS30S_degraded` | `Elongation_B` (+12 shared) | 0 | transition | — | — |
| `re0000000005` | `fMettRNAfMetCAU` → `fMettRNAfMetCAU_degraded` | `Elongation_Ca1_fMetCAU` (+1 shared) | 0 | transition | — | — |
| `re0000000006` | `tRNAfMetCAU` → `tRNAfMetCAU_degraded` | `Aminoacylation_B_fMetCAU` (+1 shared) | 0 | transition | — | — |
| `re0000000007` | `fMet` → `fMet_degraded` | `Elongation_Ca1_fMetCAU` (+1 shared) | 0 | transition | — | — |
| `re0000000008` | `mRNA` → `mRNA_degraded` | `Elongation_Ca1_GlyGCC` (+9 shared) | 0 | transition | — | — |
| `re0000000009` | `elRS70SAGGU0002_fMettRNAfMetCAU` → `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Elongation_Ca1_fMetCAU` (+1 shared) | 0 | transition | — | — |
| `re0000000010` | `elRS70SAGGU0002_fMettRNAfMetCAU` → `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Elongation_Ca1_fMetCAU` (+1 shared) | 0 | transition | — | — |
| `re0000000011` | `elRS70SAGGU0002_fMet` → `RS30S` + `RS50S_degraded` + `fMet` + `mRNA` | `Elongation_Ca1_fMetCAU` (+1 shared) | 0 | transition | — | — |
| `re0000000012` | `elRS70SAGGU0002_fMet` → `RS30S_degraded` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca1_fMetCAU` (+1 shared) | 0 | transition | — | — |
| `re0000000029` | `EFTu` → `EFTu_degraded` | `Elongation_A_Gly` (+3 shared) | 0 | transition | — | — |
| `re0000000030` | `EFG` → `EFG_degraded` | `Elongation_B` (+3 shared) | 0 | transition | — | — |
| `re0000000031` | `GlytRNAGlyGCC` → `GlytRNAGlyGCC_degraded` | `Aminoacylation_B_GlyGCC` (+3 shared) | 0 | transition | — | — |
| `re0000000032` | `Pept0002tRNAGlyGCC` → `Pept0002tRNAGlyGCC_degraded` | `Elongation_Ca1_GlyGCC` (+1 shared) | 0 | transition | — | — |
| `re0000000033` | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` → `EFTu` + `GTP` + `GlytRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000034` | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` → `EFTu` + `GTP` + `GlytRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000035` | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` → `EFTu_degraded` + `GTP` + `GlytRNAGlyGCC` + `RS30S` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000036` | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` → `EFTu` + `GDP` + `GlytRNAGlyGCC` + `PO4` + `RS30S` + `RS50S_degraded` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000037` | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` → `EFTu` + `GDP` + `GlytRNAGlyGCC` + `PO4` + `RS30S_degraded` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000038` | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` → `EFTu_degraded` + `GDP` + `GlytRNAGlyGCC` + `PO4` + `RS30S` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000039` | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` → `EFTu` + `GDP` + `GlytRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000040` | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` → `EFTu` + `GDP` + `GlytRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000041` | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` → `EFTu_degraded` + `GDP` + `GlytRNAGlyGCC` + `RS30S` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000042` | `elRS70SAGGU0002_fMet_EFTu_GDP` → `EFTu` + `GDP` + `RS30S` + `RS50S_degraded` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000043` | `elRS70SAGGU0002_fMet_EFTu_GDP` → `EFTu` + `GDP` + `RS30S_degraded` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000044` | `elRS70SAGGU0002_fMet_EFTu_GDP` → `EFTu_degraded` + `GDP` + `RS30S` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000045` | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` → `GlytRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000046` | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` → `GlytRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `fMet` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000047` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC` → `Pept0002tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000048` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC` → `Pept0002tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000049` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP` → `EFG` + `GTP` + `Pept0002tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000050` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP` → `EFG` + `GTP` + `Pept0002tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000051` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP` → `EFG_degraded` + `GTP` + `Pept0002tRNAGlyGCC` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000052` | `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP` → `EFG` + `GDP` + `Pept0002tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000053` | `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP` → `EFG` + `GDP` + `Pept0002tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000054` | `elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP` → `EFG_degraded` + `GDP` + `Pept0002tRNAGlyGCC` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000055` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `Pept0002tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000056` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `Pept0002tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000057` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4` → `EFG_degraded` + `GDP` + `PO4` + `Pept0002tRNAGlyGCC` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0002` | 0 | transition | — | — |
| `re0000000058` | `elRS70SAGGU0003_Pept0002tRNAGlyGCC` → `Pept0002tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca1_GlyGCC` (+1 shared) | 0 | transition | — | — |
| `re0000000059` | `elRS70SAGGU0003_Pept0002tRNAGlyGCC` → `Pept0002tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca1_GlyGCC` (+1 shared) | 0 | transition | — | — |
| `re0000000070` | `tRNAGlyGCC` → `tRNAGlyGCC_degraded` | `Aminoacylation_B_GlyGCC` (+6 shared) | 0 | transition | — | — |
| `re0000000071` | `Pept0002` → `Pept0002_degraded` | `Elongation_Ca1_GlyGCC` (+1 shared) | 0 | transition | — | — |
| `re0000000072` | `elRS70SAGGU0003_Pept0002` → `Pept0002` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca1_GlyGCC` (+1 shared) | 0 | transition | — | — |
| `re0000000073` | `elRS70SAGGU0003_Pept0002` → `Pept0002` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca1_GlyGCC` (+1 shared) | 0 | transition | — | — |
| `re0000000090` | `Pept0003tRNAGlyGCC` → `Pept0003tRNAGlyGCC_degraded` | `Elongation_Ca2_pept0003` (+2 shared) | 0 | transition | — | — |
| `re0000000091` | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` → `EFTu` + `GTP` + `GlytRNAGlyGCC` + `Pept0002` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000092` | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` → `EFTu` + `GTP` + `GlytRNAGlyGCC` + `Pept0002` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000093` | `elRS70SAGGU0003_Pept0002_EFTu_GTP_GlytRNAGlyGCC` → `EFTu_degraded` + `GTP` + `GlytRNAGlyGCC` + `Pept0002` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000094` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC` → `EFTu` + `GDP` + `GlytRNAGlyGCC` + `PO4` + `Pept0002` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000095` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC` → `EFTu` + `GDP` + `GlytRNAGlyGCC` + `PO4` + `Pept0002` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000096` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC` → `EFTu_degraded` + `GDP` + `GlytRNAGlyGCC` + `PO4` + `Pept0002` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000097` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` → `EFTu` + `GDP` + `GlytRNAGlyGCC` + `Pept0002` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000098` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` → `EFTu` + `GDP` + `GlytRNAGlyGCC` + `Pept0002` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000099` | `elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC` → `EFTu_degraded` + `GDP` + `GlytRNAGlyGCC` + `Pept0002` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000100` | `elRS70SAGGU0003_Pept0002_EFTu_GDP` → `EFTu` + `GDP` + `Pept0002` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000101` | `elRS70SAGGU0003_Pept0002_EFTu_GDP` → `EFTu` + `GDP` + `Pept0002` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000102` | `elRS70SAGGU0003_Pept0002_EFTu_GDP` → `EFTu_degraded` + `GDP` + `Pept0002` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000103` | `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` → `GlytRNAGlyGCC` + `Pept0002` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000104` | `elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC` → `GlytRNAGlyGCC` + `Pept0002` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000105` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC` → `Pept0003tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000106` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC` → `Pept0003tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000107` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP` → `EFG` + `GTP` + `Pept0003tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000108` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP` → `EFG` + `GTP` + `Pept0003tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000109` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP` → `EFG_degraded` + `GTP` + `Pept0003tRNAGlyGCC` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000110` | `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP` → `EFG` + `GDP` + `Pept0003tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000111` | `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP` → `EFG` + `GDP` + `Pept0003tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000112` | `elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP` → `EFG_degraded` + `GDP` + `Pept0003tRNAGlyGCC` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000113` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `Pept0003tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000114` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `Pept0003tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000115` | `elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4` → `EFG_degraded` + `GDP` + `PO4` + `Pept0003tRNAGlyGCC` + `RS30S` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` | 0 | transition | — | — |
| `re0000000116` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC` → `Pept0003tRNAGlyGCC` + `RS30S` + `RS50S_degraded` + `mRNA` | `Elongation_Ca2_pept0003` (+2 shared) | 0 | transition | — | — |
| `re0000000117` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC` → `Pept0003tRNAGlyGCC` + `RS30S_degraded` + `RS50S` + `mRNA` | `Elongation_Ca2_pept0003` (+2 shared) | 0 | transition | — | — |
| `re0000000128` | `GlyRS` → `GlyRS_degraded` | `Aminoacylation_A_Gly` | 0 | transition | — | — |
| `re0000000129` | `GlyRS_Gly_ATP` → `ATP` + `Gly` + `GlyRS_degraded` | `Aminoacylation_A_Gly` | 0 | transition | — | — |
| `re0000000130` | `GlyRS_GlyAMP` → `GlyAMP` + `GlyRS_degraded` | `Aminoacylation_A_Gly` | 0 | transition | — | — |
| `re0000000138` | `GlyRS_ATP` → `ATP` + `GlyRS_degraded` | `Aminoacylation_A_Gly` | 0 | transition | — | — |
| `re0000000139` | `GlyRS_Gly` → `Gly` + `GlyRS_degraded` | `Aminoacylation_A_Gly` | 0 | transition | — | — |
| `re0000000142` | `GlyRS_GlyAMP_PPi` → `GlyAMP` + `GlyRS_degraded` + `PPi` | `Aminoacylation_A_Gly` | 0 | transition | — | — |
| `re0000000144` | `GlyRS_AMP` → `AMP` + `GlyRS_degraded` | `Aminoacylation_A_Gly` | 0 | transition | — | — |
| `re0000000153` | `MetRS` → `MetRS_degraded` | `Aminoacylation_A_Met` | 0 | transition | — | — |
| `re0000000154` | `MetRS_Met_ATP` → `ATP` + `Met` + `MetRS_degraded` | `Aminoacylation_A_Met` | 0 | transition | — | — |
| `re0000000155` | `MetRS_MetAMP` → `MetAMP` + `MetRS_degraded` | `Aminoacylation_A_Met` | 0 | transition | — | — |
| `re0000000163` | `MetRS_ATP` → `ATP` + `MetRS_degraded` | `Aminoacylation_A_Met` | 0 | transition | — | — |
| `re0000000164` | `MetRS_Met` → `Met` + `MetRS_degraded` | `Aminoacylation_A_Met` | 0 | transition | — | — |
| `re0000000167` | `MetRS_MetAMP_PPi` → `MetAMP` + `MetRS_degraded` + `PPi` | `Aminoacylation_A_Met` | 0 | transition | — | — |
| `re0000000169` | `MetRS_AMP` → `AMP` + `MetRS_degraded` | `Aminoacylation_A_Met` | 0 | transition | — | — |
| `re0000000177` | `GlyRS_GlyAMP_tRNAGlyGCC` → `GlyAMP` + `GlyRS_degraded` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | — | — |
| `re0000000186` | `GlyRS_AMP_GlytRNAGlyGCC` → `AMP` + `GlyRS_degraded` + `GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | — | — |
| `re0000000187` | `GlyRS_GlytRNAGlyGCC` → `GlyRS_degraded` + `GlytRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | — | — |
| `re0000000211` | `GlyRS_tRNAGlyGCC` → `GlyRS_degraded` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | — | — |
| `re0000000212` | `GlyRS_ATP_tRNAGlyGCC` → `ATP` + `GlyRS_degraded` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | — | — |
| `re0000000213` | `GlyRS_Gly_tRNAGlyGCC` → `Gly` + `GlyRS_degraded` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | — | — |
| `re0000000214` | `GlyRS_Gly_ATP_tRNAGlyGCC` → `ATP` + `Gly` + `GlyRS_degraded` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | — | — |
| `re0000000215` | `GlyRS_GlyAMP_PPi_tRNAGlyGCC` → `GlyAMP` + `GlyRS_degraded` + `PPi` + `tRNAGlyGCC` | `Aminoacylation_B_GlyGCC` | 0 | transition | — | — |
| `re0000000219` | `MetRS_MetAMP_tRNAfMetCAU` → `MetAMP` + `MetRS_degraded` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | — | — |
| `re0000000228` | `MetRS_AMP_MettRNAfMetCAU` → `AMP` + `MetRS_degraded` + `MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | — | — |
| `re0000000229` | `MetRS_MettRNAfMetCAU` → `MetRS_degraded` + `MettRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | — | — |
| `re0000000253` | `MetRS_tRNAfMetCAU` → `MetRS_degraded` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | — | — |
| `re0000000254` | `MetRS_ATP_tRNAfMetCAU` → `ATP` + `MetRS_degraded` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | — | — |
| `re0000000255` | `MetRS_Met_tRNAfMetCAU` → `Met` + `MetRS_degraded` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | — | — |
| `re0000000256` | `MetRS_Met_ATP_tRNAfMetCAU` → `ATP` + `Met` + `MetRS_degraded` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | — | — |
| `re0000000257` | `MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetAMP` + `MetRS_degraded` + `PPi` + `tRNAfMetCAU` | `Aminoacylation_B_fMetCAU` | 0 | transition | — | — |
| `re0000000258` | `MettRNAfMetCAU` → `MettRNAfMetCAU_degraded` | `Aminoacylation_B_fMetCAU` (+1 shared) | 0 | transition | — | — |
| `re0000000277` | `EFTs` → `EFTs_degraded` | `Elongation_A_Gly` (+1 shared) | 0 | transition | — | — |
| `re0000000278` | `EFTu_GTP` → `EFTu_degraded` + `GTP` | `Elongation_A_Gly` (+1 shared) | 0 | transition | — | — |
| `re0000000279` | `EFTu_GDP` → `EFTu_degraded` + `GDP` | `Elongation_A_Gly` (+1 shared) | 0 | transition | — | — |
| `re0000000280` | `EFTu_EFTs` → `EFTs` + `EFTu_degraded` | `Elongation_A_Gly` (+1 shared) | 0 | transition | — | — |
| `re0000000281` | `EFTu_EFTs` → `EFTs_degraded` + `EFTu` | `Elongation_A_Gly` (+1 shared) | 0 | transition | — | — |
| `re0000000282` | `EFTu_GDP_EFTs` → `EFTs` + `EFTu_degraded` + `GDP` | `Elongation_A_Gly` (+1 shared) | 0 | transition | — | — |
| `re0000000283` | `EFTu_GDP_EFTs` → `EFTs_degraded` + `EFTu` + `GDP` | `Elongation_A_Gly` (+1 shared) | 0 | transition | — | — |
| `re0000000284` | `EFTu_GTP_EFTs` → `EFTs` + `EFTu_degraded` + `GTP` | `Elongation_A_Gly` (+1 shared) | 0 | transition | — | — |
| `re0000000285` | `EFTu_GTP_EFTs` → `EFTs_degraded` + `EFTu` + `GTP` | `Elongation_A_Gly` (+1 shared) | 0 | transition | — | — |
| `re0000000286` | `EFTu_GTP_GlytRNAGlyGCC` → `EFTu_degraded` + `GTP` + `GlytRNAGlyGCC` | `Elongation_A_Gly` | 0 | transition | — | — |
| `re0000000287` | `EFTu_GTP_GlytRNAGlyGCC` → `EFTu` + `GTP` + `GlytRNAGlyGCC_degraded` | `Elongation_A_Gly` | 0 | transition | — | — |
| `re0000000290` | `EFTu_GTP_MettRNAfMetCAU` → `EFTu_degraded` + `GTP` + `MettRNAfMetCAU` | `Elongation_A_Met` | 0 | transition | — | — |
| `re0000000291` | `EFTu_GTP_MettRNAfMetCAU` → `EFTu` + `GTP` + `MettRNAfMetCAU_degraded` | `Elongation_A_Met` | 0 | transition | — | — |
| `re0000000296` | `EFG_GTP` → `EFG_degraded` + `GTP` | `Elongation_B` (+1 shared) | 0 | transition | — | — |
| `re0000000297` | `EFG_GDP` → `EFG_degraded` + `GDP` | `Elongation_B` (+1 shared) | 0 | transition | — | — |
| `re0000000310` | `RS50S_EFG_GTP` → `EFG_degraded` + `GTP` + `RS50S` | `Elongation_B` | 0 | transition | — | — |
| `re0000000311` | `RS50S_EFG_GTP` → `EFG` + `GTP` + `RS50S_degraded` | `Elongation_B` | 0 | transition | — | — |
| `re0000000312` | `RS50S_EFG_GDP_PO4` → `EFG_degraded` + `GDP` + `PO4` + `RS50S` | `Elongation_B` | 0 | transition | — | — |
| `re0000000313` | `RS50S_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `RS50S_degraded` | `Elongation_B` | 0 | transition | — | — |
| `re0000000314` | `RS50S_EFG_GDP` → `EFG_degraded` + `GDP` + `RS50S` | `Elongation_B` (+1 shared) | 0 | transition | — | — |
| `re0000000315` | `RS50S_EFG_GDP` → `EFG` + `GDP` + `RS50S_degraded` | `Elongation_B` (+1 shared) | 0 | transition | — | — |
| `re0000000316` | `RS70S_EFG_GTP` → `EFG_degraded` + `GTP` + `RS30S` + `RS50S` | `Elongation_B` | 0 | transition | — | — |
| `re0000000317` | `RS70S_EFG_GTP` → `EFG` + `GTP` + `RS30S` + `RS50S_degraded` | `Elongation_B` | 0 | transition | — | — |
| `re0000000318` | `RS70S_EFG_GDP_PO4` → `EFG_degraded` + `GDP` + `PO4` + `RS30S` + `RS50S` | `Elongation_B` | 0 | transition | — | — |
| `re0000000319` | `RS70S_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `RS30S` + `RS50S_degraded` | `Elongation_B` | 0 | transition | — | — |
| `re0000000320` | `RS70S_EFG_GTP` → `EFG` + `GTP` + `RS30S_degraded` + `RS50S` | `Elongation_B` | 0 | transition | — | — |
| `re0000000321` | `RS70S_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `RS30S_degraded` + `RS50S` | `Elongation_B` | 0 | transition | — | — |
| `re0000000322` | `RS70S_EFG_GDP` → `EFG` + `GDP` + `RS30S` + `RS50S_degraded` | `Elongation_B` | 0 | transition | — | — |
| `re0000000323` | `RS70S_EFG_GDP` → `EFG_degraded` + `GDP` + `RS30S` + `RS50S` | `Elongation_B` | 0 | transition | — | — |
| `re0000000324` | `RS70S_EFG_GDP` → `EFG` + `GDP` + `RS30S_degraded` + `RS50S` | `Elongation_B` | 0 | transition | — | — |
| `re0000000329` | `CK` → `CK_degraded` | `EnergyRegeneration_A` | 0 | transition | — | — |
| `re0000000348` | `CK_CP` → `CK_degraded` + `CP` | `EnergyRegeneration_A` | 0 | transition | — | — |
| `re0000000349` | `CK_ADP` → `ADP` + `CK_degraded` | `EnergyRegeneration_A` | 0 | transition | — | — |
| `re0000000350` | `CK_CP_ADP` → `ADP` + `CK_degraded` + `CP` | `EnergyRegeneration_A` | 0 | transition | — | — |
| `re0000000351` | `CK_Cr_ATP` → `ATP` + `CK_degraded` + `Cr` | `EnergyRegeneration_A` | 0 | transition | — | — |
| `re0000000352` | `CK_ATP` → `ATP` + `CK_degraded` | `EnergyRegeneration_A` | 0 | transition | — | — |
| `re0000000353` | `CK_Cr` → `CK_degraded` + `Cr` | `EnergyRegeneration_A` | 0 | transition | — | — |
| `re0000000354` | `NDK` → `NDK_degraded` | `EnergyRegeneration_B` | 0 | transition | — | — |
| `re0000000369` | `NDK_GDP` → `GDP` + `NDK_degraded` | `EnergyRegeneration_B` | 0 | transition | — | — |
| `re0000000370` | `NDK_ATP` → `ATP` + `NDK_degraded` | `EnergyRegeneration_B` | 0 | transition | — | — |
| `re0000000371` | `NDK_GDP_ATP` → `ATP` + `GDP` + `NDK_degraded` | `EnergyRegeneration_B` | 0 | transition | — | — |
| `re0000000372` | `NDK_GTP_ADP` → `ADP` + `GTP` + `NDK_degraded` | `EnergyRegeneration_B` | 0 | transition | — | — |
| `re0000000373` | `NDK_ADP` → `ADP` + `NDK_degraded` | `EnergyRegeneration_B` | 0 | transition | — | — |
| `re0000000374` | `NDK_GTP` → `GTP` + `NDK_degraded` | `EnergyRegeneration_B` | 0 | transition | — | — |
| `re0000000379` | `MK` → `MK_degraded` | `EnergyRegeneration_C` | 0 | transition | — | — |
| `re0000000398` | `MK_AMP` → `AMP` + `MK_degraded` | `EnergyRegeneration_C` | 0 | transition | — | — |
| `re0000000399` | `MK_ATP` → `ATP` + `MK_degraded` | `EnergyRegeneration_C` | 0 | transition | — | — |
| `re0000000400` | `MK_ATP_AMP` → `ATP` + `MK_degraded` | `EnergyRegeneration_C` | 0 | transition | — | — |
| `re0000000401` | `MK_ADP_ADP` → `ADP` + `MK_degraded` | `EnergyRegeneration_C` | 0 | transition | — | — |
| `re0000000402` | `MK_ADP_1` → `ADP` + `MK_degraded` | `EnergyRegeneration_C` | 0 | transition | — | — |
| `re0000000403` | `MK_ADP_2` → `ADP` + `MK_degraded` | `EnergyRegeneration_C` | 0 | transition | — | — |
| `re0000000404` | `PPiase` → `PPiase_degraded` | `EnergyRegeneration_D` | 0 | transition | — | — |
| `re0000000413` | `PPiase_PPi` → `PPi` + `PPiase_degraded` | `EnergyRegeneration_D` | 0 | transition | — | — |
| `re0000000414` | `PPiase_PO4_PO4` → 2 `PO4` + `PPiase_degraded` | `EnergyRegeneration_D` | 0 | transition | — | — |
| `re0000000415` | `PPiase_PO4` → `PO4` + `PPiase_degraded` | `EnergyRegeneration_D` | 0 | transition | — | — |
| `re0000000416` | `MTF` → `MTF_degraded` | `FMet_tRNASynthesis` | 0 | transition | — | — |
| `re0000000436` | `MTF_FD` → `FD` + `MTF_degraded` | `FMet_tRNASynthesis` | 0 | transition | — | — |
| `re0000000437` | `MTF_MettRNAfMetCAU` → `MTF_degraded` + `MettRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | transition | — | — |
| `re0000000438` | `MTF_FD_MettRNAfMetCAU` → `FD` + `MTF_degraded` + `MettRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | transition | — | — |
| `re0000000439` | `MTF_THF_fMettRNAfMetCAU` → `MTF_degraded` + `THF` + `fMettRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | transition | — | — |
| `re0000000440` | `MTF_fMettRNAfMetCAU` → `MTF_degraded` + `fMettRNAfMetCAU` | `FMet_tRNASynthesis` | 0 | transition | — | — |
| `re0000000441` | `MTF_THF` → `MTF_degraded` + `THF` | `FMet_tRNASynthesis` | 0 | transition | — | — |
| `re0000000451` | `IF2` → `IF2_degraded` | `Initiation_A` (+2 shared) | 0 | transition | — | — |
| `re0000000452` | `IF2_GDP` → `GDP` + `IF2_degraded` | `Initiation_A` | 0 | transition | — | — |
| `re0000000453` | `IF2_GTP` → `GTP` + `IF2_degraded` | `Initiation_A` | 0 | transition | — | — |
| `re0000000454` | `IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF2_degraded` + `fMettRNAfMetCAU` | `Initiation_A` | 0 | transition | — | — |
| `re0000000541` | `IF1` → `IF1_degraded` | `Initiation_B1` (+2 shared) | 0 | transition | — | — |
| `re0000000542` | `IF3` → `IF3_degraded` | `Initiation_B1` (+2 shared) | 0 | transition | — | — |
| `re0000000543` | `RS70S` → `RS30S_degraded` + `RS50S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000544` | `RS70S` → `RS30S` + `RS50S_degraded` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000545` | `RS30S_IF1` → `IF1_degraded` + `RS30S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000546` | `RS30S_IF1` → `IF1` + `RS30S_degraded` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000547` | `RS30S_IF3` → `IF3_degraded` + `RS30S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000548` | `RS30S_IF3` → `IF3` + `RS30S_degraded` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000549` | `RS30S_IF3_mRNA` → `IF3_degraded` + `RS30S` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000550` | `RS30S_IF3_mRNA` → `IF3` + `RS30S_degraded` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000551` | `RS30S_IF3_fMettRNAfMetCAU_mRNA` → `IF3_degraded` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000552` | `RS30S_IF3_fMettRNAfMetCAU_mRNA` → `IF3` + `RS30S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000553` | `RS70S_IF3` → `IF3` + `RS30S_degraded` + `RS50S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000554` | `RS70S_IF3` → `IF3` + `RS30S` + `RS50S_degraded` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000555` | `RS70S_IF3` → `IF3_degraded` + `RS30S` + `RS50S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000556` | `RS70S_IF1` → `IF1` + `RS30S_degraded` + `RS50S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000557` | `RS70S_IF1` → `IF1` + `RS30S` + `RS50S_degraded` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000558` | `RS70S_IF1` → `IF1_degraded` + `RS30S` + `RS50S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000559` | `RS30S_IF1_IF3` → `IF1` + `IF3_degraded` + `RS30S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000560` | `RS30S_IF1_IF3` → `IF1` + `IF3` + `RS30S_degraded` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000561` | `RS30S_IF1_IF3` → `IF1_degraded` + `IF3` + `RS30S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000562` | `RS30S_IF3_IF2_GTP` → `GTP` + `IF2` + `IF3` + `RS30S_degraded` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000563` | `RS30S_IF3_IF2_GTP` → `GTP` + `IF2_degraded` + `IF3` + `RS30S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000564` | `RS30S_IF3_IF2_GTP` → `GTP` + `IF2` + `IF3_degraded` + `RS30S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000565` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF2` + `IF3` + `RS30S_degraded` + `fMettRNAfMetCAU` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000566` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF2_degraded` + `IF3` + `RS30S` + `fMettRNAfMetCAU` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000567` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF2` + `IF3_degraded` + `RS30S` + `fMettRNAfMetCAU` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000568` | `RS30S_IF1_IF3_mRNA` → `IF1` + `IF3_degraded` + `RS30S` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000569` | `RS30S_IF1_IF3_mRNA` → `IF1` + `IF3` + `RS30S_degraded` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000570` | `RS30S_IF1_IF3_mRNA` → `IF1_degraded` + `IF3` + `RS30S` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000571` | `RS30S_IF3_IF2_GTP_mRNA` → `GTP` + `IF2` + `IF3` + `RS30S_degraded` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000572` | `RS30S_IF3_IF2_GTP_mRNA` → `GTP` + `IF2` + `IF3_degraded` + `RS30S` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000573` | `RS30S_IF3_IF2_GTP_mRNA` → `GTP` + `IF2_degraded` + `IF3` + `RS30S` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000574` | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1` + `IF3_degraded` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000575` | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1` + `IF3` + `RS30S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000576` | `RS30S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1_degraded` + `IF3` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000577` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF2` + `IF3` + `RS30S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000578` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF2_degraded` + `IF3` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000579` | `RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF2` + `IF3_degraded` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000580` | `RS70S_IF1_IF3` → `IF1` + `IF3_degraded` + `RS30S` + `RS50S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000581` | `RS70S_IF1_IF3` → `IF1` + `IF3` + `RS30S` + `RS50S_degraded` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000582` | `RS70S_IF1_IF3` → `IF1_degraded` + `IF3` + `RS30S` + `RS50S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000583` | `RS70S_IF1_IF3` → `IF1` + `IF3` + `RS30S_degraded` + `RS50S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000584` | `RS30S_IF1_IF3_IF2_GTP` → `GTP` + `IF1` + `IF2` + `IF3_degraded` + `RS30S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000585` | `RS30S_IF1_IF3_IF2_GTP` → `GTP` + `IF1` + `IF2_degraded` + `IF3` + `RS30S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000586` | `RS30S_IF1_IF3_IF2_GTP` → `GTP` + `IF1_degraded` + `IF2` + `IF3` + `RS30S` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000587` | `RS30S_IF1_IF3_IF2_GTP` → `GTP` + `IF1` + `IF2` + `IF3` + `RS30S_degraded` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000588` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF1` + `IF2` + `IF3_degraded` + `RS30S` + `fMettRNAfMetCAU` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000589` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF1` + `IF2_degraded` + `IF3` + `RS30S` + `fMettRNAfMetCAU` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000590` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF1_degraded` + `IF2` + `IF3` + `RS30S` + `fMettRNAfMetCAU` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000591` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF1` + `IF2` + `IF3` + `RS30S_degraded` + `fMettRNAfMetCAU` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000592` | `RS30S_IF1_IF3_IF2_GTP_mRNA` → `GTP` + `IF1` + `IF2` + `IF3_degraded` + `RS30S` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000593` | `RS30S_IF1_IF3_IF2_GTP_mRNA` → `GTP` + `IF1` + `IF2` + `IF3` + `RS30S_degraded` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000594` | `RS30S_IF1_IF3_IF2_GTP_mRNA` → `GTP` + `IF1` + `IF2_degraded` + `IF3` + `RS30S` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000595` | `RS30S_IF1_IF3_IF2_GTP_mRNA` → `GTP` + `IF1_degraded` + `IF2` + `IF3` + `RS30S` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000596` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1` + `IF2` + `IF3_degraded` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000597` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1` + `IF2` + `IF3` + `RS30S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000598` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1` + `IF2_degraded` + `IF3` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000599` | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1_degraded` + `IF2` + `IF3` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000600` | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF2_degraded` + `IF3` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000601` | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF2` + `IF3` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000602` | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF2` + `IF3_degraded` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000603` | `RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF2` + `IF3` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000604` | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1` + `IF2` + `IF3` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000605` | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1` + `IF2_degraded` + `IF3` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000606` | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1` + `IF2` + `IF3` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000607` | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1_degraded` + `IF2` + `IF3` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000608` | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1` + `IF2` + `IF3_degraded` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B1` | 0 | transition | — | — |
| `re0000000689` | `RS30S_IF2_GTP` → `GTP` + `IF2` + `RS30S_degraded` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000690` | `RS30S_IF2_GTP` → `GTP` + `IF2_degraded` + `RS30S` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000691` | `RS30S_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF2` + `RS30S_degraded` + `fMettRNAfMetCAU` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000692` | `RS30S_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF2_degraded` + `RS30S` + `fMettRNAfMetCAU` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000693` | `RS30S_mRNA` → `RS30S_degraded` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000694` | `RS30S_fMettRNAfMetCAU_mRNA` → `RS30S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000695` | `RS30S_IF2_GTP_mRNA` → `GTP` + `IF2` + `RS30S_degraded` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000696` | `RS30S_IF2_GTP_mRNA` → `GTP` + `IF2_degraded` + `RS30S` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000697` | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF2` + `RS30S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000698` | `RS30S_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF2_degraded` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000699` | `RS30S_IF1_IF2_GTP` → `GTP` + `IF1` + `IF2` + `RS30S_degraded` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000700` | `RS30S_IF1_IF2_GTP` → `GTP` + `IF1` + `IF2_degraded` + `RS30S` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000701` | `RS30S_IF1_IF2_GTP` → `GTP` + `IF1_degraded` + `IF2` + `RS30S` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000702` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF1` + `IF2` + `RS30S_degraded` + `fMettRNAfMetCAU` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000703` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF1` + `IF2_degraded` + `RS30S` + `fMettRNAfMetCAU` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000704` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU` → `GTP` + `IF1_degraded` + `IF2` + `RS30S` + `fMettRNAfMetCAU` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000705` | `RS30S_IF1_mRNA` → `IF1` + `RS30S_degraded` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000706` | `RS30S_IF1_mRNA` → `IF1_degraded` + `RS30S` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000707` | `RS30S_IF1_fMettRNAfMetCAU_mRNA` → `IF1` + `RS30S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000708` | `RS30S_IF1_fMettRNAfMetCAU_mRNA` → `IF1_degraded` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000709` | `RS30S_IF1_IF2_GTP_mRNA` → `GTP` + `IF1` + `IF2` + `RS30S_degraded` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000710` | `RS30S_IF1_IF2_GTP_mRNA` → `GTP` + `IF1` + `IF2_degraded` + `RS30S` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000711` | `RS30S_IF1_IF2_GTP_mRNA` → `GTP` + `IF1_degraded` + `IF2` + `RS30S` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000712` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1` + `IF2` + `RS30S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000713` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1` + `IF2_degraded` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000714` | `RS30S_IF1_IF2_GTP_fMettRNAfMetCAU_mRNA` → `GTP` + `IF1_degraded` + `IF2` + `RS30S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_B2` | 0 | transition | — | — |
| `re0000000727` | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2_degraded` + `IF3` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000728` | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2` + `IF3` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000729` | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2` + `IF3_degraded` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000730` | `RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2` + `IF3` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000731` | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2` + `IF3` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000732` | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2_degraded` + `IF3` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000733` | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2` + `IF3` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000734` | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1_degraded` + `IF2` + `IF3` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000735` | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2` + `IF3_degraded` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000736` | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2_degraded` + `IF3` + `PO4` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000737` | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2` + `IF3` + `PO4` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000738` | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2` + `IF3_degraded` + `PO4` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000739` | `RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2` + `IF3` + `PO4` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000740` | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2` + `IF3` + `PO4` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000741` | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2_degraded` + `IF3` + `PO4` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000742` | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2` + `IF3` + `PO4` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000743` | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1_degraded` + `IF2` + `IF3` + `PO4` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000744` | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2` + `IF3_degraded` + `PO4` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000767` | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000768` | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2_degraded` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000769` | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF2` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000770` | `RS70S_IF3_fMettRNAfMetCAU_mRNA` → `IF3` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000771` | `RS70S_IF3_fMettRNAfMetCAU_mRNA` → `IF3` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000772` | `RS70S_IF3_fMettRNAfMetCAU_mRNA` → `IF3_degraded` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000773` | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1` + `IF3` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000774` | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1` + `IF3` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000775` | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1_degraded` + `IF3` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000776` | `RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` → `IF1` + `IF3_degraded` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000777` | `RS70S_IF1_fMettRNAfMetCAU_mRNA` → `IF1` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000778` | `RS70S_IF1_fMettRNAfMetCAU_mRNA` → `IF1` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000779` | `RS70S_IF1_fMettRNAfMetCAU_mRNA` → `IF1_degraded` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000780` | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2` + `RS30S_degraded` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000781` | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2_degraded` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000782` | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1` + `IF2` + `RS30S` + `RS50S_degraded` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000783` | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` → `GDP` + `IF1_degraded` + `IF2` + `RS30S` + `RS50S` + `fMettRNAfMetCAU` + `mRNA` | `Initiation_C` | 0 | transition | — | — |
| `re0000000801` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1` → `Pept0003tRNAGlyGCC` + `RF1` + `RS30S_degraded` + `RS50S` + `mRNA` | `Termination_A_RF1` | 0 | transition | — | — |
| `re0000000802` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1` → `Pept0003tRNAGlyGCC` + `RF1` + `RS30S` + `RS50S_degraded` + `mRNA` | `Termination_A_RF1` | 0 | transition | — | — |
| `re0000000803` | `RF1` → `RF1_degraded` | `Termination_A_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000804` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1` → `Pept0003tRNAGlyGCC` + `RF1_degraded` + `RS30S` + `RS50S` + `mRNA` | `Termination_A_RF1` | 0 | transition | — | — |
| `re0000000805` | `termRS70SUAA0004_tRNAGlyGCC_RF1` → `RF1` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_A_RF1` | 0 | transition | — | — |
| `re0000000806` | `termRS70SUAA0004_tRNAGlyGCC_RF1` → `RF1` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_A_RF1` | 0 | transition | — | — |
| `re0000000807` | `termRS70SUAA0004_tRNAGlyGCC_RF1` → `RF1_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_A_RF1` | 0 | transition | — | — |
| `re0000000808` | `termRS70SUAA0004_tRNAGlyGCC` → `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_A_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000809` | `termRS70SUAA0004_tRNAGlyGCC` → `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_A_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000816` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2` → `Pept0003tRNAGlyGCC` + `RF2` + `RS30S_degraded` + `RS50S` + `mRNA` | `Termination_A_RF2` | 0 | transition | — | — |
| `re0000000817` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2` → `Pept0003tRNAGlyGCC` + `RF2` + `RS30S` + `RS50S_degraded` + `mRNA` | `Termination_A_RF2` | 0 | transition | — | — |
| `re0000000818` | `RF2` → `RF2_degraded` | `Termination_A_RF2` (+1 shared) | 0 | transition | — | — |
| `re0000000819` | `elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2` → `Pept0003tRNAGlyGCC` + `RF2_degraded` + `RS30S` + `RS50S` + `mRNA` | `Termination_A_RF2` | 0 | transition | — | — |
| `re0000000820` | `termRS70SUAA0004_tRNAGlyGCC_RF2` → `RF2` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_A_RF2` | 0 | transition | — | — |
| `re0000000821` | `termRS70SUAA0004_tRNAGlyGCC_RF2` → `RF2` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_A_RF2` | 0 | transition | — | — |
| `re0000000822` | `termRS70SUAA0004_tRNAGlyGCC_RF2` → `RF2_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_A_RF2` | 0 | transition | — | — |
| `re0000000824` | `RF3` → `RF3_degraded` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000835` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` → `GTP` + `RF1` + `RF3` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000836` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` → `GTP` + `RF1` + `RF3` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000837` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` → `GTP` + `RF1_degraded` + `RF3` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000848` | `RF3_GDP` → `GDP` + `RF3_degraded` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000849` | `RF3_GTP` → `GTP` + `RF3_degraded` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000850` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP` → `GTP` + `RF1` + `RF3_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000851` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP` → `GDP` + `RF1` + `RF3` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000852` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP` → `GDP` + `RF1` + `RF3` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000853` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP` → `GDP` + `RF1_degraded` + `RF3` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000854` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP` → `GDP` + `RF1` + `RF3_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000855` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` → `RF1` + `RF3` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000856` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` → `RF1` + `RF3` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000857` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` → `RF1_degraded` + `RF3` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000858` | `termRS70SUAA0004_tRNAGlyGCC_RF1_RF3` → `RF1` + `RF3_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` | 0 | transition | — | — |
| `re0000000859` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` → `GTP` + `RF3` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000860` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` → `GTP` + `RF3` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000861` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GTP` → `GTP` + `RF3_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000862` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4` → `GDP` + `PO4` + `RF3` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000863` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4` → `GDP` + `PO4` + `RF3` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000864` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4` → `GDP` + `PO4` + `RF3_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000865` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP` → `GDP` + `RF3` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000866` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP` → `GDP` + `RF3` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000867` | `termRS70SUAA0004_tRNAGlyGCC_RF3_GDP` → `GDP` + `RF3_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF1` (+1 shared) | 0 | transition | — | — |
| `re0000000876` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` → `GTP` + `RF2` + `RF3` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000877` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` → `GTP` + `RF2` + `RF3` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000878` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` → `GTP` + `RF2_degraded` + `RF3` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000885` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP` → `GTP` + `RF2` + `RF3_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000886` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP` → `GDP` + `RF2` + `RF3` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000887` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP` → `GDP` + `RF2` + `RF3` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000888` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP` → `GDP` + `RF2_degraded` + `RF3` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000889` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP` → `GDP` + `RF2` + `RF3_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000890` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` → `RF2` + `RF3` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000891` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` → `RF2` + `RF3` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000892` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` → `RF2_degraded` + `RF3` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000893` | `termRS70SUAA0004_tRNAGlyGCC_RF2_RF3` → `RF2` + `RF3_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_B_RF2` | 0 | transition | — | — |
| `re0000000894` | `RRF` → `RRF_degraded` | `Termination_C` | 0 | transition | — | — |
| `re0000000897` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` → `EFG` + `GTP` + `RRF` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000898` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` → `EFG` + `GTP` + `RRF` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000899` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` → `EFG` + `GTP` + `RRF_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000903` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP` → `EFG_degraded` + `GTP` + `RRF` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000924` | `RS50S_tRNAGlyGCC` → `RS50S_degraded` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000925` | `RS50S_RRF` → `RRF` + `RS50S_degraded` | `Termination_C` | 0 | transition | — | — |
| `re0000000926` | `termRS30S_mRNA` → `RS30S_degraded` + `mRNA` | `Termination_C` | 0 | transition | — | — |
| `re0000000927` | `RS50S_tRNAGlyGCC` → `RS50S` + `tRNAGlyGCC_degraded` | `Termination_C` | 0 | transition | — | — |
| `re0000000928` | `RS50S_RRF` → `RRF_degraded` + `RS50S` | `Termination_C` | 0 | transition | — | — |
| `re0000000929` | `RS50S_tRNAGlyGCC_RRF` → `RRF` + `RS50S` + `tRNAGlyGCC_degraded` | `Termination_C` | 0 | transition | — | — |
| `re0000000930` | `RS50S_tRNAGlyGCC_RRF` → `RRF` + `RS50S_degraded` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000931` | `RS50S_tRNAGlyGCC_RRF` → `RRF_degraded` + `RS50S` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000932` | `RS50S_tRNAGlyGCC_EFG_GDP` → `EFG` + `GDP` + `RS50S` + `tRNAGlyGCC_degraded` | `Termination_C` | 0 | transition | — | — |
| `re0000000933` | `RS50S_tRNAGlyGCC_EFG_GDP` → `EFG` + `GDP` + `RS50S_degraded` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000934` | `RS50S_tRNAGlyGCC_EFG_GDP` → `EFG_degraded` + `GDP` + `RS50S` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000935` | `RS50S_RRF_EFG_GDP` → `EFG` + `GDP` + `RRF_degraded` + `RS50S` | `Termination_C` | 0 | transition | — | — |
| `re0000000936` | `RS50S_RRF_EFG_GDP` → `EFG` + `GDP` + `RRF` + `RS50S_degraded` | `Termination_C` | 0 | transition | — | — |
| `re0000000937` | `RS50S_RRF_EFG_GDP` → `EFG_degraded` + `GDP` + `RRF` + `RS50S` | `Termination_C` | 0 | transition | — | — |
| `re0000000938` | `termRS70SUAA0004_tRNAGlyGCC_RRF` → `RRF` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000939` | `termRS70SUAA0004_tRNAGlyGCC_RRF` → `RRF` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000940` | `termRS70SUAA0004_tRNAGlyGCC_RRF` → `RRF_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000941` | `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP` → `EFG` + `GTP` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000942` | `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP` → `EFG` + `GTP` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000943` | `termRS70SUAA0004_tRNAGlyGCC_EFG_GTP` → `EFG_degraded` + `GTP` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000944` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP` → `EFG` + `GDP` + `RRF` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000945` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP` → `EFG` + `GDP` + `RRF` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000946` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP` → `EFG` + `GDP` + `RRF_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000947` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP` → `EFG_degraded` + `GDP` + `RRF` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000948` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `RRF` + `RS30S_degraded` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000949` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `RRF` + `RS30S` + `RS50S_degraded` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000950` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` → `EFG` + `GDP` + `PO4` + `RRF_degraded` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000951` | `termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4` → `EFG_degraded` + `GDP` + `PO4` + `RRF` + `RS30S` + `RS50S` + `mRNA` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000952` | `RS50S_tRNAGlyGCC_RRF_EFG_GDP` → `EFG` + `GDP` + `RRF` + `RS50S` + `tRNAGlyGCC_degraded` | `Termination_C` | 0 | transition | — | — |
| `re0000000953` | `RS50S_tRNAGlyGCC_RRF_EFG_GDP` → `EFG` + `GDP` + `RRF` + `RS50S_degraded` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000954` | `RS50S_tRNAGlyGCC_RRF_EFG_GDP` → `EFG_degraded` + `GDP` + `RRF` + `RS50S` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |
| `re0000000955` | `RS50S_tRNAGlyGCC_RRF_EFG_GDP` → `EFG` + `GDP` + `RRF_degraded` + `RS50S` + `tRNAGlyGCC` | `Termination_C` | 0 | transition | — | — |

</details>

## 6. 数学与物料验收（任何 A→D 替代之前）

1. **Stoichiometry**：原路径列和须等于净反应列，含 AA、aa-tRNA、ATP/GTP/ADP/GDP/AMP、Pi/PPi、因子绑定状态、核糖体占据；源中未定义的 H₂O/H⁺/Mg 化学不可私自补成‘守恒已验证’。
2. **Kinetic closure**：写出推导的 `J_eff(boundary states, available resources, θ)`；指出它是 exact、QSSA、fast-equilibrium、delay/memory、mean residence time 还是经验拟合。仅有拓扑串联不能导出瞬时一阶律。
3. **Accounting**：对 `extent`、自由与结合态载体、库存变化、颗粒数 proxy 分别核对；`J_protein_release` 不等于任意时刻的残基引入速率。
4. **Domain**：作者固定参数与 source-general 分别测试；原来 0 的侧支恢复、底物耗尽、时间尺度不分离时必须有负面例子。
5. **Benchmark**：对同一个、明确支持数值运行的参数域，比较原 968 通道和候选模型的完整蛋白、两个 Gly incorporation 阶段、能量/因子释放、关键占据和累计积分。初始 transient 与长时间误差分别报告。
6. **Approval**：记录每次审查者批准的链 ID、保留/消去物种、有效动力学表达式、原 ID→新 ID 的一对多映射和增减后的实数目；未批准前不可把 P1/P2 算成已完成模型。

## 7. 统计校验

- 不重复索引：968 source rows / 968 unique IDs。
- 互斥功能组总计：968；作者条件非零 k：483；k=0：485。
- 26 个源子系统成员可重叠。算法的 12 组覆盖 30 条不重复方向；其中 3 组是可逆结合/解离对，合计 6 条，不作为 A→D 约化。余下 9 组含 24 条源方向，若均经动力学验证并各替换 1 条则假设净减少 15 条（483→468），**尚未验证**。
- 该文件为已有审计数据的可读投影，不更改标准 SBML、作者参数、`reduction_decisions.csv` 或历史 QSSA 结果。
