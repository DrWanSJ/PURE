"""Frozen CHAIN_01 V2 local comparison, with immutable numerical attempts.

Reuses V1 error/RMS, JSON and Radau/matrix-exponential conventions. Exponential
input is an autonomous forcing coordinate. Every source state, directed extent,
free/bound ledger and re21 product is retained in raw compressed CSV.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import gzip
import io
import json
from fractions import Fraction
from pathlib import Path
import platform
import sys
import traceback
from time import perf_counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.linalg import expm
from threadpoolctl import threadpool_limits

from prepare_chain01_v2 import ROOT, OUT, CONFIG, coefficients, digest, check_integrity
from validate_chain01_four_step import summarize_error, json_write

METRICS=['product_extent','product_current','pi_current','pi_extent','gdp_current','gdp_extent',
         'bound_pi','bound_gdp','bound_gtp','tu_bound','phosphate_unreleased','unfinished']
MODELS=['Full','Direct','Two-stage','Three-stage']
COLORS={'Full':'#222222','Direct':'#d2691e','Two-stage':'#2474b5','Three-stage':'#23824c'}


def matrix(spec, c=0, decay=0):
    n=len(spec['states']); r=np.array([float(Fraction(v)) for v in spec['rates_exact']])
    # chain chemical states, extents, then both exact source re21 products and
    # its extent if enabled; finally integral(u) and autonomous input q.
    labels=list(spec['states'])+[f'xi_stage_{i}' for i in range(n-1)]
    if c:
        labels+=['undocked_ribosome','undocked_intact_gtp_carrier','xi_re21']
    labels+=['input_integral','forcing_q']
    m=np.zeros((len(labels),len(labels)))
    for j,k in enumerate(r):
        m[j,j]-=k; m[j+1,j]+=k; m[n+j,j]+=k
    if c:
        m[0,0]-=c
        for label in ('undocked_ribosome','undocked_intact_gtp_carrier','xi_re21'):
            m[labels.index(label),0]=c
    m[0,-1]=1; m[-2,-1]=1; m[-1,-1]=-decay
    return m,labels,r


def initial(test,spec,labels):
    x=np.array(test['initial_full'],dtype=float)
    maps={'Full':x,'Direct':np.array([sum(x[:4]),x[4]]),
          'Two-stage':np.array([x[0]+x[1],x[2]+x[3],x[4]]),
          'Three-stage':np.array([x[0],x[1],x[2]+x[3],x[4]])}
    name=next(name for name in MODELS if spec['states']=={'Full':['S0','S1','S2','S3','S4'],'Direct':['S0','S4'],
                  'Two-stage':['S0','S2','S4'],'Three-stage':['S0','S1','S2','S4']}[name])
    state=np.zeros(len(labels)); state[:len(spec['states'])]=maps[name]
    return state


def spans(test,tau):
    end=test['end_tau']*tau
    if test['input_kind']=='rectangular':
        events=sorted(set([0.,end]+[x*tau for a,b,_ in test['input_segments'] for x in (a,b)]))
        return [(a,b,sum(amp for lo,hi,amp in test['input_segments'] if lo*tau<=(a+b)/2<hi*tau)) for a,b in zip(events,events[1:])]
    return [(0.,end,test.get('amplitude',0.))]


def times_for(test,config,tau):
    sampling=config['sampling']; end=test['end_tau']
    z=list(np.linspace(0,10,sampling['first_10_tau_count']))
    z+=list(np.linspace(0,.25,sampling['early_0_025_tau_count']))
    z+=list(np.geomspace(10,end,sampling['late_log_count']))
    if test['input_kind']=='exponential':
        z+=list(np.linspace(10,end,sampling['slow_linear_count']))
    for a,b,amp in test.get('input_segments',[]):
        for event in (a,b):
            z+=list(np.linspace(event,event+sampling['switch_band_tau'],sampling['switch_local_count']))
    z+=[v for v in sampling['checkpoint_tau'] if v<=end]
    # All times derive from the frozen grid; no search for favorable peaks.
    base=np.unique(np.array(z)*tau)
    refined=np.unique(np.r_[base,(base[:-1]+base[1:])/2])
    return base,refined,np.isin(refined,base)


def input_values(test,times,tau,side='right'):
    kind=test['input_kind']
    if kind=='zero': return np.zeros_like(times)
    if kind=='constant': return np.full_like(times,test['amplitude'])
    if kind=='exponential': return test['amplitude']*np.exp(-times/(test['T_slow_tau']*tau))
    out=np.zeros_like(times)
    for lo,hi,amp in test['input_segments']:
        mask=(times>=lo*tau)&(times<hi*tau) if side=='right' else (times>lo*tau)&(times<=hi*tau)
        out[mask]+=amp
    return out


def input_integral(test,times,tau):
    kind=test['input_kind']
    if kind=='zero': return np.zeros_like(times)
    if kind=='constant': return test['amplitude']*times
    if kind=='exponential':
        T=test['T_slow_tau']*tau
        return -test['amplitude']*T*np.expm1(-times/T)
    return sum((amp*np.maximum(0,np.minimum(times,hi*tau)-lo*tau) for lo,hi,amp in test['input_segments']),np.zeros_like(times))


def propagate(m,z,segments,times,method,rtol=None,atol=None):
    result=np.full((len(z),len(times)),np.nan); result[:,0]=z
    records=[]; state=z.copy()
    for lo,hi,amplitude in segments:
        state[-1]=amplitude
        indexes=np.flatnonzero((times>lo)&(times<=hi))
        if method=='expm':
            for i in indexes:
                result[:,i]=expm(m*(times[i]-lo))@state
            state=expm(m*(hi-lo))@state
            records.append({'start':lo,'end':hi,'success':True,'method':'augmented dense expm'})
        else:
            began=perf_counter()
            sol=solve_ivp(lambda t,y:m@y,(lo,hi),state,method=method,rtol=rtol,atol=atol,jac=m,dense_output=True)
            records.append({'start':lo,'end':hi,'success':bool(sol.success),'status':int(sol.status),'message':sol.message,
                            'nfev':sol.nfev,'nlu':sol.nlu,'internal_points':len(sol.t),'elapsed_seconds':perf_counter()-began})
            if not sol.success or sol.t[-1]!=hi:
                raise RuntimeError('NUMERICALLY_UNRESOLVED: '+sol.message)
            result[:,indexes]=sol.sol(times[indexes]); state=sol.y[:,-1]
    # The input coordinate is reset at events, while chemistry/extents are
    # continuous. The raw input columns explicitly store both event limits.
    if not np.isfinite(result).all(): raise RuntimeError('Nonfinite numerical trajectory')
    return result,records


def observable(z,spec,labels,r):
    n=len(spec['states']); x=z[:n]; xi=z[n:n+n-1]; curr=r[:,None]*x[:-1]
    obs={'product_extent':xi[-1],'product_current':curr[-1],
         'pi_current':curr[spec['pi_stage']],'pi_extent':xi[spec['pi_stage']],
         'gdp_current':curr[spec['gdp_stage']],'gdp_extent':xi[spec['gdp_stage']],
         'hydrolysis_extent':xi[spec['hydrolysis_stage']], 'S4_amount':x[-1]}
    for key,vec in coefficients(spec['states']).items(): obs[key]=np.array(vec)@x
    for key in ('undocked_ribosome','undocked_intact_gtp_carrier','xi_re21'):
        obs[key]=z[labels.index(key)] if key in labels else np.zeros(z.shape[1])
    return obs


def ledgers(z,spec,labels,obs,integral):
    n=len(spec['states']); x=z[:n]; hydro=obs['hydrolysis_extent']; escaped=obs['undocked_intact_gtp_carrier']
    delta=lambda key:obs[key]-obs[key][0]
    return {
        'ribosome':x.sum(axis=0)+obs['undocked_ribosome']-x[:,0].sum()-integral,
        'gtp_fate':delta('bound_gtp')+escaped+hydro-integral,
        'pi_fate':delta('bound_pi')+obs['pi_extent']-hydro,
        'gdp_fate':delta('bound_gdp')+obs['gdp_extent']-hydro,
        'tu_fate':delta('tu_bound')+obs['gdp_extent']+escaped-integral,
        'phosphate_total':delta('phosphate_unreleased')+obs['pi_extent']+escaped-integral,
        'product_from_extent':x[-1]-x[-1,0]-obs['product_extent'],
        'escaped_products':obs['undocked_ribosome']-escaped,
        're21_extent':obs['xi_re21']-escaped,
        'input_integral':z[-2]-integral,
    }


def masks(times,config,test,tau):
    z=times/tau; end=test['end_tau']; windows={}
    for name,bounds in config['windows'].items():
        if not isinstance(bounds,list): continue
        a,b=bounds
        hi=end if b is None else b
        if a<=end and hi>=a:
            mask=(times>=a*tau)&(times<=min(hi,end)*tau)
            if mask.any(): windows[name]=mask
    transient=times<=.25*tau
    for a,b,amp in test.get('input_segments',[]):
        for event in (a,b): transient|=(times>=event*tau)&(times<=(event+.25)*tau)
    windows['V1_transient']=(times<=10*tau)&transient
    windows['V1_post']=(times<=10*tau)&~transient
    return windows


def scale(test,metric,tau):
    key='current_scale' if metric.endswith('current') else 'amount_scale'
    return {'1':1.,'tau':tau,'1/tau':1/tau}[test[key]]


def csv_gz(path,columns,arrays):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('wb') as raw, gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as zipped:
        with io.TextIOWrapper(zipped,encoding='utf-8',newline='') as f:
            w=csv.writer(f,lineterminator='\n'); w.writerow(columns)
            for row in zip(*arrays): w.writerow([format(float(v),'.17g') if isinstance(v,(float,np.floating)) else v for v in row])


def write_raw(path,times,tau,test,base_mask,labels,solutions,observed,residues):
    columns=['t','t_over_tau','registered_grid','input_right','input_left','exact_input_integral']
    arrays=[times,times/tau,base_mask.astype(int),input_values(test,times,tau),input_values(test,times,tau,'left'),input_integral(test,times,tau)]
    for prefix,z in solutions.items():
        for i,label in enumerate(labels): columns.append(prefix+'_'+label); arrays.append(z[i])
    for label,values in observed.items(): columns.append('obs_'+label); arrays.append(values)
    for label,values in residues.items(): columns.append('residual_'+label); arrays.append(values)
    csv_gz(path,columns,arrays)


def write_error(path,times,tau,test,base_mask,ref,obs):
    columns=['t','t_over_tau','registered_grid']; arrays=[times,times/tau,base_mask.astype(int)]
    for metric in METRICS+['undocked_ribosome','undocked_intact_gtp_carrier']:
        diff=obs[metric]-ref[metric]; s=scale(test,metric,tau)
        with np.errstate(divide='ignore',invalid='ignore',over='ignore'):
            relative=np.divide(diff,np.abs(ref[metric]),out=np.full_like(diff,np.nan),where=ref[metric]!=0)
        for name,data in [('reference',ref[metric]),('candidate',obs[metric]),('signed',diff),('fixed_scale_signed',diff/s),('relative_signed',relative)]:
            columns.append(metric+'_'+name); arrays.append(data)
    csv_gz(path,columns,arrays)


def make_figures(path,runs,tau,phase):
    path.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':9,'axes.grid':True,'grid.alpha':.2})
    conditions=['A_pulse','B_constant','C_slow_20','C_slow_100','C_slow_1000','D_inventory']
    names=[('01_product_trajectory_comparison','product_extent','S4 formed (local amount)'),
           ('02_product_flux_comparison','product_current','S4 current (amount/source time)'),
           ('03_pi_release_comparison','pi_extent','Free Pi released (local amount)'),
           ('04_eftu_gdp_release_comparison','gdp_extent','Free EF-Tu.GDP released (local amount)'),
           ('05_internal_occupancy_comparison','unfinished','Unfinished ribosome inventory (local amount)')]
    for filename,metric,ylabel in names:
        fig,axes=plt.subplots(2,3,figsize=(13,7),constrained_layout=True)
        for ax,testid in zip(axes.flat,conditions):
            for name,run in runs[testid].items():
                keep=run['times']<=10*tau
                ax.plot(run['times'][keep]/tau,run['obs'][metric][keep],label=name,color=COLORS[name],linestyle='-' if name=='Full' else '--',linewidth=1.3)
            ax.set_title(testid); ax.set_xlabel('t / tau (source timebase)'); ax.set_ylabel(ylabel)
        axes.flat[0].legend(fontsize=8)
        fig.suptitle(f'{filename} | CHAIN01 V2 {phase}\nActual saved trajectories; author k=260,1000,7,1000; S4 downstream isolated',fontsize=11)
        fig.savefig(path/(filename+'.png'),dpi=150); plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(14,4.5),constrained_layout=True)
    for ax,metric in zip(axes,('product_extent','pi_extent','bound_gdp')):
        ref=runs['B_constant']['Full']['obs'][metric]
        for name,run in runs['B_constant'].items():
            ax.plot(run['times']/tau,(run['obs'][metric]-ref)/tau,color=COLORS[name],label=name)
        ax.set_xscale('symlog',linthresh=10); ax.set_title('Constant u=1: '+metric)
        ax.set_xlabel('t / tau, through 10000'); ax.set_ylabel('Signed error / fixed u0*tau')
    axes[0].legend(fontsize=8)
    fig.suptitle(f'06_long_time_output_comparison | V2 {phase}; persistent absolute offsets, actual CSV data')
    fig.savefig(path/'06_long_time_output_comparison.png',dpi=150); plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(13,7),constrained_layout=True)
    for col,ratio in enumerate((20,100,1000)):
        testid=f'C_slow_{ratio}'
        for row,metric in enumerate(('product_current','pi_current')):
            for name,run in runs[testid].items():
                axes[row,col].plot(run['times']/(ratio*tau),run['obs'][metric],label=name,color=COLORS[name],linestyle='-' if name=='Full' else '--')
            axes[row,col].set_title(f'T_slow={ratio} tau; {metric}')
            axes[row,col].set_xlabel('t / T_slow'); axes[row,col].set_ylabel('amount / source time')
    axes[0,0].legend(fontsize=8)
    fig.suptitle(f'07_slow_input_response | V2 {phase}; external u=exp(-t/T), not ATP/GTP depletion')
    fig.savefig(path/'07_slow_input_response.png',dpi=150); plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(13,7),constrained_layout=True)
    for ax,metric in zip(axes.flat,('pi_extent','gdp_extent','bound_pi','bound_gdp','bound_gtp','phosphate_unreleased')):
        ref=runs['B_constant']['Full']['obs'][metric]
        for name,run in runs['B_constant'].items():
            ax.plot(run['times']/tau,(run['obs'][metric]-ref)/tau,color=COLORS[name],label=name)
        ax.axhline(.01,color='gray',ls=':'); ax.axhline(-.01,color='gray',ls=':')
        ax.set_xscale('symlog',linthresh=10); ax.set_xlabel('t / tau'); ax.set_ylabel('Signed error / fixed u0*tau'); ax.set_title(metric)
    axes.flat[0].legend(fontsize=8)
    fig.suptitle(f'08_resource_ledger_error | V2 {phase}; actual unit-input data; fixed +/-1% budget')
    fig.savefig(path/'08_resource_ledger_error.png',dpi=150); plt.close(fig)


def run(boundary=False):
    integrity=check_integrity(); config=json.loads(CONFIG.read_text()); source=json.loads((OUT/'source_manifest.json').read_text())
    cert=json.loads((OUT/'mathematical_certificate.json').read_text()); tau=float(source['tau'])
    receipts=json.loads((OUT/'git_delivery_manifest.json').read_text())['rounds']
    needed='V2-R1' if boundary else 'V2-R0'
    assert any(r['round']==needed and r['local_commit_sha']==r['verified_remote_head_sha'] for r in receipts), 'Prior round must be delivered before first numerical run'
    phase='boundary' if boundary else 'base'; c=float(config['boundary_experiment']['rate_exact'].split('/')[0])/float(config['boundary_experiment']['rate_exact'].split('/')[1]) if boundary else 0.
    parent=OUT/phase; parent.mkdir(exist_ok=True)
    attempt=1+len(list(parent.glob('attempt_*'))); attemptpath=parent/f'attempt_{attempt:03d}'; attemptpath.mkdir()
    rawpath=OUT/'numerical_results'/phase/f'attempt_{attempt:03d}'
    errpath=OUT/'error_tables'/phase/f'attempt_{attempt:03d}'; errpath.mkdir(parents=True)
    figpath=OUT/'figures'/phase/f'attempt_{attempt:03d}'
    runtime={'phase':phase,'attempt':attempt,'started_utc':datetime.now(timezone.utc).isoformat(),'runner_sha256':digest(__file__),
             'config_sha256':digest(CONFIG),'prior_round_receipt':next(r for r in receipts if r['round']==needed),
             'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,'platform':platform.platform(),
             'no_clipping_or_projection':True,'scope':config['scope']}
    json_write(attemptpath/'runtime_manifest.json',runtime)
    runs={}; checks={}; records=[]; allsummary={}
    try:
        for testid,test in config['tests'].items():
            base,times,base_mask=times_for(test,config,tau); windows=masks(times,config,test,tau)
            integral=input_integral(test,times,tau); test_runs={}; testchecks={}
            for name in MODELS:
                spec=config['models'][name]; decay=1/(test['T_slow_tau']*tau) if test['input_kind']=='exponential' else 0.
                m,labels,r=matrix(spec,c,decay); z=initial(test,spec,labels); segments=spans(test,tau)
                z[-1]=segments[0][2]
                primary,pr=propagate(m,z,segments,times,'Radau',config['solver']['rtol'],config['solver']['atol'])
                tight,tr=propagate(m,z,segments,times,'Radau',config['solver']['tight_rtol'],config['solver']['tight_atol'])
                exact,er=propagate(m,z,segments,times,'expm')
                obs=observable(primary,spec,labels,r); exactobs=observable(exact,spec,labels,r)
                residues=ledgers(primary,spec,labels,obs,integral)
                ng=config['gates']['numerical']
                numerical={'primary_vs_expm':float(np.max(abs(primary-exact))), 'tight_vs_expm':float(np.max(abs(tight-exact))),
                           'primary_vs_tight':float(np.max(abs(primary-tight))),
                           'current_vs_expm':max(float(np.max(abs(obs[k]-exactobs[k]))) for k in METRICS if k.endswith('current')),
                           'ledger_max':max(float(np.max(abs(v))) for v in residues.values()),
                           'minimum_chemical_or_extent':float(np.min(primary[:-1])), 'segments_primary':pr,'segments_tight':tr}
                ok=(numerical['primary_vs_expm']<=ng['state_extent_absolute'] and numerical['tight_vs_expm']<=ng['state_extent_absolute'] and
                    numerical['primary_vs_tight']<=ng['convergence_absolute'] and numerical['current_vs_expm']<=ng['current_absolute'] and
                    numerical['ledger_max']<=ng['ledger_absolute'] and numerical['minimum_chemical_or_extent']>=-ng['negative_state_absolute'])
                if testid=='B_constant':
                    steady=cert['models'][name]['competition']['steady_unit_input_stage_occupancy_exact'] if boundary else cert['models'][name]['steady_unit_input_stage_occupancy_exact']
                    from fractions import Fraction
                    target=np.array([float(Fraction(v)) for v in steady])
                    numerical['steady_inventory_fixed_scale_error']=float(np.max(abs(primary[:len(r),-1]-target))/tau)
                    ok &= numerical['steady_inventory_fixed_scale_error']<=ng['steady_scaled_absolute']
                numerical['status']='PASS' if ok else 'NUMERICALLY_UNRESOLVED'
                write_raw(rawpath/f'{testid}__{name}.csv.gz',times,tau,test,base_mask,labels,{'primary':primary,'tight':tight,'expm':exact},obs,residues)
                test_runs[name]={'times':times,'obs':obs,'base_mask':base_mask,'spec':spec,'labels':labels}; testchecks[name]=numerical
            ref=test_runs['Full']['obs']; testsummary={}
            for name,runrec in test_runs.items():
                obs=runrec['obs']; metric_windows={}; densechange=0.
                for window,mask in windows.items():
                    metric_windows[window]={}
                    for metric in METRICS:
                        s=scale(test,metric,tau)
                        info=summarize_error(times,ref[metric],obs[metric],mask&base_mask,s)
                        dense=summarize_error(times,ref[metric],obs[metric],mask,s)
                        info['refined_grid_max_normalized']=dense['max_normalized']
                        info['grid_max_change']=abs(info['max_normalized']-dense['max_normalized'])
                        densechange=max(densechange,info['grid_max_change'])
                        info['max_time_over_tau']=info['time_of_max_absolute']/tau
                        threshold=.01
                        info['V2_fixed_budget_status']='PASS' if info['max_normalized']<=threshold else 'FAIL'
                        if window=='early_0_10' and metric in config['V1_diagnostic_thresholds']:
                            info['V1_diagnostic_status']='PASS' if info['max_normalized']<=config['V1_diagnostic_thresholds'][metric] else 'FAIL'
                        metric_windows[window][metric]=info
                        records.append([testid,name,window,metric,info['max_absolute'],info['max_normalized'],info['rms_normalized'],info['max_relative_defined'],s,info['max_time_over_tau'],info['V2_fixed_budget_status']])
                testchecks[name]['grid_max_change']=densechange
                if densechange>config['gates']['numerical']['dense_grid_maxima_change_absolute']:
                    testchecks[name]['status']='NUMERICALLY_UNRESOLVED'
                status={}
                for group in ('product','resources'):
                    passed=all(metric_windows[w][metric]['max_normalized']<=config['gates'][group]['max_fixed_scale_error'] for w in test['gate_windows'] for metric in config['gates'][group]['metrics'])
                    status[group]='SUPPORTED' if test['domain']=='IN_DOMAIN' and passed else 'NOT_SUPPORTED'
                    if testchecks[name]['status']!='PASS': status[group]='NUMERICALLY_UNRESOLVED'
                endpoints=[]
                for checkpoint in config['sampling']['checkpoint_tau']:
                    if checkpoint>test['end_tau'] or checkpoint<10: continue
                    i=int(np.argmin(abs(times-checkpoint*tau)))
                    row={'t_over_tau':checkpoint}
                    for metric in METRICS:
                        a=float(ref[metric][i]); b=float(obs[metric][i]); d=b-a
                        row[metric]={'reference':a,'candidate':b,'signed_absolute':d,'fixed_scale_signed':d/scale(test,metric,tau),'relative_absolute':abs(d)/abs(a) if a!=0 else None}
                    endpoints.append(row)
                initial_ledger={k:float(obs[k][0]-ref[k][0]) for k in ('bound_pi','bound_gdp','bound_gtp','tu_bound','phosphate_unreleased','unfinished')}
                production_windows={w:{'Full':float(ref['product_extent'][np.flatnonzero(mask)[-1]]-ref['product_extent'][np.flatnonzero(mask)[0]]),
                    'candidate':float(obs['product_extent'][np.flatnonzero(mask)[-1]]-obs['product_extent'][np.flatnonzero(mask)[0]])} for w,mask in windows.items()}
                rec={'domain':test['domain'],'status':status,'metrics':metric_windows,'endpoints':endpoints,'window_integrated_formation_current':production_windows,
                     'initial_resource_mapping_difference':initial_ledger,'sample_count':len(times),'registered_sample_count':int(base_mask.sum()),
                     'raw_csv':str((rawpath/f'{testid}__{name}.csv.gz').relative_to(ROOT)).replace('\\','/')}
                if boundary:
                    from fractions import Fraction
                    p=float(Fraction(cert['models'][name]['competition']['completion_probability_exact']))
                    q=float(Fraction(cert['models'][name]['competition']['escape_probability_exact']))
                    pf=float(Fraction(cert['models']['Full']['competition']['completion_probability_exact']))
                    qf=float(Fraction(cert['models']['Full']['competition']['escape_probability_exact']))
                    pe=abs(p-pf)/pf; qe=abs(q-qf)/qf
                    rec['allocation']={'completion_probability':p,'escape_probability':q,'completion_relative_error':pe,'escape_relative_error':qe,
                        'status':'LOCAL_BOUNDARY_SUPPORTED' if pe<=config['gates']['boundary']['completion_probability_relative'] and qe<=config['gates']['boundary']['escape_probability_relative'] else 'NOT_SUPPORTED'}
                    if testid=='A_pulse':
                        rec['allocation']['endpoint_yield_relative_error']=abs(obs['product_extent'][-1]-ref['product_extent'][-1])/ref['product_extent'][-1]
                        if rec['allocation']['endpoint_yield_relative_error']>config['gates']['boundary']['endpoint_yield_relative']:
                            rec['allocation']['status']='NOT_SUPPORTED'
                testsummary[name]=rec
                if name!='Full': write_error(errpath/f'{testid}__{name}.csv.gz',times,tau,test,base_mask,ref,obs)
            runs[testid]=test_runs; checks[testid]=testchecks; allsummary[testid]=testsummary
            print(f'{phase} {testid}: numerical '+', '.join(f'{name}={r["status"]}' for name,r in testchecks.items()),flush=True)
        columns=['test','model','window','metric','max_absolute','max_fixed_scale','rms_fixed_scale','max_relative_defined','fixed_scale','max_time_over_tau','V2_fixed_budget_status']
        with (errpath/'metrics.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f,lineterminator='\n'); w.writerow(columns); w.writerows(records)
        decision={}
        for name in MODELS:
            required=[rec[name] for testid,rec in allsummary.items() if config['tests'][testid]['domain']=='IN_DOMAIN']
            numeric=all(rec[name]['status']=='PASS' for rec in checks.values())
            prod=all(rec['status']['product']=='SUPPORTED' for rec in required)
            resource=all(rec['status']['resources']=='SUPPORTED' for rec in required)
            local=boundary and all(rec['allocation']['status']=='LOCAL_BOUNDARY_SUPPORTED' for rec in required)
            decision[name]={'numerical':'PASS' if numeric else 'NUMERICALLY_UNRESOLVED','product':'PRODUCT_OUTPUT_SUPPORTED' if numeric and prod else ('NOT_SUPPORTED' if numeric else 'NUMERICALLY_UNRESOLVED'),
                'resources':'RESOURCE_LEDGER_SUPPORTED' if numeric and resource else ('NOT_SUPPORTED' if numeric else 'NUMERICALLY_UNRESOLVED'),
                'boundary':'LOCAL_BOUNDARY_SUPPORTED' if local and numeric else ('NOT_SUPPORTED' if boundary and numeric else ('NOT_TESTED' if not boundary else 'NUMERICALLY_UNRESOLVED')),
                'macro':'LONG_TIME_MACRO_SUPPORTED' if numeric and prod and resource else ('NOT_SUPPORTED' if numeric else 'NUMERICALLY_UNRESOLVED')}
        summary={'protocol_id':config['protocol_id'],'phase':phase,'attempt':attempt,'config_sha256':digest(CONFIG),'tau':tau,'time_unit':config['time_unit'],
                 'c_re21':c,'decisions':decision,'tests':allsummary,'historical_integrity':integrity,
                 'scope':config['scope'],'full_coupled_validation':'NOT_STARTED','scientific_promotion':'NOT_GRANTED'}
        json_write(attemptpath/'validation_summary.json',summary)
        json_write(attemptpath/'verification_report.json',{'status':'PASS' if all(rec['status']=='PASS' for test in checks.values() for rec in test.values()) else 'NUMERICALLY_UNRESOLVED','checks':checks,'thresholds':config['gates']['numerical']})
        make_figures(figpath,runs,tau,phase)
        fig,ax=plt.subplots(figsize=(8,4.5),constrained_layout=True)
        for name in MODELS:
            worstprod=max(rec[name]['metrics'][w][metric]['max_normalized'] for testid,rec in allsummary.items() if config['tests'][testid]['domain']=='IN_DOMAIN' for w in config['tests'][testid]['gate_windows'] for metric in config['gates']['product']['metrics'])
            worstres=max(rec[name]['metrics'][w][metric]['max_normalized'] for testid,rec in allsummary.items() if config['tests'][testid]['domain']=='IN_DOMAIN' for w in config['tests'][testid]['gate_windows'] for metric in config['gates']['resources']['metrics'])
            n=len(config['models'][name]['rates_exact'])
            ax.scatter([n],[worstprod],color=COLORS[name],marker='o',label=name+' product')
            ax.scatter([n],[worstres],color=COLORS[name],marker='x',label=name+' ledger')
        ax.axhline(.01,color='gray',ls=':',label='Frozen 1% budget'); ax.set_yscale('symlog',linthresh=.001)
        ax.set_xlabel('Chain reaction count (Full 4; Direct 1; Two-stage 2; Three-stage 3)'); ax.set_ylabel('Worst required-window error / fixed scale'); ax.legend(fontsize=8,ncol=2)
        ax.set_title(f'09_complexity_accuracy_tradeoff | V2 {phase}\nActual saved errors; chemical states = reactions+1; extents counted separately')
        fig.savefig(figpath/'09_complexity_accuracy_tradeoff.png',dpi=150); plt.close(fig)
        json_write(figpath/'data_sources.json',{'model_version':config['protocol_id'],'phase':phase,'time_unit':config['time_unit'],'amount_unit':config['amount_unit'],
                   'raw_data':str(rawpath.relative_to(ROOT)).replace('\\','/'),'errors':str(errpath.relative_to(ROOT)).replace('\\','/'),
                   'condition_details':config['tests'],'c_re21':c,'plots_are_actual_saved_numerics':True})
        artifacts=[{'path':str(f.relative_to(ROOT)).replace('\\','/'),'sha256':digest(f),'bytes':f.stat().st_size} for parentpath in (rawpath,errpath,figpath,attemptpath) for f in sorted(parentpath.rglob('*')) if f.is_file()]
        json_write(attemptpath/'artifact_manifest.json',{'artifacts':artifacts,'config_sha256':digest(CONFIG)})
        json_write(OUT/(phase+'_latest.json'),{'attempt':attempt,'summary':str((attemptpath/'validation_summary.json').relative_to(ROOT)).replace('\\','/'),
                 'verification':str((attemptpath/'verification_report.json').relative_to(ROOT)).replace('\\','/'),'artifact_manifest':str((attemptpath/'artifact_manifest.json').relative_to(ROOT)).replace('\\','/')})
        print(json.dumps(decision,indent=2),flush=True)
        return summary
    except Exception as error:
        json_write(attemptpath/'failure.json',{'status':'NUMERICALLY_UNRESOLVED','error':str(error),'traceback':traceback.format_exc()})
        raise


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--boundary',action='store_true'); args=ap.parse_args()
    with threadpool_limits(limits=1): run(args.boundary)
