function summary = run_all_tests()
%RUN_ALL_TESTS Run every B1 check with a persisted log (audit hardening).
%
%   SUMMARY = RUN_ALL_TESTS()
%
%   Runs, in order:
%     1. the full unit-test suite (matlab/tests) via runtests
%     2. a benchmark smoke test (short deterministic simulation + QC asserts)
%     3. release_preflight in development mode (if available)
%
%   All output is appended to logs/<timestamp>_tests.log — test results must
%   exist as logs, not only as claims in a README. CI status is
%   not_verified (docs/audit_status.md); this script is the manual path.

d0   = fileparts(mfilename('fullpath'));         % .../scripts
root = fileparts(d0);
addpath(fullfile(root, 'matlab', 'tests'));
addpath(fullfile(root, 'matlab', 'simulate'));
addpath(fullfile(root, 'matlab', 'generated'));
addpath(fullfile(root, 'matlab', 'codegen'));
addpath(fullfile(root, 'matlab', 'provenance'));

logdir = fullfile(root, 'logs');
if ~exist(logdir, 'dir'); mkdir(logdir); end
logfile = fullfile(logdir, sprintf('%s_tests.log', ...
    char(datetime('now', 'Format', 'yyyyMMdd_HHmmss'))));
diary(logfile);
fprintf('==== PURE B1 run_all_tests | %s | MATLAB %s ====\n', ...
    char(datetime('now')), version);

summary = struct();
fprintf('\n--- 1. unit tests (matlab/tests) ---\n');
r = runtests(fullfile(root, 'matlab', 'tests'));
summary.unit_tests_passed = sum([r.Passed]);
summary.unit_tests_failed = sum([r.Failed]);
for i = 1:numel(r)
    fprintf('%-70s passed=%d failed=%d (%.2f s)\n', ...
        r(i).Name, r(i).Passed, r(i).Failed, r(i).Duration);
end
fprintf('unit tests: %d passed, %d failed\n', ...
    summary.unit_tests_passed, summary.unit_tests_failed);

fprintf('\n--- 2. benchmark smoke test ---\n');
try
    out = simulate_pure_literature_reference(0.0068, 'Tfinal', 600, 'OutputDt', 60);
    qc = out.qc;
    assert(qc.all_finite, 'smoke: trajectory not finite');
    assert(qc.nonnegative, 'smoke: negative state encountered');
    assert(qc.mass_balance_pass, 'smoke: conservation violated');
    fprintf(['smoke test: PASS (600 s @ 6.8 nM; min state %g uM; max scaled ' ...
        'balance residual %.3e)\n'], qc.min_state_value, ...
        max(qc.balance_max_scaled_residual));
    summary.smoke_test = 'passed';
catch err
    fprintf('smoke test: FAIL (%s)\n', err.message);
    summary.smoke_test = ['failed: ' err.message];
end

fprintf('\n--- 3. release preflight (development mode) ---\n');
if exist('release_preflight', 'file') == 2
    res = release_preflight('Mode', 'development');
    summary.preflight = res;
    fprintf('preflight release_ready (release mode): %d\n', res.release_ready);
else
    fprintf('release_preflight.m not present - skipped\n');
    summary.preflight = 'not_present';
end

fprintf('\n==== run_all_tests summary ====\n');
disp(summary);
fprintf('log file: %s\n', logfile);
diary off;
end
