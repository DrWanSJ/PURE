"""Prospective Branch-A CK helpers; historical runtime and inputs are read-only."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', OMP_NUM_THREADS='1')
from pathlib import Path
from fractions import Fraction
import csv, datetime, hashlib, json, math
import numpy as np
from r5_ck_partial_equilibrium_runtime_v1 import CKRuntime, material_root, FAST_IDS
from validate_source_coordinates_full_v1 import rate_jacobian

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/reduction/r6_ck_validation'
DOC = ROOT / 'docs/reduction'
TIMES = np.r_[0., np.geomspace(1e-4, 1000., 200)]
CONDITIONS = ['R3_BASE', 'R3_GLYRS_LOW', 'R3_GLYRS_HIGH', 'R3_METRS_LOW',
              'R3_METRS_HIGH', 'R3_GLY_LOW', 'R3_MET_LOW', 'R3_TRNA_LOW', 'R3_ATP_LOW']
RESOURCE_NAMES = ['ATP', 'ADP', 'AMP', 'GTP', 'GDP', 'GMP', 'CP', 'Cr', 'PPi', 'PO4',
                  'Gly', 'Met', 'fMet', 'THF', 'FD', 'mRNA', 'Pept0003', 'tRNAGlyGCC',
                  'tRNAfMetCAU', 'GlytRNAGlyGCC', 'MettRNAfMetCAU', 'fMettRNAfMetCAU']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write_json(p, data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,allow_nan=False,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def rows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
def write_csv(p, data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
def condition_record(name):
    assert name in CONDITIONS
    return next(r for r in rows(DOC/'r3_validation_grid_v1.csv') if r['condition_id']==name)
def initial(source,name):
    scale=json.loads(condition_record(name)['initial_scale_json'])
    return np.array([float(source.author_initial[n])*scale.get(n,1.) for n in source.species])
def historical_path(name):
    assert name in CONDITIONS
    base=ROOT/'results/reduction/r3_aminoacylation_qssa'
    return base/load(base/'run_001/attempt_map.json')[name]
def checked_contract():
    receipt=load(OUT/'formal_registration_binding.json')
    for p,h in receipt['file_hashes'].items(): assert sha(ROOT/p)==h, 'FROZEN_INPUT_MUTATION:'+p
    c=load(OUT/'formal_numerical_contract.json')
    assert c['mandatory_classes']==['A','B','C','D','F','H']
    assert c['conditions']==CONDITIONS and c['gross_classes_mandatory']==[]
    return c

class FormalCK(CKRuntime):
    def __init__(self,name):
        super().__init__()
        self.condition=name
        self.x0=initial(self.source,name)
        self.z0=self.T@self.x0
        self.offset=self.x0-self.Xz@self.z0-self.D@self.x0[self.qix]
        # Original condition's exact affine class, not fitted initial values.
        self.nonfast_qrows=[[(j,float(v)) for j,v in enumerate(self.Sslow.toarray()[i]) if v]
                            for i in self.qix]
        pairrows=rows(DOC/'exact_reverse_channels_v0.csv')
        ix={r['id']:j for j,r in enumerate(self.source.reactions)}
        forward={ix[r['forward_reaction_id']]:ix[r['reverse_reaction_id']] for r in pairrows}
        backwards=set(forward.values())
        self.channels=[(j,forward.get(j)) for j in range(968) if j not in backwards]
        assert len(self.channels)==678 and len(pairrows)==290
        self.N=np.column_stack([self.S[:,j].toarray().ravel() for j,_ in self.channels])
        self.fast_channels=[self.channels.index((ix[FAST_IDS[k]],ix[FAST_IDS[k+1]])) for k in [0,2]]
        self.Nqf=self.N[np.ix_(self.qix,self.fast_channels)]
        assert np.array_equal(self.Nqf,np.eye(2))
        self.channel_ids=[self.source.reactions[j]['id'] +
                          ('_MINUS_'+self.source.reactions[k]['id'] if k is not None else '_UNPAIRED')
                          for j,k in self.channels]
        resources=set(RESOURCE_NAMES)
        self.mandatory_channels=[]
        for k,(j,rev) in enumerate(self.channels):
            re=self.source.reactions[j]
            participants=set(re['reactants'])|set(re['products'])
            if k in self.fast_channels or participants&resources or any(n.startswith('CK') for n in participants):
                self.mandatory_channels.append(k)
        self.law_matrix=np.array([[float(law.get(i,0)) for i in range(241)] for law in self.source.laws])
        p,_=material_root(*self.z0[:3]);self.tau0=1/(2*p+1000);self.switch=10*self.tau0
    def channel_net(self,v):
        return np.array([v[j] if k is None else v[j]-v[k] for j,k in self.channels])
    def canonical_current(self,x): return self.channel_net(self.rates(x))
    def reduced_observables(self,dz):
        x,q,phi,dh=self.manifold_delta(dz,True)
        v=self.rates(x)
        flow=np.array([math.fsum(c*v[j] for j,c in row) for row in self.ts_rows])
        nonfast=np.array([math.fsum(c*v[j] for j,c in row) for row in self.nonfast_qrows])
        needed=dh@flow-nonfast
        j=np.linalg.solve(self.Nqf,needed)
        net=self.channel_net(v);net[self.fast_channels]=j
        return x,net,v,flow,dh,nonfast
    def law_drift(self,x):
        return np.array([[math.fsum(float(c)*(float(xx[i])-float(self.x0[i])) for i,c in law.items())
                          for law in self.source.laws] for xx in x])
    def coordinate_labels(self): return list(self.labels)

def gate_status(error,uncertainty,gate):
    if not np.isfinite(error) or not np.isfinite(uncertainty): return 'NUMERICALLY_UNRESOLVED'
    if uncertainty>0.1*gate: return 'NUMERICALLY_UNRESOLVED'
    if error+uncertainty<=gate: return 'RESOLVED_PASS'
    if max(0.,error-uncertainty)>gate: return 'RESOLVED_FAIL'
    return 'NUMERICALLY_UNRESOLVED'

def metric_rows(names,source,reduced,source_probe,reduced_probe,times,switch,floor,gate,category,
                mandatory_indices=None,extra_uncertainty=None):
    mandatory=set(range(len(names)) if mandatory_indices is None else mandatory_indices)
    result=[]
    for window,mask,is_gate in [('FULL_WINDOW',times>=0,True),('POST_INITIAL_LAYER',times>=switch,True),
                               ('POST_0P05_DIAGNOSTIC',times>=.05,False),('COMPOSITE_OR_HYBRID',times>=0,False)]:
        scale=np.maximum(np.max(abs(source[mask]),axis=0),floor)
        e=np.max(abs(reduced[mask]-source[mask]),axis=0)/scale
        u=(np.max(abs(source_probe[mask]-source[mask]),axis=0)+
           np.max(abs(reduced_probe[mask]-reduced[mask]),axis=0))/scale
        if extra_uncertainty is not None: u+=np.max(abs(extra_uncertainty[mask]),axis=0)/scale
        for k,n in enumerate(names):
            required=k in mandatory and is_gate
            result.append(dict(observable=n,category=category,window=window,mandatory=required,
                 reference_scale=float(scale[k]),floor=floor,E_inf=float(e[k]),
                 max_absolute_error=float(e[k]*scale[k]),uncertainty=float(u[k]),gate=gate,
                 status=gate_status(float(e[k]),float(u[k]),gate) if required else 'DESCRIPTIVE',
                 lower_error=max(0.,float(e[k]-u[k])),upper_error=float(e[k]+u[k])))
    return result
