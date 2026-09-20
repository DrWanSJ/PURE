function out = simulate_enzyme_qssa_full(profile)
%SIMULATE_ENZYME_QSSA_FULL Integrate the full three-state enzyme model.
%
% Exact bookkeeping:
%   s+c+p = constant
% and physical enzyme capacity requires 0<=c<=e_T.

if nargin < 1 || isempty(profile)
    profile = 'valid';
end
p = enzyme_qssa_params(profile);

tspan = (0:p.output_dt:p.t_final)';
if tspan(end) ~= p.t_final
    tspan(end+1,1) = p.t_final; %#ok<AGROW>
end

odeopts = odeset('RelTol',p.RelTol,'AbsTol',p.AbsTol);
[tt,yy] = ode15s(@(t,y) rhs_enzyme_qssa_full(t,y,p), ...
    tspan,p.y0,odeopts);

s = yy(:,1);
c = yy(:,2);
prod = yy(:,3);

target = p.s0+p.c0+p.p0;
total = s+c+prod;

qc = struct();
qc.all_finite = all(isfinite(yy(:)));
qc.min_state_uM = min(yy(:));
qc.max_complex_minus_eT_uM = max(c-p.e_T);
qc.positivity_pass = qc.min_state_uM >= p.acceptance.positivity_floor_uM;
qc.enzyme_capacity_pass = qc.max_complex_minus_eT_uM <= 1e-9;
qc.conservation_max_scaled_residual = max(abs(total-target))/(1+abs(target));
qc.conservation_pass = qc.conservation_max_scaled_residual <= ...
    p.acceptance.full_conservation_scaled_residual_max;

out = struct();
out.t = tt;
out.y = yy;
out.s = s;
out.c = c;
out.p_product = prod;
out.s_total_unreacted = s+c;
out.free_enzyme = p.e_T-c;
out.catalytic_flux = p.k2.*c;
out.p = p;
out.qc = qc;
end
