# Legacy Mavelli2015_coarse_reference
LEGACY / FROZEN / NOT ACTIVE. Historical coarse comparison only.
Active users should start at ../../project/benchmark_registry.md.
The copies of benchmark_registry.md,model_card.md,flow_contract.json,data_provenance.csv and matlab-ci.yml
preserve the pre-migration bodies byte-for-byte. Source paths,historical outputs/manifests,archive tag
archive-mavelli2015-d7-20260924 and pre-PNAS snapshot remain unchanged.
Hash-bound legacy implementation/theory/tools remain at their registered original paths:
models/literature_reference/,docs/theory_notes.md,scripts/run_all_tests.m,
matlab/src/simulate/run_fig4_benchmark.m,matlab/tools/digitization/digitize_fig4.m,
scripts/reproduce_b1.m and environment_lock.md.
These files are excluded from current scientific defaults. Their legacy headers are not edited when that would alter frozen bytes.
Historical reproduction only: matlab -batch "addpath('scripts'); reproduce_b1".
Legacy MATLAB regressions remain available through scripts/run_all_tests.m.
The archived draft CI was never an established hosted-runner PASS.

Other retained historical entrypoints and draft interfaces:
- scripts/release_preflight.m: legacy MATLAB release checks; the current preflight is scripts/run_pnas2017_preflight.py.
- docs/reports/g1_report.md and g1_pending_human_actions.md: historical coarse-model gate records.
- docs/validation/benchmark_v0.md and qc_v0.json: historical benchmark validation.
- docs/interfaces/frontend_wireframe.md and docs/project/evidence_levels.json: earlier interface drafts, not the active PNAS source-ID contract.
- models/pure_resource_core/: generic future scaffold; it is not the current detailed reference model.

Preserving these paths does not make their historical commands or coarse observables current defaults.
