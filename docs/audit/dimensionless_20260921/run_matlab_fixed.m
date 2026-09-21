% Native MATLAB validation, with actual generated-RHS comparison.
root = fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
target = fullfile(root, 'models', 'literature_reference', 'dimensionless', 'derive_dimensionless.m');
fprintf('MATLAB: %s\n', version);
disp(ver('symbolic'));
disp(checkcode(target, '-id'));
run(target);
addpath(fullfile(root, 'matlab', 'generated'));
parSymbols = [k_TX C_TXcat K_TX_DNA K_TX_NTP k_RS C_RScat K_RS_A K_RS_T ...
    K_RS_NTP k_TL K_TL_nt K_TL_AT K_TL_NTP k_EN C_ENcat K_EN_CP K_EN_NXP ...
    k_ntdeg k_TLdeg n_NTP n_A n_T DNA];
parFields = {'k_TX','TXcat','K_TX_DNA','K_TX_NTP','k_RS','RScat','K_RS_A', ...
    'K_RS_T','K_RS_NTP','k_TL','K_TL_nt','K_TL_AT','K_TL_NTP','k_EN','ENcat', ...
    'K_EN_CP','K_EN_NXP','k_nt_deg','k_TL_deg','n_NTP','n_A','n_T','DNA'};
scaleSymbols = [c_NTP0 cA0 cT0 cCP0 cTL0];
allY = [y1 y2 y3 y4 y5 y6 y7 y8 y9 y10 y11 y12];
compactBack = cellfun(@(v) subs(subs(v, [kapTXdna kapTXntp kapRSa kapRSt ...
    kapRSntp kapTLnt kapTLat kapTLntp kapENcp kapENnxp], ...
    [K_TX_DNA/DNA K_TX_NTP/c_NTP0 K_RS_A/cA0 K_RS_T/(s23*cT0) ...
    K_RS_NTP/c_NTP0 K_TL_nt/(n_NTP*c_NTP0) K_TL_AT/(s23*cT0) ...
    K_TL_NTP/c_NTP0 K_EN_CP/cCP0 K_EN_NXP/(n_NTP*c_NTP0)]), ...
    [mu_TX mu_RS mu_TL mu_EN mu_TLdeg], ...
    [k_TX*C_TXcat/Vstar k_RS*C_RScat/Vstar k_TL*cTL0/Vstar ...
    k_EN*C_ENcat/Vstar k_TLdeg/k_ntdeg]), dy, 'UniformOutput', false);
rng(20260921);
maxResidual = 0;
for trial = 1:5
    p = pure_literature_reference_params();
    p.DNA = 0.0017;
    % Physical multiplicities stay 4,20,46; scales stay independent.
    for j = 1:19
        p.(parFields{j}) = 0.05 + 4.95*rand;
    end
    parVals = cellfun(@(f) p.(f), parFields);
    scaleVals = 0.05 + 4.95*rand(1,5);
    scaleVec = double(subs([scales{:}], [parSymbols scaleSymbols], [parVals scaleVals]));
    yVals = 0.05 + 2.95*rand(1,12);
    dimensionalState = scaleVec.*yVals;
    [dimRHS, rateValues] = rhs_pure_literature_reference(0, dimensionalState(1:10), p);
    directValues = [dimRHS; rateValues(2); rateValues(5)]'./(scaleVec*p.k_nt_deg);
    compactValues = double(subs([compactBack{:}], [parSymbols scaleSymbols allY], ...
        [parVals scaleVals yVals]));
    residuals = abs(compactValues-directValues);
    assert(numel(residuals)==12 && all(isfinite(residuals)) && all(residuals < 1e-12));
    maxResidual = max(maxResidual, max(residuals));
    fprintf('Generated RHS trial %d max residual: %.17g\n', trial, max(residuals));
end
fprintf('GENERATED RHS: PASS (5 x 12), global max absolute residual %.17g\n', maxResidual);
testResults = runtests(fullfile(root, 'matlab', 'tests', 'test_pure_literature_reference.m'));
assert(all([testResults.Passed]));
fprintf('MATLAB AUDIT ALL PASS (%d existing model tests)\n', numel(testResults));
