# EF-Tu ternary-complex delivery — reduction evidence quick reference

`P06` · `AUTHOR_REFERENCE_CONDITION_ONLY` · [Global index](../pnas2017_reduction_quick_reference.md) · [Method](../pnas2017_reduction_evidence_method.md)

## 1. Process boundary

34 source reactions; 7 listed candidate intermediates. Subsystems: `Aminoacylation_B_GlyGCC`, `Aminoacylation_B_fMetCAU`, `Elongation_A_Gly`, `Elongation_A_Met`, `Elongation_Ca2_pept0002`, `Elongation_Ca2_pept0003`. Membership can overlap other cards; the global unique count remains 968. Candidate examples: `EFTu_EFTs`, `EFTu_GDP`, `EFTu_GDP_EFTs`, `EFTu_GTP`; 3 more in linked CSV. Exact candidate/reaction lists are in the [frozen cards](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/evidence_preregistration.json).

Protected species: `EFTs`, `EFTu`, `GDP`, `GTP`, `GlytRNAGlyGCC`, `MettRNAfMetCAU`. Existing protected-pool links: `EFTs_active_pool`, `EFTs_degraded_pool`, `EFTs_family_total`, `EFTu_active_pool`, `EFTu_degraded_pool`, `EFTu_family_total`, `coarse:EFTs_active_pool`, `coarse:EFTu_active_pool`. These links do not by themselves certify pool completeness. Full evidence: [events](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_evidence.csv) · [states](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_evidence.csv) · [pairs](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reverse_pair_evidence.csv) · [timescales](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/process_timescale_evidence.csv) · [pool links](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/reaction_pool_metrics.csv) · [pool certificates](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/pool_evidence.csv) · [member occupancy](../../../models/pnas2017_full_reference/audit/reduction_evidence_v0/state_pool_metrics.csv).

## 2. Reference-condition inputs

Relevant nonzero author values: `EFTs=13`; `EFTu=80`; `GTP=2500`.

Values use the inferred reference concentration convention; author CSV absolute units are unresolved. Statistics use 200 stored `1e-4..1000 s` points. Supplemental exact `t=0` is separate; the first stored point equals the initial state, so initial-layer timing is ambiguous. No perturbation domain is claimed.

## 3. Time-scale evidence

Candidate block: full-source `J_zz` restricted to the 7 registered states. Stable relaxation range `6.6289e-05..1389.2`; median `0.16575` in the seconds convention. Stable mode count per sample: `7..7`; structural neutral lower bound: `0`. Near-zero count: `0..0`; nondecaying count: `0..0`. These modes are never inverted.

Interface turnover proxy range `2.0576e-05..0.45186`; `R_tau=tau_slow/tau_fast` range `0.0047277..0.10401`, median `0.017125`; reciprocal `epsilon_tau` range `9.6146..211.52`. These compare per-time medians, not the fastest mode alone. Status: **NEED_MORE_INFORMATION**. Slow coordinates and a valid elimination domain still require a scientific choice; no ratio certifies QSSA.

## 4. Occupancy / sequestration

Qualified active pools touching this card are listed separately; each denominator is its own registered token total, including all registered members beyond the card boundary.

| Registered active pool | Free / total min / median | Max nonfree fraction | Informative sample fraction |
| --- | --- | --- | --- |
| `EFTs_active_pool` | 0.028666 / 0.030451 | 0.97133 | 1 |
| `EFTu_active_pool` | 1.9371e-05 / 2.0915e-05 | 0.99998 | 0.79 |

The linked pool certificates retain active, family-total, degraded and rejected coarse memberships separately. A family-total nonfree fraction may include degradation and is not necessarily complex occupancy. Multi-token states retain a separate member/total ratio for every qualified pool in the member-occupancy table; no scalar denominator is invented.

Protected-substrate token sequestration: **N/A_BOUND_MOIETY_MEMBERSHIP_UNRESOLVED** wherever complete token membership is absent. Enzyme occupancy cannot substitute for bound ATP, amino-acid or tRNA composition. Missing/negative/zero-denominator samples remain explicit N/A; free enzyme is not assumed equal to total enzyme.

## 5. QSS evidence

7/7 states informative; median defect 1.8398e-08–0.99903. Up to three candidate states with the largest informative median defect are shown; full state and long-form records retain all states and unavailable samples.

| Candidate state | QSS defect median / p95 / max | Informative sample fraction | Turnover median (s convention) |
| --- | --- | --- | --- |
| `EFTu_GTP_GlytRNAGlyGCC` | 0.99903 / 1 / 1 | 0.96 | 0.60088 |
| `EFTu_GTP_MettRNAfMetCAU` | 0.96518 / 0.99999 / 1 | 0.935 | 0.75926 |
| `EFTu_GDP` | 0.049035 / 0.95033 / 0.98105 | 0.96 | 0.020814 |

Initial-layer flags: `UNRESOLVED_INITIAL_LAYER_STORED_X0_AT_1E_MINUS4`: 7. `delta_QSS=|dz/dt|/(production+consumption)` is unavailable at flux ≤ `1e-12`; zero flux is uninformative, not excellent QSSA. Sample fractions are unweighted author-grid fractions. No closure or full initial-layer test has been performed.

## 6. Rapid-equilibrium evidence

9 distinct exact reverse pairs touch this card (a partner may cross its boundary). 9/9 pairs informative; median defect 6.3248e-06–0.99903. `0` pair(s) have an official disabled direction and receive `REFERENCE_DIRECTION_DISABLED`; an inactive reverse reaction is not equilibrium. Defect summaries exclude disabled or low-exchange samples. Unpaired events receive `N/A_NO_EXACT_REVERSE_PAIR`; descriptive bands select no action.

## 7. Ledger obligations

Explicit free-resource delta keys: `ADP`, `AMP`, `ATP`, `CP`, `Cr`, `GDP`, `GMP`, `GTP`, `Gly`, `GlytRNAGlyGCC`, `Met`, `MettRNAfMetCAU`, `PO4`, `PPi`, `fMet`, `fMettRNAfMetCAU`, `tRNAGlyGCC`, `tRNAfMetCAU`. ATP/GTP/AMP/ADP/GDP/Pi/PPi bookkeeping uses source IDs (`PO4` is Pi) and both directed extents. Amino-acid/tRNA, ribosome/factor occupancy and peptide effects must be reconstructed wherever source participants or protected pools touch them; absence from a free-resource delta does not establish absence of a bound moiety. The represented-particle delta is an event proxy, not osmotic pressure.

**EXACT_EVENT_STOICHIOMETRY_KNOWN; RECONSTRUCTION_REQUIRED; NO_TRANSFORMATION_EVALUATED.** Bound moieties remain unresolved where the source ledger lacks composition. Approximate trapezoidal extents and exact event stoichiometry do not establish reduced-ledger closure or kinetic validity.

## 8. Human questions

Which EF-Tu/EF-Ts and ternary-complex states need explicit dynamics to retain nucleotide exchange, charged-tRNA delivery and ribosome occupancy? What validity domain and full-versus-reduced observable/ledger checks would justify a proposed representation? No answer is selected; **PENDING_HUMAN_REVIEW**.

Status: REFERENCE ONLY — NO KINETIC REDUCTION APPROVED.
