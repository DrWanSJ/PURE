function tests = test_pure_literature_reference()
%TEST_PURE_LITERATURE_REFERENCE Equation-level and QC test suite for B1.
%
%   results = runtests('matlab/tests/test_pure_literature_reference.m')
%
%   Covers (benchmark task, Sect. 9):
%     A. finite-difference / short-step derivative sanity check
%     B. ODE consistency with the five paper balance equations (Eqs. (15)-(19))
%     C. observable mapping  [mRNA] = nt/(3L), [protein] = a/L
%     D. K_TL_RNA derived-value check (Eq. (29): K_TL_RNA = K_TL_nt/(3L))
%     E. initial-time sanity: V_TL(0) = 0 (nt = 0), V_EN(0) = 0 (NXP = 0),
%        but V_TX(0) > 0 and V_RS(0) > 0
%   plus a parameter double-entry lock against paper Tables 1-2, an
%   independent rate-law spot check, nonnegativity/mass balance on a
%   finite run, and determinism of repeated runs.
%
%   IMPORTANT: if any of these fail, the first suspicion is a transcription
%   error, NOT parameter refitting (no refitting is allowed in B1).

thisdir = fileparts(mfilename('fullpath'));   % .../matlab/tests
root    = fileparts(fileparts(thisdir));      % project root
addpath(fullfile(root, 'matlab', 'generated'));
addpath(fullfile(root, 'matlab', 'src', 'simulate'));
tests = functiontests(localfunctions);
end

% =========================================================================
function test_parameter_lock_tables_1_and_2(tc)
% Independent double-entry check: parameters.json + loader vs the values
% transcribed here directly from the paper (Table 1, Table 2, Sect. 2).
p = pure_literature_reference_params();

% Table 1: initial concentrations [uM]; multiplicity from Sect. 2; L from Sect. 3
tc.verifyEqual(p.y0, [1500; 0; 0; 300; 1.9; 0; 0; 20000; 0; 2.2], ...
    'initial state does not match Table 1 / zero-initial newly-created species');
tc.verifyEqual(p.TXcat, 0.1);
tc.verifyEqual(p.RScat, 0.16);
tc.verifyEqual(p.ENcat, 0.08);
tc.verifyEqual(p.n_NTP, 4);
tc.verifyEqual(p.n_A,   20);
tc.verifyEqual(p.n_T,   46);
tc.verifyEqual(p.n_T/p.n_A, 2.3);
tc.verifyEqual(p.L, 238);

% Table 2: kinetic constants [s^-1]
tc.verifyEqual(p.k_TX,     1.67);
tc.verifyEqual(p.k_TL,     0.085);
tc.verifyEqual(p.k_RS,     6.2);
tc.verifyEqual(p.k_EN,     100);
tc.verifyEqual(p.k_nt_deg, 7.92e-5);
tc.verifyEqual(p.k_TL_deg, 1.86e-4);

% Table 2: Michaelis-Menten constants [uM]
tc.verifyEqual(p.K_TX_DNA, 5.0e-3);
tc.verifyEqual(p.K_TX_NTP, 80);
tc.verifyEqual(p.K_TL_nt,  226);
tc.verifyEqual(p.K_TL_AT,  10);
tc.verifyEqual(p.K_TL_NTP, 10);
tc.verifyEqual(p.K_RS_A,   23);
tc.verifyEqual(p.K_RS_T,   0.7);
tc.verifyEqual(p.K_RS_NTP, 200);
tc.verifyEqual(p.K_EN_CP,  200);
tc.verifyEqual(p.K_EN_NXP, 40);

% K_TL_RNA must NOT be a flattened RHS parameter (derived QC quantity only)
tc.verifyFalse(any(strcmp('K_TL_RNA', fieldnames(p))), ...
    'K_TL_RNA must stay derived (p.derived), not an independent RHS parameter');
end

% =========================================================================
function test_rate_law_spot_values(tc)
% Independent re-derivation of all six rate laws at a random feasible state.
% Guards against transcription errors in rhs_pure_literature_reference.m.
p = pure_literature_reference_params(); p.DNA = 0.0017;
rng(20260918);
y = [1473.21; 118.44; 612.9; 289.3; 0.94; 0.96; 71.2; 18742.5; 1257.5; 1.93];

% scalar rate expressions typed independently of the implementation
V_TX     = 1.67  * 0.1  * (0.0017/(0.005+0.0017)) * (y(1)/(80+y(1)));
V_nt_deg = 7.92e-5 * y(3);
V_RS     = 6.2   * 0.16 * (y(4)/(23+y(4))) * (2.3*y(5)/(0.7+2.3*y(5))) * (y(1)/(200+y(1)));
V_TL     = 0.085 * y(10) * (y(3)/(226+y(3))) * (2.3*y(6)/(10+2.3*y(6))) * (y(1)/(10+y(1)));
V_TL_deg = 1.86e-4 * y(10);
V_EN     = 100   * 0.08 * (y(8)/(200+y(8))) * (y(2)/(40+y(2)));

[~, R] = rhs_pure_literature_reference(0, y, p);
tc.verifyEqual(R(1), V_TX,     'AbsTol', 1e-15, 'V_TX mismatch');
tc.verifyEqual(R(2), V_nt_deg, 'AbsTol', 1e-15, 'V_nt_deg mismatch');
tc.verifyEqual(R(3), V_RS,     'AbsTol', 1e-15, 'V_RS mismatch');
tc.verifyEqual(R(4), V_TL,     'AbsTol', 1e-15, 'V_TL mismatch');
tc.verifyEqual(R(5), V_TL_deg, 'AbsTol', 1e-15, 'V_TL_deg mismatch');
tc.verifyEqual(R(6), V_EN,     'AbsTol', 1e-15, 'V_EN mismatch');

% ODE right-hand sides, independently recomputed (Eqs. (20)-(27))
dydt_exp = [ ...
    (-V_TX - 2*V_TL - V_RS + V_EN)/4;   % Eq. (20)
    2*V_TL + V_RS - V_EN;               % Eq. (21)
    V_TX - V_nt_deg;                    % Eq. (22)
    -V_RS/20;                           % Eq. (23)
    (-V_RS + V_TL)/46;                  % Eq. (24a)
    (V_RS - V_TL)/46;                   % Eq. (24b)
    V_TL;                               % Eq. (25)
    -V_EN;                              % Eq. (26a)
    V_EN;                               % Eq. (26b)
    -V_TL_deg];                         % Eq. (27)
[dydt, ~] = rhs_pure_literature_reference(0, y, p);
tc.verifyEqual(dydt, dydt_exp, 'AbsTol', 1e-15, 'ODE RHS mismatch');
end

% =========================================================================
function test_initial_rate_sanity(tc)
% Task Sect. 9 E: at t = 0 with Table 1 inputs, nt = 0 => V_TL = 0;
% NXP = 0 => V_EN = 0; AT = 0 => V_TL = 0; but V_TX and V_RS start normally.
for dna = [0.00034, 0.0017, 0.0068]
    p = pure_literature_reference_params(); p.DNA = dna;
    [dydt, R] = rhs_pure_literature_reference(0, p.y0, p);
    tc.verifyEqual(R(4), 0, 'V_TL(0) must be 0 (nt = 0 and AT = 0)');
    tc.verifyEqual(R(6), 0, 'V_EN(0) must be 0 (NXP = 0)');
    tc.verifyGreaterThan(R(1), 0, 'V_TX(0) must be > 0');
    tc.verifyGreaterThan(R(3), 0, 'V_RS(0) must be > 0');
    tc.verifyGreaterThan(dydt(2), 0, 'd[NXP]/dt(0) = V_RS must be > 0');
    tc.verifyGreaterThan(dydt(3), 0, 'd[nt]/dt(0) = V_TX must be > 0');
    tc.verifyGreaterThan(dydt(6), 0, 'd[AT]/dt(0) = V_RS/n_T must be > 0');
    tc.verifyLessThan(dydt(1), 0, 'd[NTP]/dt(0) must be < 0');
    tc.verifyLessThan(dydt(4), 0, 'd[A]/dt(0) must be < 0');
    tc.verifyLessThan(dydt(5), 0, 'd[T]/dt(0) must be < 0');
    tc.verifyEqual(dydt(8), 0, 'd[C]/dt(0) = V_EN(0) must be 0 (NXP = 0)');
end
end

% =========================================================================
function test_balance_derivative_identities_random_states(tc)
% Task Sect. 9 B: the five conservation relations of Eqs. (15)-(19) must be
% invariant under Eqs. (20)-(27). Checked as exact derivative identities at
% random feasible states (to floating-point roundoff). A transcription error
% (e.g. a lost 2*V_TL factor) breaks these identities at O(1).
p = pure_literature_reference_params(); p.DNA = 0.0068;
rng(42);
nTrials = 200;
maxviol = 0;
for i = 1:nTrials
    T0 = 1.9;                     % tRNA conservation: [T] + [AT] = T0
    CP0 = 20000;                  % CP conservation:  [CP] + [C]  = CP0
    y = [1500*rand; 1000*rand; 1000*rand; 300*rand; ...
         T0*rand; T0 - T0*rand; 4000*rand; ...
         CP0*rand; CP0 - CP0*rand; 2.2*rand];
    [dydt, R] = rhs_pure_literature_reference(0, y, p);
    % B1' = n_NTP*d[NTP]/dt + d[nt]/dt + d[NXP]/dt + D_nt'   (Eq. (15))
    v1 = p.n_NTP*dydt(1) + dydt(3) + dydt(2) + R(2);
    % B2' = n_A*d[A]/dt + d[a]/dt + n_T*d[AT]/dt             (Eq. (16))
    v2 = p.n_A*dydt(4) + dydt(7) + p.n_T*dydt(6);
    % B3' = n_T*(d[T]/dt + d[AT]/dt)                          (Eq. (17))
    v3 = p.n_T*(dydt(5) + dydt(6));
    % B4' = d[CP]/dt + d[C]/dt                                (Eq. (18))
    v4 = dydt(8) + dydt(9);
    % B5' = d[TLcat]/dt + D_TLcat'                            (Eq. (19))
    v5 = dydt(10) + R(5);
    maxviol = max(maxviol, abs([v1, v2, v3, v4, v5]));
end
tc.verifyLessThan(maxviol, 1e-9, ...
    sprintf('balance-derivative violation = %.3e (check equation transcription, do NOT refit)', maxviol));
end

% =========================================================================
function test_finite_difference_short_step(tc)
% Task Sect. 9 A: short-step central finite differences of the numerical
% solution agree with the analytic RHS (up to O(h^2) truncation).
p = pure_literature_reference_params(); p.DNA = 0.0017;
rhs = @(t, z) rhs_pure_literature_reference(t, z, p);
opts = odeset('RelTol', 1e-12, 'AbsTol', 1e-13);

tstar = 600;
[~, ys] = ode15s(@(t, z) rhs_aug(t, z, p), [0 tstar], [p.y0; 0; 0], opts);
ystar = ys(end, :)';   % solution at t* (ode15s returns a row per output time)
[dfdt, ~] = rhs_pure_literature_reference(tstar, ystar(1:10), p);
dfdt = dfdt(:)';   % dydt (1st output) as a row, to match the FD rows below

h = 0.5;
[~, y1] = ode15s(@(t, z) rhs_aug(t, z, p), [tstar tstar+h],   ystar, opts);
[~, y2] = ode15s(@(t, z) rhs_aug(t, z, p), [tstar tstar-h],   ystar, opts);
[~, y3] = ode15s(@(t, z) rhs_aug(t, z, p), [tstar tstar+h/2], ystar, opts);
[~, y4] = ode15s(@(t, z) rhs_aug(t, z, p), [tstar tstar-h/2], ystar, opts);
D_h  = (y1(end, :) - y2(end, :)) / (2*h);
D_h2 = (y3(end, :) - y4(end, :)) / h;

err_h  = max(abs(D_h(1:10)  - dfdt));
err_h2 = max(abs(D_h2(1:10) - dfdt));
tc.verifyLessThan(err_h, 5e-4, ...
    sprintf('central FD vs analytic RHS error = %.3e (transcription check, not refit)', err_h));
tc.verifyLessThan(err_h2, err_h, 'halving the step must not increase the FD error');
end

% =========================================================================
function test_observable_mapping(tc)
% Task Sect. 9 C: [mRNA] = nt/(3L), [protein] = a/L, L = 238 (paper Sect. 2.5).
p = pure_literature_reference_params();
tc.verifyEqual(p.L, 238);
out = simulate_pure_literature_reference(0.00034, 'Tfinal', 600, 'OutputDt', 60);
tc.verifyTrue(isequal(out.mRNA, out.y(:,3)/(3*p.L)), 'mRNA mapping must be nt/(3L)');
tc.verifyTrue(isequal(out.protein, out.y(:,7)/p.L), 'protein mapping must be a/L');
tc.verifyEqual(out.mRNA(1), 0, 'mRNA(0) = 0 because nt(0) = 0');
tc.verifyEqual(out.protein(1), 0, 'protein(0) = 0 because a(0) = 0');
tc.verifyGreaterThan(out.protein(end), 0, 'protein must be positive at the end of the run');
end

% =========================================================================
function test_ktl_rna_derived_value(tc)
% Task Sect. 9 D: Eq. (29) K_TL_RNA = K_TL_nt/(3L) = 226/714 = 0.3165 uM,
% consistent with the Table 2 reported 0.32 +/- 0.02 uM. Derived QC only.
p = pure_literature_reference_params();
k = p.derived.K_TL_RNA;
tc.verifyEqual(k.value, p.K_TL_nt/(3*p.L), 'AbsTol', 1e-12, ...
    'derived K_TL_RNA must equal K_TL_nt/(3L)');
tc.verifyLessThanOrEqual(abs(k.value - k.paper_reported), k.paper_uncertainty, ...
    '226/714 = 0.3165 must be consistent with Table 2 value 0.32 +/- 0.02');
tc.verifyEqual(strcmp(k.formula, 'K_TL_nt/(3*L)'), true);
end

% =========================================================================
function test_short_run_mass_balance_and_nonnegativity(tc)
% Internal numerical QC on a full 1 h run at 1.7 nM: the five conservation
% relations Eqs. (15)-(19), nonnegativity without any clipping, finiteness,
% and accumulator-vs-trapz cross-check of the decay fluxes.
out = simulate_pure_literature_reference(0.0017, 'Tfinal', 3600, 'OutputDt', 10);
qc = out.qc;
tc.verifyTrue(qc.all_finite, 'trajectory must be finite');
tc.verifyTrue(qc.nonnegative, ...
    sprintf('states must stay nonnegative without clipping (min = %g)', qc.min_state_value));
tc.verifyTrue(qc.mass_balance_pass, ...
    sprintf('max scaled balance residual = %.3e', max(qc.balance_max_scaled_residual)));
tc.verifyLessThan(qc.D_nt_accumulator_vs_trapz_rel, 1e-2);
tc.verifyLessThan(qc.D_TLcat_accumulator_vs_trapz_rel, 1e-2);
tc.verifyGreaterThan(out.y(end,3), 0, 'nt must be positive at 1 h');
tc.verifyGreaterThan(out.y(end,7), 0, 'a must be positive at 1 h');
end

% =========================================================================
function test_repeatability_deterministic(tc)
% Repeated runs of the same condition must be numerically identical.
o1 = simulate_pure_literature_reference(0.0068, 'Tfinal', 3600, 'OutputDt', 30);
o2 = simulate_pure_literature_reference(0.0068, 'Tfinal', 3600, 'OutputDt', 30);
tc.verifyTrue(isequal(o1.yfull, o2.yfull), 'repeated runs must be identical (states)');
tc.verifyTrue(isequal(o1.rates, o2.rates), 'repeated runs must be identical (rates)');
end

% =========================================================================
function dz = rhs_aug(~, z, p)
% Augmented RHS used by the finite-difference test (10 states + 2 sinks).
[dydt, rates] = rhs_pure_literature_reference(0, z(1:10)', p);
dz = [dydt; rates(2); rates(5)];
end
