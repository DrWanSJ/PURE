# Phase C 正式科学接受及适用范围（2026-10-10）

研究里程碑：**PNAS2017_PHASE_C_REDUCTION_V1_20261010**。当前人工科学决定为 **PHASE_C_FORMALLY_ACCEPTED_WITH_SCOPE_CONDITIONS**；最终组合模型的原数值门结果为 **FULL_COUPLED_CANDIDATE_GATES_PASS**。两个状态分别表达人工决定和数值评估，不能互相替代。

## 人工授权与证据权威

接受来源是研究者 **2026-10-10 会话**，其[授权原文](human_decision_source_20261010.txt)引用：

> 我觉得没问题，正式接受，然后给我一个 sean codex prompt 把当前降维简化正式收束，还要更新之前的 html 方便展示。

该会话提供的任务说明逐项指定正式决定与排除项。本文件只登记该授权，没有手写签名、新增身份、精确批准时刻、外部签署 URL 或未披露的个人批准。此前 [review_and_decision](review_and_decision.md)、[reduction_report](reduction_report.md)、协议和独立审阅里的 `HUMAN_REVIEW_REQUIRED` / `HUMAN_SIGNOFF_PENDING` 保持为历史状态；本记录是较新的当前决定。

证据权威次序为 canonical SBML/author CSV、冻结数学证书与配置、实际运行及反例、限定的独立核查、研究者会话决定。人工接受改变当前科学决策，不改写源数据、阈值或原来失败的实验。

## 冻结模型层次与正式分类

| 模型 | 化学维数 | 加 20 计数器后的积分维数 | 正式研究决定 | 数学类型与条件 |
|---|---:|---:|---|---|
| R0 | 241 | 261 | 原始 canonical reference 保持 | 968 个原始有向反应，作为不变的完整参考。 |
| R1 | 214 | 234 | ACCEPTED | SOURCE_GENERAL exact conservation reduction；在每次初值对应的守恒流形上可精确恢复全源状态。 |
| R2 | 175 | 195 | ACCEPTED | 固定作者参数零模式及作者初值支持域内的 exact support reduction；不是一般参数域结论。 |
| R3_RECYCLE | 173 | 193 | CONDITIONALLY ACCEPTED | 作者条件下 7-to-5 exact protected-observable quotient；无唯一微观逆映射。 |
| R3_CHAIN1 | 174 | 194 | CONDITIONALLY ACCEPTED | 第一轮 Gly 的一处近似聚合；仅已审阅动态条件和窗口。 |
| R3_CHAIN12 | 173 | 193 | CONDITIONALLY ACCEPTED | 两轮 Gly 的两处近似聚合；不同于上面的 173 维 recycling 模型。 |
| R3_CHAIN12_RECYCLE | 171 | 191 | CONDITIONALLY ACCEPTED | 两轮 Gly 近似加 recycling 商系统；四个冻结场景、长期窗口、全耦合数值候选。 |

**171 是化学状态维数，不是反应数。** 源模型仍有 968 个 canonical directed reactions；作者参数中 483 个方向为正，其中 481 个方向在作者支持面上可能激活。最终 171 维实现计算 443 个有效 mass-action monomials，并保存源反应映射和同样的 20 个积分计数器。它是正式有条件接受的研究候选，不是一般有效的 `PURE_reduced_core`。

## 精确与近似的数学边界

R1 使用全部 968 列的有理化学计量矩阵：

\[
S\in\mathbb Q^{241\times968},\qquad \operatorname{rank}(S)=214,\qquad \dim\ker(S^{\mathsf T})=27.
\]

27 个独立左零关系逐列满足恒等式；模素数 1000003 的秩下界与守恒给出的秩上界一致。坐标图表 `x=x0+C(z-z0)` 可唯一恢复全源状态；改变初值时必须重算守恒常数，保留非负物理域检查。

R2 满足 `241=205+36`：作者初始支持 27 种，其闭包为 205 种；36 个被排除物种只在声明的作者条件下恒为零。支持矩阵为 205×481，`rank(S_support)=175`，30 个独立守恒给出 `205−30=175`，不能按 `214−36` 计算。全部 483 正参数列的全 241 行矩阵秩 177 不是支持面上的 175。更改作者关闭方向、引入额外输入或破坏初始支持面均不能继续无条件使用此证明。

Recycling 保留一个三配体态、三个双配体态、三个单配体态的五个独立观测：N3、N2、bound-tRNA、bound-RRF、bound-EFG。固定作者 12 条解离速率均为 1000，反向/降解零模式维持，并保留 `re0000000910` 三配体入口与 `re0000000306` 单 EFG 入口。在精确有理数上：

\[
P A_{\mathrm{tail}}=QP,\qquad\operatorname{rank}(P)=5,\qquad\dim\ker(P)=2.
\]

这是受保护观测与边际释放的精确投影。非负代表重构不等于恢复真实的七态分布；两维微观相关性及部分 individual gross extents（例如 0916/0917）不可唯一恢复。聚合物理域要求 N3,N2≥0、各 B_i≥N3，且 `sum_i max(0,N3+N2−B_i)≤N2`，不可删除此检查。

Gly 第一轮 `re0000000017 + re0000000018`、第二轮 `re0000000078 + re0000000079` 各减少一个内部自由度，固定：

\[
k_b=\left(\frac1{7}+\frac1{1000}\right)^{-1}=\frac{7000}{1007}.
\]

该近似匹配平均等待时间，不匹配完整等待时间分布。保留源 `0014/0016/0021`、`0075/0077/0082` 及竞争出口；聚合 Z=slow+fast 时从 free EFTu-GDP 投影中扣除被吸收的 fast 库存。相同投影下原肽形成导数可分别为 0 与 1000，已经构成非精确聚合反例。组合 171 维模型因此仍是近似模型。

## 四场景原始数值结果与冻结门

权威数值见 [validation_results.json](../../../results/reduction/rapid_v1/validation_results.json)、[window_errors.csv](../../../results/reduction/rapid_v1/window_errors.csv)、[全部原始轨迹目录](../../../results/reduction/rapid_v1/trajectories/) 与 [ribosome_errors.json](../../../results/reduction/rapid_v1/ribosome_errors.json)。本节是对冻结原结果的接受；新发布重跑的执行状态另见发布验证记录，不能将本节误读为该独立数学核查已重跑全部数值。

| 冻结场景 | 原模型 Pept@1000 | 171 维 Pept@1000 | 长期肽最大误差 | 长期资源/因子最大误差 | 净/gross 通量 RMS 最大误差 | 累计资源事件最大误差 |
|---|---:|---:|---:|---:|---:|---:|
| AUTHOR_BASELINE | 5.164491295 | 5.164491351 | 5.34709e-08% | 3.26209e-05% | 1.21008e-06% | 0.000422028% |
| FLOW_CHALLENGE | 8.689636693 | 8.689636800 | 8.03627e-08% | 6.63699e-05% | 1.47102e-06% | 0.000462741% |
| ENERGY_FACTOR_LIMITED | 7.208504242 | 7.208504352 | 1.87151e-07% | 0.000555620% | 9.90176e-06% | 0.00281105% |
| COMPETITION_OCCUPANCY | 5.138041496 | 5.138036876 | 5.89315e-05% | 0.0525020% | 0.00115311% | 0.0464469% |

四场景的最终模型原状态均为 `FULL_COUPLED_CANDIDATE_GATES_PASS`。跨四场景长期核糖体库存/占用最大归一化误差为 `0.0000236821537491494%`。以上是 **1–1000 长窗口、固定尺度归一化误差**，不是全时间、任意参数或任意初值下的通用误差。

AUTHOR_BASELINE 是预注册筛选场景；其余三项是预注册 HOLDOUT_VALIDATION。实际初值改动与零参数压力项完整固定在 [rapid_v1.json](../../../configs/reduction/rapid_v1.json)，不因接受而拟合或改变。主积分窗口 0–1000、269 个采样点，三个报告窗口为 `0–0.05`、`0.05–1`、`1–1000`，均为 **source numerical time unit，不标作秒**。计时表中的 s 才是计算耗时秒。

主算法 BDF `rtol=1e-9, atol=1e-11`；紧 BDF 为 `1e-11, 1e-13`；AUTHOR_BASELINE 与 ENERGY_FACTOR_LIMITED 另有同紧容差的 Radau 检验。数值参考收敛门为固定尺度误差 ≤1e-6；未收敛参考必须 INCONCLUSIVE。长期门为肽 ≤5%、资源/占用 ≤5%、通量 RMS ≤10%、累计转换 ≤2%、守恒绝对残差 ≤1e-8、库存下界 ≥−1e-9。四场景最终组合最大守恒残差 `1.01692e-11`，最小非负代表库存 `−6.93889e-18`。

归一化使用初值固定尺度：ATP/ADP/AMP 为 `max(1,initial ATP+ADP+AMP)`；GTP/GDP 为 `max(1,initial GTP+GDP)`；PO4 为 `max(1,initial ATP+GTP+PO4)`；PPi 为 `max(1,initial Gly+Met)`；肽为 `max(1,min(initial Gly/2,initial Met))`；翻译累计量为 `max(1,initial Gly+Met)`；因子为初始 role-pool 总量、下限 1e-3；核糖体为初始源 carrier 池。每项实际 `fixed_scales` 和 `counter_fixed_scales` 均存于 validation JSON；资源通量尺度为固定源浓度尺度 / 1 源时间单位，不使用最终产量或随时间累计量作分母。

20 个积分计数器的 NET 自由池变化、CONSUMED_ATP/GTP、RELEASED 事件及两个 RESIDUE 事件分开保留。gross CONSUMED 含可逆结合事件，不等于不可逆 ATP/GTP 水解量；不能把 gross 循环次数解释为能量耗散。候选 RHS 不使用参考轨迹作为隐藏输入。

## 计算成本：尚未加速

| 模型 | 三次重复中位耗时 / s | 相对速度 | 初始 / 末端 Jacobian 非零项 |
|---|---:|---:|---:|
| R0 241 | 0.5061 | 1.000× | 1207 / 1723 |
| R1 214 | 0.5663 | 0.894× | 1698 / 2225 |
| R2 175 | 0.5548 | 0.912× | 2089 / 7249 |
| R3_CHAIN12_RECYCLE 171 | 0.5344 | 0.947× | 2024 / 6986 |

各版本保留相同 20 计数器、采样任务与主精度，计时排除首次编译并取三次中位数。**No computational speedup yet。** 稀疏坐标重构引入更多 Jacobian 连接是受到观测矩阵结构支持的工程解释假设；这些计数不证明唯一的因果解释，也不构成已实现加速的证据。

## 独立数学核查的来源与限度

[独立数学核查原字节副本](independent_mathematical_audit_20261010.md)来自本次会话所指的桌面文件 `phase_c_independent_audit_20261010.md`，7209 bytes，SHA-256 `a5f61011bdd89b1bcbf4ba980a992f741127f58b6998dd3467cd3a4d2e49e73a`。原位置作为取得来源登记于 [current_decision_v1.json](current_decision_v1.json)，展示链接使用仓库内副本，便于另一台电脑复核。

该核查以 GitHub `DrWanSJ/PURE` 的 `codex/energy-cycles-v1`、HEAD `7a95c29b6bf80b567863cc70a631859016144924` 上的 source-derived `reaction_level_annotation_v2.csv` 及所提供数学证书为依据，独立重建矩阵、验证秩上下界、支持域、商恒等式与反例。它**没有重新下载/散列原始 canonical XML/初值 CSV，没有读取本地未提交 runtime.py 和全部 NPZ，也没有独立运行全耦合数值**。其“独立”不能扩大成完整 XML 二次提取或全数值二次复现。原文中的 HUMAN_SIGNOFF_PENDING 原字节保留；当前决定由本文件登记。

当前 Phase C 证书为 [mathematical_certificate.json](mathematical_certificate.json)，**113107 bytes**，SHA-256 `c698ca685bf1052f529c9b8b2bb3626c2a3176818e868469cf9b29e6f3e26df0`。另一个 [CHAIN_01 V2 局部证书](../../../results/reduction/chain01_v2/mathematical_certificate.json)为 **46649 bytes**，SHA-256 `7f5d1ddf6a2ada0aecb4e81ae099db90f77eb3783a738022b05ce9006651315c`。两者保留各自历史路径，不能替换或混同。

## 保留失败、限制与明确未批准项

- 非零 fast 初始占用可产生最高 10% 初始层资源误差；长期 PASS 不认证初始层精度。
- `CHAIN_INTERNAL_DOMAIN` 的 fast=1、freeTuGDP=0 投影产生 −1 的 freeTuGDP，两轮均 BLOCKED；并非所有投影初态物理可行。
- 作者关闭的 `re0000000952` 被重新激活时 R2/R3 BLOCKED；R1 的源一般守恒与 R2/R3 的作者域结论分开。
- Recycling 商系统不可唯一恢复微观态和各路径 gross extents；Gly 不是 exact kinetic lumpability。RF1/RF2 0.5 对 1.5 的反例继续 REJECTED。
- 历史 21-state QSSA 的九个完成但失败条件与一个 solver 未完成条件保留；不得把其他模型成功算作它通过。
- CK/NDK/MK/PPiase 全稳态候选的零产物无物理根、负自由形态及 fast-layer 限制保留；未批准无条件稳酶消元。
- 不批准 R2/R3 参数无关普适性、任意初值初始层准确性、所有投影初态可行性、173/171 维精确微观逆重构、一般蛋白序列有效性或实验验证的 PURE 表达。
- 不批准定量渗透压、离子强度、分子电荷声明、已实现计算加速，或将本里程碑改名为普适验证的 `PURE_reduced_core`。
- 历史评分 v1、早期证书/接口实现错误和真实求解失败留在原 [failure_evidence.jsonl](../../../results/reduction/rapid_v1/failure_evidence.jsonl) 与 `campaign_scoring_v1/`；旧阈值、参数与协议不重写。继承 MATLAB 99 passed / 3 failed / 1 incomplete 仍是历史证据。

完整源、配置、代码、证书、报告、误差和逐个 NPZ 的字节长度/SHA-256/保存位置见 [release_manifest_v1.json](release_manifest_v1.json)，原输出保持原位。统一入口及不覆盖原证据的复现说明见 [release_notes_v1.md](release_notes_v1.md)。后续仅建议稀疏坐标/Jacobian 工程优化、保留动态资源库存的能量循环候选，以及扩大已验证参数/初值域；本次收束不开始这些研究。


## 冻结关键证据 SHA-256

以下为本记录读取的原文件指纹；所有逐轨迹文件另由完整 manifest 枚举。

| 原路径（相对仓库根） | bytes | SHA-256 |
|---|---:|---|
| `models/pnas2017_full_reference/original/fMGG_synthesis.xml` | 1732620 | `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df` |
| `models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv` | 19566 | `cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465` |
| `docs/reduction/rapid_reduction/mathematical_certificate.json` | 113107 | `c698ca685bf1052f529c9b8b2bb3626c2a3176818e868469cf9b29e6f3e26df0` |
| `results/reduction/chain01_v2/mathematical_certificate.json` | 46649 | `7f5d1ddf6a2ada0aecb4e81ae099db90f77eb3783a738022b05ce9006651315c` |
| `configs/reduction/rapid_v1.json` | 42772 | `9076b2b3fcaa57b7b2c9fd2f8a92e5f37422ce47c9c633cd64fcaa6a2b187659` |
| `docs/reduction/rapid_reduction/protocol.md` | 5761 | `20015209ce29ced32b0f650771bcf03d252c2df456d8b69f99dd5a3f6daf6feb` |
| `docs/reduction/rapid_reduction/reduction_report.md` | 10341 | `3d38d3dc76b51dc26871f8406cb583c3a79afb918a54135bb2a1798061e14c5f` |
| `results/reduction/rapid_v1/validation_results.json` | 296372 | `d7874c666e2e024788fb26b64885453aed8e3a50773f4951aab0b13658785321` |
| `results/reduction/rapid_v1/window_errors.csv` | 17124 | `6b0e3f38b2f888aad3785e83e6255504fd561283fa89da51022646803522c242` |
| `results/reduction/rapid_v1/reduced_solver_crosschecks.json` | 46490 | `75ea7522e1ebdc2af481c1c41fe3d4e96ffdc3069105a8196369963fb397ba68` |
| `scripts/reduction/rapid_v1/runtime.py` | 16686 | `1fdceaa62538aa8fc9da36866da8cea26116c5762214864dd34c90f81411263c` |
| `scripts/reduction/rapid_v1/mathematics.py` | 13838 | `cdba04b5987ff4714ea1ff4a987f29037a2f4ee3c001308aa73727faa63d1730` |
| `scripts/reduction/rapid_v1/validate.py` | 11711 | `01182a85cfd274e0d1b3b5a02f1b1136b666037fc5ccd856d4f608332a94b051` |
| `scripts/reduction/rapid_v1/score_saved.py` | 4062 | `fbeee3f7feb7b84d32bd0e93b45125bd371368a41ce9f0eed5f4c4fa14e835d6` |
