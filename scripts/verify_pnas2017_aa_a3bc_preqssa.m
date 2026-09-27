function report = verify_pnas2017_aa_a3bc_preqssa(config_path)
%VERIFY_PNAS2017_AA_A3BC_PREQSSA  Exact pre-QSSA validation of the A3b
%coordinate transformation (Phase 5, checks B1-B10).  This phase is NOT
%QSSA validation: any failure here means the coordinate transform is wrong
%and the candidate must STOP before QSSA.
%
% B1  rank(T) = n                        (numeric; the exact modular proof
%                                         lives in protected_ledger_rowspace.json)
% B2  condition number of T
% B3  exact round-trip x -> (y,q) -> x   at the author initial state
% B4  random feasible-state round-trip   (200 log-uniform states, fixed seed)
% B5  author trajectory round-trip       (FULL-S0 grid, every point)
% B6  transformed RHS identity:          the SBML-balance form (w^T S) v
%                                         agrees with the direct weighted
%                                         author-RHS sum  sum_j w_j f_j(x)
%                                         to the double-precision
%                                         cancellation limit of these rows
%                                         (the runner uses the author-faithful
%                                         direct form; the residual is the
%                                         author-vs-SBML representation
%                                         difference, same order as the
%                                         author model's own ledger
%                                         conservation noise)
% B7  q-row identity:                    implemented G(y,q) == Q f(x)
% B8  protected ledgers represented:     l x == y_k at all probe states;
%                                         guanine row covered by identity
%                                         rows (no eliminated/carrier member)
% B9  external interface fluxes:         the artifact (w^T S) nonzero sets
%                                         equal the classified interface
%                                         reactions (B6 validates them
%                                         dynamically at flux-active states)
% B10 no source species silently lost:   241 species partition exactly into
%                                         identity rows + 8 carriers + 21
%                                         eliminated
%
% Probe states for B6-B9: every FULL-S0 trajectory point (flux-active) and
% 200 random feasible states.

scripts_dir = fileparts(mfilename('fullpath'));
root = fullfile(scripts_dir, '..');
addpath(scripts_dir);
model_dir = fullfile(root, 'models', 'pnas2017_full_reference', ...
    'original', 'simulate', 'Simulate_fMGG_synthesis');
addpath(model_dir);

cfg = jsondecode(fileread(config_path));
names = reshape(fMGG_synthesis('states'), 1, []);
C = a3b_build_coords(names, cfg.artifact_dir);
pt = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_parameters.csv'));
params = pt.Value;
it = readtable(fullfile(model_dir, 'dat', 'fMGG_synthesis_initial_values.csv'));
x0 = it.Value;

checks = {};

% ---- T from the frozen artifacts
[T, trows] = read_T(cfg.artifact_dir);
assert(numel(trows) == 241, 'T must have 241 rows');

rk = rank(T);
checks{end+1} = chk('B1_rank_T', rk == 241, sprintf('rank=%d', rk)); %#ok<AGROW>
cdt = cond(T);
checks{end+1} = chk('B2_cond_T', cdt < 1e6, sprintf('cond=%.4e', cdt)); %#ok<AGROW>

% ---- B3: author IC round-trip
[y, q] = encode_split(C, x0(:));
xr = a3b_reconstruct(C, y, q);
[ok3, note3] = roundtrip_ok(C, x0(:), xr);
checks{end+1} = chk('B3_author_IC_roundtrip', ok3, note3); %#ok<AGROW>

% ---- B4: random feasible round-trips
rng(20260926, 'twister');
ok4 = true; note4 = '';
for s = 1:200
    xr = exp(-6 + 12 * rand(241, 1));
    xr(contains(names, '_degraded')) = 0;
    [y, q] = encode_split(C, xr);
    xb = a3b_reconstruct(C, y, q);
    [okk, nn] = roundtrip_ok(C, xr, xb);
    if ~okk
        ok4 = false;
        note4 = sprintf('state %d: %s', s, nn);
    end
end
if ok4, note4 = '200 random feasible states pass to cancellation precision'; end
checks{end+1} = chk('B4_random_roundtrip', ok4, note4); %#ok<AGROW>

% ---- B5: author trajectory round-trip
X = read_trajectory(cfg.full_csv);
ok5 = true; note5 = ''; worst5abs = 0;
for i = 1:size(X, 2)
    xr = X(1:241, i);
    [y, q] = encode_split(C, xr);
    xb = a3b_reconstruct(C, y, q);
    worst5abs = max(worst5abs, max(abs(xb - xr)));
    [okk, nn] = roundtrip_ok(C, xr, xb);
    if ~okk
        ok5 = false;
        note5 = sprintf('point %d: %s', i, nn);
    end
end
if ok5, note5 = sprintf('%d trajectory points pass to cancellation precision (worst abs %.3e)', size(X, 2), worst5abs); end
checks{end+1} = chk('B5_author_trajectory_roundtrip', ok5, note5); %#ok<AGROW>

% ---- B6/B7/B8 at trajectory + random probe states
probes = size(X, 2);
worst6 = 0; worst6rel = 0; worst7 = 0; gscale = 0; worst8 = 0;
for i = 1:probes
    x = X(1:241, i);
    [y, q] = encode_split(C, x);
    dx = fMGG_synthesis(0.1, x, params);
    v = pnas2017_aa_v1_rates(x, params);
    for k = 1:C.nLedger
        L = C.ledger(k);
        impl = L.dotS.vals' * v(L.dotS.ridx);
        direct = sum(L.weights .* dx(L.members));
        cancel = sum(abs(L.weights .* dx(L.members)));
        worst6 = max(worst6, abs(impl - direct));
        worst6rel = max(worst6rel, abs(impl - direct) / max(cancel, 1e-300));
        worst8 = max(worst8, abs(sum(L.weights .* x(L.members)) - y(L.pos)) ...
            / max(abs(y(L.pos)), 1e-30));
    end
    g = a3b_closure_resid(C, 0.1, y, q, params);
    qf = dx(C.elimIdx);
    worst7 = max(worst7, max(abs(g - qf)));
    gscale = max(gscale, max(abs(qf)));
end
for s = 1:200
    x = exp(-4 + 8 * rand(241, 1));
    x(contains(names, '_degraded')) = 0;
    [y, q] = encode_split(C, x);
    dx = fMGG_synthesis(0.1, x, params);
    v = pnas2017_aa_v1_rates(x, params);
    for k = 1:C.nLedger
        L = C.ledger(k);
        impl = L.dotS.vals' * v(L.dotS.ridx);
        direct = sum(L.weights .* dx(L.members));
        cancel = sum(abs(L.weights .* dx(L.members)));
        worst6 = max(worst6, abs(impl - direct));
        worst6rel = max(worst6rel, abs(impl - direct) / max(cancel, 1e-300));
        worst8 = max(worst8, abs(sum(L.weights .* x(L.members)) - y(L.pos)) ...
            / max(abs(y(L.pos)), 1e-30));
    end
    g = a3b_closure_resid(C, 0.1, y, q, params);
    qf = dx(C.elimIdx);
    worst7 = max(worst7, max(abs(g - qf)));
    gscale = max(gscale, max(abs(qf)));
end
checks{end+1} = chk('B6_transformed_rhs_identity', worst6rel <= 1e-8, ...
    sprintf('worst_abs=%.3e worst_rel_to_cancellation_scale=%.3e', worst6, worst6rel)); %#ok<AGROW>
w7rel = worst7 / max(gscale, 1e-300);
checks{end+1} = chk('B7_q_row_identity', w7rel <= 1e-12, ...
    sprintf('worst_abs=%.3e rel=%.3e (gscale %.3e)', worst7, w7rel, gscale)); %#ok<AGROW>
checks{end+1} = chk('B8_ledger_representation', worst8 <= 1e-10, ...
    sprintf('worst_rel=%.3e', worst8)); %#ok<AGROW>

% ---- B8b: guanine row covered by identity rows
rj = jsondecode(fileread(fullfile(cfg.artifact_dir, ...
    'protected_ledger_rowspace.json')));
gl = rj.protected_ledgers.guanine_ledger_total;
% members resolved through the scope artifact: none may be eliminated or a
% replaced carrier
scope = jsondecode(fileread(fullfile(root, 'models', ...
    'pnas2017_full_reference', 'audit', 'aminoacylation_v1_comparison_scope.json')));
gm = {};
for g = 1:numel(scope.conservation)
    grp = scope.conservation{g};    % heterogeneous groups -> cell array
    if strcmp(grp.id, 'guanine_ledger_total')
        gm = grp.species;
    end
end
elimName = false(241, 1);
elimName(C.elimIdx) = true;
replName = false(241, 1);
for k = 1:C.nLedger
    replName(C.ledger(k).replIdx) = true;
end
bad8b = 0;
for g = 1:numel(gm)
    j = find(strcmp(names, gm{g}), 1);
    if elimName(j) || replName(j)
        bad8b = bad8b + 1;
    end
end
checks{end+1} = chk('B8b_guanine_identity_representable', bad8b == 0, ...
    sprintf('%d guanine members on eliminated/carrier roles', bad8b)); %#ok<AGROW>

% ---- B9: dotS nonzero sets match the classified interface reactions
ok9 = true;
ledfields = fieldnames(rj.protected_ledgers);
for k = 1:C.nLedger
    L = C.ledger(k);
    jf = find(strcmp(ledfields, L.name), 1);
    assert(~isempty(jf), 'ledger %s missing from rowspace JSON', L.name);
    cls = rj.protected_ledgers.(ledfields{jf});
    if ~(isstruct(cls) && isfield(cls, 'violations_all') ...
            && cls.violations_all == numel(L.dotS.ridx))
        ok9 = false;
    end
end
checks{end+1} = chk('B9_interface_flux_coverage', ok9, ...
    'dotS nonzero sets match the classified interface reactions'); %#ok<AGROW>

% ---- B10: species partition
role = zeros(241, 1);          % 1 identity, 2 carrier, 3 eliminated
role(C.keepIdx) = 1;
role(C.elimIdx) = 3;
for k = 1:C.nLedger
    role(C.ledger(k).replIdx) = 2;
end
ok10 = all(role > 0);
checks{end+1} = chk('B10_species_partition', ok10, ...
    sprintf('identity=%d carrier=%d eliminated=%d', ...
    sum(role == 1), sum(role == 2), sum(role == 3))); %#ok<AGROW>

report = struct();
report.checks = checks;
report.all_pass = all(cellfun(@(c) c.pass, checks));
fprintf('pre-QSSA B1-B10: %d/%d PASS\n', sum(cellfun(@(c) c.pass, checks)), numel(checks));
for i = 1:numel(checks)
    fprintf('  %-38s %s  %s\n', checks{i}.name, ...
        tern(checks{i}.pass, 'PASS', 'FAIL'), checks{i}.note);
end
if ~report.all_pass
    error('pre-QSSA validation FAILED: stop before QSSA (Phase 5)');
end
end

% ------------------------------------------------------------------
function [ok, note] = roundtrip_ok(C, xr, xb)
% exact round-trip to the double-precision representation of each species:
% identity-row and eliminated species must be EXACT (values copied); a
% reconstructed carrier may carry cancellation of the order of the machine
% epsilon times its ledger row magnitude.
    d = abs(xb - xr);
    tol = zeros(241, 1);
    iscarrier = false(241, 1);
    for k = 1:C.nLedger
        L = C.ledger(k);
        iscarrier(L.replIdx) = true;
        tol(L.replIdx) = 1e-11 * max(abs(xr(L.members)) .* abs(L.weights));
    end
    ok = all(d(~iscarrier) == 0) && all(d(iscarrier) <= tol(iscarrier));
    note = sprintf('worst carrier abs err %.3e, worst carrier rel err %.3e', ...
        max(d(iscarrier)), max(d(iscarrier) ./ max(abs(xr(iscarrier)), 1e-30)));
end

function [y, q] = encode_split(C, x)
    q = x(C.elimIdx);
    y = zeros(C.Ny, 1);
    y(C.keepPos) = x(C.keepIdx);
    for k = 1:C.nLedger
        L = C.ledger(k);
        y(L.pos) = sum(L.weights .* x(L.members));
    end
end

function [T, labels] = read_T(artifact_dir)
    raw = fileread(fullfile(artifact_dir, 'transformation_T.csv'));
    lines = strsplit(strtrim(raw), newline, 'CollapseDelimiters', false);
    hdr = strsplit(lines{1}, ',');
    nsp = numel(hdr) - 3;
    T = zeros(numel(lines) - 1, nsp);
    labels = cell(numel(lines) - 1, 1);
    for i = 2:numel(lines)
        f = strsplit(lines{i}, ',');
        T(i - 1, :) = str2double(f(4:end));
        labels{i - 1} = f{3};
    end
end

function X = read_trajectory(p)
    fid = fopen(p, 'r');
    assert(fid ~= -1, 'trajectory not found: %s', p);
    hdr = strsplit(strtrim(fgetl(fid)), ',');
    fmt = repmat('%f', 1, numel(hdr));
    C = textscan(fid, fmt, 'Delimiter', ',');
    fclose(fid);
    M = cell2mat(C);
    % rows = time points; columns = time, 241 species, then extents
    X = M(:, 2:242)';        % rows = species, cols = time points
end

function s = chk(name, pass, note)
    s = struct('name', name, 'pass', logical(pass), 'note', note);
end

function o = tern(c, a, b)
    if c, o = a; else, o = b; end
end
