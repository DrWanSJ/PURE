# Human B1 Audit

> 目的：只保留**必须由人判断**的 B1 科学审核。
>
> 审核方式统一为：
>
> **原文先看懂 → 打开指定 Repo 文件 → 搜指定字段 → 只比较“原文是否被正确抄入/表述” → 填 Y/N。**
>
> 数值进入 MATLAB、RHS 是否同步、ODE/stoichiometry 是否一致、守恒是否成立等机械检查，由测试负责，不再要求人工逐行查代码。

---

## 0. 审核记录

- 审核人：____________________
- 日期：2026-09-22
- 审核 commit：____________________
- 原文：`references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE.pdf`
- 机器测试 commit（应与审核 commit 一致）：____________________
- 机器测试结果：`PASS`（用户本地运行两个 test suites，`allPassed = 1`）

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

时，下面这些内容不需要再人工逐项检查：

- Table 1 / Table 2 参数进入 MATLAB 后是否正确；
- `n_NTP=4`、`n_A=20`、`n_T=46`、`n_T/n_A=2.3`；
- 六个 rate laws；
- ODE Eqs. (20)–(27)；
- stoichiometry matrix；
- 五条守恒关系；
- `mRNA=nt/(3L)`、`protein=a/L`；
- `K_TL_RNA=K_TL_nt/(3L)`；
- `model_definition.json` → generated RHS 同步；
- deterministic repeatability、nonnegativity、短程数值 sanity checks。

机器 PASS 只能证明：

> Repo 与当前冻结的 canonical definition / 参数文件一致。

它不能独立证明：

> canonical definition / 参数文件最初就是从论文正确读出来的。

所以人工审核只做下面 H01–H07。

---

# 2. Human-only checklist

## H01 — 模型范围与核心方程的原文语义

### 原文看哪里

PDF p.5–11：

- Sect. 2–2.5；
- Fig. 2–3；
- Eqs. (1)–(27)。

先人工确认论文表达的是：

- deterministic coarse-grained ODE；
- 四个主模块：TX / RS / TL / EN；
- effective Michaelis–Menten / rectangular-hyperbolic rate laws；
- `nt`、`a` 是 polymerized monomer concentrations，不是 molecule concentrations；
- `NTP`、`A`、`T` 使用 average concentration，并通过 multiplicity bookkeeping 处理总量；
- 正式模型包含 TX、RS、TL、EN 和两个 degradation processes。

### Repo 跟什么比较

先打开：

```text
models/literature_reference/model_definition.json
```

依次搜索：

```text
"purpose"
"states"
"rates"
```

重点看：

- `purpose` 是否仍声明为 Mavelli 2015 的 literal translation；
- `states` 中 `NTP`、`A`、`T` 的 `doc` 是否写成 average concentration；
- `nt`、`a` 是否写成 polymerized nucleotide / amino-acid units；
- `rates` 是否正好包含：
  `V_TX`、`V_nt_deg`、`V_RS`、`V_TL`、`V_TL_deg`、`V_EN`。

再打开：

```text
models/literature_reference/model_manifest.json
```

搜索：

```text
"scope_statement"
"model_type"
"assumptions"
```

确认没有把 B1 改成别的模型，也没有偷偷增加新机制。

### H01 只判断什么

你只判断：

> **论文的模型身份和变量语义，有没有被 Repo 正确描述。**

Repo 数学式真正生成得对不对，由机器测试负责。

- 结果 `Y / N`：`Y`
- 备注：____________________________________________________________

---

## H02 — Table 1 / Table 2 的原始数值抄录

### 原文看哪里

PDF p.12–13：

- Table 1；
- Table 2；
- Sect. 3 / Fig. 4 附近的 GFP 长度 `L=238`。

### Repo 主文件

只需要打开：

```text
models/literature_reference/parameters.json
```

然后依次搜索：

```text
"protein"
"parameters"
"initial_conditions"
```

### A. Table 1 怎么比

论文 Table 1 与 Repo 应对应：

| 原文项目 | Repo 位置 | 应看到 |
|---|---|---:|
| DNA | `initial_conditions.DNA` + `fig4_conditions_nM` | 0.34 / 1.7 / 6.8 nM 条件 |
| TXcat | `parameters.TXcat` | 0.1 µM |
| TLcat | `initial_conditions.TLcat` | 2.2 µM，来源 fitting |
| RScat | `parameters.RScat` | 0.16 µM |
| ENcat | `parameters.ENcat` | 0.08 µM |
| A | `initial_conditions.A` | 300 µM |
| T | `initial_conditions.T` | 1.9 µM |
| NTP | `initial_conditions.NTP` | 1500 µM |
| CP | `initial_conditions.CP` | 20000 µM |

DNA 的 `value=null` 是因为它是 per-run fixed input；真正的 Fig. 4 三个条件在：

```json
"fig4_conditions_nM": [0.34, 1.7, 6.8]
```

### B. Table 2 怎么比

在 `"parameters"` 中检查 6 个 kinetic constants：

```text
k_TX       1.67
k_TL       0.085
k_RS       6.2
k_EN       100
k_nt_deg   7.92e-5
k_TL_deg   1.86e-4
```

再检查 10 个 independent Michaelis–Menten constants：

```text
K_TX_DNA    0.005
K_TX_NTP    80
K_TL_nt     226
K_TL_AT     10
K_TL_NTP    10
K_RS_A      23
K_RS_T      0.7
K_RS_NTP    200
K_EN_CP     200
K_EN_NXP    40
```

同时看每项的：

```text
"origin"
"source"
```

确认论文中的：

- Fitting → Repo `origin: "fitted"`；
- BRENDA → Repo `origin: "literature"`，且 `source` 写明 BRENDA；
- Estimated → Repo `origin: "estimated"`。

### C. GFP 长度

搜索：

```text
"length_aa_L"
```

应看到：

```json
"length_aa_L": 238
```

### D. K_TL_RNA 为什么不在 10 个独立 MM 参数中

搜索：

```text
"derived_quantities"
"K_TL_RNA"
```

应看到它按 Eq. (29) 定义为：

```text
K_TL_RNA = K_TL_nt/(3*L)
```

即：

```text
226 / (3*238) = 0.31653 µM
```

与论文 Table 2 的 `0.32 ± 0.02 µM` 一致，因此它在 Repo 中是 derived QC quantity，不是第 11 个独立 MM 参数。

### H02 只判断什么

你只判断：

> **论文 Table 1 / Table 2 / L=238 是否被正确抄进 parameters.json，参数来源有没有读错。**

参数进入 MATLAB 后有没有变，由机器测试负责。

- 结果 `Y / N`：`Y`
- 备注：____________________________________________________________

---

## H03 — 原文没有明确给出的初始化 / 边界假设

### 原文看哪里

PDF p.10–12：

- Eqs. (15)–(19)；
- Sect. 2.5；
- Sect. 3 开头。

重点注意：

- 论文列出 newly-created species，但 Table 1 没逐项写 `NXP/nt/AT/a/C = 0`；
- Eq. (15) 和 Eq. (19) 只写了 degradation species，没有把它们定义成反馈状态；
- 论文讨论 closed system / resource depletion，但没有给具体 reactor volume 数字。

### Repo 跟什么比较

先打开：

```text
models/literature_reference/parameters.json
```

搜索：

```text
"NXP"
"nt"
"AT"
"a"
"C"
"D_nt"
"D_TLcat"
```

确认：

- `NXP`、`nt`、`AT`、`a`、`C` 的初值为 0；
- 这些条目的 `source` 写成 newly-created / inferred initialization，而不是声称“Table 1 明确给出 0”；
- `D_nt`、`D_TLcat` 被明确描述成 auxiliary/accounting integrators。

再打开：

```text
models/literature_reference/model_manifest.json
```

搜索：

```text
"boundary"
"D_nt"
"D_TLcat"
"newly-created species"
```

确认：

```text
batch
fixed_volume
well_mixed
```

只是模型 formulation，没有虚构具体 reactor volume。

### H03 只判断什么

你判断：

> **这些 Repo 里的“重建/初始化决定”是否合理，而且有没有诚实地区分“论文明确写了”与“为了实现模型而推断”。**

- 结果 `Y / N`：`Y`
- 备注：____________________________________________________________

---

## H04 — 论文明确省略的机制

### 原文看哪里

- PDF p.6：PPi / Pi；
- PDF p.9：GFP maturation；
- PDF p.13：Hill exponent `v=3.465` 的说明。

人工先确认论文确实表达：

- PPi hydrolysis 不显式积分；
- GFP maturation 没加入正式模型；
- Hill `v=3.465` 只是作者提到的 empirical alternative，没有纳入正式模型；
- B1 Eqs. (5)–(14) 没有温度、pH、Mg²⁺ 的显式 rate-law 输入。

### Repo 跟什么比较

打开：

```text
models/literature_reference/model_manifest.json
```

搜索：

```text
"PPi hydrolysis"
"GFP maturation"
"assumptions"
```

应看到 PPi hydrolysis 和 GFP maturation 都明确写成 omitted / not explicitly integrated。

再打开：

```text
models/literature_reference/model_definition.json
```

搜索：

```text
"V_TL"
```

确认正式 `V_TL` 仍是论文 Eq. (10) 的 rectangular-hyperbolic 形式，而不是 Hill `v=3.465` 版本。

温度 / pH / Mg²⁺ 的记录看：

```text
docs/project/benchmark_registry.md
```

搜索：

```text
Temperature / pH / Mg²⁺
```

应写成：

```text
not specified in the paper; not needed by this model
```

### H04 只判断什么

你判断：

> **Repo 对“论文省略了什么”的文字说明，有没有忠实反映原文。**

这些机制是否真的没有进入 RHS，由机器测试负责。

- 结果 `Y / N`：`Y`
- 备注：____________________________________________________________

---

## H05 — Fig. 4 图注、曲线身份与论文自己的结论

### 原文看哪里

PDF p.13–14：

- Fig. 4 caption；
- Fig. 4 前后的 Sect. 3 文字。

人工确认：

- DNA = 0.34 / 1.7 / 6.8 nM；
- top = `[nt]`；
- bottom = `[a]`；
- experimental = dotted；
- calculated = continuous；
- 颜色：0.34 blue，1.7 green，6.8 red；
- 论文说 transcription curves reproduce quite well；
- protein / `a` curves not completely satisfactory，但获得 sigmoidal time course。

### Repo 跟什么比较

DNA 条件与 GFP 长度：

```text
models/literature_reference/parameters.json
```

搜索：

```text
"fig4_conditions_nM"
"length_aa_L"
```

Fig. 4 曲线身份与颜色规则：

```text
docs/audit/manual_fig4_audit_protocol.md
```

搜索：

```text
experimental = dotted
calculated = continuous
0.34 nM blue
1.7 nM green
6.8 nM red
```

论文对拟合质量的描述以及 Repo 的证据等级：

```text
docs/project/benchmark_registry.md
```

搜索：

```text
quite well
not completely satisfactory
Fig. 4 comparison
```

再看：

```text
docs/project/evidence_levels.json
```

搜索：

```text
fig4_independent_human_audit
experimental_data_validation
fig4_human_visual_review
```

确认 Repo 没把当前状态写成“独立实验验证已经完成”。

### H05 只判断什么

你判断：

> **论文 Fig. 4 的图注、颜色、panel、作者自己的结论，有没有在 Repo 里被正确描述。**

- 结果 `Y / N`：`Y`
- 备注：____________________________________________________________

---

## H06 — 论文后文的 quantitative anchors

### 原文看哪里

PDF p.16、p.21–24：

- Sect. 4.1；
- Eq. (33)–(35)；
- Fig. 8 narrative；
- Fig. 9；
- Table 4 entry 1。

确认论文确实给出：

- standard PURE、DNA = 6.8 nM、4 h protein yield 约 `0.58 µM`；
- `chi_e = n_NTP[NTP] + [CP]`；
- `-d chi_e/dt = V_TX + 2V_TL + V_RS`；
- `phi_RS ≈ 85%` at ~1 min；
- RS minimum ~4 min；
- ~30 min 时 `phi_TL≈24%`、`phi_RS≈12%`、总和约 36%；
- 6.8 nM 时 `Q_TX=74%`、`Q_TL=15%`、`Q_RS=11%`；
- Table 4 reference ratio `(Q_TL+Q_RS)/Q_TX ≈ 0.35`。

### Repo 跟什么比较

打开：

```text
docs/project/benchmark_registry.md
```

搜索标题：

```text
Quantitative anchors available from the paper TEXT
```

这里就是 Repo 冻结的“从论文文字读出的 anchors”。

逐条把原文和这一节比较。

可再交叉看：

```text
docs/validation/benchmark_v0.md
```

搜索：

```text
Tier 3a
0.58
74
85
280
36
```

但这里主要是 simulation 与 paper anchors 的数值比较，**不是你 H06 的人工任务**。

### H06 只判断什么

你只判断：

> **benchmark_registry.md 里记录的 paper-text anchors 是否忠实来自论文。**

simulation 是否复现这些 anchors，由 benchmark/QC 负责。

- 结果 `Y / N`：`Y`
- 备注：____________________________________________________________

---

## H07 — 是否要求 strict blind Fig. 4 人工读图

这不是方程正确性问题，而是**证据等级决策**。

### Repo 当前状态看哪里

打开：

```text
docs/project/evidence_levels.json
```

搜索：

```text
fig4_independent_human_audit
fig4_human_visual_review
experimental_data_validation
```

当前应区分：

- 已有 human visual review；
- 该 review 是 non-blind；
- strict independent blind Fig. 4 audit 仍是 pending；
- experimental data validation 仍不是 true。

完整 blind protocol 在：

```text
docs/audit/manual_fig4_audit_protocol.md
```

### 你需要做的只是选择

- [x] **不要求** strict blind Fig. 4 audit。B1 保持为文献方程复现 / simulation benchmark，不宣称独立 experimental validation。
- [ ] **要求** strict blind Fig. 4 audit。按 `manual_fig4_audit_protocol.md` 完成独立读图。

选择理由：本阶段 B1 的目标是忠实复现 Mavelli et al. (2015) 文献模型并核对方程、参数和数值实现；不以独立实验数据验证为目标，因此不要求 strict blind Fig. 4 audit。

如果选择“要求”，再填写：

- 人工读图文件：____________________________________________________
- 48 点是否完成：`Y / N`：________
- 是否发现超出人工读图误差的点：`Y / N`：________

---

# 3. 最终人工判定

## 前提

- 两个 MATLAB test suites 均通过：`Y`
- H01：`Y`
- H02：`Y`
- H03：`Y`
- H04：`Y`
- H05：`Y`
- H06：`Y`
- H07 已作出明确选择：`Y`（不要求 strict blind Fig. 4 audit；B1 仅作文献模型复现）

## 判定

- 是否存在任何需要修复的 `N`：`N`
- 若有，对应 H-ID：无
- 是否允许把 B1 标记为 `human_audited`：`Y`
- 审核人签名 / 缩写：____________________
- 日期：2026-09-22

## N 项处理记录

| ID | 差异描述 | 类型：原文歧义 / Repo 错误 / 文档措辞 | 修复 commit | 修复后复核 Y/N |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |

---

# 4. 审核边界

B1 的 `human_audited` 只表示：

1. 人工确认了论文模型语义、参数表、关键文字 anchors；
2. 人工确认了 Repo 对论文未明确事项的表述是诚实的；
3. 机器确认 Repo 实现与冻结定义一致。

它**不自动表示**：

- Fig. 4 已完成 strict blind independent validation；
- Stögbauer 2012 experimental data 已被验证；
- effective Michaelis–Menten rate laws 可直接当作 SSA propensities；
- B1 已经是最终 `PURE_resource_core`；
- D6 rank / left-nullspace / conservation reduction 已经完成。
