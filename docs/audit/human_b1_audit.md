# Human B1 Audit Checklist（合并版）

> 目的：人工核对 `PURE_literature_reference` 是否忠实对应 Mavelli et al. (2015) 原文。主表用于逐项填写；精确 JSONPath / MATLAB 定位折叠在各节下方。
>
> **填写规则：一致填 `Y`，不一致填 `N`。**
>
> 不要让 AI 代填结果。若填 `N`，必须在“备注”写明差异。

## 0. 审核记录

- 审核人：____________________
- 日期：____________________
- 审核 commit：____________________
- Repo 定位核对基准：以审核时 `main` 的实际 commit 为准
- 原文文件：`references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE.pdf`
- 原文总页数：28 pages
- 结果填写：只允许 `Y` / `N`

### Repo 定位记号

- JSON 用近似 JSONPath：`$.a.b`；数组项用 `$.rates[id="V_TX"]` 表示“在数组中找到 `id=V_TX` 的对象”。
- MATLAB 用 `function_name()` 标函数；函数内再标变量/输出，例如 `rhs_pure_literature_reference() → V_TX, rates(1), dydt(1)`。
- `results/runs/<run_id>/...` 指你本次人工审核所绑定的正式运行目录；审核时把 `<run_id>` 替换成实际目录名。
- 若本表明确写“无独立字段/无专用函数”，表示当前 repo 只保存原始量，需要按各节折叠区中的“核对”方法自行计算；不要把文档中的二手数字当作独立实现。

---

## 1. 模型范围与基本定义

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| S01 | PDF p.5, Fig.2 + Sect.2, Eq.(1) | 模型围绕 TX / TL / RS / EN 四个模块；有效速率采用 Michaelis-Menten / rectangular-hyperbolic 形式 |  |  |
| S02 | PDF p.6, Sect.2 开头 | `n_NTP = 4`, `n_A = 20`, `n_T = 46` |  |  |
| S03 | PDF p.6, Sect.2 开头 | `[NTP]`, `[A]`, `[T]` 使用各类别的 **average concentration**；总量通过 multiplicity 计入 |  |  |
| S04 | PDF p.7, Sect.2.2, Eq.(7)-(8) 前文字 | `n_T/n_A = 46/20 = 2.3` |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **S01**
  - Repo：`models/literature_reference/model_definition.json` → `$.purpose`, `$.rates[*].{id,paper_equation,reaction}`；`models/literature_reference/model_manifest.json` → `$.scope_statement`, `$.model_type`, `$.assumptions[]`
  - 核对：检查 repo 是否仍是四模块、确定性 coarse-grained 文献模型；不能多出新的 B1 机制
- **S02**
  - Repo：`parameters.json` → `$.multiplicity.{n_NTP,n_A,n_T}`；`model_definition.json` → `$.intermediates[id="n_NTP"].value`, `[id="n_A"].value`, `[id="n_T"].value`；MATLAB `pure_literature_reference_params()` → `p.n_NTP,p.n_A,p.n_T`
  - 核对：三个数值逐项完全一致
- **S03**
  - Repo：`model_definition.json` → `$.states[id="NTP"].doc`, `id="A"`, `id="T"`；`model_manifest.json` → `$.states[id="NTP/A/T"].definition`；MATLAB `rhs_pure_literature_reference()` → `n_NTP,n_A,n_T` 及 `dydt(1/4/5/6)` 的除数
  - 核对：检查定义是否写成 average concentration，而不是总池浓度
- **S04**
  - Repo：`parameters.json` → `$.multiplicity.n_T_over_n_A`；`model_definition.json` → `$.intermediates[id="fTA"].{codegen,value}`；MATLAB `rhs_pure_literature_reference()` → `fTA = p.n_T/p.n_A`
  - 核对：数值与定义都一致；`fTA` 应对应 `n_T/n_A`

</details>

---

## 2. Transcription (TX)

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| TX01 | PDF p.6, Sect.2.1, Eq.(2) | `NTP --TXcat,DNA--> nt + PPi` |  |  |
| TX02 | PDF p.6, Eq.(3) | `PPi --PPase--> 2 Pi`，且原文说明该反应不显式积分 |  |  |
| TX03 | PDF p.6, Eq.(4) | `nt -> degradation` |  |  |
| TX04 | PDF p.6, Eq.(4) 后文字 | `nt` = polymerized nucleotides，不是 mRNA molecule concentration |  |  |
| TX05 | PDF p.7, Eq.(5) | `V_TX = k_TX * TXcat * DNA/(K_TX,DNA+DNA) * NTP/(K_TX,NTP+NTP)` |  |  |
| TX06 | PDF p.7, Eq.(6) | `V_nt,deg = k_nt,deg * nt` |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **TX01**
  - Repo：`model_definition.json` → `$.rates[id="V_TX"].{reaction,codegen}`, `$.stoichiometry.rates_order[0]="V_TX"`, `$.stoichiometry.matrix` 的 NTP/nt 行；MATLAB `rhs_pure_literature_reference()` → `V_TX`, `rates(1)`, `dydt(1)`, `dydt(3)`
  - 核对：检查 TX 使用 NTP、TXcat、DNA，产生 `nt`；PPi 不进入动态 RHS
- **TX02**
  - Repo：`model_manifest.json` → `$.assumptions[]` 中 “PPi hydrolysis ... not explicitly integrated”；确认 `$.states[*].id` 无 `PPi/Pi`；MATLAB `rhs_pure_literature_reference()` 无 `PPi/Pi` 变量或 rate
  - 核对：repo 不应新增 PPi/Pi 动态状态或 PPi 反馈速率
- **TX03**
  - Repo：`model_definition.json` → `$.rates[id="V_nt_deg"].{reaction,codegen}`；MATLAB `rhs_pure_literature_reference()` → `V_nt_deg`, `rates(2)`, `dydt(3)=V_TX-V_nt_deg`
  - 核对：存在 nt degradation，方向一致
- **TX04**
  - Repo：`model_definition.json` → `$.states[id="nt"].doc`；`model_manifest.json` → `$.states[id="nt"].definition`, `$.observables[id="mRNA"].mapping`
  - 核对：定义语义一致
- **TX05**
  - Repo：`model_definition.json` → `$.rates[id="V_TX"].codegen`；MATLAB `rhs_pure_literature_reference()` → local `V_TX`, output `rates(1)`
  - 核对：因子数量、变量、分母、乘法关系逐项一致
- **TX06**
  - Repo：`model_definition.json` → `$.rates[id="V_nt_deg"].codegen`；MATLAB `rhs_pure_literature_reference()` → local `V_nt_deg`, output `rates(2)`
  - 核对：必须是一阶衰减，无额外 Hill/MM 项

</details>

---

## 3. tRNA aminoacylation (RS)

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| RS01 | PDF p.7, Eq.(7) | `A + T + NTP --RScat--> AT + NXP` |  |  |
| RS02 | PDF p.7, Eq.(8) | `V_RS = k_RS*RScat * A/(K_RS,A+A) * 2.3T/(K_RS,T+2.3T) * NTP/(K_RS,NTP+NTP)` |  |  |
| RS03 | PDF p.7, Eq.(8) | `2.3` 必须乘在 `[T]` 的分子和分母对应项中 |  |  |
| RS04 | PDF p.7, Sect.2.2 | `[A]`、`[T]` 是平均浓度；`AT` multiplicity 由 `n_T/n_A` 处理 |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **RS01**
  - Repo：`model_definition.json` → `$.rates[id="V_RS"].reaction`, `$.stoichiometry.rates_order[2]="V_RS"`, `$.stoichiometry.matrix` 的 NXP/A/T/AT 行；MATLAB `rhs_pure_literature_reference()` → `V_RS`, `rates(3)`, `dydt(2/4/5/6)`
  - 核对：反应物/产物和方向一致
- **RS02**
  - Repo：`model_definition.json` → `$.rates[id="V_RS"].codegen`；MATLAB `rhs_pure_literature_reference()` → local `V_RS`, output `rates(3)`
  - 核对：三个 saturation factor 必须分别是 A、2.3T、NTP
- **RS03**
  - Repo：`model_definition.json` → `$.rates[id="V_RS"].codegen`, `$.intermediates[id="fTA"].codegen`；MATLAB `rhs_pure_literature_reference()` → `fTA=p.n_T/p.n_A` 与 `fTA*T/(p.K_RS_T+fTA*T)`
  - 核对：确认不是 `T/(K+T)`，也不是只在分子乘 2.3
- **RS04**
  - Repo：`model_definition.json` → `$.states[id="A/T/AT"].doc`, `$.intermediates[id="fTA"]`；`model_manifest.json` → `$.states[id="A/T/AT"].definition`, `$.multiplicity_factors`
  - 核对：变量定义与原文一致

</details>

---

## 4. Translation (TL)

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| TL01 | PDF p.8, Eq.(9) | `AT + 2NTP --TLcat, nt--> a + T + 2NXP` |  |  |
| TL02 | PDF p.8, Sect.2.3 | `a` = polymerized amino acids，不是 protein molecule concentration |  |  |
| TL03 | PDF p.8, Eq.(10) | `V_TL = k_TL*TLcat * nt/(K_TL,nt+nt) * 2.3AT/(K_TL,AT+2.3AT) * NTP/(K_TL,NTP+NTP)` |  |  |
| TL04 | PDF p.9, Eq.(11)-(12) | `TLcat -> degradation`; `V_TL,deg = k_TL,deg * TLcat` |  |  |
| TL05 | PDF p.9, Eq.(10) 后说明 | 虽然每个 elongation 消耗 2 NTP，但 `V_TL` 的 NTP 动力学仍只有 **一个** rectangular-hyperbolic factor；不使用 `[NTP]^2` |  |  |
| TL06 | PDF p.9, Sect.2.3 末 | GFP maturation 未纳入模型 |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **TL01**
  - Repo：`model_definition.json` → `$.rates[id="V_TL"].reaction`, `$.stoichiometry.rates_order[3]="V_TL"`, `$.stoichiometry.matrix` 的 NTP/NXP/T/AT/a 行；MATLAB `rhs_pure_literature_reference()` → `V_TL`, `rates(4)`, `dydt(1/2/5/6/7)`
  - 核对：必须有 2 NTP 消耗和 2 NXP 产生
- **TL02**
  - Repo：`model_definition.json` → `$.states[id="a"].doc`；`model_manifest.json` → `$.states[id="a"].definition`, `$.observables[id="protein"].mapping`
  - 核对：定义语义一致
- **TL03**
  - Repo：`model_definition.json` → `$.rates[id="V_TL"].codegen`；MATLAB `rhs_pure_literature_reference()` → local `V_TL`, output `rates(4)`
  - 核对：三个 saturation factor：nt、2.3AT、NTP，逐项一致
- **TL04**
  - Repo：`model_definition.json` → `$.rates[id="V_TL_deg"].{reaction,codegen}`；MATLAB `rhs_pure_literature_reference()` → `V_TL_deg`, `rates(5)`, `dydt(10)`
  - 核对：一阶衰减，方向一致
- **TL05**
  - Repo：`model_definition.json` → `$.rates[id="V_TL"].codegen` 与 `$.stoichiometry.matrix` 中 V_TL 列：NTP=`-2`, NXP=`+2`；MATLAB `rhs_pure_literature_reference()` → `V_TL` 只有单个 NTP saturation，`dydt(1)` 含 `-2*V_TL`, `dydt(2)` 含 `+2*V_TL`
  - 核对：检查 rate law 中没有 `NTP^2`；系数 2 只出现在 stoichiometry/ODE
- **TL06**
  - Repo：`model_manifest.json` → `$.assumptions[]` 中 “GFP maturation ... omitted”；确认 `model_definition.json → $.rates[*].id` 无 maturation rate；MATLAB `rhs_pure_literature_reference()` 无 maturation state/rate
  - 核对：B1 中不能额外加入 GFP maturation 动态反应

</details>

---

## 5. Energy regeneration (EN)

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| EN01 | PDF p.9, Sect.2.4 | NMP/NDP 等 exhausted nucleotides 被合并成单一 `NXP` |  |  |
| EN02 | PDF p.9, Eq.(13) | `CP + NXP --ENcat--> C + NTP` |  |  |
| EN03 | PDF p.9, Eq.(14) | `V_EN = k_EN*ENcat * CP/(K_EN,CP+CP) * NXP/(K_EN,NXP+NXP)` |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **EN01**
  - Repo：`model_definition.json` → `$.states[id="NXP"].doc`；`model_manifest.json` → `$.states[id="NXP"].definition`；MATLAB `rhs_pure_literature_reference()` → state `NXP=y(2)`
  - 核对：定义一致，不应在 B1 中拆成独立 NDP/NMP 状态
- **EN02**
  - Repo：`model_definition.json` → `$.rates[id="V_EN"].reaction`, `$.stoichiometry.rates_order[5]="V_EN"`, `$.stoichiometry.matrix` 的 NTP/NXP/CP/C 行；MATLAB `rhs_pure_literature_reference()` → `V_EN`, `rates(6)`, `dydt(1/2/8/9)`
  - 核对：反应物/产物/方向一致
- **EN03**
  - Repo：`model_definition.json` → `$.rates[id="V_EN"].codegen`；MATLAB `rhs_pure_literature_reference()` → local `V_EN`, output `rates(6)`
  - 核对：两个 saturation factor 分别为 CP、NXP

</details>

---

## 6. Fig.3 与 Overall Model 拓扑

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| OM01 | PDF p.10, Fig.3 | 四模块 TX/TL/RS/EN 的连接关系 |  |  |
| OM02 | PDF p.10, Sect.2.5 | 9 个 initially present species：DNA, A, T, NTP, CP, TXcat, TLcat, RScat, ENcat |  |  |
| OM03 | PDF p.10, Sect.2.5 | 4 kinetic stages + 2 decay reactions |  |  |
| OM04 | PDF p.10, Sect.2.5 | six kinetic rate constants + ten Michaelis-Menten constants |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **OM01**
  - Repo：`model_definition.json` → `$.rates[*].{id,reaction}`, `$.stoichiometry.{rates_order,species_order,matrix}`；MATLAB `rhs_pure_literature_reference()` → 六个 local rates `V_TX...V_EN` 与 `rates=[...]`
  - 核对：Fig.3 每条主反应在 repo 中有对应；repo 不多出 B1 新反应
- **OM02**
  - Repo：`parameters.json` → `$.initial_conditions.{DNA,A,T,NTP,CP,TLcat}` + `$.parameters.{TXcat,RScat,ENcat}`；`model_manifest.json` → 对应 `$.states[id=...].{initial_value,dynamic}`
  - 核对：名单逐项一致
- **OM03**
  - Repo：`model_definition.json` → `$.rates[*].id`（应仅 `V_TX,V_nt_deg,V_RS,V_TL,V_TL_deg,V_EN`）；MATLAB `rhs_pure_literature_reference()` → `rates(1:6)`
  - 核对：rate 数量与身份一致：V_TX, V_nt_deg, V_RS, V_TL, V_TL_deg, V_EN
- **OM04**
  - Repo：`model_manifest.json` → `$.parameter_inventory.{kinetic_constants_s^-1,michaelis_menten_constants_uM_independent,note_on_K_TL_RNA}`；`parameters.json` → `$.parameters` 与 `$.derived_quantities.K_TL_RNA`
  - 核对：独立 kinetic/MM 参数数量与分类一致；`K_TL_RNA` 另作 derived 检查

</details>

---

## 7. Mass conservation Eqs.(15)-(19)

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| MB01 | PDF p.10, Eq.(15) | `n_NTP*C_NTP^0 = n_NTP[NTP] + [nt] + [NXP] + degradation species` |  |  |
| MB02 | PDF p.10, Eq.(16) | `n_A*C_A^0 = n_A[A] + [a] + n_T[AT]` |  |  |
| MB03 | PDF p.10, Eq.(17) | `n_T*C_T^0 = n_T[T] + n_T[AT]` |  |  |
| MB04 | PDF p.10, Eq.(18) | `C_CP^0 = [CP] + [C]` |  |  |
| MB05 | PDF p.10, Eq.(19) | `C_TLcat^0 = [TLcat] + degradation species` |  |  |
| MB06 | PDF p.10, Eq.(15),(19) | degradation products 只用于守恒账本，不是新的反馈机制 |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **MB01**
  - Repo：`model_manifest.json` → `$.conservation_relations[id="B_NTP"].expression`；MATLAB `simulate_pure_literature_reference()` → local `local_qc()` 中 `B(:,1)=n_NTP*z(:,1)+z(:,3)+z(:,2)+z(:,11)`；`rhs_augmented()` 中 `z(:,11)=D_nt`
  - 核对：每一项、multiplicity 与 sink ledger 一致
- **MB02**
  - Repo：`model_manifest.json` → `$.conservation_relations[id="B_AA"].expression`；MATLAB `simulate_pure_literature_reference()` → `local_qc()` 中 `B(:,2)=n_A*z(:,4)+z(:,7)+n_T*z(:,6)`
  - 核对：系数和状态逐项一致
- **MB03**
  - Repo：`model_manifest.json` → `$.conservation_relations[id="B_tRNA"].expression`；MATLAB `simulate_pure_literature_reference()` → `local_qc()` 中 `B(:,3)=n_T*(z(:,5)+z(:,6))`
  - 核对：必须看 PDF 原式确认左侧有 superscript `0`；repo 表达式一致
- **MB04**
  - Repo：`model_manifest.json` → `$.conservation_relations[id="B_CP"].expression`；MATLAB `simulate_pure_literature_reference()` → `local_qc()` 中 `B(:,4)=z(:,8)+z(:,9)`
  - 核对：两项一致
- **MB05**
  - Repo：`model_manifest.json` → `$.conservation_relations[id="B_TLcat"].expression`；MATLAB `simulate_pure_literature_reference()` → `local_qc()` 中 `B(:,5)=z(:,10)+z(:,12)`；`z(:,12)=D_TLcat`
  - 核对：TLcat decay ledger 一致
- **MB06**
  - Repo：`parameters.json` → `$.initial_conditions.{D_nt,D_TLcat}`；`model_manifest.json` → `$.states[id="D_nt/D_TLcat"].definition`；MATLAB `simulate_pure_literature_reference()` → local `rhs_augmented()`：`dz=[dydt;rates(2);rates(5)]`，且调用 `rhs_pure_literature_reference()` 时只传 `z(1:10)`
  - 核对：确认 `D_nt`、`D_TLcat` 不进入任何 rate law

</details>

---

## 8. ODE Eqs.(20)-(27)

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| ODE01 | PDF p.11, Eq.(20) | `d[NTP]/dt = (-V_TX - 2V_TL - V_RS + V_EN)/n_NTP` |  |  |
| ODE02 | PDF p.11, Eq.(21) | `d[NXP]/dt = 2V_TL + V_RS - V_EN` |  |  |
| ODE03 | PDF p.11, Eq.(22) | `d[nt]/dt = V_TX - V_nt_deg` |  |  |
| ODE04 | PDF p.11, Eq.(23) | `d[A]/dt = -V_RS/n_A` |  |  |
| ODE05 | PDF p.11, Eq.(24) | `d[T]/dt = (-V_RS + V_TL)/n_T` |  |  |
| ODE06 | PDF p.11, Eq.(24) | `d[AT]/dt = (V_RS - V_TL)/n_T` |  |  |
| ODE07 | PDF p.11, Eq.(25) | `d[a]/dt = V_TL` |  |  |
| ODE08 | PDF p.11, Eq.(26) | `d[CP]/dt = -V_EN` |  |  |
| ODE09 | PDF p.11, Eq.(26) | `d[C]/dt = +V_EN` |  |  |
| ODE10 | PDF p.11, Eq.(27) | `d[TLcat]/dt = -V_TL_deg` |  |  |
| ODE11 | PDF p.11, Eq.(20)-(27) 后文字 | NTP 是 average concentration，NXP 是 overall concentration，因此二者 scaling 不同 |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **ODE01**
  - Repo：`model_definition.json` → `$.state_codegen[id="NTP"].codegen`, `$.stoichiometry.species_divisor.NTP`；MATLAB `rhs_pure_literature_reference()` → `dydt(1)`
  - 核对：符号、2、分母 `n_NTP` 完全一致
- **ODE02**
  - Repo：`model_definition.json` → `$.state_codegen[id="NXP"].codegen`；MATLAB `rhs_pure_literature_reference()` → `dydt(2)`
  - 核对：符号和系数完全一致
- **ODE03**
  - Repo：`model_definition.json` → `$.state_codegen[id="nt"].codegen`；MATLAB `rhs_pure_literature_reference()` → `dydt(3)`
  - 核对：完全一致
- **ODE04**
  - Repo：`model_definition.json` → `$.state_codegen[id="A"].codegen`, `$.stoichiometry.species_divisor.A`；MATLAB `rhs_pure_literature_reference()` → `dydt(4)`
  - 核对：符号和 `n_A` 完全一致
- **ODE05**
  - Repo：`model_definition.json` → `$.state_codegen[id="T"].codegen`, `$.stoichiometry.species_divisor.T`；MATLAB `rhs_pure_literature_reference()` → `dydt(5)`
  - 核对：符号和 `n_T` 完全一致
- **ODE06**
  - Repo：`model_definition.json` → `$.state_codegen[id="AT"].codegen`, `$.stoichiometry.species_divisor.AT`；MATLAB `rhs_pure_literature_reference()` → `dydt(6)`
  - 核对：与 T 方程互为相反变化，完全一致
- **ODE07**
  - Repo：`model_definition.json` → `$.state_codegen[id="a"].codegen`；MATLAB `rhs_pure_literature_reference()` → `dydt(7)`
  - 核对：完全一致
- **ODE08**
  - Repo：`model_definition.json` → `$.state_codegen[id="CP"].codegen`；MATLAB `rhs_pure_literature_reference()` → `dydt(8)`
  - 核对：符号一致
- **ODE09**
  - Repo：`model_definition.json` → `$.state_codegen[id="C"].codegen`；MATLAB `rhs_pure_literature_reference()` → `dydt(9)`
  - 核对：符号一致
- **ODE10**
  - Repo：`model_definition.json` → `$.state_codegen[id="TLcat"].codegen`；MATLAB `rhs_pure_literature_reference()` → `dydt(10)`
  - 核对：符号一致
- **ODE11**
  - Repo：`model_definition.json` → `$.states[id="NTP/NXP"].doc`, `$.stoichiometry.species_divisor.NTP="n_NTP"`（NXP 无 divisor key）；MATLAB `rhs_pure_literature_reference()` → `dydt(1)/n_NTP` vs `dydt(2)` 无除数
  - 核对：NTP 除以 `n_NTP`，NXP 不除

</details>

---

## 9. Observable mapping Eqs.(28)-(29)

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| OBS01 | PDF p.11, Eq.(28) 前文字 | `[mRNA] = [nt]/(3L)` |  |  |
| OBS02 | PDF p.11, Eq.(28) 前文字 | `[protein] = [a]/L` |  |  |
| OBS03 | PDF p.11, Eq.(28) | `k_RNA,deg = k_nt,deg` |  |  |
| OBS04 | PDF p.11, Eq.(29) | `K_TL,RNA = K_TL,nt/(3L)` |  |  |
| OBS05 | PDF p.13-14, GFP description + Fig.4 caption | `L = 238 aa`; 因而 `3L = 714` |  |  |
| OBS06 | PDF p.13 Table 2 + Eq.(29) | `K_TL,nt=226 µM`，Eq.(29) 给 `226/714 ≈ 0.31653 µM`，Table 2 报 `K_TL,RNA=0.32±0.02 µM` |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **OBS01**
  - Repo：`model_definition.json` → `$.observables[id="mRNA"].mapping`；MATLAB `simulate_pure_literature_reference()` → `out.mRNA = zz(:,3)/(3*p.L)`；测试 `test_pure_literature_reference() → test_observable_mapping()`
  - 核对：映射完全一致
- **OBS02**
  - Repo：`model_definition.json` → `$.observables[id="protein"].mapping`；MATLAB `simulate_pure_literature_reference()` → `out.protein = zz(:,7)/p.L`；测试 `test_pure_literature_reference() → test_observable_mapping()`
  - 核对：映射完全一致
- **OBS03**
  - Repo：`parameters.json` → `$.parameters.k_nt_deg`；`model_definition.json` → `$.rates[id="V_nt_deg"].codegen`。当前 repo **无独立 `k_RNA_deg` JSON key/Matlab field**；MATLAB `rhs_pure_literature_reference()` 仅实现 `V_nt_deg=p.k_nt_deg*nt`
  - 核对：若 repo 记录该关系，应与原文一致；若未单列但未违反，也可 Y
- **OBS04**
  - Repo：`parameters.json` → `$.derived_quantities.K_TL_RNA.{value,formula,paper_reported,paper_uncertainty}`；MATLAB `pure_literature_reference_params()` → `p.derived.K_TL_RNA`；测试 `test_pure_literature_reference() → test_ktl_rna_derived_value()`
  - 核对：公式一致
- **OBS05**
  - Repo：`parameters.json` → `$.protein.length_aa_L`；MATLAB `pure_literature_reference_params()` → `p.L`；`run_fig4_benchmark()` → `L=p0.L`；测试 `test_parameter_lock_tables_1_and_2()`
  - 核对：`L=238` 完全一致；手算 `3*238=714`
- **OBS06**
  - Repo：`parameters.json` → `$.parameters.K_TL_nt.value`, `$.derived_quantities.K_TL_RNA`；MATLAB `test_pure_literature_reference() → test_ktl_rna_derived_value()`
  - 核对：手工算 226/714，与 repo derived value 及 Table 2 范围比较

</details>

---

## 10. Table 1 初始浓度

原文位置统一：**PDF p.12, Table 1**。
Repo 位置统一：`models/literature_reference/parameters.json` → `initial_conditions` / fixed catalyst parameters。

| ID | 原文项目 | 原文值 | Repo 字段 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---:|---|---|---|---|
| IC01 | DNA | `0.34 to 6.8 ×10^-3 µM` | `parameters.json` → `$.initial_conditions.DNA.{value,unit,dynamic,source}`, `$.fig4_conditions_nM`；MATLAB `run_fig4_benchmark()` → `cond(k).dna_uM={0.00034,0.0017,0.0068}`；`simulate_pure_literature_reference(DNA_uM)` → `p.DNA=DNA_uM` | 单位换算后应覆盖 0.34 / 1.7 / 6.8 nM 三条件 |  |  |
| IC02 | TXcat | `0.1 µM` | `parameters.json` → `$.parameters.TXcat.{value,unit,origin,source}`；MATLAB `pure_literature_reference_params()` → `p.TXcat`；`rhs_pure_literature_reference()` → Eq.(5) `p.TXcat` | 数值、单位一致 |  |  |
| IC03 | TLcat | `2.2 ± 0.3 µM` | `parameters.json` → `$.initial_conditions.TLcat.{value,unit,dynamic,source}`；MATLAB `pure_literature_reference_params()` → `p.y0(10)`；`rhs_pure_literature_reference()` → `TLcat=y(10)` | repo 使用中心值 2.2 时，数值一致并注明来源为 fitting |  |  |
| IC04 | RScat | `0.16 µM` | `parameters.json` → `$.parameters.RScat.{value,unit,origin,source}`；MATLAB `pure_literature_reference_params()` → `p.RScat`；`rhs_pure_literature_reference()` → Eq.(8) `p.RScat` | 数值、单位一致 |  |  |
| IC05 | ENcat | `0.08 µM` | `parameters.json` → `$.parameters.ENcat.{value,unit,origin,source}`；MATLAB `pure_literature_reference_params()` → `p.ENcat`；`rhs_pure_literature_reference()` → Eq.(14) `p.ENcat` | 数值、单位一致 |  |  |
| IC06 | A | `300 µM` | `parameters.json` → `$.initial_conditions.A.{value,unit,dynamic,source}`；MATLAB `pure_literature_reference_params()` → `p.y0(4)`；`rhs_pure_literature_reference()` → `A=y(4)` | 数值一致；语义为 20 species average |  |  |
| IC07 | T | `1.9 µM` | `parameters.json` → `$.initial_conditions.T.{value,unit,dynamic,source}`；MATLAB `pure_literature_reference_params()` → `p.y0(5)`；`rhs_pure_literature_reference()` → `T=y(5)` | 数值一致；语义为 46 species average |  |  |
| IC08 | NTP | `1500 µM` | `parameters.json` → `$.initial_conditions.NTP.{value,unit,dynamic,source}`；MATLAB `pure_literature_reference_params()` → `p.y0(1)`；`rhs_pure_literature_reference()` → `NTP=y(1)` | 数值一致；语义为 4 species average |  |  |
| IC09 | CP | `20000 µM` | `parameters.json` → `$.initial_conditions.CP.{value,unit,dynamic,source}`；MATLAB `pure_literature_reference_params()` → `p.y0(8)`；`rhs_pure_literature_reference()` → `CP=y(8)` | 数值、单位一致 |  |  |
| IC10 | 新生成 species 初值 | Table 1 未逐项给出 NXP/nt/AT/a/C 初值 | `parameters.json` → `$.initial_conditions.{NXP,nt,AT,a,C}.{value,source}`；MATLAB `pure_literature_reference_params()` → `p.y0(2,3,6,7,9)`；测试 `test_parameter_lock_tables_1_and_2()` 的 expected `p.y0` | repo 若设 0，应标为 **inferred assumption**，不能写成“Table 1 明确给出” |  |  |

---

## 11. Table 2 kinetic parameters

原文位置统一：**PDF p.13, Table 2**。  
Repo 主位置：`models/literature_reference/parameters.json`；MATLAB loader：`pure_literature_reference_params()`。

| ID | 参数 | 原文值 | 原文来源 | Repo 对应位置（精确 key / function） | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---:|---|---|---|---|---|
| P01 | `k_TX` | `1.67 ± 0.14 s^-1` | Fitting | `parameters.json → $.parameters.k_TX.{value,unit,origin,source}`；`pure_literature_reference_params() → p.k_TX`；`rhs_pure_literature_reference() → V_TX` | repo 中心值、单位、origin 一致 |  |  |
| P02 | `k_TL` | `0.085 ± 0.020 s^-1` | Fitting | `parameters.json → $.parameters.k_TL.{value,unit,origin,source}`；`pure_literature_reference_params() → p.k_TL`；`rhs_pure_literature_reference() → V_TL` | 同上 |  |  |
| P03 | `k_RS` | `6.2 s^-1` | Brenda (avg.) | `parameters.json → $.parameters.k_RS.{value,unit,origin,source}`；`pure_literature_reference_params() → p.k_RS`；`rhs_pure_literature_reference() → V_RS` | 同上 |  |  |
| P04 | `k_EN` | `100 s^-1` | Brenda (EC 2.7.2.3) | `parameters.json → $.parameters.k_EN.{value,unit,origin,source}`；`pure_literature_reference_params() → p.k_EN`；`rhs_pure_literature_reference() → V_EN` | 同上 |  |  |
| P05 | `k_nt_deg` | `7.92 ± 0.51 ×10^-5 s^-1` | Fitting | `parameters.json → $.parameters.k_nt_deg.{value,unit,origin,source}`；`pure_literature_reference_params() → p.k_nt_deg`；`rhs_pure_literature_reference() → V_nt_deg` | 同上 |  |  |
| P06 | `k_TL_deg` | `1.86 ± 0.11 ×10^-4 s^-1` | Fitting | `parameters.json → $.parameters.k_TL_deg.{value,unit,origin,source}`；`pure_literature_reference_params() → p.k_TL_deg`；`rhs_pure_literature_reference() → V_TL_deg` | 同上 |  |  |
| P07 | `K_TX_DNA` | `5.00 ± 0.75 ×10^-3 µM` | Fitting | `parameters.json → $.parameters.K_TX_DNA.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_TX_DNA`；`rhs_pure_literature_reference() → V_TX` DNA denominator | 同上 |  |  |
| P08 | `K_TX_NTP` | `80 µM` | Brenda (EC 2.7.7.6) | `parameters.json → $.parameters.K_TX_NTP.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_TX_NTP`；`rhs_pure_literature_reference() → V_TX` NTP denominator | 同上 |  |  |
| P09 | `K_TL_nt` | `226 ± 16 µM` | Fitting | `parameters.json → $.parameters.K_TL_nt.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_TL_nt`；`rhs_pure_literature_reference() → V_TL` nt denominator | 同上 |  |  |
| P10 | `K_TL_RNA` | `0.32 ± 0.02 µM` | Fitting / 与 Eq.(29) 一致 | `parameters.json → $.derived_quantities.K_TL_RNA.{value,formula,paper_reported,paper_uncertainty}`；`pure_literature_reference_params() → p.derived.K_TL_RNA`；测试 `test_ktl_rna_derived_value()` | repo 应作为 derived QC quantity，不应作为独立 RHS 参数 |  |  |
| P11 | `K_TL_AT` | `10 µM` | Estimated | `parameters.json → $.parameters.K_TL_AT.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_TL_AT`；`rhs_pure_literature_reference() → V_TL` AT denominator | 数值、单位、origin 一致 |  |  |
| P12 | `K_TL_NTP` | `10 µM` | Estimated | `parameters.json → $.parameters.K_TL_NTP.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_TL_NTP`；`rhs_pure_literature_reference() → V_TL` NTP denominator | 同上 |  |  |
| P13 | `K_RS_A` | `23 µM` | Brenda (avg.) | `parameters.json → $.parameters.K_RS_A.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_RS_A`；`rhs_pure_literature_reference() → V_RS` A denominator | 同上 |  |  |
| P14 | `K_RS_T` | `0.7 µM` | Brenda (avg.) | `parameters.json → $.parameters.K_RS_T.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_RS_T`；`rhs_pure_literature_reference() → V_RS` T denominator | 同上 |  |  |
| P15 | `K_RS_NTP` | `200 µM` | Brenda (avg.) | `parameters.json → $.parameters.K_RS_NTP.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_RS_NTP`；`rhs_pure_literature_reference() → V_RS` NTP denominator | 同上 |  |  |
| P16 | `K_EN_CP` | `200 µM` | Brenda (EC 2.7.2.3) | `parameters.json → $.parameters.K_EN_CP.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_EN_CP`；`rhs_pure_literature_reference() → V_EN` CP denominator | 同上 |  |  |
| P17 | `K_EN_NXP` | `40 µM` | Brenda (EC 2.7.2.3) | `parameters.json → $.parameters.K_EN_NXP.{value,unit,origin,source}`；`pure_literature_reference_params() → p.K_EN_NXP`；`rhs_pure_literature_reference() → V_EN` NXP denominator | 同上 |  |  |

---

## 12. Fig.4 条件、坐标与曲线身份

| ID | 原文位置 | 原文检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| F401 | PDF p.13 最后一段 + p.14 Fig.4 caption | GFP 长度 `L=238`; DNA = `6.8, 1.7, 0.34 nM` |  |  |
| F402 | PDF p.14, Fig.4 caption | experimental = dotted；calculated = continuous |  |  |
| F403 | PDF p.14, Fig.4 caption | color: 0.34 nM blue, 1.7 nM green, 6.8 nM red |  |  |
| F404 | PDF p.14, Fig.4 caption | top = `[nt]`; bottom = `[a]` |  |  |
| F405 | PDF p.14, Fig.4 caption | actual mRNA = y-axis `[nt]/(3L)`；actual protein = `[a]/L` |  |  |
| F406 | PDF p.13-14 | 论文说 nt curves fit quite well；a curves 不完全满意但得到 sigmoid |  |  |
| F407 | PDF p.14 Fig.4 | 人工盲读 48 个点（3 DNA × 2 panels × 8 times） |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **F401**
  - Repo：`parameters.json` → `$.protein.length_aa_L`, `$.fig4_conditions_nM`；MATLAB `run_fig4_benchmark()` → `cond(k).dna_uM`, `L=p0.L`; `pure_literature_reference_params()` → `p.L`
  - 核对：三个 DNA 条件和 L 完全一致
- **F402**
  - Repo：`docs/audit/manual_fig4_audit_protocol.md` → Protocol step 3；MATLAB `digitize_fig4()` → docstring + output `T1.curve_type="calculated_continuous"`, `digitization_flag`
  - 核对：曲线身份说明一致
- **F403**
  - Repo：MATLAB `run_fig4_benchmark()` → `cond` 顺序 + `colors` matrix；`digitize_fig4()` → `color_name={"red","green","blue"}`, `color_dna=[6.8,1.7,0.34]`
  - 核对：颜色映射一致
- **F404**
  - Repo：MATLAB `run_fig4_benchmark()` → Fig.4 plot: top `res{k}.y(:,3)`, bottom `res{k}.y(:,7)`；`trajectory.csv` columns `nt_uM`, `a_uM`
  - 核对：repo Fig.4 reproduction 的两个 panel 变量一致
- **F405**
  - Repo：`model_definition.json` → `$.observables[id="mRNA/protein"].mapping`；MATLAB `simulate_pure_literature_reference()` → `out.mRNA,out.protein`; `run_fig4_benchmark()` → auxiliary figure `res{k}.mRNA`, `res{k}.protein`
  - 核对：repo 没把 `[nt]` 直接标成 mRNA molecules，也没把 `[a]` 直接标成 protein molecules
- **F406**
  - Repo：`docs/project/evidence_levels.json` → `$.evidence_levels.fig4_simulation_assisted_digitization_status`, `$.evidence_levels.fig4_independent_human_audit`, `$.evidence_levels.experimental_data_validation`；`docs/validation/benchmark_v0.md` → Q5 / Explicit non-claims
  - 核对：repo 不得把 Fig.4 说成“实验完美验证”
- **F407**
  - Repo：`data/manual_audit/fig4_human_digitization_template.csv` → columns `panel,dna_nM,time_h,value_uM,estimated_reading_error_uM,...`；`docs/audit/manual_fig4_audit_protocol.md` → steps 1–7。当前 repo **无专用 MATLAB human-audit comparison function**，人工填完后再对 `results/runs/<run_id>/DNA_*/trajectory.csv` 比较
  - 核对：在不看 simulation 的情况下填完；再比较 simulation 是否落入人工读图误差

</details>

### Fig.4 人工盲读结果文件

- 我的文件：`data/manual_audit/fig4_human_digitization_________________.csv`
- 是否在读图时隐藏 simulation：`Y / N`：________
- 48 点是否全部完成：`Y / N`：________
- 是否存在超出人工读图误差的点：`Y / N`：________
- 若有，列出：____________________________________________________________

---

## 13. 论文文字数值 anchors

| ID | 原文位置 | 原文值/描述 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| A01 | PDF p.16, Sect.4.1 | standard/non-diluted PURE 在 4 h 蛋白 yield = `0.58 µM` |  |  |
| A02 | PDF p.21, Eq.(33) | `chi_e = n_NTP[NTP] + [CP]` |  |  |
| A03 | PDF p.21, Eq.(34) | `-d chi_e/dt = V_TX + 2V_TL + V_RS` |  |  |
| A04 | PDF p.21, Fig.8 narrative | `phi_RS ≈ 85%` at `t ~ 1 min` |  |  |
| A05 | PDF p.22, Fig.8 narrative | RS minimum rate at about `4 min` |  |  |
| A06 | PDF p.22, Fig.8 narrative | after ~30 min: `phi_TL ≈24%`, `phi_RS ≈12%`, sum ≈`36%`, `phi_TX ≈64%` |  |  |
| A07 | PDF p.23, Fig.9 text | at DNA=6.8 nM: `Q_TX=74%`, `Q_TL=15%`, `Q_RS=11%` |  |  |
| A08 | PDF p.24, Table 4 entry 1 | standard PURE: `Q_TX=74%`, `Q_TL+Q_RS=26%`, ratio `(Q_TL+Q_RS)/Q_TX=0.35` |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **A01**
  - Repo：`results/runs/<run_id>/DNA_6p8nM/qc.json` → `$.anchors.protein_4h_molecules_uM`, `$.anchors.paper_protein_4h_molecules_uM`, `$.endpoints.protein_molecules_uM`；MATLAB `run_fig4_benchmark() → local_anchors()`
  - 核对：比较 **protein molecule concentration**，即 `a/L`，不能直接拿 `[a]` 比 0.58
- **A02**
  - Repo：`parameters.json` → `$.multiplicity.n_NTP`；`results/runs/<run_id>/DNA_6p8nM/trajectory.csv` → `NTP_uM,CP_uM`。MATLAB `simulate_pure_literature_reference() → local_qc()` 只在注释引用 Eq.(33)，**未单独输出 `chi_e` 字段**；需手算 `4*NTP_uM+CP_uM`
  - 核对：能量定义一致
- **A03**
  - Repo：`results/runs/<run_id>/DNA_6p8nM/rates.csv` → `V_TX_uM_s,V_TL_uM_s,V_RS_uM_s`；MATLAB `simulate_pure_literature_reference() → local_qc()` → `qc.energy_integral_uM=[trapz(V_TX),2*trapz(V_TL),trapz(V_RS)]`
  - 核对：必须有 `2*V_TL`
- **A04**
  - Repo：`results/runs/<run_id>/DNA_6p8nM/rates.csv` → `V_TX_uM_s,V_TL_uM_s,V_RS_uM_s`；当前 repo **无 `phi_RS` JSON 字段/专用函数**；需由瞬时分母 `V_TX+2*V_TL+V_RS` 自行计算；文档二手结果在 `docs/project/benchmark_registry.md` quantitative anchors
  - 核对：比较约数，不要求机器精度
- **A05**
  - Repo：`results/runs/<run_id>/DNA_6p8nM/rates.csv` → `time_s,V_RS_uM_s`；当前 repo **无 RS-minimum 专用函数/JSON 字段**；人工找 `V_RS_uM_s` 的局部 minimum；文档二手结果在 `docs/project/benchmark_registry.md`
  - 核对：比较时间位置，允许原文“about”的读图误差
- **A06**
  - Repo：`results/runs/<run_id>/DNA_6p8nM/rates.csv` → `time_s,V_TX_uM_s,V_TL_uM_s,V_RS_uM_s`；当前 repo **无 `phi_TX/phi_TL/phi_RS` 字段**；按 `V_TX/(V_TX+2V_TL+V_RS)`, `2V_TL/(...)`, `V_RS/(...)` 自算
  - 核对：分项和合计分别比较
- **A07**
  - Repo：`results/runs/<run_id>/DNA_6p8nM/qc.json` → `$.energy_split_percent.{Q_TX,Q_TL,Q_RS}`, `$.anchors.paper_energy_split_percent`, `$.anchors.energy_split_abs_dev_pp`；MATLAB `simulate_pure_literature_reference() → local_qc()` 与 `run_fig4_benchmark() → local_anchors()`
  - 核对：用 percentage-point difference 比较；确认定义为积分 `V_TX`, `2V_TL`, `V_RS`
- **A08**
  - Repo：`results/runs/<run_id>/DNA_6p8nM/qc.json` → `$.energy_split_percent.{Q_TX,Q_TL,Q_RS}`；MATLAB `local_qc()` 产生三分量；repo **无直接 ratio 字段**，自行算 `(Q_TL+Q_RS)/Q_TX`
  - 核对：从 repo 数值自行计算并比较

</details>

---

## 14. Source assumptions / 不可伪装成原文明示的信息

| ID | 原文位置 | 检查项 | 结果 Y/N | 备注 |
| :--- | :--- | :--- | :--- | :--- |
| AS01 | PDF p.12 Table 1 + Sect.3 | NXP/nt/AT/a/C 的初值没有在 Table 1 逐项列为 0 |  |  |
| AS02 | PDF p.11, Sect.2.5 末 | 论文讨论 closed system、资源随时间耗尽；没有给具体 reactor volume 数值 |  |  |
| AS03 | PDF p.5-14 | B1 equations 中没有温度/pH/Mg²⁺显式动力学项 |  |  |
| AS04 | PDF p.13 最后一段 | 作者提到可用 Hill `v=3.465` 得到稍好 a-curve fit，但明确**没有引入正式模型** |  |  |

<details>
<summary>展开：Repo 精确定位与核对方法</summary>

- **AS01**
  - Repo：`parameters.json` → `$.initial_conditions.{NXP,nt,AT,a,C}.source`；`model_manifest.json` → `$.assumptions[]` 中 “newly-created species ... start at zero”
  - 核对：repo 必须把这些 0 表述为推断/模型初始化决定，而不是“Table 1 明确给出”
- **AS02**
  - Repo：`model_manifest.json` → `$.boundary=["batch","fixed_volume","well_mixed"]`, `$.assumptions[]`；确认 `parameters.json`/`model_definition.json` **无具体 volume 数值 key**
  - 核对：repo 可写 batch/fixed-volume concentration formulation，但不能虚构具体体积
- **AS03**
  - Repo：`docs/project/benchmark_registry.md` → benchmark specification 的 `Temperature / pH / Mg²⁺` 行；确认 `model_definition.json → $.rates[*].codegen` 与 `parameters.json → $.parameters` 无 T/pH/Mg²⁺ 输入
  - 核对：若记录为 “not specified / not used by this model” 则一致；不能擅自补数值
- **AS04**
  - Repo：`model_definition.json` → `$.rates[id="V_TL"].codegen`；MATLAB `rhs_pure_literature_reference()` → local `V_TL`；确认无 `Hill`, `v`, `NTP^v` 等项；`model_manifest.json → $.assumptions[]`
  - 核对：B1 不能加入 Hill coefficient

</details>

---

## 15. Canonical definition → generated RHS 一致性

这部分不是和论文新增科学内容比较，而是检查 repo 内部是否从同一份模型定义生成代码。

| ID | 检查项 | Repo 位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|
| CG01 | canonical rate laws 与论文核对完成后，generated RHS 必须来自 canonical definition | `model_definition.json` → `$.generation.{generator,output,baseline_snapshot,deterministic}`；MATLAB `generate_pure_literature_reference()`；测试 `test_codegen_and_provenance() → test_generator_output_in_sync()` | 删除/备份 generated RHS 后重新生成，`git diff` 应无数学差异 |  |  |
| CG02 | `state_codegen` 与 `stoichiometry.matrix` 表达同一组 ODE | `model_definition.json` → `$.state_codegen[*].{id,codegen}`, `$.stoichiometry.{matrix,species_order,rates_order,species_divisor}`；测试 `test_codegen_and_provenance() → test_stoichiometry_matches_code()` | 人工抽查至少 NTP、NXP、T、AT 四行 |  |  |
| CG03 | generated RHS 中 Eq.(5),(8),(10),(14),(20),(21),(24) 与 PDF 对应式一致 | MATLAB `rhs_pure_literature_reference()` → `V_TX,V_RS,V_TL,V_EN,dydt(1),dydt(2),dydt(5),dydt(6)`；生成器 `generate_pure_literature_reference()`；测试 `test_pure_literature_reference() → test_rate_law_spot_values()` | 随机抽查这些关键式，逐符号比较 |  |  |

---

## 16. 最终结论

### 必须全部填写

- S01-S04：是否全为 Y：________
- TX01-TX06：是否全为 Y：________
- RS01-RS04：是否全为 Y：________
- TL01-TL06：是否全为 Y：________
- EN01-EN03：是否全为 Y：________
- OM01-OM04：是否全为 Y：________
- MB01-MB06：是否全为 Y：________
- ODE01-ODE11：是否全为 Y：________
- OBS01-OBS06：是否全为 Y：________
- IC01-IC10：是否全为 Y：________
- P01-P17：是否全为 Y：________
- F401-F407：是否全为 Y：________
- A01-A08：是否全为 Y：________
- AS01-AS04：是否全为 Y：________
- CG01-CG03：是否全为 Y：________

### 审核判定

- 是否存在任何 `N`：________
- 若存在 `N`，对应 ID：____________________________________________________
- 是否允许将 B1 标记为 `human_audited`：`Y / N`：________
- 审核人签名/缩写：____________________
- 日期：____________________

### N 项处理记录

| ID | 差异描述 | 是原文歧义 / repo 错误 / 文档措辞问题 | 修复 commit | 修复后复核 Y/N |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

