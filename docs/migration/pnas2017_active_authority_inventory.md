# PNAS 2017 active-authority inventory - read-only external deliverable

Current main audited: `0b6f9ad649a7e283e440e0294a021123551f6858`.
Starting checkout HEAD: `24335fe798e757acb2ca3582916658bfcf5c16f5` on `research/aminoacylation-qssa-pilot-v0`. Current checkout differs from main; no reset or checkout performed.

Main git-grep matches: 155 files; main pathname matches: 49 files; exact-one-classification main CSV rows (including required inspections): 171. Filesystem inventory: 5054 files; matching working-tree files: 249, of which 83 are absent from main inventory.

## Execution boundary

All planned changes are NOT_EXECUTED_STOP_BOUNDARY. Root audit identified unresolved Fig. 3A QSS transform semantics in frozen source, triggering user section 23. These inventory rows record proposals only; no repository migration, source edit, scientific decision, commit or push was performed.

## Search coverage

- `Mavelli`
- `Mavelli2015`
- `PURE_literature_reference`
- `literature_reference`
- `b1_mavelli2015`
- `b1_fig4`
- `run_fig4_benchmark`
- `reproduce_b1`
- `digitize_fig4`
- `R01_Mavelli2015`
- `GFP 238`
- `DNA_0p34nM`
- `DNA_1p7nM`
- `DNA_6p8nM`

Each main matched file has exactly one classification in pnas2017_active_authority_inventory.csv. filesystem_matching_files.csv separately classifies matching files in the older checkout, including local files absent from main. inventory_details.json preserves Git match/path lists, full filesystem inventory and all parsed JSON/CSV SHA-256 bindings.

## Classification counts

- ACTIVE_REMOVE_REFERENCE: 9
- ACTIVE_REPLACE: 4
- GENERIC_FIXTURE_KEEP: 1
- HISTORICAL_PROVENANCE_KEEP: 68
- LEGACY_KEEP_IMMUTABLE: 79
- PNAS_ALREADY_ACTIVE: 10

## Hash-binding interpretation

A recorded SHA does not automatically freeze the current mutable path. docs/audit/exact_conservation_20260922/source_inventory_before.json, docs/audit/nondim_trajectory_20260923/integrity_before.json and docs/environment/CZ_20260922/initial_state.json record earlier repository snapshots. Their immutable records must remain unchanged; current model_card.md and benchmark_registry.md can have successor active semantics after preserving old content because no current live-byte verifier for those two bodies was found.

Stronger registered artifact/source contracts protect docs/theory_notes.md and scripts/run_all_tests.m through D7 artifact_manifest.json, and models/literature_reference model definition/parameters/manifest plus generated code through multiple audited source bindings. Add successor active navigation instead of editing those protected bytes.

matlab/src/simulate/run_fig4_benchmark.m is in nondimensionalization_validation_v2_20260923/historical_integrity.json under protected_scientific_sources_checked, SHA 7d3fd3f47436e6f8abfa3f0b771f34192929cb9e5735027dda960b1a5c886240; canonical_scientific_sources_byte_identical=true. This explicit historical protection is stronger than a broad snapshot. Keep the old tool path and bytes, and remove it from current defaults.

environment_lock.md is asserted unchanged by docs/environment/environment_lock_CZ.md. docs/project/evidence_levels.json records dated human B1 decisions and is checked by frozen release_preflight regression code; preserve it and create a separate active PNAS evidence contract.

A legacy header inside an otherwise frozen file changes its hash. Use successor index/navigation/configuration rather than adding headers to registered source/tool/report bytes.

## Active proposals

- `.github/workflows/matlab-ci.yml`: ACTIVE_REMOVE_REFERENCE. Mavelli may appear only as explicit legacy/provenance; active defaults must use PNAS.
- `README.md`: ACTIVE_REMOVE_REFERENCE. Mavelli may appear only as explicit legacy/provenance; active defaults must use PNAS.
- `configs/README.md`: ACTIVE_REMOVE_REFERENCE. Mavelli may appear only as explicit legacy/provenance; active defaults must use PNAS.
- `data/README.md`: ACTIVE_REMOVE_REFERENCE. Mavelli may appear only as explicit legacy/provenance; active defaults must use PNAS.
- `data/provenance.csv`: ACTIVE_REMOVE_REFERENCE. Mavelli may appear only as explicit legacy/provenance; active defaults must use PNAS.
- `docs/README.md`: ACTIVE_REMOVE_REFERENCE. Mavelli may appear only as explicit legacy/provenance; active defaults must use PNAS.
- `docs/interfaces/flow_contract.json`: ACTIVE_REPLACE. Top-level active authority must match PNAS2017; broad old inventory snapshots are historical records, not live byte-protection.
- `docs/model_card.md`: ACTIVE_REPLACE. Top-level active authority must match PNAS2017; broad old inventory snapshots are historical records, not live byte-protection.
- `docs/project/benchmark_registry.md`: ACTIVE_REPLACE. Top-level active authority must match PNAS2017; broad old inventory snapshots are historical records, not live byte-protection.
- `matlab/README.md`: ACTIVE_REMOVE_REFERENCE. Current folder documentation advertises B1 driver/generator/digitizer as its default scientific route.
- `results/README.md`: ACTIVE_REMOVE_REFERENCE. Current body lists only Mavelli B1 baseline and generic outputs; it needs PNAS default navigation.
- `schemas/README.md`: ACTIVE_REPLACE. Current schema authority points to literature_reference definition and run_fig4 benchmark.
- `tasklist.md`: ACTIVE_REMOVE_REFERENCE. Mavelli may appear only as explicit legacy/provenance; active defaults must use PNAS.

## Key registered bindings

- `docs/model_card.md`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/144/path|sha256`: `51ca78c801bcc9b24b81d07676fd0bfd7f0b3e8956408963be33133eae42d70d`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/docs/model_card.md`: `9eddf6a2e62740aab654c39750a545a30b405df0a250a0e02cc7197f09b3ebcb`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/163/path|sha256`: `51ca78c801bcc9b24b81d07676fd0bfd7f0b3e8956408963be33133eae42d70d`; matches current Git bytes `False`.
- `docs/project/benchmark_registry.md`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/145/path|sha256`: `2d1a08ea2ee9a3192cfc623ebb878a69ebb3c40b788ac7f62c853a7cb2e51798`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/docs/project/benchmark_registry.md`: `2d1a08ea2ee9a3192cfc623ebb878a69ebb3c40b788ac7f62c853a7cb2e51798`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/164/path|sha256`: `2d1a08ea2ee9a3192cfc623ebb878a69ebb3c40b788ac7f62c853a7cb2e51798`; matches current Git bytes `False`.
- `docs/theory_notes.md`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/150/path|sha256`: `0bfd4250e17245e2ef019d8f10c61a81d76968e892b01a61cfad128abb98f86f`; matches current Git bytes `False`.
  - `docs/theory/nondim_map.json` `/source_fingerprints_sha256/1/path|sha256`: `2a8f2225afca522acf285bc3bd417f077618498ef10b2ce09d965a795291244b`; matches current Git bytes `False`.
  - `docs/audit/dimensionless_20260921/provenance.json` `/sources/15/path|sha256`: `9c3c75e74c8a2dc33842d3b23e7412ff547f7ef16dfce927bc874279504699b2`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/docs/theory_notes.md`: `6b320ecb39c13eced380cc086a7e78bb4db1b31a4efc3dd644cbab5f3fea96cb`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/170/path|sha256`: `0bfd4250e17245e2ef019d8f10c61a81d76968e892b01a61cfad128abb98f86f`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/artifact_manifest.json` `/files/28/path|sha256`: `2a8f2225afca522acf285bc3bd417f077618498ef10b2ce09d965a795291244b`; matches current Git bytes `False`.
  - `docs/audit/rs_qssa_d7_20260924/artifact_manifest.json` `/files/39/path|sha256`: `ec25567a966303ad3045c88df162c6576c4f42dd8cdc7f239dc8f5dd632eed90`; matches current Git bytes `True`.
- `scripts/run_all_tests.m`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/259/path|sha256`: `0d0859642bbdd2b2858adfdc37cf906d0edbde7384edbe251b1f1827f36fa22f`; matches current Git bytes `False`.
  - `docs/audit/rs_qssa_d7_20260924/run_002/validation_results.json` `/implementation/15/path|sha256`: `e7021ec4b2365eaa5aea38e20e83de59a5ce22b7eb4a219c7c6d33bba70af126`; matches current Git bytes `True`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/scripts/run_all_tests.m`: `0d0859642bbdd2b2858adfdc37cf906d0edbde7384edbe251b1f1827f36fa22f`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/284/path|sha256`: `0d0859642bbdd2b2858adfdc37cf906d0edbde7384edbe251b1f1827f36fa22f`; matches current Git bytes `False`.
  - `docs/audit/rs_qssa_d7_20260924/validation_results.json` `/implementation/15/path|sha256`: `e7021ec4b2365eaa5aea38e20e83de59a5ce22b7eb4a219c7c6d33bba70af126`; matches current Git bytes `True`.
  - `docs/audit/rs_qssa_d7_20260924/artifact_manifest.json` `/files/63/path|sha256`: `e7021ec4b2365eaa5aea38e20e83de59a5ce22b7eb4a219c7c6d33bba70af126`; matches current Git bytes `True`.
- `scripts/reproduce_b1.m`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/258/path|sha256`: `dba191e1ff9e59e4183b839ac976f3f741bc1c39ba9b85dc767cdab778b4cef0`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/scripts/reproduce_b1.m`: `dba191e1ff9e59e4183b839ac976f3f741bc1c39ba9b85dc767cdab778b4cef0`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/283/path|sha256`: `dba191e1ff9e59e4183b839ac976f3f741bc1c39ba9b85dc767cdab778b4cef0`; matches current Git bytes `False`.
- `scripts/release_preflight.m`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/257/path|sha256`: `e14b4b7fb738b3a24f15de9a51815eef712846ea9bf43c4dd9bfd33de6118c95`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/scripts/release_preflight.m`: `e14b4b7fb738b3a24f15de9a51815eef712846ea9bf43c4dd9bfd33de6118c95`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/282/path|sha256`: `e14b4b7fb738b3a24f15de9a51815eef712846ea9bf43c4dd9bfd33de6118c95`; matches current Git bytes `False`.
- `matlab/src/simulate/run_fig4_benchmark.m`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/187/path|sha256`: `7d3fd3f47436e6f8abfa3f0b771f34192929cb9e5735027dda960b1a5c886240`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/matlab/src/simulate/run_fig4_benchmark.m`: `7d3fd3f47436e6f8abfa3f0b771f34192929cb9e5735027dda960b1a5c886240`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/207/path|sha256`: `7d3fd3f47436e6f8abfa3f0b771f34192929cb9e5735027dda960b1a5c886240`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/isolation.json` `/copied_files/32/path|sha256`: `7d3fd3f47436e6f8abfa3f0b771f34192929cb9e5735027dda960b1a5c886240`; matches current Git bytes `False`.
  - `docs/audit/nondimensionalization_validation_v2_20260923/historical_integrity.json` `/protected_scientific_sources_checked/2/path|sha256`: `7d3fd3f47436e6f8abfa3f0b771f34192929cb9e5735027dda960b1a5c886240`; matches current Git bytes `False`.
  - `docs/audit/nondimensionalization_validation_v2_20260923/continuation_record.json` `/scientific_source_snapshot/2/path|sha256`: `7d3fd3f47436e6f8abfa3f0b771f34192929cb9e5735027dda960b1a5c886240`; matches current Git bytes `False`.
- `matlab/tools/digitization/digitize_fig4.m`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/198/path|sha256`: `f222ea5c2dc9622e9297c68e3561d4000174f09d063fdfc171834b070f5380f3`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/matlab/tools/digitization/digitize_fig4.m`: `f222ea5c2dc9622e9297c68e3561d4000174f09d063fdfc171834b070f5380f3`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/223/path|sha256`: `f222ea5c2dc9622e9297c68e3561d4000174f09d063fdfc171834b070f5380f3`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/isolation.json` `/copied_files/43/path|sha256`: `f222ea5c2dc9622e9297c68e3561d4000174f09d063fdfc171834b070f5380f3`; matches current Git bytes `False`.
- `environment_lock.md`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/154/path|sha256`: `cd69648821665da0a665cc8aea00cb9ac48435831b0639275e4883e70749ca09`; matches current Git bytes `False`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/environment_lock.md`: `cd69648821665da0a665cc8aea00cb9ac48435831b0639275e4883e70749ca09`; matches current Git bytes `False`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/174/path|sha256`: `cd69648821665da0a665cc8aea00cb9ac48435831b0639275e4883e70749ca09`; matches current Git bytes `False`.
- `models/literature_reference/model_manifest.json`
  - `docs/audit/exact_conservation_20260922/source_inventory_before.json` `/files/221/path|sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/audit/dimensionless_20260921/provenance.json` `/sources/2/path|sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/environment/CZ_20260922/initial_state.json` `/tracked_sha256/models/literature_reference/model_manifest.json`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `models/reductions/rs_qssa/parameters.json` `/source_fingerprints/2/path|sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/audit/nondim_trajectory_20260923/integrity_before.json` `/files/246/path|sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/environment/CZ_20260922/isolation.json` `/copied_files/66/path|sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/audit/rs_qssa_d7_20260924/source_byte_bindings.json` `/2/path|tested_raw_sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/audit/rs_qssa_d7_20260924/source_byte_bindings.json` `/2/path|git_blob_sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/audit/nondimensionalization_validation_v2_20260923/historical_integrity.json` `/protected_scientific_sources_checked/15/path|sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/audit/nondimensionalization_validation_v2_20260923/continuation_record.json` `/scientific_source_snapshot/16/path|sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/audit/rs_qssa_d7_20260924/artifact_manifest.json` `/files/56/path|sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.
  - `docs/audit/rs_qssa_d7_20260924/artifact_manifest.json` `/files/56/path|git_blob_sha256`: `fd5bfee5406fe3eadf087eb1b81b360bd49c0f95044c2a2801cf985f268de9e4`; matches current Git bytes `True`.

No verifier was executed; some verifiers mutate repository reports. No repository files were edited. The external artifacts may be copied to repository docs/migration only after resolving STOP boundaries and establishing the authorized successor workflow.
