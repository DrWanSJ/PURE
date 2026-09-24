# D7 reduction certificate — RS explicit mechanism and QSSA

**Status: D7 = COMPLETE for analytical derivation + synthetic main-backbone numerical validation.**
This does not establish experimental/microscopic validity of the one-intermediate aaRS surrogate.

**Input model:** frozen B1 Mavelli literature-reference backbone at commit `c2bb0ae63ba106d4f51bf2182dfd28dfe187e743`. The canonical model definition, parameters, generated RHS, and D1–D6 science are unchanged. D7 preregistration and acceptance criteria entered history in commit `cec84861ab829bf451d6902283e5f078a6e89401`, before formal validation.

**Scope:** the actual PURE aminoacylation (RS) module is expanded into a minimal explicit fast-intermediate surrogate, then reduced by QSSA. The evidence category is **derived + synthetic numerical validation; NOT experimentally supported**. Numerical results are reported in Section 8, with the synthetic evidence boundary retained.

## 1. Baseline, chemical interpretation, and interfaces

The frozen backbone uses the coarse-grained reaction

\[
A+T+NTP \xrightarrow{RScat} AT+NXP.
\]

Mavelli §2.2 describes aminoacyl-tRNA synthetases, ATP consumption, AMP and PPi production, while the backbone pools energy species into generic NTP/NXP and describes RS using apparent Michaelis-Menten factors. This D7 construction is a **model extension for reduction analysis**, not a derivation of the canonical apparent rate law from a unique microscopic mechanism.

Let \(E\) denote free RScat and \(M=RScat\cdot A\!-\!AMP\) the single activated intermediate. The conceptual chemistry is

\[
E+A+ATP \underset{k_{-1}}{\overset{k_1}{\rightleftarrows}} M,
\qquad M+T\xrightarrow{k_2}E+AT+AMP.
\]

This is deliberately lumped, not a complete elementary aaRS mechanism. PPi is not a dynamic state. The reverse constant \(k_{-1}\) is **apparent pseudo-first-order**: the assumed PPi effect is absorbed into it. No PPi state or ATP-specific experimental model is introduced.

The implemented backbone interface is explicitly

\[
ATP_{RS}:=NTP,\qquad AMP\mapsto NXP,
\qquad f_{TA}=\frac{p.n_T}{p.n_A},\qquad T_{eff}=f_{TA}T.
\]

The notation \(NTP_{RS}\), when used, means this same canonical NTP coordinate. The ATP-to-NTP mapping is bookkeeping for the coarse-grained Mavelli backbone; it does not claim that all NTP species are ATP. With frozen multiplicities, \(f_{TA}=46/20=2.3\), but every runtime calculation derives the factor from `p.n_T/p.n_A` rather than hardcoding the decimal.

Within the declared two-state enzyme model,

\[
E_T=p.RScat=E+M,\qquad E=E_T-M.
\]

The physical state order is

\[
\mathbf y=(NTP,NXP,nt,A,T,AT,a,CP,C,TLcat,M)^T,
\]

and the reduced slow order is its first ten coordinates \(\mathbf s\). DNA, TXcat, RScat and ENcat remain fixed inputs. Two no-feedback accounting integrators, \(D_{nt}\) and \(D_{TLcat}\), accompany simulation for reproducible balance checks.

## 2. Full explicit extension and backbone coupling

The two implemented RS steps are

\[
v_{1f}=k_1A\,NTP(E_T-M),\qquad
v_{1r}=k_{-1}M,\qquad
v_{1net}=v_{1f}-v_{1r},\qquad
v_2=k_2M f_{TA}T.
\]

All non-RS rates \(V_{TX},V_{nt,deg},V_{TL},V_{TL,deg},V_{EN}\) are obtained by calling `rhs_pure_literature_reference`. Their rate laws are not copied into the extension. Canonical \(V_{RS}\) is retained only for reference/provenance and never contributes to a D7 state update. Returned rate slot 3 contains actual transfer \(v_2\).

The full equations are

\[
\begin{aligned}
\dot{NTP}&=(-V_{TX}-2V_{TL}-v_{1net}+V_{EN})/n_{NTP},\\
\dot{NXP}&=2V_{TL}+v_2-V_{EN},\\
\dot{nt}&=V_{TX}-V_{nt,deg},\\
\dot A&=-v_{1net}/n_A,\\
\dot T&=(-v_2+V_{TL})/n_T,\\
\dot{AT}&=(v_2-V_{TL})/n_T,\\
\dot a&=V_{TL},\\
\dot{CP}&=-V_{EN},\qquad \dot C=V_{EN},\\
\dot{TLcat}&=-V_{TL,deg},\\
\dot M&=v_{1net}-v_2.
\end{aligned}
\]

Activation consumes one amino-acid moiety and one NTP-derived moiety; transfer releases the exhausted nucleotide into NXP and transfers the amino-acid moiety to AT. This split is essential: using \(v_2\) for activation consumption before QSSA would omit transient storage in \(M\).

Define the effective first-order rates

\[
\alpha=k_1A\,NTP,\quad \beta=k_{-1},\quad
\gamma=k_2 f_{TA}T,\quad D=\alpha+\beta+\gamma.
\]

Then

\[
G(\mathbf s,M)=\dot M=\alpha E_T-DM.
\]

The relevant fast/slow comparison is between these effective rates and backbone evolution, not directly between microscopic constants with different units.

## 3. QSSA derivation and reduced implementation

QSSA requires \(\dot M\approx0\), **not** \(M\approx0\). Solving \(G(\mathbf s,h)=0\) gives

\[
\boxed{M_{qss}=h(\mathbf s)=\frac{E_Tk_1A\,NTP}
{k_{-1}+k_2 f_{TA}T+k_1A\,NTP}=\frac{E_T\alpha}{D}.}
\]

On this manifold, \(v_{1net}=v_2\), so

\[
\boxed{V_{RS}^{qss}=k_2 f_{TA}T h
=\frac{k_1k_2E_T A\,NTP\,f_{TA}T}
{k_{-1}+k_2 f_{TA}T+k_1A\,NTP}.}
\]

`rhs_pure_rs_qssa` evaluates the explicit extension at \(M=h(\mathbf s)\) and returns its ten slow components. Thus it is \(\dot{\mathbf s}=F(\mathbf s,h(\mathbf s))\), and naturally recovers the coarse RS stoichiometric pattern with the surrogate QSSA flux. It is not a separately selected empirical rate law.

**This QSSA rate is not algebraically identical to Mavelli Eq. (8).** It is the reduced law of the explicitly declared one-intermediate surrogate. Local matching below does not establish global equality to the product of three apparent Michaelis-Menten factors.

## 4. Synthetic micro-parameter provenance

The frozen Mavelli model supplies apparent RS kinetics and the average catalyst concentration; these do not uniquely identify microscopic constants for this specific lumped two-step mechanism. No unrelated aaRS microscopic constants or apparent Michaelis constants are reinterpreted as such a source. The D7 micro-parameters are labeled **`synthetic_reduction_only`** in [the machine-readable parameter record](../../models/reductions/rs_qssa/parameters.json), without altering the canonical parameter file.

The construction uses canonical \(\mathbf y_0\):

\[
A_0=300\ \mu M,\quad NTP_0=1500\ \mu M,\quad
T_0=1.9\ \mu M,\quad T_{eff,0}=4.37\ \mu M,\quad E_T=0.16\ \mu M.
\]

The fixed, preregistered fractions are

\[
\phi_\alpha=0.05,\quad \phi_\beta=0.90,\quad
\phi_\gamma=0.05,\qquad \phi_\alpha+\phi_\beta+\phi_\gamma=1.
\]

Let \(V_{RS,ref}\) be canonical rate slot 3 evaluated at \(\mathbf y_0\). Define

\[
D_{ref}=\frac{V_{RS,ref}}{E_T\phi_\alpha\phi_\gamma},\qquad
(\alpha_{ref},\beta_{ref},\gamma_{ref})
=D_{ref}(\phi_\alpha,\phi_\beta,\phi_\gamma),
\]

\[
k_1=\frac{\alpha_{ref}}{A_0NTP_0},\qquad
k_{-1}=\beta_{ref},\qquad
k_2=\frac{\gamma_{ref}}{T_{eff,0}}.
\]

These formulas imply exactly, before floating-point roundoff,

\[
h_0=E_T\phi_\alpha=0.008\ \mu M,\qquad
V_{RS}^{qss}(\mathbf y_0)=E_T\phi_\alpha\phi_\gamma D_{ref}=V_{RS,ref}.
\]

Reference values calculated from the frozen canonical inputs are shown below; formal MATLAB validation confirms their numerical realization.

| Quantity | Value | Units |
|---|---:|---|
| \(V_{RS,ref}\) | 0.7007227534243771 | \(\mu M\,s^{-1}\) |
| \(D_{ref}\) | 1751.806883560943 | \(s^{-1}\) |
| \(\alpha_{ref}\), \(\gamma_{ref}\) | 87.59034417804713 | \(s^{-1}\) |
| \(k_1\) | 0.0001946452092845492 | \(\mu M^{-2}s^{-1}\) |
| \(k_{-1}\) | 1576.626195204849 | \(s^{-1}\) |
| \(k_2\) | 20.04355702014809 | \(\mu M^{-1}s^{-1}\) |
| \(\tau_{M,ref}\) | 0.0005708391771856008 | \(s\) |

This is a reproducible **synthetic local matching construction**, not parameter fitting, not a literature kinetic-constant assignment, and not a match over the full state domain. It provides no microscopic or experimental support for the surrogate.

## 5. Fast relaxation, moving manifold, and epsilon

For frozen \(A,NTP,T\), write \(M=h+\delta M\). Then

\[
\dot{\delta M}=-D\delta M,\qquad
\delta M(t)=\delta M(0)e^{-Dt},\qquad
\boxed{\tau_M=1/D.}
\]

For positive constants and nonnegative substrates, \(D>0\). This scalar relaxation identity supports the isolated fixture; it is not an interpretation of full-system Jacobian eigenvalues, which is outside D7.

Along the actual backbone, \(h(t)=h(A(t),NTP(t),T(t))\) moves. The QSSA question is whether relaxation toward the current target is fast enough relative to its movement; QSSA does not require \(M(t)\) to remain constant.

The fixed-state diagnostic uses fixed nonzero reference scales

\[
A_{scale}=A_0,\quad NTP_{scale}=NTP_0,\quad T_{scale}=T_0,
\]

\[
\tau_A=\frac{A_0}{|\dot A|},\quad
\tau_{NTP}=\frac{NTP_0}{|\dot{NTP}|},\quad
\tau_T=\frac{T_0}{|\dot T|},\quad
\tau_{slow,state}=\min(\tau_A,\tau_{NTP},\tau_T),
\]

\[
\epsilon_{state}=\tau_M/\tau_{slow,state}.
\]

Using fixed scales avoids a near-zero instantaneous concentration in a diagnostic denominator. A zero derivative gives the corresponding timescale \(\infty\).

The moving-manifold diagnostic uses \(M_{scale}=E_T\):

\[
\dot h=h_A\dot A+h_{NTP}\dot{NTP}+h_T\dot T,\qquad
\tau_{slow,track}=\frac{E_T}{|\dot h|},\qquad
\epsilon_{track}=\tau_M/\tau_{slow,track}.
\]

If \(\dot h=0\), its timescale is \(\infty\). The audit records min/median/max \(\tau_M\) and \(\tau_{slow,state}\), and both maximum epsilons on the complete output grid. The preregistered \(\max\epsilon_{state}<10^{-2}\) criterion is an engineering gate for this **synthetic fast_ref profile**, not a universal QSSA theorem. Tracking epsilon is reported, not used alone as evidence of physical validity.

QSSA is distinct from rapid equilibrium. A stronger rapid-equilibrium assumption would additionally require reversible activation to equilibrate much faster than downstream drain, schematically \(\alpha+\beta\gg\gamma\), with appropriate equilibrium assumptions. The implemented reduction solves \(v_{1net}-v_2=0\), not \(v_{1net}=0\); it does not impose rapid equilibrium.

## 6. Complete analytic chain-rule Jacobian

The nonzero manifold derivatives, in the actual backbone coordinates, are

\[
h_A=\frac{E_Tk_1NTP(\beta+\gamma)}{D^2},\qquad
h_{NTP}=\frac{E_Tk_1A(\beta+\gamma)}{D^2},\qquad
h_T=-\frac{E_Tk_1A\,NTP\,k_2 f_{TA}}{D^2}.
\]

All other entries of the \(1\times10\) row \(h_s\) vanish. For

\[
\dot s=F(s,M),\qquad \dot M=G(s,M),
\]

implicit differentiation of \(G(s,h(s))=0\) gives

\[
h_s=-G_M^{-1}G_s,\qquad G_M=-D.
\]

The explicit RS slow stoichiometric columns are

\[
b_1=(-1/n_{NTP},0,0,-1/n_A,0,0,0,0,0,0)^T,
\]

\[
b_2=(0,1,0,0,-1/n_T,1/n_T,0,0,0,0)^T.
\]

Consequently,

\[
F_s=J_{nonRS}+b_1(v_{1net})_s+b_2(v_2)_s,\qquad
F_M=-b_1(\alpha+\beta)+b_2\gamma,
\]

\[
G_s=(v_{1net})_s-(v_2)_s,
\]

where these partial derivatives hold \(M\) fixed:

\[
(v_{1net})_{NTP}=k_1A(E_T-M),\quad
(v_{1net})_A=k_1NTP(E_T-M),\quad
(v_2)_T=k_2M f_{TA}.
\]

The required reduced derivative is therefore

\[
\boxed{J_{slow}=F_s+F_Mh_s=F_s-F_MG_M^{-1}G_s,\quad M=h(s).}
\]

`rs_explicit_jacobian_blocks` constructs all four analytic blocks; `jacobian_pure_rs_explicit` assembles the full \(11\times11\) derivative. `jacobian_pure_rs_qssa_chain` includes the complete \(F_Mh_s\) correction. Mechanically removing the \(M\) row and column would leave only \(F_s\) and is not this reduction.

The non-RS derivatives follow the existing canonical dimensional saturation functions and the D6 analytic-derivative pattern, including the multiplicity chain factor in translation. Complex-step checks cover the **complete** reduced RHS Jacobian, the full explicit Jacobian, and \(h_s\). D7 addresses derivative correctness, not Jacobian eigenvalue interpretation or D9 stability.

## 7. Extended conservation and initialization

The simulators integrate

\[
\dot D_{nt}=V_{nt,deg},\qquad \dot D_{TLcat}=V_{TL,deg},
\]

without feedback. The full explicit balances are

\[
\begin{aligned}
B_{NTP}^{explicit}&=n_{NTP}NTP+NXP+nt+D_{nt}+M,\\
B_{AA}^{explicit}&=n_AA+a+n_TAT+M,\\
B_{tRNA}&=n_TT+n_TAT,\\
B_{CP}&=CP+C,\\
B_{TLcat}&=TLcat+D_{TLcat}.
\end{aligned}
\]

Here \(n_AA\) means \(n_A\,A\), and \(n_TAT\) means \(n_T\,AT\). In particular,

\[
\dot B_{NTP}^{explicit}=(-v_{1net}+v_2)+(v_{1net}-v_2)=0,
\quad
\dot B_{AA}^{explicit}=(-v_{1net}+v_2)+(v_{1net}-v_2)=0;
\]

all non-RS terms cancel independently. The last three derivatives also cancel identically.

The original sixth invariant needs no added \(M\):

\[
I_6=NXP+C-3a-n_TAT,
\]

because direct substitution gives

\[
\dot I_6=(2V_{TL}+v_2-V_{EN})+V_{EN}-3V_{TL}
-(v_2-V_{TL})=0.
\]

These identities are checked numerically using synchronously integrated accounting states, with no projection or clipping.

The QSSA ten-state system preserves the corresponding **coarse** NTP and amino-acid balances without \(h(s)\). Appending the moving value \(h(s)\) to those balances would generally add \(\dot h\), so it is not an invariant of the chosen QSSA coordinates.

Primary full and reduced simulations start with the **same canonical ten slow initial values**. The full model additionally starts at \(M_0=h(s_0)=0.008\ \mu M\). Hence the full initial \(B_{NTP}\) and \(B_{AA}\) inventories exceed their reduced coarse counterparts by \(M_0\); inventories are checked against each model's own initial constants. No slow initial-state adjustment, projection, or hidden inventory correction is made to improve agreement.

Starting on \(M=h(s)\) avoids an imposed off-manifold fast layer in the primary comparison. For arbitrary \(M_0\ne h(s_0)\), a fast layer of a few \(\tau_M\) is expected. A separate frozen-slow fixture uses \(M_0=0.5E_T\) to check the analytic exponential and measured relaxation time. That fixture is a unit test; primary acceptance depends on the real backbone trajectories.

## 8. Preregistered numerical validation

The audit is [rs_qssa_d7_20260924](../audit/rs_qssa_d7_20260924/README.md). [Preregistration](../audit/rs_qssa_d7_20260924/preregistration.json) and [acceptance criteria](../audit/rs_qssa_d7_20260924/acceptance_criteria.json) were committed before the first formal run.

The primary domain is DNA = 0.00034, 0.0017, and 0.0068 \(\mu M\), 0–14400 s, every 10 s, with 1441 points per DNA. MATLAB `ode15s` uses analytic Jacobians, `RelTol=1e-10`, `AbsTol=1e-12`. The full and QSSA trajectories compare all ten slow physical states, transfer flux, mRNA \(nt/(3L)\), and protein \(a/L\). Full \(M\) versus reconstructed \(h\) is supplemental, not a comparison of two independent fast states.

The frozen gates are: reference match and normalized algebraic residual \(\le10^{-12}\); manifold derivative \(\le10^{-10}\); full and chain Jacobians \(\le10^{-8}\); fast fixture \(\le10^{-6}\); slow states, transfer flux, mRNA and protein \(\le10^{-3}\); invariants \(\le10^{-8}\); and \(\max\epsilon_{state}<10^{-2}\). Per-quantity trajectory errors use each full trajectory's fixed peak absolute scale, with a \(10^{-12}\) floor. The existing D6 roundoff convention determines negativity tolerance as specified in the criteria. Finite physical concentrations, free enzyme \(E_T-M\), no clipping, no projection, and no `NonNegative` solver option are required.

All new/modified MATLAB files must pass `checkcode` review; the D7 suite and complete repository suite must report native Passed / Failed / Incomplete counts. A second complete suite run is required before final commit. Any initial failure is retained with its implementation revision; scientific equations and acceptance thresholds cannot be changed to hide it.

<!-- D7_VALIDATION_RESULTS -->

**All preregistered scientific gates PASS in run_002.** MATLAB R2025b Update 5.
D7 native TestResult counts: **13 Passed / 0 Failed / 0 Incomplete**.
Repository: **102 Passed / 0 Failed / 0 Incomplete**, B1 smoke PASS,
development preflight PASS. All 16 new/modified MATLAB files have zero checkcode messages.
The final precommit repository replay also passed **102 / 0 / 0**, with B1 smoke and development preflight PASS; see `final_regression_results.json`.

Per-quantity peak-normalized errors (threshold 1e-3):

| DNA (uM) | all 10 slow states | transfer flux | mRNA | protein |
|---:|---:|---:|---:|---:|
| 0.00034 | 1.466684018e-07 | 1.300550188e-07 | 1.435403646e-09 | 2.263311529e-09 |
| 0.0017 | 1.438721542e-07 | 1.276005519e-07 | 2.300382894e-09 | 1.039599157e-09 |
| 0.0068 | 2.631278492e-07 | 1.234351368e-07 | 1.010360415e-08 | 2.137101976e-09 |

The raw maxima, scales, every trajectory point, and full/reduced invariant residuals are retained in
[validation_results.json](../audit/rs_qssa_d7_20260924/validation_results.json) and the audit CSV/MAT files.

| Check | Measured maximum | Gate |
|---|---:|---:|
| Reference RS flux match | 0 | 1e-12 |
| Reference M match | 2.168404345e-16 | 1e-12 |
| Algebraic QSS residual | 2.133874166e-16 | 1e-12 |
| Manifold derivative complex-step | 2.168404345e-19 | 1e-10 |
| Complete chain Jacobian complex-step | 2.220446049e-16 | 1e-8 |
| Full explicit Jacobian complex-step | 3.751355959e-16 | 1e-8 |
| Frozen-slow relaxation concentration error | 2.436655912e-10 | 1e-6 |
| Measured tau relative error | 8.295755897e-10 | 1e-6 |
| Extended/coarse invariant normalized residual | 7.389644452e-13 | 1e-8 |

No negative physical, accounting, or free-enzyme values were observed. The largest raw
invariant residual was 9.367795428e-11 uM, while the maximum normalized residual above
is the zero-initial I6 with its preregistered scale 1. The independent random-state
I6 derivative residual is 1.720845688e-14 uM/s; analytic cancellation is exact.

Complete output-grid time-scale summaries:

| DNA (uM) | model | tau_M min / median / max (s) | tau_slow_state min / median / max (s) | max epsilon_state | max epsilon_track |
|---:|---|---|---|---:|---:|
| 0.00034 | full | 0.000570839177 / 0.0006016997 / 0.00060222959 | 124.72836 / 595015.52 / 595279.795 | 4.576659039e-06 | 7.279898727e-09 |
| 0.00034 | reduced | 0.000570839177 / 0.000601699698 / 0.000602229589 | 124.72836 / 595014.521 / 595278.938 | 4.576659039e-06 | 7.279918287e-09 |
| 0.0017 | full | 0.000570839177 / 0.000602812948 / 0.000604691915 | 124.72836 / 149588.9 / 149978.962 | 4.576659039e-06 | 7.142014914e-09 |
| 0.0017 | reduced | 0.000570839177 / 0.00060281295 / 0.000604691921 | 124.72836 / 149588.671 / 149978.756 | 4.576659039e-06 | 7.142034102e-09 |
| 0.0068 | full | 0.000570839177 / 0.000604713275 / 0.000608628965 | 124.72836 / 66096.4385 / 66603.3511 | 4.576659039e-06 | 6.908019588e-09 |
| 0.0068 | reduced | 0.000570839177 / 0.000604713282 / 0.00060862898 | 124.72836 / 66096.3442 / 66603.2629 | 4.576659039e-06 | 6.908038145e-09 |

The first formal run (run_001) already had **13 / 0 / 0** D7 test results but stopped
before repository regression because the audit reporter attempted indexed assignment
into an untyped empty struct. Its original log and all trajectories are preserved.
[Implementation revision 1](../audit/rs_qssa_d7_20260924/implementation_revision_1.json)
records typed metadata preallocation, analyzer cleanup, and stronger source-fingerprint
checks. No equation, microparameter, solver setting, or threshold changed. The passing
rerun is run_002. This reporting failure is not relabeled as a scientific failure or
removed from the record.

<!-- /D7_VALIDATION_RESULTS -->

## 9. Evidence boundary and failure mechanisms

The analytical derivation and implementation establish the declared surrogate, its state/stoichiometry mapping, exact enzyme bookkeeping, algebraic manifold, fast relaxation law, complete derivative formulas, and extended conservation identities. Successful synthetic backbone validation can support the declared numerical profile only.

The microscopic constants, PPi lumping assumption, generic ATP/NTP interface as chemistry, and adequacy of one intermediate for the heterogeneous 20-aaRS/46-tRNA PURE mixture **remain without experimental support**. The synthetic micro-parameters are not independently measured kinetics. A local reference flux match does not establish global matching to canonical Eq. (8) or actual PURE biology.

Expected failure mechanisms include insufficient timescale separation; a rapidly moving manifold; substrate depletion or boundary conditioning; substantial enzyme occupancy requiring different slow coordinates or total-QSSA; changing PPi; omitted aaRS states and heterogeneity; and failure of one parameter set to reproduce the canonical apparent rate away from the reference state. These must be reported if observed, not removed with state projection, clipping, fitting, or relaxed gates.

All preregistered gates and final precommit regression passed. The conclusion is: **D7 = COMPLETE for analytical derivation + synthetic main-backbone numerical validation. This does not establish experimental/microscopic validity of the one-intermediate aaRS surrogate.** The final precommit replay is retained separately in the audit.

D8 next step: preregister a bounded parameter/domain study of applicability and failure; no D8 sweep, grid, failure atlas, or curve collapse is performed in D7.
