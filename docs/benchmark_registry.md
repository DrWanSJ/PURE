# Benchmark registry — B1: `PURE_literature_reference`

Registered: 2026-09-18. Benchmark task: literal reproduction of the
deterministic coarse-grained PURE model of

> Mavelli, F., Marangoni, R., Stano, P. (2015).
> *A Simple Protein Synthesis Model for the PURE System Operation.*
> Bulletin of Mathematical Biology **77**, 1185–1212. DOI: [10.1007/s11538-015-0082-8](https://doi.org/10.1007/s11538-015-0082-8)

## Status (per tasklist Sect. 3.2)

| flag | value | evidence |
| --- | --- | --- |
| `bibliography_verified` | **true** | Title, authors, journal, volume/pages, year, DOI read from the source document itself; hashes locked in `environment_lock.md` and `data/provenance.csv` |
| `equations_verified` | **true** | Sect. 2 transcribed literally (first pass from the text conversion), then **audited page-by-page (pages 5–14) against the decrypted normalized PDF (2026-09-18): Eqs. (1)–(29), Table 1 and Table 2 confirmed identical — no discrepancies**; double-entry parameter lock in the test suite; balance-derivative identities and finite-difference check pass (see `docs/benchmark_v0.md`) |
| `reproduced` | **true (with the evidence-level split below)** | All three Fig. 4 DNA conditions actually executed with MATLAB R2025b `ode15s`; 9/9 baseline tests + hardening tests pass; QC per condition `passed_all_qc`; paper-text anchors matched (independent); Fig. 4 raster digitization match is **non-independent** (simulation-assisted assignment) and counts only as an envelope check — see verification layering |

## Source-input completeness (tasklist D1 checklist)

| item | state |
| --- | --- |
| Full paper text | available (markdown conversion + **decrypted normalized PDF**, audited page-by-page 2026-09-18) |
| Supplementary materials | none referenced by the paper |
| Machine-readable experimental data | **absent** from the repo (Stögbauer et al. 2012 curves exist only as the dotted raster lines inside Fig. 4; they were **not** digitized) |
| Model equations | complete: Eqs. (1)–(29), Sect. 2 — confirmed against the normalized PDF |
| Initial conditions | complete: Table 1 (DNA 0.34–6.8 nM; TXcat 0.1; TLcat 2.2±0.3; RScat 0.16; ENcat 0.08; A 300; T 1.9; NTP 1500; CP 20000 µM) — confirmed |
| Kinetic parameters | complete: Table 2 (6 rate constants, 10 independent MM constants; `K_TL_RNA` derived per Eq. (29)) — confirmed |
| Units | complete: time implicit s (rate constants s⁻¹), concentrations µM throughout |
| Temperature / pH / Mg²⁺ | not specified in the paper; not needed by this model (no ion- or temperature-dependent term exists in Eqs. (5)–(14)) |
| Volume | fixed, implicit (concentration formulation; batch, well-mixed) |
| Observation window | 0–4 h (paper Figs. 4, 5, 8, 9 and text: "protein produced after 4 h") |
| Reported protein / template | GFP, L = 238 aa; three DNA template concentrations 0.34 / 1.7 / 6.8 nM |

## Quantitative anchors available from the paper TEXT (used because the raster figure is not machine-readable)

1. **Protein yield at 4 h, standard composition, [DNA] = 6.8 nM = 0.58 µM** (Sect. 4.1, Fig. 5 text; same condition as the red curve of Fig. 4) → `[a](4h) ≈ 0.58 × 238 = 138.0 µM`.
2. **Energy split** over 0–4 h at 6.8 nM: `Q_TX : Q_TL : Q_RS = 74 : 15 : 11 %` (Sect. 5, Table 4 entry 1; Q's are ∫V_TX, ∫2V_TL, ∫V_RS of chemical energy χ_ε).
3. **φ dynamics** (Fig. 8 narrative): φ_RS ≈ 85 % at t ≈ 1 min; RS-rate minimum at ≈ 4 min; φ_TL + φ_RS ≈ 36 % (24 % + 12 %) at ≈ 30 min.
4. Qualitative: mRNA curves reproduced "quite well", protein curves sigmoidal with the model "not completely satisfactory" vs experiment (Sect. 3) — this refers to the *experimental* fit; the *calculated* curves are the reproduction target here.

## Verification layering (acceptance criteria Sect. 14)

No original-author numerical trajectory exists (only the raster Fig. 4). Therefore **no
"1e-5 against the paper figure" claim is made**, and validation is split as:

1. **Equation-level verification** — `matlab/tests/test_pure_literature_reference.m`, 9/9 pass:
   parameter double-entry lock (Tables 1–2, exact equality); independent rate-law
   re-derivation at a random state (agreement 1e-15); balance-derivative identities of
   Eqs. (15)–(19) at 200 random states (max violation < 1e-9); central finite-difference
   vs analytic RHS (error 6.5e-10 at h = 0.5 s, dropping 4× at h/2 — O(h²) truncation
   regime); observable mapping `nt/(3L)`, `a/L`; derived `K_TL_RNA = 226/714 = 0.31653`
   consistent with the reported 0.32 ± 0.02 µM; initial-rate sanity (V_TL(0) = 0,
   V_EN(0) = 0, V_TX(0) > 0, V_RS(0) > 0).
2. **Internal numerical / QC verification** — per run: five conservation relations
   (Eqs. (15)–(19)) hold to scaled residuals ≈ 4–6e-15; all states nonnegative with no
   clipping; no NaN/Inf; three repeat runs bitwise identical; tolerance study
   (RelTol 1e-9→1e-11, AbsTol 1e-12→1e-14) changes trajectories by ≤ 3.8e-9 (scaled).
3. **Fig. 4 comparison — TWO tiers, kept strictly separate (audit hardening):**
   - **Tier 3a (independent, text anchors):** protein(4h) at 6.8 nM = 0.589 µM vs paper
     0.58 µM (+1.5 %); energy split 72.0/15.4/12.5 % vs 74/15/11 (≤ 2 pp); φ_RS(1 min)
     87.1 % vs ~85 %; RS minimum ≈ 280 s vs ~4 min; φ_TL+φ_RS(32 min) 35.2 % vs ~36 %;
     correct DNA ordering and sigmoidal a(t). These are usable as reproduction evidence.
   - **Tier 3b (NOT independent, exploratory only):** automated raster digitization of the
     calculated curves (`matlab/simulate/digitize_fig4.m` →
     `data/processed/fig4_digitized.csv`, provenance `digitized_from_Mavelli_2015_Fig4`).
     Where the continuous and dotted curves separate, the "calculated" cluster is chosen
     by **nearest-to-simulation tracking** — `validation_status =
     non_independent_assignment`. The resulting deviations ([a] panel ≤ 1.8 %, [nt] panel
     ≤ 1.3 % of full scale) are an envelope/consistency observation and **must not be
     cited as independent reproduction acceptance evidence**. Raw clusters are preserved
     in `fig4_digitized_all_clusters.csv` for independent re-assignment.
   - Independent validation requires the blind human protocol
     (`docs/manual_fig4_audit_protocol.md`); until then
     `fig4_independent_human_audit = pending_human_audit`.
   - The digitized values are NOT experimental data (Stögbauer 2012 data absent).

## Data handling decisions

- **No experimental overlay.** Stögbauer 2012 machine-readable data are absent from the
  repo; the dotted experimental curves in Fig. 4 were themselves digitized by the paper's
  authors from Stögbauer et al. 2012. The experimental dotted curves were NOT digitized
  here (only the paper's calculated continuous curves, as the reproduction target).
- **Digitization performed (2026-09-18, second pass).** After the decrypted normalized PDF
  became available, the calculated (continuous) curves of Fig. 4 were extracted
  automatically from a 300-dpi page render (`matlab/simulate/digitize_fig4.m`) and saved to
  `data/processed/fig4_digitized.csv` with provenance `digitized_from_Mavelli_2015_Fig4`,
  per-point flags, an audit-trail CSV of all raw pixel clusters
  (`fig4_digitized_all_clusters.csv`), and the comparison table
  (`results/literature_reference/fig4_digitized_comparison.csv`). Reading precision is
  ~1–2 % of each panel's full scale; the digitized values are an approximation of a raster
  figure, not experimental data.
- **No refitting.** Table 2 central values used as-is; TLcat = 2.2 µM (central value of
  2.2 ± 0.3); no Hill coefficient; no ATP/GTP split; no additional states.

## Ambiguity / limitation log

| id | item | severity | blocks reproduction? | disposition |
| --- | --- | --- | --- | --- |
| L1 | ~~Fig. 4/Fig. 3 rasters not inspectable (password-protected PDF)~~ **RESOLVED 2026-09-18**: decrypted normalized PDF provided (`A_Simple_Protein_Synthesis_Model_PURE_normalized.pdf`, sha256 locked); pages 5–14 rendered and audited; Fig. 4 digitized | resolved | no | full equation/table audit passed (no discrepancies); quantitative raster comparison added (verification layer 3) |
| L2 | Paper Eq. (17) LHS superscript 0 lost in the md text conversion | minor | no | **confirmed by the normalized PDF**: it prints `n_T C_T^0`; the inferred reading used in the code was correct |
| L3 | `K_TL_RNA` reported as 0.32 ± 0.02 µM in Table 2, but Eq. (29) gives `K_TL_nt/(3L) = 226/714 = 0.31653 µM` | minor | no | consistent within uncertainty; treated as derived QC quantity, not an independent parameter, not used in the RHS |
| L4 | TLcat = 2.2 ± 0.3 µM is a fitted fictitious species with reported uncertainty | minor | no | central value used; uncertainty not propagated (out of B1 scope) |
| L5 | Initial values of newly-created species (nt, AT, a, NXP, C) not explicitly stated in the paper | minor | no | zeros used; implied by the curves starting at 0 and required by conservation Eqs. (15)–(19) |
| L6 | OCR artifact "k_TXz" in the text conversion of Eq. (5) prose | trivial | no | resolved as `k_TX` from context; confirmed as k_TX by the normalized PDF |
| L7 | Fig. 4 x-axis limit is not exactly 4 h (calibration gives ≈ 4.18–4.19 h at the right box edge); the plotted curves end at t = 4 h | trivial | no | handled by tick-mark calibration in the digitization |
| L8 | Fig. 4 digitization cluster assignment is **simulation-assisted** (`non_independent_assignment`): where continuous/dotted curves separate, the "calculated" cluster is chosen nearest to the new_simulation trajectory, so the digitization-vs-simulation comparison is not an independent check | limitation (validation-status) | no (Tier 3a text anchors remain independent evidence) | status recorded in `data/processed/fig4_digitized_validation_status.json` and `docs/evidence_levels.json`; independent validation = blind human protocol (`docs/manual_fig4_audit_protocol.md`), currently `pending_human_audit` |

No ambiguity blocks the reproduction. Nothing was guessed where the paper gives a value;
no parameter was invented.

## Scope restriction

`PURE_literature_reference` is the B1 benchmark only. Its effective Michaelis–Menten rate
laws must **not** automatically be read as validated stochastic propensity functions; SSA
use requires separate validation (tasklist Sect. 10.2). It is not `PURE_resource_core`;
no equation or parameter may migrate into resource models without re-derivation.
