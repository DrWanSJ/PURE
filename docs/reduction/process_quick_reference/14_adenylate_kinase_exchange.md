# Adenylate kinase exchange — reduction evidence quick reference

`P14` · `AUTHOR_REFERENCE_CONDITION_ONLY` · [Global index](../pnas2017_reduction_quick_reference.md) · [Method](../pnas2017_reduction_evidence_method.md)

## 1. Process boundary

25 source reactions; 6 listed candidate intermediates. Subsystems: `EnergyRegeneration_C`. Membership can overlap other cards; the global unique count remains 968. Candidate examples: `MK_ADP_1`, `MK_ADP_2`, `MK_ADP_ADP`, `MK_AMP`; 2 more in linked CSV. Exact candidate/reaction lists are in the [frozen cards](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/evidence_preregistration.json).

Protected species: `ADP`, `AMP`, `ATP`, `MK`. Existing protected-pool links: `MK_active_pool`, `MK_degraded_pool`, `MK_family_total`, `coarse:MK_active_pool`. These links do not by themselves certify pool completeness. Full evidence: [events](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_evidence.csv) · [states](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_evidence.csv) · [pairs](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reverse_pair_evidence.csv) · [timescales](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/process_timescale_evidence.csv) · [pool links](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_pool_metrics.csv) · [pool certificates](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/pool_evidence.csv) · [member occupancy](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_pool_metrics.csv).

## 2. Reference-condition inputs

Relevant nonzero author values: `ATP=3750`; `MK=5.6`.

Values use the inferred reference concentration convention; author CSV absolute units are unresolved. Statistics use 200 stored `1e-4..1000 s` points. Supplemental exact `t=0` is separate; the first stored point equals the initial state, so initial-layer timing is ambiguous. No perturbation domain is claimed.

## 3. Time-scale evidence

Candidate block: full-source `J_zz` restricted to the 6 registered states. Stable relaxation range `1.5503e-05..0.0010443`; median `0.00090198` in the seconds convention. Stable mode count per sample: `6..6`; structural neutral lower bound: `0`. Near-zero count: `0..0`; nondecaying count: `0..0`. These modes are never inverted.

Interface turnover proxy range `8.0125e-06..0.26279`; `R_tau=tau_slow/tau_fast` range `0.018698..87.321`, median `6.3342`; reciprocal `epsilon_tau` range `0.011452..53.483`. These compare per-time medians, not the fastest mode alone. Status: **NEED_MORE_INFORMATION**. Slow coordinates and a valid elimination domain still require a scientific choice; no ratio certifies QSSA.

## 4. Occupancy / sequestration

Qualified active pools touching this card are listed separately; each denominator is its own registered token total, including all registered members beyond the card boundary.

| Registered active pool | Free / total min / median | Max nonfree fraction | Informative sample fraction |
| --- | --- | --- | --- |
| `MK_active_pool` | 0.01574 / 0.015781 | 0.98426 | 1 |

The linked pool certificates retain active, family-total, degraded and rejected coarse memberships separately. A family-total nonfree fraction may include degradation and is not necessarily complex occupancy. Multi-token states retain a separate member/total ratio for every qualified pool in the member-occupancy table; no scalar denominator is invented.

Protected-substrate token sequestration: **N/A_BOUND_MOIETY_MEMBERSHIP_UNRESOLVED** wherever complete token membership is absent. Enzyme occupancy cannot substitute for bound ATP, amino-acid or tRNA composition. Missing/negative/zero-denominator samples remain explicit N/A; free enzyme is not assumed equal to total enzyme.

## 5. QSS evidence

6/6 states informative; median defect 2.4992e-07–0.00055046. Up to three candidate states with the largest informative median defect are shown; full state and long-form records retain all states and unavailable samples.

| Candidate state | QSS defect median / p95 / max | Informative sample fraction | Turnover median (s convention) |
| --- | --- | --- | --- |
| `MK_ADP_2` | 0.00055046 / 0.8816 / 0.95482 | 0.93 | 0.00049728 |
| `MK_ADP_1` | 0.00015928 / 0.8816 / 0.95482 | 0.93 | 0.00046531 |
| `MK_ATP_AMP` | 0.00013187 / 0.855 / 0.96379 | 0.97 | 0.00022167 |

Initial-layer flags: `UNRESOLVED_INITIAL_LAYER_STORED_X0_AT_1E_MINUS4`: 6. `delta_QSS=|dz/dt|/(production+consumption)` is unavailable at flux ≤ `1e-12`; zero flux is uninformative, not excellent QSSA. Sample fractions are unweighted author-grid fractions. No closure or full initial-layer test has been performed.

## 6. Rapid-equilibrium evidence

9 distinct exact reverse pairs touch this card (a partner may cross its boundary). 9/9 pairs informative; median defect 3.3005e-06–0.99097. `0` pair(s) have an official disabled direction and receive `REFERENCE_DIRECTION_DISABLED`; an inactive reverse reaction is not equilibrium. Defect summaries exclude disabled or low-exchange samples. Unpaired events receive `N/A_NO_EXACT_REVERSE_PAIR`; descriptive bands select no action.

## 7. Ledger obligations

Explicit free-resource delta keys: `ADP`, `AMP`, `ATP`, `CP`, `Cr`, `GDP`, `GMP`, `GTP`, `Gly`, `GlytRNAGlyGCC`, `Met`, `MettRNAfMetCAU`, `PO4`, `PPi`, `fMet`, `fMettRNAfMetCAU`, `tRNAGlyGCC`, `tRNAfMetCAU`. ATP/GTP/AMP/ADP/GDP/Pi/PPi bookkeeping uses source IDs (`PO4` is Pi) and both directed extents. Amino-acid/tRNA, ribosome/factor occupancy and peptide effects must be reconstructed wherever source participants or protected pools touch them; absence from a free-resource delta does not establish absence of a bound moiety. The represented-particle delta is an event proxy, not osmotic pressure.

**EXACT_EVENT_STOICHIOMETRY_KNOWN; RECONSTRUCTION_REQUIRED; NO_TRANSFORMATION_EVALUATED.** Bound moieties remain unresolved where the source ledger lacks composition. Approximate trapezoidal extents and exact event stoichiometry do not establish reduced-ledger closure or kinetic validity.

## 8. Human questions

Which MK complexes can be reconstructed while preserving the two ADP binding sites, ATP/AMP exchange and total occupancy? What validity domain and full-versus-reduced observable/ledger checks would justify a proposed representation? No answer is selected; **PENDING_HUMAN_REVIEW**.

Status: REFERENCE ONLY — NO KINETIC REDUCTION APPROVED.
