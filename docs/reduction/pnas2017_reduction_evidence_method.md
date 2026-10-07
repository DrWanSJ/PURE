# PNAS2017 reduction evidence method — v0

This is an evidence preparation layer for human kinetic-reduction review at source HEAD `3e22aeeb6124e2ad7d3373e0cf056383bf9c8c1e`. Its domain is **AUTHOR_REFERENCE_CONDITION_ONLY**. G1-PNAS is formally PASS / CLOSED, but that result does not certify a reduced model. The approved [species information contract](species_information_contract_summary.md) retains I=42, II-A=57, II-B=91, III=22 and C=29. All 968 [kinetic decisions](reduction_decisions.csv) remain PENDING; all 96 [process choices](human_reduction_review.md) remain unselected. `PURE_reduced_core` remains `NOT_VALIDATED`.

The [global quick reference](pnas2017_reduction_quick_reference.md) and its 16 process pages are compact views of the CSVs, not independent scientific authority. The original [aminoacylation reference](aminoacylation_qssa_quick_reference.md) and historical failed/blocked candidates are preserved.

## Frozen inputs and numerical domain

The [preregistration](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/evidence_preregistration.json) froze definitions and hashes before metric computation. It records canonical SBML, the derived numeric-stoichiometry execution SBML, author initial-value/parameter CSVs, existing classifications and process memberships, pool member lists, trajectory, tolerances and exclusions. The [manifest](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/evidence_manifest.json) records actual software versions, checks, generated-file hashes and availability counts. The canonical combined model remains 241 species and 968 directed reactions; source subsystem attributions may overlap.

The preserved [RoadRunner reference trajectory](../../results/pnas2017_reference/rr_cvode_author_csv_20260924/trajectory.csv) supplies 200 stored samples on `logspace(-4,3,200)`, through 1000 s. Loading the effective model to evaluate rates or derivatives is distinct from reintegrating it. The exact author initial state at `t=0` is a separately labeled `SUPPLEMENTAL_NUMERICAL_DIAGNOSTIC`; it is excluded from primary distribution summaries. The first stored state equals the author initial state while its stored timestamp is `1e-4`. We retain both without shifting time: this start-time ambiguity prevents a claim that the stored samples fully resolve the initial layer. A QSSA initial-layer matching test has not been performed.

Author CSVs omit absolute chemical units. Concentrations, fluxes and concentration-denominator floors use the repository's inferred reference concentration convention; no authoritative µM conversion is asserted. Times use the stored author/engine seconds convention, and reciprocal Jacobian values inherit that convention. See the [chemical ledger](../pnas2017/chemical_ledger.md). Rates and states retain signed numerical roundoff, without clipping or parameter fitting.

Primary medians and percentiles give equal weight to the 200 logarithmic-grid samples; they are **not time-weighted fractions** of the 1000 s interval. Quantiles use linear interpolation. Directed extents are trapezoidal approximations on supplemental `t=0` plus the stored grid, integrated from 0 to 1000 s. They are not solver-integrated extents or a new flux-balance acceptance test; the stored start-time convention and coarse late intervals limit quadrature accuracy.

## Three evidence levels

| Level and table | Meaning and links | What it cannot certify |
| --- | --- | --- |
| [Reaction evidence](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_evidence.csv), 968 rows | Original event, source modules/family, exact stoichiometry, author activity, rate/extent, free-resource and particle deltas; links to process, state, pair, pool and ledger evidence | A reaction has no unique QSSA state or intrinsic process relaxation time |
| [State evidence](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_evidence.csv), 241 rows | Contract class, concentration, production/consumption, QSS defect, turnover proxy, registered pool and reconstruction evidence | Cancellation alone does not validate algebraic elimination or protect a hidden resource |
| [Reverse-pair evidence](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reverse_pair_evidence.csv), 290 rows | Exact stoichiometric reverse mapping, two directed rates/extents, exchange/net flux and equilibrium defect | Pair balance does not approve rapid equilibrium under a changed domain or establish a reduced rate law |

Original IDs are the join keys. Many-to-many [reaction-pool links](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_pool_metrics.csv) retain distinct resource pools instead of collapsing them. Long-form [QSS](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_qss_timeseries.csv) and [pair](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reverse_pair_equilibrium_timeseries.csv) samples preserve unavailable points and their reasons. [Process timescales](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/process_timescale_evidence.csv) apply to the exact candidate lists in the existing 16 review cards.

These joins and the [navigation index](../../models/pnas2017_full_reference/audit/reduction_evidence_v0/evidence_navigation.json) provide derived structured navigation: original IDs, stoichiometry, author values and quoted contract/card membership are `EXTRACTED`; numerical summaries and diagnostic process interpretations are `INFERRED` computations; incomplete total-token composition, unit semantics and unchosen slow coordinates remain `AMBIGUOUS` or explicitly unresolved. Existing annotation provenance is preserved. None of these labels makes the derived layer source authority. Freshness requires the preregistered input hashes and manifest artifact hashes to match, plus a successful independent verifier run; a readable CSV alone does not establish freshness.

## Rates, QSS defect and turnover

With source stoichiometry `S` and directed rates `v`, use `f = S v`. For state `z`,

```text
P_z = sum_r max(S_zr v_r, 0)
C_z = sum_r max(-S_zr v_r, 0)
delta_QSS = |f_z| / (P_z + C_z)
tau_turnover = |x_z| / (P_z + C_z)
```

The QSS ratio is available only when `P_z+C_z > 1e-12`. Otherwise the sample is `LOW_FLUX_UNINFORMATIVE`; `0/0` never becomes a numerical zero. A zero-concentration state can have informative production and a QSS defect; its turnover time remains unavailable unless `x_z > 1e-12`. Turnover is a traffic-based proxy and differs from `|x/f|` and an eigenmode relaxation time. Tiny signed rates caused by retained roundoff do not silently become physically nonnegative fluxes.

Every sampled defect and informative flag remains inspectable. Summary QSS statistics use only informative primary samples and report their fraction. A low defect measures cancellation at the recorded trajectory point. It supplies no algebraic manifold, existence/uniqueness guarantee, stability domain, coordinate choice or full-versus-reduced error bound.

## Registered pools, occupancy and sequestration

Pool membership is taken only from preregistered existing explicit lists, with coefficient one for each registered member. The generator independently certifies the sum of the corresponding stoichiometric rows: zero for all author-enabled reactions establishes reference conservation; checking all source reactions establishes the separate unconditional certificate. Coarse or incomplete candidate lists that fail this check remain unresolved, with no invented members. A free counterpart must be the unique approved Class-I member or an explicitly registered ribosome singleton; it is not guessed from spelling.

For a qualified pool with positive denominator and no negative member at a sample,

```text
total = sum_registered_members x_s
free_fraction = x_free / total
nonfree_fraction = 1 - free_fraction
occupancy(member) = x_member / total
```

For an active pool, nonfree fraction is bound occupancy. A family total may include a degraded sink, so its nonfree fraction includes degraded material and must not be called exclusively complex occupancy. Unavailable samples retain their reason; no ratio is clipped into `[0,1]`. Multiple valid token pools remain separate rather than receiving a fabricated single denominator. Free/total scalar fields are N/A for unresolved or nonunique membership, while separate pool links retain valid evidence.

Enzyme occupancy and protected-substrate sequestration ask different questions. Large occupancy shows that free enzyme may poorly represent total enzyme. A quantitative bound amino-acid, nucleotide or tRNA token fraction additionally requires a complete vetted token definition. Missing bound-moiety membership stays `BOUND_MOIETY_MEMBERSHIP_UNRESOLVED`; enzyme-pool size or a species name does not supply that definition.

## Local Jacobian and time-scale diagnostics

At each primary point the full canonical RHS Jacobian is restricted to the exact candidate-state list `z` of each process card. All source reactions remain in the derivative, including those crossing the process boundary. This is a coordinate-dependent local `J_zz` block, not an independently closed subsystem or an approved fast manifold.

The neutral threshold combines the preregistered absolute floor `1e-10` and relative floor `1e-12` times the spectral scale. Neutral and nondecaying modes are retained and never inverted into fast times. A structural lower bound is `n_z - rank_exact(S_z,Rdep)`, where `Rdep` are author-enabled reactions depending on at least one candidate state. Its left-nullspace guarantees structural neutral modes; numerical near-zero counts may be larger. Stable modes use `tau = 1/(-Re(lambda))` only outside the neutral band. Spectra and the full stable range matter; a single fastest mode can hide slow candidate modes.

The preregistered comparison uses positive, informative turnover proxies for Class-I reaction-interface states outside `z`; their per-time median is a **candidate slow basis**, not a certified slow coordinate. At the same point,

```text
R_tau = median(interface turnover times) / median(stable J_zz relaxation times)
epsilon_tau = 1 / R_tau
```

Large `R_tau` means greater separation under this explicitly chosen diagnostic convention. The reciprocal has a separate name. No fast/slow coordinate choice has been scientifically approved, so each process retains `timescale_status = NEED_MORE_INFORMATION`, including rows with numerical proxy evidence. An empty candidate set receives `N/A_NO_CANDIDATE_STATES`. No process is selected for QSSA from this ratio. The preregistration defines no weak/strong evidence cutoffs.

## Exact reverse pairs and rapid equilibrium

The contract-derived mapping is checked against canonical reactant/product stoichiometry: 290 disjoint exact reverse pairs cover 580 directed reactions. For an informative, author-enabled pair,

```text
exchange_flux = |vf| + |vr|
net_flux = vf - vr
delta_eq = |vf - vr| / exchange_flux
net_extent = forward_extent - reverse_extent
```

`exchange_flux <= 1e-12` is `LOW_FLUX_UNINFORMATIVE`. If either official direction has `k1=0`, the pair is `REFERENCE_DIRECTION_DISABLED` and its equilibrium defect is unavailable even if the other direction is active. The two directed rates and extents remain visible. Fractions below `1e-1`, `1e-2` and `1e-3` are descriptive proportions of informative sampled points only; they select no reduction action. Unpaired reactions explicitly receive `N/A_NO_EXACT_REVERSE_PAIR`.

Free/total ratio measures a pool's distribution. Equilibrium defect measures opposing pair flux cancellation. Neither substitutes for the other. QSSA can involve several incoming/outgoing paths with net throughput, so it is also distinct from balancing one reverse pair.

## Ledger boundary and human choices

The source supplies exact individual event stoichiometry, explicit free ATP/ADP/AMP/GTP/GDP/PO4/PPi and other resource deltas, and the represented-particle proxy `sum(products)-sum(reactants)`. The source uses `PO4` as Pi; the nonunit `2 PO4` product in `re0000000414` is preserved. Source/ledger and annotation links also expose amino-acid/tRNA, ribosome/factor occupancy and peptide reconstruction obligations. Complete elemental, charge, protonation, Mg and bound-resource composition are still unresolved.

`EXACT_EVENT_STOICHIOMETRY_KNOWN` is not reduced-ledger closure. An exact reverse representation preserves event stoichiometry, but no hypothetical QSSA/lumping transformation has been evaluated here. Ledger closure and kinetic validity require separate evidence. The particle count is a represented-species proxy, not osmotic pressure or ionic strength.

QSSA eliminates states through a tested algebraic closure; total-coordinate QSSA additionally carries protected totals and reconstructs free/bound partitions. Lumping aggregates states or events and needs a justified rate plus reconstruction. Conservation reconstruction uses an exact invariant to recover coordinates and does not itself invoke a fast approximation. Rapid equilibrium imposes a justified pair balance. KEEP, LUMP, QSSA, RAPID EQUILIBRIUM, CHEMOSTAT and DROP remain human choices; no threshold maps to one of them.

## Cross-checks, regression and reproducibility

Reaction rates are independently reconstructed from canonical reactants and author parameters and compared against frozen execution-model evaluation, with scaled discrepancy `|a-b|/max(1,|a|,|b|) <= 1e-8`. The assembled analytic Jacobian is checked by central differences using `h_j = 1e-4 max(1,|x_j|)` and scaled tolerance `1e-5`. Actual execution engines, maximum errors and results are in the manifest and numerical cross-check output; a comparison tolerance is numerical engineering evidence, not a kinetic acceptance criterion.

The global aminoacylation regression retains the historical qualitative checks: short stable relaxation modes, large GlyRS/MetRS complex occupancy and substantial free GlyAMP/MetAMP accumulation. Historical concentration maxima use all 200 points of the archived author trajectory; only its time-scale calculation subsamples 30 points and uses its own block/epsilon convention. This layer uses a distinct 200-point RoadRunner trajectory and card-specific blocks. The free GlyAMP/MetAMP maxima differ from the rounded historical values by about 0.197% and 0.0268%, respectively. The global quick reference explicitly compares these values and the named complexes' individual member/active-pool occupancy; no trajectory equivalence or forced numerical agreement is asserted.

Historical [A3a](aminoacylation_A3a_final_status.md) remains `FAILED_VALIDATION_ON_REFERENCE_DOMAIN` (free-substrate sliding ledger leak); [A3b](aminoacylation_A3bc_final_decision.md) records `FAILED_SMOKE_CLOSURE_FEASIBILITY` for the broad 21-state closure near 2.498 s and `BLOCKED_NUMERICAL_COORDINATE_DEFECT` for the restricted 9-state candidate whose full window did not complete. These are archived main-branch evidence with their own conditions, not new global-domain executions. They show why fast modes and small enzyme totals cannot certify free-coordinate QSSA.

Regenerate numerical artifacts with `python scripts/analyze_pnas2017_reduction_evidence.py`, then render the compact views with `python scripts/render_pnas2017_reduction_evidence_docs.py`. Use the generator's documented runtime options when the RoadRunner environment is separate. Run `python scripts/finalize_pnas2017_reduction_evidence.py --verify` to refresh the navigation/manifest and execute the recorded validation sequence. `python scripts/verify_pnas2017_reduction_evidence.py` independently checks coverage, provenance, exact pair/pool/classification consistency, numeric availability semantics and unchanged decisions. Its temporary-copy negative controls must reject missing/duplicate reactions, altered hashes/sources/author inputs/classifications/choices, wrong reverse partners, zero-flux ratios falsely set to zero, fabricated pools and preselected process boxes. Existing artifact, integration, annotation-v1/v2, reaction-contract and species-contract validators also remain required; exact commands/results belong in the manifest. No source file is mutated by a negative test. `python scripts/render_pnas2017_reduction_evidence_docs.py --check` verifies that the rendered summaries still match the CSVs without writing.

Status: REFERENCE ONLY — NO KINETIC REDUCTION APPROVED.
