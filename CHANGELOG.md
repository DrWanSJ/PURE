# Changelog

All notable repository-level changes. The scientific model content
(`PURE_literature_reference`) is frozen after B1; entries below are
organizational/engineering changes unless stated otherwise.

## [Unreleased] - 2026-09-26 (aminoacylation A3b/A3c candidate cycle)

### Added
- A3a closed as a completed negative candidate (`docs/reduction/aminoacylation_A3a_final_status.md`).
- Phase-2 coordinate framework + protected-ledger basis for the A3b/A3c
  candidates (`scripts/analyze_pnas2017_aa_a3bc_coordinates.py`; artifacts under
  `docs/audit/pnas2017_aminoacylation_A3b/`, `..._A3b_r12/`, `..._A3c/`).
- A3b total-coordinate runner and core (`scripts/run_pnas2017_aa_a3b_formal.m`,
  `scripts/a3b_*.m`), pre-QSSA B1-B10 verifier, anti-sliding-leak validator,
  closure-failure investigation helper, and the cycle validator
  (18 PASS / 0 FAIL / 3 explained SKIP).

### Scientific results (negative; permanent evidence)
- A3b-21: transform exact, sliding leak absent by construction, but the 21-state
  closed-loop QSSA fails the smoke gate (closure feasibility loss at t=2.498 s).
- A3b-r12 (restricted 9-state fast set): closure tracks FULL to 3-5 digits and
  exact ledgers hold to 1e-14 post-layer; full-window smoke blocked by the audited
  Met/Gly material / adenine ledger rows cutting fast binding equilibria; the
  token-closed ledger derivation requires human review.
- A3c: the conservative rule admits no elimination (0/21 states eligible).
- Aminoacylation reduction paused for human review
  (`docs/reduction/aminoacylation_A3bc_final_decision.md`).

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
