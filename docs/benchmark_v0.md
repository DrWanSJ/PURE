# benchmark_v0.md — B1 `PURE_literature_reference` execution and QC report

Date: 2026-09-18. Environment: MATLAB R2025b Update 5 (25.2.0.3177638), Windows 10 x64
(see `environment_lock.md`). All internal times in **seconds**, all concentrations in **µM**;
figures display hours.

## How to reproduce

```bash
# from the project root C:\Users\sean\Desktop\SynCell
matlab -batch "r = runtests('matlab/tests/test_pure_literature_reference.m'); assert(all([r.Passed]))"
matlab -batch "addpath('matlab/simulate','matlab/generated'); run_fig4_benchmark"
# optional (requires data/raw/mavelli2015_fig4_page14_300dpi.png; regenerate with
#   pdftoppm -png -r 300 -f 14 -l 14 A_Simple_Protein_Synthesis_Model_PURE_normalized.pdf <outdir>/fig4hi):
matlab -batch "addpath('matlab/simulate'); digitize_fig4"
```

Outputs: `results/literature_reference/DNA_{0p34,1p7,6p8}nM/{trajectory.csv,rates.csv,qc.json}`,
`results/literature_reference/fig4_reproduction.png`, `observables_mRNA_protein.png`,
`benchmark_summary.json`.

## Answers to the eleven benchmark questions

### 1. Were Eqs. (5), (6), (8), (10), (12), (14), (20)–(27) implemented equation-by-equation?

**Yes.** Each rate law and each ODE line in `matlab/generated/rhs_pure_literature_reference.m`
carries the paper equation number in a comment and is a literal transcription:

- `V_TX` Eq. (5); `V_nt_deg` Eq. (6); `V_RS` Eq. (8) with the multiplicity factor
  `2.3[T] = (n_T/n_A)[T]`; `V_TL` Eq. (10) with `2.3[AT]` and a **single** rectangular-hyperbolic
  NTP factor (the 2 NTP/event cost enters only the stoichiometry of Eqs. (20)–(21), exactly as
  the paper states in Sect. 2.3); `V_TL_deg` Eq. (12); `V_EN` Eq. (14).
- ODEs: `d[NTP]/dt = (−V_TX − 2V_TL − V_RS + V_EN)/n_NTP` (20); `d[NXP]/dt = 2V_TL + V_RS − V_EN` (21);
  `d[nt]/dt = V_TX − V_nt_deg` (22); `d[A]/dt = −V_RS/n_A` (23); `d[T]/dt = (−V_RS+V_TL)/n_T` and
  `d[AT]/dt = (V_RS−V_TL)/n_T` (24); `d[a]/dt = V_TL` (25); `d[CP]/dt = −V_EN`, `d[C]/dt = V_EN` (26);
  `d[TLcat]/dt = −V_TL_deg` (27).

Verification: an independent re-derivation of all 6 rates and all 10 RHS components at a random
state agrees to 1e-15 (test `test_rate_law_spot_values`); the five balance-derivative identities of
Eqs. (15)–(19) hold at 200 random states to < 1e-9 (test `test_balance_derivative_identities_random_states`).

### 2. Are Table 1 / Table 2 complete?

**Yes.** All 9 initial concentrations (Table 1) and all 6 rate constants + 10 independent MM
constants (Table 2) are present in `models/literature_reference/parameters.json` and locked by an
exact-equality double-entry test (`test_parameter_lock_tables_1_and_2`). `K_TL_RNA` (Table 2) is
handled as derived (Q7 of the task; see question 10/L3 in the registry).

### 3. Parameter origins (per Table 2 / Table 1)

| origin | parameters |
| --- | --- |
| fitted (by the paper's authors, vs Stögbauer 2012 curves) | `k_TX`, `k_TL`, `k_nt_deg`, `k_TL_deg`, `K_TX_DNA`, `K_TL_nt`, and `TLcat = 2.2 µM` (Table 1, fitting) |
| literature database (BRENDA) | `k_RS`, `k_EN`, `K_TX_NTP`, `K_RS_A`, `K_RS_T`, `K_RS_NTP`, `K_EN_CP`, `K_EN_NXP` |
| estimated (paper's word) | `K_TL_AT`, `K_TL_NTP` |
| derived (this work, from paper Eq. (29)) | `K_TL_RNA = K_TL_nt/(3L) = 0.31653 µM` — QC only, not used in the RHS |

Nothing was re-fitted or sampled in this benchmark.

### 4. Did all three Fig. 4 DNA conditions run?

**Yes.** 0.34 / 1.7 / 6.8 nM (0.00034 / 0.0017 / 0.0068 µM), same model, same parameters,
only DNA varied; `ode15s`, t ∈ [0, 14400] s, RelTol 1e-9, AbsTol 1e-12. All three
`qc.json`: `execution_status = completed`, `scientific_status = passed_all_qc`.

### 5. Do nt/a trajectories match the paper's calculated curves in magnitude and shape?

**Yes — with the evidence kept in two strictly separate tiers** (audit hardening pass
reclassified the raster-based comparison as non-independent; see below):

**Tier 3a — independent (paper-text anchors):** protein(4h) at 6.8 nM = 0.589 µM vs paper
0.58 µM (**+1.5 %**); energy split Q_TX/Q_TL/Q_RS = 72.0/15.4/12.5 % vs paper 74/15/11
(≤ 2 pp); φ_RS(1 min) = 87.1 % (paper ≈ 85 %); RS-rate minimum ≈ 280 s (paper ≈ 4 min);
φ_TL+φ_RS(32 min) = 35.2 % (paper ≈ 36 %); correct DNA ordering (6.8 > 1.7 > 0.34 nM);
sigmoidal a(t); nt(t) near-linear with mild saturation as TLcat decays.

**Tier 3b — NOT independent (exploratory envelope only):** automated digitization of the
raster Fig. 4 (`matlab/simulate/digitize_fig4.m`) reports [a]-panel deviations ≤ 1.8 % and
[nt]-panel absolute deviations ≤ 13 µM (≈ 1.3 % of full scale) at all 24 sampled points,
endpoints nt(4h) 775.4/345.2/90.5 vs sim 778.8/344.5/86.6 µM and a(4h) 138.0/91.7/34.2 vs
sim 140.1/93.1/34.6 µM. **However**, where the continuous (calculated) and dotted
(experimental) curves separate, the digitizer assigns the "calculated" cluster by
nearest-to-simulation tracking — `validation_status = non_independent_assignment` — so
this comparison is **circular and must not be cited as reproduction acceptance evidence
on its own**. Raw clusters are preserved (`fig4_digitized_all_clusters.csv`) for
independent re-assignment; the blind human protocol
(`docs/manual_fig4_audit_protocol.md`) is the sanctioned independent check and is
**`pending_human_audit`**.

### 6. Is the observable mapping correct?

**Yes.** `mRNA = nt/(3L) = nt/714`, `protein = a/L = a/238`, L = 238 (GFP). Verified by exact
identity on simulation output (`test_observable_mapping`); the benchmark figure plots **[nt] and
[a]** first (the actual Fig. 4 y-axis quantities) and provides
`observables_mRNA_protein.png` for the molecule concentrations. nt is never labeled as mRNA
molecule concentration, a never as protein molecule concentration.

### 7. Maximum errors of the five conservation relations (Eqs. (15)–(19))

Scaled residual = max_t |B_k(t) − B_k(0)| / B_k(0). Values (max over the three conditions):

| relation | max abs residual (µM) | scaled residual |
| --- | --- | --- |
| B_NTP: n_NTP·[NTP] + [nt] + [NXP] + D_nt | 7.3e-12 | 1.2e-15 |
| B_AA: n_A·[A] + [a] + n_T·[AT] | 2.4e-11 | 3.9e-15 |
| B_tRNA: n_T·[T] + n_T·[AT] | 1.0e-13 | 1.1e-15 |
| B_CP: [CP] + [C] | 4.4e-11 | 2.2e-15 |
| B_TLcat: [TLcat] + D_TLcat | 4.4e-15 | 2.0e-15 |

Machine precision. D_nt/D_TLcat are pure integrators of the Eqs. (6)/(12) fluxes (no feedback);
they agree with independent trapz integration to 8e-8 / 3e-7 relative.

### 8. How much do trajectories change when tolerances are tightened?

RelTol 1e-9→1e-11, AbsTol 1e-12→1e-14: max scaled trajectory difference over all 10 states
(scale s_i = max(|y0_i|, max_t|y_i|)) = **3.8e-9** (0.34 nM), 3.8e-9 (1.7 nM), 3.7e-9 (6.8 nM).
Pass threshold 1e-6 → **solver_convergence_pass = true** for all conditions.

### 9. Did any negative concentration appear?

**No.** Minimum state value across all runs = 0 (NXP at t = 0). No NaN/Inf. No clipping,
no `max(y,0)`, no events — positivity is structural (checked analytically in the model README
and numerically in every run).

### 10. Unresolved ambiguities?

Seven items registered in `docs/benchmark_registry.md` (L1–L7); **none blocks reproduction**:
L1 ~~raster not viewable~~ **RESOLVED** (decrypted normalized PDF provided; pages 5–14 audited;
Fig. 4 digitized); L2 Eq. (17) LHS superscript-0 conversion artifact (**confirmed correct by
the PDF**: `n_T C_T^0`); L3 K_TL_RNA 0.31653 vs 0.32 ± 0.02 (consistent; derived per Eq. (29));
L4 TLcat uncertainty not propagated (central value); L5 zeros for newly-created species
(implied); L6 "k_TXz" OCR artifact (resolved as k_TX, confirmed by PDF); L7 Fig. 4 x-limit is
≈ 4.18 h at the box edge (handled by tick-mark calibration).

### 11. Benchmark status

```yaml
bibliography_verified: true
equations_verified: true   # incl. page-by-page audit vs decrypted normalized PDF (2026-09-18)
reproduced: true
```

`reproduced = true` is justified **per evidence level** (see `docs/evidence_levels.json`):
code actually executed in the locked environment (MATLAB R2025b, `ode15s`); 9/9 baseline
tests + hardening tests pass (AI-written tests, not human review); per-condition QC
`passed_all_qc` (nonnegativity, mass balance ≈ 4e-15 scaled, repeatability exact,
tolerance convergence ≤ 3.8e-9); independent paper-text anchors reproduced (+1.5 % protein
yield at 6.8 nM; energy split within 2 pp; φ milestones within 2 %). The Fig. 4 raster
digitization match is recorded separately as **`non_independent_assignment`** and is not
part of the acceptance evidence; `fig4_independent_human_audit = pending_human_audit`;
`experimental_data_validation = false`.

## Test suite result (final code state)

```
正在运行 test_pure_literature_reference
.........
已完成 test_pure_literature_reference
TOTAL: 9 passed, 0 failed
```

Tests: parameter lock (Tables 1–2), rate-law spot values, initial-rate sanity (task Sect. 9 E),
balance-derivative identities at 200 random states (task 9 B), finite-difference short-step
check (task 9 A; err 6.5e-10 → 1.7e-10 when h halves), observable mapping (task 9 C),
derived K_TL_RNA (task 9 D), 1 h run mass balance + nonnegativity, determinism of repeated runs.

## Explicit non-claims

- The Fig. 4 digitization approximates a raster figure at ~1–2 % of full-scale precision;
  deviations are reported at that precision and are conditional on the documented
  cluster-assignment flags (merged/nearest-to-simulation points). The digitized values are
  the paper's CALCULATED curves, NOT experimental data, and NOT a substitute for the
  original Stögbauer 2012 data.
- No claim that the paper's MM rate laws are validated stochastic propensities.
- No experimental curve overlay (Stögbauer 2012 machine-readable data remain absent).
- No parameter refitting anywhere; any mismatch would have been treated as a transcription
  bug (and the bugs found during development were indeed code bugs, not parameter tweaks).
