"""Topology-first descriptive audit. Never changes a model or scientific decision.

Run with Python 3.11+ and networkx 3.2+: python scripts/analyze_pnas2017_topology.py.
Canonical stoichiometry is read directly, including constant stoichiometryMath.
The literal SBML and frozen author-CSV overlay are always separate graph views.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import xml.etree.ElementTree as ET
import zipfile

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/topology_audit'
DOC = ROOT / 'docs/reduction'
MODEL = ROOT / 'models/pnas2017_full_reference/original/fMGG_synthesis.xml'
ARCHIVE = ROOT / 'references/PNAS2017_Matsuura/raw/SBML_files.zip'
AUTHOR = ROOT / 'references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip'
NS = '{http://www.sbml.org/sbml/level2/version4}'
MATH = '{http://www.w3.org/1998/Math/MathML}'
RESOURCE = {'ATP','ADP','AMP','GTP','GDP','GMP','PO4','PPi','CP','Cr',
            'Gly','Met','fMet','FD','THF','tRNAGlyGCC','tRNAfMetCAU',
            'GlytRNAGlyGCC','MettRNAfMetCAU','fMettRNAfMetCAU'}
MACHINERY = {'RS30S','RS50S','mRNA','EFTu','EFG','EFTu_GTP','EFTu_GDP',
             'EFG_GTP','EFG_GDP','IF1','IF2','IF3','RF1','RF2','RRF'}
BACKBONE = [13,14,16,17,18,19,22,24,25]
REPEAT = [74,75,77,78,79,80,83,85,86]

def rid(i): return f're{i:010d}'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def compact(x): return json.dumps(x, sort_keys=True, separators=(',',':'))
def write_csv(name, rows, fields=None):
    path = OUT / name
    if fields is None: fields = list(rows[0]) if rows else ['id']
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fields, lineterminator='\n')
        w.writeheader(); w.writerows(rows)
def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8', newline='\n')
def doc(name, value): (DOC / name).write_text(value.rstrip()+'\n', encoding='utf-8', newline='\n')

def refs(r, side):
    ans = defaultdict(float)
    for ref in r.findall(f'{NS}listOf{side}/{NS}speciesReference'):
        m = ref.find(NS+'stoichiometryMath')
        if m is not None:
            cn = m.findall('.//'+MATH+'cn')
            if len(cn) != 1 or m.findall('.//'+MATH+'apply'):
                raise ValueError('Nonliteral stoichiometryMath requires explicit evaluation')
            val = float(cn[0].text)
        else: val = float(ref.get('stoichiometry','1'))
        ans[ref.attrib['species']] += val
    return dict(ans)

def signature(r):
    return tuple(sorted(r['substrates'].items())), tuple(sorted(r['products'].items()))

def major(filename):
    if filename.startswith(('Aminoacylation','FMet')): return 'aminoacylation'
    if filename.startswith('Initiation'): return 'initiation'
    if filename.startswith('Elongation'): return 'elongation'
    if filename.startswith('Termination'): return 'termination'
    if filename.startswith('EnergyRegeneration'): return 'energy'
    return 'small_molecules'

def csv_member(z, suffix):
    matches = [p for p in z.namelist() if p.endswith(suffix)]
    if len(matches) != 1: raise ValueError(matches)
    raw = z.read(matches[0])
    text = raw.decode('utf-8-sig').replace('\r\r\n','\n').replace('\r\n','\n')
    return matches[0], hashlib.sha256(raw).hexdigest(), list(csv.DictReader(io.StringIO(text)))

def reachable(species, reactions, values, kval):
    available = {s for s in species if values[s] > 0}
    used = set()
    while True:
        old = len(available)
        for r in reactions:
            if kval[r['reaction_id']] > 0 and set(r['substrates']) <= available and set(r['kinetic_species']) <= available:
                used.add(r['reaction_id']); available.update(r['products'])
        if len(available) == old: break
    return available, used

def views(species, reactions, excluded):
    sg = nx.DiGraph(); sg.add_nodes_from(species)
    context = nx.DiGraph(); context.add_nodes_from(set(species)-excluded)
    producers, consumers = defaultdict(set), defaultdict(set)
    rg = nx.DiGraph(); rg.add_nodes_from(r['reaction_id'] for r in reactions)
    bg = nx.DiGraph()
    bg.add_nodes_from('s:'+s for s in species)
    for r in reactions:
        r_id = r['reaction_id']; bg.add_node('r:'+r_id)
        for s,c in r['substrates'].items():
            consumers[s].add(r_id); bg.add_edge('s:'+s,'r:'+r_id, role='substrate', coefficient=c)
        for s,c in r['products'].items():
            producers[s].add(r_id); bg.add_edge('r:'+r_id,'s:'+s, role='product', coefficient=c)
        for a in r['substrates']:
            for b in r['products']:
                if sg.has_edge(a,b): sg[a][b]['reaction_ids'].append(r_id)
                else: sg.add_edge(a,b,reaction_ids=[r_id])
                if a not in excluded and b not in excluded: context.add_edge(a,b)
    for s in species:
        for a in producers[s]:
            for b in consumers[s]:
                if rg.has_edge(a,b): rg[a][b]['shared_species'].append(s)
                else: rg.add_edge(a,b,shared_species=[s])
    return sg, context, rg, bg, producers, consumers

def scc_labels(g):
    comps = sorted(nx.strongly_connected_components(g), key=lambda s:(-len(s),min(s)))
    label, sizes, cyclic = {}, {}, set()
    for i,c in enumerate(comps,1):
        for s in c: label[s]=f'SCC_{i:03d}'; sizes[s]=len(c)
        if len(c)>1 or any(g.has_edge(s,s) for s in c): cyclic.update(c)
    return label,sizes,cyclic

def serial_chains(species, reactions, producers, consumers, excluded):
    # A carrier is eligible only if its full kinetic usage has no other reaction.
    dependencies = defaultdict(set)
    for r in reactions:
        for s in r['kinetic_species']: dependencies[s].add(r['reaction_id'])
    joins = nx.DiGraph()
    for s in species:
        if s in excluded or s.endswith('_degraded'): continue
        if len(producers[s])==1 and len(consumers[s])==1:
            a,b = next(iter(producers[s])),next(iter(consumers[s]))
            if a==b or dependencies[s]-{a,b}: continue
            joins.add_edge(a,b,intermediate=s)
    chains=[]
    for comp in nx.weakly_connected_components(joins):
        g=joins.subgraph(comp)
        if not nx.is_directed_acyclic_graph(g): continue
        if any(g.in_degree(x)>1 or g.out_degree(x)>1 for x in g): continue
        order=list(nx.topological_sort(g))
        if len(order)>=2:
            chains.append({'reaction_ids':order,'internal_species':[g[a][b]['intermediate'] for a,b in zip(order,order[1:])]})
    return sorted(chains, key=lambda c:(-len(c['reaction_ids']),c['reaction_ids']))

def main():
    OUT.mkdir(parents=True,exist_ok=True); DOC.mkdir(parents=True,exist_ok=True)
    root=ET.parse(MODEL).getroot(); model=root.find(NS+'model')
    se=list(model.find(NS+'listOfSpecies')); species=[s.attrib['id'] for s in se]
    source_hash=sha(MODEL)
    with zipfile.ZipFile(AUTHOR) as z:
        im,ih,iv=csv_member(z,'fMGG_synthesis_initial_values.csv')
        pm,ph,pv=csv_member(z,'fMGG_synthesis_parameters.csv')
    initials={r['Name']:float(r['Value']) for r in iv}; params={r['Name']:float(r['Value']) for r in pv}
    assert set(initials)==set(species)
    module_members=defaultdict(list); module_raw={}
    with zipfile.ZipFile(ARCHIVE) as z:
        for path in sorted(z.namelist()):
            if not path.endswith('.xml'): continue
            raw=z.read(path); sm=ET.fromstring(raw).find(NS+'model')
            filename=Path(path).stem
            module_raw[filename]={'module_id':filename,'module_name':filename,'major_module':major(filename),
                'source_member':path,'source_sha256':hashlib.sha256(raw).hexdigest()}
            for r in sm.find(NS+'listOfReactions'):
                sig=(tuple(sorted(refs(r,'Reactants').items())),tuple(sorted(refs(r,'Products').items())))
                module_members[sig].append({'module_id':filename,'source_reaction_id':r.get('id')})
    reactions=[]; kdefault={}; kauthor={}; parameter_rows=[]
    for el in model.find(NS+'listOfReactions'):
        r_id=el.attrib['id']; kl=el.find(NS+'kineticLaw'); math=kl.find(MATH+'math')
        # Reject unsupported expression shapes instead of assuming mass action.
        allowed={MATH+x for x in ('math','apply','times','ci','cn')}
        if any(n.tag not in allowed for n in math.iter()): raise ValueError('Unsupported kinetic MathML')
        local={p.attrib['id']:float(p.attrib['value']) for p in kl.find(NS+'listOfParameters')}
        syms=[n.text.strip() for n in math.iter(MATH+'ci')]
        if any(s not in local and s not in species for s in syms): raise ValueError(syms)
        literals=[float(n.text) for n in math.iter(MATH+'cn')]
        coeff=1.0
        for s in syms:
            if s in local: coeff*=local[s]
        for v in literals: coeff*=v
        kdefault[r_id]=coeff; kauthor[r_id]=params[r_id+'_k1']
        for p in kl.find(NS+'listOfParameters'):
            parameter_rows.append({'scope':'reaction_local','reaction_id':r_id,'parameter_id':p.attrib['id'],
                'sbml_value':float(p.attrib['value']),'author_csv_value':params[r_id+'_'+p.attrib['id']],
                'units_declared':p.get('units',''),'source_sbml_sha256':source_hash})
        r={'reaction_id':r_id,'name':el.get('name',''),'substrates':refs(el,'Reactants'),
           'products':refs(el,'Products'),'modifiers':[x.get('species') for x in el.findall(f'{NS}listOfModifiers/{NS}modifierSpeciesReference')],
           'reversible':el.get('reversible','true')=='true','kinetic_species':[s for s in syms if s in species],
           'kinetic_law_formula':' * '.join(syms+[str(v) for v in literals]),'local_parameters':local,
           'sbml_rate_coefficient':coeff,'author_rate_coefficient':kauthor[r_id]}
        r['source_matches']=module_members[signature(r)]
        assert r['source_matches'],r_id
        reactions.append(r)
    # The simulator CSV also includes compartment size 'default'; it is not k.
    kinetic_names={r['reaction_id']+'_k1' for r in reactions}
    compartments={e.attrib['id']:float(e.get('size','1')) for e in model.find(NS+'listOfCompartments')}
    assert set(params)==kinetic_names|set(compartments)
    write_csv('compartments_table.csv',[{'compartment_id':s,'sbml_size':v,'author_csv_size':params[s]} for s,v in compartments.items()])
    lookup={r['reaction_id']:r for r in reactions}
    initial_default={s.attrib['id']:float(s.get('initialConcentration',s.get('initialAmount','0'))) for s in se}
    available_default, enabled_default=reachable(species,reactions,initial_default,kdefault)
    available_author, enabled_author=reachable(species,reactions,initials,kauthor)
    participating=defaultdict(set); memberships=defaultdict(set)
    module_rx=defaultdict(set); module_sp=defaultdict(set)
    for r in reactions:
        parts=set(r['substrates'])|set(r['products'])|set(r['modifiers'])
        for s in parts: participating[s].add(r['reaction_id'])
        for m in r['source_matches']:
            name=m['module_id']; module_rx[name].add(r['reaction_id']); module_sp[name].update(parts)
            for s in parts: memberships[s].add(name)
    # Threshold is descriptive and fixed before graph extraction; resources retained.
    degree_hubs={s for s in species if len(participating[s])>=30}
    excluded=RESOURCE|MACHINERY|degree_hubs|{s for s in species if s.endswith('_degraded')}
    sg,cg,rg,bg,prod,cons=views(species,reactions,excluded)
    active=[r for r in reactions if kauthor[r['reaction_id']]>0]
    asg,acg,arg,abg,aprod,acons=views(species,active,excluded)
    context_components=[]
    for view,rs,ps,cs in [('FULL_CANONICAL',reactions,prod,cons),('AUTHOR_NONZERO',active,aprod,acons)]:
        crg=nx.Graph(); crg.add_nodes_from(r['reaction_id'] for r in rs)
        for s in set(species)-excluded:
            incident=sorted(ps[s]|cs[s])
            if incident:
                for other in incident[1:]: crg.add_edge(incident[0],other)
        components=sorted(nx.connected_components(crg),key=lambda x:(-len(x),min(x)))
        for i,rx in enumerate(components,1):
            if len(rx)<2: continue
            sp={s for a in rx for s in set(lookup[a]['substrates'])|set(lookup[a]['products'])}
            interface={s for s in sp if participating[s]-rx}
            context_components.append({'component_id':f'CONTEXT_{view}_{i:03d}','graph_view':view,
                'reaction_count':len(rx),'species_count':len(sp),'member_reactions_json':compact(sorted(rx)),
                'member_species_json':compact(sorted(sp)),'interface_species_json':compact(sorted(interface)),
                'interface_nonhub_species_json':compact(sorted(interface-excluded)),
                'source_modules':';'.join(sorted({m['module_id'] for a in rx for m in lookup[a]['source_matches']})),
                'interpretation':'CONNECTED_AFTER_DECLARED_HUB_SUPPRESSION_NOT_DYNAMICAL_INDEPENDENCE'})
    write_csv('context_components.csv',context_components)
    labels,sizes,cyclic=scc_labels(sg); alabels,asizes,acyclic=scc_labels(asg)
    clabels,csizes,ccyclic=scc_labels(cg); aclabels,acsizes,accyclic=scc_labels(acg)
    local_cycles=[]
    for view,g,rs in [('FULL_CANONICAL',cg,reactions),('AUTHOR_NONZERO',acg,active)]:
        comps=sorted((x for x in nx.strongly_connected_components(g) if len(x)>=3),key=lambda x:(-len(x),min(x)))
        for i,sp in enumerate(comps,1):
            rx=[r['reaction_id'] for r in rs if set(r['substrates'])&sp and set(r['products'])&sp]
            local_cycles.append({'cycle_region_id':f'LOCAL_SCC_{view}_{i:03d}','graph_view':view,
                'species_count':len(sp),'reaction_count':len(rx),'member_species_json':compact(sorted(sp)),
                'member_reactions_json':compact(sorted(rx)),
                'source_modules':';'.join(sorted({m['module_id'] for a in rx for m in lookup[a]['source_matches']})),
                'certificate_scope':'PROJECTION_RETURN_WALKS_NOT_FEASIBLE_FLUX_CYCLE_OR_EQUILIBRIUM'})
    write_csv('local_cycle_regions.csv',local_cycles)
    bridge=set(nx.articulation_points(cg.to_undirected()))
    abridge=set(nx.articulation_points(acg.to_undirected()))
    full_chains=serial_chains(species,reactions,prod,cons,excluded)
    author_chains=serial_chains(species,active,aprod,acons,excluded)
    chain_species={s for c in full_chains for s in c['internal_species']}
    achain_species={s for c in author_chains for s in c['internal_species']}
    chain_rx={r for c in full_chains for r in c['reaction_ids']}
    achain_rx={r for c in author_chains for r in c['reaction_ids']}
    signatures=defaultdict(list)
    for r in reactions: signatures[signature(r)].append(r['reaction_id'])
    reverse={r['reaction_id']:sorted(signatures[(signature(r)[1],signature(r)[0])]) for r in reactions}
    pairs=sorted({tuple(sorted((a,b))) for a,bs in reverse.items() for b in bs if a!=b})
    rows=[]
    for s in se:
        sid=s.attrib['id']
        rows.append({'species_id':sid,'name':s.get('name',''),'compartment':s.get('compartment',''),
            'sbml_initial_concentration':initial_default[sid],'author_initial_concentration':initials[sid],
            'sbml_initial_amount':s.get('initialAmount',''),'substance_units_declared':s.get('substanceUnits',''),
            'has_only_substance_units':s.get('hasOnlySubstanceUnits','false'),
            'boundary_condition':s.get('boundaryCondition','false'),'constant':s.get('constant','false'),
            'dynamic':s.get('boundaryCondition','false')!='true' and s.get('constant','false')!='true',
            'sbml_zero_initial':initial_default[sid]==0,'author_zero_initial':initials[sid]==0,
            'author_potentially_reachable':sid in available_author,'source_sbml_sha256':source_hash})
    write_csv('species_table.csv',rows); write_csv('parameters_table.csv',parameter_rows)
    reaction_rows=[]
    for r in reactions:
        ainit=r['author_rate_coefficient']
        for s in r['kinetic_species']: ainit*=initials[s]
        reaction_rows.append({'reaction_id':r['reaction_id'],'original_name':r['name'],'substrates_json':compact(r['substrates']),
            'products_json':compact(r['products']),'modifiers_json':compact(r['modifiers']),
            'reversible':r['reversible'],'kinetic_law_formula':r['kinetic_law_formula'],
            'kinetic_species_json':compact(r['kinetic_species']),'local_parameters_json':compact(r['local_parameters']),
            'sbml_rate_coefficient':r['sbml_rate_coefficient'],'author_rate_coefficient':r['author_rate_coefficient'],
            'sbml_structurally_enabled':r['reaction_id'] in enabled_default,
            'author_initial_rate_numerical':ainit,'author_initial_rate_zero':ainit==0,
            'author_activity':'ZERO_K_PROVEN_INACTIVE' if r['author_rate_coefficient']==0 else (
                'UNREACHABLE_MASS_ACTION_PROVEN_INACTIVE' if r['reaction_id'] not in enabled_author else 'POTENTIALLY_ENABLED_NOT_TRAJECTORY_CERTIFIED'),
            'source_module_ids':';'.join(sorted({m['module_id'] for m in r['source_matches']})),
            'source_matches_json':compact(r['source_matches']),'source_sbml_sha256':source_hash})
    write_csv('reactions_table.csv',reaction_rows)
    matrix=[]
    for s in species:
        row={'species_id':s}
        for r in reactions: row[r['reaction_id']]=r['products'].get(s,0)-r['substrates'].get(s,0)
        matrix.append(row)
    write_csv('stoichiometric_matrix.csv',matrix)
    smetrics=[]
    for s in species:
        smetrics.append({'species_id':s,'in_degree':sg.in_degree(s),'out_degree':sg.out_degree(s),
            'producing_reactions':len(prod[s]),'consuming_reactions':len(cons[s]),
            'branch_full':len(cons[s])>1,'merge_full':len(prod[s])>1,
            'branch_author':len(acons[s])>1,'merge_author':len(aprod[s])>1,
            'reactions_participated':len(participating[s]),'degree_hub_ge30':s in degree_hubs,
            'likely_resource_energy_carrier':s in RESOURCE,'likely_shared_machinery':s in MACHINERY,
            'likely_internal_intermediate':s not in excluded and not s.endswith('_degraded') and bool(prod[s]) and bool(cons[s]),
            'serial_chain_internal_full':s in chain_species,'serial_chain_internal_author':s in achain_species,
            'full_scc':labels[s],'full_scc_size':sizes[s],'projection_cycle_full':s in cyclic,
            'author_scc':alabels[s],'author_scc_size':asizes[s],'projection_cycle_author':s in acyclic,
            'context_scc':clabels.get(s,''),'context_cycle_full':s in ccyclic,
            'context_cycle_author':s in accyclic,'context_articulation_full':s in bridge,
            'context_articulation_author':s in abridge,'source_module_count':len(memberships[s]),
            'source_module_ids':';'.join(sorted(memberships[s])),
            'cross_module_bridge_candidate':len(memberships[s])>=2 and s not in excluded,
            'inference_status':'INFERRED_TOPOLOGY_CANDIDATE','HUMAN_REVIEW_REQUIRED':True})
    write_csv('species_topology_metrics.csv',smetrics)
    rmetrics=[]
    for r in reactions:
        a=r['reaction_id']; parts=set(r['substrates'])|set(r['products'])
        contexts=[]
        if a in chain_rx: contexts.append('SERIAL_FULL')
        if a in achain_rx: contexts.append('SERIAL_AUTHOR_NONZERO')
        if any(len(cons[s])>1 for s in r['substrates']): contexts.append('BRANCH')
        if any(len(prod[s])>1 for s in r['products']): contexts.append('MERGE')
        if reverse[a]: contexts.append('EXACT_REVERSE_PAIR')
        if any(s in ccyclic for s in parts): contexts.append('CONTEXT_PROJECTION_CYCLE')
        if parts&(RESOURCE|degree_hubs): contexts.append('HUB_ATTACHED')
        if not r['substrates']: contexts.append('SOURCE')
        if not r['products']: contexts.append('SINK')
        if any(s.endswith('_degraded') for s in r['products']): contexts.append('TERMINAL_DEGRADATION')
        rmetrics.append({'reaction_id':a,'substrates_json':compact(r['substrates']),'products_json':compact(r['products']),
            'reversible_attribute':r['reversible'],'reverse_reaction_ids':';'.join(reverse[a]),
            'projected_reaction_in_degree':rg.in_degree(a),'projected_reaction_out_degree':rg.out_degree(a),
            'context_tags':';'.join(contexts),'repeated_growth_backbone':a in {rid(i) for i in BACKBONE+REPEAT},
            'author_rate_positive':kauthor[a]>0,'HUMAN_REVIEW_REQUIRED':True})
    write_csv('reaction_topology_metrics.csv',rmetrics)
    write_csv('bipartite_edges.csv',[{'source':a,'target':b,**d} for a,b,d in bg.edges(data=True)])
    write_csv('kinetic_dependency_edges.csv',[{'species_id':s,'reaction_id':r['reaction_id'],'role':'kinetic_dependency_not_stoichiometric_arc'} for r in reactions for s in r['kinetic_species']])
    write_csv('projected_species_edges.csv',[{'source_species':a,'target_species':b,'reaction_ids':';'.join(sorted(d['reaction_ids']))} for a,b,d in sorted(sg.edges(data=True))])
    write_csv('projected_reaction_edges.csv',[{'source_reaction':a,'target_reaction':b,'shared_species_ids':';'.join(sorted(d['shared_species']))} for a,b,d in sorted(rg.edges(data=True))])
    write_csv('reverse_pairs.csv',[{'forward_id':a,'reverse_id':b,'both_author_positive':kauthor[a]>0 and kauthor[b]>0,'author_forward_k':kauthor[a],'author_reverse_k':kauthor[b]} for a,b in pairs])
    motifs=[]
    def add(mid,kind,sp,rx,view,category,why,limits):
        motifs.append({'motif_id':mid,'motif_type':kind,'member_species_json':compact(sorted(sp)),
            'member_reactions_json':compact(rx),'graph_view':view,'category':category,'topological_evidence':why,
            'required_assumptions_and_consequences':limits,'evidence_status':'INFERRED',
            'confidence':'STRUCTURE_EXTRACTED_REDUCTION_UNVALIDATED','HUMAN_REVIEW_REQUIRED':True})
    for view,chains in [('FULL_CANONICAL',full_chains),('AUTHOR_NONZERO',author_chains)]:
        for i,c in enumerate(chains,1):
            add(f'SERIAL_{view}_{i:03d}','SERIAL_CHAIN',c['internal_species'],c['reaction_ids'],view,
                'AGGREGATE_STATE_CANDIDATE','Every internal species has one producer, one consumer, no external kinetic dependency; acyclic maximal reaction path.',
                'Topology is necessary, not a Markov-closure proof. Preserve boundary fluxes, occupancy, staged resource release, and startup delay. AUTHOR_NONZERO depends on frozen zero directions.')
    for i,(a,b) in enumerate(pairs,1):
        sp=set(lookup[a]['substrates'])|set(lookup[a]['products'])
        both=kauthor[a]>0 and kauthor[b]>0
        add(f'REVERSE_{i:03d}','LOCAL_REVERSE_PAIR',sp,[a,b],'FULL_CANONICAL',
            'QSSA_CANDIDATE' if both else 'UNSURE',
            'Exact reactant/product stoichiometric swap; signed net-flux rewrite is exact and removes no species.',
            'One pair is not an isolated fast block. Local QSSA/equilibrium needs boundary coupling and timescale/observable evidence; gross fluxes must be retained if required. Both author directions positive='+str(both))
    for name in sorted(module_raw):
        sp=module_sp[name]; rx=sorted(module_rx[name]); outside=set()
        for s in sp:
            if participating[s]-module_rx[name]: outside.add(s)
        route='QSSA_CANDIDATE' if name.startswith(('Aminoacylation','EnergyRegeneration','FMet')) else 'UNSURE'
        add('MODULE_'+name,'NEAR_SEPARABLE_SOURCE_SUBNETWORK',sp,rx,'FULL_CANONICAL',route,
            f'Source-signature module; {len(outside)} interface species, {len(outside-excluded)} retained nonhub interfaces; no disconnectedness claim.',
            'External shared-carrier/machinery coupling remains explicit; treat as open subsystem. Source provenance alone does not prove weak dynamical coupling.')
    for r in local_cycles:
        add(r['cycle_region_id'],'LOCAL_CYCLIC_REGION',json.loads(r['member_species_json']),
            json.loads(r['member_reactions_json']),r['graph_view'],'UNSURE',
            f"Context projection SCC with {r['species_count']} species and {r['reaction_count']} participating directed reactions supports return walks.",
            'Not a feasible-flux-cycle/equilibrium certificate. Restore shared resource reactant-AND requirements and derive net stoichiometric ledger before selecting a local kinetic block.')
    for n,rs in [('FIRST_GLY',BACKBONE),('SECOND_GLY',REPEAT)]:
        sp={s for i in rs for s in set(lookup[rid(i)]['substrates'])|set(lookup[rid(i)]['products'])}
        add(n,'REPEATED_ELONGATION_BACKBONE',sp,[rid(i) for i in rs],'AUTHOR_NONZERO',
            'AGGREGATE_STATE_CANDIDATE','Two source-supported ordered Gly addition backbones with docking and factor return cycles.',
            'Not a pure unbranched serial chain and not a long polymer lattice. Preserve Gly/aa-tRNA use, factor nucleotide state, two PO4 releases and ribosome position; one E does not close all ledgers.')
    for option,category in [('DIRECT','DIRECT_LUMP_CANDIDATE'),('E_MID','AGGREGATE_STATE_CANDIDATE'),('EXPLICIT','KEEP_EXPLICIT')]:
        add('CASE_16_18_'+option,'DERIVED_CASE_OPTION',
            {s for i in (16,17,18) for s in set(lookup[rid(i)]['substrates'])|set(lookup[rid(i)]['products'])},
            [rid(i) for i in (16,17,18)],'AUTHOR_NONZERO',category,
            'Actual three-step serial subpath has no active internal side branch; summed net S0 -> S3 + PO4 + EFTu_GDP.',
            'Explicit analytical option, not an automatic deletion rule. Direct mean-dwell closure changes delay/occupancy; E_mid conserves summed occupancy but needs conditional composition or memory; explicit baseline retains each ledger. See case study.')
    for name in ('ATP','GTP','GDP','ADP','PO4','RS30S','RS50S','tRNAGlyGCC'):
        add('HUB_'+name,'HUB_ATTACHED', [name],sorted(participating[name]),'FULL_CANONICAL','KEEP_EXPLICIT',
            f'{len(participating[name])} participating reactions across {len(memberships[name])} source modules.',
            'Shared resource competition and bound/free reconstruction constrain any future coordinate change; degree does not establish dispensability.')
    write_csv('motif_catalog.csv',motifs)
    major_sp=defaultdict(set); major_rx=defaultdict(set)
    for name in module_raw:
        group=major(name); major_sp[group].update(module_sp[name]); major_rx[group].update(module_rx[name])
    routes={'aminoacylation':'QSSA_AFTER_TOPOLOGY','initiation':'DO_NOT_TOUCH_YET',
        'elongation':'TOPOLOGY_REDUCE_FIRST','termination':'KEEP_EXPLICIT','energy':'QSSA_AFTER_TOPOLOGY','small_molecules':'KEEP_EXPLICIT'}
    names={'aminoacylation':'Aminoacylation / formylation','initiation':'Initiation','elongation':'Elongation (two Gly additions)',
        'termination':'Termination / recycling','energy':'Energy regeneration','small_molecules':'Shared small molecules'}
    module_table=[]
    for group in sorted(major_sp):
        module_table.append({'module_id':group,'module_name':names[group],'species_count':len(major_sp[group]),
            'reaction_count':len(major_rx[group]),'author_nonzero_reaction_count':sum(kauthor[r]>0 for r in major_rx[group]),
            'shared_species_count':sum(len(memberships[s])>1 for s in major_sp[group]),'reduction_route':routes[group]})
    write_csv('module_table.csv',module_table)
    interfaces=[]
    groups=sorted(major_sp)
    for i,a in enumerate(groups):
        for b in groups[i+1:]:
            common=major_sp[a]&major_sp[b]
            if common: interfaces.append({'module_a':a,'module_b':b,'shared_species_count':len(common),
                'shared_species_ids':';'.join(sorted(common)),'nonhub_shared_species_count':len(common-excluded),
                'nonhub_shared_species_ids':';'.join(sorted(common-excluded))})
    write_csv('module_interfaces.csv',interfaces)
    hubs=[{'species_id':s,'reactions_participated':len(participating[s]),'producing_reactions':len(prod[s]),
        'consuming_reactions':len(cons[s]),'module_count':len(memberships[s]),
        'resource_role':'RESOURCE_OR_ENERGY' if s in RESOURCE else ('SHARED_MACHINERY' if s in MACHINERY else 'DEGREE_HUB'),
        'author_reactions_participated':len(aprod[s]|acons[s])} for s in degree_hubs|RESOURCE|MACHINERY if s in participating]
    hubs.sort(key=lambda r:(-r['reactions_participated'],r['species_id'])); write_csv('hub_table.csv',hubs)
    detailed=[]; reduction_map=[]
    for name in sorted(module_raw):
        sp=module_sp[name]; rx=module_rx[name]
        outside={s for s in sp if participating[s]-rx}
        detailed.append({**module_raw[name],'species_count':len(sp),'reaction_count':len(rx),
            'author_nonzero_reaction_count':sum(kauthor[r]>0 for r in rx),
            'interface_species_count':len(outside),'nonhub_interface_count':len(outside-excluded),
            'nonhub_species_count':len(sp-excluded),
            'nonhub_interface_fraction':len(outside-excluded)/len(sp-excluded) if sp-excluded else 0,
            'interface_species_ids':';'.join(sorted(outside)),
            'relative_separability_status':'OPEN_SUBNETWORK_WITH_MEASURED_INTERFACES'})
        route=routes[major(name)]
        if name.startswith('Elongation_A'): route='QSSA_ONLY'
        if name.startswith('Elongation_B'): route='KEEP_EXPLICIT'
        reduction_map.append({'region':name,'route':route,'member_reactions_json':compact(sorted(rx)),
            'member_species_json':compact(sorted(sp)),'nonhub_interface_count':len(outside-excluded),
            'reason':'Carrier assembly locally kinetic' if route=='QSSA_ONLY' else (
                'Two growth backbones: prototype serial segment before any local elimination' if route=='TOPOLOGY_REDUCE_FIRST' else 'Source open subnetwork; shared resources and machinery must remain coupled'),
            'decision_status':'PENDING','HUMAN_REVIEW_REQUIRED':True})
    write_csv('source_subnetworks.csv',detailed); write_csv('reduction_map.csv',reduction_map)
    serial=[rid(i) for i in (16,17,18)]
    serial_species=['elRS70SAGGU0002_fMet_EFTu_GDP_PO4_GlytRNAGlyGCC',
        'elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC',
        'elRS70SAGGU0002_fMet_GlytRNAGlyGCC','elRS70SBGGU0002_Pept0002tRNAGlyGCC']
    def net(ids):
        ans=defaultdict(float)
        for a in ids:
            for s,c in lookup[a]['products'].items(): ans[s]+=c
            for s,c in lookup[a]['substrates'].items(): ans[s]-=c
        return {s:c for s,c in sorted(ans.items()) if c}
    case={'first_backbone_reaction_ids':[rid(i) for i in BACKBONE],'second_backbone_reaction_ids':[rid(i) for i in REPEAT],
        'entry_species':'elRS70SAGGU0002_fMet','exit_species':'elRS70SAGGU0003_Pept0002tRNAGlyGCC',
        'serial_reaction_ids':serial,'serial_species_ids':serial_species,
        'serial_reactions':[{'reaction_id':a,'substrates':lookup[a]['substrates'],'products':lookup[a]['products'],
            'author_k':kauthor[a]} for a in serial],
        'net_stoichiometry':net([rid(i) for i in BACKBONE]),'serial_net_stoichiometry':net(serial),
        'internal_side_reactions':{s:sorted((prod[s]|cons[s])-set(serial)) for s in serial_species[1:3]},
        'internal_author_side_reactions':{s:sorted((aprod[s]|acons[s])-set(serial)) for s in serial_species[1:3]},
        'aggregate_definition':'E_mid = S1 + S2; retain A=S0 and B=S3',
        'aggregate_exact_balance':'dE_mid/dt = v16 - v18; PO4 flux=v16; EFTu_GDP flux=v17',
        'source_default':'AUTHOR_CSV_OVERLAY','proposal':'AGGREGATE_STATE_CANDIDATE_UNVALIDATED',
        'direct_mean_dwell_rate':1/sum(1/kauthor[a] for a in serial),
        'aggregate_mean_exit_rate':1/sum(1/kauthor[a] for a in serial[1:]),
        'source_sbml_sha256':source_hash,'HUMAN_REVIEW_REQUIRED':True}
    write_json('case_study.json',case)
    counts={'species':len(species),'dynamic_species':sum(r['dynamic'] for r in rows),'reactions':len(reactions),
        'sbml_zero_initial':sum(v==0 for v in initial_default.values()),'sbml_zero_k':sum(v==0 for v in kdefault.values()),
        'sbml_inactive_reactions':len(reactions)-len(enabled_default),'author_zero_initial':sum(v==0 for v in initials.values()),
        'author_positive_initial':sum(v>0 for v in initials.values()),'author_zero_k':sum(v==0 for v in kauthor.values()),
        'author_nonzero_k':len(active),'author_initial_zero_rate':sum(r['author_initial_rate_zero'] for r in reaction_rows),
        'author_nonzero_k_unreachable_reactions':sum(kauthor[r['reaction_id']]>0 and r['reaction_id'] not in enabled_author for r in reactions),
        'source_subnetworks':len(module_raw),'exact_reverse_pairs':len(pairs),
        'both_author_positive_reverse_pairs':sum(kauthor[a]>0 and kauthor[b]>0 for a,b in pairs),
        'full_strict_serial_chains':len(full_chains),'author_strict_serial_chains':len(author_chains),
        'degree_hubs_ge30':len(degree_hubs),'full_branch_species':sum(len(cons[s])>1 for s in species),
        'author_branch_species':sum(len(acons[s])>1 for s in species),
        'full_largest_species_scc':max(sizes.values()),'author_largest_species_scc':max(asizes.values()),
        'bipartite_nodes':bg.number_of_nodes(),'bipartite_edges':bg.number_of_edges(),
        'projected_species_edges':sg.number_of_edges(),'projected_reaction_edges':rg.number_of_edges(),
        'full_nontrivial_context_components':sum(r['graph_view']=='FULL_CANONICAL' for r in context_components),
        'author_nontrivial_context_components':sum(r['graph_view']=='AUTHOR_NONZERO' for r in context_components),
        'full_local_cyclic_regions_ge3':sum(r['graph_view']=='FULL_CANONICAL' for r in local_cycles),
        'author_local_cyclic_regions_ge3':sum(r['graph_view']=='AUTHOR_NONZERO' for r in local_cycles),
        'motifs':len(motifs),'motif_categories':dict(Counter(m['category'] for m in motifs))}
    inputs={p.relative_to(ROOT).as_posix():sha(p) for p in (MODEL,ARCHIVE,AUTHOR)}
    inputs['docs/reduction/reaction_level_annotation_v2.csv']=sha(ROOT/'docs/reduction/reaction_level_annotation_v2.csv')
    inputs['scripts/analyze_pnas2017_topology.py']=sha(Path(__file__))
    summary={'counts':counts,'full_serial_chains':full_chains,'author_serial_chains':author_chains,
        'context_excluded_species':sorted(set(species)&excluded),'hub_threshold':30,
        'status':'DESCRIPTIVE_TOPOLOGY_AUDIT_NOT_REDUCTION_VALIDATION','HUMAN_REVIEW_REQUIRED':True,
        'input_sha256':inputs,'author_csv_members':{im:ih,pm:ph},
        'software':{'python':platform.python_version(),'networkx':nx.__version__},
        'source_parent_commit':'775607bf9922c6878be0147bd7c64fa97e86a790'}
    write_json('summary.json',summary)
    # Small evidence graph navigates to full role-preserving CSVs, never replaces them.
    nodes=[{'id':p,'kind':'SOURCE','status':'EXTRACTED','sha256':h,'confidence':'BYTE_BOUND'} for p,h in inputs.items()]
    nodes += [{'id':m['motif_id'],'kind':'MOTIF','status':'INFERRED','confidence':m['confidence'],
        'source':'results/topology_audit/motif_catalog.csv','HUMAN_REVIEW_REQUIRED':True} for m in motifs]
    edges=[{'source':MODEL.relative_to(ROOT).as_posix(),'target':m['motif_id'],'relation':'SUPPORTS_TOPOLOGICAL_CANDIDATE'} for m in motifs]
    edges += [{'source':AUTHOR.relative_to(ROOT).as_posix(),'target':m['motif_id'],'relation':'BINDS_CONDITION_SPECIFIC_NONZERO_VIEW'} for m in motifs if m['graph_view']=='AUTHOR_NONZERO']
    write_json('knowledge_graph.json',{'status':'DERIVED_NAVIGATION_NOT_SOURCE_AUTHORITY','nodes':nodes,'edges':edges,
        'role_preserving_graphs':['bipartite_edges.csv','kinetic_dependency_edges.csv','projected_species_edges.csv','projected_reaction_edges.csv'],
        'freshness_rule':'Compare input SHA256 to manifest; regenerate on mismatch; source evidence takes priority.'})
    render_docs(summary,hubs,motifs,reduction_map,case,detailed)
    print(json.dumps(counts,indent=2))

def render_docs(summary,hubs,motifs,reduction_map,case,detailed):
    c=summary['counts']; h=summary['input_sha256']
    table='\n'.join(f'| {k} | {v} |' for k,v in c.items() if not isinstance(v,dict))
    doc('topology_first_audit.md',f'''# PNAS 2017 topology-first source audit

Status: **DESCRIPTIVE; HUMAN_REVIEW_REQUIRED**. No state, parameter, initial value, canonical SBML, prior evidence or decision table was changed. Audit parent: `{summary['source_parent_commit']}`.

Canonical source is `models/pnas2017_full_reference/original/fMGG_synthesis.xml`, SHA256 `{h[MODEL.relative_to(ROOT).as_posix()]}`. Subsystem ZIP supplies exact reaction signatures, not kinetics. Author simulator CSVs are a separately named parameter/initial-condition overlay. All inputs and archive member hashes are in [summary.json](../../results/topology_audit/summary.json).

| Audit quantity | Count |
| --- | ---: |
{table}

**Literal SBML default:** every initial concentration and local `k1` is 1. There are no zero initials, zero constants or structurally unreachable reactions. These placeholder values do not identify the published experiment. **Author-CSV overlay:** {c['author_positive_initial']} positive initial components, {c['author_zero_initial']} zero initial species, {c['author_zero_k']} identically zero-rate directions, {c['author_nonzero_k']} positive-rate directions. A zero initial rate is not permanent inactivity: {c['author_initial_zero_rate']} rates initially vanish, while only {c['author_nonzero_k_unreachable_reactions']} positive-k directions fail conservative reactant-AND reachability. No new numerical trajectory was run.

Activity proof uses multiplicative kinetic MathML and a monotone availability closure: all substrates and kinetic species must be potentially present. Zero-k inactivity is exact for that fixed parameter overlay. Unreachable positive-k reactions remain zero under the parsed mass-action ODE assumptions; reachable reactions are only potentially enabled. This graph closure is not a dynamical validation or an experimental finding.

The two author-positive but unreachable directions are `re0000000028` and `re0000000089`: release of EFTu_GDP from an inaccessible ribosome-bound precursor lacking the Gly-tRNA cargo. They remain in the source and audit, with an explicit condition-bound inactivity label. Tooling note: the author parameter CSV has 969 rows, including the compartment-size entry `default=1`; the audit checks that entry separately from the 968 kinetic constants. Bundled runtimes lacked the plotting/graph packages, so the existing Anaconda Python environment was used without installing or changing an environment.

All species have `boundaryCondition=false`, `constant=false`; dynamic means an ODE species, not independent dimension. Global parameters: 0; local parameters: 968; reversible SBML flags: 0. Opposite directed columns nevertheless give {c['exact_reverse_pairs']} exact reverse pairs. Constant stoichiometryMath is evaluated directly: `re0000000414` produces **2 PO4**, not the accessor default 1. Units, atomic formulas and charges remain insufficient for elemental/ionic claims.

Outputs: [species](../../results/topology_audit/species_table.csv), [reactions](../../results/topology_audit/reactions_table.csv), [parameters](../../results/topology_audit/parameters_table.csv), [net stoichiometric matrix](../../results/topology_audit/stoichiometric_matrix.csv). The signed matrix has 241 rows × 968 reaction columns; reactant/product roles remain separately available because net stoichiometry alone can cancel catalytic participants.
''')
    doc('topology_network_definition.md',f'''# Role-preserving network definition

Status: descriptive extracted graph + inferred motif labels; **HUMAN_REVIEW_REQUIRED** for all proposals.

1. **Bipartite graph:** species nodes `s:ID`; reaction nodes `r:ID`; substrate arcs species→reaction, product arcs reaction→species, with effective stoichiometric coefficients. {c['bipartite_nodes']} nodes and {c['bipartite_edges']} role arcs. Modifiers are in the reaction inventory; kinetic dependencies have a separate edge table and are never confused with material transfer.
2. **Species projection:** substrate→product for each reaction, retaining supporting reaction IDs. In/out degree means distinct predecessor/successor species, including possible self loops. An arc in a multi-reactant reaction does **not** mean one substrate alone can produce the product.
3. **Reaction projection:** reaction i→j when a product of i is a substrate of j, retaining all connecting species. It is navigation, not a runnable reaction system or stoichiometric path certificate.

All full graph edge tables are in `results/topology_audit`. No hubs or zero-rate directions are removed from these exports. A separate **context graph** suppresses free resource species, explicitly listed shared machinery, degree≥30 hubs, and degraded endpoints only to locate local structures; its exclusion list is in `summary.json`. Suppression is a visualization/analysis choice, never model deletion. Full and author-nonzero views are reported separately.

Species participation counts distinct reactions across substrates/products/modifiers. Producer/consumer counts count directed reaction IDs, not projected degree. A branch means more than one consuming reaction; a merge more than one producing reaction. Reverse return edges and disabled side exits count in the full graph and are distinguished by author-positive columns. Hubs are degree≥30 descriptive candidates, supplemented by explicit resource/machinery identities. Name-based biochemical classes are **INFERRED** and cannot replace complex-composition evidence.

Cycle membership uses strongly connected components (SCCs) of a directed projection and exact stoichiometric reverse pairs. SCCs imply possible directed walks, not independently feasible biochemical cycles, elementary flux modes or equilibrium. Full largest SCC={c['full_largest_species_scc']}; author-positive largest SCC={c['author_largest_species_scc']}. Local context SCC flags reduce currency leakage but still need chemistry checks. No exhaustive simple-cycle enumeration is claimed.

`local_cycle_regions.csv` explicitly lists all context SCC regions of at least three species: {c['full_local_cyclic_regions_ge3']} full and {c['author_local_cyclic_regions_ge3']} author-positive. Each retains actual reactions and source modules. They complement two-edge reverse pairs and are labeled UNSURE until the complete reactant requirements and catalytic resource ledger are checked.

A strict serial internal species must have exactly one producer and one consumer in the declared view, no external kinetic dependency and must not be an excluded hub/resource/sink. Maximal reaction components must be acyclic paths without reaction-level branching. This is deliberately stricter than visually finding a line. Full strict serial paths={c['full_strict_serial_chains']}; frozen-author paths={c['author_strict_serial_chains']}. Paths are candidates for aggregate-state modeling, not proofs of exact state lumpability.

Subnetwork membership comes from exact substrate/product signatures in 26 source files (memberships overlap). Interface species participate in at least one reaction outside that file's mapped reaction set. Full and nonhub interface counts/fractions are reported in `source_subnetworks.csv`. Independently, `context_components.csv` reports connected reaction components after the explicitly declared hub suppression ({c['full_nontrivial_context_components']} nontrivial full / {c['author_nontrivial_context_components']} author-positive components). Both views restore all full-network interface species to each component table. Source modules are open and no autonomous/weak-dynamical-coupling claim follows. Context articulation points and cross-module species are distinct bridge diagnostics. EnergyRegeneration A–D and formylation have zero nonhub source interfaces under this suppression, making them comparatively localized open modules; their free-resource interfaces still couple them dynamically.

Reproduce with Python 3.11+ and networkx 3.2+: `python scripts/analyze_pnas2017_topology.py`. Locally used Python {summary['software']['python']}, networkx {summary['software']['networkx']}. Refresh when any source/script hash differs; [knowledge graph](../../results/topology_audit/knowledge_graph.json) is subordinate navigation with EXTRACTED/INFERRED status. Scientific acceptance remains pending.
''')
    serials=[m for m in motifs if m['motif_type']=='SERIAL_CHAIN']
    serial_list='\n'.join(f"- `{m['motif_id']}`: {', '.join(json.loads(m['member_reactions_json']))}; internal: {', '.join(json.loads(m['member_species_json']))}." for m in serials)
    doc('motif_catalog.md',f'''# Topology-first motif catalog

All categories are **candidate proposals; HUMAN_REVIEW_REQUIRED=true**. The machine-readable [catalog](../../results/topology_audit/motif_catalog.csv) contains {c['motifs']} motifs with complete member IDs, view, evidence and required assumptions. Membership is intentionally overlapping.

| Motif type | Structural evidence | Candidate interpretation |
| --- | --- | --- |
| Strict serial chains | One producer + one consumer for each internal state; no external kinetic dependence; acyclic reaction path | AGGREGATE_STATE_CANDIDATE; direct closure requires additional delay/occupancy/ledger evidence |
| Two Gly-addition backbones | Ordered source-supported elongation reactions; repeated factor and bound-nucleotide pattern | AGGREGATE_STATE_CANDIDATE, including return loops; not an unbranched line |
| {c['exact_reverse_pairs']} exact reverse pairs | Exact stoichiometric swap | Signed net-flux rewrite is exact with no state removal; {c['both_author_positive_reverse_pairs']} pairs with both author directions positive are only local kinetic/QSSA review candidates |
| Hub-attached motifs | Explicit degree and module membership | KEEP_EXPLICIT resources/machinery unless a validated coordinate reconstruction exists |
| 26 source subnetworks | Exact source signatures + measured external interfaces | Open local submodules; no independent-module claim |

## Detected strict serial paths

{serial_list or 'None detected in either view.'}

First prototype is `re0000000016→re0000000017→re0000000018`. Its two internal states have no author-positive side exits, but the full canonical graph retains multiple side reactions. This supports a **condition-bound candidate**, not source-general deletion. The counterpart `re0000000077→re0000000078→re0000000079` occurs in the second Gly addition.

The actual fMGG network has **two** growth cycles. A long `A→X1→...→B` polymer lattice is an explanatory schematic, not a claim about this file. Each whole elongation backbone also has docking/dissociation/nucleotide return loops; these are reasons to retain occupancy and resource/progress information.

`DIRECT_LUMP_CANDIDATE` appears only as an explicitly derived, unvalidated case-study option, never as a topology-only automatic deletion rule. Topology alone establishes no exact memoryless A→B kinetics. The case study documents its delay and ledger losses. The exact reverse-channel net rewrite is a different operation that preserves all states. No category is copied into `reduction_decisions.csv`.
''')
    map_table='\n'.join(f"| {r['region']} | {r['route']} | {r['nonhub_interface_count']} |" for r in reduction_map)
    doc('global_reduction_map.md',f'''# Whole-network proposed reduction order

**HUMAN_REVIEW_REQUIRED; every route is PENDING.** This additive map does not supersede prior acceptance records or authorize elimination.

| Source region | Proposed route | Nonhub interface species |
| --- | --- | ---: |
{map_table}

`TOPOLOGY_REDUCE_FIRST`: prototype the two elongation serial subchains and test occupancy/ledger closure. `QSSA_AFTER_TOPOLOGY`: reconsider aaRS/formylation and energy enzyme blocks on the chosen retained coordinates, reusing exact conservation and observable contracts. `QSSA_ONLY`: local aminoacyl-tRNA/factor carrier assembly where no serial-growth simplification was detected. `KEEP_EXPLICIT`: shared resources, factor states with cross-module competition, terminal product and recycling outputs. `DO_NOT_TOUCH_YET`: initiation assembly with unresolved interface/closure choice. These are sequencing proposals, not conclusions that a category will succeed.

The source module counts overlap; do not sum them as disjoint partition sizes. [CSV map](../../results/topology_audit/reduction_map.csv) records exact reactions/species; [interface table](../../results/topology_audit/module_interfaces.csv) records actual coupling. A module label alone never justifies one lumped state. Retain free ATP/GTP/ADP/GDP, amino-acid/aa-tRNA pools, PO4/PPi, ribosome availability and factor coupling in the accounting contract.
''')
    top='; '.join(f"{r['species_id']} ({r['reactions_participated']} reactions)" for r in hubs[:8])
    doc('topology_first_summary.md',f'''# Topology first, QSSA second — PNAS 2017

**结果：已完成拓扑审计与候选推导，没有删除状态，没有改变标准模型；所有方案均为 HUMAN_REVIEW_REQUIRED。**

1. **哪些结构可先于 QSSA 处理？** 968 条有向反应中有 {c['exact_reverse_pairs']} 对精确反向通道，可先改写为保留全部状态的净通量表示。真正的状态合并仍需动力学闭合：完整源图检测到 {c['full_strict_serial_chains']} 条严格串联路径；固定作者参数后检测到 {c['author_strict_serial_chains']} 条。优先对延伸的三步段提出 E 聚合态，直接 A→B 只作为需验证的近似选项。
2. **哪些枢纽应显式保留？** ATP/GTP/ADP/GDP、PO4/PPi、aa-tRNA/tRNA、核糖体与跨模块共享翻译因子。完整图最高参与量示例：{top}。高度数是共享竞争提示，不能作为删状态依据。26 个源子网络均按开放模块记录接口，不宣称彼此独立。
3. **第一原型是什么？** `re0000000016→17→18`（完整 ID 见案例）：S0→S1+PO4→S2+EFTu_GDP→S3；合计 S0→S3+PO4+EFTu_GDP。E_mid=S1+S2 保留内部核糖体占据总量，但单一 E 不能精确区分两阶段的因子占据与释放账本。完整图旁支全部列出；它们在固定作者参数中关闭。
4. **如何调整顺序？** 标准 SBML → 有角色的拓扑图 → 串联/分支/循环/枢纽/接口识别 → 候选聚合与占据/资源闭合 → 局部 QSSA → 分项验证。既有 QSSA、守恒与失败证据保留，暂停新的全局快变量搜索。参见 [QSSA repositioning](qssa_repositioning_note.md)。
5. **人下一步检查什么？** 审阅这条三步段的边界、关闭旁支的条件适用性、是否选择 E_mid 或显式链，以及 ATP/GTP、Gly/aa-tRNA、PO4/PPi、因子/核糖体占据和产物的观测合同。先决定哪些阶段库存/累计账本必须重构，再授权一个有限条件集的比较；本次未启动新的 ODE 验证。

**源文件与实际预期的差异：** 标准 SBML 所有初值/常数均为 1；作者 CSV 才给出 27 个初始存在组分、485 个零速率方向。默认图与作者图不可混称。真实模型只有 fMGG 的两次 Gly 加入，产物为 Pept0003，不能把示意长链或更长蛋白的行为当成已验证事实。

**相对独立性：** 按明示规则暂时屏蔽共享枢纽后，作者非零反应图形成 10 个非平凡连接区域。起始、延伸、终止仍属于一个 305 反应的连接区域；GlyRS/MetRS 各形成 42 反应的局部区域；能量再生 A–D 及 formylation 较局部化。共享资源恢复后仍相互耦合，这不是动态独立性的证明。具体成员和完整接口见 `context_components.csv`。

**尚未解决：** 拓扑不证明精确可聚合性；延伸整轮有返向循环；聚合态的阶段分布、延迟及微观 gross flux 不可由总量直接恢复；源文件单位及复合物原子/电荷信息不足；弱连接不证明弱动态耦合。旧 QSSA 的失败/未完成状态不会因为拓扑候选而升级。

## 组会图

“Repeated chain growth can sometimes be lumped into an effective step or an aggregate state.” 这里的 sometimes 由旁支、占据、资源账本、延迟及动力学闭合共同限定。

- [Figure 1 — module map](../../results/figures/topology_first_network_map.png)
- [Figure 2 — chain options](../../results/figures/topology_first_chain_schematic.png)
- [Figure 3 — workflow](../../results/figures/topology_first_workflow.png)
- [Figure 4 — real motif](../../results/figures/topology_first_case_study.png)
- [Figure 5 — real branch, return cycle and interfaces](../../results/figures/topology_first_branch_cycle_interfaces.png)

图的 SVG/PDF 与可重现脚本一并提供。运行分析、五个绘图脚本，再运行 `scripts/verify_pnas2017_topology.py`。验证针对源哈希、图表和代数一致性，**不是 reduced-model scientific validation**。
''')

if __name__=='__main__': main()
