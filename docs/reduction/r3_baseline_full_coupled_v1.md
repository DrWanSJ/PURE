# R3 baseline full-coupled result

Status: **registered baseline condition evaluated; selective QSSA candidate
fails the fixed coupled acceptance gates.** This is one of ten preregistered
conditions, not a terminal R3 pilot decision. The source is the canonical
PNAS2017 SBML with author parameters/initial state, and the reduced candidate
is the 21-complex dynamic-resource total-QSSA chart. Free GlyAMP and MetAMP
remain dynamic. No parameters, source rates, acceptance limits, or initial
grid values were fitted or changed.

The raw 0–1000 s/201-point run is
`results/reduction/r3_aminoacylation_qssa/run_001/R3_BASE/`. Both full and
reduced BDF solves succeeded at `rtol=1e-10`, `atol=1e-14`; the full/reduced
RHS counts were 8840/90262. All 968 directed gross extents were integrated
as ODE states against the dense trajectories and retained as separate
forward/reverse ledgers. The physical closure had 142212 calls, one HYBR
fallback, maximum residual `9.999945316e-11`, and maximum fast-block
condition number `2951.65`; no concentration was clipped.

| Fixed gate | Observed | Limit | Result |
| --- | ---: | ---: | --- |
| All 241 species E_inf | `1.02130060` | `0.01` | FAIL |
| All 42 protected Class-I E_inf | `0.99905497` | `0.01` | FAIL |
| Aminoacylation directed-rate E_inf | `1.02130060` | `0.05` | FAIL |
| Aminoacylation directed-extent E_inf | `0.07692427` | `0.01` | FAIL |
| Full source material-balance residual | `7.4303e-7` | `1e-8` | FAIL |
| Reduced slow-coordinate balance residual | `2.4436e-6` | `1e-8` | FAIL |
| Algebraic closure residual | `9.99995e-11` | `1e-10` | PASS |
| SOURCE_GENERAL inventory drift | `1.82e-12` | `1e-8` | PASS |

The full-window error includes the initial QSSA layer. The failures are not
only an initial-layer artifact: after 0.05 s, MettRNAfMetCAU E_inf remains
`0.04125`, GlytRNAGlyGCC `0.01205`, maximum directed-rate E_inf `0.45604`,
and maximum directed-extent E_inf `0.07104`. The minimum reconstructed
concentration is `-1.73e-12` uM, a reported numerical negative. The
independent full-trajectory timescale screen has 21 attracting local fast
modes at all samples but fails `epsilon<=0.01` at 94 of 201 samples; this
screen is not a substitute for the coupled error gates.

The 968-row rate/extent tables, 241-row species table, raw arrays, input and
output hashes, exact command/environment, and process exit code are retained
in the run directory. Other nine fixed conditions remain required to map the
pilot failure/validity domain and assign one of the task's terminal statuses.
