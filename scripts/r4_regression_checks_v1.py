"""Read-only regression checks against frozen scientific evidence."""
from r4_fast_block_common_v1 import *
import subprocess,sys
p=OUT/'regression_checks';p.mkdir(exist_ok=True);rows=[]
for script in ['verify_pnas2017_artifacts.py','verify_source_coordinate_certificate_v1.py','verify_r3_bounded_closeout_v1.py']:
 command=[sys.executable,str(ROOT/'scripts'/script)];res=subprocess.run(command,cwd=ROOT,text=True,encoding='utf-8',errors='replace',capture_output=True)
 path=p/(script+'.log');path.write_text(res.stdout+res.stderr,encoding='utf-8',newline='\n');rows.append({'check':script,'exit_code':res.returncode,'log_sha256':sha(path)});print(script,res.returncode,flush=True)
write_json(p/'result.json',{'status':'PASS' if all(r['exit_code']==0 for r in rows) else 'FAIL','checks':rows,'scope':'Historical engineering/provenance regression only, not scientific candidate approval'})
