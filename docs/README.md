# docs/

Documentation by semantics, not by date.

- `project/` — project-level registers: `benchmark_registry.md`,
  `evidence_levels.json`, `licensing_review.md`.
- `validation/` — execution and validation reports (`benchmark_v0.md`,
  `qc_v0.json`).
- `audit/` — audit status, protocols, human checklists, dimensionless audit,
  and persisted evidence logs.
- `interfaces/` — frontend/data contracts and the low-fidelity layout
  description (`flow_contract.json`, `frontend_wireframe.md`).
- `reports/` — gate/final reports and human follow-up lists
  (`g1_report.md`, `g1_pending_human_actions.md`).
- `model_card.md` — canonical human-readable B1 model description.
- `theory_notes.md` — current theory derivation notes, including the audited
  12-state nondimensional model.

Current PNAS work adds `pnas2017/` for source/SBML/chemical audits,
`reduction/` for process-oriented decisions and candidate structure, and
`visualization/` for the implemented offline presentation and its data contract. The older B1
register, model card and theory records retain their historical Mavelli scope.

The current limited-domain milestone is **PNAS2017_PHASE_C_REDUCTION_V1_20261010**.
Historical pending reports retain their original bytes and are connected to
the current decision through the additive release navigation below.

- [既有 HTML 图谱 / Phase C 总览](visualization/reduction_reasoning_atlas.html)
- [B1-2 既有接受记录](reduction/pathways/phase_b1_2_formal_signoff_2026-10-10.md)
- [B1-3 正式限定接受](reduction/pathways/phase_b1_3_formal_acceptance_20261010.md)
- [Phase C 正式接受及全部条件](reduction/rapid_reduction/phase_c_formal_acceptance_20261010.md)
- [复现、环境、失败保留与发布说明](reduction/rapid_reduction/release_notes_v1.md)
- [文件分类和哈希清单](reduction/rapid_reduction/release_manifest_v1.json)
- [证据 / 历史决定 / 当前决定关系图](reduction/rapid_reduction/release_evidence_navigation_v1.json)
- [数学证书](reduction/rapid_reduction/mathematical_certificate.json) · [冻结数值报告](../results/reduction/rapid_v1/validation_results.json) · [实际 runtime](../scripts/reduction/rapid_v1/runtime.py)

R1/R2 精确坐标、R3_RECYCLE 精确观测商和 Gly 近似有不同适用域；171 化学维
加 20 计数器为 191 积分坐标，仍非普遍验证的 `PURE_reduced_core`，没有计算提速。

Planned (create only when content exists): `models/`, `theory/`
(conservation, reduction, stability, flow thermodynamics). Never create
time-based folders (`week1/`, `D6/`, `final2/`, ...).
