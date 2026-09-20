function summary = run_fixture_birth_death()
%RUN_FIXTURE_BIRTH_DEATH Print the B0 deterministic/exact references.

d0 = fileparts(mfilename('fullpath'));
root = fileparts(d0);
addpath(fullfile(root, 'matlab', 'src', 'fixtures'));

out = simulate_birth_death_mean();
dist = birth_death_exact_distribution(out.p.t_final,out.p);

fprintf('B0 birth_death fixture\n');
fprintf('  final exact mean: %.9g molecules\n', dist.mu);
fprintf('  numerical mean scaled error: %.3e\n', out.qc.max_scaled_mean_error);
fprintf('  PMF omitted tail mass: %.3e\n', dist.tail_mass);
fprintf('  exact reference mean = variance = %.9g\n', dist.mu);
fprintf('  generic SSA status: %s\n', out.p.stochastic_validation_status);

summary = struct('mean_qc',out.qc,'distribution',dist);
end
