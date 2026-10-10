"""Independent canonical-source replay. Does not import B1-3 builders/readers."""
import sys,json,csv,copy,re,hashlib,argparse
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict,Counter,deque
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/reduction/pathways'
sys.path.insert(0,str(ROOT/'scripts/pathways/phase_b0'))
import verify_phase_b0_witnesses as independent
sys.path.insert(0,str(ROOT/'scripts/pathways/phase_b1_2'))
import verify_elongation_witnesses as prior
need=independent.need;Rejection=independent.Rejection
T='elRS70SAUAA0004_Pept0003tRNAGlyGCC';TERM='termRS70SUAA0004_tRNAGlyGCC'
FACTOR={'RF1','RF2','RF3','RF3_GDP','RF3_GTP','RRF','EFG','EFG_GDP','EFG_GTP'}
RES={'ATP','ADP','AMP','PPi','GTP','GDP','PO4'}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_bytes((json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(v):return {s:str(n) for s,n in sorted(v.items()) if n}
def fractions(v):return {s:F(n) for s,n in v.items()}
def source():return prior.sources()
def projection(s):
    p={}
    if s.startswith('elRS70S') or s.startswith('termRS70S'):p={'R30':'SOURCE_70S','R50':'SOURCE_70S','MRNA':'BOUND'}
    if s.startswith('RS30S') or s.startswith('termRS30S'):p['R30']='FREE' if s=='RS30S' else 'BOUND'
    if s.startswith('RS50S'):p['R50']='FREE' if s=='RS50S' else 'BOUND'
    if s in {'mRNA','termRS30S_mRNA'}:p['MRNA']='FREE' if s=='mRNA' else 'BOUND'
    if 'tRNAGlyGCC' in s:p['TRNA']='FREE' if s=='tRNAGlyGCC' else 'BOUND'
    if 'Pept0003' in s:p['PEPTIDE']='FREE' if s=='Pept0003' else 'BOUND'
    for f in ('RF1','RF2','RF3','RRF','EFG'):
        match=re.search(r'(?:^|_)'+f+r'(?P<state>_GDP_PO4|_GDP|_GTP)?(?:_|$)',s)
        if match:p[f]=(match.group('state') or '_APO')[1:]
    return p
def initial_pool(w):
    tokens=[]
    for prefix,key in [('INHERITED','initial_inherited_inventory'),('ADDED','added_conditional_supplies')]:
        if prefix=='INHERITED' and w.get('starting_post_release_witness') and not w.get('upstream_W4'):
            tokens.extend(copy.deepcopy(w['initial_inherited_tokens']));continue
        for s,n in sorted(w[key].items()):
            need(F(n)>=0 and F(n).denominator==1,'INVALID_SUPPLY',s)
            for i in range(int(F(n))):
                tid=f'{prefix}:{s}:{i+1:02d}'
                tokens.append({'token_id':tid,'species_id':s,'labels':{r:tid+':'+r for r in projection(s)} if not w.get('upstream_W4') else {}})
    # Parent tokens may themselves originate in an earlier ADDED RF supply;
    # compare the complete parent portion separately from newly seeded supplies.
    parent_count=len(w['initial_inherited_tokens'])
    need(tokens[:parent_count]==w['initial_inherited_tokens'],'INVALID_LINEAGE','inherited carrier identities')
    need(exact(Counter(t['species_id'] for t in w['initial_inherited_tokens']))==w['initial_inherited_inventory'],'INVALID_LINEAGE','inherited token marking')
    return tokens
def reverse_ids(r,src):
    q=src['reactions'][r]
    return sorted(t for t,k in src['reactions'].items() if k['reactants']==q['products'] and k['products']==q['reactants'])
def scope_sets(src):
    ms=prior.independent_memberships(src);rx=src['reactions'];ann=src['annotations']
    files={'Termination_A_RF1.xml','Termination_A_RF2.xml','Termination_B_RF1.xml','Termination_B_RF2.xml'}
    tc={'TERM_factor_binding','TERM_peptide_release','TERM_energy_coupling'}
    term={r for r in rx if tc&set(ann[r]['level_c_functional_contexts'].split(';')) or any(Path(x['source_file']).name in files for x in ms[r])}
    rec={r for r in rx if 'RECYCLE_disassembly' in ann[r]['level_c_functional_contexts'].split(';') or any(Path(x['source_file']).name=='Termination_C.xml' for x in ms[r])}
    core=term|rec
    anchors={s for r in core for side in ('reactants','products') for s in rx[r][side] if s.startswith(('termRS','elRS','RS50S_')) or s in FACTOR}|{T}
    inc={r for r,q in rx.items() if anchors&(set(q['reactants'])|set(q['products']))}
    rev={t for r in core for t in reverse_ids(r,src)};selected=core|inc|rev
    return ms,term,rec,core,anchors,inc,rev,selected
def check_scope(inv,src):
    ms,term,rec,core,anchors,inc,rev,selected=scope_sets(src);rx=src['reactions']
    need(set(inv['reactions'])==set(rx),'SCOPE_COVERAGE','all 968 required')
    need(inv['selected_direction_ids']==sorted(selected) and inv['core_direction_ids']==sorted(core),'SCOPE_MEMBERSHIP','canonical set mismatch')
    allowed=sorted(r for r in core if src['parameters'][r]>0)
    need(inv['search_direction_ids']==allowed,'SCOPE_ACTIVITY','positive core')
    for r,q in rx.items():
        row=inv['reactions'][r]
        need(fractions(row['reactants'])==q['reactants'] and fractions(row['products'])==q['products'],'SOURCE_COEFFICIENT_MISMATCH',r)
        need(row['equation']==independent.equation(q['reactants'],q['products']),'SOURCE_EQUATION_MISMATCH',r)
        need(row['reverse_reaction_ids']==reverse_ids(r,src),'REVERSE_PAIR_MISMATCH',r)
        need(F(row['reference_parameter'])==src['parameters'][r],'PARAMETER_MISMATCH',r)
        need(row['level_c']==src['annotations'][r]['level_c_functional_contexts'] and row['original_subsystem_memberships']==ms[r],'SOURCE_PROVENANCE_MISMATCH',r)
        kind='OUT_OF_B1_3_SCOPE' if r not in selected else 'AUTHOR_DISABLED_CONTEXT' if not src['parameters'][r] else 'RECYCLE_SEARCH_SCOPE' if r in rec else 'TERM_SEARCH_SCOPE' if r in term else 'SOURCE_REVERSE_OR_COMPETITOR' if r in rev else 'SHARED_BOUNDARY_CONTEXT'
        need(row['classification']==kind and row['selected']==(r in selected) and row['core']==(r in core),'SCOPE_CLASSIFICATION',r)
        reasons=[k for k,b in [('TERMINATION_CORE',r in term),('RECYCLING_CORE',r in rec),('ONE_HOP_BOUNDARY',r in inc),('EXACT_REVERSE',r in rev)] if b]
        need(row['selection_reasons']==reasons,'SCOPE_MEMBERSHIP',r+' selection reasons')
        allspecies=sorted(set(q['reactants'])|set(q['products']))
        need(row['boundary_species']==[s for s in allspecies if s in anchors],'SCOPE_MEMBERSHIP',r+' boundary species')
        need(row['nucleotide_forms']==[s for s in allspecies if s in RES or '_GDP' in s or '_GTP' in s or '_PO4' in s],'SOURCE_STATE_PROJECTION',r+' nucleotide forms')
        need(row['degradation']==any('_degraded' in s for s in allspecies),'SCOPE_MEMBERSHIP',r+' degradation')
    counts=Counter(inv['reactions'][r]['classification'] for r in rx)
    expected={'all_directions':len(rx),'selected':len(selected),'core':len(core),'search_positive':len(allowed),'selected_positive':sum(src['parameters'][r]>0 for r in selected),'selected_zero':sum(src['parameters'][r]==0 for r in selected),'classification_counts':dict(sorted(counts.items()))}
    need(inv['coverage']==expected,'SCOPE_COVERAGE','counts')
    expected_incidence={s:{'producers':[r for r,q in rx.items() if s in q['products']],'consumers':[r for r,q in rx.items() if s in q['reactants']]} for s in sorted(anchors)}
    need(inv['boundary_anchor_species']==sorted(anchors) and inv['incidence']==expected_incidence,'SCOPE_MEMBERSHIP','one-hop incidence')
    for ref in inv['source_provenance']:need(digest(ROOT/ref['path'])==ref['sha256'],'SOURCE_HASH_MISMATCH',ref['path'])
    return expected
def audit_search(w,src,allowed):
    """Independent BFS from recorded finite inputs; all positive reverses retained."""
    whole=[];achieved=[];records=[]
    limits={'visited_per_leg':100000,'events_per_leg':24,'events_per_witness':128}
    def key(pool,hist):return tuple(sorted((t['token_id'],t['species_id'],tuple(sorted(t['labels'].items()))) for t in pool)),tuple(hist),tuple(achieved)
    def advance(pool,r,eid):
        p=copy.deepcopy(pool);used=[];q=src['reactions'][r]
        for s,n in sorted(q['reactants'].items()):
            ts=sorted((t for t in p if t['species_id']==s),key=lambda t:(0 if t['token_id'].startswith('INHERITED:') else 1,t['token_id']))
            for t in ts[:int(n)]:p.remove(t);used.append(t)
        labels=defaultdict(list)
        for t in used:
            for role,identity in t['labels'].items():labels[role].append(identity)
        for s,n in sorted(q['products'].items()):
            for j in range(int(n)):
                tag={}
                for role in projection(s):
                    need(len(labels[role])==1,'INVALID_LINEAGE','search carrier '+role);tag[role]=labels[role].pop()
                p.append({'token_id':eid+':'+s+':'+str(j+1).zfill(2),'species_id':s,'labels':tag})
        need(not any(labels.values()),'INVALID_LINEAGE','search carrier loss')
        return sorted(p,key=lambda t:t['token_id'])
    for ev in w['search_evidence']:
        need(ev['allowed_source_directions']==allowed and ev['limits']==limits,'SEARCH_PROTOCOL','directions/limits')
        need(ev['initial_leg_pool_sha256']==hashlib.sha256(json.dumps(ev['initial_finite_pool'],sort_keys=True).encode()).hexdigest(),'SEARCH_PROTOCOL','input hash')
        pool=ev['initial_finite_pool'];queue=deque([(pool,[])]);seen={key(pool,whole)};expanded=0;depth=0;depth_cut=False;found=None
        while queue:
            p,leg=queue.popleft();expanded+=1;depth=max(depth,len(leg));m=Counter(t['species_id'] for t in p)
            if all(m[s]>=F(n) for s,n in ev['target_marking'].items()):found=p,leg;break
            if len(leg)>=limits['events_per_leg']:depth_cut=True;continue
            for r in allowed:
                q=src['reactions'][r]
                if not all(m[s]>=n for s,n in q['reactants'].items()):continue
                p2=advance(p,r,'DISCOVERY:E'+str(len(whole)+len(leg)+1).zfill(3));k=key(p2,whole+leg+[r])
                if k in seen:continue
                need(len(seen)<limits['visited_per_leg'],'SEARCH_INCONCLUSIVE','independent budget')
                seen.add(k);queue.append((p2,leg+[r]))
        need(found is not None,'SEARCH_INCONCLUSIVE','independent waypoint')
        need(ev['status']=='REACHED' and ev['events']==found[1] and ev['visited']==len(seen) and ev['expanded']==expanded and ev['depth_reached']==depth and ev['depth_budget_encountered']==depth_cut and ev['frontier_exhausted'] is False,'SEARCH_REPRODUCTION','BFS counts/history')
        whole+=found[1];achieved.append(json.dumps(ev['target_marking'],sort_keys=True));records.append({'visited':len(seen),'expanded':expanded,'events':found[1]})
    if w['search_evidence']:need(whole==[e['reaction_id'] for e in w['reaction_occurrences']],'SEARCH_REPRODUCTION','full discovered history')
    return {'status':'PASS','independently_researched_legs':len(records),'legs':records}
def petri(w,src):
    m=defaultdict(F,fractions(w['initial_marking']));trace=[];net=defaultdict(F)
    need(set(m)<=src['species'],'UNKNOWN_SOURCE_SPECIES','initial stock')
    need(all(n>=0 and n.denominator==1 for n in m.values()),'INVALID_SUPPLY','whole finite tokens')
    for e in w['reaction_occurrences']:
        r=e['reaction_id'];need(r in src['reactions'],'UNKNOWN_SOURCE_REACTION',r);q=src['reactions'][r];before=exact(m)
        need(all(m[s]>=n for s,n in q['reactants'].items()),'NOT_PETRI_ENABLED',r)
        for s,n in q['reactants'].items():m[s]-=n;net[s]-=n
        for s,n in q['products'].items():m[s]+=n;net[s]+=n
        trace.append({'event_id':e['event_id'],'before':before,'after':exact(m)})
    return exact(m),exact(net),trace
def lineage(w,src):
    pool=initial_pool(w);need(w['initial_tokens']==pool,'INVALID_LINEAGE','initial origin lots')
    cut=w['upstream_W4']['event_count'] if w.get('upstream_W4') else 0;dag=[];streams=[]
    for i,e in enumerate(w['reaction_occurrences']):
        if cut and i==cut:
            for t in pool:
                if not t['labels']:t['labels']={r:t['token_id']+':'+r for r in projection(t['species_id'])}
        used=[];eid=e['event_id'];q=src['reactions'][e['reaction_id']]
        for s,n in sorted(q['reactants'].items()):
            choices=sorted((x for x in pool if x['species_id']==s),key=lambda x:(0 if x['token_id'].startswith('INHERITED:') else 1,x['token_id']))
            need(n.denominator==1 and len(choices)>=n,'INVALID_LINEAGE','finite token allocation')
            for t in choices[:int(n)]:pool.remove(t);used.append(t)
        need(e['consumed_tokens']==used,'INVALID_LINEAGE',eid+' wrong producer, carrier or source-state origin')
        labels=defaultdict(list)
        for t in used:
            for r,v in t['labels'].items():labels[r].append(v)
        produced=[]
        for s,n in sorted(q['products'].items()):
            for j in range(int(n)):
                tag={}
                if i>=cut:
                    for r in projection(s):
                        need(len(labels[r])==1,'INVALID_LINEAGE',eid+' carrier duplication/loss '+r);tag[r]=labels[r].pop()
                produced.append({'token_id':eid+':'+s+':'+str(j+1).zfill(2),'species_id':s,'labels':tag})
        need(e['produced_tokens']==produced,'INVALID_LINEAGE',eid+' carrier identity/state transfer')
        if i>=cut:need(not any(labels.values()),'INVALID_LINEAGE',eid+' unreported occupied carrier')
        pool=sorted(pool+produced,key=lambda t:t['token_id'])
        for t in used:dag.append({'producer_token':t['token_id'],'consumer_event':eid,'source_species':t['species_id'],'evidence_status':'EXTRACTED','authority':'CANONICAL_SBML','confidence':'EXACT_ORIGIN_ALLOCATION'})
        if i>=cut:streams.append({'event_id':eid,'inputs':[{**t,'source_roles':projection(t['species_id'])} for t in used],'outputs':[{**t,'source_roles':projection(t['species_id'])} for t in produced]})
    need(w['final_tokens']==pool and w['lineage_DAG']==dag and w['carrier_lineage']==streams,'INVALID_LINEAGE','complete carrier DAG/state history')
    return {'status':'PASS','finite_final_tokens':len(pool),'carrier_events_checked':len(streams),'molecular_composition_status':'NOT_CERTIFIED; SOURCE_STATE_IDENTITY_PROJECTION_ONLY'}
def check_witness(w,src,allowed):
    events=w['reaction_occurrences'];cut=w['upstream_W4']['event_count'] if w.get('upstream_W4') else 0
    for i,e in enumerate(events):
        r=e['reaction_id'];need(r in src['reactions'],'UNKNOWN_SOURCE_REACTION',r);q=src['reactions'][r]
        need(src['parameters'][r]>0,'AUTHOR_DISABLED_DIRECTION',r)
        need(i<cut or r in allowed,'OUT_OF_SEARCH_SCOPE',r)
        need(fractions(e['inputs'])==q['reactants'] and fractions(e['outputs'])==q['products'],'SOURCE_COEFFICIENT_MISMATCH',r)
        need(e['equation']==independent.equation(q['reactants'],q['products']),'SOURCE_EQUATION_MISMATCH',r)
        need(F(e['reference_parameter'])==src['parameters'][r],'PARAMETER_MISMATCH',r)
        need(e['reverse_reaction_ids']==reverse_ids(r,src),'REVERSE_PAIR_MISMATCH',r)
        need(e['source_segment']==('SIGNED_W4' if i<cut else 'B1_3'),'UPSTREAM_HANDOFF','segment')
        need(e['event_id']==w['witness_id']+':E'+str(i+1).zfill(3),'EVENT_HISTORY','event identity/order')
    final,net,trace=petri(w,src)
    need(w['final_marking']==final,'FINAL_SOURCE_MARKING','canonical final inventory')
    need(w['per_event_markings']==trace,'EVENT_HISTORY','occupied source intermediates')
    need(w['exact_net_stoichiometry']==net and w['occurrence_vector']==dict(sorted(Counter(e['reaction_id'] for e in events).items())),'NET_STOICHIOMETRY','S_full*w')
    aggregate=defaultdict(F)
    for field in ['initial_inherited_inventory','added_conditional_supplies']:
        for s,n in w[field].items():aggregate[s]+=F(n)
    need(w['initial_marking']==exact(aggregate),'INVALID_SUPPLY','inheritance + conditional lots')
    lineage_evidence=lineage(w,src)
    species=sorted(set(aggregate)|set(final)|set(net)|RES|FACTOR|{'RS30S','RS50S','mRNA','tRNAGlyGCC','Pept0003','Pept0003tRNAGlyGCC'})
    expected_ledger={s:{'inherited':w['initial_inherited_inventory'].get(s,'0'),'added':w['added_conditional_supplies'].get(s,'0'),'initial':str(aggregate[s]),'event_net':net.get(s,'0'),'final':final.get(s,'0'),'events':[e['event_id'] for e in events if s in e['inputs'] or s in e['outputs']]} for s in species}
    need(w['resource_ledger']==expected_ledger,'RESOURCE_LEDGER','free/bound source-species accounting')
    if w['witness_id'].startswith('W_T'):
        need(final.get('Pept0003')=='1' and w['initial_inherited_inventory']=={T:'1'},'FREE_PEPTIDE_IDENTITY','one free original Pept0003')
    if w['witness_id'].startswith(('W_R','W_JOINT')):
        need(all(F(final.get(s,'0'))>=1 for s in ['RS30S','RS50S','mRNA','tRNAGlyGCC','RRF','EFG_GDP','Pept0003']),'RECYCLING_ENDPOINT','complete free components')
    need(w['scientific_status']=='PENDING_HUMAN_REVIEW' and all(v is False for v in w['claims'].values()),'SCIENTIFIC_BOUNDARY','no automatic signoff')
    return {'witness_id':w['witness_id'],'status':'PASS','events':len(events),'final_marking':final,'exact_net':net,'lineage':lineage_evidence,'petri':'PASS','S_full_w':'PASS','resource_ledger':'PASS'}
def signed_upstream(data,src):
    baseline=load(OUT/'phase_b1_3_source_baseline.json');accept=baseline['previous_acceptance'];sign=load(ROOT/accept['path'])
    need(digest(ROOT/accept['path'])==accept['sha256'],'SIGNED_UPSTREAM_HASH','formal signoff')
    need(sign['scientific_status']=='B1_2_FORMALLY_ACCEPTED_LIMITED_SCOPE' and [h['researcher_decision'] for h in sign['human_review']]==['Y','Y','CONDITIONAL','CONDITIONAL','Y','CONDITIONAL','Y'],'SIGNED_UPSTREAM_RESTRICTIONS','H3/H4/H6 unchanged')
    for x in sign['evidence_navigation']:need(digest(ROOT/x['path'])==x['sha256'],'SIGNED_UPSTREAM_HASH',x['path'])
    old=next(x for x in load(OUT/'phase_b1_2_witnesses.json')['witnesses'] if x['witness_id']=='W4');old_result=prior.check_witness(old,src)
    for w in data['witnesses']:
        if not w.get('upstream_W4'):continue
        u=w['upstream_W4'];cut=u['event_count']
        need(u['sha256']==digest(ROOT/u['path']) and cut==len(old['reaction_occurrences']),'SIGNED_UPSTREAM_HASH','W4')
        need(w['initial_inherited_inventory']==old['initial_marking'],'UPSTREAM_HANDOFF','signed initial stock')
        need([e['reaction_id'] for e in w['reaction_occurrences'][:cut]]==[e['reaction_id'] for e in old['reaction_occurrences']],'UPSTREAM_HANDOFF','signed W4 prefix')
        before=fractions(w['per_event_markings'][cut-1]['after']);new=fractions(w['added_conditional_supplies'])
        need(exact({s:before.get(s,F())-new.get(s,F()) for s in set(before)|set(new)})==old['final_marking'],'UPSTREAM_HANDOFF','exact endpoint + unused new supplies')
        need(u['handoff_marking']==old['final_marking'],'UPSTREAM_HANDOFF','source handoff')
        efg_inputs=[t['token_id'] for e in w['reaction_occurrences'][:cut] for t in e['consumed_tokens'] if t['species_id']=='EFG_GTP']
        need(all(t.startswith('INHERITED:') for t in efg_inputs),'INVALID_LINEAGE','recycling EFG lot must survive upstream')
    return {'status':'PASS','accepted_W4_events':len(old['reaction_occurrences']),'independent_old_W4_check':old_result,'H3_H4_H6':'CONDITIONAL_UNCHANGED'}
def validate(data,inv):
    src=source();counts=independent.check_source_integrity(src)
    coefficient_sum=sum((sum(q['reactants'].values(),F())+sum(q['products'].values(),F()) for q in src['reactions'].values()),F())
    coverage=check_scope(inv,src);allowed=inv['search_direction_ids']
    need(data['protocol_sha256']==digest(OUT/'phase_b1_3_protocol.md'),'PROTOCOL_IDENTITY','frozen protocol')
    need(data['source_baseline_sha256']==digest(OUT/'phase_b1_3_source_baseline.json'),'SOURCE_HASH_MISMATCH','baseline')
    results=[]
    for w in data['witnesses']:
        result=check_witness(w,src,allowed);result['independent_search']=audit_search(w,src,allowed);results.append(result)
    ws={w['witness_id']:w for w in data['witnesses']}
    for w in data['witnesses']:
        parent=w.get('starting_post_release_witness')
        if parent and not w.get('upstream_W4'):
            need(w['initial_inherited_inventory']==ws[parent]['final_marking'],'UPSTREAM_HANDOFF',w['witness_id'])
            need(w['initial_inherited_tokens']==ws[parent]['final_tokens'],'INVALID_LINEAGE','exact parent carrier handoff '+w['witness_id'])
    # A consumed shared T_pre cannot enable the other branch without a new source event.
    release=[ws['W_T1_RF1_RELEASE'],ws['W_T2_RF2_RELEASE']]
    branches=[e['reaction_id'] for w in release for e in w['reaction_occurrences'][:1]]
    for j,r in enumerate(branches):
        q=src['reactions'][r];need(q['reactants'].get(T)==1,'RF_COMPETITION','common exact precursor')
        after={**q['products'],'RF1':F(1) if j else F(0),'RF2':F(0) if j else F(1)}
        other=src['reactions'][branches[1-j]]
        need(not all(after.get(s,F())>=n for s,n in other['reactants'].items()),'RF_COMPETITION','one token exclusivity')
    return {'status':'PASS','source_integrity':{**counts,'positive_author_parameters':483,'arc_coefficient_sum':str(coefficient_sum)},'inventory':coverage,'witnesses':results,'competition':{'status':'PASS','shared_T_pre':T,'second_binding_after_first':'NOT_PETRI_ENABLED','physiological_ranking':'NOT_ESTABLISHED'},'signed_upstream':signed_upstream(data,src),'scientific_status':'PENDING_HUMAN_REVIEW','builder_imported':False}
def main():
    p=argparse.ArgumentParser();p.add_argument('--input-dir',type=Path,default=OUT);p.add_argument('--report',type=Path,default=OUT/'phase_b1_3_independent_verification.json');a=p.parse_args()
    try:report=validate(load(a.input_dir/'phase_b1_3_witnesses.json'),load(a.input_dir/'phase_b1_3_source_scope.json'))
    except Exception as e:
        import traceback
        report={'status':'FAIL','error_category':getattr(e,'code',type(e).__name__),'diagnostic':str(e),'traceback':traceback.format_exc()}
        with (OUT/'phase_b1_3_failure_evidence.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'stage':'independent_verifier',**report})+'\n')
    save(a.report,report);print(json.dumps({'status':report['status'],'witnesses_checked':len(report.get('witnesses',[])),'error':report.get('diagnostic')}));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
