function out = simulate_pure_exact_reduced(DNA_uM, varargin)
%SIMULATE_PURE_EXACT_REDUCED Six-coordinate exact B1 conservation reduction.
% Options: Tfinal=14400 s, OutputDt=10 s, RelTol=1e-10, AbsTol=1e-12.
% Matches the full simulator's t/y/yfull/rates/mRNA/protein/p/opts/stats fields.
% Also returns z (n x 6), fixed invariants, coordinate names and raw QC minima.
% No nonnegativity projection, clipping, fitting or timescale approximation.
p = pure_literature_reference_params();
validateattributes(DNA_uM, {'numeric'}, {'real','scalar','finite','nonnegative'});
p.DNA = DNA_uM;
positiveScalar = @(x) isnumeric(x) && isreal(x) && isscalar(x) && isfinite(x) && x > 0;
ip = inputParser;
ip.addParameter('Tfinal', 14400, positiveScalar);
ip.addParameter('OutputDt', 10, positiveScalar);
ip.addParameter('RelTol', 1e-10, positiveScalar);
ip.addParameter('AbsTol', 1e-12, positiveScalar);
ip.parse(varargin{:});
opt = ip.Results;
tspan = (0:opt.OutputDt:opt.Tfinal)';
if tspan(end) ~= opt.Tfinal
    tspan(end+1,1) = opt.Tfinal;
end
indices = [1 3 4 6 8 10];
b = pure_exact_conservation_constants(p);
odeopts = odeset('RelTol', opt.RelTol, 'AbsTol', opt.AbsTol);
[tt, zz, stats] = ode15s(@(t,z) rhs_pure_exact_reduced(t,z,p,b), ...
    tspan, p.y0(indices), odeopts);
n = numel(tt);
X = zeros(n,12);
R = zeros(n,6);
for i = 1:n
    X(i,:) = reconstruct_pure_exact_reduced_state(zz(i,:)', p, b)';
    [~, R(i,:)] = rhs_pure_literature_reference(tt(i), X(i,1:10)', p);
end
out = struct();
out.t = tt;
out.z = zz;
out.yfull = X;
out.y = X(:,1:10);
out.rates = R;
out.mRNA = X(:,3)/(3*p.L);
out.protein = X(:,7)/p.L;
out.p = p;
out.opts = opt;
out.stats = stats;
out.invariants = b;
out.coordinate_names = p.state_names(indices);
out.full_state_names = [p.state_names, {'D_nt','D_TLcat'}];
out.qc.all_finite = all(isfinite([X R out.mRNA out.protein]), 'all');
out.qc.min_state_value = min(out.y, [], 'all');
out.qc.min_per_full_state = min(X, [], 1);
out.qc.negative_count_per_full_state = sum(X < 0, 1);
out.qc.nonnegative = out.qc.min_state_value >= 0;
end
