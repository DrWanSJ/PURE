# Sean repository synchronization audit — 2026-10-09

Scope: GitHub origin, all 20 original worktrees, 18 local branch heads, four tags, 480 untracked scientific artifacts, 203 apparent modifications, and the immutable safety snapshot. An isolated audit worktree is the 21st worktree. Research branch contents are preserved at their historical heads; no scientific merge or approval is made.

Read `final_sync_status.md` and `restore_CZ.md` first. CSV inventories and JSON checks are the reproducible evidence. `branch_inventory.csv`, `refs_before.json`, and `summary.json` describe the pre-push snapshot; final reference results are in `reference_verification.json` and `remote_verified_refs.json`. The audit branch's own final SHA is verified separately in the local delivery receipt, avoiding a self-referential commit hash.

Run `python docs/audit/sean_sync_20261009/verify_sync_snapshot.py --repo <clone>` after fetching origin and tags. Exact reference pins intentionally detect later remote updates as drift requiring review. This verifies content availability, not scientific accuracy or approval.
