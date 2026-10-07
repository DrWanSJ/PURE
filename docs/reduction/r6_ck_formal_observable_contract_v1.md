# R6 CK Branch A formal observable contract v1

This is a new prospective CK contract. The researcher's follow-up explicitly selects `GROSS_FLUX_NOT_REQUIRED_FOR_CK_PROMOTION` and makes A, B, C, D, F and H mandatory. The verbatim decision is `results/reduction/r6_ck_validation/human_branch_a_decision_20261007.txt`. The initial ambiguity-stop package is preserved byte-for-byte under `audit_stop_001`; its findings and verification remain historical. No R3/R4/R5/R5-C criterion or outcome is changed. Approval to test is not scientific promotion.

## Candidate, source and domain

`CK_PARTIAL_EQUILIBRIUM_V1` is the R5 mechanism-first partial-equilibrium candidate, at the actual eta=1 parameters, with exactly 332/333 and 336/337 fast. All 964 non-fast canonical reactions remain dynamic. No effective parameter, fitted initial value, source projection, clipping or time shift is introduced. The R5 centered 212-coordinate chart, affine 241-state reconstruction and 27 SOURCE_GENERAL conservation laws are retained. A per-condition anchor recomputes the exact class from that condition's unchanged canonical initial state.

The nine conditions and their initial-value multipliers are copied exactly from the completed R3 grid. R3_ADVERSE is excluded. The primary reference reporting grid remains zero plus 200 logarithmic times from 1e-4 to 1000 s. An additional disclosed startup grid has zero plus 100 logarithmic points from switch/1000 to switch. The switch is added as an event boundary, rather than interpolated from sparse source samples. This supplemental grid is frozen before the campaign; it changes no historical report.

Historical source trajectories, rates, extents and R4 full-source uncertainty probes are reusable only after the explicit R6 source verifier validates raw hashes, transitive source dependencies, canonical author kinetics, parameters, initial values, condition definitions and solver/reporting protocols. No historical reduced trajectory is reused. Full source solves over 0–1000 s are not recomputed when this verification passes.

## Startup and continuity

Reproduce the R5 rule exactly: tau0=1/(2*p0+1000), switch=10*eta*tau0, eta=1, p0 from the unmodified initial fast totals. No result-based startup-time adjustment is allowed. The full canonical 241-state startup is newly solved only over [0,switch], supplying the exact missing boundary state and controlled startup integrals. This is the same ODE, parameters, initial state and dense-output startup policy used by R5; a primary/tighter pair quantifies its numerical uncertainty. The complete source trajectory is never projected onto h0.

The hybrid equals the full startup for t<switch and reconstructs h0 from z=T*x_full(switch) at switch. Record both boundary states and the nonzero projection jump. All startup net and gross extents are retained; extent origin is t=0. The switch reconstruction jump is not silently relabeled as source reaction turnover. Raw net/algebraic accounting and accounting after explicitly subtracting the reconstruction jump are separate descriptive reports.

## Mandatory classes and gates

All curve gates are applied independently on FULL_WINDOW and POST_INITIAL_LAYER. COMPOSITE_OR_HYBRID identifies the full startup plus reduced continuation, and POST_0P05_DIAGNOSTIC is reported separately without replacing either gate. The right-hand hybrid boundary is included in POST_INITIAL_LAYER; the full startup's left boundary is separately scored under H.

| Class | Required observable | Frozen gate |
|---|---|---|
| A | All retained 212 slow coordinates, T0/T1/B, free resources and the source product Pept0003; all reconstructed 241 source trajectories are conservatively scored | E_inf <=0.01 |
| B | CK, CK_ADP, free CP, CK_CP and CK_CP_ADP, including both eliminated and otherwise algebraically affected fast entries | E_inf <=0.01 |
| C | Each of 27 exact SOURCE_GENERAL law drifts L(x-x0), independently for source and hybrid | absolute drift <=1e-8 |
| D | Both kinematically reconstructed fast-pair currents, plus net channels touching declared free resource/product identities or CK species | E_inf <=0.05 |
| F | Cumulative net extents from t=0 for the same registered net-channel set, including startup conversion | E_inf <=0.01 |
| H | Identical original initial state, retained full startup and startup extents, unchanged switch rule, zero-origin extents, physical CK root domain, switch-state jump and retained-total continuity | exact protocol assertions; scaled state jump <=0.01; absolute slow-coordinate jump <=1e-8 |

The source product is released fMGG (`Pept0003`). The historical GFP model card does not define a mature-GFP observable for this source model. Total enzyme occupancy, resources, tRNA and peptide intermediates remain reconstructable through the complete state lift. Exact source laws are not the dynamic fast totals T0/T1/B.

## Rate/extent semantics and threshold justification

Canonical exact reverse pairing yields 290 pairs and 388 unpaired channels, hence 678 oriented net channels. The orientation is the original exact-reverse table's forward column, validated against canonical stoichiometry. All 678 net extents are integrated for accounting. The mandatory resource subset is selected before solving by literal participant intersection with ATP, ADP, AMP, GTP, GDP, GMP, CP, Cr, PPi, PO4, Gly, Met, fMet, THF, FD, mRNA, Pept0003, both free/charged charging tRNAs and fMet-tRNA, or any CK species. The exact membership and columns are in `formal_net_channel_membership.csv`; it does not depend on measured errors.

For the two approximated pairs, derive N_qf from canonical columns; it has rank two. Use j=N_qf^-1[Dh0*F-(S_nonfast*v_nonfast)_q]. Evaluating gross kinetics at h0 would yield zero leading net and is not substituted for this finite redistribution current. This is the R5-C kinematic observable reconstruction; no first-order state displacement model is fitted or implemented in Branch A.

E_inf=max_window|reduced-source|/max(max_window|source|,floor). Scales use only the full source, separately for each declared window. State/total and net-extent floors are 1e-6 in the reference concentration convention; net-rate floor is 1e-9 in concentration/s. The state level and floors inherit the equivalent historical state semantics. Net current and net extent gates use the researcher's proposed 5% instantaneous-flow and 1% cumulative-conversion budgets as a new, explicitly frozen CK scientific-use criterion: the physical units and error-budget interpretation match process flow and accumulated biochemical conversion, while the observable is signed net conversion. This is not a claim that an old directed aminoacylation gate automatically applies to CK. Cancellation is assessed explicitly; near-zero channels use the declared absolute floor budget.

The H state-jump gate is the same relative state-discrepancy budget as A/B, applied to the boundary rather than fitted away. Slow-total continuity is an exact algebraic identity, evaluated under the 1e-8 conservation arithmetic budget. Initial outer occupancy mismatch and startup duration are mandatory reported observables but have no fabricated accuracy threshold: protocol identity, actual hybrid initial state, switch continuity and startup-integral retention carry the H gates. Numerical physical-root checks cover reported CK states and accepted slow totals. Tiny unused reconstructed negative roundoff remains visible; no global mathematical positivity theorem or absolute-unit validation is claimed.

## Numerical uncertainty and integration

Primary startup and reduced BDF solves use rtol=1e-10, atol=1e-14; fresh tighter startup/reduced probes use 1e-11 and 1e-15. Net extents are ODE integrators on each reporting/startup segment using DOP853, compensated accumulation and the same primary tolerances. A tighter same-primary-trajectory extent solve isolates quadrature sensitivity; tighter-state trajectory extents use 1e-11/1e-15. All 968 gross rates/extents are retained descriptively in the same bookkeeping integration but enter no promotion gate.

The reference uncertainty envelope uses the previously frozen R4 full-source 1e-8/1e-14 state probe with its original 1e-10/1e-14 extent integration. Fresh tighter startup probes cover the added startup boundary. For a difference, add source and reduced tolerance-probe envelopes; extents also add same-trajectory quadrature sensitivity and a conservative floating cancellation estimate from source forward/reverse gross integrals. These are empirical numerical uncertainty diagnostics, not rigorous continuum bounds.

PASS/FAIL is resolved only when uncertainty <=10% of the corresponding gate budget. Error+uncertainty <=gate gives RESOLVED_PASS; max(0,error-uncertainty)>gate gives RESOLVED_FAIL; all other cases are NUMERICALLY_UNRESOLVED. An unresolved observable prevents formal PASS. Resolved failures remain explicit even if another class is unresolved. State accuracy and net-current accuracy are independently classified.

Each state solve is bounded at 1800 s and 300000 RHS calls; each extent integration is bounded at 1800 s. Noncompletion retains partial accepted states/checkpoints and is numerical noncompletion, not scientific rejection. No bounds, thresholds or windows are adjusted after seeing a result.

## Gross limitation and balance policy

E and G are `SOURCE_PROVENANCE_PRESERVED / DESCRIPTIVE / BUT_NOT_VALIDATED`, not part of the promotion conjunction. Report their rates, extents and gross directed-ledger residual, without implying accurate microscopic reconstruction. All 968 source reactions, original parameters and IDs remain intact.

Four reports remain distinct: exact source-law drift (mandatory C gate), net stoichiometric accounting, reconstructed algebraic-state accounting, and gross directed-ledger residual. The last three are descriptive numerical/accounting diagnostics; no unjustified copied gross-ledger gate silently replaces exact-law drift. D/F retain independent gates on scientifically required net flows/extents. No gross-ledger failure can veto Branch A, and no such failure is hidden.

A full formal PASS requires every mandatory observable gate on every condition. A resolved net-current failure with validated states is `CK_STATE_VALID_NET_CURRENT_FAIL`, even if other observables still need numerical resolution. No result automatically promotes CK or PURE_reduced_core. Stop after the nine-condition campaign and independent verification; no first-order follow-on, aminoacylation work, adverse run, push or merge.
