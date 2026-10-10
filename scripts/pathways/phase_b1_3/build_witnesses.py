"""Frozen bounded directed Petri search and finite source-carrier allocation."""
from collections import defaultdict, Counter, deque
from fractions import Fraction as F
from pathlib import Path
import argparse,sys,json,copy,re
sys.dont_write_bytecode=True
from inspect_source import ROOT,OUT,T,TERM,FACTORS,load,save,digest,inventory,source_reader as low
LIMITS={'visited_per_leg':100000,'events_per_leg':24,'events_per_witness':128}
BASE=OUT/'phase_b1_3_source_baseline.json'
PROTOCOL=OUT/'phase_b1_3_protocol.md'
RES={'ATP','ADP','AMP','PPi','GTP','GDP','PO4'}

def roles(s):
    """Declared opaque carrier projection, not elemental composition."""
    x={}
    if s.startswith(('termRS70S','elRS70S')):x.update(R30='SOURCE_70S',R50='SOURCE_70S',MRNA='BOUND')
    if s.startswith(('RS30S','termRS30S')):x['R30']='FREE' if s=='RS30S' else 'BOUND'
    if s.startswith('RS50S'):x['R50']='FREE' if s=='RS50S' else 'BOUND'
    if s=='mRNA':x['MRNA']='FREE'
    if s=='termRS30S_mRNA':x['MRNA']='BOUND'
    if 'tRNAGlyGCC' in s:x['TRNA']='FREE' if s=='tRNAGlyGCC' else 'BOUND'
    if 'Pept0003' in s:x['PEPTIDE']='FREE' if s=='Pept0003' else 'BOUND'
    for factor in ['RF1','RF2','RF3','RRF','EFG']:
        if re.search(r'(?:^|_)'+factor+r'(?:_|$)',s):
            suffix=s.split(factor,1)[1]
            x[factor]='GDP_PO4' if suffix.startswith('_GDP_PO4') else 'GDP' if suffix.startswith('_GDP') else 'GTP' if suffix.startswith('_GTP') else 'APO'
    return x

def seed(initial,prefix='INHERITED',bridge=False):
    pool=[]
    for s,n in sorted(initial.items()):
        n=F(n)
        if n.denominator!=1 or n<0:raise ValueError('INVALID_FINITE_SUPPLY '+s)
        for i in range(int(n)):
            tid=f'{prefix}:{s}:{i+1:02d}'
            pool.append({'token_id':tid,'species_id':s,'labels':{r:tid+':'+r for r in roles(s)} if not bridge else {}})
    return pool
def marking(pool):return {s:str(n) for s,n in sorted(Counter(t['species_id'] for t in pool).items()) if n}
def statekey(pool,history,achieved):return (tuple(sorted((t['token_id'],t['species_id'],tuple(sorted(t['labels'].items()))) for t in pool)),tuple(history),tuple(achieved))
def fire(pool,q,eid,labelled=True):
    nxt=copy.deepcopy(pool);used=[]
    for s,n in sorted(q['reactants'].items()):
        n=F(n)
        if n.denominator!=1:raise ValueError('UNSUPPORTED_FRACTIONAL_TOKEN_ARC')
        choices=sorted((t for t in nxt if t['species_id']==s),key=lambda t:(0 if t['token_id'].startswith('INHERITED:') else 1,t['token_id']))
        if len(choices)<n:raise ValueError('NOT_PETRI_ENABLED '+s)
        for t in choices[:int(n)]:nxt.remove(t);used.append(t)
    gathered=defaultdict(list)
    for t in used:
        for r,v in t['labels'].items():gathered[r].append(v)
    produced=[]
    for s,n in sorted(q['products'].items()):
        if F(n).denominator!=1:raise ValueError('UNSUPPORTED_FRACTIONAL_TOKEN_ARC')
        for j in range(int(F(n))):
            labels={}
            if labelled:
                for r in roles(s):
                    if len(gathered[r])!=1:raise ValueError('INVALID_LINEAGE '+r+' '+eid)
                    labels[r]=gathered[r].pop()
            produced.append({'token_id':eid+':'+s+':'+str(j+1).zfill(2),'species_id':s,'labels':labels})
    if labelled and any(gathered.values()):raise ValueError('INVALID_LINEAGE carrier lost '+eid)
    return sorted(nxt+produced,key=lambda t:t['token_id']),used,produced
def discover(pool,waypoints,allowed,rx):
    evidence=[];whole=[];achieved=[]
    for target in waypoints:
        initial_leg_pool=copy.deepcopy(pool)
        queue=deque([(pool,[])]);seen={statekey(pool,whole,achieved)};expanded=0;depth_cut=False;found=None;deepest=0
        while queue:
            p,leg=queue.popleft();expanded+=1;deepest=max(deepest,len(leg));m=marking(p)
            if all(F(m.get(s,'0'))>=F(n) for s,n in target.items()):found=(p,leg);break
            if len(leg)>=LIMITS['events_per_leg']:depth_cut=True;continue
            for r in allowed:
                q=rx[r]
                if not all(F(m.get(s,'0'))>=F(n) for s,n in q['reactants'].items()):continue
                nxt,_,_=fire(p,q,'DISCOVERY:E'+str(len(whole)+len(leg)+1).zfill(3))
                k=statekey(nxt,whole+leg+[r],achieved)
                if k in seen:continue
                if len(seen)>=LIMITS['visited_per_leg']:raise ValueError('SEARCH_INCONCLUSIVE visited bound '+json.dumps(target))
                seen.add(k);queue.append((nxt,leg+[r]))
        ev={'target_marking':target,'visited':len(seen),'expanded':expanded,'depth_reached':deepest,'depth_budget_encountered':depth_cut,'frontier_exhausted':not queue and not found,'limits':LIMITS,'status':'REACHED' if found else 'SEARCH_INCONCLUSIVE' if depth_cut else 'FRONTIER_EXHAUSTED','allowed_source_directions':allowed,'initial_finite_pool':initial_leg_pool}
        if not found:raise ValueError(json.dumps(ev,sort_keys=True))
        pool,leg=found;whole+=leg;achieved.append(json.dumps(target,sort_keys=True));ev['events']=leg;ev['initial_leg_pool_sha256']=digest_pool(initial_leg_pool);evidence.append(ev)
        if len(whole)>LIMITS['events_per_witness']:raise ValueError('SEARCH_INCONCLUSIVE total event bound')
    return whole,evidence
def digest_pool(pool):
    import hashlib
    return hashlib.sha256(json.dumps(pool,sort_keys=True).encode()).hexdigest()
def exact_net(ids,rx):
    v=defaultdict(F)
    for r in ids:
        for s,n in rx[r]['reactants'].items():v[s]-=F(n)
        for s,n in rx[r]['products'].items():v[s]+=F(n)
    return low.exact(v)
def construct(wid,initial,supplies,ids,rx,search=None,start=None,upstream=None,inherited_tokens=None):
    inherited_tokens=copy.deepcopy(inherited_tokens) if inherited_tokens is not None else seed(initial,'INHERITED',bridge=bool(upstream))
    pool=inherited_tokens+seed(supplies,'ADDED',bridge=bool(upstream));initial_pool=copy.deepcopy(pool)
    events=[];trace=[];dag=[];carrier=[];cut=len(upstream['reaction_occurrences']) if upstream else 0
    for i,r in enumerate(ids):
        if upstream and i==cut:
            for t in pool:
                if not t['labels']:t['labels']={role:t['token_id']+':'+role for role in roles(t['species_id'])}
        eid=f'{wid}:E{i+1:03d}';before=marking(pool);q=rx[r]
        pool,used,produced=fire(pool,q,eid,labelled=i>=cut)
        ev={'event_id':eid,'reaction_id':r,'inputs':q['reactants'],'outputs':q['products'],'equation':q['equation'],'reference_parameter':q['reference_parameter'],'reverse_reaction_ids':q['reverse_reaction_ids'],'consumed_tokens':copy.deepcopy(used),'produced_tokens':copy.deepcopy(produced),'source_segment':'SIGNED_W4' if i<cut else 'B1_3'}
        events.append(ev);trace.append({'event_id':eid,'before':before,'after':marking(pool)})
        for t in used:dag.append({'producer_token':t['token_id'],'consumer_event':eid,'source_species':t['species_id'],'evidence_status':'EXTRACTED','authority':'CANONICAL_SBML','confidence':'EXACT_ORIGIN_ALLOCATION'})
        if i>=cut:carrier.append(copy.deepcopy({'event_id':eid,'inputs':[{**t,'source_roles':roles(t['species_id'])} for t in used],'outputs':[{**t,'source_roles':roles(t['species_id'])} for t in produced]}))
    net=exact_net(ids,rx);final=marking(pool)
    initial_all=Counter({s:int(F(n)) for s,n in initial.items()});initial_all.update({s:int(F(n)) for s,n in supplies.items()})
    ledger_species=sorted(set(initial_all)|set(final)|set(net)|RES|FACTORS|{'RS30S','RS50S','mRNA','tRNAGlyGCC','Pept0003','Pept0003tRNAGlyGCC'})
    return {'witness_id':wid,'initial_inherited_inventory':initial,'initial_inherited_tokens':inherited_tokens,'added_conditional_supplies':supplies,'initial_marking':{s:str(n) for s,n in sorted(initial_all.items()) if n},'initial_tokens':initial_pool,'reaction_occurrences':events,'occurrence_vector':dict(sorted(Counter(ids).items())),'per_event_markings':trace,'final_marking':final,'final_tokens':pool,'exact_net_stoichiometry':net,'lineage_DAG':dag,'carrier_lineage':carrier,'resource_ledger':{s:{'inherited':initial.get(s,'0'),'added':supplies.get(s,'0'),'initial':str(initial_all.get(s,0)),'event_net':net.get(s,'0'),'final':final.get(s,'0'),'events':[e['event_id'] for e in events if s in e['inputs'] or s in e['outputs']]} for s in ledger_species},'search_evidence':search or [],'starting_post_release_witness':start,'upstream_W4':{'path':'docs/reduction/pathways/phase_b1_2_witnesses.json','sha256':digest(OUT/'phase_b1_2_witnesses.json'),'event_count':cut,'handoff_marking':upstream['final_marking'],'scientific_restrictions_unchanged':['H3','H4','H6']} if upstream else None,'scientific_status':'PENDING_HUMAN_REVIEW','claims':{'kinetic_dominance':False,'global_elemental_moiety_conservation':False,'endogenous_EFG_GTP_regeneration':False,'full_composition_certified':False}}
def read_view(data,inv):
    lines=['# B1-3 源精确终止与核糖体回收路径','', 'PENDING_HUMAN_REVIEW；代表性有限Petri证据。参数仅标明作者可用方向，不表明通量主导或生理时序。','', '## 核心结论','', 'RF1/RF2竞争同一RF-free T_pre；各一次肽释放后仍留下RF结合终止复合物。直接解离与RF3协助为替代。两支汇合termRS70SUAA0004_tRNAGlyGCC。RRF结合不等于70S拆分；实际拆分事件见下面源方程。EFG_GDP/RF3_GDP保持结合核苷酸源种，不能计为free GDP。','']
    for w in data['witnesses']:
        lines+=['## '+w['witness_id'],'','继承库存：`'+json.dumps(w['initial_inherited_inventory'],ensure_ascii=False,sort_keys=True)+'`','', '新条件供应：`'+json.dumps(w['added_conditional_supplies'],sort_keys=True)+'`','', '| 事件 | 原始ID | 作者k1 | 精确方程 |','|---|---|---:|---|']
        for e in w['reaction_occurrences']:lines.append('| '+e['event_id']+' | '+e['reaction_id']+' | '+e['reference_parameter']+' | `'+e['equation']+'` |')
        lines+=['','最终精确源种：`'+json.dumps(w['final_marking'],sort_keys=True)+'`','', '事件和（CONCEPTUAL_NET，不是新源反应）：`'+json.dumps(w['exact_net_stoichiometry'],sort_keys=True)+'`','', '每个源种继承+新增+事件净值=终值，完整逐事件账本、token和角色来源见 witnesses.json 的同名对象。','']
    lines+=['## 替代、逆向与边界','', '所有968方向及每个选中方向的完整方程、精确逆向、五子系统映射、作者零参数和降解出口见source_scope.json。未枚举所有路径；循环和正参数逆向仍在每个搜索的allowed_source_directions中。','', 'RF3_GDP交换路线释放free GDP，随后消耗free GTP；RF3_GTP预供应路线不消耗free GTP。回收EFG_GTP是独立新lot，不是W4耗尽的两个lot。W4五个PO4在joint中仅计一次。H2O/H+隐含、完整分子组成与真实再生未证明。','']
    return '\n'.join(lines)+'\n'
def build():
    assert BASE.exists() and PROTOCOL.exists()
    inv=inventory();rx=inv['reactions'];allowed=inv['search_direction_ids'];ws=[];by={}
    def add(wid,initial,supply,targets,start=None,upstream=None,prefix=None):
        inherited=by[start]['final_tokens'] if start else seed(initial)
        pool=copy.deepcopy(inherited)+seed(supply,'ADDED');ids,ev=discover(pool,targets,allowed,rx)
        w=construct(wid,initial,supply,ids,rx,ev,start,inherited_tokens=inherited);ws.append(w);by[wid]=w;return w
    for factor in ['RF1','RF2']:
        n=factor[-1];wid='W_T'+n+'_'+factor+'_RELEASE'
        release=add(wid,{T:'1'},{factor:'1'},[{T+'_'+factor:'1'},{'Pept0003':'1',TERM+'_'+factor:'1'}])
        direct=add('W_D'+n+'_'+factor+'_DIRECT',release['final_marking'],{},[{TERM:'1',factor:'1'}],wid)
        common=[{TERM+'_RF3_GTP':'1',factor:'1'},{TERM+'_RF3_GDP_PO4':'1'},{TERM+'_RF3_GDP':'1','PO4':'1'},{TERM:'1','RF3_GDP':'1'}]
        rf3=add('W_F'+n+'_'+factor+'_RF3_EXCHANGE',release['final_marking'],{'RF3_GDP':'1','GTP':'1'},[{TERM+'_'+factor+'_RF3_GDP':'1'},{TERM+'_'+factor+'_RF3':'1','GDP':'1'},{TERM+'_'+factor+'_RF3_GTP':'1'}]+common,wid)
        add('W_F'+n+'_'+factor+'_RF3_GTP_SUPPLY',release['final_marking'],{'RF3_GTP':'1'},[{TERM+'_'+factor+'_RF3_GTP':'1'}]+common,wid)
        add('W_F'+n+'_'+factor+'_RF3_APO_SUPPLY',release['final_marking'],{'RF3':'1','GTP':'1'},[{TERM+'_'+factor+'_RF3':'1'},{TERM+'_'+factor+'_RF3_GTP':'1'}]+common,wid)
        targets=[{TERM:'1',factor:'1'},{TERM+'_RRF':'1'},{TERM+'_RRF_EFG_GTP':'1'},{TERM+'_RRF_EFG_GDP_PO4':'1'},{TERM+'_RRF_EFG_GDP':'1','PO4':'1'},{'RS50S_tRNAGlyGCC_RRF_EFG_GDP':'1','termRS30S_mRNA':'1'},{'RS30S':'1','RS50S':'1','mRNA':'1','tRNAGlyGCC':'1','RRF':'1','EFG_GDP':'1'}]
        recycling=add('W_R'+n+'_'+factor+'_TO_RECYCLING',release['final_marking'],{'RRF':'1','EFG_GTP':'1'},targets,wid)
        alt=copy.deepcopy(targets);alt[1]={TERM+'_EFG_GTP':'1'}
        add('W_R'+n+'_'+factor+'_EFG_FIRST',release['final_marking'],{'RRF':'1','EFG_GTP':'1'},alt,wid)
        add('W_R'+n+'_'+factor+'_AFTER_RF3',rf3['final_marking'],{'RRF':'1','EFG_GTP':'1'},targets[1:],rf3['witness_id'])
        old=next(w for w in load(OUT/'phase_b1_2_witnesses.json')['witnesses'] if w['witness_id']=='W4')
        suffix=[e['reaction_id'] for e in release['reaction_occurrences']]+[e['reaction_id'] for e in recycling['reaction_occurrences']]
        joint=construct('W_JOINT_'+factor,old['initial_marking'],{factor:'1','RRF':'1','EFG_GTP':'1'},[e['reaction_id'] for e in old['reaction_occurrences']]+suffix,rx,start=wid,upstream=old)
        ws.append(joint);by[joint['witness_id']]=joint
        after=by['W_R'+n+'_'+factor+'_AFTER_RF3']
        rf3_suffix=[e['reaction_id'] for e in release['reaction_occurrences']+rf3['reaction_occurrences']+after['reaction_occurrences']]
        joint_rf3=construct('W_JOINT_'+factor+'_RF3',old['initial_marking'],{factor:'1','RF3_GDP':'1','GTP':'1','RRF':'1','EFG_GTP':'1'},[e['reaction_id'] for e in old['reaction_occurrences']]+rf3_suffix,rx,start=wid,upstream=old)
        ws.append(joint_rf3);by[joint_rf3['witness_id']]=joint_rf3
    # Exact cumulative ledgers for every staged branch; no additional discovery.
    for staged in list(ws):
        if not staged.get('starting_post_release_witness') or staged.get('upstream_W4'):continue
        ancestors=[];current=staged
        while current:
            ancestors.insert(0,current)
            current=by.get(current.get('starting_post_release_witness'))
        supplies=Counter();ids=[]
        for part in ancestors:
            supplies.update({s:int(F(n)) for s,n in part['added_conditional_supplies'].items()})
            ids.extend(e['reaction_id'] for e in part['reaction_occurrences'])
        total=construct('W_C_'+staged['witness_id'],ancestors[0]['initial_inherited_inventory'],{s:str(n) for s,n in sorted(supplies.items())},ids,rx)
        total['cumulative_of_witness_ids']=[part['witness_id'] for part in ancestors]
        ws.append(total)
    data={'phase':'B1-3','protocol_sha256':digest(PROTOCOL),'source_baseline_sha256':digest(BASE),'search_limits':LIMITS,'witnesses':ws,'scientific_status':'PENDING_HUMAN_REVIEW','knowledge_navigation':{'reaction_inventory':'phase_b1_3_source_scope.json','edges':'per-witness lineage_DAG','authority':'CANONICAL_SBML_AND_SIGNED_UPSTREAM','source_state_projection':'INFERRED_CARRIER_IDENTITIES_NOT_ATOMIC_COMPOSITION'}}
    return data,inv
def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=OUT);args=p.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    try:
        data,inv=build();save(args.output_dir/'phase_b1_3_source_scope.json',inv);save(args.output_dir/'phase_b1_3_witnesses.json',data)
        (args.output_dir/'phase_b1_3_termination_recycling_pathways.md').write_bytes(read_view(data,inv).encode())
        print(json.dumps({'witnesses':len(data['witnesses']),'inventory':inv['coverage'],'events':{w['witness_id']:len(w['reaction_occurrences']) for w in data['witnesses']}}));return 0
    except Exception:
        import traceback,datetime
        with (OUT/'phase_b1_3_failure_evidence.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'stage':'build','traceback':traceback.format_exc(),'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()})+'\n')
        raise
if __name__=='__main__':raise SystemExit(main())
