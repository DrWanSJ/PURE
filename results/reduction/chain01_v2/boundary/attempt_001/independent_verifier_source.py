"""Independent source-rebuilt rational Laplace verifier; never imports V2 runner.

Trajectory checkpoints are evaluated from exact rational residues at 70 decimal
digits, including repeated rate-1000 poles. Raw all-grid currents, fate identities,
fixed-scale scores, and artifact hashes are separately reconstructed.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import mpmath as mp
import numpy as np
import sympy as sp

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/reduction/chain01_v2'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_chain01_four_step import rational_math

mp.mp.dps=70
S=sp.Symbol('s')
METRICS=['product_extent','product_current','pi_current','pi_extent','gdp_current','gdp_extent','bound_pi','bound_gdp','bound_gtp','tu_bound','phosphate_unreleased','unfinished']


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def rat(value):
    f=F(value); return sp.Rational(f.numerator,f.denominator)


def exact_refs(reaction,side):
    out={}
    for ref in reaction.findall('{*}listOf'+side+'/{*}speciesReference'):
        node=ref.find('{*}stoichiometryMath')
        value=rational_math(node) if node is not None else F(ref.get('stoichiometry','1'))
        out[ref.attrib['species']]=out.get(ref.attrib['species'],F(0))+value
    return out


def sources():
    tree=ET.parse(ROOT/'models/pnas2017_full_reference/original/fMGG_synthesis.xml')
    reactions={r.attrib['id']:r for r in tree.findall('.//{*}reaction')}
    with (ROOT/'models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv').open(encoding='utf-8-sig',newline='') as f:
        params={r['Name']:F(r['Value']) for r in csv.DictReader(f)}
    ids=[f're{i:010d}' for i in (14,16,17,18)]
    aliases=[]; rates=[]; cols=[]
    for rid in ids:
        r=reactions[rid]; lhs=exact_refs(r,'Reactants'); rhs=exact_refs(r,'Products')
        assert len(lhs)==1 and next(iter(lhs.values()))==1
        sid=next(iter(lhs)); aliases.append(sid); rates.append(params[rid+'_k1'])
        assert [(x.text or '').strip() for x in r.findall('.//{*}kineticLaw/{*}math//{*}ci')]==['k1',sid]
        cols.append({s:rhs.get(s,F(0))-lhs.get(s,F(0)) for s in lhs.keys()|rhs.keys()})
    last=exact_refs(reactions[ids[-1]],'Products'); assert len(last)==1
    aliases.append(next(iter(last)))
    r21=reactions['re0000000021']; c=params['re0000000021_k1']
    assert exact_refs(r21,'Reactants')=={aliases[0]:F(1)}
    assert exact_refs(r21,'Products')=={'EFTu_GTP_GlytRNAGlyGCC':F(1),'elRS70SAGGU0002_fMet':F(1)}
    assert [(x.text or '').strip() for x in r21.findall('.//{*}kineticLaw/{*}math//{*}ci')]==['k1',aliases[0]]
    species=[r.attrib['id'] for r in tree.findall('.//{*}species')]
    return rates,aliases,cols,c,species


@lru_cache(maxsize=None)
def residues(expr,poles):
    """Independent inverse Laplace coefficients, with exact pole multiplicity."""
    expr=sp.cancel(expr)
    if expr==0: return ()
    den=sp.Poly(sp.denom(expr),S)
    result=[]
    for pole in set(poles):
        factor=sp.Poly(S+pole,S); multiplicity=0; remden=den
        while remden.degree()>0:
            quotient,remainder=sp.div(remden,factor)
            if remainder.as_expr()!=0: break
            multiplicity+=1; remden=quotient
        if not multiplicity: continue
        h=sp.cancel(expr*(S+pole)**multiplicity)
        for j in range(1,multiplicity+1):
            a=sp.diff(h,S,multiplicity-j).subs(S,-pole)/sp.factorial(multiplicity-j)
            if a:
                result.append((mp.mpf(str(sp.N(a,75))),mp.mpf(str(sp.N(pole,75))),j))
    # A missing pole would silently omit a response component. Verify the
    # rational identity before any floating-point checkpoint evaluation.
    known_product=sp.prod((S+p)**sp.degree(sp.gcd(sp.Poly(sp.denom(expr),S),sp.Poly((S+p)**10,S))) for p in set(poles))
    assert sp.degree(sp.denom(expr),S)==sp.degree(known_product,S), 'Unrecognized rational-response pole'
    return tuple(result)


def value(terms,t):
    if t<0: return mp.mpf('0')
    return mp.fsum(a*t**(j-1)/mp.factorial(j-1)*mp.exp(-p*t) for a,p,j in terms)


def closed_forms(k,x,c,b):
    damp=[k[0]+c]+k[1:]
    init=[]; drive=[]
    for i,rate in enumerate(damp):
        init.append(sp.cancel((rat(x[i])+(k[i-1]*init[i-1] if i else 0))/(S+rate)))
        drive.append(sp.cancel((k[i-1]*drive[i-1] if i else 1)/((S+rate)*(1 if i else S+b))))
    # Final product plus directed extents; re21's two exact product amounts are
    # identical to its extent, but independently checked in the raw ledger.
    ini=init+[k[-1]*init[-1]/S+rat(x[-1])/S]+[r*v/S for r,v in zip(k,init)]+[c*init[0]/S]*3
    dri=drive+[k[-1]*drive[-1]/S]+[r*v/S for r,v in zip(k,drive)]+[c*drive[0]/S]*3
    poles=tuple(damp+[b,sp.Integer(0)])
    return [residues(v,poles) for v in ini],[residues(v,poles) for v in dri]


def mapped_initial(x,name):
    return {'Full':x,'Direct':[sum(x[:4]),x[4]],'Two-stage':[x[0]+x[1],x[2]+x[3],x[4]],'Three-stage':[x[0],x[1],x[2]+x[3],x[4]]}[name]


def independently_observe(data,states,rates,pi,gdp):
    x=np.array([data['primary_'+s] for s in states]); n=len(states)
    xi=np.array([data[f'primary_xi_stage_{i}'] for i in range(n-1)])
    v=np.array(list(map(float,rates)))[:,None]*x[:-1]
    out={'product_extent':xi[-1],'product_current':v[-1],'pi_extent':xi[pi],'pi_current':v[pi],'gdp_extent':xi[gdp],'gdp_current':v[gdp]}
    for key,aliases in {'bound_pi':['S1'],'bound_gdp':['S1','S2'],'bound_gtp':['S0'],'tu_bound':['S0','S1','S2'],'phosphate_unreleased':['S0','S1'],'unfinished':['S0','S1','S2','S3']}.items():
        out[key]=sum((x[i] for i,s in enumerate(states) if s in aliases),np.zeros(len(data)))
    return out,x,xi


def verify(boundary=False):
    phase='boundary' if boundary else 'base'; config=read(ROOT/'configs/reduction/chain01_v2_validation.json')
    freeze=read(OUT/'protocol_freeze.json')
    for rel,expected in freeze['bindings'].items(): assert sha(ROOT/rel)==expected,rel
    protected=read(OUT/'protected_files_before.json')['files']
    for rel,expected in protected.items(): assert sha(ROOT/rel)==expected,rel
    latest=read(OUT/(phase+'_latest.json')); summary=read(ROOT/latest['summary']); verifyrec=read(ROOT/latest['verification'])
    for artifact in read(ROOT/latest['artifact_manifest'])['artifacts']:
        assert sha(ROOT/artifact['path'])==artifact['sha256'],artifact['path']
    rates,aliases,cols,c_author,species=sources(); tau=sum((1/k for k in rates),F(0))
    specs={
        'Full':(['S0','S1','S2','S3','S4'],rates,1,2,[[0],[1],[2],[3]]),
        'Direct':(['S0','S4'],[1/tau],0,0,[[0,1,2,3]]),
        'Two-stage':(['S0','S2','S4'],[1/(1/rates[0]+1/rates[1]),1/(1/rates[2]+1/rates[3])],0,1,[[0,1],[2,3]]),
        'Three-stage':(['S0','S1','S2','S4'],[rates[0],rates[1],1/(1/rates[2]+1/rates[3])],1,2,[[0],[1],[2,3]])}
    manifest=read(OUT/'source_manifest.json'); cert=read(OUT/'mathematical_certificate.json')
    assert list(manifest['species_aliases'].values())==aliases
    assert abs(summary['tau']-float(tau))<1e-15
    waiting={}
    for name,(states,k,pi,gdp,segments) in specs.items():
        damp=np.array([float(k[0]+(c_author if boundary else 0))]+[float(v) for v in k[1:]])
        q=np.diag(-damp)
        for i in range(len(k)-1): q[i+1,i]=float(k[i])
        z=np.zeros(len(k)); z[0]=1
        a=np.linalg.solve(-q,z); bvec=np.linalg.solve(-q,a); cvec=np.linalg.solve(-q,bvec)
        success=float(k[-1])*a[-1]
        conditional_mean=float(k[-1])*bvec[-1]/success
        conditional_variance=2*float(k[-1])*cvec[-1]/success-conditional_mean**2
        expected_mean=sum((1/F(str(v)) for v in damp),F(0))
        # Float damping is checked against the exact parameter list separately;
        # rational expected moments below retain the source fractions.
        waits=[1/(k[0]+(c_author if boundary else 0))]+[1/v for v in k[1:]]
        exact_mean=sum(waits,F(0)); exact_variance=sum((v*v for v in waits),F(0))
        assert abs(conditional_mean-float(exact_mean))<1e-12
        assert abs(conditional_variance-float(exact_variance))<1e-12
        waiting[name]={'success_probability':success,'numeric_resolvent_mean':conditional_mean,'numeric_resolvent_variance':conditional_variance,
                       'source_expected_mean_exact':str(exact_mean),'source_expected_variance_exact':str(exact_variance),'status':'PASS'}
    checks={}; all_data={}; largest=0.
    for testid,test in config['tests'].items():
        all_data[testid]={}
        for name,(states,k,pi,gdp,segments) in specs.items():
            rec=summary['tests'][testid][name]; assert list(map(F,config['models'][name]['rates_exact']))==k
            for segment,column in zip(segments,cert['models'][name]['stoichiometric_columns_exact']):
                expected={sid:sum((cols[i].get(sid,F(0)) for i in segment),F(0)) for sid in species}
                expected={sid:v for sid,v in expected.items() if v}
                assert {sid:F(v) for sid,v in column.items()}==expected
            data=np.genfromtxt(ROOT/rec['raw_csv'],delimiter=',',names=True)
            obs,x,xi=independently_observe(data,states,k,pi,gdp); all_data[testid][name]=(data,obs)
            for metric in METRICS: assert np.max(abs(obs[metric]-data['obs_'+metric]))<=1e-12
            cp=c_author if boundary else F(0); kp=[rat(v) for v in k]; x0=mapped_initial(test['initial_full'],name)
            b=rat(1/(F(test['T_slow_tau'])*tau)) if test['input_kind']=='exponential' else sp.Integer(0)
            ini,dri=closed_forms(kp,x0,rat(cp),b)
            indexes=set(range(0,len(data),max(1,len(data)//40))); indexes.add(len(data)-1)
            for checkpoint in config['sampling']['checkpoint_tau']:
                if checkpoint<=test['end_tau']: indexes.add(int(np.argmin(abs(data['t']-checkpoint*float(tau)))))
            for wmetrics in rec['metrics'].values():
                for mrec in wmetrics.values(): indexes.add(int(np.argmin(abs(data['t']-mrec['time_of_max_absolute']))))
            expected_labels=['primary_'+s for s in states]+[f'primary_xi_stage_{i}' for i in range(len(k))]
            if boundary: expected_labels+=['primary_undocked_ribosome','primary_undocked_intact_gtp_carrier','primary_xi_re21']
            errors={}; max_current=0.
            for i in sorted(indexes):
                t=mp.mpf(str(data['t'][i])); vals=[value(term,t) for term in ini]
                kind=test['input_kind']
                if kind in ('constant','exponential'):
                    vals=[v+test['amplitude']*value(term,t) for v,term in zip(vals,dri)]
                elif kind=='rectangular':
                    for lo,hi,amp in test['input_segments']:
                        vals=[v+amp*(value(term,t-mp.mpf(str(lo*float(tau))))-value(term,t-mp.mpf(str(hi*float(tau))))) for v,term in zip(vals,dri)]
                for label,v in zip(expected_labels,vals):
                    e=abs(data[label][i]-float(v)); errors[label]=max(errors.get(label,0.),e); largest=max(largest,e)
                exactcurr=[float(kp[j]*vals[j]) for j in range(len(k))]
                max_current=max(max_current,*[abs(exactcurr[j]-float(k[j])*data['primary_'+states[j]][i]) for j in range(len(k))])
            assert max(errors.values())<=config['gates']['numerical']['state_extent_absolute'],(testid,name,errors)
            assert max_current<=config['gates']['numerical']['current_absolute'],(testid,name,max_current)
            esc=data['primary_undocked_intact_gtp_carrier'] if boundary else np.zeros(len(data))
            escape_rib=data['primary_undocked_ribosome'] if boundary else esc
            integ=data['exact_input_integral']
            delta=lambda key:obs[key]-obs[key][0]
            residuals=[x.sum(axis=0)+escape_rib-x[:,0].sum()-integ,
                       delta('bound_gtp')+esc+xi[0]-integ,
                       delta('bound_pi')+obs['pi_extent']-xi[0],
                       delta('bound_gdp')+obs['gdp_extent']-xi[0],
                       delta('tu_bound')+obs['gdp_extent']+esc-integ,
                       delta('phosphate_unreleased')+obs['pi_extent']+esc-integ,
                       x[-1]-x[-1,0]-obs['product_extent'],escape_rib-esc]
            ledger=max(np.max(abs(v)) for v in residuals); assert ledger<=config['gates']['numerical']['ledger_absolute']
            if boundary:
                assert np.max(abs(data['primary_xi_re21']-esc))<=1e-12
                p=k[0]/(k[0]+cp); q=cp/(k[0]+cp); pf=rates[0]/(rates[0]+cp); qf=cp/(rates[0]+cp)
                assert abs(rec['allocation']['completion_probability']-float(p))<1e-14
                assert abs(rec['allocation']['escape_relative_error']-float(abs(q-qf)/qf))<1e-12
            checks[testid+'__'+name]={'analytic_checkpoint_count':len(indexes),'max_state_extent_error':max(errors.values()),'max_current_error':max_current,'all_grid_ledger_error':float(ledger),'all_grid_current_reconstruction':'PASS'}
            print(f'Independent {phase} {testid} {name}: PASS ({len(indexes)} rational-residue checkpoints)',flush=True)
    # Reconstruct required-window scores and status independently from raw arrays.
    score_count=0
    for testid,test in config['tests'].items():
        full_data,ref=all_data[testid]['Full']
        for name,(data,obs) in all_data[testid].items():
            rec=summary['tests'][testid][name]; registered=data['registered_grid']==1
            group_support={}
            for w in test['gate_windows']:
                a,b=config['windows'][w]; b=test['end_tau'] if b is None else b
                mask=registered&(data['t']>=a*float(tau))&(data['t']<=b*float(tau))
                assert mask.any()
                for metric in METRICS:
                    scales={'1':1.,'tau':float(tau),'1/tau':1/float(tau)}
                    scale=scales[test['current_scale' if metric.endswith('current') else 'amount_scale']]
                    maximum=float(np.max(abs(obs[metric][mask]-ref[metric][mask]))/scale)
                    recorded=rec['metrics'][w][metric]['max_normalized']
                    assert abs(maximum-recorded)<=1e-11,(testid,name,w,metric,maximum,recorded)
                    score_count+=1
            for group in ('product','resources'):
                passed=all(rec['metrics'][w][metric]['max_normalized']<=config['gates'][group]['max_fixed_scale_error'] for w in test['gate_windows'] for metric in config['gates'][group]['metrics'])
                group_support[group]=passed and test['domain']=='IN_DOMAIN'
                numeric=verifyrec['checks'][testid][name]['status']=='PASS'
                assert rec['status'][group]==('NUMERICALLY_UNRESOLVED' if not numeric else ('SUPPORTED' if group_support[group] else 'NOT_SUPPORTED'))
    report={'status':'PASS','phase':phase,'method':'Independent exact-rational source reconstruction and 70-digit inverse Laplace residues; no V2 runner imports',
            'verifier_sha256':sha(__file__),
            'source_species_count':len(species),'source_reaction_ids':[f're{i:010d}' for i in (14,16,17,18,21)],
            'config_sha256':sha(ROOT/'configs/reduction/chain01_v2_validation.json'),'source_manifest_sha256':sha(OUT/'source_manifest.json'),
            'protected_file_count':len(protected),'analytic_checks':checks,'largest_checkpoint_state_extent_error':largest,'required_window_scores_verified':score_count,
            'waiting_time_resolvent_checks':waiting,
            'numerical_resolution_status_from_registered_run':verifyrec['status'],'scientific_approval':'NOT_GRANTED_BY_VERIFIER'}
    attemptdir=(ROOT/latest['summary']).parent
    (attemptdir/'independent_verifier_source.py').write_bytes(Path(__file__).read_bytes())
    (attemptdir/'independent_verification.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'PASS','phase':phase,'largest_checkpoint_error':largest,'required_window_scores_verified':score_count}))
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--boundary',action='store_true'); args=ap.parse_args()
    verify(args.boundary)
