# R3 coupled validation execution protocol v1

Registered before the 0–1000 s ten-condition R3 execution. This operational
protocol implements `r3_aminoacylation_qssa_method.md` without changing its
grid, source, tolerances, scales, or acceptance thresholds. The earlier short
smokes are exploratory diagnostics, not R3 validation.

- For each of the ten fixed grid rows, construct its full 241-state initial
  condition only from the listed initial scales, then compute its own R1
  source-general inventory `b=L*x0`. Solve the complete source model and the
  193-slow/21-algebraic dynamic-resource QSSA candidate from 0 to 1000 s with
  SciPy BDF, `rtol=1e-10`, `atol=1e-14`, analytic Jacobians, and the same
  201 reporting times (`0` plus 200 logarithmic points from `1e-4` to `1e3`).
  Preserve invalid roots, solver failure, and all numerical negatives.
- At each output time reconstruct all 241 species; evaluate all 968 canonical
  directed source rates for both states. A source-reaction row is retained as
  its own rate and gross extent even when a reverse partner exists. Score
  every species and every directed rate with the preregistered E_inf formula
  and floors; identify the 103 reactions touching selected fast states and
  the aminoacylation subsystem separately from the remaining source network.
- Integrate each directed extent as an ODE state `d xi_j/dt = v_j(x(t))`
  against each dense BDF state trajectory, on each adjacent registered
  reporting interval. Use SciPy DOP853 with the same `rtol=1e-10`,
  `atol=1e-14` for this triangular nonstiff extent subsystem, zero local
  starts, and compensated accumulation of segment increments. This is
  direct ODE integration of 968 directed gross extents, not a sum over sparse
  reporting samples. Record the state-solver and extent-solver statistics
  separately. Evaluate material balance with stable directed summation.
- Retain full-window errors including the initial layer. Also report a
  post-0.05 s diagnostic window; it cannot replace the full-window gate.
  Score state <=0.01, process rate <=0.05, cumulative resource extent
  <=0.01, closure residual <=1e-10, and balance <=1e-8. Report every
  condition, including expected adverse failure. A failed physical closure
  is a recorded domain failure, never replaced with a clipped trajectory.
- Run each condition into a fresh directory with source/method/grid/runtime
  hashes, command, environment and package versions, solver options, exit
  status, raw result and array paths. The runner refuses to overwrite an
  existing condition directory.
