# R1 exact-coordinate acceptance record (v4r3)

Status: **R1 scientific and implementation gates PASS; published on the research branch.**
This record covers exact representation and the frozen author-condition
numerical check. It is not approval of R2, QSSA, a mechanistically reduced
PURE model, or any of the 968 pending reaction-reduction decisions.

## Source and exact derivation

- Canonical PNAS2017 SBML SHA-256:
  `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`.
  The author-condition compatibility SBML used only by numerical engines is
  `bd1029bcb876c052e5a28049ffe16050efbfb518d0fdeac4e57d91ee6fc8327b`.
- The source-derived audit reproduces 241 species, 968 original directed
  reactions, 290 exact reverse pairs, source-general rank 214 and left
  nullity 27. The independent semantic tests include incorrect reverse
  pairing/sign, gross-ledger substitution, and duplicate/missing conservation
  candidates with unchanged row counts: 11 tests pass. Evidence:
  `results/reduction/r1_semantic_recheck_20260929`.
- The v4 SOURCE_GENERAL 241-to-214 certificate verifies independent
  conservation rows, invertible eliminated block, exact affine A/B map,
  initial reconstruction, rebasing, and all 968 lifted source columns.
  Its SHA-256 is
  `0162c0fcdecd1fd4017180eccacdfc33b2c34141cf3df7d4b2118ed7c6c05b06`.
  All 42 protected Class-I species remain retained. Evidence:
  `results/reduction/r1_source_chart_v4/certificate_001`.
- The pointwise implementation check evaluates one canonical directed-rate
  vector per state. Its maximum scaled RHS error is 0 across the declared
  four-state set, below the unchanged `1e-12` gate; zero source rows also
  have zero absolute error. Evidence:
  `results/reduction/r1_source_chart_v4/pointwise_001/result.json`.

## Full coupled 0–1000 s comparison

The preregistered v4r3 method is
`docs/reduction/source_coordinate_method_v4r3.md` (SHA-256
`3a7e5e857e3ba06985885f63c1ae07def3d54041f8dd1d9237089b2d30e4ce96`).
Separate full 241-state and reduced 214-coordinate SciPy BDF solves use
`rtol=2.5e-13`, `atol=2.5e-15`, the stable direct source RHS, and 201
report points. The 968-dimensional model-side extent ODE uses an invertible
reverse-pair basis: `n'=v_f-v_r`, `q'=v_r`, with original gross extents
`xi_f=n+q` and `xi_r=q`; all unpaired extents use `xi_j'=v_j`. No directed
rate or gross channel is removed, and there is no rate quadrature.

| Fixed gate or diagnostic | Observed maximum | Required limit |
| --- | ---: | ---: |
| All 241 species `E_inf` | `1.0736584954429418e-9` | `1e-6` |
| All 42 Class-I species `E_inf` | `1.0736584954429418e-9` | `1e-6` |
| All 29 Class-C species `E_inf` | `2.5814292564392475e-12` | `1e-6` |
| All 968 sampled directed rates `E_inf` | `1.0159783414565027e-7` | `1e-6` |
| All 968 recovered directed gross extents `E_inf` | `4.880130290985107e-7` | `1e-6` |
| Full source gross-ledger balance, absolute | `1.753925005232304e-9` | `1e-8` |
| Reduced reconstructed gross-ledger balance, absolute | `1.7837074040016887e-9` | `1e-8` |
| Reduced minimum concentration | `-3.0854948264406182e-12` | floor `-1e-11` |

The source-balance gate is calculated from all **968 recovered directed gross
extents**, not just reverse-net coordinates. All small negatives are reported
and none is clipped. Decisive evidence, per-component tables, trajectories,
raw logs, and run manifest:
`results/reduction/r1_full_coupled_v4r3/decisive_001`.

## Independent engine

The separately registered tight RoadRunner CVODE import used the same hashed
author-condition compatibility SBML at `rtol=1e-12`, `atol=1e-14`, with the
full SciPy trajectory as the comparison reference. It imported 241 species
and 968 original reactions; source stoichiometry and author initial-state
maximum absolute discrepancies were both 0. RoadRunner versus full-source
species `E_inf` was `1.2858890841016546e-8` (limit `1e-6`). At each of
the 201 saved full-source states, all 241 concentrations were set in a fresh
RoadRunner instance; the maximum parser-versus-RoadRunner directed-rate
`E_inf` was 0 (preregistered limit `1e-10`). RoadRunner version 2.10.0 was
provided in a local Python 3.11 environment. Evidence:
`results/reduction/r1_roadrunner_tight_v4r3/attempt_002`, independently
repeated through the registered gate wrapper with the explicit local Python
3.11 interpreter in `attempt_003`. Both runs passed with the same maxima;
`attempt_003` retains the raw logs, package versions, source hash, command,
and exit code in its manifest.

## Boundary and retained negative evidence

The accepted historical loose RoadRunner author baseline is unchanged.
Earlier charts, solver settings, scaled gross extent states, and rate
quadrature produced failed or diagnostic-only results retained under
`results/reduction`; no threshold was relaxed to pass v4r3. The accepted
R1 chart is source-general and exactly reconstructs source states; the
0–1000 s numerical check covers the author condition only. Frozen-only
invariants do not enter this chart. R2 must still prove the condition-specific
zero-rate view, and R3 must separately validate its approximate GlyRS/MetRS
pilot. No commit or push is represented by this local acceptance record.
