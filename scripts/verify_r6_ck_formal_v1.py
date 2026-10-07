"""Independent final Branch-A evidence and numerical-score verifier."""
from r6_ck_common_v1 import *
from verify_r6_ck_source_reuse_v1 import verify as verify_source_reuse
from verify_r5_mechanism_first_v1 import independent_canonical
import ast, subprocess

def independent_status(error,u,limit):
    if u>limit/10:return 'NUMERICALLY_UNRESOLVED'
    if error+u<=limit:return 'RESOLVED_PASS'
    if error-u>limit:return 'RESOLVED_FAIL'
    return 'NUMERICALLY_UNRESOLVED'

def close_float(a,b,label,rtol=1e-11,atol=1e-13):
    assert np.isclose(float(a),float(b),rtol=rtol,atol=atol),(label,a,b)

def verify_curve_table(table,reference,approx,ref_probe,approx_probe,t,switch,floor,gate,names,
                       mandatory,extra=None):
    index={n:i for i,n in enumerate(names)};statuses=[]
    for row in table:
        i=index[row['observable']];window=row['window']
        if window in ['FULL_WINDOW','COMPOSITE_OR_HYBRID']:mask=np.ones(len(t),dtype=bool)
        elif window=='POST_INITIAL_LAYER':mask=t>=switch
        else:assert window=='POST_0P05_DIAGNOSTIC';mask=t>=.05
        scale=max(float(np.max(np.abs(reference[mask,i]))),floor)
        error=float(np.max(np.abs(approx[mask,i]-reference[mask,i])))/scale
        u=(float(np.max(np.abs(ref_probe[mask,i]-reference[mask,i])))+
           float(np.max(np.abs(approx_probe[mask,i]-approx[mask,i]))))/scale
        if extra is not None:u+=float(np.max(np.abs(extra[mask,i])))/scale
        needed=i in mandatory and window in ['FULL_WINDOW','POST_INITIAL_LAYER']
        close_float(row['reference_scale'],scale,'scale');close_float(row['E_inf'],error,'E_inf')
        close_float(row['uncertainty'],u,'uncertainty');close_float(row['gate'],gate,'gate')
        close_float(row['floor'],floor,'floor')
        close_float(row['max_absolute_error'],error*scale,'absolute error')
        close_float(row['lower_error'],max(0.,error-u),'lower error')
        close_float(row['upper_error'],error+u,'upper error')
        assert (row['mandatory']=='True')==needed
        expected=independent_status(error,u,gate) if needed else 'DESCRIPTIVE'
        assert row['status']==expected,(row['observable'],window,row['status'],expected)
        if needed:statuses.append((row['contract_class'],expected,error,u))
    assert len(table)==4*len(names),'Missing curve/window rows'
    return statuses

def verify_partial(name,dest,species,rx,S,rhs,membership,laws):
    folder=dest/'state_current_assessment_001';report=load(folder/'assessment.json')
    for rel,h in report['dense_input_hashes'].items():assert sha(ROOT/rel)==h
    for file,h in report['output_hashes'].items():assert sha(folder/file)==h
    assert report['no_new_state_solve'] and report['no_extent_claim'] and report['no_threshold_change']
    with np.load(folder/'instantaneous_comparison.npz') as file:a={k:file[k].copy() for k in file.files}
    runtime=FormalCK(name)
    assert np.array_equal(a['x0'],initial(runtime.source,name))
    assert np.array_equal(a['source'][0],a['x0']) and np.array_equal(a['reduced'][0],a['x0'])
    assert np.array_equal(a['times'][a['times']>=1e-4],TIMES[1:])
    with np.load(historical_path(name)/'full_state.npz') as source:
        assert np.array_equal(a['source'][a['times']>=1e-4],source['state'][1:])
    with np.load(ROOT/'results/reduction/r4_fast_block_screen/source_uncertainty'/name/'probe_state.npz') as source:
        assert np.array_equal(a['source_probe'][a['times']>=1e-4],source['state'][1:])
    L=np.array([[float(law.get(i,0)) for i in range(241)] for law in laws])
    assert np.array_equal(a['T']@a['Xz'],np.eye(212))
    assert np.max(abs(L@a['Xz']))==np.max(abs(L@a['D']))==0
    t=a['times'];switch=float(a['switch']);rid={r['id']:j for j,r in enumerate(rx)}
    fast=[rid[n] for n in FAST_IDS];fastchannels=[i for i,r in enumerate(membership) if r['selected_ck_fast']=='True']
    indices={n:i for i,n in enumerate(species)};qi=[indices[n] for n in ['CK_CP','CK_CP_ADP']]
    T=a['T'];TS=T[:3]@S;assert np.array_equal(T@a['D'],np.zeros((212,2)))
    for model,field in [('source','source_net'),('reduced','reduced_net')]:
        for k,xx in enumerate(a[model]):
            _,v=rhs(xx);expected=np.array([v[rid[r['forward']]]-(v[rid[r['reverse']]] if r['reverse'] else 0.) for r in membership])
            assert np.max(abs(v-a[model+'_rates'][k])/np.maximum(abs(v),1.))<1e-12
            if model=='reduced' and t[k]>=switch:
                z=a['reduced_slow'][k];p=xx[indices['CP']];alpha=p/(500+p)
                dp=np.array([-alpha,-alpha,1.])/(1+(z[0]+z[1])*500/(500+p)**2)
                dh=np.array([[alpha,0,0],[0,alpha,0]])+z[:2,None]*500/(500+p)**2*dp
                slow=v.copy();slow[fast]=0
                F=np.array([math.fsum(coef*slow[j] for j,coef in enumerate(row) if coef) for row in TS])
                other=np.array([math.fsum(coef*slow[j] for j,coef in enumerate(S[i]) if coef) for i in qi])
                expected[fastchannels]=dh@F-other
            assert np.max(abs(expected-a[field][k])/np.maximum(abs(expected),1.))<1e-9
    extra=np.zeros_like(a['source_net'])
    for k,r in enumerate(membership):
        if r['reverse']:
            j=rid[r['forward']];b=rid[r['reverse']]
            extra[:,k]=8*np.finfo(float).eps*(abs(a['source_rates'][:,j])+abs(a['source_rates'][:,b]))
    active=[]
    active+=verify_curve_table(rows(folder/'state_errors.csv'),a['source'],a['reduced'],a['source_probe'],a['reduced_probe'],
          t,switch,1e-6,.01,species,set(range(241)))
    active+=verify_curve_table(rows(folder/'slow_total_errors.csv'),a['source']@T.T,a['reduced_slow'],a['source_probe']@T.T,a['probe_slow'],
          t,switch,1e-6,.01,a['coordinate_labels'].tolist(),set(range(212)))
    active+=verify_curve_table(rows(folder/'net_current_errors.csv'),a['source_net'],a['reduced_net'],a['source_net_probe'],a['reduced_net_probe'],
          t,switch,1e-9,.05,a['channel_ids'].tolist(),set(a['mandatory_channels'].tolist()),extra)
    for model,key in [('source','source_law_drift'),('reduced','reduced_law_drift'),('source_probe','source_law_probe'),('reduced_probe','reduced_law_probe')]:
        check=np.array([[math.fsum(float(v)*(float(xx[i])-float(a['x0'][i])) for i,v in law.items()) for law in laws] for xx in a[model]])
        assert np.array_equal(check,a[key])
    lawids=[r['conservation_id'] for r in rows(DOC/'conservation_laws_v0.csv') if r['scope']=='SOURCE_GENERAL']
    for row in rows(folder/'conservation.csv'):
        i=lawids.index(row['observable']);key,probe=('source_law_drift','source_law_probe') if row['model']=='SOURCE' else ('reduced_law_drift','reduced_law_probe')
        e=np.max(abs(a[key][:,i]));u=np.max(abs(a[key][:,i]-a[probe][:,i]))
        close_float(row['max_absolute_drift'],e,'partial conservation');close_float(row['uncertainty'],u,'partial C uncertainty')
        expected=independent_status(e,u,1e-8);assert row['status']==expected;active.append(('C',expected,e,u))
    independent={}
    for cls in ['A','B','C','D']:
        values=[s for k,s,_,_ in active if k==cls]
        independent[cls]='RESOLVED_FAIL' if 'RESOLVED_FAIL' in values else ('NUMERICALLY_UNRESOLVED' if 'NUMERICALLY_UNRESOLVED' in values else 'RESOLVED_PASS')
    assert independent==report['class_status']
    assert report['extent_status']=='NOT_ASSESSED_BY_THIS_EXTRACTOR'
    # Independently recompute summary maxima; absent extents are never filled with zero.
    state=rows(folder/'state_errors.csv');totals=rows(folder/'slow_total_errors.csv');current=rows(folder/'net_current_errors.csv')
    fastids=[membership[i]['channel_id'] for i in fastchannels]
    maxima={
       'state':max(float(r['E_inf']) for r in state if r['mandatory']=='True'),
       'slow_total':max(float(r['E_inf']) for r in totals if r['mandatory']=='True' and r['observable'] in ['T0','T1','B']),
       'retained_coordinate':max(float(r['E_inf']) for r in totals if r['mandatory']=='True'),
       'protein':max(float(r['E_inf']) for r in state if r['mandatory']=='True' and r['observable']=='Pept0003'),
       'ck_net_current':max(float(r['E_inf']) for r in current if r['mandatory']=='True' and r['observable'] in fastids),
       'net_current':max(float(r['E_inf']) for r in current if r['mandatory']=='True'),
       'ck_net_current_post_0p05':max(float(r['E_inf']) for r in current if r['window']=='POST_0P05_DIAGNOSTIC' and r['observable'] in fastids),
       'conservation':max(float(r['max_absolute_drift']) for r in rows(folder/'conservation.csv'))}
    for k,value in maxima.items():close_float(report['maxima'][k],value,'partial maximum '+k)
    return dict(condition=name,status='PASS_COMPLETED_STATE_CURRENT_TIERS_WITH_EXTENT_NONCOMPLETION',
                classes=dict(independent,F='NUMERICALLY_UNRESOLVED',H='NUMERICALLY_UNRESOLVED'))

def verify():
    c=checked_contract();checks=[]
    historical=load(OUT/'historical_snapshot.json');parent=Path(load(OUT/'input_provenance.json')['source_checkout'])
    provenance=load(OUT/'input_provenance.json')
    assert sha(OUT/'historical_snapshot.json')==provenance['historical_snapshot_sha256']
    assert len(historical)==provenance['historical_file_count']==2585
    for rel,meta in historical.items():
        assert sha(ROOT/rel)==meta['sha256'] and sha(parent/rel)==meta['sha256'],rel
    archived=load(OUT/'audit_stop_001/snapshot.json')
    for rel,h in archived['files'].items():assert sha(OUT/'audit_stop_001'/rel)==h,rel
    checks.append(dict(check='ALL_2585_PRE_R6_FILES_AND_PRIOR_R6_SCOPE_STOP_PRESERVED',status='PASS'))
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==provenance['execution_parent_sha']
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/r6-ck-validation-20261007'
    assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
    for path,h in load(OUT/'desktop_untracked_snapshot.json').items():assert sha(Path(path))==h
    assert sha(Path(provenance['request_file']))==provenance['request_sha256']==sha(OUT/'human_request.txt')
    for rel,h in load(OUT/'registration_binding.json')['file_hashes'].items():assert sha(ROOT/rel)==h
    evidence=rows(OUT/'scientific_requirement_to_observable.csv')
    assert len(evidence)==len({r['requirement_id'] for r in evidence})==23
    for row in evidence:
        path=ROOT/row['source_file'];assert sha(path)==row['source_sha256']
        lines=path.read_text(encoding='utf-8').splitlines();start,end=int(row['source_line_start']),int(row['source_line_end'])
        assert 1<=start<=end<=len(lines)
        excerpt='\n'.join(lines[start-1:end]);assert excerpt==row['source_excerpt']
        assert hashlib.sha256(excerpt.encode('utf-8')).hexdigest()==row['excerpt_sha256']
        assert row['source_location']==f'L{start}-L{end}'
        assert row['evidence_status'] in ['EXTRACTED','INFERRED','AMBIGUOUS']
    checks.append(dict(check='LINEAGE_INITIAL_AUDIT_SOURCE_LOCATIONS_AND_UNRELATED_FILES',status='PASS'))
    assert c['mandatory_classes']==['A','B','C','D','F','H'] and c['gross_classes_mandatory']==[]
    decision=load(OUT/'observable_requirement_decision.json')
    assert decision['decision']=='GROSS_FLUX_NOT_REQUIRED_FOR_CK_PROMOTION'
    assert decision['human_decision_sha256']==sha(OUT/'human_branch_a_decision_20261007.txt')
    receipt=load(OUT/'formal_registration_binding.json')
    assert receipt['decisive_run_count_before_freeze']==0
    assert {p.name for p in (OUT/'per_condition').iterdir() if p.is_dir()}==set(CONDITIONS)
    candidate=load(OUT/'candidate_definition.json')
    assert candidate['fast_reaction_ids']==FAST_IDS and candidate['nonfast_dynamic_reaction_count']==964
    assert candidate['fitted_parameters']==[]
    assert all(candidate[key] is False for key in ['initial_condition_fitting','clipping','time_shift','source_trajectory_projection','canonical_reaction_deletion','promotion'])
    reuse=verify_source_reuse(write=False)
    assert [r['condition'] for r in reuse['conditions']]==CONDITIONS
    checks.append(dict(check='EXPLICIT_HUMAN_SCOPE_PROSPECTIVE_CONTRACT_AND_SOURCE_REUSE',status='PASS'))
    species,rx,S,rhs=independent_canonical();ix={n:i for i,n in enumerate(species)}
    rid={r['id']:j for j,r in enumerate(rx)}
    fast=[rid[n] for n in FAST_IDS]
    assert [rx[j]['k'] for j in fast]==[2,1000,2,1000]
    assert all(S[ix[n],fast].max()==0 and S[ix[n],fast].min()==0 for n in ['ATP','ADP'])
    membership=rows(OUT/'formal_net_channel_membership.csv');assert len(membership)==678
    N=np.column_stack([S[:,rid[row['forward']]] for row in membership])
    for row in membership:
        if row['reverse']:assert np.array_equal(S[:,rid[row['forward']]],-S[:,rid[row['reverse']]])
        participants=set(rx[rid[row['forward']]]['sides'][0])|set(rx[rid[row['forward']]]['sides'][1])
        needed=row['forward'] in [FAST_IDS[0],FAST_IDS[2]] or bool(participants&set(c['resources'])) or any(n.startswith('CK') for n in participants)
        assert (row['mandatory_net_current_and_extent']=='True')==needed
        assert row['gross_mandatory']=='False'
    fastchannels=[i for i,row in enumerate(membership) if row['selected_ck_fast']=='True']
    qix=[ix['CK_CP'],ix['CK_CP_ADP']];nqf=N[np.ix_(qix,fastchannels)]
    assert np.array_equal(nqf,np.eye(2))
    lawrows=[r for r in rows(DOC/'conservation_laws_v0.csv') if r['scope']=='SOURCE_GENERAL'];assert len(lawrows)==27
    laws=[{ix[n]:Fraction(str(v)) for n,v in json.loads(r['species_coefficients_json']).items()} for r in lawrows]
    for law in laws:
        for j in range(968):assert sum((v*Fraction(int(S[i,j])) for i,v in law.items()),Fraction(0))==0
    checks.append(dict(check='INDEPENDENT_CANONICAL_REVERSE_MEMBERSHIP_NQF_AND_EXACT_CONSERVATION',status='PASS'))
    condition_checks=[];max_current_identity=0.;max_reconstruction=0.;all_results=[]
    domain_report={row['condition_id']:row for row in rows(OUT/'physical_domain_diagnostics.csv')}
    for name in CONDITIONS:
        dest=OUT/'per_condition'/name/'run_001';result=load(dest/'result.json');all_results.append(result)
        assert result['status'] in ['COMPLETED','NUMERICAL_NONCOMPLETION'], 'Final verification requires a terminal experiment: '+name
        assert datetime.datetime.fromisoformat(receipt['frozen_at_utc'])<datetime.datetime.fromisoformat(result['started_at_utc'])
        assert result['contract_sha256']==sha(OUT/'formal_numerical_contract.json')
        assert result['registration_sha256']==sha(OUT/'formal_registration_binding.json')
        assert result['reuse_sha256']==sha(OUT/'source_reuse_verification.json')
        assert result['runtime_sha256']==sha(ROOT/'scripts/r6_ck_common_v1.py')
        assert result['runner_sha256']==sha(ROOT/'scripts/run_r6_ck_formal_v1.py')
        claim=load(dest/'execution_claim.json')
        assert claim['condition']==name and claim['registration_sha256']==result['registration_sha256']
        assert datetime.datetime.fromisoformat(receipt['frozen_at_utc'])<datetime.datetime.fromisoformat(claim['started_at_utc'])
        assert result['fresh_reduced'] and result['historical_reduced_reused'] is False and result['promotion'] is False
        for file,h in result['output_hashes'].items():assert sha(dest/file)==h,(name,file)
        if result['status']!='COMPLETED':
            assert result['scientific_status']=='CK_NUMERICALLY_UNRESOLVED'
            if (dest/'state_current_assessment_001/assessment.json').exists():
                checked=verify_partial(name,dest,species,rx,S,rhs,membership,laws)
                condition_checks.append(checked)
                print('Independently verified completed tiers',name,checked['classes'],flush=True)
            else:condition_checks.append(dict(condition=name,status='PRESERVED_NUMERICAL_NONCOMPLETION'))
            continue
        with np.load(dest/'comparison.npz') as f:a={k:f[k].copy() for k in f.files}
        t=a['times'];switch=float(a['switch']);T=a['T'];Xz=a['Xz'];D=a['D'];x0=a['x0']
        assert np.array_equal(x0,initial(FormalCK(name).source,name))
        assert hashlib.sha256(x0.tobytes()).hexdigest()==result['initial_state_sha256']
        assert np.array_equal(t[t>=1e-4],TIMES[1:])
        assert np.array_equal(T@D,np.zeros((212,2))) and np.array_equal(T@Xz,np.eye(212))
        L=np.array([[float(law.get(i,0)) for i in range(241)] for law in laws])
        assert np.max(abs(L@Xz))==np.max(abs(L@D))==0
        for model,netkey in [('source','source_net'),('reduced','reduced_net')]:
            for sample,xx in enumerate(a[model]):
                _,v=rhs(xx)
                assert np.max(abs(v-a[model+'_rates'][sample])/np.maximum(abs(v),1.))<1e-12
                expected=np.array([v[rid[row['forward']]]-(v[rid[row['reverse']]] if row['reverse'] else 0.) for row in membership])
                if model=='reduced' and t[sample]>=switch:
                    z=a['reduced_slow'][sample];p=xx[ix['CP']];alpha=p/(500+p)
                    H=1+(z[0]+z[1])*500/(500+p)**2;dp=np.array([-alpha,-alpha,1.])/H
                    dh=np.array([[alpha,0,0],[0,alpha,0]])+np.array([z[0],z[1]])[:,None]*500/(500+p)**2*dp
                    slowv=v.copy();slowv[fast]=0
                    TS=T[:3]@S
                    F=np.array([math.fsum(coef*slowv[j] for j,coef in enumerate(row) if coef) for row in TS])
                    qslow=np.array([math.fsum(coef*slowv[j] for j,coef in enumerate(S[i]) if coef) for i in qix])
                    expected[fastchannels]=np.linalg.solve(nqf,dh@F-qslow)
                    reconstructed=x0+Xz@(z-T@x0)+D@(xx[qix]-x0[qix])
                    discrepancy=float(np.max(abs(reconstructed-xx)));max_reconstruction=max(max_reconstruction,discrepancy)
                    assert discrepancy<1e-8
                    # Verify q_i=T_i*p/(500+p) and the material identity without source projection.
                    assert np.max(abs(xx[qix]-z[:2]*p/(500+p)))<1e-10
                    assert abs(p+xx[qix].sum()-z[2])<1e-8
                err=float(np.max(abs(expected-a[netkey][sample])/np.maximum(abs(expected),1.)))
                max_current_identity=max(max_current_identity,err);assert err<1e-9,(name,model,sample,err)
        # Recompute exact conservation numerically from original law coefficients.
        for model,key in [('source','source_law_drift'),('reduced','reduced_law_drift'),
                          ('source_probe','source_law_probe'),('reduced_probe','reduced_law_probe')]:
            recomputed=np.array([[math.fsum(float(coef)*(float(xx[i])-float(x0[i])) for i,coef in law.items())
                                  for law in laws] for xx in a[model]])
            assert np.array_equal(recomputed,a[key]),(name,key)
        current_extra=np.zeros_like(a['source_net']);extent_extra=np.abs(a['same_trajectory_tight_extent']-a['reduced_extent'])
        for k,row in enumerate(membership):
            if row['reverse']:
                j=rid[row['forward']];b=rid[row['reverse']]
                current_extra[:,k]=8*np.finfo(float).eps*(np.abs(a['source_rates'][:,j])+np.abs(a['source_rates'][:,b]))
                extent_extra[:,k]+=8*np.finfo(float).eps*(np.abs(a['source_gross_extent'][:,j])+np.abs(a['source_gross_extent'][:,b]))
        active=[]
        active+=verify_curve_table(rows(dest/'state_errors.csv'),a['source'],a['reduced'],a['source_probe'],a['reduced_probe'],
            t,switch,1e-6,.01,species,set(range(241)))
        labels=a['coordinate_labels'].tolist()
        active+=verify_curve_table(rows(dest/'slow_total_errors.csv'),a['source']@T.T,a['reduced_slow'],a['source_probe']@T.T,a['probe_slow'],
            t,switch,1e-6,.01,labels,set(range(212)))
        ids=a['channel_ids'].tolist();mandatory=set(a['mandatory_channels'].tolist())
        active+=verify_curve_table(rows(dest/'net_current_errors.csv'),a['source_net'],a['reduced_net'],a['source_net_probe'],a['reduced_net_probe'],
            t,switch,1e-9,.05,ids,mandatory,current_extra)
        active+=verify_curve_table(rows(dest/'net_extent_errors.csv'),a['source_extent'],a['reduced_extent'],a['source_extent_probe'],a['reduced_extent_probe'],
            t,switch,1e-6,.01,ids,mandatory,extent_extra)
        lawids=[row['conservation_id'] for row in lawrows]
        for row in rows(dest/'conservation.csv'):
            i=lawids.index(row['observable']);key,probe=('source_law_drift','source_law_probe') if row['model']=='SOURCE' else ('reduced_law_drift','reduced_law_probe')
            e=float(np.max(abs(a[key][:,i])));u=float(np.max(abs(a[key][:,i]-a[probe][:,i])))
            close_float(row['max_absolute_drift'],e,'conservation');close_float(row['uncertainty'],u,'conservation uncertainty')
            status=independent_status(e,u,1e-8);assert row['status']==status
            active.append(('C',status,e,u))
        H=rows(dest/'initial_layer.csv');hby={row['observable']:row for row in H}
        assert np.array_equal(a['source'][0],a['reduced'][0]) and np.array_equal(a['source'][0],x0)
        assert np.array_equal(a['source'][t<switch],a['reduced'][t<switch])
        boundary=np.flatnonzero(t==switch)[0];assert np.array_equal(a['source_extent'][boundary],a['reduced_extent'][boundary])
        reference=np.maximum(np.max(np.abs(a['source']),axis=0),1e-6)
        jump=np.max(np.abs(a['reduced_switch_state']-a['full_switch_state'])/reference)
        jump_u=np.max((np.abs(a['reduced_switch_state']-a['reduced_switch_probe'])+np.abs(a['full_switch_state']-a['full_switch_probe']))/reference)
        close_float(hby['SCALED_SWITCH_STATE_JUMP']['value'],jump,'switch jump')
        close_float(hby['SCALED_SWITCH_STATE_JUMP']['uncertainty'],jump_u,'switch uncertainty')
        assert hby['SCALED_SWITCH_STATE_JUMP']['status']==independent_status(jump,jump_u,.01)
        z0=T@x0;quadratic=500+z0[0]+z0[1]-z0[2]
        discriminant=math.hypot(quadratic,2*math.sqrt(500*z0[2]))
        p0=2*500*z0[2]/(discriminant+quadratic) if quadratic>=0 else (discriminant-quadratic)/2
        expected_switch=10/(2*p0+1000)
        close_float(switch,expected_switch,'fixed switch',atol=1e-20)
        jump_vector=a['reduced_switch_state']-a['full_switch_state']
        total_jump=float(np.max(abs(T@jump_vector)))
        total_u=float(np.max(abs(T@(a['reduced_switch_state']-a['reduced_switch_probe'])))+
                      np.max(abs(T@(a['full_switch_state']-a['full_switch_probe']))))
        total_u+=8*np.finfo(float).eps*np.max(abs(T)@(abs(a['reduced_switch_state'])+abs(a['full_switch_state'])))
        close_float(hby['EXACT_SLOW_COORDINATE_SWITCH_CONTINUITY']['value'],total_jump,'total continuity')
        close_float(hby['EXACT_SLOW_COORDINATE_SWITCH_CONTINUITY']['uncertainty'],total_u,'total continuity uncertainty')
        with np.load(dest/'reduced_primary_dense.npz') as data:accepted=data['accepted'].copy()
        ck_indices=[ix[n] for n in ['CK','CK_ADP','CP','CK_CP','CK_CP_ADP']]
        physical=bool(np.min(accepted[:,:3]+z0[:3])>=0 and np.min(a['reduced'][:,ck_indices])>=0)
        assert float(hby['PHYSICAL_CK_TOTAL_AND_ROOT_DOMAIN']['value'])==(0. if physical else 1.)
        domain_row=domain_report[name]
        with np.load(dest/'reduced_primary_dense.npz') as data:accepted_times=data['steps'].copy()
        totals=accepted[:,:3]+z0[:3];reported=a['reduced'][:,ck_indices]
        i,j=np.unravel_index(np.argmin(totals),totals.shape);k,l=np.unravel_index(np.argmin(reported),reported.shape)
        close_float(domain_row['minimum_accepted_fast_total'],totals[i,j],'domain minimum total',atol=1e-30)
        close_float(domain_row['minimum_reported_ck_state'],reported[k,l],'domain minimum CK state',atol=1e-30)
        assert domain_row['coordinate']==['T0','T1','B'][j] and domain_row['ck_species']==species[ck_indices[l]]
        close_float(domain_row['accepted_time_s'],accepted_times[i],'domain time')
        close_float(domain_row['reported_time_s'],t[k],'reported domain time')
        assert (domain_row['strict_ck_domain_pass']=='True')==physical
        assert np.array_equal(a['reduced_extent'][0],np.zeros(678))
        for row in H:
            if float(row['gate'])>0:assert row['status']==independent_status(float(row['value']),float(row['uncertainty']),float(row['gate']))
            else:assert row['status']==('RESOLVED_PASS' if float(row['value'])==0 else 'RESOLVED_FAIL')
            active.append(('H',row['status'],float(row['value']),float(row['uncertainty'])))
        independent_classes={}
        for cls in c['mandatory_classes']:
            statuses=[status for klass,status,_,_ in active if klass==cls]
            independent_classes[cls]='RESOLVED_FAIL' if 'RESOLVED_FAIL' in statuses else ('NUMERICALLY_UNRESOLVED' if 'NUMERICALLY_UNRESOLVED' in statuses else 'RESOLVED_PASS')
        assert independent_classes==result['class_status']
        assert result['all_mandatory_gates_pass']==all(v=='RESOLVED_PASS' for _,v,_,_ in active)
        assert result['resolved_fail_count']==sum(v=='RESOLVED_FAIL' for _,v,_,_ in active)
        assert result['unresolved_count']==sum(v=='NUMERICALLY_UNRESOLVED' for _,v,_,_ in active)
        assert all(row['mandatory']=='False' and 'BUT_NOT_VALIDATED' in row['status'] for row in rows(dest/'gross_descriptive.csv'))
        # Recompute the four distinct accounting meanings from canonical columns.
        source_res=a['source']-x0-np.array([N@xi for xi in a['source_extent']])
        reduced_res=a['reduced']-x0-np.array([N@xi for xi in a['reduced_extent']])
        slow_res=a['reduced_slow']-z0-np.array([(T@N)@xi for xi in a['reduced_extent']])
        corrected=reduced_res.copy();corrected[t>=switch]-=jump_vector
        source_gross=a['source']-x0-np.array([S@xi for xi in a['source_gross_extent']])
        reduced_gross=a['reduced']-x0-np.array([S@xi for xi in a['reduced_gross_extent']])
        balances=[(a['source_law_drift'],a['reduced_law_drift']),
                  (source_res,reduced_res),(source_res@T.T,slow_res),
                  (source_res,corrected),(source_gross,reduced_gross)]
        balance_rows=rows(dest/'balance_accounting.csv');assert len(balance_rows)==5
        for row,(source_value,reduced_value) in zip(balance_rows,balances):
            close_float(row['source_max_abs'],np.max(abs(source_value)),'source balance',atol=1e-9)
            close_float(row['reduced_max_abs'],np.max(abs(reduced_value)),'reduced balance',atol=1e-9)
        gross_rows=rows(dest/'gross_descriptive.csv');assert len(gross_rows)==4
        assert [row['observable'] for row in gross_rows]==FAST_IDS
        for row,j in zip(gross_rows,fast):
            close_float(row['full_window_rate_E_inf'],np.max(abs(a['source_rates'][:,j]-a['reduced_rates'][:,j]))/max(np.max(abs(a['source_rates'][:,j])),1e-9),'descriptive gross rate')
            close_float(row['full_window_gross_extent_E_inf'],np.max(abs(a['source_gross_extent'][:,j]-a['reduced_gross_extent'][:,j]))/max(np.max(abs(a['source_gross_extent'][:,j])),1e-6),'descriptive gross extent')
        state_rows=rows(dest/'state_errors.csv');slow_rows=rows(dest/'slow_total_errors.csv')
        current_rows=rows(dest/'net_current_errors.csv');extent_rows=rows(dest/'net_extent_errors.csv')
        for row in state_rows:
            assert row['contract_class']==('B' if row['observable'] in c['algebraically_affected_states'] else 'A')
        fastids=[membership[i]['channel_id'] for i in fastchannels]
        maximum=lambda table,predicate:max(float(row['E_inf']) for row in table if predicate(row))
        needed=lambda row:row['mandatory']=='True'
        maxima=dict(state=maximum(state_rows,needed),slow_total=maximum(slow_rows,lambda row:needed(row) and row['observable'] in ['T0','T1','B']),
           retained_coordinate=maximum(slow_rows,needed),protein=maximum(state_rows,lambda row:needed(row) and row['observable']=='Pept0003'),
           ck_net_current=maximum(current_rows,lambda row:needed(row) and row['observable'] in fastids),net_current=maximum(current_rows,needed),
           ck_net_extent=maximum(extent_rows,lambda row:needed(row) and row['observable'] in fastids),net_extent=maximum(extent_rows,needed),
           conservation=max(float(row['max_absolute_drift']) for row in rows(dest/'conservation.csv')),switch_jump_scaled=jump,
           ck_net_current_post_0p05=maximum(current_rows,lambda row:row['window']=='POST_0P05_DIAGNOSTIC' and row['observable'] in fastids))
        for key,value in maxima.items():close_float(result['maxima'][key],value,'condition maximum '+key)
        # Solver timestamps/hashes and native dense evidence prove fresh executions, not summary reuse.
        for kind in ['startup_primary','startup_probe','reduced_primary','reduced_probe']:
            assert (dest/(kind+'_dense.npz')).is_file()
            meta=load(dest/(kind+'_solver.json'))
            assert meta['complete'] and meta['end_s']==(switch if kind.startswith('startup') else 1000)
            assert meta['rtol']==(1e-11 if kind.endswith('probe') else 1e-10)
        condition_checks.append(dict(condition=name,status='PASS_INDEPENDENT_NUMERICAL_SCORE_RECOMPUTATION',classes=independent_classes))
        print('Independently verified',name,independent_classes,flush=True)
    checks.append(dict(check='INDEPENDENT_CANONICAL_CURRENT_RECONSTRUCTION_AND_SCORE_RECOMPUTATION',status='PASS',
                       max_current_scaled_identity_error=max_current_identity,max_affine_reconstruction_error=max_reconstruction,
                       conditions=condition_checks))
    summary=load(OUT/'formal_campaign_summary.json')
    assert summary['conditions_passing_all_mandatory_gates']==sum(r.get('all_mandatory_gates_pass',False) for r in all_results)
    assert summary['completed_conditions']==sum(r['status']=='COMPLETED' for r in all_results)
    views=[]
    for result in all_results:
        partial=OUT/'per_condition'/result['condition']/'run_001/state_current_assessment_001/assessment.json'
        views.append(result if result['status']=='COMPLETED' or not partial.exists() else dict(result,**{k:load(partial)[k] for k in ['maxima','state_status','class_status']}))
    for key,record in summary['worst'].items():
        measured=[r for r in views if r.get('maxima',{}).get(key) is not None]
        if not measured:assert record is None;continue
        worst=max(measured,key=lambda r:r['maxima'][key])
        assert record['condition']==worst['condition'] and record['measured_conditions']==len(measured)
        close_float(record['value'],worst['maxima'][key],'campaign maximum '+key)
    assert summary['state_valid_all_conditions']==all(r.get('state_status')=='STATE_VALID' for r in views)
    assert summary['conservation_all_resolved_pass']==all(r.get('class_status',{}).get('C')=='RESOLVED_PASS' for r in views)
    assert summary['state_current_assessments']==sum('class_status' in r for r in views)
    for cls,counts in summary['class_condition_counts'].items():
        for status,count in counts.items():
            expected=sum(r.get('class_status',{}).get(cls)==status for r in views)
            if cls in ['F','H']:
                expected+=sum(r['status']!='COMPLETED' and r.get('class_status',{}).get(cls) is None for r in views) if status=='NUMERICALLY_UNRESOLVED' else 0
            assert count==expected
    condition_table=rows(OUT/'condition_summary.csv');assert [row['condition_id'] for row in condition_table]==CONDITIONS
    for row,result in zip(condition_table,views):
        assert row['status']==result['status'] and row['state_status']==result.get('state_status','NOT_COMPLETED')
        assert row['all_mandatory_gates_pass']==str(result.get('all_mandatory_gates_pass',False))
        for cls in ['A','B','C','D']:
            assert row[cls]==result.get('class_status',{}).get(cls,'NOT_COMPLETED')
    for file in ['state_errors.csv','slow_total_errors.csv','net_current_errors.csv','conservation.csv']:
        combined=rows(OUT/file);expected=[]
        for result in all_results:
            folder=OUT/'per_condition'/result['condition']/'run_001'
            if not (folder/file).exists():folder=folder/'state_current_assessment_001'
            expected.extend(dict(condition_id=result['condition'],**row) for row in rows(folder/file))
        assert combined==expected,'Incorrect aggregate: '+file
    fastids=[membership[i]['channel_id'] for i in fastchannels]
    for record in summary['ck_window_maxima']:
        file='net_current_errors.csv' if record['metric']=='CK_NET_CURRENT' else 'net_extent_errors.csv'
        measured=[row for row in rows(OUT/file) if row['observable'] in fastids and row['window']==record['window'] and row['E_inf']!='']
        assert record['measured_conditions']==len({row['condition_id'] for row in measured})
        assert record['mandatory']==(record['window'] in ['FULL_WINDOW','POST_INITIAL_LAYER'])
        if measured:
            maximum=max(measured,key=lambda row:float(row['E_inf']))
            assert record['condition']==maximum['condition_id'] and record['observable']==maximum['observable']
            close_float(record['E_inf'],maximum['E_inf'],'CK window maximum')
        else:assert record['E_inf'] is None
    for record in summary['balance_summary']:
        measured=[dict(row,condition=row['condition_id']) for row in rows(OUT/'balance_accounting.csv')
                  if row['accounting']==record['accounting'] and row[record['model']+'_max_abs']!='']
        assert record['measured_conditions']==len(measured)
        if measured:
            maximum=max(measured,key=lambda row:float(row[record['model']+'_max_abs']))
            assert maximum['condition']==record['condition']
            close_float(record['max_absolute_residual'],maximum[record['model']+'_max_abs'],'campaign balance maximum')
        else:assert record['max_absolute_residual'] is None
    for result in all_results:
        name=result['condition'];folder=OUT/'per_condition'/name/'run_001'
        balances=[{k:v for k,v in row.items() if k!='condition_id'} for row in rows(OUT/'balance_accounting.csv') if row['condition_id']==name]
        gross=[{k:v for k,v in row.items() if k!='condition_id'} for row in rows(OUT/'gross_descriptive.csv') if row['condition_id']==name]
        assert len(balances)==5 and len(gross)==4
        assert all(row['mandatory']=='False' and 'BUT_NOT_VALIDATED' in row['status'] for row in gross)
        if result['status']=='COMPLETED':
            assert balances==rows(folder/'balance_accounting.csv') and gross==rows(folder/'gross_descriptive.csv')
        else:
            law=rows(folder/'state_current_assessment_001/conservation.csv')
            close_float(balances[0]['source_max_abs'],max(float(row['max_absolute_drift']) for row in law if row['model']=='SOURCE'),'partial C accounting')
            close_float(balances[0]['reduced_max_abs'],max(float(row['max_absolute_drift']) for row in law if row['model']=='CK_HYBRID'),'partial C accounting')
            assert all(row['source_max_abs']==row['reduced_max_abs']=='' for row in balances[1:])
            with np.load(folder/'state_current_assessment_001/instantaneous_comparison.npz') as a:
                for row,j in zip(gross,fast):
                    expected=np.max(abs(a['source_rates'][:,j]-a['reduced_rates'][:,j]))/max(np.max(abs(a['source_rates'][:,j])),1e-9)
                    close_float(row['full_window_rate_E_inf'],expected,'partial gross descriptive rate')
                    assert row['full_window_gross_extent_E_inf']==''
    if summary['state_valid_all_conditions'] and any(r.get('class_status',{}).get('D')=='RESOLVED_FAIL' for r in views):
        assert summary['candidate_outcome']=='CK_STATE_VALID_NET_CURRENT_FAIL'
        assert summary['recommendation']=='CK_STATE_REDUCTION_SUPPORTED_BUT_FLUX_NOT_READY'
    assert summary['no_promotion'] and summary['no_next_stage']
    assert not (OUT/'first_order').exists()
    for script in ['r6_ck_common_v1.py','run_r6_ck_formal_v1.py','score_r6_ck_formal_v1.py']:
        tree=ast.parse((ROOT/'scripts'/script).read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                name=getattr(node.func,'id',None) or getattr(node.func,'attr',None)
                assert name not in ['clip','curve_fit','least_squares']
    assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).strip()
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    manifest=load(OUT/'manifest.json')
    for rel,h in manifest['file_hashes'].items():assert sha(ROOT/rel)==h,rel
    eligible={p.relative_to(ROOT).as_posix() for p in OUT.rglob('*') if p.is_file() and
              p not in [OUT/'manifest.json',OUT/'verification.json',OUT/'verification_binding.json']}
    eligible.update(p.relative_to(ROOT).as_posix() for p in DOC.glob('r6_*.md'))
    eligible.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'scripts').glob('*r6*.py'))
    assert eligible==set(manifest['file_hashes']),'Incomplete final manifest coverage'
    report=dict(schema='R6_CK_FORMAL_INDEPENDENT_VERIFICATION_V1',status='PASS_ENGINEERING_AND_EVIDENCE_VERIFICATION',
        verified_at_utc=stamp(),checks=checks,scientific_outcome=summary['candidate_outcome'],
        recommendation=summary['recommendation'],conditions_passing_all_mandatory_gates=summary['conditions_passing_all_mandatory_gates'],
        scientific_promotion='NOT_APPROVED',historical_thresholds_unchanged=True,gross_not_mandatory=True)
    write_json(OUT/'verification.json',report)
    write_json(OUT/'verification_binding.json',dict(manifest_sha256=sha(OUT/'manifest.json'),verifier_sha256=sha(Path(__file__)),
        dispatch_verifier_sha256=sha(ROOT/'scripts/verify_r6_ck_validation_v1.py'),verification_sha256=sha(OUT/'verification.json')))
    print(json.dumps(report,indent=2),flush=True)
    return report

if __name__=='__main__':verify()
