# MISSING_SOURCES / MISSING-CAPABILITY log

Honest record of what is **not** available or **not** yet done in this
acquisition + audit cycle. Nothing here has been fabricated or substituted
with a guess.

## Sources — availability

- **All 33 reference files are physically present** in
  `references/PNAS2017_Matsuura/raw/` with recorded SHA-256 (see
  `references/PNAS2017_Matsuura/provenance/source_manifest.csv`): the PNAS PDF,
  Supporting Information Datasets S1–S29 (xlsx), the combined `fMGG_synthesis.xml`
  (SBML), `SBML_files.zip` (26 subsystem SBMLs) and `Simulate_fMGG_synthesis.zip`
  (authors' MATLAB model + `dat/` CSVs).

- **MISSING: per-file direct download URLs.** The files were handed to the tree
  as one local drop (`ref-PNAS/`). The exact URL each file was downloaded from
  was not captured. The DOI (10.1073/pnas.1615351114) and the authors' model
  page (`https://sites.google.com/view/puresimulator`) are the recorded provenance
  anchors. **To close:** the researcher should confirm each file against the
  publisher / model-page and record the URL + licence.

- **UNVERIFIED against origin: no network access** in this environment
  (`pip`/web proxy error), so the local files could **not** be re-downloaded and
  byte-compared against the authors' site. Identity is therefore established only
  by content + hash, not by an online round-trip. **To close:** re-hash against a
  fresh download when connectivity is available.

## SBML tooling — capability gaps (these are NOT "missing sources" but they
## block two required validation steps)

- **MISSING: libSBML** (cannot `pip install`, no network). → `libSBML`
  syntax/consistency validation and the official SBML error/warning list were
  **not run**. Structural inventory was produced instead with Python
  `xml.etree` (see `scripts/parse_pnas2017_sbml.py`).
- **MISSING: libRoadRunner / Tellurium** (cannot install). → the designated
  **primary SBML numerical engine was not run**, and no RoadRunner import status
  exists.
- **PARTIAL: MATLAB SimBiology (R2025b) is available** and *did* import the SBML,
  but with defects that make an SBML-driven reproduction unreliable (details in
  `docs/pnas2017/reference_reproduction.md`).

## Datasets — parsed status

- **NOT YET PARSED: Datasets S1–S29.** They are present but not yet machine-read.
  `openpyxl` is unavailable (no network). xlsx is OOXML zip and **can** be read
  with the Python standard library; extracting the published time-courses (esp.
  **S27/S28**) for quantitative comparison is scheduled but not completed in this
  cycle. Until then the reproduction is compared to the authors' shipped model and
  the reported component counts, **not** to per-dataset numeric trajectories.

## Consequences for gating

The G1-PNAS gate item "reference network readable through SBML tooling" is
**partially** met: readable and fully inventoried, but **not** validated by
libSBML and **not** simulated by an SBML-standard engine in this environment.
This is explicitly recorded rather than papered over.
