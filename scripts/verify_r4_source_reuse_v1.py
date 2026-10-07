"""Explicit transitive, condition, solver and saved-output reuse verifier."""
from r4_fast_block_common_v1 import *
from validate_source_coordinates_full_v1 import rate_vector
def verify():
 prov=json.loads((OUT/'input_provenance.json').read_text());s=SourceCoordinateRuntime('source_coordinate_certificate_v4.json');rows=[]
 deps={'canonical_sbml':'models/pnas2017_full_reference/original/fMGG_synthesis.xml','grid':'docs/reduction/r3_validation_grid_v1.csv','method':'docs/reduction/r3_aminoacylation_qssa_method.md','protocol':'docs/reduction/r3_coupled_validation_protocol_v1.md','reaction_map':'docs/reduction/r3_source_reaction_candidate_map_v1.csv','aminoacylation_reactions':'models/pnas2017_full_reference/audit/aminoacylation_reactions.csv','runtime_v1':'scripts/r3_resource_total_runtime_v1.py','runtime_v2':'scripts/r3_resource_total_runtime_v2.py','runner':'scripts/run_r3_coupled_grid_v1.py'}
 transitive=['scripts/runtime_reconstruction_rhs.py','scripts/validate_source_coordinates_full_v1.py','scripts/r3_candidate_runtime_v1.py','docs/reduction/source_coordinate_certificate_v4.json','models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv','models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv']
 for c in REG['conditions']:
  name=c['condition_id'];p=historical_path(name);res=json.loads((p/'result.json').read_text());issues=[]
  for key,n in deps.items():
   if res['inputs_sha256'][key]!=sha(ROOT/n):issues.append('dependency:'+n)
  for n in transitive:
   if sha(ROOT/n)!=prov['protected_checkout_sha256'][n] or sha(ROOT/n)!=prov['external_input_source_sha256'][n]:issues.append('transitive:'+n)
  if res['initial_scale_json']!=c['initial_scale_json'] or res['condition_id']!=name:issues.append('condition')
  if res['solver']!={'state':'BDF','extent':'segmented DOP853 ODE states','rtol':1e-10,'atol':1e-14,'start':0.,'end':1000.,'report_points':201}:issues.append('solver')
  for n,h in res['outputs_sha256'].items():
   if sha(p/n)!=h:issues.append('output:'+n)
  t,x=source_data(name);a=np.load(p/'directed_ledgers.npz')
  if not np.array_equal(t,TIMES) or not np.array_equal(x[0],condition_initial(s,name)):issues.append('initial/time')
  v=np.array([rate_vector(s,row) for row in x])
  if np.max(abs(v-a['full_rates'])/np.maximum(abs(v),1))>1e-13:issues.append('saved full rates / canonical author kinetics')
  if a['full_extent'].shape!=(201,968) or not np.array_equal(a['times'],TIMES):issues.append('directed extent shape/grid')
  rows.append({'condition':name,'reuse_valid':not issues,'issues':issues,'full_state_sha256':sha(p/'full_state.npz'),'directed_ledgers_sha256':sha(p/'directed_ledgers.npz'),'result_sha256':sha(p/'result.json'),'initial_state_sha256':hashlib.sha256(x[0].tobytes()).hexdigest(),'source_dependencies_sha256':{n:sha(ROOT/n) for n in deps.values()},'transitive_source_dependencies_sha256':{n:sha(ROOT/n) for n in transitive}})
 write_json(OUT/'source_reuse_verification.json',{'status':'PASS' if all(r['reuse_valid'] for r in rows) else 'RECOMPUTE_REQUIRED','conditions':rows,'historical_reduced_reused':False,'parameters_initial_transitive_binding':'Frozen source hashes plus exact saved physical x0 and recomputed author rates; original full RHS implementation hash is identical.'})
 return rows
if __name__=='__main__':
 rows=verify();print([(r['condition'],r['reuse_valid'],r['issues']) for r in rows]);assert all(r['reuse_valid'] for r in rows)
