# G1 Pending Human Actions

**Related gate:** G1 — Week 1  
**Status:** tracking list; not all items are G1 blockers  
**Last updated:** 2026-09-23

This file separates work that still requires explicit human judgment from work that is already machine-checked, and separates G1 open evidence from tasks that properly belong to G2 or later.

## A. Completed human decisions (2026-09-22)

- B1 source-to-repository audit completed: H01-H06 = `Y`; final `human_audited = Y` for literature-reproduction scope.
- Both B1 MATLAB test suites passed in the user's local run (`allPassed = 1`).
- H07 decision completed: strict blind Fig. 4 auditing is **not required** for B1 literature reproduction. No independent experimental-validation claim is made.

## B. Remaining human actions carried out of G1

| Priority | Human action | Why human review is needed | Current evidence | Blocks entering G2? |
| --- | --- | --- | --- | :---: |
| High | Review the B1 QC definitions in `benchmark_v0.md` / `qc_v0.json` | The machine results pass, but the user should understand what each metric proves and does not prove | nonnegativity, conservation, repeatability and solver convergence pass | no |
| Medium | Review licensing/distribution decision for tracked publisher PDFs | This is a project/repository governance decision, not a numerical task | `docs/project/licensing_review.md` exists | no |
| Medium | Obtain mentor sign-off on the G1 wording/status | Gate status is a project decision; this report records the current proposed closure | G1 report prepared | no |

### Notes

- Do **not** redo parameter, rate-law, ODE, stoichiometry, observable-mapping, nonnegativity or conservation checks by manual code inspection when the B1 MATLAB test suites pass. The required B1 source audit is now complete.
- Do **not** describe the current Fig. 4 review as independent blind validation. The explicit H07 decision is that such a blind audit is not required for B1 reproduction.
- Do **not** treat absence of machine-readable experimental data as a reason to invalidate the B1 literature reproduction; it limits the experimental/B2 claim.

## C. G2 / D6 work that should not be mislabeled as a G1 failure

| Stage | Item | Required result |
| --- | --- | --- |
| D6 | Stoichiometric rank | **completed 2026-09-22:** `rank(S_eff) = 6` for the 12-state augmented B1 representation |
| D6 | Left nullspace | **completed 2026-09-22:** six readable relations verified as a complete basis; `rank(L)=6`, `L*S_eff≈0` |
| D6 | Independent coordinates | **completed 2026-09-22:** `[NTP,nt,A,AT,CP,TLcat]` |
| D6 | Exact conservation reduction | **completed 2026-09-22:** exact 12-to-6 reconstruction and all three full/reduced trajectory comparisons; regression remains PASS |
| D6 | Dimensional ↔ dimensionless trajectory check | **completed 2026-09-23:** all 12 states, 6 rates and both observables pass on all 1,441 output points for each DNA condition; six invariants and physicality pass |
| D6 | Mapping certificate | **completed 2026-09-23:** [nondim_map.json](../theory/nondim_map.json), with definitions, loaded reference values, source hashes and validation evidence |
| D7–D10 | Control groups | evaluate the dimensionless groups numerically and identify useful candidate control combinations |
| D7–D10 | Dominant-balance / sensitivity tests | determine which combinations actually organize behavior in the tested domain |
| later | `PURE_resource_core` freeze | choose/modify the project core only after structural and data evidence justify the decision |

The full 12-state nondimensional equations and the five published material/accounting balances are already audited; that evidence should be reused rather than repeated.

Two different energy-bookkeeping statements must now be kept separate:

- `4*NTP + CP + nt + D_nt + NXP + C = constant` is the readable “remaining high-energy resource + spent resource” total, but it is only `B_NTP + B_CP` and is **not independent**.
- `I6 = NXP + C - 3*a - 46*AT = constant` is analytically conserved and linearly independent of the five published balances; under the standard zero initial condition it becomes `NXP + C = 3*a + 46*AT`.

MATLAB has confirmed the formal rank and complete left nullspace for this representation: `rank(S_eff)=6`, `rank(L)=6`, and `L*S_eff≈0` with maximum floating-point residual about `2.78e-17`. The six readable relations form a complete left-nullspace basis. **D6 complete:** independent coordinates, exact full/reduced equivalence, dimensional/dimensionless back-transform verification and the mapping certificate are complete. The four regression suites pass 34/34 tests. See [conservation report](../theory/conservation_report.md) and [trajectory audit](../audit/nondim_trajectory_20260923/README.md). This status does not upgrade the B1 evidence to independent experimental validation or complete the later control/QSSA work.

## D. Optional repository-hardening decisions

These are useful but are not scientific G1 blockers:

- decide whether to enable/verify GitHub Actions MATLAB CI;
- decide whether to push the existing `ai-b1-baseline` annotated tag;
- perform human mutation-test protocol if independent software-hardening evidence is desired.

## E. Human checkpoints for future model changes

Whenever `PURE_resource_core` is changed, require an explicit human answer to:

1. What phenomenon cannot the previous model explain?
2. What new state/reaction is added or removed?
3. What material/resource ledger changes?
4. What new parameter is introduced and how is it identified?
5. What observation can distinguish the new mechanism from the previous one?
6. Does the change improve a held-out condition or only refit the same trajectory?

This prevents “more detail” from becoming an automatic substitute for evidence.
