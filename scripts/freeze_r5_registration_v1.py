"""Prospective R5 registration; run once before numerical comparisons."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,encoding='utf-8',newline='\n')
def main():
 out=ROOT/'results/reduction/r5_mechanism_first';doc=ROOT/'docs/reduction'
 assert not (doc/'r5_theory_scope_v1.json').exists()
 files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
 snapshot={p:sha(ROOT/p) for p in files if p and (ROOT/p).is_file()}
 put(out/'historical_snapshot.json',json.dumps(snapshot,indent=2)+'\n')
 request=Path('C:/Users/sean/.codex/attachments/eb22a377-3337-4743-bdd7-cdf66b0686de/已粘贴的文本.txt').read_text(encoding='utf-8')
 put(doc/'r5_mechanism_first_authorization_20261007.md','# R5 human authorization — 2026-10-07\n\nThe following is the verbatim supplied authorization. Only CK pair partial-equilibrium theory/testing, frozen-R4 GlyRS transverse diagnostics and balance decomposition are authorized. No promotion, deletion, fitting, threshold mutation, push or merge.\n\n```text\n'+request+'\n```\n')
 protocol='''# R5 mechanism-first preregistration v1

Parent main is 0b6f9ad649a7e283e440e0294a021123551f6858; execution checkout starts at local R4 9def91d, whose parent registration is 88c0bfa. No merge is performed. Every pre-existing tracked file is frozen by a byte SHA-256 snapshot. All work is additive.

Claims are separated into ANALYTICAL_STRUCTURAL, ASYMPTOTIC_LIMIT, ORIGINAL_PARAMETER_DESCRIPTIVE and SCIENTIFIC_PROMOTION. eta convergence never approves eta=1; no scientific promotion is authorized.

CK fast columns are exactly re0000000332/333/336/337, subject to canonical verification. Author parameters must equal 2/1000/2/1000; otherwise CK derivation stops. Verify concentration/time conventions from author/repository evidence, not SBML placeholder parameter units. Lf annihilates all four complete canonical columns. T0,T1,B are FAST_SUBSYSTEM_INVARIANT and DYNAMIC_TOTAL_COORDINATE. All non-fast reactions force totals.

Use analytical monotone material-equation root, explicit frozen fast Jacobian and full R1 SOURCE_GENERAL chart. Baseline only for eta=[1,0.3,0.1,0.03,0.01]. Full model scales every selected column's rate by 1/eta, with other rates and stoichiometry unchanged. Primary BDF rtol=1e-10, atol=1e-14, analytic Jacobians, interval [0,1000], source report grid [0]+geomspace(1e-4,1000,200); uncertainty baseline rtol=1e-11, atol=1e-15 if primary comparisons complete. Each solve bounded at 1800 wall seconds and 300000 RHS calls. Computational stops are UNSCORED. Saved complete/partial trajectories and failure messages are retained.

Initial layer is reported separately. Hybrid startup solves the full scaled network until t_switch=10*eta*tau0, where tau0 is slowest equilibrium frozen-layer relaxation at the unmodified author initial fast totals. This fixed ten-relaxation rule is registered before data; no fitting/time shift. Continue reduced evolution from actual startup totals. Report startup manifold distance; failure to relax is explicit. Outer reduced initial state is Phi(Lf x0), not fitted. Compare full and hybrid after max(t_switch) across eta, as well as after each layer. Descriptive convergence uses normalized max slow-coordinate error, scales=max absolute source baseline coordinate with floor 1e-6; this is a reporting scale, not a new acceptance threshold. Non-decreasing or uncertainty-sized errors trigger derivation inspection; eta=1 accuracy is gated on evidence of asymptotic consistency, never a promotion gate. Gross equilibrium fluxes are reported separately from slow net redistribution and exact source extents.

GlyRS uses every valid stored R4 source sample and root. Dh=-Gq^-1 Gz; Fq=T J D; Aperp=Gq-Dh Fq. Old e=Gq^-1 Dh F0; new e=Aperp^-1 Dh F0. No h1 simulation. Report per-coordinate full/post0.05/t>=1 correlation, relative L2, magnitude/sign, p95 absolute error, occupancy-normalized error, spectra, nonnormal numerical abscissa and conditioning. Defect propagation is diagnostic, not rigorous bound. Classify promising only on substantial descriptive improvement across conditions; unstable/unresolved samples take precedence. No new scientific threshold.

Balance uses stored R3/R4 states, ledgers, solver/uncertainty evidence first. Compare ordinary, Kahan, math.fsum and longdouble residual post-processing without changing stored trajectories. Separately report 27 exact law drift, state RHS quadrature consistency, directed ledger reconstruction, cancellation bound, extent uncertainty, interpolation and reduced-coordinate/algebraic reconstruction. Missing dense outputs or reference integrations remain UNIDENTIFIABLE_FROM_STORED_DATA; sampled quadrature is not direct solver error. Preserve R4's balance gate and classification.

Independent verifier re-parses source reaction/parameter tables, checks hashes, exact integer identities, derivatives/roots/eigenvalues/scaling, projected flow, and GlyRS derivatives by finite differences. Reporting/status files explicitly retain unavailable/unresolved evidence. Literature assumptions are separated from PURE facts. Final human decision table gives exactly one recommendation; stop before next stage/push/merge.
'''
 put(doc/'r5_mechanism_first_preregistration_v1.md',protocol)
 scope={'schema':'R5_MECHANISM_FIRST_THEORY_SCOPE_V1','parent_main_sha':'0b6f9ad649a7e283e440e0294a021123551f6858','execution_parent_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'claims':['ANALYTICAL_STRUCTURAL','ASYMPTOTIC_LIMIT','ORIGINAL_PARAMETER_DESCRIPTIVE','SCIENTIFIC_PROMOTION_NOT_AUTHORIZED'],'fast_reaction_ids':['re0000000332','re0000000333','re0000000336','re0000000337'],'eta':[1,.3,.1,.03,.01],'rtol':1e-10,'atol':1e-14,'end_s':1000,'wall_bound_s':1800,'rhs_bound':300000,'hybrid_switch':'10*eta*tau0','new_full_condition_campaign':False,'threshold_mutation':False,'fitting':False,'promotion':False,'historical_snapshot_sha256':sha(out/'historical_snapshot.json'),'registration_hashes':{p.name:sha(p) for p in [doc/'r5_mechanism_first_authorization_20261007.md',doc/'r5_mechanism_first_preregistration_v1.md']}}
 put(doc/'r5_theory_scope_v1.json',json.dumps(scope,indent=2)+'\n')
 put(out/'registration_binding.json',json.dumps({str(p.relative_to(ROOT)):sha(p) for p in [doc/'r5_mechanism_first_authorization_20261007.md',doc/'r5_mechanism_first_preregistration_v1.md',doc/'r5_theory_scope_v1.json',out/'historical_snapshot.json']},indent=2)+'\n')
 print('Frozen',len(snapshot),'pre-existing files')
if __name__=='__main__':main()
