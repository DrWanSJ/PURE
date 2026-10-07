"""Independent implicit-root directional probes; diagnostic, no new gate."""
from r4_fast_block_common_v1 import *
rows=[]
for family in ['GlyRS','MetRS']:
 r=R4FamilyRuntime(family)
 for c in REG['conditions']:
  name=c['condition_id'];_,full=source_data(name);x0=condition_initial(r.source,name)
  for i in [50,100,200]:
   z=r.T@full[i];rr=r.solve_fast(z,x0,seed=full[i,r.q_index]);q=rr['q'];x=rr['state'];J=(r.S@rate_jacobian(r.source,x)).toarray();Gq=J[r.q_index]@r.D;Gz=J[r.q_index]@r.Xz;Dh=-np.linalg.solve(Gq,Gz)
   d=np.sin(np.arange(len(z))+.73)*np.minimum(abs(z),.1);d[abs(z)<1e-7]=0
   for h in [1e-4,1e-5,1e-6]:
    qp=r.solve_fast(z+h*d,x0,seed=q);qm=r.solve_fast(z-h*d,x0,seed=q);finite=(qp['q']-qm['q'])/(2*h);analytic=Dh@d
    rows.append({'family':family,'condition':name,'sample_index':i,'step':h,'both_physical_roots':qp['valid_local_root'] and qm['valid_local_root'],'relative_l2_error':float(np.linalg.norm(finite-analytic)/max(np.linalg.norm(analytic),1e-10)),'maximum_abs_difference':float(max(abs(finite-analytic))),'scientific_gate':'NONE_DIAGNOSTIC_CROSSCHECK_ONLY'})
write_csv(OUT/'independent_implicit_derivative_crosscheck.csv',rows)
write_json(OUT/'independent_implicit_derivative_crosscheck.json',{'probes':len(rows),'all_roots_physical':all(r['both_physical_roots'] for r in rows),'worst_relative_error':max(r['relative_l2_error'] for r in rows),'median_relative_error':float(np.median([r['relative_l2_error'] for r in rows])),'role':'Independent root-FD corroboration of canonical Dh formula; no added scientific threshold'})
print('Independent implicit derivative probes',len(rows),flush=True)
