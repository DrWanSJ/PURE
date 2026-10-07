"""Extra independent canonical checks away from the zero-fast-current graph."""
from r7_ck_h1_v1 import *
from validate_source_coordinates_full_v1 import rate_jacobian
from r5_ck_partial_equilibrium_runtime_v1 import material_root

def main():
    checked_binding();records=[]
    for name in CONDITIONS:
        r=FirstOrderCK(name);Sf=r.S[:,r.fast].toarray();Sf_q=Sf[r.qix]
        assert np.linalg.matrix_rank(Sf_q)==2 and np.max(abs(r.T@Sf))==0
        with np.load(ROOT/'results/reduction/r6_ck_validation/per_condition'/name/'run_001/comparison.npz') as f:a={k:f[k].copy() for k in f.files}
        for k,(t,source) in enumerate(zip(a['times'],a['source'])):
            dz=r.T@source-r.z0;c=r.core(dz)
            # Derive g_q directly from the canonical polynomial rate Jacobian,
            # independent of the hand-written two-by-two graph Jacobian.
            Rx=rate_jacobian(r.source,c['x']).toarray()
            Jcanonical=Sf_q@Rx[r.fast]@r.D
            h1_residual=Jcanonical@c['h1']-(c['H']@c['F']-c['G0'])
            _,qfrozen=material_root(*c['z'][:3],solver_extension=True)
            equations=[]
            for multiplier in [0.,.5,1.]:
                q=c['q']+multiplier*c['h1'];x=r.affine(c['z'],q)
                v=r.rates(x);slow=v.copy();slow[r.fast]=0
                F=r.TS@slow;G0=r.Q@slow;p=c['z'][2]-q.sum()
                g=2*p*(c['z'][:2]-q)-1000*q
                for eta in [.25,1.,2.]:
                    full=np.asarray(r.source.full_rhs_from_rates(r.rates(x,eta)))
                    equations.append(float(max(np.max(abs(r.T@full-F)),np.max(abs(full[r.qix]-g/eta-G0)))))
            records.append(dict(condition=name,sample_index=k,time_s=float(t),
                canonical_Gq_max_abs_difference=float(np.max(abs(Jcanonical-c['J']))),
                canonical_h1_equation_residual=float(np.max(abs(h1_residual))),
                h0_frozen_q_difference=float(np.max(abs(qfrozen-c['q']))),
                off_graph_eta_family_max_abs_difference=max(equations),Nqf_rank=2))
        print(name,'canonical off-graph family and Gq verification complete',flush=True)
    write_csv(OUT/'canonical_structure_verification.csv',records)
    maxima={key:max(v[key] for v in records) for key in ['canonical_Gq_max_abs_difference','canonical_h1_equation_residual','h0_frozen_q_difference','off_graph_eta_family_max_abs_difference']}
    assert maxima['canonical_Gq_max_abs_difference']<1e-8
    assert maxima['canonical_h1_equation_residual']<1e-8
    assert maxima['h0_frozen_q_difference']<1e-10
    assert maxima['off_graph_eta_family_max_abs_difference']<1e-5
    write_json(OUT/'canonical_structure_verification.json',dict(status='PASS_INDEPENDENT_CANONICAL_STRUCTURE',
        conditions=CONDITIONS,samples=len(records),maxima=maxima,verified_at_utc=stamp(),
        no_new_trajectory_solves=True,no_new_conditions=True,gross_rates_used_only_for_internal_identity=True))

if __name__=='__main__':main()
