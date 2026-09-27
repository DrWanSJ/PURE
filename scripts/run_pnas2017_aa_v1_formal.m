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
% v1r2 initializer (config field "initializer" = "v1r2"; default "v1r1"
% reproduces the historical consistentStart exactly): the MOIETY-CONSISTENT
% initialization map. The 21 eliminated complexes are solved JOINTLY
% (single 21-dim Newton: the free-pool debits couple the two enzyme pools
% through free ATP and free PPi) together with the B_init inventory rows:
% every eliminated complex's substrate content is DEBITED from the free
% pool it is defensibly sourced from (free tRNAfMetCAU/tRNAGlyGCC/Met/Gly/
% ATP) and the free PPi pool is CREDITED by the PPi content already
% released from the bare-adenylate eliminated complexes. The debit
% coefficients are read from the config field init_debits (frozen, derived
% mechanically in binit_v1r2.json). Free AMP is NOT adjustable (kept
% dynamic state, author initial value 0; the registered additional
% condition delta_AMP = 0). Both models then start from identical
% physical inventories (acceptance initial_conditions_rule) with the
% closure satisfied to the registered tolerance.
%
% Cumulative-extent offsets: config field init_extents_offset (array of NC
% values, from the registered P2 fast-layer diagnostic per stress
% condition) seeds the augmented extent states so the reduced cumulative
% counters include the reaction extents the omitted initial layer already
% performed (acceptance initial_layer_rules / Phase 6). Absent or empty =
% zero seeds (historical behaviour).
%
% v1r3 realization (config field "reconstructed_ledgers"; requires
% initializer "v1r3"): the substrate-ledger analog of the registered
% v1r1 enzyme-moiety reconstruction.  The free carriers of EXACT conserved
% ledgers (free tRNAfMetCAU and tRNAGlyGCC from their family totals, free
% PPi from the weighted phosphate ledger) are no longer integrated states:
% each is reconstructed at every RHS evaluation and output time as
%   x_carrier = (total - sum_{j != carrier} w_j x_j) / w_carrier,
% with the totals and weights taken from the frozen ledger_definitions
% config block (derived mechanically from the scope conservation groups).
% This makes the T_G ledgers exact by construction AND returns the token
% content the algebraic complexes drain (the sliding leak measured in the
% v1r2 cycle) to the free pools, so it re-enters the product flow.  The
% v1r2 initializer's tRNA/PPi debit rows drop out (automatic through the
% reconstruction); the Met/Gly/ATP debits remain.  The 21-state
% eliminated set, the closure rows, the acceptance thresholds, the stress
% domain and the author sources are untouched.
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

% x0_override (initializer test suite only: I5 idempotency / I6 determinism /
% I8 perturbation smoothness run the production initializer on explicit
% initial values; the formal runs never use this field)
if isfield(cfg, 'x0_override') && ~isempty(cfg.x0_override)
    fnames = fieldnames(cfg.x0_override);
    for k = 1:numel(fnames)
        j = find(strcmp(names, fnames{k}), 1);
        assert(~isempty(j), 'unknown species %s in x0_override', fnames{k});
        x0(j) = cfg.x0_override.(fnames{k});
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

% initializer selection (needed before the v1r3 reconstruction block)
init_kind = 'v1r1';
if isfield(cfg, 'initializer') && ~isempty(cfg.initializer)
    init_kind = cfg.initializer;
end
debits = [];
if strcmp(init_kind, 'v1r2') || strcmp(init_kind, 'v1r3')
    assert(isfield(cfg, 'init_debits') && ~isempty(cfg.init_debits), ...
        '%s initializer requires the frozen init_debits matrix', init_kind);
    debits = cfg.init_debits;
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

% v1r3 ledger-reconstruction block: the free carriers of exact conserved
% ledgers leave the integrated state vector and are reconstructed at every
% evaluation (same pattern as the free enzyme).  The ledger definitions
% (species + weights + the carrier's own weight) come from the frozen
% config block; the totals are computed from the (scaled) author ICs, i.e.
% they are the FULL model's own t0 inventories.
reconNames = {};
reconIdx = [];
ledSpec = struct('carrier', {}, 'idx', {}, 'members', {}, 'weights', {}, ...
    'wself', {}, 'total', {});
if isfield(cfg, 'reconstructed_ledgers') && ~isempty(cfg.reconstructed_ledgers)
    assert(strcmp(cfg.mode, 'reduced'), ...
        'reconstructed_ledgers apply to reduced mode only');
    assert(strcmp(init_kind, 'v1r3'), ...
        'reconstructed_ledgers require the v1r3 initializer');
    reconNames = cfg.reconstructed_ledgers;
    assert(isfield(cfg, 'ledger_definitions') ...
        && numel(cfg.ledger_definitions) == numel(reconNames), ...
        'v1r3 requires ledger_definitions matching reconstructed_ledgers');
    for k = 1:numel(reconNames)
        j = find(strcmp(names, reconNames{k}), 1);
        assert(~isempty(j), 'reconstructed carrier %s is not a state', ...
            reconNames{k});
        ld = cfg.ledger_definitions(k);
        assert(strcmp(ld.carrier, reconNames{k}), ...
            'ledger_definitions(%d) carrier mismatch', k);
        wself = 0; members = []; weights = [];
        fnames = fieldnames(ld.row);
        for m = 1:numel(fnames)
            jm = find(strcmp(names, fnames{m}), 1);
            assert(~isempty(jm), 'ledger member %s is not a state', fnames{m});
            members(end+1) = jm; %#ok<AGROW>
            weights(end+1) = ld.row.(fnames{m}); %#ok<AGROW>
            if jm == j, wself = ld.row.(fnames{m}); end
        end
        assert(wself > 0, 'carrier %s absent from its own ledger', reconNames{k});
        total = sum(weights(:) .* x0(members(:)));  % FULL t0 inventory (scaled)
        ledSpec(k) = struct('carrier', reconNames{k}, 'idx', j, ...
            'members', {members}, 'weights', {weights}, 'wself', wself, ...
            'total', total);
        reconIdx(k) = j; %#ok<AGROW>
    end
    fprintf('v1r3 ledger reconstruction: %s (totals %s)\n', ...
        strjoin(reconNames, ', '), ...
        strjoin(cellfun(@(v) sprintf('%.10g', v), num2cell([ledSpec.total]), ...
        'UniformOutput', false), ', '));
end

if strcmp(cfg.mode, 'reduced')
    dyn = setdiff((1:NS)', union(union(elim(:), freeIdx), reconIdx));
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
init_kind = 'none';   % reference mode integrates every species directly

if strcmp(cfg.mode, 'reduced')
    % Consistent initial condition. Two registered initializers:
    %   "v1r1" (default): solve the algebraic rows 0 = dx_i/dt(x) for the
    %        eliminated complexes with every non-eliminated state frozen at
    %        its author value, free enzyme reconstructed from pool
    %        conservation (historical behaviour; the recorded v1r1 defect
    %        is that the eliminated complexes' substrate content is NOT
    %        debited from the free pools).
    %   "v1r2": the moiety-consistent initialization map -- the same
    %        closure rows solved JOINTLY for all 21 complexes with the
    %        B_init inventory rows enforced through the config-frozen
    %        debit matrix (init_debits): the complexes' substrate content
    %        is debited from its source free pools (and the free PPi pool
    %        credited for already-released PPi) so that both models start
    %        from identical physical inventories.
    init_kind = 'v1r1';
    if isfield(cfg, 'initializer') && ~isempty(cfg.initializer)
        init_kind = cfg.initializer;
    end
    debits = [];
    if strcmp(init_kind, 'v1r2') || strcmp(init_kind, 'v1r3')
        assert(isfield(cfg, 'init_debits') && ~isempty(cfg.init_debits), ...
            '%s initializer requires the frozen init_debits matrix', init_kind);
        debits = cfg.init_debits;
    end
    yaug0 = [x0(:); zeros(NC, 1)];
    switch init_kind
        case 'v1r1'
            [ycons, ic_jump] = consistentStart(yaug0, tgrid(1), params, ...
                NS, NC, A, used_rows, elim, names);
        case 'v1r2'
            [ycons, ic_jump, ~, ic_info] = consistentStartV1r2(yaug0, ...
                tgrid(1), params, NS, NC, A, used_rows, elim, names, debits, []);
        case 'v1r3'
            % the v1r2 joint solve IS the v1r3 initializer: its B_init debit
            % rows make the projected state satisfy the ledger constraints
            % exactly (the reconstruction correction at the seed is zero), so
            % ledSpec stays empty here; the reconstruction acts only along
            % the trajectory (residual_red), warm-started on the physical
            % branch.
            [ycons, ic_jump, ~, ic_info] = consistentStartV1r2(yaug0, ...
                tgrid(1), params, NS, NC, A, used_rows, elim, names, ...
                debits, []);
        otherwise
            error('unknown initializer %s', init_kind);
    end
    xcons = ycons(1:NS);
    [maxjump, jmax] = max(abs(xcons - x0(:)));
    fprintf('largest initial-condition adjustment: %s: %.6g -> %.6g (%.3g)\n', ...
        names{jmax}, x0(jmax), xcons(jmax), maxjump);
    if ~isempty(ledSpec)
        % v1r3: the projected seed must already satisfy the ledger
        % constraints (the B_init debit rows are the t0 reconstruction);
        % assert the residual correction is at machine level before
        % integrating.
        seedcorr = 0;
        for k = 1:numel(ledSpec)
            s = ledSpec(k);
            seedcorr = max(seedcorr, abs((s.total - ...
                sum(s.weights(:) .* xcons(s.members(:)))) / s.wself));
        end
        fprintf('v1r3 seed ledger-consistency correction: %.3e uM\n', seedcorr);
        assert(seedcorr <= 1e-9, ...
            'v1r3 seed violates the ledger constraints (correction %.3e)', seedcorr);
    end

    % cumulative-extent seeds: the registered P2 fast-layer offsets (v1r2)
    xi0 = zeros(NC, 1);
    if isfield(cfg, 'init_extents_offset') && ~isempty(cfg.init_extents_offset)
        xi0 = cfg.init_extents_offset(:);
        assert(numel(xi0) == NC, 'init_extents_offset length mismatch');
        fprintf('cumulative-extent offsets seeded (P2 fast layer): %s\n', ...
            strjoin(cellfun(@(k, v) sprintf('%s=%.6g', k, v), ...
            reshape({cfg.cumdefs.id}, [], 1), num2cell(xi0(:)), ...
            'UniformOutput', false), ', '));
    end

    % dump the projected initial state (initializer evidence artifact:
    % P1/P2 cross-validation, validator R26, manifests)
    ist = struct('initializer', init_kind, 'time', tgrid(1), ...
        'state_names', {names}, 'state', xcons, ...
        'extent_ids', {{}}, 'extent_seeds', []);
    if NC > 0
        ist.extent_ids = {cfg.cumdefs.id};
        ist.extent_seeds = xi0';
    end
    if strcmp(init_kind, 'v1r2') || strcmp(init_kind, 'v1r3')
        ist.closure_residual_abs = ic_info.res;
        ist.closure_residual_scaled = ic_info.res / max(ic_info.gscale, 1e-300);
        ist.production_scale = ic_info.gscale;
        ist.debits_applied = ic_info.debits_applied;
        ist.debit_pools = ic_info.debit_pools;
        ist.newton_iterations = ic_info.iters;
    end
    if NC > 0
        ist.extent_ids = {cfg.cumdefs.id};
        ist.extent_seeds = xi0';
    end
    fid = fopen([cfg.outfile '.initial_state.json'], 'w');
    assert(fid ~= -1, 'cannot open %s.initial_state.json', cfg.outfile);
    fprintf(fid, '{\n  "initializer": "%s",\n  "time": %.17g,\n', ...
        ist.initializer, ist.time);
    fprintf(fid, '  "state_names": [%s],\n', ...
        strjoin(cellfun(@(c) sprintf('"%s"', c), names, ...
        'UniformOutput', false), ', '));
    fprintf(fid, '  "state": [%s],\n', ...
        strjoin(cellfun(@(c) sprintf('%.17g', c), num2cell(xcons), ...
        'UniformOutput', false), ', '));
    if NC > 0
        fprintf(fid, '  "extent_ids": [%s],\n', ...
            strjoin(cellfun(@(c) sprintf('"%s"', c), ist.extent_ids, ...
            'UniformOutput', false), ', '));
        fprintf(fid, '  "extent_seeds": [%s],\n', ...
            strjoin(cellfun(@(c) sprintf('%.17g', c), num2cell(xi0), ...
            'UniformOutput', false), ', '));
    else
        fprintf(fid, '  "extent_ids": [],\n  "extent_seeds": [],\n');
    end
    if strcmp(init_kind, 'v1r2')
        fprintf(fid, ['  "closure_residual_abs": %.17g,\n' ...
                      '  "closure_residual_scaled": %.17g,\n' ...
                      '  "production_scale": %.17g,\n' ...
                      '  "newton_iterations": %d,\n'], ...
            ist.closure_residual_abs, ist.closure_residual_scaled, ...
            ist.production_scale, ist.newton_iterations);
        fprintf(fid, '  "debit_pools": [%s],\n', ...
            strjoin(cellfun(@(c) sprintf('"%s"', c), ist.debit_pools, ...
            'UniformOutput', false), ', '));
        fprintf(fid, '  "debits_applied": [%s]\n', ...
            strjoin(cellfun(@(c) sprintf('%.17g', c), ...
            num2cell(ist.debits_applied(:)'), 'UniformOutput', false), ', '));
    else
        fprintf(fid, '  "closure_residual_abs": null,\n');
        fprintf(fid, '  "closure_residual_scaled": null,\n');
        fprintf(fid, '  "production_scale": null,\n');
        fprintf(fid, '  "newton_iterations": null,\n');
        fprintf(fid, '  "debit_pools": [],\n  "debits_applied": []\n');
    end
    fprintf(fid, '}\n');
    fclose(fid);

    % per-pool rootfind cache, seeded at the consistent branch. The cache
    % is passed BY VALUE into the RHS and never written back, so every
    % evaluation warm-starts Newton from this same fixed seed: odefun(t,y)
    % stays a deterministic function of (t,y), which ode15s requires for a
    % consistent numerical Jacobian. (Persisting the cache across calls was
    % measured 2026-09-25 to make the RHS path-dependent: 9.9e6 function
    % evaluations and 1.05e5 rejected steps vs 1.7e5 / 1.9e3 here, ~15x
    % slower.) Only the statistics accumulate, via a handle Map that does
    % not feed back into r.
    cache0 = initBlockCache(xcons, elim, names, x0, tgrid(1), params, ledSpec);
    statsH = containers.Map('KeyType', 'char', 'ValueType', 'any');
    statsH('s') = newBlockStats();
    odefun = @(t, y) residual_red(t, y, params, NS, NC, A, used_rows, dyn, ...
        cache0, statsH, ledSpec);
    z0 = [xcons(dyn); xi0];
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
        if ~isempty(ledSpec)
            x = applyLedgerRecon(x, ledSpec);
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
    'initializer', init_kind, ...
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

function r = residual_red(t, y, params, NS, NC, A, used_rows, dyn, cache0, ...
    statsH, ledSpec)
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
        [cache{p}, res, nit, info] = solveBlock(cache{p}, t, x, params, ledSpec);
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
    if ~isempty(ledSpec)
        x = applyLedgerRecon(x, ledSpec);   % v1r3: tRNA/PPi ledger carriers
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

function cache = initBlockCache(xcons, elim, names, x0, t0, params, ledSpec)
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
        if nargin < 7, ledSpec = []; end
        g0 = blockResid(c, t0, x0(:), params, zeros(numel(E), 1), ledSpec);
        c.refscale = max(abs(g0));
        if ~(c.refscale > 0), c.refscale = 1; end
        cache{end+1} = c; %#ok<AGROW>
    end
end

function [c, res, nit, info] = solveBlock(c, t, x, params, ledSpec)
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
    if nargin < 5, ledSpec = []; end
    C = c.C;
    g = blockResid(c, t, x, params, C, ledSpec);
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
                J(:, j) = (blockResid(c, t, x, params, Cp, ledSpec) - g) / h;
            end
            c.J = J;
            c.hasJ = true;
        end
        d = -c.J \ g;
        alpha = 1.0;
        accepted = false;
        while alpha >= 1e-8
            Cn = C + alpha * d;
            gn = blockResid(c, t, x, params, Cn, ledSpec);
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

function g = blockResid(c, t, x, params, C, ledSpec)
% eliminated-block rows of the AUTHOR RHS at trial complexes C, with the
% free enzyme reconstructed from the conserved moiety (A2 / T_G), matching
% the registered partition-verification closure and consistentStart. The
% kept complexes x(c.K) are dynamic states already present in x.  With the
% v1r3 ledger reconstruction (ledSpec non-empty) the exact-ledger carrier
% corrections are applied BEFORE the residual evaluation so the closure is
% enforced on the reconstructed state (the carriers are functions of the
% complexes).
    xt = x;
    xt(c.E) = C(:);
    xt(c.jf) = c.ePool - sum(xt(c.K)) - sum(C(:));
    if nargin >= 6 && ~isempty(ledSpec)
        xt = applyLedgerRecon(xt, ledSpec);
    end
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

function [y, jump, slp, info] = consistentStartV1r2(y, t0, params, NS, NC, ...
    A, used_rows, elim, names, debits, ledSpec)
%CONSISTENTSTARTV1R2  Moiety-consistent initialization map (v1r2, P1).
%
%JOINT damped projected Newton on the 21 algebraic rows with the B_init
%inventory rows enforced through the frozen debit matrix.  Unknowns: the
%21 eliminated complexes of BOTH pools in one vector (the free-pool debits
%couple the pools through free ATP and free PPi, so the pools can no
%longer be solved sequentially).  For every trial C the reduced state is
%assembled as
%   eliminated complexes      = C
%   free MetRS / GlyRS        = ePool - sum(kept) - sum(eliminated)
%   debited free pools        = author value + W*C   (W = frozen debit
%                               matrix; negative entries debit the free
%                               pool for substrate sequestered into the
%                               complexes, the free-PPi entry credits the
%                               pool for PPi already released from the
%                               bare-adenylate complexes)
%   every other state         = author value
%and (v1r3, ledSpec non-empty) the exact-ledger carrier corrections.  Solving the
%closure jointly with the debits makes B*x_RED(t0) = B*x_FULL(t0) hold for
%every declared inventory row by construction (the rows whose only movable
%entries are the complexes and the debited pools), while free AMP stays at
%its author value 0 (registered additional condition delta_AMP = 0; free
%AMP is a kept dynamic state of the reduced formulation).
%
%The Newton discipline is the registered one (multi-start, central FD
%columns with step 1e-7*(|C_j|+1e-10), damped feasibility line search,
%scaled-residual acceptance 1e-10 * production scale, start-agreement
%assertion), extended by the debit-feasibility requirement that no debited
%free pool goes negative.
    yorig = y;
    x_author = y(1:NS);
    iselim = false(NS, 1);
    iselim(elim) = true;
    pools = {'MetRS', 'GlyRS'};
    nP = numel(pools);
    E = cell(nP, 1); K = cell(nP, 1); jf = zeros(nP, 1);
    ePool = zeros(nP, 1); nq = zeros(nP, 1);
    for p = 1:nP
        enz = pools{p};
        jf(p) = find(strcmp(names, enz), 1);
        assert(~isempty(jf(p)), 'consistentStartV1r2: enzyme %s not a state', enz);
        idx = find(startsWith(names, [enz '_']) & ~endsWith(names, '_degraded'));
        E{p} = idx(iselim(idx));
        K{p} = idx(~iselim(idx));
        nq(p) = numel(E{p});
        assert(nq(p) > 0 && ~isempty(K{p}), ...
            'consistentStartV1r2: pool %s partition degenerate', enz);
        ePool(p) = sum(x_author(idx)) + x_author(jf(p));
    end
    NQ = sum(nq);
    % joint unknown ordering: [MetRS eliminated; GlyRS eliminated]
    Eall = [E{1}(:); E{2}(:)];
    nq1 = nq(1);
    posMap = containers.Map(cellstr(names(Eall)), 1:NQ);

    % frozen debit matrix: rows = debited free pools, cols = joint unknowns
    dnames = fieldnames(debits);
    ND = numel(dnames);
    didx = zeros(ND, 1);
    W = zeros(ND, NQ);
    for d = 1:ND
        nm = dnames{d};
        didx(d) = find(strcmp(names, nm), 1);
        assert(~isempty(didx(d)), 'debit pool %s is not a state', nm);
        entries = debits.(nm);
        enames = fieldnames(entries);
        for k = 1:numel(enames)
            key = enames{k};
            assert(isKey(posMap, key), ...
                'debit references %s which is not an eliminated state', key);
            W(d, posMap(key)) = W(d, posMap(key)) + entries.(key);
        end
        % no pessimistic pre-check here: the debits are capacity-bounded by
        % the eliminated complexes' own feasibility (sum(C) <= eK), and the
        % line search enforces x(didx) >= -1e-15 on every trial; an
        % infeasible debit structure surfaces as "no start converged
        % feasibly" and terminates the run fail-closed.
    end
    jfrs = jf;
    freeCaps = zeros(nP, 1);
    for p = 1:nP
        freeCaps(p) = ePool(p) - sum(x_author(K{p}));  % free+eliminated capacity
    end
    % the debit is taken relative to the INPUT state's own bound content:
    %   delta_pool = W * (C - C_in)
    % For the formal runs C_in = 0 (author complexes) and the debit is the
    % sequestered content.  For an already-projected input (I5 idempotency,
    % C_in = C*) the debit vanishes and the projection is the identity, as
    % the inventory rows demand (B x_out = B x_in holds for the input too).
    Cin = x_author(Eall);
    if nargin < 11
        ledSpec = [];
    end
    jointRows = @(C) v1r2JointRows(x_author, Eall, jfrs, freeCaps, ...
        didx, W, nq1, Cin, ledSpec, params, t0, C);
    assemble = @(C) v1r2Assemble(x_author, Eall, jfrs, freeCaps, ...
        didx, W, nq1, Cin, ledSpec, C);

    eK = freeCaps;

    % multi-start: the registered verification starts (all-zero, uniform
    % half-capacity, uniform 5%)
    half = zeros(NQ, 1); five = zeros(NQ, 1);
    half(1:nq1) = 0.5 * eK(1) / nq1;
    five(1:nq1) = 0.05 * eK(1) / nq1;
    half(nq1+1:NQ) = 0.5 * eK(2) / (NQ - nq1);
    five(nq1+1:NQ) = 0.05 * eK(2) / (NQ - nq1);
    starts = {zeros(NQ, 1), half, five};

    sols = struct('C', {}, 'res', {}, 'gscale', {}, 'feas', {}, ...
        'conv', {}, 'iters', {});
    for s = 1:numel(starts)
        C = starts{s}(:);
        g = jointRows(C);
        gscale = max(abs(g));
        tol = 1e-10 * max(gscale, 1e-30);
        converged = false;
        iters = 0;
        if isfinite(gscale)
            for it = 1:300
                iters = it;
                J = zeros(NQ);
                for j = 1:NQ
                    h = 1e-7 * (abs(C(j)) + 1e-10);
                    Cp = C; Cm = C;
                    Cp(j) = Cp(j) + h;  Cm(j) = Cm(j) - h;
                    J(:, j) = (jointRows(Cp) - jointRows(Cm)) / (2 * h);
                end
                if rcond(J) < 1e-14
                    break
                end
                d = -J \ g;
                alpha = 1.0;
                accepted = false;
                while alpha > 1e-12
                    trial = max(C + alpha * d, 0);
                    % projected per-pool capacity feasibility
                    ss1 = sum(trial(1:nq1));
                    if ss1 > eK(1) * (1 + 1e-9)
                        trial(1:nq1) = trial(1:nq1) * (eK(1) * (1 + 1e-9) / ss1);
                    end
                    ss2 = sum(trial(nq1+1:NQ));
                    if ss2 > eK(2) * (1 + 1e-9)
                        trial(nq1+1:NQ) = trial(nq1+1:NQ) * (eK(2) * (1 + 1e-9) / ss2);
                    end
                    [~, feas] = assemble(trial);
                    if ~feas
                        alpha = alpha * 0.5;
                        continue
                    end
                    gt = jointRows(trial);
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
        feas = all(C >= -1e-15);
        feas = feas && sum(C(1:nq1)) <= eK(1) * (1 + 1e-9);
        feas = feas && sum(C(nq1+1:NQ)) <= eK(2) * (1 + 1e-9);
        [~, dfeas] = assemble(C);
        feas = feas && dfeas;
        sols(end+1) = struct('C', {C}, 'res', res, 'gscale', gscale, ...
            'feas', feas, 'conv', converged, 'iters', iters); %#ok<AGROW>
    end

    ok = sols([sols.feas] & [sols.conv]);
    assert(~isempty(ok), ...
        ['consistentStartV1r2: no start converged feasibly (residuals %s ' ...
         'uM/s). Refusing to proceed.'], ...
        strjoin(cellfun(@(v) sprintf('%.2e', v), num2cell([sols.res]), ...
            'UniformOutput', false), ', '));
    if numel(ok) >= 2
        spread = 0;
        for a = 1:numel(ok)
            for b = a+1:numel(ok)
                spread = max(spread, max(abs(ok(a).C - ok(b).C)));
            end
        end
        assert(spread <= 1e-6 * max(ePool), ...
            ['consistentStartV1r2: starts disagree (spread %.2e uM). ' ...
             'Refusing to proceed.'], spread);
    end
    if sols(1).feas && sols(1).conv
        cs = sols(1);
    else
        [~, k] = min([ok.res]);
        cs = ok(k);
    end
    C = cs.C;
    x = assemble(C);
    for p = 1:nP
        if p == 1
            occ = sum(C(1:nq1));
        else
            occ = sum(C(nq1+1:NQ));
        end
        fprintf(['consistent-start-v1r2 %s: n=%d, pool occupancy = %.6g ' ...
                 'of ePool %.6g\n'], pools{p}, nq(p), occ, ePool(p));
    end
    fprintf(['consistent-start-v1r2 joint: max|g| = %.3e uM/s (%.3e of ' ...
             'production scale %.3e), iters = %d, debited pools: %s\n'], ...
        cs.res, cs.res / max(cs.gscale, 1e-300), cs.gscale, cs.iters, ...
        strjoin(cellfun(@(d, nm) sprintf('%s=%.6g', nm, ...
        x(didx(d)) - x_author(didx(d))), num2cell((1:ND)'), dnames, ...
        'UniformOutput', false), ', '));

    y = [x; yorig(NS+1:end)];
    jump = y - yorig;
    slp = residual_full(t0, y, params, NS, NC, A, used_rows);
    info = struct('status', 'ok', 'res', cs.res, 'C', {C}, ...
        'gscale', cs.gscale, 'iters', cs.iters, ...
        'debits_applied', {x(didx) - x_author(didx)}, 'debit_pools', {dnames});
end

function x = applyLedgerRecon(x, ledSpec)
% v1r3 ledger reconstruction: each free carrier is corrected so that its
% ledger row evaluates exactly to the (scaled) author t0 total,
%   x_carrier <- x_carrier + (total - sum_members w_j x_j) / w_self,
% a numerically favourable correction form (the members list includes the
% carrier itself).  Same realization class as the v1r1 enzyme-moiety
% reconstruction (exact by construction at every evaluation).
    for k = 1:numel(ledSpec)
        s = ledSpec(k);
        x(s.idx) = x(s.idx) + (s.total - ...
            sum(s.weights(:) .* x(s.members(:)))) / s.wself;
    end
end

function [x, feas] = v1r2Assemble(x_author, Eall, jfrs, freeCaps, didx, W, ...
    nq1, Cin, ledSpec, C)
% reduced state at trial complexes C with the frozen debit matrix applied
% relative to the input's own bound content C_in and, for v1r3, the
% exact-ledger carrier corrections; feas = no debited free pool below the
% numerical floor
    x = x_author;
    x(Eall) = C;
    x(jfrs(1)) = freeCaps(1) - sum(C(1:nq1));
    x(jfrs(2)) = freeCaps(2) - sum(C(nq1+1:end));
    x(didx) = x_author(didx) + W * (C - Cin);
    if ~isempty(ledSpec)
        x = applyLedgerRecon(x, ledSpec);
    end
    feas = all(x(didx) >= -1e-15);
end

function g = v1r2JointRows(x_author, Eall, jfrs, freeCaps, didx, W, nq1, ...
    Cin, ledSpec, params, t0, C)
% closure rows (AUTHOR RHS dC_i/dt) at the v1r2/v1r3 assembled trial state
    [x, ~] = v1r2Assemble(x_author, Eall, jfrs, freeCaps, didx, W, nq1, ...
        Cin, ledSpec, C);
    dx = fMGG_synthesis(t0, x, params);
    g = dx(Eall);
end
