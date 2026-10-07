"""Freeze Branch-A numerical contract and membership before decisive solves."""
from r6_ck_common_v1 import *
import platform, sys, scipy, sympy

def register():
    assert not (OUT/'formal_registration_binding.json').exists(), 'Formal registration is immutable'
    assert not (OUT/'per_condition').exists(), 'Cannot register after a decisive run'
    reuse=load(OUT/'source_reuse_verification.json');assert reuse['status']=='PASS'
    snapshot=load(OUT/'historical_snapshot.json')
    for path,meta in snapshot.items():assert sha(ROOT/path)==meta['sha256'],path
    r=FormalCK('R3_BASE')
    membership=[]
    for k,(j,back) in enumerate(r.channels):
        membership.append(dict(channel_id=r.channel_ids[k],forward=r.source.reactions[j]['id'],
             reverse=r.source.reactions[back]['id'] if back is not None else '',
             mandatory_net_current_and_extent=k in r.mandatory_channels,
             selected_ck_fast=k in r.fast_channels,
             stoichiometry=json.dumps({r.source.species[i]:int(v) for i,v in enumerate(r.N[:,k]) if v}),
             scientific_basis='CK fast redistribution or literal source participant intersection with frozen resources/CK',
             gross_mandatory=False))
    write_csv(OUT/'formal_net_channel_membership.csv',membership)
    contract=dict(schema='R6_CK_BRANCH_A_NUMERICAL_CONTRACT_V1',
       decision='GROSS_FLUX_NOT_REQUIRED_FOR_CK_PROMOTION',candidate='CK_PARTIAL_EQUILIBRIUM_V1',eta=1,
       mandatory_classes=['A','B','C','D','F','H'],gross_classes_mandatory=[],
       gross_status='SOURCE_PROVENANCE_PRESERVED;DESCRIPTIVE;BUT_NOT_VALIDATED',conditions=CONDITIONS,
       condition_definitions=[condition_record(n) for n in CONDITIONS],excluded_conditions=['R3_ADVERSE'],
       fast_reaction_ids=FAST_IDS,canonical_source_sha256=sha(ROOT/'models/pnas2017_full_reference/original/fMGG_synthesis.xml'),
       selected_net_channel_count=len(r.mandatory_channels),all_net_channel_count=678,
       net_channel_membership_sha256=sha(OUT/'formal_net_channel_membership.csv'),
       resources=RESOURCE_NAMES,algebraically_affected_states=['CK','CK_ADP','CP','CK_CP','CK_CP_ADP'],
       state_observables=r.source.species,slow_coordinate_labels=r.labels,
       primary_grid=TIMES.tolist(),startup_grid='0 plus geomspace(switch/1000,switch,100)',
       mandatory_windows=['FULL_WINDOW','POST_INITIAL_LAYER'],
       descriptive_windows=['COMPOSITE_OR_HYBRID','POST_0P05_DIAGNOSTIC'],
       metric='max_window_abs_difference/max(max_window_abs_source,floor)',
       scales='full source only; separate fixed scale in each registered window',
       floors={'state':1e-6,'slow_total':1e-6,'net_current':1e-9,'net_extent':1e-6},
       gates={'state':.01,'slow_total':.01,'net_current':.05,'net_extent':.01,'exact_conservation':1e-8,
              'switch_state_jump':.01,'slow_coordinate_switch_continuity':1e-8},
       numerical_uncertainty_fraction=.1,uncertainty_rule='sum source and reduced probe envelopes; add quadrature and source cancellation for net extents',
       solver={'state':'BDF','rtol':1e-10,'atol':1e-14,'probe_rtol':1e-11,'probe_atol':1e-15,
               'net_extent':'segmented DOP853 ODE integrators with compensated accumulation',
               'extent_primary_rtol':1e-10,'extent_primary_atol':1e-14,'extent_probe_rtol':1e-11,'extent_probe_atol':1e-15},
       source_uncertainty='hash-verified historical R4 1e-8 state/1e-10 extent probe plus fresh 1e-11 startup',
       bounds={'state_wall_s':1800,'state_rhs_calls':300000,'extent_wall_s':1800},
       startup={'rule':'10*eta*tau0','tau0':'1/(2*p0+1000)','eta':1,'full_source_startup':True,
                'reduced_initial':'T*x_full(switch); centered at original condition z0',
                'no_fitting':True,'no_tuning':True,'no_time_shift':True,'startup_extents_origin':0,
                'switch_jump':'reported; no fictitious source-reaction extent'},
       physical_root_gate='nonnegative accepted T0/T1/B and reported five CK states; no clipping',
       unproven_domain='global positivity and absolute biochemical units remain qualified; all tiny negatives retained',
       descriptive_balance_reports=['net_stoichiometric_full_state','net_stoichiometric_slow_coordinates',
                                    'algebraic_accounting_with_disclosed_jump','gross_directed_ledger'],
       promotion=False,first_order_state_model=False,parameters_fitted=[],historical_criteria_mutation=False,
       history_policy='All 2585 pre-R6 files byte-identical; prior R6 scope stop preserved in audit_stop_001')
    write_json(OUT/'formal_numerical_contract.json',contract)
    write_json(OUT/'formal_environment.json',dict(python_executable=sys.executable,python=platform.python_version(),
       numpy=np.__version__,scipy=scipy.__version__,sympy=sympy.__version__,platform=platform.platform(),
       thread_limits={n:os.environ.get(n) for n in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']},
       historical_source_environment='R3 Python3.11.4/Numpy2.2.6/Scipy1.13.1; reused original arrays, explicit numerical probe envelope',
       no_dependency_installation=True))
    write_json(OUT/'observable_requirement_decision.json',dict(decision=contract['decision'],
       authority='EXPLICIT_HUMAN_FOLLOWUP',evidence_status='EXTRACTED',human_decision_sha256=sha(OUT/'human_branch_a_decision_20261007.txt'),
       mandatory_classes=contract['mandatory_classes'],gross_classes=['E','G'],gross_mandatory=False,
       gross_status=contract['gross_status'],prior_ambiguity_preserved='audit_stop_001',promotion=False))
    paths=['docs/reduction/r6_ck_formal_observable_contract_v1.md']+[
       'results/reduction/r6_ck_validation/'+n for n in ['human_branch_a_decision_20261007.txt','formal_numerical_contract.json',
       'formal_net_channel_membership.csv','formal_environment.json','source_reuse_verification.json','observable_requirement_decision.json']]+[
       'scripts/'+n for n in ['r6_ck_common_v1.py','verify_r6_ck_source_reuse_v1.py','register_r6_ck_branch_a_v1.py',
                             'run_r6_ck_formal_v1.py','score_r6_ck_formal_v1.py']]
    paths+=['scripts/r5_ck_partial_equilibrium_runtime_v1.py','scripts/r5_ck_eta_scan_v1.py',
            'docs/reduction/r5_theory_scope_v1.json','results/reduction/r6_ck_validation/historical_snapshot.json']
    write_json(OUT/'formal_registration_binding.json',dict(schema='R6_CK_BRANCH_A_PROSPECTIVE_BINDING_V1',frozen_at_utc=stamp(),
       decisive_run_count_before_freeze=0,file_hashes={p:sha(ROOT/p) for p in paths},
       note='Finalizer/verifier do not set scientific gates; scoring/runtime/contract are frozen before any fresh comparison.'))
    print(json.dumps(dict(status='FROZEN_BRANCH_A',net_channels_mandatory=len(r.mandatory_channels),conditions=9,
                         switch=r.switch,formal_registration_sha256=sha(OUT/'formal_registration_binding.json'))),flush=True)

if __name__=='__main__':register()
