# fixtures (B0 verification models)

Small, fully specified toy models for mathematical/software verification:

- `reversible_conversion` — **implemented**; deterministic solver,
  conservation, positivity and analytic-trajectory verification
- `birth_death` — pending
- `enzyme_qssa` — pending
- `appendix_a` — pending

These verify solver, conservation, reduction and stochastic machinery against
known analytical answers. They are NOT scientific claims about the PURE
system and must be labeled `synthetic_fixture`.

Implemented fixture models live in their own subdirectories under
`models/fixtures/`. MATLAB test code remains under `matlab/tests/`; do not
confuse these B0 scientific/software verification models with frozen
regression snapshots under `matlab/tests/fixtures/`.
