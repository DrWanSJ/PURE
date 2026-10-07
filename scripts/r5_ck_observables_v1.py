"""Additional stored CK state/net-conversion/conservation observables."""
from r5_ck_partial_equilibrium_runtime_v1 import *
def main():
 checked_registration();r=CKRuntime();dest=OUT/'ck';a=np.load(dest/'baseline_comparison.npz');t=a['times'];full=a['full'];sc=a['state_scale'];laws=np.array([[float(v.get(i,0)) for i in range(241)] for v in r.source.laws]);mask=t>=json.loads((dest/'initial_layer_definition.json').read_text())['switch_at_eta1_s']
 rows=[];lawrows=[]
 for name in ['outer','hybrid']:
  x=a[name]
  for i,n in enumerate(r.source.species):rows.append({'approximation':name,'species':n,'full_window_max_scaled_error':float(max(abs(x[:,i]-full[:,i]))/sc[i]),'post_startup_max_scaled_error':float(max(abs(x[mask,i]-full[mask,i]))/sc[i]),'post_0p05_max_scaled_error':float(max(abs(x[t>=.05,i]-full[t>=.05,i]))/sc[i]),'max_absolute_error':float(max(abs(x[:,i]-full[:,i])))})
  for j,law in enumerate(r.source.laws):
   drift=np.array([math.fsum(float(v)*(float(xx[i])-float(r.x0[i])) for i,v in law.items()) for xx in x]);src=np.array([math.fsum(float(v)*(float(xx[i])-float(r.x0[i])) for i,v in law.items()) for xx in full])
   lawrows.append({'approximation':name,'law_id':r.source.cert['law_ids'][j],'scope':'SOURCE_GENERAL_EXACT_CONSERVATION','reduced_max_absolute_drift':float(max(abs(drift))),'source_max_absolute_drift':float(max(abs(src)))})
 write_csv(dest/'baseline_all_species_comparison.csv',rows);write_csv(dest/'baseline_source_general_conservation.csv',lawrows)
 # Canonical exact identity: Bdot = -v338+v339, no other slow columns affect B.
 idx={re['id']:j for j,re in enumerate(r.source.reactions)};brow=r.T[2]@r.S
 expected=np.zeros(968);expected[idx['re0000000338']]=-1;expected[idx['re0000000339']]=1;assert np.array_equal(brow,expected)
 net=[]
 for i,ti in enumerate(t):
  source_net=r.z0[2]-float(r.T[2]@full[i])
  for name in ['outer','hybrid']:
   reduced_net=r.z0[2]-float(r.T[2]@a[name][i]);net.append({'approximation':name,'time_s':ti,'source_net_conversion_from_B_loss':source_net,'reduced_net_conversion_from_B_loss':reduced_net,'absolute_difference':abs(source_net-reduced_net),'interpretation':'NET338_MINUS339_EXTENT_FROM_EXACT_TOTAL_IDENTITY;NOT_GROSS_LEDGER_CLAIM'})
 write_csv(dest/'energy_regeneration_net_conversion.csv',net)
 sm=json.loads((dest/'eta_scan_summary.json').read_text());sm['original_eta1_all241_post_startup_max_scaled']={name:max(v['post_startup_max_scaled_error'] for v in rows if v['approximation']==name) for name in ['outer','hybrid']};sm['original_eta1_all241_post_0p05_max_scaled']={name:max(v['post_0p05_max_scaled_error'] for v in rows if v['approximation']==name) for name in ['outer','hybrid']};sm['source_general_conservation_drift_max']=max(v['source_max_absolute_drift'] for v in lawrows);sm['reduced_source_general_conservation_drift_max']=max(v['reduced_max_absolute_drift'] for v in lawrows);sm['net_conversion_extent_max_absolute_difference']=max(v['absolute_difference'] for v in net);sm['strict_physical_domain_not_proven']='Some reconstructed unused/zero-inventory species have retained tiny negative roundoff; hybrid eta0.3 minimum -2.18e-11. No clipping or physical-domain promotion.'
 write_json(dest/'eta_scan_summary.json',sm);print(sm)
if __name__=='__main__':main()
