# CHAIN_01 V2 resource-preserving staged-chain validation

Date: 2026-10-08 (Asia/Shanghai). Branch: `codex/pnas-topology-first`.
R1 local base-boundary comparison; R2 competition experiment remains pending.

Base numerical and independent analytic checks: **PASS**. The comparison preserves both the original coarse-grid unresolved attempt and the converged numerical successor.

## Sources, exact mapping and equations

Canonical SBML and author CSVs were reread and cross-checked, including all 968 topology reaction rows and all 241 net species coordinates. Placeholder SBML k1=1 was not used. Raw source SHA-256 is `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`.
Source time units are retained; no conversion to seconds is made. The old three-step A/X1/X2/B map to V2 S1/S2/S3/S4.
S4 is the ribosome-bound Pept0002 local extension state. It is a local production proxy, not free final Pept0003 or full PURE protein output.


| Alias | Exact SBML species ID | Chemical meaning |
| --- | --- | --- |
| S0 | `elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | EF-Tu.GTP loaded complex before hydrolysis |
| S1 | `elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC` | GDP/Pi bound after hydrolysis |
| S2 | `elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC` | Pi released; EF-Tu.GDP bound |
| S3 | `elRS70SAGGU0002_fMet_GlytRNAGlyGCC` | EF-Tu released before extension |
| S4 | `elRS70SBGGU0002_Pept0002tRNAGlyGCC` | Pept0002 formed; ribosome still bound |


| Source reaction | Author k | Products |
| --- | --- | --- |
| re0000000014 | 260 | elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC |
| re0000000016 | 1000 | PO4, elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC |
| re0000000017 | 7 | EFTu_GDP, elRS70SAGGU0002_fMet_GlytRNAGlyGCC |
| re0000000018 | 1000 | elRS70SBGGU0002_Pept0002tRNAGlyGCC |

Full: S0→S1→S2+Pi→S3+EF-Tu.GDP→S4, with rates 260,1000,7,1000.
Direct: S0→S4+Pi+EF-Tu.GDP, ke=1/tau.
Two-stage: S0→S2+Pi, then S2→S4+EF-Tu.GDP, with ka=1/(1/260+1/1000) and kb=1/(1/7+1/1000).
Three-stage: retain S0→S1 and S1→S2+Pi at source rates; S2→S4+EF-Tu.GDP uses kb.
For every model: z0′=u−J0, zi′=J(i−1)−Ji, S4′=Jlast, xi_i′=Ji with Ji=ki zi. Pi/GDP currents and extents are read from the designated release stages. All candidate columns equal their exact sums of source columns; all net differences are exactly zero.
When re21 is restored, subtract c*z0 from z0′ and add it independently to both exact source products and xi21. c=0.23; no sink or invented chemical product is used.


| Model | Chain reactions | Chemical states including S4 | Transient states | Extent counters | Mean wait | Variance |
| --- | --- | --- | --- | --- | --- | --- |
| Full | 4 | 5 | 4 | 4 | 0.148703297 | 0.0204249562 |
| Direct | 1 | 2 | 1 | 1 | 0.148703297 | 0.0221126705 |
| Two-stage | 2 | 3 | 2 | 2 | 0.148703297 | 0.0207183628 |
| Three-stage | 3 | 4 | 3 | 3 | 0.148703297 | 0.0207106705 |

Free Pi/GDP are read from extents. R2 adds two explicit source product amounts and one re21 extent to every model. The input and its integral are experiment-driver coordinates, not intrinsic reaction states. These accounting dimensions are not hidden in the reaction/state reduction claim.
All mean-dwell matches are approximate Markov candidates. Waiting variances differ; equal steady current or final cohort yield alone does not establish dynamic equivalence.

## Frozen experiments and budgets

Protocol SHA-256: `831c747c85b712de2bbb8360477f49cea4e15e6898d573205d3c7eb9c53d1960`. The R0 freeze predates all V2 trajectories and was pushed before R1 began.
Unit S0 pulse runs through 100tau; constant u=1 through 10000tau; u=exp(-t/T) at T/tau=20,100,1000 through ten supply-decay times. The V1 rectangular inputs and nonzero initial inventory [0,.25,.5,.25,0] are retained as prospectively excluded negative controls.
Required long-time windows are [5,10]tau and [10,end]tau. Early [0,10], V1 transient/post and long subwindows are all retained. Maxima are original registered sampled-grid values. Numerical midpoint refinements check convergence without changing scoring nodes. The first base attempt remains archived with native NUMERICALLY_UNRESOLVED sampling records; the successor meets the unchanged 1e-4 refinement-change budget.
Gate 2: product current and integrated formation extent each ≤1% of predeclared fixed scales. Gate 3: Pi/GDP current, extent, bound Pi/GDP, bound GTP precursor, total chain-bound Tu, unreleased phosphate equivalents and unfinished ribosome inventory each ≤1%. Amount scale is initial cohort 1 or u0*tau; current scale is cohort/tau or u0. Growing cumulative totals never set an acceptance denominator.
R2 additionally requires ≤1% relative error in both success and escape probabilities and in final cohort yield. The small escape pathway carries intact GTP-loaded carrier, so its allocation is checked separately.
Production integral means integral of formation current, equal to directed product extent. Window integrals and checkpoint cumulative-relative errors are saved separately.

## Numerical and independent verification


| Phase | Numerical | Independent | Max state/extent vs expm | Max current vs expm | Max fate residual | Max 70-digit checkpoint error |
| --- | --- | --- | --- | --- | --- | --- |
| base | PASS | PASS | 1.23631594e-09 | 4.73551154e-09 | 1.09093889e-09 | 9.24146093e-10 |

Primary Radau (1e-10,1e-12), tighter Radau (1e-12,1e-14), augmented dense expm and independent source-rebuilt exact rational Laplace residues at 70 digits are compared. Repeated rate-1000 poles are treated explicitly. All-grid currents and fate identities, required-window scores, exact candidate source-column sums, waiting-time resolvent moments and artifact hashes are checked.
No negative clipping, state projection or parameter fitting was used. 1737 preexisting tracked files retain their raw byte fingerprints. V1 remains LOCAL_CANDIDATE_FAILED_REGISTERED_SCREEN.

## Long-time product and resource scores

### base


| Model | Product | Ledger | Boundary | Worst product / fixed scale | Where | Worst resource / fixed scale | Where |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Full | PRODUCT_OUTPUT_SUPPORTED | RESOURCE_LEDGER_SUPPORTED | NOT_TESTED | 0 | C_slow_20/macro_10_end/product_extent | 0 | C_slow_20/macro_10_end/unfinished |
| Direct | PRODUCT_OUTPUT_SUPPORTED | NOT_SUPPORTED | NOT_TESTED | 0.00131981194 | C_slow_20/late_5_10/product_extent | 0.974135383 | B_constant/macro_10_end/bound_gtp |
| Two-stage | PRODUCT_OUTPUT_SUPPORTED | RESOURCE_LEDGER_SUPPORTED | NOT_TESTED | 0.000230521126 | C_slow_20/late_5_10/product_extent | 0.00672480048 | B_constant/macro_10_end/gdp_extent |
| Three-stage | PRODUCT_OUTPUT_SUPPORTED | RESOURCE_LEDGER_SUPPORTED | NOT_TESTED | 0.000224467716 | C_slow_20/late_5_10/product_extent | 0.00672480047 | B_constant/macro_10_end/gdp_extent |


| Test | Model | S4 extent | S4 current | Pi extent | Pi current | GDP extent | GDP current | Bound Pi | Bound GDP | Unfinished |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_pulse | Direct | 0.00101501497 | 0.000780814982 | 0.006737947 | 0.006737947 | 0.00105507549 | 0.000822514906 | 3.8969547e-85 | 0.0056828715 | 0.00101501497 |
| A_pulse | Two-stage | 0.000169016157 | 0.000133299796 | 7.77156117e-16 | 7.17385127e-66 | 0.000209076681 | 0.00017499972 | 3.8969547e-85 | 0.000209076681 | 0.000169016157 |
| A_pulse | Three-stage | 0.000167883179 | 0.000132128651 | 5.55111512e-16 | 6.97078221e-87 | 0.000207943704 | 0.000173828575 | 4.68771195e-89 | 0.000207943704 | 0.000167883179 |
| B_constant | Direct | 0.0012400076 | 0.001015015 | 0.967410582 | 0.00673794701 | 0.00672480048 | 0.00105507553 | 0.00672480047 | 0.967410582 | 0.0012400076 |
| B_constant | Two-stage | 0.000201993612 | 0.000169016174 | 1.07032982e-11 | 0 | 0.00672480048 | 0.000209076699 | 0.00672480047 | 0.000240479187 | 0.000201993612 |
| B_constant | Three-stage | 0.000200897547 | 0.000167883187 | 4.5871278e-12 | 0 | 0.00672480047 | 0.000207943711 | 0 | 0.00672480047 | 0.000200897547 |
| C_slow_20 | Direct | 0.00131981194 | 0.000998597288 | 0.787282429 | 0.0352876244 | 0.00626162827 | 0.000765060543 | 0.00524582551 | 0.786727955 | 0.00131981194 |
| C_slow_20 | Two-stage | 0.000230521126 | 0.000165462114 | 6.79513584e-06 | 3.39756791e-07 | 0.00554302616 | 0.000233913466 | 0.00524582551 | 0.00045411495 | 0.000230521138 |
| C_slow_20 | Three-stage | 0.000224467716 | 0.000164628592 | 2.23488092e-10 | 1.11741172e-11 | 0.00553703738 | 0.000233653874 | 7.51436794e-14 | 0.00553703738 | 0.000224467718 |
| C_slow_100 | Direct | 0.000884399743 | 0.00102385896 | 0.923023332 | 0.00881465283 | 0.006536591 | 0.000999693894 | 0.00639891334 | 0.923884086 | 0.000884399743 |
| C_slow_100 | Two-stage | 0.000139991682 | 0.000170416069 | 1.65559399e-06 | 1.65559402e-08 | 0.00636477429 | 0.000146251006 | 0.00639891334 | 0.000118001901 | 0.000139991682 |
| C_slow_100 | Three-stage | 0.000140556669 | 0.000169288722 | 9.99265176e-10 | 9.993395e-12 | 0.00636339118 | 0.000145123659 | 6.72037332e-14 | 0.00636339118 | 0.000140556669 |
| C_slow_1000 | Direct | 0.00120341835 | 0.0010162184 | 0.96074398 | 0.00578111096 | 0.00668964347 | 0.00104961949 | 0.00669147846 | 0.960968384 | 0.00120341835 |
| C_slow_1000 | Two-stage | 0.00019561215 | 0.000169211791 | 1.73078167e-07 | 1.73077663e-10 | 0.00667150501 | 0.000202612879 | 0.00669147846 | 0.000227828179 | 0.00019561215 |
| C_slow_1000 | Three-stage | 0.000194688301 | 0.000168077911 | 9.61853804e-09 | 9.62113722e-12 | 0.00667135246 | 0.000201479 | 6.47003535e-14 | 0.00667135246 | 0.000194688301 |

## Stable input: persistent absolute offsets

For base constant input, each stage current tends to u; each transient stage tends to u/k. S4 continues to increase. The eventual current equality follows for any completing irreversible chain and is not a parameter validation. xi_R=u(t-d_R)+o(1), where d_R is the mean delay through the resource-release stage.


| Model | Analytic S4 offset | Analytic Pi offset | Analytic GDP offset | Pi offset at 10000tau | Pi / fixed scale | Pi cumulative-relative | Bound GDP offset |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Full | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Direct | 0 | -0.143857143 | -0.001 | -0.143857143 | -0.967410582 | 9.67413735e-05 | -0.143857143 |
| Two-stage | 0 | 0 | -0.001 | 1.59161573e-12 | 1.07032982e-11 | 1.07033331e-15 | 0 |
| Three-stage | 0 | 0 | -0.001 | 6.82121026e-13 | 4.5871278e-12 | 4.58714275e-16 | 0.001 |

Direct has a persistent Pi deficit despite a shrinking cumulative percentage. Two-stage preserves the mean Pi-release delay but reallocates bound Pi to a longer GTP precursor residence. Three-stage preserves hydrolysis and Pi release exactly in these local tests; combining EF-Tu departure with extension delays free GDP and adds bound GDP by approximately u/1000. Both coarse multi-stage models have a nonzero free-GDP deficit; it is measured against the fixed resource scale.

## Applicability and failure mechanisms


| Control | Model | Prospective domain | Early product-current error | Early Pi-current error | Final GDP extent difference | Initial ledger projection difference |
| --- | --- | --- | --- | --- | --- | --- |
| D_fast | Direct | FAST_INPUT_NEGATIVE_CONTROL | 0.034198582 | 0.87700577 | 1.11022302e-16 | {'bound_pi': 0.0, 'bound_gdp': 0.0, 'bound_gtp': 0.0, 'tu_bound': 0.0, 'phosphate_unreleased': 0.0, 'unfinished': 0.0} |
| D_fast | Two-stage | FAST_INPUT_NEGATIVE_CONTROL | 0.00718873151 | 0.10284909 | -2.77555756e-16 | {'bound_pi': 0.0, 'bound_gdp': 0.0, 'bound_gtp': 0.0, 'tu_bound': 0.0, 'phosphate_unreleased': 0.0, 'unfinished': 0.0} |
| D_fast | Three-stage | FAST_INPUT_NEGATIVE_CONTROL | 0.0059727783 | 4.28117097e-10 | 4.4408921e-16 | {'bound_pi': 0.0, 'bound_gdp': 0.0, 'bound_gtp': 0.0, 'tu_bound': 0.0, 'phosphate_unreleased': 0.0, 'unfinished': 0.0} |
| D_inventory | Direct | OUT_OF_DOMAIN_INITIAL_COMPOSITION | 36.1758242 | 36.1758242 | 0.25 | {'bound_pi': -0.25, 'bound_gdp': -0.75, 'bound_gtp': 1.0, 'tu_bound': 0.25, 'phosphate_unreleased': 0.75, 'unfinished': 0.0} |
| D_inventory | Two-stage | OUT_OF_DOMAIN_INITIAL_COMPOSITION | 36.4005587 | 29.5046224 | 0.25 | {'bound_pi': -0.25, 'bound_gdp': 0.0, 'bound_gtp': 0.25, 'tu_bound': 0.25, 'phosphate_unreleased': 0.0, 'unfinished': 0.0} |
| D_inventory | Three-stage | OUT_OF_DOMAIN_INITIAL_COMPOSITION | 36.4005587 | 5.72153382e-10 | 0.25 | {'bound_pi': 0.0, 'bound_gdp': 0.25, 'bound_gtp': 0.0, 'tu_bound': 0.25, 'phosphate_unreleased': 0.0, 'unfinished': 0.0} |

Fast rectangular inputs remain negative controls even when some late measures pass. Arbitrary initial internal mixtures cannot be reconstructed from the retained coordinates. In the initial-inventory control, Three-stage adds 0.25 bound GDP equivalents by assigning initially Tu-free S3 to a GDP-bound reservoir; the subsequent free-GDP extent differs by 0.25. This excludes a general nonzero-internal-inventory claim.
Supported input evidence is confined to the declared pulse late windows, steady supply, and the three tested slow supply ratios. All source rates and internal zero side paths are fixed. There is no full ATP/GTP shared-pool concentration validation or demonstration of safe arbitrary upstream/downstream coupling.

## Reproduction, files and delivery

Commands actually used: `python scripts/reduction/prepare_chain01_v2.py`; `python scripts/tests/test_chain01_v2.py`; `python scripts/reduction/validate_chain01_v2.py`; `python scripts/tests/verify_chain01_v2.py`.
Each completed round runs diff checks, commit, explicit push and live `git ls-remote` confirmation. Exact payload SHA receipts and verification times are in [git_delivery_manifest.json](../../results/reduction/chain01_v2/git_delivery_manifest.json). The receipt is committed subsequently to avoid a circular self hash.

- [Frozen protocol](../../configs/reduction/chain01_v2_validation.json)
- [Source manifest](../../results/reduction/chain01_v2/source_manifest.json)
- [Exact mathematics](../../results/reduction/chain01_v2/mathematical_certificate.json)
- [Base summary](../../results/reduction/chain01_v2/base/attempt_002/validation_summary.json)
- [Base independent checks](../../results/reduction/chain01_v2/base/attempt_002/independent_verification.json)

Raw compressed CSVs include primary, tighter and expm states/extents, currents, both input limits, fate residuals and original scoring-grid membership. Error CSVs include signed, fixed-scale and relative errors without denominator clipping. Every phase has the nine requested PNG figures and a data-source map. Numerical attempts, frozen fingerprints, independent verification and derived provenance navigation are subordinate to the canonical sources and original arrays.

### Figure index

- [01_product_trajectory_comparison](../../results/reduction/chain01_v2/figures/base/attempt_002_axis_qa/01_product_trajectory_comparison.png)
- [02_product_flux_comparison](../../results/reduction/chain01_v2/figures/base/attempt_002_axis_qa/02_product_flux_comparison.png)
- [03_pi_release_comparison](../../results/reduction/chain01_v2/figures/base/attempt_002_axis_qa/03_pi_release_comparison.png)
- [04_eftu_gdp_release_comparison](../../results/reduction/chain01_v2/figures/base/attempt_002_axis_qa/04_eftu_gdp_release_comparison.png)
- [05_internal_occupancy_comparison](../../results/reduction/chain01_v2/figures/base/attempt_002_axis_qa/05_internal_occupancy_comparison.png)
- [06_long_time_output_comparison](../../results/reduction/chain01_v2/figures/base/attempt_002_axis_qa/06_long_time_output_comparison.png)
- [07_slow_input_response](../../results/reduction/chain01_v2/figures/base/attempt_002_axis_qa/07_slow_input_response.png)
- [08_resource_ledger_error](../../results/reduction/chain01_v2/figures/base/attempt_002_axis_qa/08_resource_ledger_error.png)
- [09_complexity_accuracy_tradeoff](../../results/reduction/chain01_v2/figures/base/attempt_002_axis_qa/09_complexity_accuracy_tradeoff.png)