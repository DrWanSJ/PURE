# NDK depletion-coordinate engineering addendum: derivation and diagnosis

This note describes an exact numerical coordinate change for the existing
source-derived total-QSSA candidate. It does not propose a different rate law,
parameter set, scenario, gate, observation mapping, comparison window or
initial condition. The original preregistration, frozen `runtime.py`, and
all native failure evidence remain unchanged. Executing the new library
requires the separately frozen engineering addendum; this derivation and
diagnosis perform no new trajectory comparisons.

## What the preserved failures establish

Seven NDK positive-challenge cases stopped in the original reduced solver:
the positive challenge, catalyst half/double, ATP half/double, and GDP
half/double. Every stored traceback reaches SciPy's Radau
`solve_collocation_system` at the internal trial evaluation
`fun(t+ch[i], y+Z[i])`, then fails the retained-inventory domain check. This
occurs before acceptance of that solver step. Thus these failures do not
establish that an accepted physical NDK trajectory consumed negative
resources. Nor do they constitute successful numerical validation.

The frozen solver represents retained inventories as `T=T0+nu*extent`.
NDK's chemical reverse rate is zero, so a physical forward extent increases
monotonically and cannot exceed either initial reactant total. Its RHS
vanishes at reactant exhaustion. An unconstrained collocation/Newton trial
in the extent coordinate can nevertheless overshoot a limiting total,
producing a negative algebraic input before the step is accepted.
Depletion overshoot is therefore a source-consistent engineering diagnosis.
The stored failure exception does not contain the trial time or trial state,
so its exact offending resource and magnitude cannot be recovered from
these tracebacks alone. In these seven scenarios GDP is the smaller initial
reactant total.

`results/energy_cycles_v1/ndk_depletion_diagnosis.json` records the seven exact
failure paths and hashes, the original preregistration hash, and their
common internal-trial signature. None is replaced, overwritten or relabeled
as a pass by the coordinate derivation.

## An exact irreversible-depletion coordinate

Let `L0=min(T_ATP(0),T_GDP(0))>0`, select a limiting reactant, and let
`Delta` be the nonlimiting initial reactant total minus L0. Define

```
R = L0*exp(-q)
xi = L0*(1-exp(-q))
T_limiting = R
T_other_reactant = Delta+R
T_ADP = T_ADP(0)+xi
T_GTP = T_GTP(0)+xi
q(0)=0
```

This is exactly the original resource-total trajectory
`T=T0+(-1,-1,+1,+1)*xi`. On `0<=xi<L0`, the inverse
`q=-log(1-xi/L0)` is one-to-one. Differentiating gives
`dR/dt=-R*dq/dt` and `dxi/dt=R*dq/dt`, hence
`dq/dt=v/R` produces exactly `dxi/dt=v`.

The transformed implementation constructs the remaining reactants directly
from R and Delta. It never obtains a tiny reactant concentration by
subtracting an almost exhausted extent from its initial total. For q>=0
all four retained totals are nonnegative when the initial totals are
nonnegative. The physical RHS has `dq/dt>=0`; source chemistry still
determines how rapidly depletion proceeds. No concentration clipping,
product seeding or parameter modification is used. Internal trial points
remain subject to the original physical closure guard.

## Cancellation of the apparent 0/0 at depletion

Use the notation of `effective_kinetics.md` for the NDK substrate diamond:

```
a = k_ATP*u_ATP              b = k_GDP*u_GDP
q0 = 1000                   kf = 470             kr = 0
L = 1/(q0+b)+1/(q0+a)
beta = q0*q0*L
rAB = a*b*L/(beta+kf)
```

For GDP-limited depletion set `theta=a*L/(beta+kf)`, so `rAB=b*theta`.
The GDP-only occupancy ratio is
`rB=b*(1+q0*theta)/(q0+a)`. The exact resource composition therefore gives

```
T_GDP = u_GDP + Efree*(rB+rAB)
      = u_GDP*[1+Efree*k_GDP*((1+q0*theta)/(q0+a)+theta)]
v = kf*Efree*rAB = u_GDP*kf*Efree*k_GDP*theta
v/T_GDP = kf*Efree*k_GDP*theta /
          [1+Efree*k_GDP*((1+q0*theta)/(q0+a)+theta)]
```

The final expression contains no division by `u_GDP` or `T_GDP`. It is
finite and nonnegative at a physical root, including the GDP-zero boundary.
For ATP-limited depletion exchange a and b, use
`theta=b*L/(beta+kf)`, replace `k_GDP` with `k_ATP`, and replace `q0+a`
with `q0+b`. All microscopic constants are read from the same frozen author
parameter overlay.

At the depletion boundary one reactant is absent, chemical conversion is
zero, and NDK can still bind remaining substrate and products. Its
reverse chemical conversion remains disabled. The nonlimiting reactant and
product totals approach finite values; the original stationary formulas
and a nonsingular physical reconstruction branch supply the continuous
limit of Efree and theta. The rational expression consequently defines the
limit of `v/R`. If both reactants are tied initially, both vanish together,
theta tends to zero and this limit is zero. If `L0=0` initially, the
irreversible source candidate has zero current and remains at the same
static closure; no logarithmic transformation is necessary.

For extremely large finite q, floating-point `exp(-q)` can underflow to
zero. The implementation evaluates the analytically continuous boundary
coefficient there. This is explicitly recorded as numerical underflow,
not a rule replacing a small positive trajectory by zero. The remaining
inventory is never clipped to a floor. Failure of positivity, physical
reconstruction, local invertibility or sampled normal attraction still
stops the candidate.

## Observable and roundoff preservation

`scripts/energy_cycles/ndk_depletion_coordinate.py` exposes
`integrate_reduced_ndk(m,T0,E,grid,rtol,atol)`, returning the same species and
forward/reverse extent layout as the frozen `integrate_reduced`.
It integrates q together with the original directed extent quadratures
from t=0. The forward rate is evaluated as the algebraically equivalent
factorization `R*(v/R)` and the reverse rate is exactly zero. This avoids
dividing a reconstructed rate contaminated by an absolute algebraic-root
residual by an arbitrarily small R.

At an exact closure, the factored rate is exactly
`470*h_NDK_GDP_ATP`. At finite precision, two explicit diagnostics are
retained: the factorized rate minus the original reconstructed source-law
rate, and the directly integrated forward extent minus
`L0*(1-exp(-q))`. The observation/comparison routine continues to evaluate
original source-law currents on the reconstructed state. Thus algebraic
root roundoff and coordinate/quadrature error remain visible and require
numerical convergence evidence. Changing a solver coordinate does not
waive the frozen tolerances or scientific accuracy gates.

The library is restricted to the verified NDK boundary order, net
stoichiometry and zero chemical reverse parameter. It retains the original
closure residual, nonnegativity allowance, total-map singular-value and
sampled fast-tangent checks. It certifies neither global root uniqueness
nor a uniform attraction theorem. Its SHA-256 is
`e2dda344d6121ae62abc92447f50bb877be9442e8f37709164c76ec1d9e62f2c`.
The file was syntax-compiled before freezing; trajectory outcomes belong
only to the separately preregistered engineering execution.
