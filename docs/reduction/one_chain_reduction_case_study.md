# 一个真实串联段：先拓扑聚合，再讨论局部 QSSA

**结论：首个原型建议比较 `A → B`、`A → E_mid → B` 与保留显式链，优先审查保留聚合占据量的第二种方案。** 这是结构候选和解析推导，不是已验证的减阶模型。每个选项均为 `HUMAN_REVIEW_REQUIRED = true`；未删除、修改或批准任何源状态或反应。

## 1. 来源与条件边界

Canonical topology source is `models/pnas2017_full_reference/original/fMGG_synthesis.xml`. Reactants, products and stoichiometry below were checked against its SBML equations, including `stoichiometryMath`. Functional context is supported by `docs/reduction/reaction_level_annotation_v2.csv`, not inferred solely from names or projected graph edges.

| Source | SHA-256 |
| --- | --- |
| Canonical SBML | `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df` |
| Author parameter CSV | `cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465` |
| Author initial-value CSV | `a1b6f832303303c888999968d4652b00205e6adba478b11ceab9cbff4d1c41ec` |
| Functional annotation v2 | `ee2f80a3354199a03d3072464cbc301736afad72fba01e4bfcc499c0525f3335` |

The two author CSVs are under `models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/`. Canonical SBML contains placeholder local `k1 = 1` and placeholder species initial concentrations of `1`; the author CSV overlay supplies the numerical condition used below. Consequently:

- **Full canonical structural view:** the intermediates have reverse and side-path incidences; unconditional deletion is not supported.
- **Frozen author-default view:** the relevant reverse and side-path constants are exactly zero, so the selected three-step segment is a directed serial path. Zero initial concentration does not establish inactivity: these intermediates are produced by upstream reactions.

Rates and dwell-time calculations retain the supplied model timebase. No unit conversion or correction of source kinetic units is made here.

## 2. 实际反应及四个状态

| Alias | Exact SBML species ID | Meaning supported by reaction chemistry |
| --- | --- | --- |
| `A = S0` | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` | Hydrolyzed docked complex; phosphate and EF-Tu-GDP still bound |
| `X1 = S1` | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` | Phosphate released; EF-Tu-GDP still bound |
| `X2 = S2` | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | EF-Tu-GDP released; precursor for peptide extension |
| `B = S3` | `elRS70SBGGU0002_Pept0002tRNAGlyGCC` | Peptide extended from fMet to Pept0002 |

```text
re0000000016: A  -> X1 + PO4       ; k16 = 1000
re0000000017: X1 -> X2 + EFTu_GDP  ; k17 = 7
re0000000018: X2 -> B             ; k18 = 1000
```

All stoichiometric coefficients in these three reactions are exactly one. Their summed column is:

```text
A -> B + PO4 + EFTu_GDP
```

This is a **stoichiometric path identity**, not proof that a single reaction has the same dynamics. `A` is already a GDP/phosphate state. The selected segment does not consume free GTP or ATP and does not include the preceding GTP hydrolysis (`re0000000014`). `re0000000018` is the actual peptide-extension event. It should not be relabeled as a nucleotide-conversion event.

The immediate inlet is `re0000000014`, which converts `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` into `A`; the immediate downstream EF-G binding is `re0000000019`, with active dissociation `re0000000020`. The boundary states remain connected to those surrounding reactions in any prototype comparison.

## 3. 内部节点有无旁支：必须区分两张图

| State | All canonical reaction incidences | Nonzero author-default incidences |
| --- | --- | --- |
| `A` | `re0000000014, re0000000015, re0000000016, re0000000036, re0000000037, re0000000038, re0000000060` | `re0000000014, re0000000016` |
| `X1` | `re0000000016, re0000000017, re0000000026, re0000000039, re0000000040, re0000000041, re0000000060, re0000000061, re0000000063` | `re0000000016, re0000000017` |
| `X2` | `re0000000017, re0000000018, re0000000027, re0000000045, re0000000046, re0000000061, re0000000062, re0000000064` | `re0000000017, re0000000018` |

The table counts reactant/product participation, including directions entering a state; it is not a count of outgoing branches alone. In the frozen author-default view, `X1` and `X2` each have one producing reaction and one consuming reaction, no active modifier incidences, and no active side exits.

The canonical full-network exceptions are chemically meaningful:

- `re0000000026/re0000000063`: release/rebinding of `GlytRNAGlyGCC` while EF-Tu-GDP remains ribosome-bound.
- `re0000000027/re0000000064`: release/rebinding of `GlytRNAGlyGCC` after EF-Tu-GDP has left.
- `re0000000060`: phosphate rebinding; `re0000000061`: EF-Tu-GDP rebinding; `re0000000062`: reverse peptide-extension direction.
- `re0000000039–re0000000041` and `re0000000045–re0000000046`: ribosome/factor degradation and component-release paths; `re0000000036–re0000000038` touch the boundary `A`.

These directions all have zero constants in the author-default overlay; they remain in the canonical source. If any is reactivated, this serial-chain argument must be repeated with its new boundary and resource ledger. A graph obtained by removing hubs or zero-rate edges is a derived diagnostic view, not a replacement for the source reaction network.

## 4. 原链的精确局部方程和账本

Write `a = [A]`, `x1 = [X1]`, `x2 = [X2]`, and let `u(t)` be the preserved upstream influx into `A`. Under the frozen author-default view:

```text
v16 = k16 a;      v17 = k17 x1;      v18 = k18 x2
da/dt  = u - v16
dx1/dt = v16 - v17
dx2/dt = v17 - v18
```

`B` has module-local production `v18`, plus its surrounding-network terms. `PO4` has module-local production `v16`; `EFTu_GDP` has module-local production `v17`. These are module contributions to shared-species balances, not assertions about the complete network's free-species trajectories.

Define directed extents `xi16, xi17, xi18` as time integrals of these fluxes, all starting at zero. Then:

```text
Delta x1 = xi16 - xi17
Delta x2 = xi17 - xi18
PO4 released by this module      = xi16
EFTu_GDP released by this module = xi17 = xi18 + Delta x2
B produced by this module       = xi18
```

Only once intermediate inventory has returned to its initial level does the completed-path ledger reduce to equal extents. Matching final peptide production alone does not prove the early phosphate/factor-release ledger.

The inventory-based ledger is also explicit: `A`, `X1` and `X2` each retain one occupied ribosome and the same fMet plus delivered Gly-tRNA cargo. `A` and `X1` retain EF-Tu-GDP, whereas `X2` does not; only `A` retains the phosphate represented in this segment. Thus ribosome and precursor cargo occupancy can be summed directly, while EF-Tu occupancy is stage-dependent.

## 5. OPTION A — 直接有效反应

**Proposed class: `DIRECT_LUMP_CANDIDATE`; `HUMAN_REVIEW_REQUIRED = true`.**

```text
A -> B + PO4 + EFTu_GDP      with effective flux J_eff
```

The resource products must be shown. A bare `A -> B` diagram is shorthand for this complete net reaction, not permission to discard its byproducts.

For a particle starting in `A`, a constant-rate irreversible three-stage path has mean completion dwell time:

```text
tau_A = 1/k16 + 1/k17 + 1/k18
      = 0.144857142857...  model time units
k_eff,A = 1/tau_A = 6.903353057...  inverse model time units
```

`J_eff = k_eff,A a` is a possible mean-matched candidate, not a validated flux law. It shifts the hidden dwell time into the boundary state `A`, so the meaning and residence time of `A` change. It simultaneously emits phosphate and EF-Tu-GDP at completion, while the original releases phosphate at admission to `X1` and EF-Tu-GDP before peptide formation. It also removes the separate occupied-ribosome inventory `x1 + x2`.

For zero initial `X1/X2`, the exact inlet-to-completion transfer function is:

```text
H_full(s) = k16 k17 k18 / [(s+k16)(s+k17)(s+k18)]
H_direct(s) = k_eff,A / (s+k_eff,A)
```

These functions differ. For an impulse cohort initially in `A`, the original completed fraction starts at order `t^3`, whereas the direct exponential starts at order `t`. A direct Markov step cannot exactly preserve arbitrary transient input histories. An exact memory/delay description can preserve the path response but does not constitute a one-rate mass-action closure.

**Preserved conditionally:** endpoint identity, completed-path stoichiometry, a chosen mean dwell time, eventual cargo conversion. **Lost or shifted:** internal occupancy, stage release timing, waiting-time distribution, source reaction fluxes and sensitivity to reactivated side paths. Amino-acid/resource totals are recoverable only if hidden inventory and emitted byproducts are explicitly reconstructed or their discrepancy is bounded. Later local QSSA is possible, but cannot establish retrospectively that this direct coarse-graining was acceptable.

## 6. OPTION B — 保留聚合态 `E_mid`

**Proposed class: `AGGREGATE_STATE_CANDIDATE`; preferred first prototype for human review; `HUMAN_REVIEW_REQUIRED = true`.**

Define `E_mid = x1 + x2`, retaining `A` and `B` as boundaries:

```text
A -> E_mid + PO4          ; admission J_in = k16 a
E_mid -> B + EFTu_GDP     ; candidate completion J_out
```

The exact aggregate identity is:

```text
dE_mid/dt = v16 - v18 = k16 a - k18 x2
```

It preserves internal ribosome occupancy and precursor cargo count exactly as a coordinate sum. It does **not** close the dynamics: `v18` depends on `x2`, not just `E_mid`. Two microscopic states with the same `E_mid`, one entirely in `X1` and the other entirely in `X2`, have different output fluxes and EF-Tu-GDP occupancies.

A candidate one-state completion law can match the mean dwell time **after admission**:

```text
tau_E = 1/k17 + 1/k18 = 0.143857142857... model time units
k_eff,E = 1/tau_E = 6.951340615... inverse model time units
J_out = k_eff,E E_mid
```

This is a different rate from Option A, because the `A -> E_mid` wait remains explicit. Matching the post-admission mean is an assumption for prototype comparison, not proof of a Markovian lump. The full post-admission waiting kernel has two factors, `(s+k17)(s+k18)`; the candidate has one.

The proposed phosphate release remains tied to `J_in`, matching the original module's phosphate event. Assigning EF-Tu-GDP release to `J_out` instead of `v17` incurs the exact integrated discrepancy `Delta x2` for the original path. The occupied precursor amount `E_mid` alone does not reveal its Tu-bound fraction `x1/E_mid`. Therefore an exact EF-Tu inventory cannot be assigned to a fixed chemical composition for `E_mid` without additional stage information.

Ways to handle this scientifically are review alternatives:

1. Keep a progress fraction or stage-specific occupancy/extent ledger; demonstrate its closure and count its added dimension honestly.
2. Use a delay/memory kernel, which retains history rather than claiming an exact one-state Markov model.
3. After this topology-defined aggregation, test a local assumption such as a small downstream `x2` inventory or a supported conditional stage fraction; report the domain and error in output and EF-Tu balances.

An exact memory expression makes the limitation visible:

```text
dx2/dt = k17 E_mid - (k17+k18) x2
x2(t) = exp[-(k17+k18)t] x2(0)
        + k17 integral_0^t exp[-(k17+k18)(t-q)] E_mid(q) dq
```

This closes `E_mid` using history, not using its instantaneous amount alone. A counter alone supplies bookkeeping, not an independently justified instantaneous completion law.

**Preserved:** explicit admission and phosphate release, occupied-ribosome and precursor-cargo pool, completion stoichiometry at the chosen approximation level. **Requires additional closure or error bounds:** EF-Tu occupancy/release, completion dynamics, startup delay and any restored side path. Local QSSA belongs here, after the topological boundary and observables have been defined. No measured gate or numerical trajectory validation has yet been performed.

For clarity, another coordinate sometimes useful for an open module is `E_all = a + x1 + x2`, with exact derivative `dE_all/dt = u - v18`. Its mean dwell includes all three waits and gives `k_eff,A` above. `E_all` is not the same candidate as the required `A -> E_mid -> B`; they must not share an unlabeled rate or inventory interpretation.

## 7. OPTION C — 保留显式链

**Proposed class: `KEEP_EXPLICIT` when required observables or condition scope demand it; `HUMAN_REVIEW_REQUIRED = true`.**

Keep `A, X1, X2, B` and `re0000000016/0017/0018` within the complete network. This is the comparison baseline. Preserve the source directions and their condition-specific zero constants; do not erase disabled paths.

Explicit retention is required if the intended scope includes phosphate/EF-Tu release timing, microscopic flux/extent observables, a nonnegligible intermediate occupancy, arbitrary nonzero initial internal inventories, or reactivation of a relevant side path that has not been represented in the coarse module. It preserves the source resource ledger and local mechanistic identity. It does not reduce dimension, but still permits a later independently justified local QSSA or another coordinate change.

## 8. 重复链增长确实存在，但只有两个 Gly 加成

The second Gly addition repeats the selected chemistry:

```text
re0000000077:
elRS70SAGGU0003_Pept0002_EFTu_GDP_PO4_GlytRNAGlyGCC
 -> elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC + PO4

re0000000078:
elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC
 -> elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC + EFTu_GDP

re0000000079:
elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC
 -> elRS70SBGGU0003_Pept0003tRNAGlyGCC
```

The author-default constants are likewise `1000, 7, 1000`. The full first-elongation forward backbone is `re0000000013 → 0014 → 0016 → 0017 → 0018 → 0019 → 0022 → 0024 → 0025`; its repeated counterpart is `re0000000074 → 0075 → 0077 → 0078 → 0079 → 0080 → 0083 → 0085 → 0086`. These backbone names abbreviate the common `re000000` prefix only within this sentence.

The actual model is fMGG tripeptide synthesis: fMet-to-Pept0002 and Pept0002-to-Pept0003. There is no long arbitrary-length chain-state lattice in this canonical model. Matching two motif patterns does not establish that their boundary environments, initial histories or downstream constraints are interchangeable, nor justify merging peptide lengths automatically.

For the larger first-elongation path, summing its forward stoichiometry gives:

```text
elRS70SAGGU0002_fMet + EFTu_GTP_GlytRNAGlyGCC + EFG_GTP
 -> elRS70SAGGU0003_Pept0002tRNAGlyGCC
    + EFTu_GDP + EFG_GDP + 2 PO4
```

This consumes one already-loaded Gly-tRNA carrier and two loaded GTP-factor resources per completed forward path. It does not directly write free ATP consumption. Free-GTP loading/exchange, aminoacylation ATP-to-AMP/PPi use, amino-acid charging, energy regeneration and later tRNA recycling belong to surrounding modules and must be preserved when interpreting the full ledger.

The larger path includes active returns: `re0000000021` undocks the initial carrier, `re0000000020` releases EF-G-GTP, and `re0000000023` reverses the bound EF-G nucleotide-conversion step. It is a chain with local cycles, not a branch-free serial chain. A larger elongation aggregate is a possible later extension only after preserving these boundary returns, conditional resource occupancy and completion closure; the strict three-step prototype should be assessed first.

## 9. 人工审查与验证顺序

The defensible meeting message is **“Topology first, QSSA second”** and **“Repeated chain growth can sometimes be lumped into an effective step or an aggregate state.”** In this model, “sometimes” refers to a condition-bound serial segment with explicit resource products, not automatic removal of all repeated elongation states.

The next human review should decide the permitted condition domain and required output/resource observables, then compare Options A/B/C for this one segment. Record whether startup differences are allowed and how they will be measured before numerical validation. Required comparisons include medium/long-time peptide output, occupied-ribosome inventory, phosphate and EF-Tu ledgers, and dependence on upstream time-varying input. GTP/ATP/amino-acid ledgers must also be checked in the coupled full network, without attributing unrelated surrounding events to the selected segment.

The local kinetic assumption for `J_out` must be reviewed separately from the exact topology and sum identities. All proposal choices remain `HUMAN_REVIEW_REQUIRED`; existing frozen evidence, failed gates and source scientific decision records remain authoritative and unchanged.
