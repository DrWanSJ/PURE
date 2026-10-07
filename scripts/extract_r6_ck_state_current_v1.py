"""Recover completed state/current evidence separately from ongoing extent work."""
from r6_ck_common_v1 import *

class StoredDense:
    def __init__(self,path):
        with np.load(path) as a:self.data={k:a[k].copy() for k in a.files}
    def __call__(self,t):
        d=self.data;i=max(0,min(int(np.searchsorted(d['steps'],t,side='left'))-1,len(d['order'])-1))
        order=int(d['order'][i]);products=np.cumprod((t-d['t_shift'][i,:order])/d['denom'][i,:order])
        return d['D'][i,0]+d['D'][i,1:order+1].T@products

def extract(name):
    c=checked_contract();base=OUT/'per_condition'/name/'run_001'
    required=[base/(kind+'_dense.npz') for kind in ['startup_primary','startup_probe','reduced_primary','reduced_probe']]
    if not all(p.exists() for p in required):return None
    dest=base/'state_current_assessment_001'
    if (dest/'assessment.json').exists():return load(dest/'assessment.json')
    dest.mkdir(exist_ok=True);r=FormalCK(name);sd,sp,rd,rp=[StoredDense(p) for p in required]
    ts=np.r_[0.,np.geomspace(r.switch/1000,r.switch,100)];t=np.unique(np.r_[TIMES,ts])
    def source(full,probe):
        directory=ROOT/'results/reduction/r4_fast_block_screen/source_uncertainty'/name if probe else historical_path(name)
        with np.load(directory/('probe_state.npz' if probe else 'full_state.npz')) as a:grid=a['state'].copy()
        x=np.array([full(tt) if tt<=r.switch else grid[np.flatnonzero(TIMES==tt)[0]] for tt in t])
        v=np.array([r.rates(xx) for xx in x]);net=np.array([r.channel_net(vv) for vv in v]);return x,v,net
    xs,vs,ns=source(sd,False);xp,vp,np_=source(sp,True)
    def reduced(full,slow):
        x=[];v=[];net=[];z=[]
        for tt in t:
            if tt<r.switch:
                xx=full(tt);vv=r.rates(xx);nn=r.channel_net(vv);zz=r.T@xx
            else:
                dz=slow(tt);xx,nn,vv,*_=r.reduced_observables(dz);zz=r.z0+dz
            x.append(xx);v.append(vv);net.append(nn);z.append(zz)
        return np.array(x),np.array(v),np.array(net),np.array(z)
    xr,vr,nr,zr=reduced(sd,rd);xrp,vrp,nrp,zrp=reduced(sp,rp)
    sr=metric_rows(r.source.species,xs,xr,xp,xrp,t,r.switch,1e-6,.01,'STATE')
    for row in sr:row['contract_class']='B' if row['observable'] in c['algebraically_affected_states'] else 'A'
    tr=metric_rows(r.labels,xs@r.T.T,zr,xp@r.T.T,zrp,t,r.switch,1e-6,.01,'SLOW_TOTAL_OR_COORDINATE')
    for row in tr:row['contract_class']='A'
    extra=np.zeros_like(ns)
    for i,(j,k) in enumerate(r.channels):
        if k is not None:extra[:,i]=8*np.finfo(float).eps*(abs(vs[:,j])+abs(vs[:,k]))
    cr=metric_rows(r.channel_ids,ns,nr,np_,nrp,t,r.switch,1e-9,.05,'NET_CURRENT',r.mandatory_channels,extra)
    for row in cr:row['contract_class']='D'
    ld=r.law_drift(xs);lrd=r.law_drift(xr);lp=r.law_drift(xp);lrp=r.law_drift(xrp)
    lr=[]
    for i,n in enumerate(r.source.cert['law_ids']):
        for model,a,b in [('SOURCE',ld,lp),('CK_HYBRID',lrd,lrp)]:
            e=float(np.max(abs(a[:,i])));u=float(np.max(abs(a[:,i]-b[:,i])))
            lr.append(dict(observable=n,model=model,contract_class='C',mandatory=True,
                           max_absolute_drift=e,uncertainty=u,gate=1e-8,status=gate_status(e,u,1e-8)))
    active=[row for row in sr+tr+cr+lr if row['mandatory']]
    classes={}
    for cls in ['A','B','C','D']:
        values=[row['status'] for row in active if row['contract_class']==cls]
        classes[cls]='RESOLVED_FAIL' if 'RESOLVED_FAIL' in values else ('NUMERICALLY_UNRESOLVED' if 'NUMERICALLY_UNRESOLVED' in values else 'RESOLVED_PASS')
    fastids=[r.channel_ids[i] for i in r.fast_channels]
    maxima=dict(state=max(row['E_inf'] for row in sr if row['mandatory']),
                slow_total=max(row['E_inf'] for row in tr if row['mandatory'] and row['observable'] in ['T0','T1','B']),
                retained_coordinate=max(row['E_inf'] for row in tr if row['mandatory']),
                protein=max(row['E_inf'] for row in sr if row['mandatory'] and row['observable']=='Pept0003'),
                ck_net_current=max(row['E_inf'] for row in cr if row['mandatory'] and row['observable'] in fastids),
                net_current=max(row['E_inf'] for row in cr if row['mandatory']),
                ck_net_current_post_0p05=max(row['E_inf'] for row in cr if row['window']=='POST_0P05_DIAGNOSTIC' and row['observable'] in fastids),
                conservation=max(row['max_absolute_drift'] for row in lr))
    np.savez_compressed(dest/'instantaneous_comparison.npz',times=t,switch=r.switch,source=xs,reduced=xr,
        source_probe=xp,reduced_probe=xrp,source_rates=vs,reduced_rates=vr,source_net=ns,reduced_net=nr,
        source_net_probe=np_,reduced_net_probe=nrp,reduced_slow=zr,probe_slow=zrp,T=r.T,Xz=r.Xz,D=r.D,
        x0=r.x0,channel_ids=np.array(r.channel_ids),mandatory_channels=np.array(r.mandatory_channels),
        coordinate_labels=np.array(r.labels),source_law_drift=ld,reduced_law_drift=lrd,source_law_probe=lp,reduced_law_probe=lrp)
    for file,data in [('state_errors.csv',sr),('slow_total_errors.csv',tr),('net_current_errors.csv',cr),('conservation.csv',lr)]:write_csv(dest/file,data)
    statevalid=classes['A']==classes['B']=='RESOLVED_PASS'
    report=dict(schema='R6_COMPLETED_STATE_CURRENT_EVIDENCE_V1',condition=name,
        status='COMPLETE_INSTANTANEOUS_OBSERVABLES_ONLY',class_status=classes,maxima=maxima,
        state_status='STATE_VALID' if statevalid else 'STATE_NOT_VALIDATED',
        net_current_status='NET_CURRENT_VALIDATED' if classes['D']=='RESOLVED_PASS' else 'NET_CURRENT_NOT_VALIDATED',
        extent_status='NOT_ASSESSED_BY_THIS_EXTRACTOR',initial_layer_full_gate='NOT_ASSESSED_BY_THIS_EXTRACTOR',
        scientific_status='CK_STATE_VALID_NET_CURRENT_FAIL' if statevalid and classes['D']=='RESOLVED_FAIL' else 'CK_NUMERICALLY_UNRESOLVED',
        resolved_fail_count=sum(row['status']=='RESOLVED_FAIL' for row in active),
        unresolved_count=sum(row['status']=='NUMERICALLY_UNRESOLVED' for row in active),promotion=False,
        no_new_state_solve=True,no_extent_claim=True,no_threshold_change=True,extracted_at_utc=stamp(),
        dense_input_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in required},
        output_hashes={p.name:sha(p) for p in dest.iterdir() if p.is_file() and p.name!='assessment.json'})
    write_json(dest/'assessment.json',report)
    print(name,'separate state/current evidence',classes,maxima,flush=True)
    return report

if __name__=='__main__':
    for name in CONDITIONS:extract(name)
