"""Separate fast-block condition number from actual eigenseparation diagnostics."""
from r4_fast_block_common_v1 import *
from scipy.linalg import eigvals
import pandas as pd
p=OUT/'mixed_csp_mode_block';f=pd.read_csv(p/'m4_geometry.csv');separations=[];proxies=[]
for row in f.itertuples():
 a=np.load(p/(row.condition+'_m4_bases.npz'));T=a[str(row.sample_index)+'_T'];J=a[str(row.sample_index)+'_J'];ef=eigvals(T[:4,:4]);es=eigvals(T[4:,4:]);sep=float(np.min(abs(ef[:,None]-es[None,:])));separations.append(sep);proxies.append(float(np.linalg.norm(J,'fro')/sep) if sep>0 else float('inf'))
f['fast_schur_block_condition_number']=f['gap_conditioning'];f['minimum_fast_slow_eigenvalue_separation_s_inverse']=separations;f['gap_conditioning']=proxies;f['gap_conditioning_definition']='NORM_J_FRO_OVER_MIN_EIGENSEPARATION_PROXY_NOT_SYLVESTER_OPERATOR_CONDITION';f.to_csv(p/'m4_geometry.csv',index=False)
write_json(p/'gap_descriptor_provenance.json',{'meaning':'The original gap_conditioning value was cond(T_fast), now explicitly preserved as fast_schur_block_condition_number. Added eigenseparation and a clearly labeled diagnostic ratio. No guard, matrix, participation, exclusion or scientific status changed.','source_basis_npz_sha256':{q.name:sha(q) for q in p.glob('*_m4_bases.npz')},'scientific_threshold_added':False})
print('m4 gap descriptors made explicit',flush=True)
