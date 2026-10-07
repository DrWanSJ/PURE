"""Attribution of frozen signed cumulative residuals; zero trajectory solves."""
from pathlib import Path
import json, math
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from r7_ck_h1_v1 import ROOT, CONDITIONS, FirstOrderCK, sha, load, write_json, write_csv
from r6_ck_common_v1 import rows

OUT=ROOT/'results/reduction/r8_ck_startup_layer'
R7=ROOT/'results/reduction/r7_ck_first_order'
MODELS={'zero':'ZERO_ORDER_R6','formal':'FORMAL_FIRST_ORDER_SELF_CONSISTENT'}

def check_binding():
 b=load(OUT/'registration.json')
 for p,h in b['file_hashes'].items():assert sha(ROOT/p)==h,'REGISTRATION_MUTATION:'+p
 for p,h in load(OUT/'pre_r8_snapshot.json')['files'].items():assert sha(ROOT/p)==h,'HISTORICAL_MUTATION:'+p
 return b

def scalar(t,y,dy,v,switch):
 if v<=switch:return 0.
 mask=t>=switch
 return float(CubicHermiteSpline(t[mask],y[mask],dy[mask])(v))

def node_or_linear(t,y,v):return float(np.interp(v,t,y))

def bracket(t,v):
 if np.any(t==v):return [float(v),float(v)]
 k=int(np.searchsorted(t,v));return [float(t[k-1]),float(t[k])]

def sufficient_decision(summaries):
 formal=[s for s in summaries if s['model']==MODELS['formal'] and s['condition'] in ['R3_BASE','R3_TRNA_LOW']]
 assert len(formal)==4
 unresolved=[s for s in formal if s['R7_F_status']=='RESOLVED_FAIL']
 assert {s['condition'] for s in unresolved}=={'R3_BASE','R3_TRNA_LOW'}
 if all(abs(s['after_1ms_scaled'])-s['after_1ms_uncertainty_scaled']>
        abs(s['by_1ms_scaled'])+s['by_1ms_uncertainty_scaled'] for s in unresolved):
  return 'CK_STARTUP_LAYER_ATTRIBUTION_NOT_SUPPORTED'
 return 'CK_STARTUP_LAYER_ATTRIBUTION_INCONCLUSIVE'

def main():
 registration=check_binding();intervals=[];boundaries=[];local=[];fast=[];summaries=[]
 for obj in registration['objects']:
  name=obj['condition'];r=FirstOrderCK(name)
  with np.load(ROOT/obj['comparison_path']) as f:a={k:f[k].copy() for k in f.files}
  t=a['times'];switch=float(a['switch']);bs=obj['boundaries_s'];scores=rows(R7/'per_condition'/name/'run_001/observable_scores.csv')
  assert switch==r.switch
  for ch,pair in zip(obj['CK_indices'],obj['CK_pairs']):
   for key,model in MODELS.items():
    source=a['source_extent'][:,ch];candidate=a[key+'_extent'][:,ch]
    residual=source-candidate;current=a['source_net'][:,ch]-a[key+'_net'][:,ch]
    probe=a['source_extent_probe'][:,ch]-a[key+'_extent_probe'][:,ch]
    probe_current=a['source_net_probe'][:,ch]-a[key+'_net_probe'][:,ch]
    vals=[scalar(t,residual,current,v,switch) for v in bs]
    pvals=[scalar(t,probe,probe_current,v,switch) for v in bs]
    endpoint_unc=[]
    for v,y,py in zip(bs,vals,pvals):
     interpolation=abs(y-node_or_linear(t,residual,v)) if v>switch else 0.
     tight=abs(node_or_linear(t,a[key+'_tight_extent'][:,ch]-candidate,v))
     fw,rv=r.channels[ch]
     cancel=8*np.finfo(float).eps*node_or_linear(t,abs(a['source_gross_extent'][:,fw])+abs(a['source_gross_extent'][:,rv]),v)
     unc=abs(y-py)+tight+cancel+interpolation;endpoint_unc.append(unc)
     boundaries.append(dict(condition=name,pair=pair,model=model,time_s=v,signed_cumulative_residual=y,
       primary_probe_difference=abs(y-py),tight_quadrature_allowance=tight,cancellation_allowance=cancel,
       interpolation_disagreement=interpolation,total_uncertainty=unc,storage_bracket_s=json.dumps(bracket(t,v)),
       method='SHARED_SOURCE_STARTUP' if v<=switch else 'FROZEN_LEDGER_CUBIC_HERMITE'))
    for window in ['FULL_WINDOW','POST_INITIAL_LAYER']:
     frow=next(s for s in scores if s['model']==model and s['category']=='NET_EXTENT' and s['window']==window and s['observable']==pair)
     drow=next(s for s in scores if s['model']==model and s['category']=='NET_CURRENT' and s['window']==window and s['observable']==pair)
     scale=float(frow['reference_scale']);U=float(frow['uncertainty'])*scale
     roundoff=64*np.finfo(float).eps*max(1.,np.max(abs(source)),np.max(abs(candidate)))
     tolerance=U+2*sum(endpoint_unc)+roundoff
     labels=['ZERO_TO_SWITCH','SWITCH_TO_1MS','1MS_TO_0P05','0P05_TO_FORMAL_END']
     for k,label in enumerate(labels):
      signed=vals[k+1]-vals[k];u=endpoint_unc[k]+endpoint_unc[k+1]
      intervals.append(dict(condition=name,pair=pair,model=model,window=window,interval=label,
        start_s=bs[k],end_s=bs[k+1],signed_extent=signed,absolute_signed_extent=abs(signed),
        F_reference_scale=scale,F_floor=float(frow['floor']),signed_scaled=signed/scale,
        fraction_terminal_signed_residual=signed/vals[-1] if vals[-1] else 0.,
        uncertainty=u,uncertainty_scaled=u/scale,R7_F_uncertainty_scaled=float(frow['uncertainty']),
        additive_tolerance=tolerance,label='SIGNED_EXTENT_ATTRIBUTION_DIAGNOSTIC'))
     total=sum(vals[k+1]-vals[k] for k in range(4))
     assert abs(total-vals[-1])<=tolerance
     mask=t>= (0 if window=='FULL_WINDOW' else switch)
     k=int(np.flatnonzero(mask)[np.argmax(abs(residual[mask]))])
     summaries.append(dict(condition=name,pair=pair,model=model,window=window,switch_s=switch,formal_end_s=bs[-1],
       F_reference_scale=scale,R7_F_E_inf=float(frow['E_inf']),R7_F_status=frow['status'],
       R7_F_uncertainty_scaled=float(frow['uncertainty']),R7_F_worst_time_s=float(t[k]),
       by_switch_scaled=vals[1]/scale,by_1ms_scaled=vals[2]/scale,by_0p05_scaled=vals[3]/scale,
       after_1ms_scaled=(vals[-1]-vals[2])/scale,after_0p05_scaled=(vals[-1]-vals[3])/scale,
       terminal_signed_scaled=vals[-1]/scale,terminal_signed_extent=vals[-1],
       by_1ms_uncertainty_scaled=(endpoint_unc[0]+endpoint_unc[2]+U)/scale,
       after_1ms_uncertainty_scaled=(endpoint_unc[-1]+endpoint_unc[2]+U)/scale,
       after_0p05_uncertainty_scaled=(endpoint_unc[-1]+endpoint_unc[3]+U)/scale,
       additive_reconstruction_error=abs(total-vals[-1]),additive_tolerance=tolerance,
       R7_D_E_inf=float(drow['E_inf']),R7_D_status=drow['status'],promotion=False,PURE_reduced_core='NOT_VALIDATED'))
    for label,start in [('FULL_WINDOW',0.),('POST_INITIAL_LAYER',switch),('AFTER_1MS',.001),('AFTER_0P05',.05)]:
     mask=t>=start;times=np.unique(np.r_[start,t[mask]])
     src=np.interp(times,t,a['source_net'][:,ch]);zero=np.interp(times,t,a['zero_net'][:,ch]);formal=np.interp(times,t,a['formal_net'][:,ch])
     cand=zero if key=='zero' else formal;err=src-cand;i=int(np.argmax(abs(err)));tt=float(times[i])
     fullscale=max(np.max(abs(a['source_net'][:,ch])),1e-9);postscale=max(np.max(abs(a['source_net'][t>=switch,ch])),1e-9)
     local.append(dict(condition=name,pair=pair,model=model,diagnostic_interval=label,start_s=start,end_s=float(t[-1]),
       maximum_absolute_current_discrepancy=float(abs(err[i])),signed_residual_at_max=float(err[i]),time_of_max_s=tt,
       source_current=float(src[i]),R6_current=float(zero[i]),formal_current=float(formal[i]),
       D_full_reference_scale=float(fullscale),D_post_reference_scale=float(postscale),D_floor=1e-9,
       equals_fixed_switch=tt==switch,before_1ms=tt<.001,before_0p05=tt<.05,
       maximum_definition='FROZEN_R7_SCORING_GRID_PLUS_EXACT_BOUNDARY_LINEAR_INTERPOLATION'))
  # Descriptive exact-boundary graph distances from frozen source samples.
  derivatives=np.array([r.S@r.rates(x) for x in a['source']])
  probe_derivatives=np.array([r.S@r.rates(x) for x in a['source_probe']])
  curve=CubicHermiteSpline(t,a['source'],derivatives);pcurve=CubicHermiteSpline(t,a['source_probe'],probe_derivatives)
  for v in [switch,.001,.05]:
   x=curve(v);px=pcurve(v);lx=np.array([np.interp(v,t,a['source'][:,j]) for j in range(241)])
   def distance(xx):
    c=r.core(r.T@xx-r.z0);return xx[r.qix]-(c['q']+c['h1']),c
   delta,c=distance(x);pd,_=distance(px);ld,_=distance(lx);singular=np.linalg.svd(c['J'],compute_uv=False)
   expected=c['q']+c['h1'];vector_scale=max(float(np.linalg.norm(expected)),1e-6)
   fast.append(dict(condition=name,time_s=v,coordinate_convention='R7_CANONICAL_T_SOURCE_ETA_1',
     delta_q_CP=float(delta[0]),delta_q_CP_ADP=float(delta[1]),delta_q_norm=float(np.linalg.norm(delta)),
     state_floor=1e-6,vector_state_scale=vector_scale,relative_norm=float(np.linalg.norm(delta))/vector_scale,
     relative_CP=float(delta[0]/max(abs(expected[0]),1e-6)),relative_CP_ADP=float(delta[1]/max(abs(expected[1]),1e-6)),
     singular_value_max=float(singular[0]),singular_value_min=float(singular[-1]),condition_number=float(singular[0]/singular[-1]),
     primary_probe_distance_norm=float(np.linalg.norm(delta-pd)),interpolation_distance_disagreement_norm=float(np.linalg.norm(delta-ld)),
     storage_bracket_s=json.dumps(bracket(t,v)),label='FAST_STATE_DISTANCE_DESCRIPTIVE_NO_SOURCE_PROJECTION'))
  print(name,'frozen evidence attribution complete',flush=True)
 recommendation=sufficient_decision([s for s in summaries if s['window']=='FULL_WINDOW'])
 next_step={'CK_STARTUP_LAYER_ATTRIBUTION_NOT_SUPPORTED':'INVESTIGATE_SUSTAINED_OUTER_TRUNCATION_OR_MECHANISM_ERROR_BEFORE_MATCHING',
 'CK_STARTUP_LAYER_ATTRIBUTION_SUPPORTED':'TEST_MATCHED_INITIAL_LAYER_BEFORE_HIGHER_OUTER_ORDER',
 'CK_STARTUP_LAYER_ATTRIBUTION_INCONCLUSIVE':'NO_SCIENTIFIC_ADVANCEMENT'}[recommendation]
 for filename,data in [('extent_interval_decomposition.csv',intervals),('boundary_values.csv',boundaries),
   ('current_time_localization.csv',local),('fast_state_distance.csv',fast),('condition_summary.csv',summaries)]:write_csv(OUT/filename,data)
 decision=dict(recommendation=recommendation,next_step=next_step,promotion=False,PURE_reduced_core='NOT_VALIDATED',
  conditions=CONDITIONS,new_state_solves=0,new_extent_ODE_solves=0,matched_layer_implemented=False,h2_implemented=False,
  R7_recommendation='CK_FIRST_ORDER_IMPROVES_EXTENT_NOT_CURRENT',R7_scores_unchanged=True,
  E_G_status='DESCRIPTIVE_BUT_NOT_VALIDATED',mechanistic_decisions='968_PENDING',
  uncertainty_status='PRIMARY_PROBE_AND_R7_QUADRATURE_CANCELLATION_PLUS_DESCRIPTIVE_INTERPOLATION_ENVELOPE',
  optional_linear_check='SKIPPED_NO_NATIVE_DENSE_POST_SWITCH_SOURCE_FAST_TAIL',
  limitation='Fixed-time interpolation is not a rigorous continuous-source bound; maxima are frozen-grid diagnostics.')
 write_json(OUT/'decision.json',decision)
 write_json(OUT/'evidence_navigation.json',dict(schema='R8_DERIVED_NAVIGATION_V1',authority='SUBORDINATE_TO_FROZEN_R7_AND_R8_EVIDENCE',
  nodes=[dict(id='R7',status='EXTRACTED',source='results/reduction/r7_ck_first_order/verification.json',sha256=sha(R7/'verification.json')),
    dict(id='R8_INTERVALS',status='EXTRACTED',source='results/reduction/r8_ck_startup_layer/extent_interval_decomposition.csv',sha256=sha(OUT/'extent_interval_decomposition.csv')),
    dict(id='R8_ATTRIBUTION',status='INFERRED',source='results/reduction/r8_ck_startup_layer/decision.json',sha256=sha(OUT/'decision.json')),
    dict(id='CONTINUOUS_SUBGRID_SOURCE',status='AMBIGUOUS',reason='No native dense post-switch source artifact')],
  edges=[dict(source='R7',target='R8_INTERVALS',relationship='FROZEN_INPUT'),dict(source='R8_INTERVALS',target='R8_ATTRIBUTION',relationship='BOUNDED_INFERENCE')],
  confidence='BOUNDED_BY_REPORTED_NUMERICAL_AND_INTERPOLATION_UNCERTAINTY',freshness='HASH_CHECK_EACH_REFERENCED_SOURCE'))
 summary=['# R8 CK startup-layer attribution summary','',f'**{recommendation}**','',
  'Attribution only; original R7 failures remain. promotion=false; PURE_reduced_core=NOT_VALIDATED.',
  'Exactly BASE, ATP_LOW, TRNA_LOW. No state or extent ODE solve, matching layer, h2 or aminoacylation work.',
  '', 'Signed scaled contributions use the unchanged R7 FULL_WINDOW F scale:', '',
  '| Condition / pair / model | by switch | by 1 ms | by 0.05 s | after 1 ms | after 0.05 s | terminal | R7 F supremum |',
  '|---|---:|---:|---:|---:|---:|---:|---:|']
 for s in summaries:
  if s['window']=='FULL_WINDOW':summary.append('| '+s['condition']+' / '+s['pair']+' / '+s['model']+' | '+' | '.join(f"{s[k]:.12g}" for k in ['by_switch_scaled','by_1ms_scaled','by_0p05_scaled','after_1ms_scaled','after_0p05_scaled','terminal_signed_scaled','R7_F_E_inf'])+' |')
 summary+=['','The cumulative startup difference through switch is exactly zero: the inherited candidates share source startup integrals. This does not assert that the physical initial layer is absent.',
  'A short real switch current tail and sustained cumulative extent error must be distinguished. Signed later increments, opposite-sign cancellation and each pair remain explicit in the CSVs.',
  'Fixed-time interpolation uses frozen cumulative ledgers and currents. No dense post-switch source is available. Primary/probe, original tighter quadrature, cancellation, and Hermite/linear disagreement are reported; the latter is descriptive, not a rigorous interpolation bound.',
  'F scores are original supremum scores, not terminal residuals. Current maxima use the original scoring grid plus the exact lower boundary. No registered metric is replaced.',
  f'Permitted next recommendation: **{next_step}**. No implementation follows.',
  'Fast graph distance is descriptive and includes interpolation disagreement; see fast_state_distance.csv. Optional linear-fast-mode check skipped because native dense post-switch source is absent.',
  'Independent verification is recorded separately. Every pre-R8 tracked file and Desktop donor is hash-bound. Derived navigation is subordinate to canonical artifacts.',
  'E/G remain DESCRIPTIVE / BUT_NOT_VALIDATED; all 968 mechanistic decisions remain PENDING.']
 p=ROOT/'docs/reduction/r8_ck_startup_layer_summary.md';p.write_text('\n'.join(summary)+'\n',encoding='utf-8',newline='\n')
 paths=[p]+[v for v in OUT.iterdir() if v.is_file() and v.name not in ['manifest.json','verification.json']]
 write_json(OUT/'manifest.json',dict(schema='R8_CK_STARTUP_LAYER_MANIFEST_V1',registration_sha256=sha(OUT/'registration.json'),
  parent_SHA=registration['parent_SHA'],branch=registration['branch'],recommendation=recommendation,promotion=False,
  files={p.relative_to(ROOT).as_posix():sha(p) for p in paths},historical_snapshot_sha256=sha(OUT/'pre_r8_snapshot.json')))
 print(recommendation,flush=True)

if __name__=='__main__':main()
