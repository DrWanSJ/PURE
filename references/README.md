# references/

Source documents (papers) that the models reproduce or consult.

- What goes here: one subdirectory per reference (`R01_<Author><Year>/`) with the
  PDF, any normalized copy, a text conversion, and a README recording DOI,
  origin and hashes.
- What does NOT go here: derived data (belongs in `data/`), notes about the
  project's own models (belong in `docs/`).
- Source of truth for file identity: `data/provenance.csv` (SHA-256) and
  `environment_lock.md`.
- PDFs are committed as-is (licensing status in `docs/project/licensing_review.md`).
- R02 / R03 exist locally only and are intentionally not committed (see `.gitignore`).
