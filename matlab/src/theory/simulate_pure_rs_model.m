function out = simulate_pure_rs_model(mode, DNA_uM, varargin)
%SIMULATE_PURE_RS_MODEL Shared ode15s plumbing, without state repair.
% Accounting sinks are integrated synchronously, with no feedback.
p = pure_literature_reference_params();
validateattributes(DNA_uM, {'numeric'}, {'real','scalar','finite','nonnegative'});
p.DNA = DNA_uM;
q = rs_reduction_parameters(p);
positive = @(x) isnumeric(x) && isreal(x) && isscalar(x) && isfinite(x) && x>0;
ip = inputParser;
ip.addParameter('Tfinal',14400,positive);
ip.addParameter('OutputDt',10,positive);
ip.addParameter('RelTol',1e-10,positive);
ip.addParameter('AbsTol',1e-12,positive);
ip.parse(varargin{:}); opt = ip.Results;
switch mode
    case 'explicit'
        nphys = 11;
        initial = [p.y0;rs_qssa_manifold(p.y0,p,q);0;0];
        physicalRhs = @(t,y) rhs_pure_rs_explicit(t,y,p,q);
        physicalJac = @(t,y) jacobian_pure_rs_explicit(t,y,p,q);
        names = [p.state_names,{'M'}];
    case 'qssa'
        nphys = 10;
        initial = [p.y0;0;0];
        physicalRhs = @(t,y) rhs_pure_rs_qssa(t,y,p,q);
        physicalJac = @(t,y) jacobian_pure_rs_qssa_chain(t,y,p,q);
        names = p.state_names;
    otherwise
        error('pure_rs:mode','Unknown RS simulation mode.');
end
tgrid = (0:opt.OutputDt:opt.Tfinal)';
if tgrid(end) ~= opt.Tfinal
    tgrid(end+1,1) = opt.Tfinal;
end
odeopts = odeset('RelTol',opt.RelTol,'AbsTol',opt.AbsTol, ...
    'Jacobian',@(t,y) augmented_jacobian(t,y,physicalJac,nphys,p));
rhs = @(t,y) augmented_rhs(t,y,physicalRhs,nphys);
if numel(tgrid)==2
    sol = ode15s(rhs,tgrid,initial,odeopts);
    t = tgrid; Y = deval(sol,t)'; stats = sol.stats;
else
    [t,Y] = ode15s(rhs,tgrid,initial,odeopts);
    stats = struct('note','Solver statistics not collected for requested-grid output.');
end
n = numel(t); R = zeros(n,6); Mqss = zeros(n,1); canonicalVRS = zeros(n,1);
for i = 1:n
    [dy,R(i,:),detail] = physicalRhs(t(i),Y(i,1:nphys)');
    d = rs_timescale_diagnostics(Y(i,1:10)',dy(1:10),p,q);
    fields = fieldnames(d);
    for k = 1:numel(fields)
        diagnostics.(fields{k})(i,1) = d.(fields{k});
    end
    Mqss(i) = rs_qssa_manifold(Y(i,1:10)',p,q);
    canonicalVRS(i,1) = detail.canonical_V_RS;
end
out = struct('mode',mode,'t',t,'y',Y(:,1:nphys),'yfull',Y, ...
    'rates',R,'mRNA',Y(:,3)/(3*p.L),'protein',Y(:,7)/p.L, ...
    'p',p,'q',q,'opts',opt,'stats',stats,'diagnostics',diagnostics, ...
    'M_qss',Mqss,'canonical_V_RS',canonicalVRS);
out.full_state_names = [names,{'D_nt','D_TLcat'}];
out.qc.all_finite = all(isfinite([t Y R out.mRNA out.protein Mqss]),'all');
out.qc.min_per_full_state = min(Y,[],1);
out.qc.negative_count_per_full_state = sum(Y<0,1);
out.qc.min_state_value = min(Y,[],'all');
end

function dy = augmented_rhs(t,y,physicalRhs,nphys)
[physical,r] = physicalRhs(t,y(1:nphys));
dy = [physical;r(2);r(5)];
end

function J = augmented_jacobian(t,y,physicalJac,nphys,p)
J = zeros(nphys+2,nphys+2);
J(1:nphys,1:nphys) = physicalJac(t,y(1:nphys));
J(nphys+1,3) = p.k_nt_deg;
J(nphys+2,10) = p.k_TL_deg;
end
