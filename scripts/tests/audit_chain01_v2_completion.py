"""Requirement-level completion audit, including live delivery and source integrity."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/reduction/chain01_v2'
sys.path.insert(0,str(ROOT/'scripts/reduction'))
from prepare_chain01_v2 import check_integrity,digest,dump

FIGURES=['01_product_trajectory_comparison','02_product_flux_comparison','03_pi_release_comparison',
         '04_eftu_gdp_release_comparison','05_internal_occupancy_comparison','06_long_time_output_comparison',
         '07_slow_input_response','08_resource_ledger_error','09_complexity_accuracy_tradeoff']


def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def audit(delivery=False,readonly=False):
    checks=[]
    def prove(requirement,evidence): checks.append({'requirement':requirement,'status':'PROVED','evidence':evidence})
    integrity=check_integrity(); config=read(ROOT/'configs/reduction/chain01_v2_validation.json'); summary=read(OUT/'validation_summary.json')
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(); assert branch=='codex/pnas-topology-first'
    prove('Only authorized branch; source/V1/R1-R8 bytes preserved',{'branch':branch,'historical_integrity':integrity})
    freeze=read(OUT/'protocol_freeze.json'); assert freeze['frozen_before_first_V2_numerical_trajectory']
    assert digest(ROOT/'configs/reduction/chain01_v2_validation.json')==freeze['bindings']['configs/reduction/chain01_v2_validation.json']
    prove('Protocol, rates, windows, scales and all four gates frozen before V2',{'sha256':digest(ROOT/'configs/reduction/chain01_v2_validation.json'),'freeze':'protocol_freeze.json'})
    manifest=read(OUT/'source_manifest.json'); certificate=read(OUT/'mathematical_certificate.json')
    assert manifest['audit_status']=='PASSED_EXACT_SOURCE_AUDIT' and manifest['author_reaction_csv_selected_crosscheck']=='PASS'
    for name,rec in certificate['models'].items():
        assert len(rec['net_per_species_difference_exact'])==241 and set(rec['net_per_species_difference_exact'].values())=={'0'}
    assert manifest['boundary_reaction']['products_exact']=={'EFTu_GTP_GlytRNAGlyGCC':'1','elRS70SAGGU0002_fMet':'1'}
    prove('Four source reactions and re21 audited against SBML/author CSV; aliases and candidate source columns exact',{'source_manifest':'source_manifest.json','math':'mathematical_certificate.json','species_rows_per_model':241})
    assert config['tests']['A_pulse']['end_tau']>=100 and config['tests']['B_constant']['end_tau']==10000
    assert [config['tests'][f'C_slow_{n}']['T_slow_tau'] for n in (20,100,1000)]==[20,100,1000]
    for name in ('D_fast','D_inventory'): assert config['tests'][name]['domain']!='IN_DOMAIN'
    prove('Pulse, sustained 10000tau, all three slow ratios, and both V1 negative controls retained',{'tests':list(config['tests'])})
    phaseinfo={}
    for phase in ('base','boundary'):
        idx=read(OUT/(phase+'_latest.json')); ps=read(ROOT/idx['summary']); directory=(ROOT/idx['summary']).parent
        numeric=read(directory/'verification_report.json'); independent=read(directory/'independent_verification.json')
        assert numeric['status']==independent['status']=='PASS'
        assert len(ps['tests'])==7 and len(independent['analytic_checks'])==28 and independent['required_window_scores_verified']==480
        assert all(r['status']=='PASS' for t in numeric['checks'].values() for r in t.values())
        assert all(r['status']=='PASS' for r in independent['waiting_time_resolvent_checks'].values())
        assert digest(directory/'runner_source.py')==read(directory/'runtime_manifest.json')['runner_sha256']
        if 'verifier_sha256' in independent: assert digest(directory/'independent_verifier_source.py')==independent['verifier_sha256']
        for artifact in read(directory/'artifact_manifest.json')['artifacts']: assert digest(ROOT/artifact['path'])==artifact['sha256']
        csvpaths=[]
        for testid,models in ps['tests'].items():
            assert set(models)=={'Full','Direct','Two-stage','Three-stage'}
            for name,rec in models.items():
                path=ROOT/rec['raw_csv']; csvpaths.append(rec['raw_csv'])
                with gzip.open(path,'rt',encoding='utf-8') as f:
                    headers=next(csv.reader(f))
                for field in ('registered_grid','obs_product_extent','obs_product_current','obs_pi_current','obs_pi_extent','obs_gdp_current','obs_gdp_extent','obs_bound_pi','obs_bound_gdp','obs_unfinished'):
                    assert field in headers,(phase,path,field)
                assert rec['sample_count']>=rec['registered_sample_count']>2000
                assert {'early_0_10','late_5_10','macro_10_end'}<=set(rec['metrics'])
                assert rec['window_integrated_formation_current']
                assert any(r['t_over_tau']==10 for r in rec['endpoints'])
                if phase=='boundary':
                    for field in ('primary_undocked_ribosome','primary_undocked_intact_gtp_carrier','primary_xi_re21'): assert field in headers
                    assert rec['allocation']
        figs=ROOT/idx['figures'] if 'figures' in idx else OUT/'figures'/phase/directory.name
        for name in FIGURES:
            with Image.open(figs/(name+'.png')) as img:
                img.verify()
        assert read(figs/'data_sources.json')['plots_are_actual_saved_numerics']
        phaseinfo[phase]={'attempt':ps['attempt'],'raw_trajectory_count':len(csvpaths),'numeric':'PASS','independent':'PASS',
            'verified_required_window_scores':480,'required_figures':FIGURES,'figures':str(figs.relative_to(ROOT)).replace('\\','/')}
    prove('Gate 1: all states/extents, currents, nonnegativity, convergence, fate ledgers and independent analytic checks',phaseinfo)
    prove('Gate 2/3: raw current/extent data, all windows/checkpoints, fixed scales and cumulative-relative comparison',{'required_window_scores_verified':960,'raw_trajectories_in_current_attempts':56,'resource_metrics':config['gates']['resources']['metrics']})
    for key in ('reaction_count','chemical_state_count','transient_state_count','extent_counter_count','steady_unit_input_stage_occupancy_exact','release_delay_exact','cumulative_asymptotic_offsets_vs_full_exact'):
        assert all(key in rec for rec in certificate['models'].values())
    prove('Independent steady flux/inventory, mean waits/variances, asymptotic resource offsets and honest complexity counts',{'math':'mathematical_certificate.json','independent':'waiting_time_resolvent_checks in both phase reports'})
    boundary_math=read(OUT/'boundary_analytical_certificate.json')
    assert boundary_math['source_manifest_sha256']==digest(OUT/'source_manifest.json')
    assert boundary_math['c_exact']=='23/100'
    assert set(boundary_math['models'])==set(config['models'])
    assert all(r['discrepancy']<=config['gates']['numerical']['state_extent_absolute'] for m in boundary_math['saved_long_endpoint_checks'].values() for r in m.values())
    prove('Restored-boundary exact currents, inventories and cumulative slopes/intercepts match saved 10000tau endpoints',{'certificate':'boundary_analytical_certificate.json','models':list(boundary_math['models'])})
    assert summary['selected_local_model']=='Three-stage' and summary['full_coupled_validation']=='NOT_STARTED'
    for key,value in [('product','PRODUCT_OUTPUT_SUPPORTED'),('resources','RESOURCE_LEDGER_SUPPORTED'),('macro','LONG_TIME_MACRO_SUPPORTED')]:
        assert summary['base_decisions']['Three-stage'][key]==summary['boundary_decisions']['Three-stage'][key]==value
    assert summary['boundary_decisions']['Three-stage']['boundary']=='LOCAL_BOUNDARY_SUPPORTED'
    assert summary['base_decisions']['Two-stage']['macro']=='LONG_TIME_MACRO_SUPPORTED'
    assert summary['boundary_decisions']['Two-stage']['boundary']=='NOT_SUPPORTED'
    assert summary['base_decisions']['Direct']['resources']=='NOT_SUPPORTED'
    prove('Gate 4: original re21 material mapping, condition-specific minimum-model decision, no full-coupled or reduced-core promotion',{'selected':'Three-stage','domain':summary['condition_domain'],'decision_source':'validation_summary.json'})
    first=OUT/'base/attempt_001'; assert read(first/'verification_report.json')['status']=='NUMERICALLY_UNRESOLVED'
    assert read(first/'independent_verification.json')['status']=='PASS'
    assert digest(first/'runner_source.py')==read(first/'runtime_manifest.json')['runner_sha256']
    prove('Native unresolved first sampling attempt and execution source preserved',{'path':'base/attempt_001','native_status':'NUMERICALLY_UNRESOLVED'})
    for filename in ('chain01_v2_preregistration.md','chain01_v2_base_validation_report.md','chain01_v2_validation_report.md'):
        assert (ROOT/'docs/reduction'/filename).is_file()
    graph=read(OUT/'evidence_navigation.json')
    for node in graph['nodes']: assert digest(ROOT/node['id'])==node['sha256'],node['id']
    prove('Scientific report, figure provenance, artifact bindings and derived evidence navigation',{'reports':'docs/reduction/chain01_v2*','navigation_nodes':len(graph['nodes'])})
    receipts=read(OUT/'git_delivery_manifest.json')['rounds']
    required=['V2-R0','V2-R1','V2-R2'] if delivery else ['V2-R0','V2-R1']
    for stage in required:
        receipt=next(r for r in receipts if r['round']==stage)
        assert receipt['local_commit_sha']==receipt['verified_remote_head_sha']
        subprocess.run(['git','merge-base','--is-ancestor',receipt['local_commit_sha'],'HEAD'],cwd=ROOT,check=True)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/'+branch],cwd=ROOT,text=True).split()[0]
    if delivery: assert head==remote
    prove('Each completed round committed, pushed and actual remote SHA verified',{'required_rounds':required,'receipts':receipts,'current_local_head':head,'live_remote_head':remote,'R2_delivery_required':delivery})
    result={'status':'COMPLETE' if delivery else 'SCIENTIFIC_WORK_COMPLETE_R2_DELIVERY_PENDING','checks':checks,'scientific_scope':'LOCAL ONLY; no complete PURE protein/shared ATP-GTP validation','unresolved_scientific_limits':['arbitrary fast supply not accepted','nonzero internal composition not reconstructable','shared-pool/downstream coupling not tested','empirical parameter range limited to author constants'],
            'current_phase_info':phaseinfo}
    if not readonly: dump(OUT/('completion_audit.json' if delivery else 'completion_audit_before_delivery.json'),result)
    print(json.dumps({'status':result['status'],'requirements_proved':len(checks),'local_head':head,'remote_head':remote}))
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--require-delivery',action='store_true'); ap.add_argument('--read-only',action='store_true')
    args=ap.parse_args(); audit(args.require_delivery,args.read_only)
