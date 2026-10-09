# Current archived-research recovery guide — 2026-10-09

This guide supersedes the active origin/* checkout commands in the immutable historical docs/audit/sean_sync_20261009/restore_CZ.md. Those instructions and their verifier are retained as a record of the earlier synchronization snapshot, not current branch-name requirements. Use the annotated tags below, or their recorded exact commit IDs.

While this documentation PR is pending, the guide is published on ops/topology-research-baseline-20261009. The official main branch has not admitted the policy yet. An explicit human PR merge is the governance-publication boundary for stable main; no scientific promotion is implied.

Use a fresh clone/destination and preserve frozen source-byte policies:

```powershell
git -c core.autocrlf=false -c core.longpaths=true clone https://github.com/DrWanSJ/PURE.git D:/Code/GUV
git -C D:/Code/GUV config core.autocrlf false
git -C D:/Code/GUV config core.longpaths true
git -C D:/Code/GUV fetch origin --tags
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-topology origin/codex/pnas-topology-first
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-energy origin/codex/energy-cycles-v1
```

Topology HEAD must be 60abf1e371e90f70474bc98174035726cc68f064; energy HEAD 152047da1fea4e80b1b5231594c5f70122c06e98. main remains 0b6f9ad649a7e283e440e0294a021123551f6858. Tags are annotated: compare `git rev-parse refs/tags/<tag>^{commit}` with the commit SHA, not with the tag object's SHA.

## Historical verifier local branch labels

The frozen R8 verifier asserts a local branch label. It does not fetch a same-named remote branch. In a fresh clone with no such local branch, recreate it from the verified tag:

```powershell
git -C D:/Code/GUV worktree add -b codex/r8-ck-startup-layer-20261008 D:/Code/GUV-r8-verifier refs/tags/archive/branches/20261009/codex/r8-ck-startup-layer-20261008
```

The frozen R6 verifiers assert codex/r6-ck-validation-20261007. They also require the original execution-parent HEAD 1181ab2. Its archived branch tip is pre-R6; preserve that HEAD and overlay the 479 originally untracked files from the already published preservation commit:

```powershell
git -C D:/Code/GUV merge-base --is-ancestor 9282853a24d716e3021ea85123e9ba1e0bb4c6fc refs/tags/archive/branches/20261009/codex/r8-ck-startup-layer-20261008
git -C D:/Code/GUV worktree add -b codex/r6-ck-validation-20261007 D:/Code/GUV-r6-verifier refs/tags/archive/branches/20261009/codex/r6-ck-validation-20261007
git -C D:/Code/GUV archive --format=zip --output=D:/Code/GUV-r6-overlay.zip 9282853a24d716e3021ea85123e9ba1e0bb4c6fc "docs/reduction/r6*" "scripts/*r6*.py" results/reduction/r6_ck_validation
Expand-Archive -LiteralPath D:/Code/GUV-r6-overlay.zip -DestinationPath D:/Code/GUV-r6-verifier
```

The overlay paths are absent from the parent and must remain untracked, with HEAD/index still at 1181ab2; verify the 479 paths against the archived synchronization inventory. A direct checkout of 9282853 is useful for evidence inspection, but does not recreate the original R6 execution HEAD. These recipes restore local labels and bytes without moving archive tags or modifying scientific verifiers. Frozen R6 checks also bind historical absolute paths, external request bytes and the original execution environment; restoring Git state does not make them portable automatically or claim a fresh numerical verification. On Sean's existing machine those local branches/worktrees already exist: reuse them, do not run branch-creation commands over existing names. Check each historical verifier's execution-parent and environment contract before any execution; checkout tests do not establish numerical equivalence. Some old verifier writes would update evidence, so no verifier or ODE solve is run merely to test Git recovery.

## All sixteen archives

Fetch origin tags first. Each command uses a distinct new destination. The archive registry records original SHA, tag object SHA, peeled SHA, known scientific status and deletion disposition.

### backup/sean-simulation-20261009

Original SHA: `136a9d3cce43e04c55d8b8e2afb02cc645950ff3`. Scope: `HISTORICAL_MERGE_SIMULATION_NOT_PROJECT_AUTHORITY`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-01 refs/tags/archive/branches/20261009/backup/sean-simulation-20261009
```

### backup/sean-simulation-clean-20261009

Original SHA: `1f87d563c78e52973d11536dfed6525874d1ca94`. Scope: `HISTORICAL_MERGE_SIMULATION_NOT_PROJECT_AUTHORITY`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-02 refs/tags/archive/branches/20261009/backup/sean-simulation-clean-20261009
```

### codex/pnas-active-authority

Original SHA: `bd2326078fd7d2c2307e7d2db084cf08f0c11922`. Scope: `OPEN_PR_5_HOSTED_NUMERICAL_QUALIFICATION_FAILURE_NO_MERGE`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-03 refs/tags/archive/branches/20261009/codex/pnas-active-authority
```

### codex/pnas-consolidation-20261007

Original SHA: `ffe62c4b3f65dd82b789210c653fb5701ee63f8d`. Scope: `HISTORICAL_PROVENANCE_CONSOLIDATION_NO_REDUCTION_APPROVAL`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-04 refs/tags/archive/branches/20261009/codex/pnas-consolidation-20261007
```

### codex/pnas-reduction-evidence-v0

Original SHA: `95909fdde5f5fb961a82a84ac69e55bc26d62cb1`. Scope: `FROZEN_REDUCTION_EVIDENCE_NO_SCIENTIFIC_PROMOTION`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-05 refs/tags/archive/branches/20261009/codex/pnas-reduction-evidence-v0
```

### codex/preserve-g1-worktree-20261007

Original SHA: `3e22aeeb6124e2ad7d3373e0cf056383bf9c8c1e`. Scope: `G1_HISTORICAL_HEAD_BEFORE_LATER_PREREGISTRATION_CHECKPOINT`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-06 refs/tags/archive/branches/20261009/codex/preserve-g1-worktree-20261007
```

### codex/r3-diagnostics-visualizations

Original SHA: `775607bf9922c6878be0147bd7c64fa97e86a790`. Scope: `R3_NEGATIVE_OR_NONCOMPLETED_EVIDENCE_AND_DIAGNOSTIC_VISUALIZATIONS`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-07 refs/tags/archive/branches/20261009/codex/r3-diagnostics-visualizations
```

### codex/r4-fast-block-screen-20261007

Original SHA: `9def91d4a39cad4589bd56e6db67f3a8c17b0d52`. Scope: `BOUNDED_SCREEN_UNRESOLVED_ON_REGISTERED_DOMAIN_HUMAN_REVIEW_REQUIRED`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-08 refs/tags/archive/branches/20261009/codex/r4-fast-block-screen-20261007
```

### codex/r5-mechanism-first-20261007

Original SHA: `6c11b585df42fb9aa5d5ea5d5e8be44f92e914a6`. Scope: `DESCRIPTIVE_CK_SINGULAR_LIMIT_NOT_FORMAL_PROMOTION`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-09 refs/tags/archive/branches/20261009/codex/r5-mechanism-first-20261007
```

### codex/r5c-corrigendum-20261007

Original SHA: `1181ab2f0a04d72cf76fb069be6bb842e3de75d8`. Scope: `ADDITIVE_INTERPRETATION_CORRIGENDUM_NO_PROMOTION`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-10 refs/tags/archive/branches/20261009/codex/r5c-corrigendum-20261007
```

### codex/r6-ck-validation-20261007

Original SHA: `1181ab2f0a04d72cf76fb069be6bb842e3de75d8`. Scope: `PRE_R6_EXECUTION_PARENT; R6_479_FILES_PRESERVED_AT_9282853; R6_0_OF_9_MANDATORY_PASS`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-11 refs/tags/archive/branches/20261009/codex/r6-ck-validation-20261007
```

### codex/r7-ck-first-order-20261008

Original SHA: `20ca5215d949c9451b3e6fd4435c18991783ac29`. Scope: `CK_FIRST_ORDER_IMPROVES_EXTENT_NOT_CURRENT_NO_PROMOTION`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-12 refs/tags/archive/branches/20261009/codex/r7-ck-first-order-20261008
```

### codex/r8-ck-startup-layer-20261008

Original SHA: `9ac0143b7ab6ed3b04de9d8a29a5e5732a761c7e`. Scope: `CK_STARTUP_LAYER_ATTRIBUTION_NOT_SUPPORTED_PROMOTION_FALSE`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-13 refs/tags/archive/branches/20261009/codex/r8-ck-startup-layer-20261008
```

### codex/sean-sync-audit-20261009

Original SHA: `c56ee72407f69ee91d1c4ed04cbb8a7c613f3a3f`. Scope: `GIT_BYTE_AVAILABILITY_AND_BACKUP_AUDIT_NOT_SCIENTIFIC_VALIDATION`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-14 refs/tags/archive/branches/20261009/codex/sean-sync-audit-20261009
```

### research/aminoacylation-qssa-pilot-v0

Original SHA: `24335fe798e757acb2ca3582916658bfcf5c16f5`. Scope: `R3_NINE_CASE_REJECTION_ADVERSE_NONCOMPLETION_NO_PROMOTION`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-15 refs/tags/archive/branches/20261009/research/aminoacylation-qssa-pilot-v0
```

### research/reaction-level-annotation-v0-20260928

Original SHA: `18dfddb7fd888d08ca21ea832fcab04b6739c359`. Scope: `REVIEWED_FUNCTIONAL_ANNOTATION_NOT_KINETIC_REDUCTION_APPROVAL`.

```powershell
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-archive-16 refs/tags/archive/branches/20261009/research/reaction-level-annotation-v0-20260928
```

## Observed recovery verification

Six complete independent checkouts passed: topology, energy, archived R8, simulation, synchronization audit, and exact original R6 execution parent plus its 479 raw-byte overlay files. All 16 annotations and peeled heads were fetched and verified in the independent repository. R6 476 manifest entries, energy 299 outputs plus seven source inputs, and the R8 manifest were hash-verified. The original GitHub filtered-clone metadata fetch succeeded, but its bulk lazy-blob checkout did not finish; that read-only network helper was cancelled and the partial checkout retained. Completed recovery tests used a fresh standalone clone of the verified recovery bundle, then fetched current origin refs/tags from GitHub. No original checkout was used as a shared object/index donor. This is verified offline-plus-remote-reference recovery, not a claim that the first bulk network download succeeded.
