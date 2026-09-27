# PNAS 2017 reference and historical reduction runs

The `rr_cvode_author_csv_20260924/` directory is main's current two-engine
reference reproduction evidence. The `2026-09-24_authors_model_v0/`
trajectory and the eight `2026-09-25_*` and `2026-09-26_*` directories are
research-branch historical evidence. The
[`historical_archive_manifest.json`](historical_archive_manifest.json) binds
all 179 migrated run files (25,664,925 bytes) to the research commit, original
Git blobs and SHA-256 values.

| Historical family | Role | Scientific interpretation |
| --- | --- | --- |
| `2026-09-24_authors_model_v0/` | Author MATLAB trajectory used by structural comparisons | Historical source-derived trajectory, not a reduced-model acceptance |
| `2026-09-25_aa_v1_reference_tight/`, `2026-09-25_aa_v1_runner_selfcheck/` | Reference and runner checks | Numerical integrity evidence only |
| `2026-09-25_aa_v1_formal/`, `2026-09-25_aa_v1_formal_comparison/` | A3a v1 formal runs and comparison | Failed candidate evidence |
| `2026-09-26_aa_v1r1_smoke/`, `2026-09-26_aa_v1r2_formal/`, `2026-09-26_aa_v1r2_formal_comparison/` | A3a revised smoke, formal runs and comparisons | `FAILED_VALIDATION_ON_REFERENCE_DOMAIN` |
| `2026-09-26_aa_a3bc_smoke/` | A3b-21, A3b-r12 and negative-control smoke configurations and logs | A3b-21 failed closure; A3b-r12 blocked and not validated |

The historical candidate statuses and their limitations are indexed in
[`pnas2017_historical_evidence.md`](../../docs/reduction/pnas2017_historical_evidence.md).
Configs, solver logs, trajectories, raw statistics and comparison records are
kept as coherent run families. A new integration run must receive a new run ID;
it must not replace these files or inherit a historical validation outcome.
