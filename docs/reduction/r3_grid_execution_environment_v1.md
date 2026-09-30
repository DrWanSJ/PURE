# R3 coupled-grid execution environment

The ten rows of `r3_validation_grid_v1.csv` use one canonical source model,
one coupled runner, the same 0–1000 s window, 201 reporting points, BDF state
solves and segmented DOP853 directed-extent ODEs at `rtol=1e-10` and
`atol=1e-14`. Each condition result records the Python, NumPy and SciPy
versions, command, source/protocol hashes, solver outcomes and raw output
hashes. Thread settings below affect only numerical library scheduling; no
model rate, initial scale, state partition, scoring rule or limit was changed.

| Launch setting | Conditions |
| --- | --- |
| No explicit `OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS` or `MKL_NUM_THREADS` override | `R3_BASE`, `R3_GLYRS_LOW`, `R3_GLYRS_HIGH`, `R3_METRS_LOW`, `R3_METRS_HIGH`, `R3_GLY_LOW`, `R3_MET_LOW` |
| `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1` set before starting Python | `R3_TRNA_LOW`, `R3_ATP_LOW`, `R3_ADVERSE` |

The first seven runs were launched before the three explicit thread-limited
runs. During their concurrent reduced solves, each Python process showed 39
threads and the host became slow to schedule other commands. The three
remaining conditions were therefore launched with one library thread each.
The inherited process environment inspected separately showed those three
variables unset. Every condition keeps its original raw output and gate
verdict; solver differences across thread settings are evaluated against the
same registered limits. A screen or condition failure is retained as a
failure, not tuned away by the launch setting.

## Interrupted attempts and restart

The six original `run_001` processes for `R3_METRS_HIGH`, `R3_GLY_LOW`,
`R3_MET_LOW`, `R3_TRNA_LOW`, `R3_ATP_LOW`, and `R3_ADVERSE` ended with no
`result.json` or condition manifest after saving their complete full-source
trajectories. Their trajectory and timescale files are retained as partial
attempt evidence. They are not scored as completed QSSA comparisons.

The coupled runner refuses to overwrite an existing directory. The same
registered condition IDs, source, solver protocol, tolerances, and fixed
limits are therefore executed again in fresh `restart_001` directories.
These six restarts set `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and
`MKL_NUM_THREADS=1` before Python starts. The final pilot manifest identifies
the selected attempt directory for every condition and checks that attempt's
input and output hashes. This restart does not change a scientific gate or
reinterpret a failed screen.

All six restarted full-source `full_state.npz` files were byte identical to
their preserved first-attempt files (SHA-256 checked condition by condition).
The original full-trajectory timescale CSV and JSON were copied into each
restart directory after that hash check. Their recorded command still points
to the first attempt; the state hash proves that the same sampled trajectory
was screened. No screen was recomputed or reclassified.
