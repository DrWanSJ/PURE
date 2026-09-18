# results/

Simulation outputs, with a strict tiering:

- `baselines/` — **frozen regression baselines** (committed, never overwritten,
  never extended by ordinary runs). `b1_mavelli2015/` is the B1 reference.
- `runs/<run_id>/` — ordinary simulation outputs. **Not versioned** (gitignored);
  each run carries its own `manifest.json` provenance.
- `releases/` — release evidence for versioned releases (e.g. D20 v0.1).

What does NOT go here: model inputs (`models/`, `configs/`), experimental or
literature data (`data/`). Nothing in `baselines/` may be regenerated casually;
compare new runs against a baseline instead of replacing it.
