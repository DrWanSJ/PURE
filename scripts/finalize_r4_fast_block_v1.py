"""Review package, derived navigation, seven CSV-backed decision figures."""
from r4_fast_block_common_v1 import *
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from scipy.linalg import eigvals

def historical_geometry():
 p=OUT/'historical_r3_comparison';p.mkdir(exist_ok=True);r=R3ResourceTotalRuntimeV2();s=r.source;rows=[];lags=[];summaries=[]
 for c in REG['conditions']:
  name=c['condition_id'];t,full=source_data(name);x0=condition_initial(s,name);r._last_root=None;maxclosure=0.;maxdefect=0.
  for i,x in enumerate(full):
   z=r.initial_slow(x);rr=r.solve_fast(z,x0,seed=x[r.q_index]);q=rr['q'];xc=rr['state'];G,Gq,_=r.fast_rows(z,q,x0,True);J=(r.S@rate_jacobian(s,xc)).toarray();Gz=J[r.q_index]@r.Xz;Dh=-np.linalg.solve(Gq,Gz);F=r.slow_rhs(z,q,x0)[0];vel=Dh@F;defect=G-vel;actual=x[r.q_index]-q;pred=np.linalg.solve(Gq,vel)
   rows.append({'candidate':'historical_R3_21','condition':name,'sample_index':i,'time_s':float(t[i]),'closure_max':float(max(abs(G))),'velocity_max':float(max(abs(vel))),'defect_max':float(max(abs(defect))),'physical_root':rr['valid_local_root'],'Gq_condition':float(np.linalg.cond(Gq))})
   for j,n in enumerate(r.q_names):lags.append({'candidate':'historical_R3_21','condition':name,'sample_index':i,'time_s':float(t[i]),'species':n,'actual_lag_uM':float(actual[j]),'predicted_lag_uM':float(pred[j])})
   maxclosure=max(maxclosure,float(max(abs(G))));maxdefect=max(maxdefect,float(max(abs(defect))))
  hist=json.loads((historical_path(name)/'result.json').read_text());summaries.append({'candidate':'historical_R3_21','condition':name,'dynamic':193,'algebraic':21,'scientific_status':'HISTORICAL_REJECTED','numerical_status':'HISTORICAL_COMPLETED','state':hist['maxima']['all_species_E_inf'],'post_state':float(pd.read_csv(historical_path(name)/'species_errors.csv').post_0p05_E_inf.max()),'rate':hist['maxima']['aminoacylation_rate_E_inf'],'extent':hist['maxima']['aminoacylation_extent_E_inf'],'closure':maxclosure,'defect':maxdefect,'nfev':hist['reduced_solver']['nfev'],'nlu':hist['reduced_solver']['nlu']})
 write_csv(p/'manifold_geometry.csv',rows);write_csv(p/'lag.csv',lags);write_csv(p/'comparison.csv',summaries)
 print('historical21 independent geometry recomputed',flush=True)

def manifest():
 outputs={}
 files=list(OUT.rglob('*'))+list(DOC.glob('r4_*'))+list((ROOT/'scripts').glob('*r4*_v1.py'))+[DOC/'.gitattributes',ROOT/'scripts/.gitattributes']
 for f in sorted(set(files)):
  if f.is_file() and f!=OUT/'manifest.json':outputs[str(f.relative_to(ROOT)).replace('\\','/')]={'sha256':sha(f),'bytes':f.stat().st_size}
 write_json(OUT/'manifest.json',{'schema':'R4_REVIEW_PACKAGE_MANIFEST_V1','parent_main_sha':REG['parent_main_sha'],'authorization':'EXECUTION_TESTING_ONLY','promotion_status':'HUMAN_REVIEW_REQUIRED','preregistration_binding':json.loads((OUT/'preregistration_binding.json').read_text()),'outputs':outputs,'self_hash_excluded':True,'historical_files_protected_by':'input_provenance.json','graph_is_derived_navigation_not_source_authority':True})

def finish():
 p=OUT/'figures';p.mkdir(exist_ok=True);hist=pd.read_csv(OUT/'historical_r3_comparison/comparison.csv');comparison=hist.to_dict('records');families={};counts=[]
 for family in ['GlyRS','MetRS']:
  base=OUT/(family.lower()+'_only');results=[json.loads((base/c['condition_id']/'derived_review_result.json').read_text()) for c in REG['conditions']];families[family]=results
  for res in results:
   geo=json.loads((base/res['condition']/'geometry_summary.json').read_text());mx=res.get('maxima',{});status=res.get('scientific_status');status='|'.join(status) if isinstance(status,list) else status
   comparison.append({'candidate':res['candidate'],'condition':res['condition'],'dynamic':205 if family=='GlyRS' else 202,'algebraic':9 if family=='GlyRS' else 12,'scientific_status':status,'numerical_status':res['numerical_status'],'state':mx.get('state'),'post_state':mx.get('post_state'),'rate':mx.get('rate'),'extent':mx.get('extent'),'closure':geo['closure_max'],'defect':geo['defect_max'],'nfev':res.get('primary_solver',{}).get('nfev'),'nlu':res.get('primary_solver',{}).get('nlu')})
  primary=sum(bool(r.get('primary_comparison_complete')) for r in results);completed=sum(r['status']=='COMPLETED' for r in results);passes=sum(r.get('scientific_status')=='PASS_ALL_REGISTERED_GATES' for r in results);resolved=sum(r.get('numerical_status')=='RESOLVED' for r in results)
  gateflags={g:sum(r.get('raw_gate_pass',{}).get(g)==False for r in results) for g in ['state','rate','extent','balance']}
  scientific='SUPPORTED_ON_ALL_9_PRIMARY_R4_CONDITIONS' if passes==9 else ('CONDITIONALLY_SUPPORTED_ON_EXPLICIT_SUBSET' if passes else ('REJECTED_ON_ALL_9_PRIMARY_R4_CONDITIONS' if resolved==9 and primary==9 else 'UNRESOLVED_ON_REGISTERED_DOMAIN'))
  sm={'candidate':family,'conditions_primary_compared':primary,'conditions_all_stages_complete':completed,'conditions_numerically_resolved':resolved,'conditions_passing_all_registered_gates':passes,'raw_gate_failure_counts_not_global_scientific_verdict':gateflags,'scientific_status':scientific,'numerical_status':'RESOLVED' if resolved==9 else 'NUMERICALLY_UNRESOLVED_OR_NONCOMPLETED','execution_status':'COMPLETED_BOUNDED_SCREEN','promotion_status':'HUMAN_REVIEW_REQUIRED','maxima':{k:max((r.get('maxima',{}).get(k) for r in results if r.get('maxima',{}).get(k) is not None),default=None) for k in ['state','post_state','rate','extent','all968_rate','all968_extent','closure','full_balance_abs','reduced_slow_balance_abs']},'geometry_maxima':{k:max(json.loads((base/c['condition_id']/'geometry_summary.json').read_text())[k] for c in REG['conditions']) for k in ['closure_max','defect_max','velocity_max','Gq_condition_max','tau_fast_max_s']},'conditions_passed':[r['condition'] for r in results if r.get('scientific_status')=='PASS_ALL_REGISTERED_GATES'],'conditions':[{k:r.get(k) for k in ['condition','status','scientific_status','numerical_status','failure','maxima','uncertainty','raw_gate_pass']} for r in results]}
  counts.append(sm)
  sm['resolved_tier_failure_counts']={k:sum(r.get('tier_scientific_status',{}).get(k)=='FAIL_'+k.upper() for r in results) for k in ['state','rate','extent','balance']}
  lag=pd.concat([pd.read_csv(base/c['condition_id']/'lag_summary.csv') for c in REG['conditions']]);lagstats=lag.groupby('window')[['correlation','relative_l2_error','magnitude_ratio','sign_agreement']].median().to_dict('index');sm['lag_median_diagnostics']=lagstats
  lines=[f'# R4 {family}_ONLY QSSA execution certificate', '',f'Execution: {sm["execution_status"]}. Primary comparisons: {primary}/9; all numerical stages: {completed}/9. Resolved conditions: {resolved}/9. All registered gates passed with uncertainty resolved: {passes}/9.', '',f'Scientific status: **{scientific}**. Promotion: HUMAN_REVIEW_REQUIRED; no reduced-core or reaction-deletion approval.', '',f'Fixed split: {205 if family=="GlyRS" else 202} dynamic + {9 if family=="GlyRS" else 12} algebraic =214 after exact R1. The other family and historical kept states remain dynamic. Exact map, derivative and source-inventory identities are independently verified.', '', 'Closure is not invariance. All201 source points per condition retain G, Gq, Gz, Dh, F, Dh F, G-Dh F and actual/predicted lag in NPZ/CSV. Six representative points per condition retain feasible multistart and frozen-z relaxation results. Branch continuity/occupancy, local attractivity, gap and conditioning are descriptive. Full-window, post0.05 and t>=1 lag are separate.', '', '| Condition | Numerical / scientific status | State | Post state | AA rate | AA extent |', '|---|---|---:|---:|---:|---:|']
  for rr in comparison:
   if rr['candidate']=='R4_'+family.upper()+'_ONLY':lines.append('|'+ '|'.join(str(rr[k]) for k in ['condition','scientific_status','state','post_state','rate','extent'])+'|')
  lines+=['','| Condition | State tier | Rate tier | Extent tier | Balance tier |','|---|---|---|---|---|']
  for rr in results:lines.append('|'+ '|'.join([rr['condition']]+[rr.get('tier_scientific_status',{}).get(k,'UNSCORED') for k in ['state','rate','extent','balance']])+'|')
  lines+=['',f'Resolved tier failures: `{json.dumps(sm["resolved_tier_failure_counts"])}`. The overall preregistered status remains unresolved when any relevant tier is unresolved; resolved state/rate/extent failures are retained separately. Balance involves large opposing gross directed extents; numerical error is not attributed automatically to QSSA. No thresholds or initial inventories were fitted. Initial algebraic jumps are retained and scored.','',f'Geometry maxima: `{json.dumps(sm["geometry_maxima"])}`. Coupled trajectory closure maximum: {sm["maxima"]["closure"]:.12g}.','',f'Lag medians: `{json.dumps(lagstats)}`. These are explanation, never acceptance gates.','', 'Native result.json is immutable. Six reporting-only KeyError records retain their original traceback and status; derived_review_result.json recomputes their classification from hash-bound completed primary/probe arrays. No missing solve was assumed complete. All implementation versions and numerical-method equivalence are preserved.','', 'Bounded noncompletion retains checkpoints, logs and UNSCORED status. Previous affine arithmetic attempts are separately preserved under R3_BASE/attempt_001_affine_roundoff. Stable reconstruction uses the historical operation order without changing coordinate equations.']
  (DOC/('r4_'+family.lower()+'_only_qssa_certificate.md')).write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
 # Add the same per-condition lag summaries and branch/burden descriptors.
 oldlag=pd.read_csv(OUT/'historical_r3_comparison/lag.csv')
 for row in comparison:
  if row['candidate']=='historical_R3_21':
   geo=pd.read_csv(OUT/'historical_r3_comparison/manifold_geometry.csv');geo=geo[geo.condition==row['condition']]
   row['branch_condition_max']=float(geo.Gq_condition.max());row['manifold_velocity_max']=float(geo.velocity_max.max())
   raw=oldlag[oldlag.condition==row['condition']];lagmed={}
   for window,cut in [('full_window',0),('post_0p05',.05),('t_ge_1',1)]:
    values=[];correlations=[]
    for _,g in raw[raw.time_s>=cut].groupby('species'):
     a=g.actual_lag_uM.values;b=g.predicted_lag_uM.values;values.append(float(np.linalg.norm(a-b)/max(np.linalg.norm(a),1e-30)))
     if np.std(a)*np.std(b)>0:correlations.append(float(np.corrcoef(a,b)[0,1]))
    lagmed[window]={'relative_l2_error':float(np.median(values)),'correlation':float(np.median(correlations)) if correlations else None}
   ts=pd.read_csv(historical_path(row['condition'])/'timescale.csv');row['local_fast_timescale_max_s']=float(ts.tau_fast_s.max());row['timescale_semantics']='HISTORICAL_SOURCE_TRAJECTORY_TIMESCALE_NOT_GRAPH_POINT'
  else:
   family='glyrs' if 'GLYRS' in row['candidate'] else 'metrs';base=OUT/(family+'_only')/row['condition'];gs=json.loads((base/'geometry_summary.json').read_text());row['branch_condition_max']=gs['Gq_condition_max'];row['manifold_velocity_max']=gs['velocity_max'];row['local_fast_timescale_max_s']=gs['tau_fast_max_s'];row['timescale_semantics']='SELECTED_FAMILY_GRAPH_Gq';lagmed=pd.read_csv(base/'lag_summary.csv').groupby('window')[['correlation','relative_l2_error']].median().to_dict('index')
  for window,data in lagmed.items():
   row[window+'_lag_correlation_median']=data['correlation'];row[window+'_lag_relative_l2_error_median']=data['relative_l2_error']
 write_json(OUT/'family_grid_summary.json',counts);write_csv(OUT/'historical_r3_comparison/side_by_side.csv',comparison)
 mixed=json.loads((OUT/'mixed_csp_mode_block/result.json').read_text());grid=pd.DataFrame(comparison)
 # Preserve raw mixed output; use JSON null for unavailable species equations
 # in newly derived summaries rather than propagating pandas NaN.
 for group in ['dominant_species','dominant_reactions']:
  for row in mixed[group]:
   for key,value in row.items():
    if isinstance(value,float) and not np.isfinite(value):row[key]=None
 cmp=[]
 for sm in counts:
  cmp.append({'candidate':'R4_'+sm['candidate'].upper()+'_ONLY','type':'CHEMICAL_QSSA','algebraic_dimension':9 if sm['candidate']=='GlyRS' else 12,'dynamic_dimension':205 if sm['candidate']=='GlyRS' else 202,'geometric_fast_dimension':None,'numerical_status':sm['numerical_status'],'scientific_status':sm['scientific_status'],'conditions_primary_compared':sm['conditions_primary_compared'],'conditions_all_gates_passed':sm['conditions_passing_all_registered_gates'],'worst_state':sm['maxima']['state'],'worst_post_state':sm['maxima']['post_state'],'worst_AA_rate':sm['maxima']['rate'],'worst_AA_extent':sm['maxima']['extent'],'closure':sm['geometry_maxima']['closure_max'],'invariance_defect':sm['geometry_maxima']['defect_max'],'Gq_condition':sm['geometry_maxima']['Gq_condition_max'],'local_fast_timescale':sm['geometry_maxima']['tau_fast_max_s'],'span_temporal_angle':None,'span_condition_angle':None,'max_CSP_update':None,'chemical_mapping_status':'EXACT_HISTORICAL_PARTITION_TESTED_ONLY'})
 cmp.append({'candidate':'R4_MIXED_CSP_MODE_BLOCK','type':'GEOMETRIC_MODE_DIAGNOSTIC','algebraic_dimension':None,'dynamic_dimension':214,'geometric_fast_dimension':4,'numerical_status':mixed['numerical_status'],'scientific_status':mixed['scientific_status'],'conditions_primary_compared':None,'conditions_all_gates_passed':None,'worst_state':None,'worst_post_state':None,'worst_AA_rate':None,'worst_AA_extent':None,'closure':None,'invariance_defect':None,'Gq_condition':None,'local_fast_timescale':None,'span_temporal_angle':mixed['max_temporal_angle_deg'],'span_condition_angle':mixed['max_condition_angle_deg'],'max_CSP_update':mixed['max_update'],'chemical_mapping_status':mixed['mapping_status']})
 for row,sm in zip(cmp[:2],counts):
  base=OUT/(sm['candidate'].lower()+'_only');gg=json.loads((base/'geometry_grid_summary.json').read_text());row['local_gap_ratio_min_descriptive']=min(g['gap_ratio_min'] for g in gg);row['manifold_velocity']=sm['geometry_maxima']['velocity_max'];row['resource_full_gross_balance']=sm['maxima']['full_balance_abs'];row['resource_reduced_slow_gross_balance']=sm['maxima']['reduced_slow_balance_abs'];row['conditions_all_numerical_stages_completed']=sm['conditions_all_stages_complete'];row['conditions_numerically_resolved']=sm['conditions_numerically_resolved']
  for window,data in sm['lag_median_diagnostics'].items():row[window+'_lag_correlation_median']=data['correlation'];row[window+'_lag_relative_l2_error_median']=data['relative_l2_error']
 modes_frame=pd.read_csv(OUT/'mixed_csp_mode_block/m4_geometry.csv');cmp[2].update(local_gap_ratio_min_descriptive=mixed['min_gap'],manifold_velocity=None,resource_full_gross_balance=None,resource_reduced_slow_gross_balance=None,conditions_all_numerical_stages_completed=None,conditions_numerically_resolved=None,basis_stable_samples=mixed['sample_count']-mixed['unstable_rows'],independent_unresolved_samples=mixed['independent_unresolved_rows'],mode_fast_attracting_samples=int(modes_frame.fast_attracting.sum()),basis_condition_number_max=float(modes_frame.basis_condition_number.max()),dominant_species='|'.join(x['species'] for x in mixed['dominant_species'][:8]),dominant_reactions='|'.join(x['reaction_id'] for x in mixed['dominant_reactions'][:8]),global_fixed_chemical_block_justified=False)
 fields=list(dict.fromkeys(k for row in cmp for k in row));cmp=[{k:row.get(k) for k in fields} for row in cmp]
 write_csv(OUT/'fast_block_comparison.csv',cmp)
 # Figure1: species distributions with missing/incomplete conditions explicit.
 state=[];process=[];extent=[];defects=[];lag=[]
 for c in REG['conditions']:
  name=c['condition_id'];hp=historical_path(name)
  for candidate,folder in [('historical_R3_21',hp),('R4_GLYRS_ONLY',OUT/'glyrs_only'/name),('R4_METRS_ONLY',OUT/'metrs_only'/name)]:
   if (folder/'species_errors.csv').exists():
    frame=pd.read_csv(folder/'species_errors.csv');state.extend({'candidate':candidate,'condition':name,'species':row.id,'post_state_E_inf':row.post_0p05_E_inf,'status':'MEASURED'} for row in frame.itertuples())
   else:state.append({'candidate':candidate,'condition':name,'species':'N/A','post_state_E_inf':None,'status':'UNSCORED_NUMERICAL_NONCOMPLETION'})
   if (folder/'directed_rate_errors.csv').exists():
    frame=pd.read_csv(folder/'directed_rate_errors.csv')
    if 'family' not in frame:
     frame['family']=['GlyRS' if any(n.startswith('GlyRS') for n in set(s['reactants'])|set(s['products'])) else ('MetRS' if any(n.startswith('MetRS') for n in set(s['reactants'])|set(s['products'])) else 'OTHER') for s in SourceCoordinateRuntime('source_coordinate_certificate_v4.json').reactions]
    for family in ['GlyRS','MetRS']:process.append({'candidate':candidate,'condition':name,'family':family,'rate_E_inf':float(frame[frame.family==family].E_inf.max()),'status':'MEASURED_DESCRIPTIVE'})
   else:
    for family in ['GlyRS','MetRS']:process.append({'candidate':candidate,'condition':name,'family':family,'rate_E_inf':None,'status':'UNSCORED_NUMERICAL_NONCOMPLETION'})
   if (folder/'directed_extent_errors.csv').exists():
    frame=pd.read_csv(folder/'directed_extent_errors.csv');extent.extend({'candidate':candidate,'condition':name,'reaction_id':row.id,'extent_E_inf':row.E_inf,'status':'MEASURED'} for row in frame.itertuples())
   else:extent.append({'candidate':candidate,'condition':name,'reaction_id':'N/A','extent_E_inf':None,'status':'UNSCORED_NUMERICAL_NONCOMPLETION'})
  for candidate,folder in [('R4_GLYRS_ONLY',OUT/'glyrs_only'/name),('R4_METRS_ONLY',OUT/'metrs_only'/name)]:
   frame=pd.read_csv(folder/'manifold_geometry.csv');defects.extend({'candidate':candidate,'condition':name,'time_s':row.time_s,'closure':row.closure_max,'defect':row.defect_max} for row in frame.itertuples())
   frame=pd.read_csv(folder/'lag.csv');wanted=['GlyRS_AMP_GlytRNAGlyGCC','GlyRS_Gly_ATP'] if 'GLYRS' in candidate else ['MetRS_AMP_MettRNAfMetCAU','MetRS_Met_ATP'];frame=frame[(frame.condition=='R3_BASE')&(frame.species.isin(wanted))];lag.extend({'candidate':candidate,'time_s':row.time_s,'species':row.species,'actual':row.actual_lag_uM,'predicted':row.predicted_lag_uM} for row in frame.itertuples())
 histgeom=pd.read_csv(OUT/'historical_r3_comparison/manifold_geometry.csv');defects.extend({'candidate':'historical_R3_21','condition':row.condition,'time_s':row.time_s,'closure':row.closure_max,'defect':row.defect_max} for row in histgeom.itertuples())
 for name,rows in [('01_post_layer_state_errors',state),('02_family_process_rate_errors',process),('03_directed_extent_errors',extent),('04_closure_vs_defect',defects),('05_representative_lag',lag)]:write_csv(p/(name+'.csv'),rows)
 labels=['historical_R3_21','R4_GLYRS_ONLY','R4_METRS_ONLY']
 def save(name):
  plt.tight_layout();plt.savefig(p/(name+'.png'),dpi=160);plt.close()
 for name,value,title,gate in [('01_post_layer_state_errors','post_state_E_inf','Post-0.05 s state errors (all species)',.01),('03_directed_extent_errors','extent_E_inf','Gross directed cumulative extent errors',.01)]:
  frame=pd.read_csv(p/(name+'.csv'));plt.figure(figsize=(8,4.5));boxes=[np.maximum(frame[(frame.candidate==n)&frame[value].notna()][value].values,1e-16) for n in labels]
  for j,values in enumerate(boxes):
   if len(values):
    plt.boxplot([values],positions=[j+1],widths=.5,showfliers=False)
    worst=frame[(frame.candidate==labels[j])&frame[value].notna()].groupby('condition')[value].max()
    plt.scatter(np.full(len(worst),j+1),np.maximum(worst.values,1e-16),marker='x',color='black',s=28,label='Each-condition maximum' if j==0 else None,zorder=4)
   else:plt.text(j+1,.1,'UNSCORED',ha='center')
  plt.xticks([1,2,3],labels);plt.yscale('log');plt.axhline(gate,color='red',ls='--',label='Frozen tier budget');plt.ylabel('Trajectory-scaled error');plt.title(title);plt.legend(fontsize=8);save(name)
 frame=pd.DataFrame(process);fig,axes=plt.subplots(1,2,figsize=(10,4))
 for ax,family in zip(axes,['GlyRS','MetRS']):
  for j,n in enumerate(labels):
   vals=frame[(frame.candidate==n)&(frame.family==family)].rate_E_inf.dropna().values
   if len(vals):ax.scatter(np.full(len(vals),j),vals,label=n,s=18)
   else:ax.text(j,.2,'UNSCORED',ha='center',fontsize=7)
  ax.set_xticks(range(3),['R3_21','R4_Gly','R4_Met']);ax.set_yscale('log');ax.set_title(family+' directed family steps');ax.set_ylabel('Descriptive rate error')
 fig.suptitle('Family process support; no new family-specific gate');save('02_family_process_rate_errors')
 frame=pd.DataFrame(defects);plt.figure(figsize=(8,4.5))
 for j,n in enumerate(labels):
  vals=frame[frame.candidate==n];plt.scatter(np.full(len(vals),j)-.08,np.maximum(vals.closure,1e-20),s=2,alpha=.3,label=n+' closure');plt.scatter(np.full(len(vals),j)+.08,np.maximum(vals.defect,1e-20),s=2,alpha=.3,label=n+' defect')
 plt.yscale('log');plt.xticks(range(3),labels);plt.ylabel('max |G| or |G-Dh F| (uM/s)');plt.title('Closure does not establish invariance');plt.legend(fontsize=6,ncol=2);save('04_closure_vs_defect')
 frame=pd.DataFrame(lag);fig,axes=plt.subplots(2,2,figsize=(11,7))
 for col,n in enumerate(labels[1:]):
  species=['GlyRS_Gly_ATP','GlyRS_AMP_GlytRNAGlyGCC'] if col==0 else ['MetRS_Met_ATP','MetRS_AMP_MettRNAfMetCAU']
  for ax,sp in zip(axes[:,col],species):
   vals=frame[(frame.candidate==n)&(frame.species==sp)];ax.plot(vals.time_s,vals.actual,label='Observed q_full-h0');ax.plot(vals.time_s,vals.predicted,label='Linearized predictor',ls='--');ax.set_xscale('symlog',linthresh=1e-4);ax.set_title(sp,fontsize=10);ax.set_xlabel('Time (s)');ax.set_ylabel('Lag (uM)');ax.legend(fontsize=7)
 fig.suptitle('Baseline representative lag; full window retained');save('05_representative_lag')
 modes=pd.read_csv(OUT/'mixed_csp_mode_block/m4_geometry.csv');modes.to_csv(p/'06_m4_span_persistence.csv',index=False);fig,axes=plt.subplots(1,2,figsize=(10,4))
 for condition,frame in modes.groupby('condition'):
  axes[0].plot(frame.time_s,frame.temporal_angle_deg,label=condition,lw=.8);axes[1].plot(frame.time_s,frame.baseline_same_time_angle_deg,label=condition,lw=.8)
 for ax,title in zip(axes,['Adjacent-time largest principal angle','Same-time angle to baseline']):ax.set_xscale('symlog',linthresh=1e-4);ax.set_ylabel('Degrees');ax.set_xlabel('Time (s)');ax.set_title(title)
 axes[1].legend(fontsize=5,ncol=2);fig.suptitle('m4 span persistence: no new scientific threshold');save('06_m4_span_persistence')
 sr=pd.read_csv(OUT/'mixed_csp_mode_block/species_ranked_support.csv').head(8);rr=pd.read_csv(OUT/'mixed_csp_mode_block/reaction_ranked_support.csv').head(8);participation=[]
 for typ,frame,col in [('species',sr,'species'),('reaction',rr,'reaction_id')]:
  for _,row in frame.iterrows():participation.append({'support_type':typ,'id':row[col],'mean_participation':row.mean_participation_valid_only,'canonical_equation':row.get('canonical_equation',''),'included_samples':row.number_included_samples})
 write_csv(p/'07_m4_participation.csv',participation);fig,axes=plt.subplots(1,2,figsize=(12,5))
 for ax,frame,col in [(axes[0],sr,'species'),(axes[1],rr,'reaction_id')]:ax.barh(frame[col].iloc[::-1],frame.mean_participation_valid_only.iloc[::-1]);ax.set_xlabel('Mean participation over qualified samples')
 fig.suptitle('m4 chemical support; excluded raw rows retained');save('07_m4_participation')
 # Explicit audit neighborhood, including low-support NDK.
 rrall=pd.read_csv(OUT/'mixed_csp_mode_block/reaction_ranked_support.csv');focus=rrall[(rrall.module.fillna('').str.contains('CK|MK|NDK'))|rrall.reaction_id.isin(['re0000000332','re0000000333','re0000000380','re0000000381','re0000000344','re0000000345'])];focus.to_csv(OUT/'mixed_csp_mode_block/CK_MK_NDK_neighborhood.csv',index=False)
 g,m=counts;causal='UNDETERMINED_NUMERICAL_UNCERTAINTY_OR_NONCOMPLETION'
 if g['conditions_numerically_resolved']==m['conditions_numerically_resolved']==9:
  gp=g['conditions_passing_all_registered_gates']==9;mp=m['conditions_passing_all_registered_gates']==9;causal=('BOTH_PASS_HISTORICAL_R3_FAIL' if gp and mp else ('G_PASS_M_FAIL' if gp else ('G_FAIL_M_PASS' if mp else 'BOTH_FAIL')))
 summaries={'parent_main_sha':REG['parent_main_sha'],'frozen_hashes_unchanged':'CHECK_INDEPENDENT_VERIFIER','family_candidates':counts,'mixed_mode':mixed,'causal_family_outcome':causal,'historical_R3_status':'SPECIFIC_21_STATE_QSSA_REJECTED_ON_9_COMPLETED_CONDITIONS','R3_ADVERSE':'UNSCORED_NUMERICAL_NONCOMPLETION_NOT_PART_OF_R4_PRIMARY_SCREEN','promotion':'HUMAN_REVIEW_REQUIRED','reduction_decisions':'968_PENDING','PURE_reduced_core':'NOT_VALIDATED','higher_order_old21':'NOT_EXECUTED'};write_json(OUT/'screen_summary.json',summaries)
 mixedtext=f'''# R4 mixed four-mode diagnostic

Execution: COMPLETED. Numerical/scientific outcome: **{mixed['scientific_status']}**. Exactly {mixed['sample_count']}/{mixed['expected_samples']} sampled records retained. Stable dual/projector records: {mixed['sample_count']-mixed['unstable_rows']}; large updates: {mixed['large_update_rows']}; independently unresolved probe rows: {mixed['independent_unresolved_rows']}. Qualified aggregate samples: {mixed['included_samples']}; excluded raw rows and reasons remain in all participation CSVs.

Maximum temporal angle: {mixed['max_temporal_angle_deg']:.6g} degrees; cross-condition angle: {mixed['max_condition_angle_deg']:.6g}; reference-span angle: {mixed['max_reference_angle_deg']:.6g}. Minimum adjacent gap: {mixed['min_gap']:.9g}; maximum moving-CSP update: {mixed['max_update']:.9g}. These are descriptive. No arbitrary persistence cutoff was introduced. Local attraction and dual identities cannot establish a globally reusable chemical block.

Dominant qualified species: {', '.join(row['species'] for row in mixed['dominant_species'][:8])}. Dominant reactions: {', '.join(row['reaction_id'] for row in mixed['dominant_reactions'][:8])}. Every ID maps to its canonical equation; the explicitly requested 332/333/380/381/344/345 and all CK/MK/NDK support are in `CK_MK_NDK_neighborhood.csv`. Directions shift toward translation/RF3 support at some times. Four modes are not four species.

Fixed ensemble metric, physical real-Schur initialization, Sylvester spectral projector and analytic moving-bundle CSP were independently recomputed from canonical source trajectories/Jacobians. Raw A/B/projectors/T/Q/J/Jdot/U/V are retained. External m4 span relation is an optional hash-verified cross-check; canonical recomputation has no absolute-path dependency. Finite-difference probe disagreements remain unresolved under frozen guards. No chemical deletion, effective reaction, fitted rate or reduced CRN was produced.

Chemistry-facing recommendation for human review only: investigate a conservation-preserving CK/MK module together with shared adenine/phosphate resources, retaining NDK and translation interfaces for explicit coupling analysis. This is a proposal, not an executed or scientifically accepted mapping. Global fixed chemical block presently justified: NO. Promotion: HUMAN_REVIEW_REQUIRED.
'''
 (DOC/'r4_mixed_csp_mode_diagnostic.md').write_text(mixedtext,encoding='utf-8',newline='\n')
 table='| Candidate | Type | Primary complete | Resolved / all gates | Scientific status |\n|---|---|---:|---:|---|\n'
 for sm in counts:table+=f'|{sm["candidate"]}|Chemical QSSA|{sm["conditions_primary_compared"]}/9|{sm["conditions_numerically_resolved"]}/9 ; {sm["conditions_passing_all_registered_gates"]}/9|{sm["scientific_status"]}|\n'
 table+=f'|MIXED_CSP_MODE_BLOCK|Geometric modes|198 samples|N/A|{mixed["scientific_status"]}|\n'
 metric_table='| Candidate | Worst state | Worst post0.05 state | Worst AA rate | Worst AA extent | Coupled closure | Graph defect (uM/s) |\n|---|---:|---:|---:|---:|---:|---:|\n'
 for sm in counts:
  mx=sm['maxima'];metric_table+=f'|{sm["candidate"]}|{mx["state"]:.9g}|{mx["post_state"]:.9g}|{mx["rate"]:.9g}|{mx["extent"]:.9g}|{mx["closure"]:.9g}|{sm["geometry_maxima"]["defect_max"]:.9g}|\n'
 historical_limits=grid.groupby('candidate')[['post_state','rate','extent','defect','nfev']].max()
 history_text='Historical21 versus split candidates (descriptive, identical scoring definitions): worst post-layer state error is '+', '.join(f'{n}={historical_limits.loc[n,"post_state"]:.9g}' for n in ['historical_R3_21','R4_GLYRS_ONLY','R4_METRS_ONLY'])+'. Maximum primary RHS calls are '+', '.join(f'{n}={int(historical_limits.loc[n,"nfev"])}' for n in ['historical_R3_21','R4_GLYRS_ONLY','R4_METRS_ONLY'])+'. GlyRS-only improves post-layer error and reduces solver burden; this does not repair its full-window state/rate failures or resolve balance uncertainty. MetRS-only retains essentially the historical worst post-layer error.\n'
 compare=f'''# R4 fast-block comparison

{table}
{metric_table}
{history_text}
The CSV keeps chemical QSSA gate metrics separate from geometric mode metrics. N/A is explicit; no common meaningless PASS/FAIL column is used. Detailed per-condition raw gates, uncertainties, balance, solver burden, branch geometry and lag remain in result.json and certificate tables. Side-by-side 21-state/GlyRS/MetRS comparisons are in `historical_r3_comparison/side_by_side.csv`.

Causal family outcome: **{causal}**. The four logical pass/fail alternatives cannot be asserted while a family lacks resolved full-domain tests. If any raw errors improve, that alone does not establish all-gate support. No inference that aminoacylation QSSA is impossible is authorized. Historical R3 remains unchanged; its recorded nine-condition rejection is not retroactively reclassified by new uncertainty diagnostics.

Closure, defect and lag for the historical21 block were independently recomputed as diagnostic comparison, without h1 or higher-order correction. A smaller algebraic system can still carry a large moving-manifold defect. CSP span rotations and participation are not deletion authority.

Recommendation: retain all failed/unresolved work. Resolve numerical representation and tolerance-convergence qualifications before any new scientific transition; human review must distinguish initial-layer failures from post-layer errors and chemistry-facing CSP mapping. No reduced core, final winner, fitted rate, transcription/GUV coupling, push or main merge.
'''
 (DOC/'r4_fast_block_comparison.md').write_text(compare,encoding='utf-8',newline='\n')
 summary=f'''# R4 fast-block screen summary — 2026-10-07

Actual parent main: `{REG['parent_main_sha']}`. Execution approval is for testing only. Execution status: COMPLETED_BOUNDED_SCREEN. Numerical and scientific statuses are per candidate/condition below; human promotion: HUMAN_REVIEW_REQUIRED.

{table}
{metric_table}
{history_text}
Frozen source, parameters, initial values, acceptance criteria and all pre-existing R1/R2/R3/H4/H5 evidence are individually checked against the 1,644-file parent snapshot. See the independent verifier for the final measured result. External audit: all161 registered outputs verified; used files have exact hashes; directory read only. Fresh baseline source agreement: {json.loads((OUT/'source_sanity/baseline_agreement.json').read_text())['state_scaled_max_difference']:.6g} trajectory-scaled.

Primary domain is exactly the nine completed historical source conditions. All R4 reduced primary/uncertainty solves are fresh. Numerical noncompletion is UNSCORED; relevant uncertainty >10% of tier budget takes precedence over raw gate pass/failure. Full initial layers, all241 state errors and all968 gross directed rate/extent channels are retained wherever a primary comparison completes.

Both families have nine resolved FAIL_STATE and nine resolved FAIL_RATE tier outcomes. Each has eight FAIL_EXTENT and one PASS_REGISTERED_TIER extent outcome (its own low-enzyme condition); all nine balance tiers remain NUMERICALLY_UNRESOLVED. Native reporting-only failures in six records were recovered from hash-bound completed numerical arrays; raw records/tracebacks and all failed arithmetic attempts remain unchanged. Review classification is in derived_review_result.json.

Causal family outcome: {causal}. No supported causal conclusion about combined-block/shared-resource geometry is available unless both family screens are numerically decidable. Mixed diagnostic: {mixed['scientific_status']}; span variation reaches {mixed['max_temporal_angle_deg']:.6g} degrees temporally and {mixed['max_condition_angle_deg']:.6g} across conditions. Strong CK/MK participation requires human chemistry-facing review; no global fixed block is approved.

Seven figures, each with underlying CSV, are under `figures/`. Inspect individual certificates, comparison, per-condition result/uncertainty/geometry tables and the hash-bound manifest. The derived evidence graph is navigation only and never replaces source evidence.

Unresolved questions: whether numerical uncertainty can be controlled at the fixed balance budget; whether family-only post-layer accuracy survives every coupled gate; whether moving mode-space support can be mapped to a conservation-preserving chemical module. Recommendations are for human review only. R3_ADVERSE is unchanged, unscored and not rerun. All968 mechanistic decisions remain PENDING. PURE_reduced_core remains NOT_VALIDATED. No old21 higher-order correction or automatic next stage was executed. No push or main merge.
'''
 (DOC/'r4_fast_block_summary.md').write_text(summary,encoding='utf-8',newline='\n')
 # Derived provenance navigation with freshness fingerprints.
 nodes=[{'id':'parent_main','kind':'source_commit','sha':REG['parent_main_sha'],'evidence_status':'EXTRACTED','authority':'CANONICAL_SOURCE'},{'id':'authorization','kind':'human_scope','evidence_status':'EXTRACTED','path':'docs/reduction/r4_fast_block_human_authorization_20261007.md','sha256':sha(DOC/'r4_fast_block_human_authorization_20261007.md')},{'id':'preregistration','kind':'frozen_protocol','evidence_status':'EXTRACTED','path':'docs/reduction/r4_fast_block_candidates_v1.json','sha256':sha(DOC/'r4_fast_block_candidates_v1.json')}]
 edges=[]
 for sm in counts:
  cid='R4_'+sm['candidate'].upper()+'_ONLY';nodes.append({'id':cid,'kind':'tested_candidate','evidence_status':'EXTRACTED','scientific_status':sm['scientific_status'],'promotion':'HUMAN_REVIEW_REQUIRED'});edges.extend([{'from':'authorization','to':cid,'relation':'authorizes_testing_only'},{'from':'preregistration','to':cid,'relation':'defines_domain_and_gates'}])
 for n in ['source_reuse_verification.json','screen_summary.json','fast_block_comparison.csv','mixed_csp_mode_block/result.json']:
  nodes.append({'id':n,'kind':'derived_evidence','path':'results/reduction/r4_fast_block_screen/'+n,'sha256':sha(OUT/n),'evidence_status':'EXTRACTED','freshness':'VERIFY_AGAINST_MANIFEST'});edges.append({'from':'parent_main','to':n,'relation':'derived_from'})
 nodes.append({'id':'causal_interpretation','kind':'inference','evidence_status':'AMBIGUOUS','status':causal});edges.append({'from':'fast_block_comparison.csv','to':'causal_interpretation','relation':'limits_inference'})
 write_json(OUT/'evidence_graph.json',{'status':'DERIVED_NAVIGATION_NOT_SOURCE_AUTHORITY','nodes':nodes,'edges':edges,'freshness_rule':'Recompute SHA-256 against final manifest before use.'})
 manifest();print('R4 review package finalized',flush=True)

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--historical-geometry',action='store_true');parser.add_argument('--manifest-only',action='store_true');a=parser.parse_args()
 if a.historical_geometry:historical_geometry()
 elif a.manifest_only:manifest()
 else:finish()
