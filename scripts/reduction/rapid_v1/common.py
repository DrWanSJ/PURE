"""Read-only project runtime entry points and additive Phase C evidence."""
import sys,json,hashlib,os,datetime,traceback
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
RESULT=ROOT/'results/reduction/rapid_v1';DOC=ROOT/'docs/reduction/rapid_reduction';CONFIG=ROOT/'configs/reduction/rapid_v1.json'
from verify_reduction_audit_v0 import source_network,columns,rows,OUT as LEGACY
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,data):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_bytes((json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def append(path,data):
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(data,ensure_ascii=False,sort_keys=True)+'\n')
def failure(stage,**data):append(RESULT/'failure_evidence.jsonl',{'stage':stage,'time':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),**data})
def protection():
    baseline=load(RESULT/'baseline.json');changed=[p for p,h in baseline['protected_raw_sha256'].items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    if changed:raise RuntimeError('PROTECTED_SOURCE_OR_EVIDENCE_CHANGED '+str(changed))
    freeze=load(RESULT/'freeze.json')
    if sha(CONFIG)!=freeze['config_sha256'] or sha(DOC/'protocol.md')!=freeze['protocol_sha256']:raise RuntimeError('FROZEN_PROTOCOL_CHANGED')
    return {'status':'PASS','protected_existing_files':len(baseline['protected_raw_sha256']),'B1_3_files':len(baseline['inherited_B1_3_files']),'changed':changed}
