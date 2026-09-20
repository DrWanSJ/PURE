function tests = test_fixture_reversible_conversion()
%TEST_FIXTURE_REVERSIBLE_CONVERSION B0 verification against analytic truth.

thisdir = fileparts(mfilename('fullpath'));   % .../matlab/tests
root = fileparts(fileparts(thisdir));         % project root
addpath(fullfile(root, 'matlab', 'src', 'fixtures'));
tests = functiontests(localfunctions);
end

% =========================================================================
function test_rhs_correctness(tc)
p = reversible_conversion_params();
y = [4; 6];

expected = [ ...
    -0.3*4 + 0.1*6; ...
     0.3*4 - 0.1*6];

actual = rhs_reversible_conversion(0, y, p);
tc.verifyEqual(actual, expected, 'AbsTol', 1e-15);
end

% =========================================================================
function test_derivative_conservation_identity(tc)
p = reversible_conversion_params();
rng(20260920);
maxviol = 0;
for i = 1:50
    y = 10 * rand(2,1);
    dy = rhs_reversible_conversion(0, y, p);
    maxviol = max(maxviol, abs(sum(dy)));
end
tc.verifyLessThanOrEqual(maxviol, 1e-12, ...
    sprintf('max derivative conservation violation = %.3e', maxviol));
end

% =========================================================================
function test_numerical_trajectory_matches_analytic(tc)
out = simulate_reversible_conversion();
tc.verifyLessThanOrEqual(out.qc.analytic_max_scaled_error, 1e-8, ...
    sprintf('max scaled analytic trajectory error = %.3e', ...
    out.qc.analytic_max_scaled_error));
end

% =========================================================================
function test_numerical_conservation(tc)
out = simulate_reversible_conversion();
tc.verifyEqual(out.analytic.M0, 10, 'AbsTol', 1e-15);
tc.verifyLessThanOrEqual(out.qc.conservation_max_scaled_residual, 1e-10, ...
    sprintf('max scaled conservation residual = %.3e', ...
    out.qc.conservation_max_scaled_residual));
end

% =========================================================================
function test_positivity_without_clipping(tc)
out = simulate_reversible_conversion();
tc.verifyGreaterThanOrEqual(out.qc.min_state_value_uM, -1e-12, ...
    sprintf('minimum state = %.3e uM', out.qc.min_state_value_uM));

src = fileread(which('rhs_reversible_conversion'));
tc.verifyFalse(contains(src, 'max('), ...
    'RHS must not clip states with max(...)');
tc.verifyFalse(contains(src, 'min('), ...
    'RHS must not clip states with min(...)');
end

% =========================================================================
function test_equilibrium(tc)
p = reversible_conversion_params();
ref = analytic_reversible_conversion(0, p);

tc.verifyEqual(ref.A_eq, 2.5, 'AbsTol', 1e-15);
tc.verifyEqual(ref.B_eq, 7.5, 'AbsTol', 1e-15);
tc.verifyEqual(ref.forward_eq, ref.reverse_eq, 'AbsTol', 1e-15);

out = simulate_reversible_conversion();
tc.verifyLessThan(abs(out.A(end) - ref.A_eq), 5e-5, ...
    '30 s endpoint should be close to, but not forced equal to, equilibrium');
tc.verifyLessThan(abs(out.B(end) - ref.B_eq), 5e-5, ...
    '30 s endpoint should be close to, but not forced equal to, equilibrium');
end

% =========================================================================
function test_repeatability(tc)
o1 = simulate_reversible_conversion();
o2 = simulate_reversible_conversion();

tc.verifyTrue(isequal(o1.t, o2.t), ...
    'repeated runs must use the same output grid');
tc.verifyTrue(isequal(o1.y, o2.y), ...
    'same MATLAB release and inputs should give identical deterministic states');
end

% =========================================================================
function test_frozen_parameter_values(tc)
p = reversible_conversion_params();

tc.verifyEqual(p.k_f, 0.3);
tc.verifyEqual(p.k_r, 0.1);
tc.verifyEqual(p.A0, 8.0);
tc.verifyEqual(p.B0, 2.0);
tc.verifyEqual(p.t_final, 30.0);
tc.verifyEqual(p.RelTol, 1e-10);
tc.verifyEqual(p.AbsTol, 1e-12);
tc.verifyEqual(p.fixture_id, 'reversible_conversion');
tc.verifyEqual(p.evidence_type, 'synthetic_fixture');
end
