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
