function report = diagnose_pnas2017_aa_a3b_closure(config_path)
%DIAGNOSE_PNAS2017_AA_A3B_CLOSURE  Investigation helper for the A3b smoke
%closure-feasibility failure (INVESTIGATION CODE, not a production path).
%Segmented integration through the failure era at the registered
%tolerances; at every output point the warm-started closure state is
%recorded (per-pool occupancy vs FULL, residual, feasibility margin, free
%carriers) and the lowest quasi-steady complexes are named.

scripts_dir = fileparts(mfilename('fullpath'));
addpath(scripts_dir);
model_dir = fullfile(scripts_dir, '..', 'models', 'pnas2017_full_reference', ...
    'original', 'simulate', 'Simulate_fMGG_synthesis');
addpath(model_dir);

cfg = jsondecode(fileread(config_path));
C = a3b_build_coords(reshape(fMGG_synthesis('states'), 1, []), cfg.artifact_dir);
pt = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_parameters.csv'));
params = pt.Value;
it = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_initial_values.csv'));
x0 = it.Value;
X = read_traj(cfg.full_csv);

poolInfo.pool = {'MetRS', 'GlyRS'};
for p = 1:2
    pnm = poolInfo.pool{p};
    idxp = find(startsWith(C.names, [pnm '_']) & ~endsWith(C.names, '_degraded'));
    poolInfo.E{p} = sort(idxp(ismember(idxp, C.elimIdx)));
    poolInfo.K{p} = sort(idxp(~ismember(idxp, C.elimIdx)));
    poolInfo.ePool(p) = x0(strcmp(C.names, pnm)) + sum(x0(idxp));
end

y0 = zeros(C.Ny, 1);
y0(C.keepPos) = x0(C.keepIdx);
for k = 1:C.nLedger
    L = C.ledger(k);
    y0(L.pos) = sum(L.weights .* x0(L.members));
end
[q0, ires, gscale, ~] = a3b_init_closure(C, cfg.grid(1), y0, params, poolInfo);
fprintf('init: res %.3e (scaled %.3e), gscale %.3e\n', ires, ires / gscale, gscale);

segs = unique([logspace(log10(cfg.grid(1)), 0.5, 160), 2.4]);
if isfield(cfg, 'diag_edges')
    edges = cfg.diag_edges;
else
    edges = [cfg.grid(1), 0.05, 0.5, 1.5, 2.3, 2.45, 3.0];
end
NC = 0; A = zeros(0, 968); used_rows = zeros(1, 0);
opt = odeset('RelTol', cfg.reltol, 'AbsTol', cfg.abstol);
failed = false; fail_msg = '';
tv = []; yv = [];
tcur = cfg.grid(1); ycur = y0; qcur = q0;
for sI = 1:numel(edges)-1
    if tcur >= edges(end) || failed, break, end
    if edges(sI+1) <= tcur, continue, end
    tout = segs(segs > tcur & segs <= edges(sI+1));
    if isempty(tout), continue, end
    tseg = tic;
    seedI = struct('q', qcur, 'J', [], 'hasJ', false);
    segStats = containers.Map('KeyType', 'char', 'ValueType', 'any');
    segStats('s') = struct('calls', 0, 'iters', 0, 'max_res', 0, ...
        'max_res_scaled', 0, 'min_q', inf, 'iters_all', [], ...
        'ls_rejections', 0, 'jacobian_refreshes', 0, 'plateau_accepts', 0);
    steps = zeros(0, 2);
    outfcn = @(t, y, flag) record_step(t, steps, flag);
    odefun = @(tt, yy) a3b_rhs(tt, yy, C, params, NC, used_rows, A, seedI, ...
        segStats, gscale);
    optI = odeset(opt, 'OutputFcn', outfcn);
    try
        [tvI, yvI] = ode15s(odefun, tout, [ycur; zeros(0, 1)], optI);
        if size(yvI, 1) == numel(tvI) && size(yvI, 2) == C.Ny
            yvI = yvI';
        end
        tv = [tv; tvI(:)]; %#ok<AGROW>
        yv = [yv, yvI]; %#ok<AGROW>
        ycur = yvI(:, end); tcur = tvI(end);
        seedJ = struct('q', qcur, 'J', [], 'hasJ', false);
        [qcur, ~] = a3b_solve_closure(C, tcur, ycur, qcur, params, gscale, seedJ);
        fprintf('segment [%.4g, %.4g] done in %.1f s wall\n', ...
            edges(sI), tcur, toc(tseg));
    catch e
        failed = true;
        fail_msg = regexprep(getReport(e, 'basic'), '\s+', ' ');
        fid2 = fopen(fullfile(scripts_dir, '..', 'scratch', 'a3bc', 'runs', ...
            'diag_error.txt'), 'w');
        fwrite(fid2, getReport(e, 'extended'), 'char'); fclose(fid2);
    end
end

fprintf('\n=== A3b closure diagnosis ===\n');
fprintf('integration outcome: %s\n', ...
    tern2(failed, fail_msg, 'completed without closure loss'));
fprintf('%-10s %-10s %-10s %-10s %-10s %-10s %-10s %-10s\n', ...
    't', 'max|G|sc', 'min_q', 'occ_MetRS', 'occ_GlyRS', ...
    'free_tRNAf', 'free_tRNAGly', 'free_GlyRS');
rows = {};
seed = struct('q', q0, 'J', [], 'hasJ', false);
for i = 1:numel(tv)
    t = tv(i); y = yv(1:C.Ny, i);
    q = seed.q; res = NaN;
    try
        [q, res] = a3b_solve_closure(C, t, y, seed.q, params, gscale, seed);
    catch e
        fprintf('closure solve failed at output t=%.4g: %s\n', t, ...
            regexprep(e.message, '\s+', ' '));
    end
    seed.q = q;
    x = a3b_reconstruct(C, y, q);
    r = snap(t, q, x, C, X, res, gscale);
    rows{end+1} = r; %#ok<AGROW>
    fprintf('%-10.4g %-10.3e %-10.3e %-10.4g %-10.4g %-10.4g %-10.4g %-10.4g\n', ...
        r.t, r.res_scaled, r.min_q, r.occM, r.occG, r.ftF, r.ftG, r.fGlyRS);
end
if ~isempty(rows)
    r = rows{end};
    [~, order] = sort(r.q, 'ascend');
    fprintf('\nlowest quasi-steady complexes at the last checkpoint (t=%.4g):\n', r.t);
    for k = 1:min(8, numel(order))
        fprintf('  %-32s q=%.4e  (FULL occ %.4e)\n', ...
            C.elimNames{order(k)}, r.q(order(k)), r.qfull(order(k)));
    end
end
report = struct('rows', {rows}, 'failed', failed, 'fail_msg', fail_msg);
end

% ------------------------------------------------------------------
function r = snap(t, q, x, C, X, res, gscale)
    tF = X(1, :); nsp = X(2:end, :);   % X rows: time + 241 species
    isG = startsWith(C.elimNames, 'GlyRS');
    qfull = interp1(tF', nsp(C.elimIdx, :)', t, 'linear', 'extrap')';
    r = struct('t', t, 'res_scaled', res / gscale, 'min_q', min(q), ...
        'occM', sum(q(~isG)), 'occG', sum(q(isG)), ...
        'ftF', x(strcmp(C.names, 'tRNAfMetCAU')), ...
        'ftG', x(strcmp(C.names, 'tRNAGlyGCC')), ...
        'fGlyRS', x(strcmp(C.names, 'GlyRS')), ...
        'q', q, 'qfull', qfull);
end

function X = read_traj(p)
    fid = fopen(p, 'r');
    assert(fid ~= -1, 'trajectory not found: %s', p);
    hdr = strsplit(strtrim(fgetl(fid)), ',');
    C = textscan(fid, repmat('%f', 1, numel(hdr)), 'Delimiter', ',');
    fclose(fid);
    M = cell2mat(C);
    X = M(:, 1:242)';        % rows = time + 241 species, cols = time points
end

function o = tern2(c, a, b)
    if c, o = a; else, o = b; end
end

function status = record_step(t, steps, flag)
    persistent last_t last_n
    if isempty(last_t), last_t = -inf; last_n = 0; end
    if strcmp(flag, 'done')
        last_t = -inf;
        status = 0;
        return
    end
    if numel(t) >= 1 && isfinite(t(end))
        if last_n > 0
            h = t(end) - last_t;
            fid = fopen('C:/Users/sean/Desktop/GUV-PURE/scratch/a3bc/runs/steps.txt', 'a');
            fprintf(fid, '%.6g %.6g\n', t(end), h);
            fclose(fid);
        end
        last_t = t(end); last_n = last_n + 1;
    end
    status = 0;
end
