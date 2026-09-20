function tests = test_fixture_birth_death()
%TEST_FIXTURE_BIRTH_DEATH Known-answer B0 checks for birth-death dynamics.
%
% These tests establish the exact mean, exact Poisson distribution and
% propensity convention.  They do NOT claim that generic SSA is implemented.

thisdir = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(thisdir));
addpath(fullfile(root, 'matlab', 'src', 'fixtures'));
tests = functiontests(localfunctions);
end

function test_frozen_parameters(tc)
p = birth_death_params();
tc.verifyEqual(p.alpha_b, 4.0);
tc.verifyEqual(p.beta_b, 0.5);
tc.verifyEqual(p.X0, 0);
tc.verifyEqual(p.t_final, 10.0);
tc.verifyEqual(p.evidence_type, 'synthetic_fixture');
end

function test_mean_rhs_spot_value(tc)
% At x=6: dx/dt = 4 - 0.5*6 = 1 molecule/s.
p = birth_death_params();
tc.verifyEqual(rhs_birth_death_mean(0,6,p), 1.0, 'AbsTol', 1e-15);
end

function test_propensity_convention(tc)
p = birth_death_params();

% At X=10: birth=4 events/s, death=5 events/s.
tc.verifyEqual(birth_death_propensities(10,p), [4;5], 'AbsTol', 1e-15);

% At X=0 the death channel must switch off exactly.
a0 = birth_death_propensities(0,p);
tc.verifyGreaterThan(a0(1), 0);
tc.verifyEqual(a0(2), 0);
end

function test_numerical_mean_matches_exact_mean(tc)
out = simulate_birth_death_mean();
tc.verifyTrue(out.qc.all_finite);
tc.verifyTrue(out.qc.nonnegative);
tc.verifyLessThanOrEqual(out.qc.max_scaled_mean_error, 1e-8, ...
    sprintf('max scaled mean error = %.3e', out.qc.max_scaled_mean_error));
end

function test_exact_poisson_distribution(tc)
p = birth_death_params();
dist = birth_death_exact_distribution(p.t_final,p);

tc.verifyLessThanOrEqual(dist.tail_mass, 1e-12);
tc.verifyGreaterThanOrEqual(min(dist.pmf), 0);

% The defining Poisson check: mean = variance = mu.
tc.verifyLessThanOrEqual(abs(dist.mean_truncated-dist.mu), 1e-10);
tc.verifyLessThanOrEqual(abs(dist.variance_truncated-dist.mu), 1e-10);
end

function test_mean_is_monotone_and_bounded(tc)
out = simulate_birth_death_mean();
stationary = out.p.alpha_b/out.p.beta_b;

% Starting at zero, the mean rises monotonically toward alpha_b/beta_b.
tc.verifyGreaterThanOrEqual(min(diff(out.mean_numeric)), -1e-11);
tc.verifyLessThanOrEqual(max(out.mean_numeric), stationary+1e-10);
end

function test_repeatability(tc)
o1 = simulate_birth_death_mean();
o2 = simulate_birth_death_mean();
tc.verifyTrue(isequal(o1.t,o2.t));
tc.verifyTrue(isequal(o1.mean_numeric,o2.mean_numeric));
end
