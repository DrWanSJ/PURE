# Current B0 researcher signoff - 2026-10-09

**B0_FORMALLY_ACCEPTED_LIMITED_SCOPE** is the current researcher-signed
scientific status, supplied by the researcher's explicit confirmation.
The current [formal decision and exact publication allowlist](phase_b0_b0_2_review_record.md)
is separate from the executed A-G evidence below.

W1/W2/W3 source-supported structural handoffs, exact net stoichiometry,
catalyst recovery and declared external supplies are accepted in the stated
limited scope. Shared Met-tRNA competition and both IF2 reference directions
remain constraints. Full complex composition remains **INFERRED**; kinetics,
actual flux and reduced-model validation are not established.

Publication authorization covers exactly 20 B0 files, one commit and a normal
push to codex/energy-cycles-v1. **phase_b1_authorized = false**. Stop after
publication. The historical executed-review text below is preserved verbatim,
including its earlier conditional scientific status and review hold. The
automatic report JSON, source hashes and prior execution logs are unchanged.


Post-signature publication checks reran the independent verifier and negative
controls: all five witnesses passed; required negatives 12/12, total negatives
18/18 and supplemental positives 2/2 passed. All 2342 protected tracked files
remain byte unchanged. The [separate publication-check record](phase_b0_b0_2_review_record.md)
retains the executed outcomes. Signature metadata did not alter scientific
payload, source files, prior execution reports or failure evidence.

---

## Historical executed review - original text preserved

# Phase B0 executed review — B0-2 source/document correction and revalidation

User-supplied scientific status: **B0_2_CONDITIONALLY_ACCEPTED**. Formal signoff: **PENDING_FINAL_RESEARCHER_CONFIRMATION**. Phase B1 authorized: **false**.

Execution: `COMPLETED`; overall engineering: `PASS`. These results certify conditional finite source structure only.

## Repository and review hold

Machine: sean. Repository: `C:\Users\sean\Desktop\GUV`. Origin: `https://github.com/DrWanSJ/PURE.git`. Branch: `codex/energy-cycles-v1`.

Starting HEAD and ending HEAD: `14c61055775421e9f30342507cc4fffdceed1607` / `14c61055775421e9f30342507cc4fffdceed1607`. Original B0-1 startup fetch confirmed clean tree and upstream 0/0. Commit/push: `NOT_ATTEMPTED — B0-1 review hold`. This B0-2 run continues the identified local B0 work.

## FD identity correction and original source

**FD is 10-formyltetrahydrofolate (10-甲酰四氢叶酸).** Matsuura et al. 2017, PNAS 114(8):E1336–E1344, DOI [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114), explicitly identifies it in inline SI Results / Model Construction / **Model construction for formylation of initiator tRNA**, referring to FMet_tRNASynthesis and Dataset S21. [Original article and SI text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/).

The publication describes MTF transferring the formyl group to Met-tRNAfMet and dissociation of the resulting complex containing formylated initiator tRNA and tetrahydrofolate. The earlier FD identity documentation gap is resolved. Full complex composition and real kinetic behavior remain unverified; source species, coefficients and parameters stay unchanged.

## IF2 directionality and future shared-pool constraint

Fresh canonical/source-parameter verification confirms `re0000000449` and `re0000000450` both have reference k1 = 40; both directions remain parameter-enabled. W3 fires 0449 only, does not complete initiation and does not establish irreversible binding or equilibrium.

The MTF entrances `re0000000420/0422` and EF-Tu entrance `re0000000288` consume the same original `MettRNAfMetCAU` pool. Any separately authorized B1 must preserve the competing exits and inverses; isolated B0 nets cannot be combined using duplicated Met-tRNA supplies. No B1 implementation was executed.

Ban et al. 2026, ACS Synthetic Biology 15(6):2675–2683, [DOI 10.1021/acssynbio.6c00333](https://doi.org/10.1021/acssynbio.6c00333), supplies external supporting context for initiator Met-tRNA sequestration by excess EF-Tu. Coverage was publisher metadata and abstract only. Its model explanation and experimentally confirmed supplementation prediction do not validate this repository's kinetic predictions.

The [B0-2 researcher record](phase_b0_b0_2_review_record.md) attributes the conditional decisions to the user. The automated B0-1 contract retains PENDING_HUMAN_REVIEW separately from that user decision. The pre-revision B0-1 package is preserved in phase_b0_b0_1_pre_b0_2_2026-10-09.zip. Codex does not issue a researcher signature.

## Executed gates

| Gate | Status | Executed entrypoint | Evidence |
|---|---|---|---|
| A — Source Integrity | PASS | `python scripts/pathways/phase_b0/verify_phase_b0_witnesses.py` | `phase_b0_independent_verification.json` |
| B — W1 Structural Handoff | PASS | `python scripts/pathways/phase_b0/verify_phase_b0_witnesses.py` | `phase_b0_independent_verification.json` |
| C — W2 Multi-Precursor / Alternative Entry | PASS | `python scripts/pathways/phase_b0/verify_phase_b0_witnesses.py` | `phase_b0_independent_verification.json` |
| D — W3 Formylated-tRNA Handoff | PASS | `python scripts/pathways/phase_b0/verify_phase_b0_witnesses.py` | `phase_b0_independent_verification.json` |
| E — Net Stoichiometry | PASS | `python scripts/pathways/phase_b0/verify_phase_b0_witnesses.py` | `phase_b0_independent_verification.json` |
| F — Negative Controls | PASS | `python scripts/pathways/phase_b0/test_phase_b0_negative_controls.py` | `phase_b0_negative_controls.json` |
| G — Phase A Regression / Preservation | PASS | `python scripts/pathways/verify_pathway_atlas.py; python scripts/pathways/phase_b0/run_phase_b0_validation.py` | `phase_b0_phase_a_regression.json; phase_b0_html_regression.json` |

## Witness results

| Witness | Directed occurrences | Exact structural net | Verification |
|---|---|---|---|
| W1 | 10 | `ATP + EFTu_GTP + Gly + elRS70SAGGU0002_fMet + tRNAGlyGCC -> AMP + PPi + elRS70SAGGU0002_fMet_EFTu_GTP_GlytRNAGlyGCC` | PASS |
| W2 | 13 | `ATP + FD + Met + tRNAfMetCAU -> AMP + PPi + THF + fMettRNAfMetCAU` | PASS |
| W3 | 14 | `ATP + FD + IF2_GTP + Met + tRNAfMetCAU -> AMP + IF2_GTP_fMettRNAfMetCAU + PPi + THF` | PASS |
| W2-MTF | 5 | `FD + MettRNAfMetCAU -> THF + fMettRNAfMetCAU` | PASS |
| W2-ALT | 13 | `ATP + FD + Met + tRNAfMetCAU -> AMP + PPi + THF + fMettRNAfMetCAU` | PASS |

Required negatives: 12 run, 12 passed, 0 failed. All negatives including supplements: 18 run, 18 passed, 0 failed.

| Control | Expected rejection | Actual rejection | Petri enabling | Result |
|---|---|---|---|---|
| N01 | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | PASS |
| N02 | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | PASS |
| N03 | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | PASS |
| N04 | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | PASS |
| N05 | CARRIER_LINEAGE_MISMATCH | CARRIER_LINEAGE_MISMATCH | PASS | PASS |
| N06 | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | PASS |
| N07 | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | PASS |
| N08 | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | MISSING_REQUIRED_INPUT | PASS |
| N09 | SHARED_RESOURCE_NOT_CARRIER | SHARED_RESOURCE_NOT_CARRIER | PASS | PASS |
| N10 | REFERENCE_ACTIVITY_MISMATCH | REFERENCE_ACTIVITY_MISMATCH | PASS | PASS |
| N11 | DUPLICATE_OCCURRENCE | DUPLICATE_OCCURRENCE | MISSING_REQUIRED_INPUT | PASS |
| N12 | SOURCE_COEFFICIENT_MISMATCH | SOURCE_COEFFICIENT_MISMATCH | NOT_APPLICABLE | PASS |
| S01 | NET_STOICHIOMETRY_MISMATCH | NET_STOICHIOMETRY_MISMATCH | PASS | PASS |
| S02 | EVENT_DAG_MISMATCH | EVENT_DAG_MISMATCH | PASS | PASS |
| S03 | FALSE_CYCLE_CLAIM | FALSE_CYCLE_CLAIM | PASS | PASS |
| S04 | TOKEN_PROVENANCE_MISMATCH | TOKEN_PROVENANCE_MISMATCH | PASS | PASS |
| S05 | CATALYST_NOT_RECOVERED | CATALYST_NOT_RECOVERED | PASS | PASS |
| S06 | REQUIRED_CARRIER_HANDOFF_MISSING | REQUIRED_CARRIER_HANDOFF_MISSING | PASS | PASS |

Supplemental positives verify a reordered independent precursor and two genuine MTF cycles with distinct occurrences (each source direction counted twice). N05 is Petri-enabled but rejected for carrier lineage. N09 is Petri-enabled but rejected for a shared-resource carrier claim. All mutations are in memory; none alters source files.

## Independent evidence and preservation

The verifier imports no builder. It reparses original MathML, independent author CSV values and archive bytes, checks exact signed nets, every input and token origin, DAG edges, catalyst recovery, boundary balances, alternative rejoin and reference directions. All five source-bound scenarios are independently checked. The generated witness records retain CANDIDATE_AWAITING_INDEPENDENT_VERIFICATION; executed outcomes live in separate validation reports.

All 2342 pre-existing tracked files are byte-unchanged. Phase A mutation/report writes used temporary copies. Existing HTML regression functions ran read-only with all new reports routed to B0.

Source hashes:

- `docs/reduction/reaction_level_annotation_v2.csv`: `ee2f80a3354199a03d3072464cbc301736afad72fba01e4bfcc499c0525f3335`.
- `models/pnas2017_full_reference/original/fMGG_synthesis.xml`: `dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`.
- `models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv`: `cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465`.
- `references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip`: `beb27ebbd314133fbd83f68dcf8ad2ebe08cb16a1adda170b6b7b408ad355b52`.

Two independent builder runs reproduce both new deterministic witness files and equal delivered SHA-256 values:

- `phase_b0_handoff_witnesses.json`: `f1e2c36dbe782bac4fa02cf9c5d6d45457141b650345753f403339bb4e23e0d7`.
- `phase_b0_handoff_witnesses.md`: `906e2a5cbb16c9b3bd59d54b53152ac3382aa139bd2933cdfd5ca5d082173ce2`.

## Reproduction commands

From the repository root, using the existing Python environment:

```powershell
python scripts/pathways/phase_b0/build_phase_b0_witnesses.py
python scripts/pathways/phase_b0/verify_phase_b0_witnesses.py
python scripts/pathways/phase_b0/test_phase_b0_negative_controls.py
python scripts/pathways/verify_pathway_atlas.py
python scripts/pathways/phase_b0/run_phase_b0_validation.py
```

The final command safely runs Phase A mutation tests in a temporary copy, existing HTML acceptance functions, two B0 builds and preservation checks. Do not run old report-writing mutation/browser entrypoints with default output paths: that would overwrite archived Phase A results. Exact executed temporary paths, raw outputs and exit codes are in phase_b0_execution_log.txt and the regression reports.

## Limitations, failures and unresolved questions

All selected positive directions have nonzero reference parameters; 0427 remains an original zero-parameter reverse in the context appendix. Nonzero k is not measured flux. Finite boundary supplies are explicit conditional assumptions. No full-network availability, complex molecular composition, binding-order dominance, completed elongation/initiation, kinetic feasibility, QSSA, effective-rate law or reduced model is approved.

phase_b0_failure_evidence.jsonl preserves genuine failed attempts. An initial inspection used Windows' default GBK decoding for UTF-8 JSON and failed; it was rerun with explicit UTF-8 without source modification. Any later actual failures are appended with their raw evidence. Expected negative rejections are recorded separately and do not represent failed acceptance gates.

## B0-2 user-supplied researcher decisions

| Item | Researcher's exact judgment | Scope |
|---|---|---|
| 1. W1 independent EF-Tu/ribosome interface | 接受 | Explicit external supply and binding interface; complete elongation not required |
| 2. MTF two binding entries | 通过 | 0418/0422 and 0420/0424 source-supported, correct shared rejoin |
| 3. MTF formylation, product release and enzyme recovery | 通过，需修订文档 | 0426/0428/0434 accepted; identify FD from Matsuura 2017 before final signoff |
| 4. W3 IF2 interface | 建议通过 | 0449 uses IF2_GTP and fMettRNAfMetCAU; no completed initiation; 0449/0450 both reference-enabled |
| 5. Cross-complex molecular identity | 限定接受 | Accept source-supported exact species handoffs; full complex composition remains INFERRED |

The researcher conditionally accepts source stoichiometry, catalyst recovery and finite handoffs. Full complex composition remains INFERRED and real kinetic behavior remains unverified. The researcher explicitly relies on Codex's engineering reports and has not independently rerun the unpublished code. Phase A signoff need not be repeated.

FD correction status: `DOCUMENTED_AND_REVALIDATED`.


## Final signoff and delivery checkpoint

- Preserve the original B0-1 snapshot and corrected B0-2 source/review records with actual rerun evidence.
- Obtain final researcher confirmation of bounded signoff and explicit authorization before commit/push; the earlier review hold remains active.
- Obtain separate scope authorization before Phase B1, retaining the shared Met-tRNA competition constraint.

B0 stops here. No Phase B1, commit or push was attempted.
