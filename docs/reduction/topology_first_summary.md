# Topology first, QSSA second — PNAS 2017

**结果：已完成拓扑审计与候选推导，没有删除状态，没有改变标准模型；所有方案均为 HUMAN_REVIEW_REQUIRED。**

1. **哪些结构可先于 QSSA 处理？** 968 条有向反应中有 290 对精确反向通道，可先改写为保留全部状态的净通量表示。真正的状态合并仍需动力学闭合：完整源图检测到 0 条严格串联路径；固定作者参数后检测到 12 条。优先对延伸的三步段提出 E 聚合态，直接 A→B 只作为需验证的近似选项。
2. **哪些枢纽应显式保留？** ATP/GTP/ADP/GDP、PO4/PPi、aa-tRNA/tRNA、核糖体与跨模块共享翻译因子。完整图最高参与量示例：mRNA (237 reactions); RS30S (189 reactions); RS50S (165 reactions); GDP (127 reactions); GTP (127 reactions); fMettRNAfMetCAU (114 reactions); IF3 (101 reactions); IF1 (99 reactions)。高度数是共享竞争提示，不能作为删状态依据。26 个源子网络均按开放模块记录接口，不宣称彼此独立。
3. **第一原型是什么？** `re0000000016→17→18`（完整 ID 见案例）：S0→S1+PO4→S2+EFTu_GDP→S3；合计 S0→S3+PO4+EFTu_GDP。E_mid=S1+S2 保留内部核糖体占据总量，但单一 E 不能精确区分两阶段的因子占据与释放账本。完整图旁支全部列出；它们在固定作者参数中关闭。
4. **如何调整顺序？** 标准 SBML → 有角色的拓扑图 → 串联/分支/循环/枢纽/接口识别 → 候选聚合与占据/资源闭合 → 局部 QSSA → 分项验证。既有 QSSA、守恒与失败证据保留，暂停新的全局快变量搜索。参见 [QSSA repositioning](qssa_repositioning_note.md)。
5. **人下一步检查什么？** 审阅这条三步段的边界、关闭旁支的条件适用性、是否选择 E_mid 或显式链，以及 ATP/GTP、Gly/aa-tRNA、PO4/PPi、因子/核糖体占据和产物的观测合同。先决定哪些阶段库存/累计账本必须重构，再授权一个有限条件集的比较；本次未启动新的 ODE 验证。

**源文件与实际预期的差异：** 标准 SBML 所有初值/常数均为 1；作者 CSV 才给出 27 个初始存在组分、485 个零速率方向。默认图与作者图不可混称。真实模型只有 fMGG 的两次 Gly 加入，产物为 Pept0003，不能把示意长链或更长蛋白的行为当成已验证事实。

**相对独立性：** 按明示规则暂时屏蔽共享枢纽后，作者非零反应图形成 10 个非平凡连接区域。起始、延伸、终止仍属于一个 305 反应的连接区域；GlyRS/MetRS 各形成 42 反应的局部区域；能量再生 A–D 及 formylation 较局部化。共享资源恢复后仍相互耦合，这不是动态独立性的证明。具体成员和完整接口见 `context_components.csv`。

**尚未解决：** 拓扑不证明精确可聚合性；延伸整轮有返向循环；聚合态的阶段分布、延迟及微观 gross flux 不可由总量直接恢复；源文件单位及复合物原子/电荷信息不足；弱连接不证明弱动态耦合。旧 QSSA 的失败/未完成状态不会因为拓扑候选而升级。

## 组会图

“Repeated chain growth can sometimes be lumped into an effective step or an aggregate state.” 这里的 sometimes 由旁支、占据、资源账本、延迟及动力学闭合共同限定。

- [Figure 1 — module map](../../results/figures/topology_first_network_map.png)
- [Figure 2 — chain options](../../results/figures/topology_first_chain_schematic.png)
- [Figure 3 — workflow](../../results/figures/topology_first_workflow.png)
- [Figure 4 — real motif](../../results/figures/topology_first_case_study.png)
- [Figure 5 — real branch, return cycle and interfaces](../../results/figures/topology_first_branch_cycle_interfaces.png)

图的 SVG/PDF 与可重现脚本一并提供。运行分析、五个绘图脚本，再运行 `scripts/verify_pnas2017_topology.py`。验证针对源哈希、图表和代数一致性，**不是 reduced-model scientific validation**。
