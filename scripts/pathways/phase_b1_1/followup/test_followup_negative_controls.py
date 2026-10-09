#!/usr/bin/env python3
"""Follow-up mutations use exactly the positive independent acceptance function."""
from copy import deepcopy
from pathlib import Path
import argparse
import json
import verify_followup as followup
import test_initiation_negative_controls as original_fixtures

v = followup.independent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir', type=Path, default=followup.OUT)
    p.add_argument('--report', type=Path, default=followup.OUT / 'phase_b1_1_followup_negative_controls.json')
    args = p.parse_args()
    source = v.sources()
    data = v.load(args.input_dir / 'phase_b1_1_followup_witness.json')
    controls = []

    def test(cid, description, expected, changed, must_enable=True):
        try:
            v.petri(changed['new_witness'], source)
            enabling, enabling_error = 'PASS', None
        except Exception as error:
            enabling, enabling_error = 'REJECTED', str(error)
        try:
            followup.check_followup(changed, source)
            code, detail = 'ACCEPTED_INVALID', 'Invalid mutation passed acceptance'
        except Exception as error:
            code, detail = getattr(error, 'code', type(error).__name__), str(error)
        passed = code == expected and (not must_enable or enabling == 'PASS')
        controls.append({'test_id': cid, 'mutation': description, 'expected_rejection': expected, 'actual_rejection': code,
                         'petri_enabling_result': enabling, 'petri_enabling_error': enabling_error, 'petri_PASS_required': must_enable,
                         'status': 'PASS' if passed else 'FAIL', 'evidence': detail, 'mutated_fixture': changed})

    bad = deepcopy(data)
    next(e for e in bad['new_witness']['reaction_occurrences'] if e['reaction_id'] == 're0000000747')['inputs'] = {
        'RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA': '1'}
    test('F01', '0747 claims a different 70S source state', 'SOURCE_STATE_MISMATCH', bad)
    bad = deepcopy(data)
    bad['new_witness']['reaction_occurrences'] = [e for e in bad['new_witness']['reaction_occurrences'] if e['reaction_id'] != 're0000000757']
    test('F02', 'Skip actual 0757 but still fire 0726', 'MISSING_REQUIRED_INPUT', bad, False)
    bad = deepcopy(data)
    bad['new_witness']['exact_net_stoichiometry']['PO4'] = '2'
    test('F03', 'Claim two free phosphate products', 'NET_STOICHIOMETRY_MISMATCH', bad)
    bad = deepcopy(data)
    bad['new_witness']['event_dependencies'] = [d for d in bad['new_witness']['event_dependencies']
        if d['original_species_id'] != 'RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA']
    test('F04', 'Remove true 0747-to-0757 lineage edge while keeping fireable order', 'EVENT_DAG_MISMATCH', bad)
    bad = deepcopy(data)
    prefix = data['new_witness']['reaction_occurrences'][:8]
    w = original_fixtures.fixture('F05', [e['reaction_id'] for e in prefix], data['new_witness']['initial_marking'], source,
                                 'RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA')
    w['catalyst_recovery_claims'] = [{'species_id': 'IF1', 'claim': 'SOURCE_FREE_STATE_RECOVERED'},
                                   {'species_id': 'IF3', 'claim': 'SOURCE_FREE_STATE_RECOVERED'}]
    bad['new_witness'] = w
    test('F05', 'Claim IF1 recovered while still bound after 0747', 'FALSE_RECOVERY_CLAIM', bad)
    bad = deepcopy(data)
    bad['new_witness']['reference_direction_statuses']['re0000000747']['parameter'] = '1'
    test('F06', 'Replace original 0747 author parameter', 'REFERENCE_ACTIVITY_MISMATCH', bad)
    bad = deepcopy(data)
    bad['historical_P1_annotation']['kinetic_dominance_claimed'] = True
    test('F07', 'Promote lexicographic P1 selection to kinetic dominance', 'UNSUPPORTED_KINETIC_INTERPRETATION', bad)
    bad = deepcopy(data)
    bad['interpretation_limits']['E1_E2_composition'][v.E1]['mRNA'] = 'VERIFIED'
    test('F08', 'Promote E1 mRNA composition from INFERRED', 'IDENTITY_PROMOTION', bad)
    bad = deepcopy(data)
    bad['interpretation_limits']['model_order_is_complete_physiological_mechanism'] = True
    test('F09', 'Turn source state order into a complete physiological mechanism', 'UNSUPPORTED_PHYSIOLOGICAL_INTERPRETATION', bad)
    bad = deepcopy(data)
    bad['researcher_formally_signed'] = True
    test('F10', 'Treat conditional review as formal researcher signature', 'SCOPE_PROMOTION', bad)
    bad = deepcopy(data)
    bad['release_branch_inventory'][0]['source_states'] = {'RS70S_IF1_IF2_GDP_fMettRNAfMetCAU_mRNA': '1'}
    test('F11', 'Claim a false shared precursor for the three release exits', 'CARRIER_LINEAGE_MISMATCH', bad)
    bad = deepcopy(data)
    bad['reactions']['re0000000747']['reactants']['RS70S_IF1_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA'] = '2'
    test('F12', 'Corrupt 0747 stoichiometric coefficient in source inventory', 'SOURCE_COEFFICIENT_MISMATCH', bad)
    passed = sum(c['status'] == 'PASS' for c in controls)
    report = {'status': 'PASS' if passed == len(controls) else 'FAIL', 'followup_controls_run': len(controls),
              'followup_controls_passed': passed, 'followup_controls_failed': len(controls) - passed,
              'controls_not_run': [], 'acceptance_entrypoint': 'verify_followup.check_followup', 'controls': controls,
              'canonical_mutation': False, 'historical_files_mutated': False}
    v.save(args.report, report)
    if report['status'] != 'PASS':
        with (followup.OUT / 'phase_b1_1_followup_failure_evidence.jsonl').open('a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps({'stage': 'followup_negative_controls', 'failed': [c for c in controls if c['status'] != 'PASS']}) + '\n')
    print(json.dumps({k: report[k] for k in ('status', 'followup_controls_run', 'followup_controls_passed', 'followup_controls_failed')}))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
