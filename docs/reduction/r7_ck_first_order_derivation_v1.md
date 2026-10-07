# R7 exact CK first-order graph and net-current derivation

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
