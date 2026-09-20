function out = simulate_enzyme_qssa_reduced(profile, method)
%SIMULATE_ENZYME_QSSA_REDUCED Integrate standard or total QSSA.
%
% STANDARD state z=[s,p]:
%   s is FREE substrate.
%
% TOTAL state z=[s_T,p]:
%   s_T=s+c is TOTAL unreacted substrate.
%
% This distinction is the central point of the fixture. When enzyme binding
% occupies a large fraction of substrate, free s and total s_T are not the
% same slow variable.

if nargin < 1 || isempty(profile)
    profile = 'valid';
end
if nargin < 2 || isempty(method)
    method = 'standard';
end
method = validatestring(method, {'standard','total'});
p = enzyme_qssa_params(profile);

tspan = (0:p.output_dt:p.t_final)';
if tspan(end) ~= p.t_final
    tspan(end+1,1) = p.t_final; %#ok<AGROW>
end

switch method
    case 'standard'
        z0 = [p.s0;p.p0];
    case 'total'
        z0 = [p.s0+p.c0;p.p0];
end

odeopts = odeset('RelTol',p.RelTol,'AbsTol',p.AbsTol);
[tt,zz] = ode15s(@rhs_reduced,tspan,z0,odeopts);

slow = zz(:,1);
prod = zz(:,2);
c_alg = enzyme_qssa_algebraic_complex(slow,p,method);

switch method
    case 'standard'
        s_free = slow;
        s_total = s_free+c_alg;
    case 'total'
        s_total = slow;
        s_free = s_total-c_alg;
end

out = struct();
out.t = tt;
out.method = method;
out.slow_variable = slow;
out.s_free = s_free;
out.c = c_alg;
out.s_total_unreacted = s_total;
out.p_product = prod;
out.catalytic_flux = p.k2.*c_alg;
out.p = p;

    function dz = rhs_reduced(~,z)
        c_here = enzyme_qssa_algebraic_complex(z(1),p,method);
        v = p.k2*c_here;
        dz = [-v;v];
    end
end
