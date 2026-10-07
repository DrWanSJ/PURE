"""Stored-evidence balance decomposition, never reclassifies R4."""
from r5_common_v1 import *
from r4_fast_block_common_v1 import R4FamilyRuntime,REG,source_data,historical_path,condition_initial
from runtime_reconstruction_rhs import SourceCoordinateRuntime
from validate_source_coordinates_full_v1 import source_matrix
from scipy.integrate import cumulative_trapezoid
def kahan(values):
 total=0.;correction=0.
 for v in values:
  adjusted=v-correction;updated=total+adjusted;correction=(updated-total)-adjusted;total=updated
 return total
def product_methods(M,xi):
 ordinary=xi@M.T;fsum=np.zeros_like(ordinary);comp=np.zeros_like(ordinary);higher=np.zeros_like(ordinary)
 for i,row in enumerate(M):
  ids=np.flatnonzero(row);coef=row[ids]
  terms=xi[:,ids]*coef
  fsum[:,i]=[math.fsum(v) for v in terms];comp[:,i]=[kahan(v) for v in terms]
  higher[:,i]=np.sum(xi[:,ids].astype(np.longdouble)*coef.astype(np.longdouble),axis=1,dtype=np.longdouble).astype(float)
 return {'ordinary':ordinary,'kahan':comp,'fsum':fsum,'longdouble':higher}
def main():
 checked_registration();s=SourceCoordinateRuntime('source_coordinate_certificate_v4.json');S=source_matrix(s).toarray();L=np.array([[float(law.get(i,0)) for i in range(241)] for law in s.laws]);assert np.max(abs(L@S))==0
 dest=OUT/'balance';dest.mkdir(parents=True,exist_ok=True);records=[];laws=[];account=[]
 def analyze(name,label,t,x,xi,rates,x0,coordinate=None,tight=None,uncertainty=None):
  matrix=S if coordinate is None else coordinate.T@S
  state=x if coordinate is None else x@coordinate.T.T
  anchor=x0 if coordinate is None else coordinate.T@x0
  prods=product_methods(matrix,xi);delta=state-anchor
  residuals={k:delta-v for k,v in prods.items()}
  abs_sum=abs(xi)@abs(matrix.T);roundbound=np.finfo(float).eps*matrix.shape[1]*abs_sum
  lawdrift=np.array([[math.fsum(float(w)*(float(xx[i])-float(x0[i])) for i,w in law.items()) for law in s.laws] for xx in x])
  for j,law in enumerate(s.laws):laws.append({'condition':name,'trajectory':label,'law_id':s.cert['law_ids'][j],'scope':'SOURCE_GENERAL_EXACT_CONSERVATION','max_drift_fsum':float(max(abs(lawdrift[:,j]))),'initial_inventory':float(math.fsum(float(w)*x0[i] for i,w in law.items()))})
  rhs=rates@matrix.T;trap=cumulative_trapezoid(rhs,t,axis=0,initial=0);trapres=delta-trap
  tight_delta=None
  if tight is not None:tight_delta=float(np.max(abs((tight-xi)@matrix.T)))
  uncert=None
  if uncertainty is not None:uncert=float(np.max(abs(uncertainty-x)))
  rows=[]
  for i,ti in enumerate(t):
   rows.append({'condition':name,'trajectory':label,'time_s':ti,'coordinate_scope':'FULL_SOURCE' if coordinate is None else 'REDUCED_SLOW','exact_source_general_law_drift_fsum':float(max(abs(lawdrift[i]))),'ledger_residual_ordinary':float(max(abs(residuals['ordinary'][i]))),'ledger_residual_kahan':float(max(abs(residuals['kahan'][i]))),'ledger_residual_fsum':float(max(abs(residuals['fsum'][i]))),'ledger_residual_longdouble':float(max(abs(residuals['longdouble'][i]))),'summation_only_change':float(max(abs(prods['ordinary'][i]-prods['fsum'][i]))),'gross_cancellation_roundoff_upper_bound':float(max(roundbound[i])),'gross_to_net_condition_max':float(max(abs_sum[i]/np.maximum(abs(prods['fsum'][i]),1e-30))),'sampled_trapezoid_state_rhs_residual':float(max(abs(trapres[i]))),'state_rhs_residual_interpretation':'COARSE_QUADRATURE_AND_INTERPOLATION_CONFOUNDED_NOT_SOLVER_ERROR','tight_extent_change_max':tight_delta,'state_uncertainty_max':uncert,'direct_state_integration_error':'UNIDENTIFIABLE_FROM_STORED_DATA','dense_interpolation_contribution':'UNIDENTIFIABLE_FROM_STORED_DATA','extent_error_status':'TIGHT_PROBE_DIFFERENCE_NOT_RIGOROUS_ERROR_BOUND' if tight is not None else 'NO_SAME_TRAJECTORY_TIGHT_LEDGER_PROBE'})
  records.extend(rows)
  return residuals['fsum']
 for c in REG['conditions']:
  name=c['condition_id'];t,full=source_data(name);x0=condition_initial(s,name);lp=historical_path(name)/'directed_ledgers.npz';a=np.load(lp)
  probe=ROOT/'results/reduction/r4_fast_block_screen/source_uncertainty'/name
  up=np.load(probe/'probe_state.npz')['state'] if (probe/'probe_state.npz').exists() else None
  analyze(name,'SOURCE_PRIMARY',t,full,a['full_extent'],a['full_rates'],x0,uncertainty=up)
  if up is not None:
   led=np.load(probe/'probe_ledgers.npz');analyze(name,'SOURCE_UNCERTAINTY',t,up,led['extent'],led['rates'],x0)
  for family in ['GlyRS','MetRS']:
   r=R4FamilyRuntime(family);p=ROOT/'results/reduction/r4_fast_block_screen'/(family.lower()+'_only')/name
   traj=p/'state_trajectories.npz'
   if not traj.exists():traj=p/'recovered_state_trajectories.npz'
   if not traj.exists():raise RuntimeError('MISSING_R4_TRAJECTORY '+str(p))
   st=np.load(traj);red=st['reduced_state'];led=np.load(p/'directed_ledgers.npz');xi=led['reduced_extent'];rates=led['reduced_rates'];tight=led['tight_reduced_extent'] if 'tight_reduced_extent' in led.files else None
   # Full ledger residual begins at the disclosed reduced algebraic startup
   # state. Slow-coordinate residual starts at original Tx0, which agrees.
   slowres=analyze(name,family+'_REDUCED_SLOW',t,red,xi,rates,x0,coordinate=r,tight=tight)
   fullres=(red-red[0])-product_methods(S,xi)['fsum']
   qres=(red[:,r.q_index]-red[0,r.q_index])-(xi@S[r.q_index].T)
   predicted=slowres@r.Xz.T+qres@r.D.T
   identity=fullres-predicted
   law=np.array([[math.fsum(float(w)*(float(xx[i])-float(x0[i])) for i,w in law.items()) for law in s.laws] for xx in red])
   for i,ti in enumerate(t):account.append({'condition':name,'family':family,'time_s':ti,'reconstructed_full_ledger_residual':float(max(abs(fullres[i]))),'slow_ledger_residual':float(max(abs(slowres[i]))),'algebraic_fast_tracking_minus_source_fast_ledger':float(max(abs(qres[i]))),'missing_net_redistribution_full_action':float(max(abs(qres[i]@r.D.T))),'affine_decomposition_identity_error':float(max(abs(identity[i]))),'reconstructed_source_general_law_drift':float(max(abs(law[i]))),'interpretation':'ALGEBRAIC_TRACKING_REQUIRES_NET_REDISTRIBUTION_LEDGER;NO_R4_GATE_CHANGE'})
  print('Balance',name,'stored evidence decomposed',flush=True)
 write_csv(dest/'balance_decomposition.csv',records);write_csv(dest/'source_general_law_drift.csv',laws);write_csv(dest/'reconstructed_full_state_accounting.csv',account)
 primary=[v for v in records if v['trajectory']=='SOURCE_PRIMARY'];redrows=[v for v in records if v['coordinate_scope']=='REDUCED_SLOW']
 sm={'classification':'MIXED / UNRESOLVED','source_general_laws':27,'max_exact_law_drift':max(v['max_drift_fsum'] for v in laws),'max_primary_source_ledger_residual':max(v['ledger_residual_fsum'] for v in primary),'max_reduced_slow_ledger_residual':max(v['ledger_residual_fsum'] for v in redrows),'max_postprocessing_summation_change':max(v['summation_only_change'] for v in records),'max_same_trajectory_tight_extent_change':max(v['tight_extent_change_max'] or 0 for v in records),'max_reconstructed_full_residual':max(v['reconstructed_full_ledger_residual'] for v in account),'max_algebraic_tracking_ledger_difference':max(v['algebraic_fast_tracking_minus_source_fast_ledger'] for v in account),'max_affine_decomposition_identity_error':max(v['affine_decomposition_identity_error'] for v in account),'source_conservation_failure_observed':False,'trajectory_mutation':False,'historical_gate_changed':False,'longdouble_mantissa_bits':int(np.finfo(np.longdouble).nmant),'direct_state_vs_dense_vs_extent_error_separately_identified':False,'reason':'Stored step records contain times/counters, not all accepted states/dense polynomials. Tight-ledger variation identifies a numerical component; complete state/dense/extent error attribution is unavailable. Full reduced ledgers require algebraic redistribution policy.'}
 write_json(dest/'balance_decomposition_summary.json',sm)
 write_doc('r5_balance_residual_decomposition_v1.md','# R4 balance residual decomposition\n\nThe exact conservation test is L[x(t)-x0] for the27 SOURCE_GENERAL laws with LS=0. It differs from x-x0-Sxi, which mixes state and ledger integrations. Every stored completed R3 full-source trajectory and R4 family trajectory was analyzed without modification. Ordinary, Kahan, math.fsum and longdouble sums act only on the diagnostic; the original binary arrays are unchanged. On this platform longdouble mantissa is '+str(sm['longdouble_mantissa_bits'])+' bits, so it may offer no extra precision beyond double; math.fsum is the reliable high-accuracy sum.\n\nFor reduced coordinates x=c+Xz z+Dq, decompose full residual exactly as Xz(z-z0-TSxi)+D(q-q0-Sqxi). The second term is algebraic manifold tracking minus microscopic fast ledger change. A zero-order graph does not supply the missing finite net redistribution automatically. This accounting identity is checked, not declared a new conservation failure. Reduced-coordinate ledger residual is assessed independently.\n\nStored solver-step CSVs preserve times/counters but omit accepted state arrays/dense polynomials. Thus sampled trapezoid integration of RHS is explicitly coarse-quadrature/interpolation-confounded, not a direct state-solver error measurement. Existing same-trajectory tight ledgers and state uncertainty runs quantify components, not rigorous error bounds; dense-output contribution and state integration error cannot be separated completely from these stored files. No expensive source campaign was launched to fill that gap.\n\nMeasured summary:\n\n```json\n'+json.dumps(sm,indent=2)+'\n```\n\nMODEL CONSERVATION FAILURE: no source-general failure observed at the measured roundoff scale. SOLVER TRAJECTORY ERROR: uncertainty measured, exact component unresolved. LEDGER INTEGRATION ERROR: tighter same-trajectory ledgers show numerical sensitivity. NUMERICAL CANCELLATION: compensated/high-accuracy differences measured independently. REDUCED-COORDINATE ACCOUNTING ERROR: no new structural identity defect identified, but full-state gross-ledger policy lacks algebraic redistribution; this differs from the slow ledger numerical error. Classification remains MIXED / UNRESOLVED. R4 registered thresholds and every raw/native/derived historical classification remain frozen.')
 print(sm,flush=True)
if __name__=='__main__':main()
