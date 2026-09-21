%% check_environment.m
% Environment smoke test for PURE / SynCell project.
% Checks MATLAB, Symbolic Math Toolbox, Optimization Toolbox, and SimBiology.
% This script does not modify model definitions or repository data.

clear;
clc;

fprintf('============================================================\n');
fprintf('PURE environment check\n');
fprintf('Date: %s\n', char(datetime('now')));
fprintf('MATLAB: %s\n', version);
fprintf('Computer: %s\n', computer);
fprintf('============================================================\n\n');

results = struct();

%% MATLAB base
fprintf('[1/4] MATLAB base test...\n');
results.MATLAB.installed = true;
results.MATLAB.version = version;
try
    [t, y] = ode15s(@(t,y) -y, [0 1], 1);
    assert(~isempty(t));
    assert(all(isfinite(y)));
    results.MATLAB.smoke_test = true;
    results.MATLAB.message = 'ode15s executed successfully';
    fprintf('      PASS: ode15s works.\n');
catch ME
    results.MATLAB.smoke_test = false;
    results.MATLAB.message = ME.message;
    fprintf('      FAIL: %s\n', ME.message);
end

%% Symbolic Math Toolbox
fprintf('\n[2/4] Symbolic Math Toolbox test...\n');
results.Symbolic.function_found = exist('syms', 'file') ~= 0 || exist('sym', 'class') ~= 0;
try
    results.Symbolic.license_available = license('test', 'Symbolic_Toolbox');
catch
    results.Symbolic.license_available = NaN;
end
try
    syms x
    expr = simplify((x + 1)^2 - (x^2 + 2*x + 1));
    assert(isAlways(expr == 0));
    results.Symbolic.smoke_test = true;
    results.Symbolic.message = 'symbolic simplify executed successfully';
    fprintf('      PASS: symbolic calculation works.\n');
catch ME
    results.Symbolic.smoke_test = false;
    results.Symbolic.message = ME.message;
    fprintf('      FAIL: %s\n', ME.message);
end

%% Optimization Toolbox
fprintf('\n[3/4] Optimization Toolbox test...\n');
results.Optimization.function_found = exist('fsolve', 'file') ~= 0;
try
    results.Optimization.license_available = license('test', 'Optimization_Toolbox');
catch
    results.Optimization.license_available = NaN;
end
try
    opts = optimoptions('fsolve', 'Display', 'none');
    [xsol, ~, exitflag] = fsolve(@(x) x.^2 - 2, 1, opts);
    assert(exitflag > 0);
    assert(abs(xsol - sqrt(2)) < 1e-8);
    results.Optimization.smoke_test = true;
    results.Optimization.message = sprintf('fsolve executed successfully; x = %.15g', xsol);
    fprintf('      PASS: fsolve works. sqrt(2) = %.12f\n', xsol);
catch ME
    results.Optimization.smoke_test = false;
    results.Optimization.message = ME.message;
    fprintf('      FAIL: %s\n', ME.message);
end

%% SimBiology
fprintf('\n[4/4] SimBiology test...\n');
results.SimBiology.function_found = exist('sbiomodel', 'file') ~= 0;
try
    results.SimBiology.license_available = license('test', 'SimBiology');
catch
    results.SimBiology.license_available = NaN;
end
try
    m = sbiomodel('environment_check_model');
    c = addcompartment(m, 'cell', 1);
    addspecies(c, 'X', 'InitialAmount', 1);
    assert(~isempty(m));
    assert(~isempty(c));
    results.SimBiology.smoke_test = true;
    results.SimBiology.message = 'SimBiology model construction executed successfully';
    fprintf('      PASS: SimBiology model construction works.\n');
catch ME
    results.SimBiology.smoke_test = false;
    results.SimBiology.message = ME.message;
    fprintf('      FAIL: %s\n', ME.message);
end

%% Summary
fprintf('\n============================================================\n');
fprintf('SUMMARY\n');
fprintf('============================================================\n');
fprintf('MATLAB base          : %s\n', passfail(results.MATLAB.smoke_test));
fprintf('Symbolic Toolbox     : %s\n', passfail(results.Symbolic.smoke_test));
fprintf('Optimization Toolbox : %s\n', passfail(results.Optimization.smoke_test));
fprintf('SimBiology           : %s\n', passfail(results.SimBiology.smoke_test));

all_pass = results.MATLAB.smoke_test && ...
           results.Symbolic.smoke_test && ...
           results.Optimization.smoke_test && ...
           results.SimBiology.smoke_test;

fprintf('------------------------------------------------------------\n');
fprintf('OVERALL              : %s\n', passfail(all_pass));
fprintf('============================================================\n');

%% Machine-readable output
results.overall_pass = all_pass;
results.checked_at = char(datetime('now'));
results.matlab_version = version;
results.computer = computer;

jsonText = jsonencode(results, PrettyPrint=true);
outputDir = fullfile('results', 'environment');
if ~exist(outputDir, 'dir')
    mkdir(outputDir);
end
outputFile = fullfile(outputDir, 'toolbox_check.json');
fid = fopen(outputFile, 'w');
if fid == -1
    warning('Could not write %s', outputFile);
else
    fwrite(fid, jsonText, 'char');
    fclose(fid);
    fprintf('\nSaved machine-readable report:\n');
    fprintf('  %s\n', outputFile);
end

function out = passfail(tf)
    if tf
        out = 'PASS';
    else
        out = 'FAIL';
    end
end
