"""One prospective R8 registration; no diagnostic calculation."""
from pathlib import Path
import subprocess, hashlib, json
from r7_ck_h1_v1 import ROOT, FirstOrderCK, CONDITIONS, sha, load, write_json

OUT=ROOT/'results/reduction/r8_ck_startup_layer'
PARENT='20ca5215d949c9451b3e6fd4435c18991783ac29'
BRANCH='codex/r8-ck-startup-layer-20261008'
VIS={
 'docs/visualization/reduction_reasoning_atlas.html':('8b57011b32607ee5130810434e9eb75698fa9abd471f3c54eec3c5d1247143a5','HTML','Generated Chinese-language reduction reasoning atlas, embedded scientific data and provenance.'),
 'scripts/build_reduction_reasoning_atlas.py':('5d0e1c0ec9a26b754eae2e1417398931468dfc69246392a4a88d3a5ac5c67da0','GENERATOR_CODE','Read-only provenance-bound builder with species/reaction/pair/pool assertions.'),
 'scripts/reduction_reasoning_atlas.template.html':('81b6a603cd1ee050fdc712907ae48d1fa58fa7ed3eff98b3dbd18db8b284b157','HTML_TEMPLATE','Interactive atlas layout and evidence navigation with embedded payload placeholder.')}

def git(*args):
 return subprocess.check_output(['git',*args],cwd=ROOT,text=True,encoding='utf-8').strip()

def main():
 assert git('rev-parse','HEAD')==PARENT
 assert git('branch','--show-current')==BRANCH
 assert not (OUT/'registration.json').exists(),'REGISTRATION_ALREADY_EXISTS'
 assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
 files=git('ls-files').splitlines()
 snapshot={p:sha(ROOT/p) for p in files}
 write_json(OUT/'pre_r8_snapshot.json',dict(parent=PARENT,files=snapshot))
 donor=Path('C:/Users/sean/Desktop/GUV');transfer=[]
 for p,(expected,kind,role) in VIS.items():
  assert sha(donor/p)==sha(ROOT/p)==expected,'DONOR_OR_COPY_CHANGED:'+p
  assert not git('ls-files','--',p),'TARGET_ALREADY_TRACKED:'+p
  transfer.append(dict(source_absolute_path=str(donor/p),path=p,byte_count=(donor/p).stat().st_size,
    original_sha256=expected,initial_copied_sha256=sha(ROOT/p),classification=kind,role=role,
    target_before_copy='ABSENT',status='ORIGINAL_UNTRACKED_VISUALIZATION_SOURCE'))
 write_json(OUT/'visualization_transfer_original.json',dict(files=transfer,donor_worktree=str(donor),
   donor_branch='research/aminoacylation-qssa-pilot-v0',donor_HEAD='24335fe798e757acb2ca3582916658bfcf5c16f5'))
 objects=[]
 import numpy as np
 for name in CONDITIONS:
  r=FirstOrderCK(name)
  p=ROOT/'results/reduction/r7_ck_first_order/per_condition'/name/'run_001/comparison.npz'
  with np.load(p) as a:
   t=a['times'];assert float(a['switch'])==r.switch and t[0]==0 and t[-1]==1000
   assert 0<r.switch<.001<.05<1000
   assert [r.channel_ids[c] for c in r.fast_channels]==['re0000000332_MINUS_re0000000333','re0000000336_MINUS_re0000000337']
   objects.append(dict(condition=name,switch_s=r.switch,end_s=float(t[-1]),boundaries_s=[0,r.switch,.001,.05,float(t[-1])],
    comparison_path=p.relative_to(ROOT).as_posix(),comparison_sha256=sha(p),
    CK_indices=r.fast_channels,CK_pairs=[r.channel_ids[c] for c in r.fast_channels],
    sample_count=len(t),exact_boundary_storage={str(v):bool(np.any(t==v)) for v in [.001,.05]}))
 binding_paths=['docs/reduction/r8_ck_startup_layer_preregistration.md',
 'scripts/register_r8_ck_startup_layer_v1.py','scripts/run_r8_ck_startup_layer_v1.py',
 'scripts/verify_r8_ck_startup_layer_v1.py','results/reduction/r8_ck_startup_layer/pre_r8_snapshot.json',
 'results/reduction/r8_ck_startup_layer/visualization_transfer_original.json']
 write_json(OUT/'registration.json',dict(schema='R8_CK_STARTUP_LAYER_REGISTRATION_V1',
  parent_branch='codex/r7-ck-first-order-20261008',parent_SHA=PARENT,branch=BRANCH,starting_SHA=git('rev-parse','HEAD'),
  R7_found_worktree=str(ROOT),R8_worktree=str(ROOT),origin_main_start=git('rev-parse','origin/main'),
  worktrees_at_recovery=git('worktree','list','--porcelain'),conditions=CONDITIONS,objects=objects,
  input_binding='EVERY_PRE_R8_TRACKED_FILE_SNAPSHOT_BOUND',file_hashes={p:sha(ROOT/p) for p in binding_paths},
  no_new_trajectory_solve=True,promotion=False,PURE_reduced_core='NOT_VALIDATED'))
 print('R8 frozen:',len(snapshot),'historical files; three lossless visualization transfers')

if __name__=='__main__':main()
