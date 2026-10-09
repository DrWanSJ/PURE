"""Verify protected bytes, evidence coverage and save the reproducibility manifest."""
import json
import subprocess
import sys
import platform
from pathlib import Path
from runtime import ROOT,OUT,sha,write_json

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def main():
    baseline=json.loads((OUT/'protected_inputs_before.json').read_text());changes=[]
    for f,v in baseline['all_existing_tracked_file_sha256'].items():
        p=ROOT/f
        if not p.exists() or sha(p)!=v:changes.append(f)
    tracked_diff=git('diff','--name-only');head=git('rev-parse','HEAD');branch=git('branch','--show-current')
    required=['docs/reduction/level_c_topology_reduction_protocol_v1.md']+['docs/reduction/energy_cycles/'+f for f in ['research_scope.md','topology_inventory.md','reaction_inventory.csv','topology_edges.csv','stoichiometric_certificate.md','stoichiometric_checks.json','effective_kinetics.md','validation_preregistration.json','validation_report.md','human_review.md']]
    missing=[f for f in required if not (ROOT/f).exists() or (ROOT/f).stat().st_size==0]
    reg=ROOT/'docs/reduction/energy_cycles/validation_preregistration.json';freeze=json.loads((OUT/'preregistration_freeze.json').read_text())
    modified_code=[f for f,v in json.loads(reg.read_text())['implementation_sha256'].items() if sha(ROOT/f)!=v]
    summary=json.loads((OUT/'scientific_summary.json').read_text())
    reports={}
    for f in ['independent_tests.json','numerical_verification.json','source_reference_verification.json','source_reference_import_verification.json','ndk_coordinate_v2_verification.json','supplemental_ppiase_reverse_verification.json']:
        p=OUT/f
        if p.exists():
            data=json.loads(p.read_text())
            statuses=[data['status']] if data.get('status') else [data['full_source_reference']['status']]+[v['status'] for v in data['coupled_source_reference'].values()]
            reports[f]={'sha256':sha(p),'status':'; '.join(statuses),'completed_pairs':data.get('completed_trajectory_pairs_checked',data.get('completed_coordinate_trajectory_pairs_checked',data.get('completed_pairs_checked')))}
    scenarios=json.loads(reg.read_text())['scenarios'];uncovered=[];duplicates=[]
    files=list((OUT/'numerical').rglob('metrics.json'))+list((OUT/'numerical_ndk_coordinate_v2').rglob('metrics.json'))
    metrics=[json.loads(p.read_text()) for p in files]
    missing_independent=[f for f in ['independent_tests.json','numerical_verification.json','source_reference_verification.json','source_reference_import_verification.json','ndk_coordinate_v2_verification.json','supplemental_ppiase_reverse_verification.json'] if f not in reports]
    independent_failures=[f for f,v in reports.items() if any('PASS' not in status for status in str(v['status']).split('; '))]
    independent_trajectory_pairs=sum(v['completed_pairs'] or 0 for v in reports.values())
    for c in scenarios:
        modes=[m['initial_mode'] for m in metrics if m['id']==c['id']]
        domain=(OUT/'numerical'/c['id']/'domain_failure.json').exists()
        if not domain and set(modes)!=set(c['initial_modes']):uncovered.append(c['id'])
        if len(modes)!=len(set(modes)):duplicates.append(c['id'])
    result={'status':'ENGINEERING_CLOSEOUT_PASS_NOT_SCIENTIFIC_APPROVAL' if not(changes or tracked_diff or missing or modified_code or uncovered or duplicates or missing_independent or independent_failures) and independent_trajectory_pairs==100 and head==baseline['source_commit'] and sha(reg)==freeze['sha256'] else 'FAIL',
      'source_commit':head,'branch':branch,'existing_tracked_inputs_checked':len(baseline['all_existing_tracked_file_sha256']),
      'protected_byte_changes':changes,'tracked_diff_names':tracked_diff,'missing_deliverables':missing,'modified_frozen_candidate_code':modified_code,
      'original_registration_unchanged':sha(reg)==freeze['sha256'],'uncovered_scenarios':uncovered,'duplicate_final_comparison_modes':duplicates,
      'completed_final_comparison_pairs':len(metrics),'registered_scenarios':len(scenarios),'domain_stops':len(list((OUT/'numerical').rglob('domain_failure.json'))),
      'independent_reports':reports,'no_commit_since_source_head':head==baseline['source_commit'],'no_scientific_promotion':summary['promotion']==False,
      'missing_independent_reports':missing_independent,
      'independent_report_failures':independent_failures,'independently_recomputed_unique_trajectory_pairs':independent_trajectory_pairs,
      'git_status':git('status','--short'),'command':sys.argv,'environment':{'python':sys.version,'platform':platform.platform()}}
    write_json(OUT/'closeout_checks.json',result)
    manifest={'source_commit':head,'source_hashes':summary['source_hashes'],'original_preregistration_sha256':sha(reg),
      'scientific_status':summary['scientific_status'],'protection_check':result['status'],'command':sys.argv,
      'outputs_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for folder in [ROOT/'docs/reduction/energy_cycles',ROOT/'scripts/energy_cycles',OUT] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.name!='artifact_manifest.json'},
      'protocol_sha256':sha(ROOT/'docs/reduction/level_c_topology_reduction_protocol_v1.md'),
      'authority':'All files are additive research evidence. No source/input/scientific decision mutation, commit, push or model approval.'}
    write_json(OUT/'artifact_manifest.json',manifest)
    print(json.dumps({k:result[k] for k in ['status','existing_tracked_inputs_checked','completed_final_comparison_pairs','domain_stops','uncovered_scenarios','protected_byte_changes']}))
    if result['status']=='FAIL':raise SystemExit(1)

if __name__=='__main__':main()
