#!/usr/bin/env python3
"""Run actual B1-2 gates, immutable regressions and the Human Review checkpoint."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/reduction/pathways';HERE=Path(__file__).resolve().parent
LOG=OUT/'phase_b1_2_execution_log.txt';FAIL=OUT/'phase_b1_2_failure_evidence.jsonl'
ENV={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1'}
BUNDLED=Path(r'C:\Users\sean\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
AUTH={'phase_b1_2_execution_authorized':True,'phase_b1_2_scientific_status':'PENDING_HUMAN_REVIEW',
      'phase_b1_2_formally_accepted':False,'commit_push_authorized':False,'qssa_authorized':False,
      'kinetic_reduction_authorized':False,'termination_authorized':False,'phase_b1_3_authorized':False,'full_phase_b_authorized':False}
NAMES=['phase_b1_2_protocol.md','phase_b1_2_source_baseline.json','phase_b1_2_source_scope.json',
       'phase_b1_2_elongation_pathways.md','phase_b1_2_witnesses.json','phase_b1_2_independent_verification.json',
       'phase_b1_2_negative_controls.json','phase_b1_2_regression.json','phase_b1_2_validation_report.json',
       'phase_b1_2_review.md','phase_b1_2_execution_log.txt','phase_b1_2_failure_evidence.jsonl',
       'phase_b1_2_original_source_evidence.json','phase_b1_2_original_source_evidence.md']
SCRIPTS=['build_elongation_witnesses.py','verify_elongation_witnesses.py','test_elongation_negative_controls.py',
         'run_phase_b1_2_validation.py','inspect_source_evidence.py']

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,d):Path(p).write_bytes((json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def append(p,s):
    with Path(p).open('a',encoding='utf-8',newline='\n') as f:f.write(s+'\n')
def fail(d):append(FAIL,json.dumps(d,sort_keys=True,ensure_ascii=False))

def run(command):
    cmd=[str(x) for x in command];label=subprocess.list2cmdline(cmd)
    cp=subprocess.run(cmd,cwd=ROOT,env=ENV,capture_output=True,encoding='utf-8',errors='replace')
    r={'actual_command':label,'exit_code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}
    append(LOG,'COMMAND: '+label+'\nEXIT_CODE: '+str(cp.returncode)+'\nSTDOUT:\n'+cp.stdout+'\nSTDERR:\n'+cp.stderr)
    if cp.returncode:fail({'stage':'executed_command',**r})
    print(json.dumps({'command':label,'exit_code':cp.returncode}),flush=True)
    return r

def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def regressions():
    legacy=imported('b1_2_readonly_legacy_runner',ROOT/'scripts/pathways/phase_b1_1/run_phase_b1_1_validation.py')
    reports=[]
    def intercept(path,data):
        if Path(path)!=OUT/'phase_b1_1_regression.json':raise RuntimeError('Unanticipated legacy write '+str(path))
        reports.append(data)
    legacy.save=intercept;legacy.run=run;legacy.log=lambda s:append(LOG,s);legacy.fail=fail
    # Only the established read-only regression function, never legacy.main().
    prior=legacy.regressions()
    result={'phase_a':prior['phase_a'],'b0':prior['b0'],'html':prior['html'],'cli_inspection':prior['cli_inspection']}
    with tempfile.TemporaryDirectory(prefix='b1-2-upstream-safe-') as temporary:
        tmp=Path(temporary)
        for path in OUT.glob('phase_b1_1_*'):
            if path.is_file():shutil.copyfile(path,tmp/path.name)
        shutil.copyfile(OUT/'phase_b0_handoff_witnesses.json',tmp/'phase_b0_handoff_witnesses.json')
        shim=('import sys; from pathlib import Path; '
              'sys.path[:0]=[str(Path.cwd()/"scripts/pathways/phase_b1_1"),str(Path.cwd()/"scripts/pathways/phase_b1_1/followup")]; '
              'import verify_initiation_witnesses as old; old.OUT=Path(sys.argv[1]); '
              'import verify_followup as follow; follow.OUT=Path(sys.argv[1]); '
              'entry=sys.argv[2]; sys.argv=[entry]+sys.argv[3:]; '
              'import importlib; m=importlib.import_module(entry); raise SystemExit(m.main())')
        operations=[('b1_1_positive','verify_initiation_witnesses','phase_b1_1_independent_verification.json'),
                    ('b1_1_negative','test_initiation_negative_controls','phase_b1_1_negative_controls.json'),
                    ('followup_positive','verify_followup','phase_b1_1_followup_independent_verification.json'),
                    ('followup_negative','test_followup_negative_controls','phase_b1_1_followup_negative_controls.json')]
        for name,entry,_ in operations:
            dest=tmp/(name+'.json')
            command=run([sys.executable,'-c',shim,tmp,entry,'--input-dir',OUT,'--report',dest])
            report=load(dest) if dest.exists() else {'status':'FAIL','diagnostic':'No actual rerun report'}
            status=report.get('status',report.get('structural_verification_status','FAIL'))
            result[name]={'status':'PASS' if command['exit_code']==0 and status=='PASS' else 'FAIL','execution':command,
                          'actual_report':report,'write_policy':'TEMPORARY_REPORTS_AND_FAILURES_ONLY; CANONICAL_ROOT_READ_ONLY'}
        result['temporary_failure_evidence']={p.name:p.read_text(encoding='utf-8') for p in tmp.glob('*failure*.jsonl')
            if p.name not in {q.name for q in OUT.glob('phase_b1_1_*failure*.jsonl')} or p.read_bytes()!=(OUT/p.name).read_bytes()}
    neg=result['b1_1_negative']['actual_report'];follow=result['followup_negative']['actual_report']
    result['B1_1_negative_counts']={'historical_run':neg.get('controls_run',0),'historical_passed':neg.get('controls_passed',0),
        'followup_run':follow.get('followup_controls_run',0),'followup_passed':follow.get('followup_controls_passed',0),
        'total_run':neg.get('controls_run',0)+follow.get('followup_controls_run',0),
        'total_passed':neg.get('controls_passed',0)+follow.get('followup_controls_passed',0)}
    result['mandatory_status']='PASS' if all(result[k]['status']=='PASS' for k in ('phase_a','b0','b1_1_positive','b1_1_negative','followup_positive','followup_negative')) else 'FAIL'
    result['optional_browser_policy']='NOT_RUN may limit UI coverage only; any executed FAIL remains a failure'
    result['historical_files_written']=False
    save(OUT/'phase_b1_2_regression.json',result);return result

def reproduce():
    names=['phase_b1_2_source_scope.json','phase_b1_2_witnesses.json','phase_b1_2_elongation_pathways.md']
    builds=[];executions=[]
    with tempfile.TemporaryDirectory(prefix='b1-2-determinism-') as t:
        for n in range(2):
            dest=Path(t)/str(n);executions.append(run([sys.executable,HERE/'build_elongation_witnesses.py','--output-dir',dest]))
            builds.append({p:digest(dest/p) for p in names if (dest/p).exists()})
    delivered={p:digest(OUT/p) for p in names if (OUT/p).exists()}
    ok=all(c['exit_code']==0 for c in executions) and len(delivered)==len(names) and builds[0]==builds[1]==delivered
    return {'status':'PASS' if ok else 'FAIL','fresh_builds':2,'executions':executions,'fresh_build_hashes':builds,'delivered_hashes':delivered}

def preservation():
    b=load(OUT/'phase_b1_2_source_baseline.json');changed=[p for p,h in b['protected_file_hashes'].items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
    commands=[run(['git','rev-parse','--show-toplevel']),run(['git','remote','get-url','origin']),run(['git','branch','--show-current']),
        run(['git','rev-parse','HEAD']),run(['git','rev-list','--left-right','--count','HEAD...@{upstream}']),run(['git','status','-sb']),
        run(['git','diff','--name-status']),run(['git','diff','--cached','--name-status']),run(['git','ls-files','--others','--exclude-standard']),run(['git','diff','--check'])]
    new=commands[8]['stdout'].splitlines()
    whitelist={('docs/reduction/pathways/'+n) for n in NAMES}|{('scripts/pathways/phase_b1_2/'+n) for n in SCRIPTS}
    forbidden=[p for p in new if p not in whitelist]
    ok=not changed and not forbidden and all(c['exit_code']==0 for c in commands) and commands[0]['stdout'].strip().replace('\\','/').lower()==str(ROOT).replace('\\','/').lower() and commands[1]['stdout'].strip()=='https://github.com/DrWanSJ/PURE.git' and commands[2]['stdout'].strip()==b['branch'] and commands[3]['stdout'].strip()==b['beginning_head'] and commands[4]['stdout'].split()==['0','0'] and not commands[6]['stdout'].strip() and not commands[7]['stdout'].strip()
    return {'status':'PASS' if ok else 'FAIL','protected_tracked_files':len(b['protected_file_hashes']),'changed_existing_files':changed,
        'repository_root':str(ROOT),'branch':commands[2]['stdout'].strip(),'beginning_head':b['beginning_head'],'ending_head':commands[3]['stdout'].strip(),
        'upstream_ahead_behind':commands[4]['stdout'].split(),'beginning_worktree':b['beginning_status'],'ending_worktree':commands[5]['stdout'],
        'new_files':new,'unexpected_new_files':forbidden,'all_authorized_files':sorted(whitelist),'commit_push':'NOT_ATTEMPTED',
        'executions':commands,'git_rules_file':b['git_rules_file'],'repository_ai_guidance':b['repository_ai_guidance']}

def review(report):
    data=load(OUT/'phase_b1_2_witnesses.json');scope=load(OUT/'phase_b1_2_source_scope.json');ws={w['witness_id']:w for w in data['witnesses']}
    q=scope['reactions'];w3=ws['W3'];reg=report.get('regression',{})
    groups=[('H1','E2 continuity',[1,13],'B1-1 formal signoff H2, P7; W4 single 0001','EXTRACTED source continuity; INFERRED physical release order','S27 E2 is explicitly virtual; early release is not a complete physiological mechanism'),
        ('H2','EF-Tu and two Gly deliveries',[13,14,16,17,74,75,77,78],'B0 W1 carrier rules; B1-1 P7','EXTRACTED finite source lots; author definitions EXTRACTED','S27 bound-state definitions support author interpretation; two supplies remain conditional'),
        ('H3','Two peptide formations',[18,79],'B1-1 E1/E2 composition limits','EXTRACTED source transitions; INFERRED full molecular composition','S27 peptidyltransfer definitions and Pept0002/0003 names do not certify full composition; rates assumed fast'),
        ('H4','EF-G and translocation',[19,22,24,25,80,83,85,86],'B0 multi-carrier witness acceptance; W2/W3','EXTRACTED states/author definitions; UNRESOLVED physiological timing','Article p.7 supports reaction 22 EF-G hydrolysis context; S27 defines translocation; complete SI text/PDF absent'),
        ('H5','Two-round material and energy ledger',[13,16,17,19,24,25,68,74,77,78,80,85,86],'B0 source ledger limits; B1-1 initiator release counted only in W4','EXTRACTED exact net; INFERRED moiety correspondence','Bound GTP is not extra free GTP; GDP release is not regeneration; no global conservation certificate'),
        ('H6','T_pre and termination boundary',[86,125,796,797,811,812],'B1-1 E2 handoff; no upstream termination acceptance','EXTRACTED incidence; UNRESOLVED boundary naming','S27 calls factor-free endpoint elongation complex with UAA; RF-bound successors are named pre-termination. Researcher must judge proposed T_pre label'),
        ('H7','Alternative topology and limits',[13,21,19,20,22,23,68,69,74,82,80,81,83,84],'B0 competing carrier pools; B1-1 separate release routes','EXTRACTED alternatives/reverses; UNRESOLVED unenumerated scenarios','Source-ID tie-breaking and positive k1 do not establish dominance; unsearched alternatives and resource availability remain open')]
    lines=['# Phase B1-2 Human Review package','',
        '**'+report['execution_status']+'**; scientific status **PENDING_HUMAN_REVIEW**; formally accepted **false**.','',
        'The researcher authorized local structural implementation through this checkpoint. No scientific Y/N decision, commit, push, kinetic reduction or termination execution is issued.','',
        'Read [the complete pathway equations](phase_b1_2_elongation_pathways.md), [original paper/SI interpretation evidence](phase_b1_2_original_source_evidence.md), [independent verification](phase_b1_2_independent_verification.json), [negative fixtures](phase_b1_2_negative_controls.json), and [executed gates](phase_b1_2_validation_report.json).','',
        '## Repository and authority','', '```json',json.dumps(report['repository'],ensure_ascii=False,indent=2),'```','',
        'Only new B1-2 documents and scripts are present. Every task-start tracked file is checked by raw SHA-256. The Git rules file and repository AI guidance were not found in searched locations; the explicit attached task rules governed.','',
        '## Source structure and exact ledger','',
        f"All 968 directions are inventoried; {scope['coverage']['selected_inventory']} selected core/context directions, {scope['coverage']['core_directions']} core (62 positive / 132 zero), {scope['coverage']['search_directions']} eligible positive directions for W1-W3. Original 0001 belongs to elongation context but is withheld from W1-W3 discovery and fired exactly once in W4. No core direction is silently reclassified.",'',
        '```text',w3['net_reaction'],'```','',
        'This CONCEPTUAL_NET is an independently recomputed source event sum. Two delivery lots and two EF-G GTP lots are distinct. Four PO4, two EFTu_GDP, two EFG_GDP and one free tRNAGlyGCC are produced. The second peptide-bearing tRNA remains represented in T_pre. Free ATP/ADP/AMP/GTP/GDP/PPi are absent from all W3 events and have explicit zero ledger entries. W4 adds the accepted upstream net and single initiator release, giving five PO4 and one tRNAfMetCAU.','',
        'E2 and the second-round entry are author-defined virtual complexes (S27). Their early tRNA-release convention requires scientific review. T_pre is a proposed factor-free stop-codon interface; the author calls RF-bound successor states pre-termination complexes. No endpoint substitution has been made.','',
        '## Actual validation','', '| Gate | Status | Actual evidence |','|---|---|---|']
    for gate in report['gates']:lines.append('| '+gate['gate']+' | '+gate['status']+' | '+gate['criterion']+'; '+gate['evidence_reference']+' |')
    lines+=['',f"B1-2 controls: {report.get('negative_controls',{}).get('controls_passed',0)}/{report.get('negative_controls',{}).get('controls_run',0)} passed. Five deliberately Petri-enabled/lineage-invalid controls are required to reject specifically INVALID_LINEAGE.",'',
        'Inherited MATLAB CI issue: the task reports 99 passed / 3 failed / 1 incomplete despite green workflow. It is preserved as inherited evidence, not repaired or counted as a B1-2 PASS. Browser checks are separately recorded with actual executed counts. Real inspection/environment failures remain in the append-only failure log.','',
        '## H1-H7 researcher decisions','', '| Checkpoint | Exact IDs | Original subsystem | Upstream evidence | Evidence status | Article/SI need and scientific ambiguity | Researcher conclusion | Researcher notes |','|---|---|---|---|---|---|---|']
    for h,title,nums,up,status,ambiguity in groups:
        ids=[f're{n:010d}' for n in nums];members=sorted({Path(m['source_file']).name for r in ids for m in q[r]['original_subsystem_memberships']})
        lines.append('| '+h+' '+title+' | '+', '.join(ids)+' | '+', '.join(members)+' | '+up+' | '+status+' | '+ambiguity+' | PENDING (Y / N / CONDITIONAL / PENDING) | |')
    for h,title,nums,up,status,ambiguity in groups:
        lines+=['','### '+h+' '+title,'',ambiguity,'', 'Relevant upstream record: '+up+'. Researcher conclusion: **PENDING**. Researcher notes:','']
        for n in nums:
            r=f're{n:010d}';row=q[r]
            lines+=['- `'+r+'` / '+row['level_c']+' / '+row['reference_activity']+' / k1='+row['reference_parameter']+': `'+row['equation']+'`. Original subsystem: '+('; '.join(Path(m['source_file']).name+' / '+m['local_reaction_id'] for m in row['original_subsystem_memberships']) or 'none')+'.']
    lines+=['','## Reproducible local execution','', '```powershell','python scripts/pathways/phase_b1_2/run_phase_b1_2_validation.py','```','',
        'The runner uses temporary output/failure destinations for legacy acceptance functions and two fresh B1-2 builds. It returns nonzero on any missing or failed mandatory gate. Exact commands, stdout/stderr and exit codes are in the execution log.','',
        '## Stop boundary','', '```json',json.dumps(AUTH,indent=2),'```','',
        'STOP. H1-H7 remain pending researcher decisions. No commit/push, scientific acceptance, termination, B1-3, QSSA or kinetic reduction follows automatically.','']
    (OUT/'phase_b1_2_review.md').write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    if not (OUT/'phase_b1_2_source_baseline.json').exists():raise RuntimeError('Task-start baseline required; never recapture a dirty checkout')
    started=datetime.now(timezone(timedelta(hours=8))).isoformat();append(LOG,'B1-2 VALIDATION RUN: '+started)
    report={'execution_started_Asia_Shanghai':started,'authorization':AUTH,'reproducible_command':'python scripts/pathways/phase_b1_2/run_phase_b1_2_validation.py'}
    commands=[];ind={};negative={};reg={};det={};original={}
    try:
        commands.append(run([sys.executable,HERE/'build_elongation_witnesses.py']))
        commands.append(run([sys.executable,HERE/'verify_elongation_witnesses.py']))
        ind=load(OUT/'phase_b1_2_independent_verification.json')
        commands.append(run([sys.executable,HERE/'test_elongation_negative_controls.py']))
        negative=load(OUT/'phase_b1_2_negative_controls.json')
        if BUNDLED.exists():
            commands.append(run([BUNDLED,HERE/'inspect_source_evidence.py']));original=load(OUT/'phase_b1_2_original_source_evidence.json')
        else:original={'status':'NOT_RUN','reason':'Bundled paper/workbook reader unavailable'}
        print('Running existing independent regressions with temporary output destinations.',flush=True)
        reg=regressions();det=reproduce()
    except Exception:
        report['actual_exception']=traceback.format_exc();fail({'stage':'validation_runner','traceback':report['actual_exception']});append(LOG,report['actual_exception'])
    report['executions']=commands;repo=preservation();report['repository']=repo
    report['independent_verification_summary']={'status':ind.get('status','NOT_RUN'),'witness_event_counts':{w['witness_id']:w['events_checked'] for w in ind.get('witnesses',[])}}
    report['negative_controls']={k:negative.get(k,0) for k in ('controls_run','controls_passed','controls_failed','controls_not_run','petri_enabled_lineage_invalid_cases','petri_enabled_lineage_invalid_passed')}
    report['negative_controls']['status']=negative.get('status','NOT_RUN')
    report['regression']=reg;report['deterministic_rebuild']=det;report['original_source_evidence']=original
    report['inherited_matlab_issue']={'authority':'USER_TASK_REPORTED_INHERITED_CI','passed':99,'failed':3,'incomplete':1,'rerun_in_B1_2':False,'repaired':False,'counts_as_B1_2_PASS':False}
    verified=ind.get('status')=='PASS' and all(c['exit_code']==0 for c in commands[:2])
    criterion=[('A','Canonical hashes and 241/968/3854/483/485 verified','phase_b1_2_independent_verification.json:source_integrity',verified),
       ('B','All selected directions/disabled contexts/subsystem memberships independently classified','phase_b1_2_independent_verification.json:scope',verified),
       ('C','Exact E2 and immutable B1-1 continuity; 0001 absent in W1-W3 and once in W4','phase_b1_2_independent_verification.json:boundary_verification/P7_read_only_revalidation',verified),
       ('D','W2 actual first delivery, peptide formation, EF-G and tRNA release','phase_b1_2_independent_verification.json:witnesses/W2',verified),
       ('E','W3 actual second round with distinct supplies to T_pre','phase_b1_2_independent_verification.json:witnesses/W3',verified),
       ('F','Independent rational equations, occurrence counts, markings and net','phase_b1_2_independent_verification.json:external_reference_example/witnesses',verified),
       ('G','Independently allocated finite lots and reconstructed carrier DAG','phase_b1_2_independent_verification.json:witnesses/independently_reconstructed_lineage',verified),
       ('H','Bound/free nucleotide, PO4 and tRNA accounting, no false recovery','phase_b1_2_witnesses.json:resource_ledger; independent check_witness',verified),
       ('I','Every selected outlet/reverse and T_pre termination context retained','phase_b1_2_source_scope.json:termination_boundary_appendix; original_source_evidence',verified and original.get('status')=='PASS'),
       ('J','All controls reject for correct invariant, >=4 Petri-enabled lineage controls','phase_b1_2_negative_controls.json',negative.get('status')=='PASS' and negative.get('controls_run',0)>=24 and negative.get('petri_enabled_lineage_invalid_passed',0)>=4),
       ('K','Read-only historical regressions, 35 B1-1 controls and byte-identical fresh builds','phase_b1_2_regression.json; deterministic_rebuild',reg.get('mandatory_status')=='PASS' and det.get('status')=='PASS' and reg.get('B1_1_negative_counts',{}).get('total_passed')==35 and reg.get('html',{}).get('status')!='FAIL'),
       ('L','All old hashes preserved; additive whitelist, unchanged HEAD/upstream and authority','repository/source_baseline/authorization',repo['status']=='PASS')]
    report['gates']=[{'gate':g,'criterion':c,'status':'PASS' if passed else 'FAIL' if commands else 'NOT_RUN','evidence_reference':ref} for g,c,ref,passed in criterion]
    report['engineering_status']='PASS' if all(g['status']=='PASS' for g in report['gates']) else 'FAIL'
    report['execution_status']='B1_2_ENGINEERING_COMPLETE_PENDING_HUMAN_REVIEW' if report['engineering_status']=='PASS' else 'B1_2_INCOMPLETE_OR_INCONCLUSIVE'
    report['scientific_status']='PENDING_HUMAN_REVIEW';report['phase_b1_2_formally_accepted']=False
    report['script_hashes']={p:digest(HERE/p) for p in SCRIPTS};report['frozen_protocol_sha256']=digest(OUT/'phase_b1_2_protocol.md')
    report['failure_evidence_records']=sum(1 for s in FAIL.read_text(encoding='utf-8').splitlines() if s)
    save(OUT/'phase_b1_2_validation_report.json',report)
    if (OUT/'phase_b1_2_witnesses.json').exists():review(report)
    # Final rehash after report/review writing. All authorized output files must exist.
    report['repository']=preservation();missing=[p for p in report['repository']['all_authorized_files'] if not (ROOT/p).is_file()]
    report['deliverable_completeness']={'status':'PASS' if not missing else 'FAIL','missing_files':missing,'exact_new_file_list':report['repository']['new_files']}
    if report['repository']['status']!='PASS' or missing:
        report['gates'][-1]['status']='FAIL';report['engineering_status']='FAIL';report['execution_status']='B1_2_INCOMPLETE_OR_INCONCLUSIVE'
    save(OUT/'phase_b1_2_validation_report.json',report);review(report)
    append(LOG,'FINAL_STATUS: '+report['execution_status']+'\nENGINEERING_GATES: '+json.dumps({g['gate']:g['status'] for g in report['gates']})+'\nSTOP: NO COMMIT/PUSH OR SCIENTIFIC PROMOTION')
    if report['engineering_status']!='PASS':fail({'stage':'final_gates','gates':report['gates'],'execution_status':report['execution_status']})
    print(json.dumps({'status':report['execution_status'],'gates':{g['gate']:g['status'] for g in report['gates']},'negative_controls':report['negative_controls']}),flush=True)
    return 0 if report['engineering_status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
