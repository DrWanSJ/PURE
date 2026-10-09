# B0 researcher formal signoff and publication authorization - 2026-10-09

Current researcher-signed scientific status: **B0_FORMALLY_ACCEPTED_LIMITED_SCOPE**.
Authority: the researcher's explicit formal confirmation in this chat. Codex
records that decision; the signature is supplied by the researcher, separately
from automated engineering evidence.

The researcher formally accepts W1 (GlyRS -> EF-Tu -> ribosome binding
interface), W2 (MetRS -> MTF formylation, competing binding entries, product
release and enzyme recovery), and W3 (MTF -> IF2-GTP binding interface), within
original-SBML-supported multi-carrier structural handoffs, exact net
stoichiometry and explicitly declared external supplies.

The accepted scope retains competition for one shared MettRNAfMetCAU pool
through 0420/0422 and 0288, and both IF2 directions 0449/0450 (reference k1 = 40
each). Full complex composition remains **INFERRED**. Kinetics, actual flux
and a reduced model remain **NOT_VALIDATED**. The FD documentation correction
and Matsuura 2017 original-source citation are included in the historical
B0-2 record below.

The researcher explicitly authorizes one commit and a normal push of the
exact 20 files listed in the machine-readable record to
codex/energy-cycles-v1. **phase_b1_authorized = false**. Work stops after
publication.

The conditional review JSON and the executed A-G report remain byte unchanged.
Their earlier pending-signoff and no-push fields describe historical states;
the current human signoff and Git authorization are recorded separately here.
The original conditional-review Markdown is preserved verbatim below.

## Machine-readable current researcher decision

~~~json
{
  "schema": "B0_RESEARCHER_FORMAL_SIGNOFF_V1",
  "authority": "EXPLICIT_USER_SUPPLIED_RESEARCHER_FORMAL_CONFIRMATION_IN_THIS_CHAT",
  "signoff_date": "2026-10-09",
  "scientific_status": "B0_FORMALLY_ACCEPTED_LIMITED_SCOPE",
  "phase_b1_authorized": false,
  "accepted_scope": {
    "W1": "GlyRS -> EF-Tu -> ribosome binding interface; explicit external supplies; no completed elongation claim",
    "W2": "MetRS -> MTF formylation, both competing binding entries, product release and enzyme recovery",
    "W3": "MTF -> IF2-GTP binding interface; no completed initiation claim",
    "handoffs": "Original-SBML-supported multi-carrier structural handoffs and exact net stoichiometry",
    "shared_met_trna_pool": "Retain competition among re0000000420, re0000000422 and re0000000288 for one MettRNAfMetCAU pool",
    "if2_directionality": "Retain re0000000449 and re0000000450, each reference k1 = 40; no irreversible binding claim",
    "full_complex_composition": "INFERRED",
    "kinetics": "NOT_VALIDATED",
    "actual_flux": "NOT_VALIDATED",
    "reduced_model": "NOT_VALIDATED"
  },
  "historical_review": {
    "path": "docs/reduction/pathways/phase_b0_b0_2_review_record.json",
    "sha256": "2ff933a30b3e768b3fa2420ed7b46d25e4ee30048dab968772d4029968662372",
    "scientific_status": "B0_2_CONDITIONALLY_ACCEPTED",
    "preservation": "BYTE_UNCHANGED_HISTORICAL_RECORD_NOT_CURRENT_AUTHORIZATION",
    "original_markdown_sha256": "868da6fd232cca5d33cdda82fbc5c03824bacd5ab6f98df25d1e13edaae9f9ca"
  },
  "automated_execution_evidence": {
    "path": "docs/reduction/pathways/phase_b0_validation_report.json",
    "sha256": "2fd0ed09143748c3f7c9df4e78de34b891dd9a9d21ee18e7e628bb460dd37563",
    "gates": {
      "A": "PASS",
      "B": "PASS",
      "C": "PASS",
      "D": "PASS",
      "E": "PASS",
      "F": "PASS",
      "G": "PASS"
    },
    "preservation": "BYTE_UNCHANGED_EXECUTED_REPORT_SEPARATE_FROM_RESEARCHER_SIGNOFF",
    "authority": "CODEX_EXECUTED_TEST_REPORT_NOT_RESEARCHER_SIGNATURE"
  },
  "publication_authorization": {
    "machine": "sean",
    "repository": "C:\\Users\\sean\\Desktop\\GUV",
    "origin": "https://github.com/DrWanSJ/PURE.git",
    "branch": "codex/energy-cycles-v1",
    "commit_push_authorized": true,
    "mode": "ONE_COMMIT_THEN_NORMAL_PUSH",
    "commit_message": "docs(reduction): sign off limited Phase B0 and publish verified handoff witnesses",
    "parent_head": "14c61055775421e9f30342507cc4fffdceed1607",
    "file_count": 20,
    "allowed_files": [
      "docs/reduction/pathways/phase_a_human_signoff_2026-10-09.md",
      "docs/reduction/pathways/phase_b0_b0_1_pre_b0_2_2026-10-09.zip",
      "docs/reduction/pathways/phase_b0_b0_2_review_record.json",
      "docs/reduction/pathways/phase_b0_b0_2_review_record.md",
      "docs/reduction/pathways/phase_b0_execution_log.txt",
      "docs/reduction/pathways/phase_b0_failure_evidence.jsonl",
      "docs/reduction/pathways/phase_b0_handoff_witnesses.json",
      "docs/reduction/pathways/phase_b0_handoff_witnesses.md",
      "docs/reduction/pathways/phase_b0_html_regression.json",
      "docs/reduction/pathways/phase_b0_independent_verification.json",
      "docs/reduction/pathways/phase_b0_multicarrier_protocol.md",
      "docs/reduction/pathways/phase_b0_negative_controls.json",
      "docs/reduction/pathways/phase_b0_phase_a_regression.json",
      "docs/reduction/pathways/phase_b0_review.md",
      "docs/reduction/pathways/phase_b0_source_baseline.json",
      "docs/reduction/pathways/phase_b0_validation_report.json",
      "scripts/pathways/phase_b0/build_phase_b0_witnesses.py",
      "scripts/pathways/phase_b0/run_phase_b0_validation.py",
      "scripts/pathways/phase_b0/test_phase_b0_negative_controls.py",
      "scripts/pathways/phase_b0/verify_phase_b0_witnesses.py"
    ],
    "commit_sha_record": "Final publication report and Git history; the new commit cannot embed its own SHA",
    "stop_after_publication": true
  }
}
~~~


## Publication preflight and post-signature checks - separate automated evidence

These are Codex-executed publication checks, not the researcher's scientific
signature. The full prior A-G execution report is unchanged and remains the
basis for the completed regression and reproducibility results. The two
post-signature checks were actually rerun with reports in a temporary
directory; their outcomes are retained here without replacing frozen reports.

~~~json
{
  "status": "PASS",
  "check_date": "2026-10-09",
  "check_scope": "Post-signature metadata verification; prior A-G execution report preserved",
  "independent_verification": {
    "status": "PASS",
    "witness_events": {
      "W1": 10,
      "W2": 13,
      "W2-ALT": 13,
      "W2-MTF": 5,
      "W3": 14
    }
  },
  "negative_controls": {
    "status": "PASS",
    "required_passed": 12,
    "total_passed": 18,
    "failed": 0,
    "supplemental_positive_passed": 2
  },
  "protected_tracked_files": {
    "status": "PASS",
    "unchanged": 2342,
    "changed": 0
  },
  "executions": [
    {
      "entrypoint": "scripts/pathways/phase_b0/verify_phase_b0_witnesses.py",
      "exit_code": 0,
      "stdout": "{\"status\": \"PASS\", \"witness_events\": {\"W1\": 10, \"W2\": 13, \"W3\": 14, \"W2-MTF\": 5, \"W2-ALT\": 13}, \"error\": null}",
      "stderr": ""
    },
    {
      "entrypoint": "scripts/pathways/phase_b0/test_phase_b0_negative_controls.py",
      "exit_code": 0,
      "stdout": "{\"status\": \"PASS\", \"required_controls_run\": 12, \"required_controls_passed\": 12, \"required_controls_failed\": 0, \"controls_run\": 18, \"controls_passed\": 18, \"controls_failed\": 0}",
      "stderr": ""
    }
  ],
  "historical_evidence_and_scientific_payload": "18 other authorized files byte unchanged",
  "publication_preflight": {
    "origin": "https://github.com/DrWanSJ/PURE.git",
    "branch": "codex/energy-cycles-v1",
    "head": "14c61055775421e9f30342507cc4fffdceed1607",
    "upstream_ahead": 0,
    "upstream_behind": 0,
    "allowed_new_files": 20,
    "unknown_files": 0,
    "tracked_modifications": 0,
    "zip_crc_and_manifest_hashes": "PASS",
    "zip_original_b0_1_files": 17,
    "zip_total_entries": 18,
    "credential_pattern_scan": "PASS_NO_FINDINGS"
  }
}
~~~

---

## Historical B0-2 conditional review - original text preserved

# B0-2 researcher review record — 2026-10-09

Authority: **user-supplied researcher review** in this chat. Codex records the
judgments below and checks the requested source/document correction. It does
not supply a researcher signature. Current status: **B0_2_CONDITIONALLY_ACCEPTED**;
formal signoff awaits final researcher confirmation. Commit/push authorization
and Phase B1 implementation authorization remain **false**.

| Item | Researcher's judgment | Accepted scope |
|---|---|---|
| 1. W1 independent EF-Tu/ribosome interface | 接受 | Explicit external supplies; binding endpoint; complete elongation not required |
| 2. MTF binding entries | 通过 | Source-supported 0418/0422 and 0420/0424; correct shared species |
| 3. MTF formylation, release and recovery | 通过，需修订文档 | 0426/0428/0434 accepted; add FD identity and original citation |
| 4. W3 IF2 interface | 建议通过 | Exact required reactants; no completed initiation; both directions retained |
| 5. Cross-complex identity rules | 限定接受 | Exact source-supported species handoffs accepted; full composition remains INFERRED |

The researcher's overall judgment is conditional acceptance within source
stoichiometry, catalyst recovery and finite multi-carrier structural handoffs,
with no blocking scientific error found. The researcher explicitly states that
the engineering conclusions currently rely on Codex's execution reports; the
unpublished B0 code has not been independently rerun by the researcher.
Phase A A1–A7 review is already recorded and need not be repeated.

## FD correction and original source

**FD is 10-formyltetrahydrofolate (10-甲酰四氢叶酸)**. Matsuura et al.,
*Reaction dynamics analysis of a reconstituted Escherichia coli protein
translation system by computational modeling*, PNAS 2017;114(8):E1336–E1344,
DOI [10.1073/pnas.1615351114](https://doi.org/10.1073/pnas.1615351114), explicitly
defines it in the inline SI Results, Model Construction subsection **“Model
construction for formylation of initiator tRNA”**. The short identifying phrase
is “transfer of a formyl group of 10-formyltetrahydrofolate (FD)”.
[Original article and SI text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/).

That subsection describes MTF-mediated transfer to the amino group of
Met-tRNAfMet and dissociation of the resulting complex containing formylated
initiator tRNA and tetrahydrofolate, with the model named FMet_tRNASynthesis
and [Dataset S21](https://pmc.ncbi.nlm.nih.gov/articles/PMC5338406/#d35e1396).
This resolves the earlier documentation question about FD's biochemical
identity. It does not verify every composite's full molecular composition,
trajectory flux, kinetic dominance or a reduced model. Original SBML IDs,
equations and parameters remain unchanged; no chemical formula, protonation,
ionic or thermodynamic parameter is added.

The already frozen main-article PDF remains unchanged (SHA-256
`e340ba829f87121e723059aebecc56c342c37c2cc4687692d1447f16b38f2a4e`). The specific
FD definition above was read in the online article's inline SI text; the main
PDF fingerprint is provenance context, not a claim that it contains that SI
passage. The machine record retains the DOI, URL, section and retrieval scope.

## IF2 binding retains both reference-enabled directions

Fresh canonical SBML/author-CSV reading confirms:

| Original ID | Complete source equation | Reference k1 |
|---|---|---:|
| re0000000449 | IF2_GTP + fMettRNAfMetCAU -> IF2_GTP_fMettRNAfMetCAU | 40 |
| re0000000450 | IF2_GTP_fMettRNAfMetCAU -> IF2_GTP + fMettRNAfMetCAU | 40 |

W3 fires 0449 once and does not automatically fire its inverse. Both source
directions are parameter-enabled. Equal numeric parameter values for
association and dissociation do not establish equilibrium, and the forward
step cannot be treated as irreversible under these reference parameters.

## Shared Met-tRNA pool: mandatory constraint for any later B1

| Original ID | Complete source equation | Reference k1 |
|---|---|---:|
| re0000000420 | MTF + MettRNAfMetCAU -> MTF_MettRNAfMetCAU | 2000 |
| re0000000422 | MTF_FD + MettRNAfMetCAU -> MTF_FD_MettRNAfMetCAU | 2000 |
| re0000000288 | EFTu_GTP + MettRNAfMetCAU -> EFTu_GTP_MettRNAfMetCAU | 1.5 |
| re0000000289 | EFTu_GTP_MettRNAfMetCAU -> EFTu_GTP + MettRNAfMetCAU | 0.0453 |

0420/0422 and 0288 consume **the same source species MettRNAfMetCAU pool**.
Later full-network reconstruction must retain their competing exits, exact
co-reactants and inverses. It must not give each module an independent copy
of the same finite substrate or simply add isolated B0 net reactions. These
records add a source-derived future constraint; no B1 reconstruction is run.

Ban et al., *Elucidating the Bell-Shaped Dependence of Protein Translation
Activity on EF-Tu Concentration in a Reconstituted Cell-Free System Using a
Mechanistic Model*, ACS Synthetic Biology 2026;15(6):2675–2683, DOI
[10.1021/acssynbio.6c00333](https://doi.org/10.1021/acssynbio.6c00333), reports a
model-based explanation involving sequestration of unformylated initiator
Met-tRNA in EF-Tu/GTP complexes. Its abstract also reports experimental
confirmation of the predicted response to additional tRNAfMet and MTF.
This supports retaining competition for a limited initiation resource; it
does not independently validate this repository's rates or trajectories.
[Publisher abstract](https://pubs.acs.org/asbcd6/article/15/6/2675/5161912/Elucidating-the-Bell-Shaped-Dependence-of-Protein).

Coverage: publisher metadata and abstract were read, not the full 2026 paper.
Online publication was 2026-05-28; issue publication was 2026-06-19. A PubMed
retrieval failed and the publisher abstract supplied the evidence; this access
failure is retained in the JSON record.

## Evidence and remaining authorization

The complete pre-revision B0-1 files and their SHA-256 manifest are preserved
in `phase_b0_b0_1_pre_b0_2_2026-10-09.zip`. The current corrected protocol,
witness documentation and reports link this review record. Actual rerun
results are in `phase_b0_validation_report.json` and the append-only execution
log. Final researcher signoff and explicit commit/push approval remain the
next checkpoint. Phase B1 still needs separate scope authorization.
