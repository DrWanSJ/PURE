# R3 adverse condition: reduced BDF numerical noncompletion

Status: **registered adverse condition incomplete; no full-window reduced
trajectory or coupled error score.** The completed nine-condition grid already
fails the unchanged state, process-rate, extent, and balance gates. This
diagnostic explains the tenth condition's missing scores and does not promote
the QSSA or change a threshold.

The preregistered `R3_ADVERSE` scales both GlyRS and MetRS by 20 and ATP and
both charging tRNAs by 0.02. The complete 0–1000 s, 201-point **full source**
state solve was saved to `restart_001/R3_ADVERSE/full_state.npz`; it was byte
identical to the preserved first attempt. The full-source timescale screen
has zero nonattracting fast-mode samples and 108/201 epsilon-screen failures.
It is a screen, not QSSA validation. The reduced 193-slow/21-algebraic BDF
solve at `rtol=1e-10`, `atol=1e-14` did not finish.

`scripts/probe_r3_running_bdf_v1.py` sampled the live Python process without
modifying it. Its hash-bound raw record is
`restart_001/R3_ADVERSE/stall_diagnostic.json`. Five samples over 8.54 wall
seconds showed BDF model time moving from `362.23623800556123` to
`362.2374228687863` s, with steps near `2e-6` to `5e-5` s and first-order
steps at the endpoints. The last sample recorded `16506.875` process CPU
seconds. The process was then externally stopped after `16521.78125` CPU
seconds. Its OS exit code could not be captured; the sealed result and
manifest explicitly use `null`, rather than mislabeling this as a runner
exit-1 exception. The partial source trajectory and screen remain intact.

At nearby saved **full-source** states, the same physical total-coordinate
closure succeeded: at 348.910 s its residual was `9.24e-14`, fast Jacobian
condition number `310.99`, and all reconstructed resources were nonnegative;
at 378.346 s those values were `6.39e-14` and `311.24`. This does not prove
that the unrecorded reduced state had the same closure. An earlier interactive
probe reported `6.97e-13` uM q and `1.86e-9` uM/s slow-RHS spreads across
feasible roots near this state, but its exact seeds/state were not retained.
The hash-bound four-seed test below at the saved 348.910121 s source state
instead measured `2.64e-16` uM and `1.65e-14` uM/s. Thus root-seed jitter is
not established as the cause of the registered BDF slowdown; the earlier
larger observation is preserved as unreplicated diagnostic evidence.

Exploratory local integrations starting at the 348.910 s full-source state
used the same source-derived closure. These are **not** alternate registered
condition results and do not replace the 0–1000 s grid:

| Local diagnostic | RHS-call budget/result | Interpretation |
| --- | --- | --- |
| v2 BDF, fixed `rtol=1e-10`, `atol=1e-14` | 10,001 calls; last t `348.915186` s | Numerical progress too slow |
| v2 BDF, `atol=1e-12` | 10,001 calls; last t `348.920482` s | Still slow; not the registered tolerance |
| v2 BDF, `atol=1e-10` | reached 378.346 s in 107 RHS calls | Sensitivity diagnostic only; cannot be used for acceptance |
| v3 extra-Newton-polish BDF, fixed tolerances | 10,001 calls; last t `348.915251` s | Extra root polish did not repair progress |
| diagonally scaled BDF, equivalent physical `atol=1e-14` | 10,001 calls; last t `348.913863` s | Coordinate scaling did not repair progress |
| Radau, fixed tolerances | 10,001 calls; last t `348.912538` s | Alternate stiff solver diagnostic also stalled |

A separate bounded local diagnostic is reproducible with
`scripts/diagnose_r3_adverse_local_solver_v1.py` and retained under
`results/reduction/r3_aminoacylation_qssa/local_solver_diagnostic_001/`.
It initializes from the saved **full-source**, not the registered reduced,
state at `348.9101213406774` s, and targets only `349.0101213406774` s.
All six trials use `rtol=1e-10`, `atol=1e-14`, with a 5,000 RHS-call budget;
the raw JSON records Python/NumPy/SciPy versions and input/script hashes.

| Local strategy | Result | Interpretation |
| --- | --- | --- |
| v2 BDF with implicit Jacobian | budget at `348.912413`, 5,001 RHS calls | Reproduces slow progress |
| Fixed initial physical-root seed BDF | budget at `348.912394`, 5,001 RHS calls | Seed determinism alone did not help |
| Algebraically on-manifold RHS BDF | budget at `348.912319`, 5,001 RHS calls | Omitting residual-proportional terms did not help |
| SciPy finite-difference Jacobian BDF | budget at `348.910324`, 5,001 RHS calls | Removing analytic Jacobian did not help |
| `math.fsum` fast residual BDF | budget at `348.912526`, 5,001 RHS calls | Stable residual sum did not help |
| LSODA with implicit Jacobian | reached `349.010121`, 3,387 RHS calls | Only this short local window completed; no full-grid claim |

The four physical v2 and v3 roots from source-state, 0.9x, 1.1x, and zero
seeds had maximum q spread `2.63678e-16` uM, slow-RHS spread
`1.64868e-14` uM/s, and residuals `7.11e-15` to `1.44e-12`. The local
LSODA result does not establish that the registered reduced trajectory can
reach 1000 s, nor that a solver change would satisfy the pre-registered BDF
method. No local diagnostic is substituted for the adverse grid row.

## Checkpointed reduced-state probe

`scripts/probe_r3_adverse_bdf_state_v1.py` starts again from the registered
adverse initial state with SciPy BDF, the unchanged physical closure,
`rtol=1e-10`, and `atol=1e-14`. It saves accepted reduced states through a
separate runtime so snapshot inspection does not alter the warm root used by
the integrator. The bounded `adverse_bdf_stepper_001` attempt ran for 122.06
wall seconds and stopped at its specified wall-time budget, with no exception.
This is a diagnostic stepper, not a scored grid run.

It reached model time `359.05633056357715` s in 3,664 BDF steps / 14,437
RHS evaluations. At that checkpoint it had fallen to order 1 and an
absolute step of `1.11954e-6` s. After 4,492 steps / 19,846 RHS evaluations,
it had advanced only to `359.0589556421065` s; the last step was
`1.78624e-6` s. The separately probed physical root at that accepted
reduced state was valid, with residual `1.20792e-13`, minimum selected fast
concentration `1.99602e-10` uM, and minimum reconstructed ATP/AMP/PPi
resource `0.0354073` uM. The `state_0006.npz` snapshot retains the actual
193-coordinate reduced state, 21 fast concentrations, and 241 reconstructed
species for subsequent numerical diagnosis. The `adverse_bdf_stepper_smoke_001`
15-second run separately verified the checkpoint and budget path, ending at
model time `0.00393764` s. Both outputs retain command, package versions,
source/script hashes, per-snapshot hashes, and explicit diagnostic status.

The new snapshot demonstrates severe progress loss **on the actual reduced
trajectory** near 359 s while local closure remains physical. It does not
identify a unique solver cause or complete the missing 0–1000 s comparison.

The hash-bound `adverse_snapshot_diagnostic_001` experiment starts at that
accepted reduced snapshot, and is explicitly not a registered grid result.
It uses the unchanged `rtol=1e-10`, `atol=1e-14`, a 0.1 s local target, and
5,000 RHS-call budgets. Its `result.json` and `manifest.json` bind the snapshot,
grid, canonical SBML, v2 runtime, diagnostic code, and package versions.

| Local trial from reduced t=359.058955642 s | Last model time at 5,001 RHS calls | Wall time |
| --- | ---: | ---: |
| v2 BDF | 359.061306209 s | 25.50 s |
| v2 LSODA | 359.118990403 s | 31.22 s |
| 50-digit Decimal reconstruction/rate accumulation with BDF | 359.061226005 s | 47.55 s |

All three exhausted the call budget before the local target. Decimal differs
from the float v2 RHS by at most `3.80052e-12` uM/s and from its directed
rates by at most `3.63798e-12` uM/s at this snapshot, but did not improve BDF
progress. It is a diagnostic implementation, not a replacement kinetic law.
The reduced Jacobian's eigenvalue real parts span about `-101424.22` to
`8.92e-7` 1/s. Along the normalized local RHS direction, the analytic versus
centered-difference Jacobian-vector error grows from `2.84e-7` at a `1e-2`
coordinate perturbation to `6.06e-4` at `1e-5`; all sampled roots remain
physical. Large gross directed contributions cancel in several species rows:
gross-absolute/net-absolute ratios are about `163207` for CP, `28789` for
ATP, and `6.67e6` for GlyRS. These observations show local numerical
sensitivity but do not isolate a cause or justify changing tolerances.

`scripts/r3_resource_total_runtime_v3.py` preserves the failed extra-polish
experiment. It is not used by the registered condition results or pilot
manifest; v1/v2 source and all nine completed condition hashes remain
unchanged. No acceptance limit, kinetic parameter, initial scale, or source
rate was relaxed. The absence of an adverse reduced trajectory is an explicit
limit on the domain map, while the nine evaluated failures suffice to reject
this selective QSSA pilot in every condition where a full comparison exists.
