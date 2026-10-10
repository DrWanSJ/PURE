# PURE — Cell-Free Expression Modeling Workbench

This repository studies PURE cell-free expression with explicit model,
source, simulation, audit and decision boundaries. The active detailed
benchmark is the **mRNA-directed translation** network of Matsuura et al.
(PNAS 2017, DOI: [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114)).
Transcription and GUV transport are future project extensions; they are not
part of the imported PNAS reference model.

## Scientific status and model identities

| Identity | Role | Status |
| --- | --- | --- |
| `PNAS2017_full_reference` | Literal, provenance-bound SBML import of the Matsuura et al. translation network; benchmark and inventory only | **Paper PDF and S01–S29 captured; audit and interpretation ongoing**; no scientific modification permitted |
| `PNAS2017_PHASE_C_REDUCTION_V1_20261010` | Versioned fMet–Gly–Gly reduction research milestone: 241 → 214 → 175 → conditional 171 chemical dimensions | **Formally accepted within the reviewed domains on 2026-10-10**; exact coordinates, observable quotient and approximate Gly aggregation remain distinct |
| `PURE_reduced_core` | Future interpretable project model derived from explicit, human-reviewed reduction decisions | **Proposal only**; no validated model yet |
| `Mavelli2015_coarse_reference` | Mavelli, Marangoni and Stano (2015) coarse-grained comparator, DOI: [10.1007/s11538-015-0082-8](https://doi.org/10.1007/s11538-015-0082-8) | **Frozen legacy benchmark**, completed through the previous D7 RS-QSSA work |

The publisher PDF and S01–S29 files are now preserved with hashes alongside
the author-site files; see the [source capture](references/PNAS2017_Matsuura/README.md).
The [G1-PNAS evidence report](docs/pnas2017/g1_pnas_report.md) records the
pre-integration gate, when those publisher files were missing. Its source
blocker is historical, while chemical-unit, dataset-comparison and human-review
work remains open; G1 has not been rerun. The migrated
[reduction evidence](docs/reduction/pnas2017_historical_evidence.md) retains
its failed and blocked outcomes. [Open scientific decisions](docs/reduction/open_scientific_decisions.md)
do not constitute model approval.

The Mavelli benchmark remains valid for its coarse-grained question. It is no
longer the primary benchmark because the revised question requires the
detailed translation reaction network and explicit small-molecule/resource
accounting. The existing Mavelli code and evidence remain in their current
paths. Historical results retain their original scope and acceptance status;
they are not evidence that the new PNAS model or a future reduced core has been
validated. The legacy B1 human source-to-repository audit was completed for
literature reproduction, not independent experimental validation.

The active sequence is: freeze and inventory the original PNAS sources;
validate and execute the unchanged SBML where possible; classify reaction
families and chemical flows; prepare candidate transformations with their
information loss; obtain **human scientific decisions**; then construct and
validate a reduced model. Similar protein output alone is not a deletion
criterion. The proposed reduced core must retain the information needed for
ATP/GTP, AMP/ADP/GDP, Pi/PPi, creatine phosphate/creatine, amino acids,
tRNA charging, translation-machine occupancy and an explicitly qualified
osmotic-particle proxy. Quantitative ionic-strength accounting requires
defined charges, protonation and Mg-binding conventions.

## Current research milestone / 当前展示入口

打开已有的 [PNAS2017 降维推理图谱（已升级 Phase C 总览）](docs/visualization/reduction_reasoning_atlas.html)。页面可离线使用，保留旧图谱，并提供四个冻结场景的真实轨迹、三个源时间窗口、数学分支、数值门、运行时间与科学限制。**171 是化学状态维数，不是反应数**；另有共同的 20 个积分计数器，合计 191 个积分坐标。

研究者通过 2026-10-10 会话正式接受 [B1-3 限定结构范围](docs/reduction/pathways/phase_b1_3_formal_acceptance_20261010.md)（H1–H3=Y，H4–H9=CONDITIONAL）和 [Phase C 限定科研结论](docs/reduction/rapid_reduction/phase_c_formal_acceptance_20261010.md)。[B1-2 既有接受与限制](docs/reduction/pathways/phase_b1_2_formal_signoff_2026-10-10.md)保持原样。接受来源是会话指令，未虚构手写签名或批准时刻。

R1 214 维为 SOURCE_GENERAL 精确守恒坐标；R2 175 维在作者参数/初值支持面上精确；R3_RECYCLE 173 维为受保护观测的精确商系统；R3_CHAIN1 174、R3_CHAIN12 173 与组合 R3_CHAIN12_RECYCLE 171 均含近似 Gly 聚合。两个 173 维模型并不相同。最终 171 维是四情景长期窗口条件科研候选，**尚未实现计算加速**，不支持一般参数、任意初值、全微观逆重构、一般蛋白序列或电荷/渗透压认证。旧 QSSA 失败不因本次接受而改变。

- [发布说明与复现入口](docs/reduction/rapid_reduction/release_notes_v1.md) · [完整文件分类、SHA-256 与保存位置](docs/reduction/rapid_reduction/release_manifest_v1.json)
- [当前决定](docs/reduction/rapid_reduction/current_decision_v1.json) · [源与决定的结构化导航](docs/reduction/rapid_reduction/release_evidence_navigation_v1.json)
- [Phase C 数学证书](docs/reduction/rapid_reduction/mathematical_certificate.json) · [实际降阶实现](scripts/reduction/rapid_v1/runtime.py) · [冻结数值报告](results/reduction/rapid_v1/validation_results.json)
- [独立数学审查原文](docs/reduction/rapid_reduction/independent_mathematical_audit_20261010.md) · [本次新执行的复核](results/reduction/phase_c_release_v1/)

```powershell
python -B scripts/reduction/rapid_v1/release.py verify --run-id my_verification_001 --require-manifest
python -B scripts/reduction/rapid_v1/release.py reproduce --run-id my_reproduction_001 --require-manifest
Start-Process docs/visualization/reduction_reasoning_atlas.html
```

新复现写入独立目录并拒绝已有 run-id；不会覆盖冻结科学证据。环境与详细执行步骤见发布说明。277 个原始研究文件全部版本化，包括原始轨迹、早期评分结果与失败证据，另一台电脑取得该发布提交后可直接校验。

后续仅列为建议：优先研究稀疏坐标/Jacobian 的速度优化，其次研究保留动态资源储存的能量模块简化，再扩大条件 171 维模型的适用域。本次未启动这些工作。

## Repository layout

```text
references/                         source files and provenance
  R01_Mavelli2015/                  legacy literature source
  PNAS2017_Matsuura/                captured publisher and author sources
models/
  literature_reference/             frozen Mavelli B1 implementation
  pnas2017_full_reference/          immutable import, normalization and audit
  pure_reduced_core/                future human-reviewed model
  pure_resource_core/               earlier project-model planning material
  fixtures/                         B0 known-answer models
configs/                            run conditions
data/                               raw, processed and audit data
matlab/                             legacy simulation, generated code and tests
results/                            baselines, ordinary runs and release evidence
docs/                               scientific, validation and audit records
```

The PNAS SBML is the scientific source of truth for the detailed benchmark.
Normalized inventories and solver outputs are derived artifacts. A handwritten
MATLAB or Python ODE must not replace the imported reference definition.
Source files are preserved byte-for-byte with URLs, access notes, sizes and
SHA-256 hashes. Unsupported solver imports and unresolved scientific checks
remain recorded rather than reconstructed from descriptions.

## Legacy Mavelli reproduction

The existing B1 workflow remains available for historical comparison:

```bash
matlab -batch "addpath('scripts'); reproduce_b1"
```

Ordinary B1 outputs go to `results/runs/<run_id>/`; frozen regression data
remain under `results/baselines/b1_mavelli2015/`. Its generated-code chain is

`models/literature_reference/model_definition.json` →
`matlab/codegen/generate_pure_literature_reference.m` →
`matlab/generated/rhs_pure_literature_reference.m`.

Do not edit generated B1 code by hand or reinterpret it as the PNAS model.

## Existing tests and evidence

```bash
matlab -batch "addpath('scripts'); run_all_tests"
```

This is the existing MATLAB suite for B0 fixtures and the Mavelli B1
workflow. Passing it does not validate the new PNAS reference or future
project reduction. Reports must distinguish executed tests, failed or pending
checks, source review, solver integrity and experimental validation.

`data/raw/` and new reference-source directories are immutable inputs.
Processed data must be reproducible from registered sources and tools, with
licensing status recorded. B0 synthetic parameters do not become PURE
experimental inputs. The 2026-10-10 release has an explicit exception for
the inventoried 26 B1-3 and 251 Phase C untracked outputs on the authorized
`codex/energy-cycles-v1` branch; all other preflight and history protections apply.

The current execution order and **G1-PNAS** gate are in [tasklist.md](tasklist.md).
Future phases include a human-approved `PURE_reduced_core`, transcription
extension, GUV transport, flow visualization and MCP access to audited
computations.
