# B1-3 正式限定范围科学接受（2026-10-10）

当前科学决定：**B1_3_FORMALLY_ACCEPTED_LIMITED_SCOPE**。接受范围为 RF1/RF2 termination、RF3 替代路线、游离 Pept0003 释放及源模型支持的 ribosome recycling 的 **source-exact structural reconstruction**。

## 决定来源与历史状态

本记录登记研究者通过 **2026-10-10 会话**作出的决定。会话提供的[授权原文](../rapid_reduction/human_decision_source_20261010.txt)引用：

> 我觉得没问题，正式接受，然后给我一个 sean codex prompt 把当前降维简化正式收束，还要更新之前的 html 方便展示。

该原文随后明确列出 H1–H9 和 Phase C 的决定、条件与排除项。本文件是该会话决定的追加登记，没有新增研究者身份、手写签名、精确批准时刻或外部签署 URL。人工科学决定、工程检验和 Git 发布是不同的状态。

本记录作为**当前决定**取代历史 `PENDING_HUMAN_REVIEW`；[原复核表](phase_b1_3_review.md)、协议、见证、日志、失败记录及其原字节保持不变。旧记录中的待审状态与当时的禁止提交条件仍是正确的历史证据，不应据此否定本次较新的明确接受。上游 [B1-2 正式接受](phase_b1_2_formal_signoff_2026-10-10.md) 的 H3/H4/H6 限制继续有效。

## H1–H9 正式决定

| Gate | 正式决定 | 接受范围与保留条件 |
|---|---|---|
| H1 | Y | 接受 B1-2 W4 终点与 RF-free 终止入口的精确源种连续性；`T_pre` 是项目缩写，原种为 `elRS70SAUAA0004_Pept0003tRNAGlyGCC`。 |
| H2 | Y | 接受 RF1/RF2 竞争同一源入口，一次结合消费同一枚入口 token；正参数解离允许重新选择分支，不代表同时释放两肽。 |
| H3 | Y | 接受 `re0000000798` / `re0000000813` 产生游离 `Pept0003`，并分别留下 RF1-bound / RF2-bound 终止复合物；作者关闭的肽释放逆向仍保留。 |
| H4 | CONDITIONAL | 接受直接 RF 解离、RF3-GDP 核苷酸交换、预供应 RF3-GTP 与 apo-RF3 路径作为替代路线；不作生理主导机制排序。RF3、游离 GDP/GTP 与其结合态必须区分，有限供应仍是边界假设。 |
| H5 | CONDITIONAL | 接受 RRF/EF-G 回收的源事件连续性，实际 70S 拆分为 `re0000000910`；其产物为 occupied 子单位，后续事件才恢复 free 组分。新的有限 `EFG_GTP` 与 RRF 供应不等于已证实的内源再生。 |
| H6 | CONDITIONAL | 接受精确源物种账本及 `S*w`，W4 的 5 PO4 仅计一次；joint 直接/交换路径分别为 6/7 PO4。源 token 账本不是完整分子、元素、核苷酸基团、离子或电荷认证。 |
| H7 | CONDITIONAL | 接受已记录的 RF1/RF2 竞争、正参数反向/重新结合、作者零参数及降解上下文；最短结构见证不证明主导通量、路径概率或完整路径穷举。 |
| H8 | CONDITIONAL | 接受原始 SBML 身份与 S12–S16/S27 的有出处提取；生理解释与载体投影保留 `INFERRED` 边界。源物种身份不独立认证详细肽化学、完整组成或生理时序，独立完整 SI 文本证据缺口不被填补。 |
| H9 | CONDITIONAL | 接受从源结构提出和审阅聚合问题的边界；两轮 Gly 的近似与 7-to-5 recycling 的精确观测商必须分开。具体 Phase C 接受见独立记录，不授权 RF1/RF2 精确合并或新一轮研究。 |

**3 项 Y、6 项 CONDITIONAL、0 项 N、0 项 PENDING。** CONDITIONAL 是正式接受的适用范围条件，不能自动改成无条件 Y。B1-3 的结构接受本身不等于动力学验证；已完成的有限域 Phase C 动力学候选另见 [Phase C 正式接受](../rapid_reduction/phase_c_formal_acceptance_20261010.md)。

## 原始源物种与关键事件

原种、完整源反应方程、逆向、出处与参数见 [source scope](phase_b1_3_source_scope.json)、[逐事件路径](phase_b1_3_termination_recycling_pathways.md) 及 [原始来源附录](phase_b1_3_original_source_evidence.md)。以下方程是原始源事件，不是新有效反应：

```text
re0000000796  k=60
RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1
re0000000798  k=0.5
elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF1
re0000000811  k=23
RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2
re0000000813  k=1.5
elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF2
re0000000910  k=1000
termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP -> RS50S_tRNAGlyGCC_RRF_EFG_GDP + termRS30S_mRNA
re0000000911  k=1000
termRS30S_mRNA -> RS30S + mRNA
```

RF1/RF2 入口反向 `re0000000797` / `re0000000812` 为正参数；肽释放反向 `re0000000810` / `re0000000823` 与 0910 反向 `re0000000957` 为作者零参数。直接 RF 释放为 `re0000000799` / `re0000000814`。RF3 交换路线使用两套 RF-bound 原状态，分别经 `0829/0843/0846/0838` 与 `0870/0881/0884/0879`，随后共享 `0840/0842/0847`；完整 ID 均在上述原证据内保留。七个 occupied 50S 尾态的 12 条释放方向为 `re0000000308` 与 `re0000000913`–`re0000000923`，不可将 0910 本身说成全部 free 组分已经释放。

## 接受的源物种资源账本

[34 个原始见证](phase_b1_3_witnesses.json) 的 `resource_ledger`、`exact_net_stoichiometry`、逐事件库存与 carrier DAG 是完整账本权威。每条新增有限供应都有具体源物种身份；上游继承与新增供应分开。以下仅汇总四条 joint 见证的精确事件和（**CONCEPTUAL_NET，不是新源反应或有效速率律**）：

直接 RF1 与直接 RF2 分支各为 42 个原事件，具有相同净式但不同反应历史：

```text
3 EFG_GTP + 2 EFTu_GTP_GlytRNAGlyGCC + IF2_GTP_fMettRNAfMetCAU
 -> 3 EFG_GDP + 2 EFTu_GDP + IF2_GDP + 6 PO4 + Pept0003
    + 2 tRNAGlyGCC + tRNAfMetCAU
```

RF3-GDP 交换后的 RF1 与 RF2 joint 分支各为 48 个原事件：

```text
3 EFG_GTP + 2 EFTu_GTP_GlytRNAGlyGCC + IF2_GTP_fMettRNAfMetCAU + GTP
 -> 3 EFG_GDP + 2 EFTu_GDP + IF2_GDP + 7 PO4 + Pept0003
    + 2 tRNAGlyGCC + tRNAfMetCAU + GDP
```

这些 joint 净式省去了净变化为零的 RF、RRF、RS30S、RS50S、mRNA、IF1/IF3；它们仍是显式有限库存。相对 B1-2 W4，直接路径新增一份 `EFG_GTP`、一份相应 RF1 或 RF2 和一份 RRF；交换路径再新增一份 `RF3_GDP` 与一份游离 GTP。W4 已含两份 EFG-GTP、两份 EF-Tu/Gly-tRNA 复合供应及五份 PO4 释放，不能重复计算。

直接回收新增 1 PO4；RF3-GDP 交换另消费 1 free GTP、产生 1 free GDP 和 1 PO4，RF3-GDP 最终恢复。预供应 RF3-GTP 的分支消费该复合种并产生 RF3-GDP、PO4，不可再扣一份 free GTP；apo-RF3 路径另使用 free GTP，且 RF3 最终处于 GDP-bound 状态。EFG-GDP、EFTu-GDP、IF2-GDP 不能按 free GDP 记账；GDP-form 释放不是 GTP-form 再生。

## 工程证据与明确未接受项

原工程报告记录 A–M PASS、34 个见证、36/36 负控，其中 11 个 Petri-enabled 案例因载体历史无效被拒绝；Phase C 的 [B1-3 独立重核](../rapid_reduction/b1_3_independent_scientific_audit.md) 与 [fresh audit](../../../results/reduction/rapid_v1/b1_3_fresh_audit.json) 另重算原 34 条历史。这里引用已保存结果，不冒称本文件新运行了这些检查。新发布验证由 release wrapper 的新增运行记录另行报告。

接受仍不覆盖完整组成、全网络元素/电荷/渗透压认证、实验验证、普适生理时序、全路径穷举或主导机制排序。RF1/RF2 不能合并成一个精确态：相同总占用可给出 0.5 与 1.5 的肽释放导数。B1-2 H3/H4/H6 的虚拟态、转位和术语边界全部保留。继承 MATLAB **99 passed / 3 failed / 1 incomplete** 未因本次接受而被修复、重跑或记为 PASS。

完整原文件分类、SHA-256 与保存位置见 [release manifest](../rapid_reduction/release_manifest_v1.json)；当前机器可读决定见 [current_decision_v1.json](../rapid_reduction/current_decision_v1.json)。科学接受不单独宣告 Git 发布已完成；实际发布须通过原字节保护、验证与远端同步核验。


## 冻结关键证据 SHA-256

以下为本记录读取的原文件指纹；所有逐轨迹文件另由完整 manifest 枚举。

| 原路径（相对仓库根） | bytes | SHA-256 |
|---|---:|---|
| `docs/reduction/pathways/phase_b1_3_review.md` | 23348 | `355b0de3bb20bb0605fff6b827005a7ea8c48e5af886002b7e8ee82de32d94da` |
| `docs/reduction/pathways/phase_b1_3_witnesses.json` | 2424115 | `91f492af2b7b72bf253c3fe0fba583b6d6a980d6c107017ea29fbc3c2abd000d` |
| `docs/reduction/pathways/phase_b1_3_validation_report.json` | 64219 | `10e3da2c48074e5121e1b242bfd3263cddd855a9be0a55baf26376f5030fce2f` |
| `docs/reduction/pathways/phase_b1_3_independent_verification.json` | 77301 | `fdd4a54480dfa194d88e93127f82802e805debaf9d09ef5ff21f6562d031230b` |
| `docs/reduction/pathways/phase_b1_3_matrix_verification.json` | 524263 | `1e81071162ed2a235926d6192bdc529a84df269f8232e2404fff30cff0e61297` |
| `docs/reduction/pathways/phase_b1_3_original_source_evidence.json` | 145769 | `506d5642dad2662d726f04b17e48d05a8db71e3988f0aa42eef294f484668d96` |
| `docs/reduction/pathways/phase_b1_3_source_scope.json` | 1670315 | `d30bde807c7b3176aeee9fe8c86210008f906232f53e41f1b5f1b1c7bf02be24` |
