# Git reference audit

Actual origin: https://github.com/DrWanSJ/PURE.git

Actual main: `0b6f9ad649a7e283e440e0294a021123551f6858`.

Before synchronization, 12 of the 18 original branch names were absent remotely. Ten heads were already incorporated into another remote branch. Only four unique commits were absent remotely, all reachable from the two existing simulation backup heads. Four local tags already matched remote tags. No stash entries, submodules, or tracked LFS files were found. LFS filter configuration exists, but configuration alone does not imply LFS payload dependencies.

All 12 absent names were pushed with explicit non-forced refspecs. After fresh fetch, independent ls-remote results exactly matched all 18 original branch heads and all four tag objects. All original worktree HEADs are now remotely reachable. Detached HEADs remain unchanged and are recorded in worktree_inventory.csv. No need to recreate temporary worktree directory names on another machine: Git records commits/branches; the manifest records the original mapping.
