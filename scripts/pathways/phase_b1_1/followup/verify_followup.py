#!/usr/bin/env python3
"""Independent follow-up verifier: never imports follow-up or historical builder."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'docs/reduction/pathways'
sys.path.insert(0, str(ROOT / 'scripts/pathways/phase_b1_1'))
import verify_initiation_witnesses as independent

need = independent.need


def preservation():
    baseline = independent.load(OUT / 'phase_b1_1_followup_baseline.json')
    changed = [p for p, h in baseline['protected_file_hashes'].items() if not (ROOT / p).is_file() or independent.audited.digest(ROOT / p) != h]
    need(not changed, 'PROTECTED_FILE_CHANGED', json.dumps(changed))
    historical = independent.load(ROOT / baseline['historical_report_path'])
    need({g['gate']: g['status'] for g in historical['gates']} == baseline['historical_A_J_gates'] ==
         {g: 'PASS' for g in 'ABCDEFGHIJ'}, 'HISTORICAL_GATE_CHANGED', 'Original A-J')
    return {'status': 'PASS', 'protected_files_unchanged': len(baseline['protected_file_hashes']),
            'tracked_files_unchanged': baseline['existing_tracked_count'], 'historical_B1_1_files_unchanged': baseline['existing_B1_1_untracked_count'],
            'changed_files': changed, 'historical_A_J': baseline['historical_A_J_gates'],
            'historical_report_sha256': baseline['historical_report_sha256']}


def check_followup(data, source):
    """Same material acceptance for the new positive and all follow-up mutations."""
    rx = source['reactions']
    w = data['new_witness']
    result = independent.check_witness(w, source)
    expected_sequence = [f're{n:010d}' for n in (459, 507, 513, 519, 529, 717, 722, 747, 757, 726)]
    need([e['reaction_id'] for e in w['reaction_occurrences']] == expected_sequence, 'IF3_FIRST_SEQUENCE_MISMATCH', 'user-requested independent positive')
    need(w['target_milestone'] == independent.E1, 'WRONG_MILESTONE', 'IF3-first E1')
    need(set(w['initial_marking']) == {independent.INTERFACE, 'IF1', 'IF3', 'RS30S', 'RS50S', 'mRNA'} and
         all(F(n) == 1 for n in w['initial_marking'].values()), 'UNSUPPORTED_BOUNDARY_SUPPLY', 'IF3-first supplies')
    # An independent explicit net expectation supplements the fresh S*w oracle.
    expected_net = {independent.INTERFACE: '-1', 'RS30S': '-1', 'RS50S': '-1', 'mRNA': '-1',
                    'IF2_GDP': '1', 'PO4': '1', independent.E1: '1'}
    need(w['exact_net_stoichiometry'] == expected_net, 'NET_STOICHIOMETRY_MISMATCH', 'IF3-first reference net')
    need({c['species_id'] for c in w['catalyst_recovery_claims']} == {'IF1', 'IF3'}, 'FALSE_RECOVERY_CLAIM', 'IF1/IF3 must be restored')
    for rid, record in data['reactions'].items():
        independent.source_record(rid, record, source)
    primary = set(expected_sequence) | {'re0000000724', 're0000000749', 're0000000001', 're0000000013'}
    inverse = {r for r, q in rx.items() for t in primary if q['reactants'] == rx[t]['products'] and q['products'] == rx[t]['reactants']}
    need(set(data['reactions']) == primary | inverse, 'REVERSE_PAIR_MISMATCH', 'bounded follow-up inventory')
    shared = {'RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA': F(1)}
    need([r['reaction_id'] for r in data['release_branch_inventory']] == ['re0000000724', 're0000000747', 're0000000749'],
         'COMPETITION_INCOMPLETE', 'three GDP exits')
    expected_parameters = {'re0000000724': F('0.0025'), 're0000000747': F(1000), 're0000000749': F(4)}
    for branch in data['release_branch_inventory']:
        r = branch['reaction_id']
        need(rx[r]['reactants'] == shared and independent.audited.fractions(branch['source_states']) == shared and
             independent.audited.fractions(branch['outputs']) == rx[r]['products'], 'CARRIER_LINEAGE_MISMATCH', 'shared GDP state ' + r)
        need(source['parameters'][r] == expected_parameters[r] == F(branch['reference_parameter']) and
             branch['reference_activity'] == 'REFERENCE_ENABLED', 'REFERENCE_ACTIVITY_MISMATCH', r)
        need(branch['reverse_reaction_ids'] == data['reactions'][r]['reverse_reaction_ids'], 'REVERSE_PAIR_MISMATCH', r)
    old = independent.load(OUT / 'phase_b1_1_witnesses.json')
    p1 = next(x for x in old['witnesses'] if x['witness_id'] == 'P1')
    overlay = data['historical_P1_annotation']
    need(overlay['classification'] == 'LEXICOGRAPHIC_STRUCTURAL_WITNESS' and overlay['selected_release_direction'] == 're0000000724' and
         overlay['historical_source_reaction_ids'] == p1['source_reaction_ids'] and 're0000000724' in p1['source_reaction_ids'] and
         overlay['selection_basis'] == 'SORTED_ORIGINAL_ID_TIE_BREAK_IN_SOURCE_MARKING_SEARCH' and
         overlay['kinetic_dominance_claimed'] is False and overlay['measured_path_flux_claimed'] is False,
         'UNSUPPORTED_KINETIC_INTERPRETATION', 'P1 overlay must distinguish ID selection from kinetics')
    need(p1['exact_net_stoichiometry'] == w['exact_net_stoichiometry'], 'NET_STOICHIOMETRY_MISMATCH', 'distinct routes share exact net')
    limits = data['interpretation_limits']
    need(limits['model_0001_context'] == source['annotations']['re0000000001']['level_c_functional_contexts'] == 'ELONG_tRNA_release',
         'INCORRECT_SOURCE_SCOPE', '0001')
    need(rx['re0000000001']['reactants'] == {independent.E1: F(1)} and rx['re0000000001']['products'] ==
         {independent.E2: F(1), 'tRNAfMetCAU': F(1)} and rx['re0000000013']['reactants'].get(independent.E2) == 1,
         'SOURCE_STATE_MISMATCH', 'model E1/E2/0013 interface')
    p7 = next(x for x in old['witnesses'] if x['witness_id'] == 'P7')
    bridge = next(e for e in p7['reaction_occurrences'] if e['reaction_id'] == 're0000000001')
    encounter = next(e for e in p7['reaction_occurrences'] if e['reaction_id'] == 're0000000013')
    need(any(d['producer_event_id'] == bridge['event_id'] and d['consumer_event_id'] == encounter['event_id'] and
             d['original_species_id'] == independent.E2 for d in p7['event_dependencies']), 'EVENT_DAG_MISMATCH', '0001 precedes 0013 in source witness')
    need(limits['model_order'] == ['re0000000001', 're0000000013'] and
         limits['model_order_is_complete_physiological_mechanism'] is False and
         limits['initiator_release_peptide_bond_translocation_complete_physical_mechanism_claimed'] is False and
         limits['source_species_continuity_is_global_composition_certificate'] is False,
         'UNSUPPORTED_PHYSIOLOGICAL_INTERPRETATION', 'model order is not a physical mechanism certificate')
    need(limits['E1_E2_composition'] == {s: {'mRNA': 'INFERRED', 'peptidyl_state': 'INFERRED', 'full_complex_components': 'INFERRED'}
         for s in (independent.E1, independent.E2)}, 'IDENTITY_PROMOTION', 'E1/E2 moiety interpretation')
    need(limits['IF2_GDP_release_equals_IF2_GTP_recovery'] is False, 'FALSE_RECOVERY_CLAIM', 'IF2 nucleotide state')
    need(data['suggested_review_status'] == 'B1_1_CONDITIONALLY_ACCEPTED' and data['researcher_formally_signed'] is False and
         data['formal_signoff_status'] == 'PENDING_FINAL_RESEARCHER_CONFIRMATION' and data['commit_push_authorized'] is False and
         data['phase_b1_2_authorized'] is False and data['qssa_authorized'] is False and data['kinetic_reduction_authorized'] is False,
         'SCOPE_PROMOTION', 'conditional suggestion is not formal signature')
    need([(h['id'], h['user_conclusion']) for h in data['human_review']] ==
         [('H1', 'Y'), ('H2', 'Y'), ('H3', 'Y，限定'), ('H4', 'Y'), ('H5', '限定接受')], 'HUMAN_REVIEW_RECORD_MISMATCH', 'user conclusions')
    need(len(data['future_original_source_evidence_required']) == 3 and all(q['status'].startswith(('UNRESOLVED', 'NO_COMPLETE'))
         for q in data['future_original_source_evidence_required']), 'IDENTITY_PROMOTION', 'original-paper evidence remains unresolved')
    for p in data['source_provenance']:
        need(independent.audited.digest(ROOT / p['path']) == p['sha256'], 'SOURCE_HASH_MISMATCH', p['path'])
    return {'status': 'PASS', 'new_witness': result, 'shared_release_state': independent.audited.strings(shared),
            'release_reference_parameters': {r: str(k) for r, k in expected_parameters.items()},
            'E1_reached': True, 'IF1_IF3_free_states_recovered': True, 'source_model_0001_before_0013_verified': True,
            'physical_mechanism_certified': False, 'E1_E2_full_composition': 'INFERRED',
            'new_inventory_directions': len(data['reactions']), 'P1_overlay': 'LEXICOGRAPHIC_STRUCTURAL_WITNESS'}


def validate(data, markdown):
    source = independent.sources()
    source_integrity = independent.audited.check_source_integrity(source)
    historical = independent.validate(independent.load(OUT / 'phase_b1_1_witnesses.json'),
                                      independent.load(OUT / 'phase_b1_1_source_scope.json'),
                                      (OUT / 'phase_b1_1_initiation_pathways.md').read_text(encoding='utf-8'))
    new = check_followup(data, source)
    for e in data['new_witness']['reaction_occurrences']:
        need(e['equation'] in markdown and e['reaction_id'] in markdown, 'READING_VIEW_SOURCE_MISMATCH', e['reaction_id'])
    need(data['new_witness']['net_reaction'] in markdown and 'LEXICOGRAPHIC_STRUCTURAL_WITNESS' in markdown and
         'INFERRED' in markdown and '不得把此顺序直接解释' in markdown, 'READING_VIEW_INTERPRETATION_MISMATCH', 'required limits')
    return {'status': 'PASS', 'source_integrity': source_integrity, 'historical_B1_1_independent_rerun': historical,
            'followup_acceptance': new, 'preservation': preservation(), 'researcher_formally_signed': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir', type=Path, default=OUT)
    p.add_argument('--report', type=Path, default=OUT / 'phase_b1_1_followup_independent_verification.json')
    args = p.parse_args()
    try:
        result = validate(independent.load(args.input_dir / 'phase_b1_1_followup_witness.json'),
                          (args.input_dir / 'phase_b1_1_followup_pathway.md').read_text(encoding='utf-8'))
    except Exception as error:
        result = {'status': 'FAIL', 'rejection_code': getattr(error, 'code', type(error).__name__), 'error': str(error)}
        with (OUT / 'phase_b1_1_followup_failure_evidence.jsonl').open('a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps({'stage': 'followup_verification', 'report': result}) + '\n')
    independent.save(args.report, result)
    print(json.dumps({'status': result['status'], 'error': result.get('error'), 'new_events': result.get('followup_acceptance', {}).get('new_witness', {}).get('events_checked')}))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
