"""Exact rational coordinate and projection proofs; no ODE integration."""
import sys,json,csv,math,re
from fractions import Fraction as F
from collections import defaultdict
import numpy as np
import sympy as sp
from common import *
TAIL=['RS50S_tRNAGlyGCC_RRF_EFG_GDP','RS50S_tRNAGlyGCC_RRF','RS50S_tRNAGlyGCC_EFG_GDP','RS50S_RRF_EFG_GDP','RS50S_tRNAGlyGCC','RS50S_RRF','RS50S_EFG_GDP']
TAIL_NAMES=['RECYCLE_N3','RECYCLE_N2','RECYCLE_BOUND_tRNA','RECYCLE_BOUND_RRF','RECYCLE_BOUND_EFG']
CHAIN=[{'round':1,'slow':'elRS70SAGGU0002_fMet_EFTu_GDP_GlytRNAGlyGCC','fast':'elRS70SAGGU0002_fMet_GlytRNAGlyGCC','ids':['re0000000017','re0000000018'],'k':'7000/1007'},
       {'round':2,'slow':'elRS70SAGGU0003_Pept0002_EFTu_GDP_GlytRNAGlyGCC','fast':'elRS70SAGGU0003_Pept0002_GlytRNAGlyGCC','ids':['re0000000078','re0000000079'],'k':'7000/1007'}]
def modular_rank(A,prime=1000003):
    a=np.asarray(A,dtype=np.int64).copy()%prime;row=0
    for j in range(a.shape[1]):
        piv=np.flatnonzero(a[row:,j])
        if not len(piv):continue
        k=row+int(piv[0]);a[[row,k]]=a[[k,row]]
        a[row]=(a[row]*pow(int(a[row,j]),prime-2,prime))%prime
        indices=np.flatnonzero(a[:,j]);indices=indices[indices!=row]
        a[indices]=(a[indices]-a[indices,j,None]*a[row])%prime
        row+=1
        if row==a.shape[0]:break
    return row
def rational_matrix(values):return sp.Matrix([[sp.Rational(str(n)) for n in row] for row in values])
def exact_sparse(mat):return [{str(j):str(mat[i,j]) for j in range(mat.cols) if mat[i,j]} for i in range(mat.rows)]
def laws_data(names,scope=None):
    rr=rows(LEGACY/'conservation_laws_v0.csv')
    if scope:rr=[r for r in rr if r['scope']==scope]
    return rr,rational_matrix([[json.loads(r['species_coefficients_json']).get(n,0) for n in names] for r in rr])
def matrix_source(names,rx):
    ind={s:i for i,s in enumerate(names)};entries={}
    for j,r in enumerate(rx):
        for side,sign in [('reactants',-1),('products',1)]:
            for s,n in r[side].items():entries[ind[s],j]=entries.get((ind[s],j),0)+sign*sp.Rational(str(n))
    return sp.SparseMatrix(len(names),len(rx),{k:v for k,v in entries.items() if v})
def support_proof(names,rx,initial):
    support={s for s,n in initial.items() if n>0};iterations=[]
    while True:
        enabled=[r for r in rx if r['k']>0 and (set(r['reactants'])|(set(r['factors'])-{'k1'}))<=support]
        new={s for r in enabled for s in r['products']}-support
        if not new:break
        iterations.append({'new_species':sorted(new),'source_direction_ids':[r['id'] for r in enabled if new&set(r['products'])]});support|=new
    zero=sorted(set(names)-support);proof={}
    for s in zero:
        producers=[]
        for r in rx:
            if s not in r['products']:continue
            missing=sorted((set(r['reactants'])|(set(r['factors'])-{'k1'}))-support)
            assert r['k']==0 or missing,(s,r['id'])
            producers.append({'reaction_id':r['id'],'exact_k':str(r['k']),'zero_parameter':r['k']==0,'missing_support_dependencies':missing})
        proof[s]={'initial':'0','all_original_producers':producers,'invariance':'Each production monomial is identically zero on the declared nonnegative support face.'}
    return support,{'initial_positive':sum(n>0 for n in initial.values()),'closure_count':len(support),'zero_species':zero,'iterations':iterations,'zero_proof':proof,'scope':'AUTHOR_CONDITION_EXACT','external_input_rules_events_modifiers':'ABSENT_AS_CHECKED_BY_CANONICAL_PARSER_AND_RAW_XML'}
def affine_chart(labels,N,L,x0,priority=None):
    # Independent rows of inherited laws, restricted to the new physical coordinates.
    row_indices=list(L.T.rref()[1]);L=L[row_indices,:]
    order=sorted(range(len(labels)),key=lambda i:(0 if x0[i]>0 else 1,-float(x0[i]),i)) if priority is None else priority
    columns=list(L[:,order].rref()[1]);e=[order[j] for j in columns];ret=[i for i in range(len(labels)) if i not in set(e)]
    assert len(e)==L.rows and L[:,e].det()!=0
    B=-L[:,e].inv()*L[:,ret];H=sp.zeros(len(labels),len(ret))
    for j,i in enumerate(ret):H[i,j]=1
    for i,row in enumerate(e):
        for j in range(len(ret)):H[row,j]=B[i,j]
    assert L*H==sp.zeros(L.rows,len(ret))
    assert N[e,:]==B*N[ret,:]
    assert L*N==sp.zeros(L.rows,N.cols)
    return {'physical_labels':labels,'retained_indices':ret,'eliminated_indices':e,'dimension':len(ret),'physical_dimension':len(labels),'law_rank':L.rows,'L_sparse_rows':exact_sparse(L),'lift_sparse_rows':exact_sparse(H),'B_sparse_rows':exact_sparse(B),'initial_physical':[str(n) for n in x0],'physical_feasibility':'y_i>=0 and y_E0+B*(z-z0)>=0; aggregate tail additionally requires a feasible nonnegative source representative.'},H,L
def physical_projection(names,support,chain_rounds=(),tail=False):
    index={s:i for i,s in enumerate(names)};remove={CHAIN[j-1]['fast'] for j in chain_rounds}|(set(TAIL) if tail else set());labels=[s for s in names if s in support and s not in remove]
    P=sp.zeros(len(labels)+(5 if tail else 0),len(names));H=sp.zeros(len(names),P.rows)
    for j,s in enumerate(labels):P[j,index[s]]=1;H[index[s],j]=1
    for j in chain_rounds:
        c=CHAIN[j-1];slow=labels.index(c['slow']);P[slow,index[c['fast']]]=1
        P[labels.index('EFTu_GDP'),index[c['fast']]]-=1
        labels[slow]='LUMP_'+c['slow']
    tail_block=None
    if tail:
        offset=len(labels);labels+=TAIL_NAMES
        block=sp.Matrix([[1,0,0,0,0,0,0],[0,1,1,1,0,0,0],[1,1,1,0,1,0,0],[1,1,0,1,0,1,0],[1,0,1,1,0,0,1]])
        right=block.T*(block*block.T).inv();assert block*right==sp.eye(5)
        for i in range(5):
            for j,s in enumerate(TAIL):P[offset+i,index[s]]=block[i,j]
        for j,s in enumerate(TAIL):
            for i in range(5):H[index[s],offset+i]=right[j,i]
        tail_block={'source_species':TAIL,'source_projection_rows':[[str(x) for x in block.row(i)] for i in range(5)],'physical_offset':offset,'right_inverse_rows':[[str(x) for x in right.row(i)] for i in range(7)],'discarded_micro_correlation_dimension':2,'actual_microstate_reconstruction':'NOT_UNIQUE; NONNEGATIVE_REPRESENTATIVE_ONLY'}
    assert P*H==sp.eye(P.rows)
    return labels,P,H,tail_block
def main():
    protection();names,rx,initial=source_network();S=matrix_source(names,rx);active=[j for j,r in enumerate(rx) if r['k']>0]
    lawrows,Lgeneral=laws_data(names,'SOURCE_GENERAL');assert Lgeneral.rows==27 and Lgeneral.rank()==27 and Lgeneral*S==sp.zeros(27,968)
    assert modular_rank(np.array(S.tolist(),dtype=int))==214
    old=load(LEGACY/'source_coordinate_certificate_v4.json')
    assert sha(LEGACY/'source_coordinate_certificate_v4.json')=='0162c0fcdecd1fd4017180eccacdfc33b2c34141cf3df7d4b2118ed7c6c05b06'
    from verify_source_coordinate_certificate_v1 import check_certificate
    check_certificate(old,names,columns(names,rx),initial,{r['conservation_id']:r for r in rows(LEGACY/'conservation_laws_v0.csv')})
    support,proof=support_proof(names,rx,initial);live=[j for j in active if (set(rx[j]['factors'])-{'k1'})<=support]
    all_lawrows,Lall=laws_data(names);assert Lall*S[:,active]==sp.zeros(Lall.rows,len(active))
    assert Lall.rank()==64 and modular_rank(np.array(S[:,active].tolist(),dtype=int))==177
    x0=sp.Matrix([sp.Rational(str(initial[s])) for s in names]);charts={};projection_proofs={}
    # R1 uses the exact historically accepted chart verbatim, with constants rebased per case.
    ret=[names.index(s) for s in old['retained_species']];elim=[names.index(s) for s in old['eliminated_species']];H1=sp.zeros(241,214)
    for j,i in enumerate(ret):H1[i,j]=1
    for i,row in enumerate(old['B_sparse_rows']):
        for s,n in row.items():H1[elim[i],ret.index(names.index(s))]=sp.Rational(n)
    assert H1*S[ret,:]==S
    charts['R1']={'physical_labels':names,'retained_indices':ret,'eliminated_indices':elim,'dimension':214,'physical_dimension':241,'law_rank':27,'lift_sparse_rows':exact_sparse(H1),'L_sparse_rows':exact_sparse(Lgeneral),'initial_physical':[str(x) for x in x0],'source_scope':'SOURCE_GENERAL_EXACT','original_certificate_sha256':sha(LEGACY/'source_coordinate_certificate_v4.json')}
    specs=[('R2',(),False),('R3_CHAIN1',(1,),False),('R3_CHAIN12',(1,2),False),('R3_RECYCLE',(),True),('R3_CHAIN12_RECYCLE',(1,2),True)]
    for name,chain,tail in specs:
        labels,P,H,tailblock=physical_projection(names,support,chain,tail)
        Lphys=Lall*H
        reachable=[names.index(s) for s in names if s in support]
        assert (Lphys*P-Lall)[:,reachable]==sp.zeros(Lall.rows,len(reachable))
        # Modified columns are source-event sums, never invented chemistry.
        effective=S[:,live].copy()
        for k in chain:
            a,b=[next(j for j,r in enumerate(rx) if r['id']==rid) for rid in CHAIN[k-1]['ids']]
            assert set(rx[a]['reactants'])=={CHAIN[k-1]['slow']} and set(rx[b]['reactants'])=={CHAIN[k-1]['fast']}
        N=P*effective
        chart,Hchart,Lused=affine_chart(labels,N,Lphys,P*x0)
        assert modular_rank(np.array(N.tolist(),dtype=int))==chart['dimension']
        chart.update({'source_projection_sparse_rows':exact_sparse(P),'source_lift_sparse_rows':exact_sparse(H),'live_reaction_indices':live,'chain_rounds':list(chain),'tail':tailblock,'scope':'AUTHOR_CONDITION_EXACT' if not chain else 'CONDITIONAL_APPROXIMATE_CHAIN','independent_dimension':chart['dimension'],'reaction_mapping':'Original source directions retained, combined chain pair uses identical effective rate for both source-event columns.'})
        # N includes each original chain column; the lumped physical 17 column is zero
        # and 18 has the net column. This does not add an extra conservation law.
        charts[name]=chart
        if tail:
            tail_index=[names.index(s) for s in TAIL];tail_ids=[j for j in live if set(rx[j]['factors'])-{'k1'}<=set(TAIL)]
            assert len(tail_ids)==12
            # Every external active rate is independent of the deleted microstates.
            assert all(not (set(rx[j]['factors'])&set(TAIL)) for j in live if j not in tail_ids)
            D=sp.zeros(len(tail_ids),7)
            for i,j in enumerate(tail_ids):
                assert rx[j]['k']==1000 and len(rx[j]['factors'])==2
                D[i,TAIL.index(next(s for s in rx[j]['factors'] if s!='k1'))]=1000
            Btail=P[:,tail_index];Rtail=sp.Matrix(tailblock['right_inverse_rows']);A=P*S[:,tail_ids]*D
            assert A==A*Rtail*Btail[tailblock['physical_offset']:,:]
            Q=A*Rtail
            chart['tail_rate_indices']=tail_ids;chart['tail_projected_rhs_sparse_rows']=exact_sparse(Q)
            projection_proofs[name]={'status':'EXACT_AUTHOR_PARAMETER_QUOTIENT','P_rank':5,'kernel_dimension':2,'closure_identity':'P*S_tail*diag(k)*E = Q*P_tail over Q','outside_rate_dependencies_on_tail':False,'cross_subsystem_input':'re0000000306','main_input':'re0000000910','physical_representative':'Pair lower bounds max(0,N3+N2-B_other); residual N2 distributed equally; singleton inventories derived exactly. No output clipping.','microscopic_path_gross_extents':'NOT_UNIQUELY_RECONSTRUCTED; protected aggregate resource/factor currents exact.'}
    # Exact closure counterexamples, frozen rates, nonnegative states.
    counterexamples=[]
    for c in CHAIN:
        counterexamples.append({'candidate':'CHAIN_ROUND_'+str(c['round']),'same_projected_state':'Z=Xslow+Xfast=1; free EFTuGDP adjusted to preserve the aggregate carrier inventory','state_a':{c['slow']:'1','EFTu_GDP':'0'},'state_b':{c['fast']:'1','EFTu_GDP':'1'},'projected_product_derivative_a':'0','projected_product_derivative_b':'1000','exact_lumping':'REJECTED','approximate_rate':'7000/1007','mean_wait':'1007/7000','waiting_variance_source':str(F(1,49)+F(1,1000000)),'waiting_variance_effective':str(F(1007,7000)**2)})
    counterexamples.append({'candidate':'RF1_RF2_SHARED_POST_ENDPOINT_MERGE','state_a':{'elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF1':'1'},'state_b':{'elRS70SAUAA0004_Pept0003tRNAGlyGCC_RF2':'1'},'same_aggregate_bound_ribosome':'1','Pept0003_derivative_a':'1/2','Pept0003_derivative_b':'3/2','status':'REJECTED; RF identities and competing source entrances must remain'})
    save(RESULT/'charts.json',charts)
    certificate={'source_rank':214,'source_left_nullity':27,'active_rank':177,'author_support_species':len(support),'author_condition_full_reconstruction_dimension':charts['R2']['dimension'],'zero_count':len(proof['zero_species']),'support_invariance':proof,'exact_source_matrix_shape':[241,968],'rank_lower_bound_mod_prime':1000003,'source_general_LS_zero':True,'R1_accepted_chart_reverified':True,'charts':{k:{j:v[j] for j in ['dimension','physical_dimension','law_rank','scope'] if j in v} for k,v in charts.items()},'projection_proofs':projection_proofs,'closure_counterexamples':counterexamples,'all_initial_constants_rebased_per_scenario':True,'B1_3_upstream_status':'ENGINEERING_COMPLETE_PENDING_HUMAN_REVIEW; NO_FORMAL_H1_H9_SIGNOFF','scientific_status':'HUMAN_REVIEW_REQUIRED'}
    # Exact lower bound for the author active support matrix, paired with 28 independent laws.
    supported_rows=[names.index(s) for s in names if s in support]
    actual=modular_rank(np.array(S[supported_rows,live].tolist(),dtype=int));assert actual==charts['R2']['dimension']
    certificate['support_live_rank_independent_modular_lower_bound']=actual;certificate['support_live_rank_nullspace_upper_bound']=charts['R2']['physical_dimension']-charts['R2']['law_rank']
    certificate['positive_parameter_full_source_rank']=177;certificate['support_live_rank']=actual
    save(DOC/'mathematical_certificate.json',certificate)
    print(json.dumps({'source':214,'support':len(support),'dimensions':{k:v['dimension'] for k,v in charts.items()},'tail_closure':'EXACT_IF_AUTHOR_RATES_AND_ZERO_PATTERN_FIXED'}),flush=True)
if __name__=='__main__':main()
