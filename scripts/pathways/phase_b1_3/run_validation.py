"""Actual B1-3 gates, isolated old regressions, determinism and human checkpoint."""
import os,sys,json,subprocess,tempfile,shutil,traceback,importlib.util
from pathlib import Path
from datetime import datetime,timezone,timedelta
sys.dont_write_bytecode=True
from inspect_source import ROOT,OUT,load,save,digest
HERE=Path(__file__).resolve().parent
LOG=OUT/'phase_b1_3_execution_log.txt';FAIL=OUT/'phase_b1_3_failure_evidence.jsonl'
BUNDLED=Path(r'C:\Users\sean\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe')
ENV={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1'}
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat()
def append(path,data):
    with path.open('a',encoding='utf-8') as f:f.write(data+'\n')
def failure(x):append(FAIL,json.dumps({'timestamp':now(),**x},ensure_ascii=False,sort_keys=True))
def run(args):
    args=list(map(str,args));started=now();cp=subprocess.run(args,cwd=ROOT,env=ENV,capture_output=True,encoding='utf-8',errors='replace')
    record={'started_Asia_Shanghai':started,'ended_Asia_Shanghai':now(),'actual_command':subprocess.list2cmdline(args),'exit_code':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr}
    append(LOG,json.dumps(record,ensure_ascii=False,sort_keys=True));print(json.dumps({'command':record['actual_command'],'exit_code':cp.returncode}),flush=True)
    if cp.returncode:failure({'stage':'executed_command',**record})
    return record
def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def regressions():
    legacy=imported('read_only_B1_2_regression',ROOT/'scripts/pathways/phase_b1_2/run_phase_b1_2_validation.py');captures=[]
    def intercept(path,data):
        if Path(path)!=OUT/'phase_b1_2_regression.json':raise RuntimeError('UNEXPECTED_OLD_WRITE '+str(path))
        captures.append(data)
    legacy.save=intercept;legacy.run=run;legacy.fail=failure;legacy.append=lambda path,text:append(LOG,text)
    result=legacy.regressions()
    # Only an existing read-only regression function; never any old runner main.
    with tempfile.TemporaryDirectory(prefix='b1-3-safe-b1-2-') as temp:
        tmp=Path(temp)
        for path in OUT.glob('phase_b1_2_*'):
            if path.is_file():shutil.copyfile(path,tmp/path.name)
        for path in OUT.glob('phase_b1_1_*'):
            if path.is_file():shutil.copyfile(path,tmp/path.name)
        shim=('import sys; from pathlib import Path; sys.path.insert(0,str(Path.cwd()/"scripts/pathways/phase_b1_2")); '
              'import verify_elongation_witnesses as verify; verify.OUT=Path(sys.argv[1]); entry=sys.argv[2]; '
              'sys.argv=[entry]+sys.argv[3:]; import importlib; m=importlib.import_module(entry); raise SystemExit(m.main())')
        for label,entry in [('b1_2_positive','verify_elongation_witnesses'),('b1_2_negative','test_elongation_negative_controls')]:
            report=tmp/(label+'.json');execution=run([sys.executable,'-B','-c',shim,tmp,entry,'--input-dir',OUT,'--report',report]);ev=load(report) if report.exists() else {'status':'FAIL','reason':'No fresh report'}
            result[label]={'status':'PASS' if execution['exit_code']==0 and ev.get('status')=='PASS' else 'FAIL','execution':execution,'actual_report':ev,'write_policy':'REPORT_AND_FAILURE_DESTINATIONS_TEMPORARY_ONLY'}
        result['b1_2_temporary_failure_evidence']={p.name:p.read_text(encoding='utf-8') for p in tmp.glob('*failure*.jsonl') if p.read_bytes()!=(OUT/p.name).read_bytes()}
    required=['phase_a','b0','b1_1_positive','b1_1_negative','followup_positive','followup_negative','b1_2_positive','b1_2_negative']
    result['mandatory_status']='PASS' if all(result[k]['status']=='PASS' for k in required) and result['html']['status']=='PASS' else 'FAIL'
    result['inherited_MATLAB']={'status':'NOT_RUN','reported_prior_result':'99 passed / 3 failed / 1 incomplete','fixed':False,'counted_as_B1_3_PASS':False}
    result['old_main_entrypoints_invoked']=False;result['historical_files_written']=False
    save(OUT/'phase_b1_3_regression.json',result);return result
def reproduce():
    names=['phase_b1_3_source_scope.json','phase_b1_3_witnesses.json','phase_b1_3_termination_recycling_pathways.md','phase_b1_3_independent_verification.json','phase_b1_3_negative_controls.json','phase_b1_3_original_source_evidence.json','phase_b1_3_original_source_evidence.md','phase_b1_3_source_matrices.json','phase_b1_3_matrix_verification.json']
    builds=[];commands=[]
    with tempfile.TemporaryDirectory(prefix='b1-3-determinism-') as temp:
        for i in range(2):
            dest=Path(temp)/str(i)
            commands.append(run([sys.executable,'-B',HERE/'build_witnesses.py','--output-dir',dest]))
            commands.append(run([sys.executable,'-B',HERE/'verify_witnesses.py','--input-dir',dest,'--report',dest/'phase_b1_3_independent_verification.json']))
            commands.append(run([sys.executable,'-B',HERE/'test_negative_controls.py','--input-dir',dest,'--report',dest/'phase_b1_3_negative_controls.json']))
            commands.append(run([BUNDLED,'-B',HERE/'inspect_original_evidence.py','--output-dir',dest]))
            commands.append(run([sys.executable,'-B',HERE/'audit_full_matrices.py','--input-dir',dest,'--output-dir',dest]))
            builds.append({p:digest(dest/p) for p in names if (dest/p).exists()})
    delivered={p:digest(OUT/p) for p in names if (OUT/p).exists()}
    ok=all(c['exit_code']==0 for c in commands) and len(delivered)==len(names) and builds[0]==builds[1]==delivered
    return {'status':'PASS' if ok else 'FAIL','fresh_builds':2,'deterministic_deliverables':names,'fresh_hashes':builds,'delivered_hashes':delivered,'executions':commands}
def protection():
    baseline=load(OUT/'phase_b1_3_source_baseline.json')
    changed=[p for p,h in baseline['protected_file_hashes'].items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
    cmds=[run(c) for c in [['git','rev-parse','--show-toplevel'],['git','remote','get-url','origin'],['git','branch','--show-current'],['git','rev-parse','HEAD'],['git','rev-list','--left-right','--count','HEAD...@{upstream}'],['git','ls-remote','--heads','origin','codex/energy-cycles-v1'],['git','status','-sb'],['git','diff','--name-status'],['git','diff','--cached','--name-status'],['git','ls-files','--others','--exclude-standard'],['git','diff','--check']]]
    new=cmds[9]['stdout'].splitlines();unexpected=[p for p in new if not (p.startswith('docs/reduction/pathways/phase_b1_3_') or p.startswith('scripts/pathways/phase_b1_3/'))]
    remote=cmds[5]['stdout'].split()[0] if cmds[5]['stdout'].strip() else None
    ok=not changed and not unexpected and all(c['exit_code']==0 for c in cmds) and not cmds[7]['stdout'].strip() and not cmds[8]['stdout'].strip() and cmds[4]['stdout'].split()==['0','0'] and cmds[2]['stdout'].strip()==baseline['branch'] and cmds[3]['stdout'].strip()==baseline['beginning_head'] and remote==baseline['beginning_head']
    return {'status':'PASS' if ok else 'FAIL','protected_tracked_files':len(baseline['protected_file_hashes']),'changed_existing_files':changed,'new_authorized_files':new,'unexpected_new_files':unexpected,'machine_hostname':baseline['machine_hostname'],'windows_user':baseline['windows_user'],'repository_root':str(ROOT),'branch':cmds[2]['stdout'].strip(),'beginning_head':baseline['beginning_head'],'ending_head':cmds[3]['stdout'].strip(),'live_remote_head':remote,'synchronization':cmds[4]['stdout'].split(),'ending_git_status':cmds[6]['stdout'],'commit':'NOT_ATTEMPTED','push':'NOT_ATTEMPTED','executions':cmds}
def human_review(report,data,inv):
    questions=[('H1','RF-free T_pre 连续接口',[796,811],'W4之后准确源种是否与两支入口相同？保留B1-2 H3/H4/H6条件；项目缩写不是作者定义。'),
      ('H2','RF1/RF2竞争',[796,797,811,812],'一枚T_pre被一次结合消费后不能同时进入另一支；结合逆向允许重新选择，不等于同时产两肽。'),
      ('H3','游离肽产物及残留复合物',[798,813,810,823],'只有对应源事件产生free Pept0003；两支留下不同RF-bound term态，零参数肽释放逆向仍记录。'),
      ('H4','RF3参与与直接解离替代',[799,814,829,843,846,838,840,842,847,870,881,884,879],'分别审查RF3GDP交换、预供应RF3GTP、apoRF3路径。GDP/GTP结合态不可混同free核苷酸。'),
      ('H5','RRF/EF-G回收',[904,906,895,900,901,908,909,902,910,911,913,914,915,916,917,918,919,920,921,922,923,308],'实际70S拆分是0910，先产两个occupied子单位；0911及50S释放多次序才恢复free组分。是否认可新EFG_GTP有限边界条件？'),
      ('H6','源物种资源账本',[798,813,843,846,840,842,908,902,911,913,916,918],'直接回收新增一个PO4；RF3交换另消耗freeGTP并产生freeGDP和一个PO4。joint直接/交换PO4为6/7，W4五个只计一次。完整元素/基团守恒未认证。'),
      ('H7','逆向、竞争与失活上下文',[797,800,812,815,830,832,834,839,841,844,845,871,873,875,880,882,883,896,905,907,909,810,823,957],'正参数反向与重新结合在允许集内；零参数和降解结构保留。代表性最短结构证据不能排名生理用量或通量。'),
      ('H8','源结构与解释范围',[796,798,811,813,910,911],'S12–S16、S27作者定义与原始模型结构为EXTRACTED；载体身份投影和生理解释INFERRED；完整SI文本/物理组成证书未建立。'),
      ('H9','未来拓扑降阶的问题',[796,811,799,814,838,879,904,906,908,902,910,913,914,915],'重复RF支与50S释放子路径可提出聚合问题；共享T_pre竞争、RF3核苷酸状态、释放/拆分时点、有限EFG/RRF载体约束会妨碍聚合。本轮不选择或实现降阶。')]
    lines=['# Phase B1-3 研究者科学复核表','', '**'+report['execution_status']+'**','', '所有H1–H9科学决定均为PENDING_HUMAN_REVIEW；Codex没有代签。工程PASS不等于科学接受、动力学验证或完整模型验证。','', '## 当前工程证据','', '| Gate | 状态 | 证据 |','|---|---|---|']
    for gate in report['gates']:lines.append('| '+gate['gate']+' | '+gate['status']+' | '+gate['evidence']+' |')
    lines+=['', '主文件：完整事件方程见 [pathways](phase_b1_3_termination_recycling_pathways.md)，逐事件源种/来源token/DAG/账本见 [witnesses](phase_b1_3_witnesses.json)，独立验证见 [verification](phase_b1_3_independent_verification.json)，原始S27/工作簿定位见 [source evidence](phase_b1_3_original_source_evidence.md)，实际负对照见 [negative controls](phase_b1_3_negative_controls.json)。','', '有限供应不是作者操作浓度或内源再生。保留B1-2 H3/H4/H6条件：虚拟态完整组成、真实化学与生理时序、停码接口命名和全网络结论不获自动扩展。继承MATLAB 99/3/1未重跑或修复。','']
    for h,title,nums,reason in questions:
        lines+=['## '+h+' — '+title,'', '科学状态：**PENDING_HUMAN_REVIEW**','', reason,'', '证据位置：`phase_b1_3_source_scope.json/reactions` 对应ID，`phase_b1_3_witnesses.json/witnesses`及机器账本；`phase_b1_3_original_source_evidence.json/S27_definitions,S27_parameters,subsystem_reaction_rows`提供源页/行/hash。','', '支持方程：','']
        for n in nums:
            r=f're{n:010d}';q=inv['reactions'][r];members='; '.join(Path(m['source_file']).name+':'+m['local_reaction_id'] for m in q['original_subsystem_memberships'])
            lines.append('- `'+r+'` / k1='+q['reference_parameter']+' / '+members+'：`'+q['equation']+'`。')
        lines+=['', '已知限制：源状态身份与有限可执行性不证明完整分子组成、浓度轨迹、主导通量、全网络元素或核苷酸基团守恒；更多路径未穷举。','', '研究者决定（留空）：______ `Y / N / CONDITIONAL / NEED_MORE_EVIDENCE`','', '研究者备注（留空）：','', '______','']
    lines+=['## 停止点','', '请研究者亲自填写H1–H9；本轮不提交或推送，不修改旧正式接受记录。本文件不是签署。','']
    (OUT/'phase_b1_3_review.md').write_bytes(('\n'.join(lines)+'\n').encode())
def navigation(data,inv):
    nodes=[];edges=[]
    for p in sorted(OUT.glob('phase_b1_3_*')):
        if p.is_file() and p.name!='phase_b1_3_evidence_navigation.json':nodes.append({'id':p.name,'path':p.relative_to(ROOT).as_posix(),'sha256':digest(p),'authority':'DERIVED_B1_3_ENGINEERING_EVIDENCE','freshness':'CURRENT_GENERATION_HASH','confidence':'SOURCE_BOUND','status':'EXTRACTED'})
    for ref in inv['source_provenance']:nodes.append({'id':ref['path'],'path':ref['path'],'sha256':ref['sha256'],'authority':ref['authority'],'freshness':'RAW_HASH_RECHECKED','confidence':'PRIMARY_SOURCE','status':'EXTRACTED'})
    for w in data['witnesses']:
        nodes.append({'id':w['witness_id'],'type':'finite_witness','authority':'CANONICAL_SOURCE_EVENTS','status':'EXTRACTED','confidence':'EXACT_REPLAY','freshness':'BUILD_AND_INDEPENDENT_REPLAY'})
        for e in w['reaction_occurrences']:edges.append({'source':e['reaction_id'],'target':w['witness_id'],'relation':'executed_source_direction','status':'EXTRACTED','authority':'CANONICAL_SBML','confidence':'EXACT_STOICHIOMETRY','freshness':'RAW_HASH_BOUND'})
        if w.get('starting_post_release_witness'):edges.append({'source':w['starting_post_release_witness'],'target':w['witness_id'],'relation':'exact_source_marking_handoff','status':'EXTRACTED','confidence':'EXACT_CARRIER_TOKEN_HANDOFF','authority':'FINITE_PETRI_REPLAY','freshness':'CURRENT_REPLAY'})
    reaction_nodes=set(inv['selected_direction_ids'])|{e['reaction_id'] for w in data['witnesses'] for e in w['reaction_occurrences']}
    for r in sorted(reaction_nodes):nodes.append({'id':r,'type':'original_reaction','equation':inv['reactions'][r]['equation'],'authority':'CANONICAL_SBML','confidence':'EXACT_SOURCE','freshness':'CURRENT_SOURCE_HASH','status':'EXTRACTED'})
    nodes.append({'id':'molecular_interpretation','type':'open_question','status':'AMBIGUOUS','authority':'HUMAN_REVIEW_REQUIRED','confidence':'NOT_CERTIFIED','freshness':'CURRENT_LIMITATION'})
    nodes.append({'id':'carrier_projection','type':'declared_identity_contract','status':'INFERRED','authority':'SOURCE_IDS_AND_S27_CONTEXT','confidence':'OPAQUE_CARRIER_NOT_ATOMIC_COMPOSITION','freshness':'SOURCE_HASH_BOUND'})
    save(OUT/'phase_b1_3_evidence_navigation.json',{'nodes':nodes,'edges':edges,'provenance_status':'DERIVED_NAVIGATION_ONLY','scientific_status':'PENDING_HUMAN_REVIEW'})
def main():
    append(LOG,'B1-3 ACTUAL VALIDATION RUN '+now());report={'started_Asia_Shanghai':now(),'scientific_status':'PENDING_HUMAN_REVIEW','authorization':load(OUT/'phase_b1_3_source_baseline.json')['authorization']}
    operations=[run([sys.executable,'-B',HERE/'build_witnesses.py']),run([sys.executable,'-B',HERE/'verify_witnesses.py']),run([sys.executable,'-B',HERE/'test_negative_controls.py']),run([BUNDLED,'-B',HERE/'inspect_original_evidence.py']),run([sys.executable,'-B',HERE/'audit_full_matrices.py'])]
    ind=load(OUT/'phase_b1_3_independent_verification.json');neg=load(OUT/'phase_b1_3_negative_controls.json');original=load(OUT/'phase_b1_3_original_source_evidence.json');data=load(OUT/'phase_b1_3_witnesses.json');inv=load(OUT/'phase_b1_3_source_scope.json')
    try:reg=regressions()
    except Exception:
        reg={'mandatory_status':'FAIL','traceback':traceback.format_exc()};failure({'stage':'regressions',**reg});save(OUT/'phase_b1_3_regression.json',reg)
    det=reproduce();protect=protection()
    gates=[]
    criteria={'A':'Source hashes/counts and source provenance','B':'All 968 classified; 258 exact selected contexts','C':'Shared T_pre and RF1/RF2 exclusive competition','D':'Independent free Pept0003 release in both branches','E':'Direct/RF3 alternatives and finite nucleotide carriers','F':'Both source-supported full ribosome recycling endpoints','G':'Exact S_full*w and per-event Petri execution','H':'Origin tokens and ribosome/factor/tRNA/peptide lineage','I':'Full source-species resource ledgers and cumulative histories','J':'Reverse/alternative/zero parameter topology preserved','K':'36 intended-invariant adversarial controls, >=5 Petri-enabled lineage-invalid','L':'Old source/witness/negative/browser regressions; two fresh identical builds','M':'Tracked raw SHA unchanged; additions only; no commit/push/promotion'}
    for g in 'ABCDEFGHIJ':gates.append({'gate':g,'status':'PASS' if ind['status']=='PASS' and original['status']=='PASS' else 'FAIL','criterion':criteria[g],'evidence':'phase_b1_3_independent_verification.json; phase_b1_3_original_source_evidence.json'})
    gates.append({'gate':'K','status':neg['status'],'criterion':criteria['K'],'evidence':'phase_b1_3_negative_controls.json'})
    gates.append({'gate':'L','status':'PASS' if reg.get('mandatory_status')=='PASS' and det['status']=='PASS' else 'FAIL','criterion':criteria['L'],'evidence':'phase_b1_3_regression.json; validation_report/determinism'})
    gates.append({'gate':'M','status':protect['status'],'criterion':criteria['M'],'evidence':'validation_report/git_protection; source_baseline/protected_file_hashes'})
    matrix=load(OUT/'phase_b1_3_matrix_verification.json')
    gates[6]['status']='PASS' if gates[6]['status']=='PASS' and matrix['status']=='PASS' else 'FAIL'
    gates[6]['evidence']='phase_b1_3_independent_verification.json; phase_b1_3_matrix_verification.json; phase_b1_3_source_matrices.json'
    complete=all(g['status']=='PASS' for g in gates)
    report.update({'execution_status':'B1_3_ENGINEERING_COMPLETE_PENDING_HUMAN_REVIEW' if complete else 'B1_3_INCOMPLETE_OR_INCONCLUSIVE','gates':gates,'commands':operations,'independent_verification_summary':{k:ind[k] for k in ['status','source_integrity','inventory','competition','signed_upstream'] if k in ind},'witness_count':len(data['witnesses']),'negative_controls_summary':{k:neg[k] for k in ['status','controls_run','controls_passed','controls_failed','petri_enabled_lineage_invalid_count']},'regression_status':reg.get('mandatory_status'),'browser_status':reg.get('html',{}).get('status'),'determinism':det,'git_protection':protect,'source_evidence_summary':{'status':original['status'],'subsystem_rows':len(original['subsystem_reaction_rows']),'S27_parameter_rows':len(original['S27_parameters']),'S27_definitions':len(original['S27_definitions'])},'inherited_MATLAB':reg.get('inherited_MATLAB'),'scientific_limitations':['No physiological branch ranking or kinetic validation','Conditional finite supply, not endogenous regeneration','B1-2 H3/H4/H6 remain conditional','No complete molecular/elemental/phosphate-moiety certificate','Standalone complete SI text/PDF not established locally','No complete route enumeration','H1-H9 all PENDING_HUMAN_REVIEW'],'ended_Asia_Shanghai':now()})
    report['explicit_full_matrix_audit']={k:matrix[k] for k in ['status','matrix_shape','raw_arc_entries','arc_coefficient_sum','witnesses_checked','arc_count_semantics']}
    save(OUT/'phase_b1_3_validation_report.json',report);human_review(report,data,inv);navigation(data,inv)
    # Recheck additions after creating all human-facing outputs.
    report['git_protection']=protection();report['gates'][-1]['status']=report['git_protection']['status'];report['ended_Asia_Shanghai']=now()
    save(OUT/'phase_b1_3_validation_report.json',report);navigation(data,inv)
    print(json.dumps({'execution_status':report['execution_status'],'gates':[(g['gate'],g['status']) for g in report['gates']],'witnesses':len(data['witnesses']),'negative_controls':report['negative_controls_summary'],'protected_files':protect['protected_tracked_files']},ensure_ascii=False),flush=True)
    return 0 if all(g['status']=='PASS' for g in report['gates']) else 1
if __name__=='__main__':raise SystemExit(main())
