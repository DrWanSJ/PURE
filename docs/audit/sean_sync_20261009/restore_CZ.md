# Restore on CZ

Use a fresh destination, not an existing unrelated working tree. Preserve byte-bound evidence on initial clone:

```powershell
git -c core.autocrlf=false -c core.longpaths=true clone https://github.com/DrWanSJ/PURE.git D:/Code/GUV
git -C D:/Code/GUV config core.autocrlf false
git -C D:/Code/GUV config core.longpaths true
git -C D:/Code/GUV fetch origin --tags
git -C D:/Code/GUV rev-parse origin/main
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-sync-audit origin/codex/sean-sync-audit-20261009
python D:/Code/GUV-sync-audit/docs/audit/sean_sync_20261009/verify_sync_snapshot.py --repo D:/Code/GUV
```

Expected origin/main: 0b6f9ad649a7e283e440e0294a021123551f6858. Keep the non-self-referential reference receipt with the audit if exact pin verification later reports remote drift.

All branches are fetched as origin/*; local branch labels/worktree directories are not created automatically. Choose the line of work explicitly:

```powershell
git -C D:/Code/GUV worktree add -b codex/pnas-topology-first D:/Code/GUV-topology origin/codex/pnas-topology-first
git -C D:/Code/GUV worktree add -b codex/r8-ck-startup-layer-20261008 D:/Code/GUV-r8 origin/codex/r8-ck-startup-layer-20261008
# Complete immutable R6 evidence at the original preservation commit:
git -C D:/Code/GUV worktree add --detach D:/Code/GUV-r6-evidence 9282853a24d716e3021ea85123e9ba1e0bb4c6fc
```

For another original worktree, use the branch/head in worktree_inventory.csv, creating a branch from origin/<name> or a detached worktree at its recorded SHA. The original R6 branch points to the pre-R6 parent; the complete R6 files are at 9282853 and in the R8 lineage. G1 preregistration is already in main. Backup/sean-simulation branches are historical simulations, not continuation defaults.

Consult environment_lock.md and the relevant docs/environment and campaign formal_environment.json before recreating numerical dependencies. Do not copy Windows virtual environments between machines or interpret successful content verification as numerical/scientific validation. For approved repository content no extra archive is required. Optional local resume/task context is in the separately copied recovery archive; it should be inspected and reconfigured before activation.
