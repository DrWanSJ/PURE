# SynCell 无细胞表达系统 —— 无量纲化推导与守恒律检验（审计修订版 v2）

> 生成日期：2026-09-21 · 参考时间尺度 τ = k_nt,deg·t · 依据 **Mavelli 2015 PURE** 原始物理 ODE；额外加入 `D_nt` 与 `D_TLcat` 两个仅用于守恒记账的积分器，不反馈任何速率
> 检验引擎：Wolfram Language 14.3（`wolframscript -script verify_wolfram_v2.wl`）
> 结论：**12 个 ODE 代数等价 + 5 条守恒律（有量纲层与无量纲层）全部符号恒等通过；数值残差 ≤ 3.3e-16**
> Multiplicity 约定：n_NTP = 4，n_A = 20，n_T = 46（符号保留，具体化亦复核）

---

## 0. 本次审计修订摘要

| 项 | 上一版结论 | 本次修正 |
|---|---|---|
| ① NTP/NXP 方程 n_NTP 因子不对称 | 标为"待确认，若非有意请统一" | **确认是模型本意，非缺陷**：[NTP] 是 4 种 NTP 平均浓度，[nt]/[NXP]/D_nt 是总池浓度，守恒量为 B_NTP = n_NTP[NTP]+[nt]+[NXP]+D_nt。保留 y₁/y₂ 推导不变。 |
| ② "A+AT 守恒需 n_A·c_A,0 = n_T·c_T,0（ρ_A=ρ_T）" | **错误判断，已删除** | AA 守恒真实形式为 B_AA = n_A[A] + [a] + n_T[AT]（**不是** [A]+[AT]）。A 用 n_A、T/AT 用 n_T 是正确的 multiplicity bookkeeping，不允许改动。ρ_A、ρ_T 是两个**独立**的尺度耦合比，**不令相等**。 |

---

## 1. 原始有量纲模型（Mavelli 2015 物理 ODE + 无反馈 accounting integrators）

速率：V_TX, V_RS（含 2.3 T 因子）, V_TL（含 2.3 AT 因子）, V_EN, V_nt,deg=k[nt], V_TL,deg=k[TLcat]

$$\text{NTP 计量：TX 消耗1, RS 消耗1, TL 消耗}\mathbf{2}\text{, EN 生成1}$$

$$
\begin{aligned}
\dot{[\text{NTP}]} &= (-V_{TX}-V_{RS}-2V_{TL}+V_{EN})/n_{NTP}\\
\dot{[\text{NXP}]} &= V_{RS}+2V_{TL}-V_{EN}\\
\dot{[\text{nt}]} &= V_{TX}-V_{nt,deg}\\
\dot{[A]} &= -V_{RS}/n_{A}\\
\dot{[T]} &= (-V_{RS}+V_{TL})/n_{T}\\
\dot{[AT]} &= (V_{RS}-V_{TL})/n_{T}\\
\dot{[a]} &= V_{TL}\\
\dot{[CP]} &= -V_{EN},\quad \dot{[C]}=V_{EN}\\
\dot{[\text{TLcat}]} &= -V_{TL,deg}\\
\dot{[D_{nt}]} &= V_{nt,deg},\quad \dot{[D_{TLcat}]}=V_{TL,deg}
\end{aligned}
$$

---

## 2. 无量纲变量（[X] = scale·y）

y₁=[NTP]/c_NTP,0 · y₂=[NXP]/(n·c) · y₃=[nt]/(n·c) · y₄=[A]/c_A,0 · y₅=[T]/c_T,0 · y₆=[AT]/c_T,0 · y₇=[a]/(n_A·c_A,0) · y₈=[CP]/c_CP,0 · y₉=[C]/c_CP,0 · y₁₀=[TLcat]/c_TL,0 · y₁₁=[D_nt]/(n·c) · y₁₂=[D_TLcat]/c_TL,0
（n=n_NTP, c=c_NTP,0）

---

## 3. 无量纲参数

- 速率组（统一尺度 = k_nt,deg·n_NTP·c_NTP,0）：μ_TX, μ_RS, μ_TL, μ_EN, μ_TL,deg=k_TL,deg/k_nt,deg
- 饱和常数 κ_X = K_X/(底物尺度)，2.3 吸收进 κ_RS,T、κ_TL,AT；对固定 DNA 输入，κ_TX,DNA = K_TX,DNA/[DNA]，因此 θ_DNA=1/(1+κ_TX,DNA)=[DNA]/(K_TX,DNA+[DNA])
- **独立的**尺度耦合比：ρ_A = n·c/(n_A·c_A,0)，ρ_T = n·c/(n_T·c_T,0)，ρ_C = n·c/c_CP,0
  —— ρ_A、ρ_T **互不约束**。

---

### 与 `docs/theory_notes.md` 中单方程记号的对应

此前手推 `nt` 方程使用 `\kappa_{TX,eff}` 表示当前 DNA 条件下的有效 TX capacity ratio。完整系统采用统一记号后，二者完全等价：

$$
\kappa_{TX,eff}=\mu_{TX}\theta_{DNA}.
$$

同时，$\kappa_{TX,NTP}=K_{TX,NTP}/c_{NTP,0}$ 的定义保持不变。

---

## 4. 无量纲速率

$$\tilde V_{TX}=\mu_{TX}\theta_{DNA}\frac{y_1}{\kappa_{TX,NTP}+y_1}$$
$$\tilde V_{RS}=\mu_{RS}\frac{y_4}{\kappa_{RS,A}+y_4}\frac{y_5}{\kappa_{RS,T}+y_5}\frac{y_1}{\kappa_{RS,NTP}+y_1}$$
$$\tilde V_{TL}=\mu_{TL}y_{10}\frac{y_3}{\kappa_{TL,nt}+y_3}\frac{y_6}{\kappa_{TL,AT}+y_6}\frac{y_1}{\kappa_{TL,NTP}+y_1}$$
$$\tilde V_{EN}=\mu_{EN}\frac{y_8}{\kappa_{EN,CP}+y_8}\frac{y_2}{\kappa_{EN,NXP}+y_2}$$

---

## 5. 最终无量纲方程组 dy_i/dτ

| # | y₁(NTP) | y₂(NXP) | y₃(nt) | y₄(A) | y₅(T) | y₆(AT) |
|---|---|---|---|---|---|---|
| ′ | −Ṽ_TX−Ṽ_RS−2Ṽ_TL+Ṽ_EN | Ṽ_RS+2Ṽ_TL−Ṽ_EN | Ṽ_TX−y₃ | −ρ_AṼ_RS | ρ_T(−Ṽ_RS+Ṽ_TL) | ρ_T(Ṽ_RS−Ṽ_TL) |

| # | y₇(a) | y₈(CP) | y₉(C) | y₁₀(TLcat) | y₁₁(D_nt) | y₁₂(D_TLcat) |
|---|---|---|---|---|---|---|
| ′ | ρ_AṼ_TL | −ρ_CṼ_EN | ρ_CṼ_EN | −μ_TL,deg·y₁₀ | y₃ | μ_TL,deg·y₁₀ |

**y₄–y₇ 复核确认**：y₄=−ρ_AṼ_RS、y₅=ρ_T(−Ṽ_RS+Ṽ_TL)、y₆=ρ_T(Ṽ_RS−Ṽ_TL)、y₇=ρ_AṼ_TL，ρ_A 与 ρ_T 各自独立出现。

---

## 6. 五条守恒律（有量纲 → 无量纲）

沿系统 d/dt（或 d/dτ）严格为 0，均经 Wolfram `FullSimplify` 验证：

| 守恒量 | 有量纲 | 无量纲 |
|---|---|---|
| Nucleotide | n_NTP[NTP]+[nt]+[NXP]+D_nt | y₁+y₂+y₃+y₁₁ |
| Amino-acid | n_A[A] + [a] + n_T[AT] | (y₄+y₇)/ρ_A + y₆/ρ_T |
| tRNA | n_T[T] + n_T[AT] | y₅+y₆ |
| CP | [CP]+[C] | y₈+y₉ |
| TLcat | [TLcat]+D_TLcat | y₁₀+y₁₂ |

### AA 守恒逐步符号验证（有量纲层，T2）
$$\frac{d}{dt}B_{AA}=n_A\underbrace{\!\left(-\tfrac{V_{RS}}{n_A}\right)}_{\dot A}+\underbrace{V_{TL}}_{\dot a}+n_T\underbrace{\left(\tfrac{V_{RS}-V_{TL}}{n_T}\right)}_{\dot{AT}}=-V_{RS}+V_{TL}+V_{RS}-V_{TL}=0$$

### tRNA 守恒逐步符号验证（T2）
$$\frac{d}{dt}B_{tRNA}=n_T\!\left(\tfrac{-V_{RS}+V_{TL}}{n_T}\right)+n_T\!\left(\tfrac{V_{RS}-V_{TL}}{n_T}\right)=0$$

无量纲 AA 不变量 (y₄+y₇)/ρ_A + y₆/ρ_T 沿流：
d/dτ = (−ρ_AṼ_RS+ρ_AṼ_TL)/ρ_A + ρ_T(Ṽ_RS−Ṽ_TL)/ρ_T = −Ṽ_RS+Ṽ_TL+Ṽ_RS−Ṽ_TL = 0 ✓

---

## 7. Wolfram Language 检验输出（verify_wolfram_v2.wl）

```
T2  dimensional conservation residuals: NTP / AA / tRNA / CP / TLcat  → 全 0 (True)
T1  per-ODE symbolic equivalence (12):  {1..12, 0, True}   → T1 ALL PASS: True
T3  dimensionless conservation (5):     全 0               → T3 ALL PASS: True
T4  numeric residuals (5 trials):       max|residual| = 3.33e-16 (< 1e-12) → True
T5  n_NTP=4, n_A=20, n_T=46 具体化:     B_NTP/B_AA/B_tRNA 残差 全 0
```

- **T1（代数等价性）**：把紧凑式 μ/κ/ρ 回填有量纲定义，与「dimensional→链式法则直推」逐式相减，12 式 FullSimplify 全 0。
- **T2/T3（模型结构一致性）**：原始 ODE 与声明的守恒律一致；无量纲守恒律系数正确，未假设任何 pool scale 相等。

---

## 8. 两个层次的区分（本次特别强调）

1. **dimensional → dimensionless 代数等价性**：由 T1 保证（12/12 = 0）。
2. **原始 ODE 与守恒律的结构一致性**：由 T2（有量纲）+ T3（无量纲）保证，且不要求 ρ_A=ρ_T 或 n_A·c_A,0=n_T·c_T,0。

**已彻底移除**上一版"A+AT 守恒需 ρ_A=ρ_T"的错误判断。除此之外未发现其他代数错误；原始 Mavelli 模型未作任何改动。

---

## 9. 文件

| 文件 | 用途 | 状态 |
|---|---|---|
| `verify_wolfram_v2.wl` | WL 14.3 五层检验（本文所有结果来源） | 本次新增 |
| `derive_dimensionless.py` | sympy 推导 + 数值校验 | ρ_A/ρ_T 独立，无错误逻辑，保留 |
| `derive_dimensionless.m` | MATLAB Symbolic Toolbox 推导（同构） | ρ_A/ρ_T 独立；已统一使用 MATLAB `subs`/`simplify` 语法并加入守恒检查 |

> 注：`.py`/`.m` 经 grep 审计，均以 n_A 除 A、以 n_T 除 T/AT，且 ρ_A、ρ_T、ρ_C 各自独立定义，**不存在** `rho_A==rho_T` 或 `n_A·c_A0==n_T·c_T0` 的隐含假设，无需修改。错误仅存在于旧版 Markdown 文档的叙述，已在本 v2 文档修正。
