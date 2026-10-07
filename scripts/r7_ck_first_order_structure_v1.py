"""Registered exact-family, graph, derivative and formal truncation diagnostics."""
from r7_ck_h1_v1 import *
from r5_ck_partial_equilibrium_runtime_v1 import fast_rhs, fast_jac
from scipy.optimize import brentq

def diagnose(name):
    r=FirstOrderCK(name)
    with np.load(ROOT/'results/reduction/r6_ck_validation/per_condition'/name/'run_001/comparison.npz') as f:a={k:f[k].copy() for k in f.files}
    hs=[];scales=[];ds=[];js=[]
    for k,(t,x) in enumerate(zip(a['times'],a['source'])):
        dz=r.T@x-r.z0;c=r.core(dz);xf,_,_,_=r.manifold_delta(dz,True)
        pcheck=brentq(lambda p:p+np.sum(c['z'][:2]*p/(500+p))-c['z'][2],0,max(0,c['z'][2]),xtol=1e-11) if c['z'][2]>0 else 0
        qcheck=c['z'][:2]*pcheck/(500+pcheck)
        dh=r.dh1(c,c['F']);w=c['F']/max(1,np.linalg.norm(c['F'],np.inf));factor=max(1,np.linalg.norm(c['F'],np.inf))
        hcs=np.imag(r.core(dz.astype(complex)+1e-25j*w)['h1'])/1e-25*factor
        delta=1e-3
        coarse=(r.core(dz+delta*w)['h1']-r.core(dz-delta*w)['h1'])/(2*delta)*factor
        fine=(r.core(dz+delta/2*w)['h1']-r.core(dz-delta/2*w)['h1'])/delta*factor
        fd=(4*fine-coarse)/3
        re=np.max(abs(dh-hcs))/max(1e-12,np.max(abs(dh)),np.max(abs(hcs)))
        fe=np.max(abs(dh-fd))/max(1e-12,np.max(abs(dh)),np.max(abs(fd)))
        x1,net,_,_,j1=r.observables(dz)
        _,jold,*_=FormalCK.reduced_observables(r,dz)
        res=c['J']@c['h1']+c['G0']-c['H']@c['F']
        signed=np.array([c['z'][0]-x1[r.qix[0]],c['z'][1]-x1[r.qix[1]],c['z'][2]-x1[r.qix].sum(),*x1[r.qix]])
        sing=np.linalg.svd(c['J'],compute_uv=False)
        correction=np.linalg.norm(c['h1']);qscale=max(np.linalg.norm(c['q']),1e-6);tscale=max(np.linalg.norm(c['z'][:3]),1e-6)
        hs.append(dict(condition=name,sample_index=k,time_s=float(t),h0_CP=float(c['q'][0]),h0_CP_ADP=float(c['q'][1]),h1_CP=float(c['h1'][0]),h1_CP_ADP=float(c['h1'][1]),Gq_condition=float(np.linalg.cond(c['J'])),Gq_min_singular=float(sing[-1]),h0_independent_error=float(np.max(abs(c['q']-qcheck))),h0_frozen_error=float(np.max(abs(c['x']-xf))),critical_residual=float(np.max(abs(fast_rhs(c['q'],c['z'][:3])))),h1_equation_residual=float(np.max(abs(res)))))
        scales.append(dict(condition=name,sample_index=k,time_s=float(t),eta=1,correction_norm=float(correction),fast_state_scale=float(qscale),fast_total_scale=float(tscale),correction_over_fast_state=float(correction/qscale),correction_over_fast_total=float(correction/tscale),min_physical_margin=float(signed.min()),distance_outside_domain=float(max(0,-signed.min())),Gq_condition=float(np.linalg.cond(c['J'])),Gq_min_singular=float(sing[-1]),singular_distance_lower_bound=float(sing[-1]),not_small_flag=bool(correction/qscale>=1)))
        ds.append(dict(condition=name,sample_index=k,time_s=float(t),analytic_dh1_flow_CP=float(dh[0]),analytic_dh1_flow_CP_ADP=float(dh[1]),complex_step_CP=float(hcs[0]),complex_step_CP_ADP=float(hcs[1]),complex_step_relative_error=float(re),richardson_relative_error=float(fe),richardson_self_sensitivity=float(np.max(abs(fine-coarse))),derivative_scale=float(max(np.max(abs(dh)),1e-12)),Gq_condition=float(np.linalg.cond(c['J']))))
        family=[]
        for eta in [0.25,1,2]:
            fx=r.full_rhs(0,c['x'],eta);family.append(max(np.max(abs(r.T@fx-c['F'])),np.max(abs(fx[r.qix]-(fast_rhs(c['q'],c['z'][:3])/eta+c['G0'])))))
        rhs=r.reduced_rhs_delta(0,dz);direct=c['F']+r.TS@r.derivative_rates(c['x'],r.D@c['h1'])
        js.append(dict(condition=name,sample_index=k,time_s=float(t),j0_CP=float(c['j0'][0]),j0_CP_ADP=float(c['j0'][1]),j1_CP=float(j1[0]),j1_CP_ADP=float(j1[1]),j0_R6_max_abs_error=float(np.max(abs(c['j0']-jold[r.fast_channels]))),j1_independent_CS_residual=float(np.max(abs(j1-(hcs+c['H']@c['F1']-r.Q@c['v1'])))),eta_family_identity_error=float(max(family)),formal_rhs_identity_error=float(np.max(abs(rhs-direct))),Nqf_rank=int(np.linalg.matrix_rank(r.Nqf))))
    # Full Jacobian comparison on three representative physical slow states.
    jacchecks=[]
    for k in [int(np.flatnonzero(a['times']>=r.switch)[0]),len(a['times'])//2,len(a['times'])-1]:
        dz=a['reduced_slow'][k]-r.z0
        J=r.reduced_jac_delta(0,dz).toarray();Jcs=np.empty_like(J)
        for j in range(212):
            e=np.zeros(212,dtype=complex);e[j]=1e-25j
            Jcs[:,j]=np.imag(r.reduced_rhs_delta(0,dz.astype(complex)+e))/1e-25
        err=np.max(abs(J-Jcs))/max(1e-12,np.max(abs(Jcs)))
        jacchecks.append(dict(condition=name,sample_index=k,time_s=float(a['times'][k]),relative_error=float(err)))
    return hs,scales,ds,js,jacchecks

def main():
    checked_binding();tables=[[] for _ in range(5)]
    for name in CONDITIONS:
        for table,data in zip(tables,diagnose(name)):table.extend(data)
        print(name,'registered structure checks complete',flush=True)
    for path,table in zip(['h1_samples.csv','h1_scale_diagnostics.csv','dh1_verification.csv','j0_j1_derivation_checks.csv','formal_jacobian_verification.csv'],tables):write_csv(OUT/path,table)
    assert max(row['complex_step_relative_error'] for row in tables[2])<1e-6
    assert max(row['relative_error'] for row in tables[4])<1e-6
    write_json(OUT/'structure_verification.json',dict(status='PASS',conditions=CONDITIONS,
        max_Dh1_complex_step_relative_error=max(row['complex_step_relative_error'] for row in tables[2]),
        max_formal_jacobian_relative_error=max(row['relative_error'] for row in tables[4]),
        checks_completed_at_utc=stamp()))

if __name__=='__main__':main()
