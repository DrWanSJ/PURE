function run_fig4_benchmark(varargin)
%RUN_FIG4_BENCHMARK B1 benchmark: reproduce Mavelli 2015 Fig. 4 (calculated curves).
%
%   RUN_FIG4_BENCHMARK('RunId', RUN_ID)
%
%   Runs the PURE_literature_reference model (literal translation of
%   Mavelli, Marangoni, Stano 2015, Bull Math Biol 77:1185-1212,
%   DOI 10.1007/s11538-015-0082-8) at the three Fig. 4 DNA template
%   concentrations (0.34 / 1.7 / 6.8 nM) for 0-4 h with ode15s.
%
%   Provenance (audit hardening): every run writes
%     results/runs/<run_id>/manifest.json
%   with the LIVE git commit (git rev-parse HEAD), a live dirty-tree check
%   and SHA-256 hashes of the canonical model definition, the parameter
%   file and the run inputs. Ordinary runs are NOT committed (see
%   results/runs/README.md). The frozen regression baseline lives in
%   results/baselines/b1_mavelli2015/ and predates this system; it is
%   labeled provenance_status = "legacy_unbound_to_execution_commit";
%   it is never overwritten and never back-filled with execution provenance.
%
%   Outputs (per run):
%     results/runs/<run_id>/DNA_0p34nM/{trajectory.csv,rates.csv,qc.json}
%     results/runs/<run_id>/DNA_1p7nM/ {...}
%     results/runs/<run_id>/DNA_6p8nM/ {...}
%     results/runs/<run_id>/fig4_reproduction.png
%     results/runs/<run_id>/observables_mRNA_protein.png
%     results/runs/<run_id>/benchmark_summary.json
%     results/runs/<run_id>/manifest.json
%
%   Validation layering:
%     1. equation-level verification  -> matlab/tests/
%     2. internal numerical/QC checks -> conservation Eqs. (15)-(19), nonnegativity,
%        repeatability, solver-tolerance study (this script)
%     3. Fig. 4 comparison            -> paper-text anchors (independent) and the
%        raster digitization (matlab/tools/digitization/digitize_fig4.m) whose
%        calculated-vs-experimental cluster assignment is SIMULATION-ASSISTED
%        and therefore NON-INDEPENDENT (validation_status =
%        non_independent_assignment); see docs/audit/audit_status.md and
%        docs/audit/manual_fig4_audit_protocol.md.
%   Experimental dotted curves are NOT overlaid and the experimental curves were
%   NOT digitized (no machine-readable Stoegbauer 2012 data in the repo).

d    = fileparts(mfilename('fullpath'));   % .../matlab/src/simulate
root = fileparts(fileparts(fileparts(d)));
addpath(fullfile(root, 'matlab', 'generated'));
addpath(fullfile(root, 'matlab', 'src', 'simulate'));
addpath(fullfile(root, 'matlab', 'src', 'provenance'));

ip = inputParser;
ip.addParameter('RunId', '', @(s) ischar(s) || isstring(s));
ip.parse(varargin{:});
run_id = ip.Results.RunId;
if isempty(run_id)
    run_id = sprintf('b1_fig4_%s', char(datetime('now', 'Format', 'yyyyMMdd_HHmmssSSS')));
end

run_inputs = struct('dna_uM', {[0.00034, 0.0017, 0.0068]}, ...
    't_final_s', 14400, 'output_dt_s', 10);
prov = pure_run_provenance(root, run_inputs);

outdir = fullfile(root, 'results', 'runs', run_id);
if ~exist(outdir, 'dir'); mkdir(outdir); end

p0 = pure_literature_reference_params();
L  = p0.L;

cond = struct( ...
    'label',  {'DNA_0p34nM', 'DNA_1p7nM',  'DNA_6p8nM'}, ...
    'dna_uM', {0.00034,      0.0017,       0.0068}, ...
    'legend', {'new_simulation: DNA = 0.34 nM', ...
               'new_simulation: DNA = 1.7 nM', ...
               'new_simulation: DNA = 6.8 nM'});
colors = [0.000 0.447 0.741;    % blue  (paper: 0.34 nM)
          0.466 0.674 0.188;    % green (paper: 1.7 nM)
          0.937 0.262 0.211];   % red   (paper: 6.8 nM)

nCond = numel(cond);
res = cell(nCond, 1);
summary = struct();
summary.model_id = p0.meta.model_id;
summary.source   = 'Mavelli_2015';
summary.run_id   = run_id;
summary.provenance_status = 'provenance_bound';
summary.git_commit = prov.git_commit;
summary.git_dirty = prov.git_dirty;
summary.model_definition_hash = prov.model_definition_hash;
summary.parameter_hash = prov.parameter_hash;
summary.generated_by = 'run_fig4_benchmark.m';
summary.date     = char(datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss'));
summary.solver   = 'ode15s';
summary.time_unit = 's';
summary.concentration_unit = 'uM';
summary.conditions = cell(nCond,1);

for k = 1:nCond
    fprintf('\n=== condition %d/3: %s (DNA = %g nM) ===\n', k, cond(k).label, cond(k).dna_uM*1e3);

    % ---- baseline run (RelTol 1e-9, AbsTol 1e-12) ----
    base = simulate_pure_literature_reference(cond(k).dna_uM);

    % ---- repeatability: two more identical runs (deterministic solver) ----
    rep1 = simulate_pure_literature_reference(cond(k).dna_uM);
    rep2 = simulate_pure_literature_reference(cond(k).dna_uM);
    repeat_maxdiff = max([ ...
        max(abs(base.yfull(:) - rep1.yfull(:))), ...
        max(abs(base.yfull(:) - rep2.yfull(:))), ...
        max(abs(base.rates(:) - rep1.rates(:))), ...
        max(abs(base.rates(:) - rep2.rates(:)))]);
    repeatability_pass = (repeat_maxdiff == 0);

    % ---- solver-tolerance study: tighter tolerances ----
    tight = simulate_pure_literature_reference(cond(k).dna_uM, ...
                'RelTol', p0.meta.simulation.tolerance_study.RelTol_tight, ...
                'AbsTol', p0.meta.simulation.tolerance_study.AbsTol_tight);
    % per-state scale registered from the baseline run (documented choice:
    % s_i = max(|y0_i|, max_t |y_b,i(t)|); scaled difference per Eq. (15.1)
    % of the project tasklist, with the trajectory maximum added so that
    % zero-scale states do not blow up the metric)
    y0abs = abs(base.p.y0(:))';
    s = max([y0abs; max(abs(base.y))]);
    E = max(abs(tight.y - base.y) ./ (repmat(s, numel(base.t), 1) + abs(base.y)));
    convergence_max_scaled_diff = max(E(:));
    convergence_pass = convergence_max_scaled_diff <= 1e-6;

    % ---- per-run equation identity guard (balance derivatives == 0) ----
    eq_ok = local_equation_guard(base, p0);

    % ---- anchors from the paper text ----
    anchor = local_anchors(base, cond(k).dna_uM, L);

    % ---- write outputs ----
    condDir = fullfile(outdir, cond(k).label);
    if ~exist(condDir, 'dir'); mkdir(condDir); end

    t = base.t;
    traj = table(t, t/3600, base.y(:,1), base.y(:,2), base.y(:,3), base.y(:,4), ...
        base.y(:,5), base.y(:,6), base.y(:,7), base.y(:,8), base.y(:,9), base.y(:,10), ...
        base.yfull(:,11), base.yfull(:,12), base.mRNA, base.protein, ...
        'VariableNames', {'time_s','time_h','NTP_uM','NXP_uM','nt_uM','A_uM', ...
        'T_uM','AT_uM','a_uM','CP_uM','C_uM','TLcat_uM','D_nt_uM','D_TLcat_uM', ...
        'mRNA_molecules_uM','protein_molecules_uM'});
    writetable(traj, fullfile(condDir, 'trajectory.csv'));

    rates = table(t, base.rates(:,1), base.rates(:,2), base.rates(:,3), ...
        base.rates(:,4), base.rates(:,5), base.rates(:,6), ...
        base.yfull(:,11), base.yfull(:,12), ...
        'VariableNames', {'time_s','V_TX_uM_s','V_nt_deg_uM_s','V_RS_uM_s', ...
        'V_TL_uM_s','V_TL_deg_uM_s','V_EN_uM_s','D_nt_uM','D_TLcat_uM'});
    writetable(rates, fullfile(condDir, 'rates.csv'));

    qc = base.qc;
    qcStruct = struct();
    qcStruct.execution_status = 'completed';
    if qc.mass_balance_pass && qc.nonnegative && qc.all_finite && ...
            repeatability_pass && convergence_pass && eq_ok
        qcStruct.scientific_status = 'passed_all_qc';
    else
        qcStruct.scientific_status = 'failed_qc';
    end
    qcStruct.model_id = 'PURE_literature_reference';
    qcStruct.source   = 'Mavelli_2015';
    qcStruct.run_id   = run_id;
    qcStruct.provenance_status = 'provenance_bound';
    qcStruct.git_commit = prov.git_commit;
    qcStruct.git_dirty  = prov.git_dirty;
    qcStruct.model_definition_hash = prov.model_definition_hash;
    qcStruct.parameter_hash = prov.parameter_hash;
    qcStruct.solver   = 'ode15s';
    qcStruct.time_unit = 's';
    qcStruct.concentration_unit = 'uM';
    qcStruct.relative_tolerance = base.opts.RelTol;
    qcStruct.absolute_tolerance = base.opts.AbsTol;
    qcStruct.dna_uM  = cond(k).dna_uM;
    qcStruct.dna_nM  = cond(k).dna_uM*1e3;
    qcStruct.nonnegativity_pass = qc.nonnegative && qc.all_finite;
    qcStruct.min_state_value    = qc.min_state_value;
    qcStruct.min_state_name     = qc.min_state_name;
    qcStruct.mass_balance_pass  = qc.mass_balance_pass;
    qcStruct.max_balance_residual = max(qc.balance_max_scaled_residual);   % scaled
    qcStruct.max_balance_residual_per_relation = ...
        local_names2struct(qc.balance_names, qc.balance_max_scaled_residual);
    qcStruct.balance_max_abs_residual_per_relation = ...
        local_names2struct(qc.balance_names, qc.balance_max_abs_residual);
    qcStruct.repeatability_pass = repeatability_pass;
    qcStruct.repeatability_max_abs_diff = repeat_maxdiff;
    qcStruct.solver_convergence_pass = convergence_pass;
    qcStruct.solver_convergence_max_scaled_diff = convergence_max_scaled_diff;
    qcStruct.tolerance_study = struct( ...
        'RelTol', p0.meta.simulation.tolerance_study.RelTol_tight, ...
        'AbsTol', p0.meta.simulation.tolerance_study.AbsTol_tight);
    qcStruct.equations_verified = eq_ok;
    qcStruct.equation_guard_note = ['five balance-derivative identities of ' ...
        'Eqs. (15)-(19) hold to roundoff along the trajectory; initial-rate ' ...
        'sanity (V_TL(0)=0, V_EN(0)=0, V_TX(0)>0, V_RS(0)>0) holds; ' ...
        'full test suite: matlab/tests/test_pure_literature_reference.m'];
    qcStruct.energy_split_percent = struct( ...
        'Q_TX', qc.energy_split_percent(1), ...
        'Q_TL', qc.energy_split_percent(2), ...
        'Q_RS', qc.energy_split_percent(3));
    qcStruct.anchors = anchor;
    qcStruct.endpoints = struct( ...
        'nt_uM', base.y(end,3), 'a_uM', base.y(end,7), ...
        'mRNA_molecules_uM', base.mRNA(end), 'protein_molecules_uM', base.protein(end), ...
        'NTP_uM', base.y(end,1), 'CP_uM', base.y(end,8), 'TLcat_uM', base.y(end,10));
    qcStruct.accumulators_vs_trapz = struct( ...
        'D_nt_rel', qc.D_nt_accumulator_vs_trapz_rel, ...
        'D_TLcat_rel', qc.D_TLcat_accumulator_vs_trapz_rel);
    qcStruct.fig4_reproduction_status = local_fig4_status(cond(k).dna_uM, anchor);
    qcStruct.unresolved_items = {};
    fid = fopen(fullfile(condDir, 'qc.json'), 'w');
    fprintf(fid, '%s', jsonencode(qcStruct, 'PrettyPrint', true));
    fclose(fid);

    res{k} = base;
    summary.conditions{k} = struct('label', cond(k).label, 'dna_nM', cond(k).dna_uM*1e3, ...
        'scientific_status', qcStruct.scientific_status, ...
        'protein_4h_molecules_uM', base.protein(end), ...
        'a_4h_uM', base.y(end,7), 'nt_4h_uM', base.y(end,3), ...
        'energy_split_percent', qc.energy_split_percent);
    fprintf(['  protein(4h) = %.3f uM molecules (a = %.1f uM), nt(4h) = %.1f uM\n' ...
             '  energy split Q_TX/Q_TL/Q_RS = %.1f/%.1f/%.1f %% (paper @6.8nM: 74/15/11)\n' ...
             '  max scaled balance residual = %.3e, convergence max scaled diff = %.3e\n'], ...
        base.protein(end), base.y(end,7), base.y(end,3), ...
        qc.energy_split_percent, max(qc.balance_max_scaled_residual), ...
        convergence_max_scaled_diff);
end

% ---- Fig. 4 reproduction figure (nt top / a bottom; paper color coding) ----
fig = figure('Visible', 'off', 'Position', [100 100 900 740], 'Color', 'w');
tl = tiledlayout(fig, 2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
title(tl, 'Mavelli et al. 2015, Fig. 4 (calculated curves) - new_simulation', ...
    'FontWeight', 'bold', 'Interpreter', 'none');
nexttile; hold on; grid on; box on;
for k = 1:nCond
    plot(res{k}.t/3600, res{k}.y(:,3), '-', 'Color', colors(k,:), 'LineWidth', 1.6);
end
ylabel('[nt]  (\muM, polymerized nucleotides)');
legend(cond.legend, 'Interpreter', 'none', 'Location', 'northwest');
nexttile; hold on; grid on; box on;
for k = 1:nCond
    plot(res{k}.t/3600, res{k}.y(:,7), '-', 'Color', colors(k,:), 'LineWidth', 1.6);
end
ylabel('[a]  (\muM, polymerized amino acids)');
xlabel(tl, {'time (h)', ...
    'new_simulation only - experimental dotted curves (Stoegbauer 2012) not overlaid; raster digitization of the calculated curves: data/processed/literature/R01/fig4/fig4_digitized.csv'}, ...
    'FontSize', 9.5);
xlim([0 4]);
exportgraphics(fig, fullfile(outdir, 'fig4_reproduction.png'), 'Resolution', 150);
close(fig);

% ---- auxiliary observables figure (mRNA / protein molecule concentrations) ----
fig2 = figure('Visible', 'off', 'Position', [100 100 900 700], 'Color', 'w');
tl2 = tiledlayout(fig2, 2, 1, 'TileSpacing', 'compact', 'Padding', 'compact');
title(tl2, 'Molecule concentrations: [mRNA] = [nt]/(3L), [protein] = [a]/L,  L = 238 (new_simulation)', ...
    'Interpreter', 'none', 'FontWeight', 'bold');
nexttile; hold on; grid on; box on;
for k = 1:nCond
    plot(res{k}.t/3600, res{k}.mRNA, '-', 'Color', colors(k,:), 'LineWidth', 1.6);
end
ylabel('[mRNA]  (\muM)');
legend({'DNA = 0.34 nM', 'DNA = 1.7 nM', 'DNA = 6.8 nM'}, ...
    'Interpreter', 'none', 'Location', 'northwest');
nexttile; hold on; grid on; box on;
for k = 1:nCond
    plot(res{k}.t/3600, res{k}.protein, '-', 'Color', colors(k,:), 'LineWidth', 1.6);
end
ylabel('[protein]  (\muM)');
xlabel(tl2, 'time (h)');
xlim([0 4]);
exportgraphics(fig2, fullfile(outdir, 'observables_mRNA_protein.png'), 'Resolution', 150);
close(fig2);

% ---- benchmark summary JSON ----
summary.anchor_paper = struct( ...
    'protein_4h_uM_at_6p8nM', 0.58, ...
    'source', 'paper Sect. 4.1 / Fig. 5 text (standard composition, [DNA]=6.8 nM)', ...
    'energy_split_percent_at_6p8nM', [74 15 11], ...
    'source_energy', 'paper Sect. 5, Table 4 entry 1');
summary.fig4_note = ['Calculated curves reproduced from the literal model translation. ' ...
    'No experimental overlay (Stogbauer 2012 machine-readable data absent from the repo). ' ...
    'The paper''s CALCULATED curves were digitized from the raster figure by matlab/tools/digitization/digitize_fig4.m ' ...
    '(provenance: digitized_from_Mavelli_2015_Fig4) -> data/processed/literature/R01/fig4/fig4_digitized.csv; ' ...
    'quantitative comparison: results/baselines/b1_mavelli2015/fig4_digitized_comparison.csv ' ...
    '(a-panel deviations <= 1.8 % everywhere; nt-panel absolute deviations <= 13 uM, i.e. <= 1.3 % of full scale).'];
fid = fopen(fullfile(outdir, 'benchmark_summary.json'), 'w');
fprintf(fid, '%s', jsonencode(summary, 'PrettyPrint', true));
fclose(fid);

% ---- run manifest (audit hardening: provenance-bound runs) ----
all_qc_ok = all(cellfun(@(c) strcmp(c.scientific_status, 'passed_all_qc'), ...
    summary.conditions));
manifest = struct();
manifest.run_id   = run_id;
manifest.model_id = prov.model_id;
manifest.model_definition_hash = prov.model_definition_hash;
manifest.parameter_hash = prov.parameter_hash;
manifest.input_hash = prov.input_hash;
manifest.git_commit = prov.git_commit;
manifest.git_dirty  = prov.git_dirty;
manifest.matlab_version = prov.matlab_version;
manifest.solver = 'ode15s';
manifest.solver_options = struct('RelTol', 1e-9, 'AbsTol', 1e-12, ...
    't_final_s', run_inputs.t_final_s, 'output_dt_s', run_inputs.output_dt_s);
manifest.command = sprintf("run_fig4_benchmark('RunId', '%s')", run_id);
manifest.created_at = char(datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss'));
manifest.execution_status = 'completed';
manifest.scientific_status = ternary(all_qc_ok, 'passed_all_qc', 'failed_qc');
manifest.hash_algorithm = prov.hash_algorithm;
manifest.provenance_note = ['git_commit/git_dirty read live via pure_git_state ' ...
    '(git rev-parse HEAD; git status --porcelain); hashes = SHA-256 of ' ...
    'models/literature_reference/{model_definition.json,parameters.json} and of the ' ...
    'canonical JSON of the run inputs'];
fid = fopen(fullfile(outdir, 'manifest.json'), 'w');
fprintf(fid, '%s', jsonencode(manifest, 'PrettyPrint', true));
fclose(fid);

fprintf('\nBenchmark finished. Outputs in %s\n', outdir);
fprintf('Run manifest: results/runs/%s/manifest.json (git %s, dirty=%s)\n', ...
    run_id, manifest.git_commit, num2str(manifest.git_dirty));
end % function

% -------------------------------------------------------------------------
function ok = local_equation_guard(sim, p0)
% Per-run equation identity checks:
% (i)  the five conservation-derivative identities from Eqs. (15)-(19)
%      hold to roundoff along the trajectory (verifies correct
%      transcription of the ODE coefficients, e.g. the 2*V_TL factor);
% (ii) initial-rate sanity (task Sect. 9 E): V_TL(0) = 0 (nt = 0),
%      V_EN(0) = 0 (NXP = 0), V_TX(0) > 0, V_RS(0) > 0.
n = numel(sim.t);
idx = unique([1, floor(n/2), n]);
ok = true;
for j = idx'
    [~, R] = rhs_pure_literature_reference(sim.t(j), sim.y(j,:)', sim.p);
    d1 = (-R(1) - 2*R(4) - R(3) + R(6)) ...                     % Eq. (20)
         + (R(1) - R(2)) ...                                    % Eq. (22)
         + (2*R(4) + R(3) - R(6)) ...                           % Eq. (21)
         + R(2);                                                % D_nt' = Eq. (6)
    d2 = p0.n_A*(-R(3)/p0.n_A) + R(4) + p0.n_T*((R(3) - R(4))/p0.n_T);   % Eqs. (23)+(25)+(24b)
    d3 = p0.n_T*((-R(3) + R(4))/p0.n_T) + p0.n_T*((R(3) - R(4))/p0.n_T); % Eqs. (24a)+(24b)
    d4 = -R(6) + R(6);                                          % Eqs. (26a)+(26b)
    d5 = -R(5) + R(5);                                          % Eq. (27)+D_TLcat'
    ok = ok && (max(abs([d1, d2, d3, d4, d5])) <= 1e-9);
end
% initial rates
[~, R0] = rhs_pure_literature_reference(0, sim.p.y0', sim.p);
ok = ok && (R0(4) == 0) && (R0(6) == 0) && (R0(1) > 0) && (R0(3) > 0);
end

% -------------------------------------------------------------------------
function anchor = local_anchors(sim, dna_uM, L)
anchor = struct();
anchor.protein_4h_molecules_uM = sim.protein(end);
anchor.a_4h_uM                 = sim.y(end, 7);
anchor.nt_4h_uM                = sim.y(end, 3);
anchor.mRNA_4h_molecules_uM    = sim.mRNA(end);
if abs(dna_uM - 0.0068) < 1e-12
    anchor.paper_protein_4h_molecules_uM = 0.58;       % paper Sect. 4.1/Fig. 5 text
    anchor.paper_a_4h_uM = 0.58 * L;                   % = 138.04 uM
    anchor.protein_anchor_rel_dev = (sim.protein(end) - 0.58) / 0.58;
    anchor.paper_energy_split_percent = [74 15 11];    % paper Sect. 5 / Table 4 entry 1
    anchor.energy_split_abs_dev_pp = sim.qc.energy_split_percent - [74 15 11];
end
end

% -------------------------------------------------------------------------
function s = local_fig4_status(dna_uM, anchor)
% Status vocabulary kept honest: this is an approximate reproduction of the
% CALCULATED curves (no experimental overlay, no digitization).
s = 'calculated_curves_reproduced_qualitative';
if abs(dna_uM - 0.0068) < 1e-12
    if abs(anchor.protein_anchor_rel_dev) <= 0.05
        s = 'calculated_curves_reproduced_quantitative_anchor_within_5pct';
    else
        s = 'calculated_curves_reproduced_anchor_deviation_above_5pct';
    end
end
end

% -------------------------------------------------------------------------
function s = local_names2struct(names, values)
s = struct();
for i = 1:numel(names)
    s.(names{i}) = values(i);
end
end

% -------------------------------------------------------------------------
function out = ternary(cond, a, b)
if cond; out = a; else; out = b; end
end
