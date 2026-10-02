# R1/R2 exact audit v0 method

## Evidence levels and source

`SOURCE_GENERAL` is an identity for every allowed state and parameter value
in the unchanged canonical SBML stoichiometry. `FROZEN_REFERENCE_ONLY` is
strictly conditional on the author fMGG simulation parameter CSV. Anything
requiring timescale separation, QSSA, fast equilibrium, fitting or a change
of effective kinetic law is deferred to R3–R5 and is not approved here.

The canonical combined SBML MathML is parsed directly. Each of its 968 rate
expressions is one multiplication of constant local `k1` and species factors.
The normalized execution-compatibility copy has identical rate factors,
local parameter semantics and exact stoichiometry. The recorded effective
author-condition SBML also has identical kinetic logic and reaction sides,
with each local `k1` equal to the author CSV. There are no assignment
rules, events, initial assignments or piecewise bypasses. Author parameter
names map one-to-one to `<reaction_id>_k1`; the author initial-value CSV sets
the constants for conservation laws. The model's default local `k1=1` is
not confused with the frozen author parameter override.

## R1 exact reverse representation

Exact reactant/product swap and exact negative stoichiometric columns are
checked independently of functional annotation. Every directed reaction can
enter at most one of 290 channels. `S_f*v_f + S_r*v_r = S_f*(v_f-v_r)` is
algebraically exact because `S_r=-S_f`. The alternative keeps `v_f`, `v_r`,
both source reaction IDs, both kinetic laws and both parameters; gross
resource accounting must use the directed fluxes, never `abs(v_net)`.
Random-state and source-initial RHS comparisons and one source-initialized
channel trajectory are numerical implementation checks only. A reverse pair
does not imply fast equilibrium or a `k_f/k_r` equilibrium constant.

## R1 exact conservation and candidate reconstruction

Stoichiometric coefficients are parsed as rational values, including literal
`stoichiometryMath`. Exact Fraction echelon reduction computes the rank of
all 968 columns and, separately, only columns whose frozen flux is not
identically zero. Candidate name-derived factor pools enter a basis only
when their integer vector exactly annihilates S and increases basis rank;
the remainder comes from the exact nullspace. The additional reference-only
vectors extend the source-general basis to the active-network nullspace.

Every reported law has an exact zero residual. Each elimination formula
solves one nonzero coefficient of a law with all other coordinates retained.
Alternatives must not be combined without a separate independence proof.
`HIGH_EXACT` requires an unambiguous source-general choice; none is selected
automatically. `MEDIUM_EXACT` is assigned deterministically to a source-
general named pool of support at most 16 or a frozen-reference singleton.
Other broad, mixed or interpretation-dependent laws are `LOW_CONFIDENCE` and
enter a law-level human queue. All candidates remain code-verified proposals.

## R2 frozen-reference zero flux

Only a zero author parameter that is a direct factor of the complete source
MathML product, constant locally and unmodified by rules/events, proves
`v_j(x)=0` for all x under the frozen reference. The compatibility copy is
checked for the same kinetic logic. Proven-zero directed reactions are marked
`EXCLUDED_FROM_FROZEN_REFERENCE_ACTIVE_RHS`, never deleted from source.
Single-zero channels retain their nonzero direction. Degradation cumulative
accounting and source provenance remain available for parameter changes.
`REFERENCE_ZERO_SIDE_PATH` is reserved for the eight explicitly reviewed
elongation side-path directions; other bidirectionally zero pairs are
`REFERENCE_ZERO_OTHER` unless their source role is separately established.

The species information contract and functional annotation supply output
requirements and mechanistic context; neither is used as kinetic reduction
evidence. Class I may be an algebraically reconstructed output. Class II-A
does not authorize QSSA. No final coordinate system or reduced RHS is built.
