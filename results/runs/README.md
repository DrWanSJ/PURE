# results/runs/

Ordinary simulation runs live here, one directory per run:
`results/runs/<run_id>/` with `manifest.json` (live git commit, dirty-tree
status, SHA-256 of model definition / parameters / inputs), per-condition
`trajectory.csv`, `rates.csv`, `qc.json`, figures and `benchmark_summary.json`.

Everything under `results/runs/` is **gitignored**: runs are reproducible from
the manifest + code; only baselines (`results/baselines/`) and release evidence
(`results/releases/`) are committed. Never paste run outputs into `baselines/`.
