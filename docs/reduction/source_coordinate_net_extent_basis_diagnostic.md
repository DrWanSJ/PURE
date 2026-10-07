# R1 v4 reverse-pair extent basis diagnostic

This is an exact linear change of coordinates for the 968 model-side
integrated extent ODEs. It is a diagnostic, not a decisive R1 acceptance run.
For each of the 290 source-certified reverse pairs `(f,r)`, integrate
`n'=v_f-v_r` and `q'=v_r`, both initially zero, and reconstruct the two
directed gross extents as `xi_f=n+q` and `xi_r=q`. Integrate every unpaired
directed gross extent as `xi_j'=v_j`. The transform is invertible and uses
the two original source rates and reaction IDs; it does not replace a gross
ledger with `abs(net)` or rate quadrature. Its lower Jacobian block applies
the same linear rate transform to the source rate Jacobian.

Use the v4 source-general 241-to-214 chart, complete 0-1000 s author
condition and 201 report points. Integrate the 241-state full and
214-coordinate reduced systems separately with SciPy BDF, `stable_direct`
source RHS, `rtol=5e-13`, and `atol=5e-15`. These settings match the prior
stable-RHS diagnostic and are declared before this run. No model parameter,
kinetic law, rate, or threshold changes.

Evaluate the unchanged per-component `E_inf <= 1e-6` gates on all 241
species, all 968 sampled directed rates, and all 968 reconstructed directed
gross extents. The acceptance-style material-balance calculation continues
to use those 968 physical gross extents and requires full and reduced
absolute residual `<=1e-8`; report the exact net-basis form `S_f*n` as an
additional diagnostic only. Report every negative and use the existing
`-1e-11` domain floor.

If every unchanged gate passes, write a separate preregistered method before
any decisive run and obtain the tight independent RoadRunner checks. If it
fails, retain both gross and net-basis balance values to diagnose extent
conditioning without promoting the net-basis residual alone.

## Accuracy follow-up registered after diagnostic 001

Diagnostic 001 passed gross-ledger balance and all other gates except the
largest directed extent `E_inf=1.02818012237549e-6`. To test convergence
without changing the metric or model, run one follow-up at half the solver
tolerances, `rtol=2.5e-13` and `atol=2.5e-15`, with the same complete window,
v4 chart, reverse-pair extent basis, and `stable_direct` RHS. Preserve the
first failure. A pass here remains diagnostic until a distinct decisive
method is registered and run.
