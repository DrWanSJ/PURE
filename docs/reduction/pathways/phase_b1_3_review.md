# Phase B1-3 研究者科学复核表

**B1_3_ENGINEERING_COMPLETE_PENDING_HUMAN_REVIEW**

所有H1–H9科学决定均为PENDING_HUMAN_REVIEW；Codex没有代签。工程PASS不等于科学接受、动力学验证或完整模型验证。

## 当前工程证据

| Gate | 状态 | 证据 |
|---|---|---|
| A | PASS | phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json |
| B | PASS | phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json |
| C | PASS | phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json |
| D | PASS | phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json |
| E | PASS | phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json |
| F | PASS | phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json |
| G | PASS | phase_b1_3_independent_verification.json; phase_b1_3_matrix_verification.json; phase_b1_3_source_matrices.json |
| H | PASS | phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json |
| I | PASS | phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json |
| J | PASS | phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json |
| K | PASS | phase_b1_3_negative_controls.json |
| L | PASS | phase_b1_3_regression.json; validation_report/determinism |
| M | PASS | validation_report/git_protection; source_baseline/protected_file_hashes |

主文件：完整事件方程见 [pathways](phase_b1_3_termination_recycling_pathways.md)，逐事件源种/来源token/DAG/账本见 [witnesses](phase_b1_3_witnesses.json)，独立验证见 [verification](phase_b1_3_independent_verification.json)，原始S27/工作簿定位见 [source evidence](phase_b1_3_original_source_evidence.md)，实际负对照见 [negative controls](phase_b1_3_negative_controls.json)。

有限供应不是作者操作浓度或内源再生。保留B1-2 H3/H4/H6条件：虚拟态完整组成、真实化学与生理时序、停码接口命名和全网络结论不获自动扩展。继承MATLAB 99/3/1未重跑或修复。

## H1 — RF-free T_pre 连续接口

科学状态：**PENDING_HUMAN_REVIEW**

W4之后准确源种是否与两支入口相同？保留B1-2 H3/H4/H6条件；项目缩写不是作者定义。

证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。

支持方程：

- `re0000000796` / k1=60 / Termination_A_RF1.xml:re210：`RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`。
- `re0000000811` / k1=23 / Termination_A_RF2.xml:re210：`RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`。

已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。

研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`

研究者备注（留空）：

______

## H2 — RF1/RF2竞争

科学状态：**PENDING_HUMAN_REVIEW**

一枚T_pre被一次结合消费后不能同时进入另一支；结合逆向允许重新选择，不等于同时产两肽。

证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。

支持方程：

- `re0000000796` / k1=60 / Termination_A_RF1.xml:re210：`RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`。
- `re0000000797` / k1=0.0028 / Termination_A_RF1.xml:re211：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC`。
- `re0000000811` / k1=23 / Termination_A_RF2.xml:re210：`RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`。
- `re0000000812` / k1=0.016 / Termination_A_RF2.xml:re211：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC`。

已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。

研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`

研究者备注（留空）：

______

## H3 — 游离肽产物及残留复合物

科学状态：**PENDING_HUMAN_REVIEW**

只有对应源事件产生free Pept0003；两支留下不同RF-bound term态，零参数肽释放逆向仍记录。

证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。

支持方程：

- `re0000000798` / k1=0.5 / Termination_A_RF1.xml:re212：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF1`。
- `re0000000813` / k1=1.5 / Termination_A_RF2.xml:re212：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF2`。
- `re0000000810` / k1=0 / Termination_A_RF1.xml:re228：`Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF1 -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`。
- `re0000000823` / k1=0 / Termination_A_RF2.xml:re228：`Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF2 -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`。

已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。

研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`

研究者备注（留空）：

______

## H4 — RF3参与与直接解离替代

科学状态：**PENDING_HUMAN_REVIEW**

分别审查RF3GDP交换、预供应RF3GTP、apoRF3路径。GDP/GTP结合态不可混同free核苷酸。

证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。

支持方程：

- `re0000000799` / k1=0.0028 / Termination_A_RF1.xml:re213：`termRS70SUAA0004_tRNAGlyGCC_RF1 -> RF1 + termRS70SUAA0004_tRNAGlyGCC`。
- `re0000000814` / k1=0.016 / Termination_A_RF2.xml:re213：`termRS70SUAA0004_tRNAGlyGCC_RF2 -> RF2 + termRS70SUAA0004_tRNAGlyGCC`。
- `re0000000829` / k1=30 / Termination_B_RF1.xml:re234：`RF3_GDP + termRS70SUAA0004_tRNAGlyGCC_RF1 -> termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP`。
- `re0000000843` / k1=10.5 / Termination_B_RF1.xml:re269：`termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP -> GDP + termRS70SUAA0004_tRNAGlyGCC_RF1_RF3`。
- `re0000000846` / k1=25 / Termination_B_RF1.xml:re272：`GTP + termRS70SUAA0004_tRNAGlyGCC_RF1_RF3 -> termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP`。
- `re0000000838` / k1=0.3 / Termination_B_RF1.xml:re264：`termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP -> RF1 + termRS70SUAA0004_tRNAGlyGCC_RF3_GTP`。
- `re0000000840` / k1=31 / Termination_B_RF1.xml:re266; Termination_B_RF2.xml:re266：`termRS70SUAA0004_tRNAGlyGCC_RF3_GTP -> termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4`。
- `re0000000842` / k1=5 / Termination_B_RF1.xml:re268; Termination_B_RF2.xml:re268：`termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4 -> PO4 + termRS70SUAA0004_tRNAGlyGCC_RF3_GDP`。
- `re0000000847` / k1=1000 / Termination_B_RF1.xml:re273; Termination_B_RF2.xml:re273：`termRS70SUAA0004_tRNAGlyGCC_RF3_GDP -> RF3_GDP + termRS70SUAA0004_tRNAGlyGCC`。
- `re0000000870` / k1=30 / Termination_B_RF2.xml:re234：`RF3_GDP + termRS70SUAA0004_tRNAGlyGCC_RF2 -> termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP`。
- `re0000000881` / k1=10.5 / Termination_B_RF2.xml:re269：`termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP -> GDP + termRS70SUAA0004_tRNAGlyGCC_RF2_RF3`。
- `re0000000884` / k1=25 / Termination_B_RF2.xml:re272：`GTP + termRS70SUAA0004_tRNAGlyGCC_RF2_RF3 -> termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP`。
- `re0000000879` / k1=0.77 / Termination_B_RF2.xml:re264：`termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP -> RF2 + termRS70SUAA0004_tRNAGlyGCC_RF3_GTP`。

已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。

研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`

研究者备注（留空）：

______

## H5 — RRF/EF-G回收

科学状态：**PENDING_HUMAN_REVIEW**

实际70S拆分是0910，先产两个occupied子单位；0911及50S释放多次序才恢复free组分。是否认可新EFG_GTP有限边界条件？

证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。

支持方程：

- `re0000000904` / k1=3.1 / Termination_C.xml:re302：`RRF + termRS70SUAA0004_tRNAGlyGCC -> termRS70SUAA0004_tRNAGlyGCC_RRF`。
- `re0000000906` / k1=31 / Termination_C.xml:re304：`EFG_GTP + termRS70SUAA0004_tRNAGlyGCC -> termRS70SUAA0004_tRNAGlyGCC_EFG_GTP`。
- `re0000000895` / k1=31 / Termination_C.xml:re236：`EFG_GTP + termRS70SUAA0004_tRNAGlyGCC_RRF -> termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP`。
- `re0000000900` / k1=0.6 / Termination_C.xml:re264：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP -> RRF + termRS70SUAA0004_tRNAGlyGCC_EFG_GTP`。
- `re0000000901` / k1=3.1 / Termination_C.xml:re265：`RRF + termRS70SUAA0004_tRNAGlyGCC_EFG_GTP -> termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP`。
- `re0000000908` / k1=31 / Termination_C.xml:re306：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP -> termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4`。
- `re0000000909` / k1=5 / Termination_C.xml:re307：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4 -> termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP`。
- `re0000000902` / k1=5 / Termination_C.xml:re268：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4 -> PO4 + termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP`。
- `re0000000910` / k1=1000 / Termination_C.xml:re308：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP -> RS50S_tRNAGlyGCC_RRF_EFG_GDP + termRS30S_mRNA`。
- `re0000000911` / k1=1000 / Termination_C.xml:re309：`termRS30S_mRNA -> RS30S + mRNA`。
- `re0000000913` / k1=1000 / Termination_C.xml:re311：`RS50S_tRNAGlyGCC_RRF_EFG_GDP -> EFG_GDP + RS50S_tRNAGlyGCC_RRF`。
- `re0000000914` / k1=1000 / Termination_C.xml:re312：`RS50S_tRNAGlyGCC_RRF_EFG_GDP -> RRF + RS50S_tRNAGlyGCC_EFG_GDP`。
- `re0000000915` / k1=1000 / Termination_C.xml:re313：`RS50S_tRNAGlyGCC_RRF_EFG_GDP -> RS50S_RRF_EFG_GDP + tRNAGlyGCC`。
- `re0000000916` / k1=1000 / Termination_C.xml:re314：`RS50S_tRNAGlyGCC_RRF -> RS50S_RRF + tRNAGlyGCC`。
- `re0000000917` / k1=1000 / Termination_C.xml:re315：`RS50S_tRNAGlyGCC_RRF -> RRF + RS50S_tRNAGlyGCC`。
- `re0000000918` / k1=1000 / Termination_C.xml:re316：`RS50S_RRF -> RRF + RS50S`。
- `re0000000919` / k1=1000 / Termination_C.xml:re317：`RS50S_tRNAGlyGCC -> RS50S + tRNAGlyGCC`。
- `re0000000920` / k1=1000 / Termination_C.xml:re318：`RS50S_tRNAGlyGCC_EFG_GDP -> EFG_GDP + RS50S_tRNAGlyGCC`。
- `re0000000921` / k1=1000 / Termination_C.xml:re319：`RS50S_tRNAGlyGCC_EFG_GDP -> RS50S_EFG_GDP + tRNAGlyGCC`。
- `re0000000922` / k1=1000 / Termination_C.xml:re320：`RS50S_RRF_EFG_GDP -> EFG_GDP + RS50S_RRF`。
- `re0000000923` / k1=1000 / Termination_C.xml:re321：`RS50S_RRF_EFG_GDP -> RRF + RS50S_EFG_GDP`。
- `re0000000308` / k1=1000 / Elongation_B.xml:re67; Termination_C.xml:re322：`RS50S_EFG_GDP -> EFG_GDP + RS50S`。

已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。

研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`

研究者备注（留空）：

______

## H6 — 源物种资源账本

科学状态：**PENDING_HUMAN_REVIEW**

直接回收新增一个PO4；RF3交换另消耗freeGTP并产生freeGDP和一个PO4。joint直接/交换PO4为6/7，W4五个只计一次。完整元素/基团守恒未认证。

证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。

支持方程：

- `re0000000798` / k1=0.5 / Termination_A_RF1.xml:re212：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF1`。
- `re0000000813` / k1=1.5 / Termination_A_RF2.xml:re212：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF2`。
- `re0000000843` / k1=10.5 / Termination_B_RF1.xml:re269：`termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP -> GDP + termRS70SUAA0004_tRNAGlyGCC_RF1_RF3`。
- `re0000000846` / k1=25 / Termination_B_RF1.xml:re272：`GTP + termRS70SUAA0004_tRNAGlyGCC_RF1_RF3 -> termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP`。
- `re0000000840` / k1=31 / Termination_B_RF1.xml:re266; Termination_B_RF2.xml:re266：`termRS70SUAA0004_tRNAGlyGCC_RF3_GTP -> termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4`。
- `re0000000842` / k1=5 / Termination_B_RF1.xml:re268; Termination_B_RF2.xml:re268：`termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4 -> PO4 + termRS70SUAA0004_tRNAGlyGCC_RF3_GDP`。
- `re0000000908` / k1=31 / Termination_C.xml:re306：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP -> termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4`。
- `re0000000902` / k1=5 / Termination_C.xml:re268：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4 -> PO4 + termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP`。
- `re0000000911` / k1=1000 / Termination_C.xml:re309：`termRS30S_mRNA -> RS30S + mRNA`。
- `re0000000913` / k1=1000 / Termination_C.xml:re311：`RS50S_tRNAGlyGCC_RRF_EFG_GDP -> EFG_GDP + RS50S_tRNAGlyGCC_RRF`。
- `re0000000916` / k1=1000 / Termination_C.xml:re314：`RS50S_tRNAGlyGCC_RRF -> RS50S_RRF + tRNAGlyGCC`。
- `re0000000918` / k1=1000 / Termination_C.xml:re316：`RS50S_RRF -> RRF + RS50S`。

已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。

研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`

研究者备注（留空）：

______

## H7 — 逆向、竞争与失活上下文

科学状态：**PENDING_HUMAN_REVIEW**

正参数反向与重新结合在允许集内；零参数和降解结构保留。代表性最短结构证据不能排名生理用量或通量。

证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。

支持方程：

- `re0000000797` / k1=0.0028 / Termination_A_RF1.xml:re211：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC`。
- `re0000000800` / k1=60 / Termination_A_RF1.xml:re214：`RF1 + termRS70SUAA0004_tRNAGlyGCC -> termRS70SUAA0004_tRNAGlyGCC_RF1`。
- `re0000000812` / k1=0.016 / Termination_A_RF2.xml:re211：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC`。
- `re0000000815` / k1=23 / Termination_A_RF2.xml:re214：`RF2 + termRS70SUAA0004_tRNAGlyGCC -> termRS70SUAA0004_tRNAGlyGCC_RF2`。
- `re0000000830` / k1=25 / Termination_B_RF1.xml:re235：`termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP -> RF3_GDP + termRS70SUAA0004_tRNAGlyGCC_RF1`。
- `re0000000832` / k1=25 / Termination_B_RF1.xml:re237：`termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP -> RF3_GTP + termRS70SUAA0004_tRNAGlyGCC_RF1`。
- `re0000000834` / k1=25 / Termination_B_RF1.xml:re243：`termRS70SUAA0004_tRNAGlyGCC_RF1_RF3 -> RF3 + termRS70SUAA0004_tRNAGlyGCC_RF1`。
- `re0000000839` / k1=60 / Termination_B_RF1.xml:re265：`RF1 + termRS70SUAA0004_tRNAGlyGCC_RF3_GTP -> termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP`。
- `re0000000841` / k1=5 / Termination_B_RF1.xml:re267; Termination_B_RF2.xml:re267：`termRS70SUAA0004_tRNAGlyGCC_RF3_GDP_PO4 -> termRS70SUAA0004_tRNAGlyGCC_RF3_GTP`。
- `re0000000844` / k1=5.82 / Termination_B_RF1.xml:re270：`GDP + termRS70SUAA0004_tRNAGlyGCC_RF1_RF3 -> termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GDP`。
- `re0000000845` / k1=10 / Termination_B_RF1.xml:re271：`termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP -> GTP + termRS70SUAA0004_tRNAGlyGCC_RF1_RF3`。
- `re0000000871` / k1=25 / Termination_B_RF2.xml:re235：`termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP -> RF3_GDP + termRS70SUAA0004_tRNAGlyGCC_RF2`。
- `re0000000873` / k1=25 / Termination_B_RF2.xml:re237：`termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP -> RF3_GTP + termRS70SUAA0004_tRNAGlyGCC_RF2`。
- `re0000000875` / k1=25 / Termination_B_RF2.xml:re243：`termRS70SUAA0004_tRNAGlyGCC_RF2_RF3 -> RF3 + termRS70SUAA0004_tRNAGlyGCC_RF2`。
- `re0000000880` / k1=23 / Termination_B_RF2.xml:re265：`RF2 + termRS70SUAA0004_tRNAGlyGCC_RF3_GTP -> termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP`。
- `re0000000882` / k1=5.82 / Termination_B_RF2.xml:re270：`GDP + termRS70SUAA0004_tRNAGlyGCC_RF2_RF3 -> termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GDP`。
- `re0000000883` / k1=10 / Termination_B_RF2.xml:re271：`termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP -> GTP + termRS70SUAA0004_tRNAGlyGCC_RF2_RF3`。
- `re0000000896` / k1=2.4 / Termination_C.xml:re237：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP -> EFG_GTP + termRS70SUAA0004_tRNAGlyGCC_RRF`。
- `re0000000905` / k1=0.6 / Termination_C.xml:re303：`termRS70SUAA0004_tRNAGlyGCC_RRF -> RRF + termRS70SUAA0004_tRNAGlyGCC`。
- `re0000000907` / k1=2.4 / Termination_C.xml:re305：`termRS70SUAA0004_tRNAGlyGCC_EFG_GTP -> EFG_GTP + termRS70SUAA0004_tRNAGlyGCC`。
- `re0000000909` / k1=5 / Termination_C.xml:re307：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4 -> termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP`。
- `re0000000810` / k1=0 / Termination_A_RF1.xml:re228：`Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF1 -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`。
- `re0000000823` / k1=0 / Termination_A_RF2.xml:re228：`Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF2 -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`。
- `re0000000957` / k1=0 / Termination_C.xml:re364：`RS50S_tRNAGlyGCC_RRF_EFG_GDP + termRS30S_mRNA -> termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP`。

已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。

研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`

研究者备注（留空）：

______

## H8 — 源结构与解释范围

科学状态：**PENDING_HUMAN_REVIEW**

S12–S16、S27作者定义与原始模型结构为EXTRACTED；载体身份投影和生理解释INFERRED；完整SI文本/物理组成证书未建立。

证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。

支持方程：

- `re0000000796` / k1=60 / Termination_A_RF1.xml:re210：`RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`。
- `re0000000798` / k1=0.5 / Termination_A_RF1.xml:re212：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1 -> Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF1`。
- `re0000000811` / k1=23 / Termination_A_RF2.xml:re210：`RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`。
- `re0000000813` / k1=1.5 / Termination_A_RF2.xml:re212：`elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2 -> Pept0003 + termRS70SUAA0004_tRNAGlyGCC_RF2`。
- `re0000000910` / k1=1000 / Termination_C.xml:re308：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP -> RS50S_tRNAGlyGCC_RRF_EFG_GDP + termRS30S_mRNA`。
- `re0000000911` / k1=1000 / Termination_C.xml:re309：`termRS30S_mRNA -> RS30S + mRNA`。

已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。

研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`

研究者备注（留空）：

______

## H9 — 未来拓扑降阶的问题

科学状态：**PENDING_HUMAN_REVIEW**

重复RF支与50S释放子路径可提出聚合问题；共享T_pre竞争、RF3核苷酸状态、释放/拆分时点、有限EFG/RRF载体约束会妨碍聚合。本轮不选择或实现降阶。

证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。

支持方程：

- `re0000000796` / k1=60 / Termination_A_RF1.xml:re210：`RF1 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1`。
- `re0000000811` / k1=23 / Termination_A_RF2.xml:re210：`RF2 + elRS70SAUAA0004_Pept0003tRNAGlyGCC -> elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2`。
- `re0000000799` / k1=0.0028 / Termination_A_RF1.xml:re213：`termRS70SUAA0004_tRNAGlyGCC_RF1 -> RF1 + termRS70SUAA0004_tRNAGlyGCC`。
- `re0000000814` / k1=0.016 / Termination_A_RF2.xml:re213：`termRS70SUAA0004_tRNAGlyGCC_RF2 -> RF2 + termRS70SUAA0004_tRNAGlyGCC`。
- `re0000000838` / k1=0.3 / Termination_B_RF1.xml:re264：`termRS70SUAA0004_tRNAGlyGCC_RF1_RF3_GTP -> RF1 + termRS70SUAA0004_tRNAGlyGCC_RF3_GTP`。
- `re0000000879` / k1=0.77 / Termination_B_RF2.xml:re264：`termRS70SUAA0004_tRNAGlyGCC_RF2_RF3_GTP -> RF2 + termRS70SUAA0004_tRNAGlyGCC_RF3_GTP`。
- `re0000000904` / k1=3.1 / Termination_C.xml:re302：`RRF + termRS70SUAA0004_tRNAGlyGCC -> termRS70SUAA0004_tRNAGlyGCC_RRF`。
- `re0000000906` / k1=31 / Termination_C.xml:re304：`EFG_GTP + termRS70SUAA0004_tRNAGlyGCC -> termRS70SUAA0004_tRNAGlyGCC_EFG_GTP`。
- `re0000000908` / k1=31 / Termination_C.xml:re306：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GTP -> termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4`。
- `re0000000902` / k1=5 / Termination_C.xml:re268：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP_PO4 -> PO4 + termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP`。
- `re0000000910` / k1=1000 / Termination_C.xml:re308：`termRS70SUAA0004_tRNAGlyGCC_RRF_EFG_GDP -> RS50S_tRNAGlyGCC_RRF_EFG_GDP + termRS30S_mRNA`。
- `re0000000913` / k1=1000 / Termination_C.xml:re311：`RS50S_tRNAGlyGCC_RRF_EFG_GDP -> EFG_GDP + RS50S_tRNAGlyGCC_RRF`。
- `re0000000914` / k1=1000 / Termination_C.xml:re312：`RS50S_tRNAGlyGCC_RRF_EFG_GDP -> RRF + RS50S_tRNAGlyGCC_EFG_GDP`。
- `re0000000915` / k1=1000 / Termination_C.xml:re313：`RS50S_tRNAGlyGCC_RRF_EFG_GDP -> RS50S_RRF_EFG_GDP + tRNAGlyGCC`。

已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。

研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`

研究者备注（留空）：

______

## 停止点

请研究者亲自填写H1–H9；本轮不提交或推送，不修改旧正式接受记录。本文件不是签署。

