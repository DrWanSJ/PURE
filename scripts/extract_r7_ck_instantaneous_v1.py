"""Retain completed A/B/C/D tiers while bounded net-extent quadrature proceeds."""
from r7_ck_h1_v1 import *
from r6_ck_common_v1 import metric_rows, gate_status
from r7_ck_first_order_runtime_v1 import evaluate, aggregate_status, MODELS
from extract_r6_ck_state_current_v1 import StoredDense

def main():
    checked_binding();allstate=[];allcons=[];allcurrent=[];summaries=[]
    for name in CONDITIONS:
        r=FirstOrderCK(name);dest=OUT/'per_condition'/name/'run_001';r6=ROOT/'results/reduction/r6_ck_validation/per_condition'/name/'run_001'
        with np.load(r6/'comparison.npz') as f:a={k:f[k].copy() for k in f.files}
        formal=evaluate(r,StoredDense(dest/'formal_primary_dense.npz'),a,False)
        probe=evaluate(r,StoredDense(dest/'formal_probe_dense.npz'),a,True)
        post=evaluate(r,StoredDense(r6/'reduced_primary_dense.npz'),a,False)
        postprobe=evaluate(r,StoredDense(r6/'reduced_probe_dense.npz'),a,True)
        t=a['times'];c=load(OUT/'numerical_contract.json')['r6_contract']
        sr=metric_rows(r.source.species,a['source'],formal['state'],a['source_probe'],probe['state'],t,r.switch,1e-6,.01,'STATE')
        for row in sr:row.update(condition=name,model=MODELS[2],contract_class='B' if row['observable'] in c['algebraically_affected_states'] else 'A')
        tr=metric_rows(r.labels,a['source']@r.T.T,formal['slow'],a['source_probe']@r.T.T,probe['slow'],t,r.switch,1e-6,.01,'SLOW_TOTAL_OR_COORDINATE')
        for row in tr:row.update(condition=name,model=MODELS[2],contract_class='A')
        cons=[]
        for model,state,pstate in [('SOURCE',a['source'],a['source_probe']),(MODELS[2],formal['state'],probe['state'])]:
            drift=r.law_drift(state);pd=r.law_drift(pstate)
            for k,law in enumerate(r.source.cert['law_ids']):
                e=float(np.max(abs(drift[:,k])));u=float(np.max(abs(drift[:,k]-pd[:,k])))
                cons.append(dict(condition=name,model=model,law=law,contract_class='C',max_absolute_drift=e,uncertainty=u,gate=1e-8,status=gate_status(e,u,1e-8)))
        extra=np.zeros_like(a['source_net'])
        for k,(f,b) in enumerate(r.channels):
            if b is not None:extra[:,k]=8*np.finfo(float).eps*(abs(a['source_rates'][:,f])+abs(a['source_rates'][:,b]))
        currents=[]
        for model,net,pnet in [(MODELS[0],a['reduced_net'],a['reduced_net_probe']),(MODELS[1],post['net'],postprobe['net']),(MODELS[2],formal['net'],probe['net'])]:
            cr=metric_rows(r.channel_ids,a['source_net'],net,a['source_net_probe'],pnet,t,r.switch,1e-9,.05,'NET_CURRENT',r.mandatory_channels,extra)
            for row in cr:row.update(condition=name,model=model,contract_class='D')
            currents.extend(cr)
        guard={k:aggregate_status([v for v in sr+tr if v['mandatory'] and v['contract_class']==k]) for k in ['A','B']};guard['C']=aggregate_status(cons)
        ds={window:aggregate_status([v for v in currents if v['model']==MODELS[2] and v['window']==window and v['mandatory']]) for window in ['FULL_WINDOW','POST_INITIAL_LAYER']}
        summary=dict(condition=name,guards=guard,D=ds,F='NOT_ASSESSED_BY_INSTANTANEOUS_EXTRACTOR',no_new_state_solve=True,extent_claim=False)
        write_json(dest/'instantaneous_assessment.json',summary)
        write_csv(dest/'instantaneous_state_guard.csv',sr+tr);write_csv(dest/'instantaneous_conservation_guard.csv',cons);write_csv(dest/'instantaneous_current_errors.csv',currents)
        np.savez_compressed(dest/'instantaneous_comparison.npz',times=t,switch=r.switch,formal_state=formal['state'],formal_state_probe=probe['state'],formal_slow=formal['slow'],formal_slow_probe=probe['slow'],formal_net=formal['net'],formal_net_probe=probe['net'],post_net=post['net'],post_net_probe=postprobe['net'])
        allstate.extend(sr+tr);allcons.extend(cons);allcurrent.extend(currents);summaries.append(summary)
        print(name,'completed instantaneous tiers',guard,ds,flush=True)
    write_json(OUT/'instantaneous_assessment.json',dict(conditions=summaries,net_extent_assessment='SEPARATE_BOUNDED_INTEGRATION',promotion=False))

if __name__=='__main__':main()
