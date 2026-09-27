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
`reduction/` for process-oriented **unapproved** decisions and candidate
structure, and `visualization/` for a data-contract plan. The older B1
register, model card and theory records retain their historical Mavelli scope.

Planned (create only when content exists): `models/`, `theory/`
(conservation, reduction, stability, flow thermodynamics). Never create
time-based folders (`week1/`, `D6/`, `final2/`, ...).
