"""Append a delivery receipt only after live origin HEAD equals committed local HEAD."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from prepare_chain01_v2 import ROOT, OUT, dump, check_integrity

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('round',choices=['V2-R0','V2-R1','V2-R2'])
    args=ap.parse_args()
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    if branch!='codex/pnas-topology-first':
        raise ValueError('Wrong delivery branch')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/'+branch],cwd=ROOT,text=True).split()[0]
    if head!=remote:
        raise ValueError('Push not delivered: live remote HEAD does not match local HEAD')
    path=OUT/'git_delivery_manifest.json'
    manifest=json.loads(path.read_text()) if path.exists() else {'branch':branch,'remote':'origin','rounds':[]}
    if any(rec['round']==args.round for rec in manifest['rounds']):
        raise ValueError('Round already recorded; do not overwrite receipt')
    manifest['rounds'].append({'round':args.round,'local_commit_sha':head,'verified_remote_head_sha':remote,
        'push_result':'SUCCESS; origin branch HEAD verified directly after git push',
        'verified_at_utc':datetime.now(timezone.utc).isoformat(),'historical_integrity':check_integrity(),
        'receipt_scope':'Payload commit delivery; this receipt is included in the next commit to avoid a circular self hash.'})
    dump(path,manifest)
    print(json.dumps(manifest['rounds'][-1]))
