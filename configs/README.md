# configs/

Run conditions and experiment settings. **Model ≠ run condition**: e.g.
DNA = 0.34 / 1.7 / 6.8 nM are three *conditions* of one model, not three
models.

- `benchmarks/` — registered benchmark configurations (e.g. `b1_fig4/`).
- Planned: `core/` (PURE_resource_core runs), `stochastic/` (SSA runs).
- What does NOT go here: model equations or parameters (those live in
  `models/`), results (belong in `results/`).
