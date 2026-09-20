function p = birth_death_params()
%BIRTH_DEATH_PARAMS Load the frozen B0 birth-death parameters.
%
% The JSON file is the registered source for this fixture.  We keep these
% parameters separate from PURE because this model is a molecule-count
% verification problem, not a concentration model.

thisdir = fileparts(mfilename('fullpath'));
root = fileparts(fileparts(fileparts(thisdir)));
jsonfile = fullfile(root, 'models', 'fixtures', 'birth_death', 'parameters.json');
raw = jsondecode(fileread(jsonfile));

p = struct();
p.fixture_id = raw.fixture_id;
p.evidence_type = raw.evidence_type;

% alpha_b is a zero-order birth rate [molecule/s].
% beta_b is a first-order death rate [1/s].
p.alpha_b = raw.parameters.alpha_b.value;
p.beta_b = raw.parameters.beta_b.value;

p.X0 = raw.initial_conditions.X0.value;
p.y0 = p.X0;

p.t_final = raw.simulation.t_final.value;
p.output_dt = raw.simulation.output_dt.value;
p.RelTol = raw.simulation.RelTol;
p.AbsTol = raw.simulation.AbsTol;
p.solver = raw.simulation.solver;

p.acceptance = raw.acceptance;
p.stochastic_validation_status = raw.stochastic_validation_status;
p.source_file = jsonfile;
end
