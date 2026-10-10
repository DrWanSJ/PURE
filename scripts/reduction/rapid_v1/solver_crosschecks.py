"""Tight and independent algorithms for both exact and final candidate charts."""
from runtime import *
from validate import store_run
from score_saved import read_run

def main():
    protection();cfg=load(CONFIG);out=[]
    for scenario in cfg['scenarios']:
        if scenario['id'] not in cfg['independent_solver']['scenarios']:continue
        for model in ['R2','R3_CHAIN12_RECYCLE']:
            rt=Runtime(model,scenario);main_run=read_run(scenario['id']+'__'+model);tight=rt.simulate(cfg['tight_solver']);store_run(rt,tight,scenario['id']+'__'+model+'_TIGHT');settings={k:v for k,v in cfg['independent_solver'].items() if k!='scenarios'};radau=rt.simulate(settings);store_run(rt,radau,scenario['id']+'__'+model+'_RADAU')
            checks={'tight_BDF_vs_main':compare_observables(rt,tight,main_run),'independent_Radau_vs_tight':compare_observables(rt,tight,radau)}
            passed=all(c['source_reconstruction_numeric_error']<=cfg['gates']['exact_numeric_error'] for c in checks.values()) and tight['diagnostics']['success'] and radau['diagnostics']['success'];assert passed
            out.append({'scenario':scenario['id'],'model':model,'status':'PASS','checks':checks,'tight_diagnostics':tight['diagnostics'],'Radau_diagnostics':radau['diagnostics']});print(scenario['id'],model,'independent convergence PASS',flush=True)
    save(RESULT/'reduced_solver_crosschecks.json',out);report=load(RESULT/'validation_results.json');report['reduced_solver_crosschecks']=out;save(RESULT/'validation_results.json',report)
if __name__=='__main__':main()
