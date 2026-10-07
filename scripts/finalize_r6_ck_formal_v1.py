"""Close out the registered nine-condition CK campaign without promotion."""
from r6_ck_common_v1 import *

def evidence_view(original):
    """Keep original noncompletion; add independently extractable completed tiers."""
    name=original['condition'];base=OUT/'per_condition'/name/'run_001'
    partial=base/'state_current_assessment_001/assessment.json'
    if original['status']=='COMPLETED' or not partial.exists():return original
    assessment=load(partial);view=dict(original)
    view.update({k:assessment[k] for k in ['maxima','state_status','net_current_status','scientific_status']})
    view['class_status']=dict(assessment['class_status'],F='NUMERICALLY_UNRESOLVED',H='NUMERICALLY_UNRESOLVED')
    view['full_workflow_scientific_status']=original['scientific_status']
    view['completed_tiers_extracted']=True;view['all_mandatory_gates_pass']=False
    view['resolved_fail_count']=assessment['resolved_fail_count']
    # Unresolved F/H counts are obligations, not measured error estimates.
    view['unresolved_count']=assessment['unresolved_count']+2*load(OUT/'formal_numerical_contract.json')['selected_net_channel_count']+8
    view['failure_classes']=[k for k,v in view['class_status'].items() if v=='RESOLVED_FAIL']
    view['unresolved_classes']=[k for k,v in view['class_status'].items() if v=='NUMERICALLY_UNRESOLVED']
    view['physical_ck_root_domain']=None
    return view

def table_for(name,file):
    base=OUT/'per_condition'/name/'run_001'
    if (base/file).exists():return rows(base/file)
    partial=base/'state_current_assessment_001'
    if (partial/file).exists():return rows(partial/file)
    if file=='protein_output.csv' and (partial/'state_errors.csv').exists():
        return [r for r in rows(partial/'state_errors.csv') if r['observable']=='Pept0003']
    if file=='net_extent_errors.csv':
        return [dict(observable=r['channel_id'],category='NET_EXTENT',window=window,
                     mandatory=(r['mandatory_net_current_and_extent']=='True' and window in ['FULL_WINDOW','POST_INITIAL_LAYER']),
                     reference_scale='',floor=1e-6,E_inf='',max_absolute_error='',uncertainty='',gate=.01,
                     status='NUMERICALLY_UNRESOLVED_EXTENT_NONCOMPLETION',lower_error='',upper_error='',contract_class='F')
                for window in ['FULL_WINDOW','POST_INITIAL_LAYER','POST_0P05_DIAGNOSTIC','COMPOSITE_OR_HYBRID']
                for r in rows(OUT/'formal_net_channel_membership.csv')]
    if file=='initial_layer.csv':
        return [dict(observable='FULL_H_CLASS_NOT_RESOLVED_WITH_EXTENT_NONCOMPLETION',contract_class='H',
                     mandatory=True,value='',uncertainty='',gate='',status='NUMERICALLY_UNRESOLVED')]
    if file=='balance_accounting.csv':
        law=rows(partial/'conservation.csv')
        exact=dict(accounting='EXACT_SOURCE_GENERAL_LAW_DRIFT',source_max_abs=max(float(r['max_absolute_drift']) for r in law if r['model']=='SOURCE'),
                   reduced_max_abs=max(float(r['max_absolute_drift']) for r in law if r['model']=='CK_HYBRID'),mandatory=True,interpretation='C_GATE; completed state tiers; extent noncompletion preserved')
        return [exact]+[dict(accounting=n,source_max_abs='',reduced_max_abs='',mandatory=False,
                      interpretation='N/A; extent workflow did not complete; NOT_REQUIRED_FOR_PROMOTION;BUT_NOT_VALIDATED')
                   for n in ['NET_STOICHIOMETRIC_FULL_STATE_LEDGER','NET_STOICHIOMETRIC_SLOW_COORDINATE_LEDGER',
                             'ALGEBRAIC_ACCOUNTING_AFTER_DISCLOSED_SWITCH_JUMP','GROSS_MICROSCOPIC_DIRECTED_LEDGER']]
    if file=='gross_descriptive.csv':
        with np.load(partial/'instantaneous_comparison.npz') as arrays:
            r=FormalCK(name);source=arrays['source_rates'];reduced=arrays['reduced_rates']
            return [dict(observable=r.source.reactions[j]['id'],contract_classes='E;G',mandatory=False,
                        full_window_rate_E_inf=float(np.max(abs(source[:,j]-reduced[:,j]))/max(np.max(abs(source[:,j])),1e-9)),
                        full_window_gross_extent_E_inf='',status='SOURCE_PROVENANCE_PRESERVED;DESCRIPTIVE;BUT_NOT_VALIDATED;GROSS_EXTENT_NA_NUMERICAL_NONCOMPLETION') for j in r.fast]
    return []

def finalize():
    c=checked_contract();summaries=[];results=[]
    assert {p.name for p in (OUT/'per_condition').iterdir() if p.is_dir()}==set(CONDITIONS)
    for name in CONDITIONS:
        assert load(OUT/'per_condition'/name/'run_001/result.json')['status'] in ['COMPLETED','NUMERICAL_NONCOMPLETION'], 'Cannot close an active experiment: '+name
    for name in CONDITIONS:
        path=OUT/'per_condition'/name/'run_001/result.json';r=evidence_view(load(path));results.append(r)
        m=r.get('maxima',{});states=r.get('class_status',{})
        summaries.append(dict(condition_id=name,status=r['status'],scientific_status=r['scientific_status'],
          all_mandatory_gates_pass=r.get('all_mandatory_gates_pass',False),
          state_status=r.get('state_status','NOT_COMPLETED'),net_current_status=r.get('net_current_status','NOT_COMPLETED'),
          A=states.get('A','NOT_COMPLETED'),B=states.get('B','NOT_COMPLETED'),C=states.get('C','NOT_COMPLETED'),
          D=states.get('D','NOT_COMPLETED'),F=states.get('F','NOT_COMPLETED'),H=states.get('H','NOT_COMPLETED'),
          state_error=m.get('state'),slow_total_error=m.get('slow_total'),protein_output_error=m.get('protein'),
          ck_net_current_error=m.get('ck_net_current'),ck_net_current_post_0p05=m.get('ck_net_current_post_0p05'),
          ck_net_extent_error=m.get('ck_net_extent'),all_mandatory_net_extent_error=m.get('net_extent'),
          conservation_drift=m.get('conservation'),switch_jump_scaled=m.get('switch_jump_scaled'),
          resolved_failures=r.get('resolved_fail_count'),unresolved=r.get('unresolved_count'),
          failure_classes=';'.join(r.get('failure_classes',[])),unresolved_classes=';'.join(r.get('unresolved_classes',[])),
          gross_status='SOURCE_PROVENANCE_PRESERVED;DESCRIPTIVE;BUT_NOT_VALIDATED'))
    write_csv(OUT/'condition_summary.csv',summaries)
    for file in ['state_errors.csv','slow_total_errors.csv','net_current_errors.csv','net_extent_errors.csv',
                 'conservation.csv','protein_output.csv','initial_layer.csv','balance_accounting.csv','gross_descriptive.csv']:
        data=[]
        for name in CONDITIONS:
            data.extend(dict(condition_id=name,**row) for row in table_for(name,file))
        if data:write_csv(OUT/file,data)
    issues=[]
    for name in CONDITIONS:
        for file in ['state_errors.csv','slow_total_errors.csv','net_current_errors.csv','net_extent_errors.csv','conservation.csv','initial_layer.csv']:
            for row in table_for(name,file):
                if str(row['mandatory'])=='True' and row['status']!='RESOLVED_PASS':
                    issues.append(dict(condition=name,contract_class=row['contract_class'],observable=row['observable'],
                       window=row.get('window','BOUNDARY_OR_EXACT_LAW'),error=row.get('E_inf',row.get('max_absolute_drift',row.get('value',''))),
                       uncertainty=row['uncertainty'],gate=row['gate'],status=row['status'],source_table=file))
    if issues:write_csv(OUT/'failed_or_unresolved_observables.csv',issues)
    domain=[]
    for result in results:
        if result['status']!='COMPLETED':continue
        name=result['condition'];base=OUT/'per_condition'/name/'run_001';runtime=FormalCK(name)
        with np.load(base/'comparison.npz') as a:
            reported=a['reduced'][:,runtime.ix];times=a['times'].copy();z0=a['T']@a['x0']
        with np.load(base/'reduced_primary_dense.npz') as dense:
            totals=dense['accepted'][:,:3]+z0[:3];steps=dense['steps'].copy()
        i,j=np.unravel_index(np.argmin(totals),totals.shape)
        k,l=np.unravel_index(np.argmin(reported),reported.shape)
        domain.append(dict(condition_id=name,minimum_accepted_fast_total=float(totals[i,j]),
           coordinate=runtime.labels[j],accepted_time_s=float(steps[i]),minimum_reported_ck_state=float(reported[k,l]),
           ck_species=runtime.source.species[runtime.ix[l]],reported_time_s=float(times[k]),
           strict_ck_domain_pass=result['physical_ck_root_domain'],
           interpretation='DIAGNOSTIC; frozen strict zero-boundary predicate retained; no clipping or reclassification'))
    write_csv(OUT/'physical_domain_diagnostics.csv',domain)
    completed=[r for r in results if r['status']=='COMPLETED']
    count=sum(r.get('all_mandatory_gates_pass',False) for r in results)
    statevalid=len(results)==9 and all(r.get('state_status')=='STATE_VALID' for r in results)
    resolved_current_fail=any(r.get('class_status',{}).get('D')=='RESOLVED_FAIL' for r in results)
    if count==9:recommendation='CK_READY_FOR_HUMAN_PROMOTION_REVIEW';outcome='CK_FORMAL_VALIDATION_PASS'
    elif statevalid and resolved_current_fail:recommendation='CK_STATE_REDUCTION_SUPPORTED_BUT_FLUX_NOT_READY';outcome='CK_STATE_VALID_NET_CURRENT_FAIL'
    elif len(completed)<9 or any(r.get('unresolved_count',0)>0 for r in completed):recommendation='CK_VALIDATION_NUMERICALLY_UNRESOLVED';outcome='CK_NUMERICALLY_UNRESOLVED'
    else:recommendation='CK_NOT_READY';outcome='CK_CONDITION_DEPENDENT'
    worst={}
    for key in ['state','slow_total','retained_coordinate','protein','ck_net_current','net_current','ck_net_extent','net_extent','conservation','switch_jump_scaled','ck_net_current_post_0p05']:
        measured=[r for r in results if r.get('maxima',{}).get(key) is not None]
        if measured:
            row=max(measured,key=lambda r:r['maxima'][key]);worst[key]=dict(value=row['maxima'][key],condition=row['condition'],measured_conditions=len(measured))
        else:worst[key]=None
    overall=dict(schema='R6_CK_FORMAL_CAMPAIGN_SUMMARY_V1',decision='GROSS_FLUX_NOT_REQUIRED_FOR_CK_PROMOTION',
       mandatory_classes=c['mandatory_classes'],gross_classes=['E','G'],gross_status='SOURCE_PROVENANCE_PRESERVED;DESCRIPTIVE;BUT_NOT_VALIDATED',
       registered_conditions=9,completed_conditions=len(completed),conditions_passing_all_mandatory_gates=count,
       candidate_outcome=outcome,recommendation=recommendation,worst=worst,
       state_valid_all_conditions=statevalid,resolved_net_current_failure=resolved_current_fail,
       conservation_all_resolved_pass=len(results)==9 and all(r.get('class_status',{}).get('C')=='RESOLVED_PASS' for r in results),
       initial_layer_all_resolved_pass=len(completed)==9 and all(r['class_status']['H']=='RESOLVED_PASS' for r in completed),
       unresolved_conditions=[r['condition'] for r in results if r['status']!='COMPLETED' or r.get('unresolved_count',0)>0],
       failure_classes=sorted({k for r in results for k in r.get('failure_classes',[])}),
       state_current_assessments=sum('class_status' in r for r in results),
       numerical_noncompletion_conditions=[r['condition'] for r in results if r['status']!='COMPLETED'],
       no_promotion=True,no_push=True,no_merge=True,no_next_stage=True,closed_at_utc=stamp())
    balance_summary=[]
    for accounting in ['EXACT_SOURCE_GENERAL_LAW_DRIFT','NET_STOICHIOMETRIC_FULL_STATE_LEDGER',
                       'NET_STOICHIOMETRIC_SLOW_COORDINATE_LEDGER','ALGEBRAIC_ACCOUNTING_AFTER_DISCLOSED_SWITCH_JUMP',
                       'GROSS_MICROSCOPIC_DIRECTED_LEDGER']:
        for model in ['source','reduced']:
            measured=[dict(condition=name,**row) for name in CONDITIONS for row in table_for(name,'balance_accounting.csv') if row['accounting']==accounting and row[model+'_max_abs']!='']
            maximum=max(measured,key=lambda row:float(row[model+'_max_abs'])) if measured else None
            balance_summary.append(dict(accounting=accounting,model=model,max_absolute_residual=float(maximum[model+'_max_abs']) if maximum else None,
              condition=maximum['condition'] if maximum else None,measured_conditions=len(measured),
              status='MANDATORY_C_GATE_REPORTED_SEPARATELY' if accounting=='EXACT_SOURCE_GENERAL_LAW_DRIFT' else 'DESCRIPTIVE;NOT_REQUIRED_FOR_PROMOTION;BUT_NOT_VALIDATED'))
    overall['balance_summary']=balance_summary
    overall['class_condition_counts']={cls:{status:sum(r.get('class_status',{}).get(cls)==status for r in results)
       for status in ['RESOLVED_PASS','RESOLVED_FAIL','NUMERICALLY_UNRESOLVED']} for cls in c['mandatory_classes']}
    ck_channels=[row['channel_id'] for row in rows(OUT/'formal_net_channel_membership.csv') if row['selected_ck_fast']=='True']
    bywindow=[]
    for metric,file in [('CK_NET_CURRENT','net_current_errors.csv'),('CK_NET_EXTENT','net_extent_errors.csv')]:
        for window in ['FULL_WINDOW','POST_INITIAL_LAYER','POST_0P05_DIAGNOSTIC','COMPOSITE_OR_HYBRID']:
            measured=[dict(condition=name,**row) for name in CONDITIONS for row in table_for(name,file)
                      if row['observable'] in ck_channels and row['window']==window and row['E_inf']!='']
            maximum=max(measured,key=lambda row:float(row['E_inf'])) if measured else None
            bywindow.append(dict(metric=metric,window=window,E_inf=float(maximum['E_inf']) if maximum else None,
              condition=maximum['condition'] if maximum else None,observable=maximum['observable'] if maximum else None,
              measured_conditions=len({row['condition'] for row in measured}),mandatory=window in ['FULL_WINDOW','POST_INITIAL_LAYER']))
    overall['ck_window_maxima']=bywindow
    write_json(OUT/'formal_campaign_summary.json',overall)
    write_json(OUT/'source_reuse_status.json',dict(status='PASS_HASH_VERIFIED_REUSE',
       selected_trajectories=[r['primary_directory'] for r in load(OUT/'source_reuse_verification.json')['conditions']],
       verification_sha256=sha(OUT/'source_reuse_verification.json'),historical_reduced_reused=False,
       fresh_startup_solves=True,excluded_conditions=['R3_ADVERSE']))
    write_json(OUT/'formal_input_provenance.json',dict(schema='R6_FORMAL_INPUT_PROVENANCE_V1',
       original_phase0_provenance_sha256=sha(OUT/'input_provenance.json'),
       original_scope_registration_sha256=sha(OUT/'registration_binding.json'),
       formal_registration_sha256=sha(OUT/'formal_registration_binding.json'),
       human_branch_a_decision_sha256=sha(OUT/'human_branch_a_decision_20261007.txt'),
       source_reuse_verification_sha256=sha(OUT/'source_reuse_verification.json'),
       environment_sha256=sha(OUT/'formal_environment.json'),historical_source_arrays_reused=True,
       new_decisive_comparisons_run=True,condition_count=9,completed_conditions=len(completed),
       note='The original phase-0 new_decisive_comparisons_run=false field is an immutable pre-run snapshot; this record describes the formal continuation.',
       result_hashes={r['condition']:sha(OUT/'per_condition'/r['condition']/'run_001/result.json') for r in results},promotion=False))
    write_json(OUT/'closeout.json',dict(schema='R6_FORMAL_BRANCH_A_CLOSEOUT_V1',decision=overall['decision'],
       recommendation=recommendation,candidate_outcome=outcome,completed_conditions=len(completed),
       conditions_passing_all_mandatory_gates=count,closed_at_utc=stamp(),promotion=False,no_next_stage=True))
    original_audit=OUT/'audit_stop_001/docs/reduction/r6_ck_scientific_requirement_audit.md'
    note='# Current R6 status after the human Branch A decision\n\n'
    note+='The researcher resolved the audited ambiguity in favor of descriptive gross binding rates/extents, with provenance preserved. '
    note+='Classes A, B, C, D, F and H are mandatory; E/G are BUT_NOT_VALIDATED and excluded from promotion gates. '
    note+='See `r6_ck_formal_observable_contract_v1.md` and `r6_ck_formal_validation_summary.md` for the frozen contract and executed campaign. '
    note+='The original audit below is historical and preserved byte-for-byte in `audit_stop_001`; its former stop condition has been superseded by the explicit human decision.\n\n---\n\n'
    (DOC/'r6_ck_scientific_requirement_audit.md').write_text(note+original_audit.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    lines=['# R6 CK formal Branch A validation summary','',f"**{outcome}**. Recommendation: **{recommendation}**.",'',
       f"Completed {len(completed)}/9 full numerical workflows; {overall['state_current_assessments']}/9 have completed state/current assessments; {count}/9 passed every mandatory gate. The researcher's Branch A decision makes A, B, C, D, F and H mandatory. E/G remain SOURCE_PROVENANCE_PRESERVED / descriptive / BUT_NOT_VALIDATED. No CK or reduced-core promotion occurred.",'',
       '| Condition | A/B states | C conservation | D net current | F net extent | H initial layer | Overall |',
       '|---|---|---|---|---|---|---|']
    for r in summaries:lines.append(f"| {r['condition_id']} | {r['state_status']} | {r['C']} | {r['D']} | {r['F']} | {r['H']} | {r['scientific_status']} |")
    lines+=['','## Measured worst errors','', '| Observable | Maximum | Condition |','|---|---:|---|']
    for key,v in worst.items():lines.append(f"| {key} | {v['value']:.12g} | {v['condition']} |" if v else f'| {key} | N/A | N/A |')
    lines+=['','## Distinct balance reports','', '| Accounting | Model | Maximum absolute residual | Measured conditions |','|---|---|---:|---:|']
    for row in balance_summary:
        value=f"{row['max_absolute_residual']:.12g}" if row['max_absolute_residual'] is not None else 'N/A'
        lines.append(f"| {row['accounting']} | {row['model']} | {value} | {row['measured_conditions']} |")
    lines+=['','## CK current and extent windows','', '| Metric | Window | Maximum E_inf | Condition |','|---|---|---:|---|']
    for row in bywindow:
        value=f"{row['E_inf']:.12g}" if row['E_inf'] is not None else 'N/A'
        lines.append(f"| {row['metric']} | {row['window']} | {value} | {row['condition'] or 'N/A'} |")
    lines+=['','Every mandatory non-pass row, including numerical uncertainty, is collected in `failed_or_unresolved_observables.csv` with its source table, condition, window, error, uncertainty and unchanged gate.']
    lines+=['','## H uncertainty and strict-domain results','',
       'H condition counts are '+json.dumps(overall['class_condition_counts']['H'])+'. Resolved failure takes precedence at class level while each unresolved row remains visible. The strict CK predicate fails wherever an accepted fast total or reported CK state is negative, including finite-precision-scale values. `physical_domain_diagnostics.csv` records the minimum, coordinate/species and time for each condition; no tolerance was added and no value was clipped.',
       '', '| Condition | Minimum accepted fast total | Coordinate | Strict CK-domain pass |','|---|---:|---|---|']
    for row in domain:lines.append(f"| {row['condition_id']} | {row['minimum_accepted_fast_total']:.12g} | {row['coordinate']} | {row['strict_ck_domain_pass']} |")
    lines+=['','Eight slow-coordinate continuity checks have tiny measured jumps but uncertainty above the frozen 1e-9 allowance (10% of the 1e-8 gate). They remain NUMERICALLY_UNRESOLVED; this is separate from C exact-law drift. ATP-low passes H.']
    lines+=['','Worst mandatory curve errors include separate FULL_WINDOW and POST_INITIAL_LAYER gates. CK net-current post-0.05 s is a separate descriptive window; it never replaces the boundary-inclusive post-layer gate. Every numerical status uses the registered uncertainty envelope and its 10% budget. Detailed per-observable rows retain scale, floor, uncertainty, lower/upper error and resolved status.',
      '',f"Exact conservation laws numerically resolved on all conditions: {overall['conservation_all_resolved_pass']}. H startup/continuity/domain gates resolved on all conditions: {overall['initial_layer_all_resolved_pass']}. Failure classes: {', '.join(overall['failure_classes']) or 'none'}. Numerically unresolved conditions: {', '.join(overall['unresolved_conditions']) or 'none'}.",'',
      '## Interpretation and accounting boundaries','',
      'Full-source trajectories and source uncertainty probes were reused only after the explicit source verifier passed. Every reduced primary/tighter trajectory and each full-source startup solve is fresh. The frozen R5 rule 10*eta*tau0 was used without tuning. The startup and switch jump remain visible; actual startup net/gross integrals were retained. No source projection, fitted effective parameter, initial-condition fit, clipping or time shift was used.',
      '', 'The state and current conclusions are separate. A resolved D failure prevents the registered formal conjunction even when state trajectories are valid. An unresolved class does not erase a resolved failure, and a resolved failure is not evidence that every observable is numerically characterized. If an extent integration reaches its registered computational bound, the original noncompletion result and native dense state evidence are retained; completed A/B/C/D tiers are extracted separately without another state solve. F/H remain unresolved and missing extent errors are N/A, never zero or inferred PASS. Worst metrics identify how many conditions were actually measured.',
      '', 'Exact SOURCE_GENERAL law drift, net stoichiometric accounting, algebraic-state accounting and the gross directed ledger are reported separately in balance_accounting.csv. A disclosed switch reconstruction jump can appear in the full-state net ledger; it is not invented reaction turnover. Gross directed rates/extents and gross-ledger residuals are descriptive and BUT_NOT_VALIDATED, so they do not enter this Branch A promotion conjunction.',
      '', 'Tiny negative values in unused reconstructed species remain visible in each condition record. Physical CK totals/root checks are separate from global mathematical positivity; unresolved absolute chemical units, Mg/protonation and broad physical-domain proof are not resolved by this numerical campaign. Released source product is fMGG Pept0003, not mature GFP.',
      '', 'The original R6 ambiguity stop is preserved under audit_stop_001. This new prospective contract changes no historical R3/R4 gates, R5 descriptive status or R5-C corrections. The independent verifier checks final hashes and recomputes observable scores from the primary/probe arrays; verification is not scientific promotion.',
      '', 'Stop at this bounded closeout. No first-order follow-on, adverse solve, aminoacylation reduction, push, merge or automatic promotion.']
    (DOC/'r6_ck_formal_validation_summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    write_json(OUT/'evidence_navigation_formal.json',dict(schema='R6_DERIVED_FORMAL_EVIDENCE_NAVIGATION_V1',source_authority=False,
       nodes=[dict(id='HUMAN_BRANCH_A',path='human_branch_a_decision_20261007.txt',status='EXTRACTED'),
              dict(id='CONTRACT',path='formal_numerical_contract.json',status='EXTRACTED')]+[
              dict(id=r['condition'],path=f"per_condition/{r['condition']}/run_001/result.json",status='EXTRACTED',outcome=r['scientific_status']) for r in results],
       edges=[dict(source='HUMAN_BRANCH_A',target='CONTRACT',relationship='AUTHORIZES')]+[
              dict(source='CONTRACT',target=r['condition'],relationship='PROSPECTIVE_GATES',status='EXTRACTED') for r in results],
       freshness='Every path is SHA-256-bound by the final manifest; derived navigation does not replace evidence'))
    files=[p for p in OUT.rglob('*') if p.is_file() and p not in [OUT/'manifest.json',OUT/'verification.json',OUT/'verification_binding.json']]
    files+=list(DOC.glob('r6_*.md'))+list((ROOT/'scripts').glob('*r6*.py'))
    write_json(OUT/'manifest.json',dict(schema='R6_CK_FORMAL_FINAL_MANIFEST_V1',decision=overall['decision'],
       file_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)},
       excluded_root_self_reference=['manifest.json','verification.json','verification_binding.json'],
       prior_scope_manifest_preserved='audit_stop_001/results/reduction/r6_ck_validation/manifest.json',
       promotion=False))
    print(json.dumps(overall,indent=2),flush=True)
    return overall

if __name__=='__main__':finalize()
