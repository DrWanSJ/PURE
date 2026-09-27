# Pre-PNAS archive record (2026-09-24)

Before any tracked-file edit, `git fetch origin` completed successfully. The checkout was on `main`, `git status --short --branch` printed only `## main...origin/main`, and local `main` and `origin/main` both resolved to `876d5adce13fbf7b833a889d7e22507b96f15aa1`. This equals the commit anticipated in the scope-change request; there was no remote advancement to reconcile.

| Item | Recorded value |
| --- | --- |
| Pre-pivot HEAD / archived commit | `876d5adce13fbf7b833a889d7e22507b96f15aa1` |
| Git tree object | `ef1bc41fb58fdb6de8a5c0eb1401e4ee3d463577` |
| Annotated tag | `archive-mavelli2015-d7-20260924` |
| Tag object SHA | `b5693ae7c3730b8e8b1b6f01e6733a4fc72579c3` |
| Tag message | `Freeze pre-PNAS project state: Mavelli 2015 benchmark through D7 RS QSSA.` |
| Remote tag | Pushed to `origin` and verified with `git ls-remote --tags` (tag and peeled commit agree) |
| Local bundle, outside the repository | `C:\Users\sean\Desktop\PURE_mavelli2015_20260924.bundle` |
| Bundle size / SHA-256 | `9603222` bytes / `c629c81c37ca2799dff20aeedd0e18c88f1d3688bf87aa1a9943a013ac7e1bf9` |
| Bundle check | `git bundle verify` reported complete history and both `main` and the annotated tag |

The pre-pivot repository path list is frozen in [pre_pnas_tree.txt](pre_pnas_tree.txt). The original `HEAD`, status, last ten commits, tree list, and remotes were also written before tracked edits to `C:\Users\sean\Desktop\PURE_prePNAS_20260924\` for an independent local record.

## Last ten commits before the pivot

```text
876d5adce13fbf7b833a889d7e22507b96f15aa1 theory: complete D7 RS QSSA reduction
cec84861ab829bf451d6902283e5f078a6e89401 theory: preregister D7 RS reduction validation
c2bb0ae63ba106d4f51bf2182dfd28dfe187e743 theory: add D7 RS fast-slow derivation
c2222a015f2ef0d82b05f7e6b2bd901080b833e0 theory: draft D7 RS QSSA reduction certificate
f168f0a9f11c214488ef9201934c5028f9c4b0cb docs: refresh D6 report artifact hash
8ac858a0b3bb01d152c1803ace6e519efe9f13d3 docs: clarify D6 mapping certificates
7af65b8923f47c78254598010339614b3495f2ab docs: explain D6 structural zero modes
f13d2b1058660b2e1caf45226a1acde87d1607ee theory: validate reduced nondimensionalization
b65d5e2a17716ce72dc1b26c41caed6bc4d6ef34 docs: fix exact-conservation audit artifact metadata
80185f0f5c6c4f3b80e6fe24c9ea0fc999518c02 theory: complete D6 dimensionless trajectory validation
```

The tag, rather than this document or the bundle, is the authoritative frozen Git reference. No history rewrite or deletion of the Mavelli benchmark was performed.
