# Human B1 Audit

> 目的：只保留**必须由人判断**的 B1 科学审核。凡是可以由确定性测试完成的 JSON / MATLAB / 数值一致性检查，不再要求人工逐项 `Ctrl+F`。
>
> 原则：**人负责确认“论文是什么意思、抄录依据是否正确”；机器负责确认“Repo 是否按这份定义实现且没有漂移”。**

## 0. 审核记录

- 审核人：____________________
- 日期：____________________
- 审核 commit：____________________
- 原文：`references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE.pdf`
- 机器测试 commit（应与审核 commit 一致）：____________________
- 机器测试结果：`PASS / FAIL`：________

---

## 1. 先跑机器检查

在项目根目录的 MATLAB 中运行：

```matlab
r1 = runtests('matlab/tests/test_pure_literature_reference.m');
r2 = runtests('matlab/tests/test_codegen_and_provenance.m');

allPassed = all([r1.Passed]) && all([r2.Passed])
```

只有当

```text
allPassed = 1
```

时，下面这些内容**不需要再人工逐项检查 Repo**：

- Table 1 / Table 2 已锁定的数值、`n_NTP=4`、`n_A=20`、`n_T=46`、`n_T/n_A=2.3`；
- 六个 rate laws：`V_TX`、`V_nt_deg`、`V_RS`、`V_TL`、`V_TL_deg`、`V_EN`；
- ODE Eqs. (20)–(27) 的符号、系数和 multiplicity divisors；
- 五条守恒关系的导数恒等式；
- `mRNA = nt/(3L)`、`protein = a/L`；
- `K_TL_RNA = K_TL_nt/(3L)`；
- canonical `model_definition.json` 与 generated RHS 同步；
- stoichiometry matrix 与 generated state equations 一致；
- 固定条件下的确定性重复运行、短程数值 sanity checks。

对应测试主要在：

- `matlab/tests/test_pure_literature_reference.m`
- `matlab/tests/test_codegen_and_provenance.m`

### 机器 PASS 不代表什么

这些测试只能证明：

> **Repo 与当前冻结的 canonical definition / 测试参考值一致。**

它们不能独立证明：

> **canonical definition / 测试参考值最初就是从论文正确读出来的。**

因此下面只保留这部分真正需要人工阅读原文的检查。

---

## 2. Human-only checklist

### H01 — 模型范围与核心方程的原文语义

**原文位置：** PDF p.5–11，Sect. 2–2.5，Eqs. (1)–(27)，Fig. 2–3。

人工确认：

- 模型确实是 deterministic coarse-grained ODE；
- 主模块为 TX / RS / TL / EN；
- 有效速率采用 Michaelis–Menten / rectangular-hyperbolic 形式；
- `nt`、`a` 是 polymerized monomer concentrations，不是 mRNA / protein molecule concentration；
- `NTP`、`A`、`T` 的 average-concentration 定义与 multiplicity bookkeeping 的理解无误；
- 六个 rate laws 与 Eqs. (20)–(27) 的数学结构已从原文人工确认。

- 结果 `Y / N`：________
- 备注：____________________________________________________________

> 若 H01 = Y 且机器测试 PASS，不再要求人工逐行查看 `model_definition.json` 或 `rhs_pure_literature_reference.m`。

---

### H02 — Table 1 / Table 2 的原始数值抄录

**原文位置：** PDF p.12–13，Table 1–2。

人工确认原文中的以下内容已经正确读出：

- Table 1 的 DNA、TXcat、TLcat、RScat、ENcat、A、T、NTP、CP；
- Table 2 的 6 个 kinetic constants 和 10 个 independent Michaelis–Menten constants；
- GFP 长度 `L=238`；
- 参数来源类别（fitting / BRENDA / estimated）没有被误读。

- 结果 `Y / N`：________
- 备注：____________________________________________________________

> 数值进入 `parameters.json`、loader 和 RHS 后是否一致，由机器测试负责。

---

### H03 — 原文没有明确给出的初始化 / 边界假设

人工判断以下 Repo 表述是否是**合理重建**，并且没有伪装成论文明确给出的事实：

1. `NXP`、`nt`、`AT`、`a`、`C` 初值设为 0；
2. `D_nt`、`D_TLcat` 是为了 Eq. (15)/(19) 守恒账本加入的 no-feedback accounting integrators；
3. 模型按 batch / well-mixed / fixed-volume concentration formulation 使用，但不虚构论文没有给出的具体 reactor volume。

**原文参考：** PDF p.10–12，Eqs. (15)–(19)，Sect. 2.5–3。

- 结果 `Y / N`：________
- 备注：____________________________________________________________

---

### H04 — 明确省略的机制没有被错误“补回”

**原文位置：** PDF p.6、p.9、p.13。

人工确认论文语义：

- PPi hydrolysis 不显式积分，因为 PPi / Pi 不反馈到其他反应；
- GFP maturation 在正式模型中省略；
- 作者提到 Hill exponent `v=3.465` 可改善 protein curve，但明确没有纳入正式模型；
- B1 方程中没有温度、pH、Mg²⁺ 的显式动力学状态或 rate-law 输入。

- 结果 `Y / N`：________
- 备注：____________________________________________________________

> Repo 中这些项是否真的没有进入 RHS，可以机器检查；这里仅确认“论文确实是这个意思”。

---

### H05 — Fig. 4 的图注、曲线身份与论文自己的结论

**原文位置：** PDF p.13–14，Fig. 4 及其前后文字。

人工确认：

- DNA 条件为 0.34 / 1.7 / 6.8 nM；
- top panel = `[nt]`，bottom panel = `[a]`；
- experimental = dotted，calculated = continuous；
- 0.34 / 1.7 / 6.8 nM 的颜色身份读图无误；
- 论文自己的评价是：transcription curves 较好，translation curves 并非完全满意，但得到 sigmoidal behavior；
- 因此 Repo 不应把 Fig. 4 描述成“实验完美验证”。

- 结果 `Y / N`：________
- 备注：____________________________________________________________

---

### H06 — 论文后文的 quantitative anchors

**原文位置：** PDF p.16、p.21–24，Sect. 4–5，Figs. 8–9，Table 4。

只需确认论文文字 / 表格确实给出这些参考量，不要求人工重算 Repo：

- standard PURE 4 h protein yield 约 `0.58 µM`；
- `chi_e = n_NTP[NTP] + [CP]`；
- `-d chi_e/dt = V_TX + 2V_TL + V_RS`；
- Fig. 8 中论文叙述的 `phi` 近似值与时间位置；
- DNA = 6.8 nM 时 `Q_TX=74%`、`Q_TL=15%`、`Q_RS=11%`；
- Table 4 reference case `Q_TL+Q_RS=26%`，ratio 约 `0.35`。

- 结果 `Y / N`：________
- 备注：____________________________________________________________

> Repo 是否数值复现这些 anchors，应由 benchmark / QC 代码计算，不要求人工从 CSV 一格格核对。

---

### H07 — 是否要求独立 blind Fig. 4 人工读图

这是**证据等级决策**，不是方程实现检查。

当前需要明确选择：

- [ ] **不要求** strict blind Fig. 4 audit；接受当前 B1 为文献方程复现 / simulation benchmark，不把它表述为独立实验验证。
- [ ] **要求** strict blind Fig. 4 audit；使用 `data/manual_audit/fig4_human_digitization_template.csv` 在隐藏 simulation 的条件下完成独立读图。

选择理由：__________________________________________________________

如果选择“要求”，再填写：

- 人工读图文件：____________________________________________________
- 48 点是否完成：`Y / N`：________
- 是否发现超出人工读图误差的点：`Y / N`：________

---

## 3. 最终人工判定

### 前提

- 两个 MATLAB test suites 均通过：`Y / N`：________
- H01：________
- H02：________
- H03：________
- H04：________
- H05：________
- H06：________
- H07 已作出明确选择：`Y / N`：________

### 判定

- 是否存在任何需要修复的 `N`：________
- 若有，对应 H-ID：________________________________________________
- 是否允许把 B1 标记为 `human_audited`：`Y / N`：________
- 审核人签名 / 缩写：____________________
- 日期：____________________

### N 项处理记录

| ID | 差异描述 | 类型：原文歧义 / Repo 错误 / 文档措辞 | 修复 commit | 修复后复核 Y/N |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |

---

## 4. 审核边界

B1 的 `human_audited` 只表示：

1. 人工确认了论文的模型语义、参数表和关键文字 anchors；
2. 机器确认 Repo 实现与冻结定义一致；
3. 对论文没有明确给出的重建假设进行了显式审查。

它**不自动表示**：

- Fig. 4 已完成独立 blind experimental validation；
- 该 effective Michaelis–Menten 模型可直接作为 SSA propensity；
- B1 已经是项目最终的 `PURE_resource_core`；
- 后续 D6 的守恒降维 / rank / independent-coordinate 工作已经完成。
