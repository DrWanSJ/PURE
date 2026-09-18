function tests = test_release_preflight()
%TEST_RELEASE_PREFLIGHT Tests for the repository/provenance/honesty guards.
%
%   results = runtests('matlab/tests/test_release_preflight.m')
%
%   These tests pin the audit-hardening guards:
%     - all development-mode preflight checks pass on the current tree
%     - the locked evidence levels (pending_human_audit / false /
%       non_independent_assignment) cannot be flipped silently
%     - a dirty working tree blocks release_ready in release mode
%     - legacy results cannot claim provenance_bound
%
%   NOTE: passing these AI-written checks is not a human scientific audit.

thisdir = fileparts(mfilename('fullpath'));   % .../matlab/tests
root    = fileparts(fileparts(thisdir));      % project root
addpath(fullfile(root, 'matlab', 'simulate'));
addpath(fullfile(root, 'matlab', 'provenance'));
addpath(fullfile(root, 'matlab', 'codegen'));
addpath(fullfile(root, 'matlab', 'generated'));
tests = functiontests(localfunctions);
end

% =========================================================================
function test_development_checks_all_pass(tc)
res = release_preflight('Mode', 'development');
for i = 1:numel(res.checks)
    tc.verifyTrue(res.checks(i).passed, ...
        sprintf('preflight check "%s" failed: %s', ...
        res.checks(i).name, res.checks(i).detail));
end
end

% =========================================================================
function test_dirty_tree_blocks_release_ready(tc)
% An untracked probe file makes the tree dirty; release mode must then
% refuse release_ready. The file is removed at test exit (cleanup).
thisdir0 = fileparts(mfilename('fullpath'));
root    = fileparts(fileparts(thisdir0));
probe = fullfile(root, 'dirty_probe_tmp.txt');
fid = fopen(probe, 'w'); fprintf(fid, 'probe'); fclose(fid);
cleanup = onCleanup(@() deleteIfExists(probe)); %#ok<NASGU>
res = release_preflight('Mode', 'release');
tc.verifyFalse(res.release_ready, ...
    'release mode must refuse release_ready on a dirty tree');
dirtyCheck = res.checks(strcmp({res.checks.name}, 'git_dirty'));
tc.verifyFalse(dirtyCheck.passed, 'git_dirty check must fail while dirty');
end

% =========================================================================
function deleteIfExists(f)
if exist(f, 'file') == 2; delete(f); end
end

% =========================================================================
function test_evidence_levels_locked_values(tc)
thisdir0 = fileparts(mfilename('fullpath'));
root    = fileparts(fileparts(thisdir0));
ev = jsondecode(fileread(fullfile(root, 'docs', 'evidence_levels.json')));
tc.verifyEqual(ev.evidence_levels.fig4_independent_human_audit, 'pending_human_audit', ...
    'independent Fig.4 audit status must not be flipped by automation');
tc.verifyEqual(ev.evidence_levels.experimental_data_validation, false, ...
    'experimental_data_validation must stay false (no machine-readable Stogbauer data)');
tc.verifyEqual(ev.evidence_levels.fig4_simulation_assisted_digitization_status, ...
    'non_independent_assignment', ...
    'simulation-assisted digitization must stay flagged non-independent');
tc.verifyEqual(ev.evidence_levels.b2_predictive_validation, false, ...
    'B1 reproduction must not be conflated with B2 predictive validation');
end

% =========================================================================
function test_legacy_results_cannot_claim_provenance_bound(tc)
thisdir0 = fileparts(mfilename('fullpath'));
root    = fileparts(fileparts(thisdir0));
legacy = fullfile(root, 'results', 'literature_reference');
dnas = {'DNA_0p34nM', 'DNA_1p7nM', 'DNA_6p8nM'};
files = cell(1, numel(dnas) + 1);
for i = 1:numel(dnas)
    files{i} = fullfile(legacy, dnas{i}, 'qc.json');
end
files{end} = fullfile(legacy, 'benchmark_summary.json');
for i = 1:numel(files)
    txt = fileread(files{i});
    tc.verifyTrue(contains(txt, '"legacy_unbound_to_execution_commit"'), ...
        sprintf('%s must carry the legacy provenance label', files{i}));
    tc.verifyFalse(contains(txt, '"provenance_status": "provenance_bound"'), ...
        sprintf('%s must not claim provenance_bound', files{i}));
end
end
