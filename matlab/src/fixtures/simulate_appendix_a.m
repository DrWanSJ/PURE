function out = simulate_appendix_a(profile,varargin)
%SIMULATE_APPENDIX_A Integrate the Appendix-A test system.
%
% InitialState is optional and mainly used for the perturbation-decay test.
% It is never projected or clipped into the feasible region.

if nargin < 1 || isempty(profile)
    profile = 'baseline';
end
p = appendix_a_params(profile);

ip = inputParser;
ip.addParameter('InitialState',p.y0);
ip.addParameter('Tfinal',p.tau_final);
ip.addParameter('OutputDt',p.output_dt);
ip.parse(varargin{:});
opt = ip.Results;

y0 = opt.InitialState(:);
if numel(y0) ~= 2
    error('appendix_a:badInitialState','InitialState must be [u;e].');
end

tspan = (0:opt.OutputDt:opt.Tfinal)';
if tspan(end) ~= opt.Tfinal
    tspan(end+1,1) = opt.Tfinal; %#ok<AGROW>
end

odeopts = odeset('RelTol',p.RelTol,'AbsTol',p.AbsTol);
[tt,yy] = ode15s(@(t,y) rhs_appendix_a(t,y,p),tspan,y0,odeopts);

u = yy(:,1);
e = yy(:,2);
u_bound = max(y0(1),p.alpha);

qc = struct();
qc.all_finite = all(isfinite(yy(:)));
qc.min_u = min(u);
qc.min_e = min(e);
qc.max_e = max(e);
qc.max_u_minus_bound = max(u-u_bound);
qc.feasible = qc.min_u >= p.acceptance.feasible_floor && ...
    qc.min_e >= p.acceptance.feasible_floor && ...
    qc.max_e <= p.acceptance.feasible_ceiling && ...
    qc.max_u_minus_bound <= 1e-8;

out = struct();
out.t = tt;
out.y = yy;
out.u = u;
out.e = e;
out.psi = appendix_a_psi(u,e,p);
out.p = p;
out.qc = qc;
end
