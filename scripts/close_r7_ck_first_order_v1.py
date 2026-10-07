"""Add measured boundary interpretation and bind final report without refreezing."""
from r7_ck_h1_v1 import *
from r6_ck_common_v1 import rows
from pathlib import Path
import subprocess

def main():
    checked_binding()
    component_scales=[]
    for row in rows(OUT/'h1_samples.csv'):
        for species,key in [('CK_CP','CP'),('CK_CP_ADP','CP_ADP')]:
            h0=float(row['h0_'+key]);h1=float(row['h1_'+key])
            component_scales.append(dict(condition=row['condition'],sample_index=row['sample_index'],time_s=row['time_s'],species=species,h0=h0,h1=h1,
                frozen_state_floor=1e-6,individual_state_scale=max(abs(h0),1e-6),correction_over_individual_state_scale=abs(h1)/max(abs(h0),1e-6),status='DESCRIPTIVE_NO_NEW_GATE'))
    write_csv(OUT/'h1_component_scale_diagnostics.csv',component_scales)
    decision=load(OUT/'advancement_decision.json');boundary=load(OUT/'boundary_interpretation.json')
    trajectory_scales=[];physical_scales=[]
    for name in CONDITIONS:
        r=FirstOrderCK(name);dest=OUT/'per_condition'/name/'run_001'
        if load(dest/'result.json')['status']!='COMPLETED':continue
        with np.load(dest/'comparison.npz') as f:a={k:f[k].copy() for k in f.files}
        for k,t in enumerate(a['times']):
            c=r.core(r.T@a['source'][k]-r.z0)
            for index in r.ix:
                physical_scales.append(dict(condition=name,model='SOURCE_SLOW_COORDINATES',time_s=float(t),species=r.source.species[index],
                    h0_state=float(c['x'][index]),first_order_state_change=float(c['e'][index]),frozen_state_floor=1e-6,
                    relative_correction=abs(float(c['e'][index]))/max(abs(float(c['x'][index])),1e-6),applied_by_candidate=bool(t>=r.switch),status='DESCRIPTIVE_NO_NEW_GATE'))
        for model in ['post','formal']:
            for k in np.flatnonzero(a['times']>=r.switch):
                c=r.core(a[model+'_slow'][k]-r.z0);x=c['x']+c['e'];n=float(np.linalg.norm(c['h1']))
                for index in r.ix:
                    physical_scales.append(dict(condition=name,model=model,time_s=float(a['times'][k]),species=r.source.species[index],
                        h0_state=float(c['x'][index]),first_order_state_change=float(c['e'][index]),frozen_state_floor=1e-6,
                        relative_correction=abs(float(c['e'][index]))/max(abs(float(c['x'][index])),1e-6),applied_by_candidate=True,status='DESCRIPTIVE_NO_NEW_GATE'))
                trajectory_scales.append(dict(condition=name,model=model,time_s=float(a['times'][k]),
                    correction_norm=n,correction_over_fast_state=n/max(float(np.linalg.norm(c['q'])),1e-6),
                    correction_over_fast_total=n/max(float(np.linalg.norm(c['z'][:3])),1e-6),
                    min_physical_margin=float(x[r.ix].min()),distance_outside_domain=float(max(0,-x[r.ix].min())),
                    Gq_condition=float(np.linalg.cond(c['J'])),Gq_min_singular=float(np.linalg.svd(c['J'],compute_uv=False)[-1]),
                    status='DESCRIPTIVE_NO_NEW_GATE'))
    if trajectory_scales:write_csv(OUT/'first_order_trajectory_scale_diagnostics.csv',trajectory_scales)
    if physical_scales:write_csv(OUT/'physical_fast_state_correction_scales.csv',physical_scales)
    b=boundary['ATP_LOW']
    report=ROOT/'docs/reduction/r7_ck_first_order_summary.md'
    text=report.read_text(encoding='utf-8')
    text+='\n## Signed startup-tail interpretation\n\n'
    text+=(f"The ATP_LOW 99.3% R6 post-layer peak is **a real short-lived boundary-current discrepancy, not a floor or zero-crossing artifact**. "
        f"The worst point is the fixed switch at {b['worst_time_s']:.12g} s. Source current is {b['source_current_at_switch']:.12g}, R6 current {b['R6_current_at_switch']:.12g}, "
        f"and the first-order current at identical switch slow coordinates is {b['formal_current_at_identical_slow_switch']:.12g} concentration/s. "
        f"Its post-layer scale is {b['post_source_scale']:.12g}, far above the 1e-9 floor; the source is nonzero at the worst point. "
        f"The full-window source scale is {b['full_source_scale']:.12g}, {b['full_to_post_denominator_ratio']:.12g} times larger. "
        f"Thus removing the initial burst changes the relative normalization substantially, but does not create the absolute discrepancy. "
        f"By the first stored point at/after 1 ms, the source-minus-R6 startup-tail cumulative contribution is "
        f"{b['source_early_tail_extent']-b['R6_early_tail_extent']:.12g} concentration units. "
        f"After 0.05 s the R6 CP-pair maximum absolute discrepancy is {b['post_0p05_max_abs_error']:.12g} concentration/s. "
        "The signed source fast-state distance from the first-order graph and its amplification by Gq are retained in boundary_current_diagnostics.csv. "
        "These observations support residual startup fast motion at the frozen switch. exp(-10) is a descriptive linear-mode reference, never a fitted law. "
        "No startup retuning, extra matching layer, time shift or source projection was performed.\n")
    text+='\nThe recommendation uses the preregistered requirement that current improve in **both** formal windows for each condition. '
    text+='A full-window current improvement alone cannot overturn the boundary-inclusive D failure. '
    text+='Cumulative extent improvement and current improvement are reported separately; the first-order postprocessing trajectory is not a self-consistent model.\n'
    text+='\n## Component-wise correction sizes\n\n'
    for species in ['CK_CP','CK_CP_ADP']:
        measured=[v for v in component_scales if v['species']==species]
        worst=max(measured,key=lambda v:v['correction_over_individual_state_scale'])
        text+=f"- {species}: maximum |h1_i|/max(|h0_i|,1e-6) = {worst['correction_over_individual_state_scale']:.12g}, at {worst['condition']} t={worst['time_s']} s. The 1e-6 state floor is frozen R6; this is descriptive and creates no new gate.\n"
    if trajectory_scales:
        text+=f"\nAll retained outer postprocessing/formal samples were also checked: maximum vector correction/state ratio {max(v['correction_over_fast_state'] for v in trajectory_scales):.12g}; maximum Gq condition {max(v['Gq_condition'] for v in trajectory_scales):.12g}. Full signed physical margins are in first_order_trajectory_scale_diagnostics.csv.\n"
    if physical_scales:
        worst=max(physical_scales,key=lambda v:v['relative_correction'])
        outer=max((v for v in physical_scales if v['model']=='formal'),key=lambda v:v['relative_correction'])
        text+=f"\nThe vector q norm can hide a larger relative change in a small free CK state. Across all source/outer samples, maximum physical-fast-state relative change is {worst['relative_correction']:.12g} in {worst['species']} ({worst['model']}, t={worst['time_s']:.12g} s); this sample is applied by the candidate: {worst['applied_by_candidate']}. Across the actual formal outer trajectory the corresponding maximum is {outer['relative_correction']:.12g}. These individual physical-state ratios use the frozen 1e-6 state floor and remain descriptive.\n"
    commits=subprocess.check_output(['git','log','--reverse','--format=%H %s','1181ab2..HEAD'],cwd=ROOT,text=True).strip()
    text+='\n## Local commits before evidence closeout\n\n'+commits+'\n'
    report.write_text(text,encoding='utf-8',newline='\n')
    decision['boundary_interpretation']=boundary
    decision['descriptive_flags']+=['FULL_WINDOW_CURRENT_IMPROVEMENT_REPORTED_SEPARATELY','FIXED_SWITCH_STARTUP_TAIL_NOT_RECOVERED_BY_OUTER_FIRST_ORDER_GRAPH']
    write_json(OUT/'advancement_decision.json',decision)
    nav=load(OUT/'evidence_navigation.json')
    for node in nav['nodes']:node['sha256']=sha(ROOT/node['path'])
    nav['nodes'].append(dict(path='results/reduction/r7_ck_first_order/boundary_interpretation.json',status='INFERRED',role='signed source startup-tail interpretation',sha256=sha(OUT/'boundary_interpretation.json'),authoritative=False))
    write_json(OUT/'evidence_navigation.json',nav)
    paths=list(OUT.rglob('*'))+list((ROOT/'docs/reduction').glob('r7*md'))+list((ROOT/'scripts').glob('*r7*py'))
    write_json(OUT/'manifest.json',dict(schema='R7_MANIFEST_V1',files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths) if p.is_file() and p.name not in ['manifest.json','verification.json','final_commit_receipt.json']},
        registration_sha256=sha(OUT/'registration_binding.json'),pre_r7_file_count=load(OUT/'pre_r7_snapshot.json')['count'],conditions=CONDITIONS,promotion=False))
    print('Final R7 report and supplemental diagnostics bound; registration unchanged',flush=True)

if __name__=='__main__':main()
