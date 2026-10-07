"""Preserve native run records; derive review tables from completed evidence."""
from r4_fast_block_common_v1 import *
from run_r3_coupled_grid_v1 import score_rows,stable_slow_balance
from validate_source_coordinates_full_v1 import stable_material_balance
import ast
def implementations():
 paths=[OUT/'implementation_versions/run_r4_family_grid_v1_initial.py',OUT/'implementation_versions/run_r4_family_grid_v1_queue.py',OUT/'implementation_versions/run_r4_family_grid_v1_persistence.py',OUT/'implementation_versions/run_r4_family_grid_v1_classifier.py',ROOT/'scripts/run_r4_family_grid_v1.py'];records=[]
 def numerical_fingerprint(path):
  tree=ast.parse(path.read_text(encoding='utf-8'));nodes=[]
  for n in tree.body:
   if isinstance(n,ast.FunctionDef) and n.name in ['solve_state','extents','source_uncertainty','source_check']:nodes.append(ast.dump(n,include_attributes=False))
   if isinstance(n,ast.FunctionDef) and n.name=='run':
    for sub in n.body:
     if isinstance(sub,ast.FunctionDef):nodes.append(ast.dump(sub,include_attributes=False))
    calls=[]
    for sub in ast.walk(n):
     if isinstance(sub,ast.Call) and isinstance(sub.func,ast.Name) and sub.func.id in ['solve_state','extents','score_rows','stable_material_balance','stable_slow_balance','rate_vector']:
      calls.append(ast.dump(sub,include_attributes=False))
    nodes+=sorted(calls)
  return hashlib.sha256('\n'.join(nodes).encode()).hexdigest()
 for path in paths:records.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path),'scientific_numerical_methods_ast_sha256':numerical_fingerprint(path)})
 assert len({r['scientific_numerical_methods_ast_sha256'] for r in records})==1
 write_json(OUT/'implementation_versions/numerical_equivalence.json',{'status':'PASS','versions':records,'differences':'Queue admission, metadata and primary output persistence only; numerical functions and integration/scoring call expressions identical.','actual_initial_worker_version':'run_r4_family_grid_v1_initial.py'})
 return records

def recover(completed_only=False):
 versions=implementations();oldhash=versions[0]['sha256'];known={r['sha256'] for r in versions};s=SourceCoordinateRuntime('source_coordinate_certificate_v4.json');aa={row['reaction_id'] for row in csv.DictReader((ROOT/'models/pnas2017_full_reference/audit/aminoacylation_reactions.csv').open())};ids=[rx['id'] for rx in s.reactions]
 for family in ['GlyRS','MetRS']:
  r=R4FamilyRuntime(family)
  for c in REG['conditions']:
   name=c['condition_id'];p=OUT/(family.lower()+'_only')/name
   if not (p/'result.json').exists():
    if completed_only:continue
    raise RuntimeError('Registered condition has no terminal record: '+name)
   res=json.loads((p/'result.json').read_text())
   if res['status'] in ['QUEUED_EXECUTION','RUNNING']:
    if completed_only:continue
    raise RuntimeError('Registered condition still running/queued: '+name)
   assert res['runner_sha256'] in known,res['runner_sha256']
   actual=oldhash if name in ['R3_BASE','R3_GLYRS_LOW'] else res['runner_sha256']
   write_json(p/'loaded_implementation_qualification.json',{'native_result_sha256':sha(p/'result.json'),'native_declared_runner_sha256':res['runner_sha256'],'actual_loaded_runner_sha256':actual,'metadata_discrepancy':res['runner_sha256']!=actual,'scientific_methods_equivalence_verified':True,'reason':'Initial worker loaded preserved initial code; LOW metadata may read later on-disk code. Source equations/settings/scoring identical; raw native result is never rewritten.'})
   final_logs={}
   for logpath in p.glob('execution*.log'):
    blob=logpath.read_bytes();registered=res['outputs_sha256'].get(logpath.name);prefix=0;match=0 if hashlib.sha256(b'').hexdigest()==registered else None
    for line in blob.splitlines(keepends=True):
     prefix+=len(line)
     if hashlib.sha256(blob[:prefix]).hexdigest()==registered:match=prefix;break
    if sha(logpath)==registered:match=len(blob)
    if registered is not None:assert match is not None,'Log recording prefix cannot be verified'
    final_logs[logpath.name]={'registered_prefix_sha256':registered,'registered_prefix_bytes':match,'final_log_sha256':sha(logpath),'final_log_bytes':len(blob),'reason':'Final stdout/dispatch output after native snapshot; original recorded prefix verified where present. Native result preserved.'}
   if final_logs:write_json(p/'log_finalization.json',final_logs)
   view=dict(res)
   if (p/'primary_reduced_state.npz').exists():
    z=np.load(p/'primary_reduced_state.npz')['state'];x0=condition_initial(s,name);t,full=source_data(name)
    if (p/'state_trajectories.npz').exists():red=np.load(p/'state_trajectories.npz')['reduced_state']
    else:
     red=np.array([r.solve_fast(zv,x0)['state'] for zv in z]);np.savez_compressed(p/'recovered_state_trajectories.npz',times=t,full_state=full,reduced_state=red,reduced_slow=z)
    write_csv(p/'initial_layer_jump.csv',[{'species':n,'source_initial_uM':float(x0[j]),'reduced_initial_uM':float(red[0,j]),'initial_jump_uM':float(red[0,j]-x0[j]),'inventory_initialization':'T_x0_UNFITTED'} for j,n in enumerate(s.species)])
    sp=score_rows(s.species,full,red,1e-6,TIMES>=.05);rv=np.array([rate_vector(s,x) for x in red]);hf=np.load(historical_path(name)/'directed_ledgers.npz');fv=hf['full_rates'];fe=hf['full_extent'];rate=score_rows(ids,fv,rv,1e-9,TIMES>=.05)
    for j,row in enumerate(rate):row['aminoacylation_subsystem']=ids[j] in aa
    if not (p/'species_errors.csv').exists():write_csv(p/'species_errors.csv',sp)
    if not (p/'directed_rate_errors.csv').exists():write_csv(p/'directed_rate_errors.csv',rate)
    mx=view.get('maxima',{});mx.update(state=max(row['E_inf'] for row in sp),post_state=max(row['post_0p05_E_inf'] for row in sp),rate=max(row['E_inf'] for row in rate if row['aminoacylation_subsystem']),all968_rate=max(row['E_inf'] for row in rate));view['primary_state_complete']=True
    if (p/'directed_ledgers.npz').exists():
     data=np.load(p/'directed_ledgers.npz');re=data['reduced_extent'];er=score_rows(ids,fe,re,1e-6,TIMES>=.05)
     for j,row in enumerate(er):row['aminoacylation_subsystem']=ids[j] in aa
     if not (p/'directed_extent_errors.csv').exists():write_csv(p/'directed_extent_errors.csv',er)
     fb=stable_material_balance(s,full,fe,x0);rb=stable_slow_balance(r,z,re,r.T@x0)
     mx.update(extent=max(row['E_inf'] for row in er if row['aminoacylation_subsystem']),all968_extent=max(row['E_inf'] for row in er),full_balance_abs=float(np.max(abs(fb))),reduced_slow_balance_abs=float(np.max(abs(rb))))
     view['primary_comparison_complete']=True
     if res['status']!='COMPLETED':view['scientific_status']='NUMERICALLY_UNRESOLVED';view['numerical_status']='NUMERICALLY_UNRESOLVED';view['raw_gate_pass']={'state':mx['state']<=.01,'rate':mx['rate']<=.05,'extent':mx['extent']<=.01,'balance':max(mx['full_balance_abs'],mx['reduced_slow_balance_abs'])<=1e-8,'closure_engineering':res['closure_counters']['max_residual']<=1e-10}
     if (p/'uncertainty_reduced_ledgers.npz').exists() and 'tight_reduced_extent' in data.files:
      probe=np.load(p/'uncertainty_reduced_ledgers.npz');sf=np.load(OUT/'source_uncertainty'/name/'probe_state.npz')['state'];sl=np.load(OUT/'source_uncertainty'/name/'probe_ledgers.npz');sc=np.maximum(np.max(abs(full),axis=0),1e-6);vs=np.maximum(np.max(abs(fv),axis=0),1e-9);es=np.maximum(np.max(abs(fe),axis=0),1e-6);ai=np.array([j for j,rx in enumerate(s.reactions) if rx['id'] in aa]);rbt=stable_slow_balance(r,z,data['tight_reduced_extent'],r.T@x0)
      unc={'state':float(max(np.max(abs(probe['state']-red)/sc),np.max(abs(sf-full)/sc))),'rate':float(max(np.max((abs(probe['rates']-rv)/vs)[:,ai]),np.max((abs(sl['rates']-fv)/vs)[:,ai]))),'extent':float(max(np.max((abs(probe['extent']-re)/es)[:,ai]),np.max((abs(sl['extent']-fe)/es)[:,ai]))),'balance':float(max(np.max(abs(stable_slow_balance(r,probe['slow'],probe['extent'],r.T@x0)-rb)),np.max(abs(stable_material_balance(s,sf,sl['extent'],x0)-fb)),np.max(abs(rbt-rb)))),'gross_float64_representation_bound_abs':float(max(np.max((abs(r.S)@abs(fe).T).T),np.max((abs(r.TS)@abs(re).T).T))*np.finfo(float).eps)}
      unc['balance']=max(unc['balance'],unc['gross_float64_representation_bound_abs']);resolved={k:unc[k]<=.1*REG['gates']['process_rate' if k=='rate' else k] for k in ['state','rate','extent','balance']};view.update(uncertainty=unc,numerical_tier_resolved=resolved,status='COMPLETED',numerical_status='RESOLVED' if all(resolved.values()) else 'NUMERICALLY_UNRESOLVED',scientific_status='NUMERICALLY_UNRESOLVED' if not all(resolved.values()) else ('PASS_ALL_REGISTERED_GATES' if all(view['raw_gate_pass'].values()) else ['FAIL_'+k.upper() for k,v in view['raw_gate_pass'].items() if not v and k!='closure_engineering']))
      view['reporting_exception_recovered_from_hash_bound_saved_arrays']=res.get('failure')=="'rate'"
    else:view['primary_comparison_complete']=False
    view['maxima']=mx
   if 'numerical_tier_resolved' in view:
    view['tier_scientific_status']={k:('NUMERICALLY_UNRESOLVED' if not ok else ('PASS_REGISTERED_TIER' if view['raw_gate_pass'][k] else 'FAIL_'+k.upper())) for k,ok in view['numerical_tier_resolved'].items()}
   view['native_status']=res['status'];view['native_result_sha256']=sha(p/'result.json');view['review_role']='Derived comparison/recovery of retained fresh primary evidence. Native failed probes remain unaltered; no uncertainty inferred resolved.';write_json(p/'derived_review_result.json',view)
 print('Native records and method versions preserved; derived review records ready',flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--completed-only',action='store_true');a=p.parse_args();recover(a.completed_only)
