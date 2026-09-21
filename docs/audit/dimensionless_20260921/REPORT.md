# PURE literature-reference nondimensionalization 严格代码审计

审计日期：2026-09-21。入口版本：`1aed082`（完整 SHA 见 `provenance.json`）。范围为当前仓库方程及其无量纲化，不重新设计模型。原始 canonical JSON、参数、生成 RHS、模拟器和 `dimensionless_result.txt` 均未修改。

## A. PASS / FAIL summary

**修复后 PASS，且已在真实 Wolfram kernel、Python/SymPy、MATLAB 中运行。** 原版 Wolfram 的 12 式符号等价本身通过，但其退出码和数值检验独立性不足；原版 MATLAB 实际执行失败。因此原始整套验证包不能无条件标为全部通过。

| 项目 | 原版 | 修复后 |
|---|---|---|
| Wolfram 12 式符号等价 | PASS | PASS |
| 两层各 5 条守恒 | Wolfram PASS | 三种语言 PASS |
| Wolfram 失败时退出码 | FAIL：故障注入后仍为 0 | PASS：失败返回 1 |
| 数值测试先各自求值再相减 | FAIL：原版先形成符号差 | PASS：原始 RHS 数值路径独立求值 |
| 随机 multiplicity 对应 canonical RHS | FAIL：固定 2.3 而 n_A/n_T 随机 | PASS：统一使用 n_T/n_A |
| MATLAB 实际执行 | FAIL：Array sizes must match | PASS |
| Python 完整执行 | PASS（另一次首轮因展示用 factor 耗时而终止） | PASS |
| 源模型交叉检查 | 仅手写复刻，易共同遗漏 | PASS：读取 JSON/WL/Python/generated RHS 逐项比对 |

## B. WolframScript 实际运行状态

**EXECUTED LOCALLY**。先运行版本命令，再运行原版及修复版脚本；全部 stdout、stderr、退出码留存。

```powershell
wolframscript -version
wolframscript -script models/literature_reference/dimensionless/verify_wolfram_v2.wl
```

CLI 版本为 **WolframScript 1.13.0**；实际 kernel 为 **14.3.0 for Microsoft Windows (64-bit), July 8, 2025**。二者不能混称同一个版本号。

- [版本 stdout](wolframscript_version.stdout.txt)：退出码 0。
- [原版完整 stdout](wolfram_original.stdout.txt)：T1 12/12、T2 5/5、T3 5/5、T5 通过；报告的 T4 最大残差 `3.3306690738754696e-16`，退出码 0。该数值来自先符号相减的旧算法。
- [修复版完整 stdout](wolfram_fixed.stdout.txt)：上述检查以及 mapping/no-feedback/DNA 检查全通过，`AUDIT ALL PASS: True`，退出码 0，stderr 为空。
- 修复版 T4：seed=2026，5 trials × 12 equations = **60**，每一式残差都写入 stdout；**global max absolute residual = 8.881784197001252e-16 < 1e-12**。

## C. 12-equation symbolic equivalence

`direct_i` 确实来自原始 `rhs[[i]]`，先替换 `X_i=scale_i*y_i`，再除以 `scale_i*knd`。它在 compact 构造之前独立建立；没有由 compact 反向构造 direct。compact 的 18 个参数定义一次回填后，逐式 `FullSimplify[compactDim[[i]]-direct[[i]]]` 返回**精确整数 0**。

| i | 状态 / scale | Wolfram residual | MATLAB residual |
|---|---|---|---|
| 1 | NTP / c_NTP0 | 0 — PASS | 0 — PASS |
| 2 | NXP / (n_NTP c_NTP0) | 0 — PASS | 0 — PASS |
| 3 | nt / (n_NTP c_NTP0) | 0 — PASS | 0 — PASS |
| 4 | A / c_A0 | 0 — PASS | 0 — PASS |
| 5 | T / c_T0 | 0 — PASS | 0 — PASS |
| 6 | AT / c_T0 | 0 — PASS | 0 — PASS |
| 7 | a / (n_A c_A0) | 0 — PASS | 0 — PASS |
| 8 | CP / c_CP0 | 0 — PASS | 0 — PASS |
| 9 | C / c_CP0 | 0 — PASS | 0 — PASS |
| 10 | TLcat / c_TLcat0 | 0 — PASS | 0 — PASS |
| 11 | D_nt / (n_NTP c_NTP0) | 0 — PASS | 0 — PASS |
| 12 | D_TLcat / c_TLcat0 | 0 — PASS | 0 — PASS |

源模型核对：JSON 的 10 条 physical RHS 与脚本前 10 条逐项等价；`simulate_pure_literature_reference.m` 以 `[dydt; rates(2); rates(5)]` 添加两个记账积分器，正对应后两条。6 条 rate laws 全匹配，包括两个一阶降解。T/AT 的饱和项保持原有矩形双曲形式，TL 的 NTP 因子仍为一次饱和，计量系数 2 仅出现在 NTP/NXP 的 TL 通量项。

统一速率尺度 `V_star=k_ntdeg*n_NTP*c_NTP0`；4 个 capacity μ、`mu_TLdeg=k_TLdeg/k_ntdeg`、9 个底物 κ、DNA θ、3 个 ρ 全一致。注意 `V_TLdeg/V_star=mu_TLdeg*c_TLcat0*y10/(n_NTP*c_NTP0)`；应用 TLcat 自身状态尺度后，ODE 系数才为 `mu_TLdeg`，这里不存在漏乘浓度因子。

DNA 是固定输入：`theta=DNA/(K_TX_DNA+DNA)=1/(1+kappa_TX_DNA)`，后一个参数化要求 DNA>0；DNA=0 可直接使用 theta=0 或取极限。`kappa_TX,eff=mu_TX*theta` 与 theory notes 等价；已补充明确对应。**没有令 rho_A=rho_T，也没有令 n_A*c_A0=n_T*c_T0。**

Wolfram 语义审计：`Rule` 为立即规则，无 `RuleDelayed`；右侧不含待递归回填的无量纲符号，一次 `ReplaceAll` 足够。修复版检查回填后无残留 group symbol。私有 package context 隔离 Global 定义，`Block[{$Assumptions=True},…]` 防止外部假设污染；DNA 专用假设仅为 DNA、Kd 正数。`C` 是 System 内置符号，但这里只作为被替换的原子，没有赋值或函数调用，实际运行无碰撞。其余符号在独立 context 中。等价证明适用于各分母非零的域；实际物理域为正参数、正尺度、非负状态。

## D. Conservation checks

| 守恒量 | dimensional 导数 | compact dimensionless invariant | dI/dτ |
|---|---|---|---|
| NTP | n_NTP dNTP + dnt + dNXP + dD_nt = 0 | y1+y2+y3+y11 | 0 — PASS |
| AA | n_A dA + da + n_T dAT = 0 | (y4+y7)/rho_A + y6/rho_T | 0 — PASS |
| tRNA | n_T dT + n_T dAT = 0 | y5+y6 | 0 — PASS |
| CP | dCP+dC = 0 | y8+y9 | 0 — PASS |
| TLcat | dTLcat+dD_TLcat = 0 | y10+y12 | 0 — PASS |

两层各 **5/5 PASS**。Wolfram 无量纲层使用 `D[invariant, y_i]` 得到梯度，再与 compact RHS 点乘；不是直接打印预存的零。AA 账本是 `n_A*A+a+n_T*AT`，不是 `A+AT`。两个 D 状态仅为 accounting integrators，不反馈 rate law。

## E. Cross-language consistency

**Wolfram vs Python：PASS。** [source bridge stdout](python_fixed_source_bridge.stdout.txt) 包含实际执行 Python 后的结果，以及从 canonical JSON、WL 源表达式、Python 对象和生成 MATLAB RHS 读取的逐项符号比较。覆盖 6 条速率、12 RHS、12 scales、12 mappings、所有 μ/κ/ρ/θ 定义、12 compact ODE 和源模型独立链式法则；全部为 0。生成 RHS 内嵌的 canonical SHA-256 与实际 JSON 匹配。

本机 `python` 指向缺少 SymPy 的 Hermes 环境，因此使用已有的 `python3`（3.14.3 / SymPy 1.14.0），没有安装依赖或改变环境。修复版 Python 两层守恒通过，5×12 数值测试通过，**max absolute residual = 2.220446049250313e-16**，退出码 0。Python 的 compact rates 由自身 dimensional rates 推导，单独运行不能作为独立 rate-law 来源；source bridge 与 Wolfram 的手写 compact 对照补足了该证据链。

原版首轮执行因末尾展示用 `sp.factor(expr)` 长时间运行被人工终止，退出码 -1，不算完成；[原版独立回放 stdout](python_original_replay.stdout.txt) 则完整运行成功，耗时约 21.3 s、退出码 0，见 [回放状态](python_original_replay.status.json)。因此不把原版 Python 错判为恒定失败。修复只取消全式展示阶段的高成本 factor，单独 rate 的因式形式仍保留。

**Wolfram vs MATLAB：修复后 PASS。** 原版[stdout](matlab_original.stdout.txt)和[stderr](matlab_original.stderr.txt)记录第 107 行 `Array sizes must match`，退出码 1。修复版在 **R2025b Update 4 / Symbolic Math Toolbox 25.2** 实际运行：12 式符号残差全 0、两层守恒全过；独立调用真实 `rhs_pure_literature_reference` 的 5×12 比较，**max absolute residual = 1.7763568394002505e-15 < 1e-12**；现有 9 个模型测试全部通过，退出码 0。见[stdout](matlab_fixed.stdout.txt)。日志完整保留执行工具返回的文本；MATLAB 的部分中文提示在输出解码时成为替代字符，英文错误、调用栈行号、数值指标和退出码完整可读。UTF-8 阅读副本不能恢复已经丢失的中文字符。

MATLAB 的 rho 在表达式中直接展开为尺度比，Python/Wolfram 保留 rho 符号，代数意义一致。`dimensionless_result.txt` 是人工整理的 compact reference，不是原版 `.m` 的逐字输出；现已将 MATLAB 生成结果写至 `dimensionless_result_matlab.txt`，避免覆盖 reference。

## F. 发现的问题（按严重程度）

**CRITICAL：无。** 未发现当前物理 multiplicities 下的源模型方程或守恒账本错误。

**MAJOR（已修复）：**

1. **Wolfram 检查失败仍退出 0**（原版行 116、159 等仅 Print，无全局失败退出）。注入错误 TL 计量后 `T1 ALL PASS: False` 而退出 0，可使自动化伪通过。现聚合 T1–T5、mapping、DNA、no-feedback 后显式退出 0/1。
2. **MATLAB `factor` 返回因子向量，被当作 scalar rate**（原版行 90、107、148）。本机已复现数组尺寸错误。[MathWorks 官方语义](https://www.mathworks.com/help/symbolic/sym.factor.html)也明确输出为 symbolic vector。改为 `simplify` 并增加标量检查，输出端同样移除 `factor`。
3. **原版 T4 先做符号相减，削弱数值测试独立性**（原版 WL 行 154）。部分式子在代入前已归零，因此不能证明这部分 numerical evaluation 路径被测试。现原始 dimensional RHS 与 compact 分别求数值后才相减，记录全部 60 个残差。此缺陷不抹去原版 T1 的有效符号证明。
4. **固定 2.3 与随机 multiplicities 不一致**（三份脚本 s23 定义）。原版仅在 n_T/n_A=46/20 时对应 canonical RHS；原随机测试不能声称匹配一般 multiplicity。改为 n_T/n_A，并显式验证物理取值为 23/10；未改变 literature-reference 物理参数。

**MINOR（已修复或限定）：**

- 原版缺少独立的 passive-state mapping 检查：因 D_nt/D_TLcat 无反馈，错误 y11/y12 映射无法通过 RHS 比较发现。现检查 12 个映射，故障注入可正确失败。
- 原版 Python 没有 dimensional conservation 断言、全局绝对残差输出，使用 `1e-9*max(1,abs(direct))` 混合阈值。现增加前两项，改为绝对 `1e-12` 并检查有限值。
- 原版 MATLAB `muTLD=k_TLdeg/k_ntdeg` 导致最后两式仍混用有量纲符号；虽量纲比值正确，输出与完整 compact 记号不一致。改用已声明的 `mu_TLdeg`，并新增 12 式独立链式法则证明。
- MATLAB 默认覆盖人工 compact reference，输出无来源区分；现生成单独结果文件。Python 全式 factor 的运行时间不稳定，现取消该展示操作。
- 原 README 声称只有旧 Markdown 有错、脚本无需修改，与实际运行不符；已按本次证据更新。

**STYLE：** README 标题从 SynCell 更正为当前 PURE literature-reference；CLI 与 kernel 版本、生成结果与人工 reference 分别标明。没有为样式改写物理模型。

## G. 最小修复范围

改动仅在三份验证/推导脚本和相关说明；新增审计脚本、日志、MATLAB 生成结果。未修改 `model_definition.json`、`parameters.json`、`matlab/generated`、`matlab/src` 或原有测试。时间尺度、6 个 rate law 的物理形式、NTP 非对称 multiplicity bookkeeping、AA 守恒和两个独立 rho 均保持。

## H. 修复后重新运行

```powershell
wolframscript -script models/literature_reference/dimensionless/verify_wolfram_v2.wl
python3 docs/audit/dimensionless_20260921/audit_source_bridge.py
matlab -batch "run('C:/Users/CZ/Desktop/PURE/docs/audit/dimensionless_20260921/run_matlab_fixed.m')"
python3 docs/audit/dimensionless_20260921/check_wolfram_mutations.py
```

以上全部退出码 0。Python bridge 实际调用原 `derive_dimensionless.py`；另留存直接运行脚本的 stdout。MATLAB wrapper 先执行 `checkcode`，再运行推导、真实生成 RHS 比较和 9 个既有测试。`git diff --check` 通过。

5 项[故障注入/环境隔离结果](mutation_results.json)：原版错误计量暴露退出码缺陷；修复版拒绝错误计量、错误 y11/y12 mapping、错误 rho_T；污染 Global 符号并设置外部 `$Assumptions=False` 后仍可独立通过。所有变异脚本只保存在 ignored scratch，未更改正式模型。

**明确结论：修复后的当前 `verify_wolfram_v2.wl` 足以作为这份已对照并锁定源文件的 PURE literature-reference nondimensionalization 的独立符号验证证据，而且它已在本机真实 Wolfram kernel 中实际运行通过；不是仅凭静态代码审计作出的判断。** 源文件后续变化应重新运行 source bridge 和对应引擎，不能将本次证据自动迁移到其他版本。
