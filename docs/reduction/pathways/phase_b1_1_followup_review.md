# B1-1 Human Review Follow-up — executed review record

建议审阅状态：**B1_1_CONDITIONALLY_ACCEPTED**。**不是研究者正式签署**；正式确认仍待研究者给出。

Execution: `COMPLETED`；engineering: `PASS`。原有 A–J PASS、原始 Phase A/B0/B1-1 记录和签署历史均逐字节保留。

## H1–H5：用户审阅结论与必要处理

| 项目 | 用户结论 | 已执行处理 |
|---|---|---|
| H1 — E1 initiation exit | Y | RETAIN_SOURCE_MODEL_BOUNDARY |
| H2 — 0001 elongation handoff | Y | DISTINGUISH_MODEL_ORDER_FROM_PHYSIOLOGICAL_MECHANISM |
| H3 — Alternative assembly/release routes | Y，限定 | LABEL_ID_ORDER_AND_TEST_0747_0757 |
| H4 — Nucleotide/resource ledger | Y | RETAIN_IF2_GDP_VS_IF2_GTP_DISTINCTION |
| H5 — Composite molecular identity | 限定接受 | FULL_COMPOSITION_REMAINS_INFERRED |

## 新路径与解释修订

独立 IF3-first 正例：`re0000000459 → re0000000507 → re0000000513 → re0000000519 → re0000000529 → re0000000717 → re0000000722 → re0000000747 → re0000000757 → re0000000726`。

**精确净计量：**

```text
IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> IF2_GDP + PO4 + elRS70SAGGU0002_fMettRNAfMetCAU
```

各边界物种供应 1 个形式 token；IF1/IF3 恢复到原始游离态，IF2_GDP 为实际释放产物。完整方程、参数、逆向、逐事件库存和来源链见 [新路径](phase_b1_1_followup_pathway.md) 及 [机器记录](phase_b1_1_followup_witness.json)。

现有 P1 在本次追加记录中标记为 `LEXICOGRAPHIC_STRUCTURAL_WITNESS`。0724 由 ID 排序选中，不代表动力学主导路线。0724/0747/0749 消耗同一 GDP 复合物；参考参数分别为 0.0025/1000/4，不是实测路径通量。IF3-first 与 P1 是独立场景，不共同消耗同一个有限 token。

0001 是作者模型中的 `ELONG_tRNA_release`，先产生 E2，再由第一次 Gly-tRNA 结合反应 0013 消耗。这仅验证原模型的状态依赖顺序；不得直接解释成真实细菌核糖体中起始 tRNA 释放、肽键形成和转位的完整物理机制。E1/E2 的 mRNA、肽基状态及完整复合物组成仍为 `INFERRED`。

后续原文证据需求与当前解释限制已在机器记录和路径文档中分列：需要原论文/SI 对 0001/0013 状态含义、E1/E2 组成及真实物理步骤映射的明确证据。本次没有宣称取得这些证据。

## 重新执行的验收

| Check | Status | Evidence |
|---|---|---|
| FU1 — Canonical source and original B1-1 independent rerun | PASS | phase_b1_1_followup_independent_verification.json |
| FU2 — IF3-first exact net, marking, lineage, recovery and E1 | PASS | phase_b1_1_followup_independent_verification.json |
| FU3 — Release competition and P1 lexicographic annotation | PASS | phase_b1_1_followup_witness.json |
| FU4 — Model order, composition limits and conditional review authority | PASS | phase_b1_1_followup_witness.json |
| FU5 — Historical and follow-up negative controls rerun | PASS | phase_b1_1_followup_negative_controls.json |
| FU6 — Phase A/B0/HTML/browser rerun | PASS | phase_b1_1_followup_regression.json |
| FU7 — Two fresh builds of both historical and follow-up outputs | PASS | phase_b1_1_followup_validation_report.json |
| FU8 — All beginning bytes and additive Git scope | PASS | phase_b1_1_followup_baseline.json |

原 B1-1 负控重新执行：23/23；follow-up 负控：12/12。总计 35/35；未运行 0。

原有 2362 个 tracked 文件和 16 个 B1-1 文件全部未变；原 A–J 结果仍为 PASS。

新 follow-up 两次构建与交付字节一致，原 B1-1 三个确定性文件也重新构建两次并与历史交付字节一致。

- phase_b1_1_followup_witness.json: `9e793f39ee3122119aa8e6fad9b7cc82029a6ec19a97ec8f5afb31c64244bb59`.
- phase_b1_1_followup_pathway.md: `ad3529106c57f5f672c2c94142c71d1b07428c6ea6473a12a782a64dc481db2c`.
- phase_b1_1_witnesses.json: `546badd98657cf2029a75da476a5fa9874af6db52b1f32dc4f8d6ff1702ed1d2`.
- phase_b1_1_source_scope.json: `6871bc13ff7dff6b6ba454f3404d3596df9f300a15508ab20db0991568a192ec`.
- phase_b1_1_initiation_pathways.md: `b5763a741ea4425a066b5fa973ed6478051f684c09b1ee6742c5fe9539a3da6e`.

实际命令、stdout/stderr 和退出码见 [执行日志](phase_b1_1_followup_execution_log.txt)。独立结果见 [验证报告](phase_b1_1_followup_independent_verification.json)，变异及原负控重跑见 [负控报告](phase_b1_1_followup_negative_controls.json)，Phase A/B0/HTML/browser 的实际重跑见 [回归报告](phase_b1_1_followup_regression.json)。若发生真实失败，它会追加到 phase_b1_1_followup_failure_evidence.jsonl，历史失败档案不会被改写。

## 仓库与停止状态

```json
{
  "machine": "sean",
  "repository_root": "C:\\Users\\sean\\Desktop\\GUV",
  "branch": "codex/energy-cycles-v1",
  "origin": "https://github.com/DrWanSJ/PURE.git",
  "starting_HEAD": "50888efa205837dabb621e42bf117738af661150",
  "ending_HEAD": "50888efa205837dabb621e42bf117738af661150",
  "modified_existing_files": [],
  "new_followup_files": [
    "docs/reduction/pathways/phase_b1_1_followup_baseline.json",
    "docs/reduction/pathways/phase_b1_1_followup_execution_log.txt",
    "docs/reduction/pathways/phase_b1_1_followup_independent_verification.json",
    "docs/reduction/pathways/phase_b1_1_followup_negative_controls.json",
    "docs/reduction/pathways/phase_b1_1_followup_pathway.md",
    "docs/reduction/pathways/phase_b1_1_followup_protocol.md",
    "docs/reduction/pathways/phase_b1_1_followup_regression.json",
    "docs/reduction/pathways/phase_b1_1_followup_review.md",
    "docs/reduction/pathways/phase_b1_1_followup_validation_report.json",
    "docs/reduction/pathways/phase_b1_1_followup_witness.json",
    "scripts/pathways/phase_b1_1/followup/build_followup.py",
    "scripts/pathways/phase_b1_1/followup/run_followup_validation.py",
    "scripts/pathways/phase_b1_1/followup/test_followup_negative_controls.py",
    "scripts/pathways/phase_b1_1/followup/verify_followup.py"
  ],
  "commit_push_status": "NOT_ATTEMPTED — awaiting formal researcher confirmation",
  "final_git_status": "?? docs/reduction/pathways/phase_b1_1_execution_log.txt\n?? docs/reduction/pathways/phase_b1_1_failure_evidence.jsonl\n?? docs/reduction/pathways/phase_b1_1_followup_baseline.json\n?? docs/reduction/pathways/phase_b1_1_followup_execution_log.txt\n?? docs/reduction/pathways/phase_b1_1_followup_independent_verification.json\n?? docs/reduction/pathways/phase_b1_1_followup_negative_controls.json\n?? docs/reduction/pathways/phase_b1_1_followup_pathway.md\n?? docs/reduction/pathways/phase_b1_1_followup_protocol.md\n?? docs/reduction/pathways/phase_b1_1_followup_regression.json\n?? docs/reduction/pathways/phase_b1_1_followup_review.md\n?? docs/reduction/pathways/phase_b1_1_followup_validation_report.json\n?? docs/reduction/pathways/phase_b1_1_followup_witness.json\n?? docs/reduction/pathways/phase_b1_1_independent_verification.json\n?? docs/reduction/pathways/phase_b1_1_initiation_pathways.md\n?? docs/reduction/pathways/phase_b1_1_negative_controls.json\n?? docs/reduction/pathways/phase_b1_1_protocol.md\n?? docs/reduction/pathways/phase_b1_1_regression.json\n?? docs/reduction/pathways/phase_b1_1_review.md\n?? docs/reduction/pathways/phase_b1_1_source_baseline.json\n?? docs/reduction/pathways/phase_b1_1_source_scope.json\n?? docs/reduction/pathways/phase_b1_1_validation_report.json\n?? docs/reduction/pathways/phase_b1_1_witnesses.json\n?? scripts/pathways/phase_b1_1/build_initiation_witnesses.py\n?? scripts/pathways/phase_b1_1/followup/build_followup.py\n?? scripts/pathways/phase_b1_1/followup/run_followup_validation.py\n?? scripts/pathways/phase_b1_1/followup/test_followup_negative_controls.py\n?? scripts/pathways/phase_b1_1/followup/verify_followup.py\n?? scripts/pathways/phase_b1_1/run_phase_b1_1_validation.py\n?? scripts/pathways/phase_b1_1/test_initiation_negative_controls.py\n?? scripts/pathways/phase_b1_1/verify_initiation_witnesses.py\n"
}
```

```json
{
  "execution_status": "COMPLETED",
  "engineering_status": "PASS",
  "suggested_review_status": "B1_1_CONDITIONALLY_ACCEPTED",
  "formal_signoff_status": "PENDING_FINAL_RESEARCHER_CONFIRMATION",
  "researcher_formally_signed": false,
  "phase_b1_1_formally_accepted": false,
  "commit_push_authorized": false,
  "phase_b1_2_authorized": false,
  "qssa_authorized": false,
  "kinetic_reduction_authorized": false
}
```

完成后停止，等待研究者正式确认。未 commit/push，未开始 B1-2、QSSA 或动力学降阶。
