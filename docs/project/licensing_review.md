# licensing_review.md — copyright / source-file risk register

**Status:登记 only (registration only). No file has been removed, no history
rewritten, no `git filter-repo` executed. A HUMAN decision is required.**

Recorded: 2026-09-18, branch `audit/b1-hardening`.

## Tracked files of concern

| file | nature | sha256 (locked) | notes |
| --- | --- | --- | --- |
| `references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE.pdf` | full published paper (Springer Nature, *Bulletin of Mathematical Biology* 77:1185–1212, © Society for Mathematical Biology 2015), original, password-protected | `7082156c…c93238a3` | redistributed in the repository as-is |
| `references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE_normalized.pdf` | same paper, decrypted/normalized (Ghostscript) copy | `838d1f5d…6b4bb7d0` | created to enable page-by-page audit and the Fig. 4 digitization |
| `references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE.md` | full-text transcription/conversion of the same paper | `b47bb4e0…37af8` | contains the complete body text incl. all equations/tables |
| `data/raw/literature/R01/mavelli2015_fig4_page14_300dpi.png` | 300-dpi render of page 14 (contains Fig. 4) | tracked | derivative of the publisher's figure; kept so the digitization is auditable |
| `data/processed/literature/R01/fig4/fig4_digitized.csv`, `…_all_clusters.csv` | digitized coordinates of Fig. 4 calculated curves | tracked | derived data from the publisher's figure |

Copyright status recorded in `data/provenance.csv`: publisher copyright;
equations/tables are quoted for scientific reproduction with full citation —
standard scholarly practice for the *content*, but **redistribution of the
full PDF and figures in a public repository is a separate licensing
question that this AI session cannot decide.**

## Current visibility

- The repository `https://github.com/DrWanSJ/PURE` was pushed by the project
  owner. **Verify the actual visibility (public/private) at
  `Settings → General → Danger Zone`** and record it here. If the repo is
  public, the files above are publicly redistributed right now.

## Human decision required (choose per file; record the decision + date here)

1. **keep** — accept redistribution (requires confirming license/permission,
   e.g. via the publisher or applicable exceptions). Suggested follow-up:
   note the justification here.
2. **remove from future commits** — `git rm --cached <file>` + `.gitignore`
   entry; history still contains the file (see 3). Locally keep the file so
   the digitization remains reproducible; regenerate the page render with
   `pdftoppm -png -r 300 -f 14 -l 14 references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE_normalized.pdf`.
3. **purge history** — `git filter-repo` (or BFG) + force-push; coordinate
   with all clones; **breaks commit hashes**, including the
   `ai-b1-baseline` tag target reference (the tag itself survives but the
   SHA recorded in `docs/audit/audit_status.md` would change). This is the most
   invasive option and needs explicit owner authorization.

## What the hardening pass did / did not do

- Did: register the risk, keep the SHA-256 provenance intact, document the
  reproduction path that requires the source files.
- Did not: delete files, rewrite history, or change repository visibility.
