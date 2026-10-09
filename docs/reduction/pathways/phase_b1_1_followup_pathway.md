# B1-1 Human Review Follow-up — IF3-first release

建议审阅状态：`B1_1_CONDITIONALLY_ACCEPTED`。这不是研究者正式签署；等待正式确认。原有 A–J PASS 和历史文件保持原样。

## 五项 Human Review

| 项目 | 用户结论 | 本次必要处理 |
|---|---|---|
| H1 — E1 initiation exit | Y | RETAIN_SOURCE_MODEL_BOUNDARY |
| H2 — 0001 elongation handoff | Y | DISTINGUISH_MODEL_ORDER_FROM_PHYSIOLOGICAL_MECHANISM |
| H3 — Alternative assembly/release routes | Y，限定 | LABEL_ID_ORDER_AND_TEST_0747_0757 |
| H4 — Nucleotide/resource ledger | Y | RETAIN_IF2_GDP_VS_IF2_GTP_DISTINCTION |
| H5 — Composite molecular identity | 限定接受 | FULL_COMPOSITION_REMAINS_INFERRED |

## 现有 P1 的追加标记

P1 保留，并在本记录中追加 `LEXICOGRAPHIC_STRUCTURAL_WITNESS` 标记。`re0000000724` 由源 ID 排序选中，不代表动力学主导路径。此标记通过带哈希的历史文件引用应用，未重写原 P1 或原 PASS 报告。

## 独立 IF3-first 正例

新见证：`B1-1-FOLLOWUP-IF3-FIRST`；10 个实际有向反应事件；源状态里程碑选择 IF3 先释放，再释放 IF1。这是与 P1 并列的独立场景，不能把两条路线串成同一核糖体的连续处理。

边界供应（各 1 个形式 token）：`IF1, IF2_GTP_fMettRNAfMetCAU, IF3, RS30S, RS50S, mRNA`。IF2/fMet-tRNA 为明确的 B0-W3 接口条件输入；本正例不重复执行或重复计数 B0 事件。形式库存不是浓度或实验轨迹。

| Event | Original directed reaction | Complete source equation | Level-C | Author k1 | Exact inverse / k1 |
|---|---|---|---|---:|---|
| B1-1-FOLLOWUP-IF3-FIRST:E01 | re0000000459 | `IF3 + RS30S -> RS30S_IF3` | INIT_assembly | 1160 (REFERENCE_ENABLED) | re0000000460 / 0.8 (REFERENCE_ENABLED) |
| B1-1-FOLLOWUP-IF3-FIRST:E02 | re0000000507 | `IF1 + RS30S_IF3 -> RS30S_IF1_IF3` | INIT_assembly | 20 (REFERENCE_ENABLED) | re0000000508 / 0.7 (REFERENCE_ENABLED) |
| B1-1-FOLLOWUP-IF3-FIRST:E03 | re0000000513 | `RS30S_IF1_IF3 + mRNA -> RS30S_IF1_IF3_mRNA` | INIT_assembly | 36 (REFERENCE_ENABLED) | re0000000514 / 0.7 (REFERENCE_ENABLED) |
| B1-1-FOLLOWUP-IF3-FIRST:E04 | re0000000519 | `IF2_GTP_fMettRNAfMetCAU + RS30S_IF1_IF3_mRNA -> RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_tRNA_recruitment | 220 (REFERENCE_ENABLED) | re0000000520 / 1 (REFERENCE_ENABLED) |
| B1-1-FOLLOWUP-IF3-FIRST:E05 | re0000000529 | `RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA + RS50S -> RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA` | INIT_70S_formation | 34 (REFERENCE_ENABLED) | re0000000530 / 35 (REFERENCE_ENABLED) |
| B1-1-FOLLOWUP-IF3-FIRST:E06 | re0000000717 | `RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA -> RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment | 2.3 (REFERENCE_ENABLED) | re0000000718 / 2.1 (REFERENCE_ENABLED) |
| B1-1-FOLLOWUP-IF3-FIRST:E07 | re0000000722 | `RS70S_IF1_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA -> PO4 + RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_energy_commitment | 12 (REFERENCE_ENABLED) | re0000000746 / 0 (REFERENCE_DISABLED) |
| B1-1-FOLLOWUP-IF3-FIRST:E08 | re0000000747 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release | 1000 (REFERENCE_ENABLED) | re0000000748 / 0 (REFERENCE_DISABLED) |
| B1-1-FOLLOWUP-IF3-FIRST:E09 | re0000000757 | `RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA` | INIT_factor_release | 1000 (REFERENCE_ENABLED) | re0000000758 / 0 (REFERENCE_DISABLED) |
| B1-1-FOLLOWUP-IF3-FIRST:E10 | re0000000726 | `RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + elRS70SAGGU0002_fMettRNAfMetCAU` | INIT_factor_release | 4 (REFERENCE_ENABLED) | re0000000752 / 200 (REFERENCE_ENABLED) |

**精确净计量（CONCEPTUAL_NET；不是新的源反应或速率律）：**

```text
IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> IF2_GDP + PO4 + elRS70SAGGU0002_fMettRNAfMetCAU
```

IF1 和 IF3 以各自原始游离状态恢复；IF2_GDP 为释放产物，不是 IF2_GTP 再生。源状态链、所有共反应物、逐事件标记和 token 来源保存在 JSON，执行结果属于独立验证报告。

## 共享 GDP 源状态的三个竞争出口

| Original ID | Complete source equation | Reference k1 | Exact inverse / k1 |
|---|---|---:|---|
| re0000000724 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF1 + RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA` | 0.0025 | re0000000723 / 16 |
| re0000000747 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF3 + RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA` | 1000 | re0000000748 / 0 |
| re0000000749 | `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA -> IF2_GDP + RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA` | 4 | re0000000750 / 200 |

三条方向消耗同一个原始物种 `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`。它们是竞争出口；逆向是保留的源方向，不会自动执行。参考速率常数不是实测路径通量，本次不计算或比较轨迹通量。

## E1 / E2 生化解释限制

`re0000000001` 是作者原始模型定义的 `ELONG_tRNA_release` 状态转换：

```text
elRS70SAGGU0002_fMettRNAfMetCAU -> elRS70SAGGU0002_fMet + tRNAfMetCAU
```

在当前模型交接见证中，它先产生 E2；随后第一次 Gly-tRNA 延伸结合反应 `re0000000013` 消耗 E2：

```text
EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC
```

这验证了源模型中 0001 → 0013 的状态依赖顺序。不得把此顺序直接解释为真实细菌核糖体中起始 tRNA 释放、肽键形成和转位的完整物理机制，也不据此确定常规生理时间顺序。本 follow-up 的事实权威是原始 SBML 方程及状态依赖；没有新增论文级物理机制证书。

E1/E2 的 mRNA、肽基状态及完整复合物组分继续为 `INFERRED`。源物种 ID 的连续性不等于全局分子组成验证；不从名称缺失推断 mRNA 释放，也不自行补写化学步骤。

## 后续原文证据需求（与当前解释限制分列）

- Locate original article/SI/state definitions explaining why 0001 precedes first Gly-tRNA encounter 0013 — `UNRESOLVED_NOT_SEARCHED_IN_THIS_STRUCTURAL_FOLLOWUP`.
- Obtain explicit E1/E2 mappings for mRNA, peptide/initiator-tRNA and complete ribosome composition — `UNRESOLVED_FULL_COMPOSITION_INFERRED`.
- Require original-source mechanistic evidence before mapping model states to initiator release, peptide-bond formation and translocation — `NO_COMPLETE_PHYSIOLOGICAL_MECHANISM_CERTIFIED`.

本次仅补充结构正例及审阅证据。正式接受仍待研究者确认；不得 commit/push、开始 B1-2、QSSA 或动力学降阶。
