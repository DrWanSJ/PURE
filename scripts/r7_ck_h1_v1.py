"""Analytic first-order CK graph and signed net currents in the frozen chart.

No kinetic constants, original condition values, or historical files are changed.
F=TS*v_s, G0=Q*v_s, g=2*p*(T-q)-1000*q. See registered derivation.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', OMP_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
import numpy as np
from scipy.sparse import csc_matrix
from r6_ck_common_v1 import FormalCK, ROOT, sha, load, write_json, write_csv, stamp

OUT=ROOT/'results/reduction/r7_ck_first_order'
CONDITIONS=['R3_BASE','R3_ATP_LOW','R3_TRNA_LOW']

class FirstOrderCK(FormalCK):
    def __init__(self,name):
        assert name in CONDITIONS
        super().__init__(name)
        self.Q=self.Sslow[self.qix].toarray()
        self.A=csc_matrix(self.TS)
        self.kk=self.k.copy();self.kk[self.fast]=0

    def h0(self,z):
        T=z[:2];B=z[2];a=500+T.sum()-B
        d=np.sqrt(a*a+2000*B)
        p=1000*B/(d+a) if np.real(a)>=0 else (d-a)/2
        b=p/(500+p);bp=500/(500+p)**2
        C=1+T.sum()*bp;dp=np.array([-b,-b,1])/C
        H=np.zeros((2,212),dtype=np.result_type(z,float))
        H[:,:3]=np.array([[b,0,0],[0,b,0]])+T[:,None]*bp*dp
        return p,T*b,H,dp

    def derivative_rates(self,x,dx):
        """Exact polynomial directional derivative, including repeated factors."""
        vector=dx.ndim==1
        if vector:dx=dx[:,None]
        xx=np.r_[x,1.];dd=np.vstack([dx,np.zeros((1,dx.shape[1]),dtype=dx.dtype)])
        v=np.zeros((968,dx.shape[1]),dtype=np.result_type(x,dx))
        for pos in range(self.ri.shape[1]):
            factors=xx[self.ri].copy();factors[:,pos]=1
            v+=self.kk[:,None]*np.prod(factors,axis=1)[:,None]*dd[self.ri[:,pos]]
        return v[:,0] if vector else v

    def second_rates(self,x,a,b):
        """R_xx[a,b], with all polynomial factor positions explicitly retained."""
        vector=a.ndim==1
        if vector:a=a[:,None]
        xx=np.r_[x,1.];aa=np.vstack([a,np.zeros((1,a.shape[1]))]);bb=np.r_[b,0.]
        v=np.zeros((968,a.shape[1]),dtype=np.result_type(x,a,b))
        for p in range(self.ri.shape[1]):
            for q in range(self.ri.shape[1]):
                if p==q:continue
                factors=xx[self.ri].copy();factors[:,[p,q]]=1
                v+=self.kk[:,None]*np.prod(factors,axis=1)[:,None]*aa[self.ri[:,p]]*bb[self.ri[:,q],None]
        return v[:,0] if vector else v

    def core(self,dz):
        z=self.z0+dz;p,q,H,dp=self.h0(z)
        if np.iscomplexobj(dz):x=self.x0+self.Xz@dz+self.D@(q-self.x0[self.qix])
        else:x=self.manifold_delta(dz)[0]
        v=self.kk*np.prod(np.r_[x,1.][self.ri],axis=1)
        F=self.A@v;G0=self.Q@v
        J=-(2*p+1000)*np.eye(2)-2*(z[:2]-q)[:,None]*np.ones((1,2))
        j0=H@F-G0;h1=np.linalg.solve(J,j0)
        e=self.D@h1;v1=self.derivative_rates(x,e);F1=self.A@v1
        return dict(z=z,p=p,q=q,H=H,dp=dp,x=x,v=v,F=F,G0=G0,J=J,j0=j0,h1=h1,e=e,v1=v1,F1=F1)

    def dh1(self,c,w):
        """Analytically differentiate J*h1=H*F-G0 along slow direction(s)."""
        vector=w.ndim==1
        if vector:w=w[:,None]
        p=c['p'];T=c['z'][:2];H=c['H'];dp=c['dp'];F=c['F'];h1=c['h1']
        b=p/(500+p);bp=500/(500+p)**2;bpp=-1000/(500+p)**3
        C=1+T.sum()*bp;pw=dp@w[:3]
        Cw=bp*(w[0]+w[1])+T.sum()*bpp*pw
        dDP=(np.array([-1,-1,0])[:,None]*bp*pw-dp[:,None]*Cw)/C
        dHF=bp*pw[None,:]*F[:2,None]+(w[:2]*bp+T[:,None]*bpp*pw)*(dp@F[:3])+T[:,None]*bp*(F[:3]@dDP)
        dx=self.Xz@w+self.D@(H@w)
        dv=self.derivative_rates(c['x'],dx)
        db=dHF+H@(self.A@dv)-self.Q@dv
        dJh=-2*pw[None,:]*h1[:,None]-2*(w[:2]-H@w)*h1.sum()
        result=np.linalg.solve(c['J'],db-dJh)
        return result[:,0] if vector else result

    def observables(self,dz):
        c=self.core(dz);dh=self.dh1(c,c['F'])
        j1=dh+c['H']@c['F1']-self.Q@c['v1']
        currents=self.channel_net(c['v']+c['v1'])
        currents[self.fast_channels]=c['j0']+j1
        x=c['x']+c['e']
        return x,currents,c,dh,j1

    def reduced_rhs_delta(self,t,dz):
        c=self.core(dz);return c['F']+c['F1']

    def reduced_jac_delta(self,t,dz):
        c=self.core(dz);phi=self.Xz+self.D@c['H']
        dF=self.A@self.derivative_rates(c['x'],phi)
        dh=self.dh1(c,np.eye(212))
        dF1=self.A@(self.second_rates(c['x'],phi,c['e'])+self.derivative_rates(c['x'],self.D@dh))
        return csc_matrix(dF+dF1)

def checked_binding():
    b=load(OUT/'registration_binding.json')
    for path,h in b['file_hashes'].items():assert sha(ROOT/path)==h,'R7_REGISTRATION_MUTATION:'+path
    return b
