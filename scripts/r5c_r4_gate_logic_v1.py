"""Additive uncertainty-aware gate audit; reads frozen arrays, never solves."""
from r5_common_v1 import ROOT, write_csv, write_json
from r4_fast_block_common_v1 import REG, R4FamilyRuntime, source_data, historical_path, condition_initial
from run_r3_coupled_grid_v1 import stable_slow_balance
from validate_source_coordinates_full_v1 import stable_material_balance
import numpy as np
import csv, json
OUT = ROOT/'results/reduction/r5c_corrigendum'

def characterize(error, uncertainty, budget, threshold, envelope):
    if uncertainty > budget: return 'NUMERICALLY_UNRESOLVED'
    if max(0.,error-envelope) > threshold: return 'RESOLVED_FAIL'
    if error+envelope < threshold: return 'RESOLVED_PASS'
    return 'NUMERICALLY_UNRESOLVED'

def audit():
    rows=[]; post=[]; differences=[]
    for family in ['GlyRS','MetRS']:
        r=R4FamilyRuntime(family); s=r.source
        aa={v['reaction_id'] for v in csv.DictReader((ROOT/'models/pnas2017_full_reference/audit/aminoacylation_reactions.csv').open())}
        ai=np.array([i for i,v in enumerate(s.reactions) if v['id'] in aa])
        for c in REG['conditions']:
            name=c['condition_id']; p=ROOT/'results/reduction/r4_fast_block_screen'/(family.lower()+'_only')/name
            tp=p/'state_trajectories.npz'
            if not tp.exists(): tp=p/'recovered_state_trajectories.npz'
            st=np.load(tp); full=st['full_state']; red=st['reduced_state']; z=st['reduced_slow']; t=st['times']
            led=np.load(p/'directed_ledgers.npz'); probe=np.load(p/'uncertainty_reduced_ledgers.npz')
            sp=ROOT/'results/reduction/r4_fast_block_screen/source_uncertainty'/name
            sf=np.load(sp/'probe_state.npz')['state']; sl=np.load(sp/'probe_ledgers.npz')
            x0=condition_initial(s,name)
            sc=np.maximum(np.max(abs(full),axis=0),1e-6); vs=np.maximum(np.max(abs(led['full_rates']),axis=0),1e-9); es=np.maximum(np.max(abs(led['full_extent']),axis=0),1e-6)
            measured={'state':float(np.max(abs(full-red)/sc)), 'rate':float(np.max((abs(led['full_rates']-led['reduced_rates'])/vs)[:,ai])), 'extent':float(np.max((abs(led['full_extent']-led['reduced_extent'])/es)[:,ai]))}
            fb=stable_material_balance(s,full,led['full_extent'],x0); rb=stable_slow_balance(r,z,led['reduced_extent'],r.T@x0)
            measured['balance']=float(max(np.max(abs(fb)),np.max(abs(rb))))
            sr={'state':float(np.max(abs(sf-full)/sc)), 'rate':float(np.max((abs(sl['rates']-led['full_rates'])/vs)[:,ai])), 'extent':float(np.max((abs(sl['extent']-led['full_extent'])/es)[:,ai]))}
            rr={'state':float(np.max(abs(probe['state']-red)/sc)), 'rate':float(np.max((abs(probe['rates']-led['reduced_rates'])/vs)[:,ai])), 'extent':float(np.max((abs(probe['extent']-led['reduced_extent'])/es)[:,ai]))}
            sr['balance']=float(np.max(abs(stable_material_balance(s,sf,sl['extent'],x0)-fb)))
            rr['balance']=float(np.max(abs(stable_slow_balance(r,probe['slow'],probe['extent'],r.T@x0)-rb)))
            tight=float(np.max(abs(stable_slow_balance(r,z,led['tight_reduced_extent'],r.T@x0)-rb)))
            rep=float(max(np.max((abs(r.S)@abs(led['full_extent']).T).T),np.max((abs(r.TS)@abs(led['reduced_extent']).T).T))*np.finfo(float).eps)
            view=json.loads((p/'derived_review_result.json').read_text())
            for gate in measured:
                threshold=REG['gates']['process_rate' if gate=='rate' else gate]; u=max(sr[gate],rr[gate],tight if gate=='balance' else 0.,rep if gate=='balance' else 0.)
                envelope=u if gate=='balance' else sr[gate]+rr[gate]
                status=characterize(measured[gate],u,REG['uncertainty']['tier_fraction']*threshold,threshold,envelope)
                differences.append(abs(u-view['uncertainty'][gate])); differences.append(abs(measured[gate]-view['maxima'][gate if gate!='balance' else 'full_balance_abs']) if gate!='balance' else abs(measured[gate]-max(view['maxima']['full_balance_abs'],view['maxima']['reduced_slow_balance_abs'])))
                rows.append(dict(candidate='R4_'+family.upper()+'_ONLY',condition=name,gate=gate,mandatory=True,threshold=threshold,measured_error=measured[gate],uncertainty=u,uncertainty_budget=REG['uncertainty']['tier_fraction']*threshold,source_probe_uncertainty=sr[gate],reduced_probe_uncertainty=rr[gate],comparison_envelope=envelope,lower_bound=max(0.,measured[gate]-envelope),upper_bound=measured[gate]+envelope,gate_status=status,decisive_against_all_gate_pass=status=='RESOLVED_FAIL',historical_tier_classification=view['tier_scientific_status'][gate],historical_overall_status=view['scientific_status'],uncertainty_interpretation='EMPIRICAL_REGISTERED_PROBE_ENVELOPE_NOT_RIGOROUS_BOUND',evidence_path=p.relative_to(ROOT).as_posix()))
            post.append(dict(candidate='R4_'+family.upper()+'_ONLY',condition=name,post_0p05_state_error=float(np.max((abs(full-red)/sc)[t>=.05])),source=tp.relative_to(ROOT).as_posix()))
            # Engineering closure guard is separate from four scientific tiers.
            bound=view['closure_counters']['max_residual']; rows.append(dict(candidate='R4_'+family.upper()+'_ONLY',condition=name,gate='closure_engineering',mandatory=True,threshold=REG['gates']['closure_engineering'],measured_error=bound,uncertainty='',uncertainty_budget='',source_probe_uncertainty='',reduced_probe_uncertainty='',comparison_envelope='',lower_bound='',upper_bound='',gate_status='ENGINEERING_GUARD_RECORDED',decisive_against_all_gate_pass=False,historical_tier_classification=str(view['raw_gate_pass']['closure_engineering']),historical_overall_status=view['scientific_status'],uncertainty_interpretation='NOT_A_SCIENTIFIC_ACCURACY_TIER',evidence_path=(p/'derived_review_result.json').relative_to(ROOT).as_posix()))
            if family=='GlyRS':
                hp=historical_path(name)/'state_trajectories.npz'; h=np.load(hp)
                post.append(dict(candidate='HISTORICAL_R3_21',condition=name,post_0p05_state_error=float(np.max((abs(h['full_state']-h['reduced_state'])/sc)[t>=.05])),source=hp.relative_to(ROOT).as_posix()))
            print('R4 arrays audited',family,name,flush=True)
    assert max(differences)<1e-12, max(differences)
    summary={'historical_overall_status_preserved':'NUMERICALLY_UNRESOLVED','maximum_difference_from_historical_derived_scores_uncertainty':max(differences),'post_0p05_worst':{n:max(v['post_0p05_state_error'] for v in post if v['candidate']==n) for n in sorted({v['candidate'] for v in post})},'family_screen_outcome':'BOTH_FAMILY_CANDIDATES_FAIL_REGISTERED_GATE_SCREEN','combined_failure_causal_interpretation':'UNDETERMINED','counts':{g:{k:sum(v['gate']==g and v['gate_status']==k for v in rows) for k in ['RESOLVED_FAIL','RESOLVED_PASS','NUMERICALLY_UNRESOLVED']} for g in ['state','rate','extent','balance']},'every_family_condition_has_decisive_state_rate_fail':all(any(v['candidate']=='R4_'+f.upper()+'_ONLY' and v['condition']==c['condition_id'] and v['gate']==g and v['gate_status']=='RESOLVED_FAIL' for v in rows) for f in ['GlyRS','MetRS'] for c in REG['conditions'] for g in ['state','rate'])}
    assert summary['every_family_condition_has_decisive_state_rate_fail']
    return rows,post,summary

if __name__=='__main__':
    rows,post,summary=audit(); write_csv(OUT/'r4_decisive_gate_logic.csv',rows); write_csv(OUT/'r4_post_layer_errors.csv',post); write_json(OUT/'r4_gate_summary.json',summary); print(summary)
