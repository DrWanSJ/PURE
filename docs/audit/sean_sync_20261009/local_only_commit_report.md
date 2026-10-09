# Local-only archival commits

Existing branches retained and pushed:

- `backup/sean-simulation-20261009`: `136a9d3cce43e04c55d8b8e2afb02cc645950ff3`
- `backup/sean-simulation-clean-20261009`: `1f87d563c78e52973d11536dfed6525874d1ca94`

The former descends from the latter. Four formerly remote-absent commits include two historical simulation merges and two checkout-byte-policy commits. Their research blobs were already remote-reachable; the entire newly introduced object closure has only 18 objects, including four small `.gitattributes` blobs (maximum 7,386 bytes). Those blobs were inspected for credential/private-key patterns and oversized content; no findings. This bounded scan is not a general assurance against every possible secret in pre-existing remote history. The final tree differs from current main only in a byte-policy comment and absence of the later human R3 successor document. These branches are historical merge simulations, not authoritative scientific states. They were not merged into main.

See archival_new_objects.csv and archival_safety_checks.json. Both heads independently matched GitHub advertisements after fetch.
