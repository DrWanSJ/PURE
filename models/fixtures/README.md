# fixtures (B0 verification models)

Small, fully specified known-answer models for mathematical/software verification:

- reversible_conversion — implemented; deterministic solver, conservation,
  positivity and analytic-trajectory verification.
- birth_death — implemented as deterministic-mean + exact Poisson/propensity
  reference; generic SSA hookup remains scheduled for D16.
- enzyme_qssa — implemented; full model, standard QSSA, total QSSA, exact
  conservation, a valid regime and an explicit standard-QSSA failure regime.
- appendix_a — implemented; feasible-domain, bracketed fixed-point, analytic
  Jacobian, eigenvalue-sign and asymptotic-approximation reference system.

These fixtures are NOT scientific claims about the PURE system. Every fixture is
marked synthetic_fixture; Appendix-A parameters are additionally marked synthetic_test.

Model definitions and frozen synthetic parameters live under models/fixtures/.
MATLAB implementations live under matlab/src/fixtures/ and tests under matlab/tests/.

Do not confuse these B0 models with matlab/tests/fixtures/, which stores frozen
regression snapshots for unrelated regression tests.
