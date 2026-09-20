function p = reversible_conversion_params()
%REVERSIBLE_CONVERSION_PARAMS Load the frozen B0 synthetic fixture parameters.
%
%   P = REVERSIBLE_CONVERSION_PARAMS() reads
%   models/fixtures/reversible_conversion/parameters.json.
%
%   This fixture is mathematical/software verification only. It is not a
%   PURE-system model and its parameters must not enter PURE parameter sets.

thisdir = fileparts(mfilename('fullpath'));   % .../matlab/src/fixtures
root = fileparts(fileparts(fileparts(thisdir)));
jsonfile = fullfile(root, 'models', 'fixtures', ...
    'reversible_conversion', 'parameters.json');

raw = jsondecode(fileread(jsonfile));

p = struct();
p.fixture_id = raw.fixture_id;
p.evidence_type = raw.evidence_type;

p.k_f = raw.parameters.k_f.value;
p.k_r = raw.parameters.k_r.value;
p.A0 = raw.initial_conditions.A0.value;
p.B0 = raw.initial_conditions.B0.value;
p.y0 = [p.A0; p.B0];
p.state_names = {'A', 'B'};

p.t_final = raw.simulation.t_final.value;
p.output_dt = raw.simulation.output_dt.value;
p.solver = raw.simulation.solver;
p.RelTol = raw.simulation.RelTol;
p.AbsTol = raw.simulation.AbsTol;

p.acceptance = raw.acceptance;
p.source_file = jsonfile;
end
