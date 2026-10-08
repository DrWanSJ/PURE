# MATLAB reference route — PNAS2017_full_reference
Primary author ODE entrypoint: scripts/reproduce_pnas2017_reference.m with frozen fMGG_synthesis.m and author CSVs.
The Python entrypoint verifies inputs before optional execution and requires a new external output directory.
No plots are generated. Figure comparison is paused.
Preserved SimBiology/RoadRunner diagnostics are documented in docs/pnas2017/reference_reproduction.md.
Existing src/simulate/run_fig4_benchmark.m,generated/coarse code,digitization tools and B1 tests are LEGACY Mavelli implementation.
Use docs/legacy/mavelli2015/README.md for historical commands. They are excluded from current default preflight and CI.
