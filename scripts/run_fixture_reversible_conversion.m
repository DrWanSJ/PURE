function summary = run_fixture_reversible_conversion()
%RUN_FIXTURE_REVERSIBLE_CONVERSION Execute and report B0 fixture 1.

d0 = fileparts(mfilename('fullpath'));   % .../scripts
root = fileparts(d0);
addpath(fullfile(root, 'matlab', 'src', 'fixtures'));

out = simulate_reversible_conversion();

fprintf('B0 fixture: %s\n', out.fixture_id);
fprintf('evidence_type: %s\n', out.evidence_type);
fprintf('solver: %s\n', out.solver);
fprintf('max analytic scaled error: %.3e\n', ...
    out.qc.analytic_max_scaled_error);
fprintf('max conservation scaled residual: %.3e\n', ...
    out.qc.conservation_max_scaled_residual);
fprintf('minimum state: %.15g uM\n', out.qc.min_state_value_uM);
fprintf('status: %s\n', out.qc.scientific_status);

summary = out.qc;
summary.A_eq_uM = out.analytic.A_eq;
summary.B_eq_uM = out.analytic.B_eq;
summary.A_end_uM = out.A(end);
summary.B_end_uM = out.B(end);
end
