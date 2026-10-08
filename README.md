# PURE — PNAS2017 translation reference

The active primary benchmark is **PNAS2017_full_reference**, the mRNA-directed translation model of
Matsuura et al.(2017), PNAS114(8):E1336–E1344, DOI[10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114).

Start with the [active benchmark registry](docs/project/benchmark_registry.md),
[model card](docs/model_card.md), and [current evidence status](docs/project/pnas2017_active_status.json).

~~~sh
python -B scripts/reproduce_pnas2017_reference.py --verify
python -B scripts/run_pnas2017_preflight.py --report-dir <new-external-directory>
~~~

The first command verifies frozen sources,author input mapping,stoichiometry normalization,S28 workbook/header identity,
current authority and historical preservation. The second runs all applicable current PNAS and exact-coordinate verifiers.
Neither generates plots or performs a published-figure comparison.
An optional fresh primary author ODE command is documented in the registry; it requires MATLAB and a new external output directory.

**Figure reproduction is paused by the user.** Fig2B/5A comparisons are NOT_RUN; Fig3A's exact QSS transform is UNRESOLVED.
S28 RRF1600 differs from author CSV/S27 RRF16. No figure PASS or independent experimental validation is claimed.

Source frozen;241 species,968 reactions,26 subsystem XMLs;27 positive author initial components.
G1-PNAS PASS/CLOSED covers curation. Existing cross-engine runs are separate numerical-integrity diagnostics.
241→214 SOURCE_GENERAL exact coordinate reduction is preserved. Rank177 is only a frozen-author execution view.
All968 mechanistic decisions remain PENDING. **PURE_reduced_core remains NOT_VALIDATED.**

## Repository navigation
- references/PNAS2017_Matsuura/: frozen publisher/author sources.
- models/pnas2017_full_reference/: source,compatibility normalization and audit inventories.
- configs/benchmarks/pnas2017_reference/: active source/solver/time/status configuration.
- docs/pnas2017/: current source,theory and paused figure evidence.
- docs/reduction/: unchanged human decisions,exact-coordinate and bounded reduction evidence.
- results/pnas2017_reference/: preserved full-reference engine evidence; new runs never overwrite it.
- models/pure_reduced_core/: future human-reviewed model.
- [Legacy preservation](docs/legacy/mavelli2015/README.md): Mavelli2015_coarse_reference is LEGACY/FROZEN/NOT_ACTIVE.

The canonical SBML defines model structure. The author's own fMGG_synthesis.m and CSVs define the primary author-ODE execution route.
Derived inventories,code and navigation cannot replace source authority. Transcription and GUV transport are future reviewed extensions.
Historical paths and bytes remain valid; their old commands are available only through the explicit legacy index.
See [migration inventory](docs/migration/pnas2017_active_authority_inventory.md) and
[remaining-reference audit](docs/migration/mavelli_remaining_reference_audit.md).
