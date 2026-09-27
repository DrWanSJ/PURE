function out = run_pnas2017_aa_v1_formal(config_path)
%RUN_PNAS2017_AA_V1_FORMAL  Formal full-network reference / reduced runs
% for the PNAS 2017 aminoacylation A3a validation (v1).
%
% reference mode: the AUTHOR's own RHS (fMGG_synthesis.m, unmodified)
% integrates all 241 species plus the cumulative extents.
%
% reduced mode: the registered eliminated complexes satisfy the A3a
% closure exactly, 0 = dC_i/dt(x) with the rows taken from the AUTHOR's
% RHS, and are tracked as roots of that algebraic system at every solver
% evaluation (expensive per-evaluation constraint elimination). The two
% FREE ENZYMES are not integrated: each is reconstructed at every
% evaluation from its conserved moiety, free = ePool - sum(kept) -
% sum(eliminated) (A2 "exact free-enzyme reconstruction"; acceptance T_G
% requires every enzyme family total conserved to 1e-8 in every run). The
% remaining 218 species evolve under the author RHS. Pool conservation is
% then exact by construction (free + kept + eliminated == ePool), which is
% the same reconstruction the registered partition-verification closure and
% consistentStart use; integrating the free enzyme instead was measured
% 2026-09-25 to leak ~99% of each pool by t = 1000 s (T_G residual ~0.99),
% because QSSA pins the eliminated rows to zero so enzyme held in those
% complexes never returns to the free pool as substrates drain.
% This is the same index-1 DAE as the singular-mass-matrix formulation. The
% mass-matrix harness was retired on 2026-09-25 after direct
% measurement: with 'MassSingular','yes' at the registered
% reltol/abstol = 1e-10/1e-14 the ode15s corrector reaches a
% step-size-independent error-test plateau of 1.67*rtol on the algebraic
% rows with small Jacobian diagonals (GlyRS_ATP, GlyRS_Gly). Cause: the
% author RHS sums terms up to ~3e6 uM/s, so each eliminated row carries
% ~1e-9 uM/s of double cancellation noise, and the implied root jitter
% noise/|J_ii| exceeds rtol*|C_i| ~ 1e-13. R2025b ode15s has no
% algebraic-state option ('MStates' does not exist), so the DAE form is
% numerically unattainable at the registered tolerances; elimination
% removes the jittered roots from the error vector without changing the
% mathematics.
%
% The reduced initial condition is computed by the registered damped
% projected Newton (consistentStart, free enzyme reconstructed from pool
% conservation, feasibility projected). The displacement from the author
% ICs IS the initial-layer jump: recorded in the output struct and
% printed, never suppressed.
%
% Cumulative reaction extents are augmented dynamic states
%   dxi_j/dt = sign * v_j(x),   v = pnas2017_aa_v1_rates(x, param)
% where the rate expressions are a VERBATIM line-by-line extract of the
% author file's own react(1:968) monomial block (generated and verified by
% scripts/generate_pnas2017_aa_v1_rates.py).
%
% config JSON fields:
%   mode            "reference" (no algebraic rows) or "reduced"
%   eliminated      array of species names made algebraic (reduced only)
%   reltol abstol   solver tolerances
%   grid            [start end n] log-spaced output grid
%   x0_scale        optional {species: multiplier} applied to initial values
%   outfile         CSV path for the trajectory
%   cumdefs         array of {id, reactions: [{rid, sign}]} cumulative extents
%   stats           optional true -> print solver statistics

model_dir = fullfile(fileparts(mfilename('fullpath')), '..', ...
    'models', 'pnas2017_full_reference', 'original', 'simulate', 'Simulate_fMGG_synthesis');
scripts_dir = fileparts(mfilename('fullpath'));
addpath(model_dir); addpath(scripts_dir);

cfg = jsondecode(fileread(config_path));

pt = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_parameters.csv'));
params = pt.Value;
it = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_initial_values.csv'));
x0 = it.Value;
names = reshape(fMGG_synthesis('states'), 1, []);
NS = numel(names);
assert(numel(x0) == NS, 'initial-value count mismatch');
assert(numel(params) == 969, 'parameter count mismatch');

% verify the generated rates function is ordered identically to
% fMGG_synthesis('parameters') (react(i) <-> re...i_k1)
pn = fMGG_synthesis('parameters');
assert(strcmp(pn{1}, 're0000000001_k1') && strcmp(pn{968}, 're0000000968_k1'));

if isfield(cfg, 'x0_scale') && ~isempty(cfg.x0_scale)
    fnames = fieldnames(cfg.x0_scale);
    for k = 1:numel(fnames)
        j = find(strcmp(names, fnames{k}), 1);
        assert(~isempty(j), 'unknown species %s in x0_scale', fnames{k});
        x0(j) = x0(j) * cfg.x0_scale.(fnames{k});
    end
end

tgrid = logspace(log10(cfg.grid(1)), log10(cfg.grid(2)), cfg.grid(3));

elim = [];
if strcmp(cfg.mode, 'reduced')
    assert(isfield(cfg, 'eliminated') && numel(cfg.eliminated) > 0, ...
        'reduced mode needs eliminated species');
    for k = 1:numel(cfg.eliminated)
        j = find(strcmp(names, cfg.eliminated{k}), 1);
        assert(~isempty(j), 'unknown eliminated species %s', cfg.eliminated{k});
        elim(end+1) = j; %#ok<AGROW>
    end
else
    assert(strcmp(cfg.mode, 'reference'), 'unknown mode %s', cfg.mode);
end

NC = 0;
if isfield(cfg, 'cumdefs'), NC = numel(cfg.cumdefs); end
% map each cumulative definition onto react-vector rows: A(k, react_index)
A = zeros(NC, 968);
for k = 1:NC
    terms = cfg.cumdefs(k).reactions;
    for m = 1:numel(terms)
        rid = terms(m).rid;
        ridx = str2double(rid(3:end));          % re0000000013 -> 13
        assert(ridx >= 1 && ridx <= 968, 'bad reaction id %s', rid);
        A(k, ridx) = A(k, ridx) + terms(m).sign;
    end
end
used_rows = find(any(A ~= 0, 1));

% Enzyme-pool moiety constraints (A2 "exact free-enzyme reconstruction";
% acceptance T_G requires every enzyme family total conserved to 1e-8 in
% every formal run). The free enzyme of each pool is therefore NOT an
% independent dynamic state: it is reconstructed at every RHS evaluation
% from the conserved moiety, free = ePool - sum(kept) - sum(eliminated),
% exactly as the registered partition-verification closure and
% consistentStart already do. ePool is a conserved moiety of the author RHS
% (the full reference holds each pool to ~1e-10 over t <= 1000 s). Keeping
% the free enzyme dynamic instead was measured 2026-09-25 to leak ~99% of
% each pool by t = 1000 s (T_G residual ~0.99): QSSA pins the eliminated
% rows to zero, so the enzyme held in those complexes never returns to the
% free pool as substrates drain.
poolEnz = {'MetRS', 'GlyRS'};
freeIdx = zeros(numel(poolEnz), 1);
for p = 1:numel(poolEnz)
    jf = find(strcmp(names, poolEnz{p}), 1);
    assert(~isempty(jf), 'enzyme %s is not a state', poolEnz{p});
    freeIdx(p) = jf;
end
if strcmp(cfg.mode, 'reduced')
    dyn = setdiff((1:NS)', union(elim(:), freeIdx));
else
    dyn = (1:NS)';   % reference mode integrates every species (residual_full)
end
Ndyn = numel(dyn);

opt = odeset('RelTol', cfg.reltol, 'AbsTol', cfg.abstol);
if isfield(cfg, 'stats') && cfg.stats
    opt = odeset(opt, 'Stats', 'on');
end

stat_text = '';
want_stats = isfield(cfg, 'stats') && cfg.stats;

if strcmp(cfg.mode, 'reduced')
    % Consistent initial condition: solve the algebraic rows
    % 0 = dx_i/dt(x) for the eliminated complexes with the free enzyme
    % reconstructed from pool conservation, via the registered damped
    % projected Newton (identical computation dfinit would perform for a
    % non-degenerate FD Jacobian; R2025b daeic12 itself collapses to an
    % all-zero algebraic Jacobian for the author's zero-valued complex
    % ICs - see certificate docs). The displacement from the author ICs is
    % the initial-layer jump: recorded and printed, never suppressed.
    yaug0 = [x0(:); zeros(NC, 1)];
    [ycons, ic_jump] = consistentStart(yaug0, tgrid(1), params, ...
        NS, NC, A, used_rows, elim, names);
    xcons = ycons(1:NS);
    [maxjump, jmax] = max(abs(xcons - x0(:)));
    fprintf('largest initial-condition adjustment: %s: %.6g -> %.6g (%.3g)\n', ...
        names{jmax}, x0(jmax), xcons(jmax), maxjump);

    % per-pool rootfind cache, seeded at the consistent branch. The cache
    % is passed BY VALUE into the RHS and never written back, so every
    % evaluation warm-starts Newton from this same fixed seed: odefun(t,y)
    % stays a deterministic function of (t,y), which ode15s requires for a
    % consistent numerical Jacobian. (Persisting the cache across calls was
    % measured 2026-09-25 to make the RHS path-dependent: 9.9e6 function
    % evaluations and 1.05e5 rejected steps vs 1.7e5 / 1.9e3 here, ~15x
    % slower.) Only the statistics accumulate, via a handle Map that does
    % not feed back into r.
    cache0 = initBlockCache(xcons, elim, names, x0, tgrid(1), params);
    statsH = containers.Map('KeyType', 'char', 'ValueType', 'any');
    statsH('s') = newBlockStats();
    odefun = @(t, y) residual_red(t, y, params, NS, NC, A, used_rows, dyn, ...
        cache0, statsH);
    z0 = [xcons(dyn); ycons(NS+1:end)];
    if want_stats
        diary([cfg.outfile '.stats.raw.txt']);
    end
    [tv, yv] = ode15s(odefun, tgrid, z0, opt);
    if want_stats
        diary off;
        stat_text = fileread([cfg.outfile '.stats.raw.txt']);
    end
    solver_stats = parseSolverStats(stat_text);
    % R2025b orientation: rows = output times, columns = states
    if size(yv, 1) == numel(tv) && size(yv, 2) == Ndyn + NC
        yv = yv';
    end
    % reconstruct the eliminated complexes at every output time by
    % advancing a fresh rootfind warm-started along the output grid
    cache = cache0;
    yv_full = zeros(NS + NC, numel(tv));
    for i = 1:numel(tv)
        x = zeros(NS, 1);
        x(dyn) = yv(1:Ndyn, i);
        for p = 1:numel(cache)
            [cache{p}, r] = solveBlock(cache{p}, tv(i), x, params);
            if r > 1e-10 * cache{p}.refscale
                error(['closure-lost at t=%.3e pool %s: max|g| = %.3e ' ...
                       '(scaled %.3e > registered 1e-10)'], tv(i), ...
                    cache{p}.enz, r, r / max(cache{p}.refscale, 1e-300));
            end
            x(cache{p}.E) = cache{p}.C;
            x(cache{p}.jf) = cache{p}.ePool - sum(x(cache{p}.K)) ...
                - sum(cache{p}.C);
        end
        yv_full(1:NS, i) = x;
        yv_full(NS+1:end, i) = yv(Ndyn+1:end, i);
    end
    alg_stats = statsH('s');
    fprintf(['algebraic rootfind: %d block-solves, %d Newton iters ', ...
             '(median %g, max %g per call), %d line-search rejections, ', ...
             '%d Jacobian refreshes, %d plateau accepts, ', ...
             'max|G| = %.3e uM/s (scaled %.3e), min reconstructed C = %.3e\n'], ...
        alg_stats.calls, alg_stats.iters, ...
        median(alg_stats.iters_all), max(alg_stats.iters_all), ...
        alg_stats.ls_rejections, alg_stats.jacobian_refreshes, ...
        alg_stats.plateau_accepts, alg_stats.max_res, ...
        alg_stats.max_res_scaled, alg_stats.min_C);
else
    ic_jump = [];
    alg_stats = newBlockStats();
    y0 = [x0(:); zeros(NC, 1)];
    odefun = @(t, y) residual_full(t, y, params, NS, NC, A, used_rows);
    if want_stats
        diary([cfg.outfile '.stats.raw.txt']);
    end
    [tv, yv] = ode15s(odefun, tgrid, y0, opt);
    if want_stats
        diary off;
        stat_text = fileread([cfg.outfile '.stats.raw.txt']);
    end
    solver_stats = parseSolverStats(stat_text);
    % R2025b orientation: rows = output times, columns = states
    if size(yv, 1) == numel(tv) && size(yv, 2) == NS + NC
        yv = yv';
    end
end

if strcmp(cfg.mode, 'reduced')
    Yout = yv_full;
else
    Yout = yv;
end

% first output state; for reduced runs the distance to the author ICs is
% the layer jump carried by the consistent start
x_start = Yout(1:NS, 1);

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

% also write the captured solver statistics next to the trajectory
if want_stats
    fid = fopen([cfg.outfile '.stats.txt'], 'w');
    fprintf(fid, '%s', stat_text);
    fclose(fid);
end

out = struct('mode', cfg.mode, 'outfile', cfg.outfile, ...
    'n_points', numel(tv), 'n_states', NS, 'n_cum', NC, ...
    'n_eliminated', numel(elim), ...
    't_end', tv(end), ...
    'initial_layer_jump', x_start - x0, ...
    'ic_newton_jump', ic_jump, ...
    'algebraic_stats', alg_stats, ...
    'solver_stats', solver_stats, ...
    'state_names', {names});
fprintf('done %s -> %s (%d pts, %d eliminated, %d cumulative)\n', ...
    cfg.mode, cfg.outfile, numel(tv), numel(elim), NC);
end

function r = residual_full(t, y, params, NS, NC, A, used_rows)
    x = y(1:NS);
    dx = fMGG_synthesis(t, x, params);
    r = dx;
    if NC > 0
        v = pnas2017_aa_v1_rates(x, params);
        r(NS+1:NS+NC) = (A(:, used_rows) * v(used_rows))';
    end
end

function r = residual_red(t, y, params, NS, NC, A, used_rows, dyn, cache0, statsH)
% reduced-mode RHS: track the eliminated complexes on the closure
% manifold, then return author-RHS derivatives of the dynamic species
% plus the cumulative-extent rows. No clipping: an infeasible or
% non-converging root terminates the run as a failure.
%
% cache is a LOCAL copy of the fixed seed cache0 and is never written
% back, so odefun(t,y) is a deterministic function of (t,y) (ode15s needs
% this for a consistent numerical Jacobian). Only statsH (a handle Map)
% accumulates across calls; it does not influence r.
    x = zeros(NS, 1);
    x(dyn) = y(1:numel(dyn));
    cache = cache0;
    st = statsH('s');
    for p = 1:numel(cache)
        [cache{p}, res, nit, info] = solveBlock(cache{p}, t, x, params);
        st.calls = st.calls + 1;
        st.iters = st.iters + nit;
        st.iters_all(end+1) = nit; %#ok<AGROW> % per-call Newton counts
        st.ls_rejections = st.ls_rejections + info(2);
        st.jacobian_refreshes = st.jacobian_refreshes + info(3);
        st.plateau_accepts = st.plateau_accepts + info(4);
        st.max_res = max(st.max_res, res);
        st.max_res_scaled = max(st.max_res_scaled, ...
            res / max(cache{p}.refscale, 1e-300));
        st.min_C = min(st.min_C, min(cache{p}.C));
        if res > 1e-10 * cache{p}.refscale
            error(['closure-lost at t=%.3e pool %s: max|g| = %.3e ' ...
                   '(scaled %.3e > registered 1e-10)'], t, cache{p}.enz, ...
                res, res / max(cache{p}.refscale, 1e-300));
        end
        x(cache{p}.E) = cache{p}.C;
        x(cache{p}.jf) = cache{p}.ePool - sum(x(cache{p}.K)) ...
            - sum(cache{p}.C);   % moiety reconstruction (A2 / T_G)
    end
    statsH('s') = st;   %#ok<NASGU> % handle accumulation; does not affect r
    dx = fMGG_synthesis(t, x, params);
    r = dx(dyn);
    if NC > 0
        v = pnas2017_aa_v1_rates(x, params);
        r(end+1:end+NC) = (A(:, used_rows) * v(used_rows))';
    end
end

function stats = newBlockStats()
    stats = struct('calls', 0, 'iters', 0, 'max_res', 0, ...
        'max_res_scaled', 0, 'min_C', inf, 'iters_all', [], ...
        'ls_rejections', 0, 'jacobian_refreshes', 0, 'plateau_accepts', 0);
end

function s = parseSolverStats(txt)
%PARSESOLVERSTATS  Locale-independent parse of the ode15s 'Stats' table
%(captured by diary).  The table rows have a fixed order in every locale -
%successful steps, failed attempts, function evaluations, partial
%derivatives, LU decompositions, linear-system solves - and each row BEGINS
%with its count (English: "4561 successful steps"; Chinese: "4561 个成功步骤").
%Only the first three counts are needed for the run manifest.
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

function cache = initBlockCache(xcons, elim, names, x0, t0, params)
% split the eliminated species into their enzyme pools (name prefix,
% exactly the convention of the registered partition) and seed each
% rootfind cache at the consistent-start branch values. Each cache also
% carries the pool's free-enzyme index (jf), its kept-dynamic complexes
% (K), and the conserved moiety total (ePool, from the scaled author ICs)
% so the free enzyme is reconstructed as ePool - sum(K) - sum(C) (A2/T_G).
%
% refscale is seeded with the block's PRODUCTION scale: max|dC_i/dt| of the
% author RHS at the author ICs (eliminated complexes zero, free enzyme =
% full pool), identical to consistentStart's gscale. The Newton convergence
% target is 1e-12 of this physical row scale, and the registered QSSA
% acceptance is a scaled residual <= 1e-10 of it. Seeding refscale at 1
% instead made the target 1e-12 ABSOLUTE, below the double-precision
% round-off floor of the author RHS at an already-converged root, so the
% feasibility line search could find no improving step and spuriously
% reported a root failure (observed 2026-09-25: GlyRS at t=1e-4, res
% 1.166e-12 uM/s = 9.4e-17 of the 1.245e4 uM/s production scale).
    pools = {'MetRS', 'GlyRS'};
    cache = {};
    iselim = false(numel(names), 1);
    iselim(elim) = true;
    for p = 1:numel(pools)
        jf = find(strcmp(names, pools{p}), 1);
        assert(~isempty(jf), 'enzyme %s is not a state', pools{p});
        idx = find(startsWith(names, [pools{p} '_']) & ...
                   ~endsWith(names, '_degraded'));
        E = sort(idx(iselim(idx)));
        K = sort(idx(~iselim(idx)));
        assert(~isempty(E), 'no eliminated species in pool %s', pools{p});
        c = struct();
        c.enz = pools{p};
        c.jf = jf;
        c.E = E(:);
        c.K = K(:);
        c.ePool = x0(jf) + sum(x0(idx));   % conserved enzyme moiety total
        c.C = xcons(E(:));
        c.J = [];
        c.hasJ = false;
        g0 = blockResid(c, t0, x0(:), params, zeros(numel(E), 1));
        c.refscale = max(abs(g0));
        if ~(c.refscale > 0), c.refscale = 1; end
        cache{end+1} = c; %#ok<AGROW>
    end
end

function [c, res, nit, info] = solveBlock(c, t, x, params)
%SOLVEBLOCK  damped Newton on 0 = dx_i/dt (AUTHOR RHS rows) for one
%enzyme pool's eliminated block, warm-started from the fixed seed and with
%a cached one-sided FD Jacobian that is refreshed on slow convergence.
%Deterministic and bounded (12 iterations). The row scale is c.refscale =
%the block production scale; the convergence target is 1e-12 of it and the
%registered QSSA acceptance is a scaled residual <= 1e-10 of it. Iterates
%are NEVER clipped: a step is accepted only if the residual decreases and
%the trial stays feasible (C >= -1e-14). When no feasible step reduces the
%residual it has reached the double-precision floor of the author RHS; that
%plateau is accepted as converged iff it is already within the registered
%acceptance (scaled <= 1e-10), and otherwise raises an error terminating
%the run as a genuine closure/branch failure.
%
%info = [nit, ls_rejections, jacobian_refreshes, plateau_accepts] is
%per-call statistics instrumentation only: it records which of the
%pre-existing decision branches fired and does not feed back into the
%iteration in any way.
    C = c.C;
    g = blockResid(c, t, x, params, C);
    res = max(abs(g));
    % c.refscale is the FIXED block production scale (seeded in
    % initBlockCache); the scaled residual res/refscale is the registered
    % QSSA quantity, so refscale is never inflated by a transient residual.
    tol = 1e-12 * c.refscale;
    nit = 0;
    ls_rej = 0; jref = 0; plateau = 0;
    info = [0, 0, 0, 0];
    if res <= tol
        return
    end
    refreshed = false;
    for it = 1:12
        nit = it;
        if ~c.hasJ
            n = numel(c.E);
            J = zeros(n);
            for j = 1:n
                h = 1e-7 * (abs(C(j)) + 1e-10);
                Cp = C;
                Cp(j) = Cp(j) + h;
                J(:, j) = (blockResid(c, t, x, params, Cp) - g) / h;
            end
            c.J = J;
            c.hasJ = true;
        end
        d = -c.J \ g;
        alpha = 1.0;
        accepted = false;
        while alpha >= 1e-8
            Cn = C + alpha * d;
            gn = blockResid(c, t, x, params, Cn);
            rn = max(abs(gn));
            if rn < res && all(Cn >= -1e-14)
                accepted = true;
                break
            end
            alpha = alpha * 0.5;
            ls_rej = ls_rej + 1;
        end
        if ~accepted
            if c.hasJ && ~refreshed
                c.hasJ = false;      % retry once with a fresh Jacobian
                refreshed = true;
                jref = jref + 1;
                continue
            end
            % The residual has plateaued at the double-precision floor of
            % the author RHS and no feasible step reduces it further. That
            % is a converged root, NOT a failure, provided the plateau lies
            % within the registered QSSA acceptance (scaled residual <=
            % 1e-10 of the production row scale). Above that threshold it is
            % a genuine closure/branch failure and terminates the run; no
            % clipping or projection is applied in either case.
            if res <= 1e-10 * c.refscale
                plateau = plateau + 1;
                break
            end
            error(['root failure: pool %s at t=%.3e, res = %.3e ' ...
                   '(scaled %.3e), min C = %.3e (no feasible improving ' ...
                   'step above registered acceptance)'], ...
                c.enz, t, res, res / max(c.refscale, 1e-300), min(Cn));
        end
        if rn > 0.1 * res
            c.hasJ = false;          % slow progress -> refresh J
            jref = jref + 1;
        end
        C = Cn;
        g = gn;
        res = rn;
        if res <= tol
            break
        end
    end
    c.C = C;
    info = [nit, ls_rej, jref, plateau];
end

function g = blockResid(c, t, x, params, C)
% eliminated-block rows of the AUTHOR RHS at trial complexes C, with the
% free enzyme reconstructed from the conserved moiety (A2 / T_G), matching
% the registered partition-verification closure and consistentStart. The
% kept complexes x(c.K) are dynamic states already present in x.
    xt = x;
    xt(c.E) = C(:);
    xt(c.jf) = c.ePool - sum(xt(c.K)) - sum(C(:));
    dx = fMGG_synthesis(t, xt, params);
    g = dx(c.E);
end

function [y, jump, slp, info] = consistentStart(y, t0, params, NS, NC, ...
    A, used_rows, elim, names)
%CONSISTENTSTART  Damped projected Newton on the algebraic rows only,
%multiplying out the computation dfinit would perform for a non-degenerate
%FD Jacobian.
%
%Unknowns: the eliminated complexes of each enzyme pool. For every trial
%the free enzyme is reconstructed from the pool conservation
%  free = pool - sum(eliminated) - sum(kept),
%kept complexes and all other states stay at their author values, and the
%residual rows are 0 = dC_i/dt of the AUTHOR RHS (fMGG_synthesis). The
%iteration mirrors the registered partition-verification Newton (scripts/
%analyze_pnas2017_aminoacylation_reduction_v1_partition.py): multi-start,
%central FD columns with step 1e-7*(|C_j|+1e-10), damped feasibility line
%search, scaled-residual acceptance 1e-10 * production scale.
    yorig = y;
    x = y(1:NS);
    x_author = x;
    iselim = false(NS, 1);
    iselim(elim) = true;
    pools = {'MetRS', 'GlyRS'};
    allres = 0;
    for p = 1:numel(pools)
        enz = pools{p};
        jf = find(strcmp(names, enz), 1);
        assert(~isempty(jf), 'consistentStart: enzyme %s not a state', enz);
        idx = find(startsWith(names, [enz '_']) & ...
                   ~endsWith(names, '_degraded'));
        E = idx(iselim(idx));            % algebraic unknowns of this pool
        K = idx(~iselim(idx));           % kept dynamic, frozen at author IC
        nq = numel(E);
        assert(~isempty(E) && ~isempty(K), ...
            'consistentStart: pool %s partition degenerate', enz);
        ePool = sum(x_author(idx)) + x_author(jf);
        Ksum = sum(x(K));
        eK = ePool - Ksum;                       % free + eliminated capacity
        F = @(C) algRows(t0, x, E, jf, ePool - Ksum, params, C);

        % multi-start: the registered verification used all-zero,
        % uniform-half and a reference-shape start; the reference shape is
        % not available inside the runner, so two deterministic uniform
        % starts replace it.
        starts = {zeros(nq, 1), 0.5 * eK / nq * ones(nq, 1), ...
                  0.05 * eK / nq * ones(nq, 1)}';
        sols = struct('C', {}, 'res', {}, 'gscale', {}, 'feas', {}, ...
            'conv', {}, 'iters', {});
        for s = 1:numel(starts)
            C = starts{s}(:);
            g = F(C);
            gscale = max(abs(g));     % production scale: at author ICs the
                                      % rows are pure production terms
            tol = 1e-10 * max(gscale, 1e-30);
            converged = false;
            iters = 0;
            if isfinite(gscale)
                for it = 1:200
                    iters = it;
                    J = zeros(nq);
                    for j = 1:nq
                        h = 1e-7 * (abs(C(j)) + 1e-10);
                        Cp = C; Cm = C;
                        Cp(j) = Cp(j) + h;  Cm(j) = Cm(j) - h;
                        J(:, j) = (F(Cp) - F(Cm)) / (2 * h);
                    end
                    if rcond(J) < 1e-14
                        break
                    end
                    d = -J \ g;
                    % damped step: keep C >= 0 and sum(C) <= eK (the
                    % projected feasibility of the registered Newton)
                    alpha = 1.0;
                    accepted = false;
                    while alpha > 1e-12
                        trial = max(C + alpha * d, 0);
                        ss = sum(trial);
                        if ss > eK * (1 + 1e-9)
                            trial = trial * (eK * (1 + 1e-9) / ss);
                        end
                        gt = F(trial);
                        if max(abs(gt)) < max(abs(g))
                            accepted = true;
                            break
                        end
                        alpha = alpha * 0.5;
                    end
                    if ~accepted
                        break
                    end
                    C = trial;
                    g = gt;
                    if max(abs(g)) <= tol
                        converged = true;
                        break
                    end
                end
            end
            res = max(abs(g));
            feas = all(C >= -1e-15) && sum(C) <= eK * (1 + 1e-9);
            sols(end+1) = struct('C', {C}, 'res', res, 'gscale', gscale, ...
                'feas', feas, 'conv', converged, 'iters', iters); %#ok<AGROW>
        end

        ok = sols([sols.feas] & [sols.conv]);
        assert(~isempty(ok), ...
            ['consistentStart: no start converged feasibly for pool %s ' ...
             '(residuals %s uM/s). Refusing to proceed.'], enz, ...
            strjoin(cellfun(@(v) sprintf('%.2e', v), num2cell([sols.res]), ...
                'UniformOutput', false), ', '));
        % registered start-agreement discipline: feasible converged starts
        % must reach the same branch, else the run is refused
        if numel(ok) >= 2
            spread = 0;
            for a = 1:numel(ok)
                for b = a+1:numel(ok)
                    spread = max(spread, max(abs(ok(a).C - ok(b).C)));
                end
            end
            assert(spread <= 1e-6 * max(ePool, 1e-30), ...
                ['consistentStart: starts disagree for pool %s ' ...
                 '(spread %.2e uM). Refusing to proceed.'], enz, spread);
        end
        % prefer the all-zero start (smallest displacement from the author ICs)
        if sols(1).feas && sols(1).conv
            cs = sols(1);
        else
            [~, k] = min([ok.res]);
            cs = ok(k);
        end
        x(E) = cs.C;
        x(jf) = ePool - Ksum - sum(cs.C);
        allres = max(allres, cs.res);
        fprintf(['consistent-start %s: n=%d, max|g| = %.3e uM/s ', ...
                 '(%.3e of production scale %.3e), iters = %d\n'], ...
            enz, nq, cs.res, cs.res / max(cs.gscale, 1e-300), cs.gscale, ...
            cs.iters);
    end

    y = [x; yorig(NS+1:end)];
    jump = y - yorig;
    % the full-state RHS at the consistent point (dynamic rows nonzero,
    % algebraic rows at the Newton residual): reported for the record.
    slp = residual_full(t0, y, params, NS, NC, A, used_rows);
    info = struct('status', 'ok', 'res', allres);
end

function g = algRows(t0, xbase, E, jf, freeCap, params, C)
%ALGROWS  eliminated-block rows of the AUTHOR RHS at a trial complex
%vector C, with the free enzyme reconstructed from pool conservation.
    xt = xbase;
    xt(E) = C(:);
    xt(jf) = freeCap - sum(C(:));
    dx = fMGG_synthesis(t0, xt, params);
    g = dx(E);
end
