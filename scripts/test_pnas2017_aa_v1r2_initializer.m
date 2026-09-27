function out = test_pnas2017_aa_v1r2_initializer()
%TEST_PNAS2017_AA_V1R2_INITIALIZER  I5/I6/I8 initializer tests.
%
% I5 idempotency: the production initializer applied to an ALREADY
%    projected state must leave it unchanged to machine precision.
%    Implemented with x0_override = the projected S0 state (the formal
%    code path; the debit is relative to the input's own bound content, so
%    the second application must be the identity).
% I6 determinism: the S0 smoke run twice from identical inputs must produce
%    byte-identical trajectory and initial-state artifacts.
% I8 perturbation smoothness: +/-1% perturbations of each debitable free
%    pool flow through the projection continuously (no branch jumps): the
%    projected complexes change O(perturbation) and no eliminated complex
%    appears/disappears (material threshold 1e-3 uM).
%
% Results are written to scratch/v1r2/initializer_tests.json.  The I1-I4
% and I7/I9 checks are assembled by
% scripts/validate_pnas2017_aa_v1r2_initializer.py.

outdir = fullfile(fileparts(mfilename('fullpath')), '..', 'scratch', 'v1r2');
smoke_csv = fullfile(outdir, 'RED-S0-v1r2-smoke.csv');
ist = jsondecode(fileread([smoke_csv '.initial_state.json']));
names = ist.state_names;
NS = numel(names);

res = struct();

% ---------------- I5 idempotency ----------------
cfg = jsondecode(fileread(fullfile(outdir, 'RED-S0-v1r2-smoke.json')));
ov = struct();
for k = 1:NS
    ov.(names{k}) = ist.state(k);
end
cfg.x0_override = ov;
cfg.outfile = fullfile(outdir, 'I5_idempotent.csv');
cfg.stats = false;
cfg.x0_scale = struct();
tmp_cfg = fullfile(outdir, 'I5_idempotent.json');
fid = fopen(tmp_cfg, 'w'); fwrite(fid, jsonencode(cfg)); fclose(fid);
run_pnas2017_aa_v1_formal(tmp_cfg);
ist2 = jsondecode(fileread([fullfile(outdir, 'I5_idempotent.csv') ...
    '.initial_state.json']));
d = max(abs(ist2.state - ist.state));
res.I5_idempotency_max_abs_diff = d;
res.I5_idempotency_pass = d <= 1e-9;
fprintf('I5 idempotency: max|P(P(x))-P(x)| = %.3e -> %d\n', d, res.I5_idempotency_pass);

% ---------------- I6 determinism ----------------
cfg = jsondecode(fileread(fullfile(outdir, 'RED-S0-v1r2-smoke.json')));
cfg.stats = false;
cfg.outfile = fullfile(outdir, 'I6_det_a.csv');
tmp_cfg = fullfile(outdir, 'I6_det_a.json');
fid = fopen(tmp_cfg, 'w'); fwrite(fid, jsonencode(cfg)); fclose(fid);
run_pnas2017_aa_v1_formal(tmp_cfg);
cfg.outfile = fullfile(outdir, 'I6_det_b.csv');
tmp_cfg = fullfile(outdir, 'I6_det_b.json');
fid = fopen(tmp_cfg, 'w'); fwrite(fid, jsonencode(cfg)); fclose(fid);
run_pnas2017_aa_v1_formal(tmp_cfg);
fa = fileread(fullfile(outdir, 'I6_det_a.csv'));
fb = fileread(fullfile(outdir, 'I6_det_b.csv'));
ja = fileread(fullfile(outdir, 'I6_det_a.csv.initial_state.json'));
jb = fileread(fullfile(outdir, 'I6_det_b.csv.initial_state.json'));
res.I6_trajectories_byte_identical = strcmp(fa, fb);
res.I6_initial_states_byte_identical = strcmp(ja, jb);
res.I6_pass = res.I6_trajectories_byte_identical && res.I6_initial_states_byte_identical;
fprintf('I6 determinism: traj identical = %d, initial states identical = %d\n', ...
    res.I6_trajectories_byte_identical, res.I6_initial_states_byte_identical);

% ---------------- I8 perturbation smoothness ----------------
base = jsondecode(fileread(fullfile(outdir, 'RED-S0-v1r2-smoke.json')));
base.stats = false;
pools = fieldnames(base.init_debits);
perturbable = {'ATP', 'tRNAfMetCAU', 'tRNAGlyGCC', 'Met', 'Gly'};
frac = 0.01;
I8 = struct('fraction', frac, 'cases', {{}});
for p = 1:numel(perturbable)
    nm = perturbable{p};
    for sgn = [-1, 1]
        cfg = base;
        j = find(strcmp(names, nm), 1);
        cfg.x0_override = struct();
        cfg.x0_override.(nm) = ist.state(j) * (1 + sgn * frac) ...
            + sgn * frac * 1e-6;   % keep exact-0 pools movable
        tag = sprintf('%s%+d', nm, sgn);
        cfg.outfile = fullfile(outdir, ['I8_' tag '.csv']);
        tmp_cfg = fullfile(outdir, ['I8_' tag '.json']);
        fid = fopen(tmp_cfg, 'w'); fwrite(fid, jsonencode(cfg)); fclose(fid);
        run_pnas2017_aa_v1_formal(tmp_cfg);
        istp = jsondecode(fileread([cfg.outfile '.initial_state.json']));
        dd = istp.state - ist.state;
        % eliminated-complex block: the last states are not identifiable by
        % position alone here; compare per species name below
        I8.cases{end+1} = struct('pool', nm, 'sign', sgn, ...
            'state', istp.state, 'closure_residual_scaled', ...
            istp.closure_residual_scaled); %#ok<AGROW>
        fprintf('I8 %s: max|d state| = %.3e, scaled residual = %.3e\n', ...
            tag, max(abs(dd)), istp.closure_residual_scaled);
    end
end
% smoothness analysis: per case, the projected change of each eliminated
% complex and of the debited pools, relative to the perturbation size
partj = jsondecode(fileread(fullfile(fileparts(mfilename('fullpath')), ...
    '..', 'docs', 'audit', 'pnas2017_aminoacylation_reduction_v1', ...
    'candidate_partition_v1r1.json')));
elim = partj.eliminated_states;
elim_idx = zeros(numel(elim), 1);
for k = 1:numel(elim)
    elim_idx(k) = find(strcmp(names, elim{k}), 1);
end
baseC = ist.state(elim_idx);
worst_lipschitz = 0; worst_case = ''; branch_jumps = {};
for c = 1:numel(I8.cases)
    dC = I8.cases{c}.state(elim_idx) - baseC;
    % relative-to-pool Lipschitz: complexes are O(ePool 0.44); the
    % perturbation is 1% of a pool; a branch jump would move a complex by
    % O(pool) not O(perturbation)
    lip = max(abs(dC)) / (0.44 * I8.fraction);
    if lip > worst_lipschitz
        worst_lipschitz = lip; worst_case = sprintf('%s%+d', ...
            I8.cases{c}.pool, I8.cases{c}.sign);
    end
    % material appearance/disappearance (threshold 1e-3 uM)
    for k = 1:numel(elim)
        if (abs(baseC(k)) < 1e-8 && abs(baseC(k) + dC(k)) > 1e-3) || ...
           (abs(baseC(k)) > 1e-3 && abs(baseC(k) + dC(k)) < 1e-8)
            branch_jumps{end+1} = sprintf('%s@%s%+d', elim{k}, ...
                I8.cases{c}.pool, I8.cases{c}.sign); %#ok<AGROW>
        end
    end
end
res.I8_worst_lipschitz_ratio = worst_lipschitz;
res.I8_worst_case = worst_case;
res.I8_branch_jumps = {branch_jumps};
res.I8_pass = isempty(branch_jumps) && worst_lipschitz <= 20;
fprintf('I8 smoothness: worst Lipschitz ratio %.3g (%s), jumps %d -> %d\n', ...
    worst_lipschitz, worst_case, numel(branch_jumps), res.I8_pass);

out = res;
fid = fopen(fullfile(outdir, 'initializer_tests.json'), 'w');
assert(fid ~= -1, 'cannot write initializer_tests.json');
fwrite(fid, jsonencode(res, 'PrettyPrint', true));
fclose(fid);
fprintf('initializer I5/I6/I8 results -> scratch/v1r2/initializer_tests.json\n');
end
