# PNAS2017_full_reference conditions
benchmark.json freezes source paths/hashes, author CSV inputs, executable time grid and ode15s settings.
The author sample comment says 1e-5; the executable logspace(-4,3,200) starts at 1e-4 seconds.
The active command is python -B scripts/reproduce_pnas2017_reference.py --verify.
An optional fresh author ODE run requires --execute-author --output-dir with a new external directory.
Figure comparison/plot generation is PAUSED_BY_USER. No acceptance tolerance is selected.
