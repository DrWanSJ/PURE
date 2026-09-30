# R3 direct-extent runner diagnostic

Status: **exploratory 0–0.1 s check, not the registered R3 validation grid.**
The input grid, `1e-10` BDF relative tolerance, `1e-14` absolute tolerance,
and all scientific limits were unchanged. The registered 0–1000 s baseline
and two enzyme-low cases were started afterward in separate directories.

The raw diagnostic is `results/reduction/r3_grid_runner_diagnostic_v1/attempt_001/`.
Both full and selective-QSSA state solves completed, followed by 968
directed gross-extent ODEs against each dense state trajectory. It wrote
241-species, 968-rate and 968-extent error tables. A semantic test verifies
that a forward rate of 10 and reverse rate of 9 yield distinct gross
extents of 10 and 9, rather than an `abs(net)` substitute.

| Check | Observed | Fixed limit |
| --- | ---: | ---: |
| Fast algebraic residual | `9.9391e-11` | `1e-10` |
| All-species E_inf | `1.02124` | `0.01` |
| Class-I E_inf | `0.99905` | `0.01` |
| Aminoacylation directed-rate E_inf | `2.54930` | `0.05` |
| Aminoacylation directed-extent E_inf | `0.55236` | `0.01` |
| Full source material-balance residual | `1.86369e-7` | `1e-8` |
| Reduced slow-coordinate balance residual | `2.42347e-7` | `1e-8` |
| Source-general inventory drift | `9.09e-13` | `1e-8` |

The largest full and reduced direct-extent balance residuals occur in `CK`
at approximately `0.0870` and `0.0966` s. The directed CK extents include
large opposing forward/reverse contributions. The fixed balance limit
remains in force; this diagnostic does not establish whether the observed
residual comes from BDF state error, extent integration error, or both.
No concentration was clipped; the minimum reconstructed reduced value was
`-1.73e-12` uM. The result is a failed short-run diagnostic and does not
classify the full R3 pilot.
