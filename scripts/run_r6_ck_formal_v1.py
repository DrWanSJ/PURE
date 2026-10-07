"""Fresh CK hybrid solves and independent net/gross extent bookkeeping, nine cases."""
from r6_ck_common_v1 import *
from scipy.integrate import BDF, solve_ivp, OdeSolution
import argparse, platform, time, traceback

class Bound(RuntimeError): pass

def state_solve(r, kind, start, end, x0, rtol, atol, dest, contract):
    full=kind.startswith('startup')
    clock=time.monotonic();last=clock;calls=0;steps=[start];states=[x0.copy()];pieces=[];solver=None
    def fun(t,y):
        nonlocal calls
        calls+=1
        if calls>contract['bounds']['state_rhs_calls'] or time.monotonic()-clock>contract['bounds']['state_wall_s']:
            raise Bound('FROZEN_STATE_COMPUTATIONAL_BOUND')
        return r.full_rhs(t,y,1) if full else r.reduced_rhs_delta(t,y)
    jac=(lambda t,x:r.S@rate_jacobian(r.source,x)) if full else r.reduced_jac_delta
    try:
        solver=BDF(fun,start,x0,end,jac=jac,rtol=rtol,atol=atol)
        while solver.status=='running':
            message=solver.step()
            if solver.status=='failed': raise Bound(message)
            if solver.t>steps[-1]:
                steps.append(float(solver.t));states.append(solver.y.copy());pieces.append(solver.dense_output())
            if time.monotonic()-last>30:
                write_json(dest/(kind+'_progress.json'),dict(time_s=solver.t,rhs_calls=calls,elapsed_s=time.monotonic()-clock))
                np.savez_compressed(dest/(kind+'_checkpoint.npz'),time_s=solver.t,state=solver.y)
                print(r.condition,kind,'t=',solver.t,'calls=',calls,flush=True);last=time.monotonic()
        dense=OdeSolution(np.array(steps),pieces)
        # Native dense polynomial coefficients, without pickle or interpolation of sparse samples.
        dimension=len(x0);D=np.zeros((len(pieces),6,dimension));shift=np.zeros((len(pieces),5));denom=np.ones((len(pieces),5));orders=[]
        for i,piece in enumerate(pieces):
            orders.append(piece.order);D[i,:piece.order+1]=piece.D
            shift[i,:piece.order]=piece.t_shift;denom[i,:piece.order]=piece.denom
        np.savez_compressed(dest/(kind+'_dense.npz'),steps=np.array(steps),accepted=np.array(states),
                            order=np.array(orders),D=D,t_shift=shift,denom=denom)
        stats=dict(complete=True,start_s=start,end_s=end,rtol=rtol,atol=atol,rhs_calls=calls,
                   nfev=solver.nfev,njev=solver.njev,nlu=solver.nlu,accepted_steps=len(steps),
                   minimum_accepted_coordinate=float(np.min(states)),elapsed_s=time.monotonic()-clock)
        write_json(dest/(kind+'_solver.json'),stats)
        return dense,stats
    except Exception:
        np.savez_compressed(dest/(kind+'_partial.npz'),steps=np.array(steps),accepted=np.array(states))
        raise

def extent_solve(r,dense,times,kind,dest,contract,rtol=1e-10,atol=1e-14,startup=None):
    clock=time.monotonic();values=np.zeros((len(times),1646));counts=[];total=np.zeros(1646);comp=np.zeros(1646)
    for i,(a,b) in enumerate(zip(times[:-1],times[1:]),1):
        if startup is not None and b<=r.switch:
            values[i]=startup[i];total=values[i].copy();comp=np.zeros(1646);continue
        is_startup=startup is None
        def fun(t,_y):
            if time.monotonic()-clock>contract['bounds']['extent_wall_s']:raise Bound('FROZEN_EXTENT_COMPUTATIONAL_BOUND')
            if is_startup:
                x=dense(t);v=r.rates(x);net=r.channel_net(v)
            else:
                x,net,v,*_=r.reduced_observables(dense(t))
            return np.r_[net,v]
        sol=solve_ivp(fun,(float(a),float(b)),np.zeros(1646),method='DOP853',rtol=rtol,atol=atol)
        if not sol.success:raise Bound(sol.message)
        delta=sol.y[:,-1]-comp;new=total+delta;comp=(new-total)-delta;total=new;values[i]=total
        counts.append(dict(segment=i,end_s=float(b),nfev=sol.nfev,elapsed_s=time.monotonic()-clock))
        if i%25==0:
            write_json(dest/(kind+'_extent_progress.json'),counts[-1])
    write_csv(dest/(kind+'_extent_steps.csv'),counts)
    write_json(dest/(kind+'_extent_solver.json'),dict(segments=len(counts),rtol=rtol,atol=atol,
               elapsed_s=time.monotonic()-clock,nfev=sum(v['nfev'] for v in counts),
               net_count=678,gross_count=968,gross_gate=False))
    return values

def source_arrays(r,startup_dense,startup_values,times,probe):
    base=ROOT/'results/reduction/r4_fast_block_screen/source_uncertainty'/r.condition if probe else historical_path(r.condition)
    file=base/('probe_state.npz' if probe else 'full_state.npz')
    with np.load(file) as a:x=a['state'].copy()
    with np.load(base/('probe_ledgers.npz' if probe else 'directed_ledgers.npz')) as a:
        v=a['rates' if probe else 'full_rates'].copy();xi=a['extent' if probe else 'full_extent'].copy()
    states=[];nets=[];raw=[];extents=[]
    for t in times:
        if t<=r.switch:
            k=np.flatnonzero(times[times<=r.switch]==t)[0]
            xx=startup_dense(t);vv=r.rates(xx);n=r.channel_net(vv);e=startup_values[k]
        else:
            k=np.flatnonzero(TIMES==t)[0];xx=x[k];vv=v[k];n=r.channel_net(vv);e=np.r_[r.channel_net(xi[k]),xi[k]]
        states.append(xx);nets.append(n);raw.append(vv);extents.append(e)
    return dict(state=np.array(states),net=np.array(nets),gross=np.array(raw),extent=np.array(extents))

def run(name):
    contract=checked_contract();reuse=load(OUT/'source_reuse_verification.json')
    assert reuse['status']=='PASS' and name in CONDITIONS
    for record in reuse['conditions']:
        for path,h in record['file_hashes'].items():assert sha(ROOT/path)==h
    dest=OUT/'per_condition'/name/'run_001'
    dest.mkdir(parents=True,exist_ok=True)
    with (dest/'execution_claim.json').open('x',encoding='utf-8') as f:
        json.dump(dict(condition=name,started_at_utc=stamp(),pid=os.getpid(),
                       registration_sha256=sha(OUT/'formal_registration_binding.json')),f,indent=2)
    result=dict(condition=name,status='RUNNING',started_at_utc=stamp(),fresh_reduced=True,
                historical_reduced_reused=False,promotion=False,
                contract_sha256=sha(OUT/'formal_numerical_contract.json'),
                registration_sha256=sha(OUT/'formal_registration_binding.json'),
                reuse_sha256=sha(OUT/'source_reuse_verification.json'),
                runtime_sha256=sha(ROOT/'scripts/r6_ck_common_v1.py'),runner_sha256=sha(Path(__file__)),
                python=platform.python_version(),numpy=np.__version__,platform=platform.platform())
    write_json(dest/'result.json',result)
    try:
        r=FormalCK(name)
        ts=np.r_[0.,np.geomspace(r.switch/1000,r.switch,100)]
        times=np.unique(np.r_[TIMES,ts]);nstart=len(ts)
        # Every condition uses the unmodified original condition, eta=1 and the frozen R5 switch.
        sd,ss=state_solve(r,'startup_primary',0,r.switch,r.x0,1e-10,1e-14,dest,contract)
        sp,sps=state_solve(r,'startup_probe',0,r.switch,r.x0,1e-11,1e-15,dest,contract)
        sv=extent_solve(r,sd,ts,'startup_primary',dest,contract)
        svp=extent_solve(r,sp,ts,'startup_probe',dest,contract,1e-11,1e-15)
        dz0=r.T@sd(r.switch)-r.z0;dzp0=r.T@sp(r.switch)-r.z0
        rd,rs=state_solve(r,'reduced_primary',r.switch,1000.,dz0,1e-10,1e-14,dest,contract)
        pd,ps=state_solve(r,'reduced_probe',r.switch,1000.,dzp0,1e-11,1e-15,dest,contract)
        source=source_arrays(r,sd,sv,times,False);source_probe=source_arrays(r,sp,svp,times,True)
        def evaluate(full,slow):
            xx=[];nn=[];vv=[];zz=[]
            for t in times:
                if t<r.switch:
                    x=full(t);v=r.rates(x);net=r.channel_net(v);dz=r.T@x-r.z0
                else:
                    dz=slow(t);x,net,v,*_=r.reduced_observables(dz)
                xx.append(x);nn.append(net);vv.append(v);zz.append(r.z0+dz)
            return dict(state=np.array(xx),net=np.array(nn),gross=np.array(vv),slow=np.array(zz))
        red=evaluate(sd,rd);probe=evaluate(sp,pd)
        red['extent']=extent_solve(r,rd,times,'reduced_primary',dest,contract,startup=sv)
        probe['extent']=extent_solve(r,pd,times,'reduced_probe',dest,contract,1e-11,1e-15,startup=svp)
        tight=extent_solve(r,rd,times,'same_trajectory_tight_extent',dest,contract,1e-11,1e-15,startup=sv)
        np.savez_compressed(dest/'comparison.npz',times=times,switch=r.switch,tau0=r.tau0,
             source=source['state'],reduced=red['state'],source_probe=source_probe['state'],reduced_probe=probe['state'],
             reduced_slow=red['slow'],probe_slow=probe['slow'],
             source_net=source['net'],reduced_net=red['net'],source_net_probe=source_probe['net'],reduced_net_probe=probe['net'],
             source_rates=source['gross'],reduced_rates=red['gross'],
             source_extent=source['extent'][:,:678],reduced_extent=red['extent'][:,:678],
             source_extent_probe=source_probe['extent'][:,:678],reduced_extent_probe=probe['extent'][:,:678],
             source_gross_extent=source['extent'][:,678:],reduced_gross_extent=red['extent'][:,678:],
             same_trajectory_tight_extent=tight[:,:678],x0=r.x0,
             full_switch_state=sd(r.switch),reduced_switch_state=r.manifold_delta(dz0)[0],
             full_switch_probe=sp(r.switch),reduced_switch_probe=r.manifold_delta(dzp0)[0],
             channel_ids=np.array(r.channel_ids),mandatory_channels=np.array(r.mandatory_channels),
             coordinate_labels=np.array(r.labels),T=r.T,Xz=r.Xz,D=r.D,
             source_law_drift=r.law_drift(source['state']),reduced_law_drift=r.law_drift(red['state']),
             source_law_probe=r.law_drift(source_probe['state']),reduced_law_probe=r.law_drift(probe['state']),
             minimum_primary_accepted_dz=rs['minimum_accepted_coordinate'])
        result.update(status='COMPLETED',completed_at_utc=stamp(),switch_s=r.switch,tau0_s=r.tau0,
                      primary_solver=rs,probe_solver=ps,startup_primary_solver=ss,startup_probe_solver=sps,
                      initial_state_sha256=hashlib.sha256(r.x0.tobytes()).hexdigest(),
                      minimum_reported_full_state=float(np.min(source['state'])),
                      minimum_reported_reduced_state=float(np.min(red['state'])),
                      full_initial_layer_retained=True,no_clipping=True,no_fitting=True,no_time_shift=True)
        from score_r6_ck_formal_v1 import score_condition
        scored=score_condition(name,dest,write=True)
        result.update(scored)
    except Exception as exc:
        result.update(status='NUMERICAL_NONCOMPLETION',completed_at_utc=stamp(),failure=str(exc),
                      scientific_status='CK_NUMERICALLY_UNRESOLVED',promotion=False)
        (dest/'traceback.log').write_text(traceback.format_exc(),encoding='utf-8',newline='\n')
    result['output_hashes']={p.name:sha(p) for p in sorted(dest.iterdir()) if p.is_file() and p.name!='result.json'}
    write_json(dest/'result.json',result)
    print(name,result['status'],result.get('scientific_status'),result.get('maxima'),flush=True)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--condition',choices=CONDITIONS);args=parser.parse_args()
    for name in ([args.condition] if args.condition else CONDITIONS):run(name)
