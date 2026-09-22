# Manual Fig. 4 blind-audit protocol (independent human validation)

Purpose: replace the simulation-assisted digitization match
(`validation_status = non_independent_assignment`, see
`data/processed/literature/R01/fig4/fig4_digitized_validation_status.json`) with a **human,
simulation-blind** reading of the paper's Fig. 4 calculated curves, so that
`fig4_independent_human_audit` can eventually be set to a passed value by a
human — not by the AI session that produced the model and the simulation.

Project scope decision (2026-09-22): **this strict blind audit is not required for B1 literature reproduction**. The protocol is retained for any future claim of independent Fig. 4 raster validation. If that stronger evidence stream is pursued, its status remains `pending_human_audit` until the protocol is completed.

## Why this is needed

The automated digitizer (`matlab/tools/digitization/digitize_fig4.m`) must decide, at
times where the calculated (continuous) and experimental (dotted) curves of
the same color are separated, which pixel cluster belongs to the calculated
curve. Its current rule picks the cluster nearest to the `new_simulation`
trajectory. Comparing those assigned clusters against the same simulation is
**circular**: the assignment itself is informed by the quantity being
validated. It remains useful as an exploratory/envelope tool, but it is not
independent evidence.

## Protocol (follow in order; do not skip steps)

1. **Hide the simulation.** Close all files under `results/` (both legacy
   `results/baselines/b1_mavelli2015/` and any `results/runs/<run_id>/`), do not read
   `fig4_digitized_comparison.csv`, do not read the digitized CSVs under
   `data/processed/`, and do not read the numbers quoted in
   `docs/validation/benchmark_v0.md` Section 5 before the reading is complete.
   The auditor must fill `simulation_hidden_during_reading = true` honestly.
2. **Print or open the source raster** at high zoom:
   `data/raw/literature/R01/mavelli2015_fig4_page14_300dpi.png` (300 dpi render of page 14
   of `references/R01_Mavelli2015/A_Simple_Protein_Synthesis_Model_PURE_normalized.pdf`, sha256-locked
   in `environment_lock.md`), or the paper page itself.
3. **Identify the CALCULATED (continuous) curves** visually (caption:
   experimental = dotted, calculated = continuous; colors: 0.34 nM blue,
   1.7 nM green, 6.8 nM red). Where dotted and continuous are
   indistinguishable, say so in `notes` and read the common value.
4. **Read the calculated curve values** at the pre-filled sample times
   (0.5 : 0.5 : 4 h) for both panels ([nt] top, axis 0–1000 µM; [a] bottom,
   axis 0–160 µM), using the printed gridlines for calibration. Record:
   - `value_uM` — the reading;
   - `estimated_reading_error_uM` — the auditor's own honest uncertainty
     (typically ±1–2 % of the panel full scale, i.e. ±10–20 µM for [nt] and
     ±2–3 µM for [a]);
   - `auditor` — your name/initials;
   - `notes` — anything relevant (overlap with dotted curve, readability).
5. **Save as** `data/manual_audit/fig4_human_digitization_<auditor>.csv`
   (same columns; keep the template untouched as the blank master).
6. **Only now** un-hide the simulation and compare — the comparison script
   must be run by (or with) the auditor and its output stored under
   `results/` with a run manifest. Report per curve: max |value − simulation|
   and whether it falls within the declared reading error.
7. **Record the outcome** in `docs/audit/audit_status.md` and
   `docs/project/evidence_levels.json`
   (`fig4_independent_human_audit`: `passed_by_<auditor>` /
   `failed_at_<point>`), including the comparison CSV path. Only a human may
   set these values; an AI session must not fill the template or flip the
   flag.

## Acceptance interpretation

- Agreement within the declared reading errors on both panels supports the
  statement "the new_simulation matches the paper's calculated Fig. 4 curves
  within human reading precision", as **independent** evidence.
- Disagreement beyond reading error at any point is a finding: it must be
  investigated as a possible transcription/implementation issue (or a
  mis-assigned cluster) — NOT absorbed by refitting parameters (no refitting
  is allowed in B1).
- This protocol validates only the CALCULATED curves of Fig. 4. It does not
  provide `experimental_data_validation` (the Stögbauer 2012 experimental
  data remain unavailable in machine-readable form).
