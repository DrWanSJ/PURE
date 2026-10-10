"""Recompute all scores from immutable trajectories; never changes numerical gates."""
import csv
from runtime import *

def read_run(tag):
    p=RESULT/'trajectories'/tag;z=np.load(p.with_suffix('.npz'));a={k:z[k] for k in z.files};a['diagnostics']=load(p.with_suffix('.json'));return a

def main():
    protection();report=load(RESULT/'validation_results.json');cfg=load(CONFIG);windowrows=[];costrows=[];(RESULT/'errors').mkdir(exist_ok=True)
    for scenario in cfg['scenarios']:
        entry=report['scenarios'][scenario['id']];rt0=Runtime('R0',scenario);tight=read_run(scenario['id']+'__R0_TIGHT');base=read_run(scenario['id']+'__R0')
        entry['reference_convergence']['tight_BDF']=compare_observables(rt0,tight,base);ok=entry['reference_convergence']['tight_BDF']['source_reconstruction_numeric_error']<=cfg['gates']['exact_numeric_error']
        if scenario['id'] in cfg['independent_solver']['scenarios']:
            entry['reference_convergence']['independent_Radau']=compare_observables(rt0,tight,read_run(scenario['id']+'__R0_RADAU'));ok=ok and entry['reference_convergence']['independent_Radau']['source_reconstruction_numeric_error']<=cfg['gates']['exact_numeric_error']
        assert ok;entry['reference_converged']=True
        for model,row in entry['models'].items():
            if 'diagnostics' not in row:continue
            a=read_run(scenario['id']+'__'+model);rt=Runtime(model,scenario);comp=compare_observables(rt,tight,a)
            if model!='R0':
                row['comparison']=comp
                status='EXACT_REDUCTION_VERIFIED' if model in ['R1','R2','R3_RECYCLE'] else 'FULL_COUPLED_CANDIDATE_GATES_PASS'
                passed=(comp['source_reconstruction_numeric_error']<=cfg['gates']['exact_numeric_error'] and comp['physical_pass'] and comp['conservation_pass']) if model in ['R1','R2'] else comp['long_gates_pass']
                row['status']=status if passed else 'FAILED'
            for window in comp['windows']:windowrows.append({'scenario':scenario['id'],'model':model,**{k:json.dumps(v) if isinstance(v,list) else v for k,v in window.items()}})
            d=a['diagnostics'];costrows.append({k:d[k] for k in ['model','scenario','chemical_dimension','extra_counter_dimension','evaluated_mass_action_expressions','source_mapping_directions','jacobian_nnz_at_initial','jacobian_nnz_at_final','nfev','njev','nlu','seconds','minimum_source_representative','minimum_physical','max_conservation_abs']})
            labels,O,_=observable_matrix(rt.names);sc=fixed_scales(rt,labels);obs0=O@tight['X'];obs=O@a['X'];diff=(obs-obs0)/sc[:,None]
            fields=['time']+['NORM_ERROR_'+s for s in labels]+['NORM_CUM_ERROR_'+s for s in rt.counter_names]+['NORM_CURRENT_ERROR_'+s for s in rt.counter_names]
            cs=np.array([comp['counter_fixed_scales'][s] for s in rt.counter_names]);ce=(a['counters']-tight['counters'])/cs[:,None];fe=(a['currents']-tight['currents'])/cs[:,None]
            with (RESULT/'errors'/(scenario['id']+'__'+model+'.csv')).open('w',encoding='utf-8',newline='') as f:
                w=csv.writer(f);w.writerow(fields);w.writerows(np.column_stack([a['t'],diff.T,ce.T,fe.T]).tolist())
    for filename,rr in [('window_errors.csv',windowrows),('cost_and_feasibility.csv',costrows)]:
        with (RESULT/filename).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    report['observability_coverage']={'source_free_forms':'Includes EFTu_GTP, EFG_GTP and RS70S in addition to all preregistered resources and 8 bound-carrier projections.','stored_error_data':'errors/*.csv plus window_errors.csv','full_source_numerical_scales':'Frozen protected initial-stock scales; other source coordinates max(1,initial), Cr uses CP+Cr exact source-stock inventory. No trajectory-derived scale.'}
    report['score_code_sha256']=sha(Path(__file__));save(RESULT/'validation_results.json',report);print({s:{m:r['status'] for m,r in e['models'].items()} for s,e in report['scenarios'].items()})
if __name__=='__main__':main()
