# data/

All non-model inputs and their provenance.

- `raw/` — immutable source material as acquired (renders of paper pages,
  raw digitizations). **Never modify, regenerate or overwrite raw files**;
  scripts must treat them read-only.
- `processed/` — derived, machine-readable data (`literature/R01/fig4/`:
  Fig. 4 digitization). Must be reproducible from `raw/` + the tool that made
  it (`matlab/tools/digitization/digitize_fig4.m`).
- `manual_audit/` — templates and results of blind human audits.
- `provenance.csv` — the single provenance ledger: what each file is, where it
  came from, its SHA-256 and licensing status.

What enters Git: everything here. What does not: new raw acquisitions without a
provenance row.
