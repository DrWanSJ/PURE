# Phase B1-2 frozen structural protocol

Frozen before B1-2 discovery on 2026-10-10 (Asia/Shanghai). Authority: the researcher's attached task text. This is source-exact structural curation, not a kinetic calculation. Engineering acceptance and scientific acceptance remain separate.

## Authority and preservation

Use the existing `codex/energy-cycles-v1` checkout at `672ed34c27956f50c0913efc0b153937b250c2d0`, origin `https://github.com/DrWanSJ/PURE.git`, clean and synchronized 0/0. The baseline records raw SHA-256 for every task-start tracked file (2395). Only new `phase_b1_2_*` documents and `scripts/pathways/phase_b1_2/` files are authorized. No clone, worktree, branch, commit, push, history rewrite, acceptance edit, termination execution, QSSA, fitted/effective rates, reduced SBML or B1-3 work. `PURE_two_computer_git_rules.txt` and repository/ancestor `AGENTS.md` were searched and not found; the explicit task rules govern. Missing guidance is recorded, not invented.

`phase_b1_2_execution_authorized=true`; `phase_b1_2_scientific_status=PENDING_HUMAN_REVIEW`; `phase_b1_2_formally_accepted=false`; `commit_push_authorized=false`; `qssa_authorized=false`; `kinetic_reduction_authorized=false`; `termination_authorized=false`; `phase_b1_3_authorized=false`; `full_phase_b_authorized=false`.

## Source hierarchy

Canonical `models/pnas2017_full_reference/original/fMGG_synthesis.xml` (SHA-256 `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`) and the author CSV (`cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465`) inside the original simulation ZIP (`beb27ebbd314133fbd83f68dcf8ad2ebe08cb16a1adda170b6b7b408ad355b52`) govern chemistry and parameter activity. Reuse audited B0 exact XML readers: separate builder and verifier readers. Verify 241 species, 968 directed reactions, 3854 weighted arcs, 483 positive and 485 zero directions, including reaction 0414's coefficient 2. V2 multi-context annotations and all original subsystem memberships supply context only.

## Scope derivation

Read the entire model. Select the union of ELONG Level-C contexts and actual reaction membership of all seven named original elongation subsystems, rather than an ID interval. Inventory all 968 directions with mutually exclusive operational classifications and retained multi-context metadata: positive core directions `ELONGATION_SEARCH_SCOPE`; disabled core/context `DISABLED_SOURCE_CONTEXT`; non-core exact reverses `REVERSE_OR_COMPETING_CONTEXT`; one-hop incidence on core non-resource carrier states and E1/E2/T_pre `BOUNDARY_CONTEXT_ONLY`; others `OUT_OF_B1_2_SCOPE`. E1 reaction 0001 remains elongation context but is excluded from W1-W3 execution. Termination, initiation, aminoacylation and resource interfaces are read-only context; no new regeneration is executed. Retain all selected families, equations, memberships, reverses, degradation exits, and exact incidences. Inventory coverage is not complete path enumeration.

## Bounded discovery and scenarios

Discover original directed paths with exact rational complete markings and explicit token origin states. Breadth-first search, sorted original IDs only as tie-break, maximum **50000 visited states and 16 events per waypoint leg**, maximum **64 events total**. A state includes remaining token lots and their original producer history; no merge solely by species graph. Preserve actual visited/expanded counts, reached waypoints and limits. A depth/state exhaustion is `SEARCH_INCONCLUSIVE`. No elapsed time or kinetic priority is inferred.

Waypoints are source-state identities for actual EF-Tu delivery, GDP/PO4 state, Pi and GDP-form release, peptide formation, EF-G binding, GDP/PO4 transition, translocation, GDP release and inter-round tRNA release. These define a representative staged scenario; they do not fix reaction IDs. W1 starts at E2 and reaches the first bound delivery state with one delivery supply. W2 uses E2, one `EFTu_GTP_GlytRNAGlyGCC`, and one `EFG_GTP`, reaching the second-round entry. W3 uses E2 x1 plus two independently labeled delivery tokens and two independently labeled EF-G GTP tokens, reaching `elRS70SAUAA0004_Pept0003tRNAGlyGCC`. Supplies are formal conditional inventories, not author initial concentrations. Each is allocated once. W4 imports the signed IF3-first E1 witness unchanged as upstream event evidence, fires original 0001 exactly once and then the independently discovered W3. Recompute the composition from the original initial inventory, preserving IF1/IF3 seeds and separate external EF-Tu/EF-G supplies. Revalidate P7 read-only; never rerun initiation discovery.

## Exact accounting and lineage

For each unique event record all reactants/products, complete pre/post markings, input token lots, output origin, occurrence vector, exact `S*w`, source-species resource ledger and producer-consumer DAG. Two Gly deliveries and EF-G encounters use distinct finite boundary lots. Independently rebuild token balances and all edges from canonical reactions and claimed allocations; enforce the single continuous ribosomal source carrier and use of each delivered factor carrier across state transitions. Free resource pools never certify carrier identity. Named physiological roles are context projections (INFERRED); exact source-state continuity is EXTRACTED. Composite names do not certify molecular, elemental or global nucleotide-moiety conservation. GDP-form release does not certify GTP-form recovery.

## Independent and adversarial checks

The verifier never imports the B1-2 builder. It reparses canonical XML/CSV with the audited independent B0 reader, checks hashes/memberships/scope independently, recomputes exact equations, reverses, nets, markings, finite origins, DAG, waypoints, supplies and resource claims. Use the provided 19-event example only as an independent external reference test, not builder discovery data.

Execute all applicable N01-N26 mutations through the same witness/source acceptance functions as positive evidence. At least four must remain Petri-enabled but fail specifically for INVALID_LINEAGE. Save complete fixtures or references, expected/actual codes, actual Petri feasibility, invariant, result and diagnostic. Rejecting for the wrong invariant fails the control. No threshold tuning. Preserve actual implementation/test failures in append-only B1-2 failure evidence.

## Acceptance and regression

A source integrity; B full derived inventory; C E2 continuity/0001 single use; D first round; E second round/T_pre; F exact stoichiometry; G finite multi-carrier lineage; H resources; I competition/termination boundary; J adversarial controls; K immutable prior-phase regression plus byte-identical fresh builds; L Git/authority and all old hashes preserved. Every gate is PASS, FAIL, INCONCLUSIVE or NOT_RUN; all A-L must PASS for engineering completion.

Rerun Phase A/B0/B1-1/Follow-up independent and negative functions with temporary report/failure destinations (B1-1 23+12 controls). Invoke no old runner main with defaults. Existing HTML/browser functions run read-only if dependencies are available; optional missing browser coverage is NOT_RUN and separate from mandatory source gates. Capture commands, stdout, stderr, exit codes and actual counts. Preserve inherited MATLAB CI issue (99 passed, 3 failed, 1 incomplete) as task-reported inherited evidence; no unrelated repairs or unearned current rerun claim. Build deterministic B1-2 scope, witnesses and reading view twice in distinct temporary directories and compare to delivered bytes. Rehash all old tracked bytes and inspect final Git changes.

## Human Review and stop

Provide source-exact event equations for both rounds, alternatives, ledgers, boundaries and an H1-H7 review table with researcher conclusions initially PENDING and blank notes. Original paper/SI interpretation needs explicit provenance or UNRESOLVED. Final status is `B1_2_ENGINEERING_COMPLETE_PENDING_HUMAN_REVIEW` only when every mandatory gate passes; otherwise `B1_2_INCOMPLETE_OR_INCONCLUSIVE`. Then STOP without commit/push or scientific promotion.
