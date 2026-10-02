# G1-PNAS rerun and closure report — 2026-10-02

**G1-PNAS = PASS / CLOSED.** The exact ten tasklist §13.2 criteria pass, and all six required current verifiers pass after the exact approved documentation-provenance synchronization.

G1-PNAS closes the detailed-reference curation and reduction-review preparation stage. It authorizes entry into human-reviewed kinetic reduction. It does not validate PURE_reduced_core.

## Basis and historical provenance

- Rerun source HEAD: `678fcb709324142454fd7a80cb6185c64b900510`; isolated checkout `C:\Users\sean\.codex\worktrees\g1-pnas-closure\GUV`, branch `main`, initially clean, local `main == origin/main`; expected prompt SHA matches.
- The desktop checkout started on a separate research branch at `24335fe` with untracked `.agents.zip`; it was excluded. The isolated main previously at `141140dd` was fast-forwarded to current origin/main; no research branch/PR was merged.
- Historical 2026-09-27 BLOCKED report is preserved at [`g1_pnas_report_20260927_blocked.md`](g1_pnas_report_20260927_blocked.md) under a clear historical preface. The exact original 6,270-byte payload has SHA-256 `c7bd1b36e6f67a9c8093b30c117064319d85cafc4167de2a8e432dd64f60f0ae`; its original 65-hex hash typo remains historical evidence. Later source acquisition does not retroactively change BLOCKED.
- Only current-main source, model, tables and preserved evidence support this gate. Open research PR #3/#4 remain untouched; their unmerged conclusions do not establish G1.
- Companion machine evidence: [`g1_pnas_verification_20261002.json`](g1_pnas_verification_20261002.json), with durable [`g1_pnas_evidence_20261002.zip`](g1_pnas_evidence_20261002.zip). The archive preserves all 2,904 fresh libSBML warnings, initial official failures, source/contracts diagnostics, fresh SimBiology trajectory and warnings, comparison, fresh preparation outputs and the repair proposal as preserved before application.

The earlier save-diagnostics-only instruction and original failed checks are retained in the diagnostic-history archive. The renewed request authorized only the exact audited provenance repair and formal closure. Historical integration packet files remain byte-identical; fresh literal integration output is recorded in the closure evidence archive.

## Source and model identities

The detailed benchmark is `PNAS2017_full_reference`, Matsuura et al., DOI `10.1073/pnas.1615351114`, SBML model `fMGG_synthesis`, Level 2 Version 4. It is mRNA-directed translation; no transcription module is claimed.

| Frozen input | Bytes | SHA-256 |
| --- | ---: | --- |
| Combined `fMGG_synthesis.xml`, raw and byte-identical `original/` copy | 1,732,620 | `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df` |
| `SBML_files.zip` | 250,427 | `24f0748c883eb6dcb748c20de7fdb2c8e495397f4b8ffb6c82246a03f0a93b03` |
| `Simulate_fMGG_synthesis.zip` | 46,143 | `beb27ebbd314133fbd83f68dcf8ad2ebe08cb16a1adda170b6b7b408ad355b52` |
| Publisher article PDF | 1,816,513 | `e340ba829f87121e723059aebecc56c342c37c2cc4687692d1447f16b38f2a4e` |
| Dataset S28 XLSX | 2,317,660 | `8297f2348f5ebdfc3c14083577f2c5f276f35a7ee8ab30f8a37fd8431ef565ec` |

All 33 registered acquired source files (three author-site files, article PDF, S01–S29) match registered byte sizes and SHA-256; 31 extracted original archive members match. The PDF signature is `%PDF-1.4`; all 29 workbooks opened with openpyxl 3.1.2. S27 is XLSX with four sheets; S28 is XLSX with seven sheets. A separate full Supporting Information document has not been established; that acquisition gap and S27's relation to the paper's combined-SBML wording remain mapped, not fabricated.

Fresh libSBML 5.21.2 parsing yields zero parse messages and 2,904 consistency warnings: 968 rule-10541 kinetic-law unit warnings and 1,936 rule-99505 undeclared-unit/literal warnings. All 2,904 complete fresh messages are preserved in `g1_pnas_evidence_20261002.zip` as `source/libsbml_messages_fresh.json`. Four freshly generated inventory CSVs are byte-identical to main: 241 species, 968 reactions, 968 local parameters, 26 modules; 1,098 subsystem entries reconcile to 968 unique combined signatures, with zero unmatched. Author initials have 27 positive components; raw all-one initials/`k1` are structural placeholders.

Source `re0000000414` produces **2 PO4**. The DERIVED numeric-stoichiometry compatibility copy replaces 3,854 literal `stoichiometryMath` encodings without changing any reaction signature, species/reaction ID or scientific coefficient. Raw source remains unchanged.

## Exact tasklist §13.2 gate table

The following ten criterion texts are copied from current `tasklist.md`; no extra acceptance criterion is introduced.

| Criterion | Evidence | Verification performed now | Status | Residual limitation / next-phase note |
| --- | --- | --- | --- | --- |
| 1. 权威来源文件以校验和冻结；缺失文件明确标为缺失。 | `references/PNAS2017_Matsuura/provenance/sources.json`; `references/PNAS2017_Matsuura/provenance/publisher_capture.json`; `references/PNAS2017_Matsuura/MISSING_SOURCES.md` | 33 frozen acquired source files match registered byte size and SHA-256; 31 extracted original archive members match; PDF signature and all 29 XLSX workbooks checked. | PASS | A separate full Supporting Information document is not established and remains explicitly mapped; S27 format/source relation remains open. |
| 2. 参考网络可用标准 SBML 工具读取，并保存验证消息。 | `docs/pnas2017/g1_pnas_evidence_20261002.zip (member source/libsbml_messages_fresh.json)`; `docs/pnas2017/sbml_audit.md` | Existing SBML audit executed outside repo with libSBML 5.21.2: parse messages 0; consistency warnings 2904. Fresh complete messages saved in the evidence ZIP; counts and hashes recorded in companion JSON. | PASS | 968 rate-unit and 1936 undeclared-unit/literal warnings remain; execution does not certify chemical units. |
| 3. 自动生成物种、反应、参数及模块库存，保留原始标识。 | `models/pnas2017_full_reference/audit/species.csv`; `models/pnas2017_full_reference/audit/reactions.csv`; `models/pnas2017_full_reference/audit/parameters.csv`; `models/pnas2017_full_reference/audit/modules.csv` | Regenerated all four inventories outside repo; each is byte-identical to current-main inventory, preserving original IDs. | PASS | Inventories describe the detailed reference; no new reduced model or chemical composition was created. |
| 4. 241 组分、27 初始组分、968 反应、26 子系统等发表计数得到解释，或逐项记录差异。 | `models/pnas2017_full_reference/audit/species.csv; models/pnas2017_full_reference/audit/reactions.csv; models/pnas2017_full_reference/audit/parameters.csv; models/pnas2017_full_reference/audit/modules.csv; results/pnas2017_reference/rr_cvode_author_csv_20260924/run_manifest.json`; `docs/pnas2017/reference_reproduction.md`; `models/pnas2017_full_reference/audit/resource_map_manifest.json` | Confirmed 241 species, 968 combined reactions/local parameters, 26 subsystem XMLs, 1098 subsystem entries, 968 exact unique signatures, 0 unmatched, and 27 positive author-CSV initials. | PASS | Raw all-one initial/parameter placeholders are distinguished from author execution values; shared source diagrams are not additional events. |
| 5. 资源/小分子账本可供逐反应核查。 | `docs/pnas2017/chemical_ledger.md`; `models/pnas2017_full_reference/audit/species_properties.csv`; `models/pnas2017_full_reference/audit/reaction_balance_audit.csv` | 241/968 exact-once original IDs; all 968 particle and 18 free-resource event deltas recomputed against existing source inventory and agree; manifest hashes verified. | PASS | Free-resource deltas and represented-particle proxy do not certify bound moieties, elemental balance or osmotic pressure. |
| 6. 全部实际获得的参考反应映射到模块和家族；若实际网络与 968 不同，不能假装覆盖 968。 | `docs/reduction/reduction_map.md`; `docs/reduction/reaction_level_annotation_v2.csv`; `docs/reduction/reaction_family_summary_v2.csv`; `docs/reduction/reaction_annotation_manifest_v2.json` | Existing v1/v2 and reaction-contract verifiers exit 0; v0/v1/v2 cover all 968 IDs exactly once; v2 categories 492/50/0/420/6, unresolved 0, 35 active families plus DEG. | PASS | Functional annotation is complete; 50 graph-propagated rows retain that evidence status; no kinetic-equivalence conclusion. |
| 7. AI 未静默最终确定任何降维决策；研究者审核项均保留。 | `docs/reduction/reduction_decisions.csv`; `docs/reduction/human_reduction_review.md`; `docs/reduction/species_information_contract_summary.md`; `docs/reduction/species_information_contract_detailed.md`; `docs/reduction/human_audit_sync_20260930.md` | Species verifier exit 0; approved summary/detailed/source sets independently agree at 42/57/91/22/29; all 968 kinetic decisions PENDING; 96 process boxes empty, zero selected. | PASS | Information retention is human approved; KEEP/LUMP/QSSA/CHEMOSTAT/DROP/effective kinetics remain separate pending choices. |
| 8. 候选减化核心的状态、反应、资源与不可恢复量已形成结构文档，无验证宣称。 | `docs/reduction/candidate_core_v0.md` | Read complete candidate proposal and source mapping: STRUCTURAL_PROPOSAL_ONLY / HUMAN_REVIEW_REQUIRED; states, resource obligations and irreversible information loss are documented. | PASS | About 42–70 channels is an engineering estimate; PURE_reduced_core remains NOT_VALIDATED and unconstructed as a formal accepted model. |
| 9. 渗透颗粒代理与离子强度所需物种、浓度、电荷/质子化/Mg 结合信息及缺口均被映射；资料不全不发布定量离子强度。 | `docs/pnas2017/chemical_ledger.md`; `models/pnas2017_full_reference/audit/species_properties.csv`; `models/pnas2017_full_reference/audit/reaction_balance_audit.csv`; `docs/visualization/visualization_plan.md` | All 241 formula/charge/protonation cells are blank and unresolved; units explicitly inferred; all 968 ionic statuses unavailable due to absent charge/protonation/Mg metadata; 29 terminal sinks have zero source consumption and cumulative accounting obligations. | PASS | No quantitative full-system ionic strength or validated osmotic pressure is published; authoritative formulas, charges, Mg binding and absolute units remain open. |
| 10. 可视化数据契约草案通过原始 SBML species/reaction ID 连接视图与来源。 | `docs/visualization/visualization_plan.md`; `models/pnas2017_full_reference/audit/species.csv`; `models/pnas2017_full_reference/audit/reactions.csv`; `docs/reduction/reduction_decisions.csv` | Inspected original species/reaction ID, source SHA, module-local IDs, trajectory/flux/reduction mapping and freshness requirements; 241/968 source-key table coverage verified. | PASS | This is a data-contract draft and derived navigation graph; scientific grouping differs from display grouping, and no finished UI is claimed. |

## Annotation, approved species information and kinetic boundary

Current v2 annotation covers 968/968 source reactions exactly once: DIRECT_CHEMISTRY 492; GRAPH_PROPAGATED 50; HUMAN_REVIEW_REQUIRED 0; REFERENCE_DISABLED 420; SHARED_JUNCTION 6. Unresolved/live functional-review rows are zero. There are 35 active families plus RFAM_DEG. Preserved v0/v1 remain versioned evidence; their provisional text is not current v2 status.

Approved summary/detailed species tables and source inventories independently agree exactly once on all 241 IDs: I=42, II-A=57, II-B=91, III=22, C=29. Class I protects output, not necessarily an independent ODE coordinate; II-A permits future reconstruction in principle without proving QSSA; II-B retains declared occupancy/pools; III retains aggregate elongation/resource information; C retains cumulative losses. The 29 C sinks have no source consumption reactions. No factual inconsistency was found or classification reopened.

ATP/ADP/AMP, GTP/GDP/GMP, PO4/PPi, CP/Cr, Gly/Met/fMet, charged/uncharged/peptidyl tRNAs, ribosomes, factors, synthetases, regeneration enzymes, mRNA and peptide remain distinct. All 968 free-resource/particle event deltas agree with inventory stoichiometry. All 241 formula/charge/protonation cells remain unknown; unit scale remains inferred; all 968 ionic-strength statuses remain unavailable because charge/protonation/Mg metadata are absent.

All 968 reaction decisions remain `PENDING` (candidate KEEP 202, LUMP_CANDIDATE 378, DROP_CANDIDATE 388); non-KEEP candidates require human review. All 96 boxes across 16 process cards remain empty. Functional review completion and species information approval do not approve kinetics, QSSA, lumping, fast equilibrium, deletion or chemostats. Candidate core v0 remains `STRUCTURAL_PROPOSAL_ONLY / HUMAN_REVIEW_REQUIRED`; its roughly 42–70 channels are an engineering estimate.

## Fresh execution versus verified preserved execution

The exact main reference runner was copied with five verified main input blobs to an outside-repository execution sandbox and run with `--prepare-only`: fresh deterministic normalization/author overlay, exit 0, no RoadRunner trajectory generated. Exact main `run_pnas2017_simbiology.m` was freshly executed there against the verified effective input using MATLAB 25.2.0.3177638 (R2025b Update 5), SimBiology `ode15s` (toolbox version was not returned by the probe): 241 species/968 reactions, 435 adaptive time points, 1000 s free `Pept0003 = 5.1645826540185835`; all 968 rate-dimension warnings retained.

Fresh `--prepare-only` output retains a legacy runner metadata template referring to S28 as missing. That generated wording is classified as stale template metadata, not a current source gap: the registered S28 file is present, size/hash verified and all seven workbook sheets read. The runner was not edited during the earlier diagnostic rerun or this closure task.

The preserved RoadRunner 2.10.0 trajectory, source/effective-input/run-manifest hashes were verified; its 1000 s free `Pept0003 = 5.164478733656283` is **preserved execution**, not a fresh run. Current libSBML and RoadRunner installations are in incompatible separate Python environments; an optional disposable dependency-target attempt failed TLS (exit 1). The registered trajectory runner was not freshly executed.

The exact main comparison script ran freshly (exit 0), comparing preserved RoadRunner to fresh SimBiology; endpoint absolute difference is `0.00010392036229678325`. No preregistered numerical equivalence threshold exists. These are numerical integrity diagnostics, not experimental validation, S28 comparison or reduced-model approval. S28 seven-sheet format/readability was verified; pointwise mapping/comparison was not performed.

## Current closure checks

Provenance synchronization commit: `4e63d9ef6ec1c623c485bd4553362c27114a6203`. The checked source/evidence basis remains the starting main `678fcb709324142454fd7a80cb6185c64b900510`.

All six commands ran from the dedicated main worktree after applying the unchanged audited patch; every exit code is 0.

| Command | Exit | Result |
| --- | ---: | --- |
| `python scripts/verify_pnas2017_artifacts.py` | 0 | 241/968/26 coverage; 968 pending decisions; 16 review cards |
| `python scripts/verify_pnas2017_integration.py` | 0 | 11 PASS / 0 FAIL |
| `python scripts/verify_reaction_level_annotation.py` | 0 | Source/annotation contract checks PASS; no kinetic validation |
| `python scripts/verify_reaction_level_annotation_v2.py` | 0 | Source/annotation contract checks PASS; no kinetic validation |
| `python scripts/verify_reaction_level_contract.py` | 0 | Source/annotation contract checks PASS; no kinetic validation |
| `python scripts/verify_species_information_contract.py` | 0 | 241 species; classes 42/57/91/22/29 |

The applied files match the previously audited patch SHA-256 `b338b6d580f5f17c394e14f0168e41bfadf81e1a3dccb34760120428218bea5a`. The historical render manifest remains unchanged. Current human review bytes match only the approved `d5874dec` transition; support contract text matches `678fcb7`. All six existing unauthorized-change mutation cases were rejected.

An optional old pre-application helper was invoked after patch application and refused to apply an already-applied patch (exit 1); this tooling-state error is preserved in `applied_repair_checks.json`. The state-appropriate `git apply --reverse --check` passes. This was not a failure of the six required official verifiers.

The independent source/ledger/contract checks preserve 33 acquired source hashes and all 968 pending decisions, with 96 process boxes empty and zero selected. No source model, author input, species classification or scientific acceptance threshold changed.

## Remaining scientific work

- S28 observable mapping and pointwise comparison; S27's source/model relation; separate full SI document acquisition/status.
- Authoritative absolute chemical units; complex formulas/bound moieties; charge/protonation and Mg-binding conventions.
- Quantitative whole-system ionic strength and validated osmotic pressure; represented-particle proxy remains qualified.
- Human process/reaction KEEP/LUMP/QSSA/CHEMOSTAT/DROP/effective-kinetics choices, future validity domains and full-versus-reduced validation.
- Construction and validation of `PURE_reduced_core`; old Mavelli D8–D10 and old G2 remain non-authoritative for PNAS.

No listed scientific open item is completed by G1 closure. G2 is not passed or newly defined; old Mavelli D8–D10 remain non-authoritative for PNAS.

## Preserved diagnostic history and current status

The initial 2026-10-02 artifacts exit 1 and integration 10 PASS / 1 FAIL are preserved as earlier outcomes. Both concerned `human_reduction_review.md` after the already approved `d5874dec` documentation sync: current SHA `b32dcbfa155be5d77411691889e67da7a6a89c7d87ba1406171e74db6c95c2d8`, old registered SHA `ef9f617cf9121200c52c14f00f17c86d96e48793377464b89414a631e75c1de7`. No historical result, manifest or scientific decision was rewritten to force a pass.

The original [rerun evidence archive](g1_pnas_evidence_20261002.zip) remains unchanged. The [closure evidence archive](g1_pnas_closure_evidence_20261002.zip) preserves the exact preceding report/gate/verification bytes and records successful current checks. The [gate JSON](g1_pnas_gate_20261002.json) and [verification JSON](g1_pnas_verification_20261002.json) distinguish current closure from these historical diagnostics. The 2026-09-27 [BLOCKED payload](g1_pnas_report_20260927_blocked.md), dated missing-source notes, versioned v0/v1 annotation and integration packet remain historical.

README and tasklist now state the dated G1 closure without changing the exact ten acceptance criteria. This task adds an [aminoacylation QSSA quick reference](../reduction/aminoacylation_qssa_quick_reference.md) for later human review; it makes no KEEP/LUMP/QSSA/CHEMOSTAT/DROP decision. Open PR #3/#4 are untouched.

NEXT ACTIVE SCIENTIFIC TASK:
human review of process/reaction-level reduction choices in
`docs/reduction/human_reduction_review.md`. That review is not started by this task.
