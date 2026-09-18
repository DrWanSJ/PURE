# Human B1 Audit Checklist

> 目的：人工核对 `PURE_literature_reference` 是否忠实对应 Mavelli et al. (2015) 原文。
>
> **填写规则：一致填 `Y`，不一致填 `N`。**
>
> 不要让 AI 代填结果。若填 `N`，必须在“备注”写明差异。

## 0. 审核记录

- 审核人：____________________
- 日期：____________________
- 审核 commit：****cb9b594b59df4857ba774f64f7106688da03382a****
- 原文文件：`references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE.pdf`
- 原文总页数：28 pages
- 结果填写：只允许 `Y` / `N`

---

## 1. 模型范围与基本定义

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| S01 | PDF p.5, Fig.2 + Sect.2, Eq.(1) | 模型围绕 TX / TL / RS / EN 四个模块；有效速率采用 Michaelis-Menten / rectangular-hyperbolic 形式 | `models/literature_reference/model_definition.json` → `purpose`, `rates`; `README.md` → Scope | 检查 repo 是否仍是四模块、确定性 coarse-grained 文献模型；不能多出新的 B1 机制 |  |  |
| S02 | PDF p.6, Sect.2 开头 | `n_NTP = 4`, `n_A = 20`, `n_T = 46` | `models/literature_reference/parameters.json` → `multiplicity`; `model_definition.json` → `intermediates` | 三个数值逐项完全一致 |  |  |
| S03 | PDF p.6, Sect.2 开头 | `[NTP]`, `[A]`, `[T]` 使用各类别的 **average concentration**；总量通过 multiplicity 计入 | `model_definition.json` → `states` docs; `model_manifest.json` → states/assumptions | 检查定义是否写成 average concentration，而不是总池浓度 |  |  |
| S04 | PDF p.7, Sect.2.2, Eq.(7)-(8) 前文字 | `n_T/n_A = 46/20 = 2.3` | `model_definition.json` → `intermediates.fTA`; `parameters.json` → `n_T_over_n_A` | 数值与定义都一致；`fTA` 应对应 `n_T/n_A` |  |  |

---

## 2. Transcription (TX)

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| TX01 | PDF p.6, Sect.2.1, Eq.(2) | `NTP --TXcat,DNA--> nt + PPi` | `model_definition.json` → `rates.V_TX`, `stoichiometry`; `rhs_pure_literature_reference.m` → `V_TX` | 检查 TX 使用 NTP、TXcat、DNA，产生 `nt`；PPi 不进入动态 RHS |  |  |
| TX02 | PDF p.6, Eq.(3) | `PPi --PPase--> 2 Pi`，且原文说明该反应不显式积分 | `model_manifest.json` → assumptions; `model_definition.json` | repo 不应新增 PPi/Pi 动态状态或 PPi 反馈速率 |  |  |
| TX03 | PDF p.6, Eq.(4) | `nt -> degradation` | `model_definition.json` → `V_nt_deg`; generated RHS | 存在 nt degradation，方向一致 |  |  |
| TX04 | PDF p.6, Eq.(4) 后文字 | `nt` = polymerized nucleotides，不是 mRNA molecule concentration | `model_definition.json` → state `nt`; `model_manifest.json` → state `nt` | 定义语义一致 |  |  |
| TX05 | PDF p.7, Eq.(5) | `V_TX = k_TX * TXcat * DNA/(K_TX,DNA+DNA) * NTP/(K_TX,NTP+NTP)` | `model_definition.json` → rate `V_TX.codegen`; `matlab/generated/rhs_pure_literature_reference.m` | 因子数量、变量、分母、乘法关系逐项一致 |  |  |
| TX06 | PDF p.7, Eq.(6) | `V_nt,deg = k_nt,deg * nt` | `model_definition.json` → `V_nt_deg.codegen`; generated RHS | 必须是一阶衰减，无额外 Hill/MM 项 |  |  |

---

## 3. tRNA aminoacylation (RS)

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| RS01 | PDF p.7, Eq.(7) | `A + T + NTP --RScat--> AT + NXP` | `model_definition.json` → `V_RS`, `stoichiometry` | 反应物/产物和方向一致 |  |  |
| RS02 | PDF p.7, Eq.(8) | `V_RS = k_RS*RScat * A/(K_RS,A+A) * 2.3T/(K_RS,T+2.3T) * NTP/(K_RS,NTP+NTP)` | `model_definition.json` → `V_RS.codegen`; generated RHS | 三个 saturation factor 必须分别是 A、2.3T、NTP |  |  |
| RS03 | PDF p.7, Eq.(8) | `2.3` 必须乘在 `[T]` 的分子和分母对应项中 | `model_definition.json` → `V_RS.codegen` | 确认不是 `T/(K+T)`，也不是只在分子乘 2.3 |  |  |
| RS04 | PDF p.7, Sect.2.2 | `[A]`、`[T]` 是平均浓度；`AT` multiplicity 由 `n_T/n_A` 处理 | `model_definition.json` → states/intermediates; `model_manifest.json` | 变量定义与原文一致 |  |  |

---

## 4. Translation (TL)

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| TL01 | PDF p.8, Eq.(9) | `AT + 2NTP --TLcat, nt--> a + T + 2NXP` | `model_definition.json` → `V_TL`, `stoichiometry`; generated RHS ODEs | 必须有 2 NTP 消耗和 2 NXP 产生 |  |  |
| TL02 | PDF p.8, Sect.2.3 | `a` = polymerized amino acids，不是 protein molecule concentration | `model_definition.json` → state `a`; `model_manifest.json` | 定义语义一致 |  |  |
| TL03 | PDF p.8, Eq.(10) | `V_TL = k_TL*TLcat * nt/(K_TL,nt+nt) * 2.3AT/(K_TL,AT+2.3AT) * NTP/(K_TL,NTP+NTP)` | `model_definition.json` → `V_TL.codegen`; generated RHS | 三个 saturation factor：nt、2.3AT、NTP，逐项一致 |  |  |
| TL04 | PDF p.9, Eq.(11)-(12) | `TLcat -> degradation`; `V_TL,deg = k_TL,deg * TLcat` | `model_definition.json` → `V_TL_deg`; generated RHS | 一阶衰减，方向一致 |  |  |
| TL05 | PDF p.9, Eq.(10) 后说明 | 虽然每个 elongation 消耗 2 NTP，但 `V_TL` 的 NTP 动力学仍只有 **一个** rectangular-hyperbolic factor；不使用 `[NTP]^2` | `model_definition.json` → `V_TL.codegen`; generated RHS | 检查 rate law 中没有 `NTP^2`；系数 2 只出现在 stoichiometry/ODE |  |  |
| TL06 | PDF p.9, Sect.2.3 末 | GFP maturation 未纳入模型 | `model_manifest.json` → assumptions; `model_definition.json` | B1 中不能额外加入 GFP maturation 动态反应 |  |  |

---

## 5. Energy regeneration (EN)

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| EN01 | PDF p.9, Sect.2.4 | NMP/NDP 等 exhausted nucleotides 被合并成单一 `NXP` | `model_definition.json` → state `NXP`; `model_manifest.json` | 定义一致，不应在 B1 中拆成独立 NDP/NMP 状态 |  |  |
| EN02 | PDF p.9, Eq.(13) | `CP + NXP --ENcat--> C + NTP` | `model_definition.json` → `V_EN`, `stoichiometry` | 反应物/产物/方向一致 |  |  |
| EN03 | PDF p.9, Eq.(14) | `V_EN = k_EN*ENcat * CP/(K_EN,CP+CP) * NXP/(K_EN,NXP+NXP)` | `model_definition.json` → `V_EN.codegen`; generated RHS | 两个 saturation factor 分别为 CP、NXP |  |  |

---

## 6. Fig.3 与 Overall Model 拓扑

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| OM01 | PDF p.10, Fig.3 | 四模块 TX/TL/RS/EN 的连接关系 | `model_definition.json` → `rates`, `stoichiometry`; `model_manifest.json` | Fig.3 每条主反应在 repo 中有对应；repo 不多出 B1 新反应 |  |  |
| OM02 | PDF p.10, Sect.2.5 | 9 个 initially present species：DNA, A, T, NTP, CP, TXcat, TLcat, RScat, ENcat | `parameters.json` → initial_conditions/parameters; `model_manifest.json` | 名单逐项一致 |  |  |
| OM03 | PDF p.10, Sect.2.5 | 4 kinetic stages + 2 decay reactions | `model_definition.json` → 6 rates | rate 数量与身份一致：V_TX, V_nt_deg, V_RS, V_TL, V_TL_deg, V_EN |  |  |
| OM04 | PDF p.10, Sect.2.5 | six kinetic rate constants + ten Michaelis-Menten constants | `parameters.json` → `parameters` | 独立 kinetic/MM 参数数量与分类一致；`K_TL_RNA` 另作 derived 检查 |  |  |

---

## 7. Mass conservation Eqs.(15)-(19)

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| MB01 | PDF p.10, Eq.(15) | `n_NTP*C_NTP^0 = n_NTP[NTP] + [nt] + [NXP] + degradation species` | `model_manifest.json` → `B_NTP`; `simulate_pure_literature_reference.m` → `local_qc` | 每一项、multiplicity 与 sink ledger 一致 |  |  |
| MB02 | PDF p.10, Eq.(16) | `n_A*C_A^0 = n_A[A] + [a] + n_T[AT]` | `model_manifest.json` → `B_AA`; `simulate...local_qc` | 系数和状态逐项一致 |  |  |
| MB03 | PDF p.10, Eq.(17) | `n_T*C_T^0 = n_T[T] + n_T[AT]` | `model_manifest.json` → `B_tRNA`; `simulate...local_qc` | 必须看 PDF 原式确认左侧有 superscript `0`；repo 表达式一致 |  |  |
| MB04 | PDF p.10, Eq.(18) | `C_CP^0 = [CP] + [C]` | `model_manifest.json` → `B_CP`; `simulate...local_qc` | 两项一致 |  |  |
| MB05 | PDF p.10, Eq.(19) | `C_TLcat^0 = [TLcat] + degradation species` | `model_manifest.json` → `B_TLcat`; `simulate...local_qc` | TLcat decay ledger 一致 |  |  |
| MB06 | PDF p.10, Eq.(15),(19) | degradation products 只用于守恒账本，不是新的反馈机制 | `simulate_pure_literature_reference.m` → augmented states `D_nt`, `D_TLcat` | 确认 `D_nt`、`D_TLcat` 不进入任何 rate law |  |  |

---

## 8. ODE Eqs.(20)-(27)

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| ODE01 | PDF p.11, Eq.(20) | `d[NTP]/dt = (-V_TX - 2V_TL - V_RS + V_EN)/n_NTP` | `model_definition.json` → `state_codegen[NTP]`; generated RHS | 符号、2、分母 `n_NTP` 完全一致 |  |  |
| ODE02 | PDF p.11, Eq.(21) | `d[NXP]/dt = 2V_TL + V_RS - V_EN` | `state_codegen[NXP]`; generated RHS | 符号和系数完全一致 |  |  |
| ODE03 | PDF p.11, Eq.(22) | `d[nt]/dt = V_TX - V_nt_deg` | `state_codegen[nt]`; generated RHS | 完全一致 |  |  |
| ODE04 | PDF p.11, Eq.(23) | `d[A]/dt = -V_RS/n_A` | `state_codegen[A]`; generated RHS | 符号和 `n_A` 完全一致 |  |  |
| ODE05 | PDF p.11, Eq.(24) | `d[T]/dt = (-V_RS + V_TL)/n_T` | `state_codegen[T]`; generated RHS | 符号和 `n_T` 完全一致 |  |  |
| ODE06 | PDF p.11, Eq.(24) | `d[AT]/dt = (V_RS - V_TL)/n_T` | `state_codegen[AT]`; generated RHS | 与 T 方程互为相反变化，完全一致 |  |  |
| ODE07 | PDF p.11, Eq.(25) | `d[a]/dt = V_TL` | `state_codegen[a]`; generated RHS | 完全一致 |  |  |
| ODE08 | PDF p.11, Eq.(26) | `d[CP]/dt = -V_EN` | `state_codegen[CP]`; generated RHS | 符号一致 |  |  |
| ODE09 | PDF p.11, Eq.(26) | `d[C]/dt = +V_EN` | `state_codegen[C]`; generated RHS | 符号一致 |  |  |
| ODE10 | PDF p.11, Eq.(27) | `d[TLcat]/dt = -V_TL_deg` | `state_codegen[TLcat]`; generated RHS | 符号一致 |  |  |
| ODE11 | PDF p.11, Eq.(20)-(27) 后文字 | NTP 是 average concentration，NXP 是 overall concentration，因此二者 scaling 不同 | `model_definition.json` → states + `species_divisor`; generated RHS | NTP 除以 `n_NTP`，NXP 不除 |  |  |

---

## 9. Observable mapping Eqs.(28)-(29)

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| OBS01 | PDF p.11, Eq.(28) 前文字 | `[mRNA] = [nt]/(3L)` | `model_definition.json` → observable `mRNA`; `simulate_pure_literature_reference.m` → `out.mRNA` | 映射完全一致 |  |  |
| OBS02 | PDF p.11, Eq.(28) 前文字 | `[protein] = [a]/L` | `model_definition.json` → observable `protein`; `simulate...` → `out.protein` | 映射完全一致 |  |  |
| OBS03 | PDF p.11, Eq.(28) | `k_RNA,deg = k_nt,deg` | `parameters.json` / derived documentation | 若 repo 记录该关系，应与原文一致；若未单列但未违反，也可 Y |  |  |
| OBS04 | PDF p.11, Eq.(29) | `K_TL,RNA = K_TL,nt/(3L)` | `parameters.json` → `derived_quantities.K_TL_RNA` | 公式一致 |  |  |
| OBS05 | PDF p.13-14, GFP description + Fig.4 caption | `L = 238 aa`; 因而 `3L = 714` | `parameters.json` → `protein.length_aa_L`; `model_definition.json` observables | `L=238` 完全一致；手算 `3*238=714` |  |  |
| OBS06 | PDF p.13 Table 2 + Eq.(29) | `K_TL,nt=226 µM`，Eq.(29) 给 `226/714 ≈ 0.31653 µM`，Table 2 报 `K_TL,RNA=0.32±0.02 µM` | `parameters.json` → derived `K_TL_RNA` | 手工算 226/714，与 repo derived value 及 Table 2 范围比较 |  |  |

---

## 10. Table 1 初始浓度

原文位置统一：**PDF p.12, Table 1**。
Repo 位置统一：`models/literature_reference/parameters.json` → `initial_conditions` / fixed catalyst parameters。

| ID | 原文项目 | 原文值 | Repo 字段 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---:|---|---|---|---|
| IC01 | DNA | `0.34 to 6.8 ×10^-3 µM` | `initial_conditions.DNA`; `fig4_conditions_nM` | 单位换算后应覆盖 0.34 / 1.7 / 6.8 nM 三条件 |  |  |
| IC02 | TXcat | `0.1 µM` | `parameters.TXcat` | 数值、单位一致 |  |  |
| IC03 | TLcat | `2.2 ± 0.3 µM` | `initial_conditions.TLcat` | repo 使用中心值 2.2 时，数值一致并注明来源为 fitting |  |  |
| IC04 | RScat | `0.16 µM` | `parameters.RScat` | 数值、单位一致 |  |  |
| IC05 | ENcat | `0.08 µM` | `parameters.ENcat` | 数值、单位一致 |  |  |
| IC06 | A | `300 µM` | `initial_conditions.A` | 数值一致；语义为 20 species average |  |  |
| IC07 | T | `1.9 µM` | `initial_conditions.T` | 数值一致；语义为 46 species average |  |  |
| IC08 | NTP | `1500 µM` | `initial_conditions.NTP` | 数值一致；语义为 4 species average |  |  |
| IC09 | CP | `20000 µM` | `initial_conditions.CP` | 数值、单位一致 |  |  |
| IC10 | 新生成 species 初值 | Table 1 未逐项给出 NXP/nt/AT/a/C 初值 | `parameters.json` → NXP, nt, AT, a, C initial values | repo 若设 0，应标为 **inferred assumption**，不能写成“Table 1 明确给出” |  |  |

---

## 11. Table 2 kinetic parameters

原文位置统一：**PDF p.13, Table 2**。
Repo 位置统一：`models/literature_reference/parameters.json` → `parameters`。

| ID | 参数 | 原文值 | 原文来源 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---:|---|---|---|---|
| P01 | `k_TX` | `1.67 ± 0.14 s^-1` | Fitting | repo 中心值、单位、origin 一致 |  |  |
| P02 | `k_TL` | `0.085 ± 0.020 s^-1` | Fitting | 同上 |  |  |
| P03 | `k_RS` | `6.2 s^-1` | Brenda (avg.) | 同上 |  |  |
| P04 | `k_EN` | `100 s^-1` | Brenda (EC 2.7.2.3) | 同上 |  |  |
| P05 | `k_nt_deg` | `7.92 ± 0.51 ×10^-5 s^-1` | Fitting | 同上 |  |  |
| P06 | `k_TL_deg` | `1.86 ± 0.11 ×10^-4 s^-1` | Fitting | 同上 |  |  |
| P07 | `K_TX_DNA` | `5.00 ± 0.75 ×10^-3 µM` | Fitting | 同上 |  |  |
| P08 | `K_TX_NTP` | `80 µM` | Brenda (EC 2.7.7.6) | 同上 |  |  |
| P09 | `K_TL_nt` | `226 ± 16 µM` | Fitting | 同上 |  |  |
| P10 | `K_TL_RNA` | `0.32 ± 0.02 µM` | Fitting / 与 Eq.(29) 一致 | repo 应作为 derived QC quantity，不应作为独立 RHS 参数 |  |  |
| P11 | `K_TL_AT` | `10 µM` | Estimated | 数值、单位、origin 一致 |  |  |
| P12 | `K_TL_NTP` | `10 µM` | Estimated | 同上 |  |  |
| P13 | `K_RS_A` | `23 µM` | Brenda (avg.) | 同上 |  |  |
| P14 | `K_RS_T` | `0.7 µM` | Brenda (avg.) | 同上 |  |  |
| P15 | `K_RS_NTP` | `200 µM` | Brenda (avg.) | 同上 |  |  |
| P16 | `K_EN_CP` | `200 µM` | Brenda (EC 2.7.2.3) | 同上 |  |  |
| P17 | `K_EN_NXP` | `40 µM` | Brenda (EC 2.7.2.3) | 同上 |  |  |

---

## 12. Fig.4 条件、坐标与曲线身份

| ID | 原文位置 | 原文检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| F401 | PDF p.13 最后一段 + p.14 Fig.4 caption | GFP 长度 `L=238`; DNA = `6.8, 1.7, 0.34 nM` | `parameters.json` → `L`, `fig4_conditions_nM`; benchmark runner | 三个 DNA 条件和 L 完全一致 |  |  |
| F402 | PDF p.14, Fig.4 caption | experimental = dotted；calculated = continuous | `docs/audit/manual_fig4_audit_protocol.md`; `digitize_fig4.m` | 曲线身份说明一致 |  |  |
| F403 | PDF p.14, Fig.4 caption | color: 0.34 nM blue, 1.7 nM green, 6.8 nM red | `run_fig4_benchmark.m`; manual audit protocol | 颜色映射一致 |  |  |
| F404 | PDF p.14, Fig.4 caption | top = `[nt]`; bottom = `[a]` | benchmark figure/CSV | repo Fig.4 reproduction 的两个 panel 变量一致 |  |  |
| F405 | PDF p.14, Fig.4 caption | actual mRNA = y-axis `[nt]/(3L)`；actual protein = `[a]/L` | observable mapping + benchmark docs | repo 没把 `[nt]` 直接标成 mRNA molecules，也没把 `[a]` 直接标成 protein molecules |  |  |
| F406 | PDF p.13-14 | 论文说 nt curves fit quite well；a curves 不完全满意但得到 sigmoid | `docs/validation/benchmark_v0.md`; `docs/project/benchmark_registry.md` | repo 不得把 Fig.4 说成“实验完美验证” |  |  |
| F407 | PDF p.14 Fig.4 | 人工盲读 48 个点（3 DNA × 2 panels × 8 times） | `data/manual_audit/fig4_human_digitization_template.csv` | 在不看 simulation 的情况下填完；再比较 simulation 是否落入人工读图误差 |  |  |

### Fig.4 人工盲读结果文件

- 我的文件：`data/manual_audit/fig4_human_digitization_________________.csv`
- 是否在读图时隐藏 simulation：`Y / N`：________
- 48 点是否全部完成：`Y / N`：________
- 是否存在超出人工读图误差的点：`Y / N`：________
- 若有，列出：____________________________________________________________

---

## 13. 论文文字数值 anchors

| ID | 原文位置 | 原文值/描述 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| A01 | PDF p.16, Sect.4.1 | standard/non-diluted PURE 在 4 h 蛋白 yield = `0.58 µM` | `results/runs/<run_id>/benchmark_summary.json`; 6.8 nM `qc.json` | 比较 **protein molecule concentration**，即 `a/L`，不能直接拿 `[a]` 比 0.58 |  |  |
| A02 | PDF p.21, Eq.(33) | `chi_e = n_NTP[NTP] + [CP]` | `simulate_pure_literature_reference.m` → energy bookkeeping | 能量定义一致 |  |  |
| A03 | PDF p.21, Eq.(34) | `-d chi_e/dt = V_TX + 2V_TL + V_RS` | `simulate...local_qc` | 必须有 `2*V_TL` |  |  |
| A04 | PDF p.21, Fig.8 narrative | `phi_RS ≈ 85%` at `t ~ 1 min` | `docs/project/benchmark_registry.md`; simulation-derived diagnostics | 比较约数，不要求机器精度 |  |  |
| A05 | PDF p.22, Fig.8 narrative | RS minimum rate at about `4 min` | 同上 | 比较时间位置，允许原文“about”的读图误差 |  |  |
| A06 | PDF p.22, Fig.8 narrative | after ~30 min: `phi_TL ≈24%`, `phi_RS ≈12%`, sum ≈`36%`, `phi_TX ≈64%` | `docs/project/benchmark_registry.md`; simulation diagnostics | 分项和合计分别比较 |  |  |
| A07 | PDF p.23, Fig.9 text | at DNA=6.8 nM: `Q_TX=74%`, `Q_TL=15%`, `Q_RS=11%` | `results/runs/<run_id>/benchmark_summary.json`; 6.8 nM `qc.json` | 用 percentage-point difference 比较；确认定义为积分 `V_TX`, `2V_TL`, `V_RS` |  |  |
| A08 | PDF p.24, Table 4 entry 1 | standard PURE: `Q_TX=74%`, `Q_TL+Q_RS=26%`, ratio `(Q_TL+Q_RS)/Q_TX=0.35` | benchmark docs/results | 从 repo 数值自行计算并比较 |  |  |

---

## 14. Source assumptions / 不可伪装成原文明示的信息

| ID | 原文位置 | 检查项 | Repo 对应位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|---|
| AS01 | PDF p.12 Table 1 + Sect.3 | NXP/nt/AT/a/C 的初值没有在 Table 1 逐项列为 0 | `parameters.json` → corresponding initial conditions | repo 必须把这些 0 表述为推断/模型初始化决定，而不是“Table 1 明确给出” |  |  |
| AS02 | PDF p.11, Sect.2.5 末 | 论文讨论 closed system、资源随时间耗尽；没有给具体 reactor volume 数值 | `model_manifest.json` → boundary/assumptions | repo 可写 batch/fixed-volume concentration formulation，但不能虚构具体体积 |  |  |
| AS03 | PDF p.5-14 | B1 equations 中没有温度/pH/Mg²⁺显式动力学项 | `docs/project/benchmark_registry.md` | 若记录为 “not specified / not used by this model” 则一致；不能擅自补数值 |  |  |
| AS04 | PDF p.13 最后一段 | 作者提到可用 Hill `v=3.465` 得到稍好 a-curve fit，但明确**没有引入正式模型** | `model_definition.json` → V_TL | B1 不能加入 Hill coefficient |  |  |

---

## 15. Canonical definition → generated RHS 一致性

这部分不是和论文新增科学内容比较，而是检查 repo 内部是否从同一份模型定义生成代码。

| ID | 检查项 | Repo 位置 | 怎么比较 | 结果 Y/N | 备注 |
|---|---|---|---|---|---|
| CG01 | canonical rate laws 与论文核对完成后，generated RHS 必须来自 canonical definition | `models/literature_reference/model_definition.json` → `generation`; `matlab/codegen/generate_pure_literature_reference.m` | 删除/备份 generated RHS 后重新生成，`git diff` 应无数学差异 |  |  |
| CG02 | `state_codegen` 与 `stoichiometry.matrix` 表达同一组 ODE | `model_definition.json` | 人工抽查至少 NTP、NXP、T、AT 四行 |  |  |
| CG03 | generated RHS 中 Eq.(5),(8),(10),(14),(20),(21),(24) 与 PDF 对应式一致 | `matlab/generated/rhs_pure_literature_reference.m` | 随机抽查这些关键式，逐符号比较 |  |  |

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

