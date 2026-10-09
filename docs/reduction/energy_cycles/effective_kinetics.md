# Source-derived effective kinetics for the four energy cycles

Status: `KINETIC_CANDIDATE`, `HUMAN_REVIEW_REQUIRED`. The source-derived
stationary enzyme laws below are neither exact dynamical lumpings nor approved
reduced modules. Their acceptance depends on the separately frozen numerical
gates. No approved reduced SBML is generated.

## Source authority and executable derivation

The canonical combined model is
`models/pnas2017_full_reference/original/fMGG_synthesis.xml`, starting commit
`60abf1e371e90f70474bc98174035726cc68f064`. Its SHA-256 is
`dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df`.
The author simulator ZIP and its parameter/initial-value members, rather than
the all-one structural values in this XML, supply operational inputs.
`results/energy_cycles_v1/source_inventory.json` binds the source hashes,
directed reaction IDs, exact MathML stoichiometry, subsystem provenance and
author overlays. Resource composition is inferred from exact binding edges
anchored at the free catalyst; it is not inferred solely from complex names.

Every inspected active law is mass action, `k1` multiplied by the actual
reactant species factors. Each active cycle reaction consumes one live enzyme
state and produces one live enzyme state. Consequently, with the free
resource concentrations held fixed, enzyme dynamics are a finite linear
continuous-time Markov system. This observation derives the candidate law
without fitting protein endpoints, assuming rapid binding equilibrium, or
inventing a Michaelis--Menten denominator.

The implementation is `scripts/energy_cycles/kinetics_analysis.py` (frozen
SHA-256 `f1efc0024c2e69dca3009f3fdd9ad35ea64f986c10de2feb765fd3f6951fcfc2`).
`stationary_explicit` evaluates the formulas below, including complex-step
arguments for differentiation. `generator` independently assembles the
stationary matrix from actual kinetic-law factors and stoichiometry.
`kinetic_analysis.json` records their algebraic comparisons, exact-lumpability
counterexamples, frozen-free spectra and analytically obstructed corners.
These probes are mathematical/implementation checks, not reduction trajectory
comparisons. The reference solver and candidate validation are governed by
`validation_preregistration.json`.

| Unit | Entire source subsystem | Active kinetic coverage | Reference-zero channels |
| --- | --- | --- | --- |
| CK | `re0000000329`--`re0000000353` | `re0000000330`--`re0000000347` | `0329`, `0348`--`0353`: degradation |
| NDK | `re0000000354`--`re0000000378` | `0355`--`0363`, `0365`--`0368`, `0375`--`0378` | `0354`, `0369`--`0374`: degradation; `0364`: reverse chemical conversion |
| MK | `re0000000379`--`re0000000403` | `0380`--`0397` | `0379`, `0398`--`0403`: degradation |
| PPiase | `re0000000404`--`re0000000415` | `0405`--`0412` | `0404`, `0413`--`0415`: degradation |

Abbreviated numbers in this table have the same `re000000` prefix as the full
IDs. The table does not erase zero channels: all remain in the source inventory
and provenance. In particular, NDK `re0000000364_k1=0` is preserved, whereas
PPiase `re0000000408_k1=140` is active.

## Coordinates, exact accounting and the approximation

Write free resource concentrations as `u`, live enzyme occupancies as `h`,
and the exact inferred resource-composition matrix as `C`. Every column of C
describes the free resource molecules stored in one enzyme state. Its free
enzyme column is zero. The enzyme total is `E=sum(h)`.

Two different retained coordinate choices must be distinguished:

1. A free-coordinate candidate uses `u` and evaluates `h=h*(u,E)`. Directly
   evolving `du/dt=nu*v` omits changing bound inventories. Its accounted
   inventory `u+C h*(u,E)` therefore generally fails the exact material ledger.
2. The total-resource candidate retains `T=u+C h`, evaluates the stationary
   enzyme state, and reconstructs free resources by solving
   `T=u+C h*(u,E)` with `u>=0`. It evolves `dT/dt=nu*v` for an isolated unit.
   In coupling, other source reactions act on reconstructed free resources,
   and each bound pool is counted once.

T includes chemically distinct forms, not only broad moieties. ATP, ADP and
AMP remain separate, as do GTP/GDP, CP/Cr and PPi/PO4. T is not a constant
substrate reservoir: its coordinates change under chemical conversion. The
broader moieties that annihilate nu are conserved. The enzyme total is a
parameter only because all degradation channels are zero in this reference.
Activating them invalidates that fixed-enzyme candidate.

The exact channel-level identity is
`d(u+C h)/dt=(S_B+C S_I)j=nu*(j_forward_cat-j_reverse_cat)`.
Binding and release columns cancel, whereas the chemical-conversion columns
remain. This is an exact stoichiometric identity on arbitrary microscopic
states; it does not determine the catalytic current from T. At enzyme
stationarity, `S_I j=0` also implies `du/dt=nu*v` for the frozen-free source
rates. Away from stationarity, free release currents and chemical conversion
currents differ through storage derivatives.

## No exact kinetic lumpability for either declared coordinate set

For each cycle consider state x1 with enzyme total 1 entirely free and each
free resource at 10. Consider x2 with enzyme total 1 entirely in the
substrate-loaded catalytic state (`CK_CP_ADP`, `NDK_GDP_ATP`, `MK_ATP_AMP`, or
`PPiase_PPi`). There are two counterexamples:

- Keeping the same free resource concentrations gives identical retained free
  coordinates and enzyme total, but unequal free-resource derivatives. The
  binding/release rates depend on the omitted occupancy.
- Subtracting the loaded state's exact C-column from the free resources in
  x2 gives identical retained T and enzyme total. All concentrations stay
  nonnegative. Yet x1 has zero catalytic current and x2 has current k_forward,
  so the projected resource-total derivatives differ by `nu*k_forward`.

The second difference is nonzero for all four units. Its maximum coordinate
magnitude in the model's numerical rate scale is 2.527408333 for CK, 470 for
NDK, 511.2 for MK, and 1600 for PPiase; the factors of two in MK and PPiase
come from the exact product coefficients. The first pair and both actual RHS
vectors are saved in `kinetic_analysis.json`. Thus neither retained mapping
satisfies `A f(x)=f_reduced(A x)` on the admissible microscopic state space.
This rules out exact elimination for these coordinate choices. It does not
rule out an exact conservation-based coordinate chart that retains the
remaining physical enzyme degrees of freedom.

## Unique enzyme stationarity at fixed free resources

Use a column-oriented generator Q(u): an active reaction taking enzyme state
i to j contributes its nonnegative pseudo-first-order rate to `Q[j,i]` and
its negative to `Q[i,i]`. All columns sum to zero. Candidate stationarity is

`Q(u) h=0`, `sum(h)=E`, `h>=0`.

At every finite `u>=0`, each live state has an active, positive-rate
dissociation/release path to free enzyme. The source rates on these paths
do not require any free substrate. Therefore all states reach a single
closed communicating class containing free enzyme. A finite generator with
that property has a unique normalized stationary state, its zero eigenvalue
is simple, and all its other eigenvalues have strictly negative real part.
The stationary free enzyme occupancy is strictly positive for E>0, although
some bound occupancies can vanish when resources are absent. This proves
fixed-free existence, uniqueness, positivity and linear attractivity.

It does **not** prove existence or uniqueness after imposing chemically
specific resource totals, global attractivity of the nonlinear constrained
problem, separation from translation-network evolution, or small reduction
error. The measured fixed-free eigenvalues below have this limited meaning.

## CK, NDK and MK: two random-binding diamonds

These three enzymes share seven live states:
`E, EA, EB, EAB, EC, ED, ECD`. The substrate side can bind A then B or B then A;
the product side can release C then D or D then C, with corresponding active
reverse associations. Both branches enter the same fully loaded state.
Chemical conversion is `EAB <-> ECD`.

Across the two diamonds, all eight source dissociation/release rates are q=1000.
Association constants for a given site are also identical in the two binding
orders. These source equalities are a condition of the compact formulas; a
changed parameter set must recheck them or use the general Q-system.

Define the pseudo-first-order associations
`a=k_A*u_A`, `b=k_B*u_B`, `c=k_C*u_C`, `d=k_D*u_D`; let `kf` and `kr` be the
directed catalytic constants. Put

```
L = 1/(q+b) + 1/(q+a)
R = 1/(q+d) + 1/(q+c)
alpha = a*b*L                 beta = q*q*L
gamma = c*d*R                delta = q*q*R
D0 = beta*delta + beta*kr + delta*kf
rAB = [alpha*(delta+kr) + kr*gamma]/D0
rCD = [gamma*(beta+kf) + kf*alpha]/D0
rA = (a+q*rAB)/(q+b)          rB = (b+q*rAB)/(q+a)
rC = (c+q*rCD)/(q+d)          rD = (d+q*rCD)/(q+c)
Efree = E/[1+rA+rB+rAB+rC+rD+rCD]
h = Efree*(1,rA,rB,rAB,rC,rD,rCD)
v = Efree*[kf*alpha*delta-kr*gamma*beta]/D0
```

These expressions follow by eliminating the four binary-state balance
equations and solving the remaining two-by-two system. Every denominator
is strictly positive for the author parameter set and finite `u>=0`.
No binding equilibrium assumption is needed for this stationary identity.

| Unit | A/B/C/D and source state mapping | k_A, k_B, k_C, k_D | kf, kr |
| --- | --- | --- | --- |
| CK | A=ADP, B=CP, C=ATP, D=Cr; EA=`CK_ADP`, EB=`CK_CP`, EAB=`CK_CP_ADP`, EC=`CK_ATP`, ED=`CK_Cr`, ECD=`CK_Cr_ATP` | 19.60784314 (`0330`/`0334`), 2 (`0332`/`0336`), 1.369863014 (`0345`/`0341`), 0.204081633 (`0347`/`0343`) | 2.527408333 (`0338`), 0.548808667 (`0339`) |
| NDK | A=ATP, B=GDP, C=ADP, D=GTP; EA=`NDK_ATP`, EB=`NDK_GDP`, EAB=`NDK_GDP_ATP`, EC=`NDK_ADP`, ED=`NDK_GTP`, ECD=`NDK_GTP_ADP` | 0.555555556 (`0355`/`0359`), 20.40816327 (`0357`/`0361`), 15.15151515 (`0378`/`0375`), 6.666666667 (`0377`/`0376`) | 470 (`0363`), **0** (`0364`) |
| MK | A=ATP, B=AMP, C=ADP site 1, D=ADP site 2; EA=`MK_ATP`, EB=`MK_AMP`, EAB=`MK_ATP_AMP`, EC=`MK_ADP_1`, ED=`MK_ADP_2`, ECD=`MK_ADP_ADP` | 16.66666667 (`0380`/`0384`), 8.333333333 (`0382`/`0386`), 1.098901099 (`0395`/`0393`), 35.71428571 (`0397`/`0391`) | 255.6 (`0388`), 345.6 (`0389`) |

MK's two singly ADP-bound states have distinct binding-site constants. They
are not merged. Their shared free ADP argument is used in both c and d,
so the reverse-driving numerator is quadratic in free ADP. The double state
stores exactly two ADP molecules.

The net transformations, in the declared positive direction, are
`CP+ADP <-> Cr+ATP`, `ATP+GDP -> ADP+GTP`, and `ATP+AMP <-> 2 ADP`.
NDK product binding still inhibits and sequesters its enzyme; it does not
create chemical reverse flux when kr=0. Hence its current cannot become
negative at any physical stationary state. CK and MK can have signed reverse
current. For a diamond, the current's sign is that of `kf*a*b-kr*c*d`.
This sign condition is an algebraic consequence of the supplied rates,
not an independently established thermodynamic equilibrium constant.

The two nonnegative terms in the compact v numerator can be presented as
effective forward and reverse contributions, but they are not identical to
the gross microscopic catalytic rates `kf*h_EAB` and `kr*h_ECD`. Opposing
microscopic cycling cancels in the net expression. Reconstructed gross rates
must therefore be calculated from h and their original source laws.

## PPiase: complete reversible binding/conversion/release path

The live states are `E=PPiase`, `ES=PPiase_PPi`,
`EP2=PPiase_PO4_PO4`, and `EP=PPiase_PO4`. The source has

```
E+PPi <-> ES       0405:46*PPi,     0406:200
ES <-> EP2         0407:800,        0408:140
EP2 <-> EP+PO4     0409:440,        0410:0.059*PO4
EP <-> E+PO4       0411:400,        0412:0.26*PO4
```

One turnover releases PO4 twice. The second release cannot be omitted or
replaced by counting the double-bound complex as free product. All eight
channels, including chemical reverse conversion and both product
associations, are nonzero under the author overlay.

Let `a=46*u_PPi`, `b=200`, `kf=800`, `kr=140`,
`c=0.059*u_PO4`, `d=440`, `e=400`, `f=0.26*u_PO4`. Then

```
L0 = kr*b/(b+kf) + d*e/(e+c)
rP2 = [kf*a/(b+kf) + c*f/(e+c)]/L0
rS = (a+kr*rP2)/(b+kf)
rP = (d*rP2+f)/(e+c)
Efree = E/[1+rS+rP2+rP]
(h_ES,h_EP2,h_EP) = Efree*(rS,rP2,rP)
v = Efree*(kf*a-kr*b*rP2)/(b+kf)
  = Efree*(kf*a*d*e-kr*b*c*f)/[(b+kf)*(e+c)*L0]
```

The three stationary currents
`800*h_ES-140*h_EP2`, `440*h_EP2-0.059*u_PO4*h_EP`, and
`400*h_EP-0.26*u_PO4*Efree` all equal v. Thus the boundary projection is
`dPPi/dt=-v`, `dPO4/dt=2v`. The actual stationary effective transformation
is **`PPi <-> 2 PO4`**. High PO4 can produce negative v and synthesize PPi.
An irreversible `PPi -> 2 PO4` candidate would contradict this author-input
network in a reverse-driving condition. No water, protons, Mg or charge
balancing species are added to this source-representation equation.

## Physical total-resource reconstruction: conditional, not global

For one cycle solve
`G(u;T,E)=u+C h*(u,E)-T=0` within `0<=u<=T`.
For coupling, replace C h by the sum of the distinct enzyme inventories
sharing that resource. Free and total pools must not be counted twice.

Fixed-free uniqueness of h is insufficient to establish uniqueness or even
existence of u. A root with positive free resources has a local smooth branch
if `M=I+C*(Dh*/Du)` is nonsingular. The implicit function theorem gives local
uniqueness and sensitivity `Du/DT=M^-1` there. It does not give global
uniqueness, select an untested branch, or make all nonnegative T admissible.
Deterministic multistart agreement is evidence for the sampled root, not a
proof excluding other roots throughout the domain.

Local attraction under the candidate's constrained fast-layer interpretation
must be checked separately. For `F(h;T)=Q(T-C h)h`, its derivative is

`D_hF=Q-[ (dQ/du_1)h ... (dQ/du_r)h ] C`,

restricted to the enzyme-conservation tangent `sum(delta h)=0`. The
zero normalization mode is removed before examining eigenvalues. This
derivative differs from frozen-free Q because sequestration changes u.
Negative eigenvalues of Q alone cannot substitute for this check. A local
normal-attraction calculation still does not certify the full coupled
trajectory or a singular-perturbation error bound at the finite author E.

The closure is not onto the entire nonnegative total-resource orthant.
There are exact no-root corners with E>0:

| Unit | Positive substrate totals | Zero product totals | Contradiction at enzyme stationarity |
| --- | --- | --- | --- |
| CK | T_CP>0, T_ADP>0 | T_ATP=T_Cr=0 | All product-bound states vanish; the product ternary balance demands `k0338*h_CK_CP_ADP=0`, but positive substrate totals and stationary binding force this occupancy positive. |
| NDK | T_ATP>0, T_GDP>0 | T_ADP=T_GTP=0 | The product ternary must vanish, contradicting positive `k0363*h_NDK_GDP_ATP`. |
| MK | T_ATP>0, T_AMP>0 | T_ADP=0 | Both single-ADP states and the double-ADP state vanish, contradicting positive `k0388*h_MK_ATP_AMP`. |
| PPiase | T_PPi>0 | T_PO4=0 | Both phosphate-bound states vanish, contradicting positive `k0407*h_PPiase_PPi`. |

To justify the positivity step, stationary free enzyme is positive and every
binding has positive dissociation. At the supposed zero-product root,
positive substrate totals cannot reside in substrate-bound states while their
free substrate is zero: the associated stationary equations would force
those bound states to zero. Thus the free substrate(s) and the fully loaded
substrate state must be positive. Chemical conversion then supplies a product
state forbidden by the zero product total. This is an algebraic impossibility,
not merely a solver convergence failure.

Reverse-driven substrate-zero/product-positive corners are obstructed too
when the chemical reverse constant is positive (CK, MK, PPiase). NDK has no
such reverse chemical source under the declared overlay. Report an infeasible
corner or trajectory leaving the tested branch as `OUTSIDE_CLOSURE_DOMAIN`;
do not seed products, clip concentrations, refit rates, or silently move the
initial time to manufacture a root. Retaining physical intermediate dynamics
or a separately derived alternative approximation is required to cover such
conditions.

Author baseline free inputs have zero catalytic current in every isolated
cycle: CK lacks ADP and Cr, NDK lacks GDP and ADP, MK lacks AMP and ADP, and
PPiase lacks PPi and PO4. Fixed-free stationarity therefore exists there.
This does not show that the total closure stays physical when other modules
introduce substrate. For example, new CK ADP can enter before sufficient Cr
inventory has been generated to support a stationary product-bound pool.
The solver must guard physical reconstruction throughout integration.

## Fast-layer assumptions and measured scope

The generator reduction formally eliminates normalized enzyme occupancies
when they relax rapidly compared with changes in free resources and their
source-driven forcing. A small enzyme/resource ratio, a well-conditioned
physical reconstruction branch, a uniform normal spectral gap, slowly varying
forcing and compatible initial data are relevant conditions. Large binding
constants alone do not establish them. All-enzyme stationarity also includes
chemical conversion, not only rapid binding; NDK conversion 470 and PPiase
conversion 800 are comparable to their release constants.

The algebraic script measures the following gaps (inverse model time), with
all stated spectra excluding the normalization zero mode:

| Unit | Frozen-free author initial gap | Frozen-free interior u_i=100 gap | Interior relaxation time |
| --- | ---: | ---: | ---: |
| CK | 999.9999173 | 930.0921801 | 0.00107516 |
| NDK | 999.9999854 | 775.0267731 | 0.00129028 |
| MK | 1000 | 842.2804247 | 0.00118725 |
| PPiase | 394.9050747 | 867.9246397 | 0.00115218 |

These are actual source-parameter matrix calculations at two declared frozen
free states. They are not a measured ratio to a full-model slow timescale and
do not establish observed uniform separation through 1000 seconds. The
explicit stationary occupancies agree with independent linear solves within
1.43e-14; largest unscaled Qh residual is 3.64e-12. These are bounded algebraic
checks only. Trajectory spectra, conservation, initial-layer errors, fluxes
and extents belong to the preregistered numerical report.

Original author enzyme inventories are initially entirely free. CK, NDK and
MK have nonzero baseline substrate/product binding, so this microscopic state
differs from the reconstructed stationary occupancy. A QSSA projection
changes free-versus-bound inventories immediately unless it uses a feasible
matched T. The initial transient must remain visible at t=0 and in the
0--0.05 and 0.05--1 windows; cumulative source currents start at t=0. An
initially projected condition and an original non-equilibrium condition
answer different questions and require separate results.

## Conservation, sensitivity, units and observables

The following composition-supported moieties include bound inventory through
T. In each case add the separately conserved live-enzyme total:

| Unit | Independently conserved resource moieties |
| --- | --- |
| CK | T_ATP+T_ADP; T_CP+T_Cr; 3T_ATP+2T_ADP+T_CP |
| NDK | T_ATP+T_ADP; T_GTP+T_GDP; 3T_ATP+2T_ADP+3T_GTP+2T_GDP |
| MK | T_ATP+T_ADP+T_AMP; 3T_ATP+2T_ADP+T_AMP |
| PPiase | 2T_PPi+T_PO4 |

These are molecular-group ledgers supported by the represented chemistry,
not a complete elemental/ionic conservation proof. The exact left-nullspace
calculation and disabled-channel consequences are in the stoichiometric
certificate. `MK_ADP_ADP` stores two adenylates; `PPiase_PO4_PO4` stores two
PO4 molecules. Binding is sequestration, not ATP hydrolysis. A PPi molecule
is not interchangeable with a PO4 molecule for particle count. Any
source-representation particle proxy has to specify whether a bound complex
is counted as one particle; it cannot establish osmotic pressure or ionic
strength without physicochemical metadata.

The formulas show depletion and inhibition directly: missing reactant
reduces its binding factors, product loading occupies catalyst even for
NDK's chemically one-way conversion, and bidirectional net currents can be
small differences of appreciable gross currents. Near depletion, E divided
by a relevant resource inventory becomes large; near a domain boundary,
M can become ill-conditioned and free reconstruction becomes sensitive.
Local sensitivity must include `Du/DT=M^-1`, rather than differentiating
only the fixed-free rate. A denominator positive at every fixed u does not
protect the total-coordinate domain or an integration across it.

In abstract concentration/time dimensions, association k has
`[concentration]^-1[time]^-1`, unimolecular release/conversion k has
`[time]^-1`, pseudo-first-order a--f, alpha--delta have `[time]^-1`, h has
`[concentration]`, and v has `[concentration]/[time]`. These are formal
dimensions of the concentration ODE. The canonical SBML has no explicit
unit definitions and supplies inadequate species/local-parameter unit
metadata; author CSVs provide no units. The historical execution uses a
seconds-labeled numerical interval, but physically validated absolute
concentration/time units are not established here. No physical unit claim
is repaired by a successful numerical import.

Reconstruction supplies conditional stationary occupancies and, from them,
all source-law instantaneous directed rates. It cannot recover actual
off-manifold occupancy transients, initial-layer sequestration/release,
history-dependent directed extents, dwell times, or their errors from only
T. Those observables require microscopic comparison or additional dynamic
states. Even accurate retained-pool trajectories and a protein endpoint
cannot substitute for the separately registered resource-flow and net-flux
gates.

In the author-reference active network, eliminating all live enzyme-state
variables would replace seven enzyme states per CK/NDK/MK and four for
PPiase by reconstruction. After removing each conserved enzyme-total degree
of freedom, that removes six, six, six and three independent physical enzyme
degrees of freedom, respectively. Four-cycle coupling retains nine distinct
resource-total variables and four fixed enzyme totals; it does not have
only four independent dynamic states by virtue of four net reactions.
Whether these eliminations are actually acceptable is decided only by the
preregistered evidence. Failure requires keeping or revising the microscopic
state description and preserves all earlier reduction decisions unchanged.
