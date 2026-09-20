function summary = run_fixture_enzyme_qssa()
%RUN_FIXTURE_ENZYME_QSSA Print success/failure reduction metrics.

d0 = fileparts(mfilename('fullpath'));
root = fileparts(d0);
addpath(fullfile(root,'matlab','src','fixtures'));

valid = compare_enzyme_qssa('valid');
failure = compare_enzyme_qssa('failure');

fprintf('B0 enzyme_qssa fixture\n');
fprintf('  valid standard product error: %.3e\n', ...
    valid.standard_product_scaled_error);
fprintf('  valid total product error:    %.3e\n', ...
    valid.total_product_scaled_error);
fprintf('  failure standard error:       %.3e\n', ...
    failure.standard_product_scaled_error);
fprintf('  failure total error:          %.3e\n', ...
    failure.total_product_scaled_error);

summary = struct('valid',valid,'failure',failure);
end
