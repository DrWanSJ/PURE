#!/usr/bin/env python3
"""Executed mutations against the same independent acceptance as positive cases."""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import argparse
import json
import verify_initiation_witnesses as v


def fixture(name, ids, boundary, source, target=None, event_records=None, composed=False):
    """Independent source-only fixture allocation; never imports witness builder."""
    pools = defaultdict(list)
    for s, amount in boundary.items():
        pools[s].append(['BOUNDARY:' + s, F(amount)])
    events, deps, trace, net = [], [], [], defaultdict(F)
    for i, rid in enumerate(ids):
        eid = event_records[i]['event_id'] if event_records else f'{name}:E{i+1:02d}'
        origin = event_records[i]['occurrence_origin'] if event_records else eid
        q = source['reactions'][rid]
        before = v.audited.strings({s: sum((a for _, a in p), F()) for s, p in pools.items()})
        bindings = []
        for s, amount in q['reactants'].items():
            remaining = amount
            for token in pools[s]:
                take = min(token[1], remaining)
                if take:
                    bindings.append({'species_id': s, 'amount': str(take), 'origin': token[0]})
                    if not token[0].startswith('BOUNDARY:'):
                        deps.append(edge(token[0], eid, s, str(take)))
                    token[1] -= take
                    remaining -= take
            if remaining:
                # Invalid Petri fixtures still carry full original input demands.
                bindings.append({'species_id': s, 'amount': str(remaining), 'origin': 'BOUNDARY:' + s})
                pools[s].append(['BOUNDARY:' + s, -remaining])
            net[s] -= amount
        for s, amount in q['products'].items():
            pools[s].append([eid, amount])
            net[s] += amount
        after = v.audited.strings({s: sum((a for _, a in p), F()) for s, p in pools.items()})
        events.append({'event_id': eid, 'occurrence_origin': origin, 'reaction_id': rid,
                       'inputs': v.audited.strings(q['reactants']), 'outputs': v.audited.strings(q['products']),
                       'equation': v.audited.equation(q['reactants'], q['products']), 'input_origins': bindings})
        trace.append({'event_id': eid, 'marking_before': before, 'marking_after': after})
    final = trace[-1]['marking_after']
    used = sorted(set(ids))
    return {'witness_id': name, 'reaction_occurrences': events, 'source_reaction_ids': used,
            'initial_marking': {s: str(n) for s, n in boundary.items()},
            'boundary_supplies': [{'species_id': s, 'amount': str(n)} for s, n in boundary.items()],
            'event_dependencies': deps, 'final_marking': final, 'per_event_markings': trace,
            'exact_net_stoichiometry': v.audited.strings(net),
            'net_reaction': v.audited.equation({s: -n for s, n in net.items() if n < 0}, {s: n for s, n in net.items() if n > 0}),
            'resource_ledger': {s: {'initial': str(boundary.get(s, 0)), 'final': final.get(s, '0'), 'net': str(net.get(s, 0))} for s in v.LEDGER},
            'source_contexts': {r: source['annotations'][r]['level_c_functional_contexts'] for r in used},
            'reference_direction_statuses': {r: {'parameter': str(source['parameters'][r]), 'status':
                'REFERENCE_ENABLED' if source['parameters'][r] > 0 else 'REFERENCE_DISABLED'} for r in used},
            'exact_reverse_partners': {r: sorted(t for t, q in source['reactions'].items() if q['reactants'] == source['reactions'][r]['products'] and
                q['products'] == source['reactions'][r]['reactants']) for r in used},
            'target_milestone': target or next(iter(source['reactions'][ids[-1]]['products'])),
            'composition_with_B0_W3': composed, 'catalyst_recovery_claims': [],
            'factor_release_claims': [s for s in ('IF1', 'IF3', 'IF2_GDP') if s in final],
            'carrier_streams': [], 'carrier_evidence_status': 'INFERRED'}


def edge(producer, consumer, species, amount='1', role=None):
    return {'producer_event_id': producer, 'consumer_event_id': consumer, 'original_species_id': species,
            'stoichiometric_amount': amount, 'token_provenance': 'EXACT_PRODUCER_OUTPUT',
            'carrier_role': role or ('RESOURCE_TRANSFER' if species in v.RESOURCE else 'EXACT_SPECIES_HANDOFF'), 'evidence_status': 'EXTRACTED'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir', type=Path, default=v.OUT)
    p.add_argument('--report', type=Path, default=v.OUT / 'phase_b1_1_negative_controls.json')
    args = p.parse_args()
    source = v.sources()
    data = v.load(args.input_dir / 'phase_b1_1_witnesses.json')
    inventory = v.load(args.input_dir / 'phase_b1_1_source_scope.json')
    ws = {w['witness_id']: w for w in data['witnesses']}
    controls = []

    def test(cid, mutation, expected, w=None, op=None, must_enable=False, source_ids=None):
        enabling, enabling_error = 'NOT_APPLICABLE', None
        if w is not None:
            try:
                v.petri(w, source)
                enabling = 'PASS'
            except Exception as error:
                enabling, enabling_error = 'REJECTED', str(error)
        try:
            (op or (lambda: v.check_witness(w, source)))()
            code, evidence = 'ACCEPTED_INVALID', 'Invalid mutation passed acceptance'
        except Exception as error:
            code, evidence = getattr(error, 'code', type(error).__name__), str(error)
        success = code == expected and (not must_enable or enabling == 'PASS')
        controls.append({'test_id': cid, 'mutation': mutation, 'source_reaction_ids': source_ids or
                         ([e['reaction_id'] for e in w['reaction_occurrences']] if w else []),
                         'expected_rejection': expected, 'actual_rejection': code, 'petri_enabling_result': enabling,
                         'petri_enabling_error': enabling_error, 'petri_PASS_required': must_enable,
                         'lineage_result': 'REJECTED_BY_LINEAGE_ACCEPTANCE' if code in {'RESOURCE_DOUBLE_SPEND', 'TOKEN_PROVENANCE_MISMATCH',
                             'CARRIER_LINEAGE_MISMATCH', 'EVENT_DAG_MISMATCH', 'SHARED_RESOURCE_NOT_CARRIER'} else 'NOT_TARGETED',
                         'status': 'PASS' if success else 'FAIL', 'evidence': evidence, 'mutated_fixture': w})

    rid = lambda n: f're{n:010d}'
    f = lambda name, nums, boundary, target=None: fixture(name, [rid(n) for n in nums], boundary, source, target)
    dual = 'RS30S_IF1_IF3_mRNA'
    seventy = 'RS70S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA'
    test('N01', '0519 without exact IF2/formylated-tRNA complex', 'MISSING_REQUIRED_INPUT', f('N01', [519], {dual: 1}))
    test('N02', '0519 without its exact 30S partner', 'MISSING_REQUIRED_INPUT', f('N02', [519], {v.INTERFACE: 1}))
    test('N03', '0529 without independent RS50S', 'MISSING_REQUIRED_INPUT', f('N03', [529], {seventy.replace('70S', '30S'): 1}))
    bad = deepcopy(ws['P1'])
    join = next(e for e in bad['reaction_occurrences'] if e['reaction_id'] == rid(529))
    join['inputs'] = {'RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA': '1', 'RS50S': '1'}
    test('N04', '0529 display substitutes a different 30S carrier state; source firing stays feasible', 'SOURCE_STATE_MISMATCH', bad, must_enable=True)
    bad = deepcopy(ws['P1'])
    next(e for e in bad['reaction_occurrences'] if e['reaction_id'] == rid(717))['inputs'] = {seventy.replace('IF1_IF3_', 'IF3_'): '1'}
    test('N05', '0717 claims the wrong 70S source state', 'SOURCE_STATE_MISMATCH', bad, must_enable=True)
    bad = f('N06', [717], {seventy: 1}, seventy.replace('GTP', 'GDP_PO4'))
    bad['exact_net_stoichiometry']['PO4'] = '1'
    test('N06', 'Omit actual phosphate-release event but claim free PO4 net', 'NET_STOICHIOMETRY_MISMATCH', bad, must_enable=True)
    test('N07', '0726 without exact GDP-bound precursor', 'MISSING_REQUIRED_INPUT', f('N07', [726], {seventy: 1}))
    bad = f('N08', [459], {'RS30S': 1, 'IF3': 1, v.E2: 1}, v.E2)
    test('N08', 'Claim E2 from preexisting target without actual productive source event', 'TOKEN_PROVENANCE_MISMATCH', bad, must_enable=True)
    bad = deepcopy(ws['P2'])
    bad['source_contexts'][rid(1)] = 'INIT_assembly'
    test('N09', 'Misattribute 0001 to initiation family/context', 'INCORRECT_SOURCE_SCOPE', bad, must_enable=True)
    bad = f('N10', [449, 519, 475], {'IF2_GTP': 1, 'fMettRNAfMetCAU': 1, dual: 1, 'RS30S_IF3_mRNA': 1, v.INTERFACE: 1})
    for e in bad['reaction_occurrences'][1:]:
        next(b for b in e['input_origins'] if b['species_id'] == v.INTERFACE)['origin'] = 'N10:E01'
    bad['event_dependencies'] = [edge('N10:E01', e['event_id'], v.INTERFACE) for e in bad['reaction_occurrences'][1:]]
    test('N10', 'Two branches claim the one 0449 output despite independent extra complex making both firings possible',
         'RESOURCE_DOUBLE_SPEND', bad, must_enable=True)
    bad = f('N11', [445, 459], {'GTP': 1, 'IF2': 1, 'RS30S': 1, 'IF3': 1})
    bad['event_dependencies'].append(edge('N11:E01', 'N11:E02', 'GTP', role='EXACT_SPECIES_HANDOFF'))
    test('N11', 'Declare unrelated fireable streams continuous through shared GTP', 'SHARED_RESOURCE_NOT_CARRIER', bad, must_enable=True)
    bad = deepcopy(ws['P1'])
    bad['catalyst_recovery_claims'].append({'species_id': 'IF2_GTP', 'claim': 'SOURCE_FREE_STATE_RECOVERED'})
    test('N12', 'Claim IF2_GTP regenerated from IF2_GDP release', 'FALSE_RECOVERY_CLAIM', bad, must_enable=True)
    bad = deepcopy(ws['P5'])
    bad['reaction_occurrences'].append(deepcopy(bad['reaction_occurrences'][0]))
    test('N13', 'Count a shared original W3 event twice', 'DUPLICATE_OCCURRENCE', bad)
    bad = f('N14', [2], {v.E2: 1, 'tRNAfMetCAU': 1})
    bad['reference_direction_statuses'][rid(2)]['status'] = 'REFERENCE_ENABLED'
    test('N14', 'Zero-parameter direction 0002 labeled reference-enabled', 'REFERENCE_ACTIVITY_MISMATCH', bad, must_enable=True)
    mutated = deepcopy(source)
    mutated['reactions'][rid(414)]['products']['PO4'] = F(1)
    test('N15', 'In-memory 0414 coefficient changed from 2 PO4 to 1', 'SOURCE_COEFFICIENT_MISMATCH',
         op=lambda: v.audited.check_source_integrity(mutated), source_ids=[rid(414)])
    altered = deepcopy(data)
    altered['direction_semantics'][rid(449)].update(binding_irreversible=True, automatically_fired_inverse=True)
    test('N16', '0449/0450 declared irreversible or automatic reverse occurrences', 'INCORRECT_DIRECTION_SEMANTICS',
         op=lambda: v.scope_and_contract(altered, inventory, source), source_ids=[rid(449), rid(450)])
    bad = f('N17', [459, 507], {'RS30S': 1, 'IF1': 1, 'IF3': 1}, 'RS30S_IF1_IF3')
    bad['catalyst_recovery_claims'].append({'species_id': 'IF1', 'claim': 'SOURCE_FREE_STATE_RECOVERED'})
    test('N17', 'IF1 declared recovered while trapped in terminal dual-factor complex', 'FALSE_RECOVERY_CLAIM', bad, must_enable=True)
    base = ws['P5']
    bad = fixture('P5', [e['reaction_id'] for e in base['reaction_occurrences']], {**base['initial_marking'], v.INTERFACE: '1'},
                  source, v.E1, base['reaction_occurrences'], composed=True)
    test('N18', 'Use injected preexisting recruitment target while leaving W3 output unused', 'TOKEN_PROVENANCE_MISMATCH', bad, must_enable=True)
    bad = f('N19', [459, 503], {'RS30S': 2, 'IF3': 1, 'IF1': 1})
    bad['event_dependencies'].append(edge('N19:E01', 'N19:E02', 'RS30S'))
    test('N19', 'Serialize IF3-first and IF1-first entries as one carrier history using independent extra ribosome seed',
         'CARRIER_LINEAGE_MISMATCH', bad, must_enable=True)
    bad = deepcopy(ws['P5'])
    bad['event_dependencies'].pop()
    test('N20', 'Remove a true DAG dependency while leaving feasible firing sequence', 'EVENT_DAG_MISMATCH', bad, must_enable=True)
    # Extra specificity: scope coefficients, unreleased source moieties, shared pool and exact W3 origin.
    altered = deepcopy(inventory['reactions'][rid(717)])
    altered['reactants'][seventy] = '2'
    test('S01', 'Alter another actual source coefficient in the inventory', 'SOURCE_COEFFICIENT_MISMATCH',
         op=lambda: v.source_record(rid(717), altered, source), source_ids=[rid(717)])
    test('S02', 'MTF and EF-Tu entrances overspend the single finite unformylated Met-tRNA pool', 'MISSING_REQUIRED_INPUT',
         f('S02', [420, 288], {'MTF': 1, 'EFTu_GTP': 1, 'MettRNAfMetCAU': 1}))
    altered_data = deepcopy(data)
    altered_data['witnesses'][0]['nucleotide_composite_transitions'][0]['after'] = ['GDP']
    test('S03', 'Replace original bound IF2 state with invented free GDP ledger output', 'SOURCE_STATE_MISMATCH',
         op=lambda: v.scope_and_contract(altered_data, inventory, source), source_ids=[rid(519)])
    positives = []
    reordered = deepcopy(ws['P5']['reaction_occurrences'])
    prep = next(e for e in reordered if e['reaction_id'] == rid(418))
    reordered.remove(prep)
    reordered.insert(0, prep)
    for name, make in [('INDEPENDENT_PRECURSOR_REORDER', lambda: fixture('P5', [e['reaction_id'] for e in reordered],
                       ws['P5']['initial_marking'], source, v.E1, reordered, True)),
                       ('GENUINE_REPEAT_DISTINCT_OCCURRENCES', lambda: f('GENUINE_REPEAT', [449, 450, 449],
                         {'IF2_GTP': 1, 'fMettRNAfMetCAU': 1}, v.INTERFACE))]:
        try:
            w = make()
            positives.append({'id': name, 'status': 'PASS', 'evidence': v.check_witness(w, source), 'fixture': w})
        except Exception as error:
            positives.append({'id': name, 'status': 'FAIL', 'error': str(error)})
    passed = sum(c['status'] == 'PASS' for c in controls)
    report = {'status': 'PASS' if passed == len(controls) and all(p['status'] == 'PASS' for p in positives) else 'FAIL',
              'required_controls_run': 20, 'required_controls_passed': sum(c['status'] == 'PASS' for c in controls[:20]),
              'required_controls_failed': sum(c['status'] != 'PASS' for c in controls[:20]),
              'controls_run': len(controls), 'controls_passed': passed, 'controls_failed': len(controls) - passed,
              'controls_not_run': [], 'controls': controls, 'supplemental_positives': positives,
              'canonical_mutation': False, 'acceptance_entrypoints': ['check_witness', 'scope_and_contract', 'source_record', 'check_source_integrity']}
    v.save(args.report, report)
    if report['status'] != 'PASS':
        with (v.OUT / 'phase_b1_1_failure_evidence.jsonl').open('a', encoding='utf-8', newline='\n') as f_out:
            f_out.write(json.dumps({'stage': 'negative_controls', 'failed': [c for c in controls if c['status'] != 'PASS'],
                                    'positives': [p for p in positives if p['status'] != 'PASS']}) + '\n')
    print(json.dumps({k: report[k] for k in ('status', 'required_controls_run', 'required_controls_passed', 'controls_run', 'controls_passed', 'controls_failed')}))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
