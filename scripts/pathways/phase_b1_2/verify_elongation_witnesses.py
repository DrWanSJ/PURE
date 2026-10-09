#!/usr/bin/env python3
"""Independent B1-2 acceptance; no B1-2 builder imports or classification oracle."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/reduction/pathways'
sys.path.insert(0,str(ROOT/'scripts/pathways/phase_b0'))
import verify_phase_b0_witnesses as a
need,Rejection=a.need,a.Rejection
E1='elRS70SAGGU0002_fMettRNAfMetCAU';E2='elRS70SAGGU0002_fMet'
T='elRS70SAUAA0004_Pept0003tRNAGlyGCC';D='EFTu_GTP_GlytRNAGlyGCC';G='EFG_GTP'
ENTRY='elRS70SAGGU0003_Pept0002'
FIRST=[E2+'_EFTu_GTP_GlytRNAGlyGCC',E2+'_EFTu_GDP_PO4_GlytRNAGlyGCC',E2+'_EFTu_GDP_GlytRNAGlyGCC',
       E2+'_GlytRNAGlyGCC','elRS70SBGGU0002_Pept0002tRNAGlyGCC',
       'elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GTP','elRS70SBGGU0002_Pept0002tRNAGlyGCC_EFG_GDP_PO4',
       'elRS70SCGGU0003_Pept0002tRNAGlyGCC_EFG_GDP','elRS70SAGGU0003_Pept0002tRNAGlyGCC',ENTRY]
SECOND=[ENTRY+'_EFTu_GTP_GlytRNAGlyGCC',ENTRY+'_EFTu_GDP_PO4_GlytRNAGlyGCC',ENTRY+'_EFTu_GDP_GlytRNAGlyGCC',
        ENTRY+'_GlytRNAGlyGCC','elRS70SBGGU0003_Pept0003tRNAGlyGCC',
        'elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GTP','elRS70SBGGU0003_Pept0003tRNAGlyGCC_EFG_GDP_PO4',
        'elRS70SCUAA0004_Pept0003tRNAGlyGCC_EFG_GDP',T]
RESOURCE={'ATP','ADP','AMP','GTP','GDP','PO4','PPi','Gly','Met','FD','THF'}
LEDGER=sorted(RESOURCE|{D,G,'EFTu_GDP','EFTu_GTP','EFTu','EFG_GDP','EFG','tRNAGlyGCC','GlytRNAGlyGCC',
                      'tRNAfMetCAU','fMettRNAfMetCAU',E1,E2,T,ENTRY})
ELONG={'Elongation_A_Gly.xml','Elongation_A_Met.xml','Elongation_B.xml','Elongation_Ca1_GlyGCC.xml',
       'Elongation_Ca1_fMetCAU.xml','Elongation_Ca2_pept0002.xml','Elongation_Ca2_pept0003.xml'}
AUTH={'phase_b1_2_execution_authorized':True,'phase_b1_2_scientific_status':'PENDING_HUMAN_REVIEW',
      'phase_b1_2_formally_accepted':False,'commit_push_authorized':False,'qssa_authorized':False,
      'kinetic_reduction_authorized':False,'termination_authorized':False,'phase_b1_3_authorized':False,'full_phase_b_authorized':False}

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,d):Path(p).write_bytes((json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))

def sources():
    s=a.parse_sources()
    s['annotations']={x['reaction_id']:x for x in csv.DictReader(a.V2.open(encoding='utf-8-sig',newline=''))}
    return s

def source_hashes(source, overrides=None):
    """Override paths only for disposable adversarial copies, never canonical writes."""
    for p,h in a.PINNED.items():need(a.digest((overrides or {}).get(p,p))==h,'SOURCE_HASH_MISMATCH',str(p))
    return a.check_source_integrity(source)

def independent_memberships(source):
    rx=source['reactions'];signatures=defaultdict(list)
    def sig(q):return tuple(sorted(q['reactants'].items())),tuple(sorted(q['products'].items()))
    for r,q in rx.items():signatures[sig(q)].append(r)
    members=defaultdict(list)
    for p in sorted((ROOT/'models/pnas2017_full_reference/original/subsystems').glob('*.xml')):
        model=ET.parse(p).getroot().find('s:model',a.NS)
        for n in model.findall('s:listOfReactions/s:reaction',a.NS):
            q={}
            for side,tag in [('reactants','Reactants'),('products','Products')]:
                vals=defaultdict(F)
                for ref in n.findall(f's:listOf{tag}/s:speciesReference',a.NS):
                    math=ref.find('s:stoichiometryMath/m:math',a.NS)
                    vals[ref.get('species')]+=a.number(math) if math is not None else F(ref.get('stoichiometry','1'))
                q[side]=dict(vals)
            ids=signatures[sig(q)];need(len(ids)==1,'SOURCE_PROVENANCE_MISMATCH',p.name+':'+n.get('id'))
            members[ids[0]].append({'source_file':p.relative_to(ROOT).as_posix(),'local_reaction_id':n.get('id'),
                'model_id':model.get('id'),'mapping_basis':'EXACT_BOTH_SIDES_RATIONAL_STOICHIOMETRY','evidence_status':'EXTRACTED'})
    return members

def expected_scope(source):
    rx=source['reactions'];ann=source['annotations'];members=independent_memberships(source)
    context={r for r,x in ann.items() if any(c.startswith('ELONG_') for c in x['level_c_functional_contexts'].split(';'))}
    local={r for r,ms in members.items() if any(Path(x['source_file']).name in ELONG for x in ms)}
    core=context|local
    anchors={s for r in core for side in ('reactants','products') for s in rx[r][side]
             if s.startswith('elRS') or s in {D,G,'EFTu','EFTu_GDP','EFTu_GTP','EFG','EFG_GDP','GlytRNAGlyGCC','tRNAGlyGCC','tRNAfMetCAU'}}|{E1,E2,T}
    incident={r for r,q in rx.items() if anchors&(set(q['reactants'])|set(q['products']))}
    reverses={r:sorted(t for t,v in rx.items() if v['reactants']==q['products'] and v['products']==q['reactants']) for r,q in rx.items()}
    inverse={t for r in core for t in reverses[r]};selected=core|incident|inverse
    classes={}
    for r in rx:
        classes[r]='OUT_OF_B1_2_SCOPE' if r not in selected else 'DISABLED_SOURCE_CONTEXT' if source['parameters'][r]==0 else \
          'ELONGATION_SEARCH_SCOPE' if r in core else 'REVERSE_OR_COMPETING_CONTEXT' if r in inverse else 'BOUNDARY_CONTEXT_ONLY'
    allowed=sorted(r for r in core if source['parameters'][r]>0 and
                   not any(c.startswith(('TERM_','INIT_')) for c in ann[r]['level_c_functional_contexts'].split(';')) and r!='re0000000001')
    counts={'entire_model_inventory':len(rx),'selected_inventory':len(selected),'core_directions':len(core),'search_directions':len(allowed),
        'core_positive':sum(source['parameters'][r]>0 for r in core),'core_zero':sum(source['parameters'][r]==0 for r in core),
        'inventory_positive':sum(source['parameters'][r]>0 for r in selected),'inventory_zero':sum(source['parameters'][r]==0 for r in selected),
        'context_only_directions':len(selected-core),'classification_counts':dict(sorted(Counter(classes.values()).items())),
        'selected_family_ids':sorted({ann[r]['reaction_family_id'] for r in selected})}
    return locals()

def check_scope(inv,source):
    x=expected_scope(source);rx=source['reactions']
    need(set(inv['reactions'])==set(rx),'INCORRECT_SOURCE_SCOPE','all 968 inventory rows')
    for r,row in inv['reactions'].items():
        q=rx[r];ann=source['annotations'][r]
        need(a.fractions(row['reactants'])==q['reactants'] and a.fractions(row['products'])==q['products'], 'SOURCE_REACTION_MISMATCH',r)
        need(row['equation']==a.equation(q['reactants'],q['products']),'SOURCE_EQUATION_MISMATCH',r)
        k=source['parameters'][r]
        need(F(row['reference_parameter'])==k and row['reference_activity']==('REFERENCE_ENABLED' if k>0 else 'REFERENCE_DISABLED'), 'REFERENCE_ACTIVITY_MISMATCH',r)
        need(row['classification']==x['classes'][r] and row['core_membership']==(r in x['core']),'INCORRECT_SOURCE_SCOPE',r)
        need(row['reverse_reaction_ids']==x['reverses'][r],'REVERSE_PAIR_MISMATCH',r)
        need(row['level_c']==ann['level_c_functional_contexts'] and row['reaction_family_id']==ann['reaction_family_id'] and
             row['source_subsystem_contexts']==ann['level_b_subsystem_candidates'],'ANNOTATION_MISMATCH',r)
        need(row['original_subsystem_memberships']==x['members'][r],'SOURCE_PROVENANCE_MISMATCH',r)
        reasons=[k for k,v in [('ELONG_LEVEL_C',r in x['context']),('ORIGINAL_ELONG_SUBSYSTEM',r in x['local']),
            ('ONE_HOP_CARRIER_INCIDENCE',r in x['incident']),('EXACT_REVERSE',r in x['inverse'])] if v]
        need(row['selection_reasons']==reasons,'INCORRECT_SOURCE_SCOPE',r)
    need(inv['core_direction_ids']==sorted(x['core']) and inv['search_direction_ids']==x['allowed'] and
         inv['selected_inventory_direction_ids']==sorted(x['selected']) and inv['carrier_incidence_species']==sorted(x['anchors']), 'COVERAGE_MISMATCH','selected IDs')
    need(inv['coverage']==x['counts'] and inv['unresolved_classifications']==[], 'COVERAGE_MISMATCH','counts')
    for s in (E1,E2,ENTRY,T):
        need(inv['boundary_incidence'][s]=={'producers':sorted(r for r,q in rx.items() if s in q['products']),
                'consumers':sorted(r for r,q in rx.items() if s in q['reactants'])}, 'INCIDENCE_INCOMPLETE',s)
    for p in inv['source_provenance']:need(a.digest(ROOT/p['path'])==p['sha256'],'SOURCE_HASH_MISMATCH',p['path'])
    return {'status':'PASS','inventory_rows_checked':len(rx),'coverage':x['counts'],'subsystem_local_entries_checked':sum(len(v) for v in x['members'].values())}

def petri(w,source):
    m=defaultdict(F,a.fractions(w['initial_marking']));trace=[];net=defaultdict(F)
    for e in w['reaction_occurrences']:
        need(e['reaction_id'] in source['reactions'],'UNKNOWN_REACTION',e['reaction_id'])
        q=source['reactions'][e['reaction_id']];before=a.strings(m)
        missing={s:str(v-m[s]) for s,v in q['reactants'].items() if m[s]<v}
        need(not missing,'MISSING_REQUIRED_INPUT',e['event_id']+':'+json.dumps(missing,sort_keys=True))
        for s,v in q['reactants'].items():m[s]-=v;net[s]-=v
        for s,v in q['products'].items():m[s]+=v;net[s]+=v
        trace.append({'event_id':e['event_id'],'marking_before':before,'marking_after':a.strings(m)})
    return a.strings(m),trace,a.strings(net)

def lineage(w,source):
    """Allocate true outputs afresh; independently check every consumed origin lot."""
    balance={};initial=defaultdict(F)
    for b in w['boundary_lots']:
        o,s,n=b['origin'],b['species_id'],F(b['amount'])
        need(o.startswith('BOUNDARY:') and s in source['species'] and n>0 and (o,s) not in balance,'INVALID_BOUNDARY',o)
        need(b['conditional'] is True and b['author_initial_concentration'] is False,'UNSUPPORTED_BOUNDARY_SUPPLY',o)
        balance[o,s]=n;initial[s]+=n
    need(a.strings(initial)==w['initial_marking'],'BOUNDARY_MARKING_MISMATCH',w['witness_id'])
    dag=[];carrier_prev=None;rib_origin=None;carrier_history=[];factor_bindings={D:[],G:[]};released=[]
    active_factor={};factor_paths=[];gly_paths=[];active_gly=None
    # Exact source identity is enforced at ports. Namespace merely selects the
    # source-state continuity projection, not physiological molecular identity.
    for e in w['reaction_occurrences']:
        q=source['reactions'][e['reaction_id']];allocated=defaultdict(F)
        for binding in e['input_origins']:
            s,o,n=binding['species_id'],binding['origin'],F(binding['amount'])
            need(s in q['reactants'] and n>0 and balance.get((o,s),F())>=n,'INVALID_LINEAGE',e['event_id']+' consumes unavailable '+o+':'+s)
            balance[o,s]-=n;allocated[s]+=n
            if not o.startswith('BOUNDARY:'):dag.append({'producer_event_id':o,'consumer_event_id':e['event_id'],
                'species_id':s,'amount':str(n),'evidence_status':'EXTRACTED'})
            if s in factor_bindings:
                factor_bindings[s].append({'binding_event':e['event_id'],'source_token_origin':o,'quantity':str(n)})
                family='EFTu' if s==D else 'EFG'
                need(family not in active_factor,'INVALID_LINEAGE','overlapping factor attachment on one source carrier')
                record={'factor':family,'source_supply_species':s,'source_token_origin':o,'events':[],
                        'status':'SOURCE_PORT_CONTINUITY; MOLECULAR_IDENTITY_INFERRED'}
                active_factor[family]=record;factor_paths.append(record)
                if s==D:
                    need(active_gly is None,'INVALID_LINEAGE','second Gly-tRNA before actual first release')
                    active_gly={'delivery_origin':o,'source_delivery_species':D,'events':[],
                                'composition_certificate':False,'meaning':'SOURCE_TOKENS_AND_AUTHOR_VIRTUAL_STATE_CONVENTION'}
                    gly_paths.append(active_gly)
        need(dict(allocated)==q['reactants'],'INVALID_LINEAGE',e['event_id']+' incomplete actual input allocation')
        rib_in=[s for s in q['reactants'] if s.startswith('elRS')]
        rib_out=[s for s in q['products'] if s.startswith('elRS')]
        if rib_in:
            need(len(rib_in)==1 and len(rib_out)==1,'INVALID_LINEAGE','single source ribosomal transition')
            s=rib_in[0];bindings=[b for b in e['input_origins'] if b['species_id']==s]
            need(len(bindings)==1 and F(bindings[0]['amount'])==1,'INVALID_LINEAGE','one ribosomal source token')
            origin=bindings[0]['origin']
            if carrier_prev is not None:
                need((origin,s)==carrier_prev,'INVALID_LINEAGE',e['event_id']+' jumps to another ribosomal source history')
            else:
                if w['witness_id']!='W4':need(origin=='BOUNDARY:'+E2+':01' and s==E2,'INVALID_LINEAGE','actual E2 starting carrier')
                rib_origin=origin
            carrier_prev=(e['event_id'],rib_out[0]);carrier_history.append({'event_id':e['event_id'],
                'input_source_state':s,'input_origin':origin,'output_source_state':rib_out[0],'root_source_origin':rib_origin,
                'identity_status':'EXACT_SOURCE_STATE_CONTINUITY_NOT_MOLECULAR_IDENTITY'})
            for record in active_factor.values():record['events'].append({'event_id':e['event_id'],'source_input':s,'source_output':rib_out[0]})
            if active_gly is not None:active_gly['events'].append({'event_id':e['event_id'],'source_input':s,'source_output':rib_out[0]})
        for s,n in q['products'].items():balance[e['event_id'],s]=n
        for s in ('EFTu_GDP','EFG_GDP','tRNAGlyGCC','tRNAfMetCAU'):
            if s in q['products']:released.append({'event_id':e['event_id'],'species_id':s,'amount':str(q['products'][s])})
        for family,free in [('EFTu','EFTu_GDP'),('EFG','EFG_GDP')]:
            if free in q['products'] and family in active_factor:
                record=active_factor.pop(family);record['release_event']=e['event_id'];record['released_source_species']=free
        if 'tRNAGlyGCC' in q['products'] and active_gly is not None:
            active_gly['release_event']=e['event_id'];active_gly['released_source_species']='tRNAGlyGCC'
            active_gly=None
    need(w['event_dependencies']==dag,'EVENT_DAG_MISMATCH','independently reconstructed exact producer-consumer edges')
    for s,bs in factor_bindings.items():need(len({b['source_token_origin'] for b in bs})==len(bs),'INVALID_LINEAGE','distinct supply carrier '+s)
    return {'status':'PASS','all_input_allocations_reconstructed':True,'dependency_edges':dag,'ribosomal_source_history':carrier_history,
            'factor_supply_bindings':factor_bindings,'free_source_release_events':released,
            'factor_source_port_histories':factor_paths,'gly_trna_source_port_histories':gly_paths,
            'endpoint_attached_gly_delivery_origin':active_gly['delivery_origin'] if active_gly else None,
            'unspent_origin_lots':[{'origin':o,'species_id':s,'amount':str(n)} for (o,s),n in sorted(balance.items()) if n]}

def check_witness(w,source):
    es=w['reaction_occurrences'];rx=source['reactions'];wid=w['witness_id'];need(bool(es),'EMPTY_WITNESS',wid)
    ids=[e['reaction_id'] for e in es];eids=[e['event_id'] for e in es]
    need(len(eids)==len(set(eids)),'DUPLICATE_OCCURRENCE',wid)
    need(len({e['occurrence_origin'] for e in es})==len(es),'DUPLICATE_OCCURRENCE','upstream occurrence reuse')
    if wid=='W4':need(ids.count('re0000000001')==1,'DUPLICATE_HANDOFF','0001 exactly once')
    else:need('re0000000001' not in ids,'DUPLICATE_HANDOFF','upstream handoff absent in W1-W3')
    for e in es:
        r=e['reaction_id'];need(r in rx,'UNKNOWN_REACTION',r);q=rx[r]
        need(not any(c.startswith('TERM_') for c in source['annotations'][r]['level_c_functional_contexts'].split(';')),'TERMINATION_OUT_OF_SCOPE',r)
        need(a.fractions(e['inputs'])==q['reactants'] and a.fractions(e['outputs'])==q['products'],'SOURCE_REACTION_MISMATCH',r)
        need(e['equation']==a.equation(q['reactants'],q['products']),'SOURCE_EQUATION_MISMATCH',r)
        need(F(e['reference_parameter'])==source['parameters'][r] and e['reference_activity']==('REFERENCE_ENABLED' if source['parameters'][r]>0 else 'REFERENCE_DISABLED'), 'REFERENCE_ACTIVITY_MISMATCH',r)
        need(source['parameters'][r]>0,'DISABLED_DIRECTION_EXECUTED',r)
        need(e['level_c_contexts']==source['annotations'][r]['level_c_functional_contexts'],'ANNOTATION_MISMATCH',r)
    final,trace,net=petri(w,source)
    lin=lineage(w,source)
    need(w['occurrence_vector']==dict(sorted(Counter(ids).items())),'OCCURRENCE_VECTOR_MISMATCH','only actually fired directions counted')
    need(w['exact_net_stoichiometry']==net,'NET_STOICHIOMETRY_MISMATCH','fresh rational S*w')
    need(w['net_reaction']==a.equation({s:-F(v) for s,v in net.items() if F(v)<0},{s:F(v) for s,v in net.items() if F(v)>0}), 'NET_STOICHIOMETRY_MISMATCH','rendered net')
    need(w['per_event_markings']==trace and w['final_marking']==final,'MARKING_MISMATCH','full exact replay')
    for claim in ('EFTu_GDP_is_GTP_recovery','EFG_GDP_is_GTP_recovery'):need(w['claims'][claim] is False,'FALSE_RECOVERY_CLAIM',claim)
    for claim in ('global_moiety_conservation','full_molecular_composition_verified'):need(w['claims'][claim] is False,'UNSUPPORTED_COMPOSITION_CERTIFICATE',claim)
    need(w['claims']['kinetic_preference_measured'] is False,'UNSUPPORTED_KINETIC_INTERPRETATION','IDs/parameters do not measure priority')
    need(w['claims']['termination_completed'] is False,'TERMINATION_OUT_OF_SCOPE','structural endpoint')
    expected_ledger={s:{'initial':w['initial_marking'].get(s,'0'),'final':final.get(s,'0'),'net':net.get(s,'0'),
                     'event_membership':[e['event_id'] for e in es if s in rx[e['reaction_id']]['reactants'] or s in rx[e['reaction_id']]['products']]} for s in LEDGER}
    need(w['resource_ledger']==expected_ledger,'RESOURCE_LEDGER_MISMATCH','bound/free source species ledger')
    expected_waypoints=FIRST[:1] if wid=='W1' else FIRST if wid=='W2' else ([E1,E2] if wid=='W4' else [])+FIRST+SECOND
    need(w['waypoints']==expected_waypoints,'MISSING_REQUIRED_MILESTONE',wid)
    cursor=0
    for t in expected_waypoints:
        found=next((j for j in range(cursor,len(trace)) if F(trace[j]['marking_after'].get(t,'0'))>=1),None)
        need(found is not None,'MISSING_REQUIRED_MILESTONE',t);cursor=found+1
    need(w['target_source_state']==expected_waypoints[-1] and F(final.get(expected_waypoints[-1],'0'))==1,'WRONG_ENDPOINT',wid)
    if wid!='W4':
        evidence=w['search_evidence'];need(len(evidence)==len(expected_waypoints),'SEARCH_EVIDENCE_MISMATCH','one record per leg')
        combined=[]
        for t,z in zip(expected_waypoints,evidence):
            need(z['waypoint_source_state']==t and z['status']=='REACHED' and z['bounds']=={'max_states':50000,'max_depth':16,'max_total_events':64},'SEARCH_EVIDENCE_MISMATCH',t)
            need(1<=z['expanded_states']<=z['visited_states']<=50000 and z['leg_event_count']==len(z['selected_original_ids'])<=16,'SEARCH_EVIDENCE_MISMATCH','finite bounds')
            need(z['state_identity']=='COMPLETE_RATIONAL_MARKING_ORIGIN_LOTS_AND_SOURCE_EVENT_HISTORY' and z['tie_break']=='SORTED_SOURCE_IDS_NO_KINETIC_PRIORITY','SEARCH_EVIDENCE_MISMATCH','carrier history/tie-break')
            combined+=z['selected_original_ids']
        need(combined==ids and len(ids)<=64,'SEARCH_EVIDENCE_MISMATCH','discovered event sequence')
    b={E2:'1',D:'1'} if wid=='W1' else {E2:'1',D:'1',G:'1'} if wid=='W2' else {E2:'1',D:'2',G:'2'}
    if wid=='W4':
        u=load(OUT/'phase_b1_1_followup_witness.json')['new_witness']
        prefix=[e['reaction_id'] for e in u['reaction_occurrences']]
        need(ids[:len(prefix)]==prefix and ids[len(prefix)]=='re0000000001','UPSTREAM_EVIDENCE_MISMATCH','immutable accepted route')
        b={**u['initial_marking'],D:'2',G:'2'}
        meta=w['upstream_evidence'];need(meta['sha256']==a.digest(ROOT/meta['path']) and meta['accepted_witness_id']==u['witness_id'] and meta['upstream_discovery_rerun'] is False, 'UPSTREAM_EVIDENCE_MISMATCH','signed witness bytes')
        need(meta['event_origins']==[e['occurrence_origin'] for e in u['reaction_occurrences']] and [e['occurrence_origin'] for e in es[:len(prefix)]]==meta['event_origins'], 'UPSTREAM_EVIDENCE_MISMATCH','exact upstream event occurrences')
        signed=load(OUT/'phase_b1_1_formal_signoff_2026-10-09.json')
        need(signed['phase_b1_1_formally_accepted'] is True and signed['IF3_first_witness']['original_reaction_sequence']==prefix,'UPSTREAM_EVIDENCE_MISMATCH','formal signoff')
    need(w['initial_marking']==b,'UNSUPPORTED_BOUNDARY_SUPPLY','exact finite conditional scenario')
    if wid in ('W3','W4'):
        for s,n in [('EFTu_GDP','2'),('EFG_GDP','2'),('tRNAGlyGCC','1')]:need(net.get(s)==n,'RESOURCE_LEDGER_MISMATCH',s)
        need(net.get('PO4')==('5' if wid=='W4' else '4'),'RESOURCE_LEDGER_MISMATCH','PO4')
        need(all(s not in net for s in ('ATP','ADP','AMP','GTP','GDP','PPi')),'RESOURCE_LEDGER_MISMATCH','free nucleotides absent')
        need(len(lin['factor_supply_bindings'][D])==len(lin['factor_supply_bindings'][G])==2,'INVALID_LINEAGE','two deliveries/two EF-G encounters')
    need(w['scientific_status']=='PENDING_HUMAN_REVIEW','AUTHORITY_PROMOTION',wid)
    return {'status':'PASS','witness_id':wid,'events_checked':len(es),'exact_net':net,'final_marking':final,'independently_reconstructed_lineage':lin}

def reference_example(source):
    """User-supplied external sequence is used only here, never by production builder."""
    ids=[f're{n:010d}' for n in (13,14,16,17,18,19,22,24,25,68,74,75,77,78,79,80,83,85,86)]
    final,_,net=petri({'initial_marking':{E2:'1',D:'2',G:'2'},'reaction_occurrences':[{'event_id':f'REF:{i}', 'reaction_id':r} for i,r in enumerate(ids)]},source)
    expected={E2:'-1',D:'-2',G:'-2',T:'1','tRNAGlyGCC':'1','EFTu_GDP':'2','EFG_GDP':'2','PO4':'4'}
    need(net==expected and final=={T:'1','tRNAGlyGCC':'1','EFTu_GDP':'2','EFG_GDP':'2','PO4':'4'},'REFERENCE_EXAMPLE_DISCREPANCY','derive rather than force net')
    return {'status':'PASS','original_ids':ids,'independently_derived_net':net,'expectation_agrees':True}

def validate(data,inv,markdown=None):
    source=sources();integrity=source_hashes(source);scope=check_scope(inv,source)
    need(data['authorization']==AUTH,'AUTHORITY_PROMOTION','B1-2 only')
    for p in data['source_provenance']:need(a.digest(ROOT/p['path'])==p['sha256'],'SOURCE_HASH_MISMATCH',p['path'])
    need([w['witness_id'] for w in data['witnesses']]==['W1','W2','W3','W4'],'MISSING_REQUIRED_WITNESS','W1-W4')
    checked=[check_witness(w,source) for w in data['witnesses']]
    rx=source['reactions']
    selected={s for w in data['witnesses'][:3] for e in w['reaction_occurrences'] for side in ('reactants','products') for s in rx[e['reaction_id']][side] if s not in RESOURCE}
    expected={s:sorted(r for r,q in rx.items() if s in q['reactants']) for s in sorted(selected)}
    need(data['competition_outlets']==expected and inv['selected_intermediate_outlets']==expected,'COMPETITION_INCOMPLETE','all source outlets')
    need(data['selected_source_states']==sorted(selected),'COMPETITION_INCOMPLETE','all selected states')
    ids=set(inv['boundary_incidence'][T]['producers']+inv['boundary_incidence'][T]['consumers'])
    need(set(inv['termination_boundary_appendix'])==ids and all(v==inv['reactions'][r] for r,v in inv['termination_boundary_appendix'].items()),'INCIDENCE_INCOMPLETE','termination boundary')
    need(rx['re0000000001']=={'reactants':{E1:F(1)},'products':{E2:F(1),'tRNAfMetCAU':F(1)}} and source['annotations']['re0000000001']['level_c_functional_contexts']=='ELONG_tRNA_release','SOURCE_STATE_MISMATCH','0001')
    need(rx['re0000000086']['products']=={T:F(1),'EFG_GDP':F(1)},'SOURCE_STATE_MISMATCH','0086')
    # Read immutable P7 without rerunning initiation discovery.
    sys.path.insert(0,str(ROOT/'scripts/pathways/phase_b1_1'))
    import verify_initiation_witnesses as prior
    p7=next(w for w in load(OUT/'phase_b1_1_witnesses.json')['witnesses'] if w['witness_id']=='P7')
    p7check=prior.check_witness(p7,source)
    need(p7['target_milestone']==data['witnesses'][0]['target_source_state'] and p7['reaction_occurrences'][-1]['reaction_id']==data['witnesses'][0]['reaction_occurrences'][-1]['reaction_id'],'P7_INTERFACE_MISMATCH','first delivery')
    if markdown is not None:
        for e in data['witnesses'][2]['reaction_occurrences']:need(e['reaction_id'] in markdown and e['equation'] in markdown,'READING_VIEW_SOURCE_MISMATCH',e['reaction_id'])
        for r in expected[T]:need(r in markdown,'READING_VIEW_SOURCE_MISMATCH','boundary '+r)
        need(data['witnesses'][2]['net_reaction'] in markdown and 'INFERRED' in markdown and 'PENDING_HUMAN_REVIEW' in markdown,'READING_VIEW_SOURCE_MISMATCH','net/limits')
    return {'status':'PASS','source_integrity':integrity,'scope':scope,'witnesses':checked,
            'external_reference_example':reference_example(source),'P7_read_only_revalidation':p7check,
            'boundary_verification':{'E2':E2,'T_pre':T,'T_pre_producer':'re0000000086',
                'RF1_RF2_binding_context':['re0000000796','re0000000811'],'termination_executed':False},
            'scientific_status':'PENDING_HUMAN_REVIEW','builder_imported':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-dir',type=Path,default=OUT)
    p.add_argument('--report',type=Path,default=OUT/'phase_b1_2_independent_verification.json');args=p.parse_args()
    try:r=validate(load(args.input_dir/'phase_b1_2_witnesses.json'),load(args.input_dir/'phase_b1_2_source_scope.json'),(args.input_dir/'phase_b1_2_elongation_pathways.md').read_text(encoding='utf-8'))
    except Exception as e:r={'status':'FAIL','rejection_code':getattr(e,'code',type(e).__name__),'diagnostic':str(e)}
    save(args.report,r);print(json.dumps({'status':r['status'],'diagnostic':r.get('diagnostic'),'witnesses_checked':len(r.get('witnesses',[]))}));return 0 if r['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
