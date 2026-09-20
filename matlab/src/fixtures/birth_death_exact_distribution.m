function dist = birth_death_exact_distribution(t, p, kmax)
%BIRTH_DEATH_EXACT_DISTRIBUTION Exact Poisson PMF at one time point.
%
% No Statistics Toolbox is required.  We use the Poisson recurrence
%
%   P(0)=exp(-mu)
%   P(k)=P(k-1)*mu/k
%
% and choose a default cutoff far into the upper tail.  The omitted
% probability is returned explicitly as tail_mass.

if ~(isscalar(t) && isfinite(t) && t >= 0)
    error('birth_death:badTime', 't must be a finite nonnegative scalar.');
end

ref = analytic_birth_death(t, p);
mu = ref.mean;

if nargin < 3 || isempty(kmax)
    kmax = ceil(mu + 12*sqrt(max(mu,1)) + 20);
end

k = (0:kmax)';
pmf = zeros(size(k));
pmf(1) = exp(-mu);
for j = 1:kmax
    pmf(j+1) = pmf(j) * mu / j;
end

mass = sum(pmf);

dist = struct();
dist.t = t;
dist.mu = mu;
dist.k = k;
dist.pmf = pmf;
dist.mass = mass;
dist.tail_mass = max(0, 1-mass);
dist.mean_truncated = sum(k .* pmf);
dist.variance_truncated = sum((k-mu).^2 .* pmf);
end
