function tests = test_fixture_enzyme_qssa()
%TEST_FIXTURE_ENZYME_QSSA Full/reduced known-answer reduction checks.
%
% The fixture contains both a success regime and an intentional failure
% regime. A reduction is not validated by showing only a case where it works.

thisdir = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(thisdir));
addpath(fullfile(root,'matlab','src','fixtures'));
tests = functiontests(localfunctions);
end

function test_parameter_profiles_and_KM(tc)
pv = enzyme_qssa_params('valid');
pf = enzyme_qssa_params('failure');

tc.verifyEqual(pv.K_M,(10+1)/10,'AbsTol',1e-15);
tc.verifyEqual(pf.K_M,(1+1)/10,'AbsTol',1e-15);
tc.verifyEqual(pv.e_T/pv.s0,0.01,'AbsTol',1e-15);
tc.verifyEqual(pf.e_T/pf.s0,0.5,'AbsTol',1e-15);
end

function test_full_rhs_conservation_identity(tc)
p = enzyme_qssa_params('valid');
rng(20260920);
maxviol = 0;

for j = 1:100
    % Feasible random state: s,p>=0 and 0<=c<=e_T.
    y = [10*rand;p.e_T*rand;10*rand];
    dy = rhs_enzyme_qssa_full(0,y,p);
    maxviol = max(maxviol,abs(sum(dy)));
end

% Exact identity: ds+dc+dp=0.
tc.verifyLessThanOrEqual(maxviol,1e-12);
end

function test_full_trajectory_conservation_and_positivity(tc)
for profile = {'valid','failure'}
    out = simulate_enzyme_qssa_full(profile{1});
    tc.verifyTrue(out.qc.all_finite);
    tc.verifyTrue(out.qc.positivity_pass);
    tc.verifyTrue(out.qc.enzyme_capacity_pass);
    tc.verifyTrue(out.qc.conservation_pass, ...
        sprintf('%s residual %.3e',profile{1}, ...
        out.qc.conservation_max_scaled_residual));
end
end

function test_total_qssa_rationalized_root(tc)
p = enzyme_qssa_params('failure');
sT = 6.0;

c_rat = enzyme_qssa_algebraic_complex(sT,p,'total');

% Independent direct quadratic formula for this well-conditioned spot point.
A = p.e_T+sT+p.K_M;
c_direct = (A-sqrt(A^2-4*p.e_T*sT))/2;

tc.verifyEqual(c_rat,c_direct,'AbsTol',1e-12);
tc.verifyGreaterThanOrEqual(c_rat,0);
tc.verifyLessThanOrEqual(c_rat,min(p.e_T,sT));
end

function test_valid_regime_reductions_are_accurate(tc)
cmp = compare_enzyme_qssa('valid');
a = cmp.full.p.acceptance;

tc.verifyLessThanOrEqual(cmp.standard_product_scaled_error, ...
    a.valid_standard_product_scaled_error_max);
tc.verifyLessThanOrEqual(cmp.total_product_scaled_error, ...
    a.valid_total_product_scaled_error_max);
end

function test_failure_regime_exposes_standard_qssa_breakdown(tc)
cmp = compare_enzyme_qssa('failure');
a = cmp.full.p.acceptance;

% Negative test: standard QSSA is REQUIRED to be visibly inaccurate here.
tc.verifyGreaterThanOrEqual(cmp.standard_product_scaled_error, ...
    a.failure_standard_product_scaled_error_min, ...
    sprintf('standard-QSSA error only %.3e', ...
    cmp.standard_product_scaled_error));

% Total QSSA should remain much better because it keeps bound substrate in
% s_T=s+c instead of pretending all unreacted substrate is free.
tc.verifyLessThanOrEqual(cmp.total_product_scaled_error, ...
    a.failure_total_product_scaled_error_max);
end

function test_reduced_product_is_monotone(tc)
for profile = {'valid','failure'}
    for method = {'standard','total'}
        out = simulate_enzyme_qssa_reduced(profile{1},method{1});
        tc.verifyGreaterThanOrEqual(min(diff(out.p_product)),-1e-10);
        tc.verifyGreaterThanOrEqual(min(out.c),-1e-10);
    end
end
end

function test_repeatability(tc)
c1 = compare_enzyme_qssa('valid');
c2 = compare_enzyme_qssa('valid');

tc.verifyTrue(isequal(c1.full.y,c2.full.y));
tc.verifyTrue(isequal(c1.standard.p_product,c2.standard.p_product));
tc.verifyTrue(isequal(c1.total.p_product,c2.total.p_product));
end
