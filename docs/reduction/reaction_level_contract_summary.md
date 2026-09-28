# PNAS2017 reaction-level functional contract — 组会简洁版 v0

**Status:** human-approved functional vocabulary v0；尚未把 968 条 reaction 全部逐条映射到 Level C。  
**目的：** 借用 Mavelli 2015 的宏观因果脉络，把 PNAS2017 detailed network 组织成“人能顺着讲”的功能阶段，同时保留原始 SBML reaction type、化学计量和后续 reduction 证据边界。

> Level C 回答“这条反应在 PURE 流程里干什么”。  
> CellDesigner reaction type 回答“这条边在原模型里是 association / dissociation / state transition 哪一种”。  
> 两者必须分开。

## Source-level code check

当前仓库源表经结构检查得到：

- 968 unique combined reactions；26 source subsystems。
- 原 combined SBML 的 reaction-level `reversible=true` 数量为 **0**；网络是用有向 reactions 表达。
- 按 reactants/products 的精确反向化学计量自动匹配，得到 **290 个 exact reverse pairs**，覆盖 **580 条 directed reactions**，且没有 ambiguous reverse-signature group。
- CellDesigner reaction types：`HETERODIMER_ASSOCIATION=266`、`DISSOCIATION=266`、`STATE_TRANSITION=436`。
- 现有网络另有 **388 条 degradation-related reactions** 和 **29 条 `FMet_tRNASynthesis` reactions**。因此，原先讨论的 21 个主链标签不足以诚实覆盖全部 source reactions；本 v0 增加 `RS_to_INIT_formylation` 与 coverage-only `DEG_sink`。

## Functional atlas

### RS / aminoacylation

```text
RS_binding
  ↓
RS_activation
  ATP → AMP + PPi
  ↓
RS_charging
  aa-tRNA formation
  ↓
RS_to_INIT_formylation
  initiator Met-tRNA → fMet-tRNA
```

- `RS_binding`
- `RS_activation`
- `RS_charging`
- `RS_to_INIT_formylation`

### INIT

```text
INIT_assembly
  ↓
INIT_tRNA_recruitment
  ↓
INIT_energy_commitment
  GTP → GDP + Pi
  ↓
INIT_70S_formation
  ↓
INIT_factor_release
```

- `INIT_assembly`
- `INIT_tRNA_recruitment`
- `INIT_energy_commitment`
- `INIT_70S_formation`
- `INIT_factor_release`

### ELONG — 保留 5 类

```text
ELONG_aa_tRNA_delivery
  ↓
ELONG_energy_coupling
  GTP → GDP + Pi
  ↓
ELONG_peptide_formation
  peptide +1 residue
  ↓
ELONG_translocation
  ↓
ELONG_tRNA_release
  ↺
```

- `ELONG_aa_tRNA_delivery`
- `ELONG_energy_coupling`
- `ELONG_peptide_formation`
- `ELONG_translocation`
- `ELONG_tRNA_release`

保留 5 类的原因：peptide formation 改变肽链长度；translocation 改变 ribosome/tRNA positional occupancy；两者不是同一个受保护信息，因此暂不压成单一 `translation` 标签。

### TERM / RECYCLE

```text
TERM_factor_binding
  ↓
TERM_peptide_release
  ↓
TERM_energy_coupling
  GTP → GDP + Pi
  ↓
RECYCLE_disassembly
  70S → 30S + 50S
  ↓
RECYCLE_component_release
```

- `TERM_factor_binding`
- `TERM_peptide_release`
- `TERM_energy_coupling`
- `RECYCLE_disassembly`
- `RECYCLE_component_release`

### EN / energy regeneration

```text
EN_binding
  ↓
EN_energy_transfer
  CP + ADP ↔ Cr + ATP
  ATP + GDP ↔ ADP + GTP
  ATP + AMP ↔ 2 ADP

PPi
  ↓
EN_byproduct_processing
  PPi → 2 Pi
```

- `EN_binding`
- `EN_energy_transfer`
- `EN_byproduct_processing`

### Coverage-only special class

- `DEG_sink`：进入 `*_degraded` terminal sink 的 degradation/inactivation reaction。它不属于 Mavelli 主功能链，但 source network 中有 388 条相关 reactions；后续可按 species Class-C contract 隐去 sink state，但累计损失必须保留。

## Reversibility contract

每条 reaction 后续至少记录：

- `reversibility_class = IRREVERSIBLE / EXACT_REVERSE_PAIR / POSSIBLE_REVERSE_PAIR / UNKNOWN`
- `reverse_partner_id`
- `reverse_pair_basis`
- `exact_reversible_merge`

若两条 directed reactions 是 exact reverse pair，可精确重写为一个 reversible channel，但必须保留：

```text
v_forward
v_reverse
v_net = v_forward - v_reverse
original forward ID
original reverse ID
original kinetic laws
```

这只是 **exact representation rewrite**，不是 fast equilibrium、QSSA 或 kinetic reduction。

## 当前边界

本文件冻结的是 **Level-C vocabulary**。下一步才是把 968 条 reactions 逐条赋予 Level C，并把无法自动确定的条目标成 `HUMAN_REVIEW_REQUIRED`；不能为了 100% coverage 强行猜。
