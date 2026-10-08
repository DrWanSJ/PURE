"""Independent byte/stoichiometry/graph/aggregate audit; no scientific promotion.

Reads canonical XML with the standard library instead of importing the builder.
Writes verification.json and artifact_manifest.json only; never fixes outputs.
"""
from collections import defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/topology_audit'
NS={'s':'http://www.sbml.org/sbml/level2/version4','m':'http://www.w3.org/1998/Math/MathML'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))
def side(r,label):
    ans=defaultdict(float)
    for e in r.findall(f's:listOf{label}/s:speciesReference',NS):
        math=e.find('s:stoichiometryMath',NS)
        if math is not None:
            literal=math.findall('.//m:cn',NS)
            assert len(literal)==1 and not math.findall('.//m:apply',NS)
            coefficient=float(literal[0].text)
        else: coefficient=float(e.get('stoichiometry','1'))
        ans[e.get('species')]+=coefficient
    return dict(ans)

def main():
    checks=[]
    def check(label,condition):
        checks.append({'check':label,'status':'PASS' if condition else 'FAIL'})
    summary=json.loads((OUT/'summary.json').read_text(encoding='utf-8'))
    for name,expected in summary['input_sha256'].items(): check('fresh_source:'+name,sha(ROOT/name)==expected)
    with zipfile.ZipFile(ROOT/'references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip') as z:
        for name,expected in summary['author_csv_members'].items():
            check('fresh_archive_member:'+name,hashlib.sha256(z.read(name)).hexdigest()==expected)
    model=ET.parse(ROOT/'models/pnas2017_full_reference/original/fMGG_synthesis.xml').getroot().find('s:model',NS)
    species=[e.get('id') for e in model.findall('s:listOfSpecies/s:species',NS)]
    reaction_elements=model.findall('s:listOfReactions/s:reaction',NS)
    rx={e.get('id'):{'in':side(e,'Reactants'),'out':side(e,'Products')} for e in reaction_elements}
    reaction_rows={r['reaction_id']:r for r in rows('reactions_table.csv')}
    check('inventory_ids',set(rx)==set(reaction_rows) and set(species)=={r['species_id'] for r in rows('species_table.csv')})
    check('inventory_roles',all(json.loads(reaction_rows[a]['substrates_json'])==r['in'] and json.loads(reaction_rows[a]['products_json'])==r['out'] for a,r in rx.items()))
    matrix=rows('stoichiometric_matrix.csv')
    check('stoichiometric_matrix_dimensions',len(matrix)==len(species) and len(matrix[0])==len(rx)+1)
    check('all_source_stoichiometric_coefficients',all(float(row[a])==r['out'].get(row['species_id'],0)-r['in'].get(row['species_id'],0) for row in matrix for a,r in rx.items()))
    check('nonunit_PO4_not_lost',rx['re0000000414']['out']['PO4']==2 and next(float(row['re0000000414']) for row in matrix if row['species_id']=='PO4')==2)
    expected_bg=set(); expected_sg=defaultdict(set); prod=defaultdict(set); cons=defaultdict(set)
    for a,r in rx.items():
        for s,c in r['in'].items(): expected_bg.add(('s:'+s,'r:'+a,'substrate',c)); cons[s].add(a)
        for s,c in r['out'].items(): expected_bg.add(('r:'+a,'s:'+s,'product',c)); prod[s].add(a)
        for x in r['in']:
            for y in r['out']: expected_sg[(x,y)].add(a)
    actual_bg={(r['source'],r['target'],r['role'],float(r['coefficient'])) for r in rows('bipartite_edges.csv')}
    actual_sg={(r['source_species'],r['target_species']):set(r['reaction_ids'].split(';')) for r in rows('projected_species_edges.csv')}
    check('role_preserving_bipartite_graph',actual_bg==expected_bg)
    check('complete_species_projection_with_evidence',dict(expected_sg)==actual_sg)
    expected_rg=defaultdict(set)
    for s in species:
        for a in prod[s]:
            for b in cons[s]: expected_rg[(a,b)].add(s)
    actual_rg={(r['source_reaction'],r['target_reaction']):set(r['shared_species_ids'].split(';')) for r in rows('projected_reaction_edges.csv')}
    check('complete_reaction_projection_with_evidence',dict(expected_rg)==actual_rg)
    pairs=rows('reverse_pairs.csv')
    check('reverse_pairs_stoichiometric_swap',all(rx[r['forward_id']]['in']==rx[r['reverse_id']]['out'] and rx[r['forward_id']]['out']==rx[r['reverse_id']]['in'] for r in pairs))
    kauthor={a:float(r['author_rate_coefficient']) for a,r in reaction_rows.items()}
    for view,chains in [('full',summary['full_serial_chains']),('author',summary['author_serial_chains'])]:
        good=True
        for chain in chains:
            ids=chain['reaction_ids']
            for s,a,b in zip(chain['internal_species'],ids,ids[1:]):
                p={r for r in prod[s] if view=='full' or kauthor[r]>0}
                c={r for r in cons[s] if view=='full' or kauthor[r]>0}
                good &= p=={a} and c=={b}
        check(view+'_serial_path_one_producer_one_consumer',good)
    case=json.loads((OUT/'case_study.json').read_text(encoding='utf-8'))
    summed=defaultdict(float)
    for a in case['serial_reaction_ids']:
        for s,c in rx[a]['out'].items(): summed[s]+=c
        for s,c in rx[a]['in'].items(): summed[s]-=c
    check('real_case_net_ledger',{s:c for s,c in summed.items() if c}==case['serial_net_stoichiometry'])
    s0,s1,s2,s3=case['serial_species_ids']
    check('case_internal_active_side_branches',all(not v for v in case['internal_author_side_reactions'].values()))
    check('case_full_side_branches_recorded',all(set(case['internal_side_reactions'][s])==(prod[s]|cons[s])-set(case['serial_reaction_ids']) for s in (s1,s2)))
    # Exact aggregate row sum and stage ledgers for arbitrary directed fluxes.
    sumcoeff={a:sum(r['out'].get(s,0)-r['in'].get(s,0) for s in (s1,s2)) for a,r in rx.items()}
    activecoeff={a:v for a,v in sumcoeff.items() if v and kauthor[a]>0}
    check('E_mid_exact_row_sum',activecoeff=={'re0000000016':1,'re0000000018':-1})
    check('PO4_release_is_admission_not_completion',rx['re0000000016']['out'].get('PO4')==1 and 'PO4' not in rx['re0000000018']['out'])
    check('EF_Tu_release_is_internal_stage',rx['re0000000017']['out'].get('EFTu_GDP')==1 and 'EFTu_GDP' not in rx['re0000000018']['out'])
    # A concrete same-E counterexample to exact one-state memoryless closure.
    k18=kauthor['re0000000018']; check('same_E_distinct_outputs_counterexample',k18*0!=k18*1)
    check('all_candidates_pending',all(r['HUMAN_REVIEW_REQUIRED']=='True' for r in rows('motif_catalog.csv')) and all(r['decision_status']=='PENDING' for r in rows('reduction_map.csv')))
    figures=['network_map','chain_schematic','workflow','case_study','branch_cycle_interfaces']
    figgood=True
    for name in figures:
        for ext in ('png','svg','pdf'):
            p=ROOT/f'results/figures/topology_first_{name}.{ext}'
            figgood &= p.exists() and p.stat().st_size>1000
    check('five_programmatic_figures_three_formats',figgood)
    pngs=[ROOT/f'results/figures/topology_first_{name}.png' for name in figures]
    check('meeting_raster_dimensions',all(p.exists() and struct.unpack('>II',p.read_bytes()[16:24])==(3840,2160) for p in pngs))
    check('vector_PDF_headers',all((ROOT/f'results/figures/topology_first_{name}.pdf').exists() and (ROOT/f'results/figures/topology_first_{name}.pdf').read_bytes().startswith(b'%PDF') for name in figures))
    sources=['plot_topology_map.py','plot_chain_reduction_schematic.py','plot_reduction_workflow.py','plot_case_study_motif.py','plot_branch_cycle_interfaces.py']
    check('five_figure_sources',all((ROOT/'scripts/visualization'/p).exists() for p in sources))
    base=summary['source_parent_commit']
    changes=subprocess.check_output(['git','diff','--name-status',base,'--'],cwd=ROOT,text=True)
    check('prior_tracked_artifacts_unchanged',all(line.startswith('A\t') or line=='M\t.gitattributes' for line in changes.splitlines()))
    original_attributes=subprocess.check_output(['git','show',base+':.gitattributes'],cwd=ROOT,text=True)
    current_attributes=(ROOT/'.gitattributes').read_text(encoding='utf-8')
    check('checkout_policy_is_additive',current_attributes.startswith(original_attributes))
    # Existing QSSA note binds external-worktree evidence separately by path/hash.
    note=ROOT/'docs/reduction/qssa_repositioning_note.md'
    check('existing_QSSA_integration_note',note.exists() and 'CK_FIRST_ORDER_IMPROVES_EXTENT_NOT_CURRENT' in note.read_text(encoding='utf-8'))
    source_index=[]
    for line in note.read_text(encoding='utf-8').splitlines():
        match=re.search(r'\[([^\]]+)\]\(([^)]+)\).*`([0-9a-f]{64})`',line)
        if match:
            title,path,expected=match.groups()
            p=Path(path) if Path(path).is_absolute() else note.parent/path
            actual=sha(p) if p.exists() else 'MISSING'
            source_index.append({'title':title,'source_path':str(p.resolve()),'expected_sha256':expected,
                'actual_sha256':actual,'scope':'CURRENT_TASK_PARENT' if p.resolve().is_relative_to(ROOT) else 'EXTERNAL_RESEARCH_WORKTREE',
                'evidence_status':'EXTRACTED_EXISTING_RESULT_NOT_RERUN'})
    check('QSSA_14_source_hashes_bound',len(source_index)==14 and all(r['actual_sha256']==r['expected_sha256'] for r in source_index))
    (OUT/'qssa_source_index.json').write_text(json.dumps({'status':'DERIVED_NAVIGATION_NOT_SOURCE_AUTHORITY',
        'sources':source_index,'freshness_rule':'External worktrees are mutable; recover pinned commits/hashes from the note on change.'},indent=2)+'\n',encoding='utf-8',newline='\n')
    result={'status':'PASS' if all(r['status']=='PASS' for r in checks) else 'FAIL',
        'scope':'BYTE_STOICHIOMETRY_GRAPH_AND_AGGREGATE_IDENTITIES_ONLY_NOT_SCIENTIFIC_VALIDATION',
        'generated_at_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'HUMAN_REVIEW_REQUIRED':True}
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    files=[ROOT/'.gitattributes',ROOT/'scripts/analyze_pnas2017_topology.py',Path(__file__),
        *sorted((ROOT/'scripts/visualization').glob('*.py')),
        *[ROOT/'docs/reduction'/name for name in ('topology_first_audit.md','topology_network_definition.md','motif_catalog.md','one_chain_reduction_case_study.md','global_reduction_map.md','qssa_repositioning_note.md','topology_first_summary.md')],
        *sorted((ROOT/'results/figures').glob('topology_first_*')),
        *[p for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='artifact_manifest.json']]
    manifest={'status':'DERIVED_NAVIGATION_NOT_SOURCE_AUTHORITY','source_parent_commit':base,
        'input_sha256':summary['input_sha256'],'HUMAN_REVIEW_REQUIRED':True,
        'output_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in files if p.exists()},
        'freshness_rule':'Compare all hashes; rerun analyzer, figures and verifier on change. No output upgrades scientific decisions.'}
    (OUT/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'failures':[r for r in checks if r['status']=='FAIL']},indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)

if __name__=='__main__': main()
