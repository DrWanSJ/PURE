# Research branch policy — 2026-10-09

This is a Git reference/governance policy proposed for main. Publishing this branch and PR makes the replacement recovery instructions accessible; admission of this policy to stable main awaits a human PR merge. No research content is merged into main by this operation.

| Branch | Role | Pinned observation |
|---|---|---|
| main | Official stable/default branch; source authority, established benchmarks, provenance, and decisions already admitted to main | 0b6f9ad649a7e283e440e0294a021123551f6858 |
| codex/pnas-topology-first | Active methodological baseline for topology-first reduction research | 60abf1e371e90f70474bc98174035726cc68f064 |
| codex/energy-cycles-v1 | Latest active research, directly continuing topology-first; CK, NDK, MK, PPiase | 152047da1fea4e80b1b5231594c5f70122c06e98 |

The topology baseline and main are diverged: main has 14 unique commits, topology has 17. This task does not resolve that divergence. Topology is an ancestor of energy: energy ahead=1, behind=0. Branch roles do not approve scientific models or authorize replacing main. Future changes must preserve source definitions, preregistrations, negative evidence and explicit review gates.

Sixteen historical remote heads are preserved by one annotated tag per original name, using archive/branches/20261009/<original-name>. An archive tag records original branch, full SHA and scientific/historical scope; it does not certify correctness. Existing tags are immutable in intent and are never moved or force-pushed. Preserve failed/noncompleted research as well as successful cases.

PR #5 is an exception: codex/pnas-active-authority remains while that PR is open. Latest pnas-integrity check is failure at bd2326078fd7d2c2307e7d2db084cf08f0c11922; no reviews were present at audit. No closure, merge, rerun or relaxation of qualifications is performed. Other open PR heads likewise remain. This temporary documentation PR branch remains until its workflow is explicitly resolved.

Only eligible remote branch references are removed. Existing local branch labels, worktrees, dirty/untracked files, indexed metadata and backups remain intact. Local branch-name assertions in historical verifiers are preserved; use the documented local recreation recipes. An existing worktree does not by itself require a remote branch of the same name once its exact HEAD and recovery path are verified.

Current recovery instructions are in restore_archived_research.md. Historical sean_sync_20261009/restore_CZ.md and its exact-reference verifier describe the earlier 19-branch snapshot; their raw bytes remain frozen. After archival, use the new tag registry and current guide, rather than expecting those historical origin/* names or reference-count pins to remain live.
