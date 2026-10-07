"""Claim future grid conditions before dispatch, preventing duplicate runs."""
from r4_fast_block_common_v1 import *
import subprocess,sys,uuid
def queue(family):
 token=str(uuid.uuid4());os.environ['R4_QUEUE_OWNER']=token
 conditions=[c['condition_id'] for c in REG['conditions']][2:];base=OUT/(family.lower()+'_only')
 # Both existing workers own BASE/GLYRS_LOW. Claim the other seven before
 # executing; the initial workers' existing-output guard stops at HIGH.
 for name in conditions:
  p=base/name/'result.json'
  if p.exists():raise RuntimeError('Queue must never overwrite a claimed or completed run')
  write_json(p,{'status':'QUEUED_EXECUTION','candidate':'R4_'+family.upper()+'_ONLY','condition':name,'queue_owner':token,'scientific_status':'NOT_YET_SCORED','preregistration_sha256':sha(DOC/'r4_fast_block_candidates_v1.json')})
 write_json(base/'queue_registration.json',{'queue_owner':token,'conditions':conditions,'existing_worker_conditions':[c['condition_id'] for c in REG['conditions']][:2],'scientific_protocol_unchanged':True,'purpose':'Bounded independent process parallelism; no duplicate candidate-condition solves or deleted conditions.'})
 for name in conditions:
  p=base/name
  with (p/'execution.log').open('w',encoding='utf-8') as log:
   res=subprocess.run([sys.executable,str(ROOT/'scripts/run_r4_family_grid_v1.py'),'--family',family,'--condition',name],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env=os.environ)
  status=json.loads((p/'result.json').read_text())['status'];print(family,name,status,'process_exit',res.returncode,flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--family',required=True,choices=['GlyRS','MetRS']);a=p.parse_args();queue(a.family)
