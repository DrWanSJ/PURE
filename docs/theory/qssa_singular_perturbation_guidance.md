# QSSA and singular perturbation: guidance for PURE R5

This note organizes verified primary literature, checked online on 2026-10-07. References describe mathematics; they do not certify a PURE reduction. The distinction between a structural calculation, a small-parameter limit, eta=1 numerical accuracy and scientific promotion is mandatory.

## Classical QSSA / Tikhonov singular perturbation

A parameterized family must expose a fast equilibrium problem and a smooth reduced flow. Local rank, separation of tangent and fast directions, and strictly stable transverse eigenvalues are central conditions; domain persistence and admissible initial data still matter. A small algebraic residual alone does not check those assumptions. [Feliu, Kruff and Walcher, 2020, §§2.1–2.2](https://link.springer.com/article/10.1007/s00332-020-09610-3) gives the coordinate-independent conditions and reduction formula.

PURE-specific: R5 declares a CK reaction-rate scaling family, derives its invariant coordinates, and verifies its two fast eigenvalues. Bounded-domain persistence of the complete eta family and a rigorous uniform error bound are not established.

## Rapid equilibrium / partial equilibrium

The fast process is equilibration of selected reversible reactions. Slow reactions force changes in their fast invariants; the reduced vector field follows the equilibrium surface while retaining this forcing. This differs from setting an intermediate derivative to zero over a catalytic cycle with nonzero throughput. [Gorban, 2018](https://arxiv.org/abs/1802.05745) organizes quasi-equilibrium, QSS, invariant manifolds and reaction-graph approaches.

PURE-specific: only two CP-binding CK pairs are scaled; catalytic CK conversion, CK degradation and all MK/NDK reactions remain slow and explicit. Kd is preserved. No enzyme-cycle QSSA is claimed.

## Total QSSA

Totals can be the suitable slow variables when free substrate concentrations move appreciably during binding. Applicable small parameters and timescales depend on the mechanism; total-coordinate choice alone does not prove accuracy. [Eilertsen and Schnell, 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7337988/) compares standard, reverse and total QSSA through timescales, singular parameters and error analysis.

PURE-specific: CK T0,T1,B are totals under the selected binding process, but they are dynamic in the full network. The CK study is partial equilibrium in totals, not an application of an irreversible Michaelis–Menten tQSSA theorem.

## Noninteracting species / linear elimination

Linear dependence on eliminated species can make algebraic elimination tractable. Graphical and parameter conditions are needed to connect such algebraic elimination to Tikhonov–Fenichel reduction. The correspondence need not hold automatically. [Feliu, Lax, Walcher and Wiuf](https://arxiv.org/abs/1908.11270) explicitly studies when QSS and singular perturbation reductions agree for noninteracting species.

PURE-specific: shared resources and feedback mean linearity must be checked in the actual invariant coordinates. R4 GlyRS closure is not promoted to a singular perturbation theorem through root residuals.

## Reaction-network graphical elimination

Graph-based elimination can identify effective reactions and rate functions and examine conservation and positivity properties of the resulting network. [Sáez, Wiuf and Feliu, 2016](https://arxiv.org/abs/1509.03153) develops graphical linear elimination and its reduced reaction interpretation.

PURE-specific: the R5 CK graph has two independent binding directions. Its exact canonical stoichiometry and full-network forcing are retained. No new effective MK/NDK/CK rate law or reaction deletion is authorized.

## Coordinate-independent GSPT

The reduction can be expressed through a projection along fast directions onto the tangent critical manifold; a globally fastest same-dimensional Schur subspace is not a prerequisite of the local fast-process theorem. [Feliu, Kruff and Walcher, 2020](https://link.springer.com/article/10.1007/s00332-020-09610-3) provides a parameterized-manifold formula without requiring an a priori slow/fast variable split.

PURE-specific: Lf Sf=0 gives natural slow coordinates. Combining that map with R1's exact source class yields 212 CK slow coordinates and two binding coordinates. Schur/CSP results remain supporting diagnostics.

## Initial layer / matched asymptotics

An outer solution can miss fast initial data off the critical manifold. Initial relaxation, validity of the basin and approximation away from the initial layer require separate treatment. Timescale and initial-transient issues are discussed in [Eilertsen and Schnell, 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7337988/).

PURE-specific: author CK_CP starts at zero while the outer critical root is occupied. R5 records the jump and uses a prospectively fixed ten-relaxation startup rule. This hybrid construction is numerical; no fitted switch or matched-series accuracy theorem is claimed.

## Output / flux reconstruction after elimination

A reduced state map does not automatically reconstruct microscopic directed gross fluxes. The reduced reaction interpretation in [Sáez, Wiuf and Feliu, 2016](https://arxiv.org/abs/1509.03153) is distinct from reconstructing every original microscopic ledger.

PURE-specific derivation: leading CK equilibrium rates have equal forward/reverse gross values. Finite slow redistribution satisfies n=Dh F−(S_s v_s)_q; at first order J_fast h1=n. Exact source gross extents still require source trajectories. The full reconstructed state ledger needs this redistribution, while exact source conservation tests use LS=0 independently. This project-specific equation is a derivation, not a quoted external theorem.

Unresolved PURE assumptions: authoritative absolute unit metadata; full-domain compactness and positivity for the numerical eta trajectories; uniform asymptotic error estimates; eta=1 adequacy for broader formal validation; and complete separation of historical state/dense-output/extent errors. References resolve none of these through citation alone.
