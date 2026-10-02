# Amino-acid activation — reduction evidence quick reference

`P01` · `AUTHOR_REFERENCE_CONDITION_ONLY` · [Global index](../pnas2017_reduction_quick_reference.md) · [Method](../pnas2017_reduction_evidence_method.md)

## 1. Process boundary

50 source reactions; 12 listed candidate intermediates. Subsystems: `Aminoacylation_A_Gly`, `Aminoacylation_A_Met`. Membership can overlap other cards; the global unique count remains 968. Candidate examples: `GlyRS_AMP`, `GlyRS_ATP`, `GlyRS_Gly`, `GlyRS_GlyAMP`; 8 more in linked CSV. Exact candidate/reaction lists are in the [frozen cards](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/evidence_preregistration.json).

Protected species: `AMP`, `ATP`, `Gly`, `GlyRS`, `Met`, `MetRS`, `PPi`. Existing protected-pool links: `GlyRS_active_pool`, `GlyRS_degraded_pool`, `GlyRS_family_total`, `MetRS_active_pool`, `MetRS_degraded_pool`, `MetRS_family_total`, `coarse:GlyRS_active_pool`, `coarse:MetRS_active_pool`. These links do not by themselves certify pool completeness. Full evidence: [events](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_evidence.csv) · [states](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_evidence.csv) · [pairs](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reverse_pair_evidence.csv) · [timescales](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/process_timescale_evidence.csv) · [pool links](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_pool_metrics.csv) · [pool certificates](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/pool_evidence.csv) · [member occupancy](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_pool_metrics.csv).

## 2. Reference-condition inputs

Relevant nonzero author values: `ATP=3750`; `Gly=300`; `GlyRS=0.35`; `Met=300`; `MetRS=0.44`.

Values use the inferred reference concentration convention; author CSV absolute units are unresolved. Statistics use 200 stored `1e-4..1000 s` points. Supplemental exact `t=0` is separate; the first stored point equals the initial state, so initial-layer timing is ambiguous. No perturbation domain is claimed.

## 3. Time-scale evidence

Candidate block: full-source `J_zz` restricted to the 12 registered states. Stable relaxation range `2.2853e-05..13.481`; median `0.00086198` in the seconds convention. Stable mode count per sample: `12..12`; structural neutral lower bound: `0`. Near-zero count: `0..0`; nondecaying count: `0..0`. These modes are never inverted.

Interface turnover proxy range `2.2065e-06..2249.2`; `R_tau=tau_slow/tau_fast` range `0.046836..245.31`, median `74.031`; reciprocal `epsilon_tau` range `0.0040765..21.351`. These compare per-time medians, not the fastest mode alone. Status: **NEED_MORE_INFORMATION**. Slow coordinates and a valid elimination domain still require a scientific choice; no ratio certifies QSSA.

## 4. Occupancy / sequestration

Qualified active pools touching this card are listed separately; each denominator is its own registered token total, including all registered members beyond the card boundary.

| Registered active pool | Free / total min / median | Max nonfree fraction | Informative sample fraction |
| --- | --- | --- | --- |
| `GlyRS_active_pool` | 3.7584e-05 / 0.00073454 | 0.99996 | 1 |
| `MetRS_active_pool` | 2.7718e-05 / 0.00021855 | 0.99997 | 1 |

The linked pool certificates retain active, family-total, degraded and rejected coarse memberships separately. A family-total nonfree fraction may include degradation and is not necessarily complex occupancy. Multi-token states retain a separate member/total ratio for every qualified pool in the member-occupancy table; no scalar denominator is invented.

Protected-substrate token sequestration: **N/A_BOUND_MOIETY_MEMBERSHIP_UNRESOLVED** wherever complete token membership is absent. Enzyme occupancy cannot substitute for bound ATP, amino-acid or tRNA composition. Missing/negative/zero-denominator samples remain explicit N/A; free enzyme is not assumed equal to total enzyme.

## 5. QSS evidence

12/12 states informative; median defect 4.567e-06–0.0099974. Up to three candidate states with the largest informative median defect are shown; full state and long-form records retain all states and unavailable samples.

| Candidate state | QSS defect median / p95 / max | Informative sample fraction | Turnover median (s convention) |
| --- | --- | --- | --- |
| `MetRS_MetAMP` | 0.0099974 / 0.98395 / 0.99922 | 0.995 | 0.0033011 |
| `GlyRS_GlyAMP` | 0.00073174 / 0.88394 / 0.99447 | 0.995 | 0.00048177 |
| `MetRS_AMP` | 0.00062082 / 0.92828 / 0.98492 | 0.975 | 0.0005 |

Initial-layer flags: `UNRESOLVED_INITIAL_LAYER_STORED_X0_AT_1E_MINUS4`: 12. `delta_QSS=|dz/dt|/(production+consumption)` is unavailable at flux ≤ `1e-12`; zero flux is uninformative, not excellent QSSA. Sample fractions are unweighted author-grid fractions. No closure or full initial-layer test has been performed.

The [historical aminoacylation reference](../aminoacylation_qssa_quick_reference.md) retains A3a `FAILED_VALIDATION_ON_REFERENCE_DOMAIN`, 21-state A3b `FAILED_SMOKE_CLOSURE_FEASIBILITY` and restricted 9-state `BLOCKED_NUMERICAL_COORDINATE_DEFECT`. Fast modes, high enzyme occupancy and free GlyAMP/MetAMP accumulation do not reverse those results; see the [global regression comparison](../pnas2017_reduction_quick_reference.md#aminoacylation-regression).

## 6. Rapid-equilibrium evidence

18 distinct exact reverse pairs touch this card (a partner may cross its boundary). 12/18 pairs informative; median defect 0.00099405–0.9998. `6` pair(s) have an official disabled direction and receive `REFERENCE_DIRECTION_DISABLED`; an inactive reverse reaction is not equilibrium. Defect summaries exclude disabled or low-exchange samples. Unpaired events receive `N/A_NO_EXACT_REVERSE_PAIR`; descriptive bands select no action.

## 7. Ledger obligations

Explicit free-resource delta keys: `ADP`, `AMP`, `ATP`, `CP`, `Cr`, `GDP`, `GMP`, `GTP`, `Gly`, `GlytRNAGlyGCC`, `Met`, `MettRNAfMetCAU`, `PO4`, `PPi`, `fMet`, `fMettRNAfMetCAU`, `tRNAGlyGCC`, `tRNAfMetCAU`. ATP/GTP/AMP/ADP/GDP/Pi/PPi bookkeeping uses source IDs (`PO4` is Pi) and both directed extents. Amino-acid/tRNA, ribosome/factor occupancy and peptide effects must be reconstructed wherever source participants or protected pools touch them; absence from a free-resource delta does not establish absence of a bound moiety. The represented-particle delta is an event proxy, not osmotic pressure.

**EXACT_EVENT_STOICHIOMETRY_KNOWN; RECONSTRUCTION_REQUIRED; NO_TRANSFORMATION_EVALUATED.** Bound moieties remain unresolved where the source ledger lacks composition. Approximate trapezoidal extents and exact event stoichiometry do not establish reduced-ledger closure or kinetic validity.

## 8. Human questions

Which activation states may be eliminated, and must free GlyAMP/MetAMP remain dynamic? Which total/resource coordinates preserve enzyme occupancy and ATP→AMP/PPi bookkeeping? What validity domain and full-versus-reduced observable/ledger checks would justify a proposed representation? No answer is selected; **PENDING_HUMAN_REVIEW**.

Status: REFERENCE ONLY — NO KINETIC REDUCTION APPROVED.
