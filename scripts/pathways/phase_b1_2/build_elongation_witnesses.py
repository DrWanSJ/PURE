#!/usr/bin/env python3
"""Bounded source-state discovery, exact token lots, additive B1-2 reading view."""
from collections import Counter, defaultdict, deque
from fractions import Fraction as F
from pathlib import Path
import argparse
import csv
import hashlib
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
T = 'elRS70SAUAA0004_Pept0003tRNAGlyGCC'
D = 'EFTu_GTP_GlytRNAGlyGCC'
G = 'EFG_GTP'
ENTRY2 = 'elRS70SAGGU0003_Pept0002'
R1 = [E2+'_EFTu_GTP_GlytRNAGlyGCC', E2+'_EFTu_GDP_PO4_GlytRNAGlyGCC',
      E2+'_EFTu_GDP_GlytRNAGlyGCC', E2+'_GlytRNAGlyGCC',
      'elRS70SBGGU0002_Pept0002tRNAGlyGCC',
      'elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP',
      'elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4',
      'elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP',
      'elRS70SAGGU0003_Pept0002tRNAGlyGCC', ENTRY2]
R2 = [ENTRY2+'_EFTu_GTP_GlytRNAGlyGCC', ENTRY2+'_EFTu_GDP_PO4_GlytRNAGlyGCC',
      ENTRY2+'_EFTu_GDP_GlytRNAGlyGCC', ENTRY2+'_GlytRNAGlyGCC',
      'elRS70SBGGU0003_Pept0003tRNAGlyGCC',
      'elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP',
      'elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4',
      'elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP', T]
RES = {'ATP','ADP','AMP','GTP','GDP','PO4','PPi','Gly','Met','FD','THF'}
LEDGER = sorted(RES | {D,G,'EFTu_GDP','EFTu_GTP','EFTu','EFG_GDP','EFG',
                       'tRNAGlyGCC','GlytRNAGlyGCC','tRNAfMetCAU','fMettRNAfMetCAU',E1,E2,T,ENTRY2})
SUBDIR = ROOT/'models/pnas2017_full_reference/original/subsystems'
ELONG = {'Elongation_A_Gly.xml','Elongation_A_Met.xml','Elongation_B.xml',
         'Elongation_Ca1_GlyGCC.xml','Elongation_Ca1_fMetCAU.xml',
         'Elongation_Ca2_pept0002.xml','Elongation_Ca2_pept0003.xml'}
AUTH = {'phase_b1_2_execution_authorized': True, 'phase_b1_2_scientific_status': 'PENDING_HUMAN_REVIEW',
        'phase_b1_2_formally_accepted': False, 'commit_push_authorized': False, 'qssa_authorized': False,
        'kinetic_reduction_authorized': False, 'termination_authorized': False,
        'phase_b1_3_authorized': False, 'full_phase_b_authorized': False}

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def save(p, d):
    Path(p).write_bytes((json.dumps(d, sort_keys=True, indent=2, ensure_ascii=False)+'\n').encode('utf-8'))

def membership(rx):
    """Map local IDs by both exact sides; never treat local re25 as combined 0025."""
    sig = defaultdict(list)
    for rid,q in rx.items():
        sig[(tuple(sorted(q['reactants'].items())),tuple(sorted(q['products'].items())))].append(rid)
    mapped = defaultdict(list)
    for p in sorted(SUBDIR.glob('*.xml')):
        model = ET.parse(p).getroot().find(low.SB+'model')
        for n in model.findall(low.SB+'listOfReactions/'+low.SB+'reaction'):
            sides = []
            for side in ('Reactants','Products'):
                terms = defaultdict(F)
                for ref in n.findall(low.SB+'listOf'+side+'/'+low.SB+'speciesReference'):
                    math = ref.find(low.SB+'stoichiometryMath/'+low.MM+'math')
                    terms[ref.get('species')] += low.constant(math) if math is not None else F(ref.get('stoichiometry','1'))
                sides.append(tuple(sorted(low.exact(terms).items())))
            matches = sig[tuple(sides)]
            if len(matches) != 1:
                raise ValueError('UNRESOLVED_SUBSYSTEM_MAPPING: '+p.name+':'+n.get('id')+':'+str(matches))
            mapped[matches[0]].append({'source_file':p.relative_to(ROOT).as_posix(),
                'local_reaction_id':n.get('id'),'model_id':model.get('id'),
                'mapping_basis':'EXACT_BOTH_SIDES_RATIONAL_STOICHIOMETRY','evidence_status':'EXTRACTED'})
    return mapped

def inventory(rx):
    ann = {r['reaction_id']:r for r in csv.DictReader((ROOT/low.V2).open(encoding='utf-8-sig',newline=''))}
    members = membership(rx)
    context = {r for r,a in ann.items() if any(c.startswith('ELONG_') for c in a['level_c_functional_contexts'].split(';'))}
    local = {r for r,ms in members.items() if any(Path(m['source_file']).name in ELONG for m in ms)}
    core = context | local
    # Species namespace selection is a context projection, not a moiety inference.
    anchors = {s for r in core for side in ('reactants','products') for s in rx[r][side]
               if s.startswith('elRS') or s in {D,G,'EFTu','EFTu_GDP','EFTu_GTP','EFG','EFG_GDP','GlytRNAGlyGCC','tRNAGlyGCC','tRNAfMetCAU'}}
    anchors |= {E1,E2,T}
    incident = {r for r,q in rx.items() if anchors & (set(q['reactants'])|set(q['products']))}
    inverse = {t for r in core for t in rx[r]['reverse_reaction_ids']}
    selected = core|incident|inverse
    rows = {}
    for r,q in sorted(rx.items()):
        if r not in selected: kind = 'OUT_OF_B1_2_SCOPE'
        elif F(q['reference_parameter']) == 0: kind = 'DISABLED_SOURCE_CONTEXT'
        elif r in core: kind = 'ELONGATION_SEARCH_SCOPE'
        elif r in inverse: kind = 'REVERSE_OR_COMPETING_CONTEXT'
        else: kind = 'BOUNDARY_CONTEXT_ONLY'
        rows[r] = {**q,'classification':kind,'core_membership':r in core,
            'selection_reasons':[k for k,v in [('ELONG_LEVEL_C',r in context),('ORIGINAL_ELONG_SUBSYSTEM',r in local),
                ('ONE_HOP_CARRIER_INCIDENCE',r in incident),('EXACT_REVERSE',r in inverse)] if v],
            'reaction_family_id':ann[r]['reaction_family_id'],'source_subsystem_contexts':ann[r]['level_b_subsystem_candidates'],
            'original_subsystem_memberships':members[r], 'evidence_status':'EXTRACTED',
            'confidence':'EXACT_SOURCE_DIRECTION','freshness':'TASK_CANONICAL_HASH_CHECKED'}
    allowed = sorted(r for r in core if F(rx[r]['reference_parameter'])>0 and
                     not any(c.startswith(('TERM_','INIT_')) for c in rx[r]['level_c'].split(';')) and r!='re0000000001')
    return {'reactions':rows,'core_direction_ids':sorted(core),'search_direction_ids':allowed,
            'selected_inventory_direction_ids':sorted(selected),'carrier_incidence_species':sorted(anchors),
            'coverage':{'entire_model_inventory':len(rx),'selected_inventory':len(selected),'core_directions':len(core),
                'search_directions':len(allowed),'core_positive':sum(F(rx[r]['reference_parameter'])>0 for r in core),
                'core_zero':sum(F(rx[r]['reference_parameter'])==0 for r in core),
                'inventory_positive':sum(F(rx[r]['reference_parameter'])>0 for r in selected),
                'inventory_zero':sum(F(rx[r]['reference_parameter'])==0 for r in selected),
                'context_only_directions':len(selected-core),'classification_counts':dict(sorted(Counter(v['classification'] for v in rows.values()).items())),
                'selected_family_ids':sorted({ann[r]['reaction_family_id'] for r in selected})},
            'unresolved_classifications':[], 'coverage_limit':'ALL_SELECTED_DIRECTIONS; REPRESENTATIVE_WITNESSES_NOT_ALL_ROUTES',
            'boundary_incidence':{s:{'producers':sorted(r for r,q in rx.items() if s in q['products']),
                                    'consumers':sorted(r for r,q in rx.items() if s in q['reactants'])} for s in (E1,E2,ENTRY2,T)},
            'source_provenance':[low.provenance(p,a) for p,a in [(low.SOURCE,'CANONICAL_SBML'),(low.CSV,'AUTHOR_CSV'),
                (low.ARCHIVE,'AUTHOR_ZIP'),(low.V2,'REVIEWED_CONTEXT_ONLY')]]+
                [low.provenance(p.relative_to(ROOT).as_posix(),'ORIGINAL_SUBSYSTEM') for p in sorted(SUBDIR.glob('*.xml'))]}

def seed(boundary):
    pool = {}
    for s,amount in sorted(boundary.items()):
        v = F(amount)
        if v.denominator!=1: raise ValueError('Finite explicit boundary lots require integer supplies here')
        for i in range(int(v)): pool[('BOUNDARY:'+s+':'+str(i+1).zfill(2),s)]=F(1)
    return pool

def marking(pool):
    m=defaultdict(F)
    for (_,s),v in pool.items(): m[s]+=v
    return low.exact(m)

def fire(pool,r,eid):
    nxt=dict(pool); origins=[]
    for s,amount in sorted(r['reactants'].items()):
        need=F(amount)
        for key in sorted(nxt):
            if key[1]!=s or nxt[key]<=0:continue
            take=min(need,nxt[key])
            if take:
                origins.append({'species_id':s,'amount':str(take),'origin':key[0]})
                nxt[key]-=take;need-=take
            if need==0:break
        if need:raise ValueError('MISSING_REQUIRED_INPUT: '+eid+' '+s)
    for s,v in r['products'].items():nxt[eid,s]=F(v)
    return {k:v for k,v in nxt.items() if v},origins

def key(pool):return tuple(sorted((o,s,v) for (o,s),v in pool.items() if v))

def discover(boundary,targets,allowed,rx,max_states=50000,max_depth=16,max_total=64):
    pool=seed(boundary);whole=[];evidence=[]
    for target in targets:
        queue=deque([(pool,[])]);seen={(key(pool),tuple(whole))};expanded=0;depth_cut=False;found=None
        while queue:
            p,route=queue.popleft();expanded+=1
            m={s:F(v) for s,v in marking(p).items()}
            if m.get(target,F())>=1:found=(p,route);break
            if len(route)>=max_depth:depth_cut=True;continue
            for rid in allowed:
                q=rx[rid]
                if not all(m.get(s,F())>=F(v) for s,v in q['reactants'].items()):continue
                eid='DISCOVERY:E'+str(len(whole)+len(route)+1).zfill(2)
                nxt,_=fire(p,q,eid)
                # Keep the full source-event ancestry: equal markings and equal
                # event-number origins must not merge distinct carrier histories.
                k=(key(nxt),tuple(whole+route+[rid]))
                if k in seen:continue
                if len(seen)>=max_states:raise ValueError('SEARCH_INCONCLUSIVE: state bound at '+target)
                seen.add(k);queue.append((nxt,route+[rid]))
        if found is None:raise ValueError(('SEARCH_INCONCLUSIVE' if depth_cut else 'NO_ROUTE_IN_FINITE_CONDITIONAL_INVENTORY')+': '+target)
        pool,route=found;whole+=route
        if len(whole)>max_total:raise ValueError('SEARCH_INCONCLUSIVE: total event bound')
        evidence.append({'waypoint_source_state':target,'visited_states':len(seen),'expanded_states':expanded,
            'leg_event_count':len(route),'selected_original_ids':route,'status':'REACHED',
            'bounds':{'max_states':max_states,'max_depth':max_depth,'max_total_events':max_total},
            'state_identity':'COMPLETE_RATIONAL_MARKING_ORIGIN_LOTS_AND_SOURCE_EVENT_HISTORY','tie_break':'SORTED_SOURCE_IDS_NO_KINETIC_PRIORITY'})
    return whole,evidence

def construct(wid,ids,boundary,target,rx,waypoints,discovery=None,upstream=None):
    pool=seed(boundary);events=[];dag=[];trace=[];net=defaultdict(F)
    for i,rid in enumerate(ids):
        eid=f'{wid}:E{i+1:02d}';q=rx[rid];before=marking(pool)
        pool,origins=fire(pool,q,eid)
        for x in origins:
            if not x['origin'].startswith('BOUNDARY:'):
                dag.append({'producer_event_id':x['origin'],'consumer_event_id':eid,
                            'species_id':x['species_id'],'amount':x['amount'],'evidence_status':'EXTRACTED'})
        for s,v in q['reactants'].items():net[s]-=F(v)
        for s,v in q['products'].items():net[s]+=F(v)
        events.append({'event_id':eid,'reaction_id':rid,'inputs':q['reactants'],'outputs':q['products'],
            'equation':q['equation'],'input_origins':origins,'reference_parameter':q['reference_parameter'],
            'reference_activity':q['reference_activity'],'level_c_contexts':q['level_c'],
            'occurrence_origin': upstream['event_origins'][i] if upstream and i<len(upstream['event_origins']) else eid})
        trace.append({'event_id':eid,'marking_before':before,'marking_after':marking(pool)})
    final=marking(pool)
    # These carrier labels annotate exact participants; molecular composition is not certified.
    streams=[]
    for e in events:
        c=e['level_c_contexts']
        roles=['RIBOSOMAL_SOURCE_STATE','PEPTIDE_SOURCE_STATE']
        if 'aa_tRNA' in c or 'peptide_formation' in c or 'tRNA_release' in c:roles+=['TRNA_SOURCE_TRANSITION']
        if any(s in e['inputs'] or s in e['outputs'] for s in (D,'EFTu_GDP')) or '_EFTu_' in e['equation']:roles+=['EFTU_SOURCE_CARRIER']
        if any(s in e['inputs'] or s in e['outputs'] for s in (G,'EFG_GDP')) or '_EFG_' in e['equation']:roles+=['EFG_SOURCE_CARRIER']
        streams.append({'event_id':e['event_id'],'context_roles':roles,'exact_inputs':e['inputs'],'exact_outputs':e['outputs'],
            'source_state_evidence':'EXTRACTED','physiological_identity':'INFERRED','basis':'CANONICAL_EVENTS_AND_REVIEWED_CONTEXT; NO_MOIETY_CERTIFICATE'})
    return {'witness_id':wid,'starting_source_state':E1 if upstream else E2,'target_source_state':target,
        'reaction_occurrences':events,'occurrence_vector':dict(sorted(Counter(ids).items())),
        'initial_marking':low.exact({s:F(v) for s,v in boundary.items()}),'boundary_lots':[
            {'origin':o,'species_id':s,'amount':str(v),'conditional':True,'author_initial_concentration':False} for (o,s),v in sorted(seed(boundary).items())],
        'final_marking':final,'per_event_markings':trace,'event_dependencies':dag,'carrier_streams':streams,
        'exact_net_stoichiometry':low.exact(net),'net_reaction':low.equation(low.exact({s:-v for s,v in net.items() if v<0}),low.exact({s:v for s,v in net.items() if v>0})),
        'resource_ledger':{s:{'initial':str(boundary.get(s,0)),'final':final.get(s,'0'),'net':str(net.get(s,0)),
                              'event_membership': [e['event_id'] for e in events if s in e['inputs'] or s in e['outputs']]} for s in LEDGER},
        'waypoints':waypoints,'search_evidence':discovery or [],'upstream_evidence':upstream,
        'claims':{'EFTu_GDP_is_GTP_recovery':False,'EFG_GDP_is_GTP_recovery':False,
                  'global_moiety_conservation':False,'full_molecular_composition_verified':False,
                  'kinetic_preference_measured':False,'termination_completed':False},
        'scientific_status':'PENDING_HUMAN_REVIEW'}

def build():
    rx=low.read_source();inv=inventory(rx);allowed=inv['search_direction_ids']
    specs=[('W1',{E2:'1',D:'1'},R1[:1]),('W2',{E2:'1',D:'1',G:'1'},R1),
           ('W3',{E2:'1',D:'2',G:'2'},R1+R2)]
    ws=[]
    for wid,b,targets in specs:
        ids,ev=discover(b,targets,allowed,rx)
        ws.append(construct(wid,ids,b,targets[-1],rx,targets,ev))
    upath='docs/reduction/pathways/phase_b1_1_followup_witness.json'
    u=load(ROOT/upath)['new_witness']
    signed=load(OUT/'phase_b1_1_formal_signoff_2026-10-09.json')
    assert signed['IF3_first_witness']['original_reaction_sequence']==[e['reaction_id'] for e in u['reaction_occurrences']]
    assert u['target_milestone']==E1
    boundary={**u['initial_marking'],D:'2',G:'2'}
    meta={'path':upath,'sha256':hashlib.sha256((ROOT/upath).read_bytes()).hexdigest(),
          'accepted_witness_id':u['witness_id'],'event_origins':[e['occurrence_origin'] for e in u['reaction_occurrences']],
          'signed_authority':'docs/reduction/pathways/phase_b1_1_formal_signoff_2026-10-09.json',
          'upstream_discovery_rerun':False,'route_exclusivity':'SINGLE_ACCEPTED_IF3_FIRST_SCENARIO'}
    w3=ws[-1]
    ids=[e['reaction_id'] for e in u['reaction_occurrences']]+['re0000000001']+[e['reaction_id'] for e in w3['reaction_occurrences']]
    ws.append(construct('W4',ids,boundary,T,rx,[E1,E2]+R1+R2,upstream=meta))
    selected_species={s for w in ws[:3] for e in w['reaction_occurrences'] for side in ('inputs','outputs') for s in e[side] if s not in RES}
    outlets={s:sorted(r for r,q in rx.items() if s in q['reactants']) for s in sorted(selected_species)}
    data={'phase':'B1-2','schema':'source-exact-elongation-v1','authorization':AUTH,'witnesses':ws,
          'competition_outlets':outlets,'selected_source_states':sorted(selected_species),
          'interpretation':'EXTRACTED_SOURCE_STATE_TRANSITIONS; INFERRED_PHYSIOLOGICAL_ROLES',
          'branch_variants':'OFF_PATH_OUTLETS_RETAINED; NO_DOMINANCE_OR_FULL_ROUTE_ENUMERATION',
          'unresolved':['Composite molecular/peptide/mRNA identities not independently certified',
                        'Detailed physiological timing and source step correspondence require researcher review',
                        'Formal supplies do not certify full-model availability','Complete SI text/PDF not frozen locally'],
          'source_provenance':inv['source_provenance']}
    inv['selected_intermediate_outlets']=outlets
    inv['termination_boundary_appendix']={r:inv['reactions'][r] for r in sorted(set(inv['boundary_incidence'][T]['producers']+inv['boundary_incidence'][T]['consumers']))}
    return data,inv

def reading(data,inv):
    ws={w['witness_id']:w for w in data['witnesses']};w=ws['W3']
    text=['# Phase B1-2: two Gly elongation rounds', '',
        '**Scientific status: PENDING_HUMAN_REVIEW; formally accepted: false.** This is structural source reconstruction.', '',
        f'Source E2 `{E2}` -> first peptide-bearing states -> second-round entry `{ENTRY2}` -> proposed T_pre `{T}`.', '',
        'Boundary supplies are conditional formal tokens: E2 x1, EFTu_GTP_GlytRNAGlyGCC x2, EFG_GTP x2. They are not author initial concentrations. Each delivery/factor token has its own origin lot.', '',
        'EXTRACTED means exact canonical source species/equation. Functional labels come unchanged from reviewed Level-C. Physiological role and complete composite composition remain INFERRED. Shared nucleotide pools do not identify a carrier.', '',
        '## Independent-review net expectation', '', 'CONCEPTUAL_NET (derived event sum; not a new source reaction or effective kinetic law):', '', '```text',w['net_reaction'],'```','',
        'The independent verifier reparses source and recomputes this net. Free GTP/GDP/ATP/ADP/AMP/PPi have zero change: none occurs in the principal event equations. Four PO4 are released; two EFTu_GDP and two EFG_GDP remain free. One tRNAGlyGCC is released between rounds; the second tRNA is represented in T_pre. These are source-state statements, not elemental or global nucleotide-moiety conservation.', '',
        'EF-Tu and EF-G GTP are already represented inside supplied composite species. No extra free GTP is charged. GDP-form release is not GTP-form regeneration. fMet-tRNA release belongs to the single upstream 0001 event and does not occur in W3.', '']
    for title,events in [('Round 1: fMet -> Pept0002',w['reaction_occurrences'][:len(R1)]),('Round 2: Pept0002 -> Pept0003',w['reaction_occurrences'][len(R1):])]:
        text+=['## '+title,'']
        for e in events:
            q=inv['reactions'][e['reaction_id']]
            text+=['### '+e['event_id']+' / '+e['reaction_id'], '',
                'Level-C: `'+e['level_c_contexts']+'`; source event: EXTRACTED; biochemical interpretation: INFERRED.', '',
                '```text', e['equation'],'```','',
                'Original subsystem: '+('; '.join(m['source_file']+' / '+m['local_reaction_id'] for m in q['original_subsystem_memberships']) or 'no exact local membership'),'',
                'This equation retains every input/output source state, factor-bound nucleotide state, tRNA/peptide-bearing state and free output. The per-event marking, exact consumed lots and producer-consumer edges are in the witness JSON.', '',
                'Parameter: `'+e['reference_parameter']+'`; '+e['reference_activity']+'. Exact reverse direction(s): '+(', '.join(q['reverse_reaction_ids']) or 'none')+'. No reverse is fired automatically.', '']
    text+=['## Staged witnesses and accepted upstream composition','', '| Witness | Target | Events | Original sequence |','|---|---|---:|---|']
    for x in data['witnesses']:
        text.append('| '+x['witness_id']+' | `'+x['target_source_state']+'` | '+str(len(x['reaction_occurrences']))+' | '+ ' -> '.join(e['reaction_id'] for e in x['reaction_occurrences'])+' |')
    text+=['','W1 revalidates the P7 binding interface. W4 imports only the signed IF3-first E1 scenario, adds 0001 once, and composes W3; it does not mix alternative initiation histories. IF1 and IF3 recovery is source-free-state recovery; IF2_GDP adds one PO4 to W4. External two EF-Tu and two EF-G supplies remain conditional.','',
           '## Source resource ledger for W3','', '| Source species | Initial | Final | Net |','|---|---:|---:|---:|']
    for s,l in w['resource_ledger'].items():text.append(f"| `{s}` | {l['initial']} | {l['final']} | {l['net']} |")
    text+=['','## Competing exits, reverse channels, disabled paths and exact rejoins','',
        'All original outlets of every selected non-resource source state appear below, including off-path channels and disabled directions. Shared composite source-state identities define possible rejoins; free resource pools alone do not. Alternatives are separate potential scenarios and are never extra mandatory events.','']
    for s,ids in data['competition_outlets'].items():
        text+=['### `'+s+'`','']
        for rid in ids:
            q=inv['reactions'][rid]
            text+=['- `'+rid+'`; '+q['level_c']+'; k1='+q['reference_parameter']+'; '+q['reference_activity']+'; '+q['classification']+
                   '; reverse='+','.join(q['reverse_reaction_ids'])+'; equation: `'+q['equation']+'`.']
        text+=['']
    text+=['## Read-only T_pre / termination interface','',
        '0086 produces the proposed endpoint and EFG_GDP. T_pre also participates in RF1/RF2 binding, their reverses, disabled EF-G association and degradation. No termination event is executed in W1-W4; no free Pept0003 product is claimed.','']
    for r,q in inv['termination_boundary_appendix'].items():text+=['- `'+r+'` / '+q['level_c']+' / '+q['reference_activity']+': `'+q['equation']+'`.']
    text+=['','## Coverage, interpretation and source authority','', '```json',json.dumps(inv['coverage'],sort_keys=True,indent=2),'```','',
        'Inventory selection is the union of exact original subsystem membership and ELONG contexts, augmented by one-hop carrier incidence and exact reverse metadata. It is not an ID interval. Positive author parameters mean REFERENCE_ENABLED, not measured flux, dominance, equilibrium or guaranteed occupancy. Sorted IDs are search tie-breakers only.','',
        'The local article (Matsuura et al. 2017, DOI 10.1073/pnas.1615351114), p.2 and p.8, describes 241 components / 968 reactions and construction by functional subsystems. Page 7 discusses deactivating reaction 22 as EF-G GTP hydrolysis on translating ribosomes. This supports that limited context; it does not experimentally certify all composite names or the source-model early tRNA-release order. Complete standalone SI text/PDF remains unavailable locally.','',
        'Original S27 calls E2 and the second-round entry virtual elongation complexes. Its author definitions describe the peptide-bearing states and hydrolysis/phosphate-release/translocation steps. These definitions are EXTRACTED author-model documentation; full molecular composition and physiological identity remain INFERRED/UNRESOLVED. The proposed T_pre is factor-free and has UAA at the A site; S27 calls the RF1/RF2-bound successors pre-termination complexes. The proposed boundary label remains pending H6.','',
        'S05-S11 and S27 local XLSX source evidence are inspected separately in [the original-source interpretation appendix](phase_b1_2_original_source_evidence.md). Seven elongation workbook models map 244 local reaction rows with no equation discrepancy; 44 relevant S27 parameter rows agree with the author CSV. Secondary literature references in the paper do not replace independently inspected evidence. H1-H7 remain PENDING.','',
        'Finite search counts are retained per waypoint. Reaching T_pre is one structural witness, not complete elongation-network coverage, full-model feasibility or elapsed-time dynamics.','']
    return '\n'.join(text)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=OUT);a=p.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    data,inv=build()
    save(a.output_dir/'phase_b1_2_witnesses.json',data);save(a.output_dir/'phase_b1_2_source_scope.json',inv)
    (a.output_dir/'phase_b1_2_elongation_pathways.md').write_bytes((reading(data,inv)+'\n').encode('utf-8'))
    print(json.dumps({'status':'BUILT_PENDING_INDEPENDENT_VERIFICATION','events':{w['witness_id']:len(w['reaction_occurrences']) for w in data['witnesses']},'coverage':inv['coverage']}))
    return 0

if __name__=='__main__':raise SystemExit(main())
