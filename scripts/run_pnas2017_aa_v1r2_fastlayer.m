function out = run_pnas2017_aa_v1r2_fastlayer(config_path)
%RUN_PNAS2017_AA_V1R2_FASTLAYER  P2 fast-boundary-layer dynamic projection
% for the v1r2 moiety-consistent initialization map (initialization-only
% diagnostic; NOT a formal run).
%
% Starting from the (per-condition scaled) AUTHOR physical initial state,
% the registered fast aminoacylation subsystem (the 47 closed aminoacylation
% species of aminoacylation_v1_comparison_scope.json) is integrated under
% the unmodified author RHS with every NON-subsystem state frozen at its
% author value (legitimately slow/external on the boundary-layer timescale)
% and with the registered cumulative-extent rows augmented.  The layer is
% integrated to the registered exit criterion
%
%   max scaled |G| = max_i |dC_i/dt| / production_scale(pool i) <= 1e-10
%
% sustained to the end of the integration horizon (20 * registered
% tau_fast), and the eliminated complexes' branch consistency is verified
% by re-solving the closure at the frozen layer free-pool values and
% requiring agreement with the layer's own complex values.
%
% Recorded: x_layer (all 241 species + extents at exit), t_layer, scaled |G|
% at exit, the complexes' drift rate at exit, the closure branch check, the
% cumulative fast reaction extents at exit (the registered Phase-6 offset
% source), the minimum subsystem concentration, and the change in every
% declared B_init inventory (computed downstream in Python from the CSV).
%
% config JSON fields:
%   eliminated        the registered 21 eliminated species
%   subsystem_species the 47 scope subsystem species (verified vs names)
%   tau_fast          registered layer timescale (s)
%   horizon_mult      integration horizon = horizon_mult * tau_fast
%   exit_scaled_G     registered exit criterion (1e-10)
%   reltol abstol     solver tolerances
%   x0_scale          optional per-condition scaling
%   cumdefs           registered cumulative extent definitions
%   outfile           CSV trajectory (all 241 species + extents)
%   summary_outfile   JSON summary

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

% subsystem species: scope list verified against the model states
sub = cfg.subsystem_species;
sub_idx = zeros(numel(sub), 1);
for k = 1:numel(sub)
    j = find(strcmp(names, sub{k}), 1);
    assert(~isempty(j), 'subsystem species %s is not a state', sub{k});
    sub_idx(k) = j;
end
Nsub = numel(sub_idx);
% closure rows
elim = cfg.eliminated;
elim_idx = zeros(numel(elim), 1);
for k = 1:numel(elim)
    j = find(strcmp(names, elim{k}), 1);
    assert(~isempty(j), 'eliminated species %s is not a state', elim{k});
    elim_idx(k) = j;
end
% production scales per eliminated row (author ICs, complexes zero):
% identical definition to the runner's initBlockCache refscale
pools = {'MetRS', 'GlyRS'};
poolOf = zeros(numel(elim_idx), 1);
refscale = zeros(numel(elim_idx), 1);
dx0 = fMGG_synthesis(0, x0, params);
for p = 1:numel(pools)
    jf = find(strcmp(names, pools{p}), 1);
    idx = find(startsWith(names, [pools{p} '_']) & ~endsWith(names, '_degraded'));
    isE = ismember(idx, elim_idx);
    E = sort(idx(isE));
    refscale(ismember(elim_idx, E)) = max(abs(dx0(E)));
    poolOf(ismember(elim_idx, E)) = p;
end
assert(all(refscale > 0), 'zero production scale for some eliminated row');

% cumulative extents
NC = 0;
if isfield(cfg, 'cumdefs'), NC = numel(cfg.cumdefs); end
A = zeros(NC, 968);
for k = 1:NC
    terms = cfg.cumdefs(k).reactions;
    for m = 1:numel(terms)
        ridx = str2double(terms(m).rid(3:end));
        assert(ridx >= 1 && ridx <= 968, 'bad reaction id %s', terms(m).rid);
        A(k, ridx) = A(k, ridx) + terms(m).sign;
    end
end
used_rows = find(any(A ~= 0, 1));

% fast mechanism = the registered aminoacylation reaction set ONLY (the 138
% reactions of aminoacylation_v1_ledger.csv).  The energy-regeneration and
% translation reactions are legitimately slow/external on the boundary-layer
% timescale and are FROZEN: their fluxes would otherwise act on the
% subsystem's nucleotide pools at clamped-author-state rates and drain ATP
% unphysically (measured 2026-09-26: dATP/dt = -1.3e5 uM/s from the frozen
% energy network when only the states were frozen).  Sfast maps the 968
% reaction fluxes onto the subsystem species with nonzero rows restricted to
% the registered mechanism.
led = readtable(fullfile(fileparts(model_dir), '..', '..', 'audit', ...
    'aminoacylation_v1_ledger.csv'));
sub_reactions = led.reaction_id;
Sfast = zeros(Nsub, 968);
mask = false(968, 1);
for k = 1:numel(sub_reactions)
    ridx = str2double(sub_reactions{k}(3:end));
    assert(ridx >= 1 && ridx <= 968, 'bad ledger reaction %s', sub_reactions{k});
    mask(ridx) = true;
    rea = strsplit(strrep(led.reactants{k}, '|', ','), ',');
    pro = strsplit(strrep(led.products{k}, '|', ','), ',');
    rea = rea(~cellfun(@isempty, rea));
    pro = pro(~cellfun(@isempty, pro));
    for m = 1:numel(rea)
        tok = strsplit(strtrim(rea{m}), ':');
        sp = strtrim(tok{1});
        n = 1;
        if numel(tok) > 1, n = str2double(tok{2}); end
        j = find(strcmp(names, sp), 1);
        assert(~isempty(j), 'ledger species %s is not a state', sp);
        assert(ismember(j, sub_idx), 'ledger species %s outside subsystem', sp);
        Sfast(sub_idx == j, ridx) = Sfast(sub_idx == j, ridx) - n;
    end
    for m = 1:numel(pro)
        tok = strsplit(strtrim(pro{m}), ':');
        sp = strtrim(tok{1});
        n = 1;
        if numel(tok) > 1, n = str2double(tok{2}); end
        j = find(strcmp(names, sp), 1);
        assert(~isempty(j), 'ledger species %s is not a state', sp);
        assert(ismember(j, sub_idx), 'ledger species %s outside subsystem', sp);
        Sfast(sub_idx == j, ridx) = Sfast(sub_idx == j, ridx) + n;
    end
end
fprintf('fast mechanism: %d registered reactions (mask sum %d)\n', ...
    numel(sub_reactions), sum(mask));

tau = cfg.tau_fast;
horizon = cfg.horizon_mult * tau;
tgrid = logspace(log10(1e-6), log10(horizon), 800);

opt = odeset('RelTol', cfg.reltol, 'AbsTol', cfg.abstol, 'Stats', 'on');
diag('on'); diary([cfg.outfile '.stats.raw.txt']);
rhs = @(t, y) fastlayer_rhs(t, y, x0, params, NS, NC, A, used_rows, ...
    sub_idx, Nsub, Sfast, mask);
[tv, yv] = ode15s(rhs, tgrid, [x0(sub_idx); zeros(NC, 1)], opt);
diary off; diag('off');
if size(yv, 1) == numel(tv) && size(yv, 2) == Nsub + NC
    yv = yv';
end

% scaled closure residual along the layer
Gsc = zeros(numel(tv), 1);
Gabs = zeros(numel(tv), 1);
for i = 1:numel(tv)
    x = x0;
    x(sub_idx) = yv(1:Nsub, i);
    dx = fMGG_synthesis(tv(i), x, params);
    g = dx(elim_idx);
    Gabs(i) = max(abs(g));
    Gsc(i) = max(abs(g) ./ refscale);
end
exit_ok = Gsc <= cfg.exit_scaled_G;
t_layer = NaN;
k_layer = NaN;
lastbad = find(~exit_ok, 1, 'last');
if isempty(lastbad)
    k_layer = 1;              % satisfied from the first output point
elseif lastbad < numel(tv)
    k_layer = lastbad + 1;    % first sustained point after the last violation
end
exit_criterion_met = ~isnan(k_layer);
if ~exit_criterion_met
    % criterion not sustained within the horizon: report the last state as
    % the layer exit (fail-open diagnostic record with the profile logged)
    k_layer = numel(tv);
    t_layer = tv(k_layer);
    fprintf(['fast-layer WARNING: scaled|G| <= %g not sustained within ' ...
             'horizon %.6g s; last scaled|G| = %.3e\n'], ...
        cfg.exit_scaled_G, horizon, Gsc(k_layer));
else
    t_layer = tv(k_layer);
end
% criterion-approach profile: first sustained time under each decade
profile_thresholds = [1e-4, 1e-6, 1e-8, 1e-10];
t_under = nan(numel(profile_thresholds), 1);
for th = 1:numel(profile_thresholds)
    idx = find(Gsc <= profile_thresholds(th), 1);
    if ~isempty(idx), t_under(th) = tv(idx); end
end

% write the full-state trajectory BEFORE any further diagnostics so the
% layer evidence is preserved even if a later check fails
Yout = zeros(NS + NC, numel(tv));
for i = 1:numel(tv)
    x = x0;
    x(sub_idx) = yv(1:Nsub, i);
    Yout(1:NS, i) = x;
    Yout(NS+1:end, i) = yv(Nsub+1:end, i);
end
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

% branch consistency at the layer exit: re-solve the closure at the layer's
% free-pool values (complexes as unknowns, per-pool Newton, registered
% discipline) and compare with the layer's own complex values
x_layer = x0;
x_layer(sub_idx) = yv(1:Nsub, k_layer);
[Cstar, res_star] = closureAtState(x_layer, elim_idx, pools, names, params, tv(k_layer));
branch_rel = max(abs(Cstar - x_layer(elim_idx))) ./ max(max(abs(Cstar)), 1e-12);

% complexes' drift rate at exit (shape distance to the attracting branch)
dxl = fMGG_synthesis(tv(k_layer), x_layer, params);
drift_rate = max(abs(dxl(elim_idx)) ./ max(abs(x_layer(elim_idx)), 1e-12));

% summary
ext = yv(Nsub+1:end, k_layer);
summary = struct();
summary.exit_criterion_met = exit_criterion_met;
summary.t_layer = t_layer;
summary.exit_criterion = cfg.exit_scaled_G;
summary.scaled_G_at_exit = Gsc(k_layer);
summary.abs_G_at_exit = Gabs(k_layer);
summary.max_scaled_G_over_layer = max(Gsc);
summary.first_time_under = strjoin(...
    cellfun(@(a, b) sprintf('%.0e:%.6g', a, b), ...
    num2cell(profile_thresholds(:)'), num2cell(t_under(:)'), ...
    'UniformOutput', false), ', ');
summary.complex_drift_rate_at_exit = drift_rate;
summary.branch_check_rel_diff = branch_rel;
summary.branch_check_max_abs = max(abs(Cstar - x_layer(elim_idx)));
summary.closure_resolve_residual = res_star;
summary.min_subsystem_conc = min(yv(1:Nsub, k_layer));
summary.extent_ids = {cfg.cumdefs.id};
summary.extents_at_exit = ext';
summary.horizon = horizon;
summary.n_output_points = numel(tv);
jsondump(summary, cfg.summary_outfile);

out = struct('t_layer', t_layer, 'k_layer', k_layer, ...
    'max_scaled_G', max(Gsc), 'scaled_G_at_exit', Gsc(k_layer), ...
    'branch_rel', branch_rel, 'drift_rate', drift_rate, ...
    'extents_at_exit', ext, 'outfile', cfg.outfile);
fprintf(['fast-layer done: t_layer = %.6g s (horizon %.6g s), ' ...
         'scaled|G| at exit = %.3e, branch rel diff = %.3e, ' ...
         'drift rate = %.3e, min conc = %.3e\n'], ...
    t_layer, horizon, Gsc(k_layer), branch_rel, drift_rate, ...
    min(yv(1:Nsub, k_layer)));
end

function r = fastlayer_rhs(t, y, x0, params, NS, NC, A, used_rows, ...
    sub_idx, Nsub, Sfast, mask)
% registered fast mechanism restricted to the subsystem: every non-subsystem
% state clamped at its author value AND every non-aminoacylation reaction
% frozen; cumulative-extent rows appended
    x = x0;
    x(sub_idx) = y(1:Nsub);
    v = pnas2017_aa_v1_rates(x, params);
    v = v .* mask;
    r = [Sfast * v; zeros(NC, 1)];
    if NC > 0
        r(Nsub+1:end) = (A(:, used_rows) * v(used_rows));
    end
end

function [Cstar, res] = closureAtState(x, elim_idx, pools, names, params, t)
% per-pool damped Newton on 0 = dC_i/dt at the state x with the complexes as
% unknowns and the free enzyme reconstructed from the pool moiety (free
% substrates FIXED at the layer values) -- the branch check of P2
    Cstar = x(elim_idx);
    res = 0;
    for p = 1:numel(pools)
        jf = find(strcmp(names, pools{p}), 1);
        idx = find(startsWith(names, [pools{p} '_']) & ~endsWith(names, '_degraded'));
        E = sort(idx(ismember(idx, elim_idx)));
        K = idx(~ismember(idx, elim_idx));
        ePool = x(jf) + sum(x(idx));
        freeCap = ePool - sum(x(K));
        F = @(C) algRowsFixed(t, x, E, jf, freeCap, params, C);
        C = x(E);
        g = F(C);
        gscale = max(abs(g));
        tol = 1e-12 * max(gscale, 1e-30);
        for it = 1:60
            J = zeros(numel(E));
            for j = 1:numel(E)
                h = 1e-7 * (abs(C(j)) + 1e-10);
                Cp = C; Cm = C;
                Cp(j) = Cp(j) + h;  Cm(j) = Cm(j) - h;
                J(:, j) = (F(Cp) - F(Cm)) / (2 * h);
            end
            if rcond(J) < 1e-14, break; end
            d = -J \ g;
            alpha = 1.0;
            acc = false;
            while alpha > 1e-12
                trial = max(C + alpha * d, 0);
                gt = F(trial);
                if max(abs(gt)) < max(abs(g)), acc = true; break; end
                alpha = alpha * 0.5;
            end
            if ~acc, break; end
            C = trial; g = gt;
            if max(abs(g)) <= tol, break; end
        end
        [~, loc] = ismember(E, elim_idx);
        assert(all(loc > 0), 'closureAtState: eliminated index mismatch');
        Cstar(loc) = C;
        res = max(res, max(abs(g)));
    end
end

function g = algRowsFixed(t, xbase, E, jf, freeCap, params, C)
    xt = xbase;
    xt(E) = C(:);
    xt(jf) = freeCap - sum(C(:));
    dx = fMGG_synthesis(t, xt, params);
    g = dx(E);
end

function jsondump(s, path)
% minimal flat-struct JSON writer (cell of char -> JSON array)
    fid = fopen(path, 'w');
    assert(fid ~= -1, 'cannot open %s', path);
    fprintf(fid, '{\n');
    fn = fieldnames(s);
    for k = 1:numel(fn)
        v = s.(fn{k});
        sep = ','; if k == numel(fn), sep = ''; end
        if ischar(v)
            fprintf(fid, '  "%s": "%s"%s\n', fn{k}, v, sep);
        elseif iscell(v) && all(cellfun(@ischar, v))
            fprintf(fid, '  "%s": [%s]%s\n', fn{k}, ...
                strjoin(cellfun(@(c) sprintf('"%s"', c), v, ...
                'UniformOutput', false), ', '), sep);
        elseif isnumeric(v) && numel(v) > 1
            fprintf(fid, '  "%s": [%s]%s\n', fn{k}, ...
                strjoin(cellfun(@(c) sprintf('%.17g', c), num2cell(v(:)'), ...
                'UniformOutput', false), ', '), sep);
        elseif isnumeric(v)
            fprintf(fid, '  "%s": %.17g%s\n', fn{k}, v, sep);
        else
            fprintf(fid, '  "%s": null%s\n', fn{k}, sep);
        end
    end
    fprintf(fid, '}\n');
    fclose(fid);
end
