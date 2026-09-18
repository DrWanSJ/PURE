# environment_lock.md — B1 benchmark (PURE_literature_reference)

Recorded: 2026-09-18 (local machine of the project workspace `C:\Users\sean\Desktop\SynCell`).

## MATLAB

| item | value |
| --- | --- |
| Executable | `D:\Code\MATLAB\MATLAB2025b\bin\matlab.exe` (on PATH as `matlab`) |
| Version string | `25.2.0.3177638 (R2025b) Update 5` |
| Invocation | `matlab -batch "<command>"` (headless, exit code propagates) |
| Toolboxes required | none beyond base MATLAB (used: `ode15s`, `jsondecode`, `writetable`, `exportgraphics`, `runtests`) |
| Stale-path warning at startup | `警告: 名称不存在或不是目录: D:\BaiduSyncdisk\FACHill\slanCM` — a saved MATLAB search-path entry pointing to a non-existent folder. Harmless for this benchmark; recorded for reproducibility. |

## Platform

| item | value |
| --- | --- |
| OS | Windows 10.0.22631 x64 (win32) |
| Shell | Git Bash |
| Working directory | `C:\Users\sean\Desktop\SynCell` (git repository, branch `main`) |

## Source documents (locked inputs)

Paths updated 2026-09-18 (repository reorganization); file contents and sha256 unchanged.

| file | sha256 |
| --- | --- |
| `references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE.pdf` (original, password-protected; original file name `A Simple Protein Synthesis Model for the PURE System Operation.pdf`) | `7082156ccedda9b9d5e4302b6ec7dd76a8f33cdd8974efa252663639c93238a3` |
| `references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE_normalized.pdf` (Ghostscript-normalized, decrypted; Producer GPL Ghostscript 10.05.1, `Encrypted: no`, 28 pages) | `838d1f5df209ceb9bccdd64b5e5e075cd80e4eb0f982760eecd4cc5a6b4bb7d0` |
| `references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE.md` (text conversion of the same paper; original file name `A Simple Protein Synthesis Model for the PURE System Operation.md`) | `b47bb4e08885f573fabe49068924a0d459d1ff912bc438f4c22b081ffd937af8` |
| `tasklist.md` | `341e7c707bbfec4f7a7b71d62aeec1c3ea9c449928bba0ee7e153e507cc3b125` |

Notes on source access:

- 2026-09-18 (second pass): the decrypted ("normalized") PDF was provided and used for a
  page-by-page audit. Pages 5–14 were rendered to PNG with
  `pdftoppm -png -r 150/300` and inspected: **all equations Eqs. (1)–(29), Table 1 and
  Table 2 were confirmed identical to the transcription used in the code**; Fig. 4 was
  digitized (see `matlab/tools/digitization/digitize_fig4.m`,
  `data/processed/literature/R01/fig4/fig4_digitized.csv`).
  The initial transcription had been made from the markdown conversion; the audit found
  **no discrepancies** (one conversion artifact — the missing superscript 0 in Eq. (17)'s
  LHS — was confirmed as expected: the PDF prints `n_T C_T^0`).
- The PDF page renderer used by the session misdetects both PDF files as
  "password-protected"; rendering via `pdftoppm` (poppler, texlive 2023) works and is the
  reproduction path for the digitization.
- Figure rasters (Fig. 3, Fig. 4) were inspected via the rendered PNGs of the normalized
  PDF. Fig. 4–based validation uses (i) an automated raster digitization of the calculated
  curves and (ii) quantitative anchors stated in the paper text (protein yield 0.58 µM at
  4 h for [DNA] = 6.8 nM, Fig. 5; energy split Q_TX/Q_TL/Q_RS = 74/15/11 %, Sect. 5 /
  Table 4 entry 1). See `docs/project/benchmark_registry.md`.

## Execution status

MATLAB is installed and functional in this environment: the simulations and tests of this
benchmark **were actually executed** (see `results/baselines/b1_mavelli2015/` and the run
log in `docs/validation/benchmark_v0.md`). Nothing in this benchmark is marked
`simulation_not_executed`.

## 2026-09-18 repository reorganization note

The repository layout was reorganized after the B1 freeze (no scientific/numerical
change). Files were moved as documented in the reorganization report; all moved files
kept their content (the source PDFs/MD only got path-safe names, sha256 unchanged).
`results/literature_reference/` is now the frozen baseline at
`results/baselines/b1_mavelli2015/`; new runs write unversioned outputs to
`results/runs/<run_id>/`. `.gitattributes` pins `*.json` to LF so provenance SHA-256
hashes reproduce on fresh checkouts.
