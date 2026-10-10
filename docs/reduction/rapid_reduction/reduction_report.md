# Phase C 实际降阶与验证报告

**HUMAN_REVIEW_REQUIRED**。所有结果是本地研究证据；B1-3未获正式H1–H9签署。没有提交、推送、改源文件或命名为正式PURE_reduced_core。

## 已取得的运行结果

完整源模型、精确图表和逐步拓扑候选均实际积分到源时间1000。严格、可唯一恢复完整源状态的最大减少为作者条件下241→175（66个，27.39%）；不依赖作者零模式的SOURCE_GENERAL为241→214（27个，11.20%）。回收173维是对受保护观测的精确商系统，丢失两维微观相关性；不能把它计作全源状态可逆消元。两轮Gly近似与回收商系统组合为171维（70个，29.05%），在四个冻结场景通过长期耦合门。

| 模型 | 独立化学维 | 计数器 | 有效单项式/映射源方向 | 初始/末端Jac nnz | nfev | 中位时间s / 相对速度 | 长期肽/资源最大误差 | 状态 |
|---|---:|---:|---|---|---:|---|---|---|
| R0 | 241 | 20 | 454/483 | 1207/1723 | 5081 | 0.5061 / 1.000× | 参考 | REFERENCE_CONVERGED |
| R1 | 214 | 20 | 454/483 | 1698/2225 | 4917 | 0.5663 / 0.894× | 2.27184e-09% / 5.06333e-07% | EXACT_REDUCTION_VERIFIED |
| R2 | 175 | 20 | 452/481 | 2089/7249 | 4318 | 0.5548 / 0.912× | 1.77063e-09% / 5.66794e-07% | EXACT_REDUCTION_VERIFIED |
| R3_CHAIN1 | 174 | 20 | 451/481 | 2080/7190 | 4326 | 0.5469 / 0.925× | 5.91257e-05% / 0.0518163% | FULL_COUPLED_CANDIDATE_GATES_PASS |
| R3_CHAIN12 | 173 | 20 | 450/481 | 2071/7131 | 4328 | 0.5428 / 0.932× | 5.89315e-05% / 0.052502% | FULL_COUPLED_CANDIDATE_GATES_PASS |
| R3_RECYCLE | 173 | 20 | 445/481 | 2042/7104 | 4334 | 0.5388 / 0.939× | 1.58661e-09% / 5.17103e-07% | EXACT_REDUCTION_VERIFIED |
| R3_CHAIN12_RECYCLE | 171 | 20 | 443/481 | 2024/6986 | 4330 | 0.5344 / 0.947× | 5.89315e-05% / 0.052502% | FULL_COUPLED_CANDIDATE_GATES_PASS |

维数收益不是加速保证。固定守恒图表把共享资源重构为多个坐标的线性组合，增加Jacobian连接；本实现171维相对完整241维为0.947×，未实现加速。计时排除初次编译，所有模型保留20个相同积分计数器，包含相同dense-output任务，三次重复取中位；不删除较慢测量。

## 源与数学对象

规范SBML SHA-256：dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df。作者参数CSV：cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465。241种、968方向、3854条Petri边，权重之和3855（0414产生2PO4）；483正参数/485零参数，290精确反向对。全部规则、事件、初始赋值、函数定义与修饰物输入经源读器检查。未添加化学参与物、拟合参数或外部源轨迹驱动。

R1：精确有理矩阵S与27个独立L满足L*S=0；模素数1000003给rank下界214，上界由L给214。v4证书逐列重验，x=x0+C(z-z0)。对每个初值重新取守恒常数，物理域x≥-1e-9。

R2：作者初值27种有正支持；保守闭包205种。36种的每条源生产方向均因k=0或必需底物恒零而不产生产物。两条正参数方向也缺少支持，481方向在支持面上可能有流。全241行正参数矩阵rank177；205×481支持矩阵rank175，由30个独立限制后的守恒关系与独立模秩相互证实。205−30=175；不是214−36。所有压力初值仍在同一支持面。

R3 Gly：第一轮0017+0018，第二轮0078+0079，各使用固定kb=7000/1007。保留0014/0016/0021以及0075/0077/0082，其他完整网络保持。聚合Z=slow+fast；自由EFTu_GDP投影扣除被吸收fast量，以保证同一载体账本。源事件和仅改变时序，不改变净化学。两次原方向采用同一kb*Z，所以有效列为其源列之和；所有原ID仍映射。

该聚合不是精确闭合：slow=1/freeTuGDP=0与fast=1/freeTuGDP=1同P*x，却有肽键形成导数0与1000。等待均值1007/7000相同，但源方差1/49+1e-6不同于单指数(1007/7000)^2。不会将平均时间一致升级为全分布一致。

R3回收：七态分别为三配体、三种双配体、三种单配体。投影保留N3、N2与bound-tRNA/RRF/EFG三个边际量。12条释放方向均k=1000；外部0306单EFG输入和0910三配体输入保留。符号恒等式P*S_tail*D=Q*P_tail，对全耦合其余速率不存在尾态依赖；资源/因子计数器也逐行通过同样的闭合证明。

回收尾部方程（k=1000，u3=0910，u1=0306）：N3'=u3−3kN3；N2'=3kN3−2kN2；B_tRNA'=u3−kB_tRNA；B_RRF'=u3−kB_RRF；B_EFG'=u3+u1−kB_EFG。自由50S释放为k*(B_tRNA+B_RRF+B_EFG−3N3−2N2)，各自由配体释放为k*对应边际量。外部源列按原方程同步更新。

reconstruct_full为尾态返回非负代表：三种pair下界为max(0,N3+N2−另一边际)，剩余N2均匀分配，single由边际扣除。可行性检验不能删去；同aggregate不同microstate的明确反例已保存，个别0916/0917等gross路径通量不可唯一恢复。保护的free资源、因子占用与总释放可恢复，但非所有968个微观gross extents。

## 实际数值与受保护观测

主BDF1e-9/1e-11、紧BDF1e-11/1e-13。AUTHOR_BASELINE及ENERGY_FACTOR_LIMITED另用独立Radau紧容差；所有参考的固定尺度收敛误差≤1e-6。主采样269点，分0–0.05、0.05–1、1–1000；额外保存全部求解器接受步的物理与代表源库存检查。

观测包括Pept0003、ATP/ADP/AMP/GTP/GDP/PO4/PPi/CP、游离30S/50S/70S、自由RF1/2/3及RF3-GDP/GTP、EF-Tu/EF-G GDP/GTP形态、RRF、两类tRNA和aa-tRNA、八类因子/tRNA占用及30S/50S占用。J_protein净自由肽通量、两个J_residue原肽键事件与自由资源net/gross currents独立。20个模型侧积分计数器由原源反应矩阵建立，未使用完整源轨迹当候选输入。

| 冻结场景 | Source Pept@1000 | 171维Pept@1000 | 长期肽误差 | 长期资源误差 | 净/gross flux RMS | 累计流量误差 |
|---|---:|---:|---:|---:|---:|---:|
| AUTHOR_BASELINE | 5.164491295 | 5.164491351 | 5.34709e-08% | 3.26209e-05% | 1.21008e-06% | 0.000422028% |
| FLOW_CHALLENGE | 8.689636693 | 8.6896368 | 8.03627e-08% | 6.63699e-05% | 1.47102e-06% | 0.000462741% |
| ENERGY_FACTOR_LIMITED | 7.208504242 | 7.208504352 | 1.87151e-07% | 0.00055562% | 9.90176e-06% | 0.00281105% |
| COMPETITION_OCCUPANCY | 5.138041496 | 5.138036876 | 5.89315e-05% | 0.052502% | 0.00115311% | 0.0464469% |

四场景171维最大精确守恒绝对残差1.01692e-11，最小非负代表库存-6.93889e-18。冻结门为5%肽、5%资源、10%通量RMS、2%累计流量、1e-8守恒及-1e-9库存。尺度从初值库存取得，不以最终产量或累积量作分母。

全部窗口与逐时间误差见window_errors.csv和errors/*.csv；原始源、独立坐标、物理坐标、模型计数器、currents及接受步mesh保留于trajectories/*.npz，JSON记录列序、solver、hash、时长和nfev/njev/nlu。

gross CONSUMED_ATP/GTP表示从自由池取入的累计源事件量，含可逆结合/释放，不等于不可逆ATP/GTP水解量。NET库存变化与两个肽键事件另外报告；百万级gross结合循环不能解释成百万级能量消耗，也不能按肽产量固定倍数替代资源时序。

R0的241是实际参考RHS坐标数，原始矩阵仍只有rank214；其他表格维数是执行的独立图表维数。

## 失败与适用域边界

1. 两轮Gly局部上游pulse：早期产品误差约0.584%，长期资源误差≤0.00468%；保留竞争分流结果。非零fast=.1初值局部pulse的初始层资源误差10%、产品约9.20%，过渡层亦不小；长期仍通过。仅长期门PASS，不能声称全初始层精确。
2. CHAIN_INTERNAL_DOMAIN（fast=1、freeTuGDP=0）给投影freeTuGDP=−1，两轮均BLOCKED。固定作者旁支0952重新激活时，R0和R1完成而R2/R3全部BLOCKED；36恒零证明不能越域使用。
3. RF1/RF2合并精确反例：同一bound-ribosome总量1分别给Pept导数0.5/1.5，REJECTED，保留入口身份和不同速率。
4. 既有21-state total-QSSA九个完成耦合条件失败、一个solver不完成；九态restricted候选与两个14态enzyme-bound组分开登记。没有复跑或宣称其通过。
5. 四能量循环全稳态闭合的零产物无根/完整源边界MK、PPiase负自由形态证据保留。本轮没有全稳态替换；未来仅优先带独立产品/占用储存状态的新候选。
6. 数学实现早期尾释放数误写13、旧rank177错误沿用支持面、继承API名称错误和一次单位评分错误均保存failure_evidence.jsonl。评分v1全部轨迹/报告另存campaign_scoring_v1；修正应用已冻结库存尺度，未修改协议、参数、solver或阈值。

## B1-3与候选审查

34条已有历史本轮从源独立重算S*w、每步库存与载体DAG，全部通过。H1/H2/H3建议Y；H4–H9建议CONDITIONAL。全部研究者决定空白。细节见b1_3_independent_scientific_audit.md与b1_3_fresh_audit.json；26个原B1-3文件不变。

candidate_matrix.csv/source_map含15个候选的完整原species/IDs/输入输出/共享界面/所有逆向与竞争/源方程。优先后续工作：对171维RHS做稀疏图表和Jacobian工程优化，保持当前科学映射；科学新候选优先能量循环的动态储存版本。不能为了更小维数重新尝试已经有反例的全稳态或RF合并。

## 重现

在现有仓库使用当前Anaconda Python及numpy/scipy/sympy/numba/matplotlib：

```powershell
python -B scripts/reduction/rapid_v1/mathematics.py
python -B scripts/reduction/rapid_v1/audit_and_candidates.py
python -B scripts/reduction/rapid_v1/validate.py
python -B scripts/reduction/rapid_v1/score_saved.py
python -B scripts/reduction/rapid_v1/report.py
```

实现提供rhs_reduced、reconstruct_full、simulate_reference、simulate_reduced、compare_observables。RHS只读取冻结配置和精确chart对象。本次2443原有文件全hash保持；最终Git及逐文件清单在git_and_protection.json和file_manifest.csv。正式接受与commit/push均需独立后续研究者授权。

补充算法复核：R2与171维组合在作者baseline和能源/因子限制场景均实际完成紧BDF和独立Radau；四组图表的数值收敛全部PASS。完整配置、诊断及误差见reduced_solver_crosschecks.json，原始轨迹另存*_TIGHT及*_RADAU。
