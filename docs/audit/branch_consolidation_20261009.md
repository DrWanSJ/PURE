# Branch consolidation audit — 2026-10-09

Observation began with 19 GitHub branches, four annotated tags and 21 Sean worktrees. All live heads matched the preceding synchronization record. Default branch is main. Energy inherits topology exactly (ahead 1 / behind 0); main/topology divergence is 14 / 17 and remains unresolved by design.

All 16 archival heads received separate annotated archive/branches/20261009 tags. GitHub tag-object and peeled commit advertisements were independently checked after push/fetch; all original head SHAs match and all four prior tag objects/peeled targets remain unchanged. See ../project/branch_archive_registry.csv.

PR #5 remains OPEN at bd2326078fd7d2c2307e7d2db084cf08f0c11922, targeting unchanged main. Live pnas-integrity check 113120311200 failed in run 37718451449. No reviews were present. Its remote head is retained with reason OPEN_PR_5_PENDING_HUMAN_DECISION. No PR merge/closure or CI rerun is part of this task.

Dependency scan covered all 19 original remote-tip snapshots across source scripts, docs, configs, README, tasklist and GitHub Actions: 210 mentions. Most are historical provenance. No archival-name CI/deployment dependency was found. Two active old restore commands used R8/sync-audit origin names. They are superseded by the current tag recovery guide, published in this documentation branch before any affected deletion; frozen historical records are unchanged. Four R6 local branch assertions and one R8 local branch assertion are supported by documented/tested local branch recreation and faithful R6 execution-parent/untracked-file reconstruction, without altering the scientific scripts. An R7 parent_branch string in R8 registration is provenance metadata, not a remote fetch dependency.

Independent recovery and raw scientific-byte checks PASS; all 21 original HEADs, statuses, dirty-file bytes and indexes remain unchanged. Six complete independent checkouts and all 16 fetched annotations/peeled heads were verified. R6 replay retains its original HEAD and 479 untracked files; 476 R6 manifest entries, 299 energy outputs/seven inputs and the R8 manifest match hashes. The initial incomplete GitHub bulk checkout is retained; successful checkout tests used the standalone verified bundle plus fresh GitHub refs. Detailed checks are in branch_consolidation_recovery_verification_20261009.json. Remote deletions are prohibited until those results pass and the replacement recovery document is pushed and inspectable. Local branches/worktrees and scientific files will not be deleted or rewritten. Human merge of this documentation PR remains a governance publication blocker for official main; public PR-branch recovery instructions can support independently verified reference archival.

Scientific regression scope: raw source/evidence/manifest hashes and recorded status fields, without any expensive numerical rerun. R6 mandatory passes remain 0/9; R8 promotion=false; all four energy modules retain HUMAN_REVIEW_REQUIRED/REVISE_WITH_EXTRA_STATE and no coupled/full approval; original PNAS sources and reduced-core status remain unchanged.

## Final observed reference state

Original 19 remote branches -> 5 final remote branches (the 3 active-role branches, PR #5 head, and documentation PR #6 head). Creating the documentation branch temporarily made 20; exactly 15 eligible originals were deleted sequentially. Original 4 tags -> 20 tags. All 16 archive tag objects and peeled original commits remain independently advertised; all four old tag objects/targets unchanged.

Retained:

- main: official stable/default branch; SHA unchanged.
- codex/pnas-topology-first: active methodological baseline; SHA unchanged.
- codex/energy-cycles-v1: active four-cycle continuation; SHA unchanged; topology ancestor, ahead 1/behind 0.
- codex/pnas-active-authority: OPEN_PR_5_PENDING_HUMAN_DECISION; tag archived, hosted qualification failure preserved.
- ops/topology-research-baseline-20261009: open documentation PR #6, https://github.com/DrWanSJ/PURE/pull/6; human merge needed for stable-main policy admission.

All other original candidates listed in ../project/branch_archive_registry.csv were deleted as remote references only. Before each operation, live open PR heads, unchanged branch SHA, exact published tag object/peeled SHA, independent fetched tag and publicly pushed recovery-guide commit were checked. After each operation, head absence and tag preservation were rechecked. No branch-count cleanup merge was made. The guide was public on the PR branch before deletion; official-main admission remains a governance publication blocker, not a blocker to these independently verified archive operations.

After deletion, all 21 original worktree HEADs, statuses, dirty scientific-file SHA-256 and index SHA-256 remain unchanged. Every original local branch remains. One integration worktree was added (22 in the original repository); independent test repositories are separate. No worktree removal, reset, clean, stash, rebase, force push or scientific-file edit occurred.

Acceptance: ARCHIVE_TAGS_VERIFIED_PARTIAL_BRANCH_CLEANUP. All 15 eligible deletions are complete. The protected PR #5 archive candidate remains a branch, and the proposed governance documents are not yet merged into main; therefore this is not three-branch completion or scientific promotion. Remaining human actions: review/merge documentation PR #6 if desired; separately resolve PR #5's qualification/merge-or-close decision. Recheck live dependencies/tag/HEAD/PR status before considering later deletion of either protected PR head. No additional unprotected original branch is awaiting cleanup.

git diff --check passes for the new documentation. No numerical campaigns were rerun. R6 still 0/9 mandatory passes; R8 not promoted; all four energy modules still REVISE_WITH_EXTRA_STATE / HUMAN_REVIEW_REQUIRED; coupled/full replacement blocked; PURE_reduced_core NOT_VALIDATED. Frozen historical synchronization/restore records remain byte-identical and are explicitly superseded by the current guide.
