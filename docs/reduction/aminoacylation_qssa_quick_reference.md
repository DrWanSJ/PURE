# Aminoacylation QSSA quick reference

Evidence sheet for human review; source snapshot: main `678fcb709324142454fd7a80cb6185c64b900510`. Numbers below are extracted from its frozen author/audit CSVs; percentages are arithmetic comparisons, not new acceptance criteria.

## 1. What has already been decided

The [species information contract](species_information_contract_summary.md) is **HUMAN APPROVED**: I=42, II-A=57, II-B=91, III=22, C=29. GlyRS/MetRS activation complexes are II-A: their individual trajectories need not be protected. This information-retention decision **does not validate QSSA**. ATP, AMP, PPi, Gly, Met, GlyRS and MetRS resource information, including enzyme occupancy and bound resources, must remain protected/reconstructable. The [process transformation choice](human_reduction_review.md) remains `HUMAN_REVIEW_REQUIRED`.

## 2. Author reference initial conditions

From the [frozen author initial-value CSV](../../models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv):

| Species | Initial value |
| --- | ---: |
| ATP | 3750 |
| Gly | 300 |
| Met | 300 |
| GlyRS | 0.35 |
| MetRS | 0.44 |
| tRNAGlyGCC | 3.54767184 |
| tRNAfMetCAU | 3.54767184 |

All 28 GlyRS/MetRS complex states, including the 12 activation complexes, start at zero. Values use the repository's **inferred µM concentration interpretation** from paper examples; the CSV omits units and authoritative absolute chemical units remain unresolved ([chemical ledger](../pnas2017/chemical_ledger.md)).

## 3. Mechanistic reminder

**QSSA:** `dz/dt ≈ 0` for proposed eliminated states. **Rapid equilibrium:** forward binding flux ≈ reverse binding flux. A fast mode alone does not select sQSSA, tQSSA, rapid equilibrium or another effective representation; a closure and its validity domain still need evidence.

## 4. Existing time-scale evidence

The historical [time-scale CSV](../../models/pnas2017_full_reference/audit/aminoacylation_timescale.csv) records 30 author-trajectory samples from `1e-4` to `1000` s. In its reported time convention:

- `|lambda_fast| ≈ 5.0e4 s^-1` (range `5.025484e4–5.169963e4`).
- `tau_fast ≈ 1.9e-5 s` (range `1.934250e-5–1.989858e-5`).
- Reported `epsilon_stiff` spans `1.528057e-4` down to `3.169305e-10`.

**THIS IS EVIDENCE OF FAST MODES, NOT A QSSA CERTIFICATION.** Every row records `algebraic_manifold_derived=false`; the [analysis summary](../../models/pnas2017_full_reference/audit/aminoacylation_analysis_summary.json) reports no algebraic QSSA manifold and unresolved structural separation. These historical diagnostics are not a new closure validation.

## 5. Occupancy / sequestration evidence

The [fast-state CSV](../../models/pnas2017_full_reference/audit/aminoacylation_fast_states.csv) and [enzyme-pool conservation CSV](../../models/pnas2017_full_reference/audit/aminoacylation_enzyme_pool_conservation.csv) give:

| Author-reference active enzyme pool | Recorded maximum of one complex | Fraction of pool |
| --- | ---: | ---: |
| GlyRS_total = 0.35 | GlyRS_GlyAMP = 0.3488964 | 99.68% |
| MetRS_total = 0.44 | MetRS_MetAMP = 0.4374142 | 99.41% |

One complex can approach essentially the entire enzyme pool. **Free enzyme cannot automatically be treated as total enzyme.** Here the active pool is free enzyme plus all its complexes, conserved at the author reference where degradation rates are zero; active-plus-degraded family totals are the unconditional conservation candidates.

Simple enzyme-pool size comparisons with initial bulk free substrates are:

| Pool-size bound | Percentage |
| --- | ---: |
| GlyRS_total / Gly0 | 0.117% (≈0.12%) |
| GlyRS_total / ATP0 | 0.00933% (≈0.009%) |
| MetRS_total / Met0 | 0.147% (≈0.15%) |
| MetRS_total / ATP0 | 0.01173% (≈0.012%) |

These are only simple pool-size upper bounds for enzyme-bound sequestration relative to initial substrates, **not full dynamic QSSA criteria**.

Free aminoacyl-adenylates reach `max GlyAMP = 23.7269` (≈23.73; **7.91% of Gly0**) and `max MetAMP = 29.81544` (≈29.82; **9.94% of Met0**). Free AA-AMP accumulation cannot be dismissed merely because enzyme concentration is small.

## 6. Existing reduction evidence

The historical records are already archived on main (archive commit `55b6b63e98e70980d23a4a2093e079d2dfde1096`); no unmerged PR #3/#4 evidence is used here.

- [A3a selective/free-substrate QSSA](aminoacylation_A3a_final_status.md) exposed protected-ledger and sequestration problems: integrated free substrates plus algebraic complexes produced a structural sliding leak. Its recorded status is `FAILED_VALIDATION_ON_REFERENCE_DOMAIN`.
- The [A3b historical matrix](aminoacylation_A3bc_final_decision.md) records that total-coordinate approaches removed that bookkeeping sliding leak. The broad 21-state closure nevertheless lost feasibility during a GlyAMP-associated transient at about **2.498 s**: `FAILED_SMOKE_CLOSURE_FEASIBILITY`.
- The restricted **9-state** A3b-r12 candidate showed substantially better local behavior on `[1e-4, 10] s`; its full window did not complete. Ledger-row scopes cut fast binding equilibria, leaving coordinate/ledger-definition issues and status `BLOCKED_NUMERICAL_COORDINATE_DEFECT`.

The scientific question is therefore **which states can be algebraically eliminated, in which coordinates, over what validity domain?** These records do not approve a kinetic transformation.

## 7. Questions for the human reviewer

1. Which activation/charging intermediates are acceptable to eliminate?
2. For each eliminated state, should the slow coordinates be free-substrate or total/token coordinates?
3. Are free GlyAMP/MetAMP required as explicit dynamic states?
4. Which enzyme occupancies must remain reconstructable?
5. What validity domain must a proposed QSSA satisfy?
6. What full-vs-reduced observables and ledgers will constitute acceptance?

Status: REFERENCE ONLY — NO KINETIC REDUCTION APPROVED.
