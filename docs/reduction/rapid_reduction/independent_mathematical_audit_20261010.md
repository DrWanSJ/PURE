# B1-3 / Phase C 独立数学核查附注（2026-10-10）

**结论状态：INDEPENDENT_MATHEMATICAL_AUDIT_PASS_WITH_SCOPE_CONDITIONS；HUMAN_SIGNOFF_PENDING。**

本文件是独立核查建议，不是研究者科学签署；未在本地 sean 仓库改动文件、运行其未提交的 `runtime.py`、commit 或 push。

## 1. 附件识别与验证范围

两份同名 `mathematical_certificate.json` 中，本轮 Phase C 文件为 **113,107 bytes**、SHA-256 `c698ca685bf1052f529c9b8b2bb3626c2a3176818e868469cf9b29e6f3e26df0`；另一份为早期 CHAIN_01 局部四阶段证书，**46,649 bytes**、SHA-256 `7f5d1ddf6a2ada0aecb4e81ae099db90f77eb3783a738022b05ce9006651315c`。签署文件时应固定正确的 SHA-256。

独立交叉核查所用额外证据：GitHub `DrWanSJ/PURE`，`codex/energy-cycles-v1`，HEAD `7a95c29b6bf80b567863cc70a631859016144924`，`docs/reduction/reaction_level_annotation_v2.csv`。该文件是从标准 SBML 提取、经注释审核的反应数据；本次未直接下载并重新散列 canonical XML，也未读取 sean 尚未提交的 Phase C 仿真代码/轨迹。因此下面“独立源反应检验”明确指从现有 source-derived 反应注释重新解析和重建矩阵，并非从原始 XML 做完整的全新提取。

## 2. SOURCE_GENERAL：241 → 214

- 独立从 968 个有向反应的完整 reactants/products 化学计量生成 `S`，包含 `re0000000414` 的 `2 PO4`。
- 得到 241 种、968 方向、483 正参数和 485 零参数。
- 在模素数 `p=1000003` 上计算 `rank_p(S)=214`，给出有理秩下界 214。
- 独立构造 27 条线性独立的整数左零向量（整数系数最大绝对值 4），逐条对全部 968 个反应列验证 `L^T S=0`，给出有理秩上界 `241−27=214`。
- 因此在 source-derived 计量矩阵上，严格证明 `rank_Q(S)=214`、左零空间维数 27。

状态建议：`R1 EXACT_MATHEMATICS_VERIFIED_ON_REVIEWED_SOURCE_EXTRACTION`。若正式源级验收要求从原始 XML 完全独立解析，请让 sean 的独立校验器对相同 968 列做一次对照哈希和恒等式比对。

## 3. 作者支持面：241 → 175

- Phase C JSON 给出初始支持 27、闭包 46 轮新增 178 个互不重复物种（总支持 205），其余 36 物种零初值。
- 交叉解析全部 968 个反应后，36 个零物种共有 **459 个源生产反应关联**，其方向作者参数**全部为零**。这与 JSON 的 459 条 `zero_proof` 记录一致；不存在源注释中的正参数生产方向。
- 原作者正参数共有 483 方向；其中 `re0000000028` 与 `re0000000089` 虽为正参数，但其必要底物分别是支持面外的 `elRS70SAGGU0002_fMet_EFTu_GDP` 与 `elRS70SAGGU0003_Pept0002_EFTu_GDP`。因此实际支持面保留 481 个可能激活的反应方向。
- 在支持面 205 × 481 计量子矩阵上，模素数秩为 175；独立构造并用整数运算逐列验证 30 条线性独立的左零向量。
- 据此严格得到 `rank_Q(S_support)=175` 与 `205−30=175`，不是错误地按 `214−36` 计算。

**限定条件：** 全部 36 个物种初值确为零；固定作者零参数；不增加外源输入、SBML event/rule、额外速率修饰项或重新启用关闭方向。重新启用 `re0000000952` 时必须停止应用此支持面简化。证书报告无相关额外源规则，但本次未重新读取原始 XML/初值 CSV 字节。

状态建议：`R2 AUTHOR_CONDITION_EXACT`，条件性科研接受。

## 4. 回收尾部：七微观态 → 五聚合变量

从源注释独立确认正参数跨界入口 `re0000000910`（三配体复合物）与 `re0000000306`（EFG 单配体复合物），以及 **12 个 k=1000 的解离事件**：`re0000000308` 和 `re0000000913` 至 `re0000000923`。涉及这些七个复合物的其他已检索方向均为作者零参数，包括降解和逆向重新结合。

以 A=tRNAGlyGCC、B=RRF、C=EFG_GDP，七态为 ABC、AB、AC、BC、A、B、C，取

- `N3 = x_ABC`
- `N2 = x_AB + x_AC + x_BC`
- `B_A = x_ABC + x_AB + x_AC + x_A`
- `B_B = x_ABC + x_AB + x_BC + x_B`
- `B_C = x_ABC + x_AC + x_BC + x_C`

则独立构造投影 `P`、线性生成矩阵 `A_tail` 和五维闭合矩阵 `Q`，在有理数层面直接验证 `rank(P)=5`、`dim ker(P)=2`、`P A_tail = Q P`。对应方程：

`dN3/dt = u3 − 3k N3`

`dN2/dt = 3k N3 − 2k N2`

`dB_A/dt = u3 − k B_A`

`dB_B/dt = u3 − k B_B`

`dB_C/dt = u3 + u1 − k B_C`

其中 `u3` 为 `0910`，`u1` 为 `0306`；自由 RS50S 释放通量为

`J_RS50S = k (B_A + B_B + B_C − 3N3 − 2N2)`。

这是对当前作者参数、当前七态解离网络及受保护边际通量的精确动力学闭合，**不是七态微观分布或全部 gross event flux 的精确可逆重构**。

物理可行聚合域还需满足 `N3,N2 >= 0`、每个 `B_i >= N3`、`sum_i max(0,N3+N2−B_i) <= N2`；此时可重构一个非负微观代表。对 10,000 组随机非负微观库存的聚合与代表重构测试，未出现负值或边际失配；这只是额外算法测试，不替代源代码检查。

状态建议：`R3_RECYCLE EXACT_AUTHOR_PARAMETER_OBSERVABLE_QUOTIENT`。

## 5. 两轮 Gly 与 171 维组合

源模型两轮合并 `0017+0018`、`0078+0079`，`k_b=7000/1007`，保持平均驻留时间，但不保持等待时间方差。两组投影相同、产品导数分别 0 和 1000 的反例说明**不是精确聚合**；RF1/RF2 在相同合计占用下的产品导数可为 0.5 或 1.5，也不能精确合并。

171 维模型在四个冻结场景的长期精度属于所上传报告/决策表的数值结果，本次**未独立运行** `runtime.py` 或读取全部 `*.npz` 轨迹；不能把此数学核查写成全耦合数值二次复现。

应保留：初始层最高 10% 资源误差、不可行投影初值、作者关闭反应恢复时 R2/R3 失效、无法精确恢复某些 microscopic gross flux、尚无加速（中位相对速度 0.947×）、20 个额外积分计数器。

状态建议：`R3_CHAIN12_RECYCLE CONDITIONAL_FULL_COUPLED_CANDIDATE_GATES_PASS_AS_REPORTED`；不升级为全条件 `PURE_reduced_core`。

## 6. 建议人工科学决定（不是代签）

| 项目 | 建议 | 限定与后续核验 |
|---|---|---|
| B1-3 H1/H2/H3 | Y | 原始入口、竞争、自由 Pept0003 的源事件相符；原 witness 实际代码未独立重跑 |
| B1-3 H4–H9 | CONDITIONAL | RF3 与回收有限供应、正确源计量而非元素守恒、非主导路径、解释边界 |
| R1 214维 | Y（数学） | 保留 SOURCE_GENERAL 源提取对应关系 |
| R2 175维 | CONDITIONAL | 作者初值与固定零参数、205 支持面、不重新激活旁支 |
| R3 回收 173维 | CONDITIONAL | 仅受保护观测/边际流；微观不可唯一反演 |
| R3 Gly 174/173维 | CONDITIONAL | 近似；仅已验证动态条件和窗口 |
| R3 组合 171维 | CONDITIONAL | 四场景长期门 PASS 为原报告证据，须保留初始层、投影、无加速限制 |
| 全局模型及运行提速 | NOT_APPROVED | 不宣称全参数/全初值有效，不宣称已加速 |

**需要研究者明确回答：** 是否同意按照以上分类作正式“限定范围的科学接受”？研究者签名、正式 acceptance 记录和 Git commit/push 仍需单独授权。
