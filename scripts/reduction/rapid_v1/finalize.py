"""Read-only Git/source checks, fingerprints and derived evidence navigation."""
import csv,subprocess,datetime,ast,platform
from common import *

def git(*args):
    r=subprocess.run(['git','-c','core.quotepath=false',*args],cwd=ROOT,text=True,encoding='utf-8',capture_output=True)
    assert r.returncode==0,r.stderr
    return r.stdout.strip()

def main():
    integrity=protection();branch=git('branch','--show-current');head=git('rev-parse','HEAD');origin=git('remote','get-url','origin');root=git('rev-parse','--show-toplevel');upstream=git('rev-parse','@{upstream}');remote=git('ls-remote','origin','refs/heads/'+branch).split()[0]
    assert branch=='codex/energy-cycles-v1' and head==upstream==remote=='7a95c29b6bf80b567863cc70a631859016144924'
    assert origin=='https://github.com/DrWanSJ/PURE.git' and Path(root).resolve()==ROOT.resolve()
    raw=git('status','--porcelain=v1','-uall');baseline=load(RESULT/'baseline.json');prefix=['configs/reduction/rapid_v1.json','docs/reduction/rapid_reduction/','scripts/reduction/rapid_v1/','results/reduction/rapid_v1/'];unknown=[]
    for line in raw.splitlines():
        path=line[3:]
        if not line.startswith('?? ') or not(path in baseline['protected_raw_sha256'] or any(path.startswith(p) for p in prefix)):unknown.append(line)
    assert not unknown,unknown
    sources=list((ROOT/'scripts/reduction/rapid_v1').glob('*.py'))
    for p in sources:ast.parse(p.read_text(encoding='utf-8'))
    validation=load(RESULT/'validation_results.json');review=load(RESULT/'b1_3_fresh_audit.json')['review'];assert all(r['researcher_decision']=='' for r in review)
    assert len(validation['reduced_solver_crosschecks'])==4 and all(r['status']=='PASS' for r in validation['reduced_solver_crosschecks'])
    completion=load(RESULT/'report_completion.json');assert completion['all_four_coupled_pass']
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    result={'checked_at':now,'machine':platform.node(),'account':'sean','repository_root':str(ROOT),'origin':origin,'branch':branch,'starting_HEAD':head,'final_local_HEAD':head,'final_remote_HEAD':remote,'upstream_HEAD':upstream,'ahead_behind':git('rev-list','--left-right','--count','HEAD...@{upstream}'),'source_and_inherited_protection':integrity,'unknown_changes':unknown,'syntax_checked_scripts':len(sources),'commit':'NOT_ATTEMPTED','push':'NOT_ATTEMPTED','merge':'NOT_ATTEMPTED','new_branch_worktree_clone':'NOT_ATTEMPTED','researcher_signatures':'BLANK','scientific_status':'HUMAN_REVIEW_REQUIRED'}
    save(RESULT/'git_and_protection.json',result)
    append(RESULT/'execution_log.jsonl',{'operation':'FINAL_LOCAL_VERIFICATION','checked_at':now,'mathematical_certificate':str(DOC/'mathematical_certificate.json'),'validation_results':str(RESULT/'validation_results.json'),'read_only_git':result,'Python':platform.python_version(),'source_hashes_unchanged':True})
    finalraw=git('status','--porcelain=v1','-uall');(RESULT/'final_git_status.txt').write_text(finalraw+'\n',encoding='utf-8')
    # Self-referential fingerprint artifacts are enumerated separately, never given
    # a fictitious self-hash. Every other file is hashed at finalization.
    exclusions={RESULT/'file_manifest.csv',DOC/'evidence_navigation.json'}
    files=sorted({CONFIG}|{p for d in [DOC,RESULT,ROOT/'scripts/reduction/rapid_v1'] for p in d.rglob('*') if p.is_file() and p not in exclusions})
    file_rows=[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size,'role':'PRESERVED_INITIAL_CAMPAIGN' if 'campaign_scoring_v1' in p.parts else 'PHASE_C_ADDITIVE'} for p in files]
    with (RESULT/'file_manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(file_rows[0]));w.writeheader();w.writerows(file_rows)
    candidate=load(DOC/'candidate_source_map.json');nodes=[];edges=[]
    for r in file_rows:
        pid=r['path'];kind='NUMERICAL_EVIDENCE' if pid.endswith(('.npz','.csv')) and 'results/' in pid else 'DERIVED_EVIDENCE';nodes.append({'id':pid,'path':pid,'sha256':r['sha256'],'source_authority':kind,'evidence_status':'EXTRACTED','confidence':'FILE_INTEGRITY_VERIFIED; SCIENTIFIC_APPROVAL_SEPARATE','freshness':{'checked_at':now,'source_HEAD':head},'scientific_status':'HUMAN_REVIEW_REQUIRED'})
    for cid in ['models/pnas2017_full_reference/original/fMGG_synthesis.xml','models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv','docs/reduction/source_coordinate_certificate_v4.json']:
        nodes.append({'id':cid,'path':cid,'sha256':sha(ROOT/cid),'source_authority':'CANONICAL_SOURCE_OR_PREVIOUSLY_ACCEPTED_CERTIFICATE','evidence_status':'EXTRACTED','confidence':'SOURCE_IDENTITY_VERIFIED','freshness':{'checked_at':now,'source_HEAD':head}})
        edges.append({'from':cid,'to':'docs/reduction/rapid_reduction/mathematical_certificate.json','relation':'RECOMPUTED_FROM'})
    for c in candidate:
        cid='candidate:'+c['candidate_id'];nodes.append({'id':cid,'source_authority':'DERIVED_SOURCE_TOPOLOGY','evidence_status':'INFERRED','confidence':'EXACT_IDS; VALIDATION_SCOPE_SEPARATE','status':c['status'],'provenance':'docs/reduction/rapid_reduction/candidate_source_map.json','freshness':{'checked_at':now,'source_HEAD':head}});edges.append({'from':cid,'to':'docs/reduction/rapid_reduction/candidate_source_map.json','relation':'DETAILS_AND_COMPLETE_SOURCE_EQUATIONS'})
    edges+=[{'from':'results/reduction/rapid_v1/validation_results.json','to':'docs/reduction/rapid_reduction/review_and_decision.md','relation':'NUMERICAL_EVIDENCE_FOR_HUMAN_DECISION'},{'from':'results/reduction/rapid_v1/b1_3_fresh_audit.json','to':'docs/reduction/rapid_reduction/review_and_decision.md','relation':'AI_RECOMMENDATION_NOT_HUMAN_SIGNATURE'}]
    graph={'schema':'PHASE_C_EVIDENCE_NAVIGATION_V1','nodes':nodes,'edges':edges,'uncertainties':[{'status':'AMBIGUOUS','subject':'Full biochemical composition of original complexes','effect':'No elemental or charge approval claimed.'},{'status':'AMBIGUOUS','subject':'Two discarded recycling micro correlations','effect':'Exact protected quotient does not recover individual source release paths.'}],'protected_existing_files_manifest':'results/reduction/rapid_v1/baseline.json','final_added_files_manifest':'results/reduction/rapid_v1/file_manifest.csv','manifest_self_hash_exclusions':['results/reduction/rapid_v1/file_manifest.csv','docs/reduction/rapid_reduction/evidence_navigation.json'],'scientific_status':'HUMAN_REVIEW_REQUIRED'}
    save(DOC/'evidence_navigation.json',graph)
    assert all(sha(ROOT/n['path'])==n['sha256'] for n in nodes if 'path' in n)
    print(json.dumps({'final_protection':integrity,'phase_C_files':len(file_rows)+2,'added_evidence_bytes':sum(r['bytes'] for r in file_rows),'local_remote_HEAD':head,'branch':branch,'unknown_changes':unknown,'HUMAN_REVIEW_REQUIRED':True}))
if __name__=='__main__':main()
