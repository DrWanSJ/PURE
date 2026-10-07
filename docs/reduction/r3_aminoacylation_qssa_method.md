# R3 selective GlyRS/MetRS QSSA pilot: preregistered method v1

Status: **METHOD AND GRID REGISTERED BEFORE NEW R3 FULL-COUPLED COMPARISON;
PILOT NOT YET VALIDATED.** This is an approximation experiment, distinct from
the exact R1/R2 results. The historical 2026-09-26 aminoacylation v1r2
formal run failed coupled state, process flux, cumulative extent, and tRNA
and phosphate conservation gates; its failed evidence is retained. Its
21-complex partition is a candidate to re-evaluate from canonical source,
not an accepted R3 outcome.

## Frozen source and candidate selection

- Canonical SBML: `models/pnas2017_full_reference/original/fMGG_synthesis.xml`,
  SHA-256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`.
  Original author parameter and initial-value CSVs remain fixed. There is
  no kinetic-parameter fit.
- Use the verified R1 SOURCE_GENERAL 241-to-214 affine chart as the exact
  base and recompute `b=L*x0` for every grid condition. R2 frozen-only laws
  cannot select generic coordinates or remove a state/reaction. Both source
  directed rates and gross extents remain available.
- Re-audit the canonical GlyRS and MetRS enzyme-bound reaction rows, their
  stoichiometric columns, and the exact source-general GlyRS/MetRS pool laws
  before selecting the fast set. Free `GlyAMP` and `MetAMP` remain dynamic.
  Do not make all Class-II-A states algebraic. Preserve ATP/ADP/AMP,
  Pi/PPi, Gly/Met, charged and uncharged tRNA, formylation, peptide progress,
  and translation/resource kinetics outside the selected closure.
- Candidate standard QSSA uses the selected complex concentrations `q` and
  author-derived `G(s,q)=f_q(s,q)=0`. Candidate total QSSA uses exact moiety
  totals as slow coordinates, reconstructs the relevant free carriers and
  the selected complexes, and solves the same source-derived fast balance
  on the physical branch. Both candidates must be evaluated; neither is
  assumed valid from reaction topology or rate constants alone.
- For the standard realization, do not integrate a free conserved carrier
  while setting its bound fast rows to zero: the prior v1r2 run measured
  artificial tRNA and phosphate ledger drift from that choice. Reconstruct
  or explicitly integrate the exact SOURCE_GENERAL enzyme and tRNA moiety
  totals and demonstrate balance in the coupled system. The v0 phosphate
  law containing PPi/PO4 is FROZEN_REFERENCE_ONLY, so retain their source
  dynamics and directed phosphate accounting instead of treating that law
  as a generic conserved total.

## Closure, timescale, and numerical policy

For each candidate, find nonnegative roots of `G=0`, require maximum scaled
closure residual `<=1e-10`, and document multistart branch/uniqueness and
failure regions. Do not clip a negative root or state. If using a Jacobian,
differentiate the closure through `dh/ds=-G_q^{-1}G_s`, including the
reconstruction map, instead of deleting full-system Jacobian rows. Report
fast eigenmodes, a defined slow relaxation timescale, and
`epsilon=tau_fast/tau_slow` over the actual coupled trajectory. `epsilon<=0.01`
is a screen, not proof of QSSA validity. Record enzyme occupancy and
substrate-to-enzyme ratios to distinguish standard and total QSSA regimes.

## Preregistered full-coupled comparison

`r3_validation_grid_v1.csv` fixes ten initial-condition cases before any new
R3 decisive comparison. Only listed initial values are scaled; parameters,
reaction laws, and all other initial values are unchanged. Every full and
reduced solve uses 0-1000 s, output at `t=0` plus 200 log-spaced times from
`1e-4` to `1e3` s, and matched BDF tolerances `rtol=1e-10`, `atol=1e-14`.
Record tighter-tolerance convergence where an error is near a gate. Both
models start from the same physical inventories. Report the initial QSSA
layer and the full-window scores; never erase the layer or shift time.

Compare all 42 protected Class-I species, all GlyRS/MetRS free and occupied
pools, all 47 aminoacylation inventory species where present, Gly, Met,
ATP/ADP/AMP, Pi/PPi, tRNAGlyGCC, tRNAfMetCAU,
GlytRNAGlyGCC, MettRNAfMetCAU, fMettRNAfMetCAU, downstream peptide/protein
progress, process fluxes, and all directed resource/charging extents. Use
full-reference-only scales with the established floors: concentration
`1e-6` uM, process flux `1e-9` uM/s, dimensionless `1e-12`.
For species/process/extent `E_inf=max_t |y_red-y_full|/max(max_t|y_full|,floor)`;
for gross reversible processes retain forward and reverse terms rather
than `abs(net)`. Integrate extents as solver states, not solely by sparse
sample quadrature. Report exact-source moiety and resource balances and
minimum concentrations without clipping.

Fixed limits: algebraic closure `1e-10`; balance `1e-8`; full-window
trajectory `E_inf<=0.01`; process-flux `E_inf<=0.05`; cumulative
resource-extent `E_inf<=0.01`. Report post-layer scores separately and
classify any initial-layer-only failure as limited-domain, not a full-window
PASS. An adverse-case failure is part of the validity-domain map, never a
reason to drop that grid row. Terminal status is one of
`R3_PILOT_ACCEPTED_IN_VALIDATED_DOMAIN`, `R3_PILOT_PARTIAL_DOMAIN_ONLY`, or
`R3_PILOT_REJECTED_BY_FULL_COUPLED_VALIDATION` after all ten cases and
required observables/ledgers have been evaluated. No R4 work follows.

## Required output and adversarial controls

Produce a source-reaction-to-QSSA map, a closure certificate with physical
branch and implicit derivative checks, a grid CSV with per-case verdicts,
per-observable/process/resource tables, exact balance and timescale tables,
and a raw run manifest containing source/method/grid hashes, commands,
packages, solver options, and exit codes. Negative tests must reject a
wrong closure branch, an out-of-domain root, blanket Class-II-A algebraization,
free GlyAMP/MetAMP algebraization, a deleted directed gross ledger, and
incorrect carrier reconstruction.
