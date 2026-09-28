# PNAS2017 R1/R2 exact reduction audit v0

This is an automated audit of exact representations and the frozen fMGG
reference. It is **not** a reduced model or scientific reduction approval.

| Finding | Result |
| --- | ---: |
| Source reactions / species | 968 / 241 |
| Exact reverse channels | 290 (580 directed reactions) |
| Source-general exact rank / conservation dimension | 214 / 27 |
| Verified name-derived sparse pool laws in source basis | 17 |
| Frozen-reference active rank | 177 |
| Additional frozen-reference-only invariants | 37 |
| Exact elimination alternatives: HIGH / MEDIUM / LOW | 0 / 145 / 752 |
| Frozen-reference identically-zero directed reactions | 485 |
| Reference-active directed reactions | 483 |
| Low-confidence human review items (grouped by law) | 18 |

Zero classes: {"REFERENCE_ZERO_DEGRADATION": 388, "REFERENCE_ZERO_OTHER": 24, "REFERENCE_ZERO_REVERSE_CHANNEL": 65, "REFERENCE_ZERO_SIDE_PATH": 8}. Directed zero-flux
patterns: {"BIDIRECTIONAL_ZERO": 32, "ONLY_FORWARD_ZERO": 0, "ONLY_REVERSE_ZERO": 65, "UNPAIRED_ZERO": 388}. A single-zero reverse
channel retains its active direction. The 32 bidirectionally zero directed
reactions form 16 channels; 65 channels have only the reverse direction zero,
none has only the forward direction zero, and 388 zero reactions are unpaired.
The 388 zero-rate degradation reactions
remain in the source and in the accounting schema; they are excluded only
from the frozen-reference active RHS and become available if parameters change.

The reverse-channel alternative retains both directed source kinetic laws,
official parameters, reaction IDs, `v_forward` and `v_reverse`. It uses
`v_net = v_forward - v_reverse` only for the net RHS. Gross ATP/GTP/phosphate,
tRNA, amino-acid and ribosomal-subunit ledgers continue to use the directed
fluxes. Exact stoichiometric identity is established for all 290 channels;
the scaled numerical RHS check was 2.65e-16 (limit 1e-12), and the
representative source-initialized trajectory difference was
0 (numerical limit 1e-6). These numerical limits check
implementation, not scientific approximation.

The conservation basis uses exact rational row reduction. Each source-general
law annihilates all 968 source columns; each additional frozen-reference law
annihilates only the proven-active columns. Biological labels are name-derived
candidates and may remain unassigned. Elimination entries are **one-at-a-time
alternatives**: each formula reconstructs its coordinate exactly if every
other coordinate in that law is retained. No simultaneous eliminated set is
selected. Class-I observables require exact reconstruction in any later
implementation. The human queue asks for pool interpretation and coordinate
choice, not for a code-level nullspace calculation.

The largest low-confidence pool supports are listed as a deterministic review
triage heuristic, not a scientific priority or approval:

- `CONS_027`: scope=SOURCE_GENERAL;support=102;residual=0; researcher must choose a useful observable/pool interpretation.
- `CONS_064`: scope=FROZEN_REFERENCE_ONLY;support=98;residual=0; researcher must choose a useful observable/pool interpretation.
- `CONS_026`: scope=SOURCE_GENERAL;support=84;residual=0; researcher must choose a useful observable/pool interpretation.

`reduction_decisions.csv` remains **968 / 968 PENDING**. Functional annotation
v2 is unchanged and supplies mechanistic context only. R3 QSSA, R4 functional
pool lumping, R5 effective kinetics, and all later approximate or final model
decisions remain deferred.
