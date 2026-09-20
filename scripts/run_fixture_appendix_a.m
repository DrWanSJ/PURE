function summary = run_fixture_appendix_a()
%RUN_FIXTURE_APPENDIX_A Print fixed-point and approximation diagnostics.

d0 = fileparts(mfilename('fullpath'));
root = fileparts(d0);
addpath(fullfile(root,'matlab','src','fixtures'));

p0 = appendix_a_params('baseline');
fp0 = appendix_a_fixed_point(p0);
lambda0 = eig(appendix_a_jacobian(fp0.u,fp0.e,p0));

pl = appendix_a_params('low_load');
fpl = appendix_a_fixed_point(pl);
al = appendix_a_approximations(pl);

ps = appendix_a_params('saturated');
fps = appendix_a_fixed_point(ps);
as = appendix_a_approximations(ps);

fprintf('B0 appendix_a fixture\n');
fprintf('  baseline fixed point u*=%.9g, e*=%.9g, |H|=%.3e\n', ...
    fp0.u,fp0.e,abs(fp0.H_residual));
fprintf('  max real eigenvalue: %.3e\n',max(real(lambda0)));
fprintf('  low-load A.13 relative error: %.3e\n', ...
    abs(al.e_low_load-fpl.e)/fpl.e);
fprintf('  saturated A.14 relative error: %.3e\n', ...
    abs(as.e_saturated-fps.e)/fps.e);

summary = struct('baseline_fixed_point',fp0, ...
    'baseline_eigenvalues',lambda0, ...
    'low_load_fixed_point',fpl, ...
    'saturated_fixed_point',fps);
end
