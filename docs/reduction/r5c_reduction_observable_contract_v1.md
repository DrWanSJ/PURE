# Reduction observable contract v1 — additive R5-C

Every future candidate must freeze an observable contract before validation. This semantics requirement changes no historical R4 gate, threshold, condition, floor or initial value. The CK examples below do not authorize promotion or assign new thresholds. `observable_identifiability.csv` is the machine-readable companion.

For each observable specify: scientific importance; physical definition, units and source reaction/state IDs; directly retained coordinate or reconstruction map; order; expected asymptotic accuracy and hypotheses; domain and time window; validation metric, floor and numerical uncertainty budget; whether it is mandatory for promotion. Declare all required observables and thresholds prospectively. Source kinetics must be preserved and finite-parameter validation must match the intended scientific use.

| Class | CK example | Treatment / obligation |
|---|---|---|
| A slow states/totals | ATP, protein output, T0,T1,B, dynamic enzyme totals | List exact retained coordinates. ATP/output can use exact affine reconstruction; free CP is reconstructed, while B is a slow total. Totals are dynamic under non-fast reactions. Validate states, totals and output. |
| B fast states | CK_CP, CK_CP_ADP | h0 reconstruction, generally post-layer zero order; require explicit startup treatment. |
| C exact conservation | SOURCE_GENERAL laws | Structural LS=0 and reconstruction preservation; measure L(x-x0) separately. Exact algebra does not certify a numerical ledger. |
| D net currents | j332-333, j336-337 | Kinematic reconstruction using canonical N_qf, rank and any nullspace; validate finite-parameter accuracy separately. |
| E gross directed rates | each forward/reverse fast rate | h0 gives leading circulation only. Declare whether O(1) corrections are required and how they are derived. |
| F net extents | integral j; B0-B(t) for catalytic net conversion | Include matched startup redistribution offset or retain full startup; specify integration error. |
| G gross directed extents | integral v332, integral v333, all968 source ledgers | Retain canonical provenance mapping. Gross extent accuracy needs its own reconstruction order and uncertainty analysis; it does not follow from state accuracy. |
| H initial-layer observables | binding occupancy, startup extent and hybrid switch jump | FULL_WINDOW, POST_INITIAL_LAYER and COMPOSITE_OR_HYBRID must be distinct. Fix cutoff/matching/switch policy before scoring. |

Allowed labels: PRESERVED_EXACTLY; PRESERVED_AT_ZERO_ORDER; RECONSTRUCTABLE_NET_CURRENT; DESCRIPTIVE_GROSS_FLUX_FROM_H0; REQUIRES_FIRST_ORDER_FLUX_RECONSTRUCTION; NOT_IDENTIFIABLE_AT_ZERO_ORDER; FULL_MODEL_ONLY. Labels describe capability/order, not approval. PRESERVED_EXACTLY is reserved for proved algebraic identities; zero-order accuracy requires hypotheses and measured original-parameter evidence. NOT_IDENTIFIABLE_AT_ZERO_ORDER is order-specific, not a permanent prohibition on higher-order reconstruction.

CK supports a unique pair net current because N_qf has full rank. Knowing a difference alone leaves a common forward/reverse correction free; h0 kinetics fix leading circulation but do not supply that O(1) correction. CK's full kinetic derivative and attracting fast Jacobian can constrain a first-order displacement and hence separate gross corrections if explicitly derived and validated, with startup matching. No such flux reconstruction model or certificate is built here.

All 968 directed source channels remain provenance-visible. Certificates must carry two separate declarations: SOURCE_PROVENANCE_PRESERVED and the observable-by-observable REDUCED_MODEL_ZERO_ORDER_OBSERVABLE_PRESERVED capability. No zero-order claim covers all968 gross ledgers. PURE_reduced_core remains NOT_VALIDATED and all968 decisions PENDING.
