# Level-C-guided topology-first reduction protocol v1

Status: research protocol, **HUMAN_REVIEW_REQUIRED** for all scientific choices. This protocol selects no existing reduction decision and creates no approved reduced SBML.

Level A means the five functional modules: initiation, elongation, aminoacylation (including formylation), termination/recycling, and energy regeneration. Level B means the 26 original source subsystem files. Level C means the 23 reviewed biochemical process categories in the existing reaction index; historical wording that describes CellDesigner reaction types is not an alternative category definition. A **Reduction Unit** is a connected pathway or catalytic cycle with declared inputs, outputs, intermediates and external interfaces. An **Effective Reaction** is a net stoichiometric transformation plus a mathematically justified kinetic law. A **Validated Reduced Module** passes its explicitly preregistered scientific gates and still requires a human decision about use.

## Method and evidence boundaries

1. Parse the canonical directed SBML reactions, literal MathML stoichiometry, source subsystem signatures and author operational input CSVs. Pin their bytes and the research source commit. Preserve every original ID, reverse partner, zero parameter and approved annotation. All-one structural inputs are never numerical author conditions.
2. Level-C categories guide navigation; they are not reduced reactions. A category may contain independent pathways and a reduction unit may cross categories. Source subsystems can include degradation families in addition to their principal catalytic family.
3. Determine boundaries from actual stoichiometric incidence. Inspect binding and release orders, competing paths, reverse channels, cycles, shared complexes and external consumers. Structural reachability and positive parameter channels do not imply observed flux.
4. Separate exact net chemical identity, internal steady-cycle balance, time-dependent boundary dynamics and intermediate accumulation. A net equation alone proves no effective kinetic law. Compute rational internal nullspaces and nonnegative directed-channel feasibility; include independent directions and zero-boundary cycles.
5. Preserve ATP, ADP, AMP, GTP, GDP, CP, Cr, PPi and PO4 separately. Derive free and bound inventories from source transformations. Complete enzyme totals include all occupied catalytic states. A binding event is sequestration, not hydrolysis. One PPi and two PO4 have distinct represented particle counts. Elemental, ionic, osmotic and absolute physical-unit claims require unavailable composition/unit evidence.
6. Test exact closure A f(x)=f_reduced(Ax), using counterexamples where it fails. Topology-first permits enzyme conservation, exact lumping, rapid equilibrium, standard/total QSSA, steady enzyme-state elimination or singular perturbation after topology is established. Large association constants alone justify none of them. Retain implicit equations or physical states when a simple law cannot be derived.
7. For an algebraic approximation declare positivity, selected physical root, local uniqueness and attractivity. Distinguish stationary enzyme uniqueness at fixed free substrates from uniqueness of the total-inventory inversion. Record singular or disconnected limits and unproved global properties. Stop an affected attempt if the necessary physical closure is unavailable.
8. Freeze candidate equations, source/code hashes, scenarios, initial conditions, all grids, scales, tolerances and gates **before** comparisons. Integrate from t=0 through the author's numerical 1000-s endpoint; report 0–0.05, 0.05–1 and 1–1000 separately, with all cumulative flows starting at zero. Never change a scale, parameter, gate or scenario after an outcome.
9. Compare microscopic and reduced isolated units, robustness scenarios and projected versus original initial states. Tighten solvers and independently check algorithms. Staged coupling and full embedding require their constituent candidates to pass prerequisite gates. A failed candidate stops its promotion; record the resulting downstream stage as not eligible with the actual preceding evidence.
10. Keep raw failure, solver warnings, negative values, commands, environment and manifests. Never clip trajectories, refit held-out parameters, erase earlier evidence or promote the future PURE_reduced_core. Independent mutants must exercise semantic predicates, not merely reject hashes.

## Status model

Statuses attach to a specified evidence layer and domain, rather than replace one another indiscriminately:

| Status | Required evidence |
|---|---|
| SOURCE_VERIFIED | Source identity, parameter/initial overlay and exact stoichiometry checked |
| STRUCTURE_VERIFIED | Boundaries, mapping, feasible net directions and declared moieties checked |
| KINETIC_CANDIDATE | Explicit equations, reconstruction, assumptions and mathematical limits documented |
| SUBSYSTEM_VALIDATED | All preregistered isolated/robustness gates pass with sufficient numerical certainty in the declared domain |
| FULL_MODEL_VALIDATED | Reliable source-faithful embedding passes full network gates after subsystem qualification |
| FAILED | An explicit structural, mathematical or numerical scientific gate fails |
| BLOCKED | Missing source, necessary closure, reliable solver or required evidence prevents a stage |

NUMERICALLY_INCONCLUSIVE is a numerical qualification, not a scientific pass. EMPIRICAL_APPROXIMATION labels fitted surrogates; none is selected in this v1 study. ONE_NET_DIRECTION_SUPPORTED, MULTIPLE_NET_DIRECTIONS_REQUIRED and INSUFFICIENT_EVIDENCE describe structural direction tests only. Every acceptance recommendation is HUMAN_REVIEW_REQUIRED. Independent script verification cannot approve a scientific model.

## v1 acceptance targets

Exact source stoichiometric equivalence and zero symbolic residual for exact identities; normalized numerical conservation residual ≤1e-8; no meaningful negative inventory beyond documented solver allowance. For 1–1000: maximum scaled free-concentration or retained-pool error ≤0.05, normalized RMS net-flux error ≤0.10, maximum normalized cumulative resource-flow error ≤0.02. Embedded Pept0003 endpoint error ≤0.05 if the full stage is eligible and executed. Positive inventory/reference scales and convergence uncertainty are fixed in the scenario preregistration. These are engineering research targets, not literature-established accuracy guarantees. Initial-layer errors remain disclosed even if long-term gates pass.
