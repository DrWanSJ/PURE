# Matsuura et al. 2017 primary benchmark sources

**Citation:** Matsuura T, Tanimura N, Hosoda K, Yomo T, Shimizu Y. *Reaction dynamics analysis of a reconstituted Escherichia coli protein translation system by computational modeling.* PNAS 2017;114(8):E1336–E1344. DOI: [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114).

**Scope:** The reference describes mRNA-directed PURE **translation**, including aminoacylation and energy regeneration. It does not supply a DNA-to-RNA transcription or membrane-transport module. The author's [PURE system simulator page](https://sites.google.com/view/puresimulator) describes 26 SBML modules, one merged SBML model, and a separate MATLAB implementation for fMGG synthesis. The [PNAS article](https://www.pnas.org/doi/10.1073/pnas.1615351114) reports 241 components, 27 initially present components, and 968 reactions; these are published claims to audit against the acquired model, not counts inferred from filenames.

## Frozen author-site files

The following files were acquired on **2026-09-24** from the links on the author's simulator page. Byte counts and SHA-256 hashes below are recorded in [`provenance/sources.json`](provenance/sources.json). Raw files are immutable source captures; audit exports and simulations belong outside `raw/`.

| Original filename | Author-site role | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| [`fMGG_synthesis.xml`](raw/fMGG_synthesis.xml) | Merged model; downloaded from [author's Google Drive file](https://drive.google.com/file/d/17hCxjOpbypq-ri2gOEL-ByTDQNlIit-2/view?usp=drive_link) | 1,732,620 | `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df` |
| [`SBML_files.zip`](raw/SBML_files.zip) | Archive advertised as the 26 individual SBML modules; [author's Google Drive file](https://drive.google.com/file/d/1IQ2cBPcF4uBM4lc1Mn7u3ae8XQLNsJij/view?usp=drive_link) | 250,427 | `24f0748c883eb6dcb748c20de7fdb2c8e495397f4b8ffb6c82246a03f0a93b03` |
| [`Simulate_fMGG_synthesis.zip`](raw/Simulate_fMGG_synthesis.zip) | MATLAB sample code and initial-value, parameter, and reaction CSV files; [author's Google Drive file](https://drive.google.com/file/d/1qnRPhyw2p_8tAy4kNY7Vd1SkEcb6x5xy/view?usp=drive_link) | 46,143 | `beb27ebbd314133fbd83f68dcf8ad2ebe08cb16a1adda170b6b7b408ad355b52` |

The merged XML was inspected as SBML. The ZIP files were inspected as archives; archive member names and extensions alone are insufficient to establish the format of every member. The original merged model has a byte-identical copy at `models/pnas2017_full_reference/original/fMGG_synthesis.xml`; its checksum is recorded in `provenance/sources.json`. The MATLAB and CSV files are supporting execution/provenance material, not the canonical chemical-network definition.

The author's page displays no explicit reuse license for these downloads. The PNAS article is described in [PMC metadata](https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:5338406&metadataPrefix=oai_dc) as “Freely available online through the PNAS open access option”; that statement alone does not establish a Creative Commons or software reuse license. Preserve attribution and check rights before redistribution beyond this source archive.

## Publisher paper and supplementary capture

The researcher accepted the PDF and `pnas.1615351114.sd01.xlsx` through `sd29.xlsx` carried by research commit `025fd340300a56f069c2136ea8bb0ff542b046d4` as the official PNAS supplementary source set. Their 2026-09-24 local acquisition record, byte counts and SHA-256 hashes are retained in [`provenance/source_manifest.csv`](provenance/source_manifest.csv). Individual publisher download URLs were not recorded in that capture. The publisher-source acceptance is a researcher decision; the recorded hashes bind these repository bytes but are not a new independent publisher-download comparison.

S27 opens as an XLSX workbook with initial-concentration, reaction/parameter, parameter-reference and validation-simulation sheets. S28 opens as an XLSX workbook with figure-data sheets. The [PNAS Methods](https://www.pnas.org/doi/10.1073/pnas.1615351114) describes a combined SBML in connection with Dataset S27, while the [PMC attachment listing](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/) names an XLSX. The author-site `fMGG_synthesis.xml` remains the canonical imported SBML; it is not silently equated to the publisher S27 workbook. The author CSVs remain a separate execution source.

[`MISSING_SOURCES.md`](MISSING_SOURCES.md) records the earlier 2026-09-24 acquisition attempt and is historical. A separately named complete Supporting Information text/PDF was not established by that attempt. Presence of S28 does not itself establish a validated trajectory comparison or change any reference-reproduction gate.
