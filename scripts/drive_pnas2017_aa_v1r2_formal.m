function created = drive_pnas2017_aa_v1r2_formal(runid)
%DRIVE_PNAS2017_AA_V1R2_FORMAL  Execute the registered v1r2 formal runs.
%
%Drives scripts/run_pnas2017_aa_v1_formal.m over the registered v1r2 run
%configs (run_registry_v1r2.json), one pass, in registry order.  The FULL-S0..S5
%reference runs are REUSED byte-for-byte from the v1r1 formal cycle (the freeze
%asserted config identity) and are skipped here.  Per-run output
%is captured with evalc (command-window text, including the ode15s Stats
%table whose rows begin with their counts in every locale) and written to
%logs/<RUNID>.log.txt together with a machine-readable
%  RUNSTATS {"run_id":...,"outcome":...,...}
%line for the manifest builder.  A run whose log already ends with a
%RUNSTATS line is NOT re-executed (one formal pass per registered run;
%recorded failures are preserved, never re-run).  A run killed before it
%recorded any outcome (e.g. a session timeout) has no RUNSTATS line and is
%executed when the driver is re-invoked.
%
%created = drive_pnas2017_aa_v1r2_formal()        % all remaining runs
%created = drive_pnas2017_aa_v1r2_formal('RED-S3') % a single registered run
%
%This driver changes no numerics: it is the registered executor loop.

ROOT = fileparts(fileparts(mfilename('fullpath')));
FORMAL = fullfile(ROOT, 'results', 'pnas2017_reference', '2026-09-26_aa_v1r2_formal');
LOGS = fullfile(FORMAL, 'logs');
if ~exist(LOGS, 'dir'), mkdir(LOGS); end
regfile = fullfile(ROOT, 'docs', 'audit', 'pnas2017_aminoacylation_reduction_v1', ...
    'run_registry_v1r2.json');
raw = fileread(regfile);
reg = jsondecode(raw);
if isstruct(reg.runs) && numel(reg.runs) > 1
    % jsondecode collapses the 13 homogeneous per-run objects into a struct
    % array; rebuild the named struct, preserving JSON object order
    toks = regexp(raw, '"(FULL-S\d|RED-v1r2-S\d|RED-v1r2-NEG1)"\s*:\s*\{', 'tokens');
    ids = [toks{:}];
    assert(numel(ids) == numel(reg.runs), ...
        'registry run-id recovery failed (%d ids vs %d runs)', ...
        numel(ids), numel(reg.runs));
    runs = struct();
    for k = 1:numel(ids)
        runs.(ids{k}) = reg.runs(k);
    end
    reg.runs = runs;
end
runids = fieldnames(reg.runs);
% jsondecode mangles JSON object keys into valid identifiers: "FULL-S0"
% becomes "FULL_S0".  Map both ways; logs/manifests use the REGISTRY ids.
regid = @(f) strrep(f, '_', '-');
if nargin >= 1 && ~isempty(runid)
    assert(any(strcmp(runids, strrep(runid, '-', '_'))), ...
        'unknown run id %s', runid);
    runids = {strrep(runid, '-', '_')};
end
mlver = ['MATLAB ' version];
created = {};
for k = 1:numel(runids)
    fld = runids{k};
    rid = regid(fld);
    rr = reg.runs.(fld);
    if isfield(rr, 'status') && contains(char(rr.status), 'reused_from_v1r1')
        fprintf('skip %s (FULL reference reused byte-for-byte from v1r1)\n', rid);
        continue
    end
    logpath = fullfile(LOGS, [rid '.log.txt']);
    if exist(logpath, 'file')
        prev = fileread(logpath);
        if contains(prev, 'RUNSTATS ')
            fprintf('skip %s (outcome already recorded)\n', rid);
            continue
        end
    end
    cfgpath = fullfile(ROOT, strrep(rr.config, '/', filesep));
    fprintf('=== formal run %s ===\n', rid);
    t0 = tic;
    try
        txt = evalc(sprintf('out = run_pnas2017_aa_v1_formal(''%s'');', cfgpath));
        wall = toc(t0);
        rec = parseRunText(txt, rid, cfgpath, mlver, wall, 'success');
        rec.trajectory_sha256 = fileSha(fullfile(ROOT, ...
            strrep(rr.trajectory, '/', filesep)));
    catch ME
        wall = toc(t0);
        txt = sprintf('RUN ERROR: %s\n', ME.message);
        if ~isempty(ME.stack)
            txt = [txt sprintf('  at %s line %d\n', ME.stack(1).name, ME.stack(1).line)];
        end
        rec = parseRunText('', rid, cfgpath, mlver, wall, 'failed');
        rec.error = ME.message;
    end
    fid = fopen(logpath, 'w');
    assert(fid ~= -1, 'cannot write %s', logpath);
    fprintf(fid, '%s', txt);
    fprintf(fid, '\nRUNSTATS %s\n', jsonencode(rec));
    fclose(fid);
    created{end+1} = rid; %#ok<AGROW>
    fprintf('recorded %s: outcome=%s wall=%.1f s\n', rid, rec.outcome, rec.wall_time_s);
end
fprintf('driver done: %d runs executed this invocation\n', numel(created));
end

function rec = parseRunText(txt, rid, cfgpath, mlver, wall, outcome)
% parse the runner's printed lines (locale-independent fields)
    rec = struct();
    rec.run_id = rid;
    rec.outcome = outcome;
    rec.config_sha256 = fileSha(cfgpath);
    rec.matlab_version = mlver;
    rec.solver = 'ode15s';
    rec.wall_time_s = wall;
    rec.active_partition_revision = 'v1r1';
    rec.initialization_revision = 'v1r2';
    % solver tolerances / output grid are recorded by the manifest builder
    % from the hash-verified config JSON itself
    % ode15s stats table: leading integer of each row, fixed row order
    toks = regexp(txt, '(?m)^\s*(\d+)\s', 'tokens');
    nums = cellfun(@(c) str2double(c{1}), toks);
    if numel(nums) >= 3
        rec.solver_steps_successful = nums(1);
        rec.solver_steps_failed = nums(2);
        rec.solver_rhs_evaluations = nums(3);
    end
    m = regexp(txt, 'largest initial-condition adjustment: (\S+): (\S+) -> (\S+) \((\S+)\)', 'tokens');
    if ~isempty(m)
        t = m{1};
        rec.initial_layer_max_species = t{1};
        rec.initial_layer_max_from = str2double(t{2});
        rec.initial_layer_max_to = str2double(t{3});
        rec.initial_layer_max_abs = str2double(t{4});
    end
    m = regexp(txt, 'consistent-start (\w+): n=(\d+), max\|g\| = (\S+) uM/s \((\S+) of production scale (\S+)\), iters = (\d+)', 'tokens');
    for i = 1:numel(m)
        t = m{i};
        rec.(['consistent_start_' lower(t{1})]) = struct( ...
            'n_algebraic', str2double(t{2}), 'max_residual', str2double(t{3}), ...
            'scaled_residual', str2double(t{4}), 'production_scale', str2double(t{5}), ...
            'newton_iters', str2double(t{6}));
    end
    m = regexp(txt, ['consistent-start-v1r2 joint: max\|g\| = (\S+) uM/s \((\S+) of ' ...
        'production scale (\S+)\), iters = (\d+), debited pools: (.+)'], 'tokens');
    if ~isempty(m)
        t = m{1};
        rec.consistent_start_v1r2_joint = struct( ...
            'max_residual', str2double(t{1}), 'scaled_residual', str2double(t{2}), ...
            'production_scale', str2double(t{3}), 'newton_iters', str2double(t{4}), ...
            'debited_pools', strtrim(t{5}));
    end
    m = regexp(txt, 'cumulative-extent offsets seeded \(P2 fast layer\): (.+)', 'tokens');
    if ~isempty(m)
        rec.p2_extent_offsets = strtrim(m{1}{1});
    end
    rec.initializer = 'v1r2';
    m = regexp(txt, ['algebraic rootfind: (\d+) block-solves, (\d+) Newton iters ' ...
        '\(median (\S+), max (\S+) per call\), (\d+) line-search rejections, ' ...
        '(\d+) Jacobian refreshes, (\d+) plateau accepts, max\|G\| = (\S+) ' ...
        'uM/s \(scaled (\S+)\), min reconstructed C = (\S+)'], 'tokens');
    if ~isempty(m)
        t = m{1};
        rec.algebraic = struct('block_solves', str2double(t{1}), ...
            'newton_iters_total', str2double(t{2}), ...
            'newton_iters_median', str2double(t{3}), ...
            'newton_iters_max', str2double(t{4}), ...
            'line_search_rejections', str2double(t{5}), ...
            'jacobian_refreshes', str2double(t{6}), ...
            'plateau_accepts', str2double(t{7}), ...
            'max_abs_residual', str2double(t{8}), ...
            'max_scaled_residual', str2double(t{9}), ...
            'min_reconstructed_concentration', str2double(t{10}));
        rec.root_failures = 0;
    elseif strcmp(outcome, 'success')
        rec.root_failures = 0;
    else
        rec.root_failures = [];   % unknown: run failed before reporting
    end
    m = regexp(txt, 'done \S+ -> (\S+) \((\d+) pts, (\d+) eliminated, (\d+) cumulative\)', 'tokens');
    if ~isempty(m)
        t = m{1};
        rec.trajectory = t{1};
        rec.output_points = str2double(t{2});
        rec.n_eliminated = str2double(t{3});
        rec.n_cumulative = str2double(t{4});
    end
end

function s = fileSha(p)
    sha = java.security.MessageDigest.getInstance('SHA-256');
    fid = fopen(p, 'rb');
    assert(fid ~= -1, 'cannot hash %s', p);
    while true
        blk = fread(fid, 65536, 'uint8=>uint8');
        if isempty(blk), break; end
        sha.update(blk);
    end
    fclose(fid);
    b = typecast(sha.digest(), 'uint8');
    s = sprintf('%02x', b);
end
