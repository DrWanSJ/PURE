"""Additive signed boundary diagnostics; no change to any registered score."""
from r7_ck_h1_v1 import *
from r6_ck_common_v1 import rows
import json

def main():
    checked_binding();table=[];tail=[]
    for name in CONDITIONS:
        r=FirstOrderCK(name)
        with np.load(ROOT/'results/reduction/r6_ck_validation/per_condition'/name/'run_001/comparison.npz') as f:a={k:f[k].copy() for k in f.files}
        t=a['times'];b=int(np.flatnonzero(t==r.switch)[0]);source=a['source'][b]
        dz=r.T@source-r.z0;c=r.core(dz);x1,j1,_,_,_=r.observables(dz)
        mismatch=source[r.qix]-x1[r.qix]
        for ch in r.fast_channels:
            post=t>=r.switch;late=t>=.05
            error=abs(a['reduced_net'][:,ch]-a['source_net'][:,ch]);k=int(np.flatnonzero(post)[np.argmax(error[post])])
            fullscale=max(np.max(abs(a['source_net'][:,ch])),1e-9);postscale=max(np.max(abs(a['source_net'][post,ch])),1e-9)
            early=np.flatnonzero(t>=.001)[0]
            table.append(dict(condition=name,pair=r.channel_ids[ch],switch_s=r.switch,worst_time_s=float(t[k]),
                source_current_at_switch=float(a['source_net'][b,ch]),R6_current_at_switch=float(a['reduced_net'][b,ch]),
                formal_current_at_identical_slow_switch=float(j1[ch]),source_initial_current=float(a['source_net'][0,ch]),
                frozen_initial_mode_exp10_reference=float(a['source_net'][0,ch]*np.exp(-10)),
                full_source_scale=float(fullscale),post_source_scale=float(postscale),floor=1e-9,
                full_to_post_denominator_ratio=float(fullscale/postscale),post_max_abs_current_error=float(error[post].max()),
                post_0p05_max_abs_error=float(error[late].max()),source_zero_at_worst=bool(a['source_net'][k,ch]==0),
                source_early_tail_extent=float(a['source_extent'][early,ch]-a['source_extent'][b,ch]),
                R6_early_tail_extent=float(a['reduced_extent'][early,ch]-a['reduced_extent'][b,ch]),
                source_fast_graph_mismatch_CP=float(mismatch[0]),source_fast_graph_mismatch_CP_ADP=float(mismatch[1]),
                corresponding_J_fast_forcing_CP=float((c['J']@mismatch)[0]),corresponding_J_fast_forcing_CP_ADP=float((c['J']@mismatch)[1])))
        for k in np.flatnonzero((t>=r.switch)&(t<=.001)):
            for ch in r.fast_channels:
                tail.append(dict(condition=name,time_s=float(t[k]),pair=r.channel_ids[ch],source_current=float(a['source_net'][k,ch]),zero_current=float(a['reduced_net'][k,ch]),source_extent_since_switch=float(a['source_extent'][k,ch]-a['source_extent'][b,ch]),zero_extent_since_switch=float(a['reduced_extent'][k,ch]-a['reduced_extent'][b,ch])))
    write_csv(OUT/'boundary_current_diagnostics.csv',table);write_csv(OUT/'startup_tail_net_extent.csv',tail)
    worst=next(v for v in table if v['condition']=='R3_ATP_LOW' and v['pair'].startswith('re0000000332_'))
    write_json(OUT/'boundary_interpretation.json',dict(schema='R7_BOUNDARY_INTERPRETATION_V1',status='INFERRED_FROM_HASH_BOUND_SOURCE_AND_SIGNED_CURRENTS',
        conclusion='FROZEN_SWITCH_RETAINS_NONNEGLIGIBLE_FAST_STARTUP_TAIL; NOT_FLOOR_OR_ZERO_CROSSING_ARTIFACT',
        ATP_LOW=worst,score_mutation=False,switch_mutation=False,source_projection=False,promotion=False,
        inference='At the fixed 10*tau0 switch the source has an absolute fast-current tail and a small off-graph fast-state mismatch amplified by Gq. The normalized peak is about one because its post-window scale is the boundary tail; the error is real but brief. exp(-10) is a descriptive initial-mode reference, not a fitted law or source replacement.'))
    print('ATP_LOW real boundary discrepancy:',worst['post_max_abs_current_error'],'post-window scale:',worst['post_source_scale'],'early tail extent discrepancy:',worst['source_early_tail_extent']-worst['R6_early_tail_extent'],flush=True)

if __name__=='__main__':main()
