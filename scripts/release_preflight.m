function res = release_preflight(varargin)
%RELEASE_PREFLIGHT Repository, provenance and honesty guards (audit hardening).
%
%   RES = RELEASE_PREFLIGHT('Mode', MODE)
%
%   MODE: 'development' (default) | 'release'
%
%   Checks (each reported as name/passed/detail):
%     git_in_repo               the project root is inside a git work tree
%     head_resolvable           `git rev-parse HEAD` returns a 40-hex commit
%     git_dirty                 live dirty-tree check. In RELEASE mode a
%                               dirty tree BLOCKS release_ready; in
%                               development mode it is recorded (any new
%                               run manifest must carry git_dirty=true).
%     hashes_computable         SHA-256 of model_definition.json and
%                               parameters.json can be computed
%     generated_in_sync         the checked-in generated RHS is byte-stable
%                               under the generator (regenerate + compare)
%     legacy_provenance_labels  legacy results carry
%                               legacy_unbound_to_execution_commit and do
%                               NOT claim provenance_bound
%     manifests_wellformed      every results/runs/<run_id>/manifest.json has all
%                               required provenance fields
%     evidence_guards           docs/project/evidence_levels.json pending/false
%                               values are still in place (pending human
%                               audit cannot be silently flipped)
%     tests_evidence_log        if equation_level_tests_passed = true, a
%                               persisted test log must exist under logs/
%                               (scratch) or docs/audit/logs/ (committed
%                               evidence)
%
%   RES.release_ready is true ONLY in release mode with all checks passed.
%   This tool is part of the hardening pass; it does not replace human
%   scientific review.

ip = inputParser;
d0 = fileparts(mfilename('fullpath'));            % .../scripts
root = fileparts(d0);
ip.addParameter('Mode', 'development', @(m) any(strcmp(m, {'development', 'release'})));
ip.parse(varargin{:});
mode = ip.Results.Mode;

C = {};   % rows: mkCheck structs (name, passed, detail)

% --- git facts ---------------------------------------------------------
git = pure_git_state(root);
C{end+1} = mkCheck('git_in_repo', git.in_repo, sprintf('in_repo=%d', git.in_repo));
head_ok = ~isempty(regexp(git.commit, '^[0-9a-f]{40}$', 'once'));
C{end+1} = mkCheck('head_resolvable', head_ok, sprintf('HEAD = %s', git.commit));
if strcmp(mode, 'release')
    C{end+1} = mkCheck('git_dirty', islogical(git.dirty) && ~git.dirty, ...
        sprintf('git_dirty=%s (dirty tree blocks release-ready)', mat2str(git.dirty)));
else
    C{end+1} = mkCheck('git_dirty_determined', islogical(git.dirty) || strcmp(git.dirty, 'unknown'), ...
        sprintf(['git_dirty=%s (recorded; new-run manifests must carry it; ' ...
        'dirty does not block development)'], mat2str(git.dirty)));
end

% --- hashes ------------------------------------------------------------
defpath = fullfile(root, 'models', 'literature_reference', 'model_definition.json');
parpath = fullfile(root, 'models', 'literature_reference', 'parameters.json');
try
    h1 = pure_sha256_file(defpath); h2 = pure_sha256_file(parpath);
    ok = ~isempty(regexp(h1, '^[0-9a-f]{64}$', 'once')) && ...
         ~isempty(regexp(h2, '^[0-9a-f]{64}$', 'once'));
    C{end+1} = mkCheck('hashes_computable', ok, sprintf('definition=%s parameters=%s', h1(1:12), h2(1:12)));
catch err
    C{end+1} = mkCheck('hashes_computable', false, err.message);
end

% --- generated artifact in sync ----------------------------------------
tmp = [tempname(), '.m'];
cleanup = onCleanup(@() delete(tmp));
try
    generate_pure_literature_reference('OutputFile', tmp, 'SkipConsistencyCheck', true);
    a = normalize_src(fileread(fullfile(root, 'matlab', 'generated', ...
        'rhs_pure_literature_reference.m')));
    b = normalize_src(fileread(tmp));
    C{end+1} = mkCheck('generated_in_sync', strcmp(a, b), ...
        'checked-in generated RHS == regenerated output');
catch err
    C{end+1} = mkCheck('generated_in_sync', false, err.message);
end

% --- legacy results must not pretend provenance-completeness -----------
legacy = fullfile(root, 'results', 'baselines', 'b1_mavelli2015');
dnas = {'DNA_0p34nM', 'DNA_1p7nM', 'DNA_6p8nM'};
legfiles = cell(1, numel(dnas) + 1);
for i = 1:numel(dnas)
    legfiles{i} = fullfile(legacy, dnas{i}, 'qc.json');
end
legfiles{end} = fullfile(legacy, 'benchmark_summary.json');
ok = true; det = '';
for i = 1:numel(legfiles)
    txt = fileread(legfiles{i});
    hasLegacy = contains(txt, '"legacy_unbound_to_execution_commit"');
    hasBound  = contains(txt, '"provenance_bound"');
    if ~hasLegacy || hasBound
        ok = false; det = sprintf('%s%s ', det, legfiles{i});
    end
end
C{end+1} = mkCheck('legacy_provenance_labels', ok, ...
    'legacy files carry legacy_unbound_to_execution_commit and never claim provenance_bound');
if ~isempty(det)
    C{end}.detail = ['violations: ' det];
end

% --- new-run manifests --------------------------------------------------
mandirs = arrayfun(@(d) fullfile(root, 'results', 'runs', d.name), ...
    dir(fullfile(root, 'results', 'runs', 'b1_*')), 'UniformOutput', false);
reqfields = {'run_id', 'model_id', 'model_definition_hash', 'parameter_hash', ...
    'input_hash', 'git_commit', 'git_dirty', 'matlab_version', 'solver', ...
    'solver_options', 'command', 'created_at', 'execution_status', ...
    'scientific_status'};
nman = 0; ok = true; det = '';
for i = 1:numel(mandirs)
    mf = fullfile(mandirs{i}, 'manifest.json');
    if exist(mf, 'file') ~= 2; continue; end
    nman = nman + 1;
    m = jsondecode(fileread(mf));
    for k = 1:numel(reqfields)
        if ~isfield(m, reqfields{k})
            ok = false;
            det = sprintf('%s%s missing %s; ', det, mf, reqfields{k});
        end
    end
end
if nman == 0
    C{end+1} = mkCheck('manifests_wellformed', true, 'no provenance-bound runs yet (results/runs/b1_*)');
else
    C{end+1} = mkCheck('manifests_wellformed', ok, sprintf('%d manifest(s) checked; %s', nman, det));
end

% --- evidence-level guards ---------------------------------------------
evpath = fullfile(root, 'docs', 'project', 'evidence_levels.json');
ev = jsondecode(fileread(evpath));
locked = { ...
    'fig4_independent_human_audit', 'pending_human_audit'; ...
    'experimental_data_validation', false; ...
    'fig4_simulation_assisted_digitization_status', 'non_independent_assignment'; ...
    'b2_predictive_validation', false};
ok = true; det = '';
for k = 1:size(locked, 1)
    want = locked{k, 2};
    got = ev.evidence_levels.(locked{k, 1});
    same = isequal(got, want);
    if ~same
        ok = false;
        det = sprintf('%s%s flipped (%s); ', det, locked{k, 1}, mat2str(got));
    end
end
C{end+1} = mkCheck('evidence_guards', ok, ...
    'pending/false evidence levels are intact; flipping them requires editing this check too');
if ~isempty(det)
    C{end}.detail = det;
end

% --- persisted test log ------------------------------------------------
if ev.evidence_levels.equation_level_tests_passed == true
    logdir = fullfile(root, 'logs');                      % scratch, not committed
    evlogdir = fullfile(root, 'docs', 'audit', 'logs');   % committed evidence
    dlogs = [dir(fullfile(logdir, '*_tests.log')); ...
             dir(fullfile(evlogdir, '*_tests.log'))];
    C{end+1} = mkCheck('tests_evidence_log', ~isempty(dlogs), ...
        sprintf(['%d test log file(s) under logs/ or docs/audit/logs/ ' ...
        '(AI-written tests, not human review)'], numel(dlogs)));
end

% --- aggregate ----------------------------------------------------------
allpass = all(arrayfun(@(c) c.passed, [C{:}]));
res = struct();
res.mode = mode;
res.checks = [C{:}];   % struct array (name, passed, detail)
res.release_ready = (strcmp(mode, 'release') && allpass);
res.development_checks_passed = allpass;
res.checked_at = char(datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss'));

fprintf('release_preflight (%s mode):\n', mode);
for i = 1:numel(C)
    fprintf('  [%s] %-26s %s\n', terne(C{i}.passed, 'ok ', 'FAIL'), ...
        C{i}.name, C{i}.detail);
end
fprintf('  => release_ready: %d\n', res.release_ready);
end

function t = normalize_src(txt)
t = strrep(txt, sprintf('\r\n'), sprintf('\n'));
lines = regexp(t, sprintf('\n'), 'split');
lines = regexprep(lines, '[ \t]+$', '');
lines = lines(1:max(find(~strcmp(strtrim(lines), ''))));
t = strjoin(lines, sprintf('\n'));
end

function out = terne(c, a, b)
if c; out = a; else; out = b; end
end

function c = mkCheck(name, passed, detail)
c = struct('name', name, 'passed', passed, 'detail', detail);
end
