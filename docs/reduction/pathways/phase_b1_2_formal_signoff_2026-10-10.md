# PURE Reaction Atlas Phase B1-2 正式限定范围科学签署

正式科学状态：**B1_2_FORMALLY_ACCEPTED_LIMITED_SCOPE**。研究者于 **2026-10-10** 完成 H1-H7 科学审阅，并在本会话明确授权正式签署及普通 commit/push。此记录由 sean Codex 追加登记；验收范围仅为 **source-exact structural reconstruction**。

## H1-H7 正式研究者决定

| 项目 | 正式决定 | 接受范围及条件 |
|---|---|---|
| H1 E2 continuity | Y | 接受 0001→0013 的精确源状态连续；0001 在 W4 仅出现一次。E2 保持作者虚拟复合物的解释边界。 |
| H2 EF-Tu and two Gly deliveries | Y | 接受两次独立 EF-Tu/Gly-tRNA 递送、有限来源分配及载体连续性；两份复合递送供应和两份 EF-G_GTP 供应仍是条件输入，不认证作者初始条件下必然可用。 |
| H3 Two peptide formations | CONDITIONAL | 接受 0018/0079 对 fMet→Pept0002→Pept0003 的源模型状态表达；不认证完整真实肽基转移分子机理、虚拟状态完整化学组成或全局基团守恒。 |
| H4 EF-G and translocation | CONDITIONAL | 接受两轮 EF-G 结合、GDP_PO4 复合状态、PO4 释放、转位和 EFG_GDP 释放的源反应连续性；保留正参数逆向及竞争出口。不认证真实动力学优势、完整生理时间顺序或 QSSA。 |
| H5 Two-round material and energy ledger | Y | 接受 W3/W4 精确源物种净式；复合状态内的 GTP 不重复计为游离 GTP。GDP-form 释放不等于 GTP-form 恢复；不扩展为全局元素或核苷酸基团守恒证明。 |
| H6 T_pre and termination boundary | CONDITIONAL | 接受 0086 产生的源物种及 RF1/RF2 终止入口。T_pre 仅为项目内部 RF-free termination entry 简称。S27 对无 RF 状态使用 elongation complex，对 RF-bound 后续状态使用 pre-termination complex；不得混淆。 |
| H7 Alternative topology and limitations | Y | 接受已审计范围内竞争出口、正参数逆向、零参数方向和资源共享记录；不宣称全部路径已穷举、源 ID 排序表示动力学偏好或一个到达见证证明全模型覆盖。 |

4 项 Y，3 项 CONDITIONAL，0 项 N，0 项 PENDING。三个 CONDITIONAL 是正式科学适用范围限制，继续有效，未自动改成 Y。

## W1-W4 完整证据引用

所有完整方程、标记、有限 token 分配和依赖 DAG 见 [原始见证](phase_b1_2_witnesses.json)、[路径阅读视图](phase_b1_2_elongation_pathways.md) 与 [独立验证](phase_b1_2_independent_verification.json)。这些文件保留历史状态及原字节。

### W1 / 1 个事件

原始反应顺序：

```text
re0000000013
```

精确源物种净式（CONCEPTUAL_NET，源事件之和，不是新增有效反应或宏观速率律）：

```text
EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC
```

### W2 / 10 个事件

原始反应顺序：

```text
re0000000013 → re0000000014 → re0000000016 → re0000000017 → re0000000018 → re0000000019 → re0000000022 → re0000000024 → re0000000025 → re0000000068
```

精确源物种净式（CONCEPTUAL_NET，源事件之和，不是新增有效反应或宏观速率律）：

```text
EFG_GTP + EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> EFG_GDP + EFTu_GDP + 2 PO4 + elRS70SAGGU0003_Pept0002 + tRNAGlyGCC
```

### W3 / 19 个事件

原始反应顺序：

```text
re0000000013 → re0000000014 → re0000000016 → re0000000017 → re0000000018 → re0000000019 → re0000000022 → re0000000024 → re0000000025 → re0000000068 → re0000000074 → re0000000075 → re0000000077 → re0000000078 → re0000000079 → re0000000080 → re0000000083 → re0000000085 → re0000000086
```

精确源物种净式（CONCEPTUAL_NET，源事件之和，不是新增有效反应或宏观速率律）：

```text
2 EFG_GTP + 2 EFTu_GTP_GlytRNAGlyGCC + elRS70SAGGU0002_fMet -> 2 EFG_GDP + 2 EFTu_GDP + 4 PO4 + elRS70SAUAA0004_Pept0003tRNAGlyGCC + tRNAGlyGCC
```

### W4 / 30 个事件

原始反应顺序：

```text
re0000000459 → re0000000507 → re0000000513 → re0000000519 → re0000000529 → re0000000717 → re0000000722 → re0000000747 → re0000000757 → re0000000726 → re0000000001 → re0000000013 → re0000000014 → re0000000016 → re0000000017 → re0000000018 → re0000000019 → re0000000022 → re0000000024 → re0000000025 → re0000000068 → re0000000074 → re0000000075 → re0000000077 → re0000000078 → re0000000079 → re0000000080 → re0000000083 → re0000000085 → re0000000086
```

精确源物种净式（CONCEPTUAL_NET，源事件之和，不是新增有效反应或宏观速率律）：

```text
2 EFG_GTP + 2 EFTu_GTP_GlytRNAGlyGCC + IF2_GTP_fMettRNAfMetCAU + RS30S + RS50S + mRNA -> 2 EFG_GDP + 2 EFTu_GDP + IF2_GDP + 5 PO4 + elRS70SAUAA0004_Pept0003tRNAGlyGCC + tRNAGlyGCC + tRNAfMetCAU
```

## B1-1 与 B1-2 交接

W4 仅使用 [已签署的 B1-1 IF3-first E1 路径](phase_b1_1_followup_witness.json)，由 [B1-1 正式签署](phase_b1_1_formal_signoff_2026-10-09.json) 提供上游科学权威。随后原始 0001 执行一次，产生 E2 和 tRNAfMetCAU，再接 W3。未重新发现起始路径，未拼接互斥的起始释放历史。0001 继续为 ELONG_tRNA_release。

## W3/W4 资源账本

W3：两份独立 EFTu_GTP_GlytRNAGlyGCC、两份独立 EFG_GTP；净生成两份 EFTu_GDP、两份 EFG_GDP、四份 PO4 和一份游离 tRNAGlyGCC；第二份 tRNA 位于终点肽基源状态。W4 加入已接受起始过程和单次 0001，净生成五份 PO4、一份 IF2_GDP、一份 tRNAfMetCAU；IF1/IF3 恢复为游离源状态。

游离 ATP/ADP/AMP/GTP/GDP/PPi 在 W3/W4 中净变化为零。复合供应中的 GTP 不再计为额外游离 GTP；GDP-form 释放不等于 GTP-form 再生。有限复合供应是条件输入，不认证全模型真实可用性或全局基团守恒。

完整各源物种 initial/final/net 和事件成员见本次 [签署 JSON](phase_b1_2_formal_signoff_2026-10-10.json) 中 witnesses/resource_ledger，并与原始 witness 的精确 S*w 保持一致。

## 原始来源及未解决科学限制

原始 SBML 与作者参数优先于二级描述。241 species、968 directed reactions、3854 weighted arcs、483 正参数方向、485 零参数方向已独立重核。原论文和 S05-S11/S27 的限定证据见 [原始来源附录](phase_b1_2_original_source_evidence.md)。

T_pre 仅为项目内 RF-free termination entry 简称，对应原始 elRS70SAUAA0004_Pept0003tRNAGlyGCC。S27 称其为 elongation complex；RF1/RF2-bound 后续状态称为 pre-termination complex。这是正式 H6 限制，未把 T_pre 当作作者原始物种名，也未执行终止。

- 完整复合物及虚拟状态的分子组成和真实肽基转移化学未认证。
- 全网络元素和核苷酸基团守恒未认证。
- 作者参考参数下主导通量、路径概率和完整生理时序未认证。
- 时间尺度分离、QSSA、部分平衡和降阶精度未验证。
- 完整路径枚举和全模型可达性覆盖未证明。
- 独立完整 SI 文本/PDF 来源仍未建立；已检查的原论文和 S05-S11/S27 不能填补该缺口。
- RF1/RF2 后续释放、Termination 和回收尚未执行。
- 继承 MATLAB CI 99 passed / 3 failed / 1 incomplete 问题未修复或重跑，不算本轮 PASS。

## 新鲜工程发布核验

本次独立重跑 A-L 全部 PASS，W1-W4 为 1/10/19/30 个事件。B1-2 负控 30/30，其中 5 个 Petri-enabled 案例因 INVALID_LINEAGE 正确拒绝；B1-1 原 23 项与 Follow-up 12 项共 35/35。Phase A/B0、HTML 和实际浏览器回归通过，浏览器 222 项；两次全新确定性构建与原证据字节一致。

原运行器没有临时输出参数，直接 main 会重写冻结证据。本次复用其未经修改的回归、重建、保护函数，并对各 CLI 指定临时输出；未写任何原 19 个 B1-2 文件或原 2395 个 tracked 文件。所有真实命令、stdout/stderr、退出码、失败和未运行项保存在新增 [发布核验记录](phase_b1_2_formal_acceptance_publication_checks.json)。

## 历史状态、Git 发布授权与停止边界

原 review/protocol/witnesses/logs/失败证据的 PENDING_HUMAN_REVIEW、formally_accepted=false 和旧 commit/push hold 保持不变，作为历史记录。本次新签署是研究者明确授权的较新科学决定。

本次 Git 发布授权仅允许原 B1-2 的 19 个新增文件及本次 3 个新增文件，共 22 个新增文件；起始 HEAD 为 672ed34c27956f50c0913efc0b153937b250c2d0，分支 codex/energy-cycles-v1，origin https://github.com/DrWanSJ/PURE.git，起始 ahead/behind 为 0/0。不创建 clone/worktree/分支，不修改 main 或历史文件，不强推。

提交前必须逐项核对暂存白名单、原始 SHA-256、Git blob 字节及正常 whitespace 检查；任何未满足的提交前检查均阻止 commit/push。研究者未授权绕过格式失败。推送后的实际 commit SHA、远端 SHA、同步状态及工作树核验将由执行结果报告；本签署不是未经执行的发布成功声明。

```json
{
  "phase_b1_2_scientific_status": "B1_2_FORMALLY_ACCEPTED_LIMITED_SCOPE",
  "phase_b1_2_formally_accepted": true,
  "researcher_formally_signed": true,
  "commit_push_authorized": true,
  "phase_b1_3_authorized": false,
  "termination_authorized": false,
  "topology_reduction_authorized": false,
  "qssa_authorized": false,
  "kinetic_reduction_authorized": false,
  "full_phase_b_authorized": false
}
```

完成授权发布和远端核验后 STOP。如发布检查失败则停止并报告，不自动修复冻结证据。B1-3、Termination、拓扑降阶、QSSA、动力学降阶及 full Phase B 均未授权。
