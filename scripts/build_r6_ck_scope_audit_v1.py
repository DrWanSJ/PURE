"""Additive R6 requirement audit; intentionally performs no numerical campaign."""
from pathlib import Path
import csv
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/reduction/r6_ck_validation'
DOC = ROOT / 'docs/reduction'
DECISION = 'GROSS_FLUX_REQUIREMENT_AMBIGUOUS_HUMAN_DECISION_REQUIRED'
FAST = ['re0000000332', 're0000000333', 're0000000336', 're0000000337']
CONDITIONS = ['R3_BASE', 'R3_GLYRS_LOW', 'R3_GLYRS_HIGH', 'R3_METRS_LOW',
              'R3_METRS_HIGH', 'R3_GLY_LOW', 'R3_MET_LOW', 'R3_TRNA_LOW', 'R3_ATP_LOW']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False,
                                      allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def write_csv(name, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def requirement(identifier, source, first, last, question, classes, gross, role, rationale,
                confidence='HIGH', interpretation='INFERRED'):
    lines = (ROOT / source).read_text(encoding='utf-8').splitlines()
    assert 1 <= first <= last <= len(lines)
    excerpt = '\n'.join(lines[first - 1:last])
    return dict(requirement_id=identifier, source_file=source, source_location=f'L{first}-L{last}',
                source_line_start=first, source_line_end=last, scientific_question=question,
                required_observable_class=classes, gross_microscopic_flux_required=gross,
                rationale=rationale, confidence=confidence, evidence_status=interpretation,
                requirement_vocabulary='R6_AUDIT_A_STATE_B_INVENTORY_C_CONSERVATION_D_NET_E_NET_EXTENT_F_FORWARD_G_REVERSE_H_GROSS_EXTENT',
                decision_role=role, source_sha256=sha(ROOT / source),
                excerpt_sha256=hashlib.sha256(excerpt.encode('utf-8')).hexdigest(),
                source_excerpt=excerpt)


def build():
    assert OUT.is_dir(), 'Take pre-R6 snapshot before running builder'
    assert json.loads((OUT / 'input_provenance.json').read_text(encoding='utf-8'))['new_decisive_comparisons_run'] is False
    # Phase-1 outputs and an immutable hash receipt precede the audit closeout.
    request_path = Path(json.loads((OUT / 'input_provenance.json').read_text(encoding='utf-8'))['request_file'])
    request_copy = OUT / 'human_request.txt'
    if request_copy.exists():
        assert request_copy.read_bytes() == request_path.read_bytes()
    else:
        request_copy.write_bytes(request_path.read_bytes())
    scope = dict(schema='R6_CK_CANDIDATE_DEFINITION_V1', candidate='CK_PARTIAL_EQUILIBRIUM_V1',
                 approximation='RAPID_EQUILIBRIUM / PARTIAL_EQUILIBRIUM', fast_reaction_ids=FAST,
                 nonfast_dynamic_reaction_count=964, source_provenance_reaction_count=968,
                 retained_slow_coordinate_count=212, source_general_law_count=27,
                 reconstructed_state_count=241, dynamic_fast_totals=['T0', 'T1', 'B'],
                 algebraically_affected_states=['CK', 'CK_ADP', 'CP', 'CK_CP', 'CK_CP_ADP'],
                 physical_root='p+T0*p/(500+p)+T1*p/(500+p)-B=0; 0<=p<=B',
                 source_kinetics_unchanged=True, fitted_parameters=[], initial_condition_fitting=False,
                 clipping=False, time_shift=False, source_trajectory_projection=False,
                 canonical_reaction_deletion=False, promotion=False,
                 implementation_source='scripts/r5_ck_partial_equilibrium_runtime_v1.py',
                 implementation_sha256=sha(ROOT / 'scripts/r5_ck_partial_equilibrium_runtime_v1.py'))
    write_json('candidate_definition.json', scope)
    startup = json.loads((ROOT / 'results/reduction/r5_mechanism_first/ck/initial_layer_definition.json').read_text(encoding='utf-8'))
    startup.update(schema='R6_FROZEN_R5_INITIAL_LAYER_POLICY_V1',
                   tau_formula='1/(2*p0+1000)', switch_formula='10*eta*tau0',
                   condition_policy='Recompute p0 from unchanged condition initial totals; no tuning',
                   full_startup='retain x_full(t) for 0<=t<=switch',
                   reduced_initial='T*x_full(switch)',
                   switch_jump='disclosed; no continuity fitting',
                   extent_startup='retain or independently integrate full startup; never discard turnover',
                   windows=['FULL_WINDOW', 'POST_INITIAL_LAYER', 'COMPOSITE_OR_HYBRID', 'POST_0P05_DIAGNOSTIC'],
                   full_startup_source_implementation='R5 full solve spans 0..1000 s; dense solution supplies startup',
                   implementation_reproduced_for_new_run=False,
                   source_hashes={p: sha(ROOT / p) for p in [
                       'scripts/r5_ck_eta_scan_v1.py', 'scripts/r5_ck_partial_equilibrium_runtime_v1.py',
                       'docs/reduction/r5_theory_scope_v1.json',
                       'results/reduction/r5_mechanism_first/ck/initial_layer_definition.json']})
    write_json('initial_layer_policy.json', startup)
    classes = [
        ('A', 'Retained slow states / totals', 'T0;T1;B;all212 coordinates;ATP;ADP;Cr;energy species;Pept0003', 'BRANCH_A_MINIMUM_PENDING_NUMERICAL_CONTRACT', '0.01 prospective; semantic equivalence and scales not frozen'),
        ('B', 'Reconstructed fast / altered states', 'CK;CK_ADP;CP;CK_CP;CK_CP_ADP;all241 reconstruction', 'BRANCH_A_MINIMUM_PENDING_NUMERICAL_CONTRACT', '0.01 prospective state level; scales not frozen'),
        ('C', 'Exact SOURCE_GENERAL conservation', '27 exact source laws; distinguish dynamic fast totals', 'BRANCH_A_MINIMUM_PENDING_NUMERICAL_CONTRACT', '1e-8 prospective; independent drift normalization not frozen'),
        ('D', 'Net fast currents', 'j332_333;j336_337;canonical N_qf', 'BRANCH_A_MINIMUM_PENDING_NUMERICAL_CONTRACT', 'DESCRIPTIVE until CK net-current semantics/scales justify gate; 0.05 proposed'),
        ('E', 'Gross directed rates', 'v332;v333;v336;v337', 'HUMAN_SCIENTIFIC_USE_DECISION_REQUIRED', 'NOT_FROZEN; BUT_NOT_VALIDATED'),
        ('F', 'Net cumulative extents', 'integral j332_333;integral j336_337;resource conversion;startup', 'BRANCH_A_MINIMUM_PENDING_NUMERICAL_CONTRACT', 'DESCRIPTIVE until net extent semantics/scales justify gate; 0.01 proposed'),
        ('G', 'Gross directed extents', 'xi332;xi333;xi336;xi337;directed ledger', 'HUMAN_SCIENTIFIC_USE_DECISION_REQUIRED', 'NOT_FROZEN; BUT_NOT_VALIDATED'),
        ('H', 'Initial-layer observables', 'initial occupancy mismatch;fixed switch;switch jump;startup extents', 'BRANCH_A_MINIMUM_PENDING_NUMERICAL_CONTRACT', 'DESCRIPTIVE; no inherited switch-jump threshold asserted'),
    ]
    write_csv('prospective_observable_contract.csv', [dict(contract_class=c, meaning=m, observables=o,
              promotion_requirement=status, gate_status=gate, vocabulary='R5C_VALIDATION_CONTRACT_A_H',
              numerical_uncertainty_policy='<=10% of a justified frozen gate; otherwise unresolved')
              for c, m, o, status, gate in classes])
    registered = ['docs/reduction/r6_ck_validation_authorization_20261007.md',
                  'docs/reduction/r6_ck_observable_scope_preregistration_v1.md'] + [
                  'results/reduction/r6_ck_validation/' + p for p in [
                  'human_request.txt', 'candidate_definition.json', 'initial_layer_policy.json',
                  'prospective_observable_contract.csv', 'historical_snapshot.json', 'input_provenance.json']]
    binding = OUT / 'registration_binding.json'
    hashes = {p: sha(ROOT / p) for p in registered}
    if binding.exists():
        assert json.loads(binding.read_text(encoding='utf-8'))['file_hashes'] == hashes, 'Never overwrite preregistration'
    else:
        write_json('registration_binding.json', dict(schema='R6_CK_REGISTRATION_BINDING_V1',
                   frozen_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   decisive_comparisons_before_freeze=0, file_hashes=hashes,
                   promotion_conjunction_frozen=False,
                   purpose='Freeze audit/candidate/startup; numerical contract waits for gross-use decision'))
    rows = [
        requirement('REQ01', 'README.md', 33, 51, 'What information must the reduced PNAS model preserve?', 'A;B;C;D;E', 'NOT_IMPLIED', 'PURPOSE_NET_RESOURCE', 'Explicit chemical/resource identity and occupancy; no requirement here for each CK binding event.'),
        requirement('REQ02', 'tasklist.md', 9, 21, 'What is the active scientific purpose?', 'A;B;C;D;E', 'NOT_IMPLIED', 'PURPOSE_NET_RESOURCE', 'Detailed translation, resource destinations and human-reviewed information loss; reduced scale is not an acceptance criterion.'),
        requirement('REQ03', 'tasklist.md', 112, 122, 'Which resource and reduction deliverables are required?', 'A;B;C;D;E', 'NOT_IMPLIED', 'PURPOSE_NET_RESOURCE', 'Chemical/resource ledger and candidate loss audit; this does not identify four microscopic binding turnovers as mandatory outputs.'),
        requirement('REQ04', 'tasklist.md', 192, 217, 'Which free and bound resource identities and fuel conversions are protected?', 'A;B;C;D;E', 'NOT_IMPLIED', 'PURPOSE_NET_RESOURCE', 'ATP/ADP/AMP, CP/Cr, tRNA and occupancy remain chemically explicit; distinguish ATP spend from other conversions.'),
        requirement('REQ05', 'tasklist.md', 476, 489, 'Do cumulative flows mean net inventories or every microscopic event?', 'D;E;H', 'AMBIGUOUS', 'LEDGER_SEMANTICS_UNRESOLVED', 'Requires cumulative reaction flows and storage terms, but does not scope mandatory microscopic CK binding extents.', interpretation='AMBIGUOUS'),
        requirement('REQ06', 'tasklist.md', 99, 99, 'Are ATP gross production and consumption required?', 'D;F;G', 'NOT_IMPLIED_FOR_SELECTED_CK_PAIRS', 'ATP_GROSS_NOT_BINDING_TURNOVER', 'ATP gross flows and net flow are explicit. Selected CK fast columns have zero ATP/ADP stoichiometry; catalytic energy-transfer reactions are retained.'),
        requirement('REQ07', 'tasklist.md', 580, 580, 'Does the planned carrier display require gross ATP/GTP turnover?', 'D;F;G', 'NOT_IMPLIED_FOR_SELECTED_CK_PAIRS', 'ATP_GROSS_NOT_BINDING_TURNOVER', 'Carrier gross supply/demand is relevant; binding CP is distinct from ATP generation/consumption.'),
        requirement('REQ08', 'docs/model_card.md', 1, 24, 'Is the GFP model card the active CK use contract?', 'A;C', 'NOT_APPLICABLE', 'LEGACY_MODEL', 'This is the frozen Mavelli B1 model card, a different model and scientific purpose.'),
        requirement('REQ09', 'models/pnas2017_full_reference/README.md', 1, 19, 'Which source product/system is active?', 'A', 'NOT_IMPLIED', 'ACTIVE_SOURCE', 'Active reference is mRNA-directed fMGG; neither mature GFP nor transcription is an active CK observable.'),
        requirement('REQ10', 'docs/pnas2017/reference_reproduction.md', 22, 30, 'Which protein output maps to the source?', 'A', 'NOT_IMPLIED', 'ACTIVE_SOURCE', 'Released Pept0003 is fMGG. Protein agreement does not resolve microscopic turnover needs.'),
        requirement('REQ11', 'docs/reduction/species_information_contract_detailed.md', 32, 44, 'Are CK microstate trajectories independently protected?', 'A;B;C', 'NOT_DECIDED_BY_STATE_CONTRACT', 'STATE_NOT_FLUX_CONTRACT', 'CK/CP/Cr/free carriers are Class I; CK bound intermediates are II-A and reconstructable. No gross-rate promotion decision follows.'),
        requirement('REQ12', 'docs/reduction/human_audit_sync_20260930.md', 14, 23, 'What information-level decisions are human approved?', 'A;B;C;D;E', 'NOT_DECIDED_BY_STATE_CONTRACT', 'STATE_NOT_FLUX_CONTRACT', 'Protected trajectories, occupancy and cumulative loss are approved; no selected-CK turnover mandate is specified.'),
        requirement('REQ13', 'docs/reduction/human_audit_sync_20260930.md', 60, 64, 'Which kinetic validation choices remain open?', 'A;C;D;E;F;G;H', 'AMBIGUOUS', 'KINETIC_SCOPE_OPEN', 'Validity domains, thresholds, trajectory/flux validation and final reduced-core approval remain pending.', interpretation='AMBIGUOUS'),
        requirement('REQ14', 'docs/reduction/reaction_level_contract_summary.md', 143, 154, 'Must exact reverse-pair rewriting retain separate directions?', 'D;F;G', 'EXACT_REWRITE_ONLY', 'EXACT_REWRITE_NOT_APPROXIMATION', 'Explicit retention of forward/reverse/net rates applies to exact representation rewriting; the text distinguishes it from fast equilibrium and QSSA.'),
        requirement('REQ15', 'docs/reduction/reduction_validation_protocol_v0.md', 153, 177, 'What is required by the general validation ledger?', 'A;B;C;D;E;F;G;H', 'AMBIGUOUS', 'LEDGER_SEMANTICS_UNRESOLVED', 'Cumulative extent is mandatory for resource consumption, with xi_j notation; CK gross-binding promotion applicability is not specified.', interpretation='AMBIGUOUS'),
        requirement('REQ16', 'docs/reduction/r3_coupled_validation_protocol_v1.md', 14, 33, 'Did historical validation compare all directed channels?', 'A;C;F;G;H', 'HISTORICAL_DIAGNOSTIC_NOT_SCIENTIFIC_MANDATE', 'HISTORICAL_ONLY', 'Preserves old directed-rate/extent criteria and numerical levels; historical coverage alone cannot decide R6 gross-use scope.'),
        requirement('REQ17', 'docs/reduction/r4_fast_block_preregistration_v1.md', 1, 12, 'Does a former family screen define the current scientific use?', 'A;C;F;G;H', 'HISTORICAL_DIAGNOSTIC_NOT_SCIENTIFIC_MANDATE', 'HISTORICAL_ONLY', 'Historical aminoacylation screen remains fixed; it is not the CK scientific-use contract.'),
        requirement('REQ18', 'docs/reduction/human_reduction_review.md', 451, 472, 'Does the CK process card require promotion-level gross flux accuracy?', 'A;B;C;D;F;G', 'AMBIGUOUS', 'CK_MICROSCOPIC_COMPARISON_NOT_PROMOTION_MANDATE', 'CK-specific microscopic flux comparisons and losses are requested, but mandatory promotion accuracy for 332/333/336/337 is not declared.', interpretation='AMBIGUOUS'),
        requirement('REQ19', 'docs/pnas2017/chemical_ledger.md', 3, 21, 'Does chemical accounting require fast binding turnover or conserved resources?', 'A;B;C;D;E', 'NOT_IMPLIED', 'PURPOSE_NET_RESOURCE', 'Bound carrier moieties and fuel transfer must be accounted for; annotation is not chemical/source authority.'),
        requirement('REQ20', 'docs/reduction/r5c_reduction_observable_contract_v1.md', 1, 21, 'Has R5-C fixed which gross observables are mandatory?', 'A;B;C;D;E;F;G;H', 'AMBIGUOUS', 'EXPLICIT_FUTURE_MANDATORY_DECISION', 'R5-C expressly requires future candidates to declare mandatory status and order; its capability labels are not approval.', interpretation='AMBIGUOUS'),
        requirement('REQ21', 'docs/reduction/r5c_fast_ledger_semantics_v1.md', 3, 19, 'Can exact conservation, net current and gross ledger stand in for each other?', 'B;C;D;E;F;G;H', 'NOT_DECIDED_BY_CAPABILITY', 'CAPABILITY_NOT_REQUIREMENT', 'Four accounting tests and correction orders differ; net identifiability and state accuracy do not decide scientific need.'),
        requirement('REQ22', 'docs/reduction/open_scientific_decisions.md', 10, 17, 'Are future acceptance scope and promotion already fixed?', 'A;B;C;D;E;F;G;H', 'AMBIGUOUS', 'KINETIC_SCOPE_OPEN', 'Ledger scope, kinetic reconstruction, future acceptance and reduced-model identity remain human decisions.', interpretation='AMBIGUOUS'),
        requirement('REQ23', 'docs/reduction/r5_ck_fast_reaction_definition_v1.md', 1, 5, 'Do selected CK reactions convert ATP?', 'B;D;F;G', 'NOT_IMPLIED_FOR_SELECTED_CK_PAIRS', 'ATP_GROSS_NOT_BINDING_TURNOVER', 'The candidate only approximates CP binding/unbinding; 14 other CK-touching reactions remain slow forcing.'),
    ]
    write_csv('scientific_requirement_to_observable.csv', rows)
    write_json('observable_requirement_decision.json', dict(
        decision=DECISION, status='AUDIT_COMPLETE_HUMAN_SCIENTIFIC_USE_DECISION_PENDING',
        decisive_r6_comparisons=0, branch_a_launched=False, branch_b_launched=False,
        recommendation='CK_NOT_READY', promotion=False,
        mandatory_classes_final=None, branch_a_minimum_contract_classes=['A', 'B', 'C', 'D', 'F', 'H'],
        gross_contract_classes_pending=['E', 'G'],
        explicit_selected_ck_gross_promotion_mandate_found=False,
        explicit_selected_ck_gross_accuracy_waiver_found=False,
        supporting_requirement_ids=['REQ05', 'REQ13', 'REQ14', 'REQ15', 'REQ18', 'REQ20', 'REQ22'],
        rule='No explicit selected-CK gross mandate or waiver; CK microscopic comparison and ledger applicability remain unresolved.',
        human_question='For CK 332/333 and 336/337, is accuracy of each forward/reverse binding rate and gross directed extent required for promotion, or may these stay provenance-visible descriptive outputs while state, conservation and net resource observables are mandatory?',
        followup_if_not_required='Freeze a justified full numerical Branch-A contract, verify source reuse, then run nine CK conditions.',
        followup_if_required='Derive first-order corrections and startup matching; test R3_BASE only; no broad campaign.'))
    write_csv('condition_summary.csv', [dict(condition_id=c, status='NOT_RUN_HUMAN_SCOPE_DECISION_REQUIRED',
        mandatory_gates_pass='', state_error='', slow_total_error='', protein_output_error='',
        net_current_error='', net_extent_error='', conservation_drift='',
        failure_origin='NO_NEW_COMPARISON; SCOPE_UNRESOLVED', source_reuse='NOT_ATTEMPTED') for c in CONDITIONS])
    write_json('source_reuse_status.json', dict(status='NOT_ATTEMPTED_AMBIGUITY_STOP',
        selected_trajectories=[], eligible_conditions=CONDITIONS, excluded_conditions=['R3_ADVERSE'],
        prospective_checks=['canonical_hash', 'parameters', 'initial_values', 'condition_definition',
                            'time_grid', 'dense_state_protocol', 'extent_protocol', 'run_manifest_hashes'],
        note='No trajectory reuse certificate or new source-reuse verifier is asserted before a numerical branch.'))
    write_json('evidence_navigation.json', dict(schema='R6_DERIVED_EVIDENCE_NAVIGATION_V1',
        source_authority=False, freshness='Verify source_sha256 and excerpt_sha256 before use',
        nodes=[dict(id=r['requirement_id'], source=r['source_file'], location=r['source_location'],
                    status=r['evidence_status'], confidence=r['confidence'], sha256=r['source_sha256']) for r in rows],
        edges=[dict(source=r['requirement_id'], target=DECISION, relationship=r['decision_role'],
                    status=r['evidence_status']) for r in rows]))
    old_state = json.loads((ROOT / 'results/reduction/r5_mechanism_first/ck/eta_scan_summary.json').read_text(encoding='utf-8'))
    old_current = json.loads((ROOT / 'results/reduction/r5c_corrigendum/ck_fast_current_summary.json').read_text(encoding='utf-8'))
    write_json('historical_context.json', dict(status='FROZEN_HISTORICAL_DESCRIPTIVE_NOT_R6_VALIDATION',
        baseline_hybrid_all241_post_startup_error=old_state['original_eta1_all241_post_startup_max_scaled']['hybrid'],
        baseline_representative_hybrid_net_current_error=old_current['post_0p05_representative_comparison']['hybrid']['max_scaled_error'],
        R6_formal_worst_errors=None, R6_formal_pass_count=None,
        historical_state_summary_sha256=sha(ROOT / 'results/reduction/r5_mechanism_first/ck/eta_scan_summary.json'),
        historical_current_summary_sha256=sha(ROOT / 'results/reduction/r5c_corrigendum/ck_fast_current_summary.json')))
    audit = '''# R6 CK scientific-requirement audit

**Decision: GROSS_FLUX_REQUIREMENT_AMBIGUOUS_HUMAN_DECISION_REQUIRED.**

The scientific-use audit is complete; CK formal validation and first-order baseline validation are both NOT_RUN. The request's Phase 3 requires this stop. The prospective candidate/startup package is frozen, but the final mandatory numerical contract requires a human scientific-use decision. Recommendation: CK_NOT_READY for promotion at this bounded closeout.

The 23-row `scientific_requirement_to_observable.csv` contains source locations, exact excerpts, SHA-256, confidence, interpretation status and the distinction between the audit and validation A–H vocabularies. `evidence_navigation.json` is derived navigation, subordinate to those source records.

## What the evidence establishes

The active use is mRNA-directed fMGG translation with explicit resource identity, inventories, fuel conversion, enzyme occupancy and cumulative resource accounting (REQ01–07, REQ09–12, REQ19). Pept0003 is the released fMGG product. The model card for GFP belongs to the frozen Mavelli benchmark (REQ08); that purpose cannot silently replace the active PNAS use contract.

The human-approved species contract protects free CK, CP, Cr, ATP and ADP trajectories while allowing reconstructable CK bound intermediates. It does not approve any kinetic candidate and does not settle microscopic turnover accuracy (REQ11–13). The exact reverse-pair contract retains forward/reverse kinetics for an exact rewrite, explicitly distinct from fast equilibrium (REQ14).

## Why the two gross-flux branches cannot yet be selected

The general protocol makes cumulative extent mandatory to prevent hidden resource consumption, and writes xi_j for individual reaction integrals (REQ05, REQ15). The CK review card specifically asks for microscopic intermediate flux comparisons and flags forward/reverse information loss (REQ18, `human_reduction_review.md:470–472`). These cannot be silently waived. They also do not explicitly say that accuracy of each of 332/333/336/337 is a mandatory promotion observable. A requested comparison is not automatically a promotion conjunction.

Conversely, resource and occupancy requirements alone do not require counting every fast binding cycle. Gross ATP/GTP production/consumption remains part of the project purpose, but the four candidate fast reactions bind/unbind CP without changing ATP/ADP stoichiometry; catalytic conversion remains dynamic (REQ06–07, REQ23). Whether binding turnover itself is a scientific endpoint is unresolved. R5-C explicitly requires a future mandatory-observable decision (REQ20). Neither past all-968 numerical coverage nor small state error resolves that decision.

There is no explicit CK-specific gross-turnover promotion mandate, and no explicit waiver of its accuracy requirement, in the audited scientific-use contract. The narrow missing decision is whether gross CP-binding rates/extents are essential endpoints or descriptive provenance outputs. This is not a claim that species-level information review is unfinished.

## Reviewable candidate and prospective obligations

`candidate_definition.json` freezes CK_PARTIAL_EQUILIBRIUM_V1, the four fast IDs, unchanged 964 non-fast dynamics, 212 slow coordinates and exact 241-state SOURCE_GENERAL reconstruction. `initial_layer_policy.json` freezes the R5 rule 10*eta*tau0 and retains full startup. The baseline switch is 9.906817032876724e-5 s; its nonzero manifold jump is disclosed, never tuned away.

Under Branch A, the R5-C minimum classes would be A, B, C, D, F and H; E and G would be descriptive/provenance-only and BUT_NOT_VALIDATED. Under Branch B, E/G accuracy would require a derived first-order constitutive reconstruction and startup extent matching, with R3_BASE testing only. These are conditional proposals, not final scientific obligations or approval. New net-current/net-extent thresholds need a semantic and normalization justification before a decisive run; inherited numerical levels alone do not supply it.

## Accounting and numerical status

Exact source-law drift, net stoichiometric accounting, algebraic-state accounting and gross directed-ledger residual remain separate. The independent R6 verifier recomputes canonical structural conservation identities; R6 numerical conservation is NOT_RUN. Historical R5 conservation evidence is retained without extending it across the nine conditions.

0 of 9 conditions executed in R6; the pass count is N/A, not 0/9 failed. R6 worst state, slow-total, protein, current and extent errors are N/A. Historical baseline all241 hybrid post-startup state error is 0.0003383575954227056; R5-C's representative hybrid post-0.05 s net-current scaled error is 0.14712397135760574. These are different historical windows/sample scopes and are not R6 formal results. The current error already cautions against assuming Branch A will pass.

No new numerical failure or domain outcome is assigned. The stopping cause is unresolved scientific-use scope. No first-order reconstruction was run, and no evidence is claimed about gross-rate recovery or startup extent repair. CK is not ready for human promotion review from R6 evidence.

## Required human decision

For CK's CP-binding pairs 332/333 and 336/337, must the reduced candidate accurately preserve each forward/reverse rate and gross directed extent for the intended scientific purpose? Or may those be explicitly descriptive provenance outputs, with states, occupancy, exact conservation and net resource conversion mandatory?

NOT_REQUIRED selects Branch A only after a complete numerical contract and source-reuse verifier are frozen. REQUIRED selects first-order derivation plus R3_BASE testing only. A decision does not promote CK. Historical R3/R4 criteria and outcomes, R5 descriptive status and R5-C corrections remain unchanged. No push, merge or next stage occurred.
'''
    (DOC / 'r6_ck_scientific_requirement_audit.md').write_text(audit, encoding='utf-8', newline='\n')
    closeout = dict(schema='R6_SCOPE_AUDIT_CLOSEOUT_V1', decision=DECISION,
                   closed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   registration_sha256=sha(binding), decisive_comparisons=0, promotion=False,
                   verifier_scope='AMBIGUITY_STOP_PROVENANCE_AND_STRUCTURAL_CHECKS_ONLY')
    write_json('closeout.json', closeout)
    generated = [p for p in OUT.iterdir() if p.is_file() and p.name not in
                 ['manifest.json', 'verification.json', 'verification_binding.json']]
    generated += list(DOC.glob('r6_*.md'))
    generated += [ROOT / 'scripts/build_r6_ck_scope_audit_v1.py', ROOT / 'scripts/verify_r6_ck_validation_v1.py']
    write_json('manifest.json', dict(schema='R6_CK_SCOPE_AUDIT_MANIFEST_V1', decision=DECISION,
        file_hashes={p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(generated)},
        excluded_self_reference=['manifest.json', 'verification.json', 'verification_binding.json'],
        excluded_transients=['__pycache__'], numerical_campaign='NOT_RUN_HUMAN_SCOPE_DECISION_REQUIRED'))
    print(json.dumps(dict(decision=DECISION, requirements=len(rows), conditions_executed=0)))


if __name__ == '__main__':
    build()
