function diagnose_r1_simbiology_tight_v1()
% Independent tight SimBiology diagnostic for the frozen author-condition SBML.
% This does not replace the accepted loose RoadRunner author reproduction.

root = fileparts(fileparts(mfilename('fullpath')));
source = fullfile(root, 'results', 'pnas2017_reference', ...
    'rr_cvode_author_csv_20260924', 'effective_author_conditions.xml');
out = fullfile(root, 'results', 'reduction', 'r1_simbiology_tight_v1', 'diagnostic_001');
if ~isfile(source)
    error('PURE:MissingSBML', 'Frozen author-condition SBML is unavailable.');
end
if ~isfolder(out)
    mkdir(out);
end

importLog = evalc('model = sbmlimport(source);');
if numel(model.Species) ~= 241 || numel(model.Reactions) ~= 968
    error('PURE:CountMismatch', 'Independent SBML import has wrong dimensions.');
end
[stoich, speciesNames, ~] = getstoichmatrix(model);
po4Row = find(strcmp(speciesNames, 'PO4'));
if numel(po4Row) ~= 1 || full(stoich(po4Row, 414)) ~= 2
    error('PURE:StoichiometryMismatch', 'Imported phosphate coefficient differs.');
end

config = getconfigset(model, 'active');
config.SolverType = 'ode15s';
config.StopTime = 1000;
config.SolverOptions.RelativeTolerance = 1e-12;
config.SolverOptions.AbsoluteTolerance = 1e-14;
config.SolverOptions.AbsoluteToleranceScaling = false;
times = [0, logspace(-4, 3, 200)];
outputTimesRequested = false;
if isprop(config.SolverOptions, 'OutputTimes')
    config.SolverOptions.OutputTimes = times;
    outputTimesRequested = true;
end
simulationLog = evalc('[time, values, names] = sbiosimulate(model);');
if numel(names) ~= 241 || size(values, 2) ~= 241 || ...
        any(~isfinite(values), 'all') || abs(time(end) - 1000) > 1e-10
    error('PURE:SimulationOutput', 'Tight SimBiology simulation is incomplete.');
end

writematrix([time, values], fullfile(out, 'trajectory.csv'));
fid = fopen(fullfile(out, 'names.json'), 'w');
if fid < 0
    error('PURE:OutputFile', 'Could not write names.');
end
fprintf(fid, '%s\n', jsonencode(names));
fclose(fid);
fid = fopen(fullfile(out, 'warnings.txt'), 'w');
if fid < 0
    error('PURE:OutputFile', 'Could not write warnings.');
end
fprintf(fid, '%s\n%s', importLog, simulationLog);
fclose(fid);

report = struct();
report.status = 'R1_INDEPENDENT_TIGHT_SBML_DIAGNOSTIC';
report.engine = 'MATLAB SimBiology';
report.solver = 'ode15s';
report.input = source;
report.input_status = 'derived_compatibility_copy_with_author_CSV_overlay';
report.imported_species = numel(model.Species);
report.imported_reactions = numel(model.Reactions);
report.normalized_po4_coefficient = full(stoich(po4Row, 414));
report.rtol = config.SolverOptions.RelativeTolerance;
report.atol = config.SolverOptions.AbsoluteTolerance;
report.output_times_requested = outputTimesRequested;
report.output_time_count = numel(time);
report.end_time_seconds = time(end);
report.minimum_species = min(values, [], 'all');
fid = fopen(fullfile(out, 'report.json'), 'w');
if fid < 0
    error('PURE:OutputFile', 'Could not write report.');
end
fprintf(fid, '%s\n', jsonencode(report, PrettyPrint=true));
fclose(fid);
fprintf('R1_SIMBIOLOGY_TIGHT_COMPLETE rows=%d minimum=%.12g\n', ...
    numel(time), report.minimum_species);
end
