# Phase C rapid_v1 冻结协议

科学状态：HUMAN_REVIEW_REQUIRED。本协议在首次ODE结果前冻结；原始SBML、作者CSV、B1-1/B1-2及26个B1-3文件全部保持原始字节。Git规则未在本地找到，按本次附件明确授权执行；不clone/worktree/branch、合并、清理、提交或推送。

## 源与精确层

规范241×968计量矩阵使用精确MathML系数；作者操作参数/初值覆盖占位值；数值时间为source numerical time unit，不解释成秒。现有R1 v4证书和27条SOURCE_GENERAL关系须独立验证L*S=0、逆矩阵和全部968列、初值与RHS。R0运行241维，R1运行214维。

作者固定参数的支持闭包使用全部底物、MathML动力学依赖和修饰物；检查没有规则、事件、外输入或参数切换。闭包外恒零证明按每条生产方向：要么k=0，要么至少一个必要依赖恒零。R2在可达支持上重算计量秩与守恒图表，绝不从214重复减掉36。所有改变的初值均重新计算守恒常数；参数零模式改变时R2不得沿用。

## 拓扑候选与checkpoint

至少筛查守恒/支持、两轮Gly elongation、RF1/RF2 termination、RRF/EF-G recycling、initiation、GlyRS/MetRS/formylation及CK/NDK/MK/PPiase。保留源物种/方向/共享接口/全部逆向和竞争、真实独立维数和闭合反例。

深入候选：

1. CHAIN_01 V2 Three-stage，第一轮合并源0017+0018，保留0014、0016与0021竞争；合并速率7000/1007，不拟合。删除一个快内部态。第二轮0078+0079作为独立后继checkpoint；若前继失败不得称累计成功。
2. 50S回收末端七个复合物的精确投影候选：三配体态量N3、两配体态总量N2、bound-tRNA/bound-RRF/bound-EFG三边际量。仅在固定作者释放速率均1000、反向/降解零模式下，检查P*f严格闭合。计入0306的跨子系统单EFG-bound输入和0910三配体输入。不得仅因相同末端而合并因子身份。非唯一源微观分布与唯一坐标重构要分开；若投影闭合成立，采用非负代表分布，不宣称恢复被丢弃的微观相关性。
3. RF1/RF2共同端点合并仅作为精确闭合反例筛查；保留不同源速率和入口，不重复21-state total-QSSA或四能量循环全稳态消元。

每个实现单独验证，再比较通过checkpoint的组合。未通过者保留源全模块和失败方程/数据。近似串联合并要求恒等源净列（源事件和）；资源释放时点误差分别评分。非零内部初值及零旁支重激活作为预注册压力测试；域失败不可删除。

## 固定数值策略

配置configs/reduction/rapid_v1.json在ODE前冻结，包含精确初值、参数修改（只在研究副本）、观察网格和下列固定策略。

主时间0–1000；网格含0、初始层0–0.05、过渡0.05–1、长期1–1000的固定对数点。筛选仅AUTHOR_BASELINE；FLOW_CHALLENGE、ENERGY_FACTOR_LIMITED、COMPETITION_OCCUPANCY为固定验证场景，不据结果调参数。TAIL_UNOBSERVABLE和CHAIN_INTERNAL_DOMAIN是数学/局部压力；ZERO_BRANCH_REACTIVATION为超作者固定零模式压力，不进入R2作者域。

主求解器BDF，rtol=1e-9、atol=1e-11，解析/结构Jacobian。收紧检查BDF rtol=1e-11、atol=1e-13；独立算法Radau在作者baseline和资源限制场景同紧容差检查。方法不能把源内部轨迹作为隐藏输入。所有失败记录solver status、实际t末端、异常及部分轨迹。

提前固定非负容差-1e-9；精确守恒最大绝对残差1e-8。R1/R2全部重构源物种及源反应投影必须在精确结构上成立；数值相对固定物理尺度误差<=1e-6。数值参考未收敛则比较INCONCLUSIVE，不算近似模型FAIL。

近似模型关键长期门：Pept0003轨迹/终点<=5%；重要资源与占用最大归一化误差<=5%；净形成/残基/资源通量归一化RMS<=10%；累计转换最大归一化误差<=2%；非负和守恒同上。初始和过渡窗口同样报告这些指标，但长期门不能被初始层结果替代。全部尺度是来自初值/源载体池的固定正量，不用最终产量/随时间累计量作分母。

J_protein、J_residue、J_resource分开，由原始反应映射重建。累计原始方向采用模型侧积分计数器，与化学状态维数分开。计数器至少包括源资源自由种净变化、GTP/ATP消耗、GDP/PO4/PPi释放、Pept0003净产量及两个肽键形成事件；若使用正负拆分，各方向仍可追溯，不用abs(net)替代gross。

所有模型性能用相同硬件、主精度与网格；报告RHS状态维数/计数器/有效通量表达式/原方向映射、Jacobian结构非零数、nfev/njev/nlu、实际wall time和加速比。对通过的最终模型重复至少3次，报告中位时间；不把重复后的较好一次单独作为速度结论。

## 独立审查和完成要求

B1-3从原始XML/CSV独立重算关键witness的S*w、逐步Petri、来源与资源；在新目录写H1–H9 AI建议，人工决定留空，不重复生成36控制和旧浏览器。源/旧证据hash每阶段核对。

数学证据包含完整support恒零证明、精确独立维数、affine/aggregate映射和不同full状态同P*x但P*f不同的反例。输出实际rhs_reduced、reconstruct_full、simulate_reference、simulate_reduced、compare_observables及原始轨迹、误差/成本表。拓扑近似失败时明确FAILED/BLOCKED；不能用R1/R2成功冒充。

最后提交中文不超过两页决策报告，H1–H9与每个实施候选均需研究者逐项决定，Git发布另行授权。只允许EXACT_REDUCTION_VERIFIED、CONDITIONAL_SUBSYSTEM_CANDIDATE、FULL_COUPLED_CANDIDATE_GATES_PASS、FAILED、BLOCKED和HUMAN_REVIEW_REQUIRED，不写正式PURE_reduced_core。
