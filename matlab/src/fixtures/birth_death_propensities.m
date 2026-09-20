function a = birth_death_propensities(X, p)
%BIRTH_DEATH_PROPENSITIES Exact event propensities for the B0 process.
%
%   birth: a1 = alpha_b
%   death: a2 = beta_b * X
%
% X is a molecule count, so for an SSA state it must be a nonnegative integer.
% We reject fractional/negative counts rather than silently coercing them.

if ~(isscalar(X) && isfinite(X) && X >= 0 && ...
        abs(X-round(X)) <= 10*eps(max(1,abs(X))))
    error('birth_death:badCount', ...
        'X must be a finite nonnegative integer molecule count.');
end

a = [p.alpha_b; p.beta_b * X];
end
