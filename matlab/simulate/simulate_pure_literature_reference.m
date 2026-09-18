function out = simulate_pure_literature_reference(DNA_uM, varargin)
%SIMULATE_PURE_LITERATURE_REFERENCE Deterministic run of the Mavelli 2015 model.
%
%   OUT = SIMULATE_PURE_LITERATURE_REFERENCE(DNA_UM, ...)
%
%   DNA_UM : DNA template concentration [uM]  (1 nM = 1e-3 uM).
%            Fig. 4 conditions: 0.00034 / 0.0017 / 0.0068 uM.
%
%   Name-value options:
%     'Tfinal'   final time [s]                  (default 14400 = 4 h)
%     'OutputDt' output grid spacing [s]         (default 10)
%     'RelTol'   ode15s relative tolerance       (default 1e-9)
%     'AbsTol'   ode15s absolute tolerance       (default 1e-12)
%
%   The two decay fluxes of the paper (Eqs. (6) and (12)) are additionally
%   integrated as pure accumulator states D_nt and D_TLcat ("degradation
%   species" of conservation Eqs. (15) and (19)). They do not feed back
%   into any rate law, so the dynamics of the 10 physical states is
%   exactly the paper's Eqs. (20)-(27). No state is ever clipped at zero.
%
%   OUT fields:
%     t        output times [s]                        (n x 1)
%     y        physical states, columns = state_names  (n x 10) [uM]
%     yfull    [y, D_nt, D_TLcat]                      (n x 12) [uM]
%     rates    [V_TX V_nt_deg V_RS V_TL V_TL_deg V_EN] (n x 6)  [uM/s]
%     mRNA     nt/(3L)  mRNA molecule concentration    (n x 1)  [uM]
%     protein  a/L      protein molecule concentration (n x 1)  [uM]
%     p        parameter struct used (with p.DNA set)
%     opts     solver options used
%     stats    ode15s statistics
%     qc       nonnegativity / finiteness / conservation diagnostics

p = pure_literature_reference_params();
if ~(isscalar(DNA_uM) && isfinite(DNA_uM) && DNA_uM >= 0)
    error('pure_ref:badDNA', 'DNA_uM must be a finite nonnegative scalar [uM]');
end
p.DNA = DNA_uM;   % fixed input (paper Eq. (5)); never a dynamic state

ip = inputParser;
ip.addParameter('Tfinal',   14400);
ip.addParameter('OutputDt', 10);
ip.addParameter('RelTol',   1e-9);
ip.addParameter('AbsTol',   1e-12);
ip.parse(varargin{:});
opt = ip.Results;

tspan = (0:opt.OutputDt:opt.Tfinal)';
if tspan(end) ~= opt.Tfinal
    tspan(end+1,1) = opt.Tfinal; %#ok<AGROW>
end

% augmented initial state: 10 physical states + 2 pure integrators
z0 = [p.y0(:); 0; 0];

odeopts = odeset('RelTol', opt.RelTol, 'AbsTol', opt.AbsTol);
rhs = @(t, z) rhs_augmented(t, z, p);
[tt, zz, stats] = ode15s(rhs, tspan, z0, odeopts);

% rates re-evaluated on the output grid (cheap, keeps rates/trajectory consistent)
n = numel(tt);
R = zeros(n, 6);
for i = 1:n
    [~, R(i,:)] = rhs_pure_literature_reference(tt(i), zz(i,1:10)', p);
end

out = struct();
out.t      = tt;
out.yfull  = zz;
out.y      = zz(:, 1:10);
out.rates  = R;
out.mRNA   = zz(:,3) / (3*p.L);   % paper Sect. 2.5: [mRNA] = [nt]/(3L)
out.protein = zz(:,7) / p.L;      % paper Sect. 2.5: [protein] = [a]/L
out.p      = p;
out.opts   = opt;
out.stats  = stats;
out.qc     = local_qc(tt, zz, R, p);

end % function

% -------------------------------------------------------------------------
function dz = rhs_augmented(~, z, p)
% Augmented RHS: paper Eqs. (20)-(27) + two pure integrators of the decay
% fluxes (no feedback into any rate law; pure accounting sinks).
[dydt, rates] = rhs_pure_literature_reference(0, z(1:10)', p);
dz = [dydt; rates(2); rates(5)];   % dD_nt/dt = V_nt_deg; dD_TLcat/dt = V_TL_deg
end

% -------------------------------------------------------------------------
function qc = local_qc(t, z, R, p)
% Internal QC: finiteness, nonnegativity (no clipping anywhere), and the
% five conservation relations of paper Eqs. (15)-(19).

qc = struct();
qc.all_finite = all(isfinite(z(:)));

y = z(:, 1:10);
qc.min_state_value = min(y(:));
qc.min_state_name  = p.state_names{find(min(y) == min(y(:)), 1)};
qc.nonnegative     = qc.min_state_value >= 0;

n_NTP = p.n_NTP;  n_A = p.n_A;  n_T = p.n_T;

% conservation targets = initial values (paper Eqs. (15)-(19), C^0 values)
% B1: n_NTP*[NTP] + [nt] + [NXP] + D_nt            (Eq. (15))
% B2: n_A*[A] + [a] + n_T*[AT]                     (Eq. (16))
% B3: n_T*[T] + n_T*[AT]                           (Eq. (17))
% B4: [CP] + [C]                                   (Eq. (18))
% B5: [TLcat] + D_TLcat                            (Eq. (19))
B = [n_NTP*z(:,1) + z(:,3) + z(:,2) + z(:,11), ...
     n_A*z(:,4) + z(:,7) + n_T*z(:,6), ...
     n_T*(z(:,5) + z(:,6)), ...
     z(:,8) + z(:,9), ...
     z(:,10) + z(:,12)];
B0 = B(1, :)';
names = {'B_NTP', 'B_AA', 'B_tRNA', 'B_CP', 'B_TLcat'};
qc.balance_names = names;
qc.balance_reference = B0';
qc.balance_max_abs_residual = max(abs(B - repmat(B0', numel(t), 1)));
qc.balance_max_scaled_residual = qc.balance_max_abs_residual ./ B0';
qc.mass_balance_pass = all(qc.balance_max_scaled_residual <= 1e-8);

% decay-integrator cross-check against trapz of the rate (independent method)
qc.D_nt_end    = z(end, 11);
qc.D_TLcat_end = z(end, 12);
qc.D_nt_trapz    = trapz(t, R(:,2));
qc.D_TLcat_trapz = trapz(t, R(:,5));
qc.D_nt_accumulator_vs_trapz_rel = abs(qc.D_nt_end - qc.D_nt_trapz) ...
    / max(qc.D_nt_trapz, realmin);
qc.D_TLcat_accumulator_vs_trapz_rel = abs(qc.D_TLcat_end - qc.D_TLcat_trapz) ...
    / max(qc.D_TLcat_trapz, realmin);

% energy bookkeeping (paper Sect. 5, Eqs. (33)-(35)): chi_e = n_NTP*[NTP] + [CP]
qc.energy_integral_uM = [trapz(t, R(:,1)), 2*trapz(t, R(:,4)), trapz(t, R(:,3))];
qc.energy_labels = {'Q_TX', 'Q_TL', 'Q_RS'};
Qsum = sum(qc.energy_integral_uM);
qc.energy_split_percent = 100 * qc.energy_integral_uM / max(Qsum, realmin);
end
