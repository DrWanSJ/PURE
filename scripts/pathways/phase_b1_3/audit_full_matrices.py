"""Independent explicit 241x968 rational matrices and full occurrence-vector audit."""
import sys,json,argparse
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/reduction/pathways'
sys.path.insert(0,str(ROOT/'scripts/pathways/phase_b0'))
import verify_phase_b0_witnesses as independent
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_bytes((json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode())
def exact(v):return {s:str(n) for s,n in sorted(v.items()) if n}
def main():
    p=argparse.ArgumentParser();p.add_argument('--input-dir',type=Path,default=OUT);p.add_argument('--output-dir',type=Path,default=OUT);args=p.parse_args()
    src=independent.parse_sources();counts=independent.check_source_integrity(src);species=sorted(src['species']);ids=sorted(src['reactions']);index={s:i for i,s in enumerate(species)}
    minus=[];plus=[];net=[]
    for j,r in enumerate(ids):
        q=src['reactions'][r]
        for s,n in sorted(q['reactants'].items()):minus.append([index[s],j,str(n)])
        for s,n in sorted(q['products'].items()):plus.append([index[s],j,str(n)])
        for s in sorted(set(q['reactants'])|set(q['products'])):
            n=q['products'].get(s,F())-q['reactants'].get(s,F())
            if n:net.append([index[s],j,str(n)])
    matrix={'shape':[241,968],'species_row_order':species,'original_reaction_column_order':ids,'S_minus_sparse_row_col_exact':minus,'S_plus_sparse_row_col_exact':plus,'S_full_sparse_row_col_exact':net,'raw_arc_entries':len(minus)+len(plus),'arc_coefficient_sum':str(sum((F(n) for _,_,n in minus+plus),F())),'coefficient_authority':'LITERAL_CONSTANT_MATHML_WITH_EXACT_RATIONAL_FALLBACK','source_hashes':counts['hashes'],'evidence_status':'EXTRACTED','molecular_composition_certificate':False}
    save(args.output_dir/'phase_b1_3_source_matrices.json',matrix)
    results=[];data=load(args.input_dir/'phase_b1_3_witnesses.json')
    for w in data['witnesses']:
        vector=[F(w['occurrence_vector'].get(r,0)) for r in ids];rhs=[F() for _ in species]
        for i,j,n in net:rhs[i]+=F(n)*vector[j]
        lhs=[F(w['final_marking'].get(s,'0'))-F(w['initial_marking'].get(s,'0')) for s in species]
        equal=lhs==rhs
        occurrence_match=w['occurrence_vector']==dict(sorted(Counter(e['reaction_id'] for e in w['reaction_occurrences']).items()))
        marking=[F(w['initial_marking'].get(s,'0')) for s in species];per_event=[]
        for e in w['reaction_occurrences']:
            j=ids.index(e['reaction_id']);react=[(i,F(n)) for i,k,n in minus if k==j];prod=[(i,F(n)) for i,k,n in plus if k==j]
            enabled=all(marking[i]>=n for i,n in react)
            for i,n in react:marking[i]-=n
            for i,n in prod:marking[i]+=n
            per_event.append({'event_id':e['event_id'],'column_index':j,'petri_enabled':enabled,'nonnegative_after':all(n>=0 for n in marking)})
        status='PASS' if equal and occurrence_match and all(x['petri_enabled'] and x['nonnegative_after'] for x in per_event) and marking==[F(w['final_marking'].get(s,'0')) for s in species] else 'FAIL'
        results.append({'witness_id':w['witness_id'],'status':status,'full_occurrence_vector':list(map(str,vector)),'m_final_minus_m_initial':exact(dict(zip(species,lhs))),'S_full_times_w':exact(dict(zip(species,rhs))),'exact_equality':equal,'occurrence_history_matches':occurrence_match,'per_event_matrix_execution':per_event})
    report={'status':'PASS' if all(w['status']=='PASS' for w in results) else 'FAIL','matrix_shape':[241,968],'raw_arc_entries':matrix['raw_arc_entries'],'arc_coefficient_sum':matrix['arc_coefficient_sum'],'witnesses_checked':len(results),'independent_of_B1_3_builder':True,'witnesses':results,'arc_count_semantics':'3854 species-reference edges carrying exact weights; sum of edge coefficients is 3855 because PO4 coefficient 2 in re0000000414.'}
    save(args.output_dir/'phase_b1_3_matrix_verification.json',report);print(json.dumps({k:report[k] for k in ['status','matrix_shape','raw_arc_entries','arc_coefficient_sum','witnesses_checked']}));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
