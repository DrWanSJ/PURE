# Archive record — pre-PNAS project state (Phase 0)

Frozen backup of the project before the primary benchmark pivots to Matsuura
2017 (PNAS). The annotated tag is the authoritative frozen backup; the git
bundle is an out-of-repo safety copy. No history is rewritten; the old Mavelli
benchmark is NOT deleted.

- **Archival tag:** `archive-mavelli2015-d7-20260924`
  -> commit `876d5adce13fbf7b833a889d7e22507b96f15aa1`
  ("theory: complete D7 RS QSSA reduction")
  Message: *Freeze pre-PNAS project state: Mavelli 2015 benchmark through D7 RS QSSA.*
- **Push:** NOT pushed (per operator instruction "不允许 git push"); local only.
- **Out-of-repo bundle:** `C:/Users/sean/Desktop/PURE_mavelli2015_20260924.bundle`
  (verified: complete history, includes `refs/heads/main` and the tag).
- **Verification at freeze time:** `git fetch origin`; working tree clean
  (only the untracked `ref-PNAS/` drop present); local `main` == `origin/main`
  == `876d5adce13fbf7b833a889d7e22507b96f15aa1`; expected latest commit matched (no drift).

## Tracked-file count at HEAD
405 files tracked.

## git log -10 at freeze time
```
876d5ad theory: complete D7 RS QSSA reduction
cec8486 theory: preregister D7 RS reduction validation
c2bb0ae theory: add D7 RS fast-slow derivation
c2222a0 theory: draft D7 RS QSSA reduction certificate
f168f0a docs: refresh D6 report artifact hash
8ac858a docs: clarify D6 mapping certificates
7af65b8 docs: explain D6 structural zero modes
f13d2b1 theory: validate reduced nondimensionalization
b65d5e2 docs: fix exact-conservation audit artifact metadata
80185f0 theory: complete D6 dimensionless trajectory validation
```

## Model identities frozen under this archive
`Mavelli2015_coarse_reference` (formerly `PURE_literature_reference`, B1) —
coarse-grained benchmark, completed through the prior D7 RS-QSSA work. Retained
as historical comparator, not the active benchmark.
