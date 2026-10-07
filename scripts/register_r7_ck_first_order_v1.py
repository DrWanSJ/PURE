"""Freeze the authorization, exact derivation and numerical contract before R7 tests."""
import sys, subprocess, platform, json
from pathlib import Path
from r7_ck_h1_v1 import *

DERIVATION=r'''# R7 exact CK first-order graph and net-current derivation

The authoritative source is the repository's R5 singular family and the canonical
stoichiometric matrix; this is a derived mathematical navigation artifact.
EXTRACTED: R5 `full_rhs(x,eta)` divides exactly reactions 332/333/336/337 by eta.
All other 964 reactions keep their exact author constants. No other eta dependence
occurs. z=T*x (212 coordinates), q=(CK_CP,CK_CP_ADP), and
x=offset+Xz*z+D*q are exactly the frozen R5/R6 affine chart on the condition's
SOURCE_GENERAL conservation class. T*Xz=I, T*D=0, qrows(Xz)=0, qrows(D)=I.

With v_s the canonical rates with these four entries zero, TS=T*S_s and
Q=qrows(S_s), the exact equations are

    zdot=F(z,q)=TS*v_s(x(z,q))
    qdot=eta^-1*g(z,q)+G0(z,q), G0=Q*v_s(x(z,q)).

INFERRED, to be independently checked against those matrices:
T0=z0=CK+CK_CP; T1=z1=CK_ADP+CK_CP_ADP;
B=z2=CP+CK_CP+CK_CP_ADP. p=B-q0-q1 and
g_i=2*p*(Ti-qi)-1000*qi. Fast net-pair orientation follows canonical
332 MINUS 333 and 336 MINUS 337; N_qf=I2 and rank(N_qf)=2.

## Critical graph, independently reproduced

g=0 implies qi=Ti*p/(500+p). The scalar equation is
p+sum(Ti*p/(500+p))-B=0, equivalently
p^2+(500+T0+T1-B)*p-500*B=0. Its physical nonnegative root is
p=1000*B/(sqrt(a^2+2000*B)+a) for a>=0, otherwise (sqrt(...)-a)/2,
a=500+T0+T1-B. On the physical totals domain this unique root has 0<=p<=B.
This reproduces the existing root, never creates a replacement candidate.
Let b=p/(500+p), b'=500/(500+p)^2, C=1+(T0+T1)*b',
dp/dz[:3]=(-b,-b,1)/C, H=Dh0, H_ij=delta_ij*b+Ti*b'*dp_j
for j<3; H is zero on the other 209 columns.

## Invariance expansion, all terms through order eta

Insert h_eta=h0+eta*h1+eta^2*h2+O(eta^3) into
Dh_eta*F(z,h_eta)=eta^-1*g(z,h_eta)+G0(z,h_eta).
The eta^-1 coefficient is g(z,h0)=0. Define F0=F(z,h0),
J=g_q(z,h0)=-(2*p+1000)*I-2*(T-h0)*ones(1,2).
The order-one coefficient is H*F0=J*h1+G0(z,h0), hence

    h1=solve(J,H*F0-G0).

There are no explicit F_eta, G0_eta or additional rate-scaling terms.
R6 already reconstructs j0=N_qf^-1*(H*F0-G0)=N_qf^-1*J*h1.
Computing h1 does not newly create j0.
The eta coefficient of the invariance equation is

    Dh1*F0+H*Fq*h1=J*h2+0.5*g_qq[h1,h1]+G0_q*h1.

Since physical fast current is eta^-1 times the unscaled net pair rate,
N_qf*j_eta=J*h1+eta*(J*h2+0.5*g_qq[h1,h1])+O(eta^2).
Eliminate the combination involving h2 without constructing h2:

    j1=N_qf^-1*(Dh1*F0+H*Fq*h1-G0_q*h1).

This kinematic reconstruction does not recover individual microscopic gross
fluxes. All slow channels use the formal polynomial derivative
v_s,1=v_s,x*D*h1; F1=TS*v_s,1, G0_q*h1=Q*v_s,1.
The genuine first-order slow model is zdot=F0+eta*F1; it is explicitly a
Taylor truncation, not nonlinear substitution F(z,h0+eta*h1).
Its reported states are x(z,h0)+eta*D*h1. eta=1 throughout R7.

## Analytic Dh1 and independent derivative check

Differentiate J*h1=H*F0-G0 in an arbitrary slow direction w:

    Dh1*w=solve(J,(DH*w)*F0+H*(DF0*w)-DG0*w-(DJ*w)*h1).

Let pw=dp*w[:3], b''=-1000/(500+p)^3,
Cw=b'*(w0+w1)+(T0+T1)*b''*pw. Then
Ddp*w=((-b'*pw,-b'*pw,0)-dp*Cw)/C,
DH_ij*w=delta_ij*b'*pw+(wi*b'+Ti*b''*pw)*dp_j+Ti*b'*Ddp_j*w.
DJ*w=-2*pw*I-2*(w[:2]-H*w)*ones(1,2).
DF0*w=TS*v_s,x*(Xz+D*H)*w, DG0 analogously with Q.
Rate derivatives and Hessian contractions differentiate every factor position
of the canonical mass-action polynomial, including repeated factors.
The exact Jacobian of the formal RHS is DF0+TS*(v_s,xx[phi*w,D*h1]
+v_s,x*D*Dh1*w), phi=Xz+D*H. Independent checks use complex-step
on the analytic root/rate implementation and centered Richardson finite
differences; branch selection depends on the real part away from its join.
Complex-step step=1e-25 times a normalized direction; directional slopes are
rescaled to physical flow. The root join itself and zero physical boundaries
are recorded as conditioning/domain diagnostics. No nonanalytic clipping is
used. Derivative relative error denominator has the registered 1e-12 floor;
1e-6 relative comparison is an engineering verifier allowance, not D/F gate.

## Initial layer and extents

Reuse hash-verified R6 native BDF dense startup (primary and tighter probe),
the original x0 and tau0=1/(2*p0+1000). switch=10*eta*tau0 is unchanged.
At switch start each fresh formal solve from T*x_full(switch)-z0. No fitted
initial values or projection of the source occurs. Reconstruct h0+h1 at the
boundary and report its jump. Exact R6/full startup cumulative net extent
from zero is retained. Append integration of j0+j1 on the outer trajectory.
Postprocessing uses the existing R6 zero-order native slow dense polynomials;
it is explicitly not a self-consistent model. No h2 or gross correction is
needed. Source data, grids, windows, uncertainty envelopes and historical H
classifications remain untouched.
'''

PREREG=r'''# R7 CK first-order preregistration v1

This bounded feasibility study is authorized solely for R3_BASE, R3_ATP_LOW,
R3_TRNA_LOW. No other condition, R3_ADVERSE, full nine-condition campaign,
aminoacylation work, push, merge or scientific promotion is authorized.
The four fast reactions and all 964 slow reactions are unchanged.

Inputs and all 3079 pre-R7 files are SHA-256 bound in pre_r7_snapshot.json.
The actual R6 Git execution parent is 1181ab2f0a04d72cf76fb069be6bb842e3de75d8;
R6's final execution state was uncommitted, so its final commit SHA is N/A.
An additive local preservation commit records its exact completed files in R7.
This distinction must remain visible in the lineage report.

Freeze this document, authorization, derivation, numerical contract, executable
R7 implementation and input provenance with registration_binding.json before
any decisive R7 comparison. One registration only; never rebind after results.

Objects: ZERO_ORDER_R6, FIRST_ORDER_POSTPROCESSING_ON_Z0, and
FORMAL_FIRST_ORDER_SELF_CONSISTENT, all compared with CANONICAL_FULL_SOURCE.
Source and R6 zero-order evidence are reused after checking hashes, condition
definitions, original x0, native dense data and completed R6 result records.
Fresh primary and tighter formal slow solves are mandatory for each condition.
Analytic Dh1 is primary; complex-step is independent; centered Richardson is
a further diagnostic. Structure checks, graph residuals, eta-family identities,
h0 equality, j0 equality, j1 identity and analytic formal Jacobian are tested.

Scoring is exactly R6: FULL_WINDOW and POST_INITIAL_LAYER mandatory;
POST_0P05_DIAGNOSTIC and COMPOSITE_OR_HYBRID descriptive. State/coordinate
floor=1e-6, gate=.01; current floor=1e-9, gate=.05; extent floor=1e-6, gate=.01;
exact-law drift absolute gate=1e-8. Window scale=max(max|source|,floor).
Use primary BDF rtol=1e-10, atol=1e-14; probe 1e-11,1e-15. Net extents use
segmented DOP853, compensated accumulation, the same primary/probe tolerances
and a tighter quadrature on each primary outer trajectory. Reuse the R6/R4
source uncertainty and startup probe. Current cancellation uses 8*eps times
the two source directed rates; extents use 8*eps times source gross cumulative
extents solely for uncertainty accounting, never E/G scoring. Uncertainty sums
source/probe, reduced/probe and quadrature/cancellation. Bound each state or
extent solve to the frozen R6 1800s (state RHS <=300000). Preserve noncompletion.

Resolved status: uncertainty <=.1*gate required. error+uncertainty<=gate gives
RESOLVED_PASS; max(0,error-uncertainty)>gate gives RESOLVED_FAIL; otherwise
NUMERICALLY_UNRESOLVED. Score all frozen R6 mandatory D/F channels as well as
the two CK pairs. A includes unaffected states and all 212 slow coordinates;
B uses exactly R6 algebraically affected species; C checks both full source
and formal model exact SOURCE_GENERAL laws. No H historical reclassification.

Record each pair's signed current, source maximum, floor, absolute error,
worst time, sampled zero crossings (linear diagnostic estimates plus brackets,
no time shift) and cumulative contributions. No altered denominator or window.
Report ||h1||/max(||h0||,1e-6) and ||h1||/max(||fast totals||,1e-6), individual
physical CK free/bound margins, distance outside the physical polytope,
Gq condition number, minimum singular value and stability distance. The
descriptive FIRST_ORDER_CORRECTION_NOT_SMALL flag uses ratio>=1 against
the fast-state scale, frozen prospectively; it is not an acceptance gate.
Material new CK-domain failure means correction-induced negative CK margin
larger than the corresponding frozen .01*max(full-source state scale,1e-6)
plus probe envelope. Strict negative margins and accepted totals are always
reported separately with no clipping and no positivity threshold mutation.

Advance ONLY if on all three conditions the formal model has A/B/C all
RESOLVED_PASS, D and F both FULL_WINDOW and POST_INITIAL_LAYER RESOLVED_PASS,
no noncompletion and no new material physical-domain failure. E/G are
SOURCE_PROVENANCE_PRESERVED / DESCRIPTIVE / BUT_NOT_VALIDATED, never gates.
If any advancement requirement fails, STOP with no broader run.

Choose exactly one primary recommendation from the human-authorized list.
Priority: ill-posed derivation; noncompletion/unresolved essential scores;
all advancement requirements met; correction comparable to fast-state scale;
current-only improvement; extent-only improvement; states valid and both
improved but failing; no material improvement. Improvement is descriptive:
both full and post-layer maximum CK errors decrease in each condition;
all numerical scores remain present. Additional flags are allowed.
PURE_reduced_core remains NOT_VALIDATED; all 968 decisions remain PENDING.
Derived evidence_navigation.json records EXTRACTED/INFERRED/AMBIGUOUS status,
source hashes and freshness, subordinate to canonical evidence.
'''

def main():
    assert not (OUT/'registration_binding.json').exists(),'REGISTRATION_ALREADY_EXISTS'
    snap=load(OUT/'pre_r7_snapshot.json')
    for path,h in snap['files'].items():assert sha(ROOT/path)==h,'PRE_R7_MUTATION:'+path
    r6=ROOT/'results/reduction/r6_ck_validation'
    assert load(r6/'verification.json')['status']=='PASS_ENGINEERING_AND_EVIDENCE_VERIFICATION'
    reuse=load(r6/'source_reuse_verification.json')
    selected=[]
    for name in CONDITIONS:
        rec=next(x for x in reuse['conditions'] if x['condition']==name)
        for path,h in rec['file_hashes'].items():assert sha(ROOT/path)==h
        dest=r6/'per_condition'/name/'run_001'
        assert load(dest/'result.json')['status']=='COMPLETED'
        selected.append(dict(condition=name,source_hashes=rec['file_hashes'],r6_comparison_sha256=sha(dest/'comparison.npz')))
    c=load(r6/'formal_numerical_contract.json')
    write_json(OUT/'numerical_contract.json',dict(conditions=CONDITIONS,r6_contract=c,
        derivative_engineering_relative_allowance=1e-6,derivative_relative_floor=1e-12,
        descriptive_not_small_ratio=1,material_domain_budget='frozen state gate budget plus probe',promotion=False))
    for name,body in [('r7_ck_first_order_preregistration_v1.md',PREREG),('r7_ck_first_order_derivation_v1.md',DERIVATION),
        ('r7_ck_first_order_authorization_20261008.md','# R7 authorization, 2026-10-08\n\nThe exact human request is retained in results/reduction/r7_ck_first_order/human_request.txt.\nOnly the three-condition first-order CK feasibility study is authorized. Every pre-R7 file is read-only.\nThe R6 Branch A contract, thresholds, H classifications, canonical parameters and initial values remain frozen.\nNo push, merge, broad campaign, promotion or aminoacylation work.\n')]:
        (ROOT/'docs/reduction'/name).write_text(body.strip()+'\n',encoding='utf-8',newline='\n')
    write_json(OUT/'input_provenance.json',dict(schema='R7_INPUT_PROVENANCE_V1',created_at_utc=stamp(),
        r6_execution_parent_sha=snap['r6_execution_parent_sha'],r6_final_commit_sha=None,
        r6_final_state=snap['r6_final_state'],r6_local_preservation_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        origin_main_sha=snap['origin_main_sha'],pre_r7_snapshot_sha256=sha(OUT/'pre_r7_snapshot.json'),conditions=selected,
        r6_verification_sha256=sha(r6/'verification.json'),r6_registration_sha256=sha(r6/'formal_registration_binding.json'),
        python=sys.executable,python_version=platform.python_version(),numpy=np.__version__,promotion=False))
    paths=[ROOT/'docs/reduction'/x for x in ['r7_ck_first_order_authorization_20261008.md','r7_ck_first_order_preregistration_v1.md','r7_ck_first_order_derivation_v1.md']]
    paths+=list((ROOT/'scripts').glob('*r7*py'))
    paths+=[OUT/x for x in ['input_provenance.json','numerical_contract.json','human_request.txt','pre_r7_snapshot.json']]
    write_json(OUT/'registration_binding.json',dict(schema='R7_FROZEN_REGISTRATION_V1',frozen_at_utc=stamp(),
        decisive_numerical_testing_started=False,conditions=CONDITIONS,file_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}))
    print('R7 registration frozen',sha(OUT/'registration_binding.json'),flush=True)

if __name__=='__main__':main()
