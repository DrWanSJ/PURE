# Independent energy-cycle checks — v1

Status: `INDEPENDENT_ENGINEERING_CHECKS_PASS_NOT_SCIENTIFIC_ACCEPTANCE`.

The source tests executed after the numerical preregistration was frozen at SHA-256 `fee6ae44f33d28a98ada5949e72d97ccf61f17e7111d47e22ad071ccc6ccfa5b`. All 12 required adversarial controls triggered the intended semantic failure. No mutation was rejected only by a hash comparison. Mutations were applied in memory; canonical sources and historical evidence were untouched.

Reproduce from the research worktree with:

```powershell
python scripts/energy_cycles/independent_tests.py
python scripts/energy_cycles/numerical_verify.py
```

Machine-readable evidence is in `results/energy_cycles_v1/independent_tests.json` and `results/energy_cycles_v1/numerical_verification.json`. These outputs record source hashes, source commit, commands, environment, exact witnesses, failure gates, and trajectory hashes. The independent parsers import neither `source.py` nor `runtime.py` nor `kinetics_analysis.py`. Source laws and exact rational stoichiometry are parsed directly from canonical XML MathML; author inputs come directly from the immutable simulator ZIP; subsystem provenance is recomputed from ZIP reaction signatures and checked against extracted subsystem XML and historical reaction inventories.

## Independently reproduced source and structural findings

The combined source contains 241 species and 968 reactions. The author input ZIP has 27 positive initial species and 483 nonzero directed parameters. The four source subsystems contain 87 reactions and 61 author-active channels. The unchanged structural XML has all-one initial concentrations and all-one local constants. Original and normalized compatibility XML have identical species metadata, reaction IDs, exact stoichiometry and kinetic expressions; `re0000000414` produces exactly two `PO4`.

| Unit | Original / active | Principal family / degradation | Active rank | Internal rank | Boundary projection rank | Physically supported signs |
| --- | --- | --- | --- | --- | --- | --- |
| CK | 25 / 18 | RFAM_015:18 / RFAM_DEG:7 | 7 | 6 | 1 | Forward and reverse |
| NDK | 25 / 17 | RFAM_016:18 / RFAM_DEG:7 | 7 | 6 | 1 | Forward; reverse infeasible with author-zero `re0000000364` |
| MK | 25 / 18 | RFAM_017:18 / RFAM_DEG:7 | 7 | 6 | 1 | Forward and reverse |
| PPiase | 12 / 8 | RFAM_018:8 / RFAM_DEG:4 | 4 | 3 | 1 | Forward and reverse, including both PO4 releases |

The exact kernel projection and enumeration of nonnegative simple enzyme-state cycles give the same one-dimensional boundary span. Separate linear programs provide feasible directed-flux witnesses for supported signs and reject NDK reverse operation. The PPiase author reference supports the complete reverse catalytic cycle: conceptual `PPi -> 2 PO4` does not justify suppressing its active reverse chemistry.

Complete enzyme pools and source-represented adenylate, guanylate, creatine and phosphate-group pools were proved from exact active stoichiometry where present. Form-specific bound composition was derived separately from binding/release stoichiometry and checked against CellDesigner membership. This independently recovers multiplicity two for `MK_ADP_ADP` and `PPiase_PO4_PO4`, although the diagram's included-species lists contain each resource name once.

All disabled degradation events destroy the active catalyst pool if enabled. MK `re0000000400` and `re0000000401` additionally lose one represented adenylate each; their phosphate-group residuals are respectively -1 and -2. These conditional source defects remain explicit and were not repaired. The conserved groups are representation-specific; complete elemental or ionic conservation is not claimed.

## Required adversarial controls

| No. | Deliberate mutation | Caught by |
| --- | --- | --- |
| 1 | Remove active CK `re0000000330` | Source reaction coverage |
| 2 | Reverse CK catalytic `re0000000338`, retaining its source mapping | Directed source stoichiometry |
| 3 | Double an ADP binding coefficient | Nonzero exact adenylate-pool residual |
| 4 | Enable NDK reverse chemical `re0000000364` | Author directed-parameter mismatch |
| 5 | Omit CK_CP_ADP's bound nucleotide | Exact conserved-pool residual across binding/conversion channels |
| 6 | Omit terminal PPiase PO4 release | Loss of a forward catalyst-regenerating cycle |
| 7 | Replace `PPi -> 2 PO4` with `PPi -> PO4` | Represented phosphate-group imbalance |
| 8 | All-one initial inputs with author parameters | Author initial-value mismatch in 241 species |
| 9 | Change the actual CK catalytic family membership to RFAM_016 | Source family-membership mismatch |
| 10 | Add independent `A -> C` to synthetic `A -> B` | Exact boundary rank becomes two |
| 11 | Declare canonical CK free-enzyme initial state on the fast manifold | Nonzero source enzyme-stationarity RHS versus frozen closure allowance |
| 12 | Exact protein endpoint agreement with 3% cumulative resource error | Frozen 2% resource gate rejects the candidate |

Controls 1–9 use source-derived chemistry or operational inputs. Control 11 uses a canonical CK state with enzyme total one and positive free resources; its enzyme RHS is recomputed from source laws. Controls 10 and 12 are explicitly synthetic mathematical/policy tests, and do not stand for full-PNAS simulations. Control 12 reads all acceptance thresholds from the frozen registration and requires every relevant observable.

## Mathematical fixtures and independent kinetic checks

A parallel equal-rate first-order fixture has zero exact lumpability residual. A parallel unequal-rate fixture has the same retained sum but different projected derivatives, proving non-lumpability. An analytically solved chemostatted `E + S <-> ES -> E + P` fixture gives `v=E_total*kcat*S/(S+(koff+kcat)/kon)`, a unique positive stationary complex, and a negative relaxation eigenvalue. An independent Radau trajectory agrees with its exact initial-layer solution to `1.34e-13` maximum absolute error.

For every PNAS energy unit, independently constructed pairs of microscopic states with identical free resources and enzyme total have unequal projected derivatives. Pairs with identical form-specific free-plus-bound totals and enzyme total also have unequal projected derivatives. Thus neither coordinate choice defines an exact source reduction. The fixed-free occupancies and currents reported by the explicit candidate formulas were verified against independently assembled canonical enzyme generators and source RHS.

The substrate-positive/product-total-zero corner is independently incompatible with stationary total closure for every unit. Nonnegative accounting forces product-bound states to zero, while the source-directed enzyme graph at positive free substrates is irreducible and requires strictly positive stationary occupancy. Exact linear stationarity with the required zero occupancies returns `EmptySet`. This proves a closure-domain limitation while leaving the corresponding microscopic initial state physically meaningful.

## Independent numerical recomputation

All 84 completed microscopic/reduced trajectory pairs were independently verified. The verifier re-derived the total, bound and net mappings from canonical chemistry rather than trusting the saved mappings, recomputed source reaction fluxes and catalytic forward/reverse currents, and checked every initial-layer, transition and long-window metric. It also recomputed tightened-Radau/BDF numerical uncertainty, the complete conserved groups, source resource/extent identities integrated from t=0, unclipped minimum inventories, reconstructed enzyme stationarity and the frozen scientific-gate classification.

The largest discrepancy from a reported metric was `1.39e-17`. The maximum absolute source resource/extent identity residual was `1.48e-9`; the largest normalized drift in an independently proved conserved group was `5.15e-11`. All 84 emitted comparisons agree with their recorded `SCENARIO_GATES_PASS` classifications: CK 26, NDK 12, MK 24, PPiase 22. Those scenario-level passes do not establish robustness over the entire registered domain.

Stopped attempts remain separate evidence. The four zero-product corners have an independent mathematical no-root proof. MK low fuel stopped with a reconstructed negative free inventory, so its selected physical root was not certified. Seven NDK positive-challenge variants stopped when a solver evaluation requested a negative retained inventory. An implicit solver's internal trial state can leave a physical domain; those stops alone do not prove an inaccurate completed trajectory or globally nonexistent closure. No stopped case was discarded, retuned, or promoted to acceptance. Full-model candidate validation remains a separate, unmet scientific requirement.

## Independent source-reference and engine import checks

`source_reference_verify.py` independently checks the full author overlay and both 87-channel source-coupling conditions. All 968 original source stoichiometries and kinetic expressions remain identical, all 241 operational initial inputs agree, and source metadata apart from the deliberate initial overlay remains unchanged. Full author parameters agree in all 968 channels. In isolated four-cycle source executions, the 881 external channels are exactly disabled in the results-only overlay. Shared free resources are counted once and catalyst pools do not overlap. Source resource mappings, net directions, bound storage, cumulative net extents and all saved energy reaction rates agree with independent canonical calculations.

The source full-network tight free-Pept0003 endpoint is `5.164491294743647`; its base/tight absolute endpoint difference is `3.65327812401528e-9`. These are source-reference diagnostics, not a candidate endpoint gate. A freshly assembled canonical enzyme generator and a separate finite-difference stationary-total root solver reproduce every failed source-history audit time: 13 MK samples and 36 PPiase samples, with zero CK/NDK failures among 362 observations per unit. This corroborates the selected-branch startup obstacle without proving every possible closure globally invalid.

`verify_imported_matrix.py`, executed in the existing RoadRunner environment, directly compared complete imported 241-by-968 stoichiometric matrices against a separate stdlib MathML parser. The normalized compatibility file and full author overlay match exactly. Raw canonical import has precisely one different entry: `re0000000414`/`PO4`, source coefficient two versus imported coefficient one. This independently corroborates the engine-import integrity claim and records the raw-import limitation in `source_reference_import_verification.json`.

## Additive NDK coordinate verification

`ndk_coordinate_verify.py` independently proves the exact depletion-coordinate transformation from source stationarity rows. Both ATP-limiting and GDP-limiting cases have zero symbolic residual for `J = T_lim * hazard` and for the free-plus-bound inventory factorization. The hazard remains finite at zero limiting inventory. The transformation `R=L0*exp(-q)`, `extent=L0*(1-exp(-q))`, `dq/dt=hazard` has zero exact derivative residual and preserves source chemistry at author-zero reverse conversion. It changes numerical coordinates without refitting constants or changing the registered scientific scenarios, gates, scales, grid or tolerances.

The first additive runner retained one complete original-mode trajectory before its reporting-key typo interrupted the remaining work. That duplicate is independently verified in `ndk_coordinate_v1_verification.json`; it is retained with the reporting failure and contributes no additional unique scientific comparison. Corrected v2 evidence is separately frozen and stored under `numerical_ndk_coordinate_v2`; its independent numerical result is recorded separately from the original 84-pair verification.

All 14 corrected NDK comparisons passed independent canonical metric, uncertainty, ledger, stationarity and frozen-gate recomputation in `ndk_coordinate_v2_verification.json`. Their reported metrics agree exactly with recomputation; the largest absolute source resource/extent balance defect is `3.75e-7`, consistent with the separately reported direct-quadrature/coordinate numerical difference. The core v1 dataset therefore contains 98 unique completed comparisons: CK 26, NDK 26, MK 24, PPiase 22, plus five initial-domain stops affecting both modes. The original 84-pair result, seven original solver failures, first additive reporting failure and one duplicate trajectory all remain available. The earlier `ndk_coordinate_verification.json` is the preserved symbolic-only pre-run checkpoint; the explicitly named v2 file carries final numerical evidence.

The final v2 verification command is:

```powershell
python scripts/energy_cycles/ndk_coordinate_verify.py --numerical-dir results/energy_cycles_v1/numerical_ndk_coordinate_v2 --output results/energy_cycles_v1/ndk_coordinate_v2_verification.json --addendum docs/reduction/energy_cycles/ndk_numerical_repair_preregistration_v2.json
```

## Separate supplemental reverse-driving probe

A separately frozen PPiase source-direction probe uses PPi 1, PO4 10000 and catalyst total 0.16. This adds two held-out comparisons and does not modify, rescore or replace the 54 original v1 conditions. Both original-nonequilibrium and projected modes independently pass their own registered long-window gates in `supplemental_ppiase_reverse_verification.json`. Canonical source-law recomputation confirms net catalytic extent approximately `-5.63020572874` by the source-forward convention in both microscopic and candidate trajectories, demonstrating net PPi synthesis. The reconstructed initial net current is `-1.80727862778`; the entirely free original enzyme has zero catalytic current at t=0 and then develops occupancy. This source-supported reverse result gives no scientific approval or full-model validation.

```powershell
python scripts/energy_cycles/numerical_verify.py --registration docs/reduction/energy_cycles/ppiase_reverse_probe_preregistration.json --numerical-dir results/energy_cycles_v1/supplemental_ppiase_reverse/numerical --output results/energy_cycles_v1/supplemental_ppiase_reverse_verification.json
```
