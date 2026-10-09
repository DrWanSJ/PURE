#!/usr/bin/env python3
"""Independent B1-1 acceptance: fresh canonical source, rational S*w and token DAG.

No B1-1 builder import. Reuses only the audited B0 read-only XML/CSV parser,
hash checker and exact-number helpers; all B1-1 acceptance is implemented here.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/reduction/pathways'
sys.path.insert(0, str(ROOT / 'scripts/pathways/phase_b0'))
import verify_phase_b0_witnesses as audited

need, Rejection = audited.need, audited.Rejection
E1 = 'elRS70SAGGU0002_fMettRNAfMetCAU'
E2 = 'elRS70SAGGU0002_fMet'
INTERFACE = 'IF2_GTP_fMettRNAfMetCAU'
RESOURCE = {'ATP', 'ADP', 'AMP', 'GTP', 'GDP', 'PO4', 'PPi', 'Gly', 'Met', 'FD', 'THF'}
LEDGER = sorted(RESOURCE | {'IF2_GTP', 'IF2_GDP', 'IF2', 'IF1', 'IF3', 'RS30S', 'RS50S', 'mRNA',
                           'tRNAfMetCAU', 'fMettRNAfMetCAU', 'MettRNAfMetCAU', 'MetRS', 'MTF'})


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, data):
    Path(path).write_bytes((json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode('utf-8'))


def sources():
    source = audited.parse_sources()
    with audited.V2.open(encoding='utf-8-sig', newline='') as f:
        source['annotations'] = {row['reaction_id']: row for row in csv.DictReader(f)}
    return source


def petri(w, source):
    """Pure source firing, deliberately independent of all claimed lineage."""
    m = defaultdict(F, {s: F(v) for s, v in w['initial_marking'].items()})
    trace = []
    for event in w['reaction_occurrences']:
        q = source['reactions'][event['reaction_id']]
        before = audited.strings(m)
        missing = {s: str(v - m[s]) for s, v in q['reactants'].items() if m[s] < v}
        need(not missing, 'MISSING_REQUIRED_INPUT', event['event_id'] + ' ' + json.dumps(missing))
        for s, v in q['reactants'].items():
            m[s] -= v
        for s, v in q['products'].items():
            m[s] += v
        trace.append({'event_id': event['event_id'], 'marking_before': before, 'marking_after': audited.strings(m)})
    return audited.strings(m), trace


def source_record(rid, record, source):
    q = source['reactions'][rid]
    need(audited.fractions(record['reactants']) == q['reactants'] and audited.fractions(record['products']) == q['products'],
         'SOURCE_COEFFICIENT_MISMATCH', rid)
    need(record['equation'] == audited.equation(q['reactants'], q['products']), 'SOURCE_EQUATION_MISMATCH', rid)
    k = source['parameters'][rid]
    need(F(record['reference_parameter']) == k and record['reference_activity'] == ('REFERENCE_ENABLED' if k > 0 else 'REFERENCE_DISABLED'),
         'REFERENCE_ACTIVITY_MISMATCH', rid)
    inverses = sorted(r for r, v in source['reactions'].items() if v['reactants'] == q['products'] and v['products'] == q['reactants'])
    need(record['reverse_reaction_ids'] == inverses, 'REVERSE_PAIR_MISMATCH', rid)
    a = source['annotations'][rid]
    need(record['level_c'] == a['level_c_functional_contexts'] and record['reaction_family_id'] == a['reaction_family_id'] and
         record['source_subsystems'] == a['level_b_subsystem_candidates'], 'INCORRECT_SOURCE_SCOPE', rid)


def check_witness(w, source):
    events, rx = w['reaction_occurrences'], source['reactions']
    need(bool(events), 'EMPTY_WITNESS', w['witness_id'])
    ids = [e['event_id'] for e in events]
    origins = [e['occurrence_origin'] for e in events]
    need(len(ids) == len(set(ids)) and len(origins) == len(set(origins)), 'DUPLICATE_OCCURRENCE', w['witness_id'])
    net = defaultdict(F)
    for event in events:
        r = event['reaction_id']
        need(r in rx, 'UNKNOWN_REACTION', r)
        q = rx[r]
        need(audited.fractions(event['inputs']) == q['reactants'] and audited.fractions(event['outputs']) == q['products'],
             'SOURCE_STATE_MISMATCH', r)
        need(event['equation'] == audited.equation(q['reactants'], q['products']), 'SOURCE_EQUATION_MISMATCH', r)
        for s, v in q['reactants'].items():
            net[s] -= v
        for s, v in q['products'].items():
            net[s] += v
        a = source['annotations'][r]
        need(w['source_contexts'][r] == a['level_c_functional_contexts'], 'INCORRECT_SOURCE_SCOPE', r)
        status = w['reference_direction_statuses'][r]
        k = source['parameters'][r]
        need(F(status['parameter']) == k and status['status'] == ('REFERENCE_ENABLED' if k > 0 else 'REFERENCE_DISABLED'),
             'REFERENCE_ACTIVITY_MISMATCH', r)
        need(k > 0, 'REFERENCE_DISABLED_EVENT', r)
        inv = sorted(t for t, v in rx.items() if v['reactants'] == q['products'] and v['products'] == q['reactants'])
        need(w['exact_reverse_partners'][r] == inv, 'REVERSE_PAIR_MISMATCH', r)
    actual, trace = petri(w, source)
    # Token origins are a stronger invariant than a feasible firing sequence.
    available = defaultdict(F)
    supplies = w['boundary_supplies']
    need(len({b['species_id'] for b in supplies}) == len(supplies), 'RESOURCE_DOUBLE_SPEND', 'duplicate boundary declaration')
    boundary = {b['species_id']: b['amount'] for b in supplies}
    need(boundary == w['initial_marking'], 'BOUNDARY_MARKING_MISMATCH', w['witness_id'])
    for s, v in boundary.items():
        need(s in source['species'] and F(v) > 0, 'INVALID_BOUNDARY', s)
        available[('BOUNDARY:' + s, s)] += F(v)
    edge_counts = Counter()
    by_event = {}
    for event in events:
        q = rx[event['reaction_id']]
        allocated = defaultdict(F)
        for b in event['input_origins']:
            s, origin, amount = b['species_id'], b['origin'], F(b['amount'])
            need(s in q['reactants'] and amount > 0, 'TOKEN_PROVENANCE_MISMATCH', event['event_id'])
            need(available[(origin, s)] >= amount, 'RESOURCE_DOUBLE_SPEND' if origin in by_event else 'TOKEN_PROVENANCE_MISMATCH',
                 f'{event["event_id"]} consumes unavailable {origin}:{s}')
            available[(origin, s)] -= amount
            allocated[s] += amount
            if not origin.startswith('BOUNDARY:'):
                need(origin in by_event and s in rx[by_event[origin]['reaction_id']]['products'], 'CARRIER_LINEAGE_MISMATCH', s)
                edge_counts[(origin, event['event_id'], s, str(amount))] += 1
        need(dict(allocated) == q['reactants'], 'TOKEN_PROVENANCE_MISMATCH', 'incomplete allocations ' + event['event_id'])
        for s, v in q['products'].items():
            available[(event['event_id'], s)] += v
        by_event[event['event_id']] = event
    claimed_edges = Counter()
    for d in w['event_dependencies']:
        s, producer, consumer = d['original_species_id'], d['producer_event_id'], d['consumer_event_id']
        expected_role = 'RESOURCE_TRANSFER' if s in RESOURCE else 'EXACT_SPECIES_HANDOFF'
        need(d['carrier_role'] == expected_role, 'SHARED_RESOURCE_NOT_CARRIER' if s in RESOURCE else 'CARRIER_LINEAGE_MISMATCH', s)
        need(d['token_provenance'] == 'EXACT_PRODUCER_OUTPUT' and d['evidence_status'] == 'EXTRACTED', 'IDENTITY_PROMOTION', s)
        need(producer in by_event and consumer in by_event and s in rx[by_event[producer]['reaction_id']]['products'] and
             s in rx[by_event[consumer]['reaction_id']]['reactants'], 'CARRIER_LINEAGE_MISMATCH', f'{producer}->{consumer}: {s}')
        claimed_edges[(producer, consumer, s, d['stoichiometric_amount'])] += 1
    need(edge_counts == claimed_edges, 'EVENT_DAG_MISMATCH', 'actual input origins differ from claimed DAG')
    need(w['final_marking'] == actual and w['per_event_markings'] == trace, 'MARKING_MISMATCH', w['witness_id'])
    need(w['exact_net_stoichiometry'] == audited.strings(net), 'NET_STOICHIOMETRY_MISMATCH', w['witness_id'])
    need(w['net_reaction'] == audited.equation({s: -v for s, v in net.items() if v < 0}, {s: v for s, v in net.items() if v > 0}),
         'NET_STOICHIOMETRY_MISMATCH', 'rendered net ' + w['witness_id'])
    expected_ledger = {s: {'initial': boundary.get(s, '0'), 'final': actual.get(s, '0'), 'net': str(net.get(s, 0))} for s in LEDGER}
    need(w['resource_ledger'] == expected_ledger, 'RESOURCE_LEDGER_MISMATCH', w['witness_id'])
    for claim in w['catalyst_recovery_claims']:
        s = claim['species_id']
        need(F(boundary.get(s, 0)) > 0 and F(actual.get(s, 0)) == F(boundary[s]) and net[s] == 0 and
             any(s in rx[e['reaction_id']]['products'] for e in events), 'FALSE_RECOVERY_CLAIM', s)
    need(w['factor_release_claims'] == [s for s in ('IF1', 'IF3', 'IF2_GDP') if s in actual], 'FALSE_RELEASE_CLAIM', w['witness_id'])
    need(w['source_reaction_ids'] == sorted({e['reaction_id'] for e in events}), 'COVERAGE_MISMATCH', w['witness_id'])
    target = w['target_milestone']
    need(F(actual.get(target, 0)) >= 1, 'MILESTONE_NOT_REACHED', target)
    productive = sum((v for (origin, s), v in available.items() if s == target and origin in by_event), F())
    need(productive >= 1, 'TOKEN_PROVENANCE_MISMATCH', 'target must survive from an actual producer')
    if w['composition_with_B0_W3']:
        w3 = next(x for x in load(OUT / 'phase_b0_handoff_witnesses.json')['witnesses'] if x['witness_id'] == 'W3')
        frozen = {e['event_id']: e for e in w3['reaction_occurrences']}
        need(set(frozen) <= set(by_event), 'B0_COMPOSITION_MISMATCH', w['witness_id'])
        for eid, b in frozen.items():
            e = by_event[eid]
            need(e['reaction_id'] == b['reaction_id'] and e['occurrence_origin'] == b['occurrence_origin'], 'B0_COMPOSITION_MISMATCH', eid)
        need(INTERFACE not in boundary and 'MettRNAfMetCAU' not in boundary and 'fMettRNAfMetCAU' not in boundary,
             'TOKEN_PROVENANCE_MISMATCH', 'injected duplicate upstream carrier')
        joins = [e for e in events if INTERFACE in rx[e['reaction_id']]['reactants']]
        producer = next(e['event_id'] for e in w3['reaction_occurrences'] if e['reaction_id'] == 're0000000449')
        need(len(joins) == 1 and any(b['species_id'] == INTERFACE and b['origin'] == producer for b in joins[0]['input_origins']),
             'TOKEN_PROVENANCE_MISMATCH', 'recruitment must consume actual W3 0449 output')
    if w['witness_id'] in ('P2', 'P5-E2', 'P7'):
        bridges = [e for e in events if e['reaction_id'] == 're0000000001']
        need(len(bridges) == 1, 'UNSUPPORTED_E2_PROVENANCE', 'one actual 0001 required')
        bridge = bridges[0]
        need(any(b['species_id'] == E1 and b['origin'] in by_event and
                 E1 in rx[by_event[b['origin']]['reaction_id']]['products'] for b in bridge['input_origins']),
             'TOKEN_PROVENANCE_MISMATCH', 'bridge cannot consume independently injected E1')
    # Names project streams only; neither tokens nor arithmetic certify moieties.
    need(w['carrier_evidence_status'] == 'INFERRED' and all(s['evidence_status'] == 'INFERRED' for s in w['carrier_streams']),
         'IDENTITY_PROMOTION', w['witness_id'])
    for record in w['carrier_streams']:
        need(record['event_id'] in by_event and set(record['before_species']) <= set(by_event[record['event_id']]['inputs']) and
             set(record['after_species']) <= set(by_event[record['event_id']]['outputs']), 'CARRIER_LINEAGE_MISMATCH', 'projection')
    return {'status': 'PASS', 'events_checked': len(events), 'petri_status': 'PASS', 'lineage_status': 'EXACT_PRODUCER_TOKEN_FLOW_VERIFIED',
            'event_dag_edges': sum(edge_counts.values()), 'exact_net': audited.strings(net), 'resource_ledger': expected_ledger,
            'target': target, 'target_produced_tokens': str(productive), 'catalysts_recovered': [c['species_id'] for c in w['catalyst_recovery_claims']]}


def scope_and_contract(data, inventory, source):
    rx, ann = source['reactions'], source['annotations']
    classified = {r for r, a in ann.items() if any(x.startswith('INIT_') for x in a['level_c_functional_contexts'].split(';'))}
    core = classified | {r for r, a in ann.items() if a['reaction_family_id'] in {'RFAM_022', 'RFAM_023', 'RFAM_024', 'RFAM_025', 'RFAM_026'}}
    need(inventory['source_reactions_indexed'] == 968 and set(inventory['initiation_classified_reaction_ids']) == classified and
         set(inventory['search_scope_reaction_ids']) == core, 'INCORRECT_SOURCE_SCOPE', 'bounded scope extraction')
    ws = {w['witness_id']: w for w in data['witnesses']}
    need(set(ws) == {'P1', 'P2', 'P3', 'P4', 'P5', 'P5-E2', 'P6', 'P7', 'P1-RELEASE-ALT'}, 'MISSING_SCENARIO', 'P1-P7 and release alternative')
    selected = {e['reaction_id'] for w in ws.values() for e in w['reaction_occurrences']}
    # Reconstruct bounded one-hop inventory from all actual source incidences.
    anchors = {s for r in core for side in ('reactants', 'products') for s in rx[r][side]
               if s.startswith(('RS30S', 'RS50S', 'RS70S', 'IF1', 'IF2', 'IF3'))}
    anchors.update({E1, E2, INTERFACE, 'MettRNAfMetCAU', 'fMettRNAfMetCAU'})
    local = {s for r in selected for side in ('reactants', 'products') for s in rx[r][side]
             if s not in RESOURCE and (s.startswith(('RS30S', 'RS50S', 'RS70S', 'IF1', 'IF2', 'IF3')) or
                                      s in {E1, E2, 'MettRNAfMetCAU', 'fMettRNAfMetCAU'})}
    expected = selected | {'re0000000414'} | {r for r, q in rx.items() if (set(q['reactants']) | set(q['products'])) & (anchors | local)}
    expected |= {r for r, q in rx.items() for t in list(expected) if q['reactants'] == rx[t]['products'] and q['products'] == rx[t]['reactants']}
    need(set(inventory['reactions']) == expected and set(inventory['unique_witness_reaction_ids']) == selected and
         set(inventory['source_incidence_inventory_ids']) == expected, 'INCIDENCE_INCOMPLETE', 'bounded inventory')
    for rid, record in inventory['reactions'].items():
        source_record(rid, record, source)
        need(record['evidence_status'] == 'EXTRACTED' and record['confidence'] == 'EXACT_SOURCE_REACTION_VERIFIED' and
             record['freshness'] == 'CANONICAL_HASH_CHECKED_AT_BUILD', 'IDENTITY_PROMOTION', rid)
    coverage = {'initiation_classified': len(classified), 'bounded_search_scope': len(core), 'bounded_inventory': len(expected),
                'unique_witness_directions': len(selected), 'inventory_enabled': sum(source['parameters'][r] > 0 for r in expected),
                'inventory_disabled': sum(source['parameters'][r] == 0 for r in expected),
                'search_enabled': sum(source['parameters'][r] > 0 for r in core),
                'search_disabled': sum(source['parameters'][r] == 0 for r in core),
                'original_species_in_inventory': len({s for r in expected for side in ('reactants', 'products') for s in rx[r][side]}),
                'participating_families': sorted({ann[r]['reaction_family_id'] for r in expected})}
    need(inventory['coverage'] == coverage and set(inventory['additional_context_reaction_ids']) == expected - selected,
         'COVERAGE_MISMATCH', 'source coverage counts')
    shared = {a['witness_id'] + '__' + b['witness_id']: sorted(set(a['source_reaction_ids']) & set(b['source_reaction_ids']))
              for i, a in enumerate(data['witnesses']) for b in data['witnesses'][i+1:]}
    need(inventory['shared_reaction_ids_between_scenarios'] == shared, 'COVERAGE_MISMATCH', 'shared IDs')
    concrete = defaultdict(list)
    for p in sorted((ROOT / 'models/pnas2017_full_reference/original/subsystems').glob('*.xml')):
        for n in ET.parse(p).getroot().iter():
            if n.tag.endswith('}reaction') and n.get('id') in expected:
                concrete[n.get('id')].append(p.relative_to(ROOT).as_posix())
    for r, q in inventory['reactions'].items():
        need(q.get('subsystem_source_files', []) == concrete[r], 'SOURCE_PROVENANCE_MISMATCH', r)
    # Every original outlet is retained, including disabled sinks and true reverses.
    expected_outlets = {s: sorted(r for r, q in rx.items() if s in q['reactants']) for s in sorted(local)}
    need(data['competition_outlets'] == expected_outlets, 'COMPETITION_INCOMPLETE', 'source-state outlets')
    for s, ids in expected_outlets.items():
        need(set(ids) <= expected, 'INCIDENCE_INCOMPLETE', s)
    for rid in ('re0000000420', 're0000000422', 're0000000288'):
        need(rx[rid]['reactants'].get('MettRNAfMetCAU') == 1, 'SHARED_POOL_MISMATCH', rid)
    need(data['shared_met_trna_pool'] == {'species_id': 'MettRNAfMetCAU', 'required_competitors':
         ['re0000000420', 're0000000422', 're0000000288'], 'pool_semantics': 'ONE_ORIGINAL_SPECIES_POOL'}, 'SHARED_POOL_MISMATCH', 'Met-tRNA')
    need('re0000000289' in expected and 're0000000450' in expected, 'COMPETITION_INCOMPLETE', 'inverse context')
    need(data['direction_semantics'] == {'re0000000449': {'exact_inverse': 're0000000450', 'binding_irreversible': False,
                                                        'automatically_fired_inverse': False}}, 'INCORRECT_DIRECTION_SEMANTICS', '0449/0450')
    need(source['parameters']['re0000000449'] == source['parameters']['re0000000450'] == 40, 'REFERENCE_ACTIVITY_MISMATCH', 'IF2 pair')
    # Positive scenario targets are independent requirements, not builder nets.
    for wid in ('P1', 'P3', 'P4', 'P5', 'P6', 'P1-RELEASE-ALT'):
        need(ws[wid]['target_milestone'] == E1, 'WRONG_MILESTONE', wid)
    for wid in ('P2', 'P5-E2'):
        need(ws[wid]['target_milestone'] == E2, 'WRONG_MILESTONE', wid)
    p1 = ws['P1']
    need(set(p1['initial_marking']) == {INTERFACE, 'RS30S', 'RS50S', 'IF1', 'IF3', 'mRNA'}, 'UNSUPPORTED_BOUNDARY_SUPPLY', 'P1')
    for wid in ('P1', 'P4'):
        w = ws[wid]
        join = next(e for e in w['reaction_occurrences'] if e['reaction_id'] == 're0000000519')
        need(any(b['species_id'] == 'RS30S_IF1_IF3_mRNA' and not b['origin'].startswith('BOUNDARY:') for b in join['input_origins']),
             'TOKEN_PROVENANCE_MISMATCH', 'expanded 30S assembly')
        need({'re0000000529', 're0000000717', 're0000000722', 're0000000726'} <= set(w['source_reaction_ids']), 'MISSING_INITIATION_MILESTONE', wid)
        need(w['exact_net_stoichiometry'].get('PO4') == '1' and 'GTP' not in w['exact_net_stoichiometry'], 'RESOURCE_LEDGER_MISMATCH', wid)
    need('IF1' not in ws['P3']['initial_marking'] and all('IF1' not in s for e in ws['P3']['reaction_occurrences'] for s in e['inputs']),
         'ALTERNATIVE_ROUTE_COLLAPSED', 'P3 excludes IF1')
    for wid, prefix in [('P1', ['re0000000459', 're0000000507']), ('P4', ['re0000000503', 're0000000491'])]:
        need([e['reaction_id'] for e in ws[wid]['reaction_occurrences'][:2]] == prefix, 'FALSE_REJOIN', wid + ' entry')
    need(ws['P2']['reaction_occurrences'][:-1] == p1['reaction_occurrences'], 'DUPLICATE_OCCURRENCE', 'P2 must reuse P1 once')
    need('IF2_GTP' not in ws['P6']['initial_marking'] and ws['P6']['initial_marking'].get('IF2') == '1' and
         ws['P6']['initial_marking'].get('GTP') == '1', 'UNSUPPORTED_BOUNDARY_SUPPLY', 'P6')
    need(ws['P6']['exact_net_stoichiometry'].get('GTP') == '-1' and ws['P6']['exact_net_stoichiometry'].get('IF2') == '-1' and
         'IF2_GTP' not in ws['P6']['exact_net_stoichiometry'], 'RESOURCE_LEDGER_MISMATCH', 'P6 free GTP ledger')
    encounter = ws['P7']['reaction_occurrences'][-1]
    need(encounter['reaction_id'] == 're0000000013' and ws['P7']['target_milestone'] in rx['re0000000013']['products'] and
         ws['P7']['initial_marking'].get('EFTu_GTP_GlytRNAGlyGCC') == '1', 'UNSUPPORTED_BOUNDARY_SUPPLY', 'P7')
    need(ws['P7']['classification'] == 'FIRST_ELONGATION_BINDING_INTERFACE', 'SCOPE_PROMOTION', 'P7')
    for link in data['alternative_routes']:
        left, right, s = ws[link['left']], ws[link['right']], link['species']
        producers = []
        for w in (left, right):
            hits = [e for e in w['reaction_occurrences'] if s in rx[e['reaction_id']]['products']]
            need(len(hits) == 1, 'FALSE_REJOIN', s)
            producer_index = w['reaction_occurrences'].index(hits[0])
            producers.append((hits[0], [e['reaction_id'] for e in w['reaction_occurrences'][producer_index+1:]]))
        need(producers[0][1] == producers[1][1], 'FALSE_SHARED_SUFFIX', s)
        need(link in left['alternative_entry_links'] and link in right['alternative_entry_links'], 'FALSE_REJOIN', 'missing link')
    for w in ws.values():
        need(w['scientific_status'] == 'PENDING_HUMAN_REVIEW' and w['structural_status'] == 'CANDIDATE_AWAITING_INDEPENDENT_VERIFICATION',
             'SCOPE_PROMOTION', w['witness_id'])
        rejoins = sorted({link['species'] for link in data['alternative_routes'] if w['witness_id'] in (link['left'], link['right'])})
        need(w['true_rejoin_species'] == rejoins, 'FALSE_REJOIN', w['witness_id'])
        transitions = [{'event_id': e['event_id'], 'before': list(e['inputs']), 'after': list(e['outputs']),
                        'evidence_status': 'EXTRACTED_STATES_INFERRED_NUCLEOTIDE_MOIETY'} for e in w['reaction_occurrences']
                       if any('IF2' in s for s in list(e['inputs']) + list(e['outputs']))]
        need(w['nucleotide_composite_transitions'] == transitions, 'SOURCE_STATE_MISMATCH', 'IF2 composite ledger ' + w['witness_id'])
    auth = data['authorization']
    need(auth == {'phase_b0_scientific_status': 'B0_FORMALLY_ACCEPTED_LIMITED_SCOPE', 'phase_b1_1_execution_authorized': True,
         'phase_b1_1_scientific_status': 'PENDING_HUMAN_REVIEW', 'phase_b1_1_formally_accepted': False,
         'phase_b1_2_authorized': False, 'full_phase_b_authorized': False, 'commit_push_authorized': False}, 'SCOPE_PROMOTION', 'authorization')
    return {'membership_checked': len(expected), 'coverage_independently_recomputed': coverage, 'alternatives_checked': len(data['alternative_routes']),
            'shared_pool_status': 'ONE_SOURCE_POOL', 'E1_reached': True, 'E2_reached': True,
            '0001_context': ann['re0000000001']['level_c_functional_contexts'],
            '0001_parameter': str(source['parameters']['re0000000001']), '0013_E2_input_verified': E2 in rx['re0000000013']['reactants']}


def preservation():
    baseline = load(OUT / 'phase_b1_1_source_baseline.json')
    hashes = baseline['all_tracked_file_hashes']
    changed = [p for p, h in hashes.items() if not (ROOT / p).is_file() or audited.digest(ROOT / p) != h]
    need(not changed, 'PROTECTED_FILE_CHANGED', json.dumps(changed))
    return {'status': 'PASS', 'tracked_files_unchanged': len(hashes), 'changed_files': changed,
            'starting_HEAD': baseline['starting_HEAD']}


def validate(data, inventory, markdown=None):
    source = sources()
    result = {'phase': 'B1-1', 'scientific_status': 'PENDING_HUMAN_REVIEW',
              'source_integrity': audited.check_source_integrity(source), 'witnesses': {}}
    for p in inventory['source_provenance']:
        need(audited.digest(ROOT / p['path']) == p['sha256'], 'SOURCE_HASH_MISMATCH', p['path'])
    for w in data['witnesses']:
        result['witnesses'][w['witness_id']] = check_witness(w, source)
    result['contract'] = scope_and_contract(data, inventory, source)
    # The human reading view must also contain the actual equations.
    if markdown is not None:
        for r, q in inventory['reactions'].items():
            need(f"| {r} | `{q['equation']}` |" in markdown, 'READING_VIEW_SOURCE_MISMATCH', r)
        for w in data['witnesses']:
            need(w['net_reaction'] in markdown, 'READING_VIEW_NET_MISMATCH', w['witness_id'])
    result['preservation'] = preservation()
    result['structural_verification_status'] = 'PASS'
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input-dir', type=Path, default=OUT)
    p.add_argument('--report', type=Path, default=OUT / 'phase_b1_1_independent_verification.json')
    args = p.parse_args()
    try:
        result = validate(load(args.input_dir / 'phase_b1_1_witnesses.json'), load(args.input_dir / 'phase_b1_1_source_scope.json'),
                          (args.input_dir / 'phase_b1_1_initiation_pathways.md').read_text(encoding='utf-8'))
    except Exception as error:
        result = {'structural_verification_status': 'FAIL', 'rejection_code': getattr(error, 'code', type(error).__name__), 'error': str(error)}
        with (OUT / 'phase_b1_1_failure_evidence.jsonl').open('a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps({'stage': 'independent_verification', 'report': result}) + '\n')
    save(args.report, result)
    print(json.dumps({'status': result['structural_verification_status'], 'events': {k: v['events_checked'] for k, v in result.get('witnesses', {}).items()}, 'error': result.get('error')}))
    return 0 if result['structural_verification_status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
