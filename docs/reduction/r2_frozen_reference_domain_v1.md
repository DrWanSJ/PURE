# R2 frozen-reference zero-rate domain certificate

Status: **R2 exact, condition-specific view PASS**. This certificate does not
authorize generic reaction or species deletion, QSSA, or approval of the
968 pending mechanistic reduction decisions.

## Authority and semantics

`scripts/verify_reduction_audit_v0.py` reparses the canonical PNAS2017 SBML
(SHA-256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`),
the original author parameter and initial-value CSVs, the normalized SBML,
and the effective author-condition SBML. Its strict MathML parser requires
each rate to be one product with the constant reaction-local `k1` exactly
once as a direct factor. It rejects model rules, events, initial assignments,
function definitions, constraints, and kinetic alternatives such as additive
or piecewise branches. The author CSV supplies exact zero `k1` for 485 of
968 directed reactions. Thus those 485 fluxes are identically zero for the
frozen author parameter profile at every state; 483 directions remain in its
active RHS. Every canonical reaction is retained.

The active-view treatment is exactly
`EXCLUDED_FROM_FROZEN_REFERENCE_ACTIVE_RHS`. It is a condition-specific
execution choice. The 485 directions comprise 388 unpaired zero reactions,
32 directions in 16 double-zero reverse channels, and 65 zero reverse
directions with a nonzero forward partner. Each one-sided channel retains
its active partner. The latter 65 do not create new frozen-only invariants:
their stoichiometric columns already lie in the active span. Reactivating
any of them still invalidates the frozen parameter profile and changes the
active-direction set.

## Exact invariant scope and reactivation

The canonical 241 x 968 stoichiometric matrix has exact rank 214 and 27
SOURCE_GENERAL left-null laws. The frozen-author active matrix has rank 177,
giving 37 additional, independent FROZEN_REFERENCE_ONLY laws. The generic
241-to-214 R1 chart uses only the 27 SOURCE_GENERAL laws; its exact
stoichiometric identity remains valid for all 968 source columns, including
reactivated directions. The 37 extra laws can optimize author-condition
execution but cannot define irreversible state deletion in a model intended
for variable parameters and conditions. The supplemental per-direction
artifact marks `DOMAIN_DECISION_REQUIRED` explicitly.

Setting each author-zero `k1` to one at the positive unit state makes its
rate nonzero. Exact law-column products show that 388 unpaired and 8
double-zero directions invalidate at least one frozen-only law when
reactivated. The other 24 double-zero directions and all 65 one-sided zero
directions change the parameter/active-view profile but leave the existing
frozen invariant span intact individually. Representative executable
mutants are `re0000000003` (unpaired), `re0000000417` (double-zero), and
`re0000000002` (one-sided zero). All 27 source-general laws annihilate each
mutant column exactly.

There are 34 frozen-only singleton laws with author initial constant zero.
Changing each singleton's initial value to 7/13 reconstructs exactly 7/13
when its constant is recomputed as `b=L*x0`. Reusing the author constant
would reconstruct zero and is rejected. These are initial-condition
identities, not structural zero species.

The source reaction IDs, both gross directed rates, and all directed
cumulative resource extents remain recoverable. `v_forward-v_reverse` is
only an RHS representation; `abs(v_net)` is never a replacement gross
ledger. R1's registered full-coupled gross-extent and balance gates remain
the numerical evidence for that accounting property.

## Reproducible artifacts

- `docs/reduction/frozen_reference_reactivation_v1.csv`: every frozen-zero
  direction, its partner status, exact frozen-law reactivation residuals,
  and explicit domain scope.
- `docs/reduction/frozen_reference_domain_certificate_v1.json`: source hashes,
  exact counts, per-pattern invalidation counts, all 34 singleton
  perturbations, and the CSV byte hash.
- `scripts/build_frozen_reference_domain_v1.py` derives these records from
  canonical source semantics and exact rational stoichiometry.
- `scripts/test_frozen_reference_domain_v1.py` independently rejects
  reactivation/singleton/scope and seven structural bypass mutants.
- `results/reduction/r2_frozen_reference_domain_v1/decisive_001` contains
  raw verifier logs and a machine-readable run manifest.

The historical `reduction_audit_v0_*` records describe alternatives before
the later R1 simultaneous coordinate certificate. R1 acceptance and its
unchanged numerical gates are recorded in `r1_acceptance_v4r3.md`.
