"""Fresh bounded R4 family solves, gross extents and numerical uncertainty."""
from r4_fast_block_common_v1 import *
from scipy.integrate import BDF,solve_ivp
from scipy.integrate._ivp.common import OdeSolution
from run_r3_coupled_grid_v1 import score_rows,stable_slow_balance
from validate_source_coordinates_full_v1 import stable_material_balance
import traceback,uuid,platform

def solve_state(rhs,jac,x0,rtol,prefix):
 clock=time.monotonic();calls=0;stamps=[0.];pieces=[];saved=[];snapshot=[]
 def fun(t,x):
  nonlocal calls
  calls+=1;guarded(clock,calls,REG['bounds']['state_wall_seconds_per_solve'],REG['bounds']['state_rhs_calls_per_solve']);return rhs(t,x)
 solver=BDF(fun,0.,x0,1000.,rtol=rtol,atol=1e-14,jac=jac)
 while solver.status=='running':
  msg=solver.step()
  if solver.status=='failed':raise NumericalBound(str(msg))
  pieces.append(solver.dense_output());stamps.append(float(solver.t));snapshot.append({'time_s':float(solver.t),'nfev':solver.nfev,'njev':solver.njev,'nlu':solver.nlu,'elapsed_s':time.monotonic()-clock})
  if len(snapshot)%100==0:
   write_json(prefix.parent/(prefix.name+'_progress.json'),snapshot[-1]);np.savez_compressed(prefix.parent/(prefix.name+'_checkpoint.npz'),time_s=solver.t,state=solver.y)
 dense=OdeSolution(np.array(stamps),pieces)
 np.savez_compressed(prefix.parent/(prefix.name+'_state.npz'),times=TIMES,state=dense(TIMES).T)
 write_csv(prefix.parent/(prefix.name+'_solver_steps.csv'),snapshot)
 stats={'success':True,'nfev':solver.nfev,'njev':solver.njev,'nlu':solver.nlu,'accepted_steps':len(snapshot),'elapsed_s':time.monotonic()-clock,'rtol':rtol,'atol':1e-14,'end':1000.}
 return dense,dense(TIMES).T,stats

def extents(dense,rate,prefix,rtol=1e-10,atol=1e-14):
 clock=time.monotonic();values=np.zeros((201,968));total=np.zeros(968);compensation=np.zeros(968);counts=[]
 def fun(t,e):
  guarded(clock,0,REG['bounds']['extent_wall_seconds_per_solve'],300000);return rate(t,dense(t))
 for i,(a,b) in enumerate(zip(TIMES[:-1],TIMES[1:]),1):
  sol=solve_ivp(fun,(float(a),float(b)),np.zeros(968),method='DOP853',rtol=rtol,atol=atol)
  if not sol.success:raise NumericalBound('EXTENT:'+sol.message)
  delta=sol.y[:,-1]-compensation;new=total+delta;compensation=(new-total)-delta;total=new;values[i]=total
  counts.append({'segment':i,'end_s':float(b),'nfev':sol.nfev,'elapsed_s':time.monotonic()-clock})
 write_csv(prefix.parent/(prefix.name+'_extent_solver.csv'),counts)
 return values,{'segments':200,'nfev':sum(row['nfev'] for row in counts),'elapsed_s':time.monotonic()-clock,'rtol':rtol,'atol':atol,'definition':'all968_original_directed_gross_rates'}

def source_check():
 r=R4FamilyRuntime('GlyRS');s=r.source;p=OUT/'source_sanity';p.mkdir(exist_ok=True)
 x0=condition_initial(s,'R3_BASE')
 dense,x,stat=solve_state(lambda _t,x:np.array(s.full_rhs_from_rates(rate_vector(s,x))),lambda _t,x:r.S@rate_jacobian(s,x),x0,1e-10,p/'baseline_primary')
 _,hist=source_data('R3_BASE');scale=np.maximum(np.max(abs(hist),axis=0),1e-6);err=float(np.max(abs(x-hist)/scale))
 xi,estat=extents(dense,lambda _t,x:rate_vector(s,x),p/'baseline_primary')
 np.savez_compressed(p/'baseline_directed_extents.npz',times=TIMES,extent=xi)
 write_json(p/'baseline_agreement.json',{'status':'PASS' if err<=1e-9 else 'NUMERICALLY_UNRESOLVED','state_scaled_max_difference':err,'max_absolute_uM':float(np.max(abs(x-hist))),'solver':stat,'extent_solver':estat,'historical_full_sha256':sha(historical_path('R3_BASE')/'full_state.npz'),'fresh_primary_sha256':sha(p/'baseline_primary_state.npz'),'no_reduced_trajectory_reused':True})
 print('baseline fresh agreement',err,flush=True)

def source_uncertainty(condition):
 r=R4FamilyRuntime('GlyRS');s=r.source;p=OUT/'source_uncertainty'/condition
 if (p/'result.json').exists():return
 p.mkdir(parents=True,exist_ok=True);x0=condition_initial(s,condition)
 try:
  dense,x,stats=solve_state(lambda _t,x:np.array(s.full_rhs_from_rates(rate_vector(s,x))),lambda _t,x:r.S@rate_jacobian(s,x),x0,1e-8,p/'probe')
  xi,estat=extents(dense,lambda _t,x:rate_vector(s,x),p/'probe')
  rates=np.array([rate_vector(s,v) for v in x]);np.savez_compressed(p/'probe_ledgers.npz',times=TIMES,extent=xi,rates=rates)
  write_json(p/'result.json',{'status':'COMPLETE','solver':stats,'extent_solver':estat})
 except Exception as e:write_json(p/'result.json',{'status':'NUMERICAL_NONCOMPLETION','failure':str(e)})
 print(condition,'full uncertainty probe complete',flush=True)

def run(family,condition):
 r=R4FamilyRuntime(family);s=r.source;p=OUT/(family.lower()+'_only')/condition
 if (p/'result.json').exists():
  existing=json.loads((p/'result.json').read_text())
  if existing.get('status')!='QUEUED_EXECUTION' or existing.get('queue_owner')!=os.environ.get('R4_QUEUE_OWNER'):
   raise RuntimeError('Refusing to overwrite existing run or another queue claim')
 x0=condition_initial(s,condition);z0=r.T@x0;t,full=source_data(condition);hf=np.load(historical_path(condition)/'directed_ledgers.npz');fv=hf['full_rates'];fe=hf['full_extent']
 primary_clock=time.monotonic();runner_copy=OUT/'implementation_versions/run_r4_family_grid_v1_initial.py'
 # An already-loaded initial worker remains bound to its preserved version.
 runner_path=runner_copy if 'existing' not in locals() and os.environ.get('R4_QUEUE_OWNER') is None and runner_copy.exists() else Path(__file__)
 result={'candidate':'R4_'+family.upper()+'_ONLY','condition':condition,'run_uuid':str(uuid.uuid4()),'fresh_reduced':True,'historical_reduced_reused':False,'preregistration_sha256':sha(DOC/'r4_fast_block_candidates_v1.json'),'runtime_sha256':sha(ROOT/'scripts/r4_fast_block_common_v1.py'),'runner_sha256':sha(runner_path),'source_reuse_verification_sha256':sha(OUT/'source_reuse_verification.json'),'platform':platform.platform(),'python':platform.python_version(),'solver_protocol':REG['solver'],'status':'RUNNING'}
 counters={'calls':0,'max_residual':0.,'fallbacks':0,'min_state':0.}
 def checked(t,z):
  rr=r.solve_fast(z,x0);counters['calls']+=1;counters['max_residual']=max(counters['max_residual'],rr['residual_max']);counters['fallbacks']+=rr.get('method')=='hybr_fallback';counters['min_state']=min(counters['min_state'],float(np.min(rr['state'])))
  if not rr['valid_local_root']:raise NumericalBound(f'PHYSICAL_ROOT_NONCOMPLETION t={t} residual={rr["residual_max"]}')
  return rr
 def rhs(t,z):return r.slow_rhs(z,checked(t,z)['q'],x0)[0]
 def jac(t,z):return r.slow_jacobian(z,checked(t,z)['q'],x0)[0]
 def rates(t,z):return rate_vector(s,checked(t,z)['state'])
 try:
  print(family,condition,'primary reduced start',flush=True)
  dense,z,stat=solve_state(rhs,jac,z0,1e-10,p/'primary_reduced');result['primary_solver']=stat
  red=np.array([checked(t,zv)['state'] for t,zv in zip(TIMES,z)]);rv=np.array([rate_vector(s,x) for x in red]);re,estat=extents(dense,rates,p/'primary_reduced');result['primary_extent_solver']=estat
  # Tighter extent probe does not replace the frozen primary extents.
  re_tight,tstat=extents(dense,rates,p/'tight_extent_probe',1e-11,1e-15);result['tight_extent_solver']=tstat
  np.savez_compressed(p/'state_trajectories.npz',times=TIMES,full_state=full,reduced_state=red,reduced_slow=z)
  np.savez_compressed(p/'directed_ledgers.npz',times=TIMES,full_rates=fv,reduced_rates=rv,full_extent=fe,reduced_extent=re,tight_reduced_extent=re_tight)
  post=TIMES>=.05;sp=score_rows(s.species,full,red,1e-6,post);ids=[v['id'] for v in s.reactions];rates_rows=score_rows(ids,fv,rv,1e-9,post);extent_rows=score_rows(ids,fe,re,1e-6,post)
  aa={row['reaction_id']:row for row in csv.DictReader((ROOT/'models/pnas2017_full_reference/audit/aminoacylation_reactions.csv').open())};process=[]
  for j,reaction in enumerate(s.reactions):
   names=set(reaction['reactants'])|set(reaction['products']);fam='GlyRS' if any(n.startswith('GlyRS') for n in names) else ('MetRS' if any(n.startswith('MetRS') for n in names) else 'OTHER')
   # Descriptive canonical step annotation, no pass thresholds.
   react=set(reaction['reactants']);prod=set(reaction['products']);step='binding_or_other'
   if any('AMP_PPi' in n for n in prod) and not any('AMP_PPi' in n for n in react):step='activation'
   if any('AMP_Met' in n or 'AMP_Gly' in n for n in prod) and not any('AMP_Met' in n or 'AMP_Gly' in n for n in react):step='aminoacyl_transfer'
   if ('MettRNAfMetCAU' in prod or 'GlytRNAGlyGCC' in prod) and any(n.startswith(('GlyRS','MetRS')) for n in react):step='charged_product_release'
   if 'AMP' in prod and any(n.startswith(('GlyRS','MetRS')) for n in react):step='AMP_release'
   for row in (rates_rows[j],extent_rows[j]):row.update(aminoacylation_subsystem=reaction['id'] in aa,family=fam,source_step_annotation=step)
   if fam!='OTHER':process.append({'reaction_id':reaction['id'],'family':fam,'step':step,'rate_E_inf':rates_rows[j]['E_inf'],'rate_post_0p05_E_inf':rates_rows[j]['post_0p05_E_inf'],'extent_E_inf':extent_rows[j]['E_inf'],'extent_post_0p05_E_inf':extent_rows[j]['post_0p05_E_inf'],'scientific_threshold':'DESCRIPTIVE_ONLY'})
  for n,rows in [('species_errors.csv',sp),('directed_rate_errors.csv',rates_rows),('directed_extent_errors.csv',extent_rows),('family_process_errors.csv',process)]:write_csv(p/n,rows)
  fb=stable_material_balance(s,full,fe,x0);rb=stable_slow_balance(r,z,re,z0);rbt=stable_slow_balance(r,z,re_tight,z0)
  law=np.zeros((27,241))
  for j,row in enumerate(s.laws):
   for k,v in row.items():law[j,k]=float(v)
  lawdrift=float(np.max(abs((red-x0)@law.T)))
  accounting=list(csv.DictReader((ROOT/'docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv').open()));resource=[]
  for row in accounting:
   weights=np.array([float(row[n]) for n in s.species]);target=float(weights@x0);ft=full@weights;rt=red@weights;bs=weights@r.S
   change=np.array([math.fsum(float(bs[j])*xi[j] for j in range(968) if bs[j]) for xi in re]);drift=rt-target-change
   resource.append({'resource_row':row['row'],'initial_total':target,'full_peak':float(max(abs(ft))),'reduced_peak':float(max(abs(rt))),'trajectory_error_normalized':float(max(abs(ft-rt))/max(max(abs(ft)),1e-6)),'reduced_accounting_balance_max_abs':float(max(abs(drift))),'full_network_invariant':bool(np.max(abs(bs))==0),'global_invariance_not_assumed':True})
  for n in ['ATP','AMP','PPi','ADP','GTP','GDP','PO4','Pi','CP','Cr']:
   if n in s.index:
    j=s.index[n];resource.append({'resource_row':n,'initial_total':float(x0[j]),'full_peak':float(max(abs(full[:,j]))),'reduced_peak':float(max(abs(red[:,j]))),'trajectory_error_normalized':sp[j]['E_inf'],'reduced_accounting_balance_max_abs':None,'full_network_invariant':False,'global_invariance_not_assumed':True})
  resource.append({'resource_row':'particle_number_proxy','initial_total':float(sum(x0)),'full_peak':float(max(abs(full.sum(axis=1)))),'reduced_peak':float(max(abs(red.sum(axis=1)))),'trajectory_error_normalized':float(max(abs(full.sum(axis=1)-red.sum(axis=1)))/max(max(abs(full.sum(axis=1))),1e-6)),'reduced_accounting_balance_max_abs':None,'full_network_invariant':False,'global_invariance_not_assumed':True})
  write_csv(p/'resource_accounting.csv',resource)
  maxima={'state':max(v['E_inf'] for v in sp),'post_state':max(v['post_0p05_E_inf'] for v in sp),'rate':max(v['E_inf'] for v in rates_rows if v['aminoacylation_subsystem']),'extent':max(v['E_inf'] for v in extent_rows if v['aminoacylation_subsystem']),'all968_rate':max(v['E_inf'] for v in rates_rows),'all968_extent':max(v['E_inf'] for v in extent_rows),'full_balance_abs':float(np.max(abs(fb))),'reduced_slow_balance_abs':float(np.max(abs(rb))),'source_law_drift_abs':lawdrift,'closure':counters['max_residual'],'minimum_concentration':float(red.min())}
  gates={'state':maxima['state']<=.01,'rate':maxima['rate']<=.05,'extent':maxima['extent']<=.01,'balance':max(maxima['full_balance_abs'],maxima['reduced_slow_balance_abs'],lawdrift)<=1e-8,'closure_engineering':maxima['closure']<=1e-10}
  result.update(maxima=maxima,raw_gate_pass=gates,primary_comparison_complete=True)
  # Fresh reduced tolerance-convergence solve: never reuse a primary reduced trajectory.
  r._last_root=None;probe,pz,pstat=solve_state(rhs,jac,z0,1e-8,p/'uncertainty_reduced');result['uncertainty_solver']=pstat
  px=np.array([checked(t,zv)['state'] for t,zv in zip(TIMES,pz)]);pv=np.array([rate_vector(s,x) for x in px]);pe,pestat=extents(probe,rates,p/'uncertainty_reduced');result['uncertainty_extent_solver']=pestat
  np.savez_compressed(p/'uncertainty_reduced_ledgers.npz',times=TIMES,state=px,slow=pz,rates=pv,extent=pe)
  sf=np.load(OUT/'source_uncertainty'/condition/'probe_state.npz')['state'];sl=np.load(OUT/'source_uncertainty'/condition/'probe_ledgers.npz');sfr=sl['rates'];sfe=sl['extent']
  sc=np.maximum(np.max(abs(full),axis=0),1e-6);vs=np.maximum(np.max(abs(fv),axis=0),1e-9);es=np.maximum(np.max(abs(fe),axis=0),1e-6);ai=np.array([j for j,v in enumerate(s.reactions) if v['id'] in aa])
  uncertainty={'state':float(max(np.max(abs(px-red)/sc),np.max(abs(sf-full)/sc))),'rate':float(max(np.max((abs(pv-rv)/vs)[:,ai]),np.max((abs(sfr-fv)/vs)[:,ai]))),'extent':float(max(np.max((abs(pe-re)/es)[:,ai]),np.max((abs(sfe-fe)/es)[:,ai]))),'balance':float(max(np.max(abs(stable_slow_balance(r,pz,pe,z0)-rb)),np.max(abs(stable_material_balance(s,sf,sfe,x0)-fb)),np.max(abs(rbt-rb)))),'gross_float64_representation_bound_abs':float(max(np.max((abs(r.S)@abs(fe).T).T),np.max((abs(r.TS)@abs(re).T).T))*np.finfo(float).eps)}
  uncertainty['balance']=max(uncertainty['balance'],uncertainty['gross_float64_representation_bound_abs'])
  resolved={k:uncertainty[k]<=.1*REG['gates'][k] for k in ['state','rate','extent','balance']}
  failures=['FAIL_'+k.upper() for k,v in gates.items() if not v and k!='closure_engineering']
  result.update(uncertainty=uncertainty,numerical_tier_resolved=resolved,numerical_status='RESOLVED' if all(resolved.values()) else 'NUMERICALLY_UNRESOLVED',scientific_status=('PASS_ALL_REGISTERED_GATES' if all(gates.values()) else failures) if all(resolved.values()) else 'NUMERICALLY_UNRESOLVED',status='COMPLETED',promotion_status='HUMAN_REVIEW_REQUIRED',no_clipping=True,no_fitting=True)
 except Exception as e:
  result.update(status='NUMERICAL_NONCOMPLETION',scientific_status='NUMERICAL_NONCOMPLETION' if not result.get('primary_comparison_complete') else 'NUMERICALLY_UNRESOLVED',numerical_status='NUMERICAL_NONCOMPLETION',failure=str(e),promotion_status='NOT_APPROVED')
  (p/'traceback.log').write_text(traceback.format_exc(),encoding='utf-8',newline='\n')
 result['closure_counters']=counters;result['elapsed_s']=time.monotonic()-primary_clock
 result['outputs_sha256']={f.name:sha(f) for f in sorted(p.iterdir()) if f.is_file() and f.name!='result.json'};write_json(p/'result.json',result)
 print(family,condition,result['status'],result.get('maxima'),flush=True)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--family',choices=['GlyRS','MetRS']);p.add_argument('--condition');p.add_argument('--source-check',action='store_true');p.add_argument('--source-probes',action='store_true');a=p.parse_args()
 if a.source_check:source_check()
 elif a.source_probes:
  for c in REG['conditions']:source_uncertainty(c['condition_id'])
 else:
  assert a.family
  for c in REG['conditions']:
   if a.condition is None or c['condition_id']==a.condition:run(a.family,c['condition_id'])
