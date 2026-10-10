"""Frozen local fixtures, coupled comparisons, independent solver and timings."""
import argparse,traceback,time
from runtime import *
from mathematics import *
from scipy.integrate import solve_ivp

def store_run(rt,run,tag):
    p=RESULT/'trajectories'/tag
    np.savez_compressed(p.with_suffix('.npz'),**{k:v for k,v in run.items() if k!='diagnostics'})
    save(p.with_suffix('.json'),{**run['diagnostics'],'source_species_order':rt.names,'physical_labels':rt.labels,'counter_names':rt.counter_names,'config_sha256':sha(CONFIG),'runtime_sha256':sha(Path(__file__).with_name('runtime.py'))})
    append(RESULT/'execution_log.jsonl',{'operation':'solve_ivp','tag':tag,**run['diagnostics']})

def local_tests():
    names,rx,initial=source_network();S=np.asarray(matrix_source(names,rx).tolist(),float);idx={s:i for i,s in enumerate(names)};out=[];config=load(CONFIG);grid=np.array(config['observation_grid'])
    for round_ in [1,2]:
        c=CHAIN[round_-1];ids=[14,16,17,18,21] if round_==1 else [75,77,78,79,82];rr=[j for j,r in enumerate(rx) if int(r['id'][2:]) in ids];ks=np.array([float(rx[j]['k']) for j in rr]);stage0=next(iter(rx[rr[0]]['reactants']));endpoint=next(iter(rx[rr[3]]['products']))
        support=set(names);labels,P,H,_=physical_projection(names,support,[round_]);P=np.array(P.tolist(),float);H=np.array(H.tolist(),float);N=P@S[:,rr]
        for label,stock in [('UPSTREAM_PULSE',{stage0:1}),('INTERNAL_NONZERO',{stage0:.6,c['slow']:.3,c['fast']:.1,'EFTu_GDP':.1})]:
            x0=np.zeros(241)
            for s,v in stock.items():x0[idx[s]]=v
            def full(t,x):return S[:,rr]@np.array([ks[j]*x[idx[next(iter(rx[r]['reactants']))]] for j,r in enumerate(rr)])
            def reduced(t,y):
                x=H@y;v=np.array([ks[j]*x[idx[next(iter(rx[r]['reactants']))]] for j,r in enumerate(rr)])
                v[2]=v[3]=float(F(c['k']))*x[idx[c['slow']]]
                return N@v
            settings=config['tight_solver'];a=solve_ivp(full,(0,1000),x0,t_eval=grid,method='BDF',rtol=settings['rtol'],atol=settings['atol']);b=solve_ivp(reduced,(0,1000),P@x0,t_eval=grid,method='BDF',rtol=settings['rtol'],atol=settings['atol']);xx=H@b.y
            rows_=[idx[s] for s in [endpoint,'PO4','EFTu_GDP']];errors=np.abs(a.y[rows_]-xx[rows_]);windows=[]
            for low,high in config['windows']:
                mask=(grid>=low)&(grid<=high);windows.append({'range':[low,high],'product_error':float(errors[0,mask].max()),'resource_error':float(errors[1:,mask].max())})
            gate=windows[-1]['product_error']<=.05 and windows[-1]['resource_error']<=.05
            row={'candidate':'CHAIN_'+str(round_),'fixture':label,'actual_source_ids':[rx[j]['id'] for j in rr],'stock':stock,'windows':windows,'status':'PASS' if gate and a.success and b.success else 'FAILED','competition_split_source':float(a.y[idx['elRS70SAGGU0002_fMet' if round_==1 else 'elRS70SAGGU0003_Pept0002'],-1]),'competition_split_reduced':float(xx[idx['elRS70SAGGU0002_fMet' if round_==1 else 'elRS70SAGGU0003_Pept0002'],-1]),'unit_scale':1,'solver':settings,'local_not_full_coupled':True};out.append(row)
            np.savez_compressed(RESULT/'trajectories'/('LOCAL_CHAIN'+str(round_)+'_'+label+'.npz'),t=grid,source=a.y,reduced_representative=xx)
        bad=np.zeros(241);bad[idx[c['fast']]]=1
        assert np.min(P@bad)==-1
        out.append({'candidate':'CHAIN_'+str(round_),'fixture':'CHAIN_INTERNAL_DOMAIN','stock':{c['fast']:1,'EFTu_GDP':0},'status':'BLOCKED','reason':'Projected free EFTu_GDP=-1; no physically nonnegative reduced initial inventory. Cannot claim arbitrary internal-state domain.'})
    # Identical aggregates, distinct microscopic tail distributions: quotient exact,
    # individual path currents irrecoverable. Include ALL positive external inputs.
    charts=load(RESULT/'charts.json');c=charts['R3_RECYCLE'];block=rational_matrix(c['tail']['source_projection_rows']);kernel=block.nullspace();base=sp.ones(7,1)*10;k=kernel[0];a=base;b=base+k;assert min(b)>=0 and block*a==block*b
    tailids=c['tail_rate_indices'];D=sp.zeros(len(tailids),7)
    for j,rid in enumerate(tailids):D[j,TAIL.index(next(s for s in rx[rid]['factors'] if s!='k1'))]=1000
    P=sparse_rows(c['source_projection_sparse_rows'],241);tailpos=[idx[s] for s in TAIL];diff=P@S[:,tailids]@np.array((D*(a-b)).tolist(),float)
    assert np.max(np.abs(diff))<1e-10
    out.append({'candidate':'RECYCLE','fixture':'TAIL_UNOBSERVABLE','status':'PASS','state_a':{s:str(a[j]) for j,s in enumerate(TAIL)},'state_b':{s:str(b[j]) for j,s in enumerate(TAIL)},'same_aggregate':[str(n) for n in block*a],'projected_derivative_difference_max':float(np.max(np.abs(diff))),'individual_release_direction_flux_difference':[str(n) for n in D*(a-b)],'microstate_exact_reconstruction':'REJECTED','protected_aggregate_closure':'EXACT'})
    # Standalone tail pulses, with external injection source states 0306 and 0910.
    Sx=np.asarray(S);spec=[j for j,r in enumerate(rx) if r['id'] in ['re0000000306','re0000000910'] or j in tailids];A=np.zeros((241,241))
    for j in spec:
        assert len(rx[j]['factors'])==2
        q=idx[next(s for s in rx[j]['factors'] if s!='k1')];A[:,q]+=Sx[:,j]*float(rx[j]['k'])
    H=sparse_rows(c['source_lift_sparse_rows'],203);Ap=P@A@H
    assert np.max(np.abs(P@A-np.asarray(Ap@P)))<1e-9
    x0=np.zeros(241)
    for s in TAIL:x0[idx[s]]=0.1
    for rid in ['re0000000306','re0000000910']:
        r=next(r for r in rx if r['id']==rid);x0[idx[next(iter(r['reactants']))]]=0.2
    a=solve_ivp(lambda t,x:A@x,(0,1000),x0,method='BDF',jac=A,t_eval=grid,rtol=1e-11,atol=1e-13);b=solve_ivp(lambda t,y:Ap@y,(0,1000),P@x0,method='BDF',jac=Ap,t_eval=grid,rtol=1e-11,atol=1e-13)
    err=float(np.max(np.abs(P@a.y-b.y)));assert err<1e-8
    out.append({'candidate':'RECYCLE','fixture':'COUPLED_INPUT_PULSES_0306_0910','status':'PASS','max_projection_error':err,'source_directions':[rx[j]['id'] for j in spec],'physical_full_concentrations_min':float(a.y.min())})
    save(RESULT/'local_validation.json',out);return out

def pointwise_checks():
    from runtime_reconstruction_rhs import SourceCoordinateRuntime
    old=SourceCoordinateRuntime('source_coordinate_certificate_v4.json');config=load(CONFIG);out=[]
    for scenario in config['scenarios'][:4]:
        r=Runtime('R0',scenario);samples=[r.x0,r.x0+np.linspace(0.01,0.02,241)]
        for i,x in enumerate(samples):
            a=r.rhs(0,np.r_[x,np.zeros(r.nc)])[:241];b=np.array(old.full_rhs_from_rates(old.rates(x.tolist())));err=float(np.max(np.abs(a-b)/np.maximum(1,np.abs(b))));assert err<1e-12
            out.append({'scenario':scenario['id'],'sample':i,'independent_existing_runtime_RHS_error':err})
    # Analytical Jacobian tested at a positive state (directional central difference).
    for model in ['R0','R1','R2','R3_CHAIN12_RECYCLE']:
        rt=Runtime(model,config['scenarios'][0]);z=rt.aug0.copy();z[:rt.dim]+=.001;direction=np.sin(np.arange(len(z))+1);h=1e-6
        finite=(rt.rhs(0,z+h*direction)-rt.rhs(0,z-h*direction))/(2*h);exact=rt.jac(0,z)@direction;error=float(np.max(np.abs(finite-exact)/np.maximum(1,np.abs(exact))));assert error<1e-5
        out.append({'model':model,'analytical_jacobian_directional_error':error})
    save(RESULT/'runtime_independent_checks.json',out);return out

def main():
    protection();(RESULT/'trajectories').mkdir(exist_ok=True);pointwise=pointwise_checks();local=local_tests();cfg=load(CONFIG);report={'protocol_sha256':sha(DOC/'protocol.md'),'config_sha256':sha(CONFIG),'pointwise':pointwise,'local':local,'scenarios':{},'performance':{},'scientific_status':'HUMAN_REVIEW_REQUIRED'}
    models=['R0','R1','R2','R3_CHAIN1','R3_CHAIN12','R3_RECYCLE','R3_CHAIN12_RECYCLE']
    for scenario in cfg['scenarios']:
        runs={};entry={'role':scenario['role'],'models':{},'reference_convergence':{}};report['scenarios'][scenario['id']]=entry
        for model in models:
            tag=scenario['id']+'__'+model
            try:
                rt=Runtime(model,scenario);run=rt.simulate();store_run(rt,run,tag);runs[model]=run;entry['models'][model]={'diagnostics':run['diagnostics']}
                if not run['diagnostics']['success']:failure('SOLVER_NONCOMPLETION',tag=tag,diagnostics=run['diagnostics'])
            except Exception as e:
                entry['models'][model]={'status':'BLOCKED' if isinstance(e,ValueError) else 'INCONCLUSIVE','reason':str(e)};failure('RUNTIME',tag=tag,error=traceback.format_exc());continue
        if 'R0' not in runs or not runs['R0']['diagnostics']['success']:save(RESULT/'validation_results.json',report);continue
        rt0=Runtime('R0',scenario);tight=rt0.simulate(cfg['tight_solver']);store_run(rt0,tight,scenario['id']+'__R0_TIGHT');conv=compare_observables(rt0,tight,runs['R0']);entry['reference_convergence']['tight_BDF']=conv
        reference_ok=tight['diagnostics']['success'] and conv['source_reconstruction_numeric_error']<=cfg['gates']['exact_numeric_error']
        if scenario['id'] in cfg['independent_solver']['scenarios']:
            settings={k:v for k,v in cfg['independent_solver'].items() if k!='scenarios'};radau=rt0.simulate(settings);store_run(rt0,radau,scenario['id']+'__R0_RADAU');check=compare_observables(rt0,tight,radau);entry['reference_convergence']['independent_Radau']=check;reference_ok=reference_ok and radau['diagnostics']['success'] and check['source_reconstruction_numeric_error']<=cfg['gates']['exact_numeric_error']
        entry['reference_converged']=bool(reference_ok)
        for model,run in runs.items():
            if model=='R0':entry['models'][model]['status']='REFERENCE_CONVERGED' if reference_ok else 'INCONCLUSIVE';continue
            rt=Runtime(model,scenario);comp=compare_observables(rt,tight,run);entry['models'][model]['comparison']=comp
            if not reference_ok:status='INCONCLUSIVE'
            elif model in ['R1','R2']:status='EXACT_REDUCTION_VERIFIED' if comp['source_reconstruction_numeric_error']<=cfg['gates']['exact_numeric_error'] and comp['physical_pass'] and comp['conservation_pass'] else 'FAILED'
            elif model=='R3_RECYCLE':status='EXACT_REDUCTION_VERIFIED' if comp['long_gates_pass'] else 'FAILED'
            else:status='FULL_COUPLED_CANDIDATE_GATES_PASS' if comp['long_gates_pass'] else 'FAILED'
            entry['models'][model]['status']=status
            if status in ['FAILED','INCONCLUSIVE']:failure('COUPLED_VALIDATION',tag=scenario['id']+'__'+model,status=status,comparison=comp)
        save(RESULT/'validation_results.json',report)
        print(json.dumps({'scenario':scenario['id'],'reference_ok':reference_ok,'states':{m:v['status'] for m,v in entry['models'].items()}}),flush=True)
    # Predeclared same-hardware 3-repeat medians; all solver configurations identical.
    baseline=cfg['scenarios'][0]
    for model in models:
        rt=Runtime(model,baseline);repeats=[]
        for repeat in range(cfg['performance_repeats']):
            a=rt.simulate();repeats.append(a['diagnostics']);append(RESULT/'execution_log.jsonl',{'operation':'performance_repeat','repeat':repeat,**a['diagnostics']})
        report['performance'][model]={'repeats':repeats,'median_seconds':float(np.median([a['seconds'] for a in repeats]))}
    base=report['performance']['R0']['median_seconds']
    for model,p in report['performance'].items():p['speedup_vs_R0']=base/p['median_seconds']
    report['protection']=protection();save(RESULT/'validation_results.json',report)
    print(json.dumps({'performance':{m:{k:v for k,v in p.items() if k!='repeats'} for m,p in report['performance'].items()}}),flush=True)
if __name__=='__main__':
    try:main()
    except Exception:failure('VALIDATION_PROGRAM',error=traceback.format_exc());raise
