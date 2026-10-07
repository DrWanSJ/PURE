"""CK kinematic net currents from stored R5 arrays and canonical stoichiometry."""
from r5_common_v1 import ROOT, write_json, write_csv
from r5_ck_partial_equilibrium_runtime_v1 import CKRuntime, FAST_IDS
from verify_r5_mechanism_first_v1 import independent_canonical
import numpy as np
import json
OUT=ROOT/'results/reduction/r5c_corrigendum'

def calculate():
    r=CKRuntime(); species,rx,S,rhs=independent_canonical(); ix={n:i for i,n in enumerate(species)}
    fast=[next(j for j,re in enumerate(rx) if re['id']==rid) for rid in FAST_IDS]
    forward=[]; reverse=[]; orientation=[]
    for a,b in zip(fast[::2],fast[1::2]):
        assert np.array_equal(S[:,a],-S[:,b])
        # Orient toward production of the bound independent fast coordinate.
        qcol=S[r.qix,a]; active=np.flatnonzero(qcol)
        assert len(active)==1
        f,rev=(a,b) if qcol[active[0]]>0 else (b,a)
        forward.append(f);reverse.append(rev);orientation.append({'forward':rx[f]['id'],'reverse':rx[rev]['id'],'canonical_q_column':S[r.qix,f].tolist()})
    N=S[np.ix_(r.qix,forward)]; rank=int(np.linalg.matrix_rank(N)); assert rank==len(forward)
    a=np.load(ROOT/'results/reduction/r5_mechanism_first/ck/baseline_comparison.npz'); t=a['times']; full=a['full']
    direct_rates=np.array([rhs(x)[1] for x in full]); direct=direct_rates[:,forward]-direct_rates[:,reverse]
    scale=np.maximum(np.max(abs(direct[t>=.05]),axis=0),1e-6)
    samples=sorted({int(np.argmin(abs(t-target))) for target in [0,1e-4,1e-3,.01,.05,.1,1,10,100,1000]})
    rows=[]; fdrows=[]; maxidentity=0.; maxequilibrium=0.
    for label in ['source_projected_h0','outer','hybrid']:
        trajectory=full if label=='source_projected_h0' else a[label]
        for i in samples:
            z=r.T@trajectory[i]; x,q,phi,dh=r.manifold(z,True); v=rhs(x)[1]; vs=v.copy();vs[fast]=0
            nonfast=S@vs; zdot=r.T@nonfast; manifold=dh@zdot; qnonfast=nonfast[r.qix]
            current=np.linalg.solve(N,manifold-qnonfast); identity=N@current+qnonfast-manifold; maxidentity=max(maxidentity,float(max(abs(identity))))
            eq=v[forward]-v[reverse]; maxequilibrium=max(maxequilibrium,float(max(abs(eq))))
            fullaction=phi@zdot-(nonfast+S[:,forward]@current)
            for j in range(3):
                step=1e-5*max(1.,abs(z[j])); delta=np.eye(212)[j]*step
                fd=(r.manifold(z+delta)[1]-r.manifold(z-delta)[1])/(2*step)
                fdrows.append({'approximation':label,'sample_index':i,'coordinate':r.labels[j],'step':step,'max_absolute_error':float(max(abs(fd-dh[:,j]))),'scaled_error':float(max(abs(fd-dh[:,j]))/max(1.,max(abs(dh[:,j]))))})
            for pair in range(2):
                rows.append(dict(approximation=label,time_s=float(t[i]),sample_index=i,window='INITIAL_LAYER_OR_STARTUP' if t[i]<.05 else 'POST_0p05',pair=pair,forward=rx[forward[pair]]['id'],reverse=rx[reverse[pair]]['id'],z=json.dumps(z.tolist()),z_labels=json.dumps(r.labels),h0=json.dumps(q.tolist()),z_dot=json.dumps(zdot.tolist()),Dh0=json.dumps(dh.tolist()),q_dot_manifold=float(manifold[pair]),q_dot_nonfast=float(qnonfast[pair]),reconstructed_net_current=float(current[pair]),direct_full_model_net_current=float(direct[i,pair]),absolute_error=float(abs(current[pair]-direct[i,pair])),relative_error=float(abs(current[pair]-direct[i,pair])/max(abs(direct[i,pair]),1e-6)),fixed_post_layer_scale=float(scale[pair]),scaled_error=float(abs(current[pair]-direct[i,pair])/scale[pair]),h0_forward_gross=float(v[forward[pair]]),h0_reverse_gross=float(v[reverse[pair]]),h0_net=float(eq[pair]),identity_error=float(max(abs(identity))),full_state_tangent_identity_error=float(max(abs(fullaction))),interpretation='RECONSTRUCTABLE_NET_CURRENT;FINITE_ETA_ACCURACY_DESCRIPTIVE;STARTUP_NOT_OUTER_VALIDATION'))
    summary={'N_qf':N.tolist(),'rank':rank,'nullspace_dimension':len(forward)-rank,'orientations':orientation,'q_coordinates':[species[i] for i in r.qix],'unique_net_currents':True,'identity_max_absolute_error':maxidentity,'full_state_tangent_identity_max_error':max(v['full_state_tangent_identity_error'] for v in rows),'Dh0_fd_scaled_error_max':max(v['scaled_error'] for v in fdrows),'h0_net_roundoff_max':maxequilibrium,'post_0p05_representative_comparison':{label:{'max_absolute_error':max(v['absolute_error'] for v in rows if v['approximation']==label and v['time_s']>=.05),'max_scaled_error':max(v['scaled_error'] for v in rows if v['approximation']==label and v['time_s']>=.05)} for label in ['source_projected_h0','outer','hybrid']},'comparison_is_not_an_accuracy_gate':True,'no_first_order_model_built':True}
    assert summary['identity_max_absolute_error']<1e-9 and summary['Dh0_fd_scaled_error_max']<1e-7
    return rows,fdrows,summary

if __name__=='__main__':
    rows,fd,summary=calculate();write_csv(OUT/'ck_fast_current_reconstruction.csv',rows);write_csv(OUT/'ck_Dh0_finite_difference.csv',fd);write_json(OUT/'ck_fast_current_summary.json',summary);print(summary)
