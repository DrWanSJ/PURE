"""Canonical independent m4 real-Schur / moving-CSP span diagnostic."""
from r4_fast_block_common_v1 import *
from scipy.linalg import schur,eigvals,solve_sylvester,orth,subspace_angles,solve
from threadpoolctl import threadpool_limits
threadpool_limits(1)
def spectral(J,scale,cutoff):
 T,Q,n=schur(J,output='real',sort=lambda real,imag:real<-cutoff)
 if n!=4:raise RuntimeError('SCHUR_SPLIT_DIMENSION:'+str(n))
 X=solve_sylvester(T[:4,:4],-T[4:,4:],-T[:4,4:]);aa=Q/scale[:,None];bb=Q.T*scale[None,:]
 A=np.column_stack((aa[:,:4],aa[:,4:]+aa[:,:4]@X));B=np.vstack((bb[:4]-X@bb[4:],bb[4:]));P=A[:,:4]@B[:4]
 return T,Q,A,B,P
def angle(a,b):return float(max(np.degrees(subspace_angles(orth(a),orth(b)))))
def equation(reaction):
 def side(items):return ' + '.join((str(v)+' ' if v!=1 else '')+n for n,v in items.items()) or '∅'
 return side(reaction['reactants'])+' -> '+side(reaction['products'])
def module(names):
 labels=[]
 for tag in ['CK','MK','NDK','GlyRS','MetRS','RF3','IF2','EFTu','EFTs']:
  if any(n==tag or n.startswith(tag+'_') or '_'+tag+'_' in n or n.endswith('_'+tag) for n in names):labels.append(tag)
 return '|'.join(labels) or 'OTHER'
def run(external=None):
 s=SourceCoordinateRuntime('source_coordinate_certificate_v4.json');S=source_matrix(s);L=lift_matrix(s).toarray();R=np.array(s.r_index);SR=S[R].toarray();data={c['condition_id']:source_data(c['condition_id']) for c in REG['conditions']}
 fullscale=np.maximum(np.max(abs(np.concatenate([x for _,x in data.values()])),axis=0),1e-6);scale=fullscale[R];p=OUT/'mixed_csp_mode_block';p.mkdir(exist_ok=True)
 np.savez_compressed(p/'fixed_ensemble_metric.npz',scale=scale,full_scale=fullscale,retained_species=np.array(s.retained),L=L)
 if external:
  external=Path(external);prov=json.loads((OUT/'input_provenance.json').read_text())
  for name,h in prov['external_used_sha256'].items():assert sha(external/name)==h
  em=np.load(external/'coordinate_metric_and_maps.npz');assert np.array_equal(scale,em['scale'])
 rows=[];species=[];reactions=[];probes=[];ref=None;prev_condition={};reference_times={};failures=[]
 for condition,(times,full) in data.items():
  store={};x0=condition_initial(s,condition);ext=np.load(external/(condition+'_moving_csp_bases.npz')) if external else None;prev=None;previousP=None;previous_t=None
  for i in REG['csp']['sample_indices']:
   t=float(times[i]);x=np.asarray(s.reconstruct_anchored(full[i,R],x0));J=np.asarray((SR@rate_jacobian(s,x))@L);ev=eigvals(J);d=np.sort(-ev.real[ev.real<0])[::-1];cutoff=(d[3]+d[4])/2;common={'condition':condition,'sample_index':i,'time_s':t,'fast_dimension':4}
   try:
    T,Q,A,B,P0=spectral(J,scale,cutoff);K=J*scale[None,:]/scale[:,None];f=SR@rate_vector(s,x);Jdot=np.asarray((SR@rate_jacobian(s,x.astype(complex)+1j*1e-24*(L@f)))@L).imag/1e-24;Kd=Jdot*scale[None,:]/scale[:,None];H=B@Kd@A;Tf=T[:4,:4];Ts=T[4:,4:]
    E_sf=solve_sylvester(Ts,-Tf,-H[4:,:4]);E_fs=solve_sylvester(Tf,-Ts,-H[:4,4:]);U=np.zeros((214,214));V=np.zeros((214,214));U[:4,4:]=solve(Tf,-E_fs);V[4:,:4]=solve(Tf.T,(-E_sf).T).T;I=np.eye(214)
    A1=A@(I-U)@(I+V);B1=(I-V)@(I+U)@B;Af=A1[:,:4];Bf=B1[:4];P=Af@Bf;Pd=A[:,4:]@E_sf@B[:4]-A[:,:4]@E_fs@B[4:]
    dual=float(np.linalg.norm(B1@A1-I,'fro'));idem=float(np.linalg.norm(P@P-P,'fro')/max(1,np.linalg.norm(P,'fro')));un=float(np.linalg.norm(U,2));vn=float(np.linalg.norm(V,2));update=max(un,vn);cond=float(np.linalg.cond(A1));pdrel=float(np.linalg.norm(K@Pd-Pd@K+Kd@P0-P0@Kd,'fro')/max(np.linalg.norm(K@Pd,'fro')+np.linalg.norm(Kd@P0,'fro'),1e-30));fd=None
    if i in REG['csp']['independent_probe_indices']:
     errs=[]
     for h in REG['csp']['fd_steps_s']:
      try:
       pp=[]
       for sign in [-1,1]:
        xx=x+sign*h*(L@f);jj=np.asarray((SR@rate_jacobian(s,xx))@L);pp.append(spectral(jj,scale,cutoff)[4])
       fdval=float(np.linalg.norm((pp[1]-pp[0])/(2*h)-Pd,'fro')/max(1,np.linalg.norm(Pd,'fro')));errs.append(fdval);issue=''
      except Exception as e:fdval=None;issue=str(e)
      probes.append({**common,'step_s':h,'projector_fd_relative_error':fdval,'failure':issue,'derivative_commutator_relative':pdrel})
     fd=min(errs) if errs else float('inf')
    stable=dual<=1e-8 and idem<=1e-8 and np.isfinite(cond);probeok=fd is None or (fd<=1e-4 and pdrel<=1e-8);include=stable and probeok and update<1
    reasons=[]
    if not stable:reasons.append('UNSTABLE_DUAL_OR_PROJECTOR')
    if not probeok:reasons.append('INDEPENDENT_PROJECTOR_PROBE_UNRESOLVED')
    if update>=1:reasons.append('LARGE_CSP_UPDATE')
    if ref is None:ref=Af.copy();reference_times[i]=Af.copy()
    if condition=='R3_BASE':reference_times[i]=Af.copy()
    cross=angle(Af,reference_times[i]);temp=angle(Af,prev) if prev is not None else 0.;orthref=orth(ref);qa=orth(Af);resid=float(np.linalg.norm(qa-orthref@(orthref.T@qa),'fro')/2)
    quality={'basis_numerically_stable':stable,'dual_identity_error':dual,'projector_idempotence_relative':idem,'update_norm':update,'projector_fd_agreement':fd if fd is not None else 'NOT_IN_INDEPENDENT_PROBE_SUBSET','independent_probe_resolved':probeok,'independent_subset_validation_status':('RESOLVED' if probeok else 'UNRESOLVED') if fd is not None else 'NOT_IN_REGISTERED_INDEPENDENT_SUBSET','included_in_participation_summary':include,'exclusion_reason':'|'.join(reasons)}
    gap=float(-max(eigvals(Tf).real)/max(abs(eigvals(Ts).real)));extangle=angle(Af,ext[f'{i}_4_A'][:,:4]) if ext is not None and f'{i}_4_A' in ext.files else None
    row={**common,**quality,'fast_attracting':bool(max(eigvals(Tf).real)<0),'slowest_fast_real_decay':float(-max(eigvals(Tf).real)),'local_gap':gap,'gap_conditioning':float(np.linalg.cond(Tf)),'basis_condition_number':cond,'U_update_norm':un,'L_update_norm':vn,'schur_to_CSP_angle_deg':angle(Af,A[:,:4]),'temporal_angle_deg':temp,'baseline_same_time_angle_deg':cross,'reference_span_angle_deg':angle(Af,ref),'reference_projection_residual':resid,'projector_change_fro':float(np.linalg.norm(P-previousP,'fro')) if previousP is not None else 0.,'projector_change_per_s':float(np.linalg.norm(P-previousP,'fro')/(t-previous_t)) if previousP is not None else 0.,'external_m4_angle_deg':extangle,'derivative_commutator_relative':pdrel,'no_scientific_persistence_threshold':True}
    rows.append(row);store.update({f'{i}_{k}':v for k,v in {'A':A1,'B':B1,'projector':P,'spectral_A':A,'spectral_B':B,'spectral_projector':P0,'projector_derivative':Pd,'T':T,'Q':Q,'J':J,'Jdot':Jdot,'U':U,'V':V}.items()})
    pointer=np.diag(P);den=max(np.sum(abs(pointer)),1e-30);loading=np.sum(orth(Af)**2,axis=1)
    for j,n in enumerate(s.retained):species.append({**common,**quality,'species':n,'module':module([n]),'signed_pointer':float(pointer[j]),'absolute_normalized_pointer':float(abs(pointer[j])/den),'orthogonal_subspace_loading':float(loading[j])})
    v=rate_vector(s,x);projected=P@(SR/scale[:,None]);importance=np.linalg.norm(projected*v[None,:],axis=0);denimp=max(sum(importance),1e-30);amps=np.linalg.norm((Bf@(SR/scale[:,None]))*v[None,:],axis=0);denamp=max(sum(amps),1e-30)
    for j,reaction in enumerate(s.reactions):reactions.append({**common,**quality,'reaction_id':reaction['id'],'canonical_equation':equation(reaction),'module':module(set(reaction['reactants'])|set(reaction['products'])),'directed_gross_rate':float(v[j]),'normalized_fast_importance':float(importance[j]/denimp),'normalized_amplitude_participation':float(amps[j]/denamp),'participation_defined':bool(sum(importance)>0)})
    prev=Af.copy();previousP=P.copy();previous_t=t
   except Exception as e:failures.append({**common,'exception':str(e),'status':'NUMERICALLY_UNRESOLVED'})
  np.savez_compressed(p/(condition+'_m4_bases.npz'),**store);print(condition,'canonical m4 complete',flush=True)
 write_csv(p/'m4_geometry.csv',rows);write_csv(p/'m4_species_participation.csv',species);write_csv(p/'m4_reaction_participation.csv',reactions);write_csv(p/'independent_projector_probes.csv',probes);write_json(p/'failures.json',failures)
 import pandas as pd
 for n,column,value in [('species','species','absolute_normalized_pointer'),('reaction','reaction_id','normalized_fast_importance')]:
  frame=pd.DataFrame(species if n=='species' else reactions);frame=frame[frame.included_in_participation_summary];rank=frame.groupby(column)[value].mean().sort_values(ascending=False)
  rr=[]
  for name,val in rank.items():
   row=frame[frame[column]==name].iloc[0];rr.append({column:name,'mean_participation_valid_only':float(val),'module':row['module'],'canonical_equation':row.get('canonical_equation',''),'number_included_samples':len(frame[frame[column]==name]),'scientific_status':'HUMAN_REVIEW_REQUIRED'})
  write_csv(p/(n+'_ranked_support.csv'),rr)
 unresolved=bool(failures) or any(not r['independent_probe_resolved'] or not r['basis_numerically_stable'] for r in rows)
 write_json(p/'result.json',{'candidate':'R4_MIXED_CSP_MODE_BLOCK','execution_status':'COMPLETED','scientific_status':'NUMERICALLY_UNRESOLVED' if unresolved else 'LOCAL_4D_FAST_MODE_DIAGNOSTIC_SUPPORTED','mapping_status':'CHEMICAL_BLOCK_MAPPING_REQUIRES_HUMAN_REVIEW','promotion_status':'HUMAN_REVIEW_REQUIRED','numerical_status':'NUMERICALLY_UNRESOLVED' if unresolved else 'RESOLVED','sample_count':len(rows),'expected_samples':9*len(REG['csp']['sample_indices']),'unstable_rows':sum(not r['basis_numerically_stable'] for r in rows),'large_update_rows':sum(r['update_norm']>=1 for r in rows),'independent_unresolved_rows':sum(not r['independent_probe_resolved'] for r in rows),'included_samples':sum(r['included_in_participation_summary'] for r in rows),'max_temporal_angle_deg':max(r['temporal_angle_deg'] for r in rows),'max_condition_angle_deg':max(r['baseline_same_time_angle_deg'] for r in rows),'max_reference_angle_deg':max(r['reference_span_angle_deg'] for r in rows),'min_gap':min(r['local_gap'] for r in rows),'max_update':max(r['update_norm'] for r in rows),'dominant_species':pd.read_csv(p/'species_ranked_support.csv').head(10).to_dict('records'),'dominant_reactions':pd.read_csv(p/'reaction_ranked_support.csv').head(10).to_dict('records'),'global_fixed_chemical_block_justified':False,'no_deleted_species':True,'no_effective_rate_or_fitted_parameter':True,'external_diagnostic_optional_not_required_for_canonical_recompute':True})
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--external-audit',type=Path);a=parser.parse_args();run(a.external_audit)
