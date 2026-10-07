"""Observable-specific Branch-A scoring; gross channels never enter gates."""
from r6_ck_common_v1 import *

def score_condition(name,dest=None,write=True):
    c=checked_contract();dest=dest or OUT/'per_condition'/name/'run_001';r=FormalCK(name)
    with np.load(dest/'comparison.npz') as source:a={k:source[k].copy() for k in source.files}
    t=a['times'];switch=float(a['switch']);state=a['source'];red=a['reduced'];sp=a['source_probe'];rp=a['reduced_probe']
    state_rows=metric_rows(r.source.species,state,red,sp,rp,t,switch,1e-6,.01,'STATE')
    for row in state_rows:row['contract_class']='B' if row['observable'] in c['algebraically_affected_states'] else 'A'
    slow_rows=metric_rows(r.labels,state@r.T.T,a['reduced_slow'],sp@r.T.T,a['probe_slow'],t,switch,1e-6,.01,'SLOW_TOTAL_OR_COORDINATE')
    for row in slow_rows:row['contract_class']='A'
    # Error in a difference uses summed source/reduced probe envelopes.
    current_extra=np.zeros_like(a['source_net']);extent_extra=abs(a['same_trajectory_tight_extent']-a['reduced_extent'])
    for k,(f,b) in enumerate(r.channels):
        if b is not None:
            current_extra[:,k]=8*np.finfo(float).eps*(abs(a['source_rates'][:,f])+abs(a['source_rates'][:,b]))
            extent_extra[:,k]+=8*np.finfo(float).eps*(abs(a['source_gross_extent'][:,f])+abs(a['source_gross_extent'][:,b]))
    current_rows=metric_rows(r.channel_ids,a['source_net'],a['reduced_net'],a['source_net_probe'],a['reduced_net_probe'],
                            t,switch,1e-9,.05,'NET_CURRENT',r.mandatory_channels,current_extra)
    extent_rows=metric_rows(r.channel_ids,a['source_extent'],a['reduced_extent'],a['source_extent_probe'],a['reduced_extent_probe'],
                            t,switch,1e-6,.01,'NET_EXTENT',r.mandatory_channels,extent_extra)
    for row in current_rows:row['contract_class']='D'
    for row in extent_rows:row['contract_class']='F'
    conservation=[]
    for i,lawid in enumerate(r.source.cert['law_ids']):
        for model,key,probe in [('SOURCE','source_law_drift','source_law_probe'),('CK_HYBRID','reduced_law_drift','reduced_law_probe')]:
            drift=float(np.max(abs(a[key][:,i])));u=float(np.max(abs(a[key][:,i]-a[probe][:,i])))
            conservation.append(dict(observable=lawid,model=model,contract_class='C',mandatory=True,
                        max_absolute_drift=drift,uncertainty=u,gate=1e-8,status=gate_status(drift,u,1e-8)))
    fullswitch=a['full_switch_state'];reds=a['reduced_switch_state'];fullp=a['full_switch_probe'];redp=a['reduced_switch_probe']
    scales=np.maximum(np.max(abs(state),axis=0),1e-6)
    jump=float(np.max(abs(reds-fullswitch)/scales))
    jumpu=float(np.max((abs(reds-redp)+abs(fullswitch-fullp))/scales))
    total_jump=r.T@(reds-fullswitch);total_u=np.max(abs(r.T@(reds-redp)))+np.max(abs(r.T@(fullswitch-fullp)))
    rounding=8*np.finfo(float).eps*np.max(abs(r.T)@(abs(reds)+abs(fullswitch)))
    assert np.array_equal(t[t>=1e-4],TIMES[1:])
    zero=np.flatnonzero(t==0)[0];boundary=np.flatnonzero(t==switch)[0]
    identity_start=np.array_equal(red[zero],r.x0) and np.array_equal(state[zero],r.x0)
    retained_startup=np.array_equal(red[t<switch],state[t<switch])
    extents_retained=np.array_equal(a['source_extent'][boundary],a['reduced_extent'][boundary])
    invariants=[('HYBRID_INITIAL_EQUALS_CANONICAL_INITIAL',identity_start),
                ('FULL_SOURCE_STARTUP_RETAINED',retained_startup),
                ('STARTUP_NET_EXTENTS_RETAINED',extents_retained),
                ('SWITCH_RULE_UNTUNED',abs(switch-r.switch)<=np.finfo(float).eps*switch),
                ('NET_EXTENT_ZERO_ORIGIN',np.array_equal(a['reduced_extent'][zero],np.zeros(678)))]
    initial_layer=[dict(observable=n,contract_class='H',mandatory=True,value=0. if ok else 1.,
                        uncertainty=0.,gate=0.,status='RESOLVED_PASS' if ok else 'RESOLVED_FAIL') for n,ok in invariants]
    initial_layer+= [dict(observable='SCALED_SWITCH_STATE_JUMP',contract_class='H',mandatory=True,value=jump,
                         uncertainty=jumpu,gate=.01,status=gate_status(jump,jumpu,.01)),
                    dict(observable='EXACT_SLOW_COORDINATE_SWITCH_CONTINUITY',contract_class='H',mandatory=True,
                         value=float(np.max(abs(total_jump))),uncertainty=float(total_u+rounding),gate=1e-8,
                         status=gate_status(float(np.max(abs(total_jump))),float(total_u+rounding),1e-8))]
    # Strict physical CK root domain on reported and accepted slow states.
    with np.load(dest/'reduced_primary_dense.npz') as stored:accepted=stored['accepted'].copy()
    physical_totals=accepted[:,:3]+r.z0[:3]
    root_domain=bool(np.min(physical_totals)>=0 and np.min(red[:,r.ix])>=0)
    initial_layer.append(dict(observable='PHYSICAL_CK_TOTAL_AND_ROOT_DOMAIN',contract_class='H',mandatory=True,
                value=0. if root_domain else 1.,uncertainty=0.,gate=0.,status='RESOLVED_PASS' if root_domain else 'RESOLVED_FAIL'))
    _,qinitial=material_root(*r.z0[:3])
    write_json(dest/'initial_layer_details.json',dict(switch_s=switch,tau0_s=r.tau0,
              outer_initial_occupancy_mismatch=(qinitial-r.x0[r.qix]).tolist(),
              switch_state_jump=(reds-fullswitch).tolist(),switch_state_jump_scaled=jump,
              totals_switch_jump=total_jump.tolist(),startup_preserved=retained_startup,
              startup_net_extents=a['source_extent'][boundary,r.fast_channels].tolist(),
              startup_gross_fast_extents=a['source_gross_extent'][boundary,r.fast].tolist(),
              strict_all_species_nonnegative=bool(np.min(red)>=0),minimum_reconstructed_state=float(np.min(red)),
              physical_ck_root_domain=root_domain,minimum_accepted_fast_total=float(np.min(physical_totals)),
              unused_tiny_negative_states_retained_no_clipping=True,
              switch_jump_is_not_hidden_reaction_turnover=True)) if write else None
    # Four accounting meanings, with an explicit reconstruction jump rather than fictitious turnover.
    net_source=np.array([xx-r.x0-r.N@xi for xx,xi in zip(state,a['source_extent'])])
    net_red=np.array([xx-r.x0-r.N@xi for xx,xi in zip(red,a['reduced_extent'])])
    TN=r.T@r.N
    slow_res=np.array([z-r.z0-TN@xi for z,xi in zip(a['reduced_slow'],a['reduced_extent'])])
    corrected=net_red.copy();corrected[t>=switch]-=(reds-fullswitch)
    gross_source=np.array([xx-r.x0-r.S@xi for xx,xi in zip(state,a['source_gross_extent'])])
    gross_red=np.array([xx-r.x0-r.S@xi for xx,xi in zip(red,a['reduced_gross_extent'])])
    balance=[dict(accounting='EXACT_SOURCE_GENERAL_LAW_DRIFT',source_max_abs=float(np.max(abs(a['source_law_drift']))),
                  reduced_max_abs=float(np.max(abs(a['reduced_law_drift']))),mandatory=True,
                  interpretation='C_GATE; independent of directed ledger closure'),
             dict(accounting='NET_STOICHIOMETRIC_FULL_STATE_LEDGER',source_max_abs=float(np.max(abs(net_source))),
                  reduced_max_abs=float(np.max(abs(net_red))),mandatory=False,
                  interpretation='DESCRIPTIVE; includes disclosed switch reconstruction jump'),
             dict(accounting='NET_STOICHIOMETRIC_SLOW_COORDINATE_LEDGER',source_max_abs=float(np.max(abs(net_source@r.T.T))),
                  reduced_max_abs=float(np.max(abs(slow_res))),mandatory=False,
                  interpretation='DESCRIPTIVE; state and extent error gates remain mandatory'),
             dict(accounting='ALGEBRAIC_ACCOUNTING_AFTER_DISCLOSED_SWITCH_JUMP',source_max_abs=float(np.max(abs(net_source))),
                  reduced_max_abs=float(np.max(abs(corrected))),mandatory=False,
                  interpretation='DESCRIPTIVE; no artificial extent assigned to switch jump'),
             dict(accounting='GROSS_MICROSCOPIC_DIRECTED_LEDGER',source_max_abs=float(np.max(abs(gross_source))),
                  reduced_max_abs=float(np.max(abs(gross_red))),mandatory=False,
                  interpretation='SOURCE_PROVENANCE_PRESERVED;NOT_REQUIRED_FOR_PROMOTION;BUT_NOT_VALIDATED')]
    gross=[]
    for j in r.fast:
        n=r.source.reactions[j]['id'];rs=max(float(np.max(abs(a['source_rates'][:,j]))),1e-9)
        es=max(float(np.max(abs(a['source_gross_extent'][:,j]))),1e-6)
        gross.append(dict(observable=n,contract_classes='E;G',mandatory=False,
                          full_window_rate_E_inf=float(np.max(abs(a['source_rates'][:,j]-a['reduced_rates'][:,j]))/rs),
                          full_window_gross_extent_E_inf=float(np.max(abs(a['source_gross_extent'][:,j]-a['reduced_gross_extent'][:,j]))/es),
                          status='SOURCE_PROVENANCE_PRESERVED;DESCRIPTIVE;BUT_NOT_VALIDATED'))
    protein=[row.copy() for row in state_rows if row['observable']=='Pept0003']
    allgates=state_rows+slow_rows+current_rows+extent_rows+conservation+initial_layer
    active=[row for row in allgates if row['mandatory']]
    def cls_status(cls):
        statuses=[row['status'] for row in active if row['contract_class']==cls]
        if 'RESOLVED_FAIL' in statuses:return 'RESOLVED_FAIL'
        if 'NUMERICALLY_UNRESOLVED' in statuses:return 'NUMERICALLY_UNRESOLVED'
        return 'RESOLVED_PASS'
    class_status={cls:cls_status(cls) for cls in c['mandatory_classes']}
    allpassed=all(row['status']=='RESOLVED_PASS' for row in active)
    state_valid=all(class_status[k]=='RESOLVED_PASS' for k in ['A','B'])
    if allpassed:outcome='CK_FORMAL_VALIDATION_PASS'
    elif class_status['C']=='RESOLVED_FAIL':outcome='CK_CONSERVATION_FAIL'
    elif state_valid and class_status['D']=='RESOLVED_FAIL':outcome='CK_STATE_VALID_NET_CURRENT_FAIL'
    elif state_valid and class_status['F']=='RESOLVED_FAIL':outcome='CK_STATE_VALID_NET_EXTENT_FAIL'
    elif any(v=='NUMERICALLY_UNRESOLVED' for v in class_status.values()):outcome='CK_NUMERICALLY_UNRESOLVED'
    else:outcome='CK_CONDITION_DEPENDENT'
    maxima=dict(state=max(row['E_inf'] for row in state_rows if row['mandatory']),
                slow_total=max(row['E_inf'] for row in slow_rows if row['mandatory'] and row['observable'] in ['T0','T1','B']),
                retained_coordinate=max(row['E_inf'] for row in slow_rows if row['mandatory']),
                protein=max(row['E_inf'] for row in protein if row['mandatory']),
                ck_net_current=max(row['E_inf'] for row in current_rows if row['mandatory'] and row['observable'] in [r.channel_ids[i] for i in r.fast_channels]),
                net_current=max(row['E_inf'] for row in current_rows if row['mandatory']),
                ck_net_extent=max(row['E_inf'] for row in extent_rows if row['mandatory'] and row['observable'] in [r.channel_ids[i] for i in r.fast_channels]),
                net_extent=max(row['E_inf'] for row in extent_rows if row['mandatory']),
                conservation=max(row['max_absolute_drift'] for row in conservation),switch_jump_scaled=jump,
                ck_net_current_post_0p05=max(row['E_inf'] for row in current_rows if row['window']=='POST_0P05_DIAGNOSTIC' and row['observable'] in [r.channel_ids[i] for i in r.fast_channels]))
    if write:
        for file,table in [('state_errors.csv',state_rows),('slow_total_errors.csv',slow_rows),('net_current_errors.csv',current_rows),
                           ('net_extent_errors.csv',extent_rows),('conservation.csv',conservation),('protein_output.csv',protein),
                           ('initial_layer.csv',initial_layer),('balance_accounting.csv',balance),('gross_descriptive.csv',gross)]:
            write_csv(dest/file,table)
    return dict(scientific_status=outcome,all_mandatory_gates_pass=allpassed,state_status='STATE_VALID' if state_valid else 'STATE_NOT_VALIDATED',
                net_current_status='NET_CURRENT_VALIDATED' if class_status['D']=='RESOLVED_PASS' else 'NET_CURRENT_NOT_VALIDATED',
                class_status=class_status,maxima=maxima,mandatory_gate_count=len(active),
                resolved_fail_count=sum(row['status']=='RESOLVED_FAIL' for row in active),
                unresolved_count=sum(row['status']=='NUMERICALLY_UNRESOLVED' for row in active),
                failure_classes=[k for k,v in class_status.items() if v=='RESOLVED_FAIL'],
                unresolved_classes=[k for k,v in class_status.items() if v=='NUMERICALLY_UNRESOLVED'],
                physical_ck_root_domain=root_domain,scientific_promotion='NOT_APPROVED',
                gross_status='SOURCE_PROVENANCE_PRESERVED;DESCRIPTIVE;BUT_NOT_VALIDATED')

if __name__=='__main__':
    for name in CONDITIONS:
        print(name,score_condition(name),flush=True)
