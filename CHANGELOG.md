# Changelog

All notable repository-level changes. The scientific model content
(`PURE_literature_reference`) is frozen after B1; entries below are
organizational/engineering changes unless stated otherwise.

## [0.1.0-b1] - 2026-09-18 (B1 freeze; tag `b1-reference-v1`)

### Added
- Repository structure: `references/`, `models/{literature_reference,pure_resource_core,fixtures}/`,
  `configs/`, `schemas/`, `matlab/{src,codegen,generated,tools,tests}/`,
  `scripts/`, `results/{baselines,runs,releases}/`, `docs/{project,validation,audit}/`.
- Section READMEs documenting what belongs where; this changelog.
- `.gitattributes` pinning `*.json` to LF so provenance SHA-256 hashes
  reproduce on fresh checkouts.
- `scripts/reproduce_b1.m` entry point (wraps `run_fig4_benchmark`).

### Changed
- Branch `audit/b1-hardening` fast-forwarded into `main` (no merge commit);
  branch deleted after integration.
- `results/literature_reference/` moved to `results/baselines/b1_mavelli2015/`
  (frozen regression baseline).
- Provenance-bound hardening rerun slimmed to its provenance evidence
  (`results/baselines/b1_mavelli2015/audit/hardening_20260918/`) after its
  trajectory/rates were verified byte-identical to the baseline.
- New runs write unversioned `results/runs/<run_id>/` (gitignored).
- Historical audit test logs moved from `logs/` to `docs/audit/logs/`.

### Verified (after reorganization)
- 18/18 unit tests, smoke test, release preflight (development mode) pass.
- B1 Fig. 4 benchmark byte-identical before/after for all three DNA
  conditions (0.34 / 1.7 / 6.8 nM).

### No scientific changes
- No change to equations, rate laws, states, stoichiometry, multiplicity
  coefficients, parameters, initial conditions, observables, solver
  tolerances or benchmark conditions.
