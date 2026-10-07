"""Independent canonical equations and score recalculation for additive R7."""
from r7_ck_h1_v1 import *
from r6_ck_common_v1 import rows, FormalCK
from validate_source_coordinates_full_v1 import rate_jacobian
import math, json, ast

def independent_graph(r,dz):
    """Separate scalar-root/rate implementation, including complex arithmetic."""
    z=r.z0+dz;T=z[:2];B=z[2];a=500+T.sum()-B;root=np.sqrt(a*a+2000*B)
    p=1000*B/(root+a) if np.real(a)>=0 else (root-a)/2
    q=T*p/(500+p);b=p/(500+p);d=500/(500+p)**2
    dp=np.array([-b,-b,1])/(1+T.sum()*d)
    H=np.zeros((2,212),dtype=np.result_type(dz,float));H[:,:3]=np.diag([b,b])@np.eye(2,3)+T[:,None]*d*dp
    x=r.x0+r.Xz@dz+r.D@(q-r.x0[r.qix]);x[r.ix]=[z[0]-q[0],z[1]-q[1],p,q[0],q[1]]
    v=np.array([constant*np.prod(x[factors]) for constant,factors in r.source.rate_specs])
    v[r.fast]=0
    F=r.TS@v;G=r.Q@v
    J=np.array([[-2*(p+T[0]-q[0])-1000,-2*(T[0]-q[0])],[-2*(T[1]-q[1]),-2*(p+T[1]-q[1])-1000]])
    h1=np.linalg.solve(J,H@F-G)
    return x,q,H,F,G,J,h1,v

def independently_score_curve(source,model,sp,mp,t,switch,floor,gate,extra):
    result={}
    for window,mask in [('FULL_WINDOW',t>=0),('POST_INITIAL_LAYER',t>=switch),('POST_0P05_DIAGNOSTIC',t>=.05),('COMPOSITE_OR_HYBRID',t>=0)]:
        scale=np.maximum(np.max(np.abs(source[mask]),axis=0),floor)
        errors=np.max(np.abs(model[mask]-source[mask]),axis=0)/scale
        uncertainty=(np.max(np.abs(sp[mask]-source[mask]),axis=0)+np.max(np.abs(mp[mask]-model[mask]),axis=0)+np.max(np.abs(extra[mask]),axis=0))/scale
        status=[]
        for e,u in zip(errors,uncertainty):
            status.append('NUMERICALLY_UNRESOLVED' if u>gate*.1 else ('RESOLVED_PASS' if e+u<=gate else ('RESOLVED_FAIL' if max(0,e-u)>gate else 'NUMERICALLY_UNRESOLVED')))
        result[window]=(errors,uncertainty,scale,status)
    return result

def verify():
    checked_binding();checks=[];snapshot=load(OUT/'pre_r7_snapshot.json')
    for path,h in snapshot['files'].items():assert sha(ROOT/path)==h,'HISTORICAL_BYTE_MUTATION:'+path
    original=Path(snapshot['r6_original_worktree'])
    for path,h in snapshot['files'].items():assert sha(original/path)==h,'ORIGINAL_R6_MUTATION:'+path
    checks.append(dict(check='ALL_3079_PRE_R7_AND_ORIGINAL_R6_BYTES_PRESERVED',status='PASS'))
    manifest=load(OUT/'manifest.json')
    for path,h in manifest['files'].items():assert sha(ROOT/path)==h,'MANIFEST_MUTATION:'+path
    c=load(OUT/'numerical_contract.json')['r6_contract'];r6=ROOT/'results/reduction/r6_ck_validation'
    assert c==load(r6/'formal_numerical_contract.json')
    assert c['mandatory_classes']==['A','B','C','D','F','H'] and c['gross_classes_mandatory']==[]
    assert c['gates']['net_current']==.05 and c['gates']['net_extent']==.01
    assert list(p.name for p in (OUT/'per_condition').iterdir())==CONDITIONS or sorted(p.name for p in (OUT/'per_condition').iterdir())==sorted(CONDITIONS)
    claims=list(OUT.rglob('execution_claim.json'));assert len(claims)==3
    assert sorted(load(p)['condition'] for p in claims)==sorted(CONDITIONS)
    assert all(load(p)['registration_sha256']==sha(OUT/'registration_binding.json') for p in claims)
    checks.append(dict(check='FROZEN_BRANCH_A_GATES_WINDOWS_PARAMETERS_AND_THREE_AUTHORIZED_EXECUTIONS',status='PASS'))
    identities=[];allrequired=[];guardclasses=[];complete=True;domainok=True
    for name in CONDITIONS:
        dest=OUT/'per_condition'/name/'run_001';result=load(dest/'result.json')
        if result['status']!='COMPLETED':complete=False;continue
        r=FirstOrderCK(name)
        assert [r.source.rate_specs[j][0] for j in r.fast]==[2,1000,2,1000]
        assert np.array_equal(r.Nqf,np.eye(2)) and np.linalg.matrix_rank(r.Nqf)==2
        assert np.max(abs(r.T@r.D))==0 and np.max(abs(r.T@r.Xz-np.eye(212)))==0
        with np.load(dest/'comparison.npz') as f:a={k:f[k].copy() for k in f.files}
        with np.load(r6/'per_condition'/name/'run_001/comparison.npz') as f:old={k:f[k].copy() for k in f.files}
        for k in ['source','source_probe','source_net','source_net_probe','source_extent','source_extent_probe','source_rates','source_gross_extent','times','x0']:
            assert np.array_equal(a[k],old[k]),'SOURCE_REUSE_MUTATION:'+k
        for k,j in [('zero_net','reduced_net'),('zero_net_probe','reduced_net_probe'),('zero_extent','reduced_extent'),('zero_extent_probe','reduced_extent_probe'),('zero_tight_extent','same_trajectory_tight_extent')]:assert np.array_equal(a[k],old[j])
        t=a['times'];assert float(a['switch'])==r.switch and float(a['tau0'])==r.tau0
        boundary=np.flatnonzero(t==r.switch)[0]
        assert np.array_equal(a['formal_state'][t<r.switch],a['source'][t<r.switch])
        assert np.array_equal(a['formal_extent'][t<=r.switch],a['source_extent'][t<=r.switch])
        assert np.array_equal(a['post_extent'][t<=r.switch],a['source_extent'][t<=r.switch])
        assert np.array_equal(a['formal_extent'][0],np.zeros(678))
        from extract_r6_ck_state_current_v1 import StoredDense
        native=StoredDense(dest/'formal_primary_dense.npz').data
        assert np.array_equal(native['accepted'][0],r.T@old['full_switch_state']-r.z0)
        errors=[];hres=[];jres=[];h0err=[];family=[];rhserr=[];nonlinear=[]
        for key in ['post','formal']:
            for k in np.flatnonzero(t>=r.switch):
                dz=a[key+'_slow'][k]-r.z0
                x,q,H,F,G,J,h1,v=independent_graph(r,dz)
                jac=rate_jacobian(r.source,x).tolil();jac[r.fast,:]=0;jac=jac.tocsc()
                dv=np.asarray(jac@(r.D@h1)).ravel();F1=r.TS@dv
                direction=F/max(1,np.linalg.norm(F,np.inf));factor=max(1,np.linalg.norm(F,np.inf))
                independent_Dh1=np.imag(independent_graph(r,dz.astype(complex)+1e-25j*direction)[6])/1e-25*factor
                j0=H@F-G;j1=independent_Dh1+H@F1-r.Q@dv
                n=r.channel_net(v+dv);n[r.fast_channels]=j0+j1
                scale=np.maximum(np.max(abs(a['source_net']),axis=0),1e-9)
                errors.append(float(np.max(abs(n-a[key+'_net'][k])/scale)))
                jres.append(float(np.max(abs(j1-a[key+'_j1'][k]))))
                hres.append(float(np.max(abs(J@h1+G-H@F))))
                h0err.append(float(np.max(abs(x-r.manifold_delta(dz)[0]))))
                assert np.max(abs((x+r.D@h1)-a[key+'_state'][k]))<3e-10
                if k in [boundary,len(t)//2,len(t)-1]:
                    rhserr.append(float(np.max(abs(r.reduced_rhs_delta(0,dz)-(F+F1)))))
                    resummed=r.TS@np.array([constant*np.prod((x+r.D@h1)[factors]) for constant,factors in r.source.rate_specs])
                    nonlinear.append(float(np.max(abs(resummed-(F+F1)))))
                    for eta in [.25,1,2]:
                        vv=np.array([constant*np.prod(x[factors]) for constant,factors in r.source.rate_specs]);vv[r.fast]/=eta
                        full=r.S@vv
                        gf=np.array([2*(dz+r.z0)[2]*(0.),0.]) # overwritten explicitly below
                        z=dz+r.z0;p=z[2]-q.sum();gf=2*p*(z[:2]-q)-1000*q
                        family.append(float(max(np.max(abs(r.T@full-F)),np.max(abs(full[r.qix]-(gf/eta+G))))))
        assert max(errors)<1e-6,'INDEPENDENT_CURRENT_IDENTITY'
        assert max(hres)<1e-8 and max(h0err)<3e-10
        assert max(rhserr)<1e-7,'FORMAL_TRUNCATION_MISMATCH'
        assert max(family)<1e-5,'EXACT_ETA_FAMILY_MISMATCH'
        identities.append(dict(condition=name,max_independent_current_scaled_difference=max(errors),max_h1_residual=max(hres),max_j1_abs_identity_difference=max(jres),max_h0_affine_difference=max(h0err),max_formal_truncation_abs_difference=max(rhserr),resummed_substitution_discrepancy=max(nonlinear),max_eta_family_difference=max(family)))
        cancel=np.zeros_like(a['source_net']);ecancel=np.zeros_like(a['source_extent'])
        for k,(f,b) in enumerate(r.channels):
            if b is not None:
                cancel[:,k]=8*np.finfo(float).eps*(abs(a['source_rates'][:,f])+abs(a['source_rates'][:,b]))
                ecancel[:,k]=8*np.finfo(float).eps*(abs(a['source_gross_extent'][:,f])+abs(a['source_gross_extent'][:,b]))
        actual=rows(dest/'observable_scores.csv');assert len(actual)==3*2*4*678
        table={(v['model'],v['contract_class'],v['window'],v['observable']):v for v in actual};assert len(table)==len(actual)
        condition_required=[]
        for model,key in zip(['ZERO_ORDER_R6','FIRST_ORDER_POSTPROCESSING_ON_Z0','FORMAL_FIRST_ORDER_SELF_CONSISTENT'],['zero','post','formal']):
            for cls,suffix,floor,gate,extra in [('D','net',1e-9,.05,cancel),('F','extent',1e-6,.01,ecancel+abs(a[key+'_tight_extent']-a[key+'_extent']))]:
                values=independently_score_curve(a['source_'+suffix],a[key+'_'+suffix],a['source_'+suffix+'_probe'],a[key+'_'+suffix+'_probe'],t,r.switch,floor,gate,extra)
                for window,(e,u,scale,status) in values.items():
                    for k,label in enumerate(r.channel_ids):
                        row=table[(model,cls,window,label)]
                        assert abs(float(row['E_inf'])-e[k])<1e-12 and abs(float(row['uncertainty'])-u[k])<1e-12
                        mandatory=k in r.mandatory_channels and window in ['FULL_WINDOW','POST_INITIAL_LAYER']
                        assert row['mandatory']==str(mandatory)
                        assert row['status']==(status[k] if mandatory else 'DESCRIPTIVE')
                        if model=='FORMAL_FIRST_ORDER_SELF_CONSISTENT' and mandatory:condition_required.append(status[k])
        allrequired.extend(condition_required)
        actual=rows(dest/'state_guard.csv');lookup={(v['category'],v['window'],v['observable']):v for v in actual}
        gst={'A':[],'B':[]}
        for category,labels,source,model,sp,mp in [('STATE',r.source.species,a['source'],a['formal_state'],a['source_probe'],a['formal_state_probe']),('SLOW_TOTAL_OR_COORDINATE',r.labels,a['source']@r.T.T,a['formal_slow'],a['source_probe']@r.T.T,a['formal_slow_probe'])]:
            values=independently_score_curve(source,model,sp,mp,t,r.switch,1e-6,.01,np.zeros_like(source))
            for window,(e,u,scale,status) in values.items():
                for k,label in enumerate(labels):
                    row=lookup[(category,window,label)]
                    assert abs(float(row['E_inf'])-e[k])<1e-12 and abs(float(row['uncertainty'])-u[k])<1e-12
                    cls='B' if category=='STATE' and label in c['algebraically_affected_states'] else 'A'
                    assert cls==row['contract_class']
                    if window in ['FULL_WINDOW','POST_INITIAL_LAYER']:gst[cls].append(status[k]);assert row['status']==status[k]
        lawrows=rows(dest/'conservation_guard.csv');Cstatuses=[]
        for model,key,pkey in [('SOURCE','source','source_probe'),('FORMAL_FIRST_ORDER_SELF_CONSISTENT','formal_state','formal_state_probe')]:
            drift=np.array([[math.fsum(float(co)*(float(x[i])-float(r.x0[i])) for i,co in law.items()) for law in r.source.laws] for x in a[key]])
            probe=np.array([[math.fsum(float(co)*(float(x[i])-float(r.x0[i])) for i,co in law.items()) for law in r.source.laws] for x in a[pkey]])
            for k,label in enumerate(r.source.cert['law_ids']):
                row=next(v for v in lawrows if v['model']==model and v['law']==label)
                error=float(np.max(abs(drift[:,k])));u=float(np.max(abs(drift[:,k]-probe[:,k])))
                status='NUMERICALLY_UNRESOLVED' if u>1e-9 else ('RESOLVED_PASS' if error+u<=1e-8 else ('RESOLVED_FAIL' if max(0,error-u)>1e-8 else 'NUMERICALLY_UNRESOLVED'))
                assert error==float(row['max_absolute_drift']) and u==float(row['uncertainty']) and status==row['status']
                Cstatuses.append(status)
        def agg(v):return 'RESOLVED_FAIL' if 'RESOLVED_FAIL' in v else ('NUMERICALLY_UNRESOLVED' if 'NUMERICALLY_UNRESOLVED' in v else 'RESOLVED_PASS')
        classes={k:agg(v) for k,v in gst.items()};classes['C']=agg(Cstatuses)
        assert result['guards']==classes;guardclasses.extend(classes.values())
        scales=np.maximum(np.max(abs(a['source']),axis=0),1e-6);material=False
        for dz in native['accepted']:
            x,*rest=independent_graph(r,dz);h1=rest[-2]
            material|=bool(np.any((x+r.D@h1)[r.ix]<-.01*scales[r.ix]))
        assert result['new_material_domain_failure']==material;domainok&=not material
    checks.append(dict(check='INDEPENDENT_EXACT_FAMILY_H0_H1_DH1_J0_J1_RANK_AND_FORMAL_TRUNCATION',status='PASS',identities=identities))
    checks.append(dict(check='INDEPENDENT_A_B_C_D_F_SCORING_STARTUP_DOMAIN_AND_UNCERTAINTY',status='PASS'))
    decision=load(OUT/'advancement_decision.json')
    ready=complete and bool(allrequired) and all(v=='RESOLVED_PASS' for v in allrequired+guardclasses) and domainok
    assert decision['advancement_requirements_met']==ready
    assert decision['recommend_later_nine_condition_validation']==ready
    assert decision['scientific_promotion'] is False and decision['PURE_reduced_core']=='NOT_VALIDATED'
    assert decision['mechanistic_decisions']=={'count':968,'status':'PENDING'}
    assert decision['action']=='STOP_BOUNDED_R7_NO_BROAD_RUN' and decision['historical_R6_H_unchanged']
    assert decision['gross_status']=='SOURCE_PROVENANCE_PRESERVED;DESCRIPTIVE;BUT_NOT_VALIDATED'
    for p in (ROOT/'scripts').glob('*r7*py'):ast.parse(p.read_text(encoding='utf-8'))
    checks.append(dict(check='EXACT_REGISTERED_ADVANCEMENT_NO_GROSS_GATE_NO_PROMOTION',status='PASS'))
    write_json(OUT/'verification.json',dict(schema='R7_INDEPENDENT_VERIFICATION_V1',status='PASS_ENGINEERING_AND_EVIDENCE_VERIFICATION',verified_at_utc=stamp(),checks=checks,
        manifest_sha256=sha(OUT/'manifest.json'),registration_sha256=sha(OUT/'registration_binding.json'),recommendation=decision['recommendation'],promotion=False))
    print('R7 independent verifier PASS',decision['recommendation'],flush=True)

if __name__=='__main__':verify()
