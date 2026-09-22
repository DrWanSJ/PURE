# G1 Pending Human Actions

**Related gate:** G1 — Week 1  
**Status:** tracking list; not all items are G1 blockers  
**Last updated:** 2026-09-22

This file separates work that still requires explicit human judgment from work that is already machine-checked, and separates G1 open evidence from tasks that properly belong to G2 or later.

## A. Human actions carried out of G1

| Priority | Human action | Why human review is needed | Current evidence | Blocks entering G2? |
| --- | --- | --- | --- | :---: |
| High | Complete the compact human-only checks in `docs/audit/human_b1_audit.md` | Human review is reserved for source semantics, inferred assumptions, evidence wording and the blind-audit decision; implementation consistency is machine-checked | automated/equation-level checks pass; compact human checklist remains | no |
| High | Review the B1 QC definitions in `benchmark_v0.md` / `qc_v0.json` | The machine results pass, but the user should understand what each metric proves and does not prove | nonnegativity, conservation, repeatability and solver convergence pass | no |
| Medium | Decide whether a strict **blind** Fig. 4 human audit is required | The existing 48-point review was non-blind and therefore is not independent evidence | non-blind human review complete | no |
| Medium | Review licensing/distribution decision for tracked publisher PDFs | This is a project/repository governance decision, not a numerical task | `docs/project/licensing_review.md` exists | no |
| Medium | Obtain mentor sign-off on the G1 wording/status | Gate status is a project decision; this report records the current proposed closure | G1 report prepared | no |

### Notes

- Do **not** redo parameter, rate-law, ODE, stoichiometry, observable-mapping, nonnegativity or conservation checks by manual code inspection when the B1 MATLAB test suites pass. Human review is limited to source semantics, inferred assumptions, evidence wording and the blind Fig. 4 decision.
- Do **not** describe the current Fig. 4 review as independent blind validation.
- Do **not** treat absence of machine-readable experimental data as a reason to invalidate the B1 literature reproduction; it limits the experimental/B2 claim.

## B. G2 / D6 work that should not be mislabeled as a G1 failure

| Stage | Item | Required result |
| --- | --- | --- |
| D6 | Stoichiometric rank | compute `rank(S)` for the chosen model representation |
| D6 | Left nullspace | compute and chemically interpret conservation relations |
| D6 | Independent coordinates | identify an exact reduced coordinate set or equivalent representation |
| D6 | Dimensional ↔ dimensionless trajectory check | integrate both forms, back-transform, and compare trajectories |
| D7–D10 | Control groups | evaluate the dimensionless groups numerically and identify useful candidate control combinations |
| D7–D10 | Dominant-balance / sensitivity tests | determine which combinations actually organize behavior in the tested domain |
| later | `PURE_resource_core` freeze | choose/modify the project core only after structural and data evidence justify the decision |

The full 12-state nondimensional equations and five invariants are already audited; that evidence should be reused rather than repeated. Formal conservation reduction remains a distinct D6 task.

## C. Optional repository-hardening decisions

These are useful but are not scientific G1 blockers:

- decide whether to enable/verify GitHub Actions MATLAB CI;
- decide whether to push the existing `ai-b1-baseline` annotated tag;
- perform human mutation-test protocol if independent software-hardening evidence is desired.

## D. Human checkpoints for future model changes

Whenever `PURE_resource_core` is changed, require an explicit human answer to:

1. What phenomenon cannot the previous model explain?
2. What new state/reaction is added or removed?
3. What material/resource ledger changes?
4. What new parameter is introduced and how is it identified?
5. What observation can distinguish the new mechanism from the previous one?
6. Does the change improve a held-out condition or only refit the same trajectory?

This prevents “more detail” from becoming an automatic substitute for evidence.
