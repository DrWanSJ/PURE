"""Only three authorized first-order CK comparisons; preserve noncompletion."""
from r7_ck_h1_v1 import *
from r6_ck_common_v1 import metric_rows, gate_status
from run_r6_ck_formal_v1 import state_solve
from extract_r6_ck_state_current_v1 import StoredDense
from scipy.integrate import solve_ivp
import argparse, time, traceback, json

MODELS=['ZERO_ORDER_R6','FIRST_ORDER_POSTPROCESSING_ON_Z0','FORMAL_FIRST_ORDER_SELF_CONSISTENT']

def extent(r,dense,a,probe,tight,label,dest):
    times=a['times'];values=np.zeros((len(times),678));total=np.zeros(678);comp=np.zeros(678)
    initial=a['source_extent_probe' if probe else 'source_extent']
    rtol,atol=(1e-11,1e-15) if probe or tight else (1e-10,1e-14)
    clock=time.monotonic();last=clock;counts=[]
    for k,(ta,tb) in enumerate(zip(times[:-1],times[1:]),1):
        if tb<=r.switch:
            total=initial[k].copy();values[k]=total;continue
        def fun(t,_):
            if time.monotonic()-clock>1800:raise RuntimeError('FROZEN_EXTENT_COMPUTATIONAL_BOUND')
            return r.observables(dense(t))[1]
        sol=solve_ivp(fun,(float(ta),float(tb)),np.zeros(678),method='DOP853',rtol=rtol,atol=atol)
        if not sol.success:raise RuntimeError(sol.message)
        delta=sol.y[:,-1]-comp;new=total+delta;comp=(new-total)-delta;total=new;values[k]=total
        counts.append(dict(segment=k,time_s=float(tb),nfev=sol.nfev,elapsed_s=time.monotonic()-clock))
        if time.monotonic()-last>30:
            print(r.condition,label,'extent t=',float(tb),flush=True)
            write_json(dest/(label+'_extent_progress.json'),counts[-1]);last=time.monotonic()
    write_csv(dest/(label+'_extent_steps.csv'),counts)
    write_json(dest/(label+'_extent_solver.json'),dict(complete=True,elapsed_s=time.monotonic()-clock,rtol=rtol,atol=atol,channels=678,gross_scored=False))
    return values

def evaluate(r,dense,a,probe):
    state=[];net=[];z=[];dh=[];jj=[]
    for k,t in enumerate(a['times']):
        if t<r.switch:
            x=a['source_probe' if probe else 'source'][k];n=a['source_net_probe' if probe else 'source_net'][k];zz=r.T@x;dd=np.zeros(2);j1=np.zeros(2)
        else:
            dz=dense(t);x,n,c,dd,j1=r.observables(dz);zz=r.z0+dz
        state.append(x);net.append(n);z.append(zz);dh.append(dd);jj.append(j1)
    return dict(state=np.array(state),net=np.array(net),slow=np.array(z),dh1flow=np.array(dh),j1=np.array(jj))

def aggregate_status(table):
    statuses=[x['status'] for x in table]
    assert statuses
    if 'RESOLVED_FAIL' in statuses:return 'RESOLVED_FAIL'
    if 'NUMERICALLY_UNRESOLVED' in statuses:return 'NUMERICALLY_UNRESOLVED'
    return 'RESOLVED_PASS'

def crossings(times,v):
    result=[]
    for k in range(len(times)-1):
        if v[k]==0:result.append(dict(time_s=float(times[k]),bracket=[float(times[k]),float(times[k])],kind='SAMPLED_EXACT_ZERO'))
        elif v[k]*v[k+1]<0:
            result.append(dict(time_s=float(times[k]+(times[k+1]-times[k])*abs(v[k])/(abs(v[k])+abs(v[k+1]))),bracket=[float(times[k]),float(times[k+1])],kind='LINEAR_DIAGNOSTIC_WITH_BRACKET'))
    return json.dumps(result,separators=(',',':'))

def score(name,dest,write=True):
    import json
    r=FirstOrderCK(name);contract=load(OUT/'numerical_contract.json')['r6_contract']
    with np.load(dest/'comparison.npz') as f:a={k:f[k].copy() for k in f.files}
    t=a['times'];tables=[];summary=[];currents={};extents={}
    currentextra=np.zeros_like(a['source_net']);extentcancel=np.zeros_like(a['source_extent'])
    for k,(f,b) in enumerate(r.channels):
        if b is not None:
            currentextra[:,k]=8*np.finfo(float).eps*(abs(a['source_rates'][:,f])+abs(a['source_rates'][:,b]))
            extentcancel[:,k]=8*np.finfo(float).eps*(abs(a['source_gross_extent'][:,f])+abs(a['source_gross_extent'][:,b]))
    for model,key in zip(MODELS,['zero','post','formal']):
        extras=extentcancel+abs(a[key+'_tight_extent']-a[key+'_extent'])
        cr=metric_rows(r.channel_ids,a['source_net'],a[key+'_net'],a['source_net_probe'],a[key+'_net_probe'],t,r.switch,1e-9,.05,'NET_CURRENT',r.mandatory_channels,currentextra)
        er=metric_rows(r.channel_ids,a['source_extent'],a[key+'_extent'],a['source_extent_probe'],a[key+'_extent_probe'],t,r.switch,1e-6,.01,'NET_EXTENT',r.mandatory_channels,extras)
        for rows_,category in [(cr,'D'),(er,'F')]:
            for row in rows_:row.update(condition=name,model=model,contract_class=category)
        currents[model]=cr;extents[model]=er
        for window in ['FULL_WINDOW','POST_INITIAL_LAYER','POST_0P05_DIAGNOSTIC','COMPOSITE_OR_HYBRID']:
            for rows_,category in [(cr,'D'),(er,'F')]:
                subset=[v for v in rows_ if v['window']==window];ck=[v for v in subset if v['observable'] in [r.channel_ids[k] for k in r.fast_channels]]
                mandatory=[v for v in subset if v['mandatory']]
                summary.append(dict(condition=name,model=model,category=category,window=window,
                    CK_max_E_inf=max(v['E_inf'] for v in ck),CK_max_uncertainty=max(v['uncertainty'] for v in ck),
                    all_mandatory_max_E_inf=max(v['E_inf'] for v in mandatory) if mandatory else None,
                    CK_status=aggregate_status(ck) if mandatory else 'DESCRIPTIVE',
                    all_mandatory_status=aggregate_status(mandatory) if mandatory else 'DESCRIPTIVE'))
        tables.extend(cr+er)
    st=metric_rows(r.source.species,a['source'],a['formal_state'],a['source_probe'],a['formal_state_probe'],t,r.switch,1e-6,.01,'STATE')
    for row in st:row.update(condition=name,model=MODELS[2],contract_class='B' if row['observable'] in contract['algebraically_affected_states'] else 'A')
    slow=metric_rows(r.labels,a['source']@r.T.T,a['formal_slow'],a['source_probe']@r.T.T,a['formal_slow_probe'],t,r.switch,1e-6,.01,'SLOW_TOTAL_OR_COORDINATE')
    for row in slow:row.update(condition=name,model=MODELS[2],contract_class='A')
    cons=[]
    for model,key,pkey in [('SOURCE','source','source_probe'),(MODELS[2],'formal_state','formal_state_probe')]:
        drift=r.law_drift(a[key]);pdrift=r.law_drift(a[pkey])
        for k,law in enumerate(r.source.cert['law_ids']):
            e=float(np.max(abs(drift[:,k])));u=float(np.max(abs(drift[:,k]-pdrift[:,k])))
            cons.append(dict(condition=name,model=model,law=law,contract_class='C',max_absolute_drift=e,uncertainty=u,gate=1e-8,status=gate_status(e,u,1e-8)))
    states=[v for v in st+slow if v['mandatory']]
    guards={cls:aggregate_status([v for v in states if v['contract_class']==cls]) for cls in ['A','B']}
    guards['C']=aggregate_status(cons)
    detailed=[]
    for model,key in zip(MODELS,['zero','post','formal']):
        for k in r.fast_channels:
            for row in [v for v in currents[model] if v['observable']==r.channel_ids[k]]:
                mask=t>=0 if row['window'] in ['FULL_WINDOW','COMPOSITE_OR_HYBRID'] else t>= (r.switch if row['window']=='POST_INITIAL_LAYER' else .05)
                indices=np.flatnonzero(mask);worst=indices[np.argmax(abs(a[key+'_net'][mask,k]-a['source_net'][mask,k]))]
                q=dict(row);q.update(time_of_worst_error_s=float(t[worst]),signed_source_at_worst=float(a['source_net'][worst,k]),signed_model_at_worst=float(a[key+'_net'][worst,k]),
                    source_signs=json.dumps(sorted(set(np.sign(a['source_net'][mask,k]).astype(int).tolist()))),
                    model_signs=json.dumps(sorted(set(np.sign(a[key+'_net'][mask,k]).astype(int).tolist()))),
                    source_zero_crossings=crossings(t[mask],a['source_net'][mask,k]),model_zero_crossings=crossings(t[mask],a[key+'_net'][mask,k]),
                    integrated_source_contribution=float(a['source_extent'][-1,k]-a['source_extent'][indices[0],k]),
                    integrated_model_contribution=float(a[key+'_extent'][-1,k]-a[key+'_extent'][indices[0],k]))
                detailed.append(q)
    if write:
        write_csv(dest/'observable_scores.csv',tables);write_csv(dest/'condition_summary.csv',summary)
        write_csv(dest/'state_guard.csv',st+slow);write_csv(dest/'conservation_guard.csv',cons)
        write_csv(dest/'current_physics_diagnostics.csv',detailed)
    return dict(guards=guards,summary=summary,state_max_error=max(v['E_inf'] for v in states),
        conservation_max_drift=max(v['max_absolute_drift'] for v in cons))

def run(name):
    import json
    checked_binding();assert load(OUT/'structure_verification.json')['status']=='PASS'
    dest=OUT/'per_condition'/name/'run_001';dest.mkdir(parents=True,exist_ok=True)
    with (dest/'execution_claim.json').open('x',encoding='utf-8') as f:json.dump(dict(condition=name,started_utc=stamp(),registration_sha256=sha(OUT/'registration_binding.json')),f)
    r6=ROOT/'results/reduction/r6_ck_validation/per_condition'/name/'run_001'
    result=dict(condition=name,status='RUNNING',started_utc=stamp(),promotion=False)
    write_json(dest/'result.json',result)
    try:
        with np.load(r6/'comparison.npz') as f:a={k:f[k].copy() for k in f.files}
        r=FirstOrderCK(name);contract=load(OUT/'numerical_contract.json')['r6_contract']
        assert np.array_equal(r.x0,a['x0']) and r.switch==float(a['switch'])
        rd,rs=state_solve(r,'formal_primary',r.switch,1000,r.T@a['full_switch_state']-r.z0,1e-10,1e-14,dest,contract)
        pd,ps=state_solve(r,'formal_probe',r.switch,1000,r.T@a['full_switch_probe']-r.z0,1e-11,1e-15,dest,contract)
        z0=StoredDense(r6/'reduced_primary_dense.npz');zp=StoredDense(r6/'reduced_probe_dense.npz')
        data={k:a[k] for k in ['times','source','source_probe','source_net','source_net_probe','source_extent','source_extent_probe','source_rates','source_gross_extent','full_switch_state','full_switch_probe']}
        data.update(zero_net=a['reduced_net'],zero_net_probe=a['reduced_net_probe'],zero_extent=a['reduced_extent'],zero_extent_probe=a['reduced_extent_probe'],zero_tight_extent=a['same_trajectory_tight_extent'],switch=r.switch,tau0=r.tau0,x0=r.x0)
        for key,primary,probe in [('post',z0,zp),('formal',rd,pd)]:
            p=evaluate(r,primary,a,False);q=evaluate(r,probe,a,True)
            for target,value in p.items():data[key+'_'+target]=value
            for target,value in q.items():data[key+'_'+target+'_probe']=value
            data[key+'_extent']=extent(r,primary,a,False,False,key+'_primary',dest)
            data[key+'_extent_probe']=extent(r,probe,a,True,False,key+'_probe',dest)
            data[key+'_tight_extent']=extent(r,primary,a,False,True,key+'_same_trajectory_tight',dest)
        np.savez_compressed(dest/'comparison.npz',**data)
        scored=score(name,dest)
        boundary=np.flatnonzero(a['times']==r.switch)[0]
        scale=np.maximum(np.max(abs(a['source']),axis=0),1e-6)
        margins=[];material=False
        accepted=StoredDense(dest/'formal_primary_dense.npz').data
        for tt,dz in zip(accepted['steps'],accepted['accepted']):
            c=r.core(dz);x=c['x']+c['e'];margin=x[r.ix];budget=.01*scale[r.ix]
            margins.append(dict(time_s=float(tt),min_physical_margin=float(margin.min()),
                min_fast_total=float(c['z'][:3].min()),negative_beyond_state_budget=bool(np.any(margin < -budget))))
            material|=bool(np.any(margin < -budget))
        jump=data['formal_state'][boundary]-a['full_switch_state']
        details=dict(switch_s=r.switch,tau0_s=r.tau0,scaled_switch_jump=float(np.max(abs(jump)/scale)),
            switch_jump=jump.tolist(),retained_switch_continuity=float(np.max(abs(r.T@jump))),
            startup_states_byte_identical=bool(np.array_equal(data['formal_state'][a['times']<r.switch],a['source'][a['times']<r.switch])),
            startup_extents_byte_identical=bool(np.array_equal(data['formal_extent'][boundary],a['source_extent'][boundary])),
            minimum_accepted_physical_margin=min(v['min_physical_margin'] for v in margins),
            minimum_accepted_fast_total=min(v['min_fast_total'] for v in margins),
            new_material_domain_failure=material,historical_H_unchanged=True)
        write_csv(dest/'accepted_domain_diagnostics.csv',margins);write_json(dest/'initial_layer_diagnostics.json',details)
        result.update(status='COMPLETED',completed_utc=stamp(),primary_solver=rs,probe_solver=ps,
            guards=scored['guards'],state_max_error=scored['state_max_error'],conservation_max_drift=scored['conservation_max_drift'],new_material_domain_failure=material)
    except Exception as exc:
        result.update(status='NUMERICAL_NONCOMPLETION',failure=str(exc),completed_utc=stamp(),promotion=False)
        (dest/'traceback.log').write_text(traceback.format_exc(),encoding='utf-8',newline='\n')
    write_json(dest/'result.json',result)
    print(name,result['status'],result.get('guards'),flush=True)
    return result

if __name__=='__main__':
    import json
    parser=argparse.ArgumentParser();parser.add_argument('--condition',choices=CONDITIONS,required=True);args=parser.parse_args();run(args.condition)
