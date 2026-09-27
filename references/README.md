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

## Active PNAS source archive

`PNAS2017_Matsuura/` holds the primary Matsuura et al. 2017 translation
benchmark files obtained from the authors' simulator site. Their exact
download URLs, byte counts, SHA-256 values, access date and rights status are
in `PNAS2017_Matsuura/provenance/sources.json`. Publisher article/SI and
Datasets S01–S29 that could not be frozen are explicitly listed in
`PNAS2017_Matsuura/MISSING_SOURCES.md`. The author-site combined SBML is not
silently relabeled as publisher Dataset S27.
