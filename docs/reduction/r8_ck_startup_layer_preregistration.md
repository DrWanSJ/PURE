# R8 CK startup-layer attribution

Prospective, additive diagnostic only. Parent is verified R7 final commit
20ca5215d949c9451b3e6fd4435c18991783ac29 on
codex/r7-ck-first-order-20261008. Execution branch is
codex/r8-ck-startup-layer-20261008. The Desktop aminoacylation checkout is a
read-only visualization donor; it is never switched, staged, edited or pushed.

Question: are residual R7 CK current/extent discrepancies principally a
short-lived unmatched startup layer at the inherited switch, rather than
sustained formal first-order outer evolution error?

## Frozen objects and scope

Exactly R3_BASE, R3_ATP_LOW, R3_TRNA_LOW; both mandatory CK net pairs
re0000000332_MINUS_re0000000333 and re0000000336_MINUS_re0000000337.
Use R7 comparison.npz: source, zero-order R6 and formal first-order primary,
probe and tighter same-trajectory extent arrays. R7 formal is F0+eta Fq h1,
eta=1. Postprocessing on z0 is descriptive, not a candidate trajectory.
Registration snapshots every pre-R8 tracked file, binds all R6/R7 artifacts,
equations, source trajectories, pair definitions, contracts and code by hash.
No new state/coordinate/extent ODE trajectory is solved.

Fixed boundaries are 0, the exact inherited condition switch, 0.001 s,
0.05 s, and the existing 1000 s endpoint of FULL_WINDOW and
POST_INITIAL_LAYER. Stop if outside frozen coverage. Never move boundaries.
The switch is inherited from R7 comparison metadata and independently checked
against its original canonical definition.

## Missing exact-time storage and numerical method

The authoritative source after switch is sampled, without stored native dense
coefficients. Never regenerate it. Stored cumulative residual at a node is
R(t)=source_extent(t)-candidate_extent(t); its signed derivative at that node
is source_net(t)-candidate_net(t). On post-switch segments, cubic Hermite
interpolation of this cumulative residual uses both stored quantities.
This is interpolation of frozen evidence, not a physical model or state solve.
R=0 throughout the common source startup, including the switch cumulative
value. The right-sided current may jump at switch; never smooth across it.
DeltaXi(a,b)=R(b)-R(a). Keep signed value, absolute magnitude, fraction of
terminal signed residual, and normalized signed value for every interval.

An independent verifier uses explicit scalar Hermite coefficients and
Gauss-Legendre quadrature of their derivative, not the producer's spline.
At original nodes interpolation must reproduce stored extents and currents.
At off-grid boundaries record the actual neighboring bracket and disagreement
with linear interpolation. The envelope includes primary/probe disagreement,
original tighter same-trajectory quadrature discrepancy, original 8*eps
source gross-extent cancellation allowance, and Hermite-versus-linear
disagreement. This disagreement is a descriptive interpolation uncertainty
estimate, not a rigorous error bound for the unavailable continuous source.
Interpretations depending on unbounded sub-grid behavior remain inconclusive.
No raw-current trapezoid integral may replace the frozen cumulative ledger.

For additivity and independent quadrature comparison use the original R7
absolute F uncertainty (R7 scaled uncertainty times its original F scale),
plus boundary interpolation envelopes and 64*eps times the largest stored
source/candidate extent magnitude. This is an engineering numerical check,
not a new scientific gate.

F scaling remains max(max|source cumulative net extent| in the original
window,1e-6); D scaling remains max(max|source net current| in the original
window,1e-9). Report both frozen formal windows. Do not renormalize each
interval. Original F is a supremum over the frozen grid, not necessarily the
terminal signed residual; explicitly report both and the original worst time.
Original R7 F gate=.01 and D gate=.05 are neither changed nor rescored as
new R8 validation. Carry original uncertainty separately from interpolation.

## Current localization and graph distance

Report maxima of |source-candidate| for each of the two candidates on the
frozen scoring grid: FULL_WINDOW, POST_INITIAL_LAYER, [1ms,1000s],
[0.05s,1000s]. Include the exact lower boundary by linear current interpolation
when it is not a stored node. Label as frozen-grid/boundary maxima; do not
claim a continuous-time global maximum. Record signed source/R6/formal
currents at each maximum, original full/post D scales, switch equality and
before-1ms/before-0.05s flags. Exact-time source states use cubic Hermite
interpolation with the exact canonical full RHS as endpoint slopes, with
linear and primary/probe graph-distance disagreement reported separately.
Graph distance is q_source-[h0(T source)+h1(T source)] in the original chart.
Report two signed components, norm, component/vector scales with the frozen
1e-6 state floor, singular values/condition of actual J, no projection.

Optional frozen-slow exp(J Delta t) check is skipped: exact-time post-switch
source fast displacement has no native dense source artifact. Sparse-time
interpolation is inadequate to resolve that exponential tail independently.

## Bounded interpretation and stop

No new reduced-model validation gate. Select exactly one:
CK_STARTUP_LAYER_ATTRIBUTION_SUPPORTED,
CK_STARTUP_LAYER_ATTRIBUTION_NOT_SUPPORTED,
CK_STARTUP_LAYER_ATTRIBUTION_INCONCLUSIVE.
Compare signed contributions and their envelopes, expose cancellation.
For the unresolved BASE/TRNA_LOW extent cases, a larger later increment
than early offset with nonoverlapping uncertainty supports NOT_SUPPORTED.
SUPPORTED requires early dominance consistently and later increments small
relative to the original F scale and its existing uncertainty; ambiguous or
competing interpretations give INCONCLUSIVE. No invented percentage cutoff.
The implementation records a sufficient resolved NOT_SUPPORTED case when
both unresolved cases have |after 1ms|-uncertainty greater than
|by 1ms|+uncertainty; otherwise it preserves INCONCLUSIVE pending evidence.
This ordering comparison is attribution, not model validation.

SUPPORTED permits only TEST_MATCHED_INITIAL_LAYER_BEFORE_HIGHER_OUTER_ORDER;
NOT_SUPPORTED recommends investigating sustained outer truncation/mechanism
error before constructing a matched layer, without automatically choosing h2;
INCONCLUSIVE permits no scientific advancement. Then stop scientific work.
No h2, matching/composite model, fitted fast mode, new initial condition,
switch retuning, source projection, nine-condition campaign, ADVERSE or
aminoacylation reduction. promotion=false; PURE_reduced_core=NOT_VALIDATED;
E/G remain descriptive BUT_NOT_VALIDATED; all 968 decisions remain PENDING.

## Evidence and publication

Freeze this document, additive implementation, lineage, donor provenance and
pre-R8 snapshot before calculating diagnostics, in a separate preregistration
commit. Produce four required CSVs, boundary values, manifest, independent
verification, summary and derived evidence navigation with source hashes.
Preserve all verification failures. Only after independent verification may
the three copied atlas files be refreshed from canonical R7/R8 evidence and
tracked. Preserve their roles and useful existing content. Record original,
initial copied and final hashes; Desktop donors must remain byte-identical.
Commit results and visualization separately; push only the dedicated R8
branch after direct checks and a clean working tree. No merge or force-push.
