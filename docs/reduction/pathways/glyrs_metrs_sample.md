# PNAS2017 Reaction Pathway Atlas — GlyRS / MetRS 样板

源网：241 species / 968 reactions。Phase A：134 条原始反应；其余 834 条保留在底层 Petri 网，尚未进行路径重构。

本样板沿真实载体状态阅读。`PRODUCTIVE_PATH` 仅表示结构上到达 charged tRNA 并恢复酶，不表示通量大小；所有多底物必须同时具备。`NONZERO_PARAMETER` 只说明作者参考参数非零。

科学状态：`HUMAN_REVIEW_REQUIRED`。算法、来源及验收见 [protocol](pathway_first_protocol_v1.md)；检查结果和待决问题见 [review](glyrs_metrs_review.md)。

## 1. RS / AMINOACYLATION

### 1.1 GlyRS charging

路径共享的步骤采用链接引用；分支列表为同一前体的并行出口，不能逐行串联。

<a id="GlyRS-P01"></a>

#### GlyRS-P01 — Gly-first：tRNA 在活化前结合，charged tRNA 先释放

类型：`PRODUCTIVE_PATH;RETURN_LOOP`。起点 `GlyRS`；终点 `GlyRS`。

目标释放产物：`GlytRNAGlyGCC`；最后恢复 `GlyRS`。

01. **re0000000126** `[RS_binding]`：`GlyRS` → `GlyRS_Gly`

    同时消耗：`Gly`；另外释放：`0`（`0` 表示无）。

<a id="re0000000126"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000126` | `Gly + GlyRS -> GlyRS_Gly` | `RS_binding` | `RFAM_005` | `NONZERO_PARAMETER` |

02. **re0000000136** `[RS_binding]`：`GlyRS_Gly` → `GlyRS_Gly_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000136"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000136` | `ATP + GlyRS_Gly -> GlyRS_Gly_ATP` | `RS_binding` | `RFAM_005` | `NONZERO_PARAMETER` |

03. **re0000000205** `[RS_binding]`：`GlyRS_Gly_ATP` → `GlyRS_Gly_ATP_tRNAGlyGCC`

    同时消耗：`tRNAGlyGCC`；另外释放：`0`（`0` 表示无）。

<a id="re0000000205"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000205` | `GlyRS_Gly_ATP + tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

04. **re0000000197** `[RS_activation]`：`GlyRS_Gly_ATP_tRNAGlyGCC` → `GlyRS_GlyAMP_PPi_tRNAGlyGCC`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

<a id="re0000000197"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000197` | `GlyRS_Gly_ATP_tRNAGlyGCC -> GlyRS_GlyAMP_PPi_tRNAGlyGCC` | `RS_activation` | `RFAM_010` | `NONZERO_PARAMETER` |

05. **re0000000189** `[RS_activation]`：`GlyRS_GlyAMP_PPi_tRNAGlyGCC` → `GlyRS_GlyAMP_tRNAGlyGCC`

    同时消耗：`0`；另外释放：`PPi`（`0` 表示无）。

<a id="re0000000189"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000189` | `GlyRS_GlyAMP_PPi_tRNAGlyGCC -> GlyRS_GlyAMP_tRNAGlyGCC + PPi` | `RS_activation` | `RFAM_010` | `NONZERO_PARAMETER` |

06. **re0000000178** `[RS_charging]`：`GlyRS_GlyAMP_tRNAGlyGCC` → `GlyRS_AMP_GlytRNAGlyGCC`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

<a id="re0000000178"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000178` | `GlyRS_GlyAMP_tRNAGlyGCC -> GlyRS_AMP_GlytRNAGlyGCC` | `RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

07. **re0000000182** `[RS_charging]`：`GlyRS_AMP_GlytRNAGlyGCC` → `GlyRS_AMP`

    同时消耗：`0`；另外释放：`GlytRNAGlyGCC`（`0` 表示无）。

<a id="re0000000182"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000182` | `GlyRS_AMP_GlytRNAGlyGCC -> GlyRS_AMP + GlytRNAGlyGCC` | `RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

08. **re0000000145** `[RS_charging]`：`GlyRS_AMP` → `GlyRS`

    同时消耗：`0`；另外释放：`AMP`（`0` 表示无）。

<a id="re0000000145"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000145` | `GlyRS_AMP -> AMP + GlyRS` | `RS_charging` | `RFAM_006` | `NONZERO_PARAMETER` |

<a id="GlyRS-P02"></a>

#### GlyRS-P02 — ATP-first entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `GlyRS`；终点 `GlyRS_Gly_ATP`。

01. **re0000000132** `[RS_binding]`：`GlyRS` → `GlyRS_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000132"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000132` | `ATP + GlyRS -> GlyRS_ATP` | `RS_binding` | `RFAM_005` | `NONZERO_PARAMETER` |

02. **re0000000134** `[RS_binding]`：`GlyRS_ATP` → `GlyRS_Gly_ATP`

    同时消耗：`Gly`；另外释放：`0`（`0` 表示无）。

<a id="re0000000134"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000134` | `Gly + GlyRS_ATP -> GlyRS_Gly_ATP` | `RS_binding` | `RFAM_005` | `NONZERO_PARAMETER` |

`REJOIN`：在 `GlyRS_Gly_ATP` 接入 [GlyRS-P01](#GlyRS-P01)。

<a id="GlyRS-P03"></a>

#### GlyRS-P03 — tRNAGlyGCC → Gly → ATP entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `GlyRS`；终点 `GlyRS_Gly_ATP_tRNAGlyGCC`。

01. **re0000000199** `[RS_binding]`：`GlyRS` → `GlyRS_tRNAGlyGCC`

    同时消耗：`tRNAGlyGCC`；另外释放：`0`（`0` 表示无）。

<a id="re0000000199"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000199` | `GlyRS + tRNAGlyGCC -> GlyRS_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

02. **re0000000188** `[RS_binding]`：`GlyRS_tRNAGlyGCC` → `GlyRS_Gly_tRNAGlyGCC`

    同时消耗：`Gly`；另外释放：`0`（`0` 表示无）。

<a id="re0000000188"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000188` | `Gly + GlyRS_tRNAGlyGCC -> GlyRS_Gly_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

03. **re0000000195** `[RS_binding]`：`GlyRS_Gly_tRNAGlyGCC` → `GlyRS_Gly_ATP_tRNAGlyGCC`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000195"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000195` | `ATP + GlyRS_Gly_tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P01](#GlyRS-P01)。

<a id="GlyRS-P04"></a>

#### GlyRS-P04 — tRNAGlyGCC → ATP → Gly entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `GlyRS`；终点 `GlyRS_Gly_ATP_tRNAGlyGCC`。

01. **re0000000199** `[RS_binding]`：`GlyRS` → `GlyRS_tRNAGlyGCC`

    同时消耗：`tRNAGlyGCC`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000199](#re0000000199)。

02. **re0000000191** `[RS_binding]`：`GlyRS_tRNAGlyGCC` → `GlyRS_ATP_tRNAGlyGCC`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000191"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000191` | `ATP + GlyRS_tRNAGlyGCC -> GlyRS_ATP_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

03. **re0000000193** `[RS_binding]`：`GlyRS_ATP_tRNAGlyGCC` → `GlyRS_Gly_ATP_tRNAGlyGCC`

    同时消耗：`Gly`；另外释放：`0`（`0` 表示无）。

<a id="re0000000193"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000193` | `Gly + GlyRS_ATP_tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P01](#GlyRS-P01)。

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P03](#GlyRS-P03)。

<a id="GlyRS-P05"></a>

#### GlyRS-P05 — Gly → tRNAGlyGCC → ATP entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `GlyRS`；终点 `GlyRS_Gly_ATP_tRNAGlyGCC`。

01. **re0000000126** `[RS_binding]`：`GlyRS` → `GlyRS_Gly`

    同时消耗：`Gly`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000126](#re0000000126)。

02. **re0000000200** `[RS_binding]`：`GlyRS_Gly` → `GlyRS_Gly_tRNAGlyGCC`

    同时消耗：`tRNAGlyGCC`；另外释放：`0`（`0` 表示无）。

<a id="re0000000200"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000200` | `GlyRS_Gly + tRNAGlyGCC -> GlyRS_Gly_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

03. **re0000000195** `[RS_binding]`：`GlyRS_Gly_tRNAGlyGCC` → `GlyRS_Gly_ATP_tRNAGlyGCC`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000195](#re0000000195)。

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P01](#GlyRS-P01)。

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P03](#GlyRS-P03)。

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P04](#GlyRS-P04)。

<a id="GlyRS-P06"></a>

#### GlyRS-P06 — ATP → tRNAGlyGCC → Gly entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `GlyRS`；终点 `GlyRS_Gly_ATP_tRNAGlyGCC`。

01. **re0000000132** `[RS_binding]`：`GlyRS` → `GlyRS_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000132](#re0000000132)。

02. **re0000000203** `[RS_binding]`：`GlyRS_ATP` → `GlyRS_ATP_tRNAGlyGCC`

    同时消耗：`tRNAGlyGCC`；另外释放：`0`（`0` 表示无）。

<a id="re0000000203"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000203` | `GlyRS_ATP + tRNAGlyGCC -> GlyRS_ATP_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

03. **re0000000193** `[RS_binding]`：`GlyRS_ATP_tRNAGlyGCC` → `GlyRS_Gly_ATP_tRNAGlyGCC`

    同时消耗：`Gly`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000193](#re0000000193)。

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P01](#GlyRS-P01)。

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P03](#GlyRS-P03)。

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P04](#GlyRS-P04)。

`REJOIN`：在 `GlyRS_Gly_ATP_tRNAGlyGCC` 接入 [GlyRS-P05](#GlyRS-P05)。

<a id="GlyRS-P07"></a>

#### GlyRS-P07 — 先活化、释放 PPi，再结合 tRNA

类型：`PRODUCTIVE_PATH;RETURN_LOOP`。起点 `GlyRS`；终点 `GlyRS`。

目标释放产物：`GlytRNAGlyGCC`；最后恢复 `GlyRS`。

01. **re0000000126** `[RS_binding]`：`GlyRS` → `GlyRS_Gly`

    同时消耗：`Gly`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000126](#re0000000126)。

02. **re0000000136** `[RS_binding]`：`GlyRS_Gly` → `GlyRS_Gly_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000136](#re0000000136)。

03. **re0000000140** `[RS_activation]`：`GlyRS_Gly_ATP` → `GlyRS_GlyAMP_PPi`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

<a id="re0000000140"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000140` | `GlyRS_Gly_ATP -> GlyRS_GlyAMP_PPi` | `RS_activation` | `RFAM_005` | `NONZERO_PARAMETER` |

04. **re0000000127** `[RS_activation]`：`GlyRS_GlyAMP_PPi` → `GlyRS_GlyAMP`

    同时消耗：`0`；另外释放：`PPi`（`0` 表示无）。

<a id="re0000000127"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000127` | `GlyRS_GlyAMP_PPi -> GlyRS_GlyAMP + PPi` | `RS_activation` | `RFAM_005` | `NONZERO_PARAMETER` |

05. **re0000000209** `[RS_charging]`：`GlyRS_GlyAMP` → `GlyRS_GlyAMP_tRNAGlyGCC`

    同时消耗：`tRNAGlyGCC`；另外释放：`0`（`0` 表示无）。

<a id="re0000000209"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000209` | `GlyRS_GlyAMP + tRNAGlyGCC -> GlyRS_GlyAMP_tRNAGlyGCC` | `RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

06. **re0000000178** `[RS_charging]`：`GlyRS_GlyAMP_tRNAGlyGCC` → `GlyRS_AMP_GlytRNAGlyGCC`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000178](#re0000000178)。

07. **re0000000182** `[RS_charging]`：`GlyRS_AMP_GlytRNAGlyGCC` → `GlyRS_AMP`

    同时消耗：`0`；另外释放：`GlytRNAGlyGCC`（`0` 表示无）。

原始方程：[re0000000182](#re0000000182)。

08. **re0000000145** `[RS_charging]`：`GlyRS_AMP` → `GlyRS`

    同时消耗：`0`；另外释放：`AMP`（`0` 表示无）。

原始方程：[re0000000145](#re0000000145)。

替代路段在 `GlyRS_GlyAMP_tRNAGlyGCC` 汇合；随后与 [GlyRS-P01](#GlyRS-P01) 共享连续步骤：[re0000000178](#re0000000178), [re0000000182](#re0000000182), [re0000000145](#re0000000145)。

<a id="GlyRS-P08"></a>

#### GlyRS-P08 — 先活化、结合 tRNA，再释放 PPi

类型：`PRODUCTIVE_PATH;RETURN_LOOP`。起点 `GlyRS`；终点 `GlyRS`。

目标释放产物：`GlytRNAGlyGCC`；最后恢复 `GlyRS`。

01. **re0000000126** `[RS_binding]`：`GlyRS` → `GlyRS_Gly`

    同时消耗：`Gly`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000126](#re0000000126)。

02. **re0000000136** `[RS_binding]`：`GlyRS_Gly` → `GlyRS_Gly_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000136](#re0000000136)。

03. **re0000000140** `[RS_activation]`：`GlyRS_Gly_ATP` → `GlyRS_GlyAMP_PPi`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000140](#re0000000140)。

04. **re0000000207** `[RS_activation;RS_charging]`：`GlyRS_GlyAMP_PPi` → `GlyRS_GlyAMP_PPi_tRNAGlyGCC`

    同时消耗：`tRNAGlyGCC`；另外释放：`0`（`0` 表示无）。

<a id="re0000000207"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000207` | `GlyRS_GlyAMP_PPi + tRNAGlyGCC -> GlyRS_GlyAMP_PPi_tRNAGlyGCC` | `RS_activation;RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

05. **re0000000189** `[RS_activation]`：`GlyRS_GlyAMP_PPi_tRNAGlyGCC` → `GlyRS_GlyAMP_tRNAGlyGCC`

    同时消耗：`0`；另外释放：`PPi`（`0` 表示无）。

原始方程：[re0000000189](#re0000000189)。

06. **re0000000178** `[RS_charging]`：`GlyRS_GlyAMP_tRNAGlyGCC` → `GlyRS_AMP_GlytRNAGlyGCC`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000178](#re0000000178)。

07. **re0000000182** `[RS_charging]`：`GlyRS_AMP_GlytRNAGlyGCC` → `GlyRS_AMP`

    同时消耗：`0`；另外释放：`GlytRNAGlyGCC`（`0` 表示无）。

原始方程：[re0000000182](#re0000000182)。

08. **re0000000145** `[RS_charging]`：`GlyRS_AMP` → `GlyRS`

    同时消耗：`0`；另外释放：`AMP`（`0` 表示无）。

原始方程：[re0000000145](#re0000000145)。

替代路段在 `GlyRS_GlyAMP_PPi_tRNAGlyGCC` 汇合；随后与 [GlyRS-P01](#GlyRS-P01) 共享连续步骤：[re0000000189](#re0000000189), [re0000000178](#re0000000178), [re0000000182](#re0000000182), [re0000000145](#re0000000145)。

替代路段在 `GlyRS_GlyAMP_tRNAGlyGCC` 汇合；随后与 [GlyRS-P07](#GlyRS-P07) 共享连续步骤：[re0000000178](#re0000000178), [re0000000182](#re0000000182), [re0000000145](#re0000000145)。

<a id="GlyRS-P09"></a>

#### GlyRS-P09 — 产物出口替代：AMP 先释放，再释放 charged tRNA

类型：`PRODUCTIVE_PATH;RETURN_LOOP`。起点 `GlyRS`；终点 `GlyRS`。

目标释放产物：`GlytRNAGlyGCC`；最后恢复 `GlyRS`。

01. **re0000000126** `[RS_binding]`：`GlyRS` → `GlyRS_Gly`

    同时消耗：`Gly`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000126](#re0000000126)。

02. **re0000000136** `[RS_binding]`：`GlyRS_Gly` → `GlyRS_Gly_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000136](#re0000000136)。

03. **re0000000205** `[RS_binding]`：`GlyRS_Gly_ATP` → `GlyRS_Gly_ATP_tRNAGlyGCC`

    同时消耗：`tRNAGlyGCC`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000205](#re0000000205)。

04. **re0000000197** `[RS_activation]`：`GlyRS_Gly_ATP_tRNAGlyGCC` → `GlyRS_GlyAMP_PPi_tRNAGlyGCC`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000197](#re0000000197)。

05. **re0000000189** `[RS_activation]`：`GlyRS_GlyAMP_PPi_tRNAGlyGCC` → `GlyRS_GlyAMP_tRNAGlyGCC`

    同时消耗：`0`；另外释放：`PPi`（`0` 表示无）。

原始方程：[re0000000189](#re0000000189)。

06. **re0000000178** `[RS_charging]`：`GlyRS_GlyAMP_tRNAGlyGCC` → `GlyRS_AMP_GlytRNAGlyGCC`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000178](#re0000000178)。

07. **re0000000180** `[RS_charging]`：`GlyRS_AMP_GlytRNAGlyGCC` → `GlyRS_GlytRNAGlyGCC`

    同时消耗：`0`；另外释放：`AMP`（`0` 表示无）。

<a id="re0000000180"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000180` | `GlyRS_AMP_GlytRNAGlyGCC -> AMP + GlyRS_GlytRNAGlyGCC` | `RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

08. **re0000000184** `[RS_charging]`：`GlyRS_GlytRNAGlyGCC` → `GlyRS`

    同时消耗：`0`；另外释放：`GlytRNAGlyGCC`（`0` 表示无）。

<a id="re0000000184"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000184` | `GlyRS_GlytRNAGlyGCC -> GlyRS + GlytRNAGlyGCC` | `RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

<a id="GlyRS-P10"></a>

#### GlyRS-P10 — 游离 aminoacyl-AMP 再结合入口

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `GlyRS`；终点 `GlyRS_GlyAMP`。

01. **re0000000148** `[RS_activation]`：`GlyRS` → `GlyRS_GlyAMP`

    同时消耗：`GlyAMP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000148"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000148` | `GlyAMP + GlyRS -> GlyRS_GlyAMP` | `RS_activation` | `RFAM_005` | `NONZERO_PARAMETER` |

`REJOIN`：在 `GlyRS_GlyAMP` 接入 [GlyRS-P07](#GlyRS-P07)。

#### 竞争出口：按实际前体状态展开

每个状态列出全部原始出口。`REVERSE_EDGE` 表示存在精确逆反应伙伴，两方向都保留；它不指定哪一方向为生化正向。降解出口的完整方程在附录。

<a id="state-GlyRS"></a>

##### Branches from `GlyRS`

- [re0000000126](#re0000000126) → `GlyRS_Gly`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000128](#re0000000128) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000132](#re0000000132) → `GlyRS_ATP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000146](#re0000000146) → `GlyRS_AMP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000148](#re0000000148) → `GlyRS_GlyAMP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000185](#re0000000185) → `GlyRS_GlytRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000199](#re0000000199) → `GlyRS_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

原始方程：[re0000000126](#re0000000126)。

原始方程：[re0000000132](#re0000000132)。

<a id="re0000000146"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000146` | `AMP + GlyRS -> GlyRS_AMP` | `RS_charging` | `RFAM_006` | `REFERENCE_DISABLED` |

原始方程：[re0000000148](#re0000000148)。

<a id="re0000000185"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000185` | `GlyRS + GlytRNAGlyGCC -> GlyRS_GlytRNAGlyGCC` | `RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

原始方程：[re0000000199](#re0000000199)。

<a id="state-GlyRS_Gly"></a>

##### Branches from `GlyRS_Gly`

- [re0000000131](#re0000000131) → `GlyRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000136](#re0000000136) → `GlyRS_Gly_ATP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000139](#re0000000139) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000200](#re0000000200) → `GlyRS_Gly_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

<a id="re0000000131"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000131` | `GlyRS_Gly -> Gly + GlyRS` | `RS_binding` | `RFAM_005` | `NONZERO_PARAMETER` |

原始方程：[re0000000136](#re0000000136)。

原始方程：[re0000000200](#re0000000200)。

<a id="state-GlyRS_ATP"></a>

##### Branches from `GlyRS_ATP`

- [re0000000133](#re0000000133) → `GlyRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000134](#re0000000134) → `GlyRS_Gly_ATP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000138](#re0000000138) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000203](#re0000000203) → `GlyRS_ATP_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

<a id="re0000000133"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000133` | `GlyRS_ATP -> ATP + GlyRS` | `RS_binding` | `RFAM_005` | `NONZERO_PARAMETER` |

原始方程：[re0000000134](#re0000000134)。

原始方程：[re0000000203](#re0000000203)。

<a id="state-GlyRS_AMP"></a>

##### Branches from `GlyRS_AMP`

- [re0000000144](#re0000000144) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000145](#re0000000145) → `GlyRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000183](#re0000000183) → `GlyRS_AMP_GlytRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

原始方程：[re0000000145](#re0000000145)。

<a id="re0000000183"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000183` | `GlyRS_AMP + GlytRNAGlyGCC -> GlyRS_AMP_GlytRNAGlyGCC` | `RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

<a id="state-GlyRS_GlyAMP"></a>

##### Branches from `GlyRS_GlyAMP`

- [re0000000130](#re0000000130) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000147](#re0000000147) → `GlyRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000150](#re0000000150) → `GlyRS_GlyAMP_PPi`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000209](#re0000000209) → `GlyRS_GlyAMP_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

<a id="re0000000147"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000147` | `GlyRS_GlyAMP -> GlyAMP + GlyRS` | `RS_activation` | `RFAM_005` | `NONZERO_PARAMETER` |

<a id="re0000000150"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000150` | `GlyRS_GlyAMP + PPi -> GlyRS_GlyAMP_PPi` | `RS_activation` | `RFAM_005` | `REFERENCE_DISABLED` |

原始方程：[re0000000209](#re0000000209)。

<a id="state-GlyRS_GlytRNAGlyGCC"></a>

##### Branches from `GlyRS_GlytRNAGlyGCC`

- [re0000000181](#re0000000181) → `GlyRS_AMP_GlytRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000184](#re0000000184) → `GlyRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000187](#re0000000187) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000181"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000181` | `AMP + GlyRS_GlytRNAGlyGCC -> GlyRS_AMP_GlytRNAGlyGCC` | `RS_charging` | `RFAM_010` | `REFERENCE_DISABLED` |

原始方程：[re0000000184](#re0000000184)。

<a id="state-GlyRS_tRNAGlyGCC"></a>

##### Branches from `GlyRS_tRNAGlyGCC`

- [re0000000188](#re0000000188) → `GlyRS_Gly_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000191](#re0000000191) → `GlyRS_ATP_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000201](#re0000000201) → `GlyRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000211](#re0000000211) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

原始方程：[re0000000188](#re0000000188)。

原始方程：[re0000000191](#re0000000191)。

<a id="re0000000201"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000201` | `GlyRS_tRNAGlyGCC -> GlyRS + tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

<a id="state-GlyRS_Gly_ATP"></a>

##### Branches from `GlyRS_Gly_ATP`

- [re0000000129](#re0000000129) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000135](#re0000000135) → `GlyRS_ATP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000137](#re0000000137) → `GlyRS_Gly`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000140](#re0000000140) → `GlyRS_GlyAMP_PPi`；`STATE_TRANSITION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000205](#re0000000205) → `GlyRS_Gly_ATP_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

<a id="re0000000135"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000135` | `GlyRS_Gly_ATP -> Gly + GlyRS_ATP` | `RS_binding` | `RFAM_005` | `NONZERO_PARAMETER` |

<a id="re0000000137"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000137` | `GlyRS_Gly_ATP -> ATP + GlyRS_Gly` | `RS_binding` | `RFAM_005` | `NONZERO_PARAMETER` |

原始方程：[re0000000140](#re0000000140)。

原始方程：[re0000000205](#re0000000205)。

<a id="state-GlyRS_Gly_tRNAGlyGCC"></a>

##### Branches from `GlyRS_Gly_tRNAGlyGCC`

- [re0000000190](#re0000000190) → `GlyRS_tRNAGlyGCC`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000195](#re0000000195) → `GlyRS_Gly_ATP_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000202](#re0000000202) → `GlyRS_Gly`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000213](#re0000000213) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000190"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000190` | `GlyRS_Gly_tRNAGlyGCC -> Gly + GlyRS_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

原始方程：[re0000000195](#re0000000195)。

<a id="re0000000202"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000202` | `GlyRS_Gly_tRNAGlyGCC -> GlyRS_Gly + tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

<a id="state-GlyRS_ATP_tRNAGlyGCC"></a>

##### Branches from `GlyRS_ATP_tRNAGlyGCC`

- [re0000000192](#re0000000192) → `GlyRS_tRNAGlyGCC`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000193](#re0000000193) → `GlyRS_Gly_ATP_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000204](#re0000000204) → `GlyRS_ATP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000212](#re0000000212) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000192"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000192` | `GlyRS_ATP_tRNAGlyGCC -> ATP + GlyRS_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

原始方程：[re0000000193](#re0000000193)。

<a id="re0000000204"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000204` | `GlyRS_ATP_tRNAGlyGCC -> GlyRS_ATP + tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

<a id="state-GlyRS_AMP_GlytRNAGlyGCC"></a>

##### Branches from `GlyRS_AMP_GlytRNAGlyGCC`

- [re0000000179](#re0000000179) → `GlyRS_GlyAMP_tRNAGlyGCC`；`STATE_TRANSITION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000180](#re0000000180) → `GlyRS_GlytRNAGlyGCC`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000182](#re0000000182) → `GlyRS_AMP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000186](#re0000000186) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000179"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000179` | `GlyRS_AMP_GlytRNAGlyGCC -> GlyRS_GlyAMP_tRNAGlyGCC` | `RS_charging` | `RFAM_010` | `REFERENCE_DISABLED` |

原始方程：[re0000000180](#re0000000180)。

原始方程：[re0000000182](#re0000000182)。

<a id="state-GlyRS_GlyAMP_PPi"></a>

##### Branches from `GlyRS_GlyAMP_PPi`

- [re0000000127](#re0000000127) → `GlyRS_GlyAMP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000141](#re0000000141) → `GlyRS_Gly_ATP`；`STATE_TRANSITION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000142](#re0000000142) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000207](#re0000000207) → `GlyRS_GlyAMP_PPi_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

原始方程：[re0000000127](#re0000000127)。

<a id="re0000000141"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000141` | `GlyRS_GlyAMP_PPi -> GlyRS_Gly_ATP` | `RS_activation` | `RFAM_005` | `NONZERO_PARAMETER` |

原始方程：[re0000000207](#re0000000207)。

<a id="state-GlyRS_GlyAMP_tRNAGlyGCC"></a>

##### Branches from `GlyRS_GlyAMP_tRNAGlyGCC`

- [re0000000177](#re0000000177) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000178](#re0000000178) → `GlyRS_AMP_GlytRNAGlyGCC`；`STATE_TRANSITION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000210](#re0000000210) → `GlyRS_GlyAMP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000217](#re0000000217) → `GlyRS_GlyAMP_PPi_tRNAGlyGCC`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

原始方程：[re0000000178](#re0000000178)。

<a id="re0000000210"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000210` | `GlyRS_GlyAMP_tRNAGlyGCC -> GlyRS_GlyAMP + tRNAGlyGCC` | `RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

<a id="re0000000217"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000217` | `GlyRS_GlyAMP_tRNAGlyGCC + PPi -> GlyRS_GlyAMP_PPi_tRNAGlyGCC` | `RS_activation` | `RFAM_010` | `REFERENCE_DISABLED` |

<a id="state-GlyRS_Gly_ATP_tRNAGlyGCC"></a>

##### Branches from `GlyRS_Gly_ATP_tRNAGlyGCC`

- [re0000000194](#re0000000194) → `GlyRS_ATP_tRNAGlyGCC`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000196](#re0000000196) → `GlyRS_Gly_tRNAGlyGCC`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000197](#re0000000197) → `GlyRS_GlyAMP_PPi_tRNAGlyGCC`；`STATE_TRANSITION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000206](#re0000000206) → `GlyRS_Gly_ATP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000214](#re0000000214) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000194"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000194` | `GlyRS_Gly_ATP_tRNAGlyGCC -> Gly + GlyRS_ATP_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

<a id="re0000000196"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000196` | `GlyRS_Gly_ATP_tRNAGlyGCC -> ATP + GlyRS_Gly_tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

原始方程：[re0000000197](#re0000000197)。

<a id="re0000000206"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000206` | `GlyRS_Gly_ATP_tRNAGlyGCC -> GlyRS_Gly_ATP + tRNAGlyGCC` | `RS_binding` | `RFAM_010` | `NONZERO_PARAMETER` |

<a id="state-GlyRS_GlyAMP_PPi_tRNAGlyGCC"></a>

##### Branches from `GlyRS_GlyAMP_PPi_tRNAGlyGCC`

- [re0000000189](#re0000000189) → `GlyRS_GlyAMP_tRNAGlyGCC`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000198](#re0000000198) → `GlyRS_Gly_ATP_tRNAGlyGCC`；`STATE_TRANSITION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000208](#re0000000208) → `GlyRS_GlyAMP_PPi`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000215](#re0000000215) → `GlyRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

原始方程：[re0000000189](#re0000000189)。

<a id="re0000000198"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000198` | `GlyRS_GlyAMP_PPi_tRNAGlyGCC -> GlyRS_Gly_ATP_tRNAGlyGCC` | `RS_activation` | `RFAM_010` | `REFERENCE_DISABLED` |

<a id="re0000000208"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000208` | `GlyRS_GlyAMP_PPi_tRNAGlyGCC -> GlyRS_GlyAMP_PPi + tRNAGlyGCC` | `RS_activation;RS_charging` | `RFAM_010` | `NONZERO_PARAMETER` |

#### 汇合与跨 RFAM 连接

以下为到达同一载体状态的真实入边；有向可达性依赖每步完整底物。分支的目标状态可在本节或上面的状态出口定位。

| 汇合状态 | 所有原始入边 |
|---|---|
| `GlyRS` | [re0000000131](#re0000000131), [re0000000133](#re0000000133), [re0000000145](#re0000000145), [re0000000147](#re0000000147), [re0000000184](#re0000000184), [re0000000201](#re0000000201) |
| `GlyRS_AMP` | [re0000000146](#re0000000146), [re0000000182](#re0000000182) |
| `GlyRS_AMP_GlytRNAGlyGCC` | [re0000000178](#re0000000178), [re0000000181](#re0000000181), [re0000000183](#re0000000183) |
| `GlyRS_ATP` | [re0000000132](#re0000000132), [re0000000135](#re0000000135), [re0000000204](#re0000000204) |
| `GlyRS_ATP_tRNAGlyGCC` | [re0000000191](#re0000000191), [re0000000194](#re0000000194), [re0000000203](#re0000000203) |
| `GlyRS_Gly` | [re0000000126](#re0000000126), [re0000000137](#re0000000137), [re0000000202](#re0000000202) |
| `GlyRS_GlyAMP` | [re0000000127](#re0000000127), [re0000000148](#re0000000148), [re0000000210](#re0000000210) |
| `GlyRS_GlyAMP_PPi` | [re0000000140](#re0000000140), [re0000000150](#re0000000150), [re0000000208](#re0000000208) |
| `GlyRS_GlyAMP_PPi_tRNAGlyGCC` | [re0000000197](#re0000000197), [re0000000207](#re0000000207), [re0000000217](#re0000000217) |
| `GlyRS_GlyAMP_tRNAGlyGCC` | [re0000000179](#re0000000179), [re0000000189](#re0000000189), [re0000000209](#re0000000209) |
| `GlyRS_Gly_ATP` | [re0000000134](#re0000000134), [re0000000136](#re0000000136), [re0000000141](#re0000000141), [re0000000206](#re0000000206) |
| `GlyRS_Gly_ATP_tRNAGlyGCC` | [re0000000193](#re0000000193), [re0000000195](#re0000000195), [re0000000198](#re0000000198), [re0000000205](#re0000000205) |
| `GlyRS_Gly_tRNAGlyGCC` | [re0000000188](#re0000000188), [re0000000196](#re0000000196), [re0000000200](#re0000000200) |
| `GlyRS_GlytRNAGlyGCC` | [re0000000180](#re0000000180), [re0000000185](#re0000000185) |
| `GlyRS_degraded` | [re0000000128](#re0000000128), [re0000000129](#re0000000129), [re0000000130](#re0000000130), [re0000000138](#re0000000138), [re0000000139](#re0000000139), [re0000000142](#re0000000142), [re0000000144](#re0000000144), [re0000000177](#re0000000177), [re0000000186](#re0000000186), [re0000000187](#re0000000187), [re0000000211](#re0000000211), [re0000000212](#re0000000212), [re0000000213](#re0000000213), [re0000000214](#re0000000214), [re0000000215](#re0000000215) |
| `GlyRS_tRNAGlyGCC` | [re0000000190](#re0000000190), [re0000000192](#re0000000192), [re0000000199](#re0000000199) |

跨 RFAM 的载体接续（不以功能标签切断）：

| 载体状态 | 上游反应 | 下游反应 |
|---|---|---|
| `GlyRS` | [re0000000131](#re0000000131) | [re0000000146](#re0000000146) |
| `GlyRS` | [re0000000131](#re0000000131) | [re0000000185](#re0000000185) |
| `GlyRS` | [re0000000131](#re0000000131) | [re0000000199](#re0000000199) |
| `GlyRS` | [re0000000133](#re0000000133) | [re0000000146](#re0000000146) |
| `GlyRS` | [re0000000133](#re0000000133) | [re0000000185](#re0000000185) |
| `GlyRS` | [re0000000133](#re0000000133) | [re0000000199](#re0000000199) |
| `GlyRS` | [re0000000145](#re0000000145) | [re0000000126](#re0000000126) |
| `GlyRS` | [re0000000145](#re0000000145) | [re0000000132](#re0000000132) |
| `GlyRS` | [re0000000145](#re0000000145) | [re0000000148](#re0000000148) |
| `GlyRS` | [re0000000145](#re0000000145) | [re0000000185](#re0000000185) |
| `GlyRS` | [re0000000145](#re0000000145) | [re0000000199](#re0000000199) |
| `GlyRS` | [re0000000147](#re0000000147) | [re0000000146](#re0000000146) |
| `GlyRS` | [re0000000147](#re0000000147) | [re0000000185](#re0000000185) |
| `GlyRS` | [re0000000147](#re0000000147) | [re0000000199](#re0000000199) |
| `GlyRS` | [re0000000184](#re0000000184) | [re0000000126](#re0000000126) |
| `GlyRS` | [re0000000184](#re0000000184) | [re0000000132](#re0000000132) |
| `GlyRS` | [re0000000184](#re0000000184) | [re0000000146](#re0000000146) |
| `GlyRS` | [re0000000184](#re0000000184) | [re0000000148](#re0000000148) |
| `GlyRS` | [re0000000201](#re0000000201) | [re0000000126](#re0000000126) |
| `GlyRS` | [re0000000201](#re0000000201) | [re0000000132](#re0000000132) |
| `GlyRS` | [re0000000201](#re0000000201) | [re0000000146](#re0000000146) |
| `GlyRS` | [re0000000201](#re0000000201) | [re0000000148](#re0000000148) |
| `GlyRS_AMP` | [re0000000146](#re0000000146) | [re0000000183](#re0000000183) |
| `GlyRS_AMP` | [re0000000182](#re0000000182) | [re0000000145](#re0000000145) |
| `GlyRS_ATP` | [re0000000132](#re0000000132) | [re0000000203](#re0000000203) |
| `GlyRS_ATP` | [re0000000135](#re0000000135) | [re0000000203](#re0000000203) |
| `GlyRS_ATP` | [re0000000204](#re0000000204) | [re0000000133](#re0000000133) |
| `GlyRS_ATP` | [re0000000204](#re0000000204) | [re0000000134](#re0000000134) |
| `GlyRS_Gly` | [re0000000126](#re0000000126) | [re0000000200](#re0000000200) |
| `GlyRS_Gly` | [re0000000137](#re0000000137) | [re0000000200](#re0000000200) |
| `GlyRS_Gly` | [re0000000202](#re0000000202) | [re0000000131](#re0000000131) |
| `GlyRS_Gly` | [re0000000202](#re0000000202) | [re0000000136](#re0000000136) |
| `GlyRS_GlyAMP` | [re0000000127](#re0000000127) | [re0000000209](#re0000000209) |
| `GlyRS_GlyAMP` | [re0000000148](#re0000000148) | [re0000000209](#re0000000209) |
| `GlyRS_GlyAMP` | [re0000000210](#re0000000210) | [re0000000147](#re0000000147) |
| `GlyRS_GlyAMP` | [re0000000210](#re0000000210) | [re0000000150](#re0000000150) |
| `GlyRS_GlyAMP_PPi` | [re0000000140](#re0000000140) | [re0000000207](#re0000000207) |
| `GlyRS_GlyAMP_PPi` | [re0000000150](#re0000000150) | [re0000000207](#re0000000207) |
| `GlyRS_GlyAMP_PPi` | [re0000000208](#re0000000208) | [re0000000127](#re0000000127) |
| `GlyRS_GlyAMP_PPi` | [re0000000208](#re0000000208) | [re0000000141](#re0000000141) |
| `GlyRS_Gly_ATP` | [re0000000134](#re0000000134) | [re0000000205](#re0000000205) |
| `GlyRS_Gly_ATP` | [re0000000136](#re0000000136) | [re0000000205](#re0000000205) |
| `GlyRS_Gly_ATP` | [re0000000141](#re0000000141) | [re0000000205](#re0000000205) |
| `GlyRS_Gly_ATP` | [re0000000206](#re0000000206) | [re0000000135](#re0000000135) |
| `GlyRS_Gly_ATP` | [re0000000206](#re0000000206) | [re0000000137](#re0000000137) |
| `GlyRS_Gly_ATP` | [re0000000206](#re0000000206) | [re0000000140](#re0000000140) |

#### 逆反应与返回环

下列是有限的最短返回见证，不是所有可能循环的枚举。每行从所列载体出发并回到相同载体；包含禁用边的环只能作源结构阅读。SCC 内部保留全部边，仅 SCC 之间的压缩图为 DAG。

| 返回环 | 起止载体 | 连续原始反应 | 参考参数支持 |
|---|---|---|---|
| GlyRS-L01 | `GlyRS` | [re0000000126](#re0000000126) → [re0000000131](#re0000000131) | 全部非零 |
| GlyRS-L02 | `GlyRS_GlyAMP_PPi` | [re0000000127](#re0000000127) → [re0000000150](#re0000000150) | 含 REFERENCE_DISABLED |
| GlyRS-L03 | `GlyRS` | [re0000000132](#re0000000132) → [re0000000133](#re0000000133) | 全部非零 |
| GlyRS-L04 | `GlyRS_ATP` | [re0000000134](#re0000000134) → [re0000000135](#re0000000135) | 全部非零 |
| GlyRS-L05 | `GlyRS_Gly` | [re0000000136](#re0000000136) → [re0000000137](#re0000000137) | 全部非零 |
| GlyRS-L06 | `GlyRS_Gly_ATP` | [re0000000140](#re0000000140) → [re0000000141](#re0000000141) | 全部非零 |
| GlyRS-L07 | `GlyRS_AMP` | [re0000000145](#re0000000145) → [re0000000146](#re0000000146) | 含 REFERENCE_DISABLED |
| GlyRS-L08 | `GlyRS_GlyAMP` | [re0000000147](#re0000000147) → [re0000000148](#re0000000148) | 全部非零 |
| GlyRS-L09 | `GlyRS_GlyAMP_tRNAGlyGCC` | [re0000000178](#re0000000178) → [re0000000179](#re0000000179) | 含 REFERENCE_DISABLED |
| GlyRS-L10 | `GlyRS_AMP_GlytRNAGlyGCC` | [re0000000180](#re0000000180) → [re0000000181](#re0000000181) | 含 REFERENCE_DISABLED |
| GlyRS-L11 | `GlyRS_AMP_GlytRNAGlyGCC` | [re0000000182](#re0000000182) → [re0000000183](#re0000000183) | 全部非零 |
| GlyRS-L12 | `GlyRS_GlytRNAGlyGCC` | [re0000000184](#re0000000184) → [re0000000185](#re0000000185) | 全部非零 |
| GlyRS-L13 | `GlyRS_tRNAGlyGCC` | [re0000000188](#re0000000188) → [re0000000190](#re0000000190) | 全部非零 |
| GlyRS-L14 | `GlyRS_GlyAMP_PPi_tRNAGlyGCC` | [re0000000189](#re0000000189) → [re0000000217](#re0000000217) | 含 REFERENCE_DISABLED |
| GlyRS-L15 | `GlyRS_tRNAGlyGCC` | [re0000000191](#re0000000191) → [re0000000192](#re0000000192) | 全部非零 |
| GlyRS-L16 | `GlyRS_ATP_tRNAGlyGCC` | [re0000000193](#re0000000193) → [re0000000194](#re0000000194) | 全部非零 |
| GlyRS-L17 | `GlyRS_Gly_tRNAGlyGCC` | [re0000000195](#re0000000195) → [re0000000196](#re0000000196) | 全部非零 |
| GlyRS-L18 | `GlyRS_Gly_ATP_tRNAGlyGCC` | [re0000000197](#re0000000197) → [re0000000198](#re0000000198) | 含 REFERENCE_DISABLED |
| GlyRS-L19 | `GlyRS` | [re0000000199](#re0000000199) → [re0000000201](#re0000000201) | 全部非零 |
| GlyRS-L20 | `GlyRS_Gly` | [re0000000200](#re0000000200) → [re0000000202](#re0000000202) | 全部非零 |
| GlyRS-L21 | `GlyRS_ATP` | [re0000000203](#re0000000203) → [re0000000204](#re0000000204) | 全部非零 |
| GlyRS-L22 | `GlyRS_Gly_ATP` | [re0000000205](#re0000000205) → [re0000000206](#re0000000206) | 全部非零 |
| GlyRS-L23 | `GlyRS_GlyAMP_PPi` | [re0000000207](#re0000000207) → [re0000000208](#re0000000208) | 全部非零 |
| GlyRS-L24 | `GlyRS_GlyAMP` | [re0000000209](#re0000000209) → [re0000000210](#re0000000210) | 全部非零 |

逆向伙伴与零参数方向：

| 原始方向 | 精确逆方向 | 参考方向活性 |
|---|---|---|
| [re0000000126](#re0000000126) | [re0000000131](#re0000000131) | `NONZERO_PARAMETER` |
| [re0000000127](#re0000000127) | [re0000000150](#re0000000150) | `NONZERO_PARAMETER` |
| [re0000000131](#re0000000131) | [re0000000126](#re0000000126) | `NONZERO_PARAMETER` |
| [re0000000132](#re0000000132) | [re0000000133](#re0000000133) | `NONZERO_PARAMETER` |
| [re0000000133](#re0000000133) | [re0000000132](#re0000000132) | `NONZERO_PARAMETER` |
| [re0000000134](#re0000000134) | [re0000000135](#re0000000135) | `NONZERO_PARAMETER` |
| [re0000000135](#re0000000135) | [re0000000134](#re0000000134) | `NONZERO_PARAMETER` |
| [re0000000136](#re0000000136) | [re0000000137](#re0000000137) | `NONZERO_PARAMETER` |
| [re0000000137](#re0000000137) | [re0000000136](#re0000000136) | `NONZERO_PARAMETER` |
| [re0000000140](#re0000000140) | [re0000000141](#re0000000141) | `NONZERO_PARAMETER` |
| [re0000000141](#re0000000141) | [re0000000140](#re0000000140) | `NONZERO_PARAMETER` |
| [re0000000145](#re0000000145) | [re0000000146](#re0000000146) | `NONZERO_PARAMETER` |
| [re0000000146](#re0000000146) | [re0000000145](#re0000000145) | `REFERENCE_DISABLED` |
| [re0000000147](#re0000000147) | [re0000000148](#re0000000148) | `NONZERO_PARAMETER` |
| [re0000000148](#re0000000148) | [re0000000147](#re0000000147) | `NONZERO_PARAMETER` |
| [re0000000150](#re0000000150) | [re0000000127](#re0000000127) | `REFERENCE_DISABLED` |
| [re0000000178](#re0000000178) | [re0000000179](#re0000000179) | `NONZERO_PARAMETER` |
| [re0000000179](#re0000000179) | [re0000000178](#re0000000178) | `REFERENCE_DISABLED` |
| [re0000000180](#re0000000180) | [re0000000181](#re0000000181) | `NONZERO_PARAMETER` |
| [re0000000181](#re0000000181) | [re0000000180](#re0000000180) | `REFERENCE_DISABLED` |
| [re0000000182](#re0000000182) | [re0000000183](#re0000000183) | `NONZERO_PARAMETER` |
| [re0000000183](#re0000000183) | [re0000000182](#re0000000182) | `NONZERO_PARAMETER` |
| [re0000000184](#re0000000184) | [re0000000185](#re0000000185) | `NONZERO_PARAMETER` |
| [re0000000185](#re0000000185) | [re0000000184](#re0000000184) | `NONZERO_PARAMETER` |
| [re0000000188](#re0000000188) | [re0000000190](#re0000000190) | `NONZERO_PARAMETER` |
| [re0000000189](#re0000000189) | [re0000000217](#re0000000217) | `NONZERO_PARAMETER` |
| [re0000000190](#re0000000190) | [re0000000188](#re0000000188) | `NONZERO_PARAMETER` |
| [re0000000191](#re0000000191) | [re0000000192](#re0000000192) | `NONZERO_PARAMETER` |
| [re0000000192](#re0000000192) | [re0000000191](#re0000000191) | `NONZERO_PARAMETER` |
| [re0000000193](#re0000000193) | [re0000000194](#re0000000194) | `NONZERO_PARAMETER` |
| [re0000000194](#re0000000194) | [re0000000193](#re0000000193) | `NONZERO_PARAMETER` |
| [re0000000195](#re0000000195) | [re0000000196](#re0000000196) | `NONZERO_PARAMETER` |
| [re0000000196](#re0000000196) | [re0000000195](#re0000000195) | `NONZERO_PARAMETER` |
| [re0000000197](#re0000000197) | [re0000000198](#re0000000198) | `NONZERO_PARAMETER` |
| [re0000000198](#re0000000198) | [re0000000197](#re0000000197) | `REFERENCE_DISABLED` |
| [re0000000199](#re0000000199) | [re0000000201](#re0000000201) | `NONZERO_PARAMETER` |
| [re0000000200](#re0000000200) | [re0000000202](#re0000000202) | `NONZERO_PARAMETER` |
| [re0000000201](#re0000000201) | [re0000000199](#re0000000199) | `NONZERO_PARAMETER` |
| [re0000000202](#re0000000202) | [re0000000200](#re0000000200) | `NONZERO_PARAMETER` |
| [re0000000203](#re0000000203) | [re0000000204](#re0000000204) | `NONZERO_PARAMETER` |
| [re0000000204](#re0000000204) | [re0000000203](#re0000000203) | `NONZERO_PARAMETER` |
| [re0000000205](#re0000000205) | [re0000000206](#re0000000206) | `NONZERO_PARAMETER` |
| [re0000000206](#re0000000206) | [re0000000205](#re0000000205) | `NONZERO_PARAMETER` |
| [re0000000207](#re0000000207) | [re0000000208](#re0000000208) | `NONZERO_PARAMETER` |
| [re0000000208](#re0000000208) | [re0000000207](#re0000000207) | `NONZERO_PARAMETER` |
| [re0000000209](#re0000000209) | [re0000000210](#re0000000210) | `NONZERO_PARAMETER` |
| [re0000000210](#re0000000210) | [re0000000209](#re0000000209) | `NONZERO_PARAMETER` |
| [re0000000217](#re0000000217) | [re0000000189](#re0000000189) | `REFERENCE_DISABLED` |

### 1.2 MetRS charging

路径共享的步骤采用链接引用；分支列表为同一前体的并行出口，不能逐行串联。

<a id="MetRS-P01"></a>

#### MetRS-P01 — Met-first：tRNA 在活化前结合，charged tRNA 先释放

类型：`PRODUCTIVE_PATH;RETURN_LOOP`。起点 `MetRS`；终点 `MetRS`。

目标释放产物：`MettRNAfMetCAU`；最后恢复 `MetRS`。

01. **re0000000151** `[RS_binding]`：`MetRS` → `MetRS_Met`

    同时消耗：`Met`；另外释放：`0`（`0` 表示无）。

<a id="re0000000151"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000151` | `Met + MetRS -> MetRS_Met` | `RS_binding` | `RFAM_007` | `NONZERO_PARAMETER` |

02. **re0000000161** `[RS_binding]`：`MetRS_Met` → `MetRS_Met_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000161"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000161` | `ATP + MetRS_Met -> MetRS_Met_ATP` | `RS_binding` | `RFAM_007` | `NONZERO_PARAMETER` |

03. **re0000000247** `[RS_binding]`：`MetRS_Met_ATP` → `MetRS_Met_ATP_tRNAfMetCAU`

    同时消耗：`tRNAfMetCAU`；另外释放：`0`（`0` 表示无）。

<a id="re0000000247"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000247` | `MetRS_Met_ATP + tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

04. **re0000000239** `[RS_activation]`：`MetRS_Met_ATP_tRNAfMetCAU` → `MetRS_MetAMP_PPi_tRNAfMetCAU`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

<a id="re0000000239"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000239` | `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU` | `RS_activation` | `RFAM_012` | `NONZERO_PARAMETER` |

05. **re0000000231** `[RS_activation]`：`MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetRS_MetAMP_tRNAfMetCAU`

    同时消耗：`0`；另外释放：`PPi`（`0` 表示无）。

<a id="re0000000231"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000231` | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU + PPi` | `RS_activation` | `RFAM_012` | `NONZERO_PARAMETER` |

06. **re0000000220** `[RS_charging]`：`MetRS_MetAMP_tRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

<a id="re0000000220"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000220` | `MetRS_MetAMP_tRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | `RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

07. **re0000000224** `[RS_charging]`：`MetRS_AMP_MettRNAfMetCAU` → `MetRS_AMP`

    同时消耗：`0`；另外释放：`MettRNAfMetCAU`（`0` 表示无）。

<a id="re0000000224"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000224` | `MetRS_AMP_MettRNAfMetCAU -> MetRS_AMP + MettRNAfMetCAU` | `RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

08. **re0000000170** `[RS_charging]`：`MetRS_AMP` → `MetRS`

    同时消耗：`0`；另外释放：`AMP`（`0` 表示无）。

<a id="re0000000170"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000170` | `MetRS_AMP -> AMP + MetRS` | `RS_charging` | `RFAM_008` | `NONZERO_PARAMETER` |

<a id="MetRS-P02"></a>

#### MetRS-P02 — ATP-first entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `MetRS`；终点 `MetRS_Met_ATP`。

01. **re0000000157** `[RS_binding]`：`MetRS` → `MetRS_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000157"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000157` | `ATP + MetRS -> MetRS_ATP` | `RS_binding` | `RFAM_007` | `NONZERO_PARAMETER` |

02. **re0000000159** `[RS_binding]`：`MetRS_ATP` → `MetRS_Met_ATP`

    同时消耗：`Met`；另外释放：`0`（`0` 表示无）。

<a id="re0000000159"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000159` | `Met + MetRS_ATP -> MetRS_Met_ATP` | `RS_binding` | `RFAM_007` | `NONZERO_PARAMETER` |

`REJOIN`：在 `MetRS_Met_ATP` 接入 [MetRS-P01](#MetRS-P01)。

<a id="MetRS-P03"></a>

#### MetRS-P03 — tRNAfMetCAU → Met → ATP entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `MetRS`；终点 `MetRS_Met_ATP_tRNAfMetCAU`。

01. **re0000000241** `[RS_binding]`：`MetRS` → `MetRS_tRNAfMetCAU`

    同时消耗：`tRNAfMetCAU`；另外释放：`0`（`0` 表示无）。

<a id="re0000000241"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000241` | `MetRS + tRNAfMetCAU -> MetRS_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

02. **re0000000230** `[RS_binding]`：`MetRS_tRNAfMetCAU` → `MetRS_Met_tRNAfMetCAU`

    同时消耗：`Met`；另外释放：`0`（`0` 表示无）。

<a id="re0000000230"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000230` | `Met + MetRS_tRNAfMetCAU -> MetRS_Met_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

03. **re0000000237** `[RS_binding]`：`MetRS_Met_tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000237"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000237` | `ATP + MetRS_Met_tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P01](#MetRS-P01)。

<a id="MetRS-P04"></a>

#### MetRS-P04 — tRNAfMetCAU → ATP → Met entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `MetRS`；终点 `MetRS_Met_ATP_tRNAfMetCAU`。

01. **re0000000241** `[RS_binding]`：`MetRS` → `MetRS_tRNAfMetCAU`

    同时消耗：`tRNAfMetCAU`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000241](#re0000000241)。

02. **re0000000233** `[RS_binding]`：`MetRS_tRNAfMetCAU` → `MetRS_ATP_tRNAfMetCAU`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000233"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000233` | `ATP + MetRS_tRNAfMetCAU -> MetRS_ATP_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

03. **re0000000235** `[RS_binding]`：`MetRS_ATP_tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU`

    同时消耗：`Met`；另外释放：`0`（`0` 表示无）。

<a id="re0000000235"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000235` | `Met + MetRS_ATP_tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P01](#MetRS-P01)。

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P03](#MetRS-P03)。

<a id="MetRS-P05"></a>

#### MetRS-P05 — Met → tRNAfMetCAU → ATP entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `MetRS`；终点 `MetRS_Met_ATP_tRNAfMetCAU`。

01. **re0000000151** `[RS_binding]`：`MetRS` → `MetRS_Met`

    同时消耗：`Met`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000151](#re0000000151)。

02. **re0000000242** `[RS_binding]`：`MetRS_Met` → `MetRS_Met_tRNAfMetCAU`

    同时消耗：`tRNAfMetCAU`；另外释放：`0`（`0` 表示无）。

<a id="re0000000242"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000242` | `MetRS_Met + tRNAfMetCAU -> MetRS_Met_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

03. **re0000000237** `[RS_binding]`：`MetRS_Met_tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000237](#re0000000237)。

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P01](#MetRS-P01)。

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P03](#MetRS-P03)。

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P04](#MetRS-P04)。

<a id="MetRS-P06"></a>

#### MetRS-P06 — ATP → tRNAfMetCAU → Met entry

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `MetRS`；终点 `MetRS_Met_ATP_tRNAfMetCAU`。

01. **re0000000157** `[RS_binding]`：`MetRS` → `MetRS_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000157](#re0000000157)。

02. **re0000000245** `[RS_binding]`：`MetRS_ATP` → `MetRS_ATP_tRNAfMetCAU`

    同时消耗：`tRNAfMetCAU`；另外释放：`0`（`0` 表示无）。

<a id="re0000000245"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000245` | `MetRS_ATP + tRNAfMetCAU -> MetRS_ATP_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

03. **re0000000235** `[RS_binding]`：`MetRS_ATP_tRNAfMetCAU` → `MetRS_Met_ATP_tRNAfMetCAU`

    同时消耗：`Met`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000235](#re0000000235)。

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P01](#MetRS-P01)。

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P03](#MetRS-P03)。

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P04](#MetRS-P04)。

`REJOIN`：在 `MetRS_Met_ATP_tRNAfMetCAU` 接入 [MetRS-P05](#MetRS-P05)。

<a id="MetRS-P07"></a>

#### MetRS-P07 — 先活化、释放 PPi，再结合 tRNA

类型：`PRODUCTIVE_PATH;RETURN_LOOP`。起点 `MetRS`；终点 `MetRS`。

目标释放产物：`MettRNAfMetCAU`；最后恢复 `MetRS`。

01. **re0000000151** `[RS_binding]`：`MetRS` → `MetRS_Met`

    同时消耗：`Met`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000151](#re0000000151)。

02. **re0000000161** `[RS_binding]`：`MetRS_Met` → `MetRS_Met_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000161](#re0000000161)。

03. **re0000000165** `[RS_activation]`：`MetRS_Met_ATP` → `MetRS_MetAMP_PPi`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

<a id="re0000000165"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000165` | `MetRS_Met_ATP -> MetRS_MetAMP_PPi` | `RS_activation` | `RFAM_007` | `NONZERO_PARAMETER` |

04. **re0000000152** `[RS_activation]`：`MetRS_MetAMP_PPi` → `MetRS_MetAMP`

    同时消耗：`0`；另外释放：`PPi`（`0` 表示无）。

<a id="re0000000152"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000152` | `MetRS_MetAMP_PPi -> MetRS_MetAMP + PPi` | `RS_activation` | `RFAM_007` | `NONZERO_PARAMETER` |

05. **re0000000251** `[RS_charging]`：`MetRS_MetAMP` → `MetRS_MetAMP_tRNAfMetCAU`

    同时消耗：`tRNAfMetCAU`；另外释放：`0`（`0` 表示无）。

<a id="re0000000251"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000251` | `MetRS_MetAMP + tRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU` | `RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

06. **re0000000220** `[RS_charging]`：`MetRS_MetAMP_tRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000220](#re0000000220)。

07. **re0000000224** `[RS_charging]`：`MetRS_AMP_MettRNAfMetCAU` → `MetRS_AMP`

    同时消耗：`0`；另外释放：`MettRNAfMetCAU`（`0` 表示无）。

原始方程：[re0000000224](#re0000000224)。

08. **re0000000170** `[RS_charging]`：`MetRS_AMP` → `MetRS`

    同时消耗：`0`；另外释放：`AMP`（`0` 表示无）。

原始方程：[re0000000170](#re0000000170)。

替代路段在 `MetRS_MetAMP_tRNAfMetCAU` 汇合；随后与 [MetRS-P01](#MetRS-P01) 共享连续步骤：[re0000000220](#re0000000220), [re0000000224](#re0000000224), [re0000000170](#re0000000170)。

<a id="MetRS-P08"></a>

#### MetRS-P08 — 先活化、结合 tRNA，再释放 PPi

类型：`PRODUCTIVE_PATH;RETURN_LOOP`。起点 `MetRS`；终点 `MetRS`。

目标释放产物：`MettRNAfMetCAU`；最后恢复 `MetRS`。

01. **re0000000151** `[RS_binding]`：`MetRS` → `MetRS_Met`

    同时消耗：`Met`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000151](#re0000000151)。

02. **re0000000161** `[RS_binding]`：`MetRS_Met` → `MetRS_Met_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000161](#re0000000161)。

03. **re0000000165** `[RS_activation]`：`MetRS_Met_ATP` → `MetRS_MetAMP_PPi`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000165](#re0000000165)。

04. **re0000000249** `[RS_activation;RS_charging]`：`MetRS_MetAMP_PPi` → `MetRS_MetAMP_PPi_tRNAfMetCAU`

    同时消耗：`tRNAfMetCAU`；另外释放：`0`（`0` 表示无）。

<a id="re0000000249"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000249` | `MetRS_MetAMP_PPi + tRNAfMetCAU -> MetRS_MetAMP_PPi_tRNAfMetCAU` | `RS_activation;RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

05. **re0000000231** `[RS_activation]`：`MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetRS_MetAMP_tRNAfMetCAU`

    同时消耗：`0`；另外释放：`PPi`（`0` 表示无）。

原始方程：[re0000000231](#re0000000231)。

06. **re0000000220** `[RS_charging]`：`MetRS_MetAMP_tRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000220](#re0000000220)。

07. **re0000000224** `[RS_charging]`：`MetRS_AMP_MettRNAfMetCAU` → `MetRS_AMP`

    同时消耗：`0`；另外释放：`MettRNAfMetCAU`（`0` 表示无）。

原始方程：[re0000000224](#re0000000224)。

08. **re0000000170** `[RS_charging]`：`MetRS_AMP` → `MetRS`

    同时消耗：`0`；另外释放：`AMP`（`0` 表示无）。

原始方程：[re0000000170](#re0000000170)。

替代路段在 `MetRS_MetAMP_PPi_tRNAfMetCAU` 汇合；随后与 [MetRS-P01](#MetRS-P01) 共享连续步骤：[re0000000231](#re0000000231), [re0000000220](#re0000000220), [re0000000224](#re0000000224), [re0000000170](#re0000000170)。

替代路段在 `MetRS_MetAMP_tRNAfMetCAU` 汇合；随后与 [MetRS-P07](#MetRS-P07) 共享连续步骤：[re0000000220](#re0000000220), [re0000000224](#re0000000224), [re0000000170](#re0000000170)。

<a id="MetRS-P09"></a>

#### MetRS-P09 — 产物出口替代：AMP 先释放，再释放 charged tRNA

类型：`PRODUCTIVE_PATH;RETURN_LOOP`。起点 `MetRS`；终点 `MetRS`。

目标释放产物：`MettRNAfMetCAU`；最后恢复 `MetRS`。

01. **re0000000151** `[RS_binding]`：`MetRS` → `MetRS_Met`

    同时消耗：`Met`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000151](#re0000000151)。

02. **re0000000161** `[RS_binding]`：`MetRS_Met` → `MetRS_Met_ATP`

    同时消耗：`ATP`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000161](#re0000000161)。

03. **re0000000247** `[RS_binding]`：`MetRS_Met_ATP` → `MetRS_Met_ATP_tRNAfMetCAU`

    同时消耗：`tRNAfMetCAU`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000247](#re0000000247)。

04. **re0000000239** `[RS_activation]`：`MetRS_Met_ATP_tRNAfMetCAU` → `MetRS_MetAMP_PPi_tRNAfMetCAU`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000239](#re0000000239)。

05. **re0000000231** `[RS_activation]`：`MetRS_MetAMP_PPi_tRNAfMetCAU` → `MetRS_MetAMP_tRNAfMetCAU`

    同时消耗：`0`；另外释放：`PPi`（`0` 表示无）。

原始方程：[re0000000231](#re0000000231)。

06. **re0000000220** `[RS_charging]`：`MetRS_MetAMP_tRNAfMetCAU` → `MetRS_AMP_MettRNAfMetCAU`

    同时消耗：`0`；另外释放：`0`（`0` 表示无）。

原始方程：[re0000000220](#re0000000220)。

07. **re0000000222** `[RS_charging]`：`MetRS_AMP_MettRNAfMetCAU` → `MetRS_MettRNAfMetCAU`

    同时消耗：`0`；另外释放：`AMP`（`0` 表示无）。

<a id="re0000000222"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000222` | `MetRS_AMP_MettRNAfMetCAU -> AMP + MetRS_MettRNAfMetCAU` | `RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

08. **re0000000226** `[RS_charging]`：`MetRS_MettRNAfMetCAU` → `MetRS`

    同时消耗：`0`；另外释放：`MettRNAfMetCAU`（`0` 表示无）。

<a id="re0000000226"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000226` | `MetRS_MettRNAfMetCAU -> MetRS + MettRNAfMetCAU` | `RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

<a id="MetRS-P10"></a>

#### MetRS-P10 — 游离 aminoacyl-AMP 再结合入口

类型：`ALTERNATIVE_ENTRY;REJOIN`。起点 `MetRS`；终点 `MetRS_MetAMP`。

01. **re0000000173** `[RS_activation]`：`MetRS` → `MetRS_MetAMP`

    同时消耗：`MetAMP`；另外释放：`0`（`0` 表示无）。

<a id="re0000000173"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000173` | `MetAMP + MetRS -> MetRS_MetAMP` | `RS_activation` | `RFAM_007` | `NONZERO_PARAMETER` |

`REJOIN`：在 `MetRS_MetAMP` 接入 [MetRS-P07](#MetRS-P07)。

#### 竞争出口：按实际前体状态展开

每个状态列出全部原始出口。`REVERSE_EDGE` 表示存在精确逆反应伙伴，两方向都保留；它不指定哪一方向为生化正向。降解出口的完整方程在附录。

<a id="state-MetRS"></a>

##### Branches from `MetRS`

- [re0000000151](#re0000000151) → `MetRS_Met`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000153](#re0000000153) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000157](#re0000000157) → `MetRS_ATP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000171](#re0000000171) → `MetRS_AMP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000173](#re0000000173) → `MetRS_MetAMP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000227](#re0000000227) → `MetRS_MettRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000241](#re0000000241) → `MetRS_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

原始方程：[re0000000151](#re0000000151)。

原始方程：[re0000000157](#re0000000157)。

<a id="re0000000171"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000171` | `AMP + MetRS -> MetRS_AMP` | `RS_charging` | `RFAM_008` | `REFERENCE_DISABLED` |

原始方程：[re0000000173](#re0000000173)。

<a id="re0000000227"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000227` | `MetRS + MettRNAfMetCAU -> MetRS_MettRNAfMetCAU` | `RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

原始方程：[re0000000241](#re0000000241)。

<a id="state-MetRS_Met"></a>

##### Branches from `MetRS_Met`

- [re0000000156](#re0000000156) → `MetRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000161](#re0000000161) → `MetRS_Met_ATP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000164](#re0000000164) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000242](#re0000000242) → `MetRS_Met_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

<a id="re0000000156"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000156` | `MetRS_Met -> Met + MetRS` | `RS_binding` | `RFAM_007` | `NONZERO_PARAMETER` |

原始方程：[re0000000161](#re0000000161)。

原始方程：[re0000000242](#re0000000242)。

<a id="state-MetRS_ATP"></a>

##### Branches from `MetRS_ATP`

- [re0000000158](#re0000000158) → `MetRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000159](#re0000000159) → `MetRS_Met_ATP`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000163](#re0000000163) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000245](#re0000000245) → `MetRS_ATP_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

<a id="re0000000158"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000158` | `MetRS_ATP -> ATP + MetRS` | `RS_binding` | `RFAM_007` | `NONZERO_PARAMETER` |

原始方程：[re0000000159](#re0000000159)。

原始方程：[re0000000245](#re0000000245)。

<a id="state-MetRS_AMP"></a>

##### Branches from `MetRS_AMP`

- [re0000000169](#re0000000169) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000170](#re0000000170) → `MetRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000225](#re0000000225) → `MetRS_AMP_MettRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

原始方程：[re0000000170](#re0000000170)。

<a id="re0000000225"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000225` | `MetRS_AMP + MettRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | `RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

<a id="state-MetRS_MetAMP"></a>

##### Branches from `MetRS_MetAMP`

- [re0000000155](#re0000000155) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000172](#re0000000172) → `MetRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000175](#re0000000175) → `MetRS_MetAMP_PPi`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000251](#re0000000251) → `MetRS_MetAMP_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

<a id="re0000000172"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000172` | `MetRS_MetAMP -> MetAMP + MetRS` | `RS_activation` | `RFAM_007` | `NONZERO_PARAMETER` |

<a id="re0000000175"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000175` | `MetRS_MetAMP + PPi -> MetRS_MetAMP_PPi` | `RS_activation` | `RFAM_007` | `REFERENCE_DISABLED` |

原始方程：[re0000000251](#re0000000251)。

<a id="state-MetRS_MettRNAfMetCAU"></a>

##### Branches from `MetRS_MettRNAfMetCAU`

- [re0000000223](#re0000000223) → `MetRS_AMP_MettRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000226](#re0000000226) → `MetRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000229](#re0000000229) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000223"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000223` | `AMP + MetRS_MettRNAfMetCAU -> MetRS_AMP_MettRNAfMetCAU` | `RS_charging` | `RFAM_012` | `REFERENCE_DISABLED` |

原始方程：[re0000000226](#re0000000226)。

<a id="state-MetRS_tRNAfMetCAU"></a>

##### Branches from `MetRS_tRNAfMetCAU`

- [re0000000230](#re0000000230) → `MetRS_Met_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000233](#re0000000233) → `MetRS_ATP_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000243](#re0000000243) → `MetRS`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000253](#re0000000253) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

原始方程：[re0000000230](#re0000000230)。

原始方程：[re0000000233](#re0000000233)。

<a id="re0000000243"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000243` | `MetRS_tRNAfMetCAU -> MetRS + tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

<a id="state-MetRS_Met_ATP"></a>

##### Branches from `MetRS_Met_ATP`

- [re0000000154](#re0000000154) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000160](#re0000000160) → `MetRS_ATP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000162](#re0000000162) → `MetRS_Met`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000165](#re0000000165) → `MetRS_MetAMP_PPi`；`STATE_TRANSITION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000247](#re0000000247) → `MetRS_Met_ATP_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

<a id="re0000000160"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000160` | `MetRS_Met_ATP -> Met + MetRS_ATP` | `RS_binding` | `RFAM_007` | `NONZERO_PARAMETER` |

<a id="re0000000162"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000162` | `MetRS_Met_ATP -> ATP + MetRS_Met` | `RS_binding` | `RFAM_007` | `NONZERO_PARAMETER` |

原始方程：[re0000000165](#re0000000165)。

原始方程：[re0000000247](#re0000000247)。

<a id="state-MetRS_Met_tRNAfMetCAU"></a>

##### Branches from `MetRS_Met_tRNAfMetCAU`

- [re0000000232](#re0000000232) → `MetRS_tRNAfMetCAU`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000237](#re0000000237) → `MetRS_Met_ATP_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000244](#re0000000244) → `MetRS_Met`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000255](#re0000000255) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000232"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000232` | `MetRS_Met_tRNAfMetCAU -> Met + MetRS_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

原始方程：[re0000000237](#re0000000237)。

<a id="re0000000244"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000244` | `MetRS_Met_tRNAfMetCAU -> MetRS_Met + tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

<a id="state-MetRS_ATP_tRNAfMetCAU"></a>

##### Branches from `MetRS_ATP_tRNAfMetCAU`

- [re0000000234](#re0000000234) → `MetRS_tRNAfMetCAU`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000235](#re0000000235) → `MetRS_Met_ATP_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000246](#re0000000246) → `MetRS_ATP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000254](#re0000000254) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000234"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000234` | `MetRS_ATP_tRNAfMetCAU -> ATP + MetRS_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

原始方程：[re0000000235](#re0000000235)。

<a id="re0000000246"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000246` | `MetRS_ATP_tRNAfMetCAU -> MetRS_ATP + tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

<a id="state-MetRS_AMP_MettRNAfMetCAU"></a>

##### Branches from `MetRS_AMP_MettRNAfMetCAU`

- [re0000000221](#re0000000221) → `MetRS_MetAMP_tRNAfMetCAU`；`STATE_TRANSITION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000222](#re0000000222) → `MetRS_MettRNAfMetCAU`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000224](#re0000000224) → `MetRS_AMP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000228](#re0000000228) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000221"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000221` | `MetRS_AMP_MettRNAfMetCAU -> MetRS_MetAMP_tRNAfMetCAU` | `RS_charging` | `RFAM_012` | `REFERENCE_DISABLED` |

原始方程：[re0000000222](#re0000000222)。

原始方程：[re0000000224](#re0000000224)。

<a id="state-MetRS_MetAMP_PPi"></a>

##### Branches from `MetRS_MetAMP_PPi`

- [re0000000152](#re0000000152) → `MetRS_MetAMP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000166](#re0000000166) → `MetRS_Met_ATP`；`STATE_TRANSITION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000167](#re0000000167) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000249](#re0000000249) → `MetRS_MetAMP_PPi_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。

原始方程：[re0000000152](#re0000000152)。

<a id="re0000000166"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000166` | `MetRS_MetAMP_PPi -> MetRS_Met_ATP` | `RS_activation` | `RFAM_007` | `NONZERO_PARAMETER` |

原始方程：[re0000000249](#re0000000249)。

<a id="state-MetRS_MetAMP_tRNAfMetCAU"></a>

##### Branches from `MetRS_MetAMP_tRNAfMetCAU`

- [re0000000219](#re0000000219) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000220](#re0000000220) → `MetRS_AMP_MettRNAfMetCAU`；`STATE_TRANSITION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000252](#re0000000252) → `MetRS_MetAMP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000260](#re0000000260) → `MetRS_MetAMP_PPi_tRNAfMetCAU`；`HETERODIMER_ASSOCIATION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

原始方程：[re0000000220](#re0000000220)。

<a id="re0000000252"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000252` | `MetRS_MetAMP_tRNAfMetCAU -> MetRS_MetAMP + tRNAfMetCAU` | `RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

<a id="re0000000260"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000260` | `MetRS_MetAMP_tRNAfMetCAU + PPi -> MetRS_MetAMP_PPi_tRNAfMetCAU` | `RS_activation` | `RFAM_012` | `REFERENCE_DISABLED` |

<a id="state-MetRS_Met_ATP_tRNAfMetCAU"></a>

##### Branches from `MetRS_Met_ATP_tRNAfMetCAU`

- [re0000000236](#re0000000236) → `MetRS_ATP_tRNAfMetCAU`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000238](#re0000000238) → `MetRS_Met_tRNAfMetCAU`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000239](#re0000000239) → `MetRS_MetAMP_PPi_tRNAfMetCAU`；`STATE_TRANSITION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000248](#re0000000248) → `MetRS_Met_ATP`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000256](#re0000000256) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

<a id="re0000000236"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000236` | `MetRS_Met_ATP_tRNAfMetCAU -> Met + MetRS_ATP_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

<a id="re0000000238"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000238` | `MetRS_Met_ATP_tRNAfMetCAU -> ATP + MetRS_Met_tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

原始方程：[re0000000239](#re0000000239)。

<a id="re0000000248"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000248` | `MetRS_Met_ATP_tRNAfMetCAU -> MetRS_Met_ATP + tRNAfMetCAU` | `RS_binding` | `RFAM_012` | `NONZERO_PARAMETER` |

<a id="state-MetRS_MetAMP_PPi_tRNAfMetCAU"></a>

##### Branches from `MetRS_MetAMP_PPi_tRNAfMetCAU`

- [re0000000231](#re0000000231) → `MetRS_MetAMP_tRNAfMetCAU`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000240](#re0000000240) → `MetRS_Met_ATP_tRNAfMetCAU`；`STATE_TRANSITION`；`REVERSE_EDGE;REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。
- [re0000000250](#re0000000250) → `MetRS_MetAMP_PPi`；`DISSOCIATION`；`REVERSE_EDGE;COMPETITIVE_BRANCH;REJOIN;CROSS_FAMILY_LINK`。
- [re0000000257](#re0000000257) → `MetRS_degraded`；`STATE_TRANSITION`；`REFERENCE_DISABLED;COMPETITIVE_BRANCH;REJOIN`。

原始方程：[re0000000231](#re0000000231)。

<a id="re0000000240"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000240` | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_Met_ATP_tRNAfMetCAU` | `RS_activation` | `RFAM_012` | `REFERENCE_DISABLED` |

<a id="re0000000250"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000250` | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetRS_MetAMP_PPi + tRNAfMetCAU` | `RS_activation;RS_charging` | `RFAM_012` | `NONZERO_PARAMETER` |

#### 汇合与跨 RFAM 连接

以下为到达同一载体状态的真实入边；有向可达性依赖每步完整底物。分支的目标状态可在本节或上面的状态出口定位。

| 汇合状态 | 所有原始入边 |
|---|---|
| `MetRS` | [re0000000156](#re0000000156), [re0000000158](#re0000000158), [re0000000170](#re0000000170), [re0000000172](#re0000000172), [re0000000226](#re0000000226), [re0000000243](#re0000000243) |
| `MetRS_AMP` | [re0000000171](#re0000000171), [re0000000224](#re0000000224) |
| `MetRS_AMP_MettRNAfMetCAU` | [re0000000220](#re0000000220), [re0000000223](#re0000000223), [re0000000225](#re0000000225) |
| `MetRS_ATP` | [re0000000157](#re0000000157), [re0000000160](#re0000000160), [re0000000246](#re0000000246) |
| `MetRS_ATP_tRNAfMetCAU` | [re0000000233](#re0000000233), [re0000000236](#re0000000236), [re0000000245](#re0000000245) |
| `MetRS_Met` | [re0000000151](#re0000000151), [re0000000162](#re0000000162), [re0000000244](#re0000000244) |
| `MetRS_MetAMP` | [re0000000152](#re0000000152), [re0000000173](#re0000000173), [re0000000252](#re0000000252) |
| `MetRS_MetAMP_PPi` | [re0000000165](#re0000000165), [re0000000175](#re0000000175), [re0000000250](#re0000000250) |
| `MetRS_MetAMP_PPi_tRNAfMetCAU` | [re0000000239](#re0000000239), [re0000000249](#re0000000249), [re0000000260](#re0000000260) |
| `MetRS_MetAMP_tRNAfMetCAU` | [re0000000221](#re0000000221), [re0000000231](#re0000000231), [re0000000251](#re0000000251) |
| `MetRS_Met_ATP` | [re0000000159](#re0000000159), [re0000000161](#re0000000161), [re0000000166](#re0000000166), [re0000000248](#re0000000248) |
| `MetRS_Met_ATP_tRNAfMetCAU` | [re0000000235](#re0000000235), [re0000000237](#re0000000237), [re0000000240](#re0000000240), [re0000000247](#re0000000247) |
| `MetRS_Met_tRNAfMetCAU` | [re0000000230](#re0000000230), [re0000000238](#re0000000238), [re0000000242](#re0000000242) |
| `MetRS_MettRNAfMetCAU` | [re0000000222](#re0000000222), [re0000000227](#re0000000227) |
| `MetRS_degraded` | [re0000000153](#re0000000153), [re0000000154](#re0000000154), [re0000000155](#re0000000155), [re0000000163](#re0000000163), [re0000000164](#re0000000164), [re0000000167](#re0000000167), [re0000000169](#re0000000169), [re0000000219](#re0000000219), [re0000000228](#re0000000228), [re0000000229](#re0000000229), [re0000000253](#re0000000253), [re0000000254](#re0000000254), [re0000000255](#re0000000255), [re0000000256](#re0000000256), [re0000000257](#re0000000257) |
| `MetRS_tRNAfMetCAU` | [re0000000232](#re0000000232), [re0000000234](#re0000000234), [re0000000241](#re0000000241) |

跨 RFAM 的载体接续（不以功能标签切断）：

| 载体状态 | 上游反应 | 下游反应 |
|---|---|---|
| `MetRS` | [re0000000156](#re0000000156) | [re0000000171](#re0000000171) |
| `MetRS` | [re0000000156](#re0000000156) | [re0000000227](#re0000000227) |
| `MetRS` | [re0000000156](#re0000000156) | [re0000000241](#re0000000241) |
| `MetRS` | [re0000000158](#re0000000158) | [re0000000171](#re0000000171) |
| `MetRS` | [re0000000158](#re0000000158) | [re0000000227](#re0000000227) |
| `MetRS` | [re0000000158](#re0000000158) | [re0000000241](#re0000000241) |
| `MetRS` | [re0000000170](#re0000000170) | [re0000000151](#re0000000151) |
| `MetRS` | [re0000000170](#re0000000170) | [re0000000157](#re0000000157) |
| `MetRS` | [re0000000170](#re0000000170) | [re0000000173](#re0000000173) |
| `MetRS` | [re0000000170](#re0000000170) | [re0000000227](#re0000000227) |
| `MetRS` | [re0000000170](#re0000000170) | [re0000000241](#re0000000241) |
| `MetRS` | [re0000000172](#re0000000172) | [re0000000171](#re0000000171) |
| `MetRS` | [re0000000172](#re0000000172) | [re0000000227](#re0000000227) |
| `MetRS` | [re0000000172](#re0000000172) | [re0000000241](#re0000000241) |
| `MetRS` | [re0000000226](#re0000000226) | [re0000000151](#re0000000151) |
| `MetRS` | [re0000000226](#re0000000226) | [re0000000157](#re0000000157) |
| `MetRS` | [re0000000226](#re0000000226) | [re0000000171](#re0000000171) |
| `MetRS` | [re0000000226](#re0000000226) | [re0000000173](#re0000000173) |
| `MetRS` | [re0000000243](#re0000000243) | [re0000000151](#re0000000151) |
| `MetRS` | [re0000000243](#re0000000243) | [re0000000157](#re0000000157) |
| `MetRS` | [re0000000243](#re0000000243) | [re0000000171](#re0000000171) |
| `MetRS` | [re0000000243](#re0000000243) | [re0000000173](#re0000000173) |
| `MetRS_AMP` | [re0000000171](#re0000000171) | [re0000000225](#re0000000225) |
| `MetRS_AMP` | [re0000000224](#re0000000224) | [re0000000170](#re0000000170) |
| `MetRS_ATP` | [re0000000157](#re0000000157) | [re0000000245](#re0000000245) |
| `MetRS_ATP` | [re0000000160](#re0000000160) | [re0000000245](#re0000000245) |
| `MetRS_ATP` | [re0000000246](#re0000000246) | [re0000000158](#re0000000158) |
| `MetRS_ATP` | [re0000000246](#re0000000246) | [re0000000159](#re0000000159) |
| `MetRS_Met` | [re0000000151](#re0000000151) | [re0000000242](#re0000000242) |
| `MetRS_Met` | [re0000000162](#re0000000162) | [re0000000242](#re0000000242) |
| `MetRS_Met` | [re0000000244](#re0000000244) | [re0000000156](#re0000000156) |
| `MetRS_Met` | [re0000000244](#re0000000244) | [re0000000161](#re0000000161) |
| `MetRS_MetAMP` | [re0000000152](#re0000000152) | [re0000000251](#re0000000251) |
| `MetRS_MetAMP` | [re0000000173](#re0000000173) | [re0000000251](#re0000000251) |
| `MetRS_MetAMP` | [re0000000252](#re0000000252) | [re0000000172](#re0000000172) |
| `MetRS_MetAMP` | [re0000000252](#re0000000252) | [re0000000175](#re0000000175) |
| `MetRS_MetAMP_PPi` | [re0000000165](#re0000000165) | [re0000000249](#re0000000249) |
| `MetRS_MetAMP_PPi` | [re0000000175](#re0000000175) | [re0000000249](#re0000000249) |
| `MetRS_MetAMP_PPi` | [re0000000250](#re0000000250) | [re0000000152](#re0000000152) |
| `MetRS_MetAMP_PPi` | [re0000000250](#re0000000250) | [re0000000166](#re0000000166) |
| `MetRS_Met_ATP` | [re0000000159](#re0000000159) | [re0000000247](#re0000000247) |
| `MetRS_Met_ATP` | [re0000000161](#re0000000161) | [re0000000247](#re0000000247) |
| `MetRS_Met_ATP` | [re0000000166](#re0000000166) | [re0000000247](#re0000000247) |
| `MetRS_Met_ATP` | [re0000000248](#re0000000248) | [re0000000160](#re0000000160) |
| `MetRS_Met_ATP` | [re0000000248](#re0000000248) | [re0000000162](#re0000000162) |
| `MetRS_Met_ATP` | [re0000000248](#re0000000248) | [re0000000165](#re0000000165) |

#### 逆反应与返回环

下列是有限的最短返回见证，不是所有可能循环的枚举。每行从所列载体出发并回到相同载体；包含禁用边的环只能作源结构阅读。SCC 内部保留全部边，仅 SCC 之间的压缩图为 DAG。

| 返回环 | 起止载体 | 连续原始反应 | 参考参数支持 |
|---|---|---|---|
| MetRS-L01 | `MetRS` | [re0000000151](#re0000000151) → [re0000000156](#re0000000156) | 全部非零 |
| MetRS-L02 | `MetRS_MetAMP_PPi` | [re0000000152](#re0000000152) → [re0000000175](#re0000000175) | 含 REFERENCE_DISABLED |
| MetRS-L03 | `MetRS` | [re0000000157](#re0000000157) → [re0000000158](#re0000000158) | 全部非零 |
| MetRS-L04 | `MetRS_ATP` | [re0000000159](#re0000000159) → [re0000000160](#re0000000160) | 全部非零 |
| MetRS-L05 | `MetRS_Met` | [re0000000161](#re0000000161) → [re0000000162](#re0000000162) | 全部非零 |
| MetRS-L06 | `MetRS_Met_ATP` | [re0000000165](#re0000000165) → [re0000000166](#re0000000166) | 全部非零 |
| MetRS-L07 | `MetRS_AMP` | [re0000000170](#re0000000170) → [re0000000171](#re0000000171) | 含 REFERENCE_DISABLED |
| MetRS-L08 | `MetRS_MetAMP` | [re0000000172](#re0000000172) → [re0000000173](#re0000000173) | 全部非零 |
| MetRS-L09 | `MetRS_MetAMP_tRNAfMetCAU` | [re0000000220](#re0000000220) → [re0000000221](#re0000000221) | 含 REFERENCE_DISABLED |
| MetRS-L10 | `MetRS_AMP_MettRNAfMetCAU` | [re0000000222](#re0000000222) → [re0000000223](#re0000000223) | 含 REFERENCE_DISABLED |
| MetRS-L11 | `MetRS_AMP_MettRNAfMetCAU` | [re0000000224](#re0000000224) → [re0000000225](#re0000000225) | 全部非零 |
| MetRS-L12 | `MetRS_MettRNAfMetCAU` | [re0000000226](#re0000000226) → [re0000000227](#re0000000227) | 全部非零 |
| MetRS-L13 | `MetRS_tRNAfMetCAU` | [re0000000230](#re0000000230) → [re0000000232](#re0000000232) | 全部非零 |
| MetRS-L14 | `MetRS_MetAMP_PPi_tRNAfMetCAU` | [re0000000231](#re0000000231) → [re0000000260](#re0000000260) | 含 REFERENCE_DISABLED |
| MetRS-L15 | `MetRS_tRNAfMetCAU` | [re0000000233](#re0000000233) → [re0000000234](#re0000000234) | 全部非零 |
| MetRS-L16 | `MetRS_ATP_tRNAfMetCAU` | [re0000000235](#re0000000235) → [re0000000236](#re0000000236) | 全部非零 |
| MetRS-L17 | `MetRS_Met_tRNAfMetCAU` | [re0000000237](#re0000000237) → [re0000000238](#re0000000238) | 全部非零 |
| MetRS-L18 | `MetRS_Met_ATP_tRNAfMetCAU` | [re0000000239](#re0000000239) → [re0000000240](#re0000000240) | 含 REFERENCE_DISABLED |
| MetRS-L19 | `MetRS` | [re0000000241](#re0000000241) → [re0000000243](#re0000000243) | 全部非零 |
| MetRS-L20 | `MetRS_Met` | [re0000000242](#re0000000242) → [re0000000244](#re0000000244) | 全部非零 |
| MetRS-L21 | `MetRS_ATP` | [re0000000245](#re0000000245) → [re0000000246](#re0000000246) | 全部非零 |
| MetRS-L22 | `MetRS_Met_ATP` | [re0000000247](#re0000000247) → [re0000000248](#re0000000248) | 全部非零 |
| MetRS-L23 | `MetRS_MetAMP_PPi` | [re0000000249](#re0000000249) → [re0000000250](#re0000000250) | 全部非零 |
| MetRS-L24 | `MetRS_MetAMP` | [re0000000251](#re0000000251) → [re0000000252](#re0000000252) | 全部非零 |

逆向伙伴与零参数方向：

| 原始方向 | 精确逆方向 | 参考方向活性 |
|---|---|---|
| [re0000000151](#re0000000151) | [re0000000156](#re0000000156) | `NONZERO_PARAMETER` |
| [re0000000152](#re0000000152) | [re0000000175](#re0000000175) | `NONZERO_PARAMETER` |
| [re0000000156](#re0000000156) | [re0000000151](#re0000000151) | `NONZERO_PARAMETER` |
| [re0000000157](#re0000000157) | [re0000000158](#re0000000158) | `NONZERO_PARAMETER` |
| [re0000000158](#re0000000158) | [re0000000157](#re0000000157) | `NONZERO_PARAMETER` |
| [re0000000159](#re0000000159) | [re0000000160](#re0000000160) | `NONZERO_PARAMETER` |
| [re0000000160](#re0000000160) | [re0000000159](#re0000000159) | `NONZERO_PARAMETER` |
| [re0000000161](#re0000000161) | [re0000000162](#re0000000162) | `NONZERO_PARAMETER` |
| [re0000000162](#re0000000162) | [re0000000161](#re0000000161) | `NONZERO_PARAMETER` |
| [re0000000165](#re0000000165) | [re0000000166](#re0000000166) | `NONZERO_PARAMETER` |
| [re0000000166](#re0000000166) | [re0000000165](#re0000000165) | `NONZERO_PARAMETER` |
| [re0000000170](#re0000000170) | [re0000000171](#re0000000171) | `NONZERO_PARAMETER` |
| [re0000000171](#re0000000171) | [re0000000170](#re0000000170) | `REFERENCE_DISABLED` |
| [re0000000172](#re0000000172) | [re0000000173](#re0000000173) | `NONZERO_PARAMETER` |
| [re0000000173](#re0000000173) | [re0000000172](#re0000000172) | `NONZERO_PARAMETER` |
| [re0000000175](#re0000000175) | [re0000000152](#re0000000152) | `REFERENCE_DISABLED` |
| [re0000000220](#re0000000220) | [re0000000221](#re0000000221) | `NONZERO_PARAMETER` |
| [re0000000221](#re0000000221) | [re0000000220](#re0000000220) | `REFERENCE_DISABLED` |
| [re0000000222](#re0000000222) | [re0000000223](#re0000000223) | `NONZERO_PARAMETER` |
| [re0000000223](#re0000000223) | [re0000000222](#re0000000222) | `REFERENCE_DISABLED` |
| [re0000000224](#re0000000224) | [re0000000225](#re0000000225) | `NONZERO_PARAMETER` |
| [re0000000225](#re0000000225) | [re0000000224](#re0000000224) | `NONZERO_PARAMETER` |
| [re0000000226](#re0000000226) | [re0000000227](#re0000000227) | `NONZERO_PARAMETER` |
| [re0000000227](#re0000000227) | [re0000000226](#re0000000226) | `NONZERO_PARAMETER` |
| [re0000000230](#re0000000230) | [re0000000232](#re0000000232) | `NONZERO_PARAMETER` |
| [re0000000231](#re0000000231) | [re0000000260](#re0000000260) | `NONZERO_PARAMETER` |
| [re0000000232](#re0000000232) | [re0000000230](#re0000000230) | `NONZERO_PARAMETER` |
| [re0000000233](#re0000000233) | [re0000000234](#re0000000234) | `NONZERO_PARAMETER` |
| [re0000000234](#re0000000234) | [re0000000233](#re0000000233) | `NONZERO_PARAMETER` |
| [re0000000235](#re0000000235) | [re0000000236](#re0000000236) | `NONZERO_PARAMETER` |
| [re0000000236](#re0000000236) | [re0000000235](#re0000000235) | `NONZERO_PARAMETER` |
| [re0000000237](#re0000000237) | [re0000000238](#re0000000238) | `NONZERO_PARAMETER` |
| [re0000000238](#re0000000238) | [re0000000237](#re0000000237) | `NONZERO_PARAMETER` |
| [re0000000239](#re0000000239) | [re0000000240](#re0000000240) | `NONZERO_PARAMETER` |
| [re0000000240](#re0000000240) | [re0000000239](#re0000000239) | `REFERENCE_DISABLED` |
| [re0000000241](#re0000000241) | [re0000000243](#re0000000243) | `NONZERO_PARAMETER` |
| [re0000000242](#re0000000242) | [re0000000244](#re0000000244) | `NONZERO_PARAMETER` |
| [re0000000243](#re0000000243) | [re0000000241](#re0000000241) | `NONZERO_PARAMETER` |
| [re0000000244](#re0000000244) | [re0000000242](#re0000000242) | `NONZERO_PARAMETER` |
| [re0000000245](#re0000000245) | [re0000000246](#re0000000246) | `NONZERO_PARAMETER` |
| [re0000000246](#re0000000246) | [re0000000245](#re0000000245) | `NONZERO_PARAMETER` |
| [re0000000247](#re0000000247) | [re0000000248](#re0000000248) | `NONZERO_PARAMETER` |
| [re0000000248](#re0000000248) | [re0000000247](#re0000000247) | `NONZERO_PARAMETER` |
| [re0000000249](#re0000000249) | [re0000000250](#re0000000250) | `NONZERO_PARAMETER` |
| [re0000000250](#re0000000250) | [re0000000249](#re0000000249) | `NONZERO_PARAMETER` |
| [re0000000251](#re0000000251) | [re0000000252](#re0000000252) | `NONZERO_PARAMETER` |
| [re0000000252](#re0000000252) | [re0000000251](#re0000000251) | `NONZERO_PARAMETER` |
| [re0000000260](#re0000000260) | [re0000000231](#re0000000231) | `REFERENCE_DISABLED` |

## 2. 游离中间体通道与载体交接边界

以下 8 条 RS 反应不含 GlyRS / MetRS，不能伪造酶载体边。按真实底物/产物成对保留；参考条件下全部禁用。酶释放或再结合游离 adenylate 的步骤仍见相应酶路径。

<a id="re0000000143"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000143` | `GlyAMP -> AMP + Gly` | `RS_activation` | `RFAM_005` | `REFERENCE_DISABLED` |

<a id="re0000000149"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000149` | `AMP + Gly -> GlyAMP` | `RS_activation` | `RFAM_005` | `REFERENCE_DISABLED` |

<a id="re0000000168"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000168` | `MetAMP -> AMP + Met` | `RS_activation` | `RFAM_007` | `REFERENCE_DISABLED` |

<a id="re0000000174"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000174` | `AMP + Met -> MetAMP` | `RS_activation` | `RFAM_007` | `REFERENCE_DISABLED` |

<a id="re0000000176"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000176` | `GlytRNAGlyGCC -> Gly + tRNAGlyGCC` | `RS_charging` | `RFAM_009` | `REFERENCE_DISABLED` |

<a id="re0000000216"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000216` | `Gly + tRNAGlyGCC -> GlytRNAGlyGCC` | `RS_charging` | `RFAM_009` | `REFERENCE_DISABLED` |

<a id="re0000000218"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000218` | `MettRNAfMetCAU -> Met + tRNAfMetCAU` | `RS_charging` | `RFAM_011` | `REFERENCE_DISABLED` |

<a id="re0000000259"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000259` | `Met + tRNAfMetCAU -> MettRNAfMetCAU` | `RS_charging` | `RFAM_011` | `REFERENCE_DISABLED` |

### 通往其他载体的边界

源方程支持下列 charged tRNA 的直接交接。GlyRS / MetRS 与 tRNA 的同步状态均保留在图文件；本样板不把 tRNA 与其他复合物的相遇展开为已经验证的后续路径。`HUMAN_REVIEW_REQUIRED`。

| 交接物种 | 消耗它的外部反应 | 该方向参考活性 |
|---|---|---|
| `GlytRNAGlyGCC` | [re0000000031](../reaction.md#re0000000031) | `REFERENCE_DISABLED` |
| `GlytRNAGlyGCC` | [re0000000063](../reaction.md#re0000000063) | `REFERENCE_DISABLED` |
| `GlytRNAGlyGCC` | [re0000000064](../reaction.md#re0000000064) | `REFERENCE_DISABLED` |
| `GlytRNAGlyGCC` | [re0000000121](../reaction.md#re0000000121) | `REFERENCE_DISABLED` |
| `GlytRNAGlyGCC` | [re0000000122](../reaction.md#re0000000122) | `REFERENCE_DISABLED` |
| `GlytRNAGlyGCC` | [re0000000275](../reaction.md#re0000000275) | `NONZERO_PARAMETER` |
| `MettRNAfMetCAU` | [re0000000258](../reaction.md#re0000000258) | `REFERENCE_DISABLED` |
| `MettRNAfMetCAU` | [re0000000288](../reaction.md#re0000000288) | `NONZERO_PARAMETER` |
| `MettRNAfMetCAU` | [re0000000420](../reaction.md#re0000000420) | `NONZERO_PARAMETER` |
| `MettRNAfMetCAU` | [re0000000422](../reaction.md#re0000000422) | `NONZERO_PARAMETER` |

## Appendix — DEG_sink and reference-disabled outlets

30 条酶载体降解出口逐条保留，均为 `REFERENCE_DISABLED`。它们属于相应前体的竞争出口，但不接入参考参数支持的产物路径。

<a id="re0000000128"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000128` | `GlyRS -> GlyRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000129"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000129` | `GlyRS_Gly_ATP -> ATP + Gly + GlyRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000130"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000130` | `GlyRS_GlyAMP -> GlyAMP + GlyRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000138"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000138` | `GlyRS_ATP -> ATP + GlyRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000139"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000139` | `GlyRS_Gly -> Gly + GlyRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000142"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000142` | `GlyRS_GlyAMP_PPi -> GlyAMP + GlyRS_degraded + PPi` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000144"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000144` | `GlyRS_AMP -> AMP + GlyRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000153"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000153` | `MetRS -> MetRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000154"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000154` | `MetRS_Met_ATP -> ATP + Met + MetRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000155"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000155` | `MetRS_MetAMP -> MetAMP + MetRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000163"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000163` | `MetRS_ATP -> ATP + MetRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000164"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000164` | `MetRS_Met -> Met + MetRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000167"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000167` | `MetRS_MetAMP_PPi -> MetAMP + MetRS_degraded + PPi` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000169"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000169` | `MetRS_AMP -> AMP + MetRS_degraded` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000177"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000177` | `GlyRS_GlyAMP_tRNAGlyGCC -> GlyAMP + GlyRS_degraded + tRNAGlyGCC` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000186"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000186` | `GlyRS_AMP_GlytRNAGlyGCC -> AMP + GlyRS_degraded + GlytRNAGlyGCC` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000187"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000187` | `GlyRS_GlytRNAGlyGCC -> GlyRS_degraded + GlytRNAGlyGCC` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000211"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000211` | `GlyRS_tRNAGlyGCC -> GlyRS_degraded + tRNAGlyGCC` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000212"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000212` | `GlyRS_ATP_tRNAGlyGCC -> ATP + GlyRS_degraded + tRNAGlyGCC` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000213"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000213` | `GlyRS_Gly_tRNAGlyGCC -> Gly + GlyRS_degraded + tRNAGlyGCC` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000214"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000214` | `GlyRS_Gly_ATP_tRNAGlyGCC -> ATP + Gly + GlyRS_degraded + tRNAGlyGCC` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000215"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000215` | `GlyRS_GlyAMP_PPi_tRNAGlyGCC -> GlyAMP + GlyRS_degraded + PPi + tRNAGlyGCC` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000219"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000219` | `MetRS_MetAMP_tRNAfMetCAU -> MetAMP + MetRS_degraded + tRNAfMetCAU` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000228"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000228` | `MetRS_AMP_MettRNAfMetCAU -> AMP + MetRS_degraded + MettRNAfMetCAU` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000229"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000229` | `MetRS_MettRNAfMetCAU -> MetRS_degraded + MettRNAfMetCAU` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000253"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000253` | `MetRS_tRNAfMetCAU -> MetRS_degraded + tRNAfMetCAU` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000254"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000254` | `MetRS_ATP_tRNAfMetCAU -> ATP + MetRS_degraded + tRNAfMetCAU` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000255"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000255` | `MetRS_Met_tRNAfMetCAU -> Met + MetRS_degraded + tRNAfMetCAU` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000256"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000256` | `MetRS_Met_ATP_tRNAfMetCAU -> ATP + Met + MetRS_degraded + tRNAfMetCAU` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |

<a id="re0000000257"></a>

| Reaction ID | 原始完整方程 | Level-C | RFAM | 参考方向活性 |
|---|---|---|---|---|
| `re0000000257` | `MetRS_MetAMP_PPi_tRNAfMetCAU -> MetAMP + MetRS_degraded + PPi + tRNAfMetCAU` | `DEG_sink` | `RFAM_DEG` | `REFERENCE_DISABLED` |
