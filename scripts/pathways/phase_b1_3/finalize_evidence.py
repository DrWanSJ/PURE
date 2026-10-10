"""Repair only failed isolated harness input; retain failure; finalize fresh evidence."""
import sys,shutil,tempfile,json
from pathlib import Path
sys.dont_write_bytecode=True
import run_validation as r
OUT=r.OUT;ROOT=r.ROOT
def main():
    reg=r.load(OUT/'phase_b1_3_regression.json');old=reg['b1_2_positive']
    if old['status']!='PASS':
        with tempfile.TemporaryDirectory(prefix='b1-3-complete-upstream-input-') as temporary:
            tmp=Path(temporary)
            for pattern in ['phase_b1_1_*','phase_b1_2_*']:
                for p in OUT.glob(pattern):
                    if p.is_file():shutil.copyfile(p,tmp/p.name)
            shim=('import sys; from pathlib import Path; sys.path.insert(0,str(Path.cwd()/"scripts/pathways/phase_b1_2")); '
                  'import verify_elongation_witnesses as verify; verify.OUT=Path(sys.argv[1]); '
                  'sys.argv=["verify_elongation_witnesses"]+sys.argv[2:]; raise SystemExit(verify.main())')
            dest=tmp/'fresh_positive.json';command=r.run([sys.executable,'-B','-c',shim,tmp,'--input-dir',OUT,'--report',dest]);actual=r.load(dest) if dest.exists() else {'status':'FAIL'}
            reg['b1_2_positive']={'status':'PASS' if command['exit_code']==0 and actual.get('status')=='PASS' else 'FAIL','execution':command,'actual_report':actual,'write_policy':'ALL_REQUIRED_SIGNED_UPSTREAM_FILES_COPIED_READ_ONLY; REPORT_AND_FAILURE_TEMPORARY','previous_attempts':[old],'harness_repair':'Added missing B1-1 signed upstream files to redirected OUT; unchanged verifier or acceptance logic.'}
    required=['phase_a','b0','b1_1_positive','b1_1_negative','followup_positive','followup_negative','b1_2_positive','b1_2_negative']
    reg['mandatory_status']='PASS' if all(reg[k]['status']=='PASS' for k in required) and reg['html']['status']=='PASS' else 'FAIL'
    r.save(OUT/'phase_b1_3_regression.json',reg)
    report=r.load(OUT/'phase_b1_3_validation_report.json');det=report['determinism'];names=['phase_b1_3_source_matrices.json','phase_b1_3_matrix_verification.json'];fresh=[];commands=[]
    with tempfile.TemporaryDirectory(prefix='b1-3-matrix-determinism-') as temporary:
        for i in range(2):
            dest=Path(temporary)/str(i);dest.mkdir()
            commands.append(r.run([sys.executable,'-B',r.HERE/'audit_full_matrices.py','--input-dir',OUT,'--output-dir',dest]))
            fresh.append({p:r.digest(dest/p) for p in names if (dest/p).exists()})
    delivered={p:r.digest(OUT/p) for p in names}
    matrix_ok=all(c['exit_code']==0 for c in commands) and fresh[0]==fresh[1]==delivered
    det['matrix_determinism']={'status':'PASS' if matrix_ok else 'FAIL','fresh_hashes':fresh,'delivered_hashes':delivered,'executions':commands}
    det['status']='PASS' if det['status']=='PASS' and matrix_ok else 'FAIL'
    det['deterministic_deliverables']+=names
    for i in range(2):det['fresh_hashes'][i].update(fresh[i])
    det['delivered_hashes'].update(delivered)
    matrix=r.load(OUT/'phase_b1_3_matrix_verification.json')
    report['explicit_full_matrix_audit']={k:matrix[k] for k in ['status','matrix_shape','raw_arc_entries','arc_coefficient_sum','witnesses_checked','arc_count_semantics']}
    report['regression_status']=reg['mandatory_status'];report['gates'][6]['status']=matrix['status'];report['gates'][6]['evidence']='phase_b1_3_independent_verification.json; phase_b1_3_matrix_verification.json; phase_b1_3_source_matrices.json'
    report['gates'][11]['status']='PASS' if reg['mandatory_status']=='PASS' and det['status']=='PASS' else 'FAIL'
    report['git_protection']=r.protection();report['gates'][12]['status']=report['git_protection']['status']
    complete=all(g['status']=='PASS' for g in report['gates'])
    report['execution_status']='B1_3_ENGINEERING_COMPLETE_PENDING_HUMAN_REVIEW' if complete else 'B1_3_INCOMPLETE_OR_INCONCLUSIVE';report['ended_Asia_Shanghai']=r.now()
    report['prior_failed_harness_evidence_retained']='regression/b1_2_positive/previous_attempts and append-only failure_evidence'
    r.save(OUT/'phase_b1_3_validation_report.json',report)
    data=r.load(OUT/'phase_b1_3_witnesses.json');inv=r.load(OUT/'phase_b1_3_source_scope.json')
    r.human_review(report,data,inv);r.navigation(data,inv)
    print(json.dumps({'execution_status':report['execution_status'],'gates':[(g['gate'],g['status']) for g in report['gates']],'protected_files':report['git_protection']['protected_tracked_files'],'deterministic_deliverables':len(det['deterministic_deliverables']),'previous_failures_retained':True}));return 0 if complete else 1
if __name__=='__main__':raise SystemExit(main())
