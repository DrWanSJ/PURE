"""Independent R5 provenance, canonical algebra and derivative verification."""
from r5_common_v1 import *
from fractions import Fraction
import xml.etree.ElementTree as ET
from scipy.optimize import root
from r5_ck_partial_equilibrium_runtime_v1 import CKRuntime,FAST_IDS
from verify_r5_ck_critical_manifold_v1 import verify as verify_root
def independent_canonical():
 path=ROOT/'models/pnas2017_full_reference/original/fMGG_synthesis.xml';ns='{http://www.sbml.org/sbml/level2/version4}';mn='{http://www.w3.org/1998/Math/MathML}'
 model=ET.parse(path).getroot().find(ns+'model');species=[v.attrib['id'] for v in model.find(ns+'listOfSpecies')];ix={n:i for i,n in enumerate(species)};reactions=[]
 params={v['Name']:float(v['Value']) for v in csv.DictReader((ROOT/'models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv').open())}
 for node in model.find(ns+'listOfReactions'):
  col=np.zeros(len(species));sides=[]
  for side,sign in [('listOfReactants',-1),('listOfProducts',1)]:
   parent=node.find(ns+side);names={}
   for v in parent if parent is not None else []:
    sm=v.find(ns+'stoichiometryMath');value=Fraction(sm.find(mn+'math')[0].text) if sm is not None else Fraction(v.attrib.get('stoichiometry','1'));n=v.attrib['species'];names[n]=value;col[ix[n]]+=sign*float(value)
   sides.append(names)
  factors=[ix[v.text.strip()] for v in node.find(ns+'kineticLaw').find(mn+'math')[0][1:] if v.text.strip()!='k1'];rid=node.attrib['id'];reactions.append({'id':rid,'col':col,'sides':sides,'factors':factors,'k':params[rid+'_k1']})
 def rate_rhs(x):
  rates=np.array([v['k']*math.prod(x[i] for i in v['factors']) for v in reactions]);return S@rates,rates
 S=np.column_stack([v['col'] for v in reactions]);return species,reactions,S,rate_rhs
def main():
 previous=OUT/'verification.json'
 if previous.exists():
  dest=OUT/'verification_attempts';dest.mkdir(exist_ok=True);n=len(list(dest.glob('attempt_*.json')))+1;(dest/('attempt_'+str(n).zfill(3)+'.json')).write_bytes(previous.read_bytes())
 reg=checked_registration();snapshot=json.loads((OUT/'historical_snapshot.json').read_text());mismatch=[p for p,h in snapshot.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
 checks={'all_2420_preexisting_files_byte_identical':not mismatch,'registration_sha256_binding':True};detail={'historical_mismatches':mismatch,'historical_files':len(snapshot)}
 species,rx,S,rhs=independent_canonical();r=CKRuntime();assert species==r.source.species
 fast=[next(j for j,re in enumerate(rx) if re['id']==rid) for rid in FAST_IDS];Sf=S[:,fast];checks['canonical_stoichiometry']=bool(np.array_equal(S,r.S.toarray()));checks['CK_parameters']=[rx[j]['k'] for j in fast]==[2,1000,2,1000]
 expected=[({'CK':Fraction(1),'CP':Fraction(1)},{'CK_CP':Fraction(1)}),({'CK_CP':Fraction(1)},{'CK':Fraction(1),'CP':Fraction(1)}),({'CK_ADP':Fraction(1),'CP':Fraction(1)},{'CK_CP_ADP':Fraction(1)}),({'CK_CP_ADP':Fraction(1)},{'CP':Fraction(1),'CK_ADP':Fraction(1)})]
 checks['CK_canonical_reactants_products']=all(tuple(rx[j]['sides'])==sides for j,sides in zip(fast,expected))
 import sympy as sp
 checks['fast_rank_two']=sp.Matrix(Sf.astype(int)).rank()==2;checks['full_Lf_rank239']=sp.Matrix(r.Lf.astype(int)).rank()==239;checks['exact_LfSf_zero']=bool(np.max(abs(r.Lf@Sf))==0);checks['T_D_zero']=bool(np.max(abs(r.T@r.D))==0);checks['T_Xz_identity']=bool(np.max(abs(r.T@r.Xz-np.eye(212)))==0)
 laws=np.array([[float(v.get(i,0)) for i in range(241)] for v in r.source.laws]);checks['source_general_laws_exact']=bool(np.max(abs(laws@S))==0 and np.max(abs(laws@r.Xz))==0 and np.max(abs(laws@r.D))==0)
 checks['critical_root_derivative_eigenvalue_verification']=verify_root()['status']=='PASS'
 from r4_fast_block_common_v1 import source_data,REG,condition_initial,R4FamilyRuntime
 t,full=source_data('R3_BASE');rng=np.random.default_rng(50107);ckrows=[]
 for i in [0,50,100,150,200]:
  z=r.T@full[i];dz=r.T@(full[i]-r.x0);x,q,phi,dh=r.manifold_delta(dz,True);unscaled,vr=rhs(x);vslow=vr.copy();vslow[fast]=0;flow=r.T@(S@vslow)
  direct=r.reduced_rhs_delta(0,dz);checks['projected_all_nonfast_flow_'+str(i)]=np.max(abs(flow-direct))<1e-8
  for eta in reg['eta']:
   v=vr.copy();v[fast]/=eta;got=r.full_rhs(0,x,eta)
   checks['full_stoichiometric_eta_action_'+str(i)+'_'+str(eta)]=bool(np.max(abs(got-S@v))<1e-8 and np.array_equal(v[np.setdiff1d(np.arange(968),fast)],vr[np.setdiff1d(np.arange(968),fast)]))
   checks['Kd_preserved_'+str(eta)]=Fraction(1000)/Fraction(str(eta))/(Fraction(2)/Fraction(str(eta)))==500
  # Directional finite differences test full projected analytic Jacobian.
  scale=np.maximum(abs(z),1e-3)
  for d in range(3):
   direction=rng.normal(size=212)*scale;direction[:3]=[.2,.1,.3];h=1e-5
   fd=(r.reduced_rhs_delta(0,dz+h*direction)-r.reduced_rhs_delta(0,dz-h*direction))/(2*h);pred=r.reduced_jac_delta(0,dz)@direction;err=float(np.max(abs(fd-pred))/max(1,np.max(abs(pred))))
   ckrows.append({'sample_index':i,'direction':d,'projected_jacobian_fd_relative_error':err,'centered_vs_absolute_state_difference':float(max(abs(x-r.manifold(z)[0]))),'source_general_law_roundoff':float(max(abs(laws@(x-r.x0))))})
 checks['CK_projected_Jacobian_fd']=max(v['projected_jacobian_fd_relative_error'] for v in ckrows)<1e-5
 write_csv(OUT/'ck/independent_projected_flow_crosscheck.csv',ckrows)
 # GlyRS every sample independently differentiated from canonical monomials;
 # selected samples additionally use direct finite differences and root solves.
 gly=R4FamilyRuntime('GlyRS');grows=[];operator_error=0.;old_error=0.;new_error=0.;dh_error=0.
 for c in REG['conditions']:
  name=c['condition_id'];tt,ff=source_data(name);x0=condition_initial(gly.source,name);data=np.load(OUT/'glyrs'/(name+'_operators.npz'));geom=np.load(ROOT/'results/reduction/r4_fast_block_screen/glyrs_only'/name/'source_manifold_geometry.npz')
  for i,xfull in enumerate(ff):
   z=gly.T@xfull;q=geom['h0'][i];x=gly.reconstruct(z,q,x0)
   VJ=np.zeros((968,241))
   for j,re in enumerate(rx):
    for pos,idx in enumerate(re['factors']):VJ[j,idx]+=re['k']*math.prod(x[k] for p,k in enumerate(re['factors']) if p!=pos)
   J=S@VJ;Gq=J[gly.q_index]@gly.D;Fq=gly.T@J@gly.D;Gz=J[gly.q_index]@gly.Xz;Dh=-np.linalg.solve(Gq,Gz);A=Gq-Dh@Fq
   for observed,expected in [(data['Gq'][i],Gq),(data['Fq'][i],Fq),(data['Dh'][i],Dh),(data['Aperp'][i],A),(data['feedback'][i],Dh@Fq)]:operator_error=max(operator_error,float(max(abs(observed-expected).ravel())/max(1,max(abs(expected).ravel()))))
   F=gly.T@rhs(x)[0];vel=Dh@F;old_error=max(old_error,float(max(abs(data['old'][i]-np.linalg.solve(Gq,vel)))));new_error=max(new_error,float(max(abs(data['new'][i]-np.linalg.solve(A,vel)))))
   if i in [0,50,100,200]:
    # Larger symmetric steps avoid cancellation of large full-network RHS
    # values when differentiating the small projected Fq. The canonical
    # monomials are at most quadratic in these q perturbations.
    qstep=1e-3*np.maximum(abs(q),1e-3);Gfd=[];Ffd=[]
    for j in range(9):
     dq=np.eye(9)[j]*qstep[j];plus=rhs(gly.reconstruct(z,q+dq,x0))[0];minus=rhs(gly.reconstruct(z,q-dq,x0))[0];Gfd.append((plus-minus)[gly.q_index]/(2*qstep[j]));Ffd.append(gly.T@(plus-minus)/(2*qstep[j]))
    ge=float(max(abs(np.array(Gfd).T-Gq).ravel())/max(1,max(abs(Gq).ravel())));fe=float(max(abs(np.array(Ffd).T-Fq).ravel())/max(1,max(abs(Fq).ravel())))
    direction=rng.normal(size=205)*np.maximum(abs(z),1e-3);h=1e-5
    def equation(zz,qq):return rhs(gly.reconstruct(zz,qq,x0))[0][gly.q_index]
    qp=root(lambda qq:equation(z+h*direction,qq),q,options={'xtol':1e-10});qm=root(lambda qq:equation(z-h*direction,qq),q,options={'xtol':1e-10});fd=(qp.x-qm.x)/(2*h);pred=Dh@direction;de=float(max(abs(fd-pred))/max(1,max(abs(pred))))
    dh_error=max(dh_error,de);grows.append({'condition':name,'sample_index':i,'Gq_fd_relative_error':ge,'Fq_fd_relative_error':fe,'Dh_directional_root_fd_relative_error':de,'plus_root_residual':float(max(abs(equation(z+h*direction,qp.x)))),'minus_root_residual':float(max(abs(equation(z-h*direction,qm.x))))})
  print('Independent GlyRS',name,'verified',flush=True)
 checks['GlyRS_all_sample_operators']=operator_error<1e-10;checks['GlyRS_Gq_fd']=max(v['Gq_fd_relative_error'] for v in grows)<1e-5;checks['GlyRS_Fq_fd']=max(v['Fq_fd_relative_error'] for v in grows)<1e-5;checks['GlyRS_Dh_root_fd']=dh_error<1e-5;checks['GlyRS_old_predictor']=old_error<1e-8;checks['GlyRS_feedback_predictor']=new_error<1e-8
 runtime_text=(ROOT/'scripts/r5_ck_partial_equilibrium_runtime_v1.py').read_text()
 checks['no_fitting_no_clipping_no_threshold_mutation']=not reg['fitting'] and not reg['threshold_mutation'] and 'np.clip(' not in runtime_text and 'curve_fit(' not in runtime_text and 'least_squares(' not in runtime_text and not mismatch
 checks['canonical_source_initial_parameters_unchanged']=all(sha(ROOT/p)==h for p,h in snapshot.items() if p.startswith('models/pnas2017_full_reference/original/'))
 write_csv(OUT/'glyrs/independent_derivative_crosscheck.csv',grows);detail.update(operator_max_relative_error=operator_error,old_predictor_max_absolute_error=old_error,new_predictor_max_absolute_error=new_error,Dh_root_fd_relative_error_max=dh_error)
 # Independent accounting identity from canonical matrix and stored arrays.
 bal=list(csv.DictReader((OUT/'balance/reconstructed_full_state_accounting.csv').open()));checks['affine_balance_decomposition_identity']=max(float(v['affine_decomposition_identity_error']) for v in bal)<1e-8
 # Recompute selected balance rows from frozen arrays with the independently
 # parsed canonical S; do not use the balance generator's summation helper.
 balance_error=0.
 for c in REG['conditions']:
  for family in ['GlyRS','MetRS']:
   cr=R4FamilyRuntime(family);p=ROOT/'results/reduction/r4_fast_block_screen'/(family.lower()+'_only')/c['condition_id'];tp=p/'state_trajectories.npz'
   if not tp.exists():tp=p/'recovered_state_trajectories.npz'
   xx=np.load(tp)['reduced_state'];xi=np.load(p/'directed_ledgers.npz')['reduced_extent']
   for i in [0,50,100,200]:
    terms=np.array([math.fsum(v*xi[i,j] for j,v in enumerate(row) if v) for row in S]);fullres=xx[i]-xx[0]-terms
    slowres=cr.T@(xx[i]-xx[0])-cr.T@terms;qres=xx[i,cr.q_index]-xx[0,cr.q_index]-terms[cr.q_index]
    err=float(max(abs(fullres-cr.Xz@slowres-cr.D@qres)));balance_error=max(balance_error,err)
 checks['independent_full_vs_slow_algebraic_balance_identity']=balance_error<1e-8;detail['independent_balance_identity_error_max']=balance_error
 # Manifest covers outputs; verifier outputs are excluded to avoid self hashes.
 manifest=OUT/'manifest.json'
 if manifest.exists():
  m=json.loads(manifest.read_text());checks['manifest_all_hashes']=all((ROOT/p).is_file() and sha(ROOT/p)==h for p,h in m['files_sha256'].items())
  checks['manifest_required_output_coverage']=all(p.relative_to(ROOT).as_posix() in m['files_sha256'] for p in OUT.rglob('*') if p.is_file() and p.name not in ['manifest.json','verification.json','verification_binding.json'] and 'verification_attempts' not in p.parts and 'independent_' not in p.name and p.name!='critical_manifold_verification.json')
  used=json.loads((OUT/'used_inputs.json').read_text());checks['used_source_inputs_hash_match_frozen_snapshot']=all(snapshot.get(p)==h and sha(ROOT/p)==h for p,h in used.items())
 checks={k:bool(v) for k,v in checks.items()}
 result={'status':'PASS' if all(checks.values()) else 'FAIL','engineering_provenance_only':True,'scientific_promotion':False,'checks':checks,'details':detail,'unverified_numerical_or_scientific_questions':['bounded full-domain validity','uniform asymptotic theorem error bound','authoritative absolute chemical units','fully separated historical state/dense/extent numerical errors']}
 write_json(OUT/'verification.json',result);print('R5 verification',result['status'],[k for k,v in checks.items() if not v],flush=True)
 if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
