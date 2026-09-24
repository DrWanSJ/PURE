# references/PNAS2017_Matsuura — PRIMARY BENCHMARK SOURCE

**Paper.** Matsuura T, Tanimura N, Hosoda K, Yomo T, Shimizu Y.
"Reaction dynamics analysis of a reconstituted *Escherichia coli* protein
translation system by computational modeling."
*PNAS* 2017, 114(8):E1336–E1344. DOI: [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114)

This directory holds the **immutable, provenance-registered original files**
for the new primary benchmark (`PNAS2017_full_reference`). It is the literal
imported reference model — **no scientific modification is ever applied here**;
derived/normalised artefacts live under `models/pnas2017_full_reference/`.

> Licensing note: these are publisher- and author-supplied files retained for
> scientific reproduction of the reference network. They are not to be edited,
> re-rendered, re-zipped or "fixed"; the recorded hashes are the provenance
> chain. Do not redistribute beyond the project's permitted-use review.

## Layout

```
raw/          33 downloaded originals (never edited) — see source_manifest.csv
provenance/   source_manifest.csv  (filename, bytes, SHA-256, access date)
```

## Contents of `raw/`

| file(s) | what it is | verified format |
| --- | --- | --- |
| `matsuura-et-al-2017-...-by.pdf` | PNAS 2017 article | PDF |
| `pnas.1615351114.sd01..29.xlsx` | Supporting Information Datasets S1–S29 | OOXML xlsx |
| `fMGG_synthesis.xml` | combined fMGG reaction-network model | **SBML L2V4** (confirmed by header, not by name) |
| `SBML_files.zip` | 26 per-subsystem SBML files (SBML L2V4, CellDesigner export) | ZIP |
| `Simulate_fMGG_synthesis.zip` | authors' MATLAB simulator + `dat/` CSVs (initial values, parameters, reactions) | ZIP |

Exact byte counts and SHA-256 hashes of every file:
[`provenance/source_manifest.csv`](provenance/source_manifest.csv).

## Source of acquisition

Files were assembled by the researcher from the publicly accessible primary
sources (PNAS article + Supporting Information for DOI 10.1073/pnas.1615351114,
and the authors' model distribution). They were provided to the working tree in
`ref-PNAS/` on **2026-09-24** and copied unchanged into `raw/`. Individual
per-file download URLs were not recorded at drop time — see
`MISSING_SOURCES.md`. The SHA-256 hashes, not URLs, are the authoritative file
identity.

## Published reference counts (target of the audit)

241 components · 27 initially present · 968 reactions · 26 subsystems ·
combined model · MATLAB ODE simulation. All confirmed against the SBML — see
`docs/pnas2017/sbml_audit.md`.
