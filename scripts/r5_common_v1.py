"""Read-only source access and additive R5 output helpers."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',OMP_NUM_THREADS='1')
from pathlib import Path
import json,csv,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/reduction/r5_mechanism_first'
DOC=ROOT/'docs/reduction'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def write_csv(p,rows):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def write_doc(name,text):
 p=DOC/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.rstrip()+'\n',encoding='utf-8',newline='\n')
def checked_registration():
 b=json.loads((OUT/'registration_binding.json').read_text())
 for p,h in b.items():assert sha(ROOT/p)==h,p
 return json.loads((DOC/'r5_theory_scope_v1.json').read_text())
