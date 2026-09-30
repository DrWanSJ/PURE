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
that the unrecorded reduced state had the same closure. At the 348.910 s
full-source state, different feasible warm starts that all satisfied the
unchanged `1e-10` closure gate differed in q by up to `6.97e-13` uM and in
the slow RHS by up to `1.86e-9` uM/s. This is a plausible source of the
registered BDF's sensitivity, not a proven unique cause.

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

`scripts/r3_resource_total_runtime_v3.py` preserves the failed extra-polish
experiment. It is not used by the registered condition results or pilot
manifest; v1/v2 source and all nine completed condition hashes remain
unchanged. No acceptance limit, kinetic parameter, initial scale, or source
rate was relaxed. The absence of an adverse reduced trajectory is an explicit
limit on the domain map, while the nine evaluated failures suffice to reject
this selective QSSA pilot in every condition where a full comparison exists.
