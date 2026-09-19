# Model Card — PURE_literature_reference

## 1. Identity

- Model ID: PURE_literature_reference
- Version: 1.0-b1-benchmark
- Role: B1 literature benchmark only
- Source: Mavelli, F.; Marangoni, R.; Stano, P. (2015), A Simple Protein Synthesis Model for the PURE System Operation, Bulletin of Mathematical Biology 77:1185–1212
- DOI: https://doi.org/10.1007/s11538-015-0082-8
- Relation to source: literal deterministic translation; no refitting and no added mechanism
- Canonical machine-readable definition: models/literature_reference/model_definition.json
- Parameter source: models/literature_reference/parameters.json
- Species ledger: models/literature_reference/species.csv
- Reaction ledger: models/literature_reference/reactions.csv

This model is deliberately separated from PURE_resource_core. ATP/GTP splitting, explicit AMP/ADP chemistry, mechanistic ribosome states, Mg2+ chemistry, maturation, transport, or other project-specific extensions belong to the working model, not this benchmark.

## 2. Scientific purpose

The model reconstructs the coarse-grained deterministic PURE transcription–translation model of Mavelli et al. It represents four effective modules: transcription (TX), aminoacyl-tRNA charging (RS), translation (TL), and energy regeneration (EN), plus first-order loss of polymerized RNA residues and effective translation machinery.

The benchmark is intended to test faithful model transcription, numerical integration, observable mapping, mass-balance bookkeeping, and reproducibility. It is not a mechanistically complete model of PURE chemistry.

## 3. Evidence and validation status

| Evidence item | Current status |
| --- | --- |
| Bibliographic identity | verified |
| Equations transcribed into repository | complete |
| Equation-level automated tests | passed |
| Numerical solver QC | passed |
| Paper text-anchor comparison | passed |
| Fig. 4 simulation-assisted raster comparison | available, non-independent |
| Independent human Fig. 4 audit | pending |
| Machine-readable Stögbauer 2012 experimental data | unavailable in repository |
| Experimental/B2 predictive validation | not established |

Passing repository tests does not replace independent scientific review. This remains a literature reconstruction.

## 4. Boundary conditions and units

- System mode: batch
- Volume: fixed
- Mixing: well mixed
- Spatial gradients: absent
- Membrane exchange: absent
- External feed/dilution: absent
- Time unit: s
- Concentration unit: µM
- Reaction-rate unit: µM/s
- Temperature, pH, and free Mg2+: not explicit model variables; quantitative dependence is not represented

The model is concentration-based. No explicit compartment volume is needed by the B1 RHS because volume is fixed.

## 5. Dynamic states

The canonical paper RHS contains 10 physical ODE states.

| index | state | meaning | initial value | feeds back into rates? |
| ---: | --- | --- | ---: | :---: |
| 1 | NTP | average NTP concentration per nucleotide species | 1500 µM | yes |
| 2 | NXP | overall exhausted-nucleotide pool (NDP + NMP lumped) | 0 µM | yes |
| 3 | nt | polymerized nucleotide residues; mRNA in residue units | 0 µM | yes |
| 4 | A | average free amino-acid concentration per species | 300 µM | yes |
| 5 | T | average uncharged tRNA concentration per species | 1.9 µM | yes |
| 6 | AT | average aminoacyl-tRNA concentration per tRNA species | 0 µM | yes |
| 7 | a | polymerized amino-acid residues; protein in residue units | 0 µM | no |
| 8 | CP | creatine phosphate | 20000 µM | yes |
| 9 | C | creatine | 0 µM | no |
| 10 | TLcat | effective translation machinery (ribosome + factors lumped) | 2.2 µM | yes |

a and C are terminal product accumulators in this reference model: they are produced but do not appear in any rate law. They remain useful for observables and conservation bookkeeping.

## 6. Fixed inputs

| input | meaning | value |
| --- | --- | ---: |
| DNA | DNA template/promoter concentration | per run: 0.00034, 0.0017, or 0.0068 µM for Fig. 4 |
| TXcat | T7 RNA polymerase | 0.1 µM |
| RScat | average effective aminoacyl-tRNA synthetase concentration | 0.16 µM |
| ENcat | effective energy-regeneration catalyst | 0.08 µM |

These variables affect reaction rates but are not integrated as dynamic states.

## 7. Accounting-only integrators

The simulator additionally integrates two non-feedback bookkeeping variables:

- D_nt, with dD_nt/dt = V_nt_deg, records cumulative unresolved products of nt degradation needed to reconstruct paper Eq. (15).
- D_TLcat, with dD_TLcat/dt = V_TL_deg, records cumulative unresolved loss products of TLcat needed to reconstruct paper Eq. (19).

They are not additional biochemical mechanisms and are not part of the canonical 10-state paper RHS.

## 8. Multiplicity definitions

The paper uses average concentrations for pooled molecular classes:

- n_NTP = 4
- n_A = 20
- n_T = 46
- n_T / n_A = 2.3

NTP, A, T, and AT therefore require multiplicity factors when constructing mass balances and state equations.

## 9. Reactions and rate laws

### R_TX — transcription

Paper reaction:

$$
NTP \xrightarrow{TXcat, DNA} nt + PP_i
$$

Rate:

$$
V_{TX}=k_{TX}C_{TXcat}\frac{[DNA]}{K_{TX,DNA}+[DNA]}\frac{[NTP]}{K_{TX,NTP}+[NTP]}.
$$

PPi is produced by the source reaction but is not a state in the B1 RHS.

### R_nt_deg — polymerized-RNA degradation

$$
nt \rightarrow degradation\ products
$$

$$
V_{nt,deg}=k_{nt,deg}[nt].
$$

The chemical identity of the degradation products is unresolved.

### R_RS — aminoacylation

$$
A+T+NTP \xrightarrow{RScat} AT+NXP
$$

$$
V_{RS}=k_{RS}C_{RScat}
\frac{[A]}{K_{RS,A}+[A]}
\frac{2.3[T]}{K_{RS,T}+2.3[T]}
\frac{[NTP]}{K_{RS,NTP}+[NTP]}.
$$

This is a coarse-grained B1 reaction. The mechanistic ATP → AMP + PPi chemistry is not explicit.

### R_TL — translation

$$
AT+2NTP \xrightarrow{TLcat, nt} a+T+2NXP
$$

$$
V_{TL}=k_{TL}[TLcat]
\frac{[nt]}{K_{TL,nt}+[nt]}
\frac{2.3[AT]}{K_{TL,AT}+2.3[AT]}
\frac{[NTP]}{K_{TL,NTP}+[NTP]}.
$$

The factor 2 is a stoichiometric consumption factor. The source intentionally retains one rectangular-hyperbolic NTP factor in the rate law rather than an [NTP]^2 term.

### R_TL_deg — translation-machinery loss

$$
TLcat \rightarrow degradation\ products
$$

$$
V_{TL,deg}=k_{TL,deg}[TLcat].
$$

The molecular loss mechanism is not resolved.

### R_EN — energy regeneration

$$
CP+NXP \xrightarrow{ENcat} C+NTP
$$

$$
V_{EN}=k_{EN}C_{ENcat}
\frac{[CP]}{K_{EN,CP}+[CP]}
\frac{[NXP]}{K_{EN,NXP}+[NXP]}.
$$

Individual regeneration enzymes and nucleotide-specific steps are pooled.

### Context-only PPi hydrolysis

The source also gives:

$$
PP_i \xrightarrow{PPase} 2P_i.
$$

It is not integrated as a seventh kinetic rate because the source assumes this process is fast and because PPi/Pi do not feed back into the remaining B1 rate laws. It remains in the reaction ledger as chemical context.

## 10. Canonical ODEs

$$
\frac{d[NTP]}{dt}=\frac{-V_{TX}-2V_{TL}-V_{RS}+V_{EN}}{n_{NTP}},
$$

$$
\frac{d[NXP]}{dt}=2V_{TL}+V_{RS}-V_{EN},
$$

$$
\frac{d[nt]}{dt}=V_{TX}-V_{nt,deg},
$$

$$
\frac{d[A]}{dt}=-\frac{V_{RS}}{n_A},
$$

$$
\frac{d[T]}{dt}=\frac{-V_{RS}+V_{TL}}{n_T},
\qquad
\frac{d[AT]}{dt}=\frac{V_{RS}-V_{TL}}{n_T},
$$

$$
\frac{d[a]}{dt}=V_{TL},
$$

$$
\frac{d[CP]}{dt}=-V_{EN},
\qquad
\frac{d[C]}{dt}=V_{EN},
$$

$$
\frac{d[TLcat]}{dt}=-V_{TL,deg}.
$$

The executable numerical source of truth is model_definition.json; this Markdown is explanatory and must not become a second numerical source of truth.

## 11. Observables

For GFP the source uses protein length L = 238 amino acids.

| observable | mapping |
| --- | --- |
| polymerized nucleotide residues | nt |
| polymerized amino-acid residues | a |
| mRNA molecule concentration | mRNA = nt/(3L) |
| protein molecule concentration | protein = a/L |

Thus:

$$
[mRNA]=\frac{[nt]}{714},
\qquad
[protein]=\frac{[a]}{238}.
$$

K_TL_RNA = K_TL_nt/(3L) = 226/714 ≈ 0.3165 µM is a derived QC quantity, not an independent RHS parameter.

## 12. Conservation and bookkeeping relations

The reference implementation tracks five published balance relations:

$$
B_{NTP}=4[NTP]+[nt]+[NXP]+D_{nt}=constant,
$$

$$
B_{AA}=20[A]+[a]+46[AT]=constant,
$$

$$
B_{tRNA}=46[T]+46[AT]=constant,
$$

$$
B_{CP}=[CP]+[C]=constant,
$$

$$
B_{TLcat}=[TLcat]+D_{TLcat}=constant.
$$

These are model-resolution balances. They are not a complete elemental, charge, or thermodynamic balance of the real PURE mixture.

## 13. Main coarse-graining assumptions

1. ATP, GTP, CTP, and UTP are pooled into one average NTP state.
2. NMP and NDP products are pooled into one NXP state.
3. Twenty amino acids are represented by one average A state.
4. Forty-six tRNA species are represented by average T and AT states.
5. Twenty aminoacyl-tRNA synthetases are represented by RScat.
6. Ribosome and translation factors are represented by TLcat.
7. The energy-regeneration machinery is represented by ENcat.
8. Enzyme stages use effective Michaelis-Menten forms; pre-stationary dynamics are neglected.
9. PPi hydrolysis is not dynamically integrated.
10. GFP maturation is omitted in the source benchmark.
11. No product inhibition by a or C is included.
12. No explicit ATP/ADP/AMP or GTP/GDP bookkeeping exists in B1.

## 14. Known limitations and validity boundaries

A new model derivation is required for questions that depend on:

- nucleotide-specific ATP/GTP/CTP/UTP dynamics,
- explicit ATP → AMP + PPi aminoacylation chemistry,
- adenylate energy charge,
- explicit ribosome occupancy or polysome states,
- amino-acid or codon-specific limitations,
- Mg2+, pH, ionic-strength, or temperature dependence,
- explicit protein maturation/folding,
- membrane transport, changing volume, or spatial gradients,
- open/continuous-feed stationary states,
- intrinsic stochastic dynamics or SSA propensities derived directly from effective MM rate laws,
- thermodynamically complete free-energy accounting.

The source model was designed for macroscopic deterministic conditions where intrinsic stochastic effects are negligible. Effective MM rate laws must not automatically be reinterpreted as microscopic stochastic propensities.

## 15. Relationship to PURE_resource_core

PURE_literature_reference is frozen for B1 reproduction.

PURE_resource_core is the project working model. Candidate changes such as explicit ATP/ADP/AMP and GTP/GDP states, PPi/Pi bookkeeping, sequence-length resource costs, free/occupied ribosome pools, explicit regeneration chemistry, or experimentally supported failure mechanisms belong there.

Parameters fitted for B1 state definitions do not automatically transfer to altered state definitions in PURE_resource_core.

## 16. Repository execution chain

The current single-source chain is:

models/literature_reference/model_definition.json
→ matlab/codegen/generate_pure_literature_reference.m
→ matlab/generated/rhs_pure_literature_reference.m
→ matlab/src/simulate/simulate_pure_literature_reference.m
→ benchmark/results/QC.

The generated RHS must not be hand-edited.

A frozen baseline snapshot exists only for regression testing:

matlab/tests/fixtures/rhs_pure_literature_reference_baseline_snapshot.m

## 17. Reproducibility and provenance

Relevant repository files:

- models/literature_reference/model_definition.json
- models/literature_reference/model_manifest.json
- models/literature_reference/parameters.json
- models/literature_reference/species.csv
- models/literature_reference/reactions.csv
- matlab/generated/rhs_pure_literature_reference.m
- matlab/src/simulate/simulate_pure_literature_reference.m
- matlab/tests/test_pure_literature_reference.m
- docs/project/benchmark_registry.md
- docs/audit/audit_status.md
- environment_lock.md

Any change to the canonical definition or parameter values changes the benchmark identity and must be reviewed as a new model version rather than silently modifying the frozen B1 reference.
