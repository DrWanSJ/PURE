function run_pnas2017_simbiology()
% Independent SBML import/execution check for the provenance-bound fMGG case.
% The input is a derived compatibility SBML; the author source is untouched.

root = fileparts(fileparts(mfilename('fullpath')));
runDir = fullfile(root, 'results', 'pnas2017_reference', 'rr_cvode_author_csv_20260924');
source = fullfile(runDir, 'effective_author_conditions.xml');
if ~isfile(source)
    error('PURE:MissingSBML', 'Generate the effective SBML with run_pnas2017_reference.py first.');
end

importLog = evalc('model = sbmlimport(source);');
if numel(model.Species) ~= 241 || numel(model.Reactions) ~= 968
    error('PURE:CountMismatch', 'SimBiology import count differs from source.');
end
[stoich, speciesNames, ~] = getstoichmatrix(model);
po4Row = find(strcmp(speciesNames, 'PO4'));
if numel(po4Row) ~= 1 || full(stoich(po4Row, 414)) ~= 2
    error('PURE:StoichiometryMismatch', 'Normalized source re0000000414 -> PO4 coefficient was not preserved.');
end

config = getconfigset(model, 'active');
config.SolverType = 'ode15s';
config.StopTime = 1000;
config.SolverOptions.RelativeTolerance = 1e-3;
config.SolverOptions.AbsoluteTolerance = 1e-9;
config.SolverOptions.AbsoluteToleranceScaling = false;
simulationLog = evalc('[time, values, names] = sbiosimulate(model);');
if numel(names) ~= 241 || size(values, 2) ~= 241 || any(~isfinite(values), 'all')
    error('PURE:SimulationOutput', 'SimBiology returned incomplete or nonfinite data.');
end
productColumn = find(strcmp(names, 'Pept0003'));
if numel(productColumn) ~= 1 || time(end) ~= 1000
    error('PURE:ProductOutput', 'Expected Pept0003 or final time is missing.');
end

writematrix([time, values], fullfile(runDir, 'simbiology_trajectory.csv'));
fid = fopen(fullfile(runDir, 'simbiology_names.json'), 'w');
if fid < 0, error('PURE:OutputFile', 'Could not write names JSON.'); end
fprintf(fid, '%s\n', jsonencode(names));
fclose(fid);
fid = fopen(fullfile(runDir, 'simbiology_warnings.txt'), 'w');
if fid < 0, error('PURE:OutputFile', 'Could not write warning log.'); end
fprintf(fid, '%s', importLog);
fprintf(fid, '%s', simulationLog);
fclose(fid);

report = struct();
report.engine = 'MATLAB SimBiology';
report.solver = 'ode15s';
report.input = 'effective_author_conditions.xml';
report.input_status = 'derived_compatibility_copy_with_author_csv_overlay';
report.imported_species = numel(model.Species);
report.imported_reactions = numel(model.Reactions);
report.normalized_po4_coefficient = full(stoich(po4Row, 414));
report.initial_conditions_and_parameters = 'provided_in_effective_sbml_from_author_csv';
report.end_time_seconds = time(end);
report.time_points = numel(time);
report.product_sbml_id = 'Pept0003';
report.product_final = values(end, productColumn);
report.minimum_species_concentration = min(values, [], 'all');
report.dimensional_analysis_warning_count = count(string(simulationLog), 'Reported from Dimensional Analysis');
report.scientific_status = 'integrity_cross_check_not_experimental_validation';
fid = fopen(fullfile(runDir, 'simbiology_run.json'), 'w');
if fid < 0, error('PURE:OutputFile', 'Could not write SimBiology report.'); end
fprintf(fid, '%s\n', jsonencode(report, PrettyPrint=true));
fclose(fid);
fprintf('SIMBIOLOGY_COMPLETE rows=%d product_final=%.12g warnings=%d\n', ...
    numel(time), report.product_final, report.dimensional_analysis_warning_count);
end
