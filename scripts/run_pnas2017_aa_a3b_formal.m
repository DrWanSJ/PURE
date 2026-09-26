function out = run_pnas2017_aa_a3b_formal(config_path)
%RUN_PNAS2017_AA_A3B_FORMAL  Formal full-network reduced run for the A3b
%total-coordinate / tQSSA aminoacylation candidate (and its negative
%controls).  Reference-mode trajectories are NOT produced here: the
%registered FULL-S0..S5 runs of the v1r1 cycle are reused byte-for-byte
%after independent hash verification (see the cycle run registry).
%
%A3b realization (candidate definition in
%docs/audit/pnas2017_aminoacylation_A3b/):
%
%   SLOW coordinates y (220): 212 identity rows (every species except the
%   21 eliminated complexes and the 8 replaced free carriers) + 8 protected
%   ledger total rows (MetRS_total, GlyRS_total, tRNAfMetCAU_total,
%   tRNAGlyGCC_total, adenine_ledger_total, phosphate_ledger_total,
%   Met_material_total, Gly_material_total), each replacing the identity
%   coordinate of one free carrier (MetRS, GlyRS, tRNAfMetCAU, tRNAGlyGCC,
%   ATP, PPi, Met, Gly).
%
%   FAST coordinates q (21): the same eliminated-complex set as the
%   registered A3a partition (initial A3b attempt per Phase 6: start with
%   the previous 21-state set so the effect of changing coordinates can be
%   isolated).
%
%   T = [A; Q] has rank 241 (verified exactly and numerically,
%   protected_ledger_rowspace.json); every protected ledger lies in
%   rowspace(A) BY CONSTRUCTION (each is an A row), which removes the A3a
%   sliding-leak mechanism structurally: a changing q cannot move any
%   ledger total except through the retained interface flux rows.
%
%   Closure: 0 = G(y, q) = Q f(R(y, q)) with the AUTHOR RHS rows of the
%   eliminated complexes (the registered closure equations; the closure is
%   degree 2 in q -- NOT affine -- so the registered damped projected
%   Newton discipline is retained, see closure_structure in the rowspace
%   JSON).
%
%   Reduced flow: dy/dt = A f(R(y, q)).  Identity rows use the author RHS
%   directly; the 8 ledger rows use the exact per-reaction balances
%   (w^T S) v computed from the generated monomial rate vector (no large
%   cancellation: (w^T S) is zero on every active reaction for the five
%   exact rows, so those coordinates are identically constant; the
%   adenine / Met / Gly material rows move exactly by their documented
%   interface fluxes).  Cumulative extents are augmented states exactly as
%   in the v1r1 cycle.
%
%   Initialization (Phase 10): y0 = A x0_full exactly; q0 solves the
%   closure at y0 (multi-start, start-agreement discipline, per-pool
%   capacity projection).  Because the totals encode the FULL physical
%   inventory, the reconstruction debits the free carriers by the
%   complexes' sequestered content automatically -- no debit matrix.
%
% config JSON fields:
%   mode            "a3b_reduced" (the only mode implemented here)
%   artifact_dir    directory with the frozen A3b coordinate artifacts
%   reltol abstol   solver tolerances
%   grid            [start end n] log-spaced output grid
%   x0_scale        optional {species: multiplier} applied to initial values
%   outfile         CSV path for the trajectory
%   cumdefs         array of {id, reactions: [{rid, sign}]} cumulative extents
%   stats           optional true -> capture solver statistics
%   neg_mode        optional: "ledger" | "partition" | "root" for the
%                   Phase-13 negative controls (see cycle documentation)

model_dir = fullfile(fileparts(mfilename('fullpath')), '..', ...
    'models', 'pnas2017_full_reference', 'original', 'simulate', 'Simulate_fMGG_synthesis');
scripts_dir = fileparts(mfilename('fullpath'));
addpath(model_dir); addpath(scripts_dir);

cfg = jsondecode(fileread(config_path));
assert(strcmp(cfg.mode, 'a3b_reduced'), ...
    ['run_pnas2017_aa_a3b_formal implements a3b_reduced only; reference ' ...
     'trajectories are reused from the registered v1r1 FULL runs']);

neg = 'none';
if isfield(cfg, 'neg_mode') && ~isempty(cfg.neg_mode)
    neg = cfg.neg_mode;
end

pt = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_parameters.csv'));
params = pt.Value;
it = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_initial_values.csv'));
x0 = it.Value;
names = reshape(fMGG_synthesis('states'), 1, []);
NS = numel(names);
assert(numel(x0) == NS, 'initial-value count mismatch');
assert(numel(params) == 969, 'parameter count mismatch');

pn = fMGG_synthesis('parameters');
assert(strcmp(pn{1}, 're0000000001_k1') && strcmp(pn{968}, 're0000000968_k1'), ...
    'rates ordering mismatch');

if isfield(cfg, 'x0_scale') && ~isempty(cfg.x0_scale)
    fnames = fieldnames(cfg.x0_scale);
    for k = 1:numel(fnames)
        j = find(strcmp(names, fnames{k}), 1);
        assert(~isempty(j), 'unknown species %s in x0_scale', fnames{k});
        x0(j) = x0(j) * cfg.x0_scale.(fnames{k});
    end
end

tgrid = logspace(log10(cfg.grid(1)), log10(cfg.grid(2)), cfg.grid(3));

% ---- coordinate artifacts (frozen)
C = a3b_build_coords(names, cfg.artifact_dir);
elimIdx = C.elimIdx;

% NEG-LEDGER control (Phase 13): swap the tRNAfMetCAU total coordinate for
% the free-substrate identity coordinate (the A3a coordinate choice) so the
% anti-sliding-leak validator must reject the run.
if strcmp(neg, 'ledger')
    lt = find(strcmp({C.ledger.name}, 'tRNAfMetCAU_total'), 1);
    assert(~isempty(lt), 'tRNAfMetCAU_total ledger row not found');
    jf = C.idx('tRNAfMetCAU');
    % identity row replaces the ledger row; the carrier is no longer slaved
    C.keepIdx(end+1, 1) = jf; %#ok<AGROW>
    C.keepPos = [];
    C.keepPos = (1:numel(C.keepIdx))';
    C.ledger(lt) = [];
    C.nLedger = numel(C.ledger);
    for k = 1:C.nLedger
        C.ledger(k).pos = numel(C.keepIdx) + k;
    end
    C.Ny = numel(C.keepIdx) + C.nLedger;
    fprintf(['NEG-LEDGER control active: free tRNAfMetCAU integrated, ' ...
        'tRNAfMetCAU_total coordinate dropped (Ny = %d)\n'], C.Ny);
    % NEG-LEDGER keeps the author free-tRNA initial value (A3a semantics):
    % the eliminated complexes' tRNA content is NOT debited -- the v1r1
    % phantom-inventory initialization -- so the sliding-leak signature is
    % the A3a one.
    y0 = zeros(C.Ny, 1);
    y0(C.keepPos) = x0(C.keepIdx);
    for k = 1:C.nLedger
        L = C.ledger(k);
        y0(L.pos) = sum(L.weights .* x0(L.members));
    end
else
    % y0 = A x0_full (exact inventory transfer, Phase 10)
    y0 = zeros(C.Ny, 1);
    y0(C.keepPos) = x0(C.keepIdx);
    for k = 1:C.nLedger
        L = C.ledger(k);
        y0(L.pos) = sum(L.weights .* x0(L.members));
    end
end

% ---- enzyme pool bookkeeping (capacity projection in the initializer)
pools = {'MetRS', 'GlyRS'};
poolInfo.pool = pools;
poolInfo.E = cell(2, 1);
poolInfo.K = cell(2, 1);
poolInfo.ePool = zeros(2, 1);
for p = 1:2
    jf = find(strcmp(names, pools{p}), 1);
    idxp = find(startsWith(names, [pools{p} '_']) & ~endsWith(names, '_degraded'));
    poolInfo.E{p} = sort(idxp(ismember(idxp, elimIdx)));
    poolInfo.K{p} = sort(idxp(~ismember(idxp, elimIdx)));
    assert(numel(poolInfo.E{p}) > 0, 'no eliminated species in pool %s', pools{p});
    poolInfo.ePool(p) = x0(jf) + sum(x0(idxp));
end

% ---- cumulative extents (identical mapping to the v1r1 cycle)
NC = 0;
if isfield(cfg, 'cumdefs'), NC = numel(cfg.cumdefs); end
A = zeros(NC, 968);
for k = 1:NC
    terms = cfg.cumdefs(k).reactions;
    for m = 1:numel(terms)
        rid = terms(m).rid;
        ridx = str2double(rid(3:end));
        assert(ridx >= 1 && ridx <= 968, 'bad reaction id %s', rid);
        A(k, ridx) = A(k, ridx) + terms(m).sign;
    end
end
used_rows = find(any(A ~= 0, 1));

% ---- cumulative-extent seeds: the registered P2 fast-layer offsets
% (v1r2 layer treatment, reused per condition for like-for-like cumulative
% comparison; absent or empty = zero seeds)
xi0 = zeros(NC, 1);
if isfield(cfg, 'init_extents_offset') && ~isempty(cfg.init_extents_offset)
    xi0 = cfg.init_extents_offset(:);
    assert(numel(xi0) == NC, 'init_extents_offset length mismatch');
    fprintf('cumulative-extent offsets seeded (P2 fast layer): %s\n', ...
        strjoin(cellfun(@(k, v) sprintf('%s=%.6g', k, v), ...
        reshape({cfg.cumdefs.id}, [], 1), num2cell(xi0(:)), ...
        'UniformOutput', false), ', '));
end

% ---- consistent initial closure solve (Phase 10)
[q0, ires, gscale, iinfo] = a3b_init_closure(C, tgrid(1), y0, params, poolInfo);
xcons = a3b_reconstruct(C, y0, q0);
maxjump = 0; jmax = 0;
dj = xcons - x0(:);
[maxjump, jmax] = max(abs(dj));
fprintf('largest initial-condition adjustment: %s: %.6g -> %.6g (%.3g)\n', ...
    names{jmax}, x0(jmax), xcons(jmax), maxjump);
fprintf(['a3b consistent start: max|G| = %.3e uM/s (%.3e of production ' ...
         'scale %.3e), iters = %d, starts_ok = %d\n'], ...
    ires, ires / gscale, gscale, iinfo.iters, iinfo.starts_ok);

% Phase 10 verification: protected totals exact, nonnegativity, inventory
inv_led = cell(1, C.nLedger);
inv_full_t0 = zeros(C.nLedger, 1);
inv_red_t0 = zeros(C.nLedger, 1);
inv_absdiff = zeros(C.nLedger, 1);
for k = 1:C.nLedger
    L = C.ledger(k);
    fv = sum(L.weights .* x0(L.members));
    rv = sum(L.weights .* xcons(L.members));
    inv_led{k} = L.name;
    inv_full_t0(k, 1) = fv;
    inv_red_t0(k, 1) = rv;
    inv_absdiff(k, 1) = abs(fv - rv);
    assert(abs(fv - rv) <= 1e-8 * max(abs(fv), 1), ...
        'a3b t0 inventory mismatch on %s: %.3e', L.name, abs(fv - rv));
end
minx0 = min(xcons);
fprintf('a3b t0: min reconstructed concentration = %.3e; inventory max abs diff = %.3e\n', ...
    minx0, max(inv_absdiff));
assert(minx0 >= -1e-10, 'a3b t0 reconstructed state infeasible: min = %.3e', minx0);
assert(ires <= 1e-10 * gscale, 'a3b t0 closure residual above registered acceptance');

% ---- fixed-seed closure cache (deterministic odefun, v1r1 pattern)
seed = struct('q', q0, 'J', [], 'hasJ', false);
statsH = containers.Map('KeyType', 'char', 'ValueType', 'any');
statsH('s') = newAlgStats();
odefun = @(t, y) a3b_rhs(t, y, C, params, NC, used_rows, A, seed, ...
    statsH, gscale);

opt = odeset('RelTol', cfg.reltol, 'AbsTol', cfg.abstol);
if isfield(cfg, 'stats') && cfg.stats
    opt = odeset(opt, 'Stats', 'on');
end
stat_text = '';
if isfield(cfg, 'stats') && cfg.stats
    diary([cfg.outfile '.stats.raw.txt']);
end
z0 = [y0; xi0];
[tv, yv] = ode15s(odefun, tgrid, z0, opt);
if isfield(cfg, 'stats') && cfg.stats
    diary off;
    stat_text = fileread([cfg.outfile '.stats.raw.txt']);
end
solver_stats = parseSolverStats(stat_text);
if size(yv, 1) == numel(tv) && size(yv, 2) == C.Ny + NC
    yv = yv';
end

% ---- reconstruct eliminated complexes at every output time (warm-started
% along the output grid, exactly the v1r1 output pattern)
jcache = struct('q', q0, 'J', [], 'hasJ', false);
Yout = zeros(NS + NC, numel(tv));
twall = tic;
for i = 1:numel(tv)
    y = yv(1:C.Ny, i);
    [qc, res] = a3b_solve_closure(C, tv(i), y, jcache.q, params, gscale, jcache);
    jcache.q = qc;
    fprintf('output %d/%d at t=%.4g (wall %.1f s)\n', i, numel(tv), tv(i), toc(twall));
    if res > 1e-10 * gscale
        error(['closure-lost at output t=%.3e: max|G| = %.3e (scaled %.3e ' ...
               '> registered 1e-10)'], tv(i), res, res / gscale);
    end
    x = a3b_reconstruct(C, y, qc);
    Yout(1:NS, i) = x;
    Yout(NS+1:end, i) = yv(C.Ny+1:end, i);
end
alg = statsH('s');
fprintf(['a3b algebraic rootfind: %d solves, %d Newton iters (median %g, ' ...
         'max %g), %d line-search rejections, %d Jacobian refreshes, ' ...
         '%d plateau accepts, max|G| = %.3e uM/s (scaled %.3e), min q = %.3e\n'], ...
    alg.calls, alg.iters, median(alg.iters_all), max(alg.iters_all), ...
    alg.ls_rejections, alg.jacobian_refreshes, alg.plateau_accepts, ...
    alg.max_res, alg.max_res_scaled, alg.min_q);

% ---- trajectory output (author format: 241 species + extents)
f = fopen(cfg.outfile, 'w');
assert(f ~= -1, 'cannot open %s', cfg.outfile);
hdr = [{'time'}, names];
for k = 1:NC, hdr{end+1} = ['xi_' cfg.cumdefs(k).id]; end %#ok<AGROW>
fprintf(f, '%s\n', strjoin(hdr, ','));
for i = 1:numel(tv)
    fprintf(f, '%.17g', tv(i));
    fprintf(f, ',%.17g', Yout(:, i)');
    fprintf(f, '\n');
end
fclose(f);

if isfield(cfg, 'stats') && cfg.stats
    fid = fopen([cfg.outfile '.stats.txt'], 'w');
    fprintf(fid, '%s', stat_text);
    fclose(fid);
end

% ---- initial-state evidence artifact
fid = fopen([cfg.outfile '.initial_state.json'], 'w');
assert(fid ~= -1, 'cannot open %s.initial_state.json', cfg.outfile);
fprintf(fid, '{\n  "candidate": "A3b",\n  "neg_mode": "%s",\n  "initializer": "a3b_total_coordinate",\n  "time": %.17g,\n', ...
    neg, tgrid(1));
fprintf(fid, '  "state_names": [%s],\n', ...
    strjoin(cellfun(@(c) sprintf('"%s"', c), names, 'UniformOutput', false), ', '));
fprintf(fid, '  "state": [%s],\n', ...
    strjoin(cellfun(@(c) sprintf('%.17g', c), num2cell(xcons), 'UniformOutput', false), ', '));
fprintf(fid, '  "q0_names": [%s],\n', ...
    strjoin(cellfun(@(c) sprintf('"%s"', c), C.elimNames, 'UniformOutput', false), ', '));
fprintf(fid, '  "q0": [%s],\n', ...
    strjoin(cellfun(@(c) sprintf('%.17g', c), num2cell(q0), 'UniformOutput', false), ', '));
fprintf(fid, '  "closure_residual_abs": %.17g,\n', ires);
fprintf(fid, '  "closure_residual_scaled": %.17g,\n', ires / gscale);
fprintf(fid, '  "production_scale": %.17g,\n', gscale);
fprintf(fid, '  "init_newton_iterations": %d,\n', iinfo.iters);
fprintf(fid, '  "ledger_t0_names": [%s],\n', ...
    strjoin(cellfun(@(c) sprintf('"%s"', c), inv_led, 'UniformOutput', false), ', '));
fprintf(fid, '  "ledger_t0_full": [%s],\n', ...
    strjoin(cellfun(@(c) sprintf('%.17g', c), num2cell(inv_full_t0), 'UniformOutput', false), ', '));
fprintf(fid, '  "ledger_t0_red": [%s],\n', ...
    strjoin(cellfun(@(c) sprintf('%.17g', c), num2cell(inv_red_t0), 'UniformOutput', false), ', '));
fprintf(fid, '  "ledger_t0_absdiff": [%s],\n', ...
    strjoin(cellfun(@(c) sprintf('%.17g', c), num2cell(inv_absdiff), 'UniformOutput', false), ', '));
fprintf(fid, '  "min_reconstructed": %.17g,\n', minx0);
fprintf(fid, '  "max_ic_adjustment": %.17g\n', maxjump);
fprintf(fid, '}\n');
fclose(fid);

out = struct('mode', cfg.mode, 'candidate', 'A3b', 'neg_mode', neg, ...
    'outfile', cfg.outfile, 'n_points', numel(tv), 'n_states', NS, ...
    'n_cum', NC, 'n_eliminated', numel(elimIdx), 'Ny', C.Ny, ...
    't_end', tv(end), 'ic_newton_jump', maxjump, ...
    'closure_residual_scaled_t0', ires / gscale, ...
    'algebraic_stats', alg, 'solver_stats', solver_stats, ...
    'state_names', {names});
fprintf('done a3b_reduced -> %s (%d pts, %d eliminated, %d cumulative)\n', ...
    cfg.outfile, numel(tv), numel(elimIdx), NC);
end

function stats = newAlgStats()
    stats = struct('calls', 0, 'iters', 0, 'max_res', 0, 'max_res_scaled', 0, ...
        'min_q', inf, 'iters_all', [], 'ls_rejections', 0, ...
        'jacobian_refreshes', 0, 'plateau_accepts', 0);
end

function s = parseSolverStats(txt)
% locale-independent parse of the ode15s 'Stats' table (v1r1 convention:
% each row BEGINS with its count in every locale).
    s = struct('nsteps', NaN, 'nfailed', NaN, 'nfevals', NaN);
    if isempty(txt)
        return
    end
    toks = regexp(txt, '(?m)^\s*(\d+)\s', 'tokens');
    nums = cellfun(@(c) str2double(c{1}), toks);
    if numel(nums) >= 3
        s.nsteps = nums(1);
        s.nfailed = nums(2);
        s.nfevals = nums(3);
    end
end
