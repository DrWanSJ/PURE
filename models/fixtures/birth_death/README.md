# B0 fixture: birth_death

Status: reference fixture implemented. Evidence type: synthetic_fixture.

This is the standard one-species birth-death process:

    empty --alpha_b--> X
    X     --beta_b--> empty

The point is that the exact answer is known in advance. For the frozen baseline,
alpha_b = 4 molecule/s, beta_b = 0.5 s^-1 and X(0)=0.

The deterministic mean obeys:

    d<E[X]>/dt = alpha_b - beta_b<E[X]>

The exact stochastic distribution is Poisson with:

    mu(t) = alpha_b/beta_b * (1 - exp(-beta_b*t))

so mean = variance = mu(t).

Important boundary: generic SSA is still scheduled for D16. This fixture supplies the
exact distribution and propensity convention that future generic SSA code must match.
It does not use a private one-off SSA implementation to pretend that generic SSA has
already been validated.
