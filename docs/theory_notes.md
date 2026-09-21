# 系统反应方程式

$$\text{NTP} \xrightarrow{\text{TXcat},\text{DNA}} \text{nt} + \text{PP}_i $$

$$\text{PP}_i \xrightarrow{\text{PPase}} 2\text{P}_i $$

$$\text{nt} \rightarrow \text{D}_\text{nt} $$

$$\text{A} + \text{T} + \text{NTP} \xrightarrow{\text{RScat}} \text{AT} + \text{NXP} $$

$$\text{AT} + 2 \text{NTP} \xrightarrow{\text{TLcat, nt}} \text{a} + \text{T} + 2 \text{NXP} $$

$$\text{TLcat} \rightarrow \text{D}_\text{TLcat} $$

$$\text{CP} + \text{NXP} \xrightarrow{\text{ENcat}} \text{C} + \text{NTP} $$

注意，这里 reaction (1) 的 NTP 与 (4), (5), (7) 的 NTP 需要区别对待。

TX：NTP 是聚合底物；

RS：ATP 被消耗，粗粒化进入 NXP pool，实际主要对应 ATP $\to$ AMP；

TL：GTP 被消耗，粗粒化进入 NXP pool，实际主要对应 GTP $\to$ GDP；

EN：利用 CP，把 lumped NXP pool 重新转化为 lumped NTP pool。

## 速率参数

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

## ODEs

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

## 物质守恒

$$
\begin{align}
B_{NTP}&=4[NTP]+[nt]+[NXP]+D_{nt}=constant \\
B_{AA}&=20[A]+[a]+46[AT]=constant \\
B_{tRNA}&=46[T]+46[AT]=constant \\
B_{CP}&=[CP]+[C]=constant \\
B_{TLcat}&=[TLcat]+D_{TLcat}=constant
\end{align}
$$

## 无量纲化

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


### nt 方程的无量纲化

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
