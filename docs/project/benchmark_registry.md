# Benchmark registry — PNAS2017_full_reference

## Source identity
Matsuura et al.(2017), Reaction dynamics analysis of a reconstituted Escherichia coli protein translation system by computational modeling.
PNAS114(8):E1336–E1344. DOI10.1073/pnas.1615351114. This is the active primary benchmark.
## Frozen source hashes
- models/pnas2017_full_reference/original/fMGG_synthesis.xml: dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df
- references/PNAS2017_Matsuura/raw/pnas.1615351114.sd28.xlsx: 8297f2348f5ebdfc3c14083577f2c5f276f35a7ee8ab30f8a37fd8431ef565ec
- models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/fMGG_synthesis.m: 5357b16387970d693f730102256c8d4ee30b91a318ad7482fc13e798834889f4
- models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/fMGG_synthesis_Sample.m: 9db2acfd7c5961f2bc52766df75bca619af496f999ad92b9b29a77f4c7fa6fc0
- models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv: a1b6f832303303c888999968d4652b00205e6adba478b11ceab9cbff4d1c41ec
- models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv: cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465
- models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml: 03d1413719847c4e13890b5f7ccf32713a5694f37f34b0c188e22fd9087379f6
## Model boundary
241 species,968 reactions,26 subsystem XMLs. mRNA-directed translation only; no DNA→RNA transcription module.
No membrane transport, refit or new kinetic mechanism is introduced.
## Author execution inputs
241-row initial CSV:27 positive components.968 local k1 entries plus a default sentinel;483 positive k1 values.
Raw SBML all-one initial/parameter values are structural placeholders, not the execution condition.
Author RHS: fMGG_synthesis.m. Solver ode15s,NonNegative1:241,RelTol1e-3,AbsTol1e-9.
Grid logspace(-4,3,200),0.0001–1000s. Sample comment1e-5 is a documented error.
## SBML compatibility normalization
3854 literal stoichiometryMath constants become identical numeric stoichiometry attributes in a derived copy.
re0000000414→PO4 retains coefficient2. Source bytes/reaction signatures remain authoritative.
## Reference execution status
Preserved author-CSV RoadRunner CVODE and SimBiology ode15s executions are documented in docs/pnas2017/reference_reproduction.md.
The new author-MATLAB entrypoint is available; this migration does not run it.
G1-PNAS=PASS/CLOSED for curation, not figure or reduced-model approval.
## Published-figure reproduction status
User paused figure work on2026-10-08. No published-panel PASS is claimed.
Machine-readable current statuses: docs/project/pnas2017_active_status.json.
- source_frozen = VERIFIED
- sbml_audited = VERIFIED
- inventory_verified = 241_SPECIES_968_REACTIONS_26_SUBSYSTEMS
- author_reference_execution = PRESERVED_SBML_ENGINE_RUNS_VERIFIED_AUTHOR_MATLAB_RUN_AVAILABLE_NOT_RUN
- cross_engine_check = COMPLETED_DIAGNOSTIC_NO_ACCEPTANCE_GATE
- dataset_s28_acquired = ACQUIRED
- dataset_s28_readable = READABLE
- fig2b_mapping = DIRECT_IDENTITY_RESOLVED_CONDITION_CONTRADICTED
- fig2b_reproduction = PAUSED_NOT_RUN
- fig3a_mapping = UNRESOLVED_EXACT_QSS_TRANSFORM
- fig3a_reproduction = PAUSED_BLOCKED_SOURCE_DEFINITION
- fig5a_mapping = DIRECT_IDENTITY_RESOLVED_SOURCE_SUBSET
- fig5a_reproduction = PAUSED_NOT_RUN
- supplementary_figure_reproduction = PAUSED_NOT_RUN
- pnas_figure_benchmark_status = PAUSED_NOT_ESTABLISHED
- experimental_validation_status = NOT_ESTABLISHED
- reduced_model_status = NOT_VALIDATED
## Dataset S28 mapping
Seven sheets. Fig2B:241 exact species; Fig3A:derived Boolean QSS indicators with unresolved executable rule;
Fig5A:43 exact species, same-source subset. See docs/pnas2017/s28_observable_mapping.md.
S28 RRF1600 differs from author CSV/S27 RRF16. Do not change input or silently convert units.
## Cross-engine status
COMPLETED numerical-integrity diagnostic. No preregistered equivalence threshold exists.
Cross-engine equivalence and paper/S28 reproduction are separate.
## Numerical limitations
Author solver tolerances control integration; they do not define a published-figure acceptance tolerance.
No tolerance is selected from observed S28 error. Nonfinite/negative diagnostics are preserved without clipping.
## Units limitations
Source SBML units remain ambiguous. S28 declares microM/time seconds; author CSV has no chemical unit declarations.
S27 second-order parameter declarations and concentrations require explicit source reconciliation. No silent unit correction.
## Experimental-validation limitations
No independent experimental-data comparison is completed. Plotting supplied data would not establish validation.
## Reduction boundary
241→214 SOURCE_GENERAL exact conservation-coordinate reduction remains accepted.
Rank177 is a frozen-author execution view only; no SOURCE_GENERAL deletion authority.
H1–H5, R3 negative/noncompletion evidence,968 PENDING decisions and96 process boxes remain unchanged.
PURE_reduced_core=NOT_VALIDATED.
## Open scientific questions
Figure definitions/conditions and units remain open. Source mapping/integrity is not promotion.
## Reproduction commands
~~~sh
python -B scripts/reproduce_pnas2017_reference.py --verify
python -B scripts/run_pnas2017_preflight.py --report-dir <external-new-directory>
~~~
Optional primary author ODE, without figure generation:
~~~sh
python -B scripts/reproduce_pnas2017_reference.py --execute-author --output-dir <new-external-directory>
~~~
Every fresh run uses a new directory, verifies inputs before integration and records git/solver/source/output provenance.
The old coarse registry is preserved byte-for-byte in docs/legacy/mavelli2015/benchmark_registry.md.
