# PNAS2017 Phase C Reduction V1 — 2026-10-10

**PNAS2017_PHASE_C_REDUCTION_V1_20261010** 是 Matsuura et al. PNAS 2017 fMet–Gly–Gly 模型的限定域研究里程碑。B1-3 源结构已正式接受；Phase C 的精确层和近似候选按不同适用范围接受。它没有将 `PURE_reduced_core` 升级为普适验证模型。

## 从这里开始

| 内容 | 发布入口 |
|---|---|
| 当前人工决定与模型分类 | [current_decision_v1.json](current_decision_v1.json) |
| 会话决定原文与研究者引语 | [human_decision_source_20261010.txt](human_decision_source_20261010.txt) |
| B1-3 H1–H9 与源物种资源账本 | [正式接受](../pathways/phase_b1_3_formal_acceptance_20261010.md) |
| Phase C 数学类型、四场景结果与全部限制 | [正式接受](phase_c_formal_acceptance_20261010.md) |
| 数学证书 | [Phase C certificate](mathematical_certificate.json) |
| 独立数学审核及其明确限度 | [原字节归档](independent_mathematical_audit_20261010.md) |
| 实际实现 | [runtime.py](../../../scripts/reduction/rapid_v1/runtime.py) |
| 冻结配置 | [rapid_v1.json](../../../configs/reduction/rapid_v1.json) |
| 原数值验证 | [validation_results.json](../../../results/reduction/rapid_v1/validation_results.json) |
| 逐文件分类、哈希、来源、重现与保存位置 | [release_manifest_v1.json](release_manifest_v1.json) |
| 统一验证 / 重现入口 | [release.py](../../../scripts/reduction/rapid_v1/release.py) |
| 原位升级的主要 HTML 展示入口 | [Phase C 总览与降维推理图谱](../../visualization/reduction_reasoning_atlas.html) |
| 既有辅助反应路径入口 | [Reaction Atlas](../pathways/reaction_atlas_prototype.html) |

历史协议、复核表与实验报告保留当时的 PENDING/HUMAN_REVIEW_REQUIRED 状态；当前决定由上述 dated acceptance 和机器记录表达。历史报告的结论不能通过静默改写来“清理”。

## 版本与维数

| 版本 | 化学维数 | 变换 | 当前人工决定 |
|---|---:|---|---|
| R0 | 241 | canonical source reference | 不变参考 |
| R1 | 214 | SOURCE_GENERAL 精确守恒坐标消元 | ACCEPTED |
| R2 | 175 | AUTHOR_CONDITION 精确支持面与守恒消元 | ACCEPTED，作者域限制 |
| R3_RECYCLE | 173 | recycling 7-to-5 精确受保护观测商 | CONDITIONALLY ACCEPTED，无唯一微观逆 |
| R3_CHAIN1 | 174 | 第一轮 Gly 近似聚合 | CONDITIONALLY ACCEPTED |
| R3_CHAIN12 | 173 | 两轮 Gly 近似聚合 | CONDITIONALLY ACCEPTED，区别于 recycling 173 |
| R3_CHAIN12_RECYCLE | 171 | 两轮 Gly 近似与 recycling 商组合 | CONDITIONALLY ACCEPTED，四场景长期全耦合候选 |

每个版本另有 20 个积分计数器；最终积分坐标数为 191。968 是原始反应方向数，483 是作者正参数方向数，481 是支持面上可能激活的方向数，443 是最终运行器的有效单项式数。**171 是化学状态维数，不是反应数。**

最终模型在 AUTHOR_BASELINE、FLOW_CHALLENGE、ENERGY_FACTOR_LIMITED、COMPETITION_OCCUPANCY 的原数值状态均为 `FULL_COUPLED_CANDIDATE_GATES_PASS`。长期源时间窗口 1–1000 的最大归一化误差：肽 `0.0000589315%`、资源/因子 `0.0525020%`、核糖体库存/占用 `0.0000236822%`、累计资源事件 `0.0464469%`。这不是任意时刻和初值的误差保证；原始 0–0.05 与 0.05–1 窗口数据继续保留，源时间不被标作秒。

## 不覆盖冻结证据的跨机验证与重现

在已获取本分支全部文件的现有仓库根目录运行，本次实际复现使用 Python 3.12.4；精确依赖版本见 [requirements-release.txt](../../../scripts/reduction/rapid_v1/requirements-release.txt)（numpy/scipy/sympy/numba/threadpoolctl）。执行记录应保留实际 Python/依赖版本、命令、stdout/stderr、退出码及失败信息；运行成功须以生成的验证结果为准。不要为获得相同耗时而修改求解容差或科学阈值。

```powershell
# 校验发布清单、源、数学与已保存科学证据；写入独立新目录
python -B scripts/reduction/rapid_v1/release.py verify --run-id my_verification_001 --require-manifest

# 重建数学对象并实际重跑冻结场景、比较误差，保留新轨迹与日志
python -B scripts/reduction/rapid_v1/release.py reproduce --run-id my_reproduction_001 --require-manifest
```

新输出确定地写入 `results/reduction/phase_c_release_v1/<run-id>/`。选择尚不存在的标签；运行器拒绝复用已经存在的 run-id，以避免覆盖科学证据。原 `results/reduction/rapid_v1/` 的所有轨迹和报告保持冻结。`verify` 对已保存产物的核验与 `reproduce` 的实际数值重跑是两种不同的证据；不得只执行前者就声称完成了新的全耦合数值复现。

B1-3 的独立发布核验入口将 canonical 矩阵、34 条见证和 36 个负控的检查结果写入新增运行目录：

```powershell
python -B scripts/reduction/rapid_v1/verify_b1_3_release.py --run-id my_b1_3_verification_001
```

原单项命令 `mathematics.py`、`audit_and_candidates.py`、`validate.py`、`score_saved.py`、`report.py` 保留在同一 `scripts/reduction/rapid_v1/`，没有复制另一套实现。它们的历史默认目标可能指向冻结目录；收束后的验证和重现应使用上述 wrapper，让它隔离输出。原运行时提供 `rhs_reduced`、`reconstruct_full`、`simulate_reference`、`simulate_reduced`、`compare_observables`；源轨迹不是候选 RHS 的输入。

## 本次实际执行的收束核验

- [新执行的完整数值复现](../../../results/reduction/phase_c_release_v1/closure_20261010/verification_report.json)：PASS。四个冻结场景的七模型共 28 个结果通过原门；45 次完整/交叉求解及 21 次性能求解已执行。49 个新 NPZ 与原始对应文件字节相同；没有通过修改参数、阈值或容差获得通过。
- [B1-3 独立复核](../../../results/reduction/phase_c_release_v1/b1_3_20261010/verification_report.json)：34 条见证、36/36 负控与完整源矩阵检查通过；11 个可由 Petri 启用但因果谱系不合法的反例仍被拒绝。
- [两套源解析结果的矩阵对照](../../../results/reduction/phase_c_release_v1/cross_parser_matrix.json)：241×968 矩阵按原始 ID 对齐后全部精确有理系数一致，包含 `re0000000414` 的 `2 PO4`。
- [HTML 自动核验](../../../results/reduction/phase_c_release_v1/dashboard/static_validation.json)和[浏览器记录](../../../results/reduction/phase_c_release_v1/dashboard/browser_validation.json)：静态数据、旧功能保护、链接与 36 组交互检查通过，桌面/窄屏截图归档。页面已加载后切断网络仍可切换真实数据；文件协议直接打开受本次浏览器工具策略限制，未冒称完成该检查。

以上都是本次新执行的核验，不替代原科学报告，也不重写其历史失败和待审状态。原 MATLAB 99 passed / 3 failed / 1 incomplete 未重跑。

发布打包过程中第一次清单校验在新版清单完成写入前启动，因旧哈希与已更新展示文件不符而正确失败。该[失败记录](../../../results/reduction/phase_c_release_v1/publication_verify_20261010/verification_report.json)保留原位；重新核验使用新的运行目录，不覆盖此记录。这是发布时序错误，不是数值求解失败。

随后[最终验证运行](../../../results/reduction/phase_c_release_v1/publication_verify_20261010_final/verification_report.json)完成并返回 PASS。该记录绑定运行开始时的清单；归档新增验证记录后的最新清单由 `python -B scripts/reduction/rapid_v1/package_release.py verify` 只读核验。[发布门记录](publication_gate_review_20261010.json)另行保留格式检查和 Git 发布前状态。

研究者在 2026-10-10 当前会话明确授权“允许三处 EOF 例外并继续发布”。例外仅限发布门记录列出的三个 B1-3 原始 Markdown 文件、行号和 SHA-256；保留原始末尾空行，不修改证据字节，不扩张科学接受范围。其余发布路径的格式检查仍须通过。

## 源和同名证书识别

| 对象 | SHA-256 |
|---|---|
| canonical SBML | `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df` |
| author parameter CSV | `cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465` |
| Phase C certificate，113107 bytes | `c698ca685bf1052f529c9b8b2bb3626c2a3176818e868469cf9b29e6f3e26df0` |
| CHAIN_01 V2 local certificate，46649 bytes | `7f5d1ddf6a2ada0aecb4e81ae099db90f77eb3783a738022b05ce9006651315c` |
| 独立数学核查，7209 bytes | `a5f61011bdd89b1bcbf4ba980a992f741127f58b6998dd3467cd3a4d2e49e73a` |
| 会话提供的接受任务原文 | `f713e35ee626b69aaaf0cce6ab291c6d9e629e78506cdcfa37ae41c46fad3cd4` |

两份 certificate 保持原路径。独立数学核查针对 source-derived 反应表重建矩阵，未重新解析 canonical XML，也未阅读/运行本地全部代码与 NPZ；此限制随原文保留。参数、初值、证书、运行代码、报告以及每份轨迹的具体 SHA-256 由完整 manifest 枚举，不能仅凭证书文件名识别版本。

## 原证据发布与保护

本里程碑的原始范围为 **26 个 B1-3 文件及 251 个 Phase C 文件**。发布清单逐个记录原路径、分类、bytes、SHA-256、来源、重现命令和保存位置。版本控制必需文件、可重建产物和原始科学数据的类别不同；分类本身不意味着允许删除或忽略数据。

本次发布策略将全部 277 个原文件保留原位并纳入 Git，包括原始 NPZ、初始失败、`campaign_scoring_v1/`、旧评分与报告，不依赖另一台电脑无法获取的 sean 本地专属归档。每个文件是否实际进入发布、原字节保护是否通过及远端是否可取，仍须以最终 Git/manifest 核验结果为准；本文不提前宣告 `RELEASE_CLOSED`。

## 必须随模型携带的限制

- 作者关闭反应的零模式、36 恒零物种初值与固定支持域；重新激活 `re0000000952` 时 R2/R3 必须 BLOCKED。
- 非零 fast 初值的初始层资源误差可达 10%；部分 projected initial states 不可行。
- Gly 匹配平均等待时间，不是精确 kinetic lumpability；recycling 商系统只保留规定观测，无法唯一恢复微观路径分布与全部 gross extents。
- RF1/RF2 不能精确合并；肽释放源速率分别为 0.5 和 1.5。历史 21-state QSSA 失败与能量循环物理根/快层限制继续保留。
- 尚未实现计算加速：R0 中位 0.5061 s，171 维 0.5344 s，相对速度 0.947×。末端 Jacobian 非零项为 1723 对 6986；稀疏重构 fill-in 是工程解释假设，不是唯一因果证明。
- 没有一般蛋白序列或实验验证的 PURE 表达结论，没有完整分子/元素/离子/电荷/渗透压认证。继承 MATLAB 99 passed / 3 failed / 1 incomplete 不变。

下一阶段建议按顺序研究稀疏坐标和 Jacobian 性能、保留动态储存的能量再生模块、扩大条件 171 维模型的参数及初值有效域。本次仅记录建议，不开始新的降阶、QSSA、拟合或状态消元。
