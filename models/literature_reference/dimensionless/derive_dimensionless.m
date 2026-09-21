%% derive_dimensionless.m
% PURE literature-reference model: symbolic nondimensionalization.
% Time scale: tau = k_ntdeg * t.
% Requires MATLAB Symbolic Math Toolbox.
%
% The physical ODEs follow Mavelli 2015. D_nt and D_TLcat are auxiliary
% accounting integrators used only to close the conservation ledgers.

clc;

%% 1. Symbols
syms NTP NXP nt A T AT a CP C TLcat D_nt D_TLcat DNA positive
syms k_TX C_TXcat K_TX_DNA K_TX_NTP positive
syms k_RS C_RScat K_RS_A K_RS_T K_RS_NTP positive
syms k_TL K_TL_nt K_TL_AT K_TL_NTP positive
syms k_EN C_ENcat K_EN_CP K_EN_NXP positive
syms k_ntdeg k_TLdeg positive
syms n_NTP n_A n_T c_NTP0 cA0 cT0 cCP0 cTL0 positive
syms y1 y2 y3 y4 y5 y6 y7 y8 y9 y10 y11 y12 nonnegative
syms mu_TX mu_RS mu_TL mu_EN mu_TLdeg positive
syms kapTXdna kapTXntp kapRSa kapRSt kapRSntp positive
syms kapTLnt kapTLat kapTLntp kapENcp kapENnxp positive

s23 = n_T/n_A; % canonical RHS; exactly 23/10 at n_T=46, n_A=20

%% 2. Dimensional rates
V_TX = k_TX*C_TXcat * DNA/(K_TX_DNA + DNA) * NTP/(K_TX_NTP + NTP);
V_RS = k_RS*C_RScat * A/(K_RS_A + A) * (s23*T)/(K_RS_T + s23*T) * NTP/(K_RS_NTP + NTP);
V_TL = k_TL*TLcat * nt/(K_TL_nt + nt) * (s23*AT)/(K_TL_AT + s23*AT) * NTP/(K_TL_NTP + NTP);
V_EN = k_EN*C_ENcat * CP/(K_EN_CP + CP) * NXP/(K_EN_NXP + NXP);
V_ntdeg = k_ntdeg*nt;
V_TLdeg = k_TLdeg*TLcat;

%% 3. Dimensional ODE RHS
rhs = { ...
    (-V_TX - V_RS - 2*V_TL + V_EN)/n_NTP; ... % NTP
     V_RS + 2*V_TL - V_EN; ...                  % NXP
     V_TX - V_ntdeg; ...                        % nt
    -V_RS/n_A; ...                              % A
    (-V_RS + V_TL)/n_T; ...                     % T
    ( V_RS - V_TL)/n_T; ...                     % AT
     V_TL; ...                                   % a
    -V_EN; ...                                   % CP
     V_EN; ...                                   % C
    -V_TLdeg; ...                                % TLcat
     V_ntdeg; ...                                % D_nt
     V_TLdeg};                                   % D_TLcat

% Dimensional conservation checks.
resNTP = simplify(n_NTP*rhs{1} + rhs{3} + rhs{2} + rhs{11});
resAA  = simplify(n_A*rhs{4} + rhs{7} + n_T*rhs{6});
resT   = simplify(n_T*rhs{5} + n_T*rhs{6});
resCP  = simplify(rhs{8} + rhs{9});
resTL  = simplify(rhs{10} + rhs{12});
assert(isAlways(resNTP == 0));
assert(isAlways(resAA == 0));
assert(isAlways(resT == 0));
assert(isAlways(resCP == 0));
assert(isAlways(resTL == 0));

%% 4. Scales and substitutions
scales = {c_NTP0, n_NTP*c_NTP0, n_NTP*c_NTP0, cA0, cT0, cT0, ...
          n_A*cA0, cCP0, cCP0, cTL0, n_NTP*c_NTP0, cTL0};

oldConc = [NTP, NXP, nt, A, T, AT, a, CP, C, TLcat, D_nt, D_TLcat];
newConc = [y1*c_NTP0, y2*n_NTP*c_NTP0, y3*n_NTP*c_NTP0, ...
           y4*cA0, y5*cT0, y6*cT0, y7*n_A*cA0, y8*cCP0, y9*cCP0, ...
           y10*cTL0, y11*n_NTP*c_NTP0, y12*cTL0];

oldK = [K_TX_DNA, K_TX_NTP, K_RS_A, K_RS_T, K_RS_NTP, ...
        K_TL_nt, K_TL_AT, K_TL_NTP, K_EN_CP, K_EN_NXP];
newK = [kapTXdna*DNA, kapTXntp*c_NTP0, kapRSa*cA0, kapRSt*s23*cT0, ...
        kapRSntp*c_NTP0, kapTLnt*n_NTP*c_NTP0, kapTLat*s23*cT0, ...
        kapTLntp*c_NTP0, kapENcp*cCP0, kapENnxp*n_NTP*c_NTP0];

oldMu = [k_TX, k_RS, k_TL, k_EN, k_TLdeg];
newMu = [mu_TX*k_ntdeg*n_NTP*c_NTP0/C_TXcat, ...
         mu_RS*k_ntdeg*n_NTP*c_NTP0/C_RScat, ...
         mu_TL*k_ntdeg*n_NTP*c_NTP0/cTL0, ...
         mu_EN*k_ntdeg*n_NTP*c_NTP0/C_ENcat, ...
         mu_TLdeg*k_ntdeg];

Vstar = k_ntdeg*n_NTP*c_NTP0;

%% 5. Dimensionless rates v_j = V_j/Vstar
rateDim = {V_TX, V_RS, V_TL, V_EN};
v = cell(size(rateDim));
for j = 1:numel(rateDim)
    expr = subs(rateDim{j}, oldConc, newConc);
    expr = subs(expr, oldK, newK);
    expr = subs(expr, oldMu, newMu);
    v{j} = simplify(expr/Vstar); % factor returns a VECTOR of factors in MATLAB
    assert(isscalar(v{j}));
end
vTX = v{1};
vRS = v{2};
vTL = v{3};
vEN = v{4};

rhoA = n_NTP*c_NTP0/(n_A*cA0);
rhoT = n_NTP*c_NTP0/(n_T*cT0);
rhoC = n_NTP*c_NTP0/cCP0;
muTLD = mu_TLdeg;

%% 6. Compact dimensionless ODEs
% dy_i/dtau = rhs_i/(scale_i*k_ntdeg)
dy = { ...
    -vTX - vRS - 2*vTL + vEN; ...
     vRS + 2*vTL - vEN; ...
     vTX - y3; ...
    -rhoA*vRS; ...
     rhoT*(-vRS + vTL); ...
     rhoT*( vRS - vTL); ...
     rhoA*vTL; ...
    -rhoC*vEN; ...
     rhoC*vEN; ...
    -muTLD*y10; ...
     y3; ...
     muTLD*y10};

% Dimensionless conservation checks.
resDim = { ...
    simplify(dy{1} + dy{2} + dy{3} + dy{11}); ...
    simplify((dy{4} + dy{7})/rhoA + dy{6}/rhoT); ...
    simplify(dy{5} + dy{6}); ...
    simplify(dy{8} + dy{9}); ...
    simplify(dy{10} + dy{12})};

for j = 1:numel(resDim)
    assert(isAlways(resDim{j} == 0));
end

% Independent chain-rule path from each dimensional ODE.
for i = 1:12
    direct = subs(rhs{i}, oldConc, newConc)/(scales{i}*k_ntdeg);
    direct = subs(subs(direct, oldK, newK), oldMu, newMu);
    residual = simplify(dy{i} - direct);
    assert(isscalar(residual) && isAlways(residual == 0));
    fprintf('ODE %d symbolic equivalence: PASS (residual 0)\n', i);
end

%% 7. Write generated result
names = {'y1 [NTP]','y2 [NXP]','y3 [nt]','y4 [A]','y5 [T]','y6 [AT]', ...
         'y7 [a]','y8 [CP]','y9 [C]','y10 [TLcat]','y11 [D_nt]','y12 [D_TLcat]'};

% Keep the curated compact reference intact; this is generated CAS output.
outPath = fullfile(fileparts(mfilename('fullpath')), 'dimensionless_result_matlab.txt');
fid = fopen(outPath, 'w');
assert(fid ~= -1, 'Cannot open generated output: %s', outPath);
cleanupObj = onCleanup(@() fclose(fid));

fprintf(fid, 'Dimensionless rates: v_j = V_j/(k_ntdeg*n_NTP*c_NTP0)\n');
fprintf(fid, 'v_TX = %s\n', char(latex(vTX)));
fprintf(fid, 'v_RS = %s\n', char(latex(vRS)));
fprintf(fid, 'v_TL = %s\n', char(latex(vTL)));
fprintf(fid, 'v_EN = %s\n\n', char(latex(vEN)));

fprintf(fid, 'Dimensionless ODEs: dy_i/dtau\n');
for i = 1:12
    fprintf(fid, 'd%s/dtau = %s\n', names{i}, char(latex(simplify(dy{i}))));
end

fprintf('\nAll dimensional and dimensionless conservation checks passed.\n');
fprintf('Result written to %s\n', outPath);
clear cleanupObj; % Close the file even when invoked from a shared workspace.
