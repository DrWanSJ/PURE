"""Independent source-trajectory closure/implicit geometry before coupled solves."""
from r4_fast_block_common_v1 import *
from scipy.linalg import eigvals
from scipy.integrate import solve_ivp
def analyze(family):
 r=R4FamilyRuntime(family);s=r.source;dest=OUT/(family.lower()+'_only');summary=[]
 for c in REG['conditions']:
  name=c['condition_id'];t,full=source_data(name);x0=condition_initial(s,name);p=dest/name;p.mkdir(parents=True,exist_ok=True)
  store={k:[] for k in ['h0','G','Gq','Gz','Dh','F','velocity','defect','actual_lag','predicted_lag']};rows=[];starts=[];relax=[];lagrows=[];previous=None
  qscale=np.maximum(np.max(abs(full[:,r.q_index]),axis=0),1e-6)
  for i,x in enumerate(full):
   z=r.T@x;sol=r.solve_fast(z,x0,seed=x[r.q_index]);q=sol['q'];G,Gq,xc=r.fast_rows(z,q,x0,True)
   J=(r.S@rate_jacobian(s,xc)).toarray();Gq_ind=J[r.q_index]@r.D;Gz=J[r.q_index]@r.Xz
   assert np.max(abs(Gq-Gq_ind))/max(1,np.max(abs(Gq)))<1e-12
   direct=np.array(s.full_rhs_from_rates(rate_vector(s,xc)))[r.q_index]
   assert np.max(abs(G-direct))<1e-10
   Dh=-np.linalg.solve(Gq,Gz);F=r.slow_rhs(z,q,x0)[0];vel=Dh@F;defect=G-vel;ea=x[r.q_index]-q;ep=np.linalg.solve(Gq,vel)
   ev=eigvals(Gq);tau=1/max(1e-30,-max(ev.real));jr=r.T@J@(r.Xz+r.D@Dh);slowev=eigvals(jr);slowrate=float(max(abs(slowev.real)));epsilon=tau*slowrate
   continuity=float(np.linalg.norm((q-previous)/qscale)) if previous is not None else 0.;previous=q.copy()
   row={'condition':name,'sample_index':i,'time_s':float(t[i]),'physical_root':sol['valid_local_root'],'minimum_state':float(np.min(xc)),'Gq_condition':float(np.linalg.cond(Gq)),'Gq_max_real_eigenvalue':float(max(ev.real)),'Gq_min_real_eigenvalue':float(min(ev.real)),'fast_attracting':bool(max(ev.real)<0),'tau_fast_s':float(tau),'complement_fastest_abs_real_s_inverse':slowrate,'epsilon_screen_only':float(epsilon),'gap_ratio_descriptive':float(1/max(epsilon,1e-30)),'closure_max':float(max(abs(G))),'velocity_max':float(max(abs(vel))),'defect_max':float(max(abs(defect))),'occupancy_error_scaled_l2':float(np.linalg.norm(ea/qscale)),'branch_step_scaled_l2':continuity}
   rows.append(row)
   for k,v in zip(store,[q,G,Gq,Gz,Dh,F,vel,defect,ea,ep]):store[k].append(v)
   for j,n in enumerate(r.q_names):lagrows.append({'condition':name,'sample_index':i,'time_s':float(t[i]),'species':n,'actual_lag_uM':float(ea[j]),'predicted_lag_uM':float(ep[j]),'h0_uM':float(q[j]),'q_full_uM':float(x[r.q_index[j]]),'scale_uM':float(qscale[j])})
   if i in REG['geometry']['multistart_relaxation_indices']:
    for label,seed in [('source_fast',x[r.q_index]),('zero',np.zeros(len(q))),('source_fast_scaled_half',.5*x[r.q_index])]:
     feas=float(np.min(r.reconstruct(z,seed,x0)))>=-1e-11
     rr=r.solve_fast(z,x0,seed=seed) if feas else None
     starts.append({'condition':name,'sample_index':i,'start':label,'start_feasible':feas,'valid_root':rr['valid_local_root'] if rr else False,'agreement_max_uM':float(max(abs(rr['q']-q))) if rr else None,'closure_max':rr['residual_max'] if rr else None})
    delta=.01*np.maximum(q,1e-8);factor=1.
    while np.min(r.reconstruct(z,q+factor*delta,x0)) < -1e-11 and factor>2**-40:factor*=.5
    start=q+factor*delta;clock=time.monotonic()
    def rhs(_t,v):
     guarded(clock,0,120,300000);return r.fast_rows(z,v,x0)[0]
    try:
     rr=solve_ivp(rhs,(0,10*tau),start,method='BDF',jac=lambda _t,v:r.fast_rows(z,v,x0,True)[1],rtol=1e-10,atol=1e-14)
     relax.append({'condition':name,'sample_index':i,'complete':bool(rr.success),'duration_s':10*tau,'perturbation_factor':factor,'initial_distance_uM':float(np.linalg.norm(start-q)),'final_distance_uM':float(np.linalg.norm(rr.y[:,-1]-q)),'distance_ratio':float(np.linalg.norm(rr.y[:,-1]-q)/max(np.linalg.norm(start-q),1e-30)),'minimum_q':float(rr.y.min()),'nfev':rr.nfev})
    except Exception as e:relax.append({'condition':name,'sample_index':i,'complete':False,'duration_s':10*tau,'perturbation_factor':factor,'initial_distance_uM':float(np.linalg.norm(start-q)),'final_distance_uM':None,'distance_ratio':None,'minimum_q':None,'nfev':None,'failure':str(e)})
  np.savez_compressed(p/'source_manifold_geometry.npz',times=t,**{k:np.array(v) for k,v in store.items()},D=r.D,Xz=r.Xz,T=r.T,q_index=r.q_index,slow_index=r.slow_index)
  write_csv(p/'manifold_geometry.csv',rows);write_csv(p/'multistart.csv',starts);write_csv(p/'relaxation.csv',relax);write_csv(p/'lag.csv',lagrows)
  lagstats=[]
  for label,mask in [('full_window',t>=0),('post_0p05',t>=.05),('t_ge_1',t>=1)]:
   aa=np.array(store['actual_lag'])[mask];pp=np.array(store['predicted_lag'])[mask]
   for j,n in enumerate(r.q_names):
    actual=aa[:,j];pred=pp[:,j];den=max(np.linalg.norm(actual),1e-30)
    lagstats.append({'condition':name,'window':label,'species':n,'correlation':float(np.corrcoef(actual,pred)[0,1]) if np.std(actual)*np.std(pred)>0 else None,'relative_l2_error':float(np.linalg.norm(pred-actual)/den),'magnitude_ratio':float(np.linalg.norm(pred)/den),'sign_agreement':float(np.mean(np.sign(actual)==np.sign(pred)))})
  write_csv(p/'lag_summary.csv',lagstats)
  sm={'condition':name,'physical_roots':sum(row['physical_root'] for row in rows),'attracting_points':sum(row['fast_attracting'] for row in rows),'closure_max':max(row['closure_max'] for row in rows),'velocity_max':max(row['velocity_max'] for row in rows),'defect_max':max(row['defect_max'] for row in rows),'Gq_condition_max':max(row['Gq_condition'] for row in rows),'tau_fast_max_s':max(row['tau_fast_s'] for row in rows),'gap_ratio_min':min(row['gap_ratio_descriptive'] for row in rows),'multistart_valid':sum(row['valid_root'] for row in starts),'multistart_total':len(starts),'multistart_agreement_max':max(row['agreement_max_uM'] or 0 for row in starts),'relaxations_complete':sum(row['complete'] for row in relax),'relaxation_distance_ratio_max':max(row['distance_ratio'] or 0 for row in relax)}
  write_json(p/'geometry_summary.json',sm);summary.append(sm);print(family,name,'geometry',sm['physical_roots'],sm['attracting_points'],flush=True)
 write_json(dest/'geometry_grid_summary.json',summary)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--family',choices=['GlyRS','MetRS'],required=True);a=p.parse_args();analyze(a.family)
