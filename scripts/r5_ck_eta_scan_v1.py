"""Bounded baseline singular-family and explicit startup comparison."""
from r5_ck_partial_equilibrium_runtime_v1 import *
from scipy.integrate import BDF, OdeSolution
from types import SimpleNamespace
import time,traceback
TIMES=np.r_[0.,np.geomspace(1e-4,1000,200)]
RUNTIME_SHA=sha(ROOT/'scripts/r5_ck_partial_equilibrium_runtime_v1.py')
RUNNER_SHA=sha(Path(__file__))
def solve(r,kind,eta,initial,start,end,rtol=1e-10,atol=1e-14):
 dest=OUT/'ck'/('eta_'+str(eta).replace('.','p'))/kind
 if (dest/'result.json').exists():
  n=2
  while (dest/('attempt_'+str(n).zfill(3))).exists():n+=1
  dest=dest/('attempt_'+str(n).zfill(3))
 dest.mkdir(parents=True,exist_ok=True)
 clock=time.monotonic();calls=0
 steps=[];states=[];dense=[];solver=None;last_print=clock
 centered=kind.startswith('outer') or kind.startswith('hybrid_slow')
 solver_initial=initial-r.z0 if centered else initial
 def fun(t,x):
  nonlocal calls
  calls+=1
  if time.monotonic()-clock>1800 or calls>300000:raise RuntimeError('PREREGISTERED_COMPUTATIONAL_BOUND')
  return r.reduced_rhs_delta(t,x) if centered else r.full_rhs(t,x,eta)
 def jac(t,x):return r.reduced_jac_delta(t,x) if centered else r.full_jac(t,x,eta)
 try:
  solver=BDF(fun,start,solver_initial,end,jac=jac,rtol=rtol,atol=atol)
  steps=[start];states=[solver_initial.copy()]
  while solver.status=='running':
   msg=solver.step()
   if solver.t>steps[-1]:steps.append(solver.t);states.append(solver.y.copy());dense.append(solver.dense_output())
   if time.monotonic()-last_print>30:
    info={'time_s':solver.t,'rhs_calls':calls,'steps':len(steps),'elapsed_s':time.monotonic()-clock};write_json(dest/'progress.json',info);np.savez_compressed(dest/'checkpoint.npz',time=solver.t,state=solver.y);print(kind,eta,'progress',info,flush=True);last_print=time.monotonic()
  sol=SimpleNamespace(success=solver.status=='finished',message='complete' if solver.status=='finished' else str(msg),t=np.array(steps),y=np.array(states).T,sol=OdeSolution(steps,dense),nfev=solver.nfev,njev=solver.njev,nlu=solver.nlu)
  info={'complete':bool(sol.success),'message':sol.message,'elapsed_s':time.monotonic()-clock,'rhs_calls':calls,'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu,'accepted_steps':len(sol.t),'rtol':rtol,'atol':atol,'start_s':start,'end_s':float(sol.t[-1]),'minimum_accepted_coordinate':float(sol.y.min()),'coordinate_representation':'CENTERED_FAST_INVARIANT_COORDINATES' if centered else 'FULL_SOURCE_STATES'}
  np.savez_compressed(dest/'accepted_steps.npz',times=sol.t,state=sol.y.T)
  grid=TIMES[(TIMES>=start)&(TIMES<=sol.t[-1])];np.savez_compressed(dest/'report.npz',times=grid,state=sol.sol(grid).T)
  if centered:
   sol.delta=sol.sol;sol.sol=lambda t:sol.delta(t)+r.z0 if np.ndim(t)==0 else sol.delta(t)+r.z0[:,None]
  info.update(runtime_sha256=RUNTIME_SHA,runner_sha256=RUNNER_SHA,minimum_reported_physical_state=float(min(r.manifold_delta(dz)[0].min() for dz in sol.delta(grid).T)) if centered else float(sol.y.min()))
  write_json(dest/'result.json',info);print(kind,eta,info,flush=True)
  return sol if sol.success else None
 except Exception as exc:
  if states:
   np.savez_compressed(dest/'partial_accepted_steps.npz',times=np.array(steps),state=np.array(states))
   if dense:
    grid=TIMES[(TIMES>=start)&(TIMES<=steps[-1])];np.savez_compressed(dest/'partial_report.npz',times=grid,state=OdeSolution(steps,dense)(grid).T)
  write_json(dest/'result.json',{'complete':False,'message':str(exc),'elapsed_s':time.monotonic()-clock,'rhs_calls':calls,'runtime_sha256':RUNTIME_SHA,'runner_sha256':RUNNER_SHA,'traceback':traceback.format_exc()});print(kind,eta,'FAILED',exc,flush=True);return None
def main():
 reg=checked_registration();r=CKRuntime();dest=OUT/'ck';_,q0=material_root(*r.z0[:3]);p0,_=material_root(*r.z0[:3]);tau0=1/(2*p0+1000);switch0=10*tau0
 write_json(dest/'initial_layer_definition.json',{'q_full_initial':r.x0[r.qix].tolist(),'q_outer_initial':q0.tolist(),'jump':(r.x0[r.qix]-q0).tolist(),'tau0_s':tau0,'switch_at_eta1_s':switch0,'rule':reg['hybrid_switch'],'outer_initial_total_error':float(max(abs(r.T@r.manifold(r.z0)[0]-r.z0)))})
 outer=solve(r,'outer',0,r.z0,0,1000)
 if outer is None:write_json(dest/'eta_scan_summary.json',{'status':'NUMERICALLY_UNRESOLVED','reason':'outer solve failed'});return
 zouter=outer.sol(TIMES).T;xouter=np.array([r.manifold_delta(dz)[0] for dz in outer.delta(TIMES).T])
 # Reporting scales are fixed from frozen full-source baseline, not candidates.
 from r4_fast_block_common_v1 import source_data
 t,baseline=source_data('R3_BASE');zscale=np.maximum(np.max(abs(baseline@r.T.T),axis=0),1e-6);xscale=np.maximum(np.max(abs(baseline),axis=0),1e-6)
 scans=[];fulls={};hybrids={};layer=[]
 for eta in reg['eta']:
  full=solve(r,'full',eta,r.x0,0,1000)
  if full is None:scans.append({'eta':eta,'status':'NUMERICALLY_UNRESOLVED','outer_post_layer_slow_max_scaled':None,'hybrid_post_common_layer_slow_max_scaled':None,'fast_post_layer_max_scaled':None,'switch_s':switch0*eta,'observed_order':None});continue
  fulls[eta]=full;xf=full.sol(TIMES).T;switch=switch0*eta;xs=full.sol(switch);zs=r.T@xs
  # Full scaled startup is exactly the full solution on [0,switch], retained
  # explicitly; reduced continuation uses unmodified startup totals.
  np.savez_compressed(dest/('eta_'+str(eta).replace('.','p'))/'startup.npz',times=np.r_[0,np.geomspace(switch/1000,switch,100)],state=full.sol(np.r_[0,np.geomspace(switch/1000,switch,100)]).T)
  hy=solve(r,'hybrid_slow',eta,zs,switch,1000)
  mask=TIMES>=switch;common=TIMES>=switch0
  slowerr=float(np.max(abs((xf[mask]@r.T.T-zouter[mask])/zscale)))
  fasterr=float(np.max(abs((xf[mask][:,r.qix]-xouter[mask][:,r.qix])/xscale[r.qix])))
  hybriderr=None
  if hy:
   hybrids[eta]=hy;hybriderr=float(np.max(abs((xf[common]@r.T.T-hy.sol(TIMES[common]).T)/zscale)))
  distance=np.linalg.norm(xs[r.qix]-r.manifold(zs)[1]);initialdistance=np.linalg.norm(r.x0[r.qix]-q0)
  layer.append({'eta':eta,'switch_s':switch,'startup_initial_distance':initialdistance,'startup_switch_distance':float(distance),'distance_ratio':float(distance/initialdistance),'switch_projection_jump':float(max(abs(xs-r.manifold(zs)[0]))),'startup_full_accepted_steps':int(np.sum(full.t<=switch))})
  scans.append({'eta':eta,'status':'COMPLETE','outer_post_layer_slow_max_scaled':slowerr,'hybrid_post_common_layer_slow_max_scaled':hybriderr,'fast_post_layer_max_scaled':fasterr,'switch_s':switch,'observed_order':None})
  if len(scans)>1 and scans[-2]['hybrid_post_common_layer_slow_max_scaled'] and hybriderr:
   scans[-1]['observed_order']=math.log(hybriderr/scans[-2]['hybrid_post_common_layer_slow_max_scaled'])/math.log(eta/scans[-2]['eta'])
 write_csv(dest/'singular_eta_scan.csv',scans);write_csv(dest/'initial_layer_comparison.csv',layer)
 completed=all(v['status']=='COMPLETE' and v['hybrid_post_common_layer_slow_max_scaled'] is not None for v in scans)
 decreasing=completed and all(b['hybrid_post_common_layer_slow_max_scaled']<a['hybrid_post_common_layer_slow_max_scaled'] for a,b in zip(scans,scans[1:]))
 consistent=decreasing
 sm={'status':'CK_SINGULAR_LIMIT_CONSISTENT' if consistent else 'NOT_CONSISTENT_OR_NUMERICALLY_UNRESOLVED','completed':completed,'systematically_decreasing_hybrid':decreasing,'claim':'descriptive baseline convergence, no formal order or promotion','worst_initial_layer_jump':float(max(abs(r.x0[r.qix]-q0))),'tau0_s':tau0,'eta1_descriptive_test_executed':False}
 if consistent:
  # Numerical uncertainty diagnostic at eta1, never substitutes primary evidence.
  ft=solve(r,'full_tight',1,r.x0,0,1000,1e-11,1e-15);ot=solve(r,'outer_tight',0,r.z0,0,1000,1e-11,1e-15)
  sm['full_eta1_uncertainty_scaled']=float(np.max(abs((ft.sol(TIMES).T-fulls[1].sol(TIMES).T)/xscale))) if ft else None
  sm['outer_uncertainty_scaled']=float(np.max(abs((ot.sol(TIMES).T-zouter)/zscale))) if ot else None
  xf=fulls[1].sol(TIMES).T;hy=hybrids[1];xh=xouter.copy();m=TIMES>=switch0;xh[~m]=xf[~m];xh[m]=np.array([r.manifold_delta(dz)[0] for dz in hy.delta(TIMES[m]).T])
  rows=[]
  for label,approx in [('outer',xouter),('hybrid',xh)]:
   for window,mask in [('full',TIMES>=0),('post_startup',TIMES>=switch0),('post_0p05',TIMES>=.05)]:
    for n in ['T0','T1','B']:
     j=['T0','T1','B'].index(n);a=approx@r.T[j];b=xf@r.T[j];scale=zscale[j]
     rows.append({'approximation':label,'window':window,'observability':'REDUCED_SLOW_OBSERVABLES','observable':n,'max_absolute_error':float(max(abs(a[mask]-b[mask]))),'max_scaled_error':float(max(abs(a[mask]-b[mask]))/scale),'endpoint_error':float(a[-1]-b[-1]),'interpretation':'DESCRIPTIVE_NO_PROMOTION_THRESHOLD'})
    for n in NAMES+['ATP','ADP','Cr','Pept0003']:
     j=r.source.index[n];rows.append({'approximation':label,'window':window,'observability':'RECONSTRUCTED_FAST_STATES' if n in NAMES else 'REDUCED_SLOW_OBSERVABLES','observable':n,'max_absolute_error':float(max(abs(approx[mask,j]-xf[mask,j]))),'max_scaled_error':float(max(abs(approx[mask,j]-xf[mask,j]))/xscale[j]),'endpoint_error':float(approx[-1,j]-xf[-1,j]),'interpretation':'DESCRIPTIVE_NO_PROMOTION_THRESHOLD'})
    vf=np.array([r.rates(x) for x in xf]);va=np.array([r.rates(x) for x in approx])
    # Catalytic CK conversion pair (verified in reaction definition): report each
    # touching slow net channel separately, plus equilibrium gross fast channels.
    touching=[j for j,re in enumerate(r.source.reactions) if any(n.startswith('CK') for n in set(re['reactants'])|set(re['products']))]
    for j in touching:
     sc=max(float(max(abs(vf[:,j]))),1e-6)
     rows.append({'approximation':label,'window':window,'observability':'MICROSCOPIC_GROSS_FLUXES' if j in r.fast else 'REDUCED_SLOW_OBSERVABLES','observable':r.source.reactions[j]['id'],'max_absolute_error':float(max(abs(va[mask,j]-vf[mask,j]))),'max_scaled_error':float(max(abs(va[mask,j]-vf[mask,j]))/sc),'endpoint_error':float(va[-1,j]-vf[-1,j]),'interpretation':'LEADING_GROSS_RATE_ONLY_NO_EXTENT_ACCURACY_CLAIM' if j in r.fast else 'CK_FAMILY_RATE_DESCRIPTIVE'})
   # Energy-regeneration net conversion CK CP_ADP -> CK_Cr_ATP uses source 338/339.
   idx={re['id']:j for j,re in enumerate(r.source.reactions)}
   if 're0000000338' in idx and 're0000000339' in idx:
    netf=vf[:,idx['re0000000338']]-vf[:,idx['re0000000339']];neta=va[:,idx['re0000000338']]-va[:,idx['re0000000339']]
    rows.append({'approximation':label,'window':'post_startup','observability':'REDUCED_SLOW_OBSERVABLES','observable':'CK_catalytic_net_338_minus_339','max_absolute_error':float(max(abs(neta[m]-netf[m]))),'max_scaled_error':float(max(abs(neta[m]-netf[m]))/max(max(abs(netf)),1e-6)),'endpoint_error':float(neta[-1]-netf[-1]),'interpretation':'NET_CONVERSION_RATE_DESCRIPTIVE'})
  write_csv(dest/'baseline_original_parameter_comparison.csv',rows)
  np.savez_compressed(dest/'baseline_comparison.npz',times=TIMES,full=xf,outer=xouter,hybrid=xh,slow_scale=zscale,state_scale=xscale)
  sm['eta1_descriptive_test_executed']=True;sm['eta1_outer_post_startup_worst_scaled']=max(v['max_scaled_error'] for v in rows if v['approximation']=='outer' and v['window']=='post_startup' and v['observability']!='MICROSCOPIC_GROSS_FLUXES')
  sm['eta1_hybrid_post_startup_worst_scaled']=max(v['max_scaled_error'] for v in rows if v['approximation']=='hybrid' and v['window']=='post_startup' and v['observability']!='MICROSCOPIC_GROSS_FLUXES')
 else:write_csv(dest/'baseline_original_parameter_comparison.csv',[{'status':'NOT_EXECUTED_SINGULAR_TEST_NOT_ESTABLISHED','reason':'Human protocol A10 requires successful singular-family test'}])
 write_json(dest/'eta_scan_summary.json',sm);print(sm,flush=True)
if __name__=='__main__':main()
