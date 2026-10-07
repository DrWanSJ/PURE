"""Feedback-aware transverse diagnostics on frozen R4 roots only."""
from r5_common_v1 import *
from r4_fast_block_common_v1 import R4FamilyRuntime,REG,source_data,condition_initial
from validate_source_coordinates_full_v1 import rate_jacobian
from scipy.linalg import eigvals
def metric(actual,pred,scale,occupancy):
 den=max(float(np.linalg.norm(actual)),1e-30);d=pred-actual
 weights=np.abs(occupancy)/np.maximum(np.sum(abs(occupancy)),1e-30)
 return {'correlation':float(np.corrcoef(actual,pred)[0,1]) if np.std(actual)*np.std(pred)>0 else None,'relative_l2_error':float(np.linalg.norm(d)/den),'magnitude_ratio':float(np.linalg.norm(pred)/den),'sign_agreement':float(np.mean(np.sign(actual)==np.sign(pred))),'p95_absolute_error':float(np.percentile(abs(d),95)),'max_absolute_error':float(max(abs(d))),'occupancy_weighted_rms_absolute':float(np.sqrt(np.sum(weights*d*d))),'scale_normalized_l2':float(np.linalg.norm(d/scale))}
def main():
 checked_registration();r=R4FamilyRuntime('GlyRS');dest=OUT/'glyrs';dest.mkdir(parents=True,exist_ok=True)
 operators=[];feedback=[];lags=[];summaries=[];valid=0;unstable=0
 # One fixed ensemble scale for each eliminated coordinate, never candidate fit.
 ensemble=np.concatenate([source_data(c['condition_id'])[1][:,r.q_index] for c in REG['conditions']]);scale=np.maximum(np.max(abs(ensemble),axis=0),1e-6)
 for c in REG['conditions']:
  name=c['condition_id'];t,full=source_data(name);x0=condition_initial(r.source,name)
  path=ROOT/'results/reduction/r4_fast_block_screen/glyrs_only'/name
  geom=np.load(path/'source_manifold_geometry.npz');gates=list(csv.DictReader((path/'manifold_geometry.csv').open()))
  store={k:[] for k in ['Gq','Fq','Dh','Aperp','feedback','old','new','actual','velocity','defect']};ok=[]
  for i,x in enumerate(full):
   z=r.T@x;q=geom['h0'][i];xc=r.reconstruct(z,q,x0);J=(r.S@rate_jacobian(r.source,xc)).toarray()
   Gq=geom['Gq'][i];Dh=geom['Dh'][i];F=geom['F'][i];Fq=r.T@J@r.D;fb=Dh@Fq;A=Gq-fb;velocity=Dh@F
   root_valid=gates[i]['physical_root']=='True';stable=float(max(eigvals(A).real))<0;valid+=int(root_valid);unstable+=int(root_valid and not stable);ok.append(root_valid)
   old=np.linalg.solve(Gq,velocity);new=np.linalg.solve(A,velocity);actual=x[r.q_index]-q
   ss=scale[:,None];Gs=Gq/ss*scale;As=A/ss*scale;fs=fb/ss*scale
   eigA=eigvals(A);eigG=eigvals(Gq);maxA=float(max(eigA.real));tau=1/(-maxA) if maxA<0 else None
   operators.append({'condition':name,'sample_index':i,'time_s':t[i],'valid_root':root_valid,'Gq_max_real':float(max(eigG.real)),'Aperp_max_real':maxA,'Gq_scaled_numerical_abscissa':float(max(np.linalg.eigvalsh((Gs+Gs.T)/2))),'Aperp_scaled_numerical_abscissa':float(max(np.linalg.eigvalsh((As+As.T)/2))),'Gq_condition':float(np.linalg.cond(Gq)),'Aperp_condition':float(np.linalg.cond(A)),'Aperp_scaled_condition':float(np.linalg.cond(As)),'tau_perp_eigenvalue_s':tau,'defect_propagation_absolute_scale':float(tau*np.linalg.norm(velocity)) if tau else None,'defect_propagation_scaled_scale':float(tau*np.linalg.norm(velocity/scale)) if tau else None,'inverse_operator_defect_scaled_norm':float(np.linalg.norm(new/scale)),'interpretation':'DEFECT_PROPAGATION_DIAGNOSTIC_NO_RIGOROUS_BOUND'})
   feedback.append({'condition':name,'sample_index':i,'time_s':t[i],'valid_root':root_valid,'feedback_raw_norm_ratio':float(np.linalg.norm(fb,2)/max(np.linalg.norm(Gq,2),1e-30)),'feedback_scaled_norm_ratio':float(np.linalg.norm(fs,2)/max(np.linalg.norm(Gs,2),1e-30)),'DhF_max_abs':float(max(abs(velocity))),'feedback_spectral_shift':float(max(eigA.real)-max(eigG.real))})
   for k,v in zip(store,[Gq,Fq,Dh,A,fb,old,new,actual,velocity,-velocity]):store[k].append(v)
   for j,n in enumerate(r.q_names):lags.append({'condition':name,'sample_index':i,'time_s':t[i],'valid_root':root_valid,'species':n,'actual_lag':actual[j],'old_lag':old[j],'feedback_aware_lag':new[j],'h0':q[j],'scale':scale[j]})
  np.savez_compressed(dest/(name+'_operators.npz'),times=t,scale=scale,valid=np.array(ok),**{k:np.array(v) for k,v in store.items()})
  for window,mask in [('full',t>=0),('post_0p05',t>=.05),('t_ge_1',t>=1)]:
   mask=mask&ok
   for j,n in enumerate(r.q_names):
    actual=np.array(store['actual'])[mask,j]
    for predictor in ['old','new']:
     pred=np.array(store[predictor])[mask,j];summaries.append({'condition':name,'window':window,'species':n,'predictor':predictor,'valid_samples':int(sum(mask)),**metric(actual,pred,scale[j],geom['h0'][mask,j])})
  print('GlyRS',name,'diagnosed',sum(ok),'samples',flush=True)
 write_csv(dest/'transverse_operator.csv',operators);write_csv(dest/'feedback_term.csv',feedback);write_csv(dest/'lag_predictor_comparison.csv',lags);write_csv(dest/'lag_predictor_summary.csv',summaries)
 improvements=[]
 for name in [c['condition_id'] for c in REG['conditions']]:
  a=np.load(dest/(name+'_operators.npz'));mask=(a['times']>=.05)&a['valid'];ea=a['actual'][mask]/scale;old=a['old'][mask]/scale;new=a['new'][mask]/scale
  den=max(np.linalg.norm(ea),1e-30);eold=float(np.linalg.norm(old-ea)/den);enew=float(np.linalg.norm(new-ea)/den)
  improvements.append({'condition':name,'window':'post_0p05','old_relative_scaled_l2':eold,'new_relative_scaled_l2':enew,'new_over_old_error':enew/eold,'absolute_old_error_max':float(max(abs(a['old'][mask]-a['actual'][mask]).ravel())),'absolute_new_error_max':float(max(abs(a['new'][mask]-a['actual'][mask]).ravel()))})
 write_csv(dest/'condition_predictor_comparison.csv',improvements)
 better=sum(v['new_relative_scaled_l2']<v['old_relative_scaled_l2'] for v in improvements)
 # No invented acceptance gate: substantial quantitative evidence is reported;
 # promising means consistent explanatory improvement, not model acceptance.
 classification='TRANSVERSE_DYNAMICS_NOT_UNIFORMLY_STABLE' if unstable else ('FEEDBACK_AWARE_CORRECTION_PROMISING' if better==9 else 'ZERO_ORDER_GRAPH_ERROR_NOT_EXPLAINED_BY_LOCAL_TRANSVERSE_FORCING')
 sm={'classification':classification,'valid_samples':valid,'unstable_valid_samples':unstable,'improved_conditions':better,'total_conditions':9,'feedback_raw_norm_ratio_max':max(v['feedback_raw_norm_ratio'] for v in feedback),'feedback_scaled_norm_ratio_max':max(v['feedback_scaled_norm_ratio'] for v in feedback),'new_over_old_error_range':[min(v['new_over_old_error'] for v in improvements),max(v['new_over_old_error'] for v in improvements)],'worst_old_scaled_l2':max(v['old_relative_scaled_l2'] for v in improvements),'worst_new_scaled_l2':max(v['new_relative_scaled_l2'] for v in improvements),'human_review':'HUMAN_REVIEW_REQUIRED','higher_order_model_built':False}
 write_json(dest/'summary.json',sm)
 write_doc('r5_glyrs_transverse_dynamics_v1.md','# GlyRS feedback-aware transverse diagnostics\n\nFor e=q-h0(z), edot=G(z,h0+e)-Dh0 F(z,h0+e)=-Dh0 F0+(Gq-Dh0 Fq)e+O(||e||²). Dh0=-Gq^-1 Gz and Aperp=Gq-Dh0 Fq, all on the R4 graph. Old predictor is Gq^-1 Dh0 F0; new predictor is Aperp^-1 Dh0 F0. Signs follow setting the linear edot to zero. This predicts transverse lag on frozen full-source paths, not a new reduced model.\n\nAll stored R4 valid roots and source trajectories are used; no coupled screens rerun. Full matrices are in condition NPZs; sample spectra/conditioning/numerical abscissa, term ratios and per-coordinate three-window metrics are in the CSVs. Positive numerical abscissa diagnoses potential transient growth, even with stable eigenvalues. tau_perp from spectral abscissa times defect is DEFECT_PROPAGATION_DIAGNOSTIC, not a rigorous bound; nonnormality prevents a semigroup bound from eigenvalues alone. Inverse-operator response is also reported.\n\nMeasured summary:\n\n```json\n'+json.dumps(sm,indent=2)+'\n```\n\nFuture derivation, only if human review selects it: introduce a defensible singular family and solve the invariance equation G(z,h;eta)=Dh F(z,h;eta) order by order. In standard slow-fast scaling eta qdot=g+eta g1, the first correction satisfies gq h1=Dh0 F0-g1. At eta=1 there is no automatically justified small parameter; replacing Gq by Aperp is a local lag diagnostic, not by itself an asymptotic h1 theorem. No h1 implementation or nine-condition validation was executed.')
 print(sm,flush=True)
if __name__=='__main__':main()
