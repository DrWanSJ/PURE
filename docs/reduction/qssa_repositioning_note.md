# QSSA 工作的重新定位：Topology first, QSSA second

记录日期：2026-10-08（Asia/Shanghai）。`HUMAN_REVIEW_REQUIRED = true`。
本次只整理已有证据并提出后续顺序；没有新全局快变量搜索、QSSA 求解、参数拟合、状态删除或 reduced-core 晋级。

## 1. 本轮来源边界

拓扑任务起点为 `775607bf9922c6878be0147bd7c64fa97e86a790`（`codex/r3-diagnostics-visualizations`）。该起点直接包含 R1、R2、R3 与 R3 诊断。R4–R8 位于其他本地研究分支/工作树，本轮只读查看；它们没有因为这份说明而成为起点分支已合并的结果。历史证书中的“open PR / unmerged”等文字属于当时记录，本轮不把它们当作已核实的当前远端状态。

R6 原工作树 `C:/Users/sean/.codex/worktrees/r6-ck-validation/GUV` 的 HEAD 为 `1181ab2f0a04d72cf76fb069be6bb842e3de75d8`，R6 新文件仍未提交。为避免把可变工作区当成稳定来源，下面的 R6 数值引用采用后来在 R7 系列中以 `9282853a24d716e3021ea85123e9ba1e0bb4c6fc` 保存的同一证据。本轮读取的 R7/R8 工作树是 `C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV`，实际 HEAD 为 `9ac0143b7ab6ed3b04de9d8a29a5e5732a761c7e`，分支已为 `codex/r8-ck-startup-layer-20261008`；R7 自身分支头为 `20ca5215d949c9451b3e6fd4435c18991783ac29`。这些是来源快照，不是新科学授权。

共同规范来源仍为 PNAS2017 原始 `models/pnas2017_full_reference/original/fMGG_synthesis.xml`，SHA-256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`。拓扑模型是 fMGG 三肽网络，释放产物 `Pept0003`；不能把它直接表述为已包含完整 GFP 多轮延长的模型。

## 2. 已有工作实际完成了什么

下表数值/状态为 `EXTRACTED`：从已有文件读取，未在本轮重跑动力学。用途列为 `INFERRED`，属于本次待人审建议。

| 工作 | 已有结论及边界 | 拓扑优先之后仍有用的部分 |
|---|---|---|
| R1 精确坐标 | 241 物种、968 有向反应、290 精确反向配对；源一般矩阵 rank 214、27 条守恒；241→214 是精确可重构表示。已登记作者条件数值检验通过。 | 守恒/库存、坐标和 968 有向账本作为任何新聚合的核对基础。精确冗余消除不等于拓扑链替换或 QSSA。 |
| R2 冻结作者条件 | 485 个作者 `k1=0` 的方向恒零，483 方向在此条件下活跃；活跃矩阵 rank 177，另有 37 条 `FROZEN_REFERENCE_ONLY` 关系。条件特异执行视图通过，规范反应未删除。 | 同时保留完整结构图和作者条件活跃图；对“弱分支”分别说明结构存在与冻结条件不活跃。不能把零速率方向/零初值物种永久删去。 |
| R3 21 个 GlyRS/MetRS 坐标的 QSSA | 193 慢坐标 +21 代数坐标的具体候选在九个完成条件均被耦合门槛拒绝。`R3_ADVERSE` 是未评分的数值非完成；原十条件协议仍为 `INCOMPLETE`。闭合残差小、精确库存漂移小均不保证轨迹/通量准确。 | 保留物理闭合、守恒载体/动态资源总量、隐式 Jacobian、初始层记录及失败数组。把它们用于检查某一重新定义的局部机制，而不是继续复用已失败候选作为有效模型。 |
| R4 拆分家族 + R5-C 修正 | 18 个家族/条件组合：状态与速率各 18 个 `RESOLVED_FAIL`，extent 16 fail/2 pass，balance 18 个 `NUMERICALLY_UNRESOLVED`。现时屏幕结论为 `BOTH_FAMILY_CANDIDATES_FAIL_REGISTERED_GATE_SCREEN`；组合失败原因仍 `UNDETERMINED`。 | 分家族失败证据能标出需重新检查的资源耦合/中间态；不能因未决 balance 抹去已决失败，也不能由 split screen 推导所有氨酰化 QSSA 不可能。 |
| R5 / R5-C CK 机制优先 | 从四个快结合/解离反应选 `S_f`，得到 rank-two 快子系统和动态慢总量；零阶物理平衡、快层吸引性、eta 家族有局部/描述性支持。原参数基线 hybrid/post-0.05 状态误差约 `3.38e-4`，不是晋级结论。 | 可复用“快反应→快子系统不变量→慢总量→奇异极限”的局部构造。全局最快三角/Schur/CSP 子空间仅作支持性诊断，不是局部模块 QSSA 的必要全局对齐定理。 |
| R6 CK Branch A | 九个流程完成；状态/重构与精确守恒支持，但 net current/extent 各九个 `RESOLVED_FAIL`；0/9 通过全部强制门槛。推荐 `CK_STATE_REDUCTION_SUPPORTED_BUT_FLUX_NOT_READY`。H 有 1 pass/4 fail/4 unresolved。 | 展示为何“蛋白/状态很好”还不足以满足资源消耗目标；保留 A–H 可观测契约、明确窗口、startup、净与 gross 账本分离。 |
| R7 一阶 CK | 只涵盖 BASE/ATP_LOW/TRNA_LOW；正式一阶与在零阶轨迹上的后处理分别记录。一阶改善 extent，但三条件 boundary-inclusive post-layer current 仍失败；推荐 `CK_FIRST_ORDER_IMPROVES_EXTENT_NOT_CURRENT`，不启动广泛验证。 | 高阶构造与量级核对是将来局部动力学检验的工具；不得把后处理叫做自洽一阶模型，也不得从状态通过推出 current 通过。 |
| R8 startup 归因 | 只读累计账本归因；`CK_STARTUP_LAYER_ATTRIBUTION_NOT_SUPPORTED`。原 R7 分数保持；没有新状态/extent ODE。建议先查持续 outer truncation/mechanism error 再考虑 matching。 | 将真实短暂 switch-current tail 与持续累计 extent 偏差分开。短暂初始误差可人审接受这一目标，不允许重写旧门槛或将后续偏差都归因于 startup。 |

R3 在 `t>0.05 s` 的诊断最大状态误差仍为 `0.0371711–0.141077`，高于当时 0.01 状态标准；速率和 extent 也仍超标。因此“容许第一个极短暂瞬态”不是已失败 R3 的现成修复。R6 的最大蛋白误差约 `3.02e-7`，但 CK net current 最大误差约 `0.9933`、net extent 约 `0.1274`。这些测量说明不同目标必须独立检查，不能只保留一条蛋白曲线。

## 3. 拓扑阶段与 QSSA 阶段各解决什么

**Topology first** 首先回答“哪个反应路径具有可替换的接口、库存和分支结构”。它可以给出候选，而不能单凭 degree、图上好看或零初值证明动态等价。

对内部串联链，应先检查每个中间态是否只有链内产生/消耗，是否还绑定 tRNA、核糖体或因子，以及所有旁路在完整结构图和作者活跃图中的状态。把链换成 `A→B` 需要可接受的驻留延迟/占据量损失和明示的有效 flux 假设；中间态有非可忽略的存量或会暂存资源时，应优先评估 `A→E→B`。保留一个总量 `E=ΣX_i` 并不自动封闭：若相同 E 对应的内部组成会给出不同出口通量、不同 ATP/GTP/aa-tRNA 消耗，必须增加组成/进度变量、给出受限近似，或保持显式链。

重复链增长可以有共同的反应模板，但同样模板并不保证相同出口速率。长短链的产物身份、进度分布和资源当量通常不同。提议保留 E 时，需说明 E 是“占据的延长态总量”、某个 chain-progress moment，还是某种含物料的池；它不能同时无条件代表所有这些量。

**QSSA second** 在已选定的结构接口内回答“哪些局部内部动力学能被近似重构”。具体顺序是选择快反应子集，推导快子系统不变量和动态慢总量，声明奇异缩放/参数域，再检查物理根、吸引性、移动流形 forcing、初始层和原参数误差。结合/解离的 rapid equilibrium 与催化周转的 QSSA 应分别命名。氨基酸、aa-tRNA、ATP/ADP/AMP、GTP/GDP、Pi/PPi 及共有因子/核糖体池的暂存和跨模块接口不能被一个速度标签抹去。

所有本次建议均为 `HUMAN_REVIEW_REQUIRED`；`DIRECT_LUMP_CANDIDATE`、`AGGREGATE_STATE_CANDIDATE`、`QSSA_CANDIDATE` 是候选种类，不是 `VALIDATED` 或状态删除命令。

## 4. 应保留、应后移的工作

| 工作项 | 本轮建议 | 理由/边界 |
|---|---|---|
| R1/R2 源语义、守恒和完整有向账本 | 保留 | 可验证新接口是否保留资源、反向 gross 通量、库存与条件边界。 |
| 本轮链/分支/循环/枢纽/子网络目录 | 先完成 | 给出候选结构和可检验的输入/输出接口，避免按速度选物种。 |
| 候选串联链的直接反应或 E 推导 | 先完成，再人审 | 至少明确净化学当量、驻留时间、链内库存、进度信息与旁路。 |
| 候选结构内的 binding/unbinding/catalytic cycles | `QSSA_AFTER_TOPOLOGY`，具体块待审 | 用现有局部奇异摄动工具；无新快反应块在此被批准。 |
| 全局 fast-species 排名/不断扩展物种子集搜索 | 后移 | 当前问题是接口和结构替换；速度信息以后作为局部动力学证据。 |
| 强行寻找全局固定 CSP 模态=固定化学物种块 | 后移 | 既有 moving-span 诊断未给出经化学/守恒验证的坐标映射。 |
| 已失败 21-state 图直接一阶修补，或广泛 CK follow-on | 后移 | 分别有已测失败与原注册停止边界；需独立的人审候选、契约与授权。 |
| ATP/GTP/tRNA/核糖体等共享池直接消去 | `KEEP_EXPLICIT` 接口建议 | 高连接度揭示耦合；聚合内部微态不应隐去共有库存和资源消耗。这是结构提案，不是新科学定案。 |

## 5. 新顺序与下一次人审

1. 由规范 SBML 导出带 stoichiometric role 的完整 bipartite 图，并并列记录作者条件活跃视图。
2. 识别真实串联链、分支/合流、循环、共享枢纽与有明示接口的功能模块；记录完整来源 ID。
3. 对一个真实链提出 `A→B`、`A→E→B`、保留显式链三种选项，核对反应求和后的资源当量和内部库存，不自动选胜者。
4. 人审接口、可观测量和损失：终产物/medium–long time、aa/aa-tRNA、ATP/GTP、小分子、占据量与延迟；确定哪些短时差异可接受及如何报告。冻结新候选自己的验证窗口/标准，不改写旧 R3–R8 结果。
5. 对人审保留的局部循环/内部块建立 QSSA 或 rapid-equilibrium 机制，推导慢总量和初始层。若 E 尚未封闭，先补足聚合结构，不借 QSSA 名字掩盖闭合假设。
6. 分别验证状态、动态资源、净 current/extent 与需要时的 gross 账本；完整初始层、post-layer 与 hybrid 结果分列。相对规范来源准确且满足新契约后，再进行独立科学评审。

下一次应首先审查本轮真实链案例的内部状态是否有侧支/共有因子占据、E 是否需要进度信息、以及出口/资源 flux 能否仅由保留接口确定。已有 CK 工作可作为“局部反应机制推导”的例子；已有 GlyRS/MetRS 工作则作为“闭合很小但耦合错误仍大”的反例。二者均保留，不把任一工作升级为对整个 PURE 的定理。

## 6. 可追溯来源索引

下列 SHA-256 为本轮从链接目标实际文件字节读取并核对的值。R1–R3 是起点分支文件；X4–X8 是其他本地研究工作树来源。派生说明不能替代原始数组、门槛和 native failed/incomplete 记录；本轮没有重新独立验证旧数字。外部路径可能在日后归档，本索引的提交与 hash 便于恢复同一来源。

S3 的 Desktop 原检出字节 hash 为 `97c58ab94e56332075356071e5582d583ae7f39a12294f47e75af524fd0c3369`（16,117 bytes）；本次输出工作树的 S3 为 16,374 bytes，下表列出其实际 hash。二者将 CRLF 规范为 LF 后文本完全相同，Git 均无该文件修改；这是检出换行差异，不将两个 raw hash 当作相同，也没有重写旧证书字节。

| ID | 路径 / 来源 | 本轮 SHA-256 |
|---|---|---|
| S1 | [R1 acceptance](r1_acceptance_v4r3.md)，起点 `775607b` | `9a7e250f9eb0c167a4a6bf6bcb76cc2a52a288a211c571ccd4def81beacf1d32` |
| S2 | [R2 frozen-domain certificate](r2_frozen_reference_domain_v1.md)，起点 `775607b` | `9658f8558a5c90abedeb317da6d3db42ff16ecf33957d389fd3a495951d1c46d` |
| S3 | [R3 bounded certificate](r3_aminoacylation_qssa_certificate.md)，起点 `775607b` 的本工作树检出字节 | `0ab43ba7d9625e39d251514bd3b278ee3e16297ba1e351a98a77c41e1aaac994` |
| S3a | [R3 raw aggregate](../../results/reduction/r3_aminoacylation_qssa/run_001/summary.json)，起点 `775607b` | `008296474c91bca70370f19ad07981f4ed899f2270f23b7154059077ee574c39` |
| X4 | [R5-C R4 gate reconstruction](C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV/results/reduction/r5c_corrigendum/r4_gate_summary.json)，来自 `1181ab2`，读取于 `9ac0143` | `58f9baaab93148d7836fa6d04fb340027078d3c884edac2ac04858d4dde0ecf1` |
| X4a | [R5-C interpretation corrigendum](C:/Users/sean/.codex/worktrees/r5c-corrigendum/GUV/docs/reduction/r5c_qssa_interpretation_corrigendum.md)，`1181ab2` | `a6b21ac3ed11c00c1f90843fc8a32c55704bb3cc18b946d1daad482a28893f6b` |
| X5 | [R5 mechanism summary](C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV/docs/reduction/r5_mechanism_first_summary.md)，来自 `6c11b58`，读取于 `9ac0143` | `9a5418671cf72bd79fad209cc88ffbdd139ca2b22232e152237cb883e0868fe6` |
| X5a | [R5-C fast ledger semantics](C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV/docs/reduction/r5c_fast_ledger_semantics_v1.md)，来自 `1181ab2`，读取于 `9ac0143` | `1f9f1238c4dfa7a606f32350ba9af69031569c69d52a7c2a96b79487ecff8d8f` |
| X6 | [R6 formal campaign aggregate](C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV/results/reduction/r6_ck_validation/formal_campaign_summary.json)，保存于 `9282853`，读取于 `9ac0143` | `74e856780502c91bf051ead8efb7b810bcab0dda345b539f37c2e45efe0b10e6` |
| X6a | [R6 formal summary](C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV/docs/reduction/r6_ck_formal_validation_summary.md)，保存于 `9282853`，读取于 `9ac0143` | `ddd5f47cf9a1b1f72070442a3578412cdaad70e468928cae21fa4fe833b551da` |
| X7 | [R7 advancement decision](C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV/results/reduction/r7_ck_first_order/advancement_decision.json)，R7 `20ca521`，读取于 `9ac0143` | `9863616c844df06e7591d152cfa9d40b586a745f1bc21185f0ed19854ecea399` |
| X7a | [R7 first-order summary](C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV/docs/reduction/r7_ck_first_order_summary.md)，R7 `20ca521`，读取于 `9ac0143` | `22f9e384be1e83f764d2ff1b33372fcdbe530fb8c07c5aede3683547c2f4c33b` |
| X8 | [R8 attribution decision](C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV/results/reduction/r8_ck_startup_layer/decision.json)，`9ac0143` | `d622c7b6172f2f1d83dd0f632b3666911e407e72a438066db53e231efd08051f` |
| X8a | [R8 attribution summary](C:/Users/sean/.codex/worktrees/r7-ck-first-order/GUV/docs/reduction/r8_ck_startup_layer_summary.md)，`9ac0143` | `ba58a3d7e5a7d7fc0544c6960d9aa5bb78ad6926704e90d5a0e85ac1d350e44b` |

目前 `PURE_reduced_core = NOT_VALIDATED`，968 项机理决策保持 `PENDING`。本次结构候选同样需 `HUMAN_REVIEW_REQUIRED`；工程复现、hash 一致和 verifier PASS 均不替代科学批准。
