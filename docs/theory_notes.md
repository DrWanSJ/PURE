# PURE Literature Reference 理论笔记

> 范围：Mavelli et al. (2015) 的 `PURE_literature_reference`，以及仓库为守恒审计添加的无反馈 accounting integrators。本文只整理既有 B1 方程、守恒与无量纲化，不引入新的机制。

## 1. 反应网络

$$
\text{NTP} \xrightarrow{\text{TXcat},\text{DNA}} \text{nt} + \text{PP}_i
$$

$$
\text{PP}_i \xrightarrow{\text{PPase}} 2\text{P}_i
$$

$$
\text{nt} \rightarrow \text{D}_\text{nt}
$$

$$
\text{A} + \text{T} + \text{NTP} \xrightarrow{\text{RScat}} \text{AT} + \text{NXP}
$$

$$
\text{AT} + 2 \text{NTP} \xrightarrow{\text{TLcat, nt}} \text{a} + \text{T} + 2 \text{NXP}
$$

$$
\text{TLcat} \rightarrow \text{D}_\text{TLcat}
$$

$$
\text{CP} + \text{NXP} \xrightarrow{\text{ENcat}} \text{C} + \text{NTP}
$$

注意：同一个 coarse-grained `NTP` pool 在不同模块中的物理角色不同，不能把各模块的 NTP 消耗解释成同一种微观化学步骤。

- **TX**：NTP 是聚合底物。

- **RS**：ATP 被消耗，粗粒化进入 NXP pool，实际主要对应 ATP $\to$ AMP。

- **TL**：GTP 被消耗，粗粒化进入 NXP pool，实际主要对应 GTP $\to$ GDP。

- **EN**：利用 CP，把 lumped NXP pool 重新转化为 lumped NTP pool。

## 2. 速率律

$$
\begin{align}
V_{TX} &=k_{TX}C_{TXcat}\frac{[DNA]}{K_{TX,DNA}+[DNA]}\frac{[NTP]}{K_{TX,NTP}+[NTP]} \\
V_{RS} &=k_{RS}C_{RScat}\frac{[A]}{K_{RS,A}+[A]}\frac{2.3[T]}{K_{RS,T}+2.3[T]}\frac{[NTP]}{K_{RS,NTP}+[NTP]} \\
V_{TL} &=k_{TL}[TLcat]\frac{[nt]}{K_{TL,nt}+[nt]}\frac{2.3[AT]}{K_{TL,AT}+2.3[AT]}\frac{[NTP]}{K_{TL,NTP}+[NTP]} \\
V_{EN} &=k_{EN}C_{ENcat}\frac{[CP]}{K_{EN,CP}+[CP]}\frac{[NXP]}{K_{EN,NXP}+[NXP]} \\
V_{nt,deg} &=k_{nt,deg}[nt] \\
V_{TL,deg} &=k_{TL,deg}[TLcat]
\end{align}
$$

## 3. 有量纲 ODE

以下 `D_nt` 和 `D_TLcat` 是仓库添加的无反馈 accounting integrators，用于显式闭合守恒账本；它们不是原文中额外的独立物理动力学状态，也不进入任何 rate law。

$$
\begin{align}
\frac{d[\text{NTP}]}{dt} &= \frac{-V_{\text{TX}} - 2V_{\text{TL}} - V_{\text{RS}} + V_{\text{EN}}}{n_{\text{NTP}}} \\
\frac{d[\text{NXP}]}{dt} &= 2V_{\text{TL}} + V_{\text{RS}} - V_{\text{EN}} \\
\frac{d[nt]}{dt} &= V_{\text{TX}} - V_{\text{nt,deg}} \\
\frac{d[\text{A}]}{dt} &= -\frac{V_{\text{RS}}}{n_{\text{A}}} \\
\frac{d[\text{T}]}{dt} &= -\frac{d[\text{AT}]}{dt} = \frac{-V_{\text{RS}} + V_{\text{TL}}}{n_{\text{T}}} \\
\frac{d[a]}{dt} &= V_{\text{TL}} \\
-\frac{d[\text{CP}]}{dt} &= \frac{d[\text{C}]}{dt} = V_{\text{EN}} \\
\frac{d[\text{TLcat}]}{dt} &= -V_{\text{TL,deg}} \\
\frac{d[\text{D}_{\text{nt}}]}{dt} &= V_{\text{nt,deg}} \\
\frac{d[\text{D}_{\text{TLcat}}]}{dt} &= V_{\text{TL,deg}}
\end{align}
$$

## 3.1 从反应账本到化学计量矩阵

D6 使用 stoichiometric matrix（化学计量矩阵）。它没有引入新的生物机制，只是把上面的 6 个动力学过程统一整理成“每个反应会让每个状态增加或减少多少”的账本。

状态顺序固定为

$$
\mathbf x=
\begin{bmatrix}
NTP\\
NXP\\
nt\\
A\\
T\\
AT\\
a\\
CP\\
C\\
TLcat\\
D_{nt}\\
D_{TLcat}
\end{bmatrix}.
$$

反应速率顺序固定为

$$
\mathbf V=
\begin{bmatrix}
V_{TX}\\
V_{nt,deg}\\
V_{RS}\\
V_{TL}\\
V_{TL,deg}\\
V_{EN}
\end{bmatrix}.
$$

这里每个 $V$ 表示对应过程当前进行得有多快。例如 $V_{RS}$ 是氨酰化速率，$V_{TL}$ 是翻译速率。

### 3.1.1 $S_{prediv}$：先写“每次反应真正增减几个 equivalent”

先忽略 NTP、A、T、AT 是平均浓度这一点，只按反应式本身记录一次反应事件的净变化：

$$
S_{prediv}
=
\begin{bmatrix}
-1&0&-1&-2&0& 1\\
 0&0& 1& 2&0&-1\\
 1&-1&0&0&0&0\\
 0&0&-1&0&0&0\\
 0&0&-1&1&0&0\\
 0&0& 1&-1&0&0\\
 0&0&0&1&0&0\\
 0&0&0&0&0&-1\\
 0&0&0&0&0& 1\\
 0&0&0&0&-1&0\\
 0&1&0&0&0&0\\
 0&0&0&0&1&0
\end{bmatrix}.
$$

矩阵的 12 行依次对应

$$
NTP, NXP, nt, A, T, AT, a, CP, C, TLcat, D_{nt}, D_{TLcat},
$$

6 列依次对应

$$
TX, nt\ degradation, RS, TL, TLcat\ degradation, EN.
$$

例如第一行

$$
[-1, 0, -1, -2, 0, +1]
$$

表示：

- TX 每发生一次，消耗 1 个 NTP equivalent；
- RS 每发生一次，消耗 1 个 NTP equivalent；
- TL 每发生一次，消耗 2 个 NTP equivalents；
- EN 每发生一次，生成 1 个 NTP equivalent。

同理，RS 这一列体现

$$
A+T+NTP\rightarrow AT+NXP,
$$

所以在 NTP、NXP、A、T、AT 上分别是

$$
-1, +1, -1, -1, +1.
$$

这就是 pre-divisor 的含义：**还没有把平均浓度定义中的 4、20、46 除进去。**

### 3.1.2 为什么 NTP、A、T、AT 还要除以 4、20、46

论文里的这些状态不是总 pool，而是平均浓度：

$$
4[NTP]
$$

代表四种 NTP 的总 pool，

$$
20[A]
$$

代表 20 种 amino acid 的总 pool，

$$
46[T],qquad 46[AT]
$$

分别代表 46 种 uncharged / charged tRNA 的总 pool。

因此如果一次 RS 反应真正消耗 1 个 amino-acid equivalent，那么

$$
\frac{d(20A)}{dt}=-V_{RS},
$$

所以

$$
\frac{dA}{dt}=-\frac{V_{RS}}{20}.
$$

同样地，

$$
\frac{dT}{dt}=-\frac{V_{RS}}{46},
\qquad
\frac{dAT}{dt}=+\frac{V_{RS}}{46},
$$

而 NTP 的变化需要除以 4。

把这些 divisor 写成

$$
D=
\operatorname{diag}
(4,1,1,20,46,46,1,1,1,1,1,1),
$$

那么

$$
D^{-1}
=
\operatorname{diag}
\left(
\frac14,1,1,\frac1{20},\frac1{46},\frac1{46},1,1,1,1,1,1
\right).
$$

因此真正对应论文 ODE 状态定义的矩阵是

$$
\boxed{
S_{eff}=D^{-1}S_{prediv}.
}
$$

显式写为

$$
S_{eff}
=
\begin{bmatrix}
-\frac14&0&-\frac14&-\frac12&0& \frac14\\
0&0&1&2&0&-1\\
1&-1&0&0&0&0\\
0&0&-\frac1{20}&0&0&0\\
0&0&-\frac1{46}&\frac1{46}&0&0\\
0&0&\frac1{46}&-\frac1{46}&0&0\\
0&0&0&1&0&0\\
0&0&0&0&0&-1\\
0&0&0&0&0&1\\
0&0&0&0&-1&0\\
0&1&0&0&0&0\\
0&0&0&0&1&0
\end{bmatrix}.
$$

于是完整 12 状态 ODE 可以统一写成

$$
\boxed{
\dot{\mathbf x}
=
S_{eff}\mathbf V.
}
$$

这句话的物理含义就是：

> 每个状态现在变化多快 = 每个生物反应现在有多快 × 该反应对这个状态造成的净增加或减少。

例如 NTP 这一行直接给出

$$
\frac{d[NTP]}{dt}
=
-\frac14V_{TX}
-\frac14V_{RS}
-\frac12V_{TL}
+\frac14V_{EN},
$$

也就是

$$
\frac{d[NTP]}{dt}
=
\frac{-V_{TX}-V_{RS}-2V_{TL}+V_{EN}}{4}.
$$

这与论文 ODE 完全一致。

PPi hydrolysis

$$
PP_i\rightarrow2P_i
$$

不进入这个 $12\times6$ 矩阵，因为 PPi 和 Pi 都不是当前动态状态，而且该过程没有作为第七个动力学速率被积分。它只保留为化学背景。

## 4. 五条物质 / 组分账本守恒

以下五条是当前 B1 模型中具有直接物理含义的 material / moiety balances。它们对应论文 Eqs. (15)–(19)；仓库用无反馈的 $D_{nt}$ 与 $D_{TLcat}$ 显式闭合两个降解账本。

$$
\begin{align}
B_{NTP}&=4[NTP]+[nt]+[NXP]+D_{nt}=\mathrm{const}
&&\text{（nucleotide-residue / base bookkeeping）} \\
B_{AA}&=20[A]+[a]+46[AT]=\mathrm{const}
&&\text{（amino-acid residue bookkeeping）} \\
B_{tRNA}&=46[T]+46[AT]=\mathrm{const}
&&\text{（tRNA pool bookkeeping）} \\
B_{CP}&=[CP]+[C]=\mathrm{const}
&&\text{（creatine moiety bookkeeping）} \\
B_{TLcat}&=[TLcat]+D_{TLcat}=\mathrm{const}
&&\text{（TLcat bookkeeping）}
\end{align}
$$

这里的“守恒”是在当前 coarse-grained 模型分辨率下成立的组分账本，不应扩大解释为完整元素守恒、电荷守恒或热力学能量守恒。

### 4.1 论文的高能资源账本 $\chi_e$

论文另外定义

$$
\chi_e
=
n_{NTP}[NTP]+[CP]
=
4[NTP]+[CP].
$$

$\chi_e$ 表示当前模型中“还没有被表达过程消耗掉的 energy-rich phosphate resource”的浓度账本。它的单位仍是浓度，不是 J，也不是 Gibbs free energy。

由有量纲 ODE 直接得到

$$
-\frac{d\chi_e}{dt}
=
V_{TX}+2V_{TL}+V_{RS}.
$$

其中 EN 不出现在右端，因为 EN 只把高能磷酸资源从 CP 转移回 NTP；在 $4[NTP]+[CP]$ 这个账本中属于内部转移。

### 4.2 高能资源总账：剩余资源 + 已消耗资源

把论文定义的剩余高能资源写成

$$
\chi_e=4[NTP]+[CP].
$$

TX 已经消耗的高能资源，在当前 coarse-grained 账本中由

$$
[nt]+D_{nt}
$$

记录，因为

$$
\frac{d}{dt}\left([nt]+D_{nt}\right)=V_{TX}.
$$

RS / TL 已经消耗的高能资源，更直接地由 exhausted-nucleotide / regeneration-product 账本

$$
[NXP]+[C]
$$

记录。虽然 EN 会把 NXP 再生为 NTP，但同时生成 C，因此

$$
\frac{d}{dt}\left([NXP]+[C]\right)
=
V_{RS}+2V_{TL}.
$$

于是

$$
\frac{d}{dt}
\left(
[nt]+D_{nt}+[NXP]+[C]
\right)
=
V_{TX}+V_{RS}+2V_{TL}
=
-\frac{d\chi_e}{dt}.
$$

因此有

$$
\boxed{
4[NTP]+[CP]+[nt]+D_{nt}+[NXP]+[C]
=
\mathrm{const}
}
$$

其最直观的解释是

$$
\boxed{
\text{剩余高能资源}
+
\text{TX 已经消耗的资源}
+
\text{RS/TL 已经消耗的资源}
=
\text{常数}
}
$$

但这条总账**不是新的独立守恒关系**，因为它正好等于已有两条账本之和：

$$
B_{NTP}+B_{CP}
=
4[NTP]+[nt]+[NXP]+D_{nt}+[CP]+[C].
$$

所以它主要用于解释论文的 energy bookkeeping，而不是增加 left-nullspace 的独立维数。

### 4.3 第六个线性独立结构关系：RS/TL energy-cost coupling

由当前 ODE，

$$
\frac{d}{dt}\left([NXP]+[C]\right)
=
V_{RS}+2V_{TL}.
$$

另一方面，

$$
\frac{d}{dt}\left(3[a]+n_T[AT]\right)
=
3V_{TL}+V_{RS}-V_{TL}
=
V_{RS}+2V_{TL}.
$$

因此

$$
\boxed{
\frac{d}{dt}
\left(
[NXP]+[C]-3[a]-n_T[AT]
\right)
=
0
}
$$

即在当前 reference multiplicity $n_T=46$ 下，

$$
\boxed{
I_6
=
[NXP]+[C]-3[a]-46[AT]
=
\mathrm{const}.
}
$$

这条关系与前面的五条 published material / moiety balances 线性独立：例如前五条中只有 $B_{NTP}$ 含有 $[NXP]$，但 $B_{NTP}$ 同时必然带有 $4[NTP]$；因此不能用前五条的线性组合得到一个 NTP 系数为 0、NXP 系数为 1 的 $I_6$。

对当前标准初值

$$
[NXP]_0=[C]_0=[a]_0=[AT]_0=0,
$$

所以

$$
I_6=0,
$$

并可写成更直观的形式

$$
\boxed{
[NXP]+[C]
=
3[a]+46[AT].
}
$$

物理解释：

- 左侧 $[NXP]+[C]$：RS / TL 历史上累计产生的 exhausted-nucleotide equivalents；EN 只在 NXP 与 C 之间搬运这笔历史账，因此不会改变其和；
- 右侧 $46[AT]$：仍停留在 charged-tRNA pool 中的 aminoacylation 成本，每个 charged tRNA 对应 1 个 NTP-equivalent；
- 右侧 $3[a]$：每个已经进入蛋白的 amino-acid residue 对应 1 个 aminoacylation NTP-equivalent + 2 个 translation NTP-equivalents。

因此，$I_6$ 最适合解释为 **RS/TL energy-cost coupling invariant** 或 **exhausted-nucleotide accounting invariant**。它仍然不是完整热力学能量守恒。

### 4.4 D6 MATLAB 结构验证：rank 与完整 left-nullspace basis

2026-09-22 使用上节人工核对后的 $S_{eff}$ 在 MATLAB 中计算：

$$
\boxed{
\operatorname{rank}(S_{eff})=6.
}
$$
这里 $S_{eff}$ 有 12 行、6 列。其 6 列分别对应 TX、nt degradation、RS、TL、TLcat degradation、EN 六个反应方向。rank = 6 表示这六个反应方向彼此线性独立，没有一个反应的状态变化模式可以由其余反应方向线性组合得到。

根据 rank-nullity relation，

$$
\dim\ker(S_{eff}^{T})
=
12-\operatorname{rank}(S_{eff})
=
12-6
=
6.
$$
物理上，这表示 12 个状态虽然都可以随时间变化，但它们被 6 条彼此独立的结构约束限制，因此系统只允许沿 6 个独立的 stoichiometric directions 运动。

把前面五条 published material / moiety balances 与第六条 $I_6$ 写成行向量，得到

$$
L=
\begin{bmatrix}
4&1&1&0&0&0&0&0&0&0&1&0\\
0&0&0&20&0&46&1&0&0&0&0&0\\
0&0&0&0&46&46&0&0&0&0&0&0\\
0&0&0&0&0&0&0&1&1&0&0&0\\
0&0&0&0&0&0&0&0&0&1&0&1\\
0&1&0&0&0&-46&-3&0&1&0&0&0
\end{bmatrix}.
$$
六行依次对应

$$
B_{NTP},quad
B_{AA},quad
B_{tRNA},quad
B_{CP},quad
B_{TLcat},quad
I_6.
$$
MATLAB 验证得到

$$
L S_{eff}\approx 0,
$$
其中浮点计算的最大残差约为

$$
2.78\times10^{-17},
$$
属于机器舍入误差；同时

$$
\boxed{
\operatorname{rank}(L)=6.
}
$$
因此：

1. 每一行都满足 $l_i S_{eff}=0$，即六条关系对所有 6 个反应方向都保持不变；
2. $L$ 的 6 行彼此线性独立；
3. left nullspace 的维数本身也是 6。

所以可以得到 D6 的正式结构结论：

$$
\boxed{
\text{这六条可读关系构成 }\ker(S_{eff}^{T})\text{ 的完整 basis。}
}
$$
也就是说，当前 12-state augmented B1 representation 的完整独立结构约束已经找全，不再存在第七条与它们线性独立的守恒 / accounting relation。

这一步完成了 **rank + complete left-nullspace basis**。随后已选定 $z=[NTP,nt,A,AT,CP,TLcat]^T$，于 2026-09-22 完成 exact conservation reduction 与三组 DNA 下的 full 12-state / reduced 6-state 全轨迹验证；2026-09-23 又完成 dimensional/dimensionless 全轨迹逆变换验证，见 [D6 conservation report](theory/conservation_report.md)。

## 5. 无量纲化

$$
\begin{aligned}
y_1 &= \frac{[\text{NTP}]}{c_{\text{NTP},0}}, &
y_2 &= \frac{[\text{NXP}]}{n_{\text{NTP}}c_{\text{NTP},0}}, &
y_3 &= \frac{[\text{nt}]}{n_{\text{NTP}}c_{\text{NTP},0}}, \\
y_4 &= \frac{[\text{A}]}{c_{\text{A},0}}, &
y_5 &= \frac{[\text{T}]}{c_{\text{T},0}}, &
y_6 &= \frac{[\text{AT}]}{c_{\text{T},0}}, \\
y_7 &= \frac{[\text{a}]}{n_{\text{A}}c_{\text{A},0}}, &
y_8 &= \frac{[\text{CP}]}{c_{\text{CP},0}}, &
y_9 &= \frac{[\text{C}]}{c_{\text{CP},0}}, \\
y_{10} &= \frac{[\text{TLcat}]}{c_{\text{TLcat},0}}, &
y_{11} &= \frac{[\text{D}_{\text{nt}}]}{n_{\text{NTP}}c_{\text{NTP},0}}, &
y_{12} &= \frac{[\text{D}_{\text{TLcat}}]}{c_{\text{TLcat},0}}.
\end{aligned}
$$

选择 mRNA degradation 作为参考慢时间尺度，因为 nt 是 TX 与 TL 之间的核心耦合状态，同时其一阶降解给出了一个明确、状态无关的特征时间。

即

$$
t^* = \frac{1}{k_{\text{nt,deg}}},
\qquad
\tau = \frac{t}{t^*} = k_{\text{nt,deg}} t.
$$


### 5.1 `nt` 方程示例

由

$$
\frac{d[nt]}{dt}=V_{TX}-V_{nt,deg}
$$

以及

$$
[nt]=n_{NTP}c_{NTP,0}y_3,
\qquad
\tau=k_{nt,deg}t,
$$

可得

$$
\frac{d y_3}{d \tau}
=
\frac{k_{TX}C_{TXcat}}
{k_{nt,deg}n_{NTP}c_{NTP,0}}
\frac{[DNA]}{K_{TX,DNA}+[DNA]}
\frac{y_1}
{\dfrac{K_{TX,NTP}}{c_{NTP,0}}+y_1}
-y_3.
$$

定义

$$
\rho_1=k_{TX}C_{TXcat}.
$$

$\rho_1$ 表示 TX 的本征最大催化能力，即在 DNA 和 NTP 均充分饱和时的 $V_{TX,max}$，在本模型中为常数。

定义

$$
\rho_2=k_{nt,deg}n_{NTP}c_{NTP,0}.
$$

$\rho_2$ 表示一个理论降解速率上界：假设初始总体 nucleotide pool 全部转化为 $nt$，则在一阶降解律下对应的最大 $nt$ 降解速率。在当前缩放下，它同时也是由 characteristic concentration $n_{NTP}c_{NTP,0}$ 与 characteristic time $1/k_{nt,deg}$ 共同确定的 degradation-rate scale。

定义

$$
\rho_3=
\frac{[DNA]}{K_{TX,DNA}+[DNA]}.
$$

$\rho_3$ 表示 DNA template saturation factor；由于本模型中 DNA 为固定输入，因此在单次给定 DNA 条件的仿真中为常数。

于是

$$
\frac{d y_3}{d \tau}
=
\frac{\rho_1\rho_3}{\rho_2}
\frac{y_1}
{\dfrac{K_{TX,NTP}}{c_{NTP,0}}+y_1}
-y_3.
$$

再定义无量纲比值

$$
R_{TX}
=
\frac{\rho_1}{\rho_2},
$$

其物理意义为 TX 的本征最大合成能力与上述 $nt$ 理论最大降解速率尺度之比。

定义

$$
\kappa_{TX,eff}
=
R_{TX}\rho_3
=
\frac{\rho_1\rho_3}{\rho_2},
$$

其物理意义为：在当前 DNA 条件下、且 NTP 处于饱和极限时，effective maximum transcription rate 与 $nt$ 理论最大降解速率尺度之比。

与完整系统记号的对应是 $R_{TX}=\mu_{TX}$、$\rho_3=\theta_{DNA}$，因此 $\kappa_{TX,eff}=\mu_{TX}\theta_{DNA}$。这里的理论上界使用当前 reference 初值 `nt=NXP=D_nt=0`；若初始其他 nucleotide 池非零，总量上界应使用完整 $B_{NTP}(0)$。

定义

$$
\kappa_{TX,NTP}
=
\frac{K_{TX,NTP}}{c_{NTP,0}},
$$

其物理意义为 TX 对 NTP 的半饱和浓度相对于初始 NTP 平均浓度尺度的比值。$\kappa_{TX,NTP}\ll1$ 表示初始 NTP 相对于半饱和尺度较充足；$\kappa_{TX,NTP}\gg1$ 表示 TX 更容易受到 NTP availability 限制。

最终，

$$
\boxed{
\frac{d y_3}{d \tau}
=
\kappa_{TX,eff}
\frac{y_1}{\kappa_{TX,NTP}+y_1}
-y_3
}
$$


---

## 6. 完整 12 状态无量纲模型（审计定稿）

本节是在上面的 $nt$ 单方程手推基础上，对全部 12 个状态统一无量纲化后的结果。这里保留前面的手推记号作为推导记录；完整系统统一使用 $\mu$、$\kappa$、$\rho_A,\rho_T,\rho_C$ 与 $\theta_{DNA}$。

统一时间尺度与反应速率尺度为

$$
\tau=k_{nt,deg}t,
\qquad
V_* = k_{nt,deg}n_{NTP}c_{NTP,0}.
$$

### 6.1 无量纲速率参数

$$
\begin{aligned}
\mu_{TX}
&=
\frac{k_{TX}C_{TXcat}}
{k_{nt,deg}n_{NTP}c_{NTP,0}},
&
\mu_{RS}
&=
\frac{k_{RS}C_{RScat}}
{k_{nt,deg}n_{NTP}c_{NTP,0}},
\\
\mu_{TL}
&=
\frac{k_{TL}c_{TLcat,0}}
{k_{nt,deg}n_{NTP}c_{NTP,0}},
&
\mu_{EN}
&=
\frac{k_{EN}C_{ENcat}}
{k_{nt,deg}n_{NTP}c_{NTP,0}},
\\
\mu_{TL,deg}
&=
\frac{k_{TL,deg}}{k_{nt,deg}}.
\end{aligned}
$$

其中 $\mu_{TX},\mu_{RS},\mu_{TL},\mu_{EN}$ 都表示对应模块的 catalytic-capacity scale 相对于统一 nucleotide degradation-rate scale 的比值；$\mu_{TL,deg}$ 是 TLcat degradation 与 nt degradation 的时间尺度比。

DNA 在本 reference model 中是固定输入，定义

$$
\theta_{DNA}
=
\frac{[DNA]}{K_{TX,DNA}+[DNA]}.
$$

因此前面单独推导得到的

$$
\kappa_{TX,eff}
=
\mu_{TX}\theta_{DNA}.
$$

### 6.2 无量纲饱和常数

$$
\begin{aligned}
\kappa_{TX,NTP}
&=
\frac{K_{TX,NTP}}{c_{NTP,0}},
&
\kappa_{RS,A}
&=
\frac{K_{RS,A}}{c_{A,0}},
\\
\kappa_{RS,T}
&=
\frac{K_{RS,T}}{(n_T/n_A)c_{T,0}},
&
\kappa_{RS,NTP}
&=
\frac{K_{RS,NTP}}{c_{NTP,0}},
\\
\kappa_{TL,nt}
&=
\frac{K_{TL,nt}}{n_{NTP}c_{NTP,0}},
&
\kappa_{TL,AT}
&=
\frac{K_{TL,AT}}{(n_T/n_A)c_{T,0}},
\\
\kappa_{TL,NTP}
&=
\frac{K_{TL,NTP}}{c_{NTP,0}},
&
\kappa_{EN,CP}
&=
\frac{K_{EN,CP}}{c_{CP,0}},
\\
\kappa_{EN,NXP}
&=
\frac{K_{EN,NXP}}{n_{NTP}c_{NTP,0}}.
\end{aligned}
$$

在 Mavelli reference 参数下

$$
\frac{n_T}{n_A}
=
\frac{46}{20}
=
2.3.
$$

这里 $2.3$ 只对应 T / AT multiplicity bookkeeping，不意味着 $\rho_A=\rho_T$。

### 6.3 尺度耦合比

$$
\rho_A
=
\frac{n_{NTP}c_{NTP,0}}
{n_Ac_{A,0}},
\qquad
\rho_T
=
\frac{n_{NTP}c_{NTP,0}}
{n_Tc_{T,0}},
\qquad
\rho_C
=
\frac{n_{NTP}c_{NTP,0}}
{c_{CP,0}}.
$$

$\rho_A,\rho_T,\rho_C$ 只反映不同 coarse-grained pool reference scales 之间的换算关系。特别地，$\rho_A$ 与 $\rho_T$ 是独立参数，不要求相等。

### 6.4 无量纲反应速率

$$
\widetilde V_{TX}
=
\mu_{TX}\theta_{DNA}
\frac{y_1}{\kappa_{TX,NTP}+y_1},
$$

$$
\widetilde V_{RS}
=
\mu_{RS}
\frac{y_4}{\kappa_{RS,A}+y_4}
\frac{y_5}{\kappa_{RS,T}+y_5}
\frac{y_1}{\kappa_{RS,NTP}+y_1},
$$

$$
\widetilde V_{TL}
=
\mu_{TL}y_{10}
\frac{y_3}{\kappa_{TL,nt}+y_3}
\frac{y_6}{\kappa_{TL,AT}+y_6}
\frac{y_1}{\kappa_{TL,NTP}+y_1},
$$

$$
\widetilde V_{EN}
=
\mu_{EN}
\frac{y_8}{\kappa_{EN,CP}+y_8}
\frac{y_2}{\kappa_{EN,NXP}+y_2}.
$$

这些 $\widetilde V$ 均以 $V_*$ 归一。

### 6.5 最终无量纲 ODE：显式 $dy_i/d\tau=f_i(\mathbf y)$

记

$$
\mathbf y=(y_1,y_2,\ldots,y_{12})^T,
\qquad
\tau=k_{nt,deg}t.
$$

将上面的 $\widetilde V_{TX},\widetilde V_{RS},\widetilde V_{TL},\widetilde V_{EN}$ 全部代回，可得

$$
\boxed{
\begin{aligned}
\frac{dy_1}{d\tau}
={}&
-\mu_{TX}\theta_{DNA}
\frac{y_1}{\kappa_{TX,NTP}+y_1}
\\
&-\mu_{RS}
\frac{y_4}{\kappa_{RS,A}+y_4}
\frac{y_5}{\kappa_{RS,T}+y_5}
\frac{y_1}{\kappa_{RS,NTP}+y_1}
\\
&-2\mu_{TL}y_{10}
\frac{y_3}{\kappa_{TL,nt}+y_3}
\frac{y_6}{\kappa_{TL,AT}+y_6}
\frac{y_1}{\kappa_{TL,NTP}+y_1}
\\
&+\mu_{EN}
\frac{y_8}{\kappa_{EN,CP}+y_8}
\frac{y_2}{\kappa_{EN,NXP}+y_2}.
\end{aligned}
}
$$

$$
\boxed{
\begin{aligned}
\frac{dy_2}{d\tau}
={}&
\mu_{RS}
\frac{y_4}{\kappa_{RS,A}+y_4}
\frac{y_5}{\kappa_{RS,T}+y_5}
\frac{y_1}{\kappa_{RS,NTP}+y_1}
\\
&+2\mu_{TL}y_{10}
\frac{y_3}{\kappa_{TL,nt}+y_3}
\frac{y_6}{\kappa_{TL,AT}+y_6}
\frac{y_1}{\kappa_{TL,NTP}+y_1}
\\
&-\mu_{EN}
\frac{y_8}{\kappa_{EN,CP}+y_8}
\frac{y_2}{\kappa_{EN,NXP}+y_2}.
\end{aligned}
}
$$

$$
\boxed{
\frac{dy_3}{d\tau}
=
\mu_{TX}\theta_{DNA}
\frac{y_1}{\kappa_{TX,NTP}+y_1}
-y_3
}
$$

$$
\boxed{
\frac{dy_4}{d\tau}
=
-\rho_A\mu_{RS}
\frac{y_4}{\kappa_{RS,A}+y_4}
\frac{y_5}{\kappa_{RS,T}+y_5}
\frac{y_1}{\kappa_{RS,NTP}+y_1}
}
$$

$$
\boxed{
\begin{aligned}
\frac{dy_5}{d\tau}
={}&
\rho_T
\Bigg[
-\mu_{RS}
\frac{y_4}{\kappa_{RS,A}+y_4}
\frac{y_5}{\kappa_{RS,T}+y_5}
\frac{y_1}{\kappa_{RS,NTP}+y_1}
\\
&\qquad
+\mu_{TL}y_{10}
\frac{y_3}{\kappa_{TL,nt}+y_3}
\frac{y_6}{\kappa_{TL,AT}+y_6}
\frac{y_1}{\kappa_{TL,NTP}+y_1}
\Bigg].
\end{aligned}
}
$$

$$
\boxed{
\begin{aligned}
\frac{dy_6}{d\tau}
={}&
\rho_T
\Bigg[
\mu_{RS}
\frac{y_4}{\kappa_{RS,A}+y_4}
\frac{y_5}{\kappa_{RS,T}+y_5}
\frac{y_1}{\kappa_{RS,NTP}+y_1}
\\
&\qquad
-\mu_{TL}y_{10}
\frac{y_3}{\kappa_{TL,nt}+y_3}
\frac{y_6}{\kappa_{TL,AT}+y_6}
\frac{y_1}{\kappa_{TL,NTP}+y_1}
\Bigg].
\end{aligned}
}
$$

$$
\boxed{
\frac{dy_7}{d\tau}
=
\rho_A\mu_{TL}y_{10}
\frac{y_3}{\kappa_{TL,nt}+y_3}
\frac{y_6}{\kappa_{TL,AT}+y_6}
\frac{y_1}{\kappa_{TL,NTP}+y_1}
}
$$

$$
\boxed{
\frac{dy_8}{d\tau}
=
-\rho_C\mu_{EN}
\frac{y_8}{\kappa_{EN,CP}+y_8}
\frac{y_2}{\kappa_{EN,NXP}+y_2}
}
$$

$$
\boxed{
\frac{dy_9}{d\tau}
=
\rho_C\mu_{EN}
\frac{y_8}{\kappa_{EN,CP}+y_8}
\frac{y_2}{\kappa_{EN,NXP}+y_2}
}
$$

$$
\boxed{
\frac{dy_{10}}{d\tau}
=
-\mu_{TL,deg}y_{10}
}
$$

$$
\boxed{
\frac{dy_{11}}{d\tau}
=
y_3
}
$$

$$
\boxed{
\frac{dy_{12}}{d\tau}
=
\mu_{TL,deg}y_{10}
}
$$

因此可以统一写成

$$
\boxed{
\frac{d\mathbf y}{d\tau}
=
\mathbf f(\mathbf y;\boldsymbol\pi)
}
$$

其中 $\boldsymbol\pi$ 表示全部无量纲参数组合。该显式形式与前面的 compact $\widetilde V$ 写法完全等价，但更适合后续直接计算 Jacobian、rank、局部线性化与独立坐标降维。

这里 NTP / NXP 方程的不对称是原模型定义导致的：$[NTP]$ 是 $n_{NTP}=4$ 种 NTP 的平均浓度，而 $[NXP]$、$[nt]$、$D_{nt}$ 使用 overall pool concentration。

### 6.6 无量纲守恒量

由有量纲守恒律直接得到

$$
I_{NTP}
=
y_1+y_2+y_3+y_{11},
$$

$$
I_{AA}
=
\frac{y_4+y_7}{\rho_A}
+
\frac{y_6}{\rho_T},
$$

$$
I_{tRNA}
=
y_5+y_6,
\qquad
I_{CP}
=
y_8+y_9,
\qquad
I_{TLcat}
=
y_{10}+y_{12}.
$$

沿上述无量纲 ODE，

$$
\frac{dI_{NTP}}{d\tau}
=
\frac{dI_{AA}}{d\tau}
=
\frac{dI_{tRNA}}{d\tau}
=
\frac{dI_{CP}}{d\tau}
=
\frac{dI_{TLcat}}{d\tau}
=
0.
$$

注意 AA 守恒是

$$
n_A[A]+[a]+n_T[AT]=\mathrm{const},
$$

而不是 $[A]+[AT]=\mathrm{const}$。因此 A 方程除以 $n_A$，T / AT 方程除以 $n_T$ 是正确的 multiplicity bookkeeping。

除上述五条 material / moiety balances 外，4.3 节的第六个线性独立结构关系在当前无量纲变量下写成

$$
\boxed{
I_6
=
y_2
+
\frac{y_9}{\rho_C}
-
\frac{3y_7}{\rho_A}
-
\frac{y_6}{\rho_T}
=
\mathrm{const}.
}
$$

这是对

$$
[NXP]+[C]-3[a]-n_T[AT]
$$

除以统一尺度 $n_{NTP}c_{NTP,0}$ 后得到的表达式。把完整无量纲 ODE 代入可直接得到

$$
\frac{dI_6}{d\tau}=0.
$$

对当前标准零初值，

$$
I_6=0,
$$

所以

$$
y_2+\frac{y_9}{\rho_C}
=
\frac{3y_7}{\rho_A}
+
\frac{y_6}{\rho_T}.
$$

另外，4.2 节的高能资源总账无量纲化后为

$$
y_1+y_2+y_3+y_{11}
+
\frac{y_8+y_9}{\rho_C}
=
\mathrm{const},
$$

它只是

$$
I_{NTP}+\frac{I_{CP}}{\rho_C},
$$

因此不是额外独立 invariant。
## 7. 验证状态

当前完整无量纲模型已经完成独立审计：

- Wolfram kernel：12/12 ODE 的 direct-vs-compact symbolic equivalence 均严格化简为 0；
- 论文 Eqs. (15)–(19) 对应的五条 dimensional material/accounting balances：5/5 通过；
- 对应的五条 dimensionless balances：5/5 通过；
- Wolfram 数值独立检查：5 trials × 12 equations，global max absolute residual $8.88\times10^{-16}$；
- Python / SymPy 与 MATLAB 路径均实际运行通过；
- MATLAB 与真实 generated RHS 的 5 × 12 比较最大残差约 $1.78\times10^{-15}$；
- accounting integrators $D_{nt},D_{TLcat}$ 已显式检查为 no-feedback states；
- 故障注入可识别错误 TL stoichiometry、错误 accounting mapping 与错误 $\rho_T$。

审计证据冻结在：

`docs/audit/dimensionless_20260921/REPORT.md`

因此，当前这套无量纲方程可以作为后续 conservation reduction、timescale analysis、QSSA / fast-slow analysis 的 validated baseline。

4.2 节的高能资源总账

$$
4[NTP]+[CP]+[nt]+D_{nt}+[NXP]+[C]=\mathrm{const}
$$

只是 $B_{NTP}+B_{CP}$，所以不增加独立维数。4.3 / 6.6 中记录的

$$
I_6=[NXP]+[C]-3[a]-46[AT]
$$

则是从已冻结 ODE 解析得到、且相对于前五条 published balances 线性独立的第六条结构关系；它不属于此前“5/5”审计的检查范围。

D6 的 rank 与完整 left-nullspace basis 已于 2026-09-22 用 MATLAB 验证：$\operatorname{rank}(S_{eff})=6$、$\operatorname{rank}(L)=6$、$LS_{eff}\approx0$（最大浮点残差约 $2.78\times10^{-17}$）。因此上述六条关系已经确认构成完整 left-nullspace basis。

**D6 complete（2026-09-23）**：

- rank complete；
- complete left nullspace complete；
- independent coordinates complete：$z=[NTP,nt,A,AT,CP,TLcat]^T$；
- exact conservation reduction complete；
- full/reduced trajectory validation complete；
- dimensional/dimensionless trajectory back-transform complete；
- [nondim_map.json](theory/nondim_map.json) complete。

本次直接复用已审计的 compact equations 和 scaling。两个 12-state 系统分别以 $t$ 与 $\tau=k_{nt,deg}t$ 为积分变量，在三组 Fig.4 DNA、0–14400 s、每 10 s 输出的完整网格上比较全部 12 个状态、6 个速率、mRNA 与 protein，预注册的归一化误差阈值均为 $10^{-6}$。四个 MATLAB suites 共 34 个测试全部通过；已有 12/12 符号等价和两层各 5 条守恒回归通过。数值结果、首轮失败与解析 Jacobian 修复、原始文件字节校验见 [trajectory audit](audit/nondim_trajectory_20260923/README.md)。

该完成状态仅表示当前 frozen B1 deterministic model 各表示的数学和数值等价；不建立 independent experimental validation，不扩展模型机制，也不冻结 `PURE_resource_core`。
