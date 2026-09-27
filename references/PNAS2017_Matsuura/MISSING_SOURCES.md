# PNAS 2017 sources not yet acquired

**Checked:** 2026-09-24. **Article DOI:** [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114). This is an acquisition status record, not a claim that the publisher files do not exist. No missing file has been recreated or substituted with an author-site CSV.

## Required files still unavailable locally

| Source | Confirmed evidence | Acquisition status |
| --- | --- | --- |
| PNAS article PDF | [Official article page](https://www.pnas.org/doi/10.1073/pnas.1615351114) and [PubMed record](https://pubmed.ncbi.nlm.nih.gov/28167777/) identify the paper. | The publisher's [`/doi/epdf/`](https://www.pnas.org/doi/epdf/10.1073/pnas.1615351114) PDF request returned HTTP 403 in this environment. Article metadata and indexed HTML are available, but no PDF bytes were frozen. |
| Supporting Information text/PDF | The [paper](https://www.pnas.org/doi/10.1073/pnas.1615351114) cites “SI Results”, model construction, parameter assignment, and validation. Its footer points to the [publisher supplement landing page](https://www.pnas.org/lookup/suppl/doi:10.1073/pnas.1615351114/-/DCSupplemental). | The supplement landing page returned HTTP 403. A separately named SI PDF could not be established from accessible file listings, so no filename is guessed. SI text visible in article indexes does not constitute a frozen, complete Supporting Information artifact. |
| Datasets S01–S29 | The [PMC article's Supplementary Material listing](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/) identifies the 29 publisher attachments by filename and displays approximate sizes. | None of the original publisher XLSX attachments was retrieved or byte-verified. S27 and S28 remain priority acquisitions. |

The attachment names listed by PMC are:

```text
pnas.1615351114.sd01.xlsx  pnas.1615351114.sd02.xlsx  pnas.1615351114.sd03.xlsx
pnas.1615351114.sd04.xlsx  pnas.1615351114.sd05.xlsx  pnas.1615351114.sd06.xlsx
pnas.1615351114.sd07.xlsx  pnas.1615351114.sd08.xlsx  pnas.1615351114.sd09.xlsx
pnas.1615351114.sd10.xlsx  pnas.1615351114.sd11.xlsx  pnas.1615351114.sd12.xlsx
pnas.1615351114.sd13.xlsx  pnas.1615351114.sd14.xlsx  pnas.1615351114.sd15.xlsx
pnas.1615351114.sd16.xlsx  pnas.1615351114.sd17.xlsx  pnas.1615351114.sd18.xlsx
pnas.1615351114.sd19.xlsx  pnas.1615351114.sd20.xlsx  pnas.1615351114.sd21.xlsx
pnas.1615351114.sd22.xlsx  pnas.1615351114.sd23.xlsx  pnas.1615351114.sd24.xlsx
pnas.1615351114.sd25.xlsx  pnas.1615351114.sd26.xlsx  pnas.1615351114.sd27.xlsx
pnas.1615351114.sd28.xlsx  pnas.1615351114.sd29.xlsx
```

The file extensions above are publisher listing metadata, **not a verified statement about the actual downloaded bytes**. In particular, the paper calls the combined SBML file “Dataset S27,” while the public supplement listing calls S27 an XLSX attachment. Resolve this by acquiring and inspecting the actual S27 file; do not infer that either label is sufficient proof of its internal format.

## Access checks and next acquisition route

| Endpoint checked | Result on 2026-09-24 | Interpretation |
| --- | --- | --- |
| [PNAS article PDF](https://www.pnas.org/doi/epdf/10.1073/pnas.1615351114), [publisher SI landing page](https://www.pnas.org/lookup/suppl/doi:10.1073/pnas.1615351114/-/DCSupplemental), and a conventional `doi/suppl/.../suppl_file/` S27 URL | HTTP 403 | Publisher access blocked this execution environment. The conventional S27 path was only a candidate URL, not a confirmed publisher attachment link. |
| [PMC article and attachment route](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/) | The article is indexed with attachment names, but direct automated attachment requests returned `text/html` reCAPTCHA/error pages, not XLSX bytes. | A 200 response to a PMC attachment path must not be accepted without checking `Content-Type`, file signature, size, and opening the workbook. |
| [Europe PMC supplementary-files API](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5338406/supplementaryFiles) | HTTP 200 with an XML error: `Article with id PMC5338406 is not open access one`. | The status code does not mean supplement data was returned. |
| [PMC OAI-PMH metadata](https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:5338406&metadataPrefix=oai_dc) and [current PMC cloud access guide](https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/) | The metadata rights field reads “Freely available online through the PNAS open access option”; the current OA S3 bucket listing for prefix `PMC5338406.` returned `KeyCount=0`. | The article is not currently distributed in the PMC machine-readable OA cloud subset. The [legacy PMC OA FTP/API paths were retired in August 2026](https://pmc.ncbi.nlm.nih.gov/tools/textmining/). |

To complete acquisition, retrieve the original files through the publisher's interactive supplement page or an authorized institutional/publisher access path, then record the final URL, access date, exact filename, byte count, SHA-256, response MIME type, actual file signature, workbook contents, and license/rights statement. Keep downloaded bytes unchanged. Until then, simulations using the acquired [author-site files](README.md) may be compared to the paper, but must not be described as reproductions from a frozen publisher Dataset S27/S28.
