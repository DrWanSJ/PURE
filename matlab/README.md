# matlab/

- `src/` — **hand-maintained, reusable scientific code** (simulators,
  analysis, provenance utilities). This is the only place where scientific
  code is written by hand.
  - `src/simulate/` — deterministic simulator + B1 benchmark driver
  - `src/provenance/` — git state, SHA-256, run-manifest helpers
- `codegen/` — model-definition → generated-code generators
  (`generate_pure_literature_reference.m`).
- `generated/` — **auto-generated code. Do not edit by hand**; regenerate via
  `codegen/`. Splitting per model (`generated/literature_reference/`) is
  deferred; the naming rule already applies.
- `tools/` — auxiliary tooling (`digitization/`: Fig. 4 raster digitizer).
- `tests/` — test suite (`runtests('matlab/tests')`). Categorization into
  unit/integration/acceptance is deferred to avoid breaking test discovery;
  `fixtures/` holds frozen fixtures (e.g. the baseline RHS snapshot used by
  the mutation-equivalence test).

Entry points for users live in `scripts/`, not here.
