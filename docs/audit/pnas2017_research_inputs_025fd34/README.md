# Historical PNAS reduction audit inputs

**Status:** `HISTORICAL_INPUT_SNAPSHOT`; this directory is not the current
libSBML audit. It contains exact Git blob bytes for all 37 files in
`models/pnas2017_full_reference/audit/` at research commit
`025fd340300a56f069c2136ea8bb0ff542b046d4`. The
[`snapshot_manifest.json`](snapshot_manifest.json) binds each file to its
source path, byte count, SHA-256 and Git blob. Current audit tables in
`models/pnas2017_full_reference/audit/` remain authoritative and were not
replaced.

The A3a [`input_hashes.json`](../pnas2017_aminoacylation_reduction_v1/input_hashes.json)
contains 75 historical SHA-256 bindings. Against the research commit's Git
blobs, 59 match the bytes directly, 15 match only after LF-to-CRLF conversion,
and one runner matches an earlier revision. These are historical worktree
line-ending bindings; do not silently rewrite the expected hashes or call a
fresh checkout a failed scientific validation. The earlier runner is preserved
as [`scripts/run_pnas2017_aa_v1_formal_11c4d704a.m`](scripts/run_pnas2017_aa_v1_formal_11c4d704a.m)
from commit `11c4d704a`. The later research runner remains in `scripts/` and
must not be substituted for a run whose input hash names the earlier version.

For a historical rerun, use an isolated disposable workspace with these 37
files overlaid at their listed source paths and the matching historical runner.
Do not overlay this snapshot into the integration branch's current audit
directory. A new run against current main inputs needs a new run ID and new
hashes. Historical failed or blocked results remain historical results even
when an evidence-integrity check passes.
