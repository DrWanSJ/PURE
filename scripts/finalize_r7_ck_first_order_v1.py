"""Assemble the bounded R7 evidence package and exactly one recommendation."""
from r7_ck_h1_v1 import *
from r6_ck_common_v1 import rows
import subprocess

def main():
    checked_binding();summaries=[];states=[];cons=[];post=[];formal=[];extent=[];physics=[];results=[]
    for name in CONDITIONS:
        dest=OUT/'per_condition'/name/'run_001';result=load(dest/'result.json');results.append(result)
        if result['status']!='COMPLETED':continue
        summaries.extend(rows(dest/'condition_summary.csv'));states.extend(rows(dest/'state_guard.csv'));cons.extend(rows(dest/'conservation_guard.csv'));physics.extend(rows(dest/'current_physics_diagnostics.csv'))
        r=FirstOrderCK(name)
        with np.load(dest/'comparison.npz') as f:a={k:f[k] for k in f.files}
        for key,table in [('post',post),('formal',formal)]:
            for k,t in enumerate(a['times']):
                for j,ch in enumerate(r.fast_channels):
                    table.append(dict(condition=name,time_s=float(t),pair=r.channel_ids[ch],source_current=float(a['source_net'][k,ch]),zero_order_current=float(a['zero_net'][k,ch]),first_order_current=float(a[key+'_net'][k,ch]),j1=float(a[key+'_j1'][k,j]),Dh1_F0=float(a[key+'_dh1flow'][k,j]),outer=bool(t>=r.switch)))
        for k,t in enumerate(a['times']):
            for ch in r.fast_channels:
                extent.append(dict(condition=name,time_s=float(t),pair=r.channel_ids[ch],source_extent=float(a['source_extent'][k,ch]),zero_order_extent=float(a['zero_extent'][k,ch]),postprocessed_extent=float(a['post_extent'][k,ch]),formal_extent=float(a['formal_extent'][k,ch]),startup_retained=bool(t<=r.switch)))
    for path,table in [('condition_summary.csv',summaries),('state_guard.csv',states),('conservation_guard.csv',cons),('first_order_postprocessing_current.csv',post),('first_order_self_consistent_current.csv',formal),('first_order_net_extent.csv',extent),('current_physics_diagnostics.csv',physics)]:
        if table:write_csv(OUT/path,table)
        else:(OUT/path).write_text('status\nNOT_ASSESSED_NUMERICAL_NONCOMPLETION\n',encoding='utf-8',newline='\n')
    completed=all(r['status']=='COMPLETED' for r in results)
    statesok=completed and all(all(v=='RESOLVED_PASS' for v in r['guards'].values()) for r in results)
    required=[v for v in summaries if v['model']=='FORMAL_FIRST_ORDER_SELF_CONSISTENT' and v['window'] in ['FULL_WINDOW','POST_INITIAL_LAYER']]
    fluxok=completed and len(required)==12 and all(v['all_mandatory_status']=='RESOLVED_PASS' for v in required)
    domainok=completed and not any(r.get('new_material_domain_failure',True) for r in results)
    ready=statesok and fluxok and domainok
    def improvement(category):
        comparisons=[]
        for condition in CONDITIONS:
            for window in ['FULL_WINDOW','POST_INITIAL_LAYER']:
                choose=lambda model:next((float(v['CK_max_E_inf']) for v in summaries if v['condition']==condition and v['model']==model and v['category']==category and v['window']==window),None)
                zero=choose('ZERO_ORDER_R6');new=choose('FORMAL_FIRST_ORDER_SELF_CONSISTENT')
                comparisons.append(zero is not None and new is not None and new<zero)
        return all(comparisons)
    Dbetter=improvement('D');Fbetter=improvement('F')
    scales=rows(OUT/'h1_scale_diagnostics.csv');not_small=any(v['not_small_flag']=='True' for v in scales)
    unresolved=not completed or any(v['all_mandatory_status']=='NUMERICALLY_UNRESOLVED' for v in required)
    if unresolved:recommend='CK_FIRST_ORDER_NUMERICALLY_UNRESOLVED'
    elif ready:recommend='CK_FIRST_ORDER_NET_FLUX_READY_FOR_BROAD_VALIDATION'
    elif not_small:recommend='CK_FIRST_ORDER_CORRECTION_NOT_SMALL_AT_ETA1'
    elif Dbetter and not Fbetter:recommend='CK_FIRST_ORDER_IMPROVES_CURRENT_NOT_EXTENT'
    elif Fbetter and not Dbetter:recommend='CK_FIRST_ORDER_IMPROVES_EXTENT_NOT_CURRENT'
    elif statesok and Dbetter and Fbetter:recommend='CK_FIRST_ORDER_STATE_OK_FLUX_IMPROVED_BUT_STILL_FAILS'
    else:recommend='CK_FIRST_ORDER_NO_MATERIAL_IMPROVEMENT'
    decision=dict(schema='R7_ADVANCEMENT_DECISION_V1',recommendation=recommend,
        conditions=CONDITIONS,completed=completed,A_B_C_pass_all_three=statesok,
        D_F_both_windows_all_mandatory_pass=fluxok,no_new_material_domain_failure=domainok,
        advancement_requirements_met=ready,recommend_later_nine_condition_validation=ready,
        D_improves_each_condition_both_windows=Dbetter,F_improves_each_condition_both_windows=Fbetter,
        descriptive_flags=['FIRST_ORDER_CORRECTION_NOT_SMALL'] if not_small else [],
        action='STOP_BOUNDED_R7_NO_BROAD_RUN',scientific_promotion=False,
        PURE_reduced_core='NOT_VALIDATED',mechanistic_decisions={'count':968,'status':'PENDING'},
        gross_status='SOURCE_PROVENANCE_PRESERVED;DESCRIPTIVE;BUT_NOT_VALIDATED',historical_R6_H_unchanged=True,
        numerical_results=results,registration_sha256=sha(OUT/'registration_binding.json'))
    write_json(OUT/'advancement_decision.json',decision)
    provenance=load(OUT/'input_provenance.json');dh=rows(OUT/'dh1_verification.csv');hs=rows(OUT/'h1_samples.csv')
    text=['# R7 CK first-order feasibility summary','',f'**{recommend}**. Exactly three diagnostic conditions; no promotion or broader run.','',
        '## Actual lineage','',f"R6 execution parent: `{provenance['r6_execution_parent_sha']}`. R6 final execution state: uncommitted, final commit SHA N/A. Local byte-preservation commit: `{provenance['r6_local_preservation_sha']}`. origin/main at inspection: `{provenance['origin_main_sha']}`.",
        '', 'All 3079 pre-R7 files are snapshot-bound and read-only. This work is additive on branch codex/r7-ck-first-order-20261008. The R6 preservation commit records its existing evidence; it is not a new R6 execution.',
        '', '## Derived correction','',
        'h1 was derived from the exact R5 eta-scaled canonical family. F and G0 are eta-independent in the frozen chart. j0 reproduces the existing finite R6 redistribution current. j1 follows the next invariance coefficient without constructing h2. The formal slow RHS is the Taylor truncation F0+Fq*h1, not nonlinear substitution.',
        '',f"Maximum ||h1||/fast-state scale: {max(float(v['correction_over_fast_state']) for v in scales):.12g}; maximum ||h1||/fast-total scale: {max(float(v['correction_over_fast_total']) for v in scales):.12g}. These eta=1 size diagnostics are descriptive.",
        f"Gq condition range: {min(float(v['Gq_condition']) for v in hs):.12g} to {max(float(v['Gq_condition']) for v in hs):.12g}; minimum singular value: {min(float(v['Gq_min_singular']) for v in hs):.12g} s^-1.",
        f"Independent analytic-versus-complex-step Dh1 maximum relative error: {max(float(v['complex_step_relative_error']) for v in dh):.12g}. Richardson finite-difference maximum relative discrepancy: {max(float(v['richardson_relative_error']) for v in dh):.12g}; complex-step is the independent verifier because finite differences can lose significance on near-zero slopes.",
        '', '## CK net-current and cumulative net-extent scaled errors','',
        '| Condition | Class/window | R6 zero order | Postprocessing on z0 | Formal first order | Formal CK status |','|---|---|---:|---:|---:|---|']
    for name in CONDITIONS:
        for cat in ['D','F']:
            for window in ['FULL_WINDOW','POST_INITIAL_LAYER']:
                selected=[next(v for v in summaries if v['condition']==name and v['model']==m and v['category']==cat and v['window']==window) for m in ['ZERO_ORDER_R6','FIRST_ORDER_POSTPROCESSING_ON_Z0','FORMAL_FIRST_ORDER_SELF_CONSISTENT']]
                text.append(f"| {name} | {cat} {window} | "+' | '.join(f"{float(v['CK_max_E_inf']):.10g}" for v in selected)+f" | {selected[-1]['CK_status']} |")
    text+=['','The formal advancement rule also checks every frozen R6 mandatory slow channel; all-channel scores and uncertainty are retained in condition_summary.csv and per-condition observable_scores.csv. Floors, windows and budgets are unchanged.', '', '## State guards and boundary/domain diagnostics','']
    for r in results:
        detail=load(OUT/'per_condition'/r['condition']/'run_001/initial_layer_diagnostics.json') if r['status']=='COMPLETED' else {}
        text.append(f"- {r['condition']}: {r.get('guards',{})}; maximum state/coordinate error {r.get('state_max_error','N/A')}; conservation drift {r.get('conservation_max_drift','N/A')}; switch scaled jump {detail.get('scaled_switch_jump','N/A')}; physical-domain minimum {detail.get('minimum_accepted_physical_margin','N/A')}; material new domain failure {r.get('new_material_domain_failure','N/A')}.")
    text+=['', 'Historical R6 H is preserved exactly. Fresh formal primary/probe trajectories use identical original retained switch coordinates and source startup; cumulative net extents retain the source startup integral.', '', '## ATP-low post-layer current interpretation','']
    selected=[v for v in physics if v['condition']=='R3_ATP_LOW' and v['model']=='ZERO_ORDER_R6' and v['window']=='POST_INITIAL_LAYER']
    if selected:
        worst=max(selected,key=lambda v:float(v['E_inf']))
        text+=[f"R6 worst post-layer CK pair: `{worst['observable']}`. Scaled error {worst['E_inf']}, maximum absolute error {worst['max_absolute_error']} concentration/s, source scale {worst['reference_scale']}, floor {worst['floor']}, worst time {worst['time_of_worst_error_s']} s. At that time signed source current {worst['signed_source_at_worst']} and R6 current {worst['signed_model_at_worst']}. Source zero crossings: {worst['source_zero_crossings']}. Model zero crossings: {worst['model_zero_crossings']}. Post-layer integrated source contribution {worst['integrated_source_contribution']}, zero-order contribution {worst['integrated_model_contribution']}."]
    text+=['','The boundary-inclusive post-layer normalization is reported together with its physical absolute scale and cumulative contribution. A large relative score near a small signed source signal does not by itself measure a large sustained absolute turnover error. The full-window and post-0.05 diagnostics remain separate; the formal post-layer score is never replaced.',
        '', '## Bounded decision','',f"A/B/C all resolved pass: {statesok}. D/F all mandatory rows in both windows pass: {fluxok}. No material new domain failure: {domainok}. All advancement requirements met: {ready}.",
        f"Formal current decreases in each condition/both windows: {Dbetter}; formal extent decreases in each condition/both windows: {Fbetter}.",
        f"Exactly one primary recommendation: **{recommend}**.",
        '', 'STOP after this report. No nine-condition first-order campaign has run. No push, merge, CK promotion or aminoacylation work. E/G remain descriptive BUT_NOT_VALIDATED. PURE_reduced_core remains NOT_VALIDATED and all 968 mechanistic decisions remain PENDING. Engineering verifier success does not confer scientific promotion.']
    (ROOT/'docs/reduction/r7_ck_first_order_summary.md').write_text('\n'.join(text)+'\n',encoding='utf-8',newline='\n')
    nodes=[]
    for rel,kind,role in [('docs/reduction/r7_ck_first_order_derivation_v1.md','INFERRED','math derived from exact family'),('results/reduction/r7_ck_first_order/input_provenance.json','EXTRACTED','input hashes and actual lineage'),('results/reduction/r7_ck_first_order/condition_summary.csv','EXTRACTED','measured comparisons'),('results/reduction/r7_ck_first_order/advancement_decision.json','INFERRED','registered bounded decision')]:
        nodes.append(dict(path=rel,status=kind,role=role,sha256=sha(ROOT/rel),authoritative=False))
    write_json(OUT/'evidence_navigation.json',dict(schema='R7_DERIVED_NAVIGATION_V1',nodes=nodes,
        edges=[dict(source=nodes[0]['path'],target=nodes[2]['path'],relation='IMPLEMENTS'),dict(source=nodes[2]['path'],target=nodes[3]['path'],relation='PREREGISTERED_RULE')],freshness='SHA256_CHECK_REQUIRED',source_authority=False,
        ambiguities=['Absolute biochemical unit metadata remains qualified','R6 final execution was uncommitted'],promotion=False))
    paths=list(OUT.rglob('*'))+list((ROOT/'docs/reduction').glob('r7*md'))+list((ROOT/'scripts').glob('*r7*py'))
    write_json(OUT/'manifest.json',dict(schema='R7_MANIFEST_V1',files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths) if p.is_file() and p.name not in ['manifest.json','verification.json','final_commit_receipt.json']},
        registration_sha256=sha(OUT/'registration_binding.json'),pre_r7_file_count=3079,conditions=CONDITIONS,promotion=False))
    print(recommend,'advancement',ready,flush=True)

if __name__=='__main__':main()
