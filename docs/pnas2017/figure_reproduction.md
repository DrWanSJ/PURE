# PNAS 2017 published-figure reproduction
## Scope
PAUSED_BY_USER on2026-10-08. No simulation, numerical comparison, plots or final tolerance selection is performed by this migration.
FIG2B=BLOCKED (execution paused; source-condition contradiction).
FIG3A=BLOCKED (execution paused; exact QSS transform UNRESOLVED).
FIG5A=BLOCKED (execution paused; source-condition contradiction inherited from Fig2B).
published_figure_reproduction=NOT_ESTABLISHED. These are execution/source blocks, not numerical FAIL results.
## Source files and hashes
Registered paths and exact SHA256 are in configs/benchmarks/pnas2017_reference/benchmark.json.
Canonical SBML dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df.
S28 8297f2348f5ebdfc3c14083577f2c5f276f35a7ee8ab30f8a37fd8431ef565ec,2317660bytes.
## Author execution semantics
fMGG_synthesis.m with unchanged CSVs,ode15s,NonNegative1:241,RelTol1e-3,AbsTol1e-9,logspace(-4,3,200).
Sample comment1e-5 contradicts executable1e-4. Executable code is authoritative.
## Dataset S28 structure
Seven readable sheets; see s28_figure_inventory.md and the source-audit JSON.
## Observable mapping
See s28_observable_mapping.md. Species headers are exact; Fig3A's executable transform is unresolved.
## Fig. 2B
Time plus241 concentrations. RRF1600 conflicts with author/S27 RRF16. No run or error summary.
## Fig. 3A
241 Boolean QSS indicators at197 times; missing exclusion/transform rules. No inferred algorithm.
## Fig. 5A
43-species aminoacylation trajectory subset;8600 stored values match Fig2B exactly. No model comparison.
## Supplementary figure status
See s28_figure_inventory.md. Conditions/transforms/column identities remain explicit limitations.
## Cross-engine comparison
Preserved RoadRunner/SimBiology evidence remains a separate numerical-integrity diagnostic in reference_reproduction.md.
## Numerical error summary
All panel errors NOT_COMPUTED. Existing cross-engine errors are not S28 reproduction errors.
## Human-readable visual comparison
NOT_RUN; no publisher artwork copied and no new plot generated.
## What is reproduced
No new published panel is reproduced by this migration. Historical author-input SBML-engine execution remains preserved.
## What remains unresolved
RRF source-condition contradiction, Fig3A QSS transform, supplementary conditions, chemical units.
## Explicit non-claims
No experimental validation, kinetic promotion, QSSA/lumping/deletion/chemostat/refit, or reduced-model approval.
## Reproduce commands
python -B scripts/reproduce_pnas2017_reference.py --verify
This verifies the source/authority contract only. Figure reproduction requires resumed user authorization,
source resolution and a hashed preregistration before comparison.
