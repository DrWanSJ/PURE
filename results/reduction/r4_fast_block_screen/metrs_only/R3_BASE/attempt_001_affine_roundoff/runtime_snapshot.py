"""Separate partial-family R4 runtime; canonical R1/R3 files are read only."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',OMP_NUM_THREADS='1')
import csv,json,hashlib,time,math
from pathlib import Path
import numpy as np
from scipy.optimize import root
from r3_resource_total_runtime_v2 import R3ResourceTotalRuntimeV2
from runtime_reconstruction_rhs import SourceCoordinateRuntime
from validate_source_coordinates_full_v1 import source_matrix,lift_matrix,rate_jacobian,rate_vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/reduction/r4_fast_block_screen'
DOC=ROOT/'docs/reduction'
REG=json.loads((DOC/'r4_fast_block_candidates_v1.json').read_text())
TIMES=np.r_[0.,np.geomspace(1e-4,1000,200)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p,v):
 Path(p).parent.mkdir(parents=True,exist_ok=True)
 Path(p).write_text(json.dumps(v,indent=2,allow_nan=True)+'\n',encoding='utf-8',newline='\n')
def write_csv(p,rows):
 Path(p).parent.mkdir(parents=True,exist_ok=True)
 with Path(p).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def condition_initial(source,condition):
 c=next(c for c in REG['conditions'] if c['condition_id']==condition)
 scales=json.loads(c['initial_scale_json'])
 return np.array([float(source.author_initial[n])*scales.get(n,1) for n in source.species])
def historical_path(condition):
 base=ROOT/'results/reduction/r3_aminoacylation_qssa'
 return base/json.loads((base/'run_001/attempt_map.json').read_text())[condition]
def source_data(condition):
 with np.load(historical_path(condition)/'full_state.npz') as a:return a['times'].copy(),a['state'].copy()

class R4FamilyRuntime(R3ResourceTotalRuntimeV2):
 def __init__(self,family):
  self.family=family;self.source=SourceCoordinateRuntime('source_coordinate_certificate_v4.json')
  s=self.source;self.chart=json.loads((DOC/'r3_carrier_chart_v1.json').read_text())
  self.q_names=REG['candidates']['R4_'+family.upper()+'_ONLY']['fast_species']
  partition=json.loads((ROOT/'docs/audit/pnas2017_aminoacylation_reduction_v1/candidate_partition.json').read_text())
  assert self.q_names==partition[family]['eliminated']
  self.q_index=np.array([s.index[n] for n in self.q_names]);qset=set(self.q_index)
  self.carrier_names=self.chart['carrier_species'];self.carrier_index=np.array([s.index[n] for n in self.carrier_names])
  self.slow_index=np.array([i for i in s.r_index if i not in qset]);self.slow_position={i:p for p,i in enumerate(self.slow_index)}
  self.retained_position={i:p for p,i in enumerate(s.r_index)}
  self.C=np.array([[float(row.get(n,0)) for n in self.q_names] for row in self.chart['carrier_delta_per_fast_delta_rows']])
  self.S=source_matrix(s);self.L=lift_matrix(s).toarray()
  self.D=np.zeros((241,len(qset)));self.D[self.q_index,np.arange(len(qset))]=1;self.D[self.carrier_index]=self.C
  self.Xz=self.L[:,[self.retained_position[i] for i in self.slow_index]].copy()
  self.T=np.zeros((len(self.slow_index),241));self.T[np.arange(len(self.slow_index)),self.slow_index]=1
  for row,i in enumerate(self.carrier_index):self.T[self.slow_position[i],self.q_index]-=self.C[row]
  rows={r['row']:r for r in csv.DictReader((ROOT/'docs/audit/pnas2017_aminoacylation_reduction_v1/binit_v1r2_matrix.csv').open())}
  self.a=np.array([float(rows['adenine_moiety_total'][n]) for n in self.q_names])
  self.p=np.array([float(rows['declared_phosphate_equivalent_total'][n]) for n in self.q_names]);self.k=(self.p-3*self.a)/2
  self.atp=s.index['ATP'];self.amp=s.index['AMP'];self.ppi=s.index['PPi']
  self.atp_pos=self.slow_position[self.atp];self.amp_pos=self.slow_position[self.amp];self.ppi_pos=self.slow_position[self.ppi]
  self.D[self.atp]=-self.a;self.D[self.ppi]=-self.k
  self.Xz[self.atp,self.amp_pos]=-1;self.Xz[self.ppi,self.amp_pos]=1
  self.T[self.atp_pos,self.amp]=1;self.T[self.atp_pos,self.q_index]=self.a
  self.T[self.ppi_pos,self.amp]=-1;self.T[self.ppi_pos,self.q_index]=self.k
  self.fast_reactions=np.array(sorted({j for i in self.q_index for j,_ in s.source_rows[i]}))
  self.Sq=self.S[self.q_index][:,self.fast_reactions].toarray()
  for label in ('adenine_moiety_total','declared_phosphate_equivalent_total'):
   weights=np.array([float(rows[label][n]) for n in s.species]);assert np.max(abs(weights@self.S[:,self.fast_reactions]))==0
  self.TS=np.asarray(self.T@self.S);self.ts_rows=[[(j,float(v)) for j,v in enumerate(row) if v] for row in self.TS]
  self._last_root=None
  assert np.max(abs(self.T@self.D))==0 and np.max(abs(self.T@self.Xz-np.eye(len(self.slow_index))))==0
  assert np.max(abs(self.L@self.D[s.r_index]-self.D))==0
  self.W=np.vstack((self.T[:,s.r_index],np.eye(214)[[self.retained_position[i] for i in self.q_index]]))
  self.Wi=np.column_stack((self.Xz[s.r_index],self.D[s.r_index]));assert np.max(abs(self.W@self.Wi-np.eye(214)))==0
  # Vectorized original monomials, with independent source-row checks downstream.
  specs=[s.rate_specs[j] for j in self.fast_reactions];self.fk=np.array([v[0] for v in specs]);width=max(len(v[1]) for v in specs)
  self.fi=np.full((len(specs),width),241,int)
  for j,(_,factors) in enumerate(specs):self.fi[j,:len(factors)]=factors
  self.Dpad=np.vstack((self.D,np.zeros((1,len(qset)))))
 def initial_slow(self,x):return self.T@np.asarray(x)
 def reconstruct(self,z,q,x0):
  # Exact affine chart anchored to the same physical inventories.
  return np.asarray(x0)+self.Xz@(np.asarray(z)-self.T@x0)+self.D@(np.asarray(q)-np.asarray(x0)[self.q_index])
 def fast_rows(self,z,q,x0,with_jacobian=False):
  x=self.reconstruct(z,q,x0);vals=np.r_[x,1.][self.fi];rates=self.fk*np.prod(vals,axis=1);G=self.Sq@rates
  if not with_jacobian:return G,x
  dv=np.zeros((len(rates),len(q)))
  for k in range(vals.shape[1]):
   other=np.prod(np.delete(vals,k,axis=1),axis=1)
   dv+=(self.fk*other)[:,None]*self.Dpad[self.fi[:,k]]
  return G,self.Sq@dv,x
 def solve_fast(self,z,x0,seed=None):
  # Five fixed Newton steps with tighter internal precision; target remains <=1e-10.
  if seed is None:seed=self._last_root
  if seed is None:seed=np.asarray(x0)[self.q_index]
  q=np.array(seed,copy=True)
  for step in range(5):
   G,J,x=self.fast_rows(z,q,x0,True)
   try:d=np.linalg.solve(J,-G)
   except np.linalg.LinAlgError:break
   if np.max(abs(G))<=1e-13 and np.max(abs(d))<=1e-13:
    cond=float(np.linalg.cond(J));physical=min(np.min(q),np.min(x[self.carrier_index]),x[self.atp],x[self.amp],x[self.ppi])>=-1e-12
    if cond<1e12 and physical:
     self._last_root=q.copy()
     return {'q':q,'state':x,'residual':G,'residual_max':float(np.max(abs(G))),'min_q':float(np.min(q)),'min_carrier':float(np.min(x[self.carrier_index])),'min_resource':float(min(x[self.atp],x[self.amp],x[self.ppi])),'physical':True,'valid_local_root':True,'Gq_condition_number':cond,'newton_correction_max_abs':float(np.max(abs(d))),'method':'warm_start_newton','message':'fixed Newton precision','nfev':step+1}
   q+=d
  return super().solve_fast(z,x0,seed=seed)
 def slow_rhs(self,z,q,x0):
  x=self.reconstruct(z,q,x0);v=rate_vector(self.source,x)
  return np.array([math.fsum(c*v[j] for j,c in row) for row in self.ts_rows]),v,x
 def slow_jacobian(self,z,q,x0):
  x=self.reconstruct(z,q,x0);J=(self.S@rate_jacobian(self.source,x)).toarray();Gq=J[self.q_index]@self.D;Gz=J[self.q_index]@self.Xz;Dh=-np.linalg.solve(Gq,Gz)
  return self.T@J@(self.Xz+self.D@Dh),{'Gq_condition_number':float(np.linalg.cond(Gq))}

class NumericalBound(RuntimeError):pass
def guarded(clock,calls,wall,rhs_limit):
 if time.monotonic()-clock>wall:raise NumericalBound('PREREGISTERED_WALL_BOUND')
 if calls>rhs_limit:raise NumericalBound('PREREGISTERED_RHS_CALL_BOUND')
