# Mutation-test protocol (manual, human-executed)

Purpose: demonstrate — by **deliberately breaking** the model — that the
test suite actually detects equation/stoichiometry/bookkeeping errors, i.e.
that the green suite has teeth. This is a guard against a silently useless
test suite.

**Rules**

- A human auditor performs these mutations; an AI session performing them
  must never be reported as "mutation testing completed by human review".
- Do the mutations on a **scratch branch** (e.g.
  `mutation/M1-temp`, branched from `audit/b1-hardening`), **one mutation at
  a time**, and NEVER merge a mutation commit into any main line.
- After each mutation run the full suite:
  `matlab -batch "addpath('scripts'); run_all_tests"`.
  Record which tests failed. Then `git checkout .` / revert and proceed to
  the next mutation. The correct end state for every mutation is:
  **the expected tests fail, no unexpected additional failures, and after
  revert everything passes again.**
- The formal scientific model files (`models/literature_reference/*`,
  `matlab/generated/rhs_pure_literature_reference.m`) must remain untouched
  on the audit branch; mutations live only on the scratch branch.

---

## M1 — lose the 2 NTP factor in the NTP equation (paper Eq. 20)

Mutation: in `matlab/generated/rhs_pure_literature_reference.m`, change

```matlab
dydt(1) = (-V_TX - 2*V_TL - V_RS + V_EN)/n_NTP;   % Eq. (20)
```
to
```matlab
dydt(1) = (-V_TX - V_TL - V_RS + V_EN)/n_NTP;
```

Expected failures (minimum set):

| test | why |
| --- | --- |
| `test_codegen_and_provenance/test_generator_output_in_sync` | hand edit no longer matches the canonical definition |
| `test_codegen_and_provenance/test_stoichiometry_matches_code` | state expression contradicts `S(NTP, V_TL) = -2` |
| `test_codegen_and_provenance/test_generated_matches_baseline_snapshot` | mutated RHS ≠ frozen baseline |
| `test_pure_literature_reference/test_rate_law_spot_values` | independently recomputed `dydt(1)` mismatch |
| `test_pure_literature_reference/test_balance_derivative_identities_random_states` | conservation B1 no longer cancels |
| `test_pure_literature_reference/test_short_run_mass_balance_and_nonnegativity` | B_NTP (Eq. 15) drifts |
| benchmark run | `qc.json` → `mass_balance_pass = false`, `scientific_status = failed_qc` |

## M2 — wrong tRNA multiplicity: `n_T = 46 → 45` (parameters.json)

Mutation: in `models/literature_reference/parameters.json`, set
`multiplicity.n_T = 45`.

Expected failures (minimum set):

| test | why |
| --- | --- |
| `test_pure_literature_reference/test_parameter_lock_tables_1_and_2` | double-entry lock: n_T must be 46 |
| `test_pure_literature_reference/test_rate_law_spot_values` | fTA = 45/20 changes V_RS/V_TL and all state expressions |

**Documented non-failures (important):** the conservation-derivative
identities and the short-run mass balance remain green — they are
structurally self-consistent for ANY multiplicity value. Multiplicity
*values* are guarded by the parameter double-entry lock, not by
conservation checks. (The K_TL_RNA derived test still passes: 226/714 does
not involve n_T.)

## M3 — wrong observable mapping: `protein = a/L → a/(3L)`

Mutation: in `matlab/simulate/simulate_pure_literature_reference.m`, change
`out.protein = zz(:,7)/p.L;` to `out.protein = zz(:,7)/(3*p.L);`

Expected failures (minimum set):

| test | why |
| --- | --- |
| `test_pure_literature_reference/test_observable_mapping` | mapping must be `a/L` exactly |

**Documented non-failures:** all conservation/RHS tests stay green (the
states themselves are untouched — only the observable is wrong). This is
why the blind human Fig. 4 audit (`docs/manual_fig4_audit_protocol.md`)
exists: it reads [a] from the figure and would expose a 3× protein offset
that no internal-conservation test can see.

## M4 — energy-regeneration sign reversal: `d[CP]/dt = -V_EN → +V_EN` (Eq. 26)

Mutation: in `matlab/generated/rhs_pure_literature_reference.m`, change
`dydt(8) = -V_EN;` to `dydt(8) = V_EN;`

Expected failures (minimum set):

| test | why |
| --- | --- |
| `test_codegen_and_provenance/test_generator_output_in_sync` | hand edit vs canonical definition |
| `test_codegen_and_provenance/test_stoichiometry_matches_code` | `S(CP, V_EN) = -1` contradicted |
| `test_codegen_and_provenance/test_generated_matches_baseline_snapshot` | mutated ≠ frozen baseline |
| `test_pure_literature_reference/test_rate_law_spot_values` | independently recomputed `dydt(8)` mismatch |
| `test_pure_literature_reference/test_balance_derivative_identities_random_states` | B4 (Eq. 18) no longer cancels |
| `test_pure_literature_reference/test_short_run_mass_balance_and_nonnegativity` | B_CP (Eq. 18) drifts; CP grows beyond CP0 |

## M5 — remove the nt-degradation sink from the conservation ledger (Eq. 15)

Mutation: in `matlab/simulate/simulate_pure_literature_reference.m`
(`local_qc`), compute `B1` **without** the `+ z(:,11)` term
(i.e. drop `D_nt` from the ledger).

Expected failures (minimum set):

| test | why |
| --- | --- |
| `test_pure_literature_reference/test_short_run_mass_balance_and_nonnegativity` | B_NTP residual grows by the accumulated decay flux D_nt; `mass_balance_pass` false |
| benchmark run | `qc.json` → `mass_balance_pass = false` |

**Documented non-failures:** RHS-level conservation-derivative identity
tests stay green (they check Eqs. (20)–(27), not the QC ledger); this
mutation emulates an accounting bug, which is exactly what the ledger test
exists to catch.

---

## Recording results

Append a table to this file (or a linked report) per executed mutation:
mutation id, branch, commit, date, tests failed (observed), tests failed
(expected), verdict (detected / NOT detected), auditor. If any mutation is
NOT detected by the expected tests, treat it as a hardening defect: fix the
test suite before any further scientific work.
