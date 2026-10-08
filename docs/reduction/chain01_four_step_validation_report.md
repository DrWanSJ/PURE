# CHAIN_01 四步有效速率局部验证报告

最终状态：**LOCAL_CANDIDATE_FAILED_REGISTERED_SCREEN**。数值正确性：**PASS**；独立复核：**PASS**。
本报告是本轮预注册探索性筛选结果；不赋予人工科学批准。PURE_reduced_core 的已有状态与 R1–R8 结论保持原样。

## 1. 来源、模型及边界

工作树：`C:/Users/sean/.codex/worktrees/pnas-topology-first/GUV`；分支 `codex/pnas-topology-first`；HEAD `e05436bbfbe3aa40c6d4db45a931d14401f719ef`。日期：2026-10-08（Asia/Shanghai）。
来源规范 SBML，参数为 author CSV overlay；不得使用 SBML 的局部 k1=1 占位值。全部 968 行已有反应表被交叉核对。

| State | Source species ID | Chemical stage |
| --- | --- | --- |
| S0 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | EF-Tu-GTP bound; hydrolysis not completed |
| S1 | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` | GDP + Pi bound |
| S2 | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` | GDP bound; free Pi released |
| S3 | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | EF-Tu released |
| S4 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC` | peptide extended; ribosome still bound |

| Reaction | k from author CSV | Local kinetic law |
| --- | ---: | --- |
| re0000000014 | 260 | k14 × its single substrate |
| re0000000016 | 1000 | k16 × its single substrate |
| re0000000017 | 7 | k17 × its single substrate |
| re0000000018 | 1000 | k18 × its single substrate |

S1–S3 的所有结构旁支仍保留在 canonical SBML；作者固定参数下这些旁支 k=0。全部 reactant/product/modifier/kinetic incidences 与参数见 [source_incidence_audit.csv](../../results/reduction/chain01_four_step/source_incidence_audit.csv)。
S0 的 re13（k=140）被规定外部输入 u 替代；活跃竞争解离 re21（k=0.23）在局部实验中省略。S4 的 re19（k=30）和 re20（k=25）亦被隔离。这是边界干预，不是原作者完整网络中无条件串联的声明。
时间轴保留 source model time unit，不解释成秒；浓度/库存沿用模型数值尺度，不做源单位修正。原模型未提供足以证明元素/电荷闭合的元数据；本轮 mass balance 是精确反应计量与模型库存闭合。

## 2. 首次运行前固定的协议

冻结时间（UTC）：`2026-10-08T09:45:45.851502+00:00`；config SHA-256：`ebae5ef57a51d65e94e08029a421ee9b783f9801f8fa2bbcfa6066a8e61a8ba2`。
配置： [chain01_four_step_validation.json](../../configs/reduction/chain01_four_step_validation.json)；锁定记录：[protocol_freeze.json](../../results/reduction/chain01_four_step/protocol_freeze.json)。
程序从已审计的四个作者参数计算 τ=0.148703296703297，k_eff=6.724800472953，候选标签 MEAN_DWELL_MATCHED_CANDIDATE。没有拟合或调参。

| Test | Initial full x0…x4 | Input in tau units | Amount scale | Current scale | Domain |
| --- | --- | --- | ---: | ---: | --- |
| A | `[1, 0, 0, 0, 0]` | `[]` | 1 | 6.72480047 | IN_DOMAIN |
| B | `[0, 0, 0, 0, 0]` | `[{'start_tau': 0.0, 'end_tau': 10.0, 'amplitude': 1.0}]` | 0.148703297 | 1 | IN_DOMAIN |
| C | `[0, 0, 0, 0, 0]` | `[{'start_tau': 0.5, 'end_tau': 1.0, 'amplitude': 1.0}, {'start_tau': 3.0, 'end_tau': 3.5, 'amplitude': 1.0}]` | 0.148703297 | 1 | IN_DOMAIN |
| D | `[0, 0.25, 0.5, 0.25, 0]` | `[]` | 1 | 6.72480047 | OUT_OF_DOMAIN_NEGATIVE_CONTROL |

D 使用 y0=x0+x1+x2+x3=1、y4=x4=0 的重新开始等待映射；库存没有被删除，但剩余等待时间与原始化学组成不保留，属于预声明负对照。
采样固定为 6870 个点，0–10τ；初始及每个切换后加密。事件左右极限单独保存；状态、extent 和这些释放 current 连续，输入与入口导数可跳变。
窗口：ENTIRE=0–10τ；TRANSIENT 是 [0,0.25τ] 与每个输入切换后的 [event,event+0.25τ] 的并集（含端点）；POST_TRANSIENT 是其严格补集；LATE=[5τ,10τ] 是预声明补充窗口，不能替代全窗口筛选。0.25τ 是观察带，不意味着慢阶段已完成松弛。
预注册预算：product trajectory 和 resource extents 最大归一化误差≤0.01；product/resource currents 与未完成 occupancy≤0.05。量尺度为一批初始库存或一个 τ 的单位输入量，通量尺度为 cohort/τ 或单位输入率。1%/5% 是探索性分辨率预算，非既有科学批准标准。
numerical gate：库存/extent 账本残差≤1e-8、矩阵指数误差≤1e-8、收紧积分差≤5e-9、负值容许≤1e-12、mean dwell 相对误差≤1e-8。数值误差预算远小于动力学近似预算。
所有峰值指固定采样网格上的最大值；不声称是连续时间 supremum。相对误差仅在原参考值非零处定义，参考=0 处保留未定义值；很小的非零参考产生的大相对误差仍保留，但不拿它作 gate。RMS 按时间加权，各窗口连通段分别积分。

## 3. 数学与数值正确性

四列源计量以有理数逐物种相加，全部 241 个物种差值精确为零：S0 → S4 + PO4 + EFTu_GDP。该恒等式不证明瞬时动力学等价。
Full ODE 保存五状态和四个 ξ；direct 保存 y0,y4,ξ_eff。Σx=Σx(0)+∫u，Σy=Σy(0)+∫u。
一般账本：ξ14−ξ18=Δ(x1+x2+x3)，ξ16−ξ18=Δ(x2+x3)，ξ17−ξ18=Δx3。零内部初值时退化为无初始修正项的式子。
自由 Pi=ξ16；结合态 Pi=x1；x0 的 GTP γ-phosphate 与已水解结合态 Pi 分列。自由 EF-Tu-GDP=ξ17，结合態 GDP=x1+x2，结合態 GTP=x0。故 ξ16+x1−x1(0)=ξ14；ξ17+x1+x2−x1(0)−x2(0)=ξ14。这些不是完整共享池的净轨迹。
主积分 Radau(rtol=1e-10,atol=1e-12)，收紧 Radau(1e-12,1e-14)，每个输入事件分段；独立 augmented matrix exponential 与额外 source-reconstructed sparse expm_multiply 复核。没有负值裁剪或库存投影。实际完成状态、步数与残差记录于 verification_report.json / independent_verification.json。

| Test | Numerical status | Max primary-vs-expm state/extent error | Max invariant residual |
| --- | --- | ---: | ---: |
| A | PASS | 9.16144938e-12 | 2.33146835e-15 |
| B | PASS | 4.9571458e-12 | 1.22363057e-15 |
| C | PASS | 1.11512188e-12 | 4.62737487e-16 |
| D | PASS | 7.3331341e-12 | 2.33146835e-15 |

等待时间是四个独立指数阶段之和：E[T]=Σ1/k=τ；Var[T]=Σ1/k²。Direct E[T]=τ，Var[T]=τ²。
Full variance=0.0204249561647144，direct variance=0.0221126704504287；direct 增大 8.26300077%。数值存活积分加 10τ 后的解析剩余尾部，避免把截断均值误当无限时均值；完整 mean/variance 检查见 summary 的 dwell 字段。

## 4. 筛选结果与全部窗口

A/B/C 的 ENTIRE_WINDOW 所有强制类别必须同时 PASS；D 不进入域内筛选，失败按预期负对照解释。

| Test | Window | Product output | Resource current | Resource extent | Occupancy | Domain |
| --- | --- | --- | --- | --- | --- | --- |
| A | entire | FAIL | FAIL | FAIL | PASS | PASS |
| A | transient | FAIL | FAIL | FAIL | PASS | PASS |
| A | post_transient | FAIL | FAIL | FAIL | PASS | PASS |
| A | late | PASS | PASS | PASS | PASS | PASS |
| B | entire | FAIL | FAIL | FAIL | PASS | PASS |
| B | transient | PASS | FAIL | FAIL | PASS | PASS |
| B | post_transient | FAIL | FAIL | FAIL | PASS | PASS |
| B | late | PASS | PASS | FAIL | PASS | PASS |
| C | entire | FAIL | FAIL | FAIL | PASS | PASS |
| C | transient | FAIL | FAIL | FAIL | PASS | PASS |
| C | post_transient | FAIL | FAIL | FAIL | PASS | PASS |
| C | late | PASS | FAIL | FAIL | PASS | PASS |
| D | entire | FAIL | FAIL | FAIL | FAIL | FAIL |
| D | transient | FAIL | FAIL | FAIL | FAIL | FAIL |
| D | post_transient | FAIL | FAIL | FAIL | FAIL | FAIL |
| D | late | PASS | PASS | FAIL | PASS | FAIL |

| Test | Window | Metric | Max absolute error | Max normalized error |
| --- | --- | --- | ---: | ---: |
| A | entire | S4 trajectory | 0.033555664 | 0.033555664 |
| A | entire | S4 current | 6.72480047 | 1 |
| A | entire | Pi current | 155.322889 | 23.0970256 |
| A | entire | Pi extent | 0.87700577 | 0.87700577 |
| A | entire | EF-Tu-GDP current | 6.72480047 | 1 |
| A | entire | EF-Tu-GDP extent | 0.0274107935 | 0.0274107935 |
| A | entire | unfinished occupancy | 0.033555664 | 0.033555664 |
| A | entire | hidden S1-S3 inventory | 0.917425258 | 0.917425258 |
| A | transient | S4 trajectory | 0.033555664 | 0.033555664 |
| A | transient | S4 current | 6.72480047 | 1 |
| A | transient | Pi current | 155.322889 | 23.0970256 |
| A | transient | Pi extent | 0.87700577 | 0.87700577 |
| A | transient | EF-Tu-GDP current | 6.72480047 | 1 |
| A | transient | EF-Tu-GDP extent | 0.0274107935 | 0.0274107935 |
| A | transient | unfinished occupancy | 0.033555664 | 0.033555664 |
| A | transient | hidden S1-S3 inventory | 0.917425258 | 0.917425258 |
| A | post_transient | S4 trajectory | 0.0244634473 | 0.0244634473 |
| A | post_transient | S4 current | 0.384298572 | 0.0571464645 |
| A | post_transient | Pi current | 5.20397295 | 0.773847933 |
| A | post_transient | Pi extent | 0.776778405 | 0.776778405 |
| A | post_transient | EF-Tu-GDP current | 0.345230426 | 0.0513369025 |
| A | post_transient | EF-Tu-GDP extent | 0.0188549457 | 0.0188549457 |
| A | post_transient | unfinished occupancy | 0.0244634473 | 0.0244634473 |
| A | post_transient | hidden S1-S3 inventory | 0.801262082 | 0.801262082 |
| A | late | S4 trajectory | 0.00101501497 | 0.00101501497 |
| A | late | S4 current | 0.00525082497 | 0.000780814983 |
| A | late | Pi current | 0.0453113492 | 0.006737947 |
| A | late | Pi extent | 0.006737947 | 0.006737947 |
| A | late | EF-Tu-GDP current | 0.00553124863 | 0.000822514907 |
| A | late | EF-Tu-GDP extent | 0.00105507549 | 0.00105507549 |
| A | late | unfinished occupancy | 0.00101501497 | 0.00101501497 |
| A | late | hidden S1-S3 inventory | 0.00572293203 | 0.00572293203 |
| B | entire | S4 trajectory | 0.00212880855 | 0.0143158127 |
| B | entire | S4 current | 0.033555664 | 0.033555664 |
| B | entire | Pi current | 0.87700577 | 0.87700577 |
| B | entire | Pi extent | 0.143850392 | 0.967365182 |
| B | entire | EF-Tu-GDP current | 0.0274107935 | 0.0274107935 |
| B | entire | EF-Tu-GDP extent | 0.00152746295 | 0.0102718836 |
| B | entire | unfinished occupancy | 0.00212880855 | 0.0143158127 |
| B | entire | hidden S1-S3 inventory | 0.144852653 | 0.974105193 |
| B | transient | S4 trajectory | 0.00103731727 | 0.00697575167 |
| B | transient | S4 current | 0.033555664 | 0.033555664 |
| B | transient | Pi current | 0.87700577 | 0.87700577 |
| B | transient | Pi extent | 0.0280472286 | 0.188612016 |
| B | transient | EF-Tu-GDP current | 0.0274107935 | 0.0274107935 |
| B | transient | EF-Tu-GDP extent | 0.000840724639 | 0.00565370545 |
| B | transient | unfinished occupancy | 0.00103731727 | 0.00697575167 |
| B | transient | hidden S1-S3 inventory | 0.0300844601 | 0.202311992 |
| B | post_transient | S4 trajectory | 0.00212880855 | 0.0143158127 |
| B | post_transient | S4 current | 0.0244634473 | 0.0244634473 |
| B | post_transient | Pi current | 0.776778405 | 0.776778405 |
| B | post_transient | Pi extent | 0.143850392 | 0.967365182 |
| B | post_transient | EF-Tu-GDP current | 0.0188549457 | 0.0188549457 |
| B | post_transient | EF-Tu-GDP extent | 0.00152746295 | 0.0102718836 |
| B | post_transient | unfinished occupancy | 0.00212880855 | 0.0143158127 |
| B | post_transient | hidden S1-S3 inventory | 0.144852653 | 0.974105193 |
| B | late | S4 trajectory | 0.000184393217 | 0.00124000759 |
| B | late | S4 current | 0.001015015 | 0.001015015 |
| B | late | Pi current | 0.00673794702 | 0.00673794702 |
| B | late | Pi extent | 0.143850392 | 0.967365182 |
| B | late | EF-Tu-GDP current | 0.00105507552 | 0.00105507552 |
| B | late | EF-Tu-GDP extent | 0.000997706819 | 0.00670937929 |
| B | late | unfinished occupancy | 0.000184393217 | 0.00124000759 |
| B | late | hidden S1-S3 inventory | 0.144852653 | 0.974105193 |
| C | entire | S4 trajectory | 0.00172963173 | 0.0116314283 |
| C | entire | S4 current | 0.034198582 | 0.034198582 |
| C | entire | Pi current | 0.87700577 | 0.87700577 |
| C | entire | Pi extent | 0.0598165353 | 0.402254265 |
| C | entire | EF-Tu-GDP current | 0.0283862129 | 0.0283862129 |
| C | entire | EF-Tu-GDP extent | 0.00134230249 | 0.0090267164 |
| C | entire | unfinished occupancy | 0.00172963173 | 0.0116314283 |
| C | entire | hidden S1-S3 inventory | 0.0616937144 | 0.41487792 |
| C | transient | S4 trajectory | 0.00172963173 | 0.0116314283 |
| C | transient | S4 current | 0.034198582 | 0.034198582 |
| C | transient | Pi current | 0.87700577 | 0.87700577 |
| C | transient | Pi extent | 0.0598165353 | 0.402254265 |
| C | transient | EF-Tu-GDP current | 0.0283862129 | 0.0283862129 |
| C | transient | EF-Tu-GDP extent | 0.00134230249 | 0.0090267164 |
| C | transient | unfinished occupancy | 0.00172963173 | 0.0116314283 |
| C | transient | hidden S1-S3 inventory | 0.0616937144 | 0.41487792 |
| C | post_transient | S4 trajectory | 0.00171767181 | 0.0115510002 |
| C | post_transient | S4 current | 0.0252864157 | 0.0252864157 |
| C | post_transient | Pi current | 0.776778405 | 0.776778405 |
| C | post_transient | Pi extent | 0.0584668429 | 0.393177853 |
| C | post_transient | EF-Tu-GDP current | 0.019961728 | 0.019961728 |
| C | post_transient | EF-Tu-GDP extent | 0.00133699987 | 0.00899105737 |
| C | post_transient | unfinished occupancy | 0.00171767181 | 0.0115510002 |
| C | post_transient | hidden S1-S3 inventory | 0.0608583339 | 0.409260153 |
| C | late | S4 trajectory | 0.00051241883 | 0.00344591439 |
| C | late | S4 current | 0.00129318626 | 0.00129318626 |
| C | late | Pi current | 0.0950015193 | 0.0950015193 |
| C | late | Pi extent | 0.0141270391 | 0.0950015193 |
| C | late | EF-Tu-GDP current | 0.00153535696 | 0.00153535696 |
| C | late | EF-Tu-GDP extent | 0.000605906561 | 0.00407460073 |
| C | late | unfinished occupancy | 0.00051241883 | 0.00344591439 |
| C | late | hidden S1-S3 inventory | 0.0136164477 | 0.0915678938 |
| D | entire | S4 trajectory | 0.234348171 | 0.234348171 |
| D | entire | S4 current | 243.2752 | 36.1758242 |
| D | entire | Pi current | 243.2752 | 36.1758242 |
| D | entire | Pi extent | 0.7499546 | 0.7499546 |
| D | entire | EF-Tu-GDP current | 3.22480047 | 0.479538462 |
| D | entire | EF-Tu-GDP extent | 0.249977268 | 0.249977268 |
| D | entire | unfinished occupancy | 0.234348171 | 0.234348171 |
| D | entire | hidden S1-S3 inventory | 1 | 1 |
| D | transient | S4 trajectory | 0.234348171 | 0.234348171 |
| D | transient | S4 current | 243.2752 | 36.1758242 |
| D | transient | Pi current | 243.2752 | 36.1758242 |
| D | transient | Pi extent | 0.219255773 | 0.219255773 |
| D | transient | EF-Tu-GDP current | 3.22480047 | 0.479538462 |
| D | transient | EF-Tu-GDP extent | 0.0507130091 | 0.0507130091 |
| D | transient | unfinished occupancy | 0.234348171 | 0.234348171 |
| D | transient | hidden S1-S3 inventory | 1 | 1 |
| D | post_transient | S4 trajectory | 0.194773958 | 0.194773958 |
| D | post_transient | S4 current | 1.14962724 | 0.170953361 |
| D | post_transient | Pi current | 5.22420303 | 0.776856213 |
| D | post_transient | Pi extent | 0.7499546 | 0.7499546 |
| D | post_transient | EF-Tu-GDP current | 1.17814927 | 0.175194681 |
| D | post_transient | EF-Tu-GDP extent | 0.249977268 | 0.249977268 |
| D | post_transient | unfinished occupancy | 0.194773958 | 0.194773958 |
| D | post_transient | hidden S1-S3 inventory | 0.582082255 | 0.582082255 |
| D | late | S4 trajectory | 0.00258079817 | 0.00258079817 |
| D | late | S4 current | 0.0162113073 | 0.00241067485 |
| D | late | Pi current | 0.0453113492 | 0.006737947 |
| D | late | Pi extent | 0.7499546 | 0.7499546 |
| D | late | EF-Tu-GDP current | 0.0164150076 | 0.00244096575 |
| D | late | EF-Tu-GDP extent | 0.249977268 | 0.249977268 |
| D | late | unfinished occupancy | 0.00258079817 | 0.00258079817 |
| D | late | hidden S1-S3 inventory | 0.00415714883 | 0.00415714883 |

逐时 signed/absolute/normalized/relative 误差、峰值时刻和 RMS 都保留在 error_tables；本表不隐去失败窗口。hidden_inventory 是消失的显式微态库存，不等于 total occupancy 误差。

阈值敏感性只对动力学预算乘 0.5/1/2，不移动窗口或分母，numerical/domain 预算保持不变。

| Factor | Test | Entire product | Entire current | Entire extent | Entire occupancy |
| --- | --- | --- | --- | --- | --- |
| 0.5 | A | FAIL | FAIL | FAIL | FAIL |
| 1.0 | A | FAIL | FAIL | FAIL | PASS |
| 2.0 | A | FAIL | FAIL | FAIL | PASS |
| 0.5 | B | FAIL | FAIL | FAIL | PASS |
| 1.0 | B | FAIL | FAIL | FAIL | PASS |
| 2.0 | B | PASS | FAIL | FAIL | PASS |
| 0.5 | C | FAIL | FAIL | FAIL | PASS |
| 1.0 | C | FAIL | FAIL | FAIL | PASS |
| 2.0 | C | PASS | FAIL | FAIL | PASS |
| 0.5 | D | FAIL | FAIL | FAIL | FAIL |
| 1.0 | D | FAIL | FAIL | FAIL | FAIL |
| 2.0 | D | FAIL | FAIL | FAIL | FAIL |

## 5. Q1–Q8 科学判断

**Q1 净计量：** 精确相同，全部 241 个物种差为零；S0 的结合態 GTP 经四阶段产生自由 Pi 与 EF-Tu-GDP，不能将此精确净向量等同释放时序。
**Q2 平均等待：** 解析和尾部修正数值检查 `PASS`；τ=0.148703296703297，k_eff=6.724800472953。仅均值匹配，不是 exact Markov lumping。
**Q3 形成时间分布：** full H(s)=260×7×1000²/[(s+260)(s+7)(s+1000)²]，direct H(s)=k_eff/(s+k_eff)。full density 初始为 O(t³)、CDF 为 O(t⁴)，direct CDF 为 O(t)。A 在 t=0 full product current=0、direct=6.72480047295，是结构差异；A 全窗口 product trajectory 最大误差=0.033555664（归一化）。两个 k=1000 重复根应包含 t exp(-1000t)，不能套不同速率的奇异公式。
**Q4 资源释放：** A 的 Pi current 最大归一化误差=23.0970256，Pi extent=0.87700577；EF-Tu-GDP current=1，extent=0.0274107935。单步把二者都绑定到完成事件，Pi 的快速释放被明显延迟。D 的无限时增量 full Pi=.25、Tu-GDP=.75、product=1，direct 均为1；多释放 .75/.25 来自重启映射改变组成，非求解器错误。
**Q5 核糖体占据：** y0 把等待库存移到单一入口状态，未删除总 cohort。A 的 unfinished occupancy 最大归一化误差=0.033555664，显式 hidden S1-S3 最大库存=0.917425258。总 ribosome inventory 包含 S4，局部 S4 仍结合核糖体，守恒不等于核糖体释放。恒定输入的 unfinished inventory 两模型均趋 τ，但化学阶段、bound GDP/Pi 及真实 S0 占据无法由 y0 同时恢复。
**Q6 允许的近似：** 逐窗口支持由上述 gate 表限定。A 的预声明晚期窗口通过声明尺度的门槛，S4 最大误差=0.00101501497，可支持已输入 cohort 的接近完成量；不能把晚期吻合扩展到初始或任意输入。晚期 current 支持是按初始 cohort/τ 的绝对通量预算，不是尾部相对精度：A 晚期 product current 相对误差最大为 0.387885691，几乎消失的 Pi reference 可给出极大相对误差，原始记录完整保留。B 的两模型完成通量均趋1、产物渐近 t−τ、unfinished inventory 趋τ，但 Pi extent 的持续差趋 1/7+1/1000=0.143857142857，按 τ 归一化为0.967410582348，累计资源门槛持续失败。C 的切换记忆必须逐窗口审查，固定切换后0.25τ不保证慢瞬态消失。D不在适用域。任一窗口支持均只针对边界干预、作者固定参数和所声明可观测量。
**Q7 保留 S2/E_mid：** 有理由另行预注册候选。S2 是 Pi 已释放、EF-Tu-GDP 仍被结合的慢 k17 阶段，独立保存它有助区分 Pi 早期释放与较晚 Tu/产物事件。若 A=S0、D=S4，定义 E_mid=x1+x2+x3，可保留链内库存；该 aggregate 的 microscopic exit rates=(0,0,k18) 不相等，不满足强 Markov lumpability，组成决定通量。另一个总量 E_all=x0+x1+x2+x3 的 exit rates=(0,0,0,k18)；二者不能混用。四步中的 S2 与旧三步案例的同名 alias 并非同一位置。D 真正剩余均值=0.108392857143，direct restart τ 延长 37.1892029%，也说明组成信息的必要性。A→E_mid→D 值得作为下一阶段局部候选测试，必须定义每个状态的资源组成/释放事件并重新注册，本轮没有模拟它。
**Q8 Full-coupled：** 不建议把当前 direct candidate 作为通过候选进入完整 968 反应验证：本轮已测 resource/product 瞬态缺陷与边界 re21 竞争/共享池耦合尚未解决。先测试保留 Pi admission、慢 Tu-bound intermediate 和占据量的局部候选；其成功与新增人工授权之后再决定完整 coupled validation。本次没有启动完整网络实验，也不推断所有串联简化不可能。

## 6. 图与数据

- [01_product_trajectory](../../results/reduction/chain01_four_step/figures/01_product_trajectory.png)
- [02_product_flux](../../results/reduction/chain01_four_step/figures/02_product_flux.png)
- [03_pi_release_current](../../results/reduction/chain01_four_step/figures/03_pi_release_current.png)
- [04_pi_release_extent](../../results/reduction/chain01_four_step/figures/04_pi_release_extent.png)
- [05_eftu_gdp_current](../../results/reduction/chain01_four_step/figures/05_eftu_gdp_current.png)
- [06_eftu_gdp_extent](../../results/reduction/chain01_four_step/figures/06_eftu_gdp_extent.png)
- [07_internal_occupancy](../../results/reduction/chain01_four_step/figures/07_internal_occupancy.png)
- [08_normalized_errors](../../results/reduction/chain01_four_step/figures/08_normalized_errors.png)
- [09_pulse_and_switch_responses](../../results/reduction/chain01_four_step/figures/09_pulse_and_switch_responses.png)
- [10_model_comparison_summary](../../results/reduction/chain01_four_step/figures/10_model_comparison_summary.png)

图中 Full four-step reference 与 Direct effective candidate 显式标注；每个测试完整范围及初始放大并列。figure 09 检查双矩形输入切换；figure 10 汇总窗口而不只展示吻合区间。全部图对应原始 numerical_results/test_A…D.csv 与 error_tables。

## 7. 复现与文件保护

在本工作树中，用现有 Python（本次 D:/Code/Anaconda/python.exe；NumPy/SciPy/Matplotlib 版本见 runtime_manifest）顺序运行：

```text
python scripts/reduction/audit_chain01_sources.py --verify
python scripts/reduction/validate_chain01_four_step.py
python scripts/tests/test_chain01_four_step.py
python scripts/reduction/report_chain01_four_step.py
```

保留 config 与 protocol_freeze 原始字节；重跑沿用同一协议。新协议必须另存版本并单独冻结。运行尝试与首次失败记录若存在会保留，不混同 scientific approximation fail。
本工作树全部 1660 个原有 tracked 文件逐字节 SHA-256 前后核对 PASS，HEAD 未变；新增来源/结果不改写 canonical source、author parameters、历史证据、reduction_decisions.csv 或 PURE_reduced_core。没有 commit/push/merge、软件安装、参数拟合或全局 QSSA 搜索。
导航：knowledge_graph.json 标注 EXTRACTED/INFERRED 与源 hash、confidence、freshness；只是来源与结果索引，不替代原始证据。最终所有新增文件列于 workspace_changes.json、delivery_manifest.json。
