# PURE Reaction Atlas B1-1 — 正式限定范围科学签署

正式科学状态：**B1_1_FORMALLY_ACCEPTED_LIMITED_SCOPE**。

研究者于 2026-10-09 在本会话中明确正式确认：“批准 PURE Reaction Atlas Phase B1-1 的限定范围科学验收。” 本记录由 sean Codex 登记，只覆盖 **source-exact structural pathways**。

## H1–H5 正式审阅结论

| 项目 | 正式结论 | 验收范围 |
|---|---|---|
| H1：E1 起始出口 | Y | 源模型定义的 E1 起始出口及其原始物种边界。 |
| H2：E1 → E2 交接 | Y，源模型限定 | 0001 是作者模型 ELONG_tRNA_release，先产生 E2，随后由第一次 Gly-tRNA 结合 0013 消耗；不认证完整生理机理。 |
| H3：替代装配与释放路径 | Y | 源精确替代装配和因子释放顺序，包括独立 IF3-first 正例；P1 保留为 LEXICOGRAPHIC_STRUCTURAL_WITNESS。 |
| H4：核苷酸及资源账本 | Y | 精确净化学计量、游离物种恢复及源核苷酸状态区分；IF2_GDP 释放不等于 IF2_GTP 恢复。 |
| H5：复合物完整分子组成 | Y，限定于源物种交接，完整组成仍 INFERRED | 接受 source-exact 物种和多载体结构交接；E1/E2 的 mRNA、肽基状态及完整复合物组分继续 INFERRED。 |

## 已验收的源路径与解释边界

独立 IF3-first 释放正例，逐事件净计量、Petri 可执行性、carrier lineage、IF1/IF3 恢复、参数、逆向及 E1 终点均通过独立核验：

```text
re0000000459 → re0000000507 → re0000000513 → re0000000519 → re0000000529 → re0000000717 → re0000000722 → re0000000747 → re0000000757 → re0000000726
```

精确净计量（CONCEPTUAL_NET，不新增源反应或有效速率律）：

```text
IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> IF2_GDP + PO4 + elRS70SAGGU0002_fMettRNAfMetCAU
```

IF1 和 IF3 恢复到游离原始状态；IF2_GDP 是释放产物，其释放不等于 IF2_GTP 恢复。完整逐事件证据见 [IF3-first 路径](phase_b1_1_followup_pathway.md) 和 [机器证据](phase_b1_1_followup_witness.json)。

现有 P1 保留，追加标记为 `LEXICOGRAPHIC_STRUCTURAL_WITNESS`。0724 是源 ID 排序选中的结构见证，不表示动力学主导路径。0724、0747、0749 的共享源状态为 `RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA`。

| 源反应 | 释放因子 | 作者参考参数 | 精确逆向 |
|---|---|---:|---|
| re0000000724 | IF1 | 0.0025 | re0000000723 |
| re0000000747 | IF3 | 1000 | re0000000748 |
| re0000000749 | IF2_GDP | 4 | re0000000750 |

这些参数是作者源模型参考参数，不是实测路径通量。实际路径通量及动力学优势均未获认证。

`re0000000001` 是作者原始模型定义的 `ELONG_tRNA_release`：E1 产生 E2 和 tRNAfMetCAU，随后模型中的第一次 Gly-tRNA 延伸结合反应 `re0000000013` 消耗 E2。此状态依赖顺序不得直接解释成真实细菌核糖体中起始 tRNA 释放、肽键形成和转位的完整物理机制。

接受 E1/E2 源物种及多载体结构交接。E1/E2 的 mRNA、肽基状态及完整复合物组分仍为 **INFERRED**。后续原论文/SI 对状态定义、完整组成和生理步骤映射的证据需求继续未解决，见机器记录的 `future_original_source_evidence_required`。

## 签署前重新执行的验证

- 原九个 B1-1 witness 与新 IF3-first 正例独立验证：PASS。
- 原 B1-1 23 项及 Follow-up 12 项负控：**35/35 PASS**，未运行 0。
- Phase A、B0、HTML 和实际浏览器回归：PASS；浏览器交互检查 222 项。
- 原 B1-1 三个确定性文件、Follow-up 两个文件各重建两次：均与交付字节一致。
- 原 A–J PASS 及历史报告不变；2362 个既有 tracked 文件与 30 个 B1-1/Follow-up 文件均逐字节保留。

本轮完整结果、实际命令、stdout/stderr、退出码和真实诊断见 [新增发布验证证据](phase_b1_1_formal_acceptance_publication_checks.json)。签署及来源哈希、决定历史、文件白名单见 [正式签署机器记录](phase_b1_1_formal_signoff_2026-10-09.json)。

原 [B1-1 审阅](phase_b1_1_review.md) 和 [Follow-up 审阅](phase_b1_1_followup_review.md) 中的待审/条件接受状态、当时 commit/push hold 和失败历史继续作为原始历史证据保留；本次新增签署记录给出当前正式限定范围验收及发布授权。原负控中拒绝篡改条件审阅为签署的测试继续有效，本次正式授权由独立新增记录提供。

## 保留历史日志的格式例外

完整暂存格式检查实际返回退出码 2，发现且仅发现以下两处历史原生日志末尾空行：

- `phase_b1_1_execution_log.txt:399`：new blank line at EOF。
- `phase_b1_1_followup_execution_log.txt:366`：new blank line at EOF。

两文件的工作区字节和暂存 blob 均与本次开始时的历史 SHA-256 完全一致。为遵守历史文件保留要求，仅将这两处已核实的日志末尾空行登记为格式例外；其余全部文件的暂存格式检查退出码为 0。原失败输出、实际退出码、例外路径及哈希均保存在新增发布验证证据中。任何额外格式错误都会阻止发布，科学验证结果仍全部 PASS。

## 发布授权与停止边界

研究者授权在 `codex/energy-cycles-v1` 分支提交并普通推送本次白名单中的 **33 个新增文件**：原 B1-1 16 个、Follow-up 14 个、本次签署和发布核验 3 个。原始 SBML、参数、Phase A/B0 和历史测试报告均不得修改。起始 HEAD 为 `50888efa205837dabb621e42bf117738af661150`，起始 ahead/behind 为 0/0。

提交前核对暂存清单、仅新增状态、暂存 blob 与工作区原始字节及 whitespace；推送后核对远端 HEAD、提交文件清单、ahead/behind 和工作树。此签署记录形成于提交前，发布完成状态在提交与远端核对后报告。

```json
{
  "scientific_status": "B1_1_FORMALLY_ACCEPTED_LIMITED_SCOPE",
  "researcher_formally_signed": true,
  "phase_b1_1_formally_accepted": true,
  "commit_push_authorized": true,
  "phase_b1_2_authorized": false,
  "qssa_authorized": false,
  "kinetic_reduction_authorized": false
}
```

完成授权提交与普通推送后停止。不得自动开始 B1-2、QSSA 或任何动力学降阶。
