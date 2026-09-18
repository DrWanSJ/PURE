# B1 Fig. 4 benchmark configuration

Benchmark B1 reproduces Fig. 4 of Mavelli 2015 (calculated curves):

| condition | DNA template | time span | solver | tolerances |
| --- | --- | --- | --- | --- |
| DNA_0p34nM | 0.34 nM | 0–4 h, output every 10 s | ode15s | RelTol 1e-9, AbsTol 1e-12 |
| DNA_1p7nM | 1.7 nM | same | same | same |
| DNA_6p8nM | 6.8 nM | same | same | same |

Status: these conditions are currently **hardcoded** in
`matlab/src/simulate/run_fig4_benchmark.m` (conditions struct + default
options of `simulate_pure_literature_reference`). Extracting them into a
machine-readable file here is a registered TODO — it must not be done casually,
because touching the run path risks numerical regressions (the solver input
grid must remain bit-identical).
