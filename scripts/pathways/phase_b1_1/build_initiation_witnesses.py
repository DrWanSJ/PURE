#!/usr/bin/env python3
"""Bounded, exact-source initiation discovery; no kinetic or composition oracle."""
from collections import Counter, defaultdict, deque
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
import build_phase_b0_witnesses as low

E1 = 'elRS70SAGGU0002_fMettRNAfMetCAU'
E2 = 'elRS70SAGGU0002_fMet'
INTERFACE = 'IF2_GTP_fMettRNAfMetCAU'
RESOURCES = {'GTP', 'GDP', 'PO4', 'ATP', 'ADP', 'AMP', 'PPi', 'Met', 'Gly', 'FD', 'THF'}
LEDGER = sorted(RESOURCES | {'IF2_GTP', 'IF2_GDP', 'IF2', 'IF1', 'IF3', 'RS30S', 'RS50S', 'mRNA',
                            'tRNAfMetCAU', 'fMettRNAfMetCAU', 'MettRNAfMetCAU', 'MetRS', 'MTF'})
AUTH = {'phase_b0_scientific_status': 'B0_FORMALLY_ACCEPTED_LIMITED_SCOPE',
        'phase_b1_1_execution_authorized': True, 'phase_b1_1_scientific_status': 'PENDING_HUMAN_REVIEW',
        'phase_b1_1_formally_accepted': False, 'phase_b1_2_authorized': False,
        'full_phase_b_authorized': False, 'commit_push_authorized': False}


def dump(path, data):
    path.write_bytes((json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))


def scope(rx, ann):
    classified = {r for r, a in ann.items() if any(c.startswith('INIT_') for c in a['level_c_functional_contexts'].split(';'))}
    families = {r for r, a in ann.items() if a['reaction_family_id'] in {f'RFAM_{n:03d}' for n in range(22, 27)}}
    core = classified | families
    # One-hop inventory uses ribosomal/IF states, never free shared metabolites.
    anchors = {s for r in core for k in ('reactants', 'products') for s in rx[r][k]
               if s.startswith(('RS30S', 'RS50S', 'RS70S', 'IF1', 'IF2', 'IF3'))}
    anchors |= {E1, E2, INTERFACE, 'MettRNAfMetCAU', 'fMettRNAfMetCAU'}
    incidence = {r for r, q in rx.items() if (set(q['reactants']) | set(q['products'])) & anchors}
    return classified, core, incidence


def search(initial, waypoints, allowed, rx, max_states=50000, max_depth=16):
    """BFS over complete rational markings and ordered *state* milestones.

    Each leg takes the shortest co-reactant-enabled route to the next state.
    All scoped positive source directions compete; sorted IDs break ties.
    Source-state waypoints select representative assembly/release orders.
    No reaction-ID sequence is embedded in discovery.
    """
    marking = {s: F(v) for s, v in initial.items()}
    path, evidence = [], []
    for target in waypoints:
        start = tuple(sorted((s, v) for s, v in marking.items() if v))
        queue, seen = deque([(start, [])]), {start}
        found = None
        while queue:
            state, route = queue.popleft()
            m = dict(state)
            if m.get(target, 0) >= 1:
                found = (m, route)
                break
            if len(route) >= max_depth:
                continue
            for rid in allowed:
                q = rx[rid]
                if not all(m.get(s, 0) >= F(v) for s, v in q['reactants'].items()):
                    continue
                nxt = defaultdict(F, m)
                for s, v in q['reactants'].items():
                    nxt[s] -= F(v)
                for s, v in q['products'].items():
                    nxt[s] += F(v)
                key = tuple(sorted((s, v) for s, v in nxt.items() if v))
                if key not in seen:
                    seen.add(key)
                    if len(seen) > max_states:
                        raise ValueError('SEARCH_LIMIT: ' + target)
                    queue.append((key, route + [rid]))
        if found is None:
            raise ValueError('NO_ENABLED_FINITE_ROUTE: ' + target)
        marking, route = found
        path += route
        evidence.append({'target_source_state': target, 'visited_markings': len(seen), 'selected_reaction_ids': route})
    return path, evidence


def construct(wid, occurrences, boundary, target, rx, recovered=(), composed=False):
    pool = defaultdict(list)
    for s, v in sorted(boundary.items()):
        pool[s].append(['BOUNDARY:' + s, F(v)])
    events, deps, trace, net = [], [], [], defaultdict(F)
    for eid, rid, origin in occurrences:
        q = rx[rid]
        before = low.exact({s: sum((v for _, v in ts), F()) for s, ts in pool.items()})
        bindings = []
        for s, v in q['reactants'].items():
            need = F(v)
            if sum((n for _, n in pool[s]), F()) < need:
                raise ValueError(f'MISSING_REQUIRED_INPUT: {eid} {s}')
            for token in pool[s]:
                use = min(need, token[1])
                if use:
                    producer = token[0]
                    bindings.append({'species_id': s, 'amount': str(use), 'origin': producer})
                    if not producer.startswith('BOUNDARY:'):
                        deps.append({'producer_event_id': producer, 'consumer_event_id': eid, 'original_species_id': s,
                                     'stoichiometric_amount': str(use), 'token_provenance': 'EXACT_PRODUCER_OUTPUT',
                                     'carrier_role': 'RESOURCE_TRANSFER' if s in RESOURCES else 'EXACT_SPECIES_HANDOFF',
                                     'evidence_status': 'EXTRACTED'})
                    token[1] -= use
                    need -= use
            net[s] -= F(v)
        for s, v in q['products'].items():
            pool[s].append([eid, F(v)])
            net[s] += F(v)
        after = low.exact({s: sum((v for _, v in ts), F()) for s, ts in pool.items()})
        events.append({'event_id': eid, 'reaction_id': rid, 'occurrence_origin': origin,
                       'inputs': q['reactants'], 'outputs': q['products'], 'equation': q['equation'], 'input_origins': bindings})
        trace.append({'event_id': eid, 'marking_before': before, 'marking_after': after})
    final = trace[-1]['marking_after']
    used = sorted({e['reaction_id'] for e in events})
    streams = []
    for e in events:
        for carrier, terms in {'initiator_tRNA': ('tRNAfMetCAU',), 'formylated_tRNA': ('fMettRNAfMetCAU',),
                               'IF2_nucleotide': ('IF2',), 'ribosome': ('RS30S', 'RS50S', 'RS70S'),
                               'mRNA': ('mRNA',), 'IF1': ('IF1',), 'IF3': ('IF3',),
                               'amino_acid_peptide': ('Met',)}.items():
            before = sorted(s for s in e['inputs'] if any(t in s for t in terms))
            after = sorted(s for s in e['outputs'] if any(t in s for t in terms))
            if before or after:
                streams.append({'event_id': e['event_id'], 'carrier': carrier, 'before_species': before,
                                'after_species': after, 'evidence_status': 'INFERRED',
                                'basis': 'SOURCE_NAME_CONTEXT_PROJECTION_ONLY', 'scientific_status': 'PENDING_HUMAN_REVIEW'})
    signed = low.exact(net)
    return {'witness_id': wid, 'classification': 'FIRST_ELONGATION_BINDING_INTERFACE' if wid == 'P7' else
            'INITIATION_WITH_E2_BOUNDARY' if target == E2 else 'INITIATION_E1',
            'structural_status': 'CANDIDATE_AWAITING_INDEPENDENT_VERIFICATION', 'scientific_status': 'PENDING_HUMAN_REVIEW',
            'starting_interface': INTERFACE, 'target_milestone': target, 'composition_with_B0_W3': composed,
            'source_reaction_ids': used, 'reaction_occurrences': events, 'event_dependencies': deps,
            'boundary_supplies': [{'species_id': s, 'amount': str(v), 'token_origin': 'BOUNDARY:' + s,
                                  'evidence_status': 'AMBIGUOUS', 'full_model_availability_verified': False,
                                  'justification': 'Explicit finite conditional test supply; no experimental availability assertion'}
                                 for s, v in sorted(boundary.items())],
            'initial_marking': {s: str(v) for s, v in sorted(boundary.items())}, 'final_marking': final,
            'per_event_markings': trace, 'carrier_streams': streams, 'carrier_evidence_status': 'INFERRED',
            'exact_net_stoichiometry': signed,
            'net_reaction': low.equation({s: str(-v) for s, v in net.items() if v < 0}, {s: str(v) for s, v in net.items() if v > 0}),
            'resource_ledger': {s: {'initial': str(boundary.get(s, 0)), 'final': final.get(s, '0'), 'net': str(net.get(s, 0))} for s in LEDGER},
            'nucleotide_composite_transitions': [{'event_id': e['event_id'], 'before': list(e['inputs']), 'after': list(e['outputs']),
                                                  'evidence_status': 'EXTRACTED_STATES_INFERRED_NUCLEOTIDE_MOIETY'}
                                                 for e in events if any('IF2' in s for s in list(e['inputs']) + list(e['outputs']))],
            'source_contexts': {r: rx[r]['level_c'] for r in used},
            'reference_direction_statuses': {r: {'parameter': rx[r]['reference_parameter'], 'status': rx[r]['reference_activity']} for r in used},
            'exact_reverse_partners': {r: rx[r]['reverse_reaction_ids'] for r in used},
            'alternative_entry_links': [], 'true_rejoin_species': [],
            'catalyst_recovery_claims': [{'species_id': s, 'claim': 'SOURCE_FREE_STATE_RECOVERED'} for s in recovered],
            'factor_release_claims': [s for s in ('IF1', 'IF3', 'IF2_GDP') if s in final],
            'source_provenance': [low.provenance(low.SOURCE, 'CANONICAL_SBML'), low.provenance(low.CSV, 'AUTHOR_PARAMETER_COPY')],
            'unresolved_assumptions': ['Boundary supplies conditional; no trajectory feasibility',
                                       'Composite molecular identity and mRNA/peptide moieties remain INFERRED',
                                       'RS30S/RS50S incorporation is not ribosome recovery; IF2_GDP release is not IF2_GTP recycling']}


def build():
    rx = low.read_source()
    with (ROOT / low.V2).open(encoding='utf-8-sig', newline='') as f:
        ann = {r['reaction_id']: r for r in csv.DictReader(f)}
    classified, core, incidence = scope(rx, ann)
    enabled = sorted(r for r in core if F(rx[r]['reference_parameter']) > 0)
    initial = {s: '1' for s in (INTERFACE, 'RS30S', 'RS50S', 'IF1', 'IF3', 'mRNA')}
    dual = 'RS30S_IF1_IF3'
    full = 'RS30S_IF1_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA'
    seventy = full.replace('30S', '70S')
    gdp = seventy.replace('GTP', 'GDP')
    exit_state = 'RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA'
    common = [dual, dual + '_mRNA', full, seventy, seventy.replace('GTP', 'GDP_PO4'), gdp, exit_state, E1]
    configs = [('P1', initial, ['RS30S_IF3'] + common),
               ('P3', {s: v for s, v in initial.items() if s != 'IF1'},
                ['RS30S_IF3', 'RS30S_IF3_mRNA', 'RS30S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA',
                 'RS70S_IF3_IF2_GTP_fMettRNAfMetCAU_mRNA', 'RS70S_IF3_IF2_GDP_PO4_fMettRNAfMetCAU_mRNA',
                 'RS70S_IF3_IF2_GDP_fMettRNAfMetCAU_mRNA', exit_state, E1]),
               ('P4', initial, ['RS30S_IF1'] + common),
               ('P1-RELEASE-ALT', initial, ['RS30S_IF3'] + common[:6] + ['RS70S_IF1_IF3_fMettRNAfMetCAU_mRNA', E1])]
    witnesses, discovery = [], []
    for wid, boundary, states in configs:
        ids, legs = search(boundary, states, enabled, rx)
        events = [(f'{wid}:E{i+1:02d}', r, f'{wid}:E{i+1:02d}') for i, r in enumerate(ids)]
        witnesses.append(construct(wid, events, boundary, E1, rx, [s for s in ('IF1', 'IF3') if s in boundary]))
        discovery.append({'witness_id': wid, 'waypoints': states, 'legs': legs, 'status': 'ROUTE_FOUND'})
    ws = {w['witness_id']: w for w in witnesses}
    p1events = [(e['event_id'], e['reaction_id'], e['occurrence_origin']) for e in ws['P1']['reaction_occurrences']]
    p2events = p1events + [('P2:E2-BRIDGE', low.rid(1), 'P2:E2-BRIDGE')]
    witnesses.append(construct('P2', p2events, initial, E2, rx, ('IF1', 'IF3')))
    b0 = json.loads((OUT / 'phase_b0_handoff_witnesses.json').read_text(encoding='utf-8'))
    w3 = next(w for w in b0['witnesses'] if w['witness_id'] == 'W3')
    b0events = [(e['event_id'], e['reaction_id'], e['occurrence_origin']) for e in w3['reaction_occurrences']]
    b5 = {**{s: v for s, v in initial.items() if s != INTERFACE}, **w3['initial_marking']}
    witnesses.append(construct('P5', b0events + p1events, b5, E1, rx, ('MetRS', 'MTF', 'IF1', 'IF3'), True))
    witnesses.append(construct('P5-E2', b0events + p2events, b5, E2, rx, ('MetRS', 'MTF', 'IF1', 'IF3'), True))
    b6 = {s: v for s, v in b5.items() if s != 'IF2_GTP'}
    b6.update(GTP='1', IF2='1')
    witnesses.append(construct('P6', [('P6:IF2-PREP', low.rid(445), 'P6:IF2-PREP')] + b0events + p1events,
                               b6, E1, rx, ('MetRS', 'MTF', 'IF1', 'IF3'), True))
    encounter = next(iter(rx[low.rid(13)]['products']))
    witnesses.append(construct('P7', p2events + [('P7:ENCOUNTER', low.rid(13), 'P7:ENCOUNTER')],
                               {**initial, 'EFTu_GTP_GlytRNAGlyGCC': '1'}, encounter, rx, ('IF1', 'IF3')))
    links = [{'left': 'P1', 'right': 'P4', 'species': dual, 'classification': 'ALTERNATIVE_ENTRY'},
             {'left': 'P1', 'right': 'P3', 'species': exit_state, 'classification': 'ALTERNATIVE_ROUTE'},
             {'left': 'P1', 'right': 'P1-RELEASE-ALT', 'species': E1, 'classification': 'ALTERNATIVE_FACTOR_RELEASE'}]
    for w in witnesses:
        w['alternative_entry_links'] = [x for x in links if w['witness_id'] in (x['left'], x['right'])]
        w['true_rejoin_species'] = sorted({x['species'] for x in w['alternative_entry_links']})
    selected = set().union(*(set(w['source_reaction_ids']) for w in witnesses))
    local_anchors = {s for r in selected for k in ('reactants', 'products') for s in rx[r][k]
                     if s not in RESOURCES and (s.startswith(('RS30S', 'RS50S', 'RS70S', 'IF1', 'IF2', 'IF3')) or s in
                                               {E1, E2, 'MettRNAfMetCAU', 'fMettRNAfMetCAU'})}
    appendix = incidence | selected | {low.rid(414)}
    appendix |= {r for r, q in rx.items() if (set(q['reactants']) | set(q['products'])) & local_anchors}
    appendix |= {t for r in list(appendix) for t in rx[r]['reverse_reaction_ids']}
    records = {}
    for rid in sorted(appendix):
        records[rid] = {**rx[rid], 'reaction_family_id': ann[rid]['reaction_family_id'],
                        'source_subsystems': ann[rid]['level_b_subsystem_candidates'],
                        'reviewed_annotation_status': ann[rid]['functional_annotation_status'],
                        'evidence_status': 'EXTRACTED', 'confidence': 'EXACT_SOURCE_REACTION_VERIFIED',
                        'freshness': 'CANONICAL_HASH_CHECKED_AT_BUILD'}
    # Concrete subsystem provenance remains distinct from reviewed context.
    for p in sorted((ROOT / 'models/pnas2017_full_reference/original/subsystems').glob('*.xml')):
        ids = {n.get('id') for n in ET.parse(p).getroot().iter() if n.tag.endswith('}reaction')}
        for r in ids & appendix:
            records[r].setdefault('subsystem_source_files', []).append(p.relative_to(ROOT).as_posix())
    source_scope = {'source_reactions_indexed': len(rx), 'initiation_classified_reaction_ids': sorted(classified),
                    'search_scope_reaction_ids': sorted(core), 'source_incidence_inventory_ids': sorted(appendix),
                    'unique_witness_reaction_ids': sorted(selected), 'additional_context_reaction_ids': sorted(appendix - selected),
                    'search_limits': {'max_states_per_leg': 50000, 'max_depth_per_leg': 16, 'tie_break': 'SORTED_ORIGINAL_ID'},
                    'discovery': discovery, 'reactions': records, 'unresolved_reactions': [],
                    'unresolved_path_completeness': 'ALL OTHER PATHS NOT ENUMERATED; NO FULL INITIATION COMPLETENESS CLAIM',
                    'source_provenance': [low.provenance(p, a) for p, a in [(low.SOURCE, 'CANONICAL_SBML'),
                        (low.CSV, 'AUTHOR_PARAMETER_COPY'), (low.ARCHIVE, 'AUTHOR_PARAMETER_ARCHIVE'), (low.V2, 'REVIEWED_V2'),
                        ('docs/reduction/pathways/phase_b0_handoff_witnesses.json', 'ACCEPTED_B0_EVENT_RECORD')]]}
    source_scope['coverage'] = {'initiation_classified': len(classified), 'bounded_search_scope': len(core),
        'bounded_inventory': len(appendix), 'unique_witness_directions': len(selected),
        'inventory_enabled': sum(F(rx[r]['reference_parameter']) > 0 for r in appendix),
        'inventory_disabled': sum(F(rx[r]['reference_parameter']) == 0 for r in appendix),
        'search_enabled': len(enabled), 'search_disabled': len(core) - len(enabled),
        'original_species_in_inventory': len({s for r in appendix for k in ('reactants', 'products') for s in rx[r][k]}),
        'participating_families': sorted({ann[r]['reaction_family_id'] for r in appendix})}
    competitions = {s: sorted(r for r, q in rx.items() if s in q['reactants']) for s in sorted(local_anchors)}
    data = {'schema_version': 1, 'phase': 'B1-1', 'authorization': AUTH, 'scientific_status': 'PENDING_HUMAN_REVIEW',
            'witnesses': sorted(witnesses, key=lambda w: w['witness_id']), 'alternative_routes': links,
            'competition_outlets': competitions, 'shared_met_trna_pool': {'species_id': 'MettRNAfMetCAU',
                'required_competitors': list(map(low.rid, (420, 422, 288))), 'pool_semantics': 'ONE_ORIGINAL_SPECIES_POOL'},
            'direction_semantics': {'re0000000449': {'exact_inverse': low.rid(450), 'binding_irreversible': False,
                                                     'automatically_fired_inverse': False}},
            'source_provenance': source_scope['source_provenance']}
    source_scope['shared_reaction_ids_between_scenarios'] = {
        a['witness_id'] + '__' + b['witness_id']: sorted(set(a['source_reaction_ids']) & set(b['source_reaction_ids']))
        for i, a in enumerate(data['witnesses']) for b in data['witnesses'][i+1:]}
    return data, source_scope


def markdown(data, scope_data):
    rx = scope_data['reactions']
    lines = ['# Phase B1-1 — 启动路径与首次延伸交接', '',
             'Scientific status: `PENDING_HUMAN_REVIEW`. Formal tokens are not concentrations; enabled parameters are not observed flux.', '',
             'E1: `' + E1 + '`. E2: `' + E2 + '`. E1 is initiation exit; E2 follows the separately classified `ELONG_tRNA_release` event.', '',
             'P1/P4 share the dual-factor 30S state; P3 omits IF1; the separate release alternative reaches E1 with IF2 released earlier. '
             'These are exclusive scenarios for one ribosomal carrier, never consecutive output units.', '',
             '| Scenario | Occurrences | Endpoint | Recovered free source states |', '|---|---:|---|---|']
    for w in data['witnesses']:
        lines.append(f"| {w['witness_id']} | {len(w['reaction_occurrences'])} | {w['target_milestone']} | {', '.join(c['species_id'] for c in w['catalyst_recovery_claims'])} |")
    for w in data['witnesses']:
        lines += ['', '## ' + w['witness_id'], '', 'Purpose: ' + w['classification'] + '. Boundary supplies: `' +
                  ', '.join(s + ' × ' + v for s, v in w['initial_marking'].items()) + '`.', '',
                  'Every supply is an explicit conditional assumption. P5/P6 reuse the published W3 occurrences once; '
                  'P2 references P1 event identities once. Independent W3 and 30S histories meet at recruitment; their listing is one topological order.', '']
        last = None
        for e in w['reaction_occurrences']:
            q = rx[e['reaction_id']]
            c = q['level_c']
            group = ('B0 upstream precursor (independent of 30S)' if e['event_id'].startswith('W3:') else
                     'E2 cross-module boundary' if c == 'ELONG_tRNA_release' else
                     'Conditional first elongation binding' if e['reaction_id'] == low.rid(13) else
                     '30S preparation' if c == 'INIT_assembly' else
                     'mRNA / IF2-fMet-tRNA recruitment' if c == 'INIT_tRNA_recruitment' else
                     '50S joining' if c == 'INIT_70S_formation' else
                     'GTP / GDP / PO4 source-state transition' if c == 'INIT_energy_commitment' else 'Factor release / E1')
            if group != last:
                lines += ['### ' + group, '']
                last = group
            inverses = ', '.join(r + ' k=' + rx[r]['reference_parameter'] for r in q['reverse_reaction_ids']) or 'none'
            lines += [f"- **{e['reaction_id']}** ({e['event_id']}): `{e['equation']}`. Context: `{c}`; "
                      f"author k1={q['reference_parameter']} ({q['reference_activity']}); exact inverse: {inverses}."]
            before = ', '.join(s for s in e['inputs'] if s not in RESOURCES)
            after = ', '.join(s for s in e['outputs'] if s not in RESOURCES)
            lines += [f"  Carrier/source states: `{before}` → `{after}`. All co-reactants and outputs are in the full equation."]
        lines += ['', '**Exact structural net (CONCEPTUAL_NET, not a new source reaction or rate law):**', '',
                  '```text', w['net_reaction'], '```', '',
                  'DAG token joins (arrows are exact producer-output dependencies; no extra ordering arrows):', '']
        lines += [f"- `{d['producer_event_id']}` → `{d['consumer_event_id']}`: `{d['original_species_id']}` × {d['stoichiometric_amount']}."
                  for d in w['event_dependencies']]
        lines += ['', 'True rejoins: `' + ', '.join(w['true_rejoin_species']) + '`. IF2_GDP release is not IF2_GTP recovery. '
                  'The E1 source ID omits explicit mRNA naming; no mRNA release or global composition claim is invented.', '']
        states = sorted({s for e in w['reaction_occurrences'] for s in e['inputs']
                         if s in data['competition_outlets'] and len(data['competition_outlets'][s]) > 1})
        lines += ['Competing source exits from this witness\'s actual precursor states (context only; inverse/sink directions are not extra occurrences):', '',
                  '| Original precursor state | Original outgoing directions (reference k1) |', '|---|---|']
        for s in states:
            exits = ', '.join(r + ' (k=' + rx[r]['reference_parameter'] + ')' for r in data['competition_outlets'][s])
            lines.append(f'| `{s}` | {exits} |')
    lines += ['## Alternatives, competition and source incidence', '',
              'All outgoing source directions at every retained anchor are listed in JSON `competition_outlets`, including inverse and disabled sink channels. '
              'At the GDP dual-factor 70S state, 0747 and 0749 are genuine alternative exits; the release-alt witness fires 0749. '
              'No dominance is inferred. 0449/0450 each have k1=40; no inverse occurs automatically. '
              '0420/0422/0288 compete for the single original MettRNAfMetCAU pool; 0289 and all source incidence remain available as context.', '',
              'The following bounded appendix is excluded from witness sums. It preserves complete source equations, full direction IDs, '
              'reverse partners, reviewed contexts and disabled channels. Composite carrier projections remain INFERRED.', '',
              '| Original ID | Complete source equation | Context / family | Author k1 | Exact inverses | Concrete source subsystem |',
              '|---|---|---|---:|---|---|']
    for r, q in rx.items():
        lines.append(f"| {r} | `{q['equation']}` | {q['level_c']} / {q['reaction_family_id']} | {q['reference_parameter']} ({q['reference_activity']}) | "
                     f"{', '.join(q['reverse_reaction_ids']) or 'none'} | {', '.join(q.get('subsystem_source_files', []))} |")
    return '\n'.join(lines) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, default=OUT)
    args = p.parse_args()
    data, evidence = build()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    dump(args.output_dir / 'phase_b1_1_witnesses.json', data)
    dump(args.output_dir / 'phase_b1_1_source_scope.json', evidence)
    (args.output_dir / 'phase_b1_1_initiation_pathways.md').write_bytes(markdown(data, evidence).encode('utf-8'))
    print(json.dumps({'status': 'BUILT', 'coverage': evidence['coverage'], 'events': {w['witness_id']: len(w['reaction_occurrences']) for w in data['witnesses']}}))


if __name__ == '__main__':
    main()
