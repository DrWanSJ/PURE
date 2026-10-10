"""Source mass-action runtime, exact affine charts and two explicit topology closures.

No reference trajectory is an input to a reduced model. Counters are integrated by
that model. The recycling quotient returns a representative, not lost microstates.
"""
import time
from fractions import Fraction as F
import numpy as np
from scipy.sparse import csr_matrix,csc_matrix,vstack
from scipy.integrate import solve_ivp
from numba import njit
from threadpoolctl import threadpool_limits
from common import *
from mathematics import TAIL,TAIL_NAMES,CHAIN,matrix_source,laws_data
threadpool_limits(1)

def sparse_rows(rows,ncols):
    ii=[];jj=[];vv=[]
    for i,row in enumerate(rows):
        for j,n in row.items():ii.append(i);jj.append(int(j));vv.append(float(F(n)))
    return csr_matrix((vv,(ii,jj)),shape=(len(rows),ncols))

@njit
def mv(data,indices,indptr,x):
    y=np.zeros(len(indptr)-1)
    for i in range(len(y)):
        total=0.;corr=0.
        for p in range(indptr[i],indptr[i+1]):
            a=data[p]*x[indices[p]]-corr;b=total+a;corr=(b-total)-a;total=b
        y[i]=total
    return y

@njit
def rates(x,k,factors,counts):
    v=k.copy()
    for j in range(len(k)):
        for p in range(counts[j]):v[j]*=x[factors[j,p]]
    return v

@njit
def rate_derivatives(x,k,factors,counts):
    out=np.zeros((len(k),241))
    for j in range(len(k)):
        for p in range(counts[j]):
            a=k[j]
            for q in range(counts[j]):
                if q!=p:a*=x[factors[j,q]]
            out[j,factors[j,p]]+=a
    return out

def smv(A,x):return mv(A.data,A.indices,A.indptr,x)

class Runtime:
    def __init__(self,model,scenario):
        self.model=model;self.scenario=scenario;self.names,self.rx,self.initial=source_network();self.index={s:i for i,s in enumerate(self.names)}
        self.S=csr_matrix(np.asarray(matrix_source(self.names,self.rx).tolist(),dtype=float));self.config=load(CONFIG);self.charts=load(RESULT/'charts.json')
        self.x0=np.array([float(self.initial[s]) for s in self.names])
        for s,n in scenario['initial_overrides'].items():self.x0[self.index[s]]=float(F(n))
        self.ks=np.array([float(r['k']) for r in self.rx])
        for rid,k in scenario['parameter_overrides'].items():self.ks[next(i for i,r in enumerate(self.rx) if r['id']==rid)]=float(F(k))
        self.chart=None if model=='R0' else self.charts[model]
        self.tail=None if not self.chart else self.chart.get('tail');self.chain=[] if not self.chart else self.chart.get('chain_rounds',[])
        if model not in ('R0','R1') and scenario['parameter_overrides']:raise ValueError('AUTHOR_ZERO_PATTERN_DOMAIN: R2/R3 chart blocked for parameter reactivation')
        if model=='R0':
            self.P=csr_matrix(np.eye(241));self.Hsource=self.P;self.C=self.P;self.ret=list(range(241));self.labels=self.names;self.L=laws_data(self.names,'SOURCE_GENERAL')[1]
        else:
            c=self.chart;self.labels=c['physical_labels'];nphys=c['physical_dimension'];self.ret=c['retained_indices']
            self.C=sparse_rows(c['lift_sparse_rows'],c['dimension'])
            self.P=sparse_rows(c['source_projection_sparse_rows'],241) if model!='R1' else csr_matrix(np.eye(241))
            self.Hsource=sparse_rows(c['source_lift_sparse_rows'],nphys) if model!='R1' else csr_matrix(np.eye(241))
            self.L=sparse_rows(c['L_sparse_rows'],nphys)
        self.y0=smv(self.P,self.x0);self.z0=self.y0[self.ret];self.dim=len(self.ret)
        self.yconst=self.y0-smv(self.C,self.z0);self.sourceC=(self.Hsource@self.C).tocsr();self.sourceconst=smv(self.Hsource,self.yconst)
        if np.min(self.y0)<-1e-9:raise ValueError('PROJECTED_INITIAL_DOMAIN_NEGATIVE '+str(np.min(self.y0)))
        if self.chart and model!='R1':
            support_indices={self.index[s] for s in self.charts['R2']['physical_labels']}
            if any(self.x0[i]!=0 for i in range(241) if i not in support_indices):raise ValueError('INITIAL_SUPPORT_DOMAIN')
        self.counter_names,self.M=self.counter_matrix();self.nc=len(self.counter_names)
        eligible=list(np.flatnonzero(self.ks>0)) if model in ('R0','R1') else self.chart['live_reaction_indices']
        tail_ids=[] if not self.tail else self.chart['tail_rate_indices']
        self.live=[j for j in eligible if j not in tail_ids]
        self.k=self.ks[self.live];self.factors=np.full((len(self.live),4),-1,dtype=np.int64);self.counts=np.zeros(len(self.live),dtype=np.int64)
        for j,orig in enumerate(self.live):
            fac=[self.index[s] for s in self.rx[orig]['factors'] if s!='k1']
            for round_ in self.chain:
                c=CHAIN[round_-1]
                if self.rx[orig]['id'] in c['ids']:fac=[self.index[c['slow']]];self.k[j]=float(F(c['k']))
            assert len(fac)<=4;self.factors[j,:len(fac)]=fac;self.counts[j]=len(fac)
        self.Nphysical=(self.P@self.S[:,self.live]).tocsr();self.N=vstack([self.Nphysical[self.ret,:],self.M[:,self.live]]).tocsr()
        unique={};groups=[];keep=[]
        for j in range(len(self.live)):
            key=(self.k[j],tuple(self.factors[j,:self.counts[j]]))
            if key not in unique:unique[key]=len(keep);keep.append(j)
            groups.append(unique[key])
        G=csr_matrix((np.ones(len(groups)),(np.arange(len(groups)),groups)),shape=(len(groups),len(keep)))
        self.N=(self.N@G).tocsr();self.k=self.k[keep];self.factors=self.factors[keep];self.counts=self.counts[keep]
        self.K=csr_matrix((self.dim+self.nc,self.dim));self.kconst=np.zeros(self.dim+self.nc)
        self.tail_counter_proof=True
        if self.tail:
            from mathematics import rational_matrix
            import sympy as sp
            block=rational_matrix(self.tail['source_projection_rows']);right=rational_matrix(self.tail['right_inverse_rows'])
            D=sp.zeros(len(tail_ids),7)
            for j,rid in enumerate(tail_ids):
                s=next(s for s in self.rx[rid]['factors'] if s!='k1');D[j,TAIL.index(s)]=sp.Rational(str(self.rx[rid]['k']))
            Mtail=sp.Matrix(self.M[:,tail_ids].toarray().astype(int).tolist())*D
            assert Mtail==Mtail*right*block
            Qcount=np.array((Mtail*right).tolist(),dtype=float)
            Qphys=sparse_rows(self.chart['tail_projected_rhs_sparse_rows'],5)
            Q=vstack([Qphys[self.ret,:],csr_matrix(Qcount)]).tocsr();offset=self.tail['physical_offset'];self.K=(Q@self.C[offset:,:]).tocsr();self.kconst=smv(Q,self.yconst[offset:])
        self.aug0=np.r_[self.z0,np.zeros(self.nc)]
        # Warm compilation is explicitly excluded from solver wall time for all models.
        self.rhs(0,self.aug0);self.jac(0,self.aug0)
    def counter_matrix(self):
        names=[];rows_=[]
        for s in ['Pept0003','ATP','ADP','AMP','GTP','GDP','PO4','PPi','CP']:
            names.append('NET_'+s);rows_.append(self.S[self.index[s],:].toarray()[0])
        for side,s in [('reactants','ATP'),('reactants','GTP'),('products','GDP'),('products','PO4'),('products','PPi'),('products','EFG_GDP'),('products','RRF'),('products','tRNAGlyGCC'),('products','RS50S')]:
            names.append(('CONSUMED_' if side=='reactants' else 'RELEASED_')+s);rows_.append([float(r[side].get(s,0)) for r in self.rx])
        for rid in ['re0000000018','re0000000079']:
            names.append('RESIDUE_'+rid);rows_.append([int(r['id']==rid) for r in self.rx])
        return names,csr_matrix(np.asarray(rows_,dtype=float))
    def physical(self,z):return self.yconst+smv(self.C,z[:self.dim])
    def reconstruct_full(self,z):
        y=self.physical(z);x=smv(self.Hsource,y)
        if self.tail:
            a,b,t,r,e=y[self.tail['physical_offset']:];lower=np.maximum(0,np.array([a+b-e,a+b-r,a+b-t]));rest=(b-np.sum(lower))/3
            if rest < -1e-9:raise ValueError('TAIL_NONNEGATIVE_REPRESENTATIVE_INFEASIBLE '+str(rest))
            tr,te,re_=lower+rest
            vals=[a,tr,te,re_,t-a-tr-te,r-a-tr-re_,e-a-te-re_]
            for s,v in zip(TAIL,vals):x[self.index[s]]=v
        return x
    def rhs_reduced(self,t,z):return self.rhs(t,z)
    def rhs(self,t,z):
        x=self.sourceconst+smv(self.sourceC,z[:self.dim]);v=rates(x,self.k,self.factors,self.counts)
        return smv(self.N,v)+smv(self.K,z[:self.dim])+self.kconst
    def jac(self,t,z):
        x=self.sourceconst+smv(self.sourceC,z[:self.dim]);Jrate=csr_matrix(rate_derivatives(x,self.k,self.factors,self.counts))
        J=(self.N@Jrate@self.sourceC+self.K).tocoo()
        return csc_matrix((J.data,(J.row,J.col)),shape=(self.dim+self.nc,self.dim+self.nc))
    def source_rates(self,x):
        v=np.zeros(968)
        for j,r in enumerate(self.rx):
            a=self.ks[j]
            for s in r['factors']:
                if s!='k1':a*=x[self.index[s]]
            v[j]=a
        for round_ in self.chain:
            c=CHAIN[round_-1];a=float(F(c['k']))*x[self.index[c['slow']]]
            for rid in c['ids']:v[next(i for i,r in enumerate(self.rx) if r['id']==rid)]=a
        return v
    def simulate(self,settings=None):
        settings=settings or self.config['solver'];t=np.array(self.config['observation_grid']);start=time.perf_counter()
        sol=solve_ivp(self.rhs,(0,1000),self.aug0,method=settings['method'],rtol=settings['rtol'],atol=settings['atol'],jac=self.jac,t_eval=t,dense_output=True)
        elapsed=time.perf_counter()-start
        X=np.array([self.reconstruct_full(z) for z in sol.y.T]).T;Y=np.array([self.physical(z) for z in sol.y.T]).T
        Ctr=sol.y[self.dim:];V=np.array([self.source_rates(x) for x in X.T]).T;currents=self.M@V
        L=self.L.toarray() if hasattr(self.L,'toarray') else np.array(self.L.tolist(),dtype=float)
        mesh=sol.sol.ts;mesh_z=sol.sol(mesh);mesh_Y=np.array([self.physical(z) for z in mesh_z.T]).T;mesh_X=np.array([self.reconstruct_full(z) for z in mesh_z.T]).T
        drift=max(np.max(np.abs(L@(Y-self.y0[:,None]))),np.max(np.abs(L@(mesh_Y-self.y0[:,None]))))
        diagnostics={'model':self.model,'scenario':self.scenario['id'],'success':bool(sol.success),'message':sol.message,'final_time':float(sol.t[-1]),'chemical_dimension':self.dim,'extra_counter_dimension':self.nc,'physical_coordinate_count':len(self.labels),'positive_source_parameter_directions':int(np.sum(self.ks>0)),'evaluated_mass_action_expressions':len(self.k),'source_mapping_directions':len(self.live)+(0 if not self.tail else len(self.chart['tail_rate_indices'])),'tail_linear_coordinates':5 if self.tail else 0,'jacobian_nnz_at_initial':int(self.jac(0,self.aug0).nnz),'jacobian_nnz_at_final':int(self.jac(sol.t[-1],sol.y[:,-1]).nnz),'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu,'seconds':elapsed,'solver':settings,'minimum_source_representative':float(X.min()),'minimum_physical':float(Y.min()),'max_conservation_abs':float(drift),'tail_microstate_reconstruction':'NONUNIQUE_REPRESENTATIVE' if self.tail else 'SOURCE_EXACT_OR_CHAIN_FAST_ZERO_APPROXIMATION','tail_protected_counter_closure':self.tail_counter_proof}
        diagnostics['minimum_source_representative']=float(min(X.min(),mesh_X.min()));diagnostics['minimum_physical']=float(min(Y.min(),mesh_Y.min()));diagnostics['accepted_solver_mesh_points']=len(mesh)
        return {'t':sol.t,'X':X,'physical':Y,'chemical':sol.y[:self.dim],'counters':Ctr,'currents':np.asarray(currents),'accepted_mesh_times':mesh,'accepted_mesh_source':mesh_X,'diagnostics':diagnostics}

def simulate_reference(scenario,settings=None):return Runtime('R0',scenario).simulate(settings)
def simulate_reduced(model,scenario,settings=None):return Runtime(model,scenario).simulate(settings)
def rhs_reduced(runtime,t,z):return runtime.rhs_reduced(t,z)
def reconstruct_full(runtime,z):return runtime.reconstruct_full(z)

def observable_matrix(names):
    index={s:i for i,s in enumerate(names)};rows_=[];labels=[];kinds=[]
    for s in ['Pept0003','ATP','ADP','AMP','GTP','GDP','PO4','PPi','CP','RS30S','RS50S','RF1','RF2','RF3','RF3_GDP','RF3_GTP','EFTu','EFTu_GDP','EFG','EFG_GDP','RRF','tRNAGlyGCC','GlytRNAGlyGCC','tRNAfMetCAU','MettRNAfMetCAU','fMettRNAfMetCAU','EFTu_GTP','EFG_GTP','RS70S']:
        labels.append(s);row=np.zeros(len(names));row[index[s]]=1;rows_.append(row);kinds.append('peptide' if s=='Pept0003' else 'resource')
    for role in ['RF1','RF2','RF3','EFTu','EFG','RRF','tRNAGlyGCC','tRNAfMetCAU']:
        labels.append('BOUND_'+role);rows_.append([int(role in s and not s.startswith(role) and not s.endswith('_degraded')) for s in names]);kinds.append('resource')
    labels+=['OCCUPIED_30S','OCCUPIED_50S'];kinds+=['resource','resource']
    rows_+=[[int(('RS70S' in s or 'RS30S' in s) and s not in ['RS30S','RS70S','RS30S_degraded']) for s in names],[int(('RS70S' in s or 'RS50S' in s) and s not in ['RS50S','RS70S','RS50S_degraded']) for s in names]]
    return labels,np.array(rows_,float),kinds

def fixed_scales(rt,labels):
    x=rt.x0;idx=rt.index;get=lambda s:x[idx[s]];pool=lambda role:sum(x[i] for i,s in enumerate(rt.names) if role in s and not s.endswith('_degraded'))
    rib=max(1e-3,sum(x[i] for i,s in enumerate(rt.names) if 'RS70S' in s or 'RS30S' in s))
    scale=[]
    for s in labels:
        base=s.replace('BOUND_','')
        if s=='Pept0003':v=max(1,min(get('Gly')/2,get('Met')))
        elif s in ['ATP','ADP','AMP','CP']:v=max(1,get('ATP')+get('ADP')+get('AMP'))
        elif s in ['GTP','GDP']:v=max(1,get('GTP')+get('GDP'))
        elif s=='PO4':v=max(1,get('ATP')+get('GTP')+get('PO4'))
        elif s=='PPi':v=max(1,get('Gly')+get('Met'))
        elif s.startswith('OCCUPIED_') or s in ['RS30S','RS50S','RS70S']:v=rib
        elif 'tRNA' in base:v=max(1e-3,pool('tRNAGlyGCC' if 'Gly' in base else 'tRNAfMetCAU'))
        else:v=max(1e-3,pool(base.split('_')[0]))
        scale.append(v)
    return np.array(scale)

def compare_observables(rt,reference,reduced):
    labels,O,kinds=observable_matrix(rt.names);scales=fixed_scales(rt,labels);A=O@reference['X'];B=O@reduced['X'];diff=np.abs(A-B)/scales[:,None]
    currentscale=[]
    for s in rt.counter_names:
        base=s.split('_',1)[1]
        if base.startswith('re000'):v=max(1,rt.x0[rt.index['Gly']]+rt.x0[rt.index['Met']])
        elif base in labels:v=scales[labels.index(base)]
        else:v=max(1e-3,sum(rt.x0[i] for i,n in enumerate(rt.names) if base in n.split('_') or n==base))
        currentscale.append(v)
    cs=np.array(currentscale);fdiff=(reduced['currents']-reference['currents'])/cs[:,None];cdiff=np.abs(reduced['counters']-reference['counters'])/cs[:,None]
    windows=[]
    for low,high in rt.config['windows']:
        mask=(reference['t']>=low)&(reference['t']<=high);tt=reference['t'][mask]
        rms=np.sqrt(np.trapz(fdiff[:,mask]**2,tt,axis=1)/(high-low))
        windows.append({'range':[low,high],'peptide_max':float(diff[0,mask].max()),'peptide_endpoint':float(diff[0,np.flatnonzero(mask)[-1]]),'resource_max':float(diff[1:,mask].max()),'worst_resource':labels[1+np.argmax(np.max(diff[1:,mask],axis=1))],'net_flux_rms_max':float(rms.max()),'worst_flux':rt.counter_names[int(np.argmax(rms))],'cumulative_max':float(cdiff[:,mask].max()),'worst_cumulative':rt.counter_names[int(np.argmax(np.max(cdiff[:,mask],axis=1)))]})
    d=reduced['diagnostics'];g=rt.config['gates'];long=windows[-1]
    physical=d['minimum_source_representative']>=g['negative_floor'] and d['minimum_physical']>=g['negative_floor'];conserved=d['max_conservation_abs']<=g['conservation_abs']
    numeric=all(long[k]<=g[target] for k,target in [('peptide_max','peptide'),('resource_max','resources'),('net_flux_rms_max','net_flux_rms'),('cumulative_max','cumulative')])
    # Fixed scales for source species use their source-role inventory or positive initial magnitude.
    source_scale=np.maximum(1,rt.x0)
    for i,s in enumerate(labels):
        if s in rt.index:source_scale[rt.index[s]]=scales[i]
    source_scale[rt.index['Cr']]=max(1,rt.x0[rt.index['CP']]+rt.x0[rt.index['Cr']])
    # Exact equivalence uses only numerical accuracy, never the approximate long gates.
    exact_error=float(np.max(np.abs(reference['X']-reduced['X'])/source_scale[:,None]))
    return {'windows':windows,'long_gates_pass':bool(numeric and physical and conserved and d['success']),'physical_pass':bool(physical),'conservation_pass':bool(conserved),'source_reconstruction_numeric_error':exact_error,'observable_labels':labels,'fixed_scales':dict(zip(labels,scales.tolist())),'counter_fixed_scales':dict(zip(rt.counter_names,cs.tolist())),'source_reconstruction_comparison_scope':'ALL_SOURCE_STATES' if rt.model in ['R1','R2'] else 'REPRESENTATIVE_MICROSTATES_NOT_AN_EXACT_RECOVERY','reference_endpoint_Pept0003':float(reference['X'][rt.index['Pept0003'],-1]),'reduced_endpoint_Pept0003':float(reduced['X'][rt.index['Pept0003'],-1])}
