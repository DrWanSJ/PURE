"""Independent frozen-input reconstruction; no producer import or model solve."""
from pathlib import Path
import argparse, ast, json, math, subprocess, traceback
import numpy as np
from numpy.polynomial.legendre import leggauss
from r7_ck_h1_v1 import ROOT, FirstOrderCK, sha, load, write_json
from r6_ck_common_v1 import rows
from verify_r7_ck_first_order_v1 import independent_graph

OUT=ROOT/'results/reduction/r8_ck_startup_layer'
R7=ROOT/'results/reduction/r7_ck_first_order'
NAMES=['R3_BASE','R3_ATP_LOW','R3_TRNA_LOW']
MODELS={'ZERO_ORDER_R6':'zero','FORMAL_FIRST_ORDER_SELF_CONSISTENT':'formal'}

def polynomial(t,y,d,v,switch=None):
 if switch is not None and v<=switch:return np.zeros_like(y[0])
 if np.any(t==v):return y[int(np.flatnonzero(t==v)[0])]
 k=int(np.searchsorted(t,v))-1;h=t[k+1]-t[k];s=(v-t[k])/h
 return (2*s**3-3*s**2+1)*y[k]+(s**3-2*s**2+s)*h*d[k]+(-2*s**3+3*s**2)*y[k+1]+(s**3-s**2)*h*d[k+1]

def integral(t,y,d,a,b,switch):
 total=0.;gx,gw=leggauss(3)
 cuts=np.unique(np.r_[a,t[(t>a)&(t<b)],b])
 for left,right in zip(cuts[:-1],cuts[1:]):
  if right<=switch:continue
  mid=(left+right)/2;k=int(np.searchsorted(t,mid))-1;h=t[k+1]-t[k]
  ts=(left+right)/2+(right-left)/2*gx;s=(ts-t[k])/h
  derivative=(6*s*s-6*s)/h*y[k]+(3*s*s-4*s+1)*d[k]+(-6*s*s+6*s)/h*y[k+1]+(3*s*s-2*s)*d[k+1]
  total+=float(np.dot(gw,derivative)*(right-left)/2)
 return total

def close(a,b,tol=1e-11):
 assert np.isclose(float(a),float(b),rtol=tol,atol=tol),f'NUMERICAL_MISMATCH:{a}:{b}'

def verify(with_r7=False):
 checks=[];reg=load(OUT/'registration.json');snap=load(OUT/'pre_r8_snapshot.json')
 git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
 assert reg['parent_SHA']==reg['starting_SHA']=='20ca5215d949c9451b3e6fd4435c18991783ac29'
 assert git('branch','--show-current')==reg['branch']=='codex/r8-ck-startup-layer-20261008'
 assert subprocess.run(['git','merge-base','--is-ancestor',reg['parent_SHA'],'HEAD'],cwd=ROOT).returncode==0
 for p,h in snap['files'].items():assert sha(ROOT/p)==h,'HISTORICAL_BYTE_MUTATION:'+p
 for p,h in reg['file_hashes'].items():assert sha(ROOT/p)==h,'REGISTRATION_MUTATION:'+p
 manifest=load(OUT/'manifest.json')
 for p,h in manifest['files'].items():assert sha(ROOT/p)==h,'MANIFEST_MUTATION:'+p
 transfer=load(OUT/'visualization_transfer_original.json')
 for v in transfer['files']:
  assert sha(v['source_absolute_path'])==v['original_sha256']==v['initial_copied_sha256'],'DONOR_MUTATION'
 assert len(transfer['files'])==3
 assert reg['conditions']==NAMES and [o['condition'] for o in reg['objects']]==NAMES
 checks.append(dict(check='HASH_LINEAGE_ALL_HISTORICAL_BYTES_AND_THREE_READ_ONLY_DONORS',status='PASS',historical_file_count=len(snap['files'])))
 table=rows(OUT/'extent_interval_decomposition.csv');summary=rows(OUT/'condition_summary.csv');bv=rows(OUT/'boundary_values.csv');loc=rows(OUT/'current_time_localization.csv');fs=rows(OUT/'fast_state_distance.csv')
 assert len(table)==96 and len(summary)==24 and len(bv)==60 and len(loc)==48 and len(fs)==9
 assert {v['condition'] for v in table}==set(NAMES)
 max_quad=0.;max_fast=0.;resolved_late=[]
 for obj in reg['objects']:
  name=obj['condition'];r=FirstOrderCK(name)
  with np.load(ROOT/obj['comparison_path']) as f:a={k:f[k].copy() for k in f.files}
  t=a['times'];switch=float(a['switch']);bs=obj['boundaries_s']
  assert bs==[0,switch,.001,.05,1000.] and switch==r.switch and t[-1]==1000
  assert [r.channel_ids[i] for i in obj['CK_indices']]==obj['CK_pairs']
  assert obj['CK_pairs']==['re0000000332_MINUS_re0000000333','re0000000336_MINUS_re0000000337']
  original=rows(R7/'per_condition'/name/'run_001/observable_scores.csv')
  for ch,pair in zip(obj['CK_indices'],obj['CK_pairs']):
   for model,key in MODELS.items():
    y=a['source_extent'][:,ch]-a[key+'_extent'][:,ch]
    d=a['source_net'][:,ch]-a[key+'_net'][:,ch]
    py=a['source_extent_probe'][:,ch]-a[key+'_extent_probe'][:,ch]
    pd=a['source_net_probe'][:,ch]-a[key+'_net_probe'][:,ch]
    assert np.all(y[t<=switch]==0.)
    values=[float(polynomial(t,y,d,v,switch)) for v in bs]
    boundary_unc=[]
    for v in bs:
     row=next(b for b in bv if b['condition']==name and b['pair']==pair and b['model']==model and float(b['time_s'])==v)
     expected=float(polynomial(t,y,d,v,switch));p=float(polynomial(t,py,pd,v,switch))
     close(row['signed_cumulative_residual'],expected)
     f,b=r.channels[ch];c=8*np.finfo(float).eps*np.interp(v,t,abs(a['source_gross_extent'][:,f])+abs(a['source_gross_extent'][:,b]))
     tight=abs(np.interp(v,t,a[key+'_tight_extent'][:,ch]-a[key+'_extent'][:,ch]))
     inter=abs(expected-np.interp(v,t,y)) if v>switch else 0.
     u=abs(expected-p)+tight+c+inter;close(row['total_uncertainty'],u);close(row['interpolation_disagreement'],inter);boundary_unc.append(u)
    for window,start in [('FULL_WINDOW',0.),('POST_INITIAL_LAYER',switch)]:
     original_row=next(v for v in original if v['observable']==pair and v['model']==model and v['category']=='NET_EXTENT' and v['window']==window)
     scale=max(np.max(abs(a['source_extent'][t>=start,ch])),1e-6)
     close(original_row['reference_scale'],scale)
     score=np.max(abs(y[t>=start]))/scale;close(original_row['E_inf'],score)
     s=next(v for v in summary if v['condition']==name and v['pair']==pair and v['model']==model and v['window']==window)
     close(s['R7_F_E_inf'],score);assert s['R7_F_status']==original_row['status']
     U=float(original_row['uncertainty'])*scale
     roundoff=64*np.finfo(float).eps*max(1.,np.max(abs(a['source_extent'][:,ch])),np.max(abs(a[key+'_extent'][:,ch])))
     tolerance=U+2*sum(boundary_unc)+roundoff;close(s['additive_tolerance'],tolerance)
     selected=[v for v in table if v['condition']==name and v['pair']==pair and v['model']==model and v['window']==window]
     for k,v in enumerate(selected):
      assert float(v['start_s'])==bs[k] and float(v['end_s'])==bs[k+1]
      expected=values[k+1]-values[k];close(v['signed_extent'],expected);close(v['absolute_signed_extent'],abs(expected));close(v['signed_scaled'],expected/scale)
      close(v['F_reference_scale'],scale);assert float(v['F_floor'])==1e-6
      close(v['uncertainty'],boundary_unc[k]+boundary_unc[k+1])
      q=integral(t,y,d,bs[k],bs[k+1],switch);error=abs(q-expected);max_quad=max(max_quad,error)
      assert error<=tolerance,'INDEPENDENT_QUADRATURE_RECONSTRUCTION'
     assert abs(math.fsum(float(v['signed_extent']) for v in selected)-values[-1])<=tolerance
     for field,index in [('by_switch_scaled',1),('by_1ms_scaled',2),('by_0p05_scaled',3)]:close(s[field],values[index]/scale)
     close(s['terminal_signed_scaled'],values[-1]/scale);close(s['after_1ms_scaled'],(values[-1]-values[2])/scale);close(s['after_0p05_scaled'],(values[-1]-values[3])/scale)
     earlyu=(boundary_unc[0]+boundary_unc[2]+U)/scale;lateu=(boundary_unc[-1]+boundary_unc[2]+U)/scale
     close(s['by_1ms_uncertainty_scaled'],earlyu);close(s['after_1ms_uncertainty_scaled'],lateu)
     if window=='FULL_WINDOW' and model=='FORMAL_FIRST_ORDER_SELF_CONSISTENT' and original_row['status']=='RESOLVED_FAIL' and name in ['R3_BASE','R3_TRNA_LOW']:
      resolved_late.append((name,abs((values[-1]-values[2])/scale)-lateu>abs(values[2]/scale)+earlyu))
    for label,start in [('FULL_WINDOW',0.),('POST_INITIAL_LAYER',switch),('AFTER_1MS',.001),('AFTER_0P05',.05)]:
     v=next(x for x in loc if x['condition']==name and x['pair']==pair and x['model']==model and x['diagnostic_interval']==label)
     tt=np.unique(np.r_[start,t[t>=start]]);src=np.interp(tt,t,a['source_net'][:,ch]);zero=np.interp(tt,t,a['zero_net'][:,ch]);formal=np.interp(tt,t,a['formal_net'][:,ch]);diff=src-(zero if key=='zero' else formal);k=int(np.argmax(abs(diff)))
     close(v['maximum_absolute_current_discrepancy'],abs(diff[k]));close(v['time_of_max_s'],tt[k]);close(v['source_current'],src[k]);close(v['R6_current'],zero[k]);close(v['formal_current'],formal[k])
     close(v['D_full_reference_scale'],max(np.max(abs(a['source_net'][:,ch])),1e-9));close(v['D_post_reference_scale'],max(np.max(abs(a['source_net'][t>=switch,ch])),1e-9))
     assert (v['equals_fixed_switch']=='True')==(tt[k]==switch)
  derivatives=np.array([r.S@r.rates(x) for x in a['source']])
  for v in [switch,.001,.05]:
   x=polynomial(t,a['source'],derivatives,v);_,q,H,F,G,J,h1,_=independent_graph(r,r.T@x-r.z0)
   delta=x[r.qix]-(q+h1);singular=np.linalg.svd(J,compute_uv=False)
   row=next(s for s in fs if s['condition']==name and float(s['time_s'])==v)
   error=np.linalg.norm(delta-np.array([float(row['delta_q_CP']),float(row['delta_q_CP_ADP'])]));max_fast=max(max_fast,float(error));assert error<1e-8
   close(row['singular_value_min'],singular[-1]);close(row['condition_number'],singular[0]/singular[-1]);assert float(row['state_floor'])==1e-6
 checks.append(dict(check='FIXED_TIMES_PAIRS_SIGNED_RESIDUAL_INTEGRAL_ADDITIVITY_ORIGINAL_F_D_SCALES_AND_UNCERTAINTY',status='PASS',max_independent_quadrature_difference=max_quad,max_independent_fast_graph_difference=max_fast))
 decision=load(OUT/'decision.json')
 assert {x[0] for x in resolved_late}=={'R3_BASE','R3_TRNA_LOW'}
 expected='CK_STARTUP_LAYER_ATTRIBUTION_NOT_SUPPORTED' if all(x[1] for x in resolved_late) else 'CK_STARTUP_LAYER_ATTRIBUTION_INCONCLUSIVE'
 assert decision['recommendation']==expected==manifest['recommendation']
 assert decision['promotion'] is False and decision['PURE_reduced_core']=='NOT_VALIDATED'
 assert decision['new_state_solves']==decision['new_extent_ODE_solves']==0
 assert decision['matched_layer_implemented'] is decision['h2_implemented'] is False
 source=(ROOT/'scripts/run_r8_ck_startup_layer_v1.py').read_text(encoding='utf-8')
 tree=ast.parse(source)
 forbidden={'solve_ivp','BDF','state_solve','extent_solve','odeint','reduced_rhs_delta','reduced_jac_delta'}
 for node in ast.walk(tree):
  if isinstance(node,ast.Call):
   fname=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
   assert fname not in forbidden,'NEW_SOLVER_CALL:'+fname
 checks.append(dict(check='BOUNDED_ATTRIBUTION_DECISION_NO_PROMOTION_NO_NEW_MODEL_OR_TRAJECTORY_SOLVE',status='PASS',recommendation=expected))
 if with_r7:
  import verify_r7_ck_first_order_v1 as frozen
  frozen.Path=Path
  def redirected(path,data):
   assert Path(path)==R7/'verification.json'
   write_json(OUT/'r7_read_only_reverification.json',dict(entry='ADDITIVE_OUTPUT_REDIRECTION_ONLY',frozen_body_sha256=sha(ROOT/'scripts/verify_r7_ck_first_order_v1.py'),receipt=data))
  frozen.write_json=redirected
  frozen.verify()
  for p,h in snap['files'].items():assert sha(ROOT/p)==h,'R7_REVERIFIER_MUTATED_HISTORY:'+p
  checks.append(dict(check='EXISTING_R7_VERIFIER_UNCHANGED_BODY_READ_ONLY_OUTPUT_REDIRECTION',status='PASS'))
 write_json(OUT/'verification.json',dict(schema='R8_INDEPENDENT_VERIFICATION_V1',status='PASS_ENGINEERING_AND_EVIDENCE_ONLY',
  checks=checks,recommendation=expected,promotion=False,PURE_reduced_core='NOT_VALIDATED',manifest_sha256=sha(OUT/'manifest.json'),
  verifier_sha256=sha(Path(__file__)),uncertainty_limitation='No rigorous continuous-time interpolation bound; attribution uses frozen ledgers and stated envelopes.'))
 print('R8 independent verifier PASS:',expected,flush=True)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--with-r7',action='store_true');args=parser.parse_args()
 try:verify(args.with_r7)
 except Exception:
  n=1
  while (OUT/f'verification_failure_{n:03d}.json').exists():n+=1
  write_json(OUT/f'verification_failure_{n:03d}.json',dict(status='FAIL',traceback=traceback.format_exc(),scientific_equations_changed=False))
  raise

if __name__=='__main__':main()
