# PNAS 2017 reduction research: historical evidence index

**Status:** `HISTORICAL_REDUCTION_ANALYSIS`, not current model authority. This
index navigates evidence migrated from research commit
`025fd340300a56f069c2136ea8bb0ff542b046d4`; the canonical source remains
the unchanged combined SBML (SHA-256
`dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`).
Main's libSBML audit, execution-compatible derived SBML, reference run and
current resource map remain authoritative. The records below are not an
approved `PURE_reduced_core`.

| Candidate | Historical status | Evidence entry points | Meaning |
| --- | --- | --- | --- |
| A3a | `FAILED_VALIDATION_ON_REFERENCE_DOMAIN` | [final status](aminoacylation_A3a_final_status.md), [v1r2 certificate](aminoacylation_reduction_certificate_v1r2.md), [formal failure](../audit/pnas2017_aminoacylation_reduction_v1/formal_failure_classification_v1r2.md) | Initialization repair removed phantom inventory but did not remove the substrate-ledger sliding leak. v1r3 smoke lost closure. Validator PASS is evidence-integrity PASS, not reduction PASS. |
| A3b-21 | `FAILED_SMOKE_CLOSURE_FEASIBILITY` | [candidate comparison](aminoacylation_A3b_A3c_candidate_review.md), [smoke gate](../audit/pnas2017_aminoacylation_A3b/A3b21_S0_smoke_gate.json) | Exact total coordinates removed the sliding identity; the 21-state closure lost feasibility at 2.498 s. No formal run followed. |
| A3b-r12 | `BLOCKED_NUMERICAL_COORDINATE_DEFECT`; `NOT_VALIDATED` | [smoke gate](../audit/pnas2017_aminoacylation_A3b_r12/A3br12_S0_smoke_gate.json), [investigation](../audit/pnas2017_aminoacylation_A3b_r12/r12_investigation.md), [anti-sliding result](../audit/pnas2017_aminoacylation_A3b_r12/A3br12_antisliding_validation.json) | Nine algebraic states were tested through 10 s. The 1000 s S0 smoke did not complete and no formal S0-S5 validation occurred. Token-closed ledger membership is `OPEN_SCIENTIFIC_DECISION`. |
| A3c | `REFUSED_BY_SELECTION_RULE` | [eligibility table](../audit/pnas2017_aminoacylation_A3c/a3c_eligibility.json), [candidate comparison](aminoacylation_A3b_A3c_candidate_review.md) | **0 of 21** states were eligible under that particular protected-ledger rule. This does not prove that every possible reduction fails. |

The [v1 preregistration and input hashes](../audit/pnas2017_aminoacylation_reduction_v1/input_hashes.json), [v1r2 run registry](../audit/pnas2017_aminoacylation_reduction_v1/run_registry_v1r2.json), [A3b/A3c acceptance semantics](aminoacylation_A3b_A3c_acceptance_semantics.md), candidate configurations, negative controls and original run outputs are preserved together. Historical source and input SHA-256 values are evidence bindings, not newer claims about source chemistry. Original run files must never be replaced by a regenerated main-based run; such a run would need a new run ID.

**Evidence taxonomy:** canonical SBML and author raw ZIPs are `SOURCE FACT`;
parser tables, transforms and validation JSON are `GENERATED EVIDENCE`; the
four statuses above are `HISTORICAL SCIENTIFIC RESULT`; any proposed new ledger
or reduced core remains `PROPOSAL` or `OPEN SCIENTIFIC DECISION`. Provenance and
freshness are checked against the source hashes and the historical runner
revision, not inferred from file timestamps. This index is a navigation layer,
not source authority.
