function out = simulate_pure_literature_dimensionless(DNA_uM, varargin)
%SIMULATE_PURE_LITERATURE_DIMENSIONLESS Integrate compact equations in tau.
% Outputs tau, physical t [s], ydimless (n x 12), yfull [uM] (n x 12),
% y (10 physical columns), canonical dimensional rates [uM/s] (n x 6),
% compact_rates (all six /Vstar), rates_backtransformed, mRNA, protein,
% map (scales/groups/metadata), p, opts, stats and unmodified output-grid QC.
p = pure_literature_reference_params();
validateattributes(DNA_uM, {'numeric'}, {'real','scalar','finite','nonnegative'});
p.DNA = DNA_uM;
positiveScalar = @(x) isnumeric(x) && isreal(x) && isscalar(x) && isfinite(x) && x>0;
ip = inputParser;
ip.addParameter('Tfinal',14400,positiveScalar);
ip.addParameter('OutputDt',10,positiveScalar);
ip.addParameter('RelTol',1e-10,positiveScalar);
ip.addParameter('AbsTol',1e-12,positiveScalar);
ip.parse(varargin{:}); opt = ip.Results;
m = pure_nondim_map(p);
tgrid = (0:opt.OutputDt:opt.Tfinal)';
if tgrid(end) ~= opt.Tfinal
    tgrid(end+1,1) = opt.Tfinal;
end
taugrid = m.k_nt_deg*tgrid;
odeopts = odeset('RelTol',opt.RelTol,'AbsTol',opt.AbsTol, ...
    'Jacobian',@(tau,y) jacobian_pure_literature_dimensionless(tau,y,m.groups));
rhs = @(tau,y) rhs_pure_literature_dimensionless(tau,y,m.groups);
% Two endpoint tspan values make ode15s return its internal mesh. Use deval
% in that special case to preserve the requested physical output grid.
if numel(taugrid) == 2
    sol = ode15s(rhs,taugrid,m.initial_dimensionless,odeopts);
    tau = taugrid; Y = deval(sol,tau)'; stats = sol.stats;
else
    [tau,Y,stats] = ode15s(rhs,taugrid,m.initial_dimensionless,odeopts);
end
X = Y.*m.state_scales';
t = tau/m.k_nt_deg;
n = numel(t); R = zeros(n,6); v = zeros(n,6);
for i = 1:n
    % Reference rate evaluation is postprocessing only; never the solver RHS.
    [~,R(i,:)] = rhs_pure_literature_reference(t(i),X(i,1:10)',p);
    [~,v(i,:)] = rhs_pure_literature_dimensionless(tau(i),Y(i,:)',m.groups);
end
out.tau = tau; out.t = t; out.physical_output_grid = tgrid;
out.ydimless = Y; out.yfull = X; out.y = X(:,1:10);
out.rates = R; out.compact_rates = v; out.rates_backtransformed = m.Vstar*v;
out.mRNA = X(:,3)/(3*p.L); out.protein = X(:,7)/p.L;
out.p = p; out.opts = opt; out.stats = stats; out.map = m;
out.full_state_names = m.state_order;
out.qc.all_finite = all(isfinite([tau t Y X R v out.mRNA out.protein]),'all');
out.qc.min_per_full_state = min(X,[],1);
out.qc.negative_count_per_full_state = sum(X<0,1);
out.qc.min_state_value = min(X,[],'all');
out.qc.nonnegative = out.qc.min_state_value>=0;
end
