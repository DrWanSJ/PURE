"""Independent R4 identities, recomputed metrics, quality labels and hashes."""
from r4_fast_block_common_v1 import *
from scipy.linalg import eigvals
from verify_r4_source_reuse_v1 import verify as verify_source
from run_r3_coupled_grid_v1 import stable_slow_balance
from validate_source_coordinates_full_v1 import stable_material_balance
from fractions import Fraction
import re
def verify(check_only=False,allow_running=False):
 checks=[];problems=[]
 def check(name,ok,detail=''):
  checks.append({'check':name,'pass':bool(ok),'detail':detail})
  if not ok:problems.append(name)
 prov=json.loads((OUT/'input_provenance.json').read_text())
 changed=[n for n,h in prov['protected_checkout_sha256'].items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h]
 check('all_preexisting_tracked_source_and_evidence_hashes_unchanged',not changed,changed)
 bindings=json.loads((OUT/'preregistration_binding.json').read_text());check('preregistration_hashes_unchanged',all(sha(DOC/n)==h for n,h in bindings.items()))
 check('preregistered_nine_conditions_no_adverse',len(REG['conditions'])==9 and 'R3_ADVERSE' not in [c['condition_id'] for c in REG['conditions']])
 check('frozen_solver_and_gates',REG['solver']['rtol']==1e-10 and REG['solver']['atol']==1e-14 and REG['solver']['extent_count']==968 and REG['gates']=={'state':.01,'process_rate':.05,'extent':.01,'balance':1e-8,'epsilon_screen_only':.01,'closure_engineering':1e-10})
 decisions=list(csv.DictReader((DOC/'reduction_decisions.csv').open()));check('all968_reduction_decisions_pending',len(decisions)==968 and all(row['decision_status']=='PENDING' for row in decisions))
 reuse=json.loads((OUT/'source_reuse_verification.json').read_text());check('source_reuse_all9_verified',reuse['status']=='PASS' and len(reuse['conditions'])==9)
 for row in reuse['conditions']:
  name=row['condition'];p=historical_path(name)
  for n,key in [('full_state.npz','full_state_sha256'),('directed_ledgers.npz','directed_ledgers_sha256'),('result.json','result_sha256')]:check(name+':source_reuse:'+n,sha(p/n)==row[key])
 sanity=json.loads((OUT/'source_sanity/baseline_agreement.json').read_text());check('independent_baseline_recompute',sanity['status']=='PASS' and sanity['state_scaled_max_difference']<=1e-9,sanity['state_scaled_max_difference'])
 s=SourceCoordinateRuntime('source_coordinate_certificate_v4.json');S=source_matrix(s);L=lift_matrix(s).toarray();ids=[v['id'] for v in s.reactions];uuids=[]
 aa={row['reaction_id'] for row in csv.DictReader((ROOT/'models/pnas2017_full_reference/audit/aminoacylation_reactions.csv').open())};ai=np.array([i for i,n in enumerate(ids) if n in aa])
 laws=list(csv.DictReader((DOC/'conservation_laws_v0.csv').open()));C=np.zeros((64,241))
 for j,row in enumerate(laws):
  for n,v in json.loads(row['species_coefficients_json']).items():C[j,s.index[n]]=float(Fraction(str(v)))
 check('27_generic_plus37_frozen_crosscheck_laws',len(laws)==64 and sum(row['scope']=='SOURCE_GENERAL' for row in laws)==27)
 for family in ['GlyRS','MetRS']:
  r=R4FamilyRuntime(family);dim=9 if family=='GlyRS' else 12
  partition=json.loads((ROOT/'docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition.json').read_text())
  check(family+':membership',r.q_names==partition[family]['eliminated'])
  check(family+':dimension_map',r.D.shape==(241,dim) and r.Xz.shape==(241,214-dim) and np.max(abs(r.W@r.Wi-np.eye(214)))==0 and np.max(abs(L@r.D[s.r_index]-r.D))==0)
  check(family+':all64_inventory_map_identities',np.max(abs(C@r.D))==0)
  other='MetRS' if family=='GlyRS' else 'GlyRS';check(family+':other_family_retained_dynamic',all(s.index[n] in r.slow_index for n in partition[other]['eliminated']))
  for c in REG['conditions']:
   name=c['condition_id'];p=OUT/(family.lower()+'_only')/name;x0=condition_initial(s,name);full=source_data(name)[1]
   z=r.T@full[50];q=full[50,r.q_index];check(family+name+':reconstruction_identity',np.max(abs(r.reconstruct(z,q,x0)-full[50]))<1e-9)
   geo=np.load(p/'source_manifold_geometry.npz');quality=list(csv.DictReader((p/'manifold_geometry.csv').open()));check(family+name+':all201_geometry_rows',len(quality)==201)
   for i in [0,50,100,200]:
    z=r.T@full[i];q=geo['h0'][i];x=r.reconstruct(z,q,x0);v=rate_vector(s,x);f=np.array(s.full_rhs_from_rates(v));J=(S@rate_jacobian(s,x)).toarray();G=f[r.q_index];Gq=J[r.q_index]@r.D;Gz=J[r.q_index]@r.Xz;Dh=-np.linalg.solve(Gq,Gz);F=r.T@f;velocity=Dh@F
    check(family+name+f':geometry_independent_{i}',np.max(abs(G-geo['G'][i]))<1e-10 and np.max(abs(Dh-geo['Dh'][i]))<1e-8 and np.max(abs(velocity-geo['velocity'][i]))<1e-8 and np.max(abs(G-velocity-geo['defect'][i]))<1e-8)
    # Central directional derivative of the independent full RHS, including carrier shifts.
    direction=np.sin(np.arange(dim)+.7);direction*=1e-5;h=1e-3
    fp=np.array(s.full_rhs_from_rates(rate_vector(s,x+h*r.D@direction)))[r.q_index];fm=np.array(s.full_rhs_from_rates(rate_vector(s,x-h*r.D@direction)))[r.q_index]
    check(family+name+f':independent_Gq_FD_{i}',np.linalg.norm((fp-fm)/(2*h)-Gq@direction)/max(1,np.linalg.norm(Gq@direction))<1e-7)
   result_path=p/'result.json'
   if not result_path.exists():
    check(family+name+':run_present',allow_running);continue
   native=json.loads(result_path.read_text());res=native
   if native['status']=='QUEUED_EXECUTION' and allow_running:continue
   uuids.append(res['run_uuid']);check(family+name+':fresh_reduced',res['fresh_reduced'] and not res['historical_reduced_reused'])
   check(family+name+':prereg_bound',res['preregistration_sha256']==sha(DOC/'r4_fast_block_candidates_v1.json'))
   check(family+name+':runtime_hash_bound',res['runtime_sha256']==sha(ROOT/'scripts/r4_fast_block_common_v1.py'))
   mismatch=[n for n,h in res['outputs_sha256'].items() if sha(p/n)!=h]
   if mismatch and all(n.startswith('execution') and n.endswith('.log') for n in mismatch) and (p/'log_finalization.json').exists():
    info=json.loads((p/'log_finalization.json').read_text())
    for n in mismatch:
     item=info[n];blob=(p/n).read_bytes();check(family+name+':final_stdout_log_prefix:'+n,hashlib.sha256(blob[:item['registered_prefix_bytes']]).hexdigest()==item['registered_prefix_sha256']==res['outputs_sha256'][n] and sha(p/n)==item['final_log_sha256'])
    mismatch=[]
   check(family+name+':run_outputs_hashes',not mismatch,mismatch)
   if (p/'derived_review_result.json').exists():
    res=json.loads((p/'derived_review_result.json').read_text());check(family+name+':native_record_preserved',res['native_result_sha256']==sha(result_path))
   if not allow_running:check(family+name+':all_registered_stages_terminal',res['status']=='COMPLETED' and res['primary_solver']['end']==1000 and res['uncertainty_solver']['end']==1000 and res['primary_extent_solver']['segments']==200 and res['tight_extent_solver']['segments']==200)
   if res.get('primary_comparison_complete'):
    data=np.load(p/'state_trajectories.npz');ledger=np.load(p/'directed_ledgers.npz');red=data['reduced_state'];zred=data['reduced_slow'];xi=ledger['reduced_extent'];vr=ledger['reduced_rates']
    check(family+name+':968_directed_gross_channels',xi.shape==(201,968) and vr.shape==(201,968) and np.array_equal(data['times'],TIMES))
    errors=list(csv.DictReader((p/'directed_extent_errors.csv').open()));check(family+name+':canonical_reaction_ids',len(errors)==968 and [v['id'] for v in errors]==ids)
    check(family+name+':canonical_new_rates',np.max(abs(np.array([rate_vector(s,x) for x in red])-vr)/np.maximum(abs(vr),1))<1e-13)
    reerror=np.max(abs(ledger['full_extent']-xi),axis=0)/np.maximum(np.max(abs(ledger['full_extent']),axis=0),1e-6);check(family+name+':independent_extent_scores',np.max(abs(reerror-np.array([float(v['E_inf']) for v in errors])))<1e-12)
    serr=np.max(abs(full-red),axis=0)/np.maximum(np.max(abs(full),axis=0),1e-6);check(family+name+':independent_state_scores',abs(max(serr)-res['maxima']['state'])<1e-12)
    sr=list(csv.DictReader((p/'species_errors.csv').open()));rr=list(csv.DictReader((p/'directed_rate_errors.csv').open()));vs=np.maximum(np.max(abs(ledger['full_rates']),axis=0),1e-9);ratescore=np.max(abs(ledger['full_rates']-vr),axis=0)/vs
    check(family+name+':all241_species_score_coverage',len(sr)==241 and [v['id'] for v in sr]==s.species and np.max(abs(serr-np.array([float(v['E_inf']) for v in sr])))<1e-12)
    check(family+name+':all968_independent_instantaneous_scores',len(rr)==968 and [v['id'] for v in rr]==ids and np.max(abs(ratescore-np.array([float(v['E_inf']) for v in rr])))<1e-12 and abs(max(ratescore[ai])-res['maxima']['rate'])<1e-12)
    # Dense gross extent ODE definition is inspectable, and canonical rates are independently checked.
    check(family+name+':no_initial_inventory_fit',np.max(abs(zred[0]-r.T@x0))<1e-9)
    check(family+name+':no_projection_into_full_rhs',np.max(abs(red[50]-r.reconstruct(zred[50],red[50,r.q_index],x0)))<1e-9)
    if res['status']=='COMPLETED':
     check(family+name+':uncertainty_precedes_classification',(all(res['numerical_tier_resolved'].values()) or res['scientific_status']=='NUMERICALLY_UNRESOLVED'))
     probe=np.load(p/'uncertainty_reduced_ledgers.npz');sf=np.load(OUT/'source_uncertainty'/name/'probe_state.npz')['state'];sl=np.load(OUT/'source_uncertainty'/name/'probe_ledgers.npz');sc=np.maximum(np.max(abs(full),axis=0),1e-6);es=np.maximum(np.max(abs(ledger['full_extent']),axis=0),1e-6)
     fb=stable_material_balance(s,full,ledger['full_extent'],x0);rb=stable_slow_balance(r,zred,xi,r.T@x0);rbt=stable_slow_balance(r,zred,ledger['tight_reduced_extent'],r.T@x0)
     unc={'state':float(max(np.max(abs(probe['state']-red)/sc),np.max(abs(sf-full)/sc))),'rate':float(max(np.max((abs(probe['rates']-vr)/vs)[:,ai]),np.max((abs(sl['rates']-ledger['full_rates'])/vs)[:,ai]))),'extent':float(max(np.max((abs(probe['extent']-xi)/es)[:,ai]),np.max((abs(sl['extent']-ledger['full_extent'])/es)[:,ai]))),'balance':float(max(np.max(abs(stable_slow_balance(r,probe['slow'],probe['extent'],r.T@x0)-rb)),np.max(abs(stable_material_balance(s,sf,sl['extent'],x0)-fb)),np.max(abs(rbt-rb))))}
     representation=float(max(np.max((abs(r.S)@abs(ledger['full_extent']).T).T),np.max((abs(r.TS)@abs(xi).T).T))*np.finfo(float).eps);unc['balance']=max(unc['balance'],representation)
     check(family+name+':independent_four_tier_uncertainty',all(abs(unc[k]-res['uncertainty'][k])<=1e-12*max(1,abs(unc[k])) for k in unc))
     check(family+name+':uncertainty_budget_classification',all(res['numerical_tier_resolved'][k]==(unc[k]<=.1*REG['gates']['process_rate' if k=='rate' else k]) for k in unc))
   else:check(family+name+':incomplete_unscored',res['scientific_status']=='NUMERICAL_NONCOMPLETION')
 check('fresh_run_uuids_distinct',len(uuids)==len(set(uuids)))
 if not allow_running:
  lawreport=json.loads((OUT/'frozen_law_crosscheck_summary.json').read_text());check('all18_conditions_64law_crosscheck_present',lawreport['record_count']==18*64 and lawreport['coordinate_D_all_laws_max_abs']==0 and lawreport['generic_parent_dimension']==214)
  figures=list((OUT/'figures').glob('*.png'));check('at_least7_CSV_backed_figures',len(figures)>=7 and all(f.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' and f.with_suffix('.csv').is_file() and len(list(csv.DictReader(f.with_suffix('.csv').open())))>0 for f in figures))
 cp=OUT/'mixed_csp_mode_block'
 if (cp/'result.json').exists():
  rows=list(csv.DictReader((cp/'m4_geometry.csv').open()));check('m4_all_registered_samples_retained',len(rows)==9*len(REG['csp']['sample_indices']))
  for row in rows:
   cache=np.load(cp/(row['condition']+'_m4_bases.npz'));i=row['sample_index'];A=cache[i+'_A'];B=cache[i+'_B'];P=cache[i+'_projector'];dual=float(np.linalg.norm(B@A-np.eye(214),'fro'));idem=float(np.linalg.norm(P@P-P,'fro')/max(1,np.linalg.norm(P,'fro')))
   stable=dual<=1e-8 and idem<=1e-8 and np.isfinite(float(row['basis_condition_number']));check('m4:'+row['condition']+':'+i+':quality_label',stable==(row['basis_numerically_stable']=='True') and abs(dual-float(row['dual_identity_error']))<1e-9)
   check('m4:'+row['condition']+':'+i+':four_modes',A[:,:4].shape==(214,4) and np.linalg.matrix_rank(A[:,:4])==4)
   if not stable or row['independent_probe_resolved']=='False' or float(row['update_norm'])>=1:check('m4:'+row['condition']+':'+i+':qualified_aggregate',row['included_in_participation_summary']=='False' and bool(row['exclusion_reason']))
  allreactions=list(csv.DictReader((cp/'m4_reaction_participation.csv').open()));check('m4_canonical_reaction_coverage',len(allreactions)==len(rows)*968 and set(r['reaction_id'] for r in allreactions)==set(ids))
  def side(values):return ' + '.join((str(v)+' ' if v!=1 else '')+n for n,v in values.items()) or '∅'
  eq={rx['id']:side(rx['reactants'])+' -> '+side(rx['products']) for rx in s.reactions};check('m4_all_equations_match_canonical_source',all(r['canonical_equation']==eq[r['reaction_id']] for r in allreactions))
 else:check('m4_result_present',allow_running)
 manifest=OUT/'manifest.json'
 if manifest.exists():
  m=json.loads(manifest.read_text());check('final_output_manifest_hashes',all((ROOT/n).is_file() and sha(ROOT/n)==v['sha256'] for n,v in m['outputs'].items()))
  wanted={str(f.relative_to(ROOT)).replace('\\','/') for f in OUT.rglob('*') if f.is_file() and f.name!='manifest.json'}
  wanted|={str(f.relative_to(ROOT)).replace('\\','/') for f in DOC.glob('r4_*') if f.is_file()};wanted|={str(f.relative_to(ROOT)).replace('\\','/') for f in (ROOT/'scripts').glob('*r4*_v1.py')}
  check('final_output_manifest_complete',wanted<=set(m['outputs']),sorted(wanted-set(m['outputs'])))
 for f in (ROOT/'scripts').glob('*r4*_v1.py'):
  code=f.read_text(encoding='utf-8');check(f.name+':no_clipping_or_optimization_fit',not re.search(r'np\.clip\(|np\.maximum\([^\n]*(?:state|red|q)\s*,\s*0\)|least_squares\(|curve_fit\(',code))
 result={'status':'PASS' if not problems else 'FAIL','scope':'ENGINEERING_AND_PROVENANCE_VERIFICATION_NOT_SCIENTIFIC_PROMOTION','checks':checks,'failed_checks':problems,'protected_file_count':len(prov['protected_checkout_sha256']),'historical_R3_unchanged':not changed,'scientific_promotion':'NOT_APPROVED'}
 if not check_only:write_json(OUT/'independent_verification.json',result)
 print(json.dumps({'status':result['status'],'checks':len(checks),'failed_checks':problems},indent=2));return not problems
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--check-only',action='store_true');p.add_argument('--allow-running',action='store_true');a=p.parse_args();raise SystemExit(0 if verify(a.check_only,a.allow_running) else 1)
