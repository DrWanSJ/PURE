"""Independent numerical and symbolic checks of CK formulas."""
from r5_common_v1 import *
from r5_ck_partial_equilibrium_runtime_v1 import material_root,fast_rhs,fast_jac
from scipy.optimize import root,brentq
import sympy as sp
def verify():
 p,T0,T1,B,K0,K1,k,d,q0,q1=sp.symbols('p T0 T1 B K0 K1 k d q0 q1',positive=True)
 H=p+T0*p/(K0+p)+T1*p/(K1+p)-B
 assert sp.simplify(sp.diff(H,p)-(1+T0*K0/(K0+p)**2+T1*K1/(K1+p)**2))==0
 q=sp.Matrix([q0,q1]);u=sp.Matrix([T0-q0,T1-q1]);pp=B-q0-q1
 f=k*pp*u-d*q;J=f.jacobian(q);a=k*pp+d
 assert sp.simplify(J-(-a*sp.eye(2)-k*u*sp.ones(1,2)))==sp.zeros(2)
 lam=sp.symbols('lambda');assert sp.simplify(J.charpoly(lam).as_expr()-(lam+a)*(lam+a+k*(T0+T1-q0-q1)))==0
 rng=np.random.default_rng(51007);totals=np.vstack([np.array([[0,0,0],[30,0,50000],[0,30,50000],[1,2,0],[50000,50000,1]]),10**rng.uniform(-5,5,(100,3))]);records=[]
 for ts in totals:
  pp,qq=material_root(*ts);tt0,tt1,bb=ts
  h=lambda p:p+tt0*p/(500+p)+tt1*p/(500+p)-bb
  numerical=brentq(h,0,bb,xtol=1e-14) if bb else 0.;direct=root(lambda q:np.array([2*(bb-q.sum())*(tt0-q[0])-1000*q[0],2*(bb-q.sum())*(tt1-q[1])-1000*q[1]]),qq,method='hybr',options={'xtol':1e-11})
  jac=np.column_stack([(fast_rhs(qq+np.eye(2)[i]*1e-5,ts)-fast_rhs(qq-np.eye(2)[i]*1e-5,ts))/(2e-5) for i in range(2)])
  fj=fast_jac(qq,ts);analytic=np.sort([-(2*pp+1000),-(2*pp+1000+2*(tt0+tt1-qq.sum()))]);ev=np.sort(np.linalg.eigvals(fj).real)
  hh=max(1e-4,pp*1e-5);hprime=1+(tt0+tt1)*500/(500+pp)**2;numprime=(h(pp+hh)-h(pp-hh))/(2*hh)
  row={'T0':tt0,'T1':tt1,'B':bb,'p':pp,'scalar_root_absolute_difference':abs(pp-numerical),'nonlinear_root_scaled_difference':float(max(abs(direct.x-qq))/max(1,max(abs(qq)))),'fast_rhs_scaled_residual':float(max(abs(fast_rhs(qq,ts)))/max(1,1000*max(abs(qq)))),'Hprime':hprime,'Hprime_fd_relative_error':abs(hprime-numprime)/max(1,hprime),'jacobian_fd_relative_error':float(max(abs(jac-fj).ravel())/max(1,max(abs(fj).ravel()))),'eigenvalue_relative_error':float(max(abs(ev-analytic))/max(abs(analytic)))}
  assert 0<=pp<=bb*(1+1e-14)+1e-14
  assert row['fast_rhs_scaled_residual']<1e-9 and row['nonlinear_root_scaled_difference']<1e-8
  assert row['jacobian_fd_relative_error']<1e-5 and row['Hprime_fd_relative_error']<1e-5 and row['eigenvalue_relative_error']<1e-12
  records.append(row)
 # Unequal K formula and monotonicity independently checked (not repository kinetics).
 for ts in totals[5:15]:
  pp,qq=material_root(*ts,K0=200,K1=700)
  assert abs(pp+sum(qq)-ts[2])<1e-8*max(1,ts[2])
 write_csv(OUT/'ck/independent_root_crosscheck.csv',records)
 result={'status':'PASS','cases':len(records),'symbolic_Hprime':True,'symbolic_fast_Jacobian':True,'symbolic_eigenvalues':True,'max_jacobian_fd_relative_error':max(v['jacobian_fd_relative_error'] for v in records),'max_Hprime_fd_relative_error':max(v['Hprime_fd_relative_error'] for v in records)}
 write_json(OUT/'ck/critical_manifold_verification.json',result);return result
if __name__=='__main__':print(verify())
