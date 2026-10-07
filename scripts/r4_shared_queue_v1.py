"""Share existing registered queue via atomic per-condition execution claim."""
from r4_fast_block_common_v1 import *
import subprocess,sys,uuid
def share(family):
 base=OUT/(family.lower()+'_only');registration=json.loads((base/'queue_registration.json').read_text());os.environ['R4_QUEUE_OWNER']=registration['queue_owner'];driver=str(uuid.uuid4())
 for name in registration['conditions'][2:]:
  p=base/name;current=json.loads((p/'result.json').read_text())
  if current['status']!='QUEUED_EXECUTION':continue
  with (p/('execution_'+driver+'.log')).open('w',encoding='utf-8') as log:
   res=subprocess.run([sys.executable,str(ROOT/'scripts/run_r4_family_grid_v1.py'),'--family',family,'--condition',name],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env=os.environ)
  print(family,name,json.loads((p/'result.json').read_text())['status'],'exit',res.returncode,flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--family',required=True,choices=['GlyRS','MetRS']);a=p.parse_args();share(a.family)
