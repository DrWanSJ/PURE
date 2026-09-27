# Aminoacylation selective-QSSA reduction — formal validation certificate v1

Certificate class: VERSIONED FORMAL VALIDATION CERTIFICATE (supersedes no
prior file; the v0 certificate remains in place).

**Final scoped status: `FAILED_VALIDATION_ON_REFERENCE_DOMAIN`.**
The failure is classified as an **implementation / initialization defect**
of the reduced consistent-start construction (substrate-moiety duplication),
not as a failure of the registered QSSA partition hypothesis. All 13
registered formal runs, the full comparison, and the failure analysis are
preserved as repository evidence.

---

## 1. Source branch / SHA

- Branch `research/pnas2017-full-network-reduction`
- HEAD at the start of this formal cycle:
  `8710b85cac27dbe7a1a2805a8e7f79d87e3d51e6`
- Active registration: `docs/audit/pnas2017_aminoacylation_reduction_v1/
  preregistration_revision_v1r1.json` (IMPLEMENTATION / COORDINATE
  REALIZATION REVISION, v1r1 — not a new scientific preregistration).

## 2. Source-model SHA

- Canonical SBML `models/pnas2017_full_reference/original/fMGG_synthesis.xml`
  = `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`
  (matches `data/provenance.csv`; unchanged through the cycle — validator R1).
- Author model / parameter / initial-value CSVs unchanged
  (`5357b163…`, `cfb24e2c…`, `a1b6f832…`).

## 3. Historical v0 outcome

v0 (see `aminoacylation_reduction_certificate_v0.md`): A1 pair-merge
`EXACT_REWRITE_VALIDATED`; A2/A3 not accepted (state elimination not
certified); no reduced core built. The v1 cycle replaced v0's null
approximate-tier thresholds with the registered engineering conventions and
pre-registered the A3a candidate before any formal comparison.

## 4. DAE realization failure

The singular-mass DAE harness (`MassSingular,yes`) is numerically
unattainable at RelTol 1e-10 / AbsTol 1e-14 in MATLAB R2025b: the ode15s
corrector reaches a step-size-independent error-test plateau of 1.67·RelTol
on algebraic rows with small Jacobian diagonals (author RHS sums up to
~3e6 uM/s ⇒ ~1e-9 uM/s cancellation noise per eliminated row). Full
evidence: `dae_singular_mass_failure_v1.md`. Classification:
NUMERICAL_IMPLEMENTATION_LIMITATION, not a QSSA failure.

## 5. Implementation revision (v1, then v1r1)

- v1: retired the DAE in favour of the algebraically eliminated ODE
  (G(s,q)=0, q=h(s), ds/dt=F(s,h(s))); recorded in
  `implementation_revision_v1.json`.
- v1r1 (this cycle): free MetRS/GlyRS no longer integrated; reconstructed
  exactly from the conserved enzyme moiety (220 → 218 dynamic states),
  resolving the frozen `candidate_partition.json` line-74 contradiction BY
  VERSIONING: the historical partition and preregistration remain
  byte-for-byte on disk (validator R16), and
  `candidate_partition_v1r1.json` + `preregistration_revision_v1r1.json`
  record the active realization (validator R17/R18).
- Runner statistics instrumentation (Newton per-call counts, line-search
  rejections, Jacobian refreshes, plateau accepts, locale-independent
  solver-stats parse) — decision path byte-identical; identity proven by
  exact reproduction of every recorded pre-instrumentation smoke statistic
  (`results/pnas2017_reference/2026-09-26_aa_v1r1_smoke/`).

## 6. Active candidate partition v1r1

`candidate_partition_v1r1.json`, parent
`521559bb4e703449135518ddc7b1aa772dd89de4180b379cc70ce10b20447b2f`,
active SHA bound in the revision record. `scientific_partition_changed =
false`; only the state-coordinate realization changed.

## 7. The 21 eliminated complex states

12 MetRS (`MetRS_AMP`, `MetRS_AMP_MettRNAfMetCAU`, `MetRS_ATP`,
`MetRS_ATP_tRNAfMetCAU`, `MetRS_Met`, `MetRS_MetAMP_PPi`,
`MetRS_MetAMP_PPi_tRNAfMetCAU`, `MetRS_MetAMP_tRNAfMetCAU`,
`MetRS_Met_ATP`, `MetRS_Met_ATP_tRNAfMetCAU`, `MetRS_Met_tRNAfMetCAU`,
`MetRS_tRNAfMetCAU`) + 9 GlyRS (`GlyRS_AMP_GlytRNAGlyGCC`, `GlyRS_ATP`,
`GlyRS_ATP_tRNAGlyGCC`, `GlyRS_Gly`, `GlyRS_GlyAMP_PPi`, `GlyRS_Gly_ATP`,
`GlyRS_Gly_ATP_tRNAGlyGCC`, `GlyRS_Gly_tRNAGlyGCC`, `GlyRS_tRNAGlyGCC`) —
identical to the registered parent partition (validator R17).

## 8. Exact free-enzyme moiety reconstruction

`free = ePool − Σ(kept complexes) − Σ(eliminated complexes)` with ePool from
the (per-stress scaled) author initial values, enforced at every RHS
evaluation and output time. Measured: MetRS/GlyRS family totals agree with
FULL to ≤ 4.4e-16 at t0 and ≤ 2.9e-12 relative over the whole window in
every condition (T_G met exactly for the enzyme moieties; the 220-state
formulation's 0.99 pool leak is gone).

## 9. 218 dynamic states

241 species − 21 eliminated − 2 reconstructed = 218 integrated dynamic
species (+12 cumulative-extent states = 230 total integrated; reference
mode integrates 253). Validator R17 enforces the count.

## 10. Algebraic closure method

Registered damped projected Newton per enzyme pool on the author-RHS rows
0 = dC_i/dt, warm-started from a fixed seed, cached FD Jacobian with
refresh-on-slow-progress, feasibility line search (no clipping), Newton
target 1e-12 of the block production scale, run-refusing acceptance at the
registered scaled 1e-10, multi-start consistent initialization with
registered start-agreement discipline. Formal observed: max scaled |G| ≤
1.0e-12 in every RED run; 0 root failures, 0 line-search rejections,
0 plateau accepts; consistent-start residuals ≤ 4.9e-13 scaled.

## 11. Reference-domain results (S0) — FAILED

13/13 registered runs executed once, in registry order (manifests record
config SHA, runner binding, MATLAB R2025b Update 5, ode15s, RelTol 1e-10,
AbsTol 1e-14, grid logspace(−4, 3, 200), wall time, step/failed-step/RHS
counts, initial-layer adjustment, algebraic statistics). FULL-S0 reproduced
the registered reference-mode trajectory byte-for-byte
(`7af23625…`, identical to the REFCHECK artifact).

Under the frozen acceptance criteria, S0 FAILED:

- T_C states: FAIL (worst full-window E_inf 1.03 at t=1e-4 — initial-layer
  window; worst post-layer E_inf 0.336 at t=2.7 s);
- T_D fluxes: FAIL (worst 0.98 at t=1e-4, inside the layer window);
- T_E cumulative extents: FAIL (worst 1.67e-2 vs 1e-2, at t=7.75 s);
- T_G conservation: enzyme moieties PASS exactly; tRNAfMetCAU family FAIL
  (6.6e-2), tRNAGlyGCC family FAIL (9.2e-2), phosphate ledger FAIL
  (2.9e-5); adenine ledger NUMERICALLY_UNRESOLVED (the FULL reference
  itself does not resolve it to 1e-8 at the registered tolerances; the
  source model's adenosine invariant is exact at the rate-law level —
  scope-file evidence).

## 12. Stress-domain results (S1-S5) — FAILED, same signature

Every stress condition fails the same categories with the same mechanism
(worst post-layer state error: S1 0.652, S2 0.222, S3 0.792, S4 0.082,
S5 0.336; worst extent error: S3 5.03e-2; S4 extents PASS at 3.4e-3).
No condition passes. Failure categories per condition are recorded in
`formal_comparison_summary.json` (`pairs.*.verdicts`, `conservation`).

## 13. State errors

Per-observable max absolute error, scaled E_inf, threshold, worst-error
time and floor-materiality flags: `metrics-S0..S5.json`
(`detail_max_abs_error`). Full-window worst errors are dominated by the
declared initial-layer window (t ≤ 0.049 s); post-layer errors up to 0.79
(S3) are trajectory errors caused by the initialization defect (§20), not
closure errors.

## 14. Flux errors

12 registered gross process fluxes per condition (activation, charging,
AMP release, PPi release, decharging, delivery, peptide-bond formation),
normalized by the declared production scale. Worst errors fall inside the
initial-layer window; the resource-level consequences are visible in the
cumulative extents (§15).

## 15. Cumulative-resource errors

The 12 registered cumulative extents, compared as complete curves from the
physical initial condition (never reset after the layer). Permanent
phantom-charging signature: xi_Gly_release +1.29e-2, xi_Gly_AMP_release
+1.29e-2, xi_aa_ATP_consumption_total +1.67e-2 (S0); up to 5.03e-2 (S3).

## 16. Conservation results

Token-derived ledgers verified on the tight reference at scope-build time
(enzyme moieties 2.2e-10/2.5e-10; tRNA families 2.3e-10/1.5e-10; guanine
2.0e-10; phosphate 1.1e-10; adenine 3.1e-6 transient → classified
NUMERICALLY_UNRESOLVED per the frozen numeric_uncertainty_budget rule,
with rate-law-level proof that the source invariants are exact). In the
formal runs: enzyme moieties exact in every RED run; tRNA families and the
phosphate ledger FAIL by the initialization defect; guanine PASS.

## 17. Initial-layer behavior

Recorded per run (never suppressed): largest consistent-start adjustment
MetRS 0.44 → 0.00354689 (S0; 4.36 in S3 enzyme_high, 0.0436 in S4
enzyme_low), layer window [1e-4, 1e-4 + 5·0.009825 s]. Enzyme pool
inventories at t0 agree with FULL to ≤ 4.4e-16. T_C is reported over the
complete window AND the post-layer window (post-layer columns in
metrics-*.json). Cumulative extents start from the physical initial
condition and are never reset. The layer treatment itself is NOT the
failure cause — see §20.

## 18. Numerical convergence evidence

- Tolerance-convergence study (registered): worst RelTol 1e-8 vs 1e-10
  deviation 1.496205e-7 over the 43 aminoacylation quantities — below 10%
  of every tier budget ⇒ all comparisons decidable (no
  NUMERICALLY_UNRESOLVED on budget grounds except the adenine ledger, whose
  FULL-reference residual itself exceeds T_G).
- Runner reference-mode reproduction of the tight reference: 4.975e-10
  trajectory-scaled (REFCHECK, re-verified R4/R6).
- Determinism: FULL-S0 = registered reference trajectory byte-for-byte.
- RED runs: ode15s 200-point registered grid, no failed closure solves.

## 19. Unrecoverable / approximately reconstructable observables

The 21 eliminated complex occupancies are algebraically reconstructable on
the reduced model (closure solved everywhere) and the post-layer
branch-vs-reference occupancy evidence (≤ 1.12e-3, pre-formal partition
verification) remains valid. However, under the v1r1 initialization the
reduced TRAJECTORY of the eliminated and kept complexes deviates from FULL
during t ≈ 0.05-20 s (up to 0.79 of scale in S3) because the reduced model
runs on an inflated substrate inventory; no observable class is
"unrecoverable in principle" — the deviation is initialization-driven.

## 20. Failure domain (precisely scoped)

Root cause (quantified in `formal_failure_classification_v1r1.md`):
`consistentStart` solves the closure at t0 with all non-eliminated states
frozen at author values. The free enzyme is correctly debited (moiety
reconstruction), but the free SUBSTRATE pools are not debited for the
substrate content sequestered into the eliminated complexes. The reduced
model therefore starts from the author inventory PLUS the complexes'
contents: tRNAfMetCAU tokens +0.23485 uM (+6.62%), tRNAGlyGCC tokens
+0.32496 uM (+9.16%), weighted phosphate +1.99017 uM, adenine +0.73085 uM.
The phantom inventory washes out through degradation sinks over t ≈ 1-20 s,
inflating charging fluxes and GlyRS-family occupancies in that era and
permanently elevating the cumulative extents.

This violates the frozen `initial_conditions_rule` ("identical physical
inventories") and frozen tier T_G for the substrate ledgers. Per the
execution instruction (Phase 4) the cycle was STOPPED and classified — no
repair, no re-run, no threshold change, no initialization re-fit after
results were seen. A repair (moiety-consistent initialization fixing ALL
conserved ledgers, not only the enzyme moiety) would be a new
implementation revision (v1r2) requiring a new revision record, re-freeze,
pre-formal gate, fresh smoke, and a fully fresh set of 13 formal runs.

## 21. External / experimental validation status

NONE. This certificate rests entirely on internal consistency evidence
against the author PNAS 2017 model. No laboratory or literature-external
quantity was compared.

## 22. Final scoped status

**`FAILED_VALIDATION_ON_REFERENCE_DOMAIN`** — scoped to the v1r1
realization (218-state eliminated-ODE with the implemented consistent
start). NOT `VALIDATED` in any unqualified sense. The negative software
control RED-NEG1 was rejected as registered (criterion PASS), and the
independent validator reports 24 PASS / 0 FAIL / 0 SKIP — the evidence
pipeline is intact; the scientific acceptance outcome is the recorded
failure. The registered QSSA partition hypothesis itself is neither
certified nor refuted by this cycle: its pre-formal verification evidence
stands, and the formal comparison could not test it fairly because the
reduced initial state did not reproduce the author's physical inventory.

This certificate does NOT claim the full PURE reduced model is complete;
it covers only the aminoacylation selective-QSSA candidate.
