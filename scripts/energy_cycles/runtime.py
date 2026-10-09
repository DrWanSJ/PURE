"""Preregistered microscopic and source-derived total-QSSA comparisons.

No state clipping, parameter fitting, source writes, or scientific promotion.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import root
from scipy.linalg import null_space
from kinetics_analysis import stationary_explicit, composition_matrix

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/energy_cycles_v1'
REG=ROOT/'docs/reduction/energy_cycles/validation_preregistration.json'
NET={'CK':[-1,-1,1,1],'NDK':[-1,-1,1,1],'MK':[-1,-1,2],'PPiase':[-1,2]}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_json(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf-8')

class DomainFailure(RuntimeError):pass

class Module:
    def __init__(self,d,u):
        self.unit=u;self.name=u['name'];self.B=u['boundary_species'];self.E=u['enzyme_states']
        self.species=self.B+self.E+u['degraded_states'];self.n=len(self.species)
        self.index={s:i for i,s in enumerate(self.species)}
        self.reactions=[r for r in d['reactions'] if r['id'] in u['reaction_ids']]
        self.parameters={r['id']:r['k'] for r in d['reactions']}
        self.S=np.zeros((self.n,len(self.reactions)))
        for j,r in enumerate(self.reactions):
            for side,sgn in [('reactants',-1),('products',1)]:
                for s,c in r[side].items():self.S[self.index[s],j]+=sgn*c
        self.k=np.array([r['k'] for r in self.reactions]);self.ki=[np.array([self.index[s] for s in r['kinetic_species']],int) for r in self.reactions]
        self.active=np.flatnonzero(self.k>0)
        self.Sa=self.S[:,self.active];self.ka=self.k[self.active];self.kia=[self.ki[j] for j in self.active]
        self.C=composition_matrix(u)
        self.N=np.asarray(NET[self.name],float)
        pair=list(u['catalytic_pair'])
        forward=next(r for r in self.reactions if r['id']==pair[0])
        if len(pair)==1 and forward['reverse_partner']:pair.append(forward['reverse_partner'])
        self.cat=[next(i for i,r in enumerate(self.reactions) if r['id']==rid) for rid in pair]
        self.cata=[list(self.active).index(i) if i in self.active else None for i in self.cat]
        self.A=np.zeros((len(self.B),self.n));self.A[:,:len(self.B)]=np.eye(len(self.B));self.A[:,len(self.B):len(self.B)+len(self.E)]=self.C
        self.invariant=null_space(self.N.reshape(1,-1)).T@self.A
        self.invariant=np.vstack([self.invariant,np.r_[np.zeros(len(self.B)),np.ones(len(self.E)),np.zeros(len(u['degraded_states']))]])
        self.R=np.zeros((len(self.E),len(self.E)-1));self.R[0,:]=-1;self.R[1:,:]=np.eye(len(self.E)-1)

    def rates(self,x):
        return np.array([k*np.prod(x[idx]) for k,idx in zip(self.ka,self.kia)])

    def currents(self,x):
        v=self.rates(x);f=v[self.cata[0]];r=v[self.cata[1]] if len(self.cata)>1 and self.cata[1] is not None else 0.
        return f,r

    def rhs(self,t,z):
        x=z[:self.n];v=self.rates(x);f=v[self.cata[0]];r=v[self.cata[1]] if len(self.cata)>1 and self.cata[1] is not None else 0.
        return np.r_[self.Sa@v,f,r]

    def jac(self,t,z):
        x=z[:self.n];D=np.zeros((len(self.active),self.n))
        for j,(k,idx) in enumerate(zip(self.ka,self.kia)):
            for a,i in enumerate(idx):D[j,i]+=k*np.prod(np.delete(x[idx],a))
        J=np.zeros((self.n+2,self.n+2));J[:self.n,:self.n]=self.Sa@D
        J[-2,:self.n]=D[self.cata[0]]
        if len(self.cata)>1 and self.cata[1] is not None:J[-1,:self.n]=D[self.cata[1]]
        return J

    def stationary(self,u,E):
        h,v=stationary_explicit(self.unit,dict(zip(self.B,u)),E,self.parameters)
        hv=np.array([h[s] for s in self.E]);T=u+self.C@hv
        return T,hv,v

    def total_jac(self,u,E):
        D=np.empty((len(self.B),len(self.B)))
        for j in range(len(self.B)):
            c=np.asarray(u,dtype=complex);c[j]+=1e-25j
            D[:,j]=self.stationary(c,E)[0].imag/1e-25
        return D

    def corner_proof(self,T):
        # Source chemical conversion forms obligatorily occupied product states.
        if self.name in ('CK','NDK','MK'):
            if T[0]>0 and T[1]>0 and np.all(T[2:]==0):
                return 'Positive substrate totals with zero product-form totals force every product complex to zero, but source-positive catalytic forward conversion feeds those states: no stationary physical root.'
        if self.name=='PPiase' and T[0]>0 and T[1]==0:
            return 'Positive PPi total with zero PO4 total forces both PO4 complexes to zero; source k407>0 feeds the double-PO4 state: no stationary physical root.'
        return None

    def closure(self,T,E,start=None):
        proof=self.corner_proof(T)
        if proof:raise DomainFailure(proof)
        if np.min(T)<-1e-8:raise DomainFailure('Negative retained inventory beyond frozen allowance')
        # Deterministic solve; no projection or clipping of inventory values.
        q=root(lambda u:self.stationary(u,E)[0]-T,np.asarray(T if start is None else start),
               jac=lambda u:self.total_jac(u,E),tol=1e-10)
        u=q.x;_,h,v=self.stationary(u,E);res=float(np.max(np.abs(u+self.C@h-T)))
        if res>1e-8 or min(np.min(u),np.min(h)) < -1e-8 or np.max(u-T)>1e-8:
            raise DomainFailure(f'No certified physical algebraic root: residual={res:.6g}, min_free={np.min(u):.6g}, min_bound={np.min(h):.6g}; solver={q.message}')
        singular=float(np.linalg.svd(self.total_jac(u,E),compute_uv=False)[-1])
        if singular<=1e-8:raise DomainFailure('Total inversion locally singular')
        x=np.r_[u,h,np.zeros(len(self.unit['degraded_states']))]
        f,r=self.currents(x)
        return x,np.array([f,r]),res,singular

    def fast_eigen(self,x):
        # Explicit fixed-total enzyme tangent, not merely frozen-free Q spectrum.
        J=self.jac(0,np.r_[x,0,0])[:self.n,:self.n]
        nr=len(self.B);ne=len(self.E)
        F=J[nr:nr+ne,nr:nr+ne]-J[nr:nr+ne,:nr]@self.C
        return np.linalg.eigvals((F@self.R)[1:,:])

def integrate_micro(m,x0,grid,rtol,atol,method):
    q=solve_ivp(m.rhs,(0,1000),np.r_[x0,0,0],method=method,jac=m.jac,rtol=rtol,atol=atol,t_eval=grid)
    if not q.success or q.y.shape[1]!=len(grid):raise RuntimeError('Microscopic solver did not complete: '+q.message)
    return q.y.T,{'method':method,'nfev':q.nfev,'njev':q.njev,'nlu':q.nlu,'message':q.message}

def integrate_reduced(m,T0,E,grid,rtol,atol):
    def rhs(t,z):return m.closure(T0+m.N*(z[0]-z[1]),E)[1]
    q=solve_ivp(rhs,(0,1000),[0.,0.],method='Radau',rtol=rtol,atol=atol,t_eval=grid)
    if not q.success:raise RuntimeError('Reduced solver did not complete: '+q.message)
    z=q.y.T;xr=[];res=[];sing=[];eig=[];curr=[]
    for zz in z:
        x,v,a,b=m.closure(T0+m.N*(zz[0]-zz[1]),E)
        ee=m.fast_eigen(x)
        if float(np.max(ee.real))>=-1e-8:raise DomainFailure('Selected root lacks local fixed-total fast attractivity')
        xr.append(x);curr.append(v);res.append(a);sing.append(b);eig.append(ee)
    return np.column_stack([xr,z]),np.array(curr),{'method':'Radau','nfev':q.nfev,'njev':q.njev,'nlu':q.nlu,
      'maximum_closure_residual':float(max(res)),'minimum_total_jacobian_singular_value':float(min(sing)),
      'maximum_fast_tangent_real_eigenvalue':float(np.max(np.asarray(eig).real)),
      'minimum_fast_relaxation_rate':float(np.min(-np.asarray(eig).real)),'message':q.message}

def rms(t,v):
    return float(np.sqrt(np.trapz(v*v,t)/(t[-1]-t[0])))

def observations(m,z):
    x=z[:,:m.n];nr=len(m.B);ne=len(m.E)
    return {'free':x[:,:nr],'bound':x[:,nr:nr+ne]@m.C.T,'retained':x@m.A.T,
      'occupancy':x[:,nr:nr+ne], 'current':np.array([m.currents(xx) for xx in x]),
      'net_extent':z[:,-2]-z[:,-1], 'all_active_source_flux':np.array([m.rates(xx) for xx in x])}

def compare(m,case,mode,reg,grid,micro,microtight,microbdf,red,redtight,solver):
    om=observations(m,micro);orr=observations(m,red)
    mt=observations(m,microtight);mb=observations(m,microbdf);rt=observations(m,redtight)
    scales=np.array([case['concentration_scales'][s] for s in m.B]);bsc=np.array([case['bound_scales'][s] for s in m.B]);E=case['enzyme_total']
    windows=[];flux_capacity=E*sum(m.parameters[m.reactions[j]['id']] for j in m.cat)
    long=grid>=1;vn=om['current'][:,0]-om['current'][:,1];vr=orr['current'][:,0]-orr['current'][:,1]
    flux_scale=max(rms(grid[long],vn[long]),.01*flux_capacity,1e-12)
    inv0=m.invariant@micro[0,:m.n];invs=np.maximum(abs(inv0),1.)
    cons=max(float(np.max(abs(micro[:,:m.n]@m.invariant.T-inv0)/invs)),float(np.max(abs(red[:,:m.n]@m.invariant.T-inv0)/invs)))
    for lo,hi in reg['windows']:
        ix=(grid>=lo)&(grid<=hi);t=grid[ix]
        free=float(np.max(abs(om['free'][ix]-orr['free'][ix])/scales));retained=float(np.max(abs(om['retained'][ix]-orr['retained'][ix])/scales))
        bound=float(np.max(abs(om['bound'][ix]-orr['bound'][ix])/bsc));occ=float(np.max(abs(om['occupancy'][ix]-orr['occupancy'][ix])/E))
        flow=float(np.max(abs(om['net_extent'][ix]-orr['net_extent'][ix]))/case['cumulative_extent_scale'])
        fr=rms(t,(vn-vr)[ix])/flux_scale
        conc_unc=max(float(np.max(abs(mt['free'][ix]-om['free'][ix])/scales)),float(np.max(abs(mb['free'][ix]-om['free'][ix])/scales)),float(np.max(abs(rt['free'][ix]-orr['free'][ix])/scales)),
                     float(np.max(abs(mt['retained'][ix]-om['retained'][ix])/scales)),float(np.max(abs(mb['retained'][ix]-om['retained'][ix])/scales)),float(np.max(abs(rt['retained'][ix]-orr['retained'][ix])/scales)))
        flow_unc=max(float(np.max(abs(mt['net_extent'][ix]-om['net_extent'][ix]))),float(np.max(abs(mb['net_extent'][ix]-om['net_extent'][ix]))),float(np.max(abs(rt['net_extent'][ix]-orr['net_extent'][ix]))))/case['cumulative_extent_scale']
        flux_unc=max(rms(t,(mt['current'][:,0]-mt['current'][:,1]-vn)[ix]),rms(t,(mb['current'][:,0]-mb['current'][:,1]-vn)[ix]),rms(t,(rt['current'][:,0]-rt['current'][:,1]-vr)[ix]))/flux_scale
        windows.append({'window':[lo,hi],'max_scaled_free':free,'max_scaled_retained':retained,'max_scaled_bound':bound,'max_scaled_occupancy':occ,
            'normalized_net_flux_rms':fr,'max_normalized_cumulative_resource_flow':flow,'uncertainty':{'concentration':conc_unc,'flux':flux_unc,'flow':flow_unc}})
    W=windows[-1];errors={'concentration':max(W['max_scaled_free'],W['max_scaled_retained']),'flux':W['normalized_net_flux_rms'],'flow':W['max_normalized_cumulative_resource_flow']}
    thresholds={'concentration':.05,'flux':.1,'flow':.02}
    failed=[k for k in errors if errors[k]-W['uncertainty'][k]>thresholds[k]]
    uncertain=[k for k in errors if W['uncertainty'][k]>.1*thresholds[k] or (errors[k]+W['uncertainty'][k]>thresholds[k] and k not in failed)]
    minimum=float(min(np.min(micro[:,:m.n]),np.min(red[:,:m.n]),np.min(microtight[:,:m.n]),np.min(microbdf[:,:m.n]),np.min(redtight[:,:m.n])))
    if cons>1e-8:failed.append('conservation')
    if minimum < -1e-8:failed.append('negative_inventory')
    return {'id':case['id'],'initial_mode':mode,'execution_status':'COMPLETE','scientific_status':'FAILED' if failed else 'NUMERICALLY_INCONCLUSIVE' if uncertain else 'SCENARIO_GATES_PASS',
        'failed_gates':failed,'uncertain_gates':uncertain,'windows':windows,'normalized_conservation_residual':cons,'minimum_unclipped_inventory':minimum,
        'flux_scale':flux_scale,'cumulative_extent_scale':case['cumulative_extent_scale'],'initial_projection_max_free_shift':float(np.max(abs(red[0,:len(m.B)]-np.array([case['initial_original'][s] for s in m.B])))),
        'endpoint_net_extents':{'microscopic':float(om['net_extent'][-1]),'reduced':float(orr['net_extent'][-1])},
        'solver':solver,'code_provenance':reg['implementation_sha256'],'source_commit':reg['source_commit'],'source_hashes':reg['source_hashes'],
        'parameter_set':'Author simulator CSV, unmodified','initial_conditions':case,'command':sys.argv,'environment':{'python':sys.version,'platform':platform.platform()}}

def run_case(d,case,reg):
    u=next(u for u in d['units'] if u['name']==case['unit']);m=Module(d,u);grid=np.array(reg['comparison_grid']);E=case['enzyme_total']
    x0=np.array([case['initial_original'][s] for s in m.species]);T0=m.A@x0
    try:
        xp,_,_,_=m.closure(T0,E)
        roots=[];failedstarts=[]
        for f in reg['solver']['initial_multistart_fractions']:
            try: roots.append(m.closure(T0,E,T0*f)[0])
            except DomainFailure as e:failedstarts.append(str(e))
        spread=max([float(np.max(abs(x-xp))) for x in roots]+[0.])
        if spread>1e-7:raise DomainFailure('Multiple distinct physical roots from preregistered starting points')
        if np.max(m.fast_eigen(xp).real)>=-1e-8:raise DomainFailure('Initial root not locally attractive at fixed total')
    except DomainFailure as e:
        result={'id':case['id'],'execution_status':'STOPPED_AT_MATHEMATICAL_DOMAIN_CHECK','scientific_status':'BLOCKED','error':str(e),
          'failure_kind':'NO_CERTIFIED_PHYSICAL_CLOSURE','initial_conditions':case,'source_commit':reg['source_commit'],'source_hashes':reg['source_hashes'],
          'parameter_set':'Author simulator CSV','preregistration_sha256':sha(REG),'command':sys.argv}
        write_json(OUT/'numerical'/case['id']/'domain_failure.json',result)
        print(json.dumps({'case':case['id'],'status':'BLOCKED','reason':str(e)}),flush=True)
        return
    base_red,curr,rs=integrate_reduced(m,T0,E,grid,1e-8,1e-10)
    tight_red,_,rts=integrate_reduced(m,T0,E,grid,1e-10,1e-12)
    for mode in case['initial_modes']:
        path=OUT/'numerical'/case['id']/mode
        try:
            initial=x0 if mode=='ORIGINAL_NONEQUILIBRIUM' else xp
            base,bs=integrate_micro(m,initial,grid,1e-8,1e-10,'Radau')
            tight,ts=integrate_micro(m,initial,grid,1e-10,1e-12,'Radau')
            bdf,bds=integrate_micro(m,initial,grid,1e-10,1e-12,'BDF')
            result=compare(m,case,mode,reg,grid,base,tight,bdf,base_red,tight_red,{'reference':bs,'reference_tight':ts,'independent_BDF':bds,'candidate':rs,'candidate_tight':rts,'initial_multistart_root_spread':spread,'failed_multistart_seeds':failedstarts})
            path.mkdir(parents=True,exist_ok=True)
            trajectory=path/'trajectories.npz'
            np.savez_compressed(trajectory,time=grid,species=np.array(m.species),reaction_ids=np.array([m.reactions[j]['id'] for j in m.active]),
                microscopic=base,microscopic_tight=tight,microscopic_independent_bdf=bdf,reduced=base_red,reduced_tight=tight_red,
                microscopic_active_flux=observations(m,base)['all_active_source_flux'],reconstructed_active_flux=observations(m,base_red)['all_active_source_flux'],
                net_stoichiometry=m.N,total_mapping=m.A,bound_mapping=m.C)
            result['trajectory']={'path':str(trajectory.relative_to(ROOT)).replace('\\','/'),'sha256':sha(trajectory),'quadrature_columns':['forward_extent','reverse_extent']}
            result['preregistration_sha256']=sha(REG)
            write_json(path/'metrics.json',result)
            print(json.dumps({'case':case['id'],'mode':mode,'status':result['scientific_status'],'failed':result['failed_gates'],'long':result['windows'][-1]}),flush=True)
        except Exception as e:
            write_json(path/'failure.json',{'id':case['id'],'initial_mode':mode,'execution_status':'FAILED','scientific_status':'BLOCKED','error':str(e),'traceback':traceback.format_exc(),'preregistration_sha256':sha(REG),'source_commit':reg['source_commit'],'initial_conditions':case})
            print(json.dumps({'case':case['id'],'mode':mode,'status':'BLOCKED','reason':str(e)}),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--unit',required=True);p.add_argument('--case');args=p.parse_args()
    reg=json.loads(REG.read_text());freeze=json.loads((OUT/'preregistration_freeze.json').read_text())
    if sha(REG)!=freeze['sha256']:raise RuntimeError('Frozen registration changed')
    for f,v in reg['implementation_sha256'].items():
        if sha(ROOT/f)!=v:raise RuntimeError('Candidate code changed after freeze: '+f)
    d=json.loads((OUT/'source_inventory.json').read_text())
    for case in reg['scenarios']:
        if case['unit']!=args.unit or args.case and case['condition']!=args.case:continue
        destination=OUT/'numerical'/case['id']
        if destination.exists():raise RuntimeError('Refusing to replace existing numerical evidence: '+case['id'])
        start=time.monotonic()
        try:run_case(d,case,reg)
        except Exception as e:
            write_json(destination/'failure.json',{'id':case['id'],'execution_status':'FAILED','scientific_status':'BLOCKED','error':str(e),'traceback':traceback.format_exc(),'preregistration_sha256':sha(REG),'source_commit':reg['source_commit'],'initial_conditions':case})
            print(json.dumps({'case':case['id'],'status':'BLOCKED','reason':str(e)}),flush=True)
        print(json.dumps({'case':case['id'],'wall_seconds':time.monotonic()-start}),flush=True)

if __name__=='__main__':main()
