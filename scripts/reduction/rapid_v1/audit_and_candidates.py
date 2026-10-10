"""Fresh source audit of immutable witnesses and compact candidate navigation."""
import csv,importlib.util
from collections import Counter,defaultdict
from fractions import Fraction as F
from common import *
from mathematics import TAIL,CHAIN,matrix_source

def equation(r):
    side=lambda d:' + '.join((str(v)+' ' if v!=1 else '')+s for s,v in sorted(d.items())) or '0'
    return side(r['reactants'])+' -> '+side(r['products'])

REVIEW=[
('H1','Y','0796;0811','W4末态逐字等于两支共同入口；延长复合物与项目T_pre缩写分开。','继承B1-2 H3/H4/H6限制。'),
('H2','Y','0796;0797;0811;0812','同一枚入口token经一次结合即被消费；可逆重新选择不等于同时进入两支。','不能据孤立速率判断生理主导支。'),
('H3','Y','0798;0813','两支各释放唯一的原始自由Pept0003，留下不同RF-bound终止复合物。','肽释放与因子释放、核糖体回收分开。'),
('H4','CONDITIONAL','0799;0814;0829;0843;0846;0838;0840;0842;0847;0870;0881;0884;0879','直接解离汇合到同一源终止态；RF3-GDP交换路径独立且需有限GTP供应，最终RF3_GDP。','RF3_GDP不计作自由RF3+GDP；不穷举全部替代路线。'),
('H5','CONDITIONAL','0904;0895;0908;0902;0910;0911;0913;0916;0918','0910拆分成bound-50S与termRS30S_mRNA，随后源步骤才释放亚基、mRNA、tRNA、RRF、EFG_GDP。','附加有限EFG_GTP不是B1-2已消费载体的内源再生。'),
('H6','CONDITIONAL','0016;0077;0902;0842','完整S*w独立相等，联合W4仅计一次5PO4，直接回收共6、RF3交换回收共7。','源种账本不是完整元素、磷酸基团、H+/H2O或电荷证书。'),
('H7','CONDITIONAL','0797;0812;0810;0823;0912;0924–0968','源逆向、零参数方向与可执行路径分开；本次检查全部事件的实际作者参数。','结构witness非唯一、非通量主导证明；作者零模式不可泛化。'),
('H8','CONDITIONAL','0796–0923','字面源结构、有限载体分配与数值模型证据分别记录。','所有科学决定仍待研究者；本轮未重跑继承MATLAB99/3/1。'),
('H9','CONDITIONAL','0017;0018;0078;0079;0306;0910;0913–0923','Three-stage为近似；回收7→5投影对受保护边际量闭合；RF1/RF2合并有明确反例。','回收两维微观相关性不能恢复；上游B1-3未正式签署。')]

def audit():
    protection();names,rx,initial=source_network();by={r['id']:r for r in rx};S=matrix_source(names,rx);index={s:i for i,s in enumerate(names)}
    inherited=ROOT/'docs/reduction/pathways';data=load(inherited/'phase_b1_3_witnesses.json')
    # Second pre-existing independent reader and lineage checker, never builder/main.
    spec=importlib.util.spec_from_file_location('b13_independent',ROOT/'scripts/pathways/phase_b1_3/verify_witnesses.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);source=v.source()
    assert set(names)==source['species'] and len(source['reactions'])==968
    for r in rx:
        assert r['reactants']==source['reactions'][r['id']]['reactants'] and r['products']==source['reactions'][r['id']]['products'] and r['k']==source['parameters'][r['id']]
    evidence=[]
    for w in data['witnesses']:
        marking=defaultdict(F,{s:F(n) for s,n in w['initial_marking'].items()});net=defaultdict(F);occ=Counter()
        for e in w['reaction_occurrences']:
            r=by[e['reaction_id']];assert r['k']>0 and all(marking[s]>=n for s,n in r['reactants'].items())
            assert r['reactants']=={s:F(n) for s,n in e['inputs'].items()} and r['products']=={s:F(n) for s,n in e['outputs'].items()}
            for side,sign in [('reactants',-1),('products',1)]:
                for s,n in r[side].items():marking[s]+=sign*n;net[s]+=sign*n
            assert min(marking.values())>=0;occ[r['id']]+=1
        final={s:str(n) for s,n in sorted(marking.items()) if n};assert final==w['final_marking']
        column=S*__import__('sympy').Matrix([occ[r['id']] for r in rx]);assert all(column[index[s]]==__import__('sympy').Rational(str(net[s])) for s in names)
        assert {s:str(n) for s,n in sorted(net.items()) if n}==w['exact_net_stoichiometry']
        lineage=v.lineage(w,source)
        evidence.append({'witness_id':w['witness_id'],'status':'PASS','event_count':sum(occ.values()),'exact_S_full_w':True,'per_event_Petri':True,'nonnegative_stock':True,'lineage':lineage,'final_marking':final,'net':{s:str(n) for s,n in sorted(net.items()) if n}})
    assert by['re0000000796']['reactants'].keys()&by['re0000000811']['reactants'].keys()=={'elRS70SAUAA0004_Pept0003tRNAGlyGCC'}
    assert by['re0000000798']['products']['Pept0003']==1 and by['re0000000813']['products']['Pept0003']==1
    anchors=[int(i) for i in '796 797 798 799 810 811 812 813 814 823 829 843 846 838 840 842 847 870 881 884 879 904 895 908 902 910 911 913 916 918'.split()]
    result={'source_reader_agreement':'PASS','canonical_SBML_sha256':sha(ROOT/'models/pnas2017_full_reference/original/fMGG_synthesis.xml'),'witnesses':evidence,'fresh_source_anchors':{r['id']:{'equation':equation(r),'author_k':str(r['k'])} for r in rx if int(r['id'][2:]) in anchors},'review':[{'id':h,'AI_recommendation':ai,'source_ID_suffixes':ids,'reason':reason,'limitations':lim,'researcher_decision':'','researcher_notes':''} for h,ai,ids,reason,lim in REVIEW],'inherited_negative_controls':'36 stored controls hash verified; intentionally not regenerated','scientific_status':'HUMAN_REVIEW_REQUIRED','protection':protection()}
    save(RESULT/'b1_3_fresh_audit.json',result)
    lines=['# B1-3 独立科学复核','',f"本轮从规范SBML/作者CSV独立重算全部{len(evidence)}条保存的local、cumulative与joint历史。两种独立读源器逐列一致；逐事件Petri、非负库存、S_full*w及原始载体DAG全部PASS。没有复用builder，也没有把历史工程PASS当成科学签署。",'','| 项 | AI建议 | 原始ID后缀 | 数学/结构依据与条件 | 研究者决定 |','|---|---|---|---|---|']
    for h,ai,ids,reason,lim in REVIEW:lines.append(f'| {h} | {ai} | {ids} | {reason} {lim} | ______ |')
    lines+=['','详细逐历史库存与新鲜源方程：`results/reduction/rapid_v1/b1_3_fresh_audit.json`。原始完整事件文档：`docs/reduction/pathways/phase_b1_3_termination_recycling_pathways.md`。','', '主要末端：RF1/RF2直接汇合后回收各产生自由Pept0003、RS30S、RS50S、mRNA、tRNAGlyGCC、RRF、所选RF1/RF2、EFG_GDP，各1。联合直接路径保留W4的两枚EFTu_GDP、两枚EFG_GDP及IF2_GDP，新增回收EFG_GDP，共3；PO4共6。RF3-GDP交换联合路径另有RF3_GDP1、自由GDP1及PO4共7。未消费边界库存完整保留于每条marking。','', '参数速率本轮核实：RF1释放肽k=1/2，RF2=3/2；二者不可只因终点相同合并。0910只释放bound-50S和bound-30S状态，不能在此步即声称亚基全游离。','', '人工决定全部留空；旧B1-3的18份文档和8份脚本字节不变。H3/H4/H6的B1-2条件保持。MATLAB99 passed/3 failed/1 incomplete属于继承状态，本轮未重新执行。']
    (DOC/'b1_3_independent_scientific_audit.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');return result

def candidates():
    names,rx,initial=source_network();ann={r['reaction_id']:r for r in rows(LEGACY/'reaction_level_annotation_v2.csv')};by={r['id']:r for r in rx};charts=load(RESULT/'charts.json');certificate=load(DOC/'mathematical_certificate.json');entries=[]
    def add(cid,priority,species,strategy,status,oldcount,kept,gain,proof,assumptions,cost,filter_=None):
        species=sorted(set(species));own=set(species);incident=[r for r in rx if own&(set(r['reactants'])|set(r['products']))] if filter_ is None else [r for r in rx if filter_(r)]
        moduleIDs={r['id'] for r in incident};boundary=sorted({s for r in incident for side in ['reactants','products'] for s in r[side]}-own)
        reverse={r['id']:[q['id'] for q in rx if r['reactants']==q['products'] and r['products']==q['reactants']] for r in incident}
        competitor=[r['id'] for r in incident if any(s in r['reactants'] for s in species)];inputs=sorted({s for r in incident for s in r['reactants']}&set(boundary));outputs=sorted({s for r in incident for s in r['products']}&set(boundary))
        row={'candidate_id':cid,'priority':priority,'source_species_ids':species,'source_reaction_ids':sorted(moduleIDs),'inputs':inputs,'outputs':outputs,'shared_boundary':boundary,'all_reverse_partners':reverse,'competing_and_outlet_ids':competitor,'source_state_count':oldcount,'proposed_retained_count':kept,'independent_ODE_gain':gain,'strategy':strategy,'status':status,'closure_proof_or_counterexample':proof,'domain_and_assumptions':assumptions,'retained_resource_and_occupancy':'Original source free species, factor/tRNA/ribosome projections, original reaction matrix resource counters; tail quotient loses two micro correlations only.','expected_cost':cost,'source_equations':{r['id']:{'equation':equation(r),'k':str(r['k']),'annotation':ann[r['id']]['level_c_functional_contexts']} for r in incident},'authority':'CANONICAL_SBML_AUTHOR_CSV','confidence':'EXACT_SOURCE_IDS; CANDIDATE_STATUS_SEPARATE','evidence_status':'EXTRACTED_FOR_IDS_INFERRED_FOR_PROPOSAL'};entries.append(row)
    add('SOURCE_GENERAL','P0',names,'exact conservation','EXACT',241,214,27,'27 independent L*S=0; modular rank214; reverified v4 map','All968 directions; source structure fixed','241→214; same source fluxes',lambda r:True)
    add('AUTHOR_SUPPORT_CONSERVATION','P0',certificate['support_invariance']['zero_species'],'support face then independent laws','EXACT',241,175,66,'36 invariant zeros;205 support;30 laws and modular rank175','Initial support face,483 positive author parameters;481 live expressions','175 dynamic chemical coordinates',lambda r:True)
    for j,c in enumerate(CHAIN,1):
        prefix='elRS70SAGGU0002_fMet' if j==1 else 'elRS70SAGGU0003_Pept0002';ss=[s for s in names if s.startswith(prefix) and ('EFTu_' in s or s==c['fast']) and s not in certificate['support_invariance']['zero_species']]
        add('GLY_CHAIN_'+str(j),'P1',ss,'Three-stage mean-dwell closure','CONDITIONAL_CANDIDATE',4,3,1,'Equal aggregate counterexample dProduct=0 vs1000; source mean1007/7000 and variance1/49+1e-6 differ from single exponential','Fixed author irreversible pair; upstream competition retained; initial EFTuGDP>=sum deleted fast states','One fewer independent state per round; pair monomial combined')
    add('RECYCLE_TAIL_7_TO_5','P1',TAIL,'linear exact quotient','EXACT',7,5,2,'P*f=Q*P over rationals; outside rates independent; 0306/0910 inputs included','Release rates1000 and author zero reverse/degradation; protected observables only, not individual micro paths','173 chemical states independent;5 linear tail coordinates')
    rf=[s for s in names if s.startswith('elRS70SAUAA0004_') and s.endswith(('_RF1','_RF2'))]
    add('RF1_RF2_COMMON_ENDPOINT','P1',rf,'merge bound intermediates','REJECTED',2,1,0,'Same aggregate occupancy1 gives Pept derivative1/2 vs3/2','Different source factors/entry rates; preserve both branches','No implemented gain')
    init=[s for s in names if any(t in s for t in ['IF1','IF2','IF3']) and s not in ['IF1','IF2','IF3'] and not s.endswith('_degraded')]
    add('INITIATION_ORDER_POOL','P2',init,'assembly-order occupancy grouping','BLOCKED',len(init),len(init),0,'Equal total occupied30S cannot determine distinct mRNA/IF2/fMet-dependent exits','Shared resources, branched assembly order; no proved closed projection','Full module retained')
    restricted=[r['species'] for r in rows(ROOT/'docs/audit/pnas2017_aminoacylation_A3b_r12/fast_selector_Q.csv')]
    assert len(restricted)==9
    add('AA_RESTRICTED_9','P2',restricted,'separate historical 9-state QSSA object','BLOCKED',9,9,0,'Historical A3b-r12 smoke noncompletion; no new token-closed chart proved','Independent group; never add its9 to a14-state group; no new simulation or promotion','Full microscopic source module retained')
    for enzyme in ['GlyRS','MetRS']:
        ss=[s for s in names if s.startswith(enzyme+'_') and not s.endswith('_degraded')];assert len(ss)==14
        add('AA_'+enzyme+'_BOUND_14','P2',ss,'separate 14 bound-state group; segmented candidate pending','BLOCKED',14,14,0,'Exact enzyme pool lacks occupancy information; same total can have different ATP/AMP/PPi/aa-tRNA derivatives','14 source-bound species are a distinct object, not a sequential9+14 reduction; previous21-QSSA rejected','No closure reimplemented; retain all states')
    ss=[s for s in names if s.startswith('MTF_') and not s.endswith('_degraded')]
    add('FORMYLATION','P2',ss,'segmented closure with donor/product storage','BLOCKED',len(ss),len(ss),0,'Donor/product ligand occupancy supplies distinct exit monomials; no exact pool closure','Keep FD/THF and charged tRNA interfaces','Not implemented; microscopic module retained')
    for enzyme in ['CK','NDK','MK','PPiase']:
        ss=[s for s in names if s==enzyme or s.startswith(enzyme+'_') and not s.endswith('_degraded')]
        add('ENERGY_'+enzyme+'_EXTRA_STORAGE','P3',ss,'new candidate must retain physical product/occupancy storage','BLOCKED',len(ss),len(ss),'NOT_ESTABLISHED','Historical stationary-total graph has zero-product no-root; full-MK/PPiase source-boundary negative-root evidence','Only future extra dynamic storage permitted; do not replace four cycles by stationary elimination','Gain not certified; source microscopic module retained')
    entries.sort(key=lambda e:(e['priority'],-(e['independent_ODE_gain'] if isinstance(e['independent_ODE_gain'],int) else 0),e['candidate_id']))
    save(DOC/'candidate_source_map.json',entries)
    keys=[k for k in entries[0] if k!='source_equations']
    with (DOC/'candidate_matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
        for e in entries:writer.writerow({k:json.dumps(e[k],ensure_ascii=False,separators=(',',':')) if isinstance(e[k],(dict,list)) else e[k] for k in keys})
    return entries
if __name__=='__main__':
    audit();c=candidates();print(json.dumps({'B1_3':'34 fresh exact replays and lineage PASS','candidate_count':len(c),'source_protection':protection()}))
