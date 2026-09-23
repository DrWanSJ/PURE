# D7 reduction certificate — RS fast-module draft

**Status:** analytical draft only; D7 is **not yet complete**.  
**Scope:** one real main-backbone module, aminoacylation (RS), expanded from the Mavelli coarse-grained rate law into a minimal explicit fast-intermediate model and then reduced by QSSA. No microscopic parameters have yet been fitted or sourced, and no full-vs-reduced numerical validation has yet been run.

## 1. Baseline and purpose

The frozen literature-reference backbone follows Mavelli et al. for the coarse-grained RS reaction

\[
A+T+NTP \xrightarrow{RScat} AT+NXP.
\]

Mavelli §2.2 states that the underlying PURE aminoacylation chemistry uses aminoacyl-tRNA synthetases, consumes ATP, and produces AMP and PPi, while the simplified model pools the energy species into generic NTP/NXP and uses apparent Michaelis-Menten factors. The present D7 construction is therefore a **model extension for reduction analysis**, not a claim that Mavelli's apparent rate law was derived from the microscopic mechanism below.

The goal is to introduce one explicit fast intermediate, derive its QSSA reduction and time scale, and later test where that reduction is accurate or fails when embedded in the actual PURE backbone.

## 2. Minimal explicit RS mechanistic surrogate

Let

\[
E \equiv RScat,\qquad
M \equiv RScat\cdot A\!-\!AMP,
\]

and let \(E_T\) denote the total synthetase pool represented in this two-state enzyme submodel.

The minimal surrogate is

\[
E+A+ATP
\underset{k_{-1}}{\overset{k_1}{\rightleftarrows}}
M,
\]

\[
M+T \xrightarrow{k_2} E+AT+AMP.
\]

This is a deliberately lumped mechanism, not a complete elementary aaRS kinetic scheme. In particular:

- the forward activation step is represented by the effective mass-action term \(k_1[E][A][ATP]\);
- PPi is not included as a dynamic state;
- \(k_{-1}\) is an **apparent pseudo-first-order reverse rate constant**. If a more explicit reverse reaction were written as \(M+PP_i\to E+A+ATP\), then the present \(k_{-1}\) corresponds to absorbing the assumed/frozen PPi factor into the effective reverse parameter;
- AMP is the chemically explicit product of this surrogate; when coupled back to the Mavelli backbone it must map to the generic exhausted-nucleotide pool NXP;
- the symbol \(T\) below is retained as the tRNA substrate variable of the derivation. The exact interface to Mavelli's average-tRNA multiplicity convention, including the \(n_T/n_A=2.3\) factor, must be fixed before numerical integration.

Within this two-state enzyme representation,

\[
E_T=E+M
\]

is exact, so

\[
E=E_T-M.
\]

## 3. Full intermediate equation

With mass-action kinetics for the declared surrogate,

\[
\dot M
=
k_1[A](E_T-M)[ATP]
-k_{-1}M
-k_2M[T].
\]

Define the effective first-order rates

\[
\alpha=k_1[A][ATP],\qquad
\beta=k_{-1},\qquad
\gamma=k_2[T].
\]

Then

\[
\boxed{
\dot M=\alpha E_T-(\alpha+\beta+\gamma)M.
}
\]

The comparison relevant to fast/slow analysis is therefore between the effective rates \(\alpha,\beta,\gamma\), not directly between \(k_1,k_{-1},k_2\), whose units differ.

## 4. QSSA reduction

The QSSA condition is

\[
\dot M\approx0,
\]

not \(M\approx0\). Solving the algebraic condition gives

\[
\boxed{
M_{\mathrm{QSS}}
=
h(A,ATP,T)
=
\frac{k_1E_T[A][ATP]}
{k_{-1}+k_2[T]+k_1[A][ATP]}.
}
\]

The corresponding RS product flux is

\[
V_{RS}^{\mathrm{QSS}}
=
k_2M_{\mathrm{QSS}}[T],
\]

hence

\[
\boxed{
V_{RS}^{\mathrm{QSS}}
=
\frac{k_1k_2E_T[A][T][ATP]}
{k_{-1}+k_2[T]+k_1[A][ATP]}.
}
\]

This reduced law is **not algebraically identical** to the Mavelli product of three apparent Michaelis-Menten saturation factors. It is the QSSA reduction of the explicitly declared surrogate above. Comparing these two reduced descriptions is a later model-analysis question, not an identity assumed here.

## 5. Fast relaxation time

For frozen \(A,ATP,T\), define

\[
D=k_{-1}+k_2[T]+k_1[A][ATP]
=\alpha+\beta+\gamma.
\]

The instantaneous QSS point is

\[
M^*=\frac{\alpha E_T}{D}.
\]

Write

\[
M=M^*+\delta M.
\]

With \(A,ATP,T\) frozen over the fast relaxation calculation,

\[
\frac{d\delta M}{dt}
=
-D\,\delta M,
\]

so

\[
\delta M(t)=\delta M(0)e^{-Dt}.
\]

Therefore the characteristic fast relaxation time is

\[
\boxed{
\tau_M
=
\frac{1}{D}
=
\frac{1}
{k_1[A][ATP]+k_{-1}+k_2[T]}.
}
\]

The fast subsystem is locally attracting whenever \(D>0\), which holds for positive rate constants and nonnegative substrate concentrations.

## 6. What the slow time means

The QSS target is not generally fixed during the PURE trajectory because

\[
M^*(t)=h(A(t),ATP(t),T(t)).
\]

Even when \(M(t)\) has caught the current \(M^*(t)\), the backbone reactions continue to change \(A\), ATP/NTP and \(T\). The target therefore moves.

The physical comparison is:

\[
\boxed{
\tau_M
=
\text{time for }M\text{ to relax toward the current QSS target}
}
\]

versus

\[
\boxed{
\tau_{\mathrm{slow}}
=
\text{time over which the variables determining that target change appreciably}.
}
\]

A simple conservative diagnostic along the coupled trajectory is

\[
\tau_A\sim\frac{A_{\mathrm{scale}}}{|\dot A|},\qquad
\tau_{ATP}\sim\frac{ATP_{\mathrm{scale}}}{|\dot{ATP}|},\qquad
\tau_T\sim\frac{T_{\mathrm{scale}}}{|\dot T|},
\]

with declared nonzero reference scales near depletion, and

\[
\tau_{\mathrm{slow}}
=
\min(\tau_A,\tau_{ATP},\tau_T,\ldots).
\]

A more directly QSS-oriented tracking diagnostic follows the motion of the slow manifold itself:

\[
\frac{dM^*}{dt}
=
\frac{\partial h}{\partial A}\dot A
+
\frac{\partial h}{\partial ATP}\dot{ATP}
+
\frac{\partial h}{\partial T}\dot T,
\]

and defines a slow-manifold motion time using a declared \(M\) reference scale,

\[
\tau_{\mathrm{slow}}^{(M^*)}
\sim
\frac{M_{\mathrm{scale}}}{|dM^*/dt|}.
\]

This scale-based form is preferred to \(|M^*|/|dM^*/dt|\) near \(M^*=0\), where the latter becomes numerically ill-conditioned.

The dimensionless separation parameter is then

\[
\boxed{
\epsilon(t)
=
\frac{\tau_M(t)}
{\tau_{\mathrm{slow}}(t)}.
}
\]

QSSA requires \(\epsilon\ll1\) over the declared state/time domain. No universal numerical cutoff such as 0.1 or 0.01 is assumed here; D8 must preregister a sweep and measure full-vs-reduced errors across both an applicability region and an explicit failure region.

## 7. QSSA versus rapid equilibrium

The adopted reduction is QSSA. It does **not** require the activation binding/unbinding step to be much faster than the catalytic transfer step.

A stronger rapid-equilibrium interpretation would additionally require the first reversible step to equilibrate much faster than the downstream drain, schematically

\[
k_1[A][ATP]+k_{-1}
\gg
k_2[T],
\]

together with the corresponding equilibrium assumptions. That stronger condition is not imposed in this draft.

## 8. Derivatives required for the chain-rule Jacobian

Let

\[
D=k_{-1}+k_2T+k_1A\,ATP,
\qquad
h(A,ATP,T)=\frac{E_Tk_1A\,ATP}{D}.
\]

The analytic derivatives are

\[
\boxed{
\frac{\partial h}{\partial A}
=
\frac{E_Tk_1ATP\,(k_{-1}+k_2T)}{D^2}
}
\]

\[
\boxed{
\frac{\partial h}{\partial ATP}
=
\frac{E_Tk_1A\,(k_{-1}+k_2T)}{D^2}
}
\]

\[
\boxed{
\frac{\partial h}{\partial T}
=
-\frac{E_Tk_1A\,ATP\,k_2}{D^2}.
}
\]

When the RS module is embedded into the main-chain slow equations

\[
\dot{\mathbf s}=F(\mathbf s,M),
\qquad
0=G(\mathbf s,M),
\]

the reduced Jacobian must be assembled with the full chain rule,

\[
\boxed{
J_{\mathrm{slow}}
=
F_{\mathbf s}
-
F_M\,G_M^{-1}G_{\mathbf s},
}
\]

equivalently \(F_{\mathbf s}+F_M\,dh/d\mathbf s\). It is not valid to obtain the reduced Jacobian by mechanically deleting the \(M\) row and column from the full Jacobian.

The derivatives above are complete for the present algebraic manifold \(M=h(A,ATP,T)\), but the actual main-chain \(J_{\mathrm{slow}}\) is **not yet assembled** in this draft because the explicit full RS extension has not yet been wired into the validated PURE RHS.

## 9. Initial layer and expected failure modes

If the initialized \(M_0\) is not on the QSS manifold,

\[
M_0\ne h(A_0,ATP_0,T_0),
\]

the full model contains an initial fast layer with characteristic duration of a few \(\tau_M\). A reduced simulation must state how its initial condition is projected onto the QSS manifold.

Expected failure modes to test rather than suppress include:

- \(\epsilon\) no longer small because the backbone variables change on a comparable time scale;
- substrate depletion or boundary regions where scale-based diagnostics become delicate;
- enzyme occupancy becoming large enough that alternative slow coordinates or total-QSSA treatment is preferable;
- the pseudo-first-order PPi assumption becoming invalid;
- mismatch between the present one-intermediate surrogate and the Mavelli multiplicity convention or the actual aaRS mechanism;
- inability of one parameter set to reproduce the original Mavelli apparent RS rate over the intended state domain.

## 10. Evidence status and next D7/D8 work

**Derived in this draft:** the declared two-step surrogate, enzyme conservation, full \(M\) equation, QSSA manifold, reduced RS flux, fast relaxation time, slow-manifold interpretation, analytic \(dh/d(A,ATP,T)\), and the required chain-rule Jacobian form.

**Not yet numerically supported:** any value of \(\epsilon\), any error bound, any universal fast/slow ratio, or equivalence to the Mavelli RS rate law.

**Not experimentally supported:** the microscopic parameters \(k_1,k_{-1},k_2\) and the adequacy of the one-intermediate surrogate for the heterogeneous 20-aaRS/46-tRNA PURE mixture.

Before D7 can be marked complete, the next implementation step is to define the exact interface to the frozen PURE backbone, choose/source or explicitly label the microscopic parameters, assemble the full chain-rule Jacobian, and produce a reproducible full-vs-QSSA test harness. D8 then preregisters the parameter/domain sweep and reports trajectory, flux, cumulative-cost and failure-region errors.
