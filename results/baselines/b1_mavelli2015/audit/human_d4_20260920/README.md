# D4 timing run audit snapshot — 2026-09-20

User-executed command:

```matlab
tic
run_fig4_benchmark('RunId','d4_timing_check')
elapsed_s = toc
```

- wall clock: **7.5450 s**
- MATLAB: R2025b Update 5
- all three DNA conditions: `passed_all_qc`
- max scaled mass-balance residual: **5.821e-15**
- max tightened-tolerance trajectory difference: **3.766e-9**
- source ZIP SHA-256: `b6477ac3498c5b64b0cf6e2e219fdb2858f6e3c40890a51b3921b5c7ded1a490`

The local folder was `PURE-main` without a `.git/` directory, so this run is
**not commit-bound**. The original manifest reported
`git_commit = unavailable_git_not_found` and `git_dirty = unknown`.
The benchmark runner previously hard-coded `provenance_status = provenance_bound`;
that inconsistency is fixed in the same repository update.

The supplied run's CSV numerical outputs are identical to the frozen B1 baseline after
Windows CRLF -> repository LF normalization, so no second full copy of the large CSVs is
committed. `docs/validation/qc_v0.json` is the canonical D4 machine-readable aggregate.
