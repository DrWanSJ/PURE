# PNAS 2017 reduction reproducibility routes

**Current route:** unchanged combined author SBML -> main libSBML audit ->
[`pnas2017_research_schema_adapter.py`](../../scripts/pnas2017_research_schema_adapter.py)
-> historical species and aminoacylation structural analyzers -> their
validators. The adapter emits branch-compatible species, reaction and parameter
tables into a caller-selected temporary directory. It does not replace main's
audit tables or change the SBML. P2 and P3 analyses reproduced the historical
241-species map and ten aminoacylation tables at the data level; their
structural validators passed. These are reproducibility checks, not reduction
acceptance.

**Historical candidate route:** the A3a/A3b/A3c builders, runners, comparison
scripts and validators in `scripts/` are the selected research-branch tooling.
They used older audit table layouts and, in A3a's case, a particular runner
revision and worktree line endings. The exact older audit tables and runner are
preserved in
[`pnas2017_research_inputs_025fd34`](../audit/pnas2017_research_inputs_025fd34/README.md).
Use those inputs in an isolated workspace for historical reruns; keep the
recorded failed and blocked runs unchanged. New runs against main's current
audit need a new run ID, explicit adapted inputs, and separate validation.

The author subsystem XML files and simulation files under
`models/pnas2017_full_reference/original/` are exact copies of entries in the
author-site ZIP captures. They support runner inspection and must not be read
as a replacement for the combined canonical SBML. Three old branch parser or
map scripts (`parse_pnas2017_sbml.py`, `build_pnas2017_ledger.py`, and
`build_pnas2017_reduction_map.py`) were intentionally not migrated as current
tools because main's libSBML audit and resource map are authoritative.

The [historical evidence index](pnas2017_historical_evidence.md) gives the
scientific status of each candidate. The snapshot manifest and each historical
run's configurations, logs, trajectories and validation records provide source
navigation and freshness bindings; they do not certify biological validity.
