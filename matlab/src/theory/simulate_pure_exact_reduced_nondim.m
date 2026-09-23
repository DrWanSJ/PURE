function out = simulate_pure_exact_reduced_nondim(DNA_uM, varargin)
%SIMULATE_PURE_EXACT_REDUCED_NONDIM Integrate q(tau), restore physical units.
% AbsTol is in physical reduced-state units (uM), converted per coordinate.
% RelTol is dimensionless. No NonNegative option, clipping or projection.
p = pure_literature_reference_params();
validateattributes(DNA_uM,{'numeric'},{'scalar','real','finite','nonnegative'});
p.DNA = DNA_uM;
positive = @(x) isnumeric(x) && isreal(x) && isscalar(x) && isfinite(x) && x>0;
ip = inputParser;
ip.addParameter('Tfinal',14400,positive);
ip.addParameter('OutputDt',10,positive);
ip.addParameter('RelTol',1e-10,positive);
ip.addParameter('AbsTol',1e-12,positive);
ip.parse(varargin{:}); opt = ip.Results;
m = pure_nondim_map(p); indices = [1 3 4 6 8 10]; sz = m.state_scales(indices);
I = pure_dimensionless_invariants(m.initial_dimensionless,m);
tgrid = (0:opt.OutputDt:opt.Tfinal)';
if tgrid(end) ~= opt.Tfinal
    tgrid(end+1,1) = opt.Tfinal;
end
taugrid = m.k_nt_deg*tgrid;
odeopts = odeset('RelTol',opt.RelTol,'AbsTol',opt.AbsTol./sz);
rhs = @(tau,q) rhs_pure_exact_reduced_nondim(tau,q,m,I);
q0 = m.initial_dimensionless(indices);
if numel(taugrid)==2
    sol = ode15s(rhs,taugrid,q0,odeopts);
    tau = taugrid; Q = deval(sol,tau)'; stats = sol.stats;
else
    [tau,Q,stats] = ode15s(rhs,taugrid,q0,odeopts);
end
Z = Q.*sz'; n = numel(tau);
Y = zeros(n,12); X = zeros(n,12); v = zeros(n,6);
b = pure_exact_conservation_constants(p);
for i = 1:n
    Y(i,:) = reconstruct_pure_exact_reduced_nondim_state(Q(i,:)',m,I)';
    % Dimensional reconstruction is postprocessing only, never the solver RHS.
    X(i,:) = reconstruct_pure_exact_reduced_state(Z(i,:)',p,b)';
    [~,v(i,:)] = rhs_pure_exact_reduced_nondim(tau(i),Q(i,:)',m,I);
end
out.tau = tau; out.t_s = tau/m.k_nt_deg; out.q = Q;
out.yfull_dimensionless = Y; out.z_dimensional = Z; out.yfull_dimensional = X;
out.dimensionless_rates = v; out.dimensional_rates = m.Vstar*v;
out.mRNA = X(:,3)/(3*p.L); out.protein = X(:,7)/p.L;
out.map = m; out.invariants = I; out.p = p; out.opts = opt; out.stats = stats;
out.solver_AbsTol_dimensionless = opt.AbsTol./sz;
out.qc.all_finite = all(isfinite([tau Q Y Z X v out.mRNA out.protein]),'all');
out.qc.min_per_full_state = min(X,[],1);
out.qc.negative_count_per_full_state = sum(X<0,1);
out.qc.min_state_value = min(X,[],'all');
out.qc.nonnegative = out.qc.min_state_value>=0;
end
