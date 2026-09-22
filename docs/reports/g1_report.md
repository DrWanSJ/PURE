# G1 Gate Report

**Gate:** G1 — Week 1  
**Date:** 2026-09-22  
**D6 status synchronized:** 2026-09-23
**Status:** **PASS WITH OPEN ITEMS**

This report closes the Week 1 gate defined in `tasklist.md`: freeze the primary benchmark, state definitions, units, model boundary, baseline equations, and the first analysis/interface contracts. It does **not** claim independent experimental validation or freeze the final project model.

## 1. Research object and frozen identities

### 1.1 B1 benchmark

The only B1 benchmark is `PURE_literature_reference`, a deterministic coarse-grained reconstruction of Mavelli, Marangoni & Stano (2015).

Its Week 1 purpose is to provide a reproducible literature reference for:

- equation and parameter transcription;
- numerical integration;
- observable mapping;
- conservation/accounting checks;
- later theoretical analysis.

The benchmark is **not** equivalent to independent experimental validation.

Primary evidence:

- [benchmark registry](../project/benchmark_registry.md)
- [model card](../model_card.md)
- [B1 execution/QC report](../validation/benchmark_v0.md)
- [machine-readable QC](../validation/qc_v0.json)

### 1.2 Project core

`PURE_resource_core` is defined at G1 as a **candidate project backbone**. It has a modeling direction, but its exact state set and equations are not yet frozen.

The candidate core may inherit the TX–RS–TL–EN module structure and resource-accounting logic from the literature reference. Whether it should split ATP/GTP, add explicit resource states, or alter the effective stopping/decay mechanisms will be decided from later conservation, nondimensional, control, reduction, and data evidence.

Therefore:

- `PURE_literature_reference`: **frozen B1 reference**
- `PURE_resource_core`: **candidate / not yet frozen**

No new mechanism is added at G1 solely to make the model more detailed.

## 2. What the current reference model can describe

The current reference model supports the following **model-internal** interpretation.

### 2.1 Expression startup

At the reference initial condition:

- `V_TX(0) > 0`: DNA and NTP are present, so transcription starts immediately.
- `V_RS(0) > 0`: amino acids, uncharged tRNA and NTP are present, so tRNA charging starts immediately.
- `V_TL(0) = 0`: initially `nt = 0`, so translation cannot start until polymerized RNA accumulates.
- `V_EN(0) = 0`: initially `NXP = 0`, so energy regeneration starts only after NXP is produced.

Thus the startup sequence is not “all modules simultaneously nonzero”: TX and RS start first; TX builds the RNA-residue pool, which then enables TL.

This is a statement derived from the model equations and initial conditions, not a claim that the same ordering has been independently measured experimentally.

### 2.2 Reproduced observables

All three Fig. 4 DNA conditions (0.34, 1.7, 6.8 nM) have been executed.

The current reproduction target is the paper's **calculated continuous curves**, not the dotted experimental data. The repository also records a 48-point human visual review of those calculated curves; that review was non-blind.

Observable mappings are:

- `mRNA = nt / (3L)`
- `protein = a / L`
- `L = 238 aa` for GFP.

### 2.3 Model-internal causes of slowing or stopping

The reference model contains:

- first-order degradation of `nt`;
- first-order loss of `TLcat`;
- finite batch resource pools.

These mechanisms can reduce transcription/translation capacity and contribute to late-time slowing or plateau behavior **inside the model**. Their causal contributions to the simulated trajectory can be tested by numerical intervention (for example, setting one degradation rate to zero at a time).

At G1, this is not promoted to a claim that real PURE stopping is experimentally proven to be caused by either degradation term.

## 3. State, accounting, fixed-input and boundary classification

The simulator integrates 12 explicit states: the 10 canonical paper ODE states plus two repository accounting integrators.

| State | Explicitly integrated | Feeds back into rates | G1 interpretation |
| --- | :---: | :---: | --- |
| NTP | yes | yes | dynamic feedback state |
| NXP | yes | yes | dynamic feedback state |
| nt | yes | yes | dynamic feedback state |
| A | yes | yes | dynamic feedback state |
| T | yes | yes | dynamic feedback state |
| AT | yes | yes | dynamic feedback state |
| a | yes | no | canonical product/output state |
| CP | yes | yes | dynamic feedback state |
| C | yes | no | canonical product state |
| TLcat | yes | yes | dynamic feedback state |
| D_nt | yes | no | repository accounting state |
| D_TLcat | yes | no | repository accounting state |

`D_nt` and `D_TLcat` have ODEs and are explicitly integrated, but they do not feed back into any rate law. They close the degradation ledgers used in the conservation checks.

The fixed inputs are:

- DNA — fixed template input; it modulates `V_TX` through a saturation factor.
- TXcat — fixed catalyst input.
- RScat — fixed catalyst input.
- ENcat — fixed catalyst input.

TLcat is different: it is an explicitly dynamic catalyst because the reference model includes TLcat degradation.

The reference model boundary is:

- batch;
- fixed volume;
- well mixed;
- no membrane exchange;
- no continuous feed/dilution;
- no infinite external material reservoir.

Conservation relations imply algebraic dependence between subsets of the 12 explicit states. G1 keeps the full canonical reference for auditability; the exact six-coordinate representation was subsequently completed in G2/D6 and verified against it.

## 4. Frozen units and environment

For the B1 reference:

- internal time: `s`;
- concentration: `uM`;
- reaction rate: `uM/s`;
- benchmark display time may be converted to hours.

The 2026-09-22 environment smoke test passed for:

- MATLAB R2025b Update 5;
- Symbolic Math Toolbox;
- Optimization Toolbox;
- SimBiology.

Evidence: `results/environment/toolbox_check.json`.

Base MATLAB remains sufficient for the B1 benchmark itself; the additional toolboxes are available for later project analysis.

## 5. Completed evidence and evidence level

| Evidence | Status | What it supports | Level |
| --- | --- | --- | --- |
| Benchmark registry / source lock | complete | identity, source files, parameters, units, conditions | documented |
| Species/reaction ledgers and model card | complete | explicit model semantics and bookkeeping | documented |
| Table 1 / Table 2 transcription | checked against source | repository values match literature source | documented / audited |
| Human B1 source-to-repo audit | **complete (H01-H06 = Y)** | model semantics, parameter transcription, inferred assumptions, omitted mechanisms, Fig. 4 source wording and paper-text anchors | independent human source review |
| Equation-level repository tests | pass | internal equation/rate-law consistency | numerical/software |
| B0 fixtures | pass locally | math/software procedures; **not** PURE validation | numerical/software |
| Fig. 4 three-condition execution | complete | literature calculated-curve reproduction | numerically supported |
| 48-point Fig. 4 human visual review | complete, non-blind | human review of curve identity/shape/magnitude | non-independent human evidence |
| Nonnegativity QC | pass | simulated states remain nonnegative | numerically supported |
| Conservation QC | pass | max scaled mass-balance residual about `5.82e-15` | numerically supported |
| Solver convergence / repeatability QC | pass | numerical robustness of baseline workflow | numerically supported |
| First full nondimensional model | complete and audited | dimensional/dimensionless equation equivalence and invariants | derived + numerically supported |
| D6 exact reduction and trajectory back-transform | **complete 2026-09-23** | 12/6-state equivalence, independently integrated compact dimensionless 12-state equivalence and mapping certificate | mathematical/numerical |
| Independent experimental/B2 validation | not established | no claim permitted | not available |

The human audit record is `docs/audit/human_b1_audit.md`: H01-H06 are `Y`, both MATLAB test suites passed, and H07 records that a strict blind Fig. 4 audit is not required for the B1 literature-reproduction claim. This does **not** upgrade the evidence to independent experimental validation.

The nondimensional audit is recorded in [dimensionless audit report](../audit/dimensionless_20260921/REPORT.md). D6 is now complete: the verified rank and complete left-nullspace basis (`rank(S_eff)=6`, `rank(L)=6`, `L*S_eff≈0`), independent coordinates, exact reduction, full/reduced trajectory comparison, dimensional/dimensionless back-transform and [mapping certificate](../theory/nondim_map.json) are documented in the [conservation report](../theory/conservation_report.md). The final four MATLAB suites pass 34/34 tests; canonical scientific sources and existing audited scaling are unchanged.

## 6. What G1 does not claim

G1 does **not** claim that:

- the Fig. 4 dotted experimental curves have been independently validated;
- machine-readable Stögbauer 2012 experimental data are present in the repository;
- B0 fixture success proves the PURE RHS is scientifically correct;
- the current 12 explicit simulator states are 12 independent dynamical degrees of freedom;
- the reference model is the final or uniquely correct `PURE_resource_core`;
- real PURE stopping is experimentally proven to be caused by nt or TLcat degradation;
- the effective deterministic rate laws are validated stochastic propensity functions;
- G2 control analysis, QSSA/fast-slow approximation, or broader model reduction is complete.

## 7. Missing data and open questions

The main open evidence / later-stage items are:

1. **Independent experimental data.** Machine-readable Stögbauer 2012 RNA/protein trajectories are absent from the repository; current Fig. 4 reproduction targets the literature's calculated curves. A strict blind raster audit was explicitly judged unnecessary for the B1 reproduction scope.
2. **Project-core definition.** The exact `PURE_resource_core` state set and equations must be decided from later structural and data evidence, not assumed at G1.
3. **D6 structural follow-up (complete).** The five published balances and `I6 = NXP + C - 3*a - 46*AT = constant` form the verified complete left-nullspace basis. Independent coordinates `[NTP,nt,A,AT,CP,TLcat]`, exact reconstruction and all three full/reduced trajectory comparisons are complete. Later control and approximation analyses remain open.
4. **Trajectory-level inverse transform (complete).** On 2026-09-23, independently integrated dimensional/compact dimensionless trajectories passed the preregistered criteria for all 12 states, 6 rates, mRNA and protein in all three DNA conditions, with the final mapping certificate generated. See [native validation evidence](../audit/nondim_trajectory_20260923/README.md).

Human-owned and later-stage actions are tracked separately in [g1_pending_human_actions.md](g1_pending_human_actions.md).

## 8. Direct answers to the four G1 questions

### Q1. What phenomena are explained/reproduced at this stage?

Under the Mavelli 2015 B1 conditions and 0–4 h benchmark window, the current reference reproduces the paper's calculated Fig. 4 `nt` and `a` trajectories for three DNA concentrations and provides the corresponding mRNA/protein mappings. It also gives a model-internal account of startup through TX-driven RNA accumulation followed by translation activation.

Evidence level: **derived + numerically supported literature reproduction**, not independent experimental validation.

### Q2. Which quantities are dynamic states, constraints, or reservoirs?

The simulator has 10 canonical physical ODE states plus two no-feedback accounting states (`D_nt`, `D_TLcat`). DNA, TXcat, RScat and ENcat are fixed inputs rather than dynamic states. The batch model has no continuous feed and no infinite external material reservoir.

Conservation relations create algebraic dependencies. The canonical reference retains the full explicit representation; the equivalent six-coordinate implementation and its trajectory verification are complete in D6.

### Q3. What data are missing?

The most important missing external evidence is machine-readable experimental RNA/protein data suitable for independent comparison. Its absence prevents a B2-style experimental validation claim, but it does not prevent completion of the B1 literature reconstruction or G2 structural analysis.

The human B1 source-to-repository audit is complete (H01-H06 = `Y`, as recorded in section 5); it does not supply the missing independent experimental trajectories.

### Q4. Why keep this coarse-grained backbone instead of adding more detail now?

At G1, the current model is retained because it is a reproducible literature reference and a controlled starting point for checking balances, scales, control combinations and failure modes. It is **not** assumed to be the final project model.

Additional mechanistic detail should be added only when later analysis or data show that the current coarse-graining cannot answer the project questions or close the required material/resource accounting. The `PURE_resource_core` is therefore kept as a candidate until that evidence exists.

## 9. Gate decision

**G1 decision: PASS WITH OPEN ITEMS.**

The primary B1 benchmark, equations, parameters, units, model boundary, execution path, QC path, initial nondimensional description and interface contract are sufficiently frozen to enter G2.

The following items must remain visible as explicit open work rather than being silently treated as complete:

- independent experimental data and B2 validation;
- later control, sensitivity and QSSA/fast-slow analyses;
- evidence-based definition and later freeze of `PURE_resource_core`.

The human B1 source audit and all D6 structural/mapping deliverables are complete. The remaining items are carried forward without reclassifying the completed B1 literature reconstruction as independent experimental validation; the G1 gate decision is unchanged.
