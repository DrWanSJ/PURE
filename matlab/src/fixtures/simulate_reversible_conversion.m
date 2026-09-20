function out = simulate_reversible_conversion(varargin)
%SIMULATE_REVERSIBLE_CONVERSION Run the B0 reversible-conversion fixture.
%
%   OUT = SIMULATE_REVERSIBLE_CONVERSION(...)
%
%   Name-value options:
%     'Tfinal'   final time [s]
%     'OutputDt' output spacing [s]
%     'RelTol'   ode15s relative tolerance
%     'AbsTol'   ode15s absolute tolerance
%
%   Defaults come from the frozen fixture parameters.json. No state clipping
%   is used.

p = reversible_conversion_params();

ip = inputParser;
ip.addParameter('Tfinal',   p.t_final);
ip.addParameter('OutputDt', p.output_dt);
ip.addParameter('RelTol',   p.RelTol);
ip.addParameter('AbsTol',   p.AbsTol);
ip.parse(varargin{:});
opt = ip.Results;

validateattributes(opt.Tfinal, {'numeric'}, ...
    {'scalar', 'real', 'finite', 'nonnegative'});
validateattributes(opt.OutputDt, {'numeric'}, ...
    {'scalar', 'real', 'finite', 'positive'});
validateattributes(opt.RelTol, {'numeric'}, ...
    {'scalar', 'real', 'finite', 'positive'});
validateattributes(opt.AbsTol, {'numeric'}, ...
    {'scalar', 'real', 'finite', 'positive'});

tspan = (0:opt.OutputDt:opt.Tfinal)';
if isempty(tspan) || tspan(end) ~= opt.Tfinal
    tspan(end+1,1) = opt.Tfinal; %#ok<AGROW>
end

odeopts = odeset('RelTol', opt.RelTol, 'AbsTol', opt.AbsTol);
rhs = @(t, y) rhs_reversible_conversion(t, y, p);
[tt, yy] = ode15s(rhs, tspan, p.y0, odeopts);

ref = analytic_reversible_conversion(tt, p);
exact = [ref.A, ref.B];
total = yy(:,1) + yy(:,2);

scale_uM = 1.0;
scaled_error = abs(yy - exact) ./ (scale_uM + abs(exact));
conservation_scaled_residual = abs(total - ref.M0) ./ ...
    (scale_uM + abs(ref.M0));

qc = struct();
qc.all_finite = all(isfinite(yy(:)));
qc.min_state_value_uM = min(yy(:));
qc.nonnegative = qc.min_state_value_uM >= p.acceptance.positivity_floor_uM;
qc.analytic_max_scaled_error = max(scaled_error(:));
qc.analytic_pass = qc.analytic_max_scaled_error <= ...
    p.acceptance.trajectory_scaled_error_max;
qc.conservation_max_scaled_residual = max(conservation_scaled_residual);
qc.conservation_pass = qc.conservation_max_scaled_residual <= ...
    p.acceptance.conservation_scaled_residual_max;
qc.execution_status = 'completed';
if qc.all_finite && qc.nonnegative && qc.analytic_pass && qc.conservation_pass
    qc.scientific_status = 'passed_fixture_qc';
else
    qc.scientific_status = 'failed_fixture_qc';
end

out = struct();
out.fixture_id = p.fixture_id;
out.evidence_type = p.evidence_type;
out.t = tt;
out.y = yy;
out.state_names = p.state_names;
out.A = yy(:,1);
out.B = yy(:,2);
out.total = total;
out.analytic_A = ref.A;
out.analytic_B = ref.B;
out.analytic = ref;
out.scaled_error = scaled_error;
out.p = p;
out.opts = opt;
out.solver = 'ode15s';
out.qc = qc;
end
