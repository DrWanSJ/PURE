# B0 fixture: reversible_conversion

Status: implemented. Evidence type: `synthetic_fixture`.

This fixture is a deliberately simple reversible first-order conversion used to
verify deterministic solver behavior, conservation, positivity, and comparison
against an independent analytic solution. It is not a PURE-system biochemical
model and must not be used as experimental or literature evidence.

## Model

[
A \xrightleftharpoons[k_r]{k_f} B
]

with

[
\frac{dA}{dt}=-k_f A+k_r B, \qquad
\frac{dB}{dt}= k_f A-k_r B.
]

Units are seconds for time, micromolar (`uM`) for concentrations, and
`s^-1` for both rate constants.

The frozen synthetic baseline is:

- `k_f = 0.3 s^-1`
- `k_r = 0.1 s^-1`
- `A0 = 8.0 uM`
- `B0 = 2.0 uM`
- `t_final = 30 s`
- `ode15s`, `RelTol = 1e-10`, `AbsTol = 1e-12`

## Independent analytic reference

Let

[
M_0=A_0+B_0, \qquad \lambda=k_f+k_r.
]

Then

[
A(t)=A_{eq}+(A_0-A_{eq})e^{-\lambda t},
\qquad B(t)=M_0-A(t),
]

where

[
A_{eq}=\frac{k_r}{k_f+k_r}M_0=2.5\ \mathrm{uM},
\qquad
B_{eq}=\frac{k_f}{k_f+k_r}M_0=7.5\ \mathrm{uM}.
]

The exact conservation law is `A + B = 10 uM`, and at equilibrium
`k_f*A_eq = k_r*B_eq`.

## Run

From the repository root:

```matlab
addpath('scripts');
run_fixture_reversible_conversion
```

or run the automated test directly:

```matlab
runtests('matlab/tests/test_fixture_reversible_conversion.m')
```

The test compares the numerical trajectory against the analytic solution at
every output time; it does not generate the expected answer from the numerical
RHS.
