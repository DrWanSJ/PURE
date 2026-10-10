# Phase B1-3 冻结结构重建协议

科学状态：PENDING_HUMAN_REVIEW。本协议在首次路径发现之前冻结；不修改搜索上限或验收规则以使结果通过。

授权：仅新增 docs/reduction/pathways/phase_b1_3_* 和 scripts/pathways/phase_b1_3/ 文件；不提交、推送、建分支/工作树、修改旧证据、做动力学模拟、QSSA 或降阶。缺失 PURE_two_computer_git_rules.txt 与 AGENTS.md 已记录，采用附件明确规则。

起点：7a95c29b6bf80b567863cc70a631859016144924，codex/energy-cycles-v1，原始工作树干净，远端同步。完整任务、源文件以及所有原先跟踪文件的 SHA-256 见 source_baseline。

## 源权威与范围

规范 combined SBML > 作者操作参数和初始 CSV > 五个 Termination 子系统 > 本地原论文/S27 > Level-C 注释 > 已签署 B1-2。重算241个物种、968个方向、3854条带系数的Petri弧、483正参数/485零参数；MathML常数必须按有理数读取。弧数为物种引用条目数，另报系数和，不能混淆。

全部968方向使用互斥主分类：未选中为 OUT_OF_B1_3_SCOPE；已选中且零参数为 AUTHOR_DISABLED_CONTEXT；其余依次 RECYCLE_SEARCH_SCOPE（Termination_C 或 RECYCLE_disassembly）、TERM_SEARCH_SCOPE（四个RF子系统或TERM三个context）、SOURCE_REVERSE_OR_COMPETITOR（核心的精确逆向）、SHARED_BOUNDARY_CONTEXT。非互斥标签保留全部子系统/上下文。

选择：五子系统与 TERM_factor_binding/TERM_peptide_release/TERM_energy_coupling/RECYCLE_disassembly 的并集，加核心源反应精确逆向及一次边界关联。边界种为核心所有 termRS/elRS/RS50S_/termRS30S 复合物、T_pre、RF1/RF2/RF3及各核苷酸形式、RRF、EFG及各形式；从所有968反应提取消费/生产这些种的方向，包含失活降解与共享接口。搜索允许全部正参数核心方向；边界方向可显式声明用于载体连接，默认不跨入重新起始/延长。所有逆向均保留，正参数逆向也参与发现。

## 有限供应、waypoint与搜索界限

T_pre仅为项目缩写，精确源种 elRS70SAUAA0004_Pept0003tRNAGlyGCC；作者称其为停码处elongation complex。RF1/RF2各从一个共同T_pre和一个相应RF有限token出发，先达RF结合态，再达一个free Pept0003且相应termRF态。直接解离另寻公共 termRS70SUAA0004_tRNAGlyGCC。

RF3代表路线：每个RF后释放态另加一个RF3_GDP和一个游离GTP，waypoints为RF_RF3_GDP结合态、无核苷酸RF_RF3态、RF_RF3_GTP态、RF释放后RF3_GTP态、RF3_GDP_PO4态、RF3_GDP态、公共无RF的term态。另寻预先有限RF3_GTP结合替代；以及游离RF3+GTP结合替代。供应只是条件性边界，不是作者浓度或内源再生证明。

回收从真实已执行的释放后marking出发，经直接RF解离（与RF3路线为替代）到共同term态，加一个RRF及一个新的EFG_GTP lot。waypoints为RRF结合态、RRF_EFG_GTP态、GDP_PO4态、GDP态、源50S复合物+termRS30S_mRNA拆分态、最终free RS30S/RS50S/mRNA/tRNAGlyGCC/RRF/EFG_GDP。另检查EFG-first结合和50S释放不同次序；不能把RRF结合称为拆分。

确定性广度优先有向Petri搜索；状态键含完整有理数marking、每个有限origin token、载体角色标签、完整事件来源/历史和已达waypoints。ID只作排序。每leg最多100000 visited states、24 events；每个B1-3 witness至多128 events。预算耗尽为SEARCH_INCONCLUSIVE；穷尽只说明本有限供应/允许方向下未找到，不能声称原模型不存在路线。循环/逆向不删除。

## 独立合同与冻结验收

逐事件检查m>=S_minus、m'=m+S；最终以完整241x968矩阵列和检查m_final-m_initial=S_full*w。所有库存均为源物种，整次发火，系数精确，无无限供应。

源状态token的来源DAG精确记录消费的producer和产生的source species。另建立有限角色身份投影：30S、50S、mRNA、终末Gly tRNA、肽载体、RF1/RF2/RF3、RRF、EFG及其核苷酸状态在复合物间持续；这是源状态身份合同，不是原子/完整分子组成证明。每个B1-3输入角色分配独立不可复制的label，转移到含该角色的确切输出；一个角色不得复制或被边界同类token替换。所有输入来源及输出标签、waypoint携带角色、最终库存要独立重算。RF3_GDP不是RF3+GDP；EFG_GTP的新lot不得冒充B1-2已经转成EFG_GDP的lot。

联合W_JOINT_RF1/RF2必须逐事件重放已签署W4的原始30事件，不重新发现上游；初始供应=签署初始库存+明确新lot。独立验证上游文件hash/签署限制、事件prefix、W4最终到B1-3的精确源种接口，并完整重算净向量。

A–M gates采用PASS/FAIL/INCONCLUSIVE/BLOCKED/NOT_RUN。Gate K至少24个有效负对照且至少5个Petri-enabled但lineage-invalid，必须实际拒绝且错误类别匹配。异常和搜索失败追加failure_evidence.jsonl，不删除失败。未能诚实构造5例则K不完整。判定逻辑先于控制执行编写，不因结果更改合同。

旧Phase A/B0/B1-1/followup/B1-2只读验证与负对照在temporary输出运行；不执行写历史输出的main。新build在两个不同临时目录重复，确定性文件逐字节相等。所有旧tracked raw SHA-256必须保持不变。继承MATLAB 99 passed /3 failed /1 incomplete仅记录未重跑未修复。

资源报告每一源种初值+新条件供应+事件净值=终值，包括free/bound GDP/GTP/PO4、ATP/ADP/AMP/PPi零条目、肽/tRNA/mRNA/载体占据；逐事件时点与Pept0003释放分开。W4五PO4（W3四）不能重复计入B1-3。水/质子及完整基团/元素守恒仍未证明。

最大状态 B1_3_ENGINEERING_COMPLETE_PENDING_HUMAN_REVIEW。H1–H9决定和签字始终留空，不自动提升科学接受。完整回收不解决时不可报完整工程通过。完整附件任务同时保留，并按其执行。
