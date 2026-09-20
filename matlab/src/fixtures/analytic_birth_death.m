function ref = analytic_birth_death(t, p)
%ANALYTIC_BIRTH_DEATH Exact mean/variance for the registered X(0)=0 case.
%
% For immigration-death dynamics with X(0)=0, X(t) is exactly Poisson:
%
%   mu(t) = alpha_b/beta_b * (1-exp(-beta_b*t)).
%
% A Poisson variable has mean = variance = mu.  This routine is independent
% of the numerical RHS and therefore provides a real reference answer.

if p.X0 ~= 0
    error('birth_death:analyticRequiresZeroInitial', ...
        'The registered Poisson reference assumes X0 = 0.');
end

t = t(:);
mu = (p.alpha_b / p.beta_b) .* (1 - exp(-p.beta_b .* t));

ref = struct();
ref.t = t;
ref.mean = mu;
ref.variance = mu;
ref.stationary_mean = p.alpha_b / p.beta_b;
end
