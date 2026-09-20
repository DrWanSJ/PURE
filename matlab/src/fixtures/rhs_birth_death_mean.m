function dxdt = rhs_birth_death_mean(~, x, p)
%RHS_BIRTH_DEATH_MEAN Deterministic ODE for the exact process mean.
%
% This is NOT an SSA trajectory. For this linear birth-death process, the
% expectation m(t)=E[X(t)] obeys the closed equation
%
%   dm/dt = alpha_b - beta_b*m.
%
% Keeping this separate from the stochastic propensity function helps prevent
% a common mistake: treating a deterministic rate equation as if it were an
% event propensity.

dxdt = p.alpha_b - p.beta_b * x(1);
end
