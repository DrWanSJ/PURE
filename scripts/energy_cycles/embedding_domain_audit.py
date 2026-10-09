"""Test candidate graph feasibility on actual full-reference boundary histories."""
import json
from pathlib import Path
import numpy as np
from runtime import Module, DomainFailure, ROOT, OUT, sha, write_json

def main():
    d=json.loads((OUT/'source_inventory.json').read_text())
    path=OUT/'full_reference_retry1/tight.npz';q=np.load(path);names=list(q['species']);t=q['time'];x=q['concentrations']
    evidence={'source_commit':d['source_commit'],'reference_trajectory_sha256':sha(path),'status':'CANDIDATE_GRAPH_FEASIBILITY_DIAGNOSTIC_NOT_FULL_EMBEDDING',
      'scope':'Every actual source free resource plus that energy enzyme bound-form inventory; other source reactions are external to each module. No reduced ODE is run.',
      'units':{},'command':['python','scripts/energy_cycles/embedding_domain_audit.py']}
    for u in d['units']:
        m=Module(d,u);xs=x[:,[names.index(s) for s in m.species]];T=xs@m.A.T;E=xs[:,len(m.B):len(m.B)+len(m.E)].sum(axis=1)
        failures=[];feasible=[]
        for j,tt in enumerate(t):
            try:
                xx,_,res,sing=m.closure(T[j],E[j]);feasible.append({'time':float(tt),'max_residual':res,'min_free':float(np.min(xx[:len(m.B)]))})
            except DomainFailure as err:
                failures.append({'time':float(tt),'error':str(err),'retained_totals':dict(zip(m.B,map(float,T[j])))})
        evidence['units'][u['name']]={'physical_samples':len(feasible),'failed_samples':len(failures),'failures':failures,
            'first_failure':failures[0] if failures else None,'first_feasible_after_failure':next((r for r in feasible if failures and r['time']>failures[0]['time']),None),
            'decision':'FULL_REPLACEMENT_BLOCKED_AT_AUTHOR_INITIAL_LAYER' if failures else 'SAMPLED_GRAPH_FEASIBLE_NOT_EMBEDDING_VALIDATED'}
    write_json(OUT/'embedding_domain_audit.json',evidence)
    print(json.dumps({n:{k:v[k] for k in ['physical_samples','failed_samples','first_failure']} for n,v in evidence['units'].items()}))

if __name__=='__main__':main()
