function tests = test_fixture_appendix_a()
%TEST_FIXTURE_APPENDIX_A Analytic B0 checks for tasklist Appendix A.
%
% This includes negative structure tests: trace must stay negative, so this
% fixture must not report a Hopf crossing under the allowed parameters.

thisdir = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(thisdir));
addpath(fullfile(root,'matlab','src','fixtures'));
tests = functiontests(localfunctions);
end

function test_parameter_identity(tc)
p = appendix_a_params('baseline');
tc.verifyEqual(p.alpha,2.0);
tc.verifyEqual(p.rho,1.0);
tc.verifyEqual(p.eta,0.6);
tc.verifyEqual(p.delta,0.2);
tc.verifyEqual(p.K_e,0.5);
tc.verifyEqual(p.parameter_origin,'synthetic_test');
end

function test_boundary_vector_field_points_inward(tc)
p = appendix_a_params('baseline');

% u=0 boundary: du=alpha*e >= 0.
for e = linspace(0,1,11)
    dy = rhs_appendix_a(0,[0;e],p);
    tc.verifyGreaterThanOrEqual(dy(1),-1e-14);
end

% e=0 boundary: de=rho > 0.
for u = linspace(0,p.alpha,11)
    dy = rhs_appendix_a(0,[u;0],p);
    tc.verifyEqual(dy(2),p.rho,'AbsTol',1e-14);
end

% e=1 boundary: de <= 0.
for u = linspace(0,p.alpha,11)
    dy = rhs_appendix_a(0,[u;1],p);
    tc.verifyLessThanOrEqual(dy(2),1e-14);
end
end

function test_numerical_trajectory_stays_feasible(tc)
out = simulate_appendix_a('baseline');
tc.verifyTrue(out.qc.all_finite);
tc.verifyTrue(out.qc.feasible, ...
    sprintf('min u %.3e, min e %.3e, max e %.3e', ...
    out.qc.min_u,out.qc.min_e,out.qc.max_e));
end

function test_unique_bracketed_fixed_point(tc)
p = appendix_a_params('baseline');
fp = appendix_a_fixed_point(p);

tc.verifyGreaterThan(fp.e,0);
tc.verifyLessThan(fp.e,1);
tc.verifyEqual(fp.u,p.alpha*fp.e,'AbsTol',1e-14);
tc.verifyLessThanOrEqual(abs(fp.H_residual), ...
    p.acceptance.fixed_point_residual_max);

% Numerical grid check of the analytic monotonicity H'(e)<0.
egrid = linspace(0,1,1001);
H = appendix_a_H(egrid,p);
tc.verifyGreaterThan(H(1),0);
tc.verifyLessThan(H(end),0);
tc.verifyLessThan(max(diff(H)),0);
end

function test_analytic_jacobian_matches_finite_difference(tc)
p = appendix_a_params('baseline');
y = [0.7;0.4];
J = appendix_a_jacobian(y(1),y(2),p);

% Central finite difference is independent of the analytic Jacobian formula.
h = 1e-6;
Jfd = zeros(2);
for j = 1:2
    step = zeros(2,1);
    step(j) = h;
    fp = rhs_appendix_a(0,y+step,p);
    fm = rhs_appendix_a(0,y-step,p);
    Jfd(:,j) = (fp-fm)/(2*h);
end

tc.verifyLessThanOrEqual(max(abs(J(:)-Jfd(:))), ...
    p.acceptance.jacobian_fd_max_abs_error);
end

function test_fixed_point_is_locally_stable(tc)
p = appendix_a_params('baseline');
fp = appendix_a_fixed_point(p);
J = appendix_a_jacobian(fp.u,fp.e,p);
lambda = eig(J);

tc.verifyLessThan(trace(J),0);
tc.verifyGreaterThan(det(J),0);
tc.verifyLessThan(max(real(lambda)),0);
end

function test_no_hopf_sign_structure_in_feasible_region(tc)
p = appendix_a_params('baseline');
rng(20260920);

% Sampling is a code guard, not the mathematical proof.  The proof is the
% analytic sign structure in Appendix A.
for j = 1:200
    u = p.alpha*rand;
    e = rand;
    J = appendix_a_jacobian(u,e,p);
    tc.verifyLessThan(trace(J),0);
    tc.verifyGreaterThan(det(J),0);
end
end

function test_small_perturbation_decays(tc)
p = appendix_a_params('baseline');
fp = appendix_a_fixed_point(p);

y0 = fp.y+[0.02;-0.01];
out = simulate_appendix_a('baseline','InitialState',y0);

initial_distance = norm(y0-fp.y);
final_distance = norm(out.y(end,:)'-fp.y);
tc.verifyLessThan(final_distance,initial_distance/10);
end

function test_low_load_approximation_in_its_limit(tc)
p = appendix_a_params('low_load');
fp = appendix_a_fixed_point(p);
ap = appendix_a_approximations(p);

% These are the actual assumptions behind Eq. (A.13).
tc.verifyLessThan(p.alpha*fp.e,0.1);
tc.verifyLessThan(fp.e/p.K_e,0.1);

relerr = abs(ap.e_low_load-fp.e)/fp.e;
tc.verifyLessThanOrEqual(relerr,p.acceptance.low_load_relative_error_max);
end

function test_saturated_approximation_in_its_limit(tc)
p = appendix_a_params('saturated');
fp = appendix_a_fixed_point(p);
ap = appendix_a_approximations(p);

tc.verifyTrue(ap.saturated_requires_rho_gt_eta);
tc.verifyGreaterThan(p.alpha*fp.e,10);
tc.verifyGreaterThan(fp.e/p.K_e,10);

relerr = abs(ap.e_saturated-fp.e)/fp.e;
tc.verifyLessThanOrEqual(relerr,p.acceptance.saturated_relative_error_max);
end
