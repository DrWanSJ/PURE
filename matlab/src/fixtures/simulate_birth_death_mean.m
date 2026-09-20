function out = simulate_birth_death_mean(varargin)
%SIMULATE_BIRTH_DEATH_MEAN Integrate the deterministic mean equation.
%
% This checks only the deterministic solver path.  The exact stochastic
% distribution is provided separately for future generic SSA validation.

p = birth_death_params();

ip = inputParser;
ip.addParameter('Tfinal', p.t_final);
ip.addParameter('OutputDt', p.output_dt);
ip.addParameter('RelTol', p.RelTol);
ip.addParameter('AbsTol', p.AbsTol);
ip.parse(varargin{:});
opt = ip.Results;

tspan = (0:opt.OutputDt:opt.Tfinal)';
if isempty(tspan) || tspan(end) ~= opt.Tfinal
    tspan(end+1,1) = opt.Tfinal; %#ok<AGROW>
end

odeopts = odeset('RelTol', opt.RelTol, 'AbsTol', opt.AbsTol);
[tt, xx] = ode15s(@(t,x) rhs_birth_death_mean(t,x,p), ...
    tspan, p.y0, odeopts);

ref = analytic_birth_death(tt, p);
scaled_error = abs(xx(:,1)-ref.mean) ./ (1+abs(ref.mean));

qc = struct();
qc.all_finite = all(isfinite(xx(:)));
qc.min_mean_value = min(xx(:));
qc.nonnegative = qc.min_mean_value >= p.acceptance.positivity_floor;
qc.max_scaled_mean_error = max(scaled_error);
qc.analytic_mean_pass = qc.max_scaled_mean_error <= ...
    p.acceptance.mean_trajectory_scaled_error_max;

out = struct();
out.fixture_id = p.fixture_id;
out.t = tt;
out.mean_numeric = xx(:,1);
out.mean_exact = ref.mean;
out.variance_exact = ref.variance;
out.p = p;
out.qc = qc;
end
