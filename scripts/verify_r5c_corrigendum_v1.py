"""Independent raw-evidence reproduction; no generator or ODE solver called."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',OMP_NUM_THREADS='1')
import csv, json, math, hashlib, subprocess, ast
from pathlib import Path
from fractions import Fraction
import xml.etree.ElementTree as ET
import numpy as np
from r4_fast_block_common_v1 import R4FamilyRuntime, condition_initial, historical_path
from r5_ck_partial_equilibrium_runtime_v1 import CKRuntime

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'results/reduction/r5c_corrigendum'
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x): p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def csvrows(p): return list(csv.DictReader(p.open(encoding='utf-8')))

def canonical():
    ns='{http://www.sbml.org/sbml/level2/version4}'; mn='{http://www.w3.org/1998/Math/MathML}'
    m=ET.parse(ROOT/'models/pnas2017_full_reference/original/fMGG_synthesis.xml').getroot().find(ns+'model')
    names=[n.attrib['id'] for n in m.find(ns+'listOfSpecies')]; ix={n:i for i,n in enumerate(names)}
    params={p['Name']:float(p['Value']) for p in csvrows(ROOT/'models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv')}
    columns=[]; specs=[]; ids=[]
    for n in m.find(ns+'listOfReactions'):
        col=np.zeros(len(names)); rid=n.attrib['id']; ids.append(rid)
        for tag,sign in [('listOfReactants',-1),('listOfProducts',1)]:
            p=n.find(ns+tag)
            for sr in p if p is not None else []:
                sm=sr.find(ns+'stoichiometryMath'); value=Fraction(sm.find(mn+'math')[0].text) if sm is not None else Fraction(sr.attrib.get('stoichiometry','1'))
                col[ix[sr.attrib['species']]]+=sign*float(value)
        columns.append(col)
        factors=[ix[v.text.strip()] for v in n.find(ns+'kineticLaw').find(mn+'math')[0][1:] if v.text.strip()!='k1']; specs.append((params[rid+'_k1'],factors))
    S=np.array(columns).T
    def rates(x): return np.array([k*math.prod(x[i] for i in factors) for k,factors in specs])
    return names,ids,S,specs,rates

def balance(M,state,extent,anchor):
    out=np.zeros_like(state)
    for j,row in enumerate(M):
        idx=np.flatnonzero(row)
        for k in range(len(state)):
            val=math.fsum(row[i]*extent[k,i] for i in idx)
            out[k,j]=math.fsum([state[k,j],-anchor[j],-val])
    return out

def ck_root(z):
    T0,T1,B=z[:3]; a=500+T0+T1-B; d=math.hypot(a,2*math.sqrt(500*B)); p=1000*B/(a+d) if a>=0 else (d-a)/2
    q=np.array([T0,T1])*p/(500+p)
    # Differentiate scalar material relation independently of runtime formula.
    Hp=1+500*(T0+T1)/(500+p)**2
    dp=np.array([-p/(500+p),-p/(500+p),1])/Hp
    Dh=np.zeros((2,212))
    for k in range(2):
        Dh[k,:3]=500*z[k]/(500+p)**2*dp
        Dh[k,k]+=p/(500+p)
    return p,q,Dh

def main():
    checks={}; details={}; check=lambda k,v:checks.update({k:bool(v)})
    snapshot=read('results/reduction/r5c_corrigendum/historical_parent_snapshot.json'); mismatches=[p for p,h in snapshot.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    parent=Path('C:/Users/sean/.codex/worktrees/r5-mechanism-first/GUV')
    check('all_preexisting_files_byte_identical',not mismatches)
    check('snapshot_matches_clean_execution_parent',parent.is_dir() and all((parent/p).is_file() and sha(parent/p)==h for p,h in snapshot.items()))
    initial=read('results/reduction/r5c_corrigendum/historical_snapshot.json'); qualification=read('results/reduction/r5c_corrigendum/checkout_byte_qualification.json')
    restored={v['path']:v for v in qualification['restored_files']}
    check('checkout_byte_qualification_exhaustive',set(restored)=={p for p,h in initial.items() if snapshot[p]!=h} and all(v['initial_checkout_sha256']==initial[p] and v['frozen_parent_sha256']==snapshot[p] and v['canonical_content_changed'] is False for p,v in restored.items()))
    details.update(historical_file_count=len(snapshot),mismatches=mismatches)
    binding=read('results/reduction/r5c_corrigendum/registration_binding.json');check('registration_binding',all(sha(ROOT/p)==h for p,h in binding.items()))
    check('protected_model_parameters_initial_thresholds_unchanged',not mismatches)
    names,ids,S,specs,rates=canonical(); reg=read('docs/reduction/r4_fast_block_candidates_v1.json')
    saved=csvrows(OUT/'r4_decisive_gate_logic.csv'); independent=[]; post={}; lawsmax=0.
    aa={v['reaction_id'] for v in csvrows(ROOT/'models/pnas2017_full_reference/audit/aminoacylation_reactions.csv')}; ai=[i for i,n in enumerate(ids) if n in aa]
    for family in ['GlyRS','MetRS']:
        r=R4FamilyRuntime(family);check(family+'_canonical_S',np.array_equal(S,r.S.toarray()))
        L=np.array([[float(l.get(i,0)) for i in range(241)] for l in r.source.laws]);check(family+'_exact_source_laws',np.max(abs(L@S))==0)
        for condition in reg['conditions']:
            c=condition['condition_id']; p=ROOT/'results/reduction/r4_fast_block_screen'/(family.lower()+'_only')/c
            path=p/'state_trajectories.npz'
            if not path.exists():path=p/'recovered_state_trajectories.npz'
            st=np.load(path); t=st['times']; full=st['full_state']; red=st['reduced_state']; z=st['reduced_slow']; led=np.load(p/'directed_ledgers.npz'); u=np.load(p/'uncertainty_reduced_ledgers.npz')
            sp=ROOT/'results/reduction/r4_fast_block_screen/source_uncertainty'/c; sf=np.load(sp/'probe_state.npz')['state']; sl=np.load(sp/'probe_ledgers.npz'); x0=condition_initial(r.source,c)
            scales={'state':np.maximum(np.max(abs(full),axis=0),1e-6),'rate':np.maximum(np.max(abs(led['full_rates']),axis=0),1e-9),'extent':np.maximum(np.max(abs(led['full_extent']),axis=0),1e-6)}
            primary={'state':(full,red),'rate':(led['full_rates'][:,ai],led['reduced_rates'][:,ai]),'extent':(led['full_extent'][:,ai],led['reduced_extent'][:,ai])}
            probes={'state':(sf,u['state']),'rate':(sl['rates'][:,ai],u['rates'][:,ai]),'extent':(sl['extent'][:,ai],u['extent'][:,ai])}
            metrics={};uncs={};envelopes={}
            for g,(src,approx) in primary.items():
                scale=scales[g] if g=='state' else scales[g][ai]
                metrics[g]=float(np.max(abs(src-approx)/scale)); ds=float(np.max(abs(probes[g][0]-src)/scale)); dr=float(np.max(abs(probes[g][1]-approx)/scale));uncs[g]=max(ds,dr);envelopes[g]=ds+dr
            TS=r.T@S; fb=balance(S,full,led['full_extent'],x0);rb=balance(TS,z,led['reduced_extent'],r.T@x0)
            metrics['balance']=float(max(np.max(abs(fb)),np.max(abs(rb))))
            bu=[np.max(abs(balance(S,sf,sl['extent'],x0)-fb)),np.max(abs(balance(TS,u['slow'],u['extent'],r.T@x0)-rb)),np.max(abs(balance(TS,z,led['tight_reduced_extent'],r.T@x0)-rb)),max(np.max(abs(led['full_extent'])@abs(S).T),np.max(abs(led['reduced_extent'])@abs(TS).T))*np.finfo(float).eps]
            uncs['balance']=float(max(bu));envelopes['balance']=uncs['balance']
            for g in metrics:
                threshold=reg['gates']['process_rate' if g=='rate' else g]; budget=reg['uncertainty']['tier_fraction']*threshold; lo=max(0.,metrics[g]-envelopes[g]); hi=metrics[g]+envelopes[g]
                status='NUMERICALLY_UNRESOLVED'
                if uncs[g]<=budget:
                    if lo>threshold:status='RESOLVED_FAIL'
                    elif hi<threshold:status='RESOLVED_PASS'
                row=next(v for v in saved if v['candidate']=='R4_'+family.upper()+'_ONLY' and v['condition']==c and v['gate']==g)
                ok=all(math.isclose(float(row[k]),v,rel_tol=1e-12,abs_tol=1e-12) for k,v in [('threshold',threshold),('uncertainty_budget',budget),('measured_error',metrics[g]),('uncertainty',uncs[g]),('comparison_envelope',envelopes[g]),('lower_bound',lo),('upper_bound',hi)]) and row['gate_status']==status and (row['decisive_against_all_gate_pass']=='True')==(status=='RESOLVED_FAIL')
                check(family+'_'+c+'_'+g+'_independent_gate',ok)
                historical=json.loads((p/'derived_review_result.json').read_text()); check(family+'_'+c+'_'+g+'_historical_status',row['historical_tier_classification']==historical['tier_scientific_status'][g] and row['historical_overall_status']==historical['scientific_status'])
                independent.append(dict(candidate=family,condition=c,gate=g,measured=metrics[g],uncertainty=uncs[g],envelope=envelopes[g],lower=lo,upper=hi,status=status))
            # Independently parse all source kinetics at representative samples.
            for i in [0,50,100,200]:
                check(family+'_'+c+'_canonical_rates_'+str(i),np.max(abs(rates(red[i])-led['reduced_rates'][i])/np.maximum(abs(led['reduced_rates'][i]),1))<1e-12)
            for x in [full,red,sf]:
                drift=max(abs(math.fsum(float(w)*(float(xx[j])-float(x0[j])) for j,w in enumerate(law) if w)) for xx in x for law in L)
                lawsmax=max(lawsmax,drift)
            ps=float(np.max((abs(full-red)/scales['state'])[t>=.05]));post['R4_'+family.upper()+'_ONLY']=max(post.get('R4_'+family.upper()+'_ONLY',0),ps)
            if family=='GlyRS':
                h=np.load(historical_path(c)/'state_trajectories.npz');post['HISTORICAL_R3_21']=max(post.get('HISTORICAL_R3_21',0),float(np.max((abs(h['full_state']-h['reduced_state'])/scales['state'])[t>=.05])))
            closure=next(v for v in saved if v['candidate']=='R4_'+family.upper()+'_ONLY' and v['condition']==c and v['gate']=='closure_engineering');check(family+'_'+c+'_closure_guard',float(closure['threshold'])==reg['gates']['closure_engineering'] and float(closure['measured_error'])==historical['closure_counters']['max_residual'] and closure['gate_status']=='ENGINEERING_GUARD_RECORDED')
            print('Independent raw gates',family,c,flush=True)
    gs=read('results/reduction/r5c_corrigendum/r4_gate_summary.json');check('post_layer_errors_reproduced',all(math.isclose(post[k],gs['post_0p05_worst'][k],abs_tol=1e-12) for k in post))
    check('each_family_condition_state_rate_decisively_fails',all(any(v['candidate']==f and v['condition']==c['condition_id'] and v['gate']==g and v['status']=='RESOLVED_FAIL' for v in independent) for f in ['GlyRS','MetRS'] for c in reg['conditions'] for g in ['state','rate']))
    check('balance_remains_unresolved',all(v['status']=='NUMERICALLY_UNRESOLVED' for v in independent if v['gate']=='balance'))
    check('gate_coverage',len(saved)==90 and len(independent)==72)
    details.update(post_0p05_worst=post,source_law_drift_recomputed= lawsmax)

    r=CKRuntime(); fast=[ids.index(n) for n in ['re0000000332','re0000000333','re0000000336','re0000000337']]; fw=[];rv=[]
    for a,b in zip(fast[::2],fast[1::2]):
        check('canonical_reverse_'+ids[a],np.array_equal(S[:,a],-S[:,b])); positive=S[r.qix,a].sum()>0;fw.append(a if positive else b);rv.append(b if positive else a)
    N=S[np.ix_(r.qix,fw)];cs=read('results/reduction/r5c_corrigendum/ck_fast_current_summary.json');check('canonical_Nqf_and_unique_rank',np.array_equal(N,np.array(cs['N_qf'])) and np.linalg.matrix_rank(N)==2 and cs['nullspace_dimension']==0)
    check('CK_original_parameters', [specs[i][0] for i in fast]==[2,1000,2,1000]);check('CK_fast_invariants',np.max(abs(r.T@S[:,fast]))==0 and np.max(abs(r.Lf@S[:,fast]))==0)
    a=np.load(ROOT/'results/reduction/r5_mechanism_first/ck/baseline_comparison.npz');layer=read('results/reduction/r5_mechanism_first/ck/initial_layer_definition.json'); eta=read('results/reduction/r5_mechanism_first/ck/eta_scan_summary.json');t=a['times']
    q0=ck_root(r.T@r.x0)[1];check('CK_initial_jump_independent',max(abs(q0-r.x0[r.qix]))==eta['worst_initial_layer_jump']);p0=ck_root(r.T@r.x0)[0];check('CK_initial_timescale_independent',math.isclose(1/(2*p0+1000),layer['tau0_s'],rel_tol=1e-12))
    errors={}
    for name in ['outer','hybrid']:
        errors[name]={w:float(np.max((abs(a[name]-a['full'])/a['state_scale'])[mask])) for w,mask in [('full_window',t>=0),('post_startup',t>=layer['switch_at_eta1_s']),('post_0p05',t>=.05)]}
        check('CK_'+name+'_post0p05_error_reproduced',math.isclose(errors[name]['post_0p05'],eta['original_eta1_all241_post_0p05_max_scaled'][name],rel_tol=1e-12))
        check('CK_'+name+'_post_startup_error_reproduced',math.isclose(errors[name]['post_startup'],eta['original_eta1_all241_post_startup_max_scaled'][name],rel_tol=1e-12))
    scan=csvrows(ROOT/'results/reduction/r5_mechanism_first/ck/singular_eta_scan.csv');scanerrors=[]
    for row in scan:
        ep=ROOT/'results/reduction/r5_mechanism_first/ck'/('eta_'+row['eta'].replace('.','p'))
        full=np.load(ep/'full/report.npz');hy=np.load(ep/'hybrid_slow/report.npz');mask=full['times']>=layer['switch_at_eta1_s'];hm=hy['times']>=layer['switch_at_eta1_s'];err=float(np.max(abs(full['state'][mask]@r.T.T-(hy['state'][hm]+r.z0))/a['slow_scale']))
        check('CK_eta_'+row['eta']+'_stored_array_error',math.isclose(err,float(row['hybrid_post_common_layer_slow_max_scaled']),rel_tol=1e-8,abs_tol=1e-10));scanerrors.append(err)
    check('CK_eta_systematic_decrease',all(b<a for a,b in zip(scanerrors,scanerrors[1:])))
    currents=csvrows(OUT/'ck_fast_current_reconstruction.csv');fdmax=0.;identitymax=0.;current_error=0.;scfull=np.array([rates(x)[fw]-rates(x)[rv] for x in a['full']]);scales=np.maximum(np.max(abs(scfull[t>=.05]),axis=0),1e-6)
    for row in currents:
        i=int(row['sample_index']);pair=int(row['pair']); z=np.array(json.loads(row['z']));storedq=np.array(json.loads(row['h0'])); storedDh=np.array(json.loads(row['Dh0']));zd=np.array(json.loads(row['z_dot']));p,q,Dh=ck_root(z)
        trajectory=a['full'] if row['approximation']=='source_projected_h0' else a[row['approximation']];check('CK_coordinate_'+row['approximation']+'_'+str(i)+'_'+str(pair),np.max(abs(z-r.T@trajectory[i]))<1e-9 and json.loads(row['z_labels'])==r.labels)
        x=r.affine(z,q);x[r.ix[2]]=p;v=rates(x);v[fast]=0;nonfast=S@v; expectedzd=r.T@nonfast; needed=Dh@expectedzd-nonfast[r.qix];got=np.linalg.solve(N,needed)
        check('CK_current_'+row['approximation']+'_'+str(i)+'_'+str(pair),np.max(abs(q-storedq))<1e-10 and np.max(abs(Dh-storedDh))<1e-12 and np.max(abs(zd-expectedzd))<1e-8 and abs(float(row['reconstructed_net_current'])-got[pair])<1e-8 and abs(float(row['q_dot_manifold'])-(Dh@expectedzd)[pair])<1e-8 and abs(float(row['q_dot_nonfast'])-nonfast[r.qix[pair]])<1e-8 and abs(float(row['direct_full_model_net_current'])-scfull[i,pair])<1e-8 and math.isclose(float(row['scaled_error']),abs(got[pair]-scfull[i,pair])/scales[pair],rel_tol=1e-8,abs_tol=1e-9))
        identitymax=max(identitymax,float(np.max(abs(N@got+nonfast[r.qix]-Dh@expectedzd))))
        for k in range(3):
            d=np.eye(212)[k]*max(1,abs(z[k]))*1e-5; fd=(ck_root(z+d)[1]-ck_root(z-d)[1])/(2*d[k]);fdmax=max(fdmax,float(np.max(abs(fd-Dh[:,k]))))
        current_error=max(current_error,abs(float(row['absolute_error'])-abs(got[pair]-scfull[i,pair])))
    check('CK_independent_Dh0_finite_difference',fdmax<1e-7);check('CK_fast_current_identity',identitymax<1e-9 and current_error<1e-8)
    details.update(CK_state_errors=errors,eta_hybrid_errors=scanerrors,CK_identity_max_error=identitymax,CK_Dh0_fd_max_error=fdmax,CK_representative_current_summary=cs['post_0p05_representative_comparison'])

    bal=read('results/reduction/r5_mechanism_first/balance/balance_decomposition_summary.json');check('exact_conservation_failure_not_observed',not bal['source_conservation_failure_observed'] and lawsmax<1e-8)
    check('balance_attribution_unresolved',bal['classification']=='MIXED / UNRESOLVED' and not bal['direct_state_vs_dense_vs_extent_error_separately_identified'])
    gly=read('results/reduction/r5_mechanism_first/glyrs/summary.json');check('GlyRS_historical_classification',gly['classification']=='ZERO_ORDER_GRAPH_ERROR_NOT_EXPLAINED_BY_LOCAL_TRANSVERSE_FORCING' and gly['improved_conditions']==7 and not gly['higher_order_model_built'])
    allowed={'PRESERVED_EXACTLY','PRESERVED_AT_ZERO_ORDER','RECONSTRUCTABLE_NET_CURRENT','DESCRIPTIVE_GROSS_FLUX_FROM_H0','REQUIRES_FIRST_ORDER_FLUX_RECONSTRUCTION','NOT_IDENTIFIABLE_AT_ZERO_ORDER','FULL_MODEL_ONLY'};obs=csvrows(OUT/'observable_identifiability.csv');check('observable_classes_A_through_H',set('ABCDEFGH')<={v['category'] for v in obs});check('observable_labels_consistent',all(v['identifiability_label'] in allowed for v in obs) and all(v['category']=='C' for v in obs if v['identifiability_label']=='PRESERVED_EXACTLY') and not any(v['category']=='G' and v['identifiability_label']=='PRESERVED_AT_ZERO_ORDER' for v in obs))
    corrections=csvrows(OUT/'interpretation_corrections.csv');check('all_ten_corrections_additive', {v['issue_id'] for v in corrections}=={'C'+str(i) for i in range(1,11)} and all(v['frozen_artifact_modified']=='False' and (ROOT/v['historical_evidence_affected']).is_file() for v in corrections))
    nav=read('results/reduction/r5c_corrigendum/evidence_navigation.json');check('all_claim_sources_hash_bound',all(sha(ROOT/v['evidence_path'])==v['source_sha256'] and v['classification'] in ['EXTRACTED','INFERRED','AMBIGUOUS'] for v in nav['nodes']))
    decisions=csvrows(ROOT/'docs/reduction/reduction_decisions.csv');check('all968_decisions_PENDING',len(decisions)==968 and all('PENDING' in v.values() for v in decisions))
    docs='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'docs/reduction').glob('r5c_*.md'));check('no_promotion_and_core_not_validated','CK_REDUCTION_NOT_YET_PROMOTED' in docs and 'NOT_VALIDATED' in docs and 'No scientific promotion' in docs)
    calls=[]
    for p in (ROOT/'scripts').glob('*r5c*.py'):
        tree=ast.parse(p.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                f=node.func; calls.append(f.id if isinstance(f,ast.Name) else f.attr if isinstance(f,ast.Attribute) else '')
    check('no_new_ODE_solve_h1_model_or_campaign',not set(calls)&{'solve_ivp','BDF','curve_fit','least_squares','clip'})
    # A clean additive diff plus byte-identical snapshot proves old models, h1
    # implementations and acceptance documents were neither added to nor changed.
    manifest=read('results/reduction/r5c_corrigendum/manifest.json');check('manifest_hashes',all(sha(ROOT/p)==h for p,h in manifest['files_sha256'].items()))
    bound_exclusions={'results/reduction/r5c_corrigendum/manifest.json','results/reduction/r5c_corrigendum/verification.json','results/reduction/r5c_corrigendum/verification_binding.json'}
    allnew={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.relative_to(ROOT).as_posix() not in snapshot}
    check('manifest_complete_new_file_coverage',allnew-bound_exclusions<=set(manifest['files_sha256']))
    check('manifest_scientific_scope',manifest['PURE_reduced_core']=='NOT_VALIDATED' and manifest['decisions_968']=='PENDING' and manifest['CK_promotion']=='NOT_YET_PROMOTED')
    result={'status':'PASS' if all(checks.values()) else 'FAIL','scope':'ENGINEERING_PROVENANCE_AND_REPRODUCIBLE_POSTPROCESSING_NOT_SCIENTIFIC_PROMOTION','checks':checks,'failed_checks':[k for k,v in checks.items() if not v],'details':details,'open_questions':['broad CK conditions','authoritative absolute units','full physical-domain theorem bounds','first-order gross flux reconstruction and initial-layer matching','combined21 causal explanation','complete state/dense/extent numerical attribution']}
    save(OUT/'verification.json',result);save(OUT/'verification_binding.json',{'self_hash_exclusion':'verification_binding.json; all other new files bound through this index and manifest','files_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in [OUT/'manifest.json',OUT/'verification.json']}})
    print(json.dumps({'status':result['status'],'checks':len(checks),'historical_files':len(snapshot),'failed':result['failed_checks']},indent=2));return result['status']=='PASS'

if __name__=='__main__':raise SystemExit(0 if main() else 1)
