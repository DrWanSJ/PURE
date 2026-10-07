"""CK partial-equilibrium projected slow flow in the exact R1 class."""
from r5_common_v1 import *
from runtime_reconstruction_rhs import SourceCoordinateRuntime
from validate_source_coordinates_full_v1 import source_matrix,lift_matrix,rate_vector,rate_jacobian
from scipy.optimize import brentq
from scipy.sparse import csc_matrix
import sympy as sp
FAST_IDS=['re0000000332','re0000000333','re0000000336','re0000000337']
NAMES=['CK','CK_ADP','CP','CK_CP','CK_CP_ADP']
def material_root(T0,T1,B,K0=500.,K1=500.,solver_extension=False):
 # Stable quadratic form for equal K, no subtraction of nearly equal roots.
 if min(T0,T1,B)<0 and not solver_extension:raise ValueError('NONPHYSICAL_FAST_TOTALS')
 if K0==K1:
  a=K0+T0+T1-B;d=math.hypot(a,2*math.sqrt(B*K0))
  p=2*B*K0/(d+a) if a>=0 else (d-a)/2
 else:p=brentq(lambda p:p+T0*p/(K0+p)+T1*p/(K1+p)-B,0,B,xtol=1e-13)
 return p,np.array([T0*p/(K0+p),T1*p/(K1+p)])
def fast_rhs(q,totals,kon=2.,koff=1000.):
 T0,T1,B=totals;p=B-q.sum();return kon*p*(np.array([T0,T1])-q)-koff*q
def fast_jac(q,totals,kon=2.,koff=1000.):
 T0,T1,B=totals;p=B-q.sum();free=np.array([T0,T1])-q
 return -(kon*p+koff)*np.eye(2)-kon*free[:,None]*np.ones((1,2))
class CKRuntime:
 def __init__(self):
  self.source=SourceCoordinateRuntime('source_coordinate_certificate_v4.json');s=self.source
  self.S=source_matrix(s);self.L=lift_matrix(s).toarray();self.x0=np.array([float(s.author_initial[n]) for n in s.species]);self.y0=self.x0[s.r_index]
  self.fast=np.array([next(j for j,r in enumerate(s.reactions) if r['id']==rid) for rid in FAST_IDS]);assert [s.rate_specs[j][0] for j in self.fast]==[2,1000,2,1000]
  self.ix=np.array([s.index[n] for n in NAMES]);self.qix=self.ix[3:]
  totals=np.zeros((3,241));totals[0,self.ix[[0,3]]]=1;totals[1,self.ix[[1,4]]]=1;totals[2,self.ix[[2,3,4]]]=1
  # Preserve the frozen R1 chart wherever possible: unaffected retained rows
  # precede unaffected reconstructed rows in selecting a fast-invariant basis.
  other=[i for i in s.r_index+s.e_index if i not in self.ix];lf=np.vstack([totals,np.eye(241)[other]])
  assert np.max(abs(lf@self.S[:,self.fast]))==0
  # Full left-null basis has 239 rows; restriction to R1's 214 class has rank212.
  A=lf@self.L;_,pivots=sp.Matrix(A.T.astype(int)).rref();self.selected=list(pivots);assert len(pivots)==212 and list(pivots[:3])==[0,1,2]
  self.Lf=lf;self.T=lf[self.selected];self.labels=[['T0','T1','B'][i] if i<3 else s.species[other[i-3]] for i in self.selected]
  W=np.vstack([self.T@self.L,self.L[self.qix]]);self.W=W
  Wi=np.array(sp.Matrix(W.astype(int)).inv(),dtype=float)
  self.Xz=self.L@Wi[:,:212];self.D=self.L@Wi[:,212:];self.offset=self.x0-self.Xz@(self.T@self.x0)-self.D@self.x0[self.qix]
  self.affine_terms=[[(j,float(v)) for j,v in enumerate(row) if v] for row in self.Xz]
  assert np.max(abs(self.T@self.D))==0 and np.max(abs(self.T@self.Xz-np.eye(212)))==0
  self.TS=np.asarray(self.T@self.S);self.TS[:,self.fast]=0
  self.ts_rows=[[(j,float(v)) for j,v in enumerate(row) if v] for row in self.TS]
  self.Sslow=self.S.copy().tolil();self.Sslow[:,self.fast]=0;self.Sslow=self.Sslow.tocsc()
  self.k=np.array([p for p,f in s.rate_specs]);self.factors=[f for p,f in s.rate_specs]
  self.ri=np.full((968,max(map(len,self.factors))),241,int)
  for j,f in enumerate(self.factors):self.ri[j,:len(f)]=f
  self.z0=self.T@self.x0
 def rates(self,x,eta=1):
  v=self.k*np.prod(np.r_[x,1.][self.ri],axis=1);v[self.fast]/=eta;return v
 def affine(self,z,q):
  # Same affine coordinate map with correctly rounded row summation. No
  # trajectory projection or physical clipping occurs here.
  x=np.array([math.fsum([self.offset[i]]+[v*z[j] for j,v in row]+[v*q[j] for j,v in enumerate(self.D[i]) if v]) for i,row in enumerate(self.affine_terms)])
  # Set the five physical fast entries directly from their coordinates, avoiding
  # subtraction of large full-network conservation offsets for bound CK_CP.
  p=z[2]-q.sum();x[self.ix]=[z[0]-q[0],z[1]-q[1],p,q[0],q[1]]
  return x
 def manifold(self,z,derivative=False):
  p,q=material_root(*z[:3],solver_extension=True);x=self.affine(z,q);x[self.ix[2]]=p
  if not derivative:return x,q
  T0,T1,B=z[:3];a=p/(500+p);H=1+(T0+T1)*500/(500+p)**2;dp=np.array([-a,-a,1])/H
  dh=np.zeros((2,212));dh[:,:3]=np.array([[a,0,0],[0,a,0]])+np.array([T0,T1])[:,None]*500/(500+p)**2*dp[None,:]
  return x,q,self.Xz+self.D@dh,dh
 def manifold_delta(self,dz,derivative=False):
  z=self.z0+dz;p,q=material_root(*z[:3],solver_extension=True)
  dq=q-self.x0[self.qix]
  x=np.array([math.fsum([self.x0[i]]+[v*dz[j] for j,v in row]+[v*dq[j] for j,v in enumerate(self.D[i]) if v]) for i,row in enumerate(self.affine_terms)])
  x[self.ix]=[z[0]-q[0],z[1]-q[1],p,q[0],q[1]]
  if not derivative:return x,q
  _,_,phi,dh=self.manifold(z,True);return x,q,phi,dh
 def reduced_rhs_delta(self,t,dz):
  x,q=self.manifold_delta(dz);v=self.rates(x);return np.array([math.fsum(c*v[j] for j,c in row) for row in self.ts_rows])
 def reduced_jac_delta(self,t,dz):
  x,q,phi,dh=self.manifold_delta(dz,True);return csc_matrix(self.TS@rate_jacobian(self.source,x)@phi)
 def reduced_rhs(self,t,z):
  x,q=self.manifold(z);v=self.rates(x);return np.array([math.fsum(c*v[j] for j,c in row) for row in self.ts_rows])
 def reduced_jac(self,t,z):
  x,q,phi,dh=self.manifold(z,True);return csc_matrix(self.TS@rate_jacobian(self.source,x)@phi)
 def full_rhs(self,t,x,eta):return np.array(self.source.full_rhs_from_rates(self.rates(x,eta)))
 def full_jac(self,t,x,eta):
  vj=rate_jacobian(self.source,x).tolil();vj[self.fast,:]/=eta;return self.S@vj.tocsc()
 def redistribution(self,z):
  x,q,phi,dh=self.manifold(z,True);v=self.rates(x);F=self.TS@v
  needed=dh@F-np.asarray(self.Sslow@v)[self.qix]
  # First-order signed pair-net redistribution in concentration per second.
  return needed
